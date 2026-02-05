# services/gmail_sender.py - Gmail API Version (No SMTP ports needed)

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailSender:
    """Send emails using Gmail API (works when SMTP ports are blocked)"""
    
    def __init__(self):
        """Initialize Gmail API with credentials from environment"""
        
        client_id = os.getenv('GMAIL_CLIENT_ID')
        client_secret = os.getenv('GMAIL_CLIENT_SECRET')
        refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
        
        if not all([client_id, client_secret, refresh_token]):
            raise ValueError(
                "❌ Gmail API credentials not found!\n\n"
                "Required environment variables:\n"
                "  - GMAIL_CLIENT_ID\n"
                "  - GMAIL_CLIENT_SECRET\n"
                "  - GMAIL_REFRESH_TOKEN\n\n"
                "To get these:\n"
                "1. Download get_refresh_token.py\n"
                "2. Place credentials.json in same folder\n"
                "3. Run: python get_refresh_token.py\n"
                "4. Copy the 3 variables to Render environment"
            )
        
        # Create credentials
        self.creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
        
        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=self.creds)
        print("✅ Gmail API authenticated successfully")
    
    def send_report(self, recipient_email, subject, company_name, decision, pdf_path):
        """
        Send investment report via Gmail API
        
        Args:
            recipient_email: Email address of recipient
            subject: Email subject line
            company_name: Name of the startup
            decision: Investment decision (INVEST/MAYBE/PASS)
            pdf_path: Path to the PDF report file
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        
        try:
            # Validate PDF exists
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF not found at {pdf_path}")
            
            # Create message
            message = MIMEMultipart()
            message['to'] = recipient_email
            message['subject'] = subject
            
            # Determine colors based on decision
            if decision == "INVEST":
                decision_color = "#34a853"
                decision_emoji = "✅"
            elif decision == "MAYBE":
                decision_color = "#fbbc04"
                decision_emoji = "⚠️"
            else:
                decision_color = "#ea4335"
                decision_emoji = "❌"
            
            # HTML email body
            html_body = f"""
            <html>
              <head>
                <style>
                  body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }}
                  .header {{ background: linear-gradient(90deg, #4285f4, #34a853, #fbbc04, #ea4335); height: 8px; }}
                  .container {{ padding: 30px; max-width: 600px; margin: 0 auto; }}
                  .logo {{ text-align: center; margin-bottom: 30px; }}
                  .decision-box {{ 
                    background: {decision_color}15; 
                    border-left: 5px solid {decision_color}; 
                    padding: 20px; 
                    margin: 25px 0;
                    border-radius: 5px;
                  }}
                  .decision-text {{ 
                    color: {decision_color}; 
                    font-size: 24px; 
                    font-weight: bold; 
                    margin: 0;
                  }}
                  .section {{ margin: 20px 0; }}
                  .section-title {{ 
                    color: #4285f4; 
                    font-size: 16px; 
                    font-weight: bold; 
                    margin-bottom: 10px;
                  }}
                  ul {{ padding-left: 20px; }}
                  li {{ margin: 8px 0; color: #333; }}
                  .footer {{ 
                    background: #f8f9fa; 
                    padding: 20px; 
                    margin-top: 30px; 
                    border-radius: 5px;
                    font-size: 12px; 
                    color: #5f6368;
                  }}
                </style>
              </head>
              <body>
                <div class="header"></div>
                
                <div class="container">
                  <div class="logo">
                    <h1 style="color: #4285f4; margin: 0;">🚀 AI Startup Analyzer</h1>
                    <p style="color: #5f6368; margin: 5px 0;">Investment Analysis Report</p>
                  </div>
                  
                  <p style="font-size: 16px;">Dear Investor,</p>
                  
                  <p style="line-height: 1.6;">
                    Our AI-powered multi-agent analysis system has completed a comprehensive evaluation of 
                    <strong>{company_name}</strong>. Please find the detailed investment report attached to this email.
                  </p>
                  
                  <div class="decision-box">
                    <p class="decision-text">{decision_emoji} Investment Decision: {decision}</p>
                  </div>
                  
                  <div class="section">
                    <div class="section-title">📊 Report Highlights:</div>
                    <ul>
                      <li><strong>Executive Summary</strong> - Investment decision and key metrics</li>
                      <li><strong>Company Overview</strong> - Business model and team analysis</li>
                      <li><strong>Growth Analysis</strong> - Multi-dimensional scoring with radar charts</li>
                      <li><strong>Risk Assessment</strong> - Comprehensive red flag analysis</li>
                      <li><strong>Market Validation</strong> - Third-party research and benchmarking</li>
                      <li><strong>Actionable Insights</strong> - Follow-up questions and next steps</li>
                    </ul>
                  </div>
                  
                  <div class="section">
                    <div class="section-title">🤖 Analysis Methodology:</div>
                    <p style="line-height: 1.6; color: #333;">
                      This report was generated by our 6-agent AI system, analyzing pitch decks, financial data, 
                      call transcripts, and market research. Each agent specializes in a specific dimension:
                    </p>
                    <ul>
                      <li>Agent 1: Data Extraction & Structuring</li>
                      <li>Agent 2: Sector Benchmarking</li>
                      <li>Agent 3: Risk Detection & Red Flags</li>
                      <li>Agent 4: Market Research & Validation</li>
                      <li>Agent 5: Growth Potential Assessment</li>
                      <li>Agent 6: Investment Recommendation</li>
                    </ul>
                  </div>
                  
                  <p style="line-height: 1.6; margin-top: 30px;">
                    The attached PDF contains detailed analysis, professional charts, and evidence-based insights 
                    to support your investment decision-making process.
                  </p>
                  
                  <div style="text-align: center; margin: 30px 0;">
                    <p style="font-size: 14px; color: #5f6368;">
                      <em>Please review the attached report for complete details</em>
                    </p>
                  </div>
                  
                  <div class="footer">
                    <p style="margin: 5px 0;"><strong>AI Startup Analyzer</strong></p>
                    <p style="margin: 5px 0;">Powered by Google Gemini 2.0 Flash, LangChain, ChromaDB</p>
                    <p style="margin: 15px 0 5px 0; font-size: 11px;">
                      <em>This automated analysis should be used as part of a comprehensive due diligence process. 
                      The AI-generated insights are based on available data and should be validated through 
                      direct founder interactions and additional research.</em>
                    </p>
                  </div>
                </div>
                
                <div class="header"></div>
              </body>
            </html>
            """
            
            message.attach(MIMEText(html_body, 'html'))
            
            # Attach PDF
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
            
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(pdf_data)
            encoders.encode_base64(part)
            
            filename = os.path.basename(pdf_path)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            message.attach(part)
            
            # Encode and send
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = {'raw': raw}
            
            print(f"📧 Sending via Gmail API...")
            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            print(f"✅ Email sent successfully!")
            print(f"   To: {recipient_email}")
            print(f"   Subject: {subject}")
            print(f"   Message ID: {result['id']}")
            print(f"   PDF attached: {filename}")
            
            return True
            
        except FileNotFoundError as e:
            print(f"❌ File error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_bulk_reports(self, recipient_list, subject, company_name, decision, pdf_path):
        """Send report to multiple recipients"""
        
        results = {'success': 0, 'failed': 0, 'failed_emails': []}
        
        print(f"\nSending to {len(recipient_list)} recipients...")
        
        for i, email in enumerate(recipient_list, 1):
            print(f"\n[{i}/{len(recipient_list)}] {email}")
            if self.send_report(email, subject, company_name, decision, pdf_path):
                results['success'] += 1
            else:
                results['failed'] += 1
                results['failed_emails'].append(email)
        
        print(f"\n{'='*50}")
        print(f"✅ Sent: {results['success']} | ❌ Failed: {results['failed']}")
        print(f"{'='*50}")
        
        return results
    
    def send_simple_email(self, to_email, subject, body, is_html=False):
        """Send simple email without attachment"""
        
        try:
            msg = MIMEMultipart()
            msg['to'] = to_email
            msg['subject'] = subject
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            print(f"✅ Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False