###################################################################################
## THIS PROGRAM USES AIRFOIL DATA AND BEMT TO FIND OUT THE PERFORMANCE OF A LIFT ##
###################################################################################

from __init__ import *

class rotorblade:

    def __init__(self, blade_file_path):
            
            self.blade_file_path = blade_file_path
            self.read_blade_data()

    # Reads the blade data from input JSON file
    def read_blade_data(self):
          
            with open(self.blade_file_path) as file:
                raw_data = json.load(file)
            
            self.airfoil_data_file_path = raw_data['airfoil_data_file_path']
            self.airfoil = airfoil.airfoil(self.airfoil_data_file_path)

            self.radius = raw_data['radius']
            self.root_cutout = raw_data['root_cutout']

            self.x_chord = np.array(raw_data["x_chord"])
            self.chord = np.array(raw_data["chord"])

            self.x_twist = np.array(raw_data["x_twist"])
            self.twist = np.array(raw_data["twist"])

            self.mmoi = raw_data['MMOI']

    def get_chord(self, radius: np.ndarray):
         
        if np.any(radius < self.root_cutout) or np.any(radius > self.radius):
            response = message.simMessage()
            response.add_error({'UnknownRadius':f'Radius is outside the range of the blade.'})
            return response

        response = message.simMessage()
        x = radius/self.radius
        chord_value =  np.interp(x, self.x_chord, self.chord)
        response.add_payload({'chord':chord_value})

        return response
    
    def get_twist(self, radius: np.ndarray):
             
        if np.any(radius < self.root_cutout) or np.any(radius > self.radius):
            response = message.simMessage()
            response.add_error({'UnknownRadius':'Radius is outside the range of the blade.'})
            return response

        response = message.simMessage()
        x = radius/self.radius
        twist_value =  np.interp(x, self.x_twist, self.twist)
        response.add_payload({'twist':twist_value})

        return response
    
    # Gives the thrust, drag and moment for a given pitch angle and wind conditions
    # 'msg' is expected to contain horizontal wind component (excluding blade vel) and climb vel,
    #  atmospheric conditions and number of blades
    def get_performance(self, msg: message.simMessage, get_non_dims = False):
         
        data = msg.get_payload()

        response = message.simMessage()
        
        r = np.linspace(self.root_cutout,self.radius*(1 - TIP_CUTOUT_FACTOR),N_INTEGRATION_BLADE)
        chord = self.get_chord(r).get_payload()['chord']
        twist = self.get_twist(r).get_payload()['twist']
        theta = data['pitch'] + twist

        lambda_c = data['climb_vel']/data['omega']/self.radius
        sigma = data['number_of_blades']*chord/(2*np.pi*r)
        coeff = sigma*self.airfoil.cl_alpha/16 - lambda_c/2
        lambda_ = (coeff**2 + sigma*self.airfoil.cl_alpha*theta*r/self.radius/8)**0.5 - coeff

        ## Prandtl's tip loss factor
        converged = False
        for i in range(PRANDTL_TIPLOSS_ITERATIONS):
            lambda_old = lambda_
            f = data['number_of_blades']*(1-r/self.radius)/2/lambda_
            F = 2/np.pi*np.arccos(np.exp(-f))
            lambda_ = sigma * self.airfoil.cl_alpha/16/F * (np.sqrt(1+32*F*theta*r/self.radius/sigma/self.airfoil.cl_alpha) - 1)
            if np.allclose(lambda_,lambda_old,rtol=PRANDTL_TIPLOSS_TOLERANCE):
                converged = True
                break
        
        if not converged:
            response.add_warning({'TipLoss':'Prandtl tip loss factor did not converge.'})

        ## Relative velocities wrt blade calculations
        U_p = lambda_ * data['omega'] * self.radius
        U_t = data['omega'] * r
        phi = np.arctan(U_p/U_t)
        cos_phi = np.cos(phi)
        sin_phi = np.sin(phi)

        airfoil_performance = self.airfoil.get_performance(theta - phi).get_payload()
        CL = airfoil_performance['CL']
        CD = airfoil_performance['CD']
        CM = airfoil_performance['CM']

        rho = data['atmosphere']['density']

        dT = 0.5*rho*(U_p**2 + U_t**2)*chord*(CL*cos_phi - CD*sin_phi)
        dQ = r*0.5*rho*(U_p**2 + U_t**2)*chord*(CD*cos_phi + CL*sin_phi)

        thrust = np.trapz(dT,r)

        thrust = np.trapz(dT,r)
        torque = np.trapz(dQ,r)
        power = torque*data['omega']

        response.add_payload({'thrust':thrust, 'torque':torque, 'power':power})
 
        if get_non_dims:
            non_dims = {}
            non_dims['CT'] = 2 * thrust * data['number_of_blades'] / (rho * np.pi * self.radius**4 * data['omega']**2)
            non_dims['sigma'] = data['number_of_blades']*chord[0]*(self.radius-self.root_cutout)/(np.pi*self.radius**2)
            response.add_payload({'non_dims':non_dims})


        return response
    
    def get_performance_forward_flight(self, msg: message.simMessage):
         
        data = msg.get_payload()

        response = message.simMessage()
        
        r = np.linspace(self.root_cutout,self.radius*(1 - TIP_CUTOUT_FACTOR),N_INTEGRATION_BLADE)
        chord = self.get_chord(r).get_payload()['chord']
        twist = self.get_twist(r).get_payload()['twist']
        theta = data['pitch'] + twist

        lambda_i = data['lambda_i_Glauert'] * ( 1 + data['variable_inflow_coefficient'] * r / self.radius )
        U_p = data['V_inf'] * data['alpha_tpp'][0] + lambda_i * data['omega'] * self.radius + 0 + data['V_inf'] * np.sin(data['beta_0']) * np.cos(data['phi'])
        U_t = data['omega'] * r + data['V_inf'] * np.cos(data['alpha_tpp'][0]) * np.cos(data['phi'])

        airfoil_performance = self.airfoil.get_performance(theta - np.arctan(U_p/U_t)).get_payload()
        CL = airfoil_performance['CL']
        CD = airfoil_performance['CD']
        CM = airfoil_performance['CM']

        rho = data['atmosphere']['density']
        cos_phi = np.cos(np.arctan(U_p/U_t))
        sin_phi = np.sin(np.arctan(U_p/U_t))

        # Refer to the diagram in dynamics.py for the coordinate system

        dFz = 0.5*rho*(U_p**2 + U_t**2)*chord*(CL*cos_phi - CD*sin_phi)
        dFtheta = -r*0.5*rho*(U_p**2 + U_t**2)*chord*(CD*cos_phi + CL*sin_phi) # Tangential force. Minus sign becuase it is in the opposite direction

        Ftheta = np.trapz(dFtheta,r)
        Fx = Ftheta*np.cos(data['phi'])
        Fy = Ftheta*np.sin(data['phi'])
        Fz = np.trapz(dFz,r)
        F = np.array([Fx,Fy,Fz])

        Mx = np.trapz(dFz*r,r)*np.cos(data['phi'])  # Pitch up moment is positive
        # dMy needs a minus because position vector is in x-dir and Force vector is in z-dir. Moment is rxF so ixk = -j
        My = np.trapz(-dFz*r*np.sin(data['phi']),r)  # Roll right moment is positive
        Mz = np.trapz(dFtheta*r,r)
        M = np.array([Mx,My,Mz])
        
        thrust = Fz
        torque = -Mz     # Minus because applied torque is in opposite direction
        power = torque*data['omega']

        response.add_payload({'thrust':thrust, 'torque':torque, 'power':power, 'forces':F, 'moments':M})

        return response
    
    def get_performance_forward_flight_2(self, msg: message.simMessage):
         
        data = msg.get_payload()

        response = message.simMessage()
        
        r = np.linspace(self.root_cutout,self.radius*(1 - TIP_CUTOUT_FACTOR),N_INTEGRATION_BLADE)
        chord = self.get_chord(r).get_payload()['chord']
        twist = self.get_twist(r).get_payload()['twist']
        theta = data['pitch'] + twist
        thrust=0
        torque=0
        power=0
        F=0
        M=0
        converged = False
        beta=0
        for i in range(THRUST_CONVERGENCE_ITERATIONS):
            thrust_=thrust
            mu = data['V_inf']*np.cos(data['alpha_tpp'][0]) / (data['omega'] * self.radius)
            C_T = thrust / (data['atmosphere']['density'] / np.pi * (self.radius**2-self.root_cutout**2) * (data['omega']**2) * self.radius**2)
            lambda_i_Glauert = C_T/2/mu
            lambda_G = data['V_inf'] / mu*np.tan(data['alpha_tpp'][0])#(data['omega'] * self.radius) + lambda_i_Glauert
            variable_inflow_coefficient = (4/3*mu/lambda_G)/(1.2+mu/lambda_G)
            lambda_i = lambda_i_Glauert * ( 1 + variable_inflow_coefficient *np.cos(data['phi'])* r / self.radius )
            U_p = data['V_inf'] * np.sin(data['alpha_tpp'][0]) + lambda_i * data['omega'] * self.radius + 0 + data['V_inf'] * np.sin(beta) * np.cos(data['phi'])
            U_t = data['omega'] * r + data['V_inf'] * np.cos(data['alpha_tpp'][0]) * np.sin(data['phi'])

            airfoil_performance = self.airfoil.get_performance(theta - np.arctan(U_p/U_t)).get_payload()
            #print('alpha',np.mean(theta - np.arctan(U_p/U_t)),'Up',np.mean(U_p),'Ut',np.mean(U_t))
            CL = airfoil_performance['CL']
            CD = airfoil_performance['CD']
            CM = airfoil_performance['CM']
            #print('CL',np.mean(CL))
            rho = data['atmosphere']['density']
            cos_phi = np.cos(np.arctan(U_p/U_t))
            sin_phi = np.sin(np.arctan(U_p/U_t))

            # Refer to the diagram in dynamics.py for the coordinate system
            dL = 0.5*rho*(U_p**2 + U_t**2)*chord*CL
            dFz = 0.5*rho*(U_p**2 + U_t**2)*chord*(CL*cos_phi - CD*sin_phi)
            dFtheta = -r*0.5*rho*(U_p**2 + U_t**2)*chord*(CD*cos_phi + CL*sin_phi) # Tangential force. Minus sign becuase it is in the opposite direction

            Ftheta = np.trapz(dFtheta,r)
            Fx = Ftheta*np.cos(data['phi'])
            Fy = Ftheta*np.sin(data['phi'])
            Fz = np.trapz(dFz,r)
            F = np.array([Fx,Fy,Fz])

            Mx = np.trapz(dFz*r,r)*np.cos(data['phi'])  # Pitch up moment is positive
            # dMy needs a minus because position vector is in x-dir and Force vector is in z-dir. Moment is rxF so ixk = -j
            My = np.trapz(-dFz*r*np.sin(data['phi']),r)  # Roll right moment is positive
            Mz = np.trapz(dFtheta*r,r)
            M = np.array([Mx,My,Mz])
        
            thrust = Fz
            torque = -Mz     # Minus because applied torque is in opposite direction
            power = torque*data['omega']
            L=np.trapz(dL,r)
            beta=L/self.mmoi/data['omega']**2
            #print('psi',data['phi'],'lambda_i',np.mean(lambda_i),'thrust',thrust,'beta',beta,'delta_thrust',(thrust-thrust_)/1e-6,'mu',mu)
            if np.allclose(thrust_,thrust,rtol=THRUST_CONVERGENCE_TOLERANCE):
                converged = True
                break
        
        if not converged:
            response.add_warning({'Lift Convergence':'Lift did not converge.'})
            thrust=0
            print(data['phi'])
            #torque=0
            #power=0
            #F=np.array([0,0,0])
            #M=np.array([0,0,0])

        response.add_payload({'thrust':thrust, 'torque':torque, 'power':power, 'forces':F, 'moments':M})

        return response