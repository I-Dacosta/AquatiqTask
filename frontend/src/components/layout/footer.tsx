// src/components/layout/dashboard-footer.tsx
'use client';

export function Footer() {
  return (
    <footer className="bg-card/80 dark:bg-card/80 backdrop-blur-xl border-t border-border w-full min-h-0 flex items-center shadow-lg shadow-gray-900/5 transition-all duration-300">
      <div className="w-full max-w-7xl mx-auto px-2 py-2">
        <div className="flex flex-col sm:flex-row items-center justify-between space-y-1 sm:space-y-0">
          {/* Left side - Copyright */}
          <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
            © {new Date().getFullYear()} PrioriAI. All rights reserved.
          </div>
          {/* Keyboard Shortcuts Info */}
          <div className="text-[10px] text-gray-400 flex flex-row items-center gap-2 mt-1 sm:mt-0 truncate">
            <span><span className="font-mono">Ctrl+D</span> – Gå til dashboard</span>
            <span className="hidden sm:inline">|</span>
            <span><span className="font-mono">Ctrl+N</span> – Ny oppgave</span>
            <span className="hidden sm:inline">|</span>
            <span><span className="font-mono">Ctrl+R</span> – Oppdater</span>
          </div>
          {/* Right side - Version */}
          <div className="text-xs text-gray-500 dark:text-gray-400">
            <span className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-md text-[10px] font-mono">
              v1.0.0
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}