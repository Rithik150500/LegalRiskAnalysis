# services/indexing_pipeline.py - Data Room Indexing Pipeline
import os
import subprocess
import base64
import asyncio
import json
import tempfile
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from PIL import Image
from pdf2image import convert_from_path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPT5NanoClient:
    """Client for GPT-5 Nano API for vision-based summarization"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("GPT5_NANO_MODEL", "gpt-4o-mini")  # Default to gpt-4o-mini as proxy for GPT-5 Nano

        if not self.api_key:
            logger.warning("No OpenAI API key configured. Set OPENAI_API_KEY environment variable.")

    async def summarize_page_image(self, image_base64: str, page_num: int, doc_name: str) -> str:
        """Send page image to GPT-5 Nano and get summarized description"""

        if not self.api_key:
            return f"[Page {page_num}] API key not configured - placeholder summary for {doc_name}"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a document analysis expert. Analyze the provided document page image and create a concise summary that captures the key information, topics, entities, dates, and any important details. Focus on factual content that would be useful for indexing and search purposes."
                            },
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"Analyze this page (page {page_num}) from the document '{doc_name}'. Provide a concise summary (2-4 sentences) of the key content, including any important entities, dates, numbers, or legal terms."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{image_base64}",
                                            "detail": "low"
                                        }
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 300
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"GPT-5 Nano API error: {response.status_code} - {response.text}")
                    return f"[Page {page_num}] Error processing page"

        except Exception as e:
            logger.error(f"Error calling GPT-5 Nano API: {e}")
            return f"[Page {page_num}] Error: {str(e)}"

    async def summarize_document(self, page_summaries: List[str], doc_name: str) -> str:
        """Combine page summaries and get overall document summary using GPT-5 Nano"""

        if not self.api_key:
            return f"Document summary placeholder for {doc_name}. Contains {len(page_summaries)} pages."

        combined_summaries = "\n\n".join([
            f"Page {i+1}: {summary}"
            for i, summary in enumerate(page_summaries)
        ])

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a document analysis expert. Synthesize the provided page summaries into a comprehensive document summary that captures the main topics, key entities, important dates, and overall purpose of the document. The summary should be useful for indexing and searching the document."
                            },
                            {
                                "role": "user",
                                "content": f"Create a comprehensive summary of the document '{doc_name}' based on these page summaries:\n\n{combined_summaries}\n\nProvide a well-structured summary (3-5 sentences) that captures the document's main topics, key entities, dates, and purpose."
                            }
                        ],
                        "max_tokens": 500
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"GPT-5 Nano API error: {response.status_code} - {response.text}")
                    return f"Error generating document summary for {doc_name}"

        except Exception as e:
            logger.error(f"Error calling GPT-5 Nano API: {e}")
            return f"Error: {str(e)}"


class DataRoomIndexingPipeline:
    """Pipeline for indexing documents in a data room"""

    def __init__(self,
                 upload_dir: str = None,
                 output_dir: str = None,
                 temp_dir: str = None,
                 api_key: Optional[str] = None):

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.upload_dir = upload_dir or os.path.join(base_dir, "uploads")
        self.output_dir = output_dir or os.path.join(base_dir, "outputs")
        self.temp_dir = temp_dir or os.path.join(base_dir, "temp")
        self.images_dir = os.path.join(self.output_dir, "page_images")

        # Create directories
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

        # Initialize GPT-5 Nano client
        self.gpt_client = GPT5NanoClient(api_key=api_key)

        # Supported file types for conversion
        self.convertible_extensions = {
            '.doc', '.docx', '.odt', '.rtf', '.txt',
            '.xls', '.xlsx', '.ods', '.csv',
            '.ppt', '.pptx', '.odp',
            '.html', '.htm'
        }

    def convert_to_pdf(self, file_path: str) -> str:
        """Convert file to PDF using LibreOffice"""

        file_extension = os.path.splitext(file_path)[1].lower()

        # If already PDF, return as is
        if file_extension == '.pdf':
            return file_path

        # Check if file type is supported
        if file_extension not in self.convertible_extensions:
            raise ValueError(f"Unsupported file type: {file_extension}")

        # Create output directory for converted PDFs
        pdf_output_dir = os.path.join(self.temp_dir, "converted_pdfs")
        os.makedirs(pdf_output_dir, exist_ok=True)

        try:
            # Use LibreOffice to convert to PDF
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', pdf_output_dir,
                file_path
            ]

            logger.info(f"Converting {file_path} to PDF...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                logger.error(f"LibreOffice conversion failed: {result.stderr}")
                raise RuntimeError(f"Failed to convert {file_path} to PDF: {result.stderr}")

            # Get the output PDF path
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            pdf_path = os.path.join(pdf_output_dir, f"{base_name}.pdf")

            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"Converted PDF not found: {pdf_path}")

            logger.info(f"Successfully converted to PDF: {pdf_path}")
            return pdf_path

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"LibreOffice conversion timed out for {file_path}")
        except FileNotFoundError:
            raise RuntimeError("LibreOffice not found. Please install LibreOffice.")

    def extract_pages_as_images(self, pdf_path: str, doc_id: str, dpi: int = 150) -> List[Dict[str, Any]]:
        """Extract all pages from PDF as individual images"""

        logger.info(f"Extracting pages from PDF: {pdf_path}")

        # Create directory for this document's page images
        doc_images_dir = os.path.join(self.images_dir, doc_id)
        os.makedirs(doc_images_dir, exist_ok=True)

        try:
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                fmt='png'
            )

            pages = []
            for page_num, image in enumerate(images, 1):
                # Save image
                image_filename = f"page_{page_num:04d}.png"
                image_path = os.path.join(doc_images_dir, image_filename)
                image.save(image_path, 'PNG')

                # Convert to base64 for API calls
                with open(image_path, 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')

                pages.append({
                    'page_num': page_num,
                    'image_path': image_path,
                    'image_base64': image_base64
                })

                logger.info(f"Extracted page {page_num}/{len(images)}")

            return pages

        except Exception as e:
            logger.error(f"Error extracting pages from PDF: {e}")
            raise

    async def process_document(self,
                               file_path: str,
                               doc_id: str,
                               original_filename: str,
                               progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """Process a single document through the full pipeline"""

        logger.info(f"Processing document: {original_filename} ({doc_id})")

        # Step 1: Convert to PDF if needed
        if progress_callback:
            await progress_callback(doc_id, 10, "Converting to PDF")

        pdf_path = self.convert_to_pdf(file_path)

        # Step 2: Extract pages as images
        if progress_callback:
            await progress_callback(doc_id, 20, "Extracting pages as images")

        pages = self.extract_pages_as_images(pdf_path, doc_id)
        total_pages = len(pages)

        # Step 3: Get page summaries using GPT-5 Nano
        page_summaries = []
        pages_data = []

        for i, page in enumerate(pages):
            page_num = page['page_num']
            progress_pct = 20 + int((i / total_pages) * 50)  # 20-70%

            if progress_callback:
                await progress_callback(doc_id, progress_pct, f"Summarizing page {page_num}/{total_pages}")

            # Send to GPT-5 Nano for summarization
            summary = await self.gpt_client.summarize_page_image(
                page['image_base64'],
                page_num,
                original_filename
            )

            page_summaries.append(summary)
            pages_data.append({
                'page_num': page_num,
                'summdesc': summary,
                'image_path': page['image_path'],
                'has_image': True
            })

            logger.info(f"Page {page_num} summarized")

        # Step 4: Generate document summary from all page summaries
        if progress_callback:
            await progress_callback(doc_id, 80, "Generating document summary")

        document_summary = await self.gpt_client.summarize_document(
            page_summaries,
            original_filename
        )

        if progress_callback:
            await progress_callback(doc_id, 100, "Complete")

        return {
            'doc_id': doc_id,
            'original_filename': original_filename,
            'page_count': total_pages,
            'pages_data': pages_data,
            'summdesc': document_summary,
            'processed_at': datetime.utcnow().isoformat()
        }

    async def build_data_room_index(self,
                                    documents: List[Dict[str, Any]],
                                    progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """Build the complete data room index from multiple documents"""

        logger.info(f"Building data room index for {len(documents)} documents")

        indexed_documents = []
        total_docs = len(documents)

        for i, doc in enumerate(documents):
            doc_progress = int((i / total_docs) * 100)

            if progress_callback:
                await progress_callback(
                    'index',
                    doc_progress,
                    f"Processing document {i+1}/{total_docs}: {doc.get('original_filename', doc['doc_id'])}"
                )

            # Process each document
            result = await self.process_document(
                file_path=doc['file_path'],
                doc_id=doc['doc_id'],
                original_filename=doc.get('original_filename', os.path.basename(doc['file_path']))
            )

            indexed_documents.append(result)

        # Build the final index
        data_room_index = {
            'index_id': f"IDX{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            'created_at': datetime.utcnow().isoformat(),
            'total_documents': len(indexed_documents),
            'total_pages': sum(doc['page_count'] for doc in indexed_documents),
            'documents': indexed_documents
        }

        # Save index to file
        index_path = os.path.join(self.output_dir, f"{data_room_index['index_id']}.json")
        with open(index_path, 'w') as f:
            json.dump(data_room_index, f, indent=2)

        logger.info(f"Data room index saved to: {index_path}")

        if progress_callback:
            await progress_callback('index', 100, "Data room index complete")

        return data_room_index

    def cleanup_temp_files(self):
        """Clean up temporary files created during processing"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir, exist_ok=True)
            logger.info("Temporary files cleaned up")


# Utility functions for direct usage
async def index_single_document(file_path: str, doc_id: str, original_filename: str = None) -> Dict[str, Any]:
    """Convenience function to index a single document"""
    pipeline = DataRoomIndexingPipeline()
    return await pipeline.process_document(
        file_path=file_path,
        doc_id=doc_id,
        original_filename=original_filename or os.path.basename(file_path)
    )


async def index_data_room(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Convenience function to index multiple documents"""
    pipeline = DataRoomIndexingPipeline()
    return await pipeline.build_data_room_index(documents)
