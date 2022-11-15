import logging
import os
import subprocess
from os import listdir
from os.path import isfile, join


logger = logging.getLogger(__name__)


def check_pairing_event(file, traces_path, crackle_executable_path):
    return_str = "Nothing to check for pairing event!"
    if file.split('.')[1] == "pcap" and "_decrypted" not in file.split('.')[0]:
        encrypted_file = os.path.join(traces_path, file)
        proc = subprocess.Popen(
            [crackle_executable_path, "-i", encrypted_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output, err = proc.communicate(b"input data that is passed to subprocess' stdin")
        rc = proc.returncode
        return_str = output.decode('UTF-8') + f"Processed with exit code {rc}."
    return return_str



def decrypt_file(ltk, file, traces_path, crackle_executable_path):
    return_str = "Nothing to decrypt!"
    if file.split('.')[1] == "pcap" and "_decrypted" not in file.split('.')[0]:
        encrypted_file = os.path.join(traces_path, file)
        file_decrypted = os.path.join(traces_path, file.split('.')[0] + '_decrypted' + '.' + file.split('.')[1])
        if not os.path.exists(file_decrypted):
            proc = subprocess.Popen(
                [crackle_executable_path, "-i", encrypted_file, "-o", file_decrypted, "-l", ltk],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            output, err = proc.communicate(b"input data that is passed to subprocess' stdin")
            rc = proc.returncode
            return_str = output.decode('UTF-8') + f"Processed with exit code {rc}."
        else:
            return_str = "Already decrypted"
    return return_str


def decrypt(traces_path: str, ltk: str, crackle_executable_path="./../../../crackle/crackle"):
    traces_path = str(traces_path)
    crackle_executable_path = str(crackle_executable_path)
    only_files = [f for f in listdir(traces_path) if isfile(join(traces_path, f))]
    for i, file in enumerate(only_files):
        logger.info(f"NR({i}) Try to decrypt {file}:")
        return_str = decrypt_file(ltk, file, traces_path, crackle_executable_path)
        logger.info(return_str)


def crackle_version(crackle_executable_path: str):
    return_code = subprocess.call([crackle_executable_path, "--version"])
    print(f"Processed with exit code {return_code}.")
