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
    def get_performance(self, msg: message.simMessage):
         
        data = msg.get_payload()
        
        r = np.linspace(self.root_cutout,self.radius,N_INTEGRATION_BLADE)
        chord = self.get_chord(r).get_payload()['chord']
        twist = self.get_twist(r).get_payload()['twist']
        theta = data['pitch'] + twist

        lambda_c = data['climb_vel']/data['omega']/self.radius
        sigma = data['number_of_blades']*chord/(2*np.pi*r)
        coeff = sigma*self.airfoil.cl_alpha/16 - lambda_c/2
        lambda_ = (coeff**2 + sigma*self.airfoil.cl_alpha*theta*r/self.radius/8)**0.5 - coeff

        U_p = lambda_ * data['omega'] * r
        U_t = data['h_vel'] + data['omega']*r
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
        torque = np.trapz(dQ,r)
        power = torque*data['omega']

        non_dims = {}
        non_dims['CT'] = 2 * thrust / (rho * data['number_of_blades'] * np.pi * self.radius**4 * data['omega']**2)
        non_dims['sigma'] = data['number_of_blades']*chord[0]*(self.radius-self.root_cutout)/(np.pi*self.radius**2)

        response = message.simMessage()
        response.add_payload({'thrust':thrust, 'torque':torque, 'power':power})
        response.add_payload({'non_dims':non_dims})

        return response
        
             
                     

