from lab_infoscreen.tvscreen.models import Lab, Printer, Computer, Admin, Chart
from django.contrib import admin

class ComputerInline(admin.TabularInline):
	model = Computer
	extra = 2

class PrinterInline(admin.TabularInline):
	model = Printer
	extra = 1

class LabAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,	{'fields': ['name']})
	]
	inlines = [ComputerInline, PrinterInline]

admin.site.register(Lab, LabAdmin)
admin.site.register(Printer)
admin.site.register(Computer)
admin.site.register(Admin)
admin.site.register(Chart)
