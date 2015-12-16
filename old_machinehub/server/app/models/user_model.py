from datetime import datetime
from old_machinehub.server.app import db, login_manager


class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(50), unique=True, index=True)
    password = db.Column('password', db.String(50))
    email = db.Column('email', db.String(50), unique=True, index=True)
    show_email = db.Column('show_email', db.Boolean)
    description = db.Column('description', db.String)
    name = db.Column('name', db.String(50))
    registered_on = db.Column('registered_on', db.DateTime)
    machines = db.relationship('MachineModel', backref='user', lazy='dynamic')
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def __init__(self, username, password, email, confirmed, confirmed_on=None):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()
        self.description = ""
        self.name = ""
        self.show_email = False
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on

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
        return self.id

    def __repr__(self):
        return '<UserModel %r>' % (self.username)


@login_manager.user_loader
def load_user(id):
    return UserModel.query.get(int(id))


def get_users_for_page(page, per_page):
    all_users = UserModel.query.order_by(UserModel.username).all()
    origin = per_page * (page - 1)
    end = origin + per_page
    users = all_users[origin:end] if len(all_users) > origin + per_page \
        else all_users[origin:]
    info = []
    for user in users:
        info.append((user.username, user.description))
    return info, len(all_users)
