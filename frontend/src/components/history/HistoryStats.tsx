'use client'

interface HistoryStatsProps {
  total: number
  byAction: Record<string, number>
  byStatus: Record<string, number>
}

export function HistoryStats({ total, byAction, byStatus }: HistoryStatsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-white/5 rounded-xl p-4 border border-white/10">
        <p className="text-sm text-gray-400">Total Presentations</p>
        <p className="text-2xl font-bold text-white">{total}</p>
      </div>
      <div className="bg-white/5 rounded-xl p-4 border border-white/10">
        <p className="text-sm text-gray-400">Generated</p>
        <p className="text-2xl font-bold text-white">{byAction?.generated || 0}</p>
      </div>
      <div className="bg-white/5 rounded-xl p-4 border border-white/10">
        <p className="text-sm text-gray-400">Successful</p>
        <p className="text-2xl font-bold text-white">{byStatus?.success || 0}</p>
      </div>
      <div className="bg-white/5 rounded-xl p-4 border border-white/10">
        <p className="text-sm text-gray-400">Total Assets</p>
        <p className="text-2xl font-bold text-white">0</p>
      </div>
    </div>
  )
}
