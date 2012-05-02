import collective.hostout.fabfile

from collective.hostout import read_config

read_config("parts/hostout/hostout.cfg")

from fabric.api import task, run

@task
def mytask():
  pass
