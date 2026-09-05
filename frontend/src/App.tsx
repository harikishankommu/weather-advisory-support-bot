import React, { useRef, useEffect } from 'react';
import { useChat } from './hooks/useChat';
import { Header } from './components/Header';
import { WelcomeScreen } from './components/WelcomeScreen';
import { ChatMessage } from './components/ChatMessage';
import { LoadingIndicator } from './components/LoadingIndicator';
import { ChatInput } from './components/ChatInput';
import { ConnectionError } from './components/ConnectionError';

export default function App() {
  const {
    sessionId,
    messages,
    isLoading,
    loadingStage,
    connectionError,
    apiUrl,
    isBackendHealthy,
    sendMessage,
    clearChat,
    retryLastMessage,
    updateApiUrl,
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll when messages change or loading state changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, connectionError]);

  return (
    <div className="flex flex-col h-screen w-full bg-slate-100 text-slate-900 antialiased overflow-hidden dark:bg-slate-950 dark:text-slate-100">
      {/* Top Header */}
      <Header
        sessionId={sessionId}
        isBackendHealthy={isBackendHealthy}
        apiUrl={apiUrl}
        onClearChat={clearChat}
        onUpdateApiUrl={updateApiUrl}
      />

      {/* Main Chat Scroll Container */}
      <main
        id="chat-messages-container"
        className="flex-1 overflow-y-auto px-3 sm:px-6 py-4 sm:py-6"
      >
        <div className="max-w-4xl mx-auto flex flex-col min-h-full">
          {messages.length === 0 ? (
            <div className="my-auto">
              <WelcomeScreen onSelectPrompt={sendMessage} />
            </div>
          ) : (
            <div className="flex-1 space-y-1">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
            </div>
          )}

          {/* Loading Indicator */}
          {isLoading && <LoadingIndicator stageText={loadingStage} />}

          {/* Connection Error Banner */}
          {connectionError && (
            <ConnectionError
              apiUrl={apiUrl}
              onRetry={retryLastMessage}
              onUpdateApiUrl={updateApiUrl}
            />
          )}

          <div ref={messagesEndRef} className="h-2" />
        </div>
      </main>

      {/* Bottom Fixed Chat Input */}
      <footer className="shrink-0">
        <ChatInput
          onSendMessage={sendMessage}
          isLoading={isLoading}
        />
      </footer>
    </div>
  );
}
