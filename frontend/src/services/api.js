// frontend/HireMind/src/services/api.js
import { getUserIdFromToken, isTokenExpired } from '../utils/helpers.js';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
console.log(API_BASE_URL);
const CACHE_PREFIX = 'hiremind-cache:';
const CACHE_TTLS = {
  resumes: 60_000,
  chatGroups: 30_000,
  chatHistory: 30_000,
};

const canUseSessionStorage = () => typeof window !== 'undefined' && typeof window.sessionStorage !== 'undefined';

const cacheKey = (...parts) => `${CACHE_PREFIX}${parts.join(':')}`;

const readCache = (key) => {
  if (!canUseSessionStorage()) return null;

  try {
    const rawValue = window.sessionStorage.getItem(key);
    if (!rawValue) return null;

    const parsed = JSON.parse(rawValue);
    if (!parsed || typeof parsed !== 'object') return null;

    if (parsed.expiresAt && parsed.expiresAt < Date.now()) {
      window.sessionStorage.removeItem(key);
      return null;
    }

    return parsed.value ?? null;
  } catch {
    return null;
  }
};

const writeCache = (key, value, ttlMs) => {
  if (!canUseSessionStorage()) return;

  try {
    window.sessionStorage.setItem(
      key,
      JSON.stringify({
        value,
        expiresAt: Date.now() + ttlMs,
      })
    );
  } catch {
    // Cache is best-effort only.
  }
};

const removeCacheByPrefix = (suffix = '') => {
  if (!canUseSessionStorage()) return;

  const prefix = `${CACHE_PREFIX}${suffix}`;
  const keysToRemove = [];

  for (let index = 0; index < window.sessionStorage.length; index += 1) {
    const key = window.sessionStorage.key(index);
    if (key && key.startsWith(prefix)) {
      keysToRemove.push(key);
    }
  }

  keysToRemove.forEach((key) => window.sessionStorage.removeItem(key));
};

const invalidateResumesCache = (userId) => removeCacheByPrefix(`resumes:${userId}`);
const invalidateChatCache = (userId) => {
  removeCacheByPrefix(`chatGroups:${userId}`);
  removeCacheByPrefix(`chatHistory:${userId}`);
};

export const invalidateAllAppCaches = () => removeCacheByPrefix('');

export const uploadResumes = async (files) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const token = localStorage.getItem('access_token');
  const userId = getUserIdFromToken(token);
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

  invalidateResumesCache(userId);
  return response.json();
};

export const getUserResumes = async () => {
  const token = localStorage.getItem('access_token');
  const userId = getUserIdFromToken(token);
  const key = cacheKey('resumes', userId);
  const cached = readCache(key);
  if (cached) return cached;

  const response = await fetch(`${API_BASE_URL}/resumes?user_id=${userId}`);
  if (!response.ok) {
    let errorBody = null;
    try {
      errorBody = await response.json();
    } catch {
      errorBody = { detail: 'Failed to fetch resumes' };
    }
    throw new Error(errorBody?.detail || 'Failed to fetch resumes');
  }

  const payload = await response.json();
  writeCache(key, payload, CACHE_TTLS.resumes);
  return payload;
};

export const getResume = async (fileName) => {
  const token = localStorage.getItem('access_token');
  const userId = getUserIdFromToken(token);
  const response = await fetch(`${API_BASE_URL}/resume?user_id=${userId}&file_name=${encodeURIComponent(fileName)}`);
  if (!response.ok) {
    let errorBody = null;
    try {
      errorBody = await response.json();
    } catch {
      errorBody = { detail: 'Failed to fetch resume' };
    }
    throw new Error(errorBody?.detail || 'Failed to fetch resume');
  }
  return response.blob();
};

export const deleteResume = async (fileName) => {
  const token = localStorage.getItem('access_token');
  const userId = getUserIdFromToken(token);
  const response = await fetch(`${API_BASE_URL}/resume?user_id=${userId}&file_name=${encodeURIComponent(fileName)}`, {
    method: 'DELETE'
  });
  if (!response.ok) {
    let errorBody = null;
    try {
      errorBody = await response.json();
    } catch {
      errorBody = { detail: 'Failed to delete resume' };
    }
    throw new Error(errorBody?.detail || 'Failed to delete resume');
  }
  invalidateResumesCache(userId);
  return response.json();
};

export const clearData = async () => {
  const token = localStorage.getItem('access_token');
  const userId = getUserIdFromToken(token);
  const response = await fetch(`${API_BASE_URL}/clear_data?user_id=${userId}`, {
    method: 'DELETE'
  });
  if (!response.ok) {
    let errorBody = null;
    try {
      errorBody = await response.json();
    } catch {
      errorBody = { detail: 'Failed to clear data' };
    }
    throw new Error(errorBody?.detail || 'Failed to clear data');
  }
  invalidateAllAppCaches();
  return response.json();
};
export const searchResumes = async (query, k, isJDsearch, chatGroupId = null) => {
  const token = localStorage.getItem('access_token');
  const userId = getUserIdFromToken(token);

  // DEBUG: Check token expiration
  if (!token) {
    console.error('[AUTH] No token found in localStorage');
    throw new Error('Not authenticated');
  }
  
  if (isTokenExpired(token)) {
    console.error('[AUTH] Token has expired! Need to login again.');
    localStorage.removeItem('access_token');
    throw new Error('Session expired. Please login again.');
  }

  console.log(JSON.stringify({ "user_id": userId, "user_query": query, "k": k, "chat_group_id": chatGroupId }))
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ "user_id": userId, "user_query": query, "k": k, "chat_group_id": chatGroupId }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    console.error('[API] Chat request failed:', response.status, errorData);
    throw new Error(errorData.detail || 'Failed to search resumes');
  }

  const payload = await response.json();
  invalidateChatCache(userId);
  return payload;
};

export const fetchChatGroups = async () => {
  const token = localStorage.getItem('access_token');
  const userId = getUserIdFromToken(token);
  
  // DEBUG: Check token expiration
  if (!token) {
    console.error('[AUTH] No token found in localStorage');
    throw new Error('Not authenticated');
  }
  
  if (isTokenExpired(token)) {
    console.error('[AUTH] Token has expired! Need to login again.');
    localStorage.removeItem('access_token');
    throw new Error('Session expired. Please login again.');
  }
  
  console.log('[AUTH] Token is valid, fetching chat groups for user:', userId);
  
  const key = cacheKey('chatGroups', userId);
  const cached = readCache(key);
  if (cached) {
    console.log('[CACHE] Chat groups found in cache');
    return cached;
  }

  const response = await fetch(`${API_BASE_URL}/chat/groups/${userId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    console.error('[API] Failed to fetch chat groups:', response.status, errorData);
    throw new Error(errorData.detail || 'Failed to fetch chat groups');
  }

  const payload = await response.json();
  writeCache(key, payload, CACHE_TTLS.chatGroups);
  return payload;
};

export const deleteChatGroup = async (chatGroupId) => {
  const token = localStorage.getItem('access_token');
  const userId = getUserIdFromToken(token);

  const response = await fetch(`${API_BASE_URL}/chat/groups/${userId}/${encodeURIComponent(chatGroupId)}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to delete chat group');
  }

  invalidateChatCache(userId);
  return response.json();
};

export const downloadResumes = async (files) => {
  const token = localStorage.getItem('access_token');
  const userId = getUserIdFromToken(token);
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

export const fetchChatHistory = async (chatGroupId = null, limit = 5, offset = 0) => {
  const token = localStorage.getItem('access_token');
  const userId = getUserIdFromToken(token);
  
  // DEBUG: Check token expiration
  if (!token) {
    console.error('[AUTH] No token found in localStorage');
    throw new Error('Not authenticated');
  }
  
  if (isTokenExpired(token)) {
    console.error('[AUTH] Token has expired! Need to login again.');
    localStorage.removeItem('access_token');
    throw new Error('Session expired. Please login again.');
  }
  
  const chatQuery = chatGroupId ? `&chat_group_id=${encodeURIComponent(chatGroupId)}` : '';
  const key = cacheKey('chatHistory', userId, chatGroupId || 'default', String(limit), String(offset));
  const cached = readCache(key);
  if (cached) {
    console.log('[CACHE] Chat history found in cache');
    return cached;
  }
  
  const response = await fetch(
    `${API_BASE_URL}/chat/history/${userId}?limit=${limit}&offset=${offset}${chatQuery}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    }
  );
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    console.error('[API] Failed to fetch chat history:', response.status, errorData);
    throw new Error(errorData.detail || 'Failed to fetch chat history');
  }
  
  const payload = await response.json();
  writeCache(key, payload, CACHE_TTLS.chatHistory);
  return payload;
};

export const logoutUser = async () => {
  // Clear the access token from localStorage
  localStorage.removeItem('access_token');
  invalidateAllAppCaches();
  // You can add a backend logout endpoint here if needed for token blacklisting
  return { message: 'Logged out successfully' };
};
