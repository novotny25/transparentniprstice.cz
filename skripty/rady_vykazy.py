#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roční řady a ukazatele vývoje účtu 518 — Transparentní Prštice (PLAN.md úkol 1.2)

Vstup:  audit-prstice-rozvaha-vzz-dashboard.html (<script id="audit-data">) v PACTu.
Výstup: data/vykazy-rady.json — řady 2015–2025 pro účet 518, účet 511 a
        náklady/výnosy celkem, plus ukazatele vývoje účtu 518.

Zásady:
  * Zdroj je v tis. Kč; výstup je v celých Kč a nese jednotku (ZADANI P-1).
  * Účet 518 = accrual_cost; nesčítá se s rozpočtem (FIN 2-12 M).
  * Vše se přepočítá ZE ZDROJE; skript ověří výsledky proti kontrolním hodnotám
    z plánu a při rozporu skončí chybou.

Spuštění: python3 skripty/rady_vykazy.py
"""
import os, re, json, sys, hashlib
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

PACT_ROOT = os.path.expanduser("~/Documents/AI/0_PACT")
WEB_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ZDROJ = os.path.join(
    PACT_ROOT,
    "0_Projects/4_PRŠTICE/2026_04_30 Audit hospodaření obce/"
    "audit-prstice-rozvaha-vzz-dashboard.html",
)
ZDROJ_SHA256 = "d302415662bfc3be823ce88b79a50549d9d6b65189a5ac06fc83aa16d0e08e05"

ROKY = list(range(2015, 2026))   # 2015–2025 (11 hodnot)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def kc(tis):
    """tis. Kč -> celé Kč (zaokrouhlení půl nahoru)."""
    return int((Decimal(str(tis)) * 1000).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def main():
    if not os.path.exists(ZDROJ):
        sys.exit(f"CHYBA: zdroj nenalezen:\n  {ZDROJ}")
    h = sha256_file(ZDROJ)
    if h != ZDROJ_SHA256:
        sys.exit("CHYBA: SHA-256 zdroje nesouhlasí s manifestem — zdroj se změnil!\n"
                 f"  čekáno:   {ZDROJ_SHA256}\n  zjištěno: {h}")

    html = open(ZDROJ, encoding='utf-8').read()
    d = json.loads(re.search(r'<script id="audit-data"[^>]*>(.*?)</script>', html, re.S).group(1))
    assert d['covered']['unit'] == 'tis. Kč', "Nečekaná jednotka zdroje."

    # --- Řady účtů 518 a 511 z položek VZZ (pole account) ---
    s518, s511 = {}, {}
    for it in d['items']:
        acc = str(it.get('account', ''))
        if it.get('statement') == 'Výkaz zisku a ztráty':
            if acc == '518': s518[it['year']] = it['value']
            elif acc == '511': s511[it['year']] = it['value']

    # --- Náklady/výnosy celkem z metrik ---
    metrics = {m['id']: m for m in d['metrics']}
    naklady = {s['year']: s['value'] for s in metrics['naklady']['series']}
    vynosy  = {s['year']: s['value'] for s in metrics['vynosy']['series']}

    for jmeno, serie in (('518', s518), ('511', s511), ('náklady', naklady), ('výnosy', vynosy)):
        chybi = [r for r in ROKY if r not in serie]
        if chybi:
            sys.exit(f"CHYBA: v řadě {jmeno} chybí roky {chybi}.")

    # --- Ukazatele účtu 518 (počítáno v tis. Kč, pak převod) ---
    v15, v25 = s518[2015], s518[2025]
    zmena_pct = (v25 / v15 - 1) * 100
    cagr_pct  = ((v25 / v15) ** (1 / (2025 - 2015)) - 1) * 100
    # centrovaný tříletý klouzavý průměr pro vnitřní roky 2016–2024
    ma = {}
    for r in range(2016, 2025):
        ma[r] = kc((s518[r - 1] + s518[r] + s518[r + 1]) / 3)
    pr_2015_2017 = (s518[2015] + s518[2016] + s518[2017]) / 3   # = MA 2016
    pr_2023_2025 = (s518[2023] + s518[2024] + s518[2025]) / 3   # = MA 2024
    zmena_prumeru_pct = (pr_2023_2025 / pr_2015_2017 - 1) * 100

    out = {
        "meta": {
            "titulek_518": "Vývoj účtu 518 v letech 2015–2025",
            "zdroj": "Rozvaha + Výkaz zisku a ztráty, MONITOR MF ČR (IČO 00282405)",
            "jednotka": "Kč",
            "puvodni_jednotka": "tis. Kč",
            "roky": ROKY,
            "baze": "accrual_cost",
            "poznamka": "Běžné ceny, bez odečtení inflace.",
            "vygenerovano": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "rady": {
            "ucet_518": {"label": "Účet 518 – Ostatní služby",
                         "hodnoty_kc": {str(r): kc(s518[r]) for r in ROKY}},
            "ucet_511": {"label": "Účet 511 – Opravy a udržování",
                         "hodnoty_kc": {str(r): kc(s511[r]) for r in ROKY}},
            "naklady_celkem": {"label": "Náklady celkem",
                               "hodnoty_kc": {str(r): kc(naklady[r]) for r in ROKY}},
            "vynosy_celkem": {"label": "Výnosy celkem",
                              "hodnoty_kc": {str(r): kc(vynosy[r]) for r in ROKY}},
        },
        "ukazatele_518": {
            "klouzavy_prumer_3_kc": {str(r): ma[r] for r in sorted(ma)},
            "zmena_2015_2025_pct": round(zmena_pct, 1),
            "cagr_2015_2025_pct": round(cagr_pct, 1),
            "prumer_2015_2017_kc": kc(pr_2015_2017),
            "prumer_2023_2025_kc": kc(pr_2023_2025),
            "zmena_prumeru_pct": round(zmena_prumeru_pct, 1),
        },
    }

    os.makedirs(os.path.join(WEB_ROOT, "data"), exist_ok=True)
    out_path = os.path.join(WEB_ROOT, "data", "vykazy-rady.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    # --- Kontrola proti hodnotám z plánu (tvrdý gate) ---
    def blizko(a, b, tol): return abs(a - b) <= tol
    kontroly = [
        ("změna 2015→2025 = +138,6 %", blizko(zmena_pct, 138.6, 0.15)),
        ("CAGR 2015→2025 = 9,1 %",     blizko(cagr_pct, 9.1, 0.15)),
        ("průměr 2015–2017 ≈ 1,80 mil.", blizko(pr_2015_2017 / 1000, 1.80, 0.01)),
        ("průměr 2023–2025 ≈ 4,69 mil.", blizko(pr_2023_2025 / 1000, 4.69, 0.01)),
        ("změna průměrů = +160,8 %",   blizko(zmena_prumeru_pct, 160.8, 0.15)),
    ]

    # --- Křížová kontrola proti deníku 518 (úkol 1.1), pokud existuje ---
    ledger_path = os.path.join(WEB_ROOT, "data", "ucet-518-polozky-public.json")
    krizova = []
    if os.path.exists(ledger_path):
        led = json.load(open(ledger_path, encoding='utf-8'))
        sumy = {}
        for r in led:
            sumy[r['ucetni_rok']] = sumy.get(r['ucetni_rok'], 0) + r['castka_haleru']
        for rok in (2022, 2023, 2024, 2025):
            vzz_hal = int((Decimal(str(s518[rok])) * 100000).quantize(Decimal(1), ROUND_HALF_UP))
            diff_kc = abs(sumy.get(rok, 0) - vzz_hal) / 100
            krizova.append((f"deník 518 {rok} = VZZ (±1 Kč)", diff_kc <= 1.0, diff_kc))

    print("HOTOVO — roční řady výkazů (úkol 1.2)")
    print(f"  zdroj ověřen (SHA-256): OK")
    print(f"  výstup: {out_path}")
    print(f"  účet 518 (Kč): " + ", ".join(f"{r}={kc(s518[r]):,}".replace(",", " ") for r in ROKY))
    print(f"  změna 2015→2025: {zmena_pct:.1f} % | CAGR: {cagr_pct:.1f} % | "
          f"průměry {pr_2015_2017/1000:.2f}→{pr_2023_2025/1000:.2f} mil. ({zmena_prumeru_pct:+.1f} %)")
    print("  Kontroly proti plánu:")
    ok = True
    for popis, vysledek in kontroly:
        print(f"    [{'PASS' if vysledek else 'FAIL'}] {popis}")
        ok = ok and vysledek
    if krizova:
        print("  Křížová kontrola s deníkem 518 (úkol 1.1):")
        for popis, vysledek, diff in krizova:
            print(f"    [{'PASS' if vysledek else 'FAIL'}] {popis}  (rozdíl {diff:.2f} Kč)")
            ok = ok and vysledek
    if not ok:
        sys.exit("CHYBA: některá kontrola NEPROŠLA — výstup neodpovídá zdroji/plánu.")
    print("  Všechny kontroly PASS ✓")


if __name__ == "__main__":
    main()
