#!/usr/bin/env python3
"""Srovnání čerpání dotací (přijatých transferů) Prštic s okolními obcemi.

Zdroj: MONITOR státní pokladny, rozklikávací rozpočet — konsolidovaná
skutečnost, třída 4 „Přijaté transfery". Počty obyvatel: ČSÚ (privátní zdroj).

Vytváří data/srovnani-dotaci.json. Reprodukovatelné: stačí spustit znovu.
"""
import json
import os
import time
import urllib.request

import openpyxl

ZDE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ZDE)
PRIV = os.path.expanduser("~/Developer/transparentniprstice-private")
CSU_OBCE = os.path.join(PRIV, "zdroje", "cz0643.xlsx")   # obce okresu Brno-venkov
VYSTUP = os.path.join(REPO, "data", "srovnani-dotaci.json")

ROKY = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
ROK_OBYVATEL = 2025

# Okruh obcí zvolený autorem: sousední obce Prštic a obce „přes jednu".
SOUSEDNI = ["Prštice", "Silůvky", "Radostice", "Ořechov", "Hlína"]
SIRSI = ["Mělčany", "Hajany", "Želešice", "Moravany", "Nebovidy",
         "Střelice", "Moravské Bránice"]


def http_json(url, telo=None):
    data = json.dumps(telo).encode() if telo is not None else None
    hlavicky = {"Accept": "application/json", "User-Agent": "transparentniprstice.cz"}
    if telo is not None:
        hlavicky["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hlavicky)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def obce_okresu():
    """název obce -> (kód obce, počet obyvatel k 1. 1. ROK_OBYVATEL)"""
    ws = openpyxl.load_workbook(CSU_OBCE, read_only=True, data_only=True)["CZ0643"]
    out = {}
    for r in ws.iter_rows(values_only=True):
        try:
            rok = int(r[0])
        except (TypeError, ValueError):
            continue
        if rok == ROK_OBYVATEL and r[4] not in (None, ""):
            out[str(r[2]).strip()] = (str(r[1]), int(r[4]))
    return out


def ares_ico(kod_obce):
    d = http_json("https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/vyhledat",
                  {"sidlo": {"kodObce": int(kod_obce)}, "pravniForma": ["801"],
                   "pocet": 5, "start": 0})
    for s in d.get("ekonomickeSubjekty", []):
        if s.get("sidlo", {}).get("kodObce") == int(kod_obce):
            return s["ico"]
    subs = d.get("ekonomickeSubjekty", [])
    return subs[0]["ico"] if subs else None


def monitor_prijmy(ico, rok):
    """(celkové konsolidované příjmy, přijaté transfery třídy 4) za rok."""
    url = ("https://monitor.statnipokladna.gov.cz/api/rozpocet/souhrnny"
           f"?obdobi={rok - 2000:02d}12&ic={ico}")
    try:
        d = http_json(url)
    except Exception:
        return None, None
    for ch in d.get("children", []):
        if ch.get("name") != "Revenues":
            continue
        celkem = (ch.get("budget") or {}).get("reality")
        transfery = None
        for g in ch.get("children", []):
            if str(g.get("code")) == "4":
                transfery = (g.get("budget") or {}).get("reality")
        return celkem, (transfery or 0.0)
    return None, None


def main():
    katalog = obce_okresu()
    vysledky = []
    for nazev in SOUSEDNI + SIRSI:
        if nazev not in katalog:
            print(f"  ! {nazev}: není v číselníku okresu — přeskakuji")
            continue
        kod, obyvatel = katalog[nazev]
        ico = ares_ico(kod)
        time.sleep(0.2)
        if not ico:
            print(f"  ! {nazev}: nenalezeno IČO")
            continue
        rada = {}
        for rok in ROKY:
            celkem, transfery = monitor_prijmy(ico, rok)
            time.sleep(0.2)
            if celkem:
                rada[str(rok)] = {
                    "prijmy_kc": round(celkem),
                    "dotace_kc": round(transfery),
                    "podil_pct": round(transfery / celkem * 100, 1),
                    "na_obyvatele_kc": round(transfery / obyvatel),
                }
        if not rada:
            print(f"  ! {nazev}: žádná data z MONITORu")
            continue
        soucet_dot = sum(v["dotace_kc"] for v in rada.values())
        soucet_prij = sum(v["prijmy_kc"] for v in rada.values())
        vysledky.append({
            "obec": nazev,
            "kod": kod,
            "ico": ico,
            "obyvatel": obyvatel,
            "okruh": "sousední" if nazev in SOUSEDNI else "přes jednu obec",
            "roky": rada,
            "souhrn": {
                "dotace_celkem_kc": soucet_dot,
                "prijmy_celkem_kc": soucet_prij,
                "podil_pct": round(soucet_dot / soucet_prij * 100, 1),
                "na_obyvatele_kc": round(soucet_dot / obyvatel),
                "rocne_na_obyvatele_kc": round(soucet_dot / obyvatel / len(rada)),
            },
        })
        s = vysledky[-1]["souhrn"]
        print(f"  {nazev:20s} {obyvatel:5d} obyv. | dotace {soucet_dot:12,.0f} Kč "
              f"| {s['podil_pct']:4.1f} % | {s['rocne_na_obyvatele_kc']:5d} Kč/obyv./rok"
              .replace(",", " "))

    vysledky.sort(key=lambda o: o["souhrn"]["rocne_na_obyvatele_kc"], reverse=True)
    poradi = [o["obec"] for o in vysledky]
    out = {
        "meta": {
            "ukol": "Srovnání čerpání dotací s okolními obcemi (zadání Petra 29. 8. 2026)",
            "definice": "Dotace = třída 4 rozpočtové skladby „Přijaté transfery“ "
                        "(konsolidovaná skutečnost). Zahrnuje i pravidelné transfery "
                        "na výkon státní správy, nejen investiční dotace.",
            "obdobi": f"{ROKY[0]}–{ROKY[-1]}",
            "zdroje": ["MONITOR MF ČR — rozklikávací rozpočet",
                       "ARES — IČO obcí", "ČSÚ — počty obyvatel k 1. 1. 2025"],
            "poradi_prstic_od_nejvyssiho": poradi.index("Prštice") + 1 if "Prštice" in poradi else None,
            "obci_celkem": len(vysledky),
        },
        "obce": vysledky,
    }
    with open(VYSTUP, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"\nUloženo: {VYSTUP}")
    print(f"Pořadí Prštic od nejvyššího čerpání: {out['meta']['poradi_prstic_od_nejvyssiho']}"
          f" z {len(vysledky)}")


if __name__ == "__main__":
    main()
