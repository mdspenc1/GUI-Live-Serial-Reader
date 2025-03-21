import time
import threading
import serial
from serial.tools import list_ports
import matplotlib.pyplot as plt
from plots import plots, plot
from configuration_window import configurationWindow, run_boole



config = configurationWindow.config
ports = list_ports.comports()
com_port = f"COM{config.com_port}"
serial_com = serial.Serial(com_port, config.baud_rate)