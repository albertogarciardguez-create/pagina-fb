#!/usr/bin/env python3
"""Motor ANIME ÉPICO — reels estilo "El día que…" (anime cinematográfico + diálogos doblados).

Formato (copiado de la referencia de TikTok):
  1080x1920 negro · título fijo de 2 líneas arriba · imagen 16:9 al centro · subtítulos en español abajo
  cortes secos cada ~2 s · diálogos cortos de personajes (no narrador) · música épica que crece
  · silencio antes del clímax · cámara lenta, flash blanco, temblor, líneas de velocidad · ovación final
  · cierre con la marca (Señor Fútbol o Impulso Real).

Uso:
  python3 engine/build_anime.py anime/<historia>.json            # video + portada + revision.jpg + post.txt
  VOZ_MOTOR=kokoro python3 engine/build_anime.py ...               # fuerza voz offline (en la nube)

Cada toma puede ser una imagen (.png/.jpg: se anima con movimiento de cámara) o un clip (.mp4 de
Kling/Seedance/Veo: se recorta y se le aplican los efectos). Ver anime/BIBLIA.md.
"""
import asyncio, hashlib, json, math, os, shutil, subprocess, sys
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "engine", "fonts")
CACHE = os.path.expanduser("~/.cache/senorfutbol/anime")
FPS, W, H, SR = 30, 1080, 1920, 44100

MARCAS = {
    "senorfutbol": {"acento": "#F5C518", "firma": "SEÑOR FÚTBOL", "lema": "Aquí el fútbol se debate",
                    "boton": "SÍGUENOS +", "logo": None},
    "impulso": {"acento": "#FF6A3D", "firma": "IMPULSO REAL", "lema": "Historias que te levantan",
                "boton": "SEGUIR +", "logo": "engine/assets/impulso_logo.png"},
}
KOKORO_DEF = ["em_alex", "em_santa", "ef_dora"]


def log(*a):
    print("[anime]", *a, flush=True)


def run(cmd):
    subprocess.run(cmd, check=True)


def ruta(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def fuente(nombre, tam):
    return ImageFont.truetype(os.path.join(FONTS, nombre), tam)


def h(obj):
    return hashlib.sha1(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:14]


# ───────────────────────── layout ─────────────────────────
def geometria(story):
    if story.get("formato") == "4:3":
        pw, ph = 1080, 810
    else:
        pw, ph = 1080, 608
    top = (H - ph) // 2 - (20 if ph == 608 else 0)
    return pw, ph, top


def texto_rico(draw, xy, linea, fnt, blanco, acento):
    """Escribe una línea donde *palabra* sale en color de acento."""
    x, y = xy
    for i, trozo in enumerate(linea.split("*")):
        if not trozo:
            continue
        draw.text((x, y), trozo, font=fnt, fill=acento if i % 2 else blanco)
        x += draw.textlength(trozo, font=fnt)


def envolver(draw, texto, fnt, ancho):
    out, cur = [], ""
    for w in texto.split():
        prueba = (cur + " " + w).strip()
        if draw.textlength(prueba.replace("*", ""), font=fnt) <= ancho:
            cur = prueba
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    # si un *resaltado* quedó partido entre líneas, ciérralo/ábrelo en cada línea
    fix, abierto = [], False
    for ln in out:
        if abierto:
            ln = "*" + ln
        abierto = ln.count("*") % 2 == 1
        fix.append(ln + ("*" if abierto else ""))
    return fix


def fondo_titulo(story, marca, out):
    pw, ph, top = geometria(story)
    im = Image.new("RGB", (W, H), "#000000")
    d = ImageDraw.Draw(im)
    tam = story.get("titulo_tam", 62)
    fnt = fuente("Montserrat-ExtraBold.ttf", tam)
    lineas = envolver(d, story["titulo"], fnt, W - 88)
    alto = len(lineas) * int(tam * 1.18)
    y = top - 34 - alto
    tag = fuente("Montserrat-SemiBold.ttf", 28)
    d.text((44, y - 52), " ".join(marca["firma"]), font=tag, fill=marca["acento"])
    for ln in lineas:
        texto_rico(d, (44, y), ln, fnt, "#FFFFFF", marca["acento"])
        y += int(tam * 1.18)
    im.save(out)


def tarjeta_cierre(story, marca, out):
    im = Image.new("RGB", (W, H), "#000000")
    d = ImageDraw.Draw(im)
    ac = marca["acento"]
    c = story.get("cierre", {})
    y = 560
    if marca["logo"]:
        lg = Image.open(ruta(marca["logo"])).convert("RGBA").resize((300, 300))
        arr = np.array(lg)  # quita el fondo cuadrado del logo para que flote sobre negro
        dist = np.abs(arr[:, :, :3].astype(int) - arr[4, 4, :3].astype(int)).sum(2)
        arr[:, :, 3] = np.clip((dist - 10) * 10, 0, 255).astype(np.uint8)
        lg = Image.fromarray(arr)
        im.paste(lg, ((W - 300) // 2, y - 40), lg)
        y += 300
    else:
        d.ellipse((W // 2 - 90, y, W // 2 + 90, y + 180), outline=ac, width=12)
        d.regular_polygon((W // 2, y + 90, 46), 5, fill=ac)
        y += 230
    f1 = fuente("Montserrat-ExtraBold.ttf", 92)
    d.text((W // 2, y + 40), marca["firma"], font=f1, fill="#FFFFFF", anchor="mm")
    f2 = fuente("Montserrat-SemiBold.ttf", 40)
    d.text((W // 2, y + 120), marca["lema"], font=f2, fill=ac, anchor="mm")
    y += 210
    if c.get("pregunta"):
        f3 = fuente("Montserrat-ExtraBold.ttf", 54)
        for ln in envolver(d, c["pregunta"], f3, W - 140):
            d.text((W // 2, y), ln.replace("*", ""), font=f3, fill="#FFFFFF", anchor="mm")
            y += 66
        y += 30
    bw, bh = 420, 104
    d.rounded_rectangle(((W - bw) // 2, y, (W + bw) // 2, y + bh), 52, fill=ac)
    d.text((W // 2, y + bh // 2), marca["boton"], font=fuente("Montserrat-ExtraBold.ttf", 46),
           fill="#000000", anchor="mm")
    im.save(out)


# ───────────────────────── capas de efectos ─────────────────────────
def lineas_velocidad(d, pw, ph, n=6):
    """Líneas radiales de manga (fondo transparente). Devuelve patrón para ffmpeg."""
    os.makedirs(d, exist_ok=True)
    rng = np.random.default_rng(7)
    cx, cy = pw / 2, ph / 2
    R = math.hypot(pw, ph)
    for k in range(n):
        im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        for _ in range(140):
            a = rng.uniform(0, 2 * math.pi)
            r0 = rng.uniform(0.34, 0.55) * R / 2
            w = rng.uniform(0.003, 0.012)
            pts = [(cx + math.cos(a) * r0, cy + math.sin(a) * r0),
                   (cx + math.cos(a - w) * R, cy + math.sin(a - w) * R),
                   (cx + math.cos(a + w) * R, cy + math.sin(a + w) * R)]
            dr.polygon(pts, fill=(255, 255, 255, int(rng.uniform(90, 200))))
        im.save(os.path.join(d, f"l{k}.png"))
    return os.path.join(d, "l%d.png")


def filtro_movimiento(mov, n, pw, ph):
    big_w, big_h = pw * 2, ph * 2
    zc = "1.10"
    cen_x, cen_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    p = f"(on/{max(n - 1, 1)})"
    tabla = {
        "in": (f"1.0+0.12*{p}", cen_x, cen_y),
        "out": (f"1.12-0.12*{p}", cen_x, cen_y),
        "left": (zc, f"(iw-iw/zoom)*(1-{p})", cen_y),
        "right": (zc, f"(iw-iw/zoom)*{p}", cen_y),
        "up": (zc, cen_x, f"(ih-ih/zoom)*(1-{p})"),
        "down": (zc, cen_x, f"(ih-ih/zoom)*{p}"),
        "golpe": (f"1.0+0.22*(1-exp(-on/5))", cen_x, cen_y),
        "none": ("1.04", cen_x, cen_y),
    }
    z, x, y = tabla.get(mov, tabla["in"])
    return (f"scale={big_w}:{big_h}:force_original_aspect_ratio=increase,crop={big_w}:{big_h},"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={pw}x{ph}:fps={FPS}")


def render_toma(story, i, t, pw, ph, tmp, lineas_pat):
    dur = float(t.get("dur", 2.2))
    n = max(2, round(dur * FPS))
    fx = set(t.get("fx", []))
    clave = h({"t": t, "pw": pw, "ph": ph, "v": 3})
    out = os.path.join(CACHE, "tomas", f"{clave}.mp4")
    if os.path.exists(out):
        return out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    src = t.get("src", "negro")
    if src != "negro" and not os.path.exists(ruta(src)):  # imagen aún no generada: tarjeta de aviso
        ph_img = os.path.join(tmp, f"falta_{i}.png")
        im = Image.new("RGB", (pw, ph), "#1b1f24")
        d = ImageDraw.Draw(im)
        d.text((40, 40), f"TOMA {i + 1:02d} · falta {os.path.basename(src)}", font=fuente("Montserrat-ExtraBold.ttf", 44), fill="#F5C518")
        y = 120
        for ln in envolver(d, t.get("prompt", "")[:300], fuente("Montserrat-Regular.ttf", 28), pw - 80):
            d.text((40, y), ln.replace("*", ""), font=fuente("Montserrat-Regular.ttf", 28), fill="#cfd6dd")
            y += 38
        im.save(ph_img)
        src = ph_img
        t = {**t, "fx": [x for x in t.get("fx", []) if x != "lento"]}
        out = os.path.join(tmp, f"falta_{i}.mp4")
    ins, pre = [], ""
    if src == "negro":
        ins = ["-f", "lavfi", "-i", f"color=black:s={pw}x{ph}:r={FPS}:d={dur}"]
        pre = "null"
    elif src.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        ins = ["-i", ruta(src)]  # una sola imagen: zoompan genera los n cuadros
        pre = filtro_movimiento(t.get("mov", "in"), n, pw, ph)
    else:
        lento = float(t.get("lento", 2.0 if "lento" in fx else 1.0))
        ins = ["-ss", str(t.get("desde", 0)), "-t", f"{dur / lento + 0.1:.3f}", "-i", ruta(src)]
        pre = (f"scale={pw}:{ph}:force_original_aspect_ratio=increase,crop={pw}:{ph},"
               f"setpts={lento}*PTS,fps={FPS}")
        if t.get("espejo"):
            pre += ",hflip"
    f = [f"[0:v]{pre},format=yuv420p,eq=contrast=1.05:saturation=1.12,vignette=PI/6[b0]"]
    cur = "b0"
    if "temblor" in fx or "golpe" in fx:
        amp = 16 if "golpe" in fx else 9
        dec = "exp(-t*4)" if "golpe" in fx else "1"
        f.append(f"[{cur}]scale={pw + 2 * amp}:{ph + 2 * amp},"
                 f"crop={pw}:{ph}:'{amp}+{amp}*sin(t*71)*{dec}':'{amp}+{amp}*cos(t*59)*{dec}'[b1]")
        cur = "b1"
    k = 1
    if "lineas" in fx:
        ins += ["-framerate", "12", "-stream_loop", "-1", "-i", lineas_pat.replace("%d", "%d")]
        f.append(f"[{k}:v]format=rgba,fps={FPS},colorchannelmixer=aa=0.55[ln];[{cur}][ln]overlay=shortest=1[b2]")
        cur, k = "b2", k + 1
    if "flash" in fx:
        f.append(f"[{cur}]fade=t=in:st=0:d=0.28:color=white[b3]")
        cur = "b3"
    if "blanco" in t:  # destello en un momento de la toma (s)
        a = float(t["blanco"])
        f.append(f"color=white:s={pw}x{ph}:r={FPS}:d={dur},format=rgba,"
                 f"fade=t=in:st={a}:d=0.04:alpha=1,fade=t=out:st={a + 0.06}:d=0.35:alpha=1[wh];"
                 f"[{cur}][wh]overlay[b4]")
        cur = "b4"
    if "fundido" in fx:
        f.append(f"[{cur}]fade=t=out:st={dur - 0.45}:d=0.45[b5]")
        cur = "b5"
    f.append(f"[{cur}]trim=0:{dur},setpts=PTS-STARTPTS[v]")
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(f), "-map", "[v]",
         "-frames:v", str(n), "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "15",
         "-pix_fmt", "yuv420p", "-an", out])
    return out


# ───────────────────────── voz ─────────────────────────
def motor_voz(story):
    return (os.environ.get("VOZ_MOTOR") or story.get("tts") or "edge").lower()


_kok = None


def tts_kokoro(texto, voz, vel):
    global _kok
    if _kok is None:
        sys.path.insert(0, os.path.join(ROOT, "engine"))
        from kokoro_onnx import Kokoro
        from build import ensure_model
        _kok = Kokoro(*ensure_model())
    a, sr = _kok.create(texto, voice=voz, speed=vel, lang="es-419")
    return np.asarray(a, dtype=np.float32), sr


def tts_edge(texto, voz, vel, tono, out):
    import edge_tts
    rate = f"{round((vel - 1) * 100):+d}%"
    asyncio.run(edge_tts.Communicate(texto, voz, rate=rate, pitch=tono or "+0Hz").save(out))


def linea_audio(story, quien, texto, motor):
    cfg = dict(story.get("voces", {}).get(quien, {}))
    if not cfg:
        idx = list(story.get("voces", {})).index(quien) if quien in story.get("voces", {}) else 0
        cfg = {"kokoro": KOKORO_DEF[idx % 3]}
    vel = float(cfg.get("vel", 1.05))
    st = float(cfg.get("semitonos", 0))
    clave = h({"q": quien, "t": texto, "c": cfg, "m": motor})
    out = os.path.join(CACHE, "voz", f"{clave}.wav")
    if os.path.exists(out):
        return out, motor
    os.makedirs(os.path.dirname(out), exist_ok=True)
    raw = out + ".raw.wav"
    usado = motor
    try:
        if motor == "edge":
            mp3 = out + ".mp3"
            tts_edge(texto, cfg.get("edge", "es-MX-JorgeNeural"), vel, cfg.get("tono"), mp3)
            run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", "24000", "-ac", "1", raw])
        else:
            raise RuntimeError("kokoro")
    except Exception as e:
        if motor == "edge":
            log(f"AVISO: voz edge no disponible ({type(e).__name__}); uso kokoro.")
        usado = "kokoro"
        a, sr = tts_kokoro(texto, cfg.get("kokoro", "em_alex"), vel)
        sf.write(raw, a, sr)
    r = 2 ** (st / 12)
    af = [f"asetrate={int(24000 * r)}", "aresample=24000", f"atempo={1 / r:.4f}"] if st else []
    if cfg.get("grito"):
        af += ["acompressor=threshold=-18dB:ratio=4:makeup=4", "aecho=0.8:0.6:40:0.25"]
    af += ["silenceremove=start_periods=1:start_threshold=-45dB", "areverse",
           "silenceremove=start_periods=1:start_threshold=-45dB", "areverse", f"aresample={SR}"]
    run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", ",".join(af), "-ac", "1", out])
    return out, usado


# ───────────────────────── sonido (música y efectos sintetizados, sin derechos) ─────────────────────────
def ruido_rosa(n, rng):
    w = rng.standard_normal(n).astype(np.float32)
    f = np.fft.rfft(w)
    k = np.arange(len(f)); k[0] = 1
    f /= np.sqrt(k)
    p = np.fft.irfft(f, n).astype(np.float32)
    return p / (np.abs(p).max() + 1e-9)


def banda(x, lo, hi):
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x)).astype(np.float32)


def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return (np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)).astype(np.float32)


def sfx(k, dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if k == "golpe":  # patada al balón
        n = int(0.35 * SR); t = t[:n]
        return (0.9 * np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 30)) * t) * env(n, 0.002, 0.08)
                + 0.5 * banda(rng.standard_normal(n).astype(np.float32), 800, 5000) * env(n, 0.001, 0.025))
    if k == "boom":  # impacto grave de clímax
        n = int(2.2 * SR); t = t[:n] if len(t) >= n else np.arange(n) / SR
        return (np.sin(2 * np.pi * (28 + 40 * np.exp(-t * 3)) * t) * env(n, 0.004, 0.7)
                + 0.35 * banda(rng.standard_normal(n).astype(np.float32), 30, 400) * env(n, 0.002, 0.4))
    if k == "whoosh":
        n = int(0.7 * SR); t = np.arange(n) / SR
        w = rng.standard_normal(n).astype(np.float32)
        a = banda(w, 300, 1200) * np.sin(np.pi * t / t[-1]) ** 2
        b = banda(w, 1200, 5000) * np.sin(np.pi * np.clip(t / t[-1] * 1.3 - 0.15, 0, 1)) ** 4
        return 0.6 * (a + b)
    if k == "silbato":
        n = int(0.9 * SR); t = np.arange(n) / SR
        return 0.35 * np.sin(2 * np.pi * 2900 * t + 3 * np.sin(2 * np.pi * 38 * t)) * env(n, 0.02, 0.6)
    if k == "latido":
        n = int(0.9 * SR); out = np.zeros(n, np.float32)
        for s0 in (0, 0.28):
            m = int(0.25 * SR); tt = np.arange(m) / SR
            out[int(s0 * SR):int(s0 * SR) + m] += np.sin(2 * np.pi * 55 * tt) * env(m, 0.005, 0.07)
        return out
    if k in ("estadio", "ovacion"):  # multitud (crece y baja)
        base = banda(ruido_rosa(n, rng), 250, 3500) * 2.5
        sw = np.sin(np.pi * np.clip(t / max(dur, 0.1), 0, 1)) ** 0.6
        if k == "ovacion":
            cl = np.zeros(n, np.float32)
            idx = rng.integers(0, n - 400, int(dur * 900))
            for i0 in idx:
                cl[i0:i0 + 300] += rng.standard_normal(300).astype(np.float32) * np.exp(-np.arange(300) / 40)
            base = base + 0.25 * banda(cl, 900, 6000)
        return (base * sw).astype(np.float32)
    return np.zeros(n, np.float32)


def nota(f, n, rng, brillo=4):
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * k * t + rng.uniform(0, 6)) / k ** 1.3 for k in range(1, brillo + 1))
    return (s * (1 + 0.004 * np.sin(2 * np.pi * 5 * t))).astype(np.float32)


def musica(total, tc, pausa, rng):
    """Música épica original: cuerdas menores que crecen, tambores que aceleran, silencio, clímax mayor."""
    n = int(total * SR)
    out = np.zeros(n, np.float32)
    bpm = 92
    beat = 60 / bpm
    prog = [(110.0, "m"), (87.31, "M"), (130.81, "M"), (98.0, "M")]  # Am F C G
    bar = beat * 4
    t = 0.0
    k = 0
    while t < total:
        root, q = prog[k % 4]
        tens = min(1, t / max(tc, 1))
        if t >= tc:
            root, q = (110.0, "M") if k % 2 == 0 else (146.83, "M")  # A mayor / D mayor: triunfo
        m = int(min(bar * 2, total - t) * SR)
        if m <= 0:
            break
        tri = [root, root * (1.1892 if q == "m" else 1.2599), root * 1.4983, root * 2]
        pad = sum(nota(f, m, rng) for f in tri) / 4
        sw = np.minimum(1, np.arange(m) / (0.6 * SR)) * np.minimum(1, (m - np.arange(m)) / (0.4 * SR))
        vol = 0.18 + 0.32 * tens + (0.25 if t >= tc else 0)
        out[int(t * SR):int(t * SR) + m] += pad * sw * vol
        t += bar * 2
        k += 1
    # tambores (taiko sintetizado) que se aceleran hacia el clímax
    t = 0.0
    while t < total:
        tens = min(1, t / max(tc, 1))
        paso = beat * (2 if tens < 0.4 else 1 if tens < 0.8 else 0.5)
        if t >= tc:
            paso = beat
        m = int(0.5 * SR)
        tt = np.arange(m) / SR
        g = 0.25 + 0.5 * tens
        hit = (np.sin(2 * np.pi * (60 + 50 * np.exp(-tt * 25)) * tt) * env(m, 0.002, 0.18) * g)
        i0 = int(t * SR)
        out[i0:i0 + m] += hit[:max(0, min(m, n - i0))]
        t += paso
    # arpegio agudo en la segunda mitad
    t = tc * 0.5
    while t < total:
        root = 220.0 if t < tc else 440.0
        f = root * [1, 1.1892 if t < tc else 1.2599, 1.4983, 2][int(t / (beat / 2)) % 4]
        m = int(beat / 2 * SR)
        i0 = int(t * SR)
        seg = nota(f, m, rng, 3) * env(m, 0.005, 0.12) * 0.12
        out[i0:i0 + m] += seg[:max(0, min(m, n - i0))]
        t += beat / 2
    if pausa:  # silencio dramático antes del clímax
        a, b = int((tc - pausa) * SR), int(tc * SR)
        rampa = np.linspace(1, 0, int(0.15 * SR))
        out[a:a + len(rampa)] *= rampa
        out[a + len(rampa):b] = 0
    return out


def mezcla(story, plan, total, tc, voces, out):
    rng = np.random.default_rng(11)
    n = int(total * SR) + SR
    vtrack = np.zeros(n, np.float32)
    fx = np.zeros(n, np.float32)
    for (t0, wav) in voces:
        a, sr = sf.read(wav, dtype="float32")
        if a.ndim > 1:
            a = a.mean(1)
        a = a / (np.abs(a).max() + 1e-9) * 0.85
        i0 = int(t0 * SR)
        vtrack[i0:i0 + len(a)] += a[:max(0, n - i0)]
    for p in plan:
        for s in p["toma"].get("sfx", []):
            s = {"k": s} if isinstance(s, str) else s
            d = float(s.get("dur", p["dur"]))
            a = sfx(s["k"], d, rng) * float(s.get("g", 0.7))
            i0 = int((p["t0"] + float(s.get("at", 0))) * SR)
            fx[i0:i0 + len(a)] += a[:max(0, n - i0)]
    if story.get("ambiente", True):  # murmullo del estadio todo el video
        amb = banda(ruido_rosa(n, rng), 200, 2500) * 0.9
        fx += amb * 0.12
    if story.get("musica_archivo"):
        tmp = out + ".mus.wav"
        run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", ruta(story["musica_archivo"]),
             "-t", f"{n / SR}", "-ac", "1", "-ar", str(SR), tmp])
        mus, _ = sf.read(tmp, dtype="float32")
        mus = np.pad(mus, (0, max(0, n - len(mus))))[:n] * 0.5
    else:
        mus = np.pad(musica(total, tc, story.get("pausa", 0.7), rng), (0, SR))[:n]
    # baja la música cuando hablan
    e = np.convolve(np.abs(vtrack), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.5 * np.clip(e * 12, 0, 1)
    mix = vtrack * 1.0 + fx * 0.8 + mus * 0.55 * duck
    mix = np.tanh(mix * 1.1) * 0.89
    sf.write(out, np.stack([mix, mix], 1), SR)


# ───────────────────────── subtítulos ─────────────────────────
def ass_tiempo(s):
    s = max(0, s)
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"


def subtitulos(story, subs, marca, out):
    pw, ph, top = geometria(story)
    ac = marca["acento"].lstrip("#")
    acc = f"&H00{ac[4:6]}{ac[2:4]}{ac[0:2]}&"
    y = top + ph + 46
    with open(out, "w", encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n"
                "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
                "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
                "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                f"Style: S,Montserrat SemiBold,{story.get('sub_tam', 50)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,"
                f"0,0,0,0,100,100,0,0,1,0,0,8,60,60,{y},1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        for a, b, txt in subs:
            t = txt
            while "*" in t:
                t = t.replace("*", "{\\c" + acc + "}", 1).replace("*", "{\\c&H00FFFFFF&}", 1)
            f.write(f"Dialogue: 0,{ass_tiempo(a)},{ass_tiempo(b)},S,,0,0,0,,{{\\fad(80,80)}}{t}\n")


# ───────────────────────── principal ─────────────────────────
def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    path = sys.argv[1]
    story = json.load(open(path, encoding="utf-8"))
    sid = story.get("id") or os.path.splitext(os.path.basename(path))[0]
    marca = MARCAS[story.get("marca", "senorfutbol")]
    outdir = os.path.join(ROOT, "salida", sid)
    tmp = os.path.join(outdir, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    pw, ph, top = geometria(story)
    if "--prompts" in sys.argv:  # hoja para copiar y pegar en Gemini (cada prompt ya trae estilo y personajes)
        import re
        est, pers = story.get("estilo", ""), story.get("personajes", {})
        carpeta = os.path.dirname(story["tomas"][0].get("src", f"anime/img/{sid}/t01.png"))
        L = [f"# Prompts para Gemini — {story['titulo'].replace('*', '')}", "",
             "## Cómo usarla", "1. Abre un chat nuevo en Gemini (modelo de imagen) y genera primero las HOJAS DE PERSONAJE.",
             "2. Para cada toma: adjunta la hoja del personaje que aparece y pega el prompt tal cual.",
             "3. Si sale texto, logos o escudos, pide: \"same image, remove all text and logos\".",
             f"4. Descarga cada imagen y guárdala con su nombre (t01.png, t02.png…) en `{carpeta}/`.",
             f"5. En la Mac: `python3 engine/build_anime.py anime/{os.path.basename(path)}`", "",
             "## Hojas de personaje", ""]
        for k, v in pers.items():
            L += [f"### {k}", "```", f"Character reference sheet of {v}. Front view, side view and back view, full body, "
                  f"neutral pose, plain dark background. {est} Wide 16:9 image.", "```", ""]
        L += ["## Tomas", ""]
        for i, tm in enumerate(story["tomas"]):
            pr = tm.get("prompt", "")
            usa = [k for k in pers if re.search(rf"\b{k}\b", pr)]
            for k in usa:
                pr = re.sub(rf"\b{k}'s\b", f"the {k.lower()}'s", pr)
                pr = re.sub(rf"\b{k}\b", f"the {k.lower()} ({pers[k]})", pr, count=1)
                pr = re.sub(rf"\b{k}\b", f"the {k.lower()}", pr)
            d = tm.get("dice", {})
            d = d[0] if isinstance(d, list) and d else d
            L += [f"### {os.path.basename(tm.get('src', ''))}" + (f"  · adjunta hoja: {', '.join(usa)}" if usa else "")
                  + (f"  · dice: “{d['t']}”" if d else ""),
                  "```", f"Generate a wide 16:9 image. {pr[0].upper() + pr[1:]}. {est}", "```", ""]
            if tm.get("video_prompt"):
                L += ["> Clip opcional (modo híbrido): " + tm["video_prompt"], ""]
        out = os.path.join(outdir, f"prompts-{sid}.md")
        open(out, "w", encoding="utf-8").write("\n".join(L))
        log(f"prompts: {out}")
        return
    lin = lineas_velocidad(os.path.join(CACHE, f"lineas_{pw}x{ph}"), pw, ph)

    # 1) voces: la toma dura al menos lo que dura su diálogo
    motor = motor_voz(story)
    usados = set()
    plan, t0 = [], 0.0
    for i, tm in enumerate(story["tomas"]):
        dichos = tm.get("dice", [])
        dichos = [dichos] if isinstance(dichos, dict) else dichos
        lineas, fin = [], 0.0
        for d in dichos:
            if d.get("audio"):
                wav = os.path.join(tmp, f"v{i}_{len(lineas)}.wav")
                run(["ffmpeg", "-v", "error", "-y", "-i", ruta(d["audio"]), "-ac", "1", "-ar", str(SR), wav])
            else:
                wav, u = linea_audio(story, d.get("quien", "NARRADOR"), d["t"].replace("*", ""), motor)
                usados.add(u)
            ld = sf.info(wav).duration
            at = float(d.get("at", 0.15))
            lineas.append((at, wav, ld, d))
            fin = max(fin, at + ld + 0.35)
        dur = max(float(tm.get("dur", 2.2)), fin)
        tm = {**tm, "dur": round(dur, 3)}
        plan.append({"toma": tm, "t0": t0, "dur": dur, "lineas": lineas})
        t0 += dur
    total = t0
    tc = next((p["t0"] for p in plan if p["toma"].get("climax")), total * 0.7)
    log(f"{len(plan)} tomas · {total:.1f} s · clímax en {tc:.1f} s · voz: {', '.join(sorted(usados)) or 'archivos'}")

    # 2) tomas
    piezas = []
    for i, p in enumerate(plan):
        piezas.append(render_toma(story, i, p["toma"], pw, ph, tmp, lin))
    lst = os.path.join(tmp, "lista.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{x}'\n" for x in piezas)
    pic = os.path.join(tmp, "imagen.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", pic])

    # 3) audio + subtítulos
    cierre_d = float(story.get("cierre", {}).get("dur", 3.5))
    voces, subs = [], []
    for p in plan:
        for at, wav, ld, d in p["lineas"]:
            a = p["t0"] + at
            voces.append((a, wav))
            if d.get("sub", True):
                subs.append((a, max(a + ld + 0.25, a + 1.1), d.get("st", d["t"])))
    wav = os.path.join(tmp, "mezcla.wav")
    mezcla(story, plan, total + cierre_d, tc, voces, wav)
    ass = os.path.join(tmp, "subs.ass")
    subtitulos(story, subs, marca, ass)

    # 4) composición final (una sola codificación)
    bg, cie = os.path.join(tmp, "fondo.png"), os.path.join(tmp, "cierre.png")
    fondo_titulo(story, marca, bg)
    tarjeta_cierre(story, marca, cie)
    mp4 = os.path.join(outdir, f"{sid}.mp4")
    fc = (f"[0:v][1:v]overlay=0:{top}:shortest=1,ass={ass}:fontsdir={FONTS},fps={FPS},format=yuv420p[m];"
          f"[2:v]scale=1188:2112,zoompan=z='1.1-0.1*on/{int(cierre_d * FPS)}':d={int(cierre_d * FPS)}:s={W}x{H}:fps={FPS},"
          f"fade=t=in:st=0:d=0.35,format=yuv420p[c];[m][c]concat=n=2:v=1:a=0[v]")
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", bg, "-i", pic,
         "-i", cie, "-i", wav,
         "-filter_complex", fc, "-map", "[v]", "-map", "3:a", "-t", f"{total + cierre_d:.2f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", mp4])

    # 5) portada, hoja de revisión y texto para publicar
    tp = next((p["t0"] + p["dur"] / 2 for p in plan if p["toma"].get("portada")), plan[0]["dur"] / 2)
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{tp:.2f}", "-i", mp4, "-frames:v", "1", "-q:v", "2",
         os.path.join(outdir, "portada.jpg")])
    cols = 6
    filas = math.ceil(len(plan) / cols)
    sel = "+".join(f"eq(n\\,{int((p['t0'] + p['dur'] * 0.6) * FPS)})" for p in plan)
    run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-vf",
         f"select='{sel}',crop=1080:{ph + 260}:0:{top - 40},scale=360:-2,tile={cols}x{filas}",
         "-frames:v", "1", "-q:v", "3", os.path.join(outdir, "revision.jpg")])
    post = story.get("post", "")
    if story.get("hashtags"):
        post += "\n\n" + " ".join(story["hashtags"])
    open(os.path.join(outdir, "post.txt"), "w", encoding="utf-8").write(post)
    shutil.rmtree(tmp, ignore_errors=True)
    log(f"listo: {mp4} ({total + cierre_d:.1f} s)")


if __name__ == "__main__":
    main()
