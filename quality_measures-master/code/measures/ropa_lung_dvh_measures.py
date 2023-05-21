from pymongo import MongoClient
from datetime import datetime, timedelta
from collections import OrderedDict

from .measure import Measure

class LungDVHMeasure(Measure):

		def __init__(self):
			#print("Implemented Lung DVH Measures")
			pass


		measures = OrderedDict({
			'vha_id':None, 
			'esophagus_D0-dot-035cc':None,
			'esophagus_DMax':None,
			'esophagus_DMean':None,
			'esophagus_V60Gy':None,
			'heart_V45Gy':None,
			'lung_total - lung_subtraction_structure (lung_total - lung_subtraction_structure)_DMean':None,
			'lung_total - lung_subtraction_structure (lung_total - lung_subtraction_structure)_V20Gy':None,
			'lung_total - lung_subtraction_structure (lung_total - lung_subtraction_structure)_V5Gy':None,
			'lung_total_already_subtracted_DMean':None,
			'lung_total_already_subtracted_V20Gy':None,
			'lung_total_already_subtracted_V5Gy':None,
			'ptv_D95%':None,
			'ptv_DMin':None,
			'spinalcord_D0-dot-035cc':None,
			'spinalcord_DMax':None,
			'LU_DVH_28':None,
			'LU_DVH_24':None,
			'LU_DVH_26':None,
			'lung_ipsi + lung_contra - lung_subtraction_structure ((lung_ipsi + lung_contra) - lung_subtraction_structure)_DMean':None,
			'lung_ipsi + lung_contra - lung_subtraction_structure ((lung_ipsi + lung_contra) - lung_subtraction_structure)_V20Gy':None,
			'lung_ipsi + lung_contra - lung_subtraction_structure ((lung_ipsi + lung_contra) - lung_subtraction_structure)_V5Gy':None,
			'LU_DVH_27':None,
			'LU_DVH_23':None,
			'LU_DVH_25':None,
			'brachialplexus_D0-dot-035cc':None,
			'brachialplexus_DMax':None,
			'lung_contra_already_subtracted_DMean':None,
			'lung_contra_already_subtracted_V20Gy':None,
			'lung_contra_already_subtracted_V5Gy':None,
			'lung_ipsi_already_subtracted_DMean':None,
			'lung_ipsi_already_subtracted_V20Gy':None,
			'lung_ipsi_already_subtracted_V5Gy':None,
			'lung_ipsi_already_subtracted + lung_contra_already_subtracted (lung_ipsi_already_subtracted + lung_contra_already_subtracted)_DMean':None,
			'lung_ipsi_already_subtracted + lung_contra_already_subtracted (lung_ipsi_already_subtracted + lung_contra_already_subtracted)_V20Gy':None,
			'lung_ipsi_already_subtracted + lung_contra_already_subtracted (lung_ipsi_already_subtracted + lung_contra_already_subtracted)_V5Gy':None
			})


		def esophagus_D0035cc(self):
			patient = self.patient

			try:
				eso_d0035cc_value = float(patient['Esophagus_D0-dot-035cc'])
			except:
				eso_d0035cc_value = ""

			if eso_d0035cc_value == "":
				result = ""
			elif 66.6 < eso_d0035cc_value <= 74:
				result = 'Yellow'
			elif (eso_d0035cc_value <= 74):
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def esophagus_DMax(self):
			patient = self.patient

			try:
				eso_max_value = float(patient['Esophagus_DMax'])
			except:
				eso_max_value = ""

			if eso_max_value == "":
				result = ""
			elif 66.6 < eso_max_value <= 74:
				result = 'Yellow'
			elif (eso_max_value <= 74):
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def esophagus_DMean(self):
			patient = self.patient

			try:
				eso_mean_value = float(patient['Esophagus_DMean'])
			except:
				eso_mean_value = ""

			if eso_mean_value == "":
				result = ""
			elif 30.6 < eso_mean_value <= 34:
				result = 'Yellow'
			elif (eso_mean_value <= 34):
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def esophagus_V60Gy(self):
			patient = self.patient

			try:
				eso_v60_value = float(patient['Esophagus_V60Gy'])
			except:
				eso_v60_value = ""

			if eso_v60_value == "":
				result = ""
			elif 15.3 < eso_v60_value <= 17:
				result = 'Yellow'
			elif (eso_v60_value <= 17):
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def heart_V45Gy(self):
			patient = self.patient

			try:
				heart_v45_value = float(patient['Heart_V45Gy'])
			except:
				heart_v45_value = ""

			if heart_v45_value == "":
				result = "" 
			elif 31.5 < heart_v45_value <= 35:
				result = 'Yellow'
			elif heart_v45_value <= 35:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_total_DMean(self):
			patient = self.patient

			try:
				lung_total_dmean_value = float(patient['Lung_Total - Lung_Subtraction_Structure (Lung_Total - Lung_Subtraction_Structure)_DMean'])
			except:
				lung_total_dmean_value = ""

			if lung_total_dmean_value == "":
				result = "" 
			elif 18 < lung_total_dmean_value <= 20:
				result = 'Yellow'
			elif lung_total_dmean_value <= 20:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_total_V20Gy(self):
			patient = self.patient

			try:
				lung_total_v20_value = float(patient['Lung_Total - Lung_Subtraction_Structure (Lung_Total - Lung_Subtraction_Structure)_V20Gy'])
			except:
				lung_total_v20_value = ""

			if lung_total_v20_value == "":
				result = "" 
			elif 33 < lung_total_v20_value <= 37:
				result = 'Yellow'
			elif lung_total_v20_value <= 37:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_total_V5Gy(self):
			patient = self.patient

			try:
				lung_total_v5_value = float(patient['Lung_Total - Lung_Subtraction_Structure (Lung_Total - Lung_Subtraction_Structure)_V5Gy'])
			except:
				lung_total_v5_value = ""

			if lung_total_v5_value == "":
				result = "" 
			elif 54 < lung_total_v5_value <= 60:
				result = 'Yellow'
			elif lung_total_v5_value <= 60:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_total_already_DMean(self):
			patient = self.patient

			try:
				lung_total_already_dmean_value = float(patient['Lung_Total_Already_Subtracted_DMean'])
			except:
				lung_total_already_dmean_value = ""

			if lung_total_already_dmean_value == "":
				result = "" 
			elif 18 < lung_total_already_dmean_value <= 20:
				result = 'Yellow'
			elif lung_total_already_dmean_value <= 20:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_total_already_V20Gy(self):
			patient = self.patient

			try:
				lung_total_already_v20_value = float(patient['Lung_Total_Already_Subtracted_V20Gy'])
			except:
				lung_total_already_v20_value = ""

			if lung_total_already_v20_value == "":
				result = "" 
			elif 33 < lung_total_already_v20_value <= 37:
				result = 'Yellow'
			elif lung_total_already_v20_value <= 37:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]

		def lung_total_already_V5Gy(self):
			patient = self.patient

			try:
				lung_total_already_v5_value = float(patient['Lung_Total_Already_Subtracted_V5Gy'])
			except:
				lung_total_already_v5_value = ""

			if lung_total_already_v5_value == "":
				result = "" 
			elif 54 < lung_total_already_v5_value <= 60:
				result = 'Yellow'
			elif lung_total_already_v5_value <= 60:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def ptv_D95(self):
			patient = self.patient

			try:
				ptv_d95_value = float(patient['PTV_D95%'])
			except:
				ptv_d95_value = ""

			if ptv_d95_value == "":
				result = "" 
			elif 95 <= ptv_d95_value < 100:
				result = 'Yellow'
			elif ptv_d95_value >= 100:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def ptv_DMin(self):
			patient = self.patient

			try:
				ptv_dmin_value = float(patient['PTV_DMin'])
			except:
				ptv_dmin_value = ""

			if ptv_dmin_value == "":
				result = "" 
			elif 75 <= ptv_dmin_value < 85:
				result = 'Yellow'
			elif ptv_dmin_value >= 85:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def spinalcord_D0035cc(self):
			patient = self.patient

			try:
				spinal_d0035_value = float(patient['SpinalCord_D0-dot-035cc'])
			except:
				spinal_d0035_value = ""

			if spinal_d0035_value == "":
				result37 = ""
				result41 = ""
				result42 = ""
				result50 = ""
			else:
				result37 = "Red"
				result41 = "Red"
				result42 = "Red"
				result50 = "Red"

				if spinal_d0035_value <= 33.3:	
					result37 = "Green"
				if 33.3 < spinal_d0035_value <= 37:
					result37 = 'Yellow'
				if spinal_d0035_value <= 41:
					result41 = "Green"
				if 36.9 < spinal_d0035_value <= 41:
					result41 = 'Yellow'
				if spinal_d0035_value <= 37.8:
					result42 = "Green"
				if 37.8 < spinal_d0035_value <= 42:
					result42 = 'Yellow'
				if spinal_d0035_value <= 45:
					result50 = "Green"
				if 45 < spinal_d0035_value <= 50:
					result50 = 'Yellow'

			result = [patient['vha_id'], result37, result41, result42, result50]

			return result[1]

		def spinalcord_DMax(self):
			patient = self.patient

			try:
				spinal_dmax_value = float(patient['SpinalCord_DMax'])
			except:
				spinal_dmax_value = ""

			if spinal_dmax_value == "":
				result37 = ""
				result41 = ""
				result42 = ""
				result50 = ""
			else:
				result37 = "Red"
				result41 = "Red"
				result42 = "Red"
				result50 = "Red"

				if spinal_dmax_value <= 33.3:	
					result37 = 'Green'
				if 33.3 < spinal_dmax_value <= 37:
					result37 = 'Yellow'
				if spinal_dmax_value <= 41:
					result41 = 'Green'
				if 36.9 < spinal_dmax_value <= 41:
					result41 = 'Yellow'
				if spinal_dmax_value <= 37.8:
					result42 = 'Green'
				if 37.8 < spinal_dmax_value <= 42:
					result42 = 'Yellow'
				if spinal_dmax_value <= 45:
					result50 = 'Green'
				if 45 < spinal_dmax_value <= 50:
					result50 = 'Yellow'

			result = [patient['vha_id'], result37, result41, result42, result50]

			return result[1]

			
		def lung_contra_DMean(self):
			patient = self.patient

			#Lung_Contra - Lung_Subtraction_Structure (Lung_Contra - Lung_Subtraction_Structure)_DMean
			#LU_DVH_28

			try:
				lung_contra_dmean_value = float(patient['LU_DVH_28'])
			except:
				lung_contra_dmean_value = ""

			if lung_contra_dmean_value == "":
				result = "" 
			elif 7.7 < lung_contra_dmean_value <= 8.5:
				result = 'Yellow'
			elif lung_contra_dmean_value <= 8.5:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]

		def lung_contra_V20Gy(self):
			patient = self.patient

			#lung_contra - lung_subtraction_structure (lung_contra - lung_subtraction_structure)_V20Gy
			#LU_DVH_24

			try:
				lung_contra_v20_value = float(patient['LU_DVH_24'])
			except:
				lung_contra_v20_value = ""

			if lung_contra_v20_value == "":
				result = "" 
			elif 6.3 < lung_contra_v20_value <= 7:
				result = 'Yellow'
			elif lung_contra_v20_value <= 7:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]

		def lung_contra_V5Gy(self):
			patient = self.patient

			#Lung_Contra - Lung_Subtraction_Structure (Lung_Contra - Lung_Subtraction_Structure)_V5Gy
			#LU_DVH_26

			try:
				lung_contra_v5_value = float(patient['LU_DVH_26'])
			except:
				lung_contra_v5_value = ""

			if lung_contra_v5_value == "":
				result = "" 
			elif 54 < lung_contra_v5_value <= 60:
				result = 'Yellow'
			elif lung_contra_v5_value <= 60:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_ipsi_DMean(self):
			patient = self.patient

			try:
				lung_ipsi_dmean_value = float(patient['Lung_Ipsi + Lung_Contra - Lung_Subtraction_Structure ((Lung_Ipsi + Lung_Contra) - Lung_Subtraction_Structure)_DMean'])
			except:
				lung_ipsi_dmean_value = ""

			if lung_ipsi_dmean_value == "":
				result = "" 
			elif 18 < lung_ipsi_dmean_value <= 20:
				result = 'Yellow'
			elif lung_ipsi_dmean_value <= 20:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_ipsi_V20Gy(self):
			patient = self.patient

			try:
				lung_ipsi_v20_value = float(patient['Lung_Ipsi + Lung_Contra - Lung_Subtraction_Structure ((Lung_Ipsi + Lung_Contra) - Lung_Subtraction_Structure)_V20Gy'])
			except:
				lung_ipsi_v20_value = ""

			if lung_ipsi_v20_value == "":
				result = "" 
			elif 33 < lung_ipsi_v20_value <= 37:
				result = 'Yellow'
			elif lung_ipsi_v20_value <= 37:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]
	 

		def lung_ipsi_V5Gy(self):
			patient = self.patient

			try:
				lung_ipsi_v5_value = float(patient['Lung_Ipsi + Lung_Contra - Lung_Subtraction_Structure ((Lung_Ipsi + Lung_Contra) - Lung_Subtraction_Structure)_V5Gy'])
			except:
				lung_ipsi_v5_value = ""

			if lung_ipsi_v5_value == "":
				result = "" 
			elif 54 < lung_ipsi_v5_value <= 60:
				result = 'Yellow'
			elif lung_ipsi_v5_value <= 60:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]

		def lung_ipsi_sub_DMean(self):
			patient = self.patient

			#Lung_Ipsi - Lung_Subtraction_Structure (Lung_Ipsi - Lung_Subtraction_Structure)_DMean
			#LU_DVH_27

			try:
				lung_ipsi_sub_dmean_value = float(patient['LU_DVH_27'])
			except:
				lung_ipsi_sub_dmean_value = ""

			if lung_ipsi_sub_dmean_value == "":
				result = "" 
			elif 7.7 < lung_ipsi_sub_dmean_value <= 8.5:
				result = 'Yellow'
			elif lung_ipsi_sub_dmean_value <= 8.5:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_ipsi_sub_V20Gy(self):
			patient = self.patient

			#Lung_Ipsi - Lung_Subtraction_Structure (Lung_Ipsi - Lung_Subtraction_Structure)_V20Gy
			#LU_DVH_23

			try:
				lung_ipsi_sub_v20_value = float(patient['LU_DVH_23'])
			except:
				lung_ipsi_sub_v20_value = ""

			if lung_ipsi_sub_v20_value == "":
				result = "" 
			elif 6.3 < lung_ipsi_sub_v20_value <= 7:
				result = 'Yellow'
			elif lung_ipsi_sub_v20_value <= 7:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_ipsi_sub_V5Gy(self):
			patient = self.patient

			#Lung_Ipsi - Lung_Subtraction_Structure (Lung_Ipsi - Lung_Subtraction_Structure)_V5Gy
			#LU_DVH_25

			try:
				lung_ipsi_sub_v5_value = float(patient['LU_DVH_25'])
			except:
				lung_ipsi_sub_v5_value = ""

			if lung_ipsi_sub_v5_value == "":
				result = "" 
			elif 54 < lung_ipsi_sub_v5_value <= 60:
				result = 'Yellow'
			elif lung_ipsi_sub_v5_value <= 60:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def brachialplexus_D0035cc(self):
			patient = self.patient

			try:
				brachial_d0035_value = float(patient['BrachialPlexus_D0-dot-035cc'])
			except:
				brachial_d0035_value = ""

			if brachial_d0035_value == "":
				result = "" 
			elif 59.4 < brachial_d0035_value <= 66:
				result = 'Yellow'
			elif brachial_d0035_value <= 66:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def brachialplexus_DMax(self):
			patient = self.patient

			try:
				brachial_dmax_value = float(patient['BrachialPlexus_DMax'])
			except:
				brachial_dmax_value = ""

			if brachial_dmax_value == "":
				result = "" 
			elif 59.4 < brachial_dmax_value <= 66:
				result = 'Yellow'
			elif brachial_dmax_value <= 66:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_contra_already_DMean(self):
			patient = self.patient

			try:
				lung_contra_already_dmean_value = float(patient['Lung_Contra_Already_Subtracted_DMean'])
			except:
				lung_contra_already_dmean_value = ""

			if lung_contra_already_dmean_value == "":
				result = "" 
			elif 7.7 < lung_contra_already_dmean_value <= 8.5:
				result = 'Yellow'
			elif lung_contra_already_dmean_value <= 8.5:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_contra_already_V20Gy(self):
			patient = self.patient

			try:
				lung_contra_already_v20_value = float(patient['Lung_Contra_Already_Subtracted_V20Gy'])
			except:
				lung_contra_already_v20_value = ""

			if lung_contra_already_v20_value == "":
				result = "" 
			elif 6.3 < lung_contra_already_v20_value <= 7:
				result = 'Yellow'
			elif lung_contra_already_v20_value <= 7:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_contra_already_V5Gy(self):
			patient = self.patient

			try:
				lung_contra_already_v5_value = float(patient['Lung_Contra_Already_Subtracted_V5Gy'])
			except:
				lung_contra_already_v5_value = ""

			if lung_contra_already_v5_value == "":
				result = "" 
			elif 54 < lung_contra_already_v5_value <= 60:
				result = 'Yellow'
			elif lung_contra_already_v5_value <= 60:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_ipsi_already_DMean(self):
			patient = self.patient

			try:
				lung_ipsi_already_dmean_value = float(patient['Lung_Ipsi_Already_Subtracted_DMean'])
			except:
				lung_ipsi_already_dmean_value = ""

			if lung_ipsi_already_dmean_value == "":
				result = "" 
			elif 7.7 < lung_ipsi_already_dmean_value <= 8.5:
				result = 'Yellow'
			elif lung_ipsi_already_dmean_value <= 8.5:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_ipsi_already_V20Gy(self):
			patient = self.patient

			try:
				lung_ipsi_already_v20_value = float(patient['Lung_Ipsi_Already_Subtracted_V20Gy'])
			except:
				lung_ipsi_already_v20_value = ""

			if lung_ipsi_already_v20_value == "":
				result = "" 
			elif 6.3 < lung_ipsi_already_v20_value <= 7:
				result = 'Yellow'
			elif lung_ipsi_already_v20_value <= 7:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_ipsi_already_V5Gy(self):
			patient = self.patient

			try:
				lung_ipsi_already_v5_value = float(patient['Lung_Ipsi_Already_Subtracted_V5Gy'])
			except:
				lung_ipsi_already_v5_value = ""

			if lung_ipsi_already_v5_value == "":
				result = "" 
			elif 54 < lung_ipsi_already_v5_value <= 60:
				result = 'Yellow'
			elif lung_ipsi_already_v5_value <= 60:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_ipsi_contra_already_DMean(self):
			patient = self.patient

			try:
				lung_ipsi_contra_already_dmean_value = float(patient['Lung_Ipsi_Already_Subtracted + Lung_Contra_Already_Subtracted (Lung_Ipsi_Already_Subtracted + Lung_Contra_Already_Subtracted)_DMean'])
			except:
				lung_ipsi_contra_already_dmean_value = ""

			if lung_ipsi_contra_already_dmean_value == "":
				result = "" 
			elif 18 < lung_ipsi_contra_already_dmean_value <= 20:
				result = 'Yellow'
			elif lung_ipsi_contra_already_dmean_value <= 20:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_ipsi_contra_already_V20Gy(self):
			patient = self.patient

			try:
				lung_ipsi_contra_already_v20_value = float(patient['Lung_Ipsi_Already_Subtracted + Lung_Contra_Already_Subtracted (Lung_Ipsi_Already_Subtracted + Lung_Contra_Already_Subtracted)_V20Gy'])
			except:
				lung_ipsi_contra_already_v20_value = ""

			if lung_ipsi_contra_already_v20_value == "":
				result = "" 
			elif 33 < lung_ipsi_contra_already_v20_value <= 37:
				result = 'Yellow'
			elif lung_ipsi_contra_already_v20_value <= 37:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		def lung_ipsi_contra_already_V5Gy(self):
			patient = self.patient

			try:
				lung_ipsi_contra_already_v5_value = float(patient['Lung_Ipsi_Already_Subtracted + Lung_Contra_Already_Subtracted (Lung_Ipsi_Already_Subtracted + Lung_Contra_Already_Subtracted)_V5Gy'])
			except:
				lung_ipsi_contra_already_v5_value = ""

			if lung_ipsi_contra_already_v5_value == "":
				result = "" 
			elif 54 < lung_ipsi_contra_already_v5_value <= 60:
				result = 'Yellow'
			elif lung_ipsi_contra_already_v5_value <= 60:
				result = 'Green'
			else:
				result = 'Red'

			result = [patient['vha_id'], result]

			return result[1]


		fdict = {
			'esophagus_D0-dot-035cc':esophagus_D0035cc,
			'esophagus_DMax':esophagus_DMax,
			'esophagus_DMean':esophagus_DMean,
			'esophagus_V60Gy':esophagus_V60Gy,
		 	'heart_V45Gy':heart_V45Gy,
		 	'lung_total - lung_subtraction_structure (lung_total - lung_subtraction_structure)_DMean':lung_total_DMean,
		 	'lung_total - lung_subtraction_structure (lung_total - lung_subtraction_structure)_V20Gy':lung_total_V20Gy,
		 	'lung_total - lung_subtraction_structure (lung_total - lung_subtraction_structure)_V5Gy':lung_total_V5Gy,
		 	'lung_total_already_subtracted_DMean':lung_total_already_DMean,
		 	'lung_total_already_subtracted_V20Gy':lung_total_already_V20Gy,
		 	'lung_total_already_subtracted_V5Gy':lung_total_already_V5Gy,
		 	'ptv_D95%':ptv_D95,
		 	'ptv_DMin':ptv_DMin,
		 	'spinalcord_D0-dot-035cc':spinalcord_D0035cc,
		 	'spinalcord_DMax':spinalcord_DMax,
		 	'LU_DVH_28':lung_contra_DMean,
		 	'LU_DVH_24':lung_contra_V20Gy,
		 	'LU_DVH_26':lung_contra_V5Gy,
		 	'lung_ipsi + lung_contra - lung_subtraction_structure ((lung_ipsi + lung_contra) - lung_subtraction_structure)_DMean':lung_ipsi_DMean,
		 	'lung_ipsi + lung_contra - lung_subtraction_structure ((lung_ipsi + lung_contra) - lung_subtraction_structure)_V20Gy':lung_ipsi_V20Gy,
		 	'lung_ipsi + lung_contra - lung_subtraction_structure ((lung_ipsi + lung_contra) - lung_subtraction_structure)_V5Gy':lung_ipsi_V5Gy,
		 	'LU_DVH_27':lung_ipsi_sub_DMean,
		 	'LU_DVH_23':lung_ipsi_sub_V20Gy,
		 	'LU_DVH_25':lung_ipsi_sub_V5Gy,
		 	'brachialplexus_D0-dot-035cc':brachialplexus_D0035cc,
		 	'brachialplexus_DMax':brachialplexus_DMax,
			'lung_contra_already_subtracted_DMean':lung_contra_already_DMean,
		 	'lung_contra_already_subtracted_V20Gy':lung_contra_already_V20Gy,
		 	'lung_contra_already_subtracted_V5Gy':lung_contra_already_V5Gy,
		 	'lung_ipsi_already_subtracted_DMean':lung_ipsi_already_DMean,
		 	'lung_ipsi_already_subtracted_V20Gy':lung_ipsi_already_V20Gy,
		 	'lung_ipsi_already_subtracted_V5Gy':lung_ipsi_already_V5Gy,
		 	'lung_ipsi_already_subtracted + lung_contra_already_subtracted (lung_ipsi_already_subtracted + lung_contra_already_subtracted)_DMean':lung_ipsi_contra_already_DMean,
		 	'lung_ipsi_already_subtracted + lung_contra_already_subtracted (lung_ipsi_already_subtracted + lung_contra_already_subtracted)_V20Gy':lung_ipsi_contra_already_V20Gy,
		 	'lung_ipsi_already_subtracted + lung_contra_already_subtracted (lung_ipsi_already_subtracted + lung_contra_already_subtracted)_V5Gy':lung_ipsi_contra_already_V5Gy,
		  }
