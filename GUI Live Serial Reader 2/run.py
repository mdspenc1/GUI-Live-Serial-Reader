import time
import json
import serial
import multiprocessing as mlt
from collections import Counter
from serial.tools import list_ports
from resource_manager import COMMUNICATION, CURRENT_CONFIG
from configuration import configuration
import dict_methods

class run_plots:
    def __init__(self):
        self.port_objs = list_ports.comports()
        self.port_names = [port.device for port in self.port_objs]
        self.plot_dict = {}
        self.serial_com = None
        self.valid_port = False
        self.plot_cycle_termination_event = mlt.Event()

    def start_gui_plot_processes(self):
        # plot_cycle_termination_event = mlt.Event()
        gui_plot_cycle_process = mlt.Process(target=self.gui_plot_cycle, args=(self.plot_cycle_termination_event, ))
        gui_plot_cycle_process.start()
        # if self.plot_cycle_termination_event.is_set():
        #     gui_plot_cycle_process.join()
        # return

    def gui_plot_cycle(self, termination_event):
        # Creates objects related to port validation and access which are mutable within the memory space of the process
        # self.port_objs = list_ports.comports()
        # self.port_names = [port.device for port in self.port_objs]
        # self.serial_com = serial.Serial()
        # self.valid_port = False
        print("plot cycle process has been entered!")
        # Creates a communication dictionary from communication.json
        communication_dict = read_communication_file()
        while True:
            # Checks if the module currently designated to write in communication.json is the backend_module
            time.sleep(1)
            if (
                communication_dict['designated_author'] == 'backend'
                and communication_dict['gui'] == 'waiting'
                and communication_dict['backend'] == 'requested'
                ):
                communication_dict['gui'] = 'requested' # Updating communication dict to request the gui module to run one of its methods
                communication_dict['update_config_to_json'] = True # Updating communication dict to tell the gui module which method is being requested
                communication_dict['designated_author'] = 'gui' # Changing the designated author before writing the new communication dict to communication.json to prevent two modules writing into it at once
                communication_dict['backend'] = 'waiting'
                # Dictionary of which keys must have what value in communication.json in order to unpause once the request has been completed by the gui module
                unpause_dict = {
                    'update_gui_plots': True,
                    'update_config_to_json': False,
                    'gui': 'waiting',
                    'backend': 'requested',
                    'designated_author': 'backend'
                }
                write_and_wait_function(unpause_dict, communication_dict, 'backend has requested gui to update config.json and is waiting!') # Waits for the gui module to confirm that it has completed the requested task before continuing the backend process
            else:
                communication_dict['skip_to_beginning'] = True
            config = config_from_json()
            communication_dict = read_communication_file()

            if not communication_dict['skip_to_beginning'] and isinstance(config, configuration):
                self.update_gui_plots(communication_dict, config)

            if (
                not communication_dict['skip_to_beginning']
                and not communication_dict['validate_port_settings']
                and communication_dict['generate_gui_plots']
                and communication_dict['gui'] == 'requested'
                and communication_dict['backend'] == 'waiting'
                and communication_dict['designated_author'] == 'gui'
            ):
                unpause_dict = {
                    'validate_port_settings': True,
                    'generate_gui_plots': False,
                    'gui': 'waiting',
                    'backend': 'requested',
                    'designated_author': 'backend'
                }
                write_and_wait_function(unpause_dict, communication_dict, 'process has requested and is waiting for gui to generate plots!')
                communication_dict = read_communication_file()
            if (
                communication_dict['running']
                and not communication_dict['skip_to_beginning']
                and communication_dict['validate_port_settings']
                and communication_dict['gui'] == 'waiting'
                and communication_dict['backend'] == 'requested'
                and communication_dict['designated_author'] == 'backend'
            ):
                self.validate_port_settings(communication_dict, config)
            
            if (
                communication_dict['running']
                and not communication_dict['skip_to_beginning']
                and communication_dict['obtain_serial_data']
                and communication_dict['gui'] == 'waiting'
                and communication_dict['backend'] == 'requested'
                and communication_dict['designated_author'] == 'backend'
            ):
                self.obtain_serial_data(communication_dict)
            
            if (
                communication_dict['running']
                and not communication_dict['skip_to_beginning']
                and communication_dict['plot_serial_data']
                and communication_dict['gui'] == 'requested'
                and communication_dict['backend'] == 'waiting'
                and communication_dict['designated_author'] == 'gui'
                and communication_dict['serial_values']
            ):
                unpause_dict = {
                    'plot_serial_data': False,
                    'gui': 'waiting',
                    'backend': 'requested',
                    'designated_author': 'backend'
                }
                write_and_wait_function(unpause_dict, communication_dict, 'process has requested and is waiting for the gui to plot the serial data!')
                communication_dict = read_communication_file()

            if communication_dict['exit_gui']:
                break
            else:
                communication_dict['serial_values'] = []
                communication_dict['update_gui_plots'] = False
                communication_dict['generate_gui_plots'] = False
                communication_dict['validate_port_settings'] = False
                communication_dict['obtain_serial_data'] = False
                communication_dict['plot_serial_data'] = False
                communication_dict['update_config_to_json'] = False
                communication_dict['skip_to_beginning'] = False
                communication_dict['gui'] = 'waiting'
                communication_dict['backend'] = 'requested'
                communication_dict['designated_author'] = 'backend'
            write_communication_file(communication_dict)
        return termination_event.set()

    def update_gui_plots(self, communication_dict: dict, config: configuration):
        print('process has begun updating gui plots!')
        plot_dict = dict_methods.list_to_dict(communication_dict['plot_dict'])
        plots = config.plots
        matching_plots = False
        if not plots:
            communication_dict['update_gui_plots'] = False
            communication_dict['skip_to_beginning'] = True
            communication_dict['running'] = False
            print('no plots were detected in the config!')
            return
        elif not plot_dict:
            communication_dict['gui'] = 'requested'
            communication_dict['generate_gui_plots'] = True
            communication_dict['update_gui_plots'] = False
            communication_dict['designated_author'] = 'gui'
            communication_dict['backend'] = 'waiting'
            return
        dict_plot_objs = [plot_key for plot_key in plot_dict]
        matching_plots = Counter(dict_plot_objs) == Counter(plots)
        if matching_plots:
            matching_plots = all(next((True for plot_key, ax_line_list in plot_dict.items() if plot_key == plot_obj and Counter(ax_line_list) == Counter(plot_obj.lines)), False) for plot_obj in plots)
        if not matching_plots:
            communication_dict['gui'] = 'requested'
            communication_dict['generate_gui_plots'] = True
            communication_dict['update_gui_plots'] = False
            communication_dict['designated_author'] = 'gui'
            communication_dict['backend'] = 'waiting'
            return
        elif communication_dict['running']:
            communication_dict['update_gui_plots'] = False
            communication_dict['validate_port_settings'] = True
            return
        else:
            communication_dict['update_gui_plots'] = False
            communication_dict['skip_to_beginning'] = True
            communication_dict['running'] = False
            print('process couldnt update gui plots!')
            return

    def validate_port_settings(self, communication_dict: dict, config: configuration):
        print('process has begun validating port settings!')
        com_port = f"COM{config.com_port}"
        baud_rate = config.baud_rate
        if not com_port in self.port_names:
            if isinstance(self.serial_com, serial.Serial) and self.serial_com.is_open:
                self.serial_com.close()
            error_message = f"The port {com_port} does not exist!"
            error_title = "COM Port Not Found"
            error_function(error_message, error_title, com_port=com_port)
            communication_dict['running'] = False
            communication_dict['skip_to_beginning'] = True
            communication_dict['validate_port_settings'] = False
            return
        if not isinstance(self.serial_com, serial.Serial):
            try:
                print('process is trying to create the serial com')
                self.serial_com = serial.Serial(com_port, baud_rate)
            except:
                error_message = f"Either the port {com_port} is unavaliable or the baud rate {baud_rate} is incorrect!"
                error_title = "Unavailable COM Port or Incorrect Baud Rate"
                error_function(error_message, error_title, com_port=com_port, baud_rate=baud_rate)
                communication_dict['running'] = False
                communication_dict['skip_to_beginning'] = True
                communication_dict['validate_port_settings'] = False
                return
            if not self.valid_port:
                self.serial_com.setDTR(False)
                time.sleep(1)
                self.serial_com.flushInput()
                self.serial_com.setDTR(True)
                self.valid_port = True
            communication_dict['obtain_serial_data'] = True
            communication_dict['validate_port_settings'] = False
            print('process has validated port settings!')
            return
        else:
            error_message = "Mismatched serial class!"
            error_title = "Mismatched Serial Class"
            error_function(error_message, error_title)
            self.valid_port = False            
            communication_dict['running'] = False
            communication_dict['skip_to_beginning'] = True
            communication_dict['validate_port_settings'] = False
            return

    def obtain_serial_data(self, communication_dict: dict):
        print('process has begun to obtain serial data!')
        try:
            serial_bytes = self.serial_com.readline()
            decoded_bytes = serial_bytes.decode("utf-8").strip('\r\n')
            serial_values = decoded_bytes.split(',')
            communication_dict['serial_values'] = serial_values
            communication_dict['gui'] = 'requested'
            communication_dict['plot_serial_data'] = True
            communication_dict['backend'] = 'waiting'
            communication_dict['obtain_serial_data'] = False
            communication_dict['designated_author'] = 'gui'
            print('process has successfully obtained serial values!')
            return
        except:
            communication_dict['skip_to_beginning'] = True
            communication_dict['obtain_serial_data'] = False
            print('process failed to get serial values!')
            return

def process_is_finished():
    return True

def write_and_wait_function(unpause_dict: dict, communication_dict: dict, my_message: str = None):
    communication_keys = [key for key in communication_dict]
    write_communication_file(communication_dict)
    print(my_message)
    while True:
        test_communication_dict = read_communication_file()
        if all(key in test_communication_dict for key in communication_keys):
            comparison_dict = {key: test_communication_dict[key] for key in unpause_dict if key in test_communication_dict}
            if all(unpause_dict[key] == comparison_dict[key] for key in unpause_dict):
                break
        time.sleep(0.01)
    print('process has finished waiting for gui!')
    return

def config_from_json():
    try:
        with open(CURRENT_CONFIG, "r") as file:
            config = json.load(file)
            return configuration.from_dict(config)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    
def write_communication_file(backend_to_gui_dict: dict):
    with open(COMMUNICATION, "w") as file:
        json.dump(backend_to_gui_dict, file, indent=4)
        return

def read_communication_file():
    try:
        with open(COMMUNICATION, "r") as file:
            gui_to_backend_dict = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        gui_to_backend_dict = {}
    return gui_to_backend_dict

def error_function(error_message :str, error_title: str, **kwargs):
    from warning_window import error_window
    error_win = error_window(error_message, error_title, **kwargs)
    error_win.mainloop()