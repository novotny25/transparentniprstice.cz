#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rozpočet — skutečné příjmy/výdaje po agendách — PŘEDBĚŽNÉ (PLAN.md úkol 1.4)

STAV: MONITOR byl při zpracování v údržbě. Tato PŘEDBĚŽNÁ verze čte skutečnost
z lokálních výkazů FIN 2-12 M (PDF) pro roky 2022 a 2023. Chybí 2019–2021, 2024,
2025 — doplní se z MONITORu, až bude dostupný. Metodika P-33 (opakované vs.
jednorázové) se NEDĚLÁ, protože potřebuje celou řadu let.

Vstup:  FIN 2-12 M v PDF (v PACTu, audit/01_rozpocet-a-hospodareni).
Výstup: data/rozpocet.json — báze cash_budget, incomplete; výdaje po paragrafech
        (skutečnost) + celkové příjmy/výdaje/saldo.

Zásady:
  * basis: cash_budget (peněžní rozpočet) — NEsčítá se s účtem 518 (accrual).
  * Součet paragrafů se ověřuje proti rekapitulaci „Výdaje celkem"; při rozporu chyba.
  * 6330 „Převody vlastním fondům" = vnitřní převody (ne výdaj na agendu) — příznak.

Spuštění: python3 skripty/extrakce_rozpocet.py
"""
import os, re, sys, json
from datetime import datetime
import fitz

PACT_ROOT = os.path.expanduser("~/Documents/AI/0_PACT")
WEB_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROZP_DIR  = os.path.join(PACT_ROOT, "0_Projects/4_PRŠTICE/2026_04_30 Audit hospodaření obce/01_rozpocet-a-hospodareni")

FIN_PDF = {
    2022: "2022_fin-2022798595664.pdf",
    2023: "2023_fin-2023.pdf",
}
# vnitřní převody / financování — ne skutečný výdaj na agendu (příznak pro web)
VNITRNI_PREVODY = {"6330"}


def num(s):
    s = str(s).replace("\xa0", "").replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def parse_fin(path):
    doc = fitz.open(path)
    lines = [l.strip() for p in range(doc.page_count) for l in doc[p].get_text().split("\n")]
    vyd_start = [i for i, l in enumerate(lines) if "Rozpočtové výdaje" in l][-1]
    vyd_end = next(i for i, l in enumerate(lines) if l == "Příjmy celkem")

    parag = {}
    for i in range(vyd_start, vyd_end):
        if lines[i] == "XXXX":
            code = lines[i - 1]
            skut = num(lines[i - 3])
            nazev = lines[i - 5]
            if re.match(r"^\d{4}$", code) and skut is not None:
                parag[code] = {"nazev": nazev, "skutecnost_kc": round(skut, 2)}

    def recap(label):
        i = next(k for k, l in enumerate(lines) if l == label)
        return num(lines[i + 4])

    prijmy = recap("Příjmy celkem")
    vydaje = recap("Výdaje celkem")
    vydaje_kons = recap("Výdaje celkem po konsolidaci")
    prijmy_kons = recap("Příjmy celkem po konsolidaci")
    saldo_kons = recap("Saldo příjmů a výdajů po konsolidaci")

    suma_parag = round(sum(p["skutecnost_kc"] for p in parag.values()), 2)
    if abs(suma_parag - vydaje) > 0.05:
        sys.exit(f"CHYBA [{os.path.basename(path)}]: součet paragrafů {suma_parag} "
                 f"≠ rekapitulace Výdaje celkem {vydaje}")

    return {
        "prijmy_celkem_kc": round(prijmy, 2),
        "vydaje_celkem_kc": round(vydaje, 2),
        "prijmy_po_konsolidaci_kc": round(prijmy_kons, 2),
        "vydaje_po_konsolidaci_kc": round(vydaje_kons, 2),
        "saldo_po_konsolidaci_kc": round(saldo_kons, 2),
        "vydaje_po_paragrafech": parag,
    }


def main():
    roky = {}
    for rok, fn in FIN_PDF.items():
        path = os.path.join(ROZP_DIR, fn)
        if not os.path.exists(path):
            sys.exit(f"CHYBA: chybí FIN PDF {path}")
        roky[rok] = parse_fin(path)
        # označ vnitřní převody
        for code in roky[rok]["vydaje_po_paragrafech"]:
            if code in VNITRNI_PREVODY:
                roky[rok]["vydaje_po_paragrafech"][code]["vnitrni_prevod"] = True

    out = {
        "meta": {
            "basis": "cash_budget",
            "jednotka": "Kč",
            "obec": "Prštice", "ico": "00282405",
            "zdroj": "Výkaz FIN 2-12 M (skutečnost k 31.12.), lokální PDF",
            "stav": "incomplete",
            "dostupne_roky": sorted(roky.keys()),
            "chybi_roky": [2019, 2020, 2021, 2024, 2025],
            "poznamka": "PŘEDBĚŽNÉ. MONITOR byl v údržbě; doplní se roky 2019–2021, "
                        "2024, 2025 z MONITORu. Rozlišení opakované/jednorázové (P-33) "
                        "vyžaduje celou řadu let a zatím se nedělá. "
                        "cash_budget se nesčítá s účtem 518 (accrual_cost). "
                        "6330 = vnitřní převody, ne výdaj na agendu.",
            "vygenerovano": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "roky": {str(r): roky[r] for r in sorted(roky)},
    }
    os.makedirs(os.path.join(WEB_ROOT, "data"), exist_ok=True)
    out_path = os.path.join(WEB_ROOT, "data", "rozpocet.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print("HOTOVO (PŘEDBĚŽNĚ) — rozpočet z lokálních FIN 2-12 M (úkol 1.4)")
    for r in sorted(roky):
        d = roky[r]
        print(f"  {r}: příjmy {d['prijmy_celkem_kc']:,.0f} | výdaje {d['vydaje_celkem_kc']:,.0f} "
              f"| saldo(kons) {d['saldo_po_konsolidaci_kc']:,.0f} | paragrafů {len(d['vydaje_po_paragrafech'])} "
              "(součet = rekapitulace ✓)".replace(",", " "))
    print(f"  výstup: {out_path}")
    print("  Chybí 2019–2021, 2024, 2025 (MONITOR v údržbě) · P-33 metodika odložena.")


if __name__ == "__main__":
    main()
