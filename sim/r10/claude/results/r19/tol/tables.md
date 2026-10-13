### Nominal: exact minimum vs the reserve the checker reported

| Scene | States | Exact gate reserve (mm) | Exact gap (mm) | Binding pair, where | Checker-reported reserve (mm) |
|---|---|---|---|---|---|
| play:wok | 4588 | 4.00 | 9.00 | R_gripper_r15_wok_t0 / r15_cooker, start | 2.02 |
| app:wok:0 | 54 | 9.98 | 19.98 | R_geom_16 / r15_plate, approach@pick#0 step 0 (0 cm back) | 2.4 |
| app:wok:1 | 54 | 9.98 | 19.98 | R_geom_16 / r15_plate, approach@set down#16 step 0 (0 cm back) | 2.4 |
| play:spatula | 2642 | 4.80 | 9.80 | R_gripper_r18_spat_blade4 / raw_tomato, kf 0->1 (pick -> lifted) | 2.04 |
| app:spatula:0 | 168 | 27.03 | 32.03 | R_finger_plus / r16_spatula_handle, approach@pick#0 step 0 (0 cm back) | 27.0 |
| play:lever | 128 | 8.61 | 13.61 | R_gripper_r17_lever_bar / r17_lever_hub, kf 0->1 (closed -> open) | 5.98 |
| app:lever:0 | 19 | 20.00 | 25.00 | R_finger_minus / r17_lever_tip, approach@closed#0 step 2 (2 cm back) | 20.0 |
| app:lever:1 | 19 | 15.88 | 20.88 | R_finger_minus / r17_faucet_column, approach@open#1 step 0 (0 cm back) | 7.4 |
| play:lid | 2410 | 1.00 | 6.00 | R_gripper_r16_lid_rim / r16_rack_base, kf 7->8 (over the rack -> in the rack) | 1.0 |
| app:lid:0 | 55 | 14.64 | 19.64 | R_finger_minus / r16_lid_rim, approach@lift off#0 step 0 (0 cm back) | 10.0 |
| app:lid:1 | 166 | 14.64 | 19.64 | R_finger_plus / r16_lid_rim, approach@in the rack#8 step 0 (0 cm back) | 7.2 |
| play:spider | 4335 | 5.37 | 10.37 | R_gripper_r16_spider_bowl / r16_pot_ear+1, kf 1->2 (- -> out and up) | 2.03 |
| app:spider:0 | 52 | 5.43 | 15.43 | R_geom_11 / r14_hood, approach@pick#0 step 0 (0 cm back) | 4.2 |
| app:spider:1 | 52 | 5.43 | 15.43 | R_geom_11 / r14_hood, approach@on the rest#18 step 0 (0 cm back) | 4.2 |
| edge:H_SINK__H_WOK | 215 | 80.00 (>=) | 80.00 | -, H_SINK->H_WOK 0.0% | 60.0 |
| edge:H_SPAT__H_SINK | 209 | 80.00 (>=) | 80.00 | -, H_SPAT->H_SINK 0.0% | 60.0 |
| edge:H_WOK__H_POT | 248 | 80.00 (>=) | 80.00 | -, H_WOK->H_POT 0.0% | 60.0 |
| edge:LEV_C__H_SINK | 1635 | 8.57 | 18.57 | R_geom_25 / r07_closed_door_1_0, LEV_C->H_SINK 11.8% | 2.2 |
| edge:LEV_C__H_SPAT | 1835 | 8.57 | 18.57 | R_geom_25 / r07_closed_door_1_0, LEV_C->H_SPAT 11.8% | 2.3 |
| edge:LEV_C__H_WOK | 1849 | 8.57 | 18.57 | R_geom_25 / r07_closed_door_1_0, LEV_C->H_WOK 11.7% | 2.3 |
| edge:LEV_O__H_SINK | 1489 | 2.03 | 12.03 | R_geom_25 / r07_closed_door_1_0, LEV_O->H_SINK 17.2% | 2.0 |
| edge:LEV_O__H_SPAT | 1726 | 2.39 | 12.39 | R_geom_25 / r07_closed_door_1_0, LEV_O->H_SPAT 15.0% | 2.1 |
| edge:LEV_O__H_WOK | 1735 | 2.03 | 12.03 | R_geom_25 / r07_closed_door_1_0, LEV_O->H_WOK 15.1% | 2.0 |
| edge:LEV_O__WOK | 2555 | 2.03 | 12.03 | R_geom_25 / r07_closed_door_1_0, LEV_O->WOK 10.1% | 2.0 |
| edge:LID_POT__H_POT | 1804 | 23.43 | 30.52 | R_geom_10 / r14_hood, LID_POT->H_POT 0.0% | 19.8 |
| edge:LID_POT__H_WOK | 1944 | 23.43 | 30.81 | R_geom_10 / r14_hood, LID_POT->H_WOK 0.0% | 19.8 |
| edge:LID_RACK__H_POT | 2002 | 25.81 | 30.81 | R_finger_minus / u_rack_r16_lid_tab, LID_RACK->H_POT 0.0% | 2.1 |
| edge:LID_RACK__H_WOK | 2223 | 25.81 | 30.81 | R_finger_minus / u_rack_r16_lid_tab, LID_RACK->H_WOK 0.0% | 2.3 |
| edge:SPAT__H_SINK | 1244 | 49.64 | 54.64 | R_finger_plus / r16_spatula_handle, SPAT->H_SINK 4.0% | 38.0 |
| edge:SPAT__H_SPAT | 1018 | 56.99 | 61.99 | R_finger_minus / r16_spatula_handle, SPAT->H_SPAT 6.4% | 36.5 |
| edge:SPAT__LEV_C | 2842 | 8.57 | 18.57 | R_geom_25 / r07_closed_door_1_0, SPAT->LEV_C 92.8% | 2.3 |
| edge:SPIDER__H_POT | 1987 | 17.64 | 23.54 | R_geom_11 / r14_hood, SPIDER->H_POT 0.0% | 2.1 |
| edge:SPIDER__H_WOK | 2203 | 17.64 | 26.69 | R_geom_11 / r14_hood, SPIDER->H_WOK 0.0% | 2.3 |
| edge:WOK__H_POT | 1099 | 25.33 | 30.33 | R_finger_plus / r15_wok_grip, WOK->H_POT 0.0% | 2.0 |
| edge:WOK__H_SINK | 1040 | 25.33 | 30.33 | R_finger_plus / r15_wok_grip, WOK->H_SINK 0.0% | 2.1 |
| edge:WOK__H_WOK | 859 | 25.33 | 30.33 | R_finger_plus / r15_wok_grip, WOK->H_WOK 0.0% | 2.1 |

### Cart pose tolerance per axis (worst sign): gate / contact; binding pair at the gate

| Action / edge | x (mm) | y (mm) | z (mm) | yaw (deg) | tilt_x (deg) | tilt_y (deg) | First to bind (gate) |
|---|---|---|---|---|---|---|---|
| wok | >15 / >15 | 10.3+ / >15 | 4- / 8.98- | 0.816+ / 1.23+ | 0.544- / 0.916- | 0.328+ / 0.734+ | tilt_y: R_gripper_r15_wok_t0 / r15_cooker, start (kf 0) (play:wok) |
| spatula | 4.78- / 9.78- | 5.78+ / 10.8+ | 9.28- / >15 | 0.647+ / 1.32+ | 0.347- / 0.647- | 0.294- / 0.603- | tilt_y: R_gripper_r18_spat_blade4 / raw_tomato, kf 0->1 (pick -> lifted) (play:spatula) |
| lever | >15 / >15 | 9.91+ / >15 | >15 / >15 | 1.3+ / >1.5 | 0.381- / 0.603- | 0.863- / 1.27- | tilt_x: R_gripper_r17_lever_bar / r17_lever_hub, kf 0->1 (closed -> open) (play:lever) |
| lid | 14- / >15 | 9.97+ / 15+ | 0.988- / 5.98- | 1.4+ / >1.5 | 0.122- / 0.653- | 0.137+ / 0.824+ | tilt_x: R_gripper_r16_lid_rim / r16_rack_base, kf 7->8 (over the rack -> in the rack) (play:lid) |
| spider | >15 / >15 | 5.56+ / >15 | 9.28- / 15- | >1.5 / >1.5 | 0.222- / 0.631- | 0.961+ / 1.2+ | tilt_x: R_geom_11 / r14_hood, approach@pick#0 step 0 (0 cm back) (app:spider:0) |
| H_SINK__H_WOK | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | >1.5 / >1.5 | >1.5 / >1.5 | yaw: ,  (edge:H_SINK__H_WOK) |
| H_SPAT__H_SINK | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | >1.5 / >1.5 | >1.5 / >1.5 | yaw: ,  (edge:H_SPAT__H_SINK) |
| H_WOK__H_POT | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | >1.5 / >1.5 | >1.5 / >1.5 | yaw: ,  (edge:H_WOK__H_POT) |
| LEV_C__H_SINK | >15 / >15 | >15 / >15 | 10.2+ / >15 | 1.26+ / >1.5 | 1.26- / >1.5 | 0.819- / 1.15- | tilt_y: R_geom_25 / r07_closed_door_1_0, LEV_C->H_SINK 11.6% (edge:LEV_C__H_SINK) |
| LEV_C__H_SPAT | >15 / >15 | >15 / >15 | 10.2+ / >15 | 1.26+ / >1.5 | 1.26- / >1.5 | 0.819- / 1.15- | tilt_y: R_geom_25 / r07_closed_door_1_0, LEV_C->H_SPAT 11.6% (edge:LEV_C__H_SPAT) |
| LEV_C__H_WOK | >15 / >15 | >15 / >15 | 10.2+ / >15 | 1.26+ / >1.5 | 1.26- / >1.5 | 0.819- / 1.15- | tilt_y: R_geom_25 / r07_closed_door_1_0, LEV_C->H_WOK 11.5% (edge:LEV_C__H_WOK) |
| LEV_O__H_SINK | >15 / >15 | 3.91+ / >15 | 2.38+ / 14+ | 0.366+ / >1.5 | 0.341- / >1.5 | 0.222- / 1.2- | tilt_y: R_geom_25 / r07_closed_door_1_0, LEV_O->H_SINK 17.2% (edge:LEV_O__H_SINK) |
| LEV_O__H_SPAT | >15 / >15 | 5+ / >15 | 2.72+ / 14.3+ | 0.581+ / >1.5 | 0.509- / >1.5 | 0.581- / 1.2- | tilt_x: R_geom_25 / r07_closed_door_1_0, LEV_O->H_SPAT 15.5% (edge:LEV_O__H_SPAT) |
| LEV_O__H_WOK | >15 / >15 | 3.91+ / >15 | 2.34+ / 14+ | 0.366+ / >1.5 | 0.341- / >1.5 | 0.222- / 1.2- | tilt_y: R_geom_25 / r07_closed_door_1_0, LEV_O->H_WOK 15.0% (edge:LEV_O__H_WOK) |
| LEV_O__WOK | >15 / >15 | 3.91+ / >15 | 2.34+ / 14+ | 0.366+ / >1.5 | 0.341- / >1.5 | 0.222- / 1.2- | tilt_y: R_geom_25 / r07_closed_door_1_0, LEV_O->WOK 10.1% (edge:LEV_O__WOK) |
| LID_POT__H_POT | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | 1.29- / >1.5 | >1.5 / >1.5 | tilt_x: R_geom_10 / r14_hood, LID_POT->H_POT 0.0% (edge:LID_POT__H_POT) |
| LID_POT__H_WOK | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | 1.29- / >1.5 | >1.5 / >1.5 | tilt_x: R_geom_10 / r14_hood, LID_POT->H_WOK 0.0% (edge:LID_POT__H_WOK) |
| LID_RACK__H_POT | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | >1.5 / >1.5 | >1.5 / >1.5 | yaw: ,  (edge:LID_RACK__H_POT) |
| LID_RACK__H_WOK | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | >1.5 / >1.5 | >1.5 / >1.5 | yaw: ,  (edge:LID_RACK__H_WOK) |
| SPAT__H_SINK | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | >1.5 / >1.5 | >1.5 / >1.5 | yaw: ,  (edge:SPAT__H_SINK) |
| SPAT__H_SPAT | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | >1.5 / >1.5 | >1.5 / >1.5 | yaw: ,  (edge:SPAT__H_SPAT) |
| SPAT__LEV_C | >15 / >15 | >15 / >15 | 10.2+ / >15 | 1.26+ / >1.5 | 1.26- / >1.5 | 0.819- / 1.15- | tilt_y: R_geom_25 / r07_closed_door_1_0, SPAT->LEV_C 93.0% (edge:SPAT__LEV_C) |
| SPIDER__H_POT | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | 0.725- / 1.13- | 1.1+ / >1.5 | tilt_x: R_geom_11 / r14_hood, SPIDER->H_POT 0.0% (edge:SPIDER__H_POT) |
| SPIDER__H_WOK | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | 0.725- / 1.13- | 1.1+ / >1.5 | tilt_x: R_geom_11 / r14_hood, SPIDER->H_WOK 0.0% (edge:SPIDER__H_WOK) |
| WOK__H_POT | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | >1.5 / >1.5 | >1.5 / >1.5 | yaw: ,  (edge:WOK__H_POT) |
| WOK__H_SINK | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | >1.5 / >1.5 | >1.5 / >1.5 | yaw: ,  (edge:WOK__H_SINK) |
| WOK__H_WOK | >15 / >15 | >15 / >15 | >15 / >15 | >1.5 / >1.5 | >1.5 / >1.5 | >1.5 / >1.5 | yaw: ,  (edge:WOK__H_WOK) |

### Grid (measured): min gate reserve over all states, worst sign, at each cart offset (mm; "≥10" = above 10 mm; negative = below the 10/5 mm gate, the gap is that + 10 or + 5)

| Action / edge | x ±2 | x ±5 | x ±10 | y ±2 | y ±5 | y ±10 | z ±2 | z ±5 | yaw ±0.2 | yaw ±0.5 | yaw ±1 | tilt_x ±0.1 | tilt_x ±0.2 | tilt_x ±0.5 | tilt_y ±0.2 | tilt_y ±0.5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| wok | 4.00 | 4.00 | 4.00 | 4.00 | 4.00 | 0.29 | 2.00 | -1.00 | 4.00 | 3.90 | -2.23 | 3.27 | 2.55 | 0.34 | 1.58 | -2.08 |
| spatula | 2.80 | -0.20 | -5.00 | 3.81 | 0.81 | -4.19 | 4.49 | 2.64 | 3.32 | 1.10 | -2.62 | 4.14 | 2.48 | -2.52 | 1.56 | -3.29 |
| lever | 8.61 | 8.61 | 6.01 | 6.88 | 4.28 | -0.07 | 7.61 | 6.44 | 7.43 | 5.67 | 2.78 | 6.36 | 4.11 | -2.63 | 7.92 | 6.74 |
| lid | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | -0.01 | -1.00 | -4.00 | 1.00 | 1.00 | 1.00 | 0.20 | -0.61 | -3.05 | -0.43 | -2.60 |
| spider | 4.56 | 3.42 | 1.71 | 3.48 | 0.57 | -4.29 | 4.21 | 2.46 | 4.97 | 4.44 | 3.69 | 2.99 | 0.55 | -6.76 | 4.77 | 4.15 |
| LEV_C__H_SINK | 8.57 | 8.57 | 7.00 | 7.49 | 5.86 | 3.15 | 6.89 | 4.37 | 7.20 | 5.16 | 1.75 | 7.91 | 7.25 | 5.23 | 6.46 | 3.32 |
| LEV_C__H_SPAT | 8.57 | 8.57 | 7.00 | 7.49 | 5.86 | 3.15 | 6.89 | 4.37 | 7.21 | 5.15 | 1.75 | 7.91 | 7.25 | 5.23 | 6.46 | 3.32 |
| LEV_C__H_WOK | 8.57 | 8.57 | 7.00 | 7.49 | 5.86 | 3.15 | 6.89 | 4.37 | 7.21 | 5.15 | 1.75 | 7.91 | 7.25 | 5.23 | 6.46 | 3.32 |
| LEV_O__H_SINK | 2.03 | 2.03 | 2.03 | 1.00 | -0.55 | -3.13 | 0.32 | -2.24 | 0.92 | -0.74 | -3.50 | 1.44 | 0.85 | -0.95 | 0.20 | -2.51 |
| LEV_O__H_SPAT | 2.20 | 2.05 | 2.03 | 1.43 | 0.00 | -2.31 | 0.66 | -1.95 | 1.50 | 0.30 | -1.36 | 1.90 | 1.42 | 0.05 | 1.21 | 0.14 |
| LEV_O__H_WOK | 2.03 | 2.03 | 2.03 | 0.99 | -0.56 | -3.14 | 0.32 | -2.25 | 0.92 | -0.74 | -3.49 | 1.44 | 0.85 | -0.95 | 0.20 | -2.51 |
| LEV_O__WOK | 2.03 | 2.03 | 2.03 | 1.00 | -0.55 | -3.13 | 0.32 | -2.25 | 0.92 | -0.74 | -3.50 | 1.44 | 0.85 | -0.95 | 0.20 | -2.52 |
| SPAT__LEV_C | 8.57 | 8.57 | 7.00 | 7.49 | 5.86 | 3.15 | 6.89 | 4.37 | 7.21 | 5.15 | 1.75 | 7.91 | 7.25 | 5.23 | 6.46 | 3.32 |
| SPIDER__H_POT | ≥10 | ≥10 | ≥10 | ≥10 | ≥10 | 7.81 | ≥10 | ≥10 | ≥10 | ≥10 | ≥10 | ≥10 | ≥10 | 5.48 | ≥10 | ≥10 |
| SPIDER__H_WOK | ≥10 | ≥10 | ≥10 | ≥10 | ≥10 | 7.81 | ≥10 | ≥10 | ≥10 | ≥10 | ≥10 | ≥10 | ≥10 | 5.48 | ≥10 | ≥10 |

### Fixture and grasp tolerance (worst axis and sign; gate / contact, mm or deg)

| Action | Fixture group: tolerance, binding pair | Grasp offset (tool x/y/z) | Grasp turn about the jaw axis |
|---|---|---|---|
| wok | cooker 4 / 8.98 (R_gripper_r15_wok_t0 / r15_cooker); faucet_body 10.3 / 15 (R_gripper_r15_wok_t4_2 / r17_faucet_spout); plate1 11 / 15 (R_geom_16 / r15_plate); upper 12.6 / 15 (R_geom_26 / r14_hood) | 4.41 / 9.91 | 0.938 / 2.12 |
| spatula | raw 4.78 / 9.78 (R_gripper_r18_spat_blade4 / raw_tomato); bowls 5.78 / 10.8 (R_gripper_r18_spat_blade2 / stored_bowl_leafy_greens_collar_wall4); cooker 7.47 / 14 (R_gripper_r18_spat_blade0 / r15_wok_t4_9) | 4.78 / 9.78 | 0.953 / 1.79 |
| lever | faucet_body 9.91 / 15 (R_gripper_r17_lever_bar / r17_lever_hub) | 8.6 / 13.6 | 4 / 4 |
| lid | lid_rack 1 / 5.97 (R_gripper_r16_lid_rim / r16_rack_base); pot 3 / 7.97 (R_gripper_r16_lid_rim / r16_pot_wall0); upper 9.97 / 15 (R_gripper_r16_lid_rim / r14_hood); counter 11 / 15 (R_gripper_r16_lid_rim / counter_right_piece6) | 0.988 / 5.98 | 0.491 / 1.31 |
| spider | upper 5.56 / 15 (R_geom_11 / r14_hood); pot 7.72 / 15 (R_gripper_r16_spider_bowl / r16_pot_ear+1) | 5.94 / 11.6 | 1.03 / 2.01 |

### Budget utilization U (worst-case linear / RSS); U <= 1 fits. Gate = keeps the 10/5 mm gaps; contact = keeps any clearance

| Action / edge | as_designed | R09_requirement | dock_stops | touch_off | Largest terms (as designed, contact) |
|---|---|---|---|---|---|
| wok | gate 7.12/2.7, contact 3.81/1.33 | gate 2.57/1.19, contact 1.34/0.57 | gate 2.44/1.15, contact 1.22/0.53 | gate 2.23/1.13, contact 1.14/0.52 | grasp_turn 2.0/2.119 = 0.94, fixture:plate1 10/15.0 = 0.67, odometry_x 5.0/15.0 = 0.33 |
| spatula | gate 10.35/4.12, contact 5.23/2.07 | gate 5.75/3.37, contact 2.89/1.67 | gate 5.59/3.34, contact 2.81/1.65 | gate 5.43/3.34, contact 2.72/1.65 | fixture:raw 15/9.777 = 1.53, grasp_turn 2.0/1.789 = 1.12, odometry_x 5.0/9.777 = 0.51 |
| lever | gate 3.45/1.09, contact 2.75/0.87 | gate 1.06/0.4, contact 0.91/0.36 | gate 1.15/0.42, contact 0.9/0.34 | gate 1.01/0.39, contact 0.79/0.32 | grasp_turn 2.0/4.0 = 0.5, load_tilt_x 0.25/0.603 = 0.41, odometry_x 5.0/15.0 = 0.33 |
| lid | gate 17.28/5.97, contact 4.56/1.77 | gate 5.75/2.49, contact 1.75/0.84 | gate 6.38/2.5, contact 1.69/0.82 | gate 5.78/2.41, contact 1.53/0.8 | grasp_turn 2.0/1.306 = 1.53, load_tilt_x 0.25/0.653 = 0.38, fixture:pot 3/7.969 = 0.38 |
| spider | gate 6.47/2.5, contact 3.23/1.22 | gate 2.19/1.08, contact 1.17/0.56 | gate 2.43/1.12, contact 1.15/0.55 | gate 2.17/1.09, contact 1.04/0.54 | grasp_turn 2.0/2.006 = 1.0, load_tilt_x 0.25/0.631 = 0.4, odometry_x 5.0/15.0 = 0.33 |
| H_SINK__H_WOK | gate 1.57/0.52, contact 1.57/0.52 | gate 0.56/0.24, contact 0.56/0.24 | gate 0.4/0.13, contact 0.4/0.13 | gate 0.34/0.11, contact 0.34/0.11 | odometry_x 5.0/15.0 = 0.33, dock_yaw 0.3/1.5 = 0.2, load_tilt_x 0.25/1.5 = 0.17 |
| H_SPAT__H_SINK | gate 1.57/0.52, contact 1.57/0.52 | gate 0.56/0.24, contact 0.56/0.24 | gate 0.4/0.13, contact 0.4/0.13 | gate 0.34/0.11, contact 0.34/0.11 | odometry_x 5.0/15.0 = 0.33, dock_yaw 0.3/1.5 = 0.2, load_tilt_x 0.25/1.5 = 0.17 |
| H_WOK__H_POT | gate 1.57/0.52, contact 1.57/0.52 | gate 0.56/0.24, contact 0.56/0.24 | gate 0.4/0.13, contact 0.4/0.13 | gate 0.34/0.11, contact 0.34/0.11 | odometry_x 5.0/15.0 = 0.33, dock_yaw 0.3/1.5 = 0.2, load_tilt_x 0.25/1.5 = 0.17 |
| LEV_C__H_SINK | gate 2.19/0.66, contact 1.78/0.56 | gate 0.75/0.29, contact 0.63/0.25 | gate 0.59/0.18, contact 0.47/0.14 | gate 0.47/0.15, contact 0.38/0.12 | odometry_x 5.0/15.0 = 0.33, fixture:upper 3/15.0 = 0.2, dock_yaw 0.3/1.5 = 0.2 |
| LEV_C__H_SPAT | gate 2.19/0.66, contact 1.78/0.56 | gate 0.75/0.29, contact 0.63/0.25 | gate 0.59/0.18, contact 0.47/0.14 | gate 0.47/0.15, contact 0.38/0.12 | odometry_x 5.0/15.0 = 0.33, fixture:upper 3/15.0 = 0.2, dock_yaw 0.3/1.5 = 0.2 |
| LEV_C__H_WOK | gate 2.19/0.66, contact 1.78/0.56 | gate 0.75/0.29, contact 0.63/0.25 | gate 0.59/0.18, contact 0.47/0.14 | gate 0.47/0.15, contact 0.38/0.12 | odometry_x 5.0/15.0 = 0.33, fixture:upper 3/15.0 = 0.2, dock_yaw 0.3/1.5 = 0.2 |
| LEV_O__H_SINK | gate 7.21/2.24, contact 1.82/0.57 | gate 2.59/1.01, contact 0.64/0.26 | gate 2.11/0.68, contact 0.48/0.15 | gate 1.64/0.52, contact 0.39/0.12 | odometry_x 5.0/15.0 = 0.33, fixture:upper 3/14.043 = 0.21, dock_yaw 0.3/1.5 = 0.2 |
| LEV_O__H_SPAT | gate 5.6/1.79, contact 1.81/0.57 | gate 2.08/0.79, contact 0.64/0.26 | gate 1.64/0.55, contact 0.48/0.15 | gate 1.26/0.4, contact 0.38/0.12 | odometry_x 5.0/15.0 = 0.33, fixture:upper 3/14.262 = 0.21, dock_yaw 0.3/1.5 = 0.2 |
| LEV_O__H_WOK | gate 7.26/2.26, contact 1.82/0.57 | gate 2.6/1.01, contact 0.64/0.26 | gate 2.12/0.69, contact 0.48/0.15 | gate 1.65/0.52, contact 0.39/0.12 | odometry_x 5.0/15.0 = 0.33, fixture:upper 3/14.043 = 0.21, dock_yaw 0.3/1.5 = 0.2 |
| LEV_O__WOK | gate 7.26/2.26, contact 2.27/0.85 | gate 2.6/1.01, contact 0.7/0.28 | gate 2.12/0.69, contact 0.54/0.19 | gate 1.65/0.52, contact 0.48/0.18 | fixture:plate1 10/15.0 = 0.67, odometry_x 5.0/15.0 = 0.33, dock_yaw 0.3/1.5 = 0.2 |
| LID_POT__H_POT | gate 1.94/0.63, contact 1.9/0.62 | gate 0.63/0.25, contact 0.63/0.25 | gate 0.48/0.15, contact 0.47/0.14 | gate 0.39/0.13, contact 0.37/0.12 | odometry_x 5.0/15.0 = 0.33, fixture:cooker 5/15.0 = 0.33, dock_yaw 0.3/1.5 = 0.2 |
| LID_POT__H_WOK | gate 1.94/0.63, contact 1.9/0.62 | gate 0.63/0.25, contact 0.63/0.25 | gate 0.48/0.15, contact 0.47/0.14 | gate 0.39/0.13, contact 0.37/0.12 | odometry_x 5.0/15.0 = 0.33, fixture:cooker 5/15.0 = 0.33, dock_yaw 0.3/1.5 = 0.2 |
| LID_RACK__H_POT | gate 1.77/0.56, contact 1.77/0.56 | gate 0.63/0.25, contact 0.63/0.25 | gate 0.47/0.14, contact 0.47/0.14 | gate 0.37/0.12, contact 0.37/0.12 | odometry_x 5.0/15.0 = 0.33, fixture:spider_rest 3/15.0 = 0.2, dock_yaw 0.3/1.5 = 0.2 |
| LID_RACK__H_WOK | gate 1.77/0.56, contact 1.77/0.56 | gate 0.63/0.25, contact 0.63/0.25 | gate 0.47/0.14, contact 0.47/0.14 | gate 0.37/0.12, contact 0.37/0.12 | odometry_x 5.0/15.0 = 0.33, fixture:spider_rest 3/15.0 = 0.2, dock_yaw 0.3/1.5 = 0.2 |
| SPAT__H_SINK | gate 1.57/0.52, contact 1.57/0.52 | gate 0.56/0.24, contact 0.56/0.24 | gate 0.4/0.13, contact 0.4/0.13 | gate 0.34/0.11, contact 0.34/0.11 | odometry_x 5.0/15.0 = 0.33, dock_yaw 0.3/1.5 = 0.2, load_tilt_x 0.25/1.5 = 0.17 |
| SPAT__H_SPAT | gate 1.57/0.52, contact 1.57/0.52 | gate 0.56/0.24, contact 0.56/0.24 | gate 0.4/0.13, contact 0.4/0.13 | gate 0.34/0.11, contact 0.34/0.11 | odometry_x 5.0/15.0 = 0.33, dock_yaw 0.3/1.5 = 0.2, load_tilt_x 0.25/1.5 = 0.17 |
| SPAT__LEV_C | gate 2.19/0.66, contact 1.78/0.56 | gate 0.75/0.29, contact 0.63/0.25 | gate 0.59/0.18, contact 0.47/0.14 | gate 0.47/0.15, contact 0.38/0.12 | odometry_x 5.0/15.0 = 0.33, fixture:upper 3/15.0 = 0.2, dock_yaw 0.3/1.5 = 0.2 |
| SPIDER__H_POT | gate 2.07/0.66, contact 1.85/0.58 | gate 0.63/0.25, contact 0.63/0.25 | gate 0.58/0.2, contact 0.5/0.16 | gate 0.47/0.17, contact 0.4/0.13 | odometry_x 5.0/15.0 = 0.33, load_tilt_x 0.25/1.134 = 0.22, fixture:spider_rest 3/15.0 = 0.2 |
| SPIDER__H_WOK | gate 2.07/0.66, contact 1.85/0.58 | gate 0.63/0.25, contact 0.63/0.25 | gate 0.58/0.2, contact 0.5/0.16 | gate 0.47/0.17, contact 0.4/0.13 | odometry_x 5.0/15.0 = 0.33, load_tilt_x 0.25/1.134 = 0.22, fixture:spider_rest 3/15.0 = 0.2 |
| WOK__H_POT | gate 2.24/0.85, contact 2.24/0.85 | gate 0.69/0.28, contact 0.69/0.28 | gate 0.53/0.18, contact 0.53/0.18 | gate 0.47/0.18, contact 0.47/0.18 | fixture:plate1 10/15.0 = 0.67, odometry_x 5.0/15.0 = 0.33, dock_yaw 0.3/1.5 = 0.2 |
| WOK__H_SINK | gate 2.24/0.85, contact 2.24/0.85 | gate 0.69/0.28, contact 0.69/0.28 | gate 0.53/0.18, contact 0.53/0.18 | gate 0.47/0.18, contact 0.47/0.18 | fixture:plate1 10/15.0 = 0.67, odometry_x 5.0/15.0 = 0.33, dock_yaw 0.3/1.5 = 0.2 |
| WOK__H_WOK | gate 2.24/0.85, contact 2.24/0.85 | gate 0.69/0.28, contact 0.69/0.28 | gate 0.53/0.18, contact 0.53/0.18 | gate 0.47/0.18, contact 0.47/0.18 | fixture:plate1 10/15.0 = 0.67, odometry_x 5.0/15.0 = 0.33, dock_yaw 0.3/1.5 = 0.2 |

### Cart-only budget boxes, worst sign corner replayed (measured): min gate reserve / min gap (mm)

| Action / edge | as_designed | R09_requirement | dock_stops | touch_off |
|---|---|---|---|---|
| wok | -1.066 / 3.934 | 3.0 / 8.0 | 2.355 / 7.355 | 2.599 / 7.599 |
| spatula | -4.439 / 0.561 | 1.312 / 6.312 | 2.871 / 7.871 | 3.026 / 8.026 |
| lever | -2.061 / 2.939 | 5.196 / >=10 | 5.031 / >=10 | 5.545 / >=10 |
| lid | 3.621 / 8.621 (play not run) | >=10 / >=10 (play not run) | >=10 / >=10 (play not run) | >=10 / >=10 (play not run) |
| spider | -4.008 / 5.992 (play not run) | 2.15 / 7.15 | 2.033 / >=10 (play not run) | 2.453 / >=10 (play not run) |
| H_SINK__H_WOK | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| H_SPAT__H_SINK | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| H_WOK__H_POT | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| LEV_C__H_SINK | 1.768 / >=10 | 5.277 / >=10 | 6.463 / >=10 | 6.904 / >=10 |
| LEV_C__H_SPAT | 1.768 / >=10 | 5.281 / >=10 | 6.465 / >=10 | 6.903 / >=10 |
| LEV_C__H_WOK | 1.768 / >=10 | 5.281 / >=10 | 6.465 / >=10 | 6.903 / >=10 |
| LEV_O__H_SINK | -3.976 / 6.024 | -0.967 / 9.033 | 0.121 / >=10 | 0.528 / >=10 |
| LEV_O__H_SPAT | -3.324 / 6.676 | -0.575 / 9.425 | 0.611 / >=10 | 0.989 / >=10 |
| LEV_O__H_WOK | -3.974 / 6.026 | -0.97 / 9.03 | 0.117 / >=10 | 0.529 / >=10 |
| LEV_O__WOK | -3.977 / 6.023 | -0.968 / 9.032 | 0.121 / >=10 | 0.528 / >=10 |
| LID_POT__H_POT | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| LID_POT__H_WOK | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| LID_RACK__H_POT | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| LID_RACK__H_WOK | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| SPAT__H_SINK | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| SPAT__H_SPAT | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| SPAT__LEV_C | 1.768 / >=10 | 5.281 / >=10 | 6.465 / >=10 | 6.903 / >=10 |
| SPIDER__H_POT | 7.852 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| SPIDER__H_WOK | 8.217 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| WOK__H_POT | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| WOK__H_SINK | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
| WOK__H_WOK | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 | >=10 / >=10 |
