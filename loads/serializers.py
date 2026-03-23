from rest_framework import serializers
from .models import Aircraft, LoadCase, AnalysisReport

class AircraftSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Aircraft
        fields = '__all__'
        def get_load_case_count(self,obj):
            return obj.load_cases.count()
        
class LoadCaseSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    dynamic_pressure  = serializers.ReadOnlyField()
    speed_ms          = serializers.ReadOnlyField()
    severity_label    = serializers.ReadOnlyField()
    maneuver_display  = serializers.CharField(source='get_maneuver_type_display', read_only=True)


    class Meta:
        model = LoadCase
        fields = '__all__'

    # def ValidateCruise(self,obj):
    #     if obj.get('flight_phase') == 'cruise' and obj.get('altitude_ft') < 10000:
    #         raise serializers.ValidationError('cruise phase must be above 10k feet')
    #     return obj
    # def ValidateNz(self,obj):
    #     if obj.get('load_factor_nz') > 9.0 or obj.get('load_factor_nz') < -4:
    #         raise serializers.ValidationError('Load Factor Out of Bounds')
    #     return obj.get('load_factor_nz')

class AnalysisReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisReport
        fields = '__all__'
