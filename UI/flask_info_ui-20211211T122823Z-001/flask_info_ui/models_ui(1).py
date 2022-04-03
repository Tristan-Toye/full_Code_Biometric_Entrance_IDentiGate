from flask_info_ui import db
#from flask_user import UserMixin


class User(db.Model): # additional class attributes (ctrl +b to inspect)
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30),nullable=False, unique=True)
    faces = db.Column(db.PickleType())
    veins = db.Column(db.PickleType())



    def __repr__(self):  # to change view in database
        return f'Item {self.username}'

"""
    @property
    def faces(self):
        return [[float(x) for x in pic_matrix.split(';') if x != '']
                for pic_matrix in self._user_matrix.split('/') if pic_matrix != '']

    @faces.setter
    def faces(self,values):
        one_pic = False

        for pic_matrix in values:

            if isinstance(pic_matrix,list):

                for x in pic_matrix:
                    self._user_matrix += f'{str(x)};'

                self._user_matrix += f'/'
            elif isinstance(pic_matrix,(int,float)):
                one_pic = True
                self._user_matrix += f'{str(pic_matrix)};'
        if one_pic:
            self._user_matrix += f'/'

"""