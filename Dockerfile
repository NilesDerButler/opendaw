# openDAW — MekoTools-Auslieferung als fertiges Abbild
#
# Gebaut wird aus dem festgeschriebenen Quelltext-Abzug des Originals (FASSUNG
# unten). Geändert werden nur die Stellen, an denen das Werkzeug den Anbieter
# kontaktieren würde (Klangbibliothek, Statistik, Besucherzählung, Live-Räume,
# Demo-Stücke, Plugin-Ablage, Cloud-Dienste, FFmpeg-Kern, eine Schrift von
# Google). scripts/anpassen.py prüft für jede Änderung den Anker und bricht bei
# Abweichung ab — lieber kein Abbild als ein stillschweigend falsches.
#
# Der Bau folgt dem Rezept des Originals (dessen CI): Node 22/24, Rust mit
# wasm32-Ziel (stable + nightly für die Geräte-Module), binaryen. Ohne Rust
# liesse sich nur die Oberfläche bauen, nicht die Klangmaschine.
#
# Zur Laufzeit ruft das Werkzeug keine fremde Adresse auf.

# Die Grundabbilder sind austauschbar: Docker Hub drosselt anonyme Abrufe von
# geteilten Bauservern (HTTP 429). Der Bauablauf versucht es erst amtlich und
# bei Fehlschlag über den öffentlichen Spiegel (siehe .github/workflows).
ARG BASIS_NODE=node:24-bookworm
ARG BASIS_NGINX=nginx:alpine-slim

FROM ${BASIS_NODE} AS bau

# Festgeschriebener Stand: 3ae072ef269f35d5bac868dbaf9bb4f68909c66d (2026-10-09).
ARG QUELLE=https://github.com/andremichelle/openDAW/archive/3ae072ef269f35d5bac868dbaf9bb4f68909c66d.tar.gz
ARG FASSUNG=3ae072ef269f35d5bac868dbaf9bb4f68909c66d
# Prüfsummen des FFmpeg-Kerns (@ffmpeg/core 0.12.6, MIT) — siehe README.
ARG FFMPEG_JS_SUMME=c972f5abeafcd5f3949e54edfbdc74a9badb27025809feb1945d468ffbcfb7f1
ARG FFMPEG_WASM_SUMME=2390efa7fb66e7e42dbae15427571a5ffc96b829480904c30f471f0a78967f61

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl python3 build-essential pkg-config libssl-dev binaryen \
 && rm -rf /var/lib/apt/lists/*

# Rust: stable für die Klangmaschine, nightly mit rust-src für die Geräte-Module
# (die brauchen -Zbuild-std).
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
      | sh -s -- -y --profile minimal --default-toolchain stable \
 && . "$HOME/.cargo/env" \
 && rustup target add wasm32-unknown-unknown \
 && rustup toolchain install nightly --profile minimal --component rust-src \
 && rustup target add wasm32-unknown-unknown --toolchain nightly
ENV PATH=/root/.cargo/bin:$PATH

WORKDIR /quelle
RUN curl -fsSL "$QUELLE" | tar xz --strip-components=1 \
 && test -f package.json && test -d packages/app/studio

# Änderungen am Original — mit Ankerprüfung (bricht bei Abweichung ab).
COPY scripts/anpassen.py /anpassen.py
RUN python3 /anpassen.py /quelle

# Eigene Klangbibliothek (freie CC0-Klänge, siehe klaenge/manifest.json).
COPY klaenge /klaenge
COPY scripts/bibliothek-bauen.py /bibliothek-bauen.py
RUN python3 /bibliothek-bauen.py /quelle/packages/app/studio/public

# Klangbibliothek des Anbieters kommt NICHT mit: sie enthält gekaufte Paketware
# (ModeAudio, Loopmasters). Stattdessen liefert /library die eigenen Klänge.

# FFmpeg-Kern selbst ausliefern (Original lädt ihn vom Anbieter nach).
RUN mkdir -p /quelle/packages/app/studio/public/ffmpeg \
 && curl -fsSL -o /quelle/packages/app/studio/public/ffmpeg/ffmpeg-core.js \
      https://unpkg.com/@ffmpeg/core@0.12.6/dist/esm/ffmpeg-core.js \
 && curl -fsSL -o /quelle/packages/app/studio/public/ffmpeg/ffmpeg-core.wasm \
      https://unpkg.com/@ffmpeg/core@0.12.6/dist/esm/ffmpeg-core.wasm \
 && echo "$FFMPEG_JS_SUMME  /quelle/packages/app/studio/public/ffmpeg/ffmpeg-core.js" | sha256sum -c - \
 && echo "$FFMPEG_WASM_SUMME  /quelle/packages/app/studio/public/ffmpeg/ffmpeg-core.wasm" | sha256sum -c -

# Keine Sponsorendatei vom Anbieter holen: leere Datei. Sie stand im Original
# für Bilder von avatars.githubusercontent.com — die entfallen damit.
RUN printf '{\n  "fetchedAt": null,\n  "totalCount": 0,\n  "sponsors": []\n}\n' \
      > /quelle/packages/app/studio/public/sponsors.json

# Kein Plugin-Katalog des Anbieters: die Fenster für WebCLAP-Plugins bleiben leer.
ENV VITE_WCLAP_ORIGIN=""

RUN npm ci --no-audit --no-fund
RUN npm run build \
 && test -s packages/app/studio/dist/index.html \
 && test -s packages/app/studio/dist/library/index.json \
 && test -s packages/app/studio/dist/ffmpeg/ffmpeg-core.wasm \
 && echo "--- Buendelgroesse:" && du -sh packages/app/studio/dist \
 && echo "--- Bibliothek:" && ls packages/app/studio/dist/library | wc -l

FROM ${BASIS_NGINX}
COPY --from=bau /quelle/packages/app/studio/dist/ /usr/share/nginx/html/
COPY config/default.conf /etc/nginx/conf.d/default.conf
# Selbstkontrolle: eine fehlerhafte Konfiguration soll den Bau scheitern lassen
# und nicht erst im Betrieb zu einem Neustart-Kreis führen.
RUN nginx -t
EXPOSE 80
