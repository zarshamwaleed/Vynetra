'use client'

import { useState, useEffect } from 'react'
import { Layout } from '@/components/ui/Layout'
import { Calendar, FileText, Clock, Download, Trash2, Search } from 'lucide-react'

interface Presentation {
  id: number
  title: string
  prompt: string
  status: string
  slide_count: number
  created_at: string
  updated_at: string
  latest_action: string
  latest_status: string
  asset_count: number
}

export default function HistoryPage() {
  const [presentations, setPresentations] = useState<Presentation[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({ total: 0, by_action: {}, by_status: {} })
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')

  useEffect(() => {
    fetchPresentations()
    fetchStats()
  }, [])

  const fetchPresentations = async () => {
    try {
      const response = await fetch('/api/v1/history/presentations')
      const data = await response.json()
      setPresentations(data)
    } catch (error) {
      console.error('Failed to fetch presentations:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/v1/history/stats')
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this presentation?')) return
    
    try {
      await fetch(/api/v1/presentations/, { method: 'DELETE' })
      await fetchPresentations()
    } catch (error) {
      console.error('Failed to delete:', error)
    }
  }

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const filteredPresentations = presentations.filter(p => {
    const matchesSearch = p.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         p.prompt.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' || p.status === filterStatus
    return matchesSearch && matchesStatus
  })

  if (loading) {
    return (
      <Layout>
        <div className="max-w-6xl mx-auto text-center py-12">
          <div className="animate-pulse">
            <div className="h-8 w-48 bg-white/10 rounded mx-auto mb-4"></div>
            <div className="h-4 w-64 bg-white/10 rounded mx-auto"></div>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Presentation History</h1>
          <p className="text-gray-400">View and manage all your generated presentations</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white/5 rounded-xl p-4 border border-white/10">
            <p className="text-sm text-gray-400">Total</p>
            <p className="text-2xl font-bold text-white">{stats.total || 0}</p>
          </div>
          <div className="bg-white/5 rounded-xl p-4 border border-white/10">
            <p className="text-sm text-gray-400">Generated</p>
            <p className="text-2xl font-bold text-white">{stats.by_action?.generated || 0}</p>
          </div>
          <div className="bg-white/5 rounded-xl p-4 border border-white/10">
            <p className="text-sm text-gray-400">Successful</p>
            <p className="text-2xl font-bold text-white">{stats.by_status?.success || 0}</p>
          </div>
          <div className="bg-white/5 rounded-xl p-4 border border-white/10">
            <p className="text-sm text-gray-400">Assets</p>
            <p className="text-2xl font-bold text-white">
              {presentations.reduce((acc, p) => acc + p.asset_count, 0)}
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-6">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search presentations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
          <button
            onClick={fetchPresentations}
            className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            Refresh
          </button>
        </div>

        {/* List */}
        {filteredPresentations.length === 0 ? (
          <div className="text-center py-12 bg-white/5 rounded-xl border border-white/10">
            <FileText className="w-12 h-12 text-gray-500 mx-auto mb-4" />
            <h3 className="text-white font-medium mb-2">No Presentations Found</h3>
            <p className="text-gray-400 text-sm">
              {searchTerm ? 'Try adjusting your search' : 'Generate your first presentation from the home page'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredPresentations.map((presentation) => (
              <div
                key={presentation.id}
                className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10 hover:border-purple-500/30 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-white font-semibold text-lg">{presentation.title}</h3>
                      <span className={px-2 py-0.5 rounded-full text-xs font-medium }>
                        {presentation.status}
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm mb-2 line-clamp-2">{presentation.prompt}</p>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400">
                      <span className="flex items-center gap-1">
                        <FileText className="w-4 h-4" />
                        {presentation.slide_count} slides
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {formatDate(presentation.created_at)}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {presentation.latest_action}
                      </span>
                      <span className="text-xs text-gray-500">
                        {presentation.asset_count} assets
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col gap-2 ml-4">
                    <button
                      onClick={() => window.location.href = /generate?job=}
                      className="flex items-center gap-2 px-4 py-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors text-sm"
                    >
                      <Download className="w-4 h-4" />
                      View
                    </button>
                    <button
                      onClick={() => handleDelete(presentation.id)}
                      className="flex items-center gap-2 px-4 py-2 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20 transition-colors text-sm"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}
