import collective.hostout.fabfile as hostout

from collective.hostout import read_config

#read_config("parts/hostout/hostout.cfg")

read_config(dict(
    hostouts=dict(
        host={
            'host':'noc.pretaweb.com:23',
            'buildout-user':'djay'
        }
    )
))


from fabric.api import task, run

#@task
#def mytask():
#  pass
