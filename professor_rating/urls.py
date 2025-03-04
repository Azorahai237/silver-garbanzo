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
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as authtoken_views
from ratings.views import ProfessorViewSet, ModuleViewSet, ModuleInstanceViewSet, RatingViewSet, RegisterView, RateProfessorView, AverageRatingView, RatingsListView, ListModulesView, LogoutView

router = DefaultRouter()
router.register(r'professors', ProfessorViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'module-instances', ModuleInstanceViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/token/', authtoken_views.obtain_auth_token, name='token_obtain_pair'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/rate/', RateProfessorView.as_view(), name='rate_professor'),
    path('api/average-rating/', AverageRatingView.as_view(), name='average_rating'),
    path('api/ratings-list/', RatingsListView.as_view(), name='ratings_list'),
    path('api/list-modules/', ListModulesView.as_view(), name='list_modules'),

]