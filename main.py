import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from views.homePage import HomePage
import os

APP_TITLE = "Panel IoT UMES"

def main():
    
    root = ttk.Window(title=APP_TITLE, themename="solar")
    root.geometry("980x640")
    root.minsize(800, 500)

    icon_path = os.path.join("assets", "icon.png")
    if os.path.exists(icon_path):
        try:
            root.iconphoto(False, ttk.PhotoImage(file=icon_path))
        except Exception:
            pass

    HomePage(root)
    root.mainloop()

if __name__ == "__main__":
    main()
