# Mshell - Multiple Remote Servers Controller

=====================================================

## Mshell

With the help of Mshell, users can manipulate multiple servers concurrently. The input command will be sent to all configured servers through ssh.

## Platform 

Windows 10

## Getting Started

1. Download our release version.
2. Write down your configuration in servers.json
3. Doule click Mshell.exe

## inner command

- reload: 
  - reload configuration in servers.json.
- show
  - show all connected servers.
- sftp: 
  - transport a file to all remote servers.
  - example: sftp slocal.txt remote.txt.

## Log

Mshell will generate a log directory (resp. file) for every run (resp. connected server). The log directory (file resp.) is named according to program start time (resp. ip).

## Contact

Author: Penglai Cui.

Company: Institute of computing technology, China. 