import numpy as np
from pymongo import MongoClient
from datetime import datetime, timedelta
import logging

class Measure:
	db_name = None
	read_collection = None
	write_collection = None
	patient = None
	sub_measure_collection = None

	logger = logging.getLogger(__name__)
	logging.basicConfig(filename = 'ropa_logging.log', level = logging.INFO,
						format='%(asctime)s:%(levelname)s:%(message)s')

	def __init__(self):
		pass

	def str_to_date(self, date_string):
		year, month, day = map(int, date_string.split('-'))
		return datetime(year, month, day).date()

	def set_db_name(self, db_name):
		self.db_name = db_name

	def set_read_collection_name(self, name):
		self.read_collection = name

	def set_write_collection_name(self, name):
		self.write_collection = name

	def set_sub_measure_collection_name(self, name):
		self.sub_measure_collection = name

	def reset_db_name(self):
		self.db_name = None

	def reset_read_collection_name(self):
		self.read_collection = None

	def reset_write_collection_name(self):
		self.write_collection = None

	def reset_measures(self):
		self.prostate_measures = self.prostate_measures.fromkeys(self.prostate_measures, None)

	def get_db_connection(self, collection_name):
		client = MongoClient()
		db = client[self.db_name]
		collection = db[collection_name]

		return collection

	def db_put_measures(self, collect, record, subdoc_id):

		collect.update_one(
							{'vha_id':record[subdoc_id]['vha_id']},
							{'$set':record},
							upsert=True
						)