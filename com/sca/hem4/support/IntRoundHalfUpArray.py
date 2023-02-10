# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 15:42:20 2020

@author: Steve Fudge
"""

import numpy as np

"""
Take a numpy array and return the numpy array rounded up to the nearest integer.
Note: this does not employ python's "round half to even" rule.
"""
def round_half_up(x):
    return (np.floor(x + 0.5)).astype(int)
