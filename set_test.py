# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 13:22:56 2018

@author: jbaker
"""

import pandas as pd

empty = pd.DataFrame()
a = [1, 2, 3, 4]
b = [2, 3, 6]

#set comparison
if len(set(b).difference(set(a))) > 0:

    print(set(b).difference(set(a)))
    
print(dir(empty))