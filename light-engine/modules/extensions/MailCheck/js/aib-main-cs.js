(() => {
 window.addEventListener("message", (ev => {
  if (ev.source === window && "ext-site-ident" === ev.data.key) {
   const value = ev.data.value;
   window.utag_data = {
    ...window.utag_data,
    ...value
   };
  }
 }), !1);
 const api = window.TcfApi;
 if (api && api.getPermissionFeature) {
  const allow = api.getPermissionFeature("fullConsent");
  window.postMessage({
   key: "ext-full-consent",
   value: allow
  });
 }
})();