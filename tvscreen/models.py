from django.db import models


# Create your models here.
class Lab(models.Model):
	# ...
	def __unicode__(self):
		return self.name

	name = models.CharField(max_length=200)
	welcome_msg = models.CharField(max_length=400)

class OpeningHours(models.Model):
	def __unicode__(self):
		return str(self.date_opens) + str(self.date_closes)

	lab = models.ForeignKey(Lab)

	date_opens = models.DateTimeField('date opens')
	date_closes = models.DateTimeField('date closes')


class OS(models.Model):
	def __unicode__(self):
		return self.name
	name = models.CharField(max_length=200)

class Capacity(models.Model):
	def __unicode__(self):
		return str(self.lab) + ": " + str(self.os) + ": " +str(self.total-self.in_use) + "/" + str(self.total)

	lab = models.ForeignKey(Lab)

	os = models.ForeignKey(OS)
	
	in_use = models.IntegerField()
	down = models.IntegerField()
	total = models.IntegerField()

	last_updated = models.DateTimeField('last updated')
	url = models.CharField(max_length=300)

class Printer(models.Model):
	# ...
	def __unicode__(self):
		return self.name

	lab = models.ForeignKey(Lab)

	queue_size = models.IntegerField()
	name = models.CharField(max_length=200)

class AdminComputer(models.Model):
	# ...
	def __unicode__(self):
		return self.name
	
	def is_taken(self):
		return taken == 1

	lab = models.ForeignKey(Lab)

	name = models.CharField(max_length=200)
	in_use = models.IntegerField()

class Admin(models.Model):
	def __unicode__(self):
		return self.name

	computer = models.ForeignKey(AdminComputer)

	name = models.CharField(max_length=200)

'''
The sceleton for this app is based on:
	http://docs.djangoproject.com/en/1.2/intro/tutorial02/
'''
'''
from django.db import models

class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()
'''
