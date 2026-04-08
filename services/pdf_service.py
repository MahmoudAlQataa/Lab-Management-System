"""
===============================================
خدمة توليد ملفات PDF - تصميم طبي احترافي
===============================================
يحتوي على:
- تصاميم منفصلة لكل نوع تحليل
- Header/Footer موحد
- Lab Comment
- تصميم boxes بدل جداول

التصاميم:
---------
1. URINE_ANALYSIS - عمودين Test/Result
2. SEMEN_ANALYSIS - جدول + Motility + Morphology
3. STOOL_ANALYSIS - Test/Result + Parasites
4. MICROBIOLOGY - حقول خاصة + Antibiotics
5. LAP_REPORT - Title + Content
6. GENERAL - Test/Result/Unit/Normal Range (للباقي)
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from arabic_reshaper import reshape
from bidi.algorithm import get_display

from models.database import getdb
from config import FONT_PATH, HEADER_IMAGE_PATH, PDF_OUTPUT_DIR

# =======================================
# Constants
# =======================================
SHOW_ALL_FIELDS = ['URINE_ANALYSIS', 'SEMEN_ANALYSIS', 'STOOL_ANALYSIS']

# =======================================
# Helper Functions
# =======================================

def setup_arabic_font():
    """تسجيل الخط العربي"""
    try:
        pdfmetrics.registerFont(TTFont('Arabic', FONT_PATH))
        return True
    except:
        return False


def draw_watermark(c, width, height):
    """
    رسم العلامة المائية على الصفحة
    """
    import os
    
    watermark_path = os.path.join('static', 'img', 'WaterMark.png')
    
    if os.path.exists(watermark_path):
        # حفظ الحالة الحالية
        c.saveState()
        
        # ✅ تقليل الشفافية (opacity)
        c.setFillAlpha(0.05)  # 10% opacity (كلما قل الرقم، كلما كانت أخف)
        
        # ✅ رسم الصورة في المنتصف
        # حساب المقاسات
        img_width = 500  # عرض الصورة
        img_height = 500  # ارتفاع الصورة
        
        # وضع في المنتصف
        x = (width - img_width) / 2
        y = (height - img_height) / 2
        
        c.drawImage(watermark_path, x, y, width=img_width, height=img_height, 
                    mask='auto', preserveAspectRatio=True)
        
        # استرجاع الحالة
        c.restoreState()

def ar(text):
    """تحويل النص العربي للعرض الصحيح"""
    if not text:
        return ""
    reshaped = reshape(str(text))
    return get_display(reshaped)


def draw_header_footer(c, width, height, arabic_available):
    """
    رسم Header و Footer موحد لكل الصفحات
    
    Returns:
    --------
    tuple: (header_height, footer_height)
    """
    
    # ✅ العلامة المائية أولاً (في الخلفية)
    draw_watermark(c, width, height)
    
    header_height = 130
    footer_height = 57
    
    # Header
    if os.path.exists(HEADER_IMAGE_PATH):
        c.drawImage(HEADER_IMAGE_PATH, 0, height - header_height, 
                    width=width, height=header_height, preserveAspectRatio=False)
    
    # شيل الخط تحت الهيدر
    # c.setStrokeColor(colors.black)
    # c.setLineWidth(1)
    # c.line(0, height - header_height, width, height - header_height)
    
    # Footer
    footer_height = 57
    
    # السطر الأول: "مُرخص من وزارة الصحة الفلسطينية"
    if arabic_available:
        c.setFont("Arabic", 10)
        arabic_text1 = ar("مُرخص من وزارة الصحة الفلسطينية")
        c.drawCentredString(width/2, footer_height - 12, arabic_text1)
    else:
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, footer_height - 12, "Licensed by Palestinian Ministry of Health")
    
    # الخط الفاصل
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.line(40, footer_height - 20, width - 40, footer_height - 20)
    
    # السطر الثاني - ثلاثة أقسام
    # اليسار: هاتف
    if arabic_available:
        c.setFont("Arabic", 9)
        phone_text = ar("هاتف: 0599414743")
        c.drawString(40, footer_height - 33, phone_text)
    else:
        c.setFont("Helvetica", 9)
        c.drawString(40, footer_height - 33, "Tel: 0599414743")
    
    # الوسط: شرطة
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, footer_height - 33, "-")
    
    # اليمين: العنوان
    if arabic_available:
        c.setFont("Arabic", 9)
        address_text = ar("غزة - شارع الوحدة - مقابل عيادة شهداء الدرج (البندر)")
        c.drawRightString(width - 40, footer_height - 33, address_text)
    
    return header_height, footer_height


def draw_patient_info_boxes(c, patient_data, y_start, width, arabic_available):
    """
    رسم مستطيلات معلومات المريض
    
    patient_data: tuple (name, id_number, phone, age, gender, doctor, date)
    """
    y = y_start
    
    # السطر الأول
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    
    # مربع الاسم (label + value قريبين)
    c.rect(320, y - 20, 255, 20)
    if arabic_available:
        c.setFont("Arabic", 9)
        label = ar("اسـم المريـض :")
        c.drawRightString(570, y - 13, label)
        c.setFont("Arabic", 10)
        name_arabic = ar(patient_data[0])
        c.drawRightString(480, y - 13, name_arabic)
    else:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(520, y - 13, "Name:")
        c.setFont("Helvetica", 10)
        c.drawString(480, y - 13, patient_data[0])
    
    # مربع الجنس
    c.rect(170, y - 20, 145, 20)
    if arabic_available:
        c.setFont("Arabic", 9)
        label = ar("الجنـس :")
        c.drawRightString(310, y - 13, label)
    else:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(265, y - 13, "Gender:")
    
    c.setFont("Helvetica", 9)
    gender_text = patient_data[4] if patient_data[4] else ""
    c.drawString(265, y - 13, gender_text)
    
    # مربع العمر
    c.rect(40, y - 20, 125, 20)
    if arabic_available:
        c.setFont("Arabic", 9)
        label = ar("العمـر :")
        c.drawRightString(160, y - 13, label)
    else:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(120, y - 13, "Age:")
    
    c.setFont("Helvetica", 9)
    c.drawString(120, y - 13, str(patient_data[3]))
    
    y -= 25
    
    # السطر الثاني
    # مربع تاريخ سحب العينة
    c.rect(320, y - 20, 255, 20)
    if arabic_available:
        c.setFont("Arabic", 9)
        label = ar("تاريـخ سحـب العينـة :")
        c.drawRightString(570, y - 13, label)
    else:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(490, y - 13, "Date:")
    
    c.setFont("Helvetica", 9)
    c.drawString(410, y - 13, patient_data[6])
    
    # مربع الطبيب المعالج
    c.rect(40, y - 20, 275, 20)
    if arabic_available:
        c.setFont("Arabic", 9)
        label = ar("الطبيب المعالج :")
        c.drawRightString(310, y - 13, label)
    else:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(240, y - 13, "Dr:")
    
    doctor = patient_data[5] if patient_data[5] else ""
    if arabic_available and doctor:
        c.setFont("Arabic", 10)
        doctor_ar = ar(doctor)
        c.drawRightString(230, y - 13, doctor_ar)
    else:
        c.setFont("Helvetica", 10)
        c.drawString(150, y - 13, doctor)
    
    y -= 30
    
    return y


def draw_analysis_title_box(c, title, y, width):
    """رسم مستطيل عنوان التحليل"""
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.rect(40, y - 25, 535, 25)  # ✅ نفس عرض بيانات المريض
    
    c.setFont("Courier-Bold", 12)
    c.drawCentredString(width/2, y - 17, title)
    
    return y - 35


def draw_lab_comment_box(c, lab_comment, y, width, arabic_available):
    """رسم مربع Lab Comment"""
    # إظهار المربع دائماً حتى لو فارغ
    
    # عنوان Lab Comment
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.rect(40, y - 18, 100, 18)  # ✅ يبدأ من 40
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y - 13, "Lab Comment")
    
    y -= 23
    
    # محتوى التعليق
    comment_height = 60
    c.setLineWidth(1)
    c.rect(40, y - comment_height, 535, comment_height)  # ✅ نفس العرض
    
    # كتابة التعليق
    if arabic_available:
        c.setFont("Arabic", 9)
        comment_text = ar(lab_comment)
    else:
        c.setFont("Helvetica", 9)
        comment_text = lab_comment
    
    # تقسيم حسب الأسطر (الحفاظ على \n)
    lines = []
    max_chars = 100

    paragraphs = comment_text.split("\n")

    for para in paragraphs:
        words = para.split()
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line = current_line + " " + word if current_line else word
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)
    
    # رسم الأسطر
    text_y = y - 15
    for line in lines[:3]:  # max 3 lines
        c.drawString(50, text_y, line)
        text_y -= 15
    
    y -= comment_height + 15
    
    return y


def draw_date_signature_boxes(c, y_pos, width):
    """رسم مربعات Date و Signature"""
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)

    # Date label box
    c.rect(40, y_pos, 50, 18)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y_pos + 5, "Date :")

    # Date value box
    c.setLineWidth(1)
    c.rect(95, y_pos, 140, 18)

    # Signature - مربع بقد الكلمة + مساحة فارغة على اليمين للتوقيع
    c.setLineWidth(1.5)
    c.rect(width - 230, y_pos, 80, 18)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 226, y_pos + 5, "Signature :")


# =======================================
# Template Drawing Functions
# =======================================

def draw_urine_analysis(c, results, template_fields, lab_comment, y, width, height, footer_height, arabic_available):
    """
    رسم تحليل URINE - عمودين Test/Result
    """
    y = draw_analysis_title_box(c, "Urine Analysis Report", y, width)
    
    # بناء قاموس النتائج - مع فصل template و custom
    results_dict = {}
    custom_fields = []
    
    for r in results:
        field_name = r[0]
        field_value = r[1]
        field_type = r[4] if len(r) > 4 else 'template'
        
        if field_type == 'custom':
            custom_fields.append(r)
        else:
            results_dict[field_name] = field_value
    
    # Headers
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    
    # Right column headers
    c.rect(40, y - 20, 100, 20)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(90, y - 13, "Test")
    
    c.rect(145, y - 20, 150, 20)
    c.drawCentredString(220, y - 13, "Result")
    
    # Left column headers
    c.rect(315, y - 20, 100, 20)
    c.drawCentredString(365, y - 13, "Test")
    
    c.rect(420, y - 20, 155, 20)
    c.drawCentredString(497, y - 13, "Result")
    
    y -= 25
    
    # الترتيب الثابت للعمودين
    left_column = [
        ('color',           'Color'),
        ('appearance',      'Appearance'),
        ('specific_gravity','Specific Gravity'),
        ('ph',              'pH'),
        ('glucose',         'Glucose'),
        ('protein',         'Protein'),
        ('ketones',         'Ketones'),
        ('bilirubin',       'Bilirubin'),
        ('urobilinogen',    'Urobilinogen'),
        ('blood',           'Blood'),
        ('nitrite',         'Nitrite'),
    ]
    
    right_column = [
        ('wbc_hpf',             'WBC / HPF'),
        ('rbc_hpf',             'RBC / HPF'),
        ('epithelial_cells_hpf','Epith. Cells/HPF'),
        ('casts_lpf',           'Casts / LPF'),
        ('crystals',            'Crystals'),
        ('mucous',              'Mucous'),
        ('amorphous',           'Amorphous'),
        ('bacteria',            'Bacteria'),
        ('yeast',               'Yeast'),
        ('parasites',           'Parasites'),
    ]
    
    c.setLineWidth(1)
    row_height = 20
    num_rows = max(len(left_column), len(right_column))
    
    for i in range(num_rows):
        # العمود الأيسر (x=40)
        if i < len(left_column):
            field_name, field_display = left_column[i]
            field_value = results_dict.get(field_name, "")
            c.rect(40, y - row_height, 100, row_height)
            c.setFont("Courier", 9)
            c.drawString(45, y - 13, field_display)
            c.rect(145, y - row_height, 150, row_height)
            c.setFont("Helvetica", 9)
            c.drawString(150, y - 13, str(field_value))
        
        # العمود الأيمن (x=315)
        if i < len(right_column):
            field_name, field_display = right_column[i]
            field_value = results_dict.get(field_name, "")
            c.rect(315, y - row_height, 100, row_height)
            c.setFont("Courier", 9)
            c.drawString(320, y - 13, field_display)
            c.rect(420, y - row_height, 155, row_height)
            c.setFont("Helvetica", 9)
            c.drawString(425, y - 13, str(field_value))
        
        y -= row_height
    
    y -= 10
    
    # ✅ Custom Fields - فقط إذا موجودة
    if custom_fields:
        for idx, custom_field in enumerate(custom_fields):
            field_name = custom_field[0]
            field_value = custom_field[1]
            field_unit = custom_field[2] if custom_field[2] else ""
            
            custom_text = str(field_value)
            if custom_text and field_unit:
                custom_text += " " + field_unit
            
            # تحديد العمود
            if idx % 2 == 0:  # عمود يمين
                c.rect(40, y - row_height, 100, row_height)
                c.setFont("Courier", 9)
                c.drawString(45, y - 13, field_name)
                
                c.rect(145, y - row_height, 150, row_height)
                c.setFont("Helvetica", 9)
                c.drawString(150, y - 13, custom_text)
            else:  # عمود يسار
                c.rect(315, y - row_height, 100, row_height)
                c.setFont("Courier", 9)
                c.drawString(320, y - 13, field_name)
                
                c.rect(420, y - row_height, 155, row_height)
                c.setFont("Helvetica", 9)
                c.drawString(425, y - 13, custom_text)
                
                y -= row_height
        
        # إذا عدد Custom Fields فردي
        if len(custom_fields) % 2 != 0:
            y -= row_height
        
        y -= 5
    
    # Lab Comment
    y = draw_lab_comment_box(c, lab_comment, y, width, arabic_available)
    
    # Date & Signature
    draw_date_signature_boxes(c, footer_height + 10, width)
    
    return y - 50


def draw_semen_analysis(c, results, template_fields, lab_comment, y, width, height, footer_height, arabic_available):
    """
    رسم تحليل SEMEN
    """
    y = draw_analysis_title_box(c, "Semen Analysis Report", y, width)
    
    # بناء قاموس النتائج - مع فصل template و custom
    results_dict = {}
    custom_fields = []
    
    for r in results:
        field_name = r[0]
        field_value = r[1]
        field_type = r[4] if len(r) > 4 else 'template'
        
        if field_type == 'custom':
            custom_fields.append(r)
        else:
            results_dict[field_name] = field_value
    
    # Headers - محاذاة مع Motility
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    
    c.rect(90, y - 20, 150, 20)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(165, y - 13, "Test")
    
    c.rect(245, y - 20, 295, 20)
    c.drawCentredString(392, y - 13, "Result")
    
    y -= 25
    
    # الحقول الأساسية
    basic_fields = [
        ('period', 'Period', 'Days'),
        ('volume', 'Volume / mL', 'mL'),
        ('appearance', 'Appearance', ''),
        ('viscosity', 'Viscosity', ''),
        ('liquefaction', 'Liquefaction', 'min'),
        ('sperm_count', 'Sperm Count', 'mill/mL'),
        ('ph', 'pH', ''),
        ('rbc_hpf', 'RBC / HPF', ''),
        ('wbc_hpf', 'WBC / HPF', '')
    ]
    
    c.setLineWidth(1)
    c.setFont("Courier", 9)
    row_height = 20
    
    for field_key, field_display, unit in basic_fields:
        field_value = results_dict.get(field_key, "")
        
        # Test name
        c.rect(90, y - row_height, 150, row_height)
        c.drawString(95, y - 13, field_display)
        
        # Result with unit
        c.rect(245, y - row_height, 295, row_height)
        c.setFont("Helvetica", 9)
        result_text = str(field_value)
        if result_text and unit:
            result_text += " " + unit
        c.drawString(250, y - 13, result_text)
        c.setFont("Courier", 9)
        
        y -= row_height
    
    y -= 15
    
    # Motility Section
    c.setLineWidth(1.5)
    c.rect(60, y - 18, 80, 18)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(65, y - 13, "Motility :")
    
    y -= 23
    
    motility_grades = [
        ('grade_a', 'Grade "A"', 'Rapid progressive movement'),
        ('grade_b', 'Grade "B"', 'Slow or sluggish progressive movement'),
        ('grade_c', 'Grade "C"', 'Non - Progressive movement'),
        ('grade_d', 'Grade "D"', 'Immotile')
    ]
    
    c.setLineWidth(1)
    c.setFont("Helvetica", 9)
    for grade_key, grade_name, grade_desc in motility_grades:
        c.rect(90, y - 18, 70, 18)
        c.drawString(95, y - 13, grade_name)
        
        c.rect(165, y - 18, 280, 18)
        c.drawString(170, y - 13, grade_desc)
        
        c.rect(450, y - 18, 60, 18)
        grade_value = results_dict.get(grade_key, "")
        c.drawString(470, y - 13, str(grade_value))
        
        c.rect(515, y - 18, 25, 18)
        c.drawString(520, y - 13, "%")
        
        y -= 18
    
    y -= 20  # ✅ مسافة بدل العنوان
    
    # حقلين Sperm Morphology - نفس محاذاة Test/Result
    c.setLineWidth(1)
    c.setFont("Helvetica", 9)
    
    # 1. Sperm Morphology - مع text wrapping للنص الطويل
    from reportlab.pdfbase.pdfmetrics import stringWidth
    
    morph_value = str(results_dict.get("sperm_morphology", ""))
    
    # تقسيم النص لأسطر
    morph_font = "Helvetica"
    morph_font_size = 9
    max_morph_width = 280  # عرض مربع النتيجة - هوامش
    morph_lines = []
    words = morph_value.split()
    current = ""
    for word in words:
        test = current + " " + word if current else word
        if stringWidth(test, morph_font, morph_font_size) <= max_morph_width:
            current = test
        else:
            if current:
                morph_lines.append(current)
            # الكلمة نفسها قد تكون أطول من العرض - نقسمها بالحروف
            if stringWidth(word, morph_font, morph_font_size) > max_morph_width:
                char_line = ""
                for ch in word:
                    if stringWidth(char_line + ch, morph_font, morph_font_size) <= max_morph_width:
                        char_line += ch
                    else:
                        morph_lines.append(char_line)
                        char_line = ch
                current = char_line
            else:
                current = word
    if current:
        morph_lines.append(current)
    if not morph_lines:
        morph_lines = [""]
    
    # حساب الارتفاع حسب عدد الأسطر
    morph_line_h = 14
    morph_padding = 10
    morph_box_h = max(36, len(morph_lines) * morph_line_h + morph_padding)
    
    c.rect(90, y - morph_box_h, 150, morph_box_h)
    c.setFont("Helvetica", 9)
    c.drawString(95, y - (morph_box_h / 2) - 3, "Sperm Morphology")
    
    c.rect(245, y - morph_box_h, 295, morph_box_h)
    c.setFont(morph_font, morph_font_size)
    text_y = y - morph_line_h + 3
    for line in morph_lines:
        c.drawString(250, text_y, line)
        text_y -= morph_line_h
    
    y -= morph_box_h + 5
    
    # 2. Spermatocyte / HPF
    c.rect(90, y - 18, 150, 18)
    c.drawString(95, y - 13, "Spermatocyte / HPF")
    
    c.rect(245, y - 18, 295, 18)
    sperm_hpf_value = results_dict.get("spermatocyte_hpf", "")
    c.drawString(250, y - 13, str(sperm_hpf_value))
    
    y -= 28
    
    # ✅ Extra Template Fields (Added dynamically via settings)
    basic_keys = [f[0] for f in basic_fields] + [f[0] for f in motility_grades] + ["sperm_morphology", "spermatocyte_hpf"]
    extra_template_fields = [f for f in template_fields if f[0] not in basic_keys]
    
    if extra_template_fields:
        for extra_field in extra_template_fields:
            c.rect(90, y - 18, 150, 18)
            c.drawString(95, y - 13, extra_field[0])
            
            c.rect(245, y - 18, 295, 18)
            val = results_dict.get(extra_field[0], "")
            unit = extra_field[1] if len(extra_field) > 1 else ""
            txt = str(val) + (" " + unit if unit and str(val) else "")
            c.drawString(250, y - 13, txt)
            y -= 23
            
        y -= 5
        
    # ✅ Custom Fields
    if custom_fields:
        for custom_field in custom_fields:
            c.rect(90, y - 18, 150, 18)
            c.drawString(95, y - 13, custom_field[0])
            
            c.rect(245, y - 18, 295, 18)
            custom_value = custom_field[1]
            custom_unit = custom_field[2] if custom_field[2] else ""
            custom_text = str(custom_value)
            if custom_unit:
                custom_text += " " + custom_unit
            c.drawString(250, y - 13, custom_text)
            
            y -= 23
        
        y -= 5
    
    # Lab Comment
    y = draw_lab_comment_box(c, lab_comment, y, width, arabic_available)
    
    # Date & Signature
    draw_date_signature_boxes(c, footer_height + 10, width)
    
    return y - 50


def draw_stool_analysis(c, results, template_fields, lab_comment, y, width, height, footer_height, arabic_available):
    """
    رسم تحليل STOOL
    """
    y = draw_analysis_title_box(c, "Stool Analysis Report", y, width)
    
    # بناء قاموس النتائج - مع فصل template و custom
    results_dict = {}
    custom_fields = []
    
    for r in results:
        field_name = r[0]
        field_value = r[1]
        field_type = r[4] if len(r) > 4 else 'template'
        
        if field_type == 'custom':
            custom_fields.append(r)
        else:
            results_dict[field_name] = field_value
    
    # Headers - نفس محاذاة SEMEN
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    
    c.rect(90, y - 20, 150, 20)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(165, y - 13, "Test")
    
    c.rect(245, y - 20, 295, 20)
    c.drawCentredString(392, y - 13, "Result")
    
    y -= 25
    
    # الحقول الأساسية (قبل Parasites)
    basic_fields = [
        ('color', 'Color'),
        ('consistency', 'Consistency'),
        ('ph', 'PH'),
        ('mucous', 'Mucous'),
        ('rbcs', "RBC's"),
        ('wbcs', "WBC's")
    ]
    
    c.setLineWidth(1)
    c.setFont("Courier", 9)
    row_height = 20
    
    for field_key, field_display in basic_fields:
        field_value = results_dict.get(field_key, "")
        
        c.rect(90, y - row_height, 150, row_height)
        c.drawString(95, y - 13, field_display)
        
        c.rect(245, y - row_height, 295, row_height)
        c.setFont("Helvetica", 9)
        c.drawString(250, y - 13, str(field_value))
        c.setFont("Courier", 9)
        
        y -= row_height
    
    y -= 5
    
    # Parasites - مربع كبير
    parasites_height = 40
    c.rect(90, y - parasites_height, 150, parasites_height)
    c.setFont("Courier", 9)
    c.drawString(95, y - 20, "Parasites")
    
    c.rect(245, y - parasites_height, 295, parasites_height)
    parasites_value = results_dict.get("parasites", "")
    c.setFont("Helvetica", 9)
    c.drawString(250, y - 20, str(parasites_value))
    
    y -= parasites_height + 10
    
    # ✅ Extra Template Fields (Added dynamically via settings)
    basic_keys = [f[0] for f in basic_fields] + ["parasites"]
    extra_template_fields = [f for f in template_fields if f[0] not in basic_keys]
    
    if extra_template_fields:
        for extra_field in extra_template_fields:
            c.rect(90, y - 18, 150, 18)
            c.setFont("Courier", 9)
            c.drawString(95, y - 13, extra_field[0])
            
            c.rect(245, y - 18, 295, 18)
            c.setFont("Helvetica", 9)
            val = results_dict.get(extra_field[0], "")
            unit = extra_field[1] if len(extra_field) > 1 else ""
            txt = str(val) + (" " + unit if unit and str(val) else "")
            c.drawString(250, y - 13, txt)
            y -= 23
            
        y -= 5
    
    # ✅ Custom Fields - فقط إذا موجودة
    if custom_fields:
        for custom_field in custom_fields:
            c.rect(90, y - 18, 150, 18)
            c.setFont("Courier", 9)
            c.drawString(95, y - 13, custom_field[0])  # field_name
            
            c.rect(245, y - 18, 295, 18)
            c.setFont("Helvetica", 9)
            custom_value = custom_field[1]  # field_value
            custom_unit = custom_field[2] if custom_field[2] else ""  # unit
            custom_text = str(custom_value)
            if custom_unit:
                custom_text += " " + custom_unit
            c.drawString(250, y - 13, custom_text)
            
            y -= 23
        
        y -= 5
    
    # Lab Comment
    y = draw_lab_comment_box(c, lab_comment, y, width, arabic_available)
    
    # Date & Signature
    draw_date_signature_boxes(c, footer_height + 10, width)
    
    return y - 50


def draw_microbiology(c, results, template_fields, lab_comment, y, width, height, footer_height, arabic_available):
    """
    رسم تحليل MICROBIOLOGY
    """
    y = draw_analysis_title_box(c, "Microbiology Report", y, width)
    
    # بناء قاموس النتائج
    results_dict = {}
    for r in results:
        results_dict[r[0]] = r[1]
    
    # الحقول الأربعة العلوية (2x2 grid)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.setFont("Helvetica", 9)
    
    # Specimen & Gram Stain
    c.rect(60, y - 20, 80, 20)
    c.drawString(65, y - 13, "Specimen")
    
    c.rect(145, y - 20, 200, 20)
    specimen_value = results_dict.get("specimen", "")
    c.drawString(150, y - 13, str(specimen_value))
    
    c.rect(360, y - 20, 80, 20)
    c.drawString(365, y - 13, "Gram Stain")
    
    c.rect(445, y - 20, 130, 20)
    gram_value = results_dict.get("gram_stain", "")
    c.drawString(450, y - 13, str(gram_value))
    
    y -= 25
    
    # Count & Organism
    c.rect(60, y - 20, 80, 20)
    c.drawString(65, y - 13, "Count")
    
    c.rect(145, y - 20, 200, 20)
    count_value = results_dict.get("count", "")
    c.drawString(150, y - 13, str(count_value))
    
    c.rect(360, y - 20, 80, 20)
    c.drawString(365, y - 13, "Organism")
    
    c.rect(445, y - 20, 130, 20)
    organism_value = results_dict.get("organism", "")
    c.drawString(450, y - 13, str(organism_value))
    
    y -= 30
    
    # Antibiotics - عمودين
    # Database keys (lowercase + underscores)
    antibiotics_keys = [
        'penicillin_g', 'ampicillin', 'amoxycillin', 'cloxacillin', 'piperacillin',
        'erythromycin', 'clindamycin', 'cephalexin', 'cefuroxime',
        'cefotaxime', 'ceftazidim', 'aztreofloxacin',
        'aztreonam', 'ceftriaxone', 'cephazolin',
        'amikacin', 'ofloxacin', 'augmantin', 'gentamicin', 'tetracycline',
        'chloramphenicol', 'septrin', 'nalidixic', 'ciprofloxacin',
        'polymyxin_b', 'neomycin', 'rifampicin', 'vancomycin', 'rovamycin',
        'minocyline', 'ceclor', 'nitro_furantion', 'doxycycline'
    ]
    
    # Display names (for PDF)
    antibiotics_display = [
        'Penicillin G', 'Ampicillin', 'Amoxycillin', 'Cloxacillin', 'Piperacillin',
        'Erythromycin', 'Clindamycin', 'Cephalexin (Keflex)', 'Cefuroxime (Zinnat)',
        'Cefotaxime (Claforan)', 'Ceftazidim (fortum)', 'Aztreofloxacin',
        'Aztreonam (Azactam)', 'Ceftriaxone (Rocephin)', 'Cephazolin(Cefamezine)',
        'Amikacin', 'Ofloxacin (travid)', 'Augmantin', 'Gentamicin', 'Tetracycline',
        'Chloramphenicol', 'Septrin', 'Nalidixic (Negram)', 'Ciprofloxacin',
        'Polymyxin B', 'Neomycin', 'Rifampicin', 'Vancomycin', 'Rovamycin',
        'Minocyline', 'Ceclor', 'Nitro Furantion', 'Doxycycline'
    ]
    
    # Headers
    c.setLineWidth(1.5)
    c.rect(60, y - 20, 130, 20)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(125, y - 13, "Antibiotic")
    
    c.rect(195, y - 20, 100, 20)
    c.drawCentredString(245, y - 13, "Result")
    
    c.rect(310, y - 20, 130, 20)
    c.drawCentredString(375, y - 13, "Antibiotic")
    
    c.rect(445, y - 20, 130, 20)
    c.drawCentredString(510, y - 13, "Result")
    
    y -= 25
    
    # ✅ فلترة المضادات - فقط التي لها قيم
    filled_antibiotics = []
    for i in range(len(antibiotics_keys)):
        key = antibiotics_keys[i]
        value = results_dict.get(key, "")
        if value:  # فقط إذا في قيمة
            filled_antibiotics.append({
                'key': key,
                'display': antibiotics_display[i],
                'value': value
            })
    
    # البيانات
    c.setLineWidth(1)
    c.setFont("Helvetica", 9)
    row_height = 18
    
    half = len(filled_antibiotics) // 2 + len(filled_antibiotics) % 2
    
    for i in range(half):
        left_antibiotic = filled_antibiotics[i]
        left_key = left_antibiotic['key']
        left_display = left_antibiotic['display']
        left_value = left_antibiotic['value']
        
        # عمود يسار
        c.rect(60, y - row_height, 130, row_height)
        c.drawString(65, y - 12, left_display)
        
        c.rect(195, y - row_height, 100, row_height)
        c.drawString(200, y - 12, str(left_value))
        
        # عمود يمين
        if i + half < len(filled_antibiotics):
            right_antibiotic = filled_antibiotics[i + half]
            right_key = right_antibiotic['key']
            right_display = right_antibiotic['display']
            right_value = right_antibiotic['value']
            
            c.rect(310, y - row_height, 130, row_height)
            c.drawString(315, y - 12, right_display)
            
            c.rect(445, y - row_height, 130, row_height)
            c.drawString(450, y - 12, str(right_value))
        
        y -= row_height
    
    y -= 10
    
    # Lab Comment
    y = draw_lab_comment_box(c, lab_comment, y, width, arabic_available)
    
    # Date & Signature
    draw_date_signature_boxes(c, footer_height + 10, width)
    
    return y - 50


def draw_lap_report(c, results, y, width, height, footer_height, arabic_available):
    """
    رسم LAP_REPORT - بدون Lab Comment - صندوق محتوى ديناميكي
    """
    from reportlab.pdfbase.pdfmetrics import stringWidth
    
    # بناء قاموس النتائج
    results_dict = {}
    for r in results:
        results_dict[r[0]] = r[1]
    
    # Title box
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(40, y - 30, 535, 30)
    
    title_value = results_dict.get("title", "")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width/2, y - 18, str(title_value))
    
    y -= 40
    
    # ✅ حساب ارتفاع المحتوى ديناميكياً
    content_value = results_dict.get("content", "")
    
    if content_value:
        # إعدادات النص
        if arabic_available:
            font_name = "Arabic"
            content_text = ar(content_value)
        else:
            font_name = "Helvetica"
            content_text = content_value
        
        font_size = 10
        line_height = 14
        max_width = 525  # عرض الصندوق - هوامش
        
        # تقسيم النص لأسطر بناءً على العرض
        from reportlab.pdfbase.pdfmetrics import stringWidth
        
        lines = []
        paragraphs = content_text.split('\n')
        
        for para in paragraphs:
            if not para.strip():
                lines.append('')  # سطر فارغ
                continue
            
            words = para.split(' ')
            current_line = ''
            
            for word in words:
                test_line = current_line + ' ' + word if current_line else word
                test_width = stringWidth(test_line, font_name, font_size)
                
                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
        
        # حساب الارتفاع
        num_lines = len(lines)
        content_height = (num_lines * line_height) + 40  # + padding
        
        # حدود الارتفاع
        min_height = 100
        max_height = 500
        content_height = max(min_height, min(content_height, max_height))
    else:
        content_height = 100  # ارتفاع افتراضي للصندوق الفارغ
        lines = []
    
    # رسم صندوق المحتوى
    c.rect(40, y - content_height, 535, content_height)
    
    # كتابة المحتوى
    if lines:
        c.setFont(font_name, font_size)
        text_y = y - 20
        
        for line in lines:
            if text_y > (y - content_height + 20):  # التأكد من عدم الخروج من الصندوق
                c.drawString(50, text_y, line)
                text_y -= line_height
            else:
                break  # وصلنا لنهاية الصندوق
    
    y -= content_height + 20
    
    # Date & Signature
    draw_date_signature_boxes(c, footer_height + 10, width)

    return y - 50


def draw_general_analysis(c, analysis_name, results, lab_comment, y, width, height, footer_height, arabic_available):
    """
    رسم التحليل العام - للتحاليل الباقية
    """
    y = draw_analysis_title_box(c, analysis_name, y, width)
    
    # Headers
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    
    c.rect(40, y - 25, 160, 25)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(120, y - 15, "Test")
    
    c.rect(205, y - 25, 140, 25)
    c.drawCentredString(275, y - 15, "Result")
    
    c.rect(350, y - 25, 80, 25)
    c.drawCentredString(390, y - 15, "Unit")
    
    c.rect(435, y - 25, 140, 25)
    c.drawCentredString(505, y - 15, "Normal Range")
    
    y -= 30
    
    
    # البيانات - فقط الحقول المملوءة
    c.setLineWidth(1)
    c.setFont("Courier", 9)
    row_height = 20
    
    for r in results:
        field_name = r[0]
        field_value = r[1]
        unit = r[2] if r[2] else ""
        normal_range = r[3] if r[3] else ""
        
        # Test
        c.rect(40, y - row_height, 160, row_height)
        c.drawString(45, y - 13, field_name)
        
        # Result
        c.rect(205, y - row_height, 140, row_height)
        c.setFont("Helvetica", 9)
        c.drawString(210, y - 13, str(field_value))
        c.setFont("Courier", 9)
        
        # Unit
        c.rect(350, y - row_height, 80, row_height)
        c.setFont("Helvetica", 9)
        c.drawString(355, y - 13, unit)
        c.setFont("Courier", 9)
        
        # Normal Range
        c.rect(435, y - row_height, 140, row_height)
        c.setFont("Helvetica", 9)
        c.drawString(440, y - 13, normal_range)
        c.setFont("Courier", 9)
        
        y -= row_height
    
    y -= 10
    
    # Lab Comment
    y = draw_lab_comment_box(c, lab_comment, y, width, arabic_available)
    
    # Date & Signature
    draw_date_signature_boxes(c, footer_height + 10, width)  # ✅ زيادة المسافة
    
    return y - 40


# =======================================
# Main PDF Generation Functions
# =======================================

def generate_pdf(analysis_id):
    """
    توليد PDF للتحليل الفردي
    """
    # Setup
    arabic_available = setup_arabic_font()
    
    # الاتصال بقاعدة البيانات
    conn = getdb()
    cur = conn.cursor()
    
    # جلب بيانات التحليل
    cur.execute("""
        SELECT 
            p.patient_name,
            p.patient_id_number,
            p.phone,
            p.age,
            p.gender,
            p.doctor_name,
            a.analysis_type,
            a.created_at,
            COALESCE(a.custom_name, a.analysis_type) as analysis_display_name
        FROM analysis_instances a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.id = ?
    """, (analysis_id,))
    
    analysis = cur.fetchone()
    
    if not analysis:
        conn.close()
        return None
    
    # جلب نتائج التحليل
    cur.execute("""
        SELECT field_name, field_value, unit, normal_range, field_type
        FROM results
        WHERE analysis_id = ?
        ORDER BY id
    """, (analysis_id,))
    
    results = cur.fetchall()
    
    # جلب Lab Comment
    cur.execute("""
        SELECT comment
        FROM lab_comments
        WHERE analysis_id = ?
    """, (analysis_id,))
    
    comment_row = cur.fetchone()
    lab_comment = comment_row[0] if comment_row else ""
    
    analysis_type = analysis[6]
    
    # جلب template fields إذا كان من SHOW_ALL_FIELDS
    template_fields = []
    if analysis_type in SHOW_ALL_FIELDS:
        cur.execute("""
            SELECT fields
            FROM analysis_templates
            WHERE analysis_name = ?
        """, (analysis_type,))
        
        template_row = cur.fetchone()
        if template_row:
            import json
            fields_data = json.loads(template_row[0])
            # تحويل لنفس الصيغة المتوقعة: (field_name, unit, normal_range)
            template_fields = [(f['name'], f.get('unit', ''), f.get('normal_range', '')) for f in fields_data]
    
    conn.close()
    
    # إنشاء المجلدات
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    folder_path = os.path.join(PDF_OUTPUT_DIR, year, month)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # اسم الملف - تنظيف الحروف الممنوعة في Windows
    import re
    patient_name = analysis[0].replace(" ", "_")
    patient_name = re.sub(r'[\\/:*?"<>|]', '', patient_name)
    pdf_path = os.path.join(folder_path, f"{patient_name}_{analysis_id}.pdf")
    
    # إنشاء PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Header & Footer
    header_height, footer_height = draw_header_footer(c, width, height, arabic_available)
    
    # Patient Info
    patient_data = (
        analysis[0],  # name
        analysis[1],  # id_number
        analysis[2],  # phone
        analysis[3],  # age
        analysis[4],  # gender
        analysis[5],  # doctor
        analysis[7]   # date
    )
    
    y = height - header_height - 20
    y = draw_patient_info_boxes(c, patient_data, y, width, arabic_available)
    y -= 15  # ✅ مسافة إضافية
    
    # رسم التحليل حسب النوع
    if analysis_type == 'URINE_ANALYSIS':
        draw_urine_analysis(c, results, template_fields, lab_comment, y, width, height, footer_height, arabic_available)
    
    elif analysis_type == 'SEMEN_ANALYSIS':
        draw_semen_analysis(c, results, template_fields, lab_comment, y, width, height, footer_height, arabic_available)
    
    elif analysis_type == 'STOOL_ANALYSIS':
        draw_stool_analysis(c, results, template_fields, lab_comment, y, width, height, footer_height, arabic_available)
    
    elif analysis_type == 'MICROBIOLOGY':
        draw_microbiology(c, results, template_fields, lab_comment, y, width, height, footer_height, arabic_available)
    
    elif analysis_type == 'LAP_REPORT':
        draw_lap_report(c, results, y, width, height, footer_height, arabic_available)
    
    else:
        # GENERAL template
        analysis_display_name = analysis[8]
        # إضافة كلمة Analysis
        if not analysis_display_name.endswith("Analysis"):
            analysis_display_name = analysis_display_name + " Analysis"
        draw_general_analysis(c, analysis_display_name, results, lab_comment, y, width, height, footer_height, arabic_available)
    
    # حفظ PDF
    c.save()
    
    # تحديث قاعدة البيانات
    conn = getdb()
    cur = conn.cursor()
    cur.execute("UPDATE analysis_instances SET pdf_path = ? WHERE id = ?", (pdf_path, analysis_id))
    conn.commit()
    conn.close()
    
    return pdf_path

def generate_comprehensive_pdf(patient_id):
    """
    توليد PDF شامل لكل تحاليل المريض (التحاليل العادية فقط)
    """
    # Setup
    arabic_available = setup_arabic_font()
    
    # الاتصال بقاعدة البيانات
    conn = getdb()
    cur = conn.cursor()
    
    # جلب بيانات المريض
    cur.execute("""
        SELECT patient_name, patient_id_number, phone, age, gender, doctor_name, created_at
        FROM patients
        WHERE id = ?
    """, (patient_id,))
    
    patient = cur.fetchone()
    
    if not patient:
        conn.close()
        return None
    
    # ✅ جلب التحاليل العادية فقط (استثناء المخصصة)
    STANDALONE_ANALYSES = ['URINE_ANALYSIS', 'SEMEN_ANALYSIS', 'STOOL_ANALYSIS', 'MICROBIOLOGY', 'LAP_REPORT']
    
    cur.execute("""
        SELECT 
            id,
            analysis_type,
            COALESCE(custom_name, analysis_type) as analysis_display_name
        FROM analysis_instances
        WHERE patient_id = ?
        ORDER BY created_at
    """, (patient_id,))
    
    all_analyses = cur.fetchall()
    
    # فلترة التحاليل العادية فقط
    analyses = [a for a in all_analyses if a[1] not in STANDALONE_ANALYSES]
    
    if not analyses:
        conn.close()
        return None
    
    # إنشاء المجلدات
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    folder_path = os.path.join(PDF_OUTPUT_DIR, year, month)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # اسم الملف - تنظيف الحروف الممنوعة في Windows
    import re
    patient_name = patient[0].replace(" ", "_")
    patient_name = re.sub(r'[\\/:*?"<>|]', '', patient_name)
    pdf_path = os.path.join(folder_path, f"{patient_name}_comprehensive_{patient_id}.pdf")
    
    # إنشاء PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Header & Footer
    header_height, footer_height = draw_header_footer(c, width, height, arabic_available)
    
    # Patient Info (مرة واحدة في البداية)
    patient_data = (
        patient[0],  # name
        patient[1],  # id_number
        patient[2],  # phone
        patient[3],  # age
        patient[4],  # gender
        patient[5],  # doctor
        patient[6]   # date
    )
    
    y = height - header_height - 20
    y = draw_patient_info_boxes(c, patient_data, y, width, arabic_available)
    y -= 20
    
    # ✅ تجميع كل Lab Comments
    all_comments = []
    
    # رسم كل تحليل
    for idx, analysis_row in enumerate(analyses):
        analysis_id = analysis_row[0]
        analysis_type = analysis_row[1]
        analysis_display_name = analysis_row[2]
        
        # جلب النتائج
        cur.execute("""
            SELECT field_name, field_value, unit, normal_range, field_type
            FROM results
            WHERE analysis_id = ?
            ORDER BY id
        """, (analysis_id,))
        
        results = cur.fetchall()
        
        # جلب Lab Comment
        cur.execute("""
            SELECT comment
            FROM lab_comments
            WHERE analysis_id = ?
        """, (analysis_id,))
        
        comment_row = cur.fetchone()
        if comment_row and comment_row[0]:
            all_comments.append(comment_row[0])
        
        # ✅ حساب المساحة المطلوبة
        title_space = 35  # مساحة العنوان
        header_space = 25  # مساحة headers
        min_rows = 2  # حد أدنى من الصفوف
        required_space = title_space + header_space + (min_rows * 20) + 50
        
        # ✅ التحقق من المساحة الكافية
        if y < footer_height + required_space:
            c.showPage()
            header_height, footer_height = draw_header_footer(c, width, height, arabic_available)
            y = height - header_height - 20
        
        # رسم عنوان التحليل
        y = draw_analysis_title_box(c, analysis_display_name, y, width)
        analysis_title_y = y  # حفظ موقع العنوان
        
        # رسم Headers
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.5)
        
        c.rect(40, y - 20, 160, 20)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(120, y - 13, "Test")
        
        c.rect(205, y - 20, 140, 20)
        c.drawCentredString(275, y - 13, "Result")
        
        c.rect(350, y - 20, 80, 20)
        c.drawCentredString(390, y - 13, "Unit")
        
        c.rect(435, y - 20, 140, 20)
        c.drawCentredString(505, y - 13, "Normal Range")
        
        y -= 25
        
        # البيانات
        c.setLineWidth(1)
        c.setFont("Courier", 9)
        row_height = 20
        first_row_on_page = True
        
        for r in results:
            # ✅ التحقق من المساحة قبل كل صف
            if y < footer_height + 70:
                c.showPage()
                header_height, footer_height = draw_header_footer(c, width, height, arabic_available)
                y = height - header_height - 20
                
                # ✅ إعادة رسم العنوان والـ Headers
                y = draw_analysis_title_box(c, analysis_display_name, y, width)
                
                c.setStrokeColor(colors.black)
                c.setLineWidth(1.5)
                
                c.rect(40, y - 20, 160, 20)
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(120, y - 13, "Test")
                
                c.rect(205, y - 20, 140, 20)
                c.drawCentredString(275, y - 13, "Result")
                
                c.rect(350, y - 20, 80, 20)
                c.drawCentredString(390, y - 13, "Unit")
                
                c.rect(435, y - 20, 140, 20)
                c.drawCentredString(505, y - 13, "Normal Range")
                
                y -= 25
                c.setLineWidth(1)
                c.setFont("Courier", 9)
                first_row_on_page = True
            
            field_name = r[0]
            field_value = r[1]
            unit = r[2] if r[2] else ""
            normal_range = r[3] if r[3] else ""
            
            c.rect(40, y - row_height, 160, row_height)
            c.drawString(45, y - 13, field_name)
            
            c.rect(205, y - row_height, 140, row_height)
            c.setFont("Helvetica", 9)
            c.drawString(210, y - 13, str(field_value))
            c.setFont("Courier", 9)
            
            c.rect(350, y - row_height, 80, row_height)
            c.setFont("Helvetica", 9)
            c.drawString(355, y - 13, unit)
            c.setFont("Courier", 9)
            
            c.rect(435, y - row_height, 140, row_height)
            c.setFont("Helvetica", 9)
            c.drawString(440, y - 13, normal_range)
            c.setFont("Courier", 9)
            
            y -= row_height
            first_row_on_page = False
        
        y -= 15
    
    # Lab Comment المجمّع في النهاية - يظهر دائماً حتى لو فارغ
    combined_comment = "\n".join(all_comments) if all_comments else ""

    comment_space_needed = 120
    if y < footer_height + comment_space_needed:
        c.showPage()
        header_height, footer_height = draw_header_footer(c, width, height, arabic_available)
        y = height - header_height - 20

    y = draw_lab_comment_box(c, combined_comment, y, width, arabic_available)
    
    # Date & Signature في النهاية
    draw_date_signature_boxes(c, footer_height + 10, width)
    
    # حفظ PDF
    c.save()
    conn.close()
    
    return pdf_path
