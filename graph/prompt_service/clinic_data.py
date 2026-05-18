from models.models import Clinic, Page


class ClinicDataService:

    @staticmethod
    def get_clinic_object(page_id):
        try:
            return Clinic.query.join(Page).filter(Page.page_id == page_id).first()
        except Exception as e:
            print(f"[ClinicDataService] DB error in get_clinic_object: {e}")
            return None

   
    @staticmethod
    def get_all_clinic_data(page_id) -> tuple[str, str, str]:
        clinic = ClinicDataService.get_clinic_object(page_id)

        if not clinic:
            return (
                "No doctors found.",
                "No specialties found.",
                "No services found.",
            )

        # Doctors
        doctors_info = "\n\n".join(
            f"Doctor Name: {d.name}\nDoctor Info: {d.doctor_info}"
            for d in clinic.doctors
        ) or "No doctors found."

        # Specialties
        specialties_info = "\n\n".join(
            f"Specialty Name: {s.name}\nSpecialty Details: {s.details}"
            for s in clinic.specialties
        ) or "No specialties found."

        # Services
        services_info = "\n\n".join(
            f"Service Name: {sv.name}\nService Description: {sv.description}\nService Price: {sv.price}"
            for sv in clinic.services
        ) or "No services found."

        return doctors_info, specialties_info, services_info

   

    @staticmethod
    def get_clinic_info(page_id) -> str:
        clinic = ClinicDataService.get_clinic_object(page_id)
        if clinic:
            return (
                f"Clinic Name: {clinic.name}\n"
                f"Address: {clinic.address}\n"
                f"Info: {clinic.info}"
            )
        return "No clinic found for the given page ID."

    @staticmethod
    def get_doctors_info(page_id) -> str:
        clinic = ClinicDataService.get_clinic_object(page_id)
        if not clinic:
            return "No doctors found."
        return "\n\n".join(
            f"Doctor Name: {d.name}\nDoctor Info: {d.doctor_info}"
            for d in clinic.doctors
        ) or "No doctors found."

    @staticmethod
    def get_specialties_info(page_id) -> str:
        clinic = ClinicDataService.get_clinic_object(page_id)
        if not clinic:
            return "No specialties found."
        return "\n\n".join(
            f"Specialty Name: {s.name}\nSpecialty Details: {s.details}"
            for s in clinic.specialties
        ) or "No specialties found."

    @staticmethod
    def get_services_info(page_id) -> str:
        clinic = ClinicDataService.get_clinic_object(page_id)
        if not clinic:
            return "No services found."
        return "\n\n".join(
            f"Service Name: {sv.name}\n"
            f"Service Description: {sv.description}\n"
            f"Service Price: {sv.price}"
            for sv in clinic.services
        ) or "No services found."