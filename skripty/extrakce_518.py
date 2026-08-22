#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrakce účtu 518 — soukromá extrakce a veřejný export (úkol 1.1, revize 2).

Zásada (rozhodnutí Petra): původní účetní popis obce se ZACHOVÁVÁ. Mění se
jen tam, kde obsahuje osobní údaj nebo číslo dokladu — podle explicitního
a schváleného seznamu anonymizace/popisy-zasahy.yml. Analytické téma (kód)
z anonymizace/cislenik-popisu.yml slouží k SESKUPENÍ pro rozklad změn
(úkol 1.7); do veřejných dat se nedává — tam je původní popis + kategorie.

Výstup:
  SOUKROMÉ (soukromá zóna): ucet-518-privatni.json (vše + kód), qa-report
  VEŘEJNÉ (data/): ucet-518-polozky-public.json/.csv, zdroje.json

Pojistka odmítne veřejný výstup, kde je tvrdý osobní údaj (mimo schválené
obecní výjimky) nebo velké slovo, které není ani schválené ne-jméno
(whitelist v pravidla.yml), ani vyřešené zásahem. Tím nemůže projít
přehlédnuté jméno.
"""
import argparse, csv, hashlib, json, re, sys, unicodedata
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
DEF_ZASAHY = DEF_SOUKROMA / "popisy-zasahy.yml"
DEF_PRAVIDLA = REPO / "anonymizace" / "pravidla.yml"
DEF_DATA = REPO / "data"
ZDROJ_ID = "detail-518-2022-2025"

TVRDE_PII = {
    "cp_ce": re.compile(r'(?i)(č\.\s?p\.|čp\.?|č\.\s?e\.|če\.?)\s?\d+'),
    "parcela": re.compile(r'(?i)p\.\s?č\.\s?\d+'),
    "doklad": re.compile(r'\b\d{2}-\d{3}-\d{5}\b'),
    "rodne_cislo": re.compile(r'\b\d{6}/\d{3,4}\b'),
    "email": re.compile(r'[\w.+-]+@[\w-]+\.\w+'),
    "telefon": re.compile(r'(?<!\d)(\+420)?\d{3}\s?\d{3}\s?\d{3}(?!\d)'),
}


def bez_diakritiky(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def norm(s):
    return " ".join(bez_diakritiky(s).lower().split())


def velka_slova(popis):
    return [w for w in re.findall(r'\b[\wÁ-Žá-ž]+\b', popis)
            if len(w) >= 2 and w[0].isupper() and not w.isdigit()]


def nacti_zapisy(original):
    text = original.read_text(encoding="utf-8")
    i = text.index("const DATA = ") + len("const DATA = ")
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
                if depth == 0: break
        j += 1
    return json.loads(text[start:j + 1])


def priraz_kod(popis, kategorie, kody, fallback, lock):
    if kategorie in lock:
        return fallback[kategorie]
    n = norm(popis)
    for k in kody:
        for kw in k.get("klicova_slova", []) or []:
            if kw and norm(kw) in n:
                return k["kod"]
    return fallback.get(kategorie, "ostatni")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", type=Path, default=DEF_ORIGINAL)
    ap.add_argument("--soukroma-zona", type=Path, default=DEF_SOUKROMA)
    ap.add_argument("--data", type=Path, default=DEF_DATA)
    args = ap.parse_args()
    if not args.original.exists():
        sys.exit(f"Originál nenalezen: {args.original}")

    cis = yaml.safe_load(DEF_CISLENIK.read_text(encoding="utf-8"))
    kody = cis["kody"]
    oznaceni = {k["kod"]: k["oznaceni"] for k in kody}
    fallback = cis["fallback_dle_kategorie"]
    lock = set(cis.get("kategorie_lock", []))
    zas = yaml.safe_load(DEF_ZASAHY.read_text(encoding="utf-8"))
    zasahy = zas["zasahy"]
    obecni_vyjimky = set(zas.get("ponechano_obecni_majetek", []))
    prav = yaml.safe_load(DEF_PRAVIDLA.read_text(encoding="utf-8"))
    whitelist = {norm(x) for x in prav["detekce"]["vyjimky_bez_allowlistu"]["seznam"]}

    raw = args.original.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    zapisy = nacti_zapisy(args.original)

    privatni = []
    for z in zapisy:
        rok = int(z["y"])
        den, mesic, _ = (z["dt"].split(".") + ["", "", ""])[:3]
        castka_hal = int(round(float(z["net"]) * 100))
        popis = z.get("p", "") or ""
        zasah = zasahy.get(popis)
        popis_verejny = zasah["verejny"] if zasah else popis
        privatni.append({
            "ucetni_rok": rok, "mesic": int(mesic),
            "den": int(den) if den.isdigit() else None, "doklad": z.get("doc", ""),
            "castka_hal": castka_hal, "kategorie": z["c"],
            "popis_original": popis, "popis_verejny": popis_verejny,
            "anonymizovano": bool(zasah and zasah["typ"] == "osobni_udaj"),
            "zasah_typ": zasah["typ"] if zasah else None,
            "kod": priraz_kod(popis, z["c"], kody, fallback, lock),
        })

    # ── deterministické veřejné ID bez vazby na datum ───────────────────
    verejne = []
    for rok in sorted({p["ucetni_rok"] for p in privatni}):
        v = [p for p in privatni if p["ucetni_rok"] == rok]
        v.sort(key=lambda p: (p["mesic"], p["kategorie"], p["castka_hal"], p["popis_verejny"]))
        for i, p in enumerate(v, 1):
            verejne.append({
                "id": f"518-{rok}-{i:04d}", "ucetni_rok": rok, "mesic": p["mesic"],
                "castka_hal": p["castka_hal"], "kategorie": p["kategorie"],
                "popis_verejny": p["popis_verejny"], "anonymizovano": p["anonymizovano"],
                "zdroj_id": ZDROJ_ID, "obdobi_stav": "uzavrene",
            })

    # ── POJISTKA ────────────────────────────────────────────────────────
    problemy = []
    for popis in {p["popis_verejny"] for p in verejne}:
        for kod_pii, rx in TVRDE_PII.items():
            if rx.search(popis) and popis not in obecni_vyjimky:
                problemy.append(f"tvrdé PII ({kod_pii}) v: {popis!r}")
        for w in velka_slova(popis):
            if norm(w) not in whitelist and popis not in obecni_vyjimky:
                problemy.append(f"neschválené velké slovo {w!r} v: {popis!r}")
    if problemy:
        sys.exit("STOP: veřejný výstup neprošel pojistkou:\n  " + "\n  ".join(sorted(set(problemy))))

    # ── veřejné soubory ─────────────────────────────────────────────────
    args.data.mkdir(parents=True, exist_ok=True)
    (args.data / "ucet-518-polozky-public.json").write_text(
        json.dumps({"zdroj_id": ZDROJ_ID, "polozky": verejne}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    with (args.data / "ucet-518-polozky-public.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "ucetni_rok", "mesic", "castka_hal", "kategorie",
                    "popis_verejny", "anonymizovano", "zdroj_id", "obdobi_stav"])
        for p in verejne:
            w.writerow([p["id"], p["ucetni_rok"], p["mesic"], p["castka_hal"], p["kategorie"],
                        p["popis_verejny"], int(p["anonymizovano"]), p["zdroj_id"], p["obdobi_stav"]])
    (args.data / "zdroje.json").write_text(json.dumps({"zdroje": [{
        "id": ZDROJ_ID, "nazev": "Účetní detail účtu 518 za roky 2022–2025",
        "puvod": "Obec Prštice, odpověď na žádost dle zákona č. 106/1999 Sb.",
        "vykaz": "Deník účtu 518 – Ostatní služby", "obdobi": "2022–2025",
        "poznamka": "Roční součty souhlasí s výkazem zisku a ztráty. Dodavatelé v detailu nejsou uvedeni. "
                    "Původní popisy obce jsou zachovány; anonymizovány jen popisy s osobním údajem.",
    }]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ── soukromé soubory ────────────────────────────────────────────────
    args.soukroma_zona.mkdir(parents=True, exist_ok=True)
    (args.soukroma_zona / "ucet-518-privatni.json").write_text(json.dumps({
        "zdroj_id": ZDROJ_ID, "sha256_originalu": sha, "pocet_zapisu": len(privatni),
        "zapisy": privatni}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    soucty = {r: sum(p["castka_hal"] for p in privatni if p["ucetni_rok"] == r) / 100
              for r in sorted({p["ucetni_rok"] for p in privatni})}
    napsat_report(args.soukroma_zona / "qa-report-518-private.html",
                  privatni, zasahy, obecni_vyjimky, oznaceni, kody, soucty, sha)

    zmeneno = sum(1 for p in privatni if p["zasah_typ"])
    print(f"Zpracováno {len(privatni)} zápisů, SHA-256 {sha[:16]}…")
    print("Roční součty (Kč):", {r: f"{v:,.2f}" for r, v in soucty.items()})
    print(f"Původní popis zachován u {len(privatni)-zmeneno} zápisů; zásah u {zmeneno} "
          f"({sum(1 for p in privatni if p['anonymizovano'])} anonymizace, "
          f"{sum(1 for p in privatni if p['zasah_typ']=='cislo_dokladu')} číslo dokladu).")
    print("✓ pojistka prošla — žádný neschválený osobní údaj ani velké slovo.")


def napsat_report(cesta, privatni, zasahy, obecni_vyjimky, oznaceni, kody, soucty, sha):
    import collections, html
    e = html.escape
    zmeny = [p for p in privatni if p["zasah_typ"]]
    out = ["<!doctype html><meta charset=utf-8><title>QA report účet 518</title>",
           "<style>body{font:15px/1.6 system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#1a1a1a}"
           "table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:14px}"
           "th,td{border:1px solid #ccc;padding:5px 9px;text-align:left;vertical-align:top}"
           "th{background:#f0f0f0}del{color:#a00}ins{color:#070;text-decoration:none;background:#eaf7ea}"
           ".num{text-align:right;font-variant-numeric:tabular-nums}code{background:#f4f4f4;padding:1px 4px}"
           "details>summary{cursor:pointer;font-weight:600;margin:.5rem 0}</style>"]
    out.append("<h1>Kontrolní report — účet 518</h1>")
    out.append("<p><strong>SOUKROMÝ dokument.</strong> Ukazuje, co přesně se změnilo oproti "
               "původním popisům obce. Obsahuje původní texty se jmény — nepatří na web.</p>")
    out.append(f"<p>Zdroj SHA-256: <code>{e(sha)}</code> · zápisů: {len(privatni)} · "
               f"změněno: {len(zmeny)} · beze změny: {len(privatni)-len(zmeny)}</p>")
    out.append("<h2>Roční součty</h2><table><tr><th>Rok</th><th class=num>Součet (Kč)</th></tr>"
               + "".join(f"<tr><td>{r}</td><td class=num>{v:,.2f}</td></tr>" for r, v in soucty.items())
               + "</table>")

    out.append(f"<h2>Všechny anonymizační zásahy ({len(zmeny)})</h2>")
    out.append("<p>Jediná místa, kde se veřejný popis liší od původního. Vše ostatní jde na web "
               "v původním znění.</p>")
    out.append("<table><tr><th>Původní popis obce</th><th>Veřejný popis</th><th>Typ</th><th class=num>×</th></tr>")
    seen = {}
    for p in zmeny:
        seen.setdefault(p["popis_original"], {"v": p["popis_verejny"], "t": p["zasah_typ"], "n": 0})
        seen[p["popis_original"]]["n"] += 1
    for orig, d in sorted(seen.items()):
        typ = "osobní údaj" if d["t"] == "osobni_udaj" else "číslo dokladu"
        out.append(f"<tr><td><del>{e(orig)}</del></td><td><ins>{e(d['v'])}</ins></td>"
                   f"<td>{typ}</td><td class=num>{d['n']}</td></tr>")
    out.append("</table>")

    if obecni_vyjimky:
        out.append("<h2>Ponecháno beze změny (obecní majetek)</h2><ul>"
                   + "".join(f"<li>{e(x)}</li>" for x in sorted(obecni_vyjimky)) + "</ul>")

    # analytická témata (interní seskupení pro rozklad 1.7)
    poradi = [k["kod"] for k in kody]
    per = collections.defaultdict(lambda: {"n": 0, "hal": 0})
    for p in privatni:
        per[p["kod"]]["n"] += 1; per[p["kod"]]["hal"] += p["castka_hal"]
    out.append("<details><summary>Analytická témata pro rozklad změn (interní, úkol 1.7)</summary>")
    out.append("<p>Tato témata se ve veřejných datech NEzobrazují jako popis — slouží jen k seskupení "
               "při výpočtu, co tvořilo meziroční rozdíl.</p><table>"
               "<tr><th>Téma</th><th>Označení</th><th class=num>Zápisů</th><th class=num>Součet Kč</th></tr>")
    for kod in poradi:
        if kod in per:
            out.append(f"<tr><td><code>{e(kod)}</code></td><td>{e(oznaceni[kod])}</td>"
                       f"<td class=num>{per[kod]['n']}</td><td class=num>{per[kod]['hal']/100:,.2f}</td></tr>")
    out.append("</table></details>")
    Path(cesta).write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
