"""
URL configuration for professor_rating project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from ratings import views

from django.contrib import admin
from django.urls import path, include
from ratings import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rate/', views.rate_professor, name='rate_professor'),
    path('list-modules/', views.list, name='list'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('average-rating/', views.average_rating, name='average-rating'),
    path('ratings/', views.ratings_list, name='ratings_list'),
]