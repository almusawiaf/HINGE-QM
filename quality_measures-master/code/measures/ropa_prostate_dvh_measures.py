from pymongo import MongoClient
from datetime import datetime, timedelta
from collections import OrderedDict
from .measure import Measure

class ProstateDVHMeasure(Measure):
	
	patient = None

	measures = OrderedDict({
		"center_id": None,
		"center_name": None,
		"vha_id": None,
		"Bladder_V65Gy": None,
		"Bladder_V70Gy": None,
		"Femur_L_V50Gy": None,
		"Femur_R_V50Gy": None,
		"PTV_D2%": None,
		"PTV_V100% Rx1": None,
		"Rectum_V50Gy": None,
		"Rectum_V69Gy": None,
		"Rectum_V70Gy": None,
		"Rectum_V75Gy": None,
		"LargeBowel_D0-dot-035cc": None,
		"LargeBowel_DMax": None,
		"Bladder - Bladder_Subtraction_Structure (Bladder - Bladder_Subtraction_Structure)_V40Gy": None,
		"Bladder - Bladder_Subtraction_Structure (Bladder - Bladder_Subtraction_Structure)_V65Gy": None,
		"Bladder_Already_Subtracted_V40Gy": None,
		"Bladder_Already_Subtracted_V65Gy": None,
		"Rectum_V40Gy": None,
		"Rectum_V65Gy": None,
		"SmallBowel_D0-dot-035cc": None,
		"SmallBowel_DMax": None, 
		"SmallBowel_V45Gy": None 
	})

	def QualityMeasure1(self):
		
		patient = self.patient
		
		try:
			if patient['Bladder_V65Gy'] <= 50:
				return 'Green' 
			else:
				return 'Red'
		except:
			return ''


	def QualityMeasure2(self):
		
		patient = self.patient 

		try:
			if patient['Bladder_V70Gy'] <= 35:
				return 'Green'
			else:
				return 'Red'
		except:
			return '' 

	def QualityMeasure3(self):

		patient = self.patient

		try:
			if patient['Femur_L_V50Gy'] <= 10:
				return 'Green'
			else:
				return 'Red'
		except:
			return '' 

	def QualityMeasure4(self):

		patient = self.patient 
		try:
			if patient['Femur_R_V50Gy'] <= 10:
				return 'Green'
			else:
				return 'Red'
		except:
			return '' 

	def QualityMeasure5(self):
		
		patient = self.patient 
		try:
			if patient['PTV_D2%'] <= 110: 
				return 'Green'
			elif 110 < patient['PTV_D2%'] <= 115: 
				return 'Yellow'
			else:
				return 'Red'
		except:
			return ''

	def QualityMeasure6(self):
		
		patient = self.patient 
		try:
			if patient['PTV_V100% Rx1'] >= 95: 
				return 'Green'
			elif 90 <= patient['PTV_V100% Rx1'] < 95: 
				return 'Yellow'
			else:
				return 'Red'
		except:
			return ''

	def QualityMeasure7(self):
		
		patient = self.patient
		try:
			if patient['Rectum_V50Gy'] <= 50: 
				return 'Green'
			else:
				return 'Red'
		except:
			return ''

	def QualityMeasure8(self):
		
		patient = self.patient 
		
		try:
			if patient['Rectum_V69Gy'] <= 25: 
				return 'Green'
			else:
				return 'Red'
		except:
			return ''

	def QualityMeasure9(self):
		patient = self.patient 

		try:
			if patient['Rectum_V70Gy'] <= 15: 
				return 'Green'
			else:
				return 'Red'
		except:
			return ''

	def QualityMeasure10(self):

		patient = self.patient

		try:
			if patient['Rectum_V75Gy'] <= 10: 
				return 'Green'
			else:
				return 'Red'
		except:
			return ''
	
	def QualityMeasure11(self):

		patient = self.patient 
		
		try:
			if patient['LargeBowel_D0-dot-035cc'] <= 60: 
				return 'Green'
			else:
				return 'Red'
		except:
			return ''
	
	def QualityMeasure12(self):

		patient = self.patient 
		try:
			if patient['LargeBowel_DMax'] <= 60: 
				return 'Green'
			else:
				return 'Red'
		except:
			return ''

	def QualityMeasure13(self):

		patient = self.patient 
		try:
			if patient['Bladder - Bladder_Subtraction_Structure (Bladder - Bladder_Subtraction_Structure)_V40Gy'] <= 40: 
				return 'Green'
			elif 40 < patient['Bladder - Bladder_Subtraction_Structure (Bladder - Bladder_Subtraction_Structure)_V40Gy'] <= 60:
				return 'Yellow'
			else:
				return 'Red'
		except:
			return ''

	def QualityMeasure14(self):

		patient = self.patient 

		try:
			if patient['Bladder - Bladder_Subtraction_Structure (Bladder - Bladder_Subtraction_Structure)_V65Gy'] <= 40: 
				return 'Green'
			elif 40 < patient['Bladder - Bladder_Subtraction_Structure (Bladder - Bladder_Subtraction_Structure)_V65Gy'] <= 60:
				return 'Yellow'
			else:
				return 'Red'
		except:
			return ''

	def QualityMeasure15(self):

		patient = self.patient 
		
		try:
			if patient['Bladder_Already_Subtracted_V40Gy'] <= 40: 
				return 'Green'
			elif 40 < patient['Bladder_Already_Subtracted_V40Gy'] <= 60:
				return 'Yellow'
			else:
				return 'Red'
		except:
			return ''

	def QualityMeasure16(self):
		
		patient = self.patient 

		try:
			if patient['Bladder_Already_Subtracted_V65Gy'] <= 40: 
				return 'Green'
			elif 40 < patient['Bladder_Already_Subtracted_V65Gy'] <= 60:
				return 'Yellow'
			else:
				return 'Red'
		except:
			return ''

	def QualityMeasure17(self):

		patient = self.patient 

		try:
			if patient['Rectum_V40Gy'] <= 45: 
				return 'Green'
			else:
				return 'Red'
		except:
			return ''
	
	def QualityMeasure18(self):

		patient = self.patient 

		try:
			if patient['Rectum_V65Gy'] <= 25: 
				return 'Green'
			else:
				return 'Red'
		except:
			return ''
	
	def QualityMeasure19(self):

		patient = self.patient 

		try:
			if patient['SmallBowel_D0-dot-035cc'] <= 50: 
				return 'Green'
			else:
				return 'Red'
		except:
			return ''
	
	def QualityMeasure20(self):

		patient = self.patient 

		try:
			if patient['SmallBowel_DMax'] < 50: 
				return 'Green'
			else:
				return 'Red'
		except:
			return ''
		
	def QualityMeasure21(self):

		patient = self.patient 

		try:
			if patient['SmallBowel_V45Gy'] <= 200: 
				return 'Green'
			else:
				return 'Red'
		except:
			return ''

	fdict = {
		'Bladder_V65Gy' : QualityMeasure1,
		'Bladder_V70Gy' : QualityMeasure2,
		'Femur_L_V50Gy' : QualityMeasure3,
		'Femur_R_V50Gy' : QualityMeasure4,
		'PTV_D2%' : QualityMeasure5,
		'PTV_V100% Rx1' : QualityMeasure6,
		'Rectum_V50Gy' : QualityMeasure7,
		'Rectum_V69Gy' : QualityMeasure8,
		'Rectum_V70Gy' : QualityMeasure9,
		'Rectum_V75Gy' : QualityMeasure10,
		'LargeBowel_D0-dot-035cc' : QualityMeasure11,
		'LargeBowel_DMax' : QualityMeasure12,
		'Bladder - Bladder_Subtraction_Structure (Bladder - Bladder_Subtraction_Structure)_V40Gy' : QualityMeasure13,
		'Bladder - Bladder_Subtraction_Structure (Bladder - Bladder_Subtraction_Structure)_V65Gy' : QualityMeasure14,
		'Bladder_Already_Subtracted_V40Gy' : QualityMeasure15,
		'Bladder_Already_Subtracted_V65Gy' : QualityMeasure16,
		'Rectum_V40Gy' : QualityMeasure17,
		'Rectum_V65Gy' : QualityMeasure18,
		'SmallBowel_D0-dot-035cc' : QualityMeasure19,
		'SmallBowel_DMax' : QualityMeasure20,
		'SmallBowel_V45Gy' : QualityMeasure21,
	}