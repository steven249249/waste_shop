"""waste URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path,re_path,include
from linefunc import views as lb
from django.conf.urls import url
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^js_error_hook/', include('django_js_error_hook.urls')),
    path('',lb.callback),
    path('store_give/',lb.store_give),
    path('user_get_store_food/',lb.user_get_store_food),
    path('store_check_order/',lb.store_check_order),
    path('detail_order/',lb.detail_order),
    path('test/',lb.test),
    path('user_check_order/',lb.user_check_order),
    path('change_description/',lb.change_description),
    path('user_pay/',lb.user_pay),
    path('rating/',lb.rating),
    path('subscribe_check/',lb.subscribe_check),
]
urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)