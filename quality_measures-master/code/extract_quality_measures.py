import sys
import pandas as pd
from collections import OrderedDict
import argparse
import logging
import time
from pymongo import MongoClient

from tqdm import tqdm
import pprint as pp


from measures.community_prostate_measures import CommunityProstateMeasure
from measures.ropa_prostate_measures import ProstateMeasure
from measures.ropa_lung_measures import LungMeasure
from measures.ropa_prostate_dvh_measures import ProstateDVHMeasure
from measures.ropa_lung_dvh_measures import LungDVHMeasure

logging.basicConfig(filename = 'ropa_logging.log',format='%(asctime)s:%(levelname)s:%(message)s')

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


def extract_qms(qm, patient):
    """
    Extracting Quality Measures.
    """
    pid = patient['caseId']
    qm.patient = patient

    set_patient_info(qm, pid)

    for featName, func in qm.fdict.items():
        qm.measures[featName] = func(qm)[1]
        
    #print(qm.measures)
    result = qm.measures.copy()
    return result

def extract_qms_submeasures(qm, patient):
    """
    Extracts all results and submeasures
    """
    
    pid = patient['caseId']
    qm.patient = patient

    set_patient_info(qm, pid)

    for featName, func in qm.fdict.items():
        if len(func(qm)) >= 3: 
            qm.measures[featName] = func(qm)[2]

    result = qm.measures.copy()
    return result

def extract_dvh_measures(qm, patient):
    """
    Extracts DVH measures for given patient
    """  
    if len(patient) > 0:    
        pid = patient['vha_id']
        qm.patient = patient
        set_patient_info(qm, pid)

        for featName, func in qm.fdict.items():
            qm.measures[featName] = func(qm)
    else:
        pass
    
    result =  qm.measures.copy()
    return result


def extract_dvh_values(qm, patient):
	"""
			Extracts DVH measures for given patient
	"""      
	return patient['dvh_values']

def set_database(qm, db, rc, wc):
    """
        Setup the database, read and write collection names for each class
    """
    qm.set_db_name(db)
    qm.set_read_collection_name(rc)
    qm.set_write_collection_name(wc)

######################################

if __name__ == '__main__':

    client = MongoClient()

    parser = argparse.ArgumentParser()
    requiredNamed = parser.add_argument_group('required arguments')

    requiredNamed.add_argument('-db', '--db_name', 
                                help='Name of database to access collections (hinge)', required = True)
    requiredNamed.add_argument('-rc', '--read_collection_name', 
                                help='Name of collection to read patients from', required = True)
    requiredNamed.add_argument('-wc', '--write_collection_name', 
                        help='Name of collection to read patient results to (measureTest)', required = True)
    requiredNamed.add_argument('-pid', '--patient',   
                        help='ID of the patient to calculate measures or pattern of ID', required = True)
    requiredNamed.add_argument('-d', '--disease_type', 
                                help='The disease type of the patient')
    parser.add_argument('-m', '--quality_measure', 
                        help='The individual quality measure to be checked')
    parser.add_argument('-sbc', '--sub_measure_collection',
                        help='Name of collection to write sub measures to (subMeasure)')

    args = parser.parse_args()
    db_name = args.db_name  #'hingeServer'
    read_collection_name = args.read_collection_name #patients
    write_collection_name = args.write_collection_name	#'measures'
    patient_id =  args.patient # '506-prostate-08'
    disease_type =  args.disease_type.lower() #lung, Prostate

    db_name = client[db_name]

    print(db_name, type(db_name))

    ## Query database for give seach pattern and store result in patients
    patients = db_name[read_collection_name].find({'vha_id':{'$regex': f'{patient_id}'}})

    ## based on each patient extract submeasures and store them in result collection
    for patient in tqdm(patients):
        if disease_type == 'prostate':
            qm_clinical = ProstateMeasure()
            qm_clinical_sub = ProstateMeasure()
            qm_dvh = ProstateDVHMeasure()
        elif disease_type  == 'lung': ##in ['NSCLC', 'SCLC', 'NSCLC_Surgery']:
            qm_clinical = LungMeasure()
            qm_clinical_sub = LungMeasure()
            qm_dvh = LungDVHMeasure()
        else:
            print('Please enter a valid disease type (lung or prostate) \n Use "-h" for help')
            logging.error('User entered {}, which is not a valid disease'.format(patient_id))
            exit()

        set_database(qm_clinical, db_name, read_collection_name, write_collection_name)
        set_database(qm_clinical_sub, db_name, read_collection_name, write_collection_name)
        set_database(qm_dvh, db_name, read_collection_name, write_collection_name)

        qms_submeasures_res = extract_qms_submeasures(qm_clinical_sub, patient['clinical'])
        qms_res = extract_qms(qm_clinical, patient['clinical'])
        dvh_res = extract_dvh_measures(qm_dvh, patient['dvh_values'])

        result_doc = {
            'vha_id': patient['vha_id'],
            'disease' : patient['disease'],
            'qms' : qms_res,
            'qms_submeasures' : qms_submeasures_res,
            'dvh_flags' : dvh_res, 
            'dvh_values' :patient['dvh_values']
        }
        
        ## update or insert result
        db_name[write_collection_name].update({'vha_id':patient['vha_id']},result_doc, upsert=True)
        