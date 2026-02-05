from api_backend.backend.agents.data_extraction_agent import DataExtractionAgent
from api_backend.backend.agents.benchmarking_agent import BenchmarkingAgent
from api_backend.backend.agents.risk_detection_agent import RiskDetectionAgent
from api_backend.backend.agents.market_research_agent import MarketResearchAgent
from api_backend.backend.agents.growth_agent import GrowthAgent
from api_backend.backend.agents.recommendation_agent import RecommendationAgent
import os

class AgentOrchestrator:
    """Coordinates all agents in the analysis pipeline"""
    
    def __init__(self, rag_system):
        self.rag = rag_system
        
        # Initialize all 6 agents with rag_system where needed
        self.data_extraction_agent = DataExtractionAgent(rag_system)
        self.benchmarking_agent = BenchmarkingAgent(rag_system)
        self.risk_detection_agent = RiskDetectionAgent(rag_system)
        self.market_research_agent = MarketResearchAgent(rag_system)
        self.growth_agent = GrowthAgent(rag_system)
        self.recommendation_agent = RecommendationAgent()  # No rag_system needed
    
    def analyze_startup(self, startup_id):
        """Run complete 6-agent analysis pipeline"""
        
        print("\n" + "="*60)
        print("🚀 STARTING MULTI-AGENT ANALYSIS (6 AGENTS)")
        print("="*60 + "\n")
        
        results = {
            "startup_id": startup_id,
            "status": "processing"
        }
        
        try:
            # Agent 1: Extract Data
            extracted_data = self.data_extraction_agent.extract(startup_id)
            results["extracted_data"] = extracted_data
            
            # Agent 2: Benchmarking
            benchmark_data = self.benchmarking_agent.benchmark(startup_id, extracted_data)
            results["benchmark_data"] = benchmark_data
            
            # Agent 3: Detect Risks
            risk_analysis = self.risk_detection_agent.detect_risks(startup_id, extracted_data)
            results["risk_analysis"] = risk_analysis
            
            # Agent 4: Market Research
            market_research = self.market_research_agent.research(startup_id, extracted_data)
            results["market_research"] = market_research
            
            # Agent 5: Growth Assessment
            growth_assessment = self.growth_agent.assess_growth(
                startup_id,
                extracted_data,
                benchmark_data
            )
            results["growth_assessment"] = growth_assessment
            
            # Agent 6: Generate Recommendation
            recommendation = self.recommendation_agent.generate_recommendation(
                extracted_data,
                risk_analysis,
                market_research,
                benchmark_data,
                growth_assessment
            )
            results["recommendation"] = recommendation
            
            results["status"] = "complete"
            
            print("\n" + "="*60)
            print("✅ ALL 6 AGENTS COMPLETE!")
            print("="*60 + "\n")
            
            return results
            
        except Exception as e:
            print(f"\n❌ Analysis failed: {e}\n")
            import traceback
            traceback.print_exc()
            results["status"] = "failed"
            results["error"] = str(e)
            return results
