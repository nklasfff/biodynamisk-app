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
        "Når Dynamisk Stilhed viser sig i hænderne, er det ofte ikke som fravær men som en kvalitet af bæren — som om vævet hviler i noget der holder det. Mange behandlere beskriver det som at sidde over et dybt vand de ikke længere skal forstyrre.",
        "Stilheden lader sig genkende på tværs af traditioner — i zazen-meditation, i den apophatiske teologis gud-uden-egenskaber, i ørkenfædrenes hesychia. Det betyder ikke at de er det samme — kun at mennesket har erfaret denne kvalitet før, og at vi ikke står alene i den.",
        "Den kommer ikke på vores invitation, og hyppigst slet ikke. De fleste behandlinger forløber uden at Dynamisk Stilhed viser sig direkte, og det er som det skal være. At vente på den er ofte den sikreste måde at lukke døren til den.",
    ],
    "02-breath-of-life": [
        "Sutherland skelnede skarpt mellem det fysiske åndedrag og Breath of Life. De er ikke det samme, men de mødes — som om åndedrættet er en daglig påmindelse om noget langt dybere der bærer vores liv hvert øjeblik, ikke kun ved indånding.",
        "Klienter beskriver nogle gange en oplevelse af 'første åndedrag' under en behandling — noget der trækker vejret i dem som de ikke selv styrer. Det er ofte i sådanne øjeblikke at heling, der har ventet, finder sin egen vej ind.",
        "Når Breath of Life føles fjern, er det som regel ikke et tegn på at den er væk — kun at vi leder efter den med vores aktive opmærksomhed. Den findes oftest når vi holder op med at lede og bare bliver i det vi mærker.",
    ],
    "03-primary-respiration": [
        "Den 100-sekunders cyklus er ikke en målbar konstant — Sutherland talte om 6-10 cyklusser per 10. minut, Jealous formulerede 100 sekunder vejledende. Tallene er pejlemærker, ikke definitioner. Det egentlige er at en langsom rytme bærer livet på et niveau under den hurtige.",
        "Læringen af Primary Respiration sker ikke gennem måling men gennem mentor-overlevering: en erfaren behandler holder hænderne med dig på en klient, og over tid genkender du det han eller hun mærker. Det er en mundtlig tradition mere end en målbar færdighed.",
        "Forskellen fra den kranielle rytme (CRI på 8-12 cyklusser per minut) er væsentlig — Primary Respiration er noget andet, langsommere, dybere. Begge findes, men de svarer ikke på de samme behandlings-greb. Bevidst at adskille dem skærper hænderne.",
    ],
    "04-midtlinjen": [
        "Sills' typologi af midtlinjer — primal, quantum, fluid, notochordal — kan være nyttig: hver midtlinje opstår som svar på et bestemt udviklingsfald. At mærke flere på samme klient handler om at vide hvilken man arbejder med, ikke om at samle dem alle.",
        "Embryologisk er midtlinjen ikke en linje men en proces. Notochorden, der dannes i tredje uge, organiserer alt omkring sig — og bliver siden til midten af mellemvirvelskiverne. Noget af denne organiserende impuls fortsætter i kroppen hele livet.",
        "Den følte midtlinje matcher ikke altid den anatomiske. Klienter kan have funktionelle midtlinjer der er forskudt af gamle traumer — bækkenet et sted, hovedet et andet. At arbejde med disse parallelle akser kræver tålmodighed mere end korrektion.",
    ],
    "05-the-health": [
        "Becker insisterede på at sundheden altid er til stede — også hos den syge, også hos den døende. Det er en fagligt vigtig position: vi behandler ikke noget vi tilføjer, men noget der allerede er der, som har brug for plads til at udfolde sig.",
        "I kontrast til symptom-fokuseret medicin starter biodynamikken fra det modsatte sted: ikke 'hvad er galt' men 'hvad er rigtigt' — også midt i krisen. Det er ikke optimisme. Det er en faglig disciplin der ændrer hvilke informationer vi mærker.",
        "Hvad gør vi når klienten ikke kan mærke sundheden i sig selv? Vi venter ikke på at de finder den. Vi arbejder fra antagelsen om at den findes, og lader vores hænder hvile på det sted hvor den endnu kan ses.",
    ],
    "06-motion-present": [
        "Motion Present er ikke én bevægelse men et væv af mange — fra cellulær mikrobevægelse til store fasciale ruller. At lære at lytte til dem alle uden at vælge er en disciplin: vi bliver ikke specialister i én rytme men generalister i bevægelsens fylde.",
        "Når Motion Present pludselig stiger i intensitet, er det ofte fordi systemet har fundet noget at arbejde med. Når den falder næsten til nul, er vi sjældent ude i et tomrum — oftest tæt på Stillpoint eller The Neutral. Begge tilstande er informative.",
        "At se efter motion præsent er ikke det samme som at lede efter den. Når vi leder, sender vi små signaler ind i feltet og forstyrrer det vi forsøger at observere. Lytten har en helt anden kvalitet — den modtager uden at sende.",
    ],
    "07-fulcrum": [
        "Fulcrums er ikke faste anatomiske punkter — de bevæger sig, opløses, dannes. En sund fulcrum er bevægelig; en dysfunktionel er rigid og isoleret. At skelne mellem dem er kerneobservationen i biodynamisk arbejde, og en daglig øvelse.",
        "Beckers begreb 'fulcrum of health' er en udvikling: det er det sted hvor systemets organisering er stærkest, ikke hvor det er mest belastet. At lokalisere det forskydende fulcrum tager bagsædet — vi sætter os i sundhedens fulcrum først.",
        "Når et fulcrum spontant flytter sig under hænderne, har systemet selv valgt næste fokus. Vores opgave er ikke at følge med fysisk men at give plads i opmærksomheden. Den nye placering bringer ofte information som det gamle fulcrum havde holdt skjult.",
    ],
    "08-stillpoints": [
        "Klienter beskriver stillpoints meget forskelligt — nogle som fald, nogle som svæven, nogle som klarhed der pludselig kommer. Det fælles træk er at noget sker uden anstrengelse. Det fortæller os noget om hvilken slags handling helingen er: ofte handler det om ikke-handling.",
        "Forskellen mellem en behandler-induceret stillpoint og en spontan er værd at mærke. Den inducerede er en indgang; den spontane er ofte en dybere proces. Begge har værdi — men kun hvis vi kan skelne dem og ikke prøver at fremtvinge det andet.",
        "Det der følger efter et stillpoint er lige så vigtigt som selve punktet. Mange terapeutiske ændringer sker ikke i stilheden men i den genoptagne bevægelse bagefter — som om systemet har genvejet sig selv og nu udfolder den nye balance.",
    ],
    "09-transmutation": [
        "Alkymisten ville sige: bly forvandles ikke til guld ved kraft, men ved eksponering for et felt. Transmutation i biodynamikken har den samme logik. Vi tilfører ikke noget — vi skaber et felt hvor vævets egne kvaliteter kan ændre form.",
        "Den synlige transmutation går ofte gennem en mellemtilstand — fra rigid struktur til væskelignende kvalitet, og derfra til noget endnu mere flydende. Hvert lag tager den tid det tager. Vi kan ikke springe et lag over uden at handlingen mister sin substans.",
        "Når transmutation er ufuldstændig, er det sjældent fordi den er stoppet — oftere fordi den er i et lag vi ikke kan mærke endnu. Vores tålmodighed er det enkelte stærkeste redskab. Helingen sker stadig, men i sit eget tempo.",
    ],
    "10-the-neutral": [
        "The Neutral forveksles let med afslapning, men er ikke det samme. Afslapning er en reduktion af spænding; The Neutral er en samling af alle systemers aktivitet i et fælles centrum. Klienten er ikke 'slap' — de er fuldt til stede, bare uden distance.",
        "Polyvagalt set svarer The Neutral nok mest til en dyb ventral vagal aktivitet med tilstrækkelig sympatisk tone til at opretholde nærvær. Det er ikke en passiv tilstand — det er en aktiv-balanceret tilstand som systemet kun finder under særlige betingelser.",
        "Mange behandlinger lykkes ikke med at nå The Neutral, og det er som det skal være. Den er ikke et behandlings-mål men en forudsætning, der nogle gange er der, nogle gange ikke. At kræve den er at lukke den ude.",
    ],
    "11-automatic-shifting": [
        "Automatic Shifting demonstrerer at systemet selv bestemmer rækkefølgen af heling. Hvad der ser kaotisk ud er sjældent kaos — det er en intelligens vi ikke kan forudsige. Vores job er ikke at organisere processen men at holde plads til den.",
        "Når shifting går hurtigt fra område til område, kan det føles som om der ikke 'sker noget'. Men noget af det dybeste arbejde sker netop her — systemet ordner relationer mellem dele snarere end at arbejde lokalt. At blive i åbenheden kræver disciplin.",
        "Behandlerens største fristelse i Automatic Shifting er at gribe ind med teknik. Vi vil hjælpe noget. Men oftest hjælper vi mest ved at trække vores intention tilbage og lade processen styre. Det er ofte først bagefter at meningen viser sig.",
    ],
    "12-den-iboende-behandlingsplan": [
        "Disciplinen ved ikke at have en plan er sværere end den lyder. Vores uddannelse har trænet os i at observere, vurdere, vælge intervention. At slippe alt det er ikke at blive passiv — det er at flytte tilliden fra vores plan til systemets.",
        "Den iboende plan er ikke det samme som 'lade hvad som helst ske'. Vi mærker stadig, vi vurderer stadig, vi reagerer stadig på sikkerhedsspørgsmål. Forskellen er hvor vi henter retningen — fra protokollen eller fra det levende system.",
        "Nogle gange er den iboende plan smerte. Klienten oplever ubehag, og vores trang til at lindre er stærk. At blive ved med at stole på planen kræver at vi kender forskellen mellem nyttig smerte (transmutation) og ikke-nyttig smerte (overvældelse).",
    ],
    "13-fluid-body": [
        "Modern fascia-forskning (Schleip, Stecco) bekræfter at kroppens 'tørre' væv slet ikke er tørt — fascia er gennemvædet af interstitielt fluid og bevæger sig som en sammenhængende fluid-matrix. Sutherlands intuition for over 100 år siden viser sig at have anatomisk substans.",
        "Fluid body opleves ofte først som en kvalitet i hænderne, ikke som en mekanisk bevægelse vi kan beskrive. Det er som om kroppen pludselig bliver 'vådere'. Den oplevelse er real og målbar — vævs-impedans og lokal hydration ændrer sig.",
        "Når fluid body føles låst, er det sjældent at væsken er væk — den er bare ikke i bevægelse. Det vi lytter efter er det første tegn på at strømmen begynder igen. Det første tegn er ofte mindre end vi forventer.",
    ],
    "14-the-lesion-field": [
        "Læsionsfeltet ligner i sin struktur traume-kortet hos Levine, van der Kolk og Porges: et område der har trukket sig tilbage for at beskytte helheden. At se det som beskyttelse, ikke fejl, ændrer behandlingens grundtone fundamentalt.",
        "Læsionens visdom er ofte gemt i hvad den engang reddede. At spørge 'hvad ville være sket uden denne tilbagetrækning' åbner et helt andet rum end 'hvordan får vi den tilbage'. Behandling bliver ikke korrektion men anerkendelse.",
        "Når feltet ikke vil løslade, er det oftest fordi grundpræmissen — sikkerhed nu — endnu ikke er etableret. Vi kan ikke springe det skridt over. Først nervesystemets dybe besked om 'her er sikkert', så kan læsionen begynde at slippe.",
    ],
    "15-potency": [
        "Potency forveksles let med energi-begreber fra andre traditioner (qi, prana, orgon). Forskellene er væsentlige: Potency er specifikt knyttet til sundheds- og helingsprocesser, ikke en almen livsenergi. At blande begreberne sammen mister noget af det biodynamiske.",
        "Bound potency findes overalt hvor systemet har skullet låse noget for at overleve. Når den frigives, er den ikke 'mere kraft' — det er den oprindelige kraft der ikke længere er bundet til en bestemt opgave. Den vender tilbage til helheden.",
        "Potency bevæger sig ikke som en partikel — den manifesterer sig som ændringer i feltet. At mærke potency i hænderne er at mærke tilstandsskift snarere end at mærke 'noget der bevæger sig'. Det skaber et andet sprog for det vi gør.",
    ],
    "16-ignition": [
        "Den første ignition skete ved unionens øjeblik, ved fødslen, ved første åndedræt. Det er ikke metafor — der er målbare tærskelfænomener i den embryonale udvikling der svarer til denne formulering. Hver tærskel er et 'lys-tændes' øjeblik.",
        "Re-ignition efter sygdom eller traume er ikke en restauration af det gamle — det er en ny ignition. Klienten kommer ikke 'tilbage' til som de var; de bevæger sig fremad til en ny baseline. Det er vigtigt ikke at forveksle de to.",
        "Når ignition ikke vil ske, er det sjældent fordi der mangler kraft. Oftere mangler der den indre tærskelbetingelse — en tilstand af tilstrækkelig hvile, tilstrækkelig sikkerhed, tilstrækkelig orientering. Vi tænder ikke ilden; vi forbereder brændet.",
    ],
    "17-axial-fluctuations": [
        "Aksiale fluktuationer følger ikke altid samme retning. Nogle gange er de overvejende cephal-caudale; andre gange er de spiralerende. At mærke retningen og dens variation er en finmotorisk evne der udvikles over år, ikke uger.",
        "Klienten oplever fluktuationerne forskelligt afhængigt af hvor i kroppen de mærker dem. I bækkenet ofte som vugning; i kraniet som let pres-forandring; langs columna som bølgende fornemmelse. Disse beskrivelser hjælper med at konfirmere hvad hænderne mærker.",
        "Når fluktuationerne er blokerede, mærkes de ofte som 'tør' eller 'klistret' kvalitet i vævet. Det er ikke en fagligt korrekt beskrivelse, men det er den behandlerens hænder ofte rapporterer. At give plads til denne fagligt-upræcise observation er en del af håndværket.",
    ],
    "18-wholeness": [
        "Wholeness er ikke et tilføjet begreb i biodynamikken — det er det første princip alle andre begreber forudsætter. Når Sutherland talte om 'helhedens orden', var det ikke filosofi; det var observation: kroppen organiserer sig fra helhed mod del, ikke omvendt.",
        "Når dele af kroppen 'føles separate', er det altid en relativ adskillelse, ikke en absolut. Helheden er der stadig, men dens kommunikationskanaler er sløret. Vores arbejde er at gøre de kanaler mærkbare igen, ikke at samle delene.",
        "Praktisk wholeness er ikke filosofi — det er en målbar observation: når én del bevæger sig, bevæger andre dele sig samtidigt og koordineret. Når denne koordination ikke findes, lokalt eller globalt, er der noget at lytte til.",
    ],
}


RUM_INSPIRATIONER = {
    "Rum A — Den Fysiske Krop": [
        "Det er fristende at se Rum A som det 'overfladiske' niveau, men det er en fejlforståelse. Den fysiske krop er ikke under de andre rum — den er det levende fundament hvorfra de andre rum udfolder sig. At ankre godt i Rum A er ikke begrænsning. Det er forudsætning.",
        "Nogle klienter når aldrig længere end Rum A i et behandlingsforløb. Det er ikke en mangel ved behandlingen. Det er hvad systemet kan rumme på det tidspunkt. Hvis vi presser videre, lukker vi det ned. Tålmodigheden ligger i at lade Rum A være nok når det er nok.",
        "Den hyppigste fejl i biodynamisk arbejde er at springe over Rum A på vej til 'noget dybere'. Klienten oplever det som distance — som om behandleren ikke er der hvor de er. Den dybeste behandling begynder altid med at hænderne hviler på den krop der faktisk er.",
    ],
    "Rum B — Væskekroppen": [
        "Væskekroppen i Rum B er ikke kun blod og lymfe — det er hele den fascielle interstitielle fluid-matrix. Det vi mærker når Rum B vågner er denne matrix der begynder at bevæge sig som en sammenhængende enhed snarere end som adskilte kompartments.",
        "Overgangen fra Rum A til Rum B mærkes ofte først som en kvalitetsændring i vævet. Det bliver 'vådere', mere flydende. Klienten beskriver det nogle gange som om de bliver tunge eller lette samtidigt. Det er paradokset ved væskekroppen — den har vægt og letvægt på én gang.",
        "Når Rum B nægter at vågne, er det oftest fordi nervesystemet endnu ikke har givet sin tilladelse. Væskekroppen er afhængig af parasympatisk dominans for at flyde frit. Hvis behandlingen forhastes, blokerer sympatisk aktivering den proces vi venter på.",
    ],
    "Rum C — Det Relationelle Felt": [
        "Rum C svarer biologisk til den ventral-vagale tilstand i Porges' polyvagal-teori — det system der opstår når vi sociale pattedyr mødes uden trussel. Det er ikke en metaforisk parallel; det er det samme system. Vi bygger på en eksisterende neurobiologisk arkitektur.",
        "I det relationelle felt bliver behandleren også ændret. Det er ikke en énvejsbevægelse fra os til klienten. Vi mærker noget i os selv vågne i takt med klientens åbning. At anerkende dette uden at lade vores eget materiale fylde feltet er en daglig disciplin.",
        "Når det relationelle felt overvælder klienten, er det ofte fordi det er længe siden de har været i et trygt felt. Selv det at føle sig set kan være krævende. Vores opgave er ikke at gå frem, men at give feltet plads og tid til at modne i sit eget tempo.",
    ],
    "Rum D — The Long Tide / Primary Respiration": [
        "De 100 sekunder er ikke en målbar konstant — Sutherland talte om 6-10 cyklusser pr 10 minut, Jealous formulerede 100 sekunder som vejledende. At håndtere denne variation kræver at vi holder tallet løst. Det er en pejling, ikke en definition.",
        "Læringen af at mærke Long Tide sker ikke gennem instruktion men gennem mentor-overlevering: en erfaren behandler holder hænderne med dig på en klient, og over tid genkender du det som han eller hun mærker. Det er en mundtlig tradition mere end en målbar færdighed.",
        "En vanskelig erkendelse: nogle gange tror vi at mærke Long Tide, men det er noget andet — en intern rytme i os selv, en forventning, en forestilling. At kunne skelne mellem det indre billede af Long Tide og den faktiske oplevelse er en del af modningen.",
    ],
    "Rum E — Dynamisk Stilhed": [
        "Dynamisk Stilhed er ikke en højere bevidsthedstilstand eller et behandlings-mål. Den dukker op nogle gange uden at vi har planlagt det, og den lader sig ikke trænes. Det meste arbejde sker i Rum A til D, og det er som det skal være.",
        "Når sproget rammer sin grænse i Rum E, bliver det fristende at gribe til store ord. Sutherland kaldte den den dynamiske stilhed bag al bevægelse; Becker talte om det dybeste fulcrum; Jealous om mødet med den oprindelige sundhed. Hver tradition har sit ord — fænomenet er det samme.",
        "Polyvagalt set er Rum E sandsynligvis en tilstand af dyb parasympatisk dominans med kohærent kardio-vaskulær respons. Det forklarer ikke fænomenet — men det forhindrer at vi forveksler dybde med transcendens. Klienten er ikke 'ude af kroppen'; nervesystemet hviler i sin grundtone.",
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
