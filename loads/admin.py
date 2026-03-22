from django.contrib import admin
from .models import Aircraft, LoadCase, AnalysisReport


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display  = ['name', 'registration', 'aircraft_type', 'created_by', 'created_at']
    search_fields = ['name', 'registration']
    list_filter   = ['name','created_at']


@admin.register(LoadCase)
class LoadCaseAdmin(admin.ModelAdmin):
    list_display  = ['name', 'aircraft', 'maneuver_type',
                     'load_factor_nz', 'speed_ktas', 'severity_label', 'is_critical']
    list_filter   = ['maneuver_type', 'flight_phase', 'is_critical']
    search_fields = ['name', 'aircraft__name']
    readonly_fields = ['dynamic_pressure', 'speed_ms', 'severity_label']

    # Group fields into sections in the admin form
    fieldsets = [
        ('Basic Info', {
            'fields': ['aircraft', 'name', 'maneuver_type', 'flight_phase', 'notes']
        }),
        ('Load Parameters', {
            'fields': ['load_factor_nz', 'speed_ktas', 'altitude_ft']
        }),
        ('Computed (read-only)', {
            'fields': ['dynamic_pressure', 'speed_ms', 'severity_label'],
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': ['is_critical', 'created_by']
        }),
    ]


@admin.register(AnalysisReport)
class AnalysisReportAdmin(admin.ModelAdmin):
    list_display  = ['load_case', 'status', 'safety_factor', 'is_safe', 'margin_of_safety']
    list_filter   = ['status']
    readonly_fields = ['is_safe', 'margin_of_safety']