# Udělejte si sami: občanská datová analýza hospodaření vaší obce s pomocí AI

**Koncept obsahu pro stránku webu (P-30/P-32).** Verze 0.2, 21. 8. 2026.
Podklad vychází z reálného postupu občanské datové analýzy obce Prštice
(2026). Před zveřejněním projde revizí Petra a kontrolou podle úkolu 2.8.

---

## Jak návod číst

Osm kroků v pořadí, v jakém proběhly v Pršticích. U každého kroku je:
**co uděláte vy**, **co za vás udělá AI** a **hotový prompt** ke zkopírování.
Doporučené nástroje: kterýkoli z velkých AI asistentů v placené verzi
(Claude, ChatGPT, Gemini) — pro kroky s analýzou dat a delšími dokumenty
volte vždy nejsilnější „přemýšlivý" model, který máte k dispozici; na
stavbu webu (krok 8) nástroj typu Claude Code.

Tři zásady platné pro všechny kroky:

1. **AI výstupy se ověřují.** Čísla kontrolujte kontrolními součty proti
   oficiálnímu výkazu, právní tvrzení proti zákonu. AI si umí vymýšlet.
2. **Rozlišujte typ informace.** Uveďte, zda je údaj převzatý ze zdroje,
   vypočítaný, zařazený autorem, nebo nezjištěný. Komentář držte odděleně
   a podepište ho. Jedna krátká legenda stačí pro celý web.
3. **Minimalizujte a anonymizujte.** Neanonymizované deníky, faktury ani
   žádosti nenahrávejte do cloudové AI. Před zveřejněním odstraňte osobní
   údaje ze všech JSON, CSV, HTML i PDF. Jméno fyzické osoby neponechávejte
   automaticky jen proto, že jde o funkcionáře nebo OSVČ; jeho zveřejnění
   musí být relevantní a výslovně schválené.

---

## Krok 1 — Najděte oficiální čísla své obce (30 minut)

**Vy:** zjistěte IČO své obce (je na webu obce v povinných informacích)
a otevřete její profil v MONITORu státní pokladny:
`monitor.statnipokladna.gov.cz/ucetni-jednotka/<IČO>`. Stáhněte výkaz
zisku a ztráty a rozvahu za posledních 8–10 let (jdou exportovat po letech).

**AI:** vysvětlí vám, na co se díváte.

> **Prompt 1:** Jsem občan obce [název], nejsem účetní. Přikládám výkaz
> zisku a ztráty a rozvahu obce z MONITORu státní pokladny. Vysvětli mi
> běžným jazykem: 1) co lze z těchto výkazů bezpečně vyčíst, 2) které
> nákladové a výnosové účty jsou největší, 3) které účty se v čase nejvíce
> změnily. Vysvětli rozdíl mezi rozpočtovým peněžním výdajem a účetním
> nákladem. Z čísla účtu neurčuj, co je povinné ze zákona, kdo o výdaji
> rozhodl ani kdo jej přímo ovlivňuje. Když něco nevyčteš, řekni to.

## Krok 2 — Nechte AI najít, co vybočuje (1 hodina)

**Vy:** nahrajte AI výkazy za všechny stažené roky najednou.

**AI:** sestaví časové řady a označí neobvyklé změny, které stojí za ověření.

> **Prompt 2:** Z přiložených výkazů obce [název] za roky [2015–2025]
> sestav tabulku vývoje všech nákladových a výnosových účtů po letech.
> Označ účty, které: a) vzrostly meziročně o více než 50 %, b) rostou
> setrvale rychleji než inflace, c) se chovají skokově. Ke každému
> označenému účtu napiš, co se na něm obvykle účtuje a jaké neškodné
> vysvětlení růstu připadá v úvahu — ať vím, na co se ptát, ne co tvrdit.
> Výslednou tabulku mi dej i jako CSV.

*(V Pršticích takto „vyskočil" účet 518 Ostatní služby: z ~2,3 mil. Kč
v roce 2021 na 5,8 mil. Kč v roce 2023.)*

## Krok 3 — Požádejte o detail podle zákona 106 (30 minut)

**Vy:** žádost pošlete datovou schránkou nebo na elektronickou podatelnu obce
a doplňte zákonem požadovanou identifikaci žadatele. Obec má na vyřízení
15 dnů (ze závažných důvodů může lhůtu
prodloužit až o 10 dnů — musí vám to ale oznámit).

**AI:** pomůže žádost přesně a jednoznačně vymezit.

> **Prompt 3:** Napiš žádost o informace podle zákona č. 106/1999 Sb.
> adresovanou obci [název]. Žádám opis položek účetního deníku k účtu
> [518] za roky [2022–2025] v rozsahu: datum, číslo dokladu, dodavatel,
> popis plnění, částka — ideálně ve strojově čitelném formátu (CSV/XLSX).
> Formuluj přesně a jednoznačně, ať je zřejmé, jaké informace žádám. Osobní
> údaje ponech jako zástupné značky [JMÉNO], [DATUM NAROZENÍ] a [ADRESA];
> doplním je až lokálně po ukončení práce s AI. Střízlivý úřední tón,
> žádné výčitky.

## Krok 4 — Analyzujte, co vám obec poslala (2 hodiny)

**Vy:** zkontrolujte, jestli jste dostali všechno, oč jste žádali
(v Pršticích obec poslala deník bez dodavatelů — i to je zjištění).

**AI:** roztřídí stovky řádků a najde vzory.

> **Prompt 4:** Přikládám anonymizovaný opis účetního deníku účtu [518] obce [název]
> za roky [2022–2025]. Udělej: 1) kontrolní součet po letech a porovnej
> s výkazem zisku a ztráty (přikládám) — pokud nesedí, vytvoř přehled rozdílů
> a nepokračuj v interpretaci, dokud rozdíl nevysvětlíme;
> 2) roztřiď položky do kategorií podle popisu (odpady, právní služby,
> IT, …) a označ kategorie jako svůj odhad; 3) najdi: opakované stejné
> částky (paušály), dlouho se opakující pronájmy, položky nad [50 000] Kč,
> storna; 4) ke každému nálezu napiš neutrální otázku, kterou bych měl
> obci položit. U každého výsledku označ: převzato ze zdroje / vypočítáno /
> zařazeno autorem / nezjištěno. Fakta odděl od domněnek a komentáře.

## Krok 5 — Vyžádejte si doklady k zajímavým položkám (30 minut)

**Vy:** vyberte 3–5 položek, u kterých chcete vidět smlouvu, objednávku
či výkaz práce. Méně je více — úzká žádost se hůř odmítá.

> **Prompt 5:** Napiš navazující žádost dle zákona 106/1999 Sb. obci
> [název]. K těmto účetním zápisům [vyjmenuj: datum, částka,
> popis] žádám: kopii smlouvy nebo objednávky, fakturu a doklad o rozsahu
> plnění (výkaz práce/předávací protokol). U paušálních plateb žádám
> rámcovou smlouvu a vymezení rozsahu služeb. Každý bod formuluj
> samostatně, aby byla žádost přehledná a každý bod samostatně přezkoumatelný.

## Krok 6 — Když obec mlčí nebo krouží: lhůty a stížnost (1 hodina)

**Vy:** hlídejte kalendář; každé podání i odpověď si ukládejte (dodejky!).

**AI:** pohlídá procesní postup — ale pozor, tady si nechte klíčové kroky
potvrdit i z druhého zdroje (poradna Otevřená společnost, Frank Bold).

> **Prompt 6:** Chronologie mé žádosti dle zákona 106/1999 Sb.: [data
> podání, co přišlo/nepřišlo]. Řekni mi: 1) jaké lhůty běží mně a jaké
> obci a kdy přesně končí, 2) jaký je správný další krok (stížnost dle
> § 16a? odvolání? podnět kraji na nečinnost?), 3) čeho se vyvarovat
> (např. předčasná žaloba). Připrav koncept příslušného podání. U každého
> tvrzení uveď konkrétní ustanovení zákona, ať si to můžu ověřit.

## Krok 7 — Dejte číslům kontext (2 hodiny)

Číslo bez kontextu nic neříká. Srovnávejte: s minulými roky, s podobně
velkými obcemi (MONITOR má data všech obcí), s ceníky na trhu.

**Vy:** vyberete, co srovnávat. **AI:** najde srovnatelné ceny se zdroji.

> **Prompt 7:** Obec [název] ([počet] obyvatel) podle [smlouvy / účetního
> deníku] vykazuje [částka a přesně popsané období] za [služby pověřence GDPR].
> Nejdřív ověř, co zdroj skutečně dokládá; z opakovaných účetních zápisů
> automaticky neodvozuj měsíční smluvní cenu. Zjisti z veřejných zdrojů, kolik za
> srovnatelnou službu platí obce podobné velikosti a co nabízejí svazy
> obcí; u každého údaje uveď zdroj s odkazem a porovnej známý rozsah služby,
> počet zapojených organizací, období a DPH. Kde rozsah neznáme, označ cenu
> jen jako orientační indicii. Pak přepočítej výdaj obce
> na obyvatele a na rok. Piš neutrálně — výstupem má být srovnání,
> ne obvinění.

## Krok 8 — Zveřejněte to srozumitelně (víkend práce)

**Vy:** rozhodujete, co a jak se řekne; podepište se pod to.

**AI:** postaví web. Nejjednodušší cesta: vezměte náš repozitář jako
šablonu (github.com/novotny25/transparentniprstice.cz — podmínky převzetí
v souboru LICENSE v repozitáři), vyměňte datové soubory a texty. Nebo od nuly:

> **Prompt 8:** Jsem občan obce [název] a mám ověřená data o jejím
> hospodaření (přikládám pouze sanitizované CSV + chronologii žádostí
> o informace). Postav
> statický web bez závislostí, který: 1) ukáže rozpočet obce srozumitelně
> laikovi (příjmy, výdaje, saldo, kategorie a přepočet na obyvatele), 2) má
> sekci s vývojem účtu [518] a mými otázkami k vybraným účetním zápisům — fakta
> vždy odděl od komentáře a u každého čísla uveď zdroj, 3) obsahuje
> chronologii mých žádostí dle zákona 106 s dokumenty ke stažení.
> Výstup označ jako občanskou datovou analýzu, nikoli audit. Rozpočtové
> peněžní výdaje a účetní náklady 518 ukaž odděleně. Použij jednu stručnou
> legendu typů informace. Nejdřív mi navrhni strukturu a design, nic nestav, dokud strukturu
> neschválím. Pak postupuj po malých krocích a po každém mi ukaž výsledek.

---

## Co vás to bude stát

Čas: zhruba 2–4 víkendy. Peníze: doména ~300 Kč/rok, hosting zdarma,
AI asistent ~500 Kč/měsíc v placené verzi. Podání žádosti podle zákona 106
je zdarma; obec může podle § 17 zákona žádat úhradu nákladů (kopie, nosiče
dat, odeslání, mimořádně rozsáhlé vyhledávání) — musí to ale oznámit předem,
a když žádáte elektronický opis datovou schránkou, bývá to bez nákladů.

## Čeho se vyvarovat

- Nezveřejňujte nic, co nemáte doložené. Ani sugestivní otázka nesmí
  nahrazovat chybějící skutkový základ.
- Nenechte AI „dopočítat" chybějící údaje — chybějící údaj je zjištění,
  ne mezera k vyplnění.
- Nepouštějte se do osobních útoků na zastupitele ani dodavatele —
  zabije to důvěryhodnost a vystaví vás žalobě.
- Dejte obci vždy prostor k vyjádření a zveřejněte ho po nezbytné anonymizaci
  a dalších odůvodněných redakcích.
