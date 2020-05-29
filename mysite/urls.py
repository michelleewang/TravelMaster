"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from travelmaster import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    # images using vision API
    path('images/', views.images, name='images'),
    path('detectText/', views.detectText, name='detectText'),
    path('detectLandmark/', views.detectLandmark, name='detectLandmark'),
    path('detectFaces/', views.detectFaces, name='detectFaces'),

    # translation using translation API
    path('translation/', views.translation, name='translation'),

    # maps API
    path('navigation/', views.navigation, name='navigation'),
]
