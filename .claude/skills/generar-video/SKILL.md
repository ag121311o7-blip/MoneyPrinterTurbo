---
name: generar-video
description: Genera un vídeo corto (TikTok, Reels, Shorts o YouTube) con MoneyPrinterTurbo a partir de un tema o un guion, y entrega el MP4 al usuario. Úsala siempre que el usuario pida un vídeo, un reel, un short o un TikTok, en cualquier idioma ("hazme un vídeo de…", "make a video about…").
---

# Generar un vídeo con MoneyPrinterTurbo

Todos los comandos se ejecutan desde la raíz del repositorio. El usuario habla español: respóndele en español.

## 1. Preparar (solo si hace falta)

- Si no existe `.venv/`, ejecuta `uv python install 3.11 && uv sync --frozen`.
- Si no existe `config.toml`, ejecuta `cp config.example.toml config.toml` (git lo ignora).

## 2. Concretar el encargo

Si el usuario no lo dice, usa estos valores por defecto y no preguntes:

| Opción | Por defecto | Argumento de `cli.py` |
|---|---|---|
| Formato | vertical 9:16 | `--video-aspect 9:16` (`16:9` para YouTube) |
| Idioma | español de España | `--video-language es-ES` |
| Voz | Álvaro (masculina) | `--voice-name es-ES-AlvaroNeural-Male` (femenina: `es-ES-ElviraNeural-Female`; México: `es-MX-JorgeNeural-Male` / `es-MX-DaliaNeural-Female`) |
| Duración | unos 20–40 s | longitud del guion: unas 60–100 palabras |
| Música | aleatoria, volumen bajo | `--bgm-type random --bgm-volume 0.15` |
| Subtítulos | Be Vietnam Pro, 70 px, tercio inferior | `--font-name BeVietnamPro-Bold.ttf --font-size 70 --subtitle-position two_thirds_bottom` |

## 3. Guion

Si `llm_provider` en `config.toml` no tiene clave, escribe tú el guion: frase gancho inicial, 2–4 datos, cierre con llamada a la acción. Comprueba los datos; no inventes cifras. Pásalo con `--video-script "…"` y añade `--video-subject "<tema>"`. Si el usuario da su propio guion, úsalo tal cual.

## 4. Material de vídeo

Para los clips de Pexels, prepara términos de búsqueda en inglés (3–6, separados por comas) con `--video-terms` y usa `--video-source pexels`. La clave puede llegar por dos vías:
- **Secreto de red del entorno:** la inyecta el proxy. En ese caso pon en `config.toml` `pexels_api_keys = ["proxy-injected"]`.
- **Clave real** dentro de `pexels_api_keys`.

Si Pexels responde 401/403 o no hay clave, usa fondos generados en local:

```bash
CLIPS=$(.claude/skills/generar-video/make_clips.sh "$SCRATCH/clips")   # para 16:9 añade 1920x1080
# luego: --video-source local --video-materials "$CLIPS" --video-concat-mode sequential --video-transition-mode fade-in --video-clip-duration 4
```

`$SCRATCH` es el directorio scratchpad de la sesión. Avisa al usuario de que los fondos son provisionales y de cómo añadir la clave: ajustes del entorno, **Network secrets**, host `api.pexels.com`, cabecera `Authorization`, valor de la clave **sin** prefijo `Bearer`. Nunca le pidas que pegue claves en el chat.

## 5. Generar

Lanza siempre a través de `run_cli.py`, que hace que Edge TTS use el proxy (sin él falla con un error de DNS):

```bash
SSL_CERT_FILE=/root/.ccr/ca-bundle.crt timeout 580 uv run python .claude/skills/generar-video/run_cli.py \
  --video-subject "…" --video-script "…" --video-language es-ES \
  --video-aspect 9:16 --voice-name es-ES-AlvaroNeural-Male \
  --bgm-type random --bgm-volume 0.15 \
  --font-name BeVietnamPro-Bold.ttf --font-size 70 --subtitle-position two_thirds_bottom \
  <argumentos de material del paso 4> 2>&1 | tail -5
```

- La última línea es un JSON con `result.videos[0]`, la ruta del MP4 en `storage/tasks/<id>/`, carpeta ignorada por git.
- `--task-id`, si lo usas, debe ser un UUID.
- Si falla la red (403 del proxy o error de DNS), el host necesario debe estar en el entorno «MoneyPrinterTurbo». Los hosts ya permitidos son `speech.platform.bing.com`, `api.pexels.com`, `videos.pexels.com` e `images.pexels.com`.

## 6. Revisar y entregar

1. Comprueba duración y resolución: `ffprobe -v error -show_entries format=duration:stream=width,height -of compact <mp4>`.
2. Extrae un fotograma (`ffmpeg -ss 5 -i <mp4> -frames:v 1 -vf scale=360:-1 $SCRATCH/frame.png`) y míralo: que los subtítulos se lean y tengan acentos.
3. Envía el MP4 directamente desde `storage/tasks/…` con `SendUserFile` (`display: "render"`).
4. No copies vídeos fuera de `storage/` ni hagas commit de ellos.

Al terminar, resume en español: tema, duración, formato, voz y si los clips son de Pexels o provisionales.
