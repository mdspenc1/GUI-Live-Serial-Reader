import customtkinter as ctk
from MenuWindow import MenuWindow

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("custom-dark")

class App:
    def __init__(self):
        self.master = ctk.CTk()
        self.master.title("Live Serial Reader")
        self.master.geometry("400x300")
        self.master.resizable(True, True)

        #Mechanism to Switch Windows
        self.current_window = None

        #Start with Menu Window
        self.switch_window(MenuWindow(self.master))

    def switch_window(self, new_window):
        if self.current_window:
            self.current_window.frame.destroy()

        self.current_window = new_window

    def run(self):
        self.master.mainloop()

if __name__ == "__Main__":
    app = App()
    app.run()