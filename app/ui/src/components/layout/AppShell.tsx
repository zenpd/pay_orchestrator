import { ReactNode } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'
import Footer from './Footer'

interface AppShellProps {
  children: ReactNode
}

export default function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <Header />
      <main className="ml-60 mt-16 mb-11 min-h-[calc(100vh-104px)] overflow-y-auto">
        <div className="p-6">
          {children}
        </div>
      </main>
      <Footer />
    </div>
  )
}
