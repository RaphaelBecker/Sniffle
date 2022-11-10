# crackle executable has to be there
import subprocess
from os import listdir
from os.path import isfile, join

# according to where you place the script:
# crackle = "./../../crackle"
# traces_path = "../"
# update ltk:
# ltk = ""


def decrypt(traces_path: str, cracke_executable_path: str, ltk: str):
    onlyfiles = [f for f in listdir(traces_path) if isfile(join(traces_path, f))]
    for file in onlyfiles:
        if file.split('.')[1] == "pcap":
            encrypted_file = traces_path + file
            file_decrypted = traces_path + file.split('.')[0] + '_decrypted' + '.' + file.split('.')[1]
            print('---------------------------------------------------------------------------')
            returncode = subprocess.call([cracke_executable_path, "-i", encrypted_file, "-o", file_decrypted, "-l", ltk])
            print(f"{file}:")
            print(f"Processed with exit code {returncode}.")