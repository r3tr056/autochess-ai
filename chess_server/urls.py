
from django.contrib import admin
from django.urls import path, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'^$', views.HomeView.as_view(), name='home'),
    # game api
    re_path(r'^game/add$', game_views.CreateChessGameView.as_view(), name='create-game'),
    re_path(r'^game/join_game/(?P<pk>[0-9]+)/(?P<side>[wb])$', game_views.JoinGameView.as_view(), 'chess-game')
    re_path(r'^game/(?P<pk>[0-9]+)/board/cell_click/(?P<action>[a-z]+)/(?P<line>[0-9]+)/(?P<column>[a-h]+)$', game_views.PieceActionView.as_view(), name='piece-action')
    re_path(r'^game/(?P<pk>[0-9]+)/board/promote/(?P<role_name>[QRBH])$', game_views.PiecePromoteView.as_view(), name='piece-promote'),
]
