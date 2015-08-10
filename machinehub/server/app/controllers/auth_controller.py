from flask_classy import FlaskView, route
from flask.templating import render_template
from flask.globals import request
from flask.helpers import flash, url_for
from werkzeug.utils import redirect
from flask_login import login_user, logout_user, login_required


class AuthController(FlaskView):
    decorators = []
    route_prefix = '/'
    route_base = '/'

    def __init__(self):
        from machinehub.server.app.models.user_model import User
        from machinehub.server.app.webapp import db
        self._db = db
        self._user = User

    @route('/register', methods=['GET', 'POST'])
    def register_user(self):
        if request.method == 'GET':
            return render_template('register.html')
        user = self._user(request.form['username'], request.form['password'], request.form['email'])
        self._db.session.add(user)
        self._db.session.commit()
        flash('User successfully registered')
        return redirect(url_for('AuthController:login'))

    @route('/login', methods=['GET', 'POST'])
    def login(self):
        if request.method == 'GET':
            return render_template('login.html')
        username = request.form['username']
        password = request.form['password']
        registered_user = self._user.query.filter_by(username=username, password=password).first()
        if registered_user is None:
            flash('Username or Password is invalid', 'error')
            return redirect(url_for('AuthController:login'))
        login_user(registered_user)
        flash('Logged in successfully')
        return redirect(request.args.get('next') or url_for('MachinehubController:index'))

    @route("/logout")
    @login_required
    def logout(self):
        logout_user()
        return redirect(url_for('MachinehubController:index'))
