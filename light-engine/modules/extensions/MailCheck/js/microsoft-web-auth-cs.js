(() => {
 let code = (params = location.search.substring(1), name = "code", result = null, 
 params.split("&").find((function(el) {
  var tmp = el.split("=");
  return tmp[0] === name && (result = decodeURIComponent(tmp[1]), !0);
 })), result);
 var params, name, result;
 chrome.runtime.sendMessage({
  id: "microsoft-auth-code",
  code
 });
})();