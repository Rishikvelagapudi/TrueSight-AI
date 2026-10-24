import io, datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

LIMITS = (
    "AI detection is an evidentiary tool supporting investigation. While TrueSight AI analyzes multi-domain optical, "
    "spectral, noise, and provenance signals, results should be evaluated in conjunction with primary source corroboration."
)

GUIDANCE = [
    "Preserve the original file and do not edit or re-save it; keep a copy of the hash shown in this report.",
    "Document where, when and by whom the media was found (URLs, usernames, screenshots with timestamps).",
    "Report unverified or malicious synthetic media using platform impersonation and deepfake reporting mechanisms.",
    "Identify official cyber investigation channels in your jurisdiction (e.g. national cybercrime portal 1930 / cybercrime.gov.in).",
    "Legal remedies depend on facts and jurisdiction; consult a qualified digital forensics attorney for legal proceedings."
]

def next_steps(v):
    is_ai = (v == "AI" or str(v).startswith("Likely AI"))
    if is_ai:
        return [
            "Treat media as synthetic / AI-generated; locate original primary source.",
            "Conduct reverse image/video search to trace generator provenance or prompt.",
            "Obtain certified forensic examination before legal, judicial, or newsroom publication."
        ]
    return [
        "Media displays authentic optical capture characteristics without synthetic generative patterns.",
        "Corroborate with original source context and camera hardware provenance.",
        "Maintain cryptographic SHA-256 hash record for evidentiary chain of custody."
    ]

def explain(r):
    verdict = r.get("verdict", "Not AI")
    top = sorted(r["signals"], key=lambda s: -s["suspicion"] * s["weight"])[:3]
    top_str = "; ".join(f"{s['name']} (suspicion {s['suspicion']:.2f})" for s in top)
    return (
        f"Forensic classification determined Result as {verdict} with weighted suspicion score {r['score']:.2f}. "
        f"Primary diagnostic signals: {top_str}."
    )

def determination(v):
    return "AI" if (v == "AI" or str(v).startswith("Likely AI")) else "Not AI"

def final_note(v, score=None):
    sc = f" (Suspicion Score: {score:.1%})" if score is not None else ""
    is_ai = (v == "AI" or str(v).startswith("Likely AI"))
    if is_ai:
        return (
            f"FINAL CONCLUSION: Result is AI{sc}. Multi-band forensic analysis identified synthetic generative "
            "patterns, frequency lattice anomalies, or generative metadata signatures."
        )
    return (
        f"FINAL CONCLUSION: Result is Not AI{sc}. Forensic analysis verified natural optical sensor noise distributions, "
        "coherent Bayer demosaicing gradients, and absence of synthetic generation anomalies."
    )

def build_pdf(r):
    buf = io.BytesIO()
    st = getSampleStyleSheet()
    P = lambda t, s="BodyText": Paragraph(t, st[s])
    doc = SimpleDocTemplate(buf, pagesize=A4, title="TrueSight AI Forensic Report")
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    
    verdict = r.get("verdict", "Not AI")
    det = "AI" if verdict == "AI" else "Not AI"
    note = r.get("final_note") or final_note(det, r.get("score"))
    
    e = [
        P("TrueSight AI - Forensic Analysis Report", "Title"),
        P(f"Generated {utc_now} UTC"),
        Spacer(1, 8),
        P(f"<b>Result:</b> {det} (Suspicion: {r['score']:.1%})", "Heading2"),
        P("<b>File:</b> %s | %s | %s bytes<br/><b>SHA-256:</b> %s" % (
            r["file"]["name"], r["kind"], r["file"]["size"], r["file"]["sha256"]
        ))
    ]
    
    t = Table(
        [["Signal", "Value", "Suspicion", "Note"]] + [
            [P(s["name"]), str(s["value"]), f"{s['suspicion']:.2f}", P(s["note"])] for s in r["signals"]
        ],
        colWidths=[120, 50, 55, 240]
    )
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c8d8ec")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#000080")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f7fb")]),
    ]))
    
    e += [
        Spacer(1, 8),
        P("Forensic Evidence", "Heading3"),
        t,
        P("Diagnostic Summary", "Heading3"),
        P(r["explanation"])
    ]
    
    if r.get("regions"):
        non_face = [g for g in r["regions"] if g.get("label") != "face"]
        if non_face:
            e += [
                P("Suspicious Image Regions", "Heading3"),
                P("; ".join(f"({g['x']:.2f},{g['y']:.2f}) score {g['score']}" for g in non_face))
            ]
            
    if r.get("timestamps"):
        e += [P("Suspicious Video Timestamps", "Heading3")] + [
            P(f"{x['time']}s - {x['reason']}") for x in r["timestamps"]
        ]
        
    safe_meta = {k: v for k, v in r.get("metadata", {}).items() if k not in ("exif", "tags", "info")}
    e += [
        P("Container & Provenance Metadata", "Heading3"),
        P(str(safe_meta).replace("<", "")),
        P("Recommended Investigation Steps", "Heading3")
    ] + [P("- " + s) for s in r["next_steps"]] + [
        P("Legal & Preservation Guidance", "Heading3")
    ] + [P("- " + s) for s in GUIDANCE] + [
        P("Limitations", "Heading3"),
        P(LIMITS)
    ]
    
    border_color = colors.HexColor("#b91c1c") if det == "AI" else colors.HexColor("#0d6832")
    conclusion_table = Table([
        [P(f"<b>FINAL RESULT: {det}</b>", "Heading3")],
        [P(f"<b>Conclusion:</b> {note}", "BodyText")]
    ], colWidths=[465])
    conclusion_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 2.0, border_color),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fef2f2") if det == "AI" else colors.HexColor("#f0fdf4")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    
    e += [Spacer(1, 12), conclusion_table]
    doc.build(e)
    return buf.getvalue()
