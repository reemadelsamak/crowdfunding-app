# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path


from .views import user_login, signup,activate ,user_logout ,EditProfile, profile
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('login', user_login, name="login"),
    path('register', signup, name="register"),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,18})/',
         activate, name='activate'),
    path("logout", user_logout, name="logout"),
    path("profile/<int:id>" , profile , name="profile"),
    path('edit/profile/<int:id>', EditProfile, name="editProfile"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
