#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vloží sanitizovaná data z `data/` do webu `web/index.html`.

Web je jediný soubor bez závislostí (otevře se i z disku), data ale zůstávají
oddělená v `data/*.json` — tento skript je jen přenese do označených bloků
<script type="application/json" id="...">. Po každé změně dat stačí spustit
znovu; do HTML se ručně nesahá (P-12, P-18).

Spuštění: python3 skripty/vlozit_data.py
"""
import os, re, sys, json

WEB  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIV = os.path.expanduser("~/Developer/transparentniprstice-private")
M2026 = os.path.join(PRIV, "zdroje", "monitor-2026")
DATA = os.path.join(WEB, "data")
HTML = os.path.join(WEB, "web", "index.html")
STRANKY = {                       # soubor -> {id bloku: název datového souboru}
    "index.html":      {"d-vydaje": None, "d-prijmy": None, "d-rady": None,
                        "d-temata": None, "d-vybrane": None, "d-518": None,
                        "d-srovnani": "srovnani-obci.json",
                        "d-obyvatele": "obyvatele.json"},
    "rizeni.html":     {"d-rizeni": "rizeni.json", "d-vybrane": None},
    "pro-dalsi-obce.html": {"d-navod": "navod.json"},
    "jak-to-vime.html": {"d-zadosti": "zadosti-106.json",
                         "d-chronologie": "chronologie.json",
                         "d-dokumenty": "dokumenty.json"},
}


def kc(x):
    """Zaokrouhlí na celé koruny (web nezobrazuje haléře)."""
    return int(round(x))


def blok_vydaje():
    d = json.load(open(os.path.join(DATA, "vydaje-skupiny.json"), encoding="utf-8"))
    return {"roky": [str(r) for r in d["meta"]["roky"]],
            "data": {r: {"celkem": kc(y["celkem_kc"]),
                         "skupiny": [{"n": o["oblast"], "kc": kc(o["kc"]), "barva": o["barva"],
                                      "popis": o["popis"], "k": kc(o["kapitalove_kc"]),
                                      "kk": "o|" + o["oblast"],
                                      "a": [{"n": a["nazev"], "kc": kc(a["kc"]), "k": kc(a["kapitalove_kc"]),
                                             "kk": "a|" + a["par"],
                                             "p": [[x["nazev"], kc(x["kc"]), f"p|{a['par']}|{x['kod']}"]
                                                   for x in a["polozky"]]}
                                            for a in o["agendy"]]}
                                     for o in y["oblasti"]]}
                     for r, y in d["roky"].items()}}


def blok_prijmy():
    d = json.load(open(os.path.join(DATA, "prijmy-skupiny.json"), encoding="utf-8"))
    return {"roky": [str(r) for r in d["meta"]["roky"]],
            "data": {r: {"celkem": kc(y["celkem_kc"]),
                         "skupiny": [{"n": s["skupina"], "kc": kc(s["kc"]), "barva": s["barva"],
                                      "popis": s["popis"], "kk": "s|" + s["skupina"],
                                      "p": [[x["nazev"], kc(x["kc"]), "q|" + x["kod"]]
                                            for x in s["polozky"]]}
                                     for s in y["skupiny"]]}
                     for r, y in d["roky"].items()}}


def blok_rady():
    """Časové řady pro každý řádek rozpadu — aby šel u položky rozbalit vývoj.

    Klíče:  o|<oblast>            a|<paragraf>            p|<paragraf>|<položka>
            s|<skupina příjmů>    q|<položka příjmů>
    """
    v = json.load(open(os.path.join(DATA, "vydaje-skupiny.json"), encoding="utf-8"))
    pr = json.load(open(os.path.join(DATA, "prijmy-skupiny.json"), encoding="utf-8"))
    roky = [str(r) for r in v["meta"]["roky"]]
    rady = {}

    def pridej(klic, rok, castka):
        rada = rady.setdefault(klic, {r: 0 for r in roky})
        rada[rok] = rada.get(rok, 0) + kc(castka)

    for rok, y in v["roky"].items():
        for o in y["oblasti"]:
            pridej("o|" + o["oblast"], rok, o["kc"])
            for a in o["agendy"]:
                pridej("a|" + a["par"], rok, a["kc"])
                for x in a["polozky"]:
                    pridej(f"p|{a['par']}|{x['kod']}", rok, x["kc"])
    for rok, y in pr["roky"].items():
        for sk in y["skupiny"]:
            pridej("s|" + sk["skupina"], rok, sk["kc"])
            for x in sk["polozky"]:
                pridej("q|" + x["kod"], rok, x["kc"])

    return {"roky": roky, "rady": {k: [r[y] for y in roky] for k, r in rady.items()}}


# Témata sekce „Zajímavé změny nákladů". Každé se počítá z už ověřených dat;
# výběr témat je autorský, čísla nikoli.
TEMATA = [
 {"id": "pravni", "nadpis": "Právní a poradenské služby", "barva": "#e63562",
  "pol": ["5166"],
  "popis": "Výdaje na konzultační, poradenské a právní služby rostou nepřetržitě "
           "od roku 2020 — každý rok jsou vyšší než v tom předchozím. V roce 2025 na ně "
           "z rozpočtu šlo víc než trojnásobek toho, co na hasiče.",
  "nevime": "Z rozpočtu nevyčteme, čeho se služby týkají, kdo je dodavatelem ani jaká je "
            "sjednaná sazba. O detail smluv byla obec požádána; krajský úřad 19. 8. 2026 "
            "obci nařídil žádost vyřídit."},
 {"id": "uroky", "nadpis": "Úroky z úvěrů", "barva": "#af52de",
  "pol": ["5141"],
  "popis": "Kolik obec ročně zaplatí na úrocích. Nárůst souvisí s úvěrem, který obec "
           "čerpala v roce 2023 na pořízení nemovitosti; úroky se pak projevují i v rozpočtech "
           "dalších let. Samotný nákup může být pro obec dobrý krok — o tom, "
           "jestli se úvěr vyplatil, rozhoduje využití pořízeného majetku, ne výše úroků.",
  "nevime": "Úroková sazba, doba splácení ani podmínky úvěru nejsou z rozpočtu patrné."},
 {"id": "skola", "nadpis": "Příspěvek základní a mateřské škole", "barva": "#f5a524",
  "pol": ["5331"], "par": ["3113", "3111"],
  "popis": "Provozní příspěvek, který obec posílá základní a mateřské škole. Roste každý rok. "
           "Podpora školy patří k tomu, co obec dělat má — pokud jsou peníze vynaložené "
           "hospodárně, je rostoucí příspěvek spíš dobrá zpráva než problém.",
  "odhad": False,
  "nevime": "Rozpočet neukazuje, co konkrétně růst příspěvku pokrývá (energie, mzdy, provoz)."},
 {"id": "voda", "nadpis": "Voda a odpadní vody", "barva": "#0f9fbd",
  "par": ["2321", "2310"],
  "popis": "Výdaje na pitnou vodu, kanalizaci a čištění odpadních vod prudce vzrostly "
           "v roce 2023. Za první pololetí 2026 jsou přitom náklady vyšší než za celý "
           "rok 2025 — pokud se tempo udrží, čeká nás další citelný nárůst.",
  "nevime": "Co nárůst v roce 2023 způsobilo a jak se náklady promítají do stočného, "
            "z rozpočtu není patrné."},
]


def data_2026h1():
    """Skutečnost za leden–červen 2026 z MONITORu (rozklikávací rozpočet).
    Vrací (položky, paragrafy). Když soubory chybí, vrátí prázdno a 2026 se nezobrazí."""
    def strom(cesta):
        if not os.path.exists(cesta):
            return {}
        d = json.load(open(cesta, encoding="utf-8"))
        out = {}
        def w(n):
            c = str(n.get("code") or "").strip()
            if len(c) == 4 and c.isdigit():
                out[c] = (n.get("budget") or {}).get("reality", 0)
            for ch in n.get("children") or []:
                w(ch)
        w(d)
        return out
    return (strom(os.path.join(M2026, "souhrnny-2606.json")),
            strom(os.path.join(M2026, "odvetvovy-2606.json")))


def blok_temata():
    """Řady pro sekci „Zajímavé změny nákladů" + odpady (výdaje vs. poplatky)."""
    v = json.load(open(os.path.join(DATA, "vydaje-skupiny.json"), encoding="utf-8"))
    pr = json.load(open(os.path.join(DATA, "prijmy-skupiny.json"), encoding="utf-8"))
    roky = [str(r) for r in v["meta"]["roky"]]

    def vydaj(rok, pol=None, par=None):
        s = 0
        for o in v["roky"][rok]["oblasti"]:
            for a in o["agendy"]:
                if par and a["par"] not in par:
                    continue
                for x in a["polozky"]:
                    if pol and x["kod"] not in pol:
                        continue
                    s += x["kc"]
        return kc(s)

    def prijem(rok, pol):
        return kc(sum(x["kc"] for sk in pr["roky"][rok]["skupiny"]
                      for x in sk["polozky"] if x["kod"] in pol))

    pol26, par26 = data_2026h1()

    def h1(pol=None, par=None):
        """Hodnota za 1. pololetí 2026 (None = data nejsou)."""
        if not pol26 and not par26:
            return None
        if par:
            return kc(sum(par26.get(x, 0) for x in par))
        return kc(sum(pol26.get(x, 0) for x in pol))

    out = []
    for t in TEMATA:
        rada = [vydaj(r, t.get("pol"), t.get("par")) for r in roky]
        z = {"id": t["id"], "n": t["nadpis"], "barva": t["barva"], "popis": t["popis"],
             "nevime": t["nevime"], "rada": rada}
        # u témat vázaných na paragraf bereme paragrafy, jinak položky
        v26 = h1(par=t["par"]) if t.get("par") and not t.get("pol") else h1(pol=t.get("pol"))
        if v26:
            z["h1"] = v26
            z["odhad"] = t.get("odhad", True)   # smí se dopočítat na celý rok?
        out.append(z)

    # odpady mají navíc druhou řadu — kolik z výdajů pokryjí poplatky od občanů
    odp_par = ["3721", "3722", "3725", "3726"]
    vyd = [vydaj(r, par=odp_par) for r in roky]
    popl = [prijem(r, {"1340", "1345"}) for r in roky]   # 1340 do 2021, pak 1345
    out.insert(1, {
        "id": "odpady", "n": "Odpadové hospodářství", "barva": "#a2845e",
        "popis": "Výdaje na svoz a zpracování odpadu rostou rychleji než poplatek, "
                 "který za něj platí občané. Rozdíl doplácí obec z ostatních příjmů.",
        "nevime": "Smlouvu se svozovou firmou, ceník, množství odpadu v tunách ani míru "
                  "vytřídění rozpočet neukazuje.",
        "komentar": "Krytí 40 % může působit jako vstřícnost k občanům, podstata je ale "
                    "jinde: tlak na výdaje dál poroste, protože zákonný poplatek za "
                    "skládkování využitelného odpadu se každý rok zvyšuje — až na 1 850 Kč "
                    "za tunu v roce 2029. Sníženou sazbu 500 Kč za tunu platí jen obce, "
                    "které splní zákonné cíle třídění. Pokud obec odpadové hospodářství "
                    "nezefektivní — víc třídit, vyřešit bioodpad — výdaje se budou dál "
                    "zvyšovat a dřív nebo později se promítnou do poplatku pro občany.",
        "kpozn": "Sazby: zákon č. 541/2020 Sb., příloha č. 9. Jde o komentář autora — "
                 "interpretaci, ne doložený závěr.",
        "rada": vyd, "rada2": popl, "l1": "Výdaje obce na odpad", "l2": "Poplatky od občanů",
        "kryti": [round(p / x * 100) if x else 0 for p, x in zip(popl, vyd)],
        **({"h1": h1(par=odp_par), "h1b": h1(pol={"1340", "1345"}), "odhad": True,
            "odhad2": False} if h1(par=odp_par) else {})})

    return {"roky": roky, "temata": out}


def blok_vybrane():
    """Řady pro sekci „Ptáme se na vybrané výdaje" — z účetního deníku 518."""
    r = json.load(open(os.path.join(DATA, "ucet-518-rozklad.json"), encoding="utf-8"))
    kat = r["kategorie_po_letech_kc"]
    roky = ["2022", "2023", "2024", "2025"]

    h1 = {}
    cesta = os.path.join(DATA, "ucet-518-2026H1-public.json")
    if os.path.exists(cesta):
        d26 = json.load(open(cesta, encoding="utf-8"))
        pol = d26["polozky"] if isinstance(d26, dict) and "polozky" in d26 else d26
        for x in pol:
            k = x.get("kategorie", "")
            h1[k] = h1.get(k, 0) + x["castka_haleru"] / 100

    return {
        "roky": roky,
        "gdpr": {"rada": [kc(kat["GDPR / pověřenec"][y]) for y in roky],
                 "h1": kc(h1.get("GDPR / pověřenec", 0)) or None},
        "pravni": {"rada": [kc(kat["Právní služby"][y]) for y in roky],
                   "h1": kc(h1.get("Právní služby", 0)) or None},
        "jerab": {"rada": [kc(r["temata"]["jerab_kc"].get(y, 0)) for y in roky],
                  "mesicni": 33880, "mesicni_bez_dph": 28000, "pocet_plateb": 18,
                  "celkem": kc(sum(r["temata"]["jerab_kc"].values()))},
    }


def blok_518():
    """Roční řada účtu 518 (2015–2025) + rozklad meziročních změn."""
    r = json.load(open(os.path.join(DATA, "vykazy-rady.json"), encoding="utf-8"))
    rz = json.load(open(os.path.join(DATA, "ucet-518-rozklad.json"), encoding="utf-8"))
    h = r["rady"]["ucet_518"]["hodnoty_kc"]
    roky = [str(x) for x in r["meta"]["roky"]]
    u = r["ukazatele_518"]

    # 1. pololetí 2026 z účetního deníku (neúplné období)
    h1 = None
    cesta = os.path.join(DATA, "ucet-518-2026H1-public.json")
    if os.path.exists(cesta):
        d26 = json.load(open(cesta, encoding="utf-8"))
        pol = d26["polozky"] if isinstance(d26, dict) and "polozky" in d26 else d26
        h1 = kc(sum(x["castka_haleru"] for x in pol) / 100)

    zmeny = []
    for klic, popis in (("2022_2023", "Skok nahoru"), ("2023_2024", "Návrat dolů"),
                        ("2024_2025", "Opětovný růst")):
        z = rz["rozklad"][klic]
        hlavni = [p for p in z["prispevky"] if p["nad_5pct"]]
        ostatni = round(z["celkem_kc"] - sum(p["zmena_kc"] for p in hlavni))
        zmeny.append({
            "obdobi": klic.replace("_", " → "), "titulek": popis,
            "celkem": kc(z["celkem_kc"]),
            "polozky": [{"n": p["kategorie"], "kc": kc(p["zmena_kc"]),
                         "pct": round(abs(p["zmena_kc"]) / abs(z["celkem_kc"]) * 100)}
                        for p in hlavni] + [{"n": "Ostatní změny (net)", "kc": ostatni,
                                             "pct": round(abs(ostatni) / abs(z["celkem_kc"]) * 100)}]})

    return {"roky": roky, "hodnoty": [kc(h[y]) for y in roky],
            "h1_2026": h1,
            "klouzavy": [kc(u["klouzavy_prumer_3_kc"][y]) if y in u["klouzavy_prumer_3_kc"] else None
                         for y in roky],
            "zmena_pct": u["zmena_2015_2025_pct"], "cagr": u["cagr_2015_2025_pct"],
            "prumer_start": kc(u["prumer_2015_2017_kc"]), "prumer_konec": kc(u["prumer_2023_2025_kc"]),
            "zmeny": zmeny}


def vloz(html, blok_id, data):
    vzor = re.compile(r'(<script type="application/json" id="%s">)(.*?)(</script>)' % re.escape(blok_id), re.S)
    if not vzor.search(html):
        sys.exit(f"CHYBA: v index.html chybí blok id=\"{blok_id}\"")
    return vzor.sub(lambda m: m.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + m.group(3), html)


def main():
    v, p = blok_vydaje(), blok_prijmy()
    rady, temata, vybrane = blok_rady(), blok_temata(), blok_vybrane()
    hotove = {"d-vydaje": v, "d-prijmy": p, "d-rady": rady,
              "d-temata": temata, "d-vybrane": vybrane, "d-518": blok_518()}

    for soubor, bloky in STRANKY.items():
        cesta = os.path.join(WEB, "web", soubor)
        if not os.path.exists(cesta):
            print(f"  {soubor}: přeskočeno (soubor neexistuje)")
            continue
        html = open(cesta, encoding="utf-8").read()
        vlozeno = []
        for blok_id, zdroj in bloky.items():
            data = hotove[blok_id] if zdroj is None else \
                json.load(open(os.path.join(DATA, zdroj), encoding="utf-8"))
            html = vloz(html, blok_id, data)
            vlozeno.append(blok_id)
        open(cesta, "w", encoding="utf-8").write(html)
        print(f"  {soubor}: {', '.join(vlozeno)}")

    # kontroly součtů
    for nazev, b in (("výdaje", v), ("příjmy", p)):
        for r in b["roky"]:
            y = b["data"][r]
            soucet = sum(g["kc"] for g in y["skupiny"])
            if abs(soucet - y["celkem"]) > 1:
                sys.exit(f"CHYBA: {nazev} {r} — součet skupin {soucet} ≠ celkem {y['celkem']}")
    for r in v["roky"]:
        for g in v["data"][r]["skupiny"]:
            rada = rady["rady"].get("o|" + g["n"])
            i = rady["roky"].index(r)
            if not rada or abs(rada[i] - g["kc"]) > 1:
                sys.exit(f"CHYBA: řada oblasti {g['n']} {r} nesedí")
    print(f"  kontroly: součty {len(v['roky'])} let a {len(rady['rady'])} řad sedí ✓")
    print("HOTOVO — data vložena do všech stránek")


if __name__ == "__main__":
    main()
