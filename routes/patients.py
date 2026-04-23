"""
===============================================
Routes الخاصة بإدارة المرضى
===============================================
يحتوي على:
- إضافة تقرير جديد (new_report)
- عرض تقرير محدد (view_report)
"""

import json
from datetime import datetime
import os
from config import PDF_OUTPUT_DIR, DB_NAME
import glob
from flask import Blueprint, render_template, request, redirect
from models.database import getdb
from services.pdf_service import generate_pdf

# =======================================
# إنشاء Blueprint للمرضى
# =======================================
# Blueprint يسمح لنا بتنظيم الـ routes في ملفات منفصلة
patients_bp = Blueprint('patients', __name__)


@patients_bp.route("/search-patients")
def search_patients():
    """البحث عن مريض موجود"""
    from flask import jsonify
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])

    conn = getdb()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT p.id, p.patient_name, p.patient_id_number, p.age, p.gender, p.phone, p.doctor_name
        FROM patients p
        WHERE p.patient_name LIKE ? OR p.patient_id_number LIKE ?
        ORDER BY p.id DESC
        LIMIT 10
    """, (f"%{query}%", f"%{query}%"))
    rows = cur.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "name": r[1],
            "id_number": r[2] or "",
            "age": r[3] or "",
            "gender": r[4] or "",
            "phone": r[5] or "",
            "doctor": r[6] or ""
        })
    return jsonify(results)


@patients_bp.route("/patient/<int:patient_id>")
def patient_history(patient_id):
    """صفحة تاريخ المريض"""
    conn = getdb()
    cur = conn.cursor()

    cur.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cur.fetchone()
    if not patient:
        conn.close()
        return "Patient not found", 404

    cur.execute("""
        SELECT id, COALESCE(custom_name, analysis_type) as display_name,
               analysis_type, created_at, pdf_path
        FROM analysis_instances
        WHERE patient_id = ?
        ORDER BY id DESC
    """, (patient_id,))
    analyses = cur.fetchall()
    conn.close()

    return render_template("patient_history.html", patient=patient, analyses=analyses)


@patients_bp.route("/new-report", methods=["GET", "POST"])
def new_report():
    """
    صفحة إضافة تقرير جديد
    
    التحديثات:
    -----------
    ✅ دعم التحاليل المتعددة
    ✅ معالجة كل تحليل بشكل منفصل
    ✅ توليد PDF لكل تحليل
    """
    
    # =======================================
    # معالجة POST (عند إرسال الفورم)
    # =======================================
    if request.method == "POST":
        
        # =======================================
        # الخطوة 1: جمع بيانات المريض
        # =======================================
        patient_data = {
            "name": request.form.get("name"),
            "patient_id_number": request.form.get("patient_id_number"),
            "phone": request.form.get("phone"),
            "age": request.form.get("age"),
            "gender": request.form.get("gender"),
            "doctor_name": request.form.get("doctor_name"),
        }
        sample_date = request.form.get("sample_date", "").strip() or datetime.now().strftime("%Y-%m-%d")

        # =======================================
        # الخطوة 2: جمع التحاليل المحددة
        # =======================================
        # ✅ جديد: selected_analyses هي قائمة بأسماء التحاليل
        selected_analyses = request.form.getlist("selected_analyses")
        
        # التحقق من وجود تحاليل محددة
        if not selected_analyses:
            return "Please select at least one analysis type", 400

        # =======================================
        # فتح اتصال بقاعدة البيانات
        # =======================================
        conn = getdb()
        cur = conn.cursor()

        # =======================================
        # الخطوة 3: إضافة المريض أو استخدام موجود
        # =======================================
        created_at = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        existing_patient_id = request.form.get("existing_patient_id", "").strip()

        if existing_patient_id:
            # ✅ مريض موجود - تحديث بياناته وربط التحاليل به
            patient_id = int(existing_patient_id)
            cur.execute("""
                UPDATE patients SET
                    patient_name = ?, patient_id_number = ?, phone = ?,
                    gender = ?, age = ?, doctor_name = ?
                WHERE id = ?
            """, (
                patient_data["name"], patient_data["patient_id_number"],
                patient_data["phone"], patient_data["gender"],
                patient_data["age"], patient_data["doctor_name"],
                patient_id
            ))
        else:
            # ✅ مريض جديد
            cur.execute("""
                INSERT INTO patients
                (patient_name, patient_id_number, phone, gender, age, doctor_name, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_data["name"], patient_data["patient_id_number"],
                patient_data["phone"], patient_data["gender"],
                patient_data["age"], patient_data["doctor_name"],
                created_at
            ))
            patient_id = cur.lastrowid
        
        print(f"✅ Patient created with ID: {patient_id}")
        print(f"📋 Selected analyses: {selected_analyses}")

        # =======================================
        # الخطوة 4: معالجة كل تحليل
        # =======================================
        analysis_ids = []  # لحفظ IDs التحاليل
        
        for analysis_type in selected_analyses:
            print(f"\n🔬 Processing {analysis_type}...")
            
            # =======================================
            # ✅ معالجة خاصة للقالب العام
            # =======================================
            if analysis_type.upper() == 'GENERAL':
                print("   📝 Processing GENERAL template...")
                
                # ✅ جديد: جلب الاسم المخصص
                custom_name = request.form.get("GENERAL_custom_name", "").strip()
                if not custom_name:
                    custom_name = "General Report"  # اسم افتراضي
                
                print(f"   📌 Custom name: {custom_name}")
                
                results_data = []
                
                # جمع كل الحقول الديناميكية
                # البحث عن كل الحقول بصيغة: GENERAL_field_name_1, GENERAL_field_name_2, ...
                field_counter = 1
                while True:
                    field_name_key = f"GENERAL_field_name_{field_counter}"
                    field_value_key = f"GENERAL_field_value_{field_counter}"
                    field_unit_key = f"GENERAL_field_unit_{field_counter}"
                    field_range_key = f"GENERAL_field_range_{field_counter}"
                    
                    # جلب القيم من الفورم
                    field_name = request.form.get(field_name_key, "").strip()
                    field_value = request.form.get(field_value_key, "").strip()
                    field_unit = request.form.get(field_unit_key, "").strip()
                    field_range = request.form.get(field_range_key, "").strip()
                    
                    # إذا ما في اسم حقل، معناه خلصنا الحقول
                    if not field_name:
                        break
                    
                    # حفظ فقط إذا في قيمة
                    if field_value:
                        results_data.append({
                            "field_name": field_name,
                            "field_value": field_value,
                            "unit": field_unit,
                            "normal_range": field_range
                        })
                        print(f"      ✓ {field_name}: {field_value} {field_unit}")
                    
                    field_counter += 1
                
                print(f"   📊 Found {len(results_data)} custom fields")
            
            # =======================================
            # معالجة القوالب العادية
            # =======================================
            else:
                # --------------------------------------
                # 4.1: جلب قالب التحليل
                # --------------------------------------
                cur.execute("""
                    SELECT fields
                    FROM analysis_templates
                    WHERE analysis_name = ?
                """, (analysis_type.upper(),))
                
                template_row = cur.fetchone()
                
                if not template_row:
                    print(f"⚠️ Template not found for {analysis_type}")
                    continue
                
                template_fields = json.loads(template_row[0])

                # --------------------------------------
                # 4.2: جمع نتائج هذا التحليل
                # --------------------------------------
                results_data = []
                
                for field in template_fields:
                    field_name = field["name"]
                    
                    value_key = f"{analysis_type}_{field_name}"
                    unit_key = f"{analysis_type}_{field_name}_unit"
                    range_key = f"{analysis_type}_{field_name}_range"
                    
                    value = request.form.get(value_key, "").strip()
                    unit = request.form.get(unit_key, "").strip()
                    normal_range = request.form.get(range_key, "").strip()
                    
                    # استخدام القيمة من القالب إذا ما كانت معبّاة
                    if not unit:
                        unit = field.get("unit", "")
                    if not normal_range:
                        normal_range = field.get("normal_range", "")
                    
                    if value:
                        results_data.append({
                            "field_name": field_name,
                            "field_value": value,
                            "unit": unit,
                            "normal_range": normal_range
                        })
                
                print(f"   📊 Found {len(results_data)} results")
            

            # --------------------------------------
            # 4.3: إضافة التحليل
            # --------------------------------------
            # ✅ جديد: إضافة custom_name للقالب العام
            if analysis_type.upper() == 'GENERAL':
                cur.execute("""
                    INSERT INTO analysis_instances
                    (patient_id, analysis_type, custom_name, created_at, sample_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (patient_id, analysis_type, custom_name, created_at, sample_date))
            else:
                cur.execute("""
                    INSERT INTO analysis_instances
                    (patient_id, analysis_type, created_at, sample_date)
                    VALUES (?, ?, ?, ?)
                """, (patient_id, analysis_type, created_at, sample_date))

            analysis_id = cur.lastrowid
            analysis_ids.append(analysis_id)
            print(f"   ✅ Analysis created with ID: {analysis_id}")

            # --------------------------------------
            # 4.4: حفظ النتائج
            # --------------------------------------
            for result in results_data:
                cur.execute("""
                    INSERT INTO results (analysis_id, field_name, field_value, unit, normal_range, field_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (analysis_id, result["field_name"], result["field_value"], 
                      result["unit"], result["normal_range"], "template"))
            
            print(f"   ✅ Saved {len(results_data)} template results")
            
            # --------------------------------------
            # ✅ 4.5: حفظ Custom Fields
            # --------------------------------------
            custom_field_counter = 1
            while True:
                name_key = f"{analysis_type}_custom_name_{custom_field_counter}"
                value_key = f"{analysis_type}_custom_value_{custom_field_counter}"
                unit_key = f"{analysis_type}_custom_unit_{custom_field_counter}"
                range_key = f"{analysis_type}_custom_range_{custom_field_counter}"
                
                field_name = request.form.get(name_key, "").strip()
                field_value = request.form.get(value_key, "").strip()
                field_unit = request.form.get(unit_key, "").strip()
                field_range = request.form.get(range_key, "").strip()
                
                if not field_name:
                    break
                
                if field_value:  # حفظ فقط إذا في قيمة
                    cur.execute("""
                        INSERT INTO results (analysis_id, field_name, field_value, unit, normal_range, field_type)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (analysis_id, field_name, field_value, field_unit, field_range, "custom"))
                    print(f"      ✓ Custom: {field_name}: {field_value}")
                
                custom_field_counter += 1
            
            # --------------------------------------
            # ✅ 4.6: حفظ Lab Comment
            # --------------------------------------
            lab_comment_key = f"{analysis_type}_lab_comment"
            lab_comment = request.form.get(lab_comment_key, "").strip()
            
            if lab_comment:
                cur.execute("""
                    INSERT INTO lab_comments (analysis_id, comment)
                    VALUES (?, ?)
                """, (analysis_id, lab_comment))
                print(f"   💬 Lab Comment saved")

        # =======================================
        # حفظ التغييرات
        # =======================================
        conn.commit()
        conn.close()

        # =======================================
        # الخطوة 5: توليد PDF لكل تحليل
        # =======================================
        print(f"\n📄 Generating PDFs...")
        for analysis_id in analysis_ids:
            pdf_path = generate_pdf(analysis_id)
            if pdf_path:
                print(f"   ✅ PDF created: {pdf_path}")
                
        # =======================================
        # ✅ الخطوة 6: توليد Comprehensive PDF
        # =======================================
        from services.pdf_service import generate_comprehensive_pdf
        
        # فحص: هل في تحاليل عادية؟
        STANDALONE_ANALYSES = ['URINE_ANALYSIS', 'SEMEN_ANALYSIS', 'STOOL_ANALYSIS', 'MICROBIOLOGY', 'LAP_REPORT']
        normal_analyses = [a for a in selected_analyses if a not in STANDALONE_ANALYSES]
        
        if len(normal_analyses) >= 2:  # ✅ تحليلين عاديين أو أكثر
            comprehensive_pdf = generate_comprehensive_pdf(patient_id)
            if comprehensive_pdf:
                print(f"   ✅ Comprehensive PDF created: {comprehensive_pdf}")

        # =======================================
        # عرض صفحة النجاح
        # =======================================
        
        # ✅ جديد: جلب التحليل النشط من الفورم
        active_analysis_name = request.form.get("active_analysis", "")
        
        # =======================================
        # تجهيز البيانات لصفحة النجاح
        # =======================================
        
        # ✅ إنشاء قائمة بكل التحاليل مع IDs
        analyses_list = []
        for idx, analysis_type in enumerate(selected_analyses):
            analyses_list.append({
                "id": analysis_ids[idx],
                "name": analysis_type,
                "is_active": analysis_type == active_analysis_name
            })
        
        return render_template(
            "success.html", 
            patient_id=patient_id,
            patient=patient_data,
            analyses_list=analyses_list,  # ✅ القائمة الكاملة
            analyses_count=len(analysis_ids)
        )

    # =======================================
    # معالجة GET (عرض الفورم)
    # =======================================
    
    # جلب البيانات للواجهة
    conn = getdb()
    cur = conn.cursor()
    
    # جلب قائمة الأطباء
    cur.execute("""
        SELECT doctor_name 
        FROM doctors 
        WHERE is_active = 1
        ORDER BY doctor_name
    """)
    doctors = [row[0] for row in cur.fetchall()]
    
    # جلب جميع القوالب
    cur.execute("""
        SELECT analysis_name, fields
        FROM analysis_templates
        ORDER BY analysis_name
    """)
    
    templates_data = {}
    for row in cur.fetchall():
        analysis_name = row[0]
        fields = json.loads(row[1])
        templates_data[analysis_name] = fields
    
    conn.close()
    
    # إرسال البيانات للواجهة
    return render_template(
        "patient_form.html", 
        doctors=doctors,
        templates=templates_data
    )
    
 
@patients_bp.route("/reports/<int:report_id>")
def view_report(report_id):
    """
    عرض تقرير محدد
    """
    conn = getdb()
    cur = conn.cursor()

    # ✅ جلب بيانات التحليل + analysis_type
    cur.execute("""
        SELECT 
            a.id,
            p.patient_name,
            p.patient_id_number,
            p.phone,
            p.age,
            p.gender,
            p.doctor_name,
            COALESCE(a.custom_name, a.analysis_type) as analysis_display_name,
            a.created_at,
            a.patient_id,
            a.analysis_type
        FROM analysis_instances a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.id = ?
    """, (report_id,))
    
    analysis = cur.fetchone()
    
    if not analysis:
        return "Report not found", 404
    
    patient_id = analysis[9]
    analysis_type = analysis[10]  # ✅ analysis_type

    # جلب كل تحاليل المريض
    cur.execute("""
        SELECT 
            id, 
            COALESCE(custom_name, analysis_type) as display_name,
            analysis_type
        FROM analysis_instances
        WHERE patient_id = ?
        ORDER BY created_at
    """, (patient_id,))
    
    all_analyses = cur.fetchall()
    
    # ✅ فصل التحاليل العادية عن المنفصلة
    STANDALONE_ANALYSES = ['URINE_ANALYSIS', 'SEMEN_ANALYSIS', 'STOOL_ANALYSIS', 'MICROBIOLOGY', 'LAP_REPORT']
    
    normal_analyses = [a for a in all_analyses if a[2] not in STANDALONE_ANALYSES]
    
    # يظهر Print All بس إذا في 2 تحاليل عادية أو أكثر
    show_print_all = len(normal_analyses) >= 2

    # =======================================
    # ✅ عرض النتائج حسب نوع التحليل
    # =======================================
    SHOW_ALL_FIELDS = ['URINE_ANALYSIS', 'SEMEN_ANALYSIS', 'STOOL_ANALYSIS']
    
    # جلب النتائج المحفوظة لهذا التحليل فقط
    cur.execute("""
        SELECT field_name, field_value, unit, normal_range, field_type
        FROM results
        WHERE analysis_id = ?
        ORDER BY 
            CASE 
                WHEN field_type = 'template' THEN 1 
                WHEN field_type = 'custom' THEN 2 
            END,
            id
    """, (report_id,))
    
    saved_results = cur.fetchall()
    
    # إذا التحليل يعرض كل الحقول
    if analysis_type in SHOW_ALL_FIELDS:
        # جلب قالب التحليل
        cur.execute("""
            SELECT fields
            FROM analysis_templates
            WHERE analysis_name = ?
        """, (analysis_type,))
        
        template_row = cur.fetchone()
        
        if template_row:
            template_fields = json.loads(template_row[0])
            
            # بناء dictionary من النتائج المحفوظة (template فقط)
            saved_dict = {}
            for r in saved_results:
                if r[4] == 'template':  # field_type
                    saved_dict[r[0]] = r  # field_name -> row
            
            # بناء قائمة النتائج الكاملة
            results = []
            
            # إضافة كل حقول القالب
            for field in template_fields:
                field_name = field["name"]
                
                if field_name in saved_dict:
                    # حقل موجود - استخدم القيمة المحفوظة
                    results.append(saved_dict[field_name])
                else:
                    # حقل فارغ - أضف صف فارغ
                    results.append((
                        field_name,
                        "",
                        field.get("unit", ""),
                        field.get("normal_range", ""),
                        "template"
                    ))
            
            # إضافة Custom Fields
            for r in saved_results:
                if r[4] == 'custom':
                    results.append(r)
        else:
            results = saved_results
    else:
        # تحليل عادي - فقط المحفوظ
        results = saved_results
    
    # ✅ جلب Lab Comment
    cur.execute("""
        SELECT comment
        FROM lab_comments
        WHERE analysis_id = ?
    """, (report_id,))
    
    lab_comment_row = cur.fetchone()
    lab_comment = lab_comment_row[0] if lab_comment_row else None

    conn.close()

    return render_template(
        "report_view.html", 
        patient=analysis, 
        results=results,
        patient_id=patient_id,
        all_analyses=all_analyses,
        lab_comment=lab_comment,
        show_print_all=show_print_all  
    )
    
# =======================================
# عرض ملف pdf مباشرة
# هذا الـ route يسمح بعرض ملف PDF في المتصفح بدلاً من تحميله
# =======================================
@patients_bp.route("/view-pdf/<path:filename>")
def view_pdf(filename):
    """
    عرض ملف PDF مباشرة
    """
    from flask import send_file
    import os
    
    # المسار الكامل للملف
    pdf_path = os.path.join('PDF_OUTPUT_DIR', filename)
    
    if os.path.exists(pdf_path):
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=False,  # فتح في المتصفح/Acrobat
            download_name=os.path.basename(pdf_path)
        )
    else:
        return "PDF not found", 404



@patients_bp.route("/pdf/analysis/<int:analysis_id>")
def serve_analysis_pdf(analysis_id):
    """
    فتح PDF تحليل فردي
    """
    import os
    import subprocess
    import platform
    from models.database import getdb
    
    conn = getdb()
    cur = conn.cursor()
    
    # جلب مسار الـ PDF
    cur.execute("SELECT pdf_path FROM analysis_instances WHERE id = ?", (analysis_id,))
    result = cur.fetchone()
    conn.close()
    
    if result and result[0] and os.path.exists(result[0]):
        pdf_path = os.path.abspath(result[0])
        
        # ✅ فتح الملف بالبرنامج الافتراضي (Acrobat)
        try:
            if platform.system() == 'Windows':
                os.startfile(pdf_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', pdf_path])
            else:  # Linux
                subprocess.call(['xdg-open', pdf_path])
            
            return """<html><body><script>window.close();</script></body></html>"""
        except Exception as e:
            return f"Error opening PDF: {str(e)}", 500
    else:
        return "PDF not found", 404


@patients_bp.route("/pdf/comprehensive/<int:patient_id>")
def serve_comprehensive_pdf(patient_id):
    """
    فتح PDF شامل
    """
    import os
    import subprocess
    import platform
    from models.database import getdb
    from datetime import datetime
    
    conn = getdb()
    cur = conn.cursor()
    
    # جلب اسم المريض
    cur.execute("SELECT patient_name FROM patients WHERE id = ?", (patient_id,))
    patient = cur.fetchone()
    conn.close()
    
    if not patient:
        return "Patient not found", 404
    
    # بناء اسم الملف
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    
    patient_name = patient[0].replace(" ", "_")
    pdf_filename = f"{patient_name}_comprehensive_{patient_id}.pdf"
    pdf_path = os.path.join(PDF_OUTPUT_DIR, year, month, pdf_filename)
    pdf_path = os.path.abspath(pdf_path)
    
    if os.path.exists(pdf_path):
        # ✅ فتح الملف بالبرنامج الافتراضي (Acrobat)
        try:
            if platform.system() == 'Windows':
                os.startfile(pdf_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', pdf_path])
            else:  # Linux
                subprocess.call(['xdg-open', pdf_path])
            
            return """<html><body><script>window.close();</script></body></html>"""
        except Exception as e:
            return f"Error opening PDF: {str(e)}", 500
    else:
        return "Comprehensive PDF not found. Make sure you have 2+ standard analyses.", 404

@patients_bp.route("/edit-report/<int:analysis_id>", methods=["GET", "POST"])
def edit_report(analysis_id):
    """
    تعديل تقرير موجود
    """
    conn = getdb()
    cur = conn.cursor()

    if request.method == "POST":
        patient_id = request.form.get("patient_id", type=int)

        # جلب الاسم القديم قبل التحديث
        cur.execute("SELECT patient_name FROM patients WHERE id = ?", (patient_id,))
        old_name_row = cur.fetchone()
        old_patient_name = old_name_row[0] if old_name_row else ""
        new_patient_name = request.form.get("name", "").strip()
        name_changed = old_patient_name != new_patient_name
        sample_date = request.form.get("sample_date", "").strip() or datetime.now().strftime("%Y-%m-%d")

        # جلب كل بيانات المريض القديمة للمقارنة
        cur.execute("SELECT age, gender, doctor_name FROM patients WHERE id = ?", (patient_id,))
        old_data_row = cur.fetchone()
        old_age    = old_data_row[0] if old_data_row else ""
        old_gender = old_data_row[1] if old_data_row else ""
        old_doctor = old_data_row[2] if old_data_row else ""

        patient_data_changed = (
            name_changed or
            old_age    != request.form.get("age", "").strip() or
            old_gender != request.form.get("gender", "").strip() or
            old_doctor != request.form.get("doctor_name", "").strip()
        )

        # =======================================
        # 1. تحديث بيانات المريض
        # =======================================
        cur.execute("""
            UPDATE patients SET
                patient_name = ?, patient_id_number = ?, phone = ?,
                age = ?, gender = ?, doctor_name = ?
            WHERE id = ?
        """, (
            request.form.get("name", "").strip(),
            request.form.get("patient_id_number", "").strip(),
            request.form.get("phone", "").strip(),
            request.form.get("age", "").strip(),
            request.form.get("gender", "").strip(),
            request.form.get("doctor_name", "").strip(),
            patient_id
        ))

        # =======================================
        # 2. جلب نوع التحليل والـ PDF القديم
        # =======================================
        cur.execute("SELECT analysis_type, pdf_path FROM analysis_instances WHERE id = ?", (analysis_id,))
        analysis_row = cur.fetchone()
        analysis_type = analysis_row[0]
        old_pdf_path = analysis_row[1]

        
        if analysis_type.upper() == 'GENERAL':
            custom_name = request.form.get("custom_name", "").strip() or "General Report"
            cur.execute("UPDATE analysis_instances SET custom_name = ?, sample_date = ? WHERE id = ?", (custom_name, sample_date, analysis_id))
        else:
            cur.execute("UPDATE analysis_instances SET sample_date = ? WHERE id = ?", (sample_date, analysis_id))

        # =======================================
        # 3. جمع معلومات Comprehensive قبل الإغلاق
        # =======================================
        STANDALONE_ANALYSES = ['URINE_ANALYSIS', 'SEMEN_ANALYSIS', 'STOOL_ANALYSIS', 'MICROBIOLOGY', 'LAP_REPORT']
        needs_comprehensive = analysis_type not in STANDALONE_ANALYSES
        pat_id_for_comp = None
        pname_for_comp = None
        comp_count = 0

        if needs_comprehensive:
            pat_id_for_comp = patient_id
            cur.execute("SELECT patient_name FROM patients WHERE id = ?", (pat_id_for_comp,))
            pname_row = cur.fetchone()
            if pname_row:
                pname_for_comp = pname_row[0]

            cur.execute("""
                SELECT COUNT(*) FROM analysis_instances
                WHERE patient_id = ? AND analysis_type NOT IN
                ('URINE_ANALYSIS','SEMEN_ANALYSIS','STOOL_ANALYSIS','MICROBIOLOGY','LAP_REPORT')
            """, (pat_id_for_comp,))
            comp_count = cur.fetchone()[0]

        # =======================================
        # 4. حذف النتائج والتعليق القديم
        # =======================================
        cur.execute("DELETE FROM results WHERE analysis_id = ?", (analysis_id,))
        cur.execute("DELETE FROM lab_comments WHERE analysis_id = ?", (analysis_id,))

        # =======================================
        # 5. حفظ النتائج الجديدة
        # =======================================
        if analysis_type.upper() == 'GENERAL':
            i = 1
            while True:
                fname = request.form.get(f"field_name_{i}", "").strip()
                fval  = request.form.get(f"field_value_{i}", "").strip()
                funit = request.form.get(f"field_unit_{i}", "").strip()
                frange= request.form.get(f"field_range_{i}", "").strip()
                if not fname:
                    break
                if fval:
                    cur.execute(
                        "INSERT INTO results (analysis_id, field_name, field_value, unit, normal_range, field_type) VALUES (?,?,?,?,?,?)",
                        (analysis_id, fname, fval, funit, frange, "template")
                    )
                i += 1

        elif analysis_type.upper() == 'LAP_REPORT':
            title   = request.form.get("field_title", "").strip()
            content = request.form.get("field_content", "").strip()
            if title:
                cur.execute(
                    "INSERT INTO results (analysis_id, field_name, field_value, unit, normal_range, field_type) VALUES (?,?,?,?,?,?)",
                    (analysis_id, "title", title, "", "", "template")
                )
            if content:
                cur.execute(
                    "INSERT INTO results (analysis_id, field_name, field_value, unit, normal_range, field_type) VALUES (?,?,?,?,?,?)",
                    (analysis_id, "content", content, "", "", "template")
                )
        else:
            # Template-based analyses (URINE, SEMEN, STOOL, MICROBIOLOGY)
            cur.execute("SELECT fields FROM analysis_templates WHERE analysis_name = ?", (analysis_type,))
            trow = cur.fetchone()
            if trow:
                tfields = json.loads(trow[0])
                for field in tfields:
                    fname  = field["name"]
                    fval   = request.form.get(f"field_{fname}", "").strip()
                    funit  = request.form.get(f"unit_{fname}", field.get("unit", "")).strip()
                    frange = request.form.get(f"range_{fname}", field.get("normal_range", "")).strip()
                    if fval:
                        cur.execute(
                            "INSERT INTO results (analysis_id, field_name, field_value, unit, normal_range, field_type) VALUES (?,?,?,?,?,?)",
                            (analysis_id, fname, fval, funit, frange, "template")
                        )

            # Custom Fields
            i = 1
            while True:
                fname  = request.form.get(f"custom_name_{i}", "").strip()
                fval   = request.form.get(f"custom_value_{i}", "").strip()
                funit  = request.form.get(f"custom_unit_{i}", "").strip()
                frange = request.form.get(f"custom_range_{i}", "").strip()
                if not fname:
                    break
                if fval:
                    cur.execute(
                        "INSERT INTO results (analysis_id, field_name, field_value, unit, normal_range, field_type) VALUES (?,?,?,?,?,?)",
                        (analysis_id, fname, fval, funit, frange, "custom")
                    )
                i += 1

        # =======================================
        # 6. حفظ Lab Comment
        # =======================================
        lab_comment = request.form.get("lab_comment", "").strip()
        if lab_comment:
            cur.execute("INSERT INTO lab_comments (analysis_id, comment) VALUES (?, ?)", (analysis_id, lab_comment))

        # جلب IDs كل تحاليل المريض قبل إغلاق الاتصال
        cur.execute("SELECT id FROM analysis_instances WHERE patient_id = ?", (patient_id,))
        all_patient_analysis_ids = [r[0] for r in cur.fetchall()]

        conn.commit()
        conn.close()

        # =======================================
        # 7. حذف PDF القديم وتوليد جديد
        # =======================================
        # حذف التحليل الحالي
        old_pattern = os.path.join('PDF_OUTPUT_DIR', '**', f"*_{analysis_id}.pdf")
        for old_file in glob.glob(old_pattern, recursive=True):
            if 'comprehensive' not in os.path.basename(old_file):
                try:
                    os.remove(old_file)
                except Exception:
                    pass

        generate_pdf(analysis_id)

        # إذا تغير الاسم - نجدد كل تحاليل المريض الأخرى
        if patient_data_changed:
            for other_id in all_patient_analysis_ids:
                if other_id == analysis_id:
                    continue
                other_pattern = os.path.join('PDF_OUTPUT_DIR', '**', f"*_{other_id}.pdf")
                for old_file in glob.glob(other_pattern, recursive=True):
                    if 'comprehensive' not in os.path.basename(old_file):
                        try:
                            os.remove(old_file)
                        except Exception:
                            pass
                generate_pdf(other_id)

        # =======================================
        # 8. تحديث Comprehensive PDF
        # =======================================
        if patient_data_changed and not needs_comprehensive:
            # تعديل تقرير STANDALONE غيّر بيانات المريض → نجدد الـ Comprehensive لو موجود
            from services.pdf_service import generate_comprehensive_pdf
            for search_name in set([old_patient_name, new_patient_name]):
                pname_clean = search_name.replace(" ", "_")
                pattern = os.path.join('PDF_OUTPUT_DIR', '**', f"{pname_clean}_comprehensive_{patient_id}.pdf")
                for old_comp in glob.glob(pattern, recursive=True):
                    try:
                        os.remove(old_comp)
                    except Exception:
                        pass
            cur2 = getdb().cursor()
            cur2.execute("""
                SELECT COUNT(*) FROM analysis_instances
                WHERE patient_id = ? AND analysis_type NOT IN
                ('URINE_ANALYSIS','SEMEN_ANALYSIS','STOOL_ANALYSIS','MICROBIOLOGY','LAP_REPORT')
            """, (patient_id,))
            comp_count2 = cur2.fetchone()[0]
            cur2.connection.close()
            if comp_count2 >= 2:
                generate_comprehensive_pdf(patient_id)

        if needs_comprehensive and pat_id_for_comp:
            from services.pdf_service import generate_comprehensive_pdf

            # حذف الـ Comprehensive بالاسم القديم والجديد (الاثنين للأمان)
            for search_name in set([old_patient_name, new_patient_name]):
                pname_clean = search_name.replace(" ", "_")
                pattern = os.path.join('PDF_OUTPUT_DIR', '**', f"{pname_clean}_comprehensive_{pat_id_for_comp}.pdf")
                for old_comp in glob.glob(pattern, recursive=True):
                    try:
                        os.remove(old_comp)
                    except Exception:
                        pass

            if comp_count >= 2:
                generate_comprehensive_pdf(pat_id_for_comp)

        return redirect(f"/reports/{analysis_id}")

    # =======================================
    # GET - تجهيز بيانات الفورم
    # =======================================
    cur.execute("""
        SELECT a.id, a.analysis_type, a.custom_name, a.patient_id,
               p.patient_name, p.patient_id_number, p.phone, p.age, p.gender, p.doctor_name,
               a.sample_date
        FROM analysis_instances a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.id = ?
    """, (analysis_id,))

    row = cur.fetchone()
    if not row:
        conn.close()
        return "Report not found", 404

    analysis_type = row[1]

    # جلب النتائج
    cur.execute("""
        SELECT field_name, field_value, unit, normal_range, field_type
        FROM results WHERE analysis_id = ?
        ORDER BY CASE WHEN field_type='template' THEN 1 ELSE 2 END, id
    """, (analysis_id,))
    results = cur.fetchall()

    results_dict = {}
    custom_fields = []
    for r in results:
        if r[4] == 'custom':
            custom_fields.append(r)
        else:
            results_dict[r[0]] = r

    # جلب حقول القالب
    template_fields = []
    if analysis_type not in ['GENERAL', 'LAP_REPORT']:
        cur.execute("SELECT fields FROM analysis_templates WHERE analysis_name = ?", (analysis_type,))
        t = cur.fetchone()
        if t:
            template_fields = json.loads(t[0])

    # Lab Comment
    cur.execute("SELECT comment FROM lab_comments WHERE analysis_id = ?", (analysis_id,))
    crow = cur.fetchone()
    lab_comment = crow[0] if crow else ""

    # الأطباء
    cur.execute("SELECT doctor_name FROM doctors WHERE is_active = 1 ORDER BY doctor_name")
    doctors = [r[0] for r in cur.fetchall()]

    conn.close()

    sample_date = row[10] or datetime.now().strftime("%Y-%m-%d")
    return render_template("edit_report.html",
        analysis_id=analysis_id,
        analysis_type=analysis_type,
        row=row,
        sample_date=sample_date,
        results_dict=results_dict,
        custom_fields=custom_fields,
        template_fields=template_fields,
        lab_comment=lab_comment,
        doctors=doctors
    )