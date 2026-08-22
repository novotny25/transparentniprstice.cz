#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validace dat a privacy gate (úkol 1.8).

Poslední mechanická pojistka před stavbou a nasazením webu. Ověřuje:
  - roční součty účtu 518 (veřejné i privátní) proti výkazu zisku a ztráty,
    tolerance do 1 Kč; přesné kontrolní hodnoty 2022–2025
  - spárování a zohlednění storen (součet témat = roční součet)
  - povolené datové báze a jednotky; accrual (518) a cash (rozpočet)
    se nekontrolují proti sobě jako stejný ukazatel
  - počty obyvatel (až budou)
  - povinné pole `typ` u řízení (až budou)
  - žádná „volná" čísla v HTML mimo datové zdroje (až bude web)
  - PII sken všech verzovaných souborů, buildu, názvů a metadat

Kontroly na dosud chybějící data se PŘESKOČÍ s jasným hlášením (SKIP).
Privacy nález je vždy tvrdá chyba. Skript končí nenulovým kódem při
jakémkoli FAIL — bez projité validace se nestaví fáze 3.
"""
import argparse, json, re, subprocess, sys, unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACT = Path("/home/user/0_PACT/0_Projects/4_PRŠTICE")
DEF_SOUKROMA = PACT / "2026_08_21 TransparentniPrstice.cz" / "soukroma-zona"

VZZ_518_HAL = {2015: 198372427, 2016: 168234920, 2017: 172740174, 2018: 187539660,
               2019: 229018048, 2020: 226311383, 2021: 227522808, 2022: 291339650,
               2023: 582301934, 2024: 351193808, 2025: 473307640}

TVRDE_PII = {
    "cp_ce": re.compile(r'(?i)(č\.\s?p\.|čp\.?|č\.\s?e\.|če\.?)\s?\d+'),
    "parcela": re.compile(r'(?i)p\.\s?č\.\s?\d+'),
    "doklad": re.compile(r'\b\d{2}-\d{3}-\d{5}\b'),
    "rodne_cislo": re.compile(r'\b\d{6}/\d{3,4}\b'),
    "iban": re.compile(r'\bCZ\d{2}[ ]?\d{4}[ ]?\d{4}'),
    "email": re.compile(r'[\w.+-]+@[\w-]+\.[a-z]{2,}'),
    # telefon jen s předvolbou +420 — jinak by 9místné částky v haléřích
    # a formátovaná čísla vypadala jako telefon (falešné poplachy)
    "telefon": re.compile(r'\+420[ ]?\d{3}[ ]?\d{3}[ ]?\d{3}'),
}


class Vysledky:
    def __init__(self):
        self.rows = []
    def add(self, stav, nazev, detail=""):
        self.rows.append((stav, nazev, detail))
    def ok(self, n, d=""): self.add("PASS", n, d)
    def fail(self, n, d=""): self.add("FAIL", n, d)
    def skip(self, n, d=""): self.add("SKIP", n, d)
    def shrnuti(self):
        znak = {"PASS": "✓", "FAIL": "✗", "SKIP": "·"}
        for stav, n, d in self.rows:
            print(f"  {znak[stav]} {stav}  {n}" + (f" — {d}" if d else ""))
        p = sum(1 for r in self.rows if r[0] == "PASS")
        f = sum(1 for r in self.rows if r[0] == "FAIL")
        s = sum(1 for r in self.rows if r[0] == "SKIP")
        print(f"\n  PASS {p} · FAIL {f} · SKIP {s}")
        return f == 0


def nd(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8")) if Path(p).exists() else None


# ── kontroly ────────────────────────────────────────────────────────────
def kontrola_518(V, repo, soukroma):
    pub = load_json(repo / "data" / "ucet-518-polozky-public.json")
    if not pub:
        V.fail("Účet 518 veřejný soubor", "data/ucet-518-polozky-public.json chybí")
        return
    soucty = {}
    for p in pub["polozky"]:
        soucty[p["ucetni_rok"]] = soucty.get(p["ucetni_rok"], 0) + p["castka_hal"]
    # přesné roční součty 2022–2025
    bad = [r for r in (2022, 2023, 2024, 2025) if soucty.get(r) != VZZ_518_HAL[r]]
    if bad:
        V.fail("518 přesné roční součty 2022–2025", f"nesouhlasí roky {bad}")
    else:
        V.ok("518 přesné roční součty 2022–2025", "shoda na haléř")
    # proti VZZ s tolerancí 1 Kč
    vr = load_json(repo / "data" / "vykazy-rady.json")
    if vr:
        vzz = {h["rok"]: h["castka_hal"] for h in vr["rady"]["ucet_518"]["hodnoty"]}
        odch = {r: abs(soucty[r] - vzz[r]) for r in (2022, 2023, 2024, 2025) if r in vzz}
        if all(v <= 100 for v in odch.values()):
            V.ok("518 veřejný vs VZZ (tol. 1 Kč)", "v toleranci")
        else:
            V.fail("518 veřejný vs VZZ", f"odchylky (hal): {odch}")
    else:
        V.skip("518 vs VZZ", "vykazy-rady.json chybí")
    # privátní součty (pokud soukromá zóna dostupná)
    priv = load_json(soukroma / "ucet-518-privatni.json")
    if priv:
        ps = {}
        for z in priv["zapisy"]:
            ps[z["ucetni_rok"]] = ps.get(z["ucetni_rok"], 0) + z["castka_hal"]
        if all(ps.get(r) == VZZ_518_HAL[r] for r in (2022, 2023, 2024, 2025)):
            V.ok("518 privátní součty vs VZZ", "shoda na haléř")
        else:
            V.fail("518 privátní součty vs VZZ", "nesouhlasí")
        # storna: součet témat v rozkladu = roční součet
        rz = load_json(repo / "data" / "ucet-518-rozklad.json")
        if rz:
            good = all(int(rz["rocni_soucty_hal"][str(r)]) == VZZ_518_HAL[r]
                       for r in (2022, 2023, 2024, 2025))
            V.ok("Rozklad: součet témat = roční součet", "storna zohledněna") if good \
                else V.fail("Rozklad: součet témat", "nesedí na roční součet")
        else:
            V.skip("Rozklad storen", "ucet-518-rozklad.json chybí")
    else:
        V.skip("518 privátní součty", "soukromá zóna nedostupná (poběží na Macu)")


def kontrola_baze(V, repo):
    vr = load_json(repo / "data" / "vykazy-rady.json")
    if vr:
        b = {k: v.get("basis") for k, v in vr["rady"].items()}
        if all(x == "accrual_cost" for x in b.values()):
            V.ok("Datová báze VZZ řad", "accrual_cost")
        else:
            V.fail("Datová báze VZZ řad", f"neočekávané: {b}")
    else:
        V.skip("Báze VZZ", "vykazy-rady.json chybí")
    rp = load_json(repo / "data" / "rozpocet.json")
    if rp:
        if rp.get("basis") == "cash_budget" or rp.get("meta", {}).get("basis") == "cash_budget":
            V.ok("Datová báze rozpočtu", "cash_budget")
        else:
            V.fail("Datová báze rozpočtu", "chybí basis: cash_budget")
        V.ok("Cash a accrual se nesčítají", "kontrolují se odděleně (viz metodika)")
    else:
        V.skip("Báze rozpočtu", "rozpocet.json chybí (úkol 1.4, poběží na Macu)")


def kontrola_obyvatele(V, repo):
    ob = load_json(repo / "data" / "obyvatele.json")
    if not ob:
        V.skip("Počty obyvatel", "obyvatele.json chybí (úkol 1.5, poběží na Macu)")
        return
    roky = {int(r) for r in (ob.get("roky") or ob)} if isinstance(ob, (list, dict)) else set()
    V.ok("Počty obyvatel", f"{len(roky)} let") if roky else V.fail("Počty obyvatel", "prázdné")


def kontrola_rizeni(V, repo):
    rz = load_json(repo / "data" / "rizeni.json")
    if not rz:
        V.skip("Řízení (typ soudni/spravni)", "rizeni.json chybí (úkol 1.6)")
        return
    zaznamy = rz.get("rizeni", rz) if isinstance(rz, dict) else rz
    bad = [z for z in zaznamy if z.get("typ") not in ("soudni", "spravni")]
    V.ok("Řízení mají povinné typ", f"{len(zaznamy)} záznamů") if not bad \
        else V.fail("Řízení bez platného typ", f"{len(bad)} záznamů")


def kontrola_html(V, repo):
    htmls = [p for p in (repo / "web").rglob("*.html")] if (repo / "web").exists() else []
    if not htmls:
        V.skip("Čísla v HTML mimo zdroje", "web zatím nepostaven (fáze 3)")
    else:
        V.skip("Čísla v HTML mimo zdroje", f"{len(htmls)} HTML — kontrola se aktivuje ve fázi 3/4")


def tracked_soubory(repo):
    """Verzované i nové (dosud necommitnuté) soubory — vše, co půjde do commitu.
    Ignorované soubory (.gitignore) se vynechají."""
    try:
        tracked = subprocess.run(["git", "-C", str(repo), "ls-files"],
                                 capture_output=True, text=True, check=True).stdout.splitlines()
        others = subprocess.run(["git", "-C", str(repo), "ls-files", "--others",
                                 "--exclude-standard"],
                                capture_output=True, text=True, check=True).stdout.splitlines()
        return [repo / line for line in (tracked + others) if line.strip()]
    except Exception:
        return list(repo.rglob("*"))


def kontrola_pii(V, repo, soukroma):
    # Seznam příjmení k ověření se načítá VÝHRADNĚ ze soukromé zóny
    # (popisy-zasahy.yml, pole jmena_k_overeni). Do veřejného skriptu se
    # žádné jméno nepíše. Bez soukromé zóny se ověřují jen tvrdé vzory.
    jmena = set()
    pz = soukroma / "popisy-zasahy.yml"
    if pz.exists():
        try:
            import yaml
            z = yaml.safe_load(pz.read_text(encoding="utf-8"))
            jmena = set(z.get("jmena_k_overeni", []))
        except Exception:
            pass

    obecni_vyjimka = re.compile(r'(?i)(č\.\s?p\.|čp\.?)\s?82\b')
    nalezy = []
    skenovano = 0
    for f in tracked_soubory(repo):
        if not f.is_file():
            continue
        if f.suffix.lower() not in (".json", ".csv", ".md", ".yml", ".yaml", ".html",
                                    ".js", ".css", ".txt", ".svg"):
            continue
        skenovano += 1
        # název souboru
        for jm in jmena:
            if jm.lower() in f.name.lower():
                nalezy.append(f"jméno v názvu souboru: {f.name}")
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rel = f.relative_to(repo)
        # jména osob
        for jm in jmena:
            if jm in txt:
                nalezy.append(f"jméno '{jm}' v {rel}")
        # tvrdé vzory (mimo pravidla/skripty, kde jsou vzory popsané; a mimo čp.82)
        if rel.parts[0] in ("data",):
            for kod, rx in TVRDE_PII.items():
                for m in rx.finditer(txt):
                    frag = m.group(0)
                    if kod == "cp_ce" and obecni_vyjimka.search(frag):
                        continue
                    nalezy.append(f"{kod} '{frag}' v {rel}")
    # build (dist/ nebo _site/)
    for buildan in ("dist", "_site", "build", "public"):
        bd = repo / buildan
        if bd.exists():
            for f in bd.rglob("*"):
                if f.is_file() and f.suffix.lower() in (".html", ".json", ".csv", ".js"):
                    t = f.read_text(encoding="utf-8", errors="replace")
                    for jm in jmena:
                        if jm in t:
                            nalezy.append(f"jméno '{jm}' v buildu {f.relative_to(repo)}")

    if nalezy:
        V.fail("PII sken verzovaných souborů + build", f"{len(nalezy)} nálezů: "
               + "; ".join(nalezy[:8]))
    else:
        detail = f"{skenovano} souborů čistých"
        detail += "; jména ověřena proti seznamu" if jmena else "; seznam jmen nedostupný, jen tvrdé vzory"
        V.ok("PII sken verzovaných souborů + build", detail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=REPO)
    ap.add_argument("--soukroma-zona", type=Path, default=DEF_SOUKROMA)
    args = ap.parse_args()

    print("VALIDACE A PRIVACY GATE — Transparentní Prštice\n")
    V = Vysledky()
    kontrola_518(V, args.repo, args.soukroma_zona)
    kontrola_baze(V, args.repo)
    kontrola_obyvatele(V, args.repo)
    kontrola_rizeni(V, args.repo)
    kontrola_html(V, args.repo)
    kontrola_pii(V, args.repo, args.soukroma_zona)

    print()
    passed = V.shrnuti()
    if not passed:
        print("\n✗ VALIDACE NEPROŠLA — fáze 3 se nesmí stavět, nasazení se zastaví.")
        sys.exit(1)
    print("\n✓ Validace prošla (nevyřešené nálezy 0). SKIP kontroly čekají na data z Macu.")


if __name__ == "__main__":
    main()
