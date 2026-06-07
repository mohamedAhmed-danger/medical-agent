from models.models import Page, db

class PageService:
#this fucntion to display all pages in the database
    @staticmethod
    def get_all_pages():
        pages = Page.query.all()
        return pages, "تم العثور على جميع الصفحات"
    
    #this function is used to get a page by id and platform id
    @staticmethod
    def get_page_by_id(platform_id, page_id):
        page_obj = Page.query.filter_by(platform_id=platform_id, page_id=page_id).first()
        if page_obj:
            return page_obj, "تم العثور على الصفحة"
        return None, "الصفحة غير موجودة"


    #this function is used to create a new page in the database
    @staticmethod
    def create_page(clinic_id, platform_id, page_id, token):
        existing_page = Page.query.filter_by(platform_id=platform_id, page_id=page_id).first()
        if existing_page:
            return None, "هذه الصفحة موجودة بالفعل"
        try:
            new_page = Page(
                clinic_id=clinic_id,
                platform_id=platform_id,
                page_id=page_id,
                token=token
            )
            db.session.add(new_page)
            db.session.commit()
            return new_page, "تم إنشاء الصفحة بنجاح"
        except Exception as e:
            db.session.rollback()
            return None, f"حدث خطأ أثناء إنشاء الصفحة: {str(e)}"
    #this function is used to update a page by id and platform id    
    @staticmethod
    def update_page(page_id, clinic_id=None, platform_id=None, token=None):
        page_obj = Page.query.filter_by(clinic_id=clinic_id, platform_id=platform_id, page_id=page_id).first()
        if not page_obj:
            return None, "الصفحة غير موجودة"
        try:
            page_obj.token = token
            db.session.commit()
            return page_obj, "تم تحديث الصفحة بنجاح"
        except Exception as e:
            db.session.rollback()
            return None, f"حدث خطأ أثناء تحديث الصفحة: {str(e)}"    
