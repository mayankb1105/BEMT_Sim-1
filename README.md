BEMT Simulation Project
Project Overview
This project is a Blade Element Momentum Theory (BEMT) simulation designed to analyze the performance of rotorcraft. It focuses on rotor blade aerodynamics, forces, and dynamics in varying atmospheric conditions. The code integrates aerodynamic principles and atmospheric modeling to simulate maneuvers and calculate rotor dynamics, which can be applied to helicopter and drone blade design.

Project Structure
airfoil.py: Manages airfoil properties, providing functions to load data and compute lift and drag coefficients based on angle of attack.

atmosphere.py: Models standard atmospheric conditions, computing properties like density, pressure, and temperature at different altitudes.

blade.py: Represents rotor blade geometry and aerodynamic characteristics, calculating parameters like local lift and drag based on airfoil characteristics.

dynamics.py: Calculates the dynamics of rotor motion using BEMT, including induced velocities, forces, and moments on the blades.

maneuver.py: Defines flight maneuvers for the helicopter, enabling simulation of adjustments in pitch, roll, and yaw.

mission.py: Models a complete mission profile for the helicopter, recording details like gross weight, fuel weight, fuel burn rate, altitude, power required, airspeed, and more. This module relies on mission data and helicopter specs provided via JSON files.

New_dummy_data.py: Generates or loads example data for testing airfoil or blade characteristics within the simulation.


This project offers multiple functionalities through its various modules. Here's how to use each one:

Set Up the Environment: Define airfoil and blade properties by creating instances of the Airfoil, Blade, and Atmosphere classes in the relevant modules.

Run Dynamics Calculations: Use the dynamics.py module to calculate forces and moments for specific conditions. Configure rotor parameters and call the calculate_induced_velocity() and calculate_forces_and_moments() functions to obtain results.

Simulate a Maneuver: Use the Maneuver class from maneuver.py to simulate specific flight maneuvers by adjusting pitch, roll, and yaw angles.

Run a Mission Profile: The mission.py file enables comprehensive mission simulation. Here’s a quick example:

python
Copy code
from mission import mission

# Specify file paths for mission data and helicopter data
mission_data_file = 'path_to_mission_data.json'
heli_file_path = 'path_to_heli_data.json'
fbd_file_path = 'path_to_fbd_data.json'

# Initialize the mission profile
my_mission = mission(mission_data_file, heli_file_path, fbd_file_path)

# Access mission logs or specific details
print("Mission Log:", my_mission.mission_log)
Run Example Data Generation: Execute New_dummy_data.py to load sample data and validate basic functionality of the other modules.

Example Code
Here's a basic example to initialize the environment and perform a simple simulation:

from airfoil import Airfoil
from blade import Blade
from dynamics import calculate_forces_and_moments
from atmosphere import Atmosphere

# Load airfoil and set atmospheric conditions
airfoil = Airfoil()
airfoil.load_airfoil('path_to_airfoil_data.dat')

atmosphere = Atmosphere(altitude=1000)

# Define a rotor blade
blade = Blade(length=10, chord=0.3, twist_distribution=0.1)

# Calculate forces
forces, moments = calculate_forces_and_moments(blade, atmosphere, airfoil)
print("Forces:", forces)
print("Moments:", moments)
