#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anonymizace PDF dokumentů pro veřejný web (PLAN.md úkol 2.5, ZADANI P-8b).

Redakce se NEŘEŠÍ překrytím textu obdélníkem — text se z dokumentu skutečně
odstraní (PyMuPDF apply_redactions), takže ho nejde vybrat ani vykopírovat.
Zároveň se z dokumentu smažou metadata.

Co se odstraňuje:
  * adresa trvalého pobytu žadatele,
  * ID datové schránky (žadatele i povinného subjektu — je to neveřejný údaj),
  * datum narození a rodné číslo,
  * soukromý e-mail a telefon.

Co ZŮSTÁVÁ (vědomě):
  * jméno Petra Novotného — je autorem webu a veřejně se k podáním hlásí,
  * jména úředníků a funkcionářů v úřední roli,
  * čísla jednací a spisové značky — bez nich by dokument nešlo ověřit,
  * obec Prštice, její sídlo a IČO — veřejné údaje povinného subjektu.

Spuštění:  python3 skripty/anonymizace.py            (vytvoří veřejné deriváty)
           python3 skripty/anonymizace.py --kontrola (jen ověří hotové soubory)
"""
import os, re, sys, json, hashlib
from datetime import datetime

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("CHYBA: chybí PyMuPDF (pip3 install pymupdf)")

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACT = os.path.expanduser("~/Documents/AI/0_PACT/0_Projects/4_PRŠTICE")
PRIV = os.path.expanduser("~/Developer/transparentniprstice-private")
CIL = os.path.join(WEB, "web", "dokumenty")   # publikuje se celá složka web/

# vzory citlivých údajů (case-insensitive)
VZORY = [
    (r"Ořechovská\s*\d+[^\n,;]{0,18}", "adresa"),
    (r"\bID\s*(?:DS|datové\s*schránky)?\s*[:\s]\s*[a-z0-9]{7}\b", "ID datové schránky"),
    (r"(?:datum\s+narození|nar\.)\s*[:\s]*\d{1,2}\.\s?\d{1,2}\.\s?(?:19|20)\d{2}", "datum narození"),
    (r"\bAdresa\s+trvalého\s+pobytu\s*:?[^\n]{0,40}", "adresa"),
    (r"\b\d{6}\s?/\s?\d{3,4}\b", "rodné číslo"),
    (r"[\w.\-]+@(?!prstice\.cz|kr-jihomoravsky\.cz)[\w.\-]+\.\w{2,}", "e-mail"),
    (r"\b(?:\+420\s?)?7\d{2}\s?\d{3}\s?\d{3}\b", "telefon"),
]

# (zdroj, cílový název, popis pro rejstřík)
DOKUMENTY = [
    (f"{PACT}/2026_07_28 Opatření proti nečinnosti KrÚ JMK/Priloha_1_Zadost_o_informace_2026-07-01.pdf",
     "2026-07-01_zadost_detail-smluv-518.pdf",
     "Žádost o smlouvy, faktury a výkazy práce k vybraným položkám účtu 518"),
    (f"{PACT}/2026_07_17 Stížnost 16a a nová žádost 518/2026_07_17_Stiznost_16a_ucet_518.pdf",
     "2026-07-17_stiznost-16a.pdf",
     "Stížnost na postup obce při vyřizování žádosti (§ 16a InfZ)"),
    (f"{PACT}/2026_07_28 Opatření proti nečinnosti KrÚ JMK/2026_07_28_Zadost_opatreni_proti_necinnosti_KrU_JMK.pdf",
     "2026-07-28_opatreni-proti-necinnosti.pdf",
     "Žádost ke Krajskému úřadu o opatření proti nečinnosti obce"),
    (f"{PRIV}/zdroje/datovka/2026-07-17_obec_odpoved_OUPR-867-2026.pdf",
     "2026-07-17_odpoved-obce-OUPR-867-2026.pdf",
     "Sdělení obce Prštice — odpověď na žádost z 1. 7. 2026"),
    (f"{PRIV}/zdroje/datovka/2026-08-19_KrU_JMK_rozhodnuti.pdf",
     "2026-08-19_rozhodnuti-KrU-JMK.pdf",
     "Rozhodnutí Krajského úřadu JMK — přikazuje obci žádost vyřídit"),
    (f"{PACT}/2026_08_15 Opakovaná žádost o informace - GDPR/2026_08_16_Zadost_106_GDPR_pausal.pdf",
     "2026-08-15_zadost-GDPR-pausal.pdf",
     "Žádost o rámcovou smlouvu a rozsah plnění pověřence GDPR"),
    (f"{PACT}/2026_08_15 Žádost o informace soudní procesy/2026_08_15_Zadost_soudni_rizeni_obce.pdf",
     "2026-08-15_zadost-soudni-rizeni.pdf",
     "Žádost o přehled soudních řízení obce od 1. 1. 2018"),
    (f"{PACT}/2026_08_25 Žádost o informace - detail účtu 511/2026_08_25_Zadost_106_ucet_511.pdf",
     "2026-08-25_zadost-ucet-511.pdf",
     "Žádost o rozpis účtu 511 „Opravy a udržování“ za období 1. 1. 2020 – 30. 6. 2026"),
    (f"{PACT}/2026_06_23 Zpravodaje obce Prštice/zadost-106-zpravodaje-prstice.pdf",
     "2026-06-23_zadost-zpravodaje.pdf",
     "Žádost o obecní zpravodaje ve strojově čitelné podobě"),
]


def najdi_citlive(text):
    """Vrátí seznam (nalezený řetězec, druh údaje)."""
    out = []
    for vzor, druh in VZORY:
        for m in re.finditer(vzor, text, re.I):
            out.append((m.group(0).strip(), druh))
    return out


def anonymizuj(zdroj, cil):
    """Vypálí redakce a smaže metadata. Vrací seznam provedených zásahů."""
    d = fitz.open(zdroj)
    zasahy = []
    for i, strana in enumerate(d, 1):
        for nalez, druh in najdi_citlive(strana.get_text()):
            for obdelnik in strana.search_for(nalez):
                strana.add_redact_annot(obdelnik, fill=(0, 0, 0))
                zasahy.append({"strana": i, "druh": druh, "delka": len(nalez)})
        strana.apply_redactions()
    d.set_metadata({})           # pryč s autorem, titulkem, programem
    d.del_xml_metadata()
    d.save(cil, garbage=4, deflate=True, clean=True)
    d.close()
    return zasahy


# Konkrétní hodnoty, které se ve veřejné verzi nesmí objevit. Kontrola je
# schválně NEZÁVISLÁ na vzorech výše — kdyby měl vzor slepé místo, denylist ho
# odhalí. (Poučeno z chyby: „Datum narození:" nechytil vzor hledající „nar.".)
DENYLIST = [
    "evfezzc",              # ID datové schránky žadatele
    "13. 1. 1984", "13.1.1984",
    "Ořechovská",
]


def zkontroluj(cil):
    """Ověří, že ve veřejné verzi už žádný citlivý údaj není."""
    d = fitz.open(cil)
    text = "\n".join(p.get_text() for p in d)
    # 'format' a 'encryption' jsou technické údaje o souboru, ne osobní údaje
    TECHNICKE = {"format", "encryption"}
    meta = {k: v for k, v in (d.metadata or {}).items() if v and k not in TECHNICKE}
    d.close()
    nalezy = najdi_citlive(text)
    for zakazane in DENYLIST:
        if zakazane.lower() in text.lower():
            nalezy.append((zakazane, "DENYLIST"))
    return nalezy, meta


def main():
    jen_kontrola = "--kontrola" in sys.argv
    os.makedirs(CIL, exist_ok=True)
    rejstrik, celkem_zasahu, problemy = [], 0, []

    for zdroj, nazev, popis in DOKUMENTY:
        cil = os.path.join(CIL, nazev)
        if not os.path.exists(zdroj):
            problemy.append(f"chybí zdroj: {zdroj}")
            continue
        if not jen_kontrola:
            zasahy = anonymizuj(zdroj, cil)
            celkem_zasahu += len(zasahy)
        zbytky, meta = zkontroluj(cil)
        stav = "OK" if not zbytky and not meta else "!!! NÁLEZ"
        if zbytky:
            problemy.append(f"{nazev}: zůstalo {[z[1] for z in zbytky]}")
        if meta:
            problemy.append(f"{nazev}: metadata {list(meta)}")
        d = fitz.open(cil); stran = len(d); d.close()
        rejstrik.append({"soubor": nazev, "popis": popis, "stran": stran,
                         "velikost_kb": round(os.path.getsize(cil) / 1024),
                         "sha256": hashlib.sha256(open(cil, "rb").read()).hexdigest()[:16]})
        print(f"  {stav:9} {nazev:48} {stran} str.")

    with open(os.path.join(WEB, "data", "dokumenty.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": {
            "poznamka": "Veřejné anonymizované deriváty. Odstraněny: adresa, ID datové "
                        "schránky, datum narození, rodné číslo, soukromý e-mail a telefon. "
                        "Text je z dokumentu skutečně odstraněn, nejen překryt.",
            "vygenerovano": datetime.now().strftime("%Y-%m-%d %H:%M")},
            "dokumenty": rejstrik}, f, ensure_ascii=False, indent=1)

    print(f"\n  dokumentů: {len(rejstrik)} | redakcí: {celkem_zasahu}")
    if problemy:
        for p in problemy:
            print("  PROBLÉM:", p)
        sys.exit("NEPROŠLO — nevyřešené nálezy, publikace se zastavuje.")
    print("  kontrola: 0 nevyřešených nálezů, 0 metadat ✓")


if __name__ == "__main__":
    main()
