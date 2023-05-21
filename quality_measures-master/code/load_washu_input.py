from pymongo import MongoClient
import pandas as pd
import json
import argparse
import subprocess

import pprint
from tqdm import tqdm

def load_centername_to_id_maps():
       
    centername_maps = pd.read_csv('../data/center_names.csv', index_col=0, skiprows=1, header=None)
    centername_maps.index = centername_maps.index.astype(str)
    centername_maps = centername_maps.to_dict()[1]

    return centername_maps

def load_washu_data(db_handle, input_collection_name):

    centername_maps = load_centername_to_id_maps()
        
    subprocess.run(['python', '../data/washu_ropa_import_updated.py', '../data/ROPA_SQL_Database_Final.csv', '../data/cprs_updated.json'])

    clinical_data_file = 'data.json'

    with open(clinical_data_file, 'r') as data_file:
        json_data = data_file.read()

    clinical_data = json.loads(json_data)

    df_lung_dvh_values = pd.read_csv('../washu_measures/washu_data/washu_measures_lung_all_dvh_value.csv')
    df_lung_dvh_values.columns = df_lung_dvh_values.columns.str.replace('.', '-dot-')
    df_prostate_dvh_values = pd.read_csv('../washu_measures/washu_data/washu_measures_prostate_all_dvh_value.csv')

    db[input_collection_name].drop()

    print("\nGenerating WASHU Input Collection:")
    for item in tqdm(clinical_data):
        pid = item['caseId']
        if "prostate" in pid.lower():
            dvh_values = df_prostate_dvh_values[df_prostate_dvh_values.vha_id == pid].to_json(orient='records')
            disease = 'prostate'
        elif 'sclc' in pid.lower():
            dvh_values = df_lung_dvh_values[df_lung_dvh_values.vha_id == pid].to_json(orient='records')
            disease = 'lung'
        
        try:
            dvh_values = json.loads(dvh_values)[0]     
        except:
            dvh_values = {}   
                
        center_id, cancer_type, _ =  item['caseId'].split('-')
        
        patient_doc = {
                    'vha_id' : item['caseId'],
                    'cancer_type': cancer_type,
                    'center_id' : center_id,
                    'center_name': centername_maps[center_id],
                    'disease' : disease,
                    'clinical' : item,
                    'dvh_values' : dvh_values    
                }
            
        db[input_collection_name].insert_one(patient_doc)
        
        #pprint.pprint(patient_doc)


######################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    requiredNamed = parser.add_argument_group('required arguments')

    requiredNamed.add_argument('-db', '--db_name', 
                                help='Name of database to access collections (eg. hinge)', required = True)
    requiredNamed.add_argument('-wc', '--write_collection_name', 
                        help='Name of collection to write patient records (eg. patients)', required = True)
    
    args = parser.parse_args()
    db_name = args.db_name  #'hingeServer'
    write_collection_name = args.write_collection_name	#'patients'

    client = MongoClient()
    db = client[db_name]

    load_washu_data(db, write_collection_name)