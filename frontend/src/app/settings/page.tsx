'use client'

import { useState, useEffect } from 'react'
import { Layout } from '@/components/ui/Layout'
import { Save, RefreshCw, Sun, Moon, Monitor, Sparkles } from 'lucide-react'

interface SettingsData {
  llm_provider: string
  llm_model: Record<string, string>
  theme: string
  slide_count: number
  audience: string
  tone: string
  animation_quality: string
  auto_save: boolean
  show_timeline: boolean
  enable_animations: boolean
  enable_diagrams: boolean
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [providers, setProviders] = useState([])

  useEffect(() => {
    fetchSettings()
    fetchProviders()
  }, [])

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/v1/settings/')
      const data = await response.json()
      setSettings(data)
    } catch (error) {
      console.error('Failed to fetch settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchProviders = async () => {
    try {
      const response = await fetch('/api/v1/settings/available/providers')
      const data = await response.json()
      setProviders(data.providers)
    } catch (error) {
      console.error('Failed to fetch providers:', error)
    }
  }

  const handleSave = async () => {
    if (!settings) return
    setSaving(true)
    setMessage('')

    try {
      const response = await fetch('/api/v1/settings/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      })
      const data = await response.json()
      if (data.status === 'success') {
        setMessage('✅ Settings saved successfully!')
        setSettings(data.settings)
      }
    } catch (error) {
      console.error('Failed to save settings:', error)
      setMessage('❌ Failed to save settings')
    } finally {
      setSaving(false)
      setTimeout(() => setMessage(''), 3000)
    }
  }

  const handleReset = async () => {
    if (!confirm('Are you sure you want to reset all settings to defaults?')) return

    try {
      const response = await fetch('/api/v1/settings/reset', {
        method: 'POST'
      })
      const data = await response.json()
      if (data.status === 'success') {
        setSettings(data.settings)
        setMessage('✅ Settings reset to defaults!')
      }
    } catch (error) {
      console.error('Failed to reset settings:', error)
    }
  }

  const updateSetting = (key: string, value: any) => {
    if (settings) {
      setSettings({ ...settings, [key]: value })
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto text-center py-12">
          <div className="animate-pulse">
            <div className="h-8 w-48 bg-white/10 rounded mx-auto mb-4"></div>
            <div className="h-4 w-64 bg-white/10 rounded mx-auto"></div>
          </div>
        </div>
      </Layout>
    )
  }

  if (!settings) return null

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">Configure your presentation generation preferences</p>
        </div>

        <div className="space-y-6">
          {/* LLM Provider */}
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
            <h3 className="text-white font-semibold mb-4">LLM Provider</h3>
            <div className="flex flex-wrap gap-3">
              {providers.map((provider: any) => (
                <button
                  key={provider.name}
                  onClick={() => updateSetting('llm_provider', provider.name)}
                  className={
                    px-4 py-2 rounded-lg capitalize transition-all text-sm
                    
                  }
                >
                  {provider.label}
                </button>
              ))}
            </div>
            <div className="mt-3 text-sm text-gray-500">
              {providers.find(p => p.name === settings.llm_provider)?.description}
            </div>
          </div>

          {/* Theme */}
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
            <h3 className="text-white font-semibold mb-4">Theme</h3>
            <div className="flex flex-wrap gap-3">
              {[
                { value: 'dark', icon: Moon, label: 'Dark' },
                { value: 'light', icon: Sun, label: 'Light' },
                { value: 'system', icon: Monitor, label: 'System' },
              ].map(({ value, icon: Icon, label }) => (
                <button
                  key={value}
                  onClick={() => updateSetting('theme', value)}
                  className={
                    flex items-center gap-2 px-4 py-2 rounded-lg transition-all
                    
                  }
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Slide Count */}
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
            <h3 className="text-white font-semibold mb-4">Default Slide Count</h3>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="5"
                max="20"
                value={settings.slide_count}
                onChange={(e) => updateSetting('slide_count', parseInt(e.target.value))}
                className="flex-1 h-2 bg-white/20 rounded-lg appearance-none cursor-pointer accent-purple-500"
              />
              <span className="text-white font-medium w-12 text-center">
                {settings.slide_count}
              </span>
            </div>
          </div>

          {/* Audience and Tone */}
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
            <h3 className="text-white font-semibold mb-4">Presentation Style</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-400 block mb-2">Audience</label>
                <select
                  value={settings.audience}
                  onChange={(e) => updateSetting('audience', e.target.value)}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="general">General</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="expert">Expert</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-gray-400 block mb-2">Tone</label>
                <select
                  value={settings.tone}
                  onChange={(e) => updateSetting('tone', e.target.value)}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="professional">Professional</option>
                  <option value="educational">Educational</option>
                  <option value="casual">Casual</option>
                  <option value="persuasive">Persuasive</option>
                </select>
              </div>
            </div>
          </div>

          {/* Animation Quality */}
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
            <h3 className="text-white font-semibold mb-4">Animation Quality</h3>
            <div className="flex flex-wrap gap-3">
              {['low', 'medium', 'high', 'ultra'].map((quality) => (
                <button
                  key={quality}
                  onClick={() => updateSetting('animation_quality', quality)}
                  className={
                    px-4 py-2 rounded-lg capitalize transition-all
                    
                  }
                >
                  {quality}
                </button>
              ))}
            </div>
          </div>

          {/* Features Toggles */}
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
            <h3 className="text-white font-semibold mb-4">Features</h3>
            <div className="space-y-3">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.enable_animations}
                  onChange={(e) => updateSetting('enable_animations', e.target.checked)}
                  className="w-4 h-4 accent-purple-500"
                />
                <span className="text-gray-300">Enable Animations</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.enable_diagrams}
                  onChange={(e) => updateSetting('enable_diagrams', e.target.checked)}
                  className="w-4 h-4 accent-purple-500"
                />
                <span className="text-gray-300">Enable Diagrams</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.show_timeline}
                  onChange={(e) => updateSetting('show_timeline', e.target.checked)}
                  className="w-4 h-4 accent-purple-500"
                />
                <span className="text-gray-300">Show Generation Timeline</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.auto_save}
                  onChange={(e) => updateSetting('auto_save', e.target.checked)}
                  className="w-4 h-4 accent-purple-500"
                />
                <span className="text-gray-300">Auto-save Presentations</span>
              </label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-white/10">
            <div>
              {message && (
                <span className={	ext-sm }>
                  {message}
                </span>
              )}
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-white/10 text-gray-400 rounded-lg hover:bg-white/20 transition-colors"
              >
                Reset Defaults
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {saving ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                Save Settings
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
