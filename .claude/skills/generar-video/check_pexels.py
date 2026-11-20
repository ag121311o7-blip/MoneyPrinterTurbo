"""Comprueba si Pexels está disponible y deja config.toml listo para usarlo.

Imprime una sola línea:
  pexels  -> Pexels responde con la clave (real o inyectada por el proxy)
  local   -> no hay clave válida; usar fondos generados con make_clips.sh

La clave puede venir de dos sitios:
  1. pexels_api_keys en config.toml (clave real escrita por el usuario).
  2. Un "Network secret" del entorno para api.pexels.com: el proxy de la
     sesión sustituye la cabecera Authorization por la clave real. En ese caso
     la app solo necesita un valor de relleno en config.toml, que este script
     escribe ("proxy-injected").

Uso, desde la raíz del repo:  uv run python .claude/skills/generar-video/check_pexels.py
"""

import re
import sys
from pathlib import Path

import requests
import toml

PLACEHOLDER = "proxy-injected"
CONFIG = Path("config.toml")
TEST_URL = "https://api.pexels.com/v1/videos/search?query=nature&per_page=1"


def pexels_ok(key: str) -> bool:
    try:
        r = requests.get(TEST_URL, headers={"Authorization": key}, timeout=15)
    except requests.RequestException as exc:
        print(f"aviso: no se pudo contactar con Pexels: {type(exc).__name__}", file=sys.stderr)
        return False
    if r.status_code != 200:
        print(f"aviso: Pexels respondió {r.status_code}", file=sys.stderr)
    return r.status_code == 200


def set_config_keys(keys: list[str]) -> None:
    text = CONFIG.read_text(encoding="utf-8")
    line = "pexels_api_keys = [" + ", ".join(f'"{k}"' for k in keys) + "]"
    new_text, n = re.subn(r"(?m)^pexels_api_keys\s*=.*$", line, text, count=1)
    if n == 0:
        new_text = text.replace("[app]", "[app]\n" + line, 1)
    CONFIG.write_text(new_text, encoding="utf-8")


def main() -> None:
    if not CONFIG.exists():
        print("aviso: falta config.toml (cp config.example.toml config.toml)", file=sys.stderr)
        print("local")
        return
    keys = toml.loads(CONFIG.read_text(encoding="utf-8")).get("app", {}).get("pexels_api_keys") or []
    if isinstance(keys, str):
        keys = [keys]
    real_keys = [k for k in keys if k and k != PLACEHOLDER]

    if real_keys and pexels_ok(real_keys[0]):
        print("pexels")
        return
    if pexels_ok(PLACEHOLDER):
        # El proxy inyecta la clave real; la app solo necesita un valor no vacío.
        if keys != [PLACEHOLDER] and not real_keys:
            set_config_keys([PLACEHOLDER])
        print("pexels")
        return
    print("local")


if __name__ == "__main__":
    main()
