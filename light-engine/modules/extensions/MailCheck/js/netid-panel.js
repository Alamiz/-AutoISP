(() => {
 "use strict";
 const _freeGlobal = "object" == typeof global && global && global.Object === Object && global;
 var freeSelf = "object" == typeof self && self && self.Object === Object && self;
 const _Symbol = (_freeGlobal || freeSelf || Function("return this")()).Symbol;
 var objectProto = Object.prototype, _getRawTag_hasOwnProperty = objectProto.hasOwnProperty, nativeObjectToString = objectProto.toString, symToStringTag = _Symbol ? _Symbol.toStringTag : void 0;
 const _getRawTag = function(value) {
  var isOwn = _getRawTag_hasOwnProperty.call(value, symToStringTag), tag = value[symToStringTag];
  try {
   value[symToStringTag] = void 0;
   var unmasked = !0;
  } catch (e) {}
  var result = nativeObjectToString.call(value);
  return unmasked && (isOwn ? value[symToStringTag] = tag : delete value[symToStringTag]), 
  result;
 };
 var _objectToString_nativeObjectToString = Object.prototype.toString;
 const _objectToString = function(value) {
  return _objectToString_nativeObjectToString.call(value);
 };
 var _baseGetTag_symToStringTag = _Symbol ? _Symbol.toStringTag : void 0;
 const _baseGetTag = function(value) {
  return null == value ? void 0 === value ? "[object Undefined]" : "[object Null]" : _baseGetTag_symToStringTag && _baseGetTag_symToStringTag in Object(value) ? _getRawTag(value) : _objectToString(value);
 };
 const lodash_es_isObject = function(value) {
  var type = typeof value;
  return null != value && ("object" == type || "function" == type);
 };
 const lodash_es_isFunction = function(value) {
  if (!lodash_es_isObject(value)) return !1;
  var tag = _baseGetTag(value);
  return "[object Function]" == tag || "[object GeneratorFunction]" == tag || "[object AsyncFunction]" == tag || "[object Proxy]" == tag;
 }, SET_OPTION = "set-option";
 function E(id) {
  return document.getElementById(id);
 }
 window.addEventListener("DOMContentLoaded", (function() {
  let params = window.location.search.slice(1).split("&").reduce(((result, item) => {
   let parts = item.split("=");
   return result[parts[0]] = decodeURIComponent(parts[1]), result;
  }), {});
  const m = chrome.runtime.getManifest();
  !function(container, placeholders) {
   const elements = container.querySelectorAll("*[translate]");
   for (let i = 0; i < elements.length; i++) {
    const el = elements[i], key = el.getAttribute("translate"), label = chrome.i18n.getMessage(key, placeholders);
    el.appendChild((text = label, document.createTextNode(text)));
   }
   var text;
  }(document.body, [ params.name, m.version_name || m.version ]);
  const logoEl = E("partner-logo");
  logoEl && params.logo && (logoEl.src = params.logo);
  const submitEl = E("login");
  submitEl && params.target && submitEl.addEventListener("click", (_ => {
   chrome.tabs.create({
    url: params.target,
    active: !0
   }), window.close();
  })), E("optout").addEventListener("click", (evt => {
   const sender = evt.target;
   var key, value, ns, responseHandler;
   key = sender.name, value = !sender.checked, lodash_es_isFunction(ns = response => {
    !0 !== response && console.error("failed to set option"), window.close();
   }) && (responseHandler = ns, ns = "general"), chrome.runtime.sendMessage({
    id: SET_OPTION,
    key,
    value,
    namespace: ns
   }, responseHandler);
  }), !1);
 }), !1);
})();