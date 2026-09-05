#!/usr/bin/env python3
"""Lokální náhled webu, který se chová stejně jako ostrý web na Netlify.

Obyčejný `python3 -m http.server` posílá jiné hlavičky než Netlify, takže
se náhled v drobnostech chová jinak — hlavně PDF, které se místo zobrazení
nabídne ke stažení. Tenhle server čte netlify.toml a napodobuje z něj to,
co je při prohlížení poznat: hlavičky a přesměrování krátkých adres.

Spuštění:  python3 skripty/nahled.py [port]      (výchozí port 8778)
"""
import os
import re
import sys
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

KOREN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(KOREN, "web")
TOML = os.path.join(KOREN, "netlify.toml")


def nacti_netlify(cesta):
    """Vytáhne z netlify.toml dvojice (vzor, hlavičky) a (odkud, kam) pro přesměrování."""
    try:
        with open(cesta, encoding="utf-8") as f:
            zdroj = f.read()
    except OSError:
        return [], []

    # deploy-preview kontext se na lokální náhled nevztahuje
    zdroj = re.sub(r'(?ms)^\[\[context\.[^\]]+\]\].*?(?=^\[\[|\Z)', '', zdroj)

    hlavicky = []
    for blok in re.findall(r'(?ms)^\[\[headers\]\]\s*\n(.*?)(?=^\[\[|\Z)', zdroj):
        vzor = re.search(r'for\s*=\s*"([^"]+)"', blok)
        if not vzor:
            continue
        dvojice = re.findall(r'^\s*([A-Za-z-]+)\s*=\s*"([^"]*)"', blok, re.M)
        hlavicky.append((vzor.group(1), [(k, v) for k, v in dvojice if k.lower() != "for"]))

    presmerovani = []
    for blok in re.findall(r'(?ms)^\[\[redirects\]\]\s*\n(.*?)(?=^\[\[|\Z)', zdroj):
        odkud = re.search(r'from\s*=\s*"([^"]+)"', blok)
        kam = re.search(r'to\s*=\s*"([^"]+)"', blok)
        stav = re.search(r'status\s*=\s*(\d+)', blok)
        if odkud and kam:
            presmerovani.append((odkud.group(1), kam.group(1), int(stav.group(1)) if stav else 301))
    return hlavicky, presmerovani


def sedi(vzor, cesta):
    """Netlify vzor '/dokumenty/*' proti cestě '/dokumenty/neco.pdf'."""
    return re.fullmatch(re.escape(vzor).replace(r'\*', '.*'), cesta) is not None


HLAVICKY, PRESMEROVANI = nacti_netlify(TOML)


class Nahled(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _presmeruj(self):
        cesta = self.path.split("?", 1)[0].rstrip("/") or "/"
        for odkud, kam, stav in PRESMEROVANI:
            if cesta == odkud:
                self.send_response(stav)
                self.send_header("Location", kam)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return True
        return False

    def send_head(self):
        if self._presmeruj():
            return None
        return super().send_head()

    def end_headers(self):
        # Konkrétnější pravidlo přebíjí obecnější — stejnou hlavičku poslat jen jednou.
        cesta = self.path.split("?", 1)[0]
        vysledek = {}
        for vzor, dvojice in HLAVICKY:
            if sedi(vzor, cesta):
                for k, v in dvojice:
                    vysledek[k] = v
        for k, v in vysledek.items():
            self.send_header(k, v)
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        """Nenalezenou adresu ukázat stejně jako Netlify — vlastní stránkou 404.html."""
        stranka = os.path.join(WEB, "404.html")
        if code == 404 and os.path.isfile(stranka):
            with open(stranka, "rb") as f:
                telo = f.read()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(telo)))
            self.end_headers()
            self.wfile.write(telo)
            return
        super().send_error(code, message, explain)

    def log_message(self, fmt, *args):
        if "404" in (args[1] if len(args) > 1 else ""):
            super().log_message(fmt, *args)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8778
    handler = functools.partial(Nahled, directory=WEB)
    print(f"Náhled běží na http://localhost:{port}  (složka web/, hlavičky podle netlify.toml)")
    print(f"  hlavičkových pravidel: {len(HLAVICKY)} · přesměrování: {len(PRESMEROVANI)}")
    ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    main()
