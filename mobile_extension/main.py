#!/usr/bin/env python3

# Written by Raphael Becker
# Released as open source under GPLv3
import logging
import pathlib
import sys
from logging.handlers import QueueHandler
import RPi.GPIO as GPIO
import os
import time

import usb_drive
import button
import led
import process_handler
import system_status

sys.path.append("/sniffer")


def init():
    GPIO.setmode(GPIO.BOARD)


def set_logger() -> logging.Logger:
    root_dir = pathlib.Path(__file__).resolve().parents[0]
    logs_path = root_dir.joinpath('logs')
    os.makedirs(logs_path, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
    wd_stream_handler = logging.StreamHandler()
    wd_stream_handler.setLevel(logging.INFO)
    wd_stream_handler.setFormatter(formatter)
    wd_file_handler = logging.handlers.TimedRotatingFileHandler(filename=logs_path.joinpath('mobile_extension.log'),
                                                                when='midnight',
                                                                backupCount=4)
    wd_file_handler.setLevel(logging.DEBUG)
    wd_file_handler.setFormatter(formatter)
    # noinspection PyargumentList
    logging.basicConfig(level=logging.DEBUG, handlers=[wd_stream_handler, wd_file_handler])
    logger = logging.getLogger('mobile_extension')
    return logger



def main():
    init()
    logger = set_logger()
    logger.info("\n\nSTART MOBILE EXTENSION FOR SNIFFLE")
    logger.info("logging started!")

    # automount usb drive and get usb_path:
    usb = usb_drive.USBDrive()

    # start button check thread loop:
    sst_tracing_button = button.Button(16, "sst_tracing_button")

    # start indicator led thread:
    indicator_led = led.Led(8, 10, 12)
    indicator_led.start()
    indicator_led.set_off()

    sniffer_running = False

    status = system_status.SystemStatus(usb)
    status.start()

    while True:
        try:
            if usb.mount_status():
                # button state true and sniffer does not run: -> START SNIFFING
                if sst_tracing_button.get_button_state() and not sniffer_running:
                    sniffle_process, safe_path, start_dt_opj = process_handler.start_sniffle(usb, indicator_led, logger)
                    sniffer_running = True

                # button state false and sniffer runs: -> STOP SNIFFING
                if not sst_tracing_button.get_button_state() and sniffer_running:
                    process_handler.stop_sniffle(sniffle_process, safe_path, indicator_led, logger)
                    sniffer_running = False
                    # copy developer log files to usb drive for bug fix analysis
                    usb.copy_logs_to_usb()

                # button state false and sniffer does not run: -> sniffer idle, waiting for button press
                if not sst_tracing_button.get_button_state() and not sniffer_running:
                    indicator_led.set_green()
                    time.sleep(.3)
            else:
                indicator_led.set_off()
                usb.init_automount()
                time.sleep(.5)
        except KeyboardInterrupt:
            indicator_led.set_off()
            GPIO.cleanup()
            pass


if __name__ == "__main__":
    main()
