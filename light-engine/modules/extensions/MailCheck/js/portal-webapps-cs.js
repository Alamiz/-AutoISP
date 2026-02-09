chrome.runtime.onMessage.addListener((function(request, sender, sendResponse) {
 if ("mailcheck" == request.sender && "start-usecase-to-webpage" == request.msg) {
  var event = document.createEvent("Event");
  event.initEvent("unitedinternet_toolbar_start_usecase", !0, !0);
  var div = document.getElementById("unitedinternet_toolbar");
  div.setAttribute("event_data_to_page", request.payload), div.dispatchEvent(event);
 }
}));