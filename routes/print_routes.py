"""
===============================================
Routes الخاصة بالطباعة والـ PDF
===============================================
يحتوي على:
- فتح ملف PDF المحفوظ (open_pdf)
- صفحة الطباعة (print_report)
"""

from flask import Blueprint, render_template, send_file
from models.database import getdb
from config import PDF_OUTPUT_DIR, DB_NAME

# =======================================
# إنشاء Blueprint للطباعة
# =======================================
print_bp = Blueprint('print', __name__)


@print_bp.route("/PDF_OUTPUT_DIR/<int:report_id>")
def open_pdf(report_id):
    """
    فتح ملف PDF المحفوظ
    
    Parameters:
    -----------
    report_id: int
        معرف التحليل (analysis_id)
    
    Returns:
    --------
    ملف PDF للعرض في المتصفح
    
    ملاحظة:
    --------
    ✅ تغيير: نجيب pdf_path من جدول analysis_instances
    """
    
    # =======================================
    # فتح اتصال بقاعدة البيانات
    # =======================================
    conn = getdb()
    cur = conn.cursor()
    
    # =======================================
    # جلب مسار ملف PDF
    # =======================================
    # ✅ تغيير: من جدول analysis_instances بدل patients
    cur.execute("""
        SELECT pdf_path 
        FROM analysis_instances 
        WHERE id = ?
    """, (report_id,))
    
    result = cur.fetchone()
    
    # =======================================
    # إغلاق الاتصال
    # =======================================
    conn.close()
    
    # =======================================
    # إرسال ملف PDF
    # =======================================
    if result and result[0]:
        return send_file(
            result[0],
            mimetype='application/pdf',
            as_attachment=False,  # عرض في المتصفح (مش تحميل)
            download_name=f'report_{report_id}.pdf'
        )

    # =======================================
    # إذا الملف غير موجود
    # =======================================
    return "PDF not found", 404


@print_bp.route("/print/<int:report_id>")
def print_report(report_id):
    """
    صفحة الطباعة
    """
    
    conn = getdb()
    cur = conn.cursor()

    # ✅ تعديل: إضافة custom_name
    cur.execute("""
        SELECT 
            p.patient_name,
            p.patient_id_number,
            p.phone,
            p.age,
            p.gender,
            p.doctor_name,
            COALESCE(a.custom_name, a.analysis_type) as analysis_display_name,
            a.created_at
        FROM analysis_instances a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.id = ?
    """, (report_id,))
    
    analysis = cur.fetchone()

    # جلب نتائج التحليل
    cur.execute("""
        SELECT field_name, field_value, unit, normal_range
        FROM results
        WHERE analysis_id = ?
    """, (report_id,))
    
    results = cur.fetchall()

    conn.close()

    return render_template("print.html", patient=analysis, results=results)

@print_bp.route("/print-single/<int:analysis_id>")
def print_single_report(analysis_id):
    """
    طباعة تقرير لتحليل واحد فقط
    
    Parameters:
    -----------
    analysis_id: int
        معرف التحليل
    """
    # نفس الكود الموجود في print_report
    # لكن لتحليل واحد فقط
    return print_report(analysis_id)


@print_bp.route("/print-comprehensive/<int:patient_id>")
def print_comprehensive_report(patient_id):
    """
    طباعة تقرير شامل لجميع تحاليل المريض
    """
    conn = getdb()
    cur = conn.cursor()

    # جلب بيانات المريض
    cur.execute("""
        SELECT patient_name, patient_id_number, phone, age, gender, doctor_name, created_at
        FROM patients
        WHERE id = ?
    """, (patient_id,))
    
    patient = cur.fetchone()

    # ✅ استثناء التحاليل المنفصلة
    STANDALONE_ANALYSES = ['URINE_ANALYSIS', 'SEMEN_ANALYSIS', 'STOOL_ANALYSIS', 'MICROBIOLOGY', 'LAP_REPORT']
    
    cur.execute("""
        SELECT 
            id, 
            COALESCE(custom_name, analysis_type) as analysis_display_name,
            analysis_type
        FROM analysis_instances
        WHERE patient_id = ?
        ORDER BY created_at
    """, (patient_id,))
    
    all_analyses = cur.fetchall()
    
    # ✅ فلترة: بس التحاليل العادية
    analyses_list = [a for a in all_analyses if a[2] not in STANDALONE_ANALYSES]
    
    analyses_list = cur.fetchall()
    
    # جلب نتائج كل تحليل
    all_results = []
    for analysis in analyses_list:
        analysis_id = analysis[0]
        analysis_name = analysis[1]  # ✅ هنا الاسم المعروض
        
        cur.execute("""
            SELECT field_name, field_value, unit, normal_range
            FROM results
            WHERE analysis_id = ?
        """, (analysis_id,))
        
        results = cur.fetchall()
        
        all_results.append({
            "analysis_type": analysis_name,  # ✅ استخدام الاسم المعروض
            "results": results
        })

    conn.close()

    return render_template("print_comprehensive.html", patient=patient, all_results=all_results)