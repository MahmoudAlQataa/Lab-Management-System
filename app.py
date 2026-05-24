#########################
# ملف التطبيق الرئيسي #
#########################

import sys
from flask import Flask
from config import DATA_DIR
from client_config import (
    LAB_NAME_EN, LAB_NAME_AR, LAB_PHONE,
    LAB_ADDRESS, LAB_LICENSE, PRIMARY_COLOR
)
import os

# استيراد الـ routes
from routes.patients import patients_bp
from routes.reports import reports_bp
from routes.print_routes import print_bp
from routes.doctors import doctors_bp  
from routes.settings import settings_bp
from routes.stats import stats_bp

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    template_folder = os.path.join(base_path, 'templates')
    static_folder = os.path.join(base_path, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

# تسجيل الـ Blueprints
app.register_blueprint(patients_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(print_bp)
app.register_blueprint(doctors_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(stats_bp)

@app.context_processor
def inject_lab_info():
    return dict(
        lab_name_en=LAB_NAME_EN,
        lab_name_ar=LAB_NAME_AR,
        lab_phone=LAB_PHONE,
        lab_address=LAB_ADDRESS,
        lab_license=LAB_LICENSE,
        primary_color=PRIMARY_COLOR,
    )

@app.route("/")
def home():
    return 'Lab System is Running 🏥'


def initialize():
    # التأكد من وجود مجلد البيانات قبل أي شي
    os.makedirs(DATA_DIR, exist_ok=True)
    # =======================================
    # إنشاء قاعدة البيانات والبيانات الأولية
    # =======================================
    from models.schema import init_database
    from services.template_service import seed_templates
    from services.seed_doctors import seed_doctors
    # إنشاء الجداول
    init_database()
    
    # إضافة القوالب
    seed_templates()
    
    # إضافة الأطباء ✅ جديد
    seed_doctors()
    
if __name__ == "__main__":
    initialize()
    # =======================================
    # تشغيل التطبيق
    # =======================================
    app.run(debug=False, use_reloader=False)