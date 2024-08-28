from __init__ import *

### ISA STANDARD ATMOSPHERE WITH A FIXED TEMPERATURE DEVIATION ###
class ISA:

    def __init__(self, T_deviation: float = 0):
        
        self.T_dev = T_deviation
        pass

    def get_atmosphere(self, altitude: float):
        
        response = message.simMessage()

        if altitude < 0 or altitude > 11000:
            response.add_error({'AltitudeError':'Altitude is outside the range of the model.'})
            return response

        temp = 288.15 + self.T_dev - 0.0065*altitude
        pressure = 101325*(1-22.558e-6*altitude)**5.2559
        density = pressure/(287.05*temp)

        response.add_payload({'temperature':temp, 'pressure':pressure, 'density':density})

        return response
    

        