"""
software_services/booking_services.py
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from models.models import Booking, Status, db


# ── result dataclass ──────────────────────────────────────────────────────────

@dataclass
class BookingSaveResult:
    reference_id: str
    pdf_bytes:    bytes
    booking_id:   int


# ── private helpers ───────────────────────────────────────────────────────────

def _make_reference_id() -> str:
    """Generates a short unique ID like BK-A3F2-91C0."""
    raw = uuid.uuid4().hex.upper()
    return f"BK-{raw[:4]}-{raw[4:8]}"


# ── service ───────────────────────────────────────────────────────────────────

class BookingService:

    # ── create (used by dashboard / admin) ────────────────────────────────────

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

    # ── read ──────────────────────────────────────────────────────────────────

    @staticmethod
    def display_bookings(page=1, per_page=10, search=None,
                         status=None, date_from=None, date_to=None):
        before_30_days = datetime.now(timezone.utc) - timedelta(days=30)
        query = Booking.query.filter(Booking.booking_time >= before_30_days)

        if search:
            query = query.filter(
                db.or_(
                    Booking.name.ilike(f"%{search}%"),
                    Booking.phone_number.ilike(f"%{search}%"),
                )
            )
        if status:
            query = query.filter(Booking.status == Status(status))
        if date_from:
            query = query.filter(Booking.date >= date_from)
        if date_to:
            query = query.filter(Booking.date <= date_to)

        pagination = query.order_by(
            Booking.booking_time.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        return pagination, "تم العثور على الحجوزات"

    @staticmethod
    def get_booking_by_id(booking_id):
        booking = db.session.get(Booking, booking_id)
        if booking:
            return booking, "تم العثور على الحجز"
        return None, "الحجز غير موجود"

    @staticmethod
    def get_booking_by_reference(reference_id: str):
        booking = Booking.query.filter_by(reference_id=reference_id).first()
        if booking:
            return booking, "تم العثور على الحجز"
        return None, "الحجز غير موجود"

    # ── update ────────────────────────────────────────────────────────────────

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
    def update_booking(booking_id, **fields):
        """
        Update any combination of booking fields.

        Usage:
            BookingService.update_booking(5, name="Ahmed", date="2025-01-20")
        """
        allowed = {"name", "phone_number", "details", "date", "comes_from", "status"}
        booking = db.session.get(Booking, booking_id)
        if not booking:
            return None, "الحجز غير موجود"
        try:
            for key, value in fields.items():
                if key in allowed:
                    setattr(booking, key, value)
            db.session.commit()
            return booking, "تم تحديث الحجز"
        except Exception as e:
            db.session.rollback()
            return None, f"حدث خطأ: {str(e)}"

    # ── save (called by the agent after user confirms) ─────────────────────────

    @staticmethod
    def save_booking(
        name: str,
        phone: str,
        date: str,
        details: str,
        comes_from: str,
    ) -> BookingSaveResult:
        """
        Persist a confirmed booking.
        Returns BookingSaveResult(reference_id, pdf_bytes, booking_id).
        Raises on failure — caller handles the error message.
        """
        from graph.utils import generate_booking_pdf

        reference_id = _make_reference_id()

        booking = Booking(
            name=name,
            phone_number=phone,
            date=date,
            details=details,
            comes_from=comes_from,
            reference_id=reference_id,
            booking_time=datetime.now(timezone.utc),
        )
        db.session.add(booking)
        db.session.commit()

        pdf_bytes = generate_booking_pdf(
            name=name,
            phone=phone,
            date=date,
            details=details,
            reference_id=reference_id,
        )

        return BookingSaveResult(
            reference_id=reference_id,
            pdf_bytes=pdf_bytes,
            booking_id=booking.id,
        )