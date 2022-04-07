from django.urls import path
from django.conf.urls import url


from . import views
from .views import (
    CommodityDetailView,
    CommodityListView,
  
  
)

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),

    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    path('user/', views.user, name='user'),
    path('support/', views.support, name='support'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('farmer/', views.farmer, name='farmer'),
    path('supplier/', views.supplier, name='supplier'),
    path('news/', views.news, name='news'),
    path('commodity_info/', views.commodity_info, name='commodity_info'),
    path('commodity_info/<slug>/', CommodityDetailView.as_view(), name='commodity_info'),
    path('subscription/', views.subscription, name='subs'),
    path('function/', CommodityListView.as_view(), name='function'),
    path('usermanual/',views.usermanual, name='usermanual'),
    # url(r'^$', views.Predict, name='blog-home'),
    url(r'^dashboard/model/$',views.data_Predict,name="model"),
]


