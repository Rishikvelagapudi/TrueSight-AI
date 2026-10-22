import os, tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
import analysis, report

app = FastAPI(title="TrueSight AI")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
IMG, VID, MAX = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}, {".mp4", ".mov", ".avi", ".mkv", ".webm"}, 100 * 1024 * 1024

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "TrueSight AI"}

@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in IMG | VID: raise HTTPException(415, "Unsupported file type")
    data = await file.read()
    if len(data) > MAX: raise HTTPException(413, "File exceeds 100 MB")
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f: f.write(data); p = f.name
    try:
        r = analysis.analyze_image(p) if ext in IMG else analysis.analyze_video(p)
    except Exception as e:
        raise HTTPException(422, f"Could not analyze file: {e}")
    finally: os.unlink(p)
    r["file"] = {"name": file.filename, "size": len(data), "sha256": analysis.sha256(data), "type": file.content_type}
    r.update(
        explanation=report.explain(r),
        next_steps=report.next_steps(r["verdict"]),
        guidance=report.GUIDANCE,
        limitations=report.LIMITS,
        ai_determination=report.determination(r["verdict"]),
        final_note=report.final_note(r["verdict"], r["score"])
    )
    return r

@app.post("/api/report/pdf")
async def pdf(r: dict):
    return Response(report.build_pdf(r), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=truesight-report.pdf"})

# Mount and serve built frontend in unified deployment mode if present
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    comics_dir = os.path.join(FRONTEND_DIST, "comics")
    if os.path.exists(comics_dir):
        app.mount("/comics", StaticFiles(directory=comics_dir), name="comics")

    @app.get("/")
    async def root():
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"status": "ok", "message": "TrueSight AI API running"}

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(404, "API route not found")
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        raise HTTPException(404, "Resource not found")
else:
    @app.get("/")
    async def root():
        return {"status": "ok", "message": "TrueSight AI API running", "docs": "/docs"}

