import axios from 'axios';

const API_BASE_URL = '/api';

export interface ChatRequest {
  message: string;
  history?: ChatHistoryMessage[];
}

export interface ChatResponse {
  answer: string;
}

export interface ChatHistoryMessage {
  role: 'user' | 'assistant';
  content: string;
}

export const chatAPI = {
  sendMessage: async (
    message: string,
    history: ChatHistoryMessage[] = []
  ): Promise<string> => {
    const response = await axios.post<ChatResponse>(
      `${API_BASE_URL}/chat`,
      { message, history }
    );
    return response.data.answer;
  },
};
