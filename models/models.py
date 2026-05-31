from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from enum import Enum

db = SQLAlchemy()

DEFAULT_COUNT = 0
RESET_DAYS = 30



class Status(Enum):
    PENDING = "Pending"
    REVIEWED = "Reviewed"
    ATTENDED = "Attended"
    NO_SHOW = "No Show"

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class Clinic(db.Model):
    __tablename__ = 'clinics'
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    info    = db.Column(db.String(200), nullable=False)

    doctors    = db.relationship('Doctor',    backref='clinic', lazy=True)
    specialties = db.relationship('Specialty', backref='clinic', lazy=True)
    services   = db.relationship('Service',   backref='clinic', lazy=True)
    pages      = db.relationship('Page',      backref='clinic', lazy=True)


class Doctor(db.Model):
    __tablename__ = 'doctors'
    id          = db.Column(db.Integer, primary_key=True)
    clinic_id   = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    doctor_info = db.Column(db.String(200), nullable=False)


class Specialty(db.Model):
    __tablename__ = 'specialties'
    id        = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    name      = db.Column(db.String(100), nullable=False)
    details   = db.Column(db.String(200))


class Service(db.Model):
    __tablename__ = 'services'
    id          = db.Column(db.Integer, primary_key=True)
    clinic_id   = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price       = db.Column(db.Float, nullable=False)


class Platform(db.Model):
    __tablename__ = 'platforms'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    pages = db.relationship('Page', backref='platform', lazy=True)


class Page(db.Model):
    __tablename__ = 'pages'
    __table_args__ = (
        PrimaryKeyConstraint('platform_id', 'page_id'),
    )
    clinic_id   = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), nullable=False)
    page_id     = db.Column(db.String(100), nullable=False)
    token       = db.Column(db.String(200), nullable=False)

    clients = db.relationship('Client', backref='page', lazy=True)


class Client(db.Model):
    __tablename__ = 'clients'
    __table_args__ = (
        PrimaryKeyConstraint('platform_id', 'page_id', 'sender_id'),
        ForeignKeyConstraint(
            ['platform_id', 'page_id'],
            ['pages.platform_id', 'pages.page_id']
        ),
    )

    platform_id      = db.Column(db.Integer, nullable=False)
    page_id          = db.Column(db.String(100), nullable=False)
    sender_id        = db.Column(db.String(100), nullable=False)
    summary          = db.Column(db.Text)
    last_bot_message = db.Column(db.Text)
    expiration_date  = db.Column(db.DateTime)


class Complaint(db.Model):
    __tablename__ = 'complaints'
    id             = db.Column(db.Integer, primary_key=True)
    phone_number   = db.Column(db.String(20), nullable=False)
    complaint_text = db.Column(db.Text, nullable=False)
    status         = db.Column(db.Enum(Status), default=Status.PENDING)  
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    comes_from     = db.Column(db.String(100))


class Examination(db.Model):
    __tablename__ = 'examinations'
    id           = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    symptom_text = db.Column(db.Text)
    status       = db.Column(db.Enum(Status), default=Status.PENDING)  
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    comes_from   = db.Column(db.String(100))

    

class Booking(db.Model):
    __tablename__ = 'bookings'
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    details      = db.Column(db.Text)
    date         = db.Column(db.String(100))
    phone_number = db.Column(db.String(50))
    status       = db.Column(db.Enum(Status), default=Status.PENDING)
    booking_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    comes_from   = db.Column(db.String(100))
    page_id      = db.Column(db.String(100), nullable=True)
    platform_id  = db.Column(db.Integer, nullable=True)


class RequestCounter(db.Model):
    __tablename__ = 'request_counter'
    id           = db.Column(db.Integer, primary_key=True)
    count        = db.Column(db.Integer, default=DEFAULT_COUNT, nullable=False)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_reset   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def decrement(self):
        now = datetime.now(timezone.utc)
        if self.last_reset and (now - self.last_reset) >= timedelta(days=RESET_DAYS):
            self.count        = DEFAULT_COUNT
            self.last_reset   = now
            self.last_updated = now

        if self.count > 0:
            self.count -= 1

        if self.count == 0:
            self.notify()
            self.count = DEFAULT_COUNT

        self.last_updated = now
        db.session.commit()     # single commit

    def notify(self):
        from email_sender import EmailSender
        EmailSender.EmailClient.send_email(
            subject="Billing rate",
            body="This is a reminder for exceeding the limit",
        )