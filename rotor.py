#####################################################################################
## THIS PROGRAM USES VALUES OBTAINED FROM THE BLADE TO CALCULATE ROTOR PERFORMANCE ##
#####################################################################################

from __init__ import *

class rotor:

    def __init__(self, rotor_data_file):
            
            self.rotor_data_file = rotor_data_file
            self.read_rotor_data()

    # Reads the rotor data from input JSON file
    def read_rotor_data(self):
          
            with open(self.rotor_data_file) as file:
                raw_data = json.load(file)
            
            self.blade_file_path = raw_data['blade_file_path']
            self.blade = blade.rotorblade(self.blade_file_path)

            self.omega = raw_data['omega']                           # May be changed by the simulator program later, constant for now
            self.number_of_blades = raw_data['number_of_blades']

    def get_performance(self, control_msg: message.simMessage):

        input_data = control_msg.get_payload()

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # EVALUATING FOR A ROTOR AT 90DEG WITH ZERO WIND. HAS TO BE CHANGED LATER!!!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #
        # blade needs number of blades, omega, tangential wind component, climb velocity,
        #  atmospheric conditions, pitch angle of the blade, 
        blade_conditions = message.simMessage()
        blade_conditions.add_payload({'number_of_blades':self.number_of_blades})
        blade_conditions.add_payload({'omega':self.omega})
        blade_conditions.add_payload({'h_vel':0})                                      # Would be calculated from headwind and crosswind later
        blade_conditions.add_payload({'climb_vel': input_data['climb_vel']})
        blade_conditions.add_payload({'atmosphere': input_data['atmosphere']})
        blade_conditions.add_payload({'pitch': input_data['collective']})              # Would be calculated from collective and cyclic later

        # Getting the performance of the blade
        blade_performance = self.blade.get_performance(blade_conditions)

        response = message.simMessage()
        response.add_payload(blade_performance.get_payload())

        return response
    
