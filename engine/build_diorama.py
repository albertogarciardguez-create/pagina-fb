#!/usr/bin/env python3
"""Reels "diorama" de Impulso Real: imágenes fijas estilo stop-motion (plastilina + papel) animadas sin gastar créditos.

  python3 engine/build_diorama.py diorama/<historia>.json --preview   # solo hoja de revisión (salida/<id>/revision.png)
  python3 engine/build_diorama.py diorama/<historia>.json             # MP4 1080x1920 30 fps + post.txt

Imágenes: diorama/img/<id>/<nombre>.(jpg|jpeg|png|webp), con los nombres de "img" de cada escena (p01a, p02...).
Voz: diorama/audio/<id>.mp3 (la toma de ElevenLabs). Se alinea sola con engine/alinear.py.
Si falta el audio, usa la voz gratuita kokoro solo para probar (imprime AVISO).
"""
import base64, hashlib, io, json, os, subprocess, sys
import numpy as np, soundfile as sf

ENGINE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ENGINE)
sys.path.insert(0, ENGINE)
from build_largo import lp, SR, _tts, srt  # noqa: E402

FPS = 30
EXT = (".jpg", ".jpeg", ".png", ".webp")


def log(*a):
    print("[diorama]", *a, flush=True)


# ---------- voz y tiempos ----------
def voz(story, path, out):
    mp3 = os.path.join(ROOT, story.get("audio", f"diorama/audio/{story['id']}.mp3"))
    base = mp3[:-4]
    partes = [f"{base}_{k}.mp3" for k in range(1, 30) if os.path.exists(f"{base}_{k}.mp3")]
    if not os.path.exists(mp3) and partes:  # voz larga entregada en varias partes: _1.mp3, _2.mp3...
        gap = story.get("pausaPartes", 0.6)  # silencio entre partes (p. ej. cambios de voz en un diálogo)
        ins = sum([["-i", x] for x in partes], [])
        fil = "".join(f"[{k}:a]aresample=44100,aformat=channel_layouts=mono,apad=pad_dur={gap}[a{k}];" for k in range(len(partes)))
        fil += "".join(f"[a{k}]" for k in range(len(partes))) + f"concat=n={len(partes)}:v=0:a=1[o]"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fil, "-map", "[o]", "-c:a", "libmp3lame", "-q:a", "2", mp3], check=True)
        log(f"voz: uní {len(partes)} partes en {os.path.relpath(mp3, ROOT)}")
    if os.path.exists(mp3):
        log("voz: alineando", os.path.relpath(mp3, ROOT))
        subprocess.run([sys.executable, os.path.join(ENGINE, "alinear.py"), mp3, path], check=True, cwd=ROOT)
        return os.path.join(out, "voz_raw.wav"), json.load(open(os.path.join(out, "timing.json"), encoding="utf-8"))
    import voces
    st = dict(story, scenes=[dict(s, type="plano") for s in story["scenes"]])
    motor, _ = voces.cargar_config(story)
    log(f"voz: sin MP3 en {os.path.relpath(mp3, ROOT)}; genero con el motor '{motor}'")
    try:
        return _tts(st, out, voces.crear(st))
    except voces.MotorNoDisponible as e:
        log(f"AVISO: el motor '{motor}' falló ({e}); uso kokoro.")
        return _tts(st, out, voces.crear(st, "kokoro"), aviso=str(e))


def eventos(story, timing):
    ts = timing["scenes"]
    cuts = [0.0] + [round(max(0.0, s["sents"][0]["start"] - 0.12), 3) for s in ts[1:]]
    ev = []
    for sc, st in zip(story["scenes"], ts):
        def at(s=0, f=0.0, st=st):
            se = st["sents"][min(s, len(st["sents"]) - 1)]
            return round(se["start"] + f * (se["end"] - se["start"]) - 0.05, 3)
        e = {"titles": [at(tt.get("s", 0), tt.get("at", 0)) for tt in sc.get("titles", [])],
             "sfx": [round(at(x.get("s", 0), x.get("at", 0)) + x.get("d", 0), 3) for x in sc.get("sfx", [])]}
        if sc.get("dial"):
            e["dial"] = at(sc["dial"].get("s", 0), sc["dial"].get("at", 0))
        ev.append(e)
    timing["cuts"], timing["ev"] = cuts, ev
    return timing


# ---------- audio: música por actos + efectos, todo generado ----------
def _tono(f, x, ph, arm):
    return sum(a * np.sin(2 * np.pi * f * (h + 1) * x + ph) for h, a in enumerate(arm))


def capa(N, acordes, seg, rng, arm, vib=0.0):
    out = np.zeros(N)
    for c in range(int(np.ceil(N / SR / seg)) + 1):
        a = int(c * seg * SR)
        if a >= N:
            break
        b = min(N, int((c + 1) * seg * SR + 1.5 * SR)); n = b - a; x = np.arange(n) / SR
        env = np.minimum(1, x / 1.2) * np.minimum(1, np.maximum(0, (n / SR - x) / 1.5))
        xx = x + (vib * np.sin(2 * np.pi * 5 * x) if vib else 0)
        s = np.zeros(n)
        for f in acordes[c % len(acordes)]:
            for det in (-0.5, 0.6):
                s += _tono(f + det, xx, rng.uniform(0, 6.28), arm) * (0.25 if f < 100 else 0.15)
        out[a:b] += s * env
    return lp(out, 0.05)


def bombo(n_s=0.4, f0=40, f1=55):
    x = np.arange(int(n_s * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(f0 + f1 * np.exp(-x / 0.035)) / SR) * np.exp(-x / 0.14)


def _archivo_sonido(k):
    """Sonido descargado (Pixabay, Freesound CC0, etc.) en diorama/sonidos/<k>.wav|mp3: reemplaza al generado."""
    for ext in (".wav", ".mp3", ".ogg", ".flac"):
        p = os.path.join(ROOT, "diorama", "sonidos", k + ext)
        if os.path.exists(p):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-ac", "1", "-ar", str(SR), "/tmp/_sfx.wav"], check=True)
            a, _ = sf.read("/tmp/_sfx.wav")
            return a / max(1e-6, np.abs(a).max()) * 0.8
    return None


def sfx_sig(k, rng):
    a = _archivo_sonido(k)
    if a is not None:
        return a

    def xs(sec):
        return np.arange(int(sec * SR)) / SR
    if k == "tick":
        x = xs(.06); return np.sin(2 * np.pi * 2100 * x) * np.exp(-x / 0.008) * 0.35
    if k == "papel":
        x = xs(.35); z = rng.standard_normal(len(x)); z = z - lp(z, 0.3)
        return z * np.exp(-x / 0.1) * np.minimum(1, x / 0.01) * (0.4 + 0.6 * (rng.random(len(x)) < 0.25)) * 0.22
    if k == "whoosh":
        x = xs(.9); return lp(rng.standard_normal(len(x)), 0.08) * np.sin(np.pi * x / 0.9) ** 2 * 0.4
    if k == "sello":
        x = xs(.5); return (np.sin(2 * np.pi * 60 * x) * np.exp(-x / 0.08) + rng.standard_normal(len(x)) * np.exp(-x / 0.004) * 0.6) * 0.8
    if k == "piedra":
        x = xs(1.6); z = lp(rng.standard_normal(len(x)), 0.03)
        env = np.minimum(1, x / 0.2) * np.minimum(1, np.maximum(0, (1.6 - x) / 0.3))
        return (z * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * x)) * 5 + np.sin(2 * np.pi * 38 * x) * 0.5) * env * 0.5
    if k == "rugido":
        x = xs(1.8); z = lp(rng.standard_normal(len(x)), 0.02)
        tone = np.sin(2 * np.pi * np.cumsum(95 - 25 * x / 1.8) / SR)
        env = np.minimum(1, x / 0.25) * np.exp(-np.maximum(0, x - 0.5) / 0.5)
        return (z * 6 * (0.5 + 0.5 * np.sin(2 * np.pi * 28 * x)) + tone * 0.5) * env * 0.55
    if k == "campana":
        x = xs(3.5); return sum(np.sin(2 * np.pi * f * x) * np.exp(-x / 1.2) for f in (293.66, 369.99, 440.0, 587.33)) * np.minimum(1, x / 0.005) * 0.25
    if k == "olas":
        x = xs(3.0); return lp(rng.standard_normal(len(x)), 0.04) * np.sin(np.pi * x / 3.0) ** 2 * 1.6
    if k == "trueno":
        x = xs(3.0); z = rng.standard_normal(len(x))
        return (z * np.exp(-x / 0.05) * 0.5 + lp(z, 0.01) * 14 * np.exp(-x / 1.1) * np.minimum(1, x / 0.08)) * 0.6
    if k == "agua":
        x = xs(1.2); z = rng.standard_normal(len(x))
        return (lp(z, 0.25) * np.exp(-x / 0.12) + lp(z, 0.03) * 3 * np.exp(-x / 0.5)) * 0.6
    # "tambor": golpe grave de apertura
    x = xs(2.5); s = np.sin(2 * np.pi * np.cumsum(32 + 40 * np.exp(-x / 0.08)) / SR) * np.exp(-x / 0.9)
    return s * 0.9 + lp(rng.standard_normal(len(x)), 0.05) * np.exp(-x / 0.6) * 0.4


def mezcla(story, out, raw, timing):
    proc = os.path.join(out, "voz.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-ar", str(SR), "-af",
                    "highpass=f=80,equalizer=f=200:t=q:w=1:g=1.5,equalizer=f=3000:t=q:w=1.2:g=2.5,"
                    "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3,alimiter=limit=0.9", proc], check=True)
    v, _ = sf.read(proc)
    v = v if v.ndim == 1 else v.mean(1)
    N = len(v); t = np.arange(N) / SR
    seed = int(hashlib.md5(story["id"].encode()).hexdigest()[:8], 16); rng = np.random.default_rng(seed)
    cuts, total = timing["cuts"], len(v) / SR
    capas = {
        "menor": capa(N, [[73.42, 146.83, 174.61, 220.0], [58.27, 116.54, 146.83, 174.61],
                          [49.0, 98.0, 146.83, 196.0], [55.0, 110.0, 138.59, 164.81]], 4.0, rng, (1, .5, .25, .12)),
        "mayor": capa(N, [[73.42, 146.83, 185.0, 220.0, 293.66], [98.0, 146.83, 196.0, 246.94, 293.66],
                          [110.0, 138.59, 164.81, 220.0, 277.18], [73.42, 146.83, 185.0, 220.0, 293.66]], 3.0, rng,
                      (1, .45, .3, .2, .1), vib=0.0012),
    }
    dron = lp(np.sin(2 * np.pi * 36.71 * t) + .6 * np.sin(2 * np.pi * 55 * t) + .3 * np.sin(2 * np.pi * 73.42 * t), 0.05)
    lat = np.zeros(N); kb = bombo(); beat = 60 / 66
    for k in range(int(total / beat)):
        for off, gn in ((0, 1.0), (0.24, 0.65)):
            i0 = int((k * beat + off) * SR); i1 = min(N, i0 + len(kb))
            if i0 < N:
                lat[i0:i1] += kb[:i1 - i0] * gn
    capas["foso"] = dron / max(1e-6, np.abs(dron).max()) * 0.5 + lat / max(1e-6, np.abs(lat).max()) * 0.9
    gan = {k: np.zeros(N) for k in capas}
    mask = np.ones(N)
    for i, sc in enumerate(story["scenes"]):
        a = int(cuts[i] * SR); b = int((cuts[i + 1] if i + 1 < len(cuts) else total) * SR)
        m = sc.get("mus", "menor")
        if m in gan:
            gan[m][a:b] = sc.get("nivel", 1.0)
        if sc.get("corte"):  # silencio en seco al terminar la línea de esta escena
            c0 = int((timing["scenes"][i]["end"] + 0.03) * SR); r = int(0.012 * SR)
            mask[c0:b] = 0; mask[c0:c0 + r] = np.linspace(1, 0, min(r, max(0, b - c0)))[:len(mask[c0:c0 + r])]
    mus = sum(capas[k] / max(1e-6, np.abs(capas[k]).max()) * lp(gan[k], 1 / (0.35 * SR)) for k in capas)
    if story.get("musica_archivo"):  # pista libre de derechos descargada (Pixabay, YouTube Audio Library…), en bucle
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", os.path.join(ROOT, story["musica_archivo"]),
                        "-t", str(N / SR), "-ac", "1", "-ar", str(SR), "/tmp/_mus.wav"], check=True)
        m, _ = sf.read("/tmp/_mus.wav"); m = np.pad(m, (0, max(0, N - len(m))))[:N]
        mus = m / max(1e-6, np.abs(m).max()) * 1.6
    ir_n = int(2.5 * SR); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.7); ir = lp(ir, 0.3); ir /= np.abs(ir).sum() / 8
    from numpy.fft import rfft, irfft
    L = 1 << int(np.ceil(np.log2(N + ir_n)))
    mus = mus * 0.6 + irfft(rfft(mus, L) * rfft(ir, L), L)[:N] * 0.4
    mus = mus / max(1e-6, np.abs(mus).max()) * mask
    w = int(.08 * SR); ve = np.convolve(np.abs(v), np.ones(w) / w, mode="same")
    mus = mus * 0.2 * lp(np.where(ve > 0.015, 0.55, 1.0), 0.00025)
    f = int(2.0 * SR); mus[-f:] *= np.linspace(1, 0, f)
    sfx = np.zeros(N)

    def add(k, at, gain=1.0):
        s = sfx_sig(k, rng); i = int(at * SR)
        if 0 <= i < N:
            j = min(N, i + len(s)); sfx[i:j] += s[:j - i] * gain
    for i, (sc, e) in enumerate(zip(story["scenes"], timing["ev"])):
        if sc.get("tipo") == "cierre":
            add("whoosh", cuts[i] + 0.25); add("campana", cuts[i] + 1.3, 0.8)
        elif sc.get("tipo") == "capitulo":
            add("whoosh", cuts[i] - 0.3)
        elif i > 0:
            add("papel", cuts[i] - 0.05, 0.8)
        if sc.get("ambiente") == "olas":
            fin = cuts[i + 1] if i + 1 < len(cuts) else total
            for at in np.arange(cuts[i], fin - 1.0, 2.4):
                add("olas", at, 0.45)
        for x, at in zip(sc.get("sfx", []), e["sfx"]):
            add(x["k"], at, x.get("g", 1.0))
        d = sc.get("dial")
        if d and d.get("tipo") == "dias":
            for j in range(d.get("n", 30)):
                add("tick", e["dial"] + 0.2 + j * d.get("dur", 2.0) / d.get("n", 30), 0.5)
        elif d:
            fin = cuts[i + 1] if i + 1 < len(cuts) else total
            for at in np.arange(e["dial"], fin - 0.3, 0.5):
                add("tick", at, 0.45)
    out_a = v * 0.95 + mus + sfx * 0.32
    out_a = out_a / max(1e-6, np.abs(out_a).max()) * 0.95
    path = os.path.join(out, "mezcla.wav"); sf.write(path, out_a, SR)
    return path


# ---------- imágenes y render ----------
def rellenar(im, f):
    """Cubre una franja lisa de arriba (fracción f de la altura) con la escena reflejada y desenfocada."""
    from PIL import Image, ImageFilter
    w, h = im.size; b = int(h * f)
    if b < 4:
        return im
    rad = max(8, w / 40)
    fill = im.crop((0, b, w, min(h, 2 * b))).transpose(Image.FLIP_TOP_BOTTOM).resize((w, b)).filter(ImageFilter.GaussianBlur(rad))
    out = im.copy(); out.paste(fill, (0, 0))
    s = max(6, int(h * 0.04)); blur = out.filter(ImageFilter.GaussianBlur(rad))
    col = np.clip((b + s - np.arange(h)) / (2 * s), 0, 1)
    mask = Image.fromarray((np.repeat(col[:, None], w, 1) * 255).astype(np.uint8))
    return Image.composite(blur, out, mask)


def data_url(path, max_lado=2400, franja=0.0):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if franja:
        im = rellenar(im, franja)
    if max(im.size) > max_lado:
        r = max_lado / max(im.size); im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def imagenes(story):
    carpeta = os.path.join(ROOT, story.get("imagenes", f"diorama/img/{story['id']}"))
    out, faltan = {}, []
    fr = dict(story.get("franjas", {}))
    if os.path.exists(os.path.join(carpeta, "franjas.json")):  # franjas lisas que dejó el generador de imágenes
        fr.update(json.load(open(os.path.join(carpeta, "franjas.json"))))
    for sc in story["scenes"]:
        for n in sc.get("img", []):
            p = next((os.path.join(carpeta, n + e) for e in EXT if os.path.exists(os.path.join(carpeta, n + e))), None)
            if p:
                out[n] = data_url(p, franja=fr.get(n, 0.0))
            else:
                faltan.append(n)
    if faltan:
        log(f"AVISO: faltan imágenes en {os.path.relpath(carpeta, ROOT)}: {', '.join(faltan)} (salen como marcador café)")
    return out


def clips(story, out):
    """Clips de video (p. ej. Gemini/Veo) en la carpeta de imágenes: <clip>.mp4 → cuadros a 12 fps (look stop-motion)."""
    carpeta = os.path.join(ROOT, story.get("imagenes", f"diorama/img/{story['id']}"))
    res = {}
    for sc in story["scenes"]:
        c = sc.get("clip")
        if not c or c in res:
            continue
        src = next((os.path.join(carpeta, c + e) for e in (".mp4", ".mov", ".webm") if os.path.exists(os.path.join(carpeta, c + e))), None)
        if not src:
            continue
        d = os.path.join(out, "clips", c); os.makedirs(d, exist_ok=True)
        lado = "1920:-2" if story.get("formato") == "horizontal" else "-2:1920"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"fps=12,scale={lado}", "-frames:v", "120", "-q:v", "3", f"{d}/f%03d.jpg"], check=True)
        res[c] = [f"file://{d}/{f}" for f in sorted(os.listdir(d)) if f.endswith(".jpg")]
        log(f"clip {c}: {len(res[c])} cuadros")
    return res


def abrir(pw, story, timing, imgs, cl=None):
    br = pw.chromium.launch(args=["--disable-gpu", "--allow-file-access-from-files"])
    hz = story.get("formato") == "horizontal"
    pg = br.new_page(viewport={"width": 1920 if hz else 1080, "height": 1080 if hz else 1920})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    logo = data_url(os.path.join(ENGINE, "assets", "impulso_logo.png"))
    pg.add_init_script(f"window.STORY={json.dumps(story, ensure_ascii=False)};window.TIMING={json.dumps(timing)};"
                       f"window.IMGS={json.dumps(imgs)};window.LOGO={json.dumps(logo)};window.CLIPS={json.dumps(cl or {})};")
    pg.goto(f"file://{ENGINE}/diorama.html")
    try:
        pg.wait_for_function("window.READY===true", timeout=60000)
    except Exception:
        pass
    if errors or not pg.evaluate("window.READY===true"):
        sys.exit("Error en la plantilla: " + "; ".join(errors))
    return br, pg


def cuadro(pg, t):
    return base64.b64decode(pg.evaluate("t=>window.frame(t)", t))


def revision(pg, story, timing, out):
    from PIL import Image, ImageDraw
    cuts, ev, total = timing["cuts"], timing["ev"], timing["total"]
    hz = story.get("formato") == "horizontal"
    tw, th, cols = (384, 216, 4) if hz else (270, 480, 5)
    n = len(story["scenes"]); rows = (n + cols - 1) // cols
    hoja = Image.new("RGB", (cols * tw + (cols + 1) * 8, rows * (th + 30) + 8), (24, 24, 24))
    d = ImageDraw.Draw(hoja)
    for i, sc in enumerate(story["scenes"]):
        fin = cuts[i + 1] if i + 1 < len(cuts) else total
        t = total - 0.4 if sc.get("tipo") == "cierre" else min(fin - 0.35, max([cuts[i] + 0.8] + [x + 0.7 for x in ev[i]["titles"]] + ([ev[i]["dial"] + 2.3] if "dial" in ev[i] else [])))
        im = Image.open(io.BytesIO(cuadro(pg, t))).resize((tw, th))
        dd = ImageDraw.Draw(im)  # zona segura: 250 px abajo y 150 px a la derecha (botones de TikTok/Reels)
        if not hz:
            dd.line([(0, th * 1670 / 1920), (tw, th * 1670 / 1920)], fill=(255, 60, 60), width=1)
            dd.line([(tw * 930 / 1080, 0), (tw * 930 / 1080, th)], fill=(255, 60, 60), width=1)
        x, y = 8 + (i % cols) * (tw + 8), 8 + (i // cols) * (th + 30)
        hoja.paste(im, (x, y)); d.text((x + 4, y + th + 6), f"{i + 1}  {t:.1f}s  {', '.join(sc.get('img', []))}", fill=(230, 230, 230))
    p = os.path.join(out, "revision.png"); hoja.save(p)
    log("hoja de revisión:", os.path.relpath(p, ROOT))


def youtube(story, timing, out):
    """Subtítulos .srt, youtube.txt con capítulos y miniatura.jpg (video largo)."""
    srt(timing, os.path.join(out, "subtitulos.srt"), story.get("cc"))
    yt = story["youtube"]
    mmss = lambda x: f"{int(x // 60)}:{int(x % 60):02d}"
    caps = ["0:00 " + yt.get("intro", "Introducción")]
    caps += [f"{mmss(timing['cuts'][i])} {sc['cap_titulo'].replace(chr(10), ' ')}" for i, sc in enumerate(story["scenes"]) if sc.get("tipo") == "capitulo"]
    txt = [yt["titulo"], "", yt["descripcion"], "", "Capítulos:", *caps, "", " ".join(yt.get("hashtags", [])), "", "Etiquetas: " + ", ".join(yt.get("etiquetas", []))]
    open(os.path.join(out, "youtube.txt"), "w", encoding="utf-8").write("\n".join(txt) + "\n")
    log("youtube.txt y subtitulos.srt listos")


def miniatura(pg, story, timing, out):
    m = story.get("miniatura")
    if m is None:
        return
    from PIL import Image
    t = max([timing["cuts"][m] + 0.9] + [x + 0.9 for x in timing["ev"][m]["titles"]])
    Image.open(io.BytesIO(cuadro(pg, t))).convert("RGB").resize((1280, 720)).save(os.path.join(out, "miniatura.jpg"), quality=92)


def main():
    path = os.path.abspath(sys.argv[1]); preview = "--preview" in sys.argv
    story = json.load(open(path, encoding="utf-8"))
    out = os.path.join(ROOT, "salida", story["id"]); os.makedirs(out, exist_ok=True)
    raw, timing = voz(story, path, out)
    timing = eventos(story, timing)
    json.dump(timing, open(os.path.join(out, "timing.json"), "w"), indent=1, ensure_ascii=False)
    log(f"duración: {timing['total']:.1f} s · {len(story['scenes'])} escenas")
    imgs = imagenes(story)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br, pg = abrir(pw, story, timing, imgs, clips(story, out))
        revision(pg, story, timing, out)
        if story.get("formato") == "horizontal":
            miniatura(pg, story, timing, out)
        if preview:
            br.close(); return
        audio = mezcla(story, out, raw, timing)
        mp4 = os.path.join(out, f"{story['id']}.mp4")
        nf = int(timing["total"] * FPS)
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                               "-i", audio, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4], stdin=subprocess.PIPE)
        for f in range(nf):
            ff.stdin.write(cuadro(pg, f / FPS))
            if f % 300 == 0:
                log(f"  cuadro {f}/{nf}")
        ff.stdin.close(); ff.wait(); br.close()
    if story.get("youtube"):
        youtube(story, timing, out)
    post = story.get("post", "") + "\n\n" + " ".join(story.get("hashtags", []))
    open(os.path.join(out, "post.txt"), "w", encoding="utf-8").write(post.strip() + "\n")
    if timing.get("aviso_voz"):
        log("AVISO: el video salió con la voz de prueba (kokoro), no con la de ElevenLabs.")
    log("listo:", os.path.relpath(mp4, ROOT))


if __name__ == "__main__":
    main()
