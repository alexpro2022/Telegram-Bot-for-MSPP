from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import settings
from apps.bot.views import application_form

urlpatterns = [
    path("admin/", admin.site.urls),
    path("bot/", include("bot.urls")),
    path("", application_form, name="application_form")
]

if settings.DEBUG:
    urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
