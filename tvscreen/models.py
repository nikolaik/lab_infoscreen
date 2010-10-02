from django.db import models

'''
The sceleton for this app is based on:
	http://docs.djangoproject.com/en/1.2/intro/tutorial02/
'''

# Create your models here.
class Screen(models.Model):
	# ...
	def __unicode__(self):
		return self.description

	description = models.CharField(max_length=200)
	
class Lab(models.Model):
	# ...
	def __unicode__(self):
		return self.name

	screen = models.ForeignKey(Screen)
	name = models.CharField(max_length=200)
	# TODO: Opening times

class Printer(models.Model):
	# ...
	def __unicode__(self):
		return self.name

	lab = models.ForeignKey(Lab)
	printerqueue = models.IntegerField()
	name = models.CharField(max_length=200)

class Computer(models.Model):
	# ...
	def __unicode__(self):
		return self.name
	
	def is_taken(self):
		return taken == 1

	lab = models.ForeignKey(Lab)
	os = models.CharField(max_length=200)
	name = models.CharField(max_length=200)
	taken = models.IntegerField()


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
