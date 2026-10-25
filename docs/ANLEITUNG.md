# LabelPi – Anleitung

## 1. Grundlagen
**Obere Leiste:** Drucker (nur sichtbar, wenn mehrere angeschlossen sind) · Rolle · Länge (nur bei Endlosrollen) · *gedreht* · Kopien · Dithering · Autoschnitt (nur bei Modellen mit Cutter) · **Drucken**.

- **Die gewählte Rolle muss zur eingelegten Rolle passen.** Die App fragt nach, wenn du die Rolle gegenüber dem letzten Druck wechselst.
- **gedreht:** Bei Endlosrollen wird die Länge waagerecht dargestellt und das Etikett beim Druck um 90° gedreht – so liest du es später wie am Bildschirm. Ohne Haken entspricht die Anzeige der Richtung quer zur Rolle.
- **Dithering:** Nur für Fotos/Graustufen sinnvoll (Rasterpunkte). Für Text, QR- und Barcodes **aus** lassen.
- **Schnittmarke** (nur Endlosrollen ohne Cutter): druckt eine gestrichelte Linie ans Etikettenende, damit du beim manuellen Abschneiden (z. B. QL-500) die richtige Stelle triffst.

**Bedienung im Designer**
- **Ansicht:** Standardmäßig sind nur die wichtigsten Funktionen sichtbar. Mit **Erweiterte Ansicht** (Leiste oben rechts) kommen Drehen, Dithering, Autoschnitt, Schnittmarke, Serie, Raster und Zoom dazu. Weitere Elemente (PDF, Formen, Symbole) findest du im Menü **＋ Mehr …**, Speichern/Export unter **Datei ▾**.
- Element hinzufügen über die Werkzeugleiste, **antippen** = auswählen, **ziehen** = verschieben, **Ecke unten rechts** = Größe ändern.
- Die **Eigenschaften** stehen in der Leiste unten und bleiben immer sichtbar. Dort gibt es auch Buttons zum Ausrichten am Etikett (links, Mitte, rechts, oben, unten).
- Beim Verschieben **rasten** Elemente an Rand, Mitte und Kanten anderer Elemente ein (rosa Hilfslinien).
- **↶ / ↷** machen Schritte rückgängig bzw. stellen sie wieder her (die letzten 25).

## 2. Elemente
| Element | Hinweise |
|---|---|
| **Text** | Mehrzeilig möglich. *Auto-Größe* füllt die Box mit der größtmöglichen Schrift (Box-Höhe festlegen). |
| **Symbol** | Warn-, Gefahren-, Recycling-Zeichen u. a. – sind Text in einer Symbolschrift, also frei skalierbar. |
| **QR-Code** | Beliebiger Text oder Link; Platzhalter erlaubt. |
| **Barcode** | Typ wählen (siehe unten). Bei ungültigem Inhalt erscheint eine rote Warnung und es wird **nicht** gedruckt. |
| **Bild** | Foto/Logo vom Gerät. Für Fotos Dithering einschalten. |
| **PDF** | Seitengröße wählt die passende Rolle. Mehrseitige PDFs können als Serie gedruckt werden (eine Seite pro Etikett). |
| **Formen** | Kreis, Linie, Pfeil, Dreieck – gefüllt oder als Umriss, in 45°-Schritten drehbar (Eigenschaften → Drehung). |
| **Tabelle** | Siehe Abschnitt 3. |

**Barcode-Typen**

| Typ | Eingabe |
|---|---|
| Code 128 | Beliebige Zeichen (Buchstaben, Ziffern, Sonderzeichen) |
| EAN-13 | 12 Ziffern (Prüfziffer wird ergänzt) |
| EAN-8 | 7 Ziffern |
| Code 39 | Großbuchstaben, Ziffern, `- . $ / + %` und Leerzeichen |
| GS1-128 | Mit Klammern, z. B. `(01)09501101530003(17)271231(10)AB12` |
| Datamatrix | Beliebiger Text, quadratisch |

## 3. Tabellen
- **Zelle antippen** = Zelle auswählen (blau markiert). **Doppelklick bzw. doppelt antippen** = direkt in der Zelle tippen. *Enter* übernimmt, *Tab* springt zur nächsten Zelle, *Esc* bricht ab.
- In den Eigenschaften: Zeilen/Spalten hinzufügen oder entfernen, Schrift, Linienstärke, *1. Zeile fett*.
- **Rahmen der Tabelle:** alle Linien · nur außen · Zeilenlinien · keiner.
- **Rahmen einer einzelnen Zelle:** Zelle auswählen und *oben / unten / links / rechts* ankreuzen. Das geht zusätzlich zum Tabellenrahmen – mit „keiner (nur Zellrahmen)“ bekommen nur die markierten Zellen Linien (z. B. nur eine Unterstrichlinie).
- Zu lange Texte werden automatisch kleiner, damit sie in die Zelle passen.
- Alternativ lässt sich der Inhalt als Text bearbeiten: eine Zeile pro Tabellenzeile, Spalten mit `;` getrennt.

## 4. Platzhalter
Platzhalter funktionieren in **Text, QR-Code, Barcode und Tabellenzellen**.

| Platzhalter | Bedeutung | Beispiel |
|---|---|---|
| `{n}` | Zähler innerhalb der Serie | 1, 2, 3 … |
| `{n:5}` | Zähler, 5-stellig mit führenden Nullen | 00001 |
| `{gesamt}` | Anzahl der Etiketten der Serie | `{n}/{gesamt}` → 3/10 |
| `{lfd}`, `{lfd:5}` | **Fortlaufender Zähler, der sich merkt** (auf dem Pi gespeichert, auch nach Neustart/Gerätewechsel) | 1001, 1002 … |
| `{lfd.rechnung}` | Benannter Zähler, beliebig viele möglich | unabhängig von `{lfd}` |
| `{datum}` | heutiges Datum | 24.10.2026 |
| `{datum:JJJJ-MM-TT}` | Datum mit eigenem Format (`JJJJ` `JJ` `MM` `TT`) | 2026-10-24 |
| `{datum+30}` | Datum plus 30 Tage (auch `-7`; Einheiten `d` Tage, `w` Wochen, `m` Monate, `j` Jahre) | 23.11.2026 · `{datum+6m:MM/JJJJ}` → 04/2027 |
| `{zeit}`, `{zeit:HH:MM:SS}` | Uhrzeit | 14:35 |
| `{jahr}` `{monat}` `{tag}` | einzelne Datumsteile (auch mit Versatz, z. B. `{jahr+1j}`) | 2026 · 10 · 24 |
| `{kw}` | ISO-Kalenderwoche (z. B. `{kw+2w}` = Woche in zwei Wochen) | 43 |
| `{wochentag}` `{monatname}` | Name in der Sprache der Oberfläche | Samstag / Saturday |
| `{zufall:8}` | Zufallscode (hier 8 Zeichen, ohne leicht verwechselbare wie 0/O und 1/I); jedes Etikett einer Serie bekommt einen anderen | K7HT3QWZ |
| `{uuid}` | zufällige UUID | 3f2a9c1e-… |
| `{Spaltenname}` | Wert aus der CSV-Spalte (nur bei CSV-Serie) | `{Name}` |

**Englische Kurzformen:** `{date}` `{time}` `{year}` `{month}` `{day}` `{weekday}` `{cw}` `{random}` `{total}` `{seq}`.

**Filter** (mit `|` anhängen, auch kombinierbar): `{Name|gross}` GROSSBUCHSTABEN · `{Name|klein}` kleinbuchstaben · `{Name|titel}` Wortanfänge groß · `{n:8|luhn}` hängt eine Luhn-Prüfziffer an · `{n:12|gtin}` hängt die EAN/GTIN-Prüfziffer an.

**Hinweise**
- Datum und Uhrzeit kommen vom Gerät, mit dem du druckst. Unbekannte Platzhalter bleiben unverändert stehen.
- `{lfd}` reserviert die Nummern erst beim Drucken. Schlägt der Druck fehl, wird der Zähler zurückgesetzt (keine Lücken). Den nächsten Wert siehst du in der Vorschau und unter *Einstellungen → Zähler*, dort kannst du ihn auch ändern.
- Beispiele: `SN-{jahr}-{lfd:4}` → `SN-2026-0001` · `Haltbar bis {datum+30}` · `KW {kw}/{jahr}` · `{n:11|gtin}` als EAN-Inhalt.

## 5. Serien („Serie…“)
- **Zähler:** Start, Schritt und Anzahl festlegen. Beispiel: Start 100, Schritt 5, Anzahl 10 → 100, 105, …, 145.
- **CSV-Datei:** Erste Zeile = Spaltennamen, danach pro Zeile ein Etikett. Trennzeichen `;` oder `,`, Kodierung UTF-8.
  ```
  Name;Artikel;Nummer
  Müller;Schraube M4;1001
  Schmidt;Mutter M4;1002
  ```
  Im Designer dann `{Name}`, `{Artikel}`, `{Nummer}` verwenden.
- **PDF-Seiten:** entstehen beim Import eines mehrseitigen PDFs.
- **Kopien** gelten pro Etikett der Serie. Gedruckt wird in Blöcken; im Verlauf erscheint nur das erste Etikett der Serie.
- Die Vorschau zeigt zuerst das erste Etikett; mit **‹ ›** neben „Serie…“ blätterst du durch alle Etiketten der Serie.

## 6. Raster („Raster…“)
Nur bei Endlosrollen. Mehrere Etiketten nebeneinander und untereinander auf einem Streifen:
1. *Etikettenbreite* in mm festlegen (z. B. 28 mm bei einer 62-mm-Rolle für zwei Spalten).
2. *Spalten × Zeilen* und *Abstand* einstellen.
3. Beim Drucken füllen aufeinanderfolgende Etiketten (Kopien oder Serie) das Raster. Passt das Raster nicht auf die Rolle, erscheint eine Fehlermeldung.

## 7. Vorlagen, Verlauf, Export, Backup
- **Vorlagen:** Mit „Als Vorlage speichern“ ablegen, in **Ordnern** sortieren, bearbeiten (Name/Ordner) und exportieren.
- **Verlauf:** Jeder Druck und jedes „Speichern“ landet hier. *Nochmal drucken*, *Bearbeiten* oder per *Auswählen* mehrere löschen/exportieren.
- **Export/Import:** Etiketten und Vorlagen als JSON-Datei, z. B. zum Weitergeben. **⬇ PNG/PDF** exportiert das aktuelle Etikett als Bild bzw. PDF.
- **Backup:** *Einstellungen → Datenbank sichern* speichert alles (inkl. Drucker und Passwort), *Wiederherstellen* spielt es zurück.

## 8. Drucker und Sicherheit
- **USB-Drucker** werden automatisch erkannt. Mehrere gleiche Modelle werden über den USB-Port unterschieden.
- **Netzwerkdrucker** (LAN/WLAN): *Einstellungen → Netzwerkdrucker hinzufügen* (Name, IP, Modell).
- **Passwortschutz:** *Einstellungen → Passwortschutz*. Ohne Schutz kann jeder im Netzwerk drucken – nur in vertrauenswürdigen Netzen betreiben.

## 9. Eingabe-Modus, QR-Assistent
- **Eingabe-Modus:** Auf jeder Vorlage gibt es den Button **Eingabe**. Er zeigt nur ein kleines Formular mit einem Feld für jeden eigenen Platzhalter (z. B. `{Name}`, `{Raum}`), eine Vorschau und die Kopienzahl – ohne den Designer. Ideal für Kolleginnen und Kollegen, die nur drucken sollen.
- **QR-Assistent:** Beim QR-Code in den Eigenschaften auf *QR-Assistent…* klicken. Typen: Link, WLAN-Zugang, Kontakt (vCard), E-Mail, Telefon, SMS, Standort, Freitext. Du füllst nur die Felder aus, der Inhalt wird richtig aufgebaut. Platzhalter sind auch hier erlaubt.

## 9a. Tastenkürzel
| Taste | Aktion |
|---|---|
| `Entf` | Ausgewähltes Element löschen |
| `Strg+Z` | Rückgängig |
| `Strg+Y` oder `Strg+Shift+Z` | Wiederholen |
| `Enter` / `Tab` / `Esc` | In der Tabellenzelle: übernehmen / nächste Zelle / abbrechen |

## 10. Häufige Probleme
| Problem | Lösung |
|---|---|
| Etikett wird abgeschnitten oder falsch positioniert | Rolle im Programm gleich der eingelegten Rolle? „gedreht“ prüfen. |
| Barcode wird nicht gedruckt | Eingabe prüfen (z. B. EAN-13 braucht 12 Ziffern). |
| Text sieht auf dem Papier anders aus | Dithering aus; Schrift nicht zu klein (unter ca. 6 pt). |
| Seite nicht erreichbar | Pi und Gerät im gleichen Netz? Alternativ per IP statt `labelpi.local`. |
| Weitere Hilfe | `docs/INSTALL.md` (Installation, Fehlerbehebung) |

## 11. Sprachen
Die Oberfläche gibt es in Deutsch und Englisch. Oben rechts in der Leiste wählst du die Sprache; sie wird pro Gerät gemerkt (beim ersten Start gilt die Browsersprache).

**Neue Sprache hinzufügen**
1. *Einstellungen → Sprachen → Vorlage für neue Sprache herunterladen* (`neue-sprache.json`).
2. Datei öffnen: links steht der deutsche Text (nicht ändern), rechts trägst du die Übersetzung ein. `{}` sind Platzhalter für Zahlen/Namen und müssen in gleicher Anzahl und Reihenfolge erhalten bleiben. Leere Einträge werden auf Deutsch angezeigt.
3. Ganz oben `"_name"` auf den Namen der Sprache setzen, z. B. `"Français"`.
4. Datei als **Sprachcode.json** speichern, z. B. `fr.json`.
5. *Sprachdatei hinzufügen (.json)* – oder die Datei in den Ordner `lang/` auf dem Pi legen. Eigene Dateien überstehen Updates und haben Vorrang vor eingebauten.

**Anleitung übersetzen (optional):** Diese Anleitung als `ANLEITUNG.fr.md` im Ordner `lang/` (oder `docs/`) ablegen – sie erscheint dann unter *Hilfe*, wenn die Sprache aktiv ist. Ohne Übersetzung wird die deutsche Anleitung gezeigt.

Platzhalter wie `{datum}` behalten ihre Namen; für Englisch gibt es Kurzformen (`{date}` …). Datum, Wochentag und Monatsnamen erscheinen in der gewählten Sprache. Möchtest du deine Übersetzung teilen, freut sich das Projekt über einen Pull Request.

## 12. Update
- **Hinweis:** Gibt es eine neuere Version, erscheint oben ein blauer Balken *„Update verfügbar“* (mit ✕ zum Ausblenden).
- **Aktualisieren:** *Einstellungen → Update → Jetzt aktualisieren*. LabelPi lädt die neue Version von GitHub, ersetzt die Programmdateien und startet sich neu (ca. 1–2 Minuten, die Seite lädt danach von selbst neu).
- Vorlagen, Verlauf, Zähler, Passwort und eigene Sprachen bleiben erhalten. Die vorherige Version wird gesichert; *Vorherige Version wiederherstellen* macht das Update rückgängig.
- Ändert sich `install.sh` (neue Systempakete), erscheint ein Hinweis: dann einmal `bash install.sh` auf dem Pi ausführen.
- Aus Sicherheitsgründen sollte bei Nutzung im Netzwerk der **Passwortschutz** aktiv sein – ohne Schutz kann jeder im Netzwerk ein Update anstoßen.
