from __init__ import *

#             ^  z-axis
#             |
#             |
#  y-axis     |
#   <---------+ 
# 
#                                 ____
#      ===========================|MR|====================================
#                                 |  |                                                           _____
#                   ______________|  |________________                                          /    |
#                  /    /                             \                                        /     |
#                 /    /                               \______________________________________/  TR  |
#           _____/____/                CG               _____________________________________________|
#          /                                           /
#         <___________________________________________/ 
#                 ||  ||                  ||  ||
#               ==||======================||=========  
#            ===================================


# This class calculates the accelerations of the helicopter from forces and moments
class FBD:

    def __init__( self, fbd_data_file_path ):

        self.fbd_data_file_path = fbd_data_file_path
        self.position = np.array([0,0,0])
        self.velocity = np.array([0,0,0])
        self.acceleration = np.array([0,0,0])
        self.attitude = np.array([0,0,0])
        self.angular_velocity = np.array([0,0,0])
        self.angular_acceleration = np.array([0,0,0])
        self.mr_position = np.array([0,0,0])
        self.tr_position = np.array([0,0,0])
        self.cg_position = np.array([0,0,0])

        self.read_fbd_data()

    def read_fbd_data( self ):

        with open( self.fbd_data_file_path, 'r' ) as fbd_data_file:
            fbd_data = json.load( fbd_data_file )

        self.mass = fbd_data['mass']
        self.mr_position = np.array( fbd_data['mr_position'] )
        self.tr_position = np.array( fbd_data['tr_position'] )
        self.cg_position = np.array( fbd_data['cg_position'] )
        self.gravity = np.array( fbd_data['gravity'] )

    def get_mr_position( self ):
        return self.mr_position
    
    def get_tr_position( self ):
        return self.tr_position
    
    def get_cg_position( self ):
        return self.cg_position