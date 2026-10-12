"""T08 fixture-geometry repair of the T07 R1 Pro sixteen-phase prep screen.

Only key poses are evaluated, exactly as in the golden checker. No neighbourhood,
trajectory, food-quality, peak torque, or alternative friction gate is added.
Run a foreground chunk: python run_scene.py --batch P01 P02 P03 P04
Each worker is limited to 1140 seconds and 1900 MiB; at most four workers.
The binding original is board/sim/golden/mandoline_golden.py.
"""
import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"
import argparse
import concurrent.futures
import ctypes
import hashlib
import json
import math
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import numpy as np
import mujoco
import mink
from scipy.spatial.transform import Rotation

HERE = Path(__file__).resolve().parent
SIM = HERE.parents[1]
MODEL = SIM / "t05/ref_robots/models/r1pro_kitchen_galley.xml"
META = json.loads(MODEL.with_suffix(".json").read_text())
LIM = META["torque_limits"]
ACM_NAMES = json.loads((MODEL.parent / "r1pro.acm.json").read_text())["disabled_robot_pairs"]
BASE = ["base_x", "base_y", "base_yaw"]
TORSO = [f"torso_joint{i}" for i in range(1, 5)]
ARMS = {s: [f"{label}_arm_joint{i}" for i in range(1, 8)] for s, label in (("R", "right"), ("L", "left"))}
JOINTS = TORSO + ARMS["R"] + ARMS["L"]
JAWS = [f"{s}_gripper_finger_joint{i}" for s in ("left", "right") for i in (1, 2)]
PAD = 0.0  # Full-scale R1 Pro collision hulls, as in the golden script.
MU = 0.5
SF = 1.5
NORMAL_SUM_N = 150.0  # Native G1 rated total opposing normal, T05 published reference.
KEY_FORCE_N = 150.0   # T06 F05 holder design bearing proof requirement.
KEY_MOMENT_NM = 15.0
JAW_AXES = [(0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0)]
LAYOUT = {
    "board": dict(center=[0.08, 0.19], size=[0.315, 0.295], bottom=0.85, height=0.035, source="T06 T06 Etac Fix"),
    "mandoline": dict(center=[0.47, 0.12], size=[0.345, 0.118], bottom=0.865, height=0.060, support_bottom=0.85, source="T06 T02 Kuhn Rikon 345x118x47 mm; custom 13 mm support on 15 mm receiver"),
    "wedger": dict(center=[0.39, 0.40], size=[0.216, 0.280], bottom=0.85, height=0.4826, source="T06 T08 Nemco 55550-8; custom 216 mm guide-foot width and T06 F06 280 mm bridge along Y"),
    "output_bowl": dict(center=[0.00, 0.47], size=[0.20, 0.20], bottom=0.85, height=0.09, source="T06 T25 IKEA BLANDA 20 cm; T07 reviewed P14 location used throughout T08"),
    "peeler_tray": dict(center=[0.59, 0.41], size=[0.09, 0.16], bottom=0.85, height=0.1674, source="Custom tray and upright T06 T09 152.4x76.2x25.4 mm peeler"),
    "basket": dict(center=[-1.53, 0.20], size=[0.42, 0.34], bottom=0.85, height=0.175, source="R1 galley basket; 110 mm removable false bottom"),
    "spinner": dict(center=[-1.125, 0.20], size=[0.266, 0.266], bottom=0.85, height=0.202, source="T06 T15 OXO UK 1351580 plus assumed 50 mm extended pump"),
    "knife_dock": dict(center=[-1.005, 0.475], size=[0.36, 0.10], bottom=0.85, height=0.170, source="Custom supported dock and keyed T06 T23 309x85x18 mm knife"),
}


def json_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def adjustment_parameter(result):
    return result.get("adjustment_parameter_m", result.get("adjustment_height_m", 0.))


def normalize_result(result):
    delta = adjustment_parameter(result)
    result.pop("adjustment_height_m", None); result["adjustment_parameter_m"] = delta
    pid = result["id"]
    if not delta: result["scene_adjustment"] = None
    elif pid == "P11": result["scene_adjustment"] = dict(object="rinse_basket", delta_xyz_m=[0, 0, -.080], bottom_m=.725, pump_changed=False)
    elif pid == "P14": result["scene_adjustment"] = dict(object="output_bowl", delta_xyz_m=[-.120, 0, 0], center_xy_m=[0, .470], bottom_m=.85, minimum_station_gap_mm=32.5)
    elif pid in ("P01", "P03", "P05"):
        result["scene_adjustment"] = dict(object="receiving_end_supports", delta_xyz_m=[0, 0, .050], deck_changed=False)
    else: result["scene_adjustment"] = dict(object=result["definition"]["segments"][-1]["station"], delta_xyz_m=[0, 0, delta])
    return result


def center(name, dz=0):
    a = LAYOUT[name]
    return np.array([*a["center"], a["bottom"] + dz], float)


def rotation(approach, jaw):
    # Golden tool-frame +X approach; site is the origin of R_tool/L_tool.
    a_t = np.array([1., 0, 0]); b_t = np.cross(a_t, [0, 0, 1.]); c_t = np.cross(a_t, b_t)
    a_w = np.array(approach, float); a_w /= np.linalg.norm(a_w)
    b_w = np.array(jaw, float); b_w -= a_w * (b_w @ a_w); b_w /= np.linalg.norm(b_w)
    c_w = np.cross(a_w, b_w)
    return np.column_stack([a_w, b_w, c_w]) @ np.column_stack([a_t, b_t, c_t]).T


def hand(pos, held="", kg=0., work=0., approach=(0, 0, -1), roll=0., opening=0.03,
         nominal=((0, 0, 0),), check=None, intended=(), com=None, grip="keyed", jaw_axis=None):
    return dict(pos=np.array(pos).tolist(), approach=list(approach), jaw_axis=jaw_axis,
                roll_deg=roll, held=held, held_kg=kg, work_offset_m=work,
                mass_offset_m=work if com is None else com, jaw_opening_m=opening,
                nominal_forces_N=[list(f) for f in nominal],
                check_forces_N=None if check is None else [list(f) for f in check],
                intended=list(intended), grip=grip)


def offset_vector(v):
    return np.array([v, 0., 0.]) if np.isscalar(v) else np.array(v, float)


def segment(label, poses, station, jaw_axes=None):
    return dict(label=label, station=station, poses=[{"R": p} if "pos" in p else p for p in poses],
                jaw_axes=JAW_AXES if jaw_axes is None else jaw_axes)


def phase(pid, name, segments):
    return dict(id=pid, name=name, segments=segments)


def P01(dz=0):
    p = center("basket", 0.1325 + dz) + [-0.095, -0.08, 0]
    a = hand(p, "carrot", .2, opening=.035, grip="friction", intended=["basket_"])
    b = dict(a, pos=(p + [0, 0, .1]).tolist())
    return phase("P01", "Pick carrot and lift 100 mm", [segment("pick_lift", [a, b], "basket")])


def rinse(pid, food, mass, dz):
    # Existing water outlet, not the outer spout bounding-box center.
    p = np.array(META["scene"]["water_outlet"]) + [0, 0, -.08 + dz]
    a = hand(p, food, mass, approach=(0, 1, 0), roll=-60, opening=.035 if food == "carrot" else .065,
             grip="friction", nominal=[(5, 0, 0), (-5, 0, 0)], check=[(10, 0, 0), (-10, 0, 0)])
    b = dict(a, roll_deg=60)
    return phase(pid, f"Rinse {food}, wrist -60 to +60 deg", [segment("rinse_roll", [a, b], "faucet", [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)])])


def P02(dz=0):
    return rinse("P02", "carrot", .2, dz)


def P03(dz=0):
    p = center("board", .035 + .0175 + dz)
    a = hand(p + [0, 0, .1], "carrot", .2, opening=.035, grip="friction", intended=["cutting_board", "board_mat", "board_clamp", "counter_right"])
    b = dict(a, pos=p.tolist())
    return phase("P03", "Place carrot on clamp board", [segment("place", [a, b], "board")])


def peel(pid, food, nominal, check, dz):
    # T09 outer envelope: handle/blade relationship is a declared fixture datum.
    # Blade is 65 mm beyond grasp along approach; stroke runs along world X.
    z = .035 + (.0175 if food == "carrot" else .035) + .065 + dz
    p = center("board", z)
    a = hand(p + [-.06, 0, 0], "peeler", .1, work=.065, com=.025,
             nominal=[(-nominal[0], 0, nominal[1])], check=[(-check[0], 0, check[1])],
             intended=["clamped_food", "cutting_board"])
    b = dict(a, pos=(p + [.06, 0, 0]).tolist())
    return phase(pid, f"Peel clamped {food}, 120 mm", [segment("peel_stroke", [a, b], "board", [(0, 1, 0), (0, -1, 0)])])


def P04(dz=0):
    return peel("P04", "carrot", (15, 10), (25, 15), dz)


def P05(dz=0):
    p = center("mandoline", .060 + .0175 + dz)
    a = hand(p + [0, 0, .10], "carrot", .2, opening=.035, grip="friction",
             intended=["mandoline", "holder_on_deck", "counter_right"])
    b = dict(a, pos=p.tolist())
    return phase("P05", "Load carrot in holder on deck", [segment("load", [a, b], "mandoline")])


def slicing(pid, food, feed, checkfeed, lateral, dz):
    p = center("mandoline", .060 + .080 + dz)
    nom = [(-feed, lat, 20) for lat in lateral]
    check = [(-checkfeed, lat, 20) for lat in lateral]
    a = hand(p + [-.10, 0, 0], "holder", .55 if food == "carrot" else .60,
             work=.080, nominal=nom, check=check,
             intended=["mandoline", "cutting_board", "board_mat", "counter_right"])
    b = dict(a, pos=(p + [.10, 0, 0]).tolist())
    return phase(pid, f"Mandoline {food}, 200 mm", [segment("slice_stroke", [a, b], "mandoline")])


def P06(dz=0):
    return slicing("P06", "carrot", 40, 60, (-10, 10), dz)


def P07(dz=0):
    p = center("basket", .150 + dz) + [.095, -.08, 0]
    a = hand(p, "potato", .25, opening=.065, grip="friction", intended=["basket_"])
    b = dict(a, pos=(p + [0, 0, .10]).tolist())
    return phase("P07", "Pick potato", [segment("pick_lift", [a, b], "basket")])


def P08(dz=0):
    return rinse("P08", "potato", .25, dz)


def P09(dz=0):
    return peel("P09", "potato", (20, 10), (30, 15), dz)


def P10(dz=0):
    return slicing("P10", "potato", 50, 70, (0,), dz)


def P11(dz=0):
    p = np.array(META["scene"]["water_outlet"]) + [0, 0, -.08]
    a = hand(p + [0, -.10, 0], "leaves", .1, approach=(0, 1, 0), opening=.04, grip="friction", intended=["rinse_basket"])
    b = dict(a, pos=p.tolist())
    pump = center("spinner", .152 + .050 + .060)
    c = hand(pump, "pusher", .15, work=.060, com=.030, nominal=[(0, 0, 30)],
             check=[(0, 0, 45)], intended=["spinner_pump"])
    e = dict(c, pos=(pump - [0, 0, .030]).tolist())
    # Each process stroke has one frozen base; navigation between them is not evaluated.
    return phase("P11", "Greens into rinse basket and spinner pump", [segment("place_leaves", [a, b], "faucet", [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]), segment("pump", [c, e], "spinner")])


def P12(dz=0):
    # Knife edges at X offsets 0 and 40 mm are two 50 mm down strokes.
    p = center("board", .035 + .085 + dz) + [0, .110, 0]
    segs = []
    for x in (-.020, .020):
        a = hand(p + [x, 0, .050], "knife", .198, work=[.085, 0, -.110], com=[.025, 0, -.060],
                 nominal=[(0, 0, 20)], check=[(0, 0, 30)], intended=["cutting_board", "comb_", "clamped_food"])
        b = dict(a, pos=(p + [x, 0, 0]).tolist())
        segs.append(segment(f"cut_at_{x:+.3f}", [a, b], "board", [(1, 0, 0)]))
    return phase("P12", "Greens knife cuts at 40 mm spacing", segs)


def P13(dz=0):
    # One-hand option explicitly allowed. Hand on positive keyed central bridge.
    p = center("wedger", .430 + dz) + [0, -.110, 0]
    a = hand(p, "wedger_bridge", .18, work=[.060, 0, .110], com=[0, 0, .110], nominal=[(0, 0, 50)],
             check=[(0, 0, 70)], intended=["wedger_plunger", "wedger_tomato", "wedger_blades"])
    b = dict(a, pos=(p - [0, 0, .210]).tolist())
    return phase("P13", "Tomato wedger, 50 N total with R handle", [segment("press", [a, b], "wedger", [(1, 0, 0)])])


def P14(dz=0):
    p = center("mandoline", .110)
    a = hand(p, "catch_tray", .5, work=.080, com=.080,
             intended=["mandoline", "catch_dock", "counter_right"])
    target = center("output_bowl", .380) + ([-.120, 0, 0] if dz else [0, 0, 0])
    b = dict(a, pos=target.tolist(), roll_deg=60)
    return phase("P14", "Lift loaded catch tray and tilt 60 deg over output", [segment("transfer_tilt", [a, b], "output_bowl", [(0, 1, 0), (0, -1, 0)])])


def P15(dz=0):
    p = center("peeler_tray", .080 + dz)
    a = hand(p, "peeler", .1, work=.065, com=.025, intended=["peeler_tray", "peeler_support"])
    b = dict(a, pos=(p + [0, 0, .10]).tolist())
    return phase("P15", "Pick Y-peeler and return", [segment("pick_return_reversed", [a, b], "peeler_tray", [(0, 1, 0)])])


def P16(dz=0):
    p = center("knife_dock", .130 + dz) + [-.075, 0, 0]
    a = hand(p, "knife", .198, work=[.085, 0, -.110], com=[.025, 0, -.060], intended=["knife_dock"])
    b = dict(a, pos=(p + [0, 0, .10]).tolist())
    return phase("P16", "Pick knife and return", [segment("pick_return_reversed", [a, b], "knife_dock", [(0, 1, 0)])])


PHASES = {f"P{i:02}": globals()[f"P{i:02}"] for i in range(1, 17)}


def fmt(values):
    return " ".join(f"{float(v):.10g}" for v in values)


def box(parent, name, pos, size, color=(.60, .63, .65, 1), robot=False):
    return ET.SubElement(parent, "geom", name=name, type="box", pos=fmt(pos), size=fmt(np.array(size) / 2),
                         rgba=fmt(color), contype="2" if robot else "1", conaffinity="3" if robot else "2", mass=".000001")


def vessel(parent, name, xy, bottom, diameter, height):
    # Open polygonal bowl, not a solid cylinder at the intended receiving space.
    box(parent, name + "_bottom", [*xy, bottom + .002], [diameter * .65, diameter * .65, .004], (.25, .60, .65, 1))
    for i in range(16):
        a = i * math.tau / 16
        g = box(parent, name + f"_wall{i}", [xy[0] + diameter / 2 * math.cos(a), xy[1] + diameter / 2 * math.sin(a), bottom + height / 2],
                [.004, diameter * math.sin(math.pi / 16), height], (.30, .64, .68, 1))
        g.set("euler", fmt([0, 0, a]))


def scene_tree(station=None, dz=0):
    tree = ET.parse(MODEL); root = tree.getroot(); world = root.find("worldbody")
    # Replace all loose stations; keep permanent kitchen, sink, faucet, cabinets, stove.
    removable = ("basket_", "board_mat", "cutting_board", "drain_tray", "knife_dock", "peeler_tray", "dish_rack")
    for e in list(world):
        if e.tag == "geom" and e.get("name", "").startswith(removable): world.remove(e)
        elif e.tag == "body" and e.get("name", "").startswith("scene_"): world.remove(e)
    # Inactive legacy payload geoms remain disabled and invisible; robot meshes unchanged.
    for b in world.iter("body"):
        if "_held_" in b.get("name", ""):
            for g in b.iter("geom"): g.set("rgba", "0 0 0 0")
    if station == "faucet" and dz:
        for e in world.findall("geom"):
            if e.get("name", "").startswith(("faucet", "sensor_faucet")):
                v = np.fromstring(e.get("pos"), sep=" "); v[2] += dz; e.set("pos", fmt(v))
    def base(n):
        a = LAYOUT[n]; return a["bottom"] + (dz if n == station and n != "output_bowl" else 0)
    a = LAYOUT["board"]; z = base("board")
    box(world, "board_mat", [*a["center"], z + .001], [.315, .295, .002])
    box(world, "cutting_board", [*a["center"], z + .0175], [.315, .295, .035], (.73, .60, .37, 1))
    for x in (-.13, .13):
        box(world, "board_clamp" + str(x), [a["center"][0] + x, a["center"][1] + .095, z + .055], [.025, .035, .040])
    a = LAYOUT["mandoline"]; z = base("mandoline")
    box(world, "mandoline_receiver", [*a["center"], z - .0075], [.345, .118, .015])
    box(world, "mandoline_support", [*a["center"], z + .0065], [.345, .118, .013])
    box(world, "mandoline", [*a["center"], z + .013 + .0235], [.345, .118, .047], (.65, .74, .40, 1))
    # Real low-profile edge clamps, placed at the rear of the receiver, BELOW
    # the holder and extraction tray. 54110 maximum envelope 43.2 x 19 x
    # 21.5 mm (Mitee-Bite manufacturer dimension table); long axis along Y.
    # Receiver is anchored to the countertop; no under-cabinet access assumed.
    for x in (-.15, .15):
        box(world, "mandoline_clamp" + str(x),
            [a["center"][0] + x, a["center"][1] + .080, .85 + .0215 / 2],
            [.019, .0432, .0215], (.30, .35, .39, 1))
        box(world, "mandoline_mount_lug" + str(x),
            [a["center"][0] + x, a["center"][1] + .059, .858],
            [.024, .012, .016], (.30, .35, .39, 1))
    a = LAYOUT["basket"]; z = base("basket"); x, y = a["center"]
    box(world, "basket_floor", [x, y, z + .0075], [.42, .34, .015], (.50, .62, .67, 1))
    box(world, "basket_insert", [x, y, z + .110], [.39, .31, .010], (.60, .68, .70, 1))
    for s in (-1, 1):
        box(world, f"basket_side{s}", [x + s * .205, y, z + .0875], [.010, .34, .175])
        box(world, f"basket_end{s}", [x, y + s * .165, z + .0875], [.40, .010, .175])
    a = LAYOUT["output_bowl"]; xy = np.array(a["center"]) + ([-.120, 0] if station == "output_bowl" and dz else [0, 0])
    vessel(world, "output_bowl", xy, base("output_bowl"), .20, .09)
    a = LAYOUT["spinner"]; z = base("spinner")
    vessel(world, "spinner", a["center"], z, .266, .145)
    box(world, "spinner_lid", [*a["center"], z + .1485], [.258, .258, .007], (.24, .56, .48, 1))
    box(world, "spinner_pump", [*a["center"], z + .1845], [.075, .075, .035], (.16, .45, .32, 1))
    a = LAYOUT["wedger"]; z = base("wedger"); x, y = a["center"]
    box(world, "wedger_base", [x, y, z + .012], [.2032, .2032, .024])
    for s in (-1, 1):
        # The old 84 mm centre offset put the posts inside the 150 mm plunger
        # envelope. The unchanged 16 mm posts move to 100 mm centre offsets,
        # supported by outboard foot tabs. Nominal plunger clearance is 17 mm;
        # the actual IK poses, including their allowed errors, are checked.
        box(world, f"wedger_post{s}", [x + s * .100, y + .07, z + .2533], [.016, .016, .4586])
        box(world, f"wedger_guide_foot{s}", [x + s * .098, y + .07, z + .006], [.020, .024, .012])
    box(world, "wedger_blades", [x, y, z + .170], [.150, .150, .008], (.80, .81, .82, 1))
    # Plunger moves with the held pusher during P13; its frame is not an extra static obstacle.
    a = LAYOUT["peeler_tray"]; z = base("peeler_tray")
    box(world, "peeler_tray", [*a["center"], z + .005], [.09, .16, .010], (.42, .58, .67, 1))
    box(world, "peeler_support", [a["center"][0], a["center"][1], z + .0125], [.070, .028, .005])
    a = LAYOUT["knife_dock"]; z = base("knife_dock"); x, y = a["center"]
    box(world, "knife_dock_base", [x, y, z + .005], [.36, .10, .010])
    # Narrow rests support the blade while leaving the handle and gripper clear.
    for xoff in (-.13, .13):
        box(world, f"knife_dock_support{xoff}", [x + xoff, y, z + .025], [.018, .025, .040])
    return tree


def add_held(tool, desc, side):
    # Coordinates: tool +X is approach; tool -Y is the golden jaw reference.
    item = desc["held"]; work = desc["work_offset_m"]
    def b(label, pos, size, col=(.35, .48, .27, 1)):
        return box(tool, side + "_held_" + label, pos, size, col, robot=True)
    if item == "holder":
        # Exact golden sphere/position. Mass is an external load, never counted twice.
        ET.SubElement(tool, "geom", name=side + "_held_holder", type="sphere", size=".065", pos=fmt([work / 2 + .015, 0, 0]), mass=".000001", rgba=".85 .58 .25 1")
    elif item == "carrot": b("carrot", [0, 0, 0], [.035, .035, .160], (1, .43, .12, 1))
    elif item == "potato": b("potato", [0, 0, 0], [.070, .065, .090], (.72, .55, .30, 1))
    elif item == "leaves": b("leaves", [0, 0, 0], [.015, .040, .120], (.20, .65, .20, 1))
    elif item == "peeler":
        b("peeler_handle", [-.0212, 0, 0], [.1324, .030, .0254])
        b("peeler_head", [.055, 0, 0], [.020, .0762, .010], (.78, .79, .80, 1))
    elif item == "knife":
        b("knife_handle", [0, 0, 0], [.018, .030, .119])
        b("knife_blade", [.0425, 0, -.1595], [.085, .002, .180], (.76, .78, .80, 1))
    elif item == "pusher":
        b("pusher_handle", [0, 0, 0], [.064, .030, .024])
        b("pusher_stem", [.030, 0, 0], [.060, .020, .020])
        b("pusher_face", [.060, 0, 0], [.008, .045, .020])
    elif item == "wedger_bridge":
        b("wedger_bridge", [0, 0, .110], [.030, .045, .280])
        b("wedger_stem", [.030, 0, .110], [.060, .025, .025])
        b("wedger_plunger", [.060, 0, .110], [.008, .150, .150])
    elif item == "catch_tray":
        b("tray_handle", [0, 0, 0], [.060, .030, .024])
        b("tray_stem", [.040, 0, 0], [.080, .020, .020])
        b("tray_floor", [.080, 0, 0], [.006, .100, .300], (.45, .61, .68, 1))
        for sign in (-1, 1):
            b("tray_side" + str(sign), [.065, sign * .050, 0], [.035, .004, .300])
            b("tray_end" + str(sign), [.065, 0, sign * .150], [.035, .100, .004])
    if item and desc["grip"] == "keyed":
        # Positive shoulder lands bear in both directions, unlike a friction-only sleeve.
        for s in (-1, 1): b("key_shoulder" + str(s), [s * .036, 0, 0], [.008, .046, .030], (.23, .55, .72, 1))
    for label, offset in (("work", work), ("mass", desc["mass_offset_m"])):
        ET.SubElement(tool, "site", name=side + "_" + label, pos=fmt(offset_vector(offset)), size=".003", rgba=".9 .15 .1 1")


class Checker:
    def __init__(self, phase_def, seg, dz=0):
        self.phase = phase_def; self.seg = seg
        receiving_adjustment = phase_def["id"] in ("P01", "P03", "P05") and dz > 0
        leaf_adjustment = phase_def["id"] == "P11" and dz != 0
        tree = scene_tree(seg["station"] if dz and not receiving_adjustment and not leaf_adjustment else None,
                          dz if not receiving_adjustment and not leaf_adjustment else 0)
        world = tree.getroot().find("worldbody")
        desc = seg["poses"][0]["R"]
        self.desc = desc
        item = desc["held"]
        # Every unused tool stays at its dock and unhandled produce stays in the basket.
        # Basket food is a contained station assembly, with >=30 mm mutual separation.
        pid = phase_def["id"]
        active_food = "carrot" if pid in ("P01", "P02", "P03", "P04", "P05", "P06") else "potato" if pid in ("P07", "P08", "P09", "P10") else "greens" if pid in ("P11", "P12") else "tomato" if pid == "P13" else None
        food_data = {"carrot": ([-.095, -.08], [.160, .035, .035], [1, .43, .12, 1]),
                     "potato": ([.095, -.08], [.090, .065, .070], [.72, .55, .30, 1]),
                     "greens": ([-.095, .055], [.170, .100, .070], [.20, .65, .20, 1]),
                     "tomato": ([.095, .055], [.070, .070, .060], [.90, .16, .10, 1])}
        for food, (off, size, color) in food_data.items():
            if food == active_food: continue
            p = center("basket", .115 + size[2] / 2 + (dz if seg["station"] == "basket" and not receiving_adjustment else 0))
            p[:2] += off; box(world, "stored_" + food, p, size, color)
        for stored_item, dock, pz, shift in (("peeler", "peeler_tray", .080, 0.), ("knife", "knife_dock", .130, -.075)):
            if item == stored_item: continue
            p = center(dock, pz + (dz if seg["station"] == dock else 0)); p[0] += shift
            r = rotation((0, 0, -1), (0, 1, 0)); quat = Rotation.from_matrix(r).as_quat()[[3, 0, 1, 2]]
            b = ET.SubElement(world, "body", name="stored_" + stored_item, pos=fmt(p), quat=fmt(quat))
            h = hand(p, stored_item, .1 if stored_item == "peeler" else .198,
                     work=.065 if stored_item == "peeler" else [.085, 0, -.110],
                     com=.025 if stored_item == "peeler" else [.025, 0, -.060])
            add_held(b, h, "stored_" + stored_item)
            for g in b.findall("geom"): g.set("contype", "1"); g.set("conaffinity", "2")
        if item != "wedger_bridge":
            p = center("wedger", .430 + (dz if seg["station"] == "wedger" else 0)) + [0, -.110, 0]
            r = rotation((0, 0, -1), (1, 0, 0)); quat = Rotation.from_matrix(r).as_quat()[[3, 0, 1, 2]]
            b = ET.SubElement(world, "body", name="stored_wedger_bridge", pos=fmt(p), quat=fmt(quat))
            h = hand(p, "wedger_bridge", .18, work=[.060, 0, .110], com=[0, 0, .110])
            add_held(b, h, "stored_wedger")
            for g in b.findall("geom"): g.set("contype", "1"); g.set("conaffinity", "2")
        z = .85 + (dz if seg["station"] == "board" else 0)
        if phase_def["id"] in ("P04", "P09", "P12"):
            food = "potato" if phase_def["id"] == "P09" else "carrot" if phase_def["id"] == "P04" else "greens"
            size = [.160, .035, .035] if food == "carrot" else [.090, .065, .070] if food == "potato" else [.100, .070, .025]
            box(world, "clamped_food", [*LAYOUT["board"]["center"], z + .035 + size[2] / 2], size, (1, .45, .10, 1) if food != "greens" else (.24, .68, .20, 1))
            if phase_def["id"] == "P12":
                for i in range(5):
                    box(world, f"comb_{i}", [.08 + (i - 2) * .040, .26, z + .058], [.005, .025, .046])
        if phase_def["id"] == "P05":
            # Open pronged holder nest; food is intentionally supported by its base.
            p = center("mandoline", .060 + (0 if receiving_adjustment else dz))
            box(world, "holder_on_deck", p + [0, 0, .004], [.110, .090, .008])
        if receiving_adjustment:
            # F04/F05-style end supports: food height +50 mm; the slab/deck stays put.
            # Contact supports are away from the native fingertip grasp at food center.
            if phase_def["id"] == "P01":
                surface = center("basket", .115) + [-.095, -.08, 0]; prefix = "basket_cradle"
            elif phase_def["id"] == "P03":
                surface = center("board", .035); prefix = "board_clamp"
            else:
                surface = center("mandoline", .060); prefix = "holder_on_deck"
            for s in (-1, 1):
                box(world, prefix + f"_raised_end{s}", surface + [s * .060, 0, dz / 2], [.018, .030, dz])
                box(world, prefix + f"_raised_key{s}", surface + [s * .065, .0275, dz + .010], [.016, .015, .020])
        if phase_def["id"] == "P11" and seg["label"] == "place_leaves":
            vessel(world, "rinse_basket", [-.4, .39], .725 if leaf_adjustment else .805, .23, .14)
        if phase_def["id"] == "P13":
            box(world, "wedger_tomato", [*LAYOUT["wedger"]["center"], .85 + .203 + dz], [.070, .070, .060], (.9, .16, .1, 1))
        for s in ("R", "L"):
            tool = world.find(f".//body[@name='{s}_tool']")
            hd = seg["poses"][0].get(s)
            if hd: add_held(tool, hd, s)
        xml = ET.tostring(tree.getroot(), encoding="unicode")
        self.bind_model(mujoco.MjModel.from_xml_string(xml))

    def bind_model(self, m):
        self.m = m; self.d = mujoco.MjData(m)
        self.jid = {m.joint(i).name: i for i in range(m.njnt)}
        self.qa = {n: int(m.jnt_qposadr[j]) for n, j in self.jid.items()}
        self.da = {n: int(m.jnt_dofadr[j]) for n, j in self.jid.items()}
        self.gnames = [m.geom(g).name for g in range(m.ngeom)]
        self.gbody = m.geom_bodyid; self.weld = m.body_weldid[self.gbody]
        def root(b):
            while m.body_parentid[b] != 0: b = m.body_parentid[b]
            return b
        rroot = root(m.jnt_bodyid[self.jid["base_x"]])
        self.robot = np.array([root(b) == rroot for b in self.gbody])
        self.bnames = [m.body(b).name.lower() for b in self.gbody]
        self.held = np.array([n.startswith(("R_held_", "L_held_")) for n in self.gnames])
        self.acm = {tuple(sorted((self.gnames.index(a), self.gnames.index(b)))) for a, b in ACM_NAMES if a in self.gnames and b in self.gnames}
        # Explicit work-surface / food-fixture identities. A tool name NEVER
        # includes its mounting hardware, supports, receiver or guide posts.
        # Indexed food fixtures and docks are enumerated, not prefix-matched.
        indexed = {
            "basket_": {"basket_floor", "basket_insert", "basket_side-1", "basket_side1",
                        "basket_end-1", "basket_end1", "basket_cradle_raised_end-1",
                        "basket_cradle_raised_end1", "basket_cradle_raised_key-1",
                        "basket_cradle_raised_key1"},
            "board_clamp": {"board_clamp-0.13", "board_clamp0.13", "board_clamp_raised_end-1",
                            "board_clamp_raised_end1", "board_clamp_raised_key-1", "board_clamp_raised_key1"},
            "holder_on_deck": {"holder_on_deck", "holder_on_deck_raised_end-1", "holder_on_deck_raised_end1",
                               "holder_on_deck_raised_key-1", "holder_on_deck_raised_key1"},
            "comb_": {f"comb_{i}" for i in range(5)},
            "rinse_basket": {"rinse_basket_bottom"} | {f"rinse_basket_wall{i}" for i in range(16)},
            "knife_dock": {"knife_dock_base", "knife_dock_support-0.13", "knife_dock_support0.13"},
        }
        identities = set().union(*(indexed.get(n, {n}) for n in self.desc["intended"]))
        self.intended = {i for i, n in enumerate(self.gnames) if n in identities}
        self.basegeoms = [g for g, n in enumerate(self.gnames) if n.startswith(("base_link", "steer_motor", "wheel_motor")) and m.geom_type[g] == mujoco.mjtGeom.mjGEOM_MESH]

    def side(self, g):
        n = self.bnames[g]
        return "R" if n.startswith(("r_", "right")) else "L" if n.startswith(("l_", "left")) else None

    def gripper(self, g):
        return any(k in self.bnames[g] for k in ("tool", "jaw", "finger", "gripper"))

    def forbidden(self, q):
        # Literal golden contact logic, generalized from one holder to held geometries.
        m, d = self.m, self.d
        d.qpos[:] = q; mujoco.mj_kinematics(m, d); mujoco.mj_comPos(m, d); mujoco.mj_collision(m, d)
        hits = []
        for c in d.contact[:d.ncon]:
            a, b = int(c.geom[0]), int(c.geom[1]); ra, rb = self.robot[a], self.robot[b]
            if not ra and not rb: continue
            if (self.held[a] or self.held[b]) and ({a, b} & self.intended): continue
            if self.weld[a] == self.weld[b] or tuple(sorted((a, b))) in self.acm: continue
            wa, wb = self.weld[a], self.weld[b]
            if m.body_weldid[m.body_parentid[wa]] == wb or m.body_weldid[m.body_parentid[wb]] == wa: continue
            if "floor" in (self.gnames[a], self.gnames[b]) and (ra or rb) and not (self.held[a] or self.held[b]):
                other = b if self.gnames[a] == "floor" else a
                if not any(k in self.bnames[other] for k in ("arm", "tool", "gripper", "finger")): continue
            real = c.dist + 2 * PAD
            if ra and rb:
                if self.gripper(a) and self.gripper(b) and self.side(a) == self.side(b): continue
                need = 0.0 if self.side(a) == self.side(b) else .010
            else:
                rg = a if ra else b
                need = .005 if (self.gripper(rg) or self.held[rg]) else .010
            if real < need - 1e-6:
                hits.append(dict(pair=[self.gnames[a], self.gnames[b]], real_gap_mm=round(real * 1000, 4), required_gap_mm=need * 1000))
        return hits

    def floor_margin(self, q):
        m, d = self.m, self.d; d.qpos[:] = q; mujoco.mj_kinematics(m, d)
        vv = []
        for g in self.basegeoms:
            i = m.geom_dataid[g]; a = m.mesh_vertadr[i]; v = m.mesh_vert[a:a + m.mesh_vertnum[i]]
            vv.append(v @ d.geom_xmat[g].reshape(3, 3).T + d.geom_xpos[g])
        v = np.concatenate(vv)[:, :2]; lo, hi = np.array(META["scene"]["floor_bounds_m"])
        return float(min(np.r_[v.min(0) - lo, hi - v.max(0)]))

    def initial(self, rng, k):
        m = self.m; q = m.qpos0.copy()
        x = np.mean([p["R"]["pos"][0] for p in self.seg["poses"]])
        # Same golden ranges relative to station. Rejection only enforces free floor.
        for _ in range(2000):
            lower_x = float(np.clip(x - .55, -1.45, .75))
            q[self.qa["base_x"]] = rng.uniform(lower_x, lower_x + .70)
            q[self.qa["base_y"]] = rng.uniform(-.7, -.38)
            yaw = np.pi / 2 + rng.uniform(-.5, .5); q[self.qa["base_yaw"]] = yaw
            if self.floor_margin(q) >= -1e-6: break
        else: raise RuntimeError("No sampled base fits the actual galley free floor")
        for nm in JOINTS:
            lo, hi = m.jnt_range[self.jid[nm]]; q[self.qa[nm]] = (lo + hi) / 2 + rng.uniform(-.5, .5) * (hi - lo) * .5
        for s, label in (("R", "right"), ("L", "left")):
            opening = self.desc["jaw_opening_m"] if s == "R" else .02
            for i in (1, 2): q[self.qa[f"{label}_gripper_finger_joint{i}"]] = .00165 + opening / 2
        bx, by = q[self.qa["base_x"]], q[self.qa["base_y"]]
        left = np.array([np.cos(yaw + np.pi / 2), np.sin(yaw + np.pi / 2)])
        back = -np.array([np.cos(yaw), np.sin(yaw)])
        off = [(0.32, 0., .95), (.30, .15, .80), (.25, .25, 1.10), (.35, .10, .70)][(k // 4) % 4]
        park = np.array([bx + off[0] * left[0] + off[1] * back[0], by + off[0] * left[1] + off[1] * back[1], off[2]])
        return q, park

    def target_rotation(self, desc, k):
        jaw = desc["jaw_axis"] or self.seg["jaw_axes"][k % len(self.seg["jaw_axes"])]
        a = np.array(desc["approach"])
        # Rinse roll is about approach; tray roll tilts its approach about the jaw.
        if self.phase["id"] == "P14":
            a = Rotation.from_rotvec(np.array(jaw) * math.radians(desc["roll_deg"])).apply(a)
        else:
            jaw = Rotation.from_rotvec(a * math.radians(desc["roll_deg"])).apply(jaw)
        return rotation(a, jaw)

    def solve(self, q0, hands, park, k, iters=600):
        m = self.m; cfg = mink.Configuration(m, q=q0.copy()); tasks = []; active = []
        for s, hd in hands.items():
            t = mink.FrameTask(s + "_prep", "site", position_cost=1., orientation_cost=.5, lm_damping=1e-4)
            t.set_target(mink.SE3.from_rotation_and_translation(mink.SO3.from_matrix(self.target_rotation(hd, k)), np.array(hd["pos"])))
            tasks.append(t); active.append((s, t))
        if "L" not in hands:
            tl = mink.FrameTask("L_prep", "site", position_cost=.05, orientation_cost=0., lm_damping=1e-4)
            tl.set_target(mink.SE3.from_translation(park)); tasks.append(tl)
        post = mink.PostureTask(m, cost=1e-3); post.set_target(q0.copy()); tasks.append(post)
        frozen = [self.da[n] for n in BASE + JAWS]
        for _ in range(iters):
            v = mink.solve_ik(cfg, tasks, .05, "daqp", 1e-3, limits=[mink.ConfigurationLimit(m)])
            v[frozen] = 0; cfg.integrate_inplace(v, .05)
            es = [t.compute_error(cfg) for s, t in active]
            if all(np.linalg.norm(e[:3]) < 1e-3 and np.linalg.norm(e[3:]) < 2e-3 for e in es): break
        errors = []
        for s, t in active:
            e = t.compute_error(cfg)
            errors.append(dict(side=s, position_mm=float(np.linalg.norm(e[:3]) * 1000), orientation_deg=float(np.degrees(np.linalg.norm(e[3:])))))
        return cfg.q.copy(), errors

    def torque(self, q, hd, force):
        m, d = self.m, self.d; d.qpos[:] = q; d.qvel[:] = 0; mujoco.mj_forward(m, d)
        tau = d.qfrc_bias.copy(); jp = np.zeros((3, m.nv)); jr = np.zeros_like(jp)
        mujoco.mj_jacSite(m, d, jp, jr, m.site("R_work").id); tau -= jp.T @ np.array(force)
        mass_site = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "R_mass")
        mujoco.mj_jacSite(m, d, jp, jr, m.site("R_work").id if mass_site < 0 else mass_site); tau -= jp.T @ np.array([0, 0, -hd["held_kg"] * 9.81])
        ratios = {n: abs(tau[self.da[n]]) / LIM[n]["continuous_Nm"] for n in JOINTS}
        j = max(ratios, key=ratios.get)
        return dict(ratio=float(ratios[j]), joint=j, required_Nm=float(abs(tau[self.da[j]])), continuous_Nm=LIM[j]["continuous_Nm"], joints=ratios)

    def grip(self, q, hd, force):
        # Fixed mu/SF; keyed tools carry forces and moments through positive bearing.
        f = np.array(force, float) + [0, 0, -hd["held_kg"] * 9.81]
        demand = float(np.linalg.norm(f))
        m, d = self.m, self.d; d.qpos[:] = q; mujoco.mj_kinematics(m, d)
        rot = d.site_xmat[m.site("R_prep").id].reshape(3, 3)
        moment = float(np.linalg.norm(np.cross(rot @ offset_vector(hd["work_offset_m"]), force)
                                     + np.cross(rot @ offset_vector(hd["mass_offset_m"]), [0, 0, -hd["held_kg"] * 9.81])))
        if hd["grip"] == "friction":
            cap = MU * NORMAL_SUM_N
            margin = cap / (SF * max(demand, 1e-12))
            return dict(mode="wet_pad_friction", mu=MU, normal_sum_N=NORMAL_SUM_N, force_demand_N=demand,
                        force_capacity_N=cap, SF=cap / max(demand, 1e-12), margin=margin)
        margin = min(KEY_FORCE_N / (SF * max(demand, 1e-12)), KEY_MOMENT_NM / (SF * max(moment, 1e-12)))
        return dict(mode="positive_key_bearing", force_demand_N=demand, moment_demand_Nm=moment,
                    bearing_capacity_N=KEY_FORCE_N, moment_capacity_Nm=KEY_MOMENT_NM,
                    SF=SF * margin, margin=margin,
                    bearing_area_mm2=2 * 8 * 24, factored_bearing_stress_MPa=SF * demand / (2 * 8 * 24))

    def run_seed(self, k, rng, previous=None):
        if previous is None:
            q, park = self.initial(rng, k)
        else:
            q = np.array(previous, float); self.d.qpos[:] = q; mujoco.mj_kinematics(self.m, self.d)
            park = self.d.site_xpos[self.m.site("L_prep").id].copy()
        out = dict(k=k, segment=self.seg["label"], poses=[], hits=[], nominal=None, check=None)
        for pidx, hands in enumerate(self.seg["poses"]):
            self.environment_pose(pidx)
            q, errors = self.solve(q, hands, park, k)
            po = dict(q=q.tolist(), errors=errors, floor_margin_mm=self.floor_margin(q) * 1000,
                      base=[float(q[self.qa[n]]) for n in BASE])
            out["poses"].append(po)
            if any(e["position_mm"] > 5 or e["orientation_deg"] > 3 for e in errors):
                out["blocker"] = dict(kind="IK", pose=pidx, **max(errors, key=lambda e: max(e["position_mm"] / 5, e["orientation_deg"] / 3)))
                return out
            out["hits"].extend([dict(pose=pidx, **hit) for hit in self.forbidden(q)])
            hd = hands["R"]
            for label in ("nominal", "check"):
                forces = hd[label + "_forces_N"]
                if forces is None: continue
                for force in forces:
                    tq = self.torque(q, hd, force); gr = self.grip(q, hd, force)
                    if out[label] is None: out[label] = dict(torque=tq, grip=gr, force_N=force, pose=pidx)
                    else:
                        if tq["ratio"] > out[label]["torque"]["ratio"]: out[label]["torque"] = tq; out[label]["force_N"] = force; out[label]["pose"] = pidx
                        if gr["margin"] < out[label]["grip"]["margin"]: out[label]["grip"] = gr
        if out["hits"]: out["blocker"] = dict(kind="collision", **min(out["hits"], key=lambda h: h["real_gap_mm"] - h["required_gap_mm"]))
        elif out["nominal"]["torque"]["ratio"] > 1: out["blocker"] = dict(kind="torque", **out["nominal"]["torque"])
        elif out["nominal"]["grip"]["margin"] < 1: out["blocker"] = dict(kind="grip", **out["nominal"]["grip"])
        else: out["ok"] = True
        return out

    def environment_pose(self, pidx):
        if self.phase["id"] == "P11" and self.seg["label"] == "pump":
            hd = self.seg["poses"][pidx]["R"]
            self.m.geom_pos[self.m.geom("spinner_pump").id, 2] = hd["pos"][2] - .060 - .0175


def summarize(definition, rows, seconds, dz):
    raw_good = [r for r in rows if r["ok"]]
    good = raw_good
    collisionfree = [r for r in rows if r["ik_ok"] and r["collision_free"]]
    ik = [r for r in rows if r["ik_ok"]]
    composites = []; stroke_counts = []
    if len(definition["segments"]) > 1:
        pools = []
        for i, seg in enumerate(definition["segments"]):
            parts = [r["segments"][i] for r in rows]
            passed = sorted([p for p in parts if p.get("ok")], key=lambda p: p["nominal"]["torque"]["ratio"])
            pools.append(passed)
            stroke_counts.append(dict(label=seg["label"], seeds=len(parts), feasible_seeds=len(passed),
                                      ik_seeds=sum(len(p["poses"]) == 2 and all(e["position_mm"] <= 5 and e["orientation_deg"] <= 3 for po in p["poses"] for e in po["errors"]) for p in parts),
                                      collision_free_seeds=sum(p.get("blocker", {}).get("kind") not in ("IK", "collision") for p in parts)))
        # Only each process stroke shares a frozen base. No rule requires unrelated
        # strokes to have the same RNG index. Pair independently admitted strokes.
        for i in range(min(map(len, pools))):
            parts = [pool[i] for pool in pools]
            cr = dict(k=f"composite_{i}", source_seed_ids=[p["k"] for p in parts], segments=parts,
                      ok=True, ik_ok=True, collision_free=True, nominal=None, check=None)
            for label in ("nominal", "check"):
                if label == "check" and not any(p["check"] for p in parts): continue
                cases = [p[label] or p["nominal"] for p in parts]
                cr[label] = dict(max(cases, key=lambda p: p["torque"]["ratio"]))
                cr[label]["grip"] = min(cases, key=lambda p: p["grip"]["margin"])["grip"]
            composites.append(cr)
        good = composites
    pool = good or collisionfree or ik
    best = min(pool, key=lambda r: r["nominal"]["torque"]["ratio"]) if pool else None
    bcheck = min(pool, key=lambda r: r["check"]["torque"]["ratio"]) if pool and pool[0]["check"] else None
    failures = Counter(r["blocker"]["kind"] for r in rows if not r["ok"])
    dominant = None
    if failures:
        kind, count = failures.most_common(1)[0]
        witnesses = [r for r in rows if not r["ok"] and r["blocker"]["kind"] == kind]
        if kind == "IK": rank = lambda r: max(r["blocker"]["position_mm"] / 5, r["blocker"]["orientation_deg"] / 3)
        elif kind == "collision": rank = lambda r: r["blocker"]["required_gap_mm"] - r["blocker"]["real_gap_mm"]
        elif kind == "torque": rank = lambda r: r["blocker"]["ratio"]
        else: rank = lambda r: -r["blocker"]["margin"]
        witness = min(witnesses, key=rank)
        dominant = dict(failed_seeds=count, witness_seed=witness["k"], **witness["blocker"])
    return dict(id=definition["id"], name=definition["name"], verdict="FEASIBLE" if good else "INFEASIBLE",
                seeds=len(rows), feasible_seeds=len(good),
                collision_free_seeds=min(s["collision_free_seeds"] for s in stroke_counts) if stroke_counts else len(collisionfree),
                ik_seeds=min(s["ik_seeds"] for s in stroke_counts) if stroke_counts else len(ik),
                raw_paired_collision_free_seeds=len(collisionfree), raw_paired_ik_seeds=len(ik),
                best_nominal=None if best is None else best["nominal"], best_check=None if bcheck is None else bcheck["check"],
                best_seed=None if best is None else best["k"], best_check_seed=None if bcheck is None else bcheck["k"],
                best_ratios_pool="feasible" if good else "collision_free_diagnostic" if collisionfree else "IK_diagnostic" if ik else "none",
                dominant_blocker=None if good else dominant, rejected_seed_dominant=dominant,
                blocker_counts=dict(failures), adjustment_height_m=dz, elapsed_s=seconds,
                definition=definition, rows=rows, composite_rows=composites,
                raw_paired_feasible_seeds=len(raw_good), stroke_counts=stroke_counts,
                phase_seed_definition="Independent process-stroke seeds paired by rank after admission; frozen base within each stroke" if stroke_counts else "One sampled frozen-base two-pose stroke",
                best_source_seed_ids=best.get("source_seed_ids", [best["k"]]) if best else None)


def run_phase(pid, seeds, dz=0):
    began = time.time(); definition = PHASES[pid](dz)
    checkers = [Checker(definition, seg, dz) for seg in definition["segments"]]
    rngs = [np.random.default_rng(s) for s in range(len(checkers))]; rows = []
    for k in range(seeds):
        parts = []
        for c, rng in zip(checkers, rngs):
            previous = parts[-1]["poses"][-1]["q"] if pid == "P12" and dz and parts and parts[-1].get("ok") else None
            parts.append(c.run_seed(k, rng, previous))
        row = dict(k=k, segments=parts, ok=all(p.get("ok", False) for p in parts),
                   ik_ok=all(all(max(e["position_mm"] / 5, e["orientation_deg"] / 3) <= 1 for po in p["poses"] for e in po["errors"]) and len(p["poses"]) == 2 for p in parts),
                   collision_free=all(not p["hits"] for p in parts), nominal=None, check=None)
        for label in ("nominal", "check"):
            ps = [p[label] for p in parts if p[label] is not None]
            if ps:
                row[label] = dict(max(ps, key=lambda p: p["torque"]["ratio"]))
                row[label]["grip"] = min(ps, key=lambda p: p["grip"]["margin"])["grip"]
        if not row["ok"]: row["blocker"] = next(p["blocker"] for p in parts if not p.get("ok", False))
        rows.append(row)
        if (k + 1) % 12 == 0: print(pid, "adjusted" if dz else "initial", f"{k+1}/{seeds}", f"feasible={sum(r['ok'] for r in rows)}", f"elapsed={time.time()-began:.0f}s", flush=True)
    return summarize(definition, rows, time.time() - began, dz)


def layout_audit():
    pairs = []; min_gap = 100.
    for i, (n, a) in enumerate(LAYOUT.items()):
        c = np.array(a["center"]); h = np.array(a["size"]) / 2
        limits = (-1.8, -.7) if c[0] < -.7 else (-.11, .69)
        assert c[0] - h[0] >= limits[0] and c[0] + h[0] <= limits[1]
        assert c[1] - h[1] >= 0 and c[1] + h[1] <= .6
        for n2, b in list(LAYOUT.items())[i+1:]:
            separation = np.maximum(np.abs(c - b["center"]) - h - np.array(b["size"]) / 2, 0)
            gap = float(np.linalg.norm(separation)); min_gap = min(min_gap, gap)
            pairs.append(dict(objects=[n, n2], gap_mm=gap * 1000))
            assert gap >= .03 - 1e-9, (n, n2, gap)
    return dict(countertop_height_m=.85, stations=LAYOUT, minimum_object_gap_mm=min_gap * 1000, pairs=pairs,
                stove_protected_x_m=[.69, 1.47], permanent_geometry="Original R1 galley; only loose stations replaced")


class MemoryInfo(ctypes.Structure):
    _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong), ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


def process_memory(handle):
    if sys.platform != "win32": return 0
    z = MemoryInfo(); z.cb = ctypes.sizeof(z)
    ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.c_void_p(handle), ctypes.byref(z), z.cb)
    return max(z.PeakWorkingSetSize, z.PeakPagefileUsage) / 2**20


class ProcessEntry(ctypes.Structure):
    _fields_ = [("dwSize", ctypes.c_ulong), ("cntUsage", ctypes.c_ulong), ("th32ProcessID", ctypes.c_ulong),
                ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", ctypes.c_ulong), ("cntThreads", ctypes.c_ulong),
                ("th32ParentProcessID", ctypes.c_ulong), ("pcPriClassBase", ctypes.c_long), ("dwFlags", ctypes.c_ulong),
                ("szExeFile", ctypes.c_wchar * 260)]


def process_tree(pid):
    # The Windows venv executable is a launcher: include its real Python child.
    if sys.platform != "win32": return [pid]
    k = ctypes.windll.kernel32; k.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
    snap = k.CreateToolhelp32Snapshot(2, 0); z = ProcessEntry(); z.dwSize = ctypes.sizeof(z); parents = {}
    try:
        ok = k.Process32FirstW(ctypes.c_void_p(snap), ctypes.byref(z))
        while ok:
            parents[z.th32ProcessID] = z.th32ParentProcessID
            ok = k.Process32NextW(ctypes.c_void_p(snap), ctypes.byref(z))
    finally: k.CloseHandle(ctypes.c_void_p(snap))
    found = {pid}
    while True:
        more = {p for p, parent in parents.items() if parent in found}
        if more <= found: break
        found |= more
    return list(found)


def tree_peak_memory(pid):
    if sys.platform != "win32": return 0
    k = ctypes.windll.kernel32; k.OpenProcess.restype = ctypes.c_void_p; peak = 0.
    for child in process_tree(pid):
        handle = k.OpenProcess(0x410, False, child)
        if handle:
            try: peak = max(peak, process_memory(handle))
            finally: k.CloseHandle(ctypes.c_void_p(handle))
    return peak


def kill_tree(p):
    if sys.platform == "win32":
        k = ctypes.windll.kernel32; k.OpenProcess.restype = ctypes.c_void_p
        for pid in reversed(process_tree(p.pid)):
            handle = k.OpenProcess(1, False, pid)
            if handle:
                try: k.TerminateProcess(ctypes.c_void_p(handle), 1)
                finally: k.CloseHandle(ctypes.c_void_p(handle))
    if p.poll() is None: p.kill()
    p.wait(timeout=10)


def bounded_job(pid, seeds, adjusted):
    cmd = [sys.executable, "-u", str(Path(__file__).resolve()), "--phase", pid, "--seeds", str(seeds)]
    if adjusted: cmd.append("--adjusted")
    path = HERE / "results" / (pid + ("_adjusted" if adjusted else "_initial") + ".log")
    began = time.monotonic(); peak = 0.
    with path.open("w", encoding="utf-8") as log:
        p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
        try:
            while p.poll() is None:
                peak = max(peak, tree_peak_memory(p.pid))
                if time.monotonic() - began > 1140: raise TimeoutError(f"{pid} exceeds 1140 s")
                if peak > 1900: raise MemoryError(f"{pid} exceeds 1900 MiB")
                time.sleep(1)
            if p.returncode: raise RuntimeError(f"{pid} exit {p.returncode}: {path.read_text()[-1600:]}")
        finally:
            if p.poll() is None: kill_tree(p)
    record = dict(phase=pid, adjusted=adjusted, timeout_s=1140, peak_worker_MiB=peak, elapsed_s=time.monotonic() - began, exit_code=p.returncode)
    json_write(path.with_suffix(".resource.json"), record)
    print("WORKER", json.dumps(record), flush=True)
    return record


def main():
    p = argparse.ArgumentParser(); p.add_argument("--phase", choices=PHASES); p.add_argument("--batch", nargs="+", choices=PHASES)
    p.add_argument("--seeds", type=int, default=96); p.add_argument("--workers", type=int, default=4); p.add_argument("--adjusted", action="store_true")
    p.add_argument("--audit", action="store_true"); args = p.parse_args()
    if args.audit:
        json_write(HERE / "results/layout.json", layout_audit()); print("LAYOUT_OK"); return
    if args.seeds < 96: raise ValueError("At least 96 seeds per phase")
    if args.batch:
        if not 1 <= args.workers <= 4: raise ValueError("At most 4 worker processes")
        if len(args.batch) > args.workers: raise ValueError("A foreground chunk contains at most one phase per worker")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
            fs = [ex.submit(bounded_job, pid, args.seeds, args.adjusted) for pid in args.batch]
            for f in concurrent.futures.as_completed(fs): f.result()
    elif args.phase:
        delta = (-.080 if args.phase == "P11" else -.120 if args.phase == "P14" else .050) if args.adjusted else 0.
        result = normalize_result(run_phase(args.phase, args.seeds, delta))
        if sys.platform == "win32":
            ctypes.windll.kernel32.GetCurrentProcess.restype = ctypes.c_void_p
            result["peak_worker_MiB"] = process_memory(ctypes.windll.kernel32.GetCurrentProcess())
        json_write(HERE / "results" / (args.phase + ("_adjusted" if args.adjusted else "_initial") + ".json"), result)
        print("RESULT", args.phase, result["verdict"], result["feasible_seeds"], result["best_nominal"]["torque"]["ratio"] if result["best_nominal"] else None, flush=True)
    else: p.error("Choose --phase, --batch, or --audit")


if __name__ == "__main__": main()
