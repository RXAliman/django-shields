from django.apps import AppConfig


class MasterlistConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'masterlist'
	
	def ready(self):
		import masterlist.signals