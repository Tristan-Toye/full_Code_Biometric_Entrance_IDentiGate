from flask_info import db
from flask_user import UserMixin, UserManager
from flask import flash, redirect, url_for
import datetime


class CustomUserManager(UserManager):
    def unauthorized_view(self):
        flash("You are not authorized to view this page",category='danger')
        return redirect(url_for('home'))

    def unauthenticated_view(self):
        flash("You need to login to view this page",category='info')
        return redirect(url_for('login'))



# db.session.add(class)
# db.session.commit()
# db.session.rollback()
class UserQR(db.Model):
    __tablename__ ='user_qr'
    id = db.Column(db.Integer(),primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id',onupdate='CASCADE', ondelete='CASCADE'))
    qr_id = db.Column(db.Integer(), db.ForeignKey('qr_codes.id',onupdate='CASCADE', ondelete='CASCADE'))

class UserRoles(db.Model):
    __tablename__='user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id',onupdate='CASCADE', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id',onupdate='CASCADE', ondelete='CASCADE'))

class UserLogs(db.Model):
    __tablename__='user_logs'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id',onupdate='CASCADE', ondelete='CASCADE'))
    log_id = db.Column(db.Integer(), db.ForeignKey('logs.id', onupdate='CASCADE',ondelete='CASCADE'))
    # CASCADE: ook verwijderen in gelinkte databases

class User(db.Model, UserMixin): # additional class attributes (ctrl +b to inspect)
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(),nullable=False)
    national_number = db.Column(db.String(), nullable=False,unique=True)
    email_address = db.Column(db.String(),nullable=False, unique=True)
    password = db.Column(db.String(),nullable=False)
    faces = db.Column(db.PickleType())
    roles = db.relationship('Role',secondary='user_roles')
    qr_leave = db.Column(db.String(),nullable=False, unique=True)
    qr_leave_code = db.Column(db.String(), nullable=False, unique=True)


    def __repr__(self):  # to change view in database
        return f'Item {self.username}'

class Role(db.Model):
    __tablename__ = 'roles'
    #Role.users is users classes with this role
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(),unique=True,nullable=False)

    def __repr__(self): # to change view in database
        return f'Item {self.name}'

class Log(db.Model):
    __tablename__ = 'logs'
    # iterate objects
    # Item.query.all()
    # Item.query.filter_by(entry = '16u')
    #log1.userid = User.query.filter_by(username = "username").first().userid
    # Log.user is user class
    id = db.Column(db.Integer(), primary_key=True)
    user = db.relationship('User',secondary='user_logs')
    date_entry = db.Column(db.DateTime(),nullable=False,unique=False,default= datetime.datetime.now())
    date_exit = db.Column(db.DateTime(),nullable=True, unique=False,default=None)


    def __repr__(self): # to change view in database
        return f'Log {self.date_entry} of {self.user[0].username}'

class QR(db.Model):
    __tablename__ ='qr_codes'
    id = db.Column(db.Integer(),primary_key=True)
    timestamp = db.Column(db.DateTime(),nullable=False,unique=False,default= datetime.datetime.now())
    code = db.Column(db.String(),nullable=False,unique=True)
    user = db.relationship('User', secondary='user_qr')

    def __repr__(self):
        return f"QR code from {self.user[0].username} at {self.timestamp}"


class QR_VISITOR(db.Model):
    __tablename__='qr_visitor'
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime(), nullable=False, unique=False, default= datetime.datetime.now())
    code = db.Column(db.String(), nullable=False, unique=True)
    company = db.Column(db.String(), nullable=False)




