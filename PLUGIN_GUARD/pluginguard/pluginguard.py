#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import sys
from configobj import ConfigObj, ConfigObjError, flatten_errors, get_extra_values
import readconfig
from plugincontroller import PluginController
from readconfig import ReadConf
from termcolor import colored
from readconfig import LogFormat
WORKDIR = readconfig.WORKDIR

START='start'
STOP='stop'
STATUS='status'
HELPINFO = 'python pluginguardlogic.py start|stop|status plugin_name1 plugin_name2...'
global CHEKC_FLAG
CHECK_FLAG = 0

class PluginGuard(LogFormat,ReadConf):

    def __init__(self):
        self.config_path = WORKDIR + "/etc/plugin_guard.cfg"
        self.config = ConfigObj(self.config_path, encoding='UTF8')
        self.pigctrl = PluginController()

readconf = ReadConf()
# clihandler = CmdLnHandler()
pigctrl = PluginController()

def check_dependency1():
    """
    plugins's dependency must in plugins_guard.cfg, otherwise, we can not follow the dependency.
    """
    all_plugins = readconf.get_plugins()
    for pname in all_plugins:
        dependency_plugins = readconf.get_dependencies(pname)
        if dependency_plugins == 'False':pass
        else:
           if set(dependency_plugins).issubset(set(all_plugins)):pass
           else:
               global CHECK_FLAG
               CHECK_FLAG = '1'
               info = "ERROR! %s's dependencies: %s is not in configs: %s" %(pname,dependency_plugins, all_plugins)
               #info = "lalala"
               print colored(info,color='cyan',on_color=None,attrs=['bold'])

def check_dependency2():
    all_plugins = readconf.get_plugins()
    for pname in all_plugins:
        try:
            pigctrl.get_need_to_start(pname)
        except RuntimeError:
            dependency_plugins = readconf.get_dependencies(pname)
            global CHECK_FLAG
            CHECK_FLAG = '1'
            info = "Enter endless loop,check config: %s--dependencies--%s" %(pname,dependency_plugins)
            print colored(info,color='cyan',on_color=None,attrs=['bold'])

#try:
#    check_dependency1()
#    check_dependency2()
#except RuntimeError:
    #global CHECK_FLAG
#    CHECK_FLAG = '1'
#    info = "When we seek dependencies, we enter a endless loop,check the config"
#    print colored(info,color='cyan',on_color=None,attrs=['bold'])
check_dependency1()
check_dependency2()

if CHECK_FLAG == '1':
    os._exit(0)


def main():
    pig = PluginGuard()
    if len(sys.argv) >= 2:
        if sys.argv[1] == START:
            pig.pigctrl.start(sys.argv[2:])
        elif sys.argv[1] == STOP:
            pig.pigctrl.stop(sys.argv[2:])
#        elif sys.argv[1] == RESTART:
#            svc.stop()
#            svc.start()
        elif sys.argv[1] == STATUS:
            pig.pigctrl.status()
        else:
            print HELPINFO
    else:
        print HELPINFO

def start():
    pig = PluginGuard()
    if len(sys.argv) >= 1:
        pig.pigctrl.start(sys.argv[1:])
    else:
        print HELPINFO

def stop():
    pig = PluginGuard()
    if len(sys.argv) >= 1:
        pig.pigctrl.stop(sys.argv[1:])
    else:
        print HELPINFO

def status():
    pig = PluginGuard()
    pig.pigctrl.status()

if __name__ == '__main__':
    main()
