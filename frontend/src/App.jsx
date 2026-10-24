import { useState, useRef, useEffect } from "react";

const COLORS = {
  "AI": { bg: "#b91c1c", light: "#fee2e2", border: "#ef4444", text: "#991b1b", label: "AI" },
  "Not AI": { bg: "#0d6832", light: "#e8f7ee", border: "#22c55e", text: "#0d6832", label: "Not AI" }
};

const SCAN_STEPS = [
  "Extracting spatial RGB & chroma planes...",
  "Running Error Level Analysis (ELA) recompression delta...",
  "Computing 2D Fast Fourier Transform (FFT) high-frequency spectrum...",
  "Evaluating facial boundary sharpness & Laplacian variance...",
  "Scanning file headers & provenance EXIF / C2PA tags...",
  "Synthesizing forensic indicators into final determination..."
];

const API_BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

const COMICS = [
  {
    id: 1,
    caseNum: "CASE #01",
    title: "THE $5M CEO CALL SCAM",
    subtitle: "Halting executive deepfake scams before irreversible $5,000,000 wire transfers!",
    category: "Financial & Family Protection",
    badge: "⚡ $5M Saved",
    badgeColor: "#0d6832",
    img: "/comics/comic1.png",
    caption: "Accountant spots real-time facial swap anomalies during an urgent executive call, aborting a fraudulent $5,000,000 wire transfer.",
    signals: "Facial boundary Laplacian variance & compression re-encoding delta flagged in 62ms.",
    quote: '"ALERT: FACIAL SWAP DETECTED! $5M SAVED!"',
    points: [
      {
        tag: "Warning Sign",
        title: "Unnatural Facial Artifacts",
        desc: "Watch for glitching jawlines, flickering teeth, or missing natural micro-blinking during urgent high-stakes video calls."
      },
      {
        tag: "Prevention Step",
        title: "Two-Channel Callback Rule",
        desc: "Never authorize transfers or panic payments over the same call. Disconnect and call the executive back on their verified direct mobile number."
      },
      {
        tag: "AI Inspection",
        title: "Real-Time Mesh Analysis",
        desc: "TrueSight scans frame-by-frame Laplacian sharpness differences between the face box and background environment in 62ms."
      },
      {
        tag: "Civic Awareness",
        title: "Report to Cyber Fraud Helpline 1930",
        desc: "Report digital imposter scams immediately to National Cyber Crime portal (1930 / cybercrime.gov.in) to freeze fraudulent bank accounts."
      }
    ]
  },
  {
    id: 2,
    caseNum: "CASE #02",
    title: "VIRAL ELECTION FACT-CHECK",
    subtitle: "Stopping synthetic political speech clones before they mislead millions of citizens!",
    category: "Civic & Media Truth",
    badge: "⚡ Disinformation Halted",
    badgeColor: "#b91c1c",
    img: "/comics/comic2.png",
    caption: "Newsroom investigative team halts a sensational trending video before live national broadcast after detecting synthetic audio-visual desync.",
    signals: "2D Fast Fourier Transform (FFT) spectrum & acoustic lip-sync biometric mismatch detected.",
    quote: '"STOP THE FEED! IT\'S AN AI CLONE!"',
    points: [
      {
        tag: "Warning Sign",
        title: "Robotic Lip-Audio Desync",
        desc: "Words don't perfectly synchronize with mouth muscle contractions; sensational claims engineered to trigger immediate anger or panic."
      },
      {
        tag: "Prevention Step",
        title: "Pause Before Sharing",
        desc: "Resist forwarding shocking WhatsApp clips. Verify whether recognized primary news desks have corroborated with live broadcast cameras."
      },
      {
        tag: "AI Inspection",
        title: "2D Spectral Frequency Check",
        desc: "TrueSight computes FFT high-frequency energy distribution which synthetic AI generators leave as abnormal residual artifacts."
      },
      {
        tag: "Civic Awareness",
        title: "Democratic Integrity Laws",
        desc: "Knowingly circulating malicious synthetic videos intended to disrupt public order violates IT Act and Election Commission rules."
      }
    ]
  },
  {
    id: 3,
    caseNum: "CASE #03",
    title: "DEFAMATION & EXTORTION SHIELD",
    subtitle: "Protecting personal dignity & vindicating victims with certified forensic proof!",
    category: "Youth & Personal Dignity",
    badge: "⚡ 100% Exoneration",
    badgeColor: "#000080",
    img: "/comics/comic3.png",
    caption: "A targeted student is fully vindicated after TrueSight produces a certified forensic report proving a blackmail image was completely fabricated.",
    signals: "Error Level Analysis (ELA) blocks expose synthetic generative inpainting and cloned borders.",
    quote: '"THE TRUESIGHT REPORT PROVED IT WAS ALL AI! I\'M VINDICATED!"',
    points: [
      {
        tag: "Warning Sign",
        title: "Inconsistent Pixel Compression",
        desc: "Manipulated photos often have weirdly smooth skin texture while the background remains noisy or pixelated from previous compression."
      },
      {
        tag: "Prevention Step",
        title: "Preserve Original Evidence",
        desc: "Do not delete or re-screenshot the threat. Keep the original file with its cryptographic SHA-256 hash intact for law enforcement."
      },
      {
        tag: "AI Inspection",
        title: "Error Level Analysis (ELA)",
        desc: "TrueSight performs differential re-compression to highlight pixel blocks that were modified after the original camera capture."
      },
      {
        tag: "Civic Awareness",
        title: "Legal Right to Takedown",
        desc: "Under digital privacy laws, social media intermediaries are legally mandated to remove non-consensual deepfakes within 24 hours of reporting."
      }
    ]
  },
  {
    id: 4,
    caseNum: "CASE #04",
    title: "COURTROOM CCTV PROVENANCE",
    subtitle: "Exposing manipulated surveillance videos before innocent citizens are judged!",
    category: "Judicial & Legal Integrity",
    badge: "⚡ Evidence Dismissed",
    badgeColor: "#b45309",
    img: "/comics/comic4.png",
    caption: "Defense lawyer presents certified TrueSight forensic telemetry to the judge, exposing fabricated CCTV surveillance video as an AI forgery.",
    signals: "Temporal frame-rate inconsistency & missing camera sensor noise profile.",
    quote: '"YOUR HONOR! TRUESIGHT FORENSICS PROVES THIS CCTV IS 100% SYNTHETIC!"',
    points: [
      {
        tag: "Warning Sign",
        title: "Missing Hardware Sensor EXIF",
        desc: "Genuine cameras embed distinct sensor metadata and codec profiles; AI videos often lack device tags or show generator signatures."
      },
      {
        tag: "Prevention Step",
        title: "Chain of Custody Verification",
        desc: "Legal and regulatory bodies require complete provenance trails and cryptographic validation before admitting digital evidence."
      },
      {
        tag: "AI Inspection",
        title: "Provenance & Stream Audit",
        desc: "TrueSight inspects format streams, creation time, encoder markers, and C2PA content provenance manifests."
      },
      {
        tag: "Civic Awareness",
        title: "Strict Perjury Consequences",
        desc: "Submitting AI-generated media as genuine legal evidence constitutes criminal forgery and punishable perjury under judicial law."
      }
    ]
  },
  {
    id: 5,
    caseNum: "CASE #05",
    title: "SOCIAL PLATFORM SENTINEL",
    subtitle: "Intercepting 50,000 synthetic bot accounts at platform gates in real time!",
    category: "Community & Cyber Safety",
    badge: "⚡ 50,000 Bots Blocked",
    badgeColor: "#000080",
    img: "/comics/comic5.png",
    caption: "Trust & Safety command center intercepts a coordinated bot swarm uploading synthetic deepfakes before reaching public feeds.",
    signals: "Real-time API line-speed pipeline scanning at 45ms per media item.",
    quote: '"BOT SWARM INTERCEPTED BEFORE GOING VIRAL! PLATFORM SECURED!"',
    points: [
      {
        tag: "Warning Sign",
        title: "Mass Coordinated Bot Uploads",
        desc: "Thousands of new accounts simultaneously posting near-identical synthetic reels and clips with repetitive artificial voices."
      },
      {
        tag: "Prevention Step",
        title: "Platform Reporting Cues",
        desc: "Always use in-app 'Manipulated / Synthetic Media' reporting tags when encountering suspicious content on social platforms."
      },
      {
        tag: "AI Inspection",
        title: "High-Throughput Line Scan",
        desc: "TrueSight's modular architecture enables real-time media screening to filter deepfakes at network ingest boundaries in 45ms."
      },
      {
        tag: "Civic Awareness",
        title: "Public Literacy & Vigilance",
        desc: "Awareness of bot farms empowers communities to question sensational viral trends and demand transparent AI labeling."
      }
    ]
  },
  {
    id: 6,
    caseNum: "CASE #06",
    title: "BIOMETRIC KYC BANK SHIELD",
    subtitle: "Neutralizing 3D synthetic masks & virtual camera injections on mobile banking!",
    category: "Identity & Financial Security",
    badge: "⚡ Account Protected",
    badgeColor: "#0d6832",
    img: "/comics/comic6.png",
    caption: "Cybercriminal attempts virtual camera injection with a 3D digital avatar mask to bypass mobile banking KYC authentication.",
    signals: "Micro-texture depth analysis & volumetric 3D liveness scan fail.",
    quote: '"CURSES! TRUESIGHT AI SAW RIGHT THROUGH THE SYNTHETIC MASK!"',
    points: [
      {
        tag: "Warning Sign",
        title: "Virtual Camera Injections",
        desc: "Feed freezes, unnatural lighting reflections on eyeballs, and absence of natural 3D parallax when the head turns."
      },
      {
        tag: "Prevention Step",
        title: "Multi-Factor Authentication",
        desc: "Never rely on facial biometric alone. Always pair biometric logins with hardware tokens, SMS/authenticator OTPs, and password keys."
      },
      {
        tag: "AI Inspection",
        title: "3D Liveness & Micro-Texture",
        desc: "TrueSight detects synthetic injection feeds by evaluating micro-skin texture variance and real human blood volume pulse cues."
      },
      {
        tag: "Civic Awareness",
        title: "Protect Personal Documents",
        desc: "Never share clear full-face video clips or selfies with unverified apps claiming to offer instant cash loans or crypto gifts."
      }
    ]
  }
];

function AshokaChakra({ size = 44, spinning = false, className = "" }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`ashoka-chakra ${spinning ? "fast-spin" : "gentle-spin"} ${className}`}
      aria-label="Ashoka Chakra"
    >
      <circle cx="24" cy="24" r="22" stroke="#000080" strokeWidth="2.5" />
      <circle cx="24" cy="24" r="19.5" stroke="#000080" strokeWidth="0.8" />
      <circle cx="24" cy="24" r="5" fill="#000080" />
      <circle cx="24" cy="24" r="2.2" fill="#ffffff" />
      {Array.from({ length: 24 }).map((_, i) => (
        <line
          key={i}
          x1="24"
          y1="24"
          x2="24"
          y2="4.5"
          stroke="#000080"
          strokeWidth="1.2"
          strokeLinecap="round"
          transform={`rotate(${i * 15} 24 24)`}
        />
      ))}
    </svg>
  );
}

function NationalMovingBorder() {
  return (
    <div className="national-border-frame" aria-hidden="true">
      {/* 4 Moving Border Strips with Repeating Ashoka Chakra & Lotus Rosettes */}
      <div className="national-border-strip strip-top" />
      <div className="national-border-strip strip-right" />
      <div className="national-border-strip strip-bottom" />
      <div className="national-border-strip strip-left" />

      {/* Moving Electric Navy Energy Beams */}
      <div className="border-beam beam-top" />
      <div className="border-beam beam-right" />
      <div className="border-beam beam-bottom" />
      <div className="border-beam beam-left" />

      {/* 4 Ornate Ashoka Chakra Corner Medallions */}
      <div className="corner-medallion corner-tl">
        <AshokaChakra size={26} />
      </div>
      <div className="corner-medallion corner-tr">
        <AshokaChakra size={26} />
      </div>
      <div className="corner-medallion corner-br">
        <AshokaChakra size={26} />
      </div>
      <div className="corner-medallion corner-bl">
        <AshokaChakra size={26} />
      </div>
    </div>
  );
}

function SuspicionGauge({ score, verdict }) {
  const percent = Math.round(score * 100);
  const radius = 52;
  const stroke = 8;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score * circumference);
  const isAi = verdict ? verdict === "AI" : score >= 0.50;
  const color = isAi ? "#b91c1c" : "#0d6832";

  return (
    <div className="gauge-container">
      <svg width="130" height="130" viewBox="0 0 130 130" className="gauge-svg">
        <circle cx="65" cy="65" r={radius} stroke="#e2ecf8" strokeWidth={stroke} fill="none" />
        <circle
          cx="65"
          cy="65"
          r={radius}
          stroke={color}
          strokeWidth={stroke}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="gauge-circle-anim"
          transform="rotate(-90 65 65)"
        />
      </svg>
      <div className="gauge-content">
        <span className="gauge-number" style={{ color }}>{percent}%</span>
        <span className="gauge-label">{isAi ? "AI Suspicion" : "Authenticity"}</span>
      </div>
    </div>
  );
}

function ComicCard({ comic, isExpanded, onTogglePoints, onSelect }) {
  return (
    <div className={`comic-sticker-unit ${isExpanded ? "open-drawer" : ""}`}>
      {/* Upper Main Comic Card (Sticker Frame) */}
      <div className="comic-sticker-card">
        {/* Comic Art Box */}
        <div className="comic-art-frame" onClick={onSelect} title="Click to zoom illustration">
          <img src={comic.img} alt={comic.title} loading="lazy" />
          <div className="comic-art-gradient-overlay" />

          {/* Circular Chevron Toggle Button (Top-Right) */}
          <button
            className={`comic-circle-btn ${isExpanded ? "expanded" : ""}`}
            onClick={(e) => {
              e.stopPropagation();
              onTogglePoints(comic.id);
            }}
            aria-label={isExpanded ? "Collapse Points" : "Expand Points"}
            title={isExpanded ? "Hide Awareness Points" : "Reveal Awareness Points"}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#000c24" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points={isExpanded ? "6 9 12 15 18 9" : "9 18 15 12 9 6"} />
            </svg>
          </button>
        </div>

        {/* Overlapping White Caption Box */}
        <div className="comic-caption-box">
          {/* Floating Pink Lightning Badge */}
          <div
            className="comic-lightning-badge"
            onClick={(e) => {
              e.stopPropagation();
              onTogglePoints(comic.id);
            }}
            title="Real-Time Protection Alert - Click to toggle points"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="#ffffff">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
            </svg>
          </div>

          <h3 className="comic-caption-title" onClick={onSelect}>
            {comic.title}
          </h3>
          <p className="comic-caption-subtitle">{comic.subtitle}</p>

          {/* Interactive Button to reveal points */}
          <button
            className={`comic-pill-action-btn ${isExpanded ? "active" : ""}`}
            onClick={(e) => {
              e.stopPropagation();
              onTogglePoints(comic.id);
            }}
          >
            <span>{isExpanded ? "Hide Defense Points" : "View Defense Points"}</span>
            <span className="pill-btn-chevron">{isExpanded ? "▲" : "▼"}</span>
          </button>
        </div>
      </div>

      {/* Connected Expandable Points Drawer (Matching Reference Image 2) */}
      {isExpanded && (
        <div className="comic-connected-drawer animate-pop-in">
          {/* Triangle speech pointer pointing up to the card */}
          <div className="drawer-triangle-arrow" />

          {/* Black/Navy Pill Header */}
          <div className="drawer-header-pill">
            <span className="pill-star-icon">✨</span>
            <span className="pill-header-text">REAL-TIME CITIZEN DEFENSE & AWARENESS</span>
          </div>

          {/* Points List Cards */}
          <div className="drawer-cards-stack">
            {comic.points.map((pt, pIdx) => (
              <div key={pIdx} className="drawer-point-box">
                <div className="point-box-check-badge">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="3.6" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </div>
                <div className="point-box-text-wrap">
                  <h4 className="point-box-title">✦ {pt.title.toUpperCase()}</h4>
                  <p className="point-box-desc">{pt.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ComicModal({ comic, onClose }) {
  if (!comic) return null;
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onClose} aria-label="Close">✕</button>
        <div className="modal-header">
          <div>
            <span className="modal-case">{comic.caseNum} • {comic.category}</span>
            <h2>{comic.title}</h2>
          </div>
          <span className="modal-badge" style={{ backgroundColor: comic.badgeColor }}>{comic.badge}</span>
        </div>
        <div className="modal-body">
          <div className="modal-img-wrapper">
            <img src={comic.img} alt={comic.title} />
            <div className="modal-quote">{comic.quote}</div>
          </div>

          <div className="modal-content">
            <div className="modal-story">
              <h3>Real-Time Defense Scenario:</h3>
              <p>{comic.caption}</p>
            </div>

            <div className="modal-signals-box">
              <strong>🔬 Forensic Interception Mechanism:</strong>
              <p>{comic.signals}</p>
            </div>

            {/* Social Awareness Points Section in Modal */}
            <div className="modal-points-section">
              <div className="modal-points-title">
                <AshokaChakra size={22} />
                <h3>Public Awareness & Safety Defense Points</h3>
              </div>

              <div className="modal-points-grid">
                {comic.points.map((pt, idx) => (
                  <div key={idx} className="modal-point-item">
                    <div className="modal-point-tag-row">
                      <span className="modal-point-icon">✦</span>
                      <span className="modal-point-tag">{pt.tag}</span>
                    </div>
                    <h4>{pt.title}</h4>
                    <p>{pt.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="modal-seal">
              <AshokaChakra size={36} />
              <div>
                <strong>TrueSight AI Sentinel Defense Grid</strong>
                <span>Verified Real-Time Operation & Social Awareness Simulation</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [file, setFile] = useState(null), [preview, setPreview] = useState(null);
  const [res, setRes] = useState(null), [busy, setBusy] = useState(false), [err, setErr] = useState("");
  const [stepIdx, setStepIdx] = useState(0);
  const [copied, setCopied] = useState(false);
  const [activeModal, setActiveModal] = useState(null);
  const [expandedPoints, setExpandedPoints] = useState({ 1: true }); // Case 1 open by default so user sees it right away!
  const input = useRef();

  useEffect(() => {
    let timer;
    if (busy) {
      setStepIdx(0);
      timer = setInterval(() => {
        setStepIdx((prev) => (prev + 1) % SCAN_STEPS.length);
      }, 700);
    }
    return () => clearInterval(timer);
  }, [busy]);

  const togglePoints = (id) => {
    setExpandedPoints((prev) => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const pick = (f) => {
    if (!f) return;
    setFile(f);
    setRes(null);
    setErr("");
    setPreview(URL.createObjectURL(f));
  };

  const run = async () => {
    if (!file) return;
    setBusy(true);
    setErr("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await fetch(`${API_BASE}/api/analyze`, { method: "POST", body: fd });
      if (!r.ok) throw new Error((await r.json()).detail || "Analysis failed");
      setRes(await r.json());
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  const pdf = async () => {
    const r = await fetch(`${API_BASE}/api/report/pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(res)
    });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(await r.blob());
    a.download = "truesight-report.pdf";
    a.click();
  };

  const copyHash = (hash) => {
    navigator.clipboard?.writeText(hash);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isVideo = file?.type.startsWith("video");
  const verdictStyle = res ? (COLORS[res.verdict] || (res.verdict === "AI" ? COLORS["AI"] : COLORS["Not AI"])) : null;

  return (
    <div className="page-wrapper">
      {/* Moving National Border Frame in Ashoka Navy Blue */}
      <NationalMovingBorder />

      {/* Ambient background Ashoka Chakra watermark */}
      <div className="bg-watermark">
        <AshokaChakra size={640} />
      </div>

      <div className="app-layout">
        {/* LEFT COMIC SIDEBAR: 3 COMICS */}
        <aside className="comic-sidebar comic-sidebar-left">
          <div className="sidebar-sticky">
            <div className="sidebar-header-badge">
              <AshokaChakra size={20} />
              <span>CITIZEN PROTECTION CASES</span>
            </div>

            <div className="comic-column">
              {COMICS.slice(0, 3).map((comic) => (
                <ComicCard
                  key={comic.id}
                  comic={comic}
                  isExpanded={!!expandedPoints[comic.id]}
                  onTogglePoints={togglePoints}
                  onSelect={() => setActiveModal(comic)}
                />
              ))}
            </div>
          </div>
        </aside>

        {/* CENTER MAIN SCANNER WORKSPACE */}
        <main className="main-content">
          <header>
            <div className="brand-wrapper">
              <AshokaChakra size={50} spinning={busy} />
              <h1>TrueSight AI</h1>
            </div>
            <p>Forensic Synthetic Media & Deepfake Detection Platform</p>
          </header>

          <section
            className={`drop ${file ? "has-file" : ""}`}
            onClick={() => input.current.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              pick(e.dataTransfer.files[0]);
            }}
          >
            <input ref={input} type="file" hidden accept="image/*,video/*" onChange={(e) => pick(e.target.files[0])} />
            <div className="drop-icon-wrapper">
              <svg className="drop-icon" viewBox="0 0 24 24" fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <div className="drop-text">
              <strong>{file ? file.name : "Select or Drop Image / Video"}</strong>
              <span>Supports JPG, PNG, WEBP, MP4, MOV, WEBM (up to 100 MB)</span>
            </div>
          </section>

          {preview && (
            <div className="media-container">
              <div className="media">
                {isVideo ? <video src={preview} controls /> : <img src={preview} alt="upload" />}

                {/* Forensic Laser Scanner Moving Effect */}
                {busy && (
                  <div className="scanner-overlay">
                    <div className="scanner-line" />
                    <div className="scanner-grid" />
                    <div className="scanner-badge">
                      <AshokaChakra size={22} spinning={true} />
                      <span>{SCAN_STEPS[stepIdx]}</span>
                    </div>
                  </div>
                )}

                {/* Highlighted anomaly regions */}
                {res?.regions.map((g, i) => (
                  <div
                    key={i}
                    className={"box" + (g.label ? " face" : "")}
                    title={g.label ? `Face detected (Variance log: ${g.score})` : `ELA recompression anomaly (z=${g.score})`}
                    style={{
                      left: g.x * 100 + "%",
                      top: g.y * 100 + "%",
                      width: g.w * 100 + "%",
                      height: g.h * 100 + "%"
                    }}
                  >
                    <span className="box-tag">{g.label || `ELA z=${g.score}`}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {file && (
            <div className="action-row">
              <button className="primary-btn" onClick={run} disabled={busy}>
                {busy ? (
                  <>
                    <AshokaChakra size={20} spinning={true} />
                    <span>Scanning Forensic Signals...</span>
                  </>
                ) : (
                  <>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="11" cy="11" r="8"/>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                    </svg>
                    <span>Run Forensic Analysis</span>
                  </>
                )}
              </button>
            </div>
          )}

          {err && <div className="err">{err}</div>}

          {res && (
            <article className="result-article animate-slide-up">
              {/* Header Summary with Gauge and Verdict */}
              <div className="summary-card">
                <div className="summary-left">
                  <div className="verdict-header-row">
                    <span className="verdict-label-text">RESULT:</span>
                    <span className="verdict-chip" style={{ background: verdictStyle?.bg || (res.verdict === "AI" ? "#b91c1c" : "#0d6832") }}>
                      {res.verdict}
                    </span>
                  </div>
                  <p className="summary-desc">{res.explanation}</p>
                  <div className="hash-row">
                    <span className="hash-label">SHA-256:</span>
                    <code className="hash-code">{res.file.sha256}</code>
                    <button className="copy-btn" onClick={() => copyHash(res.file.sha256)}>
                      {copied ? "Copied!" : "Copy"}
                    </button>
                  </div>
                </div>
                <div className="summary-right">
                  <SuspicionGauge score={res.score} verdict={res.verdict} />
                </div>
              </div>

              {/* Evidence Signals with Animated Progress Bars */}
              <div className="section-block">
                <h3>Forensic Evidence Breakdown</h3>
                <div className="evidence-grid">
                  {res.signals.map((s) => {
                    const barColor = s.suspicion > 0.6 ? "#b91c1c" : s.suspicion > 0.35 ? "#b45309" : "#000080";
                    return (
                      <div key={s.name} className="evidence-card">
                        <div className="evidence-card-head">
                          <strong>{s.name}</strong>
                          <span className="evidence-score" style={{ color: barColor }}>
                            {(s.suspicion * 100).toFixed(0)}% suspicion
                          </span>
                        </div>
                        <div className="meter-track">
                          <div
                            className="meter-bar"
                            style={{
                              width: `${Math.max(6, Math.round(s.suspicion * 100))}%`,
                              backgroundColor: barColor
                            }}
                          />
                        </div>
                        <p className="evidence-note">{s.note}</p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Suspicious Timestamps */}
              {res.timestamps.length > 0 && (
                <div className="section-block">
                  <h3>Suspicious Video Timestamps</h3>
                  <div className="timestamp-list">
                    {res.timestamps.map((t, i) => (
                      <div key={i} className="timestamp-item">
                        <span className="timestamp-badge">{t.time}s</span>
                        <span className="timestamp-reason">{t.reason}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actionable Next Steps */}
              <div className="section-block">
                <h3>Recommended Investigation Steps</h3>
                <ul className="step-list">
                  {res.next_steps.map((s, idx) => (
                    <li key={idx}>
                      <span className="step-num">{idx + 1}</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Legal Guidance */}
              <details className="guidance-details">
                <summary>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="16" x2="12" y2="12"/>
                    <line x1="12" y1="8" x2="12.01" y2="8"/>
                  </svg>
                  <span>Legal, Preservation & Regulatory Guidance</span>
                </summary>
                <ul>
                  {res.guidance.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </details>

              <p className="limits">{res.limitations}</p>

              {/* Final Determination Note Box */}
              <div
                className="conclusion-card"
                style={{
                  borderColor: verdictStyle?.border || "#000080",
                  background: verdictStyle?.light || "#f5f8ff"
                }}
              >
                <div className="conclusion-header">
                  <AshokaChakra size={32} />
                  <div>
                    <span className="conclusion-tag">Official Determination</span>
                    <h4 style={{ color: verdictStyle?.text || (res.verdict === "AI" ? "#991b1b" : "#0d6832") }}>
                      Result: {res.verdict}
                    </h4>
                  </div>
                </div>
                <p className="conclusion-text">
                  {res.final_note || (res.verdict === "AI"
                    ? "FINAL CONCLUSION: Result is AI. Forensic analysis detected synthetic generative patterns, frequency anomalies, or generative metadata signatures."
                    : "FINAL CONCLUSION: Result is Not AI. Forensic analysis detected authentic optical sensor characteristics, natural noise distributions, and camera provenance.")}
                </p>
              </div>

              {/* Export Action */}
              <div className="export-row">
                <button className="download-btn" onClick={pdf}>
                  <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  <span>Download Signed Forensic PDF Report</span>
                </button>
              </div>
            </article>
          )}
        </main>

        {/* RIGHT COMIC SIDEBAR: 3 COMICS */}
        <aside className="comic-sidebar comic-sidebar-right">
          <div className="sidebar-sticky">
            <div className="sidebar-header-badge">
              <AshokaChakra size={20} />
              <span>CIVIC & LEGAL DEFENSE</span>
            </div>

            <div className="comic-column">
              {COMICS.slice(3, 6).map((comic) => (
                <ComicCard
                  key={comic.id}
                  comic={comic}
                  isExpanded={!!expandedPoints[comic.id]}
                  onTogglePoints={togglePoints}
                  onSelect={() => setActiveModal(comic)}
                />
              ))}
            </div>
          </div>
        </aside>
      </div>

      {/* Interactive Detail Modal for Full Comic View */}
      {activeModal && (
        <ComicModal comic={activeModal} onClose={() => setActiveModal(null)} />
      )}
    </div>
  );
}
