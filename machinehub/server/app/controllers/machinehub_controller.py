from flask.helpers import url_for, send_from_directory, flash
from flask_classy import route, FlaskView
from flask.templating import render_template
from machinehub.server.app.models.machine_model import MachineModel
from werkzeug.exceptions import abort
from machinehub.server.app.models.explorer_model import Pagination
from werkzeug.utils import redirect
from flask.globals import request
from machinehub.server.app.models.resources_model import upload_machines
from machinehub.config import UPLOAD_FOLDER
from flask_login import login_required, current_user


PER_PAGE = 20


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


class MachinehubController(FlaskView):
    decorators = []
    route_prefix = '/'
    route_base = '/'

    def __init__(self):
        self.machines_model = MachineModel()

    @route('/machines/<int:page>')
    def machines(self, page):
        links = []
        count = self.machines_model.count
        machines = self.machines_model.get_machines_for_page(page, PER_PAGE, count)
        for name, doc in machines:
            url = url_for('MachineController:machine', machine_name=name)
            links.append((url, name, doc.title or "", doc.description or ""))
        if not machines and page != 1:
            abort(404)
        pagination = Pagination(page, PER_PAGE, count)
        return render_template('explorer.html',
                               pagination=pagination,
                               links=links
                               )

    @route('/')
    def index(self):
        machines_info = []
        machines = self.machines_model.get_last_machines()
        for name, doc in machines:
            url = url_for('MachineController:machine', machine_name=name)
            image = doc.images[0] if doc.images else None
            machines_info.append((image, doc.title or "", doc.description or "", url))

        def chunks(l, n):
            """Yield successive n-sized chunks from l."""
            for i in xrange(0, len(l), n):
                yield l[i:i+n]
        splited_machines_info = list(chunks(machines_info, 4))
        return render_template('home.html',
                               splited_machines_info=splited_machines_info)

    @route('/download/<path:filename>')
    def download(self, filename):
        return send_from_directory(UPLOAD_FOLDER, filename)

    @route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload(self):
        if request.method == 'POST':
            uploaded_files = request.files.getlist("file[]")
            names = upload_machines(uploaded_files, self.machines_model)
            if names:
                machines_to_ignore = self._user_authorized(names)
                for name in names:
                    from machinehub.server.app.models.user_model import UserMachine
                    from machinehub.server.app.webapp import db
                    if name not in machines_to_ignore:
                        machine = UserMachine(name)
                        machine.user = current_user
                        db.session.add(machine)
                db.session.commit()
                if len(names) == 1:
                    return redirect(url_for('MachineController:machine', machine_name=names[0]))
                else:
                    return redirect(url_for('MachinehubController:index'))
            elif names is None:
                flash('WARNING! Machine not found.', 'warning')
        return render_template('machine/upload.html')

    def _user_authorized(self, names):
        if current_user.is_authenticated():
            all_machines = [m.machinename for m in current_user.machines.all()]
            owner_machines = []
            for name in [name for name in names if name in all_machines]:
                if name not in name in [m.machinename for m in current_user.machines.all()]:
                    return False
                else:
                    owner_machines.append(name)
            return owner_machines
        return None
