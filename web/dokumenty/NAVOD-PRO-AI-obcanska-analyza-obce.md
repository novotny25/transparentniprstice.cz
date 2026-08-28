# Občanská datová analýza hospodaření obce — provozní manuál

**Verze 1.0 · 27. 8. 2026 · Petr Novotný, transparentniprstice.cz**

Tenhle dokument je psaný tak, aby podle něj **AI asistent postavil obdobný web
pro libovolnou českou obec**. Obsahuje konkrétní zdroje dat, adresy rozhraní,
struktury souborů, kontroly a — což je nejcennější — **pasti, na které jsme
narazili a které nejsou nikde popsané**.

Vznikl z reálného projektu pro obec Prštice (997 obyvatel, okres Brno-venkov),
který trval zhruba čtyři měsíce. Šablona webu i skripty jsou volně k dispozici:
`github.com/novotny25/transparentniprstice.cz`

> **Co potřebujete, aby manuál fungoval:** špičkový AI model v **agentním
> režimu** („vibe coding") — například Claude Code s nejvyšším dostupným
> modelem, nebo srovnatelně vyspělý nástroj — a **účet na GitHubu**.
> Části B–D (zdroje dat, analýza, žádosti dle zákona 106) zvládne i běžná
> chatovací AI; stavbu a provoz webu (části A2, E a F) s běžným chatem
> nepostavíte. Říkáme to narovinu, ať neztrácíte čas: **s neplacenou
> chatovací aplikací web jako transparentniprstice.cz nevznikne.**

---

## Jak tenhle manuál použít

**Jste-li AI asistent:** čtěte celé, postupujte po částech A → F a po každé
části ukažte člověku výsledek. Nikdy nepokračujte, když neprošla kontrola.
Části D a F obsahují rozhodnutí, která **musí udělat člověk**.

**Jste-li člověk:** předejte tenhle soubor svému AI asistentovi v agentním
režimu (např. Claude Code) s pokynem: *„Postupuj podle tohoto manuálu
a postav mi občanskou datovou analýzu hospodaření obce [název], IČO
[číslo]."* Pro samotnou analýzu bez webu stačí i běžný chat (Claude,
ChatGPT, Gemini) — předejte mu části B až D.

---

## Zásady, které platí v každém kroku

1. **Každé číslo má zdroj.** Buď je převzaté z oficiálního výkazu, nebo je
   dopočítané ze zdroje reprodukovatelným způsobem. Číslo bez zdroje na web
   nepatří.
2. **Rozlišujte typ údaje:** převzato ze zdroje / vypočítáno / zařazeno
   autorem / nezjištěno. Čtenář musí poznat, co je fakt a co úsudek.
3. **Chybějící údaj je zjištění, ne mezera k vyplnění.** AI nikdy nesmí
   „dopočítat", co v datech není.
4. **Neanonymizovaná data nikdy do cloudové AI.** Účetní deníky s adresami
   a jmény, faktury, žádosti s rodným číslem — ty zůstávají lokálně.
5. **Fakta oddělte od komentáře.** Komentář podepište a graficky odlište.
6. **Není to audit.** Je to občanská datová analýza. Tak to i pojmenujte —
   slovo „audit" má v účetnictví a právu jiný, chráněný význam.
7. **Obci vždy prostor k vyjádření**, ještě než web začnete šířit.

---

# ČÁST A — Příprava

## A1. Co potřebujete zjistit na začátku

| Údaj | Kde ho najdete |
|---|---|
| **IČO obce** | web obce (povinně zveřejňované informace) nebo ares.gov.cz |
| **Kód obce (ČSÚ)** | šestimístný, např. 583707 — v ARESu v poli `kodObce` |
| **ID datové schránky obce** | seznam držitelů na `mojedatovaschranka.cz` |
| **Okres a kraj** | ARES |

Ověření IČO přes ARES (veřejné, bez klíče):

```bash
curl -s "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/00282405"
```

Hledání IČO obce podle kódu obce (právní forma 801 = obec):

```bash
curl -s -X POST "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/vyhledat" \
  -H "Content-Type: application/json" \
  -d '{"sidlo":{"kodObce":583707},"pravniForma":["801"],"pocet":5,"start":0}'
```

## A2. Struktura projektu

Oddělte **soukromou zónu** (originály s osobními údaji) od **veřejného
repozitáře**. Tohle je nejdůležitější rozhodnutí celého projektu:

```
~/Developer/nazev-obce-web/          ← veřejný repozitář (GitHub)
├── data/                            ← jen sanitizované JSON/CSV
├── skripty/                         ← extrakce, validace, anonymizace
├── web/                             ← publikovaná složka (HTML, CSS, PDF)
│   ├── dokumenty/                   ← anonymizovaná PDF
│   └── obrazky/
├── obsah/                           ← pracovní texty (NEPUBLIKUJE se!)
└── netlify.toml

~/Developer/nazev-obce-private/      ← MIMO repozitář, nikdy necommitovat
├── zdroje/                          ← stažené originály
├── extrakty/                        ← neanonymizované výtahy
├── qa-reporty/
└── manifest-originalu.yml           ← SHA-256 všech originálů
```

> **Past, na kterou jsme narazili:** pracovní texty a odloženou (nezveřejněnou)
> sekci jsme měli uvnitř `web/`. Kdyby to neodhalila kontrola před nasazením,
> byly by veřejně dostupné na URL. **Cokoli uvnitř publikované složky je
> veřejné**, i když na to nikde nevede odkaz.

Do repozitáře patří `.gitignore`, který originály zakáže:

```
.DS_Store
.env
*.key
__pycache__/
*.xlsx
Detail_uctu_*
*-finm-*
qa-report*
```

---

# ČÁST B — Sběr dat

## B1. Rozpočet obce (MONITOR státní pokladny)

Nejcennější zdroj. **Rozklikávací rozpočet má veřejné rozhraní**, které není
nikde zdokumentované — objevili jsme ho odposlechem síťových požadavků webu.

**Období se zadává jako `YYMM`** — `2512` = prosinec 2025 (celý rok),
`2606` = červen 2026 (první pololetí).

### Druhové členění (podle položek — platy, energie, právní služby…)

```bash
curl -s "https://monitor.statnipokladna.gov.cz/api/rozpocet/souhrnny?obdobi=2512&ic=00282405"
```

Vrací strom: `children` → `Revenues` / `Expenditures` → skupiny → položky.
U každého uzlu je `code` (číslo položky), `name` a `budget.reality`
(skutečnost). **`reality` je konsolidovaná** — nezahrnuje vnitřní převody.

### Odvětvové členění (podle paragrafů — škola, odpady, úřad…)

```bash
curl -s "https://monitor.statnipokladna.gov.cz/api/rozpocet/odvetvovy?obdobi=2512&ic=00282405&cast=v"
```

> **Past:** bez parametru `cast=v` (výdaje) vrátí rozhraní chybu 400.
> Pro příjmy použijte `cast=p`.

### Metadata obce (včetně počtu obyvatel podle MF)

```bash
curl -s "https://monitor.statnipokladna.gov.cz/api/ucetni-jednotka/00282405"
```

### Kompletní data (když potřebujete i položku uvnitř paragrafu)

Rozhraní výše vrací buď paragrafy, **nebo** položky — ne jejich kombinaci.
Chcete-li vědět, *které konkrétní výdaje jsou uvnitř agendy* (např. kolik
z „činnosti místní správy" jsou právní služby), potřebujete otevřená data
výkazu **FIN 2-12 M** z datového katalogu MONITORu. Jsou v ročních balících
za celou ČR; vyfiltrujte z nich řádky svého IČO a uložte do soukromé zóny.

Struktura řádku (CSV, oddělovač `;`):

| sloupec | význam |
|---|---|
| 1 | `ZC_VTAB` — `000100` příjmy, `000200` výdaje |
| 2 | `0FISCPER` — období, první 4 znaky = rok |
| 8 | `0FUNC_AREA` — **paragraf** (odvětví) |
| 9 | `ZCMMT_ITM` — **položka** (druh výdaje) |
| 12 | `ZU_ROZKZ` — **skutečnost** |

## B2. Účetní výkazy (rozvaha, výkaz zisku a ztráty)

Roční řady jednotlivých účtů (518 Ostatní služby, 511 Opravy a udržování,
231 běžný účet, 451 dlouhodobé úvěry) najdete v profilu obce na MONITORu.
**Vezměte 10 let zpět** — bez delší řady nepoznáte, co je výkyv a co trend.

Klíčové účty, na které se dívat:

| Účet | Název | Proč |
|---|---|---|
| **518** | Ostatní služby | nakupované služby od dodavatelů — právní, IT, svoz odpadu |
| **511** | Opravy a udržování | u malých obcí bývá **největší** nákladový účet |
| **521** | Mzdové náklady | pro srovnání, nehodnotí se |
| **231 / 244** | běžný účet / termínované vklady | kolik obec reálně má |
| **451** | dlouhodobé úvěry | kolik dluží |
| **5141** | Úroky vlastní (položka) | kolik stojí obsluha dluhu |

## B3. Počty obyvatel a věková struktura (ČSÚ)

- **Bilance obyvatel po obcích** (řady od roku 1971, včetně rozdělení na
  přírozený a migrační přírůstek): databáze demografických údajů za obce,
  soubor za váš okres (`czXXXX.xlsx`).
- **Průměrný věk podle obcí:** produkt „Počet obyvatel v obcích k 1. 1.",
  tabulka za jednotlivé obce (sloupec „Průměrný věk celkem").

> **Past:** počet obyvatel za rok 2021 se u agregátorů liší. Používejte
> **oficiální bilanci ČSÚ po revizi sčítáním**, ne číslo ze sčítání ani
> z jiných webů. U Prštic: bilance 969, sčítání 959, agregátory 985.

## B4. Souřadnice obcí (pro srovnání se sousedy)

Wikidata, SPARQL, zdarma a bez klíče:

```sparql
SELECT ?obecLabel ?lat ?lon WHERE {
  ?d rdfs:label "okres Brno-venkov"@cs .
  ?obec wdt:P131 ?d ; wdt:P625 ?c .
  BIND(geof:latitude(?c) AS ?lat) BIND(geof:longitude(?c) AS ?lon)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "cs". }
}
```

## B5. Správní řízení a sankce

- **ÚOHS** — veřejná Sbírka rozhodnutí (`uohs.gov.cz`). Hledejte název obce.
  Malé obce tam bývají za neuveřejnění smlouvy na profilu zadavatele.
- **Registr smluv** (`smlouvy.gov.cz`) — pozor na výjimku níže.
- **Hlídač státu** (`hlidacstatu.cz/subjekt/<IČO>`) — agreguje smlouvy,
  dotace a zakázky.

> **Právní past, na které se dá shodit celý web:** zákon o registru smluv
> (340/2015 Sb.) **se na malé obce nevztahuje** — mají výjimku podle
> § 3 odst. 2 písm. l). Nikdy netvrďte, že obec „porušuje registr smluv".
> Pokuty ÚOHS se týkají **jiné** povinnosti: uveřejnění na **profilu
> zadavatele** podle zákona o zadávání veřejných zakázek (134/2016 Sb.).
> Tohle rozlišení si ověřte dřív, než cokoli napíšete.

---

# ČÁST C — Analýza

## C1. Sestavte časové řady a hledejte, co vybočuje

Postup, který se osvědčil:

1. Všechny nákladové účty za 10 let do jedné tabulky.
2. Spočítejte: změnu první → poslední rok, tříletý klouzavý průměr,
   průměrné roční tempo.
3. **Porovnejte průměr prvních tří let s průměrem posledních tří** — to je
   odolnější než srovnání dvou jednotlivých let, které mohou být výkyvem.
4. Označte účty, které rostou **setrvale každý rok** — to je silnější
   zjištění než jeden skok.

> **Nejsilnější nález v Pršticích** nebyl skok, ale trend: položka
> „konzultační, poradenské a právní služby" rostla **sedm let po sobě**
> z 289 tis. na 924 tis. Kč. Skok se dá vysvětlit jednorázovou akcí,
> setrvalý růst hůř.

## C2. Rozklad meziroční změny

Když účet skočí, zjistěte **co ten skok tvoří**. Potřebujete účetní detail
(část D). Postup:

1. Zápisy roztřiďte do skupin podle popisu (zámek, odpadní vody, právní…).
2. Pro dvojici let spočítejte změnu každé skupiny.
3. Zvlášť zkontrolujte všechny řádky, které tvoří **alespoň 5 %** rozdílu.
4. **Storna párujte k původnímu dokladu**, jinak vám vyjdou nesmysly.

> Rozklad odpovídá na otázku **„co tvoří rozdíl"**, nikdy na otázku
> „proč obec službu objednala". To druhé z účetnictví nevyčtete.

## C3. Rozlišení opakovaných a jednorázových výdajů

Doložitelné pravidlo, které nepotřebuje právní výklad:

- **opakovaný běžný chod** = běžné výdaje agend, které měly nenulový výdaj
  ve **všech** sledovaných letech,
- **jednorázové** = nepravidelné agendy + všechny kapitálové výdaje,
- **vnitřní převody** (paragraf 6330) vést zvlášť — nejsou výdajem navenek.

> **Nepoužívejte pojem „mandatorní výdaje"** a netvrďte, že opakovaný výdaj
> je ze zákona povinný. Označte to jako **zařazeno autorem**.
>
> A připojte upřesnění: jednorázové *rozhodnutí* (soudní spor, dvouletý
> pronájem stroje) se v datech skryje uvnitř „opakované" agendy, protože
> se platí rozložené do let. Hrubé dělení to nepozná.

## C4. Srovnání s podobnými obcemi

Dvě čísla, která dají čtenáři měřítko:

- **objem rozpočtu na obyvatele** proti obcím podobné velikosti v okrese
  (osvědčilo se pásmo ±10 % počtu obyvatel),
- **průměrný věk** proti nejbližším obcím a proti okresu.

> **Past:** nikdy neporovnávejte jediný rok — u malých obcí jedna investice
> pořadí úplně převrátí. Použijte **tříletý průměr**. V naší skupině měla
> jedna obec v jednom roce příjmy 100 mil. Kč (prodej majetku), což by ji
> jinak posunulo na první místo.

Oficiální velikostní skupiny ČSÚ: do 199, 200–499, 500–999, 1 000–1 999,
2 000–4 999 a výš. Pro fiskální srovnání je podstatnější **pásmo
rozpočtového určení daní** (zákon 243/2000 Sb.): 0–50, 50–2 000,
2 000–30 000, 30 000+.

## C5. Časté pasti v datech

| Past | Jak se projeví | Řešení |
|---|---|---|
| **Zastaralé názvy položek** | číselník MONITORu vrátí u položky 1345 „poplatek z ubytovací kapacity", ale od 2022 je to **poplatek za odpadové hospodářství** | ověřte proti vyhlášce 412/2021 Sb. a veďte si opravnou mapu |
| **Změna číslování** | odpadový poplatek byl do 2021 na položce **1340**, pak na **1345** | při časové řadě sečtěte obě, jinak vyjde, že občané neplatili |
| **Kapitálový výdaj v provozní agendě** | „chod úřadu" najednou 13,6 mil. místo 6,9 | rozlište kapitálové výdaje (položky třídy 6) a zobrazte je zvlášť |
| **Cash vs. accrual** | součty rozpočtu a účtu 518 nesedí | **nikdy je nesčítejte** — rozpočet je peněžní, účet 518 akruální |
| **Nerovnoměrné čerpání** | pololetní data × 2 dá nesmysl | poplatky se vybírají na jaře, příspěvek škole nerovnoměrně — u těch dopočet nedělejte |

---

# ČÁST D — Žádosti o informace

## D1. Co si vyžádat a v jakém pořadí

1. **Rozpis účtu, který vyskočil** (dodavatel, předmět plnění, datum,
   částka) ve strojově čitelném formátu — XLSX nebo CSV.
2. Podle nálezů: **smlouvy, faktury a výkazy práce** ke konkrétním položkám.
3. **Vnitřní směrnice** pro zadávání veřejných zakázek a finanční kontrolu.
4. Přehled **soudních řízení**, v nichž byla obec účastníkem.

## D2. Jak žádost napsat

Povinné náležitosti: identifikace povinného subjektu, identifikace žadatele
(jméno, datum narození, adresa) a srozumitelné vymezení informace.

Osvědčená struktura:

```
Věc: Žádost o poskytnutí informací podle zákona č. 106/1999 Sb. — [předmět]

[1 odstavec: proč se ptám — odkaz na veřejné výkazy s konkrétními čísly]

1. Co konkrétně žádám
   [výčet po bodech; u každého uveďte přesný rozsah a období]

2. Forma a způsob poskytnutí
   Podle § 4b a § 14 odst. 5 písm. d) žádám o poskytnutí ve strojově
   čitelném a otevřeném formátu (XLSX nebo CSV), nikoli jako sken či PDF.

Závěr: poděkování, odkaz na 15denní lhůtu, žádost o předběžné vyčíslení
nákladů podle § 17, pokud by je subjekt chtěl účtovat.
```

**Tipy, které se osvědčily:**

- Přiložte **tabulku hodnot z veřejných výkazů**, o kterých mluvíte —
  žádost je pak jednoznačná a nejde ji odbýt jako nesrozumitelnou.
- Vždy žádejte **strojově čitelný formát**; máte na to zákonný nárok.
- Posílejte **datovou schránkou** — je z toho doklad o doručení a běhu lhůt.
- Každou žádost i odpověď si **archivujte** včetně dodejek.

## D3. Když obec neodpoví nebo odpoví vyhýbavě

Lhůty podle zákona 106/1999 Sb.:

| Krok | Lhůta |
|---|---|
| Vyřízení žádosti | **15 dnů** od doručení |
| Stížnost na postup (§ 16a) | do **30 dnů** od marného uplynutí lhůty |
| Vyřízení stížnosti povinným subjektem | **7 dnů** — pak ji musí předat nadřízenému |
| Rozhodnutí nadřízeného orgánu | **15 dnů** |

Nadřízeným orgánem obce je **krajský úřad**.

> **Tohle je nejdůležitější zkušenost z celého projektu:** když obec pošle
> místo dokumentů jen slovní sdělení, je to **důvod ke stížnosti podle
> § 16a**, ne konec věci. V Pršticích krajský úřad stížnosti vyhověl
> a obci **přikázal žádost vyřídit do 15 dnů**. Proti tomu se nelze odvolat.

Zdokumentujte celý postup na webu — chronologie žádostí je pro čtenáře
často zajímavější než samotná čísla, protože ukazuje, jak úřad funguje.

---

# ČÁST E — Web

## E1. Technická volba

**Statický web bez závislostí.** Žádný redakční systém, žádná databáze,
žádné externí knihovny. Důvody: bezpečnost, rychlost, nulové náklady
a hlavně — za pět let bude pořád fungovat.

Doporučená sestava:
- HTML + CSS + čistý JavaScript (bez frameworku),
- data v `data/*.json`, do HTML je vkládá skript,
- hosting Netlify nebo GitHub Pages, nasazení z gitu,
- doména ~300 Kč/rok.

## E2. Struktura webu, která se osvědčila

Jedna dlouhá hlavní stránka postupující **od obecného ke konkrétnímu**,
plus samostatné stránky:

1. **Obec v číslech** — zajímavosti (obyvatelé, věk, rozloha, historie),
   ať čtenář nezačíná tabulkou. Sem patří i srovnání s podobnými obcemi.
2. **Rozpočet za posledních N let** — příjmy, výdaje, saldo. A hned pod tím
   **peníze obce**: kolik má na účtech a kolik dluží.
3. **Účet, který vyskočil** — roční řada, klouzavý průměr, rozklad změn.
4. **Rok zblízka** — rozklikávací rozpočet: oblast → agenda → položka.
   Napřed **výdaje** (co lidi zajímá), příjmy až za nimi.
5. **Zajímavé změny nákladů** — 4–6 témat s grafem vývoje a komentářem.
6. **Vybrané výdaje** — konkrétní položky se čtyřřádkovým souhrnem.
7. Samostatně: **soudy a řízení**, **jak jsme k datům došli**, **návod**.

## E3. Prvky, které se nejvíc osvědčily

- **Rozklikávací rozpočet do tří úrovní.** Lidi baví se v tom vrtat.
- **Ikonka grafu u každého řádku** — rozbalí vývoj té položky za všechny
  roky. Zásadní pro pochopení kontextu jednoho čísla.
- **Pruh podílů** (jako přehled úložiště v telefonu) místo klasických
  progress barů — přehlednější a modernější.
- **Štítek původu u každého čísla:** zdroj / výpočet / autor / nezjištěno.
- **Blok „Co z dat nevíme"** u každého tématu. Posiluje důvěryhodnost víc
  než cokoli jiného.
- **Neúplný rok** (probíhající) zobrazujte vybledle a s hvězdičkou.

## E4. Čtyřřádkový souhrn u citlivých témat

U každého výdaje, na který se ptáte, použijte stejnou strukturu:

> **Co víme** — jen doložená fakta ze zdroje
> **Co jsme vypočítali** — vlastní výpočty, označené
> **Co zatím nevíme** — chybějící podklady, výslovně
> **Jak se vyjádřila obec** — její stanovisko, i když se vám nelíbí

Pod tím orientační srovnání s trhem (pokud dává smysl) a **otevřené otázky
k dosledování** — nikdy verdikt.

## E5. Jak psát o citlivých věcech

Osvědčený postup pro každé zjištění:

1. **Fakt z dat:** „Obec platí za službu X ročně Y Kč."
2. **Srovnání:** „Veřejné ceníky uvádějí pro obce této velikosti Z Kč."
3. **Zmírnění a kontext:** uveďte i to, co obhajuje druhou stranu, a co
   **není** v rozporu s pravidly.
4. **Otevřená otázka**, ne závěr.

> **Příklad, který nás naučil opatrnosti:** u dvouletého pronájmu stavebního
> jeřábu jsme napřed napsali jen cenu. Pak jsme doplnili, že **jeřáb je při
> opravě střechy nezbytný** a že **měsíční sazba odpovídá trhu** — otázkou
> je jen délka pronájmu. Bez toho by se dala celá analýza shodit jedinou
> větou: „a jak jinak měli opravovat střechu?"

Zakázané: hodnotící nálepky („podezřelé", „tunel"), tvrzení o příčině tam,
kde je jen souvislost, a osobní útoky na zastupitele či dodavatele.

---

# ČÁST F — Kontroly a publikace

## F1. Tři kontroly, které musí projít

**1. Validace dat** — kontrolní součty proti oficiálním výkazům:
- roční součty účetního detailu = výkaz zisku a ztráty (tolerance 1 Kč),
- součet paragrafů = celkové výdaje roku,
- návaznost rozkladu na meziroční rozdíly,
- párování storen.

**2. Registr publikovaných tvrzení** — seznam všech skutkových tvrzení, kde
skript hodnotu **přepočítá z dat** a ověří, že tvrzené číslo na webu opravdu
je. Ne porovnání s pamětí, ale s výpočtem.

**3. Privacy gate** — sken celého repozitáře na rodná čísla, adresy, ID
datových schránek, e-maily, telefony a klíče. **Musí skončit chybou**, když
najde nevyřešený nález.

> **Past:** vzor pro rodné číslo `\d{6}/\d{3,4}` chytá i **čísla jednací**
> typu `123854/2026`. Vyžadujte platný měsíc narození (01–12, u žen +50).

## F2. Anonymizace dokumentů

PDF se **nesmí** anonymizovat překrytím textu černým obdélníkem — text
zůstane v souboru a jde vykopírovat. Použijte skutečnou redakci (v Pythonu
knihovna PyMuPDF, funkce `apply_redactions`), která text z dokumentu odstraní.
Zároveň smažte metadata.

Co odstranit: adresu trvalého pobytu, datum narození, rodné číslo, ID datové
schránky, soukromý e-mail a telefon.
Co ponechat: jméno autora (hlásí se k tomu veřejně), jména úředníků v úřední
roli, čísla jednací a spisové značky (bez nich nejde dokument ověřit).

> **Nejdůležitější past celého projektu:** naše kontrola používala **stejné
> vzory** jako samotná anonymizace. Když vzor přehlédl „Datum narození:"
> (hledal jen „nar."), kontrola to přehlédla taky a nahlásila čistý výsledek —
> **v dokumentu přitom zůstalo datum narození a ID datové schránky.**
>
> **Kontrola musí být nezávislá na redakci.** Přidejte denylist konkrétních
> hodnot (vaše adresa, vaše ID schránky, vaše datum narození) a hledejte je
> zvlášť. Po opravě počet redakcí vyskočil z 37 na 55.
>
> A vždy si **prohlédněte alespoň jednu stránku výsledku očima**.

## F3. Před spuštěním

- [ ] všechny tři kontroly PASS
- [ ] data přegenerována ze skriptů a porovnána — musí vyjít stejná
- [ ] mobil od 360 px bez vodorovného posuvu
- [ ] jeden `<h1>` na stránku, `lang="cs"`, alt u obrázků
- [ ] tabulky v posuvném rámu, grafy mají textovou alternativu
- [ ] pracovní texty **mimo** publikovanou složku (ověřte, že vrací 404)
- [ ] kontakt na autora v patičce
- [ ] title, description, Open Graph, sitemap, robots.txt

## F4. Oznámení obci

**Než web začnete šířit**, pošlete obci datovou schránkou dopis, který:

- odkáže na web a shrne, co na něm je,
- vyjmenuje konkrétní údaje, které se obce týkají, s čísly a zdroji,
- požádá o dvě věci: upozornění na věcnou chybu a případné vyjádření,
- slíbí, že vyjádření zveřejníte **nezkrácené a označené**,
- dá rozumnou lhůtu (osvědčily se dva týdny),
- vysvětlí, že nejde o osobní spor.

Tenhle krok nevynechávejte. Chrání vás právně i reputačně a je to slušnost.

## F5. Právní mantinely

- **Skutková tvrzení** jen doložená. Hodnotící soudy jen z pravdivého základu.
- U **soukromých osob a firem** opatrněji než u veřejných funkcionářů.
- **Bez znevažujících excesů** — i pravdivé tvrzení může být podané tak,
  že přesáhne přiměřenou kritiku.
- Judikatura chrání roli **„společenského hlídacího psa"**, ale jen při
  férové práci s fakty.
- U běžících řízení **nepředjímejte výsledek**.

---

# Příloha 1 — Kontrolní seznam pro AI

Než ohlásíte hotovo, projděte:

1. Má **každé** číslo na webu zdroj nebo reprodukovatelný výpočet?
2. Netvrdím někde příčinu tam, kde mám jen souvislost?
3. Nesečetl jsem někde rozpočet (cash) s účetním nákladem (accrual)?
4. Je u autorských zařazení uvedeno, že jsou autorská?
5. Je někde v publikované složce něco, co tam nemá být?
6. Prošly všechny tři kontroly?
7. Prohlédl jsem si výsledek anonymizace očima?
8. Dal jsem obci prostor k vyjádření?

## Příloha 2 — Odhad času

| Část | Čas |
|---|---|
| A — příprava, zjištění IČO a struktura | 1 hodina |
| B — sběr dat ze všech zdrojů | 3–4 hodiny |
| C — analýza a hledání zajímavého | 4–6 hodin |
| D — žádosti (čistý čas psaní) | 2 hodiny + čekání na lhůty |
| E — stavba webu | 1–2 víkendy |
| F — kontroly, anonymizace, nasazení | 4 hodiny |

**Celkem zhruba 2–4 víkendy** rozložené do několika měsíců, protože se čeká
na odpovědi. Náklady: doména ~300 Kč/rok, hosting zdarma, AI asistent
~500 Kč/měsíc.

---

*Tenhle manuál i celý web jsou volně k použití. Když podle nich něco
postavíte, dejte vědět na petr@petrnovotny.com — rád na vás odkážu.*
