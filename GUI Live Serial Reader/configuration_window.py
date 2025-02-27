import customtkinter as ctk
import tkinter as tk
from configuration import configuration, configurations
from configuration_manager import save_configurations
from create_configuration_window import open_duplicate_warning_window

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class configurationWindow(ctk.CTk):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.title(f"Live Serial Reader - {self.name}")
        self.geometry("700x450")
        self.resizable(True, True)
        self.iconbitmap("Resources/serial_port_icon_blue.ico")

        # Obtain config
        current_config = self.getConfiguration(self.name)

        # Create menubar
        menubar = tk.Menu(self)

        # Add file menu and commands
        file = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file)
        file.add_command(label="Rename Configuration", command=lambda: self.entry_popup(self.rename_configuration))
        file.add_command(label="Save", command=lambda: save_configurations(configurations))
        file.add_command(label="Delete", command=lambda: self.delete_configuration(current_config))
        file.add_command(label="Exit to Menu", command=self.openMenu)

        # Add serial variables menu and commands
        serial_variables = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Serial Variables", menu=serial_variables)
        serial_variables.add_command(label="Add Variables", command=lambda: self.addSerialVariables(current_config))
        serial_variables.add_command(label="Edit Variables", command=lambda: self.editSerialVariables(current_config))
        serial_variables.add_command(label="Delete Variables", command=None)

        # Add lines menu and commands
        lines = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Lines", menu=lines)
        lines.add_command(label="Add Lines", command=None)
        lines.add_command(label="Edit Lines", command=None)
        lines.add_command(label="Delete Lines", command=None)
        
        # Add plots menu and commands
        plots = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Plots", menu=plots)
        plots.add_command(label="Add Plots", command=None)
        plots.add_command(label="Edit Plots", command=None)
        plots.add_command(label="Merge Plots", command=None)
        plots.add_command(label="Delete Plots")

        # Add baud rate menu and commands
        baud = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Baud Rate", menu=baud)
        baud.add_command(label="Edit Baud Rate", command=None)

        # Add COM port menu and commands
        com_port = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="COM Port", menu=com_port)
        com_port.add_command(label="Edit COM Port", command=None)

        # Add CSV file menu and commands
        csv = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="CSV File", menu=csv)
        csv.add_command(label="Choose CSV File", command=None)

        # Add other settings menu and commands
        other_settings = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Other Settings", menu=other_settings)
        other_settings.add_command(label="Edit Serial Delimiter", command=None)

        self.config(menu=menubar)

    def entry_popup(self, func):
        """ General use popup for entire window's menu bar """
        entry_popup = tk.Entry(self)
        entry_popup.place(x=self.winfo_pointerx() - self.winfo_rootx(), y=self.winfo_pointery() - self.winfo_rooty(), width=100, height=20)
        entry_popup.focus_set()
        entry_popup.bind("<Return>", lambda event: self.pass_entry_popup(entry_popup, func))
        entry_popup.bind("<Escape>", lambda event: entry_popup.destroy())

    def pass_entry_popup(self, tk_entry_widget, func):
        """ Passes popup entry to a function """
        entry = tk_entry_widget.get()
        func(entry)
        tk_entry_widget.destroy()

    def rename_configuration(self, new_name, current_config):
        old_name = current_config.configuration_name
        valid_name = True

        for config in configurations:
            if new_name == config.configuration_name:
                valid_name = False

        if new_name == old_name:
            valid_name = True

        if valid_name == False:
            open_duplicate_warning_window(new_name)
            return

        for config in configurations:
            if old_name == config.configuration_name and valid_name == True:
                config.configuration_name = new_name
                self.name = new_name

        self.title(f"Live Serial Reader - {self.name}")
        save_configurations(configurations)
           
    def openMenu(self):
        self.destroy()
        open_menu_window()

    def getConfiguration(self, name):
        for config in configurations:
            if name == config.configuration_name:
                current_config = config
        return current_config

    def delete_configuration(self, config):
        """ Deletes configuration object from JSON file """
        for config_object in configurations:
            if config_object.configuration_name == config.configuration_name:
                configurations.remove(config_object)
        save_configurations(configurations)
        self.openMenu()

    def addSerialVariables(self, current_config):
        open_add_serial_variables_window(current_config)

    def editSerialVariables(self, current_config):
        open_edit_serial_variables_window(current_config)

def open_menu_window():
    from menu_window import menuWindow
    menu_win = menuWindow()
    menu_win.mainloop()

def open_add_serial_variables_window(current_config):
    from serial_variables import add_serial_variable
    add_serial_var_window = add_serial_variable(current_config)
    add_serial_var_window.mainloop()

def open_edit_serial_variables_window(current_config):
    from serial_variables import edit_serial_variables_list
    edit_serial_var_window = edit_serial_variables_list(current_config)
    edit_serial_var_window.mainloop()