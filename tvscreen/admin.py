from lab_infoscreen.tvscreen.models import Lab, Printer, Capacity, Admin, AdminComputer, OpeningHours
from django.contrib import admin

class AdminComputerInline(admin.TabularInline):
	model = AdminComputer
	extra = 2

class PrinterInline(admin.TabularInline):
	model = Printer
	extra = 1

class LabAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,	{'fields': ['name']})
	]
	inlines = [AdminComputerInline, PrinterInline]

admin.site.register(Lab, LabAdmin)
admin.site.register(Printer)
admin.site.register(Admin)
admin.site.register(AdminComputer)
admin.site.register(Capacity)
admin.site.register(OpeningHours)
