import customtkinter as ctk
from configuration import configuration, configurations
from data_manager import save_configurations
from file_manager import icon_path

class createConfigurationWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Live Serial Reader - Create New Configuration")
        self.geometry("450x150")
        self.resizable(False, False)

        self.iconbitmap(icon_path)

        self.grid_columnconfigure(0, weight=1)

        self.entryBox = ctk.CTkEntry(self, placeholder_text="Enter a configuration name...")
        self.entryBox.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.entryBox.bind("<Return>", self.updateConfigs)

        self.cancelButton = ctk.CTkButton(self, text="Cancel", anchor='e', command=self.openMainMenu)
        self.cancelButton.grid(row=1, padx=20, pady=10)

    def openMainMenu(self):
        self.destroy()
        open_menu_window()

    def updateConfigs(self, event=None):
        entryText = self.entryBox.get()
        duplicate = False

        for config in configurations:
            if entryText == config.configuration_name:
                error_message = "The configuration enetered already exists:\n\n\"{newConfigName}\""
                error_title = "Duplicate Configuration Names"
                self.openDuplicateConfigWarning(error_message, error_title, entryText)
        
        if duplicate == False:
            configuration(entryText, [], [], 0, 0, "No File", [])
            save_configurations(configurations)
            self.openConfiguration(entryText)

    def openDuplicateConfigWarning(self, newConfigName):
        open_duplicate_warning_window(newConfigName)
        self.destroy()

    def openConfiguration(self, configName):
        self.destroy()
        open_configuration_window(configName)

def open_duplicate_warning_window(error_message, error_title, newConfigName):
    from warning_window import error_window
    error_win = error_window(error_message, error_title, newConfigName=newConfigName)
    error_win.mainloop()
    
def open_configuration_window(configName):
    from configuration_window import configurationWindow
    config_win = configurationWindow(configName)
    config_win.mainloop()

def open_menu_window():
    from menu_window import menuWindow
    menu_win = menuWindow()
    menu_win.mainloop()