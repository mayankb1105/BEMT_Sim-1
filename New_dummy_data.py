import numpy as np
from __init__ import *

# Class to handle data generation
class SimulationData:
    def __init__(self,heli_file_path,fbd_file_path,V_inf,beta_0):
        with open(heli_file_path, 'r' ) as heli_file_path:
            self.heli_data = json.load( heli_file_path )
        self.main_rotor_path=self.heli_data['main_rotor_path']
        self.tail_rotor_path=self.heli_data['tail_rotor_path']
        self.fbd=dynamics.FBD(fbd_file_path)
        self.V_inf=V_inf
        self.beta_0=beta_0

    def get_forces(self, collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective):
        atmos = {'temperature': 15, 'pressure': 101325, 'density': 1.225}
        main_rot=rotor.rotor(self.main_rotor_path)
        tail_rot=rotor.rotor(self.tail_rotor_path)
        drag=0.5*self.heli_data['flat_plate_area']*atmos['density']*self.V_inf**2
        weight=(self.heli_data['dry_mass']+self.heli_data['payload_mass']+self.heli_data['fuel_mass'])*g
        thrust=(drag**2+weight**2)**0.5
        input_data={'climb_vel': 0, 'atmosphere': atmos,'mass':200, 'thrust': thrust,'control_limits':{'min_collective':0,'max_collective':20*3.14159/180},
                    'headwind':0,'crosswind':0,'V_inf':self.V_inf,
                    'lateral_force':0,'total_drag':drag,
                    'collective':collective_pitch,'cyclic_c':longitudinal_pitch,'cyclic_s':lateral_pitch,'beta_0':self.beta_0}
        msg = message.simMessage()
        msg.add_payload(input_data)
        main_forces=main_rot.get_performance_forward_flight(msg).get_payload()
        tail_forces=tail_rot.get_performance(message.simMessage(payload={'collective':tail_rotor_collective,'atmosphere':atmos,'climb_vel':0,'headwind':0,'crosswind':0}))
        Fx=main_forces['forces'][0]-tail_forces.get_payload()['thrust']
        Fy=main_forces['forces'][1]
        Fz=main_forces['forces'][2]
        Mx=main_forces['moments'][0]
        My=main_forces['moments'][0]
        Mz=main_forces['moments'][0]+tail_forces.get_payload()['thrust']*self.fbd.get_tr_position()
        return [Fx,Fy,Fz,Mx,My,Mz]
    # Functions to generate forces data
    def generate_forces_x(self, collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective):
        x=np.linspace(0,1,2)
        y=np.ones(2)
        res=self.get_forces(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        return x,y*res[0]

    def generate_forces_y(self, collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective):
        x=np.linspace(0,1,2)
        y=np.ones(2)
        res=self.get_forces(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        return x,y*res[1]

    def generate_forces_z(self, collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective):
        x=np.linspace(0,1,2)
        y=np.ones(2)
        res=self.get_forces(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        return x,y*res[2]

    def generate_forces_xyz(self, collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective):
        x=np.linspace(0,1,2)
        y=np.ones(2)
        res=self.get_forces(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        return x,y*res[0],y*res[1],y*res[2]

    # Functions to generate moments data
    def generate_moments_x(self, collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective):
        x=np.linspace(0,1,2)
        y=np.ones(2)
        res=self.get_forces(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        return x,y*res[3]

    def generate_moments_y(self, collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective):
        x=np.linspace(0,1,2)
        y=np.ones(2)
        res=self.get_forces(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        return x,y*res[4]

    def generate_moments_z(self, collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective):
        x=np.linspace(0,1,2)
        y=np.ones(2)
        res=self.get_forces(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        return x,y*res[5]

    def generate_moments_xyz(self, collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective):
        x=np.linspace(0,1,2)
        y=np.ones(2)
        res=self.get_forces(collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective)
        return x,y*res[3],y*res[4],y*res[5]

