from models.models import Service, db

class ServiceService:
    # this function is used to create a new service in db

    def create_service(name, description, clinic_id, price):
        exiting_service = Service.query.filter_by(name=name, clinic_id=clinic_id).first()
        if exiting_service:
            return None, "يوجد خدمة أخرى بنفس هذا الاسم في العيادة"
        try:
            new_service = Service(
                name=name,
                description=description,
                clinic_id=clinic_id,
                price=price
            )
    
            db.session.add(new_service)
            db.session.commit()
            return new_service, "تم إنشاء الخدمة بنجاح"
        except Exception as e:
            db.session.rollback() 
            return None, f"حدث خطأ أثناء إنشاء الخدمة: {str(e)}"
        
    # this function is used to get a service by id
    def get_service_by_id(service_id):
        service = Service.query.get(service_id)

        if service:
            return service, "تم العثور على الخدمة"
        else:
            return None, "الخدمة غير موجودة"
    # this function is used to get all services in the database
    def get_all_services():
        services = Service.query.all()

        return services, "تم العثور على جميع الخدمات"

    # this function is used to update a service by id    
    def update_service(service_id, name=None, description=None, price=None):
        service = Service.query.get(service_id)

        if not service:
            return None, "الخدمة غير موجودة"

        if name:
            existing_service = Service.query.filter_by(name=name, clinic_id=service.clinic_id).first()
            if existing_service and existing_service.id != service.id:
                return None, "يوجد خدمة أخرى بنفس هذا الاسم في العيادة"
            service.name = name

        if description is not None:
            service.description = description

        if price is not None:
            service.price = price

        try:
            db.session.commit()
            return service, "تم تحديث الخدمة بنجاح"
        except Exception as e:
            db.session.rollback() 
            return None, f"حدث خطأ أثناء تحديث الخدمة: {str(e)}"

           