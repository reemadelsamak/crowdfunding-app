
from django.urls import path, re_path
from apps.home import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [

    
    path('', views.index, name='home'),
    path('input-areas-forms', views.create_new_project, name='create_project'),
    
    path('project-details/<int:project_id>', views.show_project_details, name='show_project'),
    path('project-details/<int:project_id>/donate', views.donate, name = 'donate'),
    path('project-details/<int:project_id>/comment', views.create_comment, name = 'create_comment'),


    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

