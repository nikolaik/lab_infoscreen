from infoskjerm.tvscreen.models import Screen, Lab, Printer, Computer
from django.contrib import admin

class LabInline(admin.TabularInline):
	model = Lab
	extra = 0

class ScreenAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,	{'fields': ['description']})
	]
	inlines = [LabInline]

class LabAdmin(admin.ModelAdmin):
	list_filter = ['name']

admin.site.register(Screen, ScreenAdmin)
admin.site.register(Lab)
admin.site.register(Printer)
admin.site.register(Computer)
