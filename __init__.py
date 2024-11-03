import numpy as np
import json
from scipy.optimize import fsolve
import matplotlib.pyplot as plt

###### ENVIRONMENT VARIABLES ######

N_INTEGRATION_BLADE = 100
N_INTEGRATION_AZIMUTH = 72
TIP_CUTOUT_FACTOR = 1e-6  # to prevent problems with the prandtl tip loss factor
PRANDTL_TIPLOSS_ITERATIONS = 10
PRANDTL_TIPLOSS_TOLERANCE = 1e-6

THRUST_CONVERGENCE_ITERATIONS = 50
THRUST_CONVERGENCE_TOLERANCE = 0.005

BETA_TOLERANCE=0.0005

ENGINE_CEILING_TOLERANCE = 500 #m
ENGINE_OVERLOAD_FACTOR = 1.1

ACCELERATION_TOLERANCE = 0.008 #m/s^2 # On the order of acceleration due to fuel depletion over 1 minute
CONTROLS_CONVERGENCE_ITERATIONS = 15 # 12 should be the max iterations it should take for collective using bisection method 
                                     # if helicopter can produce max acceleration of 30m/s^2 including g
                                     # Ignore the above two lines because this number is being used in a lot of other loops

g = 9.81 #m/s^2
rho_air=1.225 #kg/m^3
pi=np.pi

import time
import message
import atmosphere
import dynamics
import airfoil
import blade
import rotor
import maneuver
#import new_simulator
# import maneuver
# import mission