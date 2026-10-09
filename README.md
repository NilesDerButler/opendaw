# openDAW — MekoTools-Auslieferung

Dieses Verzeichnis baut ein fertiges Abbild (Docker-Image) des Musikstudios
[openDAW](https://github.com/andremichelle/openDAW) für den eigenen Betrieb.
Gebaut wird **nur** in der CI (GitHub Actions), ausgeliefert wird ein Container
mit statischen Dateien hinter nginx.

## Was das Abbild enthält

* die Web-Fassung des Studios, gebaut aus dem festgeschriebenen Quelltext-Abzug
  (FASSUNG im `Dockerfile`: `3ae072ef269f35d5bac868dbaf9bb4f68909c66d`, 2026-10-09),
* eine eigene Klangbibliothek mit **51 freien Klängen (CC0)** aus Freesound
  (`klaenge/manifest.json` nennt zu jedem Klang Urheber, Quelle und Lizenz),
* den FFmpeg-Kern (`@ffmpeg/core` 0.12.6, MIT), damit Ton und Video im Browser
  erzeugt werden können, ohne etwas nachzuladen.

## Was gegenüber dem Original geändert ist

`scripts/anpassen.py` ändert ausschließlich Stellen, die den Anbieter
kontaktieren würden. Für jede Änderung ist der erwartete Wortlaut (Anker)
hinterlegt; passt er nicht, bricht der Bau ab. Am Ende prüft das Skript, dass in
keiner Anweisung des ausgelieferten Quelltexts mehr eine fremde Adresse steht.

| Stelle | Original | hier |
| --- | --- | --- |
| Klangbibliothek (`OpenSampleAPI`) | `api.opendaw.studio`, `assets.opendaw.studio` | `/library` (eigene Klänge) |
| Klangschriften (`OpenSoundfontAPI`) | Anbieter | `/soundfonts` (leer, Weg antwortet) |
| Besucherzählung (`VisitorReporter`) | `sendBeacon` an den Anbieter | abgeschaltet |
| Raumstatistik (`RoomStatsReporter`) | Anbieter | eigener Weg (bleibt ungenutzt) |
| Live-Räume | `wss://live.opendaw.studio` | ganze Datei ersetzt: abgeschaltet, mit Hinweis in der Oberfläche |
| Statistik- und Fehlerseiten | `api/logs.opendaw.studio` | eigene Wege |
| Demo-Stücke, Veröffentlichen | `api.opendaw.studio/music` | eigene Wege |
| Plugin-Ablage (WebCLAP) | `assets.opendaw.studio/wclaps` | eigene Ablage, leer |
| Voreinstellungen | `api.opendaw.studio/presets` | eigene Ablage, leer |
| Sponsorenbilder | `avatars.githubusercontent.com` (über `sponsors.json`) | leere Datei, keine Bilder |
| FFmpeg-Kern | `package.opendaw.studio` | `/ffmpeg` im eigenen Abbild |
| Schrift im VU-Meter | `fonts.googleapis.com` | Schrift des Geräts |
| Klangtrennung/Tempo/Tonhöhe (Modelle) | `assets.opendaw.studio`, Hugging Face | eigene Wege (keine Modelle mitgeliefert) |
| Speichern in Cloud-Diensten | Google Drive, Dropbox | abgeschaltet (eigene Wege) |

Nicht mitgeliefert wird die Klangbibliothek des Anbieters: sie enthält gekaufte
Paketware (ModeAudio, Loopmasters) und darf nicht weitergegeben werden.

## Bauen und betreiben

```bash
# Bau (dauert lange: die Klangmaschine ist in Rust geschrieben)
docker build -t opendaw .

# Betrieb
docker run -d --name mekotools-opendaw -p 8080:80 opendaw
```

Die Seite braucht Kopfzeilen für Kreuzherkunft-Isolation
(`Cross-Origin-Opener-Policy`, `Cross-Origin-Embedder-Policy`) — sie stehen in
`config/default.conf`. Wird das Werkzeug hinter einen Reverse Proxy gestellt,
müssen sie dort durchgereicht werden.

## Datenschutz

Zur Laufzeit ruft die Seite **keine** fremde Adresse auf: keine Zählung, keine
Statistik, keine Schrift, keine Klänge und keine Bilder von anderen Servern. Das
lässt sich im Browser unter „Netzwerk“ nachzählen. Die Content-Security-Policy
im ausliefernden nginx verbietet Fremdaufrufe zusätzlich (`connect-src 'self'`).

## Lizenzen

* openDAW: **AGPL-3.0** (siehe `LICENSE` des Originals). Wir geben den Quelltext
  dieser Fassung mit heraus; die Änderungen sind in `scripts/anpassen.py`
  vollständig beschrieben.
* Klänge: **CC0-1.0** (gemeinfrei), Urheber und Quellen in `klaenge/manifest.json`.
* FFmpeg-Kern: **MIT** (`@ffmpeg/core` 0.12.6).
* Tubular-Klangkassetten im Original: CC0, GPL-3.0 (Dexed/SynprezFM), MIT.

Näheres in `NOTICE`.
