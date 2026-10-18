"""Motores de voz para los reels de Señor Fútbol.

Motores disponibles (se eligen en config/voz.json, en la historia con "tts" o con la variable VOZ_MOTOR):
  kokoro      voz offline gratuita (em_alex). Es el respaldo: siempre funciona.
  elevenlabs  voz más expresiva por API (tu voz clonada o una de su biblioteca). Gasta créditos.
  chatterbox  tu voz clonada a partir de una grabación de referencia, con control de emoción.
              Gratis y local (licencia MIT); en la Mac usa el chip M (mps).

Si el motor elegido no está disponible (sin llave, sin internet, sin paquete), build.py
regresa solo a kokoro para TODO el video, para no mezclar voces.

Cada línea generada se guarda en ~/.cache/senorfutbol/voz/, así la hoja de revisión y el
video final usan el mismo audio y ElevenLabs no cobra dos veces la misma línea.
"""
import hashlib, json, os, subprocess, tempfile, urllib.error, urllib.request
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.expanduser("~/.cache/senorfutbol/voz")
VEL_BASE = 1.12  # la velocidad "normal" de las historias (pensada para kokoro)


class MotorNoDisponible(Exception):
    pass


def cargar_config(story):
    cfg = {}
    p = os.path.join(ROOT, "config", "voz.json")
    if os.path.exists(p):
        cfg = json.load(open(p, encoding="utf-8"))
    motor = os.environ.get("VOZ_MOTOR") or story.get("tts") or cfg.get("motor") or "kokoro"
    return motor.strip().lower(), cfg


def _llave(nombre_env, archivo):
    v = os.environ.get(nombre_env, "").strip()
    if v:
        return v
    p = os.path.expanduser(archivo)
    if os.path.exists(p):
        return open(p, encoding="utf-8").read().strip()
    return ""


def _recortar(a, sr, umbral=0.012, margen=0.04):
    """Quita silencio al inicio y al final para que los 'gap' de la historia manden."""
    idx = np.where(np.abs(a) > umbral)[0]
    if not len(idx):
        return a
    m = int(margen * sr)
    return a[max(0, idx[0] - m): min(len(a), idx[-1] + m)]


def _tempo(a, sr, factor):
    """Cambia la velocidad sin cambiar el tono (ffmpeg atempo)."""
    if abs(factor - 1) < 0.01:
        return a
    factor = min(2.0, max(0.5, factor))
    with tempfile.TemporaryDirectory() as d:
        i, o = os.path.join(d, "i.wav"), os.path.join(d, "o.wav")
        sf.write(i, a, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", i, "-af", f"atempo={factor:.3f}", o], check=True)
        b, _ = sf.read(o, dtype="float32")
    return b if b.ndim == 1 else b.mean(1)


def remuestrear(a, sr, sr_dest):
    if sr == sr_dest:
        return a
    n = int(round(len(a) * sr_dest / sr))
    return np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)


class Voz:
    """Envoltura común: caché por línea + recorte de silencios."""

    def __init__(self, motor, params, generar, recortar=True):
        self.motor, self.params, self._generar, self._recortar = motor, params, generar, recortar

    def decir(self, texto, vel=VEL_BASE, previo="", siguiente=""):
        clave = hashlib.sha1(json.dumps([self.motor, self.params, texto, round(vel, 3), previo, siguiente],
                                        ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        os.makedirs(CACHE, exist_ok=True)
        f = os.path.join(CACHE, f"{self.motor}-{clave[:20]}.wav")
        if os.path.exists(f):
            a, sr = sf.read(f, dtype="float32")
            return a, sr
        a, sr = self._generar(texto, vel, previo, siguiente)
        a = np.asarray(a, dtype=np.float32)
        if self._recortar:
            a = _recortar(a, sr)
        if len(a) < sr * 0.15:
            raise MotorNoDisponible(f"{self.motor} regresó audio vacío")
        sf.write(f, a, sr)
        return a, sr


# ---------- kokoro (respaldo) ----------
def kokoro(story, cfg):
    from kokoro_onnx import Kokoro
    from build import ensure_model
    m, v = ensure_model()
    k = Kokoro(m, v)
    voz = story.get("voice") or cfg.get("kokoro", {}).get("voz", "em_alex")

    def gen(texto, vel, previo, siguiente):
        return k.create(texto, voice=voz, speed=vel, lang="es-419")

    return Voz("kokoro", {"voz": voz}, gen, recortar=False)


# ---------- ElevenLabs ----------
def elevenlabs(story, cfg):
    c = cfg.get("elevenlabs", {})
    key = _llave("ELEVENLABS_API_KEY", c.get("archivo_llave", "~/.config/senorfutbol/elevenlabs.key"))
    vid = os.environ.get("ELEVENLABS_VOICE_ID") or story.get("voice_id") or c.get("voice_id", "")
    if not key:
        raise MotorNoDisponible("falta la llave de ElevenLabs (ELEVENLABS_API_KEY o ~/.config/senorfutbol/elevenlabs.key)")
    if not vid:
        raise MotorNoDisponible("falta voice_id de ElevenLabs en config/voz.json")
    base = os.environ.get("ELEVENLABS_URL", "https://api.elevenlabs.io").rstrip("/")
    modelo = c.get("modelo", "eleven_multilingual_v2")
    ajustes = {"stability": c.get("estabilidad", 0.35), "similarity_boost": c.get("similitud", 0.8),
               "style": c.get("estilo", 0.45), "use_speaker_boost": True}
    vel_base = c.get("velocidad", 1.05)

    def gen(texto, vel, previo, siguiente):
        body = {"text": texto, "model_id": modelo,
                "voice_settings": dict(ajustes, speed=round(min(1.2, max(0.7, vel_base * vel / VEL_BASE)), 2))}
        if previo:
            body["previous_text"] = previo
        if siguiente:
            body["next_text"] = siguiente
        if c.get("idioma"):
            body["language_code"] = c["idioma"]
        req = urllib.request.Request(f"{base}/v1/text-to-speech/{vid}?output_format=pcm_24000",
                                     data=json.dumps(body).encode(), method="POST",
                                     headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/pcm"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                pcm = r.read()
        except urllib.error.HTTPError as e:
            detalle = e.read().decode("utf-8", "ignore")[:300]
            raise MotorNoDisponible(f"ElevenLabs respondió {e.code}: {detalle}")
        except (urllib.error.URLError, OSError) as e:
            raise MotorNoDisponible(f"sin conexión a ElevenLabs ({e})")
        return np.frombuffer(pcm, dtype="<i2").astype(np.float32) / 32768.0, 24000

    return Voz("elevenlabs", {"voice_id": vid, "modelo": modelo, **ajustes, "vel": vel_base}, gen)


# ---------- Chatterbox (tu voz clonada, local) ----------
def chatterbox(story, cfg):
    c = cfg.get("chatterbox", {})
    ref = os.path.expanduser(c.get("referencia", ""))
    if not ref or not os.path.exists(ref):
        raise MotorNoDisponible(f"no encuentro la grabación de referencia de tu voz: '{c.get('referencia', '')}'")
    try:
        import torch  # noqa: F401
        import chatterbox  # noqa: F401
    except ImportError:
        raise MotorNoDisponible("falta el paquete: python3 -m pip install chatterbox-tts")
    params = {"ref": os.path.basename(ref), "ref_mtime": int(os.path.getmtime(ref)),
              "exageracion": c.get("exageracion", 0.6), "cfg": c.get("cfg", 0.4),
              "temperatura": c.get("temperatura", 0.8), "vel": c.get("velocidad", 1.05)}
    estado = {}

    def modelo():
        if "m" not in estado:
            import torch
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS
            dev = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
            if dev != "cuda":  # los pesos vienen guardados para CUDA
                original = torch.load

                def carga(*a, **k):
                    k.setdefault("map_location", torch.device(dev))
                    return original(*a, **k)
                torch.load = carga
            print(f"[reel] cargando Chatterbox en {dev} (la primera vez descarga el modelo)", flush=True)
            m = ChatterboxMultilingualTTS.from_pretrained(device=dev)
            m.prepare_conditionals(ref, exaggeration=params["exageracion"])  # tu voz se analiza una sola vez
            estado["m"] = m
        return estado["m"]

    def gen(texto, vel, previo, siguiente):
        m = modelo()
        wav = m.generate(texto, language_id="es", exaggeration=params["exageracion"],
                         cfg_weight=params["cfg"], temperature=params["temperatura"])
        a = wav.squeeze().detach().cpu().numpy().astype(np.float32)
        return _tempo(a, m.sr, params["vel"] * vel / VEL_BASE), m.sr

    return Voz("chatterbox", params, gen)


MOTORES = {"kokoro": kokoro, "elevenlabs": elevenlabs, "chatterbox": chatterbox}


def crear(story, motor=None):
    m, cfg = cargar_config(story)
    m = motor or m
    if m not in MOTORES:
        raise MotorNoDisponible(f"motor de voz '{m}' no existe ({', '.join(MOTORES)})")
    return MOTORES[m](story, cfg)
