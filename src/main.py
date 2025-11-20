"""
Legal Risk Analysis System - Main Entry Point

This module provides the main entry point for running legal risk analysis
on a data room using the Deep Agent architecture.
"""

import os
import json
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

from .config import get_config, SystemConfig
from .models.data_room import DataRoom, Document, Page, DocumentType
from .tools.data_room_tools import create_data_room_tools
from .tools.web_tools import create_web_research_tools
from .agents.main_agent import create_main_agent
from .agents.analysis_subagent import create_analysis_task
from .agents.report_subagent import create_report_task
from .agents.dashboard_subagent import create_dashboard_task


def load_data_room(data_room_path: str) -> DataRoom:
    """
    Load a data room from a JSON file.

    Args:
        data_room_path: Path to the data room JSON file.

    Returns:
        Loaded DataRoom instance.
    """
    with open(data_room_path, 'r') as f:
        data = json.load(f)

    return DataRoom.from_dict(data)


def create_sample_data_room() -> DataRoom:
    """
    Create a sample data room for demonstration.

    Returns:
        Sample DataRoom with example documents.
    """
    data_room = DataRoom(
        name="Sample Legal Data Room",
        description="Sample data room for demonstrating legal risk analysis"
    )

    # Sample Document 1: Service Agreement
    doc1 = Document(
        doc_id="DOC-001",
        summdesc="Master Service Agreement between Company A and Company B for IT services, dated January 2024. Includes standard terms for service delivery, payment, and liability provisions.",
        document_type=DocumentType.CONTRACT,
        title="Master Service Agreement",
        source="Legal Department",
        date_added="2024-01-15",
        pages=[
            Page(
                page_num=1,
                summdesc="Cover page and definitions section. Defines key terms including 'Services', 'Deliverables', and 'Fees'."
            ),
            Page(
                page_num=2,
                summdesc="Service description and scope. Outlines IT support services, response times, and service levels."
            ),
            Page(
                page_num=3,
                summdesc="Payment terms and fee schedule. 30-day payment terms, annual fee escalation clause."
            ),
            Page(
                page_num=4,
                summdesc="Liability and indemnification. Limited liability cap at 12 months fees. Standard indemnification."
            ),
            Page(
                page_num=5,
                summdesc="Term and termination. 3-year initial term with auto-renewal. 90-day termination notice."
            ),
            Page(
                page_num=6,
                summdesc="General provisions and signatures. Governing law, dispute resolution, entire agreement."
            )
        ]
    )

    # Sample Document 2: NDA
    doc2 = Document(
        doc_id="DOC-002",
        summdesc="Non-Disclosure Agreement for potential M&A transaction. Bilateral NDA with 3-year confidentiality period. Includes standard exceptions and required disclosures.",
        document_type=DocumentType.AGREEMENT,
        title="Mutual Non-Disclosure Agreement",
        source="M&A Team",
        date_added="2024-02-01",
        pages=[
            Page(
                page_num=1,
                summdesc="Parties and recitals. Identifies both parties and purpose of disclosure."
            ),
            Page(
                page_num=2,
                summdesc="Definition of confidential information. Broad definition with standard exceptions."
            ),
            Page(
                page_num=3,
                summdesc="Obligations and restrictions. Use limitations, disclosure restrictions, employee access."
            ),
            Page(
                page_num=4,
                summdesc="Term, return of materials, and remedies. Equitable relief provision included."
            )
        ]
    )

    # Sample Document 3: Regulatory Filing
    doc3 = Document(
        doc_id="DOC-003",
        summdesc="Annual compliance certification for industry regulator. Covers data privacy, security controls, and operational resilience requirements for fiscal year 2023.",
        document_type=DocumentType.REGULATORY,
        title="Annual Compliance Certification",
        source="Compliance Department",
        date_added="2024-03-15",
        pages=[
            Page(
                page_num=1,
                summdesc="Certification cover page and officer attestation."
            ),
            Page(
                page_num=2,
                summdesc="Data privacy compliance summary. GDPR and CCPA compliance status."
            ),
            Page(
                page_num=3,
                summdesc="Security controls assessment. SOC 2 Type II compliance, penetration testing results."
            ),
            Page(
                page_num=4,
                summdesc="Operational resilience. Business continuity plans, disaster recovery capabilities."
            ),
            Page(
                page_num=5,
                summdesc="Exceptions and remediation plans. Two open items with remediation timeline."
            )
        ]
    )

    data_room.add_document(doc1)
    data_room.add_document(doc2)
    data_room.add_document(doc3)

    return data_room


def run_analysis(
    data_room: DataRoom,
    config: SystemConfig,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run complete legal risk analysis on a data room.

    This function orchestrates the full analysis workflow:
    1. Initialize the main agent
    2. Generate analysis tasks for subagents
    3. Produce outputs (report and dashboard)

    Args:
        data_room: The DataRoom to analyze.
        config: System configuration.
        output_dir: Optional output directory override.

    Returns:
        Dictionary with analysis results and output paths.
    """
    # Set output directory
    output_directory = output_dir or config.output.output_directory
    os.makedirs(output_directory, exist_ok=True)

    # Create main agent
    main_agent = create_main_agent(data_room, config.to_dict())

    # Get system prompt and user content for main agent
    system_prompt = main_agent.get_system_prompt()
    user_content = main_agent.get_user_content()

    # Get subagent configurations
    subagent_configs = main_agent.get_subagent_configurations()

    # Create tools
    data_room_tools = create_data_room_tools(data_room)
    web_tools = create_web_research_tools(config.to_dict().get("web_research", {}))

    # Prepare output paths
    report_path = os.path.join(
        output_directory,
        config.output.report_filename
    )
    dashboard_path = os.path.join(
        output_directory,
        config.output.dashboard_filename
    )

    # Generate analysis task
    analysis_task = create_analysis_task(
        task_description="Perform comprehensive legal risk analysis on all documents in the data room.",
        priority_documents=None,
        focus_categories=None
    )

    # This is where you would integrate with the actual Claude API
    # For now, we return the configuration for the agent system

    return {
        "status": "configured",
        "main_agent": {
            "system_prompt": system_prompt,
            "user_content": user_content
        },
        "subagents": subagent_configs,
        "tools": {
            "data_room": data_room_tools.get_tool_definitions(),
            "web_research": web_tools.get_tool_definitions()
        },
        "tasks": {
            "analysis": analysis_task
        },
        "output_paths": {
            "report": report_path,
            "dashboard": dashboard_path
        },
        "data_room_info": {
            "name": data_room.name,
            "document_count": len(data_room.documents),
            "index": data_room.get_document_index()
        }
    }


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Legal Risk Analysis System"
    )
    parser.add_argument(
        "--data-room",
        type=str,
        help="Path to data room JSON file"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./output",
        help="Output directory for generated files"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use sample data room for demonstration"
    )

    args = parser.parse_args()

    # Load configuration
    config = get_config(args.config)

    # Load or create data room
    if args.sample:
        data_room = create_sample_data_room()
        print("Created sample data room with 3 documents")
    elif args.data_room:
        data_room = load_data_room(args.data_room)
        print(f"Loaded data room from {args.data_room}")
    else:
        print("Error: Please specify --data-room or --sample")
        return

    # Run analysis
    print(f"Running legal risk analysis on '{data_room.name}'...")
    results = run_analysis(data_room, config, args.output_dir)

    # Output results summary
    print("\n=== Legal Risk Analysis Configuration ===")
    print(f"Data Room: {results['data_room_info']['name']}")
    print(f"Documents: {results['data_room_info']['document_count']}")
    print(f"\nOutput Paths:")
    print(f"  Report: {results['output_paths']['report']}")
    print(f"  Dashboard: {results['output_paths']['dashboard']}")
    print(f"\nSubagents Configured: {len(results['subagents'])}")
    print(f"Tools Available: {len(results['tools']['data_room']) + len(results['tools']['web_research'])}")

    # Save configuration for reference
    config_output = os.path.join(args.output_dir, "analysis_config.json")
    os.makedirs(args.output_dir, exist_ok=True)

    # Remove large prompt content for config file
    config_export = {
        "status": results["status"],
        "data_room_info": results["data_room_info"],
        "output_paths": results["output_paths"],
        "subagent_names": list(results["subagents"].keys()),
        "tool_names": {
            "data_room": [t["name"] for t in results["tools"]["data_room"]],
            "web_research": [t["name"] for t in results["tools"]["web_research"]]
        }
    }

    with open(config_output, 'w') as f:
        json.dump(config_export, f, indent=2)

    print(f"\nConfiguration saved to: {config_output}")
    print("\nReady for Claude API integration.")


if __name__ == "__main__":
    main()
