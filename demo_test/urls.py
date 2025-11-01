from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect



# Redirect function for unmatched URLs
def redirect_to_home(request, path=None):
    return redirect('home')

urlpatterns = [
    path('admin-987/', admin.site.urls),
    path('', include('accounts.api_urls')),
]

# Serve static & media files in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Catch-all pattern for unmatched URLs (put **at the very end**)
urlpatterns += [
    re_path(r'^(?P<path>.*)$', redirect_to_home),
]
