# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 13:44:07 2019

@author: mmorr_000
"""

import tkinter as tk
from pandastable import *
import pandas as pd
import webbrowser

root = tk.Tk()
root.title("HEM 4 Viz Window")

datatypes = {'fips':np.str,'Fips':np.str,'FIPS':np.str,'FIPS + Block':np.str,\
             'block':np.str,'BLOCK':np.str,'Block':np.str,'Src Cat':np.str,\
             'Facility ID':np.str,'Facil_id':np.str,'Facility_id':np.str,'facility_id':np.str,\
             'source_id':np.str,'Source_id':np.str,'SOURCE_ID':np.str,'SRCID':np.str,\
             'FACNAME':np.str,'can_blk':np.str,'resp_blk':np.str,'liver_blk':np.str,\
             'neuro_blk':np.str,'devel_blk':np.str,'repro_blk':np.str,'kidney_blk':np.str,\
             'ocular_blk':np.str,'endo_blk':np.str,'hema_blk':np.str,'immun_blk':np.str,\
             'skel_blk':np.str,'spleen_blk':np.str,'thyroid_blk':np.str,'whole_blk':np.str,\
             'lat':np.float64, 'lon':np.float64}

def browse_button():
    filename = filedialog.askopenfilename(filetypes = [("Excel or csv files","*.xls; *xlsx; *.csv*")])
    if filename.split(".")[-1].lower() in ["xlsx", "xls"]:
        df = pd.read_excel(filename)
    else:
        df = pd.read_csv(filename, dtype=datatypes)
    curr_windo=tk.Toplevel()
    curr_windo.title(filename)
    curr_windo.geometry('900x600+40+20')
    pt = Table(curr_windo, dataframe = df, showtoolbar=True, showstatusbar=True)
    pt.autoResizeColumns()
    pt.colheadercolor='#448BB9'
    pt.floatprecision = 6
    pt.show()
    
def maps_button():
    filename = filedialog.askopenfilename(filetypes = [("html or kml files","*.html; *.kml; *.kmz")])
    webbrowser.open_new_tab(filename)
 

button_file = Button(root, text="Open a facility or source category output file", command=browse_button).grid(row=0, column=0)
button_maps = Button(root, text="Open a chronic or acute map", command=maps_button).grid(row=1, column=0)

root.mainloop()
