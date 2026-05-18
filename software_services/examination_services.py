from models.models import Examination, db
from datetime import datetime

class ExaminationService:
    # this function is used to create a new examination in the database
    @staticmethod
    def create_examination(phone_number, symptom_text,comes_from="unknown"):
        try:
            new_examination = Examination(
                phone_number=phone_number,
                symptom_text=symptom_text,
                comes_from=comes_from
            )
            db.session.add(new_examination)
            db.session.commit()
            return new_examination, "تم إنشاء الفحص بنجاح"
        except Exception as e:
            db.session.rollback()
            return None, f"حدث خطأ أثناء إنشاء الفحص: {str(e)}"
    # this function is used to get all unreviewed examinations
    @staticmethod
    def get_unreviewed_examination():          
        examinations = Examination.query.filter_by(is_reviewed=False)\
                                        .order_by(Examination.created_at.desc())\
                                        .all()
        return examinations, "تم العثور على الفحوصات غير المراجعة"
    

    # this function is used to get examination details by id
    @staticmethod
    def get_examination_details(examination_id):
        examination = Examination.query.get(examination_id)
        if examination:
            return examination, "تم العثور على تفاصيل الفحص"
        else:
            return None, "الفحص غير موجود"

    # this function is used to update the review status of an examination by id 
    @staticmethod
    def update_examination_status(examination_id, is_reviewed):  # ← مضافة
        try:
            examination = Examination.query.get(examination_id)
            if not examination:
                return False, "الفحص غير موجود"
            examination.is_reviewed = is_reviewed
            if is_reviewed:
                examination.reviewed_at = datetime.utcnow()
            else:
                examination.reviewed_at = None
            db.session.commit()
            return True, "تم تحديث حالة الفحص"
        except Exception as e:
            db.session.rollback()
            return False, f"حدث خطأ: {str(e)}"