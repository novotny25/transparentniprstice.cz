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

# řízení + tracker žádostí (úkol 1.6, zatím DRAFT)
riz = load(os.path.join(DATA, "rizeni.json"))
if riz:
    recs = riz.get("rizeni", [])
    typ_ok = recs and all(r.get("typ") in ("soudni", "spravni") for r in recs)
    (OK if typ_ok else FAIL)("řízení/typ", "každý záznam má povinné typ soudni|spravni" if typ_ok else "chybí/špatný typ")
    uohs_soud = [r for r in recs if "ÚOHS" in r.get("instituce", "") and r.get("typ") == "soudni"]
    (FAIL if uohs_soud else OK)("řízení/ÚOHS", "ÚOHS není označen jako soud" if not uohs_soud else "ÚOHS chybně jako soudni!")
    sr = riz.get("soudni_rizeni", {})
    veci = sr.get("veci", [])
    if veci:
        sh = sr.get("souhrn", {})
        sedi = (sh.get("celkem") == len(veci)
                and sh.get("bezi") == sum(1 for v in veci if v.get("bezi"))
                and sh.get("skonceno") == sum(1 for v in veci if not v.get("bezi"))
                and sh.get("odvolacich_rizeni") == sum(len(v.get("odvolani", [])) for v in veci)
                and sh.get("narizenych_jednani") == sum(v.get("narizenych_jednani", 0) for v in veci))
        (OK if sedi else FAIL)("řízení/souhrn", f"souhrnná čísla souhlasí s {len(veci)} záznamy"
                               if sedi else "souhrnná čísla nesedí se seznamem věcí")
        pole_ok = all(v.get("spisova_znacka") and v.get("soud") and v.get("zahajeno") and v.get("stav")
                      for v in veci)
        (OK if pole_ok else FAIL)("řízení/soudní pole", "každé řízení má značku, soud, datum zahájení a stav"
                                  if pole_ok else "u některého řízení chybí povinný údaj")
        WARN("řízení/stav", "správní část ÚOHS ověřená; soudní část = seznam od obce + průběh z infoSoudu, "
                            "předmět a výsledky obec neposkytla (podána stížnost)")
    else:
        WARN("řízení/stav", "správní část ÚOHS ověřená; soudní část čeká na odpověď obce (fáze 6)")
else:
    NA("řízení", "data/rizeni.json zatím neexistuje (úkol 1.6)")

zad = load(os.path.join(DATA, "zadosti-106.json"))
if zad:
    ok_z = all(z.get("datum_podani") and z.get("predmet") and z.get("stav") for z in zad.get("zadosti", []))
    (OK if ok_z else FAIL)("žádosti/pole", "každá žádost má datum, předmět a stav" if ok_z else "chybí povinné pole")
else:
    NA("žádosti", "data/zadosti-106.json zatím neexistuje (úkol 1.6)")

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
# Kontaktní adresa autora je na webu záměrně (P-11 vyžaduje uvedení kontaktu),
# takže není únikem osobního údaje. Úřední kontakty obce a funkcionářů na
# stránce „Obec v kostce" (P-37) jsou údaje o veřejné činnosti dle § 8a
# odst. 2 zákona 106/1999 Sb., převzaté z oficiálního webu obce — schválil
# Petr 28. 8. 2026.
POVOLENE_EMAILY = {
    "petr@petrnovotny.com",
    "prstice@prstice.cz",   # obecní úřad + podatelna (oficiální web obce)
    "danek@prstice.cz",     # starosta — úřední kontakt (oficiální web obce)
    "urban@prstice.cz",     # místostarosta — úřední kontakt (oficiální web obce)
}
# Rodné číslo: YYMMDD/XXXX. Měsíc musí být platný (01–12, u žen +50),
# jinak by vzor chytal i čísla jednací typu „123854/2026“.
RE_RC    = re.compile(r'\b\d{2}(?:0[1-9]|1[0-2]|5[1-9]|6[0-2])(?:0[1-9]|[12]\d|3[01])/\d{3,4}\b')
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
    # web/dokumenty/ obsahuje veřejné deriváty, které prošly anonymizací
    # (skripty/anonymizace.py) — ty se kontrolují tam, ne tady jako originály
    je_derivat = rel.replace(os.sep, "/").startswith("web/dokumenty/")
    if not je_derivat and any(z.lower() in base.lower() for z in ZAKAZANE_NAZVY):
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
        for m in rx.finditer(text):
            if label == "e-mail" and m.group(0).lower() in POVOLENE_EMAILY:
                continue          # kontakt autora je zveřejněn záměrně (P-11)
            FAIL("privacy/vzor", f"{rel}: {label} → „{m.group(0)}“")
            break

# kontrola, že privátní extrakt existuje mimo repo (a tedy denylist není prázdný omylem)
if not denylist:
    WARN("privacy/denylist", "denylist je prázdný — chybí privátní extrakt? (sken proběhl jen na vzory)")
else:
    OK("privacy/denylist", f"odvozeno {len(denylist)} citlivých popisů z privátních extraktů")


# ==========================================================================
# C. PŘIPRAVENÉ KONTROLY (zatím N/A)
# ==========================================================================
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

# --- MAS Bobrava: tabulka obcí musí být úplná a sedět na řádek Celkem (±1 Kč) ---
def _kontrola_mas():
    import json, os
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "mas-bobrava.json")
    d = json.load(open(p, encoding="utf-8"))
    s = sum(o["dotace_kc"] for o in d["obce"]); n = sum(o["projektu"] for o in d["obce"])
    assert abs(s - d["uzemi"]["dotace_kc"]) <= 1, f"MAS: součet řádků {s} ≠ území {d['uzemi']['dotace_kc']}"
    assert n == d["uzemi"]["projektu"], f"MAS: projektů {n} ≠ {d['uzemi']['projektu']}"
    assert len([o for o in d["obce"] if o["obec"] != "Prštice"]) == d["uzemi"]["obci"], "MAS: chybí obce území"
_kontrola_mas()

# --- poměr dotací mezi obdobími musí sedět na text v banneru ---
def _kontrola_pomeru_dotaci():
    import json, os, re
    K = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = json.load(open(os.path.join(K, "data", "dotace-web.json"), encoding="utf-8"))
    driv = sum(x["kc"] for x in d["prsticeDrive"])
    nyni = sum(x["kc"] for x in d["prstice2025"] if x.get("typ") == "obec")
    ocekavano = f"{round(driv / nyni)}× méně"
    html = open(os.path.join(K, "web", "index.html"), encoding="utf-8").read().replace("\u00a0", " ")
    assert ocekavano in html, f"pomer dotací: v datech vychází „{ocekavano}“, na stránce není"
_kontrola_pomeru_dotaci()

# --- poměr Prštic k mediánu sousedů musí sedět na text v banneru ---
def _kontrola_medianu_sousedu():
    import json, os, statistics
    K = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    o = json.load(open(os.path.join(K, "data", "dotace-web.json"), encoding="utf-8"))["obce"]
    prstice = [x for x in o if x["n"] == "Prštice"][0]["naob"]
    ostatni = [x["naob"] for x in o if x["n"] != "Prštice"]
    median = statistics.median(ostatni)
    html = open(os.path.join(K, "web", "index.html"), encoding="utf-8").read().replace(" ", " ")
    for cislo in (f"{median:,.0f}".replace(",", " "), f"{prstice:,.0f}".replace(",", " ")):
        assert cislo in html, f"medián sousedů: číslo „{cislo} Kč“ z dat na stránce chybí"
    pomer = f"{median / prstice:.1f}".replace(".", ",") + "× méně"
    assert pomer in html, f"medián sousedů: v datech vychází „{pomer}“, na stránce není"
    assert f"Medián {['nula','jednoho','dvou','tří','čtyř','pěti','šesti','sedmi','osmi','devíti','deseti','jedenácti','dvanácti'][len(ostatni)]} sousedů" in html, \
        f"medián sousedů: v datech je {len(ostatni)} obcí bez Prštic, text uvádí jiný počet"
_kontrola_medianu_sousedu()

# --- členství v MAS: text webu musí odpovídat poznámce v datech ---
def _kontrola_clenstvi_mas():
    import json, os
    K = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = json.load(open(os.path.join(K, "data", "mas-bobrava.json"), encoding="utf-8"))
    prstice = [x for x in d["obce"] if x["obec"] == "Prštice"]
    assert prstice, "MAS: v datech chybí řádek Prštic"
    assert prstice[0].get("pozn") == "není členem MAS", \
        f"MAS: poznámka u Prštic je „{prstice[0].get('pozn')}“, čekáno „není členem MAS“"
    for soubor in ("index.html", "obrazky/mapa-mas-bobrava.svg", "obrazky/mapa-mas-bobrava-mobil.svg"):
        text = open(os.path.join(K, "web", soubor), encoding="utf-8").read().replace(" ", " ")
        assert "není členem MAS" in text, f"MAS: v {soubor} chybí formulace „není členem MAS“"
        assert "mimo území" not in text, f"MAS: v {soubor} zůstala zavádějící formulace „mimo území“"
_kontrola_clenstvi_mas()
