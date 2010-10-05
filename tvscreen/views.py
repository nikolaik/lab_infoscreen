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
	capacity_list = Capacity.objects.filter(lab=lab_id)
	total_capacity, in_use_capacity = get_total(capacity_list)
	url_capacity = create_pie_url(total_capacity, in_use_capacity)
	return HttpResponse(render_to_response('public/lab.html',
		{
		'lab' : lab,
		'printer_list' : printer_list,
		'capacity_list' : capacity_list,
		'total_capacity' : total_capacity,
		'in_use_capacity' : in_use_capacity,
		'url_capacity' : url_capacity,
		}))

def printer_detail(request, lab_id, printer_id):
	lab = get_object_or_404(Lab, pk=lab_id)
	printer = get_object_or_404(Printer, pk=printer_id)
	return HttpResponse(render_to_response('public/printer.html', {'printer' : printer}))

def get_total(capacity_list):
	total = 0
	in_use = 0
	for capacity in capacity_list:
		total += capacity.total
		in_use += capacity.in_use
	
	return total, in_use

def create_pie_url(total, in_use):
	#
	# Reference: http://code.google.com/apis/chart/docs/gallery/pie_charts.html
	base = "http://chart.apis.google.com/chart?"
	# Axis style	= 0, rgb, points
	axis_style = "chxs=0,000000,40"
	# Visible Axes	= x is bottom
	visible_area = "chxt=x"
	# Size			= widht x height
	size = "chs=600x400"				
	# Type			= p is 2d-chart (choose pc?)
	ctype = "cht=p"
	# Color = red, green
	color = "chco=D43838|008000"
	# Data
	data = "chd=t:"+ str(total-in_use) +"," + str(in_use)
	# Labels = lbl1, lbl2
	labels = "chl=in_use|free"

	full = base + "&" + axis_style + "&" + visible_area + "&" + size + "&" + ctype + "&" + color + "&" + data + "&" + labels
	print full	# FIXME: Debug
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

