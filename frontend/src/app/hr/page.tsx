'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
    ArrowLeft, Users, CheckCircle, XCircle, Clock,
    BarChart3, TrendingUp, AlertTriangle, Eye,
    ThumbsUp, ThumbsDown, Pause, RefreshCw
} from 'lucide-react';

interface DashboardStats {
    total_candidates: number;
    pending_review: number;
    approved: number;
    rejected: number;
    in_progress: number;
}

interface CandidateWithAssessment {
    candidate: {
        id: string;
        name: string;
        email: string;
        job_role: string;
        status: string;
        created_at: string;
    };
    latest_report: {
        id: string;
        overall_score: number;
        technical_score: number;
        behavioral_score: number;
        recommendation: string;
        hr_reviewed: boolean;
        hr_decision: string | null;
    } | null;
    sessions_count: number;
}

export default function HRDashboardPage() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [candidates, setCandidates] = useState<CandidateWithAssessment[]>([]);
    const [selectedCandidate, setSelectedCandidate] = useState<CandidateWithAssessment | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all');

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        setIsLoading(true);
        try {
            // Fetch stats
            const statsRes = await fetch('http://localhost:8000/api/hr/dashboard/stats');
            if (statsRes.ok) {
                const statsData = await statsRes.json();
                setStats(statsData);
            }

            // Fetch candidates
            const candidatesRes = await fetch('http://localhost:8000/api/hr/candidates');
            if (candidatesRes.ok) {
                const candidatesData = await candidatesRes.json();
                setCandidates(candidatesData);
            }
        } catch (err) {
            console.error('Failed to fetch dashboard data:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDecision = async (reportId: string, decision: 'approve' | 'reject' | 'hold') => {
        try {
            const response = await fetch(`http://localhost:8000/api/hr/decision/${reportId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ decision, notes: '' }),
            });

            if (response.ok) {
                fetchDashboardData();
                setSelectedCandidate(null);
            }
        } catch (err) {
            console.error('Failed to submit decision:', err);
        }
    };

    const getStatusColor = (status: string) => {
        const colors: Record<string, string> = {
            pending: 'text-yellow-400 bg-yellow-400/20',
            data_ingestion: 'text-blue-400 bg-blue-400/20',
            profile_analysis: 'text-blue-400 bg-blue-400/20',
            technical_interview: 'text-purple-400 bg-purple-400/20',
            behavioral_interview: 'text-orange-400 bg-orange-400/20',
            evaluation: 'text-cyan-400 bg-cyan-400/20',
            hr_review: 'text-pink-400 bg-pink-400/20',
            completed: 'text-green-400 bg-green-400/20',
        };
        return colors[status] || 'text-gray-400 bg-gray-400/20';
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-green-400';
        if (score >= 60) return 'text-yellow-400';
        return 'text-red-400';
    };

    const filteredCandidates = candidates.filter(c => {
        if (filter === 'all') return true;
        if (filter === 'pending') return c.candidate.status === 'hr_review';
        if (filter === 'approved') return c.latest_report?.hr_decision === 'approve';
        if (filter === 'rejected') return c.latest_report?.hr_decision === 'reject';
        return true;
    });

    return (
        <div className="min-h-screen">
            {/* Header */}
            <header className="glass sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link
                            href="/"
                            className="text-gray-400 hover:text-white transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <div>
                            <h1 className="text-lg font-semibold text-white flex items-center gap-2">
                                <BarChart3 className="w-5 h-5" />
                                HR Dashboard
                            </h1>
                            <p className="text-sm text-gray-400">
                                Candidate Assessment Overview
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={fetchDashboardData}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 text-gray-400 hover:text-white transition-colors"
                    >
                        <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Stats Cards */}
                <div className="grid md:grid-cols-5 gap-4 mb-8">
                    <StatCard
                        icon={<Users className="w-6 h-6" />}
                        label="Total Candidates"
                        value={stats?.total_candidates || 0}
                        color="from-blue-500 to-cyan-500"
                    />
                    <StatCard
                        icon={<Clock className="w-6 h-6" />}
                        label="Pending Review"
                        value={stats?.pending_review || 0}
                        color="from-yellow-500 to-orange-500"
                    />
                    <StatCard
                        icon={<TrendingUp className="w-6 h-6" />}
                        label="In Progress"
                        value={stats?.in_progress || 0}
                        color="from-purple-500 to-pink-500"
                    />
                    <StatCard
                        icon={<CheckCircle className="w-6 h-6" />}
                        label="Approved"
                        value={stats?.approved || 0}
                        color="from-green-500 to-emerald-500"
                    />
                    <StatCard
                        icon={<XCircle className="w-6 h-6" />}
                        label="Rejected"
                        value={stats?.rejected || 0}
                        color="from-red-500 to-rose-500"
                    />
                </div>

                {/* Filters */}
                <div className="flex gap-2 mb-6">
                    {(['all', 'pending', 'approved', 'rejected'] as const).map((f) => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-4 py-2 rounded-lg capitalize transition-colors ${filter === f
                                    ? 'bg-purple-500 text-white'
                                    : 'bg-white/10 text-gray-400 hover:text-white'
                                }`}
                        >
                            {f}
                        </button>
                    ))}
                </div>

                {/* Candidates Table */}
                <div className="glass rounded-2xl overflow-hidden">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-white/10">
                                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Candidate</th>
                                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Role</th>
                                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Status</th>
                                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Score</th>
                                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Decision</th>
                                <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredCandidates.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-12 text-center text-gray-400">
                                        {isLoading ? 'Loading...' : 'No candidates found'}
                                    </td>
                                </tr>
                            ) : (
                                filteredCandidates.map((item) => (
                                    <tr key={item.candidate.id} className="border-b border-white/5 hover:bg-white/5">
                                        <td className="px-6 py-4">
                                            <div>
                                                <p className="text-white font-medium">{item.candidate.name}</p>
                                                <p className="text-sm text-gray-400">{item.candidate.email}</p>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-gray-300">{item.candidate.job_role}</td>
                                        <td className="px-6 py-4">
                                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(item.candidate.status)}`}>
                                                {item.candidate.status.replace('_', ' ')}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            {item.latest_report ? (
                                                <span className={`text-xl font-bold ${getScoreColor(item.latest_report.overall_score)}`}>
                                                    {item.latest_report.overall_score.toFixed(0)}
                                                </span>
                                            ) : (
                                                <span className="text-gray-500">-</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4">
                                            {item.latest_report?.hr_decision ? (
                                                <span className={`px-3 py-1 rounded-full text-xs font-medium ${item.latest_report.hr_decision === 'approve'
                                                        ? 'text-green-400 bg-green-400/20'
                                                        : item.latest_report.hr_decision === 'reject'
                                                            ? 'text-red-400 bg-red-400/20'
                                                            : 'text-yellow-400 bg-yellow-400/20'
                                                    }`}>
                                                    {item.latest_report.hr_decision}
                                                </span>
                                            ) : (
                                                <span className="text-gray-500">Pending</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <button
                                                    onClick={() => setSelectedCandidate(item)}
                                                    className="p-2 rounded-lg bg-white/10 text-gray-400 hover:text-white transition-colors"
                                                    title="View Details"
                                                >
                                                    <Eye className="w-4 h-4" />
                                                </button>
                                                {item.latest_report && !item.latest_report.hr_decision && (
                                                    <>
                                                        <button
                                                            onClick={() => handleDecision(item.latest_report!.id, 'approve')}
                                                            className="p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors"
                                                            title="Approve"
                                                        >
                                                            <ThumbsUp className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            onClick={() => handleDecision(item.latest_report!.id, 'reject')}
                                                            className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                                                            title="Reject"
                                                        >
                                                            <ThumbsDown className="w-4 h-4" />
                                                        </button>
                                                    </>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Detail Modal */}
                {selectedCandidate && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6">
                        <div className="glass rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                            <div className="p-6 border-b border-white/10 flex items-center justify-between">
                                <h2 className="text-xl font-semibold text-white">
                                    {selectedCandidate.candidate.name}
                                </h2>
                                <button
                                    onClick={() => setSelectedCandidate(null)}
                                    className="text-gray-400 hover:text-white"
                                >
                                    ✕
                                </button>
                            </div>
                            <div className="p-6 space-y-6">
                                {/* Basic Info */}
                                <div>
                                    <h3 className="text-sm font-medium text-gray-400 mb-2">Basic Information</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <p className="text-gray-500 text-sm">Email</p>
                                            <p className="text-white">{selectedCandidate.candidate.email}</p>
                                        </div>
                                        <div>
                                            <p className="text-gray-500 text-sm">Role</p>
                                            <p className="text-white">{selectedCandidate.candidate.job_role}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Scores */}
                                {selectedCandidate.latest_report && (
                                    <div>
                                        <h3 className="text-sm font-medium text-gray-400 mb-2">Assessment Scores</h3>
                                        <div className="grid grid-cols-3 gap-4">
                                            <ScoreCard
                                                label="Overall"
                                                score={selectedCandidate.latest_report.overall_score}
                                            />
                                            <ScoreCard
                                                label="Technical"
                                                score={selectedCandidate.latest_report.technical_score}
                                            />
                                            <ScoreCard
                                                label="Behavioral"
                                                score={selectedCandidate.latest_report.behavioral_score}
                                            />
                                        </div>

                                        <div className="mt-4 p-4 rounded-xl bg-white/5">
                                            <p className="text-sm text-gray-400 mb-1">Recommendation</p>
                                            <p className="text-white">{selectedCandidate.latest_report.recommendation}</p>
                                        </div>
                                    </div>
                                )}

                                {/* Actions */}
                                {selectedCandidate.latest_report && !selectedCandidate.latest_report.hr_decision && (
                                    <div className="flex gap-4">
                                        <button
                                            onClick={() => {
                                                handleDecision(selectedCandidate.latest_report!.id, 'approve');
                                            }}
                                            className="flex-1 py-3 rounded-xl bg-green-500 text-white font-medium hover:bg-green-600 transition-colors flex items-center justify-center gap-2"
                                        >
                                            <ThumbsUp className="w-5 h-5" />
                                            Approve
                                        </button>
                                        <button
                                            onClick={() => {
                                                handleDecision(selectedCandidate.latest_report!.id, 'hold');
                                            }}
                                            className="flex-1 py-3 rounded-xl bg-yellow-500 text-white font-medium hover:bg-yellow-600 transition-colors flex items-center justify-center gap-2"
                                        >
                                            <Pause className="w-5 h-5" />
                                            Hold
                                        </button>
                                        <button
                                            onClick={() => {
                                                handleDecision(selectedCandidate.latest_report!.id, 'reject');
                                            }}
                                            className="flex-1 py-3 rounded-xl bg-red-500 text-white font-medium hover:bg-red-600 transition-colors flex items-center justify-center gap-2"
                                        >
                                            <ThumbsDown className="w-5 h-5" />
                                            Reject
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function StatCard({
    icon,
    label,
    value,
    color
}: {
    icon: React.ReactNode;
    label: string;
    value: number;
    color: string;
}) {
    return (
        <div className="glass rounded-xl p-4">
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center mb-3`}>
                {icon}
            </div>
            <p className="text-2xl font-bold text-white">{value}</p>
            <p className="text-sm text-gray-400">{label}</p>
        </div>
    );
}

function ScoreCard({ label, score }: { label: string; score: number }) {
    const getColor = (s: number) => {
        if (s >= 80) return 'from-green-500 to-emerald-500';
        if (s >= 60) return 'from-yellow-500 to-orange-500';
        return 'from-red-500 to-rose-500';
    };

    return (
        <div className="text-center p-4 rounded-xl bg-white/5">
            <div className={`text-3xl font-bold bg-gradient-to-r ${getColor(score)} bg-clip-text text-transparent`}>
                {score.toFixed(0)}
            </div>
            <p className="text-sm text-gray-400">{label}</p>
        </div>
    );
}
