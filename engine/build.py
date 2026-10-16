#!/usr/bin/env python3
"""Fábrica de reels Señor Fútbol.

Uso:
  python3 engine/build.py stories/<historia>.json --preview   # genera voz + hoja de revisión (PNG)
  python3 engine/build.py stories/<historia>.json             # genera el video final (MP4)

Salida en salida/<id>/: voz, mezcla, hoja de revisión, video y post.txt (texto para publicar).
"""
import json, os, re, subprocess, sys, hashlib
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "engine")
CACHE = os.path.expanduser("~/.cache/senorfutbol")
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FPS = 30
SR = 44100
SCENE_TYPES = {"stats", "table", "results", "scoreboard", "play", "count", "headline", "compare", "ranking", "question", "board"}


def log(*a):
    print("[reel]", *a, flush=True)


def ensure_model():
    os.makedirs(CACHE, exist_ok=True)
    for f, src in (("kokoro.onnx", "kokoro-v1.0.onnx"), ("voices.bin", "voices-v1.0.bin")):
        dst = os.path.join(CACHE, f)
        if not os.path.exists(dst) or os.path.getsize(dst) < 1_000_000:
            log("descargando", src)
            subprocess.run(["curl", "-sSL", "--retry", "3", "-o", dst, MODEL_URL + src], check=True)
    return os.path.join(CACHE, "kokoro.onnx"), os.path.join(CACHE, "voices.bin")


def validate(story):
    errs = []
    for k in ("id", "scenes"):
        if k not in story:
            errs.append(f"falta '{k}'")
    sc = story.get("scenes", [])
    if not 3 <= len(sc) <= 16:
        errs.append(f"usa entre 3 y 16 escenas (hay {len(sc)})")
    for i, s in enumerate(sc):
        if s.get("type") not in SCENE_TYPES:
            errs.append(f"escena {i}: tipo '{s.get('type')}' no existe ({', '.join(sorted(SCENE_TYPES))})")
        if not s.get("say"):
            errs.append(f"escena {i}: falta 'say' (lo que dice la voz)")
        if re.search(r"\d", s.get("say", "")):
            errs.append(f"escena {i}: 'say' tiene dígitos; escribe los números con letra para que la voz los lea bien")
    if errs:
        sys.exit("Historia inválida:\n - " + "\n - ".join(errs))


def tts(story, outdir):
    from kokoro_onnx import Kokoro
    m, v = ensure_model()
    k = Kokoro(m, v)
    voice = story.get("voice", "em_alex")
    sr = 24000
    parts = [np.zeros(int(sr * 0.35), np.float32)]
    t = 0.35
    lines = []
    for i, s in enumerate(story["scenes"]):
        a, sr = k.create(s["say"], voice=voice, speed=s.get("speed", 1.12), lang="es-419")
        a = a.astype(np.float32)
        d = len(a) / sr
        lines.append({"i": i, "start": round(t, 3), "end": round(t + d, 3)})
        gap = s.get("gap", 0.3)
        parts += [a, np.zeros(int(sr * gap), np.float32)]
        t += d + gap
    parts.append(np.zeros(int(sr * 0.9), np.float32))
    t += 0.9
    y = np.concatenate(parts)
    y = y / max(1e-6, np.abs(y).max()) * 0.92
    raw = os.path.join(outdir, "voz_raw.wav")
    sf.write(raw, y, sr)
    timing = {"total": round(t, 3), "lines": lines}
    json.dump(timing, open(os.path.join(outdir, "timing.json"), "w"), indent=1)
    log(f"voz lista: {t:.1f} s")
    return raw, timing


def lp(x, a):
    y = np.empty_like(x); s = 0.0
    for k in range(len(x)):
        s += a * (x[k] - s); y[k] = s
    return y


def mix(story, outdir, raw, timing, hits):
    proc = os.path.join(outdir, "voz.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-ar", str(SR), "-af",
                    "highpass=f=85,equalizer=f=220:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.2:g=3.5,"
                    "equalizer=f=7000:t=q:w=1:g=1.5,acompressor=threshold=-20dB:ratio=3.5:attack=4:release=90:makeup=4,alimiter=limit=0.9",
                    proc], check=True)
    v, _ = sf.read(proc)
    v = v if v.ndim == 1 else v.mean(1)
    N = len(v)
    seed = int(hashlib.md5(story["id"].encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)

    def env(n, a, d):
        x = np.arange(n) / SR
        return np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / d)

    def add(buf, sig, at):
        i = int(at * SR)
        if i < 0 or i >= len(buf): return
        j = min(len(buf), i + len(sig)); buf[i:j] += sig[:j - i]

    bpm = [118, 120, 122, 124, 126, 128][seed % 6]
    beat = 60 / bpm
    progs = [[55.0, 43.65, 65.41, 49.0], [41.2, 49.0, 55.0, 36.71], [49.0, 41.2, 43.65, 55.0], [43.65, 55.0, 49.0, 41.2]]
    roots = progs[(seed // 7) % len(progs)]
    kick = np.sin(2 * np.pi * np.cumsum(45 + 75 * np.exp(-np.arange(int(.3 * SR)) / SR / 0.04)) / SR) * env(int(.3 * SR), .002, .11)
    cn = rng.standard_normal(int(.18 * SR)); clap = (cn - lp(cn, 0.15)) * env(len(cn), .001, .05) * 0.55
    hn = rng.standard_normal(int(.05 * SR)); hat = (hn - lp(hn, 0.5)) * env(len(hn), .0005, .012) * 0.25
    mus = np.zeros(N)
    L = timing["lines"]
    q_start = L[-1]["start"] if story["scenes"][-1]["type"] == "question" else None
    q_end = L[-1]["end"] - 1.2 if q_start else None
    for b in range(int(N / SR / beat) + 1):
        tb = b * beat
        brk = q_start is not None and q_start <= tb < q_end
        if not brk: add(mus, kick, tb)
        if b % 2 == 1 and not brk: add(mus, clap, tb)
        add(mus, hat, tb + beat / 2)
        if not brk:
            f = roots[(b // 4) % 4]; n = int(beat / 2 * SR); x = np.arange(n) / SR
            add(mus, (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x)) * env(n, .005, .12) * 0.35, tb + beat / 2)
    w = int(.05 * SR)
    ve = np.convolve(np.abs(v), np.ones(w) / w, mode="same")
    duck = lp(np.where(ve > 0.02, 0.45, 1.0), 0.0008)
    mus = mus / max(1e-6, np.abs(mus).max()) * 0.30 * duck
    sfx = np.zeros(N)
    for h in hits:
        if h["k"] == "whoosh":
            n = int(.38 * SR); x = np.arange(n) / n
            add(sfx, lp(rng.standard_normal(n), 0.25) * np.sin(np.pi * x) ** 1.5 * 0.5, h["t"] - .32)
        else:
            n = int(.45 * SR); x = np.arange(n) / SR
            s = np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-x / 0.03)) / SR) * np.exp(-x / 0.16)
            add(sfx, (s + rng.standard_normal(n) * np.exp(-x / 0.008) * 0.3) * 0.7, h["t"])
    out = v * 0.95 + mus + sfx * 0.55
    out = out / max(1e-6, np.abs(out).max()) * 0.95
    path = os.path.join(outdir, "mezcla.wav")
    sf.write(path, out, SR)
    return path


def link_lines(story):
    cfg = os.path.join(ROOT, "config", "ligas.json")
    if not os.path.exists(cfg):
        return []
    kind = story.get("kind", "noticia")
    out = []
    for l in json.load(open(cfg, encoding="utf-8")).get("ligas", []):
        if l.get("url") and l.get("para") in (kind, "ambos"):
            out.append(f"{l['texto']} {l['url']}")
    return out


def caption_text(story):
    lines = [story.get("post", "").strip()]
    links = link_lines(story)
    if links:
        lines.append("\n".join(links))
    if story.get("hashtags"):
        lines.append(" ".join(story["hashtags"]))
    txt = "\n\n".join(l for l in lines if l)
    if story.get("sources"):
        txt += "\n\n---\nFuentes (no publicar):\n" + "\n".join("- " + s for s in story["sources"])
    return txt


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
        br = pw.chromium.launch()
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.add_init_script(f"window.STORY={json.dumps(story, ensure_ascii=False)};window.TIMING={json.dumps(timing)};")
        pg.goto(f"file://{ENGINE}/reel.html")
        try:
            pg.wait_for_function("window.READY===true", timeout=20000)
        except Exception:
            pass
        if errors or not pg.evaluate("window.READY===true"):
            sys.exit("Error en la plantilla: " + "; ".join(errors))
        if preview:
            ts = []
            for L in timing["lines"]:
                ts.append(L["start"] + (L["end"] - L["start"]) * 0.45)
                ts.append(L["end"] - 0.05)
            pdir = os.path.join(outdir, "revision"); os.makedirs(pdir, exist_ok=True)
            for k, t in enumerate(ts):
                pg.evaluate(f"renderAt({t})")
                pg.screenshot(path=f"{pdir}/f{k:02d}.png")
            br.close()
            cols = min(len(ts), 6)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{pdir}/f%02d.png", "-vf",
                            f"scale=270:480,tile={cols}x{(len(ts) + cols - 1) // cols}:padding=6:color=white",
                            "-frames:v", "1", os.path.join(outdir, "revision.png")], check=True)
            log("hoja de revisión:", os.path.join(outdir, "revision.png"), "| cuadros individuales en", pdir)
            return
        hits = pg.evaluate("window.getHits()")
        audio = mix(story, outdir, raw, timing, hits)
        out = os.path.join(outdir, f"{story['id']}.mp4")
        n = int(timing["total"] * FPS)
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                               "-i", audio, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", "-movflags", "+faststart", out],
                              stdin=subprocess.PIPE)
        for f in range(n):
            pg.evaluate(f"renderAt({f / FPS})")
            ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
            if f % 300 == 0:
                log(f"cuadro {f}/{n}")
        ff.stdin.close(); ff.wait(); br.close()
        if ff.returncode != 0:
            sys.exit("ffmpeg falló")
    open(os.path.join(outdir, "post.txt"), "w", encoding="utf-8").write(caption_text(story))
    log("VIDEO LISTO:", out)
    log("TEXTO PARA PUBLICAR:", os.path.join(outdir, "post.txt"))


if __name__ == "__main__":
    main()
