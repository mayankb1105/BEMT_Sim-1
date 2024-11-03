from __init__ import *
import time

a=rotor.rotor("input_files/main_rotor.json")
tr = rotor.rotor("input_files/tail_rotor.json")
atmos = {'temperature': 15, 'pressure': 101325, 'density': 1.225}
thrust = np.sqrt((150*9.81)**2 + (150)**2)
message.simMessage.warnings_suprressed = True
rotor_inp = message.simMessage(payload={'mass':450,'thrust':thrust,'drag_area':0.3,'lateral_force':0,'atmosphere':atmos,'beta_0':3.485*3.14/180,
                                                            'cyclic_c':0.33*3.14/180,'cyclic_s':-2.21389*3.14/180,'collective':5.1*3.14/180,
                                                            'tpp_angle':np.array([np.arctan(1/9.81),0]),
                                                            "V_inf":30,'climb_vel':0,'headwind':0,'crosswind':0})
# rotor_result = a.get_performance_forward_flight(rotor_inp)
# print(rotor_result.get_payload())
t1 = time.time()
rotor_result = a.set_trim_forward_flight(rotor_inp,dynamics.FBD('input_files/fbd.json'),tr).get_payload()
t2 = time.time()
print('Controls:')
print(f'Collective:{rotor_result['controls']["collective"]*180/np.pi:.2f}')
print(f'Cyclics: {rotor_result['controls']["cyclic_c"]*180/np.pi:.2f} and {rotor_result['controls']["cyclic_s"]*180/np.pi:.2f}')
print(f'Tail Rotor Collective: {rotor_result['controls']["tr_collective"]*180/np.pi:.2f}')
print(f'Total Power: {(rotor_result["mr_performance"]['power']/1000 + rotor_result['tr_performance']['power']/1000):.2f} kW')

print(f'Time taken: {(t2-t1)*1000} ms')
# conv = a.solve_control_forward_flight(rotor_inp, 'beta_0', 0, 'coning_moment', initial_guess = 2*3.14/180)
# print(conv.get_payload()['beta_0']*180/np.pi)








# c=a.set_collectives_forward_flight(b)
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