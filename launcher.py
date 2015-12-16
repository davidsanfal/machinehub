#!/usr/bin/env python


from old_machinehub.config import machinehub_conf
from old_machinehub.server.app.webapp import app
from old_machinehub.server.app import db


def main():
    db.create_all()
    app.run(host=machinehub_conf.server.host,
            port=int(machinehub_conf.server.port),
            debug=True)


if __name__ == '__main__':
    main()
