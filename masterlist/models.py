from django.db import models


# Create your models here.	
class Person(models.Model):
	person_id = models.CharField(max_length=11, primary_key=True) # e.g. 1-0001-2023 (First Street, Entry #1, Registered on 2023)
	person_surname = models.CharField(max_length=30) 
	person_firstname = models.CharField(max_length=100)
	person_middlename = models.CharField(max_length=30, null=True)
	person_extension = models.CharField(max_length=5, null=True)
	person_street_no = models.IntegerField() # 1,2,3 or 4
	person_house_no = models.CharField(max_length=5, null=True)
	person_status = models.CharField(max_length=20) # Resident, Pending, Member
	
	def __str__(self):
		return self.person_id
	
class History(models.Model):
	history_id = models.CharField(max_length=10, primary_key=True) # 2023-00001 (History on 2023, Entry #1)
	history_timestamp = models.CharField(max_length=17) # MM-DD-YY HH:MM:SS
	history_short_desc = models.CharField(max_length=100)
	history_long_desc = models.TextField()
	history_done_by = models.CharField(max_length=20, null=True) # e.g., President, Secretary
	person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True) # prevents deletion of histories attributed to a 'Person' when it's deleted
	
	def __str__(self):
		return self.history_id