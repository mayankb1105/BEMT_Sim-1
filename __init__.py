import numpy as np
import json

###### ENVIRONMENT VARIABLES ######

N_INTEGRATION_BLADE = 30
PRANDTL_TIPLOSS_ITERATIONS = 10
PRANDTL_TIPLOSS_TOLERANCE = 0.01

ENGINE_CEILING_TOLERANCE = 500 #m
ENGINE_OVERLOAD_FACTOR = 1.1

import message
import airfoil
import blade
import rotor