from sqlalchemy.exc import IntegrityError   # FIX #12: was imported from sqlite3

from models.models import Client, db


class ClientService:

    @staticmethod
    def create_client(platform_id, page_id, sender_id, last_bot_message, summary):
        existing = Client.query.filter_by(
            platform_id=platform_id, page_id=page_id, sender_id=sender_id
        ).first()
        if existing:
            return None, "هذا العميل موجود بالفعل"
        try:
            new_client = Client(
                platform_id=platform_id,
                page_id=page_id,
                sender_id=sender_id,
                last_bot_message=last_bot_message,
                summary=summary,
            )
            db.session.add(new_client)
            db.session.commit()
            return new_client, "تم إنشاء العميل بنجاح"
        except Exception as e:
            db.session.rollback()
            return None, f"حدث خطأ أثناء إنشاء العميل: {str(e)}"

    @staticmethod
    def update_client(sender_id, platform_id, page_id,
                      last_bot_message=None, summary=None):
        client = Client.query.filter_by(
            sender_id=sender_id, platform_id=platform_id, page_id=page_id
        ).first()
        if not client:
            return None, "العميل غير موجود"
        try:
            if last_bot_message is not None:
                client.last_bot_message = last_bot_message
            if summary is not None:
                client.summary = summary
            db.session.commit()
            return client, "تم تحديث بيانات العميل بنجاح"
        except Exception as e:
            db.session.rollback()
            return None, f"حدث خطأ أثناء تحديث العميل: {str(e)}"

    @staticmethod
    def get_client(sender_id, platform_id, page_id):
        client = Client.query.filter_by(
            sender_id=sender_id, platform_id=platform_id, page_id=page_id
        ).first()
        if not client:
            return None, "العميل غير موجود"
        return client, "تم العثور على العميل بنجاح"

    @staticmethod
    def get_or_create_client(sender_id, page_id, platform_id) -> Client:
        client = Client.query.filter_by(
            sender_id=sender_id, page_id=page_id, platform_id=platform_id
        ).first()
        if not client:
            try:
                client = Client(
                    sender_id=sender_id,
                    page_id=page_id,
                    platform_id=platform_id,
                )
                db.session.add(client)
                db.session.commit()
            except IntegrityError:
           
                db.session.rollback()
                client = Client.query.filter_by(
                    sender_id=sender_id, page_id=page_id, platform_id=platform_id
                ).first()
        return client

    @staticmethod
    def update_client_summary_and_last_bot_message(
        sender_id, page_id, platform_id, summary, last_bot_message
    ):
    
        client = ClientService.get_or_create_client(sender_id, page_id, platform_id)
        try:
            client.summary          = summary          or ""
            client.last_bot_message = last_bot_message or ""
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"[ClientService] Failed to persist client state: {e}")
        return client