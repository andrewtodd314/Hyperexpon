#!/usr/bin/env python
# coding: utf-

"""
Drone Pricing Model
-------------------
Author: Andrew Todd
Description:
    This script replicates the Excel-based drone and camera pricing model.
    It calculates hull and TPL premiums using Riebesell-style ILFs, applies
    the extensions, and outputs gross and net premiums for each component.
"""

#Import math
import math

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

#create an algorithm that replicates the excel file
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
    
    #adding in a IFL function   
    def ilf(x, base_limit, z):
        """
        Compute ILF(x)
        parameters:
        x = the input eithet limit + excess or excess
        base_limit = the base limit defined in the parameters given
        z = the surcharged defined in the parameters given
        """
        ilf_core = (x/base_limit) 
        ilf_power = math.log2(1+z)
        ilfx = ilf_core ** ilf_power
        return ilfx

    def ilf_layer(limit, excess, base_limit, z):
        """
        Compute ILF layer
        parameters:
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
    
    
    
    #now calculating hull and TPL premium. To do so we need to retrive/ calculate
    #hull base rate, hull_weight_adjustment, hull_final_rate & hull premium
    for drone in data['drones']:
        #add base rate
        drone['hull_base_rate'] = hull_base_rate
        #add weight adjustments by mapping from table
        drone['hull_weight_adjustment'] = weight_adj_table.get(drone['weight'], 1)
        #calculate final rate
        drone['hull_final_rate'] = drone['hull_base_rate'] * drone['hull_weight_adjustment']
        #calculate hull premium
        drone['hull_premium'] = drone['value'] * drone['hull_final_rate']
        
        #Now calculating TPL
        #add base rate
        drone['tpl_base_rate'] = tpl_base_rate
        #calculate tpl_base_layer_premium
        drone['tpl_base_layer_premium'] = drone['tpl_base_rate'] * drone['value']
        #calculate ilf
        drone['tpl_ilf'] = ilf_layer(drone['tpl_limit'],drone['tpl_excess'], base_limit, z)
        #calcualte tpl_layer_premium
        drone['tpl_layer_premium'] = drone['tpl_base_layer_premium'] * drone['tpl_ilf']
    
    #calculating camera premiums
    #Cameras are charged at the highest rate across all drones which they can be attached i.e.
    #the highest rate for each drone where has_detachable_camera == True
    max_hull_rate = max(d['hull_final_rate'] for d in data['drones'] if d['has_detachable_camera'] == True)
    
    for camera in data['detachable_cameras']:
        #add in the max hull rate for cameras
        camera['hull_rate'] = max_hull_rate
        #calculating camera premium
        camera['hull_premium'] = camera['value'] * camera['hull_rate']
        
    #Apply the extensions for the drones. If customer has more drones than they can fly at any one time
    #charge the highest price for the n number of flying drones and charge 150 for the rest
    #get max number of drones
    max_drones = data['max_drones_in_air']
    #sort values based on hull premiums
    sorted_drones = sorted(data['drones'], key = lambda d: d['hull_premium'], reverse=True)
    #now loop through sorted_drones keeping highest premiums for n drones and setting rest to 50
    for i, drone in enumerate(sorted_drones): #enumerate adds an index to the iterable list so we can do anything >= 2 ==150
        if i >= max_drones:
            drone['adjusted_hull_premium'] = 150 #flat rate
        else:
            drone['adjusted_hull_premium'] = drone['hull_premium']
            
    #Applying the extensions for cameras. If there is more cameras than drones charge the full rate for n cameras with the highest values
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
    import pprint
    import math
    result = main()
    pprint.pprint(result)


# #### The output from this algorithm shows all of the input and the calculated values in the same data structure. It initially runs through the provided values and updates the drone and camera values that are associated with calculating premiums and also calculates the premiums of each device. The code initially updates the drone hull information by adding in and calculating the following hull premium information: 
# 
# (1) hull_base_rate, 
# (2) hull_weight_adjustment, 
# (3) hull_final_rate and 
# (4) hull_premium. 
# 
# Following this it again updates the drone information but for TPL values: 
# 
# (1) adds in tpl_base_rate, 
# (2) calculates tpl_base_layer_premium, 
# (3) calculates tpl_ilf and 
# (4) calcualtes tpl_layer_premium.
# 
# Then it updates the cameras data by adding in hull premiums. Based on the word document, as the cameras can be attached to any drone, they should be charged at the highest rate acorss all of the drones to which they can be attached i.e, for all drones with has_detachable_camera == True, find the highest rate and charge to all of the cameras. The code does the following:
# 
# (1) identifys the highest rate for cameras where has_detachable_camera == True
# (2) updates all cameras hull_rate to the max_rate
# (3) calculates each cameras hull_premium
# 
# Now once all of the relevant premiums have been calculated the algorithm takes into consideration the extensions provided in the modelling case study instrucitons which state
# 
# (i) Customers may have a large number of drones but warrant that they will only fly a small number (n) at any one time. We would like to charge the full rate for the n drones with the highest calculated premiums, and a fixed base premium of £150 for the remaining drones
# 
# (ii) Most of the risk of damage to cameras comes when they're in the air. If we have more cameras than drones, we would like to charge the full rate for the n cameras with the largest values, and a fixed premium of £50 for the remaining cameras.
# 
# 
# For the first extension, the algorithm initially identifys the max number of drones that will fly at any one time (taken from the provided data under key max_drones_in_air. Then it sorts the drone data based on hull premium with the highest values at the top of the dataset. Using enumerate we attach an index to the drone data which starts at 0 for the drone with the highest premium, 1 for the second highest premium ... N for the nth highest premium. Then it updates a new adjusted_hull_premium data point which is set to the base rate of 150 if the index is higher than the max_drones_in_air and retains the hull_premium for the N drones with the highest hull_premiums.
# 
# The second extension is handled in largely the same way. Firstly, the algorithm identifys if there are more cameras than drones. In the case where there are, it sorts the camera data based on value. Then again using enumerate we assign an index to the camera data which starts at 0 for the camera with the highest value and so on. If the index is >= the value of max drones, we adjust the hull premium to the flat rate of 50 and keep the original hull_premium value for the highest valued cameras. If the number of drones exceeds the number of cameras we keep the already calculated hull_premium.
# 
# Then the final two objects to be updated within the model are the net_prem data and the gross_prem data. To update the net_prem object the algorithm:
# 
# (1) updates drones_hull by summing together the adjusted_hull_premium for each drone
# (2) updates drones_tpl by summing together the tpl_layer_premium for each drone
# (3) updates cameras_hull by summing together the adjusted_hull_premium for each camera
# (4) Calculates the total by summing together values (1),(2) & (3)
# 
# Finally, the gross_prem object is updated by dividing the values in the net_prem object by (1-brokerage rate).
