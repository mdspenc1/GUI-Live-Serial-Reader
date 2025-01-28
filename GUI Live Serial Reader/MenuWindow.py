import customtkinter as ctk
from tkinter import *

class MenuWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Live Serial Reader - Main Menu")

        #Create Search Box
        self.master.entry = ctk.CTkEntry(self, width=250, placeholder_text="Search for configuration...")
        self.master.entry.pack(pady=20)

        #Create List Box
        self.master.list = Listbox(self, width=250)
        self.master.list.pack(pady=40)

        #List of Class Objects
        configurations = []

        #Add configurations to list
        update(configurations)

    def update(self, master, data):
        #Clear Listbox
        self.master.list.delete(0, END)
        