"use client";

import { useState, useEffect } from 'react';
import { Minus, Square, Copy, X } from 'lucide-react';
import { useProvider } from '@/contexts/provider-context';

export default function Titlebar() {
  const [isMaximized, setIsMaximized] = useState(false);
  const { selectedProvider } = useProvider();

  useEffect(() => {
    // Listen for maximize/unmaximize events from Electron
    const handleMaximize = () => setIsMaximized(true);
    const handleUnmaximize = () => setIsMaximized(false);

    // Check if the API exists and set up listeners
    if (window.electronAPI) {
      window.electronAPI.onMaximize?.(handleMaximize);
      window.electronAPI.onUnmaximize?.(handleUnmaximize);
    }

    return () => {
      // Cleanup listeners if your API supports it
      window.electronAPI.removeMaximizeListener?.(handleMaximize);
      window.electronAPI.removeUnmaximizeListener?.(handleUnmaximize);
    };
  }, []);

  return (
    <div className="h-8 bg-zinc-950 border-b border-zinc-800 flex items-center justify-between select-none z-50 sticky top-0" style={{ WebkitAppRegion: 'drag' } as React.CSSProperties}>
      {/* Drag region */}
      <div className="flex-1 h-full" style={{ WebkitAppRegion: 'drag' } as React.CSSProperties} />

      {/* App title (optional) */}
      <div className="absolute left-1/2 transform -translate-x-1/2 text-zinc-400 text-xs font-medium pointer-events-none flex items-center gap-2">
        <span>Auto ISP</span>
        {selectedProvider && (
          <>
            <span className="text-zinc-600">/</span>
            <span className="text-zinc-200">{selectedProvider.name}</span>
          </>
        )}
      </div>

      {/* Window controls */}
      <div className="flex items-center h-full" style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}>
        {/* Minimize - sends window to taskbar */}
        <button
          onClick={() => window.electronAPI.minimize()}
          className="h-full w-12 flex items-center justify-center text-zinc-400 hover:bg-zinc-800 hover:text-zinc-50 transition-colors duration-150"
          style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
          title="Minimize"
        >
          <Minus size={16} strokeWidth={2.5} />
        </button>

        {/* Maximize/Restore toggle */}
        <button
          onClick={() => window.electronAPI.maximize()}
          className="h-full w-12 flex items-center justify-center text-zinc-400 hover:bg-zinc-800 hover:text-zinc-50 transition-colors duration-150"
          style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
          title={isMaximized ? "Restore" : "Maximize"}
        >
          {isMaximized ? (
            <Copy size={14} strokeWidth={2.5} />
          ) : (
            <Square size={14} strokeWidth={2.5} />
          )}
        </button>

        {/* Close */}
        <button
          onClick={() => window.electronAPI.close()}
          className="h-full w-12 flex items-center justify-center text-zinc-400 hover:bg-red-600 hover:text-white transition-colors duration-150"
          style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
          title="Close"
        >
          <X size={16} strokeWidth={2.5} />
        </button>
      </div>
    </div>
  );
}