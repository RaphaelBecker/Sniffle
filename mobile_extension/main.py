#!/usr/bin/env python3

# Written by Raphael Becker
# Released as open source under GPLv3
import sys
# dependency root:
from mobile_extension import decryption

sys.path.append("/sniffer/Sniffle")
# print(sys.path)

import logging
import pathlib
from logging.handlers import QueueHandler
import RPi.GPIO as GPIO
import os
import time
import gc

import usb_drive
import button
import led
import system_status
from start_stop_sniffle import start_sniffle_in_process, stop_sniffle_in_process, start_sniffle_in_thread, stop_sniffle_in_thread
from state_machine import Sniffer, Ready, NotMounted, StopSniffing, StartSniffing

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
                                                                backupCount=3)
    wd_file_handler.setLevel(logging.DEBUG)
    wd_file_handler.setFormatter(formatter)
    # noinspection PyargumentList
    logging.basicConfig(level=logging.DEBUG, handlers=[wd_stream_handler, wd_file_handler])
    logger = logging.getLogger('mobile_extension')
    return logger


def main():

    statemachine = Sniffer()

    init()
    logger = set_logger()
    logger.info("\n\nSTART MOBILE EXTENSION FOR SNIFFLE")
    logger.info("logging started!")

    # automount usb drive and get usb_path:
    usb = usb_drive.USBDrive()
    execution_mode = usb.config.execution_mode

    # start button check thread loop:
    sst_tracing_button = button.Button(16, "sst_tracing_button")

    # start indicator led thread:
    status_led = led.Led(8, 10, 12)
    status_led.start()
    status_led.set_off()

    sniffer_running = False

    status = system_status.SystemStatus(usb, status_led, sst_tracing_button, statemachine)
    status.start()

    while True:
        try:
            if usb.mount_status():
                # button state true and sniffer does not run: -> START SNIFFING
                if sst_tracing_button.get_button_state() and not sniffer_running:
                    statemachine.change_state_to(StartSniffing)
                    if execution_mode == "process":
                        sniffle_process, safe_path, start_dt_opj = start_sniffle_in_process(usb, status_led, logger, statemachine)
                    else:
                        sniffle_thread, safe_path, start_dt_opj = start_sniffle_in_thread(usb, status_led, logger, statemachine)
                    sniffer_running = True

                # button state false and sniffer runs: -> STOP SNIFFING
                if not sst_tracing_button.get_button_state() and sniffer_running:
                    statemachine.change_state_to(StopSniffing)
                    if execution_mode == "process":
                        stop_sniffle_in_process(sniffle_process, safe_path, status_led, logger, statemachine)
                    else:
                        stop_sniffle_in_thread(sniffle_thread, safe_path, status_led, logger, statemachine)
                    sniffer_running = False
                    # decrypt
                    ltk = usb.config.ltk
                    usb_path_blt_traces = usb.MOUNT_DIR.joinpath("blt_traces")
                    decryption.decrypt(usb_path_blt_traces, ltk)
                    # copy developer log files to usb drive for bug fix analysis
                    usb.copy_logs_to_usb()
                    gc.collect()

                # button state false and sniffer does not run: -> sniffer idle, waiting for button press
                if not sst_tracing_button.get_button_state() and not sniffer_running:
                    statemachine.change_state_to(Ready)
                    status_led.set_green()
                    time.sleep(.2)

            else:
                statemachine.change_state_to(NotMounted)
                status_led.set_off()
                usb.init_automount()
                time.sleep(.2)
        except KeyboardInterrupt:
            status_led.set_off()
            GPIO.cleanup()
            pass


if __name__ == "__main__":
    main()








