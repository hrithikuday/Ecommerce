from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from xeon import views as xeon_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('xeon.urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Global custom 404 view handler
handler404 = 'xeon.views.custom_404_view'

# Catch-all pattern to display custom 404 page in local testing (DEBUG = True)
urlpatterns += [
    re_path(r'^.*$', xeon_views.custom_404_view, name='custom_404'),
]
