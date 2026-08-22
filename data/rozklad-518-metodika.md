# Metodika: rozklad meziročních změn účtu 518

Tenhle dokument vysvětluje, jak vzniká odpověď na otázku **„co vytvořilo
meziroční rozdíl"** na účtu 518. Je psaný tak, aby si každý mohl výpočet
ověřit. Data jsou v `data/ucet-518-rozklad.json`, skript ve
`skripty/rozklad_518.py`.

## Co rozklad říká a co ne

Rozklad ukazuje, **které skupiny nákladů tvoří meziroční rozdíl** účtu 518.
Neříká — bez dalších dokladů — **proč** obec konkrétní službu objednala ani
zda byla cena přiměřená. To jsou dvě různé věci a web je nesměšuje.

Částky jsou v **běžných cenách** daného roku, bez odečtení inflace.

## Jak se počítá

1. Každý účetní zápis účtu 518 má **téma** (odpady, zámek, ČOV, právní
   služby…). Téma je autorské zařazení podle popisu a účetní kategorie
   (štítek **zařazeno autorem** dle P-4).
2. Pro každé téma se sečtou zápisy v daném roce.
3. Meziroční rozdíl tématu = součet v pozdějším roce minus v dřívějším.
4. Součet rozdílů všech témat = celková meziroční změna účtu 518. Tato
   kontrola musí sedět na haléř (a sedí).

## Zásady přiřazení (schváleno Petrem, 22. 8. 2026)

- **Storna a opravy** se přiřazují k tématu **opravovaného dokladu**, ne
  k obecné položce „opravy". Např. storno technického dozoru vody se počítá
  zpět k vodovodu.
- **Storno 2025 −309 366 Kč** patří k **ČOV**. Jde o opravu nákladu na
  převzatou odpadní vodu; číslo dokladu v účtu 518 na první pohled nesedí,
  ale věcně jde o ČOV. Důsledek: ČOV není kladným vysvětlením růstu
  2024→2025 (po započtení storna ČOV meziročně klesá).
- **Pojištění obecních budov** je **samostatné téma**, ne součást zámku.
  Jedna pojistka kryje zámek, školu, školku, kapli, obecní dům i úřad —
  přiřadit ji celou k zámku by bylo nepřesné.
- **Doprava kontejnerů** zůstává v **odpadech**, tak jak to obec zaúčtovala.

## Provedené opravy zařazení (úkol 1.7)

- Pojištění budov („pojištění-zámek, ZŠ, MŠ, kaple…") bylo omylem u hřbitova
  (kvůli slovu „kaple") → přesunuto do samostatného tématu **Pojištění budov**.
- Právní zápis 52 272 Kč vedený v účetní kategorii „Správa / odborné služby"
  je podle popisu **právní služba** → počítá se k právním službám. Po této
  opravě právní služby 2022–2025 = **2 094 182 Kč**, GDPR samostatně
  **272 250 Kč**.
- Storna přiřazena k původním tématům podle opravovaného dokladu (viz výše).

## Kontrolní hodnoty (ověřeno proti zdroji)

| Ukazatel | Hodnota |
|---|---|
| Celková změna 2022→2023 | +2 909 622,84 Kč |
| — z toho ČOV | +1 378 428,21 Kč (47,4 %) |
| — z toho zámek | +642 772,21 Kč (22,1 %) |
| — z toho odpady | +436 346,17 Kč (15,0 %) |
| — z toho právní služby | +290 980,00 Kč (10,0 %) |
| Jeřáb 2022→2023 | −56 773,20 Kč (klesl — není příčinou skoku 2023) |
| Celková změna 2023→2024 | −2 311 081,26 Kč (pokles) |
| Celková změna 2024→2025 | +1 221 138,32 Kč |
| — z toho zámek | +550 097,45 Kč (45,0 %) |
| — z toho GDPR | +272 250,00 Kč (22,3 %) |
| — z toho sondy podlah ZŠ | +117 333,70 Kč (9,6 %) |

## Poznámka k „předběžným" hodnotám zadání

Zadání (§1.7) uvádělo předběžné odhady zámku (648 072 pro 2022→2023,
593 167 pro 2024→2025) a odpadů (447 236). Tyto odhady zahrnovaly hraniční
položky jinak (pojištění budov v zámku, doprava kontejnerů mimo odpady).
Po Petrových rozhodnutích výše platí přesné, reprodukovatelné hodnoty
z této metodiky. Hlavní čísla příběhu (celky, ČOV, právní, GDPR, jeřáb,
sondy ZŠ) souhlasí přesně na haléř.
