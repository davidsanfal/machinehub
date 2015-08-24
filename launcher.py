#!/usr/bin/env python


from machinehub.config import machinehub_conf
from machinehub.server.app.webapp import app
from machinehub.server.app import db


def main():
    db.create_all()
    app.run(host=machinehub_conf.server.host,
            port=int(machinehub_conf.server.port),
            debug=False)


if __name__ == '__main__':
    main()
