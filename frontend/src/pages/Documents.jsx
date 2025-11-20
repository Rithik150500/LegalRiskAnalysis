import { useState, useEffect, useRef } from 'react';
import {
  Upload,
  FileText,
  Trash2,
  Eye,
  Search,
  X,
  File,
  FileType
} from 'lucide-react';
import { documentsApi } from '../api/client';

function Documents() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDoc, setSelectedDoc] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const data = await documentsApi.list();
      setDocuments(data);
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setError(null);

    try {
      for (const file of files) {
        await documentsApi.upload(file);
      }
      await fetchDocuments();
    } catch (err) {
      setError('Failed to upload document');
      console.error(err);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async (docId) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await documentsApi.delete(docId);
      await fetchDocuments();
    } catch (err) {
      setError('Failed to delete document');
      console.error(err);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredDocuments = documents.filter(doc =>
    doc.original_filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.doc_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.summary?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getFileIcon = (fileType) => {
    switch (fileType?.toLowerCase()) {
      case 'pdf':
        return <FileText className="h-5 w-5 text-red-500" />;
      case 'docx':
      case 'doc':
        return <FileType className="h-5 w-5 text-blue-500" />;
      default:
        return <File className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600 mt-1">Manage your legal documents</p>
        </div>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="btn btn-primary flex items-center gap-2"
        >
          <Upload className="h-4 w-4" />
          {uploading ? 'Uploading...' : 'Upload Document'}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.doc,.docx,.txt"
          multiple
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search documents..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="input pl-10"
        />
        {searchTerm && (
          <button
            onClick={() => setSearchTerm('')}
            className="absolute right-3 top-1/2 -translate-y-1/2"
          >
            <X className="h-5 w-5 text-gray-400 hover:text-gray-600" />
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Documents Table */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">
              {searchTerm ? 'No documents match your search' : 'No documents uploaded yet'}
            </p>
            {!searchTerm && (
              <button
                onClick={() => fileInputRef.current?.click()}
                className="mt-4 text-primary-600 hover:text-primary-700"
              >
                Upload your first document
              </button>
            )}
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Document</th>
                <th>Type</th>
                <th>Size</th>
                <th>Pages</th>
                <th>Uploaded</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredDocuments.map((doc) => (
                <tr key={doc.doc_id} className="hover:bg-gray-50">
                  <td>
                    <div className="flex items-center gap-3">
                      {getFileIcon(doc.file_type)}
                      <div>
                        <p className="font-medium text-gray-900">{doc.original_filename}</p>
                        <p className="text-xs text-gray-500">{doc.doc_id}</p>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="badge bg-gray-100 text-gray-800">
                      {doc.file_type}
                    </span>
                  </td>
                  <td className="text-gray-600">{formatFileSize(doc.file_size)}</td>
                  <td className="text-gray-600">{doc.page_count}</td>
                  <td className="text-gray-600">{formatDate(doc.uploaded_at)}</td>
                  <td>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setSelectedDoc(doc)}
                        className="p-2 hover:bg-gray-100 rounded-lg"
                        title="View details"
                      >
                        <Eye className="h-4 w-4 text-gray-600" />
                      </button>
                      <button
                        onClick={() => handleDelete(doc.doc_id)}
                        className="p-2 hover:bg-red-50 rounded-lg"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4 text-red-600" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Document Detail Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Document Details</h3>
              <button
                onClick={() => setSelectedDoc(null)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="h-5 w-5 text-gray-600" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <p className="text-sm text-gray-500">Document ID</p>
                <p className="font-medium">{selectedDoc.doc_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Filename</p>
                <p className="font-medium">{selectedDoc.original_filename}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Summary</p>
                <p className="text-gray-700">{selectedDoc.summary || 'No summary available'}</p>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Type</p>
                  <p className="font-medium">{selectedDoc.file_type}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Size</p>
                  <p className="font-medium">{formatFileSize(selectedDoc.file_size)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Pages</p>
                  <p className="font-medium">{selectedDoc.page_count}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500">Uploaded</p>
                <p className="font-medium">{formatDate(selectedDoc.uploaded_at)}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Documents;
