# Reel "Hombre de piedra" (Impulso Real): une los 8 clips de Gemini con textos propios (no la letra) y cierre de marca.
# La canción se agrega después desde la biblioteca de música de cada app. Uso: python3 diorama/hombre_piedra.py
import os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D, O = f"{R}/diorama/img/hombre-piedra", f"{R}/salida/2026-11-09-hombre-piedra"
F = f"{R}/engine/fonts"
os.makedirs(O, exist_ok=True)
ESC = [("c1", 1.0, "Un día", "dejé de sentir.", 1.0), ("c2", 1.0, "Ni la lluvia", "me tocaba.", 1.0),
       ("c3", 1.0, "Lo perdí todo…", "y ni así dolía.", 1.0), ("c4", 1.5, "Hasta que alguien", "me tomó la mano.", 1.0),
       ("c5", 1.5, "La piedra", "se hizo arena.", 1.0), ("c6", 1.0, "Volví", "a sentir.", 1.0),
       ("c7", 1.0, "Y ahora canto…", "", 0.5), ("c8", 0.8, "…con el alma.", "", 0.5)]
DUR, XF = 7.4, 0.45

def texto(b, l, path):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fb, fl = ImageFont.truetype(f"{F}/Montserrat-ExtraBold.ttf", 86), ImageFont.truetype(f"{F}/Montserrat-Regular.ttf", 66)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    for dd, font, y, txt in ((d, fb, 1380, b), (d, fl, 1485, l)):
        if txt:
            ds.text((540, y + 4), txt, font=font, fill=(0, 0, 0, 230), anchor="mm")
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    im = Image.alpha_composite(sh, im); d = ImageDraw.Draw(im)
    d.text((540, 1380), b, font=fb, fill="white", anchor="mm")
    if l: d.text((540, 1485), l, font=fl, fill=(255, 233, 176), anchor="mm")
    im.save(path)

def cierre(path):
    im = Image.new("RGB", (1080, 1920), (11, 11, 11)); d = ImageDraw.Draw(im)
    lg = Image.open(f"{R}/engine/assets/impulso_logo.png").convert("RGBA").resize((900, 900)); im.paste(lg, (90, 520), lg)
    fb, fr, fs = (ImageFont.truetype(f"{F}/{n}", s) for n, s in (("Montserrat-ExtraBold.ttf", 74), ("Montserrat-Regular.ttf", 60), ("Montserrat-SemiBold.ttf", 38)))
    d.text((540, 300), "¿Qué te ayudó", font=fb, fill="white", anchor="mm"); d.text((540, 385), "a volver a sentir?", font=fr, fill="white", anchor="mm")
    d.text((540, 1530), "I M P U L S O   R E A L", font=ImageFont.truetype(f"{F}/Montserrat-ExtraBold.ttf", 64), fill="white", anchor="mm")
    d.rounded_rectangle((375, 1568, 705, 1652), radius=42, outline=(255, 107, 61), width=4); d.text((540, 1611), "SEGUIR +", font=fs, fill=(255, 107, 61), anchor="mm")
    im.save(path)

ins, fil, n = [], [], len(ESC)
for k, (c, ss, b, l, vol) in enumerate(ESC):
    texto(b, l, f"{O}/t{k}.png")
    ins += ["-ss", str(ss), "-t", str(DUR), "-i", f"{D}/{c}.mp4", "-loop", "1", "-t", str(DUR), "-i", f"{O}/t{k}.png"]
    fil.append(f"[{2*k}:v]scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p[v{k}b];"
               f"[{2*k+1}:v]format=rgba,fade=in:st=0.7:d=0.5:alpha=1,fade=out:st={DUR-1.0}:d=0.5:alpha=1[t{k}];"
               f"[v{k}b][t{k}]overlay=0:0,format=yuv420p[v{k}];[{2*k}:a]volume={vol},aresample=48000[a{k}]")
cierre(f"{O}/cierre.png"); CD = 4.0
ins += ["-loop", "1", "-t", str(CD), "-i", f"{O}/cierre.png", "-f", "lavfi", "-t", str(CD), "-i", "anullsrc=r=48000:cl=stereo"]
fil.append(f"[{2*n}:v]scale=1080:1920,fps=30,format=yuv420p,zoompan=z='1+0.0006*on':d=1:s=1080x1920:fps=30[v{n}];[{2*n+1}:a]anull[a{n}]")
vl, al, off = "v0", "a0", 0.0
for k in range(1, n + 1):
    off += (DUR if k <= n else CD) - XF if k > 0 else 0
    off = sum(DUR for _ in range(k)) - XF * k
    fil.append(f"[{vl}][v{k}]xfade=transition=fade:duration={XF}:offset={off:.2f}[x{k}];[{al}][a{k}]acrossfade=d={XF}[y{k}]")
    vl, al = f"x{k}", f"y{k}"
fil.append(f"[{al}]loudnorm=I=-18:TP=-2,afade=t=out:st={n*DUR - n*XF + CD - 1.5:.2f}:d=1.5[aout]")
out = f"{O}/2026-11-09-hombre-piedra.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fil), "-map", f"[{vl}]", "-map", "[aout]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
print("listo:", out)
