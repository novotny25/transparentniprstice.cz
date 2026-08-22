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
- [ ] **1.4 🤖 Rozpočtová data z MONITORu** — stáhnout FIN 2-12 M pro IČO
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
  🔶 ROZPRACOVÁNO 22. 8. 2026 (PŘEDBĚŽNÉ): MONITOR byl v údržbě, lokální
  `monitor_*.html` byly prázdné skořápky. Skript `skripty/extrakce_rozpocet.py`
  vytáhl skutečnost z lokálních výkazů FIN 2-12 M (PDF) pro **2022 a 2023** →
  `data/rozpocet.json` (basis: cash_budget, stav incomplete). Výdaje po 41
  paragrafech, součet = rekapitulace „Výdaje celkem" na 0,00 Kč. 6330 „Převody
  vlastním fondům" označeny jako vnitřní převod. **Zbývá:** doplnit 2019–2021,
  2024, 2025 z MONITORu (až bude dostupný) a pak s Petrem metodiku P-33
  (opakované vs. jednorázové) do `data/rozpocet-metodika.md`. Úkol proto zůstává
  otevřený.
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
  `data/rizeni.json` — DRAFT: tři správní řízení ÚOHS (S0589/2023, S1089/2024,
  S0071/2025) s povinným `typ: spravni` a rolí obce; předmět/výsledek/právní moc
  je nutné OVĚŘIT z rozhodnutí ÚOHS (rešerše zatím jen naznačila případ
  neuveřejnění smlouvy o úvěru s KB, pokuta 4 000 Kč). **Soudní část čeká na
  odpověď obce** (žádost 15. 8. 2026). `validace.py` hlídá povinné `typ`
  a že ÚOHS není soud. Úkol zůstává otevřený (ÚOHS ověřit + Petrovo schválení).
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

- [ ] **2.1 🤖 Texty přehledu a slovníček** — AI napíše úvod, „rozpočet
  v kostce", vysvětlení účtu 518 pro laika a mini-slovníček. Jazyk: běžná
  čeština, krátké věty, žádný účetní žargon bez vysvětlení. Povinné jednoduché
  vysvětlení rozdílu:
  > Rozpočet ukazuje, kdy obec peníze přijala nebo vydala. Účet 518 ukazuje,
  > kdy byl zaúčtován náklad na službu; platba může proběhnout v jiném období.
  > Proto se oba součty nemusí rovnat a na webu je nesčítáme.
  Deliverable: `web/obsah/*.md` k Petrově revizi.
- [ ] **2.2 🤝 Příběh účtu 518 a úplný rozklad změn** — z úkolu 1.7 připravit
  jednu čáru 2015–2025, nenápadný tříletý klouzavý průměr a jednoduchý graf
  „Co vytvořilo meziroční rozdíl". Roční hodnoty zůstávají viditelné; klouzavý
  průměr je pouze pomůcka, nesmí je nahrazovat. Text výslovně řekne, že vývoj
  není nepřetržitý: vrchol 2023, pokles 2024, opětovný růst 2025. Pro 2023
  zobrazit všechny hlavní příspěvky, nejen tři Petrem vybraná témata; pro 2025
  totéž po přiřazení storen. Vedle grafu krátce uvést „Co z deníku nevíme".
  Graf nese krátkou poznámku „běžné ceny, bez odečtení inflace". Deliverable:
  schválený datový příběh bez tvrzení o nedoložené příčině.
- [ ] **2.3 🤝 Tři vybraná témata v kompaktní struktuře** — právní služby,
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
- [ ] **2.4 🤖 Chronologie občanské datové analýzy jako data** —
  `data/chronologie.json`: datum, titulek, věcný popis, č. j., původ informace
  a odkaz na veřejný sanitizovaný dokument. Vychází z kontrolního dokumentu
  lhůt a všech složek od prvního sběru zdrojů 30. 4. 2026 po aktuální stav.
  Deliverable: úplná, průběžně doplnitelná osa; název zdrojové složky může
  obsahovat „Audit", veřejný text používá „analýza".
- [ ] **2.5 🤖 Strojová anonymizace JSON/CSV/HTML/PDF** — Petr ukáže soukromou
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
- [ ] **2.6 🤝 Sekce Soudní a správní řízení — obsah** — jedna stránka, dvě
  samostatné části a žádný společný počet, který by vydával ÚOHS za soud.
  Soudní karty zdůrazní řízení iniciovaná obcí, ale datově zachovají procesní
  roli u všech případů z odpovědi obce. Správní karty popíší kontrolu, zjištění,
  sankci, právní moc a primární zdroj. U běžících řízení žádná predikce.
  Nahoře samostatný graf právních nákladů 518; propojení na konkrétní řízení
  pouze s přímým dokladem. Viditelný stav žádosti z 15. 8. 2026 a upozornění na
  možnou neúplnost do obdržení odpovědi. Petr schvaluje finální znění.
- [ ] **2.7 🤝 Stránka „Pro další obce a občany" + návod „Udělejte si sami"**
  — použít revidovaný `NAVOD-UDELEJTE-SI-SAMI.md`; osobní údaje se nedávají do
  cloudového AI promptu a veřejný výstup se nenazývá audit. Pokud tento úkol
  ohrozí termín, přesune se celý do v2; pro v1 je povinná pouze stránka „Jak
  jsme postupovali". Licence se vztahuje na vlastní kód a text, ne automaticky
  na převzaté dokumenty a zdrojová data.
- [ ] **2.8 🤖 AI kontrola faktů a jazyka + Petrovo schválení** — AI vytvoří
  jednoduchý registr všech publikovaných skutkových tvrzení: tvrzení, typ (zdroj/výpočet/
  autorské zařazení/nezjištěno), zdroj, výpočet a stav kontroly. AI ověří každý
  řádek; tvrdý release gate platí zejména pro 100 % headline čísel, negativních
  tvrzení a výroků o konkrétních osobách. Opraví formulace bez podkladu a
  sugestivní otázky. Výstup: protokol NÁLEZ → OPRAVA.
  Finální text čte a schvaluje Petr; žádná další lidská kontrola není v plánu.

## Fáze 3 — Stavba webu (2–3 dny, AI skillem /web)

> Provádí se skillem **/web** — jeho postup je závazný: zakotvení → 2–3 designové
> směry → plán + kontrola proti zakázaným klišé → **živá ukázka jedné sekce
> ke schválení** → teprve pak celek. Grafy se staví podle explicitních pravidel
> v tomto plánu.

- [ ] **3.1 🤝 Zakotvení a výběr směru** — předmět: hospodaření malé obce;
  publikum: občan-laik + nepřátelský čtenář; hlavní úloha: pochopit za 2 min.
  AI nabídne 2–3 směry (očekávaný charakter: civilní, důvěryhodný, „úřední
  čistota bez úřední šedi" — žádná skandální červená), Petr vybere. *(~20 min)*
- [ ] **3.2 🤝 Živá ukázka v0** — hero + příjmy, výdaje a saldo z reálných dat
  + náhled vývoje 518, v prohlížeči. Žádný Sankey, který by naznačoval účelové
  propojení konkrétních příjmů a výdajů.
  **Nestaví se dál bez Petrova „tenhle směr ano".** *(~15 min)*
- [ ] **3.3 🤖 Stavba celku** — hlavní navigace: Přehled → Kam šly peníze →
  Účet 518 → Soudy a řízení → Jak to víme. Pořadí stavby: layout → sanitizovaná
  data → rozpočet (seřazené sloupce + rozlišení opakované/jednorázové dle P-33
  + tabulky + přepínač na obyvatele) → 518 →
  tři vybraná témata → soudní a správní řízení → chronologie a dokumenty →
  O webu; stránka pro další obce jen pokud zůstává ve v1. Informační stav se
  uvádí hlavně na úrovni grafu nebo karty; čtyřřádkový souhrn se použije jednou
  na každé vybrané téma, ne u každého čísla. **Designové detaily až nakonec.**
  Každá sekce = samostatný commit. Deliverable: kompletní web lokálně.
- [ ] **3.4 🤖 Neviditelná vrstva** — title, description, OG obrázek, sitemap,
  robots.txt, favicon (P-16); kontrola `lang="cs"` a čitelnosti dle P-14.

## Fáze 4 — Ověření (½–1 den; AI kontroly + finální oči Petra)

- [ ] **4.1 🤖 Privacy release gate** — spustit validaci z 1.8 nad celým
  veřejným repozitářem i výsledným buildem; projít názvy, metadata, vložený JSON,
  HTML komentáře, source mapy a extrahovaný/OCR text PDF. Ověřit, že originály
  nejsou tracked ani v deploy artefaktu a že sign-off odpovídá aktuálnímu
  commitu. Kritérium: automatické kontroly PASS, nevyřešené nálezy 0 a platný
  `ANONYMIZACE-SIGNOFF.md`. Při nálezu originálu v historii se publikace zastaví;
  pouhé smazání v novém commitu nestačí.
- [ ] **4.2 🤖 Technické ověření** — mobil od 360 px, text 200 %, průchod
  klávesou Tab, kontrast, odkazy, čistá konzole a skutečné tabulkové alternativy
  grafů. Světlý režim je povinný; tmavý režim lze vypustit, pokud by zdržoval.
  Důkaz: screenshoty a protokol.
- [ ] **4.3 🤖 Fakta a reprodukovatelnost** — spustit validační skript z 1.8,
  znovu vygenerovat všechny odvozené hodnoty a porovnat 100 % headline čísel
  a tvrzení s registrem z 2.8. Zvlášť ověřit storna, právní služby, jeřáb,
  odpadní vodu a rozdíl cash/accrual. Kritérium: žádné neověřené hlavní tvrzení.
- [ ] **4.4 🤝 Krátká kontrola srozumitelnosti** — bez externího uživatelského
  testování. AI projde web jako laik podle checklistu; Petr na telefonu během
  deseti minut ověří, že najde: příjmy/výdaje, skutečný vývoj 518, hlavní
  příspěvky změn, meze dostupných dat a rozdíl mezi soudním a správním řízením.
  Nejasnosti se zkrátí, nepřidávají se nové vrstvy informací.
- [ ] **4.5 🤝 Zkouška aktualizace** — Petr zadá: „přidej do chronologie
  událost X s PDF Y" — musí to projít sanitizační pipeline do 15 minut bez
  zásahu do HTML/kódu.

## Fáze 5 — Spuštění (½ dne)

- [ ] **5.1 🤝 Nasazení** — Netlify (Petr má zkušenost z prsticehospodareni)
  napojený na repozitář. Preview je `noindex` a stejně jako produkce smí vznikat
  jen z veřejných sanitizovaných dat; ostrý deploy z `main` se provede až po
  dokončení celé fáze 4. Doména + HTTPS. Přístupy zadává Petr. Součástí je
  rozhodnutí o návštěvnostní statistice
  (ZADANI §12): doporučení GoatCounter bez cookies, nebo v1 bez měření —
  rozhodne Petr.
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
