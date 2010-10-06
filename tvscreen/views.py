# Create your views here.
from lab_infoscreen.tvscreen.models import Lab, Printer, Capacity, Admin, AdminComputer, OpeningHours, OS
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
import sys, os, re
from subprocess import Popen, PIPE

def index(request):
	lab_list = Lab.objects.all().order_by('name')
	return HttpResponse(render_to_response('public/index.html', {'lab_list' : lab_list}))

def lab(request, lab_id):
	lab = get_object_or_404(Lab, pk=lab_id)


	printer_list = Printer.objects.filter(lab=lab_id)
	capacity_list = Capacity.objects.select_related().filter(lab=lab_id)
	total, in_use, free = get_totals(capacity_list)
	url_totals = create_totals_pie_url(capacity_list)
	url_os = create_os_bar_url(capacity_list)
	return HttpResponse(render_to_response('public/lab.html',
		{
		'lab' : lab,
		'printer_list' : printer_list,
		'capacity_list' : capacity_list,
		'total' : total,
		'free' : free,
		'in_use' : in_use,
		'url_totals' : url_totals,
		'url_os' : url_os,
		}))

def printer_detail(request, lab_id, printer_id):
	lab = get_object_or_404(Lab, pk=lab_id)
	printer = get_object_or_404(Printer, pk=printer_id)
	return HttpResponse(render_to_response('public/printer.html', {'printer' : printer}))

def get_totals(capacity_list):
	# TODO: This is stupid, this should be done another way.
	total = 0
	in_use = 0
	down = 0

	for capacity in capacity_list:
		total += capacity.total
		in_use += capacity.in_use
		down += capacity.down
	return (total, in_use, total-in_use-down)

def create_os_bar_url(capacity_list):
	# Reference: http://code.google.com/apis/chart/docs/gallery/bar_charts.html
	# free = total-(down+in_use)
	free = [c.total - c.down - c.in_use for c in capacity_list]
	valuelist = ",".join([str(f) for f in free])

	base = "http://chart.apis.google.com/chart?"
	# Data
	data = "chd=t:"+ str(valuelist)
	# Type = p is 2d-chart (choose pc?)
	ctype = "cht=bhs"
	# Axis style = axis_index, rgb, points
	axis_style = "chxs=0,000000,16|1,000000,16"
	# Visible Axes = y is left, x is bottom
	visible_area = "chxt=y,x"
	# Size = widht x height
	size = "chs=150x100"				
	# Color = red, green
	color = "chco=000000|4D89F9"
	# Custom axis Labels = axis_index:|lbl1|lbl2
	axis_labels = "chxl=0:|Windows|UNIX|1:|0|" + str(sum(free))
	# Data scaling
	data_scaling = "chds=0," + str(sum(free))
	# Markers
	markers = "chm=N,000000,0,-1,11"

	full = base + "&" + visible_area + "&" + size + "&" + ctype + "&" + color + "&" + data + "&" + axis_labels + "&" + axis_style + "&" + data_scaling + "&" + markers 

	return full

def create_totals_pie_url(capacity_list):
	# Reference: http://code.google.com/apis/chart/docs/gallery/pie_charts.html
	# TODO: Add markers!
	total, in_use, free = get_totals(capacity_list)
	base = "http://chart.apis.google.com/chart?"
	# Axis style	= 0, rgb, points
	axis_style = "chxs=0,000000,30"
	# Visible Axes	= x is bottom
	visible_area = "chxt=x"
	# Size			= widht x height
	size = "chs=400x200"				
	# Type			= p is 2d-chart (choose pc?)
	ctype = "cht=p"
	# Color = red, green
	color = "chco=D43838|008000"
	# Data
	data = "chd=t:"+ str(free) +"," + str(in_use)
	# Labels = lbl1, lbl2
	labels = "chl=In use|Free"
	
	full = base + "&" + axis_style + "&" + visible_area + "&" + size + "&" + ctype + "&" + color + "&" + data + "&" + labels
	return full

def update_capacities(labs, oses):

	### CONFIG ###
	# Directory containing the rrd-files to parse
	rrddir = os.path.expanduser('~termvakt/stuestatistikk/rrd/')
	# Location of rrdtool
	rrdtool = "/usr/bin/X11/rrdtool"
	# rrdtool command
	rrd_cmd = "lastupdate"

	labs = ['abel','vb','fys'] #testing 
	oses = ['windows','unix'] #testing 

	for lab in labs:
		for os in oses:
			print lab, os, ":",
			cmd = [rrdtool,rrd_cmd, get_rrd_path(lab, os)]
			p = Popen(cmd, stdout=PIPE, stderr=PIPE)
			stdout, stderr = p.communicate()

			update, use, down, total = parse_lastupdate(stdout)
			print update, use, down, total

def parse_lastupdate(string):
	return re.findall(r"(\d+)",string)

def get_rrd_path(lab, os):
	return rrddir + lab + '-' + os + '.rrd'

