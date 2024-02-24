"""
URL configuration for ANT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path

import core.views

urlpatterns = [
    path("", core.views.index, name="index"),
    path("config/", core.views.config, name="config"),
    path("db/", core.views.db, name="db"),
    path("entities/", core.views.entities, name="entities"),
    path("entity/", core.views.entity, name="entity"),
    # Uncomment this and the entry in `INSTALLED_APPS` if you wish to use the Django admin feature:
    # https://docs.djangoproject.com/en/5.0/ref/contrib/admin/
    # path("admin/", admin.site.urls),
]
