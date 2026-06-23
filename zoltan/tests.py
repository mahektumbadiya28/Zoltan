from django.test import TestCase

# Create your tests here.
# zoltan/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Opportunity

class ZoltanCoreTests(TestCase):
    
    def setUp(self):
        """Set up standard testing configurations and database records."""
        self.client = Client()
        
        # 1. Create a dummy superuser/admin for authentication testing
        self.admin_user = User.objects.create_superuser(
            username='admin@zoltan.local',
            email='admin@zoltan.local',
            password='securepassword123'
        )
        
        # 2. Add a sample mock Opportunity database entry
        self.sample_op = Opportunity.objects.create(
            title="Software Engineering Intern",
            company="Zoltan Labs",
            location="Remote",
            apply_url="https://zoltan.local/apply/1",
            source="Test Engine"
        )

    # ==========================================
    # 💾 DATA MODEL LAYER TESTS
    # ==========================================
    def test_opportunity_creation(self):
        """Validates that a model entry correctly saves attributes."""
        record = Opportunity.objects.get(id=self.sample_op.id)
        self.assertEqual(record.title, "Software Engineering Intern")
        self.assertEqual(record.company, "Zoltan Labs")
        self.assertEqual(str(record), "Software Engineering Intern at Zoltan Labs")

    # ==========================================
    # 🔒 ACCESS & PROTECTION TESTS
    # ==========================================
    def test_dashboard_unauthenticated_redirect(self):
        """Ensures unauthenticated requests to the dashboard are blocked and redirected."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect to root login

    def test_api_unauthenticated_denial(self):
        """Ensures that unauthenticated requests to the API positions route get a 403 Forbidden error."""
        response = self.client.get(reverse('api_positions_list'))
        self.assertEqual(response.status_code, 403)

    # ==========================================
    # ⚙️ REST API ENDPOINT TESTS
    # ==========================================
    def test_api_positions_list_authenticated(self):
        """Validates that an authenticated user can read entries from the REST API pipeline."""
        # Log the test client session in matching your superuser profile
        self.client.force_login(self.admin_user)
        
        response = self.client.get(reverse('api_positions_list'))
        self.assertEqual(response.status_code, 200)
        
        # Parse returned JSON structure keys
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['data'][0]['company'], "Zoltan Labs")