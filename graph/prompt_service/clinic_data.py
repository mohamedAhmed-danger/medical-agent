# graph/prompt_service/clinec_data.py
from models.models import Clinic, Page

# get clinic object to get form it data for clinic and tables related with it
class ClinicDataService:
    @staticmethod
    def get_clinic_object(page_id):
        return Clinic.query.join(Page).filter(Page.page_id == page_id).first()
    

    @staticmethod
    def get_clinic_info(page_id):
        Clinic_data = ClinicDataService.get_clinic_object(page_id)
        if Clinic_data:
            return f"Clinic Name: {Clinic_data.name}\nAddress: {Clinic_data.address}\nInfo: {Clinic_data.info}"

        else:
            return " No clinic found for the given page ID."
        
    @staticmethod
    def get_doctors_info(page_id):
        Clinic_data = ClinicDataService.get_clinic_object(page_id)
        if Clinic_data:
            doctors_info = []
            for doctor in Clinic_data.doctors:
                doctors_info.append(f"Doctor Name: {doctor.name}\nDoctor Info: {doctor.doctor_info}")
            return "\n\n".join(doctors_info)
        else:
            return "No doctors found."
    @staticmethod
    def get_specialties_info(page_id):
        Clinic_data = ClinicDataService.get_clinic_object(page_id)
        if Clinic_data:
            specialties_info = []
            for specialty in Clinic_data.specialties:
                specialties_info.append(f"Specialty Name: {specialty.name}\nSpecialty Details: {specialty.details}")
            return "\n\n".join(specialties_info)
        else:
            return "No specialties found."

    @staticmethod
    def get_services_info(page_id):
        Clinic_data = ClinicDataService.get_clinic_object(page_id)
        if Clinic_data:
            services_info = []
            for service in Clinic_data.services:
                services_info.append(f"Service Name: {service.name}\nService Description: {service.description}\nService Price: {service.price}")
            return "\n\n".join(services_info)
        else:
            return "No services found."        
