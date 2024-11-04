from __init__ import *

class mission:

    def __init__(self, mission_data_file,heli_file_path,fbd_file_path):
            self.heli_file_path=heli_file_path
            self.mission_data_file = mission_data_file
            self.fbd_file_path=fbd_file_path
            self.engine = powerplant.powerplant()
            with open(self.heli_file_path, 'r' ) as heli_file_path:
                self.heli_data = json.load( heli_file_path )

            self.mission_log = {'timestamp':[],
                           'gross_weight':[],
                           'fuel_weight':[],
                           'fuel_burn_rate':[],
                           'altitude':[],
                           'power_required':[],
                           'power_available':[],
                           'airspeed':[],
                           'groundspeed':[],
                           'climb_rate':[],
                           'distance_covered':[]}
            
            self.read_mission_data()

    # Reads the mission data from input JSON file
    def read_mission_data(self):
          
        with open(self.mission_data_file) as file:
            raw_data = json.load(file)

        self.temp_dev_isa = raw_data["temp_dev_isa"]
        self.fuel_mass = raw_data["fuel"]  # Stores the fuel mass in operation
        self.flight_segments = maneuver.create_maneuvers(raw_data["mission_phases"])
        self.dry_mass = 0
        self.altitude = 0  # Stores current altitude in operation
        self.timestamp = 0 # Time since mission started
        self.distance_travelled = 0
        self.atmosphere = atmosphere.ISA(self.temp_dev_isa)
        self.fbd = dynamics.FBD(self.fbd_file_path)
        self.main_rotor = rotor.rotor(self.heli_data['main_rotor_path'])
        self.tail_rotor = rotor.rotor(self.heli_data['tail_rotor_path'])

    def endurance(self):
        total_mass=self.heli_data['dry_mass']+self.heli_data['payload_mass']+self.heli_data['fuel_mass']
        vehicle_state={'mass':total_mass,'drag_area':self.heli_data['flat_plate_area'],'main_rotor':self.main_rotor,
                                   'tail_rotor':self.tail_rotor,'fbd':self.fbd}
        fuel_burn_rate=self.flight_segments.get_fuel_burn_rate(vehicle_state)
        return self.heli_data['fuel_mass']/fuel_burn_rate

mis=mission("input_files/mission_A.json","input_files/heli.json","input_files/fbd.json")
mis.read_mission_data()


common_input = message.simMessage()
common_input.add_payload({ 'drag_area':mis.heli_data['flat_plate_area'],
                         'temp_dev_isa':mis.temp_dev_isa,
                       'main_rotor':mis.main_rotor,
                       'tail_rotor':mis.tail_rotor,
                       'powerplant':mis.engine,
                       'fbd':mis.fbd})

segments_done = 0

for segment in mis.flight_segments:

    time_left = segment.time_taken
    mis.dry_mass = segment.dry_mass
    mis.altitude = segment.altitude
    dt = 0

    while time_left >= 0:
        
        inst_input = message.simMessage()
        inst_input.add_payload({'mass':mis.dry_mass + mis.fuel_mass,
                        'V_inf':segment.V_inf,
                        'altitude':mis.altitude,
                        'climb_vel':segment.climb_vel,
                        'atmosphere':mis.atmosphere.get_atmosphere(mis.altitude).get_payload()})
        input = inst_input + common_input
        performance_result = segment.get_fuel_burn_rate(input).get_payload()

        # Updatin all the parameters
        mis.timestamp += dt
        mis.fuel_mass -= performance_result['fuel_burn_rate'] * dt
        mis.altitude += segment.climb_vel * dt
        mis.distance_travelled += (segment.V_inf - segment.headwind) * dt

        # Log all the mission parameters
        mis.mission_log['timestamp'].append(mis.timestamp)
        mis.mission_log['gross_weight'].append(mis.dry_mass + mis.fuel_mass)
        mis.mission_log['fuel_weight'].append(mis.fuel_mass)
        mis.mission_log['fuel_burn_rate'].append(performance_result['fuel_burn_rate'])
        mis.mission_log['altitude'].append(mis.altitude)
        mis.mission_log['power_required'].append(performance_result['power_required'])
        mis.mission_log['power_available'].append(performance_result['power_available'])
        mis.mission_log['airspeed'].append(segment.V_inf)
        mis.mission_log['groundspeed'].append(segment.V_inf - segment.headwind)
        mis.mission_log['climb_rate'].append(segment.climb_vel)
        mis.mission_log['distance_covered'].append(mis.distance_travelled)

        if time_left == 0:
            break
        time_left -= dt
        dt = min(MISSION_TIME_STEP, time_left)

    segments_done += 1
    print(f"segment {segments_done} of {len(mis.flight_segments)} completed")

# write the results to a file
with open('output_files/mission_A_results.json', 'w') as file:
    json.dump(mis.mission_log, file)