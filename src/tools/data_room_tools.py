"""
Data Room Tools for Legal Risk Analysis

These tools provide access to documents and pages in the data room
for the analysis subagent.
"""

from typing import List, Dict, Any, Optional
import json

from ..models.data_room import DataRoom, Document, Page


class DataRoomTools:
    """
    Tools for accessing and retrieving documents from the data room.

    These tools are used by the Analysis Subagent to retrieve document
    content for legal risk analysis.
    """

    def __init__(self, data_room: DataRoom):
        """
        Initialize with a data room instance.

        Args:
            data_room: The DataRoom instance to provide access to.
        """
        self.data_room = data_room

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get the tool definitions for Claude API integration.

        Returns:
            List of tool definitions in Claude API format.
        """
        return [
            {
                "name": "get_document",
                "description": """Retrieve a document from the data room by its ID.

Returns the combined summary description of all pages in the document,
providing a comprehensive overview of the document's content.

Use this tool when you need to:
- Get an overview of a specific document's contents
- Understand the full scope of a document before detailed analysis
- Review the summary of all pages in a document

The returned content includes:
- Document summary description
- Combined summaries of all pages
- Document metadata (type, title, source)

Note: This does not return page images. Use get_document_pages for visual content.""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "The unique identifier of the document to retrieve"
                        }
                    },
                    "required": ["doc_id"]
                }
            },
            {
                "name": "get_document_pages",
                "description": """Retrieve specific pages from a document including their images.

Returns the page images (base64 encoded) along with page summaries and
extracted text for the specified page numbers.

Use this tool when you need to:
- Examine specific pages in detail
- View the actual page images for visual analysis
- Extract text from particular pages
- Analyze specific sections of a document

Parameters:
- doc_id: The document identifier
- page_nums: List of page numbers to retrieve (1-indexed)

Returns page images that can be analyzed visually for:
- Signatures and dates
- Tables and figures
- Specific clauses or sections
- Formatting and layout issues""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "The unique identifier of the document"
                        },
                        "page_nums": {
                            "type": "array",
                            "items": {
                                "type": "integer"
                            },
                            "description": "List of page numbers to retrieve (1-indexed)"
                        }
                    },
                    "required": ["doc_id", "page_nums"]
                }
            }
        ]

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Retrieve a document and return combined summary of all pages.

        Args:
            doc_id: The unique identifier of the document.

        Returns:
            Dictionary containing document information and combined summaries.
        """
        document = self.data_room.get_document(doc_id)

        if not document:
            return {
                "success": False,
                "error": f"Document with ID '{doc_id}' not found in data room",
                "available_documents": [
                    {"doc_id": d.doc_id, "title": d.title}
                    for d in self.data_room.documents
                ]
            }

        return {
            "success": True,
            "doc_id": document.doc_id,
            "title": document.title,
            "document_type": document.document_type.value,
            "source": document.source,
            "date_added": document.date_added,
            "combined_summary": document.get_combined_summary(),
            "page_count": len(document.pages),
            "metadata": document.metadata
        }

    def get_document_pages(
        self,
        doc_id: str,
        page_nums: List[int]
    ) -> Dict[str, Any]:
        """
        Retrieve specific pages from a document with their images.

        Args:
            doc_id: The unique identifier of the document.
            page_nums: List of page numbers to retrieve.

        Returns:
            Dictionary containing page information and images.
        """
        document = self.data_room.get_document(doc_id)

        if not document:
            return {
                "success": False,
                "error": f"Document with ID '{doc_id}' not found in data room"
            }

        pages = document.get_pages(page_nums)

        if not pages:
            available_pages = [p.page_num for p in document.pages]
            return {
                "success": False,
                "error": f"No pages found for numbers {page_nums}",
                "available_pages": available_pages
            }

        # Build page data with images
        page_data = []
        for page in sorted(pages, key=lambda p: p.page_num):
            page_info = {
                "page_num": page.page_num,
                "summdesc": page.summdesc,
                "extracted_text": page.extracted_text,
                "metadata": page.metadata
            }

            # Include page image if available
            if page.page_image:
                page_info["page_image"] = {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": page.page_image
                }

            page_data.append(page_info)

        return {
            "success": True,
            "doc_id": doc_id,
            "document_title": document.title,
            "requested_pages": page_nums,
            "returned_pages": len(page_data),
            "pages": page_data
        }

    def handle_tool_call(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle a tool call from the Claude API.

        Args:
            tool_name: Name of the tool to execute.
            tool_input: Input parameters for the tool.

        Returns:
            Tool execution result.
        """
        if tool_name == "get_document":
            return self.get_document(tool_input["doc_id"])

        elif tool_name == "get_document_pages":
            return self.get_document_pages(
                tool_input["doc_id"],
                tool_input["page_nums"]
            )

        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }


def create_data_room_tools(data_room: DataRoom) -> DataRoomTools:
    """
    Factory function to create DataRoomTools instance.

    Args:
        data_room: The DataRoom to provide access to.

    Returns:
        Configured DataRoomTools instance.
    """
    return DataRoomTools(data_room)
