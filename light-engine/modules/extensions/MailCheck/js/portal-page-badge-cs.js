(() => {
 let badgeCountEl = null;
 function prepareWebapps(port) {
  const NAV_ID_TO_ACTION_MAPPING = {
   address_book: "goto-address-book",
   calendar: "goto-calendar",
   compose_mail: "goto-mail-composer",
   online_storage: "goto-online-storage",
   unread_mails: "goto-inbox"
  }, installItemAction = (el, action) => {
   el.href = "", el.onclick = () => port.postMessage({
    action
   }), "unread_mails" === el.id && (el => {
    badgeCountEl || (badgeCountEl = document.createElement("span"), el.appendChild(badgeCountEl));
   })(el);
  };
  let navContainer = document.body.querySelector("div.mail-check-injection-container");
  if (navContainer) {
   navContainer.querySelectorAll("div").forEach((el => installItemAction(el, NAV_ID_TO_ACTION_MAPPING[el.id])));
  }
 }
 const port = chrome.runtime.connect({
  name: "portal-webapps-cs"
 });
 port.onMessage.addListener((msg => {
  var el, text;
  "ACK" === msg.id ? (!function() {
   let base = document.createElement("base");
   base.target = "_parent", document.head.appendChild(base);
  }(), prepareWebapps(port), function() {
   let uninstallLink = document.getElementById("uninstall");
   uninstallLink && (uninstallLink.href = "", uninstallLink.onclick = () => {
    window.confirm(chrome.i18n.getMessage("ntp_uninstall_q")) && port.postMessage({
     action: "uninstall"
    });
   });
  }(), port.postMessage({
   id: "INIT"
  })) : "set-badge" === msg.id && (el = badgeCountEl, text = msg.text, el && (el.textContent = text));
 })), port.postMessage({
  id: "SYN"
 });
})();