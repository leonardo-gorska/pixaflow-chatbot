import axios from 'axios';

const API_BASE_URL = '/api';

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  answer: string;
}

export const chatAPI = {
  sendMessage: async (message: string): Promise<string> => {
    const response = await axios.post<ChatResponse>(
      `${API_BASE_URL}/chat`,
      { message }
    );
    return response.data.answer;
  },
};
