# A compiled crackle executable has to be on the system
import subprocess
import sys
from os import listdir
from os.path import isfile, join

import logging

logger = logging.getLogger(__name__)


def decrypt(traces_path: str, ltk: str, crackle_executable_path="./../../../crackle/crackle"):
    traces_path = str(traces_path)
    crackle_executable_path = str(crackle_executable_path)
    onlyfiles = [f for f in listdir(traces_path) if isfile(join(traces_path, f))]
    for file in onlyfiles:
        if file.split('.')[1] == "pcap":
            encrypted_file = traces_path + file
            file_decrypted = traces_path + file.split('.')[0] + '_decrypted' + '.' + file.split('.')[1]
            proc = subprocess.Popen(
                [crackle_executable_path, "-i", encrypted_file, "-o", file_decrypted, "-l", ltk],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            output, err = proc.communicate(b"input data that is passed to subprocess' stdin")
            rc = proc.returncode

            logger.info(f"Try to decrypt {file}:")
            logger.info(output.decode('UTF-8') + f"Processed with exit code {rc}.")


def crackle_version(crackle_executable_path: str):
    return_code = subprocess.call([crackle_executable_path, "--version"])
    print(f"Processed with exit code {return_code}.")
