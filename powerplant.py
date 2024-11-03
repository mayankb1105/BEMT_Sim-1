from __init__ import *

# WARNING !!!
# This file has non-SI units. But input and output are in SI units.

# Elements in the following arrays are for temp deviation from ISA of -40, -30, -20, -10, 0, 10, 20, 30 respectively
# The key is the altitude in meters
# unit of peak power is kW and sfc is kg/kWh
ENGINE_DATA = {
    "peak_power":   {  0: np.array([112.2, 112.2, 112.2, 109.2, 102.0, 94.5, 86.3, 78.0]),
                    1000: np.array([112.2, 112.2, 107.1, 100.1, 93.7, 87.2, 80.4, 73.1]),
                    2000: np.array([112.2, 105.0, 97.9, 91.5, 85.6, 79.9, 74.2, 68.0]),
                    3000: np.array([103.7, 96.1, 89.3, 83.4, 78.0, 72.9, 67.9, 62.8]),
                    4000: np.array([96.0, 87.7, 81.4, 75.8, 70.8, 66.2, 61.8, 57.5]),
                    5000: np.array([89.5, 80.3, 74.0, 68.7, 64.1, 59.9, 55.9, 52.2]),
                    6000: np.array([83.1, 74.2, 67.1, 62.3, 57.9, 54.0, 50.4, 47.1]),
                    7000: np.array([75.9, 68.9, 61.4, 56.2, 52.2, 48.5, 45.3, 42.3]),
                    8000: np.array([69.1, 62.9, 56.5, 50.7, 46.8, 43.5, 40.5, 37.8]),
                    9000: np.array([62.3, 57.0, 51.9, 46.3, 41.9, 38.9, 36.1, 33.7]),
                   10000: np.array([55.6, 51.5, 46.9, 42.4, 37.8, 34.6, 32.1, 29.9])},

    "sfc":          {  0: np.array([0.360, 0.356, 0.353, 0.356, 0.365, 0.377, 0.392, 0.411]),
                    1000: np.array([0.345, 0.341, 0.345, 0.353, 0.362, 0.372, 0.385, 0.402]),
                    2000: np.array([0.333, 0.337, 0.344, 0.351, 0.359, 0.368, 0.380, 0.395]),
                    3000: np.array([0.332, 0.337, 0.342, 0.349, 0.357, 0.366, 0.376, 0.389]),
                    4000: np.array([0.331, 0.337, 0.342, 0.348, 0.355, 0.364, 0.373, 0.384]),
                    5000: np.array([0.330, 0.337, 0.341, 0.347, 0.354, 0.362, 0.371, 0.381]),
                    6000: np.array([0.328, 0.335, 0.342, 0.347, 0.353, 0.361, 0.369, 0.378]),
                    7000: np.array([0.328, 0.334, 0.342, 0.347, 0.353, 0.360, 0.368, 0.377]),
                    8000: np.array([0.326, 0.334, 0.341, 0.348, 0.353, 0.360, 0.367, 0.376]),
                    9000: np.array([0.324, 0.333, 0.340, 0.348, 0.355, 0.360, 0.367, 0.375]),
                   10000: np.array([0.322, 0.331, 0.340, 0.347, 0.355, 0.361, 0.368, 0.375])}
                     
}



class powerplant:

    def __init__(self):
            
            pass

    def get_fuel_rate(self, control_msg: message.simMessage):
        
        # The sim_data contains power required, altitude and temperature deviation from ISA
        sim_data = control_msg.get_payload()

        response = message.simMessage()

        # Getting the peak power and sfc values for the given altitude
        alt_lower = int(sim_data['altitude']/1000)*1000
        alt_upper = alt_lower + 1000
        
        # Checking if altitude is within limits
        if alt_upper>10000 or alt_lower<0:
            alt_upper = min(alt_upper,10000)
            alt_lower = max(alt_lower,0)
            response.add_warning({'UnknownAltitude':'Altitude is outside the range of the engine data.'})
        
        if alt_upper > 10000 + ENGINE_CEILING_TOLERANCE:
            response.add_error({'UnknownAltitude':'Altitude is outside the range of the engine data.'})
            return response
        
        # Interpolate to get peak power and sfc for the altitude and temp_dev_isa
        temp_dev_x = np.array([-40, -30, -20, -10, 0, 10, 20, 30])
        peak_power_lower = np.interp(sim_data['temp_dev_isa'], temp_dev_x, ENGINE_DATA['peak_power'][alt_lower])
        peak_power_upper = np.interp(sim_data['temp_dev_isa'], temp_dev_x, ENGINE_DATA['peak_power'][alt_upper])
        peak_power = np.interp(sim_data['altitude'], [alt_lower, alt_upper], [peak_power_lower, peak_power_upper]) #kW

        sfc_lower = np.interp(sim_data['temp_dev_isa'], temp_dev_x, ENGINE_DATA['sfc'][alt_lower])
        sfc_upper = np.interp(sim_data['temp_dev_isa'], temp_dev_x, ENGINE_DATA['sfc'][alt_upper])
        sfc = np.interp(sim_data['altitude'], [alt_lower, alt_upper], [sfc_lower, sfc_upper]) #kg/kWh

        # Generate warnings or errors in case of overload
        if sim_data['power_required']/1000 > peak_power:
            response.add_warning({'Overload':f'Power required exceeds peak power of the engine: {sim_data["power_required"]/1000:.0f}.'})
        
        if sim_data['power_required']/1000 > peak_power * ENGINE_OVERLOAD_FACTOR:
            response.add_error({'Overload':'Power required exceeds peak power of the engine.'})

        # Calculate fuel burn rate and throttle setting
        fuel_burn_rate = sim_data['power_required']/1000 * sfc / 3600 #kg/s
        throttle = sim_data['power_required']/peak_power/1000 * 100
        response.add_payload({'fuel_burn_rate':fuel_burn_rate})
        response.add_payload({'throttle':throttle})
        response.add_payload({'power_available':peak_power})

        return response