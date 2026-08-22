#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roční řady a ukazatele vývoje (úkol 1.2).

Ze zdrojového auditního dashboardu (JSON ve <script id="audit-data">)
vytáhne řady výkazu zisku a ztráty 2015–2025:
  - účet 518 (Ostatní služby)      — hlavní řada webu
  - účet 511 (Opravy a udržování)  — kontext
  - náklady celkem, výnosy celkem  — kontext

Zdroj je v tis. Kč; výstup je v celých haléřích a nese jednotku i bázi.
Pro účet 518 dopočítá změnu 2015→2025 a CAGR (odvozené z ročních hodnot,
každá ověřitelná výpočtem). Klouzavý průměr se NEuvádí — na grafu vývoje
518 musí být jen přesné roční hodnoty odpovídající veřejnému výkazu.
Vše se počítá znovu ze zdroje — žádné předem zvolené hodnoty.

Výstup: data/vykazy-rady.json (veřejný — agregát z veřejného výkazu, bez PII).
"""
import argparse, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACT = Path("/home/user/0_PACT/0_Projects/4_PRŠTICE")
DEF_SRC = PACT / "2026_04_30 Audit hospodaření obce" / "audit-prstice-rozvaha-vzz-dashboard.html"
DEF_OUT = REPO / "data" / "vykazy-rady.json"

ZDROJ = {
    "vykaz": "Výkaz zisku a ztráty (účetní, akruální)",
    "puvod": "MONITOR MF ČR, otevřená data",
    "ico": "00282405",
    "jednotka_zdroje": "tis. Kč",
}


def nacti(src: Path):
    m = re.search(r'<script id="audit-data"[^>]*>(.*?)</script>',
                  src.read_text(encoding="utf-8"), re.S)
    if not m:
        sys.exit("Nenalezen <script id=\"audit-data\"> ve zdroji.")
    return json.loads(m.group(1))


def rada(vzz, account=None, name=None):
    """Vrátí {rok: haléře} pro daný účet nebo název řádku VZZ."""
    out = {}
    for it in vzz:
        if account is not None and str(it.get("account", "")).strip() != account:
            continue
        if name is not None and (it.get("name") or "").strip() != name:
            continue
        hal = round(float(it["value"]) * 100_000)  # tis. Kč → haléře
        out[int(it["year"])] = hal
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=DEF_SRC)
    ap.add_argument("--out", type=Path, default=DEF_OUT)
    args = ap.parse_args()
    if not args.src.exists():
        sys.exit(f"Zdroj nenalezen: {args.src}")

    d = nacti(args.src)
    vzz = [it for it in d["items"] if it["statement"] == "Výkaz zisku a ztráty"]
    gen = d.get("covered", {}).get("generated_at", "")

    r518 = rada(vzz, account="518")
    r511 = rada(vzz, account="511")
    rnakl = rada(vzz, name="NÁKLADY CELKEM")
    rvyn = rada(vzz, name="VÝNOSY CELKEM")
    roky = sorted(r518)
    if roky != list(range(2015, 2026)):
        sys.exit(f"Neočekávaný rozsah let účtu 518: {roky}")

    zmena_pct = (r518[2025] - r518[2015]) / r518[2015] * 100
    cagr_pct = ((r518[2025] / r518[2015]) ** (1 / (2025 - 2015)) - 1) * 100
    avg_prvni = sum(r518[y] for y in (2015, 2016, 2017)) / 3
    avg_posl = sum(r518[y] for y in (2023, 2024, 2025)) / 3

    def serie(r):
        return [{"rok": y, "castka_hal": r[y]} for y in sorted(r)]

    out = {
        "zdroj": ZDROJ,
        "vygenerovano_ze_zdroje": gen,
        "jednotka": "haléře (celé Kč × 100)",
        "poznamka_ceny": "Běžné ceny daného roku, bez odečtení inflace.",
        "rady": {
            "ucet_518": {
                "nazev": "Účet 518 – Ostatní služby",
                "kod_vzz": "A.I.12.",
                "basis": "accrual_cost",
                "titulek_web": "Vývoj účtu 518 v letech 2015–2025",
                "hodnoty": serie(r518),
            },
            "ucet_511": {
                "nazev": "Účet 511 – Opravy a udržování",
                "kod_vzz": "A.I.8.",
                "basis": "accrual_cost",
                "hodnoty": serie(r511),
            },
            "naklady_celkem": {
                "nazev": "Náklady celkem",
                "basis": "accrual_cost",
                "hodnoty": serie(rnakl),
            },
            "vynosy_celkem": {
                "nazev": "Výnosy celkem",
                "basis": "accrual_cost",
                "hodnoty": serie(rvyn),
            },
        },
        "ukazatele_518": {
            "zmena_2015_2025_pct": round(zmena_pct, 1),
            "cagr_2015_2025_pct": round(cagr_pct, 1),
            "prumer_2015_2017_hal": round(avg_prvni),
            "prumer_2023_2025_hal": round(avg_posl),
            "zmena_prumeru_pct": round((avg_posl - avg_prvni) / avg_prvni * 100, 1),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Zapsáno {args.out}")
    print("518 (Kč):", {y: f"{r518[y]/100:,.2f}" for y in roky})
    print(f"změna 2015→2025: {out['ukazatele_518']['zmena_2015_2025_pct']} %, "
          f"CAGR {out['ukazatele_518']['cagr_2015_2025_pct']} %")
    print(f"tříletý průměr 2015–2017: {avg_prvni/1e8:.2f} mil, "
          f"2023–2025: {avg_posl/1e8:.2f} mil, "
          f"změna {out['ukazatele_518']['zmena_prumeru_pct']} %")


if __name__ == "__main__":
    main()
