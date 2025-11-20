# run_analysis.py
import os
import json
from dotenv import load_dotenv
from data_room_tools import DataRoom
from main_agent import create_legal_risk_analysis_agent

# Load environment configuration
load_dotenv()

def create_sample_data_room():
    """
    Creates a sample data room for demonstration purposes.

    In production, you would load this from your document management system,
    database, or cloud storage. This example shows the expected data structure.
    """

    # Example data room with sample documents
    documents = [
        {
            "doc_id": "DOC001",
            "summdesc": "Master Services Agreement with Acme Corp dated January 2023. This is the primary contract governing the relationship, including service specifications, payment terms, and termination provisions.",
            "pages": [
                {
                    "page_num": 1,
                    "summdesc": "Cover page and parties identification",
                    "page_image": "base64_encoded_image_data_here_or_file_path"
                },
                {
                    "page_num": 2,
                    "summdesc": "Service scope and specifications. Details the cloud hosting services to be provided including uptime requirements of 99.9%",
                    "page_image": "base64_encoded_image_data_here_or_file_path"
                },
                {
                    "page_num": 3,
                    "summdesc": "Payment terms including monthly fees of $50,000 and late payment penalties of 1.5% per month",
                    "page_image": "base64_encoded_image_data_here_or_file_path"
                },
                {
                    "page_num": 4,
                    "summdesc": "Limitation of liability clause capping vendor liability at fees paid in prior 12 months",
                    "page_image": "base64_encoded_image_data_here_or_file_path"
                },
                {
                    "page_num": 5,
                    "summdesc": "Termination provisions including 90-day notice requirement and termination for convenience by either party",
                    "page_image": "base64_encoded_image_data_here_or_file_path"
                }
            ]
        },
        {
            "doc_id": "DOC002",
            "summdesc": "Data Processing Agreement related to DOC001, addressing GDPR compliance requirements for personal data handling",
            "pages": [
                {
                    "page_num": 1,
                    "summdesc": "DPA terms including roles as data processor and data controller responsibilities",
                    "page_image": "base64_encoded_image_data_here_or_file_path"
                },
                {
                    "page_num": 2,
                    "summdesc": "Security measures and data breach notification requirements within 24 hours",
                    "page_image": "base64_encoded_image_data_here_or_file_path"
                },
                {
                    "page_num": 3,
                    "summdesc": "Sub-processor provisions and requirement for customer approval before engaging new sub-processors",
                    "page_image": "base64_encoded_image_data_here_or_file_path"
                }
            ]
        },
        {
            "doc_id": "DOC003",
            "summdesc": "Regulatory compliance certification letter from vendor dated March 2023 claiming SOC 2 Type II and ISO 27001 certification",
            "pages": [
                {
                    "page_num": 1,
                    "summdesc": "Compliance certification claims and validity dates showing ISO cert expires December 2023",
                    "page_image": "base64_encoded_image_data_here_or_file_path"
                }
            ]
        }
    ]

    return DataRoom(documents)

def format_data_room_index(data_room: DataRoom) -> str:
    """
    Formats the data room contents as a concise index for the main agent.

    This provides just enough information for strategic planning without
    overwhelming the agent's initial context.
    """
    index_parts = ["# Data Room Index\n"]

    for doc_id, doc in data_room.documents.items():
        index_parts.append(f"## {doc_id}")
        index_parts.append(f"**Summary**: {doc['summdesc']}")
        index_parts.append(f"**Pages**: {len(doc['pages'])}")
        index_parts.append("")  # Blank line

    return "\n".join(index_parts)

def run_legal_risk_analysis():
    """
    Main function to execute a legal risk analysis workflow.

    This demonstrates the complete system in action: creating the agent,
    providing it with the data room context, and executing the analysis.
    """

    print("=" * 80)
    print("LEGAL RISK ANALYSIS SYSTEM")
    print("=" * 80)
    print()

    # Step 1: Initialize the data room
    print("[1/4] Loading data room...")
    data_room = create_sample_data_room()
    data_room_index = format_data_room_index(data_room)
    print(f"Loaded {len(data_room.documents)} documents")
    print()

    # Step 2: Create the agent
    print("[2/4] Initializing Legal Risk Analysis Agent...")
    agent = create_legal_risk_analysis_agent(
        data_room=data_room,
        tavily_api_key=os.environ["TAVILY_API_KEY"]
    )
    print("Agent initialized with Analysis, Report, and Dashboard subagents")
    print()

    # Step 3: Prepare the analysis request
    print("[3/4] Preparing analysis request...")
    user_request = f"""Please conduct a comprehensive legal risk analysis of the following data room.

{data_room_index}

Analyze all documents to identify contractual risks, regulatory compliance issues, litigation exposure, intellectual property concerns, and operational risks.

For each risk identified, assess its severity and likelihood, cite specific evidence from the documents, and provide recommended mitigations.

Once analysis is complete, create both a professional Word document report and an interactive HTML dashboard for presenting the findings."""

    print("Request prepared")
    print()

    # Step 4: Execute the analysis
    print("[4/4] Executing analysis (this may take several minutes)...")
    print("-" * 80)
    print()

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": user_request
            }
        ]
    })

    # Display the final response
    print()
    print("-" * 80)
    print("ANALYSIS COMPLETE")
    print("-" * 80)
    print()
    print(result["messages"][-1].content)
    print()
    print("=" * 80)
    print("Check /outputs directory for:")
    print("  - Legal_Risk_Analysis_Report.docx")
    print("  - Legal_Risk_Dashboard.html")
    print("=" * 80)

if __name__ == "__main__":
    run_legal_risk_analysis()
