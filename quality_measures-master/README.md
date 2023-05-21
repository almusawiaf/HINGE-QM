# quality_measures
ROPA Quality Measures


##### Traverse to code folder to run below scripts


## To load WASHU provide patient data
``` console
#python load_washu_input.py  -h
usage: load_washu_input.py [-h] -db DB_NAME -wc WRITE_COLLECTION_NAME

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -db DB_NAME, --db_name DB_NAME
                        Name of database to access collections (eg. hinge)
  -wc WRITE_COLLECTION_NAME, --write_collection_name WRITE_COLLECTION_NAME
                        Name of collection to write patient records (eg.
                        patients)

```
#### Eg: python load_washu_input.py --db hingeServer --wc patients


## To load WASHU calculated quality measures data. 
``` console
usage: load_washu_input.py [-h] -db DB_NAME -wc WRITE_COLLECTION_NAME

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -db DB_NAME, --db_name DB_NAME
                        Name of database to access collections (eg. hingeServer)
  -wc WRITE_COLLECTION_NAME, --write_collection_name WRITE_COLLECTION_NAME
                        Name of collection to write patient records (eg. patients)
```

#### Eg: python load_washu_resuls.py -db hingeServer -rc patients -wc measures


## To extract quality measure from scratch using our qm scripts. 

```console 
usage: extract_quality_measures.py [-h] -db DB_NAME -rc READ_COLLECTION_NAME
                                   -wc WRITE_COLLECTION_NAME -pid PATIENT
                                   [-d DISEASE_TYPE] [-m QUALITY_MEASURE]
                                   [-sbc SUB_MEASURE_COLLECTION]

optional arguments:
  -h, --help            show this help message and exit
  -m QUALITY_MEASURE, --quality_measure QUALITY_MEASURE
                        The individual quality measure to be checked
  -sbc SUB_MEASURE_COLLECTION, --sub_measure_collection SUB_MEASURE_COLLECTION
                        Name of collection to write sub measures to
                        (subMeasure)

required arguments:
  -db DB_NAME, --db_name DB_NAME
                        Name of database to access collections (hinge)
  -rc READ_COLLECTION_NAME, --read_collection_name READ_COLLECTION_NAME
                        Name of collection to read patients from
  -wc WRITE_COLLECTION_NAME, --write_collection_name WRITE_COLLECTION_NAME
                        Name of collection to read patient results to
                        (measureTest)
  -pid PATIENT, --patient PATIENT
                        ID of the patient to calculate measures or pattern of
                        ID
  -d DISEASE_TYPE, --disease_type DISEASE_TYPE
                        The disease type of the patient
 ```
 
#### Eg: python extract_quality_measures.py  -db hingeServer -rc patients -wc measures -d Prostate -pid 506-Prostate-01




 

