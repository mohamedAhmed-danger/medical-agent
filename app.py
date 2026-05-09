from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from software_services.User_services import UserService
from software_services.clinic_services import ClinicService   
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


@app.route('/clinics')
@login_required                              
def list_clinics():
    clinics, message = ClinicService.get_all_clinics()
    return render_template('clinics.html', clinics=clinics)


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
            return redirect(url_for('list_clinics'))   # ← fixed
        else:
            flash(message, 'danger')

    return render_template('edit_clinic.html', clinic=clinic)



if __name__ == '__main__':
    app.run(debug=True)