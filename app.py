from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from software_services.User_services import UserService
from software_services.clinic_services import ClinicService 
from software_services.doctor_services import DoctorService  
from models.models import db, User


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

if __name__ == '__main__':
    app.run(debug=True)