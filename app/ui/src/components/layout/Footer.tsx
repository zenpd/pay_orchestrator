export default function Footer() {
  return (
    <footer className="fixed bottom-0 left-60 right-0 h-11 bg-white/80 backdrop-blur-xl border-t border-gray-100/80 z-30">
      <div className="h-full px-6 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-3">
          <span>PayFlow</span>
          <span>·</span>
          <span>v1.0.0</span>
          <span>·</span>
          <span>© 2025 ZenLabs</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            API Online
          </span>
        </div>
      </div>
    </footer>
  )
}
