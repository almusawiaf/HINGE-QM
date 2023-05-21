from pymongo import MongoClient
import pandas as pd
import json
import argparse
import subprocess
from tqdm import tqdm

from measures.ropa_prostate_measures import ProstateMeasure
from measures.ropa_lung_measures import LungMeasure

centername_maps = pd.read_csv('../data/center_names.csv', index_col=0, skiprows=1, header=None)
centername_maps.index = centername_maps.index.astype(str)
centername_maps = centername_maps.to_dict()[1]

def set_patient_info(qm, pid):
    """
    Add common data fields to the subdocument
    """
    qm.measures['center_id'] = pid[:3]
    qm.measures['vha_id']= pid
    qm.measures['cancer_type']= pid.split('-')[1]
    qm.measures['center_name']= centername_maps[str(qm.measures['center_id'])]

def extract_qms_submeasures(qm, db_name, rc, wc,patient_id):
    """
    Extracts all results and submeasures
    """

    #make query to input fetch patient
    try:
        patient = db_name[rc].find({'vha_id':{'$regex': f'{patient_id}'}})
    except:
        print(f"error reading patient infor for tree generation of patient with id {patient_id}!!")
        exit(0)
        

    if patient.count() == 0:
        print("PyMongo Query did not find any patients\n")
        results = qm.measures.copy()
        return results

    patient = patient[0]['clinical']

    pid = patient['caseId']
    qm.patient = patient

    set_patient_info(qm, pid)

    for featName, func in qm.fdict.items():
        if len(func(qm)) >= 3: 
            qm.measures[featName] = func(qm)[2]

    result = qm.measures.copy()

    return result

def set_database(qm, db, rc, wc):
    """
        Setup the database, read and write collection names for each class
    """
    qm.set_db_name(db)
    qm.set_read_collection_name(rc)
    qm.set_write_collection_name(wc)


def load_washu_calculated_measures(db, rc, wc):
        
    df_lung_clinical = pd.read_csv('../washu_measures/washu_data/washu_measures_lung_all.csv').fillna("").astype(str)
    df_lung_dvh_flags = pd.read_csv('../washu_measures/washu_data/washu_measures_lung_all_dvh_flag.csv').fillna("").astype(str)
    df_lung_dvh_values = pd.read_csv('../washu_measures/washu_data/washu_measures_lung_all_dvh_value.csv').fillna("").astype(str)
    df_lung_dvh_values.columns = df_lung_dvh_values.columns.str.replace('.', '-dot-')

    df_prostate_clinical = pd.read_csv('../washu_measures/washu_data/washu_measures_prostate_all.csv').fillna("").astype(str)
    df_prostate_dvh_flags = pd.read_csv('../washu_measures/washu_data/washu_measures_prostate_all_dvh_flag.csv').fillna("").astype(str)
    df_prostate_dvh_values = pd.read_csv('../washu_measures/washu_data/washu_measures_prostate_all_dvh_value.csv').fillna("").astype(str)

    print('\nprostate patients')
    print("Clinical: ", len(df_prostate_clinical.vha_id.tolist()))
    print("DVH Flags: ", len(df_prostate_dvh_flags.vha_id.tolist()))
    print("DVH Vlaues: ", len(df_prostate_dvh_values.vha_id.tolist()))

    print("Intersection of DVH values and Flags: ", len(set(df_prostate_dvh_flags.vha_id.tolist()).intersection(df_prostate_dvh_values.vha_id.tolist())))

    print('\nLung Patients')
    print("Clinical: ", len(df_lung_clinical.vha_id.tolist()))
    print("DVH Flags: ",len(df_lung_dvh_flags.vha_id.tolist()))
    print("DVH Values: ", len(df_lung_dvh_values.vha_id.tolist()))

    print("Intersection of DVH values and Flags: ", len(set(df_lung_dvh_flags.vha_id.tolist()).intersection(df_lung_dvh_values.vha_id.tolist())))

    prostate_vha_ids = set(df_prostate_clinical.vha_id.tolist()).intersection(df_prostate_dvh_flags.vha_id.tolist() + df_prostate_dvh_values.vha_id.tolist())
    lung_vha_ids = set(df_lung_clinical.vha_id.tolist()).intersection(df_lung_dvh_flags.vha_id.tolist() + df_lung_dvh_values.vha_id.tolist())
    vha_ids = list(prostate_vha_ids) + list(lung_vha_ids)

    print(f"\nProstate patients: {len(prostate_vha_ids)}")
    print(f"Lung patients: {len(lung_vha_ids)}")
    print(f"Total (prostate + lung) patients: {len(vha_ids)}\n")

    for vha_id in tqdm(vha_ids): 
        
        if 'sclc' in vha_id.lower():
            cancer_type = 'lung'
            qm = LungMeasure()

            set_database(qm, db, rc, wc)
            qms_submeasures = extract_qms_submeasures(qm, db, rc, wc, vha_id)
            
            db[wc].insert_one({
                'vha_id': vha_id,
                'disease': cancer_type,
                'qms': json.loads(df_lung_clinical[df_lung_clinical.vha_id == vha_id].to_json(orient='records'))[0],
                'dvh_flags': json.loads(df_lung_dvh_flags[df_lung_dvh_values.vha_id == vha_id].to_json(orient='records'))[0],
                'dvh_values': json.loads(df_lung_dvh_values[df_lung_dvh_values.vha_id == vha_id].to_json(orient='records'))[0],
                'qms_submeasures': qms_submeasures
            })

        elif 'prostate' in vha_id.lower():
            cancer_type = 'prostate'
            qm = ProstateMeasure()

            set_database(qm, db, rc, wc)
            qms_submeasures = extract_qms_submeasures(qm, db, rc, wc, vha_id)

            db[wc].insert_one({
                'vha_id': vha_id,
                'disease': cancer_type,
                'qms': json.loads(df_prostate_clinical[df_prostate_clinical.vha_id == vha_id].to_json(orient='records'))[0],
                'dvh_flags': json.loads(df_prostate_dvh_flags[df_prostate_dvh_values.vha_id == vha_id].to_json(orient='records'))[0],
                'dvh_values': json.loads(df_prostate_dvh_values[df_prostate_dvh_values.vha_id == vha_id].to_json(orient='records'))[0],
                'qms_submeasures': qms_submeasures
            })

        else:
            print('Error: Disease type is unknown')

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    requiredNamed = parser.add_argument_group('required arguments')

    requiredNamed.add_argument('-db', '--db_name', help='The MongoDB database to upload the data', required=True)
    requiredNamed.add_argument('-wc',  '--write_collection_name', help='The Collection to write results.', required=True)
    requiredNamed.add_argument('-rc',  '--read_collection_name', help='The Collection to read input.', required=True)

    args = parser.parse_args()

    db_name = args.db_name
    wc = args.write_collection_name
    rc = args.read_collection_name

    client = MongoClient()
    db = client[db_name]
  
    collections = db.list_collection_names()

    if rc not in collections:
        print(f"collection named {rc} is not found in databes {db}.\n")
        print("please load patients before loading WASHU results")
        exit(0)

    if db[rc].count_documents({}) == 0:
        print(f"read collection {rc} is empty, please make sure you load patients in {rc} collection\n")
        exit(0)

    
    db[wc].drop()

    load_washu_calculated_measures(db, rc, wc)
