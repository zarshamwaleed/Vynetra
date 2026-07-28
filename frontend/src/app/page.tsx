'use client'

import { useState, useEffect } from 'react'

export default function HomePage() {
  const [prompt, setPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('')
  const [steps, setSteps] = useState([])
  const [completed, setCompleted] = useState(false)
  const [slides, setSlides] = useState([])
  const [diagrams, setDiagrams] = useState([])
  const [animation, setAnimation] = useState(null)
  const [downloadReady, setDownloadReady] = useState(false)
  const [error, setError] = useState(null)

  const handleGenerate = async () => {
    if (!prompt.trim()) return

    setIsLoading(true)
    setJobId(null)
    setProgress(0)
    setStatus('Starting generation...')
    setSteps([])
    setCompleted(false)
    setDownloadReady(false)
    setError(null)
    setSlides([])
    setDiagrams([])
    setAnimation(null)

    try {
      const response = await fetch('/api/v1/presentations/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt,
          slide_count: 10,
        }),
      })
      const data = await response.json()

      if (data.job_id) {
        setJobId(data.job_id)
        setStatus('Generating presentation...')
        pollStatus(data.job_id)
      } else {
        setStatus('Failed to start generation')
        setError('Could not start generation. Please try again.')
        setIsLoading(false)
      }
    } catch (error) {
      console.error('Generation failed:', error)
      setStatus('Error: ' + error)
      setError('Network error. Please check if backend is running.')
      setIsLoading(false)
    }
  }

  const pollStatus = async (id) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch('/api/v1/timeline/' + id)
        if (!response.ok) {
          if (response.status === 404) {
            clearInterval(interval)
            return
          }
          throw new Error('Failed to fetch status')
        }
        const data = await response.json()

        setProgress(data.progress || 0)

        if (data.steps) {
          const stepNames = ['planning', 'research', 'slides', 'diagrams', 'animation', 'ppt', 'pdf', 'complete']
          const stepLabels = {
            planning: 'Planning',
            research: 'Research',
            slides: 'Content',
            diagrams: 'Diagrams',
            animation: 'Animation',
            ppt: 'PowerPoint',
            pdf: 'PDF Export',
            complete: 'Complete!',
          }

          const activeSteps = stepNames
            .filter((key) => data.steps[key]?.status === 'completed' || data.steps[key]?.status === 'in_progress')
            .map((key) => stepLabels[key] || key)

          setSteps(activeSteps)

          if (data.steps.complete?.status === 'completed') {
            setCompleted(true)
            setStatus('Presentation Complete!')
            setDownloadReady(true)
            clearInterval(interval)
            setIsLoading(false)
            
            // Fetch content with diagrams and animation
            fetchContent(id)
          }
        }
      } catch (error) {
        console.error('Status check failed:', error)
      }
    }, 1500)
  }

  const fetchContent = async (id) => {
    try {
      const response = await fetch('/api/v1/presentations/' + id + '/content')
      if (response.ok) {
        const data = await response.json()
        setSlides(data.slides || [])
        setDiagrams(data.diagrams || [])
        setAnimation(data.animation || null)
      }
    } catch (error) {
      console.error('Failed to fetch content:', error)
    }
  }

  const handleDownload = async (fileType) => {
    if (!jobId) return

    try {
      const response = await fetch('/api/v1/presentations/' + jobId + '/download/' + fileType)
      if (!response.ok) {
        throw new Error('Download failed')
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = fileType === 'pptx' ? 'presentation.pptx' : 
                    fileType === 'pdf' ? 'presentation.pdf' : 
                    fileType === 'notes' ? 'speaker_notes.txt' :
                    'animation.mp4'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      a.remove()
    } catch (error) {
      console.error('Download failed:', error)
      alert('Download failed. Please try again.')
    }
  }

  const handleNewPrompt = () => {
    setPrompt('')
    setJobId(null)
    setProgress(0)
    setStatus('')
    setSteps([])
    setCompleted(false)
    setDownloadReady(false)
    setSlides([])
    setDiagrams([])
    setAnimation(null)
    setError(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #0f172a, #312e81, #0f172a)', 
      padding: '20px',
      overflowX: 'hidden' // Prevent horizontal overflow
    }}>
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto',
        padding: '0 4px' // Add small padding to prevent edge overflow
      }}>
        <div style={{ textAlign: 'center', padding: '30px 0 15px' }}>
          <h1 style={{ fontSize: '48px', fontWeight: 'bold', color: 'white' }}>
            <span style={{ background: 'linear-gradient(to right, #a78bfa, #f472b6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Vynetra
            </span>
          </h1>
          <p style={{ color: '#9ca3af', fontSize: '18px', marginTop: '8px' }}>One Prompt. A Complete Presentation.</p>
        </div>

        <div style={{ 
          background: 'rgba(255,255,255,0.08)', 
          backdropFilter: 'blur(12px)', 
          borderRadius: '16px', 
          padding: '24px', 
          border: '1px solid rgba(255,255,255,0.1)', 
          marginBottom: '24px',
          overflow: 'hidden' // Ensure container doesn't overflow
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your presentation topic or prompt..."
              style={{
                width: '100%',
                minHeight: '80px',
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.15)',
                borderRadius: '12px',
                padding: '16px',
                color: 'white',
                fontSize: '16px',
                resize: 'vertical',
                outline: 'none',
                fontFamily: 'inherit',
                boxSizing: 'border-box', // Critical: ensures padding is included in width
                maxWidth: '100%' // Prevent overflow
              }}
              disabled={isLoading}
            />
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <button
                onClick={handleGenerate}
                disabled={isLoading || !prompt.trim()}
                style={{
                  flex: 1,
                  padding: '12px 24px',
                  background: isLoading ? 'linear-gradient(to right, #6b21a5, #be185d)' : 'linear-gradient(to right, #8b5cf6, #ec4899)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontWeight: '600',
                  fontSize: '16px',
                  cursor: isLoading || !prompt.trim() ? 'not-allowed' : 'pointer',
                  opacity: isLoading || !prompt.trim() ? 0.6 : 1,
                  transition: 'all 0.2s',
                  boxSizing: 'border-box'
                }}
              >
                {isLoading ? 'Generating...' : 'Generate Presentation'}
              </button>
            </div>
          </div>
          {error && (
            <div style={{ marginTop: '12px', padding: '12px', background: 'rgba(239,68,68,0.1)', borderRadius: '8px', border: '1px solid rgba(239,68,68,0.2)', color: '#f87171' }}>
              {error}
            </div>
          )}
        </div>

        {isLoading && (
          <div style={{ background: 'rgba(255,255,255,0.08)', backdropFilter: 'blur(12px)', borderRadius: '16px', padding: '24px', border: '1px solid rgba(255,255,255,0.1)', marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ color: '#9ca3af', fontSize: '14px' }}>Progress</span>
              <span style={{ color: 'white', fontSize: '14px', fontWeight: '600' }}>{progress}%</span>
            </div>
            <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
              <div
                style={{
                  height: '100%',
                  background: 'linear-gradient(to right, #8b5cf6, #ec4899)',
                  transition: 'width 0.5s ease',
                  width: progress + '%',
                  borderRadius: '3px'
                }}
              />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px' }}>
              <span style={{ color: '#60a5fa' }}>⏳</span>
              <span style={{ color: '#9ca3af', fontSize: '14px' }}>{status}</span>
            </div>

            {steps.length > 0 && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '8px', marginTop: '16px' }}>
                {['planning', 'research', 'slides', 'diagrams', 'animation', 'ppt', 'pdf', 'complete'].map((key) => {
                  const labels = {
                    planning: 'Planning',
                    research: 'Research',
                    slides: 'Content',
                    diagrams: 'Diagrams',
                    animation: 'Animation',
                    ppt: 'PowerPoint',
                    pdf: 'PDF Export',
                    complete: 'Complete!',
                  }
                  const isDone = steps.includes(labels[key])
                  const colors = {
                    planning: { bg: 'rgba(139,92,246,0.2)', border: '#8b5cf6' },
                    research: { bg: 'rgba(59,130,246,0.2)', border: '#3b82f6' },
                    slides: { bg: 'rgba(16,185,129,0.2)', border: '#10b981' },
                    diagrams: { bg: 'rgba(245,158,11,0.2)', border: '#f59e0b' },
                    animation: { bg: 'rgba(236,72,153,0.2)', border: '#ec4899' },
                    ppt: { bg: 'rgba(168,85,247,0.2)', border: '#a855f7' },
                    pdf: { bg: 'rgba(239,68,68,0.2)', border: '#ef4444' },
                    complete: { bg: 'rgba(34,197,94,0.2)', border: '#22c55e' },
                  }
                  return (
                    <div
                      key={key}
                      style={{
                        padding: '8px 12px',
                        background: isDone ? colors[key].bg : 'rgba(255,255,255,0.03)',
                        borderRadius: '8px',
                        border: '1px solid ' + (isDone ? colors[key].border : 'rgba(255,255,255,0.05)'),
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '13px',
                        color: isDone ? 'white' : '#6b7280'
                      }}
                    >
                      <span>{isDone ? '✅' : '⏳'}</span>
                      <span>{labels[key]}</span>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}

        {completed && downloadReady && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{ background: 'rgba(34,197,94,0.1)', backdropFilter: 'blur(12px)', borderRadius: '16px', padding: '24px', border: '1px solid rgba(34,197,94,0.3)', textAlign: 'center' }}>
              <h2 style={{ color: '#4ade80', fontSize: '24px', fontWeight: '600', marginBottom: '8px' }}>Presentation Ready!</h2>
              <p style={{ color: '#9ca3af' }}>Your presentation has been generated successfully.</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center', marginTop: '16px' }}>
                <button onClick={() => handleDownload('pptx')} style={{ padding: '8px 16px', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '500', fontSize: '14px' }}>
                  Download PPTX
                </button>
                <button onClick={() => handleDownload('pdf')} style={{ padding: '8px 16px', background: '#ec4899', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '500', fontSize: '14px' }}>
                  Download PDF
                </button>
                <button onClick={() => handleDownload('notes')} style={{ padding: '8px 16px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '500', fontSize: '14px' }}>
                  Speaker Notes
                </button>
                {animation && (
                  <button onClick={() => handleDownload('animation')} style={{ padding: '8px 16px', background: '#10b981', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '500', fontSize: '14px' }}>
                    Download Animation
                  </button>
                )}
                <button onClick={handleNewPrompt} style={{ padding: '8px 16px', background: 'rgba(255,255,255,0.1)', color: '#9ca3af', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' }}>
                  New Presentation
                </button>
              </div>
            </div>

            {diagrams.length > 0 && (
              <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '16px', padding: '16px', border: '1px solid rgba(255,255,255,0.1)' }}>
                <h3 style={{ color: 'white', fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>📊 Diagrams</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
                  {diagrams.map((diagram, index) => (
                    <div key={index} style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '8px', padding: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
                      <div style={{ color: 'white', fontWeight: '500', fontSize: '14px', marginBottom: '4px' }}>{diagram.title}</div>
                      <div style={{ color: '#9ca3af', fontSize: '12px' }}>{diagram.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {slides.length > 0 && (
              <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '16px', padding: '16px', border: '1px solid rgba(255,255,255,0.1)' }}>
                <h3 style={{ color: 'white', fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>📄 Slides Preview</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '12px' }}>
                  {slides.slice(0, 6).map((slide) => (
                    <div key={slide.number} style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '8px', padding: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
                      <div style={{ fontSize: '11px', color: '#6b7280', marginBottom: '4px' }}>Slide {slide.number}</div>
                      <div style={{ color: 'white', fontWeight: '500', fontSize: '14px', marginBottom: '4px' }}>{slide.title}</div>
                      <div style={{ color: '#9ca3af', fontSize: '12px' }}>{slide.content}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div style={{ marginTop: '32px', padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)', textAlign: 'center' }}>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '32px', flexWrap: 'wrap', color: '#6b7280', fontSize: '14px' }}>
            <span>Vynetra AI</span>
            <span>One Prompt. A Complete Presentation.</span>
            <span>v1.0.0</span>
          </div>
        </div>
      </div>
    </div>
  )
}