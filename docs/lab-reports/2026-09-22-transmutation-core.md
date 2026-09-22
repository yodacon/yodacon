# The transmutation core: lithium as a battery made of matter

**22 September 2026** · design · follows
[the lithium fuel cycle](2026-09-22-lithium-fuel-cycle.md)

The fuel report ended on a famine. Twenty-eight electronics plants in the
galaxy held 1,660 t/day of nameplate capacity against 1,757 t/day of demand
and actually made **54.6 t/day**, because chips need copper, copper is a
one-jump good, and the recovered gazetteer has one world per system. Three
shipyards existed. Not one ton of hull plate was pressed in two simulated
years. The diagnosis was: *there is nowhere for the copper to go.*

This report is the other answer to that. Not a better road — **a different
kind of cargo.**

> A ship does not haul copper. It hauls heavy lithium, and a transmutation
> core at the far end makes copper out of it. Lithium is not one commodity
> among thirty: it is the form every other commodity travels in.

That one sentence does a great deal of work, and none of it is invented.
Lithium sits in the deepest trough of the binding-energy curve of any stable
element. Everything else in the periodic table is downhill from it. A tonne
of lithium is a tonne of matter **with an energy debt already paid into it**,
and letting it fall toward iron pays the debt back. It is a charged battery
whose electrolyte is the cargo.

So the lithium trade is simultaneously a matter trade and an energy trade,
and the transmutation core is the terminal at both ends of it.

---

## 1. Two curves and a line

Everything about the economics of this device falls out of two quantities
that are measured, not designed.

### The yield: binding energy

The chart of the nuclides is, read economically, a price list. A nucleus's
binding energy per nucleon is how much energy was released assembling it, and
the difference between two nuclides is what you get (or pay) for going from
one to the other.

```
  BE/A            the iron peak
  (MeV)              ↓
   9 ┤                    ▁▄█████▇▆▅▅▄▄▃▃▂▂▁
   8 ┤              ▂▄▆███                   ▔▔▔▚▄▃▂
   7 ┤        ▁▃▅██                                  ▔▚▂   ← U-238  7.570
   6 ┤     ▂▄█                                              
   5 ┤  ▁▄█ ← ⁷Li  5.606   THE LITHIUM TROUGH
   4 ┤ ▄
   3 ┤█
     └┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬──
      H   He   Li    C    O   Si   Fe   Ag   Ba   Au    U
```

Lithium, beryllium and boron are the hole in the curve — the elements the Big
Bang under-made and stars destroy rather than build. `⁷Li` binds at **5.606
MeV/nucleon** against iron's 8.790 and the true maximum, `⁶²Ni`, at **8.7945**.
That 3.18 MeV/nucleon gap is the whole business.

The unit that converts it into game numbers:

> **1 MeV/nucleon, applied to one tonne = 96.48 PJ**
> (6.022×10²⁹ nucleons/t × 1.602×10⁻¹³ J/MeV)

So `Li → Fe` releases **307 PJ per tonne**, and the tonne gets *lighter* by
exactly 3.42 kg, because that energy was mass. There is no bookkeeping
problem here, only a bookkeeping *upgrade* — see §9.

### The cost: the Coulomb barrier

The binding-energy gain says the reaction is downhill. It does not say it is
easy. Assembling a nucleus of charge *Z* means pushing charge together
against its own repulsion, and the semi-empirical mass formula prices that
exactly:

```
    E_C = a_C · Z(Z−1) / A^⅓        a_C = 0.714 MeV
```

Per nucleon, that runs from 0.32 MeV for lithium to 4.05 MeV for uranium. It
is not stored in the product — it is *circulated* through the drive — so what
it costs you is the drive's inefficiency.

### The line

Yield minus barrier, against lithium, at perfect coupling:

| target | BE/A | ΔBE/A | E_C/A | ΔE_C/A | net MeV/nuc | **PJ / tonne** | mass lost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C-12 | 7.680 | 2.074 | 0.780 | 0.460 | **+1.614** | **+156** | 2.23 kg/t |
| O-16 | 7.976 | 2.370 | 0.992 | 0.672 | +1.698 | +164 | 2.54 |
| Al-27 | 8.332 | 2.726 | 1.375 | 1.055 | +1.671 | +161 | 2.93 |
| Si-28 | 8.448 | 2.842 | 1.528 | 1.208 | +1.634 | +158 | 3.05 |
| Cr-52 | 8.776 | 3.170 | 2.031 | 1.711 | +1.459 | +141 | 3.40 |
| **Fe-56** | 8.790 | 3.184 | 2.166 | 1.846 | **+1.338** | **+129** | 3.42 |
| Ni-62 | 8.7945 | 3.188 | 2.200 | 1.880 | +1.309 | +126 | 3.42 |
| **Cu-63** | 8.752 | 3.146 | 2.313 | 1.993 | **+1.153** | **+111** | 3.38 |
| Zn-64 | 8.736 | 3.130 | 2.426 | 2.107 | +1.023 | +99 | 3.36 |
| Ag-107 | 8.554 | 2.948 | 3.039 | 2.719 | +0.229 | +22 | 3.16 |
| Sn-118 | 8.517 | 2.911 | 3.022 | 2.702 | +0.209 | +20 | 3.13 |
| **Ba-138** | 8.393 | 2.787 | 3.084 | 2.764 | **+0.023** | **+2** | 2.99 |
| W-184 | 8.026 | 2.420 | 3.685 | 3.366 | −0.946 | −91 | 2.60 |
| Pt-195 | 7.927 | 2.321 | 3.792 | 3.472 | −1.151 | −111 | 2.49 |
| Au-197 | 7.916 | 2.310 | 3.838 | 3.518 | −1.208 | −117 | 2.48 |
| Pb-208 | 7.867 | 2.261 | 3.848 | 3.528 | −1.267 | −122 | 2.43 |
| U-238 | 7.570 | 1.964 | 4.053 | 3.733 | −1.769 | −171 | 2.11 |

The two curves cross at **barium, Z = 56**, where the net is +0.023
MeV/nucleon — two picojoules per tonne, which is zero.

> **THE BARIUM LINE.** Everything lighter than barium is a power station.
> Everything heavier is a power bill. Tungsten, platinum, gold, lead, thorium
> and uranium are net energy sinks *at any efficiency a machine can have* —
> their break-even coupling is 1.39, 1.50, 1.52, 1.56, 1.84 and 1.90, and
> coupling cannot exceed one.

Nobody chose that. It is where the Coulomb term overtakes the binding term,
and it is the reason gold has been worth something on every world humans have
ever stood on: **past barium, the universe charges you.**

### Efficiency is the tech tree

The core's coupling η is the one number an upgrade moves, and moving it walks
the paying line up the chart. Net PJ per tonne of lithium converted:

| target | Mk I η .35 | Mk II η .55 | Mk III η .70 | Mk IV η .88 | Mk V η .97 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Carbon | **+73** | +119 | +137 | +150 | +154 |
| Silicon | −59 | **+62** | +108 | +142 | +154 |
| Iron | −202 | −17 | **+53** | +105 | +124 |
| Copper | −246 | −46 | **+29** | +85 | +105 |
| Silver | −465 | −193 | −90 | −14 | **+14** |
| Barium | −493 | −216 | −112 | −34 | −6 |
| Gold | −747 | −394 | −262 | −163 | −127 |
| Uranium | −840 | −465 | −325 | −220 | −182 |

A Mk I core is a carbon plant. A Mk III is a foundry — it pays to make iron
and copper, which is precisely the famine the last report measured. A Mk V
reaches silver and stops, for ever, because barium is where physics stops.

---

## 2. The machine

The device is called a **transmutation core**, and it is three machines in a
feedback loop. Each stage answers a different question.

### Stage 1 — the sort. *Which nuclide am I holding?*

This is the "really strong MRI", and it is the part of the analogy that is
literally correct. Nuclear magnetic resonance is **isotope-selective**,
because the Larmor frequency ω = γB depends on the gyromagnetic ratio, and γ
is a property of the *nuclide*, not the element:

| nuclide | γ/2π (MHz/T) | Larmor at 1 kT |
| --- | ---: | ---: |
| ¹H | 42.577 | 42.6 GHz |
| ⁶Li | 6.266 | 6.3 GHz |
| ⁷Li | 16.546 | 16.5 GHz |

⁶Li and ⁷Li are separated by a factor of 2.6 in frequency. A sorting field
addresses one and ignores the other, so the core takes a **pure isotope
stream off an impure feedstock with no centrifuge, no cascade and no
half-life**. That matters because the two lithium isotopes do opposite jobs:
`⁶Li + n → ⁴He + ³H` releases 4.78 MeV and breeds tritium, while
`⁷Li + n → ⁴He + ³H + n` *costs* 2.47 MeV and multiplies neutrons. You need
both, in a ratio you choose, and the sort is how you choose it.

### Stage 2 — the drive. *Deposit quanta at the nucleus's own frequency.*

A nucleus has a natural oscillation: the **giant dipole resonance**, the
collective mode where all the protons swing against all the neutrons. It sits
at

```
    E_GDR ≈ 78 · A^(−⅓)  MeV
```

which is 20.4 MeV at iron and 13.2 MeV at lead — against measured values of
18.5 and 13.4. It is the frequency at which a nucleus will *absorb*, and it
is the only frequency at which you can put energy into the nucleus as a whole
rather than merely heating the electrons off it.

That is the feedback loop, and it is forced rather than chosen: **as the
charge builds, A rises, and E_GDR falls as A^(−⅓).** The drive must chirp
downward through the whole synthesis, tracking a resonance that is moving
because of what the drive is doing to it. Lock is the entire engineering
problem. Lose lock and you are depositing 20 MeV quanta into a nucleus whose
resonance has walked to 16, which does not build anything — it just boils.

| A | E_GDR | frequency |
| --- | ---: | ---: |
| 7 (Li) | ~41 MeV | 9.9 × 10²¹ Hz |
| 56 (Fe) | 20.4 MeV | 4.9 × 10²¹ Hz |
| 197 (Au) | 13.4 MeV | 3.2 × 10²¹ Hz |

### Stage 3 — the confinement. *Hold it still while it decides what to be.*

The charge is a millimetre of plasma at silicon-burning conditions. It is
held by the same physics the Yodacon flies behind, and this is not a
coincidence of fiction — it is the same three problems:

| reentry pillow | transmutation core |
| --- | --- |
| magnetopause stand-off ∝ (p_mag/p_flow)^⅙ | magnetic bottle vs. charge pressure |
| polar cusps leak flow onto the nose | cusps leak charge out of the focus |
| phased array leans the envelope | phased array steers the arc field for uniformity |
| seed ring buys continuum where air is too thin | laser ablation drives the implosion |

**Uniformity is the whole game**, exactly as it is in inertial confinement
fusion. An implosion that is 1% out of round is not 99% as good; the
Rayleigh–Taylor instability turns the asymmetry into a jet, the jet reaches
the wrong part of the chart, and — see §3 — the charge walks past a drip line
and dismantles itself. The lasers compress; the steering field keeps the
compression *round*; the GDR drive pumps; and the product is a single nuclide
rather than a smear.

### On "energies above a supernova"

Worth being exact about, because the interesting claim is the opposite one.

The **per-nucleon** energies are supernova energies: 10–40 MeV quanta exist
naturally only in the photon tail of silicon burning at T ≈ 5×10⁹ K, which is
also where stellar photodisintegration happens. But the **total** energy is
trivial — a few hundred petajoules per tonne, against roughly 10⁴⁴ J for a
core collapse.

So the core is not a small supernova. A supernova has overwhelming energy and
no containment, and what it produces is a *smeared abundance curve* —
everything at once, in the proportions the r-process happens to leave. The
core has almost no energy and total containment, and what it produces is
**one nuclide on purpose**. That is the entire technology: not more energy,
better-aimed energy.

---

## 3. The drip lines: the walls of the board

The chart of the nuclides is not an open plain. It has edges, and the edges
are where a nucleus stops being able to hold another nucleon at all — the
separation energy goes negative and the nucleon *drips out*. Three
consequences, all of them mechanics.

### The walls

Beyond the drip line there is nothing to make. A drive that overshoots does
not make a heavier nuclide, it makes a lighter one plus a loose nucleon, on a
timescale of ~10⁻²² s. **Overdrive is not inefficiency; it is loss of
product.** This is the mechanical consequence of imperfect uniformity, and it
is why confinement quality and drive power are separate upgrades that must be
bought in step.

### The waiting points

Climbing the chart by capture drives you *off* the valley of stability toward
a drip line. You cannot keep capturing; you have to stop and let the nucleus
beta-decay back toward the valley before it can take another nucleon. Those
stalls are the **waiting points**, and beta decay is the slowest thing in the
process by orders of magnitude.

> **Throughput is gated by half-lives, not by power.** A core with a star
> behind it still cannot make tin faster than the isobaric chain to tin will
> settle.

This is a *second cost axis*, independent of energy, and it is what stops a
well-fed core from being an infinite-matter printer. The proton-rich path's
waiting points are known and conspicuously even-Z — ²¹Mg, ³⁰S, ³⁴Ar, ³⁸Ca,
⁵⁶Ni, ⁶⁰Zn, ⁶⁴Ge, ⁶⁸Se, ⁷²Kr, ⁷⁶Sr, ⁸⁰Zr — because nucleon pairing binds even
numbers harder. The neutron-rich path's stalls are the closed shells at
N = 50, 82 and 126, which is why those are the abundance peaks in the real
solar system.

### The two roads, and where each one ends

`⁷Li` has N/Z = 1.33. It is **already neutron-rich for a light nucleus**, so
the natural road up the chart from lithium is the neutron road. Going
proton-rich means stripping neutrons first, and paying for it.

| | neutron road (r-like) | proton road (rp-like) |
| --- | --- | --- |
| driver | neutron flux | proton capture |
| natural from ⁷Li | **yes** | no — strip first |
| stalls at | N = 50, 82, 126 | even-Z waiting points |
| barrier | none (neutrons are neutral) | Coulomb, rising as Z |
| terminates | the neutron drip line — **unmapped past neon** | **A ≈ 107**, the Sn–Sb–Te cycle |

That second termination is real and it is a gift to the design: the
proton-capture road genuinely cannot get past about A = 107, because (γ,p)
and (γ,α) photodisintegration and alpha instability close it into a cycle.
**If you want anything heavier than silver, you must take the neutron road.**

### The chart runs out at neon

The single best piece of lore in the source material is that it is *true*:
the neutron drip line has been established experimentally only to **neon,
Z = 10**, at N = 24. The heaviest bound sodium, `³⁹Na`, was confirmed in 2022
on nine detection events out of 5×10¹⁷ beam nuclei. Beyond Z ≈ 12 the edge of
nuclear existence is model extrapolation — and the models disagree: the
finite-range droplet model and the Hartree–Fock–Bogoliubov mass model both
predicted ³⁹Na *unbound*; the shell model got it right.

So a transmutation core does not ship with a map. It ships with a **chart**,
and the chart is an asset:

> **A core's route table is a purchasable upgrade, separate from its power.**
> The cheap chart is a droplet model: fine through the iron peak, wrong at
> the edges, and a route it plots into unmapped territory sometimes ends at a
> drip line nobody had measured. The expensive chart is shell-model data
> somebody flew a survey to obtain.

That gives the survey AI a second job — prospecting *nuclides* rather than
seams — and it makes "we do not know where the edge is" a mechanic instead of
a hand-wave.

---

## 4. Reverse gear: how a metal becomes lithium again

The user's question — *how do ships move metals around?* — is answered by
running the core backwards, and the physics for that is already in the source
material: **photodisintegration**. Drive a nucleus above its separation
energy and a gamma knocks a nucleon out. At 10⁹ K the photon bath alone
strips nucleons from anything with a separation energy under 3 MeV.

So the core has two gears:

| gear | direction | energy | where it is done |
| --- | --- | --- | --- |
| **capture** | Li → metal | releases (below barium) | where power is scarce and matter is wanted |
| **photodisintegration** | metal → Li | costs the same, exactly | where power is abundant and matter is cheap |

And that symmetry is the trade:

```
   POWER-RICH WORLD                          POWER-POOR WORLD
   (blue star, big collector)                (dim star, big city)

   scrap, ore, slag, wrecks                  wants copper, steel, chips
            │                                          ▲
            │ photodisintegration                      │ capture
            │ −307 PJ/t  (charging)                    │ +307 PJ/t (discharging)
            ▼                                          │
        HEAVY LITHIUM ──────── ship ──────────► HEAVY LITHIUM
        the charged state                        the charged state
```

**Heavy lithium is a battery you can put in a hold.** Hauling it is hauling
energy; the metal that comes out the far end is the flat battery. The round
trip is not free — it never is — but it does something no amount of freight
capacity can: it lets a world that has *sunlight and no ore* trade with a
world that has *ore and no sunlight*, in one cargo, in both directions.

It also collapses the commodity graph. A courier carrying copper has to know
that the destination wants copper. A courier carrying lithium does not have
to know anything, which is exactly why real economies invented money.

---

## 5. The energy economy

Energy becomes the third accounted quantity, after mass and credits. It is
**not a cargo** — it does not ship, except as lithium, which is the point.

### Conversion table

```
    1 solar constant on 1 km² of collector  =  0.1176 PJ/day
    1 MeV/nucleon applied to 1 tonne        =  96.48 PJ
    1 tonne-equivalent of energy (E = mc²)  =  89,876 PJ
```

### Stellar output by class

The map gains an axis it did not have: **what star is this world under.**

| class | L/L☉ | 100 km² farm at 1 AU | what it can afford |
| --- | ---: | ---: | --- |
| M | 0.02 | 0.2 PJ/day | nothing; buys lithium |
| K | 0.3 | 3.5 PJ/day | trickle; carbon at Mk I |
| G | 1.0 | 11.8 PJ/day | a foundry, slowly |
| F | 4 | 47 PJ/day | a working foundry |
| A | 40 | 470 PJ/day | the heavy end, modestly |
| B | 10,000 | **117,590 PJ/day** | gold, platinum, actinides |
| O | 100,000 | 1,175,904 PJ/day | anything, and it will sterilise you |

Worked example — **10 t/day of gold at a Mk II core** costs 3,943 PJ/day:

| star | collector needed |
| --- | ---: |
| G-class | 33,529 km² |
| F-class | 8,382 km² |
| A-class | 838 km² |
| B-class | **3 km²** |

> **Gold is made at blue stars.** Not because anybody wrote that down, but
> because the Coulomb barrier costs 117 PJ a tonne and a B-class star is four
> orders of magnitude brighter than a red dwarf.

This gives us a **second kind of hostile world**, and it pairs beautifully
with the first. The lithium cycle put the fuel under worlds nobody can live
on because the seam is radiologically hot. This puts the heavy-element
industry under worlds nobody can live on because *the star is hot*. Two
uninhabitable classes, two indispensable industries, two different reasons,
and both of them trading zones rather than territory.

---

## 6. The core as a world upgrade

A new building, and — answering the brief directly — it can stand on **any**
body: planet, station, or nebula. The same device behaves differently on
each, and the differences are physical rather than arbitrary.

| | **Planetary core** | **Orbital core** | **Nebula core** |
| --- | --- | --- | --- |
| confinement quality | poor — gravity biases the implosion, Rayleigh–Taylor grows down-gradient | **best** — free-fall, perfect symmetry, vacuum | fair |
| throughput | **highest** — mass for shielding, atmosphere or ocean as heat sink | limited by radiators | limited by diffuse feedstock |
| η penalty / bonus | −0.10 | **+0.12** | +0.04 |
| waste heat | dumped into the biosphere | radiated | absorbed by the cloud, effectively unlimited |
| **side effect** | **raises the world's dose** — a working core makes its own hostile world | none | ambient neutron flux from the cloud aids the neutron road |
| best at | bulk light elements, iron-peak metals | the heavy end, precision nuclides | neutron-road climbs past silver |

The planetary side effect is the one worth keeping. **Run a big enough
planetary core for long enough and the world becomes radiologically
hostile** — which feeds straight back into the lithium siting rule from the
last report, lowers the population ceiling, and eventually licenses the world
to breed fuel. A world can *industrialise itself into* the hot-world
category. That is the kind of consequence this economy is built out of.

---

## 7. Minerals, and the trades they make

Deliberately few new commodities. The core's job is to *collapse* the
commodity graph, not inflate it — thirty elements on a board is a spreadsheet,
not a game.

| new material | tier | made by | wanted by | why it exists |
| --- | --- | --- | --- | --- |
| **Carbon** | refined | core, Mk I+ | thermal piles (moderator), hulls (composite) | the cheapest thing a core can make; a Mk I core's whole output |
| **Platinum** | refined | core, Mk IV+ / mined | chemical works, fabricator | catalyst — ties the heavy end to the chemical and chip chains |
| **Tungsten** | refined | core, Mk IV+ / mined | hot cells, presses, yards | refractory — the lithium line's own plant wears out in it |
| **Actinide** | refined | core, Mk V+ | planetary power, Silo warheads | the far end; only a blue star can afford it |
| **Energy** | *not a material* | stars, reactors, exothermic transmutation | everything above | a per-world budget, never a cargo |

And the core can synthesise **existing** crust and refined materials —
ferrite, cuprite, silicate, copper, silicon, steel — which is the point. It
is a universal, expensive substitute for a mine, sited by starlight rather
than by geology.

### What the trade map looks like afterwards

- **Lithium becomes the trunk route.** Hot worlds breed it; everybody hauls
  it; cores at both ends charge and discharge it. The 4,000-route board from
  the last report collapses toward a few hundred fat lanes, which is a board
  a player can actually read.
- **Star class becomes a reason to go somewhere.** Blue-star systems are
  industrial addresses. Red-dwarf systems are customers.
- **The copper famine ends without a single new road.** A Mk III core on a
  chip world makes its own copper at +29 PJ/t — profitably — and the
  one-jump shuttle rule stops being a death sentence for electronics.
- **Scrap becomes feedstock.** A battle leaves wrecks; a photodisintegration
  core turns wrecks into lithium. The war economy and the fuel economy join
  at the breaker's yard.

---

## 8. What this does to yesterday's measurements

| measured fault | what the core does to it |
| --- | --- |
| chips at 3 % of demand; copper immobile | a Mk III core makes copper in-system, profitably |
| 3 shipyards galaxy-wide, 0 t/d hull plate | yards get steel and chips locally; plate flows; the profitability-driven fleet can finally grow |
| berth pressure 58–107× the commissioning threshold and unable to fire | fires |
| 4,000 live routes, 168 hulls, 2,128 t/d | fewer, fatter, longer lanes carrying one dense cargo |
| fuel cover 1–8 % of appetite | unchanged — and now it matters far more, because lithium is everything |

That last row is the warning. **The core makes the lithium bottleneck the
only bottleneck.** If breeding capacity stays at 2 % of demand, a galaxy full
of transmutation cores is a galaxy full of idle transmutation cores. The map
work (three bodies per system) is still item one; this is item two, and it
does not substitute.

---

## 9. The conservation law gets an upgrade

The existing invariant is that mass is conserved exactly — `Audit` rolls every
pool in the universe into one column and compares the total. The core breaks
it, on purpose, and the fix is the most satisfying part of this design.

`Li → Fe` turns 1,000 kg of lithium into 996.58 kg of iron. The missing 3.42
kg is not lost; it is the 307 PJ. So:

> **MASS–ENERGY IS CONSERVED.** The auditor gains one pool — energy, carried
> in tonnes-equivalent at 89,876 PJ per tonne — and the invariant becomes
> `Σ mass + Σ energy/c² = genesis`. Every existing pool, every test and every
> guarantee survives unchanged, because every existing process has zero
> energy term.

That is a strictly stronger law than the one the economy has now, it is
checkable by the auditor already written, and it means the first process in
the game that converts matter into energy does so **in the books, in tonnes,
where somebody can point at it.**

A useful consequence: because the mass defect is fixed by binding energies
alone and the Coulomb barrier is only *circulated*, the mass ledger does not
depend on η at all. A bad core wastes energy, never mass.

---

## 10. Balance risks, and the guard rails

An element printer is the most dangerous thing anybody has proposed adding to
this economy. Five rails, each of which is physics rather than a dial:

1. **The barium line.** Nothing past Z = 56 ever pays. Gold, platinum,
   tungsten and the actinides are permanent energy sinks at any η ≤ 1.
2. **Efficiency gates the chart.** Mk I reaches carbon; Mk III reaches copper;
   Mk V stops at silver. The tech tree is the break-even table.
3. **Waiting points gate throughput.** Beta decay is the slow step and no
   amount of power shortens it.
4. **Drip lines gate overdrive.** Push harder than the confinement is round
   and the product dismantles itself.
5. **Stars gate everything.** A red-dwarf world with a Mk V core and no
   lithium is a monument.

And one economic rail: the core consumes **heavy lithium**, which is made at
the 14–22 % of worlds that are radiologically hostile, at 2 % of demand. The
printer is fed by the tightest supply line in the game.

---

## 11. Implementation plan

| slice | package | what |
| --- | --- | --- |
| **T1** | `econ` | `Joules` as a tonnes-equivalent pool; `Audit` becomes mass–energy. No behaviour change: every existing process has a zero energy term, so all current tests must pass untouched. |
| **T2** | `econ/nuclide.go` | The chart: Z, A, BE/A and the Coulomb term for ~30 nuclides. `Yield(from,to)`, `Barrier(from,to)`, `Net(from,to,η)`. Pure data + two functions; unit-testable against the tables in §1. |
| **T3** | `universe` | `World.Star` (class + band) → `Insolation`; `Collector` building; a daily energy budget with sources and sinks. |
| **T4** | `universe/transmute.go` | `Core` building at three grades; capture and photodisintegration; waiting-point throughput caps; the planetary dose side-effect. |
| **T5** | `industry` | Carbon, Platinum, Tungsten, Actinide; the core as a `Module` so it composes like every other plant. |
| **T6** | `universe/routes.go` | Teach the router that lithium substitutes for anything a core can make — the "haul the battery, not the cargo" rule. |
| **T7** | rig | Extend `TestGazetteer` with energy and transmutation columns; re-measure the chips famine. |

The natural order is T1–T2 first and alone: the nuclide chart and the
mass–energy auditor are both pure, both testable against published values,
and both are the foundation everything else stands on. T3 needs star classes,
which the gazetteer does not currently carry — that is a data question to
settle before writing code.

---

## 12. Open questions

1. **Star classes.** The recovered gazetteer has no stellar data. Invent it
   from the seed (like `Dose`), or extract it from the 1997 plugin if the
   `sÿst` records carry anything usable?
2. **Does energy ship at all?** The clean answer is no — lithium is the
   carrier. But a "charged capacitor bank" cargo would be a second, faster,
   lossier option, and it might be worth the complexity.
3. **Does the player get a core?** A shipboard breeder already transmutes.
   A shipboard *core* would make the player a mobile foundry, which is either
   the best item in the game or the end of the trade loop.
4. **How visible is the chart?** The nuclide chart is a genuinely beautiful
   screen and a genuinely intimidating one. A route planner that shows the
   path from lithium to your target, with its waiting points and its drip-line
   margins, might be the best UI in the game — or it might be the one nobody
   opens.
5. **Ordering against the map work.** This report and the last one both
   converge on the same bottleneck from opposite sides. Three bodies per
   system is still first; whether the core comes before or after the
   commodity screen is a question about what the player is asked to
   understand, and in what order.

---

*Lithium is the trough at the bottom of the binding-energy curve, and that is
why it is fuel, why it is cargo, why it is currency, and why the worlds that
make it are uninhabitable. Everything else in the periodic table is downhill
from it — right up to barium, where the universe starts charging.*
