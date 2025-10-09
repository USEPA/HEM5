# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:26:30 2020

@author: Steve Fudge
"""

import os

# Set the PROJ_LIB environment variable that is required by pyproj.
# This setting only holds during the course of the process.

os.environ['PROJ_LIB'] = os.path.join(os.getcwd(), 'share')
