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
    ],
    "14-the-lesion-field": [
        "Læsionsfeltet er ikke en fejl. Det er livskraft der har gjort det bedste den kunne under de vilkår der var. At se det som beskyttelse, ikke fejl, ændrer behandlingens grundtone fundamentalt — fra at ville fjerne noget til at anerkende det der allerede er.",
        "Læsionen er ikke et sted men en proces. Feltet vedligeholder sin egen organisering med energi, og det kræver vores anerkendelse, ikke vores intervention, for at slippe sin opgave. Når det opdager at det ikke længere skal beskytte, vender potency tilbage til helheden.",
        "Når feltet ikke vil løslade, er det oftest fordi grundpræmissen — sikkerhed nu — endnu ikke er etableret. Det skridt kan vi ikke springe over. Først nervesystemets dybe besked om 'her er sikkert', så kan læsionen begynde at slippe sin beskyttelses-opgave.",
    ],
    "15-potency": [
        "Bound potency findes overalt hvor systemet har skullet låse noget for at overleve. Free potency er det der er tilgængeligt for almen heling og vedligeholdelse. Når bound potency frigives, er det ikke 'mere kraft' — det er den oprindelige kraft der ikke længere er bundet til en opgave.",
        "Potency bevæger sig ikke som en partikel — den manifesterer sig som ændringer i feltet. At mærke potency i hænderne er at mærke tilstandsskift snarere end at mærke 'noget der bevæger sig'. Det skaber et andet sprog for det vi gør.",
        "Når bound potency slipper sin opgave, vender den ikke 'frem' til behandleren eller 'ud' af kroppen — den vender tilbage til helheden hvor den startede. Vi mærker ikke en strøm fra A til B. Vi mærker en omfordeling i feltet, en genfordeling af kraften.",
    ],
    "16-ignition": [
        "Vi har alle gennemlevet flere ignition-øjeblikke — ved unionens øjeblik, ved fødslen, ved første åndedrag, ved den fulde landing i kroppen i de første år. Hver ignition er en tærskel-overskridelse til ny biologisk organisering. Tærsklerne er aktive påmindelser om hvad kroppen kan.",
        "Re-ignition efter sygdom eller traume er ikke en restauration af det gamle — det er en ny ignition. Klienten kommer ikke 'tilbage' til som de var; de bevæger sig fremad til en ny baseline. Det er en vigtig skelnen for både behandler og klient.",
        "Når ignition ikke vil ske, er det sjældent fordi der mangler kraft. Oftere mangler tærskelbetingelserne — tilstrækkelig hvile, tilstrækkelig sikkerhed, tilstrækkelig orientering. Vi tænder ikke ilden; vi forbereder brændet. Når brændet er klart, kommer flammen af sig selv.",
    ],
    "17-axial-fluctuations": [
        "Aksiale fluktuationer følger ikke altid samme retning. Nogle gange er de overvejende fra coccyx mod kraniet, andre gange fra kraniet mod coccyx, andre gange spiralerende. At mærke retningen og dens variation er en finmotorisk evne der udvikles over år, ikke uger.",
        "Klienten oplever fluktuationerne forskelligt afhængigt af hvor i kroppen de mærker dem. I bækkenet ofte som vugning; i kraniet som let pres-forandring; langs columna som bølgende fornemmelse. Disse spontane beskrivelser hjælper med at konfirmere hvad behandlerens hænder allerede mærker.",
        "Når fluktuationerne er blokerede, mærkes de ofte som en tør eller klistret kvalitet i vævet. Det er ikke en fagligt korrekt beskrivelse, men det er den hænderne ofte rapporterer. At give plads til denne fagligt-upræcise observation er en del af håndværket — ikke en mangel.",
    ],
    "18-wholeness": [
        "Embryologisk er kroppen aldrig blevet 'sat sammen af dele' — vi var aldrig dele først. Vi var en helhed der differentierede sig. Den primære helhed forbliver tilstede gennem hele livet som det organiserende princip vi kalder sundhed. Helhed er ikke en præstation; den er udgangspunkt.",
        "Praktisk wholeness er ikke filosofi — det er en målbar observation: når én del bevæger sig, bevæger andre dele sig samtidigt og koordineret. Når denne synkronicitet ikke findes, lokalt eller globalt, er der noget at lytte til. Det er ofte det første hænderne læser når de lander.",
        "Når dele af kroppen 'føles separate', er det altid en relativ adskillelse, ikke en absolut. Helheden er der stadig, men dens kommunikationskanaler er sløret. Vores arbejde er at gøre de kanaler mærkbare igen — ikke at samle delene, for de var aldrig adskilt.",
    ],
}


RUM_INSPIRATIONER = {
    "Rum A — Den Fysiske Krop": [
        "Det er fristende at se Rum A som det 'overfladiske' niveau, men det er en fejlforståelse. Den fysiske krop er ikke under de andre rum — den er det levende fundament hvorfra de andre rum udfolder sig. At ankre godt i Rum A er ikke begrænsning. Det er forudsætning.",
        "Nogle klienter når aldrig længere end Rum A i et behandlingsforløb. Det er ikke en mangel ved behandlingen. Det er hvad systemet kan rumme på det tidspunkt. Hvis vi presser videre, lukker vi det ned. Tålmodigheden ligger i at lade Rum A være nok når det er nok.",
        "Den hyppigste fejl i biodynamisk arbejde er at springe over Rum A på vej til 'noget dybere'. Klienten oplever det som distance — som om behandleren ikke er der hvor de er. Den dybeste behandling begynder altid med at hænderne hviler på den krop der faktisk er.",
    ],
    "Rum B — Væskekroppen": [
        "Væskekroppen i Rum B er ikke kun blod og lymfe — det er hele kroppens samlede væskemiljø der begynder at bevæge sig som én sammenhængende enhed. Det vi mærker når Rum B vågner er denne matrix der træder ud af adskilte kompartments og bliver ét felt.",
        "Overgangen fra Rum A til Rum B mærkes ofte først som en kvalitetsændring i vævet. Det bliver 'vådere', mere flydende. Klienten beskriver det nogle gange som om de bliver tunge eller lette samtidigt. Det er paradokset ved væskekroppen — den har vægt og letvægt på én gang.",
        "Når Rum B nægter at vågne, er det oftest fordi nervesystemet endnu ikke har givet sin tilladelse. Væskekroppen er afhængig af parasympatisk dominans for at flyde frit. Hvis behandlingen forhastes, blokerer den sympatiske aktivering den proces vi venter på.",
    ],
    "Rum C — Det Relationelle Felt": [
        "Det relationelle felt er ikke metafor men biologi. Når to nervesystemer mødes uden trussel, opstår en målbar fælles regulering — det er det system der opstod blandt sociale pattedyr og som vi alle bærer. Vi bygger på en eksisterende neurobiologisk arkitektur, ikke på spirituel idé.",
        "I det relationelle felt bliver behandleren også ændret. Det er ikke en énvejsbevægelse fra os til klienten. Vi mærker noget i os selv vågne i takt med klientens åbning. At anerkende dette uden at lade vores eget materiale fylde feltet er en daglig disciplin.",
        "Når det relationelle felt overvælder klienten, er det ofte fordi det er længe siden de har været i et trygt felt. Selv det at føle sig set kan være krævende. Vores opgave er ikke at gå frem, men at give feltet plads og tid til at modne i sit eget tempo.",
    ],
    "Rum D — The Long Tide / Primary Respiration": [
        "De 100 sekunder er ikke en målbar konstant. Cyklusserne kommer i et bredere spektrum — nogle gange 80, nogle gange 120 — og varierer fra klient til klient og fra øjeblik til øjeblik. Tallet er en pejling, ikke en definition. Hvad vi lytter til er rytmens natur, ikke dens præcision.",
        "Læringen af at mærke Long Tide sker ikke gennem instruktion. Det sker oftest ved at sidde sammen med en mere erfaren behandler ved den samme klient — over tid genkender hænderne det andre hænder allerede mærker. Det er en mundtlig tradition, ikke en målbar færdighed.",
        "En vanskelig erkendelse: nogle gange tror vi at mærke Long Tide, men det er noget andet — en intern rytme i os selv, en forventning, en forestilling om hvordan det skal føles. At kunne skelne mellem det indre billede og den faktiske oplevelse er en del af modningen.",
    ],
    "Rum E — Dynamisk Stilhed": [
        "Dynamisk Stilhed er ikke en højere bevidsthedstilstand eller et behandlings-mål. Den dukker op nogle gange uden at vi har planlagt det, og den lader sig ikke trænes. Det meste arbejde sker i Rum A til D, og det er som det skal være. Rum E er bonus, ikke mål.",
        "Når sproget rammer sin grænse i Rum E, bliver det fristende at gribe til store ord. Men ord er ord. De peger og svigter. Det vigtigste er ikke ordet vi vælger — kærlighed, mysteriet, nåde, tilstedeværelse — men at vi ikke forveksler ordet med fænomenet.",
        "Rum E er det rum der har været til stede under alle de andre. Da vi i Rum A mærkede vævets historie, var stilheden allerede der. Den dukker bare ikke altid op i forgrunden. Når den gør, er det som om noget kort har ladet sig se af sig selv.",
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
