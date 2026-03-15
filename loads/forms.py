from django import forms
from .models import Aircraft, LoadCase, AnalysisReport


class AircraftForm(forms.ModelForm):
    class Meta:
        model  = Aircraft
        fields = ['name', 'registration', 'aircraft_type', 'max_takeoff_weight']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Airbus A320'
            }),
            'registration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. VT-ANK'
            }),
            'aircraft_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Narrow-body commercial'
            }),
            'max_takeoff_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'MTOW in kg'
            }),
        }


class LoadCaseForm(forms.ModelForm):
    class Meta:
        model  = LoadCase
        fields = [
            'aircraft', 'name', 'maneuver_type', 'flight_phase',
            'load_factor_nz', 'speed_ktas', 'altitude_ft',
            'is_critical', 'notes'
        ]
        widgets = {
            'aircraft':       forms.Select(attrs={'class': 'form-control'}),
            'name':           forms.TextInput(attrs={'class': 'form-control'}),
            'maneuver_type':  forms.Select(attrs={'class': 'form-control'}),
            'flight_phase':   forms.Select(attrs={'class': 'form-control'}),
            'load_factor_nz': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.1'
            }),
            'speed_ktas':     forms.NumberInput(attrs={
                'class': 'form-control', 'step': '1'
            }),
            'altitude_ft':    forms.NumberInput(attrs={
                'class': 'form-control', 'step': '100'
            }),
            'notes':          forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3
            }),
        }

    def clean_load_factor_nz(self):
        """Custom validation — FAR 25 structural limits"""
        nz = self.cleaned_data['load_factor_nz']
        if nz > 9.0 or nz < -4.0:
            raise forms.ValidationError(
                "Load factor must be between -4g and +9g (FAR 25 structural limits)"
            )
        return nz

    def clean_speed_ktas(self):
        speed = self.cleaned_data['speed_ktas']
        if speed <= 0:
            raise forms.ValidationError("Speed must be a positive value.")
        if speed > 900:
            raise forms.ValidationError("Speed exceeds maximum credible value (900 KTAS).")
        return speed

    def clean(self):
        """Cross-field validation"""
        cleaned = super().clean()
        flight_phase = cleaned.get('flight_phase')
        altitude     = cleaned.get('altitude_ft')
        if flight_phase == 'cruise' and altitude and altitude < 10000:
            raise forms.ValidationError(
                "Cruise phase load cases should be above 10,000 ft."
            )
        return cleaned


class AnalysisReportForm(forms.ModelForm):
    class Meta:
        model  = AnalysisReport
        fields = ['max_bending_moment', 'max_shear_force', 'safety_factor', 'status', 'notes']
        widgets = {
            'max_bending_moment': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_shear_force':    forms.NumberInput(attrs={'class': 'form-control'}),
            'safety_factor':      forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }