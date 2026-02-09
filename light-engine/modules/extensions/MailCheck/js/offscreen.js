(() => {
 "use strict";
 const _baseDelay = function(func, wait, args) {
  if ("function" != typeof func) throw new TypeError("Expected a function");
  return setTimeout((function() {
   func.apply(void 0, args);
  }), wait);
 };
 const lodash_es_identity = function(value) {
  return value;
 };
 const _apply = function(func, thisArg, args) {
  switch (args.length) {
  case 0:
   return func.call(thisArg);

  case 1:
   return func.call(thisArg, args[0]);

  case 2:
   return func.call(thisArg, args[0], args[1]);

  case 3:
   return func.call(thisArg, args[0], args[1], args[2]);
  }
  return func.apply(thisArg, args);
 };
 var nativeMax = Math.max;
 const _overRest = function(func, start, transform) {
  return start = nativeMax(void 0 === start ? func.length - 1 : start, 0), function() {
   for (var args = arguments, index = -1, length = nativeMax(args.length - start, 0), array = Array(length); ++index < length; ) array[index] = args[start + index];
   index = -1;
   for (var otherArgs = Array(start + 1); ++index < start; ) otherArgs[index] = args[index];
   return otherArgs[start] = transform(array), _apply(func, this, otherArgs);
  };
 };
 const lodash_es_constant = function(value) {
  return function() {
   return value;
  };
 };
 const _freeGlobal = "object" == typeof global && global && global.Object === Object && global;
 var freeSelf = "object" == typeof self && self && self.Object === Object && self;
 const _root = _freeGlobal || freeSelf || Function("return this")();
 const _Symbol = _root.Symbol;
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
 };
 const _coreJsData = _root["__core-js_shared__"];
 var uid, maskSrcKey = (uid = /[^.]+$/.exec(_coreJsData && _coreJsData.keys && _coreJsData.keys.IE_PROTO || "")) ? "Symbol(src)_1." + uid : "";
 const _isMasked = function(func) {
  return !!maskSrcKey && maskSrcKey in func;
 };
 var funcToString = Function.prototype.toString;
 const _toSource = function(func) {
  if (null != func) {
   try {
    return funcToString.call(func);
   } catch (e) {}
   try {
    return func + "";
   } catch (e) {}
  }
  return "";
 };
 var reIsHostCtor = /^\[object .+?Constructor\]$/, _baseIsNative_funcProto = Function.prototype, _baseIsNative_objectProto = Object.prototype, _baseIsNative_funcToString = _baseIsNative_funcProto.toString, _baseIsNative_hasOwnProperty = _baseIsNative_objectProto.hasOwnProperty, reIsNative = RegExp("^" + _baseIsNative_funcToString.call(_baseIsNative_hasOwnProperty).replace(/[\\^$.*+?()[\]{}|]/g, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$");
 const _baseIsNative = function(value) {
  return !(!lodash_es_isObject(value) || _isMasked(value)) && (lodash_es_isFunction(value) ? reIsNative : reIsHostCtor).test(_toSource(value));
 };
 const _getValue = function(object, key) {
  return null == object ? void 0 : object[key];
 };
 const _getNative = function(object, key) {
  var value = _getValue(object, key);
  return _baseIsNative(value) ? value : void 0;
 };
 const _defineProperty = function() {
  try {
   var func = _getNative(Object, "defineProperty");
   return func({}, "", {}), func;
  } catch (e) {}
 }();
 const _baseSetToString = _defineProperty ? function(func, string) {
  return _defineProperty(func, "toString", {
   configurable: !0,
   enumerable: !1,
   value: lodash_es_constant(string),
   writable: !0
  });
 } : lodash_es_identity;
 var nativeNow = Date.now;
 const _setToString = function(func) {
  var count = 0, lastCalled = 0;
  return function() {
   var stamp = nativeNow(), remaining = 16 - (stamp - lastCalled);
   if (lastCalled = stamp, remaining > 0) {
    if (++count >= 800) return arguments[0];
   } else count = 0;
   return func.apply(void 0, arguments);
  };
 }(_baseSetToString);
 var reWhitespace = /\s/;
 const _trimmedEndIndex = function(string) {
  for (var index = string.length; index-- && reWhitespace.test(string.charAt(index)); ) ;
  return index;
 };
 var reTrimStart = /^\s+/;
 const _baseTrim = function(string) {
  return string ? string.slice(0, _trimmedEndIndex(string) + 1).replace(reTrimStart, "") : string;
 };
 const lodash_es_isObjectLike = function(value) {
  return null != value && "object" == typeof value;
 };
 const lodash_es_isSymbol = function(value) {
  return "symbol" == typeof value || lodash_es_isObjectLike(value) && "[object Symbol]" == _baseGetTag(value);
 };
 var reIsBadHex = /^[-+]0x[0-9a-f]+$/i, reIsBinary = /^0b[01]+$/i, reIsOctal = /^0o[0-7]+$/i, freeParseInt = parseInt;
 const lodash_es_toNumber = function(value) {
  if ("number" == typeof value) return value;
  if (lodash_es_isSymbol(value)) return NaN;
  if (lodash_es_isObject(value)) {
   var other = "function" == typeof value.valueOf ? value.valueOf() : value;
   value = lodash_es_isObject(other) ? other + "" : other;
  }
  if ("string" != typeof value) return 0 === value ? value : +value;
  value = _baseTrim(value);
  var isBinary = reIsBinary.test(value);
  return isBinary || reIsOctal.test(value) ? freeParseInt(value.slice(2), isBinary ? 2 : 8) : reIsBadHex.test(value) ? NaN : +value;
 };
 const lodash_es_delay = function(func, start) {
  return _setToString(_overRest(func, start, lodash_es_identity), func + "");
 }((function(func, wait, args) {
  return _baseDelay(func, lodash_es_toNumber(wait) || 0, args);
 }));
 function hours(h) {
  return h * minutes(60);
 }
 function minutes(m) {
  return m * seconds(60);
 }
 function seconds(s) {
  return 1e3 * s;
 }
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
 const playFor = (duration, audio) => {
  lodash_es_delay((_ => function(audio) {
   audio.currentTime = hours(99999);
  }(audio)), duration), audio.play();
 };
 chrome.runtime.onMessage.addListener((function(message) {
  if ("offscreen" === message.target && "play-audio" === message.id) {
   console.log(JSON.stringify(message.data));
   let audio = new Audio;
   audio.src = message.data.src, audio.volume = message.data.volume, playFor(seconds(3), audio);
  }
 })), setInterval((async () => {
  (await navigator.serviceWorker.ready).active.postMessage("keep-alive");
 }), 2e4);
})();