"""app URL Configuration

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
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

import testsuite
from testsuite.views import LeaderBoardView

handler400 = 'testsuite.views.handler400'
handler403 = 'testsuite.views.handler403'
handler404 = 'testsuite.views.handler404'
handler500 = 'testsuite.views.handler500'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('user_account.urls')),
    path('leaderboard/', LeaderBoardView.as_view(), name='leaderboard'),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('tests/', include('testsuite.urls')),

]

urlpatterns += \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += \
    static(settings.STATIC_URL, document_root=settings.STATIC_URL)