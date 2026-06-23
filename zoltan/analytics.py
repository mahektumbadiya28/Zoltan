# zoltan/analytics.py
import pandas as pd
from .models import Opportunity

def generate_market_insights():
    """
    Uses Pandas to analyze scraped opportunities from the database.
    Returns metrics ready for dashboard display.
    """
    # 1. Fetch data directly from the Django ORM database model
    queryset = Opportunity.objects.all().values('title', 'company', 'location')
    
    if not queryset.exists():
        return {
            "total_records": 0,
            "top_companies": [],
            "top_locations": []
        }
        
    # 2. Load the dataset into a Pandas DataFrame
    df = pd.DataFrame(list(queryset))
    
    # 3. Perform data grouping and calculations
    total_records = len(df)
    
    # Calculate top 3 companies (Returns list of dicts: [{'company': 'X', 'count': Y}])
    top_companies_df = df['company'].value_counts().head(3).reset_index()
    top_companies_df.columns = ['company', 'count']
    top_companies = top_companies_df.to_dict(orient='records')
    
    # Calculate top 3 locations
    top_locations_df = df['location'].value_counts().head(3).reset_index()
    top_locations_df.columns = ['location', 'count']
    top_locations = top_locations_df.to_dict(orient='records')
    
    return {
        "total_records": total_records,
        "top_companies": top_companies,
        "top_locations": top_locations
    }