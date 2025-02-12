import customtkinter as ctk
from tkinter import *
from tkinter.ttk import *
from configuration import configuration, configurations

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class configurationWindow(ctk.CTk):
    def __init__(self, name):
        super().__init__()

        self.title(f"Live Serial Reader - {name}")
        self.geometry("700x450")
        self.resizable(True, True)

        self.iconbitmap("Resources/serial_port_icon_blue.ico")

        # Create menubar
        menubar = Menu(self)

        # Add file menu and commands
        file = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file)
        file.add_command(label="Rename Configuration", command=None)
        file.add_command(label="Save", command=None)
        file.add_command(label="Undo", command=None)
        file.add_command(label="Redo", command=None)
        file.add_command(label="Delete", command=None)
        file.add_command(label="Exit to Menu", command=None)

        # Add serial variables menu and commands
        serial_variables = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Serial Variables", menu=serial_variables)
        serial_variables.add_command(label="Add Variables", command=None)
        serial_variables.add_command(label="Edit Variables", command=None)
        serial_variables.add_command(label="Delete Variables", command=None)

        # Add lines menu and commands
        lines = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Lines", menu=lines)
        lines.add_command(label="Add Lines", command=None)
        lines.add_command(label="Edit Lines", command=None)
        lines.add_command(label="Delete Lines", command=None)
        
        # Add plots menu and commands
        plots = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Plots", menu=plots)
        plots.add_command(label="Add Plots", command=None)
        plots.add_command(label="Edit Plots", command=None)
        plots.add_command(label="Merge Plots", command=None)
        plots.add_command(label="Delete Plots")

        # Add baud rate menu and commands
        baud = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Baud Rate", menu=baud)
        baud.add_command(label="Edit Baud Rate", command=None)

        # Add COM port menu and commands
        com_port = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="COM Port", menu=com_port)
        com_port.add_command(label="Edit COM Port", command=None)

        # Add CSV file menu and commands
        csv = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="CSV File", menu=csv)
        csv.add_command(label="Choose CSV File", command=None)

        # Add other settings menu and commands
        other_settings = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Other Settings", menu=other_settings)
        other_settings.add_command(label="Edit Serial Delimiter", command=None)

    def openMenu(self):
        self.destroy()
        open_menu_window()

    def getConfiguration(self, name):
        for config in configurations:
            if name == config.configuration_name:
                current_config = config
        return current_config

def open_menu_window():
    from menu_window import menuWindow
    menu_win = menuWindow()
    menu_win.mainloop()