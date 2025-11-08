import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def buildHeader(parent, title="Panel IoT UMES", subtitle=None, logo_path=None):

    frame = ttk.Frame(parent)
    frame.pack(fill="x", padx=10, pady=(10,5))

    left = ttk.Frame(frame)
    left.pack(side="left", anchor="w")

    lbl_title = ttk.Label(left, text=title, font=("Segoe UI", 16, "bold"))
    lbl_title.pack(anchor="w")
    if subtitle:
        lbl_sub = ttk.Label(left, text=subtitle, font=("Segoe UI", 9))
        lbl_sub.pack(anchor="w")

    if logo_path:
        try:
            img = ttk.PhotoImage(file=logo_path)
            lbl_logo = ttk.Label(frame, image=img)
            lbl_logo.image = img
            lbl_logo.pack(side="right")
        except Exception:
            pass

    return frame
    