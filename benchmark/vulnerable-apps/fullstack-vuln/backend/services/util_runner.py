import subprocess


def run_system_command(cmd):
    return subprocess.getoutput(cmd)
