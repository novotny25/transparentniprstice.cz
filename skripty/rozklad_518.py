#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rozklad meziročních změn účtu 518 (úkol 1.7).

Ze soukromého extraktu (ucet-518-privatni.json) sestaví „co vytvořilo
meziroční rozdíl" po tématech pro dvojice let 2022→2023, 2023→2024,
2024→2025. Odpovídá na otázku „co tvoří rozdíl", ne bez dokladů na
„proč obec službu objednala".

Zásady (schváleno Petrem, úkol 1.7):
  - Storna/opravy se přiřazují k tématu opravovaného dokladu.
  - Storno 2025 −309 366 Kč patří k ČOV (autorské rozhodnutí; doklad
    v účtu 518 nesedí, ale věcně jde o opravu nákladu na ČOV).
  - Pojištění obecních budov je SAMOSTATNÉ téma, ne součást zámku
    (kryje i školu, úřad a další budovy).
  - Doprava kontejnerů zůstává v odpadech (tak to obec zaúčtovala).

Výstup (veřejné, agregát bez PII):
  data/ucet-518-rozklad.json
"""
import argparse, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACT = Path("/home/user/0_PACT/0_Projects/4_PRŠTICE")
DEF_PRIV = PACT / "2026_08_21 TransparentniPrstice.cz" / "soukroma-zona" / "ucet-518-privatni.json"
DEF_OUT = REPO / "data" / "ucet-518-rozklad.json"

# kód → téma rozkladu (laické názvy)
TEMA = {}
for k in ["zamek-jerab", "zamek-strecha-fasada", "zamek-leseni-plosina",
          "zamek-statika", "zamek-plyn-kotle", "zamek-ostatni"]:
    TEMA[k] = "Zámek – opravy a údržba budovy"
for k in ["odpady-svoz", "odpady-bio", "odpady-nebezpecny", "odpady-ulozeni", "odpady-ostatni"]:
    TEMA[k] = "Odpady"
for k in ["voda-dozor", "voda-kalkulace", "voda-rozbor", "voda-deratizace",
          "voda-pripojky", "voda-poradenstvi", "voda-geodet", "voda-ostatni", "plyn-pripojky"]:
    TEMA[k] = "Vodovod a kanalizace (provoz)"
for k in ["telekom-tel-net", "telekom-telefony", "telekom-internet", "telekom-ostatni"]:
    TEMA[k] = "Telefony a internet"
for k in ["it-software", "spravni-agenda", "certifikaty-podpisy", "tech-pomoc",
          "kancelar-material", "kopirovani-tisk", "datovy-trezor"]:
    TEMA[k] = "Správa a IT"
for k in ["sdh-vozidla", "sdh-vystroj"]:
    TEMA[k] = "Hasiči (SDH)"
TEMA.update({
    "cov-prevzata": "ČOV / převzatá odpadní voda",
    "pravni-sluzby": "Právní služby",
    "gdpr-poverenec": "GDPR – pověřenec",
    "pojisteni-budovy": "Pojištění obecních budov",
    "bankovni-poplatky": "Bankovní poplatky",
    "postovne": "Poštovné",
    "rozhlas-osa": "Rozhlas a OSA",
    "zelen": "Veřejná zeleň",
    "vozidla-obce": "Obecní vozidla",
    "les-drevo": "Obecní les",
    "knihovna": "Knihovna",
    "skolka-uver": "Mateřská škola – úvěr",
    "zs-udrzba": "Základní škola – opravy",
    "geometr-kn": "Geometrie a katastr",
    "pozemky-najem": "Pozemky – nájem",
    "detske-hriste": "Dětské hřiště",
    "revize-hasici-pristroje": "Revize hasicích přístrojů",
    "hrbitov-pohrebnictvi": "Hřbitov a pohřebnictví",
    "kultura-akce": "Kultura a akce",
    "zpravodaj": "Obecní zpravodaj",
    "skoleni": "Školení",
    "cestovne": "Cestovné",
    "danovy-poradce": "Daňový poradce",
    "bozp": "BOZP",
    "notarske": "Notářské služby",
    "udrzba-obce": "Údržba obce",
})
TEMA_DEFAULT = "Ostatní"

# doklad storna → téma (autorské přeřazení, kde doklad v 518 nesedí)
STORNO_OVERRIDE = {"25-005-00038": "ČOV / převzatá odpadní voda"}


def tema_kod(kod):
    return TEMA.get(kod, TEMA_DEFAULT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--priv", type=Path, default=DEF_PRIV)
    ap.add_argument("--out", type=Path, default=DEF_OUT)
    args = ap.parse_args()
    if not args.priv.exists():
        sys.exit(f"Soukromý extrakt nenalezen: {args.priv}\n(Spusť nejdřív extrakce_518.py.)")

    zapisy = json.loads(args.priv.read_text(encoding="utf-8"))["zapisy"]
    doc2tema = {z["doklad"]: tema_kod(z["kod"]) for z in zapisy if z["doklad"]}

    # téma každého zápisu (se zohledněním storen)
    def tema_zapisu(z):
        m = re.search(r"Oprava dokladu číslo (\S+)", z["popis_original"])
        if m:
            if z["doklad"] in STORNO_OVERRIDE:
                return STORNO_OVERRIDE[z["doklad"]]
            ref = m.group(1)
            return doc2tema.get(ref, "Opravy dokladů (nezařazeno)")
        return tema_kod(z["kod"])

    roky = sorted({z["ucetni_rok"] for z in zapisy})
    sums = {}  # tema -> rok -> hal
    for z in zapisy:
        t = tema_zapisu(z)
        sums.setdefault(t, {}).setdefault(z["ucetni_rok"], 0)
        sums[t][z["ucetni_rok"]] += z["castka_hal"]

    def hodnota(t, rok):
        return sums.get(t, {}).get(rok, 0)

    # rozklady pro dvojice let
    rozklady = []
    for a, b in [(2022, 2023), (2023, 2024), (2024, 2025)]:
        celkem = sum(hodnota(t, b) - hodnota(t, a) for t in sums)
        prispevky = []
        for t in sums:
            zmena = hodnota(t, b) - hodnota(t, a)
            if zmena != 0:
                prispevky.append({
                    "tema": t,
                    "hodnota_pred_hal": hodnota(t, a),
                    "hodnota_po_hal": hodnota(t, b),
                    "zmena_hal": zmena,
                    "podil_na_zmene_pct": round(zmena / celkem * 100, 1) if celkem else None,
                })
        prispevky.sort(key=lambda x: -abs(x["zmena_hal"]))
        rozklady.append({"z_roku": a, "do_roku": b, "celkova_zmena_hal": celkem,
                         "prispevky": prispevky})

    # jeřáb jako sledovaná podpoložka zámku
    jerab = {r: sum(z["castka_hal"] for z in zapisy
                    if z["kod"] == "zamek-jerab" and z["ucetni_rok"] == r) for r in roky}

    out = {
        "zdroj_id": "detail-518-2022-2025",
        "jednotka": "haléře (celé Kč × 100)",
        "poznamka": "Rozklad odpovídá na otázku, co tvoří meziroční rozdíl, "
                    "nikoli bez dalších dokladů, proč obec službu objednala. "
                    "Běžné ceny, bez odečtení inflace.",
        "zasady_prirazeni": [
            "Storna a opravy jsou přiřazeny k tématu opravovaného dokladu.",
            "Storno 2025 −309 366 Kč patří k ČOV (autorské rozhodnutí).",
            "Pojištění obecních budov je samostatné téma, ne součást zámku.",
            "Doprava kontejnerů zůstává v odpadech.",
        ],
        "rocni_soucty_hal": {str(r): sum(hodnota(t, r) for t in sums) for r in roky},
        "jerab_hal": {str(r): jerab[r] for r in roky},
        "rozklady": rozklady,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Zapsáno {args.out}")
    for r in rozklady:
        print(f"\n{r['z_roku']}→{r['do_roku']}: celkem {r['celkova_zmena_hal']/100:+,.2f} Kč")
        for p in r["prispevky"][:6]:
            print(f"   {p['zmena_hal']/100:>+13,.2f}  {p['podil_na_zmene_pct']:>6}%  {p['tema']}")


if __name__ == "__main__":
    main()
