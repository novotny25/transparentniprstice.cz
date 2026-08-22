#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validace dat a privacy gate — Transparentní Prštice (PLAN.md úkol 1.8)

Spojuje všechny kontroly do jednoho reprodukovatelného gate:
  A. Číselná integrita účtu 518 (součty vs výkaz do 1 Kč, přesné roky, storna,
     báze/jednotky, neúplný rok 2026, návaznost rozkladu).
  B. Privacy gate: PII sken všech tracked souborů a souborů v data/ (obsah,
     názvy), kontrola, že originály ani privátní extrakty nejsou v repu.
  C. Připravené (zatím N/A) kontroly pro obyvatele, řízení, rozpočet a HTML.

Skript skončí chybou (exit 1) při jakémkoli tvrdém nálezu.
„Bez projité validace se nestaví fáze 3." (ZADANI P-19, P-8, PLAN 1.8)

Spuštění: python3 skripty/validace.py
"""
import os, re, json, sys, csv, subprocess

PRIVATE_ZONE = os.path.expanduser("~/Developer/transparentniprstice-private")
WEB_ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA         = os.path.join(WEB_ROOT, "data")

fails, warns, oks, nas = [], [], [], []
def FAIL(cat, msg): fails.append(f"{cat}: {msg}")
def WARN(cat, msg): warns.append(f"{cat}: {msg}")
def OK(cat, msg):   oks.append(f"{cat}: {msg}")
def NA(cat, msg):   nas.append(f"{cat}: {msg}")

def load(path):
    return json.load(open(path, encoding='utf-8')) if os.path.exists(path) else None


# ==========================================================================
# A. ČÍSELNÁ INTEGRITA ÚČTU 518
# ==========================================================================
pub = load(os.path.join(DATA, "ucet-518-polozky-public.json"))
vyk = load(os.path.join(DATA, "vykazy-rady.json"))
roz = load(os.path.join(DATA, "ucet-518-rozklad.json"))
p26 = load(os.path.join(DATA, "ucet-518-2026H1-public.json"))
priv = load(os.path.join(PRIVATE_ZONE, "extrakty", "ucet-518-privatni.json"))

ROKY = [2022, 2023, 2024, 2025]
KONTROLA_ROKY = {2022: 291339650, 2023: 582301934, 2024: 351193808, 2025: 473307640}  # haléře

if pub:
    # placeholdery
    ph = [r for r in pub if str(r.get("popis_verejny", "")).startswith("(popis")]
    (FAIL if ph else OK)("518/placeholder", f"nevyřešených popisů: {len(ph)}")
    # báze
    bad = {r.get("baze") for r in pub} - {"accrual_cost"}
    (FAIL if bad else OK)("518/báze", f"nepovolené báze: {bad or 'žádné'}")
    # roční součty (haléře) přesně
    sums = {}
    for r in pub:
        sums[r["ucetni_rok"]] = sums.get(r["ucetni_rok"], 0) + r["castka_haleru"]
    for rok in ROKY:
        got = sums.get(rok, 0)
        good = got == KONTROLA_ROKY[rok]
        (OK if good else FAIL)("518/roční součet",
            f"{rok}: {got/100:,.2f} Kč {'=' if good else '≠'} kontrola {KONTROLA_ROKY[rok]/100:,.2f}".replace(",", " "))
    # public == private (odvození sedí)
    if priv:
        psum = {}
        for r in priv:
            psum[r["ucetni_rok"]] = psum.get(r["ucetni_rok"], 0) + r["castka_haleru"]
        eq = all(psum.get(y, 0) == sums.get(y, 0) for y in ROKY)
        (OK if eq else FAIL)("518/public=private", "veřejné součty = privátní extrakt" if eq else "veřejné ≠ privátní")
else:
    NA("518", "data/ucet-518-polozky-public.json zatím neexistuje")

# 518 vs VÝKAZ (VZZ) do 1 Kč — accrual vs accrual, NE proti FIN
if pub and vyk:
    v518 = vyk["rady"]["ucet_518"]["hodnoty_kc"]
    for rok in ROKY:
        pub_kc = sums.get(rok, 0) / 100
        vzz_kc = v518[str(rok)]
        good = abs(pub_kc - vzz_kc) <= 1.0
        (OK if good else FAIL)("518 vs výkaz",
            f"{rok}: deník {pub_kc:,.2f} vs výkaz {vzz_kc:,.0f} (±1 Kč) {'OK' if good else 'MIMO'}".replace(",", " "))

# rozklad navazuje na roční změny
if roz and pub:
    for a, b in [(2022, 2023), (2023, 2024), (2024, 2025)]:
        celk = roz["rozklad"][f"{a}_{b}"]["celkem_kc"]
        rozdil = round((sums[b] - sums[a]) / 100, 2)
        good = abs(celk - rozdil) <= 0.05
        (OK if good else FAIL)("rozklad/návaznost",
            f"{a}→{b}: rozklad {celk:,.2f} vs roční rozdíl {rozdil:,.2f}".replace(",", " "))

# neúplný rok 2026
if p26:
    inc = p26.get("meta", {}).get("period_status") == "incomplete"
    (OK if inc else FAIL)("2026/status", "period_status=incomplete" if inc else "chybí incomplete flag!")
    s26 = sum(r["castka_haleru"] for r in p26["polozky"]) / 100
    good = abs(s26 - 2707114.51) <= 0.01
    (OK if good else FAIL)("2026/součet", f"{s26:,.2f} Kč vs kontrola 2 707 114,51".replace(",", " "))
    ph26 = [r for r in p26["polozky"] if str(r.get("popis_verejny", "")).startswith("(popis")]
    (FAIL if ph26 else OK)("2026/placeholder", f"nevyřešených popisů: {len(ph26)}")
else:
    NA("2026", "data/ucet-518-2026H1-public.json zatím neexistuje")

# obyvatelé (úkol 1.5)
oby = load(os.path.join(DATA, "obyvatele.json"))
if oby:
    vals = oby.get("obyvatele", {})
    have = all(str(r) in vals for r in range(2015, 2026))
    (OK if have else FAIL)("obyvatele/roky", "2015–2025 přítomny" if have else "chybí roky 2015–2025")
    pos = vals and all(isinstance(v, int) and v > 0 for v in vals.values())
    (OK if pos else FAIL)("obyvatele/hodnoty", "kladné celé počty" if pos else "neplatné hodnoty")
    src = bool(oby.get("meta", {}).get("zdroj"))
    (OK if src else FAIL)("obyvatele/zdroj", "uveden zdroj + referenční datum" if src else "chybí zdroj")
else:
    NA("obyvatele", "data/obyvatele.json zatím neexistuje (úkol 1.5)")

# rozpočet FIN (úkol 1.4, zatím PŘEDBĚŽNÉ)
rozp = load(os.path.join(DATA, "rozpocet.json"))
if rozp:
    basis = rozp.get("meta", {}).get("basis")
    (OK if basis == "cash_budget" else FAIL)("rozpočet/báze",
        "basis=cash_budget (nesčítá se s 518)" if basis == "cash_budget" else f"nečekaná báze: {basis}")
    # součet paragrafů = výdaje celkem (za každý dostupný rok)
    for rok, d in rozp.get("roky", {}).items():
        s = round(sum(p["skutecnost_kc"] for p in d.get("vydaje_po_paragrafech", {}).values()), 2)
        good = abs(s - d.get("vydaje_celkem_kc", 0)) <= 0.05
        (OK if good else FAIL)("rozpočet/paragrafy", f"{rok}: součet paragrafů = výdaje celkem" if good else f"{rok}: nesedí")
    if rozp.get("meta", {}).get("stav") == "incomplete":
        WARN("rozpočet/stav", f"PŘEDBĚŽNÉ — chybí roky {rozp['meta'].get('chybi_roky')}, P-33 odložena (MONITOR)")
else:
    NA("rozpočet", "data/rozpocet.json zatím neexistuje (úkol 1.4)")

# FIN a VZZ se nekontrolují proti sobě jako stejný ukazatel (strukturální připomínka)
OK("báze/oddělení", "účet 518 = accrual_cost; rozpočet FIN = cash_budget; nesčítají se")


# ==========================================================================
# B. PRIVACY GATE — PII SKEN
# ==========================================================================
# Denylist odvozený z PRIVÁTNÍCH extraktů: přesné původní popisy s PII.
denylist = set()
for ex in (priv, load(os.path.join(PRIVATE_ZONE, "extrakty", "ucet-518-2026H1-privatni.json"))):
    if ex:
        for r in ex:
            if r.get("pii"):
                denylist.add(r["popis_puvodni"])

RE_CP    = re.compile(r'č\.?\s?[pe]\.?\s?\d')                 # adresa čp./če.
RE_DOC   = re.compile(r'\b\d{2}-\d{3}-\d{5}\b')               # interní číslo dokladu
RE_EMAIL = re.compile(r'[\w.+-]+@[\w.-]+\.\w{2,}')
RE_RC    = re.compile(r'\b\d{6}/\d{3,4}\b')                   # rodné číslo
HARD_PAT = [("adresa čp./če.", RE_CP), ("číslo dokladu", RE_DOC),
            ("e-mail", RE_EMAIL), ("rodné číslo", RE_RC)]

# Množina souborů ke skenu: tracked v gitu + vše v data/
try:
    tracked = subprocess.run(["git", "-C", WEB_ROOT, "ls-files"],
                             capture_output=True, text=True).stdout.split("\n")
except Exception as e:
    tracked = []
    WARN("privacy/git", f"git ls-files selhal: {e}")
scan_files = set(f for f in tracked if f.strip())
if os.path.isdir(DATA):
    for fn in os.listdir(DATA):
        scan_files.add(os.path.join("data", fn))

ZAKAZANE_NAZVY = ("privatni", "Detail_uctu", "audit-prstice-rozvaha", "priloha_", ".pdf", ".xlsx", ".docx")

for rel in sorted(scan_files):
    full = os.path.join(WEB_ROOT, rel)
    if not os.path.isfile(full):
        continue
    base = os.path.basename(rel)
    # originály/privátní soubory se nikdy nesmí objevit v repu
    if any(z.lower() in base.lower() for z in ZAKAZANE_NAZVY):
        FAIL("privacy/originál", f"zakázaný soubor v repu: {rel}")
        continue
    try:
        text = open(full, encoding='utf-8').read()
    except (UnicodeDecodeError, IsADirectoryError):
        continue
    # denylist (přesné původní popisy)
    for s in denylist:
        if s and s in text:
            FAIL("privacy/popis", f"{rel}: uniklý původní popis „{s[:40]}…“")
    # strukturované vzory
    for label, rx in HARD_PAT:
        m = rx.search(text)
        if m:
            FAIL("privacy/vzor", f"{rel}: {label} → „{m.group(0)}“")

# kontrola, že privátní extrakt existuje mimo repo (a tedy denylist není prázdný omylem)
if not denylist:
    WARN("privacy/denylist", "denylist je prázdný — chybí privátní extrakt? (sken proběhl jen na vzory)")
else:
    OK("privacy/denylist", f"odvozeno {len(denylist)} citlivých popisů z privátních extraktů")


# ==========================================================================
# C. PŘIPRAVENÉ KONTROLY (zatím N/A)
# ==========================================================================
for soubor, popis in [("rizeni.json", "soudní/správní řízení + povinné pole typ (úkol 1.6)")]:
    if load(os.path.join(DATA, soubor)) is None:
        NA("data", f"{soubor} — {popis}")
if not os.path.isdir(os.path.join(WEB_ROOT, "web")) or not any(
        f.endswith(".html") for f in os.listdir(os.path.join(WEB_ROOT, "web")) if os.path.isfile(os.path.join(WEB_ROOT, "web", f))):
    NA("web", "HTML zatím neexistuje — kontrola 'žádná čísla mimo datové zdroje' (fáze 3)")


# ==========================================================================
# VÝSLEDEK
# ==========================================================================
print("=" * 68)
print("VALIDACE A PRIVACY GATE — účet 518")
print("=" * 68)
for x in oks:   print(f"  [PASS] {x}")
for x in nas:   print(f"  [N/A ] {x}")
for x in warns: print(f"  [WARN] {x}")
for x in fails: print(f"  [FAIL] {x}")
print("-" * 68)
print(f"  PASS: {len(oks)}  |  N/A: {len(nas)}  |  WARN: {len(warns)}  |  FAIL: {len(fails)}")
if fails:
    print("\n❌ VALIDACE NEPROŠLA — nestaví se fáze 3, necommitují se veřejná data.")
    sys.exit(1)
print("\n✅ VALIDACE PROŠLA — číselná integrita i privacy gate v pořádku.")
