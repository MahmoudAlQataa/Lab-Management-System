"""
settings.py
===============================================
إعدادات القوالب (Test & Units & Normal Ranges)
===============================================
"""

import json
from flask import Blueprint, render_template, request, redirect, url_for
from models.database import getdb
from config import DB_NAME

settings_bp = Blueprint('settings', __name__)


@settings_bp.route("/template-settings", methods=["GET", "POST"])
def template_settings():
    """
    صفحة إعدادات القوالب - تعديل Units و Normal Ranges
    """
    
    if request.method == "POST":
        # =======================================
        # حفظ التعديلات
        # =======================================
        conn = getdb()
        cur = conn.cursor()
        
        # جلب كل القوالب
        cur.execute("SELECT analysis_name, fields FROM analysis_templates")
        templates = cur.fetchall()
        
        # ✅ استثناء GENERAL و LAP_REPORT
        EXCLUDE_TEMPLATES = ['GENERAL', 'LAP_REPORT']
        
        for template in templates:
            analysis_name = template[0]
            
            # تخطي القوالب الديناميكية المستثناة
            if analysis_name in EXCLUDE_TEMPLATES:
                continue
                
            existing_fields = json.loads(template[1])
            
            # جلب القيم الجديدة من الفورم كقوائم
            old_names = request.form.getlist(f"fields_{analysis_name}_old_name[]")
            names     = request.form.getlist(f"fields_{analysis_name}_name[]")
            units     = request.form.getlist(f"fields_{analysis_name}_unit[]")
            ranges    = request.form.getlist(f"fields_{analysis_name}_range[]")
            types     = request.form.getlist(f"fields_{analysis_name}_type[]")

            if f"fields_{analysis_name}_name[]" not in request.form:
                continue

            new_fields = []
            for i, (old_name, new_name, unit, rng) in enumerate(zip(old_names, names, units, ranges)):
                name_stripped = new_name.strip()
                if not name_stripped:
                    continue

                field_type = types[i] if i < len(types) else "text"

                field_data = {
                    "name": name_stripped,
                    "unit": unit.strip() if unit else "",
                    "normal_range": rng.strip() if rng else "",
                    "type": field_type
                }

                # إذا dropdown للنتيجة - جلب الخيارات
                if field_type == "dropdown":
                    options_key = f"fields_{analysis_name}_options_{i}[]"
                    options = request.form.getlist(options_key)
                    field_data["options"] = [o.strip() for o in options if o.strip()]

                # نوع الـ Normal Range
                range_type_key = f"fields_{analysis_name}_range_type_{i}"
                range_type = request.form.get(range_type_key, "text")
                field_data["range_type"] = range_type

                if range_type == "dropdown":
                    range_options_key = f"fields_{analysis_name}_range_options_{i}[]"
                    range_options = request.form.getlist(range_options_key)
                    field_data["range_options"] = [o.strip() for o in range_options if o.strip()]

                new_fields.append(field_data)
            
            # حفظ القالب المحدث
            cur.execute("""
                UPDATE analysis_templates 
                SET fields = ? 
                WHERE analysis_name = ?
            """, (json.dumps(new_fields), analysis_name))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('settings.template_settings'))
    
    # =======================================
    # عرض الصفحة
    # =======================================
    conn = getdb()
    cur = conn.cursor()
    
    cur.execute("SELECT analysis_name, fields FROM analysis_templates ORDER BY analysis_name")
    templates_data = {}
    
    # ✅ استثناء GENERAL و LAP_REPORT
    EXCLUDE_TEMPLATES = ['GENERAL', 'LAP_REPORT']
    
    for row in cur.fetchall():
        analysis_name = row[0]
        
        # تخطي القوالب الديناميكية
        if analysis_name in EXCLUDE_TEMPLATES:
            continue
            
        fields = json.loads(row[1])
        templates_data[analysis_name] = fields
    
    conn.close()
    
    return render_template("template_settings.html", templates=templates_data)


@settings_bp.route("/reorder-fields", methods=["POST"])
def reorder_fields():
    """حفظ ترتيب الحقول الجديد"""
    data = request.get_json()
    analysis_name = data.get("analysis_name")
    new_order = data.get("order", [])  # قائمة بأسماء الحقول بالترتيب الجديد

    conn = getdb()
    cur = conn.cursor()
    cur.execute("SELECT fields FROM analysis_templates WHERE analysis_name = ?", (analysis_name,))
    row = cur.fetchone()

    if row:
        fields = json.loads(row[0])
        fields_dict = {f["name"]: f for f in fields}
        reordered = [fields_dict[name] for name in new_order if name in fields_dict]
        cur.execute("UPDATE analysis_templates SET fields = ? WHERE analysis_name = ?",
                    (json.dumps(reordered), analysis_name))
        conn.commit()

    conn.close()
    return {"status": "ok"}