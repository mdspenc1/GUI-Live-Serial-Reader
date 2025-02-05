import customtkinter as ctk
import tkinter as tk
from configuration import configuration
from configuration import configurations

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class menuWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        global configurations

        self.title("Live Series Reader - Main Menu")
        self.geometry("700x450")
        self.resizable(True, True)

        #Row & Column Configuration
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        #Create Entry Box for Search Bar
        self.entryBox = ctk.CTkEntry(self, placeholder_text="Search for configuration...")
        self.entryBox.grid(fill="x", row=0)

        #Create Header for Results Box
        headers = ["Config Name", "Variables", "Plots", "Baud Rate", "COM Port", "CSV File"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(self, text=header)
            label.grid(row=1, column=col, sticky="ew", fill="x")

        #Creates Self Configuration List to Create Configuration Buttons Later
        self.configs = configurations

        #Initially Populate Scrollable Frame with All Configurations
        self.populateFrame(self.configs)

        #Bind Entry Box to Update Function
        self.entryBox.bind("<KeyRelease>", self.updateFrame)

        #Find Number of Filtered Results
        resultNum = self.resultNumber(self)

        #Create Scroll Frame for Search Results
        self.scrollFrame = ctk.CTkScrollableFrame(self)
        self.scrollFrame.grid(row=2, column=0, rowspan=resultNum+1, fill="x")
    
    def populateFrame(self, configs):
        #Clear Existing Configurations from Scrollable Frame
        for widget in self.scrollFrame.winfo_children():
            widget.destroy()

        #Add Filtered Configurations to Scrollable Frame
        for config in configs:
            name = config.configuration_name
            serialVars = str(config.serial_variables)
            plots = str(config.plots)
            baud = str(config.baud_rate)
            comPort = "COM" + str(config.com_port)
            csvFile = config.csv_file
            configParameters = [name, serialVars, plots, baud, comPort, csvFile]
            configText = " ".join(configParameters)
            button = ctk.CTkButton(self.scrollFrame, text=configText, command=lambda: self.openConfiguration(name))
            button.pack()

    def updateFrame(self, event):
        #Obtain Text in Entry Box as Lowercase
        searchText = self.entryBox.get().lower()
        
        #Filter Configurations Based on Entry
        filteredConfigs = [config for config in self.configs if searchText in config.configuration_name.lower()]

        #Update Scrollable Frame with Filtered Configs
        self.populateFrame(filteredConfigs)

    def resultNumber(self):
        #Obtain Text in Entry Box as Lowercase
        searchText = self.entryBox.get().lower()

        #Filter Configurations Based on Entry
        filteredConfigs = [config for config in self.configs if searchText in config.configuration_name.lower()]

        #Return Number of Filtered Results
        resultNum = len(filteredConfigs)
        return resultNum

    def openConfiguration(self, name):
        self.destroy()
        open_configuration_window(name)

def open_configuration_window(name):
    from configuration_window import configurationWindow
    config_win = configurationWindow(name)
    config_win.mainloop()

if __name__ == "__main__":
    MenuWindow = menuWindow()
    MenuWindow.mainloop()
