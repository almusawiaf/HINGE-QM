import numpy as np
from pymongo import MongoClient
from datetime import datetime, timedelta
from collections import OrderedDict

from .measure import Measure
from .measure import logging


class CommunityProstateMeasure(Measure):

	patient = None

	measures = OrderedDict({
		"center_id": None,
		"center_name": None,
		"vha_id": None,
		"disease_type": None,
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
		#"QualityMeasure18": None,
		"QualityMeasure19": None,
		"QualityMeasure24": None,
		"NumberOfNotesWithToxicityInitialized" : None,
		"TotalNumberOfNotes" : None,
		"AcuteGUWithGrade" : None,
		"AcuteGUTotal" : None,
		# "LateGUWithGrade" : None,
		# "LateGUTotal" : None,
		"AcuteGIWithGrade" : None,
		"AcuteGITotal" : None,
		# "LateGIWithGrade" : None,
		# "LateGITotal" : None
	})

	def GetTreatmentDate(self, date_type):

		patient = self.patient

		start_times = []

		try:

			if 'prostateExternalBeamTreatment' in patient:
				plans = patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']
				times = [datetime.strptime(plan['startDate'], '%Y-%m-%d').date() for plan in plans if 'startDate' in plan]
				start_times.extend(times)
			else:
				times = []

		except:
			logging.info('no ebrt!!')

		logging.info('After EBRT: {}'.format(start_times))
		try:
			if 'prostateAdt' in patient:
				injections = patient['prostateAdt']['prostateAdtInjection']
				times = [datetime.strptime(injection['adtInjectionDate'], '%Y-%m-%d').date()
						 for injection in injections if 'adtInjectionDate' in injection]
				start_times.extend(times)
			else:
				times = []
		except:
			logging.info('no ADT!!!')

		logging.info('after ADT: {}'.format(start_times))

		try:

			if 'prostateLdrTreatment' in patient:
				plans = patient['prostateLdrTreatment']['prostateLdrPlan']
				times = [datetime.strptime(plan['implantDate'], '%Y-%m-%d').date()
				for plan in plans if 'implantDate' in plan]
				start_times.extend(times)
			else:
				times = []
		except:
			logging.info('no LDR times')

		logging.info('after LDR-: {}'.format(start_times))

		if len(start_times) > 0:
			sorted_times = start_times.sort()
			if date_type == 'start':
				return sorted_times[0]
			elif date_type == 'end':
				return sorted_times[-1]
			else:
				logging.error("Treatment dates: provide proper type!")
		else:
			return datetime.now().date()

	def QualityMeasure1(self):

		patient = self.patient

		ps_instruments_std = set(['ecog', 'who', 'kps', 'zubrod'])

		try:
			ps = patient['performanceStatusConsult']
			ps_instruments_found = [ps['performanceInstrument'].lower()]
		except:
			ps_instruments_found = ['not_found']

		condition_1 = len(ps_instruments_std.intersection(ps_instruments_found)) > 0

		if condition_1:
			logging.info(ps_instruments_found)
			result = 1
		else:
			logging.info(ps_instruments_found)
			result = 0

		result = [patient['caseId'], result, condition_1]

		return result

	def QualityMeasure2(self):

		patient = self.patient

		try:
			had_surgery = True if (
				patient['isSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False

		try:
			logging.info(patient['prostateScoringAndGrades'])
			psa = [float(item['PSAScore']) for item in patient['prostateScoringAndGrades']['psaScores'] if 'PSAScore' in item]
			logging.info(psa)
		except:
			psa = []

		if len(psa) == 0:
			try:
				print(patient['psa']['psaScores'])
				psa = [float(item['PSAScore']) for item in patient['psa']['psaScores'] if 'PSAScore' in item]
			except:
				psa = []
		try:
			primary_gs = float(patient['prostateScoringAndGrades']['primaryGS'])
		except:
			primary_gs = np.nan

		try:
			secondary_gs = float(patient['prostateScoringAndGrades']['secondaryGS'])
		except:
			secondary_gs = np.nan

		try:
			total_gs = float(patient['prostateScoringAndGrades']['totalGS'])
		except:
			total_gs = np.nan

		# Staging
		valid_t_stage = ['t1', 't1a', 't1b', 't1c', 't2', 't2a', 't2b', 't2c', 't3', 't3a', 't3b', 't4', 't4a', 't4b']
		try:
			t_stage = patient['prostateScoringAndGrades']['TX'].lower()
		except:
			t_stage = None

		valid_risks = ['very low', 'low', 'intermediate', 'high', 'very high']

		try:
			risk = patient['prostateScoringAndGrades']['riskGroup'].lower()
		except:
			risk = None

		print("PSA:{}, \t risk: {} \t t_stage: {} \t primary: {} \t secondary:{} \t total: {}".format(psa, risk, t_stage, primary_gs, secondary_gs, total_gs))

		condition_true =  (risk in valid_risks) and (len(psa) > 0) and ((isinstance(primary_gs, float) or  isinstance(secondary_gs, float) or isinstance(total_gs, float))) and (t_stage in valid_t_stage)
		if had_surgery: 
			result = 2
		elif condition_true:
			result = 1
		else:
			result = 0

		logging.info([str(item) for item in [psa, t_stage, primary_gs, secondary_gs, total_gs, risk]])

		result = ([patient['caseId'], result, had_surgery, condition_true])

		return result

	def QualityMeasure3(self):

		patient = self.patient
		
		valid_risks = ['high', 'very high']

		try:
			had_surgery = True if (
				patient['isSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False

		try:
			risk = patient['prostateScoringAndGrades']['riskGroup'].lower()
		except:
			risk = None

		Not_Found = 0

		try:
			boneScan = True if patient['prostateImagingStudies']['boneScan'].lower() == 'yes' else False
		except:
			boneScan = False
			Not_Found += 1
		
		try:
			pelvicMRI = True if patient['prostateImagingStudies']['pelvicMRI'].lower() == 'yes' else False
		except:
			pelvicMRI = False
			Not_Found += 1		
		try:
			pelvicCT = True if patient['prostateImagingStudies']['pelvicCt'].lower() == 'yes' else False
		except:
			pelvicCT = False
			Not_Found += 1

		if Not_Found == 3 or risk not in valid_risks or had_surgery == True:
			result = 2
		elif(pelvicCT or pelvicMRI) and boneScan  and Not_Found < 3 :
			result = 1
		else:
			result = 0

		print("had_surgery:{}\t risk:{}\t pelvicCT:{}\t pelvicMRI:{}\t boneScan:{}\tNot Found count:{}".format(had_surgery, risk, pelvicCT, pelvicMRI, boneScan, Not_Found))
		result = [patient['caseId'], result, had_surgery, risk, Not_Found]

		return result

	# FIX ME: producing wrong results
	def QualityMeasure4(self):

		patient = self.patient

		#current_date = datetime(2100, 1, 1).date()
		
		valid_risks = ['intermediate']

		try:
			logging.info(patient['prostateImagingStudies'])
		except:
			logging.info('no diagnosticTests')
		
		try:
			had_surgery = True if (
				patient['isSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False
		try:
			risk = patient['prostateScoringAndGrades']['riskGroup'].lower()
		except:
			risk = None

		valid_treatment_options = set(['external beam rt', 'interstitial prostate brachytherapy', 'radical prostatectomy'])

		try:
			options = patient['prostateTreatmentOptions']
			if 'prostateTreatmentOption' in options:
				found_options = [item['treatmentTechnique'].lower()
								 for item in options['prostateTreatmentOption']]
			else:
				found_options = [item['treatmentTechnique'].lower()
								 for item in options]

		except:
			found_options = [None]

		logging.info("PatietID:{} \t had_surgry: {} \t Risk:{} \t found_Options:{}\t".format(patient['caseId'],had_surgery, risk, found_options))
		
		invalid_risks = ['very low', 'low', 'high', 'very high']

		if had_surgery or (risk in invalid_risks):
			result = 2
		elif risk == 'not stated':
			result = 0
		elif len(valid_treatment_options.intersection(found_options)) == 3 and (risk in valid_risks):
			result = 1
		else:
			result = 0

		print("PatietID:{} \t had_surgry: {} \t Risk:{} \t found_Options:{}\t".format(patient['caseId'],had_surgery, risk, found_options))
		result = [patient['caseId'], result, had_surgery, risk in valid_risks, len(valid_treatment_options.intersection(found_options)) == 3]

		return result

	def QualityMeasure5(self):

		patient = self.patient

		qols_valid = set(['ipss', 'aua', 'epic-26', 'iief/shim'])

		try:
			if 'qualityOfLifeConsult' in patient:
				consult_notes = patient['qualityOfLifeConsult']
				logging.info(consult_notes)
				qols_found = [item['assessment'].lower()
							  for item in consult_notes['qualityOfLifeScore']]
			else:
				consult_notes = ['No qualityOfLifeConsult']
				qols_found = [None]

		except:
			consult_notes = ['No qualityOfLifeConsult']
			qols_found = [None]

		if len(qols_valid.intersection(qols_found)) > 0:
			result = 1
		else:
			result = 0

		logging.info([str(item) for item in [qols_found, consult_notes]])
		print("PatientId: {}\t QoL found: {} \t".format(patient['caseId'], qols_found ))

		result = [patient['caseId'], result, len(qols_valid.intersection(qols_found)) > 0]

		return result

	def QualityMeasure6(self):
		patient = self.patient		
		current_date = datetime.now().date()
		
		try:
			isclinical =  True if('clinicalTrial' in patient) else False
		except:
			isclinical = False

		try:
			isclinical_selected = True if (patient['clinicalTrial']['clinicalTrialEnrollment'].lower() == 'yes') else False
		except:
			isclinical_selected = False

		try:
			trial_date  = self.str_to_date(patient['clinicalTrial']['clinicalTrialEnrollmentDate'])
		except:
			trial_date = current_date
	
		try:
			tmt_start_date = self.GetTreatmentDate('start')
		except:
			tmt_start_date = current_date

		if isclinical and\
			isclinical_selected  and\
			trial_date < tmt_start_date and (tmt_start_date != current_date and trial_date != current_date):
			result = 1
		else:
			logging.info([str(item) for item in [isclinical, isclinical_selected, trial_date, tmt_start_date]])
			result = 0

		
		result = [patient['caseId'], result, isclinical, isclinical_selected, trial_date < tmt_start_date and (tmt_start_date != current_date and trial_date != current_date)]
		
		logging.info([str(item) for item in result])
		if result[1] == 1:
			print("patienId: {} \t isClinical: {} \t isClinical_Selected: {} \t Trial Date: {} \t Treatment Start Date: {}".format(patient['caseId'], isclinical, isclinical_selected, trial_date, tmt_start_date))
		return result

	def QualityMeasure7(self):

		patient = self.patient

		try:
			logging.info(patient['prostateExternalBeamTreatment'])

			is_ebrt_present = True if(len(patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']) > 0) else False
		except:
			is_ebrt_present = False

		try:
			mod_count = 0
			modalities_found = []
			plans = patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']
			for plan in plans:
				if ('modality' in plan) and (plan['modality'].lower() in ['3d', 'imrt']):
					mod_count += 1			
					modalities_found.append(plan['modality'].lower())

		except:
			mod_count = 0
			plans = []

		if not is_ebrt_present:
			result = 2
		elif (mod_count != 0) and (mod_count == len(plans)) and (len(plans) != 0):
			result = 1
		else:
			result = 0

		print("patientId: {}\t EBRT Present: {} \t Modalities Found: {}\t Modalities Count: {}".format(patient['caseId'], is_ebrt_present, modalities_found, mod_count))

		result = [patient['caseId'], result, is_ebrt_present,
				  (mod_count != 0) and mod_count == len(plans)]

		logging.info([str(item) for item in result])

		return result

	def QualityMeasure8(self):

		patient = self.patient

		dvh_true_strucs = set(['ptv', 'bladder', 'rectum'])

		try:
			is_ebrt_present = True if(len(patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']) > 0) else False
		except:
			is_ebrt_present = False

		try:
			logging.info( patient['prostateOtherInformation'])
			is_dvh_analysis = patient['prostateOtherInformation']['dhvAnalysis'].lower()
		except:
			is_dvh_analysis = 'no'

		try:
			dvh_strucs = [item['structuresEvaluated'].lower() for item in patient['prostateOtherInformation']['prostateDvhEvaluatedStructures']]
		except:
			dvh_strucs = [None]

		if not is_ebrt_present:
			result = 2
		elif is_dvh_analysis == 'yes' and len(dvh_true_strucs.intersection(dvh_strucs)) == 3:
			result = 1
		else:
			result = 0

		logging.info(dvh_strucs)

		print("PatientID: {} \t is_dvh_analysis: {} \t DVH Structure: {}".format(patient['caseId'], is_dvh_analysis, dvh_strucs))
		result = [patient['caseId'], result, is_ebrt_present, is_dvh_analysis == 'yes', len(dvh_true_strucs.intersection(dvh_strucs)) == 3]

		return result

	def QualityMeasure9(self):

		patient = self.patient

		current_date = datetime(2100, 1, 1).date()

		valid_risks = ['high', 'very high']

		try:
			had_surgery = True if (
				patient['isSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False

		try:
			logging.info(patient['prostateScoringAndGrades'])
			risk = patient['prostateScoringAndGrades']['riskGroup'].lower()
		except:
			risk = 'not_high'

		try:
			adt_injection_count = len(patient['prostateAdt']['prostateAdtInjection'])
		except:
			adt_injection_count = 0

		try:
			adt_date = self.str_to_date(patient['prostateAdt']['prostateAdtInjection'][0]['adtInjectionDate'])
		except:
			adt_date = current_date

		try:
			logging.info(patient['prostateExternalBeamTreatment'])
			ebrt_date = self.str_to_date(patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan'][0]['startDate'])
		except:
			ebrt_date = current_date

		logging.info([str(item) for item in [had_surgery, risk, adt_injection_count, adt_date, type(adt_date), ebrt_date, type(ebrt_date)]])

		adt_days = adt_date - ebrt_date

		if had_surgery or (risk not in valid_risks):
			result = 2
		elif adt_injection_count > 0: 
			#(((adt_date - ebrt_date).days <= 15)) and (adt_date != current_date and ebrt_date != current_date):
			result = 1
		elif adt_injection_count <= 0: #
			#or adt_days.days >= 15:
			result = 0

		logging.info('quality measure 9: {}'.format([risk, adt_days.days,  adt_date, ebrt_date, adt_injection_count]))
		print("PatientID: {} \t had_surgery: {} \t risk: {} \t ADT_Injection_count:{}".format(patient['caseId'], had_surgery, risk, adt_injection_count))

		result = [patient['caseId'], result, had_surgery, risk not in valid_risks, adt_injection_count > 0 ]

		return result

	def QualityMeasure10(self):

		patient = self.patient

		current_date = datetime(2100, 1, 1).date()

		valid_risks = ['intermediate']

		try:
			had_surgery = True if (
				patient['isSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False

		try:
			logging.info(patient['prostateScoringAndGrades'])
			risk = patient['prostateScoringAndGrades']['riskGroup'].lower()
		except:
			risk = 'not_found'

		try:
			adt_injection_count = len(patient['prostateAdt']['prostateAdtInjection'])
		except:
			adt_injection_count = 0

		try:
			adt_date = self.str_to_date(patient['prostateAdt']['prostateAdtInjection'][0]['adtInjectionDate'])
		except:
			adt_date = current_date

		try:
			logging.info(patient['prostateExternalBeamTreatment'])
			ebrt_date = self.str_to_date(patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan'][0]['startDate'])
		except:
			ebrt_date = current_date

		logging.info([str(item) for item in [had_surgery, risk, adt_injection_count, adt_date, type(adt_date), ebrt_date, type(ebrt_date)]])

		adt_days = adt_date - ebrt_date

		if had_surgery or (risk not in valid_risks):
			result = 2
		elif adt_injection_count > 0: 
			#(((adt_date - ebrt_date).days <= 15)) and (adt_date != current_date and ebrt_date != current_date):
			result = 1
		elif adt_injection_count <= 0: #
			#or adt_days.days >= 15:
			result = 0

		logging.info('quality measure 10: {}'.format([risk, adt_days.days,  adt_date, ebrt_date, adt_injection_count]))
		print("PatientID: {} \t had_surgery: {} \t risk: {} \t ADT_Injection_count:{}".format(patient['caseId'], had_surgery, risk, adt_injection_count))

		result = [patient['caseId'], result, had_surgery, risk not in valid_risks, adt_injection_count == 0, adt_injection_count > 0]

		return result

	def QualityMeasure11(self):

		patient = self.patient

		try:                
			had_surgery=  True  if (patient['isSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False

		try:
			had_ebrt = True if (int(patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan'][0]['prescriptionDose']) > 0)  else  False                  
		except:
			had_ebrt = False

		try:                
			had_hdr = True  if patient['prostateHdrTreatment'] else False
		except:
			had_hdr = False 
			
		try:                
			had_ldr = True if (patient['prostateLdrTreatment']['prostateLdrPlan']) else False
		except:
			had_ldr = False

		try:
			daily_target = patient['prostateOtherInformation']['dailyTargetLocalization'].lower()
		except:
			daily_target = None		
		
		valid_daily_targets = ['Cone Beam CT', 'Fiducial markers with portal imaging', 'Fiducial markers with cone beam CT',  'Electromagnetic transponders', 'Utrasound (transabdominal or transperineal)']
		valid_daily_targets = [item.lower() for item in valid_daily_targets]
	
		if had_surgery  or  (had_ebrt and ( had_ldr or  had_hdr)):
			result = 2
		elif had_ebrt  and (daily_target in valid_daily_targets):
			result = 1
		else:
			result = 0    

		logging.info([str(item) for item in [had_surgery, had_ebrt, had_ldr, had_hdr, daily_target]])

		print("PaatientID:{} \t Had_Surgery:{} \t Had_EBRT: {} \t Had_LDR:{} \t Had_HDR:{} \t Daily_Target:{}".format(patient['caseId'], had_surgery, had_ebrt, had_ldr, had_hdr, daily_target))
		result =  [patient['caseId'], result, had_surgery,  (had_ebrt and (not had_ldr and not had_hdr)), daily_target in valid_daily_targets]

		return result

	def QualityMeasure12(self):

		patient = self.patient

		valid_risks = ['high', 'very high']

		try:
			logging.info(patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan'][0]['prescriptionDose'])
			had_ebrt = True if (int(patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan'][0]['prescriptionDose']) > 0)  else  False                  
		except:
			had_ebrt = False

	
		try:                
			had_surgery=  True  if (patient['isSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False


		try:
			logging.info(patient['prostateScoringAndGrades'])
			risk = patient['prostateScoringAndGrades']['riskGroup'].lower()
		except:  
			risk = 'not_valid_risk'

		try:
			plans = patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']
			comprehensive_plan = [item['wholePelvis'].lower() for item in plans]
		except:
			comprehensive_plan = ['none']        

		logging.info([str(item) for item in [had_ebrt, had_surgery, risk, comprehensive_plan]])
		
		if (not had_ebrt) or (risk not in valid_risks) or had_surgery:
			result = 2
		elif had_ebrt and not had_surgery and (risk in valid_risks) and ('yes' in comprehensive_plan):
			result = 1
		else:
			result = 0

		result = [patient['caseId'], result,  had_ebrt, had_surgery, risk in valid_risks, 'yes' in comprehensive_plan]
		print("PateintID:{} \t Had_EBRT: {} \t Had_Surgery:{} \t Risk: {} \t Comprehensive Plans: {}".format(patient['caseId'], had_ebrt, had_surgery, risk, comprehensive_plan))

		return result

	def QualityMeasure13(self):

		patient = self.patient

		immobilizations = ['body mold', 'bound feet']
		invalid_daily_targets = ['electromagnetic transponders', 'not_found']

		try:
			logging.info(patient['prostateOtherInformation'])
			immobilization = patient['prostateOtherInformation']['immobilization'].lower()
		except:
			immobilization = "not_found"

		try:
			had_ebrt = True if (int(patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan'][0]['fractions']) > 0)  else  False                  
		except:
			had_ebrt = False
		
		try:    
			daily_target = patient['prostateOtherInformation']['dailyTargetLocalization'].lower()
		except:
			daily_target = 'not_found'
		 
		try:    
			#sim_note = patient['prostateOtherInformation']['isSimNoteOrSiteSetup'].lower()
			#we are assuming that is In SimNote or Site Setup for community data
			sim_note = 'yes'

		except:
			sim_note = 'not_found'
		

		if  (not had_ebrt) or (daily_target in invalid_daily_targets):
			result =  2
		elif (immobilization in immobilizations )and  had_ebrt and sim_note == 'yes':
			result = 1
		else:
			result = 0

		logging.info([str(item) for item in [had_ebrt, sim_note, daily_target, immobilization]])
		
		result = [patient['caseId'], result,  had_ebrt, sim_note == 'yes', daily_target.lower() in  invalid_daily_targets, immobilization in immobilizations]
		
		print("PatientID: {} \t Had_EBRT: {} \t  Daily_Target: {} \t Immobolization: {} \t SimNote: {}".format(patient['caseId'], had_ebrt, daily_target, immobilization, sim_note))

		return result

	def QualityMeasure14(self):

		patient = self.patient

		try:
			tottal_dose = int(patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan'][0]['prescriptionDose'])
			logging.info('QM14 - EBRT Fractions: {}'.format([tottal_dose]))
			had_ebrt = True if tottal_dose > 0 else  False                   
		except:
			had_ebrt = False

		try:                
			had_hdr = True  if patient['prostateHdrTreatment'] else False
		except:
			had_hdr = False 
			
		try:                
			had_ldr = True if (patient['prostateLdrTreatment']['prostateLdrPlan']) else False
		except:
			had_ldr = False
		
		try:
			plans = patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']
			for plan in plans:
				if ('modality' in plan ) and (plan['modality'].lower() == 'sbrt'):
					sbrt = True
					break
				else:
					sbrt = False
		except:  
			sbrt = False

		try:                
			cl_trials = True if self.QualityMeasure6()[1] == 1 else False
		except:
			cl_trials = False 
		
		try:                
			had_surgery=  True  if (patient['isSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False

			   
		try:                
			is_recurrent = True  if (patient['patientInformation']['recurrentDisease'].lower() == 'yes') else False
			logging.info('is_recurrent:' + str(patient['patientInformation']['recurrentDisease'].lower()))
		except:
			is_recurrent = False 


		dose_fraction_200 = 0 
		try:
			plans = patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']
			num_plans = len(plans) if (len(plans) > 0) else 0

			for plan in plans:
				dose = float(plan['prescriptionDose']) * 100.0
				fractions = int(plan['fractions'])

				logging.info([str(item) for item in [dose, fractions]])
				print("Fractions: {}, {}, {}".format(dose, fractions, dose/fractions))
				if round((dose / fractions), 0) > 200.0 :
					dose_fraction_200 += 1
		except:  
			dose_fraction_200 = 0
			num_plans = 0

		logging.info('dose_fraction: {}'.format([dose_fraction_200, num_plans]))

		if (dose_fraction_200 > 0 and num_plans > 0 and num_plans == dose_fraction_200):
			is_all_plan = True
		else: 
			is_all_plan = False

		try:
			dose_fraction_count = 0 
			plans = patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']
			num_plans = len(plans) if (len(plans) > 0) else 0
			cumilative_plans = 0

			for plan in plans:
				dose = float(plan['prescriptionDose']) * 100.0
				fractions = int(plan['fractions'])
				
				cumilative_plans += dose
				dose_per_fraction = round(dose / fractions, 0)
				
				if  dose_per_fraction >= 180.0 and  dose_per_fraction <= 200.0 :
					dose_fraction_count += 1
					logging.info([dose, fractions, dose_per_fraction, dose_per_fraction >= 180.0 and dose_per_fraction <= 200.0])
				else:
					logging.info([dose, fractions, dose_per_fraction, dose_per_fraction >= 180.0 and dose_per_fraction <= 200.0])
					pass
		except:  
			dose_fraction_count = 0
			num_plans = 0
			cumilative_plans = 0

		if (dose_fraction_count > 0 and num_plans > 0 and num_plans == dose_fraction_count and (cumilative_plans <= 7400.0)):
			is_cumilative = True
		else: 
			is_cumilative = False
			


		if (had_ebrt and (had_hdr and had_ldr)) or sbrt or cl_trials or had_surgery or is_recurrent or is_all_plan:
			result = 2
		#elif (had_ebrt and (not had_hdr and  not had_ldr)) and (not sbrt) and (not cl_trials) and (not had_surgery )and (not is_recurrent) and
		elif (had_ebrt and (not had_hdr and  not had_ldr)) and (not is_all_plan) and is_cumilative:
			result = 1
		else:
			result = 0

		logging.info([str(item) for item in [[patient['caseId'], result, (had_ebrt and (not had_hdr and  not had_ldr)), sbrt, cl_trials, had_surgery, is_recurrent, is_all_plan, is_cumilative]]])

		print("PatientID:{} \t Had_EBRT: {} \t Had_LDR:{} \t Had_HDR: {} \t SBRT: {} \t CLinical_Trials: {} \t  Had_Surgery: {} \t Is_Recurrent: {} \t Is_All_Plans: {}, \t Is_Cumilative: {}".format(patient['caseId'], had_ebrt, had_ldr, had_hdr, sbrt, cl_trials, had_surgery, is_recurrent, is_all_plan, is_cumilative ))
		
		result = [patient['caseId'], result, (had_ebrt and (not had_hdr and  not had_ldr)), sbrt, cl_trials, had_surgery, is_recurrent, is_all_plan, is_cumilative]
		
		return result
		
	def QualityMeasure15_color(self):

		patient = self.patient

		try:
			fractions = int(patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan'][0]['fractions'])
			logging.info('QM14 - EBRT Fractions: {}'.format(fractions))
			had_ebrt = True if fractions > 0 else  False                   
		except:
			had_ebrt = False

		try:                
			had_hdr = True  if patient['prostateHdrTreatment'] else False
		except:
			had_hdr = False 
			
		try:                
			had_ldr = True if (patient['prostateLdrTreatment']['prostateLdrPlan']) else False
		except:
			had_ldr = False
		
		try:
			plans = patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']
			for plan in plans:
				sbrt_val = plan['modality'].lower()
				if ('modality' in plan ) and (sbrt_val == 'sbrt'):
					sbrt = True
					break
				else:
					sbrt = False
		except:  
			sbrt = False

		try:                
			cl_trials = True if self.QualityMeasure6()[1] == 1 else False
		except:
			cl_trials = False 
		
		try:                
			had_surgery=  True  if (patient['isSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False
 
	 
		try:
			dose_fraction_200 = 0 
			plans = patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']
			
			num_plans = len(plans) if (len(plans) > 0) else 0

			for plan in plans:
				dose = round(float(plan['prescriptionDose']) * 100.0, 0)
				fractions = (plan['fractions'])
				logging.info(str(patient['caseId']) + ' dose_fraction {}'.format([dose, fractions, round(dose/fractions), 0]))
				if (dose / fractions) > 200.0 :
					dose_fraction_200 += 1
		except:  
			dose_fraction_200 = 0
			num_plans = 0

		try:
			dose_fraction_count = 0 
			plans = patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']
			num_plans = len(plans) if (len(plans) > 0) else 0
			cumilative_plans = 0


			for plan in plans:
				dose = round(float(plan['prescriptionDose']) * 100.0, 0)
				fractions = int(plan['fractions'])
				cumilative_plans += dose
				dose_per_fraction = round(dose / fractions, 0)

				if  dose_per_fraction >= 180.0 and  dose_per_fraction <= 200.0 :
					dose_fraction_count += 1
					logging.info([dose, fractions, dose_per_fraction, dose_per_fraction >= 180.0 and dose_per_fraction <= 200.0, cumilative_plans])
					#print('******************************************************')
				else:
					logging.info([dose, fractions, dose_per_fraction, dose_per_fraction >= 180.0 and dose_per_fraction <= 200.0, cumilative_plans])
					pass
		except:  
			dose_fraction_count = 0
			num_plans = 0
			cumilative_plans = 0

		logging.info([dose_fraction_count, num_plans, cumilative_plans])
		if (dose_fraction_count > 0 and num_plans > 0 and num_plans == dose_fraction_count and cumilative_plans >= 6000.0 and cumilative_plans <= 7400.0):
			is_cumilative = True
		else: 
			is_cumilative = False

		def get_color_code(cumilative):
			if cumilative >= 6400.0 and cumilative <= 7200.0:
				return 'Green'
			elif cumilative >= 6000.0 and cumilative < 6400.0:
				return 'Yellow'
			elif cumilative > 7200.0:
				return 'Red'
			else:
				logging.info('cumilative: {}'.format(cumilative))
				return 'total_dose_{}_<_6000.0'.format(str(cumilative))
			

		if (had_surgery) | (not (had_ebrt & (not had_hdr and not had_ldr)))  |  sbrt  |  cl_trials | dose_fraction_200 > 0:
			logging.info(['dose_fractions_200', dose_fraction_200])
			result = 'Excluded'
		elif is_cumilative:
				result = get_color_code(cumilative_plans)
		else:
				result = get_color_code(cumilative_plans)

		result = [patient['caseId'], result, had_surgery, (had_ebrt and (not had_hdr and not had_ldr)), sbrt, cl_trials, dose_fraction_200 > 0, is_cumilative]
		
		return result

	def QualityMeasure15(self):
		patient = self.patient

		try:
			total_dose = int(patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan'][0]['prescriptionDose'])
			logging.info('QM15 - EBRT Fractions: {}'.format(total_dose))
			had_ebrt = True if total_dose > 0 else  False                   
		except:
			had_ebrt = False

		try:                
			had_hdr = True  if patient['prostateHdrTreatment'] else False
		except:
			had_hdr = False 
			
		try:                
			had_ldr = True if (patient['prostateLdrTreatment']['prostateLdrPlan']) else False
		except:
			had_ldr = False
		
		try:
			plans = patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']
			for plan in plans:
				sbrt_val = plan['modality'].lower()
				if ('modality' in plan ) and (sbrt_val == 'sbrt'):
					sbrt = True
					break
				else:
					sbrt = False
		except:  
			sbrt = False

		try:                
			cl_trials = True if self.QualityMeasure6()[1] == 1 else False
		except:
			cl_trials = False 
		
		try:                
			had_surgery=  True  if (patient['isSurgery'].lower() == 'yes') else False
		except:
			had_surgery = False
 
	 
		try:
			dose_fraction_200 = 0 
			dose_fraction_count = 0 
			cumilative_plans = 0
			invalid_fractions = 0

			plans = patient['prostateExternalBeamTreatment']['prostateExternalBeamPlan']
			num_plans = len(plans) if (len(plans) > 0) else 0

			for plan in plans:
				dose = round(float(plan['prescriptionDose']) * 100.0, 0)
				fractions = (plan['fractions'])
				logging.info('dose_fraction {}'.format([dose, fractions, round(dose/fractions), 0]))

				cumilative_plans += dose
				dose_per_fraction = round(dose / fractions, 0)

				if dose_per_fraction > 200.0 :
					dose_fraction_200 += 1
				elif dose_per_fraction < 180.0:
					invalid_fractions += 1
				elif  dose_per_fraction >= 180.0 and  dose_per_fraction <= 200.0 :
					dose_fraction_count += 1
				
				else:
					logging.warn("Dose per fraction is wrong {}".format(dose_per_fraction))
		except:  
			dose_fraction_200 = 0
			dose_fraction_count = 0
			cumilative_plans = 0
			invalid_fractions = 0
			num_plans = 0

		logging.info([dose_fraction_count, num_plans, cumilative_plans])

		if (dose_fraction_count > 0) and (num_plans > 0) and (num_plans == dose_fraction_count) and (invalid_fractions == 0)  and (cumilative_plans >= 6000.0 and cumilative_plans <= 7400.0):
			is_cumilative = True
		else: 
			is_cumilative = False

		if had_surgery | (had_ebrt &  (had_hdr | had_ldr))  |  sbrt  |  cl_trials | dose_fraction_200 > 0:
			result = 2
		elif  is_cumilative :				
				result = 1
		else:
				result = 0

		result = [patient['caseId'], result, had_surgery, (had_ebrt and (not had_hdr and not had_ldr)), sbrt, cl_trials, dose_fraction_200 > 0, is_cumilative]
		
		print("PatientID: {} \t Had_Surgery: {} \t Had_EBRT: {} \t Had_LDR: {} \t Had_HDR: {}\t SBRT: {}\t IsClinical: {}\t Dose_Per_Fraction_200: {} \t Dose_Per_Fraction_180:{} \tCumilativeDose:{}\t ".format(patient['caseId'], had_surgery, had_ebrt, had_ldr, had_hdr, sbrt, cl_trials, dose_fraction_200, dose_fraction_count, cumilative_plans)	)
		print("PatientID: {} \t Dose_Per_Fraction_200: {} \t Dose_Per_Fraction_180:{} \t CumilativeDose:{}\t ".format(patient['caseId'],  dose_fraction_200, dose_fraction_count, cumilative_plans)	)
				
		return result

	def QualityMeasure16(self):
		"""
		Survivorship Plan
		"""
		valid_plans = set(['follow up care', 'dose delivered', 'relevant assessment of tolerance to and progress towards the treatment goals'])
		patient = self.patient
		try:
			survivorship = patient['survivorship']['survivorshipCarePlan']
			survivorship_care_plans = [item['carePlan'].lower() for item in survivorship]
		except:
			print("No Survivorhhsip care Plans")
			survivorship_care_plans = [None]
		
		plans_found = len(valid_plans.intersection(survivorship_care_plans))
		
		if plans_found == 3:
			result = 1
		else:
			result =0

		print(survivorship_care_plans)
		return [patient['caseId'], result, plans_found]

	def QualityMeasure17A(self):

		patient = self.patient
		   
		try:
			had_ldr = True if (len(patient['prostateLdrTreatment']['prostateLdrPlan']) > 0) else False
		except:
			had_ldr = False

		try:
			dosimetry_eval = True if (patient['prostateLdrTreatment']['prostateLdrPlan'][0]['postTreatmentDosimetry'].lower() == 'yes') else False
		except:
			dosimetry_eval = False

		try:
			structures_evaluated = patient['prostateLdrTreatment']['prostateLdrPlan'][0]['postTreatmentEvaluation']
		except:
			structures_evaluated = ['nothing']

		post_treatment_valid_structures = set(['ct or mri', 'prostate v100', 'prostate d90', 'rectum v100', 'physician review'])

		is_all_structures = True if len(post_treatment_valid_structures.intersection(structures_evaluated)) ==  5 else False
		
		if not had_ldr:
			result = 2
		elif not dosimetry_eval or not is_all_structures:
			result = 0
		else:
			result = 1

		result = [patient['caseId'], result,  had_ldr, dosimetry_eval, structures_evaluated, is_all_structures]

		return result

	def QualityMeasure17B(self):

		patient = self.patient
		   
		try:
			had_ldr = True if (len(patient['prostateLdrTreatment']['prostateLdrPlan']) > 0) else False
		except:
			had_ldr = False

		try:
			post_txt_dosimetry_eval = True if (patient['prostateLdrTreatment']['prostateLdrPlan'][0]['postTreatmentDosimetry'].lower() == 'yes') else False
		except:
			post_txt_dosimetry_eval = False

		try:

			post_tx_dose_date = datetime.strptime(patient['prostateLdrTreatment']['prostateLdrPlan'][0]['postTreatmentDosimetryDate'], '%Y-%m-%d').date()
			logging.info('post_tx_dose_Date: {}'.format([post_tx_dose_date, patient['prostateLdrPlan'][0]['postTreatmentDosimetry']]))
		except:
			post_tx_dose_date = datetime.now().date()

		try:
			implant_date = datetime.strptime(patient['prostateLdrTreatment']['prostateLdrPlan'][0]['implantDate'], '%Y-%m-%d').date()
			
		except:
			implant_date = datetime.now().date()

		if not had_ldr:
			result = 2
		elif post_txt_dosimetry_eval  and (post_tx_dose_date <= (implant_date + timedelta(days=60))) and \
			  post_tx_dose_date != datetime.now().date() and implant_date != datetime.now().date():
			result = 1
		else:
			result = 0

		result =  [patient['caseId'], result,  had_ldr, post_txt_dosimetry_eval, post_tx_dose_date, implant_date]

		return result

	def QualityMeasure18(self):
		patient = self.patient
		#print('Needs to Inmplement the logic for this measure!!!!!!')

		return [patient['caseId'], 'Not for community!!']

	def QualityMeasure19(self):

		patient = self.patient

		qol_valid_instruments = ['aua', 'ipss', 'epic-26', 'iiem/shim']

		try:

			if 'qualityOfLifeEOT' in patient and 'qualityOfLifeScore' in patient['qualityOfLifeEOT']:
				logging.info(patient['qualityOfLifeEOT']['qualityOfLifeScore'])
				followup_notes = patient['qualityOfLifeEOT']['qualityOfLifeScore']

				qol_instruments = set([fnote['assessment'].lower()for fnote in followup_notes])
				qol_count = len(qol_instruments.intersection(qol_valid_instruments))

			elif 'qualityOfLifeEOT' not in patient:
				qol_count = -1
				qol_instruments = ['In try']
			else:
				qol_count = 0
				qol_instruments = ['Else of try!!']
				logging.info('not_found')
		except:
			qol_count = -1
			qol_instruments = [None]

		if qol_count > 0:
			result = 1
		elif qol_count == -1:
			result = 2
		else:
			result = 0

		print("PatienId:{}\t QoL_Count:{}\t Qol_Found:{}".format(patient['caseId'], qol_count, qol_instruments))
		result = [patient['caseId'], result,  qol_count]

		return result

	def QualityMeasure24(self):

		patient = self.patient
		current_date = datetime.now().date()

		try:
			if 'prostateAdt' in patient:
				adt_duration = True if patient['prostateAdt']['durationIntentOfADT'].lower() == 'long term' else False
			else:
				adt_duration = False
		except:
			adt_duration = False

		try:
			bone_density = True if patient['prostateImagingStudies']['boneDensityAssessment'].lower() == 'yes' else False
		except:
			bone_density = False

		try:
			logging.info(patient['prostateAdt'])
			adt_start_date = datetime.strptime(
				patient['prostateAdt']['prostateAdtInjection'][0]['adtInjectionDate'], '%Y-%m-%d').date()
		except:
			adt_start_date = current_date

		try:
			logging.info(patient['prostateImagingStudies']['boneDensityDate'])
			bone_density_date = datetime.strptime(
				patient['prostateImagingStudies']['boneDensityDate'], '%Y-%m-%d').date()
		except:
			bone_density_date = current_date

		logging.info(([adt_start_date - timedelta(days=90), bone_density_date, adt_start_date + timedelta(days=90)]))

		if not adt_duration:
			result = 2
		elif bone_density and \
				bone_density_date <= adt_start_date + timedelta(days=90) and \
				bone_density_date >= adt_start_date - timedelta(days=90) and \
				bone_density_date != current_date and \
				adt_start_date != current_date:
			result = 1
		else:
			result = 0

		result = ([patient['caseId'], result,  adt_duration,
				   adt_start_date, bone_density, bone_density_date])

		return result

	def QualityMeasureNumberOfNotesWithToxicityInitialized(self):

		patient = self.patient

		try:
			total_tox_notes = 0
			if 'otv' in patient:
				for item in patient['otv']:
					if 'otvAssessmentDate' and 'toxicity' in item:
						total_tox_notes +=1
		except:
			total_tox_notes = 0

		return [patient['caseId'], total_tox_notes]

	def QualityMeasureTotalNumberOfNotes(self):

		patient = self.patient

		try:
			total_notes = 0
			if 'otv' in patient:
				for item in patient['otv']:
					if 'otvAssessmentDate' in item:
						total_notes += 1
		except:
			total_notes = 0

		return [patient['caseId'], total_notes]

	def QualityMeasureGUWithGrade(self):

		patient = self.patient

		current_date = datetime(2100, 1, 1).date()
		valid_grades = ['grade 1', 'grade 2', 'grade 3', 'grade 4' , 'grade 5']

		try:
			tmt_end_date = self.GetTreatmentDate('end')
		except:
			tmt_end_date = current_date

		try:
			acutegu_withgrade = 0
			if 'otv' in patient:
				if 'toxicity' in patient['otv']:
					for note in patient['otv']['toxicity']:
						if (note['toxicity'].lower() == 'acute gu') and note['grade'].lower() in valid_grades and \
						(datetime.strptime(patient['otv']['otvAssessmentDate'], '%Y-%m-%d').date()) <= (tmt_end_date + timedelta(days=90)):
							acutegu_withgrade += 1
		except:
			acutegu_withgrade = 0

		result = [patient['caseId'], acutegu_withgrade]

		return result

	def QualityMeasureGUTotal(self):

		patient = self.patient
		current_date = datetime(2100, 1, 1).date()

		try:
			tmt_end_date = self.GetTreatmentDate('end')
		except:
			tmt_end_date = current_date

		try:
			acutegu_total = 0
			if 'otv' in patient:
				if 'toxicity' in patient['otv']:
					for note in patient['otv']['toxicity']:
						if note['toxicity'].lower() == ('acute gu') and \
							datetime.strptime(patient['otv']['otvAssessmentDate'], '%Y-%m-%d').date() <= (tmt_end_date + timedelta(days=90)):
							acutegu_total += 1
		except:
			acutegu_total = 0

		result = [patient['caseId'], acutegu_total]

		return result

	def QualityMeasureGIWithGrade(self):

		patient = self.patient

		current_date = datetime(2100, 1, 1).date()
		valid_grades = ['grade 1', 'grade 2', 'grade 3', 'grade 4' , 'grade 5']

		try:
			tmt_end_date = self.GetTreatmentDate('end')
		except:
			tmt_end_date = current_date

		try:
			acutegi_withgrade = 0
			if 'otv' in patient:
				if 'toxicity' in patient['otv']:
					for note in patient['otv']['toxicity']:
						if (note['toxicity'].lower() == 'acute gi') and note['grade'].lower() in valid_grades and \
						(datetime.strptime(patient['otv']['otvAssessmentDate'], '%Y-%m-%d').date()) <= (tmt_end_date + timedelta(days=90)):
							acutegi_withgrade += 1
		except:
			acutegi_withgrade = 0

		result = [patient['caseId'], acutegi_withgrade]

		return result

	def QualityMeasureGITotal(self):

		patient = self.patient
		current_date = datetime(2100, 1, 1).date()

		try:
			tmt_end_date = self.GetTreatmentDate('end')
		except:
			tmt_end_date = current_date

		try:
			acutegi_total = 0
			if 'otv' in patient:
				if 'toxicity' in patient['otv']:
					for note in patient['otv']['toxicity']:
						if note['toxicity'].lower() == ('acute gi') and \
							datetime.strptime(patient['otv']['otvAssessmentDate'], '%Y-%m-%d').date() <= (tmt_end_date + timedelta(days=90)):
							acutegi_total += 1
		except:
			acutegi_total = 0

		result = [patient['caseId'], acutegi_total]

		return result

	#####################################################
	# Different grades of toxicity needs to be measured #
	#####################################################

	# "NumberOfNotesWithToxicityInitialized" : None,
	# "TotalNumberOfNotes" : None,
	# "AcuteGUWithGrade" : None,
	# "AcuteGUTotal" : None,
	# "LateGUWithGrade" : None,
	# "LateGUTotal" : None,
	# "AcuteGIWithGrade" : None,
	# "AcuteGITotal" : None,
	# "LateGIWithGrade" : None,
	# "LateGITotal" : None,

	# "AcuteGUWithGrade" : None,
	# "AcuteGUTotal" : None,

	# "LateGUWithGrade" : None,
	# "LateGUTotal" : None,

	# "AcuteGIWithGrade" : None,
	# "AcuteGITotal" : None,

	# "LateGIWithGrade" : None,
	# "LateGITotal" : None,

	fdict = {
		'QualityMeasure1': QualityMeasure1,
		'QualityMeasure2': QualityMeasure2,
		'QualityMeasure3': QualityMeasure3,
		'QualityMeasure4': QualityMeasure4,
		'QualityMeasure5': QualityMeasure5,
		'QualityMeasure6': QualityMeasure6,
		'QualityMeasure7': QualityMeasure7,
		'QualityMeasure8': QualityMeasure8,
		'QualityMeasure9': QualityMeasure9,
		'QualityMeasure10': QualityMeasure10,
		'QualityMeasure11': QualityMeasure11,
		'QualityMeasure12': QualityMeasure12,
		'QualityMeasure13':QualityMeasure13,
		'QualityMeasure14': QualityMeasure14,
		'QualityMeasure15': QualityMeasure15,
		'QualityMeasure15_color': QualityMeasure15_color,
		'QualityMeasure16':QualityMeasure16,
		'QualityMeasure17A': QualityMeasure17A,
		'QualityMeasure17B': QualityMeasure17B,
		# 'QualityMeasure18':QualityMeasure18,
		'QualityMeasure19': QualityMeasure19,
		'QualityMeasure24': QualityMeasure24,
		'NumberOfNotesWithToxicityInitialized':QualityMeasureNumberOfNotesWithToxicityInitialized,
		'TotalNumberOfNotes':QualityMeasureTotalNumberOfNotes,
		'AcuteGUWithGrade': QualityMeasureGUWithGrade,
		'AcuteGUTotal': QualityMeasureGUTotal,
		'AcuteGIWithGrade': QualityMeasureGIWithGrade,
		'AcuteGITotal': QualityMeasureGITotal,
	}
