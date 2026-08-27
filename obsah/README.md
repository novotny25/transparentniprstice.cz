# Obsah webu — textové koncepty (fáze 2)

Tato složka drží **zdrojové texty** webu odděleně od kódu. Web (fáze 3) se
z nich sestaví; čísla se přebírají z `data/`, ne z těchto textů.

Stav: **koncepty k revizi Petra** (úkol 2.1 hotov jako návrh; význam schvaluje Petr).

| Soubor | Sekce webu | Úkol PLAN.md | Stav |
|---|---|---|---|
| `00-uvod.md` | Úvod (kdo je obec, příjmy/výdaje, srovnání) | 2.1 + P-35 | schváleno (doladění po vizuálu) |
| `01-rozpocet-v-kostce.md` | Rozpočet v kostce | 2.1 | schváleno (doladění po vizuálu) |
| `02-ucet-518-vysvetleni.md` | Účet 518 — vysvětlení pro laika | 2.1 | schváleno (doladění po vizuálu) |
| `slovnicek.md` | Mini-slovníček + legenda štítků | 2.1 (P-9, P-4) | schváleno (doladění po vizuálu) |
| `03-ucet-518-pribeh.md` | Příběh 518 a rozklad změn | 2.2 (🤝) | schváleno |
| `05-soudni-spravni-rizeni.md` | Soudní a správní řízení | 2.6 (🤝) | upraveno dle Petra — k finálnímu schválení |
| `06-jak-jsme-postupovali.md` | Jak jsme postupovali + tracker 106 | 2.4 (🤖) | **koncept k revizi** |
| `04-vybrane-polozky.md` | Vybrané položky (GDPR, právní, jeřáb, odpady, ČOV) | 2.3 (🤝) | **koncept k revizi** (GDPR/právní čekají na doklady) |

Data pro časovou osu sekce „Jak jsme postupovali": `data/chronologie.json`
(odkazy na sanitizované PDF doplní krok 2.5).

## Pravidla pro tyto texty
- Vrstva **tvrdých fakt** (P-34a): neutrální tón, žádné hodnotící nálepky,
  žádné obviňování osob. Interpretační/investigativní vrstva (P-34b) je jinde
  a o jejím zveřejnění rozhoduje Petr až po právní kontrole.
- Každé číslo má zdroj a datum, nebo je označeno jako výpočet.
- Rozpočtové peněžní výdaje (báze *cash*) a účetní náklad 518 (báze *accrual*)
  se **nesčítají** — viz povinný box v `02-ucet-518-vysvetleni.md`.
- Štítky původu údaje podle P-4: **[zdroj]**, **[výpočet]**, **[autor]**,
  **[nezjištěno]** — vysvětleny v `slovnicek.md`.
