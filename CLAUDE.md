# Transparentní Prštice — pravidla pro AI

Web transparentniprstice.cz: srozumitelná a doložitelná občanská datová analýza
hospodaření obce Prštice. Provozovatel: Petr Novotný, občan Prštic — osobní
občanský projekt, neutrální datový tón. Projekt není audit.

**Závazné zadání je v `ZADANI.md` v1.4.** Prováděcí kopie je v `PLAN.md` v1.4;
autorský originál obou dokumentů leží v PACT workspace:
`0_Projects/4_PRŠTICE/2026_08_21 TransparentniPrstice.cz/`.

## Struktura repozitáře

| Složka | Obsah | Pravidlo |
|---|---|---|
| `data/` | pouze veřejné sanitizované JSON/CSV | grafy a texty se generují odsud, nikdy z originálů |
| `dokumenty/` | strojově anonymizované veřejné deriváty PDF | žádný originál ani skrytá původní vrstva |
| `anonymizace/` | publikační pravidla a allowlist | bez soukromých hodnot a privátních QA reportů |
| `web/` | HTML/CSS/JS statického webu | bez buildu, bez externích závislostí |
| `skripty/` | Python — extrakce, anonymizace a validace | privacy gate musí projít před každým nasazením |

## MUSÍ (MUST)

- Každé číslo na webu pochází ze sanitizovaného souboru v `data/` a má zdroj,
  datum nebo reprodukovatelný výpočet.
- Před hlášením „hotovo": spustit `skripty/validace.py`, otevřít web
  v prohlížeči a ověřit hlavní cestu čtenáře; u větší změny přiložit screenshot.
- Fakta a komentář oddělovat — komentářové bloky jsou označené jako názor autora.
- U důležitých údajů rozlišovat: převzato ze zdroje / vypočítáno / zařazeno
  autorem / nezjištěno.
- Rozpočtové peněžní výdaje a akruální účetní náklady 518 ukazovat odděleně.
- Soudní a správní řízení vést jako dva typy; ÚOHS nikdy neoznačovat jako soud.
- Před commitem veřejných dat nebo dokumentů vyžadovat privacy PASS,
  nevyřešené nálezy 0 a Petrův sign-off pro aktuální commit.
- Po každém uzavřeném úkolu shrnout: co se změnilo, jak ověřeno, co se může rozbít.
- Psát česky, běžným jazykem; účetní pojmy vysvětlovat (slovníček).

## NESMÍ (MUST NOT)

- Commitnout originální účetní export, neanonymizované JSON/CSV/HTML/PDF,
  soukromý QA report, API klíč nebo token — ani dočasně, do jiné větve nebo
  deploy preview.
- Zveřejnit původní volný účetní popis nebo jméno fyzické osoby mimo výslovně
  schválený publikační allowlist.
- Používat hodnotící nálepky („podezřelé", „tunel", „rozkradli"). Hodnocení
  hospodárnosti musí uvést kritérium a doložený základ.
- Tvrdit příčinnou souvislost tam, kde je doložená jen souvislost.
- Měnit soubory mimo zadaný úkol; přepisovat data v `data/` bez validace.
- Commitovat bez vědomí Petra — commit je jeho rozhodnutí.

## Styl a kvalita webu

- Statický HTML bez závislostí; text ≥ 16 px, řádek max 65ch, kontrast WCAG AA,
  jeden H1, funkční od šířky 360 px, spolehlivý světlý režim, `lang="cs"`.
- Barva nikdy jako jediný nositel významu; každý graf má tabulkovou alternativu
  a tlačítko „stáhnout data (CSV)".
- Postupné odkrývání: přehled → kategorie → položka → původní dokument.
