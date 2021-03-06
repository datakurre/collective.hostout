
Overview
********

Hostout is a framework for managing remote buildouts via fabric scripts. It
includes many helpful builtin commands to package, deploy and bootstrap a
remote server with based on your local buildout.

Hostout uses fabric files. Fabric is an easy way to write python that
calls commands on a host over ssh.

Hostout is built around two ideas :-

1. Sharing Fabric command configuration amongst developers in a team
so where and how your applications is deployed becomes configuration, not
documentation. Deployment then becomes a single action by any member of the team.

2. Sharing fabric scripts via PyPi so we don't have to reinvent ways
to deploy or manage hosted applications


How?

Combining Fabric and buildout
*****************************

Here is a basic fabfile which will echo two variables on the remote server.


>>> write('fabfile.py',"""
...
... from fabric import api
... from fabric.api import run
...
... def echo(cmdline1):
...    option1 = api.env.option1
...    run("echo '%s %s'" % (option1, cmdline1) )
...
... """)

Using hostout we can predefine some of the fabric scripts parameters
as well as install the fabric runner. Each hostout part in your buildout.cfg
represents a connection to a server at a given path.

>>> write('buildout.cfg',
... """
... [buildout]
... parts = host1
...
... [host1]
... recipe = collective.hostout
... host = 127.0.0.1:10022
... fabfiles = fabfile.py
... option1 = buildout
... user = root
... password = root
... path = /var/host1
...
... """ )

If you don't include your password you will be prompted for it later.    

When we run buildout a special fabric runner will be installed called bin/hostout

>>> print system('bin/buildout -N')
Installing host1.
Generated script '/sample-buildout/bin/hostout'.


>>> print system('bin/hostout')
cmdline is: bin/hostout host1 [host2...] [all] cmd1 [cmd2...] [arg1 arg2...]
Valid hosts are: host1

We can run our fabfile by providing the

 - host which refers to the part name in buildout.cfg.
 
 - command which refers to the method name in the fabfile
 
 - any other options we want to pass to the command
 
Note: We can run multiple commands on one or more hosts using a single commandline.

In our example

>>> print system('bin/hostout host1 echo "is cool"')
Hostout: Running command 'echo' from 'fabfile.py'
Logging into the following hosts as root:
    127.0.0.1
[127.0.0.1] run: echo 'cd /var/host1 && buildout is cool'
[127.0.0.1] out: ...
Done.

Note that we combined information from our buildout with
commandline paramaters to determine the exact command sent
to our server.

Making a hostout plugin
***********************

It can be very helpful to package up our fabfiles for others to use.

Hostout Plugins are eggs with three parts :-

1. Fabric script

2. A zc.buildout recipe to initialise the parameters of the fabric file commands

3. Entry points for both the recipe and the fabric scripts

>>>    entry_points = {'zc.buildout': ['default = hostout.myplugin:Recipe',],
...                    'fabric': ['fabfile = hostout.myplugin.fabfile']
...                    },

Once packaged and released others can add your plugin to their hostout e.g.

>>> write('buildout.cfg',
... """
... [buildout]
... parts = host1
...
... [host1]
... recipe = collective.hostout
... extends = hostout.myplugin
... param1 = blah
... """ )

>>> print system('bin/buildout')

>>> print system('bin/hostout host1')
cmdline is: bin/hostout host1 [host2...] [all] cmd1 [cmd2...] [arg1 arg2...]
Valid commands are:
...
   mycommand        : example of command from hostout.myplugin


#TODO Example of echo plugin


Using fabric plugins
********************

You use commands others have made via the extends option.
Name a buildout recipe egg in the extends option and buildout will download
and merge any fabfiles and other configuration options from that recipe into
your current hostout configuration.  The following are examples of builtin
plugins.  Others are available on pypi.

see hostout.cloud_, hostout.supervisor_, hostout.ubuntu_ or
hostout.mrdeveloper for examples.

.. _hostout.cloud: http://pypi.python.org/pypi/hostout.cloud
.. _hostout.supervisor: http://pypi.python.org/pypi/hostout.supervisor
.. _hostout.ubuntu: http://pypi.python.org/pypi/hostout.ubuntu



Builtin Commands
****************

Hostout comes with a set of helpful commands. You can show this list by
not specifying any command at all. The list of commands will vary depending
on what fabfiles your hostout references.

>>> print system('bin/hostout host1')
cmdline is: bin/hostout host1 [host2...] [all] cmd1 [cmd2...] [arg1 arg2...]
Valid commands are:
   bootscript_list      : Lists the buildout bootscripts that are currently installed on the host
   bootstrap            : Install python and users needed to run buildout
   buildout             : Run the buildout on the remote server
   deploy               : predeploy, uploadeggs, uploadbuildout, buildout and then postdeploy
   install_bootscript   : Installs a system bootscript
   postdeploy           : Perform any final plugin tasks
   predeploy            : Install buildout and its dependencies if needed. Hookpoint for plugins
   setupusers           : create buildout and the effective user and allow hostout access
   setowners            : Ensure ownership and permissions are correct on buildout and cache
   run                  : Execute cmd on remote as login user
   sudo                 : Execute cmd on remote as root user
   uninstall_bootscript : Uninstalls a system bootscript
   uploadbuildout       : Upload buildout pinned to local picked versions + uploaded eggs
   uploadeggs           : Any develop eggs are released as eggs and uploaded to the server
<BLANKLINE>

The run command is helpful to run quick remote commands as the buildout user on the remote host

>>> print system('bin/hostout host1 run pwd')
Hostout: Running command 'run' from collective.hostout
Logging into the following hosts as root:
    127.0.0.1
[127.0.0.1] run: sh -c "cd /var/host1 && pwd"
[127.0.0.1] out: ...
Done.

We can also use our login user and password to run quick sudo commands

>>> print system('bin/hostout host1 sudo cat /etc/hosts')
Hostout: Running command 'sudo' from collective.hostout
Logging into the following hosts as root:
    127.0.0.1
[127.0.0.1] run: sh -c "cd /var/host1 && cat/etc/hosts"
[127.0.0.1] out: ...
Done.

Hostout, users and logins
*************************

#TODO

effective-user
  This user will own the buildouts var files. This allows the application to write to database files
  in the var directory but not be allowed to write to any other part of teh buildout code.
  
buildout-user
  The user which will own the buildout files. During bootstrap this user will be created and be given a ssh key
  such that hostout can login and run buildout using this account.

buildout-group
  A group which will own the buildout files including the var files. This group is created if needed in the bootstrap
  command.
  


Definitions
***********

buildout
  zc.buildout is a tool for creating an isolated environment for running applications. It is controlled
  by a configuration file(s) called a buidout file.

buildout recipe
  A buildout file consists of parts each of which has a recipe which is in charge of installing a particular
  piece of softare. 
  
deploy
  Take a an application you are developing and move it to a host server for use. Often deployment will be
  to a staging location for limited use in testing or production for mainstream use. Production, staging
  and development often have different but related to buildouts and could involve different numbers of hosts
  for each.

host
  In the context of this document this a machine or VPS running linux which you would like to deploy your
  application to.

fabric file
  see fabric_

Using builtin deploy command
****************************

Often we have a buildout installed and working on a development machine and we need to get it working on
one or many hosts quickly and easily. 

First you will need a linux host. You'll need a linux with ssh access and sudo access. VPS and cloud hosting is
now cheap and plentiful with options as low as $11USD a month. If you're not sure, pick a pay per hour 
option pre-configured with Ubuntu and give it a go for example rackspacecloud or amazon EC2.

Next you need a production buildout for your application. There are plenty available whether it be for Plone, 
grok, django, BFG, pylons. Often a buildout will come in several files, one for development and one for production. 
Just remember that to get the best performance you will need to understand your buildout.

For this example we've added a development egg
to our buildout as well.

>>> mkdir('example')

>>> write('example', 'example.py',
... """
... def run():
...    print "all your hosts are belong to us!!!"
...
... """)

>>> write('example', 'setup.py',
... """
... from setuptools import setup
...
... setup(
...     name = "example",
...     entry_points = {'default': ['run = example:run']},
...     )
... """)

>>> write('buildout.cfg',
... """
... [buildout]
... parts = example host1
... develop = example
...
... [example]
... recipe = zc.recipe.egg
... eggs = example
... 
... [host1]
... recipe = collective.hostout
... host = 127.0.0.1:10022
... user = root
... password = root
...
... """ )
>>> print system('bin/buildout -N')
Develop: '.../example'
Uninstalling host1.
Installing example.
Installing host1.

Hostout will record the versions of eggs in a local file

>>> print open('hostoutversions.cfg').read()
[versions]
collective.hostout = 0.9.4
<BLANKLINE>
# Required by collective.hostout 0.9.4
Fabric = ...


The deploy command will login to your host and setup a buildout environment if it doesn't exist, upload
and installs the buildout. The deploy command is actually five commands

predeploy
  Bootstrap the server if needed. Create needed users, groups and set permissions and passwordless access
  
uploadeggs
  Any develop eggs are released as eggs and uploaded to the server
  
uploadbuildout
  A special buildout is prepared referencing uploaded eggs and all other eggs pinned to the local picked versions
  
buildout
  Run the buildout on the remote server
  
postdeploy
  Perform any final plugin tasks

>>> print system('bin/hostout host1 deploy')
    running clean
    ...
    creating '...example-0.0.0dev_....egg' and adding '...' to it
    ...
    Hostout: Running command 'predeploy' from '.../collective.hostout/collective/hostout/fabfile.py'
    ...
    Hostout: Running command 'uploadeggs' from '.../collective.hostout/collective/hostout/fabfile.py'
    Hostout: Preparing eggs for transport
    Hostout: Develop egg /sample-buildout/example changed. Releasing with hash ...
    Hostout: Eggs to transport:
    	example = 0.0.0dev-...
    Hostout: Wrote versions to /sample-buildout/host1.cfg
    ...
    Hostout: Running command 'uploadbuildout' from '.../collective.hostout/collective/hostout/fabfile.py'
    ...
    Hostout: Running command 'buildout' from '.../collective/hostout/fabfile.py'
    ...
    Hostout: Running command 'postdeploy' from '.../collective.hostout/collective/hostout/fabfile.py'
    ...

We now have a live version of our buildout deployed to our host

The buildout file used on the host pins pins the uploaded eggs

    >>> print open('host1.cfg').read()
    [buildout]
    develop = 
    eggs-directory = /var/lib/plone/buildout-cache/eggs
    versions = versions
    newest = true
    extends = buildout.cfg hostoutversions.cfg
    download-cache = /var/lib/plone/buildout-cache/downloads
    <BLANKLINE>
    [versions]
    example = 0.0.0dev-...



Bootstrapping
-------------

collective.hostout doesn't currently have a builtin bootstrap command as this is currently platform
dependent. You can use extend your hostout from hostout.ubuntu

[hostout]
recipe = collective.hostout
extends = hostout.ubuntu


Hostout will call a bootstrap command if the predeploy command doesn't find buildout
installed at the remote path.
Bootstrap not only installs buildout but
also installs the correct version of python, development tools, needed libraries and creates users needed to
manage the buildout. The buildin bootstrap may not work for all versions of linux so look
for hostout plugins that match the distribution of linux you installed.


Managing Bootscripts
--------------------

Hostout can generate bootscripts to run commands in your buildout directory on the host during startup and
shutdown.

>>> system('bin/hostout host1 "bin/srvctrl start" "bin/srvctrl stop" myinstance')

Will create the boot script /etc/init.d/buildout-myinstance and install the script into the appreopreate 
run levels using the system's run level management (Debian based and RedHat systems currently supported).

The myinstance identifiyer is optional, if it is not supplied the hostout name will be used which 
is "host1" in this case resulting in boot script /etc/init.d/buildout-host1

>>> system('bin/hostout host1 list_bootscripts')

Displays all the bootscripts in the /etc/init.d directory matching buildout-*

>>> system('bin/hostout host1 uninstall_bootscript myinstance')

Will remove the bootscript and unregister it from the run levels.



Deploy options
--------------

buildout
  The configuration file you which to build on the remote host. Note this doesn't have
  to be the same .cfg as the hostout section is in but the versions of the eggs will be determined
  from the buildout with the hostout section in. Defaults to buildout.cfg

effective-user
  This user will own the buildouts var files. This allows the application to write to database files
  in the var directory but not be allowed to write to any other part of teh buildout code.
  
buildout-user
  The user which will own the buildout files. During bootstrap this user will be created and be given a ssh key
  such that hostout can login and run buildout using this account.

buildout-group
  A group which will own the buildout files including the var files. This group is created if needed in the bootstrap
  command.
  

path
  The absolute path on the remote host where the buildout will be created.
  Defaults to ~${hostout:effective-user}/buildout

pre-commands
  A series of shell commands executed before the buildout is run. You can use this 
  to shut down your application. If these commands fail they will be ignored. These
  will be run as root.
  
post-commands
  A series of shell commands executed after the buildout is run. You can use this 
  to startup your application. If these commands fail they will be ignored. These
  will be run as root.
  
sudo-parts
  Buildout parts which will be installed after the main buildout has been run. These will be run
  as root.

parts
  Runs the buildout with a parts value equal to this
  
include
  Additional configuration files or directories needed to run this buildout
   
buildout-cache
  If you want to override the default location for the buildout-cache on the host

python-version
  The version of python to install during bootstrapping. Defaults to version
  used in the local buildout.




Sharing hostout options
***********************

For more complicated arrangements you can use the extends value to share defaults 
between multiple hostout definitions

>>> write('buildout.cfg',
... """
... [buildout]
... parts = prod staging
...
... [hostout]
... recipe = collective.hostout
... password = blah
... user = root
... identity-file = id_dsa.pub
... pre-commands =
...    ${buildout:directory}/bin/supervisorctl shutdown || echo 'Unable to shutdown'
... post-commands = 
...    ${buildout:directory}/bin/supervisord
... effective-user = plone
... include = config/haproxy.in
...  
... 
... [prod]
... recipe = collective.hostout
... extends = hostout
... host = localhost:10022
... buildout =
...    config/prod.cfg
... path = /var/plone/prod
...
... [staging]
... recipe = collective.hostout
... extends = hostout
... host = staging.prod.com
... buildout =
...    config/staging.cfg
... path = /var/plone/staging
...
... """ % globals())

>>> print system('bin/buildout -N')
    Uninstalling host1.
    Installing hostout.
    Installing staging.
    Installing prod.

#>>> print system('bin/hostout deploy')
Invalid hostout hostouts are: prod staging



Using hostout with a python2.4 buildout
***************************************

Hostout itself requires python2.6. However it is possible to use hostout with
a buildout that requires python 2.4 by using buildout's support for different
python interpretters.

>>> write('buildout.cfg',
... """
... [buildout]
... parts = host1
...
... [host1]
... recipe = collective.hostout
... host = 127.0.0.1:10022
... python = python26
...
... [python26]
... executalble = /path/to/your/python2.6/binary
...
... """ )

or alternatively if you don't want to use your local python you can get buildoit to
build it for you.


>>> write('buildout.cfg',
... """
... [buildout]
... parts = host1
...
... [host1]
... recipe = collective.hostout
... host = 127.0.0.1:10022
... python = python26
...
... [python26]
... recipe = zc.recipe.cmmi
... url = http://www.python.org/ftp/python/2.6.1/Python-2.6.1.tgz
... executable = ${buildout:directory}/parts/python/bin/python2.6
... extra_options=
...    --enable-unicode=ucs4
...    --with-threads
...    --with-readline
...
... """ )




Detailed Hostout Options
************************

host
  the IP or hostname of the host to deploy to. by default it will connect to port 22 using ssh.
  You can override the port by using hostname:port

user
  The user which hostout will attempt to login to your host as. Will read a users ssh config to get a default.

password
  The password for the login user. If not given then hostout will ask each time.
  
identity-file
  A public key for the login user.

extends 
  Specifies another part which contains defaults for this hostout
  
fabfiles
  Path to fabric files that contain commands which can then be called from the hostout
  script. Commands can access hostout options via hostout.options from the fabric environment.




Todo list
*********
- import fabfiles so they don't produce warnings

- use decorators for picking user for commands instead of initcommand hack

- properly support inheritance and scope for command plugins

- plugins for database handling including backing up, moving between development, staging and production
  regardless of location.
  
- Integrate with SCM to tag all parts so deployments can be rolled back.

- Handle basic rollback when no SCM exists, for instance when buildout fails.

- Help deploy DNS settings, possibly by hosting company specific plugins

- Incorporate unified installer environment setup scripts directly.

- Support firewalled servers by an optional tunnel back to a client side web proxy.

- Explore ways to make an even easier transition from default plone install to fully hosted site.

Credits
*******

Dylan Jay ( software at pretaweb dot com )




