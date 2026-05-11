from models.models import Client, db

class ClientService:
    # this funciton is used to create a new client in the database and create
    @staticmethod
    def create_client(platform_id, page_id, sender_id, clinic_id, last_bot_replay, summary):
            existing_client = Client.query.filter_by(platform_id=platform_id, page_id=page_id, sender_id=sender_id).first()
            if existing_client:
                return None, "هذا العميل موجود بالفعل"  
            try:
                new_client = Client(
                    platform_id=platform_id,
                    page_id=page_id,
                    sender_id=sender_id,
                    clinic_id=clinic_id,
                    last_bot_replay=last_bot_replay,
                    summary=summary
                )
                db.session.add(new_client)
                db.session.commit()
                return new_client, "تم إنشاء العميل بنجاح"
            except Exception as e:
                db.session.rollback() 
                return None, f"حدث خطأ أثناء إنشاء العميل: {str(e)}"

    #this fucntion is used to update a client in the database by id
    @staticmethod
    def update_client(sender_id, platform_id,page_id,last_bot_replay=None,summary=None):
         client=Client.query.filter_by(sender_id=sender_id,platform_id=platform_id,page_id=page_id).first()
         if not client:
                return None, "العميل غير موجود"
         if last_bot_replay is not None:
            client.last_bot_replay=last_bot_replay
         if summary is not None:
            client.summary=summary
         db.session.commit()
         return client, "تم تحديث بيانات العميل بنجاح"