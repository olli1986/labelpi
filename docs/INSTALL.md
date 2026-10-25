# LabelPi – Installationsanleitung (Raspberry Pi + Brother QL)

Kurzfassung und Funktionsübersicht: [README](../README.md). Beispiel hier: Raspberry Pi 2 B + QL-500.

## 0. Was du brauchst
- Raspberry Pi 2 B, Netzteil (5 V / 2 A), microSD (8 GB+)
- **USB-WLAN-Stick** (der Pi 2 B hat kein WLAN eingebaut; am besten ein 2,4-GHz-Stick, der unter Raspberry Pi OS ohne Zusatztreiber läuft, z. B. mit Realtek-/MediaTek-Chip)
- Brother QL-500 per USB, 62-mm-Rolle eingelegt

## 1. SD-Karte vorbereiten
1. **Raspberry Pi Imager** starten → Gerät: *Raspberry Pi 2* → OS: *Raspberry Pi OS (other) → Raspberry Pi OS Lite (32-bit)*.
2. Zahnrad / „Einstellungen bearbeiten“:
   - Hostname: `labelpi`
   - Benutzer + Passwort festlegen
   - WLAN: SSID und Passwort deines **Hotspots** (ggf. zusätzlich dein Heim-WLAN), Land `DE`
   - SSH aktivieren (Passwort oder Schlüssel)
   - Zeitzone `Europe/Berlin`
3. Schreiben, SD in den Pi, WLAN-Stick einstecken, Strom an. Erster Start dauert 1–2 Minuten.

> Hotspot-Tipp (iPhone): *Einstellungen → Persönlicher Hotspot → „Kompatibilität maximieren“* einschalten, damit er 2,4 GHz nutzt. Der Hotspot muss beim Einschalten des Pi bereits aktiv sein.

## 2. Per SSH verbinden
```
ssh DEIN_BENUTZER@labelpi.local
```
Klappt `.local` nicht, die IP in den Geräteinfos des Hotspots nachsehen.

## 3. Dateien auf den Pi bringen
**Variante A (ein Befehl, empfohlen):** direkt auf dem Pi
```
curl -fsSL https://raw.githubusercontent.com/DEIN-USER/labelpi/main/install.sh | bash
```
Damit sind Schritt 3 und 4 erledigt, weiter mit Schritt 5.

**Variante B (manuell):**
Vom PC aus (Ordner `labelpi` aus dem ZIP entpackt):
```
scp -r labelpi DEIN_BENUTZER@labelpi.local:~
```

## 4. Installieren
```
cd ~/labelpi
bash install.sh
```
Das Skript installiert Python-Pakete in einer venv, legt die USB-Rechte für Brother-Drucker an und richtet den Dienst `labelpi` ein (startet automatisch beim Booten, Port 80). Die Installation dauert auf dem Pi 2 einige Minuten.

## 5. Drucker prüfen
QL-500 einschalten, dann:
```
lsusb | grep 04f9      # sollte "Brother Industries" zeigen
sudo systemctl status labelpi
```
Falls der Drucker nicht erkannt wird: einmal aus- und wieder einschalten bzw. `sudo reboot`.

## 6. Benutzen
Im Browser (PC, iPad, iPhone, gleiches Netz/Hotspot): **http://labelpi.local**
- Grüner Punkt oben = Drucker gefunden.
- iPhone/iPad: Teilen → „Zum Home-Bildschirm“ für ein App-Symbol.
- Modelle mit Autoschnitt zeigen oben die Option „Autoschnitt“. Der QL-500 schneidet **nicht** automatisch: nach dem Druck Etikett am Cutter manuell abtrennen. Bei mehreren Kopien kommen die Etiketten hintereinander raus.
- Die Schrift wird auf dem jeweiligen Gerät gerendert (WYSIWYG: gedruckt wird, was du siehst). Auf iPad/PC können Schriftarten leicht abweichen.

Oben rechts gibt es Buttons zum **Neustarten** und **Herunterfahren** des Pi. Nach dem Herunterfahren erst Strom trennen, wenn die grüne LED nicht mehr blinkt.

## 7. Wartung
- Logs: `journalctl -u labelpi -f`
- Neustart: `sudo systemctl restart labelpi`
- **Backup:** Vorlagen und Verlauf liegen in `~/labelpi/labels.db` (einfach kopieren).
- Weiteres WLAN hinzufügen: `sudo nmcli device wifi connect "SSID" password "PASSWORT"`
- Update: neue Dateien drüberkopieren, dann `sudo systemctl restart labelpi`.

## 8. Fehlerbehebung
| Problem | Lösung |
|---|---|
| `ImportError: libopenjp2.so.7` (Dienst startet nicht) | `bash install.sh` erneut ausführen (installiert die fehlenden Bibliotheken), Prüfen mit `journalctl -u labelpi -n 30` |
| „Drucker nicht gefunden“ | Strom/USB prüfen, `lsusb`, Dienst neu starten |
| „Resource busy“ / „Access denied“ | `echo 'blacklist usblp' \| sudo tee /etc/modprobe.d/blacklist-usblp.conf`, dann `sudo reboot` |
| Fehler zur Rollen-/Etikettengröße | Im Designer dieselbe Rolle wählen wie im Drucker eingelegt (QL-500 erkennt sie nicht selbst) |
| WLAN-Stick verbindet nicht mit Hotspot | `nmcli device wifi list` (sieht der Stick das Netz?), WLAN-Land `DE` setzen (`sudo raspi-config`), Hotspot auf **2,4 GHz** und **WPA2** stellen (viele Sticks können kein 5 GHz/WPA3) |
| Seite nicht erreichbar | Hotspot aktiv? Gleiches Netz? Alternativ per IP statt `labelpi.local` |

## 9. Sicherheit
Optional: Passwortschutz unter *Einstellungen*. Ohne Passwort gibt es **keinen Login**. Nutze die Seite nur im eigenen Hotspot/Heimnetz mit starkem WLAN-Passwort, nicht im Firmen-WLAN.
