import numpy as np
import json

###### ENVIRONMENT VARIABLES ######

N_INTEGRATION_BLADE = 100
TIP_CUTOUT_FACTOR = 1e-6  # to prevent problems with the prandtl tip loss factor
PRANDTL_TIPLOSS_ITERATIONS = 10
PRANDTL_TIPLOSS_TOLERANCE = 1e-6

ENGINE_CEILING_TOLERANCE = 500 #m
ENGINE_OVERLOAD_FACTOR = 1.1

ACCELERATION_TOLERANCE = 0.008 #m/s^2 # On the order of acceleration due to fuel depletion over 1 minute
CONTROLS_CONVERGENCE_ITERATIONS = 15 # 12 should be the max iterations it should take for collective using bisection method 
                                     # if helicopter can produce max acceleration of 30m/s^2 including g

g = 9.81 #m/s^2

import time
import message
import atmosphere
import airfoil
import blade
import rotor
# import maneuver
# import mission