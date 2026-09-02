# Transparentní Prštice

Zdrojový kód a veřejné sanitizované podklady webu
**transparentniprstice.cz** — občanské datové analýzy hospodaření obce
Prštice (IČO 00282405).

Provozovatel: Petr Novotný, občan Prštic. Osobní občanský projekt — fakta
se zdrojem, autorské výpočty a zařazení viditelně označené, komentář oddělený
a podepsaný. Projekt není účetním, právním ani úředním auditem.

## Stav

Dokumentace je synchronizovaná ve verzi **1.4 (21. 8. 2026)**. Realizace webu
začíná datovou a anonymizační pipeline podle `PLAN.md`.

- Zadání projektu: [ZADANI.md](ZADANI.md)
- Prováděcí plán: [PLAN.md](PLAN.md)
- Pravidla pro AI: [CLAUDE.md](CLAUDE.md)
- Volitelný návod pro další obce: [NAVOD-UDELEJTE-SI-SAMI.md](NAVOD-UDELEJTE-SI-SAMI.md)

## Veřejný repozitář

- `data/` — pouze sanitizované JSON/CSV
- `dokumenty/` — pouze strojově anonymizované veřejné deriváty PDF
- `anonymizace/` — publikační pravidla a allowlist bez soukromých údajů
- `web/` — statický web generovaný výhradně z veřejných dat
- `skripty/` — extrakce, anonymizace a validace

Původní účetní exporty a neanonymizované dokumenty zůstávají mimo tento
repozitář, jeho historii i deploy preview.

Zdroje dat: účetní podklady poskytnuté dle zákona 106/1999 Sb., MONITOR
státní pokladny MF ČR, úřední deska obce, odpovědi obce a primární záznamy
soudních či správních orgánů.

## Pracovní postup nasazení

Změny se ukládají na větev `draft` — to nic nestojí a Netlify k otevřenému
Pull Requestu samo vygeneruje živý náhled (Deploy Preview) zdarma. Na
produkci (transparentniprstice.cz) se změna dostane až sloučením
(„Merge pull request") PR do větve `main` — to je jediný moment, kdy se
strhávají Netlify kredity.
