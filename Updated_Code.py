"""
Drone Pricing Model
-------------------
Author: Andrew Todd
Description:
    This script replicates the Excel-based drone and camera pricing model.
    It calculates hull and TPL premiums using Riebesell-style ILFs, applies
    the extensions, and outputs gross and net premiums for each component.
    
    In this update I aim to update the code based on the feedback recieved from
    the development team at HX. The three aims are to:
    (1) breaking code into smaller reusable functions
    (2) adhering to python conventions
    (3) incorporating input validation to enhance robustness and maintainability
"""

#Import math
import math
import pprint

#structing code the same way it will be in the .py file

#define input data structure
def get_example_data():
    """
    Return an example data structure containing the inputs and placeholder outputs for the drone pricing model
    """
    example_data = {
        "insured": "Drones R Us",
        "underwriter": "Michael",
        "broker": "AON",
        "brokerage": 0.3,
        "max_drones_in_air": 2,
        "drones": [
            {
                "serial_number": "AAA-111",
                "value": 10000,
                "weight": "0 - 5kg",
                "has_detachable_camera": True,
                "tpl_limit": 1000000, #set tpl_limit to its numerical value as this is an input variable
                "tpl_excess": 0, #set tpl_excess to its numerical value as this is an input variable
                "hull_base_rate": None,
                "hull_weight_adjustment": None,
                "hull_final_rate": None,
                "hull_premium": None,
                "tpl_base_rate": None,
                "tpl_base_layer_premium": None,
                "tpl_ilf": None,
                "tpl_layer_premium": None
            },
            {
                "serial_number": "BBB-222",
                "value": 12000,
                "weight": "10 - 20kg",
                "has_detachable_camera": False,
                "tpl_limit": 4000000, #set tpl_limit to its numerical value as this is an input variable
                "tpl_excess": 1000000, #set tpl_excess to its numerical value as this is an input variable
                "hull_base_rate": None,
                "hull_weight_adjustment": None,
                "hull_final_rate": None,
                "hull_premium": None,
                "tpl_base_rate": None,
                "tpl_base_layer_premium": None,
                "tpl_ilf": None,
                "tpl_layer_premium": None
            },
            {
                "serial_number": "AAA-123",
                "value": 15000,
                "weight": "5 - 10kg",
                "has_detachable_camera": True,
                "tpl_limit": 5000000, #set tpl_limit to its numerical value as this is an input variable
                "tpl_excess": 5000000, #set tpl_excess to its numerical value as this is an input variable
                "hull_base_rate": None,
                "hull_weight_adjustment": None,
                "hull_final_rate": None,
                "hull_premium": None,
                "tpl_base_rate": None,
                "tpl_base_layer_premium": None,
                "tpl_ilf": None,
                "tpl_layer_premium": None
            }
        ],
        "detachable_cameras": [
            {
                "serial_number": "ZZZ-999",
                "value": 5000,
                "hull_rate": None,
                "hull_premium": None
            },
            {
                "serial_number": "YYY-888",
                "value": 2500,
                "hull_rate": None,
                "hull_premium": None
            },
            {
                "serial_number": "XXX-777",
                "value": 1500,
                "hull_rate": None,
                "hull_premium": None
            },
            {
                "serial_number": "WWW-666",
                "value": 2000,
                "hull_rate": None,
                "hull_premium": None
            }

        ],
        "gross_prem": {
            "drones_hull": None,
            "drones_tpl": None,
            "cameras_hull": None,
            "total": None
        },
        "net_prem": {
            "drones_hull": None,
            "drones_tpl": None,
            "cameras_hull": None,
            "total": None
        }
    }

    return example_data

# Validation functions

def validate_drone(drone: dict):
    
    #Checking all required data is available
    required = ['value','weight', 'tpl_limit', 'tpl_excess']
    
    for key in required:
        if key not in drone:
            raise KeyError(f"Missing Key '{key}' in drone data")
        
        #completing type checks which raise errors if weight is not
        #string tpye or if value, tpl_limit and tpl_excess are not numeric
        if key == 'weight': 
            if not isinstance(drone[key], str):
                raise TypeError("Drone field 'weight' must be a string")
        
        else:
            if not isinstance(drone[key], (int, float)):
                raise TypeError(f"Drone field '{key}' must be numeric")
                
        #Field specific validation (confirm with hx)
        if drone['value'] < 0:
            raise ValueError("Drone value must be positive")

#Set up functions to be used in the main

def ilf(x, base_limit, z) -> float:
    """
    Compute ILF(x).
    
    Parameters:
    x = the input eithet limit + excess or excess
    base_limit = the base limit defined in the parameters given
    z = the surcharged defined in the parameters given
    """
    ilf_core = (x/base_limit) 
    ilf_power = math.log2(1+z)
    ilfx = ilf_core ** ilf_power
    return ilfx

def ilf_layer(limit, excess, base_limit, z) -> float:
    """
    Compute ILF layer.
    
    Parameters:
    limit = tpl_limit given in the input data
    excess = tpl_excess given in the input data
    base_limit = the base limit defined in the parameters given
    z = the surcharged defined in the parameters given
    """
    limit_excess = limit + excess
    ilf_limit_excess = ilf(limit_excess, base_limit, z)
    ilf_excess = ilf(excess, base_limit, z)
    layer_ilf = ilf_limit_excess - ilf_excess
    return layer_ilf

# Firstly I will write the function calculate_hull_premium and then the function to 
# calculate_tpl_premium. This will mirror section (1) in the main code below

def calculate_hull_premium(drone: dict, hull_base_rate: float, weight_adj_table: dict) -> None:
    """
    Compute Drone Hull Premium.
    
    Parameters:
    drone = drone dictionaries from get_example_data
    hull_base_rate = base rate provided in parameters
    weight_adj_table = table of drone weights and their corresponding weight adjustment values
    """
    #validate inputs
    validate_drone(drone)
    #add base rate
    drone['hull_base_rate'] = hull_base_rate
    #add weight adjustments by mapping from table
    drone['hull_weight_adjustment'] = weight_adj_table.get(drone['weight'], 1)
    #calculate final rate
    drone['hull_final_rate'] = drone['hull_base_rate'] * drone['hull_weight_adjustment']
    #calculate hull premium
    drone['hull_premium'] = drone['value'] * drone['hull_final_rate']


def calculate_tpl_premium(drone: dict, tpl_base_rate: float, base_limit: float, z: float) -> None:
    """
    Compute TPL Premium.
    
    Parameters:
    drone = drone dictionaries from get_example_data
    tpl_base_rate = base rate provided in parameters
    base_limit = base_limit provided in parameters
    z = z provided in parameters
    """
    #validate inputs
    validate_drone(drone)
    #add base rate
    drone['tpl_base_rate'] = tpl_base_rate
    #calculate tpl_base_layer_premium
    drone['tpl_base_layer_premium'] = drone['tpl_base_rate'] * drone['value']
    #calculate ilf
    drone['tpl_ilf'] = ilf_layer(drone['tpl_limit'],drone['tpl_excess'], base_limit, z)
    #calcualte tpl_layer_premium
    drone['tpl_layer_premium'] = drone['tpl_base_layer_premium'] * drone['tpl_ilf']
        
# Now I will write a function for calculating section 2 in the main code below which relates
# to calculating camera premiums


def get_max_hull_rate(drones: list) -> float:
    """
    Loop through the list of dictionaries and identify the max hull rate for drones that have detachable cameras.
    
    Parameters:
    drones = list of drone dictionaries
    """
    max_rate = None
    for d in drones:
        if d['has_detachable_camera'] == True:
            if max_rate is None or d['hull_final_rate'] > max_rate:
                max_rate = d['hull_final_rate']
    return max_rate
            

def calculate_camera_premium(detachable_cameras: list, max_hull_rate: float) -> None:
    """
    Compute camera hull premium.
    
    Parameters:
    detachable_cameras = list of camera dictionaries
    """
    for camera in detachable_cameras:
        camera['hull_rate'] = max_hull_rate
        camera['hull_premium'] = camera['value'] * camera['hull_rate']


# Now I will write a function for section 3 in the main code - applying extensions

def applying_extensions(data: dict) -> None:
    """
    Implement the extensions provided in the word document provided by HX.
    
    Parameters:
    data = full data dictionary
    """
    
    max_drones = data['max_drones_in_air']
    
    #sort values based on hull premiums
    sorted_drones = sorted(data['drones'], key = lambda d: d['hull_premium'], reverse=True)
    #now loop through sorted_drones keeping highest premiums for n drones and setting rest to 50
    for i, drone in enumerate(sorted_drones): #enumerate adds a index to the iterable list so we can do anything >= 2 ==150
        if i >= max_drones:
            drone['adjusted_hull_premium'] = 150 #flat rate
        else:
            drone['adjusted_hull_premium'] = drone['hull_premium']
            
    # (3)(ii) Applying the extensions for cameras. 
    #If there is more cameras than drones charge the full rate for n camers     with the highest values
    # and charge a flat rate for the remaning n of 50
    #first identify if there are more cameras than drones
    if len(data['detachable_cameras']) > len(data['drones']):
        sorted_cameras = sorted(data['detachable_cameras'], key = lambda c: c['value'], reverse = True)
        for i, cam in enumerate(sorted_cameras):
            if i >= max_drones:
                cam['adjusted_hull_premium'] = 50
            else:
                cam['adjusted_hull_premium'] = cam['hull_premium']
    
    else:
        for cam in data['detachable_cameras']:
            cam['adjusted_hull_premium'] = cam['hull_premium']
            

def main():
    # 
    data = get_example_data()
    
    ##Adding Parameters
    
    #hull_rates based on weughts
    weight_adj_table = {"0 - 5kg": 1, "5 - 10kg": 1.2, "10 - 20kg": 1.6, "> 20kg": 2.5}
    #base rates
    hull_base_rate = 0.06
    tpl_base_rate = 0.02
    #base_limit and z
    base_limit = 1000000
    z = 0.2
    
    
    # (1) Calculating drone hull + tpl premiums
    
    for drone in data['drones']:
        calculate_hull_premium(drone, hull_base_rate, weight_adj_table)
        calculate_tpl_premium(drone, tpl_base_rate, base_limit, z)
          
    
    # (2) Calculating camera premiums
    
    max_rate = get_max_hull_rate(data['drones'])
    calculate_camera_premium(data['detachable_cameras'], max_rate)
    
  
    # (3) Applying extensions
        
    applying_extensions(data)
            
    
    # (4) Calculating net and gross premiums
        
    #sum together net premiums
    data['net_prem']['drones_hull'] = sum(d['adjusted_hull_premium'] for d in data['drones'])
    data['net_prem']['drones_tpl'] = sum(d['tpl_layer_premium'] for d in data['drones'])
    data['net_prem']['cameras_hull'] =  sum(c['adjusted_hull_premium'] for c in data['detachable_cameras'])
    data['net_prem']['total'] = data['net_prem']['drones_hull'] + data['net_prem']['drones_tpl'] +data['net_prem']['cameras_hull']
    
    #calculate gross premiums
    brokerage = data['brokerage']
    
    data['gross_prem']['drones_hull'] = data['net_prem']['drones_hull'] / (1-brokerage)
    data['gross_prem']['drones_tpl'] = data['net_prem']['drones_tpl'] / (1-brokerage)
    data['gross_prem']['cameras_hull'] = data['net_prem']['cameras_hull'] / (1-brokerage)
    data['gross_prem']['total'] = data['gross_prem']['drones_hull'] + data['gross_prem']['drones_tpl'] + data['gross_prem']['cameras_hull']
    
    
    return data
                                                                                                       
# Execute model and print results
                                                                                                       
if __name__ == "__main__":
    result = main()
    pprint.pprint(result)
                                                                                                       



