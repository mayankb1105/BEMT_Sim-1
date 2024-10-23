from __init__ import *
import time

a=rotor.rotor("input_files/main_rotor.json")
atmos = {'temperature': 15, 'pressure': 101325, 'density': 1.225}
b = message.simMessage(payload={'mass':150,'total_drag':50,'lateral_force':0,'atmosphere':atmos,
                                                            'cyclic_c':0.01,'cyclic_s':0,'collective':0.15,
                                                            "V_inf":1,'climb_vel':0,'headwind':0,'crosswind':0})
c=a.set_collectives_forward_flight(b)
#d=a.get_performance(b)
#beta=c.get_payload()['beta']
#beta_0=np.mean(beta)
#beta_1c=beta_0-beta[36]
#print(c.get_payload()['thrust'],c.get_payload()['power'])
#plt.plot(np.linspace(0,360,72),beta)
#plt.show()

#atmos = {'temperature': 15, 'pressure': 101325, 'density': 1.225}
#rot = rotor.rotor('input_files/simple_rotor.json')
#blade_inp = {'climb_vel': 0, 'atmosphere': atmos,'mass':200, 'desired_thrust': 20,'control_limits':{'min_collective':0,'max_collective':20*3.14159/180},
#             'headwind':0,'crosswind':0}
#msg = message.simMessage()
#t1 = time.time()
#msg.add_payload(blade_inp)
#print(rot.set_thrust(msg).get_payload())
#t2 = time.time()
#print(f'Time taken: {(t2-t1)*1000} ms')


#rot=rotor.rotor('input_files/simple_rotor.json')
#input_data={'climb_vel': 0, 'atmosphere': atmos,'mass':200, 'thrust': 20,'control_limits':{'min_collective':0,'max_collective':20*3.14159/180},
#             'headwind':0,'crosswind':0,'V_inf':0
#             , 'lateral_force':0,'total_drag':1,'collective':0.1,'cyclic_c':0,'cyclic_s':0}#,'beta_0':0.002}
#msg = message.simMessage()
#t1 = time.time()
#msg.add_payload(input_data)
#print(rot.get_performance_forward_flight(msg).get_payload())
#t2 = time.time()
#print(f'Time taken: {(t2-t1)*1000} ms')