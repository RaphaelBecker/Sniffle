import logging
import os
import signal
import subprocess

import psutil

logger = logging.getLogger(__name__)

def start_process(command: []) -> subprocess.Popen:
    logger.info(f"Executing command in subprocess: \n{command}")
    # sniffle_process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    # parse argumentlist to string
    shell = True
    if shell:
        argString = ""
        for arg in command:
            argString = argString + " " + str(arg)
        command = argString
    try:
        sniffle_process = subprocess.Popen(command, shell=shell, close_fds=True, preexec_fn=os.setsid)
        logger.info(f"Process with pid: {sniffle_process.pid} started!")
    except subprocess.TimeoutExpired:
        sniffle_process.kill()
        outs, errs = sniffle_process.communicate()
        logger.error(f"Process timeout: outs: {outs} err: {errs}")
    return sniffle_process


def os_kill_pid(pid: int):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 9)
    except OSError:
        return False
    else:
        return True


def kill_process(sniffle_process: subprocess.Popen) -> bool:
    pid = sniffle_process.pid
    os.killpg(os.getpgid(pid), signal.SIGTERM)
    sniffle_process.poll()
    exit_status = sniffle_process.wait()
    if psutil.pid_exists(pid):
        logger.info(f"Process pid {pid} still running after kill! Exit status: {exit_status}!")
        return False
    else:
        logger.info(f"Process pid {pid} terminated with exit status: {exit_status}!")
        return True


def process_running(sniffle_process: subprocess.Popen) -> bool:
    if psutil.pid_exists(sniffle_process.pid):
        return True
    else:
        return False


def list_running_processes():
    subprocesses = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    process_list_os, error = subprocesses.communicate()
    for line in process_list_os.splitlines():
        logger.info(line)
    subprocesses.terminate()


def clean_processes(processes=[]):
    subprocesses = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    process_list_os, error = subprocesses.communicate()

    for line in process_list_os.splitlines():
        for process in processes:
            if process in str(line):
                pid = int(line.split(None, 1)[0])
                logger.info(str(line) + ' with PID: ' + str(pid) + ' terminated!')
                os.kill(pid, 9)
    subprocesses.terminate()


class Processes:
    def __init__(self):
        pass
