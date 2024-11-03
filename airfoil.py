#####################################################################################
## THIS PROGRAM READS ANY AIRFOIL DATA AND MAKES IT AVAILABLE FOR OTHER COMPONENTS ##
#####################################################################################

from __init__ import *

class airfoil:

    def __init__(self, airfoil_data_file_path):

        self.airfoil_data_file_path = airfoil_data_file_path
        self.read_airfoil_data()

    def read_airfoil_data(self):

        # airfoil data is in a json file
        with open(self.airfoil_data_file_path) as file:
            raw_data = json.load(file)

        self.name = raw_data['name']
        self.alphacrit = raw_data['alphacrit']
        self.cl_alpha = raw_data['cl_alpha']
        self.alpha = np.array(raw_data['alpha'])
        self.alpha_reverse = np.array(raw_data['alpha_reverse'])
        self.CL = np.array(raw_data['CL'])
        self.CD = np.array(raw_data['CD'])
        self.CM = np.array(raw_data['CM'])
        

    def get_performance(self, alpha: np.ndarray):

        if (np.any(alpha < self.alpha[0]) or np.any(alpha > self.alpha[-1])) and (np.any(alpha > self.alpha_reverse[0]) or np.any(alpha < self.alpha_reverse[-1])):
            response = message.simMessage()
            response.add_error({'UnknownAlpha':f'AoA is outside the range of the airfoil data: {alpha.min()*180/np.pi:.1f} deg'})

        response = message.simMessage()

        if np.any(alpha > 1.57255) and np.any(alpha < 3.1415):
            CL_value =  np.interp(alpha, self.alpha_reverse, -1.0*self.CL)
            response.add_payload({'CL':CL_value})

            CD_value =  np.interp(alpha, self.alpha, self.CD)
            response.add_payload({'CD':CD_value})

            CM_value =  np.interp(alpha, self.alpha, self.CM)
            response.add_payload({'CM':CM_value})
        else:
            CL_value =  np.interp(alpha, self.alpha, self.CL)
            response.add_payload({'CL':CL_value})

            CD_value =  np.interp(alpha, self.alpha, self.CD)
            response.add_payload({'CD':CD_value})

            CM_value =  np.interp(alpha, self.alpha, self.CM)
            response.add_payload({'CM':CM_value})

        if np.any(alpha > self.alphacrit):
            response.add_warning({'Stall':f'Critical AoA exceeded at {alpha.max()*180/np.pi:.1f} deg.'})

        if np.any(alpha > 1.57255) and np.any(alpha < 3.1415):
            response.add_warning({'Reverse Flow':'Reverse Flow'})

        return response