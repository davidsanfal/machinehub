from flask.helpers import url_for, send_from_directory
from flask_classy import route, FlaskView
from flask.templating import render_template
from machinehub.server.app.models.machine_model import MachineManager
from werkzeug.exceptions import abort
from machinehub.server.app.models.explorer_model import Pagination
from machinehub.config import UPLOAD_FOLDER
from machinehub.common.model.machine_name import MachineName
from machinehub.server.app.models.user_model import get_users_for_page


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
        self.machines_manager = MachineManager()

    @route('/machines/<int:page>')
    def machines(self, page):
        links = []
        machines, count = self.machines_manager.get_machines_for_page(page, PER_PAGE)
        for name, doc in machines:
            url = url_for('MachineController:machine', machine_name=name)
            desc = doc.description if len(doc.description) <= 280 else doc.description[:277] + '...'
            links.append((url, name, doc.title or "", desc or ""))
        if not machines and page != 1:
            abort(404)
        pagination = Pagination(page, PER_PAGE, count)
        return render_template('explorer.html',
                               pagination=pagination,
                               links=links
                               )

    @route('/users/<int:page>')
    def users(self, page):
        links = []
        users, count = get_users_for_page(page, PER_PAGE)
        for name, desc in users:
            url = url_for('UserController:user', username=name)
            desc = desc if len(desc) <= 280 else desc[:277] + '...'
            links.append((url, name, None, desc))
        if not users and page != 1:
            abort(404)
        pagination = Pagination(page, PER_PAGE, count)
        return render_template('explorer.html',
                               pagination=pagination,
                               links=links
                               )

    @route('/')
    def index(self):
        machines_info = []
        machines = self.machines_manager.get_last_machines()
        for name, doc in machines:
            machine_name = MachineName(name)
            machine_url = url_for('MachineController:machine', machine_name=name)
            user_url = url_for('UserController:user', username=machine_name.user)
            image = doc.images[0] if doc.images else None
            machines_info.append((image,
                                  doc.title or "",
                                  doc.description or "",
                                  machine_name.user, user_url,
                                  machine_name.name, machine_url))

        def chunks(l, n):
            """Yield successive n-sized chunks from l."""
            for i in iter(range(0, len(l), n)):
                yield l[i:i+n]
        splited_machines_info = list(chunks(machines_info, 4))
        return render_template('home.html',
                               splited_machines_info=splited_machines_info)

    @route('/download/<path:filename>')
    def download(self, filename):
        return send_from_directory(UPLOAD_FOLDER, filename)
