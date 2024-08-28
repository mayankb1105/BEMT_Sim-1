import numpy as np
import json

###### ENVIRONMENT VARIABLES ######

N_INTEGRATION_BLADE = 100
TIP_CUTOUT_FACTOR = 1e-6  # to prevent problems with the prandtl tip loss factor
PRANDTL_TIPLOSS_ITERATIONS = 10
PRANDTL_TIPLOSS_TOLERANCE = 1e-6

ENGINE_CEILING_TOLERANCE = 500 #m
ENGINE_OVERLOAD_FACTOR = 1.1

import time
import message
import atmosphere
import airfoil
import blade
import rotor