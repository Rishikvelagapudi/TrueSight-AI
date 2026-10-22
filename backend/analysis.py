import hashlib, io, json, os, subprocess
import cv2, numpy as np
from PIL import Image, ExifTags

AI_TAGS = ("midjourney", "dall-e", "dall·e", "stable diffusion", "firefly", "comfyui", "sdxl", "imagen", "automatic1111", "c2pa", "openai")
FACE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_model = None

def sig(name, value, suspicion, weight, note):
    return {"name": name, "value": round(float(value), 4), "suspicion": round(float(max(0, min(1, suspicion))), 3), "weight": weight, "note": note}

def model_signal(bgr):
    """Optional PyTorch hook: TRUESIGHT_MODEL = TorchScript model, input 1x3x224x224, output P(fake)."""
    global _model
    path = os.getenv("TRUESIGHT_MODEL")
    if not path:
        return None
    import torch
    if _model is None:
        _model = torch.jit.load(path).eval()
    x = cv2.resize(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), (224, 224)).astype("float32") / 255
    with torch.no_grad():
        p = float(_model(torch.from_numpy(x).permute(2, 0, 1)[None]).flatten()[0])
    return sig("Pretrained model P(fake)", p, p, 3.0, "Pretrained model output; accuracy drops on unfamiliar generators and compressed media.")

def ela_regions(bgr, q=90):
    ok, enc = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, q])
    d = np.abs(bgr.astype(np.float32) - cv2.imdecode(enc, 1).astype(np.float32)).sum(2)
    h, w = d.shape; g = 8
    blocks = np.array([[d[i*h//g:(i+1)*h//g, j*w//g:(j+1)*w//g].mean() for j in range(g)] for i in range(g)])
    mu, sd = blocks.mean(), blocks.std() + 1e-6
    regions = [{"x": j/g, "y": i/g, "w": 1/g, "h": 1/g, "score": round(float((blocks[i, j]-mu)/sd), 2)}
               for i in range(g) for j in range(g) if (blocks[i, j]-mu)/sd > 2.2]
    return regions, float(sd / (mu + 1e-6))

def spectral_ratio(gray):
    f = np.abs(np.fft.fftshift(np.fft.fft2(cv2.resize(gray, (256, 256)).astype(np.float32))))
    yy, xx = np.ogrid[-128:128, -128:128]; r = np.hypot(xx, yy)
    return float(f[r > 64].sum() / (f.sum() + 1e-6))

def analyze_frame(bgr):
    sigs = []
    regions, var = ela_regions(bgr)
    sigs.append(sig("Error-level inconsistency", var, (var - 0.35) / 0.8, 1.5, "Uneven recompression error across blocks can indicate splicing or local edits."))
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    hf = spectral_ratio(gray)
    sigs.append(sig("High-frequency spectrum ratio", hf, abs(hf - 0.045) / 0.04 - 0.5, 1.0, "Generated images often show atypical frequency energy (weak signal, content dependent)."))
    faces = FACE.detectMultiScale(gray, 1.1, 5, minSize=(48, 48))
    if len(faces):
        x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
        face_s = cv2.Laplacian(gray[y:y+h, x:x+w], cv2.CV_64F).var()
        bg_s = cv2.Laplacian(gray, cv2.CV_64F).var() + 1e-6
        ratio = float(np.log((face_s + 1e-6) / bg_s))
        sigs.append(sig("Face/background sharpness mismatch", ratio, (abs(ratio) - 1.0) / 1.5, 1.5, "Face swaps often differ in sharpness/noise from the surrounding frame."))
        H, W = gray.shape
        regions.append({"x": x/W, "y": y/H, "w": w/W, "h": h/H, "score": 0, "label": "face"})
    m = model_signal(bgr)
    if m: sigs.append(m)
    return sigs, regions, len(faces)

def metadata_signal(meta):
    blob = json.dumps(meta).lower()
    hit = [t for t in AI_TAGS if t in blob]
    if hit:
        return sig("Generator markers in metadata", 1, 0.95, 3.0, f"Metadata mentions: {', '.join(hit)}. Metadata can be forged or stripped.")
    if not meta.get("camera"):
        return sig("No camera metadata", 0, 0.5, 0.5, "Missing EXIF is common after social-media re-encoding; weak, not evidence of fakery.")
    return sig("Camera metadata present", 1, 0.1, 1.0, "Camera make/model present. Metadata can be forged.")

def image_meta(img):
    ex = {ExifTags.TAGS.get(k, str(k)): str(v)[:100] for k, v in (img.getexif() or {}).items()}
    return {"format": img.format, "size": list(img.size), "camera": " ".join(filter(None, [ex.get("Make"), ex.get("Model")])) or None,
            "software": ex.get("Software"), "datetime": ex.get("DateTime"), "exif": ex, "info_keys": list(img.info.keys())[:15]}

def video_meta(path):
    try:
        o = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path], capture_output=True, text=True, timeout=30)
        j = json.loads(o.stdout); tags = j.get("format", {}).get("tags", {})
        vs = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
        return {"codec": vs.get("codec_name"), "size": [vs.get("width"), vs.get("height")], "duration": j["format"].get("duration"),
                "encoder": tags.get("encoder"), "creation_time": tags.get("creation_time"), "camera": tags.get("com.apple.quicktime.model"), "tags": tags}
    except Exception as e:
        return {"error": f"ffprobe unavailable: {e}", "camera": None}

def combine(sigs):
    tw = sum(s["weight"] for s in sigs)
    score = sum(s["suspicion"] * s["weight"] for s in sigs) / tw if tw else 0.5
    verdict = "Likely Authentic" if score < 0.35 else "Likely AI-Generated or Manipulated" if score > 0.62 else "Inconclusive"
    return round(score, 3), verdict

def analyze_image(path):
    img = Image.open(path); meta = image_meta(img)
    bgr = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
    sigs, regions, nf = analyze_frame(bgr)
    sigs.append(metadata_signal(meta))
    score, verdict = combine(sigs)
    return dict(kind="image", score=score, verdict=verdict, signals=sigs, regions=regions, timestamps=[], metadata=meta, faces=nf)

def analyze_video(path, n=24):
    meta = video_meta(path); cap = cv2.VideoCapture(path)
    total, fps = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), cap.get(cv2.CAP_PROP_FPS) or 25
    frames, per = [], []
    for idx in np.linspace(0, max(total - 1, 0), n).astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx)); ok, f = cap.read()
        if ok: frames.append((idx / fps, cv2.resize(f, (640, int(640 * f.shape[0] / f.shape[1])))))
    cap.release()
    if len(frames) < 2: raise ValueError("Could not decode video frames")
    for t, f in frames: per.append((t, *analyze_frame(f)))
    agg = {}
    for _, s, _, _ in per:
        for x in s: agg.setdefault(x["name"], []).append(x)
    sigs = [dict(v[0], value=round(float(np.mean([x["value"] for x in v])), 4), suspicion=round(float(np.mean([x["suspicion"] for x in v])), 3)) for v in agg.values()]
    diffs = np.array([np.abs(frames[i+1][1].astype(float) - cv2.resize(frames[i][1], frames[i+1][1].shape[1::-1]).astype(float)).mean() for i in range(len(frames)-1)])
    z = (diffs - diffs.mean()) / (diffs.std() + 1e-6)
    ts = [{"time": round(frames[i+1][0], 2), "reason": f"Abrupt frame change (z={z[i]:.1f}); possible splice or generation glitch"} for i in range(len(z)) if z[i] > 2.5]
    cv_ = float(diffs.std() / (diffs.mean() + 1e-6))
    sigs.append(sig("Frame-to-frame inconsistency", cv_, (cv_ - 0.6) / 0.8, 1.5, "Irregular temporal change can reflect cuts, splices or unstable synthetic frames (cuts are also normal editing)."))
    sigs.append(metadata_signal(meta))
    score, verdict = combine(sigs)
    return dict(kind="video", score=score, verdict=verdict, signals=sigs, regions=[], timestamps=ts, metadata=meta, faces=max(p[3] for p in per), frames_sampled=len(frames))

def sha256(b): return hashlib.sha256(b).hexdigest()
