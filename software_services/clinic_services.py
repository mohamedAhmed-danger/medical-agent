from models.models import Clinic, db


class ClinicService:

    # this function is used to create a new clinic in the database
    @staticmethod
    def create_clinic(name, address, info):
        new_clinic = Clinic(name=name, address=address, info=info)

        db.session.add(new_clinic)
        db.session.commit()

        return new_clinic, "تم إنشاء العيادة بنجاح"

    # this function is used to get a clinic by id
    @staticmethod
    def get_clinic_by_id(clinic_id):
        clinic = Clinic.query.get(clinic_id)

        if clinic:
            return clinic, "تم العثور على العيادة"
        else:
            return None, "العيادة غير موجودة"

    # this function is used to get all clinics in the database
    @staticmethod
    def get_all_clinics():
        clinics = Clinic.query.all()

        return clinics, "تم العثور على جميع العيادات"

    # this function is used to update a clinic by id
    @staticmethod
    def update_clinic(clinic_id, name=None, address=None, info=None):
        clinic = Clinic.query.get(clinic_id)

        if not clinic:
            return None, "العيادة غير موجودة"

        if name is not None:
            clinic.name = name

        if address is not None:
            clinic.address = address

        if info is not None:
            clinic.info = info

        db.session.commit()

        return clinic, "تم تحديث العيادة بنجاح"