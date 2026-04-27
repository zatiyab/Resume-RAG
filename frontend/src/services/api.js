// frontend/HireMind/src/services/api.js
const API_BASE_URL = 'http://localhost:5000';

export const uploadResumes = async (files) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const userId = localStorage.getItem('user_id') || "be54d72a-4e8f-450b-99a7-8b9770b6a469";
  const response = await fetch(`${API_BASE_URL}/upload_resumes?user_id=${userId}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorBody = null;
    try {
      errorBody = await response.json();
    } catch {
      errorBody = { detail: 'Upload failed' };
    }
    throw new Error(errorBody?.detail?.message || errorBody?.detail || 'Upload failed');
  }

  return response.json();
};

export const searchResumes = async (query, k,isJDsearch) => {
  const userId = localStorage.getItem('user_id') || "be54d72a-4e8f-450b-99a7-8b9770b6a469";
  console.log(JSON.stringify({ "user_id": userId, "user_query":query, "k":k}))
  const response = await fetch(`${API_BASE_URL}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ "user_id": userId,"user_query":query, "k":k}),
  });
  return response.json();
};

export const downloadResumes = async (files) => {
  const userId = localStorage.getItem('user_id') || "be54d72a-4e8f-450b-99a7-8b9770b6a469";
  const response = await fetch(`${API_BASE_URL}/download_resumes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ files, user_id: userId }),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to download resumes');
  }
  
  return response.blob(); // Returns blob for file download
};

export const signupUser = async (userData) => {
  const response = await fetch(`${API_BASE_URL}/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });
  return response.json(); 
};

export const loginUser = async (credentials) => {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });
  return response.json();
};
