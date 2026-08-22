#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrakce a veřejný export deníku 518 za 1–6/2026 — (PLAN.md úkol 1.3)

Vstup:  PDF „Opis deníku" 518 za období 1/2026–6/2026 (OUPR-1007/2026) v PACTu.
Výstup:
  - soukromý extrakt (všechna pole)              -> soukromá zóna / extrakty/
  - veřejný export s period_status: incomplete   -> web repo / data/
  - soukromý report                              -> soukromá zóna / qa-reporty/

Zásady (shodné s úkolem 1.1):
  * Neúplné období „leden–červen 2026" — NEPRODLUŽUJE hlavní řadu uzavřených let
    a nesrovnává se s celým rokem 2025.
  * Anonymizace se přebírá z extrakce_518.py (stejná pravidla).
  * Zdroj nemá kategorie — přiřazují se pravidly podle popisu (k revizi Petrem).

Spuštění: python3 skripty/extrakce_518_2026.py
"""
import os, re, sys, json, hashlib
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extrakce_518 import detekuj, strojove_ocisteni, PLACEHOLDER, DRZET, nacti_schvalene_popisy

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("CHYBA: chybí PyMuPDF (fitz). Nainstaluj: pip install pymupdf")

PACT_ROOT    = os.path.expanduser("~/Documents/AI/0_PACT")
PRIVATE_ZONE = os.path.expanduser("~/Developer/transparentniprstice-private")
WEB_ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ZDROJ = os.path.join(
    PACT_ROOT,
    "0_Projects/4_PRŠTICE/2026_08_03 Prštice detail účtu 518 za rok 2026/"
    "priloha_1743030179_1_Novotny_;518;_1.1.2026-30.6.2026_dle_106.pdf",
)
KONTROLNI_SOUCET = 2707114.51   # z řádku CELKEM v PDF

DOK = re.compile(r'^(\d{2}-\d{3}-\d{5})\s+(\d+)/2026\s+(\d{2}\.\d{2}\.\d{4})')
AMT = re.compile(r'^(-?[\d  ]+,\d{2})\s*(.*)$')

# Pravidla kategorizace (podle popisu; ordered, první shoda vyhrává).
# Vychází z kategorií a vzorů deníku 2022–2025. Kategorie NEJSOU osobní údaj.
PRAVIDLA = [
    (['banka', 'bankovní popl'], 'Bankovní poplatky'),
    (['gdpr', 'pověřenec'], 'GDPR / pověřenec'),
    (['právní', 'právné', 'advokát'], 'Právní služby'),
    (['poštov'], 'Poštovné'),
    (['geometr', 'znalec', 'katastr', 'vklad do', 'geodet'], 'Geometr./znalecké/KN'),
    (['kopírov', 'tisk', 'toner'], 'Kopírování / tisk'),
    (['licence', 'm365', 'mapový portál', 'dálkový přístup', 'zoner',
      'software', 'internet', 'telefon', 'webov', 'doména', 'office365'], 'Telekomunikace / IT'),
    (['čov', 'odpadní vod', 'čištění odpad', 'převzat'], 'ČOV / odpadní vody'),
    (['odpad', 'svoz', 'popelnic', 'kontejner'], 'Odpady (svoz)'),
    (['voda', 'kanaliz', 'přípojk', 'vodoměr', 'vodovod'], 'Voda/kanalizace (provoz)'),
    (['zeleň', 'altán', 'seč', 'kácen', 'strom', 'park'], 'Veřejná zeleň'),
    (['zámek'], 'Zámek (budova)'),
    (['oprava dokladu', 'storno'], 'Opravy/storna dokladů'),
    (['čin.míst.spr', 'správ', 'ověřovací', 'daňové přiznání', 'tech.pomoc'], 'Správa / odborné služby'),
]


def kategorizuj(p):
    pl = p.lower()
    for kw, kat in PRAVIDLA:
        if any(k in pl for k in kw):
            return kat
    return 'Ostatní'


def parse_pdf():
    doc = fitz.open(ZDROJ)
    kept = []
    for pg in range(doc.page_count):
        L = [l.strip() for l in doc[pg].get_text().split('\n')]
        start = next((i for i, l in enumerate(L) if DOK.match(l)), None)
        if start is None:
            continue
        end = next((i for i, l in enumerate(L) if l.startswith('Zpracováno') or l.startswith('CELKEM')), len(L))
        kept += [l for l in L[start:end] if l]
    di = [i for i, l in enumerate(kept) if DOK.match(l)] + [len(kept)]
    ent = []
    for k in range(len(di) - 1):
        i = di[k]; m = DOK.match(kept[i])
        vals, descs = [], []
        for b in kept[i + 1:di[k + 1]]:
            if b.startswith('518'):
                continue
            am = AMT.match(b)
            if am:
                vals.append(float(am.group(1).replace(' ', '').replace(' ', '').replace(',', '.')))
                if am.group(2).strip():
                    descs.append(am.group(2).strip())
            else:
                descs.append(b)
        madati = vals[0] if vals else 0.0
        dal = vals[1] if len(vals) > 1 else 0.0
        ent.append({
            'doc': m.group(1), 'dt': m.group(3), 'mesic': int(m.group(2)),
            'net': round(madati - dal, 2), 'p': ' '.join(descs).strip(),
        })
    return ent


def main():
    if not os.path.exists(ZDROJ):
        sys.exit(f"CHYBA: zdroj (PDF) nenalezen:\n  {ZDROJ}")
    entries = parse_pdf()
    soucet = round(sum(e['net'] for e in entries), 2)
    if abs(soucet - KONTROLNI_SOUCET) > 0.01:
        sys.exit(f"CHYBA: součet {soucet} ≠ kontrolní {KONTROLNI_SOUCET} — parser PDF selhal.")

    allowlist = nacti_schvalene_popisy()
    privatni, verejne, flagged = [], [], {}
    for e in entries:
        p = e['p']
        haleru = round(e['net'] * 100)
        idz = hashlib.sha256(e['doc'].encode('utf-8')).hexdigest()[:12]
        kat = kategorizuj(p)
        nalezy = detekuj(p)
        if nalezy:
            flagged.setdefault(p, set()).update(nalezy)
        privatni.append({
            "id_zdroje": idz, "ucetni_rok": 2026, "mesic": e['mesic'], "datum_dokladu": e['dt'],
            "cislo_dokladu": e['doc'], "castka_kc": e['net'], "castka_haleru": haleru,
            "kategorie": kat, "popis_puvodni": p, "pii": nalezy,
        })
        if not nalezy:
            popis_verejny = p
        elif set(nalezy) & DRZET:
            popis_verejny = allowlist.get(p, PLACEHOLDER)
        else:
            popis_verejny = allowlist.get(p, strojove_ocisteni(p))
        verejne.append({
            "id_zdroje": idz, "ucetni_rok": 2026, "mesic": e['mesic'],
            "castka_haleru": haleru, "kategorie": kat,
            "popis_verejny": popis_verejny, "baze": "accrual_cost",
        })

    # zápis
    for d in (os.path.join(PRIVATE_ZONE, "extrakty"), os.path.join(PRIVATE_ZONE, "qa-reporty"),
              os.path.join(WEB_ROOT, "data")):
        os.makedirs(d, exist_ok=True)
    with open(os.path.join(PRIVATE_ZONE, "extrakty", "ucet-518-2026H1-privatni.json"), 'w', encoding='utf-8') as f:
        json.dump(privatni, f, ensure_ascii=False, indent=1)

    pub = {
        "meta": {
            "obdobi": "leden–červen 2026",
            "period_status": "incomplete",
            "poznamka": "Neúplné období. Neprodlužuje řadu uzavřených let 2015–2025 "
                        "a nesrovnává se s celým rokem. Kategorie přiřazeny pravidly podle popisu.",
            "zdroj": "Opis deníku 518, období 1–6/2026 (OUPR-1007/2026)",
            "baze": "accrual_cost", "jednotka_castky": "haléře",
            "celkem_kc": soucet,
            "vygenerovano": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "polozky": verejne,
    }
    pub_path = os.path.join(WEB_ROOT, "data", "ucet-518-2026H1-public.json")
    with open(pub_path, 'w', encoding='utf-8') as f:
        json.dump(pub, f, ensure_ascii=False, indent=1)

    # souhrny
    mz, kz = {}, {}
    for v in verejne:
        mz[v['mesic']] = mz.get(v['mesic'], 0) + v['castka_haleru']
        kz[v['kategorie']] = kz.get(v['kategorie'], 0) + v['castka_haleru']
    drzeno = sum(1 for v in verejne if v['popis_verejny'] == PLACEHOLDER)

    rep = [f"# Report deníku 518 za 1–6/2026 — úkol 1.3 (SOUKROMÉ)\n",
           f"Vygenerováno: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
           "## Souhrn\n",
           f"- Zápisů: **{len(entries)}** | součet **{soucet:,.2f} Kč** (= kontrolní CELKEM)".replace(",", " "),
           f"- Popisů s PII: **{len(flagged)}** | podrženo řádků: **{drzeno}**\n",
           "## Po měsících (Kč)\n", "| Měsíc | Kč |", "|---:|---:|"]
    for m in sorted(mz):
        rep.append(f"| {m}/2026 | {mz[m]/100:,.2f} |".replace(",", " "))
    rep += ["\n## Po kategoriích (Kč) — K REVIZI (kategorie přiřazeny pravidly)\n", "| Kategorie | Kč |", "|---:|---:|"]
    for k in sorted(kz, key=lambda x: -kz[x]):
        rep.append(f"| {k} | {kz[k]/100:,.2f} |".replace(",", " "))
    rep += ["\n## Popisy PODRŽENÉ k rozhodnutí (osobní údaj)\n", "| Původní popis | Nález | Strojový návrh |", "|---|---|---|"]
    for p in sorted(flagged):
        rep.append(f"| {p} | {', '.join(sorted(flagged[p]))} | {strojove_ocisteni(p)} |")
    with open(os.path.join(PRIVATE_ZONE, "qa-reporty", "report-518-2026H1.md"), 'w', encoding='utf-8') as f:
        f.write("\n".join(rep))

    print("HOTOVO — deník 518 za 1–6/2026 (úkol 1.3)")
    print(f"  zápisů: {len(entries)} | součet: {soucet:,.2f} Kč = kontrolní CELKEM ✓".replace(",", " "))
    print(f"  popisů s PII: {len(flagged)} | podrženo řádků: {drzeno}")
    print(f"  veřejný export: {pub_path}  (period_status: incomplete)")
    print("  po měsících:", ", ".join(f"{m}={mz[m]/100:,.0f}".replace(",", " ") for m in sorted(mz)))


if __name__ == "__main__":
    main()
