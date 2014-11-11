from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('process.views',
    #url(r'^$', 'busca_proc', name='busca_proc_web'),
    #url(r'^meus_processos/$', 'busca_proc_web'),
    url(r'^tj/$', 'mock_data'),
    url(r'^add/$', 'adiciona_processo'),
    url(r'^delete/(?P<processo>\w+)/$', 'deleta_processo'),
    url(r'^detail/(?P<processo>\w+)/$', 'busca_processo'),
    url(r'^list/(?P<proc_list>\w+)/$', 'busca_processos'),
    
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += patterns('django.contrib.auth',
    url(r'^login/$', 'views.login', {'template_name': 'juris/login.html'}),
    url(r'^logout/$', 'views.logout_then_login', name='logout'),
)
