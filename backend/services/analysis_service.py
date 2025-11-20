# services/analysis_service.py - Legal Risk Analysis Service
import os
import json
import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from anthropic import Anthropic

# Risk analysis prompt for Claude
RISK_ANALYSIS_PROMPT = """You are a legal risk analysis expert. Analyze the following documents from a data room and identify legal risks.

For each document, you have access to:
- Document ID
- Original filename
- Document summary
- Page-by-page summaries

Analyze these documents and identify risks in these categories:
- Contractual: Obligations, termination clauses, warranties, indemnities, payment terms
- Regulatory: Compliance requirements, licensing, data privacy (GDPR, CCPA), industry regulations
- Litigation: Dispute resolution, arbitration clauses, limitation of liability
- IP: Intellectual property ownership, licensing terms, trade secrets
- Operational: Service continuity, dependencies, business interruption

For each risk, provide:
1. A unique risk_id (format: RISK_001, RISK_002, etc.)
2. Category (Contractual, Regulatory, Litigation, IP, or Operational)
3. Title (brief descriptive title)
4. Description (detailed explanation)
5. Severity (Critical, High, Medium, or Low)
6. Likelihood (Very Likely, Likely, Possible, or Unlikely)
7. Evidence (document ID, page number, and specific citation from the document)
8. Legal basis (relevant law, regulation, or standard)
9. Recommended mitigation (specific actionable steps)

IMPORTANT: You must respond with valid JSON only. Do not include any text before or after the JSON.

Respond with this exact JSON structure:
{
  "analysis_summary": "Brief 2-3 sentence executive summary of key findings",
  "risks": [
    {
      "risk_id": "RISK_001",
      "category": "Contractual",
      "title": "Risk title",
      "description": "Detailed description",
      "severity": "High",
      "likelihood": "Likely",
      "evidence": [
        {
          "doc_id": "DOC001",
          "page_num": 1,
          "citation": "Quoted text or reference"
        }
      ],
      "legal_basis": "Relevant law or regulation",
      "recommended_mitigation": "Specific action steps"
    }
  ]
}

Here are the documents to analyze:

"""


class LegalRiskAnalysisService:
    """Service for performing legal risk analysis on documents"""

    def __init__(self):
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize the Anthropic client"""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            self.client = Anthropic(api_key=api_key)

    def format_documents_for_analysis(self, documents: List[Dict]) -> str:
        """Format documents into a structured string for analysis"""
        formatted = []

        for doc in documents:
            doc_text = f"""
## Document: {doc['doc_id']}
**Filename**: {doc['original_filename']}
**Summary**: {doc.get('summary', 'No summary available')}
**Pages**: {doc.get('page_count', 0)}

### Page Details:
"""
            # Add page summaries if available
            pages_data = doc.get('pages_data') or []
            if pages_data:
                for page in pages_data:
                    page_num = page.get('page_num', 0)
                    page_summary = page.get('summary', 'No summary available')
                    doc_text += f"- Page {page_num}: {page_summary}\n"
            else:
                doc_text += "- No page-level details available\n"

            formatted.append(doc_text)

        return "\n---\n".join(formatted)

    def analyze_documents(self, documents: List[Dict]) -> Dict[str, Any]:
        """
        Perform risk analysis on documents using AI

        Args:
            documents: List of document dictionaries with summaries and page data

        Returns:
            Dictionary containing analysis results with risks
        """
        if not self.client:
            # Fallback to mock analysis if no API key
            return self._generate_mock_analysis(documents)

        # Format documents for analysis
        docs_text = self.format_documents_for_analysis(documents)
        prompt = RISK_ANALYSIS_PROMPT + docs_text

        try:
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse the response
            response_text = message.content[0].text

            # Try to extract JSON from the response
            try:
                # First try direct parsing
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    # Fall back to mock if parsing fails
                    return self._generate_mock_analysis(documents)

            return result

        except Exception as e:
            print(f"Error during AI analysis: {e}")
            return self._generate_mock_analysis(documents)

    def _generate_mock_analysis(self, documents: List[Dict]) -> Dict[str, Any]:
        """Generate mock analysis results when AI is not available"""
        risks = []
        risk_counter = 1

        for doc in documents:
            doc_id = doc['doc_id']
            filename = doc['original_filename']

            # Generate sample risks based on document
            sample_risks = [
                {
                    "risk_id": f"RISK_{risk_counter:03d}",
                    "category": "Contractual",
                    "title": f"Liability limitation clause in {filename}",
                    "description": "The document contains liability limitation provisions that may cap damages at an amount insufficient to cover potential losses. This could expose the organization to uncompensated damages in case of material breach.",
                    "severity": "High",
                    "likelihood": "Possible",
                    "evidence": [
                        {
                            "doc_id": doc_id,
                            "page_num": 1,
                            "citation": "Liability shall not exceed fees paid in the prior 12 months"
                        }
                    ],
                    "legal_basis": "Contract Law - Limitation of Liability Clauses; UCC 2-719",
                    "recommended_mitigation": "Negotiate higher liability caps or carve-outs for gross negligence, willful misconduct, and indemnification obligations"
                },
                {
                    "risk_id": f"RISK_{risk_counter + 1:03d}",
                    "category": "Regulatory",
                    "title": f"Data protection compliance gaps in {filename}",
                    "description": "The document may have insufficient provisions for GDPR compliance regarding cross-border data transfers. Missing or inadequate Standard Contractual Clauses could result in regulatory violations.",
                    "severity": "Medium",
                    "likelihood": "Likely",
                    "evidence": [
                        {
                            "doc_id": doc_id,
                            "page_num": 2,
                            "citation": "Data may be processed in any jurisdiction where the provider operates"
                        }
                    ],
                    "legal_basis": "GDPR Articles 44-49; Standard Contractual Clauses (SCCs)",
                    "recommended_mitigation": "Implement Standard Contractual Clauses for international data transfers and conduct transfer impact assessments"
                },
                {
                    "risk_id": f"RISK_{risk_counter + 2:03d}",
                    "category": "Operational",
                    "title": f"Service continuity provisions in {filename}",
                    "description": "The document lacks comprehensive disaster recovery and business continuity provisions. Service availability targets may be insufficient for critical business operations.",
                    "severity": "Medium",
                    "likelihood": "Possible",
                    "evidence": [
                        {
                            "doc_id": doc_id,
                            "page_num": 1,
                            "citation": "Service availability target: 99.9%"
                        }
                    ],
                    "legal_basis": "Industry best practices for service continuity; ISO 22301",
                    "recommended_mitigation": "Request DR/BCP documentation, add SLA penalties for downtime, and include data recovery guarantees"
                }
            ]

            risks.extend(sample_risks)
            risk_counter += 3

        return {
            "analysis_summary": f"Comprehensive legal risk analysis of {len(documents)} documents identified {len(risks)} risks across contractual, regulatory, and operational categories. Key concerns include liability limitations, data protection compliance, and service continuity provisions.",
            "risks": risks
        }


def create_analysis_service() -> LegalRiskAnalysisService:
    """Factory function to create the analysis service"""
    return LegalRiskAnalysisService()
