#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrakce a veřejný export účtu 518 — Transparentní Prštice (PLAN.md úkol 1.1)

Vstup:  originál Detail_uctu_518_Prstice.html (v PACTu, mimo web repo)
Výstup:
  - soukromý extrakt (všechna původní pole)          -> soukromá zóna / extrakty/
  - veřejné deriváty JSON + CSV (schéma z úkolu 1.0)  -> web repo / data/
  - soukromý report odstranění a kandidátů           -> soukromá zóna / qa-reporty/

Zásady (ZADANI P-8, P-8a; anonymizace/pravidla.yml):
  * Nic z původního volného popisu (p) se nezveřejní přímo.
  * Strukturované osobní údaje (adresa čp./če., e-mail, telefon, účet, RČ)
    se odstraní automaticky.
  * Popis s MOŽNÝM jménem se PODRŽÍ ke kontrole (placeholder), nikdy se
    nezveřejní automaticky — o čistém veřejném popisu rozhoduje Petr přes
    anonymizace/verejna-allowlist.yml.
  * Skript je deterministický; při změně zdroje selže kontrola SHA-256.

Spuštění:  python3 skripty/extrakce_518.py
"""
import os, re, json, csv, sys, hashlib
from datetime import datetime

PACT_ROOT    = os.path.expanduser("~/Documents/AI/0_PACT")
PRIVATE_ZONE = os.path.expanduser("~/Developer/transparentniprstice-private")
WEB_ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ZDROJ = os.path.join(
    PACT_ROOT,
    "0_Projects/4_PRŠTICE/2026_06_22 Analýza účtu 518/Detail_uctu_518_Prstice.html",
)
ZDROJ_SHA256 = "907c98e54737add0169cbf38663b92e4f4b660b21f5fb4d71fda4fb7fe515dff"

PLACEHOLDER = "(popis se doplňuje po kontrole)"

# --- Detekce osobních údajů (zrcadlí anonymizace/pravidla.yml sekci detekce_pii) ---
RE_ADRESA = re.compile(r'č\.?\s?[pe]\.?\s?\d+[a-z]?', re.I)          # čp./če. + číslo (adresa nemovitosti)
RE_EMAIL  = re.compile(r'[\w.+-]+@[\w.-]+\.\w{2,}')
RE_TEL    = re.compile(r'(?<!\d)(?:\+?420)?\s?\d{3}\s?\d{3}\s?\d{3}(?!\d)')
RE_UCET   = re.compile(r'\b\d{1,6}-?\d{2,10}/\d{4}\b')
RE_RC     = re.compile(r'\b\d{6}/\d{3,4}\b')
RE_DOKLAD = re.compile(r'\b\d{2}-\d{3}-\d{5}\b')                     # interní číslo dokladu, formát RR-NNN-NNNNN
# Možné jméno: dvě slova s velkým počátečním písmenem (může jít i o značku auta
# → proto jen KANDIDÁT k ruční kontrole, nikdy se neodstraní automaticky).
_TW = r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]{2,}'
RE_JMENO = re.compile(_TW + r'\s+' + _TW)
# Iniciála + příjmení: "X.Novák", "J. Svoboda" (i bez mezery, i za pomlčkou).
RE_INICIALA = re.compile(r'\b[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ]\.\s?' + _TW)

# Nálezy, které PODRŽÍ popis ke kontrole (možný soukromý jedinec).
# Ostatní nálezy (číslo dokladu, e-mail, telefon, účet, RČ) se očistí automaticky.
DRZET = {'adresa_cp_ce', 'mozne_jmeno'}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def detekuj(p):
    """Seznam typů PII nalezených v původním popisu."""
    n = []
    if RE_ADRESA.search(p): n.append('adresa_cp_ce')
    if RE_DOKLAD.search(p): n.append('cislo_dokladu')
    if RE_EMAIL.search(p):  n.append('email')
    if RE_TEL.search(p):    n.append('telefon')
    if RE_UCET.search(p):   n.append('ucet')
    if RE_RC.search(p):     n.append('rodne_cislo')
    if RE_JMENO.search(p) or RE_INICIALA.search(p): n.append('mozne_jmeno')
    return n


def strojove_ocisteni(p):
    """Odstraní STRUKTUROVANÉ PII (číslo dokladu, adresa, e-mail, telefon, účet,
    RČ). Jména nechává být (mohou být značky) — u popisů s možným jménem je
    proto výsledek jen NÁVRH k Petrově kontrole."""
    s = p
    s = RE_DOKLAD.sub('', s)
    s = RE_ADRESA.sub('', s)
    s = RE_EMAIL.sub('', s)
    s = RE_TEL.sub('', s)
    s = RE_UCET.sub('', s)
    s = RE_RC.sub('', s)
    s = RE_INICIALA.sub('', s)                           # iniciála+příjmení (nízké riziko záměny)
    s = re.sub(r'\bul\.\b', '', s)                       # zbytek "ul." po odstranění adresy
    s = re.sub(r'\b(číslo|č\.)\s*$', '', s.strip(), flags=re.I)  # visící "číslo" po odstranění dokladu
    s = re.sub(r'[-–]\s*[-–]', '-', s)                   # dvojité pomlčky
    s = re.sub(r'\s{2,}', ' ', s).strip(' -–.,')
    return s or "(bez popisu)"


def nacti_schvalene_popisy():
    """Načte schválené čisté popisy z PRIVÁTNÍ mapy popisy-schvalene.yml.
    Klíče jsou původní popisy = osobní údaj, proto mapa leží v soukromé zóně
    a NIKDY se necommituje. Bez PyYAML — jednoduchý parser dvojic
    `- puvodni: "..." / verejny: "..."`. Dokud soubor neexistuje, vrací {}."""
    path = os.path.join(PRIVATE_ZONE, "popisy-schvalene.yml")
    mapa = {}
    if not os.path.exists(path):
        return mapa
    puvodni = None
    for line in open(path, encoding='utf-8'):
        s = line.strip()
        if s.startswith('#'):
            continue
        m = re.match(r'-?\s*puvodni:\s*"(.*)"\s*$', s)
        if m:
            puvodni = m.group(1); continue
        m = re.match(r'verejny:\s*"(.*)"\s*$', s)
        if m and puvodni is not None:
            mapa[puvodni] = m.group(1); puvodni = None
    return mapa


def main():
    # 1) Ověření zdroje proti manifestu
    if not os.path.exists(ZDROJ):
        sys.exit(f"CHYBA: zdroj nenalezen:\n  {ZDROJ}")
    h = sha256_file(ZDROJ)
    if h != ZDROJ_SHA256:
        sys.exit("CHYBA: SHA-256 zdroje nesouhlasí s manifestem — zdroj se změnil!\n"
                 f"  čekáno:   {ZDROJ_SHA256}\n  zjištěno: {h}")

    html = open(ZDROJ, encoding='utf-8').read()
    m = re.search(r'const DATA = (\[.*?\]);', html, re.S)
    if not m:
        sys.exit("CHYBA: ve zdroji nenalezeno pole `const DATA = [...]`.")
    data = json.loads(m.group(1))

    allowlist = nacti_schvalene_popisy()

    privatni, verejne = [], []
    flagged = {}   # puvodni_popis -> set(typů PII)

    for row in data:
        y   = int(row['y'])
        dt  = row['dt']                    # DD.MM.RRRR
        doc = row['doc']
        net = float(row['net'])
        c   = row['c']
        p   = (row.get('p') or '').strip()
        mesic  = int(dt.split('.')[1])
        haleru = round(net * 100)
        idz    = hashlib.sha256(doc.encode('utf-8')).hexdigest()[:12]
        nalezy = detekuj(p)
        if nalezy:
            flagged.setdefault(p, set()).update(nalezy)

        privatni.append({
            "id_zdroje": idz, "ucetni_rok": y, "datum_dokladu": dt,
            "cislo_dokladu": doc, "castka_kc": net, "castka_haleru": haleru,
            "kategorie": c, "popis_puvodni": p, "pii": nalezy,
        })

        if not nalezy:
            popis_verejny = p
        elif set(nalezy) & DRZET:
            # možný soukromý jedinec (adresa/jméno) → jen schválená privátní mapa, jinak placeholder
            popis_verejny = allowlist.get(p, PLACEHOLDER)
        else:
            # jen strukturované PII (číslo dokladu apod.) → deterministické automatické očištění
            popis_verejny = allowlist.get(p, strojove_ocisteni(p))

        verejne.append({
            "id_zdroje": idz, "ucetni_rok": y, "mesic": mesic,
            "castka_haleru": haleru, "kategorie": c,
            "popis_verejny": popis_verejny, "baze": "accrual_cost",
        })

    # 2) Zápis souborů
    for d in (os.path.join(PRIVATE_ZONE, "extrakty"),
              os.path.join(PRIVATE_ZONE, "qa-reporty"),
              os.path.join(WEB_ROOT, "data")):
        os.makedirs(d, exist_ok=True)

    priv_path = os.path.join(PRIVATE_ZONE, "extrakty", "ucet-518-privatni.json")
    with open(priv_path, 'w', encoding='utf-8') as f:
        json.dump(privatni, f, ensure_ascii=False, indent=1)

    pub_json = os.path.join(WEB_ROOT, "data", "ucet-518-polozky-public.json")
    with open(pub_json, 'w', encoding='utf-8') as f:
        json.dump(verejne, f, ensure_ascii=False, indent=1)

    pub_csv = os.path.join(WEB_ROOT, "data", "ucet-518-polozky-public.csv")
    with open(pub_csv, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(["id_zdroje", "ucetni_rok", "mesic", "castka_haleru",
                    "kategorie", "popis_verejny", "baze"])
        for v in verejne:
            w.writerow([v["id_zdroje"], v["ucetni_rok"], v["mesic"],
                        v["castka_haleru"], v["kategorie"], v["popis_verejny"], v["baze"]])

    # 3) Kontrolní součty po letech (v Kč, z haléřů)
    soucty, pocty = {}, {}
    for v in verejne:
        soucty[v["ucetni_rok"]] = soucty.get(v["ucetni_rok"], 0) + v["castka_haleru"]
        pocty[v["ucetni_rok"]]  = pocty.get(v["ucetni_rok"], 0) + 1
    drzeno = sum(1 for v in verejne if v["popis_verejny"] == PLACEHOLDER)
    held = {p: n for p, n in flagged.items() if set(n) & DRZET}
    auto = {p: n for p, n in flagged.items() if not (set(n) & DRZET)}

    # 4) Soukromý report
    report = []
    report.append("# Report extrakce účtu 518 — úkol 1.1 (SOUKROMÉ)\n")
    report.append(f"Vygenerováno: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    report.append("Tento report leží v soukromé zóně a NIKDY se necommituje.\n")
    report.append("## Souhrn\n")
    report.append(f"- Zápisů celkem: **{len(data)}**")
    report.append(f"- Unikátních popisů: **{len({r.get('p','') for r in data})}**")
    report.append(f"- Popisů s nálezem PII: **{len(flagged)}** "
                  f"(podrženo k rozhodnutí: {len(held)}, automaticky očištěno: {len(auto)})")
    report.append(f"- Řádků s podrženým popisem (placeholder): **{drzeno}**")
    report.append(f"- Schválených popisů převzato z privátní mapy: **{len(allowlist)}**\n")

    report.append("## Kontrolní součty po letech (čistý náklad, Kč)\n")
    report.append("| Rok | Počet zápisů | Součet (Kč) |")
    report.append("|---:|---:|---:|")
    for rok in sorted(soucty):
        report.append(f"| {rok} | {pocty[rok]} | {soucty[rok]/100:,.2f} |".replace(",", " "))
    report.append(f"| **∑** | **{len(data)}** | **{sum(soucty.values())/100:,.2f}** |".replace(",", " ") + "\n")

    report.append("## Popisy PODRŽENÉ k rozhodnutí (možný soukromý jedinec)\n")
    report.append(f"Celkem {len(held)} popisů. Placeholder „{PLACEHOLDER}“ ve veřejném "
                  "exportu se nahradí až po schválení čistého popisu v PRIVÁTNÍ mapě "
                  "`~/Developer/transparentniprstice-private/popisy-schvalene.yml`.\n")
    report.append("| Původní popis | Nález | Strojový návrh (uprav dle potřeby) |")
    report.append("|---|---|---|")
    for p in sorted(held):
        report.append(f"| {p} | {', '.join(sorted(held[p]))} | {strojove_ocisteni(p)} |")
    report.append("")

    report.append("## Popisy AUTOMATICKY OČIŠTĚNÉ (jen strukturované PII)\n")
    report.append(f"Celkem {len(auto)} popisů. Číslo dokladu / kontakt odstraněny "
                  "deterministicky; ve veřejném exportu je rovnou očištěná verze.\n")
    report.append("| Původní popis | Nález | Veřejný popis (očištěno) |")
    report.append("|---|---|---|")
    for p in sorted(auto):
        report.append(f"| {p} | {', '.join(sorted(auto[p]))} | {strojove_ocisteni(p)} |")
    report.append("")

    rep_path = os.path.join(PRIVATE_ZONE, "qa-reporty", "report-518-1.1.md")
    with open(rep_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))

    # 5) Shrnutí na výstup
    print("HOTOVO — extrakce účtu 518 (úkol 1.1)")
    print(f"  zdroj ověřen (SHA-256): OK")
    print(f"  zápisů: {len(data)} | popisů s PII: {len(flagged)} | podrženo řádků: {drzeno}")
    print(f"  soukromý extrakt : {priv_path}")
    print(f"  veřejné JSON     : {pub_json}")
    print(f"  veřejné CSV      : {pub_csv}")
    print(f"  soukromý report  : {rep_path}")
    print("  součty po letech (Kč):",
          ", ".join(f"{r}={soucty[r]/100:,.0f}".replace(",", " ") for r in sorted(soucty)))


if __name__ == "__main__":
    main()
