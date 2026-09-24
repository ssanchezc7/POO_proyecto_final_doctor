"""
URL configuration for proy_clinico project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from applications.security.views.home import ModuloTemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ModuloTemplateView.as_view(), name='home'),
    path('auth/', include('applications.security.urls')),
    path('doctor/', include('applications.doctor.urls')),
    path('core/', include('applications.core.urls')),
    path('chatbot/', include('applications.chatbot.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
