/**
 * Decode JWT token and extract user_id from the 'sub' claim
 * @param {string} token - The JWT token
 * @returns {string|null} - The user_id if valid, null otherwise
 */
export const getUserIdFromToken = (token) => {
  if (!token) {
    console.warn('No token provided');
    return null;
  }

  try {
    // JWT format: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.warn('Invalid token format');
      return null;
    }

    // Decode the payload (second part)
    // Base64url decode
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
    
    // Extract user_id from 'sub' claim
    if (payload.sub) {
      return payload.sub;
    } else {
      console.warn('Token does not contain user_id in sub claim');
      return null;
    }
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
};

/**
 * Decode JWT token and extract user name from the 'name' claim
 * @param {string} token - The JWT token
 * @returns {string|null} - The user name if present, null otherwise
 */
export const getUserNameFromToken = (token) => {
  if (!token) {
    return null;
  }

  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
    return payload.name || null;
  } catch (error) {
    console.error('Error decoding token for name:', error);
    return null;
  }
};

/**
 * Check if JWT token is expired
 * @param {string} token - The JWT token
 * @returns {boolean} - True if token is expired, false otherwise
 */
export const isTokenExpired = (token) => {
  if (!token) {
    return true;
  }

  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return true;
    }

    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
    
    if (!payload.exp) {
      console.warn('Token does not contain exp claim');
      return true;
    }

    // Convert exp (seconds since epoch) to milliseconds and compare with current time
    const expirationTime = payload.exp * 1000;
    const now = Date.now();
    const isExpired = now > expirationTime;
    
    if (isExpired) {
      console.warn(`Token expired at ${new Date(expirationTime).toISOString()}, current time: ${new Date(now).toISOString()}`);
    }
    
    return isExpired;
  } catch (error) {
    console.error('Error checking token expiration:', error);
    return true;
  }
};
