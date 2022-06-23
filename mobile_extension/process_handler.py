import datetime
import logging
import subprocess
import time
import os

from mobile_extension import usb_drive, led, system


def create_new_pcap_name(date_string: str) -> str:
    # dd/mm/YY-TH:M:S
    return "blt_sniffle_trace-" + date_string + ".pcap"


def start_sniffle(usb: usb_drive.USBDrive, indicator_led: led.Led, logger: logging.Logger):
    start_dt_opj = datetime.datetime.now()
    dt_string = start_dt_opj.strftime("%d_%m_%Y-T%H_%M_%S")
    blt_tracefile_name = create_new_pcap_name(dt_string)
    safe_path = str(usb.trace_file_folder_path) + "/" + blt_tracefile_name
    cmd_command = usb.config.sniffle_cmd_command_without_outpath + [safe_path]
    sniffle_process = system.start_process(cmd_command)
    if system.process_running(sniffle_process=sniffle_process):
        logger.info(f"Sniffer started!")
        indicator_led.set_blue()
    else:
        logger.error(f"Sniffer was started but process was not able to start!")
    return sniffle_process, safe_path, start_dt_opj


def stop_sniffle(sniffle_process: subprocess.Popen, safe_path: str, indicator_led: led.Led,
                 logger: logging.Logger):
    if system.process_running(sniffle_process):
        if system.kill_process(sniffle_process=sniffle_process):
            logger.info("Sniffer stopped, process successfully killed!")
            time.sleep(.35)
            if os.path.exists(safe_path):
                logger.info(
                    f"BLT trace {safe_path} successfully saved! Size: {(os.path.getsize(safe_path) / 1024)} KB \n")
                indicator_led.indicate_successful()
            else:
                logger.error(f"BLT trace {safe_path} NOT successfully saved!")
                indicator_led.indicate_failure()
