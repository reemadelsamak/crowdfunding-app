
from django.urls import path, re_path
from apps.home import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [

    
    path('', views.index, name='home'),
    path('create-project', views.create_new_project, name='create_project'),
    
    path('project-details/<int:project_id>', views.show_project_details, name='show_project'),
    path('project-details/<int:project_id>/donate', views.donate, name = 'donate'),
    path('project-details/<int:project_id>/comment', views.create_comment, name = 'create_comment'),

    path('projects', views.all_projects, name = 'all_projects'),
    path('projects/category/<int:category_id>', views.get_category_projects, name = 'get_category'),
    path('projects/featured', views.get_featured_projects, name = 'featured_projects'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

