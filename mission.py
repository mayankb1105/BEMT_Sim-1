from __init__ import *

class mission:

    def __init__(self, mission_data_file):
            
            self.mission_data_file = mission_data_file
            self.read_mission_data()

    # Reads the mission data from input JSON file
    def read_mission_data(self):
          
        with open(self.mission_data_file) as file:
            raw_data = json.load(file)

        self.temp_dev_isa = np.array(raw_data["temp_dev_isa"])
        self.flight_segments = maneuver.create_maneuvers(raw_data["flight_segments"])

    def
