"""Ejecuta cli.py de MoneyPrinterTurbo haciendo que Edge TTS use el proxy HTTPS.

En las sesiones en la nube la salida a Internet pasa por un proxy, pero
edge_tts (aiohttp) no lee HTTPS_PROXY por su cuenta. Este lanzador se lo pasa
sin modificar el código de la aplicación. Uso, desde la raíz del repo:

    SSL_CERT_FILE=/root/.ccr/ca-bundle.crt uv run python .claude/skills/generar-video/run_cli.py [args de cli.py]
"""

import os
import runpy
import sys

import edge_tts

_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
_original_init = edge_tts.Communicate.__init__


def _init_with_proxy(self, *args, **kwargs):
    if _proxy:
        kwargs.setdefault("proxy", _proxy)
    _original_init(self, *args, **kwargs)


edge_tts.Communicate.__init__ = _init_with_proxy
sys.argv = ["cli.py"] + sys.argv[1:]
sys.path.insert(0, os.getcwd())
runpy.run_path("cli.py", run_name="__main__")
