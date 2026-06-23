import json
import random
import pandas as pd
from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone

# Django REST Framework Imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# Local App Imports
from .models import Opportunity, ScheduleTask, RoadmapTrack, RoadmapMilestone, InterviewPipeline, InterviewQuestion
from .forms import InterviewPipelineForm
from .scraper import scrape_live_opportunities
from .analytics import generate_market_insights

# In-memory storage for pending admin multi-factor authorizations
# Format: { email: {"otp": "123456", "expires_at": datetime_object} }
TEMP_OTP_STORAGE = {}


# =====================================================================
# 🔑 MULTI-FACTOR SECURITY AUTHENTICATION FLOW
# =====================================================================

def admin_login_step1(request):
    """
    Step 1: Validates basic administrator password credentials.
    Generates an OTP token, saves it to memory, prints it to the console, and emails it.
    """
    if request.method == 'POST':
        try:
            # Handle standard form data or asynchronous fetch JSON payloads
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                email = data.get('email')
                password = data.get('password')
            else:
                email = request.POST.get('email')
                password = request.POST.get('password')

            # Authenticate user via email address matching
            user = authenticate(request, username=email, password=password)
            
            if user is not None and user.is_staff:
                # Generate a 6-digit numeric OTP token string valid for 3 minutes
                otp_token = str(random.randint(100000, 999999))
                expiration_time = timezone.now() + timedelta(minutes=3)
                
                # Keep record inside our in-memory cache dict
                TEMP_OTP_STORAGE[email] = {
                    "otp": otp_token,
                    "expires_at": expiration_time
                }
                
                # Write to a file for retrieval
                try:
                    with open("otp.txt", "w") as f:
                        f.write(otp_token)
                except Exception:
                    pass
                
                # Print to local console terminal workspace for easy copying
                print(f"\n[🔑 ZOLTAN MFA SECURITY] Core OTP Generated for {email} -> {otp_token}\n")
                
                # Optional: Send email out safely if email backend configs exist
                try:
                    send_mail(
                        subject='🚨 Zoltan Security Authorization Code',
                        message=f'Your administrative access code is: {otp_token}. This code expires in 3 minutes.',
                        from_email='security@zoltan.local',
                        recipient_list=[user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass # Keep going if local mail server configuration is absent
                
                return JsonResponse({
                    'status': 'success', 
                    'message': 'MFA Step 1 cleared. Check your mailbox/terminal for the secure OTP token.', 
                    'email': email
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Access Denied: Invalid credentials or insufficient permissions.'}, status=401)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return render(request, 'login.html')


def admin_login_step2(request):
    """
    Step 2: Verifies temporary OTP token values and time bounds to grant full session access.
    """
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                email = data.get('email')
                otp_input = data.get('otp')
            else:
                email = request.POST.get('email')
                otp_input = request.POST.get('otp')

            user_record = TEMP_OTP_STORAGE.get(email)

            if user_record:
                current_time = timezone.now()
                
                # Enforce signature verification matching and expiration bounds
                if user_record['otp'] == str(otp_input) and current_time < user_record['expires_at']:
                    user = User.objects.get(email=email)
                    login(request, user)  # Bind persistent secure session cookie token
                    
                    # Flush the memory lookup index clean
                    TEMP_OTP_STORAGE.pop(email, None)
                    return JsonResponse({'status': 'success', 'redirect_url': '/dashboard/'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Security validation error: Invalid or expired OTP token.'}, status=401)
            
            return JsonResponse({'status': 'error', 'message': 'Security record context missing or expired.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid layout method'}, status=400)


def admin_logout_view(request):
    """Flushes active tracking security tokens and terminates session context."""
    logout(request)
    return redirect('login_page')


# =====================================================================
# 📝 USER REGISTRATION / SIGNUP VIEW
# =====================================================================

def signup_view(request):
    """
    Handles new user registration.
    GET: Renders the signup form.
    POST: Creates a new user account in the database.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')

            if not email or not password:
                return JsonResponse({'status': 'error', 'message': 'Email and password are required.'}, status=400)

            if len(password) < 6:
                return JsonResponse({'status': 'error', 'message': 'Password must be at least 6 characters.'}, status=400)

            # Check if a user with this email already exists
            if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
                return JsonResponse({'status': 'error', 'message': 'An account with this email already exists.'}, status=409)

            # Create the user (username = email for this app)
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True  # Allow MFA login flow
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Account created successfully!'
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid request format.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return render(request, 'signup.html')

# =====================================================================
# 📊 MAIN SECURE CORE WORKSPACE DASHBOARD VIEW
# =====================================================================

@login_required(login_url='/')
def dashboard_view(request):
    """
    Primary Administrative Control Room View. Handles pipeline submissions, 
    ORM queries, and analytical compilation.
    """
    # Inside zoltan/views.py (dashboard_view function context block)

    # Handle New Interview Pipeline Form Submission via Dashboard Modal overlay
    if request.method == 'POST' and 'add_interview' in request.POST:
        form = InterviewPipelineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = InterviewPipelineForm()

    # Query core tracking tables
    opportunities_list = Opportunity.objects.all().order_by('-date_scraped')[:10]
    tasks_list = ScheduleTask.objects.all().order_by('created_at')
    roadmap_tracks = RoadmapTrack.objects.prefetch_related('milestones').all()
    interviews = InterviewPipeline.objects.prefetch_related('questions').all().order_by('date_scheduled')
    
    # Run predictive data insights parsing via Pandas
    insights = generate_market_insights()

    # -------------------------------------------------------------
    # BOILERPLATE SEEDING SYSTEM (Populates data on first runtime if blank)
    # -------------------------------------------------------------
    if not tasks_list.exists():
        ScheduleTask.objects.create(title="Review Core Django Authentication middleware flows", category="Security")
        ScheduleTask.objects.create(title="Execute exploratory analysis on student metrics dataset", category="Analytics")
        ScheduleTask.objects.create(title="Simulate backend API authentication responses via Postman", category="Testing")
        tasks_list = ScheduleTask.objects.all().order_by('created_at')

    if not roadmap_tracks.exists():
        web_track = RoadmapTrack.objects.create(title="Full-Stack Web Architecture")
        RoadmapMilestone.objects.create(track=web_track, title="Django REST Framework & Serializers", order=1)
        RoadmapMilestone.objects.create(track=web_track, title="MongoDB Atlas Cloud Integration", order=2)
        RoadmapMilestone.objects.create(track=web_track, title="Automated End-to-End Playwright Scrapers", order=3)
        
        logic_track = RoadmapTrack.objects.create(title="Digital Logic & Systems Design")
        RoadmapMilestone.objects.create(track=logic_track, title="Combinational Logic & 7447 Decoder ICs", order=1)
        RoadmapMilestone.objects.create(track=logic_track, title="Sequential State Machines & Finite Automata (DFA)", order=2)
        roadmap_tracks = RoadmapTrack.objects.prefetch_related('milestones').all()

    if not interviews.exists():
        mock_pipeline = InterviewPipeline.objects.create(
            company_name="Zoltan Automations",
            role_title="Associate Full-Stack Developer",
            status="Technical Practical Round",
            date_scheduled=timezone.now() + timedelta(days=2),
            notes="Be ready to discuss Django-to-MongoDB workflows and system logic integration."
        )
        InterviewQuestion.objects.create(
            pipeline=mock_pipeline,
            topic="Full-Stack Web Architecture",
            question_text="Explain how Django templates fetch and dynamically stream documents stored inside non-relational collection engines like MongoDB Atlas."
        )
        interviews = InterviewPipeline.objects.prefetch_related('questions').all().order_by('date_scheduled')

    context = {
        'opportunities': opportunities_list,
        'tasks': tasks_list,
        'tracks': roadmap_tracks,
        'interviews': interviews,
        'insights': insights,
        'interview_form': form,
        # Injected Profile Metrics Context
        'admin_user': request.user,
        'last_login': request.user.last_login if request.user.last_login else timezone.now(),
    }
    return render(request, 'dashboard.html', context)


# =====================================================================
# 🤖 SCRAPER CORE CONNECTOR AGENT VIEW
# =====================================================================

@login_required(login_url='/')
def run_ingestion_api(request):
    """
    Triggers the internal scraping agent, checks unique values using get_or_create
    to reject duplications, and returns operational data parameters.
    """
    if request.method == 'POST':
        scraped_data = scrape_live_opportunities()
        saved_count = 0
        
        for item in scraped_data:
            opportunity, created = Opportunity.objects.get_or_create(
                apply_url=item['apply_url'],
                defaults={
                    'title': item['title'],
                    'company': item['company'],
                    'location': item['location'],
                    'source': item['source']
                }
            )
            if created:
                saved_count += 1
                
        return JsonResponse({
            "status": "success",
            "message": f"Scraped successfully! Added {saved_count} brand new unique records to the database.",
            "records_found": len(scraped_data),
            "sample_data": scraped_data[:3]
        })
        
    return JsonResponse({"status": "error", "message": "Invalid extraction method request."}, status=400)


# =====================================================================
# 🔄 ASYNCHRONOUS INTERACTIVE DATA TOGGLE API PORTS
# =====================================================================

@login_required(login_url='/')
def toggle_task_api(request, task_id):
    """Asynchronously switches a schedule task status between complete and pending."""
    if request.method == 'POST':
        try:
            task = ScheduleTask.objects.get(id=task_id)
            task.is_completed = not task.is_completed
            task.save()
            return JsonResponse({'status': 'success', 'is_completed': task.is_completed})
        except ScheduleTask.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task profile not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request action protocol'}, status=400)


@login_required(login_url='/')
def toggle_milestone_api(request, milestone_id):
    """Asynchronously switches a learning roadmap milestone mastery status checkbox."""
    if request.method == 'POST':
        try:
            milestone = RoadmapMilestone.objects.get(id=milestone_id)
            milestone.is_mastered = not milestone.is_mastered
            milestone.save()
            return JsonResponse({'status': 'success', 'is_mastered': milestone.is_mastered})
        except RoadmapMilestone.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Milestone metadata matching record missing'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid method structure execution'}, status=400)


# =====================================================================
# 🌐 DJANGO REST FRAMEWORK INTERNAL OUTFLOW FORWARDER
# =====================================================================

class OpportunityListAPIView(APIView):
    """
    Secure REST API Endpoint to fetch and filter scraped data engine records.
    Accessible only to authenticated accounts.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        location_param = request.query_params.get('location', None)
        
        if location_param:
            records = Opportunity.objects.filter(location__icontains=location_param).order_by('-date_scraped')
        else:
            records = Opportunity.objects.all().order_by('-date_scraped')
            
        try:
            from .serializers import OpportunitySerializer
            serializer = OpportunitySerializer(records, many=True)
            return Response({
                "status": "success",
                "count": len(serializer.data),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except ImportError:
            # Fallback manual serialization array structure if no serializer file exists
            data = list(records.values('id', 'title', 'company', 'location', 'source', 'apply_url'))
            return Response({"status": "success", "count": len(data), "data": data}, status=status.HTTP_200_OK)

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def create_interview(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            company_name = data.get('company_name')
            role_title = data.get('role_title')
            status = data.get('status')
            date_scheduled = data.get('date_scheduled')
            
            if not all([company_name, role_title, status, date_scheduled]):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields.'}, status=400)
            
            # Save using standard Django ORM model instead of MongoDB
            InterviewPipeline.objects.create(
                company_name=company_name,
                role_title=role_title,
                status=status,
                date_scheduled=date_scheduled
            )
            
            return JsonResponse({'status': 'success', 'message': 'Pipeline track added successfully!'})
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)