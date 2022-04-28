
from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('input-areas-forms', views.create_new_project, name='create_project'),
    
    path('project-details', views.show_project_details, name='show_project'),


    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
