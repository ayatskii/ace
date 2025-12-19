import { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import AdminLayout from '../../components/layout/AdminLayout';

export default function MediaLibrary() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, audio, image
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchFiles();
  }, [filter]);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/upload/files?type=${filter}`);
      setFiles(response.data);
    } catch (error) {
      console.error('Failed to fetch files:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e, type) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      const endpoint = type === 'audio' ? '/upload/audio' : '/upload/image';
      await apiClient.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchFiles();
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (file) => {
    if (!confirm(`Delete ${file.name}? This cannot be undone.`)) return;
    
    try {
      // file.type is 'audio' or 'image' from the API
      // file.url is like /uploads/audio/filename.mp3
      // We need to extract filename
      const filename = file.name;
      const fileType = file.type === 'audio' ? 'audio' : 'images'; // API expects 'images' for delete endpoint
      
      await apiClient.delete(`/upload/files/${fileType}/${filename}`);
      fetchFiles();
    } catch (error) {
      console.error('Delete failed:', error);
      alert('Failed to delete file');
    }
  };

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleDateString();
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Media Library</h1>
          <div className="flex space-x-2">
            <label className="cursor-pointer px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm flex items-center">
              <span>+ Upload Audio</span>
              <input 
                type="file" 
                accept="audio/*" 
                className="hidden" 
                onChange={(e) => handleFileUpload(e, 'audio')}
                disabled={uploading}
              />
            </label>
            <label className="cursor-pointer px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm flex items-center">
              <span>+ Upload Image</span>
              <input 
                type="file" 
                accept="image/*" 
                className="hidden" 
                onChange={(e) => handleFileUpload(e, 'image')}
                disabled={uploading}
              />
            </label>
          </div>
        </div>

        <div className="flex space-x-4 border-b border-gray-200 pb-4">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              filter === 'all' ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            All Files
          </button>
          <button
            onClick={() => setFilter('audio')}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              filter === 'audio' ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Audio
          </button>
          <button
            onClick={() => setFilter('images')}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              filter === 'images' ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Images
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">Loading media...</div>
        ) : files.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
            <p className="text-gray-500">No media files found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {files.map((file, idx) => (
              <div key={idx} className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition">
                <div className="aspect-w-16 aspect-h-9 bg-gray-100 flex items-center justify-center relative group">
                  {file.type === 'image' ? (
                    <img 
                      src={file.url} 
                      alt={file.name} 
                      className="object-cover w-full h-48"
                    />
                  ) : (
                    <div className="w-full h-48 flex flex-col items-center justify-center text-gray-400">
                      <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                      </svg>
                      <span className="text-xs uppercase font-bold">Audio</span>
                    </div>
                  )}
                  
                  {/* Overlay Actions */}
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100 space-x-2">
                    <a 
                      href={file.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="p-2 bg-white rounded-full hover:bg-gray-100 text-gray-900"
                      title="View/Play"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </a>
                    <button 
                      onClick={() => handleDelete(file)}
                      className="p-2 bg-white rounded-full hover:bg-red-50 text-red-600"
                      title="Delete"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
                
                <div className="p-3">
                  <p className="text-sm font-medium text-gray-900 truncate" title={file.name}>{file.name}</p>
                  <div className="flex justify-between items-center mt-1">
                    <span className="text-xs text-gray-500">{formatSize(file.size)}</span>
                    <span className="text-xs text-gray-400">{formatDate(file.created_at)}</span>
                  </div>
                  <div className="mt-2">
                    <input 
                      type="text" 
                      readOnly 
                      value={file.url} 
                      className="w-full text-xs bg-gray-50 border border-gray-200 rounded px-2 py-1 text-gray-600 select-all"
                      onClick={(e) => e.target.select()}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
