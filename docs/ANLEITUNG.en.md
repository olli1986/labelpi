# LabelPi – User guide

## 1. Basics
**Top bar:** printer (only shown if several are connected) · roll · length (continuous rolls only) · *rotated* · copies · dithering · auto-cut (models with a cutter only) · cut mark · **Print**.

- **The roll selected here must match the roll that is loaded.** LabelPi asks if you change the roll compared with the last print.
- **rotated:** On continuous rolls the length is shown horizontally and the label is rotated by 90° when printing, so you read it like on screen.
- **Dithering:** Only useful for photos/greys. Keep it **off** for text, QR codes and barcodes.
- **Cut mark** (continuous rolls without a cutter): prints a dashed line at the end of the label so you cut in the right place by hand (e.g. QL-500).

**Working in the designer**
- **View:** By default only the most important functions are shown. **Advanced view** (bar at the top right) adds rotate, dithering, auto-cut, cut mark, series, grid and zoom. More elements (PDF, shapes, symbols) are in the **＋ More …** menu, saving/export under **File ▾**.
- Add elements from the toolbar, **tap** = select, **drag** = move, **bottom-right corner** = resize.
- The **properties** are in the bar at the bottom, which always stays visible. It also has buttons to align the element to the label.
- Elements **snap** to the edge, centre and other elements while moving (pink guide lines).
- **↶ / ↷** undo and redo (last 25 steps).

## 2. Elements
| Element | Notes |
|---|---|
| **Text** | Multi-line. *Auto size* fills the box with the largest possible font (set the box height). |
| **Symbol** | Warning, hazard, recycling signs etc. – they are text in a symbol font, so freely scalable. |
| **QR code** | Any text or link; placeholders allowed. The *QR assistant* builds Wi-Fi, vCard, email … for you. |
| **Barcode** | Choose a type (see below). With invalid content a red warning appears and **nothing is printed**. |
| **Image** | Photo/logo from your device. Switch dithering on for photos. |
| **PDF** | The page size selects the matching roll. Multi-page PDFs can be printed as a series (one page per label). |
| **Shapes** | Circle, line, arrow, triangle – filled or outline, rotatable in 45° steps (properties → Rotation). |
| **Table** | See section 3. |

**Barcode types**

| Type | Input |
|---|---|
| Code 128 | Any characters |
| EAN-13 | 12 digits (check digit is added) |
| EAN-8 | 7 digits |
| Code 39 | Capital letters, digits, `- . $ / + %` and space |
| GS1-128 | With brackets, e.g. `(01)09501101530003(17)271231(10)AB12` |
| Data Matrix | Any text, square |

## 3. Tables
- **Tap a cell** = select it (blue). **Double-click or double-tap** = type directly into the cell. *Enter* accepts, *Tab* jumps to the next cell, *Esc* cancels.
- In the properties: add/remove rows and columns, font, line width, *first row bold*.
- **Table border:** all lines · outside only · row lines · none.
- **Border of a single cell:** select the cell and tick *top / bottom / left / right*. This is in addition to the table border – with “none (cell borders only)” just the marked cells get lines (e.g. a single underline).
- Texts that are too long shrink automatically to fit the cell.
- You can also edit the content as text: one line per table row, columns separated by `;`.

## 4. Placeholders
Placeholders work in **text, QR codes, barcodes and table cells**. The names are German; English short forms exist.

| Placeholder | Meaning | Example |
|---|---|---|
| `{n}` | Counter within the series | 1, 2, 3 … |
| `{n:5}` | Counter, 5 digits with leading zeros | 00001 |
| `{gesamt}` / `{total}` | Number of labels in the series | `{n}/{gesamt}` → 3/10 |
| `{lfd}`, `{lfd:5}` | **Running counter that remembers** (stored on the Pi, survives restarts and device changes) | 1001, 1002 … |
| `{lfd.invoice}` | Named counter, as many as you like | independent of `{lfd}` |
| `{datum}` / `{date}` | Today's date | 24.10.2026 |
| `{datum:JJJJ-MM-TT}` | Date with a custom format (`JJJJ`/`YYYY`, `JJ`/`YY`, `MM`, `TT`/`DD`) | 2026-10-24 |
| `{datum+30}` | Date plus 30 days (also `-7`; units `d` days, `w` weeks, `m` months, `j`/`y` years) | 23.11.2026 · `{datum+6m:MM/JJJJ}` → 04/2027 |
| `{zeit}`, `{zeit:HH:MM:SS}` | Time | 14:35 |
| `{jahr}` `{monat}` `{tag}` | Single date parts (also with offset, e.g. `{jahr+1j}`) | 2026 · 10 · 24 |
| `{kw}` / `{cw}` | ISO calendar week (e.g. `{kw+2w}` = week in two weeks) | 43 |
| `{wochentag}` `{monatname}` | Name in the interface language | Saturday |
| `{zufall:8}` / `{random:8}` | Random code (8 characters, without easily confused ones like 0/O and 1/I); every label of a series gets a different one | K7HT3QWZ |
| `{uuid}` | Random UUID | 3f2a9c1e-… |
| `{ColumnName}` | Value from the CSV column (CSV series only) | `{Name}` |

**English short forms:** `{date}` `{time}` `{year}` `{month}` `{day}` `{weekday}` `{cw}` `{random}` `{total}` `{seq}`.

**Filters** (append with `|`, combinable): `{Name|gross}` UPPERCASE · `{Name|klein}` lowercase · `{Name|titel}` Title Case (English: `|upper` `|lower` `|title`) · `{n:8|luhn}` appends a Luhn check digit · `{n:12|gtin}` appends the EAN/GTIN check digit.

**Notes**
- Date and time come from the device you print from. Unknown placeholders are left unchanged.
- `{lfd}` reserves the numbers when printing. If printing fails the counter is reset (no gaps). You see the next value in the preview and under *Settings → Counter*, where you can also change it.
- Examples: `SN-{jahr}-{lfd:4}` → `SN-2026-0001` · `Best before {datum+30}` · `CW {kw}/{jahr}` · `{n:11|gtin}` as EAN content.

## 5. Series (“Series…”)
- **Counter:** set start, step and count. Example: start 100, step 5, count 10 → 100, 105, …, 145.
- **CSV file:** first row = column names, then one label per row. Separator `;` or `,`, UTF-8.
  ```
  Name;Item;Number
  Miller;Screw M4;1001
  Smith;Nut M4;1002
  ```
  Use `{Name}`, `{Item}`, `{Number}` in the designer.
- **PDF pages:** created when you import a multi-page PDF.
- **Copies** apply per label of the series. Printing happens in blocks; the history only shows the first label of the series.
- The preview first shows label 1; use **‹ ›** next to “Series…” to page through all labels.

## 6. Grid (“Grid…”)
Continuous rolls only. Several labels side by side and below each other on one strip:
1. Set the *label width* in mm (e.g. 28 mm on a 62 mm roll for two columns).
2. Set *columns × rows* and *gap*.
3. When printing, consecutive labels (copies or series) fill the grid. If the grid does not fit the roll an error appears.

## 7. Templates, history, export, backup
- **Templates:** save with “Save as template”, sort into **folders**, edit (name/folder) and export.
- **History:** every print and every “Save” ends up here. *Print again*, *Edit*, or use *Select* to delete/export several.
- **Export/import:** labels and templates as a JSON file, e.g. to share. **⬇ PNG/PDF** exports the current label as an image or PDF.
- **Backup:** *Settings → Save database* stores everything (including printers and password), *Restore backup* puts it back.

## 8. Printers and security
- **USB printers** are detected automatically. Several identical models are told apart by their USB port.
- **Network printers** (LAN/Wi-Fi): *Settings → Add network printer* (name, IP, model).
- **Password protection:** *Settings → Password protection*. Without it anyone on the network can print – use it only in trusted networks.

## 9. Form mode, QR assistant
- **Form mode:** every template has an **Form** button. It shows only a small form with one field per custom placeholder (e.g. `{Name}`, `{Room}`), a preview and the number of copies – no designer. Ideal for colleagues who only need to print.
- **QR assistant:** select the QR code and click *QR assistant…* in the properties. Types: link, Wi-Fi access, contact (vCard), email, phone, SMS, location, free text. You fill in the fields and the content is built correctly. Placeholders are allowed here too.

## 9a. Keyboard shortcuts
| Key | Action |
|---|---|
| `Del` | Delete the selected element |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` or `Ctrl+Shift+Z` | Redo |
| `Enter` / `Tab` / `Esc` | In a table cell: accept / next cell / cancel |

## 10. Common problems
| Problem | Solution |
|---|---|
| Label cut off or misplaced | Is the roll in the app the same as the loaded one? Check “rotated”. |
| Barcode is not printed | Check the input (e.g. EAN-13 needs 12 digits). |
| Text looks different on paper | Dithering off; font not too small (below about 6 pt). |
| Page not reachable | Pi and device on the same network? Use the IP instead of `labelpi.local`. |
| More help | `docs/INSTALL.md` (installation, troubleshooting) |

## 11. Languages
The interface is available in German and English. Choose the language in the bar at the top right; it is remembered per device (the browser language is used on first start).

**Adding a new language**
1. *Settings → Languages → Download template for a new language* (`neue-sprache.json`).
2. Open the file: the German text on the left must not be changed, enter your translation on the right. `{}` are placeholders for numbers/names and must stay in the same number and order. Empty entries are shown in German.
3. Set `"_name"` at the top to the name of the language, e.g. `"Français"`.
4. Save the file as **languagecode.json**, e.g. `fr.json`.
5. *Add language file (.json)* – or put the file into the `lang/` folder on the Pi. Custom files survive updates and take precedence over built-in ones.

**Translating this guide (optional):** put it into the `lang/` folder (or `docs/`) as `ANLEITUNG.fr.md` – it is then shown under *Help* when that language is active. Without a translation the German guide is shown.

Placeholders such as `{datum}` keep their names; English short forms exist (`{date}` …). Dates, weekdays and month names appear in the selected language. If you would like to share your translation, the project welcomes a pull request.

## 12. Update
- **Notice:** If a newer version exists, a blue bar *“Update available”* appears at the top (✕ dismisses it).
- **Updating:** *Settings → Update → Update now*. LabelPi downloads the new version from GitHub, replaces the program files and restarts (about 1–2 minutes; the page reloads by itself).
- Templates, history, counters, password and custom languages are kept. The previous version is backed up; *Restore previous version* undoes the update.
- If `install.sh` changes (new system packages) a note appears: run `bash install.sh` once on the Pi.
- For security, **password protection** should be on when used in a network – without it anyone on the network can trigger an update.
