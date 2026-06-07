from models.models import Examination, Status, db
from datetime import datetime, timezone


class ExaminationService:

    @staticmethod
    def get_all_examinations(page=1, per_page=10, search=None, status=None):
        query = Examination.query

        if search:
            query = query.filter(
                db.or_(
                    Examination.phone_number.ilike(f'%{search}%'),
                    Examination.symptom_text.ilike(f'%{search}%'),
                )
            )

        if status:
            query = query.filter(Examination.status == Status(status))

        query = query.order_by(Examination.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination, "تم العثور على الفحوصات"

    @staticmethod
    def get_examination_details(examination_id):
        examination = db.session.get(Examination, examination_id)
        if not examination:
            return None, "الفحص غير موجود"
        return examination, "تم العثور على الفحص"

    @staticmethod
    def update_examination_status(examination_id, new_status: Status):
        examination = db.session.get(Examination, examination_id)
        if not examination:
            return None, "الفحص غير موجود"
        try:
            examination.status = new_status
            db.session.commit()
            return examination, "تم تحديث الحالة"
        except Exception as e:
            db.session.rollback()
            return None, f"حدث خطأ: {str(e)}"

    @staticmethod
    def save_examination(phone_number: str, symptom_text: str, comes_from: str = "unknown") -> str:
        try:
            examination = Examination(
                phone_number=phone_number,
                symptom_text=symptom_text,
                comes_from=comes_from,
            )
            db.session.add(examination)
            db.session.commit()
            return (
                f"تم تسجيل فحصك بنجاح ✅\n"
                f"رقم هاتفك: {phone_number}\n"
                f"سيتواصل معك فريقنا في أقرب وقت ممكن."
            )
        except Exception as e:
            db.session.rollback()
            return f"حدث خطأ أثناء حفظ الفحص: {str(e)}"