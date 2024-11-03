from __init__ import *

class mission:

    def __init__(self, mission_data_file,heli_file_path,fbd_file_path):
            self.heli_file_path=heli_file_path
            self.mission_data_file = mission_data_file
            self.fbd_file_path=fbd_file_path
            self.engine = powerplant.powerplant()
            with open(self.heli_file_path, 'r' ) as heli_file_path:
                self.heli_data = json.load( heli_file_path )
            
            self.read_mission_data()

    # Reads the mission data from input JSON file
    def read_mission_data(self):
          
        with open(self.mission_data_file) as file:
            raw_data = json.load(file)

        self.temp_dev_isa = raw_data["temp_dev_isa"]
        self.fuel_mass = raw_data["fuel_mass"]
        self.flight_segments = maneuver.create_maneuvers(raw_data["mission_phases"])
        self.fbd = dynamics.FBD(self.fbd_file_path)
        self.main_rotor = rotor.rotor(self.heli_data['main_rotor_path'])
        self.tail_rotor = rotor.rotor(self.heli_data['tail_rotor_path'])

    def endurance(self):
        total_mass=self.heli_data['dry_mass']+self.heli_data['payload_mass']+self.heli_data['fuel_mass']
        vehicle_state={'mass':total_mass,'drag_area':self.heli_data['flat_plate_area'],'main_rotor':self.main_rotor,
                                   'tail_rotor':self.tail_rotor,'fbd':self.fbd}
        fuel_burn_rate=self.flight_segments.get_fuel_burn_rate(vehicle_state)
        return self.heli_data['fuel_mass']/fuel_burn_rate

mis=mission("input_files/mission_data.json","input_files/heli.json","input_files/fbd.json")
mis.read_mission_data()

timestamp = [0]
gross_weight = [mis.flight_segments[0].dry_mass + mis.fuel_mass]
fuel_weight = [mis.fuel_mass]
fuel_burn_rate = [0]
altitude = [mis.flight_segments[0].altitude]
power_required = [0]
power_available = [0]
airspeed = [mis.flight_segments[0].parameters['V_inf']]
climb_rate = [mis.flight_segments[0].parameters['climb_vel']]
distance_covered = [0]


basic_input = message.simMessage()
basic_input.add_payload({ 'drag_area':mis.heli_data['flat_plate_area'],
                         'temp_dev_isa':mis.temp_dev_isa,
                       'main_rotor':mis.main_rotor,
                       'tail_rotor':mis.tail_rotor,
                       'powerplant':mis.engine,
                       'fbd':mis.fbd})

segments_done = 0

for segment in mis.flight_segments:

    for t in range(int(segment.parameters['time_taken'] / 60)):
         
        input = message.simMessage()
        input.add_payload({'mass':segment.dry_mass + mis.fuel_mass,
                        'V_inf':segment.parameters['V_inf'],
                        'climb_vel':segment.parameters['climb_vel']})
        
        input = input + basic_input
        segment.altitude -= segment.climb_vel*t*60
        result = segment.get_fuel_burn_rate(input).get_payload()

        mis.fuel_mass -= result['fuel_burn_rate']*60
        timestamp.append(timestamp[-1] + 60)
        gross_weight.append(segment.dry_mass + mis.fuel_mass)
        fuel_weight.append(mis.fuel_mass)
        fuel_burn_rate.append(result['fuel_burn_rate'])
        altitude.append(segment.altitude - segment.climb_vel*t*60)
        power_required.append(result['power_required'])
        power_available.append(result['power_available'])
        airspeed.append(segment.parameters['V_inf'])
        climb_rate.append(segment.parameters['climb_vel'])
        distance_covered.append(distance_covered[-1] + segment.parameters['V_inf']*60) # Headwind is now availble in segment parameters ADD ITTTTT!!!!!

    segments_done += 1
    print(f"segment {segments_done} of {len(mis.flight_segments)} completed")

# write the results to a file
with open('output_files/mission_results.json', 'w') as file:
    json.dump({'timestamp':timestamp, 'gross_weight':gross_weight, 'fuel_weight':fuel_weight, 'fuel_burn_rate':fuel_burn_rate,
               'altitude':altitude, 'power_required':power_required, 'power_available':power_available,
               'airspeed':airspeed, 'climb_rate':climb_rate, 'distance_covered':distance_covered}, file)

plt.figure()
plt.plot(timestamp, gross_weight, label='Gross Weight')
plt.plot(timestamp, fuel_weight, label='Fuel Weight')
plt.xlabel('Time (s)')
plt.ylabel('Weight (kg)')
plt.legend()
plt.grid()

# power required and power available
plt.figure()
plt.plot(timestamp, power_required, label='Power Required')
plt.plot(timestamp, power_available, label='Power Available')
plt.xlabel('Time (s)')
plt.ylabel('Power (W)')
plt.legend()
plt.grid()

# altitude and airspeed
plt.figure()
plt.plot(timestamp, altitude, label='Altitude')
plt.plot(timestamp, airspeed, label='Airspeed')
plt.xlabel('Time (s)')
plt.ylabel('Altitude (m) / Airspeed (m/s)')
plt.legend()
plt.grid()

# climb rate
plt.figure()
plt.plot(timestamp, climb_rate, label='Climb Rate')
plt.xlabel('Time (s)')
plt.ylabel('Climb Rate (m/s)')
plt.legend()
plt.grid()

plt.show()