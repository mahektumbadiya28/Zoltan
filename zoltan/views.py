import json
import random
from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone

# In-memory storage for pending admin multi-factor authorizations
TEMP_OTP_STORAGE = {}
BACKUP_OTP_EMAIL = 'mahek282007@gmail.com'


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
                
                # Send email out safely if email backend configs exist
                try:
                    recipient_list = list({user.email, BACKUP_OTP_EMAIL})
                    send_mail(
                        subject='🚨 Zoltan Security Authorization Code',
                        message=f'Your administrative access code is: {otp_token}. This code expires in 3 minutes.',
                        from_email='security@zoltan.local',
                        recipient_list=recipient_list,
                        fail_silently=True,
                    )
                except Exception:
                    pass
                
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
                    login(request, user)
                    
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
    Primary Administrative Control Room View. 
    """
    context = {
        'admin_user': request.user,
        'last_login': request.user.last_login if request.user.last_login else timezone.now(),
    }
    return render(request, 'dashboard.html', context)


# =====================================================================
# 🔄 ASYNCHRONOUS INTERACTIVE DATA TOGGLE API PORTS
# =====================================================================

@login_required(login_url='/')
def toggle_task_api(request, task_id):
    """Asynchronously switches a schedule task status between complete and pending."""
    return JsonResponse({'status': 'error', 'message': 'Not implemented'}, status=400)


@login_required(login_url='/')
def toggle_milestone_api(request, milestone_id):
    """Asynchronously switches a learning roadmap milestone mastery status checkbox."""
    return JsonResponse({'status': 'error', 'message': 'Not implemented'}, status=400)


def create_interview(request):
    """Create interview pipeline."""
    return JsonResponse({'status': 'error', 'message': 'Not implemented'}, status=400)


def run_ingestion_api(request):
    """Scraper API endpoint."""
    return JsonResponse({'status': 'error', 'message': 'Not implemented'}, status=400)


def send_otp(request):
    send_otp_email("user@example.com", "123456")
    return JsonResponse({"status": "Email sent"})