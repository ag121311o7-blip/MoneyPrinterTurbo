#!/usr/bin/env bash
# Genera 4 fondos animados de 8 s (1080x1920) con ffmpeg, para cuando no hay
# clave de Pexels. Uso: make_clips.sh <directorio_salida> [WxH]
set -euo pipefail
out="${1:?directorio de salida}"; size="${2:-1080x1920}"
mkdir -p "$out"
i=1
for colors in "0x3b1f0e:0xc68642:0x6f3b1a" "0x1d2b53:0xff7a59:0xffd166" \
              "0x2d0b3d:0x9b5de5:0xf15bb5" "0x0b3d2e:0x2ec4b6:0xcbf3f0"; do
  IFS=: read -r c0 c1 c2 <<<"$colors"
  ffmpeg -y -loglevel error -f lavfi \
    -i "gradients=s=${size}:c0=${c0}:c1=${c1}:c2=${c2}:n=3:speed=0.025:d=8" \
    -c:v libx264 -pix_fmt yuv420p -r 30 "$out/c$i.mp4"
  i=$((i + 1))
done
ls "$out"/c*.mp4 | paste -sd, -
