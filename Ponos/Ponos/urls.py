from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from sray.views import index, voting, vote

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('nomination/<int:nomination_id>/', voting, name='voting'),
    path('nomination/<int:nomination_id>/vote/', vote, name='vote'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'sray.views.custom_404'
handler500 = 'sray.views.custom_500'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)