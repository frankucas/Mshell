
import time
import os
from contextlib import contextmanager 
from threadpool import ThreadPool,makeRequests
from Assist import remoteAssist,assistBase,reloadException,loadJson
import pdb

class Controller(assistBase):
    """
        1) Read network configuration from servers.json.
        The structure of servers.json like this:
            {id: [ip, user_name, passwd]}
        2) connect servers and exec given commands.
    """
    def __init__(self):
        self.log_time = time.strftime("%Y-%m-%d_%H-%M-%S",time.localtime())
        self.log_path = f"log\\{self.log_time}"
        os.makedirs(self.log_path)
        self.ssh_assist = remoteAssist()
        self.load_json  = loadJson()
        self.local_command = {
            "show"   : self.show_connected_servers,
            "reload" : self.raise_reload_exception,
        }
    
    def is_zero_sucess_sessions(self, sucess_num, timeout=30):
        if sucess_num: return 
        assistBase.print_dangerous_message(f"No accessible hosts, please check servers.json. The program will end in {timeout}s.")
        time.sleep(timeout)
        exit(0)
    
    def check_failed_sessions(self, sessions):
        sucess_sessions = {}
        for ip,*_ in sessions: sucess_sessions[ip]=True
        for ip,*_ in self.servers_configure:
            if not sucess_sessions.get(ip):
                assistBase.print_dangerous_message(f"Connection to {ip} failed.")
        self.is_zero_sucess_sessions(len(sucess_sessions))
    
    def init_ssh_and_sftp_sessions(self):
        sessions = []
        for configure in self.servers_configure:
            ssh  = self.ssh_assist.init_ssh_session(configure)
            sftp = ssh.open_sftp()
            if ssh and sftp: sessions.append([configure[0],ssh,sftp])
        return sessions

    @contextmanager
    def init_sessions(self):
        print("* Conneting to servers...")
        sessions = self.init_ssh_and_sftp_sessions()
        self.is_zero_sucess_sessions(len(sessions))
        try: yield sessions
        except reloadException: pass
        finally:
            for _,ssh,sftp in sessions:
                ssh.close()
                sftp.close()
    
    def prepare_ssh_requests(self, sessions, command):
        return makeRequests(self.ssh_assist.ssh_exec_one_command,[[ssh,self.log_path,ip,command] for ip,ssh,_ in sessions])
    
    def get_address(self,command):
        command_list = list(command.split())
        if len(command_list)<3: return " "," "
        return command_list[1],command_list[2]

    def prepare_sftp_requests(self, sessions, command):
        source,dest = self.get_address(command)
        return makeRequests(self.ssh_assist.sftp_exec_one_transport,[[sftp,ip,source,dest] for ip,_,sftp in sessions])

    def is_sftp(self, command):
        return command.strip().split()[0]=="sftp"

    def prepare_requests(self, sessions, command):
        if self.is_sftp(command): return self.prepare_sftp_requests(sessions, command)
        return self.prepare_ssh_requests(sessions, command)

    def exec_one_remote_command(self, sessions, command):
        requests = self.prepare_requests(sessions, command)
        for req in requests: self.thread_pool.putRequest(req)
        self.thread_pool.wait()
    
    def show_connected_servers(self, sessions):
        print(f"* {len(sessions)} servers connected.")
        for ip,*_ in sessions: print(f"* {ip}")
    
    def raise_reload_exception(self, sessions=None):
        raise reloadException
    
    def exec_one_command(self, sessions, command):
        exe_name = command.strip().split()[0]
        if self.local_command.get(exe_name): self.local_command[exe_name](sessions)
        else: self.exec_one_remote_command(sessions, command)

    def input_command(self):
        while True:
            command = input("CMD:/> ")
            if command:return command
    
    def init_configure(self):
        self.servers_configure = [configure for configure in self.load_json.get_network_configure().values()]
        self.thread_pool = ThreadPool(len(self.servers_configure))
    
    def run_ide(self):
        self.init_configure()
        with self.init_sessions() as sessions:
            while command:=self.input_command():
                self.exec_one_command(sessions, command)
        self.run_ide()

if __name__=="__main__":
    controller = Controller()
    controller.run_ide()