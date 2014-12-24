# -*-  coding: utf-8 -*-
from __future__ import with_statement
from fabric.api import *
from fabric.contrib.project import rsync_project

HOST = '148.251.192.21'
PORT = "22"
EXCLUDE = "*.log *.map examples *.coffee *.db *.pyc *~ .idea .git *.png".split(' ')

env.hosts = [HOST]
env.port = PORT


WORK_DIR = '/home/evren/'



def sync():
    rsync_project(WORK_DIR, exclude=EXCLUDE)

def uwsgi():
    sync()
    with cd(WORK_DIR + "pyexp"):
        run("uwsgi --stop /tmp/uwsgimaster.pid", warn_only=True)
        run("uwsgi uwsgi.ini")


# def deploy(migrate=False):
#     local("git push")
#     with cd(deploy_dir):
#         run("git fetch --all")
#         run("git reset --hard origin/master")
#         if migrate:
#             remote_migrate()
#         restart_sites()

