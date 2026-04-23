"""
===============================================
Routes الخاصة بالاحصائيات (Statistics)
===============================================
"""

from flask import Blueprint, render_template, request
from models.database import getdb
from datetime import datetime
from config import DB_NAME

# =======================================
# إنشاء Blueprint للإحصائيات
# =======================================
stats_bp = Blueprint('stats', __name__)

@stats_bp.route("/stats")
def view_stats():
    """
    عرض إحصائيات النظام (عدد المرضى والتحاليل للشهر المحدد أو الحالي)
    """
    conn = getdb()
    cur = conn.cursor()

    # جلب الشهر المحدد من الرابط (إذا تم اختياره)
    selected_month = request.args.get('month')

    if not selected_month:
        # إذا لم يتم تحديد شهر، استخدم الشهر الحالي بصيغة YYYY-MM
        selected_month = datetime.now().strftime("%Y-%m")

    # =======================================
    # منطق החישוב:
    # عدد المرضى = عدد المرضى المميزين (DISTINCT) 
    # في جدول التحاليل (analysis_instances) خلال هذا الشهر
    # =======================================
    # التاريخ مخزن بصيغة: YYYY-MM-DD HH:MM AM/PM
    # لذلك نستخدم LIKE 'YYYY-MM-%' للبحث عن الشهر
    month_pattern = f"{selected_month}-%"

    cur.execute("""
        SELECT COUNT(DISTINCT 
            CASE 
                WHEN p.patient_id_number IS NOT NULL AND TRIM(p.patient_id_number) != '' THEN TRIM(p.patient_id_number)
                ELSE TRIM(p.patient_name) || '_' || p.age || '_' || p.gender
            END
        ) 
        FROM analysis_instances a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.created_at LIKE ?
    """, (month_pattern,))
    patients_count_row = cur.fetchone()
    patients_count = patients_count_row[0] if patients_count_row else 0

    # =======================================
    # عدد التحاليل الإجمالي
    # =======================================
    cur.execute("""
        SELECT COUNT(id) 
        FROM analysis_instances 
        WHERE created_at LIKE ?
    """, (month_pattern,))
    analyses_count_row = cur.fetchone()
    analyses_count = analyses_count_row[0] if analyses_count_row else 0

    # =======================================
    # عدد كل نوع تحليل بشكل منفصل
    # =======================================
    cur.execute("""
        SELECT 
            COALESCE(custom_name, analysis_type) as display_name,
            COUNT(*) as count
        FROM analysis_instances
        WHERE created_at LIKE ?
        GROUP BY display_name
        ORDER BY count DESC
    """, (month_pattern,))
    analyses_breakdown = cur.fetchall()

    conn.close()

    return render_template(
        "stats.html", 
        selected_month=selected_month,
        patients_count=patients_count,
        analyses_count=analyses_count,
        analyses_breakdown=analyses_breakdown
    )