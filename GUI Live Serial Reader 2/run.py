import time
import serial
#import threading
from smart_thread import smart_thread
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING
from serial.tools import list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from configuration import configuration
from collections import Counter

if TYPE_CHECKING:
    from configuration_window import configurationWindow

class run_plots:
    def __init__(self, ctk_window: 'configurationWindow', config: configuration):
        self.ctk_window = ctk_window
        self.config = config
        self.port_objs = list_ports.comports()
        self.port_names = [port.device for port in self.port_objs]
        self.plot_dict = {}
        self.serial_com = None
        self.valid_port = False
        self.port_validation_thread = smart_thread(target=self.validate_port_settings, daemon=True)
        self.serial_data_collection_thread = smart_thread(target=self.obtain_serial_data, daemon=True)
        self.update_plot_thread = smart_thread(target=self.update_gui_plots, daemon=True)
    
    def start(self):
        self.start_threading()
        self.ctk_window.start_gui_plot_cycle()
        return

    def start_threading(self):
        self.port_validation_thread.start()
        self.serial_data_collection_thread.start()
        self.update_plot_thread.start()
        return

    def validate_port_settings(self):
        com_port = f'COM{self.config.com_port}'
        baud_rate = self.config.baud_rate
        if com_port not in self.port_names:
            if isinstance(self.serial_com, serial.Serial) and self.serial_com.is_open:
                self.serial_com.close()
            error_message = f"The port {com_port} does not exist!"
            error_title = "COM Port Not Found"
            error_function(error_message, error_title, com_port=com_port)
            self.ctk_window.running = False
            self.valid_port = False
            self.ctk_window.start_gui_plot_cycle()
            return
        if not isinstance(self.serial_com, serial.Serial):
            try:
                self.serial_com = serial.Serial(com_port, baud_rate)
            except:
                error_message = f"Either the port {com_port} is unavaliable or the baud rate {baud_rate} is incorrect!"
                error_title = "Unavailable COM Port or Incorrect Baud Rate"
                error_function(error_message, error_title, com_port=com_port, baud_rate=baud_rate)
                self.ctk_window.running = False
                self.valid_port = False
                self.ctk_window.start_gui_plot_cycle()
                return
        if isinstance(self.serial_com, serial.Serial):                                                                   
            if not self.valid_port:
                self.serial_com.setDTR(False)
                time.sleep(1)
                self.serial_com.flushInput()
                self.serial_com.setDTR(True)
                self.valid_port = True
            self.obtain_serial_data()
            return
        else:
            error_message = "Mismatched serial class!"
            error_title = "Mismatched Serial Class"
            error_function(error_message, error_title)
            self.valid_port = False
            self.ctk_window.start_gui_plot_cycle()
            return

    def obtain_serial_data(self):
        serial_variables = self.config.serial_variables
        try:
            serial_bytes = self.serial_com.readline()
            decoded_bytes = serial_bytes.decode("utf-8").strip('\r\n')
            values = decoded_bytes.split(",")
            self.ctk_window.plot_serial_data(values)
            return
        except:
            self.ctk_window.start_gui_plot_cycle()
            return

    def update_gui_plots(self):
        plots = self.config.plots
        matching_plots = False
        if not plots:
            self.ctk_window.start_gui_plot_cycle()
            return
        if not self.plot_dict:
            self.ctk_window.generate_gui_plots()
            return
        dict_plot_objs = [plot_key for plot_key in self.plot_dict]
        matching_plots = Counter(dict_plot_objs) == Counter(plots)
        if matching_plots:
            matching_plots = all(next((True for plot_key, (_, _, ax) in self.plot_dict.items() if plot_key == plot_obj and Counter(list(ax.get_lines())) == Counter(plot_obj.lines)), False) for plot_obj in plots)
        if not matching_plots:
            self.ctk_window.generate_gui_plots()
            return
        elif self.ctk_window.running:
            self.validate_port_settings()
            return
        else:
            self.ctk_window.start_gui_plot_cycle()
            return

def error_function(error_message :str, error_title: str, **kwargs):
    from warning_window import error_window
    error_win = error_window(error_message, error_title, **kwargs)
    error_win.mainloop()