#tkDirSelector.py
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
folder_path = filedialog.askdirectory()
if folder_path:
    print(folder_path)
    root.destroy()
else:
    print("no folder selected")
    root.destroy()

root.mainloop()