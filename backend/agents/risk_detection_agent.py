import google.generativeai as genai
import os
import json
import re

from config import settings
GEMINI_API_KEY = settings.GEMINI_API_KEY
from langchain_groq import ChatGroq
groq_api_key= settings.GROQ_API_KEY
class RiskDetectionAgent:
    """Agent to detect red flags and risks"""
    
    def __init__(self, rag_system):
        self.rag = rag_system
        self.model = ChatGroq(groq_api_key=groq_api_key,model="openai/gpt-oss-120b",temperature=0.7)
    
    def detect_risks(self, startup_id, extracted_data):
        """Detect all risk flags"""
        
        print("🚨 Agent 3: Detecting risks and red flags...")
        
        # Query for metrics inconsistencies
        metrics_context = self.rag.query(
            "Find all mentions of revenue, MRR, ARR, growth rate, customer count across all documents",
            startup_id,
            n_results=10
        )
        
        # Query for market size claims
        market_context = self.rag.query(
            "What market size, TAM, SAM claims are made? What is the addressable market?",
            startup_id,
            n_results=5
        )
        
        # Query for financial health
        financial_context = self.rag.query(
            "What is the burn rate, runway, cash position, funding needs?",
            startup_id,
            n_results=5
        )
        
        # Query for team concerns
        team_context = self.rag.query(
            "Information about founders' experience, team composition, key roles filled",
            startup_id,
            n_results=5
        )
        
        # Query for customer feedback
        customer_context = self.rag.query(
            "Customer retention, churn rate, customer satisfaction, feedback",
            startup_id,
            n_results=5
        )
        
        prompt = f"""
You are a risk assessment specialist for venture capital.

Analyze these documents for RED FLAGS and return ONLY valid JSON.

EXTRACTED STRUCTURED DATA:
{json.dumps(extracted_data, indent=2)}

METRICS ACROSS DOCUMENTS:
{metrics_context}

MARKET SIZE CLAIMS:
{market_context}

FINANCIAL HEALTH:
{financial_context}

TEAM INFORMATION:
{team_context}

CUSTOMER INFORMATION:
{customer_context}

Detect these specific risks:

1. INCONSISTENT METRICS - Do numbers contradict across documents?
2. INFLATED MARKET SIZE - Is TAM unrealistic or too broad?
3. FINANCIAL DISTRESS - Burn rate too high? Running out of money soon?
4. TEAM RISKS - Missing critical roles? Lack of experience?
5. CUSTOMER/MARKET RISKS - High churn rate? Unclear product-market fit?
6. UNREALISTIC PROJECTIONS - Growth projections too aggressive?
7. EXECUTION RISKS - Product not launched yet but claiming traction?

CRITICAL INSTRUCTIONS:
- Return ONLY valid JSON, no other text
- Use double quotes for all strings
- Escape any quotes inside strings with backslash
- No trailing commas
- No comments in JSON

Return this EXACT JSON structure:
{{
  "red_flags": [
    {{
      "type": "inconsistent_metrics",
      "severity": "MEDIUM",
      "title": "Example Risk",
      "description": "Brief description without quotes or special characters",
      "evidence": ["Evidence point 1", "Evidence point 2"],
      "impact": "Why this matters"
    }}
  ],
  "risk_score": 50,
  "overall_assessment": "Medium Risk"
}}

Rules:
- Only flag risks with concrete evidence
- Be specific but keep descriptions simple
- Avoid quotes inside string values
- If NO red flags found, return empty array []
- Severity options: LOW, MEDIUM, HIGH, CRITICAL
- Return ONLY the JSON object, nothing else
"""
        
        try:
            response = self.model.invoke(prompt)
            response_text = response.text.strip()
            
            # More aggressive JSON cleaning
            response_text = self._clean_json_response(response_text)
            
            # Try to parse
            data = json.loads(response_text)
            
            # Validate structure
            if not isinstance(data.get('red_flags'), list):
                data['red_flags'] = []
            if 'risk_score' not in data:
                data['risk_score'] = 50
            if 'overall_assessment' not in data:
                data['overall_assessment'] = "Medium Risk"
            
            print(f"✅ Risk detection complete! Found {len(data.get('red_flags', []))} red flags")
            return data
            
        except json.JSONDecodeError as je:
            print(f"⚠️ JSON parsing error: {je}")
            print(f"Response text: {response_text[:500]}...")
            
            # Try to extract partial data or return safe default
            return self._extract_partial_or_default(response_text)
            
        except Exception as e:
            print(f"❌ Error in risk detection: {e}")
            return self._get_default_structure()
    
    def _clean_json_response(self, text):
        """Aggressively clean JSON response"""
        # Remove markdown code blocks
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'^```\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        
        # Remove any leading/trailing whitespace
        text = text.strip()
        
        # Fix common JSON issues
        # Replace single quotes with double quotes (but be careful)
        # Only do this if it looks like the issue
        
        # Remove any text before first {
        first_brace = text.find('{')
        if first_brace > 0:
            text = text[first_brace:]
        
        # Remove any text after last }
        last_brace = text.rfind('}')
        if last_brace > 0 and last_brace < len(text) - 1:
            text = text[:last_brace + 1]
        
        return text
    
    def _extract_partial_or_default(self, text):
        """Try to extract useful information even if JSON is malformed"""
        # Look for risk indicators in the text
        red_flags = []
        
        risk_keywords = {
            'CRITICAL': ['critical', 'severe', 'major concern', 'deal breaker'],
            'HIGH': ['high risk', 'significant', 'serious'],
            'MEDIUM': ['moderate', 'concerning', 'noteworthy'],
            'LOW': ['minor', 'small', 'slight']
        }
        
        # Try to extract some basic risk info
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            for severity, keywords in risk_keywords.items():
                if any(kw in line_lower for kw in keywords):
                    red_flags.append({
                        "type": "detected_issue",
                        "severity": severity,
                        "title": "Detected Risk",
                        "description": line[:200],
                        "evidence": ["Extracted from analysis"],
                        "impact": "Requires manual review"
                    })
                    break
        
        # Calculate risk score based on findings
        risk_score = 50
        if len(red_flags) > 0:
            risk_score = min(90, 40 + len(red_flags) * 10)
        
        return {
            "red_flags": red_flags[:5],  # Limit to 5
            "risk_score": risk_score,
            "overall_assessment": "Manual Review Required",
            "parsing_note": "JSON parsing failed, extracted partial information"
        }
    
    def _get_default_structure(self):
        """Default structure when detection fails completely"""
        return {
            "red_flags": [],
            "risk_score": 50,
            "overall_assessment": "Unable to assess - analysis error",
            "error_note": "Risk detection encountered an error"

        }

