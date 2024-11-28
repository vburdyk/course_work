from django.urls import path
from . import views
urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('', views.dashboard, name='dashboard'),
    path('new_ticket/', views.new_ticket, name='new_ticket'),
    path('logout/', views.logout_user, name='logout'),
    path('add-subscription/', views.add_subscription_plan, name='add_subscription_plan'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('manage-tickets/', views.manage_tickets, name='manage_tickets'),

]

