'use client';

import Link from 'next/link';
import { Users, MessageSquare, Mic, BarChart3, ArrowRight, Sparkles, Shield, Zap } from 'lucide-react';

export default function HomePage() {
    return (
        <div className="min-h-screen">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 glass">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                            <Sparkles className="w-6 h-6 text-white" />
                        </div>
                        <span className="text-xl font-bold text-white">AssessAI</span>
                    </div>
                    <div className="flex items-center space-x-4">
                        <Link
                            href="/hr"
                            className="text-gray-300 hover:text-white transition-colors px-4 py-2"
                        >
                            HR Dashboard
                        </Link>
                        <Link
                            href="/candidate"
                            className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-2 rounded-full font-medium hover:opacity-90 transition-opacity"
                        >
                            Start Assessment
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="pt-32 pb-20 px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
                            AI-Powered
                            <span className="block gradient-text">Candidate Assessment</span>
                        </h1>
                        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
                            Revolutionize your hiring process with our multi-agent AI system.
                            Conduct intelligent interviews through chat or voice with real-time avatar interaction.
                        </p>
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Link
                                href="/candidate"
                                className="group flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-4 rounded-full font-semibold text-lg hover:opacity-90 transition-all transform hover:scale-105"
                            >
                                Begin Assessment
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </Link>
                            <Link
                                href="/hr"
                                className="flex items-center gap-2 glass text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-white/20 transition-all"
                            >
                                <BarChart3 className="w-5 h-5" />
                                HR Dashboard
                            </Link>
                        </div>
                    </div>

                    {/* Feature Cards */}
                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <FeatureCard
                            icon={<Users className="w-8 h-8" />}
                            title="Multi-Agent System"
                            description="5 specialized AI agents work together for comprehensive assessment"
                            gradient="from-blue-500 to-cyan-500"
                        />
                        <FeatureCard
                            icon={<MessageSquare className="w-8 h-8" />}
                            title="Chat Interview"
                            description="Natural language chat-based assessment with context awareness"
                            gradient="from-purple-500 to-pink-500"
                        />
                        <FeatureCard
                            icon={<Mic className="w-8 h-8" />}
                            title="Voice Interview"
                            description="Real-time voice interview with AI avatar interviewer"
                            gradient="from-orange-500 to-red-500"
                        />
                        <FeatureCard
                            icon={<BarChart3 className="w-8 h-8" />}
                            title="HR Dashboard"
                            description="Comprehensive reports with scores, strengths, and recommendations"
                            gradient="from-green-500 to-emerald-500"
                        />
                    </div>
                </div>
            </section>

            {/* Process Section */}
            <section className="py-20 px-6">
                <div className="max-w-7xl mx-auto">
                    <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-12">
                        How It Works
                    </h2>
                    <div className="grid md:grid-cols-3 gap-8">
                        <ProcessStep
                            number="01"
                            title="Submit Profile"
                            description="Upload your resume, LinkedIn, and GitHub profiles for analysis"
                        />
                        <ProcessStep
                            number="02"
                            title="AI Interview"
                            description="Engage with our AI agents in chat or voice-based interviews"
                        />
                        <ProcessStep
                            number="03"
                            title="Get Results"
                            description="Receive comprehensive assessment report reviewed by HR"
                        />
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="py-20 px-6 glass-dark mx-6 rounded-3xl my-12">
                <div className="max-w-7xl mx-auto">
                    <div className="grid md:grid-cols-4 gap-8 text-center">
                        <StatItem value="5" label="AI Agents" />
                        <StatItem value="95%" label="Accuracy" />
                        <StatItem value="<10min" label="Average Time" />
                        <StatItem value="24/7" label="Availability" />
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 px-6">
                <div className="max-w-4xl mx-auto text-center">
                    <div className="glass rounded-3xl p-12">
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                            Ready to Transform Your Hiring?
                        </h2>
                        <p className="text-gray-400 mb-8">
                            Experience the future of candidate assessment with our AI-powered platform.
                        </p>
                        <Link
                            href="/candidate"
                            className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-4 rounded-full font-semibold text-lg hover:opacity-90 transition-all transform hover:scale-105"
                        >
                            Start Free Assessment
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-8 px-6 border-t border-white/10">
                <div className="max-w-7xl mx-auto text-center text-gray-500">
                    <p>© 2024 AI Candidate Assessment Platform. Built for Vision Tact.</p>
                </div>
            </footer>
        </div>
    );
}

function FeatureCard({
    icon,
    title,
    description,
    gradient
}: {
    icon: React.ReactNode;
    title: string;
    description: string;
    gradient: string;
}) {
    return (
        <div className="glass rounded-2xl p-6 hover:bg-white/10 transition-all group cursor-pointer">
            <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                {icon}
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
            <p className="text-gray-400">{description}</p>
        </div>
    );
}

function ProcessStep({
    number,
    title,
    description
}: {
    number: string;
    title: string;
    description: string;
}) {
    return (
        <div className="text-center">
            <div className="text-6xl font-bold gradient-text mb-4">{number}</div>
            <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
            <p className="text-gray-400">{description}</p>
        </div>
    );
}

function StatItem({ value, label }: { value: string; label: string }) {
    return (
        <div>
            <div className="text-4xl font-bold text-white mb-2">{value}</div>
            <div className="text-gray-400">{label}</div>
        </div>
    );
}
