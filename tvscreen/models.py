from django.db import models

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
		return str(self.lab) + ": " + str(self.os) + ": " +str(free()) + "/" + str(self.total)

	def free(self):
		return self.total - self.in_use - self.down

	lab = models.ForeignKey(Lab)

	os = models.ForeignKey(OS)
	
	in_use = models.IntegerField()
	down = models.IntegerField()
	total = models.IntegerField()

	last_updated = models.DateTimeField('last updated')

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

