from django.shortcuts               import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth            import login, logout, authenticate
from django.contrib.auth.models     import User
from django.contrib                 import messages
from django.http                    import HttpResponse
from django.views.generic           import ListView, DetailView
from django.contrib.auth.mixins     import LoginRequiredMixin
import csv
import json
from .models import Aircraft, LoadCase, AnalysisReport
from .forms  import AircraftForm, LoadCaseForm, AnalysisReportForm
from .serializers import AircraftSerializer, LoadCaseSerializer, AnalysisReportSerializer
from rest_framework import generics, viewsets


#Rest Framework ________________________________________________________________
class AircraftSerializerViewRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    lookup_field = 'pk'

class AircraftSerializerViewC(generics.ListCreateAPIView):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer

class LoadCaseSerializerView(generics.ListCreateAPIView):
    queryset = LoadCase.objects.all()
    serializer_class = LoadCaseSerializer

class AnalysisReportSerializerView(generics.ListCreateAPIView):
    queryset = AnalysisReport.objects.all()
    serializer_class = AnalysisReportSerializer
    

# ── Auth views ────────────────────────────────────────────────────────────────

def register_view(request):
    if request.method == 'POST':
        username  = request.POST['username']
        email     = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, f"Welcome, {username}! Account created.")
        return redirect('dashboard')

    return render(request, 'loads/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user     = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Invalid username or password.")
    return render(request, 'loads/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user        = request.user
    aircraft    = Aircraft.objects.filter(created_by=user)
    load_cases  = LoadCase.objects.filter(created_by=user).select_related('aircraft')
    reports     = AnalysisReport.objects.filter(analyst=user)
    critical    = load_cases.filter(is_critical=True)
    # Build chart data safely in Python — not in the template
    chart_data = json.dumps([
        {
            'name': lc.name,
            'nz':   lc.load_factor_nz,
        }
        for lc in load_cases[:10]
    ])
    context = {
        'aircraft_count':   aircraft.count(),
        'load_case_count':  load_cases.count(),
        'critical_count':   critical.count(),
        'report_count':     reports.count(),
        'recent_cases':     load_cases[:5],
        'recent_aircraft':  aircraft[:4],
        'chart_data':      chart_data,
    }
    return render(request, 'loads/dashboard.html', context)


# ── Aircraft views ─────────────────────────────────────────────────────────────

@login_required
def aircraft_list(request):
    aircraft = Aircraft.objects.filter(created_by=request.user)
    return render(request, 'loads/aircraft_list.html', {'aircraft': aircraft})


@login_required
def aircraft_create(request):
    form = AircraftForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)   # don't save to DB yet
        obj.created_by = request.user   # inject the current user
        obj.save()
        messages.success(request, f"Aircraft '{obj.name}' created.")
        return redirect('aircraft-list')
    return render(request, 'loads/aircraft_form.html', {'form': form, 'title': 'Add Aircraft'})


@login_required
def aircraft_delete(request, pk):
    aircraft = get_object_or_404(Aircraft, pk=pk, created_by=request.user)
    if request.method == 'POST':
        aircraft.delete()
        messages.success(request, "Aircraft deleted.")
        return redirect('aircraft-list')
    return render(request, 'loads/confirm_delete.html', {'obj': aircraft})


# ── LoadCase views ─────────────────────────────────────────────────────────────

@login_required
def loadcase_list(request):
    cases = LoadCase.objects.filter(
        created_by=request.user
    ).select_related('aircraft')
    return render(request, 'loads/loadcase_list.html', {'cases': cases})


@login_required
def loadcase_detail(request, pk):
    case = get_object_or_404(LoadCase, pk=pk, created_by=request.user)
    report = getattr(case, 'report', None)   # OneToOne — may not exist yet
    return render(request, 'loads/loadcase_detail.html', {
        'case': case,
        'report': report
    })


@login_required
def loadcase_create(request):
    form = LoadCaseForm(request.POST or None)
    # Limit aircraft dropdown to user's own aircraft only
    form.fields['aircraft'].queryset = Aircraft.objects.filter(created_by=request.user)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.save()
        messages.success(request, f"Load case '{obj.name}' created.")
        return redirect('loadcase-list')
    return render(request, 'loads/loadcase_form.html', {'form': form, 'title': 'New Load Case'})


@login_required
def loadcase_edit(request, pk):
    case = get_object_or_404(LoadCase, pk=pk, created_by=request.user)
    form = LoadCaseForm(request.POST or None, instance=case)
    form.fields['aircraft'].queryset = Aircraft.objects.filter(created_by=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Load case updated.")
        return redirect('loadcase-detail', pk=pk)
    return render(request, 'loads/loadcase_form.html', {'form': form, 'title': 'Edit Load Case'})


@login_required
def loadcase_delete(request, pk):
    case = get_object_or_404(LoadCase, pk=pk, created_by=request.user)
    if request.method == 'POST':
        case.delete()
        messages.success(request, "Load case deleted.")
        return redirect('loadcase-list')
    return render(request, 'loads/confirm_delete.html', {'obj': case})


# ── Report views ───────────────────────────────────────────────────────────────

@login_required
def report_create(request, pk):
    case = get_object_or_404(LoadCase, pk=pk, created_by=request.user)
    # Prevent duplicate reports
    if hasattr(case, 'report'):
        messages.warning(request, "Report already exists. Edit it instead.")
        return redirect('loadcase-detail', pk=pk)
    form = AnalysisReportForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.load_case = case
        obj.analyst   = request.user
        obj.save()
        messages.success(request, "Analysis report saved.")
        return redirect('loadcase-detail', pk=pk)
    return render(request, 'loads/report_form.html', {'form': form, 'case': case})


# ── CSV Export ─────────────────────────────────────────────────────────────────

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="load_cases.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Aircraft', 'Maneuver', 'Flight Phase',
        'Load Factor (g)', 'Speed (KTAS)', 'Altitude (ft)',
        'Dynamic Pressure (Pa)', 'Severity', 'Critical'
    ])
    for lc in LoadCase.objects.filter(created_by=request.user).select_related('aircraft'):
        writer.writerow([
            lc.name,
            lc.aircraft.name,
            lc.get_maneuver_type_display(),
            lc.get_flight_phase_display(),
            lc.load_factor_nz,
            lc.speed_ktas,
            lc.altitude_ft,
            lc.dynamic_pressure,
            lc.severity_label,
            'Yes' if lc.is_critical else 'No',
        ])
    return response