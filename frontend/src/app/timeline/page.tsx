'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, RefreshCw } from 'lucide-react'

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  )
}

function TimelineStep({ label, status, message, isLast }: { 
  label: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  message?: string
  isLast?: boolean
}) {
  const statusIcons = {
    pending: '⏸',
    in_progress: '⏳',
    completed: '✅',
    failed: '❌',
  }

  const statusColors = {
    pending: 'text-gray-400',
    in_progress: 'text-yellow-400',
    completed: 'text-green-400',
    failed: 'text-red-400',
  }

  return (
    <div className="relative">
      {!isLast && (
        <div className="absolute left-5 top-10 bottom-0 w-0.5 bg-gray-700" />
      )}
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border-2 border-gray-700 bg-white/5">
          <span className={statusColors[status]}>
            {statusIcons[status]}
          </span>
        </div>
        <div className="flex-1 pb-6">
          <div className="flex items-center gap-3">
            <span className={`font-medium ${statusColors[status]}`}>
              {label}
            </span>
            <span className="text-xs text-gray-500">
              {status === 'completed' ? '✓ Done' :
               status === 'in_progress' ? '⏳ In Progress' :
               status === 'failed' ? '✗ Failed' :
               '⏸ Pending'}
            </span>
          </div>
          {message && (
            <p className="text-sm text-gray-500 mt-1">{message}</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default function TimelinePage() {
  const searchParams = useSearchParams()
  const jobId = searchParams.get('job')
  const [timeline, setTimeline] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!jobId) {
      setError('No job ID provided')
      setLoading(false)
      return
    }

    const fetchTimeline = async () => {
      try {
        const response = await fetch(`/api/v1/timeline/${jobId}`)
        if (!response.ok) {
          if (response.status === 404) {
            setError('Job not found')
          }
          throw new Error('Failed to fetch timeline')
        }
        const data = await response.json()
        setTimeline(data)
        setLoading(false)
      } catch (err) {
        console.error('Error fetching timeline:', err)
        setLoading(false)
      }
    }

    fetchTimeline()
    const interval = setInterval(fetchTimeline, 2000)
    return () => clearInterval(interval)
  }, [jobId])

  if (loading) {
    return (
      <Layout>
        <div className="max-w-3xl mx-auto text-center py-12">
          <div className="animate-pulse">
            <div className="h-8 w-48 bg-white/10 rounded mx-auto mb-4"></div>
            <div className="h-4 w-64 bg-white/10 rounded mx-auto"></div>
          </div>
        </div>
      </Layout>
    )
  }

  if (error || !timeline) {
    return (
      <Layout>
        <div className="max-w-3xl mx-auto text-center py-12">
          <div className="bg-white/5 rounded-xl p-8 border border-red-500/20">
            <p className="text-red-400 mb-4">{error || 'Timeline not found'}</p>
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Go Back Home
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  const steps = ['planning', 'research', 'slides', 'diagrams', 'ppt', 'pdf', 'complete']
  const stepLabels: Record<string, string> = {
    planning: 'Planning',
    research: 'Research',
    slides: 'Content Generation',
    diagrams: 'Diagram Generation',
    ppt: 'PowerPoint Building',
    pdf: 'PDF Export',
    complete: 'Complete!',
  }

  return (
    <Layout>
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Link>
            <h1 className="text-2xl font-bold text-white">Generation Timeline</h1>
            <p className="text-gray-400 text-sm mt-1 truncate max-w-md">
              {timeline.prompt}
            </p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="flex items-center gap-2 px-4 py-2 bg-white/5 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        <div className="bg-white/5 rounded-xl p-6 border border-white/10 mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Progress</span>
            <span className="text-sm font-medium text-white">{timeline.progress}%</span>
          </div>
          <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500 rounded-full"
              style={{ width: `${timeline.progress}%` }}
            />
          </div>
          <div className="flex items-center gap-2 mt-2">
            <span className={`text-xs px-2 py-0.5 rounded-full ${
              timeline.status === 'completed' ? 'bg-green-500/20 text-green-400' :
              timeline.status === 'failed' ? 'bg-red-500/20 text-red-400' :
              'bg-yellow-500/20 text-yellow-400'
            }`}>
              {timeline.status}
            </span>
            <span className="text-xs text-gray-500">
              Job ID: {timeline.job_id.substring(0, 8)}...
            </span>
          </div>
        </div>

        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          {steps.map((stepKey, index) => {
            const step = timeline.steps[stepKey]
            return (
              <TimelineStep
                key={stepKey}
                label={stepLabels[stepKey] || stepKey}
                status={step.status as any}
                message={step.message}
                isLast={index === steps.length - 1}
              />
            )
          })}
        </div>

        {timeline.status === 'completed' && (
          <div className="mt-6 p-4 bg-green-500/10 border border-green-500/20 rounded-lg text-center">
            <p className="text-green-400 font-medium">🎉 Presentation Generation Complete!</p>
            <p className="text-gray-400 text-sm mt-1">Your presentation is ready for download.</p>
          </div>
        )}

        {timeline.status === 'failed' && (
          <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-center">
            <p className="text-red-400 font-medium">❌ Generation Failed</p>
            <p className="text-gray-400 text-sm mt-1">Please try again or check the logs.</p>
          </div>
        )}
      </div>
    </Layout>
  )
}