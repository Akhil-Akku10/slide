import React, { useState } from 'react';
import { FiUpload, FiX } from 'react-icons/fi';

const FileUpload = ({ onFilesSelected }) => {
  const [files, setFiles] = useState([]);

  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files);
    setFiles([...files, ...newFiles]);
  };

  const removeFile = (index) => {
    const updatedFiles = [...files];
    updatedFiles.splice(index, 1);
    setFiles(updatedFiles);
  };

  return (
    <div className="file-upload">
      <div className="file-dropzone">
        <label htmlFor="file-input" className="file-label">
          <FiUpload className="upload-icon" />
          <span>Drag & drop files here or click to browse</span>
          <input
            id="file-input"
            type="file"
            multiple
            accept=".csv,.xlsx,.xls,.pdf"
            onChange={handleFileChange}
            className="file-input"
          />
        </label>
      </div>
      
      {files.length > 0 && (
        <div className="file-list">
          <h4>Selected Files:</h4>
          <ul>
            {files.map((file, index) => (
              <li key={index}>
                <span>{file.name}</span>
                <button onClick={() => removeFile(index)} className="remove-btn">
                  <FiX />
                </button>
              </li>
            ))}
          </ul>
          <button onClick={() => onFilesSelected(files)} className="process-btn">
            Process Files
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;