# Finger design inputs: DH PGC-140-50 fingers for wet produce

Compiled 2026-10-11 by read-only web research. Every number has a source key (see **Sources** at the end) and a source type:
**[M]** manufacturer datasheet/manual · **[P]** peer-reviewed paper · **[O]** other (distributor, preprint, project docs, forum).
"derived" = simple arithmetic or chart reading by me, labelled as such. "not found" = searched, no usable number.

---

## 1. DH Robotics PGC-140-50

| Item | Value | Conditions / notes | Source |
|---|---|---|---|
| Stroke | 50 mm total (manual: "0-50mm, both sides") | Symmetric jaws | [M] S1, S2 |
| Gripping force per jaw | 40–140 N | **Minimum is 40 N per jaw** | [M] S1, S2 |
| Force setting | Register 0x0101, 20–100 % | Manual: it "defines the current for the Gripper. If the current limit is exceeded, the fingers stop and trigger an object detection." The mapping from % to N is **not found** | [M] S2 |
| Position setting | Register 0x0103, 0–1000 ‰ of stroke | 1 ‰ ≈ 0.05 mm (derived) | [M] S2 |
| Speed setting | Register 0x0104, 1–100 % | | [M] S2 |
| Grip state feedback | 0x0201: 0 = moving; 1 = "at reference position. No object detected"; 2 = "stopped due to an object detection"; 3 = object dropped. 0x0202 = actual position (read-only) | With position-limited compliant fingers, the state would likely read "1" while it is holding (my inference). 0x0202 can confirm where the jaws actually stopped | [M] S2 |
| Control mode | "The combination of force control and position control is adopted": it moves to the position target and stops early at the current limit | There is no separate force-only mode in the manual | [M] S2 |
| Repeatability | ±0.03 mm | | [M] S1, S2 |
| Opening/closing time | 0.6 s / 0.6 s | Distributors list **0.75 s / 0.75 s** (conflict) | [M] S1, S2; [O] S4, S5 |
| Recommended workpiece | 3 kg | "depends on the shape … friction of the contact surface, and the acceleration" | [M] S1 |
| Max static vertical load Fz | 300 N | | [M] S1, S2 |
| Allowable static moments | Mx = 7 N·m, My = 7 N·m, Mz = 7 N·m | The moment reference point is not stated (not found) | [M] S1, S2 |
| Max finger length | **not found** (no figure in the catalog, manual or distributor pages) | Derived from Mx/My: lever arm ≤ 7/140 = **50 mm** at 140 N, ≤ 7/40 = 175 mm at 40 N (static only) | derived from S1 |
| Body size | 138.5 × 75 × 75 mm (Ø75 body) | Height includes the standard fingers. One distributor lists 73 mm, which is the finger span | [M] S1; [O] S6 |
| Weight | 1 kg | | [M] S1, S2 |
| IP rating | IP67 | Manual v2.1 table says **IP54** (conflict; appears copied from PGC-50) | [M] S1 vs S2 |
| Current | 0.4 A rated / 1 A peak, 24 V DC ±10 % | Manual v2.1 says 0.25/0.5 A; welectron says 1.2 A peak | [M] S1 vs S2; [O] S4 |
| Noise | < 50 dB | | [M] S1 |
| Flange | ISO 9409-1-50-4-M6; 4× Ø6.5 through holes on PCD Ø50 | | [M] S1 |
| **Jaw ("rail") interface, fingers removed** | Total 4× M4 depth 8 + 2× Ø3 depth 3.5, so **per jaw: 2× M4 + 1× Ø3 dowel hole**, in a line at 5 mm pitch (10 mm M4-to-M4 span). Other drawing dimensions: 26.40, 7 and 4 mm | Read from the "Rail mounting holes" drawing. The hole order M4–Ø3–M4 is my reading of the drawing. **Verify against the DH STEP file** | [M] S2 (Fig 1.3b), S1 |
| **Standard finger mounting plate** | Total 8× M3 depth 5 + 4× Ø3 depth 3.2, so **per plate: 4× M3 + 2× Ø3 pin holes** in a 2 × 3 grid at 5 mm pitch (10 mm span). Other dimensions: 9.60 and 21.70 mm | DH: "If you need to customize the finger, it is recommended to design according to the size of the finger mounting plate" | [M] S1, S2 |
| Standard finger geometry | 17.60 mm wide; tip 19 mm above the body top plus a 1.50 mm gap; 50 mm between inner faces when open, 73 mm outside span | From the front and side views | [M] S1, S2 |
| Blank or standard fingers sold | Ships with "Standard Replaceable Fingertips (J1) ×1 set". A separately sold blank finger is **not found** | | [O] S5 |

## 2. Tomato damage, firmness and safe grasp forces

| Quantity | Value | Conditions | Source |
|---|---|---|---|
| **Non-destructive clamping force** | **< 11.13 N** | Momotaro, 63.8–89.7 mm. Ø50 mm flat probe covered with 3 mm Dragon Skin 30, on a 3 mm DS30 pad, 30 mm/min. Damage criterion: shelf life ≥ 9 days. 11.13 N occurred at about 4 % compression (≈3 mm) | [P] T1 |
| Compression data (same test) | 1 % strain: 2.99–3.96 N. 4 %: 8.33–11.13 N. 6 %: 10.2–19.5 N. 15 %: 34–48 N | Unloaded controls lasted 10–13 days. At 6–15 % compression, shelf life scattered between 4 and 15 days, trending downward | [P] T1 |
| Implied secant firmness | ≈4–5.5 N/mm at 1 %; ≈3–4 N/mm at 4 % | Derived from T1 Table 6. Includes the silicone pads in series | derived |
| Rupture force | 83.5–147.9 N (mean 96.3 N at the equator; per-location means 96–131 N) | Same rig. Elastic stage to d < 12.5 mm | [P] T1 |
| Design guideline per finger | **< 10 N per finger** with a 30 mm wide finger (≈1800 mm² contact) | FEA-based. Cites Li et al. 2010: deformation < 1.5 mm is elastic and does not affect storage. Mean pressure ≈5.6 kPa at 10 N (derived) | [P] T2 |
| Bio-yield of ripe tomato | ≈2.75 N | Cited from Sirisomboon et al. 2012 (J Food Eng 111:618) for Momotaro. The test type was not verified, and the citing paper's own abstract says 2.57 N (internal inconsistency). The gripper measured 1.62 N max per finger | [P] T3 |
| Cell-wall fracture force | 16.88 N red, 21.77 N yellow | Eva F1 (small local cultivar), ELE compression machine | [P] T4 |
| Acceptable firmness | ≥ 1.45 N/mm marketable; ≥ 1.28 N/mm for home use | Instron firmness, cv. Liberto and Criterium | [P] T5 |
| Measured grasp force in a recent gripper | 0.20–0.50 N (set point 0.30 N), 80 % success | FSR on TPU 95A auxetic fingers; tomatoes 43–57 mm, 40–81 g | [P] T6 |
| Grasp-pattern study | Lowest plastic deformation 0.0026 mm (early red) / 0.0098 mm (middle red) at 1 s grasp time and 1 mm/s | Two-finger gripper. Abstract only (seen via search snippet) | [P] T7 |
| Li, Li & Liu 2011 friction, rupture and compressibility values | **not found** (paywalled, abstract only) | | [P] T8 |
| Static contact-pressure bruise threshold (kPa) | **not found** | | — |
| Carrot (for comparison) | Max bruise force 71.90 N at 19.32 mm deformation; E = 0.038 MPa | Round probe, 20 mm/min | [P] T9 |

## 3. Friction: produce against soft materials

| Pair | μ | Conditions | Source |
|---|---|---|---|
| Tomato vs Dragon Skin 30 silicone (3 mm pad) | **μs = 1.41** (range 1.15–1.79, n = 10) | Pull test at 30 mm/min, Momotaro. Surface moisture not stated (taken as dry) | [P] T1 |
| Same pair as cited elsewhere | μs = 1.34 | T2 cites T1 for this value, but T1 reports 1.41 | [P] T2 |
| Fuji apple vs TPU rubber | μs = 0.88 ± 0.03 (vs aluminium 0.14 ± 0.003) | Dry | [P] F1 |
| Potato (Cara, 50–64 mm) vs rubber belting, dynamic | ≈0.66 clean-dry; **≈0.65 clean-wet**; ≈0.62 wet-dirty; ≈0.66 dry-dirty | Read from the Fig. 2 bar chart (±≈0.02, derived). Text: "Moisture also reduced µ"; rubber was the most consistent | [P] F2 |
| Potato vs mild steel / PVC belting, dynamic | Steel ≈0.59 / 0.57 / 0.51 / 0.51; PVC ≈0.74 / 0.57 / 0.48 / 0.63 (same order as the rubber row) | As above | [P] F2 |
| 3M Gripping Material, kinetic (ASTM D1894), **tested against its mating material, not produce** | TB614 (15A): dry 2.8 / wet 2.6. TB631 (30A): 3.3 / 3.0. **TB641 (40A): 3.5 / 3.4**. TB400/TB731 (TPU, 75A): 1.1 / 0.98 | TB641 is the grip tape the UMI fingers use | [M] F3 |
| Textured vs smooth silicone, wet | Qualitative: smooth silicone had a higher COF than fingerprint textures **in dry and water-lubricated** contact with glass; textures were better only with oil | Abstract only | [P] F4 |
| Wet tomato vs silicone or TPU | **not found** | | — |
| Carrot vs any gripper material (dry or wet) | **not found** | | — |
| Potato vs silicone or TPU | **not found** | | — |
| TPU 95A in FEA models | μ = 0.25 (an assumption, not a measurement) | | [O] R3 |

## 4. Fin Ray and concave fingers

| Item | Value | Conditions | Source |
|---|---|---|---|
| Festo DHAS sizes 60 / 80 / 120 | Finger length 50 / 80 / 115 mm; height H1 61.5 / 94.5 / 134.5 mm; base L1 26 / 37.5 / 50 mm; B1 18 / 21.3 / 25 mm; B2 11.8 mm; weight 6.5 / 13 / 29 g | TPE-U (PU), marked "Food-safe". Stroke per jaw should be ≥ 10 mm. Best grip point MP2 = 25 / 40 / 57.5 mm from the base | [M] R1 |
| DHAS indentation stiffness at MP2 | ≈1.8 / ≈1.0 / ≈0.75 N/mm (sizes 60 / 80 / 120); max indentation 12 / 20 / 30 mm | Read from charts (derived) | [M] R1 |
| DHAS-80 retention force FH (pull-out) on Ø70–80 mm cylinder | ≈2–3 N at FG ≈ 20 N; ≈11–14 N at FG ≈ 100 N | FG is the gripping force "of two gripper fingers". HGPL-14 gripper, 23 °C. Chart reading (derived) | [M] R1 |
| DHAS-80 lateral slip force FQ, Ø70–80 mm | ≈3.5–5 N at FG ≈ 20 N; ≈15–16.5 N at FG ≈ 100 N | As above | [M] R1 |
| TPU 95A Fin Ray FEA | 100 mm long × 30 mm wide, 35 mm base. Beams 1.5–4 mm, crossbeams 0.8–1.6 mm, spacing 10–16 mm. Force at 25 mm base displacement against Ø20 mm: **16.0 N** (1.5 mm beams) to **94.1 N** (4 mm beams) | E = 26 MPa, ν = 0.48. FEM only | [O] R3 (preprint) |
| NinjaFlex (85A) soft Fin Ray, thin ribs | Tilted-rib layer jamming raises force at large displacement while keeping contact force minimal at small displacement | Abstract only; numbers not accessed | [P] R2 |
| Classic Fin Ray FEA | Tip moved 8.14 mm at 5 N and 16.8 mm at 10 N; modified design moved ≈15 % more and held 560 g vs 390 g | Silicone (DS30) model; Objet print | [P] R4 |
| 3D-printed Fin Ray, 40 Shore A resin | 50 mm fingers; ≈2.4 N on Ø50 mm; "0.1–3 N for small packaged foods and fruits" | 3-finger, tendon driven | [P] R5 |
| Fin Ray + linkage tomato gripper | Tomatoes up to 73 mm; 13.9 N stem-cutting force | Abstract | [P] R6 |
| Open-source TPU fin-ray finger (UMI) | Polymaker TPU 95A; 0.6 mm nozzle, 0.3 mm layers, 100 % infill (lines), 255 °C, fan 0 %; faced with 3M TB641 grip tape | CAD: Onshape (link under R7). The actuated-UMI repo calls this content "MIT License" | [O] R7 |
| Tip-surface texture | Silicone A30 with a grid of 0.76 mm void depth × 0.95 mm void width: **93.7 %** success vs 28.7 % factory tips, 68.7 % taped, 80.0 % gecko | 1377 grasps, rigid objects | [P] R8 |
| Concave three-finger tomato gripper | 30 mm wide fingers, 60 mm long, 15° arc, 2 mm silicone cover; handles 65–95 mm | Simulation | [P] T2 |
| V-groove / concave jaws for cylinders and spheres | Qualitative: a V-shape localizes and holds a cylinder after a wedge reorients it. **No quantitative V-angle guideline found** | | [P] R9 |

## 5. Printable and castable materials and food contact

| Material | Hardness / properties | Food contact | Source |
|---|---|---|---|
| NinjaFlex TPU | 85A | No statement found | [M] M1 |
| Polymaker PolyFlex TPU95 | ~95A; 100 % modulus 9.4 MPa; tensile 29.0 MPa; elongation 330 % | No statement in the TDS | [M] M2 |
| Kimya TPU-92A | 92A (ISO 868) | "Food contact certification EU 10/2011 and FDA 21 CFR (except black color)" | [M] M3 |
| Kimya PETG-S | Tg 80 °C | "EU 10/2011 and FDA 21 CFR (natural color only)" | [M] M4 |
| Smooth-Sil 940 (platinum silicone) | 40A | On Smooth-On's food-safe list (21 CFR 177.2600, "compliant ≠ FDA approved"). Same list: Smooth-Sil 950/960, SORTA-Clear 18/37/40, Equinox 35/38/40 | [M] M5 |
| Dragon Skin 30 (used in T1) | — | **Not** on the food-safe list. Dragon Skin 25 NV and Mold Star 40T are "limited use" (dry food, water/ice) | [M] M5 |
| Festo DHAS TPE-U | — | Datasheet marks it "Food-safe" | [M] R1 |
| Wet friction of TPU 85A/95A filament | **not found** | | — |
| FDM part caveats | "a filament being 'food-contact compliant' does not automatically make the finished FDM print food safe"; layer grooves trap residue and bacteria; brass nozzle wear and cross-contamination; pigments may not be compliant | Recommends low-risk or short-contact use | [M] M6 |

---

## Sources

**DH Robotics**
- S1 [M] DH PGC series catalog pages (PGC-50-35 / 140-50 / 300-60), hosted by Neobotix: https://www.neobotix-robots.com/fileadmin/user_upload/PGC-Gripper_Datasheet.pdf. The same data is in the DH catalog EN: https://uploads.unchainedrobotics.de/media/file_upload/DH-Robotics-catalog-EN_46faa8dd.pdf
- S2 [M] DH PGC-140 Short Manual v2.1: https://uploads.unchainedrobotics.de/media/file_upload/PGC-140-Short-Manual_v2.1_e46a3c6b.pdf. The official site en.dh-robotics.com returned HTTP 403 to automated fetches.
- S4 [O] welectron: https://www.welectron.com/DH-Robotics-PGC-140-50-Collaborative-Electric-Parallel-Gripper
- S5 [O] OpenELAB: https://openelab.io/products/dhrobotics-pgc14050-heavy-duty-gripper
- S6 [O] Unchained Robotics: https://unchainedrobotics.de/en/products/end-of-arm-effectors/grippers/finger-grippers/dh-robotics-pgc-140

**Tomato and other produce**
- T1 [P] Zhou K. et al. 2022, Int J Agric Biol Eng 15(2):13–24, doi:10.25165/j.ijabe.20221502.6672: https://ijabe.org/index.php/ijabe/article/view/6672
- T2 [P] Zheng Y. et al. 2022, Front. Plant Sci., doi:10.3389/fpls.2022.974456: https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2022.974456/full
- T3 [P] Kultongkham A. et al. 2021, J Agric Eng 52:1090: https://www.agroengineering.org/jae/article/view/1090
- T4 [P] Uba F. et al. 2020, Scientific African, doi:10.1016/j.sciaf.2020.e00616 (abstract via OpenAlex): https://doi.org/10.1016/j.sciaf.2020.e00616
- T5 [P] Batu A. 1998, Turk J Agric For 22(4) (abstract): https://journals.tubitak.gov.tr/agriculture/vol22/iss4/15/
- T6 [P] Ansari S. et al. 2026, Scientific Reports (PMC): https://pmc.ncbi.nlm.nih.gov/articles/PMC13223203/
- T7 [P] Zhang B. et al. 2018, Biosyst Eng 171:245–257 (abstract via search): https://www.sciencedirect.com/science/article/abs/pii/S1537511017306888
- T8 [P] Li Z., Li P., Liu J. 2011, J Food Eng 103:170–178 (abstract only): https://www.phtnet.org/research/download/pdf/mj364.pdf
- T9 [P] Jahanbakhshi A. et al. 2018, Food Sci Nutr 6(7):1898–1903: https://pmc.ncbi.nlm.nih.gov/articles/PMC6189625/

**Friction**
- F1 [P] Fuji apple peel and pulp, Int J Food Prop 2022 (abstract): https://doi.org/10.1080/10942912.2022.2107006
- F2 [P] Bishop C.F.H. et al. 2012, Res Agr Eng 58:114–117: https://rae.agriculturejournals.cz/pdfs/rae/2012/03/05.pdf
- F3 [M] 3M Gripping Material TDS: https://multimedia.3m.com/mws/media/1001810O
- F4 [P] Hao T. et al. 2022, Friction, doi:10.1007/s40544-022-0688-4 (abstract): https://link.springer.com/article/10.1007/s40544-022-0688-4

**Fin Ray and finger design**
- R1 [M] Festo DHAS datasheet 2023/01: https://www.landefeld.com/shop/media/festo/gruppendatenblaetter/dhas_en.pdf
- R2 [P] Elgeneidy, Lightbody, Pearson, RoboSoft 2019 (abstract): https://figshare.com/articles/conference_contribution/Characterising_3D-printed_Soft_Fin_Ray_Robotic_Fingers_with_Layer_Jamming_Capability_for_Delicate_Grasping/25175234
- R3 [O] Multi-objective NN-assisted Fin-Ray optimization (arXiv preprint): https://arxiv.org/html/2506.00494
- R4 [P] Crooks W. et al. 2016, Front Robot AI 3:70: https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2016.00070/full
- R5 [P] Yang Y. et al. 2021, Micromachines 12:1141: https://pmc.ncbi.nlm.nih.gov/articles/PMC8538355/
- R6 [P] An B., Choi T., Kim U. 2025, Comput Electron Agric, doi:10.1016/j.compag.2025.110118 (abstract): https://doi.org/10.1016/j.compag.2025.110118
- R7 [O] UMI hardware guide: https://docs.google.com/document/d/1TPYwV9sNVPAi0ZlAupDMkXZ4CA1hsZx7YDMSmcEy6EU. Soft finger CAD: https://cad.onshape.com/documents/c8d06048fc2e425772f2749c. License note: https://github.com/actuated-umi/actuated-umi-gripper
- R8 [P] Guo M. et al., ICRA 2017: https://goldberg.berkeley.edu/pubs/gripper-tip-surface-design-icra-2017-camera-ready.pdf
- R9 [P] Chavan-Dafle N., Lee K., Rodriguez A., CASE 2018: https://dspace.mit.edu/handle/1721.1/130008

**Materials**
- M1 [M] NinjaTek NinjaFlex: https://ninjatek.com/shop/ninjaflex/
- M2 [M] Polymaker PolyFlex TPU95 TDS v4: https://cdn.shopify.com/s/files/1/1339/4265/files/Polymaker_PolyFlex_TPU95_TDS_V4.pdf
- M3 [M] Kimya TPU-92A: https://shop3duniverse.com/cdn/shop/t/116/assets/kimya-tpu-92a-3d-filament_en.pdf
- M4 [M] Kimya PETG-S: https://shop3duniverse.com/cdn/shop/t/137/assets/kimya-petg-s-3d-filament_en_1.pdf
- M5 [M] Smooth-On food-safe list: https://www.smooth-on.com/page/food-safe-materials-list/ and Smooth-Sil 940: https://www.smooth-on.com/products/smooth-sil-940/
- M6 [M] Polymaker food-safety guidance: https://wiki.polymaker.com/polymaker-products/more-about-our-products/safety-in-3d-printing/food-safety
