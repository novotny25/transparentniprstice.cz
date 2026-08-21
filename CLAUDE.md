# Transparentní Prštice — pravidla pro AI

Web transparentniprstice.cz: srozumitelné a doložitelné informace o hospodaření
obce Prštice pro občany. Provozovatel: Petr Novotný, občan Prštic — osobní
občanský projekt, neutrální datový tón.

**Závazné zadání je v `ZADANI.md`** (požadavky P-1 až P-24 a sekce 7 „Co v první
verzi NEBUDE"). Prováděcí plán leží v PACT workspace:
`0_Projects/4_PRŠTICE/2026_08_21 TransparentniPrstice.cz/PLAN.md`.

## Struktura repozitáře

| Složka | Obsah | Pravidlo |
|---|---|---|
| `data/` | JSON/CSV — jediný zdroj pravdy pro všechna čísla | grafy a texty se generují odsud, nikdy naopak |
| `dokumenty/` | anonymizovaná PDF (žádosti 106, odpovědi obce…) | názvosloví `RRRR-MM-DD_nazev.pdf` |
| `web/` | HTML/CSS/JS statického webu | bez buildu, bez externích závislostí |
| `skripty/` | Python — extrakce a validace dat | `skripty/validace.py` musí projít před každým nasazením |

## MUSÍ (MUST)

- Každé číslo na webu pochází ze souboru v `data/` a má uvedený zdroj a datum.
- Před hlášením „hotovo": spustit `skripty/validace.py`, otevřít web
  v prohlížeči a ověřit hlavní cestu čtenáře; u větší změny přiložit screenshot.
- Fakta a komentář oddělovat — komentářové bloky jsou označené jako názor autora.
- U dat rozlišovat ✅ doloženo dokumentem / ⚠️ odvozeno či dopočteno autorem.
- Po každém uzavřeném úkolu shrnout: co se změnilo, jak ověřeno, co se může rozbít.
- Psát česky, běžným jazykem; účetní pojmy vysvětlovat (slovníček).

## NESMÍ (MUST NOT)

- Commitnout neanonymizovaný dokument, osobní údaje soukromých osob, API klíč
  nebo token — ani dočasně (historie gitu je veřejná paměť).
- Používat hodnotící nálepky („podezřelé", „tunel", „rozkradli") — pouze fakta,
  otázky a srovnání se zdrojem.
- Tvrdit příčinnou souvislost tam, kde je doložená jen souvislost.
- Měnit soubory mimo zadaný úkol; přepisovat data v `data/` bez validace.
- Commitovat bez vědomí Petra — commit je jeho rozhodnutí.

## Styl a kvalita webu

- Statický HTML bez závislostí; text ≥ 16 px, řádek max 65ch, kontrast WCAG AA,
  jeden H1, funkční od šířky 360 px, světlý i tmavý režim, `lang="cs"`.
- Barva nikdy jako jediný nositel významu; každý graf má tabulkovou alternativu
  a tlačítko „stáhnout data (CSV)".
- Postupné odkrývání: přehled → kategorie → položka → původní dokument.
