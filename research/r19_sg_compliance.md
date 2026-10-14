# R19: Singapore compliance: SAFETY Mark, LEW work, HDB/condo rules, insurance (GitHub #24)

Date: 2026-10-14. Desk study: repo files plus read-only web reading (WebSearch, WebFetch, and Chrome for pages that only render with scripts). Nothing was bought. No logins, no forms, nobody was contacted. No other file was changed.

**Labels**
- **[S]**: sourced, either a repo `file:line` or a URL listed in §10. Quotes are short and verbatim.
- **[E]**: my estimate, inference or proposal. Not sourced.

Paths are relative to `robot_rail/`.

**This is not legal advice.** It is an engineering reading of public rules. Before money is spent, an LEW, HDB or the MCST, the CPSO and the insurer must confirm the points marked "confirm".

---

## 0. Answer first

1. **The HDB 15 A rule is real, and it blocks the planned 3.5 kW wok cooker in an HDB flat.** The current HDB electrical-works page (updated 24 Jul 2026) says "Appliances with electrical rating exceeding 15amps power is not allowed". It also says the "20amps isolator is only allowed for air-conditioner installation" [S H1]. The cooker draws 15.2 A [S `sim/r10/claude/README_R10.md:503`]. In an HDB flat the wok therefore has to be a unit of ≤ 15 A (≤ about 3.3 kW at 230 V [E]) on a 15 A or 13 A point, or the user must get HDB approval for an unlisted item [S H1]. In a condo no such rule was found, and the 20 A hard-wired point stays possible (LEW + MCST). **The first fact needed is the housing type.** The repo does not record it.
2. **SAFETY Mark (CPSR): the duty is on suppliers, not on a person who imports for their own use.** The offence is supplying Controlled Goods "in the course of any trade or business" without registration [S C1 p.7]. Importers must register only goods "meant for sale in Singapore" [S C1 p.35]. I found no CPSO text that speaks about personal imports directly. IMDA's analogous rule for radio devices says so explicitly: personal-use imports need no registration [S I1 Q40]. So importing the China units for own use is very probably not a CPSR offence [E, confirm with CPSO]. It is not risk-free, though:
   - **Insurance:** one current home policy (Etiqa ePROTECT home) makes it "a condition precedent" to *all* claims that all electrical equipment is CPSR-compliant and carries the SAFETY Mark [S N1 cond. 21]. With that wording, one unmarked imported cooker could void a fire claim.
   - **Plugs:** GB and Schuko plugs do not fit SG sockets. Universal sockets and adaptors cannot be registered in SG [S C3].
   - **Practical path:** buy SG-registered units where an equivalent exists (rice cooker, kettle, flat induction, fryer, smart plugs, slicer). Import only items with no SG equivalent (the concave cooker), have an LEW connect it, and disclose it to the insurer in writing.
3. **On the BOM, these are Controlled Goods** (33 categories; all of the following are "Medium risk") [S C2]:
   - concave and flat induction cookers ("hot plate (including induction type)");
   - the fryer;
   - the rice cooker;
   - the water-bath stew pot ("slow cooker … stewing pot");
   - the kettle;
   - the slicer and powered peelers ("Kitchen machines", e.g. "Food Slicer");
   - the IPC and monitor ("Home computer system");
   - plug-in PSUs ("AC adaptors");
   - 3-pin plugs, multi-way adaptors, and the cable reel ("Portable socket-outlet … including portable cable reels");
   - the RCCB (Low risk); wall sockets and switches (High risk).

   **Not Controlled Goods:**
   - the robot arm, the UR controller, the cart drives, contactors and safety relays;
   - the hood ("Cooker hood" is on the non-controlled list [S C1 p.54]);
   - battery or manual items.
4. **Electrical work.** Only a Licensed Electrical Worker (LEW) may do work on the fixed installation [S E1]. The Electricity Act's definition of "electrical installation" **excludes everything plugged in beyond an outlet where fixed wiring ends** [S E2 s.2(b)]. So:
   - the user may build and wire the cart, the 24/48 V SELV side and plug-in appliances;
   - the LEW does and certifies the new radials, RCBOs, outlets and the hard-wired wok feed, **and the 230 V contactor box from `r19_fire_heatcut.md` once it is fed from fixed wiring** [S `research/r19_fire_heatcut.md:214-215`].

   A 30 mA RCCB on every home has been compulsory since 1 Jul 2025, with a fine of up to S$5,000 [S E1].
5. **Renovation rules (HDB).**
   - The floor rail as designed (adhesive on tiles plus 12 screws into the plinth [S `sim/r10/claude/R19_DOCK.md:117-120`]) fits HDB's limits: fasteners ≤ 6 mm diameter and ≤ 40 mm deep; no wiring may be embedded in the RC slab, walls or plaster [S H1, H2]. Equipment ≤ 150 kg needs no permit [S H2]. The cart is 131.9 kg [S `sim/r10/claude/results/hardware.json`, `cart.total_model_mass_kg`].
   - New 13 A points need no HDB permit, but they need SP Services testing (Form CS/5H) through the LEW [S H1].
   - Faucet, solenoid or water-pipe work needs a PUB Licensed Plumber. Any gas work needs City Energy or an LGSW [S H3].

   **Condo:** the MCST's approval is usually needed before renovation [S M1], plus its by-laws [E].
6. **Robots.** I found no Singapore law or standard specific to home robots (§4). The WSH Act does not cover domestic workers [S W1]. If a foreign domestic worker (FDW) uses the robot, the employer's work-permit duty to provide "safe working conditions" applies. MOM prosecutes breaches, with fines up to S$10,000 or jail [S W2].
7. **Insurance.**
   - HDB fire insurance covers only what HDB provided, and "excludes any renovations or improvements" by the owner [S N3 §15.2].
   - Contents and liability policies typically exclude electrical or mechanical breakdown, and liability from alterations to buildings or from "any mechanically propelled vehicle" [S N2]. The cart's drives could be argued into that last exclusion [E].
   - The insured must disclose material facts and changes [S N1, N2].
   - **Tell the insurer in writing before the first powered run (§5).**

---

## 1. CPS / SAFETY Mark (CPSR, administered by CPSO)

### 1.1 What the rules bind [S C1 = CPSR Information Booklet, updated 24 Jun 2026]

| Point | Text / fact | Src |
|---|---|---|
| Scope | 33 categories of household electrical, electronic and gas appliances "need to be tested … registered with the CPSO, and affixed with the SAFETY Mark before they can be sold in Singapore" | C1 p.5 |
| Who it binds | "all Controlled Goods supplied in Singapore, in the course of any trade or business" must be registered and marked (Reg. 4(1)). Fine up to $10,000 and/or 2 years | C1 p.7 |
| Importers | "Importers who import Controlled Goods that are meant for sale in Singapore are required to apply for registration" | C1 p.35 |
| Retailers who modify | Retailers who modify registered goods in a way that "impact[s] the safety" must register again | C1 p.35 |
| Household vs B2B | The SAFETY Mark requirement "applies to Controlled Goods that are supplied for personal use by consumers"; goods solely for non-household (B2B) use "may not be subject" | C1 p.5 |
| Exemption | Only for Registered Suppliers, for display or demonstration goods | C1 p.48 |
| Supplier | A Registered Supplier is tied to an ACRA-registered business (UEN). The CPSO fee is $180 per model registration | C1 p.35, p.40 |
| Consumer FAQ | Outside CPSO's purview: "Used or second-hand general consumer goods", goods "imported solely for re-export". Nothing on personal imports | C4 |
| Consumer advice | Buy only goods with a valid SAFETY Mark. Check that products use "plugs and voltages suitable for local use, such as a 3-pin Singapore plug with a valid SAFETY Mark" | C4, C5 |
| Personal imports | **No CPSO statement found.** Searched the CPSO consumer FAQ, the online-shopping page, the CPSR overview, the booklet, and web searches for "personal use", "own use" and "overseas". By analogy, IMDA states that personal-use telecom imports "not for sale or hire" need no registration [S I1 Q40] | — |

**Reading [E].** Every operative duty is attached to *supply in the course of trade or business* or to *import for sale*. A private person who imports a China cooker and uses it at home supplies nobody, so CPSR as written does not seem to bind them. The CPSO never says so expressly, though, and it recommends against it. Confirm with the CPSO in writing (the user's action).

What does still bind a private user:
- the Electricity Act s.83(3): a "rash or negligent act" in respect of an installation that causes hurt or damage is an offence, with a fine up to $10,000 or 3 years [S E3];
- the insurer's policy conditions (§5);
- if the robot or its parts are ever sold or given away in the course of business, CPSR applies in full [E].

### 1.2 BOM items against the Controlled Goods list [S C2 tiers; S C1 definitions]

| BOM item (repo source) | Controlled Good category (tier) | SG-registered equivalent? | Plug / voltage now | Path [E] |
|---|---|---|---|---|
| Concave 3.5 kW induction, 美的 MC-E35D2 / 九阳 N3501 (`r19_system_cost.md:66`) | "Toaster, grill, roaster, hot plate (including induction type) …" (Medium) | **None found** [S `research/r15_cooking_market.md:420`]. SG has hybrid built-ins "for round bottom wok" (gas + induction) [S r15:63] | China 220 V, 16 A GB plug; 15.2 A at 230 V (`README_R10.md:503`). CPSR item #6: appliances rated above about 3 kW "shall be connected to fixed wiring" [S C1 p.21; the comparison symbol did not extract from the PDF] | Import for own use; LEW hard-wires it (condo), **or** choose a ≤ 3.3 kW unit for HDB (§2.4) |
| Zone 2 米家电磁炉 N1, 2100 W (`r19_system_cost.md:69`) | Same (Medium) | Likely: SG-plug induction plates are common [E] | China plug | Buy an SG-registered flat induction plate. MIoT writability must then be re-checked (the N1 is already unknown) |
| Fryer, Tefal FR8040 (`:73`) | "… deep fryer …" (Medium) | Not checked for this model. SG-registered fryers exist [E] | EU Schuko | Buy an SG-registered fryer, or drop the fryer (`r19_fire_heatcut.md` D4) |
| Water-bath stew pot (`:70`) | "Coffee maker, slow cooker …" (Medium). "Stewing Pot" is listed as an example [S C1 p.53] | Yes, common [E] | China plug | Buy SG-registered |
| Rice cooker 米家 C1 (`:71`) | "Rice cooker" (Medium) | Xiaomi and others sell SG-plug units [E, not verified per model] | China plug | Buy SG-registered |
| Kettle, Philips HD9350 class (`r19_power_budget.md:88`) | "Liquid heating appliances" (Medium) | Yes [E] | — | Buy SG-registered, or drop it (R17 says it is optional) |
| Slicer 卓晋 3-in-1, powered peelers (`r19_system_cost.md:82`; #33 comment) | "Kitchen machines" (Medium). "Food Slicer", "Food Processor" are listed as examples [S C1 p.53] | Unknown per model | China plug | Prefer a manual or battery tool, or an SG-registered machine. Otherwise import for own use + SG plug |
| Smart plugs (`:70`, `:235`) | Not clearly a listed category. A single-socket plug-in is neither a "Multi-way adaptor" (more than one socket set) nor a "3-pin mains plug" as defined [S C1 p.15, 17] | SG-plug smart plugs are sold locally [E] | GB | Buy BS 1363 SG versions, 13 A, power-on state OFF [S `r19_power_budget.md:231`] |
| Brennenstuhl Schuko reel (`sim/r10/claude/hardware.py:15`) | "Portable socket-outlet … including portable cable reels" (Medium) | n/a | Schuko sockets and plug | Already rejected (BLOCKING) by the tether study [S `research/r19_tether.md:28`]. Do not use |
| Industrial PC, monitor (`r19_system_cost.md:60`) | "Home computer system" (Medium) | Use an SG-plug PSU [E] | — | Buy locally, or give it an SG-registered PSU |
| 24 V / 48 V PSUs | Plug-in units = "AC Adaptor" (Medium) [S C1 p.10]. DIN-rail PSUs wired inside the cart: not a listed category [E] | — | — | Use DIN-rail PSUs inside the cart enclosure, fed through one SAFETY-Marked BS 1363 plug |
| UR5e / FR5 arm, controller, drives, gripper, contactors, safety relay | Not in the 33 categories | — | 100–240 VAC (UR) [S `research/r19_tether.md:48`] | Not CPSR. Electrical safety is the user's and the LEW's responsibility |
| Fridge, hood (user's own) | Fridge: "Refrigerators" (High). Hood: not controlled [S C1 p.54] | Already installed | — | — |

### 1.3 Plugs and adaptors
- Singapore uses **BS 1363 13 A** (SS 145-1) and **BS 546 15 A round-pin** (SS 472). Both are Controlled Goods and carry their *own* SAFETY Mark [S C1 p.17; C4 Q6].
- **Universal socket-outlets "cannot be registered with a valid Safety Mark"** [S C3]. The CPSO has issued an alert on a non-compliant travel adaptor (HK:088) [S C3 search result].
- EMA: do not piggy-back plugs with double adaptors [S E1].
- A 16 A GB plug has no BS 1363 counterpart [S issue #24 body]. The 3.5 kW cooker cannot go on any 13 A plug.

**Recommendation [E].** For every imported appliance that stays, cut off the foreign plug and fit a SAFETY-Marked BS 1363 plug with the right fuse (13 A for heaters ≤ 3 kW). This is plug-side work, outside the definition of an "electrical installation" [S E2 s.2(b)], so the user may do it. Never use a travel adaptor, a universal socket or a Schuko reel.

### 1.4 If someone wanted to register an imported model (the importer route)
- They must be a Registered Supplier (an ACRA business with a UEN).
- They need a CoC from a designated CAB, because medium-risk goods need third-party certification [S C2].
- Testing is at 230 VAC 50 Hz to IEC 60335-2-9 (hot plates) or 2-13 (fryers) and so on, plus CPSO's extra requirements [S C1 p.20-21].
- The fee is $180 per model, plus the CAB's test and certification fee: **not found**. My guess is SGD 2,000–10,000 per model [E].
- Not sensible for one cooker. Only relevant if the robot ever becomes a product.

### 1.5 Issue study step 2: does a bolt-on knob servo or a UART tap "void the registration"?
- CPSR registration is the *supplier's* obligation. A retailer who modifies goods "which impact the safety" must re-register [S C1 p.35]. A home owner who adds a servo for own use does not trigger CPSR [E].
- Practical effects [E]:
  - the maker's warranty is probably void;
  - an insurer with a "CPSR-compliant + SAFETY Mark" condition [S N1] could argue that a modified unit is no longer the registered product.
- **A bolt-on knob servo that does not open the case is the lower-risk option. A UART tap inside the case is the higher-risk one [E].**

---

## 2. Electrical installation (EMA, Electricity Act, SS 638)

### 2.1 Rules

| Rule | Text / fact | Src |
|---|---|---|
| Who | "EMA requires electrical works at consumers' premises to be carried out by Licensed Electrical Workers (LEWs)". Electrical works "includes any rewiring, modification/alteration, repair or replacement to the electrical installation". New wiring, rewiring and extensions are tested by SP Services before supply is turned on. Check an LEW's licence on ELISE | E1 |
| What an "electrical installation" is | Any appliance, wire or fitting used to convey or control electricity on premises, **but not** "any appliance, wire, fitting or apparatus connected to and beyond any electrical outlet … at which fixed wiring terminates" (s.2(b), in force 8 Dec 2023) | E2 |
| What "electrical work" is | Installing, altering or adding to an installation. Excludes manufacturing or assembling a new article, and oiling, cleaning or painting | E2 |
| Offences | s.83(2) wilful tampering that is likely to cause danger: up to 5 years. s.83(3) rash or negligent act causing hurt or damage: up to $10,000 or 3 years | E3 |
| RCCB | All homes must have an RCCB or ELCB of ≤ 30 mA. From 1 Jul 2025, a fine of up to $5,000 for homes without one | E1 |
| Code | SS 638 (BS 7671-derived). Fixed-wiring connections of appliances "shall be in accordance with SS 638" | C1 p.21; `r19_power_budget.md:207` |
| HDB | "All wiring installation work must be carried out by an EMA licensed electrical worker". Submit SPSL Form CS/5H (endorsed by HDB) for testing of new wiring. Apply to SPSL for inspection through the LEW | H1 |

### 2.2 What the user may do themselves [E, from E2's definitions]
- Everything on the plug side of an outlet:
  - building the cart, the 48 V SELV/PELV system and the 24 V safety-relay side;
  - changing appliance plugs;
  - smart plugs;
  - a plug-in seasoning-station PSU.
- Testing their own equipment (insulation and leakage with a meter). This is good practice, not a certificate.
- **Not:** adding or moving any outlet, spur, MCB, RCBO, isolator, hard-wired appliance connection or DB work. Also not the contactor box once it is fed from fixed wiring (§2.3).

### 2.3 The contactor / safety-relay "heat enable" box (`r19_fire_heatcut.md` §2.3–2.4)
- As designed, K1 sits in a hard-wired 20 A radial feeding the wok. K2–K4 switch outlets on the radials and on an FCU spur [S `research/r19_fire_heatcut.md:61-64,75-79`]. That is fixed wiring, so **an LEW must design (or accept), install, test and certify it** under SS 638 [S E1, E2; already stated at `r19_fire_heatcut.md:214`].
- **Who builds the box.** E2 excludes "manufacturing … or assembling … to produce a new article" from "electrical work". So a panel builder (or the user) could assemble the DIN box, and the LEW installs, connects and certifies it [E: whether an LEW will certify a panel they did not build is the LEW's call; most will want to build or inspect it]. **Recommended [E]:** the LEW supplies and builds the 230 V part (contactors, terminals, fusing). The project supplies only the 24 V SELV side (safety relay, watchdog, sensors) and a terminal list, as `r19_fire_heatcut.md:215` already proposes.
- **Plug-in alternative [E]:**
  - Built as a plug-in box (one BS 1363 13 A inlet plug, contactors, 13 A outlets), it is outside the "installation", and the user may build it.
  - But it is limited to 13 A in total, so it cannot carry the wok, and only one heater at a time.
  - A home-made multi-outlet box is a "Portable socket-outlet" in form. That is fine for own use under CPSR, but it fails an insurer's SAFETY Mark condition [S N1].
  - Not recommended for the heaters.
- **Leakage and RCD type.**
  - Keep one 30 mA RCBO per new circuit [S `r19_power_budget.md:220-222`].
  - Servo drives and PSUs can put smooth DC leakage on the PE conductor. Ask the LEW to choose Type A (or F) RCBOs, not AC type [E].

### 2.4 The wok feed: HDB vs condo (this changes the electrical scope)

| Housing | Rule | Wok option | Src |
|---|---|---|---|
| HDB, 40 A main switch (blocks from 1 Jan 1994 or MUP/HIP) | New 15 A point / 20 A isolator: no permit. But "Appliances with electrical rating exceeding 15amps power is not allowed", and the 20 A isolator is only for air-con. Cooker units: no limit on number, but "the rating of appliances not exceeding 15amps power point" | A ≤ 15 A cooker (≤ about 3.3 kW at 230 V) on a 15 A round-pin point, or a 3.0 kW unit on 13 A (`r19_power_budget.md:71`). The 3.5 kW unit only with HDB's written approval: "seek HDB's approval before starting electrical works that involve electrical items not listed" | H1 |
| HDB, 30 A main switch | New 15 A points need an HDB permit. Cooker unit ≤ 3 kW | ≤ 3 kW unit; a permit for a 15 A point. The 40 A main (ELUP) may come later [S `r19_power_budget.md:203`] | H1 |
| Condo / private | No 15 A appliance rule found. The load is set by the approved load; upgrades go through the LEW and the MCST [S `r19_power_budget.md:199,211`] | A 20 A radial + hard-wired 3.5 kW unit (the current plan) | SP1 via `r19_power_budget.md` |

---

## 3. HDB vs condo/MCST renovation rules

| Work in this project | HDB | Condo / MCST |
|---|---|---|
| Floor rail (#39): MS-polymer and VHB on tiles + 12 screws into the plinth [S `R19_DOCK.md:117-120`] | No permit. Fasteners "must not exceed 6mm in diameter and 40mm in penetration depth" [S H2, H3]. Keep away from concealed conduits (HDB "Drilling of Holes in Flats with Concealed Electrical Wiring" drawing) [S H1] | By-laws apply; many MCSTs require a renovation application [S M1; E]. BCA: structural works need plans by a PE; light fixings are not structural [S M2; E] |
| Tether chain or reel in the plinth void, slotted kickboard [S `research/r19_tether.md:19-20`] | Carpentry; no permit [E] | Same [E] |
| Cart (131.9 kg) and appliances on the floor | "Installation of equipment not exceeding 150kg": no permit [S H2] | — |
| New circuits, outlets, contactor box | LEW. New 13 A points, extensions and rewiring: no permit in any flat. New 15 A point: a permit only in 30 A flats. Never embed conduit in the RC slab, wall or plaster: surface trunking only. CS/5H + SPSL test [S H1] | LEW + SP Services. A load upgrade needs MCST approval [S `r19_power_budget.md:199`]. MCST renovation approval is often required [S M1] |
| Kitchen modifications (counter, dapoh, shelf) | Counter top / cement base: no permit, but no concrete shelf, and finishes ≤ 50 mm [S H2] | By-laws [E] |
| Faucet replacement, solenoid valve (DECISIONS:59-61) | Water service and sanitary works by a PUB Licensed Plumber. Simple plumbing by a handyman [S H3] | Same PUB rule [E] |
| Gas (hob stays) | Gas pipe alteration and removal by City Energy or an LGSW. Gas pipes not embedded in floor screed or finishes [S H2, H3] | Same EMA gas rule [S `r15_cooking_market.md:125`] |
| Work hours | Electrical work 8am–6pm. Noisy work weekdays 9am–5pm only. Max 2 approved power tools at once [S H1] | By-laws [E] |
| Indemnity | The owner indemnifies HDB for damage or injury arising from the works [S H1] | — |

**Condo sources are weak.** I read only a law-firm note that SPs "are generally required to apply the management corporation (MCST) for approval … before proceeding" [S M1]. Each MCST's by-laws differ. Ask the condo office for its renovation guidelines (the user's action).

---

## 4. Robots / machinery

- **No home-robot law found.**
  - Searched: "Singapore regulation household robot safety", consumer-robot legislation, the CPSR list (no robot category; the only robot item is a robot-vacuum *docking station*, under "Vacuum cleaner" [S C1 p.53]).
  - Results: a 2026 press feature in which a company says there is no legislation for humanoid robots [S R1, secondary]; a TÜV SÜD case of a cleaning robot certified against CE and local standards [S R1].
  - ISO 13482 and IEC 60335 are voluntary bases here, as the project already assumes [S `DECISIONS.md:7`]. China's GB/T 41527-2022 (household service robots) is a reference only [S R1].
- **WSH Act.** It applies to workplaces. A home becomes one for the LEW, plumber or renovator while they work there (their employer's duty) [E]. Singapore's UPR submission says foreign domestic workers "are not covered by the Workplace Safety and Health Act" [S W1].
- **A foreign domestic worker using the robot.** The Employment of Foreign Manpower (Work Passes) Regulations, Fourth Schedule, Part I, condition 2: the employer "shall provide safe working conditions and take such measures as are necessary to ensure the safety and health" of the FDW. MOM has prosecuted employers for unsafe tasks (cleaning windows, a glass ceiling); fines up to $10,000 or 12 months [S W2]. **Implications [E]:**
  - she is trained on the E-stop, re-arm and fire actions (`r19_fire_heatcut.md` §3.3);
  - she is never inside the arm's reach while heat is armed;
  - she is not left as the only "capable adult" unless the user decides she is (decision D-FDW below).
- **IMDA (radio parts: MIoT, Wi-Fi smart plugs, BLE).** Personal-use imports need no registration, but the user must make sure the equipment complies with IMDA standards and does not interfere [S I1 Q40-Q42].

---

## 5. Insurance

| Policy | What it says (relevant) | Src |
|---|---|---|
| HDB fire insurance (Etiqa, compulsory for HDB loans [E]) | Covers HDB-provided structure, fixtures and fittings; "excludes any renovations or improvements made to the insured property by the Lessee". Contents and liability are not covered | N3 §15.2 |
| Etiqa ePROTECT home (2024 wording) | **General condition 21:** "It is a condition precedent to Our liability that all electrical equipment is compliant with the … (CPSR) and affixed with the Safety Mark." Accidental damage to appliances is covered only under the same condition. Personal liability up to $500,000 per occurrence; excludes "mechanically propelled vehicle" and business use. Duty of care; duty of disclosure under Insurance Act s.23(5) | N1 |
| AIG Homes Advantage | Excludes "Electrical or mechanical break down(s)"; repair costs after "attempted repair or modification by You"; liability "arising from the carrying out of alterations, additions, repairs or decorations"; "any mechanically propelled vehicle"; business activity. You "must inform us immediately" when information changes. Duty to take "all reasonable precautions" | N2 |
| Tokio Marine Flexi Home | Exclusions include "faulty workmanship or design" (brochure) | N4 |

**What to tell the insurer, in writing, before the first powered run [E]:**
1. A self-built cooking robot: arm model, cart with motorised wheels on a floor rail, about 132 kg.
2. The heat sources: power, origin, and whether each one carries the SAFETY Mark. Imported units: say "own import, LEW-connected".
3. The electrical work: an LEW-certified installation (SS 638, CS/5H / SPSL tested). Attach the certificate.
4. The safety design: the heat-enable contactor chain, manual re-arm, the heat detector, the fire blanket and extinguisher (`r19_fire_heatcut.md` §2, §3).
5. The supervision rule (D1 in `r19_fire_heatcut.md`): an adult at home and awake while heat is armed.
6. Whether an FDW operates it.
7. Ask four questions: does cover still apply to fire or smoke damage from the robot or imported appliances? Does personal liability cover injury to a visitor, the FDW or a neighbour's flat? Does the "mechanically propelled vehicle" exclusion apply to the cart? Is an endorsement or extra premium needed?

**Typical exclusions to expect** [S N1, N2; E for the generalisation]:
- breakdown or burnout of the appliance itself;
- wear and tear;
- faulty design or workmanship;
- business use;
- fines;
- property in your own care;
- non-disclosure (policy void);
- with Etiqa-type wording, any non-SAFETY-Marked electrical equipment.

**If the current insurer has a SAFETY Mark condition precedent, either replace every unmarked heater with an SG-registered one, or move to an insurer that confirms cover in writing [E].**

---

## 6. Gas (the user's 4-burner gas hob stays)

- **Rules already in the repo:**
  - gas work only by City Energy or an LGSW;
  - buy gas cookers with the SAFETY Mark;
  - City Energy checks every 5 years;
  - an unlicensed worker is an offence, fine up to $10,000 or jail
  
  [S `research/r15_cooking_market.md:38,125-129`]. Gas cooking appliances are a **High-risk** Controlled Good [S C2].
- A robot turning the existing knobs from outside leaves the gas train untouched. A solenoid, a sensor or a motor *inside* the hob is gas service work: LGSW, and it may void the approval [S `r15_cooking_market.md:132`, inferred there].
- No rule was found against an electric countertop cooker standing next to a gas hob [E: none found]. Keep the manufacturers' clearances. Do not stand the cooker on the gas hob or route cables over the gas hose or pipe [E].
- **Current safety plan:** gas valve closed during every robot session (`r19_fire_heatcut.md:30,235`, D7). Removing or capping the gas branch must be done by City Energy or an LGSW, leaving 100 mm of capped pipe [S H3].
- HDB: no gas pipe may be enclosed in false ceilings or embedded in floor screed [S H2]. The floor rail must not cover or stress the gas pipe [E].

---

## 7. Checklist

| # | Item | Rule | Who | Cost [E unless S] | Status |
|---|---|---|---|---|---|
| 1 | Record housing type (HDB / condo) and main switch (30 / 40 / 63 A) | Decides the wok path (§2.4) | User | 0 | **Open** |
| 2 | Wok cooker choice | HDB: ≤ 15 A appliance [S H1]. Condo: 20 A hard-wired possible | User + LEW | 0–300 SGD to change models | Open |
| 3 | Replace China/EU plug-in heaters with SG-registered ones (zone 2, fryer, stew pot, rice cooker, kettle) | CPSR (supplier) + insurer condition [S C2, N1] | User | about 300–900 SGD in total | Open |
| 4 | Imported items kept (concave cooker; slicer if no SG model): SAFETY-Marked BS 1363 plug, or LEW hard-wire | Plugs CG [S C1 p.17]; fixed wiring for > about 3 kW [S C1 p.21] | User (plug) / LEW | Plug 5–15 SGD each | Open |
| 5 | Never use travel adaptors, universal sockets or the Schuko reel | [S C3, E1; `r19_tether.md:28`] | User | 0 | Reel already rejected |
| 6 | LEW survey: DB, RCCB, circuits, spare ways (`r19_power_budget.md:214-218`) | EMA LEW only [S E1] | LEW | 100–200 SGD visit | Open (#11) |
| 7 | 2 new 20 A radials with 30 mA RCBO (Type A), about 6 × 13 A outlets, a 3 A spur, surface trunking | SS 638; no embedding in HDB [S H1] | LEW | 1,200–2,500 SGD | Open |
| 8 | Wok feed (condo: hard-wired 20 A; HDB: 15 A point, cooker ≤ 15 A) | [S H1] | LEW | 150–400 SGD | Open |
| 9 | Contactor box K1–K4 on the 230 V side, connected and certified | Fixed wiring [S E2]; `r19_fire_heatcut.md:214` | LEW (230 V); project (24 V side) | Parts SGD 1–2k [S `r19_fire_heatcut.md:210`] + LEW 300–800 | Open |
| 10 | CS/5H + SPSL test of new wiring; LEW certificate | [S H1, E1] | LEW applies | SPSL fee not found | Open |
| 11 | RCCB present and tested monthly | Statutory since 1 Jul 2025 [S E1] | User | 0 (if present) | Check at survey |
| 12 | Floor rail fixing ≤ 6 mm / 40 mm, clear of conduits and gas pipe | [S H1, H2] | User / carpenter | 0 | Design complies (`R19_DOCK.md:117-120`) |
| 13 | Condo only: MCST renovation application, by-laws, deposit | [S M1] | User | Deposit varies | Open if condo |
| 14 | Faucet / solenoid valve | PUB Licensed Plumber [S H3] | Plumber | 100–300 SGD | Open |
| 15 | Gas hob: valve closed in sessions; any capping by City Energy / LGSW | [S H3; r15:125] | User / LGSW | 0 / 100–200 SGD | Proposed (D7) |
| 16 | Insurer: written disclosure + written answer | Duty of disclosure [S N1, N2] | User | Possible premium change | Open |
| 17 | Confirm the personal-import reading with the CPSO (optional) | §1.1 | User | 0 | Optional |
| 18 | FDW: training and rule, if applicable | EFMA work-permit condition [S W2] | User | 0 | Open |
| 19 | Fire blanket + powder extinguisher | `r19_fire_heatcut.md` §3.1 | User | S$35 blanket [S `r19_fire_heatcut.md:208`] + 30–60 SGD | Proposed (D2) |
| 20 | Radio devices conform to IMDA standards | [S I1] | User | 0 | Prefer SG-sold devices |

All LEW prices are guesses. No SG quote was read for this scope. The repo's figure is "3,000 + electrician (unknown)" [S `research/r19_system_cost.md:64`].

---

## 8. Decisions for the user

- **D-HOME.** Is the flat HDB (which block loading?) or a condo? Everything in §2.4 depends on this.
- **D-WOK.**
  - (a) Condo: keep the 3.5 kW import, hard-wired by an LEW.
  - (b) HDB: switch to a ≤ 15 A cooker (≤ about 3.3 kW; 3.0 kW is the safe pick) on a 15 A or 13 A point.
  - (c) HDB: apply for HDB approval for the 3.5 kW unit (an unlisted item; the outcome is unknown).
- **D-SOURCE.** SG-registered equivalents for every heater that has one (recommended), with imports only where none exists. Or keep the China/EU units for own use and accept the insurance risk.
- **D-PANEL.** The heat-enable contactor box built and certified by the LEW on the 230 V side (recommended). Or a plug-in box (not possible for the wok; 13 A total).
- **D-INSURER.** Tell the current insurer in writing now, or change to one whose wording has no SAFETY Mark condition precedent.
- **D-FDW.** If a domestic worker lives in: may she operate or supervise the robot, and does she count as the "capable adult" under `r19_fire_heatcut.md` D1?
- **D-GAS.** Keep the gas hob with its valve closed during sessions (D7), or have City Energy or an LGSW cap it.

## 9. Next steps
1. User: record the housing type, the main switch rating and the RCCB rating (photo of the DB) in `inputs/user_kitchen/`. Closes the D-HOME blocker for #17 and #24.
2. Rerun the power and heat-cut plans for the HDB case if D-HOME = HDB: a ≤ 15 A wok and K1 on a 15 A point (`r19_power_budget.md` P1 still holds for the other loads [E]).
3. Write the LEW brief: survey items (`r19_power_budget.md:214-231`) + contactor box (`r19_fire_heatcut.md` §2.4) + "Type A RCBOs, surface trunking, CS/5H". Get 2–3 quotes (#24 study step 3; the user contacts the LEWs).
4. Fill the SG-registered alternatives into the BOM: one candidate per heater, checked on the CPSO Register of Registered Controlled Goods (go.gov.sg/safety-mark [S C5]). Re-check MIoT or local control for the new zone-2 unit.
5. Bench-check that the chosen plug-in heaters return to OFF after a power cut (already `r19_fire_heatcut.md` next step 3). Same test for any replacement models.
6. User: send the insurer the written disclosure in §5 and file the reply in the repo. Optionally, ask the CPSO to confirm the personal-import reading.
7. Condo only: get the MCST renovation guidelines and by-laws.
8. Close #24 when the matrix (§1.2) is accepted, the LEW scope is quoted and the insurer has replied (the issue's own close rule).

---

## 10. Sources (web, read-only, 2026-10-14)

- **C1** CPSO, *Consumer Protection (Safety Requirements) Regulations Information Booklet*, updated 24 Jun 2026. PDF read in full via pdftotext; page numbers are PDF pages: https://isomer-user-content.by.gov.sg/498/d3a57a14-70d7-41fb-b395-683970d06c80/cps-info-booklet.pdf
- **C2** CPSO, List of controlled goods (33 categories with risk tiers): https://www.consumerproductsafety.gov.sg/suppliers/cpsr/list-of-controlled-goods/ ; CPSR overview (fine up to S$10,000 or 2 years): https://www.consumerproductsafety.gov.sg/suppliers/cpsr/overview-of-cpsr/
- **C3** CPSO, Safety tips on universal socket outlets ("cannot be registered with a valid Safety Mark"): https://www.consumerproductsafety.gov.sg/consumers/product-safety-tips/home-appliances-furniture-and-indoor-product-safety/safety-tips-on-universal-socket-outlets/ [search snippet]; HK:088 travel adaptor alert: https://www.consumerproductsafety.gov.sg/files/product-safety-alerts-and-recalls/electrical/electrical-alert-2022-06-16-hk088%20travel%20adaptor.pdf [search result]
- **C4** CPSO FAQ for consumers (purview, plug SAFETY Mark, plug advice): https://www.consumerproductsafety.gov.sg/about/faqs/for-consumers/
- **C5** CPSO, Shopping for safe products online (register link go.gov.sg/safety-mark): https://www.consumerproductsafety.gov.sg/consumers/choose-safer-products/shopping-for-safe-products-online/
- **E1** EMA, Electrical Safety (LEW requirement, RCCB rule, $5,000 fine, no piggy-backing), last updated 19 Mar 2026: https://ema.gov.sg/consumer-information/electricity/electrical-safety [read in Chrome]
- **E2** Electricity Act 2001, s.2 definitions ("electrical installation", exclusion (b) wef 8 Dec 2023; "electrical work"): https://sso.agc.gov.sg/Act/EA2001?ProvIds=pr2-
- **E3** Electricity Act 2001, s.83 offences: https://sso.agc.gov.sg/Act/EA2001?ProvIds=pr83-
- **H1** HDB, Renovation Guidelines for Electrical Works (15 A appliance rule, 20 A isolator for air-con only, LEW, CS/5H, no embedding), last updated 24 Jul 2026: https://www.hdb.gov.sg/managing-my-home/renovation-and-maintenance/renovation/renovation-guidelines/electrical-works [read in Chrome; this settles the "to confirm" item at `r19_power_budget.md:68-71,202`]
- **H2** HDB, Renovation Guidelines for Building Works (fasteners 6 mm / 40 mm, equipment ≤ 150 kg, kitchen, floor finishes), last updated 2 Sep 2026: https://www.hdb.gov.sg/managing-my-home/renovation-and-maintenance/renovation/renovation-guidelines/building-works
- **H3** HDB, Water and Sanitary Plumbing Works and Gas Works (PUB Licensed Plumber, LGSW / City Energy, capping): https://www.hdb.gov.sg/managing-my-home/renovation-and-maintenance/renovation/renovation-guidelines/water-and-sanitary-plumbing-works-and-gas-works
- **M1** Lee & Lee, BMSMA law update (SPs generally need MCST approval before renovating): https://www.leenlee.com.sg/wp-content/uploads/2017/02/BMSMA-Law-Update-Full2.pdf [search snippet]; Rajah & Tann, *Judicial approach in MCST cases*: https://www.rajahtannasia.com/viewpoints/judicial-approach-in-mcst-cases-to-defer-to-or-differ-from-a-management-corporation/ [search snippet]
- **M2** BCA, building works not requiring approval / structural plans by a PE: https://www1.bca.gov.sg/guidelines-and-requirements/building-works-not-requiring-approval/ [search snippet; the page did not render]
- **N1** Etiqa, ePROTECT home policy wording V9.0 (condition 21 SAFETY Mark; Section B liability $500,000; exclusions): https://www.etiqa.com.sg/wp-content/uploads/2024/01/ePROTECT-home-Policy-Wording.pdf [PDF read in full]
- **N2** AIG, Homes Advantage policy wording (exclusions, duty to inform, duty of care): https://orgn-aigsg1.dmp.aig.com/content/dam/aig/apac/singapore/documents/forms/homes-advantage-policy-wording-with-home-assistance.pdf [PDF read in full]
- **N3** Etiqa, HDB fire insurance terms and conditions V1.0, Aug 2024 (§15.2 excludes owner renovations): https://etiqa.com.sg/wp-content/uploads/2024/06/hdb-fireinsurance-tcs.pdf [PDF read]
- **N4** Tokio Marine Flexi Home brochure, Aug 2025: https://www.tokiomarine.com/content/dam/tokiomarine/sg/non-life/product-personal/home/Tokio%20Marine-Flexi%20Home%20Brochure_Aug%202025_v5.pdf [search snippet only]
- **I1** IMDA, Equipment Registration Q&A (Oct 2016), Q40–Q45 "Telecommunication Equipment for Personal Use": https://imda.gov.sg/-/media/imda/files/regulation-licensing-and-consultations/licensing/licenses/eqrqna.pdf [PDF read]
- **W1** Singapore UPR submission (FDWs not covered by the WSH Act, EA or WICA; covered by EFMA): https://upr-info.org/sites/default/files/documents/2021-04/cde_upr38_sgp_e_main.pdf [search snippet]
- **W2** MOM press releases: https://www.mom.gov.sg/newsroom/press-releases/2018/0517-employer-charged-for-failing-to-ensure-safety-of-fdw and https://www.mom.gov.sg/newsroom/press-releases/2018/0808-employer-fined-for-failing-to-ensure-safety-of-two-foreign-domestic-workers [search snippets: Fourth Schedule condition 2, fines]
- **R1** Robot rules search (none SG-specific): LinkedIn repost of a Lianhe Zaobao feature, https://sg.linkedin.com/in/jiabinqin ; TÜV SÜD LionsBot case, https://www.tuvsud.com/en-id/industries/manufacturing/machinery-and-robotics/robotic-safety/lionsbot-certificate-ceremony ; GB/T 41527-2022 summary, https://backup.sesec.eu/?p=6392 [all search snippets, low weight]
- **SP1** SP Group, *How to Apply for Electricity Connection*, Jan 2026, as cited at `research/r19_power_budget.md:199,273`.
- **Repo:** `DECISIONS.md:7,29,59-61`; `research/r15_cooking_market.md:38,63,125-132,420`; `research/r19_power_budget.md:68-71,88,197-231`; `research/r19_system_cost.md:60-82`; `research/r19_fire_heatcut.md:30,61-79,208-216,235`; `research/r19_tether.md:17,19-20,28,48`; `sim/r10/claude/hardware.py:15`; `sim/r10/claude/README_R10.md:503`; `sim/r10/claude/R19_DOCK.md:117-120`; `sim/r10/claude/results/hardware.json` (`cart.total_model_mass_kg` = 131.9).

**Not found / gaps.**
- A CPSO statement on personal imports.
- The CAB test cost for registering one model.
- SP Services' CS/5H testing fee.
- SG LEW price lists for this scope.
- Condo by-law texts.
- The BCA list of insignificant works (the page did not render).
- The SG-registered status of each specific replacement model.
- Income and MSIG home policy wordings (not read).
