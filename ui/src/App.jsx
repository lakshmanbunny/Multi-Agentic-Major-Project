import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import ResearchFeed from './ResearchFeed'

const API_BASE = 'http://localhost:8000'

// HITL Approval Modal Component
function ApprovalModal({ isOpen, onApprove, onReject, datasetUrl }) {
    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-xl"></div>
            <div className="relative w-full max-w-[560px]">
                <div className="absolute -inset-1 bg-gradient-to-r from-primary via-accent-cyan to-primary rounded-xl opacity-30 blur-2xl animate-pulse"></div>
                <div className="relative flex flex-col overflow-hidden rounded-xl bg-surface-dark shadow-2xl ring-1 ring-white/10">
                    <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-primary via-accent-cyan to-primary"></div>
                    <div className="relative flex flex-col p-8 z-20">
                        <div className="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-amber-500/10 ring-1 ring-amber-500/30 animate-pulse relative">
                            <span className="material-symbols-outlined text-[48px] text-amber-500">warning</span>
                        </div>
                        <div className="text-center space-y-2 mb-8">
                            <h2 className="text-2xl font-mono font-bold text-white">Human Verification Required</h2>
                            <div className="inline-flex items-center gap-2 rounded-md bg-white/5 px-3 py-1.5 ring-1 ring-white/10">
                                <span className="h-2 w-2 rounded-full bg-accent-cyan animate-pulse"></span>
                                <span className="font-mono text-xs uppercase text-accent-cyan">Agent: Critic Agent</span>
                            </div>
                        </div>
                        <div className="mb-8 text-center">
                            <p className="text-gray-300 text-lg">Please check the <span className="text-accent-cyan font-medium">Browser Window</span>.</p>
                            <p className="text-white font-medium mt-2">Did the dataset load successfully?</p>
                            {datasetUrl && <p className="text-xs text-gray-500 mt-2 font-mono truncate">{datasetUrl}</p>}
                        </div>
                        <div className="flex gap-4 justify-center">
                            <button onClick={onReject} className="flex-1 rounded-lg bg-[#1a1a2e] px-6 py-4 ring-1 ring-[#ff006e]/30 hover:shadow-[0_0_20px_rgba(255,0,110,0.3)] transition-all hover:-translate-y-1">
                                <div className="flex items-center justify-center gap-3">
                                    <span className="material-symbols-outlined text-[#ff006e]">close</span>
                                    <span className="font-bold text-white">Reject</span>
                                </div>
                            </button>
                            <button onClick={onApprove} className="flex-1 rounded-lg bg-[#1a1a2e] px-6 py-4 ring-1 ring-accent-green/30 hover:shadow-[0_0_20px_rgba(0,255,136,0.3)] transition-all hover:-translate-y-1">
                                <div className="flex items-center justify-center gap-3">
                                    <span className="material-symbols-outlined text-accent-green">check</span>
                                    <span className="font-bold text-white">Approve</span>
                                </div>
                            </button>
                        </div>
                        <div className="mt-6 flex justify-between items-center border-t border-white/5 pt-4">
                            <div className="flex items-center gap-2 text-xs text-gray-500 font-mono">
                                <span className="material-symbols-outlined text-[14px]">schedule</span>
                                <span>Awaiting response</span>
                            </div>
                            <div className="text-xs text-gray-600 font-mono">HITL_v2.4.0</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

// Final Satisfaction Modal Component
function FinalSatisfactionModal({ isOpen, onComplete, onRetry, isSubmitting }) {
    const [showFeedback, setShowFeedback] = useState(false)
    const [feedbackText, setFeedbackText] = useState('')

    if (!isOpen) return null

    const handleRetryClick = () => {
        setShowFeedback(true)
    }

    const handleSendFeedback = () => {
        onRetry(feedbackText)
        setShowFeedback(false)
        setFeedbackText('')
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-xl"></div>
            <div className="relative w-full max-w-[560px]">
                <div className="absolute -inset-1 bg-gradient-to-r from-accent-green via-accent-cyan to-accent-green rounded-xl opacity-30 blur-2xl animate-pulse"></div>
                <div className="relative flex flex-col overflow-hidden rounded-xl bg-surface-dark shadow-2xl ring-1 ring-white/10">
                    <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-accent-green via-accent-cyan to-accent-green"></div>
                    <div className="relative flex flex-col p-8 z-20">
                        <div className="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-accent-green/10 ring-1 ring-accent-green/30 animate-pulse relative">
                            <span className="material-symbols-outlined text-[48px] text-accent-green">rocket_launch</span>
                        </div>
                        <div className="text-center space-y-2 mb-8">
                            <h2 className="text-2xl font-mono font-bold text-white">Workflow Complete! 🚀</h2>
                            <div className="inline-flex items-center gap-2 rounded-md bg-white/5 px-3 py-1.5 ring-1 ring-white/10">
                                <span className="h-2 w-2 rounded-full bg-accent-green animate-pulse"></span>
                                <span className="font-mono text-xs uppercase text-accent-green">Execution Finished</span>
                            </div>
                        </div>
                        <div className="mb-8 text-center">
                            <p className="text-gray-300 text-lg">The Browser Agent has finished execution.</p>
                            <p className="text-white font-medium mt-2">Are you satisfied with the generated data and models?</p>
                        </div>

                        {!showFeedback ? (
                            <div className="flex gap-4 justify-center">
                                <button onClick={handleRetryClick} disabled={isSubmitting} className="flex-1 rounded-lg bg-[#1a1a2e] px-6 py-4 ring-1 ring-[#ff006e]/30 hover:shadow-[0_0_20px_rgba(255,0,110,0.3)] transition-all hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed">
                                    <div className="flex items-center justify-center gap-3">
                                        <span className="material-symbols-outlined text-[#ff006e]">refresh</span>
                                        <span className="font-bold text-white">❌ No, Improve</span>
                                    </div>
                                </button>
                                <button onClick={onComplete} disabled={isSubmitting} className="flex-1 rounded-lg bg-[#1a1a2e] px-6 py-4 ring-1 ring-accent-green/30 hover:shadow-[0_0_20px_rgba(0,255,136,0.3)] transition-all hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed">
                                    <div className="flex items-center justify-center gap-3">
                                        <span className="material-symbols-outlined text-accent-green">check_circle</span>
                                        <span className="font-bold text-white">✅ Yes, Complete</span>
                                    </div>
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        What would you like to improve?
                                    </label>
                                    <textarea
                                        value={feedbackText}
                                        onChange={(e) => setFeedbackText(e.target.value)}
                                        placeholder="E.g., 'Use different preprocessing, try Random Forest instead...'"
                                        className="w-full h-32 rounded-lg bg-black/40 border border-white/10 px-4 py-3 text-white placeholder-gray-500 focus:ring-2 focus:ring-accent-cyan focus:border-transparent resize-none"
                                        disabled={isSubmitting}
                                    />
                                </div>
                                <div className="flex gap-4">
                                    <button onClick={() => setShowFeedback(false)} disabled={isSubmitting} className="flex-1 rounded-lg bg-black/40 px-4 py-3 ring-1 ring-white/10 hover:bg-black/60 transition-all disabled:opacity-50">
                                        <span className="text-gray-300">Cancel</span>
                                    </button>
                                    <button onClick={handleSendFeedback} disabled={isSubmitting || !feedbackText.trim()} className="flex-1 rounded-lg bg-[#ff006e] px-4 py-3 hover:bg-[#ff006e]/80 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                                        <div className="flex items-center justify-center gap-2">
                                            {isSubmitting && <span className="material-symbols-outlined animate-spin text-sm">progress_activity</span>}
                                            <span className="font-bold text-white">{isSubmitting ? 'Refining...' : 'Submit & Retry'}</span>
                                        </div>
                                    </button>
                                </div>
                            </div>
                        )}

                        <div className="mt-6 flex justify-between items-center border-t border-white/5 pt-4">
                            <div className="flex items-center gap-2 text-xs text-gray-500 font-mono">
                                <span className="material-symbols-outlined text-[14px]">task_alt</span>
                                <span>Final review</span>
                            </div>
                            <div className="text-xs text-gray-600 font-mono">HITL_v2.4.0</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

// Schema Verification Modal Component - HITL Checkpoint for Schema
function SchemaVerificationModal({ isOpen, onApprove, onReject, schema, isSubmitting }) {
    if (!isOpen) return null

    const hasValidSchema = schema && schema.length > 20 && !schema.includes("not available")

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-xl"></div>
            <div className="relative w-full max-w-[600px]">
                <div className="absolute -inset-1 bg-gradient-to-r from-yellow-500 via-amber-500 to-yellow-500 rounded-xl opacity-30 blur-2xl animate-pulse"></div>
                <div className="relative flex flex-col overflow-hidden rounded-xl bg-surface-dark shadow-2xl ring-1 ring-yellow-500/30">
                    <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-yellow-500 via-amber-500 to-yellow-500"></div>
                    <div className="relative flex flex-col p-8 z-20">
                        <div className="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-yellow-500/10 ring-1 ring-yellow-500/30 animate-pulse relative">
                            <span className="text-[48px]">🧐</span>
                        </div>
                        <div className="text-center space-y-2 mb-6">
                            <h2 className="text-2xl font-mono font-bold text-white">Schema Verification Required</h2>
                            <div className="inline-flex items-center gap-2 rounded-md bg-white/5 px-3 py-1.5 ring-1 ring-yellow-500/30">
                                <span className="h-2 w-2 rounded-full bg-yellow-500 animate-pulse"></span>
                                <span className="font-mono text-xs uppercase text-yellow-500">Checkpoint: Pre-ML</span>
                            </div>
                        </div>

                        <p className="text-gray-300 text-center mb-4">
                            The Data Engineer has extracted the columns below.<br />
                            <span className="text-white font-medium">Verify them before running the ML Agent.</span>
                        </p>

                        {/* Schema Display */}
                        <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-xs overflow-x-auto mb-6 border border-gray-700 max-h-48 overflow-y-auto">
                            <div className="flex justify-between text-gray-500 mb-2 border-b border-gray-700 pb-1">
                                <span className="font-bold text-yellow-500">DETECTED COLUMNS</span>
                                <span className="text-[10px] uppercase tracking-wider">Source: Memory Introspection</span>
                            </div>
                            <div className="whitespace-pre-wrap text-sm">
                                {hasValidSchema ? (
                                    <span className="text-green-400">{schema}</span>
                                ) : (
                                    <span className="text-red-400">⚠️ No schema detected. (This indicates a failure - you should likely Reject)</span>
                                )}
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-4 justify-center">
                            <button
                                onClick={onReject}
                                disabled={isSubmitting}
                                className="flex-1 rounded-lg bg-[#1a1a2e] px-6 py-4 ring-1 ring-[#ff006e]/30 hover:shadow-[0_0_20px_rgba(255,0,110,0.3)] transition-all hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <div className="flex items-center justify-center gap-3">
                                    <span className="material-symbols-outlined text-[#ff006e]">close</span>
                                    <span className="font-bold text-white">❌ Reject & Stop</span>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">Save tokens</p>
                            </button>
                            <button
                                onClick={onApprove}
                                disabled={isSubmitting}
                                className="flex-1 rounded-lg bg-[#1a1a2e] px-6 py-4 ring-1 ring-accent-green/30 hover:shadow-[0_0_20px_rgba(0,255,136,0.3)] transition-all hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <div className="flex items-center justify-center gap-3">
                                    {isSubmitting && <span className="material-symbols-outlined animate-spin text-sm">progress_activity</span>}
                                    <span className="material-symbols-outlined text-accent-green">check</span>
                                    <span className="font-bold text-white">✅ Approve Schema</span>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">Continue to ML</p>
                            </button>
                        </div>

                        <div className="mt-6 flex justify-between items-center border-t border-white/5 pt-4">
                            <div className="flex items-center gap-2 text-xs text-gray-500 font-mono">
                                <span className="material-symbols-outlined text-[14px]">schema</span>
                                <span>Schema Checkpoint</span>
                            </div>
                            <div className="text-xs text-gray-600 font-mono">HITL_v2.4.1</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

function App() {
    const [workflowId, setWorkflowId] = useState(null)
    const [userGoal, setUserGoal] = useState('')
    const [datasetUrl, setDatasetUrl] = useState('')
    const [status, setStatus] = useState(null)
    const [logs, setLogs] = useState([])
    const [isRunning, setIsRunning] = useState(false)
    const [history, setHistory] = useState([])
    const [showApprovalModal, setShowApprovalModal] = useState(false)
    const [showFinalModal, setShowFinalModal] = useState(false)
    const [showSchemaModal, setShowSchemaModal] = useState(false)
    const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false)
    const [activeTab, setActiveTab] = useState('research')  // Research tab active by default
    const [agentSteps, setAgentSteps] = useState([
        { name: 'Research Agent', status: 'pending', description: 'Pending...' },
        { name: 'Critic Agent', status: 'pending', description: 'Pending...' },
        { name: 'Data Engineer', status: 'pending', description: 'Pending...' },
        { name: 'ML Engineer', status: 'pending', description: 'Pending...' },
        { name: 'Browser Agent', status: 'pending', description: 'Pending...' },
    ])
    const logsEndRef = useRef(null)

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [logs])

    // Poll workflow status
    useEffect(() => {
        if (!workflowId || !isRunning) return
        const interval = setInterval(async () => {
            try {
                const res = await axios.get(`${API_BASE}/workflow/${workflowId}/status`)
                setStatus(res.data)

                // Update agent steps based on current step
                updateAgentSteps(res.data.current_step, res.data.status)

                // Debug logging
                console.log('Status response:', res.data.current_step, res.data.status)

                // Show HITL modal when waiting for approval
                if (res.data.status === 'waiting_approval') {
                    console.log('HITL MODAL TRIGGERED!')
                    setShowApprovalModal(true)
                }

                // Show Schema Verification modal
                if (res.data.status === 'waiting_schema_approval') {
                    console.log('SCHEMA VERIFICATION MODAL TRIGGERED!')
                    setShowSchemaModal(true)
                    setIsRunning(false)  // Pause polling while waiting for user
                }

                // Show Final Satisfaction modal
                if (res.data.status === 'waiting_final_approval') {
                    console.log('FINAL APPROVAL MODAL TRIGGERED!')
                    setShowFinalModal(true)
                    setIsRunning(false)  // Stop polling while waiting for user
                }

                // Add log entry
                const timestamp = new Date().toLocaleTimeString()
                setLogs(prev => {
                    const lastLog = prev[prev.length - 1] || ''
                    if (!lastLog.includes(res.data.current_step)) {
                        return [...prev, `[${timestamp}] ${res.data.current_step}: ${res.data.status}`]
                    }
                    return prev
                })

                // Check if completed
                if (res.data.status === 'completed' || res.data.status === 'failed') {
                    setIsRunning(false)
                }
            } catch (error) {
                console.error('Polling error:', error)
            }
        }, 2000)
        return () => clearInterval(interval)
    }, [workflowId, isRunning])

    const updateAgentSteps = (currentStep, workflowStatus) => {
        const stepMap = {
            'research_agent': 0,
            'critic_agent': 1,
            'waiting_human_approval': 1,
            'data_engineering_agent': 2,
            'intermediate_schema_capture': 2,
            'waiting_schema_approval': 2,  // Schema checkpoint after Data Engineer
            'ml_engineering_agent': 3,
            'browser_execution': 4,
            'completed': 5,
        }

        const stepDescriptions = {
            0: { active: 'Searching datasets & methods...', completed: 'Found dataset & research plan' },
            1: { active: 'Validating dataset URL...', waiting: 'Awaiting your approval', completed: 'Dataset validated' },
            2: { active: 'Generating EDA code...', waiting: 'Schema detected - awaiting verification', completed: 'EDA code generated' },
            3: { active: 'Training ML model...', completed: 'Model trained' },
            4: { active: 'Executing in Colab browser...', completed: 'Execution complete' },
        }

        const currentIdx = stepMap[currentStep] ?? -1
        console.log('Timeline update:', currentStep, '-> idx:', currentIdx, 'status:', workflowStatus)

        setAgentSteps(prev => prev.map((step, idx) => {
            let newStatus = step.status
            let description = 'Pending...'

            if (idx < currentIdx) {
                newStatus = 'completed'
                description = stepDescriptions[idx]?.completed || 'Done'
            } else if (idx === currentIdx) {
                if (workflowStatus === 'waiting_approval' || workflowStatus === 'waiting_schema_approval') {
                    newStatus = 'waiting'
                    description = stepDescriptions[idx]?.waiting || 'Waiting...'
                } else {
                    newStatus = 'active'
                    description = stepDescriptions[idx]?.active || 'Processing...'
                }
            } else {
                newStatus = 'pending'
                description = 'Pending...'
            }

            return { ...step, status: newStatus, description }
        }))
    }

    const startWorkflow = async () => {
        if (!userGoal.trim()) return

        // Reset state for new workflow
        setAgentSteps([
            { name: 'Research Agent', status: 'active', description: 'Searching datasets & methods...' },
            { name: 'Critic Agent', status: 'pending', description: 'Pending...' },
            { name: 'Data Engineer', status: 'pending', description: 'Pending...' },
            { name: 'ML Engineer', status: 'pending', description: 'Pending...' },
            { name: 'Browser Agent', status: 'pending', description: 'Pending...' },
        ])
        setIsRunning(true)
        setLogs([])
        setShowApprovalModal(false)
        setShowFinalModal(false)
        setIsSubmittingFeedback(false)

        try {
            const res = await axios.post(`${API_BASE}/workflow/start`, { user_goal: userGoal, dataset_url: datasetUrl || '' })
            setWorkflowId(res.data.workflow_id)
            setLogs([`[${new Date().toLocaleTimeString()}] Workflow started: ${res.data.workflow_id}`])
            setHistory(prev => [{ id: res.data.workflow_id, goal: userGoal, status: 'running', time: 'Just now' }, ...prev])
        } catch (error) {
            setLogs([`[ERROR] ${error.message}`])
            setIsRunning(false)
        }
    }

    // Clear all state - reset everything
    const clearState = async () => {
        try {
            await axios.post(`${API_BASE}/workflow/clear`)
            setWorkflowId(null)
            setUserGoal('')
            setDatasetUrl('')
            setStatus(null)
            setLogs([])
            setIsRunning(false)
            setHistory([])
            setShowApprovalModal(false)
            setShowFinalModal(false)
            setIsSubmittingFeedback(false)
            setAgentSteps([
                { name: 'Research Agent', status: 'pending', description: 'Pending...' },
                { name: 'Critic Agent', status: 'pending', description: 'Pending...' },
                { name: 'Data Engineer', status: 'pending', description: 'Pending...' },
                { name: 'ML Engineer', status: 'pending', description: 'Pending...' },
                { name: 'Browser Agent', status: 'pending', description: 'Pending...' },
            ])
            setLogs([`[${new Date().toLocaleTimeString()}] State cleared`])
        } catch (error) {
            console.error('Clear error:', error)
        }
    }

    // HITL: Approve via API
    const handleApprove = async () => {
        setShowApprovalModal(false)
        try {
            await axios.post(`${API_BASE}/workflow/${workflowId}/approve`)
            setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ✅ Dataset APPROVED - continuing workflow`])
        } catch (error) {
            setLogs(prev => [...prev, `[ERROR] Approval failed: ${error.message}`])
        }
    }

    // HITL: Reject via API
    const handleReject = async () => {
        setShowApprovalModal(false)
        try {
            await axios.post(`${API_BASE}/workflow/${workflowId}/reject`)
            setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ❌ Dataset REJECTED - retrying research`])
        } catch (error) {
            setLogs(prev => [...prev, `[ERROR] Rejection failed: ${error.message}`])
        }
    }

    // SCHEMA CHECKPOINT: Approve Schema -> Continue to ML
    const handleSchemaApprove = async () => {
        setShowSchemaModal(false)
        setIsSubmittingFeedback(true)
        try {
            await axios.post(`${API_BASE}/workflow/${workflowId}/schema/approve`)
            setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ✅ Schema APPROVED - starting ML Engineer`])
            setIsRunning(true)  // Resume polling
        } catch (error) {
            setLogs(prev => [...prev, `[ERROR] Schema approval failed: ${error.message}`])
        } finally {
            setIsSubmittingFeedback(false)
        }
    }

    // SCHEMA CHECKPOINT: Reject Schema -> Abort Workflow
    const handleSchemaReject = async () => {
        if (!confirm("Are you sure? This will abort the workflow to save tokens.")) return
        setShowSchemaModal(false)
        try {
            await axios.post(`${API_BASE}/workflow/${workflowId}/schema/reject`)
            setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ⛔ Workflow ABORTED at Schema Checkpoint`])
            setIsRunning(false)
        } catch (error) {
            setLogs(prev => [...prev, `[ERROR] Schema rejection failed: ${error.message}`])
        }
    }

    // Final Satisfaction: Complete workflow
    const handleFinalComplete = async () => {
        setShowFinalModal(false)
        setIsSubmittingFeedback(true)
        try {
            await axios.post(`${API_BASE}/workflow/${workflowId}/feedback`, {
                satisfied: true,
                feedback: ''
            })
            setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ✅ Workflow COMPLETED - results approved`])
            setIsRunning(false)
        } catch (error) {
            setLogs(prev => [...prev, `[ERROR] Completion failed: ${error.message}`])
        } finally {
            setIsSubmittingFeedback(false)
        }
    }

    // Final Satisfaction: Retry with feedback
    const handleFinalRetry = async (feedbackText) => {
        setShowFinalModal(false)
        setIsSubmittingFeedback(true)
        try {
            await axios.post(`${API_BASE}/workflow/${workflowId}/feedback`, {
                satisfied: false,
                feedback: feedbackText || 'Please refine the results'
            })
            setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] 🔄 Retrying workflow from Data Engineering...`])
            setIsRunning(true)  // Resume polling
        } catch (error) {
            setLogs(prev => [...prev, `[ERROR] Retry failed: ${error.message}`])
        } finally {
            setIsSubmittingFeedback(false)
        }
    }

    return (
        <>
            <div className="h-screen w-full bg-background-dark text-white flex overflow-hidden">

                {/* LEFT SIDEBAR */}
                <aside className="w-64 flex-shrink-0 border-r border-glass-border bg-surface-dark flex flex-col">
                    <div className="p-4 border-b border-glass-border shrink-0 flex justify-between items-center">
                        <div>
                            <h2 className="text-sm uppercase tracking-widest text-gray-400 font-semibold">History</h2>
                            <span className="text-xs text-gray-500">{history.length} Workflows</span>
                        </div>
                        <button
                            onClick={clearState}
                            className="text-xs bg-red-500/10 text-red-400 border border-red-500/30 px-2 py-1 rounded hover:bg-red-500/20 transition-colors"
                        >
                            Clear
                        </button>
                    </div>
                    <div className="flex-1 overflow-y-auto p-3 space-y-3">
                        {history.length === 0 ? (
                            <div className="text-center text-gray-600 text-sm mt-8">No workflows yet</div>
                        ) : history.map((item, idx) => (
                            <div key={idx} className="p-3 rounded-xl bg-background-dark/50 border border-glass-border hover:border-primary/50 cursor-pointer">
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-xs font-mono text-gray-400">#{item.id.slice(0, 8)}</span>
                                    <span className="text-[10px] text-gray-500">{item.time}</span>
                                </div>
                                <h3 className="text-sm text-white line-clamp-2">{item.goal}</h3>
                                <span className="mt-2 inline-block px-2 py-0.5 rounded text-[10px] bg-accent-green/10 text-accent-green">{item.status}</span>
                            </div>
                        ))}
                    </div>
                </aside>

                {/* MAIN CONTENT */}
                <div className="flex-1 flex flex-col h-full relative">

                    {/* NAVBAR */}
                    <header className="h-16 border-b border-glass-border bg-surface-dark flex items-center px-6 shrink-0 z-10">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-background-dark rounded-lg border border-glass-border flex items-center justify-center">
                                <span className="material-symbols-outlined text-accent-cyan text-[20px]">science</span>
                            </div>
                            <h1 className="text-xl font-bold">AUTO-<span className="text-accent-cyan">DATASCIENTIST</span></h1>
                        </div>
                        <div className="ml-auto flex items-center gap-4">
                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent-green/10 border border-accent-green/20">
                                <div className="w-2 h-2 rounded-full bg-accent-green animate-pulse"></div>
                                <span className="text-xs text-accent-green">ONLINE</span>
                            </div>
                            <button onClick={clearState} className="px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 border border-red-500/30 text-xs hover:bg-red-500/20">
                                Reset All
                            </button>
                            <button className="w-9 h-9 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white flex items-center justify-center">
                                <span className="material-symbols-outlined">settings</span>
                            </button>
                        </div>
                    </header>

                    {/* DASHBOARD */}
                    <div className="flex-1 overflow-y-auto p-6">
                        <div className="flex gap-6 h-full">

                            {/* CENTER COLUMN */}
                            <div className="flex-1 flex flex-col gap-4 min-w-0">
                                {/* Workflow Form */}
                                <div className="glass-panel rounded-2xl p-5 relative">
                                    <div className="absolute top-0 left-0 w-1 h-full bg-primary rounded-l-2xl"></div>
                                    <div className="flex justify-between items-center mb-4">
                                        <h2 className="text-lg font-bold flex items-center gap-2">
                                            <span className="material-symbols-outlined text-primary">rocket_launch</span>
                                            Define Mission
                                        </h2>
                                        <span className="text-xs font-mono text-primary bg-primary/10 px-2 py-1 rounded">v2.4.0</span>
                                    </div>
                                    <div className="space-y-3">
                                        <div>
                                            <label className="block text-xs text-gray-400 mb-1.5">USER GOAL</label>
                                            <textarea
                                                className="w-full bg-background-dark border border-glass-border rounded-xl p-3 text-sm text-white placeholder-gray-600 focus:border-accent-cyan focus:outline-none resize-none"
                                                placeholder="e.g., 'Train a model to predict diabetes risk'"
                                                rows="2"
                                                value={userGoal}
                                                onChange={(e) => setUserGoal(e.target.value)}
                                                disabled={isRunning}
                                            />
                                        </div>
                                        <div className="flex gap-3">
                                            <div className="flex-1">
                                                <label className="block text-xs text-gray-400 mb-1.5">DATASET URL</label>
                                                <input
                                                    className="w-full bg-background-dark border border-glass-border rounded-xl py-2.5 px-3 text-sm text-white placeholder-gray-600 focus:border-accent-cyan focus:outline-none font-mono"
                                                    placeholder="Optional"
                                                    value={datasetUrl}
                                                    onChange={(e) => setDatasetUrl(e.target.value)}
                                                    disabled={isRunning}
                                                />
                                            </div>
                                            <button
                                                className="self-end bg-primary hover:bg-primary/90 text-white font-bold py-2.5 px-5 rounded-xl shadow-neon-purple flex items-center gap-2 disabled:opacity-50"
                                                onClick={startWorkflow}
                                                disabled={isRunning || !userGoal.trim()}
                                            >
                                                <span className="material-symbols-outlined text-[18px]">play_arrow</span>
                                                Start
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                {/* Agent Timeline */}
                                <div className="flex-1 flex flex-col min-h-0">
                                    <div className="flex justify-between items-center mb-3">
                                        <h3 className="text-sm font-semibold text-gray-300">Agent Timeline</h3>
                                        {isRunning && <span className="text-xs text-accent-cyan animate-pulse">Processing...</span>}
                                    </div>
                                    <div className="relative flex-1 overflow-y-auto pl-4 pr-2">
                                        <div className="absolute left-[11px] top-2 bottom-2 w-0.5 bg-gray-800"></div>
                                        {agentSteps.map((step, idx) => (
                                            <div key={idx} className={`relative flex items-start gap-3 mb-4 ${step.status === 'pending' ? 'opacity-50' : ''}`}>
                                                <div className={`relative z-10 w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${step.status === 'completed' ? 'bg-background-dark border border-accent-green text-accent-green' :
                                                    step.status === 'active' ? 'bg-primary text-white' :
                                                        step.status === 'waiting' ? 'bg-amber-500 text-white animate-pulse' :
                                                            'bg-background-dark border border-gray-700 text-gray-500'
                                                    }`}>
                                                    {step.status === 'completed' && <span className="material-symbols-outlined text-[12px]">check</span>}
                                                    {step.status === 'active' && <span className="material-symbols-outlined text-[12px] animate-spin">sync</span>}
                                                    {step.status === 'waiting' && <span className="material-symbols-outlined text-[12px]">hourglass_top</span>}
                                                    {step.status === 'pending' && <span className="text-[9px] font-bold">{idx + 1}</span>}
                                                </div>
                                                <div className={`flex-1 rounded-lg p-2.5 ${step.status === 'completed' ? 'bg-surface-dark/30 border border-glass-border' :
                                                    step.status === 'active' ? 'bg-primary/10 border border-primary/50' :
                                                        step.status === 'waiting' ? 'bg-amber-500/10 border border-amber-500/50' :
                                                            'border border-dashed border-glass-border'
                                                    }`}>
                                                    <div className="flex justify-between items-center">
                                                        <h4 className={`text-sm font-bold ${step.status === 'pending' ? 'text-gray-400' : 'text-white'}`}>{step.name}</h4>
                                                        {step.status === 'active' && <span className="text-[10px] text-primary font-bold animate-pulse">Active</span>}
                                                        {step.status === 'waiting' && <span className="text-[10px] text-amber-500 font-bold animate-pulse">Waiting Approval</span>}
                                                        {step.status === 'completed' && <span className="text-[10px] text-accent-green">Completed</span>}
                                                    </div>
                                                    <p className={`text-xs mt-0.5 ${step.status === 'pending' ? 'text-gray-600' : 'text-gray-400'}`}>
                                                        {step.description || 'Pending...'}
                                                    </p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Terminal Logs */}
                                <div className="h-36 bg-black rounded-xl border border-glass-border flex flex-col shrink-0">
                                    <div className="px-3 py-2 bg-[#111] border-b border-[#222] flex justify-between items-center rounded-t-xl">
                                        <div className="flex gap-1.5">
                                            <div className="w-2.5 h-2.5 rounded-full bg-red-500/50"></div>
                                            <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/50"></div>
                                            <div className="w-2.5 h-2.5 rounded-full bg-green-500/50"></div>
                                        </div>
                                        <span className="text-[10px] font-mono text-gray-500">TERMINAL</span>
                                        <button onClick={() => setLogs([])} className="text-gray-600 hover:text-white text-xs">Clear</button>
                                    </div>
                                    <div className="flex-1 p-3 font-mono text-xs overflow-y-auto text-accent-green/90 space-y-0.5">
                                        {logs.length === 0 ? (
                                            <div className="opacity-50">[System] Waiting...</div>
                                        ) : logs.map((log, idx) => (
                                            <div key={idx} className={idx === logs.length - 1 ? 'typing-cursor' : 'opacity-70'}>{log}</div>
                                        ))}
                                        <div ref={logsEndRef} />
                                    </div>
                                </div>
                            </div>

                            {/* RIGHT COLUMN - Tabs */}
                            <div className="w-80 flex flex-col shrink-0">
                                {/* Tab Navigation */}
                                <div className="flex border-b border-glass-border">
                                    <button
                                        onClick={() => setActiveTab('research')}
                                        className={`flex-1 py-3 text-sm font-medium transition-all ${activeTab === 'research'
                                            ? 'text-white border-b-2 border-accent-cyan bg-surface-dark/50'
                                            : 'text-gray-400 hover:text-white'
                                            }`}>
                                        <span className="flex items-center justify-center gap-1">
                                            <span className="material-symbols-outlined text-sm">science</span>
                                            Research
                                        </span>
                                    </button>
                                    <button
                                        onClick={() => setActiveTab('code')}
                                        className={`flex-1 py-3 text-sm font-medium transition-all ${activeTab === 'code'
                                            ? 'text-white border-b-2 border-primary bg-surface-dark/50'
                                            : 'text-gray-400 hover:text-white'
                                            }`}>
                                        Code
                                    </button>
                                    <button
                                        onClick={() => setActiveTab('visuals')}
                                        className={`flex-1 py-3 text-sm font-medium transition-all ${activeTab === 'visuals'
                                            ? 'text-white border-b-2 border-primary bg-surface-dark/50'
                                            : 'text-gray-400 hover:text-white'
                                            }`}>
                                        Visuals
                                    </button>
                                </div>

                                {/* Tab Content */}
                                <div className="flex-1 bg-[#0d0d12] rounded-b-xl overflow-hidden flex flex-col">
                                    {activeTab === 'research' && (
                                        <ResearchFeed data={status?.research_data || {}} />
                                    )}

                                    {activeTab === 'code' && (
                                        <>
                                            <div className="p-3 flex items-center justify-between border-b border-glass-border bg-[#15151e]">
                                                <div className="flex items-center gap-2">
                                                    <span className="material-symbols-outlined text-yellow-400 text-sm">description</span>
                                                    <span className="text-xs font-mono text-gray-300">generated_code.py</span>
                                                </div>
                                                <button className="text-primary text-[10px] font-bold flex items-center gap-1">
                                                    <span className="material-symbols-outlined text-[14px]">content_copy</span>
                                                    COPY
                                                </button>
                                            </div>
                                            <div className="flex-1 overflow-y-auto p-3 font-mono text-xs text-gray-400">
                                                <div className="opacity-50"># Code appears here...</div>
                                            </div>
                                        </>
                                    )}

                                    {activeTab === 'visuals' && (
                                        <div className="flex-1 flex items-center justify-center">
                                            <div className="text-center">
                                                <span className="material-symbols-outlined text-6xl text-gray-700 mb-4">insights</span>
                                                <p className="text-gray-500">Visuals coming soon</p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                        </div>
                    </div>
                </div>
            </div>

            {/* HITL Modal - triggers from backend status */}
            <ApprovalModal
                isOpen={showApprovalModal}
                onApprove={handleApprove}
                onReject={handleReject}
                datasetUrl={datasetUrl}
            />

            {/* Final Satisfaction Modal - triggers after workflow execution */}
            <FinalSatisfactionModal
                isOpen={showFinalModal}
                onComplete={handleFinalComplete}
                onRetry={handleFinalRetry}
                isSubmitting={isSubmittingFeedback}
            />

            {/* Schema Verification Modal - triggers after Data Engineer */}
            <SchemaVerificationModal
                isOpen={showSchemaModal}
                onApprove={handleSchemaApprove}
                onReject={handleSchemaReject}
                schema={status?.schema || ''}
                isSubmitting={isSubmittingFeedback}
            />
        </>
    )
}

export default App
