import os
import sys

# ============================================================
# تحديد المجلد الجذر للبرنامج
# sys.executable = مسار الـ exe عند التشغيل كبرنامج
# __file__       = مسار الـ .py عند التشغيل العادي للتطوير
# ============================================================
if getattr(sys, 'frozen', False):
    # نحن داخل PyInstaller exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # نحن في بيئة التطوير العادية
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# مجلد البيانات — بجانب الـ exe، منفصل عن البرنامج
# ============================================================
DATA_DIR = os.path.join(BASE_DIR, "LapData")

# إعدادات قاعدة البيانات
DB_NAME = os.path.join(DATA_DIR, "lap.db")

# ============================================================
# مسارات الملفات الثابتة (static)
# داخل الـ exe تكون في _internal/static/...
# ============================================================
if getattr(sys, 'frozen', False):
    STATIC_DIR = os.path.join(sys._MEIPASS, "static")
else:
    STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

FONT_PATH = os.path.join(STATIC_DIR, "fonts", "Arial.ttf")
HEADER_IMAGE_PATH = os.path.join(STATIC_DIR, "img", "ترويسة.png")
PDF_OUTPUT_DIR = os.path.join(DATA_DIR, "pdf_reports")

# إعدادات Flask
DEBUG_MODE = False
USE_RELOADER = False

# إنشاء المجلدات تلقائياً
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)