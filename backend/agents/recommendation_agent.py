import google.generativeai as genai
import os
import json

from config import settings
GEMINI_API_KEY = settings.GEMINI_API_KEY

from langchain_groq import ChatGroq
groq_api_key= settings.GROQ_API_KEY
class RecommendationAgent:
    """Agent to generate final investment recommendation"""
    
    def __init__(self):
         self.model =ChatGroq(groq_api_key=groq_api_key,model="openai/gpt-oss-120b",temperature=0.7)
    
    def generate_recommendation(self, extracted_data, risk_analysis, market_research, benchmark_data, growth_assessment):
        """Generate final investment recommendation"""
        
        print("💰 Agent 6: Generating investment recommendation...")
        
        # Extract key metrics for decision making
        risk_score = risk_analysis.get('risk_score', 50)
        benchmark_score = benchmark_data.get('benchmark_score', 50)
        growth_score = growth_assessment.get('overall_growth_score', 5)
        red_flags_count = len(risk_analysis.get('red_flags', []))
        critical_flags = [f for f in risk_analysis.get('red_flags', []) if f.get('severity') == 'CRITICAL']
        
        prompt = f"""
You are a senior venture capital partner making final investment decisions.

STARTUP DATA:
{json.dumps(extracted_data, indent=2)}

RISK ANALYSIS:
{json.dumps(risk_analysis, indent=2)}

MARKET RESEARCH:
{json.dumps(market_research, indent=2)}

BENCHMARK DATA:
{json.dumps(benchmark_data, indent=2)}

GROWTH ASSESSMENT:
{json.dumps(growth_assessment, indent=2)}

KEY METRICS SUMMARY:
- Risk Score: {risk_score}/100 (lower is better)
- Benchmark Score: {benchmark_score}/100 (higher is better)
- Growth Score: {growth_score}/10 (higher is better)
- Red Flags Count: {red_flags_count}
- Critical Red Flags: {len(critical_flags)}

Generate a comprehensive investment recommendation and return ONLY valid JSON:

{{
  "decision": "PASS|MAYBE|INVEST",
  "confidence": number_from_0_to_100,
  "investment_thesis": "2-3 sentence summary of why invest or pass",
  "key_strengths": [
    "Strength 1",
    "Strength 2",
    "Strength 3"
  ],
  "key_concerns": [
    "Concern 1",
    "Concern 2",
    "Concern 3"
  ],
  "suggested_valuation": "Range or null if PASS",
  "suggested_investment": "Amount or null if PASS",
  "follow_up_questions": [
    "Question 1 for founders",
    "Question 2 for founders",
    "Question 3 for founders"
  ],
  "deal_score": number_from_0_to_100,
  "next_steps": "What should happen next"
}}

Decision Guidelines:
- PASS: Any critical red flags OR risk_score > 70 OR deal_score < 40 OR growth_score < 4
- MAYBE: Some concerns but potential OR deal_score 40-65 OR growth_score 5-6
- INVEST: Strong opportunity, manageable risks, deal_score > 65 AND growth_score > 6

Deal Score Calculation (guide):
- Start with 50 base points
- Add up to +20 for strong growth score (>7)
- Add up to +15 for good benchmark score (>60)
- Add up to +15 for low risk score (<40)
- Subtract -10 for each HIGH severity red flag
- Subtract -25 for each CRITICAL red flag
- Add up to +10 for strong market validation
- Add up to +10 for exceptional team

Key Strengths should include:
- Specific metrics (e.g., "120% YoY revenue growth")
- Market advantages (e.g., "First mover in $2B market")
- Team strengths (e.g., "Founders have 15+ years industry experience")

Key Concerns should include:
- Specific risks with evidence
- Financial concerns (e.g., "Only 4 months runway remaining")
- Market/competitive concerns

Follow-up Questions should be:
- Specific and actionable
- Address key concerns or validate strengths
- Help make final investment decision

Return ONLY JSON, no markdown formatting.
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
            
            # Validate decision matches guidelines
            decision = data.get('decision', 'MAYBE')
            deal_score = data.get('deal_score', 50)
            
            # Override if critical flags exist
            if len(critical_flags) > 0 and decision == 'INVEST':
                data['decision'] = 'PASS'
                data['key_concerns'].insert(0, f"CRITICAL: {len(critical_flags)} critical red flags detected")
            
            print(f"✅ Recommendation: {data['decision']} (Confidence: {data['confidence']}%)")
            print(f"   Deal Score: {deal_score}/100")
            
            return data
            
        except Exception as e:
            print(f"❌ Error generating recommendation: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "decision": "MAYBE",
                "confidence": 50,
                "investment_thesis": "Unable to generate recommendation due to processing error. Manual review required.",
                "key_strengths": ["Analysis data collected successfully"],
                "key_concerns": [
                    "Analysis incomplete - technical error occurred",
                    f"Error: {str(e)}"
                ],
                "suggested_valuation": None,
                "suggested_investment": None,
                "follow_up_questions": [
                    "Please rerun the analysis",
                    "Verify all document uploads were successful",
                    "Check system logs for detailed error information"
                ],
                "deal_score": 50,
                "next_steps": "Manual review required - rerun analysis or review documents manually"

            }

