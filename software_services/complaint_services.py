# FIX #8: Removed stray import from inside the class body — all imports at top
from models.models import Complaint, db
from datetime import datetime, timezone


class ComplaintService:

    @staticmethod
    def get_all_complaints():
        return Complaint.query.order_by(Complaint.created_at.desc()).all()

    @staticmethod
    def get_complaint_by_id(complaint_id):
        return db.session.get(Complaint, complaint_id)

    @staticmethod
    def get_unresolved_complaints():
        complaints = (
            Complaint.query
            .filter_by(is_resolved=False)
            .order_by(Complaint.created_at.desc())
            .all()
        )
        return complaints, "تم العثور على الشكاوى"

    @staticmethod
    def get_complaint_details(complaint_id):
        complaint = db.session.get(Complaint, complaint_id)
        if not complaint:
            return None, "الشكوى غير موجودة"
        return complaint, "تم العثور على الشكوى بنجاح"

    @staticmethod
    def create_complaint(message, phone_number, comes_from="unknown"):

        new_complaint = Complaint(
            phone_number=phone_number,
            complaint_text=message,
            comes_from=comes_from
        )
        db.session.add(new_complaint)
        db.session.commit()
        return new_complaint.id      

    @staticmethod
    def resolve_complaint(complaint_id):
        complaint = db.session.get(Complaint, complaint_id)
        if not complaint:
            return False, "الشكوى غير موجودة"
        complaint.is_resolved = True
        complaint.resolved_at = datetime.now(timezone.utc)
        db.session.commit()
        return True, "تم حل الشكوى بنجاح"

    @staticmethod
    def update_complaint_status(complaint_id, is_resolved):
        complaint = db.session.get(Complaint, complaint_id)
        if not complaint:
            return False, "الشكوى غير موجودة"
        complaint.is_resolved = is_resolved
        complaint.resolved_at = datetime.now(timezone.utc) if is_resolved else None
        db.session.commit()
        return True, "تم تحديث حالة الشكوى"

   
    @staticmethod
    def save_complaint(phone_number: str, complaint_text: str, comes_from: str = "unknown") -> str:
        try:
            complaint = Complaint(
                phone_number=phone_number,
                complaint_text=complaint_text,
                is_resolved=False,
                created_at=datetime.now(timezone.utc),
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