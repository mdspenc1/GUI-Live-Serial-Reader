import os
from resource_manager import script_dir
mpl_config_win_gui = os.path.join(script_dir, 'mpl_config_win_gui')
os.environ['MPLCONFIGDIR'] = mpl_config_win_gui
import customtkinter as ctk
import tkinter as tk
import warnings
#warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
import matplotlib.pyplot as plt
from tkinter import scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from configuration import configurations
from data_manager import save_configurations, find_file
from input_check import int_check
from run import run_plots
from resource_manager import icon_path
import csv
from configuration import configuration

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

global csv_path
csv_path = ''

class configurationWindow(ctk.CTk):
    def __init__(self, name):
        # Define window appearance and behavior
        super().__init__()
        self.name = name
        self.title(f"Live Serial Reader - {self.name}")
        self.geometry("700x450")
        self.resizable(True, True)
        self.iconbitmap(icon_path)
        # self.event_loop = asyncio.get_event_loop()
        # print(self.event_loop)

        # Obtain config
        self.current_config = self.getConfiguration(self.name)

        # Running bool for live plotting
        self.running = False

        # Create menubar
        menubar = tk.Menu(self)

        # Add file menu and commands
        file = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file)
        file.add_command(label="Rename Configuration", command=lambda: self.entry_popup(self.rename_configuration, self.current_config))
        file.add_command(label="Save", command=lambda: save_configurations(configurations))
        file.add_command(label="Delete", command=lambda: self.delete_configuration(self.current_config))
        file.add_command(label="Exit to Menu", command=lambda: open_menu_window(self, self.run_module))

        # Add serial variables menu and commands
        serial_variables = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Serial Variables", menu=serial_variables)
        serial_variables.add_command(label="Add Variables", command=lambda: open_add_serial_variables_window(self.current_config))
        serial_variables.add_command(label="Edit Variables", command=lambda: open_edit_serial_variables_window(self.current_config))
        serial_variables.add_command(label="Delete Variables", command=lambda: open_delete_serial_variables_window(self.current_config))

        # Add lines menu and commands
        lines = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Lines", menu=lines)
        lines.add_command(label="Add Lines", command=lambda: open_add_basic_lines_window(self.current_config))
        lines.add_command(label="Edit Lines", command=lambda: open_edit_basic_lines_window(self.current_config))
        lines.add_command(label="Delete Lines", command=lambda: open_delete_lines_window(self.current_config))
        
        # Add plots menu and commands
        plots = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Plots", menu=plots)
        plots.add_command(label="Add Plots", command=lambda: open_add_plot_window(self.current_config))
        plots.add_command(label="Edit Plots", command=lambda: open_edit_plot_window(self.current_config))
        plots.add_command(label="Delete Plots", command=lambda: open_delete_plot_window(self.current_config))

        # Add baud rate menu and commands
        baud = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Baud Rate", menu=baud)
        baud.add_command(label="Edit Baud Rate", command=lambda: self.entry_popup(self.edit_baud, self.current_config))

        # Add COM port menu and commands
        com_port = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="COM Port", menu=com_port)
        com_port.add_command(label="Edit COM Port", command=lambda: self.entry_popup(self.edit_com, self.current_config))

        # Add CSV file menu and commands
        csv = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="CSV File", menu=csv)
        csv.add_command(label="Choose CSV File", command=lambda: self.entry_popup(self.edit_csv, self.current_config))

        # Add other settings menu and commands
        other_settings = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Other Settings", menu=other_settings)
        #other_settings.add_command(label="Edit Serial Delimiter", command=None)
        other_settings.add_command(label="View Configuration Details", command=lambda: self.view_config_settings(self.current_config))
        other_settings.add_command(label="Help", command=self.help)

        # Add run button to menubar
        run_list = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="RUN!", menu=run_list)
        run_list.add_command(label="RUN!", command=lambda: setattr(self, "running", True))
        run_list.add_command(label="STOP!", command=lambda: setattr(self, "running", False))
        run_list.add_command(label="Toggle CSV Data Recording", command=None)

        self.config(menu=menubar)
        self.run_module = run_plots(self, self.current_config)
        self.run_module.start()

    def start_gui_plot_cycle(self):
        # print('Beginning gui plot cycle!')
        self.after(1, lambda: self.run_module.update_gui_plots())
        return

    def plot_serial_data(self, values):
        print('Attempting to plot data!')
        try:
            value_index = 0
            for value_index in range(len(values)):
                for serial_var in self.current_config.serial_variables:
                    if serial_var.variable_number == value_index:
                        serial_var.data_array.append(float(values[value_index].strip()))
            print('Serial variable data arrays have been populated!')
            for plot_key, (canvas, fig, ax) in self.run_module.plot_dict.items():
                for line_obj in list(ax.get_lines()):
                    line_obj.update_line()

                ax.relim()
                ax.autoscale()

                canvas.draw()
                canvas_widget = canvas.get_tk_widget()
                canvas_widget.grid(row=plot_key.plot_position[0], column=plot_key.plot_position[1], sticky="nsew")
                self.grid_rowconfigure(plot_key.plot_position[0], weight=1)
                self.grid_columnconfigure(plot_key.plot_position[1], weight=1)
            print('Data has been plotted!')
            self.start_gui_plot_cycle()
            return
        except:
            print('Failed to plot data!')
            self.start_gui_plot_cycle()
            return

    def generate_gui_plots(self):
        print('Generating gui plots!')
        plots = self.current_config.plots
        for (canvas, fig, ax) in self.run_module.plot_dict.values():
            plt.close(fig)
            ax.get_lines().clear()
        self.run_module.plot_dict = {}
        for plot_obj in plots:
            fig, ax = plt.subplots()

            ax.set_title(plot_obj.plot_title)
            ax.set_xlabel(plot_obj.x_label)
            ax.set_ylabel(plot_obj.y_label)
            ax.yaxis.set_label_position("right")
            ax.yaxis.tick_right()
            ax.grid()

            for line_obj in plot_obj.lines:
                ax.add_line(line_obj.duplicate())

            ax.legend(loc=plot_obj.legend_position)
            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            fig.tight_layout()
            fig.subplots_adjust(right=0.75, bottom=0.25, top=0.85)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.grid(row=plot_obj.plot_position[0], column=plot_obj.plot_position[1], sticky="nsew")
            self.grid_rowconfigure(plot_obj.plot_position[0], weight=1)
            self.grid_columnconfigure(plot_obj.plot_position[1], weight=1)

            self.run_module.plot_dict[plot_obj] = (canvas, fig, ax)
        print('Plot dictionary has been updated!')
        self.run_module.update_gui_plots()
        return

    def entry_popup(self, func, current_config):
        """ General use popup for entire window's menu bar """
        entry_popup = tk.Entry(self)
        entry_popup.place(x=self.winfo_pointerx() - self.winfo_rootx(), y=self.winfo_pointery() - self.winfo_rooty(), width=100, height=20)
        entry_popup.focus_set()
        entry_popup.bind("<Return>", lambda event: self.pass_entry_popup(entry_popup, func, current_config))
        entry_popup.bind("<Escape>", lambda event: entry_popup.destroy())

    def pass_entry_popup(self, tk_entry_widget, func, current_config):
        """ Passes popup entry to a function """
        entry = tk_entry_widget.get()
        func(entry, current_config)
        tk_entry_widget.destroy()

    def edit_csv(self, csv_name, current_config):
        valid_csv = True
        if any(char in csv_name for char in r""":"'/\*?|!@$%^&""") or csv_name.count(".") > 1 or csv_name[-4:] != '.csv' or csv_name == '':
            valid_csv = False
        
        if valid_csv:
            csv_path = find_file(csv_name)
        else:
            error_message = f'The CSV file {csv_name} is invalid!'
            error_title = "CSV File Error"
            error_function(error_message, error_title, csv_name=csv_name)

        if csv_path is None:
            error_message = f"The CSV file {csv_name} doesn't exist!"
            error_title = "CSV File Error"
            error_function(error_message, error_title, csv_name=csv_name)
        else:
            current_config.csv_file = csv_name

    def edit_baud(self, new_baud, current_config):
        valid_baud = int_check(new_baud)
        if not valid_baud:
            valid_baud = False
        elif valid_baud:
            current_config.baud_rate = new_baud
        else:
            error_message = f"The baud rate {new_baud} is invalid!"
            error_title = "Invalid Baud Rate"
            error_function(error_message, error_title, new_baud=new_baud)

    def edit_com(self, new_com, current_config):
        valid_port = int_check(new_com)
        if not valid_port:
            valid_port = False
        elif valid_port:
            current_config.com_port = new_com
        else:
            error_message = f"The COM port {new_com} is invalid!"
            error_title = "Invalid COM Port"
            error_function(error_message, error_title, new_com=new_com)

    def rename_configuration(self, new_name, current_config):
        old_name = current_config.configuration_name
        valid_name = True

        for config in configurations:
            if new_name == config.configuration_name:
                valid_name = False

        if new_name == old_name:
            valid_name = True

        if not valid_name:
            error_message = f'The configuration enetered already exists:\n\n"{new_name}"'
            error_title = "Duplicate Configuration Names"
            error_function(error_message, error_title, new_name=new_name)
            return

        for config in configurations:
            if old_name == config.configuration_name and valid_name == True:
                config.configuration_name = new_name
                self.name = new_name

        self.title(f"Live Serial Reader - {self.name}")
        save_configurations(configurations)

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
        open_menu_window(self)

    def view_config_settings(self, current_config):
        self.settings_window = config_settings(current_config)
        self.settings_window.mainloop()

    def help(self):
        self.help_win = help_window()
        self.help_win.mainloop()

class help_window(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Live Serial Reader - Help Window")
        self.resizable(True, True)
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15, width=50)
        with open("Resources/Help.txt", "r") as file:
            content = file.read()
        self.text_area.insert(tk.END, content)
        self.text_area.config(state=tk.DISABLED)

class config_settings(tk.Toplevel):
    def __init__(self, current_config):
        super().__init__()
        self.title("Live Serial Reader - Config Settings")
        self.resizable(False, False)

        self.config_name = tk.Label(self, text=f"Config Name: {current_config.configuration_name}")
        self.config_name.grid(row=0, column=0)
        
        self.config_baud = tk.Label(self, text=f"Baud Rate: {current_config.baud_rate}")
        self.config_baud.grid(row=1, column=0)

        self.config_com = tk.Label(self, text=f"COM Port: {current_config.com_port}")
        self.config_com.grid(row=2, column=0)

        self.config_csv = tk.Label(self, text=f"CSV File: {current_config.csv_file}")
        self.config_csv.grid(row=3, column=0)

def open_add_serial_variables_window(current_config):
    from serial_variables import add_serial_variable
    add_serial_var_window = add_serial_variable(current_config)
    add_serial_var_window.mainloop()

def open_edit_serial_variables_window(current_config):
    from serial_variables import edit_serial_variables_list
    edit_serial_var_window = edit_serial_variables_list(current_config)
    edit_serial_var_window.mainloop()

def open_delete_serial_variables_window(current_config):
    from serial_variables import delete_serial_variables
    delete_serial_var_window = delete_serial_variables(current_config)
    delete_serial_var_window.mainloop()

def open_add_basic_lines_window(current_config):
    from lines import add_basic_line
    add_basic_line_window = add_basic_line(current_config)
    add_basic_line_window.mainloop()

def open_edit_basic_lines_window(current_config):
    from lines import edit_basic_line_list
    edit_basic_line_window = edit_basic_line_list(current_config)
    edit_basic_line_window.mainloop()

def open_delete_lines_window(current_config):
    from lines import delete_lines
    delete_lines_window = delete_lines(current_config)
    delete_lines_window.mainloop()

def open_add_plot_window(current_config):
    from plots import add_plots
    add_plot_win = add_plots(current_config)
    add_plot_win.mainloop()

def open_edit_plot_window(current_config):
    from plots import edit_plots_list
    edit_plot_win = edit_plots_list(current_config)
    edit_plot_win.mainloop()

def open_delete_plot_window(current_config):
    from plots import delete_plot_list
    delete_plot_win = delete_plot_list(current_config)
    delete_plot_win.mainloop()

def open_menu_window(current_win: configurationWindow, run_module: run_plots):
    from menu_window import menuWindow
    run_module.stop_threading()
    current_win.withdraw()
    current_win.after(250, lambda: current_win.destroy)
    menu_win = menuWindow()
    menu_win.mainloop()

def error_function(error_message :str, error_title: str, **kwargs):
    from warning_window import error_window
    error_win = error_window(error_message, error_title, **kwargs)
    error_win.mainloop()

# def initialize_processes(config: configuration):
#     if __name__ == "__main__":
#         ctk_window = configurationWindow(config.configuration_name)
#         ctk_window.create_processes()