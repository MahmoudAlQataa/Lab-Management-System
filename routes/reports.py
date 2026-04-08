"""
===============================================
Routes الخاصة بقائمة التقارير
===============================================
"""

import os
import glob
from flask import Blueprint, render_template, redirect, request
from models.database import getdb

reports_bp = Blueprint('reports', __name__)


@reports_bp.route("/reports")
def reports_list():
    """
    عرض قائمة جميع التقارير
    """
    
    conn = getdb()
    cur = conn.cursor()

    # ✅ تعديل: نستخدم COALESCE لعرض custom_name إذا موجود، وإلا analysis_type
    # فلتر التاريخ
    selected_month = request.args.get('month', '')

    if selected_month:
        month_pattern = f"{selected_month}-%"
        cur.execute("""
        SELECT 
            a.id,
            p.patient_name,
            p.patient_id_number,
            COALESCE(a.custom_name, a.analysis_type) as analysis_display_name,
            a.created_at,
            p.id as patient_id
        FROM analysis_instances a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.created_at LIKE ?
        ORDER BY a.id DESC
    """, (month_pattern,))
    else:
        cur.execute("""
        SELECT 
            a.id,
            p.patient_name,
            p.patient_id_number,
            COALESCE(a.custom_name, a.analysis_type) as analysis_display_name,
            a.created_at,
            p.id as patient_id
        FROM analysis_instances a
        JOIN patients p ON a.patient_id = p.id
        ORDER BY a.id DESC
    """)

    analyses = cur.fetchall()
    conn.close()

    return render_template("reports.html", patients=analyses, selected_month=selected_month)

@reports_bp.route("/delete-analysis/<int:analysis_id>", methods=["POST"])
def delete_analysis(analysis_id):
    """
    حذف تحليل فردي مع تحديث الـ Comprehensive
    """
    conn = getdb()
    cur = conn.cursor()

    # جلب معلومات التحليل قبل الحذف
    cur.execute("""
        SELECT a.analysis_type, a.pdf_path, a.patient_id, p.patient_name
        FROM analysis_instances a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.id = ?
    """, (analysis_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return "Analysis not found", 404

    analysis_type = row[0]
    pdf_path      = row[1]
    patient_id    = row[2]
    patient_name  = row[3]

    # حذف النتائج والتعليق
    cur.execute("DELETE FROM results WHERE analysis_id = ?", (analysis_id,))
    cur.execute("DELETE FROM lab_comments WHERE analysis_id = ?", (analysis_id,))
    cur.execute("DELETE FROM analysis_instances WHERE id = ?", (analysis_id,))

    # فحص كم تحليل عادي تبقى للمريض
    STANDALONE_ANALYSES = ['URINE_ANALYSIS', 'SEMEN_ANALYSIS', 'STOOL_ANALYSIS', 'MICROBIOLOGY', 'LAP_REPORT']
    cur.execute("""
        SELECT COUNT(*) FROM analysis_instances
        WHERE patient_id = ? AND analysis_type NOT IN
        ('URINE_ANALYSIS','SEMEN_ANALYSIS','STOOL_ANALYSIS','MICROBIOLOGY','LAP_REPORT')
    """, (patient_id,))
    remaining_normal = cur.fetchone()[0]

    conn.commit()
    conn.close()

    # حذف PDF الفردي
    old_pattern = os.path.join('pdf_reports', '**', f"*_{analysis_id}.pdf")
    for f in glob.glob(old_pattern, recursive=True):
        if 'comprehensive' not in os.path.basename(f):
            try:
                os.remove(f)
            except:
                pass

    # تحديث Comprehensive
    if analysis_type not in STANDALONE_ANALYSES:
        pname_clean = patient_name.replace(" ", "_")
        import re
        pname_clean = re.sub(r'[\\/:*?"<>|]', '', pname_clean)

        # حذف الـ Comprehensive القديم
        comp_pattern = os.path.join('pdf_reports', '**', f"{pname_clean}_comprehensive_{patient_id}.pdf")
        for f in glob.glob(comp_pattern, recursive=True):
            try:
                os.remove(f)
            except:
                pass

        # إعادة توليد فقط إذا تبقى 2+ تحاليل عادية
        if remaining_normal >= 2:
            from services.pdf_service import generate_comprehensive_pdf
            generate_comprehensive_pdf(patient_id)

    return redirect("/reports")