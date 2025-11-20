# data_room_tools.py
from typing import List, Dict, Any, Optional
import base64
from io import BytesIO
from PIL import Image

class DataRoom:
    """
    Represents a legal data room containing documents with their metadata.

    This class serves as the backend for our data room tools. In a real system,
    this would interface with a document management system, cloud storage, or
    database. For now, we'll implement it as an in-memory structure that you
    can populate with your actual documents.
    """

    def __init__(self, documents: List[Dict[str, Any]]):
        """
        Initialize the data room with a collection of documents.

        Args:
            documents: List of document dictionaries, each containing:
                - doc_id: Unique identifier for the document
                - summdesc: Summary description of the document
                - pages: List of page dictionaries with:
                    - page_num: Page number
                    - summdesc: Summary of the page content
                    - page_image: Either a file path or base64-encoded image data
        """
        self.documents = {doc['doc_id']: doc for doc in documents}

    def get_document_summary(self, doc_id: str) -> str:
        """
        Retrieve the combined summary of all pages in a document.

        This method provides a high-level view without consuming excessive tokens.
        It's designed to be the first tool an Analysis Subagent calls to understand
        what a document contains before deciding which specific pages to examine.

        Args:
            doc_id: The unique identifier for the document

        Returns:
            A formatted string containing the document summary and all page summaries
        """
        if doc_id not in self.documents:
            return f"Error: Document {doc_id} not found in data room."

        doc = self.documents[doc_id]

        # Build a comprehensive summary that includes document-level context
        # and page-level details
        summary_parts = [
            f"Document: {doc_id}",
            f"Summary: {doc['summdesc']}",
            f"Total Pages: {len(doc['pages'])}",
            "\nPage Summaries:"
        ]

        for page in doc['pages']:
            summary_parts.append(
                f"  Page {page['page_num']}: {page['summdesc']}"
            )

        return "\n".join(summary_parts)

    def get_document_pages(
        self,
        doc_id: str,
        page_nums: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve specific page images from a document.

        This is the more expensive operation in terms of tokens because images
        can be quite large. The Analysis Subagent should use this selectively,
        only for pages that the summary indicates contain important information.

        Args:
            doc_id: The unique identifier for the document
            page_nums: Optional list of specific page numbers to retrieve.
                      If None, returns all pages (use with caution for large docs)

        Returns:
            List of dictionaries with page_num, summdesc, and image data
        """
        if doc_id not in self.documents:
            return [{"error": f"Document {doc_id} not found in data room."}]

        doc = self.documents[doc_id]
        pages = doc['pages']

        # Filter to specific pages if requested
        if page_nums is not None:
            pages = [p for p in pages if p['page_num'] in page_nums]

            # Check if any requested pages weren't found
            found_nums = {p['page_num'] for p in pages}
            missing = set(page_nums) - found_nums
            if missing:
                return [{
                    "error": f"Pages {sorted(missing)} not found in document {doc_id}"
                }]

        # Prepare page data for return
        result = []
        for page in pages:
            page_data = {
                'page_num': page['page_num'],
                'summdesc': page['summdesc'],
                'image': page['page_image']  # This should be base64 or image data
            }
            result.append(page_data)

        return result

# Now let's create the actual tools that the subagents will use
# These are wrapper functions that follow LangChain's tool interface

def create_data_room_tools(data_room: DataRoom):
    """
    Factory function that creates tool instances bound to a specific data room.

    This approach allows us to create tools that have access to the data room
    instance without exposing the entire DataRoom class to the agents. It's a
    form of dependency injection that keeps our tool interface clean.

    Args:
        data_room: The DataRoom instance containing the documents

    Returns:
        A tuple of (get_document, get_document_pages) tool functions
    """

    def get_document(doc_id: str) -> str:
        """
        Retrieve a high-level summary of a document including summaries of all pages.

        Use this tool first to understand what a document contains before deciding
        whether to retrieve specific page images. This is much more token-efficient
        than retrieving all pages immediately.

        Args:
            doc_id: The unique identifier for the document (e.g., "DOC001")

        Returns:
            A formatted summary of the document and all its pages

        Example:
            get_document("DOC001")
            # Returns summary with page-by-page descriptions
        """
        return data_room.get_document_summary(doc_id)

    def get_document_pages(doc_id: str, page_nums: List[int]) -> str:
        """
        Retrieve specific page images from a document for detailed analysis.

        Use this tool after reviewing the document summary to fetch only the pages
        that appear to contain relevant legal content. Page images consume significant
        tokens, so be selective about which pages you retrieve.

        Args:
            doc_id: The unique identifier for the document
            page_nums: List of specific page numbers to retrieve (e.g., [1, 3, 7])

        Returns:
            JSON string containing page data with images

        Example:
            get_document_pages("DOC001", [1, 5, 6])
            # Returns detailed data for pages 1, 5, and 6 only
        """
        pages = data_room.get_document_pages(doc_id, page_nums)

        # Format the response in a way that's easy for the agent to parse
        import json
        return json.dumps(pages, indent=2)

    return get_document, get_document_pages
