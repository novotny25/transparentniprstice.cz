# ZADÁNÍ: Web Transparentní Prštice

**Verze:** 1.5 (21. 8. 2026) — v1.4 zapracovala rozhodnutí Petra po oponentuře:
strojovou anonymizaci všech veřejných výstupů, vývoj účtu 518 za roky
2015–2025 s účetním detailem od roku 2022, oddělení soudních a správních
řízení a zjednodušené informační stavy „víme / vypočítali jsme / nevíme /
vyjádření obce". V1.5 vrací Petrův původní požadavek na rozlišení výdajů,
ovšem doložitelnou formou „opakované vs. jednorázové" místo právního pojmu
mandatorní (P-33).
**Autor zadání:** Petr Novotný + AI (na základě rozhovoru a průzkumu workspace)
**Schváleno:** Petr schvaluje zadání spuštěním realizace (zadáním spouštěcího
promptu z PLAN.md); do té doby jde o návrh.

---

## 1. O co jde

Veřejný web **transparentniprstice.cz**, který srozumitelně a doložitelně informuje
občany obce Prštice o hospodaření obce v minulém a předminulém volebním období
a je připravený na průběžné doplňování informací v obdobích následujících.

Jádrem je: (a) jednoduchý přehled skutečných rozpočtových příjmů a výdajů,
(b) vývoj účtu 518 Ostatní služby v letech 2015–2025 a účetní detail od roku
2022, včetně rozkladu změn podle kategorií, (c) transparentní chronologie
získávání a ověřování dat včetně dokumentů a žádostí dle zákona 106/1999 Sb.
a (d) oddělený přehled soudních řízení a správních kontrol či sankcí.

Projekt je **občanská datová analýza hospodaření**. Není účetním, právním ani
úředním auditem.

Provozovatel: **Petr Novotný, občan Prštic** — osobní občanský projekt,
podepsaný, s kontaktem. Neutrální datový tón: fakta a čísla se zdrojem,
komentář vždy graficky oddělený a označený jako názor autora.

## 2. Problém a pro koho

**Problém:** Občan Prštic dnes obtížně zjišťuje, jak obec hospodaří. Oficiální
zdroje (MONITOR, úřední deska, závěrečné účty v PDF) jsou pro laika obtížně
čitelné. Účet 518 vzrostl z přibližně 2,3 mil. Kč (2021) na 5,8 mil. Kč (2023),
v roce 2024 klesl na 3,5 mil. Kč a v roce 2025 znovu vzrostl na 4,7 mil. Kč.
Obec poskytla účetní detail bez údajů o dodavatelích; o poskytnutí dalších
vyžádaných informací probíhá navazující proces u Krajského úřadu JMK.

**Primární publikum:** běžný občan Prštic (~1 000 obyvatel), bez znalosti účetnictví.
**Sekundární publika:** zastupitelé, novináři, úředníci KrÚ, kritický oponent
(web musí obstát i při nepřátelském čtení — každé číslo doložené).

**Hlavní úloha stránky:** občan za 2 minuty pochopí, s čím obec hospodaří,
jak se účet 518 vyvíjel, které doložené skupiny nákladů tvoří jeho změny,
co je autorský výpočet či zařazení a co zatím zůstává nezjištěné. U vybraných
výdajů dostane podklady a srovnání, podle kterých si může udělat vlastní úsudek
o jejich hospodárnosti.

## 3. Proč teď

- Komunální volby se konají 9.–10. 10. 2026. Web má být záměrně zveřejněn
  s předstihem, aby měli občané čas se s podklady seznámit.
- 27. 8. 2026 uplyne lhůta KrÚ JMK k opatření proti nečinnosti — proces bude mít
  nový vývoj, web je místo, kde ho průběžně dokumentovat.
- Data i analýzy už existují (viz sekce 8) — chybí jen srozumitelná veřejná vrstva.

## 4. Co už existuje (nezačínáme od nuly)

- **1 335 účetních zápisů účtu 518 za 2022–2025** s pracovními kategoriemi (JSON v
  `0_Projects/4_PRŠTICE/2026_06_22 Analýza účtu 518/Detail_uctu_518_Prstice.html`,
  řádek 160) — jejich roční součty sedí na výkaz zisku a ztráty. Kategorie
  jsou autorské a před zveřejněním se opraví zjevná chybná zařazení a storna.
- **Rozvaha + výkaz zisku a ztráty 2015–2025** (JSON v
  `2026_04_30 Audit hospodaření obce/audit-prstice-rozvaha-vzz-dashboard.html`),
  nasazená pracovní verze: prsticehospodareni.netlify.app.
- **Hotové rozbory:** slabá místa hospodaření (A1–A10), rozbor GDPR pověřence
  s cenovým srovnáním trhu a kontrola lhůt s čísly jednacími. Vybrané téma
  jeřábu nemá samostatný rozbor — píše se přímo z účetního detailu.
- **Chronologie získávání informací** s daty, sp. zn. SP/088/2026,
  č. j. OUPR-867-2026 atd.
- **PDF dokumenty** (žádosti, odpovědi, dodejky) — jen na Petrově Macu, ne v gitu.
- **K soudním řízením:** žádost dle 106/1999 Sb. o přehled řízení, v nichž byla
  obec účastníkem od 1. 1. 2018, byla podána 15. 8. 2026; odpověď se čeká.
- **Ke správním řízením:** veřejně jsou dohledatelná tři pravomocná rozhodnutí
  ÚOHS (S0589/2023, S1089/2024 a S0071/2025). Jde o správní, nikoli soudní
  řízení, a na webu budou vedena odděleně.
- **Oficiální otevřená data MONITOR** (IČO 00282405): výkaz FIN 2-12 M
  (rozpočet dle paragrafů a položek), výkaz zisku a ztráty (účet 518) — CSV extrakty
  i webová služba pro budoucí automatickou aktualizaci.

## 5. Jak to funguje — struktura webu (v1)

Princip **postupného odkrývání**: přehled → kategorie → položka → původní dokument.
Nikdo není nucen do účetnictví, ale cesta dolů je vždy nabídnutá.

1. **Úvod** — jedna věta lidsky („Obec Prštice loni hospodařila s X mil. Kč…"),
   vedle sebe skutečné příjmy, skutečné výdaje a saldo; přepínač Kč / Kč na
   obyvatele. Graf nespojuje konkrétní příjmy s konkrétními výdaji.
2. **Rozpočet v kostce** — příjmy a výdaje jako jednoduché seřazené sloupce
   se srozumitelnými názvy agend: odpady, škola a školka, údržba, chod úřadu…;
   časová řada přes obě volební období a vždy i tabulková alternativa.
   Součástí je jednoduché rozlišení, kolik z výdajů se **opakuje každý rok**
   (běžný chod obce) a kolik tvoří **jednorázové položky** daného roku
   (investice a nepravidelné služby) — viz P-33.
3. **Účet 518** — vysvětlení pro laika a roční hodnoty 2015–2025. Graf
   vývoje ukazuje **přesné roční hodnoty na haléř** odpovídající veřejnému
   výkazu; klouzavý průměr se neuvádí, aby nešlo zapochybovat o přesnosti
   čísel (revize 22. 8. 2026 na pokyn Petra). Účetní detail začíná rokem 2022. Web ukazuje „co vytvořilo
   meziroční rozdíl" podle autorských kategorií, nikoli bez důkazů „proč obec
   službu objednala". Částky jsou označeny jako běžné ceny bez odečtení inflace.
   Neúplný rok 2026 je zobrazen samostatně.
4. **Ptáme se na vybrané výdaje** — právní služby, GDPR pověřenec a stavební
   jeřáb. Každé téma má jeden kompaktní čtyřřádkový souhrn: **Co víme** →
   **Co jsme vypočítali** → **Co zatím nevíme** → **Jak se vyjádřila obec**.
   Kontext, srovnání a komentář autora jsou až v rozbalitelném detailu. Téma
   jeřábu se nepředstavuje jako příčina růstu roku 2023: podle účetního detailu
   náklady na jeřáb mezi lety 2022 a 2023 klesly; jde o samostatně vybraný
   výdaj k posouzení.
5. **Soudní a správní řízení** — jedna stránka se dvěma jasně oddělenými
   částmi. Soudní část vychází především z odpovědi obce a u každého případu
   uvádí, kdo řízení inicioval a jakou roli obec měla. Správní část shrnuje
   kontroly a sankce správních orgánů, zejména ÚOHS. Souhrnný vývoj právních
   nákladů je zobrazen vedle řízení; vazba konkrétního nákladu na konkrétní
   řízení se uvede jen tehdy, když ji dokládá zdroj.
6. **Jak jsme postupovali** — chronologická osa občanské datové analýzy od
   nalezení výkazů ve veřejných zdrojích po řízení u KrÚ, s odkazy na
   anonymizovaná PDF;
   součástí je tabulkový přehled všech žádostí o informace a jejich stavu.
7. **Dokumenty** — knihovna všech podkladů ke stažení.
8. **Pro další obce a občany (volitelně ve v1)** — jak web vznikl, co dělala
   AI a co kontroloval člověk, odkaz na otevřený repozitář a návod, jak si totéž
   udělat jinde. Pokud by stránka ohrozila termín, přesune se celá do v2.
9. **O webu** — kdo, proč, zdroje dat, metodika, kontakt, prostor pro vyjádření obce.

## 6. Požadavky

### Nutné pro první verzi

**Obsah a data**
- **P-1:** Každé číslo na webu má uvedený zdroj a datum („zdroj: výkaz zisku a ztráty,
  MONITOR MF ČR, k 31. 12. 2025") a tam, kde existuje, proklik na dokument.
- **P-2:** Údaje se zobrazují v Kč i v přepočtu na obyvatele (přepínač); počet
  obyvatel dle ČSÚ je uveden u každého roku.
- **P-3:** Rozpočtová data v1 pokrývají minimálně roky 2019–2025. Účet 518 se
  zobrazuje v roční řadě 2015–2025 a v účetním detailu od roku 2022 do
  posledního dostupného období. Neúplné období roku 2026 se nesmí v grafu
  tvářit jako celý uzavřený rok.
- **P-4:** U důležitých údajů se rozlišuje: **převzato ze zdroje**, **vypočítáno**,
  **zařazeno autorem** a **nezjištěno**. Jedna krátká legenda platí pro celý
  web; štítek se opakuje jen tam, kde by mohl vzniknout omyl. Komentář autora
  zůstává samostatně podle P-5.
- **P-5:** Fakta a komentář jsou vizuálně i textově oddělené; komentářové bloky
  jsou označené (např. „Komentář Petra Novotného") a nepoužívají hodnotící
  nálepky typu „podezřelé", „tunel". Hodnocení hospodárnosti vždy uvádí
  použité kritérium a doložený základ; bez něj zůstává u otázky nebo indicie.
- **P-6:** Téma GDPR obsahuje cenové srovnání se zdroji. Čísla se označí jako
  srovnatelná pouze při obdobném rozsahu služby; jinak jde o orientační indicii
  a web vedle ceny stručně uvede známý rozsah plnění.
- **P-7:** Chronologie občanské datové analýzy obsahuje všechny kroky s daty a čísly jednacími
  a u každého kroku odkaz na anonymizované PDF (kde existuje).
- **P-8:** Veřejný repozitář, build ani deploy preview nikdy neobsahuje původní
  účetní exporty nebo neanonymizované dokumenty. Originály zůstávají mimo
  repozitář; veřejné JSON, CSV, HTML a PDF jsou nově vytvořené sanitizované
  deriváty. Toto pravidlo platí i pro metadata, názvy souborů a historii gitu.
- **P-8a:** Veřejný účetní dataset používá předem schválený seznam polí.
  **Revize 22. 8. 2026 (pokyn Petra):** původní účetní popis obce se
  ZACHOVÁVÁ; anonymizuje se jen tam, kde obsahuje osobní údaj (jméno fyzické
  osoby, adresu domácnosti, čp./če., parcelu) nebo číslo dokladu. Přejmenovávat
  čistý obecní popis by bylo zbytečným zásahem do surových dat a snižovalo by
  důvěryhodnost. Úplný seznam zásahů je v soukromé zóně a schvaluje ho Petr;
  veřejný souhrn zásahů (bez původních textů) je v repozitáři. Ponechané jméno
  fyzické osoby musí být výslovně uvedeno v publikačním allowlistu s důvodem.
- **P-8b:** Sanitizované soubory a PDF vyrábí lokální skript. U PDF se redakce
  neřeší pouhým překrytím textu: veřejná verze vznikne vypálením začernění,
  odstraněním původních vrstev, metadat, příloh a formulářů a novým OCR až nad
  začerněnou verzí.
- **P-8c:** Skript vytvoří jeden soukromý kontrolní report se všemi nálezy,
  veřejnými popisy a náhledy všech stran PDF. Petr provede jedinou souhrnnou
  kontrolu, případné opravy zapíše do pravidel a výstupy se znovu vygenerují.
  Bez automatické kontroly PASS, nulového počtu nevyřešených nálezů a Petrova
  sign-off se nic necommitne ani nenasadí. AI ani regex nejsou samy o sobě
  zárukou úplné anonymizace.
- **P-9:** Web obsahuje mini-slovníček přímo u grafů: účet 518, paragraf,
  položka, RUD a rozdíl mezi rozpočtovým výdajem a účetním nákladem — krátké
  vysvětlení v bublině nebo rozbalení, ne zvláštní stránka.
- **P-10:** Web obsahuje sekci „Kam se dívat dál" s odkazy na oficiální zdroje
  (profil obce v MONITORu, registr smluv, úřední deska, Hlídač státu).
- **P-11:** Stránka „O webu" uvádí provozovatele jménem, kontakt a nabídku
  obci na zveřejnění vyjádření po nezbytném odstranění osobních údajů.

**Technika a forma**
- **P-12:** Statický web bez přihlašování a databáze; data oddělená od prezentace.
  Web i grafy se generují výhradně ze sanitizovaných JSON/CSV v repozitáři.
- **P-13:** U každého grafu tlačítko „stáhnout data (CSV)" a tabulková alternativa.
  Stahovaná data jsou agregovaná nebo samostatně sanitizovaná podle P-8.
- **P-14:** Web splňuje pravidla čitelnosti skillu /web: text ≥ 16 px, řádek
  max 65ch, kontrast WCAG AA, jeden H1, funguje od šířky 360 px, spolehlivý
  světlý režim a `lang="cs"`. Tmavý režim je volitelný.
- **P-15:** Barva není nikdy jediným nositelem významu; grafy mají popisky os
  a tooltips; žádná kauzální tvrzení tam, kde je jen souvislost.
- **P-16:** SEO/sdílení: title, description, Open Graph obrázek, sitemap,
  robots.txt; produkční web je indexovatelný, preview zůstává `noindex`.
- **P-17:** Vlastní GitHub repozitář novotny25/transparentniprstice.cz
  (mimo PACT), nasazení z gitu (Netlify nebo GitHub Pages) až po privacy gate,
  doména transparentniprstice.cz (zaregistrována 21. 8. 2026).
- **P-18:** Přidání nové události do chronologie nebo nového dokumentu = úprava
  jednoho datového souboru + přidání soukromého PDF a spuštění sanitizační
  pipeline, bez zásahu do HTML/kódu.
- **P-19:** Před spuštěním projde web kontrolním seznamem: všechna hlavní čísla
  strojově přepočítána proti zdrojovým datům, AI kontrola každého publikovaného
  tvrzení proti dostupným podkladům, právně-jazyková kontrola, privacy gate dle
  P-8, test na mobilu, test čitelnosti a funkční odkazy. Finální obsah a
  anonymizaci vizuálně schvaluje Petr.

**Soudní a správní řízení a otevřenost procesu**
- **P-25:** Stránka „Soudní a správní řízení" obsahuje dvě oddělené části.
  Soudní část zahrnuje řízení před soudy, která probíhala alespoň zčásti od
  1. 1. 2018; u každého záznamu uvádí procesní roli obce a kdo řízení zahájil.
  Správní část zahrnuje kontroly, přestupková řízení a sankce správních orgánů,
  zejména ÚOHS. Záznamy se nesměšují ve společných počtech ani titulcích.
- **P-26:** Stránka se generuje z `data/rizeni.json`; každý záznam má povinné
  pole `typ: soudni | spravni`, instituci, spisovou značku, předmět, roli obce,
  stav, výsledek, zdroj a datum posledního ověření. Dokud obec neposkytne
  požadovaný přehled, web uvádí, že seznam veřejně dohledaných řízení nemusí
  být úplný. ÚOHS se nikdy neoznačuje jako soud.
- **P-27:** Vedle řízení se zobrazí celkový vývoj účetních nákladů na právní
  služby. Vazba konkrétního účetního zápisu na konkrétní řízení se zobrazí jen
  tehdy, je-li doložena fakturou, smlouvou nebo potvrzením obce. Jinak se uvede
  „Vazba na konkrétní náklad nezjištěna".
- **P-28:** Tabulkový přehled všech žádostí o informace („tracker 106"):
  datum podání, předmět, stav (odpovězeno / částečně / neposkytnuto /
  stížnost / u kraje), počet dní od podání. Generuje se
  z `data/zadosti-106.json` a je součástí sekce „Jak jsme postupovali".
- **P-29:** U klíčových čísel boxy „Ověř si to sám" — tři až pět kroků, jak si
  občan stejný údaj najde v oficiálním zdroji (MONITOR, úřední deska, ÚOHS).
### Až potom (v2+)
- **P-20:** Automatická čtvrtletní aktualizace rozpočtových dat z MONITORu
  (webová služba pro IČO 00282405 nebo CSV extrakty).
- **P-21:** Srovnání s 3–5 podobně velkými obcemi okresu Brno-venkov.
- **P-22:** Sekce pro nové volební období (sliby vs. skutečnost, noví zastupitelé)
  — v1 jen připravená struktura dat, bez obsahu.
- **P-23:** Napojení na registr smluv / Hlídač státu API (výpis posledních smluv).
- **P-24:** Převod „co by se za to dalo pořídit" (oprava X m chodníku apod.).
- **P-30:** Stránka „Pro další obce a občany": jak web vznikl, co dělala AI
  a co kontroloval člověk, odkaz na veřejný repozitář a vlastní kód/text pod
  otevřenou licencí. Lze dokončit už ve v1, pouze pokud neohrozí hlavní obsah.
- **P-32:** Návod „Udělejte si sami" s osmi kroky občanské datové analýzy,
  prompty, odhadem času a rubrikou „čeho se vyvarovat". Koncept je v
  `NAVOD-UDELEJTE-SI-SAMI.md`; stejně jako P-30 je volitelný pro v1.
- **P-33:** Web rozliší, kolik z ročních výdajů tvoří **opakovaný běžný chod**
  obce a kolik **jednorázové položky** daného roku. Pravidlo je doložitelné
  z dat, ne z právního výkladu: opakovaná je agenda (paragraf) s nenulovým
  výdajem ve všech sledovaných letech; jednorázová je ta, která se objevuje
  nepravidelně, plus kapitálové výdaje. Zobrazuje se jako dvě části sloupce
  s vysvětlením v jedné větě a je označeno jako **zařazeno autorem** (P-4);
  metodika a hraniční případy jsou v `data/rozpocet-metodika.md`, který
  schvaluje Petr. Web **nepoužívá pojem „mandatorní výdaje"** ani netvrdí,
  že opakovaný výdaj je ze zákona povinný nebo že jednorázový je zbytný.
- **P-31:** Zásobník pro v2+ (každý nápad se před realizací zváží proti §7):
  mapa investic v obci (co se kde opravilo a za kolik); roční jednostránkový
  report „Rozpočet za 60 sekund" ke stažení a tisku do schránek; interaktivní
  „kam šla moje tisícovka" (rozpočítání daní občana na agendy); AI shrnutí
  zápisů ze zastupitelstva se seznamem přijatých usnesení; upozornění na
  novinky (RSS); veřejný errata log (nalezené a opravené chyby webu).

## 7. Co v první verzi NEBUDE (závazné)

1. **Žádná automatika napojená na MONITOR** — v1 se staví z ručně ověřených dat;
   automatizace až v2, aby chyba pipeline nemohla poškodit důvěryhodnost při startu.
2. **Žádné srovnání s okolními obcemi** — vyžaduje MONITOR pipeline a pečlivý
   výběr srovnatelných obcí; polovičaté srovnání by byl snadný terč kritiky.
3. **Žádný redakční systém, přihlašování, komentáře ani diskuse** — statický web;
   reakce občanů jde přes e-mail.
4. **Žádné hodnocení současného/nového vedení** — web hodnotí hospodaření,
   ne osoby; sekce pro další období zůstává prázdná struktura.
5. **Žádná anglická verze, žádný newsletter, žádné sociální sítě jako součást
   webu** — sdílení řeší OG metadata.
6. **Žádné hodnocení ani predikce výsledků běžících soudních či správních
   řízení** a žádné spekulace o motivech — obě části jsou rejstřík faktů se
   zdroji, ne komentář.

Když bude chuť něco přidat: buď to jde do „až potom", nebo se za to musí
něco z v1 vyškrtnout.

## 8. Data a soubory

| Zdroj | Co | Kde |
|---|---|---|
| Deník účtu 518 2022–2025 | 1 335 účetních zápisů (účetní rok, datum dokladu, doklad, částka, popis, pracovní kategorie) | `4_PRŠTICE/2026_06_22 Analýza účtu 518/Detail_uctu_518_Prstice.html` ř. 160 (JSON); originál zůstává mimo veřejný repozitář |
| Rozvaha + VZZ 2015–2025 | 2 609 položek vč. řady účtu 518 | `4_PRŠTICE/2026_04_30 Audit hospodaření obce/audit-prstice-rozvaha-vzz-dashboard.html` (`<script id="audit-data">`) |
| Rozpočet dle paragrafů/položek | FIN 2-12 M — **nutno stáhnout** z otevřených dat MONITOR (IČO 00282405) | monitor.statnipokladna.gov.cz/datovy-katalog/open-data |
| Chronologie a č. j. | kompletní časová osa | `4_PRŠTICE/2026_08_15 Opakovaná žádost.../2026_08_15_Kontrola_lhut_a_procesniho_postupu.md` |
| Rozbory témat | GDPR, jeřáb, právní služby, slabá místa A1–A10 | složky `2026_08_15*`, `2026_04_30*` |
| PDF dokumenty procesu | žádosti, sdělení OUPR-867-2026, stížnost, podání na KrÚ, dodejky | **jen na Petrově Macu** — do veřejného repa pouze strojově anonymizované deriváty |
| Deník 518 za 1–6/2026 | poskytnut 3. 8. 2026 (OUPR-1007/2026) | pouze samostatně označený detail leden–červen 2026, ne celý rok |
| Soudní a správní řízení | odpověď obce na žádost z 15. 8. 2026, soudní databáze a rozhodnutí správních orgánů včetně ÚOHS | `data/rizeni.json` s povinným polem `typ` |
| Žádosti 106 | chronologie a stavy všech podaných žádostí | `data/zadosti-106.json` — sestaví se ze složek žádostí (viz PLAN 1.6) |
| Počty obyvatel | roční stavy 2015–2026 pro přepočet na obyvatele (P-2) | ČSÚ otevřená data → `data/obyvatele.json` (PLAN 1.5) |

**Známé mezery v datech** (na webu se přiznávají, nezakrývají): účetní detail
za roky 2015–2021 není k dispozici a nebude pro v1 znovu vyžadován; u detailu
od roku 2022 chybějí dodavatelé; chybějí smlouvy a faktury k části vybraných
výdajů; kategorie zápisů jsou přiřazené autorem podle krátkých popisů. Proto lze
z detailu doložit, **co tvoří rozdíl**, ale ne vždy skutečný důvod, rozsah služby
nebo přiměřenost ceny.

## 9. Hranice a rizika

- **Právní:** skutková tvrzení jen doložená; hodnotící soudy jen z pravdivého
  základu, bez znevažujících excesů; u soukromých dodavatelů opatrněji než
  u veřejných funkcionářů; obci vždy prostor k vyjádření. Judikatura NSS chrání
  roli „společenského hlídacího psa" — ale jen při férové práci s fakty.
- **Ochrana osobních údajů:** soukromé originály a veřejné deriváty jsou
  oddělené. Sanitizaci strukturovaných dat i PDF provádí lokální skript; Petr
  kontroluje jeden konsolidovaný report a schvaluje aktuální výstupy (P-8).
- **Reputační:** web musí obstát při nepřátelském čtení — proto P-1, P-4, P-5.
- **Nesouběh s řízením:** web popisuje stav řízení věcně; nepředjímá výsledek
  rozhodnutí KrÚ ani případného soudu.
- **Bezpečnostní:** žádné API klíče v repozitáři; repozitář neobsahuje
  neanonymizované dokumenty ani v historii commitů.

## 10. Ekonomika

Doména ~300 Kč/rok. Hosting (Netlify/GitHub Pages) zdarma. Ostatní práce
vlastními silami s AI. Celkové provozní náklady < 500 Kč/rok.

## 11. Jak poznáme úspěch

- Web je živý na transparentniprstice.cz **nejpozději 15. 9. 2026**.
- Při závěrečném dvouminutovém průchodu Petr bez otevírání metodiky najde
  odpověď na otázky: „S kolika penězi obec hospodaří? Jak se účet 518 změnil?
  Které skupiny tvoří meziroční rozdíl a co zatím nevíme?"
- 100 % publikovaných čísel má zdroj nebo reprodukovatelný výpočet; automatické
  kontrolní součty projdou a AI zkontroluje všechna publikovaná skutková tvrzení.
- Přidání nové události do chronologie trvá do 15 minut a zvládne to AI
  na jeden pokyn (test před spuštěním).

## 12. Otevřené otázky

- ~~Přesný název domény~~ → **VYŘEŠENO 21. 8. 2026:** zaregistrována
  transparentniprstice.cz, repozitář novotny25/transparentniprstice.cz.
- **[ROZHODNUTO]** Hlavní roční řada účtu 518 zobrazuje uzavřené roky
  2015–2025. Účetní detail začíná rokem 2022; leden–červen 2026 jde do v1
  pouze jako samostatně označené neúplné období. Detail roku 2021 se nezískává.
- **[OTEVŘENÉ — rozhodne se v úkolu 5.1]** Návštěvnostní statistika: buď
  GoatCounter/Plausible bez cookies, nebo v1 zcela bez měření.
- ~~Termín komunálních voleb~~ → **VYŘEŠENO:** 9.–10. 10. 2026; zveřejnění
  webu před volbami je vědomé rozhodnutí autora.
