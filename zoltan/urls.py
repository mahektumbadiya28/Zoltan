# # zoltan/urls.py
# from django.urls import path
# from django.views.generic import TemplateView
# from . import views
# from .views import OpportunityListAPIView

# urlpatterns = [
#     # Static Page Routes
#     path('', TemplateView.as_view(template_name='login.html'), name='login_page'),
#     path('dashboard/', views.dashboard_view, name='dashboard'),

#     # Backend Secure Multi-Factor AJAX Endpoints
#     path('admin-login-step1/', views.admin_login_step1, name='admin_login_step1'),
#     path('admin-login-step2/', views.admin_login_step2, name='admin_login_step2'),
#     path('', views.admin_login_step1, name='login_step1'),
#     path('verify-otp/', views.admin_login_step2, name='login_step2'),
#     path('dashboard/', views.dashboard_view, name='dashboard'),
  
#     # Add this path rule to your existing zoltan/urls.py urlpatterns list
#     path('api/run-scraper/', views.run_ingestion_api, name='run_scraper_api'),
#     path('api/positions/', OpportunityListAPIView.as_view(), name='api_positions_list'),
#     path('logout/', views.admin_logout_view, name='logout_action'),
#     # Add this path layout inside your zoltan/urls.py patterns array:

# path('api/tasks/<int:task_id>/toggle/', views.toggle_task_api, name='toggle_task_api'),

# # Add this path layout rule inside your zoltan/urls.py patterns array:

# path('api/milestones/<int:milestone_id>/toggle/', views.toggle_milestone_api, name='toggle_milestone_api'),
# ]

# zoltan/urls.py
from django.urls import path
from django.views.generic import TemplateView
from . import views
from .views import OpportunityListAPIView # REST API view built previously

urlpatterns = [
    # Core Presentation View Layer Pages
    path('', views.admin_login_step1, name='login_page'),
    path('signup/', views.signup_view, name='signup_page'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.admin_logout_view, name='logout_action'),

    # Multi-Factor Verification Backed Endpoints
    path('admin-login-step1/', views.admin_login_step1, name='admin_login_step1'),
    path('admin-login-step2/', views.admin_login_step2, name='admin_login_step2'),
    
    # Scraper Aggregator Trigger Route
    path('api/run-scraper/', views.run_ingestion_api, name='run_scraper_api'),
    
    # Django REST Framework Data Endpoint JSON Outflow
    path('api/positions/', OpportunityListAPIView.as_view(), name='api_positions_list'),
    
    # Asynchronous Interactivity Toggle API Pipeline 
    path('api/tasks/<int:task_id>/toggle/', views.toggle_task_api, name='toggle_task_api'),
    path('api/milestones/<int:milestone_id>/toggle/', views.toggle_milestone_api, name='toggle_milestone_api'),
    path('api/interviews/create/', views.create_interview, name='create_interview'),
]