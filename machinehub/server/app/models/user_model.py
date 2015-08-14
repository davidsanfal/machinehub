from datetime import datetime
from flask_login import current_user
from machinehub.server.app import db, login_manager


class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True, index=True)
    password = db.Column('password', db.String(10))
    email = db.Column('email', db.String(50),unique=True, index=True)
    registered_on = db.Column('registered_on', db.DateTime)
    machines = db.relationship('MachineModel', backref='user', lazy='dynamic')

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()

    @property
    def machine_names(self):
        return [m.machinename for m in self.machines.all()]

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<UserModel %r>' % (self.username)


@login_manager.user_loader
def load_user(id):
    return UserModel.query.get(int(id))
