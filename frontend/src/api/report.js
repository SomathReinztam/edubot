import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const generateReport = async (query, token) => {
  const response = await axios.post(
    `${API_URL}/analysis/stream/`,
    { query_text: query },
    {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      // Note: For actual streaming, you might need to use a different approach
      // like EventSource or a custom fetch implementation to handle chunks.
      // This example assumes the API returns the full report and reasonings
      // at once or that you will process the stream in the component.
    }
  );
  return response.data;
};
