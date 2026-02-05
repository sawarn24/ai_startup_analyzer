import google.generativeai as genai
import os
import json

from config import settings
GEMINI_API_KEY = settings.GEMINI_API_KEY
from langchain_groq import ChatGroq
groq_api_key= settings.GROQ_API_KEY

class DataExtractionAgent:
    """Agent to extract structured data from documents"""
    
    def __init__(self, rag_system):
        self.rag = rag_system
        self.model =ChatGroq(groq_api_key=groq_api_key,model="openai/gpt-oss-120b",temperature=0.7)
    
    def extract(self, startup_id):
        """Extract all structured data"""
        
        print("🔍 Agent 1: Extracting structured data...")
        
        # Query RAG for different information
        company_context = self.rag.query(
            "What is the company name, sector, industry, and location?",
            startup_id,
            n_results=3
        )
        
        business_context = self.rag.query(
            "What problem are they solving? What is their solution? Who are their target customers? What is their business model?",
            startup_id,
            n_results=5
        )
        
        metrics_context = self.rag.query(
            "What are the financial metrics: revenue, MRR, ARR, growth rate, customers, burn rate, runway?",
            startup_id,
            n_results=5
        )
        
        team_context = self.rag.query(
            "Who are the founders? What is the team size? What is their experience?",
            startup_id,
            n_results=3
        )
        
        market_context = self.rag.query(
            "What is the market size? TAM, SAM, SOM? Market opportunity?",
            startup_id,
            n_results=3
        )
        
        funding_context = self.rag.query(
            "How much funding have they raised? From which investors? What round?",
            startup_id,
            n_results=3
        )
        
        # Combine all contexts
        full_context = f"""
COMPANY INFORMATION:
{company_context}

BUSINESS MODEL:
{business_context}

FINANCIAL METRICS:
{metrics_context}

TEAM:
{team_context}

MARKET:
{market_context}

FUNDING:
{funding_context}
"""
        
        prompt = f"""
You are a professional data extraction specialist for venture capital analysis.

Extract structured information from these startup documents and return ONLY valid JSON (no markdown, no explanation).

DOCUMENTS:
{full_context}

Return this EXACT JSON structure:
{{
  "company_info": {{
    "name": "company name or Unknown",
    "sector": "SaaS/FinTech/HealthTech/E-commerce/AI/EdTech/etc or Unknown",
    "stage": "Pre-seed/Seed/Series A/Series B/etc or Unknown",
    "founded_year": year_number_or_null,
    "location": "City, Country or Unknown"
  }},
  "business": {{
    "problem": "brief problem description or Not stated",
    "solution": "brief solution description or Not stated",
    "target_market": "target customer description or Not stated",
    "business_model": "revenue model description or Not stated",
    "unique_value_prop": "what makes them unique or Not stated",
    "market_size_tam": "TAM value with currency or Not stated"
  }},
  "metrics": {{
    "mrr": number_or_null,
    "arr": number_or_null,
    "revenue": number_or_null,
    "growth_rate_monthly": "percentage_string_or_null",
    "customers": number_or_null,
    "burn_rate_monthly": number_or_null,
    "runway_months": number_or_null,
    "churn_rate": "percentage_string_or_null"
  }},
  "team": {{
    "founders": ["list", "of", "names"],
    "total_employees": number_or_null,
    "key_hires": ["list of key positions filled"]
  }},
  "funding": {{
    "total_raised": number_or_null,
    "last_round": "round_name_or_null",
    "last_round_amount": number_or_null,
    "investors": ["list", "of", "investors"]
  }},
  "traction": {{
    "product_status": "Idea/MVP/Beta/Live/Scaling or Unknown",
    "customer_examples": ["list of notable customers if mentioned"],
    "partnerships": ["list of partnerships if mentioned"],
    "awards": ["list of awards if mentioned"]
  }}
}}

Rules:
- Use null for missing numbers
- Use "Unknown" or "Not stated" for missing text
- Extract exact values when available
- Be conservative, don't make up data
- Return ONLY the JSON object, no other text
"""
        
        try:
            response = self.model.invoke(prompt)
            response_text = response.text.strip()
            
            # Clean JSON response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            data = json.loads(response_text)
            
            print("✅ Data extraction complete!")
            return data
            
        except Exception as e:
            print(f"❌ Error in data extraction: {e}")
            return self._get_default_structure()
    
    def _get_default_structure(self):
        """Default structure if extraction fails"""
        return {
            "company_info": {
                "name": "Unknown",
                "sector": "Unknown",
                "stage": "Unknown",
                "founded_year": None,
                "location": "Unknown"
            },
            "business": {
                "problem": "Not stated",
                "solution": "Not stated",
                "target_market": "Not stated",
                "business_model": "Not stated",
                "unique_value_prop": "Not stated",
                "market_size_tam": "Not stated"
            },
            "metrics": {
                "mrr": None,
                "arr": None,
                "revenue": None,
                "growth_rate_monthly": None,
                "customers": None,
                "burn_rate_monthly": None,
                "runway_months": None,
                "churn_rate": None
            },
            "team": {
                "founders": [],
                "total_employees": None,
                "key_hires": []
            },
            "funding": {
                "total_raised": None,
                "last_round": None,
                "last_round_amount": None,
                "investors": []
            },
            "traction": {
                "product_status": "Unknown",
                "customer_examples": [],
                "partnerships": [],
                "awards": []
            }

        }

