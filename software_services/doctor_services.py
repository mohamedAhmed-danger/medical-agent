from models.models import Doctor, db

class DoctorService:
    # this function is used to create a new doctor in the database
    @staticmethod
    def create_doctor(name, doctor_info, clinic_id):
      name=name.strip().lower
      existing_doctor = Doctor.query.filter_by(name=name, clinic_id=clinic_id).first()
      if existing_doctor:
          return None, "يوجد طبيب آخر بنفس هذا الاسم في العيادة"
      
      try:
          new_doctor = Doctor(
          name=name,
          doctor_info=doctor_info,
          clinic_id=clinic_id
                             )

          db.session.add(new_doctor)
          db.session.commit()
          return new_doctor, "تم إنشاء الطبيب بنجاح"
      except Exception as e:
            db.session.rollback() 
            return None, f"حدث خطأ أثناء إنشاء الطبيب: {str(e)}"
    # this function is used to get a doctor by id
    @staticmethod
    def get_doctor_by_id(doctor_id):
        doctor = Doctor.query.get(doctor_id)

        if doctor:
            return doctor, "تم العثور على الطبيب"
        else:
            return None, "الطبيب غير موجود"

    # this function is used to get all doctors in the database
    @staticmethod
    def get_all_doctors():
        doctors = Doctor.query.all()

        return doctors, "تم العثور على جميع الأطباء"

    # this function is used to update a doctor by id
    @staticmethod
    def update_doctor(doctor_id, name=None, doctor_info=None):
        doctor = Doctor.query.get(doctor_id)

        if not doctor:
            return None, "الطبيب غير موجود"

        if name :
            name=name.strip().lower()
            existing_doctor = Doctor.query.filter_by(name=name, clinic_id=doctor.clinic_id).first()
            if existing_doctor and existing_doctor.id != doctor.id:
                return None, "يوجد طبيب آخر بنفس هذا الاسم في العيادة"
            doctor.name = name

        if doctor_info is not None:
            doctor.doctor_info = doctor_info
        try:
          db.session.commit()
          return doctor, "تم تحديث الطبيب بنجاح"
        except Exception as e:
          db.session.rollback()
          return None, f"حدث خطأ أثناء تحديث الطبيب: {str(e)}"
