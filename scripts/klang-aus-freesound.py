#!/usr/bin/env python3
"""Freie (CC0) Klänge für die MekoTools-Klangbibliothek aus Freesound holen.

Warum eigenes Skript: Die Klangbibliothek des Originals (openDAW) enthält
gekaufte Paketware (ModeAudio, Loopmasters) und darf nicht weitergegeben werden.
Also beschaffen wir eigene Klänge — nur CC0, damit keine Namensnennung nötig ist
(sie wird trotzdem festgehalten), Herkunft nachvollziehbar im Manifest.

Ablauf je Rolle: suchen (CC0, Längengrenze, meistgeladen zuerst) -> Vorschau
laden (der HQ-Vorschau-Download ist der einzige Weg ohne OAuth) -> mit ffmpeg
dekodieren -> Stille am Anfang/Ende weg, auf -1 dBFS pegeln, als 16-Bit-WAV
schreiben -> Quelle ins Manifest.

Aufruf: python3 klang-aus-freesound.py [zielverzeichnis]
"""
import json
import math
import os
import re
import struct
import subprocess
import sys
import urllib.parse
import urllib.request
import uuid
import wave

ENV = "/opt/data/.env"
UA = {"User-Agent": "mekotools-klangbeschaffung/1.0"}

# (Ordner, Kurzname, Suchbegriffe (der Reihe nach), Anzahl, min. Länge, max. Länge in Sekunden)
ROLLEN = [
    ("Schlagzeug", "Kick", ["kick drum one shot", "bass drum one shot"], 6, 0.15, 1.2),
    ("Schlagzeug", "Snare", ["snare drum one shot"], 6, 0.15, 1.2),
    ("Schlagzeug", "Clap", ["hand clap one shot", "clap one shot"], 3, 0.10, 1.0),
    ("Schlagzeug", "HiHat", ["hi hat closed one shot", "closed hihat"], 4, 0.05, 0.8),
    ("Schlagzeug", "HiHat offen", ["open hi hat one shot", "open hihat"], 4, 0.10, 1.6),
    ("Schlagzeug", "Tom", ["tom drum one shot", "floor tom one shot"], 3, 0.20, 1.5),
    ("Schlagzeug", "Percussion", ["percussion one shot", "conga one shot"], 5, 0.10, 1.5),
    ("Schlagzeug", "Becken", ["crash cymbal one shot", "cymbal crash"], 3, 0.30, 3.0),
    ("Schlagzeug", "Ride", ["ride cymbal one shot", "ride cymbal"], 2, 0.30, 3.0),
    ("Schlagzeug", "Rimshot", ["rimshot one shot", "side stick"], 2, 0.05, 0.6),
    ("Schlagzeug", "Shaker", ["shaker one shot", "egg shaker"], 2, 0.10, 1.2),
    ("Baesse", "Bass", ["bass synth one shot", "sub bass one shot"], 4, 0.20, 2.0),
    ("Tasten", "Klavier", ["piano note one shot", "rhodes one shot", "electric piano note",
                           "marimba note", "organ note one shot"], 4, 0.30, 3.0),
    ("Effekte", "Effekt", ["synth stab one shot", "synth hit one shot"], 3, 0.10, 2.0),
]

MAX_LAENGE = 3.0          # Sekunden, danach wird gekappt
ZIEL_PEGEL = 0.891        # -1 dBFS
STILLE_SCHWELLE = 0.005   # relativ zur Spitze
VORSCHAU_TAIL = 0.02      # Sekunden Nachlauf am Ende behalten


def schluessel():
    for zeile in open(ENV):
        if zeile.startswith("FREESOUND_API_KEY="):
            return zeile.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("FREESOUND_API_KEY fehlt in " + ENV)


def suche(token, begriff, dauer_min, dauer_max, seite=1):
    q = urllib.parse.urlencode({
        "query": begriff,
        "filter": 'license:"Creative Commons 0" duration:[%s TO %s]' % (dauer_min, dauer_max),
        "sort": "downloads_desc",
        "fields": "id,name,username,license,duration,previews,num_downloads",
        "page_size": 15,
        "page": seite,
        "token": token,
    })
    r = urllib.request.Request("https://freesound.org/apiv2/search/text/?" + q, headers=UA)
    with urllib.request.urlopen(r, timeout=90) as a:
        return json.loads(a.read().decode()).get("results", [])


def dekodiere(pfad):
    """MP3 -> float-Liste (mono, 48 kHz) über ffmpeg."""
    p = subprocess.run(["ffmpeg", "-v", "quiet", "-i", pfad, "-ac", "1", "-ar", "48000",
                        "-f", "f32le", "-"], capture_output=True)
    if p.returncode != 0 or not p.stdout:
        raise RuntimeError("ffmpeg konnte %s nicht lesen" % pfad)
    roh = p.stdout
    return list(struct.unpack("<%df" % (len(roh) // 4), roh[:len(roh) // 4 * 4]))


def aufbereiten(werte, rate=48000):
    """Stille weg, Pegel setzen, Länge begrenzen."""
    if not werte:
        raise RuntimeError("leere Aufnahme")
    spitze = max(abs(w) for w in werte)
    if spitze < 1e-6:
        raise RuntimeError("Aufnahme ist still")
    schwelle = spitze * STILLE_SCHWELLE
    start = next((i for i, w in enumerate(werte) if abs(w) >= schwelle), 0)
    ende = next((i for i in range(len(werte) - 1, -1, -1) if abs(werte[i]) >= schwelle), len(werte) - 1)
    ende = min(len(werte), ende + int(rate * VORSCHAU_TAIL))
    werte = werte[start:ende]
    grenze = int(rate * MAX_LAENGE)
    if len(werte) > grenze:
        werte = werte[:grenze]
    faktor = ZIEL_PEGEL / max(abs(w) for w in werte)
    ausblenden = int(rate * 0.02)
    ergebnis = []
    for i, w in enumerate(werte):
        x = w * faktor
        rest = len(werte) - i
        if rest < ausblenden:
            x *= rest / ausblenden
        ergebnis.append(max(-1.0, min(1.0, x)))
    return ergebnis


def schreibe_wav(pfad, werte, rate=48000):
    with wave.open(pfad, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h", int(x * 32767)) for x in werte))


def sauberer_name(text, fallback):
    text = re.sub(r"[^A-Za-z0-9]+", " ", text).strip()
    text = re.sub(r"\s+", " ", text)
    return (text[:40] or fallback)


def main():
    ziel = sys.argv[1] if len(sys.argv) > 1 else "/opt/data/cache/scratch/opendaw-klang"
    token = schluessel()
    klang = os.path.join(ziel, "klaenge")
    os.makedirs(klang, exist_ok=True)
    manifest = []
    gesehen = set()
    lfd = {}
    for ordner, kurz, begriffe, anzahl, dmin, dmax in ROLLEN:
        genommen = 0
        for begriff in begriffe:
            if genommen >= anzahl:
                break
            treffer = suche(token, begriff, dmin, dmax)
            for t in treffer:
                if genommen >= anzahl:
                    break
                if t["id"] in gesehen:
                    continue
                vorschau = (t.get("previews") or {}).get("preview-hq-mp3")
                if not vorschau:
                    continue
                temp = os.path.join(ziel, "temp.mp3")
                urllib.request.urlretrieve(vorschau, temp)
                try:
                    werte = aufbereiten(dekodiere(temp))
                except Exception as fehler:
                    print("   übersprungen:", t["name"], "-", fehler)
                    continue
                lfd[kurz] = lfd.get(kurz, 0) + 1
                name = "%s %d" % (kurz, lfd[kurz])
                dateiname = "%s.wav" % re.sub(r"[^A-Za-z0-9]", "", name)
                zielpfad = os.path.join(klang, dateiname)
                schreibe_wav(zielpfad, werte)
                manifest.append({
                    "uuid": str(uuid.uuid4()),
                    "datei": dateiname,
                    "ordner": ordner,
                    "name": name,
                    "quelltitel": t["name"],
                    "autor": t["username"],
                    "lizenz": "CC0-1.0",
                    "quelle": "https://freesound.org/s/%d/" % t["id"],
                    "dauer": round(len(werte) / 48000.0, 4),
                    "abtastrate": 48000,
                    "dateigroesse": os.path.getsize(zielpfad),
                })
                gesehen.add(t["id"])
                genommen += 1
                print("   %-16s %5.2f s  %6.0f KB  %s" % (name, len(werte) / 48000.0,
                                                          os.path.getsize(zielpfad) / 1024, t["username"]))
        if genommen < anzahl:
            print("   Achtung: nur %d von %d für „%s“" % (genommen, anzahl, kurz))
    os.path.exists(os.path.join(ziel, "temp.mp3")) and os.remove(os.path.join(ziel, "temp.mp3"))
    with open(os.path.join(ziel, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
    gesamt = sum(e["dateigroesse"] for e in manifest)
    print("\n%d Klänge, %.1f MB, Manifest: %s/manifest.json" % (len(manifest), gesamt / 1048576, ziel))


if __name__ == "__main__":
    main()
