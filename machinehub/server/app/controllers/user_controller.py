from flask_classy import route, FlaskView
from flask.templating import render_template
from flask_login import current_user
from flask_sqlalchemy import Pagination
from flask.helpers import url_for
from machinehub.server.app.models.machine_model import MachineModel


class UserController(FlaskView):
    decorators = []
    route_prefix = '/'
    route_base = '/'

    @route('/<username>', methods=['GET'])
    def user(self, username):
        from machinehub.server.app.models.user_model import User
        if username not in [m.username for m in User.query.all()]:
            return render_template('404.html'), 404
        try:
            authoraize_user = current_user.username == username
        except AttributeError:
            authoraize_user = False
        from machinehub.server.app.models.user_model import User
        from machinehub.server.app.models.user_model import UserMachine
        links = []
        user_id = User.query.filter_by(username=username).first().id
        machines = [m.machinename for m in UserMachine.query.filter_by(user_id=user_id).all()]
        for name, doc in MachineModel().machines(machines):
            url = url_for('MachineController:machine', machine_name=name)
            links.append((url, name, doc.title or "", doc.description or ""))

        return render_template('user/profile.html',
                               user=username,
                               authoraize_user=authoraize_user,
                               links=links)
