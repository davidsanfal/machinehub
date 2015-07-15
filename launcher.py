#!/usr/bin/env python


from machinehub.config import machinehub_conf
from machinehub.server.app import app


def main():
    app.run(host=machinehub_conf.server.host,
            port=int(machinehub_conf.server.port),
            debug=True)


if __name__ == '__main__':
    main()
