from lab_infoscreen.tvscreen.models import Lab, Printer, AdminComputer, OS
from django.contrib import admin

class AdminComputerInline(admin.TabularInline):
	fieldsets = [
		(None, {'fields': ['name']})
	]
	model = AdminComputer
	extra = 0

class PrinterInline(admin.TabularInline):
	fieldsets = [
		(None, {'fields': ['name','system']})
	]
	model = Printer
	extra = 0

class LabAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,	{'fields': ['name','welcome_msg']})
	]
	inlines = [AdminComputerInline, PrinterInline]

class PrinterAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields': ['name','system']})
	]

class AdminComputerAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields': ['name']})
	]

admin.site.register(Lab, LabAdmin)
admin.site.register(Printer, PrinterAdmin)
admin.site.register(AdminComputer, AdminComputerAdmin)
admin.site.register(OS)
