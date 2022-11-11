import pathlib
from unittest import TestCase
from mobile_extension import decryption
import mobile_extension.configuration as configuration
import mobile_extension.usb_drive as usb


class Test(TestCase):
    def test_crackle_version(self):
        decryption.crackle_version("./../../../../crackle/crackle")

    def test_decrypt(self):
        # blt_traces
        usb_drive = usb.USBDrive()
        usb_path_blt_traces = usb_drive.MOUNT_DIR.joinpath("blt_traces")
        MOUNT_DIR = pathlib.Path("/media/usb0")
        config = configuration.Config(MOUNT_DIR)
        ltk = config.ltk
        print("Trace path on usb: " + str(usb_path_blt_traces))
        print("LTK:  " + ltk)
        decryption.decrypt(usb_path_blt_traces, ltk, "./../../../../crackle/crackle")