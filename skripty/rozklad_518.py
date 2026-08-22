#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oprava kategorií, párování storen a rozklad změn účtu 518 — (PLAN.md úkol 1.7)

Vstup:
  - soukromý extrakt deníku 518 (soukromá zóna / extrakty/)
  - verzovaná pravidla oprav (soukromá zóna / kategorie-opravy.yml)
Výstup:
  - data/ucet-518-rozklad.json — kategorie po letech + rozklad meziročních změn
    2022→2023, 2023→2024, 2024→2025 + vybraná témata (jeřáb, střecha zámku, ZŠ).

Zásady:
  * Rozklad odpovídá na „co vytvořilo meziroční rozdíl", ne „proč obec objednala".
  * Opravy kategorií jsou verzované a schvaluje je Petr.
  * Storna se párují ke kategorii původního dokladu (je-li v datech).
  * Skript ověří výstup proti kontrolním hodnotám z plánu; při rozporu skončí chybou.
  * Výstup obsahuje jen názvy kategorií a částky — žádné osobní údaje.

Spuštění: python3 skripty/rozklad_518.py
"""
import os, re, json, sys
from datetime import datetime

PRIVATE_ZONE = os.path.expanduser("~/Developer/transparentniprstice-private")
WEB_ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRAKT      = os.path.join(PRIVATE_ZONE, "extrakty", "ucet-518-privatni.json")
OPRAVY_YML   = os.path.join(PRIVATE_ZONE, "kategorie-opravy.yml")

ROKY = [2022, 2023, 2024, 2025]
PARY = [(2022, 2023), (2023, 2024), (2024, 2025)]


def nacti_opravy():
    """Minimální parser kategorie-opravy.yml (bez PyYAML): mapa doklad->na
    a příznak storno_parovani."""
    opravy, storno, cur, in_opravy = {}, False, None, False
    if not os.path.exists(OPRAVY_YML):
        return opravy, storno
    for line in open(OPRAVY_YML, encoding='utf-8'):
        s = line.strip()
        if s.startswith('#'):
            continue
        if s.startswith('opravy:'):    in_opravy = True;  continue
        if s.startswith('kandidati:'): in_opravy = False; continue
        if s.startswith('storno_parovani:'):
            storno = 'true' in s.lower(); in_opravy = False; continue
        m = re.match(r'-?\s*doklad:\s*"(.*)"', s)
        if m and in_opravy: cur = m.group(1); continue
        m = re.match(r'na:\s*"(.*)"', s)
        if m and cur and in_opravy: opravy[cur] = m.group(1); cur = None
    return opravy, storno


def main():
    if not os.path.exists(EXTRAKT):
        sys.exit(f"CHYBA: chybí soukromý extrakt {EXTRAKT}\n  Spusť nejdřív skripty/extrakce_518.py")
    data = json.load(open(EXTRAKT, encoding='utf-8'))
    opravy, storno_parovani = nacti_opravy()

    by_doc = {}
    for d in data:
        by_doc.setdefault(d['cislo_dokladu'], []).append(d)

    def kat_zaklad(d):
        return opravy.get(d['cislo_dokladu'], d['kategorie'])

    def kat_final(d):
        k = kat_zaklad(d)
        if k == 'Opravy/storna dokladů' and storno_parovani:
            m = re.search(r'(\d{2}-\d{3}-\d{5})', d['popis_puvodni'])
            if m and m.group(1) in by_doc:
                return kat_zaklad(by_doc[m.group(1)][0])
            return 'Storna (nepárované)'
        return k

    # matice kategorie × rok (haléře → přesné součty)
    cats = sorted({kat_final(d) for d in data})
    mat = {c: {r: 0 for r in ROKY} for c in cats}
    for d in data:
        mat[kat_final(d)][d['ucetni_rok']] += d['castka_haleru']

    def kc(hal): return round(hal / 100, 2)

    # rozklad meziročních změn
    rozklad = {}
    for a, b in PARY:
        total = sum(mat[c][b] - mat[c][a] for c in cats)
        prisp = []
        for c in cats:
            dl = mat[c][b] - mat[c][a]
            if dl == 0:
                continue
            prisp.append({
                "kategorie": c,
                "zmena_kc": kc(dl),
                "podil_pct": round(dl / total * 100, 1) if total else 0.0,
                "nad_5pct": abs(dl) >= 0.05 * abs(total),
            })
        prisp.sort(key=lambda x: -abs(x["zmena_kc"]))
        rozklad[f"{a}_{b}"] = {"celkem_kc": kc(total), "prispevky": prisp}

    # cross-cutting témata (z popisů, jen agregáty do výstupu)
    def theme_sum(rok, kat, keep, drop=()):
        s = 0
        for d in data:
            if d['ucetni_rok'] == rok and kat_final(d) == kat:
                pl = d['popis_puvodni'].lower()
                if any(k in pl for k in keep) and not any(x in pl for x in drop):
                    s += d['castka_haleru']
        return s

    jerab = {}
    for d in data:
        if 'jeřáb' in d['popis_puvodni'].lower():
            jerab[d['ucetni_rok']] = jerab.get(d['ucetni_rok'], 0) + d['castka_haleru']
    strecha_atika_2023 = theme_sum(2023, 'Zámek (budova)', ('střech', 'atik'), drop=('povolení',))
    zs_sondy_2025 = theme_sum(2025, 'Ostatní', ('sond',))

    pravni_total = sum(mat['Právní služby'][r] for r in ROKY)
    gdpr_2025 = mat.get('GDPR / pověřenec', {}).get(2025, 0)

    out = {
        "meta": {
            "zdroj": "Účetní deník účtu 518 obce Prštice (accrual_cost), 2022–2025",
            "jednotka": "Kč",
            "baze": "accrual_cost",
            "poznamka": "Rozklad ukazuje, které skupiny nákladů tvoří meziroční rozdíl. "
                        "Není tvrzením o důvodu objednávky. Běžné ceny, bez inflace.",
            "pravidla_oprav": "verzovaná privátní pravidla (kategorie-opravy.yml); storna párována k původnímu dokladu",
            "vygenerovano": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "kategorie_po_letech_kc": {c: {str(r): kc(mat[c][r]) for r in ROKY} for c in cats},
        "rozklad": rozklad,
        "temata": {
            "jerab_kc": {str(r): kc(jerab[r]) for r in sorted(jerab)},
            "jerab_zmena_2022_2023_kc": kc(jerab.get(2023, 0) - jerab.get(2022, 0)),
            "zamek_strecha_atika_2023_kc": kc(strecha_atika_2023),
            "zs_sondy_podlah_2025_kc": kc(zs_sondy_2025),
        },
        "souhrn": {
            "pravni_sluzby_2022_2025_kc": kc(pravni_total),
            "gdpr_2025_kc": kc(gdpr_2025),
        },
    }

    os.makedirs(os.path.join(WEB_ROOT, "data"), exist_ok=True)
    out_path = os.path.join(WEB_ROOT, "data", "ucet-518-rozklad.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    # ---- kontroly proti plánu ----
    def d23(cat): return kc(mat[cat][2023] - mat[cat][2022])
    def d25(cat): return kc(mat[cat][2025] - mat[cat][2024])
    tvrde = [
        ("celkem 2022→2023 = 2 909 622,84", rozklad["2022_2023"]["celkem_kc"], 2909622.84, 0.05),
        ("celkem 2024→2025 = 1 221 138,32", rozklad["2024_2025"]["celkem_kc"], 1221138.32, 0.05),
        ("zámek 2022→2023 = 648 072,21",    d23('Zámek (budova)'), 648072.21, 0.05),
        ("odpady 2022→2023 = 447 236,17",   d23('Odpady (svoz)'), 447236.17, 0.05),
        ("právní 2022→2023 = 290 980,00",   d23('Právní služby'), 290980.00, 0.05),
        ("právní služby 2022–2025 = 2 094 182", kc(pravni_total), 2094182.00, 0.05),
        ("GDPR 2025 = 272 250",             kc(gdpr_2025), 272250.00, 0.05),
        ("GDPR+právní 2024→2025 = 288 060", round(d25('GDPR / pověřenec') + d25('Právní služby'), 2), 288060.00, 0.05),
        ("jeřáb 2022→2023 = −56 773,20",    kc(jerab.get(2023,0)-jerab.get(2022,0)), -56773.20, 0.05),
        ("střecha+atika zámku 2023 = 788 099,85", kc(strecha_atika_2023), 788099.85, 0.05),
        ("sondy podlah ZŠ 2025 = 117 333,70", kc(zs_sondy_2025), 117333.70, 0.05),
    ]
    mekke = [
        ("ČOV 2022→2023 ≈ 1 378 428,21", d23('ČOV / odpadní vody'), 1378428.21, 300.0),
        ("zámek 2024→2025 ≈ 593 167,45 (párování storna −3 460)", d25('Zámek (budova)'), 593167.45, 4000.0),
    ]

    print("HOTOVO — rozklad změn účtu 518 (úkol 1.7)")
    print(f"  oprav kategorií: {len(opravy)} | storno pairing: {storno_parovani}")
    print(f"  výstup: {out_path}")
    print("  Tvrdé kontroly (musí sedět):")
    ok = True
    for popis, mam, ctrl, tol in tvrde:
        good = abs(mam - ctrl) <= tol
        ok = ok and good
        print(f"    [{'PASS' if good else 'FAIL'}] {popis}  (mám {mam:,.2f})".replace(",", " "))
    print("  Měkké kontroly (předběžná hodnota z plánu, tolerováno):")
    for popis, mam, ctrl, tol in mekke:
        good = abs(mam - ctrl) <= tol
        print(f"    [{'OK' if good else '≠'}] {popis}  (mám {mam:,.2f}, rozdíl {mam-ctrl:+,.2f})".replace(",", " "))
    if not ok:
        sys.exit("CHYBA: tvrdá kontrola NEPROŠLA.")
    print("  Všechny tvrdé kontroly PASS ✓")


if __name__ == "__main__":
    main()
