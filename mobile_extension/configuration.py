import os
import yaml
import logging
from os import walk
import pathlib


class Config:
    def __init__(self, config_path: pathlib.Path):
        """config_path: root directory of usb flash.
        The filename must contain 'config', '.yml' file extension required
        and be place at root dir of usb flash drive"""
        self.config_dictionary = dict()
        self.sniff_receiver_base_command = ["sudo", "/bin/python3", "/sniffer/python_cli/sniff_receiver.py"]
        self.serial_port_command_argument = ["-s", "/dev/ttyACM0"]
        self.output_argument = ["-o"] # output path can only be added when cmd command is called, because out path contains timestamp in blt_trace_name pcap
        self.optional_arguments = [] # filled from config file with init_config(config_path)
        self.sniffle_cmd_command_without_outpath = [] # filled from usb class if mounted
        self.logger = None
        self.init_config(config_path)


    def init_config(self, config_path: pathlib.Path):
        self.logger = logging.getLogger(__name__)
        filenames = next(walk(config_path), (None, None, []))[2]  # [] if no file
        for filename in filenames:
            if "config" in filename:
                if ".yml" in filename:
                    # sanitize:
                    if ".txt" in filename:
                        filename_path = config_path.joinpath(filename)
                        sanitized_filename_path = config_path.joinpath(filename.replace('.txt', ''))
                        os.rename(filename_path, sanitized_filename_path)
                        self.logger.info(f"Sanitized {filename_path} to {str(sanitized_filename_path)}")
                        filename = filename.replace('.txt', '')
                    config_path = config_path.joinpath(filename)
                    with open(config_path, 'r') as stream:
                        try:
                            self.config_dictionary = yaml.safe_load(stream=stream)
                            self.init_cmd_command()
                        except yaml.YAMLError as exception:
                            self.logger.error("Error while loading config.", exc_info=True)
                            raise exception
                else:
                    self.logger.error(f"Not able to load Config file: '{filename}'. No '.yml' file extension.")
            else:
                self.logger.error(
                    f"Cannot load config file: {filename}. The filename must contain 'config', '.yml' file extension required and be place at root dir of usb flash drive.")


    def init_cmd_command(self):
        if "optional_arguments" in self.config_dictionary:
            self.optional_arguments = self.config_dictionary["optional_arguments"]
            self.sniffle_cmd_command_without_outpath = self.sniff_receiver_base_command + self.serial_port_command_argument + self.optional_arguments + self.output_argument
            try:
                self.logger.info(f"CMD sniffle command without output path: {self.sniffle_cmd_command_without_outpath}")
            except OSError:
                pass
        else:
            try:
                self.logger.error(f"<optional_arguments> not found in config file>, import of arguments not possible. Dict: {str(self.config_dictionary)}")
            except OSError:
                pass

    def get_config(self) -> dict:
            return self.config_dictionary

    def save_config(self, save_config_path: pathlib.Path):
        """saves the dictionary to save_config_path"""
        with open(save_config_path, 'w') as outfile:
            try:
                yaml.dump(self.config_dictionary, outfile, default_flow_style=False)
                self.logger.info(f"Config saved to <{str(save_config_path)}>")
            except yaml.YAMLError as exception:
                self.logger.error(f"Error while writing config to {str(save_config_path)}", exc_info=True)
                raise exception

