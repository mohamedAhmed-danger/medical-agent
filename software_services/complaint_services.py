from models.models import Complaint, Status, db
from datetime import datetime, timezone


class ComplaintService:

    @staticmethod
    def get_all_complaints(page=1, per_page=10, search=None, status=None):
        query = Complaint.query

        if search:
            query = query.filter(
                db.or_(
                    Complaint.phone_number.ilike(f'%{search}%'),
                    Complaint.complaint_text.ilike(f'%{search}%'),
                )
            )

        if status:
            query = query.filter(Complaint.status == Status(status))

        query = query.order_by(Complaint.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination, "تم العثور على الشكاوى"

    @staticmethod
    def get_complaint_details(complaint_id):
        complaint = db.session.get(Complaint, complaint_id)
        if not complaint:
            return None, "الشكوى غير موجودة"
        return complaint, "تم العثور على الشكوى"

    @staticmethod
    def update_complaint_status(complaint_id, new_status: Status):
        complaint = db.session.get(Complaint, complaint_id)
        if not complaint:
            return None, "الشكوى غير موجودة"
        try:
            complaint.status = new_status
            db.session.commit()
            return complaint, "تم تحديث الحالة"
        except Exception as e:
            db.session.rollback()
            return None, f"حدث خطأ: {str(e)}"

    @staticmethod
    def save_complaint(phone_number: str, complaint_text: str, comes_from: str = "unknown") -> str:
        try:
            complaint = Complaint(
                phone_number=phone_number,
                complaint_text=complaint_text,
                comes_from=comes_from,
            )
            db.session.add(complaint)
            db.session.commit()
            return (
                f"تم تسجيل شكواك بنجاح ✅\n"
                f"رقم هاتفك: {phone_number}\n"
                f"سيتواصل معك فريقنا في أقرب وقت ممكن."
            )
        except Exception as e:
            db.session.rollback()
            return f"حدث خطأ أثناء حفظ الشكوى: {str(e)}"