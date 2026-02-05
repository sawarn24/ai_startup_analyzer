# services/professional_report_generator.py

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import os

class ProfessionalReportGenerator:
    """Generate comprehensive PDF reports with charts"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()
    
    def _add_custom_styles(self):
        """Add professional custom styles"""
        
        self.styles.add(ParagraphStyle(
            name='CoverTitle', parent=self.styles['Heading1'], fontSize=32,
            textColor=colors.HexColor('#1a1a1a'), spaceAfter=20,
            alignment=TA_CENTER, fontName='Helvetica-Bold', leading=38
        ))
        
        self.styles.add(ParagraphStyle(
            name='CoverSubtitle', parent=self.styles['Normal'], fontSize=18,
            textColor=colors.HexColor('#4285f4'), spaceAfter=30,
            alignment=TA_CENTER, fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader', parent=self.styles['Heading1'], fontSize=18,
            textColor=colors.HexColor('#4285f4'), spaceAfter=15, spaceBefore=20,
            fontName='Helvetica-Bold', borderWidth=2,
            borderColor=colors.HexColor('#4285f4'), borderPadding=8,
            backColor=colors.HexColor('#e8f0fe')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader', parent=self.styles['Heading2'], fontSize=14,
            textColor=colors.HexColor('#34a853'), spaceAfter=10, spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyJustified', parent=self.styles['Normal'], fontSize=11,
            alignment=TA_JUSTIFY, spaceAfter=12, leading=14
        ))
    
    def create_radar_chart(self, categories, values, title="Growth Dimensions"):
        """Create radar chart for growth dimensions"""
        
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='polar')
        
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        values_plot = values + [values[0]]
        angles += angles[:1]
        
        # Startup score
        ax.plot(angles, values_plot, 'o-', linewidth=2, color='#4285f4', label='Startup Score')
        ax.fill(angles, values_plot, alpha=0.25, color='#4285f4')
        
        # Target line
        target_values = [7] * (N + 1)
        ax.plot(angles, target_values, '--', linewidth=1.5, color='#34a853', label='Target (7/10)')
        ax.fill(angles, target_values, alpha=0.1, color='#34a853')
        
        ax.set_ylim(0, 10)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=11, weight='bold')
        
        plt.title(title, size=15, weight='bold', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True, alpha=0.3)
        
        img_buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def create_score_bars(self, categories, values, title):
        """Create bar chart for scores"""
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors_list = []
        for val in values:
            if val >= 70:
                colors_list.append('#34a853')
            elif val >= 40:
                colors_list.append('#fbbc04')
            else:
                colors_list.append('#ea4335')
        
        bars = ax.barh(categories, values, color=colors_list, alpha=0.8)
        
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(val + 2, i, f'{val}', va='center', fontweight='bold', fontsize=11)
        
        ax.set_xlabel('Score', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlim(0, 105)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        img_buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def generate_report(self, results, output_path):
        """Generate comprehensive professional report"""
        
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=60, leftMargin=60,
                              topMargin=60, bottomMargin=40)
        
        story = []
        
        # Extract data
        company_info = results['extracted_data']['company_info']
        business = results['extracted_data'].get('business', {})
        metrics = results['extracted_data'].get('metrics', {})
        team = results['extracted_data'].get('team', {})
        funding = results['extracted_data'].get('funding', {})
        traction = results['extracted_data'].get('traction', {})
        
        recommendation = results['recommendation']
        risk_analysis = results['risk_analysis']
        benchmark_data = results.get('benchmark_data', {})
        growth_assessment = results.get('growth_assessment', {})
        market_research = results.get('market_research', {})
        
        # === COVER PAGE ===
        story.append(Spacer(1, 1.5*inch))
        
        bar_data = [['', '', '', '']]
        bar_table = Table(bar_data, colWidths=[1.5*inch]*4)
        bar_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor('#4285f4')),
            ('BACKGROUND', (1,0), (1,0), colors.HexColor('#ea4335')),
            ('BACKGROUND', (2,0), (2,0), colors.HexColor('#fbbc04')),
            ('BACKGROUND', (3,0), (3,0), colors.HexColor('#34a853')),
        ]))
        story.append(bar_table)
        story.append(Spacer(1, 0.5*inch))
        
        story.append(Paragraph("AI-POWERED INVESTMENT ANALYSIS", self.styles['CoverTitle']))
        story.append(Paragraph(f"<b>{company_info['name']}</b>", self.styles['CoverSubtitle']))
        story.append(Spacer(1, 0.3*inch))
        
        cover_info = [
            ['Report Date:', datetime.now().strftime('%B %d, %Y')],
            ['Company Stage:', company_info['stage']],
            ['Sector:', company_info['sector']],
            ['Analysis Type:', '6-Agent Multi-Dimensional Assessment'],
        ]
        
        cover_table = Table(cover_info, colWidths=[2*inch, 3.5*inch])
        cover_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('TOPPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(cover_table)
        
        story.append(PageBreak())
        
        # === EXECUTIVE SUMMARY ===
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        decision = recommendation['decision']
        confidence = recommendation['confidence']
        deal_score = recommendation['deal_score']
        
        if decision == "INVEST":
            decision_color = colors.HexColor('#34a853')
            decision_bg = colors.HexColor('#e6f4ea')
            emoji = "✅"
        elif decision == "MAYBE":
            decision_color = colors.HexColor('#fbbc04')
            decision_bg = colors.HexColor('#fef7e0')
            emoji = "⚠️"
        else:
            decision_color = colors.HexColor('#ea4335')
            decision_bg = colors.HexColor('#fce8e6')
            emoji = "❌"
        
        decision_text = Paragraph(
            f"<font size=24><b>{emoji} DECISION: {decision}</b></font>",
            self.styles['Normal']
        )
        
        decision_box = [[decision_text]]
        decision_table = Table(decision_box, colWidths=[6.5*inch])
        decision_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), decision_bg),
            ('BOX', (0,0), (-1,-1), 3, decision_color),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 20),
            ('BOTTOMPADDING', (0,0), (-1,-1), 20),
        ]))
        story.append(decision_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Key metrics
        summary_metrics = [
            ['METRIC', 'SCORE', 'ASSESSMENT'],
            ['Deal Score', f'{deal_score}/100', self._assess_score(deal_score)],
            ['Confidence', f'{confidence}%', self._assess_confidence(confidence)],
            ['Growth Score', f"{growth_assessment.get('overall_growth_score',5)}/10", 
             self._assess_growth(growth_assessment.get('overall_growth_score',5))],
            ['Risk Score', f"{risk_analysis.get('risk_score',50)}/100", 
             risk_analysis.get('overall_assessment','Medium')],
        ]
        
        summary_table = Table(summary_metrics, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4285f4')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(summary_table)
        
        story.append(Spacer(1, 0.3*inch))
        
        thesis_box = [[Paragraph(f"<b>Investment Thesis:</b><br/>{recommendation['investment_thesis']}", 
                                self.styles['BodyJustified'])]]
        thesis_table = Table(thesis_box, colWidths=[6.5*inch])
        thesis_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e8f0fe')),
            ('BOX', (0,0), (-1,-1), 2, colors.HexColor('#4285f4')),
            ('PADDING', (0,0), (-1,-1), 15),
        ]))
        story.append(thesis_table)
        
        story.append(PageBreak())
        
        # === COMPANY OVERVIEW ===
        story.append(Paragraph("COMPANY OVERVIEW", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        company_data = [
            ['Company', company_info['name']],
            ['Sector', company_info['sector']],
            ['Stage', company_info['stage']],
            ['Location', company_info['location']],
            ['Founded', str(company_info.get('founded_year', 'N/A'))],
        ]
        
        company_table = Table(company_data, colWidths=[2*inch, 4*inch])
        company_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#e8f0fe')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('PADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(company_table)
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("<b>Business Model:</b>", self.styles['SubsectionHeader']))
        story.append(Paragraph(f"<b>Problem:</b> {business.get('problem','Not stated')}", 
                              self.styles['BodyJustified']))
        story.append(Paragraph(f"<b>Solution:</b> {business.get('solution','Not stated')}", 
                              self.styles['BodyJustified']))
        
        story.append(PageBreak())
        
        # === GROWTH ANALYSIS WITH RADAR CHART ===
        story.append(Paragraph("GROWTH DIMENSION ANALYSIS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        growth_scores = growth_assessment.get('growth_scores', {})
        categories = ['Market\nOpportunity', 'Competitive\nMoat', 'Product\nInnovation', 
                     'Scalability', 'Team\nExecution']
        values = [
            growth_scores.get('market_opportunity', {}).get('score', 5),
            growth_scores.get('competitive_moat', {}).get('score', 5),
            growth_scores.get('product_innovation', {}).get('score', 5),
            growth_scores.get('scalability', {}).get('score', 5),
            growth_scores.get('team_execution', {}).get('score', 5)
        ]
        
        radar_img = self.create_radar_chart(categories, values, "Growth Dimension Scores")
        story.append(Image(radar_img, width=5*inch, height=5*inch))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Dimension details
        for dim, data in growth_scores.items():
            if isinstance(data, dict):
                story.append(Paragraph(
                    f"<b>{dim.replace('_',' ').title()}:</b> {data.get('score',0)}/10 - {data.get('reasoning','N/A')[:150]}...",
                    self.styles['Normal']
                ))
                story.append(Spacer(1, 0.1*inch))
        
        story.append(PageBreak())
        
        # === SCORE COMPARISON CHART ===
        story.append(Paragraph("COMPREHENSIVE SCORE ANALYSIS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        score_categories = ['Deal Score', 'Growth Score\n(x10)', 'Benchmark\nScore', 
                          'Market\nCredibility', 'Risk Score\n(inverted)']
        score_values = [
            deal_score,
            growth_assessment.get('overall_growth_score', 5) * 10,
            benchmark_data.get('benchmark_score', 50),
            market_research.get('credibility_score', 50),
            100 - risk_analysis.get('risk_score', 50)  # Inverted
        ]
        
        bars_img = self.create_score_bars(score_categories, score_values, 
                                         "Multi-Dimensional Score Comparison")
        story.append(Image(bars_img, width=6.5*inch, height=4*inch))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            "<i>Note: Higher scores indicate better performance. Risk score is inverted (higher = lower risk).</i>",
            self.styles['Normal']
        ))
        
        story.append(PageBreak())
        
        # === STRENGTHS & CONCERNS ===
        story.append(Paragraph("KEY STRENGTHS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        for i, strength in enumerate(recommendation['key_strengths'], 1):
            strength_box = [[Paragraph(f"<b>{i}.</b> {strength}", self.styles['Normal'])]]
            strength_table = Table(strength_box, colWidths=[6.5*inch])
            strength_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e6f4ea')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#34a853')),
                ('PADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(strength_table)
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("KEY CONCERNS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        for i, concern in enumerate(recommendation['key_concerns'], 1):
            concern_box = [[Paragraph(f"<b>{i}.</b> {concern}", self.styles['Normal'])]]
            concern_table = Table(concern_box, colWidths=[6.5*inch])
            concern_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef7e0')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#fbbc04')),
                ('PADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(concern_table)
            story.append(Spacer(1, 0.1*inch))
        
        story.append(PageBreak())
        
        # === RED FLAGS ===
        if risk_analysis.get('red_flags'):
            story.append(Paragraph("RISK ANALYSIS - RED FLAGS", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.2*inch))
            
            for flag in risk_analysis['red_flags']:
                severity = flag['severity']
                
                if severity == "CRITICAL":
                    flag_color = colors.HexColor('#ea4335')
                    bg_color = colors.HexColor('#fce8e6')
                elif severity == "HIGH":
                    flag_color = colors.HexColor('#fbbc04')
                    bg_color = colors.HexColor('#fef7e0')
                else:
                    flag_color = colors.HexColor('#5f6368')
                    bg_color = colors.HexColor('#f8f9fa')
                
                flag_content = Paragraph(
                    f"<b>[{severity}] {flag['title']}</b><br/>"
                    f"{flag['description']}<br/><br/>"
                    f"<b>Impact:</b> {flag['impact']}",
                    self.styles['Normal']
                )
                
                flag_box = [[flag_content]]
                flag_table = Table(flag_box, colWidths=[6.5*inch])
                flag_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), bg_color),
                    ('BOX', (0,0), (-1,-1), 2, flag_color),
                    ('PADDING', (0,0), (-1,-1), 12),
                ]))
                
                story.append(flag_table)
                story.append(Spacer(1, 0.15*inch))
            
            story.append(PageBreak())
        
        # === FOLLOW-UP QUESTIONS ===
        story.append(Paragraph("FOLLOW-UP QUESTIONS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        for i, question in enumerate(recommendation['follow_up_questions'], 1):
            q_box = [[Paragraph(f"<b>Q{i}:</b> {question}", self.styles['Normal'])]]
            q_table = Table(q_box, colWidths=[6.5*inch])
            q_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e8f0fe')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#4285f4')),
                ('PADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(q_table)
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.3*inch))
        
        # === NEXT STEPS ===
        story.append(Paragraph("RECOMMENDED NEXT STEPS", self.styles['SectionHeader']))
        next_steps_box = [[Paragraph(recommendation.get('next_steps', 'Continue due diligence'), 
                                    self.styles['BodyJustified'])]]
        next_steps_table = Table(next_steps_box, colWidths=[6.5*inch])
        next_steps_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e6f4ea')),
            ('BOX', (0,0), (-1,-1), 2, colors.HexColor('#34a853')),
            ('PADDING', (0,0), (-1,-1), 15),
        ]))
        story.append(next_steps_table)
        
        # === FOOTER ===
        story.append(Spacer(1, 0.5*inch))
        story.append(bar_table)
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(
            "<i>Generated by AI Startup Analyzer • Powered by Google Gemini 2.0, LangChain & ChromaDB</i>",
            self.styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        print(f"✅ Professional report generated: {output_path}")
        
        return output_path
    
    def _assess_score(self, score):
        if score >= 75: return "Excellent"
        elif score >= 60: return "Good"
        elif score >= 40: return "Fair"
        else: return "Weak"
    
    def _assess_confidence(self, conf):
        if conf >= 80: return "Very High"
        elif conf >= 60: return "High"
        elif conf >= 40: return "Medium"
        else: return "Low"
    
    def _assess_growth(self, score):
        if score >= 8: return "Exceptional"
        elif score >= 6: return "Strong"
        elif score >= 4: return "Moderate"
        else: return "Limited"