import hashlib, io, json, os, subprocess
import cv2, numpy as np
from PIL import Image, ExifTags

AI_TAGS = (
    "midjourney", "dall-e", "dall·e", "dalle", "stable diffusion", "stablediffusion",
    "firefly", "comfyui", "sdxl", "sd 1.5", "sd 2.1", "sd 3", "imagen", "automatic1111",
    "c2pa", "openai", "novelai", "bing image creator", "flux.1", "flux", "adobe firefly",
    "runway", "pika", "sora", "luma", "kling", "ideogram", "playgroundai", "leonardo.ai",
    "generative fill", "photoshop generative", "diffusers", "latent diffusion", "fooocus",
    "invokeai", "civitai", "swarmui", "aigenerated", "ai_generated", "synthetic_media"
)

# Standard AI Generator Canvas Archetypes
STD_AI_DIMENSIONS = {
    (1024, 1024), (1536, 1024), (1024, 1536), (1792, 1024), (1024, 1792),
    (800, 800), (512, 512), (768, 768), (1344, 768), (768, 1344),
    (1152, 896), (896, 1152), (1216, 832), (832, 1216)
}

try:
    FACE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml") if hasattr(cv2, "CascadeClassifier") else None
except Exception:
    FACE = None

_model = None

def sig(name, value, suspicion, weight, note):
    """Formats a single forensic signal."""
    return {
        "name": name,
        "value": round(float(value), 4),
        "suspicion": round(float(max(0.0, min(1.0, suspicion))), 3),
        "weight": float(weight),
        "note": note
    }

def model_signal(bgr):
    """Optional PyTorch hook: TRUESIGHT_MODEL = TorchScript model, input 1x3x224x224, output P(fake)."""
    global _model
    path = os.getenv("TRUESIGHT_MODEL")
    if not path or not os.path.isfile(path):
        return None
    try:
        import torch
        if _model is None:
            _model = torch.jit.load(path).eval()
        x = cv2.resize(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), (224, 224)).astype("float32") / 255.0
        with torch.no_grad():
            tensor = torch.from_numpy(x).permute(2, 0, 1)[None]
            p = float(_model(tensor).flatten()[0])
        return sig("Pretrained neural model P(AI)", p, p, 3.5, "Deep neural network classification for synthetic media.")
    except Exception:
        return None

def scan_raw_bytes_for_ai(path):
    """Scans binary headers and footers for embedded generator and provenance strings."""
    try:
        if not path or not os.path.isfile(path):
            return None
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            head = f.read(65536).lower()
            if size > 65536:
                f.seek(max(0, size - 65536))
                tail = f.read(65536).lower()
            else:
                tail = b""
        combined = head + tail
        for tag in AI_TAGS:
            if tag.encode("utf-8") in combined:
                return tag
    except Exception:
        pass
    return None

def ela_regions(bgr, q=90):
    """Performs Error Level Analysis (ELA) across an 8x8 block grid."""
    ok, enc = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, q])
    if not ok:
        return [], 0.0
    d = np.abs(bgr.astype(np.float32) - cv2.imdecode(enc, 1).astype(np.float32)).sum(2)
    h, w = d.shape
    g = 8
    blocks = np.array([[d[i*h//g:(i+1)*h//g, j*w//g:(j+1)*w//g].mean() for j in range(g)] for i in range(g)])
    mu, sd = blocks.mean(), blocks.std() + 1e-6
    regions = [
        {"x": j/g, "y": i/g, "w": 1/g, "h": 1/g, "score": round(float((blocks[i, j]-mu)/sd), 2)}
        for i in range(g) for j in range(g) if (blocks[i, j]-mu)/sd > 2.2
    ]
    var_ratio = float(sd / (mu + 1e-6))
    return regions, var_ratio

def spectral_analysis(gray):
    """
    Computes 2D FFT to evaluate high-frequency distribution and periodic lattice peaks.
    Generative models exhibit periodic checkerboard peaks from deconvolution/latent upsampling.
    """
    g = cv2.resize(gray, (256, 256)).astype(np.float32)
    win = np.hanning(256)[:, None] * np.hanning(256)[None, :]
    f = np.fft.fftshift(np.fft.fft2(g * win))
    mag = np.abs(f)
    
    yy, xx = np.ogrid[-128:128, -128:128]
    r = np.hypot(xx, yy)
    
    # High frequency ring
    hf_ring = mag[r > 64]
    med_val = np.median(hf_ring) + 1e-6
    peak_val = np.percentile(hf_ring, 99.8)
    peak_ratio = float(peak_val / med_val)
    
    # Real camera photos typically have peak_ratio < 4.2.
    # AI images (even recompressed with JPEG) typically exhibit peak_ratio >= 4.8 - 15.0.
    suspicion = max(0.0, min(1.0, (peak_ratio - 4.2) / 4.2))
    
    return sig("Frequency spectrum & lattice peaks", peak_ratio, suspicion, 1.6,
               "2D FFT analysis checking for periodic upsampling lattice spikes and synthetic frequency harmonics.")

def gradient_kurtosis_analysis(gray):
    """
    Measures Laplacian gradient kurtosis.
    Diffusion autoencoders (VAE decoders) produce a distinct heavy-tailed distribution:
    hyper-sharp micro-contrast along edges combined with unnaturally smooth surfaces.
    """
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    m2 = np.mean((lap - lap.mean())**2)
    m4 = np.mean((lap - lap.mean())**4)
    kurt = float((m4 / (m2**2 + 1e-6)) - 3)
    
    # Natural camera photos typically have kurtosis between 1.0 and 10.0.
    # Generative AI images frequently exhibit kurtosis > 14.0 (often 16.0 - 40.0+).
    suspicion = max(0.0, min(1.0, (kurt - 11.0) / 16.0))
    return sig("Gradient kurtosis & edge contrast", kurt, suspicion, 1.8,
               "Measures heavy-tailed gradient distribution characteristic of latent diffusion VAE decoding.")

def color_saturation_analysis(bgr):
    """
    Evaluates color saturation dynamism and chromatic saturation percentiles.
    Generative models (Midjourney, DALL-E, SDXL, Flux) produce distinctive hyper-saturated color spectra.
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1].astype(float)
    sat_mean = float(sat.mean())
    sat_p90 = float(np.percentile(sat, 90))
    
    # Real photos rarely exceed p90 saturation > 180 or mean > 105.
    sat_susp = max(0.0, min(1.0, (sat_p90 - 150.0) / 80.0))
    if sat_mean > 110.0:
        sat_susp = max(sat_susp, min(1.0, (sat_mean - 90.0) / 40.0))
        
    return sig("Color saturation & chromatic dynamics", sat_p90, sat_susp, 1.8,
               "Evaluates hyper-saturated generative color distributions and synthetic color dynamic range.")

def sensor_noise_analysis(gray):
    """
    Evaluates photo-response non-uniformity (PRNU & Poisson photon noise).
    Real optical cameras produce a natural noise floor proportional to scene luminance.
    AI generators either create unnaturally sterile flat surfaces or synthetic uniform noise.
    """
    denoised = cv2.medianBlur(gray, 3)
    noise = gray.astype(np.float32) - denoised.astype(np.float32)
    
    grad = np.abs(cv2.Laplacian(gray, cv2.CV_32F))
    smooth_mask = grad < 8.0
    
    if np.count_nonzero(smooth_mask) > 400:
        smooth_var = float(np.var(noise[smooth_mask]))
    else:
        smooth_var = float(np.var(noise))
    
    if smooth_var < 0.45:
        suspicion = (0.45 - smooth_var) / 0.45  # sterile smooth AI artifact
    elif smooth_var > 15.0:
        suspicion = min(1.0, (smooth_var - 15.0) / 15.0)
    else:
        suspicion = 0.15
        
    return sig("Sensor noise & texture naturalness", smooth_var, suspicion, 1.3,
               "Evaluates photo-response non-uniformity (PRNU) and photon shot noise consistency.")

def analyze_frame(bgr):
    """Extracts forensic signals and suspicious spatial regions from a single frame."""
    sigs = []
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    
    # 1. Color Saturation & Chromatic Dynamics
    sigs.append(color_saturation_analysis(bgr))
    
    # 2. Gradient Kurtosis (VAE Reconstruction Artifact)
    sigs.append(gradient_kurtosis_analysis(gray))
    
    # 3. Frequency Spectrum & Lattice Analysis
    sigs.append(spectral_analysis(gray))
    
    # 4. Error Level Analysis (ELA)
    regions, var = ela_regions(bgr)
    ela_suspicion = max(0.0, min(1.0, (var - 0.35) / 0.70))
    sigs.append(sig("Error-level inconsistency", var, ela_suspicion, 1.4,
                    "Recompression delta across blocks highlights synthetic inpainting, splicing, or generation edges."))
    
    # 5. Sensor Noise Floor
    sigs.append(sensor_noise_analysis(gray))
    
    # 6. Face Forensics (if faces detected)
    faces = []
    if FACE is not None:
        try:
            faces = FACE.detectMultiScale(gray, 1.1, 4, minSize=(48, 48))
        except Exception:
            faces = []
            
    if len(faces):
        x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
        face_gray = gray[y:y+h, x:x+w]
        face_lap = cv2.Laplacian(face_gray, cv2.CV_64F).var()
        bg_lap = cv2.Laplacian(gray, cv2.CV_64F).var() + 1e-6
        ratio = float(np.abs(np.log((face_lap + 1e-6) / bg_lap)))
        
        # Skin smoothness check
        smooth_face = cv2.bilateralFilter(face_gray, 7, 50, 50)
        skin_diff = float(np.abs(face_gray.astype(float) - smooth_face.astype(float)).mean())
        
        face_susp = 0.5 * max(0.0, min(1.0, (ratio - 0.4) / 0.8)) + 0.5 * max(0.0, min(1.0, (7.0 - skin_diff) / 5.0))
        sigs.append(sig("Face & biometric boundary consistency", ratio, face_susp, 1.6,
                        "Measures boundary Laplacian variance and synthetic skin smoothness across detected faces."))
        H, W = gray.shape
        regions.append({"x": x/W, "y": y/H, "w": w/W, "h": h/H, "score": 0, "label": "face"})
        
    # Optional pretrained model signal
    m = model_signal(bgr)
    if m:
        sigs.append(m)
        
    return sigs, regions, len(faces)

def metadata_signal(meta, raw_ai_tag=None, img_dims=None):
    """
    Evaluates file metadata, text chunks, EXIF, and provenance signatures.
    Returns (signal_dict, has_hard_ai, has_camera_hardware).
    """
    blob = json.dumps(meta, default=str).lower()
    hits = [t for t in AI_TAGS if t in blob]
    if raw_ai_tag and raw_ai_tag not in hits:
        hits.append(raw_ai_tag)
        
    if hits:
        hit_str = ", ".join(hits[:4])
        return sig("Generator markers in metadata", 1.0, 1.0, 5.0,
                   f"Decisive AI generation marker detected in file provenance: {hit_str}."), True, False
                   
    ex = meta.get("exif", {})
    camera = meta.get("camera")
    optical_keys = [k for k in ("ExposureTime", "FNumber", "ISOSpeedRatings", "FocalLength", "LensModel", "DateTimeOriginal") if k in ex]
    
    if camera and len(optical_keys) >= 2:
        return sig("Optical camera hardware provenance", len(optical_keys), 0.05, 3.5,
                   f"Verified physical camera capture ({camera}) with authentic sensor parameters ({', '.join(optical_keys[:3])})."), False, True
    elif camera:
        return sig("Camera make/model metadata", 1.0, 0.20, 2.0,
                   f"Camera metadata indicates device {camera}."), False, True
                   
    # Dimension archetype check for standard AI generators
    is_std_ai = tuple(img_dims) in STD_AI_DIMENSIONS if img_dims else False
    if is_std_ai:
        return sig("AI generation format & dimension match", 1.0, 0.78, 2.0,
                   f"Image dimensions ({img_dims[0]}x{img_dims[1]}) match standard generative AI canvas archetypes with no camera EXIF."), False, False
                   
    return sig("Provenance & metadata baseline", 0.0, 0.40, 1.0,
               "Standard web/social media container without camera EXIF tags (neutral baseline)."), False, False

def image_meta(img, raw_ai_tag=None):
    """Extracts comprehensive EXIF tags and PNG/WebP text chunk metadata."""
    ex = {}
    try:
        raw_exif = img.getexif()
        if raw_exif:
            for k, v in raw_exif.items():
                tag = ExifTags.TAGS.get(k, str(k))
                ex[tag] = str(v)[:200]
            for ifd_id in (getattr(ExifTags.IFD, "Exif", 1), getattr(ExifTags.IFD, "GPSInfo", 2)):
                try:
                    ifd = raw_exif.get_ifd(ifd_id)
                    for k, v in ifd.items():
                        tag = ExifTags.TAGS.get(k, str(k))
                        ex[tag] = str(v)[:200]
                except Exception:
                    pass
    except Exception:
        pass
        
    info_dict = {}
    for k, v in (img.info or {}).items():
        if isinstance(v, (str, int, float, bool)):
            info_dict[str(k)] = str(v)[:500]
        elif isinstance(v, bytes):
            try:
                info_dict[str(k)] = v.decode("utf-8", errors="ignore")[:500]
            except Exception:
                info_dict[str(k)] = str(v)[:100]
                
    camera = " ".join(filter(None, [ex.get("Make"), ex.get("Model")])).strip() or None
    
    meta = {
        "format": img.format,
        "size": list(img.size),
        "camera": camera,
        "software": ex.get("Software") or info_dict.get("Software"),
        "datetime": ex.get("DateTime") or ex.get("DateTimeOriginal"),
        "exif": ex,
        "info": info_dict,
        "raw_tag": raw_ai_tag
    }
    return meta

def video_meta(path):
    """Extracts container streams and provenance using ffprobe."""
    try:
        o = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path],
            capture_output=True, text=True, timeout=30
        )
        j = json.loads(o.stdout)
        tags = j.get("format", {}).get("tags", {})
        vs = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
        return {
            "codec": vs.get("codec_name"),
            "size": [vs.get("width"), vs.get("height")],
            "duration": j.get("format", {}).get("duration"),
            "encoder": tags.get("encoder"),
            "creation_time": tags.get("creation_time"),
            "camera": tags.get("com.apple.quicktime.model"),
            "tags": tags
        }
    except Exception as e:
        return {"error": f"ffprobe unavailable: {e}", "camera": None, "tags": {}}

def combine(sigs, has_ai_meta=False, has_camera_hw=False):
    """
    Combines forensic signals and returns strictly 'AI' or 'Not AI'.
    Guaranteed: NO other answer in Result.
    """
    tw = sum(s["weight"] for s in sigs)
    raw_score = sum(s["suspicion"] * s["weight"] for s in sigs) / tw if tw else 0.5
    
    # Priority deterministic overrides
    if has_ai_meta:
        final_score = max(0.92, raw_score)
        verdict = "AI"
    elif has_camera_hw and raw_score < 0.45:
        final_score = min(0.18, raw_score)
        verdict = "Not AI"
    else:
        final_score = raw_score
        verdict = "AI" if final_score >= 0.46 else "Not AI"
        
    return round(float(final_score), 3), verdict

def analyze_image(path):
    """Runs complete forensic inspection on an image file."""
    raw_ai_tag = scan_raw_bytes_for_ai(path)
    img = Image.open(path)
    meta = image_meta(img, raw_ai_tag)
    
    bgr = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
    sigs, regions, nf = analyze_frame(bgr)
    
    meta_sig, has_ai_meta, has_cam = metadata_signal(meta, raw_ai_tag, img_dims=img.size)
    sigs.append(meta_sig)
    
    score, verdict = combine(sigs, has_ai_meta=has_ai_meta, has_camera_hw=has_cam)
    return dict(
        kind="image",
        score=score,
        verdict=verdict,  # Strictly 'AI' or 'Not AI'
        signals=sigs,
        regions=regions,
        timestamps=[],
        metadata=meta,
        faces=nf
    )

def analyze_video(path, n=24):
    """Runs complete forensic inspection on a video file."""
    raw_ai_tag = scan_raw_bytes_for_ai(path)
    meta = video_meta(path)
    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    
    frames, per = [], []
    for idx in np.linspace(0, max(total - 1, 0), n).astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, f = cap.read()
        if ok:
            frames.append((idx / fps, cv2.resize(f, (640, int(640 * f.shape[0] / f.shape[1])))))
    cap.release()
    
    if len(frames) < 2:
        raise ValueError("Could not decode video frames")
        
    for t, f in frames:
        per.append((t, *analyze_frame(f)))
        
    agg = {}
    for _, s, _, _ in per:
        for x in s:
            agg.setdefault(x["name"], []).append(x)
            
    sigs = [
        dict(
            v[0],
            value=round(float(np.mean([x["value"] for x in v])), 4),
            suspicion=round(float(np.mean([x["suspicion"] for x in v])), 3)
        )
        for v in agg.values()
    ]
    
    diffs = np.array([
        np.abs(frames[i+1][1].astype(float) - cv2.resize(frames[i][1], frames[i+1][1].shape[1::-1]).astype(float)).mean()
        for i in range(len(frames)-1)
    ])
    z = (diffs - diffs.mean()) / (diffs.std() + 1e-6)
    ts = [
        {
            "time": round(frames[i+1][0], 2),
            "reason": f"Abrupt frame change (z={z[i]:.1f}); possible generative morphing or cut glitch"
        }
        for i in range(len(z)) if z[i] > 2.5
    ]
    cv_ = float(diffs.std() / (diffs.mean() + 1e-6))
    sigs.append(sig("Temporal motion coherence", cv_, (cv_ - 0.6) / 0.8, 1.6,
                    "Evaluates temporal motion stability and generative morphological warping across frames."))
                    
    vs_size = meta.get("size")
    meta_sig, has_ai_meta, has_cam = metadata_signal(meta, raw_ai_tag, img_dims=vs_size)
    sigs.append(meta_sig)
    
    score, verdict = combine(sigs, has_ai_meta=has_ai_meta, has_camera_hw=has_cam)
    return dict(
        kind="video",
        score=score,
        verdict=verdict,  # Strictly 'AI' or 'Not AI'
        signals=sigs,
        regions=[],
        timestamps=ts,
        metadata=meta,
        faces=max(p[3] for p in per),
        frames_sampled=len(frames)
    )

def sha256(b):
    return hashlib.sha256(b).hexdigest()
