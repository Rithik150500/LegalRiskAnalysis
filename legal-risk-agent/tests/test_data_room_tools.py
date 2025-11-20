# test_data_room_tools.py - Tests for DataRoom and data room tools
import pytest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_room_tools import DataRoom, create_data_room_tools


class TestDataRoom:
    """Test DataRoom class"""

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for testing"""
        return [
            {
                "doc_id": "DOC001",
                "summdesc": "Service Agreement between Company A and Company B",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Cover page with parties and effective date",
                        "page_image": "base64_encoded_image_1"
                    },
                    {
                        "page_num": 2,
                        "summdesc": "Terms and conditions section",
                        "page_image": "base64_encoded_image_2"
                    },
                    {
                        "page_num": 3,
                        "summdesc": "Liability and indemnification clauses",
                        "page_image": "base64_encoded_image_3"
                    }
                ]
            },
            {
                "doc_id": "DOC002",
                "summdesc": "NDA Agreement",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Non-disclosure agreement terms",
                        "page_image": "base64_encoded_image_4"
                    }
                ]
            }
        ]

    @pytest.fixture
    def data_room(self, sample_documents):
        """Create DataRoom instance for testing"""
        return DataRoom(sample_documents)

    def test_data_room_initialization(self, data_room):
        """Test DataRoom initializes correctly"""
        assert "DOC001" in data_room.documents
        assert "DOC002" in data_room.documents
        assert len(data_room.documents) == 2

    def test_data_room_stores_document_by_id(self, data_room):
        """Test documents are stored by their ID"""
        doc = data_room.documents["DOC001"]
        assert doc["summdesc"] == "Service Agreement between Company A and Company B"
        assert len(doc["pages"]) == 3

    def test_get_document_summary_returns_formatted_string(self, data_room):
        """Test get_document_summary returns formatted summary"""
        summary = data_room.get_document_summary("DOC001")

        assert "Document: DOC001" in summary
        assert "Service Agreement" in summary
        assert "Total Pages: 3" in summary
        assert "Page 1:" in summary
        assert "Page 2:" in summary
        assert "Page 3:" in summary

    def test_get_document_summary_not_found(self, data_room):
        """Test get_document_summary handles missing document"""
        result = data_room.get_document_summary("NONEXISTENT")
        assert "Error" in result
        assert "not found" in result

    def test_get_document_pages_all_pages(self, data_room):
        """Test get_document_pages returns all pages when no filter"""
        pages = data_room.get_document_pages("DOC001")

        assert len(pages) == 3
        assert pages[0]["page_num"] == 1
        assert pages[1]["page_num"] == 2
        assert pages[2]["page_num"] == 3

    def test_get_document_pages_specific_pages(self, data_room):
        """Test get_document_pages returns specific pages"""
        pages = data_room.get_document_pages("DOC001", [1, 3])

        assert len(pages) == 2
        page_nums = [p["page_num"] for p in pages]
        assert 1 in page_nums
        assert 3 in page_nums
        assert 2 not in page_nums

    def test_get_document_pages_not_found(self, data_room):
        """Test get_document_pages handles missing document"""
        result = data_room.get_document_pages("NONEXISTENT")
        assert "error" in result[0]

    def test_get_document_pages_missing_page(self, data_room):
        """Test get_document_pages handles missing page numbers"""
        result = data_room.get_document_pages("DOC001", [1, 99])
        assert "error" in result[0]
        assert "99" in str(result[0]["error"])

    def test_get_document_pages_includes_image_data(self, data_room):
        """Test get_document_pages includes image data"""
        pages = data_room.get_document_pages("DOC001", [1])

        assert len(pages) == 1
        assert "image" in pages[0]
        assert pages[0]["image"] == "base64_encoded_image_1"

    def test_get_document_pages_includes_summary(self, data_room):
        """Test get_document_pages includes page summary"""
        pages = data_room.get_document_pages("DOC001", [2])

        assert pages[0]["summdesc"] == "Terms and conditions section"


class TestDataRoomToolCreation:
    """Test create_data_room_tools function"""

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for testing"""
        return [
            {
                "doc_id": "DOC001",
                "summdesc": "Test Document",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Test page",
                        "page_image": "test_image_data"
                    }
                ]
            }
        ]

    @pytest.fixture
    def tools(self, sample_documents):
        """Create tools for testing"""
        data_room = DataRoom(sample_documents)
        return create_data_room_tools(data_room)

    def test_create_data_room_tools_returns_tuple(self, tools):
        """Test create_data_room_tools returns tuple of two functions"""
        assert isinstance(tools, tuple)
        assert len(tools) == 2

    def test_get_document_tool_callable(self, tools):
        """Test get_document tool is callable"""
        get_document, _ = tools
        assert callable(get_document)

    def test_get_document_pages_tool_callable(self, tools):
        """Test get_document_pages tool is callable"""
        _, get_document_pages = tools
        assert callable(get_document_pages)

    def test_get_document_tool_returns_summary(self, tools):
        """Test get_document tool returns document summary"""
        get_document, _ = tools
        result = get_document("DOC001")

        assert "Document: DOC001" in result
        assert "Test Document" in result

    def test_get_document_pages_tool_returns_json(self, tools):
        """Test get_document_pages tool returns JSON string"""
        _, get_document_pages = tools
        result = get_document_pages("DOC001", [1])

        # Should be valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]["page_num"] == 1

    def test_get_document_tool_handles_missing_doc(self, tools):
        """Test get_document tool handles missing document"""
        get_document, _ = tools
        result = get_document("NONEXISTENT")

        assert "Error" in result
        assert "not found" in result

    def test_get_document_pages_tool_handles_missing_doc(self, tools):
        """Test get_document_pages tool handles missing document"""
        _, get_document_pages = tools
        result = get_document_pages("NONEXISTENT", [1])

        parsed = json.loads(result)
        assert "error" in parsed[0]


class TestDataRoomEdgeCases:
    """Test edge cases for DataRoom"""

    def test_empty_data_room(self):
        """Test DataRoom with no documents"""
        data_room = DataRoom([])
        assert len(data_room.documents) == 0

    def test_document_with_no_pages(self):
        """Test DataRoom with document having no pages"""
        docs = [{
            "doc_id": "DOC001",
            "summdesc": "Empty document",
            "pages": []
        }]
        data_room = DataRoom(docs)

        summary = data_room.get_document_summary("DOC001")
        assert "Total Pages: 0" in summary

    def test_document_with_many_pages(self):
        """Test DataRoom with document having many pages"""
        pages = [
            {
                "page_num": i,
                "summdesc": f"Page {i} content",
                "page_image": f"image_{i}"
            }
            for i in range(1, 101)  # 100 pages
        ]
        docs = [{
            "doc_id": "DOC001",
            "summdesc": "Large document",
            "pages": pages
        }]
        data_room = DataRoom(docs)

        summary = data_room.get_document_summary("DOC001")
        assert "Total Pages: 100" in summary

    def test_multiple_documents_same_type(self):
        """Test DataRoom with multiple similar documents"""
        docs = [
            {
                "doc_id": f"DOC{i:03d}",
                "summdesc": f"Contract {i}",
                "pages": [{"page_num": 1, "summdesc": "Page 1", "page_image": "img"}]
            }
            for i in range(1, 11)  # 10 documents
        ]
        data_room = DataRoom(docs)

        assert len(data_room.documents) == 10
        assert "DOC001" in data_room.documents
        assert "DOC010" in data_room.documents
