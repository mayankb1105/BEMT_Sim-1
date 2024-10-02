from __init__ import *
import time

atmos = {'temperature': 15, 'pressure': 101325, 'density': 1.225}
rot = rotor.rotor('input_files/simple_rotor.json')
blade_inp = {'climb_vel': 0, 'atmosphere': atmos,'mass':200, 'desired_thrust': 2000,'control_limits':{'min_collective':0,'max_collective':20*3.14159/180}}
msg = message.simMessage()
t1 = time.time()
msg.add_payload(blade_inp)
print(rot.set_thrust(msg).get_payload())
t2 = time.time()
print(f'Time taken: {(t2-t1)*1000} ms')