"""
Meeting Summarizer & Action Item Extractor
Author: Rishi Raj
Stack: Python + Streamlit + Whisper + Claude API
"""

import os
import json
import tempfile
import traceback
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────── Page config ───────────────────────────
st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────── CSS ────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 { margin: 0; font-size: 2.2rem; }
    .main-header p  { margin: 0.5rem 0 0; opacity: 0.9; font-size: 1rem; }

    .file-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .file-card.success { border-left: 4px solid #28a745; }
    .file-card.error   { border-left: 4px solid #dc3545; }

    .summary-box {
        background: linear-gradient(135deg, #e8f4fd 0%, #d6eaf8 100%);
        border: 1px solid #3498db;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .action-item {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #764ba2;
    }
    .action-item h4 { margin: 0 0 0.5rem; color: #333; }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
        font-weight: 600;
    }
    .badge-person { background: #d4edda; color: #155724; }
    .badge-due    { background: #fff3cd; color: #856404; }
    .stExpander   { border: 1px solid #e9ecef !important; border-radius: 8px !important; }
    div[data-testid="metric-container"] {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────── Lazy imports ───────────────────────────
@st.cache_resource
def load_whisper_model(model_size="base"):
    import whisper
    return whisper.load_model(model_size)


def import_pdfplumber():
    import pdfplumber
    return pdfplumber


def import_docx():
    from docx import Document
    return Document


def import_pillow_tesseract():
    from PIL import Image
    import pytesseract
    return Image, pytesseract


def get_anthropic_client():
    import anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY not set. Add it to your .env file or environment.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)


# ─────────────────────────── Extraction helpers ─────────────────────
def extract_audio(file_bytes: bytes, filename: str) -> tuple[str, str | None]:
    """Transcribe audio with Whisper. Returns (text, error_msg)."""
    suffix = Path(filename).suffix.lower()
    try:
        model = load_whisper_model(
            st.session_state.get("whisper_model", "base")
        )
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        result = model.transcribe(tmp_path)
        os.unlink(tmp_path)
        return result["text"].strip(), None
    except Exception as e:
        return "", f"Whisper error: {e}\n\nTip: Check that ffmpeg is installed and the audio format is supported."


def extract_pdf(file_bytes: bytes, filename: str) -> tuple[str, str | None]:
    """Extract text from PDF with pdfplumber."""
    try:
        pdfplumber = import_pdfplumber()
        import io
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"[Page {i}]\n{page_text}")
        if not text_parts:
            return "", "PDF appears to have no extractable text (possibly scanned). Try converting to image and re-uploading."
        return "\n\n".join(text_parts), None
    except Exception as e:
        return "", f"PDF extraction error: {e}"


def extract_docx(file_bytes: bytes, filename: str) -> tuple[str, str | None]:
    """Extract text from .docx with python-docx."""
    try:
        import io
        Document = import_docx()
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(
                    cell.text.strip() for cell in row.cells if cell.text.strip()
                )
                if row_text:
                    paragraphs.append(row_text)
        if not paragraphs:
            return "", "DOCX has no readable text."
        return "\n".join(paragraphs), None
    except Exception as e:
        return "", f"DOCX extraction error: {e}"


def extract_txt(file_bytes: bytes, filename: str) -> tuple[str, str | None]:
    """Read plain-text file."""
    try:
        return file_bytes.decode("utf-8", errors="replace").strip(), None
    except Exception as e:
        return "", f"Text file read error: {e}"


def extract_image(file_bytes: bytes, filename: str) -> tuple[str, str | None]:
    """OCR an image with pytesseract."""
    try:
        import io
        Image, pytesseract = import_pillow_tesseract()
        img = Image.open(io.BytesIO(file_bytes)).convert("L")  # grayscale
        text = pytesseract.image_to_string(img)
        if not text.strip():
            return "", "No text detected in image. Check image quality."
        return text.strip(), None
    except ImportError:
        return "", (
            "OCR requires **Tesseract** to be installed.\n\n"
            "• **macOS**: `brew install tesseract`\n"
            "• **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`\n"
            "• **Windows**: Download installer from https://github.com/UB-Mannheim/tesseract/wiki\n\n"
            "Also install the Python binding: `pip install pytesseract Pillow`"
        )
    except Exception as e:
        return "", f"Image OCR error: {e}"


EXTRACTOR_MAP = {
    ".mp3":  extract_audio,
    ".wav":  extract_audio,
    ".m4a":  extract_audio,
    ".flac": extract_audio,
    ".ogg":  extract_audio,
    ".pdf":  extract_pdf,
    ".docx": extract_docx,
    ".txt":  extract_txt,
    ".png":  extract_image,
    ".jpg":  extract_image,
    ".jpeg": extract_image,
}

AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}


def process_file(uploaded_file) -> dict:
    """Process a single uploaded file and return a result dict."""
    name = uploaded_file.name
    ext  = Path(name).suffix.lower()
    file_bytes = uploaded_file.read()

    extractor = EXTRACTOR_MAP.get(ext)
    if extractor is None:
        return {"name": name, "ext": ext, "text": "", "error": f"Unsupported file type: {ext}", "ok": False}

    text, error = extractor(file_bytes, name)
    return {
        "name": name,
        "ext":  ext,
        "text": text,
        "error": error,
        "ok":   bool(text and not error),
    }


# ─────────────────────────── Claude integration ─────────────────────
SYSTEM_PROMPT = """You are an expert meeting analyst. You will receive combined text from multiple meeting artifacts (audio transcripts, documents, images, etc.).

Your task is to produce a JSON object — and NOTHING else (no markdown, no preamble):

{
  "summary": "<concise synthesis of ALL sources, max 200 words, highlight key decisions>",
  "action_items": [
    {"task": "<clear action>", "responsible": "<person or team, or 'TBD'>", "due": "<deadline or 'TBD'>"}
  ]
}

Rules:
- summary must be 200 words or fewer.
- Extract EVERY action item mentioned across ALL sources. If no action items, return an empty list.
- Do NOT include any text outside the JSON object."""


def call_claude(combined_text: str, model: str) -> tuple[dict | None, str | None]:
    """Call Claude API and return (parsed_json, error_message)."""
    client = get_anthropic_client()
    try:
        message = client.messages.create(
            model=model,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Here are the meeting artifacts:\n\n"
                        + combined_text
                        + "\n\nGenerate the JSON output now."
                    ),
                }
            ],
        )
        raw = message.content[0].text.strip()
        # Strip accidental markdown code fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)
        return parsed, None
    except json.JSONDecodeError:
        return None, f"Claude returned non-JSON output:\n\n```\n{raw}\n```"
    except Exception as e:
        return None, f"Claude API error: {e}\n\n{traceback.format_exc()}"


# ─────────────────────────── Markdown export ────────────────────────
def build_markdown(results: list[dict], claude_output: dict) -> str:
    lines = ["# Meeting Summary & Action Items\n"]
    lines.append("## 📝 Summary\n")
    lines.append(claude_output.get("summary", "_No summary generated._"))
    lines.append("\n\n## ✅ Action Items\n")
    items = claude_output.get("action_items", [])
    if items:
        lines.append("| # | Task | Responsible | Due |")
        lines.append("|---|------|-------------|-----|")
        for i, item in enumerate(items, 1):
            lines.append(
                f"| {i} | {item.get('task','—')} | {item.get('responsible','TBD')} | {item.get('due','TBD')} |"
            )
    else:
        lines.append("_No action items identified._")

    lines.append("\n\n## 📂 Source Files\n")
    for r in results:
        status = "✅" if r["ok"] else "❌"
        lines.append(f"- {status} `{r['name']}`")

    return "\n".join(lines)


# ─────────────────────────── Session state ──────────────────────────
def init_state():
    defaults = {
        "results":      [],
        "claude_output": None,
        "processing":   False,
        "whisper_model": "base",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────── UI ─────────────────────────────────────
def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>🎙️ Meeting Summarizer</h1>
        <p>Upload audio, PDFs, Word docs, images & text — get a unified summary + action items</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Settings")
        st.session_state.whisper_model = st.selectbox(
            "Whisper model (audio)",
            ["tiny", "base", "small", "medium", "large"],
            index=1,
            help="Larger = more accurate, slower. 'base' is a good default."
        )
        claude_model = st.selectbox(
            "Claude model",
            [
                "claude-sonnet-4-20250514",
                "claude-haiku-4-5-20251001",
            ],
            index=0,
        )
        st.divider()
        st.markdown("**Supported file types**")
        st.markdown("""
- 🎵 Audio: mp3, wav, m4a, flac, ogg
- 📄 PDF: pdf
- 📝 Word: docx
- 📃 Text: txt
- 🖼️ Image: png, jpg, jpeg
""")
        st.divider()
        st.caption("Built with ❤️ by Rishi Raj")
    return claude_model


def render_file_results(results: list[dict]):
    st.subheader("📂 Extracted Content")
    for r in results:
        status_class = "success" if r["ok"] else "error"
        icon = "✅" if r["ok"] else "❌"
        ext = r["ext"].upper().lstrip(".")

        with st.expander(f"{icon} `{r['name']}` ({ext})", expanded=False):
            if r["error"]:
                st.error(r["error"])
            if r["text"]:
                st.text_area(
                    label=f"Extracted text — {r['name']}",
                    value=r["text"],
                    height=200,
                    disabled=True,
                    key=f"ta_{r['name']}",
                    label_visibility="collapsed",
                )
                st.caption(f"~{len(r['text'].split())} words")


def render_claude_output(claude_output: dict, results: list[dict]):
    st.divider()
    col1, col2, col3 = st.columns(3)
    n_sources  = sum(1 for r in results if r["ok"])
    n_words    = len(claude_output.get("summary", "").split())
    n_actions  = len(claude_output.get("action_items", []))
    col1.metric("📂 Sources processed", n_sources)
    col2.metric("📝 Summary words",     n_words)
    col3.metric("✅ Action items",       n_actions)

    st.subheader("📋 Meeting Summary")
    st.markdown(
        f'<div class="summary-box">{claude_output.get("summary","_No summary._")}</div>',
        unsafe_allow_html=True,
    )

    st.subheader("✅ Action Items")
    items = claude_output.get("action_items", [])
    if items:
        for i, item in enumerate(items, 1):
            task        = item.get("task", "—")
            responsible = item.get("responsible", "TBD")
            due         = item.get("due", "TBD")
            st.markdown(f"""
<div class="action-item">
    <h4>#{i} — {task}</h4>
    <span class="badge badge-person">👤 {responsible}</span>
    <span class="badge badge-due">📅 {due}</span>
</div>
""", unsafe_allow_html=True)
    else:
        st.info("No action items were identified in the uploaded content.")

    # Download button
    md_content = build_markdown(results, claude_output)
    st.download_button(
        label="⬇️ Download as Markdown",
        data=md_content,
        file_name="meeting_summary.md",
        mime="text/markdown",
        use_container_width=True,
    )


# ─────────────────────────── Main ───────────────────────────────────
def main():
    init_state()
    render_header()
    claude_model = render_sidebar()

    # ── File uploader ──
    uploaded_files = st.file_uploader(
        label="Upload meeting files",
        accept_multiple_files=True,
        type=["mp3", "wav", "m4a", "flac", "ogg", "pdf", "docx", "txt", "png", "jpg", "jpeg"],
        help="Select one or more files from your meeting (audio, slides PDF, notes, screenshots…)",
    )

    if uploaded_files:
        st.caption(f"📎 {len(uploaded_files)} file(s) selected")

        if st.button("🚀 Process & Summarize", type="primary", use_container_width=True):
            # Clear previous results
            st.session_state.results      = []
            st.session_state.claude_output = None

            # ── Extract text from each file ──
            has_audio = any(
                Path(f.name).suffix.lower() in AUDIO_EXTS for f in uploaded_files
            )
            progress_label = "Transcribing audio & extracting text…" if has_audio else "Extracting text from files…"

            with st.status(progress_label, expanded=True) as status:
                results = []
                for i, uf in enumerate(uploaded_files, 1):
                    st.write(f"Processing `{uf.name}`…")
                    result = process_file(uf)
                    results.append(result)
                    if result["ok"]:
                        word_count = len(result["text"].split())
                        st.write(f"  ✅ Extracted ~{word_count} words")
                    else:
                        st.write(f"  ⚠️ Issue: {result['error']}")

                st.session_state.results = results

                # ── Build combined text ──
                good_results = [r for r in results if r["ok"]]
                if not good_results:
                    status.update(label="❌ No text extracted", state="error")
                    st.error("Could not extract text from any of the uploaded files. Check the errors above.")
                    return

                combined_parts = [
                    f"[Source: {r['name']}]\n{r['text']}" for r in good_results
                ]
                combined_text = "\n\n{'='*60}\n\n".join(combined_parts)

                total_words = len(combined_text.split())
                if total_words > 6000:
                    st.warning(
                        f"⚠️ Combined text is ~{total_words} words (>{6000} recommended). "
                        "Claude may truncate context. Consider uploading fewer or shorter files."
                    )

                # ── Call Claude ──
                st.write("🤖 Sending to Claude for summarization…")
                claude_output, error = call_claude(combined_text, claude_model)

                if error:
                    status.update(label="⚠️ Claude error", state="error")
                    st.error(error)
                    return

                st.session_state.claude_output = claude_output
                status.update(label="✅ Done!", state="complete", expanded=False)

    # ── Display results (persists after button click) ──
    if st.session_state.results:
        render_file_results(st.session_state.results)

    if st.session_state.claude_output:
        render_claude_output(st.session_state.claude_output, st.session_state.results)

    # ── Empty state ──
    if not uploaded_files and not st.session_state.results:
        st.markdown("""
        <div style="text-align:center; padding:3rem; color:#6c757d;">
            <div style="font-size:4rem;">🎙️</div>
            <h3>Ready to summarize your meeting</h3>
            <p>Upload one or more files above to get started.</p>
            <p style="font-size:0.85rem;">Supports: audio (mp3/wav/m4a), PDF, Word (docx), plain text, and images (png/jpg)</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
