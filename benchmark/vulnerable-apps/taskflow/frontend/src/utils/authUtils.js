export const saveSession = (token, user, refreshToken) => {
  localStorage.setItem('tf_token', token);
  localStorage.setItem('tf_refresh', refreshToken);
  localStorage.setItem('tf_user', JSON.stringify(user));
};

export const clearSession = () => {
  localStorage.removeItem('tf_token');
  localStorage.removeItem('tf_refresh');
  localStorage.removeItem('tf_user');
};

export const getToken = () => localStorage.getItem('tf_token');
export const getRefreshToken = () => localStorage.getItem('tf_refresh');

export const getStoredUser = () => {
  try {
    const raw = localStorage.getItem('tf_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};
