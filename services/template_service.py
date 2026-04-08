"""
===============================================
خدمة إدارة قوالب التحاليل
===============================================
"""

import json
from models.database import getdb


def seed_templates():
    """
    إضافة القوالب الأساسية لقاعدة البيانات
    
    القوالب المتوفرة:
    -----------------
    1. HEMATOLOGY - تحليل الدم الشامل
    2. HORMONES - تحليل الهرمونات
    3. CLINICAL_CHEMISTRY - الكيمياء السريرية
    4. SEMEN_ANALYSIS - تحليل السائل المنوي
    5. STOOL_ANALYSIS - تحليل البراز
    6. URINE_ANALYSIS - تحليل البول
    7. TUMOR_MARKERS - علامات الأورام
    8. SERO_IMMU - الفحوصات المناعية
    9. SERO_VIROLOGY - الفحوصات الفيروسية
    10. MICROBIOLOGY - الزراعة والحساسية
    11. GENERAL - قالب عام مخصص
    """
    
    conn = getdb()
    cur = conn.cursor()

    # =======================================
    # 1. HEMATOLOGY REPORT
    # =======================================
    hematology_fields = [
        {"name": "hb", "unit": "gm/dl", "normal_range": ""},
        {"name": "rbc", "unit": "x 10³/μL", "normal_range": ""},
        {"name": "mcv", "unit": "Fl", "normal_range": ""},
        {"name": "wbc", "unit": "x 10³/μL", "normal_range": ""},
        {"name": "platelets", "unit": "x 10³/μL", "normal_range": ""},
    ]
    
    cur.execute("""
        INSERT OR IGNORE INTO analysis_templates (analysis_name, fields)   
        VALUES (?, ?)
    """, ("HEMATOLOGY", json.dumps(hematology_fields)))

    # =======================================
    # 2. HORMONES REPORT
    # =======================================
    hormones_fields = [
        {"name": "total_t4", "unit": "ug/dl", "normal_range": "Adult: 4.5-12.0"},
        {"name": "total_t3", "unit": "ng/ml", "normal_range": "0.65-1.75"},
        {"name": "free_t4", "unit": "ng/dl", "normal_range": "0.7-1.85"},
        {"name": "free_t3", "unit": "pg/mL", "normal_range": "1.4-3.5"},
        {"name": "tsh", "unit": "mIU/ml", "normal_range": "0.5-5.0"},
        {"name": "prolactin", "unit": "ng/ml", "normal_range": "Male: 0.9-20.9 / Female: 2.4-25.2"},
        {"name": "fsh", "unit": "mIU/ml", "normal_range": "Male: 2.0-10.0 / Follicular: 2.0-10.0"},
        {"name": "lh", "unit": "mIU/ml", "normal_range": "Male: 1.0-13.2 / Follicular: 1.2-20.0"},
        {"name": "beta_hcg", "unit": "mIU/ml", "normal_range": "Nonpregnant: 0.0-5.0"},
        {"name": "progesterone", "unit": "ng/ml", "normal_range": "Luteal phase: 4.0-25.0"},
        {"name": "total_testosterone", "unit": "ng/ml", "normal_range": "Male: 2.5-10.5 / Female: 0.3-0.95"},
    ]
    
    cur.execute("""
        INSERT OR IGNORE INTO analysis_templates (analysis_name, fields)   
        VALUES (?, ?)
    """, ("HORMONES", json.dumps(hormones_fields)))

    # =======================================
    # 3. CLINICAL CHEMISTRY REPORT
    # =======================================
    clinical_chemistry_fields = [
        {"name": "glucose_fasting", "unit": "mg/dL", "normal_range": ""},
        {"name": "glucose_2hr", "unit": "mg/dL", "normal_range": "< 140"},
        {"name": "glucose_random", "unit": "mg/dL", "normal_range": "Dependent on last meal"},
        {"name": "hba1c", "unit": "%", "normal_range": "Excellent Control < 7.0"},
        {"name": "urea", "unit": "mg/dL", "normal_range": ""},
        {"name": "creatinine", "unit": "mg/dL", "normal_range": ""},
        {"name": "uric_acid", "unit": "mg/dL", "normal_range": ""},
        {"name": "calcium", "unit": "mg/dL", "normal_range": ""},
        {"name": "magnesium", "unit": "mg/dL", "normal_range": ""},
        {"name": "phosphorus", "unit": "mg/dL", "normal_range": ""},
        {"name": "cholesterol", "unit": "mg/dL", "normal_range": "Desirable: < 220"},
        {"name": "hdl", "unit": "mg/dL", "normal_range": ""},
        {"name": "ldl", "unit": "mg/dL", "normal_range": "Desirable: < 130"},
        {"name": "triglycerides", "unit": "mg/dL", "normal_range": "Desirable: < 200"},
        {"name": "total_protein", "unit": "g/dL", "normal_range": ""},
        {"name": "albumin", "unit": "g/dL", "normal_range": ""},
        {"name": "bilirubin_total", "unit": "mg/dL", "normal_range": ""},
        {"name": "bilirubin_direct", "unit": "mg/dL", "normal_range": ""},
        {"name": "alkaline_phosphatase", "unit": "U/L", "normal_range": ""},
        {"name": "alt_agpt", "unit": "U/L", "normal_range": ""},
        {"name": "ast_agot", "unit": "U/L", "normal_range": ""},
        {"name": "ldh", "unit": "U/L", "normal_range": ""},
        {"name": "cpk", "unit": "U/L", "normal_range": ""},
    ]
    
    cur.execute("""
        INSERT OR IGNORE INTO analysis_templates (analysis_name, fields)   
        VALUES (?, ?)
    """, ("CLINICAL_CHEMISTRY", json.dumps(clinical_chemistry_fields)))

    # =======================================
    # 4. SEMEN ANALYSIS REPORT
    # =======================================
    semen_analysis_fields = [
        {"name": "period", "unit": "Days", "normal_range": ""},
        {"name": "volume", "unit": "mL", "normal_range": ""},
        {"name": "appearance", "unit": "", "normal_range": ""},
        {"name": "viscosity", "unit": "", "normal_range": ""},
        {"name": "liquefaction", "unit": "min", "normal_range": ""},
        {"name": "sperm_count", "unit": "mill/mL", "normal_range": ""},
        {"name": "ph", "unit": "", "normal_range": ""},
        {"name": "rbc_hpf", "unit": "/HPF", "normal_range": ""},
        {"name": "wbc_hpf", "unit": "/HPF", "normal_range": ""},
        {"name": "grade_a", "unit": "%", "normal_range": ""},
        {"name": "grade_b", "unit": "%", "normal_range": ""},
        {"name": "grade_c", "unit": "%", "normal_range": ""},
        {"name": "grade_d", "unit": "%", "normal_range": ""},
        {"name": "sperm_morphology", "unit": "", "normal_range": ""},
        {"name": "spermatocyte_hpf", "unit": "/HPF", "normal_range": ""},
    ]
    
    cur.execute("""
        INSERT OR IGNORE INTO analysis_templates (analysis_name, fields)   
        VALUES (?, ?)
    """, ("SEMEN_ANALYSIS", json.dumps(semen_analysis_fields)))

    # =======================================
    # 5. STOOL ANALYSIS REPORT
    # =======================================
    stool_analysis_fields = [
        {"name": "color", "unit": "", "normal_range": ""},
        {"name": "consistency", "unit": "", "normal_range": ""},
        {"name": "ph", "unit": "", "normal_range": ""},
        {"name": "mucous", "unit": "", "normal_range": ""},
        {"name": "rbcs", "unit": "", "normal_range": ""},
        {"name": "wbcs", "unit": "", "normal_range": ""},
        {"name": "parasites", "unit": "", "normal_range": ""},
    ]
    
    cur.execute("""
        INSERT OR IGNORE INTO analysis_templates (analysis_name, fields)   
        VALUES (?, ?)
    """, ("STOOL_ANALYSIS", json.dumps(stool_analysis_fields)))

    # =======================================
    # 6. URINE ANALYSIS REPORT
    # =======================================
    urine_analysis_fields = [
        {"name": "color", "unit": "", "normal_range": ""},
        {"name": "appearance", "unit": "", "normal_range": ""},
        {"name": "specific_gravity", "unit": "", "normal_range": ""},
        {"name": "ph", "unit": "", "normal_range": ""},
        {"name": "glucose", "unit": "", "normal_range": ""},
        {"name": "protein", "unit": "", "normal_range": ""},
        {"name": "ketones", "unit": "", "normal_range": ""},
        {"name": "bilirubin", "unit": "", "normal_range": ""},
        {"name": "urobilinogen", "unit": "", "normal_range": ""},
        {"name": "blood", "unit": "", "normal_range": ""},
        {"name": "nitrite", "unit": "", "normal_range": ""},
        {"name": "wbc_hpf", "unit": "/HPF", "normal_range": ""},
        {"name": "rbc_hpf", "unit": "/HPF", "normal_range": ""},
        {"name": "epithelial_cells_hpf", "unit": "/HPF", "normal_range": ""},
        {"name": "casts_lpf", "unit": "/LPF", "normal_range": ""},
        {"name": "crystals", "unit": "", "normal_range": ""},
        {"name": "mucous", "unit": "", "normal_range": ""},
        {"name": "amorphous", "unit": "", "normal_range": ""},
        {"name": "bacteria", "unit": "", "normal_range": ""},
        {"name": "yeast", "unit": "", "normal_range": ""},
        {"name": "parasites", "unit": "", "normal_range": ""},
    ]
    
    cur.execute("""
        INSERT OR IGNORE INTO analysis_templates (analysis_name, fields)   
        VALUES (?, ?)
    """, ("URINE_ANALYSIS", json.dumps(urine_analysis_fields)))

    # =======================================
    # 7. TUMOR MARKERS
    # =======================================
    tumor_markers_fields = [
        {"name": "cea", "unit": "ng/ml", "normal_range": "Adult < 5.0"},
        {"name": "psa", "unit": "ng/mL", "normal_range": "Up to 4.1"},
        {"name": "ca_15_3", "unit": "U/mL", "normal_range": "Healthy Female: 0-28"},
        {"name": "ca_125", "unit": "U/mL", "normal_range": "Healthy Female: 0-35"},
        {"name": "ca_19_9", "unit": "U/mL", "normal_range": "Healthy Less Than 37"},
        {"name": "alpha_feroprotien", "unit": "ng/ml", "normal_range": "Adult Healthy: 0-10"},
    ]
    
    cur.execute("""
        INSERT OR IGNORE INTO analysis_templates (analysis_name, fields)   
        VALUES (?, ?)
    """, ("TUMOR_MARKERS", json.dumps(tumor_markers_fields)))

    # =======================================
    # 8. SERO - IMMU
    # =======================================
    sero_immu_fields = [
        {"name": "pregnancy_test", "unit": "", "normal_range": "Negative"},
        {"name": "h_pylori", "unit": "", "normal_range": "Negative"},
        {"name": "rf", "unit": "IU/ml", "normal_range": "< 8"},
        {"name": "crp", "unit": "mg/L", "normal_range": "< 6"},
        {"name": "asot", "unit": "IU/ml", "normal_range": "< 200"},
        {"name": "vdrl", "unit": "", "normal_range": "Negative"},
        {"name": "rw", "unit": "", "normal_range": "Negative"},
        {"name": "brucella", "unit": "", "normal_range": "Negative"},
        {"name": "proteus_ox_19", "unit": "", "normal_range": "< 1/160"},
        {"name": "monospot", "unit": "", "normal_range": "Negative"},
        {"name": "le_cells", "unit": "", "normal_range": "Negative"},
        {"name": "widal_th", "unit": "", "normal_range": "< 1/100"},
        {"name": "widal_ah", "unit": "", "normal_range": "< 1/100"},
        {"name": "widal_bh", "unit": "", "normal_range": "< 1/100"},
        {"name": "widal_to", "unit": "", "normal_range": "< 1/100"},
        {"name": "widal_ao", "unit": "", "normal_range": "< 1/100"},
        {"name": "widal_bo", "unit": "", "normal_range": "< 1/100"},
    ]
    
    cur.execute("""
        INSERT OR IGNORE INTO analysis_templates (analysis_name, fields)   
        VALUES (?, ?)
    """, ("SERO_IMMU", json.dumps(sero_immu_fields)))

    # =======================================
    # 9. SERO - VIROLOGY
    # =======================================
    sero_virology_fields = [
        {"name": "hbsag", "unit": "", "normal_range": ""},
        {"name": "hbeag", "unit": "", "normal_range": ""},
        {"name": "hbcigm", "unit": "", "normal_range": ""},
        {"name": "hbcab_total", "unit": "", "normal_range": ""},
        {"name": "hbeab", "unit": "", "normal_range": ""},
        {"name": "hbsab", "unit": "", "normal_range": ""},
        {"name": "hav_igm", "unit": "", "normal_range": ""},
        {"name": "hcv", "unit": "", "normal_range": ""},
        {"name": "hiv_1_and_2", "unit": "", "normal_range": ""},
        {"name": "toxoplasmosis_igm", "unit": "", "normal_range": "Negativ Index: < 1.0"},
        {"name": "toxoplasmosis_igg", "unit": "IU/mL", "normal_range": "Up to 50.0"},
        {"name": "rubella_igm", "unit": "MU/mL", "normal_range": "Negative: < 70"},
        {"name": "rubella_igg", "unit": "IU/mL", "normal_range": "Up to 10.0"},
        {"name": "cmv_igm", "unit": "", "normal_range": "Negative Index: UP to 0.85"},
        {"name": "cmv_igg", "unit": "IU/mL", "normal_range": "UP to 6.0"},
        {"name": "chlamydia_igm", "unit": "IU/mL", "normal_range": "Negative: < 1.0"},
        {"name": "chlamydia_igg", "unit": "IU/mL", "normal_range": "Up to 10.0"},
        {"name": "chlamydia_iga", "unit": "IU/mL", "normal_range": "Up to 10.0"},
        {"name": "ebv_igm", "unit": "", "normal_range": ""},
        {"name": "ebv_igg", "unit": "", "normal_range": ""},
        {"name": "mycoplasma_igg", "unit": "", "normal_range": ""},
    ]
    
    cur.execute("""
        INSERT OR IGNORE INTO analysis_templates (analysis_name, fields)   
        VALUES (?, ?)
    """, ("SERO_VIROLOGY", json.dumps(sero_virology_fields)))

    # =======================================
    # 10. MICROBIOLOGY
    # =======================================
    microbiology_fields = [
        # المعلومات الأساسية
        {"name": "specimen", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Urine", "Pus", "Semen", "Blood", "Prostatic Secretion"]},
        
        {"name": "count", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["20,000", "30,000", "40,000", "50,000", "60,000", "70,000", "80,000", "90,000", "> 100,000"]},
        
        {"name": "gram_stain", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Positive", "Negative"]},
        
        {"name": "organism", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Streptococcus pyogenes", "Streptococcus pneumonia", "Staphylococcus aureus", 
                     "Haemophilus influenzae", "Klebsilla species", "Pseudomonas species", 
                     "Proteus species", "Staphylococcus epidermidis", "E.scherichia coli", 
                     "Shigella species", "Hemolytic streptococci", "Enterococci group", 
                     "Negative culture for bacteria"]},
        
        # المضادات الحيوية - كلهم نفس الخيارات
        {"name": "penicillin_g", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "ampicillin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "amoxycillin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "cloxacillin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "piperacillin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "erythromycin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "clindamycin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "cephalexin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "cefuroxime", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "cefotaxime", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "ceftazidim", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "aztreofloxacin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "aztreonam", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "ceftriaxone", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "cephazolin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "amikacin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "ofloxacin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "augmantin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "gentamicin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "tetracycline", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "chloramphenicol", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "septrin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "nalidixic", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "ciprofloxacin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "polymyxin_b", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "neomycin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "rifampicin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "vancomycin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "rovamycin", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "minocyline", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "ceclor", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "nitro_furantion", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
        {"name": "doxycycline", "unit": "", "normal_range": "", "type": "dropdown",
         "options": ["Resistant", "Intermediate", "Sensitive"]},
    ]
    
    cur.execute("""
        INSERT OR IGNORE INTO analysis_templates (analysis_name, fields)   
        VALUES (?, ?)
    """, ("MICROBIOLOGY", json.dumps(microbiology_fields)))

    # =======================================
    # 11. LAP REPORT (تقرير مختبر حر)
    # =======================================
    # قالب خاص: عنوان + نص طويل فقط (بدون unit و normal_range)
    lap_report_fields = [
        {"name": "title", "type": "text", "label": "Report Title"},
        {"name": "content", "type": "textarea", "label": "Report Content"},
    ]
    
    cur.execute("""
        INSERT OR IGNORE INTO analysis_templates (analysis_name, fields)   
        VALUES (?, ?)
    """, ("LAP_REPORT", json.dumps(lap_report_fields)))

    # =======================================
    # 12. GENERAL REPORT (قالب عام مخصص)
    # =======================================
    general_fields = [
        {"name": "field_1", "unit": "", "normal_range": ""},
        {"name": "field_2", "unit": "", "normal_range": ""},
        {"name": "field_3", "unit": "", "normal_range": ""},
        {"name": "field_4", "unit": "", "normal_range": ""},
        {"name": "field_5", "unit": "", "normal_range": ""},
    ]
    
    cur.execute("""
        INSERT OR IGNORE INTO analysis_templates (analysis_name, fields)   
        VALUES (?, ?)
    """, ("GENERAL", json.dumps(general_fields)))

    # =======================================
    # حفظ وإغلاق
    # =======================================
    conn.commit()
    conn.close()
    
    print("✅ Templates seeded successfully.")


if __name__ == "__main__":
    seed_templates()