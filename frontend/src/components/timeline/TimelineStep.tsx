'use client'

import { CheckCircle, Clock, Loader2, XCircle, Circle } from 'lucide-react'

interface TimelineStepProps {
  label: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  message?: string
  isLast?: boolean
}

export function TimelineStep({ label, status, message, isLast = false }: TimelineStepProps) {
  const statusIcons = {
    pending: <Circle className="w-5 h-5 text-gray-500" />,
    in_progress: <Loader2 className="w-5 h-5 text-yellow-400 animate-spin" />,
    completed: <CheckCircle className="w-5 h-5 text-green-400" />,
    failed: <XCircle className="w-5 h-5 text-red-400" />,
  }

  const statusColors = {
    pending: 'border-gray-700',
    in_progress: 'border-yellow-400',
    completed: 'border-green-400',
    failed: 'border-red-400',
  }

  return (
    <div className="relative">
      {!isLast && (
        <div className="absolute left-5 top-10 bottom-0 w-0.5 bg-gray-700" />
      )}
      <div className="flex items-start gap-4">
        <div className={lex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border-2  bg-white/5}>
          {statusIcons[status]}
        </div>
        <div className="flex-1 pb-6">
          <div className="flex items-center gap-3">
            <span className={ont-medium }>
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
