"""
Meeting Summarizer & Action Item Extractor
Author : Rishi Raj
UI     : Dark SaaS — inspired by intenta.ai
         #0A0A0A bg · Inter · green/purple pills · glowing cards
Fix    : @import for fonts (never <link> in Streamlit)
"""

import os, json, tempfile, traceback
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

<<<<<<< HEAD
# ══════════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
  --bg        : #0A0A0A;
  --surface   : #111111;
  --surface2  : #1A1A1A;
  --surface3  : #222222;
  --border    : rgba(255,255,255,0.07);
  --border2   : rgba(255,255,255,0.12);
  --text      : #F0F0F0;
  --text2     : #999999;
  --text3     : #555555;
  --green     : #22C55E;
  --green-bg  : rgba(34,197,94,0.10);
  --green-border: rgba(34,197,94,0.25);
  --purple    : #A855F7;
  --purple-bg : rgba(168,85,247,0.10);
  --purple-border: rgba(168,85,247,0.25);
  --blue      : #3B82F6;
  --blue-bg   : rgba(59,130,246,0.10);
  --glow-g    : 0 0 20px rgba(34,197,94,0.15);
  --glow-p    : 0 0 20px rgba(168,85,247,0.15);
  --card-shadow: 0 1px 0 rgba(255,255,255,0.04) inset,
                 0 20px 60px rgba(0,0,0,0.5),
                 0 6px 20px rgba(0,0,0,0.3);
  --card-hover : 0 1px 0 rgba(255,255,255,0.06) inset,
                 0 32px 80px rgba(0,0,0,0.6),
                 0 10px 30px rgba(0,0,0,0.4),
                 0 0 0 1px rgba(255,255,255,0.1);
}

*,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }

html,body,[class*="css"] {
  font-family   : 'Inter', -apple-system, sans-serif !important;
  background    : var(--bg) !important;
  color         : var(--text) !important;
  font-size     : 15px !important;
  -webkit-font-smoothing: antialiased !important;
}

#MainMenu,footer,header { visibility:hidden !important; }
.stApp { background: var(--bg) !important; }
.block-container {
  padding  : 2.5rem 3.5rem 6rem !important;
  max-width: 1080px !important;
}

/* ─── Sidebar ─── */
section[data-testid="stSidebar"] > div {
  background  : var(--surface) !important;
  border-right: 1px solid var(--border2) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ─── Selectbox ─── */
.stSelectbox > div > div {
  background    : var(--surface2) !important;
  border        : 1px solid var(--border2) !important;
  border-radius : 10px !important;
  color         : var(--text) !important;
  font-family   : 'Inter', sans-serif !important;
  font-size     : .9rem !important;
  transition    : border-color .18s, box-shadow .18s !important;
}
.stSelectbox > div > div:focus-within {
  border-color: var(--green) !important;
  box-shadow  : 0 0 0 3px rgba(34,197,94,.15) !important;
}
.stSelectbox > div > div > div { color: var(--text) !important; }

/* ─── File uploader ─── */
[data-testid="stFileUploader"] {
  background    : var(--surface) !important;
  border        : 1.5px dashed var(--border2) !important;
  border-radius : 16px !important;
  padding       : 2.5rem !important;
  transition    : all .25s ease !important;
  box-shadow    : var(--card-shadow) !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--green) !important;
  box-shadow  : var(--card-shadow), var(--glow-g) !important;
  transform   : translateY(-2px) !important;
}
[data-testid="stFileUploader"] *,
[data-testid="stFileUploaderDropzone"] * {
  color      : var(--text2) !important;
  font-family: 'Inter',sans-serif !important;
}

/* ─── Primary button ─── */
.stButton > button[kind="primary"] {
  background    : var(--green) !important;
  color         : #000 !important;
  font-family   : 'Inter',sans-serif !important;
  font-weight   : 700 !important;
  letter-spacing: .04em !important;
  font-size     : .85rem !important;
  border        : none !important;
  border-radius : 10px !important;
  padding       : .85rem 2.5rem !important;
  box-shadow    : 0 4px 20px rgba(34,197,94,.35) !important;
  transition    : all .2s cubic-bezier(.34,1.56,.64,1) !important;
}
.stButton > button[kind="primary"]:hover {
  transform  : translateY(-3px) scale(1.02) !important;
  box-shadow : 0 8px 32px rgba(34,197,94,.5) !important;
  background : #16a34a !important;
}
.stButton > button[kind="primary"]:active {
  transform: translateY(0) scale(.98) !important;
}

/* ─── Download button ─── */
.stDownloadButton > button {
  background    : transparent !important;
  color         : var(--text) !important;
  font-family   : 'Inter',sans-serif !important;
  font-weight   : 600 !important;
  letter-spacing: .04em !important;
  font-size     : .85rem !important;
  border        : 1px solid var(--border2) !important;
  border-radius : 10px !important;
  padding       : .85rem 2rem !important;
  transition    : all .2s ease !important;
}
.stDownloadButton > button:hover {
  border-color: var(--green) !important;
  color       : var(--green) !important;
  box-shadow  : var(--glow-g) !important;
  transform   : translateY(-2px) !important;
}

/* ─── Expander ─── */
.streamlit-expanderHeader {
  background    : var(--surface) !important;
  border        : 1px solid var(--border) !important;
  border-radius : 10px !important;
  font-family   : 'Inter',sans-serif !important;
  font-size     : .9rem !important;
  font-weight   : 500 !important;
  color         : var(--text) !important;
  padding       : .85rem 1.2rem !important;
  transition    : border-color .18s, box-shadow .18s !important;
}
.streamlit-expanderHeader:hover {
  border-color: var(--border2) !important;
  box-shadow  : var(--card-shadow) !important;
}
.streamlit-expanderContent {
  background   : var(--surface2) !important;
  border       : 1px solid var(--border) !important;
  border-top   : none !important;
  border-radius: 0 0 10px 10px !important;
}

/* ─── Text area ─── */
.stTextArea textarea {
  background  : var(--surface2) !important;
  border      : 1px solid var(--border) !important;
  border-radius:8px !important;
  color       : var(--text2) !important;
  font-family : 'Inter',sans-serif !important;
  font-size   : .85rem !important;
  line-height : 1.75 !important;
}

/* ─── Metric cards ─── */
[data-testid="metric-container"] {
  background   : var(--surface) !important;
  border       : 1px solid var(--border2) !important;
  border-radius: 14px !important;
  padding      : 1.6rem 1.8rem !important;
  box-shadow   : var(--card-shadow) !important;
  transition   : transform .2s ease, box-shadow .2s ease, border-color .2s !important;
}
[data-testid="metric-container"]:hover {
  transform   : translateY(-4px) !important;
  border-color: var(--green) !important;
  box-shadow  : var(--card-shadow), var(--glow-g) !important;
}
[data-testid="metric-container"] label {
  font-family   : 'Inter',sans-serif !important;
  font-size     : .7rem !important;
  letter-spacing: .12em !important;
  text-transform: uppercase !important;
  color         : var(--text3) !important;
  font-weight   : 600 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: 'Inter',sans-serif !important;
  font-size  : 2.4rem !important;
  font-weight: 800 !important;
  color      : var(--text) !important;
  line-height: 1.1 !important;
}

/* ─── Status ─── */
[data-testid="stStatusWidget"] {
  background   : var(--surface) !important;
  border       : 1px solid var(--border2) !important;
  border-radius: 12px !important;
  color        : var(--text) !important;
}
[data-testid="stStatusWidget"] * { color: var(--text) !important; font-family:'Inter',sans-serif !important; }

/* ─── Alerts ─── */
[data-testid="stAlert"] {
  background   : var(--surface2) !important;
  border       : 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color        : var(--text) !important;
  font-family  : 'Inter',sans-serif !important;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar       { width:4px; height:4px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--surface3); border-radius:2px; }
::-webkit-scrollbar-thumb:hover { background:var(--green); }

hr { border:none !important; border-top:1px solid var(--border) !important; margin:2.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

=======
# ══════════════════════════════════════════════════════════════════
#  GLOBAL STYLES  — injected once, applies to everything
# ══════════════════════════════════════════════════════════════════
>>>>>>> 9625fbda9aae40516b9e9dd707ab58510ff9e9fc

# ══════════════════════════════════════════════════════════════════════
#  LAZY IMPORTS
# ══════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_whisper_model(size="base"):
    import whisper; return whisper.load_model(size)

def import_pdfplumber():
    import pdfplumber; return pdfplumber

def import_docx():
    from docx import Document; return Document

def import_pillow_tesseract():
    from PIL import Image; import pytesseract; return Image, pytesseract

def get_anthropic_client():
    import anthropic
    key = os.environ.get("ANTHROPIC_API_KEY","")
    if not key: st.error("ANTHROPIC_API_KEY not set."); st.stop()
    return anthropic.Anthropic(api_key=key)


# ══════════════════════════════════════════════════════════════════════
#  EXTRACTION
# ══════════════════════════════════════════════════════════════════════
def extract_audio(b, name):
    suf = Path(name).suffix.lower()
    try:
        m = load_whisper_model(st.session_state.get("whisper_model","base"))
        with tempfile.NamedTemporaryFile(suffix=suf, delete=False) as t:
            t.write(b); p = t.name
        r = m.transcribe(p); os.unlink(p)
        return r["text"].strip(), None
    except Exception as e: return "", f"Whisper error: {e}"

def extract_pdf(b, name):
    try:
        import io; pp = import_pdfplumber(); parts=[]
        with pp.open(io.BytesIO(b)) as pdf:
            for i,pg in enumerate(pdf.pages,1):
                t=pg.extract_text()
                if t: parts.append(f"[Page {i}]\n{t}")
        return ("\n\n".join(parts),None) if parts else ("","No extractable text in PDF.")
    except Exception as e: return "", f"PDF error: {e}"

def extract_docx(b, name):
    try:
        import io; Doc=import_docx(); d=Doc(io.BytesIO(b))
        ps=[p.text.strip() for p in d.paragraphs if p.text.strip()]
        for tbl in d.tables:
            for row in tbl.rows:
                rt=" | ".join(c.text.strip() for c in row.cells if c.text.strip())
                if rt: ps.append(rt)
        return ("\n".join(ps),None) if ps else ("","DOCX has no readable text.")
    except Exception as e: return "", f"DOCX error: {e}"

def extract_txt(b, name):
    try: return b.decode("utf-8",errors="replace").strip(), None
    except Exception as e: return "", f"TXT error: {e}"

def extract_image(b, name):
    try:
        import io; Img,tess=import_pillow_tesseract()
        t=tess.image_to_string(Img.open(io.BytesIO(b)).convert("L"))
        return (t.strip(),None) if t.strip() else ("","No text detected.")
    except ImportError:
        return "", "Tesseract not installed. brew install tesseract / apt-get install tesseract-ocr"
    except Exception as e: return "", f"OCR error: {e}"

EXT_MAP={
    ".mp3":extract_audio,".wav":extract_audio,".m4a":extract_audio,
    ".flac":extract_audio,".ogg":extract_audio,
    ".pdf":extract_pdf,".docx":extract_docx,".txt":extract_txt,
    ".png":extract_image,".jpg":extract_image,".jpeg":extract_image,
}
AUDIO_EXTS={".mp3",".wav",".m4a",".flac",".ogg"}

def process_file(uf):
    name=uf.name; ext=Path(name).suffix.lower(); b=uf.read()
    fn=EXT_MAP.get(ext)
    if not fn: return {"name":name,"ext":ext,"text":"","error":f"Unsupported: {ext}","ok":False}
    text,err=fn(b,name)
    return {"name":name,"ext":ext,"text":text,"error":err,"ok":bool(text and not err)}


# ══════════════════════════════════════════════════════════════════════
#  CLAUDE
# ══════════════════════════════════════════════════════════════════════
SYS="""You are an expert meeting analyst. Return ONLY a raw JSON object — no markdown, no preamble:
{"summary":"<synthesis ≤200 words, highlight key decisions>","action_items":[{"task":"...","responsible":"...","due":"..."}]}"""

def call_claude(text, model):
    try:
        c=get_anthropic_client()
        msg=c.messages.create(model=model,max_tokens=1500,system=SYS,
            messages=[{"role":"user","content":"Meeting artifacts:\n\n"+text+"\n\nOutput JSON now."}])
        raw=msg.content[0].text.strip()
        if raw.startswith("```"): raw=raw.split("```")[1].lstrip("json").strip()
        return json.loads(raw), None
    except json.JSONDecodeError: return None, f"Non-JSON response:\n```\n{raw}\n```"
    except Exception as e: return None, f"Claude API error: {e}"

def build_markdown(results, out):
    lines=["# Meeting Summary\n\n## Summary\n",out.get("summary",""),"\n\n## Action Items\n"]
    items=out.get("action_items",[])
    if items:
        lines+=["| # | Task | Responsible | Due |","|---|------|-------------|-----|"]
        for i,it in enumerate(items,1):
            lines.append(f"| {i} | {it.get('task','—')} | {it.get('responsible','TBD')} | {it.get('due','TBD')} |")
    else: lines.append("No action items.")
    lines.append("\n\n## Sources\n")
    for r in results: lines.append(f"- {'✅' if r['ok'] else '❌'} `{r['name']}`")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════
def init_state():
    for k,v in [("results",[]),("claude_output",None),("whisper_model","base")]:
        if k not in st.session_state: st.session_state[k]=v


# ══════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════════════════════
def tag(text, color="green"):
    colors = {
        "green" : ("rgba(34,197,94,.12)",  "rgba(34,197,94,.3)",  "#22C55E"),
        "purple": ("rgba(168,85,247,.12)", "rgba(168,85,247,.3)", "#A855F7"),
        "blue"  : ("rgba(59,130,246,.12)", "rgba(59,130,246,.3)", "#3B82F6"),
        "gray"  : ("rgba(255,255,255,.06)","rgba(255,255,255,.12)","#888888"),
    }
    bg, border, fg = colors.get(color, colors["gray"])
    return (f'<span style="font-family:Inter,sans-serif;font-size:.72rem;font-weight:600;'
            f'letter-spacing:.06em;text-transform:uppercase;'
            f'background:{bg};color:{fg};border:1px solid {border};'
            f'padding:.25rem .75rem;border-radius:20px;white-space:nowrap;">{text}</span>')

def section_heading(label, title):
    st.markdown(f"""
<div style="margin:3.5rem 0 1.5rem;">
  <span style="font-family:Inter,sans-serif;font-size:.68rem;font-weight:700;
    letter-spacing:.2em;text-transform:uppercase;color:#22C55E;">{label}</span>
  <p style="font-family:Inter,sans-serif;font-size:1.9rem;font-weight:800;
    color:#F0F0F0;margin:.4rem 0 0;line-height:1.15;letter-spacing:-.03em;">{title}</p>
</div>""", unsafe_allow_html=True)

def sidebar_label(text):
    st.markdown(
        f'<p style="font-family:Inter,sans-serif;font-size:.68rem;font-weight:700;'
        f'letter-spacing:.14em;text-transform:uppercase;color:#555;margin:0 0 .4rem;">{text}</p>',
        unsafe_allow_html=True)

def uploader_label(text):
    st.markdown(
        f'<p style="font-family:Inter,sans-serif;font-size:.72rem;font-weight:600;'
        f'letter-spacing:.14em;text-transform:uppercase;color:#555;margin:0 0 .5rem;">{text}</p>',
        unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════
def render_header():
    st.markdown("""
<div style="padding:4rem 0 2rem;max-width:780px;">

  <!-- Status pill — like intenta's "SUGGESTED: KEEP GOING" -->
  <div style="display:inline-flex;align-items:center;gap:8px;
       background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.2);
       border-radius:20px;padding:.3rem .9rem .3rem .55rem;margin-bottom:2rem;">
    <span style="width:7px;height:7px;border-radius:50%;background:#22C55E;
          box-shadow:0 0 8px #22C55E;display:inline-block;flex-shrink:0;"></span>
    <span style="font-family:Inter,sans-serif;font-size:.72rem;font-weight:600;
          letter-spacing:.1em;text-transform:uppercase;color:#22C55E;">
      AI-Powered · Multi-Format
    </span>
  </div>

  <!-- Main headline -->
  <h1 style="font-family:Inter,sans-serif;font-size:clamp(2.6rem,5.5vw,4rem);
       font-weight:900;letter-spacing:-.04em;line-height:1.08;
       color:#F0F0F0;margin:0 0 1.2rem;">
    Turn any meeting<br>
    <span style="color:#22C55E;">into clear action.</span>
  </h1>

  <!-- Sub -->
  <p style="font-family:Inter,sans-serif;font-size:1.05rem;font-weight:400;
     color:#777;line-height:1.75;margin:0 0 2rem;max-width:560px;">
    Upload audio, PDFs, Word docs, images or plain text.
    Claude extracts every decision and action item — automatically.
  </p>

  <!-- Format pills row -->
  <div style="display:flex;flex-wrap:wrap;gap:.5rem;">
""" + "".join([
    f'<span style="font-family:Inter,sans-serif;font-size:.72rem;font-weight:500;'
    f'color:#888;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);'
    f'padding:.28rem .8rem;border-radius:6px;">{t}</span>'
    for t in ["mp3","wav","m4a","pdf","docx","txt","png","jpg"]
]) + """
  </div>

</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown("""
<div style="padding:1.8rem 0 1.4rem;">
  <p style="font-family:Inter,sans-serif;font-size:1.15rem;font-weight:800;
     color:#F0F0F0;margin:0;letter-spacing:-.02em;">Settings</p>
  <div style="height:2px;width:24px;background:#22C55E;border-radius:2px;
       margin-top:.5rem;box-shadow:0 0 8px #22C55E;"></div>
</div>""", unsafe_allow_html=True)

        sidebar_label("Whisper Model")
        wm = st.selectbox("Whisper model", ["tiny","base","small","medium","large"],
                          index=1, label_visibility="collapsed")
        st.session_state.whisper_model = wm

        st.markdown("<div style='height:.7rem'></div>", unsafe_allow_html=True)
        sidebar_label("Claude Model")
        cm = st.selectbox("Claude model",
             ["claude-sonnet-4-20250514","claude-haiku-4-5-20251001"],
             index=0, label_visibility="collapsed")

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("""
<p style="font-family:Inter,sans-serif;font-size:.68rem;font-weight:700;
   letter-spacing:.14em;text-transform:uppercase;color:#555;margin-bottom:.8rem;">
   Accepted Formats
</p>""", unsafe_allow_html=True)
        for icon,txt,clr in [
            ("🎵","Audio — mp3, wav, m4a","#22C55E"),
            ("📄","PDF","#3B82F6"),
            ("📝","Word — docx","#A855F7"),
            ("📃","Text — txt","#F59E0B"),
            ("🖼️","Images — png, jpg","#EC4899"),
        ]:
            st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:.5rem;padding:.4rem .6rem;
     background:rgba(255,255,255,.02);border-radius:8px;border:1px solid rgba(255,255,255,.04);">
  <span style="font-size:.9rem;">{icon}</span>
  <span style="font-family:Inter,sans-serif;font-size:.82rem;color:#888;font-weight:400;">{txt}</span>
</div>""", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
<p style="font-family:Inter,sans-serif;font-size:.8rem;color:#444;
   text-align:center;margin:0;">Built by <span style="color:#22C55E;font-weight:600;">Rishi Raj</span></p>
""", unsafe_allow_html=True)
    return cm


# ══════════════════════════════════════════════════════════════════════
#  FILE CARD
# ══════════════════════════════════════════════════════════════════════
_ICONS={".mp3":"🎵",".wav":"🎵",".m4a":"🎵",".flac":"🎵",".ogg":"🎵",
        ".pdf":"📄",".docx":"📝",".txt":"📃",".png":"🖼️",".jpg":"🖼️",".jpeg":"🖼️"}

def render_file_card(r):
    ico  = _ICONS.get(r["ext"],"📎")
    ext  = r["ext"].upper().lstrip(".")
    tick = "✅" if r["ok"] else "❌"
    with st.expander(f"{tick}  {ico}  {r['name']}  ·  {ext}", expanded=False):
        if r["error"]: st.error(r["error"])
        if r["text"]:
            wc = len(r["text"].split())
            st.markdown(
                f'<p style="font-family:Inter,sans-serif;font-size:.75rem;color:#555;'
                f'margin-bottom:.5rem;font-weight:500;">~{wc:,} words extracted</p>',
                unsafe_allow_html=True)
            st.text_area("t", value=r["text"], height=180, disabled=True,
                         key=f"ta_{r['name']}", label_visibility="collapsed")


# ══════════════════════════════════════════════════════════════════════
#  RESULTS
# ══════════════════════════════════════════════════════════════════════
def divider():
    st.markdown("""
<div style="display:flex;align-items:center;gap:16px;margin:3rem 0;">
  <div style="flex:1;height:1px;background:rgba(255,255,255,.06);"></div>
</div>""", unsafe_allow_html=True)

def render_results(results, out):

    # ─── Metric row ───
    divider()
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("Sources", sum(1 for r in results if r["ok"]))
    with c2: st.metric("Summary Words", len(out.get("summary","").split()))
    with c3: st.metric("Action Items",  len(out.get("action_items",[])))

    # ─── Summary ───
    section_heading("MEETING SUMMARY", "What Was Discussed")
    summary = out.get("summary","No summary generated.")
    st.markdown(f"""
<div style="
  background:var(--surface);
  border:1px solid var(--border2);
  border-radius:16px;
  padding:2.4rem 2.6rem;
  position:relative;overflow:hidden;
  box-shadow:var(--card-shadow);
  margin-bottom:1rem;
">
  <!-- Green top bar -->
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
       background:linear-gradient(90deg,#22C55E,transparent);"></div>
  <!-- Content -->
  <div style="display:flex;gap:1.2rem;align-items:flex-start;">
    <div style="width:36px;height:36px;border-radius:10px;flex-shrink:0;
         background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.2);
         display:flex;align-items:center;justify-content:center;font-size:1.1rem;">🎙️</div>
    <p style="font-family:Inter,sans-serif;font-size:.97rem;line-height:1.85;
       color:#C8C8C8;margin:0;font-weight:400;flex:1;">{summary}</p>
  </div>
</div>
""", unsafe_allow_html=True)

    # ─── Action items ───
    items = out.get("action_items",[])
    section_heading("NEXT STEPS", "Action Items & Owners")

    if items:
        for i,it in enumerate(items,1):
            task = it.get("task","—")
            resp = it.get("responsible","TBD")
            due  = it.get("due","TBD")
            st.markdown(f"""
<div style="
  display:flex;align-items:flex-start;gap:1.2rem;
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:14px;
  padding:1.4rem 1.6rem;
  margin-bottom:.65rem;
  box-shadow:var(--card-shadow);
  transition:border-color .2s,box-shadow .2s;
  position:relative;overflow:hidden;
" onmouseover="this.style.borderColor='rgba(255,255,255,0.14)';this.style.transform='translateY(-2px)'"
  onmouseout="this.style.borderColor='rgba(255,255,255,0.07)';this.style.transform='translateY(0)'">
  <!-- Left accent -->
  <div style="position:absolute;top:0;left:0;bottom:0;width:3px;
       background:linear-gradient(180deg,#22C55E,#16a34a);border-radius:3px 0 0 3px;"></div>
  <!-- Number badge -->
  <div style="min-width:2rem;height:2rem;border-radius:8px;flex-shrink:0;
       background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.2);
       display:flex;align-items:center;justify-content:center;margin-left:.2rem;">
    <span style="font-family:Inter,sans-serif;font-size:.8rem;
          font-weight:800;color:#22C55E;">{i}</span>
  </div>
  <!-- Content -->
  <div style="flex:1;min-width:0;">
    <p style="font-family:Inter,sans-serif;font-size:.95rem;font-weight:600;
       color:#F0F0F0;margin:0 0 .65rem;line-height:1.45;">{task}</p>
    <div style="display:flex;gap:.5rem;flex-wrap:wrap;align-items:center;">
      {tag("👤 " + resp, "green")}
      {tag("📅 " + due, "purple")}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.info("No action items identified.")

    # ─── Source files ───
    divider()
    section_heading("SOURCE FILES", "Extracted Content")
    for r in results:
        render_file_card(r)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    st.download_button(
        label="↓   Download Summary as Markdown",
        data=build_markdown(results, out),
        file_name="meeting_summary.md",
        mime="text/markdown",
        use_container_width=True,
    )


# ══════════════════════════════════════════════════════════════════════
#  EMPTY STATE
# ══════════════════════════════════════════════════════════════════════
def render_empty_state():
    st.markdown("""
<div style="
  background:var(--surface);
  border:1px solid var(--border2);
  border-radius:20px;
  padding:5rem 2rem;
  text-align:center;
  margin-top:1rem;
  box-shadow:var(--card-shadow);
  position:relative;overflow:hidden;
">
  <!-- Glow backdrop -->
  <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
       width:320px;height:320px;border-radius:50%;
       background:radial-gradient(circle,rgba(34,197,94,.06) 0%,transparent 70%);
       pointer-events:none;"></div>

  <div style="font-size:2.8rem;margin-bottom:1.4rem;">🎙️</div>
  <p style="font-family:Inter,sans-serif;font-size:1.5rem;font-weight:800;
     color:#F0F0F0;margin:0 0 .75rem;letter-spacing:-.03em;">
    Drop your meeting files
  </p>
  <p style="font-family:Inter,sans-serif;font-size:.95rem;color:#666;
     max-width:380px;margin:0 auto;line-height:1.8;font-weight:400;">
    Audio, PDFs, Word docs, screenshots — upload any combination
    and get a summary with action items in seconds.
  </p>
  <div style="display:flex;justify-content:center;gap:.5rem;flex-wrap:wrap;margin-top:2rem;">
""" + "".join([
    f'<span style="font-family:Inter,sans-serif;font-size:.7rem;font-weight:600;'
    f'letter-spacing:.08em;text-transform:uppercase;color:#555;'
    f'background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);'
    f'padding:.3rem .9rem;border-radius:6px;">{t}</span>'
    for t in ["Audio","PDF","Word","Images","Text"]
]) + """
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════
def main():
    init_state()
    render_header()
    claude_model = render_sidebar()

    uploader_label("Upload Meeting Files")
    uploaded = st.file_uploader(
        "Drop files here", accept_multiple_files=True,
        type=["mp3","wav","m4a","flac","ogg","pdf","docx","txt","png","jpg","jpeg"],
        label_visibility="collapsed",
    )

    if uploaded:
        st.markdown(
            f'<p style="font-family:Inter,sans-serif;font-size:.78rem;color:#555;'
            f'margin:.5rem 0 1.2rem;font-weight:500;">'
            f'{len(uploaded)} file{"s" if len(uploaded)>1 else ""} selected</p>',
            unsafe_allow_html=True)

        if st.button("  Analyze Meeting  ", type="primary"):
            st.session_state.results      = []
            st.session_state.claude_output = None
            has_audio = any(Path(f.name).suffix.lower() in AUDIO_EXTS for f in uploaded)

            with st.status(
                "Transcribing & extracting…" if has_audio else "Extracting text…",
                expanded=True) as status:

                results=[]
                for uf in uploaded:
                    st.write(f"Processing `{uf.name}`…")
                    r=process_file(uf); results.append(r)
                    if r["ok"]: st.write(f"  ✅  ~{len(r['text'].split()):,} words")
                    else:       st.write(f"  ⚠️  {r['error']}")

                st.session_state.results=results
                good=[r for r in results if r["ok"]]
                if not good:
                    status.update(label="No text extracted",state="error")
                    st.error("Could not extract text from any file."); return

                combined=("\n\n"+"─"*60+"\n\n").join(
                    f"[Source: {r['name']}]\n{r['text']}" for r in good)
                if len(combined.split())>6000:
                    st.warning("⚠️ Text exceeds 6 000 words — consider fewer files.")

                st.write("🤖 Analyzing with Claude…")
                out,err=call_claude(combined, claude_model)
                if err:
                    status.update(label="Claude error",state="error")
                    st.error(err); return

                st.session_state.claude_output=out
                status.update(label="Done",state="complete",expanded=False)

    if st.session_state.claude_output and st.session_state.results:
        render_results(st.session_state.results, st.session_state.claude_output)
    elif not uploaded and not st.session_state.results:
        render_empty_state()

if __name__=="__main__":
    main()
