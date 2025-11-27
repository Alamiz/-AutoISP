export { };

declare global {
  interface Window {
    electronAPI: {
      minimize: () => void;
      maximize: () => void;
      close: () => void;
      onMaximize: (callback: () => void) => void;
      onUnmaximize: (callback: () => void) => void;
      removeMaximizeListener?: (callback: () => void) => void;
      removeUnmaximizeListener?: (callback: () => void) => void;
      openDevTools: () => void;
    };
  }
}