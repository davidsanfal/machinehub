from datetime import datetime
from machinehub.server.app.webapp import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True, index=True)
    password = db.Column('password', db.String(10))
    email = db.Column('email', db.String(50),unique=True, index=True)
    registered_on = db.Column('registered_on', db.DateTime)
    machines = db.relationship('UserMachine', backref='user', lazy='dynamic')

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


class UserMachine(db.Model):
    __tablename__ = 'machines'
    id = db.Column('machines_id', db.Integer, primary_key=True)
    machinename = db.Column('machinename', db.String(100), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __init__(self, machinename):
        self.machinename = machinename
