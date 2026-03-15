from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/',       views.register_view,  name='register'),
    path('login/',          views.login_view,      name='login'),
    path('logout/',         views.logout_view,     name='logout'),

    # Dashboard
    path('',                views.dashboard,       name='dashboard'),

    # Aircraft
    path('aircraft/',              views.aircraft_list,   name='aircraft-list'),
    path('aircraft/new/',          views.aircraft_create, name='aircraft-create'),
    path('aircraft/<int:pk>/delete/', views.aircraft_delete, name='aircraft-delete'),

    # Load Cases
    path('loadcases/',                  views.loadcase_list,   name='loadcase-list'),
    path('loadcases/new/',              views.loadcase_create, name='loadcase-create'),
    path('loadcases/<int:pk>/',         views.loadcase_detail, name='loadcase-detail'),
    path('loadcases/<int:pk>/edit/',    views.loadcase_edit,   name='loadcase-edit'),
    path('loadcases/<int:pk>/delete/',  views.loadcase_delete, name='loadcase-delete'),

    # Reports
    path('loadcases/<int:pk>/report/',  views.report_create,   name='report-create'),

    # Export
    path('export/csv/',                 views.export_csv,      name='export-csv'),
]