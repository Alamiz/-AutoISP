chrome.runtime.sendMessage({
 id: "get-ext-info"
}, (response => {
 if (!response) return;
 let html = document.documentElement;
 html.setAttribute("data-tr-component-path", `${response.product}.${response.brand}.${response.version}.${response.variant}`), 
 html.setAttribute("united-toolbar-brand", response.brand), html.setAttribute("united-toolbar-version", response.version), 
 html.setAttribute("united-toolbar-variant", response.variant);
}));