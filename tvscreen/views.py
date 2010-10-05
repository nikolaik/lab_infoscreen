# Create your views here.
from lab_infoscreen.tvscreen.models import Lab, Printer, Capacity, Admin, AdminComputer, OpeningHours
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404

def index(request):
	lab_list = Lab.objects.all().order_by('name')
	return HttpResponse(render_to_response('public/index.html', {'lab_list' : lab_list}))

def lab(request, lab_id):
	lab = get_object_or_404(Lab, pk=lab_id)
	printer_list = Printer.objects.filter(lab=lab_id)
	capacity_list = Capacity.objects.filter(lab=lab_id)
	total_capacity, busy_capacity = get_total(capacity_list)
	url_capacity = create_pie_url(total_capacity, busy_capacity)
	return HttpResponse(render_to_response('public/lab.html',
		{
		'lab' : lab,
		'printer_list' : printer_list,
		'capacity_list' : capacity_list,
		'total_capacity' : total_capacity,
		'busy_capacity' : busy_capacity,
		'url_capacity' : url_capacity,
		}))

def printer_detail(request, lab_id, printer_id):
	lab = get_object_or_404(Lab, pk=lab_id)
	printer = get_object_or_404(Printer, pk=printer_id)
	return HttpResponse(render_to_response('public/printer.html', {'printer' : printer}))

def get_total(capacity_list):
	total = 0
	busy = 0
	for capacity in capacity_list:
		total += capacity.total
		busy += capacity.busy
	
	return total, busy

def create_pie_url(total, busy):
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
	data = "chd=t:"+ str(total-busy) +"," + str(busy)
	# Labels = lbl1, lbl2
	labels = "chl=busy|free"

	full = base + "&" + axis_style + "&" + visible_area + "&" + size + "&" + ctype + "&" + color + "&" + data + "&" + labels
	print full
	return full
