# zoltan/urls.py
from django.urls import path
from django.views.generic import TemplateView
from . import views
# from .views import OpportunityListAPIView

urlpatterns = [
    # Core Presentation View Layer Pages
    # path('', views.admin_login_step1, name='login_page'),
    # path('signup/', views.signup_view, name='signup_page'),
    # path('dashboard/', views.dashboard_view, name='dashboard'),
    # path('logout/', views.admin_logout_view, name='logout_action'),

    # # Multi-Factor Verification Backed Endpoints
    # path('admin-login-step1/', views.admin_login_step1, name='admin_login_step1'),
    # path('admin-login-step2/', views.admin_login_step2, name='admin_login_step2'),
    
    # # Scraper Aggregator Trigger Route
    # path('api/run-scraper/', views.run_ingestion_api, name='run_scraper_api'),
    
    # # Django REST Framework Data Endpoint JSON Outflow
    # path('api/positions/', OpportunityListAPIView.as_view(), name='api_positions_list'),
    
    # # Asynchronous Interactivity Toggle API Pipeline 
    # path('api/tasks/<int:task_id>/toggle/', views.toggle_task_api, name='toggle_task_api'),
    # path('api/milestones/<int:milestone_id>/toggle/', views.toggle_milestone_api, name='toggle_milestone_api'),
    # path('api/interviews/create/', views.create_interview, name='create_interview'),

    path('api/send-otp/', views.send_otp, name='send_otp'),     
]
