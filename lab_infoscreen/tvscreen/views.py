# Create your views here.
from lab_infoscreen.tvscreen.models import Lab, Printer, Capacity, AdminComputer, OpeningHours, OS
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
import os, re, pwd, string
from datetime import datetime, timedelta
from subprocess import Popen, PIPE
import gdata.calendar.service
from pygooglechart import PieChart2D
import pygooglechart as gc


def index(request):
	lab_list = Lab.objects.all().order_by('name')
	return HttpResponse(render_to_response('public/index.html', {'lab_list' : lab_list}))

def lab(request, lab_name):
	lab = get_object_or_404(Lab, name=lab_name)
	mobile_url = create_mobile_url()

	data = {
		'lab':lab,
		'mobile_url':mobile_url,
	}
	return HttpResponse( render_to_response('public/lab.html', data) )

def printer_detail(request, lab_id, printer_id):
	lab = get_object_or_404(Lab, pk=lab_id)
	printer = get_object_or_404(Printer, pk=printer_id)
	return HttpResponse( render_to_response('public/printer.html', {'printer' : printer}) )

def lab_capacity(request, lab_name):
	if request.is_ajax():
		lab = get_object_or_404(Lab, name=lab_name)

		update_capacities()
		capacity_list = Capacity.objects.select_related().filter(lab=lab.id)
		totals = get_totals(capacity_list)
		url_totals = create_totals_pie_url(capacity_list, 400)
		url_os = create_os_bar_url(capacity_list)
		others = create_other_urls(lab.id)
		data = {
			'capacity_list' : capacity_list,
			'totals' : totals,
			'url_totals' : url_totals,
			'url_os' : url_os,
			'others' : others,
		}
		
		return render_to_response( 'public/capacity.html', data, context_instance = RequestContext(request) )
	
def lab_admins(request, lab_name):
	if request.is_ajax():
		lab = get_object_or_404(Lab, name=lab_name)

		update_admins_martbo_style()
		admins = get_names(lab.id)
		data = { 'admins':admins }
		
		return render_to_response( 'public/admins.html', data, context_instance = RequestContext(request) )

def lab_printers(request, lab_name):
	if request.is_ajax():
		lab = get_object_or_404(Lab, name=lab_name)

		printer_list = Printer.objects.filter(lab=lab.id)
		get_printer_queues(lab.id)
		data = { 'printer_list':printer_list }

		return render_to_response( 'public/printers.html', data, context_instance = RequestContext(request) )
	
def lab_hours(request, lab_name):

	if request.is_ajax():
		lab = get_object_or_404(Lab, name=lab_name)
		
		hours = get_todays_opening_hours(lab.id)
		data = { 'hours':hours }
		
		return render_to_response( 'public/hours.html', data, context_instance = RequestContext(request) )

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
	free = [c.free() for c in capacity_list]
	os_capacities = []
	for c in capacity_list:
		os_capacities.append(str(c.os).capitalize())
	
	chart = gc.GroupedHorizontalBarChart(150, 75, x_range=(0, sum(free)) )
	chart.fill_solid(PieChart2D.BACKGROUND, "000000")
	chart.set_colours_within_series(["ffffff","4D89F9"])
	chart.add_marker(0, 0, "t"+str(free[0]), "ffffff", 16)
	chart.add_marker(0, 1, "t"+str(free[1]), "ffffff", 16)
	chart.set_axis_labels(gc.Axis.LEFT, os_capacities)
	chart.set_axis_style(0, "ffffff", 16, -1)
	for f in [free]:
		chart.add_data(f)

	return chart.get_url()

def create_mobile_url():
	size = 300 #px
	url = "http://luke.ifi.uio.no:8000"
	# Create a size x size QR code chart
	chart = gc.QRChart(size, size)
	# Add the text
	chart.add_data(url)
	# "Level H" error correction with a 0 pixel margin
	chart.set_ec('H', 0)

	return chart.get_url()

def create_totals_pie_url(capacity_list, px):
	# Reference: http://code.google.com/apis/chart/docs/gallery/pie_charts.html
	totals = get_totals(capacity_list)
	if totals['total'] <= 0:
		return ""
	
	chart = PieChart2D(px, px)
	chart.set_colours(["008000","D43838"])
	chart.fill_solid(PieChart2D.BACKGROUND, "000000")
	chart.fill_solid(PieChart2D.CHART, "000000")
	chart.add_data([totals['free'],totals['in_use']])
	
	return chart.get_url()

def update_capacities():
	# Location of rrdtool
	rrdtool = "/usr/bin/X11/rrdtool"
	if not os.path.exists(rrdtool):
		print "rrdtool is not installed. Run: 'sudo apt-get install rrdtool' to fix."
		return

	# rrdtool command
	rrd_cmd = "lastupdate"
	# 15 minutes ago
	rrd_update_interval = datetime.now() - timedelta(minutes=15)

	labs = Lab.objects.all()
	oses = OS.objects.all()

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
			
			# Is the cached capacity data more than 15 min. old?
			need_update = cur.last_updated <= rrd_update_interval
			# Also check if it has just been created.
			if (not created) or need_update:
				# Update all the labs.
				cur.last_updated = new_last_updated
				cur.in_use = new_in_use
				cur.down = new_down
				cur.total = new_total
				cur.save()

def parse_lastupdate(text):
	return re.findall(r"(\d+)",text)

def get_rrd_path(lab, the_os):
	# Directory containing the rrd-files to parse
	rrd_dir = os.path.expanduser('~termvakt/stuestatistikk/rrd/')
	rrd_path = rrd_dir + lab + '-' + the_os + '.rrd'
	if not os.path.exists(rrd_path):
		print 'Looked in ' + rrd_dir + ' for ' + lab + '-' + the_os + '.rrd, but did not find it.'
		return None
	return rrd_path

def update_admins_martbo_style():
	path = '/local/ifivar/rwho2/'
	rwhodir = os.path.expanduser(path)

	adm_comp = AdminComputer.objects.all()

	for comp in adm_comp:
		filename = os.path.join(rwhodir,"rwho2." + comp.name + ".ifi.uio.no")
		if not os.path.exists(filename):
			print "did not find " + filename + ". Path or admin computer name is wrong!"
			break
		else:
			try:
				file = open(filename)
				# Search for the user attached to the console session.
				search = re.findall(r"user;1;(\w+);;:0",file.read())
				if len(search) == 1:
					comp.admin_username = search[0]
				else:
					# Put the empty string in the db when no one is logged in.
					comp.admin_username = ""
				comp.save()
				file.close()
			except Exception:
				print "could not open " + filename + "."

def get_names(lab_id):
	comps = AdminComputer.objects.filter(lab=lab_id)

	names = []
	for comp in comps:
		name = get_firstname(comp.admin_username)
		if name is not None:
			names.append(name)
	
	return names
	
def get_firstname(username):
	# ask the user database for iso-8859-1 encoded full name, then take the first name from it.
	if len(username) == 0:
		# No user.
		return None
	try:
		firstname = pwd.getpwnam(username)[4].decode('iso-8859-1').split()[0]
	except KeyError: 
		print 'Looked for \'' + username + '\' in the user database, but with no luck...'
		return None
	return firstname

def get_todays_opening_hours(lab_id):
	#TODO: Save opening hours from gcal and update @ 07, 15, 19.
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
	
def get_printer_queues(lab_id):
	printers = Printer.objects.filter(lab=lab_id)
	ppq = '/local/bin/ppq'
	lpq = '/local/bin/lpq' # TODO: Move this to a general settings page in the admin panel.
	
	for printer in printers:
		queue = []

		if printer.system == 'ppq':
			if not os.path.exists(ppq):
				print "ppq (PRISS) is not present, are you @UiO?"
			else:
				cmd = [ppq, printer.name]
				p = Popen(cmd, stdout=PIPE, stderr=PIPE)
				stdout, stderr = p.communicate()
				
				queue = parse_ppq_data(stdout)
		elif printer.system == 'lpq':
			if not os.path.exists(lpq):
				print "lpq (CUPS) not found at '"+ lpq + "'. Try 'sudo apt-get install cups' or change the path."
			else:
				cmd = [lpq, '-P'+printer.name]
				p = Popen(cmd, stdout=PIPE, stderr=PIPE)
				stdout, stderr = p.communicate()

				queue = parse_lpq_data(stdout)
		else:
			pass
		
		printer.queue = ', '.join(queue)
		printer.queue_size = len(queue)
		printer.save()

def parse_lpq_data(data):
	# skip after titles and general status 
	hr = '  Rank     Owner    Job                 Title                  Size     Time   '
	pos = string.find(data,hr)
	jobs = data[pos+len(hr):]

	users = re.findall(r" (\w+) \d+ ", jobs)
	return users

def parse_ppq_data(data):
	# skip after titles and general status 
	hr = '----------------------------------------------------------------------------\n'
	pos = string.find(data,hr)
	jobs = data[pos+len(hr):]

	users = re.findall(r"\d+ (\w+)@",jobs)
	return users

