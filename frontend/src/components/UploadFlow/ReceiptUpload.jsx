/**
 * Receipt image upload component
 */
import { useState } from 'react';
import './ReceiptUpload.css';

export const ReceiptUpload = ({ onUploadSuccess, onError }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      handleFile(file);
    } else {
      onError?.('Please upload an image file');
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleFile = (file) => {
    setSelectedFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(file);

    onUploadSuccess?.(file);
  };

  return (
    <div className="receipt-upload">
      <div
        className={`upload-area ${isDragging ? 'dragging' : ''} ${preview ? 'has-preview' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {preview ? (
          <div className="preview-container">
            <img src={preview} alt="Receipt preview" className="receipt-preview" />
            <button
              className="change-button"
              onClick={() => {
                setPreview(null);
                setSelectedFile(null);
              }}
            >
              Change Receipt
            </button>
          </div>
        ) : (
          <>
            <div className="upload-icon">📸</div>
            <h3>Upload Receipt</h3>
            <p>Drag and drop a receipt image here, or click to browse</p>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileInput}
              className="file-input"
              id="file-input"
            />
            <label htmlFor="file-input" className="browse-button">
              Choose File
            </label>
          </>
        )}
      </div>
    </div>
  );
};
