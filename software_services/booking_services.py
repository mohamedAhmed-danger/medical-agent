from models.models import Booking, db
from datetime import datetime, timezone, timedelta


class BookingService:

    @staticmethod
    def create_booking(name, details, date, phone_number, are_received=False, comes_from=None):
        try:
            new_booking = Booking(
                name=name,
                details=details,
                date=date,
                phone_number=phone_number,
                are_received=are_received,
                comes_from=comes_from,
                booking_time=datetime.now(timezone.utc),
            )
            db.session.add(new_booking)
            db.session.commit()
            return new_booking, "تم إنشاء الحجز بنجاح"
        except Exception as e:
            db.session.rollback()
            return None, f"حدث خطأ: {str(e)}"

    @staticmethod
    def display_bookings():
        try:
            before_yesterday = datetime.now(timezone.utc) - timedelta(days=2)
            bookings = Booking.query.filter(
                Booking.booking_time >= before_yesterday
            ).all()
            return bookings, "تم العثور على الحجوزات"
        except Exception as e:
            return None, f"حدث خطأ: {str(e)}"

    @staticmethod
    def get_booking_by_id(booking_id):
        booking = db.session.get(Booking, booking_id)
        if booking:
            return booking, "تم العثور على الحجز"
        return None, "الحجز غير موجود"

    @staticmethod
    def update_booking_received(booking_id, status):
        # FIX #5: same Query.get() fix
        booking = db.session.get(Booking, booking_id)
        if not booking:
            return None, "الحجز غير موجود"
        try:
            booking.are_received = status
            db.session.commit()
            return booking, "تم تحديث الحجز"
        except Exception as e:
            db.session.rollback()
            return None, f"حدث خطأ: {str(e)}"

    @staticmethod
    def save_booking(name: str, phone: str, date: str, details: str, comes_from: str) -> str:
       
        try:
            booking = Booking(
                name=name,
                phone_number=phone,      
                date=date,
                details=details,
                comes_from=comes_from,
                booking_time=datetime.now(timezone.utc),
            )
            db.session.add(booking)
            db.session.commit()
            return (
                f"تم حجز موعدك بنجاح ✅\n"
                f"الاسم: {name}\n"
                f"التاريخ: {date}\n"
                f"سيتم التواصل معك على {phone}"
            )
        except Exception as e:
            db.session.rollback()
            return f"حدث خطأ أثناء حفظ الحجز: {str(e)}"