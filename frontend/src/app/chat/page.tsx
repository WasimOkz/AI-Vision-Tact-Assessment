'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
    ArrowLeft, Send, Loader2, Bot, User,
    MessageSquare, Mic, StopCircle, PhoneOff
} from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    agent?: string;
    timestamp: Date;
}

export default function ChatPage() {
    const searchParams = useSearchParams();
    const candidateId = searchParams.get('candidateId');

    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isConnected, setIsConnected] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [currentAgent, setCurrentAgent] = useState('profile_analyzer');
    const [isComplete, setIsComplete] = useState(false);

    const wsRef = useRef<WebSocket | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Start assessment session
    const startSession = useCallback(async () => {
        if (!candidateId) return;

        try {
            const response = await fetch('http://localhost:8000/api/assessment/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    candidate_id: candidateId,
                    interview_type: 'chat'
                }),
            });

            if (!response.ok) throw new Error('Failed to start session');

            const data = await response.json();
            setSessionId(data.id);

            // Add initial message
            if (data.messages && data.messages.length > 0) {
                const initialMsg = data.messages[0];
                setMessages([{
                    id: initialMsg.id || Date.now().toString(),
                    role: 'assistant',
                    content: initialMsg.content,
                    agent: initialMsg.agent_name || 'profile_analyzer',
                    timestamp: new Date()
                }]);
            }

            // Connect WebSocket
            connectWebSocket(data.id);

        } catch (err) {
            console.error('Failed to start session:', err);
        }
    }, [candidateId]);

    const connectWebSocket = (sid: string) => {
        const ws = new WebSocket(`ws://localhost:8000/ws/chat/${sid}`);

        ws.onopen = () => {
            setIsConnected(true);
            console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'typing') {
                setIsTyping(true);
                setCurrentAgent(data.agent || 'assistant');
            } else if (data.type === 'response') {
                setIsTyping(false);
                setMessages(prev => [...prev, {
                    id: Date.now().toString(),
                    role: 'assistant',
                    content: data.content,
                    agent: data.agent,
                    timestamp: new Date()
                }]);
                setCurrentAgent(data.agent || 'assistant');
                if (data.is_complete) {
                    setIsComplete(true);
                    // Auto-save the session to generate report
                    fetch(`http://localhost:8000/api/assessment/session/${sid}/end`, {
                        method: 'POST'
                    }).catch(err => console.error('Failed to auto-save session:', err));
                }
            } else if (data.type === 'ready') {
                console.log('Chat ready:', data.message);
            }
        };

        ws.onclose = () => {
            setIsConnected(false);
            console.log('WebSocket disconnected');
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        wsRef.current = ws;
    };

    useEffect(() => {
        startSession();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [startSession]);

    const sendMessage = () => {
        if (!inputValue.trim() || !wsRef.current || !isConnected) return;

        // Add user message to UI
        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: inputValue,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, userMessage]);

        // Send via WebSocket
        wsRef.current.send(JSON.stringify({
            type: 'message',
            content: inputValue
        }));

        setInputValue('');
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const endSession = async () => {
        if (wsRef.current) {
            wsRef.current.send(JSON.stringify({ type: 'end' }));
            wsRef.current.close();
        }

        if (sessionId) {
            await fetch(`http://localhost:8000/api/assessment/session/${sessionId}/end`, {
                method: 'POST'
            });
        }
    };

    const getAgentDisplayName = (agent: string) => {
        const names: Record<string, string> = {
            'profile_analyzer': 'Profile Analyzer',
            'technical_interviewer': 'Technical Interviewer',
            'behavioral_interviewer': 'Behavioral Interviewer',
            'evaluation': 'Evaluation Agent',
            'hr_handoff': 'HR Agent'
        };
        return names[agent] || 'AI Assistant';
    };

    const getAgentColor = (agent: string) => {
        const colors: Record<string, string> = {
            'profile_analyzer': 'from-blue-500 to-cyan-500',
            'technical_interviewer': 'from-purple-500 to-pink-500',
            'behavioral_interviewer': 'from-orange-500 to-amber-500',
            'evaluation': 'from-green-500 to-emerald-500',
            'hr_handoff': 'from-red-500 to-rose-500'
        };
        return colors[agent] || 'from-gray-500 to-gray-600';
    };

    return (
        <div className="min-h-screen flex flex-col">
            {/* Header */}
            <header className="glass sticky top-0 z-50">
                <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link
                            href="/candidate"
                            className="text-gray-400 hover:text-white transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <div>
                            <h1 className="text-lg font-semibold text-white flex items-center gap-2">
                                <MessageSquare className="w-5 h-5" />
                                Chat Assessment
                            </h1>
                            <p className="text-sm text-gray-400">
                                {isConnected ? (
                                    <span className="flex items-center gap-1">
                                        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                                        Connected - {getAgentDisplayName(currentAgent)}
                                    </span>
                                ) : (
                                    'Connecting...'
                                )}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <Link
                            href={`/voice?candidateId=${candidateId}`}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 transition-colors"
                        >
                            <Mic className="w-4 h-4" />
                            Voice Mode
                        </Link>
                        <button
                            onClick={endSession}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                        >
                            <PhoneOff className="w-4 h-4" />
                            End
                        </button>
                    </div>
                </div>
            </header>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-8">
                <div className="max-w-4xl mx-auto space-y-6">
                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`flex items-start gap-4 ${message.role === 'user' ? 'flex-row-reverse' : ''
                                }`}
                        >
                            {/* Avatar */}
                            <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ${message.role === 'user'
                                ? 'bg-gradient-to-br from-gray-600 to-gray-700'
                                : `bg-gradient-to-br ${getAgentColor(message.agent || '')}`
                                }`}>
                                {message.role === 'user' ? (
                                    <User className="w-5 h-5 text-white" />
                                ) : (
                                    <Bot className="w-5 h-5 text-white" />
                                )}
                            </div>

                            {/* Message Content */}
                            <div className={`flex-1 max-w-[80%] ${message.role === 'user' ? 'text-right' : ''}`}>
                                {message.role === 'assistant' && (
                                    <p className="text-xs text-gray-500 mb-1">
                                        {getAgentDisplayName(message.agent || '')}
                                    </p>
                                )}
                                <div className={`inline-block rounded-2xl px-5 py-3 ${message.role === 'user'
                                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                                    : 'glass text-gray-200'
                                    }`}>
                                    <p className="whitespace-pre-wrap">{message.content}</p>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                    {message.timestamp.toLocaleTimeString()}
                                </p>
                            </div>
                        </div>
                    ))}

                    {/* Typing Indicator */}
                    {isTyping && (
                        <div className="flex items-start gap-4">
                            <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center bg-gradient-to-br ${getAgentColor(currentAgent)}`}>
                                <Bot className="w-5 h-5 text-white" />
                            </div>
                            <div className="glass rounded-2xl px-5 py-3">
                                <div className="flex items-center gap-2">
                                    <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                                    <span className="text-gray-400">
                                        {getAgentDisplayName(currentAgent)} is thinking...
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Complete Message */}
                    {isComplete && (
                        <div className="text-center py-8">
                            <div className="inline-block glass rounded-2xl px-8 py-6">
                                <p className="text-green-400 font-semibold mb-2">Assessment Complete!</p>
                                <p className="text-gray-400 text-sm mb-4">
                                    Thank you for completing the interview. Your results are being processed.
                                </p>
                                <Link
                                    href="/hr"
                                    className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium"
                                >
                                    View Results
                                </Link>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            <div className="glass border-t border-white/10">
                <div className="max-w-4xl mx-auto px-6 py-4">
                    <div className="flex items-center gap-4">
                        <input
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyPress={handleKeyPress}
                            disabled={!isConnected || isTyping || isComplete}
                            placeholder={
                                isComplete
                                    ? 'Assessment complete'
                                    : isTyping
                                        ? 'Please wait...'
                                        : 'Type your response...'
                            }
                            className="flex-1 px-6 py-4 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors disabled:opacity-50"
                        />
                        <button
                            onClick={sendMessage}
                            disabled={!inputValue.trim() || !isConnected || isTyping || isComplete}
                            className="p-4 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
