#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import sys
import logging
from configobj import ConfigObj, ConfigObjError, flatten_errors, get_extra_values
from termcolor import colored

def search_workdir():
    workdir = None
    cfg = None

    sys_workdir = '/'

    os.path.expandvars('$HOME')
    usr_workdir = os.path.expanduser('~')

    script_workdir = os.path.dirname(os.path.dirname(__file__))
    last_part = os.path.basename(script_workdir)
    cwd_workdir = script_workdir.strip(last_part)

    sys_cfg_path = os.path.join(sys_workdir,'etc/pluginguard/plugin_guard.cfg')
    usr_cfg_path = os.path.join(usr_workdir,'etc/pluginguard/plugin_guard.cfg')
    cwd_cfg_path = os.path.join(cwd_workdir,'etc/pluginguard/plugin_guard.cfg')

    if os.path.exists(sys_cfg_path):
        workdir = sys_workdir
    elif os.path.exists(usr_cfg_path):
        workdir = usr_workdir
    elif os.path.exists(cwd_cfg_path):
        workdir = cwd_workdir

    if workdir is None:
        return None
    else:
        return workdir
# When needing return more then one cfg path, better use dictionary
#         return {"workdir":workdir,"cfg":cfg}

WORKDIR = search_workdir()

GLOBAL = 'global'
PLUGINS = 'plugins'
DEPENDENCIES = 'dependencies'
DEFAULT_USER = 'default_user'
HOSTNAME = 'hostname'
TYPE = 'type'
PID_FILE = 'pid_file'
START = 'start'
STOP = 'stop'
STATUS = 'status'
CRONTAB_FILE = 'crontab_file'

class LogFormat():

    def create_directory(directory):
        """Create direcotry
        Create partition directory, like "./atpco/YYYYMMDD/hhmmss", if it exists do nothing.
        Args:
            path: An absolutely directory or relative directory with string format.
        Returns:
            True: success
            False: failure
        """
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                return True
            except OSError, e:
                self.LOG.error(e)
                return False
        else:
                return True

    import logging

    log_path = WORKDIR + "var/log/plugin_guard/"
    if os.path.exists(log_path):
        pass
    else:
        if create_directory(log_path):
            print 'Path %s is created' % log_path
        else:
            print 'Path %s create failed' % log_path
            sys.exit(1)

    logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=WORKDIR + "var/log/plugin_guard/plugin_guard.log",
                filemode='a')

class ReadConf(LogFormat):

    def __init__(self):
        self.config_path = WORKDIR + "etc/pluginguard/plugin_guard.cfg"
        self.log_path = WORKDIR + "var/log/plugin_guard/plugin_guard.log"
        self.config = ConfigObj(self.config_path, encoding='UTF8')
        self.default_user = self.config[GLOBAL][DEFAULT_USER]
        self.plugins = self.config[PLUGINS]
#         LogFormat().logging.info('lalala')
        LogFormat().logging.info('Use cfg:%s, log_path:%s, user:%s',
                                 self.config_path, self.log_path, self.default_user)

    def get_plugins(self):
         return self.plugins.keys()
    
    def get_hostname(self,pig_name):
        return self.plugins[pig_name][HOSTNAME]
    def get_type(self,pig_name):
        try:
            return self.plugins[pig_name][TYPE]
        except:
            return None
    def get_dependencies(self,pig_name):
        # if dependencies is not Flase,we need to return a list type here!
        dependencies_list = []
        if self.plugins[pig_name][DEPENDENCIES] == 'False':
            return self.plugins[pig_name][DEPENDENCIES]
        if isinstance(self.plugins[pig_name][DEPENDENCIES],list):
            return self.plugins[pig_name][DEPENDENCIES]
        else:
            dependencies_list.append(self.plugins[pig_name][DEPENDENCIES])
            return dependencies_list 
#    def get_trigger(self,pig_name):
#        return self.plugins[pig_name]['trigger']
    def get_pid_file(self,pig_name):
        return self.plugins[pig_name][PID_FILE]
    def get_crontab_file(self,pig_name):
        return self.plugins[pig_name][CRONTAB_FILE]
    def get_start(self,pig_name):
        return self.plugins[pig_name][START]
    def get_stop(self,pig_name):
        return self.plugins[pig_name][STOP]
    def get_status(self,pig_name):
        return self.plugins[pig_name][STATUS]

