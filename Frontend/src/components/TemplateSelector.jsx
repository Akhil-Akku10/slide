import React, { useState, useEffect } from 'react';
import { getTemplates } from '../services/api';

const TemplateSelector = ({ onTemplateSelect }) => {
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const templateList = await getTemplates();
        setTemplates(templateList);
        if (templateList.length > 0) {
          setSelectedTemplate(templateList[0]);
          onTemplateSelect(templateList[0]);
        }
      } catch (error) {
        console.error('Error fetching templates:', error);
      }
    };

    fetchTemplates();
  }, [onTemplateSelect]);

  const handleTemplateChange = (e) => {
    const template = e.target.value;
    setSelectedTemplate(template);
    onTemplateSelect(template);
  };

  return (
    <div className="template-selector">
      <h3>Select Template</h3>
      <select 
        value={selectedTemplate} 
        onChange={handleTemplateChange}
        className="template-dropdown"
      >
        {templates.map((template) => (
          <option key={template} value={template}>
            {template.charAt(0).toUpperCase() + template.slice(1)}
          </option>
        ))}
      </select>
    </div>
  );
};

export default TemplateSelector;