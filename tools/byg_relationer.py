#!/usr/bin/env python3
"""
Bygger relationer.json fra råtabellen og validerer konsistens.
Regel: A.haenger_sammen_med(B) ⇔ B.haenger_sammen_med(A)
       A.lever_ogsaa_i(B) ⇔ B.lever_ogsaa_i(A)
Typer: begreb, zone, kvalitet, stadie, oevelse
"""
import json
from collections import defaultdict

# Type-lookup for alle entries
TYPE = {}

# Alle 18 begreber
for b in [
    "dynamisk-stilhed", "breath-of-life", "primary-respiration", "midtlinjen",
    "the-health", "motion-present", "fulcrum", "stillpoints", "transmutation",
    "the-neutral", "automatic-shifting", "den-iboende-behandlingsplan",
    "fluid-body", "the-lesion-field", "potency", "ignition",
    "axial-fluctuations", "wholeness"
]:
    TYPE[b] = "begreb"

# 5 zoner
for z in ["a-fysisk-krop", "b-vaeskekrop", "c-relationelle-felt",
          "d-primary-respiration", "e-dynamisk-stilhed"]:
    TYPE[z] = "zone"

# 8 kvaliteter
for k in ["k1-neutral-lytten", "k2-selvregulering", "k3-sansning",
          "k4-taalmodighed-uvished", "k5-helhedens-prioritering",
          "k6-synkron-bevaegelse", "k7-beroering", "k8-rytme"]:
    TYPE[k] = "kvalitet"

# 5 stadier
for s in ["s1-foerste-stadie", "s2-andet-stadie", "s3-tredje-stadie",
          "s4-fjerde-stadie", "s5-femte-stadie"]:
    TYPE[s] = "stadie"

# 4 øvelser (kommer med A2 for fuldstændighed af 'lever_ogsaa_i' refs)
for o in ["o1-the-neutral", "o2-kroppens-egen-viden",
          "o3-kroppens-dynamiske-landskaber", "o4-vejrtraekningen"]:
    TYPE[o] = "oevelse"

# ----------------------------------------------------------------------------
# DATA: Samme-type-relationer (haenger_sammen_med)
# Format: (A, B, beskrivelse-fra-A-til-B, beskrivelse-fra-B-til-A)
# Scriptet sætter automatisk A→B og B→A (symmetrisk regel)
# ----------------------------------------------------------------------------
samme_type = [
    # BEGREB ↔ BEGREB
    ("dynamisk-stilhed", "breath-of-life",
     "Breath of Life er første manifestation fra stilheden",
     "udspringer fra Dynamisk Stilhed som første udtryk"),
    ("dynamisk-stilhed", "midtlinjen",
     "midtlinjens essens er dynamisk stilhed",
     "dynamisk stilhed er midtlinjens essens"),
    ("dynamisk-stilhed", "primary-respiration",
     "Primary Respiration er stilhedens åndedræt",
     "nedkog af Breath of Life som udspringer fra stilheden"),

    ("breath-of-life", "primary-respiration",
     "Primary Respiration er nedkog af Breath of Life's energi",
     "bærer livskraften fra stilheden ud i biologisk rytme"),
    ("breath-of-life", "midtlinjen",
     "Breath of Life strækker sig fra midtlinjen til horisonten",
     "hav af Breath of Life mellem midtlinje og horisont"),
    ("breath-of-life", "the-neutral",
     "Breath of Life kommer ind gennem The Neutral",
     "porten hvor Breath of Life kan arbejde optimalt"),
    ("breath-of-life", "transmutation",
     "Breath of Life gennem The Neutral skaber transmutation",
     "den alkymistiske ild der forvandler selve vævets natur"),

    ("primary-respiration", "midtlinjen",
     "The Long Tide bevæger sig fra horisonten mod midtlinjen",
     "midtlinjen er hvor Long Tide rammer og skaber Fluid Tide"),
    ("primary-respiration", "fluid-body",
     "Fluid Tide manifesterer sig gennem væskekroppen",
     "bærer Primary Respiration's rytme som 2-3 cyklusser/min"),
    ("primary-respiration", "the-neutral",
     "ved The Neutral kan Primary Respiration re-mønstrere",
     "forudsætning for at Primary Respiration arbejder uhindret"),

    ("midtlinjen", "fulcrum",
     "hele midtlinjen fungerer som ét enkelt fulcrum",
     "midtlinjen er det ultimative omdrejningspunkt"),
    ("midtlinjen", "stillpoints",
     "embryologiske fulcrums langs midtlinjen bliver stillepunkter",
     "stillepunkter opstår langs midtlinjens akse"),
    ("midtlinjen", "ignition",
     "ilden tændes gennem stilhedens enkle dør i midtlinjen",
     "antændelsen af Primary Respiration sker gennem midtlinjen"),
    ("midtlinjen", "axial-fluctuations",
     "fluktuationer sker langs midtlinjens akse",
     "bølger fra coccyx til sphenoid følger midtlinjen"),

    ("the-health", "wholeness",
     "sundhed i delen er aspekt af sundhed i helheden",
     "helhedens integritet manifesterer sig som Sundheden"),
    ("the-health", "den-iboende-behandlingsplan",
     "Sundhedens skabelon er behandlingens skabelon",
     "behandlingsplanen arbejder fra Sundhedens perspektiv"),
    ("the-health", "the-lesion-field",
     "selv inden i det låste læsionsfelt findes Sundheden",
     "Sundheden kan ikke mistes selv i læsionsfeltet"),
    ("the-health", "potency",
     "potency arbejder i relation til Sundhedens skabelon",
     "livskraften der realiserer Sundhedens potentiale"),

    ("motion-present", "fulcrum",
     "al bevægelse sker i relation til et fulcrum",
     "fulcrum er omdrejningspunkt for Motion Present"),
    ("motion-present", "the-lesion-field",
     "Motion Present findes selv i det mest dysfunktionelle felt",
     "bærer altid Motion Present selv når mest isoleret"),
    ("motion-present", "wholeness",
     "arbejder altid i forhold til helheden",
     "helheden prioriterer gennem Motion Present"),
    ("motion-present", "primary-respiration",
     "Primary Respiration er del af Motion Present",
     "den dybeste lag af Motion Present"),

    ("fulcrum", "stillpoints",
     "fulcrums i væsken bliver til stillepunkter",
     "stillepunkter er kraftens punkter fra fulcrums"),
    ("fulcrum", "the-lesion-field",
     "læsion = opsplitning i tre forskellige fulcrums",
     "falske fulcrums opstår i læsionsfeltet"),

    ("stillpoints", "transmutation",
     "stillepunktet er hvor transformation sker",
     "den alkymistiske forvandling finder sted i stillepunktet"),
    ("stillpoints", "primary-respiration",
     "Primary Respiration er intenst mærkbar i stillepunktet",
     "stillepunkter augmenterer Primary Respiration"),

    ("transmutation", "ignition",
     "Ignition er den alkymistiske ild der transmuterer alt",
     "antændelsen udløser transmutation"),
    ("transmutation", "the-lesion-field",
     "transmutation sker I dysfunktionelle zoner",
     "den alkymistiske ild aktiveres hvor heling behøves"),
    ("transmutation", "the-neutral",
     "transmutation sker når Breath of Life kommer gennem The Neutral",
     "porten hvor alkymien kan ske"),

    ("the-neutral", "den-iboende-behandlingsplan",
     "The Neutral er porten hvor behandlingsplanen overtager",
     "overtager styringen når The Neutral indfinder sig"),
    ("the-neutral", "automatic-shifting",
     "Automatic Shifting opstår i direkte forlængelse af The Neutral",
     "forudsætningen for at shifting kan ske"),
    ("the-neutral", "the-lesion-field",
     "læsionsfeltet vil ikke gå til neutral",
     "det væsentlige kendetegn er fraværet af The Neutral"),
    ("the-neutral", "potency",
     "potency arbejder gennem The Neutral med mindst modstand",
     "hvor livskraften kan frigives optimalt"),
    ("the-neutral", "fluid-body",
     "væv, væske og energi bliver én homogen substans",
     "væskekroppen er central i The Neutral-tilstanden"),

    ("automatic-shifting", "den-iboende-behandlingsplan",
     "orkestreres af den iboende behandlingsplan",
     "behandlingsplanen styrer shifting-sekvensen"),
    ("automatic-shifting", "wholeness",
     "orkestreret af helhedens prioritering",
     "helhedens intelligens i action"),

    ("den-iboende-behandlingsplan", "wholeness",
     "prioriterer efter helhedens behov",
     "helheden udtrykker sig som behandlingsplanen"),

    ("fluid-body", "ignition",
     "hele væskekroppen simultant antændes ved ignition",
     "antændelsen sker gennem hele væskekroppen simultant"),
    ("fluid-body", "axial-fluctuations",
     "aksiale fluktuationer er væskekroppens bevægelser",
     "væskekroppens bevægelser langs midtlinjen"),
    ("fluid-body", "potency",
     "potency flyder gennem væskekroppen",
     "væskekroppen er mediet for potency"),

    ("the-lesion-field", "potency",
     "potency bindes i læsionsfeltet",
     "bundet potency som sammenpresset fjeder"),
    ("the-lesion-field", "wholeness",
     "har mistet forbindelsen til helheden",
     "når læsionsfeltet genforbinder, genvindes helheden"),

    ("ignition", "primary-respiration",
     "antændelsen af Primary Respiration gennem midtlinjen",
     "PR tændes gennem ignition-øjeblikket"),
    ("ignition", "fluid-body",
     "hele væskekroppen simultant antændes",
     "antændelsen sker gennem hele væskekroppen"),
    ("ignition", "dynamisk-stilhed",
     "tændes gennem stilhedens enkle dør",
     "ilden tændes fra stilheden"),

    # ZONE ↔ ZONE (naboer)
    ("a-fysisk-krop", "b-vaeskekrop", "nabozone, overgang til væskekroppen", "nabozone, Zone A's dybere lag"),
    ("b-vaeskekrop", "c-relationelle-felt", "åbner mod det relationelle felt", "forudsætter væskekroppens åbning"),
    ("c-relationelle-felt", "d-primary-respiration", "det fælles felt udvides til det universelle", "Zone C båret af The Long Tide"),
    ("d-primary-respiration", "e-dynamisk-stilhed", "porten til Dynamisk Stilhed", "manifesterer sig gennem Zone D's Long Tide"),

    # KVALITET ↔ KVALITET
    ("k1-neutral-lytten", "k3-sansning",
     "lytter og sanser går tæt sammen", "sansning bygger på neutral lytten"),
    ("k1-neutral-lytten", "k7-beroering",
     "neutral berøring som aktiv tilstedeværelse uden agenda", "berøringens neutralitet spejler lytningens"),
    ("k1-neutral-lytten", "k4-taalmodighed-uvished",
     "not-knowing kræver tålmodighed", "tålmodigheden åbner for not-knowing"),

    ("k2-selvregulering", "k1-neutral-lytten",
     "uden forankring kan man ikke lytte neutralt", "neutral lytten kræver selvreguleret tilstand"),
    ("k2-selvregulering", "k6-synkron-bevaegelse",
     "kræver egen ro for at følge synkront", "synkronisering bygger på egen stabilitet"),

    ("k3-sansning", "k5-helhedens-prioritering",
     "sansning mærker hvor helheden kalder", "at mærke helheden kræver finstemt sansning"),
    ("k3-sansning", "k8-rytme",
     "sansning af mætning", "rytme mærkes gennem sansning"),

    ("k4-taalmodighed-uvished", "k5-helhedens-prioritering",
     "tålmodighed til at stole på at helheden ved", "helhedens vej kræver uvished og tålmod"),
    ("k4-taalmodighed-uvished", "k6-synkron-bevaegelse",
     "følge uden at dirigere", "synkron bevægelse kræver tålmodighed"),

    ("k6-synkron-bevaegelse", "k7-beroering",
     "kvalitet i kontakten hænger sammen med bevægelse", "berøringen bærer den synkrone bevægelse"),

    ("k5-helhedens-prioritering", "k8-rytme",
     "respektere hvad helheden tillader", "rytmen følger helhedens prioritet"),

    # STADIE ↔ STADIE (fuld forbundet — bogen har 4 explicit-forbindelser per stadie)
    ("s1-foerste-stadie", "s2-andet-stadie",
     "overgang gennem udmattelse af forstå-viljen",
     "bærer stadig spor af første stadies uro"),
    ("s1-foerste-stadie", "s3-tredje-stadie",
     "rationalitet kan ikke nå det relationelle",
     "første stadies isolation udfordres af relationelle virkelighed"),
    ("s1-foerste-stadie", "s4-fjerde-stadie",
     "længste rejse, Sundheden arbejder fra begyndelsen",
     "første stadies søgen har forberedt overgivelsen"),
    ("s1-foerste-stadie", "s5-femte-stadie",
     "genbesøges altid — spiralens natur",
     "dybeste afstand + mest intime forbindelse"),

    ("s2-andet-stadie", "s3-tredje-stadie",
     "væskekroppens balancepunkter = dørtærskel til relationelle",
     "det relationelle udvider andet stadies pauser"),
    ("s2-andet-stadie", "s4-fjerde-stadie",
     "REM-tilstande varsler dybere bevidsthedstilstande",
     "pauserne indeholder nu gammelt sprog"),
    ("s2-andet-stadie", "s5-femte-stadie",
     "transformationens arbejdsværelse",
     "pausernes kvalitet udviklet til Dynamisk Stilhed"),

    ("s3-tredje-stadie", "s4-fjerde-stadie",
     "gennem nære lærer vi at åbne for det universelle",
     "co-regulering transcenderer det personlige"),
    ("s3-tredje-stadie", "s5-femte-stadie",
     "fælles felter forbereder mødet med enhed",
     "relationelle ekspanderet til universel forbindelse"),

    ("s4-fjerde-stadie", "s5-femte-stadie",
     "Long Tide fører naturligt til Dynamisk Stilhed",
     "at blive bevæget → at blive skabt"),
]

# ----------------------------------------------------------------------------
# DATA: Krydstype-relationer (lever_ogsaa_i)
# Format: (A, B, beskrivelse-fra-A-til-B, beskrivelse-fra-B-til-A)
# A og B er af FORSKELLIG type — scriptet tjekker det
# ----------------------------------------------------------------------------
kryds_type = [
    # BEGREB ↔ ZONE
    ("dynamisk-stilhed", "e-dynamisk-stilhed",
     "Zone E er mødet med Dynamisk Stilhed",
     "Zone E bærer dens navn og essens"),
    ("breath-of-life", "e-dynamisk-stilhed",
     "viser sig i Zone E som første manifestation",
     "Breath of Life åbenbares her som ilden fra stilheden"),
    ("breath-of-life", "d-primary-respiration",
     "The Long Tide er Breath of Life's første udtryk",
     "Zone D bærer Breath of Life's kaleidoskopiske energi"),
    ("primary-respiration", "d-primary-respiration",
     "Zone D ER Primary Respiration / The Long Tide",
     "selve zonen ER Primary Respiration"),
    ("primary-respiration", "b-vaeskekrop",
     "Fluid Tide manifesterer sig gennem væskekroppen",
     "Zone B ånder under Primary Respiration"),
    ("primary-respiration", "c-relationelle-felt",
     "Primary Respiration skaber fælles felt mellem to mennesker",
     "Zone C er hvor PR bliver fælles"),
    ("midtlinjen", "a-fysisk-krop",
     "midtlinjen som naturligt fulcrum i Zone A",
     "Zone A's strukturelle integritet hviler på midtlinjen"),
    ("midtlinjen", "b-vaeskekrop",
     "oprindelig midtlinje som stabilt fulcrum i væsken",
     "Zone B bærer den oprindelige midtlinje som anker"),
    ("midtlinjen", "d-primary-respiration",
     "Long Tide bevæger sig mod midtlinjen",
     "Zone D's bevægelse ender i midtlinjen"),
    ("midtlinjen", "e-dynamisk-stilhed",
     "midtlinjens essens er dynamisk stilhed",
     "midtlinjens inderste er Zone E's stilhed"),
    ("fulcrum", "a-fysisk-krop",
     "midtlinjen som naturligt fulcrum i Zone A",
     "Zone A's fulcrums er strukturelle ankerpunkter"),
    ("fulcrum", "b-vaeskekrop",
     "normale og falske fulcrums i væsken",
     "Zone B rummer både naturlige og dysfunktionelle fulcrums"),
    ("fluid-body", "b-vaeskekrop",
     "Zone B ER væskekroppen",
     "selve zonen ER væskekroppen"),
    ("the-neutral", "b-vaeskekrop",
     "kapaciteten til The Neutral lever her",
     "Zone B er hvor The Neutral oftest indfinder sig"),
    ("automatic-shifting", "b-vaeskekrop",
     "naturlig mulighed i Zone B",
     "Zone B er hvor shifting kan udfolde sig"),
    ("the-lesion-field", "a-fysisk-krop",
     "læsionsfelter findes i Zone A",
     "Zone A rummer de konkrete læsionsfelter"),
    ("motion-present", "a-fysisk-krop",
     "fysisk bevægelse er Motion Presents grundlag",
     "Zone A er hvor Motion Present først mærkes"),
    ("transmutation", "e-dynamisk-stilhed",
     "øjeblikkelig transmutation i Zone E",
     "Zone E er hvor transmutation kan ske med ét"),

    # BEGREB ↔ KVALITET
    ("the-neutral", "k1-neutral-lytten",
     "neutral lytten afspejler The Neutral som kvalitet",
     "lytter fra den neutrale tilstand"),
    ("the-neutral", "k3-sansning",
     "sanse The Neutrals forskellige dybder",
     "dybdekendskab til The Neutral"),
    ("the-neutral", "k7-beroering",
     "neutral berøring uden agenda",
     "berøringens neutralitet er aktiv tilstedeværelse"),
    ("motion-present", "k1-neutral-lytten",
     "lytter til det nu-tilstedeværende",
     "at høre hvad der allerede bevæger sig"),
    ("motion-present", "k3-sansning",
     "finde Motion Present selv i dysfunktionelt felt",
     "sansningens mål er den altid-tilstedeværende bevægelse"),
    ("motion-present", "k5-helhedens-prioritering",
     "helheden prioriterer gennem hvor Motion Present kalder",
     "at finde hvor kroppen inviterer"),
    ("motion-present", "k6-synkron-bevaegelse",
     "synkronisere med kroppens bevægelse",
     "at blive ét med den tilstedeværende bevægelse"),
    ("midtlinjen", "k2-selvregulering",
     "finde egen midtlinje som forberedelse",
     "selvreguleringens anker"),
    ("primary-respiration", "k2-selvregulering",
     "finde egen Primary Respiration",
     "synkronisering med egen PR som grundlag"),
    ("primary-respiration", "k6-synkron-bevaegelse",
     "matche Primary Respirations rytme",
     "den ultimative synkronisering"),
    ("primary-respiration", "k8-rytme",
     "følge Primary Respirations rytme",
     "rytmens kildelag"),
    ("the-lesion-field", "k3-sansning",
     "finde Sundheden selv i det låste læsionsfelt",
     "sansningens mod i dysfunktionelle felter"),
    ("the-health", "k3-sansning",
     "skelne ægte healing fra kompensation",
     "at mærke Sundheden som reference"),
    ("wholeness", "k5-helhedens-prioritering",
     "arbejde med helheden frem for imod",
     "helhedens stemme i behandlerens sansning"),
    ("den-iboende-behandlingsplan", "k4-taalmodighed-uvished",
     "stole på processen uden at forstå den",
     "uvisheden åbner for behandlingsplanen"),
    ("den-iboende-behandlingsplan", "k5-helhedens-prioritering",
     "behandlingsplanen kender helhedens vej",
     "at mærke hvor behandlingsplanen kalder"),
    ("automatic-shifting", "k4-taalmodighed-uvished",
     "kroppen prioriterer selv — tålmodighed kræves",
     "at slippe kontrol og tillade shifting"),
    ("automatic-shifting", "k5-helhedens-prioritering",
     "helhedens prioritering i action",
     "at følge shiftings intelligens"),

    # BEGREB ↔ STADIE
    ("fluid-body", "s2-andet-stadie",
     "væskekroppen vågner i andet stadie",
     "andet stadies kernefænomen er væskekroppens vågnen"),
    ("primary-respiration", "s3-tredje-stadie",
     "PR skaber fælles felt i det relationelle stadie",
     "tredje stadies opdagelse af PR mellem mennesker"),
    ("primary-respiration", "s4-fjerde-stadie",
     "The Long Tide overtager i fjerde stadie",
     "fjerde stadie ER mødet med The Long Tide"),
    ("breath-of-life", "s4-fjerde-stadie",
     "The Long Tide som Breath of Life's udtryk",
     "fjerde stadies kontakt med Breath of Life gennem Long Tide"),
    ("breath-of-life", "s5-femte-stadie",
     "første manifestation fra stilheden",
     "femte stadies oplevelse af Breath of Life som ilden"),
    ("dynamisk-stilhed", "s5-femte-stadie",
     "femte stadie ER mødet med Dynamisk Stilhed",
     "stadiet bærer Dynamisk Stilhed som essens"),
    ("transmutation", "s5-femte-stadie",
     "den ultimative transformation i femte stadie",
     "femte stadies transsubstantiation"),

    # ZONE ↔ STADIE (direkte parallel i bogens struktur)
    ("b-vaeskekrop", "s2-andet-stadie",
     "andet stadies væskekrop-vågnen svarer til Zone B",
     "Zone B som stadie-parallel"),
    ("c-relationelle-felt", "s3-tredje-stadie",
     "tredje stadie svarer til Zone C's relationelle felt",
     "Zone C som stadie-parallel"),
    ("d-primary-respiration", "s4-fjerde-stadie",
     "fjerde stadie svarer til Zone D's Long Tide",
     "Zone D som stadie-parallel"),
    ("e-dynamisk-stilhed", "s5-femte-stadie",
     "femte stadie svarer til Zone E's Dynamisk Stilhed",
     "Zone E som stadie-parallel"),

    # KVALITET ↔ ZONE
    ("k2-selvregulering", "c-relationelle-felt",
     "co-regulering med klient foregår i Zone C",
     "Zone C er hvor selvregulering møder klientens"),

    # BEGREB ↔ ØVELSE (kun de A2 har brug for — øvelser er "lever_ogsaa_i")
    ("fulcrum", "o3-kroppens-dynamiske-landskaber",
     "øvelsen handler om fulcrums i egen krop",
     "øvelsen udforsker fulcrums direkte"),
    ("stillpoints", "o3-kroppens-dynamiske-landskaber",
     "øvelsen indeholder stillepunkter",
     "øvelsen udforsker stillepunkter direkte"),
    ("automatic-shifting", "o3-kroppens-dynamiske-landskaber",
     "øvelsen indeholder automatic shifting",
     "øvelsen udforsker shifting direkte"),
    ("the-neutral", "o1-the-neutral",
     "øvelsen er direkte om The Neutral",
     "øvelsen udforsker The Neutral direkte"),
]

# ----------------------------------------------------------------------------
# BYG JSON
# ----------------------------------------------------------------------------
relationer = {id_: {"haenger_sammen_med": [], "lever_ogsaa_i": []}
              for id_ in TYPE}

errors = []

def add_same_type(a, b, desc_ab, desc_ba):
    """A og B skal have samme type. Tilføj begge veje."""
    if TYPE[a] != TYPE[b]:
        errors.append(f"SAMME-TYPE-FEJL: {a} ({TYPE[a]}) og {b} ({TYPE[b]}) har forskellig type")
        return
    relationer[a]["haenger_sammen_med"].append({
        "id": b, "type": TYPE[b], "kort_beskrivelse": desc_ab
    })
    relationer[b]["haenger_sammen_med"].append({
        "id": a, "type": TYPE[a], "kort_beskrivelse": desc_ba
    })

def add_kryds(a, b, desc_ab, desc_ba):
    """A og B skal have forskellig type. Tilføj begge veje."""
    if TYPE[a] == TYPE[b]:
        errors.append(f"KRYDS-FEJL: {a} og {b} har samme type ({TYPE[a]})")
        return
    relationer[a]["lever_ogsaa_i"].append({
        "id": b, "type": TYPE[b], "kort_beskrivelse": desc_ab
    })
    relationer[b]["lever_ogsaa_i"].append({
        "id": a, "type": TYPE[a], "kort_beskrivelse": desc_ba
    })

# Tilføj alle relationer
for a, b, d1, d2 in samme_type:
    if a not in TYPE:
        errors.append(f"UKENDT ID: {a}")
        continue
    if b not in TYPE:
        errors.append(f"UKENDT ID: {b}")
        continue
    add_same_type(a, b, d1, d2)

for a, b, d1, d2 in kryds_type:
    if a not in TYPE:
        errors.append(f"UKENDT ID: {a}")
        continue
    if b not in TYPE:
        errors.append(f"UKENDT ID: {b}")
        continue
    add_kryds(a, b, d1, d2)

# ----------------------------------------------------------------------------
# VALIDATION — tjek at alt er symmetrisk (burde være automatisk OK)
# ----------------------------------------------------------------------------
def check_symmetry():
    for id_a, data in relationer.items():
        for ref in data["haenger_sammen_med"]:
            id_b = ref["id"]
            back_refs = [r["id"] for r in relationer[id_b]["haenger_sammen_med"]]
            if id_a not in back_refs:
                errors.append(f"ASYMMETRI haenger_sammen_med: {id_a} → {id_b} men ikke omvendt")
        for ref in data["lever_ogsaa_i"]:
            id_b = ref["id"]
            back_refs = [r["id"] for r in relationer[id_b]["lever_ogsaa_i"]]
            if id_a not in back_refs:
                errors.append(f"ASYMMETRI lever_ogsaa_i: {id_a} → {id_b} men ikke omvendt")

check_symmetry()

# ----------------------------------------------------------------------------
# RAPPORT
# ----------------------------------------------------------------------------
print("=" * 70)
print(f"RELATIONER.JSON BYGGET")
print("=" * 70)
print(f"Antal entries: {len(relationer)}")
print(f"  - Begreber: {sum(1 for t in TYPE.values() if t=='begreb')}")
print(f"  - Zoner: {sum(1 for t in TYPE.values() if t=='zone')}")
print(f"  - Kvaliteter: {sum(1 for t in TYPE.values() if t=='kvalitet')}")
print(f"  - Stadier: {sum(1 for t in TYPE.values() if t=='stadie')}")
print(f"  - Øvelser: {sum(1 for t in TYPE.values() if t=='oevelse')}")
print()
print(f"Antal samme-type-relationer: {len(samme_type)} (bliver til {len(samme_type)*2} refs begge veje)")
print(f"Antal kryds-type-relationer: {len(kryds_type)} (bliver til {len(kryds_type)*2} refs begge veje)")
print()

# Entries uden relationer (sanity check)
empty = [k for k, v in relationer.items()
         if not v["haenger_sammen_med"] and not v["lever_ogsaa_i"]]
if empty:
    print(f"OBS — {len(empty)} entries uden relationer (forventet for rene øvelses-referencer):")
    for e in empty:
        print(f"  - {e} ({TYPE[e]})")
    print()

if errors:
    print(f"❌ {len(errors)} FEJL:")
    for e in errors:
        print(f"  - {e}")
else:
    print("✅ Ingen fejl. Alle referencer går begge veje.")
print()

# Per-entry count
print("Antal referencer per entry:")
for id_, data in sorted(relationer.items()):
    n1 = len(data["haenger_sammen_med"])
    n2 = len(data["lever_ogsaa_i"])
    print(f"  {id_:35s} {TYPE[id_]:10s} samme:{n1:2d}  kryds:{n2:2d}")

# Skriv JSON
with open("/home/claude/relationer.json", "w", encoding="utf-8") as f:
    json.dump(relationer, f, ensure_ascii=False, indent=2)

print()
print(f"✅ Skrevet til /home/claude/relationer.json")
