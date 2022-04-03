from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, NumberRange
from flask_info.models import User, Role, QR_VISITOR
from flask_info.functions import function_filter_hash
import re

class ChangeRoleForm(FlaskForm):
    def validate_user_change_email_address(self, user_change_email_address_to_validate):
        
        user = User.query.filter_by(email_address=user_change_email_address_to_validate.data).first()
        if not user:
            raise ValidationError('User is not defined in database')
    def validate_user_change_role(self,user_change_role_to_validate):
        role = Role.query.filter_by(name=user_change_role_to_validate.data).first()
        print(user_change_national_number_to_validate)
        user = User.query.filter_by(email_address=self.user_change_email_address.data).first()
        print(user)
        if not role:
            raise ValidationError('Role is not defined in database')
        if user:
            print(user.roles[0].name)
            print(role.name)
            if user.roles[0].name == role.name:
                print('validation error')
                raise ValidationError('This action seems to have no effect')
        else:
            raise ValidationError(f'User does not exist')
    user_change_email_address = StringField(label='Email address',validators=[DataRequired(),Email()])
    user_change_role = StringField(label='Role',validators=[DataRequired()])
    password = PasswordField(label='Confirm your Password', validators=[DataRequired()])
    submit = SubmitField(label='Validate')

class GoogleAuthenticatorForm(FlaskForm):
    time_based_pincode = StringField(label="Google authenticater pin:",validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class RegisterForm(FlaskForm):

    def validate_national_number(self,national_number_to_validate):

        print("function validate_rijksregister")
        if len(national_number_to_validate.data) != 15:
            raise ValidationError('Seems nationalnumber is not of the correct length')
        list_dots = list(map(national_number_to_validate.data.__getitem__,[2,5,12]))

        if any(elem != '.' for elem in list_dots) or national_number_to_validate.data[8] != '-':
            raise ValidationError('Seems nationalnumber is not of the correct syntax')
        print(re.split('\.|-',national_number_to_validate.data))
        if not all(number.isdecimal() for number in re.split('\.|-',national_number_to_validate.data)):
            raise ValidationError('Seems the input does not consist of numbers in the syntax')
        national_number_to_validate = function_filter_hash(national_number_to_validate.data)
        national_number = User.query.filter_by(national_number=national_number_to_validate).first()
        print(national_number)
        if national_number:
            raise ValidationError('National number already in database. Do you already have an account?')
        

    def validate_email_address(self, email_address_to_validate):
        print("function validate_email_address")
        email = User.query.filter_by(email_address=email_address_to_validate.data).first()
        if email:
            raise ValidationError('Email address already exists! Please try a different email address')

    username = StringField(label='Username', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email address', validators=[Email(), DataRequired()])
    national_number = StringField(label='National number',validators=[DataRequired()])
    password1 = PasswordField(label='Password', validators=[Length(min=6, max=60), DataRequired()])
    password2 = PasswordField(label='Confirm password', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create account')


class RegisterFormEmployee(FlaskForm):
    def validate_role(self,role_to_validate):
        role = Role.query.filter_by(name=role_to_validate.data).first()
        if not role:
            raise ValidationError('Role is not defined in database')

    def validate_national_number(self, national_number_to_validate):

        print("function validate_rijksregister")
        if len(national_number_to_validate.data) != 15:
            raise ValidationError('Seems nationalnumber is not of the correct length')
        list_dots = list(map(national_number_to_validate.data.__getitem__, [2, 5, 12]))

        if any(elem != '.' for elem in list_dots) or national_number_to_validate.data[8] != '-':
            raise ValidationError('Seems nationalnumber is not of the correct syntax')
        print(re.split('\.|-', national_number_to_validate.data))
        if not all(number.isdecimal() for number in re.split('\.|-', national_number_to_validate.data)):
            raise ValidationError('Seems the input does not consist of numbers in the syntax')
        national_number_to_validate = function_filter_hash(national_number_to_validate.data)
        national_number = User.query.filter_by(national_number=national_number_to_validate).first()
        print(national_number)
        if national_number:
            raise ValidationError('National number already in database. Do you already have an account?')

    def validate_email_address(self, email_address_to_validate):
        print("function validate_email_address")
        email = User.query.filter_by(email_address=email_address_to_validate.data).first()
        if email:
            raise ValidationError('Email address already exists! Please try a different email address')

    username = StringField(label='Username', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email address', validators=[Email(), DataRequired()])
    national_number = StringField(label='National number', validators=[DataRequired()])
    role = StringField(label='Role', validators=[DataRequired()])
    password1 = PasswordField(label='Password', validators=[Length(min=6, max=60), DataRequired()])
    password2 = PasswordField(label='Confirm password', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create account')
    
class LoginForm(FlaskForm):
    email_address = StringField(label='Email', validators=[Email(),DataRequired()])
    password = PasswordField(label='Confirm Password', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class QR_code_self_Form(FlaskForm):
    password = PasswordField(label='Confirm Password', validators=[DataRequired()])
    submit = SubmitField(label='Request QR code')
class QR_make_visitor(FlaskForm):
    
    password =  PasswordField(label='Confirm Password', validators=[DataRequired()])
    company = StringField(label='Company', validators=[DataRequired()])
    submit = SubmitField(label='Request QR code')
