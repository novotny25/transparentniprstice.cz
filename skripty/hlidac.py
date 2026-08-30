#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hlídač webu — Transparentní Prštice

Denní kontrola, že web pořád platí. Doplňuje `validace.py` (ta hlídá integritu
dat před nasazením); tenhle skript hlídá HOTOVÝ, UŽ NASAZENÝ web:

  1. ODKAZY VEN     — každý externí odkaz se opravdu otevře (HTTP kód)
  2. ODKAZY DOVNITŘ — každá stránka, kotva `#id` a dokument existují
  3. ZDROJE         — každý obrázek, CSS, JSON a PDF, na který se web odkazuje
  4. ČÍSLA          — čísla natvrdo v HTML sedí na hodnoty v data/*.json
  5. TVRZENÍ        — věty s datem spotřeby („obec doloží do 9. září")
  6. ŽIVÝ WEB       — stránky vracejí 200 a mají bezpečnostní hlavičky

Odkazy, kotvy a zdroje si skript odvodí ze stránek SÁM — když na web přibude
nový odkaz, začne se hlídat bez jakéhokoli nastavení.

Nastavení potřebují jen dvě věci, které se ze stránky vyčíst nedají:
  data/hlidka-tvrzeni.json — věty, které jednou přestanou platit
  data/hlidka-cisla.json   — které číslo v textu patří ke které hodnotě v datech
Oba soubory jsou ručně editovatelné a mají uvnitř vysvětlivku.

Spuštění:
    python3 skripty/hlidac.py                 # všechno včetně internetu
    python3 skripty/hlidac.py --bez-site      # jen soubory, offline
    python3 skripty/hlidac.py --report x.md   # kam zapsat hlášení

Návratový kód:  0 = vše v pořádku
                1 = jsou otázky nebo varování (nic rozbitého)
                2 = něco je rozbité, je potřeba zásah
"""
from __future__ import annotations

import argparse
import shutil
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from datetime import date, datetime
from html.parser import HTMLParser
from urllib.parse import urlparse

# Nastavení se vyplní v main() — buď se odvodí ze složky projektu, nebo
# se předá parametrem. Díky tomu je skript přenositelný na další weby.
KOREN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(KOREN, "web")
DATA = os.path.join(KOREN, "data")
DOMENA = ""
ZIVY = ""

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 (hlidac odkazu)")

# Kde se web obvykle nachází — hledá se v tomhle pořadí.
OBVYKLE_SLOZKY_WEBU = ["web", "public", "dist", "site", "_site", "docs", "."]

# Hlavičky, které musí živý web posílat (nastavené v netlify.toml).
POVINNE_HLAVICKY = [
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
    "strict-transport-security",
]

# ---------------------------------------------------------------------------
# Sběr nálezů
# ---------------------------------------------------------------------------
ROZBITE: list[tuple[str, str]] = []   # 🔴 musí se opravit
VAROVANI: list[tuple[str, str]] = []  # 🟡 podívat se, nemusí být chyba
OTAZKY: list[tuple[str, str]] = []    # ❓ hlídač se ptá autora
VPORADKU: list[str] = []              # 🟢 souhrnné hlášky


def rozbite(kde: str, co: str) -> None:
    ROZBITE.append((kde, co))


def varovani(kde: str, co: str) -> None:
    VAROVANI.append((kde, co))


def otazka(kde: str, co: str) -> None:
    OTAZKY.append((kde, co))


def vporadku(co: str) -> None:
    VPORADKU.append(co)


# ---------------------------------------------------------------------------
# Čtení stránek
# ---------------------------------------------------------------------------
class Stranka(HTMLParser):
    """Vytáhne ze stránky odkazy, zdroje, kotvy a čistý text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.odkazy: list[tuple[str, str, int]] = []   # (href, text, řádek)
        self.zdroje: list[tuple[str, str, int]] = []   # (url, atribut, řádek)
        self.kotvy: set[str] = set()
        self.duplicitni_kotvy: list[str] = []
        self._text: list[str] = []
        self._sbiram_text_odkazu: list[str] | None = None
        self._posledni_odkaz: tuple[str, int] | None = None
        self._preskocit = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        radek = self.getpos()[0]

        if tag in ("script", "style"):
            self._preskocit += 1

        ident = a.get("id")
        if ident:
            if ident in self.kotvy:
                self.duplicitni_kotvy.append(ident)
            self.kotvy.add(ident)
        # <a name="..."> se historicky používá jako kotva
        if tag == "a" and a.get("name"):
            self.kotvy.add(a["name"])

        if tag == "a" and a.get("href"):
            self._posledni_odkaz = (a["href"], radek)
            self._sbiram_text_odkazu = []

        for atr in ("src", "href", "data-src", "poster"):
            url = a.get(atr)
            if not url:
                continue
            if tag == "a" and atr == "href":
                continue  # odkazy řešíme zvlášť
            self.zdroje.append((url, f"{tag}[{atr}]", radek))

        srcset = a.get("srcset")
        if srcset:
            for kus in srcset.split(","):
                url = kus.strip().split(" ")[0]
                if url:
                    self.zdroje.append((url, f"{tag}[srcset]", radek))

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._preskocit > 0:
            self._preskocit -= 1
        if tag == "a" and self._posledni_odkaz is not None:
            href, radek = self._posledni_odkaz
            text = " ".join("".join(self._sbiram_text_odkazu or []).split())
            self.odkazy.append((href, text[:120], radek))
            self._posledni_odkaz = None
            self._sbiram_text_odkazu = None

    def handle_data(self, data):
        if self._preskocit:
            return
        self._text.append(data)
        if self._sbiram_text_odkazu is not None:
            self._sbiram_text_odkazu.append(data)

    @property
    def text(self) -> str:
        return normalizuj_mezery("".join(self._text))


def najdi_slozku_webu(koren: str) -> str:
    """Najde složku s HTML stránkami. Většina webů má `web/` nebo `public/`."""
    for jmeno in OBVYKLE_SLOZKY_WEBU:
        kandidat = os.path.join(koren, jmeno) if jmeno != "." else koren
        if os.path.isdir(kandidat) and any(
                f.endswith(".html") for f in os.listdir(kandidat)):
            return os.path.abspath(kandidat)
    return os.path.join(koren, "web")


def zjisti_domenu(web: str) -> str:
    """Vyčte doménu z sitemap.xml, CNAME nebo robots.txt. Prázdno = neznámá."""
    sm = os.path.join(web, "sitemap.xml")
    if os.path.exists(sm):
        with open(sm, encoding="utf-8") as f:
            m = re.search(r"<loc>\s*(https?://[^<\s/]+)", f.read())
        if m:
            host = urlparse(m.group(1)).hostname
            if host:
                return host.lower()

    cname = os.path.join(web, "CNAME")
    if os.path.exists(cname):
        with open(cname, encoding="utf-8") as f:
            host = f.read().strip()
        if host:
            return host.lower().replace("https://", "").rstrip("/")

    rb = os.path.join(web, "robots.txt")
    if os.path.exists(rb):
        with open(rb, encoding="utf-8") as f:
            m = re.search(r"(?im)^\s*sitemap:\s*(https?://[^\s]+)", f.read())
        if m:
            host = urlparse(m.group(1)).hostname
            if host:
                return host.lower()
    return ""


def je_nas(url: str) -> bool:
    """Patří URL našemu webu? Porovnává hostitele, ne jen výskyt řetězce —
    `github.com/…/transparentniprstice.cz` je cizí odkaz, ne náš."""
    if not DOMENA:
        return False
    host = (urlparse(url).hostname or "").lower()
    zaklad = DOMENA[4:] if DOMENA.startswith("www.") else DOMENA
    return host == zaklad or host.endswith("." + zaklad)


def normalizuj_mezery(s: str) -> str:
    """Sjednotí všechny druhy mezer (pevná, úzká, tabulátor) na obyčejnou."""
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", " ", s.replace(" ", " ").replace(" ", " ")).strip()


# Kotvy, které vyrábí JavaScript za běhu — staticky je v HTML nevidíme.
# Poznáme je podle šablony v kódu: id="t-'+t.id+'"  → předpona "t-".
# Možné hodnoty pak dohledáme mezi klíči "id" ve vložených i souborových datech.
RE_SABLONA_ID = re.compile(r"""id=["']([A-Za-z0-9_-]*)["']\s*\+""")
RE_JSON_BLOK_S_ID = re.compile(
    r"""<script[^>]*type=["']application/json["'][^>]*\sid=["']([^"']+)["'][^>]*>(.*?)</script>""",
    re.S | re.I)
RE_JSON_BLOK = re.compile(
    r"""<script[^>]*type=["']application/json["'][^>]*>(.*?)</script>""",
    re.S | re.I)


def posbirej_id(uzel, ven: set) -> None:
    """Projde JSON a posbírá každou hodnotu pod klíčem "id"."""
    if isinstance(uzel, dict):
        for k, v in uzel.items():
            if k == "id" and isinstance(v, str):
                ven.add(v)
            else:
                posbirej_id(v, ven)
    elif isinstance(uzel, list):
        for v in uzel:
            posbirej_id(v, ven)


def dynamicke_kotvy() -> set[str]:
    """Vrátí kotvy, které stránka poskládá za běhu (předpona + id z dat)."""
    predpony: set[str] = set()
    hodnoty: set[str] = set()

    for jmeno in os.listdir(WEB):
        if not jmeno.endswith(".html"):
            continue
        with open(os.path.join(WEB, jmeno), encoding="utf-8") as f:
            zdroj = f.read()
        for m in RE_SABLONA_ID.finditer(zdroj):
            if m.group(1):
                predpony.add(m.group(1))
        for m in RE_JSON_BLOK.finditer(zdroj):
            try:
                posbirej_id(json.loads(m.group(1)), hodnoty)
            except json.JSONDecodeError:
                pass

    if os.path.isdir(DATA):
        for jmeno in os.listdir(DATA):
            if not jmeno.endswith(".json"):
                continue
            try:
                with open(os.path.join(DATA, jmeno), encoding="utf-8") as f:
                    posbirej_id(json.load(f), hodnoty)
            except Exception:  # noqa: BLE001
                pass

    return {p + h for p in predpony for h in hodnoty}


def nacti_stranky() -> dict[str, Stranka]:
    stranky: dict[str, Stranka] = {}
    for jmeno in sorted(os.listdir(WEB)):
        if not jmeno.endswith(".html"):
            continue
        p = Stranka()
        with open(os.path.join(WEB, jmeno), encoding="utf-8") as f:
            p.feed(f.read())
        p.close()
        stranky[jmeno] = p
    return stranky


# ---------------------------------------------------------------------------
# 1. ODKAZY VEN
# ---------------------------------------------------------------------------
def zkontroluj(url: str, metoda: str = "HEAD", timeout: int = 25):
    """Vrátí (kód, konečná URL, chyba). Kód None = spojení vůbec neproběhlo."""
    req = urllib.request.Request(url, method=metoda, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
        "Accept-Language": "cs,en;q=0.7",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.url, None
    except urllib.error.HTTPError as e:
        return e.code, url, None
    except Exception as e:  # noqa: BLE001 — chceme jméno jakékoli chyby
        return None, url, f"{type(e).__name__}: {e}"


def kontrola_odkazu_ven(stranky: dict[str, Stranka]) -> None:
    vsechny: dict[str, list[str]] = {}
    for jmeno, p in stranky.items():
        for href, text, radek in p.odkazy:
            if href.startswith(("http://", "https://")) and not je_nas(href):
                vsechny.setdefault(href, []).append(f"{jmeno}:{radek} „{text}“")

    if not vsechny:
        return

    ok = 0
    for url in sorted(vsechny):
        kde = "; ".join(vsechny[url][:3])
        kod, konec, chyba = zkontroluj(url)
        # Některé servery na HEAD neodpovídají správně — zkusíme GET.
        if kod is None or kod in (403, 405, 501):
            kod, konec, chyba = zkontroluj(url, "GET")

        if kod is None:
            rozbite("odkaz ven", f"{url}\n    nepodařilo se spojit ({chyba})\n    odkud: {kde}")
        elif kod == 200:
            ok += 1
        elif kod in (401, 403, 429):
            varovani("odkaz ven", f"{url}\n    server vrátil {kod} — nejspíš blokuje roboty, "
                                  f"ověř ručně v prohlížeči\n    odkud: {kde}")
        elif 300 <= kod < 400:
            varovani("odkaz ven", f"{url}\n    přesměrování ({kod}) na {konec}\n    odkud: {kde}")
        else:
            rozbite("odkaz ven", f"{url}\n    server vrátil {kod}\n    odkud: {kde}")

    vporadku(f"Odkazy ven: {ok} z {len(vsechny)} se otevřelo bez potíží.")


# ---------------------------------------------------------------------------
# 2. ODKAZY DOVNITŘ A KOTVY
# ---------------------------------------------------------------------------
def kontrola_odkazu_dovnitr(stranky: dict[str, Stranka]) -> None:
    dynamicke = dynamicke_kotvy()
    pocet = 0
    dyn_pouzitych = 0
    for jmeno, p in stranky.items():
        for href, text, radek in p.odkazy:
            if href.startswith(("mailto:", "tel:", "javascript:", "data:")):
                continue
            # odkaz na vlastní doménu bereme jako vnitřní
            cil = href
            if cil.startswith(("http://", "https://")):
                if not je_nas(cil):
                    continue
                cil = re.sub(r"^https?://[^/]+", "", cil) or "/"

            cesta, _, kotva = cil.partition("#")
            cesta = cesta.split("?")[0]
            pocet += 1

            if cesta in ("", "./"):
                cilova_stranka = jmeno
            elif cesta == "/":
                cilova_stranka = "index.html"
            else:
                rel = cesta.lstrip("/")
                soubor = os.path.join(WEB, rel)
                if os.path.isdir(soubor):
                    soubor = os.path.join(soubor, "index.html")
                    rel = os.path.join(rel, "index.html")
                if not os.path.exists(soubor):
                    rozbite("odkaz dovnitř",
                            f"{jmeno}:{radek} → `{href}` — soubor neexistuje "
                            f"(text odkazu: „{text}“)")
                    continue
                cilova_stranka = os.path.basename(rel)

            if kotva:
                cilova = stranky.get(cilova_stranka)
                if cilova is None:
                    continue  # cíl není HTML stránka (např. PDF) — kotvu neověříme
                if kotva in dynamicke and kotva not in cilova.kotvy:
                    dyn_pouzitych += 1
                elif kotva not in cilova.kotvy:
                    rozbite("kotva",
                            f"{jmeno}:{radek} → `{href}` — na stránce {cilova_stranka} "
                            f"není nic s id=\"{kotva}\" (text odkazu: „{text}“)")

    for jmeno, p in stranky.items():
        for dup in sorted(set(p.duplicitni_kotvy)):
            rozbite("duplicitní id", f"{jmeno}: id=\"{dup}\" je na stránce víckrát — "
                                     f"odkaz `#{dup}` skočí jen na první výskyt")

    zprava = f"Odkazy dovnitř a kotvy: prověřeno {pocet}."
    if dyn_pouzitych:
        zprava += (f" Z toho {dyn_pouzitych} kotev vyrábí JavaScript z dat — "
                   f"ověřeno proti datům, ne proti HTML.")
    vporadku(zprava)


# ---------------------------------------------------------------------------
# 3. ZDROJE (obrázky, CSS, JSON, PDF)
# ---------------------------------------------------------------------------
def kontrola_zdroju(stranky: dict[str, Stranka]) -> None:
    # zdroje z HTML atributů
    kandidati: dict[str, list[str]] = {}
    for jmeno, p in stranky.items():
        for url, atr, radek in p.zdroje:
            if url.startswith(("http://", "https://", "data:", "//", "mailto:")):
                continue
            kandidati.setdefault(url.split("?")[0].split("#")[0], []).append(f"{jmeno}:{radek} {atr}")

    # zdroje, které si stránka natahuje JavaScriptem: fetch('data/neco.json')
    for jmeno in stranky:
        with open(os.path.join(WEB, jmeno), encoding="utf-8") as f:
            zdroj = f.read()
        for m in re.finditer(r"""["'`](\.{0,2}/?(?:data|dokumenty|obrazky)/[^"'`?\s]+)["'`]""", zdroj):
            radek = zdroj[:m.start()].count("\n") + 1
            kandidati.setdefault(m.group(1), []).append(f"{jmeno}:{radek} fetch")

    # zdroje z CSS (url(...))
    css = os.path.join(WEB, "styl.css")
    if os.path.exists(css):
        with open(css, encoding="utf-8") as f:
            obsah = f.read()
        for m in re.finditer(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""", obsah):
            u = m.group(1).strip()
            if u.startswith(("data:", "http://", "https://", "//")):
                continue
            radek = obsah[:m.start()].count("\n") + 1
            kandidati.setdefault(u, []).append(f"styl.css:{radek} url()")

    ok = 0
    for url in sorted(kandidati):
        rel = url.lstrip("./").lstrip("/")
        # data/ leží vedle web/, ne uvnitř
        cesty = [os.path.join(WEB, rel), os.path.join(KOREN, rel)]
        nalezeno = next((c for c in cesty if os.path.exists(c)), None)
        kde = "; ".join(kandidati[url][:3])
        if nalezeno is None:
            rozbite("chybějící soubor", f"`{url}` neexistuje — odkud: {kde}")
        elif os.path.getsize(nalezeno) == 0:
            rozbite("prázdný soubor", f"`{url}` má nulovou velikost — odkud: {kde}")
        else:
            ok += 1
    vporadku(f"Zdroje (obrázky, CSS, data, PDF): {ok} z {len(kandidati)} na svém místě.")


# ---------------------------------------------------------------------------
# 4. ČÍSLA — text vs. data
# ---------------------------------------------------------------------------
def hodnota_z_cesty(data, cesta: str):
    """Projde JSON podle tečkové cesty: `roky.2025.vydaje` nebo `polozky.0.castka`."""
    kus = data
    for krok in cesta.split("."):
        if isinstance(kus, list):
            kus = kus[int(krok)]
        elif isinstance(kus, dict):
            if krok in kus:
                kus = kus[krok]
            else:
                raise KeyError(krok)
        else:
            raise KeyError(krok)
    return kus


def secti(data, predpis: dict):
    """Sečte hodnoty. Umí dva tvary dat:

    a) seznam řádků — `pole` je název sloupce, `kde` volitelný filtr:
       {"v": "polozky", "pole": "castka", "kde": {"rok": 2025}}
    b) slovník rok → hodnota — `klice` vyjmenuje, co sečíst:
       {"v": "rady.ucet_511.hodnoty_kc", "klice": ["2020", "2021"]}
    """
    kus = hodnota_z_cesty(data, predpis["v"]) if predpis.get("v") else data

    if isinstance(kus, dict):
        klice = predpis.get("klice") or list(kus)
        return sum(kus.get(k) or 0 for k in klice)

    pole = predpis["pole"]
    kde = predpis.get("kde") or {}
    celkem = 0
    for r in kus:
        if all(r.get(k) == v for k, v in kde.items()):
            celkem += r.get(pole) or 0
    return celkem


def naformatuj(hodnota, predpis: dict) -> str:
    delitel = predpis.get("delitel", 1)
    if delitel:
        hodnota = hodnota / delitel
    mist = predpis.get("desetinna", 0)
    s = f"{hodnota:,.{mist}f}".replace(",", " ").replace(".", ",")
    return s


def kontrola_cisel(stranky: dict[str, Stranka]) -> None:
    soubor = os.path.join(DATA, "hlidka-cisla.json")
    if not os.path.exists(soubor):
        varovani("čísla", "chybí `data/hlidka-cisla.json` — kontrola čísel proti datům neběží")
        return
    with open(soubor, encoding="utf-8") as f:
        nastaveni = json.load(f)
    polozky = nastaveni.get("kontroly", [])
    if not polozky:
        varovani("čísla", "`data/hlidka-cisla.json` je prázdný — žádné číslo se nehlídá")
        return

    cache: dict[str, object] = {}
    ok = 0
    for k in polozky:
        popis = k.get("popis", "(bez popisu)")
        stranka = k.get("stranka", "index.html")
        p = stranky.get(stranka)
        if p is None:
            rozbite("čísla", f"{popis}: stránka `{stranka}` neexistuje")
            continue

        zdroj = k.get("zdroj", {})
        jmeno_souboru = zdroj.get("soubor")
        try:
            if jmeno_souboru not in cache:
                with open(os.path.join(DATA, jmeno_souboru), encoding="utf-8") as f:
                    cache[jmeno_souboru] = json.load(f)
            data = cache[jmeno_souboru]
            if "soucet" in zdroj:
                hodnota = secti(data, zdroj["soucet"])
            else:
                hodnota = hodnota_z_cesty(data, zdroj["klic"])
        except Exception as e:  # noqa: BLE001
            rozbite("čísla", f"{popis}: nepodařilo se přečíst hodnotu z dat "
                            f"({jmeno_souboru}) — {type(e).__name__}: {e}")
            continue

        ocekavany = naformatuj(hodnota, k)
        hledany = normalizuj_mezery(k.get("predpona", "") + ocekavany + k.get("pripona", ""))
        if hledany in p.text:
            ok += 1
        else:
            v_textu = k.get("v_textu")
            napoveda = ""
            if v_textu:
                napoveda = (f"\n    na webu je podle poslední kontroly „{v_textu}“ — "
                            f"nejspíš se text a data rozešly")
            rozbite("čísla",
                    f"{popis}: v datech vychází „{hledany}“, ale tenhle text "
                    f"na stránce {stranka} není.{napoveda}\n"
                    f"    zdroj: {jmeno_souboru} → {zdroj.get('klic') or zdroj.get('soucet')}")

    vporadku(f"Čísla proti datům: {ok} z {len(polozky)} sedí.")


# ---------------------------------------------------------------------------
# 4b. VLOŽENÉ DATOVÉ BLOKY vs. SOUBORY V data/
# ---------------------------------------------------------------------------
def kontrola_bloku(stranky: dict[str, Stranka]) -> None:
    """Stránky mají data vložená přímo v HTML (`<script type="application/json">`).
    Když se rozejdou se soubory v `data/`, hrozí, že publikační skript web
    tiše vrátí do staršího stavu. Tahle kontrola to odhalí dřív."""
    soubor = os.path.join(DATA, "hlidka-bloky.json")
    if not os.path.exists(soubor):
        return
    with open(soubor, encoding="utf-8") as f:
        mapa = json.load(f).get("bloky", {})
    if not mapa:
        return

    nalezene: set[str] = set()
    shoda = 0
    for jmeno in sorted(stranky):
        with open(os.path.join(WEB, jmeno), encoding="utf-8") as f:
            zdroj = f.read()
        for m in RE_JSON_BLOK_S_ID.finditer(zdroj):
            bid, telo = m.group(1), m.group(2)
            nalezene.add(bid)
            zdrojovy = mapa.get(bid)
            if not zdrojovy:          # blok bez zdroje = psaný rovnou do HTML
                continue
            cesta = os.path.join(DATA, zdrojovy)
            if not os.path.exists(cesta):
                rozbite("datový blok",
                        f"{jmeno}: blok `{bid}` má pocházet z `{zdrojovy}`, "
                        f"ale ten soubor neexistuje")
                continue
            try:
                v_html = json.loads(telo)
                with open(cesta, encoding="utf-8") as f:
                    v_data = json.load(f)
            except json.JSONDecodeError as e:
                rozbite("datový blok", f"{jmeno}: blok `{bid}` nebo `{zdrojovy}` "
                                       f"není platný JSON — {e}")
                continue

            if v_html == v_data:
                shoda += 1
            else:
                rozbite("datový blok",
                        f"{jmeno}: blok `{bid}` se rozešel se souborem `{zdrojovy}`.\n"
                        f"    {popis_rozdilu(v_html, v_data)}\n"
                        f"    POZOR: dokud to nesrovnáš, NESPOUŠTĚJ publikační skript — "
                        f"přepsal by web starší verzí dat.")

    nezname = nalezene - set(mapa)
    if nezname:
        varovani("datový blok",
                 f"bloky bez uvedeného zdroje: {', '.join(sorted(nezname))} — "
                 f"jsou psané rovnou do HTML a nic je nehlídá. Když je to záměr, "
                 f"dopiš je do data/hlidka-bloky.json s hodnotou null.")
    if shoda:
        vporadku(f"Vložené datové bloky: {shoda} přesně odpovídá souborům v data/.")


def rozdily(a, b, cesta: str = "", strop: int = 40) -> list[str]:
    """Projde dvě verze dat a vypíše, čím přesně se liší."""
    ven: list[str] = []
    if len(ven) >= strop:
        return ven
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if len(ven) >= strop:
                break
            if k not in a:
                ven.append(f"{cesta}.{k} — je v data/, chybí v HTML")
            elif k not in b:
                ven.append(f"{cesta}.{k} — je v HTML, chybí v data/")
            else:
                ven += rozdily(a[k], b[k], f"{cesta}.{k}", strop)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            ven.append(f"{cesta} — v HTML {len(a)} položek, v data/ {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            if len(ven) >= strop:
                break
            ven += rozdily(x, y, f"{cesta}[{i}]", strop)
    elif a != b:
        ven.append(f"{cesta} — HTML {zkrat(a)} vs. data/ {zkrat(b)}")
    return ven


def zkrat(h, n: int = 60) -> str:
    t = repr(h)
    return t if len(t) <= n else t[:n - 1] + "…'"


def popis_rozdilu(a, b) -> str:
    """Řekne lidsky, čím se dvě verze dat liší."""
    r = rozdily(a, b)
    if not r:
        return "obsah se liší, ale rozdíl se nepodařilo pojmenovat"
    hlava = "\n    ".join("• " + x for x in r[:5])
    if len(r) > 5:
        hlava += f"\n    • … a dalších {len(r) - 5} rozdílů"
    return f"{len(r)} rozdílů:\n    {hlava}"


# ---------------------------------------------------------------------------
# 5. TVRZENÍ S DATEM SPOTŘEBY
# ---------------------------------------------------------------------------
def kontrola_tvrzeni(stranky: dict[str, Stranka]) -> None:
    soubor = os.path.join(DATA, "hlidka-tvrzeni.json")
    if not os.path.exists(soubor):
        varovani("tvrzení", "chybí `data/hlidka-tvrzeni.json` — věty s datem spotřeby se nehlídají")
        return
    with open(soubor, encoding="utf-8") as f:
        nastaveni = json.load(f)
    polozky = nastaveni.get("tvrzeni", [])
    dnes = date.today()
    cekajicich = 0

    for t in polozky:
        if t.get("vyrizeno"):
            continue
        citace = normalizuj_mezery(t.get("citace", ""))
        stranka = t.get("stranka", "index.html")
        p = stranky.get(stranka)

        # a) je věta na webu pořád? (když ji autor smazal, tvrzení už nehlídáme)
        na_webu = bool(p and citace and citace in p.text)
        if citace and p is not None and not na_webu:
            varovani("tvrzení",
                     f"[{t.get('id', '?')}] věta už na stránce {stranka} není:\n"
                     f"    „{citace[:100]}“\n"
                     f"    Buď byla přepsaná — pak uprav citaci v data/hlidka-tvrzeni.json, "
                     f"nebo je hotovo — pak dej \"vyrizeno\": true.")
            continue

        # b) nadešel den kontroly?
        kdy = t.get("datum_kontroly")
        if not kdy:
            continue
        try:
            kdy_d = datetime.strptime(kdy, "%Y-%m-%d").date()
        except ValueError:
            varovani("tvrzení", f"[{t.get('id', '?')}] nesrozumitelné datum_kontroly: {kdy!r}")
            continue

        if kdy_d <= dnes:
            po = (dnes - kdy_d).days
            kolik = "dnes" if po == 0 else f"už {po} dní"
            otazka(f"{stranka} — {t.get('id', '?')}",
                   f"**{t.get('otazka') or 'Platí tohle ještě?'}**\n"
                   f"    Věta na webu: „{citace[:160]}“\n"
                   f"    Termín kontroly byl {kdy} ({kolik}).\n"
                   f"    Když to už neplatí: {t.get('co_udelat', 'uprav větu na webu')}\n"
                   f"    Až to vyřídíš, zapiš do data/hlidka-tvrzeni.json k id "
                   f"„{t.get('id', '?')}“ buď nové `datum_kontroly`, nebo `\"vyrizeno\": true`.")
        else:
            cekajicich += 1

    vporadku(f"Tvrzení s datem spotřeby: {len(OTAZKY)} k vyřízení, "
             f"{cekajicich} hlídaných dál běží.")


# ---------------------------------------------------------------------------
# 6. ŽIVÝ WEB
# ---------------------------------------------------------------------------
def kontrola_ziveho_webu(stranky: dict[str, Stranka]) -> None:
    ok = 0
    hlavicky_overeny = False
    for jmeno in sorted(stranky):
        url = f"{ZIVY}/" if jmeno == "index.html" else f"{ZIVY}/{jmeno}"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                telo = r.read().decode("utf-8", "replace")
                hlavicky = {k.lower(): v for k, v in r.headers.items()}
                status = r.status
        except Exception as e:  # noqa: BLE001
            rozbite("živý web", f"{url} se nenačetl — {type(e).__name__}: {e}")
            continue

        if status != 200:
            rozbite("živý web", f"{url} vrátil {status}")
            continue
        if len(telo) < 2000:
            rozbite("živý web", f"{url} vrátil podezřele krátkou stránku ({len(telo)} znaků) — "
                                f"nasadilo se nasazení celé?")
            continue
        ok += 1

        if not hlavicky_overeny:
            hlavicky_overeny = True
            for h in POVINNE_HLAVICKY:
                if h not in hlavicky:
                    rozbite("bezpečnostní hlavičky",
                            f"živý web neposílá `{h}` — zkontroluj netlify.toml a nasazení")
            if "server" in hlavicky:
                vporadku(f"Živý web běží na: {hlavicky['server']}.")

    vporadku(f"Živý web: {ok} z {len(stranky)} stránek se načetlo (HTTP 200).")


# ---------------------------------------------------------------------------
# Hlášení
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 7. VIDITELNOST OBSAHU — nejzákeřnější porucha: stránka se načte, ale je bílá
# ---------------------------------------------------------------------------
# Vzniklo z ostré poruchy 30. 8. 2026: pravidlo `html.js .reveal{opacity:0}`
# přebilo `.reveal.in{opacity:1}`, protože má vyšší specificitu. Sekce dostaly
# příznak „ukaž se", ale zůstaly průhledné — pod hero bylo bílo. HTTP kódy,
# odkazy i čísla přitom seděly, takže to žádná dosavadní kontrola neviděla.

def _specificita(selektor: str) -> tuple:
    """Spočítá CSS specificitu (id, třídy/atributy/pseudotřídy, elementy)."""
    sel = re.sub(r"::[a-zA-Z-]+", " ", selektor)          # pseudoelementy zvlášť
    idcka = len(re.findall(r"#[\w-]+", sel))
    tridy = len(re.findall(r"\.[\w-]+", sel)) + len(re.findall(r"\[[^\]]+\]", sel)) \
        + len(re.findall(r":(?!not\()[a-zA-Z-]+", sel))
    elementy = len(re.findall(r"(?:^|[\s>+~])([a-zA-Z][\w-]*)", sel))
    return (idcka, tridy, elementy)


def _tridy_v(selektor: str) -> set:
    return set(re.findall(r"\.([\w-]+)", selektor))


def kontrola_viditelnosti() -> None:
    """Skrývá-li CSS obsah (opacity:0), musí existovat silnější pravidlo,
    které ho zase odkryje. Jinak zůstane web bílý, i když je obsah v HTML."""
    css = os.path.join(WEB, "styl.css")
    if not os.path.exists(css):
        return
    with open(css, encoding="utf-8") as f:
        zdroj = f.read()

    # pravidla „selektor { ... }" mimo @media (uvnitř @media je logika jiná)
    pravidla = []
    for m in re.finditer(r"([^{}@]+)\{([^{}]*)\}", zdroj):
        sel, telo = m.group(1).strip(), m.group(2)
        if not sel or sel.startswith("@"):
            continue
        op = re.search(r"(?:^|;|\s)opacity\s*:\s*([\d.]+)", telo)
        if op:
            pravidla.append((sel, float(op.group(1)), zdroj[:m.start()].count("\n") + 1))

    skryvaci = [p for p in pravidla if p[1] == 0]
    odkryvaci = [p for p in pravidla if p[1] > 0]

    for sel_s, _, radek_s in skryvaci:
        tridy_s = _tridy_v(sel_s)
        if not tridy_s:
            continue
        # Cílová třída = ta, na které skrývání visí (poslední v selektoru).
        # Odkrývací pravidlo ji musí obsahovat taky — a nemusí mít zbylé třídy
        # skrývacího selektoru; právě ten rozdíl bývá zdrojem chyby.
        posledni = re.findall(r"\.([\w-]+)", sel_s)
        if not posledni:
            continue
        cilova = posledni[-1]
        partneri = [o for o in odkryvaci
                    if cilova in _tridy_v(o[0]) and _tridy_v(o[0]) != tridy_s]
        if not partneri:
            continue  # nic to neodkrývá — buď je to záměr, nebo to řeší JS jinak
        nejsilnejsi = max(partneri, key=lambda o: _specificita(o[0]))
        if _specificita(nejsilnejsi[0]) <= _specificita(sel_s):
            rozbite("viditelnost",
                    f"styl.css:{radek_s} — `{sel_s}` skrývá obsah (opacity:0), ale "
                    f"`{nejsilnejsi[0]}` (řádek {nejsilnejsi[2]}), které ho má zase "
                    f"odkrýt, je slabší nebo stejně silné pravidlo. "
                    f"Specificita {_specificita(sel_s)} vs. {_specificita(nejsilnejsi[0])}. "
                    f"Obsah zůstane neviditelný — na webu bude bílo. "
                    f"Oprava: doplň do odkrývacího selektoru stejného předka "
                    f"(např. `{sel_s.rsplit(' ', 1)[0]} {nejsilnejsi[0].strip()}`).")
        else:
            vporadku(f"Odkrývání obsahu: `{nejsilnejsi[0]}` správně přebíjí `{sel_s}`.")


def najdi_chrome() -> str:
    """Cesta k prohlížeči pro vykreslovací test, nebo prázdno."""
    kandidati = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for jmeno in ("google-chrome", "chromium", "chromium-browser"):
        cesta = shutil.which(jmeno)
        if cesta:
            kandidati.append(cesta)
    for c in kandidati:
        if os.path.exists(c):
            return c
    return ""


def kontrola_vykresleni(stranky: dict) -> None:
    """Vykreslí živou hlavní stránku prohlížečem a ověří, že JavaScript
    opravdu naplnil obsah. Chytá pád skriptu, který HTML kontroly nevidí."""
    prohlizec = najdi_chrome()
    if not prohlizec:
        vporadku("Vykreslení v prohlížeči: přeskočeno (Chrome/Chromium není k dispozici).")
        return
    if not ZIVY:
        return

    # id kontejnerů, které plní JavaScript — musí být po vykreslení neprázdné
    cile = {"temata": "grafy rostoucích výdajů",
            "rows-vydaje": "rozklikávací rozpočet",
            "chart-rozpocet": "graf příjmů a výdajů"}
    # Chrome s `--dump-dom` vypíše hotový DOM, ale sám se neukončí. Píšeme
    # proto do souboru a proces ukončíme, jakmile výstup přestane růst.
    import subprocess, tempfile, time
    vystup = ""
    try:
        with tempfile.TemporaryDirectory() as tmp:
            dom = os.path.join(tmp, "dom.html")
            with open(dom, "w") as f:
                proc = subprocess.Popen(
                    [prohlizec, "--headless", "--disable-gpu", "--no-sandbox",
                     f"--user-data-dir={tmp}/profil", "--virtual-time-budget=9000",
                     "--dump-dom", ZIVY + "/"],
                    stdout=f, stderr=subprocess.DEVNULL)
                predchozi, stabilni = -1, 0
                for _ in range(40):                       # nejvýš ~40 s
                    time.sleep(1)
                    velikost = os.path.getsize(dom)
                    if velikost > 5000 and velikost == predchozi:
                        stabilni += 1
                        if stabilni >= 2:                 # dvě kola beze změny
                            break
                    else:
                        stabilni = 0
                    predchozi = velikost
                    if proc.poll() is not None:
                        break
                proc.kill()
                proc.wait(timeout=10)
            with open(dom, encoding="utf-8", errors="ignore") as f:
                vystup = f.read()
    except Exception as e:  # noqa: BLE001
        varovani("vykreslení", f"prohlížeč se nepodařilo spustit ({type(e).__name__}) "
                               f"— vykreslení se nekontroluje")
        return

    if len(vystup) < 5000:
        rozbite("vykreslení", "živá hlavní stránka se v prohlížeči nevykreslila "
                              "(prázdný výstup) — zkontroluj ji očima hned")
        return

    prazdne = []
    for cil, popis in cile.items():
        m = re.search(r'id="%s"[^>]*>(.*?)</' % re.escape(cil), vystup, re.S)
        if not m or len(m.group(1).strip()) < 40:
            prazdne.append(f"{popis} (#{cil})")
    if prazdne:
        rozbite("vykreslení", "po spuštění JavaScriptu zůstalo prázdné: "
                + ", ".join(prazdne)
                + ". Skript nejspíš spadl — otevři web v prohlížeči a přečti konzoli.")
    else:
        vporadku(f"Vykreslení v prohlížeči: {len(cile)} obsahových bloků se naplnilo.")


def hlaseni() -> str:
    dnes = date.today().isoformat()
    r = [f"# Hlídka webu {DOMENA or os.path.basename(KOREN)} — {dnes}", ""]

    if ROZBITE:
        stav = f"🔴 **{len(ROZBITE)} věcí je rozbitých**"
    elif OTAZKY:
        stav = f"❓ **{len(OTAZKY)} věcí čeká na tvoje rozhodnutí**"
    elif VAROVANI:
        stav = f"🟡 **{len(VAROVANI)} věcí stojí za mrknutí**"
    else:
        stav = "🟢 **Všechno v pořádku.**"
    r += [stav, ""]

    if OTAZKY:
        r += ["## ❓ Otázky pro tebe", "",
              "Tohle jsou věty na webu, kterým vypršelo datum kontroly. "
              "U každé odpověz a web podle toho uprav.", ""]
        for kde, co in OTAZKY:
            r += [f"### {kde}", "", co, ""]

    if ROZBITE:
        r += ["## 🔴 Rozbité — opravit", ""]
        for kde, co in ROZBITE:
            r += [f"- **{kde}** — {co}"]
        r += [""]

    if VAROVANI:
        r += ["## 🟡 Podívat se", ""]
        for kde, co in VAROVANI:
            r += [f"- **{kde}** — {co}"]
        r += [""]

    r += ["## 🟢 Co proběhlo", ""]
    for c in VPORADKU:
        r += [f"- {c}"]
    r += ["", "---", "",
          "Hlídku spouští `skripty/hlidac.py`. Věty s datem spotřeby se nastavují "
          "v `data/hlidka-tvrzeni.json`, čísla v `data/hlidka-cisla.json` — "
          "oba soubory jsou obyčejný text a dají se upravit ručně."]
    return "\n".join(r)


def main() -> int:
    ap = argparse.ArgumentParser(description="Denní hlídka webu Transparentní Prštice")
    ap.add_argument("--bez-site", action="store_true",
                    help="přeskočí kontroly, které potřebují internet")
    ap.add_argument("--report", default=None, help="kam zapsat hlášení (Markdown)")
    ap.add_argument("--tise", action="store_true", help="nevypisovat hlášení na obrazovku")
    ap.add_argument("--projekt", default=None,
                    help="kořen projektu (výchozí: složka nad tímhle skriptem)")
    ap.add_argument("--web", default=None,
                    help="složka s HTML stránkami (výchozí: najde se sama)")
    ap.add_argument("--data", default=None,
                    help="složka s daty pro grafy (výchozí: <projekt>/data)")
    ap.add_argument("--domena", default=None,
                    help="doména živého webu (výchozí: vyčte se ze sitemap.xml)")
    a = ap.parse_args()

    global KOREN, WEB, DATA, DOMENA, ZIVY
    if a.projekt:
        KOREN = os.path.abspath(a.projekt)
    WEB = os.path.abspath(a.web) if a.web else najdi_slozku_webu(KOREN)
    DATA = os.path.abspath(a.data) if a.data else os.path.join(KOREN, "data")
    DOMENA = (a.domena or zjisti_domenu(WEB)).lower().strip()
    ZIVY = f"https://{DOMENA}" if DOMENA else ""

    if not os.path.isdir(WEB):
        print(f"CHYBA: složka {WEB} neexistuje", file=sys.stderr)
        return 2

    stranky = nacti_stranky()
    if not stranky:
        print(f"CHYBA: v {WEB} nejsou žádné .html stránky", file=sys.stderr)
        return 2

    kontrola_odkazu_dovnitr(stranky)
    kontrola_zdroju(stranky)
    kontrola_cisel(stranky)
    kontrola_bloku(stranky)
    kontrola_tvrzeni(stranky)
    kontrola_viditelnosti()
    if a.bez_site:
        vporadku("Kontroly přes internet přeskočeny (--bez-site).")
    else:
        kontrola_odkazu_ven(stranky)
        if DOMENA:
            kontrola_ziveho_webu(stranky)
            kontrola_vykresleni(stranky)
        else:
            varovani("živý web", "nepodařilo se zjistit doménu (chybí sitemap.xml, "
                                 "CNAME i robots.txt) — živý web se nekontroluje. "
                                 "Doménu lze zadat přepínačem --domena.")

    text = hlaseni()
    if not a.tise:
        print(text)
    if a.report:
        os.makedirs(os.path.dirname(os.path.abspath(a.report)), exist_ok=True)
        with open(a.report, "w", encoding="utf-8") as f:
            f.write(text + "\n")

    if ROZBITE:
        return 2
    if OTAZKY or VAROVANI:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
