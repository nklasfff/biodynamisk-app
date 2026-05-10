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
        "Dynamisk Stilhed mærkes ofte først som en ændring i hænderne — vævet holder op med at arbejde, pulsationer aftager til en tærskel hvor de næsten ikke er der. Klienten falder dybere. Tiden mister sit tempo. Det er i denne kvalitet at de stærkeste forvandlinger får plads.",
        "Stilheden er ikke kun det sjældne øjeblik hvor den viser sig — den er til stede gennem hele behandlingen som det grundlag al rytme udfolder sig fra. Vi mærker den ofte først bagefter, som det rum hvori alt det andet allerede har fundet sted.",
        "I Dynamisk Stilhed mister distancen mellem behandler og klient sin betydning. Hænderne er stadig hænder, kroppen er stadig krop, men adskillelsen som arbejdsantagelse træder midlertidigt tilbage. Det er ikke noget vi opnår; det er det vi opdager allerede er sket.",
        "I behandlingssituationen kommer stilheden ofte uden varsel — typisk efter at vævet har bevæget sig gennem flere lag og fundet et fælles rum. Klientens åndedrag falder, hænderne holder op med at registrere bevægelse, og noget i selve rummet forandrer kvalitet uden at man kan pege på hvad.",
        "Stilheden viser sig forskelligt afhængigt af klientens system. Hos den traumatiserede mærkes den ofte først som tøvende tilstedeværelse. Hos den udmattede som dyb hvile. Hos den åbne som klar genkendelse. Det er samme stilhed — men dens måde at vise sig på følger klientens egen indre tilgængelighed.",
        "Stilheden er ikke det modsatte af aktivitet — den er den tilstand hvor aktivitet og hvile rummer hinanden. Det betyder, at vi godt kan møde stilheden midt i intens proces, midt i klientens stærke følelser eller fysiske ubehag. Den er ikke betinget af ydre ro.",
        "Når Dynamisk Stilhed har vist sig under en behandling, fortsætter dens virkning ofte mange timer eller dage efter. Klienter beskriver det som en bæren, en orientering, en undertone af ro. Det er ikke en effekt vi har skabt; det er en kvalitet som har genfundet sin plads.",
    ],
    "02-breath-of-life": [
        "Breath of Life er ikke kun den første gnist — den er den samme kraft der hver dag organiserer dit liv. Den former cellerne, vedligeholder funktionen, mobiliserer helingen. Hvert åndedrag er en miniature af samme proces der dannede dig i de første ni måneder.",
        "Det fysiske åndedrag og Breath of Life er ikke det samme, selvom de mødes. Breath of Life fortsætter under søvnen, under bedøvelsen, gennem alle livets pauser. Den er den finere åndedragsproces der bærer livet selv, ikke bare lungerne.",
        "I behandlingen mærker vi Breath of Life som en kvalitet snarere end som rytme — noget der gennemstrømmer feltet uden at være lokaliseret. Klienter beskriver det nogle gange som 'et åndedrag der trækker vejret i mig'. Det er en præcis beskrivelse af det vi mærker.",
        "I behandlingssituationen viser Breath of Life sig ofte som en stille iver i feltet — som om noget længe har ventet på at få plads. Hænderne mærker det først som en svag pulserende kvalitet, så som en bredere bevægelse, og til sidst som en gennemstrømning der har sin egen retning.",
        "Breath of Life forveksles let med klientens almindelige åndedrag, men de bevæger sig på forskellige niveauer. Det fysiske åndedrag løber omkring 12-20 cyklusser i minuttet; Breath of Life manifesterer sig som langsommere bølger der ikke følger lungernes tempo og ikke ophører ved tilbageholdt åndedrag.",
        "Når vi forsøger at forklare Breath of Life for klienter, sker det ofte at de spontant genkender det — fra meditation, fra øjeblikke i naturen, fra dybe relationer. Det er ikke et fagligt fænomen alene; det er noget mange mennesker har mærket uden at have sprog for det.",
        "Breath of Life er aldrig fraværende, men den er ikke altid mærkbar for behandleren. Når vi ikke kan mærke den, er det sjældent fordi den er væk — oftere fordi vores eget system endnu ikke er stille nok til at registrere den. At lytte efter den er at gøre os modtagelige.",
    ],
    "03-primary-respiration": [
        "Primary Respiration manifesterer sig i flere rytmer på forskellige niveauer — den langsomste cyklus omkring 100 sekunder, en mellemste på 2-3 cyklusser i minuttet, og den hurtigste på 8-12. Hver rytme kalder på en anden kvalitet i lytten, og hver giver adgang til et andet niveau af systemet.",
        "Det er sjældent gennem instruktion vi lærer at mærke Primary Respiration. Det sker oftest gennem at sidde sammen med en mere erfaren behandler ved den samme klient — over tid genkender hænderne det andre hænder allerede mærker. Det er en mundtlig kunst, ikke en målbar færdighed.",
        "Nogle gange tror vi at mærke Primary Respiration, men det viser sig at være vores egen interne rytme — en forventning, et indre billede. At kunne skelne mellem den oplevede rytme og den faktiske kræver mange års modning. Det er en del af håndværket, ikke et mål man når.",
        "I behandlingssituationen begynder Primary Respiration ofte at træde frem først efter klienten er faldet til ro. De hurtige rytmer (CRI) viser sig først; den mellemste fluide tide derefter; Long Tide tit kun mod slutningen af en behandling. Tålmodighed er en del af perceptionen.",
        "Primary Respiration har en kvalitet af 'fyldighed' der adskiller den fra andre rytmer i kroppen. Hjerterytmen er kort og pulserende; åndedrættet er bredere men afgrænset; Primary Respiration har en bærende, gennemstrømmende karakter — som om hele organismen flytter sig let i takt med rytmen.",
        "Hos visse klienter er Primary Respiration vanskelig at mærke. Det er sjældent at den ikke er der — oftere at vævet er så bundet eller systemet så trækbart, at rytmen ikke har plads til at udfolde sig fuldt. At skabe det rum hvor den kan mærkes er ofte selve behandlingen.",
        "Når Primary Respiration ændrer karakter under en behandling — bliver bredere, dybere, mere koherent — er det et kliniske tegn på at noget integrerer sig. Det er ikke et resultat af vores intervention men en bekræftelse på, at det rum vi har holdt har givet plads til systemets egen organisering.",
    ],
    "04-midtlinjen": [
        "Midtlinjen er ikke kun den anatomiske akse — den er den oprindelige organiserende impuls der valgte hvad der skulle være op og ned, hvad der skulle være forrest og bagest. Denne impuls er fortsat aktiv i den voksne krop som det dybeste ordens-princip vi kender.",
        "Den følte midtlinje matcher ikke altid den anatomiske. Klienter kan have funktionelle midtlinjer der er forskudt af tidlige traumer — bækkenet et sted, hovedet et andet. At arbejde med flere parallelle akser samtidig er en del af klinisk virkelighed, ikke en undtagelse.",
        "Når midtlinjen er fragmenteret, mærker hænderne det som flere konkurrerende midter snarere end én samlet akse. Det er ikke et mål at 'rette dem'. Det er en lytten til hvor systemet selv bærer midten — og at lade den lange organisering mod én akse ske i sit eget tempo.",
        "I behandlingssituationen viser midtlinjen sig ofte som det første hænderne stiller sig i forhold til, når de lander. Vi mærker hvor den løber, om den er sammenhængende, om den er sløret eller klar. Resten af behandlingen organiserer sig ofte omkring denne første registrering af midten.",
        "Midtlinjen har forskellige kvaliteter i forskellige områder af kroppen. I bækkenet er den ofte tæt og jordet; i thorax bredere og mere bevægelig; i kraniet finere og mere lysende. At kunne mærke disse kvalitative forskelle er en del af det differentierede arbejde med aksen.",
        "Hos klienter med kronisk skoliose eller anden strukturel asymmetri er det vigtigt at huske at midtlinjen ikke er den samme som ryggen. Den anatomiske ryg kan være krum mens den funktionelle midtlinje organisatorisk er klar. At skelne mellem disse to lag åbner andre behandlings-muligheder.",
        "Midtlinjen er det punkt hvor højre og venstre møder hinanden. I behandlingen er det ofte gennem dette møde at integration sker — ikke ved at arbejde med enkelte sider men ved at lytte til hvor de to halvdele finder hinanden. Midten er ikke en linje men et møde.",
    ],
    "05-the-health": [
        "Sundheden er ikke fravær af sygdom — den er en aktiv organiserende kraft der bygger og vedligeholder hvert øjeblik. Også midt i den dybeste sygdom virker den under overfladen. Vores arbejde er ikke at tilføje sundhed; den er der, og venter på at få plads.",
        "At starte fra sundheden snarere end fra symptomet er en faglig disciplin. Det ændrer hvilke informationer hænderne mærker, hvilke spørgsmål vi stiller, hvor vi lader vores opmærksomhed hvile. Det er ikke optimisme. Det er en præcis arbejdsmåde, der åbner et andet behandlingsfelt.",
        "Når klienten oplever sig så syg at sundheden synes umulig, behøver vi ikke vente på at de finder den. Vi arbejder fra antagelsen om at den findes, og lader vores hænder hvile et sted hvor den endnu kan ses. Selv et lille felt af sundhed er nok udgangspunkt.",
        "I behandlingssituationen viser sundheden sig ofte først som en kvalitet i et område hvor klienten ikke har klager. Hænderne søger ikke det smertende sted først — de finder først det ubelastede, det levende, det organiserede. Derfra åbnes resten af systemet.",
        "Sundheden har en kvalitet der adskiller sig fra blot fravær af belastning. Hænderne mærker den som let, koherent, sammenhængende — vævet bevæger sig som ét felt snarere end som adskilte dele. Det er en specifik perception der udvikles over tid.",
        "Hos klienter med kronisk sygdom kan sundheden være tilsløret men ikke væk. Den findes ofte længere væk fra symptomet end vi forventer — i et område der virker uberørt, i en kvalitet af vejrtrækningen, i et roligt sted i feltet. Den ligger ikke skjult; den ligger uden for det vi normalt kigger.",
        "Når sundheden begynder at folde sig ud under en behandling, sker det ofte gradvist. Først som en lille ændring i vævs-tonen; så som bredere bevægelighed; så som en kvalitativt anderledes oplevelse for klienten. Vi følger denne udfoldelse mere end vi initierer den.",
    ],
    "06-motion-present": [
        "Motion Present er ikke én bevægelse men et væv af mange — celler der pulserer, autonome rytmer, fluide bølger, primære åndedragsmønstre. At lytte til dem alle samtidig uden at vælge én er en disciplin: vi bliver ikke specialister i én rytme men generalister i bevægelsens fylde.",
        "Når Motion Present pludselig falder næsten til nul, er det sjældent tomrum — oftere er vi tæt på et stillpoint eller The Neutral. Når den stiger i intensitet, har systemet ofte fundet noget at arbejde med. Begge tilstande er informative og kalder hver sin lytten.",
        "At se efter Motion Present er ikke det samme som at lede efter den. Når vi leder, sender vi små signaler ind i feltet og forstyrrer det vi forsøger at mærke. Lytten har en helt anden kvalitet — den modtager uden at sende, og det vi mærker er anderledes.",
        "I behandlingssituationen er Motion Present det første hænderne registrerer når de lander. Den fortæller med det samme om systemets aktuelle tilstand: om det er roligt eller aktiveret, om bevægelsen er fri eller bundet, om de forskellige lag bevæger sig sammen eller adskilt fra hinanden.",
        "Motion Present har en signatur i hver enkelt klient. Nogle har en hurtig, let bevægelseskvalitet; andre en langsom, dyb. Nogle bevæger sig overvejende horisontalt; andre vertikalt. At lære en klients individuelle bevægelsessignatur er en del af det relationelle arbejde over tid.",
        "Når én del af kroppen pludselig holder op med at bevæge sig, mens resten fortsætter, er det et tegn på lokal organisation eller bunden potency. Det er sjældent en mangel på liv — det er liv der er bundet til en bestemt opgave. At lytte til denne lokale stilhed åbner ofte for det videre arbejde.",
        "Motion Present skifter karakter i overgangene mellem de fem rum. I Rum A er den lokal og fysisk; i Rum B fluide og bredere; i Rum C deler den sig mellem klient og behandler; i Rum D bliver den universel; i Rum E hviler den i sig selv. At mærke disse skift orienterer os.",
    ],
    "07-fulcrum": [
        "Fulcrums er ikke faste anatomiske punkter — de bevæger sig, opløses, dannes nye. Når et fulcrum spontant flytter sig under hænderne, har systemet selv valgt næste fokus. Vores opgave er ikke at følge med fysisk men at give plads i opmærksomheden.",
        "Når vi sætter os ved et dysfunktionelt fulcrum og arbejder med det, sker der ofte mindre end vi forventer. Når vi i stedet sætter os ved sundhedens fulcrum og bliver der, organiserer det belastede område sig spontant mod balance. Det er ofte hurtigere end direkte intervention.",
        "Behandleren er også et fulcrum i feltet. Den måde vi sidder, den måde vi lytter, den ro vi har — alt det bliver et omdrejningspunkt klientens system kan organisere sig omkring. At blive et stille, stabilt fulcrum er måske vores vigtigste tekniske bidrag.",
        "I behandlingssituationen finder hænderne ofte et primært fulcrum først — et sted hvor systemet selv organiserer sig. Det kan være et helt andet sted end klagepunktet. Resten af behandlingen organiserer sig ofte rundt om dette første fulcrum, og det er værd at blive der længe.",
        "Fulcrums har forskellig karakter hos forskellige klienter. Hos den hyperaktive er de ofte for mange og for bevægelige; hos den nedlukkede er de få og rigide. Hos den balancerede er der få men dybt forankrede fulcrums omkring midtlinjen. Klientens fulcrum-mønster fortæller om systemets aktuelle organisering.",
        "Når et dysfunktionelt fulcrum slipper, er det ofte mærkbart i hele kroppen samtidig. Klienten kan opleve det som et 'fald', en 'lettelse', en pludselig udglatning af spændinger der ikke nødvendigvis var lokaliseret til det område. Det er en bekræftelse på at fulcrums ordner mere end deres umiddelbare område.",
        "Fulcrums findes på flere skalaer samtidigt. På cellulært niveau organiserer hver celle sig omkring et fulcrum; på lokalt niveau finder ledforbindelser deres dynamiske centrum; på global skala bevæger hele kroppen sig omkring sit samlede tyngdepunkt. At lytte på flere niveauer giver et rigere billede.",
    ],
    "08-stillpoints": [
        "Stillpoints sker på alle niveauer af systemet — i et lille fascialag, i hele den fluide krop, i Long Tide. Et stillpoint i Long Tide er kvalitativt anderledes end et i den hurtige rytme: dybere, mere altomfattende, ofte ledsaget af et autonomt skift.",
        "Det der følger efter et stillpoint er lige så vigtigt som selve punktet. Bevægelsen genoptages ofte med ny kvalitet — som om systemet har genvejet sig selv. Mange terapeutiske ændringer manifesterer sig først her, ikke i selve pausen. Lyttetid efter er ikke spildt tid.",
        "Klienter beskriver stillpoints meget forskelligt — som fald, som svæven, som klarhed der pludselig kommer. Det fælles træk er at noget sker uden anstrengelse. Klientens beskrivelse hjælper os med at konfirmere hvad hænderne mærker — det er en del af lytningen.",
        "I behandlingssituationen kommer stillpoints ofte i en bestemt rækkefølge — først lokale, så bredere, så hele systemet. Mod slutningen af en god behandling kan der opstå en serie stillpoints i Long Tide som synes at organisere alt det foregående. Det er ikke tilfældigt; det er rytmisk.",
        "Forskellen mellem en induceret og en spontan stillpoint mærkes tydeligt i hænderne. Den inducerede har en bestemt karakter — vi har skabt en pause. Den spontane føles som om systemet selv har valgt det. Klinisk er den spontane oftest mere transformativ, fordi systemets eget timing er respekteret.",
        "Stillpointens dybde mærkes på hvor stille hænderne bliver. Et overfladisk stillpoint efterlader stadig nogle pulseringer mærkbare. Et dybere fjerner næsten al rytme. Det dybeste — i Long Tide — opleves som om alt vævet holder vejret samtidigt. Hver dybde har sin egen karakter.",
        "Hos klienter der har gennemlevet meget, kan stillpoints være ledsaget af følelser eller minder der pludselig løsnes. Hos andre er de stille i sig selv — bare en pause. Det er ikke et tegn på dybde at meget kommer op; det er bare en forskel i hvordan systemet afgiver det det har båret.",
    ],
    "09-transmutation": [
        "Transmutation er ikke metafor men en mærkbar ændring i vævets kvalitet. Det der var tæt og rigid bliver flydende og levende. Hænderne registrerer det ofte først som en ændret modstand, så som en ny bevægelighed, og til sidst som en helt anden tonalitet i feltet.",
        "Den synlige transmutation går ofte gennem en mellemtilstand — fra rigid struktur til væskelignende kvalitet, og derfra til noget endnu mere flydende. Hvert lag tager den tid det tager. At springe et lag over forvandler ikke; det dækker bare over.",
        "Når transmutation er ufuldstændig, er det sjældent at processen er stoppet — oftere at den arbejder i et lag vi ikke kan mærke endnu. Helingen sker stadig, men i sit eget tempo og i sit eget rum. Vores tålmodighed er det stærkeste redskab vi har her.",
        "I behandlingssituationen mærker hænderne transmutation som flere lag der løsner sig efter hinanden. Først kan der være modstand der opløses; så en anden kvalitet der træder frem; så en tredje. Hvert lag tager den tid det tager. At lade hver fase være færdig før den næste begynder er essentielt.",
        "Transmutation har forskellig karakter i forskellige vævs-typer. I muskel-fascia mærkes den som blødgøring og udvidelse; i ledforbindelser som ny bevægelighed; i organer som fornyet rytmisk pulsering; i nervesystem som dybere ro. Hver vævstype taler sit eget sprog i transmutationsprocessen.",
        "Transmutation kan både mærkes og 'vides' uden at man helt kan beskrive det. Hænderne registrerer noget, og samtidig opstår en indre genkendelse hos behandleren — en uudtalt sikkerhed på, at noget er ændret. Begge informationer er gyldige og ofte nødvendige sammen.",
        "Transmutation kommer ofte i kølvandet på frigivelse af bound potency. Når kraften slipper sin lokale opgave, er der pludselig 'noget at arbejde med', og vævet får mulighed for at omorganisere sig. De to fænomener er knyttet sammen — frigjort potency er det der gør transmutation mulig.",
    ],
    "10-the-neutral": [
        "The Neutral forveksles let med afslapning, men er noget andet. Afslapning er en reduktion af spænding; The Neutral er en samling af alle systemers aktivitet i et fælles centrum. Klienten er ikke 'slap' — de er fuldt til stede, bare uden distance til sig selv.",
        "The Neutral er en præ-betingelse, ikke et mål. De dybeste behandlingsprocesser begynder først NÅR The Neutral er etableret. Behandlingen før den er forberedelse; behandlingen efter er det reelle arbejde. At gennemskue forskellen er en del af klinisk modenhed.",
        "Mange behandlinger lykkes ikke med at nå The Neutral, og det er som det skal være. Den er ikke noget vi kan fremtvinge; den dukker op når betingelserne er der. At kræve den er at lukke den ude. At vente på den er ofte det mest virksomme.",
        "Vi genkender indgangen til The Neutral ved en samlet kvalitetsændring. Hænderne mærker en bredere koherens, klientens åndedrag bliver dybere men roligere, det relationelle felt bliver klarere. Det er ikke ét tegn — det er flere små signaler der lægger sig sammen i et samlet billede.",
        "Forskellige klienter kommer til The Neutral via forskellige veje. Nogle gennem afslapning af nervesystemet; nogle gennem fluide skift; nogle gennem relationel tryghed; nogle pludselig som om noget falder på plads. At kende klientens vej hjælper med ikke at tvinge en bestemt route der ikke passer.",
        "Når The Neutral er etableret, mærker hænderne en stabilitet i feltet der ikke før var der. Klientens system bevæger sig som ét snarere end som dele. Behandlerens egne hænder bliver mere stille af sig selv. Tiden bliver mindre presserende. Disse er ikke tilfældige sammenfald.",
        "The Neutral og det fænomen der kaldes Holistic Shift er to sider af samme sag. Holistic Shift er det biologiske udtryk — autonome skift, åndedrags-ændring, hjerterytme-koherens. The Neutral er den oplevede kvalitet — det stille rum hvor alt finder sammen. De forekommer altid sammen.",
    ],
    "11-automatic-shifting": [
        "Automatic Shifting demonstrerer at systemet selv bestemmer rækkefølgen af heling. Hvad der ser kaotisk ud er sjældent kaos — det er en intelligens vi ikke kan forudsige. Vores rolle er ikke at organisere processen men at holde plads til den valgte rækkefølge.",
        "Når shifting går hurtigt fra område til område, kan det føles som om der ikke 'sker noget'. Men noget af det dybeste arbejde sker netop her — systemet ordner relationer mellem dele snarere end at arbejde lokalt. At blive i åbenheden kræver disciplin.",
        "Behandlerens største fristelse i Automatic Shifting er at gribe ind med teknik. Vi vil hjælpe noget. Men oftest hjælper vi mest ved at trække vores intention tilbage og lade processen styre. Det er ofte først bagefter at meningen viser sig.",
        "I behandlingssituationen ses Automatic Shifting ofte som hænderne der pludselig bliver opmærksomme på et nyt sted. Det område vi var ved føles 'mæt' eller 'færdigt'; et andet område kalder. Det er ikke vores valg — det er systemets valg, som vi følger snarere end leder.",
        "Shifting-mønstre varierer mellem klienter. Nogle skifter hurtigt og let mellem mange områder; andre har lange perioder ved samme sted før et skift kommer. Der er ikke ét rigtigt mønster — hvert system har sit eget tempo, og det er informativt om hvor klienten aktuelt arbejder fra.",
        "Når shifting går i ring og vender tilbage til samme områder igen og igen, er det ofte fordi noget endnu ikke er klar til at slippe. Vi lader processen vende tilbage; ofte sker der noget på det femte besøg som ikke skete på det første. Tålmodighed har sin egen virkning.",
        "Når Automatic Shifting holder op midt i en behandling og hænderne 'sidder fast' et bestemt sted, er det værd at lytte længere her. Ofte er der ikke et nyt skift fordi noget dybt er ved at organisere sig på det aktuelle sted. At blive er en del af processen, ikke en fejl.",
    ],
    "12-den-iboende-behandlingsplan": [
        "Disciplinen ved ikke at have en plan er sværere end den lyder. Vores uddannelse har trænet os i at observere, vurdere, vælge intervention. At slippe alt det er ikke at blive passiv — det er at flytte tilliden fra vores plan til systemets egen.",
        "At læse den iboende plan kræver dyb stilhed i behandleren. Når vi har en agenda, hører vi vores agenda; når vi er stille, hører vi planen. Den bliver ofte først tydelig efter at vi har sluppet vores eget greb om hvor det skal hen.",
        "Den iboende plan kan inkludere ubehag — smerte, følelser, midlertidig dysregulering. Vi må kende forskellen mellem nyttig smerte (transmutation, der hører til processen) og overvældelse (der ikke gør). Når planen leder gennem ubehag, er udfordringen at holde plads uden at lindre væk.",
        "Den iboende plan viser sig sjældent i begyndelsen af en behandling. Først efter klienten er faldet til ro, efter de første lag er mødt, begynder retningen at træde frem. At vente på den uden at presse er en del af det at lade planen styre. Den kommer når den kommer.",
        "Hos nogle klienter er den iboende plan tydelig fra første berøring; hos andre er den sløret af mange års kompensation eller traumer. Når planen er sløret, bliver vores opgave først at hjælpe systemet med at lytte til sig selv igen. Det er ofte den længste del af arbejdet.",
        "Når vi følger den iboende plan, er der en kvalitet af 'lethed' i behandlingen — vi behøver ikke skubbe, vi behøver ikke vælge. Når vi i stedet er begyndt at indføre vores egen plan, mærkes det som modstand: vævet svarer ikke, klienten bliver mere distanceret, hænderne 'kæmper' med at finde retning.",
        "Når vi kortvarigt overhører den iboende plan og indfører vores egen retning, kan vi mærke det med det samme — feltet bliver fladere, mindre koherent. Korrektionen er ikke at gøre noget anderledes, men at trække opmærksomheden tilbage til at lytte. Planen er stadig der.",
    ],
    "13-fluid-body": [
        "Vi var primært væske før vi blev fast væv. I de første uger efter unionen er kroppen ren væske — celler der svømmer i fluid medium, der gradvist organiseres. Den primære væske-natur forsvinder aldrig; den bliver bare struktureret. Den kan vækkes igen.",
        "Når Fluid Body vågner, mærker hænderne det ofte først som en kvalitetsændring i vævet — det bliver 'vådere', mere flydende. Klienten beskriver det som om de bliver tunge og lette samtidigt. Det er væskens paradoks: den har vægt og letvægt på én gang.",
        "Når Fluid Body føles låst, er det sjældent at væsken er væk — den er bare ikke i bevægelse. Det vi lytter efter er det første tegn på at strømmen begynder igen. Det første tegn er ofte mindre end vi forventer; en lille kvalitetsændring er nok at følge.",
        "I behandlingssituationen mærkes Fluid Body ofte først som en ændret hånd-fornemmelse. Vævet under fingrene bliver mindre 'tørt', mere 'levende'. Det er ikke noget vi kan fremtvinge — det viser sig når klientens system har givet sin tilladelse, ofte gennem etablering af The Neutral.",
        "Hos sportsudøvere og kropsvante klienter er Fluid Body ofte hurtigt tilgængelig — vævet er allerede vant til at bevæge sig som ét felt. Hos klienter der har levet i meget hovedfokuseret tilstand, kan det tage længere tid for væsken at samle sig. Det er ikke et tegn på dybde, kun på vej.",
        "Når Fluid Body træder ind, ændrer hænderne ofte deres positionering af sig selv. Det vi før mærkede lokalt — en spænding her, en tæthed der — bliver pludselig dele af et større fluid felt. Vores fokus udvider sig fra punktet til feltet, fordi det er det som klienten nu er.",
        "Vævet husker sin fluid-oprindelse selv mange år efter, det er blevet 'tørt'. Når Fluid Body vågner, er det ikke en ny tilstand — det er en gammel tilstand der genfindes. Hænderne mærker det som noget der allerede vidste det skulle være sådan; klienten beskriver det ofte som genkendelse.",
    ],
    "14-the-lesion-field": [
        "Læsionsfeltet er ikke en fejl. Det er livskraft der har gjort det bedste den kunne under de vilkår der var. At se det som beskyttelse, ikke fejl, ændrer behandlingens grundtone fundamentalt — fra at ville fjerne noget til at anerkende det der allerede er.",
        "Læsionen er ikke et sted men en proces. Feltet vedligeholder sin egen organisering med energi, og det kræver vores anerkendelse, ikke vores intervention, for at slippe sin opgave. Når det opdager at det ikke længere skal beskytte, vender potency tilbage til helheden.",
        "Når feltet ikke vil løslade, er det oftest fordi grundpræmissen — sikkerhed nu — endnu ikke er etableret. Det skridt kan vi ikke springe over. Først nervesystemets dybe besked om 'her er sikkert', så kan læsionen begynde at slippe sin beskyttelses-opgave.",
        "I behandlingssituationen mærkes læsionsfeltet ofte som et område hvor hænderne ikke 'kommer ind'. Der er en stilhed eller tæthed der adskiller sig fra resten af vævet. At blive ved feltets kant uden at presse er ofte den mest virksomme tilgang — feltet åbner sig når det selv er klar.",
        "Læsionsfelter har forskellig karakter. Nogle er små og dybt fokuserede; andre er store og diffuse. Nogle er akutte og levende; andre kroniske og stillestående. Klientens samlede mønster af læsionsfelter fortæller om systemets historie — hvad det har båret, hvor det har trukket sig tilbage.",
        "Når et læsionsfelt begynder at slippe, er der ofte en gradvis åbning af feltets kanter. Hænderne mærker først en blødgøring i kantområdet; så en udvidelse af feltet selv; så en tilbagevenden af bevægelse i området. Det sker sjældent pludseligt — oftere som en langsom omfordeling.",
        "Læsionsfeltet er stedet hvor potency er bundet. Når feltet slipper, er det fordi den bundne potency ikke længere er nødvendig at holde lokalt. Den vender tilbage til den almene cirkulation, og området får adgang til feltets samlede ressourcer igen. De to fænomener er det samme set fra to vinkler.",
    ],
    "15-potency": [
        "Bound potency findes overalt hvor systemet har skullet låse noget for at overleve. Free potency er det der er tilgængeligt for almen heling og vedligeholdelse. Når bound potency frigives, er det ikke 'mere kraft' — det er den oprindelige kraft der ikke længere er bundet til en opgave.",
        "Potency bevæger sig ikke som en partikel — den manifesterer sig som ændringer i feltet. At mærke potency i hænderne er at mærke tilstandsskift snarere end at mærke 'noget der bevæger sig'. Det skaber et andet sprog for det vi gør.",
        "Når bound potency slipper sin opgave, vender den ikke 'frem' til behandleren eller 'ud' af kroppen — den vender tilbage til helheden hvor den startede. Vi mærker ikke en strøm fra A til B. Vi mærker en omfordeling i feltet, en genfordeling af kraften.",
        "I behandlingssituationen mærker hænderne potency som en kvalitativ kraft i feltet snarere end som lokaliseret bevægelse. Det er som en intensitet eller koncentration der enten er åbent flydende eller bundet til et bestemt sted. Forskellen er en del af det første hænderne læser i en behandling.",
        "Potency har forskellig karakter afhængigt af hvor i organismen den er. I cerebrospinalvæsken mærkes den ofte som let og fluide; i fascia som tættere og strømmende; i organer som mere indeholdt. Klinisk lytter vi til disse kvalitative forskelle som information om systemets aktuelle organisering.",
        "Når potency mobiliseres fra en bunden tilstand, mærkes det ofte som en indre 'genåbning'. Hænderne registrerer en ændring i feltets kraft og retning. Klienten oplever det undertiden som varme, kuldegysninger, eller en svag elektrisk fornemmelse — det er feltet der genfordeler sin kraft.",
        "Potency manifesterer sig gennem Primary Respiration — den er det der bærer rytmen og giver den dens helbredende kraft. Når Primary Respiration er stærk og koherent, er potency tilgængelig; når rytmen er svag eller fragmenteret, er potency ofte bundet i lokale opgaver. De to fænomener er knyttet sammen.",
    ],
    "16-ignition": [
        "Vi har alle gennemlevet flere ignition-øjeblikke — ved unionens øjeblik, ved fødslen, ved første åndedrag, ved den fulde landing i kroppen i de første år. Hver ignition er en tærskel-overskridelse til ny biologisk organisering. Tærsklerne er aktive påmindelser om hvad kroppen kan.",
        "Re-ignition efter sygdom eller traume er ikke en restauration af det gamle — det er en ny ignition. Klienten kommer ikke 'tilbage' til som de var; de bevæger sig fremad til en ny baseline. Det er en vigtig skelnen for både behandler og klient.",
        "Når ignition ikke vil ske, er det sjældent fordi der mangler kraft. Oftere mangler tærskelbetingelserne — tilstrækkelig hvile, tilstrækkelig sikkerhed, tilstrækkelig orientering. Vi tænder ikke ilden; vi forbereder brændet. Når brændet er klart, kommer flammen af sig selv.",
        "I behandlingssituationen kommer ignition sjældent som planlagt — den dukker op når betingelserne er rette. Hænderne mærker en pludselig kvalitetsændring i feltet: noget tænder, noget begynder at gløde af sig selv. Det er et af de øjeblikke vi ikke kan forudbestille, men kun forberede.",
        "Ignition viser sig forskelligt afhængigt af, hvor i organismen den sker. I bækkenet mærkes den som en grundforankring; i hjertet som en udvidelse; i kraniet som en lyshed. Klientens egen oplevelse afspejler ofte præcis hvor i kroppen ignition har fundet sit sted, og det giver os en indikation.",
        "Når ignition lykkes, mærker hænderne ofte en 'opadgående' kvalitet i feltet — som om noget har genfundet sin orientering. Klienten beskriver det undertiden som lethed, klarhed, eller en mærkbar tilstedeværelse i et område der før følte sig fjern. Forandringen er typisk varig.",
        "Ignition og potency er knyttede fænomener. Ignition er det øjeblik, hvor bunden potency frigives og finder sit nye anvendelses-felt; potency er den substans, der gør ignition mulig. Vi kan ikke skille de to — uden potency ingen ignition; uden ignition ingen ny anvendelse af potency.",
    ],
    "17-axial-fluctuations": [
        "Aksiale fluktuationer følger ikke altid samme retning. Nogle gange er de overvejende fra coccyx mod kraniet, andre gange fra kraniet mod coccyx, andre gange spiralerende. At mærke retningen og dens variation er en finmotorisk evne der udvikles over år, ikke uger.",
        "Klienten oplever fluktuationerne forskelligt afhængigt af hvor i kroppen de mærker dem. I bækkenet ofte som vugning; i kraniet som let pres-forandring; langs columna som bølgende fornemmelse. Disse spontane beskrivelser hjælper med at konfirmere hvad behandlerens hænder allerede mærker.",
        "Når fluktuationerne er blokerede, mærkes de ofte som en tør eller klistret kvalitet i vævet. Det er ikke en fagligt korrekt beskrivelse, men det er den hænderne ofte rapporterer. At give plads til denne fagligt-upræcise observation er en del af håndværket — ikke en mangel.",
        "I behandlingssituationen mærkes axial fluctuations ofte tydeligst når klienten er i Rum B — i den fluide tilstand. Hænderne registrerer dem som en bølgende bevægelse langs aksen, og rytmen kan variere fra langsom og dyb til hurtigere og mere overfladisk afhængigt af klientens aktuelle organisering.",
        "Hos klienter med god midt-organisering er fluctuationerne ofte ensartede og rolige. Hos klienter med traumer eller fragmentering kan fluctuationerne være afbrudte, sprungne, eller helt manglende i visse zoner. Det fragmenterede mønster er ikke en fejl at rette — det er informativt om hvor vi skal lytte længere.",
        "Sunde axial fluctuations har en kvalitet af 'fyldighed' — bølgen bærer hele kropsbredden samtidigt og forbinder bækken med kraniet i én bevægelse. Når fluctuationerne er svage, er det ikke nødvendigvis et tegn på sygdom — bare på at systemet aktuelt arbejder på et andet niveau.",
        "Axial fluctuations og midtlinjen er afhængige af hinanden. Uden klar midtlinje fragmenteres fluctuationerne; uden fluctuationer mangler midtlinjen sin bevægelses-kvalitet. Når begge er til stede sammen, opleves kroppen som ét organiseret felt der både har form (midtlinje) og bevægelse (fluctuationer).",
    ],
    "18-wholeness": [
        "Embryologisk er kroppen aldrig blevet 'sat sammen af dele' — vi var aldrig dele først. Vi var en helhed der differentierede sig. Den primære helhed forbliver tilstede gennem hele livet som det organiserende princip vi kalder sundhed. Helhed er ikke en præstation; den er udgangspunkt.",
        "Praktisk wholeness er ikke filosofi — det er en målbar observation: når én del bevæger sig, bevæger andre dele sig samtidigt og koordineret. Når denne synkronicitet ikke findes, lokalt eller globalt, er der noget at lytte til. Det er ofte det første hænderne læser når de lander.",
        "Når dele af kroppen 'føles separate', er det altid en relativ adskillelse, ikke en absolut. Helheden er der stadig, men dens kommunikationskanaler er sløret. Vores arbejde er at gøre de kanaler mærkbare igen — ikke at samle delene, for de var aldrig adskilt.",
        "I behandlingssituationen er wholeness ofte det første hænderne registrerer når de lander — er feltet helt eller fragmenteret. Det fortæller med det samme om systemets aktuelle organisering. Resten af behandlingen organiserer sig ofte efter denne første registrering: hvor er helheden klar, hvor er den sløret.",
        "Klienter har forskellige profiler af wholeness. Nogle er fragmenterede i specifikke områder (typisk hvor traumer eller skader har skabt isolation); andre har generel diffus fragmentering; andre igen har god wholeness i kroppen men ikke i nervesystemet eller omvendt. Mønstret er ikke binært — det er nuanceret.",
        "Når wholeness reorganiserer sig under behandling, sker det ofte i bølger. Et område samler sig, så et andet, så et tredje. Til sidst er der en samlet kvalitet, hvor alle dele bevæger sig som ét. Det er et af de stærkeste signaler på, at den iboende behandlingsplan har gjort sit arbejde.",
        "Wholeness er forudsætningen for alle de andre begreber. Uden wholeness er der ikke noget felt at bevæge sig i; uden den er Primary Respiration, potency, midtlinjen alt sammen lokale fragmenter. Wholeness er ikke ét begreb blandt flere — det er den baggrund hvorpå alle de andre tegner sig.",
    ],
}


RUM_INSPIRATIONER = {
    "Rum A — Den Fysiske Krop": [
        "Det er fristende at se Rum A som det 'overfladiske' niveau, men det er en fejlforståelse. Den fysiske krop er ikke under de andre rum — den er det levende fundament hvorfra de andre rum udfolder sig. At ankre godt i Rum A er ikke begrænsning. Det er forudsætning.",
        "Nogle klienter når aldrig længere end Rum A i et behandlingsforløb. Det er ikke en mangel ved behandlingen. Det er hvad systemet kan rumme på det tidspunkt. Hvis vi presser videre, lukker vi det ned. Tålmodigheden ligger i at lade Rum A være nok når det er nok.",
        "Den hyppigste fejl i biodynamisk arbejde er at springe over Rum A på vej til 'noget dybere'. Klienten oplever det som distance — som om behandleren ikke er der hvor de er. Den dybeste behandling begynder altid med at hænderne hviler på den krop der faktisk er.",
        "I behandlingssituationen er Rum A oftest indgangen — den krop hænderne lander på. Vi mærker først vævets faste struktur, dets historie, dets kompensationer. Først når denne indgang er fuldt anerkendt, åbner systemet sig for de dybere lag. Rum A er ikke et trin der skal forlades, men en kvalitet der bliver.",
        "Forskellige klienter har forskellige profiler i Rum A. Atleten har et tonet, organiseret væv; den langtidssyge har tæt, beskyttende struktur; den traumatiserede har områder af adskilt væv. Profilen er informativ — den fortæller om systemets aktuelle organiseringsmønster og hvor lytten skal gå hen først.",
        "Når Rum A er fuldt mødt, ændrer vævet kvalitet. Hænderne mærker en større tilgængelighed — det fastsiddende blødgøres, det adskilte begynder at kommunikere. Klienten oplever det som en ankring i kroppen, en samling. Det er forudsætningen for at de andre rum kan åbne sig på en bæredygtig måde.",
        "Rum A er ikke det samme som overflade-anatomien. Den anatomiske skelet er udgangspunktet, men Rum A inkluderer hele den fysiske krops levende kvalitet — tone, vævs-tæthed, organisering, struktur, holdning. At lytte til Rum A er at lytte til det levende, ikke til formen.",
    ],
    "Rum B — Væskekroppen": [
        "Væskekroppen i Rum B er ikke kun blod og lymfe — det er hele kroppens samlede væskemiljø der begynder at bevæge sig som én sammenhængende enhed. Det vi mærker når Rum B vågner er denne matrix der træder ud af adskilte kompartments og bliver ét felt.",
        "Overgangen fra Rum A til Rum B mærkes ofte først som en kvalitetsændring i vævet. Det bliver 'vådere', mere flydende. Klienten beskriver det nogle gange som om de bliver tunge eller lette samtidigt. Det er paradokset ved væskekroppen — den har vægt og letvægt på én gang.",
        "Når Rum B nægter at vågne, er det oftest fordi nervesystemet endnu ikke har givet sin tilladelse. Væskekroppen er afhængig af parasympatisk dominans for at flyde frit. Hvis behandlingen forhastes, blokerer den sympatiske aktivering den proces vi venter på.",
        "I behandlingssituationen kommer overgangen til Rum B ofte gradvist. Først blødgøres vævet lokalt; så bredere; så bevæger hele organismen sig som ét fluid felt. Hænderne kan ikke fremtvinge denne overgang — de kan kun give plads til den. Klienten mærker det ofte før behandleren kan beskrive det.",
        "Hos klienter der lever meget i hovedet, kan Rum B være tilgængelig først efter længere arbejde. Hos klienter med god kropsforankring åbner den sig næsten automatisk når The Neutral er etableret. Hos klienter med lange traumer kan Rum B være beskyttet — adgangen til væsken er en tærskel der skal mødes med tålmodighed.",
        "Når Rum B er fuldt etableret, mærker hænderne en bredere koherens. Det er ikke længere kun lokale strukturer der bevæger sig, men hele organismen som én fluid enhed. Klientens åndedrag bliver dybere og mere langsomt; deres ansigt får ofte en blødere kvalitet. Disse er ikke tilfældige sammenfald.",
        "Rum B er forbindelsen mellem den faste krop (Rum A) og de subtile rum (Rum C-E). Uden Rum B kan vi ikke nå Long Tide-rummet — væskens åbning er den nødvendige passage. Det er en af de grunde, vi ikke springer rummene over: hver indeholder den foregående og forbereder den næste.",
    ],
    "Rum C — Det Relationelle Felt": [
        "Det relationelle felt er ikke metafor men biologi. Når to nervesystemer mødes uden trussel, opstår en målbar fælles regulering — det er det system der opstod blandt sociale pattedyr og som vi alle bærer. Vi bygger på en eksisterende neurobiologisk arkitektur, ikke på spirituel idé.",
        "I det relationelle felt bliver behandleren også ændret. Det er ikke en énvejsbevægelse fra os til klienten. Vi mærker noget i os selv vågne i takt med klientens åbning. At anerkende dette uden at lade vores eget materiale fylde feltet er en daglig disciplin.",
        "Når det relationelle felt overvælder klienten, er det ofte fordi det er længe siden de har været i et trygt felt. Selv det at føle sig set kan være krævende. Vores opgave er ikke at gå frem, men at give feltet plads og tid til at modne i sit eget tempo.",
        "I behandlingssituationen mærkes det relationelle felt ofte først som en ændret tilstedeværelse i rummet. Klienten og behandleren begynder at åndedrætte i en bestemt rytme uden at planlægge det. Hænderne mærker en bredere koherens. Noget tredje — som ingen af os bringer alene — opstår i samspillet.",
        "Det relationelle felts kvalitet varierer mellem behandlinger. Nogle gange er det stille og tilbagetrukket; andre gange aktivt og bevægeligt; andre gange ladet med følelser eller minder. Hver kvalitet er informativ om klientens aktuelle behov. Det er ikke noget vi vælger — det er noget der opstår mellem os.",
        "Når det relationelle felt er fuldt etableret, ophører rolle-skellet midlertidigt. Behandleren er ikke længere 'den der gør'; klienten er ikke længere 'den der modtager'. Begge er deltagere i et fælles felt. Det er sjældent vi taler om dette under behandlingen — det mærkes, det udfolder sig, det forsvinder igen.",
        "Rum C adskiller sig fra både Rum A og Rum B ved at involvere to nervesystemer i stedet for ét. Det er ikke længere klientens system alene der bærer behandlingen; det er feltet mellem os. Det stiller andre krav til behandleren — vi skal kunne være distinkte og åbne på samme tid.",
    ],
    "Rum D — The Long Tide / Primary Respiration": [
        "De 100 sekunder er ikke en målbar konstant. Cyklusserne kommer i et bredere spektrum — nogle gange 80, nogle gange 120 — og varierer fra klient til klient og fra øjeblik til øjeblik. Tallet er en pejling, ikke en definition. Hvad vi lytter til er rytmens natur, ikke dens præcision.",
        "Læringen af at mærke Long Tide sker ikke gennem instruktion. Det sker oftest ved at sidde sammen med en mere erfaren behandler ved den samme klient — over tid genkender hænderne det andre hænder allerede mærker. Det er en mundtlig tradition, ikke en målbar færdighed.",
        "En vanskelig erkendelse: nogle gange tror vi at mærke Long Tide, men det er noget andet — en intern rytme i os selv, en forventning, en forestilling om hvordan det skal føles. At kunne skelne mellem det indre billede og den faktiske oplevelse er en del af modningen.",
        "I behandlingssituationen kommer Long Tide sjældent som det første rum vi besøger. Den åbner sig oftest mod slutningen af en behandling, efter de andre rum har gjort deres arbejde. Hænderne mærker en udvidelse af opmærksomheden — fra kroppen til rummet til horisonten. Det er en perception der udvikler sig over tid.",
        "Forskellige klienter oplever Long Tide forskelligt. Nogle mærker den som en stor bølgende bevægelse; andre som en stille ankring; andre igen som en udvidelse af kroppens grænser. Disse beskrivelser hjælper os ikke med at validere eller invalidere — de er bare informative om hvordan klientens system er åbent for det universelle.",
        "Når Long Tide er stærk og koherent, opleves hele behandlingen som båret af noget større. Hænderne behøver næsten ikke gøre noget; klienten falder dybere af sig selv; tiden mister sit tempo. Det er en kvalitet der adskiller sig markant fra arbejdet i de andre rum — bredere, langsommere, mere altomfattende.",
        "Long Tide forbinder den enkelte organisme med noget større — det universelle felt af Primary Respiration. Det er ikke metafor: rytmen er den samme der bevæger sig gennem hele biosfæren. At mærke den er at mærke at klientens organisme aldrig var separat fra livets samlede åndedrag, kun en lokalisering af det.",
    ],
    "Rum E — Dynamisk Stilhed": [
        "Dynamisk Stilhed er ikke en højere bevidsthedstilstand eller et behandlings-mål. Den dukker op nogle gange uden at vi har planlagt det, og den lader sig ikke trænes. Det meste arbejde sker i Rum A til D, og det er som det skal være. Rum E er bonus, ikke mål.",
        "Når sproget rammer sin grænse i Rum E, bliver det fristende at gribe til store ord. Men ord er ord. De peger og svigter. Det vigtigste er ikke ordet vi vælger — kærlighed, mysteriet, nåde, tilstedeværelse — men at vi ikke forveksler ordet med fænomenet.",
        "Rum E er det rum der har været til stede under alle de andre. Da vi i Rum A mærkede vævets historie, var stilheden allerede der. Den dukker bare ikke altid op i forgrunden. Når den gør, er det som om noget kort har ladet sig se af sig selv.",
        "I behandlingssituationen viser Dynamisk Stilhed sig sjældent på vores invitation. Den dukker op når alle de andre rum har gjort deres arbejde — eller indimellem helt uden den foregående proces. Hænderne mærker en samlet stilhed der ikke er fravær men en kvalitet der bærer alt det øvrige.",
        "Klienter beskriver mødet med Dynamisk Stilhed forskelligt. Nogle som dyb hvile; andre som klarhed; andre som genkendelse af noget de altid har vidst. Beskrivelserne varierer, men den fælles kvalitet er at noget hviler i sig selv — uden at klienten føler sig adskilt fra det.",
        "Effekterne af Dynamisk Stilhed kan vare længe efter behandlingen. Klienter rapporterer ofte en undertone af ro de næste dage eller uger — som om noget har genfundet sin baseline. Det er ikke en effekt vi har skabt; det er en kvalitet der har fået plads til at vise sig.",
        "Dynamisk Stilhed er det rum hvori alle de andre rum hviler. Den er ikke et af de fem — den er den baggrund de fire andre udfolder sig på. Rum A til D har deres egne kvaliteter, men de bæres alle af stilheden. At mærke den er at mærke det grundlag al behandling allerede står på.",
    ],
}


STADIE_INSPIRATIONER = {
    "01-foerste-stadie": [
        "Det første stadie mærkes ofte som en kropslig anspændthed — skulderne sidder oppe, nakken er stiv, åndedrættet er overfladisk. Vi forsøger at forstå med hovedet og mister kontakten med hænderne. Oplevelsen af at 'gøre det rigtigt' presser sig ind i hver eneste behandling vi giver.",
        "Behandlere i første stadie har ofte en oplevelse af at svinge mellem dage med klarhed og dage med tvivl. Den ene dag mærker vi alt med sikkerhed; næste dag føles hænderne fremmede. Disse svingninger er ikke tegn på inkompetence — de er tegn på at sansningen endnu ikke har fundet sin baseline.",
        "I første stadie bruger vi mange teknikker. Hver klagepunkt får sin egen tilgang, hver behandling sin egen plan. Det er ikke en fejl — det er en nødvendig fase af læringen. Det er gennem teknikkernes mangfoldighed at vi senere bliver i stand til at slippe dem og bare være til stede.",
        "Overgangen fra første til andet stadie viser sig ofte som tøvende pauser i den mentale aktivitet. Mens vi behandler, opstår der pludselig et mellemrum — vi havde en plan, og så blev den væk. I begyndelsen er det skræmmende; senere bliver det det vi venter på.",
        "Første stadie er ikke noget vi vokser fra — det er noget vi vokser igennem. Hver ny behandlingsstil, hvert nyt fagligt område, hver gang vi møder en klient med en ny problemstilling, kan vi befinde os i første stadie igen. Det er ikke regression. Det er den dybde læring kræver.",
        "Selv erfarne behandlere genkender første stadie hos sig selv på særligt udfordrende dage. Når vi er trætte, presset, eller møder noget der overrasker os, kan tankestrømmen vende tilbage. At kunne genkende det uden at dømme os selv er en del af det at være i stadiet uden at være fanget i det.",
        "Første stadie giver fundamentet. Det vi lærer her — anatomi, teknik, faglig orientering — bliver det ankerpunkt vi senere kan slippe fra. Uden første stadies disciplinerede arbejde har de senere stadier ikke noget at hvile på. Den intense søgen er ikke uden formål; den bygger den substans hvorfra slipperne kan blive bæredygtige.",
    ],
    "02-andet-stadie": [
        "I andet stadie begynder vi at mærke væske-kvaliteter i hænderne. Vævet er ikke længere kun fast og lokalt — der er noget der bevæger sig som én sammenhængende strøm. Det første tegn er ofte en uventet 'fugtighed' eller 'flydenhed' under fingerspidserne, hvor vi før kun mærkede struktur.",
        "Pauserne i den mentale aktivitet bliver mere stabile. Vi kan sidde ved en klient i flere minutter uden at planlægge eller analysere. I stedet er der bare en lytten. Det føles ofte uvant i begyndelsen — som om noget mangler — men over tid bliver det den tilstand vi længes efter at vende tilbage til.",
        "I andet stadie begynder Primary Respiration at træde frem. Den er der ikke som en idé længere — den er der som en faktisk perception. Hænderne registrerer en langsom rytme der ikke følger åndedrættet eller hjerteslaget. Først som en svag fornemmelse; senere som en tydelig bæren.",
        "Behandlinger i andet stadie bliver mindre tekniske og mere lyttende. Vi har stadig vores faglige redskaber, men de bruges sjældnere. I stedet bliver vores grundholdning at vente på det systemet selv vil. Det er ofte i denne fase at klienter rapporterer 'noget anderledes' uden at kunne sætte ord på det.",
        "Andet stadie er sårbart. Vi har sluppet en del af det første stadies sikkerhed (planen, teknikken), men har endnu ikke fuld tillid til det vi mærker. Tvivl og selvbebrejdelse kan være intense. At blive ved med at lytte trods tvivlen er det der gradvist styrker den nye kapacitet.",
        "Overgangen til tredje stadie sker når vi opdager at klienten ikke længere er en isoleret enhed for os. Feltet mellem os bliver mærkbart. Det er ikke længere kun deres krop vi behandler — vi er begge i et fælles rum. Først er det skræmmende; senere bliver det selve behandlingen.",
        "Andet stadie kan strække sig over mange år. Det er ikke en fase vi 'kommer igennem' hurtigt. Hver ny dybde i mødet med klienter åbner nye muligheder for at lytte til væsken og rytmerne. Det er ikke ineffektivt — det er det stadie hvor håndværket modnes til kunst.",
    ],
    "03-tredje-stadie": [
        "Tredje stadie begynder ofte med en uventet oplevelse — vi mærker at klientens åndedrag og vores eget følges ad uden at vi har planlagt det. Det er ikke synkronisering som teknik; det er biologisk co-regulering. Det første tegn er ofte at behandlingen pludselig virker mindre vores og mere fælles.",
        "I tredje stadie ophører distinktionen mellem 'hvad vi giver' og 'hvad vi modtager' midlertidigt. Vi bliver lige så meget ændret af behandlingen som klienten. Det er ikke en svaghed eller grænseoverskridelse — det er hvordan det relationelle felt fungerer. At anerkende det uden at være bange for det er en del af stadiet.",
        "Behandlere i tredje stadie mærker ofte deres egne følelser, kropslige fornemmelser eller minder dukke op under sessioner. Det er ikke nødvendigvis vores eget materiale — det kan være feltets respons. At kunne skelne mellem det der hører til klienten, til feltet, og til os selv, er en finmotorisk færdighed der udvikles over tid.",
        "I tredje stadie ændrer behandlinger sig kvalitativt. De bliver mindre fokuserede på lokale problemer og mere på hele organismens orientering. Klienten kommer ofte ud af sessionen med en oplevelse der er svær at sætte ord på — 'noget skiftede', 'jeg blev set', 'vi mødte hinanden'. Det er feltets virkning, ikke teknikkens.",
        "Risikoen i tredje stadie er at miste sig selv i feltet. Når grænserne mellem behandler og klient bliver fluide, kan vi tabe vores eget anker. Klinisk modenhed i tredje stadie er at kunne være distinkt og åben på samme tid — at have en stemme, der kan holde feltet, samtidig med at den ikke fylder feltet.",
        "Overgangen til fjerde stadie sker når feltet ikke længere kun er mellem os og én klient, men begynder at åbne sig mod det universelle. Vi mærker at det vi sidder i ikke er begrænset til denne person, dette rum, dette øjeblik. Det er en gradvis udvidelse, ikke et pludseligt skifte.",
        "Tredje stadie giver behandleren en helt anden form for trættet. Det er ikke fysisk udmattelse fra mange klienter — det er feltets vægt. At være i intim relationel kontakt med menneske efter menneske kalder på en restitution der ikke er bare hvile. Det er en del af håndværket at kunne genoplade på det relationelle plan.",
    ],
    "04-fjerde-stadie": [
        "Fjerde stadie begynder ofte med en oplevelse af at noget bærer behandlingen — ikke os, ikke klienten, men noget større. Vores opmærksomhed udvider sig fra kroppen til rummet til horisonten. Long Tide bliver ikke længere noget vi prøver at mærke, men det grundlag al perception finder sted i.",
        "I fjerde stadie behandler vi mindre og mindre. Hænderne hviler stadig, klienten ligger stadig, men det 'arbejde' vi før gjorde, gøres ikke længere. I stedet sker der noget der ikke kan tilskrives os eller dem. Det er ofte den dybeste behandling vi kan tilbyde, og samtidig den der kræver mindst aktiv handling.",
        "Tiden ændrer karakter i fjerde stadie. Behandlinger kan vare i et halvtimes ur og samtidig opleves som timer. Eller de kan vare to timer og opleves som minutter. Både klient og behandler oplever ofte denne tids-dilatation, og det er informativt — det er et tegn på at vi er i Long Tide-rummets felt.",
        "Behandlere i fjerde stadie taler ofte mindre om teknik og mere om perception. Når vi forklarer hvad vi gør, bruger vi ord som 'lytte', 'rumme', 'være med'. Tekniske termer bliver irrelevante — ikke fordi de er forkerte, men fordi de ikke længere beskriver hvad der faktisk sker i sessionen.",
        "I fjerde stadie kan behandlinger have effekter der rækker langt ud over det øjeblikkelige problem. Klienten kommer ind med en specifik klagepunkt, og det de oplever bagefter er en orientering der spænder over hele deres liv. Det er ikke noget vi har planlagt — det er Long Tide-rummets natur.",
        "Sårbarheden i fjerde stadie er at miste forbindelsen til det praktiske og det jordnære. Vi kan blive så optaget af det subtile at vi mister det konkrete. Klinisk modenhed på dette niveau er at kunne være i Long Tide og samtidig huske at klienten har en krop, en hverdag, en konkret virkelighed.",
        "Fjerde stadie giver behandleren en ny form for tilstedeværelse. Vi behøver ikke gøre noget særligt for at være effektive — vores blotte tilstedeværelse i et trygt felt har effekt. Klienter kan melde forbedringer mellem sessioner som ikke er relateret til specifikke behandlings-greb. Det er feltets virkning, ikke teknikkens.",
    ],
    "05-femte-stadie": [
        "Femte stadie er ikke et stadie vi kommer til — det er en kvalitet der lejlighedsvis viser sig på vejen. De fleste behandlere oplever korte øjeblikke af det selv tidligt i deres rejse, lange før de er 'i' stadiet. Det er ikke afhængigt af år af praksis; det er afhængigt af betingelser.",
        "I femte stadie ophører den oplevede distinktion mellem behandler, klient og felt midlertidigt. Det er ikke en blanding af tre — det er en samtidig oplevelse af én. Bagefter kan vi ikke beskrive hvem der gjorde hvad. Det er sjældent og uforudsigeligt, og det kan hverken kaldes frem eller forhindres.",
        "Behandlinger der finder vej til femte stadie efterlader ofte både klient og behandler stille bagefter. Der er sjældent meget at sige. Klienten oplever ofte en samlet ro de næste dage eller uger; behandleren mærker det som om noget er trukket tilbage til hvor det hører hjemme. Det er ikke effekter vi har skabt.",
        "I femte stadie ophører selv den lytten vi har trænet os op i. Der er ikke længere en der lytter til noget; der er bare lytten — eller bare det der er. Det er vanskeligt at beskrive uden at falde ind i mystiske ord, men de fleste behandlere der har oplevet det genkender beskrivelsen umiddelbart.",
        "Risikoen ved at sigte mod femte stadie er at skabe en illusion om det. Vi kan beslutte at noget var stilhed, når det egentlig var afslapning eller udmattelse. Klinisk modenhed er at kunne lade stadiet komme uden at kalde det frem, og at kunne anerkende dets fravær uden at føle os mislykkede.",
        "Femte stadie kan ikke trænes som teknik. Det kan kun forberedes ved at de fire foregående stadier er fuldt mødt. Når der ikke længere er forberedelse at gøre — når al teknik, al lytten, alt nærvær er på plads — kan stilheden vise sig. Den kommer altid i stedet for, ikke som tilføjelse til arbejdet.",
        "Selv erfarne behandlere oplever femte stadie sjældent. Det er ikke et tegn på at vi ikke er nået langt nok. Det er en påmindelse om at den dybeste dybde ikke er en præstation. Det vi kalder god behandling involverer ofte ikke femte stadie — bare gode kvaliteter af de fire foregående.",
    ],
}


EGENSKAB_INSPIRATIONER = {
    "1. Neutral lytten uden agenda": [
        "Den neutrale lytten begynder allerede inden hænderne lander. Den kvalitet vi bringer ind i rummet — hvilken intention vi har, hvilke forventninger vi bærer — registreres af klientens system før den fysiske kontakt. Forberedelsen er en del af lytningen, ikke en separat fase.",
        "Den neutrale lytten adskiller sig fra klinisk vurdering ved fraværet af kategori. Vurdering placerer det vi mærker i forud-kendte kasser. Lytten lader fænomenet være sig selv først, og lader sproget komme bagefter — hvis det overhovedet kommer. Det er to forskellige perceptions-modi, ikke to grader af samme.",
        "Det er sjældent agendaen forsvinder helt — oftere bliver vi opmærksomme på den. At kunne mærke at vi har en plan, og lade planen træde til side uden at fortrænge den, er noget andet end at være helt neutral. Det er en levende disciplin, ikke en opnået tilstand.",
        "Når lytten begynder at trække sig sammen, kan det mærkes som en svag krampe i hænderne, en let fokusering der bliver til søgen. Det er sjældent dramatisk. Men over tid lærer behandleren at registrere disse mikroskopiske skift som tegn på at agendaen er begyndt at overtage feltet.",
        "Nogle klienter responderer på neutral lytten ved at åbne sig, andre ved at trække sig. Det er ikke et tegn på at lytningen er forkert — snarere på at klientens system har sin egen tærskel for hvor meget rum det kan modtage. Lytningen tilpasser sig denne tærskel uden at miste sin kvalitet.",
        "Den neutrale lytten modnes ikke ved at blive mere intens, men ved at blive mere rummelig. Den unge behandler lytter ofte ved at fokusere; den modne behandler lytter ved at brede opmærksomheden ud. Begge er gyldige, men kvaliteten af det vi mærker forskydes med årene.",
        "Den lytten der er neutral, har en særlig kvalitet af tilgængelighed uden tilbøjelighed. Den er hverken passiv eller aktiv, hverken forventende eller indolent. Den har en parathed der ikke retter sig mod noget bestemt — og det er præcis denne åbne parathed der giver klientens system rum til at vise sig.",
    ],
    "2. Selvregulering af nervesystemet": [
        "Selvreguleringen er ikke noget vi kun gør før behandlingen — den fortsætter gennem hele sessionen som mikroskopiske justeringer. Når vi mærker vores eget åndedrag blive overfladisk eller skuldrene løfte sig, er det signal om at finde tilbage til det centrale uden at afbryde kontakten med klienten.",
        "Co-regulering sker uanset om vi er bevidste om det eller ej. To nervesystemer i samme rum påvirker hinanden. Forskellen er om vores egen tilstand er stabil nok til at virke som et anker, eller om vi følger med ind i klientens dysregulering uden at registrere det.",
        "Tegnene på at vi har mistet vores forankring er ofte subtile: tankerne begynder at vandre, vi mærker en let utålmodighed, hænderne får en let intention de ikke havde før. At kunne registrere disse tidlige signaler er forskellen mellem at miste sig selv og at finde tilbage.",
        "Afslapning og selvregulering er ikke det samme. Vi kan være afslappede uden at være regulerede — slappe i muskulaturen men diffuse i opmærksomheden. Selvregulering har en kvalitet af koherens, en samling af systemet omkring midten, som afslapning alene ikke nødvendigvis indeholder.",
        "Hver behandler har sit eget sæt af reguleringsstrategier. For nogle er det åndedraget, for andre fødderne mod gulvet, for andre igen en indre orientering mod et bestemt punkt i kroppen. Det vigtige er ikke metoden men dens pålidelighed — at den faktisk virker når vi har brug for den.",
        "Med årene vokser kapaciteten til at blive i regulering selv under intensivt klinisk pres. Det betyder ikke at vi aldrig forskydes, men at restitueringstiden bliver kortere. Den modne behandler kan mærke en bølge af klientens dysregulering passere gennem feltet uden at miste sin egen forankring.",
        "Mellem to klienter er det sjældent nok at gå på toilettet og drikke vand. Den fysiologiske reset kræver bevidst opmærksomhed — en kort genfinding af jordingen, en stilhed der lader det forrige aftryk slippe. Selv to minutter brugt rigtigt kan være forskellen på en frisk eller en slidt næste session.",
    ],
    "3. Sansning af den terapeutiske proces": [
        "Skiftet fra forarbejde til egentlig terapeutisk proces kommer ofte uden varsel. Hænderne mærker pludselig at noget er anderledes — vævet har en anden karakter, åndedrættet har skiftet kvalitet, rummet selv føles forandret. At kunne registrere dette skift øjeblikkeligt er en af de finere kliniske færdigheder.",
        "Symptomlindring og terapeutisk proces er ikke det samme. Et symptom kan aftage uden at noget grundlæggende har ændret sig — et væv slapper af, men mønsteret består. Den ægte proces involverer en omorganisering på et dybere lag, hvor strukturen selv finder ny ligevægt.",
        "Den ro der ledsager terapeutisk proces, har en specifik kvalitet af fylde. Den er ikke tom stilhed men en mætning af potentiale. Hænderne mærker det som et felt der er blevet bredere, mere koherent, mere tilgængeligt. Klienter beskriver det ofte som at synke ned i sig selv.",
        "Den terapeutiske proces forløber sjældent lineært. Den kan tage pauser, gentage sig, fordybes i bølger. Hvad der ligner stagnation er ofte integration. At kunne lade processen folde sig ud i sit eget tempo, uden at fortolke pauserne som mangel på fremgang, er en del af håndværket.",
        "To behandlinger med samme klient kan have helt forskellige signaturer. Den ene gang viser processen sig som langsom omformning, den anden som hurtige skift. Det er ikke os der vælger formen — det er klientens system der i øjeblikket beslutter hvilken vej forandringen skal tage.",
        "Sansningen af den terapeutiske proces udvikles ikke gennem tænkning men gennem tusindevis af behandlinger. Hver gang vi har siddet med en klient og bagefter genkendt 'der skete noget', skærper hænderne deres genkendelse. Det er en kropslig læring der ikke kan forceres frem.",
        "Det sker også at sessionen forløber uden at den terapeutiske proces træder tydeligt frem. Det er ikke nødvendigvis tegn på at intet skete — ofte arbejder systemet på et niveau vi ikke kan registrere i øjeblikket. Klientens efterforløb afslører ofte det vi ikke kunne mærke direkte.",
    ],
    "4. Tålmodighed & uvished": [
        "Trangen til at gøre noget melder sig næsten altid på et tidspunkt — særligt når processen virker langsom eller uklar. At kunne mærke trangen og lade den passere uden at handle på den er en disciplin der modnes over år. Det er ikke fravær af intention; det er valg.",
        "Tålmodighed er ikke passivitet. Den passive behandler er fraværende, fjern, måske endda kedet. Den tålmodige behandler er fuldt til stede, opmærksom, engageret — bare uden at presse. Det er en aktiv venten, en tilstedeværelse der har givet slip på resultatet uden at give slip på engagementet.",
        "Uvisheden er ikke en ulempe ved arbejdet — den er noget af det vi arbejder med. Den åbner det rum hvor klientens system kan vise hvad vi ikke kunne forestille os. At kunne hvile i ikke-at-vide er ikke det samme som at være forvirret; det er at have plads til at blive overrasket.",
        "Den unge behandler tror ofte at uvisheden er tegn på manglende kompetence. Den modne behandler genkender den som signal om at processen er åben. Skiftet fra at fortolke uvished som mangel til at læse den som mulighed er en af de vigtigste indre forskydninger i behandlerens udvikling.",
        "Når vi mister tålmodigheden uden at vide det, viser det sig ofte som en forhastet konklusion — vi tror vi har forstået processen, og hænderne begynder at arbejde ud fra denne forståelse. Det er præcis i dette øjeblik, at vi mister kontakten med det der faktisk er ved at ske.",
        "Nogle klienters processer udfolder sig i løbet af minutter; andres tager hele behandlinger eller endda flere sessioner. Tålmodigheden tilpasser sig dette individuelle tempo. At forsøge at fremskynde en langsom proces eller bremse en hurtig er at gå på tværs af systemets egen visdom.",
        "Når processen ser ud til at gå i stå midt i en behandling, kan minutterne føles meget lange. Klientens tavshed, vores eget åndedrag, tikkende klokker, det hele bliver tydeligt. Det er ofte præcis i denne tilsyneladende tomhed, at den dybeste integration foregår.",
    ],
    "5. At mærke helhedens prioritering": [
        "Helhedens invitation viser sig sjældent som et råb. Oftere er det en svag trækning af opmærksomheden mod et område, en fornemmelse af at hænderne 'falder' et bestemt sted hen, en let resonans i feltet. At kunne mærke disse subtile pegne kræver en lyttende kvalitet, ikke en søgende.",
        "Klientens beskrevne symptom og kroppens prioritet falder ikke altid sammen. En klient med skuldersmerter kan have et system der kalder mod bækkenet eller åndedrættet. At kunne lytte forbi det tydelige symptom uden at ignorere klientens lidelse er en finstemt klinisk balancegang.",
        "Helheden synes at have sin egen rangordning af hvad der skal løses først. Det er sjældent vi kan forstå rationalet bagved — men når vi følger det, viser efterfølgende behandlinger ofte at den valgte vej var mere effektiv end den vi ville have valgt rationelt.",
        "Et område der afviser arbejde, har en bestemt kvalitet under hænderne. Det er ikke spændt eller modstandsfuldt på den almindelige måde — det er stille, lukket, ikke til stede. At forveksle denne afvisning med modstand og forsøge at presse igennem er en af de almindelige kliniske fejl.",
        "Det kræver tillid at lade systemet vælge. Vi har lært at diagnosticere, at se sammenhænge, at lægge planer. At lade alt dette træde tilbage og lade kroppen pege er en omvendt logik. Det føles ofte forkert i begyndelsen — og bliver med tiden den eneste rigtige vej.",
        "Helhedens prioritering kan ændre sig undervejs. Det område der inviterede ved behandlingens start, kan være færdigt halvvejs igennem, og noget andet træder frem. At følge denne forskydning frem for at holde fast i den oprindelige plan er en del af det dynamiske arbejde.",
        "Når vi virkelig giver helheden lov til at lede, er der øjeblikke hvor behandlingen tager retninger der overrasker os. Klienten klagede over et knæ, og pludselig er det åndedrættet der frigøres. Det er sjældent vi kunne have forudsagt det — og næsten altid mere virkningsfuldt end det vi havde planlagt.",
    ],
    "6. Synkron bevægelse med kroppen": [
        "Synkroniseringen kræver konstant mikroskopiske justeringer. Vævets retning ændrer sig let, hastigheden skifter, kvaliteten varierer. Hænderne er ikke statiske — de er i levende dialog med bevægelsen, justerer sig fra øjeblik til øjeblik uden at klienten registrerer det som aktivt arbejde fra vores side.",
        "Forskellen mellem at følge og at lede er ofte meget lille. En lille fremskubning af hånden, en mikroskopisk forventning om hvor bevægelsen skal hen — og pludselig er vi gået fra synkron til styrende. At kunne mærke denne grænse, og blive på den rigtige side, er en finstemt færdighed.",
        "Når synkroniseringen brydes, mærkes det ofte først som en let modstand i vævet — som om kroppen registrerer at vi ikke længere er med. Det kan også vise sig som at bevægelsen taber kvalitet, bliver mindre koherent, eller stopper helt. Disse er signaler om at finde tilbage til lytten.",
        "Når kroppen vælger ekstremt langsom bevægelse, kommunikerer den noget. Det kan være om at integration kræver tid, om at processen er på et følsomt sted, om at systemet beder os om at sænke vores eget tempo. At respektere denne langsomhed uden at forsøge at opmuntre den er at høre hvad der bliver sagt.",
        "Trangen til at hjælpe bevægelsen videre melder sig ofte når den er allermest langsom eller stopper helt. Det er præcis her, at vi forstyrrer mest. At kunne mærke trangen som signal om at gøre mindre, ikke mere, er en af de modige indre vendinger i behandlingen.",
        "Nogle klienters væv bevæger sig så hurtigt at vores opmærksomhed knap kan følge med; andres så langsomt at vi tror der ingen bevægelse er. Synkroniseringen tilpasser sig dette individuelle tempo. Den rigtige hastighed er aldrig vores; den tilhører altid systemet vi sidder hos.",
        "En pause i bevægelsen er ikke fravær af bevægelse — det er bevægelse der har skiftet niveau. Mens den ydre form står stille, sker der ofte noget på et finere lag. At kunne være i pausen uden at fylde den er at give plads til denne skjulte bevægelse.",
    ],
    "7. Kvalitet i berøringen": [
        "Hvordan hænderne lander, er allerede en kommunikation. Vægten af kontakten, tempoet, retningen — alt sender signaler ind i klientens system. Ofte mærker klientens nervesystem hvad der er muligt eller ikke muligt i de første sekunder, før der er begyndt egentlig behandling.",
        "Berøringen er et sprog uden ord, og det taler hele tiden. Hver sekund kommunikerer vores hænder noget om vores tilstand, vores intention, vores nærvær. Klienten registrerer dette på et niveau der ligger under det bevidste, men der bliver hørt — og responderet på.",
        "Blød berøring og kollapset berøring er ikke det samme. Den bløde har form, struktur, klar tilstedeværelse — bare uden tryk. Den kollapsede har mistet sit center, sin retning. Klientens system genkender forskellen øjeblikkeligt og responderer kun på den første.",
        "Klientens første response på vores berøring fortæller meget. Et åbent system folder sig let ud; et lukket trækker sig let; et oversensitivt overreagerer. Disse første signaler er ofte de vigtigste i hele sessionen — de viser hvilken kvalitet af berøring resten af behandlingen kalder på.",
        "Klienter har vidt forskellige tærskler for berøringskvalitet. Den traumatiserede kan opfatte selv let kontakt som invasion; den somatisk lukkede kan have brug for tydeligere kontakt for overhovedet at registrere os. At kunne læse den individuelle tærskel og tilpasse berøringen er en del af det kliniske håndværk.",
        "Kvaliteten af berøring er noget vi øver, ikke noget vi er. Det er en daglig praksis — at mærke hvad hænderne gør, justere, lære. Selv erfarne behandlere kan opdage at deres berøring er blevet mekanisk eller distraheret, og må vende tilbage til den grundlæggende kvalitet igen.",
        "Den neutrale berøring er ikke fravær af kvalitet — den er en bestemt kvalitet. Den har en aktiv tilstedeværelse uden bestemt retning, en åbenhed der er etableret med præcision. Klienten kan mærke forskellen mellem en behandler der bare lægger hænderne på, og en der har valgt sin neutralitet.",
    ],
    "8. Sans for behandlingens rytme": [
        "Mod slutningen af en optimal behandling viser der sig ofte en bestemt kvalitet — en bølge af integration der er ved at folde sig ud. Hænderne mærker det som en samlende bevægelse, en slags hjemkomst. At genkende denne bølge er ofte tegnet på at behandlingen nærmer sig sin naturlige afslutning.",
        "Mætning har en specifik kvalitet i vævet — en fylde der er begyndt at lukke sig. Det er ikke modstand men signalering om at systemet har modtaget hvad det kan absorbere lige nu. At kunne mærke denne kvalitet og respektere den er en del af det differentierede arbejde.",
        "En for kort behandling efterlader processen uden at have nået integration; en for lang overstrækker kapaciteten. Begge kan virke kontraproduktivt. Den rigtige længde er sjældent den klokken angiver — den er den klientens system selv definerer gennem sine subtile signaler.",
        "Når vi har overskredet systemets kapacitet, mister behandlingen ofte sin friskhed. Vævet bliver mindre responsivt, energien i feltet aftager, kvaliteten der var der midtvejs forsvinder. At kunne registrere denne kvalitative ændring og afslutte i stedet for at fortsætte er en del af håndværket.",
        "Det kræver mod at afslutte en behandling før klokken siger det er tid. Vi har lært at give 'fuld behandling' og kan opleve det som mangelfuldt at slutte tidligt. Men når systemet er færdigt, er det færdigt — og at trække sessionen er at gå på tværs af det vi netop har skabt.",
        "Samme klient kan have brug for forskellig længde i forskellige sessioner. Den ene gang er behandlingen færdig efter 30 minutter, den næste skal der bruges fulde 75. At kunne tilpasse sig disse variationer uden at spørge 'hvad har de betalt for' er en del af den kliniske respekt for processen.",
        "Efter den aktive del af behandlingen kommer ofte en integrationsfase, hvor systemet sætter sig. Denne fase kan ligne afslutning, men kalder på at vi bliver siddende et øjeblik mere — uden at arbejde, uden at udløse noget, blot som vidne til at processen finder sin egen ro.",
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
                                    section_inspirationer: dict = None) -> str:
    """Render brødtekst-sektioner og refleksioner fra et body-stykke.

    Hvis 'inspirationer' angives, indsættes en INSPIRATION-blok lige før
    refleksionsspørgsmålene. Hvis 'section_inspirationer' (dict) er angivet,
    slås op pr. sektion-heading (fx Rum X eller numererede egenskaber).
    """
    out = ""
    sections = parse_sektioner(body)
    current_section = None
    for heading, content in sections:
        if not content.strip() and not heading:
            continue
        if heading.lower().startswith("til refleksion"):
            # Indsæt inspirations-blok før refleksioner
            if inspirationer:
                out += render_inspiration_block(inspirationer)
            elif section_inspirationer and current_section and current_section in section_inspirationer:
                out += render_inspiration_block(section_inspirationer[current_section])
                current_section = None
            out += "**[REFLEKSIONSSPØRGSMÅL]**\n\n"
            for i, q in enumerate(parse_refleksioner(content), 1):
                out += f"{i}. {q}\n\n"
        elif heading.lower() == "relationer":
            continue
        elif heading:
            if section_inspirationer and heading in section_inspirationer:
                current_section = heading
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
    # For de-fem-zoner og de-otte-essentielle-egenskaber: pass section_inspirationer
    # så de injiceres pr. sektion (Rum X eller nummereret egenskab)
    if filnavn == "de-fem-zoner":
        out += render_kapitel_body_sektioner(body, section_inspirationer=RUM_INSPIRATIONER)
    elif filnavn == "de-otte-essentielle-egenskaber":
        out += render_kapitel_body_sektioner(body, section_inspirationer=EGENSKAB_INSPIRATIONER)
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
        # Pass inspirations-paragraffer pr. underafsnit-filnavn
        if undermappe == "begreber":
            inspirationer = BEGREB_INSPIRATIONER.get(filnavn)
            out += render_kapitel_body_sektioner(body, inspirationer=inspirationer)
        elif undermappe == "stadier":
            inspirationer = STADIE_INSPIRATIONER.get(filnavn)
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
