import sys,os
from readconfig import ReadConf
from readconfig import LogFormat
from prettytable import PrettyTable
import commands
import time
import re
from subprocess import Popen,PIPE

DAEMON='DAEMON'
CRONTAB='CRONTAB'

class PluginController(ReadConf):

    def __init__(self):
        ReadConf.__init__(self)
        self._pig_name = None
        self._pig_cmd = None
        self.need_to_start_list = []

    def hello(self):
        print "hello"

    def run_cmd(self,pname,cmd):
        """
        run the command and get the echo
        """
#        status, result = commands.getstatusoutput(cmd)
#        return result
        p = Popen(cmd,shell=True,stdout=PIPE)
        p.wait()
        result = p.stdout.read()
        return result

    def show_result(self,pname,result):
        '''
        Use this function for display which cann't added in prettytable. Some results has terminal color which makes prettytable mistake 
        '''
        #print "%r--%r: %r" % (self.get_type(pname), pname, result)
        print self.get_type(pname), pname,":" ,result
        return True
        
    def hide_file(self,pname):
        all_file_path = self.get_crontab_file(pname)
        file_path,file_name = os.path.split(all_file_path)

        hide_all_file_name = os.path.join(file_path,'.'+file_name)
        #print all_file_path, hide_all_file_name
        try:
            os.rename(all_file_path, hide_all_file_name)
            result = "DEAD"
        except:
            return "FAILED"
        return result

    def unhide_file(self,pname):

        all_file_path = self.get_crontab_file(pname)
        file_path,file_name = os.path.split(all_file_path)
        hide_all_file_name = os.path.join(file_path,'.'+file_name)
        try:
            os.rename(hide_all_file_name,all_file_path)
        except:
            return "FAILED"
        return True

    def num2human_readable(self,num):
        if num == 0:
           return "RUNNING"
        if num == 3:
           return "DEAD"
        else:
           return "PENDING ERRORCODE:"+str(num)

    def get_need_to_start(self,pname):

#        print "pname is:",pname
#        print self.get_dependencies(pname),self.need_to_start_list
        if self.get_dependencies(pname) == 'False':
            return
        self.need_to_start_list = self.get_dependencies(pname) + self.need_to_start_list
#        print "add %s into _need_to_start_list" % self.get_dependencies(pname)
#        raw_input("break point")
#        print "need_to_start_list is:",self.need_to_start_list
        for ppname in self.get_dependencies(pname):
#            print "ppname is", ppname
            if self.get_dependencies(ppname) == 'False':
                pass
            else:
                self.get_need_to_start(ppname)

    def make_list_unique(self,unprocessed_list):
        unique_list = list(set(unprocessed_list))
        unique_list.sort(key = unprocessed_list.index)
        return unique_list

    def query_one_plugin_status(self,pname):
        '''
        reference to /etc/init.d/functions standard

        return 0 ok
        return 1 Program is dead and /var/run pid file exists
        return 2 ${base} dead but subsys locked
        return 3 Program is not running
        return 4 user had insufficient privilege
        '''
        if self.get_type(pname) == DAEMON:
            
            lock_dir = os.path.join("/var/lock/subsys/", pname)
            if self.get_pid_file(pname) == 'False':
                result = self.run_cmd(pname,self.get_status(pname))
                return result

            if os.access(self.get_pid_file(pname) ,os.F_OK):
                pid = None
                if not os.access(self.get_pid_file(pname) ,os.R_OK):
                    return 4
                else:
                    with open (self.get_pid_file(pname)) as line:
                        for p in line:
                            p = p.strip('\n')
                            pid_dir = os.path.join("/proc", p)
                            if str.isdigit(str(p)) and os.path.isdir(pid_dir):
                                pid = p

                    if str.isdigit(str(pid)):
                        return 0

                    return 1

            # See if /var/lock/subsys/${lock_file} exists
            elif os.access(lock_dir ,os.F_OK):
                return 2

            else:
                return 3

        if self.get_type(pname) == CRONTAB:

            if os.path.exists(self.get_crontab_file(pname)):
                if os.path.exists(self.get_crontab_file(pname)) == 0:
                    return 1
                else:
                    return 0
            else:
                return 3

    def start_one_plugin(self,pname):
        #if pname's all depend pname started ,start it!
        dependency_fail = []
        if self.get_dependencies(pname) == 'False':
            pass
        else:
            for dependency in self.get_dependencies(pname):
                num = self.query_one_plugin_status(dependency)
                if num != 0:
                    dependency_fail.append([dependency,num])

        if len(dependency_fail) == 0:
            if self.get_type(pname) == DAEMON:
                self.run_cmd(pname, self.get_start(pname))
                time.sleep(1)

            if self.get_type(pname) == CRONTAB:
                result = self.unhide_file(pname)

    def stop_one_plugin(self,pname):
        if self.get_type(pname) == DAEMON:
            self.run_cmd(pname, self.get_stop(pname))
            time.sleep(1)

        if self.get_type(pname) == CRONTAB:
            if os.path.isfile(self.get_crontab_file(pname)):
                self.hide_file(pname)

    def status(self):
        """
        return all registried plugins
        """
        self._pig_name = self.get_plugins()
        print "ALL PLUGINS:    ", ','.join(self._pig_name)
        #show = PrettyTable(["Plugin Type","Plugin Name","Hostname","Status","Where is PID","PID","Where is CRON"])
        show = PrettyTable(["Plugin Type","Plugin Name","Hostname","Status","Crontab File","Pid"])
        show.sortby = "Plugin Type"
        show.padding_width = 1 # One space between column edges and contents (default)

        for pname in self._pig_name:
#             LogFormat().logging.info('lalala2')
            result = self.num2human_readable(self.query_one_plugin_status(pname))
            show.add_row([self.get_type(pname), 
                      pname, 
                      self.get_hostname(pname), 
                      result,
                      os.path.basename(self.get_crontab_file(pname)),
                      os.path.basename(self.get_pid_file(pname)),
                    ])
        print (show)

    def start(self,*args):
        """
        We need to check dependencies,check already running and then start them one by one
        """
        received_plugins = args[0]
        self._pig_name = self.get_plugins()
        LogFormat().logging.info('Received start plugins: %s',received_plugins)
        show = PrettyTable(["Plugin Type","Plugin Name","Result"])
        show.sortby = "Plugin Type"
        for pname in received_plugins:

            self.need_to_start_list = []
            if pname not in self._pig_name:
                result = "Wrong parameter,we cann't find this plugin"
                show.add_row([self.get_type(pname), pname, result])
                continue

            self.get_need_to_start(pname)
            needed_to_start = self.need_to_start_list
            LogFormat().logging.info('Get dependencies start plugin: %s',self.need_to_start_list)
            needed_to_start_uniq = self.make_list_unique(needed_to_start)
            LogFormat().logging.info('Start plugins: %s dependencies plugins:%s',[pname],needed_to_start_uniq)
            for start_pname in needed_to_start_uniq:
                '''
                start the dependency plugin one by one
                '''
                if self.num2human_readable(self.query_one_plugin_status(start_pname)) == 'RUNNING':
                    result = "ALREADY STARTED"
#                     show.add_row([self.get_type(start_pname), start_pname, result])
                else:
#                    raw_input("break point")
                    self.start_one_plugin(start_pname)
                    result = self.num2human_readable(self.query_one_plugin_status(start_pname))
#                     show.add_row([self.get_type(start_pname), start_pname, result])

            if self.num2human_readable(self.query_one_plugin_status(pname)) == 'RUNNING':
                result = "ALREADY STARTED"
                show.add_row([self.get_type(pname), pname, result])
            else:
                self.start_one_plugin(pname)
                result = self.num2human_readable(self.query_one_plugin_status(pname))
#                 print "Plugin %s start result:" % pname
                show.add_row([self.get_type(pname), pname, result])

        print (show)

    def stop(self,*args):
        """
        directly stop without any check
        """
        received_plugins = args[0]
        self._pig_name = self.get_plugins()
        show = PrettyTable(["Plugin Type","Plugin Name","Result"])
        show.sortby = "Plugin Type"

        LogFormat().logging.info('Received stop plugins: %s',received_plugins)
        for pname in received_plugins:
            if pname not in self._pig_name:
                result = "Wrong parameter,we cann't find this plugin"
                show.add_row([self.get_type(pname), pname, result])
                continue

            stop_pname = pname
            self.stop_one_plugin(stop_pname)
            result = self.num2human_readable(self.query_one_plugin_status(stop_pname))
#             print "Plugin %s start result:" % pname
            if result != "DEAD": result = "FAILED" 
            show.add_row([self.get_type(pname), pname, result])

        print(show)
