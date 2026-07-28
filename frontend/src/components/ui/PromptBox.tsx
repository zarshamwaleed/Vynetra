'use client'

import { useState } from 'react'
import { Sparkles } from 'lucide-react'

interface PromptBoxProps {
  onSubmit: (prompt: string) => void
  isLoading?: boolean
  placeholder?: string
}

export function PromptBox({
  onSubmit,
  isLoading = false,
  placeholder = 'Enter your presentation topic or prompt...',
}: PromptBoxProps) {
  const [prompt, setPrompt] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (prompt.trim() && !isLoading) {
      onSubmit(prompt.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={placeholder}
          className={
            w-full h-32 bg-white/5 border border-white/20 rounded-xl p-4 
            text-white placeholder-gray-400 
            focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent
            resize-none transition-all
            
          }
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !prompt.trim()}
          className={
            absolute bottom-4 right-4
            bg-gradient-to-r from-purple-500 to-pink-500 
            text-white px-6 py-2 rounded-lg font-medium
            transition-all flex items-center gap-2
            
          }
        >
          {isLoading ? (
            'Generating...'
          ) : (
            <>
              Generate <Sparkles className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </form>
  )
}
