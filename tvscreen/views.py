# Create your views here.
from lab_infoscreen.tvscreen.models import Screen, Lab, Printer, Computer
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404

def index(request):
	lab_list = Lab.objects.all().order_by('name')
	return HttpResponse(render_to_response('public/index.html', {'lab_list' : lab_list}))

def lab(request, lab_id):
	lab = get_object_or_404(Lab, pk=lab_id)
	printer_list = Printer.objects.filter(lab=lab_id)
	return HttpResponse(render_to_response('public/lab.html', {'lab' : lab,'printer_list' : printer_list}))

def printer_detail(request, lab_id, printer_id):
	lab = get_object_or_404(Lab, pk=lab_id)
	printer = get_object_or_404(Printer, pk=printer_id)
	return HttpResponse(render_to_response('public/printer.html', {'printer' : printer}))
