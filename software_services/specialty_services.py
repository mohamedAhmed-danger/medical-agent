from models.models import  Specialty, db


class SpecialtyService:
    # this function is used to create a new specialty in the database
    @staticmethod
    def create_specialty(name,details,clinic_id):
    
        try:
          new_specialty = Specialty(
            name=name,
            details=details,
            clinic_id=clinic_id
          )

          db.session.add(new_specialty)
          db.session.commit()
          return new_specialty, "تم إنشاء التخصص بنجاح"
        except Exception as e:
          db.session.rollback() 
        return None, f"حدث خطأ أثناء إنشاء التخصص: {str(e)}"

    # this function is to get a specialty by id
    @staticmethod
    def get_specialty_by_id(specialty_id):
        specialty = Specialty.query.get(specialty_id)

        if specialty:
            return specialty, "تم العثور على التخصص"
        else:
            return None, "التخصص غير موجود"
    # this function is used to get all specialties in the database
    @staticmethod
    def get_all_specialties():
        specialties = Specialty.query.all()

        return specialties, "تم العثور على جميع التخصصات" 

    # this function is used to update a specialty by id
    
    @staticmethod
    def update_specialty(specialty_id, name=None, details=None):
        specialty = Specialty.query.get(specialty_id)
        if not specialty:
            return None, "التخصص غير موجود"

        if name:
            # نتأكد إن الاسم الجديد مش مستخدم في نفس عيادة التخصص ده
            name=name.strip().lower()
            existing = Specialty.query.filter_by(name=name, clinic_id=specialty.clinic_id).first()
            if existing and existing.id != specialty.id:
                return None, "يوجد تخصص آخر بنفس هذا الاسم في العيادة"
            specialty.name = name

        if details is not None:
            specialty.details = details

        try:
            db.session.commit()
            return specialty, "تم تحديث التخصص بنجاح"
        except Exception as e:
            db.session.rollback()
            return None, "فشل تحديث البيانات"              