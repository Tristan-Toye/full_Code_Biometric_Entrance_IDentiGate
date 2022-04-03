from werkzeug import security

from flask_info import app, db, time_based_pin
from flask import render_template, redirect, url_for, flash, session
from flask_info.models import User,Log, Role, CustomUserManager, QR, QR_VISITOR
from flask_info.forms import RegisterForm, LoginForm, QR_code_self_Form, GoogleAuthenticatorForm, ChangeRoleForm, RegisterFormEmployee, QR_make_visitor
from flask_login import login_user, logout_user
from flask_user import roles_required, login_required, current_user
from flask_info.constants import *
from flask_info.functions import create_specific_qr_combination, function_filter_hash, generate_qr_leave
from flask_info.decorators import required_path,reset_session, add_url,check_register_admin

import os
import io
import base64
user_manager = CustomUserManager(app, db, User)


@app.before_first_request
def before_first_request():
    print('before_first_request')
    session['face_validated'] = False
    session['password_validated'] = False
    session['attemped_user'] = ''
    session['url_path']=['']
    session['counter_google_auth'] = 0
    session['user_to_create'] = None
    session['correct_faces'] = []
    session['face_registration_complete'] = False


@app.route("/home")
@app.route("/")
@reset_session
@add_url
def home():
    return render_template('home.html')


@app.route("/home/login", methods=["GET", "POST"])
@add_url
def login():
    form = LoginForm()
    if form.validate_on_submit():

        attemped_user = User.query.filter_by(email_address=form.email_address.data).first()

        if attemped_user and user_manager.verify_password(form.password.data,attemped_user.password):

           # staff => password
           # security => password
           # recruiting => password and google authenticater
           # admin => password, facial and google authenticater

            if attemped_user.roles[0].name =='staff':
                login_user(attemped_user)
                flash(f"Successfull login as {attemped_user.roles[0].name}",category='success')
                return redirect(url_for('home'))
            elif any(attemped_user.roles[0].name == role for role in ['recruiter','security']):
                session['attemped_user'] = attemped_user.username
                session['password_validated'] = True
                return redirect(url_for('time_based_authentication'))
            elif(attemped_user.roles[0].name == 'admin'):# admin
                session['attemped_user'] = attemped_user.username
                session['password_validated'] = True
                return redirect(url_for('face_recognition_admin'))
            else:
                print(f"this role has not been implemented yet : {attemped_user.roles[0].name}")
                flash("something went wrong!",category='info')
                return redirect(url_for('home'))

        else:

            flash("Email address or password incorrect, please try again", category='danger')

    elif form.errors != {}:  # dictionary
        for err_msg in form.errors.values():
            flash(err_msg, category='danger')


    return render_template('login.html',form = form)


@app.route('/home/face_recognition_admin')
@required_path
@add_url
def face_recognition_admin():
    return render_template('face_validation_Java.html')



@app.route('/home/time_based_authentication',methods=["GET","POST"])
@required_path

def time_based_authentication():

    form = GoogleAuthenticatorForm()
    if form.validate_on_submit():

        if time_based_pin.verify(form.time_based_pincode.data):

            attemped_user = User.query.filter_by(username=session.get('attemped_user')).first()
            login_user(attemped_user)
            flash(f"Successfull login as {attemped_user.roles[0].name}", category='success')
            return redirect(url_for('home'))
        else:

            session['counter_google_auth'] +=1
            if session.get('counter_google_auth') == max_attempts_google_auth:
                flash("To many attempts",category='danger')
                return redirect(url_for('home'))

            flash(f"Invalid code, try again: {max_attempts_google_auth - session.get('counter_google_auth')} attempts left", category='info')
    elif form.errors != {}:  # dictionary
        for err_msg in form.errors.values():
            flash(err_msg, category='danger')

    return render_template('time_based_authentication.html',form = form)




@app.route('/home/logout')
@reset_session
@login_required
@add_url
def logout():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for('home'))





@app.route("/home/register_staff", methods=["GET","POST"])
@reset_session
@add_url
@roles_required(['admin','recruiter'])
def register_staff():
    form = RegisterForm()
    if form.validate_on_submit():
        national_number = function_filter_hash(form.national_number.data)
        code = os.urandom(10).hex()
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password = user_manager.hash_password(form.password1.data),
            national_number=national_number,
            qr_leave = generate_qr_leave(national_number,code),
            qr_leave_code = code
            
        )

        user_to_create.roles.append(Role.query.filter_by(name='staff').first())

        db.session.add(user_to_create)
        db.session.commit()

        flash(f"Successfully added {user_to_create.username} as {user_to_create.roles[0].name} to the system", category='success')
        return redirect(url_for('home'))

    elif form.errors != {}: # dictionary
        for err_msg in form.errors.values():
            flash(err_msg,category='danger')

    return render_template('register.html',form = form)

@app.route('/home/register_employee',methods=["GET","POST"])
@reset_session
@roles_required('admin')
@add_url
def register_employee():
    form = RegisterFormEmployee()
    if form.validate_on_submit():

        national_number = function_filter_hash(form.national_number.data)
        code = os.urandom(10).hex()
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password = user_manager.hash_password(form.password1.data),
            national_number=national_number,
            qr_leave = generate_qr_leave(national_number,code),
            qr_leave_code = code
        )

        user_to_create.roles.append(Role.query.filter_by(name=form.role.data).first())
        if form.role.data == 'admin':
            session['user_to_create'] = user_to_create

            return redirect(url_for('register_admin_faces'))
        db.session.add(user_to_create)
        db.session.commit()

        flash(f"Successfully added {user_to_create.username} as {user_to_create.roles[0].name} to the system",
              category='success')
        return redirect(url_for('home'))

    elif form.errors != {}:  # dictionary
        for err_msg in form.errors.values():
            flash(err_msg, category='danger')

    return render_template('register_employee.html', form=form)
"""
@app.route('/home/register_admin',methods=["GET","POST"])
@reset_session
@roles_required('admin')
@add_url
def register_admin():

    form = RegisterForm()
    if form.validate_on_submit():

        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=user_manager.hash_password(form.password1.data),
            national_number=function_filter_hash(form.national_number.data),
             )

        user_to_create.roles.append(Role.query.filter_by(name='admin').first())
        session['user_to_create'] = user_to_create

        return redirect(url_for('register_admin_faces'))

    elif form.errors != {}:  # dictionary
        for err_msg in form.errors.values():
            flash(err_msg, category='danger')

    return render_template('register.html', form=form)
    """
@app.route('/home/register_admin_faces')
@roles_required('admin')
@check_register_admin
def register_admin_faces():
    return render_template('register_faces.html')


@app.route('/home/QR_code_request', methods=["GET","POST"])
@reset_session
@login_required
@add_url
def QR_code_self_request():
    form = QR_code_self_Form()
    if form.validate_on_submit():

        if user_manager.verify_password(form.password.data, current_user.password):

            # code om  qr code te maken
            # variabelen: naam, varvaldatum (, wachtwoord)
            # opslaan in de map static_test
            code = os.urandom(10).hex()
           
            img = create_specific_qr_combination(current_user.national_number,code)

            qr = QR(code=code)
            qr.user.append(current_user)
            db.session.add(qr)
            db.session.commit()
            file_object = io.BytesIO()
            img.save(file_object,format='PNG')
            file_object.seek(0,0)
            print(file_object.getvalue())
            flash(f"Credential match", category='success')
            base = base64.b64encode(file_object.getvalue())
            base = base.decode("utf-8")

            return render_template('show_QR_code.html',image_data=base)
            #return redirect(url_for('QR_code_self',username=current_user.username))
            #return redirect('/home/QR_code_self_request/'+current_user.username)
        else:
            flash("Username or password incorrect, please try again", category='danger')

    elif form.errors != {}:  # dictionary
        for err_msg in form.errors.values():
            flash(err_msg, category='danger')

    return render_template('QR_code_request.html',form=form)

@app.route('/home/QR_code_leave')
@reset_session
@login_required
@add_url
def QR_code_leave():

    base = current_user.qr_leave

    return render_template('show_QR_code.html',image_data=base)

"""
ROUTES FOR CONTENT

"""

@app.route("/home/employee_list")
@roles_required(['admin','security'])
@reset_session
@add_url
def employee_list():
    send_dict = {}
    roles = [item[0] for item in Role.query.with_entities(Role.name).all()]
    print(roles)
    for name in roles:
        items = User.query.filter(User.roles.any(name=name)).order_by(User.username).all()
        send_dict[name] = items
    print(send_dict)
    return render_template('employee_list.html',items=send_dict)

@app.route("/home/employee_list/<national_number>")
@login_required
@reset_session
@add_url
def logs_employee(national_number):
    logs = Log.query.filter(Log.user.any(national_number=national_number)).order_by(Log.date_entry.desc()).all()
    user = User.query.filter_by(national_number=national_number).first()
    send_dict={
        'user': user,
        'logs': logs}
    #send_graph_logs(national_number)
    return render_template('logs_employee.html',items = send_dict)


@app.route("/home/change_role", methods=["GET", "POST"])
@roles_required('admin')
@reset_session
@add_url
def change_role():
    form = ChangeRoleForm()
    if form.validate_on_submit():

        if user_manager.verify_password(form.password.data, current_user.password):
            email_address = form.user_change_email_address.data
            role_name = form.user_change_role.data
           
            user = User.query.filter_by(email_address=email_address).first()
            role = Role.query.filter_by(name=role_name).first()
            user.roles = [role]
            db.session.commit()
            assert role_name == user.roles[0].name
            assert len(user.roles) == 1
            if role_name == 'admin':
                session['user_to_create'] = user
                return redirect(url_for('register_admin_faces'))
            else:
                flash(f"The role of {user.username} was successfully changed to {user.roles[0].name}",category='success')
                return redirect(url_for('home'))
            # return redirect(url_for('QR_code_self',username=current_user.username))
            # return redirect('/home/QR_code_self_request/'+current_user.username)
        else:
            flash("Email or password incorrect, please try again", category='danger')

    elif form.errors != {}:  # dictionary
        for err_msg in form.errors.values():
            flash(err_msg, category='danger')

    return render_template('change_role.html', form=form)


@app.route("/home/visitor_qr", methods=["GET", "POST"])
@roles_required(['admin','recruiter','security'])
@reset_session
@add_url
def make_visitor_QR():
    
    form = QR_make_visitor()
    if form.validate_on_submit():

        if user_manager.verify_password(form.password.data, current_user.password):

            # code om  qr code te maken
            # variabelen: naam, varvaldatum (, wachtwoord)
            # opslaan in de map static_test
            code = os.urandom(10).hex()
           
            img = create_specific_qr_combination(form.company.data,code)

            qr = QR_VISITOR(code=code, company= form.company.data)
            db.session.add(qr)
            db.session.commit()
            file_object = io.BytesIO()
            img.save(file_object,format='PNG')
            file_object.seek(0,0)
            print(file_object.getvalue())
            flash(f"Credential match", category='success')
            base = base64.b64encode(file_object.getvalue())
            base = base.decode("utf-8")

            return render_template('show_QR_code.html',image_data=base)
            #return redirect(url_for('QR_code_self',username=current_user.username))
            #return redirect('/home/QR_code_self_request/'+current_user.username)
        else:
            flash("Username or password incorrect, please try again", category='danger')

    elif form.errors != {}:  # dictionary
        for err_msg in form.errors.values():
            flash(err_msg, category='danger')

    return render_template('QR_code_visitor.html',form=form)
@app.route("/home/present_employees", methods=["GET", "POST"])
@login_required
@reset_session
@add_url
def present_employees():
    
    users = [log.user for log in Log.query.filter_by(date_exit=None).all()]
    
    print(users)
    
    return render_template('present_employees.html',users = users)
