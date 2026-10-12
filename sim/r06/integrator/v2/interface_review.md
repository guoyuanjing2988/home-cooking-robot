# R06 revision2 interface decision record

The selected simulation is L17: a fixed, side-mounted UR5e, four ingredient pans,
two broad docking lands and a locked enclosure. The closed guard envelope is
1606 x 906 mm. This is a 156 mm width and156 mm depth increase over the1450 x750
source concept, justified by the full arm/base and open approach corridors.
The floor render is not part of the module footprint. The outward door needs
additional stopped-service space. No rail is used in the selected variant.

The model is **not a released appliance design**. It has a working container
interface, tested clamp/lid motions and explicit unresolved food-processing
interfaces. The lack of a wash/cradle/peel/cut implementation is a failure, not
an implied vendor feature or an impossible-to-simulate quality waiver.

## Commodity comparison

* Robot Coupe CL20 has a documented325 x310 x570 mm envelope,400 W drive,
  diameter58 mm feed tube and104 square-centimetre larger hopper. Its18289 disc
  is nominally5 mm. A closed GN pan is not its loading interface. The supplied
  potato's65 x70 mm cross-section exceeds the small tube. The larger aperture
  and terminal recovery still need an actual operating-interface model; nominal
  disc thickness does not establish all the requested slice tolerances.
  [OEM product](https://www.robot-coupe.com/uk/en_GB/p/vegetable-preparation-machines-cl-20/18232)
* Nemco55200AN Easy Slicer is better documented mechanically. The operating
  manual describes opening a cover, loading a trough, closing the cover and
  cranking while applying pusher pressure. The complete envelope with handle
  out is533.4 x279.4 x406.4 mm; the blade plate is234.95 mm diameter. Its fixed
  3/16-inch cut is4.7625 mm. An automated implementation needs full crank,
  cover, pusher, individual-root retention, catch and cleaning interfaces. It
  is not a whole-pan inlet and does not certify the final10 mm stub or yield.
  [Manual](https://nemco.com/wp-content/uploads/2025/06/Operations_Manual_and_Parts_Breakdown-55200AN_10-2014.pdf),
  [dimensions](https://nemco.com/wp-content/uploads/2025/06/55200AN_Easy_Slicer_11-2019.pdf)
* DitoSama T-series offers5–25 kg batch peelers with optional washing/knife
  plates. This does not establish controlled0.2–0.8 mm peeling for this120 g
  carrot or200 g potato, every eye, or subsequent slice geometry.
  [OEM range](https://www.ditosama.com/en/products/multipurpose-peelers/)

These devices are not silently represented by a small generic box. None was
purchased, contacted, or declared adopted and qualified. A real slicer would
resolve some cutting hardware but would add ingredient loading and controls;
the whole-pan concept remains a custom interface development proposal.

## Modeled container and docking contract

* Full source GN pan265 x163 x100 mm; all source food, insert, lid, keys and
  UR5e collision solids retained. Complete EOAT cup translated140 mm; no
  reduction of palm, cup, jaw or food envelopes. L17 also translates the full
  cup80 mm upward and updates the tool CoM to clear returned-pan lid shafts.
  Jaw opening is a physical
  actuator-range change to110 mm inner opening, not a smaller jaw.
* Key center relative to pan origin: (0,-155,150) mm. Source-size key and
  backer are connected by neck, lower bridge and bolts. Added lid/handle
  budget0.40 kg per pan is included in torque/grip and combined CoM.
* Station support330 x245 x24 mm; input/output support290 x210 x24 mm.
  Pan bottom seats exactly on its owning top face. No pocket insertion.
  Approach/lift is80 mm, with only the first50 mm eligible for a support
  window and only until the specific pair reaches5 mm separation.
* Station retention:20 x140 x35 mm shoe, named `wash_retention_x` or
  `process_retention_x`,34.5 mm closing stroke onto that pan's right face.
  Other solid pairs have no retention exemption. Arm withdraws before
  appliance operation. Structural reactions pass into the frame, not the arm.
* Full pan lid opens to-1.7 rad on its source hinge. L13 bolts and L14's
  through-shaft obstructed the lid. L15 retains the complete150 mm shaft,
  moves it toY=115 mm and enlarges the outside gearbox to41 x60 x48 mm.
  A33.5 mm parallel-axis offset is the proposed sealed geared transmission.
  The drive mass allocation, sealing, transmission internals and actual
  power/brake parts are engineering assumptions, not supplier specifications.
* Door remains locked; no person inside. Input and output are the four labeled
  front pan bays behind the stopped-service access door. Output acceptance
  remains false until all food quality and mass-transfer tests pass.

## Washing: explicit boundary of verification

The land, catch basin, manifold, integral lid drive, side retention, below-deck
drive enclosure and household utility envelopes exist. Clamp and lid sweeps
are checked, including moving appliance versus environment solids. The2 L
working charge is below the source pan's2.8 L nominal capacity; freeboard,
overflow, drain valves, plumbing apertures and food-safe wetted construction
are **not** qualified by this arithmetic.

The insert has the source120 mm vertical slide joint. Its geometric sweep is
checked as a conditional mechanism diagnostic. There is no complete drive,
latch/guide, turn/brush trajectory or independently retained insert transaction. Every
surface and basal crease is therefore not accessible through an executed
program. Timed spraying or soaking cannot change `raw_unwashed` to `washed`.
Potato still requires fresh changes until no white swirl and draining without
a puddle; bok choy requires root separation, every crease,600 s soak and grit
inspection. Dirty/clean sanitation and scraps are unresolved.

## Processing: actual opening, pusher, retention and obstruction

The330 x245 mm loading land has no surrounding insertion cage. The full blade
is3 x140 x110 mm with40 x180 x30 mm carriage,100 mm rear parking slide and275 mm
downward slide. The pusher is20 x80 x90 mm on a200 mm feed axis. A full rear
guard and the cell enclosure remain present, with monitored cover states.
The carriage and pusher have full parked and commanded swept geometry.
L16/L17 add a250 mm lateral parking slide,330 x60 x40 mm rail and100 x80 x80 mm
motor envelope so the complete blade can leave the vertical pan corridor.

Food is still inside the full100 mm pan wall. Without a supported cradle that
lifts food out of the pan, the pusher meets the pan side before reaching the
food. A blade lowering into a static uncut solid is not an executed cutting
transition. No blanket pan/tool contact permission is granted. The same-frame
worktop/drive/waste-routing overlaps also require fabrication apertures and a
complete cleanable design; fixed-solid overlap is not treated as a food path.

Still missing: independent food cradle/support, controlled peel coverage and
eyes, stable trim/facet reorientation, every cut child/scrap geometry, terminal
edible-piece recovery, greens separation/crease presentation, tomato core-only
removal and controlled radial slicing, and unobstructed retained scrap delivery.
These are named failed obligations. They are not removed by grouping the
recipe into28 supervisory events.

## Loads and timing

The arm carries a pan; it does not take appliance cutting reactions after a
verified support and withdrawal. Carry-force basis is4.2 kg x0.3 m/s² x1.5 =
1.89 N. All selected witnesses and accepted paths require the final Cartesian
force-envelope replay. Root cutting force data were measured at20–40 mm/min;
the0.5 mm/s conditional rate remains inside that range. The source scaled
process forces are structural proxies, not a1000 N press qualification or a
produce-damage guarantee. [Primary study](https://iseki-food-ejournal.com/article/69/pdf)

Complete prep time is null while the meal is blocked. Actual path durations,
stops and the successful clamp/lid motions are reported separately. No
unexecuted parallelism or source45-minute estimate is promoted to a result.
