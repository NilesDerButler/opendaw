#!/usr/bin/env python3
"""Änderungen am festgeschriebenen Quelltext von openDAW für die MekoTools-Auslieferung.

Aufruf: python3 anpassen.py <quellverzeichnis>

Zwei Aufgaben, beide mit Prüfung:

1. **Alle Fremdaufrufe entfernen.** openDAW lädt zur Laufzeit von den Servern des
   Anbieters (Klangbibliothek, Besucherzählung, Statistik, Live-Räume, Demo-Stücke,
   Plugin-Katalog, eine Schrift von Google). Wir betreiben das Werkzeug selbst,
   also zeigen diese Wege künftig auf die eigene Adresse oder entfallen.
   Die Klangbibliothek des Anbieters wird dabei **nicht** mitgeliefert: sie
   enthält gekaufte Paketware (ModeAudio, Loopmasters). Stattdessen liefert
   scripts/bibliothek-bauen.py eigene, freie Klänge aus.

2. **Live-Räume abschalten** (eigene Datei, siehe DATEIERSATZ unten) — sie sind
   ohne den Server des Anbieters nicht möglich.

Jede Ersetzung nennt die erwartete Trefferzahl. Passt ein Anker nicht, bricht
der Bau ab (Hausregel: lieber kein Abbild als ein stillschweigend falsches).
Zum Schluss läuft eine Kontrolle: bleibt irgendwo im ausgelieferten Quelltext
eine fremde Adresse in einer Anweisung (nicht in einem Kommentar), bricht der
Bau ebenfalls ab.
"""
import re
import sys
from pathlib import Path

QUELLEN = [
    # (Datei, alter Text, neuer Text)
    # --- Klangbibliothek auf die eigene Adresse ---
    ("packages/app/studio/src/opendaw-api/OpenSampleAPI.ts",
     '    static readonly ApiRoot = "https://api.opendaw.studio/samples"',
     '    static readonly ApiRoot = "/library"'),
    ("packages/app/studio/src/opendaw-api/OpenSampleAPI.ts",
     '    static readonly FileRoot = "https://assets.opendaw.studio/samples"',
     '    static readonly FileRoot = "/library"'),
    # --- Klangschriften (Soundfonts): eigener Ort, wir liefern keine mit ---
    ("packages/app/studio/src/opendaw-api/OpenSoundfontAPI.ts",
     '    static readonly ApiRoot = "https://api.opendaw.studio/soundfonts"',
     '    static readonly ApiRoot = "/soundfonts"'),
    ("packages/app/studio/src/opendaw-api/OpenSoundfontAPI.ts",
     '    static readonly FileRoot = "https://assets.opendaw.studio/soundfonts"',
     '    static readonly FileRoot = "/soundfonts"'),
    # --- Besucherzählung: abschalten ---
    ("packages/app/studio/src/VisitorReporter.ts",
     'const API_URL = "https://api.opendaw.studio/users/count.php"',
     'const API_URL = "/library/users/count"'),
    ("packages/app/studio/src/VisitorReporter.ts",
     '    navigator.sendBeacon(API_URL)',
     '    // MekoTools: keine Besuchermeldung an den Anbieter.\n    void API_URL'),
    # --- Raumstatistik ---
    ("packages/app/studio/src/service/RoomStatsReporter.ts",
     'const ENDPOINT = "https://api.opendaw.studio/rooms/room-counter.php"',
     'const ENDPOINT = "/library/rooms/counter"'),
    # --- Statistikseiten ---
    ("packages/app/studio/src/ui/pages/stats/data.ts",
     '"https://api.opendaw.studio/rooms/rooms-result.json"', '"/stats/rooms-result.json"'),
    ("packages/app/studio/src/ui/pages/stats/data.ts",
     '"https://api.opendaw.studio/rooms/rooms-duration.json"', '"/stats/rooms-duration.json"'),
    ("packages/app/studio/src/ui/pages/stats/data.ts",
     '"https://logs.opendaw.studio/status.php"', '"/stats/status.json"'),
    ("packages/app/studio/src/ui/pages/stats/data.ts",
     '"https://api.opendaw.studio/users/unique.json"', '"/stats/unique.json"'),
    ("packages/app/studio/src/ui/pages/ErrorsPage.tsx",
     "fetch(`https://logs.opendaw.studio/list.php?offset=${offset}&limit=${loadLimit}`)",
     "fetch(`/stats/list.php?offset=${offset}&limit=${loadLimit}`)"),
    ("packages/app/studio/src/ui/pages/ErrorsPage.tsx",
     'fetch("https://logs.opendaw.studio/status.php")', 'fetch("/stats/status.json")'),
    # --- Veröffentlichen von Stücken ---
    ("packages/app/studio/src/ui/info-panel/PublishMusic.ts",
     '"https://api.opendaw.studio/music/upload.php"', '"/music/upload.php"'),
    ("packages/app/studio/src/ui/info-panel/PublishMusic.ts",
     '"https://api.opendaw.studio/music/delete.php"', '"/music/delete.php"'),
    ("packages/app/studio/src/ui/pages/OpenBundlePage.tsx",
     "fetch(`https://api.opendaw.studio/music/uploads/${folder}/project.odb`)",
     "fetch(`/music/uploads/${folder}/project.odb`)"),
    # --- Demo-Stücke des Anbieters ---
    ("packages/app/studio/src/ui/dashboard/DemoProject.tsx",
     "? `https://api.opendaw.studio/music/cover.php?id=${json.id}&preview=true`",
     "? `/music/cover.php?id=${json.id}&preview=true`"),
    ("packages/app/studio/src/ui/dashboard/DemoProjectsList.tsx",
     'const listUrl = `https://api.opendaw.studio/music/list-by-ids.php?ids=${ids.join(",")}`',
     'const listUrl = `/music/list-by-ids.php?ids=${ids.join(",")}`'),
    ("packages/app/studio/src/ui/dashboard/DemoProjectsList.tsx",
     "fetch(`https://api.opendaw.studio/music/uploads/${json.id}/project.odb`)",
     "fetch(`/music/uploads/${json.id}/project.odb`)"),
    # --- Prüfseite für die Klangtrennung (Modelle von fremden Ablagen) ---
    ("packages/app/studio/src/ui/pages/SpikeTestPage.tsx",
     'label: "assets.opendaw.studio htdemucs v4 (304 MB, MIT) — DEFAULT"',
     'label: "eigene Ablage htdemucs v4 (304 MB, MIT)"'),
    ("packages/app/studio/src/ui/pages/SpikeTestPage.tsx",
     'url: "https://assets.opendaw.studio/models/htdemucs/v4/model.onnx"',
     'url: "/models/htdemucs.onnx"'),
    ("packages/app/studio/src/ui/pages/SpikeTestPage.tsx",
     'label: "smank/htdemucs-onnx via Hugging Face (304 MB, MIT) — fallback / known-good"',
     'label: "smank/htdemucs-onnx (304 MB, MIT) — zweite Quelle"'),
    ("packages/app/studio/src/ui/pages/SpikeTestPage.tsx",
     'url: "https://huggingface.co/smank/htdemucs-onnx/resolve/469b019bf7ac20e03dc68a8fa791323434862390/htdemucs.onnx"',
     'url: "/models/htdemucs-smank.onnx"'),
    ("packages/app/studio/src/ui/pages/SpikeTestPage.tsx",
     'label: "jackjiangxinfa/demucs-onnx via Hugging Face (304 MB, Apache-2.0) — alternate"',
     'label: "jackjiangxinfa/demucs-onnx (304 MB, Apache-2.0) — dritte Quelle"'),
    ("packages/app/studio/src/ui/pages/SpikeTestPage.tsx",
     'url: "https://huggingface.co/jackjiangxinfa/demucs-onnx/resolve/49fcb820b3fa39937e955dda5cef1ad35dec1f7c/model.onnx"',
     'url: "/models/demucs.onnx"'),
    ("packages/app/studio/src/ui/pages/SpikeTestPage.tsx",
     'url: "https://huggingface.co/ModernMube/HTDemucs_onnx/resolve/edd8347a8191d6b73635675688d01e125d3ae336/htdemucs.onnx"',
     'url: "/models/htdemucs-modernmube.onnx"'),
    ("packages/app/studio/src/ui/pages/SpikeTestPage.tsx",
     "<span>The default candidate is the openDAW-hosted copy (assets.opendaw.studio). The\n"
     "                    Hugging Face fallbacks are kept around so the spike still functions if the openDAW\n"
     "                    CDN is unreachable, and so the original \"known fail\" export remains documented as\n"
     "                    a regression test for ORT-Web's strict shape validator.</span>",
     "<span>In dieser Fassung werden keine Modelle nachgeladen; die Klangtrennung ist\n"
     "                    damit nicht verfügbar.</span>"),
    # --- Fehlermeldungen an den Anbieter: entfällt ---
    ("packages/app/studio/src/errors/ErrorHandler.ts",
     'fetch("https://logs.opendaw.studio/log.php"', 'fetch("/stats/log.php"'),
    # --- Plugin-Ablage (WebCLAP) und Voreinstellungen ---
    ("packages/app/studio/src/opendaw-api/OpenWclapAPI.ts",
     'static readonly FileRoot = "https://assets.opendaw.studio/wclaps"',
     'static readonly FileRoot = "/library/wclaps"'),
    ("packages/app/studio/src/opendaw-api/OpenPresetAPI.ts",
     'static readonly ApiRoot = "https://api.opendaw.studio/presets"',
     'static readonly ApiRoot = "/library/presets"'),
    ("packages/app/studio/src/opendaw-api/OpenPresetAPI.ts",
     'static readonly FileRoot = "https://assets.opendaw.studio/presets"',
     'static readonly FileRoot = "/library/presets"'),
    # --- Raum-Server (nur über den abgeschalteten Live-Raum erreichbar) ---
    ("packages/studio/core/src/ysync/YService.ts",
     'const ONLINE_SERVER_URL = "wss://live.opendaw.studio"',
     'const ONLINE_SERVER_URL = "wss://" + location.host + "/live-room"'),
    ("packages/studio/p2p/src/AssetPeerConnection.ts",
     '{urls: "turn:live.opendaw.studio:3478", username: "opendaw", credential: "opendaw"}',
     '{urls: "turn:kein-server.invalid:3478", username: "abgeschaltet", credential: "abgeschaltet"}'),
    # --- Modelle für Klangtrennung, Tonhöhe und Tempo: eigene Ablage ---
    ("packages/lib/inference/src/tasks/StemSeparationTask.ts",
     'url: "https://assets.opendaw.studio/models/htdemucs/v4/model.onnx"',
     'url: "/models/htdemucs.onnx"'),
    ("packages/lib/inference/src/tasks/StemSeparationTask.ts",
     'url: "https://assets.opendaw.studio/models/htdemucs-jx/v4/model.onnx"',
     'url: "/models/htdemucs-jx.onnx"'),
    ("packages/lib/inference/src/tasks/BasicPitchTask.ts",
     'url: "https://assets.opendaw.studio/models/basic-pitch/v0.4.0/model.onnx"',
     'url: "/models/basic-pitch.onnx"'),
    ("packages/lib/inference/src/tasks/TempoDetectionTask.ts",
     'url: "https://assets.opendaw.studio/models/tempo-cnn/v0/model.onnx"',
     'url: "/models/tempo-cnn.onnx"'),
    # --- FFmpeg-Kern (Klangausgabe/Video) auf die eigene Ablage ---
    ("packages/studio/core/src/ffmpeg/FFmpegWorker.ts",
     '        const baseURL = "https://package.opendaw.studio" // mirror of https://unpkg.com/@ffmpeg/core@0.12.6/dist/esm',
     '        // MekoTools: der FFmpeg-Kern liegt im eigenen Abbild unter /ffmpeg\n'
     '        // (Quelle: @ffmpeg/core 0.12.6, MIT — siehe README).\n'
     '        const baseURL = "/ffmpeg"'),
    # --- Statistikseite: Angaben über GitHub und Discord ---
    ("packages/app/studio/src/ui/pages/stats/data.ts",
     "await fetchJson<RepoResponse>(`https://api.github.com/repos/${GITHUB_REPO}`)",
     "await fetchJson<RepoResponse>(`/stats/repo.json?repo=${GITHUB_REPO}`)"),
    ("packages/app/studio/src/ui/pages/stats/data.ts",
     "`https://api.github.com/repos/${GITHUB_REPO}/contributors?per_page=100`)",
     "`/stats/contributors.json?repo=${GITHUB_REPO}&per_page=100`)"),
    ("packages/app/studio/src/ui/pages/stats/data.ts",
     "`https://discord.com/api/v10/invites/${DISCORD_INVITE}?with_counts=true`)",
     "`/stats/discord.json?invite=${DISCORD_INVITE}`)"),
    # --- Speichern in fremden Cloud-Diensten: abgeschaltet ---
    ("packages/studio/core/src/cloud/CloudAuthManager.ts",
     'authUrlBase: "https://www.dropbox.com/oauth2/authorize",', 'authUrlBase: "/cloud/dropbox/authorize",'),
    ("packages/studio/core/src/cloud/CloudAuthManager.ts",
     'tokenUrl: "https://api.dropboxapi.com/oauth2/token",', 'tokenUrl: "/cloud/dropbox/token",'),
    ("packages/studio/core/src/cloud/CloudAuthManager.ts",
     'const scope = "https://www.googleapis.com/auth/drive.appdata"',
     'const scope = "/cloud/google/scope"'),
    ("packages/studio/core/src/cloud/CloudAuthManager.ts",
     "const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`",
     "const authUrl = `/cloud/google/auth?${params.toString()}`"),
    ("packages/studio/core/src/cloud/GoogleDriveHandler.ts",
     'const DRIVE_FILES_API = "https://www.googleapis.com/drive/v3/files"',
     'const DRIVE_FILES_API = "/cloud/google/files"'),
    ("packages/studio/core/src/cloud/GoogleDriveHandler.ts",
     'const DRIVE_UPLOAD_API = "https://www.googleapis.com/upload/drive/v3/files"',
     'const DRIVE_UPLOAD_API = "/cloud/google/upload"'),
    # --- Schrift von Google: entfällt ---
    ("packages/app/studio/src/ui/meter/VUMeter.tsx",
     '    const getGoogleFontUrl = (fontFamily: string, fontWeight: number) =>\n'
     '        `url("https://fonts.googleapis.com/css?family=${fontFamily.replace(" ", "+")}:${fontWeight}")`',
     '    // MekoTools: keine Schrift von einem fremden Server laden.\n'
     '    const getGoogleFontUrl = (fontFamily: string, fontWeight: number) => {\n'
     '        void fontWeight\n'
     '        return `local("${fontFamily}")`\n'
     '    }'),
]

# Ganze Dateien, die ersetzt werden.
DATEIERSATZ = {
    "packages/app/studio/src/service/StudioLiveRoomConnect.ts": '''// MekoTools-Fassung dieser Datei.
//
// Im Original verbindet connectRoom den Rechner mit dem Raum-Server des Anbieters
// (wss://live.opendaw.studio) und meldet das Ergebnis an dessen Statistik. Beides
// entfällt: Wir betreiben keinen Raum-Server, und Fremdaufrufe sind in dieser
// Auslieferung nicht erlaubt. Statt still nichts zu tun, sagt die Oberfläche es.
import {Optional, RuntimeNotifier} from "@opendaw/lib-std"
import {StudioService} from "@/service/StudioService"

export const connectRoom = async (_service: StudioService,
                                 _prefillRoomName?: Optional<string>): Promise<void> => {
    RuntimeNotifier.notify({message: "Gemeinsames Arbeiten in Echtzeit ist in dieser Fassung abgeschaltet."})
}
''',
}

# Adressen, die im ausgelieferten Quelltext in keiner Anweisung mehr vorkommen dürfen.
# (Verweise in Kommentaren sind erlaubt; reine Verweise zum Anklicken in der
# Oberfläche — etwa ein Newsletter-Link — sind keine Aufrufe und stehen hier nicht.)
FREMD = [
    "api.opendaw.studio",
    "assets.opendaw.studio",
    "logs.opendaw.studio",
    "live.opendaw.studio",
    "opendaw-plugins.studio",
    "package.opendaw.studio",
    "fonts.googleapis.com",
    "huggingface.co",
    "api.github.com",
    "githubusercontent.com",
    "discord.com",
    "googleapis.com",
    "accounts.google.com",
    "api.dropboxapi.com",
    "www.dropbox.com",
    "unpkg.com",
]

# Prüfdateien (Tests) werden nicht mit ausgeliefert und bleiben außen vor.
UEBERSPRINGEN = ("/test/", ".test.ts", ".test.tsx", "/tests/")

PRUEFORDNER = [
    "packages/app/studio/src",
    "packages/app/studio/public",
    "packages/app/studio/index.html",
    "packages/studio",
    "packages/lib",
]


def pruefe(datei: Path) -> str:
    if not datei.exists():
        raise SystemExit("Datei fehlt: %s" % datei)
    return datei.read_text(encoding="utf8")


def ersetze(wurzel: Path, datei: str, alt: str, neu: str) -> None:
    pfad = wurzel / datei
    text = pruefe(pfad)
    anzahl = text.count(alt)
    if anzahl != 1:
        raise SystemExit("Anker passt nicht (%d Treffer) in %s:\n%s" % (anzahl, datei, alt[:160]))
    pfad.write_text(text.replace(alt, neu), encoding="utf8")


def ist_kommentar(zeile: str) -> bool:
    zeile = zeile.strip()
    return zeile.startswith("//") or zeile.startswith("*") or zeile.startswith("/*")


def kontrolle(wurzel: Path) -> None:
    treffer = []
    for ordner in PRUEFORDNER:
        ziel = wurzel / ordner
        if not ziel.exists():
            continue
        dateien = [ziel] if ziel.is_file() else [p for p in ziel.rglob("*") if p.is_file()
                                                and p.suffix in (".ts", ".tsx", ".js", ".jsx", ".html", ".json", ".css")
                                                and "node_modules" not in p.parts
                                                and not any(t in "/" + str(p) for t in UEBERSPRINGEN)]
        for pfad in dateien:
            try:
                text = pfad.read_text(encoding="utf8")
            except (UnicodeDecodeError, IsADirectoryError):
                continue
            for nummer, zeile in enumerate(text.splitlines(), 1):
                for host in FREMD:
                    if host in zeile and not ist_kommentar(zeile):
                        treffer.append("%s:%d  %s" % (pfad.relative_to(wurzel), nummer, zeile.strip()[:120]))
    if treffer:
        raise SystemExit("Fremde Adressen in Anweisungen gefunden:\n" + "\n".join(treffer[:20]))
    print("Kontrolle: keine fremde Adresse mehr in einer Anweisung (%d Dateien geprüft)." % len(PRUEFORDNER))


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    wurzel = Path(sys.argv[1])
    for datei, alt, neu in QUELLEN:
        ersetze(wurzel, datei, alt, neu)
        print("geändert:", datei)
    for datei, inhalt in DATEIERSATZ.items():
        pfad = wurzel / datei
        pruefe(pfad)
        pfad.write_text(inhalt, encoding="utf8")
        print("ersetzt (ganze Datei):", datei)
    kontrolle(wurzel)
    print("Fertig: %d Ersetzungen, %d Dateien ersetzt." % (len(QUELLEN), len(DATEIERSATZ)))


if __name__ == "__main__":
    main()
