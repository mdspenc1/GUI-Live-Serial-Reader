import time
import serial
#import threading
from multiprocessing import Process
from smart_thread import smart_thread
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING
from serial.tools import list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from configuration import configuration
from collections import Counter
import asyncio

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
    
    def start(self):
        asyncio.create_task(self.ctk_window.start_gui_plot_cycle())
        return

    async def validate_port_settings(self):
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
            asyncio.create_task(self.ctk_window.start_gui_plot_cycle())
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
                asyncio.create_task(self.ctk_window.start_gui_plot_cycle())
                return
        if isinstance(self.serial_com, serial.Serial):                                                                   
            if not self.valid_port:
                self.serial_com.setDTR(False)
                time.sleep(1)
                self.serial_com.flushInput()
                self.serial_com.setDTR(True)
                self.valid_port = True
            asyncio.create_task(self.obtain_serial_data())
            return
        else:
            error_message = "Mismatched serial class!"
            error_title = "Mismatched Serial Class"
            error_function(error_message, error_title)
            self.valid_port = False
            asyncio.create_task(self.ctk_window.start_gui_plot_cycle())
            return

    async def obtain_serial_data(self):
        serial_variables = self.config.serial_variables
        try:
            serial_bytes = self.serial_com.readline()
            decoded_bytes = serial_bytes.decode("utf-8").strip('\r\n')
            values = decoded_bytes.split(",")
            asyncio.create_task(self.ctk_window.plot_serial_data(values))
            return
        except:
            asyncio.create_task(self.ctk_window.start_gui_plot_cycle())
            return

    async def update_gui_plots(self):
        plots = self.config.plots
        matching_plots = False
        if not plots:
            asyncio.create_task(self.ctk_window.start_gui_plot_cycle())
            return
        if not self.plot_dict:
            asyncio.create_task(self.ctk_window.generate_gui_plots())
            return
        dict_plot_objs = [plot_key for plot_key in self.plot_dict]
        matching_plots = Counter(dict_plot_objs) == Counter(plots)
        if matching_plots:
            matching_plots = all(next((True for plot_key, (_, _, ax) in self.plot_dict.items() if plot_key == plot_obj and Counter(list(ax.get_lines())) == Counter(plot_obj.lines)), False) for plot_obj in plots)
        if not matching_plots:
            asyncio.create_task(self.ctk_window.generate_gui_plots())
            return
        elif self.ctk_window.running:
            asyncio.create_task(self.validate_port_settings())
            return
        else:
            asyncio.create_task(self.ctk_window.start_gui_plot_cycle())
            return

def error_function(error_message :str, error_title: str, **kwargs):
    from warning_window import error_window
    error_win = error_window(error_message, error_title, **kwargs)
    error_win.mainloop()