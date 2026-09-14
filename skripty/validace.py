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


# --- MAS Bobrava: tabulka obcí musí být úplná a sedět na řádek Celkem (±1 Kč) ---
def _kontrola_mas():
    p = os.path.join(DATA, "mas-bobrava.json")
    d = json.load(open(p, encoding="utf-8"))
    s = sum(o["dotace_kc"] for o in d["obce"]); n = sum(o["projektu"] for o in d["obce"])
    kontroly = [
        (abs(s - d["uzemi"]["dotace_kc"]) <= 1, f"součet řádků {s} vs území {d['uzemi']['dotace_kc']}"),
        (n == d["uzemi"]["projektu"], f"projektů {n} vs {d['uzemi']['projektu']}"),
        (len([o for o in d["obce"] if o["obec"] != "Prštice"]) == d["uzemi"]["obci"], "13 obcí území + Prštice"),
        (all(re.fullmatch(r"\d{6}", o.get("kod", "")) for o in d["obce"]), "všechny obce mají šestimístný kód ČSÚ"),
        (len({o["kod"] for o in d["obce"]}) == len(d["obce"]), "kódy ČSÚ jsou jedinečné"),
    ]
    for plati, zprava in kontroly:
        (OK if plati else FAIL)("MAS", zprava)
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
    (OK if ocekavano in html else FAIL)("poměr dotací", f"v datech i textu {ocekavano}")
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
        (OK if cislo in html else FAIL)("medián dotací", f"číslo {cislo} Kč je v textu")
    pomer = f"{median / prstice:.1f}".replace(".", ",") + "× méně"
    (OK if pomer in html else FAIL)("medián dotací", f"poměr {pomer} je v textu")
    pocet = f"jedenácti ostatních srovnávaných obcí"
    (OK if pocet in html else FAIL)("medián dotací", "text výslovně vylučuje Prštice")
_kontrola_medianu_sousedu()

# --- členství v MAS: text webu musí odpovídat poznámce v datech ---
def _kontrola_clenstvi_mas():
    import json, os
    K = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = json.load(open(os.path.join(K, "data", "mas-bobrava.json"), encoding="utf-8"))
    prstice = [x for x in d["obce"] if x["obec"] == "Prštice"]
    if not prstice:
        FAIL("MAS/členství", "v datech chybí řádek Prštic")
        return
    (OK if prstice[0].get("pozn") == "není členem MAS" else FAIL)("MAS/členství", "poznámka u Prštic: není členem MAS")
    for soubor in ("index.html", "obrazky/mapa-mas-bobrava.svg", "obrazky/mapa-mas-bobrava-mobil.svg"):
        text = open(os.path.join(K, "web", soubor), encoding="utf-8").read().replace(" ", " ")
        (OK if "není členem MAS" in text else FAIL)("MAS/členství", f"{soubor}: správná formulace")
        (OK if "mimo území" not in text else FAIL)("MAS/členství", f"{soubor}: bez zavádějící formulace mimo území")
_kontrola_clenstvi_mas()

# --- nové publikační pojistky: veřejné souhrny, medián, storno a datové bloky ---
def _kontrola_publikace():
    import statistics
    from datetime import date, timedelta
    souhrny = load(os.path.join(DATA, "web-souhrny.json"))
    povinne = {"meta", "rozpocet", "penize", "prubezne_2026H1"}
    (OK if souhrny and set(souhrny) == povinne else FAIL)("publikace/souhrny", "přesné schéma veřejného souhrnu")
    if souhrny:
        r = souhrny["rozpocet"]
        p = souhrny["penize"]
        (OK if len(r["roky"]) == len(r["prijmy"]) == len(r["vydaje"]) else FAIL)("publikace/souhrny", "rozpočtové řady mají stejnou délku")
        (OK if len(p["roky"]) == len(p["ucty"]) == len(p["uvery"]) else FAIL)("publikace/souhrny", "stavové řady mají stejnou délku")

    spolky = load(os.path.join(DATA, "spolky-okoli.json"))
    ostatni = [o["na_obyv_2025"] for o in spolky["obce"] if o["kod"] != "583707"]
    med = statistics.median(ostatni)
    meta = spolky["meta"]
    (OK if med == meta.get("median_ostatnich_na_obyv_2025") and meta.get("median_vylucuje_kod") == "583707" else FAIL)(
        "spolky/medián", f"medián 11 obcí bez Prštic = {med:g} Kč")

    oprava = next((x for x in pub if x.get("id_zdroje") == "fad753e0bf70"), None)
    (OK if oprava and oprava.get("kategorie") == "Opravy/storna dokladů" and oprava.get("kategorie_web") == "ČOV / odpadní vody" else FAIL)(
        "518/storno", "původní kategorie zachována, pro web použita věcná kategorie")

    zadosti = load(os.path.join(DATA, "zadosti-106.json"))["zadosti"]
    for z in (x for x in zadosti if x.get("typ_podani", "").startswith("žádost o informace") and x.get("lhuta_do")):
        if not z.get("datum_doruceni") or not z.get("doklad_doruceni"):
            FAIL("žádosti/lhůta", f"{z['datum_podani']}: chybí doložené datum doručení")
            continue
        konec = date.fromisoformat(z["datum_doruceni"]) + timedelta(days=15)
        while konec.weekday() >= 5:
            konec += timedelta(days=1)
        (OK if konec.isoformat() == z["lhuta_do"] and z.get("lhuta_overena") is True else FAIL)(
            "žádosti/lhůta", f"{z['datum_podani']}: podání, doručení a konec lhůty jsou oddělené a výpočet sedí")

    html = open(os.path.join(WEB_ROOT, "web", "index.html"), encoding="utf-8").read()
    def blok(bid):
        m = re.search(rf'<script[^>]+id="{re.escape(bid)}"[^>]*>(.*?)</script>', html, re.S)
        return json.loads(m.group(1)) if m else None
    if souhrny:
        (OK if blok("d-rozpocet") == souhrny["rozpocet"] else FAIL)("publikace/blok", "d-rozpocet přesně odpovídá veřejnému souhrnu")
        (OK if blok("d-penize") == souhrny["penize"] else FAIL)("publikace/blok", "d-penize přesně odpovídá veřejnému souhrnu")
    datove = re.findall(r'<script[^>]+type="application/json"[^>]*>(.*?)</script>', html, re.S)
    (OK if datove and all("</script" not in x.lower() for x in datove) else FAIL)("publikace/JSON", "datové bloky nemohou předčasně ukončit script")
_kontrola_publikace()


# --- právní a poradenské služby v okrese: data ↔ text na rizeni.html a index.html ---
def _kontrola_pravni_okres():
    import statistics
    d = load(os.path.join(DATA, "pravni-okres.json"))
    if not d:
        FAIL("právní/okres", "data/pravni-okres.json chybí nebo nejde načíst"); return
    m = d["meta"]; p = m["prstice"]; roky = ("2022", "2023", "2024", "2025")
    sk = sorted([o for o in d["obce"] if o.get("skupina_700_1500")], key=lambda o: -o["celkem_2022_2025"])
    (OK if all(700 <= o["obyvatel"] <= 1500 for o in sk) else FAIL)("právní/okres", "skupina = jen obce 700–1 500 obyvatel")
    (OK if len(sk) == m["skupina_pocet"] else FAIL)("právní/okres", f"velikost skupiny {len(sk)} = meta {m['skupina_pocet']}")
    (OK if sk and sk[0]["kod"] == "583707" and p["poradi_skupina_celkem"] == 1 else FAIL)("právní/okres", "Prštice jsou ve skupině první v částce")
    (OK if all(re.fullmatch(r"\d{6}", o["kod"]) for o in d["obce"]) and len({o["kod"] for o in d["obce"]}) == len(d["obce"]) else FAIL)(
        "právní/okres", "kódy ČSÚ jsou šestimístné a jedinečné")
    for o in d["obce"][:20] + [x for x in d["obce"] if x["kod"] == "583707"]:
        if sum(o["roky"][r] for r in roky) != o["celkem_2022_2025"]:
            FAIL("právní/okres", f"{o['obec']}: součet let ≠ celkem"); break
    else:
        OK("právní/okres", "součty let sedí (namátkou 20 obcí + Prštice)")
    med = statistics.median(o["celkem_2022_2025"] for o in sk if o["kod"] != "583707")
    (OK if int(med) == m["median_skupiny_bez_prstic_celkem"] else FAIL)("právní/okres", f"medián skupiny bez Prštic = {int(med)} Kč")
    # položka 5166 Prštic v datech okresu = řada tématu „pravni“ na hlavní stránce (stejný zdroj MONITOR)
    html_i = open(os.path.join(WEB_ROOT, "web", "index.html"), encoding="utf-8").read()
    mt = re.search(r'<script[^>]+id="d-temata"[^>]*>(.*?)</script>', html_i, re.S)
    if mt:
        tem = next((t for t in json.loads(mt.group(1))["temata"] if t["id"] == "pravni"), None)
        rada = dict(zip(json.loads(mt.group(1))["roky"], tem["rada"])) if tem else {}
        prs = next(o for o in d["obce"] if o["kod"] == "583707")
        (OK if all(abs(rada.get(r, -1) - prs["roky"][r]) < 1 for r in roky) else FAIL)("právní/okres", "položka 5166 Prštic = řada tématu na hlavní stránce")
    # podíl právní + GDPR z účtu 518 na položce 5166 — text říká 99 %
    s518 = {"Právní služby": 0.0, "GDPR / pověřenec": 0.0}
    for x in pub:
        k = x.get("kategorie_web") or x.get("kategorie")
        if k in s518 and str(x.get("ucetni_rok")) in roky:
            s518[k] += x["castka_haleru"] / 100
    podil = round(100 * (s518["Právní služby"] + s518["GDPR / pověřenec"]) / p["celkem_2022_2025"])
    (OK if podil == p["podil_pravni_a_gdpr_na_polozce_pct"] else FAIL)("právní/okres", f"podíl právní + GDPR na položce = {podil} %")
    html_r = open(os.path.join(WEB_ROOT, "web", "rizeni.html"), encoding="utf-8").read().replace("\u00a0", " ").replace("&nbsp;", " ")
    (OK if f"z {podil} %" in html_r else FAIL)("právní/okres", f"text na rizeni.html uvádí {podil} %")
    # blok dodavatele: jméno, IČO a obě částky musí být u sebe a rozlišené podle doloženosti
    dod = re.search(r'<div class="dodavatel">(.*?)<details', html_r, re.S)
    if not dod:
        FAIL("právní/dodavatel", "blok s dodavatelem na stránce chybí")
    else:
        b = dod.group(1)
        for co in ("Mgr. Radovan Vrbka", "IČO 60353091", "Rašínova 103/2"):
            (OK if co in b else FAIL)("právní/dodavatel", f"blok uvádí {co}")
        for cislo in (p["ucet_518_pravni_2022_2025"], p["ucet_518_gdpr_2022_2025"]):
            (OK if f"{cislo:,}".replace(",", " ") in b else FAIL)(
                "právní/dodavatel", f"blok uvádí částku {cislo:,} Kč".replace(",", " "))
        (OK if 'chip nezjisteno' in b and "nepotvrdila" in b else FAIL)(
            "právní/dodavatel", "u pověřence GDPR je vyznačeno, že příjemce není doložený")
        (OK if "opravím to" in b else FAIL)(
            "právní/dodavatel", "u neověřené části je nabídnuta oprava, doloží-li obec jinak")
        (OK if "271/2010/Z26" in b and "11. 3. 2010" in b else FAIL)(
            "právní/dodavatel", "je uvedeno usnesení zastupitelstva, na jehož základě zakázky jdou")
        # citace usnesení musí doslova sedět na sdělení obce, ne na parafrázi
        try:
            import fitz
            pdf = " ".join(x.get_text() for x in fitz.open(
                os.path.join(WEB_ROOT, "web", "dokumenty", "2026-09-04_odpoved-obce-OUPR-1132-2026.pdf")))
            pdf = re.sub(r"\s+", " ", pdf)
            citace = re.search(r"<q>(.*?)</q>", b, re.S)
            cit = re.sub(r"<[^>]+>", "", citace.group(1)) if citace else ""
            cit = re.sub(r"\s+", " ", cit).strip()
            (OK if cit and cit in pdf else FAIL)(
                "právní/dodavatel", "citace usnesení doslova odpovídá sdělení obce v PDF")
        except ImportError:
            NA("právní/dodavatel", "citaci usnesení proti PDF nelze ověřit — chybí PyMuPDF")
        soucet = p["ucet_518_pravni_2022_2025"] + p["ucet_518_gdpr_2022_2025"]
        (OK if f"{soucet:,}".replace(",", " ") in b else FAIL)(
            "právní/dodavatel", f"součet {soucet:,} Kč sedí na obě částky".replace(",", " "))
    for cislo in (p["ucet_518_pravni_2022_2025"], p["ucet_518_gdpr_2022_2025"], p["celkem_2022_2025"]):
        t = f"{cislo:,}".replace(",", " ")
        (OK if t in html_r else FAIL)("právní/okres", f"částka {t} Kč je v textu rizeni.html")
    (OK if "<!--pravni-tab-start--><div" in html_r and "<!--pravni-veta-start--><p" in html_r else FAIL)("právní/okres", "tabulka a věta jsou vložené staticky")
    # graf: žebříček má všech 63 řádků, Prštice zvýrazněné a čáru mediánu z dat
    graf = re.search(r"<!--pravni-graf-start-->(.*?)<!--pravni-graf-konec-->", html_r, re.S)
    if not graf:
        FAIL("právní/graf", "graf není vložený do stránky")
    else:
        g = graf.group(1)
        (OK if g.count('class="radek') == len(sk) else FAIL)(
            "právní/graf", f"žebříček kreslí všech {len(sk)} obcí")
        (OK if g.count('class="radek my"') == 1 else FAIL)("právní/graf", "Prštice jsou zvýrazněné právě jednou")
        med_pct = f'--med:{med / sk[0]["celkem_2022_2025"] * 100:.2f}%'
        (OK if med_pct in g else FAIL)("právní/graf", f"čára mediánu odpovídá datům ({med_pct})")
        (OK if 'width:100.00%' in g else FAIL)("právní/graf", "nejdelší sloupeček patří Pršticím")
        (OK if "<svg" not in g else FAIL)("právní/graf", "graf je HTML, ne SVG — písmo se nezmenšuje se šířkou okna")
    # v kartě nesmí zůstat odstavec bez třídy — dědil by velikost z těla stránky (19 px)
    karta = re.search(r'<h2 id="okres-h".*?</div>\s*</section>', html_r, re.S)
    bez_tridy = re.findall(r"<p>(?!\s*</p>)", karta.group(0)) if karta else ["?"]
    (OK if not bez_tridy else FAIL)("právní/graf", "všechny odstavce v kartě mají třídu (sub/souhrn/src)")

_kontrola_pravni_okres()


# --- průměrný věk na stránce Obec v kostce musí sedět na data rešerše ---
def _kontrola_veku():
    d = load(os.path.join(DATA, "srovnani-obci.json"))
    if not d or "vek" not in d:
        FAIL("věk", "data/srovnani-obci.json chybí nebo nemá část o věku"); return
    v = d["vek"]
    html = open(os.path.join(WEB_ROOT, "web", "obec.html"), encoding="utf-8").read()
    html = html.replace("\u00a0", " ").replace("&nbsp;", " ")
    # pozor: f"{41.65:.1f}" dá 41,6 — plovoucí čárka drží 41,6499…, proto Decimal
    from decimal import Decimal, ROUND_HALF_UP
    des = lambda x: str(Decimal(str(x)).quantize(Decimal("0.1"), ROUND_HALF_UP)).replace(".", ",")
    for t in (des(v["prstice"]),
              f"{v['poradi_prstic_od_nejstarsiho']}. nejvyšší ze {v['obci_v_okrese']} obcí",
              f"průměr okresu {des(v['okres'])}"):
        (OK if t in html else FAIL)("věk", f"obec.html uvádí „{t}“ podle dat")
    # věk se nesmí vrátit na hlavní stránku pod jiným srovnávacím základem
    idx = open(os.path.join(WEB_ROOT, "web", "index.html"), encoding="utf-8").read()
    (OK if "Průměrný věk" not in idx and "d-srovnani" not in idx else FAIL)(
        "věk", "hlavní stránka věk neuvádí — jeden srovnávací základ místo dvou")
_kontrola_veku()


# ==========================================================================
# VÝSLEDEK — tiskne se až po všech povinných kontrolách
# ==========================================================================
print("=" * 68)
print("VALIDACE A PRIVACY GATE — účet 518 a publikace webu")
print("=" * 68)
for x in oks:   print(f"  [PASS] {x}")
for x in nas:   print(f"  [SKIP] {x}")
for x in warns: print(f"  [WARN] {x}")
for x in fails: print(f"  [FAIL] {x}")
print("-" * 68)
print(f"  PASS: {len(oks)}  |  SKIP: {len(nas)}  |  WARN: {len(warns)}  |  FAIL: {len(fails)}")
if fails:
    print("\n❌ VALIDACE NEPROŠLA — web se nesmí publikovat.")
    sys.exit(1)
print("\n✅ VALIDACE PROŠLA — povinné kontroly doběhly a nemají chybu.")
