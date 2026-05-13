import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from software_services.User_services import UserService
from software_services.clinic_services import ClinicService 
from software_services.complaint_services import ComplaintService
from software_services.doctor_services import DoctorService  
from software_services.specialty_services import SpecialtyService
from software_services.service_services import ServiceService
from software_services.platform_services import PlatformService
from software_services.page_services import PageService
from software_services.booking_services import BookingService
from models.models import db, User
from flask import request, abort
from models.models import Page
from parsers.facebook import parse_facebook_message
from platfroms.facebook_handler import FacebookHandler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical_agent.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

login_manager = LoginManager(app)
db.init_app(app)
migrate = Migrate(app, db)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


#  AUTH

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users'))

    if request.method == 'POST':
        name     = request.form['name']
        password = request.form['password']
        user, message = UserService.login_user(name, password)

        if user:
            login_user(user)
            flash(message, 'success')
            return redirect(url_for('users'))
        else:
            flash(message, 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('login'))


#  USERS

@app.route('/users')
@login_required
def users():
    all_users = UserService.get_all_users()
    return render_template('users.html', users=all_users)


@app.route('/users/new', methods=['GET', 'POST'])
@login_required
def create_user():
    if request.method == 'POST':
        name     = request.form['name']
        password = request.form['password']
        user, message = UserService.create_user(name, password)
        if user:
            flash(message, 'success')
            return redirect(url_for('users'))
        else:
            flash(message, 'danger')

    return render_template('create_user.html')


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user, message = UserService.get_user_by_id(user_id)

    if not user:
        flash(message, 'danger')
        return redirect(url_for('users'))

    if request.method == 'POST':
        name     = request.form['name']
        password = request.form['password']
        updated_user, message = UserService.update_user(user_id, name, password)

        if updated_user:
            flash(message, 'success')
            return redirect(url_for('users'))
        else:
            flash(message, 'danger')

    return render_template('edit_user.html', user=user)


#  CLINICS

#this route is used to display all clinics
@app.route('/clinics')
@login_required                              
def list_clinics():
    clinics, message = ClinicService.get_all_clinics()
    return render_template('clinics.html', clinics=clinics)

#this route is used to create a new clinic and save it in the database
@app.route('/clinics/new', methods=['GET', 'POST'])
@login_required                              
def create_clinic():
    if request.method == 'POST':
        name    = request.form['name']
        address = request.form['address']
        info    = request.form['info']
        clinic, message = ClinicService.create_clinic(name, address, info)

        if clinic:
            flash(message, 'success')
            return redirect(url_for('list_clinics'))  
        else:
            flash(message, 'danger')

    return render_template('create_clinic.html')

#this route is used to edit a clinic by id and update it in the database
@app.route('/clinics/<int:clinic_id>/edit', methods=['GET', 'POST'])   
@login_required                                                       
def edit_clinic(clinic_id):
    clinic, message = ClinicService.get_clinic_by_id(clinic_id)

    if not clinic:
        flash(message, 'danger')
        return redirect(url_for('list_clinics'))       

    if request.method == 'POST':
        name    = request.form['name']
        address = request.form['address']
        info    = request.form['info']
        updated_clinic, message = ClinicService.update_clinic(clinic_id, name, address, info)

        if updated_clinic:
            flash(message, 'success')
            return redirect(url_for('list_clinics'))   
        else:
            flash(message, 'danger')

    return render_template('edit_clinic.html', clinic=clinic)
# end of clinic routes

#  DOCTORS

#this route is used to display all doctors
@app.route('/doctors')
@login_required
def list_doctors():
    doctors, message = DoctorService.get_all_doctors()
    return render_template('doctors.html', doctors=doctors)


#this route is used to create a new doctor and save it in the database
@app.route('/doctors/new', methods=['GET', 'POST'])
@login_required
def create_doctor():
    clinics, _ = ClinicService.get_all_clinics()

    if request.method == 'POST':
        name = request.form['name']
        doctor_info = request.form['doctor_info']
        clinic_id = request.form['clinic_id']

        doctor, message = DoctorService.create_doctor(
            name,
            doctor_info,
            clinic_id
        )

        if doctor:
            flash(message, 'success')
            return redirect(url_for('list_doctors'))
        else:
            flash(message, 'danger')

    return render_template(
        'create_doctor.html',
        clinics=clinics
    )

#this route is used to edit a doctor by id and update it in the database
@app.route('/doctors/<int:doctor_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_doctor(doctor_id):
    doctor, message = DoctorService.get_doctor_by_id(doctor_id)

    if not doctor:
        flash(message, 'danger')
        return redirect(url_for('list_doctors'))       

    if request.method == 'POST':
        name      = request.form['name']
        doctor_info = request.form['doctor_info']
        updated_doctor, message = DoctorService.update_doctor(doctor_id, name, doctor_info)

        if updated_doctor:
            flash(message, 'success')
            return redirect(url_for('list_doctors'))   
        else:
            flash(message, 'danger')

    return render_template('edit_doctor.html', doctor=doctor)

# end of doctor routes

#sepcialties routes

#this route is used to display all specialties
@app.route('/specialties')
@login_required
def list_specialties():
    specialties, message = SpecialtyService.get_all_specialties()
    return render_template('specialties.html', specialties=specialties)

#this route is used to create a new specialty and save it in the database
@app.route('/specialties/new', methods=['GET', 'POST'])
@login_required
def create_specialty():
    clinics, _ = ClinicService.get_all_clinics()

    if request.method == 'POST':
        name = request.form['name']
        details = request.form['details']
        clinic_id = request.form['clinic_id']

        specialty, message = SpecialtyService.create_specialty(
            name,
            details,
            clinic_id
        )

        if specialty:
            flash(message, 'success')
            return redirect(url_for('list_specialties'))
        else:
            flash(message, 'danger')

    return render_template(
        'create_specialty.html',
        clinics=clinics
    )

    #this route is used to edit a specialty by id and update it in the database
@app.route('/specialties/<int:specialty_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_specialty(specialty_id):
    specialty, message = SpecialtyService.get_specialty_by_id(specialty_id)

    if not specialty:
        flash(message, 'danger')
        return redirect(url_for('list_specialties'))       

    if request.method == 'POST':
        name      = request.form['name']
        details   = request.form['details']
        updated_specialty, message = SpecialtyService.update_specialty(specialty_id, name, details)

        if updated_specialty:
            flash(message, 'success')
            return redirect(url_for('list_specialties'))   
        else:
            flash(message, 'danger')

    return render_template('edit_specialty.html', specialty=specialty)    




# end of specialty routes
# services routes
# this route is used to display all services
@app.route('/services')
@login_required
def list_services():
    services, message = ServiceService.get_all_services()
    return render_template('services.html', services=services)

# this route is used to create a new service and save it in the database
@app.route('/services/new', methods=['GET', 'POST'])
@login_required
def create_service():
    clinics, _ = ClinicService.get_all_clinics()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        clinic_id = request.form['clinic_id']

        service, message = ServiceService.create_service(
            name,
            description,
            clinic_id,
            price
        )

        if service:
            flash(message, 'success')
            return redirect(url_for('list_services'))
        else:
            flash(message, 'danger')

    return render_template(
        'create_service.html',
        clinics=clinics
    )

# this route is used to edit a service by id and update it in the database
@app.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    service, message = ServiceService.get_service_by_id(service_id)

    if not service:
        flash(message, 'danger')
        return redirect(url_for('list_services'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        updated_service, message = ServiceService.update_service(service_id, name, description, price)

        if updated_service:
            flash(message, 'success')
            return redirect(url_for('list_services'))
        else:
            flash(message, 'danger')

    return render_template('edit_service.html', service=service)

# end of services routes

# platforms routes

# this route is used to display all platforms
@app.route('/platforms')
@login_required
def list_platforms():
    platforms, message = PlatformService.get_all_platforms()
    return render_template('platforms.html', platforms=platforms)


# this route is used to create a new platform and save it in the database
@app.route('/platforms/new', methods=['GET', 'POST'])
@login_required
def create_platform():
    if request.method == 'POST':
        name = request.form['name']
        platform, message= PlatformService.create_platform(name)
        if platform:
            flash(message, 'success')
            return redirect(url_for('list_platforms'))
        else:
            flash(message, 'danger')
    return render_template('create_platform.html')

@app.route('/platforms/<int:platform_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_platform(platform_id):
    platform, message = PlatformService.get_platform_by_id(platform_id)

    if not platform:
        flash(message, 'danger')
        return redirect(url_for('list_platforms'))

    if request.method == 'POST':
        name = request.form['name']

        updated_platform, message = PlatformService.update_platform(platform_id, name)

        if updated_platform:
            flash(message, 'success')
            return redirect(url_for('list_platforms'))
        else:
            flash(message, 'danger')

    return render_template('edit_platform.html', platform=platform)

# end of platforms routes
#  pages routes

# this route is used to display the pages
@app.route('/pages')
@login_required
def list_pages():
    pages, message = PageService.get_all_pages()
    return render_template('pages.html', pages=pages)
#this route to add page
@app.route('/pages/new', methods=['GET', 'POST'])
@login_required
def create_page():
    if request.method == 'POST':
        clinic_id = request.form['clinic_id']
        platform_id = request.form['platform_id']
        page_id = request.form['page_id']
        token = request.form['token']
        page, message = PageService.create_page(clinic_id, platform_id, page_id, token)
        if page:
            flash(message, 'success')
            return redirect(url_for('list_pages'))
        else:
            flash(message, 'danger')

    clinics, _ = ClinicService.get_all_clinics()
    platforms, _ = PlatformService.get_all_platforms()
    return render_template('create_page.html', clinics=clinics, platforms=platforms)

# this route is used to edit a page by id and update it in the database
@app.route('/pages/<int:platform_id>/<page_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_page(platform_id, page_id):
    page, message = PageService.get_page_by_id(platform_id=platform_id, page_id=page_id)
    if not page:
        flash(message, 'danger')
        return redirect(url_for('list_pages'))

    if request.method == 'POST':
        clinic_id = request.form['clinic_id']
        platform_id_new = request.form['platform_id']
        token = request.form['token']
        updated_page, message = PageService.update_page(
            page_id=page.page_id,
            clinic_id=clinic_id,
            platform_id=platform_id_new,
            token=token
        )
        if updated_page:
            flash(message, 'success')
            return redirect(url_for('list_pages'))
        else:
            flash(message, 'danger')

    clinics, _ = ClinicService.get_all_clinics()
    platforms, _ = PlatformService.get_all_platforms()
    return render_template('edit_page.html', page=page, clinics=clinics, platforms=platforms)
# end of pages routes

#this is route for display the bookings
@app.route('/bookings')
@login_required
def list_bookings():
    bookings, message = BookingService.display_bookings()
    return render_template('bookings.html', bookings=bookings)

#this is route for make toggle
@app.route('/bookings/toggle_received/<int:booking_id>', methods=['POST'])
@login_required
def toggle_booking_received(booking_id):
    booking, message = BookingService.get_booking_by_id(booking_id)
    if not booking:
        flash(message, 'danger')
        return redirect(url_for('list_bookings'))

    updated_booking, message = BookingService.update_booking_received(booking_id, not booking.are_received)
    if updated_booking:
        flash(message, 'success')
    else:
        flash(message, 'danger')

    return redirect(url_for('list_bookings'))

# end of bookings routes

# complaints routes

# this route is to display the complaints is not resolved
@app.route('/complaints')
@login_required
def list_complaints():
    complaints, message = ComplaintService.get_unresolved_complaints()
    return render_template('complaints.html', complaints=complaints)


# this route is to display the complaint details
@app.route('/complaints/<int:complaint_id>', methods=['GET', 'POST'])
@login_required
def complaint_details(complaint_id):

    complaint, message = ComplaintService.get_complaint_details(complaint_id)

    if request.method == 'POST':

        is_resolved = request.form.get('is_resolved') == 'on'

        success, message = ComplaintService.update_complaint_status(
            complaint_id,
            is_resolved
        )

        return redirect(url_for('list_complaints'))

    return render_template(
        'complaint_details.html',
        complaint=complaint
    )

VERIFY_TOKEN = "dangerMo"
@app.route("/webhook/facebook", methods=["GET", "POST"])
def fb_webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge", "")
        abort(403)

    try:
        payload = request.json
        page_id = payload["entry"][0]["id"]
        page    = Page.query.filter_by(page_id=page_id).first()
        if not page:
            return "page not found", 404

        handler = FacebookHandler(page)
        message = parse_facebook_message(payload, page.page_id, handler.platform_id)

        if message:
            reply = handler.handle(message)
            if reply:
                handler.send(message.sender_id, reply)

    except Exception as e:
        import traceback
        print("WEBHOOK ERROR:", traceback.format_exc())  # ← هيطبع الـ error كامل

    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)
