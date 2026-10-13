## 1. Inventory per meal (events, est.)

| Type | Category | Regime | A | B | C |
|---|---|---|---|---|---|
| g_rigid | grasp/release | structured | 117 | 131 | 101 |
| r_rigid | grasp/release | structured | 117 | 131 | 101 |
| g_food_rigid | grasp/release | unstructured | 3 | 3 | 4 |
| g_food_soft | grasp/release | unstructured | 3 | 10 | 1 |
| g_food_wet | grasp/release | unstructured | 9 | 1 | 7 |
| g_food_small | grasp/release | unstructured | 32 | 8 | 0 |
| r_food | grasp/release | unstructured | 47 | 22 | 12 |
| seat | insertion/seating | structured | 82 | 99 | 87 |
| contact_mech | contact | structured | 50 | 47 | 33 |
| stir_dice | contact | semi | 9 | 35 | 6 |
| stir_shred | contact | unstructured | 2 | 0 | 10 |
| food_contact | contact | unstructured | 28 | 22 | 1 |
| pour_liquid | pour/tip | structured | 10 | 19 | 16 |
| pour_food | pour/tip | unstructured | 37 | 54 | 45 |
| tool_change | tool change | structured | 5 | 5 | 5 |
| appl_cmd | appliance | structured | 41 | 51 | 61 |
| appl_proc | appliance | unstructured | 38 | 38 | 21 |
| perc_struct | perception | structured | 50 | 71 | 58 |
| perc_food | perception | unstructured | 74 | 62 | 46 |
| transit | free move | structured | 112 | 106 | 74 |
| hw | hardware | structured | 1 | 1 | 1 |

| Meal | events | grasp+release | prep share | hot-phase | structured / semi / unstructured | no-method ops |
|---|---|---|---|---|---|---|
| A | 868 | 328 | 60% | 84 | 585 / 9 / 274 | 4 |
| B | 916 | 306 | 46% | 147 | 661 / 35 / 220 | 8 |
| C | 690 | 226 | 48% | 102 | 537 / 6 / 147 | 4 |

by category: {'A': {'grasp/release': 328, 'insertion/seating': 82, 'contact': 89, 'pour/tip': 47, 'tool change': 5, 'appliance': 80, 'perception': 124, 'free move': 112, 'hardware': 1}, 'B': {'grasp/release': 306, 'insertion/seating': 99, 'contact': 104, 'pour/tip': 73, 'tool change': 5, 'appliance': 88, 'perception': 133, 'free move': 106, 'hardware': 1}, 'C': {'grasp/release': 226, 'insertion/seating': 87, 'contact': 50, 'pour/tip': 61, 'tool change': 5, 'appliance': 82, 'perception': 104, 'free move': 74, 'hardware': 1}}

## 2. Monte Carlo (N=20000 per cell). K = interventions + silent defects; clean meal = K 0

| Meal | Rates | Policy | P(clean) | P(K<=1) | E[interventions] | E[silent] | P(hot dish at risk) | T p50 / p90 min |
|---|---|---|---|---|---|---|---|---|
| A | lo | none | 0.581 | 0.898 | 0.54 | 0.00 | 0.015 | 54.3 / 60.3 |
| A | lo | user | 0.584 | 0.900 | 0.41 | 0.12 | 0.011 | 54.0 / 59.5 |
| A | lo | retry | 0.760 | 0.970 | 0.15 | 0.12 | 0.004 | 53.3 / 58.3 |
| A | mid | none | 0.084 | 0.291 | 2.50 | 0.00 | 0.078 | 60.2 / 70.4 |
| A | mid | user | 0.088 | 0.290 | 1.91 | 0.60 | 0.052 | 58.3 / 67.5 |
| A | mid | retry | 0.268 | 0.619 | 0.72 | 0.60 | 0.022 | 55.3 / 61.9 |
| A | hi | none | 0.000 | 0.000 | 12.94 | 0.00 | 0.380 | 93.7 / 115.2 |
| A | hi | user | 0.000 | 0.000 | 9.86 | 3.15 | 0.299 | 83.8 / 102.3 |
| A | hi | retry | 0.002 | 0.013 | 3.62 | 3.15 | 0.099 | 65.9 / 78.3 |
| B | lo | none | 0.670 | 0.940 | 0.40 | 0.00 | 0.028 | 87.2 / 92.7 |
| B | lo | user | 0.679 | 0.941 | 0.29 | 0.10 | 0.021 | 87.0 / 92.1 |
| B | lo | retry | 0.811 | 0.981 | 0.11 | 0.10 | 0.008 | 86.5 / 91.1 |
| B | mid | none | 0.151 | 0.432 | 1.92 | 0.00 | 0.130 | 91.7 / 100.9 |
| B | mid | user | 0.155 | 0.434 | 1.40 | 0.51 | 0.098 | 90.1 / 98.2 |
| B | mid | retry | 0.345 | 0.709 | 0.57 | 0.50 | 0.035 | 88.0 / 94.0 |
| B | hi | none | 0.000 | 0.001 | 10.07 | 0.00 | 0.584 | 118.0 / 136.6 |
| B | hi | user | 0.000 | 0.001 | 7.42 | 2.68 | 0.469 | 109.3 / 125.6 |
| B | hi | retry | 0.004 | 0.028 | 2.90 | 2.67 | 0.179 | 96.6 / 107.4 |
| C | lo | none | 0.783 | 0.974 | 0.24 | 0.00 | 0.024 | 47.1 / 51.7 |
| C | lo | user | 0.786 | 0.975 | 0.17 | 0.07 | 0.016 | 46.9 / 51.4 |
| C | lo | retry | 0.874 | 0.992 | 0.07 | 0.07 | 0.005 | 46.7 / 50.9 |
| C | mid | none | 0.313 | 0.674 | 1.17 | 0.00 | 0.114 | 49.6 / 57.0 |
| C | mid | user | 0.306 | 0.666 | 0.86 | 0.33 | 0.080 | 48.7 / 55.2 |
| C | mid | retry | 0.511 | 0.855 | 0.34 | 0.33 | 0.031 | 47.5 / 52.5 |
| C | hi | none | 0.002 | 0.014 | 6.45 | 0.00 | 0.495 | 66.3 / 81.4 |
| C | hi | user | 0.002 | 0.013 | 4.67 | 1.77 | 0.380 | 60.7 / 73.5 |
| C | hi | retry | 0.030 | 0.137 | 1.75 | 1.77 | 0.148 | 52.3 / 61.2 |

schedule + prep block only (no failures): {'A': {'base_cook_min': 38.2, 'p50': 50.8, 'p90': 55.4}, 'B': {'base_cook_min': 75.6, 'p50': 84.3, 'p90': 88.4}, 'C': {'base_cook_min': 35.6, 'p50': 44.7, 'p90': 48.6}}

## 3. Exposure at mid rates, retry policy: top contributors to E[K]

A: E[K] 1.33 (int 0.73 + silent 0.60); types: appl_proc 22%, perc_food 22%, g_food_small 17%, food_contact 10%, pour_food 8%, r_food 7%; families: PLACE 31%, PRESS 26%, PIECE_SHORT 9%, PIECE 5%, BASKET 4%, SEAS_DOSE 3%
B: E[K] 1.08 (int 0.57 + silent 0.50); types: appl_proc 26%, perc_food 22%, pour_food 14%, food_contact 10%, g_food_small 5%, g_food_soft 5%; families: PRESS 22%, PIECE 15%, SEAS_DOSE 8%, MAIN_BOWL 7%, SEAS_PICK 7%, EGG 7%
C: E[K] 0.68 (int 0.35 + silent 0.33); types: perc_food 26%, appl_proc 23%, pour_food 18%, g_food_wet 7%, stir_shred 6%, seat 4%; families: SEAS_DOSE 13%, PIECE_SHORT 11%, MINCE 8%, MAIN_BOWL 7%, MEAT 7%, PIECE 7%

## 4. Targets. Scale s on all mid first-attempt failure rates (relative difficulty kept), and the equal allocation

| Meal | Target | lambda | equal alloc: residual per-event success | s (no recovery) | s (retry) | g_rigid | seat | g_food_rigid | g_food_soft/wet | pour_food | appl_proc | perc_food |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | P(K=0)>=0.90 | 0.105 | 99.988 % | 0.042 | 0.079 | 99.996 | 99.992 | 99.960 | 99.881 / 99.841 | 99.960 | 99.921 | 99.960 |
| A | P(K=0)>=0.95 | 0.051 | 99.994 % | 0.020 | 0.039 | 99.998 | 99.996 | 99.981 | 99.942 / 99.923 | 99.981 | 99.961 | 99.981 |
| A | P(K=0)>=0.99 | 0.010 | 99.999 % | 0.004 | 0.008 | 100.000 | 99.999 | 99.996 | 99.989 / 99.985 | 99.996 | 99.992 | 99.996 |
| A | P(K<=1)>=0.90 | 0.532 | 99.939 % | 0.212 | 0.401 | 99.980 | 99.960 | 99.800 | 99.399 / 99.199 | 99.800 | 99.599 | 99.800 |
| A | P(K<=1)>=0.95 | 0.355 | 99.959 % | 0.141 | 0.268 | 99.987 | 99.973 | 99.866 | 99.598 / 99.465 | 99.866 | 99.732 | 99.866 |
| A | P(K<=1)>=0.99 | 0.149 | 99.983 % | 0.059 | 0.112 | 99.994 | 99.989 | 99.944 | 99.832 / 99.776 | 99.944 | 99.888 | 99.944 |
| A | E[K]<=1/week (7 meals) | 0.143 | 99.984 % | 0.057 | 0.108 | 99.995 | 99.989 | 99.946 | 99.839 / 99.785 | 99.946 | 99.892 | 99.946 |
| B | P(K=0)>=0.90 | 0.105 | 99.988 % | 0.055 | 0.098 | 99.995 | 99.990 | 99.951 | 99.853 / 99.804 | 99.951 | 99.902 | 99.951 |
| B | P(K=0)>=0.95 | 0.051 | 99.994 % | 0.027 | 0.048 | 99.998 | 99.995 | 99.976 | 99.929 / 99.905 | 99.976 | 99.952 | 99.976 |
| B | P(K=0)>=0.99 | 0.010 | 99.999 % | 0.005 | 0.009 | 100.000 | 99.999 | 99.995 | 99.986 / 99.981 | 99.995 | 99.991 | 99.995 |
| B | P(K<=1)>=0.90 | 0.532 | 99.942 % | 0.278 | 0.494 | 99.975 | 99.951 | 99.753 | 99.259 / 99.012 | 99.753 | 99.506 | 99.753 |
| B | P(K<=1)>=0.95 | 0.355 | 99.961 % | 0.186 | 0.330 | 99.983 | 99.967 | 99.835 | 99.505 / 99.340 | 99.835 | 99.670 | 99.835 |
| B | P(K<=1)>=0.99 | 0.149 | 99.984 % | 0.078 | 0.138 | 99.993 | 99.986 | 99.931 | 99.793 / 99.724 | 99.931 | 99.862 | 99.931 |
| B | E[K]<=1/week (7 meals) | 0.143 | 99.984 % | 0.075 | 0.133 | 99.993 | 99.987 | 99.934 | 99.801 / 99.735 | 99.934 | 99.867 | 99.934 |
| C | P(K=0)>=0.90 | 0.105 | 99.985 % | 0.089 | 0.155 | 99.992 | 99.985 | 99.923 | 99.768 / 99.691 | 99.923 | 99.845 | 99.923 |
| C | P(K=0)>=0.95 | 0.051 | 99.993 % | 0.044 | 0.075 | 99.996 | 99.992 | 99.962 | 99.887 / 99.849 | 99.962 | 99.925 | 99.962 |
| C | P(K=0)>=0.99 | 0.010 | 99.999 % | 0.009 | 0.015 | 99.999 | 99.999 | 99.993 | 99.978 / 99.971 | 99.993 | 99.985 | 99.993 |
| C | P(K<=1)>=0.90 | 0.532 | 99.923 % | 0.451 | 0.780 | 99.961 | 99.922 | 99.610 | 98.830 / 98.440 | 99.610 | 99.220 | 99.610 |
| C | P(K<=1)>=0.95 | 0.355 | 99.948 % | 0.301 | 0.521 | 99.974 | 99.948 | 99.739 | 99.218 / 98.957 | 99.739 | 99.479 | 99.739 |
| C | P(K<=1)>=0.99 | 0.149 | 99.978 % | 0.126 | 0.218 | 99.989 | 99.978 | 99.891 | 99.673 / 99.564 | 99.891 | 99.782 | 99.891 |
| C | E[K]<=1/week (7 meals) | 0.143 | 99.979 % | 0.121 | 0.210 | 99.990 | 99.979 | 99.895 | 99.686 / 99.581 | 99.895 | 99.790 | 99.895 |

Per-type first-attempt success needed (retry policy as designed; worst of A/B/C; all mid rates scaled by one factor s):

| Type | regime | mid assumption | P(K=0)>=0.90 | P(K=0)>=0.95 | P(K=0)>=0.99 | P(K<=1)>=0.90 | P(K<=1)>=0.95 | P(K<=1)>=0.99 | E[K]<=1/week (7 meals) |
|---|---|---|---|---|---|---|---|---|---|
| g_rigid | structured | 99.950 | 99.996 | 99.998 | 100.000 | 99.980 | 99.987 | 99.994 | 99.995 |
| r_rigid | structured | 99.990 | 99.999 | 100.000 | 100.000 | 99.996 | 99.997 | 99.999 | 99.999 |
| g_food_rigid | unstructured | 99.500 | 99.960 | 99.981 | 99.996 | 99.800 | 99.866 | 99.944 | 99.946 |
| g_food_soft | unstructured | 98.500 | 99.881 | 99.942 | 99.989 | 99.399 | 99.598 | 99.832 | 99.839 |
| g_food_wet | unstructured | 98.000 | 99.841 | 99.923 | 99.985 | 99.199 | 99.465 | 99.776 | 99.785 |
| g_food_small | unstructured | 98.000 | 99.841 | 99.923 | 99.985 | 99.199 | 99.465 | 99.776 | 99.785 |
| r_food | unstructured | 99.700 | 99.976 | 99.988 | 99.998 | 99.880 | 99.920 | 99.966 | 99.968 |
| seat | structured | 99.900 | 99.992 | 99.996 | 99.999 | 99.960 | 99.973 | 99.989 | 99.989 |
| contact_mech | structured | 99.900 | 99.992 | 99.996 | 99.999 | 99.960 | 99.973 | 99.989 | 99.989 |
| stir_dice | semi | 99.900 | 99.992 | 99.996 | 99.999 | 99.960 | 99.973 | 99.989 | 99.989 |
| stir_shred | unstructured | 99.500 | 99.960 | 99.981 | 99.996 | 99.800 | 99.866 | 99.944 | 99.946 |
| food_contact | unstructured | 99.000 | 99.921 | 99.961 | 99.992 | 99.599 | 99.732 | 99.888 | 99.892 |
| pour_liquid | structured | 99.950 | 99.996 | 99.998 | 100.000 | 99.980 | 99.987 | 99.994 | 99.995 |
| pour_food | unstructured | 99.500 | 99.960 | 99.981 | 99.996 | 99.800 | 99.866 | 99.944 | 99.946 |
| tool_change | structured | 99.900 | 99.992 | 99.996 | 99.999 | 99.960 | 99.973 | 99.989 | 99.989 |
| appl_cmd | structured | 99.990 | 99.999 | 100.000 | 100.000 | 99.996 | 99.997 | 99.999 | 99.999 |
| appl_proc | unstructured | 99.000 | 99.921 | 99.961 | 99.992 | 99.599 | 99.732 | 99.888 | 99.892 |
| perc_struct | structured | 99.950 | 99.996 | 99.998 | 100.000 | 99.980 | 99.987 | 99.994 | 99.995 |
| perc_food | unstructured | 99.500 | 99.960 | 99.981 | 99.996 | 99.800 | 99.866 | 99.944 | 99.946 |
| transit | structured | 99.990 | 99.999 | 100.000 | 100.000 | 99.996 | 99.997 | 99.999 | 99.999 |
| hw | structured | 99.900 | 99.992 | 99.996 | 99.999 | 99.960 | 99.973 | 99.989 | 99.989 |
| (scale s) | | 1 | 0.079 | 0.039 | 0.008 | 0.401 | 0.268 | 0.112 | 0.108 |

Allocation 2 (structured types kept at mid, only semi/unstructured scaled). Structured floor E[K]: A 0.094, B 0.110, C 0.088
  P(K=0)>=0.90: A s_u=0.009, B infeasible, C s_u=0.029
  P(K=0)>=0.95: A infeasible, B infeasible, C infeasible
  P(K=0)>=0.99: A infeasible, B infeasible, C infeasible
  P(K<=1)>=0.90: A s_u=0.355, B s_u=0.437, C s_u=0.748
  P(K<=1)>=0.95: A s_u=0.212, B s_u=0.254, C s_u=0.450
  P(K<=1)>=0.99: A s_u=0.044, B s_u=0.040, C s_u=0.102
  E[K]<=1/week (7 meals): A s_u=0.039, B s_u=0.034, C s_u=0.092

without recovery the same targets need s = {'P(K=0)>=0.90': 0.042, 'P(K=0)>=0.95': 0.02, 'P(K=0)>=0.99': 0.004, 'P(K<=1)>=0.90': 0.212, 'P(K<=1)>=0.95': 0.141, 'P(K<=1)>=0.99': 0.059, 'E[K]<=1/week (7 meals)': 0.057}
sensitivity baseline: E[K] A 1.33, B 1.08, C 0.68; E[interventions] A 0.73, B 0.57, C 0.35
sensitivity independent retries (q_floor 0): E[K] A 1.08, B 0.90, C 0.59; E[interventions] A 0.48, B 0.40, C 0.25
sensitivity strongly correlated retries (q_floor 0.5): E[K] A 1.78, B 1.40, C 0.88; E[interventions] A 1.18, B 0.90, C 0.54
sensitivity detection -0.2 on every type: E[K] A 1.63, B 1.30, C 0.82; E[interventions] A 0.53, B 0.41, C 0.25
sensitivity detection 0.95 on every type: E[K] A 1.07, B 0.86, C 0.54; E[interventions] A 0.95, B 0.76, C 0.48

## 5. Levers: E[K] per meal (interventions + silent defects), retry policy. P(clean) ~ exp(-E[K])

| Lever | mid: A | B | C | mean | change | P(clean) | hi: mean | change |
|---|---|---|---|---|---|---|---|---|
| baseline (retry k=1) | 1.33 | 1.08 | 0.68 | 1.03 | +0.00 | 0.37 | 5.29 | +0.00 |
| recovery off: every failure goes to the user (p^n) | 2.51 | 1.91 | 1.18 | 1.87 | +0.84 | 0.18 | 9.82 | +4.54 |
| retry twice (k=2) | 1.10 | 0.93 | 0.60 | 0.88 | -0.15 | 0.43 | 4.51 | -0.77 |
| grasp / pour / placement sensing (d -> 0.98, food release 0.9) | 1.24 | 1.01 | 0.64 | 0.96 | -0.07 | 0.39 | 4.99 | -0.30 |
| process verification: scale + camera after each prep output (appl_proc, perc_food d -> 0.9) | 1.20 | 0.96 | 0.60 | 0.92 | -0.11 | 0.41 | 4.66 | -0.62 |
| food on keyed slot trays (food grasp p x0.3, locate x0.5) | 0.97 | 0.87 | 0.55 | 0.80 | -0.23 | 0.46 | 3.99 | -1.29 |
| better food-state perception (perc_food p x0.3) | 1.13 | 0.91 | 0.56 | 0.86 | -0.16 | 0.43 | 4.30 | -0.99 |
| keyed lead-ins + force-monitored contact (rigid/seat/contact p x0.3) | 1.28 | 1.03 | 0.64 | 0.98 | -0.04 | 0.39 | 5.07 | -0.22 |
| bench-proven prep appliances (process outcome p x0.3) | 1.12 | 0.88 | 0.57 | 0.86 | -0.17 | 0.44 | 4.43 | -0.85 |
| pour-portion the stew cups (A: 32 placements -> 8 pours) | 1.02 | 1.08 | 0.68 | 0.93 | -0.10 | 0.40 | 4.77 | -0.52 |
| powered section/belt cutter instead of 45 lever presses | 1.00 | 0.90 | 0.68 | 0.86 | -0.17 | 0.43 | 4.45 | -0.83 |
| one finger set for most items (5 -> 1 swap per meal) | 1.32 | 1.07 | 0.68 | 1.03 | -0.00 | 0.37 | 5.27 | -0.01 |
| no drum rim holder found: plan P1 (cups for the stir bursts too) | 1.33 | 1.09 | 0.69 | 1.03 | +0.01 | 0.37 | 5.31 | +0.02 |
| stirring appliance at the wok (not adopted; market survey) | 1.33 | 1.08 | 0.66 | 1.02 | -0.01 | 0.37 | 5.28 | -0.00 |
| one prep faucet session instead of 2 | 1.33 | 1.07 | 0.68 | 1.03 | -0.00 | 0.37 | 5.28 | -0.01 |
| consumer smart plugs without read-back (appl_cmd p = 1e-2) | 1.39 | 1.15 | 0.77 | 1.10 | +0.07 | 0.34 | 5.29 | +0.00 |
| **package of the design levers** | 0.21 | 0.29 | 0.23 | 0.24 | -0.78 | 0.78 | 1.20 | -4.08 |

package MC: {'A|mid': {'p_clean': 0.81, 'p_le1': 0.981, 'E_int': 0.169, 'E_sil': 0.041, 'p_dish_at_risk': 0.014, 'T_p50': 53.39, 'T_p90': 58.423, 'T_mean': 53.44}, 'A|hi': {'p_clean': 0.349, 'p_le1': 0.72, 'E_int': 0.812, 'E_sil': 0.232, 'p_dish_at_risk': 0.068, 'T_p50': 55.708, 'T_p90': 62.475, 'T_mean': 56.06}, 'B|mid': {'p_clean': 0.746, 'p_le1': 0.966, 'E_int': 0.225, 'E_sil': 0.066, 'p_dish_at_risk': 0.024, 'T_p50': 86.938, 'T_p90': 91.899, 'T_mean': 87.134}, 'B|hi': {'p_clean': 0.244, 'p_le1': 0.583, 'E_int': 1.06, 'E_sil': 0.357, 'p_dish_at_risk': 0.115, 'T_p50': 89.919, 'T_p90': 97.231, 'T_mean': 90.494}, 'C|mid': {'p_clean': 0.792, 'p_le1': 0.978, 'E_int': 0.174, 'E_sil': 0.059, 'p_dish_at_risk': 0.025, 'T_p50': 46.964, 'T_p90': 51.491, 'T_mean': 47.107}, 'C|hi': {'p_clean': 0.325, 'p_le1': 0.685, 'E_int': 0.836, 'E_sil': 0.302, 'p_dish_at_risk': 0.113, 'T_p50': 49.268, 'T_p90': 55.821, 'T_mean': 49.746}}

structural (no designed method, a certain user step each until designed): {'A': (4, 2), 'B': (8, 4), 'C': (4, 1)}

## 6. Failure-free trials needed at 95 % confidence: n = ln(0.05)/ln(1-p)
  per-event failure <= 0.1: 29 clean events
  per-event failure <= 0.05: 59 clean events
  per-event failure <= 0.01: 299 clean events
  per-event failure <= 0.001: 2,995 clean events
  per-event failure <= 0.0001: 29,956 clean events
  clean-meal rate >= 0.9: 29 clean meals in a row
  clean-meal rate >= 0.95: 59 clean meals in a row
  clean-meal rate >= 0.99: 299 clean meals in a row
