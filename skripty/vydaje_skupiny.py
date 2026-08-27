#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rozpad rozpočtu 2019–2025: výdaje ve třech úrovních (oblast → agenda → položka)
a příjmy ve dvou (skupina → položka).

Zdroj: MONITOR FIN 2-12 M (řádky obce v soukromé zóně), názvy paragrafů z
       CIS_PARAGRAF.CSV, názvy položek z API rozklikávacího rozpočtu MONITORu
       (uloženo v soukromé zóně jako nazvy-polozek.json).

Výstup: data/vydaje-skupiny.json, data/prijmy-skupiny.json (oba za všechny roky)

Zásady:
  * basis: cash_budget — nesčítá se s účtem 518 (accrual).
  * Seskupení paragrafů do „oblastí" je zařazeno autorem (P-4); součet oblastí
    se musí rovnat celkovým výdajům roku (tvrdá kontrola).
"""
import os, sys, json, csv
from datetime import datetime

PRIV = os.path.expanduser("~/Developer/transparentniprstice-private")
WEB  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINM = os.path.join(PRIV, "zdroje", "prstice-finm-2019-2025.csv")
PARAG= os.path.join(PRIV, "zdroje", "CIS_PARAGRAF.CSV")
POLOZ= os.path.join(PRIV, "zdroje", "nazvy-polozek.json")
ROKY = list(range(2019, 2026))
KONTROLA = {  # výdaje / příjmy podle data/rozpocet.json
    2025: (22484603.25, 28380970.77),
}

# oblast: (název, [paragrafy], barva, popis)
OBLASTI = [
 ("Chod úřadu a zastupitelstvo", ["6171","6112","6399","6310","6402","6320","6114","6115","6117","6118","6409"], "#0a84ff",
  "Provoz obecního úřadu, odměny zastupitelů, finanční operace a volby."),
 ("Zámek a památky", ["3322","3329"], "#5e5ce6",
  "Obnova a údržba kulturních památek — v Pršticích především budova zámku."),
 ("Voda a kanalizace", ["2321","2310"], "#0f9fbd",
  "Odvádění a čištění odpadních vod, pitná voda."),
 ("Škola a děti", ["3113","3111","3118","3421","3429"], "#f5a524",
  "Základní škola, mateřská škola, volný čas dětí a mládeže."),
 ("Zeleň a veřejná prostranství", ["3745","3631","3632","3639","2341","3635"], "#1a9e4b",
  "Péče o vzhled obce, veřejné osvětlení, pohřebnictví, vodní plochy, územní plánování."),
 ("Odpady", ["3722","3725","3721","3726"], "#a2845e",
  "Svoz a zpracování komunálního i nebezpečného odpadu."),
 ("Doprava a pošta", ["2411","2219","2292","2212","2221"], "#e63562",
  "Pošta, místní komunikace, dopravní obslužnost."),
 ("Vnitřní převody", ["6330"], "#8e8e93",
  "Přesun peněz mezi účty obce — není to výdaj navenek."),
 ("Hasiči", ["5512","5213"], "#ff6b35",
  "Dobrovolná požární ochrana a krizová opatření."),
 ("Kultura, knihovna a ostatní", ["3314","3349","3399","3341","3319","4359","1039","3900","2141"], "#af52de",
  "Knihovna, zpravodaj, sociální služby, lesy a další drobné agendy."),
]


def nazvy_paragrafu():
    m = {}
    with open(PARAG, encoding="utf-8", errors="replace") as f:
        r = csv.reader(f, delimiter=";"); next(r, None)
        for row in r:
            if len(row) >= 7:
                c = row[0].strip().strip('"')
                if len(c) == 4 and c.isdigit():
                    m[c] = row[6].strip().strip('"')
    return m


# Opravy názvů, které číselník MONITORu vrací v zastaralém znění.
# Zdroj správných názvů: vyhláška č. 412/2021 Sb., o rozpočtové skladbě.
OPRAVY_NAZVU = {
    # od 1. 1. 2022 nahradila položky 1337 a 1340; MONITOR vrací starý název
    # „Poplatek z ubytovací kapacity", což je věcně jiný poplatek
    "1345": "Poplatek za obecní systém odpadového hospodářství",
    # do roku 2021 se odpadový poplatek účtoval na 1340, pak ho nahradila 1345
    "1340": "Poplatek za provoz systému shromažďování a odstraňování odpadů",
    "1346": "Poplatek za povolení k vjezdu do vybraných míst",
    "1382": "Odvod z loterií a podobných her (doběh)",
    "5345": "Převody vlastním rozpočtovým účtům (vnitřní převod)",
    "4134": "Převody z rozpočtových účtů (vnitřní převod)",
    "4139": "Ostatní převody z vlastních fondů (vnitřní převod)",
}


def nazvy_polozek():
    """Názvy druhů výdajů a příjmů. Preferuje krátkou poznámku z MONITORu,
    u položek v OPRAVY_NAZVU použije ověřené znění dle vyhlášky 412/2021 Sb."""
    if not os.path.exists(POLOZ):
        sys.exit(f"CHYBA: chybí {POLOZ} (názvy položek z API MONITORu)")
    raw = json.load(open(POLOZ, encoding="utf-8"))
    m = {k: (v.get("short") or v.get("name")) for k, v in raw.items()}
    m.update(OPRAVY_NAZVU)
    return m


# Skupiny příjmů: (název, funkce výběru položky, barva, popis)
PRIJMY_SKUPINY = [
 ("Daně přerozdělené státem", lambda p: p in {"1111","1112","1113","1121","1122","1219","1211"}, "#0a84ff",
  "DPH a daně z příjmů. Vybírá je stát a přerozděluje obcím podle zákona — obec jejich výši neovlivní."),
 ("Příjmy z vlastní činnosti a majetku", lambda p: p.startswith("2"), "#1a9e4b",
  "Poplatky za služby obce, nájmy, úroky z vkladů, pojistné náhrady."),
 ("Dotace a transfery", lambda p: p.startswith("4") and p not in {"4134","4139"}, "#5e5ce6",
  "Peníze ze státního rozpočtu nebo kraje, často na konkrétní účel."),
 ("Daň z nemovitých věcí", lambda p: p == "1511", "#f5a524",
  "Daň z pozemků a staveb v obci. Její výši může obec ovlivnit koeficientem."),
 ("Místní poplatky a daně z hazardu", lambda p: p.startswith("13"), "#e63562",
  "Poplatek za odpad, ze psů, správní poplatky a podíl na daních z hazardních her."),
 ("Vnitřní převody", lambda p: p in {"4134","4139"}, "#8e8e93",
  "Přesun peněz mezi účty obce — nejde o nový příjem zvenčí."),
 ("Prodej majetku", lambda p: p.startswith("3"), "#af52de",
  "Jednorázové příjmy z prodeje obecního majetku."),
]


def prijmy(data_p, npol):
    """Sestaví příjmy do skupin (dvě úrovně: skupina → položka)."""
    out, prirazene = [], set()
    for nazev, test, barva, popis in PRIJMY_SKUPINY:
        pol = sorted(({"kod": k, "nazev": npol.get(k, f"(položka {k})"), "kc": round(v, 2)}
                      for k, v in data_p.items() if test(k) and v != 0),
                     key=lambda x: -x["kc"])
        for x in pol:
            prirazene.add(x["kod"])
        if not pol:
            continue
        out.append({"skupina": nazev, "barva": barva, "popis": popis,
                    "kc": round(sum(x["kc"] for x in pol), 2), "polozky": pol})
    chybi = sorted(k for k, v in data_p.items() if v != 0 and k not in prirazene)
    if chybi:
        sys.exit(f"CHYBA: příjmové položky mimo skupiny: {chybi}")
    out.sort(key=lambda x: -x["kc"])
    return out


def nacti_finm():
    """rok -> ('v': paragraf -> položka -> Kč, 'p': položka -> Kč)"""
    d = {r: {"v": {}, "p": {}} for r in ROKY}
    with open(FINM, encoding="utf-8", errors="replace") as f:
        f.readline()
        for line in f:
            c = line.rstrip("\n").split(";")
            if len(c) < 13:
                continue
            try:
                rok, v = int(c[2][:4]), float(c[12])
            except ValueError:
                continue
            if rok not in d or v == 0:
                continue
            if c[1] == "000100":
                k = c[9].strip()
                d[rok]["p"][k] = d[rok]["p"].get(k, 0.0) + v
            elif c[1] == "000200":
                pg, pol = c[8].strip(), c[9].strip()
                d[rok]["v"].setdefault(pg, {})
                d[rok]["v"][pg][pol] = d[rok]["v"][pg].get(pol, 0.0) + v
    return d


def vydaje_rok(data, npar, npol):
    """Výdaje jednoho roku do oblastí (tři úrovně)."""
    prirazene, out = set(), []
    for nazev, pars, barva, popis in OBLASTI:
        agendy = []
        for pg in pars:
            if pg not in data:
                continue
            prirazene.add(pg)
            polozky = sorted(({"kod": k, "nazev": npol.get(k, f"(položka {k})"), "kc": round(v, 2)}
                              for k, v in data[pg].items() if v != 0), key=lambda x: -x["kc"])
            s = round(sum(x["kc"] for x in polozky), 2)
            if s == 0:
                continue
            kap = round(sum(x["kc"] for x in polozky if x["kod"].startswith("6")), 2)
            agendy.append({"par": pg, "nazev": npar.get(pg, f"(paragraf {pg})"),
                           "kc": s, "kapitalove_kc": kap, "polozky": polozky})
        if not agendy:
            continue
        agendy.sort(key=lambda x: -x["kc"])
        out.append({"oblast": nazev, "barva": barva, "popis": popis,
                    "kc": round(sum(a["kc"] for a in agendy), 2),
                    "kapitalove_kc": round(sum(a["kapitalove_kc"] for a in agendy), 2),
                    "agendy": agendy})
    chybi = sorted(set(data) - prirazene)
    if chybi:
        sys.exit(f"CHYBA: paragrafy mimo oblasti: {chybi} — doplň je do OBLASTI.")
    out.sort(key=lambda x: -x["kc"])
    return out


def main():
    for p in (FINM, PARAG):
        if not os.path.exists(p):
            sys.exit(f"CHYBA: chybí zdroj {p}")
    npar, npol = nazvy_paragrafu(), nazvy_polozek()
    finm = nacti_finm()

    # kontrolní součty z už ověřeného data/rozpocet.json
    roz = json.load(open(os.path.join(WEB, "data", "rozpocet.json"), encoding="utf-8"))["roky"]

    vyd_roky, pri_roky = {}, {}
    print(f"Rozpad rozpočtu {ROKY[0]}–{ROKY[-1]}:")
    for r in ROKY:
        ob = vydaje_rok(finm[r]["v"], npar, npol)
        pr = prijmy(finm[r]["p"], npol)
        v_cel = round(sum(o["kc"] for o in ob), 2)
        p_cel = round(sum(s["kc"] for s in pr), 2)

        # tvrdé kontroly proti rozpocet.json
        ocek_v = roz[str(r)]["vydaje_celkem_kc"]
        ocek_p = roz[str(r)]["prijmy_celkem_kc"]
        if abs(v_cel - ocek_v) > 0.05:
            sys.exit(f"CHYBA {r}: výdaje {v_cel} ≠ rozpocet.json {ocek_v}")
        if abs(p_cel - ocek_p) > 0.05:
            sys.exit(f"CHYBA {r}: příjmy {p_cel} ≠ rozpocet.json {ocek_p}")
        if r in KONTROLA:
            kv, kp = KONTROLA[r]
            if abs(v_cel - kv) > 0.05 or abs(p_cel - kp) > 0.05:
                sys.exit(f"CHYBA {r}: neshoda s pevnou kontrolou")

        vyd_roky[str(r)] = {"celkem_kc": v_cel, "oblasti": ob}
        pri_roky[str(r)] = {"celkem_kc": p_cel, "skupiny": pr}
        print(f"  {r}: výdaje {v_cel:>13,.0f} ({len(ob)} oblastí) | příjmy {p_cel:>13,.0f} ({len(pr)} skupin)  ✓".replace(",", " "))

    spolecne = {
        "basis": "cash_budget", "jednotka": "Kč", "roky": ROKY,
        "zdroj": "MONITOR (MF ČR), výkaz FIN 2-12 M, skutečnost k 31.12.",
        "vygenerovano": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    json.dump({"meta": dict(spolecne, poznamka=(
        "Tři úrovně: oblast (zařazeno autorem) → agenda = paragraf → položka = druh výdaje. "
        "Součet oblastí se v každém roce rovná celkovým výdajům.")), "roky": vyd_roky},
        open(os.path.join(WEB, "data", "vydaje-skupiny.json"), "w", encoding="utf-8"),
        ensure_ascii=False, indent=1)
    json.dump({"meta": dict(spolecne, poznamka=(
        "Dvě úrovně: skupina (zařazeno autorem) → položka rozpočtové skladby. "
        "Vnitřní převody (4134, 4139) jsou vedeny zvlášť — nejde o příjem zvenčí.")), "roky": pri_roky},
        open(os.path.join(WEB, "data", "prijmy-skupiny.json"), "w", encoding="utf-8"),
        ensure_ascii=False, indent=1)
    print("HOTOVO — data/vydaje-skupiny.json + data/prijmy-skupiny.json (kontroly PASS)")


if __name__ == "__main__":
    main()
