"""
===============================================
Routes الخاصة بإدارة الأطباء
===============================================
إضافة وحذف فقط - بسيط جداً
"""

from flask import Blueprint, render_template, request, redirect
from models.database import getdb
from config import DB_NAME

doctors_bp = Blueprint('doctors', __name__)


@doctors_bp.route("/manage-doctors", methods=["GET"])
def manage_doctors():
    """
    صفحة إدارة الأطباء
    """
    
    conn = getdb()
    cur = conn.cursor()
    
    # ✅ نعرض بس النشطين (is_active = 1)
    cur.execute("""
        SELECT id, doctor_name
        FROM doctors
        WHERE is_active = 1
        ORDER BY doctor_name
    """)
    
    doctors = cur.fetchall()
    conn.close()
    
    return render_template("manage_doctors.html", doctors=doctors)


@doctors_bp.route("/add-doctor", methods=["POST"])
def add_doctor():
    """
    إضافة طبيب جديد
    """
    
    doctor_name = request.form.get("doctor_name", "").strip()
    
    if not doctor_name:
        return redirect("/manage-doctors")
    
    conn = getdb()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO doctors (doctor_name, is_active)
            VALUES (?, 1)
        """, (doctor_name,))
        
        conn.commit()
    except:
        pass  # إذا الاسم مكرر، تجاهل
    
    conn.close()
    return redirect("/manage-doctors")


@doctors_bp.route("/delete-doctor/<int:doctor_id>", methods=["POST"])
def delete_doctor(doctor_id):
    """
    حذف طبيب
    
    ملاحظة: الحذف soft delete (is_active = 0)
    عشان البيانات التاريخية تبقى سليمة
    """
    
    conn = getdb()
    cur = conn.cursor()
    
    # ✅ soft delete - عشان السجلات القديمة ما تتأثر
    cur.execute("""
        UPDATE doctors
        SET is_active = 0
        WHERE id = ?
    """, (doctor_id,))
    
    conn.commit()
    conn.close()
    
    return redirect("/manage-doctors")