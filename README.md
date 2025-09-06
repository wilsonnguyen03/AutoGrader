# 📝 AutoGrader

An experimental grading application that combines **OCR text recognition** with **AI-based answer checking**.  
Teachers can upload a worksheet, define question/answer regions, and automatically grade scanned student submissions.

---

## 🚩 Problem
Grading student worksheets manually is time-consuming and error-prone. Handwriting recognition is especially challenging.

## 💡 Solution
AutoGrader allows teachers to:
- Upload a blank worksheet, highlight question and answer regions.
- Save answer keys interactively.
- Upload student worksheets for automated scanning and grading.
- Compare answers with OCR + AI similarity checks (Groq API).

---

## ⚙️ Tech Stack
- **Frontend / GUI:** Tkinter, CustomTkinter  
- **OCR Engines:** Tesseract · EasyOCR · PaddleOCR  
- **AI Model API:** Groq (LLaMA-3.3-70b)  
- **Image Processing:** OpenCV, PIL  
- **Deployment Target:** Desktop (Python app)

---

## 🔑 Features
- Highlight Q&A regions on a worksheet interactively.  
- Multi-engine OCR (Tesseract, EasyOCR, PaddleOCR) for better recognition.  
- AI-powered similarity checking to allow flexible student answers.  
- Automatic placement of ✓ (correct) or ✗ (incorrect) markers on worksheets.  
- Export graded worksheets as image files.  
- Repeat grading with multiple student uploads.  

---

## 📸 Screenshots (optional)
*(Insert example screenshots of worksheet upload, Q&A region selection, and grading output.)*

---

## ▶️ How to Run
1. Clone this repo:
   ```bash
   git clone https://github.com/wilsonnguyen03/autograder
   cd autograder
