import google.generativeai as genai
import os
import requests
import json
from config import settings
GEMINI_API_KEY = settings.GEMINI_API_KEY
GOOGLE_SEARCH_API_KEY= settings.GOOGLE_SEARCH_API_KEY
SEARCH_ENGINE_ID= settings.SEARCH_ENGINE_ID
from langchain_groq import ChatGroq
groq_api_key= settings.GROQ_API_KEY

class BenchmarkingAgent:
    """Agent to benchmark startup against industry peers"""
    
    def __init__(self, rag_system):
        self.rag = rag_system
        self.model = ChatGroq(groq_api_key=groq_api_key,model="openai/gpt-oss-120b",temperature=0.7)
    
    def benchmark(self, startup_id, extracted_data):
        """Benchmark startup against sector peers"""
        
        print("📊 Agent 2: Benchmarking against sector peers...")
        
        sector = extracted_data.get('company_info', {}).get('sector', 'Unknown')
        stage = extracted_data.get('company_info', {}).get('stage', 'Seed')
        
        # Search for sector benchmarks
        benchmark_queries = [
            f"{sector} {stage} stage average metrics 2024",
            f"{sector} startup valuation multiples",
            f"{sector} startup growth rates benchmarks",
            f"{sector} seed stage revenue benchmarks"
        ]
        
        benchmark_data = []
        for query in benchmark_queries:
            results = self._google_search(query, num_results=3)
            benchmark_data.extend(results)
        
        # Get startup metrics from RAG
        metrics_context = self.rag.query(
            "What are all the metrics: revenue, MRR, growth rate, team size, customers?",
            startup_id,
            n_results=5
        )
        
        prompt = f"""
You are a venture capital benchmarking analyst.

STARTUP INFORMATION:
Company: {extracted_data.get('company_info', {}).get('name', 'Unknown')}
Sector: {sector}
Stage: {stage}

STARTUP METRICS:
{json.dumps(extracted_data.get('metrics', {}), indent=2)}

Team Size: {extracted_data.get('team', {}).get('total_employees', 'Unknown')}
Customers: {extracted_data.get('metrics', {}).get('customers', 'Unknown')}

METRICS CONTEXT FROM DOCUMENTS:
{metrics_context}

INDUSTRY BENCHMARK DATA (from web search):
{json.dumps(benchmark_data, indent=2)}

Compare this startup against sector benchmarks and return ONLY valid JSON:

{{
  "sector_benchmarks": {{
    "sector": "{sector}",
    "stage": "{stage}",
    "avg_revenue_seed": "typical seed stage revenue or Unknown",
    "avg_growth_rate": "typical monthly growth % or Unknown",
    "avg_team_size": "typical team size or Unknown",
    "avg_valuation_multiple": "typical revenue multiple or Unknown"
  }},
  "comparisons": {{
    "revenue": {{
      "startup_value": "their revenue or Unknown",
      "sector_average": "sector avg or Unknown",
      "percentile": number_0_to_100_or_null,
      "status": "Above Average|Average|Below Average|Unknown",
      "notes": "Brief explanation"
    }},
    "growth_rate": {{
      "startup_value": "their growth rate or Unknown",
      "sector_average": "sector avg or Unknown",
      "percentile": number_0_to_100_or_null,
      "status": "Above Average|Average|Below Average|Unknown",
      "notes": "Brief explanation"
    }},
    "team_size": {{
      "startup_value": "their team size or Unknown",
      "sector_average": "sector avg or Unknown",
      "status": "Appropriate|Too Large|Too Small|Unknown",
      "notes": "Brief explanation"
    }},
    "customer_count": {{
      "startup_value": "their customers or Unknown",
      "sector_average": "sector avg or Unknown",
      "percentile": number_0_to_100_or_null,
      "status": "Above Average|Average|Below Average|Unknown",
      "notes": "Brief explanation"
    }},
    "revenue_per_employee": {{
      "startup_value": "calculated value or Unknown",
      "sector_average": "sector avg or Unknown",
      "status": "Efficient|Average|Inefficient|Unknown",
      "notes": "Brief explanation"
    }}
  }},
  "competitive_position": {{
    "overall_ranking": "Top 25%|Top 50%|Bottom 50%|Bottom 25%|Unknown",
    "key_advantages": ["Advantage 1", "Advantage 2"],
    "key_gaps": ["Gap 1", "Gap 2"],
    "catch_up_difficulty": "Easy|Moderate|Difficult|Very Difficult"
  }},
  "benchmark_score": number_from_0_to_100,
  "summary": "2-3 sentence summary of how they compare"
}}

Guidelines:
- If data is missing, use "Unknown" and null
- Be realistic with percentiles based on actual data
- Consider stage appropriateness (seed vs Series A expectations differ)
- Focus on metrics relevant to their sector
- Return ONLY JSON
"""
        
        try:
            response = self.model.invoke(prompt)
            response_text = response.text.strip()
            
            # Clean JSON
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            data = json.loads(response_text)
            
            print(f"✅ Benchmarking complete! Score: {data.get('benchmark_score', 'N/A')}/100")
            return data
            
        except Exception as e:
            print(f"❌ Error in benchmarking: {e}")
            return self._get_default_structure(sector, stage)
    
    def _google_search(self, query, num_results=3):
        """Search Google for benchmark data"""
        if not GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_API_KEY == "YOUR_SEARCH_API_KEY_HERE":
            print("⚠️ Google Search API not configured, using placeholder benchmarks")
            return self._get_placeholder_benchmarks()
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': GOOGLE_SEARCH_API_KEY,
                'cx': SEARCH_ENGINE_ID,
                'q': query,
                'num': num_results
            }
            
            response = requests.get(url, params=params, timeout=10)
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
            return self._get_placeholder_benchmarks()
    
    def _get_placeholder_benchmarks(self):
        """Return placeholder benchmarks when search unavailable"""
        return [
            {
                'title': 'General Startup Metrics',
                'snippet': 'Seed stage startups typically have 5-15 employees, $50K-500K ARR, 10-20% monthly growth',
                'link': 'placeholder'
            }
        ]
    
    def _get_default_structure(self, sector, stage):
        """Default structure when benchmarking fails"""
        return {
            "sector_benchmarks": {
                "sector": sector,
                "stage": stage,
                "avg_revenue_seed": "Unknown",
                "avg_growth_rate": "Unknown",
                "avg_team_size": "Unknown",
                "avg_valuation_multiple": "Unknown"
            },
            "comparisons": {
                "revenue": {
                    "startup_value": "Unknown",
                    "sector_average": "Unknown",
                    "percentile": None,
                    "status": "Unknown",
                    "notes": "Insufficient benchmark data"
                },
                "growth_rate": {
                    "startup_value": "Unknown",
                    "sector_average": "Unknown",
                    "percentile": None,
                    "status": "Unknown",
                    "notes": "Insufficient benchmark data"
                },
                "team_size": {
                    "startup_value": "Unknown",
                    "sector_average": "Unknown",
                    "status": "Unknown",
                    "notes": "Insufficient benchmark data"
                },
                "customer_count": {
                    "startup_value": "Unknown",
                    "sector_average": "Unknown",
                    "percentile": None,
                    "status": "Unknown",
                    "notes": "Insufficient benchmark data"
                },
                "revenue_per_employee": {
                    "startup_value": "Unknown",
                    "sector_average": "Unknown",
                    "status": "Unknown",
                    "notes": "Cannot calculate"
                }
            },
            "competitive_position": {
                "overall_ranking": "Unknown",
                "key_advantages": [],
                "key_gaps": [],
                "catch_up_difficulty": "Unknown"
            },
            "benchmark_score": 50,
            "summary": "Unable to benchmark due to insufficient data"

        }

