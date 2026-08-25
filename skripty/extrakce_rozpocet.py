#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rozpočet — skutečné příjmy/výdaje po agendách 2019–2025 (PLAN.md úkol 1.4)

Zdroj: oficiální open-data MONITOR, výkaz FIN 2-12 M (CSUIS), tabulka FINM201
       (I. příjmy VTAB 000100, II. výdaje VTAB 000200), skutečnost = ZU_ROZKZ.
       Řádky obce Prštice (IČO 00282405) jsou vytažené v soukromé zóně/zdroje;
       názvy paragrafů z číselníku CIS_PARAGRAF.CSV (MONITOR).

Výstup:
  - data/rozpocet.json         — příjmy/výdaje/saldo + výdaje po paragrafech,
                                  běžné/kapitálové a příznak opakované/jednorázové (P-33)
  - data/rozpocet-metodika.md   — metodika P-33 a hraniční případy (SCHVALUJE Petr)

Zásady:
  * basis: cash_budget — NEsčítá se s účtem 518 (accrual_cost).
  * P-33: opakovaná agenda = paragraf s nenulovým výdajem VE VŠECH sledovaných
    letech; jednorázové = nepravidelné agendy + kapitálové výdaje (třída 6).
  * 6330 „Převody vlastním fondům" = vnitřní převod, ne výdaj na agendu.

Spuštění: python3 skripty/extrakce_rozpocet.py
"""
import os, csv, sys, json
from datetime import datetime

PRIVATE_ZONE = os.path.expanduser("~/Developer/transparentniprstice-private")
WEB_ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINM_CSV     = os.path.join(PRIVATE_ZONE, "zdroje", "prstice-finm-2019-2025.csv")
PARAG_CSV    = os.path.join(PRIVATE_ZONE, "zdroje", "CIS_PARAGRAF.CSV")

ROKY = list(range(2019, 2026))
VNITRNI_PREVODY = {"6330"}            # převody vlastním fondům — ne výdaj na agendu
KONTROLA_2022_VYDAJE = 24054654.06    # křížová kontrola proti FIN PDF


def nacti_nazvy_paragrafu():
    mapa = {}
    with open(PARAG_CSV, encoding="utf-8", errors="replace") as f:
        r = csv.reader(f, delimiter=";")
        next(r, None)
        for row in r:
            if len(row) >= 7:
                code = row[0].strip().strip('"')
                if len(code) == 4 and code.isdigit():
                    mapa[code] = row[6].strip().strip('"')
    return mapa


def nacti_finm():
    """Vrátí řádky: (rok, vtab, paragraf, polozka, skutecnost)."""
    rows = []
    with open(FINM_CSV, encoding="utf-8", errors="replace") as f:
        header = f.readline()
        for line in f:
            c = line.rstrip("\n").split(";")
            if len(c) < 13:
                continue
            rok = int(c[2][:4])
            vtab = c[1]
            parag = c[8]
            polozka = c[9]
            try:
                skut = float(c[12].strip())
            except ValueError:
                skut = 0.0
            rows.append((rok, vtab, parag, polozka, skut))
    return rows


def main():
    for p in (FINM_CSV, PARAG_CSV):
        if not os.path.exists(p):
            sys.exit(f"CHYBA: chybí zdroj {p}")
    nazvy = nacti_nazvy_paragrafu()
    rows = nacti_finm()

    # výdaje po paragrafech (VTAB 000200), skutečnost, s rozlišením běžné/kapitálové
    vydaje = {r: {} for r in ROKY}    # rok -> paragraf -> {skut, bezne, kapit}
    prijmy_celkem = {r: 0.0 for r in ROKY}
    for rok, vtab, parag, polozka, skut in rows:
        if rok not in vydaje:
            continue
        if vtab == "000100":
            prijmy_celkem[rok] += skut
        elif vtab == "000200":
            d = vydaje[rok].setdefault(parag, {"skut": 0.0, "bezne": 0.0, "kapit": 0.0})
            d["skut"] += skut
            if polozka.startswith("6"):
                d["kapit"] += skut
            else:
                d["bezne"] += skut

    vydaje_celkem = {r: round(sum(p["skut"] for p in vydaje[r].values()), 2) for r in ROKY}
    kapitalove = {r: round(sum(p["kapit"] for p in vydaje[r].values()), 2) for r in ROKY}
    bezne = {r: round(sum(p["bezne"] for p in vydaje[r].values()), 2) for r in ROKY}

    # P-33: opakovaná agenda = nenulový výdaj VE VŠECH sledovaných letech
    vsechny_parag = set().union(*[set(vydaje[r]) for r in ROKY])
    opakovana = set()
    for pg in vsechny_parag:
        if all(vydaje[r].get(pg, {}).get("skut", 0) != 0 for r in ROKY):
            opakovana.add(pg)
    # vnitřní převody nepovažujeme za „běžný chod obce" (řadíme mimo opakovaný chod)
    opakovana_chod = opakovana - VNITRNI_PREVODY

    # rozdělení každého roku: opakovaný běžný chod vs jednorázové
    rozdeleni = {}
    for r in ROKY:
        chod = round(sum(vydaje[r].get(pg, {}).get("bezne", 0) for pg in opakovana_chod), 2)
        prevody = round(sum(vydaje[r].get(pg, {}).get("skut", 0) for pg in VNITRNI_PREVODY), 2)
        jednoraz = round(vydaje_celkem[r] - chod - prevody, 2)
        rozdeleni[r] = {
            "opakovany_bezny_chod_kc": chod,
            "jednorazove_kc": jednoraz,
            "vnitrni_prevody_kc": prevody,
        }

    # sestavení výstupu
    def parag_out(rok):
        out = {}
        for pg, d in sorted(vydaje[rok].items(), key=lambda x: -x[1]["skut"]):
            out[pg] = {
                "nazev": nazvy.get(pg, f"(paragraf {pg})"),
                "skutecnost_kc": round(d["skut"], 2),
                "bezne_kc": round(d["bezne"], 2),
                "kapitalove_kc": round(d["kapit"], 2),
                "opakovana": pg in opakovana_chod,
            }
            if pg in VNITRNI_PREVODY:
                out[pg]["vnitrni_prevod"] = True
        return out

    out = {
        "meta": {
            "basis": "cash_budget",
            "jednotka": "Kč",
            "obec": "Prštice", "ico": "00282405",
            "zdroj": "MONITOR (MF ČR), výkaz FIN 2-12 M, skutečnost k 31.12. (open-data CSUIS)",
            "zdroj_url": "https://monitor.statnipokladna.gov.cz/datovy-katalog/open-data",
            "stav": "complete",
            "roky": ROKY,
            "poznamka": "cash_budget se NEsčítá s účtem 518 (accrual_cost). "
                        "6330 = vnitřní převody vlastním fondům, vedeny zvlášť. "
                        "P-33: opakovaná = paragraf s nenulovým výdajem ve všech letech "
                        "2019–2025; jednorázové = nepravidelné agendy + kapitálové výdaje. "
                        "Metodika a hraniční případy v rozpocet-metodika.md (schvaluje Petr).",
            "vygenerovano": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "roky": {
            str(r): {
                "prijmy_celkem_kc": round(prijmy_celkem[r], 2),
                "vydaje_celkem_kc": vydaje_celkem[r],
                "saldo_kc": round(prijmy_celkem[r] - vydaje_celkem[r], 2),
                "bezne_vydaje_kc": bezne[r],
                "kapitalove_vydaje_kc": kapitalove[r],
                "rozdeleni_p33": rozdeleni[r],
                "vydaje_po_paragrafech": parag_out(r),
            } for r in ROKY
        },
    }
    os.makedirs(os.path.join(WEB_ROOT, "data"), exist_ok=True)
    with open(os.path.join(WEB_ROOT, "data", "rozpocet.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    # metodika P-33
    md = ["# Metodika rozlišení výdajů: opakované vs. jednorázové (P-33)\n",
          f"Obec Prštice, IČO 00282405 · zdroj MONITOR FIN 2-12 M · roky 2019–2025 · "
          f"vygenerováno {datetime.now().strftime('%Y-%m-%d')}\n",
          "> **SCHVALUJE Petr.** Web nepoužívá pojem 'mandatorní výdaje' a netvrdí, "
          "že opakovaný výdaj je ze zákona povinný nebo jednorázový zbytný. Jde o "
          "**doložitelné** rozlišení z dat, ne o právní výklad.\n",
          "## Pravidlo\n",
          "- **Opakovaný běžný chod** = běžné výdaje (třída 5) těch agend (paragrafů), "
          "které mají **nenulový výdaj ve všech sledovaných letech 2019–2025**.\n",
          "- **Jednorázové položky** = vše ostatní: běžné výdaje nepravidelných agend "
          "+ **všechny kapitálové výdaje** (třída 6).\n",
          "- **Vnitřní převody** (paragraf 6330 'Převody vlastním fondům') se vedou "
          "**zvlášť** — nejsou výdajem na agendu ani na běžný chod.\n",
          "## Opakované agendy (nenulový výdaj ve všech 7 letech)\n",
          "| Paragraf | Název |", "|---|---|"]
    for pg in sorted(opakovana_chod):
        md.append(f"| {pg} | {nazvy.get(pg, '?')} |")
    md += ["\n## Rozdělení výdajů po letech (Kč)\n",
           "| Rok | Opakovaný běžný chod | Jednorázové | Vnitřní převody | Výdaje celkem |",
           "|---:|---:|---:|---:|---:|"]
    for r in ROKY:
        rd = rozdeleni[r]
        md.append(f"| {r} | {rd['opakovany_bezny_chod_kc']:,.0f} | {rd['jednorazove_kc']:,.0f} | "
                  f"{rd['vnitrni_prevody_kc']:,.0f} | {vydaje_celkem[r]:,.0f} |".replace(",", " "))
    md += ["\n## Hraniční případy k rozhodnutí Petra\n",
           "1. **Vnitřní převody (6330)** vedeny zvlášť, ne jako výdaj. Alternativa: zahrnout do jednorázových.\n",
           "2. **Kapitálové výdaje** u opakované agendy (např. investice do silnic) jsou "
           "řazeny mezi jednorázové, i když agenda je opakovaná — počítá se jen její běžná část.\n",
           "3. Sledované období je 2019–2025 (7 let). Zkrácení období by změnilo, které "
           "agendy jsou 've všech letech'.\n"]
    with open(os.path.join(WEB_ROOT, "data", "rozpocet-metodika.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # kontroly
    diff2022 = abs(vydaje_celkem[2022] - KONTROLA_2022_VYDAJE)
    print("HOTOVO — rozpočet 2019–2025 z MONITOR FIN 2-12 M (úkol 1.4)")
    for r in ROKY:
        rd = rozdeleni[r]
        print(f"  {r}: příjmy {prijmy_celkem[r]:,.0f} | výdaje {vydaje_celkem[r]:,.0f} "
              f"| saldo {prijmy_celkem[r]-vydaje_celkem[r]:+,.0f} | opak.chod {rd['opakovany_bezny_chod_kc']:,.0f} "
              f"| jednoráz {rd['jednorazove_kc']:,.0f}".replace(",", " "))
    print(f"  opakovaných agend: {len(opakovana_chod)} | kontrola 2022 výdaje: rozdíl {diff2022:.2f} Kč "
          + ("OK" if diff2022 <= 0.05 else "!!!"))
    if diff2022 > 0.05:
        sys.exit("CHYBA: 2022 výdaje nesedí na FIN PDF.")


if __name__ == "__main__":
    main()
