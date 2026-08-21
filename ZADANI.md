# ZADÁNÍ: Web Transparentní Prštice

**Verze:** 1.0 (21. 8. 2026)
**Autor zadání:** Petr Novotný + AI (na základě rozhovoru a průzkumu workspace)
**Schváleno:** čeká na schválení Petrem

---

## 1. O co jde

Veřejný web **transparentniprstice.cz**, který srozumitelně a doložitelně informuje
občany obce Prštice o hospodaření obce v minulém a předminulém volebním období
a je připravený na průběžné doplňování informací v obdobích následujících.

Jádrem je: (a) vizuální přehled celého obecního rozpočtu „kudy tečou peníze",
(b) speciální sekce o účtu 518 Ostatní služby — jednom z mála nákladových účtů,
který vedení obce přímo ovlivňuje — a rozbor jeho nárůstu, (c) transparentní
chronologie občanského auditu včetně všech dokumentů (žádosti dle zákona
106/1999 Sb., odpovědi obce, stížnost, řízení u KrÚ JMK).

Provozovatel: **Petr Novotný, občan Prštic** — osobní občanský projekt,
podepsaný, s kontaktem. Neutrální datový tón: fakta a čísla se zdrojem,
komentář vždy graficky oddělený a označený jako názor autora.

## 2. Problém a pro koho

**Problém:** Občan Prštic dnes nemá šanci pochopit, jak obec hospodaří. Oficiální
zdroje (MONITOR, úřední deska, závěrečné účty v PDF) jsou pro laika nečitelné.
Účet 518 mezitím narostl z ~2,3 mil. Kč (2021) na 5,8 mil. Kč (2023) a 4,7 mil. Kč
(2025) a obec odmítá vydat podrobnosti — spor běží u Krajského úřadu JMK.

**Primární publikum:** běžný občan Prštic (~1 000 obyvatel), bez znalosti účetnictví.
**Sekundární publika:** zastupitelé, novináři, úředníci KrÚ, kritický oponent
(web musí obstát i při nepřátelském čtení — každé číslo doložené).

**Hlavní úloha stránky:** občan za 2 minuty pochopí, s čím obec hospodaří,
co z toho vedení přímo ovlivňuje a proč se autor ptá na konkrétní výdaje.

## 3. Proč teď

- Komunální volby jsou na podzim 2026 — web musí být venku s předstihem,
  aby se stihl vstřebat a nebyl čten jen jako kampaň na poslední chvíli.
- 27. 8. 2026 uplyne lhůta KrÚ JMK k opatření proti nečinnosti — kauza bude mít
  nový vývoj, web je místo, kde ho průběžně dokumentovat.
- Data i analýzy už existují (viz sekce 8) — chybí jen srozumitelná veřejná vrstva.

## 4. Co už existuje (nezačínáme od nuly)

- **1 335 transakcí účtu 518 za 2022–2025** s kategoriemi (JSON v
  `0_Projects/4_PRŠTICE/2026_06_22 Analýza účtu 518/Detail_uctu_518_Prstice.html`,
  řádek 160) — sedí přesně na výkaz zisku a ztráty.
- **Rozvaha + výkaz zisku a ztráty 2015–2025** (JSON v
  `2026_04_30 Audit hospodaření obce/audit-prstice-rozvaha-vzz-dashboard.html`),
  nasazená pracovní verze: prsticehospodareni.netlify.app.
- **Hotové rozbory:** slabá místa hospodaření (A1–A10), rozbor GDPR pověřence
  s cenovým srovnáním trhu, analýza jeřábu, kontrola lhůt s čísly jednacími.
- **Chronologie kauzy** s daty, sp. zn. SP/088/2026, č. j. OUPR-867-2026 atd.
- **PDF dokumenty** (žádosti, odpovědi, dodejky) — jen na Petrově Macu, ne v gitu.
- **Oficiální otevřená data MONITOR** (IČO 00282405): výkaz FIN 2-12 M
  (rozpočet dle paragrafů a položek), výkaz zisku a ztráty (účet 518) — CSV extrakty
  i webová služba pro budoucí automatickou aktualizaci.

## 5. Jak to funguje — struktura webu (v1)

Princip **postupného odkrývání**: přehled → kategorie → položka → původní dokument.
Nikdo není nucen do účetnictví, ale cesta dolů je vždy nabídnutá.

1. **Úvod** — jedna věta lidsky („Obec Prštice loni hospodařila s X mil. Kč…"),
   tok peněz příjmy → výdaje (Sankey nebo ekvivalent), přepínač Kč / Kč na obyvatele.
2. **Rozpočet v kostce** — výdaje jako klikací dlaždice (treemap) s českými názvy
   agend: odpady, škola a školka, údržba, chod úřadu…; mandatorní vs. ovlivnitelné
   výdaje; časová řada přes obě volební období; vždy i tabulková alternativa.
3. **Účet 518** — co to je (vysvětlení pro laika), vývoj 2015–2025, proč je to
   účet, který vedení obce přímo ovlivňuje, rozklad nárůstu podle kategorií.
4. **Ptáme se** — tři kauzy: právní služby (2,04 mil. Kč / 4 roky), GDPR pověřenec
   (27 225 Kč/měs.), stavební jeřáb (846 tis. Kč / ~23 měsíců). Každá kauza má
   pevnou strukturu: **Fakta** (jen doložené, se zdrojem) → **Kontext a srovnání** →
   **Naše otázky obci** → **Odpověď obce** (v plném znění, jakmile existuje).
5. **Jak jsme postupovali** — chronologická osa auditu od nalezení výkazů ve
   veřejných zdrojích po řízení u KrÚ, s odkazy na anonymizovaná PDF.
6. **Dokumenty** — knihovna všech podkladů ke stažení.
7. **O webu** — kdo, proč, zdroje dat, metodika, kontakt, prostor pro vyjádření obce.

## 6. Požadavky

### Nutné pro první verzi

**Obsah a data**
- **P-1:** Každé číslo na webu má uvedený zdroj a datum („zdroj: výkaz zisku a ztráty,
  MONITOR MF ČR, k 31. 12. 2025") a tam, kde existuje, proklik na dokument.
- **P-2:** Údaje se zobrazují v Kč i v přepočtu na obyvatele (přepínač); počet
  obyvatel dle ČSÚ je uveden u každého roku.
- **P-3:** Rozpočtová data v1 pokrývají minimálně roky 2019–2025 (dvě volební
  období), účet 518 v řadě 2015–2025 a v transakčním detailu 2022–2025.
- **P-4:** U dat je rozlišeno ✅ doloženo dokumentem / ⚠️ odvozeno či dopočteno
  (např. kategorie transakcí 518 jsou dopočtené autorem — musí to být uvedeno).
- **P-5:** Fakta a komentář jsou vizuálně i textově oddělené; komentářové bloky
  jsou označené (např. „Komentář Petra Novotného") a nepoužívají hodnotící
  nálepky typu „podezřelé", „tunel" — pouze otázky a srovnání.
- **P-6:** Kauza GDPR obsahuje cenové srovnání trhu (SMO 250 Kč/měs … Brno
  6 000 Kč/měs vs. Prštice 22 500 Kč/měs bez DPH) s odkazy na zdroje.
- **P-7:** Chronologie auditu obsahuje všechny kroky s daty a čísly jednacími
  a u každého kroku odkaz na anonymizované PDF (kde existuje).
- **P-8:** Všechna zveřejněná PDF jsou anonymizovaná (jména a adresy soukromých
  fyzických osob, čísla účtů FO, podpisy); jména veřejných funkcionářů
  a podnikatelů-dodavatelů obce zůstávají.
- **P-9:** Web obsahuje mini-slovníček přímo u grafů (co je účet 518, paragraf,
  položka, RUD, mandatorní výdaj) — bublina/rozbalení, ne zvláštní stránka.
- **P-10:** Web obsahuje sekci „Kam se dívat dál" s odkazy na oficiální zdroje
  (profil obce v MONITORu, registr smluv, úřední deska, Hlídač státu).
- **P-11:** Stránka „O webu" uvádí provozovatele jménem, kontakt a nabídku
  obci na zveřejnění vyjádření v plném znění.

**Technika a forma**
- **P-12:** Statický web bez přihlašování a databáze; data oddělená od prezentace
  (JSON/CSV soubory v repozitáři, grafy se z nich generují).
- **P-13:** U každého grafu tlačítko „stáhnout data (CSV)" a tabulková alternativa.
- **P-14:** Web splňuje pravidla čitelnosti skillu /web: text ≥ 16 px, řádek
  max 65ch, kontrast WCAG AA, jeden H1, funguje od šířky 360 px, světlý
  i tmavý režim, `lang="cs"`.
- **P-15:** Barva není nikdy jediným nositelem významu; grafy mají popisky os
  a tooltips; žádná kauzální tvrzení tam, kde je jen souvislost.
- **P-16:** SEO/sdílení: title, description, Open Graph obrázek, sitemap,
  robots.txt; web je indexovatelný.
- **P-17:** Vlastní GitHub repozitář novotny25/transparentniprstice.cz
  (mimo PACT), nasazení automatické z gitu (Netlify nebo GitHub Pages),
  doména transparentniprstice.cz (zaregistrována 21. 8. 2026).
- **P-18:** Přidání nové události do chronologie nebo nového dokumentu = úprava
  jednoho datového souboru + přidání PDF, bez zásahu do HTML/kódu.
- **P-19:** Před spuštěním projde web kontrolním seznamem: každé číslo ověřeno
  proti zdroji, právní jazyková kontrola (fakta vs. hodnotící soudy),
  test na mobilu, test čitelnosti, funkční odkazy.

### Až potom (v2+)
- **P-20:** Automatická čtvrtletní aktualizace rozpočtových dat z MONITORu
  (webová služba pro IČO 00282405 nebo CSV extrakty).
- **P-21:** Srovnání s 3–5 podobně velkými obcemi okresu Brno-venkov.
- **P-22:** Sekce pro nové volební období (sliby vs. skutečnost, noví zastupitelé)
  — v1 jen připravená struktura dat, bez obsahu.
- **P-23:** Napojení na registr smluv / Hlídač státu API (výpis posledních smluv).
- **P-24:** Převod „co by se za to dalo pořídit" (oprava X m chodníku apod.).

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

Když bude chuť něco přidat: buď to jde do „až potom", nebo se za to musí
něco z v1 vyškrtnout.

## 8. Data a soubory

| Zdroj | Co | Kde |
|---|---|---|
| Deník účtu 518 2022–2025 | 1 335 transakcí (datum, doklad, částka, popis, kategorie) | `4_PRŠTICE/2026_06_22 Analýza účtu 518/Detail_uctu_518_Prstice.html` ř. 160 (JSON) |
| Rozvaha + VZZ 2015–2025 | 2 609 položek vč. řady účtu 518 | `4_PRŠTICE/2026_04_30 Audit hospodaření obce/audit-prstice-rozvaha-vzz-dashboard.html` (`<script id="audit-data">`) |
| Rozpočet dle paragrafů/položek | FIN 2-12 M — **nutno stáhnout** z otevřených dat MONITOR (IČO 00282405) | monitor.statnipokladna.gov.cz/datovy-katalog/open-data |
| Chronologie a č. j. | kompletní časová osa | `4_PRŠTICE/2026_08_15 Opakovaná žádost.../2026_08_15_Kontrola_lhut_a_procesniho_postupu.md` |
| Rozbory kauz | GDPR, jeřáb, právní služby, slabá místa A1–A10 | složky `2026_08_15*`, `2026_04_30*` |
| PDF dokumenty kauzy | žádosti, sdělení OUPR-867-2026, stížnost, podání na KrÚ, dodejky | **jen na Petrově Macu** — do web repa až po anonymizaci |
| Deník 518 za 1–6/2026 | poskytnut 3. 8. 2026 (OUPR-1007/2026) | na Macu, do datasetu zatím nezanesen |

**Známé mezery v datech** (na webu se přiznávají, nezakrývají): chybí dodavatelé
transakcí (obec je odmítla vydat — to je jádro sporu), chybí smlouvy ke třem
kauzám, kategorie transakcí jsou dopočtené autorem.

## 9. Hranice a rizika

- **Právní:** skutková tvrzení jen doložená; hodnotící soudy jen z pravdivého
  základu, bez znevažujících excesů; u soukromých dodavatelů opatrněji než
  u veřejných funkcionářů; obci vždy prostor k vyjádření. Judikatura NSS chrání
  roli „společenského hlídacího psa" — ale jen při férové práci s fakty.
- **GDPR:** anonymizace PDF před zveřejněním je tvrdá podmínka (P-8);
  anonymizaci dělá Petr na Macu, AI připraví checklist co začernit.
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
- Nezaujatý testovací čtenář (ne Petr) do 2 minut správně odpoví: „S kolika
  penězi obec ročně hospodaří? Co je účet 518 a proč roste?"
- 100 % čísel na webu má zdroj; namátková kontrola 20 čísel = 20 sedí.
- Přidání nové události do chronologie trvá do 15 minut a zvládne to AI
  na jeden pokyn (test před spuštěním).

## 12. Otevřené otázky

- ~~Přesný název domény~~ → **VYŘEŠENO 21. 8. 2026:** zaregistrována
  transparentniprstice.cz, repozitář novotny25/transparentniprstice.cz.
- **[OTEVŘENÉ]** Zanese se deník 518 za 1–6/2026 už do v1, nebo až v aktualizaci
  po rozhodnutí kraje? (doporučení: do v1, ať je řada úplná)
- **[OTEVŘENÉ]** Bude na webu jednoduchá návštěvnostní statistika (např.
  GoatCounter/Plausible bez cookies), nebo v1 zcela bez měření?
- **[PŘEDPOKLAD]** Komunální volby proběhnou na podzim 2026; přesné datum
  doplnit do plánu, jakmile bude vyhlášeno.
