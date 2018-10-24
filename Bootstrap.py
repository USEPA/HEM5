import queue
from Hem4Gui_Threaded import Hem4

"""
Create the application and start it up.
"""
messageQueue = queue.Queue()
callbackQueue = queue.Queue()
hem4 = Hem4(messageQueue, callbackQueue)
hem4.start_gui()