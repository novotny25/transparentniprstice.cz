# Jak jsme postupovali

Tento web je **občanská datová analýza hospodaření** — ne audit. Tady je
otevřeně popsané, **odkud data pocházejí a jak se ověřovala**: od veřejných
účetních výkazů, přes žádosti o informace podle zákona 106/1999 Sb., až po
řízení u nadřízeného úřadu.

## Stručně, jak šel čas

- **Duben 2026** — z **veřejných účetních výkazů** (MONITOR, rozvaha a výkaz
  zisku a ztráty) sestaven přehled hospodaření obce 2015–2025. Nápadný nárůst
  účtu 518 „Ostatní služby" dal podnět k bližšímu zkoumání.
- **Červen–srpen 2026** — série **žádostí o informace** (rozpis účtu 518,
  smlouvy, zpravodaje, pověřenec GDPR, přehled soudních řízení).
- **Obstrukce ve vyřízení** — na žádost o smlouvy obec odpověděla jen **slovním
  sdělením bez dokladů**. Následovala **stížnost** podle § 16a a poté **žádost
  o opatření proti nečinnosti** u Krajského úřadu JMK.
- **Souběžně** z veřejné **Sbírky rozhodnutí ÚOHS** ověřena tři pravomocná
  rozhodnutí (viz sekce *Soudní a správní řízení*).

> Úplná časová osa se všemi kroky a čísly jednacími se zobrazuje z dat
> (`data/chronologie.json`) — vykreslí ji hotový web.

---

## Přehled žádostí a podání (agenda podle zákona 106)

Stav **k 25. 8. 2026**. „Dní" = počet dní od podání.

| Datum | Čeho se týká | Stav | Dní |
|---|---|---|---:|
| 4. 6. 2026 | Rozpis nákladů účtu 518 (2022–2025) | částečně poskytnuto (bez dodavatelů) | 82 |
| 23. 6. 2026 | Obecní zpravodaje | k ověření | 63 |
| 1. 7. 2026 | Detail smluv k účtu 518 (SP/088/2026) | neposkytnuto | 55 |
| 17. 7. 2026 | Stížnost § 16a (k SP/088/2026) | lhůta marně uplynula | 39 |
| 17. 7. 2026 | Opis deníku 518 za 1.–6. 2026 | poskytnuto | 39 |
| 28. 7. 2026 | Opatření proti nečinnosti — KrÚ JMK | u kraje | 28 |
| 15. 8. 2026 | Pověřenec GDPR — smlouva, paušál, rozsah | podáno | 10 |
| 15. 8. 2026 | Přehled soudních řízení obce od 1. 1. 2018 | podáno — čeká se odpověď | 10 |
| 25. 8. 2026 | Rozpis účtu 511 „Opravy a udržování" (2021–2025) | podáno | 0 |

**[zdroj]** Vlastní žádosti a podání žadatele; kontrolní dokument lhůt.
**[výpočet]** Počet dní k 25. 8. 2026.

---

## Kde proces stojí

- **Krajský úřad JMK** má na rozhodnutí o opatření proti nečinnosti lhůtu
  **do 27. 8. 2026** — úřad musí vydat usnesení, i když žádosti nevyhoví.
- **Přehled soudních řízení** obce (žádost z 15. 8. 2026) — odpověď se čeká;
  do té doby je sekce soudních řízení nutně neúplná.
- **Seznam se průběžně doplňuje.** Přidání nové události = úprava jednoho
  datového souboru, bez zásahu do webu.

## Co to znamená pro čísla na webu

Detail účtu 518 obec poskytla (ovšem **bez jmen dodavatelů**). Detail dalších
velkých účtů a jednotlivé smlouvy zatím k dispozici nejsou. Proto web u řady
věcí poctivě uvádí **„nezjištěno"** a nedovozuje, co nelze doložit.
