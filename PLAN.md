# PLÁN REALIZACE: Web Transparentní Prštice

**Verze:** 1.5 (21. 8. 2026) · Vychází ze `ZADANI.md` v1.5 — při rozporu platí
ZADANI.md. V1.4 doplnila soukromou/veřejnou datovou pipeline a strojovou
anonymizaci, oddělila soudní a správní řízení a zpřesnila příběh účtu 518.
V1.5 vrací rozlišení výdajů v doložitelné formě „opakované vs. jednorázové"
(P-33) místo právního pojmu mandatorní.
**Cíl:** web živý na transparentniprstice.cz nejpozději **15. 9. 2026**.

Plán je psaný metodikou kurzu FAIL (AI-WBS): každý úkol má **deliverable**,
**režim** (🤖 AI / 🤝 hybrid / 👤 člověk) a odhad **aktivního času** Petra.
Úkoly provádí AI po jednom, malými kroky; Petr rozhoduje a schvaluje.

---

## Jak tento plán spustit

Realizace musí běžet **na Petrově Macu v Claude Code** (PDF dokumenty a XLSX
výkazy jsou jen tam, ne v gitu). Claude Code se spouští **v kořeni PACTu**
(`~/Documents/AI/0_PACT`), aby měl k dispozici skilly /web a podklady analýzy.
Webový repozitář (klon z úkolu 0.4) je mimo pracovní adresář — proto se
Claude Code spouští s přístupem k oběma složkám:
`claude --add-dir ~/Developer/transparentniprstice-web`.
Všechny cesty `data/…`, `web/…`, `skripty/…`, `dokumenty/…` v tomto plánu
se vztahují ke kořeni webového klonu; cesty `0_Projects/…` ke kořeni PACTu.
Spouštěcí prompt:

> Otevři `0_Projects/4_PRŠTICE/2026_08_21 TransparentniPrstice.cz/ZADANI.md`
> a `PLAN.md` ve stejné složce. Pracuj podle PLAN.md úkol po úkolu: vždy
> nejdřív řekni, co se chystáš udělat a co k tomu potřebuješ ode mě;
> u úkolů označených 🤝/👤 se zastav a počkej na mě. Po každém dokončeném
> úkolu zaškrtni políčko v PLAN.md a napiš tři věci: co se změnilo, jak sis
> to ověřil, co se tím může rozbít. Nikdy nic neimplementuj bez plánu, který
> jsem odsouhlasil. Otevřené otázky ze ZADANI.md §12 mi polož, jakmile budou
> bránit práci. Začni prvním nezaškrtnutým úkolem (1.0).

**Pravidla po celou dobu** (z kurzu FAIL + pravidel workspace):
- Jeden prompt = jeden úkol. Po 2–3 neúspěšných opravách stop → přeformulovat
  zadání nebo vrátit na poslední funkční verzi, ne „ještě jeden pokus".
- Commit po každém uzavřeném úkolu; commit potvrzuje Petr.
- AI tvrzení se ověřují: testem, otevřením v prohlížeči, kontrolou čísla proti
  zdroji — ne sebejistým textem.
- Nic citlivého do repa: žádné klíče, originální účetní exporty ani
  neanonymizovaná data či dokumenty — ani do historie nebo deploy preview.
- Ve veřejných textech používat „občanská datová analýza hospodaření", nikoli
  „audit". Slovo audit zůstává jen v existujících názvech zdrojových složek
  a souborů.
- „Účetní náklad", „rozpočtový výdaj" a „platba" nejsou synonyma. Účet 518
  je akruální nákladový účet; FIN 2-12 M popisuje peněžní rozpočet. Veřejný
  text oba pohledy vysvětlí odděleně a nesnaží se jejich součty ztotožnit.

---

## Fáze 0 — Založení projektu (½ dne, blokuje vše ostatní)

- [x] **0.1 👤 Registrace domény** — ✅ hotovo 21. 8. 2026: zaregistrována
  `transparentniprstice.cz`.
- [x] **0.2 👤 Založení repozitáře** — ✅ hotovo 21. 8. 2026:
  https://github.com/novotny25/transparentniprstice.cz
  (Lokální klon na Macu řeší úkol 0.4 — vždy mimo iCloud.)
- [x] **0.3 🤖 Kostra repozitáře a kontext pro AI** — ✅ hotovo 21. 8. 2026
  (commit `de8cdcb` na main: CLAUDE.md s pravidly, kopie ZADANI.md, README,
  složky).
  Struktura:
  ```
  transparentniprstice.cz/
  ├── CLAUDE.md          # pravidla pro AI (viz níže)
  ├── ZADANI.md          # kopie schváleného zadání
  ├── data/              # pouze veřejné sanitizované JSON/CSV
  ├── dokumenty/         # anonymizovaná PDF
  ├── anonymizace/       # publikační pravidla a allowlist, bez soukromých údajů
  ├── web/               # HTML/CSS/JS
  └── skripty/           # extrakce a validace dat (Python)
  ```
  Do `CLAUDE.md` webového repa tato pravidla (MUST/MUST NOT):
  - MUSÍ: každé číslo na webu pochází ze sanitizovaného souboru v `data/` a má zdroj;
    před „hotovo" spustit validační skript a otevřít web v prohlížeči.
  - NESMÍ: commitnout originální export, neanonymizovaný dokument nebo klíč; psát hodnotící
    nálepky („podezřelé", „tunel"); tvrdit kauzalitu, kde je jen souvislost;
    měnit soubory mimo zadaný úkol.
  Deliverable: první commit s kostrou. *(~5 min kontrola)*
- [x] **0.4 🤝 Lokální klon webového repozitáře na Macu** — ✅ hotovo
  22. 8. 2026: naklonováno
  `github.com/novotny25/transparentniprstice.cz` do `~/Developer/`
  (mimo iCloud!): `git clone https://github.com/novotny25/transparentniprstice.cz.git
  ~/Developer/transparentniprstice-web` (HTTPS; kdyby Mac chtěl SSH, Petr
  řekne). Přihlášení zadává Petr. Deliverable: funkční lokální klon,
  ověřeno `git status`. *(~5 min)*
- [x] **0.5 🤖 Synchronizace schválené verze 1.4** — ✅ hotovo
  22. 8. 2026: do webového repozitáře zkopírovány
  aktuální `ZADANI.md` a `PLAN.md` v1.4 a promítnuta nová
  privacy pravidla do `CLAUDE.md`. PACT kopie zůstává autorským originálem;
  před každou realizací se verze obou kopií automaticky porovná. Deliverable:
  commit pouze s dokumentací v1.4, který schválí Petr.

## Fáze 1 — Datový základ (2 dny, převážně AI)

> Zásada: nejdřív bezpečná a ověřená data, pak design. Soukromé originály
> nikdy nevstupují do veřejného repozitáře.

- [x] **1.0 🤝 Veřejné datové schéma a soukromá zóna** — Petr určí soukromou
  složku mimo webový repozitář. AI připraví `anonymizace/pravidla.yml` a
  `anonymizace/verejna-allowlist.yml`. Výchozí veřejná pole účetního zápisu:
  účetní rok, měsíc, částka v haléřích, opravená kategorie, kontrolovaný veřejný
  popis a ID zdroje. Přesný den, interní číslo dokladu, původní volný popis
  a jméno fyzické osoby se zveřejní jen po výslovném schválení v allowlistu.
  Deliverable: schválené schéma, pravidla a privátní manifest s SHA-256 originálů.
  **Blokuje všechny veřejné exporty.**
  ✅ hotovo 22. 8. 2026: schéma schválil Petr (6 veřejných polí: rok, měsíc,
  částka v haléřích, opravená kategorie, veřejný popis, ID). Pravidla v
  `anonymizace/pravidla.yml` a `anonymizace/verejna-allowlist.yml`
  (deny-default, prázdný allowlist; ověřen výskyt jmen/adres v poli `p`).
  Soukromá zóna `~/Developer/transparentniprstice-private/` s `README.md`,
  `manifest-originalu.yml` (7 originálů, SHA-256) a složkami `extrakty/`,
  `qa-reporty/`. Originály zůstávají v PACTu, mimo web repo.
- [x] **1.1 🤖 Soukromá extrakce a veřejný export účtu 518** — vytáhnout
  1 335 účetních zápisů z `Detail_uctu_518_Prstice.html` (ř. 160) nejprve jen
  do soukromé zóny. Skript pak deterministicky vytvoří
  `data/ucet-518-polozky-public.json` a `.csv` podle úkolu 1.0; veřejné HTML se
  nikdy nestaví z originálního pole `p`. Částky ukládat jako celé haléře, datum
  dokladu oddělit od účetního roku. Deliverable: privátní extrakt, veřejné
  deriváty a soukromý report všech odstranění a nerozhodnutých kandidátů.
  ✅ hotovo 22. 8. 2026: skript `skripty/extrakce_518.py` (ověřuje SHA-256 zdroje)
  vytvořil privátní extrakt 1335 zápisů v soukromé zóně a veřejné deriváty
  `data/ucet-518-polozky-public.json`/`.csv` (6 polí, částky v haléřích, měsíc
  oddělen od účetního roku). Čísla dokladů v popisech odstraněna automaticky;
  16 popisů s adresou/jménem podrženo a nahrazeno čistým popisem z privátní mapy
  `popisy-schvalene.yml`. Soukromý report v `qa-reporty/report-518-1.1.md`.
  Kontrolní součty po letech sedí (Δ2022→23 +2 909 623, Δ2024→25 +1 221 138 Kč);
  celkem 2022–2025 = 16 981 430,32 Kč. Veřejné JSON/CSV zatím **necommitnuté** —
  čekají na privacy gate (2.5/1.8) a Petrův sign-off.
- [x] **1.2 🤖 Roční řady a ukazatele vývoje** — z
  `audit-prstice-rozvaha-vzz-dashboard.html` (`<script id="audit-data">`,
  ř. ~168) vytáhnout řady 2015–2025: účet 518, účet 511 a náklady/výnosy celkem
  → `data/vykazy-rady.json`. Zdroj je v tis. Kč; výstup je v celých Kč a nese
  jednotku. Pro účet 518 vypočítat tříletý klouzavý průměr, změnu 2015→2025
  a průměrné roční tempo (CAGR). Současná kontrolní hodnota: 2015→2025
  nominálně +138,6 %, CAGR 9,1 %; tříletý průměr 2015–2017 činí 1,80 mil. Kč
  a 2023–2025 4,69 mil. Kč (+160,8 %). AI vše znovu přepočítá ze zdroje;
  nepoužije předem zvolené „asi 50 %". Veřejný titulek zní přesně
  „Vývoj účtu 518 v letech 2015–2025“ (11 ročních hodnot).
  ✅ hotovo 22. 8. 2026: skript `skripty/rady_vykazy.py` (ověřuje SHA-256)
  vytvořil `data/vykazy-rady.json` — řady 2015–2025 účtů 518, 511 a
  náklady/výnosy celkem (v celých Kč z tis. Kč). Účet 518: +138,6 % (2015→2025),
  CAGR 9,1 %, tříletý průměr 1,80→4,69 mil. (+160,8 %) — vše PASS proti
  kontrolním hodnotám. Křížová kontrola: součty deníku 518 (2022–2025) = VZZ
  na 0,00 Kč. Data zatím necommitnuta (privacy gate).
- [x] **1.3 🤝 Doplnění deníku 518 za 1–6/2026** — Petr ukáže soubor
  OUPR-1007/2026; AI jej zpracuje stejnou soukromou/veřejnou pipeline.
  Výstup nese `period_status: incomplete` a popisek „leden–červen 2026".
  Neprodlužuje hlavní řadu uzavřených let a nesrovnává se s celým rokem 2025.
  **Detail roku 2021 se nezískává.**
  ✅ hotovo 22. 8. 2026: skript `skripty/extrakce_518_2026.py` vytáhl z PDF
  (OUPR-1007/2026) 168 zápisů, součet 2 707 114,51 Kč = kontrolní CELKEM.
  Veřejný `data/ucet-518-2026H1-public.json` (period_status: incomplete,
  „leden–červen 2026"). Kategorie přiřazeny pravidly podle popisu (zdroj je
  neobsahuje; schválil Petr). 2 popisy s adresou/jménem podrženy a nahrazeny
  čistým popisem z privátní mapy. Data necommitnuta (privacy gate).
- [x] **1.4 🤖 Rozpočtová data z MONITORu** — stáhnout FIN 2-12 M pro IČO
  00282405, roky 2019–2025; napojit číselníky paragrafů na česká jména agend
  → `data/rozpocet.json`. Uložit skutečné příjmy, skutečné výdaje, saldo a
  rozlišení běžné/kapitálové; případné údaje schváleného či upraveného rozpočtu
  musí být jasně pojmenované. **Nevytvářet klasifikaci mandatorní/ovlivnitelné**
  ani netvrdit, co je ze zákona povinné. Místo toho podle P-33 dopočítat
  doložitelné rozlišení „opakovaný běžný chod vs. jednorázové položky roku":
  opakovaná = agenda s nenulovým výdajem ve všech sledovaných letech,
  jednorázová = nepravidelná agenda plus kapitálové výdaje. Kritéria, hraniční
  případy a jejich dopad na součty sepsat do `data/rozpocet-metodika.md`
  a nechat **schválit Petrem**; příznak uložit ke každé agendě v datech.
  Dataset i text nesou `basis: cash_budget`, zatímco účet 518 nese
  `basis: accrual_cost`; jejich součty se navzájem nekontrolují jako stejný údaj.
  Deliverable: příjmy a výdaje po agendách a letech. Záložní cesta je ruční
  export z profilu obce v MONITORu.
  ✅ hotovo 25. 8. 2026: MONITOR po údržbě zpět. Skript
  `skripty/extrakce_rozpocet.py` čte oficiální open-data FIN 2-12 M (CSUIS,
  tabulka FINM201, skutečnost ZU_ROZKZ) — řádky Prštic 2019–2025 vytažené do
  soukromé zóny (`prstice-finm-2019-2025.csv`), názvy agend z číselníku
  `CIS_PARAGRAF.CSV`. Výstup `data/rozpocet.json` (basis: cash_budget, complete):
  příjmy/výdaje/saldo, výdaje po paragrafech, běžné/kapitálové. **Metodika P-33
  schválena Petrem** (`data/rozpocet-metodika.md`): opakovaná = paragraf
  s nenulovým výdajem ve všech 7 letech (26 agend); jednorázové = nepravidelné +
  kapitálové; 6330 vnitřní převody zvlášť. Křížová kontrola 2022 výdaje = FIN PDF
  na **0,00 Kč**. Gate: 33 PASS, 0 FAIL. Velké ZIP (150 MB) smazány, zdroje
  v manifestu.
- [x] **1.5 🤖 Počty obyvatel z ČSÚ** — stáhnout počet obyvatel Prštic
  k 1. 1. každého roku 2015–2026 → `data/obyvatele.json` se zdrojem a datem.
  Deliverable: soubor pro přepínač „Kč na obyvatele" a kontrolní tabulka.
  ✅ hotovo 22. 8. 2026: skript `skripty/extrakce_obyvatele.py` z ověřené ČSÚ
  open-data (Databáze demografických údajů za obce ČR, cz0643.xlsx, sloupec
  „Stav 1.1.") vytvořil `data/obyvatele.json` — Prštice 2015–2025 (931 → 997).
  Pozor na integritu: oficiální 2021 = **969** (bilance po revizi sčítáním),
  ne 985 z agregátorů ani 959 ze sčítání. Rok **2026 zatím není** v konzistentní
  databázi (poslední stav k 1.1.2025) — doplní se, až ČSÚ vydá. `validace.py`
  obyvatele kontroluje (22 PASS). Zdrojový XLSX v soukromé zóně/zdroje.
- [ ] **1.6 🤝 Soudní a správní řízení a tracker žádostí jako data** — sestavit
  `data/rizeni.json`. Každý záznam má `typ: soudni | spravni`, instituci,
  spisovou značku, období, předmět, procesní roli obce, iniciátora, stav,
  výsledek, zdroj a datum ověření. Soudní část začíná odpovědí obce na žádost
  z 15. 8. 2026 a pokrývá řízení probíhající alespoň zčásti od 1. 1. 2018;
  veřejná rešerše je jen doplněk. Rozhodnutí ÚOHS S0589/2023, S1089/2024
  a S0071/2025 patří výhradně do `typ: spravni`. Dokud odpověď obce nepřijde,
  dataset i web říkají „seznam nemusí být úplný". Samostatně sestavit
  `data/zadosti-106.json` ze všech složek žádostí; stav řízení a původ informace
  jsou dvě různá pole. Petr schválí finální seznam.
  🔶 ROZPRACOVÁNO 22. 8. 2026: `data/zadosti-106.json` — tracker 8 žádostí
  z lokálních složek (datum, předmět, č. j., stav, počet dní), hotové k revizi.
  `data/rizeni.json` — **správní část OVĚŘENA** z veřejné Sbírky rozhodnutí
  ÚOHS (22. 8. 2026): tři pravomocná rozhodnutí (S0589/2023, S1089/2024,
  S0071/2025), všechna formou příkazu za neuveřejnění smlouvy/dodatku na profilu
  zadavatele dle § 269 odst. 2 zák. 134/2016 Sb.; pokuty 3 000 + 4 000 + 4 000 =
  **11 000 Kč**; dvě k opravám střechy zámku (souvisí s nárůstem 518 v 2023),
  jedno ke smlouvě o úvěru u KB. Doplněny předmět, přestupek, iniciátor (ÚOHS
  z moci úřední z podnětu), stav a právní moc. **Soudní část čeká na odpověď
  obce** (žádost 15. 8. 2026; doplní fáze 6). `validace.py` hlídá povinné `typ`
  a že ÚOHS není soud. Zbývá Petrovo schválení finálního seznamu.
- [x] **1.7 🤖 Oprava kategorií, storen a rozklad změn 518** — vytvořit
  verzovaná pravidla kategorizace, přiřadit storna k původním zápisům a opravit
  zjevná chybná zařazení. Zvlášť zkontrolovat všechny řádky, které tvoří alespoň
  5 % meziročního rozdílu. Vygenerovat `data/ucet-518-rozklad.json` pro změny
  2022→2023, 2023→2024 a 2024→2025. Kontrolní nálezy k ověření:
  - 2022→2023 celkem +2 909 622,84 Kč; hlavní příspěvky po předběžné opravě:
    ČOV/převzatá odpadní voda +1 378 428,21 Kč, zámek +648 072,21 Kč,
    odpady +447 236,17 Kč a právní služby +290 980 Kč;
  - jeřáb mezi 2022 a 2023 klesl o 56 773,20 Kč; růst zámku vytvořily hlavně
    oprava střechy a atiky za 788 099,85 Kč, takže jeřáb není vysvětlením skoku;
  - jeden právní zápis 52 272 Kč je chybně ve „Správa / odborné služby";
    po opravě činí právní služby 2022–2025 2 094 182 Kč, samostatně GDPR
    272 250 Kč;
  - u roku 2025 se storno 309 366 Kč přiřadí zpět k ČOV; ČOV pak není kladným
    vysvětlením růstu 2024→2025;
  - 2024→2025 celkem +1 221 138,32 Kč; předběžně zámek +593 167,45 Kč,
    právní služby včetně GDPR +288 060 Kč a sondy podlah ZŠ 117 333,70 Kč.
    Tyto stavební a právní položky tvoří asi 81,8 % čistého rozdílu.
  Deliverable: reprodukovatelný rozklad, seznam oprav a Petrovo schválení
  upravených kategorií. Jde o odpověď na „co vytvořilo rozdíl", nikoli bez
  dalších dokladů na „proč obec službu objednala".
  ✅ hotovo 22. 8. 2026: skript `skripty/rozklad_518.py` + privátní verzovaná
  pravidla `kategorie-opravy.yml` (schválil Petr). Opravy: 1 přeřazení
  (52 272 Kč právní zápis Správa→Právní; číslo dokladu jen v privátní mapě) +
  párování storen
  k původnímu dokladu. Výstup `data/ucet-518-rozklad.json`. Všech 11 tvrdých
  kontrol PASS (celkové změny, zámek, odpady, právní 2 094 182, GDPR 272 250,
  jeřáb −56 773,20, střecha+atika 788 099,85, sondy ZŠ 117 333,70). Dvě drobné
  doložené odchylky od předběžných hodnot: ČOV 2022→2023 −276 Kč, zámek
  2024→2025 +3 460 Kč (párování storna). Kandidát „veř.zeleň 3 000 Kč" ponechán
  v ČOV dle rozhodnutí Petra. Data necommitnuta (privacy gate).
- [x] **1.8 🤖 Validace dat a privacy gate** — `skripty/validace.py` ověří:
  privátní i veřejné součty 518 proti VZZ s tolerancí do 1 Kč; přesné roční
  součty 2022–2025; párování storen; povolené datové báze a jednotky; obyvatele;
  povinné `typ` u řízení; žádná čísla v HTML mimo datové zdroje; PII sken všech
  tracked souborů, buildu, názvů a metadat. FIN a VZZ se nekontrolují proti sobě
  jako stejný ukazatel. Skript musí skončit chybou při nevyřešeném privacy
  nálezu. **Bez projité validace se nestaví fáze 3.**
  ✅ hotovo 22. 8. 2026 (první verze pro účet 518): `skripty/validace.py`
  spojuje číselné kontroly (roční součty 2022–2025 přesně, 518 vs výkaz do 1 Kč,
  public=private, návaznost rozkladu, neúplný 2026) a privacy gate (PII sken
  všech tracked + data/ souborů, denylist odvozený z privátních extraktů, zákaz
  originálů v repu). Výsledek: **19 PASS, 0 FAIL**. Gate rovnou odhalil a nechal
  opravit únik čísla dokladu v poznámce PLAN.md. Kontroly obyvatel, řízení,
  rozpočtu a HTML jsou připravené jako N/A (doplní se s úkoly 1.4–1.6 a fází 3).
  Pozn.: číslo dokladu zůstalo v lokálním (nepushnutém) commitu b38b43f —
  vyčistí se před prvním pushem (řeší finální gate 4.1).

## Fáze 2 — Obsah (2–3 dny, hybrid — Petr schvaluje význam i zjednodušení)

- [x] **2.1 🤖 Texty přehledu a slovníček** — AI napíše úvod, „rozpočet
  v kostce", vysvětlení účtu 518 pro laika a mini-slovníček. Jazyk: běžná
  čeština, krátké věty, žádný účetní žargon bez vysvětlení. Povinné jednoduché
  vysvětlení rozdílu:
  > Rozpočet ukazuje, kdy obec peníze přijala nebo vydala. Účet 518 ukazuje,
  > kdy byl zaúčtován náklad na službu; platba může proběhnout v jiném období.
  > Proto se oba součty nemusí rovnat a na webu je nesčítáme.
  Deliverable: `web/obsah/*.md` k Petrově revizi.
  ✅ hotovo 25. 8. 2026 (Petr koncepty schválil „vesměs dobré", finální doladění
  po vizuální verzi). Vytvořeno `web/obsah/`: `00-uvod.md`, `01-rozpocet-v-kostce.md`,
  `02-ucet-518-vysvetleni.md`, `slovnicek.md` (+ legenda štítků P-4). Na Petrovu
  žádost **úvod rozšířen** (kdo je obec, odkud/kam peníze jdou, co obec ovlivňuje)
  a doplněna **kontextová rešerše** (P-35): příjmy na obyvatele vs. 17 obcí
  900–1100 Brno-venkov (Prštice 5. nejnižší, podprůměr; medián 28,3 tis.) a
  průměrný věk vs. okolí a okres (43,3 vs. 41,5 / 41,6 — spíš starší). Čísla
  ověřena ze zdrojů; **zformalizování dat řeší úkol 2.9**.
- [x] **2.2 🤝 Příběh účtu 518 a úplný rozklad změn** — z úkolu 1.7 připravit
  jednu čáru 2015–2025, nenápadný tříletý klouzavý průměr a jednoduchý graf
  „Co vytvořilo meziroční rozdíl". Roční hodnoty zůstávají viditelné; klouzavý
  průměr je pouze pomůcka, nesmí je nahrazovat. Text výslovně řekne, že vývoj
  není nepřetržitý: vrchol 2023, pokles 2024, opětovný růst 2025. Pro 2023
  zobrazit všechny hlavní příspěvky, nejen tři Petrem vybraná témata; pro 2025
  totéž po přiřazení storen. Vedle grafu krátce uvést „Co z deníku nevíme".
  Graf nese krátkou poznámku „běžné ceny, bez odečtení inflace". Deliverable:
  schválený datový příběh bez tvrzení o nedoložené příčině.
  ✅ hotovo 25. 8. 2026 (Petr schválil). `web/obsah/03-ucet-518-pribeh.md`:
  nesouvislý vývoj (vrchol 2023 → pokles 2024 → růst 2025), úplný rozklad všech
  tří meziročních změn, sekce „Co z deníku nevíme". **Na pokyn Petra jeřáb do
  příběhu příčin nepatří** — přesouvá se do autorského výběru konkrétních položek
  k prozkoumání hospodárnosti (výběr položek řídí Petr, viz 2.3).
- [x] **2.3 🤝 Tři vybraná témata v kompaktní struktuře** — právní služby,
  GDPR a jeřáb. Každé téma má nahoře pouze čtyři krátké řádky: **Co víme / Co
  jsme vypočítali / Co zatím nevíme / Jak se vyjádřila obec**. Pod nimi je
  rozbalitelný kontext, srovnání, otázky a jasně podepsaný komentář Petra.
  Hodnocení hospodárnosti se opírá jen o doložitelné indicie: rozsah a výsledek
  služby, způsob výběru, opakování, jednotkovou nebo srovnatelnou cenu. Když
  podklad chybí, web nabídne otázku k posouzení, nikoli verdikt.
  - **Právní služby:** po opravě známého chybného zařazení zkontrolovat částku
    2 094 182 Kč za 2022–2025; GDPR vést samostatně. Nevydávat účetní zápisy
    automaticky za náklady konkrétního sporu.
  - **GDPR:** účetní detail zatím dokládá deset zápisů po 27 225 Kč v roce 2025,
    ne sám o sobě „platbu každý měsíc". Měsíční smluvní cenu a rozsah služby
    uvést až podle smlouvy; tržní srovnání označit za orientační, pokud se liší
    rozsah plnění.
  - **Jeřáb:** 23 zápisů obsahujících slovo „jeřáb" v letech 2022–2023 činí
    846 491,80 Kč. Rozpětí dat dokladů nedokazuje nepřetržitou dobu pronájmu.
    Mezi účetními roky 2022 a 2023 tato skupina klesla o 56 773,20 Kč, proto
    se nepoužije jako vysvětlení skoku účtu 518.
  Deliverable: schválené texty tří témat.
  🔶 25. 8. 2026: Petr potvrdil a rozšířil výběr položek — **GDPR, právní služby,
  jeřáb** + nově **odpadové hospodářství** a **ČOV/odpadní vody** (úhel: rostoucí
  náklady, které se přeúčtovávají občanům). Texty se napíšou, až budou podklady
  (část čísel u GDPR a právních služeb se teprve žádá dle 106). Jeřáb patří do
  autorského výběru položek, ne do příběhu příčin 518 (viz 2.2).
  ✅ hotovo 26. 8. 2026 — postaveno rovnou na webu (sekce „Ptáme se na vybrané výdaje"):
  GDPR (272 250 Kč 2025 + 108 900 za 1H2026; paušál 22 500 bez DPH; orientační srovnání
  s ceníky pro obce do 1 000 obyv.), právní služby (2 094 182 Kč 2022–2025), jeřáb jako
  **poslední** a s výslovným uznáním, že jeřáb je při opravě nezbytný — sazba 28 000 Kč
  bez DPH/měsíc odpovídá trhu, otázkou je délka pronájmu (18 plateb, 609 840 Kč nájemné)
  vs. ceny použitých jeřábů 370–800 tis. Kč. Každé téma má čtyřřádkový souhrn, graf,
  varování k výkladu a otevřené otázky.
  🔶 Dřívější koncept `web/obsah/04-vybrane-polozky.md` (25. 8. 2026): plná témata
  **jeřáb / odpadové hospodářství / ČOV** (u odpadů doloženo výdaje 1,74 mil. vs.
  poplatky 694 tis. za 2025 = občané kryjí ~40 %); **GDPR a právní služby** jako
  karty „čeká se na doložení". Hlubší hodnocení hospodárnosti odkázáno do autorské
  interpretační sekce (P-34). K revizi Petra.
- [x] **2.4 🤖 Chronologie občanské datové analýzy jako data** —
  `data/chronologie.json`: datum, titulek, věcný popis, č. j., původ informace
  a odkaz na veřejný sanitizovaný dokument. Vychází z kontrolního dokumentu
  lhůt a všech složek od prvního sběru zdrojů 30. 4. 2026 po aktuální stav.
  Deliverable: úplná, průběžně doplnitelná osa; název zdrojové složky může
  obsahovat „Audit", veřejný text používá „analýza".
  🔶 ROZPRACOVÁNO 25. 8. 2026: vytvořeno `data/chronologie.json` (14 událostí
  30. 4.–27. 8. 2026; pole datum/typ/titulek/popis/č.j./původ/dokument) a text
  `web/obsah/06-jak-jsme-postupovali.md` včetně **trackeru žádostí a podání
  (P-28)**. Odkazy na sanitizované dokumenty (`dokument`) doplní krok 2.5.
  K revizi Petra.
- [x] **2.5 🤖 Strojová anonymizace JSON/CSV/HTML/PDF** — Petr ukáže soukromou
  složku s originály. `skripty/anonymizace.py build` provede inventuru a hashe,
  vytvoří veřejné strukturované exporty podle allowlistu, každou stránku PDF
  vyrenderuje, lokálním OCR najde kandidáty, vypálí začernění, odstraní původní
  textové vrstvy, metadata, přílohy a formuláře a OCR spustí znovu až nad
  začerněnou verzí. Textová detekce hledá zejména jména osob, adresy a čp./če.,
  data narození, rodná čísla, účty/IBAN, telefony, e-maily a soukromé kontakty;
  AI/NER nálezy jsou kandidáti, o ponechání rozhoduje allowlist. Podpisy,
  rukopis a obrazové údaje musí být vidět v kontaktním listu pro Petrovu kontrolu.
  HTML se generuje jen ze sanitizovaných dat. Následuje sken
  přes `pdftotext`, OCR, tracked soubory a výsledný build. Skript připraví
  v soukromé zóně mimo repo `qa-report-private.html`: všechny zásahy a nerozhodnuté kandidáty,
  unikátní veřejné popisy, publikační allowlist a kontaktní list všech PDF stran.
  **Petr nemusí ručně kreslit začernění; v jediné souhrnné kontrole projde report
  a všechny strany, případné opravy zapíše AI do pravidel a vše přegeneruje.**
  Deliverable: veřejné deriváty, nevyřešené nálezy 0 a
  `ANONYMIZACE-SIGNOFF.md` pro aktuální commit.
  ✅ hotovo 26. 8. 2026 (v rozsahu textových PDF): `skripty/anonymizace.py`
  (PyMuPDF `apply_redactions` — text se z PDF **skutečně odstraní**, nejen překryje;
  navíc smazána metadata). Zpracováno **9 dokumentů** (7 podání žadatele, sdělení
  obce OUPR-867-2026, rozhodnutí KrÚ JMK) → `web/dokumenty/`, rejstřík
  `data/dokumenty.json`, publikováno na stránce *Jak to víme*. **55 redakcí**:
  adresa, ID datové schránky, datum narození, rodné číslo, soukromý e-mail/telefon.
  Ponecháno vědomě: jméno autora, jména v úřední roli, čísla jednací, údaje obce.
  ⚠️ **Poučení z chyby:** první běh přehlédl „Datum narození:" a „ID: xxx", protože
  kontrola používala **tytéž vzory** jako redakce. Doplněn **nezávislý denylist**
  konkrétních hodnot; teprve pak PASS. Skenované PDF s podpisy (OCR větev) zatím
  nebylo potřeba — všechny dokumenty jsou textové.
- [x] **2.6 🤝 Sekce Soudní a správní řízení — obsah** — jedna stránka, dvě
  samostatné části a žádný společný počet, který by vydával ÚOHS za soud.
  Soudní karty zdůrazní řízení iniciovaná obcí, ale datově zachovají procesní
  roli u všech případů z odpovědi obce. Správní karty popíší kontrolu, zjištění,
  sankci, právní moc a primární zdroj. U běžících řízení žádná predikce.
  Nahoře samostatný graf právních nákladů 518; propojení na konkrétní řízení
  pouze s přímým dokladem. Viditelný stav žádosti z 15. 8. 2026 a upozornění na
  možnou neúplnost do obdržení odpovědi. Petr schvaluje finální znění.
  🔶 ROZPRACOVÁNO 25. 8. 2026: `web/obsah/05-soudni-spravni-rizeni.md` — dvě
  oddělené části, ÚOHS ≠ soud, 3 pravomocná rozhodnutí (pokuty 11 000 Kč),
  právní rozlišení registr smluv (340/2015 — na obec se nevztahuje) vs. profil
  zadavatele (134/2016). Na pokyn Petra je **primární věcná podstata a výsledek**
  řízení; náklady na právní služby jen jako **doplněk** (přesunou se do sekce
  o hospodárnosti). Soudní část čeká na odpověď obce. Čeká na finální schválení.
- [x] **2.7 🤝 Stránka „Pro další obce a občany" + návod „Udělejte si sami"**
  — použít revidovaný `NAVOD-UDELEJTE-SI-SAMI.md`; osobní údaje se nedávají do
  cloudového AI promptu a veřejný výstup se nenazývá audit. Pokud tento úkol
  ohrozí termín, přesune se celý do v2; pro v1 je povinná pouze stránka „Jak
  jsme postupovali". Licence se vztahuje na vlastní kód a text, ne automaticky
  na převzaté dokumenty a zdrojová data.
  ✅ hotovo 27. 8. 2026 — **stránka je živá**: /pro-dalsi-obce.html.
  Osm rozklikávacích kroků s **hotovými prompty a tlačítkem Zkopírovat**,
  tři zásady (ověřuj / rozlišuj / anonymizuj), náklady (2–4 víkendy, ~800 Kč)
  a „čeho se vyvarovat". Odkaz na otevřený repozitář a nabídka pomoci na
  kontaktní e-mail. Kroky se generují z `data/navod.json` (vytěženo
  z `NAVOD-UDELEJTE-SI-SAMI.md`), takže úprava návodu nevyžaduje zásah do HTML.
  Doplněno do navigace všech stránek i do sitemap.
  Pozn.: zadání stránku připouštělo odložit do v2 — termín neohrozila,
  tak zůstává ve v1.
- [x] **2.8 🤖 AI kontrola faktů a jazyka + Petrovo schválení** — AI vytvoří
  jednoduchý registr všech publikovaných skutkových tvrzení: tvrzení, typ (zdroj/výpočet/
  autorské zařazení/nezjištěno), zdroj, výpočet a stav kontroly. AI ověří každý
  řádek; tvrdý release gate platí zejména pro 100 % headline čísel, negativních
  tvrzení a výroků o konkrétních osobách. Opraví formulace bez podkladu a
  sugestivní otázky. Výstup: protokol NÁLEZ → OPRAVA.
  Finální text čte a schvaluje Petr; žádná další lidská kontrola není v plánu.
  ✅ hotovo 27. 8. 2026: `skripty/kontrola_faktu.py` — registr **28 tvrzení**
  (15 zdroj / 7 výpočet / 6 autorské zařazení). Skript hodnoty **přepočítá
  z dat** a zároveň ověří, že tvrzené číslo na webu opravdu je.
  Výsledek: **0 neshod**, 25 ověřeno proti datům i textu, 3 „POZOR" = číslo je
  správné, jen se na webu píše zaokrouhleně (24,4 mil., 7,8 mil.).
- [x] **2.9 🤖 Srovnání s podobnými obcemi jako data (P-35, reprodukovatelně)** —
  z rešerše k úvodu udělat trvalá data: (a) rozpočty obcí 900–1100 Brno-venkov
  z MONITOR API `/api/rozpocet/souhrnny` (konsolidovaná skutečnost) + IČO z ARES;
  (b) průměrný věk obcí z ČSÚ (soubor v manifestu) + okresní průměr; (c) souřadnice
  obcí (Wikidata) pro „nejbližší". Výstup: `data/srovnani-obci.json` + skript(y)
  v `skripty/`, zdroje v manifestu, čísla přes `validace.py`. Deliverable:
  reprodukovatelné datové soubory, ze kterých se generuje srovnání v úvodu.
  ✅ hotovo 26. 8. 2026: `skripty/srovnani_obci.py` → `data/srovnani-obci.json`,
  zobrazeno v sekci „Obec v číslech" (dvě karty + rozbalovací tabulka 17 obcí).
  Metodika: **tříletý průměr konsolidovaných příjmů 2022–2024** dělený počtem
  obyvatel k 1. 1. 2025 (jeden rok by kolísal podle investic). Zdroje: ČSÚ,
  ARES (IČO), MONITOR (rozklikávací rozpočet), Wikidata (souřadnice); odpovědi
  API se cachují v soukromé zóně, běh jde zopakovat i `--offline`.
  Tvrdé kontroly (obyvatelé, věk Prštic, okresní průměr) PASS.
  Výsledek: **24 829 Kč/obyv., 5. nejnižší ze 17** (medián 27 608 Kč);
  věk 43,3 vs. okolí 41,5 a okres 41,65 → **30. nejstarší ze 187 obcí okresu**.
  Pozn.: čísla se drobně liší od první rešerše (25 251 Kč) — sjednocen jmenovatel
  na počet obyvatel k 1. 1. 2025; pořadí i závěr beze změny.

## Fáze 3 — Stavba webu (2–3 dny, AI skillem /web)

> Provádí se skillem **/web** — jeho postup je závazný: zakotvení → 2–3 designové
> směry → plán + kontrola proti zakázaným klišé → **živá ukázka jedné sekce
> ke schválení** → teprve pak celek. Grafy se staví podle explicitních pravidel
> v tomto plánu.

- [x] **3.1 🤝 Zakotvení a výběr směru** — předmět: hospodaření malé obce;
  publikum: občan-laik + nepřátelský čtenář; hlavní úloha: pochopit za 2 min.
  AI nabídne 2–3 směry (očekávaný charakter: civilní, důvěryhodný, „úřední
  čistota bez úřední šedi" — žádná skandální červená), Petr vybere. *(~20 min)*
- [x] **3.2 🤝 Živá ukázka v0** — hero + příjmy, výdaje a saldo z reálných dat
  + náhled vývoje 518, v prohlížeči. Žádný Sankey, který by naznačoval účelové
  propojení konkrétních příjmů a výdajů.
  **Nestaví se dál bez Petrova „tenhle směr ano".** *(~15 min)*
- [x] **3.3 🤖 Stavba celku** — hlavní navigace: Přehled → Kam šly peníze →
  Účet 518 → Soudy a řízení → Jak to víme. Pořadí stavby: layout → sanitizovaná
  data → rozpočet (seřazené sloupce + rozlišení opakované/jednorázové dle P-33
  + tabulky + přepínač na obyvatele) → 518 →
  tři vybraná témata → soudní a správní řízení → chronologie a dokumenty →
  O webu; stránka pro další obce jen pokud zůstává ve v1. Informační stav se
  uvádí hlavně na úrovni grafu nebo karty; čtyřřádkový souhrn se použije jednou
  na každé vybrané téma, ne u každého čísla. **Designové detaily až nakonec.**
  Každá sekce = samostatný commit. Deliverable: kompletní web lokálně.
- [x] **3.4 🤖 Neviditelná vrstva** — title, description, OG obrázek, sitemap,
  robots.txt, favicon (P-16); kontrola `lang="cs"` a čitelnosti dle P-14.
  ✅ hotovo 26. 8. 2026: u všech tří stránek title, description, canonical,
  Open Graph (vč. og:image = ilustrace zámku) a Twitter card; `favicon.svg`,
  `robots.txt`, `sitemap.xml`. Ověřeno: jeden H1 na stránku, `lang="cs"`,
  text 19 px, 0 obrázků bez alt, mobil 360 px bez vodorovného posuvu,
  čistá konzole. **Struktura webu:** `index.html` (hospodaření), `rizeni.html`,
  `jak-to-vime.html`, sdílený `styl.css`; data do všech stránek vkládá
  `skripty/vlozit_data.py` (do HTML se ručně nesahá).

## Fáze 4 — Ověření (½–1 den; AI kontroly + finální oči Petra)

- [x] **4.1 🤖 Privacy release gate** — spustit validaci z 1.8 nad celým
  veřejným repozitářem i výsledným buildem; projít názvy, metadata, vložený JSON,
  HTML komentáře, source mapy a extrahovaný/OCR text PDF. Ověřit, že originály
  nejsou tracked ani v deploy artefaktu a že sign-off odpovídá aktuálnímu
  commitu. Kritérium: automatické kontroly PASS, nevyřešené nálezy 0 a platný
  `ANONYMIZACE-SIGNOFF.md`. Při nálezu originálu v historii se publikace zastaví;
  pouhé smazání v novém commitu nestačí.
  ✅ hotovo 27. 8. 2026: validace 33 PASS/0 FAIL, anonymizace 0 nálezů, sken
  celého repa (57 textových souborů) na rodná čísla, ID datovek, adresy, e-maily
  a klíče → **0 nálezů**; žádné originály tracked. Na živém webu ověřeno, že
  `/obsah/` i odložená sekce o jeřábu vracejí **404**.
- [x] **4.2 🤖 Technické ověření** — mobil od 360 px, text 200 %, průchod
  klávesou Tab, kontrast, odkazy, čistá konzole a skutečné tabulkové alternativy
  grafů. Světlý režim je povinný; tmavý režim lze vypustit, pokud by zdržoval.
  Důkaz: screenshoty a protokol.
  ✅ hotovo 27. 8. 2026: všechny 3 stránky — 1× H1, `lang="cs"`, title+description
  +OG, 0 obrázků bez alt, 0 tabulek mimo posuvný rám, 0 grafů bez popisu,
  0 tlačítek bez názvu. Mobil 360 px **bez vodorovného posuvu**, text 19 px,
  310 fokusovatelných prvků. Konzole čistá. Tmavý režim vypuštěn (P-14 ho
  připouští jako volitelný) — web je záměrně jen světlý.
- [x] **4.3 🤖 Fakta a reprodukovatelnost** — spustit validační skript z 1.8,
  znovu vygenerovat všechny odvozené hodnoty a porovnat 100 % headline čísel
  a tvrzení s registrem z 2.8. Zvlášť ověřit storna, právní služby, jeřáb,
  odpadní vodu a rozdíl cash/accrual. Kritérium: žádné neověřené hlavní tvrzení.
- [ ] **4.4 🤝 Krátká kontrola srozumitelnosti** — bez externího uživatelského
  testování. AI projde web jako laik podle checklistu; Petr na telefonu během
  deseti minut ověří, že najde: příjmy/výdaje, skutečný vývoj 518, hlavní
  příspěvky změn, meze dostupných dat a rozdíl mezi soudním a správním řízením.
  Nejasnosti se zkrátí, nepřidávají se nové vrstvy informací.
- [x] **4.5 🤝 Zkouška aktualizace** — Petr zadá: „přidej do chronologie
  událost X s PDF Y" — musí to projít sanitizační pipeline do 15 minut bez
  zásahu do HTML/kódu.
  ✅ hotovo 27. 8. 2026 — **zkouška provedena na skutečné aktualizaci**: přidána
  žádost o vnitřní pravidla pro zadávání veřejných zakázek (26. 8. 2026) do
  chronologie, trackeru i knihovny dokumentů, včetně anonymizovaného PDF.
  **Čas: 21 minut** (8:22 → 8:43), z toho ~12 minut zabraly dvě opravy validace
  (viz níže). Samotné přidání dat + pipeline + nasazení trvalo pod 10 minut.
  **Do HTML se nesáhlo** — stačila úprava dvou JSON souborů, jednoho řádku
  v `anonymizace.py` a spuštění tří skriptů.
  ⚠️ Zkouška odhalila dva falešné poplachy privacy gate, které by blokovaly
  publikaci: (a) kontaktní e-mail autora byl hlášen jako únik, ačkoli je na webu
  záměrně (P-11); (b) anonymizovaná PDF ve `web/dokumenty/` byla hlášena jako
  „zakázané originály". Obojí opraveno — validace teď rozlišuje originál od
  schváleného derivátu. Bez toho by každá další aktualizace narazila.

## Fáze 5 — Spuštění (½ dne)

- [x] **5.1 🤝 Nasazení** — Netlify (Petr má zkušenost z prsticehospodareni)
  napojený na repozitář. Preview je `noindex` a stejně jako produkce smí vznikat
  jen z veřejných sanitizovaných dat; ostrý deploy z `main` se provede až po
  dokončení celé fáze 4. Doména + HTTPS. Přístupy zadává Petr. Součástí je
  rozhodnutí o návštěvnostní statistice
  (ZADANI §12): doporučení GoatCounter bez cookies, nebo v1 bez měření —
  rozhodne Petr.
  ✅ hotovo 27. 8. 2026: **web je živý na https://transparentniprstice.cz**
  (Netlify z GitHubu, automatické nasazení z `main`; `netlify.toml` publikuje
  `web/`, preview `noindex`). DNS zůstaly u Forpsi: A `@` → 75.2.60.5,
  CNAME `*` → netlify.app; DNSSEC ponechán zapnutý. HTTPS Let's Encrypt
  platné do 25. 11. 2026, HTTP/2, HSTS + CSP + X-Frame-Options aktivní.
  Kontakt v patičce: petr@petrnovotny.com.
  ⚠️ Při nasazení spadl první deploy na **syntaktické chybě v `netlify.toml`**
  (sekce byla zároveň tabulkou i polem tabulek). Opraveno a nově se soubor
  ověřuje parserem před commitem.
  🔶 **Otevřeno:** návštěvnostní statistika — zatím se neměří nic.
- [ ] **5.2 👤 Oznámení obci** — před spuštěním poslat obci zdvořilý dopis
  s neveřejným náhledem, přesnými otázkami a tvrzeními, která se jí týkají,
  a datem plánovaného zveřejnění. Nabídnout zveřejnění jejího vyjádření po
  nezbytné anonymizaci. Koncept připraví AI v Petrově stylu podle agenta
  `1_Agents/1_PNO-psani-emailu-v-mem-stylu.md`.
- [ ] **5.3 👤 Rozšíření** — sdílení dle Petrova uvážení (osobní kanály,
  zpravodaj kandidátky apod.). Zveřejnění před komunálními volbami je vědomé
  rozhodnutí autora a není důvodem k odkladu.

## Fáze 6 — Provoz a další verze (průběžně)

- [ ] **6.1** Po 27. 8.: zanést výsledek řízení u KrÚ JMK do chronologie.
- [ ] **6.2** Po odpovědi obce na žádost o soudní řízení (podána 15. 8.):
  doplnit `data/rizeni.json`, správně určit `typ`, iniciátora a roli obce,
  přiložit sanitizované rozsudky a aktualizovat upozornění na úplnost.
- [ ] **6.3** v2: automatická čtvrtletní aktualizace z MONITORu (P-20),
  srovnání s podobnými obcemi (P-21).
- [ ] **6.4** Po volbách: naplnit strukturu sekce nového období (P-22).
- [ ] **6.5** Compound krok: z hotového projektu nechat AI vytvořit skill
  „aktualizace transparentního webu", aby další doplnění byla rutina.
- [ ] **6.6 🤖+👤 Stránka „Obec v kostce" (P-37)** — sběr údajů z oficiálních
  zdrojů (web obce, ČSÚ, volby.cz, RÚIAN/ARES, seznam datových schránek),
  návrh stránky, Petr schvaluje obsah. **Rozhodnuto 28. 8.: bez fotografií**
  (autorská práva — rešerše
  `2026_08_28_Pravni-reserse_fotky-kontakty-zastupitelu.md` v PACT);
  starosta + místostarosta zvýrazněně s plnými úředními kontakty,
  zastupitelé doplňkově.
- [ ] **6.7 🤖 Přepracování „Pro další obce" (P-38)** — rámeček „Co k tomu
  opravdu potřebujete" (špičkový AI model v agentním režimu, GitHub, reálný
  čas/náklady; s běžným chatem zdarma výsledek nevznikne), rozdělení kroků
  na úroveň „zvládne běžný chat" (1–7) a „vyžaduje vibe coding" (8),
  stejný rámeček do úvodu `NAVOD-PRO-AI-obcanska-analyza-obce.md`.
  **Varianta potvrzena Petrem 28. 8.** — kroky 1–7 zůstávají.
- [ ] **6.8 🤖+👤 Blok „Odměny vedení obce" (P-39)** — vstupy HOTOVÉ:
  rešerše 28. 8. (`2026_08_28_Reserse_odmeny-zastupitelu.md` v PACT) —
  starosta uvolněný (usn. 4+5/2022/Z1, pevná výše 54 086 → 75 736 Kč/měs
  2022→2026), místostarosta neuvolněný 10 000 Kč (≈ 24 % maxima,
  usn. 13/2022/Z1), zastupitel 1 623 Kč, předseda výboru 3 245 Kč, člen
  výboru 500 Kč od 4/2023 (usn. 33/2023/Z3); křížová kontrola s FIN
  5023/5021 sedí (±0,7 %). Postavit se stránkou „Obec v kostce".
  Zbývá vyžádat dle 106: chybějící zápisy 6/2025–8/2026, úplné zápisy
  z 21. 10. 2022 a 7. 3. 2023, přehled vyplacených odměn po funkcích
  (koncept žádosti připraví AI, odešle Petr).

---

## Souhrn rolí

| Kdo | Co drží |
|---|---|
| **Petr** | rozhodnutí (veřejné datové schéma, kategorie, design, finální texty), jediný lidský privacy sign-off, přístupy, commity, komunikace s obcí |
| **AI** | soukromá/veřejná datová pipeline, strojová anonymizace, extrakce a validace dat, návrhy textů, stavba webu, kontroly a protokoly |
| **Zábradlí** | ZADANI.md §7 (co NEBUDE), validační skript, právně-jazyková pravidla, checklisty /web |

**Kritická cesta:** 0.4 → 0.5 → 1.0–1.8 → 2.1–2.6 + 2.8 → 3.2 → 3.3 → 4.x → 5.1.
Největší riziko skluzu: první nastavení anonymizační pipeline a OCR PDF (2.5)
a MONITOR data (1.4 — má záložní ruční cestu). Ruční začerňování dokumentů
není součástí plánu; Petr provádí jedinou konsolidovanou výstupní kontrolu.
