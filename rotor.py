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

        # Evaluate blade performance at every 5 deg of azimuth
        # Azimuth is zero at the tail, increases anti-clockwise when viewed from above
        for phi in np.linspace(0, 2*np.pi, 72, endpoint=False):
             
            # Blade needs number of blades, omega, tangential wind component, climb velocity,
            # atmospheric conditions, pitch angle of the blade, 
            # Calculate the performance of a blade
            blade_conditions = message.simMessage()
            blade_conditions.add_payload({'number_of_blades':self.number_of_blades})
            blade_conditions.add_payload({'omega':self.omega})
            # blade_conditions.add_payload({'tangential_vel': input_data['headwind'] * np.sin(phi) + input_data['crosswind'] * np.cos(phi)}) # Tangential wind component
            blade_conditions.add_payload({'climb_vel': input_data['climb_vel']})
            blade_conditions.add_payload({'atmosphere': input_data['atmosphere']})
            blade_conditions.add_payload({'pitch': input_data['collective']}) # Would be calculated from collective and cyclic later

                # Add the performance of this blade to our list
                ###!!!!!! This is being done at a single point. Should be done at every 5 degrees later
            blade_performance = self.blade.get_performance(blade_conditions).get_payload()

        # Calculate the total performance of the rotor
        thrust = self.number_of_blades * blade_performance["thrust"]
        power = self.number_of_blades * blade_performance["power"]
        torque = self.number_of_blades * blade_performance["torque"]

        response = message.simMessage()
        response.add_payload({'thrust': thrust, 'power': power, 'torque': torque})

        return response
    
    # Takes the collectives, cyclics and conditions to get the performance of the rotor
    def get_performance_forward_flight(self, control_msg: message.simMessage):

        input_data = control_msg.get_payload()
        response = message.simMessage()

        # TPP angle calculations
        # Forward alpha_tpp comes from both rotor tilt due to drag and climb velocity
        alpha_tpp_c = input_data['tpp_angle'][0]
        # Lateral TPP angle comes from lateral force and thrust
        alpha_tpp_s = input_data['tpp_angle'][1]
        
        # Calculations to help find inflow velocity
        mu = input_data['V_inf'] / (self.omega * self.blade.radius)
        C_T = input_data['thrust'] / (input_data['atmosphere']['density'] \
                                              * np.pi * (self.blade.radius**2-self.blade.root_cutout**2) \
                                              * (self.omega**2) * self.blade.radius**2)
        lambda_i_Glauert = C_T/2/mu
        lambda_G = input_data['V_inf'] * np.sin(alpha_tpp_c) / (self.omega * self.blade.radius) + lambda_i_Glauert
        variable_inflow_coefficient = (4/3*mu/lambda_G)/(1.2+mu/lambda_G)

        # mu has to be greater than 0.2 for this to be valid
        if mu < 0.2:
            response.add_warning({'InflowWarning':f'Inflow ratio is {mu:0.4f} (less than 0.2). Results may not be accurate.'})
        
        # alpha_tpp has to be small for this to be valid
        if (alpha_tpp_s**2 + alpha_tpp_c**2) > 0.033:
             response.add_warning({'TPPWarning':'TPP angles are too high. Results may not be accurate.'})

        # Evaluate blade performance at every 5 deg of azimuth
        # Azimuth is zero at the tail, increases anti-clockwise when viewed from above
        forces_phi = []
        moments_phi = []
        coning_moment = 0
        for phi in np.linspace(0, 2*np.pi, N_INTEGRATION_AZIMUTH, endpoint=False):
             
            # Blade needs number of blades, omega, tangential wind component, climb velocity,
            # atmospheric conditions, pitch angle of the blade, 
            # Calculate the performance of a blade
            blade_conditions = message.simMessage()
            blade_conditions.add_payload({  'omega':self.omega,
                                            'V_inf': input_data['V_inf'],
                                            'phi': phi,
                                            'climb_vel': input_data['climb_vel'],
                                            'atmosphere': input_data['atmosphere'],
                                            'pitch': input_data['collective'] 
                                                    + input_data['cyclic_c']*np.cos(phi) 
                                                    + input_data['cyclic_s']*np.sin(phi), # Would be calculated from collective and cyclic later
                                            'beta_0': input_data['beta_0'],
                                            'variable_inflow_coefficient': variable_inflow_coefficient * np.cos(phi),
                                            'lambda_i_Glauert': lambda_i_Glauert,
                                            'alpha_tpp': [alpha_tpp_c, alpha_tpp_s]})

            # Get the results for this phi
            blade_performance = self.blade.get_performance_forward_flight(blade_conditions).get_payload()
            forces_phi.append(blade_performance['forces'])
            moments_phi.append(blade_performance['moments'])
            coning_moment += blade_performance['coning_moment']

        cycle_avg_force = self.number_of_blades * np.mean(forces_phi, axis=0)
        cycle_avg_moment = self.number_of_blades * np.mean(moments_phi, axis=0)
        cycle_avg_coning_moment = coning_moment / N_INTEGRATION_AZIMUTH
        
        # Calculate the total performance of the rotor
        thrust = cycle_avg_force[2]  # Thrust is in the z direction
        torque = (-cycle_avg_moment[2]) # Minus sign because torque is in the opposite direction
        power = torque * self.omega

        response.add_payload({'thrust': thrust, 'power': power, 'torque': torque, 'forces': cycle_avg_force, 'moments': cycle_avg_moment, 'coning_moment': cycle_avg_coning_moment})

        return response
    
    def get_performance_forward_flight_2(self, control_msg: message.simMessage):

        input_data = control_msg.get_payload()
        response = message.simMessage()

        # Calculations to help find inflow velocity
        #mu = input_data['V_inf'] / (self.omega * self.blade.radius)
        #C_T = input_data['thrust'] / (input_data['atmosphere']['density'] \
        #                                      * np.pi * (self.blade.radius**2-self.blade.root_cutout**2) \
        #                                      * (self.omega**2) * self.blade.radius**2)
        #lambda_i_Glauert = C_T/2/mu
        #lambda_G = input_data['V_inf'] / (self.omega * self.blade.radius) + lambda_i_Glauert
        #variable_inflow_coefficient = (4/3*mu/lambda_G)/(1.2+mu/lambda_G)

        # mu has to be greater than 0.2 for this to be valid
        #if mu < 0.2:
        #    response.add_warning({'InflowWarning':'Inflow ratio is less than 0.2. Results may not be accurate.'})
        
        # alpha_tpp has to be small for this to be valid
        #if (alpha_tpp_s**2 + alpha_tpp_c**2) > 0.033:
        #     response.add_warning({'TPPWarning':'TPP angles are too high. Results may not be accurate.'})

        # TPP angle calculations
        # Lateral TPP angle comes from lateral force and thrust
        alpha_tpp_s = np.arctan(input_data['lateral_force']/input_data['mass']/g)
        # Forward alpha_tpp comes from both rotor tilt due to drag and climb velocity
        alpha_tpp_c = np.arctan(input_data['total_drag']/input_data['mass']/g) #+ np.arctan(input_data['climb_vel']/input_data['V_inf']) 

        # Evaluate blade performance at every 5 deg of azimuth
        # Azimuth is zero at the tail, increases anti-clockwise when viewed from above
        forces_phi = []
        moments_phi = []
        beta=[]
        for psi in np.linspace(0, 2*np.pi, N_INTEGRATION_AZIMUTH, endpoint=False):
             
            # Blade needs number of blades, omega, tangential wind component, climb velocity,
            # atmospheric conditions, pitch angle of the blade, 
            # Calculate the performance of a blade
            blade_conditions = message.simMessage()
            blade_conditions.add_payload({'omega':self.omega})
            blade_conditions.add_payload({'V_inf': input_data['V_inf']}) # Total wind speed
            blade_conditions.add_payload({'psi': psi})
            blade_conditions.add_payload({'atmosphere': input_data['atmosphere']})
            blade_conditions.add_payload({'pitch': input_data['collective'] 
                                                 + input_data['cyclic_c']*np.cos(psi) 
                                                 + input_data['cyclic_s']*np.sin(psi)}) # Would be calculated from collective and cyclic later
            #blade_conditions.add_payload({'beta_0': input_data['beta_0']})
            #blade_conditions.add_payload({'variable_inflow_coefficient': variable_inflow_coefficient * np.cos(phi)})
            #blade_conditions.add_payload({'lambda_i_Glauert': lambda_i_Glauert})
            blade_conditions.add_payload({'alpha_tpp': [alpha_tpp_c, alpha_tpp_s]})

            # Get the results for this phi
            blade_performance = self.blade.get_performance_forward_flight_2(blade_conditions).get_payload()
            forces_phi.append(blade_performance['forces'])
            moments_phi.append(blade_performance['moments'])
            beta.append(blade_performance['beta'])

        cycle_avg_force = np.mean(forces_phi, axis=0)
        cycle_avg_moment = np.mean(moments_phi, axis=0)
        
        # Calculate the total performance of the rotor
        thrust = self.number_of_blades * cycle_avg_force[2]  # Thrust is in the z direction
        torque = self.number_of_blades * (-cycle_avg_moment[2]) # Minus sign because torque is in the opposite direction
        power = torque * self.omega

        response.add_payload({'thrust': thrust, 'power': power, 'torque': torque, 'forces': cycle_avg_force, 'moments': cycle_avg_moment,
                              'Force_y':thrust*np.cos(alpha_tpp_c),'Force_z':thrust*np.sin(alpha_tpp_c),'beta':beta})

        return response
    
    def get_performance_forward_flight_3(self, control_msg: message.simMessage):

        input_data = control_msg.get_payload()
        response = message.simMessage()
        alpha_tpp_s = np.arctan(input_data['lateral_force']/input_data['mass']/g)
        # Forward alpha_tpp comes from both rotor tilt due to drag and climb velocity
        alpha_tpp_c = np.arctan(input_data['total_drag']/input_data['mass']/g) #+ np.arctan(input_data['climb_vel']/input_data['V_inf']) 

        # Evaluate blade performance at every 5 deg of azimuth
        # Azimuth is zero at the tail, increases anti-clockwise when viewed from above
        forces_phi = []
        moments_phi = []
        beta=[]
        psi=np.linspace(0,pi,72)
        blade_conditions = message.simMessage()
        blade_conditions.add_payload({'omega':self.omega})
        blade_conditions.add_payload({'V_inf': input_data['V_inf']}) # Total wind speed
        blade_conditions.add_payload({'psi': psi})
        blade_conditions.add_payload({'atmosphere': input_data['atmosphere']})
        blade_conditions.add_payload({'pitch': input_data['collective'] 
                                                 + input_data['cyclic_c']*np.cos(psi) 
                                                 + input_data['cyclic_s']*np.sin(psi)})
        blade_conditions.add_payload({'alpha_tpp': [alpha_tpp_c, alpha_tpp_s]})
        blade_performance = self.blade.get_performance_forward_flight_2(blade_conditions).get_payload()
        forces_phi.append(blade_performance['forces'])
        moments_phi.append(blade_performance['moments'])
        beta.append(blade_performance['beta'])

        cycle_avg_force = np.mean(forces_phi, axis=0)
        cycle_avg_moment = np.mean(moments_phi, axis=0)
        
        # Calculate the total performance of the rotor
        thrust = self.number_of_blades * cycle_avg_force[2]  # Thrust is in the z direction
        torque = self.number_of_blades * (-cycle_avg_moment[2]) # Minus sign because torque is in the opposite direction
        power = np.abs(torque * self.omega)

        response.add_payload({'thrust': thrust, 'power': power, 'torque': torque, 'forces': cycle_avg_force, 'moments': cycle_avg_moment,
                              'Force_y':thrust*np.cos(alpha_tpp_c),'Force_z':thrust*np.sin(alpha_tpp_c),'beta':beta})

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

            rotor_performance = self.get_performance(message.simMessage(payload = {'collective': collective,**conditions,'atmosphere':conditions['atmosphere'],'climb_vel':conditions['climb_vel']})).get_payload()
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
    
    def set_trim_forward_flight(self, conditions: message.simMessage, fbd, tail_rotor):

        # Before I forget, let me list down the algorithm for forward flight trim
        # We have to balance all three forces and moments
        # We can control the collective, two cyclics and tail rotor collective
        # We can also control the angle between hub plane and tip path plane
        #
        # 1. First, we will find the total thrust required to balance weight and drag.
        # 2. Then, calculate tip path plane angles to make it perpendicular to the resultant thrust.
        # 3. Once this is done, set collective to reach the required thrust
        # 4. Then, find beta0 and cyclics. In TPP, beta0 should balance total coning moment,
        #     cyclics should balance moment along lateral axes because rotor shouldn't produce any moment in the TPP
        # 5. Once this is done, we get moments in the helicopter plane. Tilt the hub plane (the entire helicopter) to balance these moments.
        #    This moment balance happens because the hinge of the rotor is offset from the centre
        # Repeat parts of these process until convergence

        response = message.simMessage()

        conditions = conditions.get_payload()

        # First, find the total thrust required to balance weight and drag
        F_desired = np.array([0, \
                              0.5 * conditions['atmosphere']['density'] * conditions['V_inf']**2 * conditions['drag_area'],\
                              conditions['mass'] * g ])
        M_desired = np.array([0, 0, 0])
        tpp_angle = np.array([np.arctan(F_desired[1]/F_desired[2]), \
                              np.arctan(F_desired[0]/F_desired[2]) ])
        beta_0 =  2 * np.pi / 180
        collective = 2 * np.pi / 180
        cyclic_c = 0
        cyclic_s = 0
        tr_collective = 0
        hub_plane_angle = np.array([0, 0])

        mr_performance = None
        tr_performance = None

        # Run mr tr calculations
        for j in range(CONTROLS_CONVERGENCE_ITERATIONS):

            # Find the tip path plane angles to make it perpendicular to the resultant thrust

            for i in range(CONTROLS_CONVERGENCE_ITERATIONS):

                tpp_angle = np.array([np.arctan(F_desired[1]/F_desired[2]), \
                                    np.arctan(F_desired[0]/F_desired[2]) ])
                controls = message.simMessage()
                controls.add_payload({  'thrust':np.linalg.norm(F_desired),
                                        'atmosphere': conditions['atmosphere'],
                                        'V_inf': conditions['V_inf'],
                                        'climb_vel': conditions['climb_vel'],
                                        'tpp_angle': tpp_angle,
                                        'collective': collective,
                                        'cyclic_c': cyclic_c,
                                        'cyclic_s': cyclic_s,
                                        'beta_0': beta_0 })
                
                # Set collective to reach the required thrust
                collective = self.solve_control_forward_flight(controls, 'collective', np.linalg.norm(F_desired), 'thrust', initial_guess = collective).get_payload()['collective'] 

                # Find beta_0
                beta_0 = self.solve_control_forward_flight(controls, 'beta_0', 0, 'coning_moment', initial_guess = beta_0).get_payload()['beta_0']

                # Find cyclics
                cyclic_c = self.solve_control_forward_flight(controls, 'cyclic_c', 0, 'moments', 0, initial_guess = cyclic_c).get_payload()['cyclic_c']
                cyclic_s = self.solve_control_forward_flight(controls, 'cyclic_s', 0, 'moments', 1, initial_guess = cyclic_s).get_payload()['cyclic_s']

                # Check for convergence
                controls = message.simMessage()
                controls.add_payload({  'thrust':np.linalg.norm(F_desired),
                                        'atmosphere': conditions['atmosphere'],
                                        'climb_vel': conditions['climb_vel'],
                                        'V_inf': conditions['V_inf'],
                                        'tpp_angle': tpp_angle,
                                        'collective': collective,
                                        'cyclic_c': cyclic_c,
                                        'cyclic_s': cyclic_s,
                                        'beta_0': beta_0 })
                
                mr_performance_message = self.get_performance_forward_flight(controls)
                mr_performance = mr_performance_message.get_payload(suppress_warnings=True)
                if np.linalg.norm(mr_performance['thrust'] * np.cos(tpp_angle[0]) * np.cos(tpp_angle[1]) * np.array([np.tan(tpp_angle[1]), np.tan(tpp_angle[0]), 1]) - F_desired) < ACCELERATION_TOLERANCE * conditions['mass'] and \
                np.linalg.norm((mr_performance['moments'] - M_desired)[:2]) < ACCELERATION_TOLERANCE*self.blade.radius:
                    break

                # This will only run if the collective pitch doesn't converge or the rotor can't produce enough thrust
                if i == CONTROLS_CONVERGENCE_ITERATIONS - 1:
                    response.add_error({'ConvergenceError':'TPP forces and moments did not converge. Try increasing CONTROLS_CONVERGENCE_ITERATIONS.'})

            # Calculate tail rotor collective
            # Forward flight effects are being ignore for tail rotor right now. This is a very bad assumption but we will fix it later
            tr_conditions = message.simMessage()
            tr_conditions.add_payload({'desired_thrust':mr_performance['torque']/(fbd.get_cg_position()[1]-fbd.get_tr_position()[1]),
                                        'mass':conditions['mass'],
                                        'climb_vel':0,
                                        'atmosphere':conditions['atmosphere']})
            
            tr_performance_message = tail_rotor.set_thrust(tr_conditions)
            tr_performance = tr_performance_message.get_payload()
            tr_collective = tr_performance['collective']
            F_desired[0] = -tr_performance['thrust'] # Tail rotor thrust has to be balanced by main rotor

            # Transform main rotor forces into ground plane
            F_ground_plane = mr_performance['thrust'] * np.cos(tpp_angle[0]) * np.cos(tpp_angle[1]) * np.array([np.tan(tpp_angle[1]), np.tan(tpp_angle[0]), 1])
            F_ground_plane[0] += tr_performance['thrust']
            F_ground_plane[1] += -0.5 * conditions['atmosphere']['density'] * conditions['V_inf']**2 * conditions['drag_area']
            F_ground_plane[2] += -conditions['mass'] * g

            if np.linalg.norm(F_ground_plane) < 10: # Fixed 10N tolerance for now
                break

            # This will only run if the collective pitch doesn't converge or the rotor can't produce enough thrust
            if j == CONTROLS_CONVERGENCE_ITERATIONS - 1:
                response.add_error({'ConvergenceError':'Forces did not converge. Try increasing CONTROLS_CONVERGENCE_ITERATIONS.'})

        _ = mr_performance_message.get_payload(suppress_warnings=False) # To check for pending warnings after convergence
        _ = tr_performance_message.get_payload(suppress_warnings=False) # To check for pending warnings after convergence

        controls = {'collective':collective,
                    'cyclic_c':cyclic_c,
                    'cyclic_s':cyclic_s,
                    'climb_vel':conditions['climb_vel'],
                    'beta_0':beta_0,
                    'tpp_angle':tpp_angle,
                    'tr_collective':tr_collective}
        response.add_payload({  'controls':controls,
                                'mr_performance':mr_performance,
                                'tr_performance':tr_performance})
        
        return response

    
     # Takes required thrust, alpha_tpp and conditions to get the collective and cyclic required, power required and torque in forward flight
    def set_collectives_forward_flight(self, conditions: message.simMessage):

        response = message.simMessage()

        conditions = conditions.get_payload()
        collective_lower = 0
        collective_upper = self.blade.airfoil.alphacrit
        collective = (collective_lower + collective_upper)/2
        collective_1c = (collective_lower + collective_upper)/2
        rotor_performance = None
        set_collective=collective
        set_collective_1c=collective_1c
        print('Starting forward flight trim iterations')
        for j in range(CONTROLS_CONVERGENCE_ITERATIONS):
        # Bisection method to find the collective required to maintain hover
            collective_lower = 0
            collective_upper = self.blade.airfoil.alphacrit
            collective = set_collective
            collective_1c = set_collective_1c
            for i in range(CONTROLS_CONVERGENCE_ITERATIONS):
                b = message.simMessage(payload={'mass':conditions['mass'],'total_drag':conditions['total_drag'],'lateral_force':0,'atmosphere':conditions['atmosphere'],
                                                             'cyclic_c':set_collective_1c,'cyclic_s':0,'collective':collective,
                                                                "V_inf":conditions['V_inf'],'climb_vel':conditions['climb_vel'],'headwind':0,'crosswind':0})
                rotor_performance = self.get_performance_forward_flight_2(b).get_payload()
                desired_thrust=((conditions['mass']*g)**2+conditions['total_drag']**2)**0.5
                #print('Collective',set_collective)
                if abs((rotor_performance['thrust']-desired_thrust)/conditions['mass']) < ACCELERATION_TOLERANCE: # Convergence criteria
                    set_collective=collective
                    break
                if rotor_performance['thrust'] > desired_thrust:
                    collective_upper = collective
                    collective = (collective + collective_lower)/2
                else:
                    collective_lower = collective
                    collective = (collective + collective_upper)/2

                #if abs((rotor_performance['thrust']-conditions['desired_thrust'])/conditions['mass']) < ACCELERATION_TOLERANCE: # Convergence criteria
                #    break

            # This will only run if the collective pitch doesn't converge or the rotor can't produce enough thrust
                if i == CONTROLS_CONVERGENCE_ITERATIONS - 1:
                    response.add_error({'ConvergenceError':'Thrust convergence could not be achieved. Try increasing CONTROLS_CONVERGENCE_ITERATIONS.'})

            collective_lower = 0
            collective_upper = self.blade.airfoil.alphacrit
            collective = set_collective
            collective_1c = set_collective_1c
            for i in range(CONTROLS_CONVERGENCE_ITERATIONS):
                b = message.simMessage(payload={'mass':conditions['mass'],'total_drag':conditions['total_drag'],'lateral_force':0,'atmosphere':conditions['atmosphere'],
                                                                'cyclic_c':collective_1c,'cyclic_s':0,'collective':set_collective,
                                                                "V_inf":conditions['V_inf'],'climb_vel':conditions['climb_vel'],'headwind':0,'crosswind':0})
                rotor_performance = self.get_performance_forward_flight_2(b).get_payload()
                alpha_tpp=conditions['total_drag']/conditions['mass']/g
                beta_1c=rotor_performance['beta'][0]-rotor_performance['beta'][36]
                #print('Cyclic_1c',set_collective_1c)
                if abs(beta_1c-alpha_tpp) < BETA_TOLERANCE: # Convergence criteria
                    set_collective_1c=collective_1c
                    break
                if beta_1c > alpha_tpp:
                    collective_upper = collective_1c
                    collective_1c = (collective_1c + collective_lower)/2
                else:
                    collective_lower = collective_1c
                    collective_1c = (collective_1c + collective_upper)/2
            # This will only run if the collective pitch doesn't converge or the rotor can't produce enough thrust
                if i == CONTROLS_CONVERGENCE_ITERATIONS - 1:
                    response.add_error({'ConvergenceError':'Thrust convergence could not be achieved. Try increasing CONTROLS_CONVERGENCE_ITERATIONS.'})
            t=rotor_performance['thrust']
            w=conditions['mass']*g
            print(f'After :{j+1} iterations \n Thrust={t}, Required thrust={w} \n Beta_1c={beta_1c} , alpha_tpp:{alpha_tpp}')
            print(f' Collective={set_collective}, Cyclic_1c={set_collective_1c}')
        response.add_payload(rotor_performance)
        response.add_payload({'collective':collective,'cyclic_1c':set_collective_1c})

        return response
    

    # Tries to get a control input using a variant of Newton-Raphson method
    def solve_control_forward_flight(self, conditions: message.simMessage, control: str, des_output: float, output: str, output_index = None, initial_guess = 1*np.pi/180):

        response = message.simMessage()

        guess = initial_guess
        delta = 1*np.pi/180
        
        # Initialising the first step for solution
        conditions.add_payload({control: guess})
        rotor_performance = self.get_performance_forward_flight(conditions).get_payload(suppress_warnings=True)
        output_value_prev = rotor_performance[output]
        if output_index is not None:
            output_value_prev = output_value_prev[output_index]
        
        # Solution convergence loop
        for i in range(CONTROLS_CONVERGENCE_ITERATIONS):

            guess += delta if abs(delta) < 1*np.pi/180 else 1*np.pi/180*delta/abs(delta) # not more than 1 degree at a time
            conditions.add_payload({control: guess})
            rotor_performance = self.get_performance_forward_flight(conditions).get_payload(suppress_warnings=True)
            output_value = rotor_performance[output]
            if output_index is not None:
                output_value = output_value[output_index]
            
            # Check for convergence
            if abs(output_value - des_output) < ACCELERATION_TOLERANCE:
                break

            delta = (des_output - output_value) * delta / (output_value - output_value_prev)
            output_value_prev = output_value

            # This will only run if the collective pitch doesn't converge or the rotor can't produce enough thrust
            if i == CONTROLS_CONVERGENCE_ITERATIONS - 1:
                response.add_warning({'ControlConvergence':f'{control} convergence could not be achieved. Try increasing CONTROLS_CONVERGENCE_ITERATIONS.'})
            
        response.add_payload({control: guess})

        return response
