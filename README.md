# LabelPi

Webbasierter Etiketten-Designer und Druckserver für **Brother-QL-Drucker** – gedacht für den Raspberry Pi (läuft aber auf jedem Linux-Rechner). Bedienung per Browser vom PC, iPad oder iPhone, auf dem Client ist kein Treiber nötig.

*English: web-based label designer and print server for Brother QL label printers, made for the Raspberry Pi. No client drivers required.*

## Funktionen
- **Designer:** Text (viele Schriftarten, lokal mitgeliefert), QR-Codes, Bilder, Rechtecke/Linien, **Tabellen** mit wählbarem Rahmen
- **Alle QL-Modelle der Bibliothek [brother_ql](https://github.com/pklaus/brother_ql)** (QL-500 bis QL-1060N) mit den jeweils passenden DK-Rollen (Endlos, Stanz, rund); **Autoschnitt** wählbar, wenn das Modell ihn kann
- Mehrere Drucker: ein USB-Drucker wird automatisch Standard, bei mehreren erscheint eine Auswahl; **Netzwerkdrucker** (LAN/WLAN, Port 9100) in den Einstellungen hinzufügbar
- **Barcodes** (Code 128, EAN-13/8, Code 39), **Seriennummern** (Zähler, `{n:5}`, `{datum}`) und **Serienetiketten aus CSV**
- **Formen** (Kreis, Linie, Pfeil, Dreieck) und **Symbole** (Warn-, Recycling-, Gefahrenzeichen u. v. m.), **Auto-Textgröße**, GS1-128 und **Datamatrix**
- **Raster** (mehrere Etiketten pro Streifen), **Rollen-Check** (Warnung bei Rollenwechsel), **Backup/Wiederherstellung** der Datenbank
- **Mehrsprachig** (Deutsch, Englisch; weitere Sprachen per Datei hinzufügbar), **Zähler, die sich merken**, Datum-Rechnen (`{datum+30}`), **Eingabe-Modus**, **QR-Assistent**, **Schnittmarken**
- **PDF-Import** (Seitengröße wählt die passende Rolle, mehrseitig als Serie), **Rückgängig/Wiederholen**, **Ausrichtungshilfen** (Einrasten, Mittig/Rand)
- **Vorlagen** mit Ordnern, **Verlauf** mit „Nochmal drucken“ und Mehrfachauswahl
- **Export/Import** einzelner oder aller Etiketten/Vorlagen (JSON), Download als **PNG/PDF**, Speichern ohne Drucken
- Einstellungen (Rolle, Länge, Drehung …) werden auf dem Server gemerkt, also auf allen Geräten gleich
- Optionaler **Passwortschutz** (in der Weboberfläche einstellbar), Neustart/Herunterfahren per Button

## Installation (Raspberry Pi OS Lite)
Bedienung, Platzhalter, Serien, Barcodes: [docs/ANLEITUNG.md](docs/ANLEITUNG.md) (Deutsch) · [docs/ANLEITUNG.en.md](docs/ANLEITUNG.en.md) (English) (in der App über den Button *? Hilfe*). Ausführliche Installationsanleitung inkl. SD-Karte, WLAN und Fehlerbehebung: [docs/INSTALL.md](docs/INSTALL.md)

**Ein Befehl** (installiert nach `~/labelpi`, richtet Dienst und USB-Rechte ein):
```
curl -fsSL https://raw.githubusercontent.com/olli1986/labelpi/main/install.sh | bash
```
**Oder manuell:** Ordner per `scp -r` auf den Pi kopieren, dann `cd labelpi && bash install.sh`.

Danach im Browser: `http://<hostname>.local` (z. B. `http://labelpi.local`).

**Update:** in der Weboberfläche unter *Einstellungen → Update* (ein Hinweis erscheint oben, sobald eine neue Version verfügbar ist). Alternativ per `cd ~/labelpi && git pull && sudo systemctl restart labelpi`. Für Maintainer: [docs/RELEASING.md](docs/RELEASING.md)

## Hinweise
- Rot/Schwarz-Rollen werden nicht unterstützt (der Designer ist Schwarz/Weiß).
- QL-700/710W/720NW: die Taste „Editor Lite“ (LED) muss aus sein.
- Netzwerkdrucker: nur Modelle mit LAN/WLAN (z. B. QL-580N, QL-710W, QL-720NW, QL-810W, QL-820NWB, QL-1060N); die Drucker-IP am besten reservieren/fest vergeben.
- Mehrere **gleiche** USB-Modelle werden über den USB-Port unterschieden – nach dem Umstecken in einen anderen Port die Auswahl neu prüfen.
- Word-Dateien werden nicht direkt importiert (als PDF speichern).
- Ohne Passwortschutz hat jeder im Netz Zugriff – nur in vertrauenswürdigen Netzen betreiben. HTTP-Basic-Auth sendet das Passwort unverschlüsselt; für Zugriff aus dem Internet einen HTTPS-Reverse-Proxy davorsetzen.
- Die DK-Nummern sind nach bestem Wissen ergänzt; maßgeblich sind die Rollenmaße.

## Entstehung
Dieses Projekt ist in Zusammenarbeit von Oliver Braasch und **Claude (Anthropic)** entstanden: Anforderungen, Tests und Ziel-Hardware stammen vom Autor, der Code wurde im Dialog mit Claude geschrieben und iterativ verbessert (KI-unterstützte Entwicklung).

## Lizenz
[MIT](LICENSE). Verwendet u. a. Flask, Pillow, qrcode, brother_ql (GPL-3.0, als separate Abhängigkeit installiert) und Schriften über [Fontsource](https://fontsource.org) (SIL OFL / Apache 2.0).
