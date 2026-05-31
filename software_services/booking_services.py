from models.models import Booking,Status, db
from datetime import datetime, timezone, timedelta


class BookingService:

    @staticmethod
    def create_booking(name, details, date, phone_number, comes_from=None):
        try:
            new_booking = Booking(
                name=name,
                details=details,
                date=date,
                phone_number=phone_number,
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
    def display_bookings(page=1, per_page=10, search=None, status=None, date_from=None, date_to=None):
        before_30_days = datetime.now(timezone.utc) - timedelta(days=30)
        query = Booking.query.filter(Booking.booking_time >= before_30_days)

        if search:
            query = query.filter(
                db.or_(
                    Booking.name.ilike(f'%{search}%'),
                    Booking.phone_number.ilike(f'%{search}%'),
                )
            )

        if status:
            query = query.filter(Booking.status == Status(status))

        if date_from:
            query = query.filter(Booking.date >= date_from)

        if date_to:
            query = query.filter(Booking.date <= date_to)

        query = query.order_by(Booking.booking_time.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination, "تم العثور على الحجوزات"

    @staticmethod
    def get_booking_by_id(booking_id):
        booking = db.session.get(Booking, booking_id)
        if booking:
            return booking, "تم العثور على الحجز"
        return None, "الحجز غير موجود"

    @staticmethod
    def update_booking_status(booking_id, new_status: Status):
        booking = db.session.get(Booking, booking_id)
        if not booking:
            return None, "الحجز غير موجود"
        try:
            booking.status = new_status
            db.session.commit()
            return booking, "تم تحديث الحالة"
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