export { };

declare global {
  interface Window {
    electronAPI: {
      minimize: () => void;
      maximize: () => void;
      close: () => void;
      resize: (width: number, height: number) => void;
      onMaximize: (callback: () => void) => void;
      onUnmaximize: (callback: () => void) => void;
      removeMaximizeListener?: (callback: () => void) => void;
      removeUnmaximizeListener?: (callback: () => void) => void;
      openDevTools: () => void;
    };
  }
}