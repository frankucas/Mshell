import paramiko  
from contextlib import contextmanager 
from colorama import Fore,Style,init
import json
import time

class loadJson:
    def is_annotation(self, line):
        return line[:2]=="//"

    def strip_annotation(self, file_handle):
        no_annotaion_content = ""
        for line in file_handle:     
            if self.is_annotation(line.strip()): continue
            no_annotaion_content += line
        return no_annotaion_content

    @contextmanager
    def json_load_except_handler(self, timeout=30):
        try: yield
        except json.decoder.JSONDecodeError as e:
            assistBase.print_dangerous_message(f"Fatal error, program will end in {timeout}s.\n{e}")
            time.sleep(timeout)
            exit(1)

    def get_network_configure(self):
        with open("servers.json", "r", encoding='utf-8') as f:
            with self.json_load_except_handler():
                return json.loads(self.strip_annotation(f))

class reloadException(Exception):
    def __str__(self):
        return "Reloading..."

class assistBase:
    @contextmanager
    def pass_connect_fail(self, ip, method="SSH"):
        try: yield
        except: assistBase.print_dangerous_message(f"{method} connection to {ip} failed.")
    
    @staticmethod
    def print_dangerous_message(message):
        init(autoreset=True)
        print(Fore.RED+Style.BRIGHT+message+Style.RESET_ALL)

    def store_txt_file(self, path, content, access_authority="a"):
        with open(path+".txt",access_authority,encoding='utf-8')as f:
            f.writelines(content)

class remoteAssist(assistBase):
    @contextmanager
    def path_not_found(self, ip):
        try: yield
        except: assistBase.print_dangerous_message(f"Error happened in {ip}: sftp path not found")
        else: print("* Transport succeed.")

    def init_ssh_session(self, configure):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        with self.pass_connect_fail(configure[0],"SSH"):
            ssh.connect(hostname=configure[0], port=configure[3], username=configure[1], password=configure[2], timeout=5)
            return ssh

    def error_happened(self, stderr_str):
        return ("error" in stderr_str) or ("Error" in stderr_str) or ("command not found" in stderr_str)

    def store_line(self, log_path, read_method):
        line = read_method()
        if isinstance(line,list): line="".join(line) 
        line = line.replace("\r\n","\n")
        self.store_txt_file(log_path, f"{line}")
        return line 

    def store_stdout(self, ip, path, stdout, command):
        stderr_str,log_path = "",path+f"\{ip}"
        self.store_txt_file(log_path, f"CMD: {command}\n")
        while not stdout.channel.exit_status_ready():
            stderr_str += self.store_line(log_path, stdout.readline)
        stderr_str += self.store_line(log_path, stdout.readlines)
        if self.error_happened(stderr_str): assistBase.print_dangerous_message(f"Error happened in {ip}.") 

    def ssh_exec_one_command(self, args):
        """
            @args: [session, log_path, ip, command]
        """
        _,stdout,_ = args[0].exec_command(args[3], get_pty=True)
        self.store_stdout(args[2], args[1], stdout, args[3])

    def sftp_exec_one_transport(self, args):
        """
            @args: [transport, ip source, destination]
        """
        with self.path_not_found(args[1]):
            args[0].put(args[2],args[3])


    