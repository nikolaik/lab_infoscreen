# Create your views here.
from lab_infoscreen.tvscreen.models import Lab, Printer, Computer, Admin, Chart
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404

def index(request):
	lab_list = Lab.objects.all().order_by('name')
	return HttpResponse(render_to_response('public/index.html', {'lab_list' : lab_list}))

def lab(request, lab_id):
	lab = get_object_or_404(Lab, pk=lab_id)
	printer_list = Printer.objects.filter(lab=lab_id)
	chart = Chart.objects.filter(lab=lab_id)
	total_num_computers = Computer.objects.filter(lab=lab_id).count()
	return HttpResponse(render_to_response('public/lab.html',
		{
		'lab' : lab,
		'printer_list' : printer_list,
		'chart' : chart,
		'total_num_computers' : total_num_computers,
		}))

def printer_detail(request, lab_id, printer_id):
	lab = get_object_or_404(Lab, pk=lab_id)
	printer = get_object_or_404(Printer, pk=printer_id)
	return HttpResponse(render_to_response('public/printer.html', {'printer' : printer}))
