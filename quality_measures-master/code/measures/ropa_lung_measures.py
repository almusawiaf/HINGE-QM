from pymongo import MongoClient
from datetime import datetime, timedelta
from collections import OrderedDict

from .measure import Measure
from .measure import logging

class LungMeasure(Measure):


	def __init__(self):
			#print("Lung Quality Measures")
			pass

	measures = OrderedDict({
		'center_id' : None,
		'center_name' : None,
		'vha_id' : None,
		"cancer_type" : None,
		'QualityMeasure1' : None,
		'QualityMeasure2' : None,
		'QualityMeasure3' : None,
		'QualityMeasure4' : None,
		'QualityMeasure5' : None,
		'QualityMeasure6' : None,
		'QualityMeasure7' : None,
		'QualityMeasure8A' : None,
		'QualityMeasure8B' : None,
		'QualityMeasure9' : None,
		'QualityMeasure10' : None,
		'QualityMeasure11' : None,
		'QualityMeasure12' : None,
		'QualityMeasure13' : None,
		'QualityMeasure14' : None,
		'QualityMeasure15' : None,
		'QualityMeasure16' : None,
		'QualityMeasure17' : None,
		'QualityMeasure18' : None,
		'QualityMeasure19' : None,
		'QualityMeasure19_color' : None,
		'QualityMeasure20' : None,
		'QualityMeasure21A' : None,
		'QualityMeasure21B' : None,
		'QualityMeasure22' : None,
		'QualityMeasure23' : None,
		'QualityMeasure24' : None,
		'TotalNumberOfNotes' : None,
		'NumberOfNotesWithToxicityInitialized' : None,
		'LungEsophagitisTotal' : None,
		'LungEsophagitisWithGrade' : None,
		'LungPneumonitisTotal': None,
		'LungPneumonitisWithGrade' : None,
		'QualityMeasure27' : None
	})

	def GetTreatmentDate(self):

		patient = self.patient

		end_times = []

		try:
			if 'multidisciplinaryConsultDate' in patient['consult'][0]:
				consult_date = Measure.str_to_date(self, patient['consult'][0]['multidisciplinaryConsultDate'])
				end_times.append(consult_date)
				#print('consult', consult_date)
		except:
			logging.info('No consult')

		try:
			if 'chemotherapyEndDate' in patient['chemotherapy'][0]:
				chemo_end_date = Measure.str_to_date(self, patient['chemotherapy'][0]['chemotherapyEndDate'])
				end_times.append(chemo_end_date)
				#print('chemo', chemo_end_date)
		except:
			logging.info('No chemo')

		try:
			rt_end_dates = []
			for plan in patient['treatmentSummary'][0]['ebrt']:
				rt_end_dates.append(Measure.str_to_date(self, plan['endDate']))

			rt_end_date = sorted(rt_end_dates)[-1]

			end_times.append(rt_end_date)
				#print('ebrt', rt_end_date)
		except:
			logging.info('No ebrt')

		try:
			if patient['diagnosis']['previousSurgery'].lower() == 'yes':
				surgery_date = Measure.str_to_date(self, patient['diagnosis']['surgeryDate'])
				end_times.append(surgery_date)
		except:
			logging.info('No surgery')

		try:
			tmt_end_date = sorted(end_times)[-1]
		except:
			print('Error')

		return tmt_end_date


	def QualityMeasure1(self):
		#Unable to locate 'MRI Mention Date', 'CT Mention Date', 'PET-CT Mention Date'

		patient = self.patient

		current_date = datetime(2100, 1, 1).date()

		
		try:
			rt_start_dates = []

			for plan in patient['treatmentSummary'][0]['ebrt']:
				rt_start_dates.append(Measure.str_to_date(self, plan['startDate']))

			rt_start_date = sorted(rt_start_dates)[0]
		except:
			rt_start_date = current_date

		try:
			if 'diagnosticImaging' in patient:
				mri_report_date = Measure.str_to_date(self, patient['diagnosticImaging']['mriDate'])
		except:
			mri_report_date = current_date

		try:
			if 'diagnosticImaging' in patient:
				ct_report_date = Measure.str_to_date(self, patient['diagnosticImaging']['ctDate'])
		except:
			ct_report_date = current_date

		try:
			if 'diagnosticImaging' in patient:
				petct_date = Measure.str_to_date(self, patient['diagnosticImaging']['petctDate'])
		except:
			petct_date = current_date

		try:
			is_mri = True if patient['diagnosticImaging']['mri'].lower() == 'yes' else False

		except:
			is_mri = False

		try:
			is_ct = True if patient['diagnosticImaging']['ct'].lower() == 'yes' else False
		except:
			is_ct = False

		try:
			is_petct = True if patient['diagnosticImaging']['petct'].lower() == 'yes' else False
		except:
			is_petct = False


		logging.info([str(item) for item in [rt_start_date, petct_date, mri_report_date, ct_report_date]])

		if (petct_date < rt_start_date) and (mri_report_date >= rt_start_date) and (ct_report_date >= rt_start_date):
			result = 'Fail'
		else:
			result = 'Pass'

		result = [patient['caseId'], result, [{
					'name': 'PET-CT Report Date < RT Start Date',
					'parent': 'null',
					'children': [{
						'name': 'PET-CT Mention Date < RT Start Date',
						'parent': 'PET-CT Report Date < RT Start Date',
						'level': 'green' if petct_date >= rt_start_date else 'null',
						'condition': 'No',
						'children': [{
							'name': 'Fail',
							'parent': 'PET-CT Mention Date < RT Start Date',
							'level': 'null',
							'condition': 'No',
							'result': 'No',
							},
							{
							'name': 'MRI Report Date < RT Start Date',
							'parent': 'PET-CT Mention Date < RT Start Date',
							'level': 'null',
							'condition': 'Yes',
							}]
						},
						{
						'name': 'MRI Report Date < RT Start Date',
						'parent': 'PET-CT Report Date < RT Start Date',
						'level': 'green' if petct_date < rt_start_date else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Pass',
							'parent': 'MRI Report Date < RT Start Date',
							'level': 'green' if result == 'Pass' and mri_report_date < rt_start_date else 'null',
							'condition': 'Yes',
							'result': 'green' if result == 'Pass' and mri_report_date < rt_start_date else 'null',
							},
							{
							'name': 'MRI Mention Date < RT Start Date',
							'parent': 'MRI Report Date < RT Start Date',
							'level': 'green' if mri_report_date >= rt_start_date else 'null', 
							'condition': 'No',
							'children': [{
								'name': 'Pass',
								'parent': 'MRI Mention Date < RT Start Date',
								'level': 'null',
								'condition': 'Yes',
								'result': 'null'
								},
								{
								'name': 'CT Report Date < RT Start Date',
								'parent': 'MRI Mention Date < RT Start Date',
								'level': 'green' if mri_report_date >= rt_start_date else 'null',
								'condition': 'No',
								'children': [{
									'name': 'Pass',
									'parent': 'CT Report Date < RT Start Date',
									'level': 'green' if mri_report_date >= rt_start_date and ct_report_date < rt_start_date else 'null',
									'condition': 'Yes',
									'result': 'green' if mri_report_date >= rt_start_date and ct_report_date < rt_start_date else 'null',
									},
									{
									'name': 'CT Mention Date < RT Start Date',
									'parent': 'CT Report Date < RT Start Date',
									'level': 'green' if mri_report_date >= rt_start_date and ct_report_date >= rt_start_date else 'null',
									'condition': 'No',
									'children': [{
										'name': 'Fail',
										'parent': 'CT Mention Date < RT Start Date',
										'level': 'green' if result == 'Fail' else 'null',
										'condition': 'No',
										'result': 'red' if result == 'Fail' else 'null', 
										},
										{
										'name': 'Pass',
										'parent': 'CT Mention Date < RT Start Date',
										'level': 'null',
										'condition': 'Yes',
										'result': 'null', 
										}]
									}]
								}]
							}]
						}]
		}]]
		
		return result

	def QualityMeasure2(self):
		patient = self.patient

		valid_source = ['consult', 'addendum']
		valid_reason = ['comorbidities/frailty']
		current_date = datetime(2100, 1, 1).date()


		try:
			path_report = True if patient['pathology']['isPathologyReport'].lower() == 'yes' else False
		except:
			path_report = False

		try:
			if 'pathology' in patient:
				path_report_date = Measure.str_to_date(self, patient['pathology']['pathologyReportDate'])
		except:
			path_report_date = current_date

		try:
			if 'consult' in patient:
				consult_date = Measure.str_to_date(self, patient['consult'][0]['multidisciplinaryConsultDate'])
		except:
			consult_date = current_date

		try:
			if 'pathology' in patient:
				no_path_reason = patient['pathology']['reasonForNoPathologyReport'].lower()
		except:
			no_path_reason = None

		try:
			#path_source = True if patient['pathology']['pathologySource'].lower() in valid_source else False
			path_source = True if patient['consult'] else False
		except:
			path_source = False


		logging.info([str(item) for item in [path_report, path_report_date, consult_date, no_path_reason, path_source]])

		if not path_report and (no_path_reason not in valid_reason) and not path_source or \
		   path_report and path_report_date > consult_date and (not path_source):
		   	result = 'Fail'
		elif path_report and no_path_reason in valid_reason:
			result = 'Excluded'
		else:
			result = 'Pass'

		result = [patient['caseId'], result, [{
			'name': 'Is there a pathology report?',
			'parent': 'null',
			'children': [{
				'name': 'Pathology Report Date <= Consult Date',
				'parent': 'Is there a pathology report?',
				'level': 'green' if path_report else 'null',
				'condition': 'Yes',
				'children': [{
					'name': 'Pass',
					'parent': 'Pathology Report Date <= Consult Date',
					'level': 'green' if path_report and path_report_date <= consult_date else 'null',
					'condition': 'Yes', 
					'result': 'green' if path_report and path_report_date <= consult_date else 'null',
					},
					{
					'name': '"Consult" or "Addendum" selected for Pathology',
					'parent': 'Pathology Report Date <= Consult Date',
					'level': 'green' if path_report and path_report_date > consult_date else 'null',
					'condition': 'No',
					'children': [{
						'name': 'Pass',
						'parent': '"Consult" or "Addendum" selected for Pathology',
						'level': 'green' if result == 'Pass' and not path_report or result == 'Pass' and path_report_date > consult_date else 'null',
						'condition': 'Yes',
						'result': 'green' if result == 'Pass' and not path_report or result == 'Pass' and path_report_date > consult_date else 'null',
						},
						{
						'name': 'Fail',
						'parent': '"Consult" or "Addendum" selected for Pathology',
						'level': 'green' if result == 'Fail' else 'null',
						'condition': 'No',
						'result': 'red' if result == 'Fail' else 'null'
						}
						]
					}]
				},
				{
				'name': '“Comorbidities/Frailty” selected for No Pathology Report Reason',
				'parent': 'Is there a pathology report?',
				'level': 'green' if not path_report else 'null',
				'condition': 'No',
				'children': [{
					'name': '“Consult” or “Addendum” selected for Pathology',
					'parent': '“Comorbidities/Frailty” selected for No Pathology Report Reason',
					'level': 'green' if not path_report and result != 'Excluded' else 'null',
					'condition': 'No', 
					},
					{
					'name': 'Excluded',
					'parent': '“Comorbidities/Frailty” selected for No Pathology Report Reason',
					'level': 'green' if result == 'Excluded' else 'null',
					'condition': 'Yes',
					'result': 'blue' if result == 'Excluded' else 'null',
					}]
				}]
		}]]
		return result

	def QualityMeasure3(self):
		patient = self.patient

		valid_reason = ['comorbidities/frailty']
		valid_source = ['consult', 'addendum']
		current_date = datetime(2100, 1, 1).date()

		try:
			if 'diagnosis' in patient:
				no_class_reason = patient['diagnosis']['nsclcClassificationType'].lower()
		except:
			no_class_reason = None

		try:
			#class_source = patient['diagnosis']['nsclcClassificationSource'].lower()
			class_source = 'consult' if patient['consult'] else None
		except:
			class_source = None

		try:
			if 'diagnosis' in patient:
				class_source_date = Measure.str_to_date(self, patient['diagnosis']['nsclcClassificationDate'])
		except:
			class_source_date = current_date

		try:
			if 'consult' in patient:
				consult_date = Measure.str_to_date(self, patient['consult'][0]['multidisciplinaryConsultDate'])
		except:
			consult_date = current_date 

		logging.info([str(item)for item in [no_class_reason, class_source, class_source_date, consult_date, patient['caseId']]])

		try:
			is_sclc = True if '-SCLC' in patient['caseId'] else False
		except:
			is_sclc = False


		if is_sclc:
			result = "Excluded"
		elif no_class_reason in valid_reason:
			result = 'Excluded'
		elif (no_class_reason not in valid_reason) and (class_source in valid_source) or \
			 (no_class_reason not in valid_reason) and (class_source not in valid_source) and \
			 class_source == 'other' and (class_source_date <= consult_date):
			 result = 'Pass'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [
			{
				'name': 'Is SCLC?',
				'parent': 'null', 
				'children': [
				{
					'name': 'Excluded', 
					'parent': 'Is SCLC', 
					'condition': 'Yes', 
					'level': 'green' if is_sclc else 'null', 
					'result': 'green' if is_sclc else 'null'
				},
				{
					'name': '"Comorbidities/ Frailty" selected for NSCLC Classification Type',
					'parent': 'Is SCLC?',
					'condition': 'No', 
					'level': 'green' if not is_sclc else 'null', 
					'children': [{
						'name': 'Excluded',
						'parent': '"Comorbidities/ Frailty" selected for NSCLC Classification Type',
						'condition': 'Yes', 
						'level': 'green' if no_class_reason in valid_reason and not is_sclc else 'null',
						'result': 'blue' if no_class_reason in valid_reason and not is_sclc else 'null',
						},
						{
						'name': '"Consult" or "Addendum" selected for NSCLC Classification',
						'parent': '"Comorbidities/ Frailty" selected for NSCLC Classification Type',
						'condition': 'No', 
						'level': 'green' if no_class_reason not in valid_reason and not is_sclc else 'null',
						'children': [{
							'name': 'Pass',
							'parent': '"Consult" or "Addendum" selected for NSCLC Classification',
							'level': 'green' if class_source in valid_source and no_class_reason not in valid_reason and not is_sclc else 'null',
							'condition': 'Yes', 
							'result': 'green' if class_source in valid_source and no_class_reason not in valid_reason and not is_sclc else 'null',
							},
							{
							'name': '"Other" selected for NSCLC Classification',
							'parent': '"Consult" or "Addendum" selected for NSCLC Classification',
							'level': 'green' if class_source not in valid_source and no_class_reason not in valid_reason and not is_sclc else 'null',
							'condition': 'No', 
							'children': [{
								'name': 'Fail',
								'parent': '"Other" selected for NSCLC Classification',
								'level': 'green' if class_source not in valid_source and class_source != 'other' and no_class_reason not in valid_reason and not is_sclc else 'null',
								'condition': 'No', 
								'level': 'red' if class_source not in valid_source and class_source != 'other' and no_class_reason not in valid_reason and not is_sclc else 'null',
								},
								{
								'name': '"Other" date <= Consult date',
								'parent': '"Other" selected for NSCLC Classification',
								'level': 'green' if class_source not in valid_source and class_source == 'other' and no_class_reason not in valid_reason and not is_sclc else 'null',
								'condition': 'Yes', 
								'children': [{
									'name': 'Pass',
									'parent': '"Other" date <= Consult date',
									'level': 'green' if class_source not in valid_source and class_source == 'other' and \
												no_class_reason not in valid_reason and class_source_date <= consult_date and not is_sclc else 'null',
									'condition': 'Yes', 
									'result': 'green' if class_source not in valid_source and class_source == 'other' and \
												no_class_reason not in valid_reason and class_source_date <= consult_date and not is_sclc else 'null',
									},
									{
									'name': 'Fail',
									'parent': '"Other" date <= Consult date',
									'level': 'green' if class_source not in valid_source and class_source == 'other' and \
												no_class_reason not in valid_reason and class_source_date > consult_date and not is_sclc else 'null',
									'condition': 'No', 
									'result': 'green' if class_source not in valid_source and class_source == 'other' and \
												no_class_reason not in valid_reason and class_source_date > consult_date and not is_sclc else 'null',
									}
									]
								}
								]
							}
							]
						}
					]
				}]
			}
		]
		]
		return result

	def QualityMeasure4(self):
		#For the second decision, "Yes" is selected for Molecular Info Report Type, "Yes" is not an option for molecularInformationReportType, currently using isMolecularInformationReport
		patient = self.patient

		valid_reason = ['comorbidities/frailty']
		current_date = datetime(2100, 1, 1).date()

		try:
			#molc_info_source = patient['molecular']['molecularInformationSource'].lower()
			molc_info_source = True if patient['consult'] else False
			#Most sources are not stated, should this be true
		except:
			molc_info_source = False

		try:
			molecular_info_date = Measure.str_to_date(self, patient['molecular']['molecularInformationDate'])
		except:
			molecular_info_date = current_date

		try:
			molecular_info_report_date = Measure.str_to_date(self, patient['molecular']['molecularInformationReportDate'])
		except:
			molecular_info_report_date = current_date

		try:
			molecular_info_type = patient['molecular']['molecularInformationType'].lower()
		except:
			molecular_info_type = None

		try:
			is_molc_report = True if patient['molecular']['isMolecularInformationReport'].lower() == 'yes' else False
		except:
			is_molc_report = None

		try:
			molc_info_report_type = patient['molecular']['molecularInformationReportType'].lower()
		except:
			molc_info_report_type = None

		try:
			no_molc_reason = patient['molecular']['reasonForNoMolecularReport'].lower()
		except:
			no_molc_reason = None

		try:
			rt_start_dates = []

			for plan in patient['treatmentSummary'][0]['ebrt']:
				rt_start_dates.append(Measure.str_to_date(self, plan['startDate']))

			rt_start_date = sorted(rt_start_dates)[0]

		except:
			rt_start_date = current_date


		if '-SCLC' in patient['caseId']:
			result = ""

		elif (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and not is_molc_report and no_molc_reason in valid_reason:
			result = 'Excluded'

		elif (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and is_molc_report and molc_info_report_type != 'not stated' and molecular_info_report_date <= rt_start_date or \
			not molc_info_source and molecular_info_type != 'not stated' and molecular_info_date <= rt_start_date:
			result = 'Pass'

		else:
			result = 'Fail'

		
		result = [patient['caseId'], result, [{
					'name': '"Not stated" selected for Molecular Information',
					'parent': 'null',
					'children': [{
						'name': '"Yes" is selected for "Is there a Molecular Report?"',
						'parent': '"Not stated" selected for Molecular Information',
						'level': 'green' if molc_info_source else 'null',
						'condition': 'Yes',
						'children': [{
							'name': '"Comorbidities/ Frailty" selected for No Molecular Information Report Reason',
							'parent': '"Yes" is selected for "Is there a Molecular Report?"',
							'level': 'green' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and not is_molc_report else 'null', 
							'condition': 'No',
							'children': [{
								'name': 'Excluded',
								'parent': '"Comorbidities/ Frailty" selected for No Molecular Information Report Reason',
								'level': 'green' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and not is_molc_report and no_molc_reason in valid_reason else 'null',
								'condition': 'Yes',
								'result': 'green' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and not is_molc_report and no_molc_reason in valid_reason else 'null',
								},
								{
								'name': 'Fail',
								'parent': '"Comorbidities/ Frailty" selected for No Molecular Information Report Reason',
								'level': 'green' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and not is_molc_report and no_molc_reason not in valid_reason else 'null',
								'condition': 'No',
								'result': 'red' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and not is_molc_report and no_molc_reason not in valid_reason else 'null',
								}]
							},
							{
							'name': '"Not Stated" is selected for Molecular Information \n Report Type',
							'parent': '"Yes" is selected for "Is there a Molecular Report?"',
							'level': 'green' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and is_molc_report else 'null',
							'condition': 'Yes',
							'children': [{
								'name': 'Fail',
								'parent':  '"Not Stated" is selected for Molecular Information Report Type',
								'level': 'green' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and is_molc_report and molc_info_report_type == 'not stated' else 'null',
								'condition': 'Yes',
								'result': 'red' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and is_molc_report and molc_info_report_type == 'not stated' else 'null',
								},
								{
								'name': 'Molecular Information \n Report date <= RT Start Date',
								'parent':  '"Not Stated" is selected for Molecular Information Report Type',
								'level': 'green' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and is_molc_report and molc_info_report_type != 'not stated' else 'null',
								'condition': 'No',
								'children': [{
									'name': 'Pass',
									'parent': 'Molecular Information Report date <= RT Start Date',
									'level': 'green' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and is_molc_report and molc_info_report_type != 'not stated' \
													and molecular_info_report_date <= rt_start_date else 'null',
									'condition': 'Yes',
									'result': 'green' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and is_molc_report and molc_info_report_type != 'not stated' \
													and molecular_info_report_date <= rt_start_date else 'null',
									},
									{
									'name': 'Fail',
									'parent': 'Molecular Information Report date <= RT Start Date',
									'level': 'green' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and is_molc_report and molc_info_report_type != 'not stated' \
													and molecular_info_report_date > rt_start_date else 'null',
									'condition': 'No',
									'result': 'red' if (molc_info_source or not molc_info_source and molecular_info_type =='not stated') and is_molc_report and molc_info_report_type != 'not stated' \
													and molecular_info_report_date > rt_start_date else 'null',
									}]
								}]
							}]
						},
						{
						'name': '"Not Stated" is selected for Molecular Information Type',
						'parent': '"Not stated" selected for Molecular Information',
						'level': 'green' if not molc_info_source else 'null',
						'condition': 'No', 
						'children': [
							{
							'name': '"Yes" is selected for Molecular Information Report Type', 
							},
							{
							'name': 'Molecular Information date <= RT Start Date',
							'parent': '"Not Stated" is selected for Molecular Information Type',
							'level': 'green' if not molc_info_source and molecular_info_type != 'not stated' else 'null', 
							'condition': 'No',
							'children': [{
								'name': 'Pass',
								'parent': 'Molecular Information date <= RT Start Date',
								'level': 'green' if not molc_info_source and molecular_info_type != 'not stated' and molecular_info_date <= rt_start_date else 'null', 
								'condition': 'Yes',
								'result': 'green' if not molc_info_source and molecular_info_type != 'not stated' and molecular_info_date <= rt_start_date else 'null',
								},
								{
								'name': 'Fail',
								'parent': 'Molecular Information date <= RT Start Date',
								'level': 'green' if not molc_info_source and molecular_info_type != 'not stated' and molecular_info_date > rt_start_date else 'null',
								'condition': 'No',
								'result': 'red' if not molc_info_source and molecular_info_type != 'not stated' and molecular_info_date > rt_start_date else 'null',
								}]
							}]
						}
						]
			}]]
		return result


	def QualityMeasure5(self):
		patient = self.patient
		
		valid_source = ['consult', 'addendum']
		current_date = datetime(2100, 1, 1).date()

		try:
			#staging_sys_source = patient['diagnosis']['clinicalStageSource'].lower()
			staging_sys_source = 'consult' if patient['consult'] else None
		except:
			staging_sys_source = None

		try:
			if 'diagnosis' in patient:
				staging_sys_date = Measure.str_to_date(self, patient['diagnosis']['tnmTumorStageDate'])
		except:
			staging_sys_date = current_date

		try:
			if 'consult' in patient:
				consult_date = Measure.str_to_date(self, patient['consult'][0]['multidisciplinaryConsultDate'])
		except:
			consult_date = current_date

		logging.info([str(item) for item in [staging_sys_source, staging_sys_date, consult_date, patient['caseId']]])

		if (staging_sys_source in valid_source) or \
			(staging_sys_source not in valid_source) and staging_sys_source == 'other' and staging_sys_date <= consult_date:
			result = 'Pass'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
				'name': '"Consult" or "Addendum" selected for Staging System/ Stage',
				'parent': 'null',
				'children': [{
					'name': 'Pass',
					'parent': '"Consult" or "Addendum" selected for Staging System/ Stage',
					'level': 'green' if staging_sys_source in valid_source else 'null',
					'condition': 'Yes', 
					'result': 'green' if staging_sys_source in valid_source else 'null',
					},
					{
					'name': '"Other" selected for Staging System/ Stage',
					'parent': '"Consult" or "Addendum" selected for Staging System/ Stage',
					'level': 'green' if staging_sys_source == 'other' else 'null',
					'condition': 'No', 
					'children': [{
						'name': 'Fail',
						'parent': '"Other" selected for Staging System/ Stage',
						'level': 'green' if staging_sys_source not in valid_source else 'null',
						'condition': 'No', 
						'result': 'red' if staging_sys_source not in valid_source else 'null'
						},
						{
						'name': '"Other" date <= Consult date',
						'parent': '"Other" selected for Staging System/ Stage',
						'level': 'green' if staging_sys_source == 'other' else 'null', 
						'condition': 'Yes', 
						'children': [{
							'name': 'Fail',
							'parent': '"Other" date <= Consult date',
							'level': 'green' if staging_sys_source == 'other' and staging_sys_date > consult_date else 'null',
							'condition': 'No', 
							'result': 'red' if staging_sys_source == 'other' and staging_sys_date > consult_date else 'null',
							},
							{
							'name': 'Pass',
							'parent': '"Other" date <= Consult date',
							'level': 'green' if staging_sys_source == 'other' and staging_sys_date <= consult_date else 'null',
							'condition': 'Yes', 
							'result': 'green' if staging_sys_source == 'other' and staging_sys_date <= consult_date else 'null',
							}
						]
						}
					]
					}
				]
				}]
		]
		return result

	def QualityMeasure6(self):
		patient = self.patient
		
		current_date = datetime(2100, 1, 1).date()

		try:
			#multi_disc_consult = patient['consult'][0]['multidisciplinaryConsultType'].lower()
			multi_disc_consult = 'consult' if patient['consult'] else None
		except:
			multi_disc_consult = None

		try:
			multi_disc_consult_date = Measure.str_to_date(self, patient['consult'][0]['multidisciplinaryConsultDate'])

			rt_start_dates = []

			for plan in patient['treatmentSummary'][0]['ebrt']:
				rt_start_dates.append(Measure.str_to_date(self, plan['startDate']))

			rt_start_date = sorted(rt_start_dates)[0]
		except:
			multi_disc_consult_date = current_date
			rt_start_date = current_date

		if multi_disc_consult == 'not found' or multi_disc_consult != 'not found' and multi_disc_consult_date >= rt_start_date:
			result = 'Fail'
		else:
			result = 'Pass'

		result = [patient['caseId'], result, 
					[{'name': '"Not Found" selected for Multidisciplinary Consult',
					'parent': 'null',
					'children': [{
						'name': 'Fail',
						'parent': '"Not Found" selected for Multidisciplinary Consult',
						'level': 'green' if multi_disc_consult == 'not found' else 'null',
						'condition': 'Yes', 
						'result': 'red' if multi_disc_consult == 'not found' else 'null',
								},
						{
						'name': 'Multidisciplinary Consult Date < RT start date',
						'parent': '"Not Found" selected for Multidisciplinary Consult',
						'level': 'green' if multi_disc_consult != 'not found' else 'null',
						'condition': 'No', 
						'children': [{
							'name': 'Pass',
							'parent': 'Multidisciplinary Consult Date < RT start date',
							'level': 'green' if multi_disc_consult != 'not found' and multi_disc_consult_date < rt_start_date else 'null',
							'condition': 'Yes', 
							'result': 'green' if multi_disc_consult != 'not found' and multi_disc_consult_date < rt_start_date else 'null',
									},
							{
							'name': 'Fail',
							'parent': 'Multidisciplinary Consult Date < RT start date',
							'level': 'green' if multi_disc_consult != 'not found' and multi_disc_consult_date >= rt_start_date else 'null',
							'condition': 'No', 
							'result': 'red' if multi_disc_consult != 'not found' and multi_disc_consult_date >= rt_start_date else 'null',
									}]
								}]
					}]
				]

		return result
		
	def QualityMeasure7(self):
		patient = self.patient

		valid_source = ['consult', 'addendum']

		try:
			performance_status = 'consult' if patient['consult'][0]['performanceStatus'] else None
		except:
			performance_status = None

		if performance_status in valid_source:
			result = 'Pass'
		else:
			result = 'Fail'

		result =  [patient['caseId'], result, [{'name': '"Consult or "Addendum" selected for Performance Status',
												'parent': 'null',
												'children': [{
												'name': 'Pass',
												'parent': 'Consult or "Addendum" selected for Perfomrance Status',
												'level': 'green' if (performance_status in valid_source) else 'null',
												'condition': 'Yes',
												'result': 'green' if result == 'Pass' else 'null',
												},
												{
												'name': 'Fail',
												'parent': 'Consult or "Addendum" selected for Perfomrance Status',
												'level': 'null' if (performance_status in valid_source) else 'green',
												'condition': 'No', 
												'result': 'red' if result == 'Fail' else 'null'
												}]}]]

		return result

	def QualityMeasure8A(self):
		patient = self.patient
		
		valid_source = ['consult', 'addendum']


		try:
			#smoke_status = patient['consult'][0]['smokingStatusSource'].lower()
			smoke_status = 'consult' if patient['consult'] else None
		except:
			smoke_status = None


		if smoke_status in valid_source:
			result = 'Pass'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
					'name': '"Consult" or "Addendum" selected for Smoking Status', 
					'parent': 'null',
					'children': [{
						'name': 'Pass',
						'parent': '"Consult" or "Addendum" selected for Smoking Status', 
						'level': 'green' if smoke_status in valid_source else 'null',
						'condition': 'Yes', 
						'result': 'green' if smoke_status in valid_source else 'null',
						},
						{
						'name': 'Fail',
						'parent': '"Consult" or "Addendum" selected for Smoking Status', 
						'level': 'green' if smoke_status not in valid_source else 'null',
						'condition': 'No', 
						'result': 'green' if smoke_status not in valid_source else 'null',
						}
					]
			}]

		]
		return result
		
	def QualityMeasure8B(self):
		patient = self.patient

		try:
			smoking_status = patient['consult'][0]['currentSmokingStatus']
		except:
			smoking_status = None

		try:
			smoke_cess = patient['consult'][0]['smokingCessationPlan'].lower()
		except:
			smoke_cess = None


		if smoking_status == 'Former Smoker' or (not smoking_status and not smoke_cess) or smoking_status == 'Never Smoker':
			result = 'Excluded'
		elif smoke_cess == 'not stated' and not (smoking_status == 'Former Smoker'):
			result = 'Fail'
		else:
			result = 'Pass'

		result = [patient['caseId'], result, [{
				'name': '"Not Stated" is NOT selected QM 8A: Smoking Status and "Smoker" selected for QM 8A: Current Smoking Status',
				'parent': 'null',
				'children': [{
					'name': 'Excluded',
					'parent': '"Not Stated" is NOT selected QM 8A: Smoking Status and "Smoker" selected for QM 8A: Current Smoking Status',
					'level': 'green' if smoking_status == 'Former Smoker' or (not smoking_status and not smoke_cess) or smoking_status == 'Never Smoker' else 'null',
					'condition': 'No', 
					'result': 'blue' if smoking_status == 'Former Smoker' or (not smoking_status and not smoke_cess) or smoking_status == 'Never Smoker' else 'null', 
					},
					{
					'name': '"Not Stated" selected for Smoking Cessation',
					'parent': '"Not Stated" is NOT selected QM 8A: Smoking Status and "Smoker" selected for QM 8A: Current Smoking Status',
					'level': 'green' if result != 'Excluded' else 'null',
					'condition': 'Yes', 
					'children': [{
						'name': 'Fail',
						'parent': '"Not Stated" selected for Smoking Cessation',
						'level': 'green' if smoking_status != 'Former Smoker' and smoke_cess == 'not stated' and result != 'Excluded' else 'null',
						'condition': 'Yes', 
						'result': 'red' if smoking_status != 'Former Smoker' and smoke_cess == 'not stated' and result != 'Excluded' else 'null',
						},
						{
						'name': 'Pass',
						'parent': '"Not Stated" selected for Smoking Cessation',
						'level': 'green' if smoking_status != 'Former Smoker' and smoke_cess != 'not stated' and result != 'Excluded'  else 'null',
						'condition': 'No', 
						'result': 'green' if smoking_status != 'Former Smoker' and smoke_cess != 'not stated' and result != 'Excluded'  else 'null',
						}
					]
					}
					]
			}

		]]



		return result

	def QualityMeasure9(self):
		
		patient = self.patient

		current_date = datetime(2100, 1, 1).date()

		try:
			clinical_trail_init = True if len(patient['clinicalTrials']) > 0 else False
		except:
			clinical_trail_init = False

		try:
			clinical_enroll = True if patient['clinicalTrials'][0]['enrollmentStatus'].lower() == 'yes' else False
		except:
			clinical_enroll = False

		try:
			clinical_date = Measure.str_to_date(self, patient['clinicalTrials'][0]['enrollmentDate'])
		except:
			clinical_date = current_date

		try:
			rt_start_dates = []

			for plan in patient['treatmentSummary'][0]['ebrt']:
				rt_start_dates.append(Measure.str_to_date(self, plan['startDate']))

			rt_start_date = sorted(rt_start_dates)[0]
		except:
			rt_start_date = current_date


		if clinical_trail_init and clinical_enroll and clinical_date < rt_start_date:
			result = 'Pass'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, 
					[{'name': 'Clinical Trial Enrollment is initalized',
					'parent': 'null',
					'children': [{
						'name': '"Yes" selected for Clinical Trial Enrollment',
						'parent': 'Clinical Trial Enrollment is initalized',
						'level': 'green' if clinical_trail_init else 'null',
						'condition': 'Yes', 
						'children': [{
							'name': 'Fail',
							'parent': 'Yes" selected for Clinical Trial Enrollment',
							'level': 'green' if not clinical_enroll else 'null',
							'condition': 'No', 
							'result': 'red' if not clinical_enroll else 'null',
							},
							{
							'name': 'Clinical Trial Enrollment Date < RT Start Date',
							'parent': '"Yes" selected for Clinical Trial Enrollment',
							'level': 'green' if clinical_enroll else 'null',
							'condition': 'Yes', 
							'children': [{
								'name': 'Pass',
								'parent': 'Clinical Trial Enrollment Date < RT Start Date',
								'level': 'green' if clinical_date < rt_start_date else 'null',
								'condition': 'Yes', 
								'result': 'green' if clinical_date < rt_start_date else 'null',
										},
								{
								'name': 'Fail',
								'parent': 'Clinical Trial Enrollment Date < RT Start Date',
								'level': 'green' if not clinical_date < rt_start_date and clinical_enroll else 'null',
								'condition': 'No', 
								'result': 'red' if not clinical_date < rt_start_date and clinical_enroll else 'null',
										}]
									}]
								},
							{
							'name': 'Fail',
							'parent': 'Clinical Trial Enrollment is initalized',
							'level': 'green' if not clinical_trail_init else 'null',
							'condition': 'No', 
							'result': 'red' if not clinical_trail_init else 'null',
								}]
								
					}]
				]

		return result


	def QualityMeasure10(self):
		patient = self.patient
		
		current_date = datetime(2100, 1, 1).date()

		try:
			#imp_cardiac_dev_source = patient['consult'][0]['implantableCardiacDeviceSource'].lower()
			imp_cardiac_dev_source = 'consult' if patient['consult'] else None
		except:
			imp_cardiac_dev_source = None

		try:
			imp_cardiac_dev_date = Measure.str_to_date(self, patient['consult'][0]['implantableCardiacDeviceDate'])
		except:
			imp_cardiac_dev_date = current_date

		try:
			sim_date = Measure.str_to_date(self, patient['treatmentSummary'][0]['otherInformation']['dateOfSimulation'])
		except:
			sim_date = current_date

		logging.info([str(item) for item in [imp_cardiac_dev_source, imp_cardiac_dev_date, sim_date, patient['caseId']]])


		if (imp_cardiac_dev_source != 'not stated') and (imp_cardiac_dev_date <= sim_date):
			result = 'Pass'
		else:
			result = 'Fail'


		result = [patient['caseId'], result, [{
			'name': '"Not stated" selected for Implantable Cardiac Device',
			'parent': 'null',
			'children': [{
				'name': 'Fail',
				'parent': '"Not stated" selected for Implantable Cardiac Device',
				'level': 'green' if imp_cardiac_dev_source == 'not stated' else 'null',
				'condition': 'Yes', 
				'result': 'red' if imp_cardiac_dev_source == 'not stated' else 'null'
				},
				{
				'name': 'Implantable Cardiac Device date <= Simulation date',
				'parent': '"Not stated" selected for Implantable Cardiac Device',
				'level': 'green' if imp_cardiac_dev_source != 'not stated' else 'null',
				'condition': 'No', 
				'children': [{
					'name': 'Pass',
					'parent': 'Implantable Cardiac Device date <= Simulation date',
					'level': 'green' if imp_cardiac_dev_date <= sim_date else 'null',
					'condition': 'Yes', 
					'result': 'green'  if imp_cardiac_dev_date <= sim_date else 'null',
					},
					{
					'name': 'Fail',
					'parent': 'Implantable Cardiac Device date <= Simulation date',
					'level': 'green' if imp_cardiac_dev_date > sim_date else 'null',
					'condition': 'No', 
					'result': 'red'  if imp_cardiac_dev_date > sim_date else 'null',
					}
					]
				}
			]
			}
		]]

		return result

	def QualityMeasure11(self):
		patient = self.patient
		
		valid_modality = ['3d', 'imrt']

		try:
			if 'treatmentSummary' in patient:
				had_ebrt = True if (len(patient['treatmentSummary'][0]['ebrt'][0]) > 0) else False
		except:
			had_ebrt = False

		try:
			ebrt_modality = []
			if 'treatmentSummary' in patient:
				for item in patient['treatmentSummary'][0]['ebrt']:
					ebrt_modality.append(item['modality'] if item['modality'].lower() in valid_modality else False)

			ebrt_modality = False if False in ebrt_modality else True

		except:
			ebrt_modality = None

		logging.info([str(item) for item in [had_ebrt, ebrt_modality, patient['caseId']]])

		if had_ebrt and (ebrt_modality):
			result = 'Pass'
		elif not had_ebrt:
			result = 'Excluded'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
					'name': 'Did the patient have EBRT?',
					'parent': 'null', 
					'children': [{
						'name': 'Excluded', 
						'parent': 'Did the patient have EBRT?',
						'level': 'green' if not had_ebrt else 'null',
						'condition': 'No',
						'result': 'blue' if not had_ebrt else 'null', 
						},
						{
						'name': 'For each EBRT Plan: Is "3D" or "IMRT" selected?',
						'parent': 'Did the patient have EBRT?',
						'level': 'green' if had_ebrt else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Fail',
							'parent': 'For each EBRT Plan: Is "3D" or "IMRT" selected?',
							'level': 'green' if had_ebrt and not ebrt_modality else 'null',
							'condition': 'No',
							'result': 'red' if had_ebrt and not ebrt_modality else 'null',
							},
							{
							'name': 'Pass',
							'parent': 'For each EBRT Plan: Is "3D" or "IMRT" selected?',
							'level': 'green' if had_ebrt and ebrt_modality else 'null', 
							'condition': 'Yes',
							'result': 'green' if had_ebrt and ebrt_modality else 'null'
							}
							]
						}
						]
					}

		]]
		return result

	def QualityMeasure12(self):
		patient = self.patient
		
		valid_structures = set(['heart', 'esophagus', 'spinal cord'])

		try:
			had_dvh_analysis = True if patient['treatmentSummary'][0]['otherInformation']['dvhAnalysisPerformed'].lower() == 'yes' else False
		except:
			had_dvh_analysis = False

		try:
			evaluated_strucutres = [structure.lower() for structure in patient['treatmentSummary'][0]['otherInformation']['dvhStructuresEvaluated']]
		except:
			evaluated_strucutres = [None]

		try:
			lung_eval = True if 'lung' in evaluated_strucutres else False
		except:
			lung_eval = False

		try:
			other_eval = True if len(set(evaluated_strucutres).intersection(valid_structures)) >= 2 else False
		except:
			other_eval = False

		if had_dvh_analysis and lung_eval and other_eval:
			result = 'Pass'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
					'name': 'Is there a DVH analysis?',
					'parent': 'null',
					'children': [{
						'name': 'Fail',
						'parent': 'Is there a DVH analysis?',
						'level': 'green' if not had_dvh_analysis else 'null',
						'condition': 'No',
						'result': 'red' if not had_dvh_analysis else 'null',
							},
						{
						'name': 'Are the lungs and 2 or more of Spinal Cord, Esophagus, or Heart \n selected in "Structures Evaluated"?',
						'parent': 'Is there a DVH analysis?',
						'level': 'green' if had_dvh_analysis else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Pass',
							'parent': 'Are the lungs and 2 or more of the following OARs selected in "Strucutres Evaluated" (Spinal Cord, Esophagus, Heart)?',
							'level': 'green' if lung_eval and other_eval else 'null',
							'condition': 'Yes',
							'result': 'green' if lung_eval and other_eval else 'null',
							}, 
							{
							'name': 'Fail',
							'parent': 'Are the lungs and 2 or more of the following OARs selected in "Strucutres Evaluated" (Spinal Cord, Esophagus, Heart)?',
							'level': 'green' if not lung_eval and had_dvh_analysis or not other_eval and had_dvh_analysis else 'null',
							'condition': 'No',
							'result': 'red' if not lung_eval and had_dvh_analysis or not other_eval and had_dvh_analysis else 'null',
							}
							]
						}
					]

		}]]

		return result

	def QualityMeasure13(self):
		patient = self.patient

		valid_algorithm = ['convolution', 'monte carlo', 'grid boltzman solver']
		
		try:
			algorithm = patient['treatmentSummary'][0]['otherInformation']['planningAlgorithm'].lower()
		except:
			algorithm = None

		if algorithm in valid_algorithm:
			result = 'Pass'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
					'name': 'Is "Convolution", "Monte Carolo" or "Grid Boltzman Solver" selected as the algorithm?',
					'parent': 'null',
					'children': [{
						'name': 'Pass',
						'parent': 'Is "Convolution", "Monte Carolo" or "Grid Boltzman Solver" selected as the algorithm?',
						'level': 'green' if algorithm in valid_algorithm else 'null',
						'condition': 'Yes',
						'result': 'green' if algorithm in valid_algorithm else 'null',
						},
						{
						'name': 'Fail',
						'parent': 'Is "Convolution", "Monte Carolo" or "Grid Boltzman Solver" selected as the algorithm?',
						'level': 'green' if algorithm not in valid_algorithm else 'null',
						'condition': 'No',
						'result': 'red' if algorithm not in valid_algorithm else 'null',
						}
					]

			}]]

		return result

	def QualityMeasure14(self):
		patient = self.patient
		
		try:
			is_sim_note = True if patient['treatmentSummary'][0]['otherInformation']['isSimNote'].lower() == 'yes' else False
		except:
			is_sim_note = False

		try:
			if 'nsclcMotionManagement' in patient['treatmentSummary'][0]['otherInformation']:
				none_motion = True if 'None' in patient['treatmentSummary'][0]['otherInformation']['nsclcMotionManagement'] else False 
			if 'sclcMotionManagement' in patient['treatmentSummary'][0]['otherInformation']:
				none_motion = True if 'None' in patient['treatmentSummary'][0]['otherInformation']['sclcMotionManagement'] else False
		except:
			none_motion = False

		if is_sim_note and not none_motion:
			result = 'Pass'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
					'name': 'Is SIM Note a "Yes"?',
					'parent': 'null',
					'children': [{
						'name': 'Fail',
						'parent': 'Is SIM Note a "Yes"?',
						'level': 'green' if not is_sim_note else 'null',
						'condition': 'No',
						'result': 'red' if not is_sim_note else 'null',
						},
						{
						'name': 'Is "None" selected in Motion Management?',
						'parent': 'Is SIM Note a "Yes"?',
						'level': 'green' if is_sim_note else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Pass', 
							'parent': 'Is "None" selected in Motion Management?',
							'level': 'green' if is_sim_note and not none_motion else 'null',
							'condition': 'No',
							'result': 'green' if is_sim_note and not none_motion else 'null'
							},
							{
							'name': 'Fail', 
							'parent': 'Is "None" selected in Motion Management?',
							'level': 'green' if is_sim_note and none_motion else 'null',
							'condition': 'Yes',
							'result': 'red' if is_sim_note and none_motion else 'null'
							}
							]
						}
						]
			}]]
		return result

	def QualityMeasure15(self):
		patient = self.patient

		current_date = datetime(2100, 1, 1).date()
		
		try:
			# if 'pathology' in patient:
			# 	is_path_report = len(patient['pathology']) > 1  
			is_path_report = True if patient['pathology']['isPathologyReport'].lower() == 'yes' else False
		except:
			is_path_report = False

		try:
			if 'pathology' in patient:
				path_report_date = Measure.str_to_date(self, patient['pathology']['pathologyReportDate'])
		except:
			path_report_date = current_date

		try:
			rt_start_dates = []

			for plan in patient['treatmentSummary'][0]['ebrt']:
				rt_start_dates.append(Measure.str_to_date(self, plan['startDate']))

			rt_start_date = sorted(rt_start_dates)[0]
		except:
			rt_start_date = current_date

		try:
			if 'diagnosis' in patient:
				had_surgery = True if (patient['diagnosis']['previousSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False

		try:
			if 'diagnosis' in patient:
				surgery_date = Measure.str_to_date(self, patient['diagnosis']['surgeryDate'])
		except:
			surgery_date = current_date 

		try:
			if 'chemotherapy' in patient:
				had_chemo = len(patient['chemotherapy'][0]) > 0
		except:
			had_chemo = False

		try:
			if 'chemotherapy' in patient:
				chemo_date = Measure.str_to_date(self, patient['chemotherapy'][0]['chemotherapyStartDate'])
		except:
			chemo_date = current_date

		path_rt_diff = True if ((path_report_date + timedelta(days=28)) >= rt_start_date and path_report_date <= rt_start_date) else False
		path_surgery_diff = True if ((path_report_date + timedelta(days=28)) >= surgery_date and path_report_date <= surgery_date) else False
		path_chemo_diff = True if ((path_report_date + timedelta(days=28)) >= chemo_date and path_report_date <= chemo_date) else False

		if not is_path_report:
			result = 'Excluded'

		elif is_path_report and path_rt_diff or \
				is_path_report and not path_rt_diff and had_surgery and (surgery_date != current_date) and path_surgery_diff or \
				is_path_report and not path_rt_diff and (not had_surgery or (had_surgery and surgery_date == current_date) or \
				(had_surgery and surgery_date != current_date and not path_surgery_diff)) and had_chemo and path_chemo_diff:
				result = 'Pass'

		else:
			result = 'Fail' 

		result = [patient['caseId'], result, [{
					'name': 'Is there a pathology report?',
					'parent': 'null',
					'children': [{
						'name': 'Excluded',
						'parent': 'Is there a pathology report?',
						'level': 'green' if result == 'Excluded' else 'null',
						'condition': 'No',
						'result': 'blue' if result == 'Excluded' else 'null',
						},
						{
						'name': 'Pathology Report date + 28 days >= RT Start Date',
						'parent': 'Is there a pathology report',
						'level': 'green' if result != 'Excluded' else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Pass',
							'parent': 'Pathology Report date + 28 days >= RT Start Date',
							'level': 'green' if result != 'Excluded' and path_rt_diff else 'null',
							'condition': 'Yes',
							'result': 'green' if result != 'Excluded' and path_rt_diff else 'null',
							},
							{
							'name': 'Patient has had surgery',
							'parent': 'Pathology Report date + 28 days >= RT Start Date',
							'level': 'green' if result != 'Excluded' and not path_rt_diff else 'null',
							'condition': 'No',
							'children': [{
								'name': 'Surgery date is available',
								'parent': 'Patient has had surgery',
								'level': 'green' if result != 'Excluded' and not path_rt_diff and had_surgery else 'null',
								'condition': 'Yes',
								'children': [{
									'name': 'Pathology Report date + 28 days >= Surgery date',
									'parent': 'Patient has had surgery',
									'level': 'green' if result != 'Excluded' and not path_rt_diff and surgery_date != current_date else 'null',
									'condition': 'Yes',
									'children': [{
										'name': 'Pass',
										'parent': 'Pathology Report date + 28 days >= Surgery date',
										'level': 'green' if result == 'Pass' and path_surgery_diff and surgery_date != current_date else 'null',
										'condition': 'Yes',
										'result': 'green' if result == 'Pass' and path_surgery_diff and surgery_date != current_date else 'null',
										},
										{
										'name': 'Patient has had chemotherapy',
										'parent': 'Patient has had surgery',
										'level': 'null',
										'condition': 'No'
										}]
									},
									{
									'name': 'Patient has had chemotherapy',
									'parent': 'Patient has had surgery',
									'level': 'null',
									'condition': 'No'
									}]
								},
								{
								'name': 'Patient has had chemotherapy',
								'parent': 'Patient has had surgery',
								'level': 'green' if result != 'Excluded' and not path_rt_diff and not had_surgery else 'null',
								'condition': 'No',
								'children': [{
									'name': 'Fail',
									'parent': 'Patient has had chemotherapy',
									'level': 'green' if not had_chemo and result == 'Fail' else 'null',
									'condition': 'No',
									'result': 'red' if not had_chemo and result == 'Fail' else 'null'
									},
									{
									'name': 'Pathology Report date + 28 days >= Chemotherapy Start date',
									'parent': 'Patient has had chemotherapy',
									'level': 'green' if result != 'Excluded' and not path_rt_diff and not path_surgery_diff and had_chemo else 'null',
									'condition': 'Yes',
									'children': [{
										'name': 'Pass',
										'parent': 'Pathology Report date + 28 days >= Chemotherapy Start date',
										'level': 'green' if result != 'Excluded' and not path_rt_diff and not path_surgery_diff and path_chemo_diff else 'null',
										'condition': 'Yes',
										'result': 'green' if result != 'Excluded' and not path_rt_diff and not path_surgery_diff and path_chemo_diff else 'null',
										},
										{
										'name': 'Fail',
										'parent': 'Pathology Report date + 28 days >= Chemotherapy Start date',
										'level': 'green' if result != 'Excluded' and not path_rt_diff and not path_surgery_diff and not path_chemo_diff else 'null',
										'condition': 'No',
										'result': 'red' if result != 'Excluded' and not path_rt_diff and not path_surgery_diff and not path_chemo_diff else 'null',
										}
										] 
									}
									]
								}
								]
							}
							]
						}
						]
		}]]

		return result

	def QualityMeasure16(self):
		patient = self.patient

		current_date = datetime(2100, 1, 1).date()

		try:
			consult_date = Measure.str_to_date(self, patient['consult'][0]['multidisciplinaryConsultDate'])
		except:
			consult_date = current_date

		try:
			rt_start_dates = []

			for plan in patient['treatmentSummary'][0]['ebrt']:
				rt_start_dates.append(Measure.str_to_date(self, plan['startDate']))

			rt_start_date = sorted(rt_start_dates)[0]
		except:
			rt_start_date = current_date

		if (consult_date + timedelta(days=21)) >= rt_start_date and rt_start_date >= consult_date:
			result = 'Pass'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
					'name': 'Consult Date + 21 says >= RT Start date',
					'parent': 'null',
					'children': [{
						'name': 'Pass',
						'parent': 'Consult Date + 21 says >= RT Start date',
						'level': 'green' if result == 'Pass' else 'null',
						'condition': 'Yes', 
						'result': 'green' if result == 'Pass' else 'null',
						}, 
						{
						'name': 'Fail',
						'parent': 'Consult Date + 21 says >= RT Start date',
						'level': 'green' if result == 'Fail' else 'null',
						'condition': 'No', 
						'result': 'red' if result == 'Fail' else 'null',
						}
						]
		}]]

		return result


	def QualityMeasure17(self):
		patient = self.patient
		
		current_date = datetime(2100, 1, 1).date()

		try:
			is_sim = True if patient['treatmentSummary'][0]['otherInformation']['isSimNote'].lower() == 'yes' else False
		except:
			is_sim = False

		try:
			sim_date = Measure.str_to_date(self, patient['treatmentSummary'][0]['otherInformation']['dateOfSimulation'])
		except:
			sim_date = current_date

		try:
			rt_start_dates = []

			for plan in patient['treatmentSummary'][0]['ebrt']:
				rt_start_dates.append(Measure.str_to_date(self, plan['startDate']))

			rt_start_date = sorted(rt_start_dates)[0]
		except:
			rt_start_date = current_date


		#Doesn't match washu results due to "and is_sim" matches perfectly without this line
		if (sim_date + timedelta(days=14)) >= rt_start_date and is_sim and rt_start_date >= sim_date:
			result = 'Pass'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
					'name': 'SIM note is available',
					'parent': 'null',
					'children': [{
						'name': 'Fail',
						'parent': 'SIM note is available',
						'level': 'green' if not is_sim else 'null',
						'condition': 'No',
						'result': 'red' if not is_sim else 'null'
						},
						{
						'name': 'Simulation date + 14 days >= RT Start date',
						'parent': 'SIM note is available',
						'level': 'green' if is_sim else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Pass',
							'parent': 'Simulation date + 14 days >= RT Start date',
							'level': 'green' if result == 'Pass' else 'null',
							'condition': 'Yes',
							'result': 'green' if result == 'Pass' else 'null',
							},
							{
							'name': 'Fail',
							'parent': 'Simulation date + 14 days >= RT Start date',
							'level': 'green' if is_sim and result == 'Fail' else 'null',
							'condition': 'No',
							'result': 'red' if is_sim and result == 'Fail' else 'null',
							}
							]
						}
						]
		}]]

		return result

	def QualityMeasure18(self):
		patient = self.patient

		poor_otv = ['ecog', 'who', 'zubrod']
		valid_source = ['consult', 'addendum', 'other']
		current_date = datetime(2100, 1, 1).date()

		try:
			
			otv_scores = []

			for note in patient['otv']:

				if 'performanceStatus' in note:

					if 'performanceInstrument' in note['performanceStatus'] and 'performanceScore' in note['performanceStatus']:

						if note['performanceStatus']['performanceInstrument'].lower() in poor_otv and \
							int(note['performanceStatus']['performanceScore']) >= 2:
							otv_scores.append(True)
					
						elif note['performanceStatus']['performanceInstrument'].lower() == 'kps' and \
							int(note['performanceStatus']['performanceScore']) <= 60:
							otv_scores.append(True)

						else:
							pass

			if 'performanceStatus' in patient['consult'][0]:

				for item in patient['consult'][0]['performanceStatus']:

					if item['performanceInstrument'].lower() in poor_otv and \
						int(item['performanceScore']) >= 2:
						otv_scores.append(True)
					
					elif item['performanceInstrument'].lower() == 'kps' and \
						int(item['performanceScore']) <= 60:
						otv_scores.append(True)

					else:
						pass

			else:
				pass

			otv_score = True if (True in otv_scores) else False
		except:
			otv_score = None

		try:
			#chemo_source = True if patient['chemotherapy'][0]['chemotherapySource'].lower() in valid_source else False
			chemo_source = True if patient['consult'] else False
		except:
			chemo_source = False

		try:
			if 'chemotherapy' in patient:
				chemo_start_date = Measure.str_to_date(self, patient['chemotherapy'][0]['chemotherapyStartDate'])
		except:
			chemo_start_date = current_date

		try:
			rt_start_dates = []

			for plan in patient['treatmentSummary'][0]['ebrt']:
				rt_start_dates.append(Measure.str_to_date(self, plan['startDate']))

			rt_start_date = sorted(rt_start_dates)[0]
		except:
			rt_start_date = current_date

		try:
			rt_end_dates = []

			for plan in patient['treatmentSummary'][0]['ebrt']:
				rt_end_dates.append(Measure.str_to_date(self, plan['endDate']))

			rt_end_date = sorted(rt_end_dates)[-1]
		except:
			rt_end_date = current_date

		try:
			if 'chemotherapy' in patient:
				chemo_end_date = Measure.str_to_date(self, patient['chemotherapy'][0]['chemotherapyEndDate'])
		except:
			chemo_end_date = current_date

		chemo_rt_overlap = True if ((rt_start_date <= chemo_start_date <= rt_end_date) or (rt_start_date <= chemo_end_date <= rt_end_date) or \
								 (chemo_start_date <= rt_start_date <= chemo_end_date) or (chemo_start_date <= rt_end_date <= chemo_end_date) or \
									(chemo_end_date <= rt_start_date <= (chemo_end_date + timedelta(days=7)))) else False

		if otv_score and chemo_source and chemo_rt_overlap:
			result = 'Excluded'
			qm19 = 1
		elif otv_score:
			result = 'Excluded'
			qm19 = 2
		elif (not otv_score) and chemo_source and chemo_rt_overlap:
			result = 'Pass'
			qm19 = 1
		else:
			result = 'Fail'
			qm19 = 0

		result = [patient['caseId'], result, [{
					'name': 'PS in either consult or any OTV is poor (KPS <= 60 or ECOG/WHO/ZUBROD >= 2)',
					'parent': 'null',
					'children': [{
						'name': 'Exclude for QM 18',
						'parent': 'PS in either consult or any OTV is poor (KPS <= 60 or ECOG/WHO/ZUBROD >= 2)',
						'level': 'green' if result == 'Excluded' else 'null',
						'condition': 'Yes',
						'result': 'blue' if result == 'Excluded' else 'null',
						'children': [{
							'name': 'Consult, Addendum, or other \n selected for Chemotherapy',
							'parent': 'Exclude for QM 18',
							'level': 'blue' if otv_score else 'null',
							'children': [{
								'name': 'Fail for QM 19 and 20',
								'parent': 'Consult, Addendum, or other selected for Chemotherapy',
								'level': 'green' if otv_score and not chemo_source else 'null',
								'condition': 'No',
								'result': 'red' if otv_score and not chemo_source else 'null', 
								},
								{
								'name': 'Chemotherapy overlaps RT or is one week \n prior to RT start',
								'parent': 'Consult, Addendum, or other selected for Chemotherapy',
								'level': 'green' if otv_score and chemo_source else 'null',
								'condition': 'Yes',
								'children': [{
									'name': 'Concurrent for QM 19 and 20',
									'parent': 'Chemotherapy overlaps RT or is one week prior to RT start',
									'level': 'green' if qm19 == 1 and result == 'Excluded' else 'null',
									'condition': 'Yes',
									'result': 'green' if qm19 == 1 and result == 'Excluded' else 'null'
									},
									{
									'name': 'Fail for QM 19 and 20',
									'parent': 'Chemotherapy overlaps RT or is one week prior to RT start',
									'level': 'green' if otv_score and chemo_source and not chemo_rt_overlap else 'null',
									'condition': 'No',
									'result': 'red' if otv_score and chemo_source and not chemo_rt_overlap else 'null'
									}
									]
								}]
							}]
						},
						{
						'name': 'Consult, Addendum, or other selected for Chemotherapy',
						'parent': 'PS in either consult or any OTV is poor (KPS <= 60 or ECOG/WHO/ZUBROD >= 2)',
						'level': 'green' if not otv_score else 'null',
						'condition': 'No',
						'children': [{
							'name': 'Fail',
							'parent': 'Consult, Addendum, or other selected for Chemotherapy',
							'level': 'green' if not otv_score and not chemo_source else 'null',
							'condition': 'No',
							'result': 'red' if not otv_score and not chemo_source else 'null', 
							},
							{
							'name': 'Chemotherapy overlaps RT or is one week prior to RT start',
							'parent': 'Consult, Addendum, or other selected for Chemotherapy',
							'level': 'green' if not otv_score and chemo_source else 'null',
							'condition': 'Yes',
							'children': [{
								'name': 'Pass',
								'parent': 'Chemotherapy overlaps RT or is one week prior to RT start',
								'level': 'green' if result == 'Pass' else 'null',
								'condition': 'Yes',
								'result': 'green' if result == 'Pass' else 'null'
								},
								{
								'name': 'Fail',
								'parent': 'Chemotherapy overlaps RT or is one week prior to RT start',
								'level': 'green' if not otv_score and chemo_source and not chemo_rt_overlap else 'null',
								'condition': 'No',
								'result': 'red' if not otv_score and chemo_source and not chemo_rt_overlap else 'null'
								}
								]
							}
							]
						}]}]	
		 ,qm19]

		return result

	def QualityMeasure19(self):
		patient = self.patient
		
		try:
			if 'treatmentSummary' in patient:
				is_sbrt = True if patient['treatmentSummary'][0]['ebrt'][0]['modality'].lower() == 'sbrt' else False
		except:
			is_sbrt = False

		try:
			on_clinical_trial = True if (self.QualityMeasure9()[1] == 1) else False
		except:
			on_clinical_trial = False

		try:
			if 'treatmentSummary' in patient:
				dose_per_frac = 0
				for item in patient['treatmentSummary'][0]['ebrt']:
					dose = float(item['prescriptionDose']) * 100
					fractions = float(item['numberOfPlannedFractions'])
					if 180 <= (dose / fractions) <= 200:
						dose_per_frac += 1
				dose_per_fraction = True if dose_per_frac == len(patient['treatmentSummary'][0]['ebrt']) and len(patient['treatmentSummary'][0]['ebrt']) != 0 else False
		except:
			dose_per_fraction = False

		try:
			if 'treatmentSummary' in patient:
				dose = 0
				for item in patient['treatmentSummary'][0]['ebrt']:
					dose += float(item['prescriptionDose'])
		except:
			dose = 0 

		try:
			con_chemo = True if (self.QualityMeasure18()[1] == 1 or self.QualityMeasure18()[-1] == 1) else False
		except:
			con_chemo = False

		try:
			dose_59_70 = True if (59 <= dose <=70) else False
		except:
			dose_59_70 = False

		try:
			dose_59_84 = True if (59 <= dose <= 84) else False
		except:
			dose_59_84 = False

		try:
			dose_greater_84 = True if (dose > 84) else False
		except:
			dose_greater_84 = False

		try:
			dose_74_84 = True if (74 < dose <= 84) else False
		except:
			dose_74_84 = False


		if '-SCLC' in patient['caseId']:
			result = ""
			color = ""
		elif is_sbrt or (not is_sbrt and on_clinical_trial) or (not is_sbrt and not on_clinical_trial and not dose_per_fraction):
			result = 'Excluded'
			color = ""
		elif not is_sbrt and not on_clinical_trial and dose_per_fraction and con_chemo and not dose_59_70 or \
					not is_sbrt and not on_clinical_trial and dose_per_fraction and not con_chemo and not dose_59_84 and not dose_greater_84:
					result = 'Fail'
					color = ""
		elif not is_sbrt and not on_clinical_trial and dose_per_fraction and (not con_chemo) and dose_59_84 and not dose_74_84:
			result = 'Pass'
			color = 'Green'
		else:
			result = 'Pass'
			color = ""

		result = [patient['caseId'], result, [{
			'name': 'Is SBRT selected for EBRT?',
			'parent': 'null',
			'children': [{
				'name': 'Excluded',
				'parent': 'Is SBRT selected for EBRT?',
				'level': 'green' if is_sbrt else 'null',
				'condition': 'Yes',
				'result': 'blue' if is_sbrt else 'null'
				},
				{
				'name': 'On a clinical trial',
				'parent': 'Is SBRT selected in EBRT?',
				'level': 'green' if not is_sbrt else 'null',
				'condition': 'No',
				'children': [{
					'name': 'Excluded',
					'parent': 'On a clinical trial',
					'level': 'green' if not is_sbrt and on_clinical_trial else 'null',
					'condition': 'Yes',
					'result': 'blue' if not is_sbrt and on_clinical_trial else 'null'
					},
					{
					'name': 'Is the dose per fraction between 180 and 200 cGy/ Fx?',
					'parent': 'On a clinical trial',
					'level': 'green' if not is_sbrt and not on_clinical_trial else 'null',
					'condition': 'No',
					'children': [{
						'name': 'Excluded',
						'parent': 'Is the dose per fraction between 180 and 200 cGy/ Fx?',
						'level': 'green' if not is_sbrt and not on_clinical_trial and not dose_per_fraction else 'null',
						'condition': 'No',
						'result': 'blue' if not is_sbrt and not on_clinical_trial and not dose_per_fraction else 'null'
						},
						{
						'name': 'Did they get concurrent chemotherapy?',
						'parent': 'Is the dose per fraction between 180 and 200 cGy/ Fx?',
						'level': 'green' if result != 'Excluded' else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Is the dose between 59 Gy and 70 Gy?',
							'parent': 'Did they get concurrent chemotherapy?',
							'level': 'green' if result != 'Excluded' and con_chemo else 'null',
							'condition': 'Yes',
							'children': [{
								'name': 'Pass',
								'parent': 'Is the dose between 59 Gy and 70 Gy?',
								'level': 'green' if result != 'Excluded' and con_chemo and dose_59_70 else 'null',
								'condition': 'Yes',
								'result': 'green' if result != 'Excluded' and con_chemo and dose_59_70 else 'null'
								},
								{
								'name': 'Fail',
								'parent': 'Is the dose between 59 Gy and 70 Gy?',
								'level': 'green' if result != 'Excluded' and con_chemo and not dose_59_70 else 'null',
								'condition': 'No',
								'result': 'red' if result != 'Excluded' and con_chemo and not dose_59_70 else 'null'
								}
								]
							},
							{
							'name': 'Is the dose between 59 Gy and 84 Gy?',
							'parent': 'Did they get concurrent chemotherapy?',
							'level': 'green' if result != 'Excluded' and not con_chemo else 'null',
							'condition': 'No',
							'children': [{
								'name': 'Is the dose between 74 Gy and 84 Gy?',
								'parent': 'Is the dose between 59 Gy and 84 Gy?',
								'level': 'green' if result != 'Excluded' and not con_chemo and dose_59_84 else 'null',
								'condition': 'Yes',
								'children': [{
									'name': 'Pass, Yellow',
									'parent': 'Is the dose between 74 Gy and 84 Gy?',
									'level': 'green' if result != 'Excluded' and not con_chemo and dose_74_84 else 'null',
									'condition': 'Yes',
									'result': 'green' if result != 'Excluded' and not con_chemo and dose_74_84 else 'null',
									},
									{
									'name': 'Pass, Green',
									'parent': 'Is the dose between 74 Gy and 84 Gy?',
									'level': 'green' if result != 'Excluded' and not con_chemo and dose_59_84 and not dose_74_84 else 'null',
									'condition': 'No',
									'result': 'green' if result != 'Excluded' and not con_chemo and dose_59_84 and not dose_74_84 else 'null',
									}
									]
								},
								{
								'name': 'Is the dose greater than 84 Gy?',
								'parent': 'Is the dose between 59 Gy and 84 Gy?',
								'level': 'green' if result != 'Excluded' and not con_chemo and not dose_59_84 else 'null',
								'condition': 'No',
								'children': [{
									'name': 'Pass, Red',
									'parent': 'Is the dose greater than 84 Gy?',
									'level': 'green' if result != 'Excluded' and not con_chemo and not dose_59_84 and dose_greater_84 else 'null',
									'condition': 'Yes',
									'result': 'green' if result != 'Excluded' and not con_chemo and not dose_59_84 and dose_greater_84 else 'null',
									},
									{
									'name': 'Fail',
									'parent': 'Is the dose greater than 84 Gy?',
									'level': 'green' if result != 'Excluded' and not con_chemo and not dose_59_84 and not dose_greater_84 else 'null',
									'condition': 'No',
									'result': 'red' if result != 'Excluded' and not con_chemo and not dose_59_84 and not dose_greater_84 else 'null',
									}
									]
								}
								]
							}
							]
						}
						]
					}
					]
				}
				]
		}], color]

		return result

	def QualityMeasure19_color(self):
		patient = self.patient

		result = self.QualityMeasure19()[-1]

		return [patient['caseId'], result]

	def QualityMeasure20(self):
		patient = self.patient

		try:
			con_chemo = True if (self.QualityMeasure18()[1] == 1 or self.QualityMeasure18()[-1] == 1) else False
		except:
			con_chemo = False

		try:
			on_clinical_trial = True if (self.QualityMeasure9()[1] == 1) else False
		except:
			on_clinical_trial = False

		try:
			is_bid = True if patient['treatmentSummary'][0]['ebrt'][0]['frequency'] == 'BID' else False
		except:
			is_bid = False

		try:
			if 'treatmentSummary' in patient:
				dose = 0
				for item in patient['treatmentSummary'][0]['ebrt']:
					dose += float(item['prescriptionDose'])
		except:
			dose = 0

		try:
			if 'treatmentSummary' in patient:
				dose_36_44 = True if (36.045 < dose < 44.005 and (patient['treatmentSummary'][0]['ebrt'][0]['numberOfPlannedFractions'] == 15)) else False
		except:
			dose_36_44 = False

		try:
			dose_48_77 = True if (48.6 <= dose <= 77) else False
		except:
			dose_48_77 = False

		try:
			dose_40 = True if (dose >= 40.5) else False
		except:
			dose_40 = False

		try:
			if 'treatmentSummary' in patient:
				dose_per_150 = 0
				dose_per_200 = 0
				for item in patient['treatmentSummary'][0]['ebrt']:
					dose = float(item['prescriptionDose']) * 100
					fractions = float(item['numberOfPlannedFractions'])
					if 180 <= round(dose / fractions) <= 200:
						dose_per_200 += 1
					elif 150 == (dose / fractions):
						dose_per_150 += 1
				dose_per_fraction_150 = True if (dose_per_150) == len(patient['treatmentSummary'][0]['ebrt']) and len(patient['treatmentSummary'][0]['ebrt']) != 0 else False
				dose_per_fraction_200 = True if (dose_per_200) == len(patient['treatmentSummary'][0]['ebrt']) and len(patient['treatmentSummary'][0]['ebrt']) != 0 else False
		except:
			dose_per_fraction_150 = False
			dose_per_fraction_200 = False

		if '-NSCLC' in patient['caseId']:
			result = ""

		elif (not con_chemo) or (con_chemo and on_clinical_trial):
			result = 'Excluded'
		elif (con_chemo) and (not on_clinical_trial) and dose_36_44 or (con_chemo) and (not on_clinical_trial) and  \
		 		(not dose_36_44) and dose_48_77 and dose_per_fraction_200 or (con_chemo) and (not on_clinical_trial) and is_bid and dose_40 and dose_per_fraction_150:
		 	result = 'Pass'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
					'name': 'Did they get concurrent chemotherapy?',
					'parent': 'null',
					'children': [{
						'name': 'Excluded',
						'parent': 'Did they get concurrent chemotherapy?',
						'level': 'green' if not con_chemo else 'null',
						'condition': 'No',
						'result': 'blue' if not con_chemo else 'null'
						},
						{
						'name': 'On a clinical trial',
						'parent': 'Did they get concurrent chemotherapy?',
						'level': 'green' if con_chemo else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Excluded',
							'parent': 'On a clinical trial',
							'level': 'green' if not con_chemo and on_clinical_trial else 'null',
							'condition': 'Yes',
							'result': 'green' if not con_chemo and on_clinical_trial else 'null'
							},
							{
							'name': 'Is "BID" selected',
							'parent': 'On a clinical trial',
							'level': 'green' if result != 'Excluded' else 'null',
							'condition': 'No',
							'children': [{
								'name': 'Dose >= 40.5 Gy and Dose/ Fx is 150 cGy/ Fx',
								'parent': 'Is "BID" selected',
								'level': 'green' if result != 'Excluded' and is_bid else 'null',
								'condition': 'Yes',
								'children': [{
									'name': 'Pass',
									'parent': 'Dose >= 40.5 Gy and Dose/ Fx is 150 cGy/ Fx',
									'level': 'green' if result == 'Pass' and is_bid else 'null',
									'condition': 'Yes',
									'result': 'green' if result == 'Pass' and is_bid else 'null',
									},
									{
									'name': 'Fail',
									'parent': 'Dose >= 40.5 Gy and Dose/ Fx is 150 cGy/ Fx',
									'level': 'green' if result == 'Fail' and is_bid else 'null',
									'condition': 'No',
									'result': 'red' if result == 'Fail' and is_bid else 'null',
									}
								]
							},
							{
							'name': 'Is the Dose between 36.045 and 44.005 Gy and total fractions is 15?',
							'parent': 'Is "BID" selected?',
							'level': 'green' if result != 'Excluded' and not is_bid else 'null', 
							'condition': 'No',
							'children': [{
								'name': 'Pass',
								'parent': 'Is the Dose between 36.045 and 44.005 Gy and total fractions is 15?',
								'level': 'green' if result != 'Excluded' and not is_bid and dose_36_44 else 'null',
								'condition': 'Yes',
								'result': 'green' if result != 'Excluded' and not is_bid and dose_36_44 else 'null',
								},
								{
								'name': 'Is the dose between 48.6 and 77 Gy and the dose/ fx is between 180 and 200 cGy',
								'parent': 'Is the Dose between 36.045 and 44.005 Gy and total fractions is 15?',
								'level': 'green' if result != 'Excluded' and not is_bid and not dose_36_44 else 'null',
								'condition': 'No',
								'children': [{
									'name': 'Pass',
									'parent': 'Is the dose between 48.6 and 77 Gy and the dose/ fx is between 180 and 200 cGy',
									'level': 'green' if result != 'Excluded' and not is_bid and not dose_36_44 and dose_48_77 and dose_per_fraction_200 else 'null',
									'condition': 'Yes',
									'result': 'green' if result != 'Excluded' and not is_bid and not dose_36_44 and dose_48_77 and dose_per_fraction_200 else 'null',
									},
									{
									'name': 'Fail',
									'parent': 'Is the dose between 48.6 and 77 Gy and the dose/ fx is between 180 and 200 cGy',
									'level': 'green' if result == 'Fail' and not is_bid else 'null',
									'condition': 'No',
									'result': 'red' if result == 'Fail'  and not is_bid else 'null',
									}
									]
								}]
							}
							]
						}
						]
		}]}]]

		return result

	def QualityMeasure21A(self): 
	#Technical page is unknown for 21A, affects results, eg 506-SCLC-05, unable to find tech page on otv
		patient = self.patient

		current_date = datetime(2100, 1, 1).date()
		
		try:
			is_pci = True if patient['treatmentSummary'][0]['pci']['treatmentStatus'] == 'Completed' else False
		except:
			is_pci = False

		try:
			pci_start = Measure.str_to_date(self, patient['treatmentSummary'][0]['pci']['startDate'])
		except:
			pci_start = current_date

		try:
			chemo_end_date = Measure.str_to_date(self, patient['chemotherapy'][0]['chemotherapyEndDate'])
		except:
			chemo_end_date = current_date

		try:
			rt_end_dates = []

			for plan in patient['treatmentSummary'][0]['ebrt']:
				rt_end_dates.append(Measure.str_to_date(self, plan['endDate']))

			rt_end_date = sorted(rt_end_dates)[-1]
		except:
			rt_end_date = current_date

		try:
			tmt_end_date = self.GetTreatmentDate()
		except:
			tmt_end_date = current_date

		try:
			extraction_date = current_date
		except:
			extraction_date = current_date

		if '-NSCLC' in patient['caseId']:
			result = ""

		elif (is_pci and chemo_end_date <= pci_start <= (chemo_end_date + timedelta(days=60))) or (is_pci and tmt_end_date <= pci_start <= (tmt_end_date + timedelta(days=60))):
			result = 'Pass'
		elif not is_pci and (extraction_date < (chemo_end_date + timedelta(days=60))) or not is_pci and (extraction_date < (rt_end_date + timedelta(days=60))):
			result = 'Excluded'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
					'name': 'Is PCI "Yes" on the Survivorship Care Plan/ PCI page',
					'parent': 'null',
					'children': [{
						'name': 'Is extraction date >= 60 days after either chemotherapy end or RT end?',
						'parent': 'Is PCI "Yes" on the Survivorship Care Plan/ PCI page',
						'level': 'green' if not is_pci else 'null',
						'condition': 'No',
						'children': [{
							'name': 'Excluded',
							'parent': 'Is PCI "Yes" on the Survivorship Care Plan/ PCI page',
							'level': 'green' if not is_pci and extraction_date < (chemo_end_date + timedelta(days=60) or \
										not is_pci and extraction_date < (rt_end_date + timedelta(days=60))) else 'null',
							'condition': 'No',
							'result': 'blue' if not is_pci and extraction_date < (chemo_end_date + timedelta(days=60) or \
										not is_pci and extraction_date < (rt_end_date + timedelta(days=60))) else 'null',
							},
							{
							'name': 'Fail',
							'parent': 'Is PCI "Yes" on the Survivorship Care Plan/ PCI page',
							'level': 'green' if not is_pci and extraction_date >= (chemo_end_date + timedelta(days=60) or \
										not is_pci and extraction_date >= (rt_end_date + timedelta(days=60))) else 'null',
							'condition': 'Yes',
							'result': 'red' if not is_pci and extraction_date >= (chemo_end_date + timedelta(days=60) or \
										not is_pci and extraction_date >= (rt_end_date + timedelta(days=60))) else 'null',
							}
							]
						},
						{
						'name': 'Was a PCI added on the Technical page?',
						'parent': 'Is PCI "Yes" on the Survivorship Care Plan/ PCI page',
						'level': 'green' if is_pci else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Fail',
							'parent': 'Was a PCI added on the Technical page?',
							'level': 'null' ,
							'condition': 'No',
							'result': 'null',
							},
							{
							'name': 'Is PCI Start Date <= 60 days after chemotherapy or treatment end date?',
							'parent': 'Was a PCI added on the Technical page?',
							'level': 'green' if is_pci else 'null',
							'condition': 'Yes',
							'children': [{
								'name': 'Pass',
								'parent': 'Is PCI Start Date <= 60 days after chemotherapy or treatment end date?',
								'level': 'green' if result == 'Pass' else 'null',
								'condition': 'Yes',
								'result': 'green' if result == 'Pass' else 'null', 
								},
								{
								'name': 'Fail',
								'parent': 'Is PCI Start Date <= 60 days after chemotherapy or treatment end date?',
								'level': 'green' if is_pci and result == 'Fail' else 'null',
								'condition': 'No',
								'result': 'red' if is_pci and result == 'Fail' else 'null', 
								}
								]
							}
							]
						}
						]
		}]]

		return result


	def QualityMeasure21B(self):
		#Technical page is unknown for 21B
		patient = self.patient

		try:
			is_pci = True if patient['treatmentSummary'][0]['pci']['treatmentStatus'] == 'Completed' else False
		except:
			is_pci = False

		try:
			prescription = True if patient['treatmentSummary'][0]['pci']['commonPrescription'].lower() == 'other' else False
		except:
			prescription = False

		if '-NSCLC' in patient['caseId']:
			result = ""

		elif not is_pci:
			result = 'Excluded'
		elif is_pci and not prescription:
			result = 'Pass'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
					'name': 'Is PCI "Yes" on the Survivorship Care Plan/ PCI Page',
					'parent': 'null',
					'children': [{
						'name': 'Excluded',
						'parent': 'Is PCI "Yes" on the Survivorship Care Plan/ PCI Page',
						'level': 'green' if not is_pci else 'null',
						'condition': 'No', 
						'result': 'blue' if not is_pci else 'null'
						},
						{
						'name': 'Was a PCI added on the Technical page?',
						'parent': 'Is PCI "Yes" on the Survivorship Care Plan/ PCI Page',
						'level': 'green' if is_pci else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Excluded',
							'parent': 'Was a PCI added on the Technical page?',
							'level': 'null',
							'condition': 'No',
							'result': 'null'
							},
							{
							'name': 'Is "other" selected for prescription?',
							'parent': 'Was a PCI added on the Technical page?',
							'level': 'green' if is_pci else 'null',
							'condition': 'Yes',
							'children': [{
								'name': 'Pass',
								'parent': 'Is "other" selected for prescription?',
								'level': 'green' if is_pci and not prescription else 'null',
								'condition': 'No',
								'result': 'green' if is_pci and not prescription else 'null', 
								},
								{
								'name': 'Fail',
								'parent': 'Is "other" selected for prescription?',
								'level': 'green' if is_pci and prescription else 'null',
								'condition': 'Yes',
								'result': 'red' if is_pci and prescription else 'null', 
								}
								]
							}
							]
						}
						]
		}]]

		return result

	def QualityMeasure22(self):
		patient = self.patient
	
		current_date = datetime(2100, 1, 1).date()

		note_list = ['lcss', 'fact', 'eortc']

		try:
			qol = True if patient['consult']['qualityOfLife'] else False
		except:
			qol = False

		try:
			treat_comp = self.GetTreatmentDate()
		except:
			treat_comp = current_date

		try:
			consult_date = Measure.str_to_date(self, patient['consult'][0]['multidisciplinaryConsultDate'])
		except:
			consult_date = current_date

		try:
			otv = len(patient['otv']) > 0 
		except:
			otv = False

		try:
			for item in patient['otv']:
				if 'qualityOfLife' in item:
					otv_note = True
					break
				else:
					otv_note = False
		except:
			otv_note = False

		try:
			note = []
			for item in patient['otv']:
				if 'qualityOfLife' in item:
					note.append('y' if item['qualityOfLife'][0]['qualityOfLifeInstrument'].lower() in note_list else 'n')
			notes = True if 'y' in note else False
		except:
			notes = False

		if qol and (consult_date < treat_comp) and notes or not qol and otv and otv_note and notes or qol and \
		 	not (consult_date < treat_comp) and otv and otv_note and notes:
			result = 'Pass'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
					'name': 'Consult, addendum, or toher is selected for QoL in consult section',
					'parent': 'null',
					'children': [{
						'name': 'OTV section is initialized',
						'parent': 'Consult, addendum, or toher is selected for QoL in consult section',
						'level': 'green' if not qol else 'null',
						'condition': 'No',
						'children': [{
							'name': 'Fail',
							'parent': 'OTV section is initalized',
							'level': 'green' if (not qol or qol and consult_date > treat_comp) and not otv else 'null',
							'condition': 'No',
							'result': 'red' if (not qol or qol and consult_date > treat_comp) and not otv else 'null',
							},
							{
							'name': "OTV or Nurse's note is selected",
							'parent': 'OTV section is initialized',
							'level': 'green' if (not qol or qol and consult_date > treat_comp) and otv else 'null',
							'condition': 'Yes',
							'children': [{
								'name': 'Fail', 
								'parent': "OTV or Nurse's note is selected",
								'level': 'green' if (not qol or qol and consult_date > treat_comp) and otv and not otv_note else 'null',
								'condition': 'No',
								'result': 'red' if (not qol or qol and consult_date > treat_comp) and otv and not otv_note else 'null',
								},
								{
								'name': 'LCSS, FACT, or EORTC QoL AND score \n is in any selected notes', 
								'parent': "OTV or Nurse's note is selected",
								'level': 'green' if (not qol or qol and consult_date > treat_comp) and otv and otv_note else 'null',
								'condition': 'Yes',
								'children': [{
									'name': 'Fail',
									'parent': 'LCSS, FACT, or EORTC QoL AND score is in any selected notes',
									'level': 'green' if (not qol or qol and consult_date > treat_comp) and otv and otv_note and not notes else 'null',
									'condition': 'No', 
									'result': 'red' if (not qol or qol and consult_date > treat_comp) and otv and otv_note and not notes else 'null',
									},
									{
									'name': 'Pass',
									'parent': 'LCSS, FACT, or EORTC QoL AND score is in any selected notes',
									'level': 'green' if (not qol or qol and consult_date > treat_comp) and otv and otv_note and notes else 'null',
									'condition': 'Yes', 
									'result': 'green' if (not qol or qol and consult_date > treat_comp) and otv and otv_note and notes else 'null',
									}]
								}]
							}]
						},
						{
						'name': 'Date is prior to treatment completion', 
						'parent': 'Consult, addendum, or toher is selected for QoL in consult section',
						'level': 'green' if qol else 'null', 
						'condition': 'Yes', 
						'children': [{
							'name': 'OTV section is initialized', 
							'parent': 'Date is prior to treatment completion', 
							'level': 'green' if qol and consult_date > treat_comp else 'null', 
							'condition': 'No'
							},
							{
							'name': 'LCSS, FACT, or EORTC QoL AND score is in any selected notes', 
							'parent': 'Date is prior to treatment completion', 
							'level': 'green' if qol and consult_date < treat_comp else 'null', 
							'condition': 'Yes',
							'children': [{
									'name': 'Fail',
									'parent': 'LCSS, FACT, or EORTC QoL AND score is in any selected notes',
									'level': 'green' if qol and consult_date < treat_comp and not notes else 'null', 
									'condition': 'No', 
									'result': 'red' if qol and consult_date < treat_comp and not notes else 'null', 
									},
									{
									'name': 'Pass',
									'parent': 'LCSS, FACT, or EORTC QoL AND score is in any selected notes',
									'level': 'red' if qol and consult_date < treat_comp and notes else 'null', 
									'condition': 'Yes', 
									'result': 'red' if qol and consult_date < treat_comp and notes else 'null', 
									}]
							}]
						}]
			}]]

		return result

	def QualityMeasure23(self):
		patient = self.patient
		current_date = datetime(2100, 1, 1).date()
		

		try:
			is_dead = True if ('deceased' in [item['patientStatus'].lower() for item in patient['followUp']]) else False
		except:
			is_dead = False

		try:
			followup_init = len(patient['followUp']) > 0
		except:
			followup_init = False

		try:
			if len(patient['followUp']) == 0:
				death_date = current_date

			else: 

				for note in patient['followUp']:
					if 'dateOfDeath' in note:
						death_date = Measure.str_to_date(self, note['dateOfDeath'])
						break
					else:
						death_date = current_date

		except:
			death_date = current_date

		try:
			tmt_end_date = self.GetTreatmentDate()
			#rt_end_dates = []

			# for plan in patient['treatmentSummary'][0]['ebrt']:
			# 	rt_end_dates.append(Measure.str_to_date(self, plan['endDate']))

			# tmt_end_date = sorted(rt_end_dates)[-1]
		except:
			tmt_end_date = current_date

		try:
			all_comp = False
			missing_comp = False
			scp_mention = False
			scp_tx_date = False
			for note in patient['followUp']:
				if 'survivorshipCarePlan' in note:

					if tmt_end_date < Measure.str_to_date(self, note['visitDate']) < tmt_end_date + timedelta(days=90):
						scp_tx_date = True
						scp_mention = True

						if len(note['survivorshipCarePlan']) == 3:
							all_comp = True

						elif len(note['survivorshipCarePlan']) > 0:
							missing_comp = True
					else:
						scp_tx_date = False
						scp_mention = True
		except:
			all_comp = False
			scp_tx_date = False
			missing_comp = False
			scp_mention = False


		if all_comp and scp_tx_date and scp_mention:
			result = 'Pass'

		elif missing_comp and scp_tx_date and scp_mention:
			result = 'Fail'

		elif not followup_init:
			result = 'Excluded'

		elif not is_dead or scp_mention and not scp_tx_date:
			result = 'Fail'

		elif is_dead and death_date > tmt_end_date + timedelta(days=91) and death_date != current_date and not scp_mention:
			result = 'Fail'

		else:
			result = 'Excluded'

		result = [patient['caseId'], result, [{
					'name': 'SCP Mention date in follow up, addendum, other',
					'parent': 'null',
					'children': [{
						'name': 'Is the patient deceased?',
						'parent': 'SCP Mention date in follow up, addendum, other',
						'level': 'green' if not scp_mention else 'null', 
						'condition': 'No',
						'children': [{
							'name': 'Fail',
							'parent': 'Is the patient deceased?',
							'level': 'green' if not scp_mention and not is_dead else 'null',
							'condition': 'No',
							'result': 'red' if not scp_mention and not is_dead else 'null'
							},
							{
							'name': 'Is there a date of death',
							'parent': 'Is the patient deceased?',
							'level': 'green' if not scp_mention and is_dead else 'null', 
							'condition': 'Yes',
							'children': [{
								'name': 'Excluded',
								'parent': 'Is there a date of death',
								'level': 'green' if not scp_mention and death_date == current_date and is_dead else 'null',
								'condition': 'No',
								'result': 'blue' if not scp_mention and death_date == current_date and is_dead else 'null', 
								},
								{
								'name': 'Date of death is within 3 months \n of treatment completion',
								'parent': 'Is there a date of death',
								'level': 'green' if not scp_mention and death_date != current_date else 'null',
								'condition': 'Yes',
								'children': [{
									'name': 'Excluded',
									'parent': 'Date of death is within 3 months of treatment completion',
									'level': 'green' if not scp_mention and death_date != current_date and death_date <= tmt_end_date + timedelta(days=91) else 'null',
									'condition': 'Yes',
									'result': 'blue' if not scp_mention and death_date != current_date and death_date <= tmt_end_date + timedelta(days=91) else 'null'
									},
									{
									'name': 'Fail',
									'parent': 'Date of death is within 3 months of treatment completion',
									'level': 'green' if not scp_mention and death_date != current_date and death_date > tmt_end_date + timedelta(days=91) else 'null',
									'condition': 'No',
									'result': 'red' if not scp_mention and death_date != current_date and death_date > tmt_end_date + timedelta(days=91) else 'null'
									}
									]
								}
								]
							}
							]
						},
						{
						'name': 'SCP mention date is within 90 days of treatment completion',
						'parent': 'SCP Mention date in follow up, addendum, other',
						'level': 'green' if scp_mention else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Fail',
							'parent': 'SCP mention date is within 90 days of treatment completion',
							'level': 'green' if not scp_tx_date and scp_mention else 'null',
							'condition': 'No',
							'result': 'red' if not scp_tx_date and scp_mention else 'null',
							},
							{
							'name': 'Is there a SCP report date?',
							'parent': 'SCP mention date is within 90 days of treatment completion',
							'level': 'green' if scp_tx_date else 'null',
							'condition': 'Yes',
							'children': [{
								'name': 'Fail', 
								'parent': 'Is there a SCP report date?',
								'level': 'null',
								'condition': 'No',
								'result': 'null'
								},
								{
								'name': 'SCP has ALL 3 components',
								'parent': 'Is there a SCP report date?',
								'level': 'green' if scp_tx_date else 'null',
								'condition': 'Yes',
								'children': [{
									'name': 'Pass',
									'parent': 'SCP has ALL 3 components',
									'level': 'green' if all_comp and scp_tx_date else 'null',
									'condition': 'Yes',
									'result': 'green' if all_comp and scp_tx_date else 'null'
									},
									{
									'name': 'Fail',
									'parent': 'SCP has ALL 3 components',
									'level': 'green' if missing_comp and scp_tx_date else 'null',
									'condition': 'No',
									'result': 'red' if missing_comp and scp_tx_date else 'null'
									}
									]
								}
								]
							}
							]
						}]
		}]]

		return result

	def QualityMeasure24(self):
		
		patient = self.patient
		current_date = datetime(2100, 1, 1).date()
		result = None
		
		# Getting  treatment end date 
		try:
			treatment_end_date = self.GetTreatmentDate()
		except:
			treatment_end_date = current_date
		
		# Follow up note within 5 months of EOT?
		try:
			follow_up_within_5_months = False 
			for note in patient['followUp']:
				
				if treatment_end_date >= Measure.str_to_date(self, note['visitDate']) - timedelta(days=152):
					follow_up_within_5_months = True
					break 
		except: 
			follow_up_within_5_months = False
		
		# Deceased (Within 8 months of treatment end date - follow up not possible therefore pass)
		try:
			deceased = False
			for note in patient['followUp']:
				if note['patientStatus'].lower() == 'deceased':
					deceased = True if treatment_end_date >= Measure.str_to_date(self, note['dateOfDeath']) - timedelta(days=243) else False 
		except:
			deceased = False
		
		# Progression Stated 
		try:
			progression_stated = False
			
			for note in patient['followUp']: 
				if 'diseaseProgression' in note:
					if note['diseaseProgression'].lower() != 'not stated':
						progression_stated = True 
		except: 
			progression_stated = False

		# NSCLC Tree 
		if '-NSCLC' in patient['caseId']:
			if (not follow_up_within_5_months and not deceased) or (follow_up_within_5_months and not progression_stated): 
				result = "Fail"
			elif (not follow_up_within_5_months and deceased) or (follow_up_within_5_months and progression_stated): 
				result = "Pass"
			
			result = [patient['caseId'], result, [{
					'name': 'Follow up note within 5 months of EOT?',
					'parent': 'null',
					'children': [{
						'name': 'Deceased',
						'parent': 'Follow up note within 5 months of EOT?',
						'level': 'green' if not follow_up_within_5_months else 'null',
						'condition': 'No',
						'children': [{
							'name': 'Pass',
							'parent': 'Deceased',
							'level': 'green' if not follow_up_within_5_months and deceased else 'null',
							'condition': 'Yes',
							'result': 'greeen' if not follow_up_within_5_months and deceased else 'null',
							},
							{
							'name': 'Fail',
							'parent': 'Treatment end date >= Extraction Date - 8 months',
							'level': 'green' if not follow_up_within_5_months and not deceased else 'null',
							'condition': 'No',
							'result': 'red' if not follow_up_within_5_months and not deceased else 'null',
							}]
						},
						{
						'name': 'Progression Stated',
						'parent': 'Follow up note within 5 months of EOT?',
						'level': 'green' if follow_up_within_5_months else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Pass',
							'parent': 'Progression Stated',
							'level': 'green' if follow_up_within_5_months and progression_stated else 'null',
							'condition': 'Yes',
							'result': 'green' if follow_up_within_5_months and progression_stated else 'null',
							},
							{
							'name': 'Fail',
							'parent': 'Progression Stated',
							'level': 'green' if follow_up_within_5_months and not progression_stated else 'null',
							'condition': 'No',
							'result': 'red' if follow_up_within_5_months and not progression_stated else 'null',
							}]
					}]
			}]]
			return result 
		
		# SCLC Calculation 

		# PCI ?
		try:
			pci = True if 'pci' in [item for item in patient['treatmentSummary']] else False
		except: 
			pci = False 

		# PCI End Date
		try:
			pci_end = Measure.str_to_date(self, patient['treatmentSummary'][0]['pci']['endDate'])
		except:
			pci_end = current_date

		# Getting the last note 
		try:
			if 'visitDate' in patient['followUp'][-1]:
				last_note_date = Measure.str_to_date(self, patient['followUp'][-1]['visitDate']) 
			
			# Getting the second to last if the last follow up note does not have a visit date - as that means it was a deceased note 
			elif 'visitDate' in patient['followUp'][-2]:
				last_note_date = Measure.str_to_date(self, patient['followUp'][-2]['visitDate']) 

			else:
				last_note_date = current_date
		except:
			last_note_date= current_date

		# Follow up note after PCI ? 
		follow_up_after_pci = True if last_note_date > pci_end else False 

		if (not follow_up_within_5_months and deceased) or (follow_up_within_5_months and progression_stated and not pci) or \
			(follow_up_within_5_months and progression_stated and pci and follow_up_after_pci):
			result = "Pass"
		
		elif (not follow_up_within_5_months and not deceased) or (follow_up_within_5_months and not progression_stated) or \
			(follow_up_within_5_months and progression_stated and pci and not follow_up_after_pci): 
			result = "Fail"
	
		result = [patient['caseId'], result, [{
					'name': 'Follow up note within 5 months of EOT?',
					'parent': 'null',
					'children': [{
						'name': 'Deceased',
						'parent': 'Follow up note within 5 months of EOT?',
						'level': 'green' if not follow_up_within_5_months else 'null',
						'condition': 'No',
						'children': [{
							'name': 'Pass',
							'parent': 'Deceased',
							'level': 'green' if not follow_up_within_5_months and deceased else 'null',
							'condition': 'Yes',
							'result': 'green' if not follow_up_within_5_months and deceased else 'null',
							},
							{
							'name': 'Fail',
							'parent': 'Treatment end date >= Extraction Date - 8 months',
							'level': 'green' if not follow_up_within_5_months and not deceased else 'null',
							'condition': 'No',
							'result': 'red' if not follow_up_within_5_months and not deceased else 'null',
							}]
						},
						{
						'name': 'Progression Stated',
						'parent': 'Follow up note within 5 months of EOT?',
						'level': 'green' if follow_up_within_5_months else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Fail',
							'parent': 'Progression Stated',
							'level': 'green' if follow_up_within_5_months and not progression_stated else 'null',
							'condition': 'No',
							'result': 'red' if follow_up_within_5_months and not progression_stated else 'null',
							},
							{
							'name': 'PCI?',
							'parent': 'Progression Stated',
							'level': 'green' if follow_up_within_5_months and progression_stated else 'null',
							'condition': 'Yes',
							'children' : [{
								'name': 'Pass',
								'parent': 'Deceased',
								'level': 'green' if follow_up_within_5_months and progression_stated and not pci else 'null',
								'condition': 'No',
								'result': 'green' if follow_up_within_5_months and progression_stated and not pci else 'null',
								},
								{
								'name': 'Follow up note after PCI?',
								'parent': 'PCI',
								'level': 'green' if follow_up_within_5_months and progression_stated and pci else 'null',
								'condition': 'Yes',
								'children': [{
									'name': 'Fail',
									'parent': 'Follow up note after PCI?',
									'level': 'green' if follow_up_within_5_months and progression_stated and pci and not follow_up_after_pci else 'null',
									'condition': 'No',
									'result': 'red' if follow_up_within_5_months and progression_stated and pci and not follow_up_after_pci else'null',
									},
									{
									'name': 'Pass',
									'parent': 'Follow up note after PCI?',
									'level': 'green' if follow_up_within_5_months and progression_stated and pci and follow_up_after_pci else 'null',
									'condition': 'Yes',
									'result': 'green' if follow_up_within_5_months and progression_stated and pci and follow_up_after_pci else'null',
								}]
								
							}]
						}]
					}]
			}]]
			

		return result
		

	def TotalNumberOfNotes(self):
		patient = self.patient

		total_notes = len(patient['otv']) + len(patient['followUp'])

		return [patient['caseId'], str(total_notes)]


	def NumberOfNotesWithToxicityInitialized(self):
		patient = self.patient
		
		try:
			follow_up_tx_tot = 0
			if 'followUp' in patient: 
				for item in patient['followUp']:
					if 'toxicity' in item:
						if len(item['toxicity']) > 0:
							follow_up_tx_tot += 1
		except:
			follow_up_tx_tot = 0

		try:
			otv_tx_tot = 0
			if 'otv' in patient: 
				for item in patient['otv']:
					if 'toxicity' in item:
						if len(item['toxicity']) > 0:
							otv_tx_tot += 1
							
		except:
			otv_tx_tot = 0

		total_tx_notes = otv_tx_tot + follow_up_tx_tot

		result = [patient['caseId'], str(total_tx_notes)]


		return result

	def LungEsophagitisTotal(self):
		patient = self.patient

		otv_tx_es_tot = 0
		follow_up_tx_es_tot = 0

		try:
			if 'followUp' in patient: 
				for item in patient['followUp']:
					if 'toxicity' in item:
						for tox in item['toxicity']:
							if 'toxicity' in tox:
								if tox['toxicity'] == 'Esophagitis':
									follow_up_tx_es_tot += 1
									break
		except:
			follow_up_tx_es_tot = 0

		try:
			if 'otv' in patient: 
				for item in patient['otv']:
					if 'toxicity' in item:
						for tox in item['toxicity']:
							if 'toxicity' in tox:
								if tox['toxicity'] == 'Esophagitis':
									otv_tx_es_tot += 1
									break
		except:
			otv_tx_es_tot = 0

		total_notes = otv_tx_es_tot + follow_up_tx_es_tot

		result = [patient['caseId'], str(total_notes)]

		return result

	def LungEsophagitisWithGrade(self):
		patient = self.patient

		follow_up_tx_es = 0
		otv_tx_es = 0

		try:
			if 'followUp' in patient: 
				for item in patient['followUp']:
					if 'toxicity' in item:
						for tox in item['toxicity']:
							if 'toxicity' in tox:
								if tox['toxicity'] == 'Esophagitis' and tox['grade'] not in ['Not Stated', 'Grade 0']:
									follow_up_tx_es += 1
									break
		except:
			follow_up_tx_es = 0

		try:
			if 'otv' in patient: 
				for item in patient['otv']:
					if 'toxicity' in item:
						for tox in item['toxicity']:
							if 'toxicity' in tox:
								if tox['toxicity'] == 'Esophagitis' and tox['grade'] not in ['Not Stated', 'Grade 0']:
									otv_tx_es += 1
									break
		except:
			otv_tx_es = 0

		total_grades = otv_tx_es + follow_up_tx_es

		result = [patient['caseId'], str(total_grades)]

		return result

	# def QualityMeasure26E(self):
	# 	patient = self.patient
	# 	#Updated to new schmea, LungEsophagitis

	# 	follow_up_tx_es = 0
	# 	otv_tx_es = 0
	# 	otv_tx_es_tot = 0
	# 	follow_up_tx_es_tot = 0

	# 	try:
	# 		if 'followUp' in patient: 
	# 			for item in patient['followUp']:
	# 				for tox in item['toxicity']:
	# 					if tox['toxicity'] == 'Esophagitis' and tox['grade'] != 'Not Stated':
	# 						follow_up_tx_es += 1
	# 					if tox['toxicity'] == 'Esophagitis':
	# 						follow_up_tx_es_tot += 1
	# 	except:
	# 		follow_up_tx_es_tot = 0
	# 		follow_up_tx_es = 0

	# 	try:
	# 		if 'otv' in patient: 
	# 			for item in patient['otv']:
	# 				for tox in item['toxicity']:
	# 					if tox['toxicity'] == 'Esophagitis' and tox['grade'] != 'Not Stated':
	# 						otv_tx_es += 1
	# 					if tox['toxicity'] == 'Esophagitis':
	# 						otv_tx_es_tot += 1
	# 	except:
	# 		otv_tx_es_tot = 0
	# 		otv_tx_es = 0

	# 	denominator = follow_up_tx_es_tot + otv_tx_es_tot
	# 	numerator = follow_up_tx_es + otv_tx_es

	# 	try:
	# 		result = numerator / denominator
	# 	except:
	# 		result = 'No Esophagitis'

	# 	result = [patient['caseId'], result]
	# 	return result


	def LungPneumonitisTotal(self):
		patient = self.patient

		otv_tx_ps_tot = 0
		follow_up_tx_ps_tot = 0

		try:
			if 'followUp' in patient: 
				for item in patient['followUp']:
					for tox in item['toxicity']:
						if 'toxicity' in tox:
							if tox['toxicity'] == 'Pneumonitis':
								follow_up_tx_ps_tot += 1
								break
		except:	
			follow_up_tx_ps_tot = 0

		try:
			if 'otv' in patient: 
				for item in patient['otv']:
					for tox in item['toxicity']:
						if 'toxicity' in tox:
							if tox['toxicity'] == 'Pneumonitis':
								otv_tx_ps_tot += 1
								break
		except:	
			otv_tx_ps_tot = 0
	
		total_notes = follow_up_tx_ps_tot + otv_tx_ps_tot

		result = [patient['caseId'], str(total_notes)]

		return result

	def LungPneumonitisWithGrade(self):
		patient = self.patient

		follow_up_tx_ps = 0
		otv_tx_ps = 0

		try:
			if 'followUp' in patient: 
				for item in patient['followUp']:
					if 'toxicity' in item:
						for tox in item['toxicity']:
							if 'toxicity' in tox:
								if tox['toxicity'] == 'Pneumonitis' and tox['grade'] not in ['Not Stated', 'Grade 0']:
									follow_up_tx_ps += 1
									break
		except:
			follow_up_tx_ps = 0

		try:
			if 'otv' in patient: 
				for item in patient['otv']:
					if 'toxicity' in item:
						for tox in item['toxicity']:
							if 'toxicity' in tox:
								if tox['toxicity'] == 'Pneumonitis' and tox['grade'] not in ['Not Stated', 'Grade 0']:
									otv_tx_ps += 1
									break
		except:
			otv_tx_ps = 0	

		total_grades = follow_up_tx_ps + otv_tx_ps

		result = [patient['caseId'], str(total_grades)]

		return result	


	# def QualityMeasure26P(self):
	# 	patient = self.patient

	# 	follow_up_tx_ps = 0
	# 	otv_tx_ps = 0
	# 	otv_tx_ps_tot = 0
	# 	follow_up_tx_ps_tot = 0

	# 	try:
	# 		if 'followUp' in patient: 
	# 			for item in patient['followUp']:
	# 				for tox in item['toxicity']:
	# 					if tox['toxicity'] == 'Pneumonitis' and tox['grade'] != 'Not Stated':
	# 						follow_up_tx_ps += 1
	# 					if tox['toxicity'] == 'Pneumonitis':
	# 						follow_up_tx_ps_tot += 1
	# 	except:
	# 		follow_up_tx_ps_tot = 0
	# 		follow_up_tx_ps = 0

	# 	try:
	# 		if 'otv' in patient: 
	# 			for item in patient['otv']:
	# 				for tox in item['toxicity']:
	# 					if tox['toxicity'] == 'Pneumonitis' and tox['grade'] != 'Not Stated':
	# 						otv_tx_ps += 1
	# 					if tox['toxicity'] == 'Pneumonitis':
	# 						otv_tx_ps_tot += 1
	# 	except:
	# 		otv_tx_ps_tot = 0
	# 		otv_tx_ps = 0

	# 	denominator = follow_up_tx_ps_tot + otv_tx_ps_tot
	# 	numerator = follow_up_tx_ps + otv_tx_ps

	# 	try:
	# 		result = numerator / denominator
	# 	except:
	# 		result = 'No Pneumonitis'

	# 	result = [patient['caseId'], result]
	# 	return result

	def QualityMeasure27(self):
		patient = self.patient

		valid_grades = ['grade 4', 'grade 5']
		current_date = datetime(2100, 1, 1).date()
		#M&M does not exist

		try:
			otv_followup_init = True if patient['otv'] or patient['followUp'] else False
		except:
			otv_followup_init = False

		try:
			tmt_end_date = self.GetTreatmentDate()
		except:
			tmt_end_date = current_date

		try:
			grades = 0
			grades_date = 0

			for item in patient['otv']:

				if 'toxicity' in item:
					for tox in item['toxicity']:

						if 'grade' in tox:
							if tox['grade'].lower() in valid_grades:
								grades += 1

				if 'visitDate'  in item:
					if Measure.str_to_date(self, item['visitDate']) <= (tmt_end_date + timedelta(days=30)):
						for tox in item['toxicity']:

							if tox['grade'].lower() in valid_grades:
								grades_date += 1

			grades = (grades) > 0
			grades_date = (grades_date) > 0
		except:
			grades = None
			grades_date = None

		if not otv_followup_init or not grades or not grades_date:
			result = 'Excluded'
		else:
			result = 'Fail'

		result = [patient['caseId'], result, [{
					'name': 'Follow up or OTV is initalized',
					'parent': 'null',
					'children': [{
						'name': 'Excluded',
						'parent': 'Follow up or OTV is initalized',
						'level': 'green' if not otv_followup_init else 'null',
						'condition': 'No',
						'result': 'blue' if not otv_followup_init else 'null'
						},
						{
						'name': 'Any toxicity section is initalized and a grade 4-5 is selected in any note',
						'parent': 'Follow up or OTV is initalized',
						'level': 'green' if otv_followup_init else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Excluded',
							'parent': 'Any toxicity section is initalized and a grade 4-5 is selected in any note',
							'level': 'green' if otv_followup_init and not grades else 'null',
							'condition': 'No',
							'result': 'blue' if otv_followup_init and not grades else 'null',
							},
							{
							'name': 'Note date of Grade 4-5 toxicity is within 30 days of treatment completion',
							'parent': 'Any toxicity section is initalized and a grade 4-5 is selected in any note',
							'level': 'green' if otv_followup_init and grades else 'null',
							'condition': 'Yes',
							'children': [{
								'name': 'Excluded',
								'parent': 'Note date of Grade 4-5 toxicity is within 30 days of treatment completion',
								'level': 'green' if otv_followup_init and grades and not grades_date else 'null',
								'condition': 'No',
								'result': 'blue' if otv_followup_init and grades and not grades_date else 'null',
								},
								{
								'name': 'Yes is selected for "M&M"?',
								'parent': 'Note date of Grade 4-5 toxicity is within 30 days of treatment completion',
								'level': 'green' if otv_followup_init and grades and grades_date else 'null',
								'condition': 'Yes',
								'children':  [{
									'name': 'Fail',
									'parent': 'Yes is selected for "M&M"?',
									'level': 'null',
									'condition': 'No',
									'result': 'No'
									},
									{
									'name': 'Yes is selected for "Is there an M&M date"?',
									'parent': 'Yes is selected for "M&M"?',
									'level': 'null',
									'condition': 'Yes',
									'children': [{
										'name': 'Fail',
										'parent': 'Yes is selected for "Is there an M&M date"?',
										'level': 'null',
										'condition': 'No',
										'result': 'null'
										},
										{
										'name': 'M&M Date is within 30 days of note date?',
										'parent': 'Yes is selected for "Is there an M&M date"?',
										'level': 'null',
										'condition': 'Yes',
										'children': [{
											'name': 'Fail',
											'parent': 'M&M Date is within 30 days of note date?',
											'level': 'null',
											'condition': 'No',
											'result': 'null'
											},
											{
											'name': 'Pass',
											'parent': 'M&M Date is within 30 days of note date?',
											'level': 'null',
											'condition': 'Yes',
											'result': 'null'
											}
											]
										}
										]
									}
									]
								}
								]
							}
							]
						}
						]
		}]]

		return result

	fdict = {
		'QualityMeasure1' : QualityMeasure1,
		'QualityMeasure2' : QualityMeasure2,
		'QualityMeasure3' : QualityMeasure3,
		'QualityMeasure4' : QualityMeasure4,
		'QualityMeasure5' : QualityMeasure5,
		'QualityMeasure6' : QualityMeasure6,
		'QualityMeasure7' : QualityMeasure7,
		'QualityMeasure8A' : QualityMeasure8A,
		'QualityMeasure8B' : QualityMeasure8B,
		'QualityMeasure9' : QualityMeasure9,
		'QualityMeasure10' : QualityMeasure10,
		'QualityMeasure11' : QualityMeasure11,
		'QualityMeasure12' : QualityMeasure12,
		'QualityMeasure13' : QualityMeasure13,
		'QualityMeasure14' : QualityMeasure14,
		'QualityMeasure15' : QualityMeasure15,
		'QualityMeasure16' : QualityMeasure16,
		'QualityMeasure17' : QualityMeasure17,
		'QualityMeasure18' : QualityMeasure18,
		'QualityMeasure19' : QualityMeasure19,
		'QualityMeasure19_color' : QualityMeasure19_color,
		'QualityMeasure20' : QualityMeasure20,
		'QualityMeasure21A' : QualityMeasure21A,
		'QualityMeasure21B' : QualityMeasure21B,
		'QualityMeasure22' : QualityMeasure22,
		'QualityMeasure23' : QualityMeasure23,
		'QualityMeasure24' : QualityMeasure24,
		'TotalNumberOfNotes' : TotalNumberOfNotes,
		'NumberOfNotesWithToxicityInitialized' : NumberOfNotesWithToxicityInitialized,
		'LungEsophagitisTotal' : LungEsophagitisTotal,
		'LungEsophagitisWithGrade' : LungEsophagitisWithGrade,
		'LungPneumonitisTotal' : LungPneumonitisTotal,
		'LungPneumonitisWithGrade' : LungPneumonitisWithGrade,
		'QualityMeasure27' : QualityMeasure27
	}