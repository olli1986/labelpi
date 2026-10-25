"""LabelPi – Etikettendruck für Brother-QL-Drucker per Weboberfläche (MIT-Lizenz)."""
import base64, glob, io, json, os, re, shutil, socket, sqlite3, subprocess, sys, tarfile, tempfile, threading, time, urllib.error, urllib.parse, urllib.request
from flask import Flask, Response, jsonify, request, send_file, send_from_directory
from PIL import Image
import barcode
import markdown
from ppf.datamatrix import DataMatrix
import qrcode
from werkzeug.security import check_password_hash, generate_password_hash
from brother_ql.conversion import convert
from brother_ql.raster import BrotherQLRaster
from brother_ql.backends.helpers import send, discover
from brother_ql.labels import ALL_LABELS
from brother_ql.models import ALL_MODELS

BASE = os.path.dirname(os.path.abspath(__file__))
VERSION = open(os.path.join(BASE, "VERSION")).read().strip() if os.path.isfile(os.path.join(BASE, "VERSION")) else "0.7.0"
DB = os.path.join(BASE, "labels.db")
app = Flask(__name__, static_folder="static")
lock = threading.Lock()
MODELS = {m.identifier: m for m in ALL_MODELS}
PIDS = {0x2015: "QL-500", 0x2016: "QL-550", 0x2027: "QL-560", 0x2028: "QL-570", 0x2029: "QL-580N", 0x201b: "QL-650TD",
        0x2042: "QL-700", 0x2043: "QL-710W", 0x2044: "QL-720NW", 0x209b: "QL-800", 0x209c: "QL-810W", 0x209d: "QL-820NWB",
        0x2020: "QL-1050", 0x202a: "QL-1060N"}  # USB-Produkt-ID -> Modell
# DK-Nummern (Größen kommen aus der brother_ql-Bibliothek); leer = unbekannt
DK = {"12": "DK-22214", "29": "DK-22210", "38": "DK-22225", "50": "DK-22223", "54": "DK-N55224", "62": "DK-22205",
      "102": "DK-22243", "17x54": "DK-11204", "17x87": "DK-11203", "23x23": "DK-11221", "29x90": "DK-11201",
      "39x90": "DK-11208", "39x48": "DK-11220", "62x29": "DK-11209", "62x100": "DK-11202", "102x51": "DK-11240",
      "102x152": "DK-11241", "d12": "DK-11219", "d24": "DK-11218", "d58": "DK-11207"}
LABELS = []
for l in ALL_LABELS:
    if l.identifier == "62red": continue  # Rot/Schwarz: Designer ist nur Schwarz/Weiß
    ff, w = l.form_factor.name, l.tape_size
    name = f"{w[0]} mm Endlos" if ff == "ENDLESS" else f"Ø {w[0]} mm rund" if ff == "ROUND_DIE_CUT" else f"{w[0]}×{w[1]} mm"
    LABELS.append(dict(id=l.identifier, name=name, dk=DK.get(l.identifier, ""), endless=ff == "ENDLESS",
                       tw=w[0], tl=w[1], across=l.dots_printable[0], along=l.dots_printable[1], only=list(l.restricted_to_models)))

LBL = {l["id"]: l for l in LABELS}

def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

with db() as c:
    c.executescript("""
CREATE TABLE IF NOT EXISTS templates(id INTEGER PRIMARY KEY, name TEXT, label TEXT, design TEXT, png BLOB, ts TEXT DEFAULT (datetime('now','localtime')));
CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, ts TEXT DEFAULT (datetime('now','localtime')), label TEXT, copies INT, rotate INT, dither INT, design TEXT, png BLOB);
CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS counters(name TEXT PRIMARY KEY, v INTEGER);""")

def migrate():
    with db() as c:
        try: c.execute("ALTER TABLE templates ADD COLUMN folder TEXT DEFAULT ''")
        except sqlite3.OperationalError: pass

migrate()

def sget(k, d=None):
    with db() as c: r = c.execute("SELECT v FROM settings WHERE k=?", (k,)).fetchone()
    v = json.loads(r["v"]) if r else None
    return d if v is None else v

def sput(k, v):
    with db() as c: c.execute("INSERT OR REPLACE INTO settings(k,v) VALUES(?,?)", (k, json.dumps(v)))

def b64(s): return base64.b64decode(s.split(",", 1)[1])
def pngd(b): return "data:image/png;base64," + base64.b64encode(b).decode()

def gray(png):
    b = io.BytesIO(); Image.open(io.BytesIO(png)).convert("L").save(b, "PNG", optimize=True); return b.getvalue()

# ---------- Login (optional) ----------
OK = set()

@app.before_request
def guard():
    a = sget("auth")
    if not a: return
    h = request.headers.get("Authorization", "")
    if h in OK: return
    r = request.authorization
    if r and r.username == a["user"] and check_password_hash(a["hash"], r.password or ""):
        OK.add(h); return
    return Response("Login erforderlich", 401, {"WWW-Authenticate": 'Basic realm="LabelPi"'})

@app.get("/api/auth")
def a_get():
    a = sget("auth"); return jsonify(enabled=bool(a), user=(a or {}).get("user", ""))

@app.post("/api/auth")
def a_set():
    j = request.get_json() or {}; old = sget("auth")
    if not j.get("enabled"): sput("auth", None)
    else:
        user, pw = (j.get("user") or "").strip(), j.get("password") or ""
        if not user or (not pw and not old): return jsonify(error="Benutzername und Passwort angeben"), 400
        sput("auth", {"user": user, "hash": generate_password_hash(pw, method="pbkdf2:sha256:60000") if pw else old["hash"]})
    OK.clear(); return jsonify(ok=True)

# ---------- Drucker ----------
def reachable(h):
    try: socket.create_connection((h, 9100), 0.7).close(); return True
    except OSError: return False

def printers():
    out = []
    try:
        for d in discover("pyusb"):
            dev = d["instance"]; pid = dev.idProduct
            if pid in PIDS:  # gleiche Modelle werden über den USB-Port unterschieden
                port = f"{dev.bus}-" + ".".join(map(str, dev.port_numbers or ()))
                out.append(dict(id=f"usb:{pid:04x}:{port}", name=PIDS[pid] + " (USB)", model=PIDS[pid], host="", port=port,
                                uri=f"usb://0x04f9:0x{pid:04x}", backend="pyusb", online=True, dev=dev))
    except Exception: pass
    for p in out:
        if sum(q["model"] == p["model"] for q in out) > 1: p["name"] = f'{p["model"]} (USB-Port {p["port"]})'
    for p in sget("printers", []):
        out.append(dict(id="net:" + p["host"], name=f'{p["name"]} (Netzwerk)', model=p["model"], host=p["host"], uri=f'tcp://{p["host"]}:9100', backend="network", online=reachable(p["host"])))
    for p in out: p["cutting"] = MODELS[p["model"]].cutting
    return out

def pick(pid):
    ps = printers()
    p = next((x for x in ps if x["id"] == pid), None) or next((x for x in ps if x["online"]), None)
    if not p: raise RuntimeError("Kein Drucker gefunden (USB, Strom, Netzwerk prüfen)")
    return p

def compose(tiles, label, rot, grid):
    """Mehrere Etiketten (Kacheln) als Raster auf eine Endlosrolle legen."""
    W = LBL[label]["across"]; cols, rows = int(grid["cols"]), int(grid["rows"]); gap = round(float(grid.get("gap", 2)) * 300 / 25.4)
    out = []
    for i in range(0, len(tiles), cols * rows):
        grp = [t.rotate(-90, expand=True) if rot else t for t in tiles[i:i + cols * rows]]
        tw, th = grp[0].size; used = -(-len(grp) // cols)
        if cols * tw + (cols - 1) * gap > W: raise ValueError("Das Raster ist breiter als die Rolle (Etikettenbreite/Spalten prüfen)")
        x0 = (W - (cols * tw + (cols - 1) * gap)) // 2
        im = Image.new("RGB", (W, used * th + (used - 1) * gap), "white")
        for k, t in enumerate(grp): im.paste(t, (x0 + (k % cols) * (tw + gap), (k // cols) * (th + gap)))
        out.append(im)
    return out

def do_print(pngs, label, rot, dither, pid, cut, grid=None):
    tiles = [Image.open(io.BytesIO(b)).convert("RGB") for b in pngs]
    if grid and LBL[label]["endless"] and int(grid["cols"]) * int(grid["rows"]) > 1: imgs = compose(tiles, label, rot, grid)
    else: imgs = [t.rotate(-90, expand=True) if rot else t for t in tiles]  # 90° im Uhrzeigersinn
    with lock:
        for i in range(0, len(imgs), 20):  # in Blöcken, schont den Speicher des Pi
            p = pick(pid)
            ins = convert(qlr=BrotherQLRaster(p["model"]), images=imgs[i:i + 20], label=label, rotate="0", threshold=70.0,
                          dither=dither, compress=False, red=False, dpi_600=False, hq=True, cut=bool(cut) and p["cutting"])
            send(instructions=ins, printer_identifier=p.get("dev") or p["uri"], backend_identifier=p["backend"], blocking=True)

@app.errorhandler(Exception)
def err(e): return jsonify(error=str(e)), getattr(e, "code", 500)

@app.get("/")
def index(): return send_from_directory("static", "index.html")

@app.get("/api/models")
def models(): return jsonify(list(MODELS))

@app.get("/api/printers")
def p_list(): return jsonify([{k: v for k, v in p.items() if k != "dev"} for p in printers()])

@app.post("/api/printers")
def p_add():
    j = request.get_json() or {}; host = (j.get("host") or "").strip()
    if not host or j.get("model") not in MODELS: return jsonify(error="Name, Adresse und Modell angeben"), 400
    sput("printers", [p for p in sget("printers", []) if p["host"] != host] + [dict(name=(j.get("name") or host).strip(), host=host, model=j["model"])])
    return jsonify(ok=True)

@app.post("/api/printers/delete")
def p_del():
    h = (request.get_json() or {}).get("host"); sput("printers", [p for p in sget("printers", []) if p["host"] != h]); return jsonify(ok=True)

@app.get("/api/labels")
def labels():
    p = next((x for x in printers() if x["id"] == request.args.get("printer")), None)
    model = p["model"] if p else "QL-500"
    return jsonify([l for l in LABELS if not l["only"] or model in l["only"]])

@app.get("/api/bc")
def bc():
    t, d = request.args.get("t", "code128"), request.args.get("d", "")
    if not d or t not in ("code128", "ean13", "ean8", "code39", "gs1_128", "dm"): return jsonify(error="ungültig"), 400
    try:
        if t == "dm": return jsonify(m=["".join(map(str, r)) for r in DataMatrix(d).matrix])
        cls = barcode.get_barcode_class(t)
        return jsonify(m=(cls(d, add_checksum=False) if t == "code39" else cls(d)).build()[0])
    except Exception as e: return jsonify(error=str(e)), 400

@app.post("/api/pdfin")
def pdfin():
    f, page = request.files["f"], max(1, int(request.form.get("page", 1)))
    try:
        with tempfile.TemporaryDirectory() as t:
            src = os.path.join(t, "in.pdf"); f.save(src)
            mt = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", src], capture_output=True, text=True).stdout)
            pages = int(mt.group(1)) if mt else 1; page = min(page, pages)
            def enc(fp, mx):
                im = Image.open(fp).convert("L"); mm = (im.width / 300 * 25.4, im.height / 300 * 25.4)
                im.thumbnail((mx, mx)); b = io.BytesIO(); im.save(b, "PNG", optimize=True); return pngd(b.getvalue()), mm
            if request.form.get("all") == "1":  # alle Seiten (max. 60) -> Serie
                subprocess.run(["pdftoppm", "-r", "300", "-png", "-l", "60", src, os.path.join(t, "o")], check=True, timeout=600)
                res = [enc(fp, 2400) for fp in sorted(glob.glob(os.path.join(t, "o-*.png")))]
                return jsonify(pngs=[r[0] for r in res], w=res[0][1][0], h=res[0][1][1], pages=len(res))
            subprocess.run(["pdftoppm", "-r", "300", "-png", "-f", str(page), "-l", str(page), "-singlefile", src, os.path.join(t, "o")], check=True, timeout=120)
            png, (w, h) = enc(os.path.join(t, "o.png"), 4000)
    except FileNotFoundError: return jsonify(error="poppler-utils fehlt: sudo apt install poppler-utils"), 500
    return jsonify(png=png, w=w, h=h, pages=pages)

@app.get("/qr")
def qr():
    q = qrcode.QRCode(border=0, box_size=8, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(request.args.get("d", "")); q.make(fit=True)
    b = io.BytesIO(); q.make_image(fill_color="black", back_color="white").save(b); b.seek(0)
    return send_file(b, mimetype="image/png")

@app.post("/api/pdf")
def pdf():
    b = io.BytesIO(); Image.open(io.BytesIO(b64(request.get_json()["png"]))).convert("RGB").save(b, "PDF", resolution=300.0); b.seek(0)
    return send_file(b, mimetype="application/pdf")

def log(j, n):
    with db() as c:
        c.execute("INSERT INTO history(label,copies,rotate,dither,design,png) VALUES(?,?,?,?,?,?)",
                  (j["label"], n, int(bool(j.get("rotate"))), int(bool(j.get("dither"))), json.dumps(j["design"]), gray(b64(j["png"]))))
        c.execute("DELETE FROM history WHERE id NOT IN (SELECT id FROM history ORDER BY id DESC LIMIT 1000)")

@app.post("/api/print")
def print_():
    j = request.get_json(); n = max(1, min(50, int(j.get("copies", 1))))
    pngs = [b64(x) for x in j["pngs"]]
    do_print([b for b in pngs for _ in range(n)][:600], j["label"], bool(j.get("rotate")), bool(j.get("dither")), j.get("printer"), j.get("cut"), j.get("grid"))
    if j.get("log", True): j["png"] = j["pngs"][0]; log(j, n * len(pngs))
    return jsonify(ok=True)

@app.post("/api/save")
def save():
    log(request.get_json(), 0); return jsonify(ok=True)

# ---------- Verlauf ----------
@app.get("/api/history")
def h_list():
    with db() as c: return jsonify([dict(r) for r in c.execute("SELECT id,ts,label,copies FROM history ORDER BY id DESC LIMIT 200")])

@app.get("/api/history/<int:i>")
def h_get(i):
    with db() as c: return jsonify(design=c.execute("SELECT design FROM history WHERE id=?", (i,)).fetchone()["design"])

@app.get("/api/history/<int:i>.png")
def h_png(i):
    with db() as c: return send_file(io.BytesIO(c.execute("SELECT png FROM history WHERE id=?", (i,)).fetchone()["png"]), mimetype="image/png")

@app.post("/api/history/<int:i>/reprint")
def h_reprint(i):
    j = request.get_json(silent=True) or {}
    with db() as c: r = c.execute("SELECT * FROM history WHERE id=?", (i,)).fetchone()
    n = max(1, min(50, int(j.get("copies", 1))))
    do_print([r["png"]] * n, r["label"], bool(r["rotate"]), bool(r["dither"]), j.get("printer"), j.get("cut"))
    with db() as c: c.execute("UPDATE history SET ts=datetime('now','localtime'), copies=? WHERE id=?", (n, i))
    return jsonify(ok=True)

@app.post("/api/history/delete")
def h_del_many():
    ids = [int(x) for x in (request.get_json() or {}).get("ids", [])]
    with db() as c: c.executemany("DELETE FROM history WHERE id=?", [(i,) for i in ids])
    return jsonify(ok=True, n=len(ids))

@app.delete("/api/history/<int:i>")
def h_del(i):
    with db() as c: c.execute("DELETE FROM history WHERE id=?", (i,))
    return jsonify(ok=True)

# ---------- Vorlagen ----------
@app.get("/api/templates")
def t_list():
    with db() as c: return jsonify([dict(r) for r in c.execute("SELECT id,name,label,COALESCE(folder,'') AS folder FROM templates ORDER BY name COLLATE NOCASE")])

@app.post("/api/templates")
def t_add():
    j = request.get_json()
    with db() as c:
        c.execute("INSERT INTO templates(name,label,design,png,folder) VALUES(?,?,?,?,?)", (j["name"], j["label"], json.dumps(j["design"]), gray(b64(j["png"])), (j.get("folder") or "").strip()))
    return jsonify(ok=True)

@app.put("/api/templates/<int:i>")
def t_put(i):
    j = request.get_json()
    with db() as c: c.execute("UPDATE templates SET name=?, folder=? WHERE id=?", (j["name"].strip(), (j.get("folder") or "").strip(), i))
    return jsonify(ok=True)

@app.get("/api/templates/<int:i>")
def t_get(i):
    with db() as c: return jsonify(design=c.execute("SELECT design FROM templates WHERE id=?", (i,)).fetchone()["design"])

@app.get("/api/templates/<int:i>.png")
def t_png(i):
    with db() as c: return send_file(io.BytesIO(c.execute("SELECT png FROM templates WHERE id=?", (i,)).fetchone()["png"]), mimetype="image/png")

@app.delete("/api/templates/<int:i>")
def t_del(i):
    with db() as c: c.execute("DELETE FROM templates WHERE id=?", (i,))
    return jsonify(ok=True)

# ---------- Export / Import (JSON) ----------
@app.get("/api/export")
def export():
    tpl = request.args.get("kind") == "templates"
    ids = [int(x) for x in request.args.get("ids", "").split(",") if x.strip().isdigit()]
    q = f"SELECT * FROM {'templates' if tpl else 'history'}" + (f" WHERE id IN ({','.join('?' * len(ids))})" if ids else "")
    with db() as c: rows = c.execute(q, ids).fetchall()
    items = [dict(kind="template" if tpl else "label", name=r["name"] if tpl else "", folder=(r["folder"] or "") if tpl else "",
                  label=r["label"], design=json.loads(r["design"]), png=pngd(r["png"])) for r in rows]
    return Response(json.dumps(dict(labelpi=1, items=items)), mimetype="application/json",
                    headers={"Content-Disposition": f"attachment; filename=labelpi-{'vorlagen' if tpl else 'etiketten'}.json"})

@app.post("/api/import")
def imp():
    n = 0
    with db() as c:
        for i in (request.get_json() or {}).get("items", []):
            png, d = gray(b64(i["png"])), json.dumps(i["design"])
            if i.get("kind") == "template":
                c.execute("INSERT INTO templates(name,label,design,png,folder) VALUES(?,?,?,?,?)", (i.get("name") or "Import", i["label"], d, png, i.get("folder", "")))
            else:
                c.execute("INSERT INTO history(label,copies,rotate,dither,design,png) VALUES(?,?,?,?,?,?)", (i["label"], 0, int(bool(i["design"].get("rot"))), 0, d, png))
            n += 1
    return jsonify(ok=True, n=n)

# ---------- Einstellungen / System ----------
@app.get("/api/settings")
def s_get(): return jsonify(sget("ui", {}))

@app.post("/api/settings")
def s_set():
    j = request.get_json() or {}; d = sget("ui", {})
    d.update({k: j[k] for k in ("label", "len", "rot", "dither", "printer", "cut", "roll", "cw", "grid", "cmk") if k in j}); sput("ui", d); return jsonify(ok=True)

# ---------- Zähler (merken die nächste Nummer dauerhaft) ----------
@app.get("/api/counters")
def c_list():
    with db() as c: return jsonify({r["name"]: r["v"] for r in c.execute("SELECT name,v FROM counters")})

@app.post("/api/counters/reserve")
def c_reserve():
    out = {}
    with db() as c:
        for k, n in ((request.get_json() or {}).get("names") or {}).items():
            k = k.lower()[:40]; r = c.execute("SELECT v FROM counters WHERE name=?", (k,)).fetchone(); v = r["v"] if r else 1
            c.execute("INSERT OR REPLACE INTO counters(name,v) VALUES(?,?)", (k, v + max(1, int(n)))); out[k] = v
    return jsonify(out)

@app.post("/api/counters/set")
def c_set():
    j = request.get_json() or {}
    with db() as c: c.execute("INSERT OR REPLACE INTO counters(name,v) VALUES(?,?)", ((j.get("name") or "default").lower()[:40], int(j.get("value", 1))))
    return jsonify(ok=True)

@app.post("/api/counters/delete")
def c_del():
    with db() as c: c.execute("DELETE FROM counters WHERE name=?", ((request.get_json() or {}).get("name", "").lower(),))
    return jsonify(ok=True)

# ---------- Sprachen: eingebaut (static/lang) und eigene (lang/) ----------
LANGD = [os.path.join(BASE, "static", "lang"), os.path.join(BASE, "lang")]
CODE = re.compile(r"[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})?")

def lang_file(code):
    if CODE.fullmatch(code or ""):
        for d in reversed(LANGD):  # eigene Dateien haben Vorrang
            p = os.path.join(d, code + ".json")
            if os.path.isfile(p): return p

@app.get("/api/langs")
def langs():
    out = {"de": "Deutsch"}
    for d in LANGD:
        for p in sorted(glob.glob(os.path.join(d, "*.json"))):
            try: out[os.path.basename(p)[:-5]] = json.load(open(p, encoding="utf-8")).get("_name", os.path.basename(p)[:-5])
            except Exception: pass
    return jsonify([dict(code=k, name=v, custom=os.path.isfile(os.path.join(LANGD[1], k + ".json"))) for k, v in out.items()])

@app.get("/api/lang/<code>")
def lang(code):
    p = lang_file(code)
    return Response(open(p, encoding="utf-8").read(), mimetype="application/json") if p else jsonify(strings={})

@app.post("/api/lang")
def lang_up():
    f = request.files["f"]; code = os.path.basename(f.filename or "")[:-5]
    try: data = json.loads(f.read().decode("utf-8-sig"))
    except Exception: data = None
    if not CODE.fullmatch(code) or not isinstance(data, dict) or not data.get("_name") or not isinstance(data.get("strings"), dict):
        return jsonify(error="Ungültige Sprachdatei (Dateiname = Sprachcode, Inhalt mit _name und strings)"), 400
    os.makedirs(LANGD[1], exist_ok=True)
    json.dump(data, open(os.path.join(LANGD[1], code + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return jsonify(ok=True)

@app.post("/api/lang/delete")
def lang_del():
    code = (request.get_json() or {}).get("code", "")
    if CODE.fullmatch(code) and os.path.isfile(os.path.join(LANGD[1], code + ".json")): os.unlink(os.path.join(LANGD[1], code + ".json"))
    return jsonify(ok=True)

@app.get("/api/langtemplate")
def lang_tpl():
    keys = json.load(open(os.path.join(LANGD[0], "en.json"), encoding="utf-8"))["strings"]
    return Response(json.dumps({"_name": "Name der Sprache", "strings": {k: "" for k in keys}}, ensure_ascii=False, indent=1),
                    mimetype="application/json", headers={"Content-Disposition": "attachment; filename=neue-sprache.json"})

@app.get("/api/help")
def help_():
    lg = request.args.get("lang", "de")
    if not CODE.fullmatch(lg): lg = "de"
    for p in (os.path.join(LANGD[1], f"ANLEITUNG.{lg}.md"), os.path.join(BASE, "docs", f"ANLEITUNG.{lg}.md"), os.path.join(BASE, "docs", "ANLEITUNG.md")):
        if os.path.isfile(p):
            return Response(markdown.markdown(open(p, encoding="utf-8").read(), extensions=["tables", "fenced_code"]), mimetype="text/html")
    return Response("", mimetype="text/html")

# ---------- Update über die Weboberfläche (GitHub-Releases oder main) ----------
REPO = os.environ.get("LABELPI_REPO_SLUG", "olli1986/labelpi")
BK = os.path.join(BASE, ".update-backup")
PROTECT = {".venv", ".git", "labels.db", "lang", ".update-backup", "__pycache__"}  # bleiben beim Update unberührt
UPD = {"state": "idle", "log": []}; _chk = {"t": 0, "v": None}
RESTART = lambda: os._exit(0)  # systemd (Restart=always) startet LabelPi danach neu

def _get(url, timeout=10):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "LabelPi/" + VERSION}), timeout=timeout)

def _ver(s):
    n = [int(x) for x in re.findall(r"\d+", s or "")[:3]]; return tuple(n + [0] * (3 - len(n)))

def is_git(): return os.path.isdir(os.path.join(BASE, ".git")) and bool(shutil.which("git"))

def update_info(force=False):
    if not force and _chk["v"] and time.time() - _chk["t"] < 6 * 3600: return _chk["v"]
    info = dict(current=VERSION, latest=VERSION, available=False, tag="", notes="", source="", repo=REPO, backup=os.path.isdir(BK), method="git" if is_git() else "archive")
    try:
        # Release-Tag ohne API (keine Rate-Limits, z. B. hinter Mobilfunk-NAT): /releases/latest leitet auf /releases/tag/<tag> um
        m = re.search(r"/releases/tag/([^/?#]+)", _get(f"https://github.com/{REPO}/releases/latest").geturl())
        if m:
            tag = urllib.parse.unquote(m.group(1)); info.update(latest=tag.lstrip("vV"), tag=tag, source="release")
            try:  # Release-Beschreibung (optional, die API kann begrenzt sein)
                req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases/tags/{m.group(1)}", headers={"User-Agent": "LabelPi/" + VERSION, "Accept": "application/vnd.github+json"})
                info["notes"] = (json.load(urllib.request.urlopen(req, timeout=5)).get("body") or "")[:1500]
            except Exception: pass
        else:  # kein Release vorhanden: VERSION-Datei auf main
            try: v = _get(f"https://raw.githubusercontent.com/{REPO}/main/VERSION").read().decode().strip()
            except urllib.error.HTTPError:
                v = re.search(r'VERSION\s*=\s*"([^"]+)"', _get(f"https://raw.githubusercontent.com/{REPO}/main/app.py").read().decode()).group(1)
            info.update(latest=v, source="main")
        info["available"] = _ver(info["latest"]) > _ver(VERSION)
        _chk.update(t=time.time(), v=info)
    except Exception as e: info["error"] = str(e)[:200]
    return info

def _copy_in(src, skip=PROTECT):
    for n in os.listdir(src):
        if n in skip: continue
        a, b = os.path.join(src, n), os.path.join(BASE, n)
        if os.path.isdir(a): shutil.copytree(a, b, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
        else: shutil.copy2(a, b)

def _restore():
    if os.path.isdir(BK): _copy_in(BK, {"__pycache__"})

def pip_install():
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-r", os.path.join(BASE, "requirements.txt"), "--disable-pip-version-check"], capture_output=True, text=True, timeout=1800)
    if r.returncode: raise RuntimeError((r.stderr or r.stdout)[-300:])

def _read(p, mode="r"):
    try:
        with open(p, mode) as f: return f.read()
    except OSError: return None

def do_update():
    log = UPD["log"]
    try:
        info = update_info(True)
        if info.get("error") or not info["available"]: raise RuntimeError(info.get("error") or "Keine neuere Version verfügbar")
        req, inst = os.path.join(BASE, "requirements.txt"), os.path.join(BASE, "install.sh")
        old_req, old_inst = _read(req), _read(inst, "rb")
        log.append("Sichere aktuelle Version …")
        shutil.rmtree(BK, ignore_errors=True); os.makedirs(BK)
        for n in os.listdir(BASE):
            if n not in PROTECT:
                a = os.path.join(BASE, n)
                if os.path.isdir(a): shutil.copytree(a, os.path.join(BK, n), ignore=shutil.ignore_patterns("__pycache__"))
                else: shutil.copy2(a, BK)
        log.append(f"Lade Version {info['latest']} herunter …")
        if is_git():
            log.append("Hole Änderungen per git …")
            for cmd in (["fetch", "--tags", "--force", "origin"], ["reset", "--hard", info["tag"] or "origin/main"]):
                r = subprocess.run(["git", "-C", BASE] + cmd, capture_output=True, text=True, timeout=300)
                if r.returncode: raise RuntimeError(r.stderr[-300:])
        else:
            with tempfile.TemporaryDirectory() as t:
                url = f"https://codeload.github.com/{REPO}/tar.gz/refs/" + (f"tags/{info['tag']}" if info["tag"] else "heads/main")
                tgz = os.path.join(t, "src.tgz")
                with open(tgz, "wb") as f: f.write(_get(url, 120).read())
                log.append("Entpacke …")
                with tarfile.open(tgz) as tf:
                    for m in tf.getmembers():
                        if not (m.isfile() or m.isdir()) or os.path.normpath(m.name).startswith(("/", "..")): continue
                        try: tf.extract(m, t, filter="data")
                        except TypeError: tf.extract(m, t)
                root = next((os.path.join(t, d) for d in os.listdir(t) if os.path.isfile(os.path.join(t, d, "app.py"))), None)
                if not root or not os.path.isfile(os.path.join(root, "static", "index.html")): raise RuntimeError("Die heruntergeladene Datei enthält kein LabelPi")
                log.append("Kopiere neue Dateien …"); _copy_in(root)
        if _read(req) != old_req:
            log.append("Installiere Python-Pakete (kann einige Minuten dauern) …")
            try: pip_install()
            except Exception as e: _restore(); raise RuntimeError("Installation der Python-Pakete fehlgeschlagen, vorherige Version wiederhergestellt: " + str(e))
        if _read(inst, "rb") != old_inst: log.append("Hinweis: install.sh hat sich geändert – bitte danach einmal „bash install.sh“ ausführen (Systempakete).")
        log.append("Fertig – LabelPi startet neu …"); UPD["state"] = "done"; threading.Timer(2, RESTART).start()
    except Exception as e:
        log.append(f"Fehler: {e}"); UPD["state"] = "error"

@app.get("/api/update/check")
def u_check(): return jsonify(update_info(request.args.get("force") == "1"))

@app.post("/api/update/apply")
def u_apply():
    if UPD["state"] == "running": return jsonify(error="Update läuft bereits"), 409
    UPD.update(state="running", log=[]); threading.Thread(target=do_update, daemon=True).start(); return jsonify(ok=True)

@app.get("/api/update/status")
def u_status(): return jsonify(state=UPD["state"], log=UPD["log"], version=VERSION)

@app.post("/api/update/rollback")
def u_rollback():
    if not os.path.isdir(BK): return jsonify(error="Keine Sicherung vorhanden"), 404
    _restore(); UPD.update(state="done", log=["Vorherige Version wiederhergestellt – LabelPi startet neu …"]); threading.Timer(2, RESTART).start(); return jsonify(ok=True)

@app.get("/api/backup")
def backup():
    t = tempfile.NamedTemporaryFile(suffix=".db", delete=False); t.close()
    src, dst = sqlite3.connect(DB), sqlite3.connect(t.name); src.backup(dst); dst.close(); src.close()
    r = send_file(t.name, as_attachment=True, download_name=time.strftime("labelpi-backup-%Y%m%d-%H%M.db"))
    r.call_on_close(lambda: os.unlink(t.name)); return r

@app.post("/api/restore")
def restore():
    t = tempfile.NamedTemporaryFile(suffix=".db", delete=False); request.files["f"].save(t.name); t.close()
    try:
        s = sqlite3.connect(t.name); names = {r[0] for r in s.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"templates", "history", "settings"} <= names: raise ValueError("Keine gültige LabelPi-Sicherung")
        d = sqlite3.connect(DB); s.backup(d); d.close(); s.close()
    finally: os.unlink(t.name)
    migrate(); OK.clear(); return jsonify(ok=True)

@app.post("/api/power")
def power():
    a = (request.get_json() or {}).get("action")
    if a not in ("reboot", "poweroff"): return jsonify(error="Ungültige Aktion"), 400
    cmd = ["sudo", "-n", "/usr/bin/systemctl", a]
    if subprocess.run(cmd[:2] + ["-l"] + cmd[2:], capture_output=True).returncode != 0:
        return jsonify(error="Keine sudo-Berechtigung (install.sh erneut ausführen)"), 500
    subprocess.Popen("sleep 1; " + " ".join(cmd), shell=True)
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run("0.0.0.0", int(os.environ.get("PORT", 80)), threaded=True)
