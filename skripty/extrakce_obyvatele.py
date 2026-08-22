#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Počty obyvatel obce Prštice — Transparentní Prštice (PLAN.md úkol 1.5)

Vstup:  ČSÚ „Databáze demografických údajů za obce ČR" — okres Brno-venkov
        (cz0643.xlsx, list CZ0643, sloupec „Stav 1.1."), v soukromé zóně/zdroje.
Výstup: data/obyvatele.json — počet obyvatel Prštic (kód 583707) k 1.1.
        za roky 2015–2025 se zdrojem a datem (pro přepínač „Kč na obyvatele").

Zásady:
  * Oficiální bilance ČSÚ (po revizi sčítáním 2021) — konzistentní řada „k 1.1.".
  * Rok 2026 zatím není v konzistentní databázi (poslední stav k 1.1.2025).
  * Zdroj je veřejná open-data ČSÚ; originál leží v soukromé zóně, do repa jde
    jen odvozený JSON.

Spuštění: python3 skripty/extrakce_obyvatele.py
"""
import os, sys, json, hashlib
from datetime import datetime
import openpyxl

PRIVATE_ZONE = os.path.expanduser("~/Developer/transparentniprstice-private")
WEB_ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZDROJ        = os.path.join(PRIVATE_ZONE, "zdroje", "cz0643.xlsx")
ZDROJ_SHA256 = "d53159d9271d6055ae474ae284633f143b58fed7a775c5b0072ac12ffe6c2ec6"

KOD_OBCE = "583707"
ROKY = list(range(2015, 2026))   # 2015–2025 (2026 zatím není v DB)

# Kontrolní tabulka (ČSÚ Stav k 1.1.) — pro ověření správné extrakce.
KONTROLA = {2015: 931, 2016: 938, 2017: 951, 2018: 955, 2019: 974, 2020: 971,
            2021: 969, 2022: 978, 2023: 982, 2024: 981, 2025: 997}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not os.path.exists(ZDROJ):
        sys.exit(f"CHYBA: zdroj nenalezen:\n  {ZDROJ}\n  (ČSÚ open data cz0643.xlsx, soukromá zóna/zdroje)")
    h = sha256_file(ZDROJ)
    if h != ZDROJ_SHA256:
        sys.exit(f"CHYBA: SHA-256 zdroje nesouhlasí — zdroj se změnil.\n  čekáno: {ZDROJ_SHA256}\n  zjištěno: {h}")

    wb = openpyxl.load_workbook(ZDROJ, read_only=True, data_only=True)
    ws = wb["CZ0643"]
    obyv = {}
    for row in ws.iter_rows(values_only=True):
        if row[0] == "Rok":
            assert row[4] and "1.1." in str(row[4]), "Nečekaná struktura: sloupec 4 není „Stav 1.1.“"
            continue
        if str(row[1]) == KOD_OBCE:
            obyv[int(row[0])] = int(row[4])

    chybi = [r for r in ROKY if r not in obyv]
    if chybi:
        sys.exit(f"CHYBA: v datech chybí roky {chybi}.")

    # kontrola proti kontrolní tabulce
    nesed = [(r, obyv[r], KONTROLA[r]) for r in ROKY if obyv[r] != KONTROLA[r]]
    if nesed:
        for r, a, b in nesed:
            print(f"  [FAIL] {r}: {a} ≠ kontrola {b}")
        sys.exit("CHYBA: hodnoty nesedí na kontrolní tabulku.")

    out = {
        "meta": {
            "obec": "Prštice", "kod_obce": KOD_OBCE, "okres": "Brno-venkov",
            "ukazatel": "počet obyvatel, stav k 1.1.",
            "zdroj": "Český statistický úřad — Databáze demografických údajů za obce ČR",
            "zdroj_url": "https://csu.gov.cz/databaze-demografickych-udaju-za-obce-cr",
            "referencni_datum": "k 1.1.",
            "poznamka": "Oficiální bilance ČSÚ (po revizi sčítáním 2021, proto 2021 = 969, "
                        "nikoli 985 z některých agregátorů ani 959 ze sčítání). "
                        "Rok 2026 zatím není v konzistentní databázi (poslední stav k 1.1.2025).",
            "staženo": "2026-08-22",
            "vygenerovano": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "obyvatele": {str(r): obyv[r] for r in ROKY},
    }
    os.makedirs(os.path.join(WEB_ROOT, "data"), exist_ok=True)
    out_path = os.path.join(WEB_ROOT, "data", "obyvatele.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print("HOTOVO — počty obyvatel Prštic (úkol 1.5)")
    print(f"  zdroj ověřen (SHA-256): OK | výstup: {out_path}")
    print("  Stav k 1.1.:", ", ".join(f"{r}={obyv[r]}" for r in ROKY))
    print("  Všechny hodnoty sedí na kontrolní tabulku ✓")


if __name__ == "__main__":
    main()
