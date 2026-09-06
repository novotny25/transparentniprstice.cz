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
DATA = os.path.join(WEB, "data")
HTML = os.path.join(WEB, "web", "index.html")
def esc_html(t):
    return (str(t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def renderuj_aktuality(akt):
    """Pruh aktualit na hlavní stránce — statické HTML, rozbalování řeší
    nativní <details>, žádný JavaScript není potřeba."""
    mesice = ["", "ledna", "února", "března", "dubna", "května", "června",
              "července", "srpna", "září", "října", "listopadu", "prosince"]
    def datum_cz(iso):
        r, m, d = iso.split("-")
        return f"{int(d)}. {mesice[int(m)]} {int(r)}"
    polozky = akt["polozky"][:akt.get("zobrazit", 6)]
    prvni = polozky[0]
    radky = ""
    for a in polozky:
        href = bezpecny_href(a.get("odkaz"))
        odkaz = f' <a href="{esc_html(href)}">více →</a>' if href else ""
        radky += (f'<li><span class="ad">{datum_cz(a["datum"])}</span>'
                  f'<span class="at">{esc_html(a["text"])}{odkaz}</span></li>')
    return (f'<details class="aktuality"><summary><span class="aznak">Aktuálně</span>'
            f'<span class="ateaser"><b>{datum_cz(prvni["datum"])}:</b> {esc_html(prvni["text"])}</span>'
            f'<span class="acaret">▾</span></summary>'
            f'<ul>{radky}</ul>'
            f'<p class="apata">Úplný přehled všech kroků a dokladů: '
            f'<a href="jak-to-vime.html">Zdroje a doklady</a>.</p></details>')


def renderuj_kroky(navod):
    """Vykreslí kroky návodu do statického HTML — stejné značení, jaké kreslí
    JavaScript na stránce. Díky <details>/<summary> funguje i úplně bez JS;
    skript na stránce pak jen připojí tlačítka kopírování."""
    out = []
    for k in navod["kroky"]:
        znacka = ('<span class="stavZ cast">AI agent</span>' if k.get("u") == "agent"
                  else '<span class="stavZ ok">běžný chat</span>')
        vnitrek = ""
        if k.get("vy"):
            vnitrek += '<p class="kr"><b>Co uděláte vy:</b> ' + esc_html(k["vy"]) + "</p>"
        if k.get("ai"):
            vnitrek += '<p class="kr"><b>Co udělá AI:</b> ' + esc_html(k["ai"]) + "</p>"
        if k.get("pozn"):
            vnitrek += '<p class="kpozn">' + esc_html(k["pozn"]) + "</p>"
        if k.get("p"):
            vnitrek += ('<div class="prompt"><div class="ph"><span>Hotový prompt</span>'
                        '<button class="btn kopir" type="button">Zkopírovat</button></div>'
                        "<pre>" + esc_html(k["p"]) + "</pre></div>")
        out.append('<details class="krok"><summary>'
                   '<span class="cislo">' + esc_html(k["c"]) + "</span>"
                   '<span class="knazev">' + esc_html(k["n"]) + "</span>" + znacka +
                   '<span class="kcas">' + esc_html(k.get("cas", "")) + "</span>"
                   '<span class="caret">▶</span></summary>'
                   '<div class="kinner">' + vnitrek + "</div></details>")
    return "".join(out)


def bezpecny_href(hodnota):
    """Povolí jen běžný webový nebo relativní odkaz z publikačních dat."""
    if not hodnota or not isinstance(hodnota, str):
        return None
    hodnota = hodnota.strip()
    if re.match(r"^https?://", hodnota, re.I):
        return hodnota
    if not re.match(r"^[a-z][a-z0-9+.-]*:", hodnota, re.I) and not hodnota.startswith("//"):
        return hodnota
    raise ValueError(f"Nepovolené schéma odkazu v datech: {hodnota!r}")


STRANKY = {                       # soubor -> {id bloku: název datového souboru}
    "index.html":      {"d-rozpocet": None, "d-penize": None,
                        "d-vydaje": None, "d-prijmy": None, "d-rady": None,
                        "d-temata": None, "d-vybrane": None, "d-518": None,
                        "d-dotace": "dotace-web.json",
                        "d-mas": "mas-bobrava.json",
                        "d-spolky": "spolky-okoli.json",
                        "d-obyvatele": "obyvatele.json"},
    "rizeni.html":     {"d-rizeni": "rizeni.json", "d-vybrane": None,
                        "d-pravni-okres": "pravni-okres.json"},
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
 {"id": "pravni", "nadpis": "Konzultační a právní služby (rozpočtová položka)", "barva": "#e63562",
  "pol": ["5166"],
  "vazba": {"text": "Pozor, tady měřím širší rozpočtovou položku 5166 — vedle právních služeb "
                    "zahrnuje i konzultace a poradenství. Rozbor samotných právních služeb "
                    "z účetního deníku (617 tis. Kč za rok 2025) je výše.",
            "kotva": "#p-pravni", "odkaz": "přejít na rozbor právních služeb ↑"},
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
           "hospodárně, je rostoucí příspěvek spíš dobrá zpráva než problém. "
           "Od 1. 1. 2026 přešlo financování nepedagogické práce a části dalších výdajů "
           "na zřizovatele. Příspěvek školy proto s předchozími roky nesrovnávám bez "
           "rozpisu; rozpočet Prštic tento dopad zatím nerozlišuje.",
  "odhad": False,
  "nevime": "Rozpočet neukazuje, co konkrétně růst příspěvku pokrývá (energie, mzdy, provoz)."},
 {"id": "voda", "nadpis": "Voda a odpadní vody", "barva": "#0f9fbd",
  "par": ["2321", "2310"],
  "popis": "Výdaje na pitnou vodu, kanalizaci a čištění odpadních vod prudce vzrostly "
           "v roce 2023. Za první pololetí 2026 jsou přitom náklady vyšší než za celý "
           "rok 2025 — pokud se tempo udrží, čeká obec další citelný nárůst.",
  "nevime": "Co nárůst v roce 2023 způsobilo a jak se náklady promítají do stočného, "
            "z rozpočtu není patrné."},
]


def nacti_web_souhrny():
    """Načte malé veřejné souhrny a odmítne neúplné či nečekané schéma."""
    cesta = os.path.join(DATA, "web-souhrny.json")
    if not os.path.exists(cesta):
        sys.exit("CHYBA: chybí povinný veřejný zdroj data/web-souhrny.json")
    d = json.load(open(cesta, encoding="utf-8"))
    povinne = {"meta", "rozpocet", "penize", "prubezne_2026H1"}
    if set(d) != povinne:
        sys.exit(f"CHYBA: data/web-souhrny.json má klíče {sorted(d)}, čekáno {sorted(povinne)}")
    for k, rady in (("rozpocet", ("roky", "prijmy", "vydaje")),
                    ("penize", ("roky", "ucty", "uvery"))):
        if set(d[k]) != set(rady) or len({len(d[k][x]) for x in rady}) != 1:
            sys.exit(f"CHYBA: neplatné schéma nebo délky řad web-souhrny/{k}")
    p = d["prubezne_2026H1"]
    if set(p) != {"obdobi", "jednotka", "baze", "zdroj", "temata"} or p["baze"] != "cash_budget":
        sys.exit("CHYBA: neplatné schéma průběžných dat 2026 v data/web-souhrny.json")
    return d


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

    h1_data = nacti_web_souhrny()["prubezne_2026H1"]["temata"]

    out = []
    for t in TEMATA:
        rada = [vydaj(r, t.get("pol"), t.get("par")) for r in roky]
        z = {"id": t["id"], "n": t["nadpis"], "barva": t["barva"], "popis": t["popis"],
             "nevime": t["nevime"], "rada": rada}
        if t.get("vazba"):
            z["vazba"] = t["vazba"]
        # u témat vázaných na paragraf bereme paragrafy, jinak položky
        v26 = h1_data.get(t["id"], {}).get("hodnota")
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
        "komentar": "Nízký poplatek je pro občany dnes výhodný. Zákonný poplatek za skládkování využitelného odpadu ale poroste každý rok — až na 1 850 Kč za tunu v roce 2029. Sníženou sazbu 500 Kč za tunu lze uplatnit na množství odpadu do zákonného limitu podle počtu obyvatel. Procentní cíle třídění jsou samostatnou povinností. Z dostupných dat zatím nevím, v jakém rozsahu Prštice sníženou sazbu využily.",
        "kpozn": "Sazby: zákon č. 541/2020 Sb., příloha č. 9. Jde o komentář autora — "
                 "interpretaci, ne doložený závěr.",
        "rada": vyd, "rada2": popl, "l1": "Výdaje obce na odpad", "l2": "Poplatky od občanů",
        "kryti": [round(p / x * 100) if x else 0 for p, x in zip(popl, vyd)],
        **({"h1": h1_data["odpady"]["hodnota"], "h1b": h1_data["odpady"]["poplatky"],
            "odhad": True, "odhad2": False} if h1_data.get("odpady") else {})})

    return {"roky": roky, "temata": out}


def blok_vybrane():
    """Řady pro sekci vybraných výdajů — z účetního deníku 518."""
    r = json.load(open(os.path.join(DATA, "ucet-518-rozklad.json"), encoding="utf-8"))
    kat = r["kategorie_po_letech_kc"]
    roky = ["2022", "2023", "2024", "2025"]

    h1 = {}
    cesta = os.path.join(DATA, "ucet-518-2026H1-public.json")
    if os.path.exists(cesta):
        d26 = json.load(open(cesta, encoding="utf-8"))
        pol = d26["polozky"] if isinstance(d26, dict) and "polozky" in d26 else d26
        for x in pol:
            k = x.get("kategorie_web") or x.get("kategorie", "")
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


def renderuj_spolky(sp):
    """Statické HTML pro zjištění o podpoře spolků: vodorovné sloupce
    (Kč na obyvatele, 2025) a tabulka obec × rok. Bez JavaScriptu."""
    srov = json.load(open(os.path.join(DATA, "srovnani-dotaci.json"), encoding="utf-8"))
    okruh = {o["kod"]: o.get("okruh", "") for o in srov["obce"]}
    obce = sorted(sp["obce"], key=lambda o: -o["na_obyv_2025"])
    mx = max(o["na_obyv_2025"] for o in obce) or 1
    def kcs(n):
        return f"{int(round(n)):,}".replace(",", "\u00a0")
    radky = []
    for o in obce:
        my = o["kod"] == "583707"
        sous = okruh.get(o["kod"], "") == "sousední"
        cls = "radek my" if my else ("radek sous" if sous else "radek")
        w = max(o["na_obyv_2025"] / mx * 100, 0.6)
        radky.append(f'<div class="{cls}"><span class="jm">{esc_html(o["obec"])}{" *" if sous and not my else ""}</span>'
                     f'<span class="zl"><i style="width:{w:.1f}%"></i></span>'
                     f'<span class="hod">{kcs(o["na_obyv_2025"])}\u00a0Kč</span></div>')
    barh = "".join(radky) + ('<p class="src" style="margin-top:10px">* sousední obec Prštic. Hodnota = transfery spolkům '
            'a neziskovým organizacím v roce 2025 na jednoho obyvatele.</p>')
    roky = [str(r) for r in range(2019, 2026)]
    def rocni(o, r):
        return o["roky"][r]["5222"] + o["roky"][r]["5229"]
    def suma(o):
        return sum(rocni(o, r) for r in roky)
    tabulka = sorted(sp["obce"], key=lambda o: -o["na_obyv_2025"])   # stejné pořadí jako sloupce
    max_suma = max(suma(o) for o in tabulka) or 1
    hlav = ('<tr><th class="ob">obec</th>'
            + "".join(f'<th class="rok">{r}</th>' for r in roky[:-1])
            + '<th class="suma">2019–2025 celkem</th><th class="r25">rok 2025</th><th class="naob">2025 na obyvatele</th></tr>')
    telo = []
    for o in tabulka:
        my = o["kod"] == "583707"
        drobne = "".join(f'<td class="rok">{kcs(rocni(o, r) / 1000)}</td>' for r in roky[:-1])
        podil = suma(o) / max_suma * 100
        telo.append(f'<tr{" class=\"my\"" if my else ""}>'
                    f'<th class="ob">{esc_html(o["obec"])}<small>{kcs(o["obyvatel"])}\u00a0obyv.</small></th>{drobne}'
                    f'<td class="suma" style="--p:{podil:.1f}%"><span>{kcs(suma(o))}\u00a0Kč</span></td>'
                    f'<td class="r25">{kcs(rocni(o, "2025"))}\u00a0Kč</td>'
                    f'<td class="naob">{kcs(o["na_obyv_2025"])}\u00a0Kč</td></tr>')
    tab = ('<table class="spolkytab"><thead>' + hlav + '</thead><tbody>' + "".join(telo) + '</tbody></table>')
    return barh, tab


def vloz(html, blok_id, data):
    vzor = re.compile(r'(<script type="application/json" id="%s">)(.*?)(</script>)' % re.escape(blok_id), re.S)
    if not vzor.search(html):
        sys.exit(f"CHYBA: v index.html chybí blok id=\"{blok_id}\"")
    obsah = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # JSON uvnitř HTML nesmí vytvořit značku ani předčasně ukončit <script>.
    obsah = obsah.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    return vzor.sub(lambda m: m.group(1) + obsah + m.group(3), html)


def renderuj_pravni_graf(d):
    """Žebříček všech obcí skupiny jako HTML sloupečky (třída .barh, kterou web
    už používá u spolků). Proti SVG má tu výhodu, že písmo je skutečné písmo
    stránky — nezmenšuje se s šířkou okna a je stejné jako v okolním textu."""
    NB = "\u00a0"
    m = d["meta"]; med = m["median_skupiny_bez_prstic_celkem"]
    sk = sorted([o for o in d["obce"] if o.get("skupina_700_1500")], key=lambda o: -o["celkem_2022_2025"])
    mx = sk[0]["celkem_2022_2025"] or 1
    def kcs(n):
        return f"{int(round(n)):,}".replace(",", NB)
    radky = []
    for i, o in enumerate(sk, 1):
        my = o["kod"] == "583707"
        # nula musí zůstat nula — proužek „skoro nic" by tvrdil, že obec něco vydala
        w = 0.0 if o["celkem_2022_2025"] == 0 else max(o["celkem_2022_2025"] / mx * 100, 0.4)
        radky.append(
            f'<div class="radek{" my" if my else ""}">'
            f'<span class="jm">{i}.{NB}{esc_html(o["obec"])}'
            f'<small>{kcs(o["obyvatel"])}</small></span>'
            f'<span class="zl"><i style="width:{w:.2f}%"></i></span>'
            f'<span class="hod">{kcs(o["celkem_2022_2025"] / 1000)}</span></div>')
    return (f'<div class="barh zebricek" style="--med:{med / mx * 100:.2f}%">'
            f'<p class="legenda">Svislá čárka je <b>medián ostatních obcí</b> '
            f'({kcs(med / 1000)}{NB}tis.{NB}Kč). Šedě za názvem je počet obyvatel, '
            f'vpravo výdaje za roky 2022–2025 v tisících Kč.</p>'
            + "".join(radky) + '</div>')


def renderuj_pravni_okres(d):
    """Statické HTML pro srovnání položky 5166 (konzultační, poradenské a právní
    služby) s obcemi okresu Brno-venkov o 700–1 500 obyvatelích. Bez JavaScriptu:
    věta se souhrnem, tabulka prvních dvanácti a rozbalovací zbytek skupiny."""
    m = d["meta"]; p = m["prstice"]
    roky = ["2022", "2023", "2024", "2025"]
    def kcs(n):
        return f"{int(round(n)):,}".replace(",", "\u00a0")
    sk = [o for o in d["obce"] if o.get("skupina_700_1500")]
    sk.sort(key=lambda o: -o["celkem_2022_2025"])
    assert sk and sk[0]["kod"] == "583707", "pravni-okres: Prštice nejsou první ve skupině — text sekce by nesouhlasil"
    assert len(sk) == m["skupina_pocet"], "pravni-okres: počet obcí ve skupině nesedí s meta"
    ostatni = m["skupina_pocet"] - 1
    veta = (f'<p class="souhrn"><b>Prštice: {kcs(p["celkem_2022_2025"] / 1000)}\u00a0tis.\u00a0Kč za roky 2022–2025 — '
            f'{p["poradi_skupina_celkem"]}. místo z {m["skupina_pocet"]} obcí</b> okresu Brno-venkov se 700–1\u00a0500 obyvateli. '
            f'Medián ostatních {ostatni} obcí je <b>{kcs(m["median_skupiny_bez_prstic_celkem"] / 1000)}\u00a0tis.\u00a0Kč</b>; '
            f'druhé v pořadí, {esc_html(sk[1]["obec"])} ({kcs(sk[1]["obyvatel"])} obyvatel), vydaly {kcs(sk[1]["celkem_2022_2025"] / 1000)}\u00a0tis.\u00a0Kč. '
            f'V celém okrese ({m["obci_v_okrese"]} obcí) jsou Prštice v částce {p["poradi_okres_celkem"]}., na obyvatele {p["poradi_okres_na_obyv"]}. '
            f'a v podílu na celkových výdajích obce {p["poradi_okres_podil"]}.</p>')
    mx = sk[0]["celkem_2022_2025"] or 1
    hlav = ('<tr><th class="ob">obec</th>' + "".join(f'<th class="rok">{r}</th>' for r in roky[:-1])
            + '<th class="r25">rok 2025</th><th class="suma">2022–2025 celkem</th><th class="naob">na obyvatele</th></tr>')
    def radek(i, o):
        my = o["kod"] == "583707"
        drobne = "".join(f'<td class="rok">{kcs(o["roky"][r] / 1000)}</td>' for r in roky[:-1])
        return (f'<tr{" class=\"my\"" if my else ""}><th class="ob">{i}. {esc_html(o["obec"])}'
                f'<small>{kcs(o["obyvatel"])}\u00a0obyv.</small></th>{drobne}'
                f'<td class="r25">{kcs(o["roky"]["2025"] / 1000)}</td>'
                f'<td class="suma" style="--p:{o["celkem_2022_2025"] / mx * 100:.1f}%"><span>{kcs(o["celkem_2022_2025"] / 1000)}\u00a0tis.\u00a0Kč</span></td>'
                f'<td class="naob">{kcs(o["na_obyv"])}\u00a0Kč</td></tr>')
    telo = "".join(radek(i, o) for i, o in enumerate(sk, 1))
    tab = ('<div class="tblscroll"><table class="spolkytab"><thead>' + hlav
           + '</thead><tbody>' + telo + '</tbody></table></div>')
    return veta, tab


def main():
    souhrny = nacti_web_souhrny()
    v, p = blok_vydaje(), blok_prijmy()
    rady, temata, vybrane = blok_rady(), blok_temata(), blok_vybrane()
    hotove = {"d-rozpocet": souhrny["rozpocet"], "d-penize": souhrny["penize"],
              "d-vydaje": v, "d-prijmy": p, "d-rady": rady,
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
            # aktuality: pruh na hlavní stránce ze souboru data/aktuality.json
            if soubor == "index.html" and blok_id == "d-obyvatele":
                akt = json.load(open(os.path.join(DATA, "aktuality.json"), encoding="utf-8"))
                html = re.sub(r"<!--aktuality-start-->.*?<!--aktuality-konec-->",
                              "<!--aktuality-start-->" + renderuj_aktuality(akt) + "<!--aktuality-konec-->",
                              html, flags=re.S)
                vlozeno.append("aktuality (statické HTML)")
            # spolky: sloupce a tabulka staticky, ať existují bez JavaScriptu
            if blok_id == "d-spolky":
                barh, tab = renderuj_spolky(data)
                html = re.sub(r"<!--spolky-barh-start-->.*?<!--spolky-barh-konec-->",
                              "<!--spolky-barh-start-->" + barh + "<!--spolky-barh-konec-->", html, flags=re.S)
                html = re.sub(r"<!--spolky-tab-start-->.*?<!--spolky-tab-konec-->",
                              "<!--spolky-tab-start-->" + tab + "<!--spolky-tab-konec-->", html, flags=re.S)
                vlozeno.append("spolky (statické HTML)")
            # právní a poradenské služby v okrese: věta a tabulka staticky
            if blok_id == "d-pravni-okres":
                veta, tab = renderuj_pravni_okres(data)
                html = re.sub(r"<!--pravni-veta-start-->.*?<!--pravni-veta-konec-->",
                              "<!--pravni-veta-start-->" + veta + "<!--pravni-veta-konec-->", html, flags=re.S)
                html = re.sub(r"<!--pravni-tab-start-->.*?<!--pravni-tab-konec-->",
                              "<!--pravni-tab-start-->" + tab + "<!--pravni-tab-konec-->", html, flags=re.S)
                html = re.sub(r"<!--pravni-graf-start-->.*?<!--pravni-graf-konec-->",
                              "<!--pravni-graf-start-->" + renderuj_pravni_graf(data) + "<!--pravni-graf-konec-->",
                              html, flags=re.S)
                vlozeno.append("právní služby v okrese (statické HTML)")
            # návod: kroky vykreslit i staticky, ať existují bez JavaScriptu
            if blok_id == "d-navod":
                html = re.sub(r"<!--kroky-start-->.*?<!--kroky-konec-->",
                              "<!--kroky-start-->" + renderuj_kroky(data) + "<!--kroky-konec-->",
                              html, flags=re.S)
                vlozeno.append("kroky (statické HTML)")
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
