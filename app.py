"""
Meeting Summarizer & Action Item Extractor
Author: Rishi Raj
UI: Cinematic editorial — Cormorant Garamond, warm cream, deep 3D
"""

import os, json, tempfile, traceback
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════
#  GLOBAL STYLES  — injected once, applies to everything
# ══════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
#  LAZY IMPORTS
# ══════════════════════════════════════════════════════════════════
@st.cache_resource
def load_whisper_model(size="base"):
    import whisper
    return whisper.load_model(size)

def import_pdfplumber():
    import pdfplumber; return pdfplumber

def import_docx():
    from docx import Document; return Document

def import_pillow_tesseract():
    from PIL import Image; import pytesseract; return Image, pytesseract

def get_anthropic_client():
    import anthropic
    key = os.environ.get("ANTHROPIC_API_KEY","")
    if not key:
        st.error("ANTHROPIC_API_KEY not set."); st.stop()
    return anthropic.Anthropic(api_key=key)


# ══════════════════════════════════════════════════════════════════
#  EXTRACTION
# ══════════════════════════════════════════════════════════════════
def extract_audio(b, name):
    suf = Path(name).suffix.lower()
    try:
        m = load_whisper_model(st.session_state.get("whisper_model","base"))
        with tempfile.NamedTemporaryFile(suffix=suf, delete=False) as t:
            t.write(b); p = t.name
        r = m.transcribe(p); os.unlink(p)
        return r["text"].strip(), None
    except Exception as e:
        return "", f"Whisper error: {e}"

def extract_pdf(b, name):
    try:
        import io; pp = import_pdfplumber()
        parts=[]
        with pp.open(io.BytesIO(b)) as pdf:
            for i,pg in enumerate(pdf.pages,1):
                t=pg.extract_text()
                if t: parts.append(f"[Page {i}]\n{t}")
        return ("\n\n".join(parts), None) if parts else ("","No extractable text in PDF.")
    except Exception as e: return "", f"PDF error: {e}"

def extract_docx(b, name):
    try:
        import io; Doc = import_docx()
        d = Doc(io.BytesIO(b))
        ps = [p.text.strip() for p in d.paragraphs if p.text.strip()]
        for tbl in d.tables:
            for row in tbl.rows:
                rt = " | ".join(c.text.strip() for c in row.cells if c.text.strip())
                if rt: ps.append(rt)
        return ("\n".join(ps), None) if ps else ("","DOCX has no readable text.")
    except Exception as e: return "", f"DOCX error: {e}"

def extract_txt(b, name):
    try: return b.decode("utf-8",errors="replace").strip(), None
    except Exception as e: return "", f"TXT error: {e}"

def extract_image(b, name):
    try:
        import io; Img, tess = import_pillow_tesseract()
        t = tess.image_to_string(Img.open(io.BytesIO(b)).convert("L"))
        return (t.strip(), None) if t.strip() else ("","No text detected in image.")
    except ImportError:
        return "", ("Tesseract not installed.\n• macOS: `brew install tesseract`\n"
                    "• Ubuntu: `sudo apt-get install tesseract-ocr`\n"
                    "• Windows: https://github.com/UB-Mannheim/tesseract/wiki")
    except Exception as e: return "", f"OCR error: {e}"

EXT_MAP = {
    ".mp3":extract_audio,".wav":extract_audio,".m4a":extract_audio,
    ".flac":extract_audio,".ogg":extract_audio,
    ".pdf":extract_pdf,".docx":extract_docx,".txt":extract_txt,
    ".png":extract_image,".jpg":extract_image,".jpeg":extract_image,
}
AUDIO_EXTS = {".mp3",".wav",".m4a",".flac",".ogg"}

def process_file(uf):
    name = uf.name; ext = Path(name).suffix.lower()
    b = uf.read(); fn = EXT_MAP.get(ext)
    if not fn:
        return {"name":name,"ext":ext,"text":"","error":f"Unsupported: {ext}","ok":False}
    text, err = fn(b, name)
    return {"name":name,"ext":ext,"text":text,"error":err,"ok":bool(text and not err)}


# ══════════════════════════════════════════════════════════════════
#  CLAUDE
# ══════════════════════════════════════════════════════════════════
SYS = """You are an expert meeting analyst. Return ONLY a raw JSON object (no markdown, no preamble):
{"summary":"<max 200 words, key decisions highlighted>","action_items":[{"task":"...","responsible":"...","due":"..."}]}"""

def call_claude(text, model):
    try:
        client = get_anthropic_client()
        msg = client.messages.create(
            model=model, max_tokens=1500, system=SYS,
            messages=[{"role":"user","content":"Meeting artifacts:\n\n"+text+"\n\nOutput JSON now."}],
        )
        raw = msg.content[0].text.strip()
        if raw.startswith("```"): raw = raw.split("```")[1].lstrip("json").strip()
        return json.loads(raw), None
    except json.JSONDecodeError:
        return None, f"Non-JSON response:\n```\n{raw}\n```"
    except Exception as e:
        return None, f"Claude API error: {e}"

def build_markdown(results, out):
    lines=["# Meeting Summary & Action Items\n\n## Summary\n",out.get("summary",""),
           "\n\n## Action Items\n"]
    items=out.get("action_items",[])
    if items:
        lines+=["| # | Task | Responsible | Due |","|---|------|-------------|-----|"]
        for i,it in enumerate(items,1):
            lines.append(f"| {i} | {it.get('task','—')} | {it.get('responsible','TBD')} | {it.get('due','TBD')} |")
    else: lines.append("No action items.")
    lines.append("\n\n## Sources\n")
    for r in results: lines.append(f"- {'✅' if r['ok'] else '❌'} `{r['name']}`")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════
def init_state():
    for k,v in [("results",[]),("claude_output",None),("whisper_model","base")]:
        if k not in st.session_state: st.session_state[k]=v


# ══════════════════════════════════════════════════════════════════
#  UI HELPERS — all inline styles, no class-only styling
# ══════════════════════════════════════════════════════════════════
def label(text):
    st.markdown(
        f'<p style="font-family:\'DM Sans\',sans-serif;font-size:.68rem;'
        f'letter-spacing:.18em;text-transform:uppercase;color:#9C8E84;'
        f'font-weight:500;margin:0 0 .5rem;">{text}</p>',
        unsafe_allow_html=True
    )

def section_title(eyebrow, heading):
    st.markdown(f"""
<div style="margin:2.5rem 0 1.2rem;">
  <p style="font-family:'DM Sans',sans-serif;font-size:.65rem;letter-spacing:.22em;
     text-transform:uppercase;color:#A67C3A;font-weight:500;margin:0 0 .3rem;">{eyebrow}</p>
  <p style="font-family:'Cormorant Garamond',serif;font-size:1.75rem;font-weight:400;
     color:#18140F;margin:0;line-height:1.15;">{heading}</p>
  <div style="height:2px;width:36px;background:linear-gradient(90deg,#A67C3A,transparent);margin-top:.6rem;border-radius:2px;"></div>
</div>""", unsafe_allow_html=True)

def thin_rule():
    st.markdown("""
<div style="display:flex;align-items:center;gap:16px;margin:2.5rem 0;">
  <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(24,20,15,.1));"></div>
  <span style="color:#C9A55A;font-size:.9rem;letter-spacing:.3em;">✦</span>
  <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(24,20,15,.1),transparent);"></div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  HEADER — fully inline, no external class dependencies
# ══════════════════════════════════════════════════════════════════
def render_header():
    st.markdown("""
<div style="text-align:center;padding:3.5rem 2rem 2.5rem;position:relative;">

  <div style="display:flex;align-items:center;justify-content:center;gap:14px;margin-bottom:2rem;">
    <div style="height:1px;width:56px;background:linear-gradient(90deg,transparent,#A67C3A);"></div>
    <span style="font-family:'DM Sans',sans-serif;font-size:.62rem;letter-spacing:.35em;
          text-transform:uppercase;color:#A67C3A;font-weight:500;">Est. 2025</span>
    <div style="height:1px;width:56px;background:linear-gradient(90deg,#A67C3A,transparent);"></div>
  </div>

  <div style="font-family:'Cormorant Garamond',serif;font-size:clamp(3rem,7vw,5.5rem);
       font-weight:300;line-height:1;color:#18140F;margin:0;">
    Meeting
  </div>
  <div style="font-family:'Cormorant Garamond',serif;font-size:clamp(3rem,7vw,5.5rem);
       font-weight:600;font-style:italic;line-height:1;color:#4A3728;margin:0 0 1.2rem;">
    Summarizer
  </div>

  <div style="display:flex;align-items:center;justify-content:center;gap:20px;margin-bottom:1.4rem;">
    <div style="height:1px;width:40px;background:rgba(24,20,15,.12);"></div>
    <span style="font-family:'DM Sans',sans-serif;font-size:.72rem;
          letter-spacing:.2em;text-transform:uppercase;color:#9C8E84;font-weight:400;">
      Action Items &nbsp;·&nbsp; Unified Summary &nbsp;·&nbsp; All File Types
    </span>
    <div style="height:1px;width:40px;background:rgba(24,20,15,.12);"></div>
  </div>

</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown("""
<div style="padding:1.8rem 0 1.2rem;">
  <p style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;
     font-weight:600;color:#18140F;margin:0 0 .15rem;">Settings</p>
  <div style="height:2px;width:28px;background:linear-gradient(90deg,#A67C3A,transparent);border-radius:2px;"></div>
</div>""", unsafe_allow_html=True)

        label("Whisper Model")
        wm = st.selectbox("Whisper model",["tiny","base","small","medium","large"],
                          index=1, label_visibility="collapsed")
        st.session_state.whisper_model = wm

        st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
        label("Claude Model")
        cm = st.selectbox("Claude model",
                          ["claude-sonnet-4-20250514","claude-haiku-4-5-20251001"],
                          index=0, label_visibility="collapsed")

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("""
<p style="font-family:'DM Sans',sans-serif;font-size:.65rem;letter-spacing:.18em;
   text-transform:uppercase;color:#9C8E84;font-weight:500;margin-bottom:.8rem;">
  Accepted Formats
</p>""", unsafe_allow_html=True)
        for icon, txt in [("🎵","Audio — mp3, wav, m4a, flac"),("📄","PDF"),
                          ("📝","Word — docx"),("📃","Text — txt"),("🖼️","Images — png, jpg")]:
            st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:.45rem;">
  <span style="font-size:.9rem;">{icon}</span>
  <span style="font-family:'DM Sans',sans-serif;font-size:.8rem;color:#5C5248;">{txt}</span>
</div>""", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
<p style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1rem;
   color:#9C8E84;text-align:center;margin:0;">Built by Rishi Raj</p>
""", unsafe_allow_html=True)
    return cm


# ══════════════════════════════════════════════════════════════════
#  FILE CARDS
# ══════════════════════════════════════════════════════════════════
_ICONS = {".mp3":"🎵",".wav":"🎵",".m4a":"🎵",".flac":"🎵",".ogg":"🎵",
          ".pdf":"📄",".docx":"📝",".txt":"📃",".png":"🖼️",".jpg":"🖼️",".jpeg":"🖼️"}

def render_file_card(r):
    icon = _ICONS.get(r["ext"],"📎")
    ext  = r["ext"].upper().lstrip(".")
    tick = "✅" if r["ok"] else "❌"
    with st.expander(f"{tick}  {icon}  {r['name']}  ·  {ext}", expanded=False):
        if r["error"]:
            st.error(r["error"])
        if r["text"]:
            wc = len(r["text"].split())
            st.markdown(f'<p style="font-family:\'DM Mono\',monospace;font-size:.72rem;'
                        f'color:#9C8E84;letter-spacing:.05em;margin-bottom:.5rem;">~{wc:,} words</p>',
                        unsafe_allow_html=True)
            st.text_area("t", value=r["text"], height=170, disabled=True,
                         key=f"ta_{r['name']}", label_visibility="collapsed")


# ══════════════════════════════════════════════════════════════════
#  RESULTS PAGE
# ══════════════════════════════════════════════════════════════════
def render_results(results, out):

    # ── Metric cards ──
    thin_rule()
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("Sources Processed", sum(1 for r in results if r["ok"]))
    with c2: st.metric("Summary Words", len(out.get("summary","").split()))
    with c3: st.metric("Action Items", len(out.get("action_items",[])))

    # ── Summary ──
    section_title("Meeting Summary", "What was discussed")
    summary = out.get("summary","No summary generated.")
    st.markdown(f"""
<div style="background:#FFFFFF;border:1px solid rgba(24,20,15,.08);border-radius:16px;
     padding:2.4rem 2.8rem 2.4rem 3.2rem;
     box-shadow:0 1px 0 rgba(255,255,255,.85) inset,
                0 20px 50px rgba(24,20,15,.1),
                0 6px 16px rgba(24,20,15,.07),
                0 2px 4px rgba(24,20,15,.04);
     position:relative;overflow:hidden;margin-bottom:1rem;">
  <div style="position:absolute;top:0;left:0;bottom:0;width:4px;
       background:linear-gradient(180deg,#C9A55A,#A67C3A);border-radius:4px 0 0 4px;"></div>
  <div style="position:absolute;bottom:-10px;right:20px;
       font-family:'Cormorant Garamond',serif;font-size:7rem;font-weight:600;
       color:rgba(200,165,90,.12);line-height:1;user-select:none;pointer-events:none;">"</div>
  <p style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;line-height:1.9;
     color:#18140F;margin:0;font-style:italic;font-weight:400;position:relative;z-index:1;">
    {summary}
  </p>
</div>""", unsafe_allow_html=True)

    # ── Action Items ──
    items = out.get("action_items", [])
    section_title("Next Steps", "Action items &amp; owners")

    if items:
        for i, it in enumerate(items, 1):
            task  = it.get("task","—")
            resp  = it.get("responsible","TBD")
            due   = it.get("due","TBD")
            st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:1.2rem;
     background:#FFFFFF;border:1px solid rgba(24,20,15,.08);border-radius:12px;
     padding:1.4rem 1.8rem;margin-bottom:.7rem;
     box-shadow:0 1px 0 rgba(255,255,255,.85) inset,
                0 12px 32px rgba(24,20,15,.08),
                0 4px 10px rgba(24,20,15,.05),
                0 1px 3px rgba(24,20,15,.04);
     transition:transform .2s ease,box-shadow .2s ease;">
  <div style="min-width:2.3rem;height:2.3rem;
       background:linear-gradient(145deg,#2E2218,#18140F);
       border-radius:50%;display:flex;align-items:center;justify-content:center;
       box-shadow:0 4px 12px rgba(24,20,15,.28),0 1px 3px rgba(24,20,15,.15);
       flex-shrink:0;margin-top:.05rem;">
    <span style="font-family:'Cormorant Garamond',serif;font-size:1rem;
          font-weight:600;color:#EDD9A3;">{i}</span>
  </div>
  <div style="flex:1;min-width:0;">
    <p style="font-family:'Cormorant Garamond',serif;font-size:1.12rem;font-weight:500;
       color:#18140F;margin:0 0 .65rem;line-height:1.45;">{task}</p>
    <div style="display:flex;gap:.6rem;flex-wrap:wrap;">
      <span style="font-family:'DM Sans',sans-serif;font-size:.72rem;font-weight:500;
            letter-spacing:.04em;background:#F5EDD8;color:#7A5C20;
            padding:.22rem .8rem;border-radius:20px;border:1px solid rgba(166,124,58,.25);">
        👤 {resp}
      </span>
      <span style="font-family:'DM Sans',sans-serif;font-size:.72rem;font-weight:500;
            letter-spacing:.04em;background:#EEEEFF;color:#3636A0;
            padding:.22rem .8rem;border-radius:20px;border:1px solid rgba(54,54,160,.18);">
        📅 {due}
      </span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
    else:
        st.info("No action items identified in the uploaded content.")

    # ── Source files ──
    thin_rule()
    section_title("Source Files", "Extracted content")
    for r in results:
        render_file_card(r)

    # ── Download ──
    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    st.download_button(
        label="↓   Download Summary as Markdown",
        data=build_markdown(results, out),
        file_name="meeting_summary.md",
        mime="text/markdown",
        use_container_width=True,
    )


# ══════════════════════════════════════════════════════════════════
#  EMPTY STATE
# ══════════════════════════════════════════════════════════════════
def render_empty_state():
    st.markdown("""
<div style="text-align:center;padding:4rem 2rem 4.5rem;
     background:#FFFFFF;border:1px solid rgba(24,20,15,.07);
     border-radius:18px;margin-top:.5rem;
     box-shadow:0 1px 0 rgba(255,255,255,.85) inset,
                0 20px 50px rgba(24,20,15,.09),
                0 6px 16px rgba(24,20,15,.06),
                0 2px 4px rgba(24,20,15,.04);">
  <div style="font-size:3rem;margin-bottom:1.4rem;opacity:.5;letter-spacing:.1em;">🎬</div>
  <p style="font-family:'Cormorant Garamond',serif;font-size:1.7rem;font-weight:400;
     font-style:italic;color:#18140F;margin:0 0 .75rem;">Ready for your meeting files</p>
  <p style="font-family:'DM Sans',sans-serif;font-size:.84rem;color:#9C8E84;
     max-width:360px;margin:0 auto;line-height:1.75;">
    Upload any combination of audio, PDF, Word, images, or text files.<br>
    Claude synthesises everything into one clean summary.
  </p>
  <div style="display:flex;justify-content:center;gap:.6rem;flex-wrap:wrap;margin-top:2rem;">
""" + "".join(
    f'<span style="font-family:\'DM Sans\',sans-serif;font-size:.7rem;letter-spacing:.1em;'
    f'text-transform:uppercase;color:#9C8E84;background:#F5F2EA;'
    f'padding:.35rem 1rem;border-radius:20px;border:1px solid rgba(24,20,15,.08);">{t}</span>'
    for t in ["Audio","PDF","Word","Images","Text"]
) + """
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    init_state()
    render_header()
    claude_model = render_sidebar()

    label("Upload Meeting Files")
    uploaded = st.file_uploader(
        "Drop files here", accept_multiple_files=True,
        type=["mp3","wav","m4a","flac","ogg","pdf","docx","txt","png","jpg","jpeg"],
        label_visibility="collapsed",
    )

    if uploaded:
        st.markdown(
            f'<p style="font-family:\'DM Mono\',monospace;font-size:.75rem;color:#9C8E84;'
            f'margin:.5rem 0 1.2rem;letter-spacing:.04em;">'
            f'{len(uploaded)} file{"s" if len(uploaded)>1 else ""} selected</p>',
            unsafe_allow_html=True
        )
        if st.button("  Process & Summarize  ", type="primary"):
            st.session_state.results = []
            st.session_state.claude_output = None
            has_audio = any(Path(f.name).suffix.lower() in AUDIO_EXTS for f in uploaded)

            with st.status("Extracting text from files…" if not has_audio else "Transcribing audio & extracting text…",
                           expanded=True) as status:
                results = []
                for uf in uploaded:
                    st.write(f"Processing `{uf.name}`…")
                    r = process_file(uf); results.append(r)
                    st.write(f"  {'✅' if r['ok'] else '⚠️'}  {'~'+str(len(r['text'].split()))+' words' if r['ok'] else r['error']}")

                st.session_state.results = results
                good = [r for r in results if r["ok"]]
                if not good:
                    status.update(label="No text extracted", state="error")
                    st.error("Could not extract text from any file."); return

                combined = ("\n\n" + "─"*60 + "\n\n").join(
                    f"[Source: {r['name']}]\n{r['text']}" for r in good)
                if len(combined.split()) > 6000:
                    st.warning("Combined text exceeds 6 000 words — results may be truncated.")

                st.write("Sending to Claude…")
                out, err = call_claude(combined, claude_model)
                if err:
                    status.update(label="Claude error", state="error")
                    st.error(err); return

                st.session_state.claude_output = out
                status.update(label="Analysis complete", state="complete", expanded=False)

    if st.session_state.claude_output and st.session_state.results:
        render_results(st.session_state.results, st.session_state.claude_output)
    elif not uploaded and not st.session_state.results:
        render_empty_state()


if __name__ == "__main__":
    main()
