(() => {
 "use strict";
 var __webpack_modules__ = {
  8379: module => {
   module.exports = JSON.parse('{"storeExtensionUrlPrefix":"https://chrome.google.com/webstore/detail/","brand":{"aib":{"uninstallURL":"https://go.mail.com/tb/en-us/gc_uninstall_runonce?portal=mailcom&browser=chrome&_c=0"},"cm":{"searchURL":"https://go.mail.com/tb/en-us/gc_labelsearch?q="},"faviconURL":"https://s.uicdn.com/mailint/8.1259.0/assets/favicon.ico","login":{"name":"mail.com","provider":"mailcom","createAccountURLWeb":"https://go.mail.com/tb/en-us/gc_signup","forgotPasswordURL":"https://go.mail.com/tb/en-us/gc_help_password"},"searchReferrer":"https://search.mail.com/","feedbackURL":"https://go.mail.com/tb/en-us/gc_feedback","firstrunURL":"https://go.mail.com/tb/en-us/gc_runonce","helpURL":"https://go.mail.com/tb/en-us/gc_help","homepageURL":"https://go.mail.com/tb/en-us/gc_home","lastTabURL":"https://go.mail.com/tb/en-us/gc_lasttab","notFoundURL":"https://go.mail.com/tb/en-us/gc_search_404","privacyDetailsURL":"https://go.mail.com/tb/en-us/gc_usage_data","privacyURL":"https://go.mail.com/tb/login/gc_datenschutz","ratingURL":"https://go.mail.com/tb/gc_star_","redirectSearchURL":"https://go.mail.com/tb/en-us/gc_websearch","searchOnLogoutURL":"https://go.mail.com/tb/en-us/gc_logout","startpageHomepageURL":"https://go.mail.com/tb/en-us/gc_startpage_homepage","startpageURL":"https://go.mail.com/tb/en-us/gc_startpage","upgradeURL":"https://go.mail.com/tb/en-us/gc_addon","versionURL":"https://go.mail.com/tb/en-us/gc_version"}}');
  }
 }, __webpack_module_cache__ = {};
 function __webpack_require__(moduleId) {
  var cachedModule = __webpack_module_cache__[moduleId];
  if (void 0 !== cachedModule) return cachedModule.exports;
  var module = __webpack_module_cache__[moduleId] = {
   exports: {}
  };
  return __webpack_modules__[moduleId](module, module.exports, __webpack_require__), 
  module.exports;
 }
 (() => {
  const _data = __webpack_require__(8379), {brand: config_brand, storeExtensionUrlPrefix} = _data;
  function Exception(msg) {
   this._message = msg;
   try {
    dummy.to.provoke.a.native.exception += 1;
   } catch (e) {
    this.stack = e.stack;
   }
  }
  function NotReached(msg) {
   Exception.call(this, msg);
  }
  function UserError(msg) {
   Exception.call(this, msg), this.causedByUser = !0;
  }
  function Abortable() {}
  function TimeoutAbortable(setTimeoutID) {
   this._id = setTimeoutID;
  }
  function IntervalAbortable(setIntervalID) {
   this._id = setIntervalID;
  }
  function SuccessiveAbortable() {
   this._current = null;
  }
  function extend(child, supertype) {
   var properties = Object.create(null);
   Object.getOwnPropertyNames(child.prototype).forEach((function(key) {
    properties[key] = Object.getOwnPropertyDescriptor(child.prototype, key);
   })), child.prototype = Object.create(supertype.prototype, properties);
  }
  function assert(test, errorMsg) {
  }
  Exception.prototype = {
   get message() {
    return this._message;
   },
   set message(msg) {
    this._message = msg;
   },
   toString: function() {
    return this._message;
   }
  }, extend(NotReached, Exception), UserError.prototype = {}, extend(UserError, Exception), 
  Abortable.prototype = {
   cancel: function() {}
  }, TimeoutAbortable.prototype = {
   cancel: function() {
    clearTimeout(this._id);
   }
  }, extend(TimeoutAbortable, Abortable), IntervalAbortable.prototype = {
   cancel: function() {
    clearInterval(this._id);
   }
  }, extend(IntervalAbortable, Abortable), SuccessiveAbortable.prototype = {
   set current(abortable) {
    assert(abortable instanceof Abortable || null == abortable, "need an Abortable object (or null)"), 
    this._current = abortable;
   },
   get current() {
    return this._current;
   },
   cancel: function() {
    this._current && this._current.cancel();
   }
  }, extend(SuccessiveAbortable, Abortable);
  function isAIBEnabled(opts) {
   const state = opts.privacy_usage_data && opts.privacy_usage_data_tcf;
   return 1 == state;
  }
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
  var responseHandler;
  window.addEventListener("message", (ev => {
   if (ev.source === window && "ext-full-consent" === ev.data.key) {
    const value = ev.data.value;
    return function(key, value, ns, responseHandler) {
     lodash_es_isFunction(ns) && (responseHandler = ns, ns = "general"), chrome.runtime.sendMessage({
      id: SET_OPTION,
      key,
      value,
      namespace: ns
     }, responseHandler);
    }("privacy_usage_data_tcf", value, (response => {})), value;
   }
  }), !1), responseHandler = opts => {
   isAIBEnabled(opts) && chrome.runtime.sendMessage({
    id: "get-aib-identity"
   }, (function(response) {
    response && window.postMessage({
     key: "ext-site-ident",
     value: response.addOnInfo
    });
   }));
  }, chrome.runtime.sendMessage({
   id: "get-general-options"
  }, responseHandler);
 })();
})();