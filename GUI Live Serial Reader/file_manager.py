import os

global script_dir
script_dir = os.path.dirname(os.path.abspath(__file__))
global icon_path
icon_path = os.path.join(script_dir, "Resoruces", "serial_port_icon_blue.ico")
global error_icon_path
error_icon_path = os.path.join(script_dir, "Resoruces", "error_icon.png")
global CONFIG_FILE
CONFIG_FILE = os.path.join(script_dir, "configuration.json")