import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import TemplateSelector from './components/TemplateSelector';
import SlideViewer from './components/SlideViewer';
import { uploadFiles, testWithSampleData } from './services/api';
import './App.css';

function App() {
  const [templateId, setTemplateId] = useState('saas');
  const [slideData, setSlideData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFilesSelected = async (files) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await uploadFiles(files, templateId);
      setSlideData(data);
    } catch (err) {
      setError(err.message || 'Failed to process files');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestWithSampleData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await testWithSampleData(templateId);
      setSlideData(data);
    } catch (err) {
      setError(err.message || 'Failed to load sample data');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Boardroom Slide Generator</h1>
      </header>
      
      <main className="app-content">
        <div className="controls">
          <TemplateSelector onTemplateSelect={setTemplateId} />
          <FileUpload onFilesSelected={handleFilesSelected} />
          <button 
            onClick={handleTestWithSampleData} 
            className="test-btn"
            disabled={isLoading}
          >
            {isLoading ? 'Loading...' : 'Test with Sample Data'}
          </button>
        </div>
        
        {isLoading && <div className="loading">Processing...</div>}
        {error && <div className="error">{error}</div>}
        
        <div className="slide-area">
          {slideData ? (
            <SlideViewer slideData={slideData} />
          ) : (
            <div className="welcome-message">
              <p>Upload your business data files (CSV, Excel, PDF) or click "Test with Sample Data" to get started.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
import React from 'react';
import FileUpload from './components/FileUpload';

const App = () => {
  const handleFiles = (files) => {
    console.log('Selected files:', files);

    // Optional: send to backend
    const formData = new FormData();
    files.forEach(file => formData.append('file', file));

    fetch('http://localhost:8001/upload/', {
      method: 'POST',
      body: formData,
    })
    .then(res => res.json())
    .then(data => {
      console.log('Upload response:', data);
    })
    .catch(err => {
      console.error('Error uploading:', err);
    });
  };

  return (
    <div className="App">
      <h1>📊 AI Slide Generator</h1>
      <FileUpload onFilesSelected={handleFiles} />
    </div>
  );
};

export default App;