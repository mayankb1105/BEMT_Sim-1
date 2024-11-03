from __init__ import *

class maneuver:
        
    def __init__(self, maneuver_params):
        
        self.parameters = maneuver_params
        self.altitude = self.parameters["altitude"]
        self.atmosphere = atmosphere.ISA(0).get_atmosphere(self.parameters['altitude']).get_payload()
        self.climb_vel = self.parameters["climb_vel"]
        self.dry_mass = self.parameters["mass"]

### For now this class doesn't account for wind conditions or unwanted effects of tail rotor. Should be added later
class hover(maneuver):

    def get_fuel_burn_rate(self, vehicle_state):

        vehicle_state = vehicle_state.get_payload()
        # Calculate the power consumed by the main rotor to match the weight of the vehicle
        vehicle_parameters_main_rotor = message.simMessage()
        vehicle_parameters_main_rotor.add_payload({'mass':vehicle_state['mass'], 'desired_thrust': vehicle_state['mass']*g, 'atmosphere':self.atmosphere, 'climb_vel':self.climb_vel}) # For passing to the rotor
        main_rotor_performance = vehicle_state['main_rotor'].set_thrust(vehicle_parameters_main_rotor).get_payload()

        # Calculate the thrust required by the tail rotor to match the torque of the main rotor
        # !!! In the future, offload this to the fbd class ////////////////////////////
        tail_rotor_thrust = main_rotor_performance['torque'] / (vehicle_state['fbd'].get_cg_position()[1] - vehicle_state['fbd'].get_tr_position()[1])
        # /////////////////////////////////////////////////////////////////////////////

        # Calculate the power consumed by the tail rotor to match the torque of the main rotor
        vehicle_parameters_tail_rotor = message.simMessage(payload={'mass':vehicle_state['mass'], 'desired_thrust': tail_rotor_thrust, 'atmosphere': self.atmosphere, 'climb_vel':self.climb_vel}) # For passing to the rotor
        tail_rotor_performance = vehicle_state['tail_rotor'].set_thrust(vehicle_parameters_tail_rotor).get_payload()

        # Calculate fuel consumption rate for both rotors
        power_required = main_rotor_performance['power'] + tail_rotor_performance['power']
        fuel_burn_rate_parameters = message.simMessage(payload={'power_required':power_required,
                                                                'altitude':self.parameters['altitude'],
                                                                'temp_dev_isa':vehicle_state['temp_dev_isa']})
        fuel_burn_rate = vehicle_state['powerplant'].get_fuel_rate(fuel_burn_rate_parameters)
        
        # Return the fuel burn rate
        response = message.simMessage()
        response.add_payload({'power_required':power_required})
        response = response + fuel_burn_rate

        return response
    
class forward_flight(maneuver):
    #the trim values of collectives and cyclics of main rotor have to be provided as a part of maneuver parameters, which have to obtained by the GUI
    def get_fuel_burn_rate(self, vehicle_state):

        vehicle_state = vehicle_state.get_payload()
        drag=0.5*rho_air*vehicle_state['drag_area']*self.parameters['V_inf']**2
        alpha_tpp=np.arctan(drag/vehicle_state['mass']*g)
        # Calculate the power consumed by the main rotor to match the weight of the vehicle
        vehicle_parameters_main_rotor = message.simMessage(payload={'mass':vehicle_state['mass'],
                                                                    'climb_vel':self.climb_vel,
                                                                    'V_inf':self.parameters['V_inf'],
                                                                    'atmosphere':self.atmosphere,'drag_area':vehicle_state['drag_area']}) # For passing to the rotor
        rotors_result = vehicle_state['main_rotor'].set_trim_forward_flight(vehicle_parameters_main_rotor,vehicle_state['fbd'],vehicle_state['tail_rotor']).get_payload()

        power_required = rotors_result['mr_performance']['power'] + rotors_result['tr_performance']['power'] + self.climb_vel*vehicle_state['mass']*g
        fuel_burn_rate_parameters = message.simMessage(payload={'power_required':power_required,
                                                                'altitude':self.parameters['altitude'],
                                                                'temp_dev_isa':vehicle_state['temp_dev_isa']})
        fuel_burn_rate = vehicle_state['powerplant'].get_fuel_rate(fuel_burn_rate_parameters)
        
        # Return the fuel burn rate
        response = message.simMessage()
        response.add_payload({'power_required':power_required})
        response = response + fuel_burn_rate

        return response


def create_maneuvers(maneuver_params):

    maneuvers = []
    for man in maneuver_params:

        if man['type'] == 'Hover':
            maneuvers.append(hover(man))
        elif man['type'] == 'Forward Flight':
            maneuvers.append(forward_flight(man))      
        elif man['type'] == 'Climb':
            maneuvers.append(hover(man))

    return maneuvers            