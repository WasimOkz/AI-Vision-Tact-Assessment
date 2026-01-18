'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
    ArrowLeft, Upload, Linkedin, Github, FileText,
    Loader2, CheckCircle, AlertCircle, User, Mail, Briefcase
} from 'lucide-react';

export default function CandidatePage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [candidateId, setCandidateId] = useState<string | null>(null);

    const [formData, setFormData] = useState({
        name: '',
        email: '',
        jobRole: 'Software Engineer',
        linkedinUrl: '',
        githubUrl: '',
    });
    const [resumeFile, setResumeFile] = useState<File | null>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData(prev => ({
            ...prev,
            [e.target.name]: e.target.value
        }));
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setResumeFile(e.target.files[0]);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            const formDataToSend = new FormData();
            formDataToSend.append('name', formData.name);
            formDataToSend.append('email', formData.email);
            formDataToSend.append('job_role', formData.jobRole);

            if (formData.linkedinUrl) {
                formDataToSend.append('linkedin_url', formData.linkedinUrl);
            }
            if (formData.githubUrl) {
                formDataToSend.append('github_url', formData.githubUrl);
            }
            if (resumeFile) {
                formDataToSend.append('resume', resumeFile);
            }

            const response = await fetch('http://localhost:8000/api/candidates/', {
                method: 'POST',
                body: formDataToSend,
            });

            if (!response.ok) {
                throw new Error('Failed to submit candidate data');
            }

            const data = await response.json();
            setCandidateId(data.id);
            setSuccess(true);

            // Wait a moment then redirect to chat
            setTimeout(() => {
                router.push(`/chat?candidateId=${data.id}`);
            }, 2000);

        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen py-20 px-6">
            <div className="max-w-2xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <Link
                        href="/"
                        className="inline-flex items-center text-gray-400 hover:text-white transition-colors mb-4"
                    >
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back to Home
                    </Link>
                    <h1 className="text-3xl font-bold text-white">Start Your Assessment</h1>
                    <p className="text-gray-400 mt-2">
                        Fill in your details and upload your profile information to begin the AI-powered assessment.
                    </p>
                </div>

                {/* Success Message */}
                {success && (
                    <div className="mb-6 p-4 rounded-xl bg-green-500/20 border border-green-500/50 flex items-center gap-3">
                        <CheckCircle className="w-6 h-6 text-green-400" />
                        <div>
                            <p className="text-green-400 font-medium">Profile submitted successfully!</p>
                            <p className="text-green-400/70 text-sm">Redirecting to assessment...</p>
                        </div>
                    </div>
                )}

                {/* Error Message */}
                {error && (
                    <div className="mb-6 p-4 rounded-xl bg-red-500/20 border border-red-500/50 flex items-center gap-3">
                        <AlertCircle className="w-6 h-6 text-red-400" />
                        <p className="text-red-400">{error}</p>
                    </div>
                )}

                {/* Form */}
                <form onSubmit={handleSubmit} className="glass rounded-2xl p-8 space-y-6">
                    {/* Basic Info */}
                    <div className="space-y-4">
                        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                            <User className="w-5 h-5" />
                            Basic Information
                        </h2>

                        <div className="grid md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm text-gray-400 mb-2">Full Name *</label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleInputChange}
                                    required
                                    className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                                    placeholder="John Doe"
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-gray-400 mb-2">Email *</label>
                                <div className="relative">
                                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                    <input
                                        type="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleInputChange}
                                        required
                                        className="w-full pl-12 pr-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                                        placeholder="john@example.com"
                                    />
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Job Role</label>
                            <div className="relative">
                                <Briefcase className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                <select
                                    name="jobRole"
                                    value={formData.jobRole}
                                    onChange={handleInputChange}
                                    className="w-full pl-12 pr-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white focus:outline-none focus:border-purple-500 transition-colors appearance-none cursor-pointer"
                                >
                                    <option value="Software Engineer">Software Engineer</option>
                                    <option value="Senior Software Engineer">Senior Software Engineer</option>
                                    <option value="Frontend Developer">Frontend Developer</option>
                                    <option value="Backend Developer">Backend Developer</option>
                                    <option value="Full Stack Developer">Full Stack Developer</option>
                                    <option value="AI/ML Engineer">AI/ML Engineer</option>
                                    <option value="DevOps Engineer">DevOps Engineer</option>
                                    <option value="Data Scientist">Data Scientist</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Social Profiles */}
                    <div className="space-y-4 pt-4 border-t border-white/10">
                        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                            <Linkedin className="w-5 h-5" />
                            Social Profiles
                        </h2>

                        <div>
                            <label className="block text-sm text-gray-400 mb-2">LinkedIn Profile URL</label>
                            <div className="relative">
                                <Linkedin className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                <input
                                    type="url"
                                    name="linkedinUrl"
                                    value={formData.linkedinUrl}
                                    onChange={handleInputChange}
                                    className="w-full pl-12 pr-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                                    placeholder="https://linkedin.com/in/johndoe"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm text-gray-400 mb-2">GitHub Profile URL</label>
                            <div className="relative">
                                <Github className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                <input
                                    type="url"
                                    name="githubUrl"
                                    value={formData.githubUrl}
                                    onChange={handleInputChange}
                                    className="w-full pl-12 pr-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                                    placeholder="https://github.com/johndoe"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Resume Upload */}
                    <div className="space-y-4 pt-4 border-t border-white/10">
                        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                            <FileText className="w-5 h-5" />
                            Resume Upload
                        </h2>

                        <div className="relative">
                            <input
                                type="file"
                                id="resume"
                                accept=".pdf"
                                onChange={handleFileChange}
                                className="hidden"
                            />
                            <label
                                htmlFor="resume"
                                className="flex flex-col items-center justify-center w-full h-40 rounded-xl border-2 border-dashed border-white/20 hover:border-purple-500/50 transition-colors cursor-pointer bg-white/5 hover:bg-white/10"
                            >
                                {resumeFile ? (
                                    <div className="flex items-center gap-3 text-green-400">
                                        <CheckCircle className="w-8 h-8" />
                                        <div>
                                            <p className="font-medium">{resumeFile.name}</p>
                                            <p className="text-sm text-gray-400">Click to change file</p>
                                        </div>
                                    </div>
                                ) : (
                                    <>
                                        <Upload className="w-10 h-10 text-gray-500 mb-3" />
                                        <p className="text-gray-400">Drop your resume here or click to browse</p>
                                        <p className="text-sm text-gray-500 mt-1">PDF format, max 10MB</p>
                                    </>
                                )}
                            </label>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <div className="pt-4">
                        <button
                            type="submit"
                            disabled={isLoading || success}
                            className="w-full py-4 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold text-lg hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Processing...
                                </>
                            ) : success ? (
                                <>
                                    <CheckCircle className="w-5 h-5" />
                                    Submitted!
                                </>
                            ) : (
                                'Start Assessment'
                            )}
                        </button>
                    </div>

                    {/* Assessment Options */}
                    {success && candidateId && (
                        <div className="pt-4 grid md:grid-cols-2 gap-4">
                            <Link
                                href={`/chat?candidateId=${candidateId}`}
                                className="p-4 rounded-xl bg-blue-500/20 border border-blue-500/50 text-center hover:bg-blue-500/30 transition-colors"
                            >
                                <p className="text-blue-400 font-medium">Chat Interview</p>
                                <p className="text-sm text-gray-400">Text-based assessment</p>
                            </Link>
                            <Link
                                href={`/voice?candidateId=${candidateId}`}
                                className="p-4 rounded-xl bg-purple-500/20 border border-purple-500/50 text-center hover:bg-purple-500/30 transition-colors"
                            >
                                <p className="text-purple-400 font-medium">Voice Interview</p>
                                <p className="text-sm text-gray-400">With AI avatar</p>
                            </Link>
                        </div>
                    )}
                </form>
            </div>
        </div>
    );
}
