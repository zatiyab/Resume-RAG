// frontend/HireMind/src/services/api.js
const API_BASE_URL = 'http://localhost:8000'; // Flask backend URL

export const uploadResumes = async (files) => {
  // const formData = new FormData();
  // files.forEach(file => {
  //   formData.append('files', file);
  // });
  // console.log(formData)

  console.log(files);
  
};

export const searchResumes = async (query, k,isJDsearch) => {
  console.log(JSON.stringify({ "user_id":"7a3d2e98-ef7f-4c80-a8b5-1457c9a7d3e0","user_query":query, "k":k}))
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ "user_id":"7a3d2e98-ef7f-4c80-a8b5-1457c9a7d3e0","user_query":query, "k":k}),
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