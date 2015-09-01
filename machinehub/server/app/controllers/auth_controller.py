from flask_classy import FlaskView, route
from flask.templating import render_template
from flask.globals import request
from flask.helpers import flash, url_for
from werkzeug.utils import redirect
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from machinehub.server.app.models.user_model import UserModel
from machinehub.server.app import db
from machinehub.server.app.services.email_service import generate_confirmation_token,\
    confirm_token, send_email
import datetime
from machinehub.common.model.user_name import UserName
from machinehub.common.errors import InvalidNameException


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
                username = UserName(username)
                user = UserModel(username,
                                 password,
                                 email,
                                 confirmed=False)
                db.session.add(user)
                db.session.commit()

                token = generate_confirmation_token(user.email)
                confirm_url = url_for('AuthController:confirm_email', token=token, _external=True)
                html = render_template('user/activate_email.html', confirm_url=confirm_url)
                subject = "Please confirm your email"
                send_email(user.email, subject, html)

                login_user(user)

                flash('A confirmation email has been sent via email.', category='success')
                return redirect(url_for('AuthController:unconfirmed'))
            except IntegrityError:
                flash('Email or UserModel already exists!', category='danger')
                return render_template('auth/register.html')

            except InvalidNameException as e:
                flash(e.message, category='danger')
                return render_template('auth/register.html')

    @route('/login', methods=['GET', 'POST'])
    def login(self):
        if request.method == 'GET':
            return render_template('auth/login.html')
        username = request.form['username']
        password = request.form['password']
        registered_user = UserModel.query.filter_by(username=username, password=password).first()
        if registered_user is None:
            flash('Username or Password is invalid', category='danger')
            return redirect(url_for('AuthController:login'))
        login_user(registered_user)
#         if current_user.confirmed is False:
#             flash('Please confirm your account!', 'warning')
#             return redirect(url_for('AuthController:unconfirmed'))
        flash('Logged in successfully', category='success')
        return redirect(request.args.get('next') or url_for('UserController:user',
                                                            username=username))

    @route("/logout")
    @login_required
    def logout(self):
        logout_user()
        return redirect(url_for('MachinehubController:index'))

    @route('/confirm/<token>')
    @login_required
    def confirm_email(self, token):
        try:
            email = confirm_token(token)
        except:
            flash('The confirmation link is invalid or has expired.', 'danger')
        user = UserModel.query.filter_by(email=email).first_or_404()
        if user.confirmed:
            flash('Account already confirmed. Please login.', 'success')
        else:
            user.confirmed = True
            user.confirmed_on = datetime.datetime.now()
            db.session.add(user)
            db.session.commit()
            flash('You have confirmed your account. Thanks!', 'success')
        return redirect(url_for('MachinehubController:index'))

    @route('/unconfirmed')
    @login_required
    def unconfirmed(self):
        if current_user.confirmed:
            return redirect('MachinehubController:index')
        return render_template('user/unconfirmed.html')
