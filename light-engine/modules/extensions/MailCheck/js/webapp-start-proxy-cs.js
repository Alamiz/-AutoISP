(() => {
 function field(key, value) {
  let f = document.createElement("input");
  return f.setAttribute("type", "hidden"), f.setAttribute("name", key), f.setAttribute("value", decodeURIComponent(value)), 
  f;
 }
 window.go = function(uploadBody) {
  let params = function(uploadBody) {
   let json = '{"' + uploadBody.replace(/"/g, '\\"').replace(/&/g, '","').replace(/=/g, '":"') + '"}';
   return JSON.parse(json);
  }(uploadBody), form = document.createElement("form");
  for (var key in form.setAttribute("method", "post"), form.setAttribute("action", params.url), 
  delete params.url, params) console.log(key + "=" + params[key]), form.appendChild(field(key, params[key]));
  document.body.appendChild(form), form.submit();
 }, chrome.runtime.sendMessage({
  id: "webapp-start-inject-now"
 });
})();