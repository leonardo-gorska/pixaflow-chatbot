import { useEffect, useRef, useState } from 'react';
import { ChatHistoryMessage, chatAPI } from '../api';
import './Chat.css';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
}

const Chat = () => {
  const nextMessageId = useRef(1);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      text: 'Olá! Sou o assistente virtual do mercado. Como posso ajudar você hoje?',
      isUser: false,
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const createMessage = (text: string, isUser: boolean): Message => {
    const message = {
      id: nextMessageId.current,
      text,
      isUser,
    };
    nextMessageId.current += 1;
    return message;
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const focusInput = () => {
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const messageText = input.trim();
    if (!messageText || isLoading) return;

    const history: ChatHistoryMessage[] = messages
      .slice(-8)
      .map((message) => ({
        role: message.isUser ? 'user' : 'assistant',
        content: message.text,
      }));

    setMessages((prev) => [...prev, createMessage(messageText, true)]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(messageText, history);
      setMessages((prev) => [...prev, createMessage(response, false)]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        createMessage('Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.', false),
      ]);
    } finally {
      setIsLoading(false);
      focusInput();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.altKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>Mercado Virtual</h1>
        <p>Assistente de Atendimento</p>
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.isUser ? 'user' : 'bot'}`}
          >
            {!message.isUser && <span className="message-avatar">🛒</span>}
            <div className="message-content">{message.text}</div>
            {message.isUser && <span className="message-avatar">👤</span>}
          </div>
        ))}
        {isLoading && (
          <div className="message bot">
            <span className="message-avatar">🛒</span>
            <div className="message-content typing">Digitando...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Digite sua mensagem..."
          disabled={isLoading}
          rows={1}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          {isLoading ? '...' : 'Enviar'}
        </button>
      </form>
    </div>
  );
};

export default Chat;
