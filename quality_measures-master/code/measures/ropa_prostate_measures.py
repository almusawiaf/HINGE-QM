import numpy as np
import re 
from pymongo import MongoClient
from datetime import date, datetime, timedelta
from collections import OrderedDict

from .measure import Measure

class ProstateMeasure(Measure):

	patient = None

	res_map = {
		0: 'Fail',
		1: 'Pass',
		2: 'Excluded'
	}

	measures = OrderedDict({
		"center_id": None,
		"center_name": None,
		"vha_id": None,
		"cancer_type" : None,
		"QualityMeasure1": None,
		"QualityMeasure2": None,
		"QualityMeasure3": None,
		"QualityMeasure4": None,
		"QualityMeasure5": None,
		"QualityMeasure6": None,
		"QualityMeasure7": None,
		"QualityMeasure8": None,
		"QualityMeasure9": None,
		"QualityMeasure10": None,
		"QualityMeasure11": None,
		"QualityMeasure12": None,
		"QualityMeasure13": None,
		"QualityMeasure14": None,
		"QualityMeasure15": None,
		"QualityMeasure15_color": None,
		"QualityMeasure16": None,
		"QualityMeasure17A": None,
		"QualityMeasure17B": None,
		"QualityMeasure18": None,
		"QualityMeasure19": None,
		"QualityMeasure23": None, 
		"QualityMeasure24": None,
		"NumberOfNotesWithToxicityInitialized" : None, 
		"TotalNumberOfNotes" : None, 
		"AcuteGUWithGrade" : None, 
		"AcuteGUTotal" : None, 
		"LateGUWithGrade" : None, 
		"LateGUTotal" : None, 
		"AcuteGIWithGrade" : None, 
		"AcuteGITotal" : None, 
		"LateGIWithGrade" : None, 
		"LateGITotal" : None
	})
	
	
	# Returns the treatment start date or treatment end date. If start date, returns the earliest start date present. If end date, returns the last end date present 
	# Parameters: dateType is of type string: either startDate or endDate 
	
	def GetTreatmentDate(self, dateType):
		
		patient = self.patient
		current_date = datetime(2100, 1, 1).date()
		dates = [] 
		
		try:
			if 'ebrt' in patient['treatmentSummary'][0]:
				for item in patient['treatmentSummary'][0]['ebrt']:
					dates.append(self.str_to_date(item['startDate']))
					dates.append(self.str_to_date(item['endDate']))
		except:
			pass

		try:
			if 'treatmentSummary' in patient:
				if 'ldr' in patient['treatmentSummary'][0]:
					for item in patient['treatmentSummary'][0]['ldr']:
						dates.append(self.str_to_date(item['implantDate']))
		except:
			pass 
		
		# try:
		# 	if 'adtInjections' in patient:
		# 		for item in patient['adtInjections']:
		# 			dates.append(self.str_to_date(item['adtInjectionDate']))
		# except:
		# 	pass 
		
		try:
			if 'diagnosis' in patient:
				dates.append(self.str_to_date(patient['diagnosis']['surgeryDate']))
		except:
			pass 
		
		try:
			dates_sorted = sorted(dates)
		except:
			dates_sorted = sorted(dates)
		try:
			tmt_end_date = dates_sorted[-1] 
			tmt_start_date = dates_sorted[0]
		
		except:
			tmt_start_date = current_date
			tmt_end_date =  current_date

		if dateType == 'startDate':
			return tmt_start_date
		
		elif dateType == 'endDate':
			return tmt_end_date
		
		else:
			return current_date
		
	def QualityMeasure1(self):

		patient = self.patient

		try:
			perf_source = True 
		except:
			perf_source = False

		possibleInstruments = set(['ecog', 'who', 'kps', 'zubrod'])
		
		try:
			instruments = []
			status = patient['consult'][0]['performanceStatus']
			instruments = [item['performanceInstrument'].lower() for item in status]

		except:
			instruments = []

		if len(possibleInstruments.intersection(instruments))> 0:
			result = 1
		else:
			result = 0

		#result = [patient['caseId'], self.self.res_map[result], len(possibleInstruments.intersection(instruments))> 0]
		result = [patient['caseId'], self.res_map[result], [{
			'name': 'Instrument and Score?',
            'parent': 'null',
            'children': [{
				"name" : "Pass",
				"parent" : "Instrument and Score?",
				"level" : "green" if result == 1 else 'null',
				"condition" : "Yes",
				"result" : 'green' if result == 1 else 'null', 
				},
                {
				"name" : "Fail",
                "parent" : "Instrument and Score?",
            	"level" : 'green' if result == 0 else 'null', 
                "condition" : "No",
                "result": 'red' if result == 0 else 'null' 
            }]     
		}]]
		return result
	
	#FIXME not producing correct results
	def QualityMeasure2(self):

		patient = self.patient

		try:                
			had_surgery = True if (patient['diagnosis']['previousSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False 

		## Staging
		try:
			TX = patient['diagnosis']['tStage']
			t_stage = TX if (TX) else -1
		except:  
			t_stage = -1 
	
		## Gleason Scores 
		try:
			primary = float(patient['diagnosis']['gleasonScore']['primaryGS'])
			primary_gs = primary if (primary >= 0) else -1
		except:  
			primary_gs = -1

		try:
			secondary = float(patient['diagnosis']['gleasonScore']['secondaryGS'])
			secondary_gs = secondary if (secondary >= 0) else -1
		except:  
			secondary_gs = -1 

		try:
			total = float(patient['diagnosis']['gleasonScore']['totalGS'])
			total_gs = total if (total >= 0.0) else -1 
		except:  
			total_gs = -1

		## Prostate-Specific Antigen 
		
		try:
			psaScore = patient['diagnosis']['psa'][0]['psaScore']
			prostate_antigen = True if psaScore > 0 else False 
		except: 
			psaScore = np.nan 
			prostate_antigen = False

		valid_risks = ['very low', 'low', 'intermediate', 'high', 'very high']
		
		try:
			risk_group = patient['diagnosis']['nccnRiskCategory'].lower()
			risk = risk_group if (risk_group) else None
		except:  
			risk = None
		
		if had_surgery:
			result = 2
		elif t_stage != -1 and risk in valid_risks and (total_gs != -1) and prostate_antigen:	
			result = 1
		else:
			result = 0
		
		#result = [patient['caseId'], self.res_map[result], had_surgery, t_stage != -1, total_gs != -1, prostate_antigen, risk in valid_risks]		
		
		result = [patient['caseId'], self.res_map[result], [{
               'name' : 'Prostate Surgery Patient?',
               'parent' : 'null',
               'children': [{
	                        'name' : 'Excluded',
	                        'parent' : 'Prostate Surgery Patient?',
	                        'level' : 'green' if had_surgery else 'null',
	                        'condition': 'Yes',
	                        'result': 'blue' if had_surgery else 'null'
	                    	},
                      		{
	                        'name' : 'T Stage in Consult or Addendum',
	                        'parent': 'Prostate Surgery Patient',
	                        "level" : 'green' if not had_surgery else 'null', 
	                        'condition' : 'No',
                          	'children':[{
								'name': 'Fail',
		                        'parent': 'T Stage in Consult or Addendum',
		                        'level': 'green' if not had_surgery and t_stage == -1 else 'null',
		                        'condition': 'No',
		                        'result': 'red' if not had_surgery and t_stage == -1 else 'null'
		                        },
                            	{
	                        	'name' : 'Gleason Score is in Consult or Addendum',
								'parent' : 'T Stage in Consult or Addendum',
                  				'level' : 'green' if not had_surgery and t_stage != -1 else 'null',
								'condition': 'Yes',
                            	'children':[{
			                        'name': 'Fail',
			                        'parent': 'Gleason Score is in Consult or Addendum',
			                        'level': 'green' if not had_surgery and t_stage != -1 and total_gs == -1 else 'null',
			                        'condition': 'No',
			                        'result': 'red' if not had_surgery and t_stage != -1 and total_gs == -1 else 'null'
			                        },
		                            {
				                    'name': 'Prostate Specific Antigen is in Consult or Addendum',
				                    'parent': 'Gleason Score is in Consult or Addendum',
				                    'level': 'green' if not had_surgery and t_stage != -1 and total_gs != -1 else 'null',
				                    'condition': 'Yes',
                                    'children':[{
										'name': 'Fail',
					                    'parent': 'Prostate Specific Antigen is in Consult or Addendum',
					                    'level': 'green' if not had_surgery and t_stage != -1 and total_gs != -1 and not prostate_antigen else 'null',
					                    'condition': 'No', 
					                    'result': 'red' if not had_surgery and t_stage != -1 and total_gs != -1 and not prostate_antigen else 'null',
			                            },
                                        {
										'name': 'Risk Group in Consult or Addendum',
										'parent': 'Prostate Specific Antigen is in Consult or Addendum',
                            			'level': 'green' if not had_surgery and t_stage != -1 and total_gs != -1 and prostate_antigen else 'null',
										'condition': 'Yes',
										'children':[{
											'name': 'Fail',
											'parent': 'Risk Group in Consult or Addendum',
											'level': 'green' if not had_surgery and t_stage != -1 and total_gs != -1 and prostate_antigen and risk not in valid_risks else 'null',
                                          	'condition': 'No',
                                          	'result': 'red' if not had_surgery and t_stage != -1 and total_gs != -1 and prostate_antigen and risk not in valid_risks else 'null',
                                          	},
                                          	{
                                          	'name': 'Pass',
                                          	'parent': 'Risk Group in Consult or Addendum',
                                          	'level': 'green' if not had_surgery and t_stage != -1 and total_gs != -1 and prostate_antigen and risk in valid_risks else 'null',
                                          	'condition': 'Yes',
                                           	'result': 'green' if not had_surgery and t_stage != -1 and total_gs != -1  and prostate_antigen and risk in valid_risks else 'null',
											}]
                                    	}]
                                	}]
                            	}]
                			}] 
          
        			}]]
		return result

	def QualityMeasure3(self):
	

		patient = self.patient

		current_date = datetime(2100, 1, 1).date()
		valid_risks = ['high', 'very high']

		try:                
			had_surgery = True if (patient['diagnosis']['previousSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False 

		try:
			risk = patient['diagnosis']['nccnRiskCategory'].lower()
		except:  
			risk = None

		try:
			bone_scan_date = self.str_to_date(patient['diagnosticImaging']['boneScanDate'])
		except: 
			bone_scan_date = current_date

		try:
			ct_scan_date = self.str_to_date(patient['diagnosticImaging']['ctDate'])
		except: 
			ct_scan_date = current_date 

		try:
			mri_scan_date = self.str_to_date(patient['diagnosticImaging']['mriDate'])
		except:  
			mri_scan_date = current_date

		try:
			tmt_start_date = self.GetTreatmentDate('startDate')
		except:
			tmt_start_date = current_date

		bone_scan_check = bone_scan_date < tmt_start_date and bone_scan_date != current_date and tmt_start_date != current_date
		
		mri_scan_check = mri_scan_date < tmt_start_date and mri_scan_date != current_date
		
		ct_scan_check = ct_scan_date < tmt_start_date and ct_scan_date != current_date and tmt_start_date != current_date

		if had_surgery or (risk not in valid_risks):
			result= 2

		elif bone_scan_check and (mri_scan_check or ct_scan_check):
			result = 1
		else:
			result = 0

		#result = [patient['caseId'], self.res_map[result], had_surgery, risk in valid_risks, bone_scan_check, mri_scan_check, ct_scan_check]
		
		result = [patient['caseId'], self.res_map[result], [{
			'name': 'Is patient prostate surgery',
			'parent': 'null',
			'children': [{
				'name': 'Excluded',
				'parent': 'Is patient prostate surgery',
	            'level': 'green' if had_surgery else 'null',
	            'condition': 'Yes',
	            'result': 'blue' if had_surgery else 'null',
	            },
                {
	            'name': 'Risk Group is High or Very High',
	            'parent': 'Is patient prostate surgery',
	            'level' : 'green' if not had_surgery else 'null',
	            'condition' : 'No',
				'children':[{
					'name': 'Exclude',
					'parent': 'Risk Group is High or Very High',
		            'level': 'green' if not had_surgery and not risk in valid_risks else 'null',
		            'condition': 'No',
		            'result': 'blue' if not had_surgery and not risk in valid_risks else 'null'
		            },
                    {
	                'name' : 'Bone Scan Report date before tmt start date',
					'parent' : 'Risk Group is High or Very High',
                    'level' : 'green' if not had_surgery and risk in valid_risks else 'null',
                    'condition': 'Yes',
                    'children':[{
			        	'name': 'Fail',
			            'parent': 'Bone Scan Report date before tmt start date',
			            'level': 'green' if not had_surgery and risk in valid_risks and not bone_scan_check else 'null',
			            'condition': 'No',
			            'result': 'red' if not had_surgery and risk in valid_risks and not bone_scan_check else 'null'
			            },
		                {
				        'name': 'Pelvic MRI report date is before tmt start date',
				        'parent': 'Bone Scan Report date before tmt start date',
				        'level': 'green' if not had_surgery and risk in valid_risks and bone_scan_check else 'null',
				        'condition': 'Yes',
                        'children':[{
							'name': 'Pass',
					        'parent': 'Pelvic MRI report date is before tmt start date',
					        'level': 'green' if not had_surgery and risk in valid_risks and bone_scan_check and mri_scan_check else 'null',
					        'condition': 'Yes',
					        'result': 'green' if not had_surgery and risk in valid_risks and bone_scan_check and mri_scan_check else 'null',
			                },
                            {
							'name': 'Pelvic CT Report Date is before tmt start date',
							'parent': 'Pelvic MRI report date is before tmt start date',
                            'level': 'green' if not had_surgery and risk in valid_risks and bone_scan_check and not mri_scan_check else 'null',
							'condition': 'No',
							'children':[{
                            	'name': 'Fail',
								'parent': 'Pelvic CT Report Date is before tmt start date',
								'level': 'green' if not had_surgery and risk in valid_risks and bone_scan_check and not mri_scan_check and not ct_scan_check else 'null',
                                'condition': 'No',
                                'result': 'red' if not had_surgery and risk in valid_risks and bone_scan_check and not mri_scan_check and not ct_scan_check else 'null'
                            	},
								{
                            	'name': 'Pass',
                            	'parent': 'Pelvic CT Report Date is before tmt start date',
                                'level': 'green' if not had_surgery and risk in valid_risks and bone_scan_check and not mri_scan_check and ct_scan_check else 'null',
                                'condition': 'Yes',
                                'result': 'green' if not had_surgery and risk in valid_risks and bone_scan_check and not mri_scan_check and ct_scan_check else 'null',
                                }]
                            }]
                    	}]
                    }]
                }] 
          
        	}]]
		
		return result
	
	
	def QualityMeasure4(self):

		patient = self.patient

		try:                
			had_surgery=  True  if (patient['diagnosis']['previousSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False
		try:
			risk_group = patient['diagnosis']['nccnRiskCategory'].lower()
			risk = risk_group if (risk_group) else None
		except: 
			risk_group = [] 
			risk = None
		
		valid_treatment_options = set(['external beam rt', 'interstitial prostate brachytherapy', 'radical prostatectomy'])
		
		try:
		   options = patient['consult'][0]['discussedTreatmentOptions']
		   found_options = [item.lower() for item in options]
		except:
			found_options = [None]

		ipb = True if 'interstitial prostate brachytherapy' in found_options else False
		rp = True if 'radical prostatectomy'in found_options else False 
		ebrt = True if 'external beam rt' in found_options else False 

		if had_surgery or (risk  != 'intermediate'):
			result = 2
		elif len(valid_treatment_options.intersection(found_options)) == 3: 
			result = 1
		else:
			result = 0
		
		#result = [patient['caseId'], self.res_map[result], had_surgery, risk  == 'intermediate', ipb, rp, ebrt]
		
		result = [patient['caseId'], self.res_map[result], [{
			'name': 'prostate surgery',
			'parent': 'null',
			'children': [{
				'name': 'Excluded',
				'parent': 'prostate surgery',
				'level': 'green' if had_surgery else 'null',
				'condition': 'Yes',
				'result': 'blue' if had_surgery else 'null',
	            },
                {
	            'name': 'Intermediate Risk Group',
				'parent': 'prostate surgery',
	            'level': 'green' if not had_surgery else 'null',
	            'condition': 'No',
				'children': [{
					'name': 'Excluded',
					'parent': 'prostate surgery',
					'level': 'green' if not had_surgery and risk != 'intermediate' else 'null',
					'condition': 'No',
					'result': 'blue' if not had_surgery and risk != 'intermediate' else 'null'
					},
					{
					'name': 'Interstitial Prostate Brachytherapy mentioned in consult, adddendum, or other',
					'parent': 'Intermediate Risk Group',
					'level': 'green' if not had_surgery and risk == 'intermediate' else 'null',
					'condition': 'Yes', 
					'children': [{
						'name': 'Fail',
						'parent': 'Interstitial Prostate Brachytherapy mentioned in consult, adddendum, or other',
						'level': 'green' if not had_surgery and risk == 'intermediate' and 'interstitial prostate brachytherapy' not in found_options else 'null',
						'condition': 'No', 
						'result': 'red' if not had_surgery and risk == 'intermediate' and 'interstitial prostate brachytherapy' not in found_options else 'null'
						},
						{
						'name': 'Radical Prostatectomy is mentioned in consult, addendum, or other',
						'parent': 'Interstitial Prostate Brachytherapy mentioned in consult, adddendum, or other',
						'level': 'green' if not had_surgery and risk == 'intermediate' and 'interstitial prostate brachytherapy' in found_options else 'null',
						'condition': 'Yes', 
						'children': [{
							'name': 'Fail',
							'parent': 'Radical Prostatectomy is mentioned in consult, addendum, or other',
							'level': 'green' if not had_surgery and risk == 'intermediate' and 'interstitial prostate brachytherapy' in found_options and 'radical prostatectomy' not in found_options else 'null',
							'condition': 'No', 
							'result': 'red' if not had_surgery and risk == 'intermediate' and 'interstitial prostate brachytherapy' in found_options and 'radical prostatectomy' not in found_options else 'null'
							},
							{
							'name': 'External Beam RT is mentioned in consult, addendum, or other',
							'parent': 'Radical Prostatectomy is mentioned in consult, addendum, or other',
							'level': 'green' if not had_surgery and risk == 'intermediate' and 'interstitial prostate brachytherapy' in found_options and 'radical prostatectomy' in found_options else 'null',
							'condition': 'Yes',
							'children': [{
								'name': 'Fail',
								'parent': 'External Beam RT is mentioned in consult, addendum, or other',
								'level': 'green' if not had_surgery and risk == 'intermediate' and 'interstitial prostate brachytherapy' in found_options and 'radical prostatectomy' in found_options and not 'external beam rt' in found_options else 'null',
								'condition': 'No', 
								'result': 'red' if not had_surgery and risk == 'intermediate' and 'interstitial prostate brachytherapy' in found_options and 'radical prostatectomy' in found_options and not 'external beam rt' in found_options else 'null'
								},
								{
								'name': 'Pass',
								'parent': 'External Beam RT is mentioned in consult, addendum, or other',
								'level': 'green' if result == 1 else 'null',
								'condition': 'Yes', 
								'result': 'green' if result == 1 else 'null'
							}]
						}]
					}]
				}]
			}]
		}]]
		return result

	def QualityMeasure5(self):

		patient = self.patient

		qols_valid = set(['ipss', 'aua', 'epic-26', 'iief/shim'])

		try:
			qols_found = [item['qualityOfLifeInstrument'].lower() for item in patient['consult'][0]['qualityOfLife']]
		except: 
			qols_found = [None]
			
		if  len(qols_valid.intersection(qols_found)) > 0:
			result = 1
		else:
			result = 0
		
		#result = [patient['caseId'], self.res_map[result], len(qols_valid.intersection(qols_found)) > 0]
		result = [patient['caseId'], self.res_map[result], [{
			'name': 'Instrument and score in consult or addendum',
			'parent': 'null',
			'children':[{
				'name': 'Pass',
				'parent': 'Instrument and score in consult or addendum',
				'level': 'green' if result == 1 else 'null',
				'condition': 'Yes',
				'result': 'green' if result == 1 else 'null'
				},
				{
				'name': 'Fail',
				'parent': 'Instrument and score in consult or addendum',
				'level': 'green' if result == 0 else 'null',
				'condition': 'No',
				'result': 'red' if result == 0 else 'null'
				}]
			}]]
		return result
				
	def QualityMeasure6(self):

		patient = self.patient		

		current_date = datetime(2100, 1, 1).date()

		try:
			clinical_initialized =  True if len(patient['clinicalTrials']) > 0 else False
		except:
			clinical_initialized = False

		try:
			enrollment_selected = True if (patient['clinicalTrials'][0]['enrollmentStatus']).lower() == 'yes' else False
		except:
			enrollment_selected = False


		try:            
		   enrollment_date = self.str_to_date(patient['clinicalTrials'][0]['enrollmentDate'])
		except:
		   enrollment_date = current_date


		try:
			tmt_start_date = self.GetTreatmentDate('startDate')
		except:
			tmt_start_date = current_date
		
		try:
			enrolled_before_start = True if enrollment_date < tmt_start_date and tmt_start_date != current_date and enrollment_date != current_date else False 
		except:
			enrolled_before_start = False 
		
		if clinical_initialized and enrollment_selected and enrolled_before_start: 
			result = 1
		else:
			result = 0 

		#result = [patient['caseId'], self.res_map[result], clinical_initialized, enrollment_selected, enrollment_date, tmt_start_date]  #enrollment_date < tmt_start_date and tmt_start_date != current_date and enrollment_date!= current_date]
		
		result = [patient['caseId'], self.res_map[result], [{
			'name': 'Clinical trial initialized',
			'parent': 'null',
			'children':[{
				'name': 'Fail',
				'parent': 'Clinical trial initialized',
				'level': 'green' if not clinical_initialized else 'null',
				'condition': 'Yes',
				'result': 'red' if not clinical_initialized else 'null',
				},
				{
				'name': 'Is yes selected for enrollment',
				'parent': 'Clinical trial initialized',
				'level': 'green' if clinical_initialized else 'null',
				'condition': 'Yes',
				'children':[{
					'name': 'Fail',
					'parent': 'Is yes selected for enrollment',
					'level': 'green' if clinical_initialized and not enrollment_selected else 'null',
					'condition': 'Yes',
					'result': 'red' if clinical_initialized and not enrollment_selected else 'null'
					},
					{
					'name': 'Was the patient enrolled before treatment start',
					'parent': 'Is yes selected for enrollment',
					'level': 'green' if clinical_initialized and enrollment_selected else 'null',
					'condition': 'Yes',
					'children': [{
						'name': 'Pass',
						'parent': 'Was the patient enrolled before treatment start',
						'level': 'green' if clinical_initialized and enrollment_selected and enrolled_before_start else 'null',
						'condition': 'Yes',
						'result': 'green' if clinical_initialized and enrollment_selected and enrolled_before_start else 'null',
						},
						{
						'name': 'Fail',
						'parent': 'Was the patient enrolled before treatment start',
						'level': 'green' if clinical_initialized and enrollment_selected and not enrolled_before_start else 'null',
						'condition': 'No',
						'result': 'red' if clinical_initialized and enrollment_selected and not enrolled_before_start else 'null',	
					}]

				}]
			}]

		}]]
		
		
		return result

	def QualityMeasure7(self):

		patient = self.patient

		try:
			is_ebrt_present = True if len(patient['treatmentSummary'][0]['ebrt']) > 0 else False
		except:
			is_ebrt_present = False
	  
		try:
			mod_count = 0
			ebrt_count = 0 
			ebrt_array = patient['treatmentSummary'][0]['ebrt']
			for item in ebrt_array:
				if ('modality' in item ) and (item['modality'].lower() in ['3d', 'imrt']):
					mod_count += 1           
				if len(item) != 0:
					ebrt_count += 1 
		except:
			mod_count = 0  
			plans = []

		if not is_ebrt_present:
			result = 2
		elif mod_count != 0 and (mod_count == ebrt_count):
			result = 1
		else:
			result = 0

		#result = [patient['caseId'], self.res_map[result], is_ebrt_present, mod_count != 0 and (mod_count == ebrt_count)]

		result = [patient['caseId'], self.res_map[result], [{
			'name': 'Did the patient have EBRT',
			'parent': 'null',
			'children': [{
				'name': 'Exclude', 
				'parent': 'Did the patient have EBRT',
				'level': 'green' if not is_ebrt_present else 'null',
				'condition': 'No',
				'result': 'blue' if not is_ebrt_present else 'null'
				},
				{
				'name': 'For each EBRT plan per patient: is 3D or IMRT selected',
				'parent': 'Did the patient have EBRT',
				'level': 'green' if is_ebrt_present else 'null',
				'condition': 'Yes',
				'result': 'null',
				'children': [{
					'name': 'Fail',
					'parent': 'For each EBRT plan per patient: is 3D or IMRT selected',
					'level': 'green' if result == 0 else 'null',
					'condition': 'No',
					'result': 'red' if result == 0 else 'null'
					},
					{
					'name': 'Pass',
					'parent': 'For each EBRT plan per patient: is 3D or IMRT selected',
					'level': 'green' if result == 1 else 'null',
					'condition': 'Yes',
					'result': 'green' if result == 1 else 'null'	
				}]
			}]
		}]]
		return result

	def QualityMeasure8(self):

		patient = self.patient

		dvh_true_strucs = set(['ptv', 'bladder', 'rectum'])

		try:
			is_ebrt_present = True if(len(patient['treatmentSummary'][0]['ebrt']) > 0) else False
		except:
			is_ebrt_present = False

		try:
			is_dvh_analysis = patient['treatmentSummary'][0]['otherInformation']['dvhAnalysisPerformed'].lower()
		except:
			is_dvh_analysis = 'no'

		try:
			dvh_strucs = [item.lower() for item in patient['treatmentSummary'][0]['otherInformation']['dvhStructuresEvaluated']]
		except:
			dvh_strucs = ['nothing']

		if not is_ebrt_present:
			result =  2
		elif is_dvh_analysis == 'yes' and len(dvh_true_strucs.intersection(dvh_strucs)) == 3 :
			result = 1
		else:
			result = 0
		
		#result =  [patient['caseId'], self.res_map[result], is_ebrt_present, is_dvh_analysis == 'yes', len(dvh_true_strucs.intersection(dvh_strucs)) == 3]
		result =  [patient['caseId'], self.res_map[result], [{
			'name': 'Did the patient have EBRT',
			'parent': 'null',
			'children': [{
				'name': 'Excluded',
				'parent': 'Did the patient have EBRT',
				'level': 'green' if not is_ebrt_present else 'null',
				'condition': 'No',
				'result': 'blue' if not is_ebrt_present else 'null',
				},
				{
				'name': 'Is there a DVH analysis?',
				'parent': 'Did the patient have EBRT',
				'level': 'green' if is_ebrt_present else 'null',
				'condition': 'Yes',
				'children': [{
					'name': 'Fail',
					'parent': 'Is there a DVH analysis?',
					'level': 'green' if is_ebrt_present and is_dvh_analysis != 'yes' else 'null',
					'condition': 'No',
					'result': 'red' if is_ebrt_present and is_dvh_analysis != 'yes' else 'null',
					},
					{
					'name': 'Are all items selected in Structures Evaluated',
					'parent': 'Is there a DVH analysis?',
					'level': 'green' if is_ebrt_present and is_dvh_analysis == 'yes' else 'null',
					'condition': 'Yes',
					'children':[{
						'name': 'Fail',
						'parent': 'Are all items selected in Structures Evaluated',
						'level': 'green' if is_ebrt_present and is_dvh_analysis == 'yes' and len(dvh_true_strucs.intersection(dvh_strucs)) != 3 else 'null',
						'condition': 'No',
						'result': 'red' if is_ebrt_present and is_dvh_analysis == 'yes' and len(dvh_true_strucs.intersection(dvh_strucs)) != 3 else 'null',
						},
						{
						'name': 'Pass',
						'parent': 'Are all items selected in Structures Evaluated', 
						'level': 'green' if is_ebrt_present and is_dvh_analysis == 'yes' and len(dvh_true_strucs.intersection(dvh_strucs)) == 3 else 'null',
						'condition': 'Yes',
						'result': 'green' if is_ebrt_present and is_dvh_analysis == 'yes' and len(dvh_true_strucs.intersection(dvh_strucs)) == 3 else 'null'
					}]
				}]
			}]

		}]]
		return result

	def QualityMeasure9(self):

		patient = self.patient

		current_date = datetime(2100, 1, 1).date()

		valid_risks = ['high', 'very high']
		
		try:                
			had_surgery=  True  if (patient['diagnosis']['previousSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False

		try:
			risk_group = patient['diagnosis']['nccnRiskCategory'].lower()
			risk = risk_group if (risk_group) else np.nan
		except:  
			risk = None

		try:
			adt_injection_dates = [self.str_to_date(item['adtInjectionDate'].lower()) for item in patient['adtInjections']]
			adt_injection_dates.sort()
			adt_date = adt_injection_dates[0] # Get earliest adt injection date 
		except:
			adt_injection_dates = [] 
			adt_date = current_date
		

		try:
			ebrt_total_dates = [self.str_to_date(item['startDate'].lower()) for item in patient['treatmentSummary'][0]['ebrt']]	
			ebrt_total_dates.sort()
			ebrt_date = ebrt_total_dates[0] # Get first ebrt date
		except:
			ebrt_total_dates = [current_date] 
			ebrt_date = current_date 
		


		if had_surgery or (risk not in valid_risks) :      
			result =  2
		elif (((adt_date - ebrt_date).days <= 14)) and (adt_date != current_date and ebrt_date != current_date) and len(adt_injection_dates) > 0: # If ADT injection prior to or within 2 weeks of ebrt start date 
			result = 1
		else:
			result = 0 
		
		
		
		#result = [patient['caseId'], self.res_map[result], had_surgery, risk in valid_risks, len(adt_injection_dates)  > 0, (((adt_date - ebrt_date).days <= 14) and adt_date != current_date and ebrt_date != current_date)]
		result = [patient['caseId'], self.res_map[result],[{
			'name': 'Prostate Surgery',
			'parent': 'null',
			'children': [{
				'name': 'Excluded',
				'parent': 'Prostate Surgery',
				'level': 'green' if had_surgery else 'null',
				'condition': 'Yes',
				'result': 'blue' if had_surgery else 'null', 
				},
				{
				'name': 'High or very high risk',
				'parent': 'Prostate Surgery',
				'level': 'green' if not had_surgery else 'null',
				'condition': 'No',
				'children': [{
					'name': 'Excluded',
					'parent': 'High or very high risk',
					'level': 'green' if not had_surgery and risk not in valid_risks else 'null',
					'condition': 'No',
					'result': 'blue' if not had_surgery and risk not in valid_risks else 'null'
					},
					{
					'name': 'Is ADT Injection Initialized',
					'parent': 'High or very high risk',
					'level': 'green' if not had_surgery and risk in valid_risks else 'null',
					'condition': 'Yes',
					'children':[{
						'name': 'Fail',
						'parent': 'Is ADT Injection Initialized',
						'level': 'green' if not had_surgery and risk in valid_risks and not len(adt_injection_dates) > 0 else 'null',
						'condition': 'No',
						'result': 'red' if not had_surgery and risk in valid_risks and not len(adt_injection_dates) > 0 else 'null',
						},
						{
						'name': 'An injection date is: prior to or within 2 weeks of RT start',
						'parent': 'Is ADT Injection Initialized',
						'level': 'green' if not had_surgery and risk in valid_risks and len(adt_injection_dates) > 0 else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Fail',
							'parent': 'An injection date is: prior to or within 2 weeks of RT start',
							'level': 'green' if not had_surgery and risk in valid_risks and len(adt_injection_dates) > 0 and result == 0 else 'null',
							'condition': 'No',
							'result': 'red' if not had_surgery and risk in valid_risks and len(adt_injection_dates) > 0 and result == 0 else 'null'
							},
							{
							'name': 'Pass',
							'parent': 'An injection date is: prior to or within 2 weeks of RT start',
							'level': 'green' if result == 1 else 'null',
							'condition': 'Yes',
							'result': 'green' if result == 1 else 'null'
						}]
					}]
				}]
				
			}]
		}]]
		
		return result

	def QualityMeasure10(self):

		patient = self.patient

		current_date = datetime(2100, 1, 1).date()

		valid_risks = ['intermediate']

		try:                
			had_surgery = True if (patient['diagnosis']['previousSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False

		try:
			risk_group = patient['diagnosis']['nccnRiskCategory'].lower()
			risk = risk_group if (risk_group) else np.nan
		except:  
			risk = None

		try:
			adt_injection_dates = [self.str_to_date(item['adtInjectionDate'].lower()) for item in patient['adtInjections']]
			adt_injection_dates.sort()
			adt_date = adt_injection_dates[0] # Get earliest adt injection date 
		except:
			adt_injection_dates = [] 
			adt_date = current_date
		

		try:
			ebrt_total_dates = [self.str_to_date(item['startDate'].lower()) for item in patient['treatmentSummary'][0]['ebrt']]	
			ebrt_total_dates.sort()
			ebrt_date = ebrt_total_dates[0] # Get last ebrt date 
		except:
			ebrt_total_dates = [current_date] 
			ebrt_date = current_date 


		if had_surgery or (risk not in valid_risks) :      
			result =  2
		elif ((adt_date - ebrt_date).days <= 14) and (adt_date != current_date and ebrt_date != current_date) and len(adt_injection_dates) > 0: # If ADT injection prior to or within 2 weeks of ebrt start date 
			result = 1
		else:
			result = 0 
		
		#result = [patient['caseId'], self.res_map[result], had_surgery, risk in valid_risks, len(adt_injection_dates) > 0, (adt_date - ebrt_date).days <= 14 and adt_date != current_date and ebrt_date != current_date]

		result = [patient['caseId'], self.res_map[result], [{
			'name': 'Prostate Surgery',
			'parent': 'null',
			'children': [{
				'name': 'Excluded',
				'parent': 'Prostate Surgery',
				'level': 'green' if had_surgery else 'null',
				'condition': 'Yes',
				'result': 'blue' if had_surgery else 'null', 
				},
				{
				'name': 'intermediate risk',
				'parent': 'Prostate Surgery',
				'level': 'green' if not had_surgery else 'null',
				'condition': 'No',
				'children': [{
					'name': 'Excluded',
					'parent': 'intermediate risk',
					'level': 'green' if not had_surgery and risk not in valid_risks else 'null',
					'condition': 'No',
					'result': 'blue' if not had_surgery and risk not in valid_risks else 'null'
					},
					{
					'name': 'Is ADT Injection Initialized',
					'parent': 'intermediate risk',
					'level': 'green' if not had_surgery and risk in valid_risks else 'null',
					'condition': 'Yes',
					'children':[{
						'name': 'Fail',
						'parent': 'Is ADT Injection Initialized',
						'level': 'green' if not had_surgery and risk in valid_risks and not len(adt_injection_dates) > 0 else 'null',
						'condition': 'No',
						'result': 'red' if not had_surgery and risk in valid_risks and not len(adt_injection_dates) > 0 else 'null',
						},
						{
						'name': 'An injection date is: prior to or within 2 weeks of RT start',
						'parent': 'Is ADT Injection Initialized',
						'level': 'green' if not had_surgery and risk in valid_risks and len(adt_injection_dates) > 0 else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Fail',
							'parent': 'An injection date is: prior to or within 2 weeks of RT start',
							'level': 'green' if not had_surgery and risk in valid_risks and len(adt_injection_dates) > 0 and result == 0 else 'null',
							'condition': 'No',
							'result': 'red' if not had_surgery and risk in valid_risks and len(adt_injection_dates) > 0 and result == 0 else 'null'
							},
							{
							'name': 'Pass',
							'parent': 'An injection date is: prior to or within 2 weeks of RT start',
							'level': 'green' if result == 1 else 'null',
							'condition': 'Yes',
							'result': 'green' if result == 1 else 'null'
						}]
					}]
				}]
				
			}]
		}]]
		
		return result

	def QualityMeasure11(self):

		patient = self.patient

		#otherInformation

		try:                
			had_surgery = True if (patient['diagnosis']['previousSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False

		try:
			had_ebrt = True if (len(patient['treatmentSummary'][0]['ebrt']) > 0) else  False                  
		except:
			had_ebrt = False

		try:                
			had_hdr = True if (len(patient['treatmentSummary'][0]['hdr']) > 0) else False
		except:
			had_hdr = False 
			
		try:                
			had_ldr = True if (len(patient['treatmentSummary'][0]['ldr']) > 0) else False
		except:
			had_ldr = False

		try:
			none_stated = True if (patient['treatmentSummary'][0]['otherInformation']['dailyTargetLocalization'].lower() == 'none stated') else False 
		except:
			none_stated = False 
		
		if had_surgery or (not (had_ebrt and (not had_ldr and not had_hdr))):
			result = 2
		elif not none_stated: 
			result = 1
		else:
			result = 0    
		  
		#result = [patient['caseId', result, had_surgery, had_surgery or (not (had_ebrt and (not had_ldr and not had_hdr))), none_stated]
		result =  [patient['caseId'], self.res_map[result], [{
					'name': 'Is the patient a surgery patient?', 
					'parent': 'null', 
					'children': [{
						'name': 'Excluded', 
						'parent': 'Is the patient a surgery patient?', 
						'level': 'green' if had_surgery else 'null', 
						'condition': 'Yes', 
						'result': 'blue' if had_surgery else 'null'
						},
						{
						'name': 'Did the patient recieve EBRT and no LDR or HDR?', 
						'parent': 'Is the patient a surgery patient?', 
						'level': 'green' if not had_surgery else 'null', 
						'condition': 'No',
						'children': [{
							'name': 'Excluded', 
							'parent': 'Did the patient recieve EBRT and no LDR or HDR?',
							'level': 'green' if not had_surgery and not (had_ebrt and not (had_ldr or had_hdr)) else 'null', 
							'condition': 'No', 
							'result': 'blue' if not had_surgery and (had_hdr or had_ldr) or not had_surgery and not had_ebrt and not had_ldr and not had_ebrt else 'null',
							},
							{
							'name': 'Is None Stated selected?',
							'parent': 'did the patient recieve EBRT and no LDR or HDR?', 
							'level': 'green' if not had_surgery and had_ebrt and not (had_ldr or had_hdr) else 'null', 
							'condition': 'Yes', 
							'children': [{
								'name': 'Pass', 
								'parent': 'Is None Stated selected?', 
								'level': 'green' if not had_surgery and had_ebrt and not (had_ldr or had_hdr) and not none_stated else 'null', 
								'condition': 'No', 
								'result': 'green' if not had_surgery and had_ebrt and not (had_ldr or had_hdr) and not none_stated else 'null', 
								},
								{
								'name': 'Fail', 
								'parent': 'Is None Stated selected?', 
								'level': 'green' if not had_surgery and had_ebrt and not (had_ldr or had_hdr) and none_stated else 'null', 
								'condition': 'Yes', 
								'result': 'red' if not had_surgery and had_ebrt and not (had_ldr or had_hdr) and none_stated else 'null', 
								}]
							}]
						}]
		}]]

		return result

	def QualityMeasure12(self):

		patient = self.patient

		valid_risks = ['high', 'very high']

		try:
			had_ebrt = True if (len(patient['treatmentSummary'][0]['ebrt']) > 0) else  False                  
		except:
			had_ebrt = False

		try:                
			had_surgery = True if (patient['diagnosis']['previousSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False
		
		try:
			risk_group = patient['diagnosis']['nccnRiskCategory'].lower()
			risk = risk_group if (risk_group) else np.nan
		except:  
			risk = None
			
		try:
			ebrt_all_cycles = [item['wholePelvis'].lower() for item in patient['treatmentSummary'][0]['ebrt']]	 
		except:
			ebrt_all_cycles = []
			   

		if not had_ebrt or risk not in valid_risks or had_surgery:
			result = 2
		elif (risk in valid_risks) and ('yes' in ebrt_all_cycles):
			result = 1
		else:
			result = 0

		result = [patient['caseId'], self.res_map[result], [{
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
						'name': 'Did the patient have prostate surgery?', 
						'parent': 'Did the patient have EBRT?', 
						'level': 'green' if had_ebrt else 'null', 
						'condition': 'Yes', 
						'children': [{
							'name': 'Excluded', 
							'parent': 'Did the patient have prostate surgery?', 
							'level': 'green' if had_ebrt and had_surgery else 'null', 
							'condition': 'Yes', 
							'result': 'blue' if had_ebrt and had_surgery else 'null', 
							},
							{
							'name': 'Is High or Very High risk selected?', 
							'parent': 'Did the patient have prostate surgery', 
							'level': 'green' if had_ebrt and not had_surgery else 'null', 
							'condition': 'No', 
							'children': [{
								'name': 'Excluded',
								'parent': 'Is High or Very High risk selected?',
								'level': 'green' if had_ebrt and not had_surgery and risk not in valid_risks else 'null', 
								'condition': 'No', 
								'result': 'blue' if had_ebrt and not had_surgery and risk not in valid_risks else 'null', 
								},
								{
								'name': 'Is whole pelvis a Yes for any of the RT treatment cycles?',
								'parent': 'Is High or Very High risk selected?',
								'level': 'green' if result == 1 or result == 0 else 'null', 
								'condition': 'Yes', 
								'children': [{
									'name': 'Pass', 
									'parent': 'Is whole pelvis a Yes for any of the RT treatment cycles?',
									'level': 'green' if result == 1 else 'null', 
									'condition': 'Yes', 
									'result': 'green' if result == 1 else 'null'
									},
									{
									'name': 'Fail', 
									'parent': 'Is whole pelvis a Yes for any of the RT treatment cycles?',
									'level': 'green' if result == 0 else 'null', 
									'condition': 'No', 
									'result': 'red' if result == 0 else 'null'
									}]
								}]
							}]
						}]
		}]]
		
		return result

	def QualityMeasure13(self):

		patient = self.patient
		
		try:
			had_ebrt = True if (len(patient['treatmentSummary'][0]['ebrt']) > 0) else  False                  
		except:
			had_ebrt = False
		
		try:
			electromagnetic_selected = True if (patient['treatmentSummary'][0]['otherInformation']['dailyTargetLocalization'].lower() == 'electromagnetic transponders') else False 
		except:
			electromagnetic_selected = False 

		try:
			none_selected = True if patient['treatmentSummary'][0]['otherInformation']['immbolizationMethods'].lower() == 'none' else False 
		except: 
			none_selected = False 

		try:    
			sim_note = True if patient['treatmentSummary'][0]['otherInformation']['isSimNote'].lower() == 'yes' else False 
		except:
			sim_note = False 
		
		

		if  not had_ebrt or electromagnetic_selected:
			result =  2
		elif sim_note and not none_selected: 
			result = 1
		else:
			result = 0

		
		
		result = [patient['caseId'], self.res_map[result], [{
					'name': 'Did the patient receive EBRT?', 
					'parent': 'null', 
					'children': [{
						'name': 'Excluded', 
						'parent': 'Did the patient receive EBRT?', 
						'level': 'green' if not had_ebrt else 'null', 
						'condition': 'No', 
						'result': 'blue' if not had_ebrt else 'null', 
						},
						{
						'name': 'Is Electromagnetic Transponders selected for target localization?', 
						'parent': 'Did the patient receive EBRT?', 
						'level': 'green' if had_ebrt else 'null', 
						'condition': 'Yes', 
						'children': [{
							'name': 'Excluded', 
							'parent': 'Is Electromagnetic Transponders selected for target localization?', 
							'level': 'green' if had_ebrt and electromagnetic_selected else 'null', 
							'condition': 'Yes', 
							'result': 'blue' if had_ebrt and electromagnetic_selected else 'null'
							},
							{
							'name': 'Is None selected?', 
							'parent': 'Is Electromagnetic Transponders selected for target localization?', 
							'level': 'green' if result != 2 else 'null', 
							'condition': 'No', 
							'children': [{
								'name': 'Fail', 
								'parent': 'Is None selected?', 
								'level': 'green' if result == 0 and none_selected else 'null', 
								'condition': 'Yes', 
								'result': 'red' if result == 0 and none_selected else 'null', 
								},
								{
								'name': 'Is In SIM Note or Site Setup? a Yes?', 
								'parent': 'Is None selected?', 
								'level': 'green' if result != 2 and not none_selected else 'null', 
								'condition': 'No', 
								'children': [{
									'name': 'Pass', 
									'parent': 'Is In SIM Note or Site Setup? a Yes?', 
									'level': 'green' if not none_selected and result == 1 else 'null', 
									'condition': 'Yes', 
									'result': 'green' if not none_selected and result == 1 else 'null'
									},
									{
									'name': 'Fail', 
									'parent': 'Is In SIM Note or Site Setup? a Yes?', 
									'level': 'green' if not none_selected and result == 0 else 'null', 
									'condition': 'No', 
									'result': 'red' if not none_selected and result == 0 else 'null'
									}]
								}]
							}]
						}]
		}]]
		
		return result

	def QualityMeasure14(self):
		
		patient = self.patient

		# Level 1 EBRT HDR and LDR 
		try:
			had_ebrt = True if (len(patient['treatmentSummary'][0]['ebrt']) > 0) else  False                  
		except:
			had_ebrt = False

		try:                
			had_hdr = True if len(patient['treatmentSummary'][0]['hdr']) > 0 else False
		except:
			had_hdr = False 
			
		try:                
			had_ldr = True if len(patient['treatmentSummary'][0]['ldr']) > 0 else False
		except:
			had_ldr = False
		
		# Level 2 SBRT
		try:
			count = 0
			for item in patient['treatmentSummary'][0]['ebrt']:
				if item['modality'].lower() == 'sbrt': 
					count += 1
			sbrt_selected = True if count > 0 else False 
		except:
			sbrt_selected = False 
		
		# Level 3 Clinical Trial 
		try:
			clinical_trial = False
			for item in patient['clinicalTrials']: 
				if item['enrollmentStatus'].lower() == 'yes':
					clinical_trial = True 
					break 
		except:
			clinical_trial = False 
		
		# Level 4 Surgery
		try:                
			had_surgery = True if (patient['diagnosis']['previousSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False
		
		
		# Level 5 Recurrent Disease 
		try:
			recurrent_disease = True if (patient['diagnosis']['recurrentDisease'].lower() == 'yes') else False 
		except: 
			recurrent_disease = False 

		# Level 6 Dose Per Fraction 
		try:	
			count = 0
			dose_per_fracture = False 
			num_ebrt = len(patient['treatmentSummary'][0]['ebrt'])
			#print(num_ebrt)
			for item in patient['treatmentSummary'][0]['ebrt']: 
				if (float((item['prescriptionDose']) * 100) / item['numberOfPlannedFractions']) > 200: 
					count += 1
			if num_ebrt == count and count != 0:
				dose_per_fracture = True
		except: 
			dose_per_fracture = False 	

		
		# Level 7 Total Dose in EBRT and EBRT Plan Dose 180-200
		try:
			individual_dosages = [] 
			individual_fractures = [] 
			dosage_total = 0
			individual_between = True 

			for item in patient['treatmentSummary'][0]['ebrt']: 
				dosage_total += (float(item['prescriptionDose']) * 100)
				individual_dosages.append(float((item['prescriptionDose']) * 100))
				individual_fractures.append(float((item['numberOfPlannedFractions'])))
				
			if (len(individual_dosages) == len(individual_fractures)) and len(individual_dosages) != 0:
				for i in range(len(individual_dosages)): 
					item = round(float(individual_dosages[i] / individual_fractures[i]))
					if item > 200 or item < 180: 
						individual_between = False
						break 
			else:
				individual_between = False 						
			
			if (dosage_total >= 7400.0) and individual_between:
				is_cumulative = True
			else:
				is_cumulative = False 

		except: 
			dosage_total = 0 
			individual_dosages = [] 
			individual_fractures = [] 
			individual_between = False 
			is_cumulative = False
		
		if (not (had_ebrt and (not had_ldr and not had_hdr))) or sbrt_selected or clinical_trial or had_surgery or recurrent_disease or dose_per_fracture: 
			result = 2

		elif is_cumulative: 
			result = 1
		else:
			result = 0

		#result = [patient['caseId'], self.res_map[result], not (had_ebrt and (not had_hdr and  not had_ldr)), sbrt_selected, clinical_trial, had_surgery, recurrent_disease, dose_per_fracture, is_cumulative]
		result = [patient['caseId'], self.res_map[result], [{
					'name': 'Did the patient receive EBRT and no LDR or HDR treatments?', 
					'parent': 'null', 
					'children': [{
						'name': 'Excluded', 
						'parent': 'Did the patient receive EBRT and no LDR or HDR treatments?', 
						'level': 'green' if (not (had_ebrt and (not had_ldr and not had_hdr))) else 'null', 
						'condition': 'No', 
						'result': 'blue' if (not (had_ebrt and (not had_hdr and not had_ldr))) else 'null'
						},
						{
						'name': 'Is SBRT selected?', 
						'parent': 'Did the patient receive EBRT and no LDR or HDR treatments?', 
						'level': 'green' if (had_ebrt and (not had_ldr and not had_hdr)) else 'null', 
						'condition': 'Yes', 
						'children': [{
							'name': 'Excluded', 
							'parent': 'Is SBRT selected?', 
							'level': 'green' if (had_ebrt and (not had_ldr and not had_hdr)) and sbrt_selected else 'null', 
							'condition': 'Yes', 
							'result': 'blue' if (had_ebrt and (not had_ldr and not had_hdr)) and sbrt_selected else 'null'					 
							},
							{
							'name': 'On a clinical trial', 
							'parent': 'Is SBRT selected?', 
							'level':  'green' if (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected else 'null', 
							'condition': 'No', 
							'children': [{
								'name': 'Excluded', 
								'parent': 'On a clinical trial', 
								'level': 'green' if (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and clinical_trial else 'null',
								'condition': 'Yes', 
								'result': 'blue' if (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and clinical_trial else 'null'
								},
								{
								'name': 'Did the patient have prostate surgery?', 
								'parent': 'On a clinical trial', 
								'level': 'green' if (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and not clinical_trial else 'null', 
								'condition': 'No', 
								'children': [{
									'name': 'Excluded', 
									'parent': 'Did the patient have prostate surgery?', 
									'level': 'green' if (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and not clinical_trial and had_surgery else 'null',
									'condition': 'Yes', 
									'result': 'blue' if (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and not clinical_trial and had_surgery else 'null',
									},
									{
									'name': 'Is recurrent disease a Yes?', 
									'parent': 'Did the patient have prostate surgery?', 
									'level': 'green' if (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and not clinical_trial and not had_surgery else 'null',
									'condition': 'No', 
									'children': [{
										'name': 'Excluded', 
										'parent': 'Is recurrent disease a Yes?', 
										'level': 'green' if (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and not clinical_trial and not had_surgery \
													and recurrent_disease else 'null',
										'condition': 'Yes', 
										'result': 'blue' if (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and not clinical_trial and not had_surgery \
													and recurrent_disease else 'null',
										},
										{
										'name': 'Do all plans have a dose per fraction > 200 cGy/ Fraction', 
										'parent': 'Is recurrent disease a Yes?', 
										'level': 'green' if (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and not clinical_trial and not had_surgery \
													and not recurrent_disease else 'null',
										'condition': 'No', 
										'children': [{
											'name': 'Excluded', 
											'parent': 'Do all plans have a dose per fraction > 200 cGy/ Fraction', 
											'level': 'green' if (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and not clinical_trial and not had_surgery \
													and not recurrent_disease and dose_per_fracture else 'null',
											'condition': 'Yes', 
											'result': 'blue' if (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and not clinical_trial and not had_surgery \
													and not recurrent_disease and dose_per_fracture else 'null',
											},
											{
											'name': 'Is 7400 cGy <= Cumulative EBRT Dose and each EBRT plan has a Dose/ Fraction at 180-200 cGY/ Fraction', 
											'parent': 'Do all plans have a dose per fraction > 200 cGy/ Fraction', 
											'level': 'green' if result != 2 else 'null', 
											'condition': 'No', 
											'children': [{
												'name': 'Pass', 
												'parent': 'Is 7400 cGy <= Cumulative EBRT Dose and each EBRT plan has a Dose/ Fraction at 180-200 cGY/ Fraction', 
												'level': 'green' if result == 1 else 'null', 
												'condition': 'Yes', 
												'result': 'green' if result == 1 else 'null', 
												},
												{
												'name': 'Fail', 
												'parent': 'Is 7400 cGy <= Cumulative EBRT Dose and each EBRT plan has a Dose/ Fraction at 180-200 cGY/ Fraction', 
												'level': 'green' if result == 0 else 'null', 
												'condition': 'No', 
												'result': 'red' if result == 0 else 'null', 
												}]
											}]
										}]
									}]
								}]
							}]
						}]
		}]]

		return result
		
	def QualityMeasure15(self):

		patient = self.patient

		try:                
			had_surgery = True if (patient['diagnosis']['previousSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False               

		try:
			had_ebrt = True if (len(patient['treatmentSummary'][0]['ebrt']) > 0) else  False                  
		except:
			had_ebrt = False

		try:                
			had_hdr = True if len(patient['treatmentSummary'][0]['hdr']) > 0 else False
		except:
			had_hdr = False 
			
		try:                
			had_ldr = True if len(patient['treatmentSummary'][0]['ldr']) > 0 else False
		except:
			had_ldr = False
		
		try:
			sbrt_selected = False 
			for item in patient['treatmentSummary'][0]['ebrt']:
				if item['modality'].lower() == 'sbrt': 
					sbrt_selected = True
					break 
		except:
			sbrt_selected = False 

		try:
			clinical_trial = False
			for item in patient['clinicalTrials']: 
				if item['enrollmentStatus'].lower() == 'yes':
					clinical_trial = True 
					break 
		except:
			clinical_trial = False  
	 
		try:	
			count = 0
			dose_per_fracture = False 
			num_ebrt = len(patient['treatmentSummary'][0]['ebrt'])
			for item in patient['treatmentSummary'][0]['ebrt']: 
				if (float((item['prescriptionDose']) * 100) / item['numberOfPlannedFractions']) > 200: 
					count += 1
			if num_ebrt == count and count != 0:
				dose_per_fracture = True
		except: 
			dose_per_fracture = False 		

		
		try:
			individual_dosages = [] 
			individual_fractures = [] 
			dosage_total = 0
			individual_between = True 

			for item in patient['treatmentSummary'][0]['ebrt']: 
				dosage_total += (float(item['prescriptionDose']) * 100)
				individual_dosages.append(float((item['prescriptionDose']) * 100))
				individual_fractures.append(float((item['numberOfPlannedFractions'])))
				
			if (len(individual_dosages) == len(individual_fractures)) and len(individual_dosages) != 0:
				for i in range(len(individual_dosages)): 
					item = round(float(individual_dosages[i] / individual_fractures[i]))
					if item > 200 or item < 180: 
						individual_between = False
						break 
			else:
				individual_between = False 
				dosage_total = 0 
		except: 
			individual_between = False 
			dosage_total = 0

		if not had_surgery or (not (had_ebrt & (not had_hdr and not had_ldr))) or sbrt_selected or clinical_trial or dose_per_fracture:
			result = 2
		elif 6000 <= dosage_total <= 7200: 
				result = 1
		else:
				result = 0

		#result = [patient['caseId'], self.res_map[result], had_surgery, (had_ebrt & (not had_hdr and not had_ldr)), sbrt_selected, clinical_trial, dose_per_fracture, 6000 <= dosage_total <= 7200]
		result = [patient['caseId'], self.res_map[result], [{
					'name': 'Did the patient have prostate surgery?', 
					'parent': 'null', 
					'children': [{
						'name': 'Excluded', 
						'parent': 'Did the patient have prostate surgery?', 
						'level': 'green' if not had_surgery else 'null', 
						'condition': 'No', 
						'result': 'blue' if not had_surgery else 'null'
						},
						{
						'name': 'Did the patient recieve EBRT and no LDR or HDR treatments?', 
						'parent': 'Did the patient have prostate surgery?', 
						'level': 'green' if had_surgery else 'null', 
						'condition': 'Yes', 
						'children': [{
							'name': 'Excluded', 
							'parent': 'Did the patient recieve EBRT and no LDR or HDR treatments?', 
							'level': 'green' if had_surgery and (not (had_ebrt & (not had_hdr and not had_ldr))) else 'null', 
							'condition': 'No', 
							'result': 'blue' if had_surgery and (not (had_ebrt & (not had_hdr and not had_ldr))) else 'null', 
							},
							{
							'name': 'Is SBRT selected?', 
							'parent': 'Did the patient recieve EBRT and no LDR or HDR treatments?', 
							'level': 'green' if had_surgery and (had_ebrt and (not had_hdr and not had_ldr)) else 'null', 
							'condition': 'Yes', 
							'children': [{
								'name': 'Excluded', 
								'parent': 'Is SBRT selected?', 
								'level': 'green' if had_surgery and (had_ebrt and (not had_hdr and not had_ldr)) and sbrt_selected else 'null',
								'condition': 'Yes', 
								'result': 'blue' if had_surgery and (had_ebrt and (not had_hdr and not had_ldr)) and sbrt_selected else 'null'
								},
								{
								'name': 'On a clinical trial', 
								'parent': 'Is SBRT selected?', 
								'level':  'green' if had_surgery and (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected else 'null', 
								'condition': 'No', 
								'children': [{
									'name': 'Excluded', 
									'parent': 'On a clinical trial', 
									'level': 'green' if had_surgery and (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and clinical_trial else 'null',
									'condition': 'Yes', 
									'result': 'blue' if had_surgery and (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and clinical_trial else 'null'
									},
									{
									'name': 'Is the dose per fraction > 200 cGy/ Fraction',
									'parent': 'On a clinical trial', 
									'level': 'green' if had_surgery and (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and not clinical_trial else 'null', 
									'condition': 'No', 
									'children': [{
										'name': 'Excluded', 
										'parent': 'Is the dose per fraction > 200 cGy/ Fraction', 
										'level': 'green' if had_surgery and (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and not clinical_trial \
														and dose_per_fracture else 'null',
										'condition': 'Yes', 
										'result': 'blue' if had_surgery and (had_ebrt and (not had_ldr and not had_hdr)) and not sbrt_selected and not clinical_trial \
														and dose_per_fracture else 'null',
										},
										{
										'name': 'Do all plans have a dose per fraction of 180-200 cGy/ Fraction?', 
										'parent': 'Is the dose per fraction > 200 cGy/ Fraction', 
										'level': 'green' if result != 2 else 'null', 
										'conditon': 'No', 
										'children': [{
											'name': 'Fail', 
											'parent': 'Do all plans have a dose per fraction of 180-200 cGy/ Fraction?', 
											'level': 'green' if result == 0 and not individual_between else 'null', 
											'condition': 'No', 
											'result': 'red' if result == 0 and not individual_between else 'null', 
											},
											{
											'name': '6000 <= Dose <= 7200', 
											'parent': 'Do all plans have a dose per fraction of 180-200 cGy/ Fraction?', 
											'level': 'green' if result != 2 and individual_between else 'null', 
											'condition': 'Yes', 
											'children': [{
												'name': 'Pass', 
												'parent': '6000 <= Dose <= 7200', 
												'level': 'green' if result == 1 else 'null', 
												'condition': 'Yes', 
												'result': 'green' if result == 1 else 'null'
												},
												{
												'name': 'Fail', 
												'parent': '6000 <= Dose <= 7200', 
												'level': 'green' if result == 0 and individual_between else 'null', 
												'condition': 'No', 
												'result': 'red' if result == 0 and individual_between else 'null'
												}]
											}]
										}]
									}]
								}]
							}]
						}]
		}]]

		return result

	def QualityMeasure15_color(self):

		patient = self.patient
			   
		try:                
			had_surgery=  True  if (patient['patientInformation']['surgery'].lower() == 'yes') else False
		except:
			had_surgery = False                 

		try:
			had_ebrt = True if (int(patient['prostateExternalBeamPlan'][0]['fractions']) > 0)  else  False                  
		except:
			had_ebrt = False

		try:                
			had_hdr = True  if patient['prostateHdrPlan'] else False
		except:
			had_hdr = False 
			
		try:                
			had_ldr = True if (patient['prostateLdrPlan']) else False
		except:
			had_ldr = False
		
		try:
			plans = patient['prostateExternalBeamPlan']
			for item in plans:
				sbrt_val = item['modality'].lower()
				if ('modality' in item ) and (sbrt_val == 'sbrt'):
					sbrt = True
					break
				else:
					sbrt = False
		except:  
			sbrt = False

		try:                
			cl_trials = True if (patient['clinicalTrial']['clinicalTrialEnrollment'].lower() == 'yes') else False
		except:
			cl_trials = False  
	 
		try:
			dose_fraction_200 = 0 
			plans = patient['prostateExternalBeamPlan']
			num_plans = len(plans) if (len(plans) > 0) else 0

			for item in plans:
				dose = round(float(item['prescriptionDose']) * 100.0, 0)
				fractions = (item['fractions'])
				#print('dose_fraction ', dose, fractions, round(dose/fractions, 0))
				if (dose / fractions) > 200 :
					dose_fraction_200 += 1
		except:  
			dose_fraction_200 = 0
			num_plans = 0

		

		try:
			dose_fraction_count = 0 
			plans = patient['prostateExternalBeamPlan']
			num_plans = len(plans) if (len(plans) > 0) else 0
			cumilative_plans = 0


			for item in plans:
				dose = round(float(item['prescriptionDose']) * 100.0, 0)
				fractions = int(item['fractions'])
				cumilative_plans += dose
				dose_per_fraction = dose / fractions

				if  dose_per_fraction >= 180.0 and  dose_per_fraction <= 200.0 :
					dose_fraction_count += 1
					#print(dose, fractions, dose_per_fraction, dose_per_fraction >= 180.0 and dose_per_fraction <= 200.0, cumilative_plans)
				else:
					#print(dose, fractions, dose_per_fraction, dose_per_fraction >= 180.0 and dose_per_fraction <= 200.0, cumilative_plans)
					pass
					
		except:  
			dose_fraction_count = 0
			num_plans = 0
			cumilative_plans = 0


		if (dose_fraction_count > 0 and num_plans > 0 and num_plans == dose_fraction_count and cumilative_plans >= 6000.0 and cumilative_plans <= 7400.0):
			is_cumilative = True
		else: 
			is_cumilative = False

		def get_color_code(cumilative):
			if cumilative >= 6400.0 and cumilative <= 7200.0:
				return 'Green'
			elif cumilative >= 6000.0 and cumilative <= 6400.0:
				return 'Yellow'
			elif cumilative > 7200.00:
				return 'Red'
			else:
				return 'Something Went Wrong'
			

		if (not had_surgery) | (not (had_ebrt & (not had_hdr and not had_ldr)))  |  sbrt  |  cl_trials | dose_fraction_200 > 0:
			result = 2

		elif is_cumilative:
				result = get_color_code(cumilative_plans)
		else:
				result = get_color_code(cumilative_plans)

		result =  [patient['caseId'], self.res_map[result], had_surgery, had_ebrt, had_hdr, had_ldr, sbrt, cl_trials, dose_fraction_200 > 0, is_cumilative]
		
		return result

	def QualityMeasure17A(self):

		patient = self.patient
		   
		try:                
			had_ldr = True if len(patient['treatmentSummary'][0]['ldr']) > 0 else False
		except:
			had_ldr = False
			
		try:
			for item in patient['treatmentSummary'][0]['ldr']:
				dosimetry_eval = True if item['postDosimetryPeformed'].lower() == 'yes' else False 
		except:
			dosimetry_eval = False
		
		# Items needed to be checked in eval: CT or MRI, Prostate V100 Eval, Rectum V100 Eval, Physician Review 
		try:
			post_treatment_evaluations = []
			for item in patient['treatmentSummary'][0]['ldr'][0]['postTreatmentEvaluation']:
				post_treatment_evaluations.append(item)
		except:
			post_treatment_evaluations = []
		
		try:
			all_options = set(['CT or MRI', 'Prostate V100 Eval.', 'Prostate D90 Eval.', 'Rectum V100 Eval.', 'Physician Review'])
			all_options_selected = True if len(all_options.intersection(post_treatment_evaluations)) == 5 else False 

		except:
			all_options = set(['CT or MRI', 'Prostate V100 Eval.', 'Prostate D90 Eval.', 'Rectum V100 Eval.', 'Physician Review'])
			all_options_selected = False 
		
		if not had_ldr:
			result = 2
		elif dosimetry_eval and all_options_selected:
			result = 1
		else:
			result = 0
		
		#result = [patient['caseId'], self.res_map[result], had_ldr, dosimetry_eval, all_options_selected]

		result = [patient['caseId'], self.res_map[result], [{
					'name': 'Did the patient recieve LDR treatment?', 
					'parent': 'null', 
					'children': [{
						'name': 'Excluded', 
						'parent': 'Did the patient recieve LDR treatment?',
						'level': 'green' if not had_ldr else 'null', 
						'condition': 'No', 
						'result': 'blue' if not had_ldr else 'null'
						},
						{
						'name': 'Is there a post dosimetry evaluation', 
						'parent': 'Did the patient recieve LDR treatment?',
						'level': 'green' if had_ldr else 'null', 
						'condition': 'Yes', 
						'children': [{
							'name': 'Fail', 
							'parent': 'Is there a post dosimetry evaluation', 
							'level': 'green' if had_ldr and not dosimetry_eval else 'null', 
							'condition': 'No', 
							'result': 'red' if had_ldr and not dosimetry_eval else 'null'
							},
							{
							'name': 'Are all the options in Post-Treatment Evaluation selected?', 
							'parent': 'Is there a post dosimetry evaluation', 
							'level': 'green' if had_ldr and dosimetry_eval else 'null', 
							'condition': 'Yes', 
							'children': [{
								'name': 'Pass', 
								'parent': 'Are all the options in Post-Treatment Evaluation selected?',
								'level': 'green' if result == 1 else 'null', 
								'condition': 'Yes', 
								'result': 'green' if result == 1 else 'null'
								},
								{
								'name': 'Fail', 
								'parent': 'Are all the options in Post-Treatment Evaluation selected?',
								'level': 'green' if result == 0 and dosimetry_eval else 'null', 
								'condition': 'No', 
								'result': 'red' if result == 0 and dosimetry_eval else 'null'
								}]
							}]
						}]
		}]]

		return result

	def QualityMeasure17B(self):

		patient = self.patient
		current_date = datetime(2100, 1, 1).date()

		try:                
			had_ldr = True if len(patient['treatmentSummary'][0]['ldr']) > 0 else False
		except:
			had_ldr = False

		try:
			for item in patient['treatmentSummary'][0]['ldr']:
				dosimetry_eval = True if item['postDosimetryPeformed'].lower() == 'yes' else False 
		except:
			dosimetry_eval = False

		try:
			for item in patient['treatmentSummary'][0]['ldr']:
				post_tx_dosimetry_date = self.str_to_date(item['postTreatmentEvaluationDate'])
		except:
			post_tx_dosimetry_date = current_date

		try:
			for item in patient['treatmentSummary'][0]['ldr']:
				implant_date = self.str_to_date(item['implantDate'])
		except:
			implant_date = current_date

		if not had_ldr:
			result = 2
		elif dosimetry_eval and post_tx_dosimetry_date <= (implant_date + timedelta(days=60)) and \
			  post_tx_dosimetry_date != current_date and implant_date != current_date:
			result = 1
		else:
			result = 0

		#result =  [patient['caseId'], self.res_map[result],  had_ldr, dosimetry_eval, post_tx_dosimetry_date <= (implant_date + timedelta(days=60))\
		#and post_tx_dosimetry_date != current_date and implant_date != current_date]

		result = [patient['caseId'], self.res_map[result], [{
					'name': 'Did the patient recieve LDR treatment?', 
					'parent': 'null', 
					'children': [{
						'name': 'Excluded', 
						'parent': 'Did the patient recieve LDR treatment?',
						'level': 'green' if not had_ldr else 'null', 
						'condition': 'No', 
						'result': 'blue' if not had_ldr else 'null'
						},
						{
						'name': 'Is there a post dosimetry evaluation', 
						'parent': 'Did the patient recieve LDR treatment?',
						'level': 'green' if had_ldr else 'null', 
						'condition': 'Yes', 
						'children': [{
							'name': 'Fail', 
							'parent': 'Is there a post dosimetry evaluation', 
							'level': 'green' if had_ldr and not dosimetry_eval else 'null', 
							'condition': 'No', 
							'result': 'red' if had_ldr and not dosimetry_eval else 'null'
							},
							{
							'name': 'Is the Post-Treatment Dosimetry Date <= Date of Implant + 60 Days', 
							'parent': 'Is there a post dosimetry evaluation', 
							'level': 'green' if had_ldr and dosimetry_eval else 'null', 
							'condition': 'Yes', 
							'children': [{
								'name': 'Pass', 
								'parent': 'Is the Post-Treatment Dosimetry Date <= Date of Implant + 60 Days',
								'level': 'green' if result == 1 else 'null', 
								'condition': 'Yes', 
								'result': 'green' if result == 1 else 'null'
								},
								{
								'name': 'Fail', 
								'parent': 'Is the Post-Treatment Dosimetry Date <= Date of Implant + 60 Days',
								'level': 'green' if result == 0 and dosimetry_eval else 'null', 
								'condition': 'No', 
								'result': 'red' if result == 0 and dosimetry_eval else 'null'
								}]
							}]
						}]
		}]]

		return result

	# Updated Tree - See followup_dts.pdf for reference 
	def QualityMeasure18(self):

		patient = self.patient
		current_date = datetime(2100, 1, 1).date()
		result = None

		# Getting  treatment end date 
		try:
			treatment_end_date = self.GetTreatmentDate('endDate')
		except:
			treatment_end_date = current_date
		
		# Follow up note within 8 months of end of treatment?
		try:
			follow_up_within_8_months = False 
			for note in patient['followUp']:
				if 'visitDate' in note: 
					if treatment_end_date >= self.str_to_date(note['visitDate']) - timedelta(days=243):
						follow_up_within_8_months = True
						break 
		except: 
			follow_up_within_8_months = False 

		# Deceased (Within 8 months of treatment end date - follow up not possible therefore pass)
		try:
			deceased = False
			for note in patient['followUp']:
				if note['patientStatus'].lower() == 'deceased':
					deceased = True if treatment_end_date >= self.str_to_date(note['dateOfDeath']) - timedelta(days=243) else False 
		except:
			deceased = False

		# Progression Stated 
		try:
			progression_stated = False
			possible_progressions = ['no progression', 'indeterminate', 'metastatic/distant progression', 'local/regional progression', 'biochemical failure']
			for note in patient['followUp']: 
				if 'diseaseProgression' in note:
					if note['diseaseProgression'].lower() != 'not stated':
						progression_stated = True 
		except: 
			progression_stated = False
		  	
		if (not follow_up_within_8_months and not deceased) or (follow_up_within_8_months and not progression_stated): 
			result = 0 

		elif (not follow_up_within_8_months and deceased) or (follow_up_within_8_months and progression_stated): 
			result = 1
	
		result = [patient['caseId'], self.res_map[result], [{
					'name': 'Follow up note within 8 months of EOT?',
					'parent': 'null',
					'children': [{
						'name': 'Deceased',
						'parent': 'Follow up note within 8 months of EOT?',
						'level': 'green' if not follow_up_within_8_months else 'null',
						'condition': 'No',
						'children': [{
							'name': 'Pass',
							'parent': 'Deceased',
							'level': 'green' if not follow_up_within_8_months and deceased else 'null',
							'condition': 'Yes',
							'result': 'green' if not follow_up_within_8_months and deceased else 'null',
							},
							{
							'name': 'Fail',
							'parent': 'Treatment end date >= Extraction Date - 8 months',
							'level': 'green' if not follow_up_within_8_months and not deceased else 'null',
							'condition': 'No',
							'result': 'red' if not follow_up_within_8_months and not deceased else 'null',
							}]
						},
						{
						'name': 'Progression Stated',
						'parent': 'Follow up note within 8 months of EOT?',
						'level': 'green' if follow_up_within_8_months else 'null',
						'condition': 'Yes',
						'children': [{
							'name': 'Pass',
							'parent': 'Progression Stated',
							'level': 'green' if follow_up_within_8_months and progression_stated else 'null',
							'condition': 'Yes',
							'result': 'green' if follow_up_within_8_months and progression_stated else 'null',
							},
							{
							'name': 'Fail',
							'parent': 'Progression Stated',
							'level': 'green' if follow_up_within_8_months and not progression_stated else 'null',
							'condition': 'No',
							'result': 'red' if follow_up_within_8_months and not progression_stated else 'null',
							}]
					}]
		}]]

		return result
	

	def QualityMeasure19(self):

		patient = self.patient

		try:
			followUp = True if 'followUp' in patient else False
			number_of_notes = len(patient['followUp'])

		except:
			followUp = False 	
			number_of_notes = 0
		
		try:
			loops = 0
			another_follow_up = False 
			qol_initialized = False
			for item in patient['followUp']:
				if 'qualityOfLife' in item: 
					qol_initialized = True 
				else:
					qol_initialized = False 
					break 
				
				if loops == number_of_notes: 
					another_follow_up = False 
					break 
				else:
					another_follow_up = True
		except:
			qol_initialized = False 
			another_follow_up = False 	
				
		if not followUp: 
			result = 2
		
		elif not qol_initialized: 
			result = 0
		
		else:
			result = 1 

		#result = [patient['caseId'], self.res_map[result], followUp, qol_initialized, another_follow_up] 

		result = [patient['caseId'], self.res_map[result], [{
					'name': 'Follow up note is initialized', 
					'parent': 'null', 
					'children': [{
						'name': 'Excluded', 
						'parent': 'Follow up note is initialized', 
						'level': 'green' if not followUp else 'null', 
						'condition': 'No', 
						'result': 'blue' if not followUp else 'null',
						},
						{
						'name': 'Quality of Life section is initialzed in all notes', 
						'parent': 'Follow up note is initialized', 
						'level': 'green' if followUp else 'null', 
						'condition': 'Yes', 
						'children': [{
							'name': 'Fail', 
							'parent': 'Quality of Life section is initialzed in all notes', 
							'level': 'green' if result == 0 else 'null', 
							'condition': 'No', 
							'result': 'red' if result == 0 else 'null'
							},
							{
							'name': 'Pass', 
							'parent': 'Quality of Life section is initialzed in all notes', 
							'level': 'green' if result == 1 else 'null', 
							'condition': 'Yes', 
							'result': 'green' if result == 1 else 'null'
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
						death_date = self.str_to_date(self, note['dateOfDeath'])
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

					if tmt_end_date < self.str_to_date(self, note['visitDate']) < tmt_end_date + timedelta(days=90):
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
			result = 1

		elif missing_comp and scp_tx_date and scp_mention:
			result = 0

		elif not followup_init:
			result = 2

		elif not is_dead or scp_mention and not scp_tx_date:
			result = 0

		elif is_dead and death_date > tmt_end_date + timedelta(days=91) and death_date != current_date and not scp_mention:
			result = 0

		else:
			result = 2

		result = [patient['caseId'], self.res_map[result], [{
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
								'name': 'Date of death is within 3 months \\n of treatment completion',
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
		node_three = False 

		try:
			adt_duration = True if patient['consult'][0]['adtDuration'].lower() == 'long term' else False
		except:            
			adt_duration = False

		try:
			bone_density = True if patient['diagnosticImaging']['boneDensityAssessment'].lower() == 'yes' else False
		except:
			bone_density = False

		try:
			bone_density_date = self.str_to_date(patient['diagnosticImaging']['boneDensityDate'])
		except:
			bone_density_date = current_date 
		try:
			adt_inj_dates = sorted([self.str_to_date(item['adtInjectionDate']) for item in patient['adtInjections']])
			adt_start_date = adt_inj_dates[0]
		except:
			adt_start_date = current_date 
		
		if not adt_duration:
			result = 2	
		elif bone_density and \
			bone_density_date <= adt_start_date + timedelta(days=90) and \
			bone_density_date >= adt_start_date - timedelta(days=90) and \
			bone_density_date != datetime.now().date() and \
			adt_start_date != current_date and bone_density_date != current_date:
			result = 1
			node_three = True 
		else:
			result = 0
			

		#result = [patient['caseId'], self.res_map[result], adt_duration, bone_density, node_three]

		result = [patient['caseId'], self.res_map[result], [{
					'name': 'ADT Intent is Long-term', 
					'parent': 'null', 
					'children': [{
						'name': 'Excluded', 
						'parent': 'ADT Intent is Long-term', 
						'level': 'green' if not adt_duration else 'null', 
						'condition': 'No', 
						'result': 'blue' if not adt_duration else 'null'
						},
						{
						'name': 'Is there a bone density assessment?', 
						'parent': 'ADT Intent is Long-term', 
						'level': 'green' if adt_duration else 'null', 
						'condition': 'No', 
						'children': [{
							'name': 'Fail', 
							'parent': 'Is there a bone density assessment?', 
							'level': 'green' if adt_duration and not bone_density else 'null',
							'condition': 'No', 
							'result': 'red' if adt_duration and not bone_density else 'null'
							},
							{
							'name': 'Bone density assessment is three months prior to or after the ADT start date?', 
							'parent': 'Is there a bone density assessment?', 
							'level': 'green' if adt_duration and bone_density else 'null',
							'condition': 'Yes', 
							'children': [{
								'name': 'Pass', 
								'parent': 'Bone density assessment is three months prior to or after the ADT start date?', 
								'level': 'green' if result == 1 else 'null', 
								'condition': 'Yes', 
								'result': 'green' if result == 1 else 'null'
								},
								{
								'name': 'Fail', 
								'parent': 'Bone density assessment is three months prior to or after the ADT start date?', 
								'level': 'green' if result == 0 and bone_density else 'null', 
								'condition': 'No', 
								'result': 'red' if result == 0 and bone_density else 'null'
								}]
							}]
						}]
		}]]


		return result
	
	def AcuteGITotal(self):
		
		patient = self.patient

		current_date = datetime(2100, 1, 1).date()
		tmt_end_date = self.GetTreatmentDate('endDate')
		total_in_follow_up = 0 
		total_in_otv = 0 
		
		gi_type_list = ['acute gi', 'other gi', 'constipation', 'diarrhea', 'hematochezia', 'nausea', 'procititus', 'small bowel obstruction', 'stomach ulcer', 'vomit']
	
		if 'followUp' in patient:
			for follow_up_note in patient['followUp']:
				if 'visitDate' in follow_up_note:
					note_date = self.str_to_date(follow_up_note['visitDate']) 
				else:
					note_date = current_date
				if 'toxicity' in follow_up_note:
					for item in follow_up_note['toxicity']: 
						if 'toxicity' and 'grade' in item: 
							tox = item['toxicity'].lower()
							grade = re.search("[1-5]", item['grade'])
							grade2 = re.search("Not Stated", item['grade'])
							if (tox in gi_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and (grade or grade2):
								total_in_follow_up += 1
								break 

		if 'otv' in patient:
			for otv_note in patient['otv']:
				if 'visitDate' in otv_note:
					note_date = self.str_to_date(otv_note['visitDate']) 
					if 'toxicity' in otv_note:
						for item in otv_note['toxicity']: 
							if 'toxicity' and 'grade' in item: 
								tox = item['toxicity'].lower() 
								grade = re.search("[1-5]", item['grade'])
								grade2 = re.search("Not Stated", item['grade'])
								if (tox in gi_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
								(note_date and tmt_end_date) != current_date) and (grade or grade2):
									total_in_otv += 1 
									break 						

						
		total_notes = total_in_follow_up + total_in_otv
		return [patient['caseId'], total_notes]
	
	def AcuteGIWithGrade(self):
		
		patient = self.patient
		
		current_date = datetime(2100, 1, 1).date()
		tmt_end_date = self.GetTreatmentDate('endDate')
		total_in_follow_up = 0 
		total_in_otv = 0 
		
		gi_type_list = ['acute gi', 'constipation', 'diarrhea', 'hematochezia', 'nausea', 'procititus', 'small bowel obstruction', 'stomach ulcer', 'vomit']
				
		if 'followUp' in patient:
			for follow_up_note in patient['followUp']:
				if 'visitDate' in follow_up_note:
					note_date = self.str_to_date(follow_up_note['visitDate']) 
				else:
					note_date = current_date
				if 'toxicity' in follow_up_note:
					for item in follow_up_note['toxicity']: 
						if 'toxicity' and 'grade' in item: 
							tox = item['toxicity'].lower()
							grade = re.search("[1-5]", item['grade'])
							if (tox in gi_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and grade:
								total_in_follow_up += 1
								break 

		if 'otv' in patient:
			for otv_note in patient['otv']:
				if 'visitDate' in otv_note:
					note_date = self.str_to_date(otv_note['visitDate']) 
				if 'toxicity' in otv_note:
					for item in otv_note['toxicity']: 
						if 'toxicity' and 'grade' in item: 
							tox = item['toxicity'].lower() 
							grade = re.search("[1-5]", item['grade'])
							if (tox in gi_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and grade:
								total_in_otv += 1 
								break 						

		total_notes = total_in_follow_up + total_in_otv
	
		return [patient['caseId'], total_notes]

	def AcuteGUTotal(self):

		patient = self.patient
		
		current_date = datetime(2100, 1, 1).date()
		tmt_end_date = self.GetTreatmentDate('endDate')
		total_in_follow_up = 0 
		total_in_otv = 0 
		
		gu_type_list = ['acute gu','cystitis', 'dysuria', 'erectile dysfunction', 'frequency', 'nocturia', 'urgency']
				
		if 'followUp' in patient:
			for follow_up_note in patient['followUp']:
				if 'visitDate' in follow_up_note:
					note_date = self.str_to_date(follow_up_note['visitDate']) 
				else:
					note_date = current_date
				if 'toxicity' in follow_up_note:
					for item in follow_up_note['toxicity']: 
						if 'toxicity' and 'grade' in item: 
							tox = item['toxicity'].lower()
							grade = re.search("[1-5]", item['grade'])
							grade2 = re.search("Not Stated", item['grade'])
							if (tox in gu_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and (grade or grade2):
								total_in_follow_up += 1
								break 
		
		if 'otv' in patient:
			for otv_note in patient['otv']:
				if 'visitDate' in otv_note:
					note_date = self.str_to_date(otv_note['visitDate']) 
				if 'toxicity' in otv_note:
					for item in otv_note['toxicity']: 
						if 'toxicity' and 'grade' in item: 
							tox = item['toxicity'].lower() 
							grade = re.search("[1-5]", item['grade'])
							grade2 = re.search("Not Stated", item['grade'])
							if (tox in gu_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and (grade or grade2):
								total_in_otv += 1 
								break 									

						
		total_notes = total_in_follow_up + total_in_otv
	
		return [patient['caseId'], total_notes]

	def AcuteGUWithGrade(self):

		patient = self.patient
		
		current_date = datetime(2100, 1, 1).date()
		tmt_end_date = self.GetTreatmentDate('endDate')
		total_in_follow_up = 0 
		total_in_otv = 0 
		
		gu_type_list = ['acute gu','cystitis', 'dysuria', 'erectile dysfunction', 'frequency', 'nocturia', 'urgency']
				
		if 'followUp' in patient:
			for follow_up_note in patient['followUp']:
				if 'visitDate' in follow_up_note:
					note_date = self.str_to_date(follow_up_note['visitDate']) 
				else:
					note_date = current_date
				if 'toxicity' in follow_up_note:
					for item in follow_up_note['toxicity']: 
						if 'toxicity' and 'grade' in item: 
							tox = item['toxicity'].lower()
							grade = re.search("[1-5]", item['grade'])
							if (tox in gu_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and grade:
								total_in_follow_up += 1
								break 
		if 'otv' in patient:
			for otv_note in patient['otv']:
				if 'visitDate' in otv_note:
					note_date = self.str_to_date(otv_note['visitDate']) 
				if 'toxicity' in otv_note:
					for item in otv_note['toxicity']: 
						if 'toxicity' and 'grade' in item: 
							tox = item['toxicity'].lower() 
							grade = re.search("[1-5]", item['grade'])
							if (tox in gu_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and grade:
								total_in_otv += 1 
								break 							

						
		total_notes = total_in_follow_up + total_in_otv
	
		#print(total_notes, total_in_follow_up, total_in_otv)
		return [patient['caseId'], total_notes]
	
	def LateGITotal(self):

		patient = self.patient

		current_date = datetime(2100, 1, 1).date()
		tmt_end_date = self.GetTreatmentDate('endDate')
		total_in_follow_up = 0 
		total_in_otv = 0 

		gi_type_list = ['late gi', 'constipation', 'diarrhea', 'hematochezia', 'nausea', 'procititus', 'small bowel obstruction', 'stomach ulcer', 'vomit']

		if 'followUp' in patient:
			for follow_up_note in patient['followUp']:
				if 'visitDate' in follow_up_note:
					note_date = self.str_to_date(follow_up_note['visitDate']) 
				else:
					note_date = current_date
				if 'toxicity' in follow_up_note:
					for item in follow_up_note['toxicity']: 
						if 'toxicity' and 'grade' in item: 
							tox = item['toxicity'].lower()
							grade = re.search("[1-5]", item['grade'])
							grade2 = re.search("Not Stated", item['grade'])
							if (tox in gi_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and (grade or grade2):
								total_in_follow_up += 1
								break 
		
		if 'otv' in patient:
			for otv_note in patient['otv']:
				if 'visitDate' in otv_note:
					note_date = self.str_to_date(otv_note['visitDate']) 
				if 'toxicity' in otv_note:
					for item in otv_note['toxicity']: 
						if 'toxicity' and 'grade' in item: 
							tox = item['toxicity'].lower() 
							grade = re.search("[1-5]", item['grade'])
							grade2 = re.search("Not Stated", item['grade'])
							if (tox in gi_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and (grade or grade2):
								total_in_otv += 1 
								break 						

		total_notes = total_in_follow_up + total_in_otv

		return [patient['caseId'], total_notes]						

	def LateGIWithGrade(self):

		patient = self.patient 

		current_date = datetime(2100, 1, 1).date()
		tmt_end_date = self.GetTreatmentDate('endDate')
		total_in_follow_up = 0 
		total_in_otv = 0 

		gi_type_list = ['late gi', 'constipation', 'diarrhea', 'hematochezia', 'nausea', 'procititus', 'small bowel obstruction', 'stomach ulcer', 'vomit']

		if 'followUp' in patient:
			for follow_up_note in patient['followUp']:
				if 'visitDate' in follow_up_note:
					note_date = self.str_to_date(follow_up_note['visitDate']) 
				else:
					note_date = current_date
				if 'toxicity' in follow_up_note:
					for item in follow_up_note['toxicity']: 
						if 'toxicity' and 'grade' in item:  
							tox = item['toxicity'].lower() 
							grade = re.search("[1-5]", item['grade'])
							if (tox in gi_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and grade:
								total_in_follow_up += 1
								break 

		if 'otv' in patient:
			for otv_note in patient['otv']:
				if 'visitDate' in otv_note:
					note_date = self.str_to_date(otv_note['visitDate']) 
				else:
					note_date = current_date
				if 'toxicity' in otv_note:
					for item in otv_note['toxicity']: 
						if 'toxicity' and 'grade' in item: 
							tox = item['toxicity'].lower()  
							grade = re.search("[1-5]", item['grade'])
							if (tox in gi_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and grade:
								total_in_otv += 1 
								break 		

		total_notes = total_in_follow_up + total_in_otv
		
		return [patient['caseId'], total_notes]		

	def LateGUTotal(self):

		patient = self.patient

		current_date = datetime(2100, 1, 1).date()
		tmt_end_date = self.GetTreatmentDate('endDate')
		total_in_follow_up = 0 
		total_in_otv = 0 
		gu_type_list = ['late gu','cystitis', 'dysuria', 'erectile dysfunction', 'frequency', 'nocturia', 'urgency']

		if 'followUp' in patient:
			for follow_up_note in patient['followUp']:
				if 'visitDate' in follow_up_note:
					note_date = self.str_to_date(follow_up_note['visitDate']) 
				else:
					note_date = current_date
				if 'toxicity' in follow_up_note:
					for item in follow_up_note['toxicity']: 
						if 'toxicity' and 'grade' in item:  
							tox = item['toxicity'].lower() 
							grade = re.search("[1-5]", item['grade'])
							grade2 = re.search("Not Stated", item['grade'])
							if (tox in gu_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and (grade or grade2):
								total_in_follow_up += 1
								break 

		if 'otv' in patient:
			for otv_note in patient['otv']:
				if 'visitDate' in otv_note:
					note_date = self.str_to_date(otv_note['visitDate']) 
				else:
					note_date = current_date
				if 'toxicity' in otv_note:
					for item in otv_note['toxicity']: 
						if 'toxicity' and 'grade' in item: 
							tox = item['toxicity'].lower()  
							grade = re.search("[1-5]", item['grade'])
							grade2 = re.search("Not Stated", item['grade'])
							if (tox in gu_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and (grade or grade2):
								total_in_otv += 1 
								break 		

		total_notes = total_in_follow_up + total_in_otv
	
		return [patient['caseId'], total_notes]						

	def LateGUWithGrade(self):
		 
		patient = self.patient 
		
		current_date = datetime(2100, 1, 1).date()
		tmt_end_date = self.GetTreatmentDate('endDate')
		total_in_follow_up = 0 
		total_in_otv = 0 
		gu_type_list = ['late gu','cystitis', 'dysuria', 'erectile dysfunction', 'frequency', 'nocturia', 'urgency']

		if 'followUp' in patient:
			for follow_up_note in patient['followUp']:
				if 'visitDate' in follow_up_note:
					note_date = self.str_to_date(follow_up_note['visitDate']) 
				else:
					note_date = current_date
				if 'toxicity' in follow_up_note:
					for item in follow_up_note['toxicity']: 
						if 'toxicity' and 'grade' in item:  
							tox = item['toxicity'].lower() 
							grade = re.search("[1-5]", item['grade'])
							grade2 = re.search("Not Stated", item['grade'])
							if (tox in gu_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and grade:
								total_in_follow_up += 1
								break 

		if 'otv' in patient:
			for otv_note in patient['otv']:
				if 'visitDate' in otv_note:
					note_date = self.str_to_date(otv_note['visitDate']) 
				else:
					note_date = current_date
				if 'toxicity' in otv_note:
					for item in otv_note['toxicity']: 
						if 'toxicity' and 'grade' in item: 
							tox = item['toxicity'].lower()  
							grade = re.search("[1-5]", item['grade'])
							grade2 = re.search("Not Stated", item['grade'])
							if (tox in gu_type_list and note_date <= tmt_end_date + timedelta(days=90) and \
							(note_date and tmt_end_date) != current_date) and grade:
								total_in_otv += 1 
								break 				

		total_notes = total_in_follow_up + total_in_otv		

		return [patient['caseId'], total_notes]	

	def QualityMeasureNumberOfNotesWithToxicityInitialized(self):

		patient = self.patient
		tox_count_in_follow = 0 
		tox_count_in_otv = 0 

		if 'followUp' in patient:
			for follow_up_note in patient['followUp']: 
				if 'toxicity' in follow_up_note: 
					if len(follow_up_note['toxicity']) > 0: 
						tox_count_in_follow += 1

		if 'otv' in patient:
			for otv_note in patient['otv']:
				if 'toxicity' in otv_note:
					if len(otv_note['toxicity']) > 0:
						tox_count_in_otv += 1
		
		tox_count_total = tox_count_in_follow + tox_count_in_otv
		return [patient['caseId'], tox_count_total]

	def QualityMeasureWithGrade(self):

		patient = self.patient

		dates = []
		had_ebrt = False
		had_ldr = False        
		had_hdr = False        

		if 'prostateExternalBeamPlan' in patient:
			#print('prostateExternalBeamPlan:', patient['prostateExternalBeamPlan'])
			
			try:
				for item in patient['prostateExternalBeamPlan']:
					dates.append(('ebrt',item['endDate'].date()))
			except:
				pass
				
			
		if 'prostateLdrPlan'  in patient:
			for item in patient['prostateLdrPlan']:
				try:
					print('IMplantDate$$$$$$$$$$$$$$$$',item['implantDate'].date())
					dates.append(('ldr',item['implantDate'].date()))
					had_ldr = True
				except:
					pass

		
		if 'prostateHdrPlan'  in patient:
			for item in patient['prostateHdrPlan']:
				try:
					dates.append(('hdr',item['implantDate'].date()))
					had_hdr = True
				except:
					pass

		
		if 'prostateAdt' in patient:
			#print('ADT:' , patient['prostateAdt']['prostateAdtInjection'])
			if  patient['prostateAdt']:

				try:
					for item in patient['prostateAdt']['prostateAdtInjection']:
					# print(item['adtInjectionDate'].date())
						dates.append(('adt',item['adtInjectionDate'].date()))
						pass

				except:
					pass


		if  'surgeryDate'  in patient['patientInformation']:
			try:
				#print('SurgeryDate::::::::::::::::::::', patient['patientInformation']['surgeryDate'].date())
				dates.append(('surgery',patient['patientInformation']['surgeryDate'].date()))
			except :
				pass
			
				
		print(sorted(dates, key= lambda x : x[1]))
		# if had_ebrt and had_ldr:
		#     return 1

		return ['Needs fix', None]

	def TotalNumberOfNotes(self):
		return 0
	
	fdict = {
		'QualityMeasure1':QualityMeasure1,
		'QualityMeasure2':QualityMeasure2,
		'QualityMeasure3':QualityMeasure3,
		'QualityMeasure4':QualityMeasure4,
		'QualityMeasure5':QualityMeasure5,
		'QualityMeasure6':QualityMeasure6,
		'QualityMeasure7':QualityMeasure7,
		'QualityMeasure8':QualityMeasure8,
		'QualityMeasure9':QualityMeasure9,
		'QualityMeasure10':QualityMeasure10,
		'QualityMeasure11':QualityMeasure11,
		'QualityMeasure12':QualityMeasure12,
		'QualityMeasure13':QualityMeasure13,
		'QualityMeasure14':QualityMeasure14,
		'QualityMeasure15':QualityMeasure15,
		'QualityMeasure15_color':QualityMeasure15_color,
		'QualityMeasure17A':QualityMeasure17A,
		'QualityMeasure17B':QualityMeasure17B,
		'QualityMeasure18':QualityMeasure18,
		'QualityMeasure19':QualityMeasure19,
		'QualityMeasure23':QualityMeasure23,
		'QualityMeasure24':QualityMeasure24,
	#	'TotalNumberOfNotes': TotalNumberOfNotes,
		'AcuteGITotal':AcuteGITotal,
		'AcuteGIWithGrade':AcuteGIWithGrade,
		'AcuteGUTotal':AcuteGUTotal,
		'AcuteGUWithGrade':AcuteGUWithGrade,
		'LateGITotal': LateGITotal, 
		'LateGIWithGrade': LateGIWithGrade,
		'LateGUTotal': LateGUTotal, 
		'LateGUWithGrade': LateGUWithGrade,
		'NumberOfNotesWithToxicityInitialized':QualityMeasureNumberOfNotesWithToxicityInitialized
	}
