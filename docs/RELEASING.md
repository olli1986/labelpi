# Updates veröffentlichen (für Maintainer)

LabelPi prüft auf GitHub, ob es eine neuere Version gibt, und zeigt dann in der Weboberfläche den Update-Hinweis an.
Welche Version „die neueste“ ist, wird so bestimmt:

1. Gibt es im Repository mindestens ein **Release**, gilt das **neueste Release** (Tag z. B. `v0.7.1`). Nur diese Versionen werden angeboten – halbfertige Änderungen auf `main` erreichen die Nutzer nicht.
2. Gibt es **kein** Release, gilt die Zahl in der Datei **`VERSION`** auf dem `main`-Zweig.

## Empfohlener Ablauf (ohne Git-Kenntnisse, nur im Browser)
1. **Dateien ändern:** auf GitHub im Repository *Add file → Upload files* (bestehende Dateien werden überschrieben) oder eine Datei öffnen und mit dem Stift-Symbol bearbeiten. Mit *Commit changes* speichern.
2. **Version hochzählen:** Datei `VERSION` bearbeiten, z. B. von `0.7.0` auf `0.7.1` (Schema `Haupt.Neben.Fehlerkorrektur`).
3. **Release erstellen:** *Releases → Draft a new release* → bei *Choose a tag* `v0.7.1` eintippen und *Create new tag* wählen → Titel und Beschreibung eintragen (die Beschreibung erscheint den Nutzern als Update-Hinweis) → *Publish release*.

Danach sehen alle Installationen innerhalb von ca. 6 Stunden den Hinweis (oder sofort über *Einstellungen → Update → Nach Updates suchen*).

> Tipp: Der Tag (`v0.7.1`) und die Zahl in `VERSION` (`0.7.1`) müssen übereinstimmen.

## Mit Git auf dem PC
```
git add -A
git commit -m "Beschreibung der Änderung"
git push
git tag v0.7.1
git push --tags
```
Das Release mit Beschreibung legst du danach wie in Schritt 3 auf GitHub an.

## Wichtig
- Nur Dateien im Repository werden verteilt. `labels.db` (Daten) und der Ordner `lang/` (eigene Sprachen) liegen nur auf dem Pi und werden nie überschrieben.
- Neue Python-Pakete in `requirements.txt` werden beim Update automatisch installiert. Neue **Systempakete** (apt) gehören in `install.sh` – dann erscheint für die Nutzer der Hinweis, es einmal auszuführen.
- Zusätzliche Sprachen: Datei `static/lang/xx.json` (Aufbau siehe Anleitung, Abschnitt Sprachen) ins Repository legen.
- Gitea: Die Update-Funktion nutzt aktuell die GitHub-Schnittstellen.
