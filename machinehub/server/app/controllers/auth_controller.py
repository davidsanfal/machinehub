from flask_classy import FlaskView, route
from flask.templating import render_template
from flask.globals import request
from flask.helpers import flash, url_for
from werkzeug.utils import redirect
from flask_login import login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from machinehub.server.app.models.user_model import User
from machinehub.server.app import db


class AuthController(FlaskView):
    decorators = []
    route_prefix = '/'
    route_base = '/'

    @route('/register', methods=['GET', 'POST'])
    def register_user(self):
        if request.method == 'GET':
            return render_template('auth/register.html')
        else:
            try:
                username = request.form['username']
                password = request.form['password']
                email = request.form['email']
                user = User(username, password, email)
                db.session.add(user)
                db.session.commit()
                flash('User successfully registered', category='success')
                registered_user = User.query.filter_by(username=username, password=password).first()
                login_user(registered_user)
                return redirect(request.args.get('next') or url_for('UserController:user', username=username))
            except IntegrityError:
                flash('Email or User already exists!', category='danger')
                return render_template('auth/register.html')

    @route('/login', methods=['GET', 'POST'])
    def login(self):
        if request.method == 'GET':
            return render_template('auth/login.html')
        username = request.form['username']
        password = request.form['password']
        registered_user = User.query.filter_by(username=username, password=password).first()
        if registered_user is None:
            flash('Username or Password is invalid', category='danger')
            return redirect(url_for('AuthController:login'))
        login_user(registered_user)
        flash('Logged in successfully', category='success')
        return redirect(request.args.get('next') or url_for('UserController:user', username=username))

    @route("/logout")
    @login_required
    def logout(self):
        logout_user()
        return redirect(url_for('MachinehubController:index'))
