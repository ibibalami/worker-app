from django.urls import path
from . import views

urlpatterns = [
    path('', views.worker_list, name='worker_list'),
    path('location-finder/', views.location_finder, name='location_finder'),
    path('upload-excel/', views.upload_excel_view, name='upload_excel'),

]
