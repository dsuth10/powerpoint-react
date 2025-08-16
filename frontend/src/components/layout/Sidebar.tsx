import { Link, useLocation } from '@tanstack/react-router'
import { MessageSquare, Presentation, Settings } from 'lucide-react'
import { useChatStore } from '@/stores/chat-store'

export default function Sidebar() {
  const location = useLocation()
  const currentSessionId = useChatStore((s) => s.currentSessionId)
  
  const linkClass = (path: string) => {
    const isActive = location.pathname.startsWith(path)
    return `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
      isActive 
        ? 'bg-primary text-primary-foreground' 
        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
    }`
  }

  // Determine the slides link based on whether we have a current session
  const slidesLink = currentSessionId ? `/slides/${currentSessionId}` : '/slides'

  return (
    <div className="w-64 bg-card border-r h-full">
      <div className="p-6">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
          AI Slides
        </h1>
      </div>
      
      <nav className="px-4 space-y-2">
        <Link to="/chat" className={linkClass('/chat')}>
          <MessageSquare className="w-5 h-5" />
          <span>Chat</span>
        </Link>
        
        <Link to={slidesLink} className={linkClass('/slides')}>
          <Presentation className="w-5 h-5" />
          <span>Slides</span>
        </Link>
        
        <Link to="/settings" className={linkClass('/settings')}>
          <Settings className="w-5 h-5" />
          <span>Settings</span>
        </Link>
      </nav>
    </div>
  )
}


