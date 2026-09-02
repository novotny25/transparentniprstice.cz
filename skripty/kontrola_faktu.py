#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kontrola publikovaných tvrzení (PLAN.md úkoly 2.8 a 4.3, ZADANI P-19).

Registr všech skutkových tvrzení, která web tvrdí navenek. U každého je uvedeno:
  * text tvrzení tak, jak ho čtenář uvidí,
  * typ (zdroj / výpočet / autorské zařazení / nezjištěno),
  * kde se na webu vyskytuje,
  * a hlavně KONTROLA — funkce, která hodnotu znovu spočítá z dat v `data/`.

Skript neporovnává text webu s pamětí autora, ale **přepočítává čísla ze
zdrojových souborů**. Když se hodnota v datech změní, kontrola spadne.
Navíc ověřuje, že tvrzené číslo v HTML skutečně je (ať web netvrdí něco jiného,
než co je v registru).

Spuštění: python3 skripty/kontrola_faktu.py
"""
import os, re, sys, json, unicodedata

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(WEB, "data")
STRANKY = ["index.html", "rizeni.html", "jak-to-vime.html"]


def nacti(jmeno):
    return json.load(open(os.path.join(DATA, jmeno), encoding="utf-8"))


D = {j[:-5]: nacti(j) for j in os.listdir(DATA) if j.endswith(".json")}


def html_text():
    """Spojený viditelný text všech stránek (bez skriptů a stylů)."""
    cely = []
    for s in STRANKY:
        p = os.path.join(WEB, "web", s)
        if not os.path.exists(p):
            continue
        t = open(p, encoding="utf-8").read()
        # datové bloky ponecháváme — web z nich čísla vykresluje JavaScriptem,
        # takže hodnota v nich JE hodnotou, kterou čtenář uvidí
        t = re.sub(r'<script(?! type="application/json").*?</script>', " ", t, flags=re.S)
        t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
        cely.append(re.sub(r"<[^>]+>", " ", t))
    return " ".join(cely)


def normalizuj(s):
    """Sjednotí mezery (i pevné) a desetinnou čárku, aby šla čísla porovnat."""
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"[\s  ]+", " ", s)


HTML = normalizuj(html_text())
# všechna čísla vyskytující se v textu webu, znormalizovaná na celé číslo
CISLA_V_HTML = set()
for m in re.finditer(r"\d[\d ]{0,12}\d|\d", HTML):
    CISLA_V_HTML.add(m.group(0).replace(" ", ""))


def v_html(hodnota, presne=True):
    """Je hodnota na webu opravdu napsaná?"""
    if isinstance(hodnota, float):
        cely = f"{hodnota:.1f}".replace(".", ",")
        return cely in HTML or f"{hodnota:.2f}".replace(".", ",") in HTML
    return str(int(hodnota)) in CISLA_V_HTML if presne else True


# ── registr tvrzení ─────────────────────────────────────────────────────────
# (oblast, tvrzení, typ, funkce vracející (spočítaná hodnota, očekávaná hodnota))
def rozpocet_rok(rok, klic):
    return D["rozpocet"]["roky"][str(rok)][klic]


def obl(rok, nazev):
    for o in D["vydaje-skupiny"]["roky"][str(rok)]["oblasti"]:
        if o["oblast"] == nazev:
            return o["kc"]
    return None


def pol_soucet(rok, kod):
    s = 0
    for o in D["vydaje-skupiny"]["roky"][str(rok)]["oblasti"]:
        for a in o["agendy"]:
            for x in a["polozky"]:
                if x["kod"] == kod:
                    s += x["kc"]
    return s


def par_soucet(rok, pary):
    s = 0
    for o in D["vydaje-skupiny"]["roky"][str(rok)]["oblasti"]:
        for a in o["agendy"]:
            if a["par"] in pary:
                s += a["kc"]
    return s


REGISTR = [
    ("Úvod", "Prštice mají 997 obyvatel (ČSÚ, 1. 1. 2025)", "zdroj",
     lambda: (D["obyvatele"]["obyvatele"]["2025"], 997)),
    ("Úvod", "Počet obyvatel vzrostl z 931 (2015) na 997 (2025)", "zdroj",
     lambda: (D["obyvatele"]["obyvatele"]["2015"], 931)),
    ("Úvod", "Průměrný věk 43,3 roku", "zdroj",
     lambda: (D["srovnani-obci"]["vek"]["prstice"], 43.3)),
    ("Úvod", "Průměrný věk okresu Brno-venkov 41,65", "výpočet",
     lambda: (D["srovnani-obci"]["vek"]["okres"], 41.65)),
    ("Úvod", "Prштice jsou 30. nejstarší z 187 obcí okresu", "výpočet",
     lambda: (D["srovnani-obci"]["vek"]["poradi_prstic_od_nejstarsiho"], 30)),
    ("Úvod", "Rozpočet na obyvatele 24 829 Kč — 5. nejnižší ze 17", "výpočet",
     lambda: (D["srovnani-obci"]["rozpocet"]["prstice_na_obyvatele_kc"], 24829)),
    ("Úvod", "Medián srovnávané skupiny 27 608 Kč", "výpočet",
     lambda: (D["srovnani-obci"]["rozpocet"]["median_kc"], 27608)),

    ("Rozpočet", "Příjmy 2025 = 28 380 971 Kč", "zdroj",
     lambda: (round(rozpocet_rok(2025, "prijmy_celkem_kc")), 28380971)),
    ("Rozpočet", "Výdaje 2025 = 22 484 603 Kč", "zdroj",
     lambda: (round(rozpocet_rok(2025, "vydaje_celkem_kc")), 22484603)),
    ("Rozpočet", "Výdaje 2023 = 34 439 399 Kč (nejvyšší rok)", "zdroj",
     lambda: (round(rozpocet_rok(2023, "vydaje_celkem_kc")), 34439399)),
    ("Rozpočet", "Chod úřadu a zastupitelstvo 2025 = 6 926 488 Kč", "autorské zařazení",
     lambda: (obl(2025, "Chod úřadu a zastupitelstvo"), 6926488)),
    ("Rozpočet", "Chod úřadu 2023 = 13 555 386 Kč (v tom 8 mil. budova)", "autorské zařazení",
     lambda: (obl(2023, "Chod úřadu a zastupitelstvo"), 13555386)),
    ("Rozpočet", "Zámek a památky 2025 = 4 593 683 Kč", "autorské zařazení",
     lambda: (obl(2025, "Zámek a památky"), 4593683)),

    ("Změny", "Právní a poradenské služby (5166) 2025 = 924 tis. Kč", "zdroj",
     lambda: (pol_soucet(2025, "5166"), 923508)),
    ("Změny", "Úroky z úvěrů (5141) 2025 = 445 tis. Kč", "zdroj",
     lambda: (pol_soucet(2025, "5141"), 444885)),
    ("Změny", "Příspěvek škole (5331) 2025 = 1 376 tis. Kč", "zdroj",
     lambda: (pol_soucet(2025, "5331"), 1376000)),
    ("Změny", "Odpady 2025 = 1 739 736 Kč", "autorské zařazení",
     lambda: (par_soucet(2025, {"3721", "3722", "3725", "3726"}), 1739736)),
    ("Změny", "Voda a odpadní vody 2025 = 2 505 093 Kč", "autorské zařazení",
     lambda: (par_soucet(2025, {"2321", "2310"}), 2505093)),

    ("Účet 518", "Právní služby 2022–2025 = 2 094 182 Kč", "autorské zařazení",
     lambda: (round(D["ucet-518-rozklad"]["souhrn"]["pravni_sluzby_2022_2025_kc"]), 2094182)),
    ("Účet 518", "GDPR 2025 = 272 250 Kč", "zdroj",
     lambda: (round(D["ucet-518-rozklad"]["souhrn"]["gdpr_2025_kc"]), 272250)),
    ("Účet 518", "Účet 518 v roce 2023 = 5 823 019 Kč (vrchol)", "zdroj",
     lambda: (D["vykazy-rady"]["rady"]["ucet_518"]["hodnoty_kc"]["2023"], 5823019)),
    ("Účet 518", "Nárůst účtu 518 2015→2025 o 138,6 %", "výpočet",
     lambda: (D["vykazy-rady"]["ukazatele_518"]["zmena_2015_2025_pct"], 138.6)),

    ("Účet 511", "Účet 511 za 2020–2025 = 24,4 mil. Kč", "výpočet",
     lambda: (sum(D["vykazy-rady"]["rady"]["ucet_511"]["hodnoty_kc"][str(r)]
                  for r in range(2020, 2026)), 24387419)),
    ("Účet 511", "Účet 511 v roce 2022 = 7 813 997 Kč (nejvyšší)", "zdroj",
     lambda: (D["vykazy-rady"]["rady"]["ucet_511"]["hodnoty_kc"]["2022"], 7813997)),

    ("Řízení", "Tři pravomocná rozhodnutí ÚOHS", "zdroj",
     lambda: (len([r for r in D["rizeni"]["rizeni"] if r["typ"] == "spravni"]), 3)),
    ("Řízení", "Pokuty ÚOHS celkem 11 000 Kč", "výpočet",
     lambda: (sum(r.get("pokuta_kc", 0) for r in D["rizeni"]["rizeni"]), 11000)),

    ("Zdroje a doklady", "Podáno 10 žádostí a podání", "zdroj",
     lambda: (len(D["zadosti-106"]["zadosti"]), 10)),
    ("Zdroje a doklady", "Zveřejněno 11 anonymizovaných dokumentů", "zdroj",
     lambda: (len(D["dokumenty"]["dokumenty"]), 11)),
]


def main():
    print(f"REGISTR PUBLIKOVANÝCH TVRZENÍ — {len(REGISTR)} položek\n")
    ok = chyby = mimo_html = 0
    podle_typu = {}
    for oblast, tvrzeni, typ, fn in REGISTR:
        podle_typu[typ] = podle_typu.get(typ, 0) + 1
        try:
            spocteno, ocekavano = fn()
        except Exception as e:
            print(f"  [CHYBA]  {oblast:11} {tvrzeni[:56]:58} — {e}")
            chyby += 1
            continue
        sedi = (abs(spocteno - ocekavano) < 0.05 if isinstance(ocekavano, float)
                else abs(spocteno - ocekavano) <= 1)
        na_webu = v_html(ocekavano)
        if not sedi:
            print(f"  [FAIL]   {oblast:11} {tvrzeni[:56]:58} data={spocteno} ≠ registr={ocekavano}")
            chyby += 1
        elif not na_webu:
            print(f"  [POZOR]  {oblast:11} {tvrzeni[:56]:58} hodnota {ocekavano} není v textu webu")
            mimo_html += 1
        else:
            ok += 1
    print(f"\n{'─' * 76}")
    print("  podle typu: " + " | ".join(f"{k}: {v}" for k, v in sorted(podle_typu.items())))
    print(f"  ověřeno proti datům i textu webu: {ok}  |  neshoda s daty: {chyby}"
          f"  |  v datech OK, ale nenalezeno v textu: {mimo_html}")
    if chyby:
        sys.exit("❌ NEPROŠLO — tvrzení nesedí na zdrojová data.")
    print("✅ Všechna tvrzení sedí na zdrojová data.")
    if mimo_html:
        print("   (POZOR položky nejsou chyba: číslo je správné, jen se na webu píše "
              "zaokrouhleně nebo slovy — projít ručně.)")


if __name__ == "__main__":
    main()
