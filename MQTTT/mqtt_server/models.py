
from flask_user import UserMixin
import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from mqtt_server.constants import base_db

# db.session.add(class)
# db.session.commit()
# db.session.rollback()
class User(base_db, UserMixin): # additional class attributes (ctrl +b to inspect)
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    username = Column(String(),nullable=False)
    national_number = Column(String(), nullable=False,unique=True)
    email_address = Column(String(),nullable=False, unique=True)
    password = Column(String(),nullable=False)
    roles = relationship('Role',secondary='user_roles')
    qr_leave = Column(String(),nullable=False,unique=True)
    qr_leave_code = Column(String(), nullable=False, unique=True)

    def __repr__(self):  # to change view in database
        return f'Item {self.username}'


class QR(base_db):
    __tablename__ = 'qr_codes'
    id = Column(Integer(), primary_key=True)
    timestamp = Column(DateTime(), nullable=False, unique=False, default= datetime.datetime.now())
    code = Column(String(), nullable=False, unique=True)
    user = relationship('User', secondary='user_qr')

    def __repr__(self):
        return f"QR code from {self.user[0].username} at {self.timestamp}"

class Role(base_db):
    __tablename__ = 'roles'
    #Role.users is users classes with this role
    id = Column(Integer(), primary_key=True)
    name=Column(String(),unique=True,nullable=False)

    def __repr__(self): # to change view in database
        return f'Item {self.name}'

class Log(base_db):
    __tablename__ = 'logs'
    # iterate objects
    # Item.query.all()
    # Item.query.filter_by(entry = '16u')
    #log1.userid = User.query.filter_by(username = "username").first().userid
    # Log.user is user class
    id = Column(Integer(), primary_key=True)
    user = relationship('User',secondary='user_logs')
    date_entry = Column(DateTime(),nullable=False,unique=False,default= datetime.datetime.now())
    date_exit =Column(DateTime(),nullable=True, unique=False,default=None)


    def __repr__(self): # to change view in database
        return f'Log {self.date_entry} of {self.user[0].username}'


class UserQR(base_db):
    __tablename__ = 'user_qr'
    id = Column(Integer(), primary_key=True)
    user_id =Column(Integer(), ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
    qr_id = Column(Integer(), ForeignKey('qr_codes.id', onupdate='CASCADE', ondelete='CASCADE'))

class UserRoles(base_db):
    __tablename__='user_roles'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.id',onupdate='CASCADE', ondelete='CASCADE'))
    role_id = Column(Integer(), ForeignKey('roles.id',onupdate='CASCADE', ondelete='CASCADE'))

class UserLogs(base_db):
    __tablename__='user_logs'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.id',onupdate='CASCADE', ondelete='CASCADE'))
    log_id = Column(Integer(), ForeignKey('logs.id', onupdate='CASCADE',ondelete='CASCADE'))
    # CASCADE: ook verwijderen in gelinkte databases

class QR_VISITOR(base_db):
    __tablename__='qr_visitor'
    id = Column(Integer(), primary_key=True)
    timestamp = Column(DateTime(), nullable=False, unique=False, default= datetime.datetime.now())
    code = Column(String(), nullable=False, unique=True)



