# TrueSight AI 🛡️

**Forensic-Grade Deepfake & AI Manipulation Detection Engine**

TrueSight AI combines multi-spectral heuristics (Error Level Analysis, 2D FFT spectral anomaly analysis, facial boundary sharpness variance, frame-to-frame temporal delta) with digital provenance metadata parsing (EXIF/C2PA) and optional deep neural network inference to classify and explain synthetic media.

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+
- [FFmpeg](https://ffmpeg.org/) (required for video forensics)

### 1. Run Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API runs at: `http://localhost:8000` (Docs at `http://localhost:8000/docs`)

### 2. Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Client runs at: `http://localhost:5173` (Vite dev server proxies `/api` requests to backend at `http://localhost:8000`).

---

## 🐳 Docker Deployment (Single Container)

TrueSight AI includes a multi-stage production Dockerfile that compiles the React frontend and serves both API and UI via FastAPI on a single port.

### Build and Run Locally:
```bash
docker build -t truesight-ai .
docker run -p 8000:8000 truesight-ai
```
Visit `http://localhost:8000`.

---

## ☁️ Cloud Deployment Options

### Option 1: Render (Recommended - Free Web Service)
1. Fork or push this repository to GitHub: `https://github.com/Rishikvelagapudi/TrueSight-AI`
2. Log in to [Render](https://render.com/) and click **New > Web Service**.
3. Connect your GitHub repository.
4. Select **Docker** as the runtime (Render will automatically pick up `Dockerfile` or `render.yaml`).
5. Choose the **Free** instance type and click **Create Web Service**.
6. Render builds and hosts the complete full-stack application!

### Option 2: Hugging Face Spaces (Free Docker Space)
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Name your space (e.g. `truesight-ai`) and choose **Docker** as the SDK (Blank).
3. Push or mirror this repository to your Hugging Face Space repository.
4. Hugging Face builds the Docker container and serves your application with free GPU/CPU!

### Option 3: Railway
1. Go to [Railway](https://railway.app/).
2. Click **New Project** > **Deploy from GitHub repo**.
3. Select `TrueSight-AI`. Railway detects `Dockerfile` and deploys automatically.

### Option 4: Split Deployment (Frontend on Vercel + Backend on Render/Railway)
- **Backend**: Deploy the `backend/` folder to Render or Railway. You will get a backend URL, e.g. `https://truesight-backend.onrender.com`.
- **Frontend**: Deploy to [Vercel](https://vercel.com/):
  - Connect GitHub repo.
  - Set Root Directory to `frontend` (or let `vercel.json` handle root).
  - Add Environment Variable:
    - `VITE_API_URL` = `https://truesight-backend.onrender.com`
  - Deploy!

---

## 🔬 Forensic Detection Pipeline

TrueSight AI applies a multi-layered verification strategy:

1. **Error Level Analysis (ELA)**: Recompresses images at fixed quality levels to identify compression error discrepancies across 8x8 spatial grid blocks.
2. **2D FFT Frequency Analysis**: Computes radial high-frequency spectral ratios to identify synthetic generative artifacts.
3. **Facial Boundary & Sharpness Analysis**: Isolates detected faces using Haar cascades and evaluates Laplacian variances against background noise levels to catch face-swap boundaries.
4. **Temporal Consistency Delta (Video)**: Analyzes frame-to-frame pixel variances across sampled frames to detect synthetic generation glitches and splice anomalies.
5. **Metadata & Provenance Inspection**: Parses EXIF tags, encoder markers, and known AI generator fingerprints (Midjourney, DALL-E, Stable Diffusion, C2PA, etc.).
6. **Optional Deep Neural Model**: Set `TRUESIGHT_MODEL=/path/to/model.pt` (TorchScript, input `1x3x224x224`, output probability `P(fake)`).
7. **Forensic PDF Export**: Generates tamper-evident cryptographic reports with SHA-256 hashes, confidence scores, and legal guidance.

---

## 📄 License
MIT License.
