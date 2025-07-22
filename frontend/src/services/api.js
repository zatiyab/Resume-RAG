// frontend/HireMind/src/services/api.js
const API_BASE_URL = 'http://localhost:5000'; // Flask backend URL

export const uploadResumes = async (files) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  const response = await fetch(`${API_BASE_URL}/upload_resumes`, {
    method: 'POST',
    body: formData,
  });
  return response.json();
};

export const searchResumes = async (query, k, isJDSearch) => {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, k, is_jd_search: isJDSearch }),
  });
  return response.json();
};

export const downloadResumes = async (files) => {
  const response = await fetch(`${API_BASE_URL}/download_resumes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ files }),
  });
  return response.blob(); // Returns blob for file download
};

// You might need an API to fetch chat history from the backend if you store it per chat session
// export const getChatHistory = async (chatId) => { ... }
// export const startNewChat = async () => { ... }