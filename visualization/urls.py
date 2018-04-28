from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('docview/', views.doc_view, name='docview'),
    path('patentfile/', views.patent_file, name='patentfile'),
]