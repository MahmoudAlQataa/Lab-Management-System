# 🏥 Nebras Medical Laboratory System

A comprehensive medical laboratory management system built with Flask, designed to streamline patient data management, test result entry, and professional PDF report generation.

---

## ✨ Features

### 📋 Patient Management
- Add and manage patient records (name, age, gender, ID number, doctor)
- Search existing patients instantly while adding new reports
- Full patient history — view all analyses per patient in one place
- Link new analyses to existing patient records

### 🔬 Analysis Support
Supports multiple analysis types out of the box:

| Type | Description |
|------|-------------|
| General | Fully customizable fields |
| Clinical Chemistry | Template-based with custom fields |
| Hematology | Template-based |
| Hormones | Template-based |
| Microbiology | 4 core fields + 33 antibiotics |
| Semen Analysis | Full morphology + motility grading |
| Urine Analysis | Two-column layout |
| Stool Analysis | Core fields + parasites |
| Serology / Virology | Template-based |
| Tumor Markers | Template-based |
| Lab Report | Title + free-text content |

### 📄 PDF Generation
- Individual PDF reports per analysis
- Comprehensive PDF combining all standard analyses for one patient
- Professional header/footer with lab logo and watermark
- Arabic text support (names, comments, footer)
- Direct print via Adobe Acrobat

### ⚙️ Template Settings
- Edit field names, units, and normal ranges per template
- Set result fields as **Text** or **Dropdown** with custom options
- Set normal range as **Text** or **Dropdown** (e.g. `male: 13.5`, `female: 12.5`, `child: 11.0`)
- Auto-fill normal range based on patient age and gender

### 📊 Statistics
- Monthly patient and analysis counts
- Breakdown by analysis type with visual bar chart

### 🗂️ Reports Page
- Search by patient name or ID number
- Filter by month
- View, Edit, Delete, and History actions per report

### 🖥️ UI / UX
- Screensaver after 15 seconds of inactivity (patient form only)
- Existing patient search with auto-fill from navbar
- Dynamic tabs for multiple simultaneous analyses

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python / Flask |
| Database | SQLite |
| PDF Generation | ReportLab |
| Arabic Support | arabic-reshaper, python-bidi |
| Frontend | HTML, CSS, JavaScript |

---

## 📁 Project Structure

```
Lap_System/
├── app.py
├── config.py
├── models/
│   ├── database.py
│   └── schema.py
├── routes/
│   ├── patients.py        # Patient & analysis routes
│   ├── reports.py         # Reports list & delete
│   ├── settings.py        # Template settings
│   ├── stats.py           # Statistics
│   └── doctors.py         # Doctor management
├── services/
│   ├── pdf_service.py     # PDF generation engine
│   └── template_service.py
├── templates/             # HTML templates
├── static/
│   ├── css/
│   └── img/
│       ├── header.png
│       └── WaterMark.png
└── pdf_reports/           # Generated PDFs (YYYY/MM/)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/Lap_System.git
cd Lap_System

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

The app will be available at `http://127.0.0.1:5000`

---

## 📌 Notes

- PDF files are saved under `pdf_reports/YYYY/MM/`
- Patient names are sanitized before use in file paths (Windows-safe)
- Comprehensive PDF is generated automatically when a patient has 2+ standard analyses
- Standalone analyses (Urine, Semen, Stool, Microbiology, Lab Report) are excluded from Comprehensive PDF

---

## 📷 Screenshots

> Coming soon

---

## 📄 License

This project is proprietary. All rights reserved.
