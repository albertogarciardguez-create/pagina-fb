#!/usr/bin/env python3
"""Usa una narración ya grabada (p. ej. un MP3 de ElevenLabs con varios Shorts seguidos) en lugar de generar la voz.

  python3 engine/alinear.py voz.mp3 largos/shorts/a.json largos/shorts/b.json ...

Encuentra las pausas del audio y las asigna a los finales de oración (programación dinámica por
proporción de caracteres). Corta el audio por historia en salida/<id>/voz_raw.wav y escribe timing.json;
luego build_largo.py lo reutiliza si la historia tiene "audio_externo": true.
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_largo import frases, ROOT

SR = 24000


def pausas(y, sr, min_dur=0.06, umbral_db=-30):
    hop = int(sr * 0.01)
    e = np.array([np.sqrt(np.mean(y[i:i + hop] ** 2) + 1e-12) for i in range(0, len(y) - hop, hop)])
    db = 20 * np.log10(e / e.max())
    sil = db < umbral_db
    out, i = [], 0
    while i < len(sil):
        if sil[i]:
            j = i
            while j < len(sil) and sil[j]:
                j += 1
            if (j - i) * 0.01 >= min_dur:
                out.append(((i * 0.01), (j * 0.01)))  # (inicio, fin) del silencio
            i = j
        else:
            i += 1
    return out, db


def main():
    mp3, stories = sys.argv[1], sys.argv[2:]
    tmp = "/tmp/_alinear.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ac", "1", "-ar", str(SR), tmp], check=True)
    y, _ = sf.read(tmp, dtype="float32")
    sts = [json.load(open(p, encoding="utf-8")) for p in stories]
    sents = []  # (historia, escena, texto)
    for k, s in enumerate(sts):
        for i, sc in enumerate(s["scenes"]):
            for f in frases(sc["say"]):
                sents.append((k, i, f))
    P, db = pausas(y, SR)
    voz = np.where(db >= -30)[0]
    t0, t1 = voz[0] * 0.01, voz[-1] * 0.01 + 0.01
    P = [p for p in P if p[0] > t0 and p[1] < t1]
    # esperado: fin de cada oración (salvo la última) según proporción de caracteres
    L = np.array([len(f[2]) + 6 for f in sents], float)
    try:  # mejor estimación: duración de cada oración con la voz gratuita (misma prosodia aproximada)
        import voces
        kv = voces.crear(sts[0], "kokoro")
        L = np.array([len(kv.decir(f[2], 1.08)[0]) / 24000 + 0.25 for f in sents], float)
    except Exception as e:
        print("aviso: uso proporción de caracteres", e)
    cum = np.cumsum(L) / L.sum()
    n, m = len(sents) - 1, len(P)
    e = L / L.sum() * (t1 - t0)          # duración esperada de cada oración (incluye su pausa)
    # posición j=0 es el inicio (t0); j=1..m son las pausas; el final es t1
    pos_end = [t0] + [a_ for a_, b_ in P]   # donde termina la voz de la oración si corta en la pausa j
    pos_ini = [t0] + [b_ for a_, b_ in P]   # donde empieza la siguiente
    dur = [0.0] + [b_ - a_ for a_, b_ in P]
    INF = 1e18
    D = np.full((n + 1, m + 1), INF); B = np.zeros((n + 1, m + 1), int); D[0, 0] = 0
    for i in range(1, n + 1):
        frontera = sents[i - 1][0] != sents[i][0]
        for j in range(i, m + 1):
            best, bj = INF, 0
            for q in range(i - 1, j):
                if D[i - 1, q] >= INF: continue
                c = D[i - 1, q] + ((pos_ini[j] - pos_ini[q]) - e[i - 1]) ** 2 / max(.4, e[i - 1]) - (1.5 if frontera else .4) * dur[j]
                if c < best: best, bj = c, q
            D[i, j], B[i, j] = best, bj
    # última oración: de la pausa elegida al final
    last = min(range(n, m + 1), key=lambda j: D[n, j] + ((t1 - pos_ini[j]) - e[n]) ** 2 / max(.4, e[n]))
    cortes, j = [], last
    for i in range(n, 0, -1):
        cortes.append(P[j - 1]); j = B[i, j]
    cortes = cortes[::-1]
    starts = [t0] + [b for a, b in cortes]
    ends = [a for a, b in cortes] + [t1]
    for k, s in enumerate(sts):
        idx = [q for q, f in enumerate(sents) if f[0] == k]
        a, b = starts[idx[0]], ends[idx[-1]]
        ini, cola = s.get("inicio", 0.12), s.get("cola", 1.0)
        seg = y[max(0, int((a - 0.03) * SR)): int((b + 0.05) * SR)]
        seg = np.concatenate([np.zeros(int(ini * SR), np.float32), seg, np.zeros(int(cola * SR), np.float32)])
        off = ini - (a - 0.03)
        scenes = []
        for i, sc in enumerate(s["scenes"]):
            q = [x for x in idx if sents[x][1] == i]
            scenes.append({"i": i, "start": round(starts[q[0]] + off, 3), "end": round(ends[q[-1]] + off, 3),
                           "sents": [{"start": round(starts[x] + off, 3), "end": round(ends[x] + off, 3), "text": sents[x][2]} for x in q]})
        out = os.path.join(ROOT, "salida", s["id"]); os.makedirs(out, exist_ok=True)
        sf.write(os.path.join(out, "voz_raw.wav"), seg / max(1e-6, np.abs(seg).max()) * 0.92, SR)
        json.dump({"total": round(len(seg) / SR, 3), "scenes": scenes, "motor": "elevenlabs-externo"},
                  open(os.path.join(out, "timing.json"), "w"), indent=1, ensure_ascii=False)
        print(s["id"], f"{len(seg) / SR:.1f} s")


if __name__ == "__main__":
    main()
