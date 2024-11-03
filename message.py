################################################################################################
## THIS PROGRAM CONTAINS FUNCTIONS TO CREATE AND PARSE MESSAGES SENT BY SIMULATION COMPONENTS ##
################################################################################################

from __init__ import *


# To create a message object that can be passed between simulation components
# Payload Eg. Lift and Drag from airfoil, Thrust from rotor
# Warnings Eg. Stall warning, Tip overspeed warning
# Errors Eg. Crash, Overload

class simMessage:

    warnings_suprressed = True
    errors_suprressed = False    

    def __init__ (self, **kwargs):

        self.payload = {}
        self.warnings = {}
        self.errors = {}

        try:
            self.payload.update(kwargs.get('payload', None))
        except TypeError:
            pass

        try:
            self.warnings.update(kwargs.get('warnings', None))
        except TypeError:
            pass

        try:
            self.errors.update(kwargs.get('errors', None))
        except TypeError:
            pass

    def add_payload(self, payload_dict):
        self.payload.update(payload_dict)

    def add_warning(self, warning_dict):
        self.warnings.update(warning_dict)

    def add_error(self, error_dict):        
        self.errors.update(error_dict)

    def get_payload(self, suppress_warnings = warnings_suprressed, suppress_errors = errors_suprressed):

        if not suppress_warnings:
            for key, value in self.warnings.items():
                print(f'\33[33mWarning: {key} : {value}\33[0m')

        if not suppress_errors:
            for key, value in self.errors.items():
                raise Exception(f'\33[31mError: {key} : {value}\33[0m')

        return self.payload
    
    def get_warnings(self, suppress_errors = errors_suprressed):
        if not suppress_errors:
            for key, value in self.errors.items():
                raise Exception(f'\33[31mError: {key} : {value}\33[0m')
        return self.warnings
    
    def get_errors(self):
        return self.errors
    
    def __add__(self, message2):
        
        payload = {**self.payload, **message2.payload}
        warnings = {**self.warnings, **message2.warnings}
        errors = {**self.errors, **message2.errors}
        
        return simMessage(payload = payload, warnings = warnings, errors = errors)