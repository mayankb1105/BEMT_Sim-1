import numpy as np
from __init__ import *

# Class to handle data generation
class SimulationData:
    def __init__(self,heli_file_path,fbd_file_path,V_inf,beta_0,altitude):
        with open(heli_file_path, 'r' ) as heli_file_path:
            self.heli_data = json.load( heli_file_path )
        self.main_rotor_path=self.heli_data['main_rotor_path']
        self.tail_rotor_path=self.heli_data['tail_rotor_path']
        self.fbd=dynamics.FBD(fbd_file_path)
        self.V_inf=V_inf
        self.beta_0=beta_0
        self.altitude=altitude

    def get_forces(self, collective_pitch, lateral_pitch, longitudinal_pitch, tail_rotor_collective):
        collective_pitch=collective_pitch*np.pi/180
        lateral_pitch=lateral_pitch*np.pi/180
        longitudinal_pitch=longitudinal_pitch*np.pi/180
        tail_rotor_collective=tail_rotor_collective*np.pi/180
        atmos=atmosphere.ISA()
        atmos=atmos.get_atmosphere(self.altitude).get_payload()
        #atmos = {'temperature': 15, 'pressure': 101325, 'density': 1.225}
        main_rot=rotor.rotor(self.main_rotor_path)
        tail_rot=rotor.rotor(self.tail_rotor_path)
        drag=0.5*self.heli_data['flat_plate_area']*atmos['density']*self.V_inf**2
        weight=(self.heli_data['dry_mass']+self.heli_data['payload_mass']+self.heli_data['fuel_mass'])*g
        alpha_tpp=np.arctan(drag/weight)
        thrust=(drag**2+weight**2)**0.5
        input_data={'climb_vel': 0, 'atmosphere': atmos,'mass':weight/g, 'thrust': thrust,'control_limits':{'min_collective':0,'max_collective':20*3.14159/180},
                    'headwind':0,'crosswind':0,'V_inf':self.V_inf,
                    'lateral_force':0,'total_drag':drag,
                    'collective':collective_pitch,'cyclic_c':longitudinal_pitch,'cyclic_s':lateral_pitch,'beta_0':self.beta_0}
        msg = message.simMessage()
        msg.add_payload(input_data)
        main_forces=main_rot.get_performance_forward_flight(msg).get_payload()
        tail_forces=tail_rot.get_performance(message.simMessage(payload={'collective':tail_rotor_collective,'atmosphere':atmos,'climb_vel':0,'headwind':0,'crosswind':0}))
        Fx=main_forces['forces'][0]+tail_forces.get_payload()['thrust']
        Fy_=main_forces['forces'][1]
        Fz_=main_forces['forces'][2]
        Fy=Fy_*np.cos(alpha_tpp)+Fz_*np.sin(alpha_tpp)
        Fz=Fz_*np.cos(alpha_tpp)-Fy*np.sin(alpha_tpp)
        Mx=main_forces['moments'][0]
        My=main_forces['moments'][0]
        Mz=main_forces['moments'][0]+tail_forces.get_payload()['thrust']*self.fbd.get_tr_position()[1]
        print('Power Available',(86500-tail_forces.get_payload()['power']-main_forces['power']))
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

#sim_data = SimulationData('input_files/heli.json','input_files/fbd.json',14,0.2,2000)
#print(sim_data.generate_forces_xyz(48,0,10,17))
#print(sim_data.generate_moments_xyz(60,20,0,0))