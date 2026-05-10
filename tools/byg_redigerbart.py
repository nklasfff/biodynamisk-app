#!/usr/bin/env python3
"""
byg_redigerbart.py — Generér ét samlet redigerbart Word-udkast med ALT
indhold fra bogen i klartekst-format. Round-trip: brugeren redigerer
direkte i Word, sender filen retur, og ændringer kan applikeres tilbage
til kildematerialet (content/*.md, hero-motiver/*.svg, mikrotekster.json,
byg_bog.py-konstanter).

Output:
  tools/output/manuskript-redigerbar.docx

Brug:
  python3 tools/byg_redigerbart.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).resolve().parent))
from byg_bog import (
    ROOT, CONTENT, OUT,
    DELE, CHAPTER_HERO, SAMLING_HERO, SUBSECTION_HERO,
    PERSPEKTIVER_FIGURER, EGENSKABER_FIGURER,
    RUM_HERO_FIGURER, HELHED_HERO_FIGURER, OEVELSE_HERO_FIGURER,
    EGENSKAB_SUBTITLES, SPECIELLE_TEMAER_SUBTITLES,
    KATEGORI_ORDEN,
    hent_mikrotekster, laes_md, strip_relationer, strip_html_illustrations,
    _kapitel_kategori_indeks, _vaelg_invitation_for_kapitel,
)


# ============================================================================
# ILLUSTRATIONS-INVENTAR
# ============================================================================
#
# For hver hero-illustration: en strukturet beskrivelse af tekstindholdet
# brugeren kan redigere. Ekstraheres delvist fra Python-konstanter,
# delvist fra SVG'erne.
# ============================================================================

# Manuelt opretholdt kontekst-information for de største illustrationer
# (positions-labels for koncentriske/venn/konstellations-layouts).
KAPITEL_HERO_TEKSTER = {
    "den-biodynamiske-model-figur.svg": [
        ("Type", "5 koncentriske ovaler omkring en mørk kerne"),
        ("Ydre oval (lysest)", "De Embryologiske Kræfter / iboende intelligens fra foster til heling"),
        ("Næstydre oval", "Kroppen som Ubrudt Helhed / et integreret kontinuum fra første celle"),
        ("Midt", "Den Kontinuerlige Tilblivelse / uafbrudt flyden-til — aldrig statisk"),
        ("Næstinder", "Enhedens Paradoks / The Neutral — fri til alle retninger"),
        ("Inder", "Felters Dynamik og Grænser / grænseflader som indgange til nyt"),
        ("Center (mørkest)", "DEN BIODYNAMISKE MODEL / når livets kræfter mødes"),
    ],
    "embryologi-figur.svg": [
        ("Type", "Konstellation: 9 cirkler omkring centrum"),
        ("Center", "Embryologi"),
        ("Bevægelse", "Bevægelse / skaber form"),
        ("Væskedynamik", "Væske- / dynamik"),
        ("Metaboliske felter", "Metaboliske / felter"),
        ("Ekstragenetisk", "Ekstragenetisk / information"),
        ("Selvreferentiel", "Selvreferentiel / kapacitet"),
        ("Cellen", "Cellen som / bevægelse"),
        ("Periferi", "Periferi / til centrum"),
        ("Rytmer", "Rytmer af / aktivitet og hvile"),
        ("Kræfter", "Kræfter / livet igennem"),
    ],
    "begreber-figur.svg": [
        ("Type", "Konstellation: 18 cirkler — én pr. begreb"),
        ("Note", "Hvert begrebs-glyf har egen titel + tagline; redigeres pr. begreb under selve begreb-afsnittet."),
    ],
    "i-behandlingssituationen-figur.svg": [
        ("Type", "Behandlerens proces / klient-rejse"),
    ],
    "helheden-under-pres-figur.svg": [
        ("Type", "Fire forskydnings-stadier"),
        ("Stadie 1", "Helheden lever"),
        ("Stadie 2", "Første forskydning"),
        ("Stadie 3", "Ubalancen breder sig"),
        ("Stadie 4", "Det kroniske mønster"),
    ],
    "ordliste-figur.svg": [
        ("Type", "Konstellation: 7 kategorier omkring 'Vendinger & Betydninger'"),
        ("Center", "Vendinger & Betydninger"),
        ("Top", "De 18 / Biodynamiske / Begreber"),
        ("Top-højre", "Termer fra / Andre / Traditioner"),
        ("Højre", "Embryologiske / Termer"),
        ("Bund-højre", "Nervesystem / og Regulering"),
        ("Bund-venstre", "Rytmer og / Bevægelser"),
        ("Venstre", "Terapeutiske / Processer"),
        ("Top-venstre", "Behandlings- / termer"),
    ],
    "otte-egenskaber-figur.svg": [
        ("Type", "Konstellation: 8 essentielle egenskaber omkring centrum"),
        ("Note", "Hver egenskab har titel + 2-linjers cirkel-tekst — listet pr. egenskab nedenfor (kapitel 6)."),
    ],
    "de-fem-rum-figur.svg": [
        ("Type", "Venn diagram med 5 overlappende cirkler"),
        ("Cirkel 1 (top)", "Den fysiske krop / Form bliver til flow"),
        ("Cirkel 2 (top-højre)", "Væskekroppen / Flowet forbinder felter"),
        ("Cirkel 3 (bund-højre)", "Det relationelle felt / Mødet med den dybere rytme"),
        ("Cirkel 4 (bund-venstre)", "Primary Respiration / Rytmen hviler i kilden"),
        ("Cirkel 5 (venstre)", "Dynamisk Stilhed / Kilden bliver til form"),
        ("Center", "De 5 Rum"),
    ],
    "klientmoenstre-figur.svg": [
        ("Type", "9 cirkler — én pr. klient-mønster"),
    ],
    "behandlerens-indre-rejse-figur.svg": [
        ("Type", "Konstellation: 5 stadier omkring 'Den biodynamiske model'"),
        ("Center", "Den biodynamiske model"),
        ("A.T. Still", "A.T. / Still"),
        ("William G. Sutherland", "William G. / Sutherland"),
        ("Rollin E. Becker", "Rollin E. / Becker"),
        ("James Jealous", "James / Jealous"),
        ("Alle os", "Alle / os"),
    ],
    "de-syv-perspektiver-figur.svg": [
        ("Type", "Konstellation: 7 perspektiver"),
        ("Note", "Hvert perspektiv har titel + 2-linjers cirkeltekst — listet pr. perspektiv nedenfor (kapitel 10)."),
    ],
    "de-fire-oevelser-figur.svg": [
        ("Type", "Venn med 4 overlappende cirkler"),
        ("Top", "At Opleve The Neutral / Lytten der vækker indre viden"),
        ("Højre", "Kroppens Egen Viden / Indsigt møder åndedrættet"),
        ("Bund", "Vejrtrækningen Som En Levende Proces / Åndedrættet bevæger landskabet"),
        ("Venstre", "Kroppens Dynamiske Landskaber / Bevægelsen finder hvile"),
        ("Center", "De 4 Guidede Øvelser"),
    ],
    "traditioner-figur.svg": [
        ("Type", "Konstellation: traditioner og specielle temaer"),
    ],
    "integration-figur.svg": [
        ("Type", "Konstellation: integrations-temaer"),
    ],
    "afslutning-figur.svg": [
        ("Type", "Konstellation"),
    ],
    "forord-figur.svg": [
        ("Type", "Konstellation: 5 osteopati-pionerer + 'Alle os' omkring 'Den biodynamiske model'"),
        ("Center", "Den biodynamiske model"),
        ("A.T. Still", "A.T. / Still"),
        ("William G. Sutherland", "William G. / Sutherland"),
        ("Rollin E. Becker", "Rollin E. / Becker"),
        ("James Jealous", "James / Jealous"),
        ("Alle os", "Alle / os"),
    ],
}


# ============================================================================
# HJÆLPERE
# ============================================================================

def parse_sektioner(body: str):
    """Split body på '## Heading' og returnér liste af (heading, content)-pairs."""
    pattern = re.compile(r'^(##+)\s+(.+?)\s*$', re.MULTILINE)
    matches = list(pattern.finditer(body))
    sections = []
    if not matches:
        return [("", body.strip())]
    if matches[0].start() > 0:
        pre = body[:matches[0].start()].strip()
        if pre:
            sections.append(("", pre))
    for i, m in enumerate(matches):
        heading = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[start:end].strip()
        sections.append((heading, content))
    return sections


def parse_refleksioner(body: str):
    """Returnér liste af refleksionsspørgsmål fra et body-stykke."""
    cleaned = re.sub(r'^###+\s+.+$', '', body, flags=re.MULTILINE)
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', cleaned) if p.strip()]
    return paragraphs


def extract_svg_texts(svg_path: Path) -> list:
    """Returnér liste af tekstindhold fra alle <text> elementer i en SVG."""
    if not svg_path.exists():
        return []
    text = svg_path.read_text(encoding='utf-8')
    matches = re.findall(r'<text[^>]*>(.*?)</text>', text, re.DOTALL)
    cleaned = []
    for m in matches:
        t = re.sub(r'<[^>]+>', '', m).strip()
        if t:
            cleaned.append(t)
    return cleaned


def render_illustration(svg_navn: str, label: str = None) -> str:
    """Render en illustrations-tekst-blok som markdown."""
    overskrift = label or svg_navn
    out = f"**[ILLUSTRATION: {overskrift}]**\n\n"

    if svg_navn in KAPITEL_HERO_TEKSTER:
        for k, v in KAPITEL_HERO_TEKSTER[svg_navn]:
            out += f"- **{k}:** {v}\n"
    else:
        # Fallback: ekstraher fra SVG
        svg_path = ROOT / "hero-motiver" / svg_navn
        texts = extract_svg_texts(svg_path)
        if texts:
            out += "*Tekster ekstraheret fra SVG (i SVG-rækkefølge):*\n\n"
            for i, t in enumerate(texts, 1):
                out += f"- **Tekst {i}:** {t}\n"
        else:
            out += "*(ingen tekst-elementer fundet)*\n"
    out += "\n"
    return out


def render_glyf_for_begreb(filnavn: str, del_titel: str) -> str:
    """For begreb: returner glyfens tekstindhold."""
    glyf_navn = SUBSECTION_HERO.get(filnavn)
    if not glyf_navn:
        return ""
    glyf_path = ROOT / "hero-motiver" / glyf_navn
    texts = extract_svg_texts(glyf_path)
    if not texts:
        return ""
    out = f"**[ILLUSTRATION: Glyf — {del_titel}]**\n\n"
    for i, t in enumerate(texts, 1):
        out += f"- **Tekst {i}:** {t}\n"
    out += "\n"
    return out


def render_stadie_figur(filnavn: str, del_titel: str) -> str:
    """For stadie: returner stadie-figurens tekstindhold."""
    sub_navn = SUBSECTION_HERO.get(filnavn)
    if not sub_navn:
        return ""
    sub_path = ROOT / "hero-motiver" / sub_navn
    texts = extract_svg_texts(sub_path)
    if not texts:
        return ""
    out = f"**[ILLUSTRATION: Stadie-figur — {del_titel}]**\n\n"
    for i, t in enumerate(texts, 1):
        out += f"- **Tekst {i}:** {t}\n"
    out += "\n"
    return out


# ============================================================================
# INSPIRATIONS-PARAGRAFFER (kursiv) — nye vinkler til hvert begreb og rum
# ============================================================================

BEGREB_INSPIRATIONER = {
    "01-dynamisk-stilhed": [
        "Charles Ridley kalder Dynamisk Stilhed for 'the source field' — kilden hvorfra al rytme og form udspringer. Hans pointe: stilheden er ikke fravær af bevægelse, men det generative felt selv. Vi sigter ikke mod stilheden — vi opdager, at den allerede sigter mod os.",
        "Franklyn Sills sporer Dynamisk Stilhed tilbage til den embryonale præ-form-tilstand før den første celledeling. Tilstanden bærer hele organismens blueprint som ubrudt potentiale, og det samme felt forbliver tilgængeligt livet igennem som det dybeste fulcrum systemet kan hvile i — hans 'ground of being'.",
        "Når Dynamisk Stilhed viser sig, registrerer mange behandlere det 'Holistic Shift', Sills og Kern beskriver: en målbar autonom skift mod dyb parasympatisk dominans. Vejrtrækningen aftager hos både klient og behandler, det relationelle felt smelter sammen, kroppen begynder at bevæge sig fra et helt andet sted.",
    ],
    "02-breath-of-life": [
        "Sutherland opdagede Breath of Life ved længe at observere kranielle pulseringer der ikke kunne forklares ved hjerte eller lunge. Han konkluderede, at en finere åndedragsproces gennemstrømmer hele organismen. Sills beskriver den som tilstedeværende fra unionens øjeblik — det organiserende åndedrag bag al embryologisk udvikling.",
        "Michael Kern udfolder Breath of Life gennem tre funktioner: den formative (organiserer fra første celle), den helende (mobiliserer ved sygdom og skade), og den ordnende (vedligeholder den daglige homeostase). I praksis ses ikke én af dem isoleret, men de tre vævet sammen i hver puls.",
        "Roger Gilchrist og Scott Zamurut introducerer 'the embodiment tide' som den dybeste manifestation af Breath of Life — den tide der bærer fuld kropslig forankring efter dissociation eller traume. Det er ikke en yderligere tide; det er Breath of Life når den lander helt i organismens fysisk-fluide-tidale-helhed.",
    ],
    "03-primary-respiration": [
        "Sutherland kaldte Primary Respiration 'the breath of life expressing itself in motion'. Becker udfoldede det videre: tre rytmer der manifesterer Breath of Life på forskellige niveauer — Long Tide, Mid Tide og Cranial Rhythmic Impulse — hver med sin egen funktion og sin egen tilgangsvej i klinikken.",
        "Sills' inddeling af de tre tider giver klinisk præcision: Long Tide (~100 sekunder pr cyklus) som universel orientering, Mid Tide eller Fluid Tide (~2-3 cyklusser/minut) som vævenes fluide udfoldelse, og CRI (~8-12 cyklusser/minut) som det mest fysisk-mekaniske udtryk. Hver tide vækker et andet niveau.",
        "Embryologisk viser Primary Respiration sig allerede inden hjertet begynder at slå. Den primære rytmiske organisering forbereder den kommende kardio-vaskulære funktion og fortsætter parallelt hele livet — en arv fra det tidspunkt, hvor liv var bevægelse uden organer at bevæge sig i.",
    ],
    "04-midtlinjen": [
        "Sills skelner mellem fire midtlinjer: Primal Midline (Breath of Lifes første organiserende impuls fra unionens øjeblik), Quantum Midline (det forholdsmæssige rum mellem to fluid felter), Fluid Midline (notochordens fluide forløber) og den anatomiske notochordal midtlinje. Hver enkelt har sin egen behandlings-tilgang.",
        "Notochorden, der dannes i embryonets tredje uge, er ikke kun en forløber for kroppens midte — den er den første struktur der organiserer al øvrig formation omkring sig. Sills beskriver, at samme organiserende impuls fortsat er aktiv i den voksne krop som dybeste organiserings-akse.",
        "I klinik manifesterer Primal Midline sig ofte som en mærkbar kraft-orientering fra perinæum til kraniets top. Den følte midtlinje matcher ikke altid den anatomiske — funktionelle midtlinjer kan være forskudt af tidlige traumer. Hvor de mødes eller divergerer, åbner et særligt klinisk landskab.",
    ],
    "05-the-health": [
        "Andrew Taylor Stills grundsætning 'find the health, anyone can find disease' er biodynamikkens kerneorientering. Becker udfoldede den: sundheden er aldrig fraværende, kun nogle gange tilsløret. Kern bygger videre — sundheden er ikke fravær af sygdom men en aktiv organiserende kraft til stede i ethvert øjeblik.",
        "Sills knytter The Health til Breath of Lifes formative funktion: sundheden er det blueprint, organismen oprindeligt blev formet fra, og som forbliver tilstede som referencepunkt hele livet. Klinisk arbejder vi ikke FOR sundheden — vi arbejder FRA den, som vores faste udgangspunkt.",
        "Når klienten oplever sig så syg at sundheden synes umulig, er Beckers råd at lade hænderne hvile et sted hvor sundheden stadig kan ses — selv et lille felt er nok. Derfra organiserer systemet sig selv mod helhed. Sundheden behøver kun et arbejdspunkt for at begynde.",
    ],
    "06-motion-present": [
        "Becker: 'liv er bevægelse'. Hver levende celle, hvert system, hvert vævslag udtrykker sig som bevægelse på sit eget niveau. Motion Present samler dem ikke som ét fænomen men som et væv af samtidige rytmer — fra cellulær mikrobevægelse til den langsomme tidale udfoldelse i hele organismen.",
        "Sills understreger den kliniske vigtighed af at lytte til ALLE rytmer samtidigt uden at vælge én. Den behandler der hænger fast i én rytme (ofte CRI) mister information fra de dybere tider. Motion Present-perceptionen er derfor en disciplin i ikke-selektion.",
        "Når Motion Present pludselig stiger i intensitet, har systemet ofte fundet noget at arbejde med. Når den falder næsten til nul, er det sjældent tomrum — oftere er vi tæt på Stillpoint eller The Neutral. Kern beskriver disse skift som signaler fra den iboende behandlingsplan.",
    ],
    "07-fulcrum": [
        "Sutherland opdagede fulcrum-konceptet ved at observere, at kraniets membraner organiserede sig omkring et bevægeligt centrum — Sutherlands 'fulcrum of the falx'. Beckers udvikling: hvert system har et 'fulcrum of health', hvor organisering er stærkest, og et 'fulcrum of dysfunction', hvor energien er bundet.",
        "Sills udvider med begrebet 'inherent fulcrum' — naturligt forekommende ankerpunkter i organismen som hele systemet refererer til. Disse er ikke fast anatomi; de er funktionelle ligevægtspunkter der dynamisk omorganiserer sig som svar på indre eller ydre belastning.",
        "Klinisk er forskydende fulcrums et tegn på dyb proces — systemet vælger nyt fokus, ofte uden vores intervention. Beckers anbefaling: bliv i fulcrum of health, ikke i det dysfunktionelle fulcrum. Derfra organiserer det belastede område sig spontant mod balance, ofte hurtigere end ved direkte intervention.",
    ],
    "08-stillpoints": [
        "Sutherlands originale stillpoint var CV4-teknikken — en induceret pause i den kranielle bevægelse. Senere blev det klart, at stillpoints opstår spontant under behandling, ofte som tegn på systemets eget skift mod dybere lag. Sills beskriver dem som naturlige hvilepladser mellem cyklusser snarere end induktioner.",
        "Becker pegede på, at stillpoints sker på alle tide-niveauer — ikke kun i CRI. Et Long Tide-stillpoint er kvalitativt anderledes: dybere, mere altomfattende, ofte ledsaget af Holistic Shift. Det fortæller os noget om hvilket niveau systemet aktuelt arbejder på.",
        "Det der følger efter et stillpoint er lige så vigtigt som selve punktet. Kern: efter et autentisk stillpoint genoptages bevægelsen ofte med ny kvalitet — som om systemet har genvejet sig. Mange terapeutiske ændringer manifesterer sig først her, ikke i selve pausen.",
    ],
    "09-transmutation": [
        "Becker introducerede 'transmutation of fluid' — observationen af at vævet under behandling kan ændre kvalitet fra tæt og rigid til flydende og levende. Det er ikke metafor men en målbar fænomenologisk forandring i vævs-impedans, hydration og bevægelses­karakter.",
        "Sills udfolder transmutation som overgangen mellem hans tre kroppe: Physical Body → Fluid Body → Tidal Body. Hver overgang har sin egen kvalitet og sit eget tempo. Klienten oplever ofte transmutation som indre opløsning eller flyden — terminologien er hvad de spontant rapporterer.",
        "Den alkymistiske metafor (bly til guld) bruges i flere biodynamiske skoler ikke som esoterisk tilføjelse, men som beskrivelse af det observerede: en lavere-organiseret struktur transformeres til en højere-organiseret tilstand, ikke ved kraft men ved at blive holdt i et felt af tilstedeværelse.",
    ],
    "10-the-neutral": [
        "I osteopatisk tradition betyder 'neutral' et punkt af mekanisk balance hvorfra alle bevægelser er mulige. Sills har biodynamisk udvidet det til en tilstand af systemisk balance: alle aspekter af klienten — fysisk, fluid, autonomt — finder hvile i samme centrum, åbent mod transformation.",
        "The Neutral er en præ-betingelse, ikke et mål. Becker pegede på, at de dybeste behandlingsprocesser kun begynder NÅR The Neutral er etableret. Uden den er vi i ANS-aktivitet, ikke i biodynamisk arbejde. Behandlingen før The Neutral er forberedelse; behandlingen efter er den reelle proces.",
        "Holistic Shift er det biologiske udtryk for The Neutral. Sills og Kern beskriver det som det øjeblik klientens autonome system bevæger sig fra arousal eller defense til parasympatisk dominans. Det er målbart i hjerterytme-variabilitet og åndedrag — det er ikke kun en oplevelse.",
    ],
    "11-automatic-shifting": [
        "Becker brugte termen 'automatic shifting' om kroppens egen kapacitet til at flytte fokus mellem områder uden vores indgriben. Hans pointe: systemet ved bedst, hvor energien skal hen først. Vores opgave er ikke at organisere processen men at give plads til den valgte rækkefølge.",
        "Sills knytter Automatic Shifting til Inherent Treatment Plan-konceptet: shifting er den synlige manifestation af den underliggende plan. Hvad der ser kaotisk ud er sjældent kaos — det er en intelligens vi ikke kan forudsige. At lade den udfolde sig kræver tillid til processen selv.",
        "Klinisk yder hurtig shifting fra område til område ofte den dybeste effekt. Kern beskriver dette som 'global behandling' — systemet ordner relationer mellem dele snarere end at arbejde lokalt. Behandlerens fristelse til at gribe ind med teknik er størst her, og oftest mest skadelig.",
    ],
    "12-den-iboende-behandlingsplan": [
        "Beckers 'inherent treatment plan' er biodynamikkens måske mest radikale ide: kroppen kender sin egen vej til heling, og vores rolle er at lytte den frem. Det er ikke teknik men en attitude — et faktisk skift fra at være planlæggeren til at være vidnet.",
        "Kern beskriver, at læsning af den iboende plan kræver dyb stilhed i behandleren. Når vi har en agenda, hører vi vores agenda; når vi er stille, hører vi planen. Sills tilføjer, at planen ofte først bliver tydelig efter The Neutral er etableret — ikke før.",
        "Den iboende plan kan inkludere ubehag — smerte, følelser, midlertidig dysregulering. Becker: vi må kende forskellen mellem nyttig smerte (transmutation, der hører til processen) og skadelig overvældelse. Når planen leder gennem ubehag, er behandlerens udfordring at holde plads uden at lindre væk.",
    ],
    "13-fluid-body": [
        "Sutherland brugte termen 'fluid body' om hele organismens samlede væskemiljø — blod, lymfe, cerebrospinalvæske, interstitielt fluid. Sills udfoldede det som én af tre kroppe i sin model: Physical, Fluid, Tidal. Fluid Body er overgangen mellem den tørre fysiske krop og det subtile tidale felt.",
        "Embryologisk var vi primært væske før vi blev fast væv. Kern peger på, at denne primære væske-natur aldrig forsvinder — den bliver bare struktureret. I behandling kan vi vække denne primære væske-organisering igen, og det vi mærker i hænderne er denne genvågnen.",
        "Roger Gilchrists 'embodiment tide' opstår i Fluid Body-niveauet — det er den tide der bærer kroppen tilbage til fuld inkarnering efter dissociation eller traume. Klienter beskriver det ofte som 'at lande i sig selv igen'. Klinisk er det et af de stærkeste tegn på integration.",
    ],
    "14-the-lesion-field": [
        "Sutherland brugte oprindeligt termen 'lesion' om en lokal restriktion i den kranielle bevægelse. Senere generationer (Sills, Kern, Shea) udvidede det: en læsion er ikke et sted men et felt af bundet potency, der har trukket sig fra den almene cirkulation for at beskytte helheden.",
        "Sills beskriver lesional process snarere end lesional structure — feltet er en aktiv proces, ikke en fast struktur. Det vedligeholder sin egen organisering med energi, og det kræver vores anerkendelse, ikke vores intervention, for at slippe sin opgave og vende tilbage til feltet.",
        "Klinisk åbner læsionsfeltet sig oftest ikke ved direkte arbejde med selve læsionen, men ved at etablere The Neutral i resten af systemet. Når organismen oplever sig sikker nok, slipper feltet sin opgave. Becker: vi behandler aldrig læsionen — vi behandler systemet omkring den.",
    ],
    "15-potency": [
        "Sutherland kaldte potency for 'liquid light' — han observerede et felt af bioelektrisk energi der gennemstrømmer cerebrospinalvæsken og bærer den helbredende kraft. Senere blev det målbart som specifikke elektriske og elektromagnetiske mønstre i CSF og fascia. Det er ikke metafor — det er mærkbart.",
        "Becker skelnede mellem 'bound potency' (kraft bundet i lokale læsionsfelter for at opretholde dem) og 'free potency' (kraft til rådighed for almen heling og vedligeholdelse). Frigørelse af bound potency forøger ikke systemets energi — det vender den tilbage til helheden hvor den startede.",
        "Sills udfolder potency som 'the active fluid principle' — den fluide ordens-bærende kraft. Den manifesterer sig ikke som energi-strøm men som ændringer i vævets organisering: noget bliver mere koherent, mere bevægeligt, mere åbent. Vi mærker potency som tilstandsskift, ikke som energi der bevæger sig.",
    ],
    "16-ignition": [
        "Sills identificerer tre primære ignition-events i menneskets udvikling: ved unionens øjeblik (zygote-formation), ved fødslen (det første åndedrag), og ved 'embodiment' (den fulde landing i kroppen, der sker over de første år). Hver ignition er en tærskel-overskridelse til ny biologisk organisering.",
        "Kern beskriver re-ignition som processen, hvor en organisme der har trukket sig tilbage (efter sygdom, traume eller overvældelse) genfinder kraften til at være fuldt til stede. Det er ikke en restauration af det gamle — det er en ny ignition mod en ny baseline.",
        "Klinisk kan ignition mærkes i hænderne som en pludselig 'tænden' i feltet — en kvalitativ forskel før og efter. Sills: ignition kommer ikke fra teknik, men fra at de underliggende tærskelbetingelser er på plads — tilstrækkelig hvile, tilstrækkelig sikkerhed, tilstrækkelig orientering.",
    ],
    "17-axial-fluctuations": [
        "Becker beskrev axial fluctuations som de fluide bevægelser der følger kroppens centrale akse — særligt langs notochord og columna fra coccyx til sphenoid. De er en specifik manifestation af Primary Respiration i fluid body, og deres tilstand fortæller om midtlinjens organiserings-kapacitet.",
        "Sills udfolder axial fluctuations som direkte udtryk for Primal Midline-aktivitet. Når den centrale ordens-impuls er stærk, fluktuerer væsken tydeligt langs aksen. Når den er svag eller blokeret, mærkes fluktuationerne som tørre, klistrede eller helt fraværende — et klinisk tegn på dyb dysorganisering.",
        "Klienten kan opleve axial fluctuations forskelligt afhængigt af hvor i kroppen de mærker dem. I bækkenet ofte som vugning; i kraniet som let pres-forandring; langs columna som bølgende fornemmelse. Disse spontane beskrivelser hjælper med at konfirmere hvad behandlerens hænder mærker.",
    ],
    "18-wholeness": [
        "Stills 'principle of wholeness' er osteopatiens første princip og biodynamikkens fundament: organismen er en helhed, og hver del afspejler helheden. Sills udfolder det som 'the whole is in every part' — vi behandler aldrig isolerede dele, vi adresserer altid helheden gennem den del vi har under hænderne.",
        "Embryologisk er kroppen aldrig blevet 'sat sammen af dele' — vi var aldrig dele først. Vi var en helhed der differentierede sig. Sills peger på, at denne primære helhed forbliver til stede gennem hele livet som det organiserende princip vi kalder sundhed.",
        "Klinisk wholeness er en målbar observation, ikke filosofi: når en del bevæger sig, bevæger andre dele sig samtidigt og koordineret. Når denne synkronicitet ikke findes, er der dys-organisering at lytte til. Kern beskriver det som det første vi læser når hænderne lander: er feltet helt eller fragmenteret.",
    ],
}


RUM_INSPIRATIONER = {
    "Rum A — Den Fysiske Krop": [
        "Sills beskriver Physical Body som første af tre kroppe — den vi alle er trænet til at arbejde med. Den biodynamiske udvidelse er ikke at forlade Physical Body, men at lytte til den fra et andet sted: den er ikke separat fra Fluid og Tidal Body, den er deres mest manifeste lag.",
        "Embryologisk dannes Physical Body sidst — efter at fluid og tidal-organisering allerede har formet rummet. Kern udfolder dette: vævet bærer hukommelsen om sin fluid- og tidal-oprindelse, og det er denne hukommelse vi vækker, ikke en ny information vi tilfører.",
        "Klinisk lytning til Rum A er ikke at fokusere på struktur, men at lytte gennem strukturen til de dybere lag den hviler på. Becker: vi behandler aldrig kun vævet, men vævet er altid vores indgang. Den dybeste struktur-arbejde sker ofte uden at vi rører strukturen direkte.",
    ],
    "Rum B — Væskekroppen": [
        "Sutherlands oprindelige observation var, at hele organismens fluid-system bevæger sig som én sammenhængende enhed. Sills udfoldede det som Fluid Body — anden af tre kroppe — der inkluderer både cerebrospinalvæske, blod, lymfe og interstitielt fluid. Behandling af Fluid Body adresserer dem alle samtidigt.",
        "Roger Gilchrists 'embodiment tide' viser sig særligt tydeligt i Fluid Body-niveauet. Det er den tide der bærer fuld kropslig integration efter dissociation eller traume. Klienter beskriver oplevelsen som 'at lande i sig selv igen', 'at blive levende', 'at finde tilbage til sin krop'.",
        "Kern beskriver overgangen fra Rum A til Rum B som ofte mærkbar i en kvalitetsændring i hænderne — vævet bliver 'vådere', mere flydende. Klinisk er denne overgang ikke noget vi tvinger frem; den sker når nervesystemet har givet sin tilladelse via The Neutral.",
    ],
    "Rum C — Det Relationelle Felt": [
        "Sills og Kern udfolder det relationelle felt som biologisk realitet, ikke metafor. Når to nervesystemer mødes uden trussel, opstår en målbar fælles regulering — det vi kalder 'the field between'. Det er denne fælles biologi terapien arbejder med, ikke kun den individuelle klients indre.",
        "Charles Ridley peger på, at det relationelle felt har sin egen autoritet og intelligens. Det 'behandler' os begge, ikke kun klienten. Når vi indgår fuldt, ophører rollerne midlertidigt — der er kun feltet, og det vi kalder heling sker spontant indenfor det.",
        "Klinisk udfordring i Rum C er at give plads uden at forsvinde. Kern: behandleren må forblive distinkt nok til at være ankret, og åben nok til at lade feltet etablere sig. For lidt anker, og vi mister os selv; for meget anker, og feltet kan ikke åbne.",
    ],
    "Rum D — The Long Tide / Primary Respiration": [
        "Sills' Tidal Body — tredje af tre kroppe — er hjemstedet for Long Tide. Den bevæger sig fra horisonten ind mod kroppens midtlinje med en cyklus på cirka 100 sekunder, men intervallet varierer. Det er ikke en præcis konstant, men et felt vi orienterer os i.",
        "Becker beskrev Long Tide som 'den evige strøm' — ikke noget vi føler i vævet, men i det rum vi sidder i sammen med klienten. Det er en perception der kræver, at vores opmærksomhed udvider sig ud over kroppens grænser, mod horisonten og tilbage.",
        "Læringen af Long Tide sker ikke gennem instruktion. Sills og Kern lægger vægt på mentor-overlevering: en erfaren behandler holder hænderne sammen med dig på en klient, og over tid genkender du det de mærker. Det er en mundtlig tradition mere end en målbar færdighed.",
    ],
    "Rum E — Dynamisk Stilhed": [
        "Charles Ridleys 'Stillness' beskriver Dynamisk Stilhed som det 'source field' alle praksisser fører hen mod, hvis de er rene. Hans bidrag er den kontemplative gren af biodynamikken — formuleringer der honorerer det ufattelige uden at forklare det væk. Stilheden er kilden, ikke fraværet.",
        "Sills knytter Dynamisk Stilhed til 'ground of being' — det dybeste fulcrum organismen kan hvile i. Embryonalt svarer det til præ-form-tilstanden før den første celledeling. Klinisk genkendes det ved Holistic Shift: vejrtrækningen aftager, det relationelle felt smelter, tiden mister sit tempo.",
        "Hverken Sutherland, Becker eller Jealous beskrev Dynamisk Stilhed som et behandlings-mål, men som det grundlag al behandling foregår på. Det er sjældent vi når den direkte; oftest viser den sig som det rum, hvori al anden behandling allerede har fundet sted, når vi opdager det.",
    ],
}


# ============================================================================
# RENDERING
# ============================================================================

def render_intro_side() -> str:
    return dedent("""
        ---
        title: "Den Biodynamiske Model — Redigerbart Udkast"
        subtitle: "Komplet manuskript til redigering"
        author: "Niklas Patursson"
        lang: da
        toc: true
        toc-depth: 2
        ...

        # Vejledning

        Dette dokument indeholder ALT redigerbart indhold fra bogen i ét samlet
        Word-format: brødtekst, illustrationstekster, refleksionsspørgsmål og
        daglige invitationer.

        **Sådan bruger du dokumentet:**

        1. Redigér frit i Word — alt under en heading kan ændres.
        2. Bevar markørerne `[BRØDTEKST: ...]`, `[ILLUSTRATION: ...]`,
           `[REFLEKSIONSSPØRGSMÅL]`, `[DAGLIG INVITATION]`, `[UNDERTITEL]`,
           `[PART-BESKRIVELSE]` præcis som de står — de bruges til round-trip.
        3. Bevar etiketterne i illustrations-listerne ("Center", "Top", etc.)
           som de står; redigér kun selve teksten efter kolon.
        4. Send det redigerede dokument retur når du er færdig.

        ---
    """).strip() + "\n\n"


def render_part(part_nr: int, titel: str, beskrivelse: str) -> str:
    roman = ['I', 'II', 'III', 'IV'][part_nr - 1]
    return (
        f"\n# Part {roman} — {titel}\n\n"
        f"**[PART-BESKRIVELSE]**\n\n"
        f"{beskrivelse}\n\n"
        "---\n\n"
    )


def render_forord() -> str:
    """Forord — bruger den redigerede bog-version (ikke app's info.html)."""
    from byg_bog import render_forord as bog_forord
    raw = bog_forord()
    # Fjern hero-illustration fra bog-rendering (vi har vores eget)
    raw = re.sub(r'```\{=latex\}.*?```\n?', '', raw, flags=re.DOTALL)
    raw = raw.replace("# Forord", "").strip()

    out = "\n# Forord\n\n"
    out += render_illustration("forord-figur.svg", "Forord-konstellation")
    out += "**[BRØDTEKST: Forord]**\n\n"
    out += raw + "\n\n"
    out += "---\n\n"
    return out


def render_kapitel_body_sektioner(body: str,
                                    inspirationer: list = None,
                                    rum_inspirationer: dict = None) -> str:
    """Render brødtekst-sektioner og refleksioner fra et body-stykke.

    Hvis 'inspirationer' angives (3 tekster), indsættes en INSPIRATION-blok
    lige før refleksionsspørgsmålene. Hvis 'rum_inspirationer' (dict) er
    angivet, slås op pr. Rum X-heading.
    """
    out = ""
    sections = parse_sektioner(body)
    current_rum = None
    for heading, content in sections:
        if not content.strip() and not heading:
            continue
        if heading.lower().startswith("til refleksion"):
            # Indsæt inspirations-blok før refleksioner
            if inspirationer:
                out += render_inspiration_block(inspirationer)
            elif rum_inspirationer and current_rum and current_rum in rum_inspirationer:
                out += render_inspiration_block(rum_inspirationer[current_rum])
                current_rum = None
            out += "**[REFLEKSIONSSPØRGSMÅL]**\n\n"
            for i, q in enumerate(parse_refleksioner(content), 1):
                out += f"{i}. {q}\n\n"
        elif heading.lower() == "relationer":
            continue
        elif heading:
            if heading.startswith("Rum "):
                current_rum = heading
            out += f"**[BRØDTEKST: {heading}]**\n\n"
            out += content + "\n\n"
        else:
            out += content + "\n\n"
    return out


def render_inspiration_block(paragraphs: list) -> str:
    """Render 3 inspirations-paragraffer i kursiv som forslag til redaktion."""
    out = "**[INSPIRATION — nye vinkler at overveje]**\n\n"
    for p in paragraphs:
        out += f"*{p}*\n\n"
    return out


def render_kapitel_fil(filnavn: str, kapitel_nr: int) -> str:
    """Render én markdown-fil som kapitel — med illustrationen inline."""
    path = CONTENT / f"{filnavn}.md"
    if not path.exists():
        return f"\n# Kapitel {kapitel_nr}: {filnavn} (mangler)\n\n"

    fm, body = laes_md(path)
    body = strip_relationer(body)
    body = strip_html_illustrations(body)

    titel = fm.get("titel", filnavn).strip()
    undertitel = fm.get("undertitel", "").strip()

    out = f"\n# Kapitel {kapitel_nr}: {titel}\n\n"
    if undertitel:
        out += f"**[UNDERTITEL]** {undertitel}\n\n"

    # Kapitel-hero illustration inline
    hero_svg = CHAPTER_HERO.get(filnavn)
    if hero_svg:
        out += render_illustration(hero_svg, f"Kapitel-hero ({titel})")

    # Special-cases: list de underliggende konstellations-tekster lige under
    # hovedillustrationen, så brugeren kan editere dem nær hovedillustrationen
    if filnavn == "de-syv-perspektiver":
        out += "**[ILLUSTRATION: De 7 Perspektiver — konstellations-tekster]**\n\n"
        out += "*Hvert perspektiv har en fuld titel + to-linjers cirkeltekst (samme tekst genbruges i alle perspektivets cirkel-varianter).*\n\n"
        for fuld, l1, l2 in PERSPEKTIVER_FIGURER:
            out += f"- **{fuld}** → cirkel-tekst: \"{l1}\" / \"{l2}\"\n"
        out += "\n"
    elif filnavn == "de-otte-essentielle-egenskaber":
        out += "**[ILLUSTRATION: De 8 Egenskaber — konstellations-tekster]**\n\n"
        out += "*Hver egenskab har en fuld titel + to-linjers cirkeltekst.*\n\n"
        for fuld, l1, l2 in EGENSKABER_FIGURER:
            out += f"- **{fuld}** → cirkel-tekst: \"{l1}\" / \"{l2}\"\n"
        out += "\n"
        out += "**[UNDEROVERSKRIFTER: 8 Egenskaber — taglines]**\n\n"
        out += "*Korte taglines tilføjet under hver egenskab i bogen (ikke i kildemarkdown).*\n\n"
        for k, v in EGENSKAB_SUBTITLES.items():
            out += f"- **{k}** → {v}\n"
        out += "\n"
    elif filnavn == "de-fem-zoner":
        out += "**[ILLUSTRATION: De 5 Rum — venn-tekster]**\n\n"
        out += "*Hvert rum har sin egen venn-figur (rum-a-figur.svg ... rum-e-figur.svg). Tekstindhold pr. rum:*\n\n"
        for rum_titel, svg_navn in RUM_HERO_FIGURER.items():
            svg_path = ROOT / "hero-motiver" / svg_navn
            texts = extract_svg_texts(svg_path)
            out += f"- **{rum_titel}** ({svg_navn}):\n"
            for t in texts:
                out += f"  - {t}\n"
        out += "\n"
    elif filnavn == "helheden-under-pres":
        out += "**[ILLUSTRATION: Helheden under pres — fire forskydnings-figurer]**\n\n"
        out += "*Hver forskydning har sin egen konstellations-figur:*\n\n"
        for label, svg_navn in HELHED_HERO_FIGURER.items():
            svg_path = ROOT / "hero-motiver" / svg_navn
            texts = extract_svg_texts(svg_path)
            out += f"- **{label}** ({svg_navn}):\n"
            for t in texts:
                out += f"  - {t}\n"
        out += "\n"
    elif filnavn == "de-fire-guidede-oevelser":
        out += "**[ILLUSTRATION: De 4 Øvelser — koncentriske-figurer]**\n\n"
        out += "*Hver øvelse har sin egen koncentriske-ovaler-figur:*\n\n"
        for label, svg_navn in OEVELSE_HERO_FIGURER.items():
            svg_path = ROOT / "hero-motiver" / svg_navn
            texts = extract_svg_texts(svg_path)
            out += f"- **{label}** ({svg_navn}):\n"
            for t in texts:
                out += f"  - {t}\n"
        out += "\n"
    elif filnavn == "andre-traditioner-og-specielle-temaer":
        out += "**[UNDEROVERSKRIFTER: Specielle Temaer — taglines]**\n\n"
        out += "*Korte taglines tilføjet under hvert speciel-tema i bogen.*\n\n"
        for k, v in SPECIELLE_TEMAER_SUBTITLES.items():
            out += f"- **{k}** → {v}\n"
        out += "\n"

    # Brødtekst-sektioner og refleksioner
    # For de-fem-zoner: pass rum_inspirationer så de injiceres pr. Rum X
    if filnavn == "de-fem-zoner":
        out += render_kapitel_body_sektioner(body, rum_inspirationer=RUM_INSPIRATIONER)
    else:
        out += render_kapitel_body_sektioner(body)

    # Daglig invitation
    inv = _vaelg_invitation_for_kapitel(kapitel_nr)
    if inv:
        out += "**[DAGLIG INVITATION]**\n\n"
        out += f"- **Kategori:** {inv['kategori']}\n"
        out += f"- **Titel:** {inv['navn']}\n"
        out += f"- **Evokation:** {inv['evokation']}\n"
        out += f"- **Invitation:** {inv['invitation']}\n\n"

    out += "---\n\n"
    return out


def render_samling(samling_titel: str, undermappe: str, filnavne: list,
                    kapitel_nr: int) -> str:
    """Render en samling (begreber eller stadier) som ét kapitel."""
    out = f"\n# Kapitel {kapitel_nr}: {samling_titel}\n\n"

    # Samling-hero illustration
    samling_svg = SAMLING_HERO.get(undermappe)
    if samling_svg:
        out += render_illustration(samling_svg, f"Samling-hero ({samling_titel})")

    for filnavn in filnavne:
        path = CONTENT / undermappe / f"{filnavn}.md"
        if not path.exists():
            out += f"\n## {filnavn} (mangler)\n\n"
            continue

        fm, body = laes_md(path)
        body = strip_relationer(body)
        body = strip_html_illustrations(body)

        del_titel = fm.get("titel", filnavn).strip()
        del_undertitel = fm.get("undertitel", "").strip()

        out += f"\n## {del_titel}\n\n"
        if del_undertitel:
            out += f"**[UNDERTITEL]** {del_undertitel}\n\n"

        # Glyf eller stadie-figur inline
        if undermappe == "begreber":
            out += render_glyf_for_begreb(filnavn, del_titel)
        elif undermappe == "stadier":
            out += render_stadie_figur(filnavn, del_titel)

        # Brødtekst og refleksioner
        # For begreber-samling: pass inspirationer pr. begreb-filnavn
        if undermappe == "begreber":
            inspirationer = BEGREB_INSPIRATIONER.get(filnavn)
            out += render_kapitel_body_sektioner(body, inspirationer=inspirationer)
        else:
            out += render_kapitel_body_sektioner(body)

    # Daglig invitation
    inv = _vaelg_invitation_for_kapitel(kapitel_nr)
    if inv:
        out += "**[DAGLIG INVITATION]**\n\n"
        out += f"- **Kategori:** {inv['kategori']}\n"
        out += f"- **Titel:** {inv['navn']}\n"
        out += f"- **Evokation:** {inv['evokation']}\n"
        out += f"- **Invitation:** {inv['invitation']}\n\n"

    out += "---\n\n"
    return out


def render_litteraturliste() -> str:
    from byg_bog import render_litteraturliste as bog_litt
    raw = bog_litt()
    raw = re.sub(r'^# Litteraturliste', '# Litteraturliste', raw, count=1, flags=re.MULTILINE)
    return "\n" + raw + "\n"


def render_alle_invitationer_bilag() -> str:
    """Bilag: alle 120 daglige invitationer (kildedata)."""
    out = "\n# Bilag — Alle 120 Daglige Invitationer (kildedata)\n\n"
    out += "*Kun 15 invitationer bruges i bogen (én pr. kapitel). Resten er reservedata. Hver kategori har 20 invitationer.*\n\n"
    teksters = hent_mikrotekster()
    grupper = {}
    rækkefølge = []
    for t in teksters:
        cat = t.get("kategori", "andet")
        if cat not in grupper:
            rækkefølge.append(cat)
            grupper[cat] = []
        grupper[cat].append(t)

    KATEGORI_NAVNE = {
        "princip": "De 10 Biodynamiske Principper",
        "blechschmidt": "Blechschmidt-Principper",
        "perspektiv": "De 7 Perspektiver",
        "egenskab": "De 8 Essentielle Egenskaber",
        "zone": "De 5 Rum",
        "stadie": "De 5 Stadier",
    }
    for cat in rækkefølge:
        out += f"## {KATEGORI_NAVNE.get(cat, cat)}\n\n"
        for t in grupper[cat]:
            out += f"### {t['navn']}\n\n"
            out += f"- **Titel:** {t['navn']}\n"
            out += f"- **Evokation:** {t['evokation']}\n"
            out += f"- **Invitation:** {t['invitation']}\n\n"
    return out


# ============================================================================
# SAMLET MANUSKRIPT
# ============================================================================

def byg_redigerbart_udkast() -> str:
    out = []
    out.append(render_intro_side())
    out.append(render_forord())

    kapitel_nr = 1
    for part_idx, (part_titel, part_beskrivelse, kapitler) in enumerate(DELE):
        out.append(render_part(part_idx + 1, part_titel, part_beskrivelse))
        for spec in kapitler:
            if spec[0] == "fil":
                out.append(render_kapitel_fil(spec[1], kapitel_nr))
            elif spec[0] == "samling":
                _, titel, undermappe, filnavne = spec
                out.append(render_samling(titel, undermappe, filnavne, kapitel_nr))
            kapitel_nr += 1

    out.append(render_alle_invitationer_bilag())
    out.append(render_litteraturliste())

    return "\n".join(out)


# ============================================================================
# PANDOC
# ============================================================================

def kor_pandoc(md_path: Path, out_path: Path) -> bool:
    cmd = ["pandoc", str(md_path), "-o", str(out_path),
           "--toc", "--toc-depth=2"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            print("PANDOC FEJL:", r.stderr[-2000:], file=sys.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        print("PANDOC TIMEOUT", file=sys.stderr)
        return False


def main():
    print("Bygger redigerbart udkast …")
    md = byg_redigerbart_udkast()

    md_path = OUT / "manuskript-redigerbar.md"
    md_path.write_text(md, encoding='utf-8')
    print(f"  ✓ {md_path} ({len(md):,} tegn)")

    docx_path = OUT / "manuskript-redigerbar.docx"
    if kor_pandoc(md_path, docx_path):
        print(f"  ✓ {docx_path}")
    else:
        print("  × DOCX fejlede", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
