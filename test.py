from models.models import db
from app import app
from sqlalchemy import text

with app.app_context():
    with db.engine.begin() as conn:
        # تأكيد تحويل أي قيمة NULL إلى PENDING
        conn.execute(text("UPDATE complaints SET status = 'PENDING' WHERE status IS NULL"))
        print("Done updating NULL values!")