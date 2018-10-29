# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 13:55:46 2018

@author: dlindsey
"""

from upload.InputFile import InputFile

class GasParams(InputFile):

    def __init__(self):
        InputFile.__init__(self, "resources/Gas_Param.xlsx")

    def createDataframe(self):
        self.dataframe = self.readFromPath(('pollutant', 'da', 'dw', 'rcl', 
                                            'henry', 'valid', 'source', 
                                            'dw_da_source', 'rcl_source', 'notes'
                                            ), {})
        
        
        self.dataframe['pollutant'] = self.dataframe['pollutant'].str.lower()