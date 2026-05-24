"""
===============================================
إضافة أطباء افتراضيين لقاعدة البيانات
===============================================
"""

from models.database import getdb


def seed_doctors():
    """
    إضافة أطباء افتراضيين
    """
    
    conn = getdb()
    cur = conn.cursor()

    # =======================================
    # قائمة الأطباء الافتراضيين
    # =======================================
    doctors = [
        ("د. حسام قويدر", ""),
        ("د. محمد قويدر", ""),
        ("د. ديب الراعي", ""),
    ]

    # =======================================
    # إضافة الأطباء
    # =======================================
    for doctor_name, specialization in doctors:
        cur.execute("""
            INSERT OR IGNORE INTO doctors (doctor_name, specialization, is_active)
            VALUES (?, ?, 1)
        """, (doctor_name, specialization))

    # =======================================
    # حفظ وإغلاق
    # =======================================
    conn.commit()
    conn.close()
    
    print("✅ Doctors seeded successfully.")


if __name__ == "__main__":
    seed_doctors()