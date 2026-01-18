'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
    ArrowLeft, Mic, MicOff, PhoneOff, MessageSquare,
    Volume2, VolumeX, Loader2, Bot
} from 'lucide-react';

type AvatarState = 'idle' | 'listening' | 'thinking' | 'speaking';

interface TranscriptItem {
    id: string;
    role: 'user' | 'assistant';
    text: string;
    timestamp: Date;
}

export default function VoicePage() {
    const searchParams = useSearchParams();
    const candidateId = searchParams.get('candidateId');

    const [isConnected, setIsConnected] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [isMuted, setIsMuted] = useState(false);
    const [avatarState, setAvatarState] = useState<AvatarState>('idle');
    const [transcript, setTranscript] = useState<TranscriptItem[]>([]);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [currentText, setCurrentText] = useState('');
    const [isComplete, setIsComplete] = useState(false);

    const wsRef = useRef<WebSocket | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    // Start session
    const startSession = useCallback(async () => {
        if (!candidateId) return;

        try {
            // First start an assessment session
            const assessmentRes = await fetch('http://localhost:8000/api/assessment/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    candidate_id: candidateId,
                    interview_type: 'voice'
                }),
            });

            if (!assessmentRes.ok) throw new Error('Failed to start assessment');
            const assessmentData = await assessmentRes.json();
            setSessionId(assessmentData.id);

            // Connect WebSocket
            connectWebSocket(assessmentData.id);

        } catch (err) {
            console.error('Failed to start session:', err);
        }
    }, [candidateId]);

    const connectWebSocket = (sid: string) => {
        const ws = new WebSocket(`ws://localhost:8000/ws/voice/${sid}`);

        ws.onopen = () => {
            setIsConnected(true);
            console.log('Voice WebSocket connected');
        };

        ws.onmessage = async (event) => {
            const data = JSON.parse(event.data);

            switch (data.type) {
                case 'ready':
                    setCurrentText(data.message);
                    setAvatarState('speaking');
                    setTranscript(prev => [...prev, {
                        id: Date.now().toString(),
                        role: 'assistant',
                        text: data.message,
                        timestamp: new Date()
                    }]);
                    // Play audio if available
                    if (data.audio_base64) {
                        playAudio(data.audio_base64);
                    } else {
                        // Use browser TTS
                        speakText(data.message);
                    }
                    break;

                case 'status':
                    setAvatarState(data.avatar_state as AvatarState);
                    if (data.message) setCurrentText(data.message);
                    break;

                case 'transcription':
                    setTranscript(prev => [...prev, {
                        id: Date.now().toString(),
                        role: 'user',
                        text: data.text,
                        timestamp: new Date()
                    }]);
                    break;

                case 'response':
                    setCurrentText(data.text);
                    setAvatarState('speaking');
                    setTranscript(prev => [...prev, {
                        id: Date.now().toString(),
                        role: 'assistant',
                        text: data.text,
                        timestamp: new Date()
                    }]);
                    if (data.audio_base64) {
                        playAudio(data.audio_base64);
                    } else {
                        speakText(data.text);
                    }
                    if (data.is_complete) {
                        setIsComplete(true);
                    }
                    break;

                case 'error':
                    console.error('Voice error:', data.message);
                    setAvatarState('idle');
                    break;
            }
        };

        ws.onclose = () => {
            setIsConnected(false);
            console.log('Voice WebSocket disconnected');
        };

        wsRef.current = ws;
    };

    useEffect(() => {
        startSession();
        return () => {
            if (wsRef.current) wsRef.current.close();
            if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
        };
    }, [startSession]);

    // Audio playback
    const playAudio = (base64Audio: string) => {
        try {
            const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);
            audioRef.current = audio;
            audio.onended = () => setAvatarState('idle');
            if (!isMuted) audio.play();
        } catch (err) {
            console.error('Audio playback error:', err);
            setAvatarState('idle');
        }
    };

    // Browser TTS fallback
    const speakText = (text: string) => {
        if ('speechSynthesis' in window && !isMuted) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.onend = () => setAvatarState('idle');
            speechSynthesis.speak(utterance);
        } else {
            setTimeout(() => setAvatarState('idle'), 3000);
        }
    };

    // Start recording
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                const base64Audio = await blobToBase64(audioBlob);

                // Send to server
                if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                    wsRef.current.send(JSON.stringify({
                        type: 'audio',
                        audio_base64: base64Audio,
                        format: 'webm'
                    }));
                }

                // Stop tracks
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
            setAvatarState('listening');

        } catch (err) {
            console.error('Microphone error:', err);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const blobToBase64 = (blob: Blob): Promise<string> => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64 = (reader.result as string).split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    };

    const endSession = () => {
        if (wsRef.current) {
            wsRef.current.send(JSON.stringify({ type: 'end' }));
            wsRef.current.close();
        }
    };

    const getAvatarAnimation = () => {
        switch (avatarState) {
            case 'listening':
                return 'scale-110 ring-4 ring-blue-500/50';
            case 'thinking':
                return 'animate-pulse';
            case 'speaking':
                return 'avatar-pulse';
            default:
                return '';
        }
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
                                <Mic className="w-5 h-5" />
                                Voice Interview
                            </h1>
                            <p className="text-sm text-gray-400">
                                {isConnected ? (
                                    <span className="flex items-center gap-1">
                                        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                                        Connected - {avatarState}
                                    </span>
                                ) : (
                                    'Connecting...'
                                )}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <Link
                            href={`/chat?candidateId=${candidateId}`}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors"
                        >
                            <MessageSquare className="w-4 h-4" />
                            Chat Mode
                        </Link>
                        <button
                            onClick={() => setIsMuted(!isMuted)}
                            className={`p-2 rounded-lg transition-colors ${isMuted ? 'bg-red-500/20 text-red-400' : 'bg-white/10 text-gray-400'
                                }`}
                        >
                            {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
                        </button>
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

            {/* Main Content */}
            <div className="flex-1 flex flex-col items-center justify-center px-6 py-8">
                {/* Avatar */}
                <div className={`relative w-48 h-48 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-8 transition-all duration-300 ${getAvatarAnimation()}`}>
                    <Bot className="w-24 h-24 text-white" />

                    {/* Status indicator */}
                    <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full glass text-sm text-white capitalize">
                        {avatarState}
                    </div>
                </div>

                {/* Current Text */}
                <div className="max-w-2xl text-center mb-8">
                    <p className="text-xl text-white">
                        {currentText || 'Click the microphone button to start speaking'}
                    </p>
                </div>

                {/* Microphone Button */}
                <button
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={!isConnected || avatarState === 'speaking' || avatarState === 'thinking' || isComplete}
                    className={`w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 ${isRecording
                            ? 'bg-red-500 hover:bg-red-600 scale-110'
                            : 'bg-gradient-to-br from-purple-500 to-pink-500 hover:scale-105'
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                    {isRecording ? (
                        <MicOff className="w-10 h-10 text-white" />
                    ) : (
                        <Mic className="w-10 h-10 text-white" />
                    )}
                </button>
                <p className="text-gray-400 mt-4">
                    {isRecording ? 'Click to stop recording' : 'Click to speak'}
                </p>

                {/* Transcript */}
                <div className="w-full max-w-2xl mt-12">
                    <h3 className="text-sm font-medium text-gray-400 mb-4">Transcript</h3>
                    <div className="glass rounded-2xl p-4 max-h-64 overflow-y-auto space-y-3">
                        {transcript.length === 0 ? (
                            <p className="text-gray-500 text-center py-4">
                                Your conversation will appear here
                            </p>
                        ) : (
                            transcript.map((item) => (
                                <div
                                    key={item.id}
                                    className={`flex ${item.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div className={`max-w-[80%] px-4 py-2 rounded-xl ${item.role === 'user'
                                            ? 'bg-purple-500/30 text-purple-200'
                                            : 'bg-white/10 text-gray-300'
                                        }`}>
                                        <p className="text-sm">{item.text}</p>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Complete Message */}
                {isComplete && (
                    <div className="mt-8 text-center glass rounded-2xl px-8 py-6">
                        <p className="text-green-400 font-semibold mb-2">Interview Complete!</p>
                        <p className="text-gray-400 text-sm mb-4">
                            Thank you for completing the voice interview.
                        </p>
                        <Link
                            href="/hr"
                            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium"
                        >
                            View Results
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
}
