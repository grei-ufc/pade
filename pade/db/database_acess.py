from twisted.enterprise import adbapi

class DataBaseAcess(object):
	def __init__(self, name = 'database'):
		self.database_name = name

	def _create_agents_table(self, transaction, name):
		pass

	def create_agents_table(self, name):
		pass

	def insert_agent(self, ):
		pass

dbpool = adbapi.ConnectionPool('sqlite3', DATABASE_NAME + '.db')
