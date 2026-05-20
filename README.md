# 🎙️ Meeting Summarizer & Action Item Extractor

> Upload audio recordings, PDFs, Word documents, images, and plain text files — get a unified meeting summary and extracted action items powered by Claude AI.

Built by **Rishi Raj** 

---
## ScreenShot
<img width="1522" height="486" alt="image" src="https://github.com/user-attachments/assets/817284f6-35fb-46a7-bd3f-7aa53ad98bd9" />

---
## Features

| Feature | Detail |
|---|---|
| 🎵 Audio transcription | Whisper (tiny → large models) |
| 📄 PDF extraction | pdfplumber (multi-page) |
| 📝 Word docs | python-docx (paragraphs + tables) |
| 🖼️ Image OCR | pytesseract + Pillow (grayscale preprocessing) |
| 📃 Plain text | UTF-8 direct read |
| 🤖 Summarization | Claude `claude-sonnet-4-20250514` or Haiku |
| ✅ Action items | Task + Responsible + Due date |
| ⬇️ Export | Download summary as Markdown |

---

## 🏗️ Tech Stack

- **UI & Backend**: Python 3.11 + Streamlit
- **Speech-to-Text**: `openai-whisper`
- **LLM**: Anthropic Claude API (`anthropic` package)
- **PDF**: `pdfplumber`
- **DOCX**: `python-docx`
- **OCR**: `pytesseract` + `Pillow`
- **Audio support**: `ffmpeg` (system dependency)
- **Config**: `python-dotenv`

---

## 🚀 Local Setup

### Prerequisites

1. **Python 3.10+**
2. **ffmpeg** (for audio files)
3. **Tesseract OCR** (for image files)
4. **Anthropic API key** — get one at https://console.anthropic.com

### Install system dependencies

**macOS (Homebrew):**
```bash
brew install ffmpeg tesseract
```

**Ubuntu / Debian:**
```bash
sudo apt-get install -y ffmpeg tesseract-ocr tesseract-ocr-eng
```

**Windows:**
- ffmpeg: https://ffmpeg.org/download.html (add to PATH)
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki

### Install Python dependencies & run

```bash
# 1. Clone / enter the project directory
cd meeting-summarizer

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install packages
pip install -r requirements.txt

# 4. Set up API key
cp .env.example .env
# Edit .env and paste your ANTHROPIC_API_KEY

# 5. Run the app
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🐳 Docker (Recommended for Deployment)

Docker bundles ffmpeg and Tesseract so you don't need to install them manually.

```bash
# Build the image
docker build -t meeting-summarizer .

# Run with your API key
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=sk-ant-... meeting-summarizer
```

Open **http://localhost:8501**

---

## 📁 Project Structure

```
meeting-summarizer/
├── app.py              # Main Streamlit application (single file)
├── requirements.txt    # Python dependencies
├── Dockerfile          # Production container
├── .env.example        # Environment variable template
├── .gitignore
└── README.md
```

---

## 🔧 Configuration

| Setting | Where | Options |
|---|---|---|
| Whisper model size | Sidebar | tiny / base / small / medium / large |
| Claude model | Sidebar | claude-sonnet-4-20250514 / claude-haiku-4-5-20251001 |
| API Key | `.env` file | `ANTHROPIC_API_KEY=...` |

**Whisper model sizes:**

| Model | VRAM | Speed | Accuracy |
|---|---|---|---|
| tiny | ~1 GB | Fastest | Basic |
| base | ~1 GB | Fast | Good ← default |
| small | ~2 GB | Medium | Better |
| medium | ~5 GB | Slow | Great |
| large | ~10 GB | Slowest | Best |

---

## ⚠️ Known Limitations

- **Scanned PDFs**: pdfplumber cannot extract text from image-based PDFs. Convert to image and upload as PNG/JPEG instead.
- **Token limit**: If combined extracted text exceeds ~6000 words, a warning is shown. Upload fewer/shorter files.
- **First audio run**: Whisper downloads the model on first use (~150 MB for `base`). Subsequent runs use the cache.
- **OCR accuracy**: pytesseract works best on clean, high-contrast images. Blurry or stylized text may not extract well.

---

## 📋 Example Output (Markdown download)

```markdown
# Meeting Summary & Action Items

## 📝 Summary
The team discussed Q3 roadmap priorities. The engineering team will 
focus on the new authentication system, while design finalises mockups 
for the onboarding flow. Budget approval for cloud infrastructure 
is pending sign-off from finance...

## ✅ Action Items

| # | Task | Responsible | Due |
|---|------|-------------|-----|
| 1 | Finalise auth system design doc | Alice (Engineering) | 2024-07-15 |
| 2 | Submit cloud budget proposal | Bob (Finance) | 2024-07-10 |
| 3 | Share onboarding mockups v2 | Carol (Design) | 2024-07-12 |

## 📂 Source Files
- ✅ `meeting_recording.mp3`
- ✅ `q3_slides.pdf`
- ✅ `whiteboard_photo.jpg`
```

---

## 📄 License

MIT — free to use and modify.
