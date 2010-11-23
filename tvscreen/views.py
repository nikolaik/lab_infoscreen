# Create your views here.
from lab_infoscreen.tvscreen.models import Lab, Printer, Capacity, AdminComputer, OpeningHours, OS
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
import sys, os, re, pwd
from datetime import datetime, timedelta, date, time
from subprocess import Popen, PIPE
import gdata.calendar.service
from urllib import urlencode, quote


def index(request):
	lab_list = Lab.objects.all().order_by('name')
	return HttpResponse(render_to_response('public/index.html', {'lab_list' : lab_list}))

def lab(request, lab_id):
	lab = get_object_or_404(Lab, pk=lab_id)

	printer_list = Printer.objects.filter(lab=lab_id)
	update_capacities()
	update_admins_martbo_style()
	capacity_list = Capacity.objects.select_related().filter(lab=lab_id)
	totals = get_totals(capacity_list)
	url_totals = create_totals_pie_url(capacity_list, 400)
	url_os = create_os_bar_url(capacity_list)
	others = create_other_urls(lab_id)
	admins = get_names(lab_id)
	hours = get_todays_openinghours(lab_id)
	return HttpResponse(render_to_response('public/lab.html',
		{
		'lab' : lab,
		'printer_list' : printer_list,
		'capacity_list' : capacity_list,
		'totals' : totals,
		'url_totals' : url_totals,
		'url_os' : url_os,
		'others' : others,
		'admins' : admins,
		'hours' : hours,
		}))

def printer_detail(request, lab_id, printer_id):
	lab = get_object_or_404(Lab, pk=lab_id)
	printer = get_object_or_404(Printer, pk=printer_id)
	return HttpResponse(render_to_response('public/printer.html', {'printer' : printer}))

def get_totals(capacity_list):
	# TODO: This is stupid and should be done another way.
	total = 0
	in_use = 0
	down = 0

	for capacity in capacity_list:
		total += capacity.total
		in_use += capacity.in_use
		down += capacity.down
	#total = 20;in_use = 5; down = 0 # FIXME: DEBUG
	return {'total':total, 'in_use':in_use, 'free':total-in_use-down}

def create_other_urls(lab_id):
	other_labs = Lab.objects.exclude(pk=lab_id)
	urls = []
	for olab in other_labs:
		urls.append( {'lab': olab, 'url': create_totals_pie_url(Capacity.objects.select_related().filter(lab=olab.id), 200)})
	return urls

def create_os_bar_url(capacity_list):
	# TODO: text color-parameter
	# TODO: urllib.urlencode
	# Reference: http://code.google.com/apis/chart/docs/gallery/bar_charts.html
	# free = total-(down+in_use)
	free = [c.total - c.down - c.in_use for c in capacity_list]
	valuelist = ",".join([str(f) for f in free])

	o = "http://chart.apis.google.com/chart?"
	# Data
	o += "chd=t:"+ str(valuelist) + "&"
	# Type = p is 2d-chart (choose pc?)
	o += "cht=bhs&"
	# Axis style = axis_index, rgb, points
	o += "chxs=0,ffffff,16|1,ffffff,16&"
	# Visible Axes = y is left, x is bottom
	o += "chxt=y&"
	# Size = widht x height
	o += "chs=150x100&"
	# Color = red, green
	o += "chco=ffffff|4D89F9&"
	# Custom axis Labels = axis_index:|lbl1|lbl2
	#axis_labels = "chxl=0:|Windows|UNIX|1:|0|" + str(sum(free))
	o += "chxl=0:|Windows|UNIX&"
	# Data scaling
	o += "chds=0," + str(sum(free)) + "&"
	# Markers
	o += "chm=N,ffffff,0,-1,16&"
	# color fills (background)
	o += "chf=bg,s,ffffff00"

	return o

def create_totals_pie_url(capacity_list, px):
	# Reference: http://code.google.com/apis/chart/docs/gallery/pie_charts.html
	# TODO: Add markers!
	# TODO: text color-parameter
	# TODO: urllib.urlencode
	totals = get_totals(capacity_list)
	if totals['total'] == 0:
		print "Could not create a pie-url. No capacity data."
		return "" 

	o = "http://chart.apis.google.com/chart?"
	# Axis style = 0, rgb, points
	o += "chxs=0,000000,30&"
	# Size = widht x height
	o += "chs="+ str(px) + "x" + str(px) + "&"
	# Type = p is 2d-chart (choose pc?)
	o += "cht=p&"
	# Color = green|red
	o += "chco=008000|D43838&"
	# Data
	o += "chd=t:"+ str(totals['free']) +"," + str(totals['in_use']) + "&"
	# Visible Axes = x is bottom
	#o += "chxt=x&"
	# Labels = lbl1, lbl2
	#o += "chl=Free|In use"
	# color fills (background)
	o += "chf=bg,s,ffffff00"
	
	return o

def update_capacities():
	### CONFIG ###
	# Location of rrdtool
	rrdtool = "/usr/bin/X11/rrdtool"
	if not os.path.exists(rrdtool):
		print "rrdtool is not installed. Run: 'sudo apt-get install rrdtool' to fix"
		return

	# rrdtool command
	rrd_cmd = "lastupdate"
	rrd_update = datetime.now() - timedelta(minutes=15)

	labs = Lab.objects.all()
	oses = OS.objects.all()
	'''
	Is update older than now-rrd-update interval min?
	If not then update, else return true.
	Update all the labs.
	'''
	for the_lab in labs:
		for the_os in oses:
			rrd_path = get_rrd_path(the_lab.name, the_os.name)
			if not rrd_path:
				return
			cmd = [rrdtool, rrd_cmd, rrd_path]
			p = Popen(cmd, stdout=PIPE, stderr=PIPE)
			stdout, stderr = p.communicate()

			tmp_new_last_updated, new_in_use, new_down, new_total = parse_lastupdate(stdout)
			new_last_updated = datetime.fromtimestamp(int(tmp_new_last_updated))
			cur, created = Capacity.objects.get_or_create(lab=the_lab,os=the_os,
				defaults={'last_updated': new_last_updated, 'in_use': new_in_use, 'down': new_down, 'total': new_total })

			need_update = rrd_update <= cur.last_updated
			if (not created) or need_update:
				cur.last_updated = new_last_updated
				cur.in_use = new_in_use
				cur.down = new_down
				cur.total = new_total
				cur.save()

def parse_lastupdate(string):
	return re.findall(r"(\d+)",string)

def get_rrd_path(lab, the_os):
	# Directory containing the rrd-files to parse
	rrd_dir = os.path.expanduser('~termvakt/stuestatistikk/rrd/')
	rrd_path = rrd_dir + lab + '-' + the_os + '.rrd'
	if not os.path.exists(rrd_path):
		print 'Looked in ' + rrd_dir + ' for ' + lab + '-' + the_os + '.rrd, but did not find it.'
		return None
	return rrd_path

def update_admins_martbo_style():
	'''path = "~martbo/bin/infoskjerm/"'''
	path = '/local/ifivar/rwho2/'
	rwhodir = os.path.expanduser(path)

	adm_comp = AdminComputer.objects.all()

	for comp in adm_comp:
		filename = os.path.join(rwhodir,"rwho2." + comp.name + ".ifi.uio.no")
		if not os.path.exists(filename):
			print "did not find " + filename + ". Aborting update..."
			break
		else:
			try:
				file = open(filename)
				search = re.findall(r"user;1;(\w+);;:0",file.read())
				if len(search) == 1:
					comp.admin_username = search[0]
				else:
					comp.admin_username = ""
				comp.save()
				file.close()
			except Exception:
				print "could not open " + filename + "."

def get_names(lab_id):
	comps = AdminComputer.objects.filter(lab=lab_id)

	names = [get_firstname(comp.admin_username) for comp in comps]
	if names[0] == None:
		return
	return names
	
def get_firstname(username):
	# ask the user database for iso-8859-1 encoded full name, then take the first name from it.
	if username is '':
		return None
	try:
		firstname = pwd.getpwnam(username)[4].decode('iso-8859-1').split()[0]
	except KeyError: 
		print 'Looked for \'' + username + '\' in the user database, but with no luck...'
		return None
	return firstname

def get_todays_openinghours(lab_id):
	lab = Lab.objects.get(pk=lab_id)
	today = datetime.today()
	today_str = today.strftime("%Y-%m-%d")
	tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")

	# Create a client class which will make HTTP requests.
	client = gdata.calendar.service.CalendarService()
	# Build the query 
	calendar_id = 'omhp3g69p6cgc0je9mfr31bcv4@group.calendar.google.com'
	query = gdata.calendar.service.CalendarEventQuery(calendar_id, 'public', 'full')
	query.start_min = today_str	# inclusive
  	query.start_max = tomorrow_str # exclusive
	# Query the server for an Atom feed containing a list of your calendars.
  	calendar_feed = client.CalendarQuery(query)
	# Loop through the feed and extract each calendar entry.
	for event in calendar_feed.entry:
		if event.title.text == lab.name:
			when = event.when[0]
			# Note: Slicing of tz-data
			start = datetime.strptime(when.start_time[:-6],'%Y-%m-%dT%H:%M:%S.000')
			end = datetime.strptime(when.end_time[:-6],'%Y-%m-%dT%H:%M:%S.000')
			return {'start':start,'end':end}
	
				

