#!/usr/bin/env python3
"""Videos largos 16:9 para YouTube (Impulso Real).

Uso:
  python3 engine/build_largo.py largos/<historia>.json --preview   # voz + hoja de revisión (PNG)
  python3 engine/build_largo.py largos/<historia>.json             # video final 1920x1080 + miniatura + textos

Salida en salida/<id>/: <id>.mp4, miniatura.jpg, subtitulos.srt, youtube.txt (título, descripción con capítulos, etiquetas).
La voz usa el mismo motor que los reels (config/voz.json o VOZ_MOTOR=chatterbox para tu voz clonada en la Mac).
"""
import json, os, re, subprocess, sys, hashlib
from multiprocessing import Process
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "engine")
sys.path.insert(0, ENGINE)
FPS = 30
SR = 44100
TYPES = {"chapter", "ink", "quote", "stats", "timeline", "split", "step", "list", "duo", "end", "route"}
import base64


def plantilla(story):
    """largo = estilo dorado (episodio 1); plano = estilo de los reels de TikTok/Facebook."""
    return story.get("plantilla", "largo")


def foto(pg, story, path=None, t=None):
    """Captura un cuadro: en "plano" se lee directo del canvas (más rápido)."""
    if plantilla(story).startswith("plano"):
        data = base64.b64decode(pg.evaluate("t=>window.frame(t)", t))
        if path:
            open(path, "wb").write(data)
        return data
    pg.evaluate(f"renderAt({t})")
    return pg.screenshot(path=path, type="jpeg", quality=90) if not path else pg.screenshot(path=path)


def log(*a):
    print("[largo]", *a, flush=True)


def frases(texto):
    """Parte el texto en oraciones (cada una se genera por separado y sirve para sincronizar)."""
    t = re.sub(r"\s+", " ", texto.strip())
    partes = re.split(r"(?<=[.!?…])\s+(?=[¿¡«“\"A-ZÁÉÍÓÚÑ0-9])", t)
    return [p.strip() for p in partes if p.strip()]


def validate(story):
    errs = []
    for i, s in enumerate(story.get("scenes", [])):
        if s.get("type") not in TYPES:
            errs.append(f"escena {i}: tipo '{s.get('type')}' no existe")
        if not s.get("say"):
            errs.append(f"escena {i}: falta 'say'")
        if re.search(r"\d", s.get("say", "")):
            errs.append(f"escena {i}: 'say' tiene dígitos; escríbelos con letra")
    if errs:
        sys.exit("Historia inválida:\n - " + "\n - ".join(errs))


def tts(story, outdir):
    import voces
    motor, _ = voces.cargar_config(story)
    try:
        return _tts(story, outdir, voces.crear(story))
    except voces.MotorNoDisponible as e:
        if motor == "kokoro":
            raise
        log(f"AVISO: no se pudo usar la voz '{motor}' ({e}). Uso kokoro.")
        return _tts(story, outdir, voces.crear(story, "kokoro"), aviso=str(e))


def _tts(story, outdir, voz, aviso=""):
    import voces
    sr = 24000
    vel = story.get("speed", 1.0)
    pausa_frase, pausa_escena = story.get("pausaFrase", 0.38), story.get("pausaEscena", 0.95)
    ini = story.get("inicio", 1.2)
    parts = [np.zeros(int(sr * ini), np.float32)]
    t = ini
    scenes = []
    todas = []
    for s in story["scenes"]:
        todas.append(frases(s["say"]))
    plano = [f for fs in todas for f in fs]
    k = 0
    log(f"voz: {voz.motor} · {len(plano)} frases")
    for i, s in enumerate(story["scenes"]):
        if s["type"] == "chapter":
            parts.append(np.zeros(int(sr * 0.5), np.float32)); t += 0.5
        sents = []
        for j, f in enumerate(todas[i]):
            a, sr_a = voz.decir(f, s.get("speed", vel), plano[k - 1] if k else "", plano[k + 1] if k + 1 < len(plano) else "")
            a = voces.remuestrear(np.asarray(a, np.float32), sr_a, sr)
            d = len(a) / sr
            sents.append({"start": round(t, 3), "end": round(t + d, 3), "text": f})
            parts.append(a)
            t += d
            g = pausa_frase if j + 1 < len(todas[i]) else s.get("gap", pausa_escena + (0.6 if s["type"] == "chapter" else 0))
            parts.append(np.zeros(int(sr * g), np.float32)); t += g
            k += 1
            if k % 20 == 0:
                log(f"  {k}/{len(plano)} frases")
        scenes.append({"i": i, "start": sents[0]["start"], "end": sents[-1]["end"], "sents": sents})
    cola = story.get("cola", 2.5)
    parts.append(np.zeros(int(sr * cola), np.float32)); t += cola
    y = np.concatenate(parts)
    y = y / max(1e-6, np.abs(y).max()) * 0.92
    raw = os.path.join(outdir, "voz_raw.wav")
    sf.write(raw, y, sr)
    timing = {"total": round(t, 3), "scenes": scenes, "motor": voz.motor}
    if aviso:
        timing["aviso_voz"] = aviso
    json.dump(timing, open(os.path.join(outdir, "timing.json"), "w"), indent=1, ensure_ascii=False)
    log(f"voz lista: {t / 60:.1f} min")
    return raw, timing


def lp(x, a):
    """Filtro pasa-bajos de un polo (vectorizado con scipy si está)."""
    try:
        from scipy.signal import lfilter
        return lfilter([a], [1, a - 1], x)
    except ImportError:
        y = np.empty_like(x); s = 0.0
        for k in range(len(x)):
            s += a * (x[k] - s); y[k] = s
        return y


def ambient(N, seed):
    """Música de fondo: colchón de acordes lento + notas sueltas tipo piano, con reverberación."""
    rng = np.random.default_rng(seed)
    t = np.arange(N) / SR
    # progresión en La menor: Am - F - C - G (cada acorde 8 s)
    prog = [[110.0, 164.81, 220.0, 261.63], [87.31, 130.81, 174.61, 220.0], [65.41, 130.81, 164.81, 196.0], [98.0, 146.83, 196.0, 246.94]]
    dur = 8.0
    pad = np.zeros(N)
    nseg = int(np.ceil(N / SR / dur)) + 1
    for c in range(nseg):
        a, b = int(c * dur * SR), int((c + 1) * dur * SR + 3 * SR)
        if a >= N: break
        b = min(N, b); n = b - a; x = np.arange(n) / SR
        envl = np.minimum(1, x / 2.5) * np.minimum(1, np.maximum(0, (n / SR - x) / 3.0))
        seg = np.zeros(n)
        for f in prog[c % 4]:
            for det in (-0.6, 0.0, 0.7):
                seg += np.sin(2 * np.pi * (f + det) * x + rng.uniform(0, 6.28)) * (0.22 if f < 100 else 0.14)
        pad[a:b] += seg * envl
    pad = lp(pad, 0.06)
    pad *= 0.75 + 0.25 * np.sin(2 * np.pi * t / 23.0)
    # notas sueltas (escala menor), suaves
    escala = [220.0, 261.63, 293.66, 329.63, 392.0, 440.0, 523.25]
    bells = np.zeros(N)
    tt = 3.0
    while tt < N / SR - 2:
        f = escala[rng.integers(len(escala))]
        n = int(3.5 * SR); i0 = int(tt * SR); n = min(n, N - i0); x = np.arange(n) / SR
        s = (np.sin(2 * np.pi * f * x) + 0.25 * np.sin(4 * np.pi * f * x) + 0.08 * np.sin(6 * np.pi * f * x)) * np.exp(-x / 0.9) * np.minimum(1, x / 0.01)
        bells[i0:i0 + n] += s * 0.18
        tt += rng.choice([2.0, 3.0, 4.0, 4.0, 6.0])
    dry = pad + bells
    # reverberación: convolución con ruido que decae (3 s)
    ir_n = int(3.0 * SR)
    ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.8)
    ir = lp(ir, 0.3); ir /= np.abs(ir).sum() / 8
    from numpy.fft import rfft, irfft
    L = 1 << int(np.ceil(np.log2(N + ir_n)))
    wet = irfft(rfft(dry, L) * rfft(ir, L), L)[:N]
    out = dry * 0.55 + wet * 0.45
    return out / max(1e-6, np.abs(out).max())


def mix(story, outdir, raw, timing, hits):
    proc = os.path.join(outdir, "voz.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-ar", str(SR), "-af",
                    "highpass=f=80,equalizer=f=200:t=q:w=1:g=1.5,equalizer=f=3000:t=q:w=1.2:g=2.5,"
                    "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3,alimiter=limit=0.9",
                    proc], check=True)
    v, _ = sf.read(proc)
    v = v if v.ndim == 1 else v.mean(1)
    N = len(v)
    seed = int(hashlib.md5(story["id"].encode()).hexdigest()[:8], 16)
    mus = ambient(N, seed)
    w = int(.08 * SR)
    ve = np.convolve(np.abs(v), np.ones(w) / w, mode="same")
    duck = lp(np.where(ve > 0.015, 0.55, 1.0), 0.00025)
    mus = mus * 0.17 * duck
    if story.get("musica") == "pulso":  # pulso suave (bombo + shaker) que da ritmo sin tapar la voz
        bpm = story.get("bpm", 84); beat = 60 / bpm; rng2 = np.random.default_rng(seed + 1)
        nk = int(.35 * SR); xk = np.arange(nk) / SR
        kick = np.sin(2 * np.pi * np.cumsum(42 + 55 * np.exp(-xk / 0.035)) / SR) * np.exp(-xk / 0.14)
        hn = int(.06 * SR); hat = (lambda z: z - lp(z, 0.45))(rng2.standard_normal(hn)) * np.exp(-np.arange(hn) / SR / 0.015)
        pulse = np.zeros(N)
        for bt in range(int(N / SR / beat)):
            i0 = int(bt * beat * SR)
            for sig, off, g in ((kick, 0, 1.0 if bt % 2 == 0 else .7), (hat, beat / 2, .35)):
                j0 = i0 + int(off * SR); j1 = min(N, j0 + len(sig))
                if j0 < N: pulse[j0:j1] += sig[:j1 - j0] * g
        pulse = pulse / max(1e-6, np.abs(pulse).max()) * 0.11 * lp(np.where(ve > 0.015, 0.6, 1.0), 0.00025)
        mus = mus + pulse
    fade = int(3 * SR)
    mus[:fade] *= np.linspace(0, 1, fade); mus[-fade:] *= np.linspace(1, 0, fade)
    rng = np.random.default_rng(seed)
    sfx = np.zeros(N)

    def add(sig, at):
        i = int(at * SR)
        if 0 <= i < N:
            j = min(N, i + len(sig)); sfx[i:j] += sig[:j - i]
    for h in hits:
        if h["k"] == "tick":
            n = int(.08 * SR); x = np.arange(n) / SR
            add(np.sin(2 * np.pi * 1800 * x) * np.exp(-x / 0.012) * 0.35, h["t"])
        elif h["k"] == "whoosh":
            n = int(.9 * SR); x = np.arange(n) / n
            add(lp(rng.standard_normal(n), 0.08) * np.sin(np.pi * x) ** 2 * 0.35, h["t"] - .6)
        else:
            n = int(2.5 * SR); x = np.arange(n) / SR
            s = np.sin(2 * np.pi * np.cumsum(32 + 40 * np.exp(-x / 0.08)) / SR) * np.exp(-x / 0.9)
            add(s * 0.9 + lp(rng.standard_normal(n), 0.05) * np.exp(-x / 0.6) * 0.4, h["t"])
    out = v * 0.95 + mus + sfx * 0.30
    out = out / max(1e-6, np.abs(out).max()) * 0.95
    path = os.path.join(outdir, "mezcla.wav")
    sf.write(path, out, SR)
    return path


def ts(sec, srt=True):
    h, r = divmod(sec, 3600); m, s = divmod(r, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"
    return f"{int(h)}:{int(m):02d}:{int(s):02d}" if h else f"{int(m)}:{int(s):02d}"


def srt(timing, path, cambios=None):
    out, n = [], 1
    for sc in timing["scenes"]:
        for s in sc["sents"]:
            txt = s["text"]
            for a, b in (cambios or {}).items():  # números con letra → dígitos en los subtítulos
                txt = txt.replace(a, b)
            trozos = [txt]
            if len(txt) > 84:  # parte en comas para que no queden renglones larguísimos
                trozos, cur = [], ""
                for w in re.split(r"(?<=,)\s+", txt):
                    if cur and len(cur) + len(w) > 80:
                        trozos.append(cur); cur = w
                    else:
                        cur = (cur + " " + w).strip()
                if cur: trozos.append(cur)
            tot = sum(len(x) for x in trozos); a = s["start"]
            for x in trozos:
                b = a + (s["end"] - s["start"]) * len(x) / tot
                out.append(f"{n}\n{ts(a)} --> {ts(b)}\n{x}\n"); n += 1; a = b
    open(path, "w", encoding="utf-8").write("\n".join(out))


def youtube_txt(story, timing, path):
    yt = story.get("youtube", {})
    caps = ["0:00 " + yt.get("intro", "Introducción")]
    for sc, tm in zip(story["scenes"], timing["scenes"]):
        if sc["type"] == "chapter":
            caps.append(f"{ts(max(0, tm['start'] - 0.8), False)} {sc['title']}")
    if yt.get("cierre"):
        last = [tm for sc, tm in zip(story["scenes"], timing["scenes"]) if sc["type"] == "end"]
        if last:
            caps.append(f"{ts(last[0]['start'] - 0.5, False)} {yt['cierre']}")
    desc = yt.get("descripcion", "").strip()
    txt = (f"TÍTULO:\n{yt.get('titulo', story['id'])}\n\n"
           f"DESCRIPCIÓN:\n{desc}" + ("\n\nCapítulos:\n" + "\n".join(caps) if len(caps) > 2 else "") +
           ("\n\n" + yt["pie"].strip() if yt.get("pie") else "") +
           f"\n\nETIQUETAS:\n{', '.join(yt.get('etiquetas', []))}\n")
    if story.get("sources"):
        txt += "\n---\nFuentes (no publicar):\n" + "\n".join("- " + s for s in story["sources"])
    open(path, "w", encoding="utf-8").write(txt)


def abrir(pw, story, timing, w=1920, h=1080):
    if story.get("plantilla") == "plano_v":
        w, h = 1080, 1920
    br = pw.chromium.launch(args=["--disable-gpu"])
    pg = br.new_page(viewport={"width": w, "height": h})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.add_init_script(f"window.STORY={json.dumps(story, ensure_ascii=False)};window.TIMING={json.dumps(timing)};")
    pg.goto(f"file://{ENGINE}/{plantilla(story)}.html")
    try:
        pg.wait_for_function("window.READY===true", timeout=30000)
    except Exception:
        pass
    if errors or not pg.evaluate("window.READY===true"):
        sys.exit("Error en la plantilla: " + "; ".join(errors))
    return br, pg


def render_tramo(story, timing, f0, f1, out):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br, pg = abrir(pw, story, timing)
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                               "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "9M", "-bufsize", "14M", "-pix_fmt", "yuv420p", "-r", str(FPS), out], stdin=subprocess.PIPE)
        for f in range(f0, f1):
            ff.stdin.write(foto(pg, story, t=f / FPS))
            if (f - f0) % 900 == 0:
                log(f"tramo {os.path.basename(out)}: cuadro {f - f0}/{f1 - f0}")
        ff.stdin.close(); ff.wait(); br.close()


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    spath = sys.argv[1]
    preview = "--preview" in sys.argv
    story = json.load(open(spath, encoding="utf-8"))
    validate(story)
    outdir = os.path.join(ROOT, "salida", story["id"])
    os.makedirs(outdir, exist_ok=True)
    raw, timing = tts(story, outdir)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br, pg = abrir(pw, story, timing)
        if preview:
            pdir = os.path.join(outdir, "revision"); os.makedirs(pdir, exist_ok=True)
            for f in os.listdir(pdir): os.remove(os.path.join(pdir, f))
            k = 0
            ext = "jpg" if plantilla(story).startswith("plano") else "png"
            for sc in timing["scenes"]:
                for t in (sc["start"] + 1.5, sc["end"] - 0.1):
                    foto(pg, story, f"{pdir}/f{k:03d}.{ext}", t); k += 1
            br.close()
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{pdir}/f%03d.{ext}", "-vf",
                            f"scale={'270:480' if story.get('plantilla') == 'plano_v' else '480:270'},tile=6x{(k + 5) // 6}:padding=6:color=white", "-frames:v", "1",
                            os.path.join(outdir, "revision.png")], check=True)
            log("hoja de revisión:", os.path.join(outdir, "revision.png"), f"| {k} cuadros en", pdir)
            return
        hits = pg.evaluate("window.getHits()")
        if story.get("thumb"):
            png = os.path.join(outdir, "miniatura.png")
            if plantilla(story) == "plano":
                open(png, "wb").write(base64.b64decode(pg.evaluate("th=>window.thumbPNG(th)", story["thumb"])))
            else:
                pg.evaluate(f"renderThumb({json.dumps(story['thumb'], ensure_ascii=False)})")
                pg.screenshot(path=png)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", png, "-vf", "scale=1280:720", "-q:v", "2",
                            os.path.join(outdir, "miniatura.jpg")], check=True)
        br.close()
    audio = mix(story, outdir, raw, timing, hits)
    n = int(timing["total"] * FPS)
    if os.environ.get("LARGO_HASTA"):  # muestra corta: solo los primeros N segundos
        n = min(n, int(float(os.environ["LARGO_HASTA"]) * FPS))
    workers = max(1, min(int(os.environ.get("LARGO_PROCESOS", os.cpu_count() or 2)), 6))
    cortes = [n * k // workers for k in range(workers + 1)]
    tramos = [os.path.join(outdir, f"tramo{k}.mp4") for k in range(workers)]
    log(f"renderizando {n} cuadros ({timing['total'] / 60:.1f} min) en {workers} procesos…")
    ps = [Process(target=render_tramo, args=(story, timing, cortes[k], cortes[k + 1], tramos[k])) for k in range(workers)]
    for p in ps: p.start()
    for p in ps: p.join()
    if any(p.exitcode for p in ps):
        sys.exit("falló el render de un tramo")
    lista = os.path.join(outdir, "tramos.txt")
    open(lista, "w").write("".join(f"file '{t}'\n" for t in tramos))
    out = os.path.join(outdir, f"{story['id']}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-i", audio, "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-af", "loudnorm=I=-14:TP=-1.5",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    for t in tramos: os.remove(t)
    srt(timing, os.path.join(outdir, "subtitulos.srt"), story.get("cc"))
    youtube_txt(story, timing, os.path.join(outdir, "youtube.txt"))
    log("VIDEO LISTO:", out)
    if timing.get("aviso_voz"):
        log("AVISO de voz:", timing["aviso_voz"])


if __name__ == "__main__":
    main()
