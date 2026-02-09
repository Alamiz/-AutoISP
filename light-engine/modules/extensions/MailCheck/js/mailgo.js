(() => {
 "use strict";
 var title, open, copyMail, mailcheck, url, mail, encEmail, cc, bcc, subject, bodyMail, openMailCheck, openDefault, copy, mailgoCheckRender, mailgoKeydown, showMailgo, hideMailgo, mailgoIsShowing, byElement, createElement, createTextNode, mailToEncoded, encodeEmail, E, getDisplay, setDisplay, composedPath, validateEmail, validateEmails, copyToClipboard;
 url = "", mail = "", encEmail = "", cc = "", bcc = "", subject = "", bodyMail = "", 
 openMailCheck = function() {
  !function(params) {
   chrome.runtime.sendMessage({
    id: "compose-mailto-message",
    params
   }, (function(response) {
    chrome.runtime.lastError, hideMailgo();
   }));
  }({
   to: mail,
   cc,
   bcc,
   subject,
   body: bodyMail
  });
 }, openDefault = function() {
  mailToEncoded(encEmail), hideMailgo();
 }, copy = function(content) {
  var activeCopy;
  copyToClipboard(content), (activeCopy = mailgoIsShowing("mail") ? copyMail : copyTel).textContent = chrome.i18n.getMessage("mailto_copied"), 
  setTimeout((function() {
   activeCopy.textContent = chrome.i18n.getMessage("mailto_copy_clipboard"), hideMailgo();
  }), 999);
 }, mailgoCheckRender = function(event) {
  if (document.contains(E("mailgo")) && !mailgoIsShowing("mail")) {
   var path = event.path || event.composedPath && event.composedPath() || composedPath(event.target);
   path && path.forEach((function(element) {
    if (!(element instanceof HTMLDocument || element instanceof Window)) return function(element) {
     return "mail" === (arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : "mail") && (element.href && element.href.toLowerCase().startsWith("mailto:") && !element.classList.contains("no-mailgo") || element.hasAttribute("data-address") && (element.href && "#mailgo" === element.getAttribute("href").toLowerCase() || element.classList && element.classList.contains("mailgo")));
    }(element, "mail") ? (event.preventDefault(), void function() {
     var mailgo = arguments.length > 1 ? arguments[1] : void 0;
     if ("mail" === (arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : "mail")) {
      if (mailgo.href && mailgo.href.toLowerCase().startsWith("mailto:")) {
       mail = decodeURIComponent(mailgo.href.split("?")[0].split("mailto:")[1].trim()), 
       url = new URL(mailgo.href);
       var urlParams = new URLSearchParams(url.search);
       cc = urlParams.get("cc"), bcc = urlParams.get("bcc"), subject = urlParams.get("subject"), 
       bodyMail = urlParams.get("body");
      }
      if (!validateEmails(mail.split(","))) return;
      cc && !validateEmails(cc.split(",")) && (cc = ""), bcc && !validateEmails(bcc.split(",")) && (bcc = ""), 
      title.innerHTML = chrome.i18n.getMessage("mailto_compose") + "<br/>", mailcheck.removeEventListener("click", openMailCheck), 
      mailcheck.addEventListener("click", openMailCheck), encEmail = encodeEmail(mail), 
      open.addEventListener("click", openDefault), copyMail.addEventListener("click", (function() {
       return copy(mail);
      }));
     }
     showMailgo(), document.addEventListener("keydown", mailgoKeydown);
    }("mail", element)) : void 0;
   }));
  }
 }, mailgoKeydown = function(event) {
  if (mailgoIsShowing("mail")) switch (event.keyCode) {
  case 27:
   hideMailgo();
   break;

  case 77:
   openMailCheck();
   break;

  case 71:
   !function() {
    var url = "https://mail.google.com/mail/u/0/?extsrc=mailto&url=" + encodeURIComponent(url);
    window.open(url, "_blank"), hideMailgo();
   }();
   break;

  case 79:
   outlookUrl = "https://outlook.live.com/owa/?path=/mail/action/compose&to=" + encodeURIComponent(mail), 
   subject && (outlookUrl = outlookUrl.concat("&subject=" + subject)), bodyMail && (outlookUrl = outlookUrl.concat("&body=" + bodyMail)), 
   window.open(outlookUrl, "_blank"), hideMailgo();
   break;

  case 32:
  case 13:
   openDefault();
   break;

  case 67:
   copy(mail);
   break;

  default:
   return;
  }
  var outlookUrl;
 }, showMailgo = function() {
  setDisplay("mailgo", "flex");
 }, hideMailgo = function() {
  setDisplay("mailgo", "none"), document.removeEventListener("keydown", mailgoKeydown);
 }, mailgoIsShowing = function() {
  return "mail" === (arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : "mail") && "flex" === getDisplay("mailgo");
 }, byElement = function() {
  var by = createElement("a");
  by.className = "m-by";
  var textBy = createTextNode(chrome.i18n.getMessage("appName"));
  return by.appendChild(textBy), by;
 }, createElement = function(element) {
  return document.createElement(element);
 }, createTextNode = function(element) {
  return document.createTextNode(element);
 }, mailToEncoded = function(encoded) {
  return window.location.href = "mailto:" + atob(encoded);
 }, encodeEmail = function(email) {
  return btoa(email);
 }, E = function(id) {
  return document.getElementById(id);
 }, getDisplay = function(id) {
  return E(id).style.display;
 }, setDisplay = function(id, value) {
  return E(id).style.display = value;
 }, composedPath = function(el) {
  for (var path = []; el; ) {
   if (path.push(el), "HTML" === el.tagName) return path.push(document), path.push(window), 
   path;
   el = el.parentElement;
  }
 }, validateEmail = function(email) {
  return /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(email);
 }, validateEmails = function(arr) {
  return arr.every(validateEmail);
 }, copyToClipboard = function(str) {
  var el = createElement("textarea");
  el.value = str, el.setAttribute("readonly", ""), el.style.position = "absolute", 
  el.style.left = "-9999px", document.body.appendChild(el);
  var selected = document.getSelection().rangeCount > 0 && document.getSelection().getRangeAt(0);
  el.select(), document.execCommand("copy"), document.body.removeChild(el), selected && (document.getSelection().removeAllRanges(), 
  document.getSelection().addRange(selected));
 }, function() {
  var mailgoCSS = document.getElementById("mailgo-style");
  mailgoCSS && mailgoCSS.parentElement.removeChild(mailgoCSS), (mailgoCSS = createElement("style")).id = "mailgo-style", 
  mailgoCSS.type = "text/css";
  var mailgoCSSContent = createTextNode('.m-modal{position:fixed;top:0;right:0;bottom:0;left:0;-webkit-box-pack:center;-webkit-justify-content:center;-moz-box-pack:center;-ms-flex-pack:center;justify-content:center;-webkit-box-align:center;-webkit-align-items:center;-moz-box-align:center;-ms-flex-align:center;align-items:center;-webkit-box-orient:vertical;-webkit-box-direction:normal;-webkit-flex-direction:column;-moz-box-orient:vertical;-moz-box-direction:normal;-ms-flex-direction:column;flex-direction:column;overflow:hidden;font-size:14px;z-index:10000}.m-modal a,.m-modal p,.m-modal span,.m-modal strong{border:none;margin:0;padding:0;font-size:100%;line-height:1;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";text-rendering:optimizeLegibility}.m-modal strong{font-weight:700}.m-modal .m-modal-back{position:absolute;z-index:10001;top:0;right:0;bottom:0;left:0;background-color:rgba(32,35,42,.75);opacity:.8}.m-modal .m-modal-content{position:relative;z-index:10002;-webkit-box-sizing:content-box;-moz-box-sizing:content-box;box-sizing:content-box;text-align:center;min-width:200px;max-width:240px;background-color:#fff;opacity:.97;-webkit-border-radius:8px;-moz-border-radius:8px;border-radius:8px;-webkit-box-shadow:0 3px 20px rgba(32,35,42,.5);-moz-box-shadow:0 3px 20px rgba(32,35,42,.5);box-shadow:0 3px 20px rgba(32,35,42,.5);color:#4a4a4a;display:-webkit-box;display:-webkit-flex;display:-moz-box;display:-ms-flexbox;display:flex;-webkit-box-orient:vertical;-webkit-box-direction:normal;-webkit-flex-direction:column;-moz-box-orient:vertical;-moz-box-direction:normal;-ms-flex-direction:column;flex-direction:column;overflow:auto;padding:20px;-webkit-transition:.5s -webkit-box-shadow;transition:.5s -webkit-box-shadow;-o-transition:.5s box-shadow;-moz-transition:.5s box-shadow,.5s -moz-box-shadow;transition:.5s box-shadow;transition:.5s box-shadow,.5s -webkit-box-shadow,.5s -moz-box-shadow}.m-modal .m-modal-content:hover{opacity:1;-webkit-box-shadow:0 7px 20px rgba(32,35,42,.85);-moz-box-shadow:0 7px 20px rgba(32,35,42,.85);box-shadow:0 7px 20px rgba(32,35,42,.85)}.m-modal .m-modal-content .m-title{margin-bottom:8px;overflow:hidden;white-space:nowrap;-o-text-overflow:ellipsis;text-overflow:ellipsis}.m-modal .m-modal-content .m-details{margin-bottom:10px}.m-modal .m-modal-content .m-details p{font-size:12px;margin-top:3px;margin-bottom:3px}.m-modal .m-modal-content a{padding:10px;color:#4a4a4a;-webkit-border-radius:8px;-moz-border-radius:8px;border-radius:8px;text-decoration:none}.m-modal .m-modal-content a.m-mailcheck{font-size:16px}.m-modal .m-modal-content a.m-mailcheck:hover{background-color:rgba(0,0,0,.08)}.m-modal .m-modal-content a.m-gmail{color:#d44638}.m-modal .m-modal-content a.m-gmail:hover{background-color:rgba(212,70,56,.08)}.m-modal .m-modal-content a.m-outlook{color:#0072c6}.m-modal .m-modal-content a.m-outlook:hover{background-color:rgba(0,114,198,.08)}.m-modal .m-modal-content a.m-copy{padding:16px 10px}.m-modal .m-modal-content a.m-copy:hover,.m-modal .m-modal-content a.m-default:hover{background-color:rgba(0,0,0,.08);color:#4a4a4a}.m-modal .m-modal-content a.m-by{font-size:8px;margin-top:.8rem;padding:5px;color:#4a4a4a;opacity:.5}.m-modal .m-modal-content a.m-by:hover{opacity:1}.m-modal .m-modal-content .w-500{font-weight:500}');
  mailgoCSS.appendChild(mailgoCSSContent), document.head.appendChild(mailgoCSS), function() {
   var modal = createElement("div");
   modal.style.display = "none", modal.id = "mailgo", modal.classList.add("m-modal");
   var modalBackground = createElement("div");
   modalBackground.className = "m-modal-back", modal.appendChild(modalBackground);
   var modalContent = createElement("div");
   modalContent.className = "m-modal-content", modal.appendChild(modalContent), (title = createElement("strong")).id = "m-title", 
   title.className = "m-title", modalContent.appendChild(title), (mailcheck = createElement("a")).id = "m-mailcheck", 
   mailcheck.href = "javascript:void(0);", mailcheck.classList.add("m-open"), mailcheck.classList.add("m-mailcheck");
   var mailcheckSpan = createElement("span");
   mailcheckSpan.className = "w-500";
   var mailcheckSpanContent = createTextNode("MailCheck");
   mailcheckSpan.appendChild(mailcheckSpanContent), mailcheck.appendChild(mailcheckSpan), 
   modalContent.appendChild(mailcheck), (open = createElement("a")).id = "m-open", 
   open.href = "javascript:void(0);", open.classList.add("m-open"), open.classList.add("m-default");
   var openSpan = createElement("span");
   openSpan.className = "w-500";
   var openSpanContent = createTextNode("Desktop App");
   openSpan.appendChild(openSpanContent), open.appendChild(openSpan), modalContent.appendChild(open), 
   (copyMail = createElement("a")).id = "m-copy", copyMail.href = "javascript:void(0);", 
   copyMail.classList.add("m-copy"), copyMail.classList.add("w-500");
   var copyContent = createTextNode(chrome.i18n.getMessage("mailto_copy_clipboard"));
   copyMail.appendChild(copyContent), modalContent.appendChild(copyMail), modalContent.appendChild(byElement()), 
   document.body.appendChild(modal), modalBackground.removeEventListener("click", hideMailgo), 
   modalBackground.addEventListener("click", hideMailgo);
  }(), document.removeEventListener("click", mailgoCheckRender), document.addEventListener("click", mailgoCheckRender);
 }();
})();