# Anleitung: openDAW bedienen

openDAW ist ein Musikstudio im Browser. Man legt Klänge auf Spuren, baut ein
Schlagzeug aus einzelnen Schlägen zusammen, spielt eine Melodie ein, mischt
alles und sichert das Ergebnis als Datei. Es ist **kein Konto** nötig; die
Aufnahmen bleiben auf dem Gerät.

Adresse: <https://opendaw.mekotools.de> — einfach im Browser öffnen.

---

## 1. Was man auf dem Bildschirm sieht

* **Oben die Werkzeugleiste**: links der Name des Stücks, in der Mitte die
  Abspielknöpfe, rechts Angaben zu Tempo (BPM) und Takt.
* **Links die Spuren**: Jede Spur ist eine Zeile. Dort liegen die Geräte, die
  Klänge erzeugen (Instrumente, Schlagzeug, Aufnahme).
* **Unten die Zeitleiste**: Sie läuft von links nach rechts. Die senkrechte
  Linie ist der **Abspielkopf** — er zeigt, wo man gerade hört.
* **Der Reiterkasten unten** („Piano Roll", „Drum Grid", „Mixer"): je nachdem,
  welches Gerät gerade gewählt ist, zeigt er Noten, Schläge oder Lautstärken.

Englische Beschriftungen: Die Oberfläche kommt vom Original und ist englisch.
Die wichtigsten Wörter stehen am Ende dieser Anleitung in einer Liste.

## 2. Ein neues Stück beginnen

1. Beim Öffnen erscheint die Startseite. Wähle **„New Project"**.
2. Das leere Stück hat einen Taktgeber („Metronome") und eine Mischpult-Spur.
3. Rechts oben stellt man das **Tempo** ein (BPM). Für erste Versuche passen
   90 oder 120 BPM.
4. Damit der Browser Ton abspielen darf, muss man **einmal auf Abspielen
   drücken** (oder irgendwo in die Seite klicken) — Browser erlauben Ton erst
   nach einer Berührung. Das ist keine Fehlfunktion.

## 3. Klänge: die eigene Klangbibliothek

openDAW kann Klänge aus einer Bibliothek laden. Dieses MekoTools-Studio bringt
eine **eigene Sammlung mit 51 freien Klängen (CC0)** — sie liegt auf unserem
Server und wird nicht von fremden Servern nachgeladen.

1. Spur hinzufügen („Add Track"), dann ein Instrument, das Klänge abspielt
   (z. B. **Vaporisateur** oder **Playfield**).
2. Im Gerät den Klangbereich öffnen (Knopf mit dem Ordner- oder Notensymbol)
   und **„Library"** wählen.
3. Es erscheinen die Ordner:
   * **Schlagzeug** — Kick, Snare, Clap, HiHat, offenes HiHat, Tom,
     Percussion, Becken, Ride, Rimshot, Shaker
   * **Baesse** — vier Bassklänge
   * **Tasten** — vier Tastenklänge
   * **Effekte** — drei Klänge für Akzente
4. Klang anklicken: Er wird geladen und ist hörbar, sobald man einen Ton
   auslöst.

Zusätzlich bringt das Studio eigene Klangerzeuger mit, die **ohne** Klänge
auskommen: **Tubular** (Klangkassetten, u. a. „Tubular Classics", CC0),
**Nano**, **Apparat** und weitere. Damit lässt sich sofort Musik machen, auch
ohne die Bibliothek zu öffnen.

## 4. Ein Schlagzeug programmieren (Drum Grid)

1. Ein Gerät wählen, das Schläge auf ein Raster legt (z. B. **Playfield**).
2. Der Reiter **„Drum Grid"** zeigt ein Raster: links die Klänge, oben die
   Schritte im Takt.
3. Mit Klick auf ein Kästchen setzt man einen Schlag; nochmal klicken löscht
   ihn.
4. Typisches Muster für einen Takt (16 Schritte): Kick auf 1, 9; Snare auf 5,
   13; HiHat auf jeden zweiten Schritt. Abspielen und weiterbauen.

## 5. Eine Melodie einspielen (Piano Roll)

1. Ein Instrument mit Noten (z. B. **Vaporisateur** mit einem Klang aus
   „Tasten" oder **Tubular**) wählen.
2. Der Reiter **„Piano Roll"** zeigt ein Notenraster. Mit Klick setzt man
   Noten; die Länge zieht man mit der Maus.
3. Wer ein MIDI-Tastatur hat, kann direkt einspielen: Gerät wählen, dann
   **„Aufnahme"** (roter Knopf) drücken und spielen.
4. Mit der Maus statt Tastatur: Note setzen, dann mit dem Lautsprecher-Symbol
   anhören.

## 6. Mit dem Mikrofon aufnehmen

1. Spur hinzufügen und **Aufnahme** („Audio Input" / „Audio Recording")
   wählen. Der Browser fragt nach Erlaubnis für das Mikrofon — erlauben.
2. Abspielkopf an die Stelle setzen, an der die Aufnahme beginnen soll.
3. Aufnahme starten, spielen oder sprechen, Aufnahme beenden. Die Spur
   erscheint als Wellenform in der Zeitleiste.
4. Aufnahmen bleiben **auf dem Gerät**; sie werden erst verschickt, wenn man
   das Stück ausdrücklich teilt (siehe Abschnitt 8).

## 7. Mischen und verändern

* Jede Spur hat einen **Lautstärkeregler** und einen **Pan-Regler** (links /
  rechts). Im Reiter **„Mixer"** stehen alle nebeneinander.
* Effekte wie Hall („Reverb") oder Filter legt man als Gerät auf die Spur.
* Mit **„Solo"** hört man eine Spur allein, mit **„Mute"** schaltet man sie
  stumm — gut, um Fehler zu suchen.
* Der Knopf **„Undo"** nimmt den letzten Schritt zurück; **„Redo"** holt ihn
  wieder.

## 8. Sichern und wieder öffnen

* **Sichern**: Menü oben rechts → **„Export"** → **„Project Bundle"** (oder
  „Save Project"). Es entsteht eine Datei (`.odb`), die man speichern kann.
  Diese Datei enthält das ganze Stück samt verwendeter Klänge.
* **Ton fertigstellen**: Menü → **„Export"** → **„Audio"** (WAV/MP3). Beim
  ersten Mal lädt der Browser das dafür nötige Zusatzprogramm (FFmpeg) — bei
  uns **vom eigenen Server**, nicht aus dem Netz.
* **Öffnen**: Startseite → **„Open Project"** → Datei auswählen.

## 9. Was in dieser Fassung abgeschaltet ist

Damit das Studio **keine fremden Server** kontaktiert, fehlen einige Funktionen
des Originals. Das ist Absicht:

* **Live-Räume** (gemeinsames Arbeiten in Echtzeit): brauchen den Server des
  Anbieters. Beim Klick erscheint ein Hinweis.
* **Klangbibliothek des Anbieters**: enthält gekaufte Klangpakete, die wir nicht
  weitergeben dürfen. Stattdessen die 51 freien Klänge.
* **Demo-Stücke**, **Plugin-Katalog**, **Klangtrennung** (Stimmen aus einem
  Stück herauslösen), **Klangschriften** und **Speichern in fremden
  Cloud-Diensten** (Google Drive, Dropbox).
* Die **Statistikseite** zeigt keine Angaben über fremde Server.

## 10. Wörterliste (englisch → deutsch)

* Add Track — Spur hinzufügen
* Audio Input — Tonaufnahme (Mikrofon)
* BPM / Tempo — Schläge pro Minute, Geschwindigkeit
* Drum Grid — Raster für Schlagzeug
* Export — Ausgabe/Sichern (Projektdatei oder Ton)
* Loop — Schleife, wiederkehrender Abschnitt
* Metronome — Taktgeber
* Mixer — Mischpult
* Mute — stumm schalten
* Piano Roll — Notenraster
* Playhead — Abspielkopf (senkrechte Linie)
* Quantize — auf das Raster einrasten
* Redo / Undo — wiederholen / zurücknehmen
* Sample / Library — Klang / Klangbibliothek
* Solo — nur diese Spur hören
* Track — Spur
* Volume / Pan — Lautstärke / links-rechts

## 11. Wenn etwas nicht geht

* **Kein Ton**: einmal auf Abspielen gedrückt? Browser fragen erst nach einer
  Berührung. Lautsprecher/Kopfhörer und Systemlautstärke prüfen.
* **Mikrofon geht nicht**: Im Browser die Erlaubnis für die Seite prüfen
  (Schloss-Symbol links in der Adresszeile).
* **Seite lädt lange**: Beim ersten Start werden Bündel und Klänge geladen;
  danach liegt vieles im Zwischenspeicher.
* **Etwas wirkt englisch und unklar**: Wörterliste oben benutzen; die
  Funktionen sind dieselben wie im Original.
