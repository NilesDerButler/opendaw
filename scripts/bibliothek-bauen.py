#!/usr/bin/env python3
"""Baut die eigene Klangbibliothek für die openDAW-Auslieferung.

Aufruf: python3 bibliothek-bauen.py <zielordner>

Erzeugt im Zielordner (dem öffentlichen Ordner des Studios):
  library/index.json   — Verzeichnis der Klänge im Format von openDAW
  library/<kennung>    — je eine WAV-Datei (PCM 16 Bit, 48 kHz, mono)
  soundfonts/index.json— leeres Verzeichnis für Klangschriften

Die Kennungen (UUID) und die Namen sind fest (siehe klangverzeichnis/) und
ändern sich nicht, damit ein Projekt, das auf einen Klang zeigt, ihn nach
einem neuen Bau wiederfindet.

Herkunft: klaenge/manifest.json (je Klang Freesound-Kennung, Urheber, Lizenz).
Alle Klänge sind CC0 (gemeinfrei) — Namensnennung ist freiwillig, wird aber
in der Anleitung genannt.
"""
import json
import shutil
import sys
import wave
from pathlib import Path

HIER = Path(__file__).resolve().parent
VERZEICHNIS = HIER.parent / "klaenge"


def dauer(pfad: Path) -> float:
    with wave.open(str(pfad), "rb") as datei:
        return datei.getnframes() / float(datei.getframerate())


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    ziel = Path(sys.argv[1])
    manifest = json.loads((VERZEICHNIS / "manifest.json").read_text(encoding="utf8"))
    if isinstance(manifest, dict):
        manifest = manifest["klaenge"]
    bibliothek = ziel / "library"
    if bibliothek.exists():
        shutil.rmtree(bibliothek)
    bibliothek.mkdir(parents=True)
    ordner: dict[str, list] = {}
    anzahl = 0
    for eintrag in manifest:
        quelle = VERZEICHNIS / eintrag["datei"]
        if not quelle.exists():
            raise SystemExit("Klangdatei fehlt: %s" % quelle)
        kennung = eintrag["uuid"]
        shutil.copyfile(quelle, bibliothek / kennung)
        name = eintrag["name"]
        ordner.setdefault(eintrag["ordner"], []).append({
            "uuid": kennung,
            "name": name,
            "bpm": 0,
            "duration": round(dauer(quelle), 6),
            "sample_rate": 48000
        })
        anzahl += 1
    index = {
        "version": 1,
        "folders": [{"name": name, "samples": klänge} for name, klänge in sorted(ordner.items())]
    }
    (bibliothek / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf8")
    # Klangschriften: wir liefern keine mit — der Weg muss aber antworten.
    klangschriften = ziel / "soundfonts"
    klangschriften.mkdir(parents=True, exist_ok=True)
    (klangschriften / "index.json").write_text(json.dumps({"version": 1, "folders": []}), encoding="utf8")
    print("%d Klänge in %d Ordnern abgelegt (%s)" % (anzahl, len(ordner), ziel))


if __name__ == "__main__":
    main()
