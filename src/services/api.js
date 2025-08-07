import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Your FastAPI backend URL

export const getTemplates = async () => {
  const response = await axios.get(`${API_BASE_URL}/templates`);
  return response.data.templates;
};

export const uploadFiles = async (files, templateId) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  const response = await axios.post(`${API_BASE_URL}/upload?template_id=${templateId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const testWithSampleData = async (templateId) => {
  const response = await axios.get(`${API_BASE_URL}/test?template_id=${templateId}`);
  return response.data;
};