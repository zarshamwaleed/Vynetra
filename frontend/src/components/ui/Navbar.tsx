'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Wand2, History, Settings, Server, Sparkles } from 'lucide-react'

const navItems = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/generate', label: 'Generate', icon: Wand2 },
  { href: '/history', label: 'History', icon: History },
  { href: '/mcp-monitor', label: 'MCP Monitor', icon: Server },
  { href: '/settings', label: 'Settings', icon: Settings },
]

export function Navbar() {
  const pathname = usePathname()

  return (
    <nav className="bg-white/10 backdrop-blur-lg border-b border-white/10">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-purple-400" />
            <span className="text-white font-bold text-xl">Vynetra</span>
          </Link>
          <div className="flex items-center gap-1">
            {navItems.map(({ href, label, icon: Icon }) => {
              const isActive = pathname === href
              return (
                <Link
                  key={href}
                  href={href}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors text-gray-400 hover:text-white hover:bg-white/10"
                >
                  <Icon className="w-4 h-4" />
                  <span>{label}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}