# Create or edit zoltan/forms.py
from django import forms
from .models import InterviewPipeline

class InterviewPipelineForm(forms.ModelForm):
    class Meta:
        model = InterviewPipeline
        fields = ['company_name', 'role_title', 'status', 'date_scheduled', 'notes']
        widgets = {
            'company_name': forms.TextInput(attrs={'style': 'width:100%; padding:0.5rem; border-radius:4px; border:1px solid var(--border); background:var(--bg); color:var(--text);'}),
            'role_title': forms.TextInput(attrs={'style': 'width:100%; padding:0.5rem; border-radius:4px; border:1px solid var(--border); background:var(--bg); color:var(--text);'}),
            'status': forms.TextInput(attrs={'style': 'width:100%; padding:0.5rem; border-radius:4px; border:1px solid var(--border); background:var(--bg); color:var(--text);'}),
            'date_scheduled': forms.DateTimeInput(attrs={'type': 'datetime-local', 'style': 'width:100%; padding:0.5rem; border-radius:4px; border:1px solid var(--border); background:var(--bg); color:var(--text);'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'style': 'width:100%; padding:0.5rem; border-radius:4px; border:1px solid var(--border); background:var(--bg); color:var(--text);'}),
        }