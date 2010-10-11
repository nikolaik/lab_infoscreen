# Create your views here.
from lab_infoscreen.tvscreen.models import Lab, Printer, Capacity, Admin, AdminComputer, OpeningHours, OS
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
import sys, os, re
from datetime import datetime, timedelta
from subprocess import Popen, PIPE

def index(request):
	lab_list = Lab.objects.all().order_by('name')
	return HttpResponse(render_to_response('public/index.html', {'lab_list' : lab_list}))

def lab(request, lab_id):
	lab = get_object_or_404(Lab, pk=lab_id)

	printer_list = Printer.objects.filter(lab=lab_id)
	update_capacities(Lab.objects.all(),OS.objects.all())
	capacity_list = Capacity.objects.select_related().filter(lab=lab_id)
	totals = get_totals(capacity_list)
	url_totals = create_totals_pie_url(capacity_list, 300)
	url_os = create_os_bar_url(capacity_list)
	others = create_other_urls(Lab.objects.exclude(pk=lab_id))
	return HttpResponse(render_to_response('public/lab.html',
		{
		'lab' : lab,
		'printer_list' : printer_list,
		'capacity_list' : capacity_list,
		'totals' : totals,
		'url_totals' : url_totals,
		'url_os' : url_os,
		'others' : others,
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
	return {'total':total, 'in_use':in_use, 'free':total-in_use-down}

def create_other_urls(other_labs):
	urls = []
	for olab in other_labs:
		urls.append( {'lab': olab, 'url': create_totals_pie_url(Capacity.objects.select_related().filter(lab=olab.id), 200)})
	return urls

def create_os_bar_url(capacity_list):
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
	o += "chxs=0,000000,16|1,000000,16&"
	# Visible Axes = y is left, x is bottom
	o += "chxt=y&"
	# Size = widht x height
	o += "chs=150x100&"
	# Color = red, green
	o += "chco=000000|4D89F9&"
	# Custom axis Labels = axis_index:|lbl1|lbl2
	#axis_labels = "chxl=0:|Windows|UNIX|1:|0|" + str(sum(free))
	o += "chxl=0:|Windows|UNIX&"
	# Data scaling
	o += "chds=0," + str(sum(free)) + "&"
	# Markers
	o += "chm=N,000000,0,-1,11"

	return o

def create_totals_pie_url(capacity_list, px):
	# Reference: http://code.google.com/apis/chart/docs/gallery/pie_charts.html
	# TODO: Add markers!
	totals = get_totals(capacity_list)
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
	
	return o

def update_capacities(labs, oses):

	### CONFIG ###
	# Location of rrdtool
	rrdtool = "/usr/bin/X11/rrdtool"
	# rrdtool command
	rrd_cmd = "lastupdate"
	rrd_update = datetime.now() - timedelta(minutes=15)
	'''
	Is update is older than now - rrd-update interval min?
	If not then update, else return true.
	Update all the labs
	'''
	i = 0
	for the_lab in labs:
		#if lab.update < 
		for the_os in oses:
			#cmd = [rrdtool,rrd_cmd, get_rrd_path(lab, os)]
			#p = Popen(cmd, stdout=PIPE, stderr=PIPE)
			#stdout, stderr = p.communicate()
			i = i + 1

			stdout = "1286747381 10 0 " + str(20 + i + 7)
			tmp_new_last_updated, new_in_use, new_down, new_total = parse_lastupdate(stdout)
			new_last_updated = datetime.fromtimestamp(int(tmp_new_last_updated))
			cur, created = Capacity.objects.get_or_create(lab=the_lab,os=the_os,
				defaults={'last_updated': new_last_updated, 'in_use': new_in_use, 'down': new_down, 'total': new_total })

			need_update = rrd_update <= cur.last_updated
			if (not created) and need_update:
				cur.last_updated = new_last_updated
				cur.in_use = new_in_use
				cur.down = new_down
				cur.total = new_total
				cur.save()

def parse_lastupdate(string):
	return re.findall(r"(\d+)",string)

def get_rrd_path(lab, os):
	# Directory containing the rrd-files to parse
	#rrddir = os.path.expanduser('~termvakt/stuestatistikk/rrd/')
	return rrddir + lab + '-' + os + '.rrd'
