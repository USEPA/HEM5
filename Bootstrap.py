import queue
from Hem4Gui_Threaded import Hem4

"""
Create the application and start it up.
"""
messageQueue = queue.Queue()
hem4 = Hem4(messageQueue)
hem4.start_gui()