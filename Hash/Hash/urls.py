from django.contrib import admin
from django.urls import path
from newad.views import *


urlpatterns = [
    path("admin/", admin.site.urls),
    path('ads/', AdViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('ads/<int:pk>/', AdViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('ads/<int:ad_id>/report/', DailyVisitorReportView.as_view(), name='daily-visitor-report'),
    path('ads/<int:ad_id>/block/<int:loc_id>/', BlockAdView.as_view(), name='block-loc-ad')
]
