FreeCAD native solid concepts and STEP, millimetres. The 18 IDs denote distinct
custom designs, with physical quantities in cad_manifest.json. All bodies have
positive volume and valid solids; several are multi-body assemblies. Local library
objects overlap by design; use counter_layout.FCStd for the assembled layout.

Master C01 + mate C02 is a fixed bolted wrist interface with antirotation dowels.
C03 is the common gripper-picked key, not an automatic wrist changer. C04 includes
collar tabs, legs and a connected top bridge; its removable retention is a design
requirement still needing captive hardware. C05 supports root ends so fingers can
grasp the exposed centre. C06 is thin folded/welded sheet. C18 uses an offset handle.
CAD/tool coordinate mapping for the bowl is documented in process_v2.json.

Manufacturing release gates: measured wrist/rim/Nemco datums; matched pusher and
blade; continuous food loading support rather than a free fall; feed transmission
and terminal release; load-bearing joints; motor running torque; parked-blade
catch; brake/interlock/hinge details; safe retention and hygienic finish. C16 is a
review blank with nominal holes, explicitly not a fitted Nemco replacement part.
Purchased objects and drives in the layout are envelope proxies.

Use certified food-contact 304/316L, grade-specific POM-C and molded approved
silicone. Direct-food FDM is not selected; prototypes may be printed for external
fit/handle trials with no food contact. Deburr, radius, polish and eliminate blind
crevices; disassemble food-path parts for cleaning. No material label substitutes
for a finished assembly's compliance and cleaning validation.
