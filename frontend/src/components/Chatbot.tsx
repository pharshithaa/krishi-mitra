import React, { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useTranslation } from 'react-i18next';
import { Bot, User, Loader2, AlertCircle } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  timestamp?: string;
}

interface SourceInfo {
  source: string;
  page?: number;
  chunk_id: string;
  score: number;
}

interface RAGResponse {
  answer: string;
  sources: SourceInfo[];
  retrieved_chunks: string[];
  latency_ms: number;
  node_latencies?: {
    embed_ms: number;
    retrieve_ms: number;
    generate_ms: number;
  };
}

interface ChatbotProps {
  lang: string;
}

const Chatbot: React.FC<ChatbotProps> = ({ lang }) => {
  const { t } = useTranslation();
  const { toast } = useToast();
  const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI agricultural assistant. Ask me anything about farming, crops, fertilizers, pest management, or agricultural best practices.',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  // Fallback responses when RAG system has no indexed content
  const generateFallbackResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('wheat')) {
      return `Wheat is best grown during the Rabi season (October-March) in India. Key points:\n\n• **Sowing**: October-December\n• **Temperature**: 15-25°C optimal\n• **Rainfall**: 300-400mm required\n• **Soil**: Well-drained loamy soil, pH 6.0-7.5\n• **Harvest**: March-April\n\nWheat requires cool, dry weather during grain filling. Avoid excessive moisture during maturity to prevent fungal diseases.`;
    }
    
    if (lowerQuery.includes('rice')) {
      return `Rice is primarily grown during Kharif season (June-November). Details:\n\n• **Sowing**: June-July\n• **Temperature**: 20-35°C\n• **Rainfall**: 1000-2000mm\n• **Soil**: Clayey, waterlogged conditions\n• **Harvest**: October-November\n\nRice requires high humidity and standing water. Transplanting is done 20-25 days after sowing.`;
    }
    
    if (lowerQuery.includes('fertilizer')) {
      return `General fertilizer recommendations:\n\n• **NPK ratio**: Varies by crop and soil test\n• **Timing**: Split application for better efficiency\n• **Organic**: Compost, FYM improve soil health\n• **Micronutrients**: Zinc, iron often deficient\n\nAlways conduct soil testing before fertilizer application for best results.`;
    }
    
    if (lowerQuery.includes('pest') || lowerQuery.includes('disease')) {
      return `Integrated Pest Management (IPM) approach:\n\n• **Prevention**: Crop rotation, resistant varieties\n• **Monitoring**: Regular field inspection\n• **Biological**: Beneficial insects, biopesticides\n• **Chemical**: Last resort, follow label instructions\n• **Cultural**: Proper spacing, sanitation\n\nEarly detection and prevention are key to effective pest management.`;
    }
    
    // General agricultural guidance
    return `I'd be happy to help with your agricultural question! Here are some general principles:\n\n• **Soil health**: Regular testing and organic matter addition\n• **Water management**: Efficient irrigation and drainage\n• **Crop selection**: Choose varieties suited to your climate\n• **Timing**: Follow local agricultural calendars\n• **Integrated approach**: Combine traditional and modern practices\n\nFor specific guidance, please consult your local agricultural extension officer or provide more details about your farming context.`;
  };

  // Convert markdown formatting to JSX
  const renderMessageContent = (content: string) => {
    // First handle bold text (**text**)
    let processedContent = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Then handle bullet points (* item)
    processedContent = processedContent.replace(/^\s*\*\s+/gm, '• ');
    
    // Split by HTML tags and convert to JSX
    const parts = processedContent.split(/(<strong>.*?<\/strong>)/g);
    
    return parts.map((part, index) => {
      if (part.startsWith('<strong>') && part.endsWith('</strong>')) {
        // Extract text between <strong> tags
        const boldText = part.replace(/<\/?strong>/g, '');
        return <strong key={index} className="font-semibold text-gray-900">{boldText}</strong>;
      }
      return part;
    });
  };

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE}/api/v1/rag/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          query: userMessage.content,
          top_k: 5,
          filters: null
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: RAGResponse = await response.json();
      
      // Handle case where no chunks were retrieved
      let responseContent = data.answer;
      let responseSources = data.sources.map(s => s.source);
      
      if (!data.answer || data.retrieved_chunks.length === 0) {
        responseContent = generateFallbackResponse(userMessage.content);
        responseSources = ["General Agricultural Knowledge"];
      }
      
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: responseContent,
        sources: responseSources,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      toast({
        title: "Response Generated",
        description: data.retrieved_chunks.length > 0 
          ? `Retrieved ${data.retrieved_chunks.length} sources in ${data.latency_ms}ms`
          : "Got your agricultural guidance!",
      });

    } catch (err: any) {
      console.error('Chat error:', err);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `I apologize, but I encountered an error while processing your question. Please try again or contact support if the issue persists. Error: ${err.message}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
      
      toast({
        title: "Error",
        description: "Failed to get response from AI assistant",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="h-[70vh] flex flex-col">
      <CardHeader>
        <CardTitle>{t('chat.title')}</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto space-y-4" ref={containerRef}>
        {messages.map((message, idx) => (
          <div key={idx} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {message.role === 'assistant' && (
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-green-600" />
              </div>
            )}
            <div className={`max-w-[80%] ${message.role === 'user' ? 'order-first' : ''}`}>
              <div className={`px-4 py-3 rounded-lg ${
                message.role === 'user' 
                  ? 'bg-blue-500 text-white ml-auto' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                <div className="text-sm leading-relaxed whitespace-pre-wrap">
                  {renderMessageContent(message.content)}
                </div>
              </div>
              {message.timestamp && (
                <p className="text-xs text-gray-500 mt-1 px-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              )}
            </div>
            {message.role === 'user' && (
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-blue-600" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-green-600" />
            </div>
            <div className="bg-gray-100 text-gray-800 px-4 py-3 rounded-lg">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter className="border-t">
        <form onSubmit={sendMessage} className="w-full flex items-center gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about crops, fertilizers, pest management, weather..."
            disabled={loading}
            className="flex-1"
          />
          <Button type="submit" disabled={loading || !input.trim()}>
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              'Send'
            )}
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
};

export default Chatbot;
