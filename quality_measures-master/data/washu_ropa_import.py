from pprint import pprint
import json
import sys
from datetime import datetime, timedelta
#from hinge_import import db_put

fake_consult_date = datetime(2010, 1, 1)
json_data = None
cprs_data = None


#FIXME - use date not string value
def convert_date(d):
    if d == 'NULL':
        return ''
    rel_date = d.split(' ')
    if '-' in rel_date:
        return '' #FIXME - check wrong date (- -3 0), treat it as invaid
    for index in range(0, len(rel_date)):
        rel_date[index] = int(rel_date[index].strip())
    date_delta = rel_date[2] * 365 + rel_date[1] * 30 + rel_date[0]
    date_format = '%Y-%m-%d'
    return (fake_consult_date + timedelta(days=date_delta)).strftime(date_format)


def is_int(num):
    try:
        x = int(num)
        return True
    except:
        return False


def process_clinical_validation(data_lines, disease_site, surgery):
    global json_data

    scoringAndGrades = {}
    patientInformation = {'dateOfROConsult': '2010-01-01'}

    for line in data_lines:
        data_key = line[8]
        value = line[11]

        if 'tumorType' not in patientInformation:
            # patientInformation['tumorType'] = line[4].lower().split(' ')[0]
            patientInformation['tumorType'] = disease_site

        if data_key == 'ICD 9/10 code':
            patientInformation['icdCode'] = value
        elif data_key == 'Surgery':
            patientInformation['surgery'] = value
        elif data_key == 'Surgery Date':
            patientInformation['surgeryDate'] = convert_date(value)
        elif data_key == 'Recurrent Disease':
            patientInformation['recurrentDisease'] = value

        elif data_key == 'Prostate-Specific Antigen':
            scoringAndGrades['PSASource'] = value
        elif data_key == 'PSA Count':
            scoringAndGrades['PSACount'] = value
        elif data_key == 'PSA Date':
            scoringAndGrades['PSADate'] = convert_date(value)
        elif data_key == 'Gleason Score':
            scoringAndGrades['gleasonScoreSource'] = value
        elif data_key == 'Primary / Secondary Score?':
            scoringAndGrades['primaryAndSecondaryGS'] = value
        elif data_key == 'Primary GS':
            scoringAndGrades['primaryGS'] = value
        elif data_key == 'Secondary GS':
            scoringAndGrades['secondaryGS'] = value
        elif data_key == 'Total GS':
            scoringAndGrades['totalGS'] = value
        elif data_key == 'Gleason Score Date':
            scoringAndGrades['gleasonDate'] = convert_date(value)
        elif data_key == 'NCCN Risk Group':
            scoringAndGrades['riskGroupSource'] = value
        elif data_key == 'NCCN Risk Group Date':
            scoringAndGrades['riskGroupDate'] = value
        elif data_key == 'Risk':
            scoringAndGrades['riskGroup'] = value

        elif data_key == 'Stage':
            scoringAndGrades['sclcStageSource'] = value
        elif data_key == 'Stage Date':
            scoringAndGrades['sclcStageDate'] = convert_date(value)
        elif data_key == 'Staging':
            scoringAndGrades['sclcStage'] = value

        elif data_key == 'Primary Tumor Stage':
            scoringAndGrades['tnmTumorStageSource'] = value
        elif data_key == 'Primary Tumor Stage Date':
            scoringAndGrades['tnmTumorStageDate'] = value

        elif data_key == 'TNM Staging':
            tnm_key = line[9]
            if len(value) > 0:
                if value[-1] == 'x':
                    value = value.replace('x', 'X')
            if tnm_key == '--Select T-Stage --':
                scoringAndGrades['TX'] = value
            elif tnm_key == '--Select N-Stage--':
                scoringAndGrades['NX'] = value
            elif tnm_key == '--Select M-Stage--':
                scoringAndGrades['MX'] = value
        elif data_key == 'Overall Staging':
            scoringAndGrades['overallTumorStage'] = value.upper()
        elif data_key == 'Overall Stage':
            scoringAndGrades['overallTumorStageSource'] = value
        elif data_key == 'Overall Stage Date':
            scoringAndGrades['overallTumorStageDate'] = convert_date(value)
        elif data_key == 'Staging System':
            scoringAndGrades['stagingSystemSource'] = value
        elif data_key == 'Staging System Type':
            scoringAndGrades['stagingSystemType'] = value
        elif data_key == 'Staging System Date':
            scoringAndGrades['stagingSystemDate'] = convert_date(value)

    json_data['patientInformation'] = patientInformation
    json_data[disease_site.lower() + 'ScoringAndGrades'] = scoringAndGrades
    json_data['tumorType'] = disease_site
    if 'surgery' in patientInformation:
        json_data['isSurgery'] = patientInformation['surgery']
    else:
        json_data['isSurgery'] = 'No'

# Take array'ed sub-form data and form correct JSON document, handing missing entries
def process_multi_field(values):
    max_count = 0
    for tag in values:
        if len(values[tag]) > max_count:
            max_count = len(values[tag])
    results = [dict() for x in range(max_count)]
    for element in values:
        for value in values[element]:
            results[value[0]][element] = value[1]
    return results


def process_multi_otvs(toxicities, qualityOfLife, performanceStatus, values_2):
    max_count = 0
    for tag in toxicities:
        for index in range(0, len(toxicities[tag])):
            if len(toxicities[tag]) > 0:
                if toxicities[tag][index][0] > max_count:
                    max_count = toxicities[tag][index][0]

    for tag in values_2:
            for index in range(0, len(values_2[tag])):
                if len(values_2[tag]) > 0:
                    if values_2[tag][index][0] > max_count:
                        max_count = values_2[tag][index][0]
    max_count += 1

    final_results = []

    # toxicity
    counts = [0 for x in range(max_count)]
    for tag in toxicities:
        for entry in toxicities[tag]:
            if entry[1] > counts[entry[0]]:
                counts[entry[0]] = entry[1]
    for index in range(0, len(counts)):
        counts[index] += 1
    results = [[] for x in range(max_count)]
    for index, entry in enumerate(counts):
        results[index] = [{} for y in range(0, counts[index])]

    for tag in toxicities:
        for entry in toxicities[tag]:
            results[entry[0]][entry[1]][tag] = entry[2]

    for entry in results:
        final_results.append({'toxicity': entry})

    # Quality of Life
    counts = [0 for x in range(max_count)]
    for tag in qualityOfLife:
        for entry in qualityOfLife[tag]:
            if entry[1] > counts[entry[0]]:
                counts[entry[0]] = entry[1]
    for index in range(0, len(counts)):
        counts[index] += 1
    results = [[] for x in range(max_count)]
    for index, entry in enumerate(counts):
        results[index] = [{} for y in range(0, counts[index])]

    for tag in qualityOfLife:
        for entry in qualityOfLife[tag]:
            results[entry[0]][entry[1]][tag] = entry[2]
    #FIXME
    for index, entry in enumerate(results):
        final_results[index]['qualityOfLife'] = entry

    # Performance Status
    counts = [0 for x in range(max_count)]
    for tag in performanceStatus:
        for entry in performanceStatus[tag]:
            if entry[1] > counts[entry[0]]:
                counts[entry[0]] = entry[1]
    for index in range(0, len(counts)):
        counts[index] += 1
    results = [[] for x in range(max_count)]
    for index, entry in enumerate(counts):
        results[index] = [{} for y in range(0, counts[index])]

    for tag in performanceStatus:
        for entry in performanceStatus[tag]:
            results[entry[0]][entry[1]][tag] = entry[2]
    # FIXME
    for index, entry in enumerate(results):
        final_results[index]['performanceStatus'] = entry


    print("***")
    print(final_results)
    print("***")

    return final_results


def add_section_values(otvs, otvAssessments):
    for tag in otvAssessments:
        for entry in otvAssessments[tag]:
            otvs[entry[0]].append({tag: entry[2]})


def process_consult(data_lines, disease_site):
    global json_data

    qualityOfLife = []
    performanceStatus = []
    clinicalTrials = {}
    treatmentOptions = []
    adt = {}
    imagingStudies = {}
    pathology = {}
    chemotherapy = {}
    molecular = {}
    history = {}


    qualityOfLifeEntries = []
    performanceStatusEntries = []
    clinicalTrialsEntries = []
    treatmentOptionsEntries = []
    adtEntries = []
    imagingStudiesEntries = []
    pathologyEntries = []
    chemotherapyEntries = []
    molecularEntries = []
    treatmentEntries = []

    for line in data_lines:
        data_key = line[8]
        sub_group = line[7]
        value = line[11]
        if sub_group == 'Quality of Life':
            qualityOfLifeEntries.append(line)
        elif sub_group == 'Performance Status':
            performanceStatusEntries.append(line)
        elif sub_group == 'Clinical Trials' or sub_group == 'Clinical Trial Enrollment':
            clinicalTrialsEntries.append(line)
        elif sub_group == 'Treatment Options':
            treatmentOptionsEntries.append(line)
        elif sub_group == 'ADT Intent' or sub_group == 'ADT Injection':
            adtEntries.append(line)
        elif sub_group == 'Imaging Studies' or sub_group == 'Image Studies':
            imagingStudiesEntries.append(line)
        elif sub_group == 'Pathology':
            pathologyEntries.append(line)
        elif sub_group == 'Chemotherapy':
            chemotherapyEntries.append(line)
        elif sub_group == 'Molecular':
            molecularEntries.append(line)
        elif sub_group == 'Treatment':
            treatmentEntries.append(line)

    ##############################
    # process Quality of Life Scores
    ##############################
    qualityOfLifeInstruments = []
    qualityOfLifeScores = []

    for entry in qualityOfLifeEntries:
        data_key = entry[8]
        item_type = entry[9]
        value = entry[11]
        if data_key == 'Quality of Life Assessment':
            #qualityOfLife['qualityOfLifeAssessmentSource'] = value
            pass
        elif data_key == 'Quality of Life Assessment Date':
            #qualityOfLife['qualityOfLifeAssessmentDate'] = convert_date(value)
            pass
        if data_key == 'Quality of Life Instrument':
            if item_type == '--Select Instrument--':
                qualityOfLifeInstruments.append(value)
            elif item_type == 'Input Numeric Score':
                qualityOfLifeScores.append(value)
    #qualityOfLife['qualityOfLifeScore'] = []
    for index in range(0, len(qualityOfLifeInstruments)):
        #qualityOfLife['qualityOfLifeScore'].append({'assessment': qualityOfLifeInstruments[index],
        #                                    'numericScore': qualityOfLifeScores[index]})
        print('******')
        print(qualityOfLifeInstruments, qualityOfLifeScores)

        #FIXME!!!!!!
        try:
            qualityOfLife.append({'qualityOfLifeInstrument': qualityOfLifeInstruments[index],
                                            'qualityOfLifeScore': int(qualityOfLifeScores[index])})
        except:
            pass
    json_data['qualityOfLife'] = qualityOfLife
    pprint(json_data['qualityOfLife'])

    ##############################
    # process Performance Status
    ##############################
    performanceInstruments = []
    performanceScores = []

    for entry in performanceStatusEntries:
        data_key = entry[8]
        item_type = entry[9]
        value = entry[11]
        if data_key == 'Performance Status':
            #performanceStatus['performanceStatusSource'] = value
            pass
        elif data_key == 'Performance Status Date':
            #performanceStatus['performanceStatusDate'] = convert_date(value)
            pass
        elif data_key == 'Performance Scoring':
            if item_type == '-Select Instrument--' or item_type == '--Select Instrument--':
                performanceInstruments.append(value)
            elif item_type == 'Input Numeric Score':
                performanceScores.append(value)

    #performanceStatus['performanceScoring'] = []
    for index in range(0, len(performanceInstruments)):
        performanceStatus.append(
            {'performanceInstrument': performanceInstruments[index], 'performanceScore': int(performanceScores[index])})

    json_data['performanceStatus'] = performanceStatus

    ##############################
    # process Clinical Trials
    ##############################
    for entry in clinicalTrialsEntries:
        data_key = entry[8]
        value = entry[11]
        if data_key == 'Clinical Trials':
            clinicalTrials['clinicalTrialSource'] = value
        elif data_key == 'Clinical Trials Date':
            clinicalTrials['clinicalTrialSourceDate'] = convert_date(value)
        elif data_key == 'Clinical Trial Enrollment':
            clinicalTrials['clinicalTrialEnrollment'] = value
        elif data_key == 'Input Trial Number':
            clinicalTrials['clinicalTrialNumber'] = value
        elif data_key == 'Is there an enrollment date?':
            clinicalTrials['isClinicalTrialEnrollmentDate'] = value
        elif data_key == 'Enrollment Date':
            clinicalTrials['clinicalTrialEnrollmentDate'] = convert_date(value)
    json_data['clinicalTrials'] = clinicalTrials


    ##############################
    # process Imaging Studies
    ##############################
    for entry in imagingStudiesEntries:
        data_key = entry[8]
        value = entry[11]
        if data_key == 'Pelvic MRI':
            imagingStudies['pelvicMRISource'] = value
        elif data_key == 'Pelvic MRI Mention Date':
            imagingStudies['pelvicMriMentionDate'] = convert_date(value)
        elif data_key == 'Is There a Pelvic MRI Report Date?':
            imagingStudies['isPelvicMriDate'] = value
        elif data_key == 'Pelvic MRI Report Date':
            imagingStudies['pelvicMriReportDate'] = convert_date(value)

        elif data_key == 'Pelvic CT':
            imagingStudies['pelvicCTSource'] = value
        elif data_key == 'Pelvic CT Mention Date':
            imagingStudies['pelvicCtMentionDate'] = convert_date(value)
        elif data_key == 'Is There a Pelvic CT Report Date?':
            imagingStudies['isPelvicCtDate'] = value
        elif data_key == 'Pelvic CT Report Date':
            imagingStudies['pelvicCtReportDate'] = convert_date(value)

        elif data_key == 'Bone Scan':
            imagingStudies['boneScanSource'] = value
        elif data_key == 'Bone Scan Mention Date':
            imagingStudies['boneScanMentionDate'] = convert_date(value)
        elif data_key == 'Is There a Bone Scan Report Date?':
            imagingStudies['isBoneScanDate'] = value
        elif data_key == 'Bone Scan Report Date':
            imagingStudies['boneScanReportDate'] = convert_date(value)
        elif data_key == 'Bone Scan Type':
            if value == 'NaF PET':
                value = 'NaF-PET'
            imagingStudies['boneScanType'] = value

        elif data_key == 'Bone Density Assessment':
            imagingStudies['boneDensityAssessment'] = value
        elif data_key == 'Bone Density Date':
            imagingStudies['boneDensityDate'] = convert_date(value)

        elif data_key == 'MRI of Brain':
            imagingStudies['mriOfBrainSource'] = value
        elif data_key == 'MRI of Brain Mention Date': # FIXME - what does this really mean?
            imagingStudies['mriOfBrainDate'] = convert_date(value)
        elif data_key == 'Is There an MRI of Brain Report Date?':
            imagingStudies['isMriOfBrainReportDate'] = value
        elif data_key == 'MRI of Brain Report Date':
            imagingStudies['mriOfBrainReportDate'] = convert_date(value)

        elif data_key == 'CT of Brain':
            imagingStudies['ctOfBrainSource'] = value
        elif data_key == 'CT of Brain Mention Date':
            imagingStudies['ctOfBrainDate'] = convert_date(value)
        elif data_key == 'Is There an CT of Brain Report Date?':
            imagingStudies['isCtOfBrainReportDate'] = value
        elif data_key == 'CT of Brain Report Date':
            imagingStudies['ctOfBrainReportDate'] = convert_date(value)

        elif data_key == 'PET/CT':
            imagingStudies['petctSource'] = value
        elif data_key == 'PET/CT Mention Date':
            imagingStudies['petctDate'] = convert_date(value)
        elif data_key == 'Is There an PET/CT Report Date?':
            imagingStudies['isPetctReportDate'] = value
        elif data_key == 'PET/CT Report Date':
            imagingStudies['petctReportDate'] = convert_date(value)
        #json_data[disease_site.lower() + 'ImagingStudies'] = imagingStudies

        json_data['consult'] = {}
        json_data['consult']['imagingStudies'] = imagingStudies



    if disease_site.lower() == 'prostate':
        ##############################
        # process Treatment Options
        ##############################
        treatmentOptionsArrays = {'treatmentOptionsSource': [], 'treatmentOptionsDate': [], 'treatmentTechnique': []}

        for entry in treatmentOptionsEntries:
            data_key = entry[8]
            value = entry[11]
            sub_index = int(entry[13])
            line_result = [sub_index, value]

            if data_key == 'Treatment Options':
                treatmentOptionsArrays['treatmentOptionsSource'].append(line_result)
            elif data_key == 'Treatment Options Date':
                line_result[1] = convert_date(value)
                treatmentOptionsArrays['treatmentOptionsDate'].append(line_result)
            elif data_key == 'Treatment Technique':
                treatmentOptionsArrays['treatmentTechnique'].append(line_result)
        treatmentOptions = process_multi_field(treatmentOptionsArrays)
        json_data[disease_site.lower() + 'TreatmentOptions'] = treatmentOptions

        ##############################
        # process
        ##############################
        adtArrays = {'adtInjectionDose': [], 'adtInjectionDate': []}

        for entry in adtEntries:
            data_key = entry[8]
            data_type = entry[10]
            value = entry[11]
            sub_index = int(entry[13])
            line_result = [sub_index, value]

            if data_key == 'Duration Intent of ADT':
                value = value.replace('-', ' ')
                adt['durationIntentOfADT'] = value
            elif data_key == 'ADT Injection Dose':
                if data_type == 'number-field':
                    adtArrays['adtInjectionDose'].append(line_result)
                elif data_type == 'relative-date-delta-field':
                    line_result[1] = convert_date(line_result[1])
                    adtArrays['adtInjectionDate'].append(line_result)

        adt['prostateAdtInjection'] = process_multi_field(adtArrays)
        json_data['prostateAdt'] = adt
    else:
        ##############################
        # process Molecular
        ##############################
        for entry in molecularEntries:
            data_key = entry[8]
            value = entry[11]

            if data_key == 'Molecular Information':
                molecular['molecularInformationSource'] = value
            elif data_key == 'Molecular Information Date':
                molecular['molecularInformationDate'] = convert_date(value)
            elif data_key == 'Molecular Information Type':
                molecular['molecularInformationType'] = value
            elif data_key == 'Molecular Information Report':
                molecular['isMolecularInformationReport'] = value
            elif data_key == 'No Molecular Information Report Reason':
                molecular['noMolecularInformationReportReason'] = value
            elif data_key == 'Molecular Information Report Type':
                molecular['molecularInformationReportType'] = value
            elif data_key == 'Molecular Information Report Date':
                molecular['molecularInformationReportDate'] = convert_date(value)
        json_data[disease_site.lower() + 'Molecular'] = molecular

        ##############################
        # process Treatment
        ##############################
        for entry in treatmentEntries:
            data_key = entry[8]
            value = entry[11]

            if data_key == 'Smoking Status':
                history['smokingStatusSource'] = value
            elif data_key == 'Smoking Status Date':
                history['smokingStatusDate'] = convert_date(value)
            elif data_key == 'Current Smoking Status':
                history['currentSmokingStatus'] = value
            elif data_key == 'Smoking Cessation':
                history['smokingCessation'] = value
            elif data_key == 'Implantable Cardiac Device':
                history['implantableCardiacDeviceSource'] = value
            elif data_key == 'Implantable Cardiac Device Date':
                history['implantableCardiacDeviceDate'] = convert_date(value)
            elif data_key == 'Multidisciplinary Consult':
                history['multidisciplinaryConsult'] = value
            elif data_key == 'Multidisciplinary Consult Date':
                history['multidisciplinaryConsultDate'] = convert_date(value)

            elif data_key == 'NSCLC Classification':
                json_data[disease_site.lower() + 'ScoringAndGrades']['nsclcClassificationSource'] = value
            elif data_key == 'NSCLC Classification Date':
                json_data[disease_site.lower() + 'ScoringAndGrades']['nsclcClassificationDate'] = convert_date(value)
            elif data_key == 'NSCLC Classification Type':
                json_data[disease_site.lower() + 'ScoringAndGrades']['nsclcClassificationType'] = value

        json_data[disease_site.lower() + 'History'] = history

        ##############################
        # process Pathology
        ##############################
        for entry in pathologyEntries:
            data_key = entry[8]
            value = entry[11]

            if data_key == 'Pathology':
                pathology['pathologySource'] = value
            elif data_key == 'Pathology Date':
                pathology['pathologyDate'] = convert_date(value)
            elif data_key == 'Is There a Pathology Report?':
                pathology['isPathologyReport'] = value
            elif data_key == 'Pathology Report':
                if value == 'Not Specified':
                    value = 'Not Stated'
                pathology['pathologyReportType'] = value
            elif data_key == 'Pathology Report Date':
                pathology['pathologyReportDate'] = convert_date(value)
            elif data_key == 'No Pathology Report Reason':
                pathology['noPathologyReportReason'] = value
        json_data[disease_site.lower() + 'Pathology'] = pathology

        ##############################
        # process Chemotherapy
        ##############################
        chemotherapyArrays = {'chemotherapySource': [], 'chemotherapyStartDate': [], 'chemotherapyEndDate': []}

        for entry in chemotherapyEntries:
            data_key = entry[8]
            item_type = entry[9]
            value = entry[11]
            sub_index = int(entry[13])
            line_result = [sub_index, value]
            if data_key == 'Chemotherapy':
                chemotherapyArrays['chemotherapySource'].append(line_result)
            elif data_key == 'Chemotherapy Dates' or data_key == 'Date':
                if item_type == 'Start Date':
                    line_result[1] = convert_date(line_result[1])
                    chemotherapyArrays['chemotherapyStartDate'].append(line_result)
                elif item_type == 'End Date':
                    line_result[1] = convert_date(line_result[1])
                    chemotherapyArrays['chemotherapyEndDate'].append(line_result)

        chemotherapy = process_multi_field(chemotherapyArrays)
        json_data[disease_site.lower() + 'Chemotherapy'] = chemotherapy


def process_otv(data_lines, disease_site):
    global json_data

    otvs = {}
    assessments = {}
    qualityOfLife = {}
    performanceStatus = {}
    toxicity = {}

    ##############################
    # process Assessment source
    ##############################
    otvToxicities = {'toxicity': [], 'grade': [], 'system': []}
    otvAssessments = {'otvAssessmentSource': [], 'otvAssessmentDate': []}

    otvQualityOfLife = {'qualityOfLifeInstrument': [], 'qualityOfLifeScore': []}
    otvPerformanceStatus = {'performanceInstrument': [], 'performanceScore': []}
    # FIXME - add performance status

    for entry in data_lines:
        print(entry)
        data_sub_key = entry[9]
        value = entry[11]
        index = int(entry[12])
        sub_index = int(entry[13])
        line_result = [index, sub_index, value]
        if data_sub_key == '--Select Document--':
            otvAssessments['otvAssessmentSource'].append(line_result)
        elif data_sub_key == 'MM/DD/YYYY':
            line_result[2] = convert_date(line_result[2])
            otvAssessments['otvAssessmentDate'].append(line_result)
        elif data_sub_key == '--Select Toxicity--':
            otvToxicities['toxicity'].append(line_result)
        elif data_sub_key == '--Select System--':
            if line_result[2] == 'No Toxicity':
                line_result[2] = 'Not Stated'
            otvToxicities['system'].append(line_result)
        elif data_sub_key == '--Select Grade--':
            otvToxicities['grade'].append(line_result)

        elif data_sub_key == '--Select Instrument--':
            if entry[8] == 'Quality of Life Assessment':
                otvQualityOfLife['qualityOfLifeInstrument'].append(line_result)
            elif entry[8] == 'Performance Status':
                otvPerformanceStatus['performanceInstrument'].append(line_result)
        elif data_sub_key == 'Input Numeric Score':
            if entry[8] == 'Quality of Life Assessment':
                otvQualityOfLife['qualityOfLifeScore'].append(line_result)
            elif entry[8] == 'Performance Status':
                otvPerformanceStatus['performanceScore'].append(line_result)


        #elif data_sub_key == '--Select Instrument--': #FIXME - check for SCLC
        #    otvQualityOfLife['qualityOfLifeInstrument'].append(line_result)
        #elif data_sub_key == 'Input Numeric Score':
        #    otvQualityOfLife['qualityOfLifeScore'].append(line_result)

    otvs = process_multi_otvs(otvToxicities, otvQualityOfLife, otvPerformanceStatus, otvAssessments) #FIXME <-------------------------------------- AT Performance Status
    #print("***")
    #pprint(len(otvs))
    #print("***")
    for tag in otvAssessments:
        for entry in otvAssessments[tag]:
            otvs[entry[0]][tag] = entry[2]
    final_otvs = []
    for otv in otvs:
     #   print(otv)
        if otv != {"toxicity": [{}], "qualityOfLife": [{}]}:
            final_otvs.append(otv)
       # final_otvs.append(otv)   #bug-  added extra copy of each otv
    json_data['otv'] = final_otvs
    #pprint(len(json_data['otv']))


def process_survivorship(data_lines, disease_site):
    global json_data

    survivorship = {}
    for line in data_lines:
        data_key = line[8]
        sub_group = line[7]
        value = line[11]
        if data_key == 'Survivorship Care Plan Mention':
            survivorship['survivorshipCarePlanSource'] = value
        elif data_key == 'Survivorship Care Plan Mention Date':
            survivorship['survivorshipCarePlanMentionDate'] = convert_date(value)
        elif data_key == 'Is There a Survivorship Care Plan Report Date?':
            survivorship['isSurvivorshipCarePlanReportDate'] = value
        elif data_key == 'Survivorship Care Plan Report Date':
            survivorship['survivorshipCarePlanReportDate'] = convert_date(value)
        elif data_key == 'Survivorship Care Plan':
            care_plans = []
            if 'NULL' not in value:
                for item in value:
                    if item == 'Relevant Assessment of tolerance to and progress towards the treatment goals':
                        item = 'Relevant assessment of tolerance to and progress towards the treatment goals'
                    care_plans.append({'carePlan': item})
            survivorship['survivorshipCarePlan'] = care_plans
    json_data['survivorship'] = survivorship


def process_follow_up(data_lines, disease_site):
    global json_data

    followup_arrays = {'Follow-Up': [], 'Quality of Life': [], 'Toxicity': [], 'Toxicity Grades': []}

    max_count = 0
    for line in data_lines:
        followup_arrays[line[7]].append(line)
        if int(line[12]) > max_count:
            max_count = int(line[12])
    max_count += 1

    followups = [{} for x in range(0, max_count)]
    for line in followup_arrays['Follow-Up']:
        data_key = line[8]
        value = line[11]
        index = int(line[12])
        if data_key == 'Patient Status':
            followups[index]['patientStatus'] = value
        elif data_key == 'Patient Progression':
            followups[index]['patientProgression'] = value
        #elif data_key == 'Reason(s) for Treatment Incompletion':
        #    print('***************', value)
        #    followups[index]['reasonForTreatmentIncompletion'] = value
        elif data_key == 'Follow-Up Date':
            followups[index]['followUpDate'] = convert_date(value)
        elif data_key == 'Date of Death':
            followups[index]['dateOfDeath'] = convert_date(value)

    quality_of_life_counts = [-1 for x in range(0, max_count)]
    for line in followup_arrays['Quality of Life']:
        index = int(line[12])
        sub_index = int(line[13])
        if sub_index > quality_of_life_counts[index]:
            quality_of_life_counts[index] = sub_index
    for index, value in enumerate(quality_of_life_counts):
        quality_of_life_counts[index] += 1
        if quality_of_life_counts[index] > 0:
            followups[index]['qualityOfLifeScore'] = [{} for x in range(0, quality_of_life_counts[index])]

    for line in followup_arrays['Quality of Life']:
        sub_group = line[9]
        value = line[11]
        index = int(line[12])
        sub_index = int(line[13])
        if sub_group == '--Select Instrument--':
            followups[index]['qualityOfLifeScore'][sub_index]['qualityOfLifeInstrument'] = value
        elif sub_group == 'Input Numeric Score':
            #print(value)
            followups[index]['qualityOfLifeScore'][sub_index]['qualityOfLifeScore'] = float(value)

    if len(followup_arrays['Toxicity']) > 0:
        tox_key = 'Toxicity'
    elif len(followup_arrays['Toxicity Grades']) > 0:
        tox_key = 'Toxicity Grades'
    else:
        tox_key = None

    if tox_key:
        tox_max = 0
        for line in followup_arrays[tox_key]:
            if int(line[13]) > tox_max:
                tox_max = int(line[13])
        tox_max += 1
        toxicity_count = [0 for x in range(0, max_count)]

        for line in followup_arrays[tox_key]:
            index = int(line[12])
            sub_index = int(line[13])
            if sub_index > toxicity_count[index]:
                toxicity_count[index] = sub_index

        for index, value in enumerate(quality_of_life_counts):
            toxicity_count[index] += 1
            followups[index]['toxicity'] = [{} for x in range(0, toxicity_count[index])]
        for line in followup_arrays[tox_key]:
            sub_group = line[9]
            value = line[11]
            index = int(line[12])
            sub_index = int(line[13])
            if sub_group == '--Select Toxicity--':
                followups[index]['toxicity'][sub_index]['toxicity'] = value
            elif sub_group == '--Select System--':
                if value == 'No Toxicity':
                    value = 'Not Stated'
                followups[index]['toxicity'][sub_index]['system'] = value
            elif sub_group == '--Select Grade--':
                followups[index]['toxicity'][sub_index]['grade'] = value
        json_data['followUp'] = followups


def process_technical_validation(data_lines, disease_site):
    global json_data

    technical_validation_arrays = {'External Beam Plan': [], 'HDR Plan Information': [], 'LDR Plan Information': [], 'Other Information': [], 'PCI': []}

    for line in data_lines:
        data_key = line[7]
        technical_validation_arrays[data_key].append(line)

    # external beam
    max_external_beam_count = 0
    for entry in technical_validation_arrays['External Beam Plan']:
        index = int(entry[13])
        if index > max_external_beam_count:
            max_external_beam_count = index
    max_external_beam_count += 1
    external_beam = [{} for x in range(0, max_external_beam_count)]
    for line in technical_validation_arrays['External Beam Plan']:
        other = line[7]
        data_key = line[8]
        sub_key = line[9]
        value = line[11]
        index = int(line[13])
        print(data_key)
        if data_key == 'Modality':
            external_beam[index]['modality'] = value


        elif data_key == 'Whole Pelvis':
            external_beam[index]['wholePelvis'] = value
        elif data_key == 'Prescription':
            external_beam[index]['prescriptionDose'] = value
        elif data_key == 'Fractions':
            external_beam[index]['fractions'] = value
        elif data_key == 'Treatment Completion':
            external_beam[index]['treatmentCompletion'] = value
        elif data_key == 'Number of Fractions Completed':
            external_beam[index]['fractionsCompleted'] = value
        elif data_key == 'External Beam Plan Date' or other == 'External Beam Plan':
            if sub_key == 'Start Date':
                external_beam[index]['startDate'] = convert_date(value)
            elif sub_key == 'End Date':
                external_beam[index]['endDate'] = convert_date(value)



        #elif data_key == 'TreatmeNumber of Fractions Completednt Completion':
        #    external_beam[index]['treatmentCompletion'] = value
        #elif data_key == '':
        #    external_beam[index]['fractionsCompleted'] = value
    json_data[disease_site.lower() + 'ExternalBeamPlan'] = external_beam

    if disease_site.lower() == 'prostate':
        # LDR
        ldr_count = 0
        for entry in technical_validation_arrays['LDR Plan Information']:
            index = int(entry[12])
            if index > ldr_count:
                ldr_count = index
        ldr_count += 1
        ldr = [{} for x in range(0, ldr_count)]
        for line in technical_validation_arrays['LDR Plan Information']:
            data_key = line[8]
            value = line[11]
            index = int(line[13])
            if data_key == 'Prescription':
                ldr[index]['prescriptionDose'] = value
            elif data_key == 'Date of Implant':
                ldr[index]['implantDate'] = convert_date(value)
            elif data_key == 'Is There a Post-Treatment Dosimetry?':
                ldr[index]['isPostDosimetry'] = value
            elif data_key == 'Post-Treatment Dosimetry':
                ldr[index]['postTreatmentDosimetry'] = convert_date(value)
            elif data_key == 'Post-Treatment Evaluation':
                ldr[index]['postTreatmentEvaluation'] = value
            #FIXME
            #elif data_key == 'Post-Treatment Evaluation':
            #    ldr[index]['postTreatmentEvaluation'] = value
        json_data[disease_site.lower() + 'LdrPlan'] = [x for x in ldr if len(x) > 0]

        # HDR
        hdr_count = 0
        for entry in technical_validation_arrays['HDR Plan Information']:
            index = int(entry[12])
            if index > hdr_count:
                hdr_count = index
            hdr_count += 1
        hdr = [{} for x in range(0, hdr_count)]
        for line in technical_validation_arrays['HDR Plan Information']:
            data_key = line[8]
            value = line[11]
            index = int(line[13])
            if data_key == 'Prescription':
                hdr[index]['prescriptionDose'] = value
            elif data_key == 'Date of Implant':
                hdr[index]['implantDate'] = convert_date(value)
            elif data_key == 'Is There a Post-Treatment Dosimetry?':
                hdr[index]['isPostDosimetry'] = value
            elif data_key == 'Post-Treatment Dosimetry':
                hdr[index]['postTreatmentDosimetry'] = value
            elif data_key == 'Post-Treatment Evaluation':
                hdr[index]['postTreatmentEvaluation'] = value
        json_data[disease_site.lower() + 'HdrPlan'] = [x for x in hdr if len(x) > 0]
    else:
        if disease_site.lower() == 'sclc':
            # PCI
            pci = {}
            for line in technical_validation_arrays['PCI']:
                data_key = line[8]
                sub_key = line[9]
                value = line[11]
                if data_key == 'Common Prescription':
                    pci['commonPrescription'] = value
                elif data_key == 'Prescription':
                    pci['prescriptionDose'] = value
                elif data_key == 'Fractions':
                    pci['fractions'] = int(value)
                elif data_key == 'Date':
                    if sub_key == 'Start Date':
                        pci['startDate'] = convert_date(value)
                    elif sub_key == 'End Date':
                        pci['endDate'] = convert_date(value)
                elif data_key == 'Treatment Completion':
                    pci['treatmentCompletion'] = value
                elif data_key == 'Number of Fractions Completed':
                    pci['fractionsCompleted'] = value
            json_data['sclcPci'] = pci
            # Other information

    other_information = {}
    for line in technical_validation_arrays['Other Information']:
        data_key = line[8]
        sub_key = line[9]
        value = line[11]
        if data_key == 'Is There a Date of Simulation?':
            other_information['isDateOfSimulation'] = value
        elif data_key == 'Simulation Date':
            other_information['simulationDate'] = convert_date(value)
        elif data_key == 'DVH Analysis':
            other_information['dhvAnalysis'] = value
        elif data_key == 'Structures Evaluated':
            other_information[disease_site.lower() + 'DvhEvaluatedStructures'] = []
            for item in value:
                other_information[disease_site.lower() + 'DvhEvaluatedStructures'].append({'structuresEvaluated': item.strip()})
        elif data_key == 'Motion Management':
            other_information[disease_site.lower() + 'MotionManagement'] = []
            for item in value:
                other_information[disease_site.lower() + 'MotionManagement'].append({'motionManagementMethod': item.strip()})
        elif data_key == 'Daily Target Localization':
            other_information['dailyTargetLocalization'] = value
        elif data_key == 'Immobilization':
            other_information['immobilization'] = value
        elif data_key == 'In SIM Note or Site Setup?' or data_key == 'In SIM Note?':
            if value == 'No SIM Note Found':
                value = 'No'
            other_information['isSimNoteOrSiteSetup'] = value
        elif data_key == 'Planning Algorithm':
            other_information['planningAlgorithm'] = value
        elif data_key == 'Laterality':
            other_information['laterality'] = value

    json_data[disease_site.lower() + 'OtherInformation'] = other_information


def reformat_data(json_data):
    updated_data = {}
    updated_data['caseId'] = json_data['caseId']
        #updated_data['patientInformation'] = json_data['patientInformation']
        #updated_data['isSurgery'] = json_data['patientInformation']['surgery']
    updated_data['tumorType'] = json_data['patientInformation']['tumorType']


    #updated_data['vitals'] = {}
    #updated_data['allergies'] = {}
    #updated_data['labs'] = {}
    #updated_data['surgeryList'] = {}

    current_cprs = None

    if json_data['caseId'] in cprs_data:
        current_cprs = cprs_data[json_data['caseId']]
        updated_data['activeMeds'] = current_cprs['medication']
        updated_data['insurance'] = {}#current_cprs['insurance']
        updated_data['problemList'] = process_problem_list(current_cprs['problem_list'])

        updated_data['patientDemographics'] = {'ageAtDiagnosis': current_cprs['ageAtDiagnosis'],
                                               'dataOfDeath': current_cprs['dataOfDeath'],
                                               'ethnicity': current_cprs['ethnicity'], 'race': current_cprs['race'],
                                               'gender': current_cprs['gender'], 'weight': current_cprs['weight'],
                                               'height': current_cprs['height'], 'zipCode': current_cprs['zipCode']
                                            }
    updated_data['consult'] = []

    current_consult = {}
    try:
        current_consult['visitDate'] = json_data['patientInformation']['dateOfROConsult']
    except KeyError:
        pass
    #try:
    #    current_consult['chiefComplaint'] = json_data['patientInformation']['tumorType'] + " cancer"
    #except KeyError:
    #    pass
    try:
        current_consult['qualityOfLife'] = json_data['qualityOfLife']
        print("here")
        print(current_consult['qualityOfLife'])
    except KeyError:
        print("XXX")
        pass

    if 'performanceStatus' in json_data:
        # Grab first if multiples were somehow added
        if len(json_data['performanceStatus']) > 0:
            current_consult['performanceStatus'] = json_data['performanceStatus'][0]

    try:
        current_consult['adtDuration'] = json_data['prostateAdt']['durationIntentOfADT']
    except KeyError:
        pass

    try:
        current_consult['discussedTreatmentOptions'] = []
        for item in json_data['prostateTreatmentOptions']:
            current_consult['discussedTreatmentOptions'].append(item['treatmentTechnique'])
    except KeyError:
        pass

    tumor_type_lower = updated_data['tumorType'].lower()
    history_label = tumor_type_lower + 'History'

    if history_label in json_data:
        if 'currentSmokingStatus' in json_data[history_label]:
            current_consult['currentSmokingStatus'] = json_data[history_label]['currentSmokingStatus']
        if 'smokingCessation' in json_data[history_label]:
            current_consult['smokingCessationPlan'] = json_data[history_label]['smokingCessation']
        #if 'implantableCardiacDevice' in json_data[historyLabel]:
        #    current_consult['cardiacDeviceImplanted'] = json_data[historyLabel]['implantableCardiacDevice']
        if 'implantableCardiacDeviceDate' in json_data[history_label]:
            current_consult['implantableCardiacDeviceDate'] = json_data[history_label]['implantableCardiacDeviceDate']
        if 'multidisciplinaryConsult' in json_data[history_label]:
            current_consult['multidisciplinaryConsultType'] = json_data[history_label]['multidisciplinaryConsult']
        if 'multidisciplinaryConsultDate' in json_data[history_label]:
            current_consult['multidisciplinaryConsultDate'] = json_data[history_label]['multidisciplinaryConsultDate']
    updated_data['consult'].append(current_consult)

    # OTVs
    updated_data['otv'] = []
    #pprint(json_data['otv'])

    for otv in json_data['otv']:
        current_otv = dict()
        if 'otvAssessmentDate' in otv:
            current_otv['visitDate'] = otv['otvAssessmentDate']
        current_otv['toxicity'] = []

        for toxicity in otv['toxicity']:
            current_toxicity = {}
            if 'grade' in toxicity:
                current_toxicity['grade'] = toxicity['grade']
            if 'toxicity' in toxicity:
                current_toxicity['toxicity'] = toxicity['toxicity']
            if 'system' in toxicity:
                current_toxicity['system'] = toxicity['system']
            if len(current_toxicity) > 0:
                current_otv['toxicity'].append(current_toxicity)

        if 'qualityOfLife' in otv:
            if otv['qualityOfLife'] != [{}]:
                current_otv['qualityOfLife'] = otv['qualityOfLife']
            else:
                current_otv['qualityOfLife'] = {}
        if 'performanceStatus' in otv:
            # Grab first if multiples were somehow added
            if len(otv['performanceStatus']) > 0:
                current_otv['performanceStatus'] = otv['performanceStatus'][0]
            #print(current_otv)
        updated_data['otv'].append(current_otv)

    # Follow ups
    updated_data['followUp'] = []
    #print("**** follow up *****")
    #pprint(json_data['followUp'])
    #print("*****")

    if 'followUp' in json_data:
        for follow_up in json_data['followUp']:
            current_follow_up = dict()
            if 'followUpDate' in follow_up:
                current_follow_up['visitDate'] = follow_up['followUpDate']
            if 'patientProgression' in follow_up:
                current_follow_up['diseaseProgression'] = follow_up['patientProgression']

            if 'toxicity' in follow_up:
                current_follow_up['toxicity'] = []
                print('toxicity count: ' + str(len(follow_up['toxicity'])))
                for toxicity in follow_up['toxicity']:
                    current_toxicity = {}
                    if 'grade' in toxicity:
                        current_toxicity['grade'] = toxicity['grade']
                    if 'toxicity' in toxicity:
                        current_toxicity['toxicity'] = toxicity['toxicity']
                    if 'system' in toxicity:
                        current_toxicity['system'] = toxicity['system']
                    current_follow_up['toxicity'].append(current_toxicity)
            print('Final tox count: ' + str(len(current_follow_up['toxicity'])))
            if 'qualityOfLifeScore' in follow_up:
                current_follow_up['qualityOfLife'] = follow_up['qualityOfLifeScore']
            # Performance status was not recorded in follow ups
            if len(current_follow_up) > 0:
                updated_data['followUp'].append(current_follow_up)
        
        #pprint(updated_data['followUp'])

    if 'survivorship' in json_data:
        if 'survivorshipCarePlanReportDate' in json_data['survivorship']:
            date_to_use = json_data['survivorship']['survivorshipCarePlanReportDate']
        elif 'survivorshipCarePlanMentionDate' in json_data['survivorship']:
            date_to_use = json_data['survivorship']['survivorshipCarePlanMentionDate']

        #FIXME - deal with issue related to missing follow up dates
        try:
            for follow_up in updated_data['followUp']:
                if follow_up['visitDate'] == date_to_use:
                    print("matching: " + date_to_use)
                    if 'survivorshipCarePlan' in json_data['survivorship']:
                        print("!!!!!!!!!!!!!")
                        pprint(json_data['survivorship']['survivorshipCarePlan'])
                        care_plans = []
                        for item in json_data['survivorship']['survivorshipCarePlan']:
                            for x in item:
                                care_plans.append(item[x])
                        if len(care_plans) > 0:
                            follow_up['survivorshipCarePlan'] = care_plans
                        #follow_up['survivorshipCarePlan'] = json_data['survivorship']['survivorshipCarePlan']
            #pprint(json_data['survivorship'])
        except:
            pass

    #pprint(updated_data['followUp'])
    if 'clinicalTrials' in json_data:
        updated_data['clinicalTrials'] = []
        current_trial = {}
        if 'clinicalTrialNumber' in json_data['clinicalTrials']:
            current_trial['trialNumber'] = json_data['clinicalTrials']['clinicalTrialNumber']
        if 'clinicalTrialEnrollmentDate' in json_data['clinicalTrials']:
            current_trial['enrollmentDate'] = json_data['clinicalTrials']['clinicalTrialEnrollmentDate']
        if 'clinicalTrialEnrollment' in json_data['clinicalTrials']:
            current_trial['enrollmentStatus'] = json_data['clinicalTrials']['clinicalTrialEnrollment']
        updated_data['clinicalTrials'].append(current_trial)

    if tumor_type_lower + 'Pathology' in json_data:
        pathology = json_data[tumor_type_lower + 'Pathology']

        pprint(json_data[tumor_type_lower + 'Pathology'])
        updated_data['pathology'] = {}

        if 'pathologyReportDate' in pathology:
            updated_data['pathology']['pathologyReportDate'] = pathology['pathologyReportDate']
        if 'pathologyReportType' in pathology:
            updated_data['pathology']['pathologyReportType'] = pathology['pathologyReportType']
        if 'noPathologyReportReason' in pathology:
            updated_data['pathology']['reasonForNoPathologyReport'] = pathology['noPathologyReportReason']

    if tumor_type_lower + 'Molecular' in json_data:
        molecular = json_data[tumor_type_lower + 'Molecular']
        updated_data['molecular'] = {}
        # FIXME - which should be the primary value?
        if 'molecularInformationDate' in molecular:
            updated_data['molecular']['molecularInformationDate'] = molecular['molecularInformationDate']
        elif 'molecularInformationReportDate' in molecular:
            updated_data['molecular']['molecularInformationDate'] = molecular['molecularInformationReportDate']
        if 'molecularInformationType' in molecular:
            updated_data['molecular']['molecularInformationType'] = molecular['molecularInformationType']
        if 'noMolecularInformationReportReason' in molecular:
            updated_data['molecular']['reasonForNoMolecularReport'] = molecular['noMolecularInformationReportReason']

    if tumor_type_lower + 'Chemotherapy' in json_data:
        chemotherapy = json_data[tumor_type_lower + 'Chemotherapy']
        updated_chemo = []
        for entry in chemotherapy:
            updated_chemo.append({'chemotherapyStartDate': entry['chemotherapyStartDate'], 'chemotherapyEndDate':
                entry['chemotherapyEndDate']})
        updated_data['chemotherapy'] = updated_chemo


    updated_diagnosis = {}
    scoringAndGrades = tumor_type_lower + 'ScoringAndGrades'
    updated_diagnosis['tumorType'] = updated_data['tumorType']
    if 'icdCode' in json_data['patientInformation']:
        updated_diagnosis['icdCode'] = json_data['patientInformation']['icdCode']
    if 'recurrentDisease' in json_data['patientInformation']:
        updated_diagnosis['recurrentDisease'] = json_data['patientInformation']['recurrentDisease']
    if 'surgeryDate' in json_data['patientInformation']:
        updated_diagnosis['surgeryDate'] = json_data['patientInformation']['surgeryDate']

    if 'Surgery' in updated_data['caseId']:
        updated_diagnosis['previousSurgery'] = 'Yes'
    else:
        updated_diagnosis['previousSurgery'] = 'No'

    if scoringAndGrades in json_data:
        if 'TX' in json_data[scoringAndGrades]:
            updated_diagnosis['tStage'] = json_data[scoringAndGrades]['TX']
        if 'NX' in json_data[scoringAndGrades]:
            updated_diagnosis['nStage'] = json_data[scoringAndGrades]['NX']
        if 'MX' in json_data[scoringAndGrades]:
            updated_diagnosis['mStage'] = json_data[scoringAndGrades]['MX']
        if 'overallTumorStage' in json_data[scoringAndGrades]:
            updated_diagnosis['clinicalStage'] = json_data[scoringAndGrades]['overallTumorStage']

        if 'tnmTumorStageDate' in json_data[scoringAndGrades]:
            updated_diagnosis['tnmTumorStageDate'] = convert_date(json_data[scoringAndGrades]['tnmTumorStageDate'])
        #else:
        #    updated_diagnosis['clinicalStageDate'] = "2010-01-01"

        if 'overallTumorStageDate' in json_data[scoringAndGrades]:
            updated_diagnosis['clinicalStageDate'] = json_data[scoringAndGrades]['overallTumorStageDate']
        #else:
        #    updated_diagnosis['clinicalStageDate'] = "2010-01-01"

        gleasonScore = {}
        if 'primaryGS' in json_data[scoringAndGrades]:
            gleasonScore['primaryGS'] = int(json_data[scoringAndGrades]['primaryGS'])
        if 'secondaryGS' in json_data[scoringAndGrades]:
            gleasonScore['secondaryGS'] = int(json_data[scoringAndGrades]['secondaryGS'])
        if 'totalGS' in json_data[scoringAndGrades]:
            gleasonScore['totalGS'] = int(json_data[scoringAndGrades]['totalGS'])
        if 'gleasonDate' in json_data[scoringAndGrades]:
            gleasonScore['gleasonDate'] = json_data[scoringAndGrades]['gleasonDate']
        if len(gleasonScore) > 0:
            updated_diagnosis['gleasonScore'] = gleasonScore

        psa = {}
        if 'PSACount' in json_data[scoringAndGrades]:
            psa['psaScore'] = float(json_data[scoringAndGrades]['PSACount'])
        #FIXME - don't think ROPA data had any PSA dates or a tag for it
        if 'PSADate' in json_data[scoringAndGrades]:
            psa['PSADate'] = convert_date(json_data[scoringAndGrades]['PSADate'])
        if len(psa) > 0:
            updated_diagnosis['psa'] = [psa]

        if 'riskGroup' in json_data[scoringAndGrades]:
            updated_diagnosis['nccnRiskCategory'] = json_data[scoringAndGrades]['riskGroup']
        if 'riskGroupDate' in json_data[scoringAndGrades]:
            updated_diagnosis['nccnRiskCategoryDate'] = convert_date(json_data[scoringAndGrades]['riskGroupDate'])

        if 'nsclcClassificationDate' in json_data[scoringAndGrades]:
            updated_diagnosis['nsclcClassificationDate'] = json_data[scoringAndGrades]['nsclcClassificationDate']
        if 'nsclcClassificationType' in json_data[scoringAndGrades]:
            updated_diagnosis['nsclcClassificationType'] = json_data[scoringAndGrades]['nsclcClassificationType']

    updated_data['diagnosis'] = updated_diagnosis

    if 'prostateAdt' in json_data:
        if 'prostateAdtInjection' in json_data['prostateAdt']:
            updated_data['adtInjections'] = json_data['prostateAdt']['prostateAdtInjection']
            for entry in updated_data['adtInjections']:
                if 'adtInjectionDose' in entry:
                    entry['adtInjectionDose'] = float(entry['adtInjectionDose'])

    updated_data['diagnosticImaging'] = {}
    if 'imagingStudies' in json_data['consult']:
        if 'boneDensityAssessment' in json_data['consult']['imagingStudies']:
            updated_data['diagnosticImaging']['boneDensityAssessment'] = json_data['consult']['imagingStudies']['boneDensityAssessment']
        if 'boneDensityDate' in json_data['consult']['imagingStudies']:
            updated_data['diagnosticImaging']['boneDensityDate'] = json_data['consult']['imagingStudies']['boneDensityDate']

        if 'boneScanType' in json_data['consult']['imagingStudies']:
            updated_data['diagnosticImaging']['boneScanType'] = json_data['consult']['imagingStudies'][
                'boneScanType']
        if 'boneScanReportDate' in json_data['consult']['imagingStudies']:
            updated_data['diagnosticImaging']['boneScanDate'] = json_data['consult']['imagingStudies'][
                'boneScanReportDate']
        if 'boneScanType' in updated_data['diagnosticImaging'] or 'boneScanDate' in updated_data['diagnosticImaging']:
            updated_data['diagnosticImaging']['boneScan'] = 'Yes'
        else:
            updated_data['diagnosticImaging']['boneScan'] = 'No'

        if 'pelvicCtReportDate' in json_data['consult']['imagingStudies']:
            updated_data['diagnosticImaging']['ctDate'] = json_data['consult']['imagingStudies']['pelvicCtReportDate']
        if 'pelvicCtReportDate' in json_data['consult']['imagingStudies'] or 'pelvicCTSource' in json_data['consult']['imagingStudies'] or 'pelvicCtMentionDate' in json_data['consult']['imagingStudies']:
            updated_data['diagnosticImaging']['ct'] = 'Yes'

        if 'pelvicMriReportDate' in json_data['consult']['imagingStudies']:
            updated_data['diagnosticImaging']['mriDate'] = json_data['consult']['imagingStudies']['pelvicMriReportDate']
        if 'pelvicMriReportDate' in json_data['consult']['imagingStudies'] or 'pelvicMRISource' in json_data['consult']['imagingStudies'] or 'pelvicMriMentionDate' in json_data['consult']['imagingStudies']:
            updated_data['diagnosticImaging']['mri'] = 'Yes'
        else:
            updated_data['diagnosticImaging']['mri'] = 'No'

        if 'mriOfBrainReportDate' in json_data['consult']['imagingStudies']:
            updated_data['diagnosticImaging']['mriDate'] = json_data['consult']['imagingStudies']['mriOfBrainReportDate']
        if 'mriOfBrainReportDate' in json_data['consult']['imagingStudies'] or 'mriOfBrainSource' in json_data['consult'][
            'imagingStudies'] or 'mriOfBrainMentionDate' in json_data['consult']['imagingStudies']:
            updated_data['diagnosticImaging']['mri'] = 'Yes'

        if 'petctReportDate' in json_data['consult']['imagingStudies']:
            updated_data['diagnosticImaging']['petctDate'] = json_data['consult']['imagingStudies']['petctReportDate']
        if 'petctReportDate' in json_data['consult']['imagingStudies'] or 'petctSource' in json_data['consult'][
            'imagingStudies'] or 'petctMentionDate' in json_data['consult']['imagingStudies']:
            updated_data['diagnosticImaging']['petct'] = 'Yes'

          # [updated_treatment_summary]
        current_treatments = {}

        pci_treatment = {}
        if 'sclcPci' in json_data:
            if 'commonPrescription' in json_data['sclcPci']:
                pci_treatment['commonPrescription'] = json_data['sclcPci']['commonPrescription']
            if 'prescriptionDose' in json_data['sclcPci']:
                pci_treatment['prescriptionDose'] = float(json_data['sclcPci']['prescriptionDose'])
            if 'fractions' in json_data['sclcPci']:
                pci_treatment['numberOfPlannedFractions'] = int(json_data['sclcPci']['fractions'])
            if 'fractionsCompleted' in json_data['sclcPci']:
                pci_treatment['numberOfDeliveredFractions'] = int(json_data['sclcPci']['fractionsCompleted'])
            if 'startDate' in json_data['sclcPci']:
                pci_treatment['startDate'] = json_data['sclcPci']['startDate']
            if 'endDate' in json_data['sclcPci']:
                pci_treatment['endDate'] = json_data['sclcPci']['endDate']
            if 'treatmentCompletion' in json_data['sclcPci']:
                if json_data['sclcPci']['treatmentCompletion'] == 'Yes':
                    pci_treatment['treatmentStatus'] = 'Completed'
                elif json_data['sclcPci']['treatmentCompletion'] == 'No':
                    pci_treatment['treatmentStatus'] = 'Not Completed'
            if len(pci_treatment) > 0:
                current_treatments['pci'] = pci_treatment

        #ldr = json_data[tumor_type_lower + 'LdrPlan']
        #pprint("***")
        #pprint(ldr)
        #pprint("***")

        ldr_treatments = []
        if tumor_type_lower + 'LdrPlan' in json_data:
            ldr_data = json_data[tumor_type_lower + 'LdrPlan']
            for tx in ldr_data:
                current_ldr_tx = {}
                if 'implantDate' in tx:
                    current_ldr_tx['implantDate'] = tx['implantDate']
                if 'isPostDosimetry' in tx:
                    current_ldr_tx['postDosimetryPeformed'] = tx['isPostDosimetry']
                if 'postTreatmentDosimetry' in tx:
                    current_ldr_tx['postTreatmentEvaluationDate'] = tx['postTreatmentDosimetry']
                if 'postTreatmentEvaluation' in tx:
                    current_ldr_tx['postTreatmentEvaluation'] = tx['postTreatmentEvaluation']
                if 'prescriptionDose' in tx:
                    current_ldr_tx['prescriptionDose'] = float(tx['prescriptionDose'])
                if len(current_ldr_tx) > 0:
                    ldr_treatments.append(current_ldr_tx)
        if len(ldr_treatments) > 0:
            current_treatments['ldr'] = ldr_treatments

        external_beam_treatments = []
        if tumor_type_lower.lower() + 'ExternalBeamPlan' in json_data:
            ebrt_data = json_data[tumor_type_lower.lower() + 'ExternalBeamPlan']
            for tx in ebrt_data:
                current_ebrt_tx = {}
                if 'modality' in tx:
                    current_ebrt_tx['modality'] = tx['modality']
                if 'wholePelvis' in tx:
                    current_ebrt_tx['wholePelvis'] = tx['wholePelvis']
                if 'prescriptionDose' in tx:
                    current_ebrt_tx['prescriptionDose'] = float(tx['prescriptionDose'])
                if 'fractions' in tx:
                    current_ebrt_tx['numberOfPlannedFractions'] = int(tx['fractions'])
                if 'startDate' in tx:
                    current_ebrt_tx['startDate'] = tx['startDate']
                if 'endDate' in tx:
                    current_ebrt_tx['endDate'] = tx['endDate']
                if 'treatmentCompletion' in tx:
                    current_ebrt_tx['treatmentStatus'] = tx['treatmentCompletion']
                if 'fractionsCompleted' in tx:
                    current_ebrt_tx['numberOfDeliveredFractions'] = int(tx['fractionsCompleted'])

                if 'treatmentCompletion' in tx:
                    if tx['treatmentCompletion'] == 'Yes':
                        current_ebrt_tx['treatmentStatus'] = 'Completed'
                    elif tx['treatmentCompletion'] == 'No':
                        current_ebrt_tx['treatmentStatus'] = 'Not Completed'

                if len(current_ebrt_tx) > 0:
                    external_beam_treatments.append(current_ebrt_tx)
            if len(external_beam_treatments) > 0:
                current_treatments['ebrt'] = external_beam_treatments


        other_information = {}
        other_data = json_data[tumor_type_lower.lower() + 'OtherInformation']

        print("***")
        pprint(other_data)
        print("***")
        pass

        if 'simulationDate' in other_data:
            other_information['dateOfSimulation'] = other_data['simulationDate']
        if 'dhvAnalysis' in other_data:
            other_information['dvhAnalysisPerformed'] = other_data['dhvAnalysis']
        if 'dailyTargetLocalization' in other_data:
            other_information['dailyTargetLocalization'] = other_data['dailyTargetLocalization']
        if 'immobilization' in other_data:
            other_information['immbolizationMethods'] = other_data['immobilization']
        if 'isSimNoteOrSiteSetup' in other_data:
            pass
        if 'prostateDvhEvaluatedStructures' in other_data:
            other_information['dvhStructuresEvaluated'] = []
            for item in other_data['prostateDvhEvaluatedStructures']:
                for x in item:
                    other_information['dvhStructuresEvaluated'].append(item[x])
                print(item)
        if len(other_information) > 0:
            current_treatments['otherInformation'] = other_information

        updated_data['treatmentSummary'] = [current_treatments]

    '''
     
     
              
    '''

    pprint(json_data['consult']['imagingStudies'])

    #pprint(chemotherapy)
    #try:
    #    current_consult['isStagingComplete'] = "Yes"
    #except KeyError:
    #    pass
    #try:
    #    current_consult['diagnosticTests'] = {}
    #except KeyError:
    #    pass

    #pprint(json_data['prostateImagingStudies'])
    '''
    diagnostic_tests = {}
    try:
        diagnostic_tests['boneDensityAssessment'] = json_data['prostateImagingStudies'][
            'boneDensityAssessment']
    except KeyError:
        pass
    try:
        diagnostic_tests['boneScanDate'] = json_data['prostateImagingStudies'][
            'boneScanReportDate']
    except KeyError:
        pass
    try:
        diagnostic_tests['boneScanType'] = json_data['prostateImagingStudies'][
            'boneScanType']
    except KeyError:
        pass
    try:
        diagnostic_tests['pelvisCtDate'] = json_data['prostateImagingStudies'][
            'pelvicCtReportDate']
    except KeyError:
        pass
    try:
        diagnostic_tests['prostateMriDate'] = json_data['prostateImagingStudies'][
            'pelvicMriReportDate']
    except KeyError:
        pass
    # "priorHormones": "No",
    updated_data['diagnosticTests'] = diagnostic_tests

    diagnosis = {}
    diagnosis['icdCode'] = json_data['patientInformation']['icdCode']
    try:
        diagnosis['nccnRiskCategory'] = json_data['prostateScoringAndGrades']['riskGroup']
    except KeyError:
        pass
    try:
        diagnosis['tStage'] = json_data['prostateScoringAndGrades']['TX']
    except KeyError:
        pass
    try:
        diagnosis['nStage'] = json_data['prostateScoringAndGrades']['NX']
    except KeyError:
        pass
    try:
        diagnosis['mStage'] = json_data['prostateScoringAndGrades']['MX']
    except KeyError:
        pass
    #diagnosis['groupStage'] = json['prostateScoringAndGrades']['']
    diagnosis['gleasonScore'] = {}
    try:
        diagnosis['gleasonScore']['primaryGleasonScore'] = json_data['prostateScoringAndGrades']['primaryGS']
    except KeyError:
        pass
    try:
        diagnosis['gleasonScore']['secondaryGleasonScore'] = json_data['prostateScoringAndGrades']['secondaryGS']
    except KeyError:
        pass
    try:
        diagnosis['gleasonScore']['totalGleasonScore'] = json_data['prostateScoringAndGrades']['totalGS']
    except KeyError:
        pass

    try:
        diagnosis['surgery'] = json_data['patientInformation']['surgery']
    except KeyError:
        pass
    #diagnosis['surgeryDate'] = json_data['patientInformation']['surgeryDate']
    try:
        diagnosis['recurrentDisease'] = json_data['patientInformation']['recurrentDisease']
    except KeyError:
        pass

    try:
        diagnosis['psaValues'] = [{'psaScore': json_data['prostateScoringAndGrades']['PSACount']}]
    except KeyError:
        pass

    try:
        diagnosis['prostateAdt'] = json_data['prostateAdt']
    except KeyError:
        pass



    diagnosis['tumorType'] = updated_data['tumorType']


    updated_data['diagnosis'] = diagnosis
    updated_data['consult'].append(current_consult)


    ### Treatment ###
    treatment = {}
    treatment['treatmentIntent'] = 'Definitive'
    treatment['organsAtRisk'] = ''
    treatment['isStagingComplete'] = 'Yes'
    treatment['wasTreatmentCompleted'] = 'Yes'
    updated_data['treatment'] = treatment


    ### Patient History ###
    patient_history = {}
    if current_cprs:
        patient_history['familtyHistoryOfDifferentCancerReported'] = current_cprs['familtyHistoryOfDifferentCancerReported']
        patient_history['familtyHistoryOfSameCancerReported'] = current_cprs['familtyHistoryOfSameCancerReported']
    updated_data['patientHistory'] = patient_history



    ##### Sim Directive ###
    # None

    ##### Pre-Treatment ###
    # None

    ##### TreatmentPlan ###
    treatment_plan = {}

    treatment_plan['isStagingComplete'] = 'Yes'
    treatment_plan['isStagingComplete'] = 'Definitive'
    try:
        treatment_plan['immoblizationMethod'] = json_data['prostateOtherInformation']['immobilization']
    except KeyError:
        pass
    treatment_plan['treatmentCourseNumber'] = 1
    updated_data['treatmentPlan'] = treatment_plan

    #"frequencyOfTargetLocalization": "Weekly",
    #"targetLocalizationMethod": "Cone Beam CT",
    #"radiotherapyTechnique": "IMRT",

    #"organsAtRisk": ["Rectum", "Bladder", "Femurs"],
    #"bracytherapyBoostPlanned": "No",
    #"hormones": "No",


    ##### OTV ###
    otvs = []

    for otv in json_data['otv']:
        current_otv = {}
        try:
            current_otv['dateSigned'] = otv['otvAssessmentDate']
        except KeyError:
            pass
        current_otv['toxicity'] = []
        for toxicity in otv['toxicity']:
            current_toxicity = {}
            try:
                current_toxicity['system'] = toxicity['system']
            except KeyError:
                pass
            try:
                current_toxicity['grade'] = toxicity['grade']
            except KeyError:
                pass
            try:
                current_toxicity['toxicity'] = toxicity['toxicity']
            except KeyError:
                pass
            try:
                current_otv['toxicity'].append(current_toxicity)
            except KeyError:
                pass

        otvs.append(current_otv)

    updated_data['otv'] = otvs



    ##### Treatment Summary ###
    treatmentSummary = {}
    # "treatmentSummary - derive this value
    treatmentSummary['wasTreatmentCompleted'] = 'Yes'
    treatmentSummary['treatmentIntent'] = 'Definitive'

    updated_data['treatmentSummary'] = [treatmentSummary]

    
    ##### Follow Up ###
    followups = []
    try:
        for followup in json_data['followUp']:
            current_followup = {}
            try:
                current_followup['wasTreatmentCompleted'] = 'Yes'
            except KeyError:
                pass
            try:
                current_followup['dateOfNote'] = followup['followUpDate']
            except KeyError:
                pass
            try:
                current_followup['diseaseProgression'] = followup['patientProgression']
            except KeyError:
                pass

            # FIXME - listed as mutliple items for follow ups
            current_followup['qualityOfLife'] = []
            try:
                for qualityOfLife in followup['qualityOfLifeScore']:
                    currentQualityOfLife = {}

                    try:
                        currentQualityOfLife['assessment'] = qualityOfLife['assessment']
                    except KeyError:
                        pass
                    try:
                        currentQualityOfLife['numericScore'] = int(qualityOfLife['numericScore'])
                    except KeyError:
                        pass

                    current_followup['qualityOfLife'].append(currentQualityOfLife)

                current_followup['toxicity'] = []
                for toxicity in followup['toxicity']:
                    current_toxicity = {}
                    try:
                        current_toxicity['system'] = toxicity['system']
                    except KeyError:
                        pass
                    try:
                        current_toxicity['grade'] = toxicity['grade']
                    except KeyError:
                        pass
                    try:
                        current_toxicity['toxicity'] = toxicity['toxicity']
                    except KeyError:
                        pass
                    try:
                        current_followup['toxicity'].append(current_toxicity)
                    except KeyError:
                        pass
            except KeyError:
                pass

            followups.append(current_followup)
    except KeyError:
        pass

    updated_data['followup'] = followups
    '''
    return updated_data


def process_problem_list(problem_list):
    result = []
    for problem in problem_list:
        current_problem = {}
        description = problem['Description'].split('(')
        for item in description:
            item = item.strip('() ')
            if item[:3] == 'SCT':
                current_problem['SCT'] = item
            elif item[:3] == 'ICD':
                current_problem['ICD'] = item
            else:
                current_problem['description'] = item

        result.append(current_problem)
    return result


def main():
    global json_data
    global cprs_data
    #data_lines = None

    if len(sys.argv) != 3:
        print('Usage: washu_ropa_import.py [ROPA csv file] [CPRS json file]')
        return -1

    csv_path = sys.argv[1]
    data_file = open(csv_path)

    with open(sys.argv[2]) as f:
        cprs_data = json.load(f)

    patient_data = []
    patient_map = {}
    data_file.readline()  # skip header

    # parse csv file
    for line in data_file.readlines():
        line = line.strip().replace('"', '').split(',')
        if (line[10] == 'multi-select-field' or line[9] == '--Select Motion Management--') and line[11] != 'NA':
            updated_line = []
            for i in range(0, 11):
                updated_line.append(line[i])
            multi_value = []
            for i in range(11, len(line) - 3):
                multi_value.append(line[i])
            updated_line.append(multi_value)
            for i in range(len(line) - 3, len(line)):
                updated_line.append(line[i])
            line = updated_line

        if line[3] == 'Complete':
            if line[1] not in patient_map:
                #print(line[1])
                patient_map[line[1]] = []
            patient_map[line[1]].append(line)

    master_list = []
    # create json object per patient from csv data

    for patient in patient_map:
        #if patient != '671-Prostate-10':
        #    continue
        #print(patient)
        json_data = {}
        data_lines = {}
        disease_site = None
        surgery = None

        # prep data array before json creation
        for line in patient_map[patient]:
            if is_int(line[0]):
                json_data['caseId'] = line[1]
                if line[4] == 'Prostate' or line[4] == 'Prostate Surgery':
                    # disease_site = 'prostate'
                    disease_site = 'Prostate'
                    if line[4] == 'Prostate Surgery':
                        surgery = "Yes"
                    else:
                        surgery = "No"
                elif line[4] == 'NSCLC' or line[4] == 'NSCLC Surgery':
                    # disease_site = 'nsclc'
                    disease_site = 'NSCLC'
                    if line[4] == 'NSCLC Surgery':
                        surgery = "Yes"
                    else:
                        surgery = "No"
                elif line[4] == 'SCLC':
                    # disease_site = 'sclc'
                    disease_site = 'SCLC'
            if line[6] not in data_lines:
                data_lines[line[6]] = []
            if line[-4] != 'NA' and line[-4] != 'NULL' and len(line[-4]) != 0 and line[-4] != '- - -':
                if line[-4] != ["NULL"] and line[-4] != "\"\"" and line[-4] != ['']:
                    #print(line[-4])
                    try:
                        date_values = line[-4].split(' ')
                        if len(date_values) == 3:
                            if '-' in date_values:
                                continue
                    except:
                        pass
                    if line[11] == 'Not stated':
                        line[11] = 'Not Stated'
                    if line[3] != 'Pending':
                        data_lines[line[6]].append(line)

        #if patient != '528-NSCLC-01':#'528-SCLC-01':#''506-NSCLC-01':
        #    continue
        # parse data sections
        if 'Clinical Validation' in data_lines:
            process_clinical_validation(data_lines['Clinical Validation'], disease_site, surgery)

        if 'Consult' in data_lines:
            process_consult(data_lines['Consult'], disease_site)

        if 'OTV' in data_lines:
            process_otv(data_lines['OTV'], disease_site)

        #FIXME
        if 'Survivorship' in data_lines:
            process_survivorship(data_lines['Survivorship'], disease_site)
        elif 'Survivorship/PCI' in data_lines:
            process_survivorship(data_lines['Survivorship/PCI'], disease_site)

        if 'Follow-Up' in data_lines:
            process_follow_up(data_lines['Follow-Up'], disease_site)
        if 'Technical Validation' in data_lines:
            process_technical_validation(data_lines['Technical Validation'], disease_site)

        # FIXME - remove this when all data is available
        try:
            #print(json_data)le
            if 'patientInformation' in json_data: #'icdCode' in json_data['patientInformation']:
                #pprint(json_data)
                updated_data = reformat_data(json_data)
                master_list.append(updated_data)

                #db_put(json_data)
                #break
        except KeyError as e:
            #pprint(json_data['patientInformation']['icdCode'])
            print("KeyError: ", e)
            pass
        except AssertionError as e:
            print(e)
            exit(0)


    pprint(json_data)
    print('count: ' + str(len(master_list)))
    with open('data.json', 'w') as outfile:
        json.dump(master_list, outfile)


if __name__ == '__main__':
    main()
