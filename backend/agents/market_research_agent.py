import google.generativeai as genai
import os
import json
import requests

from config import settings
GEMINI_API_KEY = settings.GEMINI_API_KEY
GOOGLE_SEARCH_API_KEY= settings.GOOGLE_SEARCH_API_KEY
SEARCH_ENGINE_ID= settings.SEARCH_ENGINE_ID
from langchain_groq import ChatGroq
groq_api_key= settings.GROQ_API_KEY
class MarketResearchAgent:
    """Agent to validate claims with web research"""
    
    def __init__(self, rag_system):
        self.rag = rag_system
        self.model = ChatGroq(groq_api_key=groq_api_key,model="openai/gpt-oss-120b",temperature=0.7)
    
    def research(self, startup_id, extracted_data):
        """Conduct market research and validation"""
        
        print("🔍 Agent 4: Conducting market research...")
        
        company_name = extracted_data.get('company_info', {}).get('name', 'Unknown')
        sector = extracted_data.get('company_info', {}).get('sector', 'Unknown')
        
        # Search for company
        company_results = self._google_search(f"{company_name} startup")
        
        # Search for market size validation
        market_query = f"{sector} market size 2024"
        market_results = self._google_search(market_query)
        
        # Search for competitors
        competitor_query = f"{sector} startups competitors"
        competitor_results = self._google_search(competitor_query)
        
        prompt = f"""
You are a market research analyst.

COMPANY CLAIMS (from pitch deck):
{json.dumps(extracted_data, indent=2)}

PUBLIC SEARCH RESULTS:

Company Search Results:
{json.dumps(company_results, indent=2)}

Market Size Results:
{json.dumps(market_results, indent=2)}

Competitor Results:
{json.dumps(competitor_results, indent=2)}

Validate the startup's claims and return ONLY valid JSON:

{{
  "validations": {{
    "market_size": {{
      "claimed": "What they claimed",
      "found": "What research shows",
      "status": "Verified|Inflated|Conservative|Unable to verify",
      "notes": "Explanation"
    }},
    "competitors": {{
      "claimed": "Their claim about competition",
      "found": ["List", "of", "actual", "competitors"],
      "status": "Accurate|Understated|Overstated",
      "notes": "Explanation"
    }},
    "company_presence": {{
      "found_online": true_or_false,
      "news_mentions": number,
      "credibility": "High|Medium|Low",
      "notes": "What was found"
    }}
  }},
  "market_insights": {{
    "market_trend": "Growing|Stable|Declining|Emerging",
    "market_maturity": "Nascent|Growing|Mature|Saturated",
    "opportunity_score": number_from_1_to_10,
    "notes": "Key market insights"
  }},
  "credibility_score": number_from_0_to_100
}}

Return ONLY JSON.
"""
        
        try:
            response = self.model.invoke(prompt)
            response_text = response.text.strip()
            
            
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            data = json.loads(response_text)
            
            print("✅ Market research complete!")
            return data
            
        except Exception as e:
            print(f"❌ Error in market research: {e}")
            return self._get_default_structure()
    
    def _google_search(self, query, num_results=5):
        """Search Google using Custom Search API"""
        if not GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_API_KEY == "YOUR_SEARCH_API_KEY_HERE":
            print("⚠️ Google Search API not configured, skipping web search")
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': GOOGLE_SEARCH_API_KEY,
                'cx': SEARCH_ENGINE_ID,
                'q': query,
                'num': num_results
            }
            
            response = requests.get(url, params=params)
            results = response.json()
            
            if 'items' in results:
                return [
                    {
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'link': item.get('link', '')
                    }
                    for item in results['items']
                ]
            
            return []
            
        except Exception as e:
            print(f"⚠️ Google Search error: {e}")
            return []
    
    def _get_default_structure(self):
        return {
            "validations": {
                "market_size": {
                    "claimed": "Unknown",
                    "found": "Unable to verify",
                    "status": "Unable to verify",
                    "notes": "Research unavailable"
                },
                "competitors": {
                    "claimed": "Unknown",
                    "found": [],
                    "status": "Unable to verify",
                    "notes": "Research unavailable"
                },
                "company_presence": {
                    "found_online": False,
                    "news_mentions": 0,
                    "credibility": "Low",
                    "notes": "No online presence found"
                }
            },
            "market_insights": {
                "market_trend": "Unknown",
                "market_maturity": "Unknown",
                "opportunity_score": 5,
                "notes": "Insufficient data"
            },
            "credibility_score": 50

        }


