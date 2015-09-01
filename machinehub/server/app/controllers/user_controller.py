from flask_classy import route, FlaskView
from flask.templating import render_template
from flask_login import current_user, login_required
from flask.helpers import url_for
from machinehub.server.app.models.machine_model import MachineManager,\
    MachineModel
from machinehub.server.app.models.user_model import UserModel
from machinehub.server.app import db
from flask.globals import request
from werkzeug.utils import redirect
from machinehub.server.app.utils.decorators import check_confirmed


class UserController(FlaskView):
    decorators = []
    route_prefix = '/'
    route_base = '/'

    @route('/<username>', methods=['GET'])
    def user(self, username):
        if username not in [m.username for m in UserModel.query.all()]:
            return render_template('404.html'), 404
        try:
            authoraize_user = current_user.username == username and current_user.confirmed
        except AttributeError:
            authoraize_user = False
        links = []
        user = UserModel.query.filter_by(username=username).first()
        user_id = user.id
        machines = [m.machinename for m in MachineModel.query.filter_by(user_id=user_id).all()]
        for name, doc in MachineManager().machines(machines):
            url = url_for('MachineController:machine', machine_name=name)
            links.append((url, name, doc.title or "", doc.description or ""))

        return render_template('user/profile.html',
                               user=username,
                               name=user.name,
                               description=user.description.split('\n'),
                               show_email=user.show_email,
                               email=user.email,
                               authoraize_user=authoraize_user,
                               links=links)

    @route('/<username>/settings', methods=['GET'])
    @login_required
    @check_confirmed
    def settings(self, username):
        if current_user.username == username:
            user = UserModel.query.filter_by(username=username).first()
            return render_template('user/settings.html',
                                   user=username,
                                   name=user.name,
                                   description=user.description,
                                   show_email=user.show_email)
        return render_template('403.html'), 403

    @route('/<username>/settings', methods=['POST'])
    @login_required
    @check_confirmed
    def update_settings(self, username):
        if current_user.username == username:
            user = UserModel.query.filter_by(username=username).first()
            user.name = request.form['name']
            user.description = request.form['description']
            user.show_email = True if request.form.get('show_email') else False
#             db.session.update(user)
            db.session.commit()
            return redirect(url_for('UserController:user', username=username))
        return render_template('403.html'), 403
