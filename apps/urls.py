
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views
from django.conf.urls.static import static

from forms import AuthForm
from auto_chess_engine.views import *
from views import *

urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'', include('auto_chess_engine.urls')),
	url(r'^login/$', views.login, {'template_name': 'auto_chess_engine/login.html', 'authentication': AuthForm }),
	url(r'^register/$', views.RegisterView.as_view(), name='register'),
	url(r'^profile/(?P<pk>[0-9]+)$', views.ProfileView.as_view(), name='profile'),
	url(r'^profile/(?P<pk>[0-9]+)/history/(?P<type>[a-Z]+)$', views.ProfileShowRankingHistoryView.as_view(), name='show-ranking-history'),
	url(r'^profile/(?P<pk>[0-9]+)/load_data$', views.ProfileLoadData.as_view(), name='profile-load-data'),
	url(r'^profile/(?P<pk>[0-9]+)/(?P<update_type>[a-Z]+)/(?P<key>[a-zA-Z0-9_]+)/(?P<value>[a-zA-Z0-9_ -]+)$', views.ProfileUpdateKeyView.as_view(), name='profile-update-key'),
	url(r'^logout/$', views.logout, {'next_page': '/login'}, name='logout'),
	url(r'^docs/$', views.DocsView.as_view(), name='docs')
]
