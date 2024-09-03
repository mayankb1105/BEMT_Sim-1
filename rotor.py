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
            self.blade_angle = np.linspace(0, 2*np.pi, self.number_of_blades, endpoint=False) # Angle of each blade from the front of the rotor

    # Takes the collective and conditions to get the performance of the rotor
    def get_performance(self, control_msg: message.simMessage):

        input_data = control_msg.get_payload()

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # EVALUATING FOR A ROTOR AT 90DEG WITH ZERO WIND. HAS TO BE CHANGED LATER!!!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        # Blade needs number of blades, omega, tangential wind component, climb velocity,
        # atmospheric conditions, pitch angle of the blade, 
        # Calculate the performance of each blade
        blade_performance = []
        for blade_number in range(self.number_of_blades):
            blade_conditions = message.simMessage()
            blade_conditions.add_payload({'number_of_blades':self.number_of_blades})
            blade_conditions.add_payload({'omega':self.omega})
            blade_conditions.add_payload({'h_vel':0})                                # Would be calculated from headwind and crosswind later
            blade_conditions.add_payload({'climb_vel': input_data['climb_vel']})
            blade_conditions.add_payload({'atmosphere': input_data['atmosphere']})
            blade_conditions.add_payload({'pitch': input_data['collective']}) # Would be calculated from collective and cyclic later

            # Add the performance of this blade to our list
            ###!!!!!! This is being done at a single point. Should be done at every 5 degrees later
            blade_performance.append(self.blade.get_performance(blade_conditions).get_payload())

        # Calculate the total performance of the rotor
        thrust = sum([blade['thrust'] for blade in blade_performance])
        power = sum([blade['power'] for blade in blade_performance])
        torque = sum([blade['torque'] for blade in blade_performance])

        response = message.simMessage()
        response.add_payload({'thrust': thrust, 'power': power, 'torque': torque})

        return response
    
    # Takes required thrust and conditions to get the collective required, power required and torque.
    def set_thrust(self, conditions: message.simMessage):

        response = message.simMessage()

        conditions = conditions.get_payload()
        collective_lower = 0
        collective_upper = self.blade.airfoil.alphacrit
        collective = (collective_lower + collective_upper)/2
        rotor_performance = None

        # Bisection method to find the collective required to maintain hover
        for i in range(CONTROLS_CONVERGENCE_ITERATIONS):

            rotor_performance = self.get_performance(message.simMessage(payload = {'collective': collective,**conditions})).get_payload()
            if rotor_performance['thrust'] > conditions['desired_thrust']:
                collective_upper = collective
                collective = (collective + collective_lower)/2
            else:
                collective_lower = collective
                collective = (collective + collective_upper)/2

            if abs((rotor_performance['thrust']-conditions['desired_thrust'])/conditions['mass']) < ACCELERATION_TOLERANCE: # Convergence criteria
                break

            # This will only run if the collective pitch doesn't converge or the rotor can't produce enough thrust
            if i == CONTROLS_CONVERGENCE_ITERATIONS - 1:
                response.add_error({'ConvergenceError':'Thrust convergence could not be achieved. Try increasing CONTROLS_CONVERGENCE_ITERATIONS.'})
        
        response.add_payload(rotor_performance)
        response.add_payload({'collective':collective})

        return response