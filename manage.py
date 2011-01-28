#!/usr/bin/env python
from flaskext.script import Manager
from feedback import app, db


manager = Manager(app)


@manager.command
def initdb():
    """Creates all database tables"""
    print 'Database: %s' % db.engine.url
    db.create_all()
    print 'All tables created'


@manager.command
def dropdb():
    """Drops all database tables"""
    print 'Database: %s' % db.engine.url
    db.drop_all()
    print 'All tables dropped'


if __name__ == '__main__':
    manager.run()
