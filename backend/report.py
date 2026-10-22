import io, datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

LIMITS = ("AI detection is not definitive proof that media is genuine or fake. Results can be wrong, especially after compression, editing, or with unfamiliar generation tools. "
          "This report supports preliminary investigation and does not replace expert forensic examination or legal advice.")
GUIDANCE = ["Preserve the original file and do not edit or re-save it; keep a copy of the hash shown in this report.",
            "Document where, when and by whom the media was found (URLs, usernames, screenshots with timestamps).",
            "Report the content to the hosting platform using its impersonation / synthetic-media / intimate-imagery reporting tools.",
            "Identify official channels in your jurisdiction (e.g. national cybercrime portal or local police cyber cell).",
            "Legal remedies depend on the facts and applicable law; consult a qualified lawyer. This tool does not determine that a crime occurred."]

def next_steps(v):
    if v.startswith("Likely AI"): return ["Treat the media as unverified; find the original source.", "Run a reverse image/video search.", "Seek expert forensic review before relying on or publishing it."]
    if v == "Likely Authentic": return ["No strong manipulation indicators found, but this is not proof of authenticity.", "Corroborate with the original source and context."]
    return ["Evidence is mixed. Obtain the highest-quality original file.", "Corroborate through source tracing and an expert review."]

def explain(r):
    top = sorted(r["signals"], key=lambda s: -s["suspicion"] * s["weight"])[:3]
    return (f"Combined weighted suspicion score is {r['score']:.2f} (0 = no indicators, 1 = strong indicators). Main contributors: "
            + "; ".join(f"{s['name']} (suspicion {s['suspicion']:.2f})" for s in top) + ". Scores come from heuristic and model signals with known error rates.")

def determination(v):
    if v.startswith("Likely AI"): return "AI-Generated / Manipulated"
    if v == "Likely Authentic": return "Not AI-Generated (Authentic)"
    return "Inconclusive (Uncertain)"

def final_note(v, score=None):
    sc = f" (Score: {score:.2f})" if score is not None else ""
    if v.startswith("Likely AI"):
        return f"FINAL CONCLUSION: This media is classified as AI-GENERATED or MANIPULATED{sc}. Forensic analysis revealed strong patterns indicative of synthetic generation or digital tampering."
    if v == "Likely Authentic":
        return f"FINAL CONCLUSION: This media is classified as NOT AI-GENERATED (AUTHENTIC){sc}. No substantial indicators of synthetic generation or tampering were detected."
    return f"FINAL CONCLUSION: INCONCLUSIVE regarding whether this media is AI-generated or authentic{sc}. Forensic indicators are mixed or insufficient to make a definitive determination."

def build_pdf(r):
    buf = io.BytesIO(); st = getSampleStyleSheet(); P = lambda t, s="BodyText": Paragraph(t, st[s])
    doc = SimpleDocTemplate(buf, pagesize=A4, title="TrueSight AI Forensic Report")
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    det = r.get("ai_determination") or determination(r["verdict"])
    note = r.get("final_note") or final_note(r["verdict"], r.get("score"))
    e = [P("TrueSight AI - Forensic Report", "Title"), P(f"Generated {utc_now} UTC"), Spacer(1, 8),
         P(f"<b>Result:</b> {r['verdict']} (score {r['score']})", "Heading2"),
         P("<b>File:</b> %s | %s | %s bytes<br/><b>SHA-256:</b> %s" % (r["file"]["name"], r["kind"], r["file"]["size"], r["file"]["sha256"]))]
    t = Table([["Signal", "Value", "Suspicion", "Note"]] + [[P(s["name"]), s["value"], s["suspicion"], P(s["note"])] for s in r["signals"]], colWidths=[110, 50, 55, 250])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c8d8ec")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#000080")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f7fb")]),
    ]))
    e += [Spacer(1, 8), P("Evidence", "Heading3"), t, P("Explanation", "Heading3"), P(r["explanation"])]
    if r["regions"]: e += [P("Suspicious regions", "Heading3"), P("; ".join(f"({g['x']:.2f},{g['y']:.2f}) score {g['score']}" for g in r["regions"] if g.get("label") != "face"))]
    if r["timestamps"]: e += [P("Suspicious timestamps", "Heading3")] + [P(f"{x['time']}s - {x['reason']}") for x in r["timestamps"]]
    e += [P("Metadata", "Heading3"), P(str({k: v for k, v in r["metadata"].items() if k not in ("exif", "tags")}).replace("<", "")),
          P("Recommended next steps", "Heading3")] + [P("- " + s) for s in r["next_steps"]] + [P("Legal and safety guidance", "Heading3")] + [P("- " + s) for s in GUIDANCE] + [P("Limitations", "Heading3"), P(LIMITS)]
    
    border_color = colors.HexColor("#d64545") if "AI-Generated" in det and "Not" not in det else (colors.HexColor("#1f9d55") if "Not AI-Generated" in det else colors.HexColor("#d69e2e"))
    conclusion_table = Table([
        [P(f"<b>FINAL AI DETERMINATION: {det.upper()}</b>", "Heading3")],
        [P(f"<b>Note:</b> {note}", "BodyText")]
    ], colWidths=[465])
    conclusion_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.5, border_color),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f6f8")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    e += [Spacer(1, 12), conclusion_table]
    doc.build(e); return buf.getvalue()
