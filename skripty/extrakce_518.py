#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrakce účtu 518 — soukromá extrakce a veřejný export (úkol 1.1).

Vstup:  originální účetní detail (HTML s JSON na řádku 160) — SOUKROMÁ ZÓNA
Výstup:
  SOUKROMÉ (mimo veřejné repo, do soukromé zóny):
    - ucet-518-privatni.json      všech 1335 zápisů se VŠEMI poli + přiřazený kód
    - mapovani-popisu.yml         původní popis -> kód (obsahuje původní texty)
    - qa-report-518-private.html  kontrolní report ke schválení
  VEŘEJNÉ (do data/ ve webovém repu):
    - ucet-518-polozky-public.json  jen povolená pole, popis z číselníku
    - ucet-518-polozky-public.csv
    - zdroje.json                   evidence zdrojových datasetů

Bezpečnost: veřejný výstup NIKDY neobsahuje původní pole dt/doc/p.
Popis se nahrazuje označením z řízeného číselníku (anonymizace/cislenik-popisu.yml).
"""
import argparse, csv, hashlib, html, json, sys, unicodedata
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Chybí PyYAML: pip install pyyaml")

REPO = Path(__file__).resolve().parent.parent
PACT = Path("/home/user/0_PACT/0_Projects/4_PRŠTICE")
DEF_ORIGINAL = PACT / "2026_06_22 Analýza účtu 518" / "Detail_uctu_518_Prstice.html"
DEF_SOUKROMA = PACT / "2026_08_21 TransparentniPrstice.cz" / "soukroma-zona"
DEF_CISLENIK = REPO / "anonymizace" / "cislenik-popisu.yml"
DEF_DATA = REPO / "data"

ZDROJ_ID = "detail-518-2022-2025"


def bez_diakritiky(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def norm(s: str) -> str:
    return " ".join(bez_diakritiky(s).lower().split())


def nacti_zapisy(original: Path):
    """Vytáhne JSON pole DATA = [...] ze zdrojového HTML."""
    text = original.read_text(encoding="utf-8")
    marker = "const DATA = "
    i = text.index(marker) + len(marker)
    # najdi vyvážené hranaté závorky
    start = text.index("[", i)
    depth, j, in_str, esc = 0, start, False, False
    while j < len(text):
        ch = text[j]
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': in_str = False
        else:
            if ch == '"': in_str = True
            elif ch == "[": depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    break
        j += 1
    return json.loads(text[start:j + 1])


def priraz_kod(popis: str, kategorie: str, kody, fallback, lock=()):
    """Vrátí (kod, zpusob). U zamčených kategorií přebíjí kategorie popis."""
    if kategorie in lock:
        return fallback[kategorie], f"zámek kategorie: {kategorie}"
    n = norm(popis)
    for k in kody:
        for kw in k.get("klicova_slova", []) or []:
            if kw and norm(kw) in n:
                return k["kod"], f"klíč: {kw}"
    fb = fallback.get(kategorie)
    if fb is None:
        return "ostatni", "fallback: neznámá kategorie"
    return fb, f"fallback: {kategorie}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", type=Path, default=DEF_ORIGINAL)
    ap.add_argument("--cislenik", type=Path, default=DEF_CISLENIK)
    ap.add_argument("--soukroma-zona", type=Path, default=DEF_SOUKROMA)
    ap.add_argument("--data", type=Path, default=DEF_DATA)
    args = ap.parse_args()

    if not args.original.exists():
        sys.exit(f"Originál nenalezen: {args.original}\n"
                 f"Skript běží jen tam, kde je soukromý originál (PACT / Mac).")

    cis = yaml.safe_load(args.cislenik.read_text(encoding="utf-8"))
    kody = cis["kody"]
    oznaceni = {k["kod"]: k["oznaceni"] for k in kody}
    fallback = cis["fallback_dle_kategorie"]
    lock = set(cis.get("kategorie_lock", []))
    # kontrola: každý fallback kód existuje
    for cat, kod in fallback.items():
        if kod not in oznaceni:
            sys.exit(f"Fallback kategorie '{cat}' míří na neexistující kód '{kod}'")

    raw = args.original.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    zapisy = nacti_zapisy(args.original)

    # ── zpracování ──────────────────────────────────────────────────
    privatni, mapovani = [], {}
    for z in zapisy:
        rok = int(z["y"])
        den, mesic, _rok = (z["dt"].split(".") + ["", "", ""])[:3]
        mesic = int(mesic)
        castka_hal = int(round(float(z["net"]) * 100))
        popis = z.get("p", "") or ""
        kod, zpusob = priraz_kod(popis, z["c"], kody, fallback, lock)
        privatni.append({
            "ucetni_rok": rok, "mesic": mesic, "den": int(den) if den.isdigit() else None,
            "doklad": z.get("doc", ""), "castka_hal": castka_hal,
            "kategorie": z["c"], "popis_original": popis,
            "kod": kod, "popis_verejny": oznaceni[kod], "zpusob_prirazeni": zpusob,
        })
        mapovani.setdefault(popis, {"kod": kod, "oznaceni": oznaceni[kod],
                                    "zpusob": zpusob, "pocet": 0})
        mapovani[popis]["pocet"] += 1

    # ── veřejné ID: deterministicky, BEZ vazby na datum ─────────────
    verejne = []
    for rok in sorted({p["ucetni_rok"] for p in privatni}):
        v = [p for p in privatni if p["ucetni_rok"] == rok]
        v.sort(key=lambda p: (p["mesic"], p["kategorie"], p["castka_hal"], p["popis_verejny"]))
        for i, p in enumerate(v, 1):
            verejne.append({
                "id": f"518-{rok}-{i:04d}",
                "ucetni_rok": rok, "mesic": p["mesic"],
                "castka_hal": p["castka_hal"], "kategorie": p["kategorie"],
                "popis_verejny": p["popis_verejny"], "zdroj_id": ZDROJ_ID,
                "obdobi_stav": "uzavrene",
            })

    # ── POJISTKA: veřejný výstup smí obsahovat jen povolené hodnoty ──
    # 1) veřejný popis musí pocházet z číselníku, ne z původního textu
    povolene = set(oznaceni.values())
    cizi = [p["popis_verejny"] for p in verejne if p["popis_verejny"] not in povolene]
    if cizi:
        sys.exit("STOP: veřejný popis mimo číselník: " + "; ".join(sorted(set(cizi))[:5]))
    # 2) povolené klíče a kategorie
    ok_klice = {"id","ucetni_rok","mesic","castka_hal","kategorie","popis_verejny","zdroj_id","obdobi_stav"}
    for p in verejne:
        if set(p) != ok_klice:
            sys.exit(f"STOP: veřejný zápis {p.get('id')} má neočekávaná pole: {set(p)^ok_klice}")
    ok_kat = set(fallback)
    bad_kat = {p["kategorie"] for p in verejne} - ok_kat
    if bad_kat:
        sys.exit(f"STOP: neočekávaná kategorie ve veřejném výstupu: {bad_kat}")
    # 3) tvrdé PII-vzory z pravidel nesmí být nikde ve veřejném blobu
    #    (jméno-kandidát se zde nepoužívá — číselník legitimně obsahuje velká písmena)
    import re as _re
    blob = json.dumps(verejne, ensure_ascii=False)
    pravidla = yaml.safe_load((REPO/"anonymizace"/"pravidla.yml").read_text(encoding="utf-8"))
    tvrde = {"cp_ce","parcela","doklad","rodne_cislo","iban_ucet","email","telefon","datum_narozeni"}
    nalezy=[]
    for v in pravidla["detekce"]["vzory"]:
        if v["kod"] in tvrde:
            m=_re.search(v["regex"], blob)
            if m: nalezy.append(f"{v['kod']}: '{m.group(0)}'")
    if nalezy:
        sys.exit("STOP: ve veřejném výstupu tvrdý osobní údaj:\n  " + "\n  ".join(nalezy))

    # ── zápis veřejných souborů ─────────────────────────────────────
    args.data.mkdir(parents=True, exist_ok=True)
    (args.data / "ucet-518-polozky-public.json").write_text(
        json.dumps({"zdroj_id": ZDROJ_ID, "polozky": verejne},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (args.data / "ucet-518-polozky-public.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "ucetni_rok", "mesic", "castka_hal", "kategorie", "popis_verejny", "zdroj_id", "obdobi_stav"])
        for p in verejne:
            w.writerow([p["id"], p["ucetni_rok"], p["mesic"], p["castka_hal"],
                        p["kategorie"], p["popis_verejny"], p["zdroj_id"], p["obdobi_stav"]])
    (args.data / "zdroje.json").write_text(json.dumps({
        "zdroje": [{
            "id": ZDROJ_ID,
            "nazev": "Účetní detail účtu 518 za roky 2022–2025",
            "puvod": "Obec Prštice, odpověď na žádost dle zákona č. 106/1999 Sb.",
            "vykaz": "Deník účtu 518 – Ostatní služby",
            "obdobi": "2022–2025",
            "poznamka": "Roční součty souhlasí s výkazem zisku a ztráty. Dodavatelé v detailu nejsou uvedeni.",
        }]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ── zápis soukromých souborů ────────────────────────────────────
    args.soukroma_zona.mkdir(parents=True, exist_ok=True)
    (args.soukroma_zona / "ucet-518-privatni.json").write_text(json.dumps({
        "zdroj_id": ZDROJ_ID, "sha256_originalu": sha,
        "pocet_zapisu": len(privatni), "zapisy": privatni,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.soukroma_zona / "mapovani-popisu.yml").write_text(
        "# SOUKROMÉ — původní popisy se jmény. Nikdy do veřejného repa.\n"
        "# Původní popis -> kód číselníku (výsledek úkolu 1.1).\n"
        + yaml.safe_dump(mapovani, allow_unicode=True, sort_keys=True), encoding="utf-8")

    # ── kontrolní součty ────────────────────────────────────────────
    soucty = {}
    for rok in sorted({p["ucetni_rok"] for p in privatni}):
        soucty[rok] = sum(p["castka_hal"] for p in privatni if p["ucetni_rok"] == rok) / 100

    napsat_report(args.soukroma_zona / "qa-report-518-private.html",
                  privatni, mapovani, oznaceni, kody, soucty, sha, len(zapisy))

    # ── shrnutí na konzoli ──────────────────────────────────────────
    print(f"Zpracováno {len(privatni)} zápisů, SHA-256 originálu {sha[:16]}…")
    print("Roční součty (Kč):", {r: f"{v:,.2f}" for r, v in soucty.items()})
    fb = sum(1 for p in privatni if p["zpusob_prirazeni"].startswith("fallback"))
    print(f"Přiřazeno klíčovým slovem: {len(privatni)-fb}, fallbackem dle kategorie: {fb}")
    print("Veřejné soubory:", args.data)
    print("Soukromé soubory + report:", args.soukroma_zona)


def napsat_report(cesta, privatni, mapovani, oznaceni, kody, soucty, sha, n):
    import collections
    e = html.escape
    poradi = [k["kod"] for k in kody]
    per_kod = collections.defaultdict(lambda: {"pocet": 0, "hal": 0, "popisy": set()})
    for p in privatni:
        d = per_kod[p["kod"]]
        d["pocet"] += 1; d["hal"] += p["castka_hal"]; d["popisy"].add(p["popis_original"])
    fallbacky = [p for p in privatni if p["zpusob_prirazeni"].startswith("fallback")]

    out = ["<!doctype html><meta charset=utf-8><title>QA report účet 518</title>",
           "<style>body{font:15px/1.5 system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#1a1a1a}"
           "h1,h2{line-height:1.2}table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:14px}"
           "th,td{border:1px solid #ccc;padding:4px 8px;text-align:left;vertical-align:top}"
           "th{background:#f0f0f0}code{background:#f4f4f4;padding:1px 4px;border-radius:3px}"
           ".flag{background:#fff3cd}.num{text-align:right;font-variant-numeric:tabular-nums}"
           "details{margin:.3rem 0}summary{cursor:pointer}</style>"]
    out.append("<h1>Kontrolní report — účet 518, úkol 1.1</h1>")
    out.append("<p><strong>SOUKROMÝ dokument.</strong> Slouží ke kontrole, jak se z původních "
               "popisů staly veřejné popisy. Obsahuje původní texty se jmény — nikdy nepatří do webu.</p>")
    out.append(f"<p>Zdroj SHA-256: <code>{sha}</code><br>Zápisů: {n}</p>")

    out.append("<h2>Roční součty</h2><table><tr><th>Rok</th><th class=num>Součet (Kč)</th></tr>")
    for r, v in soucty.items():
        out.append(f"<tr><td>{r}</td><td class=num>{v:,.2f}</td></tr>")
    out.append("</table><p>Tyto součty musí sedět na výkaz zisku a ztráty (kontrola v úkolu 1.8).</p>")

    out.append(f"<h2 class=flag>Přiřazeno fallbackem dle kategorie: {len(fallbacky)} zápisů</h2>")
    out.append("<p>U těchto zápisů nezabralo žádné klíčové slovo — dostaly obecné označení "
               "podle kategorie. Zkontroluj, zda je obecné označení dostatečné, nebo zda si "
               "téma zaslouží vlastní kód.</p>")
    fb_popisy = collections.Counter(p["popis_original"] for p in fallbacky)
    out.append("<table><tr><th>Původní popis</th><th class=num>×</th><th>Veřejné označení</th></tr>")
    for popis, cnt in sorted(fb_popisy.items(), key=lambda x: (-x[1], x[0])):
        kod_here = next(p["kod"] for p in fallbacky if p["popis_original"] == popis)
        out.append(f"<tr><td>{e(popis) or '<em>(prázdný)</em>'}</td><td class=num>{cnt}</td>"
                   f"<td>{e(oznaceni[kod_here])}</td></tr>")
    out.append("</table>")

    out.append("<h2>Souhrn po kódech</h2><table><tr><th>Kód</th><th>Veřejné označení</th>"
               "<th class=num>Zápisů</th><th class=num>Součet Kč</th><th>Původní popisy</th></tr>")
    for kod in poradi:
        if kod not in per_kod: continue
        d = per_kod[kod]
        popisy = sorted(d["popisy"])
        det = "<details><summary>{} unikátních</summary><ul>{}</ul></details>".format(
            len(popisy), "".join(f"<li>{e(x) or '<em>(prázdný)</em>'}</li>" for x in popisy))
        out.append(f"<tr><td><code>{e(kod)}</code></td><td>{e(oznaceni[kod])}</td>"
                   f"<td class=num>{d['pocet']}</td><td class=num>{d['hal']/100:,.2f}</td><td>{det}</td></tr>")
    out.append("</table>")
    Path(cesta).write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
