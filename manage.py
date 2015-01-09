#!/usr/bin/env python

from flask.ext.script import Manager, Server

import impschedules

def run():
    impschedules.db.create_all()
    manager = Manager(impschedules.app)
    server = Server(host='0.0.0.0')
    manager.add_command("runserver", server)
    manager.run()

if __name__ == "__main__":
    run()
