from __init__ import *

class mission:

    def __init__(self, mission_data_file,heli_file_path,fbd_file_path):
            self.heli_file_path=heli_file_path
            self.mission_data_file = mission_data_file
            self.fbd_file_path=fbd_file_path
            with open(self.heli_file_path, 'r' ) as heli_file_path:
                self.heli_data = json.load( heli_file_path )
            
            self.read_mission_data()

    # Reads the mission data from input JSON file
    def read_mission_data(self):
          
        with open(self.mission_data_file) as file:
            raw_data = json.load(file)

        self.temp_dev_isa = np.array(raw_data["temp_dev_isa"])
        self.fuel_mass = raw_data["fuel_mass"]
        self.flight_segments = maneuver.create_maneuvers(raw_data["mission_phases"])

    def endurance(self):
        fbd=dynamics.FBD(self.fbd_file_path)
        total_mass=self.heli_data['dry_mass']+self.heli_data['payload_mass']+self.heli_data['fuel_mass']
        vehicle_state={'mass':total_mass,'drag_area':self.heli_data['flat_plate_area'],'main_rotor':rotor.rotor(self.heli_data['main_rotor_path']),
                                   'tail_rotor':rotor.rotor(self.heli_data['tail_rotor_path']),'fbd':fbd}
        fuel_burn_rate=self.flight_segments.get_fuel_burn_rate(vehicle_state)
        return self.heli_data['fuel_mass']/fuel_burn_rate

mis=mission("input_files/mission.json","input_files/heli.json","input_files/fbd.json")
mis.read_mission_data()
print(mis.flight_segments)