# -*- coding: utf-8 -*-
"""
QUALITY MEASURES - DECISION TREES
"""

import csv
import json
import numpy as np


DB_lung = ["temp-lung-dvh",
            "washu_measures_lung_all",
            "washu_measures_lung_all_dvh_flag",
            "washu_measures_lung_all_dvh_value"]
DB_prostate = ["temp-prostate-dvh",
                "washu_measures_prostate_all",
                "washu_measures_prostate_all_dvh_flag",
                "washu_measures_prostate_all_dvh_value"]
DB = [DB_lung, DB_prostate]
files = ['Lung', 'Prostate']
h = int(input('0 for Lung, 1 for prostate....'))
sample = json.dumps({
                        'test_feature': 'chiefComplaint',
                        'success_features': ['Prostate cancer', 'Lung Cancer'],
                        'fail_features': '',
                        'yes_child': 'Pass',
                        'no_child': 'Exclude'
                    })

#-----------------------------------------------------------------------------

#                       New Implementation
#-----------------------------------------------------------------------------
class DTNode:
    def __init__(self, obj):
        print(obj)
        _=input('....')
        self.featureID  = obj['featureID']
        self.yes_child  = obj['yes_child']
        self.no_child  = obj['no_child']
        self.next = ''


    def query_system(self, patient):
        
        valid_risks = ['very low', 'low', 'intermediate', 'high', 'very high']
        
        
        if self.featureID ==1:
            try:                
                had_surgery = True if (patient['diagnosis']['previousSurgery'].lower() == 'yes') else False
            except:			
                had_surgery = False 
            return had_surgery
        
        
        elif self.featureID ==2:
            ## Staging
            try:
                TX = patient['diagnosis']['tStage']
                t_stage = True if (TX) else False
                # t_stage = TX if (TX) else -1
            except:  
                # t_stage = -1 
                t_stage = False
            return t_stage
	

		## Gleason Scores 
        elif self.featureID ==3:
            # try:
            #     primary = float(patient['diagnosis']['gleasonScore']['primaryGS'])
            #     primary_gs = primary if (primary >= 0) else -1
            # except:  
            #     primary_gs = -1
            try:
                primary = float(patient['diagnosis']['gleasonScore']['primaryGS'])
                primary_gs = True if (primary >= 0) else False
            except:  
                primary_gs = False
            return primary_gs


        elif self.featureID ==4:
            # try:
            #     secondary = float(patient['diagnosis']['gleasonScore']['secondaryGS'])
            #     secondary_gs = secondary if (secondary >= 0) else -1
            # except:  
            #     secondary_gs = -1 
            try:
                secondary = float(patient['diagnosis']['gleasonScore']['secondaryGS'])
                secondary_gs = True if (secondary >= 0) else False
            except:  
                secondary_gs = False
            return secondary_gs




        elif self.featureID ==5:
            # try:
            #     total = float(patient['diagnosis']['gleasonScore']['totalGS'])
            #     total_gs = total if (total >= 0.0) else -1 
            # except:  
            #     total_gs = -1
            try:
                total = float(patient['diagnosis']['gleasonScore']['totalGS'])
                total_gs = True if (total >= 0.0) else False
            except:  
                total_gs = False
            return total_gs

		


        elif self.featureID ==6:
            ## Prostate-Specific Antigen 
            try:
                psaScore = patient['diagnosis']['psa'][0]['psaScore']
                prostate_antigen = True if psaScore > 0 else False 
            except: 
                psaScore = np.nan 
                prostate_antigen = False
            return prostate_antigen
		


        elif self.featureID ==7:
            # try:
            #     risk_group = patient['diagnosis']['nccnRiskCategory'].lower()
            #     risk = risk_group if (risk_group) else None
            # except:  
            #     risk = None
            try:
                risk_group = patient['diagnosis']['nccnRiskCategory'].lower()
                risk = True if (risk_group) else False
            except:  
                risk = False
            return risk
		
            

                

    def description(self):
        print(f'\t Feature = {self.featureID}')
        print(f'\t Yes child = {self.yes_child}')
        print(f'\t No child = {self.no_child}')
    
    def processing(self, data):
        
        print('\nProcessing the data...')
        # print(f'current feature = {self.test_feature}\nsuccess feature = {self.success_features}')
        r = self.query_system(data)
        print(r)
        if r != None:
            if r in self.success_features:
                return self.yes_child
            else:
                return self.no_child
        else:
            return None
        
        
        
        
    def find_feature(self, obj, feature):
        """
        Recursively search for a feature in a JSON object.
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == feature:
                    return value
                else:
                    result = self.find_feature(value, feature)
                    if result is not None:
                        return result
        elif isinstance(obj, list):
            for item in obj:
                result = self.find_feature(item, feature)
                if result is not None:
                    return result
        return None


class DT:
    dt_json = None
    def __init__(self, dt_json, data):
        '''- Read a list of decision tree nodes as json
           - we create a list of DTNodes
           - we iterate through the ids and check...'''
        self.dt_json = dt_json
        self.current_node = DTNode(dt_json[0])
        self.result = self.current_node.processing(data)

        while self.result not in ['pass', 'fail', 'exclude']:            
            self.current_node = DTNode(self.get_next(self.result, self.dt_json))
            self.result = self.current_node.processing(data)
        print(self.result)
            
    def get_next(self, next_node, dt_json):
        '''search for the next item'''
        print('Next node is : ', next_node)
        for node_dict in dt_json:
            if node_dict['featureID']==next_node:
                return node_dict



#------------------------------------------------------------------------------  
#                           Dealing with bson files
#------------------------------------------------------------------------------  
# import bson
# import json

# # Load the BSON file
# with open("data/measures.bson", "rb") as f:
#     bson_data = f.read()

# # Decode the BSON data to a Python object
# bson_obj = bson.loads(bson_data)



# # Convert the BSON object to a Python dictionary
# dict_obj = bson_obj.to_dict()

# # Save the dictionary to a JSON file
# with open("example.json", "w") as f:
#     json.dump(dict_obj, f)
#------------------------------------------------------------------------------  
  



with open('DT2.json', 'r') as f:
    dt2 = json.load(f)


with open('Data/data.json', 'r') as f:
    data = json.load(f)

# # Open the CSV file for reading
# with open(f'Data/{files[h]}/{DB[h][0]}.csv', 'r') as csv_file:
#     # Read the CSV data using a DictReader
#     csv_reader = csv.DictReader(csv_file)
#     # Convert the CSV data to a list of dictionaries
#     data = list(csv_reader)

# json_data = json.loads(json.dumps(data))

results = {}
for patient in data:
    results[patient['vha_id']] = DT( dt2, patient).result
print(results)
        

