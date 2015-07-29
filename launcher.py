#!/usr/bin/env python


from machinehub.config import machinehub_conf
from machinehub.server.app.webapp import app


def main():
    app.run(host=machinehub_conf.server.host,
            port=int(machinehub_conf.server.port),
            debug=None)


if __name__ == '__main__':
    main()
