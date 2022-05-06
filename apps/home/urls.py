
from django.urls import path, re_path
from apps.home import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [

    path('', views.index, name='home'),

    path('create-project', views.create_new_project, name='create_project'),

    path('category_form', views.add_category, name='create_category'),

    path('project-details/<int:project_id>', views.show_project_details, name='show_project'),

    path('project-details/<int:project_id>/donate', views.donate, name='donate'),

    path('project-details/<int:project_id>/comment', views.create_comment, name='create_comment'),

    path('project-details/<int:project_id>/cancel', views.cancel_project, name='cancel_project'),

    path('project-details/<int:project_id>/report', views.add_report, name='create_report'),

    path('project-details/<int:comment_id>/report_comment', views.add_comment_report, name='create_comment_report'),

    path('project-details/<int:comment_id>/reply', views.create_comment_reply, name='create_comment_reply'),

    path('projects', views.all_projects, name='all_projects'),

    path('projects/category/<int:category_id>', views.get_category_projects, name='get_category'),

    path('projects/tag/<int:tag_id>', views.get_tag_projects, name='get_tag'),

    path('projects/featured', views.get_featured_projects, name='featured_projects'),

    path('search-result', views.search, name='search-result'),

    path('<int:project_id>/rate', views.rate, name='project_rate'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
