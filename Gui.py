"""
Gui.py:
This gui module starts the HEM4 application and is located in the root directory of the repository 
(HEM4) to accommodate how Pyinstaller wants the directory structure to be ordered. All other gui modules are
located in HEM4/com/sca/hem4/gui. Pyinstaller wants the initial module to be located in the root.
"""
import tkinter as tk
from com.sca.hem4.gui.MainView import MainView


def on_closing(hem):
    
    if hem.running == True:
    
            hem.quit_app()
            if hem.aborted == True:
                root.destroy()
                
    else:
        root.destroy()


# infinite loop which is required to 
# run tkinter program infinitely 
# until an interrupt occurs
if __name__ == "__main__":
    root = tk.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='images/HEM_arial.png'))
    root.title("")

    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(main.hem))
    #Testing
#    root.geometry("1000x800")
    #End testing
    root.wm_minsize(1000,800)
    root.mainloop()
