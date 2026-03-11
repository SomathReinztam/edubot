import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const loginUser = async (email, password) => {
  const response = await axios.post(`${API_URL}/users/login`, { email, password });
  return response.data;
};

export const registerUser = async (name, email, password) => {
  const response = await axios.post(`${API_URL}/users/`, { name, email, password });
  return response.data;
};
