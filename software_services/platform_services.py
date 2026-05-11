from models.models import  Platform, db


class PlatformService:

      # this function is used to create a new platform in the database
        @staticmethod
        def create_platform(id, name):
            exiting_platform = Platform.query.filter_by(name=name).first()
            if exiting_platform:
                return None, "يوجد منصة أخرى بنفس هذا الاسم"
            try:
                new_platform = Platform(
                    id=id,
                    name=name
                )

                db.session.add(new_platform)
                db.session.commit()
                return new_platform, "تم إنشاء المنصة بنجاح"
            except Exception as e:
                db.session.rollback() 
                return None, f"حدث خطأ أثناء إنشاء المنصة: {str(e)}"
            

        # this function to get all platforms in the database
        @staticmethod
        def get_all_platforms():
            platforms = Platform.query.all()

            return platforms, "تم العثور على جميع المنصات"
        #this function is used to update a platform by id
        @staticmethod
        def update_platform(platform_id, name=None):
            platform = Platform.query.get(platform_id)

            if not platform:
                return None, "المنصة غير موجودة"

            if name:
                existing_platform = Platform.query.filter_by(name=name).first()
                if existing_platform and existing_platform.id != platform.id:
                    return None, "يوجد منصة أخرى بنفس هذا الاسم"
                platform.name = name

            try:
                db.session.commit()
                return platform, "تم تحديث المنصة بنجاح"
            except Exception as e:
                db.session.rollback() 
                return None, f"حدث خطأ أثناء تحديث المنصة: {str(e)}"