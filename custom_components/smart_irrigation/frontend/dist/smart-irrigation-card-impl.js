!function (e) {
  "use strict";

  var t = function (e, i) {
    return t = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (e, t) {
      e.__proto__ = t;
    } || function (e, t) {
      for (var i in t) Object.prototype.hasOwnProperty.call(t, i) && (e[i] = t[i]);
    }, t(e, i);
  };
  function i(e, i) {
    if ("function" != typeof i && null !== i) throw new TypeError("Class extends value " + String(i) + " is not a constructor or null");
    function r() {
      this.constructor = e;
    }
    t(e, i), e.prototype = null === i ? Object.create(i) : (r.prototype = i.prototype, new r());
  }
  var r = function () {
    return r = Object.assign || function (e) {
      for (var t, i = 1, r = arguments.length; i < r; i++) for (var n in t = arguments[i]) Object.prototype.hasOwnProperty.call(t, n) && (e[n] = t[n]);
      return e;
    }, r.apply(this, arguments);
  };
  function n(e, t, i, r) {
    var n,
      o = arguments.length,
      a = o < 3 ? t : null === r ? r = Object.getOwnPropertyDescriptor(t, i) : r;
    if ("object" == typeof Reflect && "function" == typeof Reflect.decorate) a = Reflect.decorate(e, t, i, r);else for (var s = e.length - 1; s >= 0; s--) (n = e[s]) && (a = (o < 3 ? n(a) : o > 3 ? n(t, i, a) : n(t, i)) || a);
    return o > 3 && a && Object.defineProperty(t, i, a), a;
  }
  function o(e, t, i) {
    if (i || 2 === arguments.length) for (var r, n = 0, o = t.length; n < o; n++) !r && n in t || (r || (r = Array.prototype.slice.call(t, 0, n)), r[n] = t[n]);
    return e.concat(r || Array.prototype.slice.call(t));
  }
  "function" == typeof SuppressedError && SuppressedError;
  /**
       * @license
       * Copyright 2019 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  const a = window,
    s = a.ShadowRoot && (void 0 === a.ShadyCSS || a.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype,
    l = Symbol(),
    c = new WeakMap();
  class h {
    constructor(e, t, i) {
      if (this._$cssResult$ = !0, i !== l) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
      this.cssText = e, this.t = t;
    }
    get styleSheet() {
      let e = this.o;
      const t = this.t;
      if (s && void 0 === e) {
        const i = void 0 !== t && 1 === t.length;
        i && (e = c.get(t)), void 0 === e && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), i && c.set(t, e));
      }
      return e;
    }
    toString() {
      return this.cssText;
    }
  }
  const u = (e, ...t) => {
      const i = 1 === e.length ? e[0] : t.reduce((t, i, r) => t + (e => {
        if (!0 === e._$cssResult$) return e.cssText;
        if ("number" == typeof e) return e;
        throw Error("Value passed to 'css' function must be a 'css' function result: " + e + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
      })(i) + e[r + 1], e[0]);
      return new h(i, e, l);
    },
    d = s ? e => e : e => e instanceof CSSStyleSheet ? (e => {
      let t = "";
      for (const i of e.cssRules) t += i.cssText;
      return (e => new h("string" == typeof e ? e : e + "", void 0, l))(t);
    })(e) : e
    /**
         * @license
         * Copyright 2017 Google LLC
         * SPDX-License-Identifier: BSD-3-Clause
         */;
  var p;
  const g = window,
    m = g.trustedTypes,
    f = m ? m.emptyScript : "",
    b = g.reactiveElementPolyfillSupport,
    v = {
      toAttribute(e, t) {
        switch (t) {
          case Boolean:
            e = e ? f : null;
            break;
          case Object:
          case Array:
            e = null == e ? e : JSON.stringify(e);
        }
        return e;
      },
      fromAttribute(e, t) {
        let i = e;
        switch (t) {
          case Boolean:
            i = null !== e;
            break;
          case Number:
            i = null === e ? null : Number(e);
            break;
          case Object:
          case Array:
            try {
              i = JSON.parse(e);
            } catch (e) {
              i = null;
            }
        }
        return i;
      }
    },
    _ = (e, t) => t !== e && (t == t || e == e),
    y = {
      attribute: !0,
      type: String,
      converter: v,
      reflect: !1,
      hasChanged: _
    },
    w = "finalized";
  class E extends HTMLElement {
    constructor() {
      super(), this._$Ei = new Map(), this.isUpdatePending = !1, this.hasUpdated = !1, this._$El = null, this._$Eu();
    }
    static addInitializer(e) {
      var t;
      this.finalize(), (null !== (t = this.h) && void 0 !== t ? t : this.h = []).push(e);
    }
    static get observedAttributes() {
      this.finalize();
      const e = [];
      return this.elementProperties.forEach((t, i) => {
        const r = this._$Ep(i, t);
        void 0 !== r && (this._$Ev.set(r, i), e.push(r));
      }), e;
    }
    static createProperty(e, t = y) {
      if (t.state && (t.attribute = !1), this.finalize(), this.elementProperties.set(e, t), !t.noAccessor && !this.prototype.hasOwnProperty(e)) {
        const i = "symbol" == typeof e ? Symbol() : "__" + e,
          r = this.getPropertyDescriptor(e, i, t);
        void 0 !== r && Object.defineProperty(this.prototype, e, r);
      }
    }
    static getPropertyDescriptor(e, t, i) {
      return {
        get() {
          return this[t];
        },
        set(r) {
          const n = this[e];
          this[t] = r, this.requestUpdate(e, n, i);
        },
        configurable: !0,
        enumerable: !0
      };
    }
    static getPropertyOptions(e) {
      return this.elementProperties.get(e) || y;
    }
    static finalize() {
      if (this.hasOwnProperty(w)) return !1;
      this[w] = !0;
      const e = Object.getPrototypeOf(this);
      if (e.finalize(), void 0 !== e.h && (this.h = [...e.h]), this.elementProperties = new Map(e.elementProperties), this._$Ev = new Map(), this.hasOwnProperty("properties")) {
        const e = this.properties,
          t = [...Object.getOwnPropertyNames(e), ...Object.getOwnPropertySymbols(e)];
        for (const i of t) this.createProperty(i, e[i]);
      }
      return this.elementStyles = this.finalizeStyles(this.styles), !0;
    }
    static finalizeStyles(e) {
      const t = [];
      if (Array.isArray(e)) {
        const i = new Set(e.flat(1 / 0).reverse());
        for (const e of i) t.unshift(d(e));
      } else void 0 !== e && t.push(d(e));
      return t;
    }
    static _$Ep(e, t) {
      const i = t.attribute;
      return !1 === i ? void 0 : "string" == typeof i ? i : "string" == typeof e ? e.toLowerCase() : void 0;
    }
    _$Eu() {
      var e;
      this._$E_ = new Promise(e => this.enableUpdating = e), this._$AL = new Map(), this._$Eg(), this.requestUpdate(), null === (e = this.constructor.h) || void 0 === e || e.forEach(e => e(this));
    }
    addController(e) {
      var t, i;
      (null !== (t = this._$ES) && void 0 !== t ? t : this._$ES = []).push(e), void 0 !== this.renderRoot && this.isConnected && (null === (i = e.hostConnected) || void 0 === i || i.call(e));
    }
    removeController(e) {
      var t;
      null === (t = this._$ES) || void 0 === t || t.splice(this._$ES.indexOf(e) >>> 0, 1);
    }
    _$Eg() {
      this.constructor.elementProperties.forEach((e, t) => {
        this.hasOwnProperty(t) && (this._$Ei.set(t, this[t]), delete this[t]);
      });
    }
    createRenderRoot() {
      var e;
      const t = null !== (e = this.shadowRoot) && void 0 !== e ? e : this.attachShadow(this.constructor.shadowRootOptions);
      return ((e, t) => {
        s ? e.adoptedStyleSheets = t.map(e => e instanceof CSSStyleSheet ? e : e.styleSheet) : t.forEach(t => {
          const i = document.createElement("style"),
            r = a.litNonce;
          void 0 !== r && i.setAttribute("nonce", r), i.textContent = t.cssText, e.appendChild(i);
        });
      })(t, this.constructor.elementStyles), t;
    }
    connectedCallback() {
      var e;
      void 0 === this.renderRoot && (this.renderRoot = this.createRenderRoot()), this.enableUpdating(!0), null === (e = this._$ES) || void 0 === e || e.forEach(e => {
        var t;
        return null === (t = e.hostConnected) || void 0 === t ? void 0 : t.call(e);
      });
    }
    enableUpdating(e) {}
    disconnectedCallback() {
      var e;
      null === (e = this._$ES) || void 0 === e || e.forEach(e => {
        var t;
        return null === (t = e.hostDisconnected) || void 0 === t ? void 0 : t.call(e);
      });
    }
    attributeChangedCallback(e, t, i) {
      this._$AK(e, i);
    }
    _$EO(e, t, i = y) {
      var r;
      const n = this.constructor._$Ep(e, i);
      if (void 0 !== n && !0 === i.reflect) {
        const o = (void 0 !== (null === (r = i.converter) || void 0 === r ? void 0 : r.toAttribute) ? i.converter : v).toAttribute(t, i.type);
        this._$El = e, null == o ? this.removeAttribute(n) : this.setAttribute(n, o), this._$El = null;
      }
    }
    _$AK(e, t) {
      var i;
      const r = this.constructor,
        n = r._$Ev.get(e);
      if (void 0 !== n && this._$El !== n) {
        const e = r.getPropertyOptions(n),
          o = "function" == typeof e.converter ? {
            fromAttribute: e.converter
          } : void 0 !== (null === (i = e.converter) || void 0 === i ? void 0 : i.fromAttribute) ? e.converter : v;
        this._$El = n, this[n] = o.fromAttribute(t, e.type), this._$El = null;
      }
    }
    requestUpdate(e, t, i) {
      let r = !0;
      void 0 !== e && (((i = i || this.constructor.getPropertyOptions(e)).hasChanged || _)(this[e], t) ? (this._$AL.has(e) || this._$AL.set(e, t), !0 === i.reflect && this._$El !== e && (void 0 === this._$EC && (this._$EC = new Map()), this._$EC.set(e, i))) : r = !1), !this.isUpdatePending && r && (this._$E_ = this._$Ej());
    }
    async _$Ej() {
      this.isUpdatePending = !0;
      try {
        await this._$E_;
      } catch (e) {
        Promise.reject(e);
      }
      const e = this.scheduleUpdate();
      return null != e && (await e), !this.isUpdatePending;
    }
    scheduleUpdate() {
      return this.performUpdate();
    }
    performUpdate() {
      var e;
      if (!this.isUpdatePending) return;
      this.hasUpdated, this._$Ei && (this._$Ei.forEach((e, t) => this[t] = e), this._$Ei = void 0);
      let t = !1;
      const i = this._$AL;
      try {
        t = this.shouldUpdate(i), t ? (this.willUpdate(i), null === (e = this._$ES) || void 0 === e || e.forEach(e => {
          var t;
          return null === (t = e.hostUpdate) || void 0 === t ? void 0 : t.call(e);
        }), this.update(i)) : this._$Ek();
      } catch (e) {
        throw t = !1, this._$Ek(), e;
      }
      t && this._$AE(i);
    }
    willUpdate(e) {}
    _$AE(e) {
      var t;
      null === (t = this._$ES) || void 0 === t || t.forEach(e => {
        var t;
        return null === (t = e.hostUpdated) || void 0 === t ? void 0 : t.call(e);
      }), this.hasUpdated || (this.hasUpdated = !0, this.firstUpdated(e)), this.updated(e);
    }
    _$Ek() {
      this._$AL = new Map(), this.isUpdatePending = !1;
    }
    get updateComplete() {
      return this.getUpdateComplete();
    }
    getUpdateComplete() {
      return this._$E_;
    }
    shouldUpdate(e) {
      return !0;
    }
    update(e) {
      void 0 !== this._$EC && (this._$EC.forEach((e, t) => this._$EO(t, this[t], e)), this._$EC = void 0), this._$Ek();
    }
    updated(e) {}
    firstUpdated(e) {}
  }
  /**
       * @license
       * Copyright 2017 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  var k;
  E[w] = !0, E.elementProperties = new Map(), E.elementStyles = [], E.shadowRootOptions = {
    mode: "open"
  }, null == b || b({
    ReactiveElement: E
  }), (null !== (p = g.reactiveElementVersions) && void 0 !== p ? p : g.reactiveElementVersions = []).push("1.6.3");
  const A = window,
    x = A.trustedTypes,
    S = x ? x.createPolicy("lit-html", {
      createHTML: e => e
    }) : void 0,
    T = "$lit$",
    $ = `lit$${(Math.random() + "").slice(9)}$`,
    H = "?" + $,
    z = `<${H}>`,
    C = document,
    L = () => C.createComment(""),
    B = e => null === e || "object" != typeof e && "function" != typeof e,
    P = Array.isArray,
    N = "[ \t\n\f\r]",
    I = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,
    M = /-->/g,
    R = />/g,
    O = RegExp(`>|${N}(?:([^\\s"'>=/]+)(${N}*=${N}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`, "g"),
    U = /'/g,
    D = /"/g,
    G = /^(?:script|style|textarea|title)$/i,
    F = (e => (t, ...i) => ({
      _$litType$: e,
      strings: t,
      values: i
    }))(1),
    W = Symbol.for("lit-noChange"),
    Z = Symbol.for("lit-nothing"),
    j = new WeakMap(),
    V = C.createTreeWalker(C, 129, null, !1);
  function X(e, t) {
    if (!Array.isArray(e) || !e.hasOwnProperty("raw")) throw Error("invalid template strings array");
    return void 0 !== S ? S.createHTML(t) : t;
  }
  const K = (e, t) => {
    const i = e.length - 1,
      r = [];
    let n,
      o = 2 === t ? "<svg>" : "",
      a = I;
    for (let t = 0; t < i; t++) {
      const i = e[t];
      let s,
        l,
        c = -1,
        h = 0;
      for (; h < i.length && (a.lastIndex = h, l = a.exec(i), null !== l);) h = a.lastIndex, a === I ? "!--" === l[1] ? a = M : void 0 !== l[1] ? a = R : void 0 !== l[2] ? (G.test(l[2]) && (n = RegExp("</" + l[2], "g")), a = O) : void 0 !== l[3] && (a = O) : a === O ? ">" === l[0] ? (a = null != n ? n : I, c = -1) : void 0 === l[1] ? c = -2 : (c = a.lastIndex - l[2].length, s = l[1], a = void 0 === l[3] ? O : '"' === l[3] ? D : U) : a === D || a === U ? a = O : a === M || a === R ? a = I : (a = O, n = void 0);
      const u = a === O && e[t + 1].startsWith("/>") ? " " : "";
      o += a === I ? i + z : c >= 0 ? (r.push(s), i.slice(0, c) + T + i.slice(c) + $ + u) : i + $ + (-2 === c ? (r.push(void 0), t) : u);
    }
    return [X(e, o + (e[i] || "<?>") + (2 === t ? "</svg>" : "")), r];
  };
  class Y {
    constructor({
      strings: e,
      _$litType$: t
    }, i) {
      let r;
      this.parts = [];
      let n = 0,
        o = 0;
      const a = e.length - 1,
        s = this.parts,
        [l, c] = K(e, t);
      if (this.el = Y.createElement(l, i), V.currentNode = this.el.content, 2 === t) {
        const e = this.el.content,
          t = e.firstChild;
        t.remove(), e.append(...t.childNodes);
      }
      for (; null !== (r = V.nextNode()) && s.length < a;) {
        if (1 === r.nodeType) {
          if (r.hasAttributes()) {
            const e = [];
            for (const t of r.getAttributeNames()) if (t.endsWith(T) || t.startsWith($)) {
              const i = c[o++];
              if (e.push(t), void 0 !== i) {
                const e = r.getAttribute(i.toLowerCase() + T).split($),
                  t = /([.?@])?(.*)/.exec(i);
                s.push({
                  type: 1,
                  index: n,
                  name: t[2],
                  strings: e,
                  ctor: "." === t[1] ? te : "?" === t[1] ? re : "@" === t[1] ? ne : ee
                });
              } else s.push({
                type: 6,
                index: n
              });
            }
            for (const t of e) r.removeAttribute(t);
          }
          if (G.test(r.tagName)) {
            const e = r.textContent.split($),
              t = e.length - 1;
            if (t > 0) {
              r.textContent = x ? x.emptyScript : "";
              for (let i = 0; i < t; i++) r.append(e[i], L()), V.nextNode(), s.push({
                type: 2,
                index: ++n
              });
              r.append(e[t], L());
            }
          }
        } else if (8 === r.nodeType) if (r.data === H) s.push({
          type: 2,
          index: n
        });else {
          let e = -1;
          for (; -1 !== (e = r.data.indexOf($, e + 1));) s.push({
            type: 7,
            index: n
          }), e += $.length - 1;
        }
        n++;
      }
    }
    static createElement(e, t) {
      const i = C.createElement("template");
      return i.innerHTML = e, i;
    }
  }
  function q(e, t, i = e, r) {
    var n, o, a, s;
    if (t === W) return t;
    let l = void 0 !== r ? null === (n = i._$Co) || void 0 === n ? void 0 : n[r] : i._$Cl;
    const c = B(t) ? void 0 : t._$litDirective$;
    return (null == l ? void 0 : l.constructor) !== c && (null === (o = null == l ? void 0 : l._$AO) || void 0 === o || o.call(l, !1), void 0 === c ? l = void 0 : (l = new c(e), l._$AT(e, i, r)), void 0 !== r ? (null !== (a = (s = i)._$Co) && void 0 !== a ? a : s._$Co = [])[r] = l : i._$Cl = l), void 0 !== l && (t = q(e, l._$AS(e, t.values), l, r)), t;
  }
  class J {
    constructor(e, t) {
      this._$AV = [], this._$AN = void 0, this._$AD = e, this._$AM = t;
    }
    get parentNode() {
      return this._$AM.parentNode;
    }
    get _$AU() {
      return this._$AM._$AU;
    }
    u(e) {
      var t;
      const {
          el: {
            content: i
          },
          parts: r
        } = this._$AD,
        n = (null !== (t = null == e ? void 0 : e.creationScope) && void 0 !== t ? t : C).importNode(i, !0);
      V.currentNode = n;
      let o = V.nextNode(),
        a = 0,
        s = 0,
        l = r[0];
      for (; void 0 !== l;) {
        if (a === l.index) {
          let t;
          2 === l.type ? t = new Q(o, o.nextSibling, this, e) : 1 === l.type ? t = new l.ctor(o, l.name, l.strings, this, e) : 6 === l.type && (t = new oe(o, this, e)), this._$AV.push(t), l = r[++s];
        }
        a !== (null == l ? void 0 : l.index) && (o = V.nextNode(), a++);
      }
      return V.currentNode = C, n;
    }
    v(e) {
      let t = 0;
      for (const i of this._$AV) void 0 !== i && (void 0 !== i.strings ? (i._$AI(e, i, t), t += i.strings.length - 2) : i._$AI(e[t])), t++;
    }
  }
  class Q {
    constructor(e, t, i, r) {
      var n;
      this.type = 2, this._$AH = Z, this._$AN = void 0, this._$AA = e, this._$AB = t, this._$AM = i, this.options = r, this._$Cp = null === (n = null == r ? void 0 : r.isConnected) || void 0 === n || n;
    }
    get _$AU() {
      var e, t;
      return null !== (t = null === (e = this._$AM) || void 0 === e ? void 0 : e._$AU) && void 0 !== t ? t : this._$Cp;
    }
    get parentNode() {
      let e = this._$AA.parentNode;
      const t = this._$AM;
      return void 0 !== t && 11 === (null == e ? void 0 : e.nodeType) && (e = t.parentNode), e;
    }
    get startNode() {
      return this._$AA;
    }
    get endNode() {
      return this._$AB;
    }
    _$AI(e, t = this) {
      e = q(this, e, t), B(e) ? e === Z || null == e || "" === e ? (this._$AH !== Z && this._$AR(), this._$AH = Z) : e !== this._$AH && e !== W && this._(e) : void 0 !== e._$litType$ ? this.g(e) : void 0 !== e.nodeType ? this.$(e) : (e => P(e) || "function" == typeof (null == e ? void 0 : e[Symbol.iterator]))(e) ? this.T(e) : this._(e);
    }
    k(e) {
      return this._$AA.parentNode.insertBefore(e, this._$AB);
    }
    $(e) {
      this._$AH !== e && (this._$AR(), this._$AH = this.k(e));
    }
    _(e) {
      this._$AH !== Z && B(this._$AH) ? this._$AA.nextSibling.data = e : this.$(C.createTextNode(e)), this._$AH = e;
    }
    g(e) {
      var t;
      const {
          values: i,
          _$litType$: r
        } = e,
        n = "number" == typeof r ? this._$AC(e) : (void 0 === r.el && (r.el = Y.createElement(X(r.h, r.h[0]), this.options)), r);
      if ((null === (t = this._$AH) || void 0 === t ? void 0 : t._$AD) === n) this._$AH.v(i);else {
        const e = new J(n, this),
          t = e.u(this.options);
        e.v(i), this.$(t), this._$AH = e;
      }
    }
    _$AC(e) {
      let t = j.get(e.strings);
      return void 0 === t && j.set(e.strings, t = new Y(e)), t;
    }
    T(e) {
      P(this._$AH) || (this._$AH = [], this._$AR());
      const t = this._$AH;
      let i,
        r = 0;
      for (const n of e) r === t.length ? t.push(i = new Q(this.k(L()), this.k(L()), this, this.options)) : i = t[r], i._$AI(n), r++;
      r < t.length && (this._$AR(i && i._$AB.nextSibling, r), t.length = r);
    }
    _$AR(e = this._$AA.nextSibling, t) {
      var i;
      for (null === (i = this._$AP) || void 0 === i || i.call(this, !1, !0, t); e && e !== this._$AB;) {
        const t = e.nextSibling;
        e.remove(), e = t;
      }
    }
    setConnected(e) {
      var t;
      void 0 === this._$AM && (this._$Cp = e, null === (t = this._$AP) || void 0 === t || t.call(this, e));
    }
  }
  class ee {
    constructor(e, t, i, r, n) {
      this.type = 1, this._$AH = Z, this._$AN = void 0, this.element = e, this.name = t, this._$AM = r, this.options = n, i.length > 2 || "" !== i[0] || "" !== i[1] ? (this._$AH = Array(i.length - 1).fill(new String()), this.strings = i) : this._$AH = Z;
    }
    get tagName() {
      return this.element.tagName;
    }
    get _$AU() {
      return this._$AM._$AU;
    }
    _$AI(e, t = this, i, r) {
      const n = this.strings;
      let o = !1;
      if (void 0 === n) e = q(this, e, t, 0), o = !B(e) || e !== this._$AH && e !== W, o && (this._$AH = e);else {
        const r = e;
        let a, s;
        for (e = n[0], a = 0; a < n.length - 1; a++) s = q(this, r[i + a], t, a), s === W && (s = this._$AH[a]), o || (o = !B(s) || s !== this._$AH[a]), s === Z ? e = Z : e !== Z && (e += (null != s ? s : "") + n[a + 1]), this._$AH[a] = s;
      }
      o && !r && this.j(e);
    }
    j(e) {
      e === Z ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, null != e ? e : "");
    }
  }
  class te extends ee {
    constructor() {
      super(...arguments), this.type = 3;
    }
    j(e) {
      this.element[this.name] = e === Z ? void 0 : e;
    }
  }
  const ie = x ? x.emptyScript : "";
  class re extends ee {
    constructor() {
      super(...arguments), this.type = 4;
    }
    j(e) {
      e && e !== Z ? this.element.setAttribute(this.name, ie) : this.element.removeAttribute(this.name);
    }
  }
  class ne extends ee {
    constructor(e, t, i, r, n) {
      super(e, t, i, r, n), this.type = 5;
    }
    _$AI(e, t = this) {
      var i;
      if ((e = null !== (i = q(this, e, t, 0)) && void 0 !== i ? i : Z) === W) return;
      const r = this._$AH,
        n = e === Z && r !== Z || e.capture !== r.capture || e.once !== r.once || e.passive !== r.passive,
        o = e !== Z && (r === Z || n);
      n && this.element.removeEventListener(this.name, this, r), o && this.element.addEventListener(this.name, this, e), this._$AH = e;
    }
    handleEvent(e) {
      var t, i;
      "function" == typeof this._$AH ? this._$AH.call(null !== (i = null === (t = this.options) || void 0 === t ? void 0 : t.host) && void 0 !== i ? i : this.element, e) : this._$AH.handleEvent(e);
    }
  }
  class oe {
    constructor(e, t, i) {
      this.element = e, this.type = 6, this._$AN = void 0, this._$AM = t, this.options = i;
    }
    get _$AU() {
      return this._$AM._$AU;
    }
    _$AI(e) {
      q(this, e);
    }
  }
  const ae = A.litHtmlPolyfillSupport;
  null == ae || ae(Y, Q), (null !== (k = A.litHtmlVersions) && void 0 !== k ? k : A.litHtmlVersions = []).push("2.8.0");
  /**
       * @license
       * Copyright 2017 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  var se, le;
  class ce extends E {
    constructor() {
      super(...arguments), this.renderOptions = {
        host: this
      }, this._$Do = void 0;
    }
    createRenderRoot() {
      var e, t;
      const i = super.createRenderRoot();
      return null !== (e = (t = this.renderOptions).renderBefore) && void 0 !== e || (t.renderBefore = i.firstChild), i;
    }
    update(e) {
      const t = this.render();
      this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(e), this._$Do = ((e, t, i) => {
        var r, n;
        const o = null !== (r = null == i ? void 0 : i.renderBefore) && void 0 !== r ? r : t;
        let a = o._$litPart$;
        if (void 0 === a) {
          const e = null !== (n = null == i ? void 0 : i.renderBefore) && void 0 !== n ? n : null;
          o._$litPart$ = a = new Q(t.insertBefore(L(), e), e, void 0, null != i ? i : {});
        }
        return a._$AI(e), a;
      })(t, this.renderRoot, this.renderOptions);
    }
    connectedCallback() {
      var e;
      super.connectedCallback(), null === (e = this._$Do) || void 0 === e || e.setConnected(!0);
    }
    disconnectedCallback() {
      var e;
      super.disconnectedCallback(), null === (e = this._$Do) || void 0 === e || e.setConnected(!1);
    }
    render() {
      return W;
    }
  }
  ce.finalized = !0, ce._$litElement$ = !0, null === (se = globalThis.litElementHydrateSupport) || void 0 === se || se.call(globalThis, {
    LitElement: ce
  });
  const he = globalThis.litElementPolyfillSupport;
  null == he || he({
    LitElement: ce
  }), (null !== (le = globalThis.litElementVersions) && void 0 !== le ? le : globalThis.litElementVersions = []).push("3.3.3");
  /**
       * @license
       * Copyright 2017 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  const ue = (e, t) => "method" === t.kind && t.descriptor && !("value" in t.descriptor) ? {
    ...t,
    finisher(i) {
      i.createProperty(t.key, e);
    }
  } : {
    kind: "field",
    key: Symbol(),
    placement: "own",
    descriptor: {},
    originalKey: t.key,
    initializer() {
      "function" == typeof t.initializer && (this[t.key] = t.initializer.call(this));
    },
    finisher(i) {
      i.createProperty(t.key, e);
    }
  };
  function de(e) {
    return (t, i) => void 0 !== i ? ((e, t, i) => {
      t.constructor.createProperty(i, e);
    })(e, t, i) : ue(e, t);
    /**
         * @license
         * Copyright 2017 Google LLC
         * SPDX-License-Identifier: BSD-3-Clause
         */
  }
  function pe(e) {
    return de({
      ...e,
      state: !0
    });
  }
  /**
       * @license
       * Copyright 2021 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  var ge;
  null === (ge = window.HTMLSlotElement) || void 0 === ge || ge.prototype.assignedElements;
  let me = !1,
    fe = null;
  const be = async () => {
    if (me && fe) return fe;
    if (customElements.get("ha-checkbox") && customElements.get("ha-slider") && customElements.get("ha-panel-config") && customElements.get("ha-entity-picker")) return Promise.resolve();
    me = !0, fe = async function () {
      try {
        await new Promise(e => {
          "requestIdleCallback" in window ? requestIdleCallback(() => e()) : setTimeout(() => e(), 0);
        }), await customElements.whenDefined("partial-panel-resolver");
        const e = document.createDocumentFragment(),
          t = document.createElement("partial-panel-resolver");
        e.appendChild(t), t.hass = {
          panels: [{
            url_path: "tmp",
            component_name: "config"
          }]
        }, await new Promise(e => queueMicrotask(() => e())), t._updateRoutes(), await t.routerOptions.routes.tmp.load(), await customElements.whenDefined("ha-panel-config"), await new Promise(e => queueMicrotask(() => e()));
        const i = document.createElement("ha-panel-config");
        e.appendChild(i), await i.routerOptions.routes.automation.load(), customElements.get("ha-entity-picker") || (await Promise.race([customElements.whenDefined("ha-entity-picker"), new Promise(e => setTimeout(e, 3e3))])), e.textContent = "";
      } catch (e) {
        console.error("Failed to load HA form elements:", e);
      }
    }();
    try {
      await fe;
    } finally {
      me = !1, fe = null;
    }
  };
  const ve = "smart_irrigation",
    _e = ["de", "en", "es", "fr", "it", "nl", "no", "sk"],
    ye = "metric",
    we = "bucket",
    Ee = e => e.callWS({
      type: ve + "/zones"
    }),
    ke = e => e.callWS({
      type: ve + "/irrigation_outlook"
    }),
    Ae = e => {
      class t extends e {
        connectedCallback() {
          super.connectedCallback(), this.__checkSubscribed();
        }
        disconnectedCallback() {
          if (super.disconnectedCallback(), this.__unsubs) {
            for (; this.__unsubs.length;) {
              const e = this.__unsubs.pop();
              e instanceof Promise ? e.then(e => e()) : e();
            }
            this.__unsubs = void 0;
          }
        }
        updated(e) {
          super.updated(e), e.has("hass") && this.__checkSubscribed();
        }
        hassSubscribe() {
          return [];
        }
        __checkSubscribed() {
          void 0 === this.__unsubs && this.isConnected && void 0 !== this.hass && (this.__unsubs = this.hassSubscribe());
        }
      }
      return n([de({
        attribute: !1
      })], t.prototype, "hass", void 0), t;
    };
  var xe, Se;
  !function (e) {
    e.Sunrise = "sunrise", e.Sunset = "sunset", e.SolarAzimuth = "solar_azimuth";
  }(xe || (xe = {})), function (e) {
    e.Disabled = "disabled", e.Manual = "manual", e.Automatic = "automatic";
  }(Se || (Se = {}));
  /**
       * @license
       * Copyright 2017 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  const Te = 2;
  class $e {
    constructor(e) {}
    get _$AU() {
      return this._$AM._$AU;
    }
    _$AT(e, t, i) {
      this._$Ct = e, this._$AM = t, this._$Ci = i;
    }
    _$AS(e, t) {
      return this.update(e, t);
    }
    update(e, t) {
      return this.render(...t);
    }
  }
  /**
       * @license
       * Copyright 2017 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  class He extends $e {
    constructor(e) {
      if (super(e), this.et = Z, e.type !== Te) throw Error(this.constructor.directiveName + "() can only be used in child bindings");
    }
    render(e) {
      if (e === Z || null == e) return this.ft = void 0, this.et = e;
      if (e === W) return e;
      if ("string" != typeof e) throw Error(this.constructor.directiveName + "() called with a non-string value");
      if (e === this.et) return this.ft;
      this.et = e;
      const t = [e];
      return t.raw = t, this.ft = {
        _$litType$: this.constructor.resultType,
        strings: t,
        values: []
      };
    }
  }
  He.directiveName = "unsafeHTML", He.resultType = 1;
  const ze = (e => (...t) => ({
    _$litDirective$: e,
    values: t
  }))(He);
  var Ce = {
      loading: "Loading",
      saving: "Saving",
      actions: {
        delete: "Delete",
        edit: "Edit",
        save: "Save",
        cancel: "Cancel",
        confirm_delete: "Confirm Delete",
        confirm_delete_zone: "Are you sure you want to delete this zone?"
      },
      labels: {
        module: "Module",
        no: "No",
        select: "Select",
        yes: "Yes",
        enabled: "Enabled",
        disabled: "Disabled",
        before: "before",
        after: "after",
        settings: "Settings",
        bulk_actions: "Bulk Actions"
      },
      units: {
        seconds: "seconds"
      },
      attributes: {
        size: "size",
        throughput: "throughput",
        state: "state",
        bucket: "bucket",
        last_updated: "last updated",
        last_calculated: "last calculated",
        number_of_data_points: "number of data points"
      },
      "loading-messages": {
        configuration: "Loading configuration...",
        modules: "Loading modules...",
        general: "Loading..."
      },
      "saving-messages": {
        adding: "Adding...",
        saving: "Saving..."
      },
      errors: {
        load_failed: "Couldn't load data",
        save_failed: "Couldn't save changes",
        delete_failed: "Couldn't delete",
        action_failed: "Action failed"
      }
    },
    Le = {
      "default-zone": "Default zone",
      "default-mapping": "Default sensor group"
    },
    Be = {
      calculation: {
        explanation: {
          "module-returned-evapotranspiration-deficiency": "Note: this explanation uses '.' as decimal separator, shows rounded and metric values. Module returned Evapotranspiration deficiency ( = et0 * hour_multiplier + precipitation) of",
          "bucket-was": "Bucket was",
          "new-bucket-values-is": "New bucket value is",
          bucket: "bucket",
          "old-bucket-variable": "old_bucket",
          "max-bucket-variable": "max_bucket",
          delta: "delta",
          "bucket-less-than-zero-irrigation-necessary": "Since bucket < 0, irrigation is necessary",
          "steps-taken-to-calculate-duration": "To calculate the exact duration, the following steps were taken",
          "precipitation-rate-defined-as": "The precipitation rate is defined as",
          "duration-is-calculated-as": "The duration is calculated as",
          drainage: "drainage",
          "drainage-rate": "drainage_rate",
          hours: "hours",
          "precipitation-rate-variable": "precipitation_rate",
          "multiplier-is-applied": "Now, the multiplier is applied. The multiplier is",
          "duration-after-multiplier-is": "hence the duration is",
          "maximum-duration-is-applied": "Then, the maximum duration is applied. The maximum duration is",
          "duration-after-maximum-duration-is": "hence the duration is",
          "lead-time-is-applied": "Finally, the lead time is applied. The lead time is",
          "duration-after-lead-time-is": "hence the final duration is",
          "bucket-larger-than-or-equal-to-zero-no-irrigation-necessary": "Since bucket >= 0, no irrigation is necessary and duration is set to",
          "maximum-bucket-is": "Maximum bucket size is",
          "drainage-rate-is": "Drainage rate when saturated (bucket at max) is",
          "current-drainage-is": "Current drainage is calculated as",
          "no-drainage": "Current drainage is 0 because"
        }
      }
    },
    Pe = {
      pyeto: {
        description: "Calculate duration based on the FAO56 calculation from the PyETO library"
      },
      static: {
        description: "'Dummy' module with a static configurable delta"
      },
      passthrough: {
        description: "Passthrough module that returns the value of an Evapotranspiration sensor as delta"
      }
    },
    Ne = {
      general: {
        cards: {
          "automatic-duration-calculation": {
            header: "Automatic duration calculation",
            description: "Calculation takes collected weather data up to that point and updates the bucket for each automatic zone. Then, the duration is adjusted based on the new bucket value and the collected weather data is removed.",
            labels: {
              "auto-calc-enabled": "Automatically calculate irrigation durations",
              "calc-time": "Calculate at"
            }
          },
          "automatic-update": {
            errors: {
              "warning-update-time-on-or-after-calc-time": "Warning: weather data update time on or after calculation time"
            },
            header: "Automatic weather data update",
            description: "Collect and store weather data automatically. Weather data is required to calculate zone buckets and durations.",
            labels: {
              "auto-update-enabled": "Automatically update weather data",
              "auto-update-schedule": "Update schedule",
              "auto-update-time": "Update at",
              "auto-update-interval": "Update sensor data every",
              "auto-update-delay": "Update delay"
            },
            options: {
              minutes: "minutes",
              hours: "hours",
              days: "days"
            }
          },
          "automatic-clear": {
            header: "Automatic weather data pruning",
            description: "Automatically remove collected weather data at a configured time. Use this to make sure that there is no left over weather data from previous days. Don't remove the weather data before you calculate and only use this option if you expect the automatic update to collect weather data after you calculated for the day. Ideally, you want to prune as late in the day as possible.",
            labels: {
              "automatic-clear-enabled": "Automatically clear collected weather data",
              "automatic-clear-time": "Clear weather data at"
            }
          },
          continuousupdates: {
            header: "Continuous updates for sensors (experimental)",
            description: "This experimental feature will continuously update the sensor data. This is useful for sensor groups that use sources that provide continuous data, such as weather stations. This feature cannot be used for sensor groups that at least partly rely on weather services as continous polling of APIs will incur costs. Keep in mind that this is experimental and may not work as expected. Use at your own risk.",
            labels: {
              continuousupdates: "Enable continuous updates",
              sensor_debounce: "Sensor debounce"
            }
          }
        },
        description: "This page provides global settings.",
        title: "General",
        sections: {
          weather: "Weather",
          automation: "Automation",
          location: "Location",
          watering: "Watering behavior"
        }
      },
      schedules: {
        title: "Schedules",
        description: "Create recurring schedules to automatically calculate, update, or irrigate your zones. No automations needed.",
        add: "Add Schedule",
        no_items: "No schedules configured yet. Click 'Add Schedule' to get started.",
        zones_all: "All zones",
        zones_specific: "Specific zones",
        hours: "hours",
        minutes: "min",
        types: {
          daily: "Daily",
          weekly: "Weekly",
          monthly: "Monthly",
          interval: "Every N hours",
          sunrise: "Sunrise",
          sunset: "Sunset",
          solar_azimuth: "Solar azimuth"
        },
        actions: {
          calculate: "Calculate (update irrigation duration)",
          update: "Update (collect weather data)",
          irrigate: "Irrigate (run valves directly)"
        },
        days: {
          monday: "Mon",
          tuesday: "Tue",
          wednesday: "Wed",
          thursday: "Thu",
          friday: "Fri",
          saturday: "Sat",
          sunday: "Sun"
        },
        fields: {
          name: "Name",
          type: "Schedule type",
          enabled: "Enabled",
          time: "Time (HH:MM)",
          days_of_week: "Days of week",
          day_of_month: "Day of month",
          interval_hours: "Interval",
          action: "Action",
          zones: "Zones",
          start_date: "Start date (optional)",
          end_date: "End date (optional)",
          offset_minutes: "Offset from sunrise/sunset",
          account_for_duration: "Start early so irrigation finishes at trigger time",
          azimuth_angle: "Solar azimuth angle",
          time_anchor: "Time marks the"
        },
        dialog: {
          add_title: "Add Schedule",
          edit_title: "Edit Schedule"
        },
        time_anchor: {
          start: "Start of irrigation",
          finish: "End of irrigation"
        }
      },
      setup: {
        title: "Setup"
      },
      help: {
        title: "Help",
        cards: {
          "how-to-get-help": {
            title: "How to get help",
            "first-read-the": "First, read the",
            wiki: "Documentation",
            "if-you-still-need-help": "If you still need help reach out on the",
            "community-forum": "Community forum",
            "or-open-a": "or open a",
            "github-issue": "Github Issue",
            "english-only": "English only"
          }
        }
      },
      info: {
        title: "Info",
        description: "View information about next irrigation and system status.",
        "configuration-not-available": "Configuration not available.",
        cards: {
          "zone-bucket-values": {
            title: "Zone Bucket Values & Duration",
            labels: {
              bucket: "Bucket",
              duration: "Duration"
            },
            "no-zones": "No zones configured"
          },
          "next-irrigation": {
            title: "Next Irrigation",
            labels: {
              "next-start": "Next start",
              duration: "Duration",
              zones: "Zones"
            },
            "no-data": "No data available"
          },
          "irrigation-reason": {
            title: "Irrigation Reason",
            labels: {
              reason: "Reason",
              sunrise: "Sunrise",
              "total-duration": "Total duration",
              explanation: "Explanation"
            },
            "no-data": "No data available"
          },
          irrigate_now: {
            title: "Irrigate Now",
            description: "Immediately start irrigation for all zones that have a linked entity. Skip conditions are ignored.",
            button_all: "Run all zones now",
            no_linked_zones: "No zones have a linked switch/valve entity with a calculated duration."
          }
        }
      },
      mappings: {
        cards: {
          "add-mapping": {
            actions: {
              add: "Add sensor group"
            },
            header: "Add sensor groups"
          },
          mapping: {
            aggregates: {
              average: "Average",
              first: "First",
              last: "Last",
              maximum: "Maximum",
              median: "Median",
              minimum: "Minimum",
              riemannsum: "Riemann sum",
              sum: "Sum",
              delta: "Delta"
            },
            errors: {
              "cannot-delete-mapping-because-zones-use-it": "You cannot delete this sensor group because there is at least one zone using it.",
              invalid_source: "Invalid source",
              source_does_not_exist: "Source does not exist. Please enter a valid source, such as 'sensor.mysensor'."
            },
            items: {
              dewpoint: "Dewpoint",
              evapotranspiration: "Evapotranspiration",
              humidity: "Humidity",
              "maximum temperature": "Maximum temperature",
              "minimum temperature": "Minimum temperature",
              precipitation: "Total precipitation",
              "current precipitation": "Current precipitation",
              pressure: "Pressure",
              "solar radiation": "Solar radiation",
              temperature: "Temperature",
              windspeed: "Wind speed"
            },
            pressure_types: {
              absolute: "absolute",
              relative: "relative"
            },
            "pressure-type": "Pressure is",
            "sensor-aggregate-of-sensor-values-to-calculate": "of sensor values to calculate duration",
            "sensor-aggregate-use-the": "Use the",
            "sensor-entity": "Sensor entity",
            static_value: "Value",
            "input-units": "Input provides values in",
            source: "Source",
            sources: {
              none: "None",
              weather_service: "Weather service",
              sensor: "Sensor",
              static: "Static value"
            }
          }
        },
        description: "Add one or more sensor groups that retrieve weather data from Weather service, from sensors or a combination of these. You can map each sensor group to one or more zones",
        labels: {
          "mapping-name": "Name"
        },
        no_items: "There are no sensor group defined yet.",
        title: "Sensor Groups",
        "weather-records": {
          title: "Weather Records",
          timestamp: "Time",
          temperature: "Temp",
          humidity: "Hum",
          dewpoint: "Dew",
          wind: "Wind",
          pressure: "Press",
          precipitation: "Precip",
          "retrieval-time": "Retrieved",
          "no-data": "No weather data available for this sensor group"
        }
      },
      modules: {
        cards: {
          "add-module": {
            actions: {
              add: "Add module"
            },
            header: "Add module"
          },
          module: {
            errors: {
              "cannot-delete-module-because-zones-use-it": "You cannot delete this module because there is at least one zone using it."
            },
            labels: {
              configuration: "Configuration",
              required: "indicates a required field"
            },
            "translated-options": {
              DontEstimate: "Do not estimate",
              EstimateFromSunHours: "Estimate from sun hours",
              EstimateFromTemp: "Estimate from temperature",
              EstimateFromSunHoursAndTemperature: "Estimate from average of sun hours and temperature"
            }
          }
        },
        description: "Add one or more modules that calculate irrigation duration. Each module comes with its own configuration and can be used to calculate duration for one or more zones.",
        no_items: "There are no modules defined yet.",
        title: "Modules"
      },
      zones: {
        actions: {
          add: "Add",
          calculate: "Calculate",
          information: "Information",
          update: "Update",
          "reset-bucket": "Reset bucket",
          "view-weather-info": "View weather data",
          "view-weather-info-message": "Weather data available for",
          "view-watering-calendar": "View watering calendar",
          irrigate_all: "Water all zones now",
          open_settings: "Edit settings"
        },
        cards: {
          "add-zone": {
            actions: {
              add: "Add zone"
            },
            header: "Add zone"
          },
          "zone-actions": {
            actions: {
              "calculate-all": "Recalculate durations",
              "update-all": "Refresh weather data",
              "reset-all-buckets": "Reset all buckets",
              "clear-all-weatherdata": "Clear all weather data"
            },
            header: "Actions on all zones"
          }
        },
        description: "Specify one or more irrigation zones here. The irrigation duration is calculated per zone, depending on size, throughput, state, module and sensor group.",
        labels: {
          bucket: "Bucket",
          duration: "Duration",
          "lead-time": "Lead time",
          mapping: "Sensor Group",
          "maximum-duration": "Maximum duration",
          multiplier: "Multiplier",
          name: "Name",
          size: "Size",
          state: "State",
          states: {
            automatic: "Automatic",
            disabled: "Disabled",
            manual: "Manual"
          },
          throughput: "Throughput",
          "maximum-bucket": "Maximum bucket",
          last_calculated: "Last calculated",
          "data-last-updated": "Data last updated",
          "data-number-of-data-points": "Number of data points",
          drainage_rate: "Drainage rate",
          linked_entity: "Linked switch/valve entity",
          linked_entity_placeholder: "e.g. switch.garden_valve",
          flow_sensor: "Flow meter sensor (optional)",
          flow_sensor_placeholder: "e.g. sensor.zone_flow_rate",
          irrigate_now: "Irrigate Now",
          bucket_threshold: "Minimum deficit to irrigate"
        },
        no_items: "There are no zones defined yet.",
        title: "Zones",
        status: {
          decision_disabled: "Turned off — this zone won't be watered automatically.",
          decision_water: "Watering needed: about {duration} on the next scheduled run.",
          decision_water_at: "Will water about {duration} at {time}.",
          decision_water_skip: "Deficit ~{duration}, but the next run will likely be skipped ({reason}).",
          decision_water_no_schedule: "Deficit ~{duration} — no schedule waters this zone; trigger it manually.",
          decision_no_water: "No watering needed right now — the soil has enough moisture.",
          decision_unknown: "Not calculated yet — press Update, then Calculate to check.",
          last_checked: "Last checked",
          never: "never",
          saved: "Saved",
          estimate_now: "Now",
          estimate_tag: "est.",
          estimate_method: {
            hourly: "Live estimate from hourly weather since the last calculation",
            proxy: "Estimate distributed from today's forecast since the last calculation"
          }
        },
        help: {
          bucket: "Soil-moisture balance. A negative value means the soil is dry and the zone needs water.",
          calculate: "Works out how long to water from the latest data. Run this after Update.",
          update: "Fetches the latest weather/sensor data for this zone.",
          irrigate_link_entity: "Link a switch/valve in this zone's settings to enable manual watering.",
          irrigate_all: "Opens the linked valves now for every zone with a deficit. Skip conditions (rain, wind, temperature) are ignored.",
          update_all: "Collects the latest weather/sensor data for all zones. Does not change durations on its own.",
          calculate_all: "Recomputes each automatic zone's watering duration from the data collected so far."
        },
        outlook: {
          next_run: "Next run",
          no_schedule: "No automatic schedule — zones water only when you trigger them.",
          setup_schedule: "Set up a schedule",
          targets_all: "all zones",
          targets_zones: "{count} zones",
          will_skip: "Next run will likely be skipped",
          will_run: "Conditions look clear for the next run.",
          why_skipped: "Why?",
          provisional: "forecast — may change",
          active_guards: "Active guards",
          last_run: "Last run",
          last_run_skipped: "skipped",
          last_run_ran: "ran",
          today: "today",
          tomorrow: "tomorrow",
          actions: {
            irrigate: "Water",
            calculate: "Recalculate",
            update: "Refresh data"
          },
          checks: {
            precipitation: "Rain forecast",
            days_between: "Days between watering",
            temperature: "Low temperature",
            wind: "High wind",
            rain_sensor: "Rain sensor"
          },
          check_detail: {
            precipitation: "{observed} mm (≥ {threshold} mm)",
            days_between: "{observed}/{threshold} days",
            temperature: "{observed}° (below {threshold}°)",
            wind: "{observed} (above {threshold})",
            rain_sensor: "{observed}"
          }
        },
        calendar: {
          no_data: "No watering calendar data available for this zone.",
          error_prefix: "Error generating calendar:",
          month: "Month",
          et: "ET (mm)",
          precipitation: "Precipitation (mm)",
          watering: "Watering (L)",
          avg_temp: "Avg Temp (°C)",
          method_prefix: "Method:"
        },
        confirm_action: {
          reset_bucket_title: "Reset this zone's bucket?",
          reset_bucket_body: "This sets the bucket back to 0, discarding the accumulated moisture balance for this zone.",
          reset_all_buckets_title: "Reset all buckets?",
          reset_all_buckets_body: "This sets every zone's bucket back to 0, discarding the accumulated moisture balance. Watering calculations start fresh from the next update.",
          clear_weather_title: "Clear all weather data?",
          clear_weather_body: "This deletes all collected weather and sensor records for every zone. Zones will need fresh data before they can calculate again."
        },
        confirm_irrigate: {
          title: "Start irrigation?",
          body: "This opens the linked valve(s) now and bypasses all skip conditions (rain, temperature, minimum days between watering).",
          all_linked_zones: "All linked zones",
          toast_started: "Irrigation started",
          toast_failed: "Irrigation failed"
        }
      }
    },
    Ie = "Smart Irrigation",
    Me = {
      title: "Weather Service",
      description: "Configure which weather service to use for ET calculations and skip conditions.",
      enabled_label: "Enable weather service",
      service_label: "Weather service",
      api_key_label: "API key",
      api_key_placeholder: "Leave blank to keep existing key",
      api_key_configured: "API key is configured",
      api_key_not_configured: "No API key configured",
      api_key_help: "An API key from your chosen weather service provider. Open-Meteo does not require a key. OpenWeatherMap and Pirate Weather both offer free tiers.",
      no_api_key_needed: "Open-Meteo is a free service and requires no API key.",
      save_button: "Save weather settings",
      saved: "Weather settings saved",
      owm: "OpenWeatherMap",
      pw: "Pirate Weather",
      openmeteo: "Open-Meteo (free, no key needed)",
      test_button: "Test Connection",
      test_button_testing: "Testing…",
      test_success: "✓ Connection successful",
      test_error_invalid_auth: "✗ Invalid API key — check that it is correct and active",
      test_error_cannot_connect: "✗ Cannot connect — check your internet connection",
      test_error_no_service: "✗ Select a weather service first",
      test_error_unknown: "✗ Test failed — unknown error"
    },
    Re = {
      title: "Irrigation Start Triggers",
      description: "Configure when irrigation should start based on solar events. You can add multiple triggers for different schedules. For sunrise triggers, leaving offset at 0 will automatically use the total duration of all enabled zones.",
      add_trigger: "Add Trigger",
      edit_trigger: "Edit Trigger",
      delete_trigger: "Delete Trigger",
      trigger_types: {
        sunrise: "Sunrise",
        sunset: "Sunset",
        solar_azimuth: "Solar Azimuth"
      },
      fields: {
        name: {
          name: "Trigger Name",
          description: "A descriptive name to identify this trigger"
        },
        type: {
          name: "Trigger Type",
          description: "The type of solar event to trigger on"
        },
        enabled: {
          name: "Enabled",
          description: "Whether this trigger is currently active"
        },
        offset_minutes: {
          name: "Offset (minutes)",
          description: "Minutes before (-) or after (+) the solar event. For sunrise triggers, use 0 for automatic timing based on total zone duration."
        },
        azimuth_angle: {
          name: "Azimuth Angle (degrees)",
          description: "Solar azimuth angle in degrees where 0=North, 90=East, 180=South, 270=West"
        },
        account_for_duration: {
          name: "Account for Duration",
          description: "When enabled, irrigation will start early enough to finish at the specified time. When disabled, irrigation will start exactly at the specified time."
        }
      },
      dialog: {
        add_title: "Add Irrigation Start Trigger",
        edit_title: "Edit Irrigation Start Trigger",
        cancel: "Cancel",
        save: "Save",
        delete: "Delete"
      },
      no_triggers: "No irrigation start triggers configured. The system will use the default behavior (sunrise with total zone duration). Add triggers to customize when irrigation starts.",
      offset_auto: "Auto (calculated from total zone duration)",
      confirm_delete: "Are you sure you want to delete the trigger '{name}'?",
      validation: {
        name_required: "Trigger name is required",
        azimuth_invalid: "Azimuth angle must be a valid number"
      },
      help: {
        sunrise_offset: "For sunrise triggers: Use negative values to start before sunrise, positive to start after. Set to 0 to automatically start early enough to complete all zones before sunrise.",
        sunset_offset: "For sunset triggers: Use negative values to start before sunset, positive to start after sunset.",
        azimuth_explanation: "Solar azimuth is the compass direction of the sun. 0°=North, 90°=East, 180°=South, 270°=West. You can enter any angle value (e.g., 450° = 90°, -30° = 330°). Use this to trigger irrigation when the sun reaches a specific position.",
        multiple_triggers: "You can configure multiple triggers. Each enabled trigger will independently schedule irrigation starts."
      }
    },
    Oe = {
      title: "Skip Conditions",
      description: "Automatically skip irrigation when conditions are unfavorable. Precipitation check requires a weather service. Temperature and wind checks also require a weather service.",
      threshold_label: "Precipitation Threshold",
      threshold_description: "Minimum total precipitation (in mm) forecast across the look-ahead window to skip irrigation.",
      lookahead_label: "Forecast look-ahead (days)",
      lookahead_help: "How many upcoming forecast days to add up when checking for rain. The forecast starts at tomorrow (today is excluded), so 1 = just the next day, 2 = the next two days, and so on.",
      temp_section_title: "Skip on low temperature",
      temp_threshold_label: "Skip if temperature is below",
      wind_section_title: "Skip on high wind speed",
      wind_threshold_label: "Skip if wind speed is above",
      rain_sensor_section_title: "Skip on rain sensor",
      rain_sensor_label: "Rain sensor entity (optional)",
      rain_sensor_placeholder: "e.g. binary_sensor.rain"
    },
    Ue = {
      title: "Location Coordinates",
      description: "Configure location coordinates for weather data retrieval. You can use manual coordinates different from your Home Assistant location if needed.",
      manual_enabled: "Use manual coordinates",
      use_ha_location: "Use Home Assistant location",
      latitude: "Latitude (decimal degrees)",
      longitude: "Longitude (decimal degrees)",
      elevation: "Elevation (meters above sea level)",
      current_ha_coords: "Current Home Assistant coordinates"
    },
    De = {
      title: "Days Between Irrigation",
      description: "Configure the minimum number of days that must pass between irrigation events. This helps control watering frequency for water conservation and plant health management.\n\nTypical real-world use cases:\n• Lawn care: 1-2 day intervals prevent overwatering\n• Drought restrictions: 6+ day intervals for weekly watering\n• Deep-rooted plants: 3-7 day intervals for less frequent watering\n• Water conservation: Customizable based on climate and soil conditions",
      label: "Minimum days between irrigation",
      help_text: "Set to 0 to disable this feature. Values from 1-365 days are supported. This setting works alongside existing precipitation forecasting logic."
    },
    Ge = {
      title: "Zone Sequencing",
      description: "When multiple zones need irrigation, choose whether they run at the same time or one after another. Sequential mode waits for each zone to finish before starting the next. Rotating mode cycles through zones, giving each one a limited consecutive run before moving to the next.",
      parallel: "Parallel (all zones at once)",
      sequential: "Sequential (one zone at a time)",
      rotating: "Rotating (zones take turns)",
      max_consecutive_duration_label: "Max consecutive run time per zone",
      max_consecutive_duration_unit: "minutes",
      min_absorption_time_label: "Min. absorption time between slots",
      min_absorption_time_unit: "minutes (0 = disabled)"
    },
    Fe = {
      zone_size: "The total irrigated area of this zone. Used with throughput to calculate how much water is applied per run.",
      zone_throughput: "Total water flow of your irrigation system for this zone (litres/min in metric, gal/min in imperial). Check your sprinkler datasheet or measure by timing how long it takes to fill a known container.",
      zone_drainage_rate: "How fast excess water drains from the soil when the bucket is full. Typical: lawn 50 mm/h, sandy soil 100+ mm/h, clay 10 mm/h.",
      zone_bucket: "Current water deficit (negative) or surplus (positive) for this zone. Irrigation triggers when bucket drops below the threshold.",
      zone_maximum_bucket: "Maximum moisture surplus the zone can hold. Water above this level is treated as runoff. Typical value: 50 mm.",
      zone_bucket_threshold: "Irrigation triggers when the bucket drops below this value. Must be 0 or negative. 0 means irrigate whenever there is any deficit.",
      zone_multiplier: "Scale factor applied to the calculated duration. Use above 1.0 to increase, below 1.0 to decrease. Useful for fine-tuning without changing physical measurements.",
      zone_lead_time: "Extra seconds added before irrigation starts. Use for pump warm-up or system pressurisation.",
      zone_maximum_duration: "Hard cap on any single irrigation run in seconds. Prevents runaway watering. Default: 3600 s (1 hour).",
      zone_linked_entity: "The HA switch or valve entity controlling water flow for this zone. This entity is turned on when irrigation runs.",
      zone_flow_sensor: "Optional sensor measuring actual water flow rate. Used for reporting only — does not affect duration calculations.",
      general_autoupdatedelay: "Seconds to wait after HA starts before the first weather data fetch. Allows other integrations to initialise first.",
      general_sensor_debounce: "Minimum gap in milliseconds between sensor readings to filter noise from rapidly changing sensors.",
      general_calctime: "Time of day when irrigation durations are recalculated from collected weather data. Format: HH:MM (24-hour).",
      general_cleardatatime: "Time of day when old weather data is purged. Must be set later than the calculation time.",
      general_days_between: "Minimum days between irrigation events for the same zone. Set to 0 to disable (irrigate whenever deficit exists).",
      general_autoupdateinterval: "How often weather data is collected. Choose a value that balances fresh data against API rate limits.",
      general_precipitation_threshold: "Irrigation is skipped if total forecast precipitation across the look-ahead window exceeds this amount.",
      general_temp_threshold: "Irrigation is skipped if the current temperature is below this value (e.g. to prevent frost damage).",
      general_wind_threshold: "Irrigation is skipped if wind speed exceeds this value (high winds reduce efficiency and cause drift)."
    },
    We = {
      title: "Setup Wizard",
      open_button: "Setup Wizard",
      close: "Close",
      next: "Next",
      back: "Back",
      finish: "Finish",
      skip_step: "Skip this step",
      step_indicator: "Step {current} of {total}",
      stepper: {
        weather: "Weather",
        module: "Module",
        mapping: "Sensor Group",
        zone: "Zone"
      },
      setup_complete_banner: "Setup not complete. Run the wizard to get started.",
      open_wizard: "Open Wizard",
      steps: {
        welcome: {
          title: "Welcome to Smart Irrigation",
          intro: "This wizard guides you through the four steps needed to get your first zone irrigating automatically.",
          step1_label: "Weather Service — where to get weather data",
          step2_label: "Calculation Module — how irrigation duration is computed",
          step3_label: "Sensor Group — which data sources to use",
          step4_label: "Zone — your first irrigation zone",
          tip: "You can skip any step and configure it later from the Setup tab."
        },
        weather: {
          title: "Weather Service",
          description: "Choose how to get weather data. Open-Meteo is free and requires no API key — it is the easiest choice for most users."
        },
        module: {
          title: "Calculation Module",
          description: "A module calculates how long to irrigate based on evapotranspiration (ET). The PyETO module (FAO-56 method) is recommended for most users.",
          pick_label: "Select module type",
          no_modules: "No module types available."
        },
        mapping: {
          title: "Sensor Group",
          description: "A sensor group links each weather variable to a data source. Set the key variables below — you can refine individual sensor mappings later from the Setup → Sensor Groups tab.",
          name_label: "Sensor group name",
          source_label: "Data source for",
          use_weather_service: "Weather service",
          use_sensor: "Sensor",
          use_static: "Static value",
          use_none: "None / not used"
        },
        zone: {
          title: "First Zone",
          description: "A zone is one irrigation area (e.g. lawn, garden bed). Set the physical properties so the system can calculate the correct irrigation duration.",
          name_label: "Zone name",
          size_label: "Area",
          throughput_label: "Sprinkler throughput",
          entity_label: "Linked switch or valve",
          entity_placeholder: "e.g. switch.garden_valve",
          module_label: "Calculation module",
          mapping_label: "Sensor group"
        },
        done: {
          title: "Setup Complete!",
          description: "Your first zone is ready. Smart Irrigation will now calculate irrigation durations automatically based on weather data.",
          next_steps: "What you can do next:",
          tip1: "Go to Zones to view calculated durations and bucket values.",
          tip2: "Add more zones from the Zones tab.",
          tip3: "Refine all settings from the Setup tab.",
          go_zones: "Go to Zones",
          go_setup: "Go to Setup"
        }
      },
      confirm_close: {
        body: "Close the setup wizard? Your progress so far is saved.",
        keep: "Keep editing",
        close: "Close"
      }
    },
    Ze = {
      common: Ce,
      defaults: Le,
      module: Be,
      calcmodules: Pe,
      panels: Ne,
      title: Ie,
      weather_service_config: Me,
      irrigation_start_triggers: Re,
      weather_skip: Oe,
      coordinate_config: Ue,
      days_between_irrigation: De,
      zone_sequencing: Ge,
      field_help: Fe,
      wizard: We
    },
    je = Object.freeze({
      __proto__: null,
      common: Ce,
      defaults: Le,
      module: Be,
      calcmodules: Pe,
      panels: Ne,
      title: Ie,
      weather_service_config: Me,
      irrigation_start_triggers: Re,
      weather_skip: Oe,
      coordinate_config: Ue,
      days_between_irrigation: De,
      zone_sequencing: Ge,
      field_help: Fe,
      wizard: We,
      default: Ze
    });
  function Ve(e, t) {
    var i = t && t.cache ? t.cache : rt,
      r = t && t.serializer ? t.serializer : Je;
    return (t && t.strategy ? t.strategy : qe)(e, {
      cache: i,
      serializer: r
    });
  }
  function Xe(e, t, i, r) {
    var n,
      o = null == (n = r) || "number" == typeof n || "boolean" == typeof n ? r : i(r),
      a = t.get(o);
    return void 0 === a && (a = e.call(this, r), t.set(o, a)), a;
  }
  function Ke(e, t, i) {
    var r = Array.prototype.slice.call(arguments, 3),
      n = i(r),
      o = t.get(n);
    return void 0 === o && (o = e.apply(this, r), t.set(n, o)), o;
  }
  function Ye(e, t, i, r, n) {
    return i.bind(t, e, r, n);
  }
  function qe(e, t) {
    return Ye(e, this, 1 === e.length ? Xe : Ke, t.cache.create(), t.serializer);
  }
  var Je = function () {
    return JSON.stringify(arguments);
  };
  function Qe() {
    this.cache = Object.create(null);
  }
  Qe.prototype.get = function (e) {
    return this.cache[e];
  }, Qe.prototype.set = function (e, t) {
    this.cache[e] = t;
  };
  var et,
    tt,
    it,
    rt = {
      create: function () {
        return new Qe();
      }
    },
    nt = {
      variadic: function (e, t) {
        return Ye(e, this, Ke, t.cache.create(), t.serializer);
      },
      monadic: function (e, t) {
        return Ye(e, this, Xe, t.cache.create(), t.serializer);
      }
    };
  function ot(e) {
    return e.type === tt.literal;
  }
  function at(e) {
    return e.type === tt.argument;
  }
  function st(e) {
    return e.type === tt.number;
  }
  function lt(e) {
    return e.type === tt.date;
  }
  function ct(e) {
    return e.type === tt.time;
  }
  function ht(e) {
    return e.type === tt.select;
  }
  function ut(e) {
    return e.type === tt.plural;
  }
  function dt(e) {
    return e.type === tt.pound;
  }
  function pt(e) {
    return e.type === tt.tag;
  }
  function gt(e) {
    return !(!e || "object" != typeof e || e.type !== it.number);
  }
  function mt(e) {
    return !(!e || "object" != typeof e || e.type !== it.dateTime);
  }
  !function (e) {
    e[e.EXPECT_ARGUMENT_CLOSING_BRACE = 1] = "EXPECT_ARGUMENT_CLOSING_BRACE", e[e.EMPTY_ARGUMENT = 2] = "EMPTY_ARGUMENT", e[e.MALFORMED_ARGUMENT = 3] = "MALFORMED_ARGUMENT", e[e.EXPECT_ARGUMENT_TYPE = 4] = "EXPECT_ARGUMENT_TYPE", e[e.INVALID_ARGUMENT_TYPE = 5] = "INVALID_ARGUMENT_TYPE", e[e.EXPECT_ARGUMENT_STYLE = 6] = "EXPECT_ARGUMENT_STYLE", e[e.INVALID_NUMBER_SKELETON = 7] = "INVALID_NUMBER_SKELETON", e[e.INVALID_DATE_TIME_SKELETON = 8] = "INVALID_DATE_TIME_SKELETON", e[e.EXPECT_NUMBER_SKELETON = 9] = "EXPECT_NUMBER_SKELETON", e[e.EXPECT_DATE_TIME_SKELETON = 10] = "EXPECT_DATE_TIME_SKELETON", e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE = 11] = "UNCLOSED_QUOTE_IN_ARGUMENT_STYLE", e[e.EXPECT_SELECT_ARGUMENT_OPTIONS = 12] = "EXPECT_SELECT_ARGUMENT_OPTIONS", e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE = 13] = "EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE", e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE = 14] = "INVALID_PLURAL_ARGUMENT_OFFSET_VALUE", e[e.EXPECT_SELECT_ARGUMENT_SELECTOR = 15] = "EXPECT_SELECT_ARGUMENT_SELECTOR", e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR = 16] = "EXPECT_PLURAL_ARGUMENT_SELECTOR", e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT = 17] = "EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT", e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT = 18] = "EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT", e[e.INVALID_PLURAL_ARGUMENT_SELECTOR = 19] = "INVALID_PLURAL_ARGUMENT_SELECTOR", e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR = 20] = "DUPLICATE_PLURAL_ARGUMENT_SELECTOR", e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR = 21] = "DUPLICATE_SELECT_ARGUMENT_SELECTOR", e[e.MISSING_OTHER_CLAUSE = 22] = "MISSING_OTHER_CLAUSE", e[e.INVALID_TAG = 23] = "INVALID_TAG", e[e.INVALID_TAG_NAME = 25] = "INVALID_TAG_NAME", e[e.UNMATCHED_CLOSING_TAG = 26] = "UNMATCHED_CLOSING_TAG", e[e.UNCLOSED_TAG = 27] = "UNCLOSED_TAG";
  }(et || (et = {})), function (e) {
    e[e.literal = 0] = "literal", e[e.argument = 1] = "argument", e[e.number = 2] = "number", e[e.date = 3] = "date", e[e.time = 4] = "time", e[e.select = 5] = "select", e[e.plural = 6] = "plural", e[e.pound = 7] = "pound", e[e.tag = 8] = "tag";
  }(tt || (tt = {})), function (e) {
    e[e.number = 0] = "number", e[e.dateTime = 1] = "dateTime";
  }(it || (it = {}));
  var ft = /[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/,
    bt = /(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;
  function vt(e) {
    var t = {};
    return e.replace(bt, function (e) {
      var i = e.length;
      switch (e[0]) {
        case "G":
          t.era = 4 === i ? "long" : 5 === i ? "narrow" : "short";
          break;
        case "y":
          t.year = 2 === i ? "2-digit" : "numeric";
          break;
        case "Y":
        case "u":
        case "U":
        case "r":
          throw new RangeError("`Y/u/U/r` (year) patterns are not supported, use `y` instead");
        case "q":
        case "Q":
          throw new RangeError("`q/Q` (quarter) patterns are not supported");
        case "M":
        case "L":
          t.month = ["numeric", "2-digit", "short", "long", "narrow"][i - 1];
          break;
        case "w":
        case "W":
          throw new RangeError("`w/W` (week) patterns are not supported");
        case "d":
          t.day = ["numeric", "2-digit"][i - 1];
          break;
        case "D":
        case "F":
        case "g":
          throw new RangeError("`D/F/g` (day) patterns are not supported, use `d` instead");
        case "E":
          t.weekday = 4 === i ? "long" : 5 === i ? "narrow" : "short";
          break;
        case "e":
          if (i < 4) throw new RangeError("`e..eee` (weekday) patterns are not supported");
          t.weekday = ["short", "long", "narrow", "short"][i - 4];
          break;
        case "c":
          if (i < 4) throw new RangeError("`c..ccc` (weekday) patterns are not supported");
          t.weekday = ["short", "long", "narrow", "short"][i - 4];
          break;
        case "a":
          t.hour12 = !0;
          break;
        case "b":
        case "B":
          throw new RangeError("`b/B` (period) patterns are not supported, use `a` instead");
        case "h":
          t.hourCycle = "h12", t.hour = ["numeric", "2-digit"][i - 1];
          break;
        case "H":
          t.hourCycle = "h23", t.hour = ["numeric", "2-digit"][i - 1];
          break;
        case "K":
          t.hourCycle = "h11", t.hour = ["numeric", "2-digit"][i - 1];
          break;
        case "k":
          t.hourCycle = "h24", t.hour = ["numeric", "2-digit"][i - 1];
          break;
        case "j":
        case "J":
        case "C":
          throw new RangeError("`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead");
        case "m":
          t.minute = ["numeric", "2-digit"][i - 1];
          break;
        case "s":
          t.second = ["numeric", "2-digit"][i - 1];
          break;
        case "S":
        case "A":
          throw new RangeError("`S/A` (second) patterns are not supported, use `s` instead");
        case "z":
          t.timeZoneName = i < 4 ? "short" : "long";
          break;
        case "Z":
        case "O":
        case "v":
        case "V":
        case "X":
        case "x":
          throw new RangeError("`Z/O/v/V/X/x` (timeZone) patterns are not supported, use `z` instead");
      }
      return "";
    }), t;
  }
  var _t = /[\t-\r \x85\u200E\u200F\u2028\u2029]/i;
  var yt = /^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g,
    wt = /^(@+)?(\+|#+)?[rs]?$/g,
    Et = /(\*)(0+)|(#+)(0+)|(0+)/g,
    kt = /^(0+)$/;
  function At(e) {
    var t = {};
    return "r" === e[e.length - 1] ? t.roundingPriority = "morePrecision" : "s" === e[e.length - 1] && (t.roundingPriority = "lessPrecision"), e.replace(wt, function (e, i, r) {
      return "string" != typeof r ? (t.minimumSignificantDigits = i.length, t.maximumSignificantDigits = i.length) : "+" === r ? t.minimumSignificantDigits = i.length : "#" === i[0] ? t.maximumSignificantDigits = i.length : (t.minimumSignificantDigits = i.length, t.maximumSignificantDigits = i.length + ("string" == typeof r ? r.length : 0)), "";
    }), t;
  }
  function xt(e) {
    switch (e) {
      case "sign-auto":
        return {
          signDisplay: "auto"
        };
      case "sign-accounting":
      case "()":
        return {
          currencySign: "accounting"
        };
      case "sign-always":
      case "+!":
        return {
          signDisplay: "always"
        };
      case "sign-accounting-always":
      case "()!":
        return {
          signDisplay: "always",
          currencySign: "accounting"
        };
      case "sign-except-zero":
      case "+?":
        return {
          signDisplay: "exceptZero"
        };
      case "sign-accounting-except-zero":
      case "()?":
        return {
          signDisplay: "exceptZero",
          currencySign: "accounting"
        };
      case "sign-never":
      case "+_":
        return {
          signDisplay: "never"
        };
    }
  }
  function St(e) {
    var t;
    if ("E" === e[0] && "E" === e[1] ? (t = {
      notation: "engineering"
    }, e = e.slice(2)) : "E" === e[0] && (t = {
      notation: "scientific"
    }, e = e.slice(1)), t) {
      var i = e.slice(0, 2);
      if ("+!" === i ? (t.signDisplay = "always", e = e.slice(2)) : "+?" === i && (t.signDisplay = "exceptZero", e = e.slice(2)), !kt.test(e)) throw new Error("Malformed concise eng/scientific notation");
      t.minimumIntegerDigits = e.length;
    }
    return t;
  }
  function Tt(e) {
    var t = xt(e);
    return t || {};
  }
  function $t(e) {
    for (var t = {}, i = 0, n = e; i < n.length; i++) {
      var o = n[i];
      switch (o.stem) {
        case "percent":
        case "%":
          t.style = "percent";
          continue;
        case "%x100":
          t.style = "percent", t.scale = 100;
          continue;
        case "currency":
          t.style = "currency", t.currency = o.options[0];
          continue;
        case "group-off":
        case ",_":
          t.useGrouping = !1;
          continue;
        case "precision-integer":
        case ".":
          t.maximumFractionDigits = 0;
          continue;
        case "measure-unit":
        case "unit":
          t.style = "unit", t.unit = o.options[0].replace(/^(.*?)-/, "");
          continue;
        case "compact-short":
        case "K":
          t.notation = "compact", t.compactDisplay = "short";
          continue;
        case "compact-long":
        case "KK":
          t.notation = "compact", t.compactDisplay = "long";
          continue;
        case "scientific":
          t = r(r(r({}, t), {
            notation: "scientific"
          }), o.options.reduce(function (e, t) {
            return r(r({}, e), Tt(t));
          }, {}));
          continue;
        case "engineering":
          t = r(r(r({}, t), {
            notation: "engineering"
          }), o.options.reduce(function (e, t) {
            return r(r({}, e), Tt(t));
          }, {}));
          continue;
        case "notation-simple":
          t.notation = "standard";
          continue;
        case "unit-width-narrow":
          t.currencyDisplay = "narrowSymbol", t.unitDisplay = "narrow";
          continue;
        case "unit-width-short":
          t.currencyDisplay = "code", t.unitDisplay = "short";
          continue;
        case "unit-width-full-name":
          t.currencyDisplay = "name", t.unitDisplay = "long";
          continue;
        case "unit-width-iso-code":
          t.currencyDisplay = "symbol";
          continue;
        case "scale":
          t.scale = parseFloat(o.options[0]);
          continue;
        case "rounding-mode-floor":
          t.roundingMode = "floor";
          continue;
        case "rounding-mode-ceiling":
          t.roundingMode = "ceil";
          continue;
        case "rounding-mode-down":
          t.roundingMode = "trunc";
          continue;
        case "rounding-mode-up":
          t.roundingMode = "expand";
          continue;
        case "rounding-mode-half-even":
          t.roundingMode = "halfEven";
          continue;
        case "rounding-mode-half-down":
          t.roundingMode = "halfTrunc";
          continue;
        case "rounding-mode-half-up":
          t.roundingMode = "halfExpand";
          continue;
        case "integer-width":
          if (o.options.length > 1) throw new RangeError("integer-width stems only accept a single optional option");
          o.options[0].replace(Et, function (e, i, r, n, o, a) {
            if (i) t.minimumIntegerDigits = r.length;else {
              if (n && o) throw new Error("We currently do not support maximum integer digits");
              if (a) throw new Error("We currently do not support exact integer digits");
            }
            return "";
          });
          continue;
      }
      if (kt.test(o.stem)) t.minimumIntegerDigits = o.stem.length;else if (yt.test(o.stem)) {
        if (o.options.length > 1) throw new RangeError("Fraction-precision stems only accept a single optional option");
        o.stem.replace(yt, function (e, i, r, n, o, a) {
          return "*" === r ? t.minimumFractionDigits = i.length : n && "#" === n[0] ? t.maximumFractionDigits = n.length : o && a ? (t.minimumFractionDigits = o.length, t.maximumFractionDigits = o.length + a.length) : (t.minimumFractionDigits = i.length, t.maximumFractionDigits = i.length), "";
        });
        var a = o.options[0];
        "w" === a ? t = r(r({}, t), {
          trailingZeroDisplay: "stripIfInteger"
        }) : a && (t = r(r({}, t), At(a)));
      } else if (wt.test(o.stem)) t = r(r({}, t), At(o.stem));else {
        var s = xt(o.stem);
        s && (t = r(r({}, t), s));
        var l = St(o.stem);
        l && (t = r(r({}, t), l));
      }
    }
    return t;
  }
  var Ht,
    zt = {
      "001": ["H", "h"],
      419: ["h", "H", "hB", "hb"],
      AC: ["H", "h", "hb", "hB"],
      AD: ["H", "hB"],
      AE: ["h", "hB", "hb", "H"],
      AF: ["H", "hb", "hB", "h"],
      AG: ["h", "hb", "H", "hB"],
      AI: ["H", "h", "hb", "hB"],
      AL: ["h", "H", "hB"],
      AM: ["H", "hB"],
      AO: ["H", "hB"],
      AR: ["h", "H", "hB", "hb"],
      AS: ["h", "H"],
      AT: ["H", "hB"],
      AU: ["h", "hb", "H", "hB"],
      AW: ["H", "hB"],
      AX: ["H"],
      AZ: ["H", "hB", "h"],
      BA: ["H", "hB", "h"],
      BB: ["h", "hb", "H", "hB"],
      BD: ["h", "hB", "H"],
      BE: ["H", "hB"],
      BF: ["H", "hB"],
      BG: ["H", "hB", "h"],
      BH: ["h", "hB", "hb", "H"],
      BI: ["H", "h"],
      BJ: ["H", "hB"],
      BL: ["H", "hB"],
      BM: ["h", "hb", "H", "hB"],
      BN: ["hb", "hB", "h", "H"],
      BO: ["h", "H", "hB", "hb"],
      BQ: ["H"],
      BR: ["H", "hB"],
      BS: ["h", "hb", "H", "hB"],
      BT: ["h", "H"],
      BW: ["H", "h", "hb", "hB"],
      BY: ["H", "h"],
      BZ: ["H", "h", "hb", "hB"],
      CA: ["h", "hb", "H", "hB"],
      CC: ["H", "h", "hb", "hB"],
      CD: ["hB", "H"],
      CF: ["H", "h", "hB"],
      CG: ["H", "hB"],
      CH: ["H", "hB", "h"],
      CI: ["H", "hB"],
      CK: ["H", "h", "hb", "hB"],
      CL: ["h", "H", "hB", "hb"],
      CM: ["H", "h", "hB"],
      CN: ["H", "hB", "hb", "h"],
      CO: ["h", "H", "hB", "hb"],
      CP: ["H"],
      CR: ["h", "H", "hB", "hb"],
      CU: ["h", "H", "hB", "hb"],
      CV: ["H", "hB"],
      CW: ["H", "hB"],
      CX: ["H", "h", "hb", "hB"],
      CY: ["h", "H", "hb", "hB"],
      CZ: ["H"],
      DE: ["H", "hB"],
      DG: ["H", "h", "hb", "hB"],
      DJ: ["h", "H"],
      DK: ["H"],
      DM: ["h", "hb", "H", "hB"],
      DO: ["h", "H", "hB", "hb"],
      DZ: ["h", "hB", "hb", "H"],
      EA: ["H", "h", "hB", "hb"],
      EC: ["h", "H", "hB", "hb"],
      EE: ["H", "hB"],
      EG: ["h", "hB", "hb", "H"],
      EH: ["h", "hB", "hb", "H"],
      ER: ["h", "H"],
      ES: ["H", "hB", "h", "hb"],
      ET: ["hB", "hb", "h", "H"],
      FI: ["H"],
      FJ: ["h", "hb", "H", "hB"],
      FK: ["H", "h", "hb", "hB"],
      FM: ["h", "hb", "H", "hB"],
      FO: ["H", "h"],
      FR: ["H", "hB"],
      GA: ["H", "hB"],
      GB: ["H", "h", "hb", "hB"],
      GD: ["h", "hb", "H", "hB"],
      GE: ["H", "hB", "h"],
      GF: ["H", "hB"],
      GG: ["H", "h", "hb", "hB"],
      GH: ["h", "H"],
      GI: ["H", "h", "hb", "hB"],
      GL: ["H", "h"],
      GM: ["h", "hb", "H", "hB"],
      GN: ["H", "hB"],
      GP: ["H", "hB"],
      GQ: ["H", "hB", "h", "hb"],
      GR: ["h", "H", "hb", "hB"],
      GT: ["h", "H", "hB", "hb"],
      GU: ["h", "hb", "H", "hB"],
      GW: ["H", "hB"],
      GY: ["h", "hb", "H", "hB"],
      HK: ["h", "hB", "hb", "H"],
      HN: ["h", "H", "hB", "hb"],
      HR: ["H", "hB"],
      HU: ["H", "h"],
      IC: ["H", "h", "hB", "hb"],
      ID: ["H"],
      IE: ["H", "h", "hb", "hB"],
      IL: ["H", "hB"],
      IM: ["H", "h", "hb", "hB"],
      IN: ["h", "H"],
      IO: ["H", "h", "hb", "hB"],
      IQ: ["h", "hB", "hb", "H"],
      IR: ["hB", "H"],
      IS: ["H"],
      IT: ["H", "hB"],
      JE: ["H", "h", "hb", "hB"],
      JM: ["h", "hb", "H", "hB"],
      JO: ["h", "hB", "hb", "H"],
      JP: ["H", "K", "h"],
      KE: ["hB", "hb", "H", "h"],
      KG: ["H", "h", "hB", "hb"],
      KH: ["hB", "h", "H", "hb"],
      KI: ["h", "hb", "H", "hB"],
      KM: ["H", "h", "hB", "hb"],
      KN: ["h", "hb", "H", "hB"],
      KP: ["h", "H", "hB", "hb"],
      KR: ["h", "H", "hB", "hb"],
      KW: ["h", "hB", "hb", "H"],
      KY: ["h", "hb", "H", "hB"],
      KZ: ["H", "hB"],
      LA: ["H", "hb", "hB", "h"],
      LB: ["h", "hB", "hb", "H"],
      LC: ["h", "hb", "H", "hB"],
      LI: ["H", "hB", "h"],
      LK: ["H", "h", "hB", "hb"],
      LR: ["h", "hb", "H", "hB"],
      LS: ["h", "H"],
      LT: ["H", "h", "hb", "hB"],
      LU: ["H", "h", "hB"],
      LV: ["H", "hB", "hb", "h"],
      LY: ["h", "hB", "hb", "H"],
      MA: ["H", "h", "hB", "hb"],
      MC: ["H", "hB"],
      MD: ["H", "hB"],
      ME: ["H", "hB", "h"],
      MF: ["H", "hB"],
      MG: ["H", "h"],
      MH: ["h", "hb", "H", "hB"],
      MK: ["H", "h", "hb", "hB"],
      ML: ["H"],
      MM: ["hB", "hb", "H", "h"],
      MN: ["H", "h", "hb", "hB"],
      MO: ["h", "hB", "hb", "H"],
      MP: ["h", "hb", "H", "hB"],
      MQ: ["H", "hB"],
      MR: ["h", "hB", "hb", "H"],
      MS: ["H", "h", "hb", "hB"],
      MT: ["H", "h"],
      MU: ["H", "h"],
      MV: ["H", "h"],
      MW: ["h", "hb", "H", "hB"],
      MX: ["h", "H", "hB", "hb"],
      MY: ["hb", "hB", "h", "H"],
      MZ: ["H", "hB"],
      NA: ["h", "H", "hB", "hb"],
      NC: ["H", "hB"],
      NE: ["H"],
      NF: ["H", "h", "hb", "hB"],
      NG: ["H", "h", "hb", "hB"],
      NI: ["h", "H", "hB", "hb"],
      NL: ["H", "hB"],
      NO: ["H", "h"],
      NP: ["H", "h", "hB"],
      NR: ["H", "h", "hb", "hB"],
      NU: ["H", "h", "hb", "hB"],
      NZ: ["h", "hb", "H", "hB"],
      OM: ["h", "hB", "hb", "H"],
      PA: ["h", "H", "hB", "hb"],
      PE: ["h", "H", "hB", "hb"],
      PF: ["H", "h", "hB"],
      PG: ["h", "H"],
      PH: ["h", "hB", "hb", "H"],
      PK: ["h", "hB", "H"],
      PL: ["H", "h"],
      PM: ["H", "hB"],
      PN: ["H", "h", "hb", "hB"],
      PR: ["h", "H", "hB", "hb"],
      PS: ["h", "hB", "hb", "H"],
      PT: ["H", "hB"],
      PW: ["h", "H"],
      PY: ["h", "H", "hB", "hb"],
      QA: ["h", "hB", "hb", "H"],
      RE: ["H", "hB"],
      RO: ["H", "hB"],
      RS: ["H", "hB", "h"],
      RU: ["H"],
      RW: ["H", "h"],
      SA: ["h", "hB", "hb", "H"],
      SB: ["h", "hb", "H", "hB"],
      SC: ["H", "h", "hB"],
      SD: ["h", "hB", "hb", "H"],
      SE: ["H"],
      SG: ["h", "hb", "H", "hB"],
      SH: ["H", "h", "hb", "hB"],
      SI: ["H", "hB"],
      SJ: ["H"],
      SK: ["H"],
      SL: ["h", "hb", "H", "hB"],
      SM: ["H", "h", "hB"],
      SN: ["H", "h", "hB"],
      SO: ["h", "H"],
      SR: ["H", "hB"],
      SS: ["h", "hb", "H", "hB"],
      ST: ["H", "hB"],
      SV: ["h", "H", "hB", "hb"],
      SX: ["H", "h", "hb", "hB"],
      SY: ["h", "hB", "hb", "H"],
      SZ: ["h", "hb", "H", "hB"],
      TA: ["H", "h", "hb", "hB"],
      TC: ["h", "hb", "H", "hB"],
      TD: ["h", "H", "hB"],
      TF: ["H", "h", "hB"],
      TG: ["H", "hB"],
      TH: ["H", "h"],
      TJ: ["H", "h"],
      TL: ["H", "hB", "hb", "h"],
      TM: ["H", "h"],
      TN: ["h", "hB", "hb", "H"],
      TO: ["h", "H"],
      TR: ["H", "hB"],
      TT: ["h", "hb", "H", "hB"],
      TW: ["hB", "hb", "h", "H"],
      TZ: ["hB", "hb", "H", "h"],
      UA: ["H", "hB", "h"],
      UG: ["hB", "hb", "H", "h"],
      UM: ["h", "hb", "H", "hB"],
      US: ["h", "hb", "H", "hB"],
      UY: ["h", "H", "hB", "hb"],
      UZ: ["H", "hB", "h"],
      VA: ["H", "h", "hB"],
      VC: ["h", "hb", "H", "hB"],
      VE: ["h", "H", "hB", "hb"],
      VG: ["h", "hb", "H", "hB"],
      VI: ["h", "hb", "H", "hB"],
      VN: ["H", "h"],
      VU: ["h", "H"],
      WF: ["H", "hB"],
      WS: ["h", "H"],
      XK: ["H", "hB", "h"],
      YE: ["h", "hB", "hb", "H"],
      YT: ["H", "hB"],
      ZA: ["H", "h", "hb", "hB"],
      ZM: ["h", "hb", "H", "hB"],
      ZW: ["H", "h"],
      "af-ZA": ["H", "h", "hB", "hb"],
      "ar-001": ["h", "hB", "hb", "H"],
      "ca-ES": ["H", "h", "hB"],
      "en-001": ["h", "hb", "H", "hB"],
      "en-HK": ["h", "hb", "H", "hB"],
      "en-IL": ["H", "h", "hb", "hB"],
      "en-MY": ["h", "hb", "H", "hB"],
      "es-BR": ["H", "h", "hB", "hb"],
      "es-ES": ["H", "h", "hB", "hb"],
      "es-GQ": ["H", "h", "hB", "hb"],
      "fr-CA": ["H", "h", "hB"],
      "gl-ES": ["H", "h", "hB"],
      "gu-IN": ["hB", "hb", "h", "H"],
      "hi-IN": ["hB", "h", "H"],
      "it-CH": ["H", "h", "hB"],
      "it-IT": ["H", "h", "hB"],
      "kn-IN": ["hB", "h", "H"],
      "ml-IN": ["hB", "h", "H"],
      "mr-IN": ["hB", "hb", "h", "H"],
      "pa-IN": ["hB", "hb", "h", "H"],
      "ta-IN": ["hB", "h", "hb", "H"],
      "te-IN": ["hB", "h", "H"],
      "zu-ZA": ["H", "hB", "hb", "h"]
    };
  function Ct(e) {
    var t = e.hourCycle;
    if (void 0 === t && e.hourCycles && e.hourCycles.length && (t = e.hourCycles[0]), t) switch (t) {
      case "h24":
        return "k";
      case "h23":
        return "H";
      case "h12":
        return "h";
      case "h11":
        return "K";
      default:
        throw new Error("Invalid hourCycle");
    }
    var i,
      r = e.language;
    return "root" !== r && (i = e.maximize().region), (zt[i || ""] || zt[r || ""] || zt["".concat(r, "-001")] || zt["001"])[0];
  }
  var Lt = new RegExp("^".concat(ft.source, "*")),
    Bt = new RegExp("".concat(ft.source, "*$"));
  function Pt(e, t) {
    return {
      start: e,
      end: t
    };
  }
  var Nt = !!String.prototype.startsWith && "_a".startsWith("a", 1),
    It = !!String.fromCodePoint,
    Mt = !!Object.fromEntries,
    Rt = !!String.prototype.codePointAt,
    Ot = !!String.prototype.trimStart,
    Ut = !!String.prototype.trimEnd,
    Dt = !!Number.isSafeInteger ? Number.isSafeInteger : function (e) {
      return "number" == typeof e && isFinite(e) && Math.floor(e) === e && Math.abs(e) <= 9007199254740991;
    },
    Gt = !0;
  try {
    Gt = "a" === (null === (Ht = Yt("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu").exec("a")) || void 0 === Ht ? void 0 : Ht[0]);
  } catch (M) {
    Gt = !1;
  }
  var Ft,
    Wt = Nt ? function (e, t, i) {
      return e.startsWith(t, i);
    } : function (e, t, i) {
      return e.slice(i, i + t.length) === t;
    },
    Zt = It ? String.fromCodePoint : function () {
      for (var e = [], t = 0; t < arguments.length; t++) e[t] = arguments[t];
      for (var i, r = "", n = e.length, o = 0; n > o;) {
        if ((i = e[o++]) > 1114111) throw RangeError(i + " is not a valid code point");
        r += i < 65536 ? String.fromCharCode(i) : String.fromCharCode(55296 + ((i -= 65536) >> 10), i % 1024 + 56320);
      }
      return r;
    },
    jt = Mt ? Object.fromEntries : function (e) {
      for (var t = {}, i = 0, r = e; i < r.length; i++) {
        var n = r[i],
          o = n[0],
          a = n[1];
        t[o] = a;
      }
      return t;
    },
    Vt = Rt ? function (e, t) {
      return e.codePointAt(t);
    } : function (e, t) {
      var i = e.length;
      if (!(t < 0 || t >= i)) {
        var r,
          n = e.charCodeAt(t);
        return n < 55296 || n > 56319 || t + 1 === i || (r = e.charCodeAt(t + 1)) < 56320 || r > 57343 ? n : r - 56320 + (n - 55296 << 10) + 65536;
      }
    },
    Xt = Ot ? function (e) {
      return e.trimStart();
    } : function (e) {
      return e.replace(Lt, "");
    },
    Kt = Ut ? function (e) {
      return e.trimEnd();
    } : function (e) {
      return e.replace(Bt, "");
    };
  function Yt(e, t) {
    return new RegExp(e, t);
  }
  if (Gt) {
    var qt = Yt("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu");
    Ft = function (e, t) {
      var i;
      return qt.lastIndex = t, null !== (i = qt.exec(e)[1]) && void 0 !== i ? i : "";
    };
  } else Ft = function (e, t) {
    for (var i = [];;) {
      var r = Vt(e, t);
      if (void 0 === r || ii(r) || ri(r)) break;
      i.push(r), t += r >= 65536 ? 2 : 1;
    }
    return Zt.apply(void 0, i);
  };
  var Jt,
    Qt = function () {
      function e(e, t) {
        void 0 === t && (t = {}), this.message = e, this.position = {
          offset: 0,
          line: 1,
          column: 1
        }, this.ignoreTag = !!t.ignoreTag, this.locale = t.locale, this.requiresOtherClause = !!t.requiresOtherClause, this.shouldParseSkeletons = !!t.shouldParseSkeletons;
      }
      return e.prototype.parse = function () {
        if (0 !== this.offset()) throw Error("parser can only be used once");
        return this.parseMessage(0, "", !1);
      }, e.prototype.parseMessage = function (e, t, i) {
        for (var r = []; !this.isEOF();) {
          var n = this.char();
          if (123 === n) {
            if ((o = this.parseArgument(e, i)).err) return o;
            r.push(o.val);
          } else {
            if (125 === n && e > 0) break;
            if (35 !== n || "plural" !== t && "selectordinal" !== t) {
              if (60 === n && !this.ignoreTag && 47 === this.peek()) {
                if (i) break;
                return this.error(et.UNMATCHED_CLOSING_TAG, Pt(this.clonePosition(), this.clonePosition()));
              }
              if (60 === n && !this.ignoreTag && ei(this.peek() || 0)) {
                if ((o = this.parseTag(e, t)).err) return o;
                r.push(o.val);
              } else {
                var o;
                if ((o = this.parseLiteral(e, t)).err) return o;
                r.push(o.val);
              }
            } else {
              var a = this.clonePosition();
              this.bump(), r.push({
                type: tt.pound,
                location: Pt(a, this.clonePosition())
              });
            }
          }
        }
        return {
          val: r,
          err: null
        };
      }, e.prototype.parseTag = function (e, t) {
        var i = this.clonePosition();
        this.bump();
        var r = this.parseTagName();
        if (this.bumpSpace(), this.bumpIf("/>")) return {
          val: {
            type: tt.literal,
            value: "<".concat(r, "/>"),
            location: Pt(i, this.clonePosition())
          },
          err: null
        };
        if (this.bumpIf(">")) {
          var n = this.parseMessage(e + 1, t, !0);
          if (n.err) return n;
          var o = n.val,
            a = this.clonePosition();
          if (this.bumpIf("</")) {
            if (this.isEOF() || !ei(this.char())) return this.error(et.INVALID_TAG, Pt(a, this.clonePosition()));
            var s = this.clonePosition();
            return r !== this.parseTagName() ? this.error(et.UNMATCHED_CLOSING_TAG, Pt(s, this.clonePosition())) : (this.bumpSpace(), this.bumpIf(">") ? {
              val: {
                type: tt.tag,
                value: r,
                children: o,
                location: Pt(i, this.clonePosition())
              },
              err: null
            } : this.error(et.INVALID_TAG, Pt(a, this.clonePosition())));
          }
          return this.error(et.UNCLOSED_TAG, Pt(i, this.clonePosition()));
        }
        return this.error(et.INVALID_TAG, Pt(i, this.clonePosition()));
      }, e.prototype.parseTagName = function () {
        var e = this.offset();
        for (this.bump(); !this.isEOF() && ti(this.char());) this.bump();
        return this.message.slice(e, this.offset());
      }, e.prototype.parseLiteral = function (e, t) {
        for (var i = this.clonePosition(), r = "";;) {
          var n = this.tryParseQuote(t);
          if (n) r += n;else {
            var o = this.tryParseUnquoted(e, t);
            if (o) r += o;else {
              var a = this.tryParseLeftAngleBracket();
              if (!a) break;
              r += a;
            }
          }
        }
        var s = Pt(i, this.clonePosition());
        return {
          val: {
            type: tt.literal,
            value: r,
            location: s
          },
          err: null
        };
      }, e.prototype.tryParseLeftAngleBracket = function () {
        return this.isEOF() || 60 !== this.char() || !this.ignoreTag && (ei(e = this.peek() || 0) || 47 === e) ? null : (this.bump(), "<");
        var e;
      }, e.prototype.tryParseQuote = function (e) {
        if (this.isEOF() || 39 !== this.char()) return null;
        switch (this.peek()) {
          case 39:
            return this.bump(), this.bump(), "'";
          case 123:
          case 60:
          case 62:
          case 125:
            break;
          case 35:
            if ("plural" === e || "selectordinal" === e) break;
            return null;
          default:
            return null;
        }
        this.bump();
        var t = [this.char()];
        for (this.bump(); !this.isEOF();) {
          var i = this.char();
          if (39 === i) {
            if (39 !== this.peek()) {
              this.bump();
              break;
            }
            t.push(39), this.bump();
          } else t.push(i);
          this.bump();
        }
        return Zt.apply(void 0, t);
      }, e.prototype.tryParseUnquoted = function (e, t) {
        if (this.isEOF()) return null;
        var i = this.char();
        return 60 === i || 123 === i || 35 === i && ("plural" === t || "selectordinal" === t) || 125 === i && e > 0 ? null : (this.bump(), Zt(i));
      }, e.prototype.parseArgument = function (e, t) {
        var i = this.clonePosition();
        if (this.bump(), this.bumpSpace(), this.isEOF()) return this.error(et.EXPECT_ARGUMENT_CLOSING_BRACE, Pt(i, this.clonePosition()));
        if (125 === this.char()) return this.bump(), this.error(et.EMPTY_ARGUMENT, Pt(i, this.clonePosition()));
        var r = this.parseIdentifierIfPossible().value;
        if (!r) return this.error(et.MALFORMED_ARGUMENT, Pt(i, this.clonePosition()));
        if (this.bumpSpace(), this.isEOF()) return this.error(et.EXPECT_ARGUMENT_CLOSING_BRACE, Pt(i, this.clonePosition()));
        switch (this.char()) {
          case 125:
            return this.bump(), {
              val: {
                type: tt.argument,
                value: r,
                location: Pt(i, this.clonePosition())
              },
              err: null
            };
          case 44:
            return this.bump(), this.bumpSpace(), this.isEOF() ? this.error(et.EXPECT_ARGUMENT_CLOSING_BRACE, Pt(i, this.clonePosition())) : this.parseArgumentOptions(e, t, r, i);
          default:
            return this.error(et.MALFORMED_ARGUMENT, Pt(i, this.clonePosition()));
        }
      }, e.prototype.parseIdentifierIfPossible = function () {
        var e = this.clonePosition(),
          t = this.offset(),
          i = Ft(this.message, t),
          r = t + i.length;
        return this.bumpTo(r), {
          value: i,
          location: Pt(e, this.clonePosition())
        };
      }, e.prototype.parseArgumentOptions = function (e, t, i, n) {
        var o,
          a = this.clonePosition(),
          s = this.parseIdentifierIfPossible().value,
          l = this.clonePosition();
        switch (s) {
          case "":
            return this.error(et.EXPECT_ARGUMENT_TYPE, Pt(a, l));
          case "number":
          case "date":
          case "time":
            this.bumpSpace();
            var c = null;
            if (this.bumpIf(",")) {
              this.bumpSpace();
              var h = this.clonePosition();
              if ((v = this.parseSimpleArgStyleIfPossible()).err) return v;
              if (0 === (g = Kt(v.val)).length) return this.error(et.EXPECT_ARGUMENT_STYLE, Pt(this.clonePosition(), this.clonePosition()));
              c = {
                style: g,
                styleLocation: Pt(h, this.clonePosition())
              };
            }
            if ((_ = this.tryParseArgumentClose(n)).err) return _;
            var u = Pt(n, this.clonePosition());
            if (c && Wt(null == c ? void 0 : c.style, "::", 0)) {
              var d = Xt(c.style.slice(2));
              if ("number" === s) return (v = this.parseNumberSkeletonFromString(d, c.styleLocation)).err ? v : {
                val: {
                  type: tt.number,
                  value: i,
                  location: u,
                  style: v.val
                },
                err: null
              };
              if (0 === d.length) return this.error(et.EXPECT_DATE_TIME_SKELETON, u);
              var p = d;
              this.locale && (p = function (e, t) {
                for (var i = "", r = 0; r < e.length; r++) {
                  var n = e.charAt(r);
                  if ("j" === n) {
                    for (var o = 0; r + 1 < e.length && e.charAt(r + 1) === n;) o++, r++;
                    var a = 1 + (1 & o),
                      s = o < 2 ? 1 : 3 + (o >> 1),
                      l = Ct(t);
                    for ("H" != l && "k" != l || (s = 0); s-- > 0;) i += "a";
                    for (; a-- > 0;) i = l + i;
                  } else i += "J" === n ? "H" : n;
                }
                return i;
              }(d, this.locale));
              var g = {
                type: it.dateTime,
                pattern: p,
                location: c.styleLocation,
                parsedOptions: this.shouldParseSkeletons ? vt(p) : {}
              };
              return {
                val: {
                  type: "date" === s ? tt.date : tt.time,
                  value: i,
                  location: u,
                  style: g
                },
                err: null
              };
            }
            return {
              val: {
                type: "number" === s ? tt.number : "date" === s ? tt.date : tt.time,
                value: i,
                location: u,
                style: null !== (o = null == c ? void 0 : c.style) && void 0 !== o ? o : null
              },
              err: null
            };
          case "plural":
          case "selectordinal":
          case "select":
            var m = this.clonePosition();
            if (this.bumpSpace(), !this.bumpIf(",")) return this.error(et.EXPECT_SELECT_ARGUMENT_OPTIONS, Pt(m, r({}, m)));
            this.bumpSpace();
            var f = this.parseIdentifierIfPossible(),
              b = 0;
            if ("select" !== s && "offset" === f.value) {
              if (!this.bumpIf(":")) return this.error(et.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE, Pt(this.clonePosition(), this.clonePosition()));
              var v;
              if (this.bumpSpace(), (v = this.tryParseDecimalInteger(et.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE, et.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE)).err) return v;
              this.bumpSpace(), f = this.parseIdentifierIfPossible(), b = v.val;
            }
            var _,
              y = this.tryParsePluralOrSelectOptions(e, s, t, f);
            if (y.err) return y;
            if ((_ = this.tryParseArgumentClose(n)).err) return _;
            var w = Pt(n, this.clonePosition());
            return "select" === s ? {
              val: {
                type: tt.select,
                value: i,
                options: jt(y.val),
                location: w
              },
              err: null
            } : {
              val: {
                type: tt.plural,
                value: i,
                options: jt(y.val),
                offset: b,
                pluralType: "plural" === s ? "cardinal" : "ordinal",
                location: w
              },
              err: null
            };
          default:
            return this.error(et.INVALID_ARGUMENT_TYPE, Pt(a, l));
        }
      }, e.prototype.tryParseArgumentClose = function (e) {
        return this.isEOF() || 125 !== this.char() ? this.error(et.EXPECT_ARGUMENT_CLOSING_BRACE, Pt(e, this.clonePosition())) : (this.bump(), {
          val: !0,
          err: null
        });
      }, e.prototype.parseSimpleArgStyleIfPossible = function () {
        for (var e = 0, t = this.clonePosition(); !this.isEOF();) {
          switch (this.char()) {
            case 39:
              this.bump();
              var i = this.clonePosition();
              if (!this.bumpUntil("'")) return this.error(et.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE, Pt(i, this.clonePosition()));
              this.bump();
              break;
            case 123:
              e += 1, this.bump();
              break;
            case 125:
              if (!(e > 0)) return {
                val: this.message.slice(t.offset, this.offset()),
                err: null
              };
              e -= 1;
              break;
            default:
              this.bump();
          }
        }
        return {
          val: this.message.slice(t.offset, this.offset()),
          err: null
        };
      }, e.prototype.parseNumberSkeletonFromString = function (e, t) {
        var i = [];
        try {
          i = function (e) {
            if (0 === e.length) throw new Error("Number skeleton cannot be empty");
            for (var t = e.split(_t).filter(function (e) {
                return e.length > 0;
              }), i = [], r = 0, n = t; r < n.length; r++) {
              var o = n[r].split("/");
              if (0 === o.length) throw new Error("Invalid number skeleton");
              for (var a = o[0], s = o.slice(1), l = 0, c = s; l < c.length; l++) if (0 === c[l].length) throw new Error("Invalid number skeleton");
              i.push({
                stem: a,
                options: s
              });
            }
            return i;
          }(e);
        } catch (e) {
          return this.error(et.INVALID_NUMBER_SKELETON, t);
        }
        return {
          val: {
            type: it.number,
            tokens: i,
            location: t,
            parsedOptions: this.shouldParseSkeletons ? $t(i) : {}
          },
          err: null
        };
      }, e.prototype.tryParsePluralOrSelectOptions = function (e, t, i, r) {
        for (var n, o = !1, a = [], s = new Set(), l = r.value, c = r.location;;) {
          if (0 === l.length) {
            var h = this.clonePosition();
            if ("select" === t || !this.bumpIf("=")) break;
            var u = this.tryParseDecimalInteger(et.EXPECT_PLURAL_ARGUMENT_SELECTOR, et.INVALID_PLURAL_ARGUMENT_SELECTOR);
            if (u.err) return u;
            c = Pt(h, this.clonePosition()), l = this.message.slice(h.offset, this.offset());
          }
          if (s.has(l)) return this.error("select" === t ? et.DUPLICATE_SELECT_ARGUMENT_SELECTOR : et.DUPLICATE_PLURAL_ARGUMENT_SELECTOR, c);
          "other" === l && (o = !0), this.bumpSpace();
          var d = this.clonePosition();
          if (!this.bumpIf("{")) return this.error("select" === t ? et.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT : et.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT, Pt(this.clonePosition(), this.clonePosition()));
          var p = this.parseMessage(e + 1, t, i);
          if (p.err) return p;
          var g = this.tryParseArgumentClose(d);
          if (g.err) return g;
          a.push([l, {
            value: p.val,
            location: Pt(d, this.clonePosition())
          }]), s.add(l), this.bumpSpace(), l = (n = this.parseIdentifierIfPossible()).value, c = n.location;
        }
        return 0 === a.length ? this.error("select" === t ? et.EXPECT_SELECT_ARGUMENT_SELECTOR : et.EXPECT_PLURAL_ARGUMENT_SELECTOR, Pt(this.clonePosition(), this.clonePosition())) : this.requiresOtherClause && !o ? this.error(et.MISSING_OTHER_CLAUSE, Pt(this.clonePosition(), this.clonePosition())) : {
          val: a,
          err: null
        };
      }, e.prototype.tryParseDecimalInteger = function (e, t) {
        var i = 1,
          r = this.clonePosition();
        this.bumpIf("+") || this.bumpIf("-") && (i = -1);
        for (var n = !1, o = 0; !this.isEOF();) {
          var a = this.char();
          if (!(a >= 48 && a <= 57)) break;
          n = !0, o = 10 * o + (a - 48), this.bump();
        }
        var s = Pt(r, this.clonePosition());
        return n ? Dt(o *= i) ? {
          val: o,
          err: null
        } : this.error(t, s) : this.error(e, s);
      }, e.prototype.offset = function () {
        return this.position.offset;
      }, e.prototype.isEOF = function () {
        return this.offset() === this.message.length;
      }, e.prototype.clonePosition = function () {
        return {
          offset: this.position.offset,
          line: this.position.line,
          column: this.position.column
        };
      }, e.prototype.char = function () {
        var e = this.position.offset;
        if (e >= this.message.length) throw Error("out of bound");
        var t = Vt(this.message, e);
        if (void 0 === t) throw Error("Offset ".concat(e, " is at invalid UTF-16 code unit boundary"));
        return t;
      }, e.prototype.error = function (e, t) {
        return {
          val: null,
          err: {
            kind: e,
            message: this.message,
            location: t
          }
        };
      }, e.prototype.bump = function () {
        if (!this.isEOF()) {
          var e = this.char();
          10 === e ? (this.position.line += 1, this.position.column = 1, this.position.offset += 1) : (this.position.column += 1, this.position.offset += e < 65536 ? 1 : 2);
        }
      }, e.prototype.bumpIf = function (e) {
        if (Wt(this.message, e, this.offset())) {
          for (var t = 0; t < e.length; t++) this.bump();
          return !0;
        }
        return !1;
      }, e.prototype.bumpUntil = function (e) {
        var t = this.offset(),
          i = this.message.indexOf(e, t);
        return i >= 0 ? (this.bumpTo(i), !0) : (this.bumpTo(this.message.length), !1);
      }, e.prototype.bumpTo = function (e) {
        if (this.offset() > e) throw Error("targetOffset ".concat(e, " must be greater than or equal to the current offset ").concat(this.offset()));
        for (e = Math.min(e, this.message.length);;) {
          var t = this.offset();
          if (t === e) break;
          if (t > e) throw Error("targetOffset ".concat(e, " is at invalid UTF-16 code unit boundary"));
          if (this.bump(), this.isEOF()) break;
        }
      }, e.prototype.bumpSpace = function () {
        for (; !this.isEOF() && ii(this.char());) this.bump();
      }, e.prototype.peek = function () {
        if (this.isEOF()) return null;
        var e = this.char(),
          t = this.offset(),
          i = this.message.charCodeAt(t + (e >= 65536 ? 2 : 1));
        return null != i ? i : null;
      }, e;
    }();
  function ei(e) {
    return e >= 97 && e <= 122 || e >= 65 && e <= 90;
  }
  function ti(e) {
    return 45 === e || 46 === e || e >= 48 && e <= 57 || 95 === e || e >= 97 && e <= 122 || e >= 65 && e <= 90 || 183 == e || e >= 192 && e <= 214 || e >= 216 && e <= 246 || e >= 248 && e <= 893 || e >= 895 && e <= 8191 || e >= 8204 && e <= 8205 || e >= 8255 && e <= 8256 || e >= 8304 && e <= 8591 || e >= 11264 && e <= 12271 || e >= 12289 && e <= 55295 || e >= 63744 && e <= 64975 || e >= 65008 && e <= 65533 || e >= 65536 && e <= 983039;
  }
  function ii(e) {
    return e >= 9 && e <= 13 || 32 === e || 133 === e || e >= 8206 && e <= 8207 || 8232 === e || 8233 === e;
  }
  function ri(e) {
    return e >= 33 && e <= 35 || 36 === e || e >= 37 && e <= 39 || 40 === e || 41 === e || 42 === e || 43 === e || 44 === e || 45 === e || e >= 46 && e <= 47 || e >= 58 && e <= 59 || e >= 60 && e <= 62 || e >= 63 && e <= 64 || 91 === e || 92 === e || 93 === e || 94 === e || 96 === e || 123 === e || 124 === e || 125 === e || 126 === e || 161 === e || e >= 162 && e <= 165 || 166 === e || 167 === e || 169 === e || 171 === e || 172 === e || 174 === e || 176 === e || 177 === e || 182 === e || 187 === e || 191 === e || 215 === e || 247 === e || e >= 8208 && e <= 8213 || e >= 8214 && e <= 8215 || 8216 === e || 8217 === e || 8218 === e || e >= 8219 && e <= 8220 || 8221 === e || 8222 === e || 8223 === e || e >= 8224 && e <= 8231 || e >= 8240 && e <= 8248 || 8249 === e || 8250 === e || e >= 8251 && e <= 8254 || e >= 8257 && e <= 8259 || 8260 === e || 8261 === e || 8262 === e || e >= 8263 && e <= 8273 || 8274 === e || 8275 === e || e >= 8277 && e <= 8286 || e >= 8592 && e <= 8596 || e >= 8597 && e <= 8601 || e >= 8602 && e <= 8603 || e >= 8604 && e <= 8607 || 8608 === e || e >= 8609 && e <= 8610 || 8611 === e || e >= 8612 && e <= 8613 || 8614 === e || e >= 8615 && e <= 8621 || 8622 === e || e >= 8623 && e <= 8653 || e >= 8654 && e <= 8655 || e >= 8656 && e <= 8657 || 8658 === e || 8659 === e || 8660 === e || e >= 8661 && e <= 8691 || e >= 8692 && e <= 8959 || e >= 8960 && e <= 8967 || 8968 === e || 8969 === e || 8970 === e || 8971 === e || e >= 8972 && e <= 8991 || e >= 8992 && e <= 8993 || e >= 8994 && e <= 9e3 || 9001 === e || 9002 === e || e >= 9003 && e <= 9083 || 9084 === e || e >= 9085 && e <= 9114 || e >= 9115 && e <= 9139 || e >= 9140 && e <= 9179 || e >= 9180 && e <= 9185 || e >= 9186 && e <= 9254 || e >= 9255 && e <= 9279 || e >= 9280 && e <= 9290 || e >= 9291 && e <= 9311 || e >= 9472 && e <= 9654 || 9655 === e || e >= 9656 && e <= 9664 || 9665 === e || e >= 9666 && e <= 9719 || e >= 9720 && e <= 9727 || e >= 9728 && e <= 9838 || 9839 === e || e >= 9840 && e <= 10087 || 10088 === e || 10089 === e || 10090 === e || 10091 === e || 10092 === e || 10093 === e || 10094 === e || 10095 === e || 10096 === e || 10097 === e || 10098 === e || 10099 === e || 10100 === e || 10101 === e || e >= 10132 && e <= 10175 || e >= 10176 && e <= 10180 || 10181 === e || 10182 === e || e >= 10183 && e <= 10213 || 10214 === e || 10215 === e || 10216 === e || 10217 === e || 10218 === e || 10219 === e || 10220 === e || 10221 === e || 10222 === e || 10223 === e || e >= 10224 && e <= 10239 || e >= 10240 && e <= 10495 || e >= 10496 && e <= 10626 || 10627 === e || 10628 === e || 10629 === e || 10630 === e || 10631 === e || 10632 === e || 10633 === e || 10634 === e || 10635 === e || 10636 === e || 10637 === e || 10638 === e || 10639 === e || 10640 === e || 10641 === e || 10642 === e || 10643 === e || 10644 === e || 10645 === e || 10646 === e || 10647 === e || 10648 === e || e >= 10649 && e <= 10711 || 10712 === e || 10713 === e || 10714 === e || 10715 === e || e >= 10716 && e <= 10747 || 10748 === e || 10749 === e || e >= 10750 && e <= 11007 || e >= 11008 && e <= 11055 || e >= 11056 && e <= 11076 || e >= 11077 && e <= 11078 || e >= 11079 && e <= 11084 || e >= 11085 && e <= 11123 || e >= 11124 && e <= 11125 || e >= 11126 && e <= 11157 || 11158 === e || e >= 11159 && e <= 11263 || e >= 11776 && e <= 11777 || 11778 === e || 11779 === e || 11780 === e || 11781 === e || e >= 11782 && e <= 11784 || 11785 === e || 11786 === e || 11787 === e || 11788 === e || 11789 === e || e >= 11790 && e <= 11798 || 11799 === e || e >= 11800 && e <= 11801 || 11802 === e || 11803 === e || 11804 === e || 11805 === e || e >= 11806 && e <= 11807 || 11808 === e || 11809 === e || 11810 === e || 11811 === e || 11812 === e || 11813 === e || 11814 === e || 11815 === e || 11816 === e || 11817 === e || e >= 11818 && e <= 11822 || 11823 === e || e >= 11824 && e <= 11833 || e >= 11834 && e <= 11835 || e >= 11836 && e <= 11839 || 11840 === e || 11841 === e || 11842 === e || e >= 11843 && e <= 11855 || e >= 11856 && e <= 11857 || 11858 === e || e >= 11859 && e <= 11903 || e >= 12289 && e <= 12291 || 12296 === e || 12297 === e || 12298 === e || 12299 === e || 12300 === e || 12301 === e || 12302 === e || 12303 === e || 12304 === e || 12305 === e || e >= 12306 && e <= 12307 || 12308 === e || 12309 === e || 12310 === e || 12311 === e || 12312 === e || 12313 === e || 12314 === e || 12315 === e || 12316 === e || 12317 === e || e >= 12318 && e <= 12319 || 12320 === e || 12336 === e || 64830 === e || 64831 === e || e >= 65093 && e <= 65094;
  }
  function ni(e) {
    e.forEach(function (e) {
      if (delete e.location, ht(e) || ut(e)) for (var t in e.options) delete e.options[t].location, ni(e.options[t].value);else st(e) && gt(e.style) || (lt(e) || ct(e)) && mt(e.style) ? delete e.style.location : pt(e) && ni(e.children);
    });
  }
  function oi(e, t) {
    void 0 === t && (t = {}), t = r({
      shouldParseSkeletons: !0,
      requiresOtherClause: !0
    }, t);
    var i = new Qt(e, t).parse();
    if (i.err) {
      var n = SyntaxError(et[i.err.kind]);
      throw n.location = i.err.location, n.originalMessage = i.err.message, n;
    }
    return (null == t ? void 0 : t.captureLocation) || ni(i.val), i.val;
  }
  !function (e) {
    e.MISSING_VALUE = "MISSING_VALUE", e.INVALID_VALUE = "INVALID_VALUE", e.MISSING_INTL_API = "MISSING_INTL_API";
  }(Jt || (Jt = {}));
  var ai,
    si = function (e) {
      function t(t, i, r) {
        var n = e.call(this, t) || this;
        return n.code = i, n.originalMessage = r, n;
      }
      return i(t, e), t.prototype.toString = function () {
        return "[formatjs Error: ".concat(this.code, "] ").concat(this.message);
      }, t;
    }(Error),
    li = function (e) {
      function t(t, i, r, n) {
        return e.call(this, 'Invalid values for "'.concat(t, '": "').concat(i, '". Options are "').concat(Object.keys(r).join('", "'), '"'), Jt.INVALID_VALUE, n) || this;
      }
      return i(t, e), t;
    }(si),
    ci = function (e) {
      function t(t, i, r) {
        return e.call(this, 'Value for "'.concat(t, '" must be of type ').concat(i), Jt.INVALID_VALUE, r) || this;
      }
      return i(t, e), t;
    }(si),
    hi = function (e) {
      function t(t, i) {
        return e.call(this, 'The intl string context variable "'.concat(t, '" was not provided to the string "').concat(i, '"'), Jt.MISSING_VALUE, i) || this;
      }
      return i(t, e), t;
    }(si);
  function ui(e) {
    return "function" == typeof e;
  }
  function di(e, t, i, r, n, o, a) {
    if (1 === e.length && ot(e[0])) return [{
      type: ai.literal,
      value: e[0].value
    }];
    for (var s = [], l = 0, c = e; l < c.length; l++) {
      var h = c[l];
      if (ot(h)) s.push({
        type: ai.literal,
        value: h.value
      });else if (dt(h)) "number" == typeof o && s.push({
        type: ai.literal,
        value: i.getNumberFormat(t).format(o)
      });else {
        var u = h.value;
        if (!n || !(u in n)) throw new hi(u, a);
        var d = n[u];
        if (at(h)) d && "string" != typeof d && "number" != typeof d || (d = "string" == typeof d || "number" == typeof d ? String(d) : ""), s.push({
          type: "string" == typeof d ? ai.literal : ai.object,
          value: d
        });else if (lt(h)) {
          var p = "string" == typeof h.style ? r.date[h.style] : mt(h.style) ? h.style.parsedOptions : void 0;
          s.push({
            type: ai.literal,
            value: i.getDateTimeFormat(t, p).format(d)
          });
        } else if (ct(h)) {
          p = "string" == typeof h.style ? r.time[h.style] : mt(h.style) ? h.style.parsedOptions : r.time.medium;
          s.push({
            type: ai.literal,
            value: i.getDateTimeFormat(t, p).format(d)
          });
        } else if (st(h)) {
          (p = "string" == typeof h.style ? r.number[h.style] : gt(h.style) ? h.style.parsedOptions : void 0) && p.scale && (d *= p.scale || 1), s.push({
            type: ai.literal,
            value: i.getNumberFormat(t, p).format(d)
          });
        } else {
          if (pt(h)) {
            var g = h.children,
              m = h.value,
              f = n[m];
            if (!ui(f)) throw new ci(m, "function", a);
            var b = f(di(g, t, i, r, n, o).map(function (e) {
              return e.value;
            }));
            Array.isArray(b) || (b = [b]), s.push.apply(s, b.map(function (e) {
              return {
                type: "string" == typeof e ? ai.literal : ai.object,
                value: e
              };
            }));
          }
          if (ht(h)) {
            if (!(v = h.options[d] || h.options.other)) throw new li(h.value, d, Object.keys(h.options), a);
            s.push.apply(s, di(v.value, t, i, r, n));
          } else if (ut(h)) {
            var v;
            if (!(v = h.options["=".concat(d)])) {
              if (!Intl.PluralRules) throw new si('Intl.PluralRules is not available in this environment.\nTry polyfilling it using "@formatjs/intl-pluralrules"\n', Jt.MISSING_INTL_API, a);
              var _ = i.getPluralRules(t, {
                type: h.pluralType
              }).select(d - (h.offset || 0));
              v = h.options[_] || h.options.other;
            }
            if (!v) throw new li(h.value, d, Object.keys(h.options), a);
            s.push.apply(s, di(v.value, t, i, r, n, d - (h.offset || 0)));
          } else ;
        }
      }
    }
    return function (e) {
      return e.length < 2 ? e : e.reduce(function (e, t) {
        var i = e[e.length - 1];
        return i && i.type === ai.literal && t.type === ai.literal ? i.value += t.value : e.push(t), e;
      }, []);
    }(s);
  }
  function pi(e, t) {
    return t ? Object.keys(e).reduce(function (i, n) {
      var o, a;
      return i[n] = (o = e[n], (a = t[n]) ? r(r(r({}, o || {}), a || {}), Object.keys(o).reduce(function (e, t) {
        return e[t] = r(r({}, o[t]), a[t] || {}), e;
      }, {})) : o), i;
    }, r({}, e)) : e;
  }
  function gi(e) {
    return {
      create: function () {
        return {
          get: function (t) {
            return e[t];
          },
          set: function (t, i) {
            e[t] = i;
          }
        };
      }
    };
  }
  !function (e) {
    e[e.literal = 0] = "literal", e[e.object = 1] = "object";
  }(ai || (ai = {}));
  var mi = function () {
      function e(t, i, n, a) {
        void 0 === i && (i = e.defaultLocale);
        var s,
          l = this;
        if (this.formatterCache = {
          number: {},
          dateTime: {},
          pluralRules: {}
        }, this.format = function (e) {
          var t = l.formatToParts(e);
          if (1 === t.length) return t[0].value;
          var i = t.reduce(function (e, t) {
            return e.length && t.type === ai.literal && "string" == typeof e[e.length - 1] ? e[e.length - 1] += t.value : e.push(t.value), e;
          }, []);
          return i.length <= 1 ? i[0] || "" : i;
        }, this.formatToParts = function (e) {
          return di(l.ast, l.locales, l.formatters, l.formats, e, void 0, l.message);
        }, this.resolvedOptions = function () {
          var e;
          return {
            locale: (null === (e = l.resolvedLocale) || void 0 === e ? void 0 : e.toString()) || Intl.NumberFormat.supportedLocalesOf(l.locales)[0]
          };
        }, this.getAst = function () {
          return l.ast;
        }, this.locales = i, this.resolvedLocale = e.resolveLocale(i), "string" == typeof t) {
          if (this.message = t, !e.__parse) throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");
          var c = a || {};
          c.formatters;
          var h = function (e, t) {
            var i = {};
            for (var r in e) Object.prototype.hasOwnProperty.call(e, r) && t.indexOf(r) < 0 && (i[r] = e[r]);
            if (null != e && "function" == typeof Object.getOwnPropertySymbols) {
              var n = 0;
              for (r = Object.getOwnPropertySymbols(e); n < r.length; n++) t.indexOf(r[n]) < 0 && Object.prototype.propertyIsEnumerable.call(e, r[n]) && (i[r[n]] = e[r[n]]);
            }
            return i;
          }(c, ["formatters"]);
          this.ast = e.__parse(t, r(r({}, h), {
            locale: this.resolvedLocale
          }));
        } else this.ast = t;
        if (!Array.isArray(this.ast)) throw new TypeError("A message must be provided as a String or AST.");
        this.formats = pi(e.formats, n), this.formatters = a && a.formatters || (void 0 === (s = this.formatterCache) && (s = {
          number: {},
          dateTime: {},
          pluralRules: {}
        }), {
          getNumberFormat: Ve(function () {
            for (var e, t = [], i = 0; i < arguments.length; i++) t[i] = arguments[i];
            return new ((e = Intl.NumberFormat).bind.apply(e, o([void 0], t, !1)))();
          }, {
            cache: gi(s.number),
            strategy: nt.variadic
          }),
          getDateTimeFormat: Ve(function () {
            for (var e, t = [], i = 0; i < arguments.length; i++) t[i] = arguments[i];
            return new ((e = Intl.DateTimeFormat).bind.apply(e, o([void 0], t, !1)))();
          }, {
            cache: gi(s.dateTime),
            strategy: nt.variadic
          }),
          getPluralRules: Ve(function () {
            for (var e, t = [], i = 0; i < arguments.length; i++) t[i] = arguments[i];
            return new ((e = Intl.PluralRules).bind.apply(e, o([void 0], t, !1)))();
          }, {
            cache: gi(s.pluralRules),
            strategy: nt.variadic
          })
        });
      }
      return Object.defineProperty(e, "defaultLocale", {
        get: function () {
          return e.memoizedDefaultLocale || (e.memoizedDefaultLocale = new Intl.NumberFormat().resolvedOptions().locale), e.memoizedDefaultLocale;
        },
        enumerable: !1,
        configurable: !0
      }), e.memoizedDefaultLocale = null, e.resolveLocale = function (e) {
        if (void 0 !== Intl.Locale) {
          var t = Intl.NumberFormat.supportedLocalesOf(e);
          return t.length > 0 ? new Intl.Locale(t[0]) : new Intl.Locale("string" == typeof e ? e : e[0]);
        }
      }, e.__parse = oi, e.formats = {
        number: {
          integer: {
            maximumFractionDigits: 0
          },
          currency: {
            style: "currency"
          },
          percent: {
            style: "percent"
          }
        },
        date: {
          short: {
            month: "numeric",
            day: "numeric",
            year: "2-digit"
          },
          medium: {
            month: "short",
            day: "numeric",
            year: "numeric"
          },
          long: {
            month: "long",
            day: "numeric",
            year: "numeric"
          },
          full: {
            weekday: "long",
            month: "long",
            day: "numeric",
            year: "numeric"
          }
        },
        time: {
          short: {
            hour: "numeric",
            minute: "numeric"
          },
          medium: {
            hour: "numeric",
            minute: "numeric",
            second: "numeric"
          },
          long: {
            hour: "numeric",
            minute: "numeric",
            second: "numeric",
            timeZoneName: "short"
          },
          full: {
            hour: "numeric",
            minute: "numeric",
            second: "numeric",
            timeZoneName: "short"
          }
        }
      }, e;
    }(),
    fi = mi;
  const bi = {
      en: je
    },
    vi = {};
  function _i(e) {
    return e.replace(/['"]+/g, "").split(/[-_]/)[0].toLowerCase();
  }
  function yi(e) {
    const t = _i(e);
    return t in bi || !_e.includes(t);
  }
  function wi(e, t, ...i) {
    const r = _i(t);
    let n;
    try {
      n = e.split(".").reduce((e, t) => e[t], bi[r]);
    } catch (t) {
      n = e.split(".").reduce((e, t) => e[t], bi.en);
    }
    if (void 0 === n && (n = e.split(".").reduce((e, t) => e[t], bi.en)), !i.length) return n;
    const o = {};
    for (let e = 0; e < i.length; e += 2) {
      let t = i[e];
      t = t.replace(/^{([^}]+)?}$/, "$1"), o[t] = i[e + 1];
    }
    try {
      return new fi(n, t).format(o);
    } catch (e) {
      return "Translation " + e;
    }
  }
  function Ei(e, t) {
    switch (t) {
      case "drainage_rate":
        return e.units == ye ? F`${ze("mm/h")}` : F`${ze("in/h")}`;
      case "precipitation_threshold_mm":
      case we:
        return e.units == ye ? F`${ze("mm")}` : F`${ze("in")}`;
      case "size":
        return e.units == ye ? F`${ze("m<sup>2</sup>")}` : F`${ze("sq ft")}`;
      case "throughput":
        return e.units == ye ? F`${ze("l/minute")}` : F`${ze("gal/minute")}`;
      default:
        return F``;
    }
  }
  const ki = (e, t, i = !1) => {
    var r, n, o;
    i ? history.replaceState(null, "", t) : history.pushState(null, "", t), r = window, n = "location-changed", o = {
      replace: i
    }, r.dispatchEvent(new CustomEvent(n, {
      detail: o,
      bubbles: !0,
      composed: !0,
      cancelable: !1
    }));
  };
  function Ai(e) {
    var t;
    if (!e) return "Unknown error";
    if ("string" == typeof e) return e;
    const i = e;
    return (null === (t = null == i ? void 0 : i.body) || void 0 === t ? void 0 : t.message) || (null == i ? void 0 : i.message) || (null == i ? void 0 : i.error) || JSON.stringify(e);
  }
  function xi(e, t) {
    e.dispatchEvent(new CustomEvent("hass-notification", {
      detail: {
        message: t
      },
      bubbles: !0,
      composed: !0
    }));
  }
  function Si(e, t, i, r) {
    var n;
    xi(e, `${wi(i, null !== (n = null == t ? void 0 : t.language) && void 0 !== n ? n : "en")}: ${Ai(r)}`);
  }
  const Ti = (e, ...t) => {
      let i = {
        page: e,
        params: {}
      };
      t.forEach(e => {
        "string" == typeof e ? i = Object.assign(Object.assign({}, i), {
          subpage: e
        }) : "params" in e ? i = Object.assign(Object.assign({}, i), {
          params: e.params
        }) : "filter" in e && (i = Object.assign(Object.assign({}, i), {
          filter: e.filter
        }));
      });
      const r = e => {
        let t = Object.keys(e);
        t = t.filter(t => e[t]), t.sort();
        let i = "";
        return t.forEach(t => {
          const r = e[t];
          i = i.length ? `${i}/${t}/${r}` : `${t}/${r}`;
        }), i;
      };
      let n = `/${ve}/${i.page}`;
      return i.subpage && (n = `${n}/${i.subpage}`), r(i.params).length && (n = `${n}/${r(i.params)}`), i.filter && (n = `${n}/filter/${r(i.filter)}`), n;
    },
    $i = u`
  /* Existing common styles */
  ha-card {
    display: flex;
    flex-direction: column;
    margin: 5px;
    max-width: calc(100vw - 10px);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
  }
  .card-header .name {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  span.dialog-header {
    font-size: 24px;
    letter-spacing: -0.012em;
    line-height: 48px;
    padding: 12px 16px 16px;
    display: block;
    margin-block: 0px;
    font-weight: 400;
  }

  div.warning {
    color: var(--error-color);
    margin-top: 20px;
  }

  div.checkbox-row {
    min-height: 40px;
    display: flex;
    align-items: center;
  }

  div.checkbox-row ha-switch {
    margin-right: 20px;
  }

  div.checkbox-row.right ha-switch {
    margin-left: 20px;
    position: absolute;
    right: 0px;
  }

  div.entity-row {
    display: flex;
    align-items: center;
    flex-direction: row;
    margin: 10px 0px;
  }
  div.entity-row .info {
    margin-left: 16px;
    flex: 1 0 60px;
  }
  div.entity-row .info,
  div.entity-row .info > * {
    color: var(--primary-text-color);
    transition: color 0.2s ease-in-out;
  }
  div.entity-row .secondary {
    display: block;
    color: var(--secondary-text-color);
    transition: color 0.2s ease-in-out;
  }
  div.entity-row state-badge {
    flex: 0 0 40px;
  }

  ha-dialog div.wrapper {
    margin-bottom: -20px;
  }

  ha-textfield {
    min-width: 220px;
  }

  a,
  a:visited {
    color: var(--primary-color);
  }

  ha-card settings-row:first-child,
  ha-card settings-row:first-of-type {
    border-top: 0px;
  }

  ha-card > ha-card {
    margin: 10px;
  }

  /* Common utility classes shared across views */
  .hidden {
    display: none;
  }

  /* Shared action button style (used instead of ha-button which may not load) */
  button.action-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    background: var(--primary-color);
    border: none;
    border-radius: 4px;
    color: var(--text-primary-color, white);
    cursor: pointer;
    font-family: var(--mdc-typography-button-font-family, Roboto, sans-serif);
    font-size: 0.875rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    padding: 8px 16px;
    text-transform: uppercase;
    transition: opacity 0.15s;
  }

  button.action-btn ha-icon {
    --mdc-icon-size: 18px;
    flex-shrink: 0;
  }

  button.action-btn:hover {
    opacity: 0.9;
  }

  button.action-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  button.action-btn.secondary {
    background: transparent;
    border: 1px solid var(--primary-color);
    color: var(--primary-color);
  }

  button.action-btn.secondary:hover {
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
    opacity: 1;
  }

  /* Dialog footer row (replaces ha-dialog-footer) */
  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 16px 0 8px;
    margin-top: 8px;
    border-top: 1px solid var(--divider-color);
  }

  .dialog-btn {
    background: transparent;
    border: 1px solid var(--primary-color);
    border-radius: 4px;
    color: var(--primary-color);
    cursor: pointer;
    font-family: var(--mdc-typography-button-font-family, Roboto, sans-serif);
    font-size: 0.875rem;
    font-weight: 500;
    padding: 8px 16px;
    text-transform: uppercase;
    transition: background 0.15s;
  }

  .dialog-btn:hover {
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
  }

  .dialog-btn-primary {
    background: var(--primary-color);
    color: var(--text-primary-color, white);
    border-color: var(--primary-color);
  }

  .dialog-btn-primary:hover {
    opacity: 0.9;
    background: var(--primary-color);
  }

  .dialog-btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .dialog-btn-danger {
    border-color: var(--error-color);
    color: var(--error-color);
  }

  .dialog-btn-danger:hover {
    background: rgba(var(--rgb-error-color, 244, 67, 54), 0.08);
  }

  .shortinput {
    width: 50px;
  }

  .loading-indicator {
    text-align: center;
    padding: 20px;
    color: var(--primary-text-color);
    font-style: italic;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }

  /* Lightweight CSS spinner — avoids depending on ha-circular-progress /
     ha-spinner, whose element name changed across HA versions. */
  .loading-indicator::before {
    content: "";
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 3px solid var(--divider-color, rgba(127, 127, 127, 0.3));
    border-top-color: var(--primary-color);
    animation: si-spin 0.8s linear infinite;
  }

  @keyframes si-spin {
    to {
      transform: rotate(360deg);
    }
  }

  .saving {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .saving-indicator {
    color: var(--primary-color);
    font-style: italic;
    margin-top: 8px;
    font-size: 0.9em;
  }

  /* Disabled input styling */
  button:disabled,
  select:disabled,
  input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* Common line/row layouts */
  .zoneline,
  .mappingsettingline,
  .schemaline {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 12px;
    align-items: center;
    margin-left: 0;
    margin-top: 8px;
    padding: 6px 8px;
    border-bottom: 1px solid var(--divider-color);
    font-size: 0.9em;
  }

  .zoneline label,
  .mappingsettingline label,
  .schemaline label {
    color: var(--primary-text-color);
    font-weight: 500;
  }

  .zoneline input,
  .zoneline select,
  .mappingsettingline input,
  .mappingsettingline select,
  .schemaline input,
  .schemaline select {
    justify-self: end;
  }

  /* Common container styles */
  .zone,
  .mapping {
    margin-top: 25px;
    margin-bottom: 25px;
  }

  /* Mapping-specific container */
  .mappingline {
    margin-top: 16px;
    padding: 8px;
    border: 1px solid var(--divider-color);
    border-radius: 4px;
  }

  /* Note/alert styles - consolidated */
  .weather-note,
  .calendar-note,
  .info-note {
    padding: 8px;
    background: var(--secondary-background-color);
    color: var(--secondary-text-color);
    border-radius: 4px;
    font-size: 0.9em;
    font-style: italic;
  }

  .info-note {
    margin-top: 16px;
    background: var(--warning-color);
    color: var(--text-primary-color);
  }

  /* Radio button group styling */
  .radio-group {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin: 8px 0;
  }

  .radio-group label {
    display: flex;
    align-items: center;
    gap: 4px;
    cursor: pointer;
  }

  .radio-group input[type="radio"] {
    margin: 0;
  }

  input[type="radio"] {
    margin-right: 5px;
    margin-left: 10px;
  }

  input[type="radio"] + label {
    margin-right: 15px;
  }

  /* Common header styles */
  .subheader,
  .mappingsettingname {
    font-weight: bold;
  }

  /* Load more button styling */
  .load-more {
    text-align: center;
    padding: 16px;
  }

  .load-more button {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
  }

  .load-more button:hover {
    background: var(--primary-color-dark, var(--primary-color));
  }

  /* Strikethrough utility */
  .strikethrough {
    text-decoration: line-through;
  }

  /* Information text styling */
  .information {
    margin-left: 20px;
    margin-top: 5px;
  }

  /* Calendar and weather table styles */
  .watering-calendar,
  .weather-records {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--divider-color);
  }

  .watering-calendar h4,
  .weather-records h4 {
    margin: 0 0 12px 0;
    font-size: 1em;
    font-weight: 500;
    color: var(--primary-text-color);
  }

  .calendar-table,
  .weather-table {
    display: grid;
    gap: 8px;
    font-size: 0.85em;
  }

  .calendar-table {
    grid-template-columns: 1fr 0.8fr 1fr 0.8fr 0.8fr;
  }

  .weather-table {
    grid-template-columns: 1fr 0.7fr 0.7fr 0.7fr 0.7fr 0.8fr 0.7fr 1fr;
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid var(--divider-color);
    border-radius: 4px;
  }

  .calendar-header,
  .weather-header {
    display: contents;
    font-weight: 500;
    color: var(--primary-text-color);
  }

  .calendar-header span,
  .weather-header span {
    padding: 4px;
    background: var(--card-background-color);
    border-bottom: 2px solid var(--primary-color);
  }

  .calendar-row,
  .weather-row {
    display: contents;
    color: var(--secondary-text-color);
  }

  .calendar-row span,
  .weather-row span {
    padding: 4px;
    border-bottom: 1px solid var(--divider-color);
  }

  .calendar-info {
    margin-top: 8px;
    padding: 4px 8px;
    background: var(--info-color, var(--primary-color));
    color: white;
    border-radius: 4px;
    font-size: 0.8em;
  }

  /* Zone info table styles */
  .zone-info-table {
    display: grid;
    grid-template-columns: 1fr;
    gap: 4px;
    margin-bottom: 16px;
  }

  .zone-info-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    padding: 6px 8px;
    border-bottom: 1px solid var(--divider-color);
    font-size: 0.9em;
  }

  .zone-info-label {
    color: var(--primary-text-color);
    font-weight: 500;
  }

  .zone-info-value {
    color: var(--secondary-text-color);
    text-align: right;
  }

  /* Info item styles */
  .info-item {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    align-items: center;
    margin-bottom: 8px;
    padding: 6px 8px;
    border-bottom: 1px solid var(--divider-color);
    font-size: 0.9em;
  }

  .info-item label {
    font-weight: 500;
    min-width: 120px;
    color: var(--primary-text-color);
  }

  .info-item .value {
    color: var(--secondary-text-color);
    font-family: monospace;
    text-align: right;
    justify-self: end;
  }

  .info-item.explanation {
    grid-template-columns: 1fr;
    align-items: flex-start;
  }

  .explanation-text {
    background: var(--card-background-color);
    border: 1px solid var(--divider-color);
    border-radius: 4px;
    padding: 8px;
    font-size: 0.9em;
    line-height: 1.4;
    white-space: pre-wrap;
    margin-top: 4px;
    width: 100%;
    box-sizing: border-box;
  }

  /* Action button containers for zones page */
  .action-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 16px;
    padding: 12px 8px;
    border-top: 1px solid var(--divider-color);
  }

  .action-buttons-left,
  .action-buttons-right {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  /* Labeled action button - generic class for all pages */
  .action-button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .action-button:hover {
    background-color: var(--secondary-background-color);
  }

  /* For zones page - left column has label on right of icon */
  .action-button-left {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
    flex-direction: row;
  }

  /* For zones page - right column has label on left of icon */
  .action-button-right {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
    text-align: right;
    justify-content: flex-end;
  }

  .action-button-left:hover,
  .action-button-right:hover {
    background-color: var(--secondary-background-color);
  }

  .action-button svg {
    flex-shrink: 0;
  }

  .action-button-label {
    font-size: 0.85em;
    color: var(--primary-text-color);
    white-space: nowrap;
  }
`;
  u`
  /* ha-dialog styles */
  ha-dialog {
    --mdc-dialog-min-width: 400px;
    --mdc-dialog-max-width: 600px;
    --mdc-dialog-heading-ink-color: var(--primary-text-color);
    --mdc-dialog-content-ink-color: var(--primary-text-color);
    --justify-action-buttons: space-between;
  }
  /* make dialog fullscreen on small screens */
  @media all and (max-width: 450px), all and (max-height: 500px) {
    ha-dialog {
      --mdc-dialog-min-width: calc(
        100vw - env(safe-area-inset-right) - env(safe-area-inset-left)
      );
      --mdc-dialog-max-width: calc(
        100vw - env(safe-area-inset-right) - env(safe-area-inset-left)
      );
      --mdc-dialog-min-height: 100%;
      --mdc-dialog-max-height: 100%;
      --vertial-align-dialog: flex-end;
      --ha-dialog-border-radius: 0px;
    }
  }
  ha-dialog div.description {
    margin-bottom: 10px;
  }
`;
  const Hi = e => String(e).padStart(2, "0");
  function zi(e) {
    return e instanceof Date ? e : new Date(e);
  }
  function Ci(e) {
    const t = zi(e);
    return `${Hi(t.getHours())}:${Hi(t.getMinutes())}`;
  }
  function Li(e, t) {
    return e.getFullYear() === t.getFullYear() && e.getMonth() === t.getMonth() && e.getDate() === t.getDate();
  }
  class Bi extends Ae(ce) {
    constructor() {
      super(...arguments), this.hideSettingsLinks = !1, this.actionsMode = "full", this.zones = [], this.isLoading = !0, this._initialLoadDone = !1, this.isSaving = !1, this._operationError = null, this._confirmIrrigate = null, this._skipDetailsOpen = !1, this._updateScheduled = !1;
    }
    _scheduleUpdate() {
      this._updateScheduled || (this._updateScheduled = !0, requestAnimationFrame(() => {
        this._updateScheduled = !1, this.requestUpdate();
      }));
    }
    firstUpdated() {
      be().then(() => this._scheduleUpdate()).catch(e => {
        console.error("Failed to load HA form:", e), this._scheduleUpdate();
      });
    }
    hassSubscribe() {
      return this._fetchData().catch(e => {
        console.error("Failed to fetch initial data:", e);
      }), [this.hass.connection.subscribeMessage(() => {
        this._fetchData().catch(e => {
          console.error("Failed to fetch data on config update:", e);
        });
      }, {
        type: ve + "_config_updated"
      })];
    }
    async _fetchData() {
      if (!this.hass) return;
      const e = !this._initialLoadDone;
      try {
        e && (this.isLoading = !0);
        const [i, r, n] = await Promise.all([(t = this.hass, t.callWS({
          type: ve + "/config"
        })), Ee(this.hass), ke(this.hass).catch(e => {
          console.error("Failed to fetch irrigation outlook:", e);
        })]);
        this.config = i, this.zones = r, this._outlook = n, this._initialLoadDone = !0;
      } catch (e) {
        console.error("Error fetching data:", e), Si(this, this.hass, "common.errors.load_failed", e);
      } finally {
        e && (this.isLoading = !1), this._scheduleUpdate();
      }
      var t;
    }
    handleCalculateAllZones() {
      var e;
      this.hass && (this.isSaving = !0, this._scheduleUpdate(), (e = this.hass, e.callApi("POST", ve + "/zones", {
        calculate_all: !0
      })).catch(e => {
        console.error("Failed to calculate all zones:", e), Si(this, this.hass, "common.errors.action_failed", e);
      }).finally(() => {
        this.isSaving = !1, this._fetchData().catch(e => console.error("fetchData after calc-all:", e));
      }));
    }
    handleUpdateAllZones() {
      var e;
      this.hass && (this.isSaving = !0, this._scheduleUpdate(), (e = this.hass, e.callApi("POST", ve + "/zones", {
        update_all: !0
      })).catch(e => {
        console.error("Failed to update all zones:", e), Si(this, this.hass, "common.errors.action_failed", e);
      }).finally(() => {
        this.isSaving = !1, this._fetchData().catch(e => console.error("fetchData after update-all:", e));
      }));
    }
    get _linkedZoneCount() {
      return this.zones.filter(e => {
        var t;
        return e.linked_entity && (null !== (t = e.duration) && void 0 !== t ? t : 0) > 0;
      }).length;
    }
    async _doIrrigate() {
      var e;
      const t = this._confirmIrrigate;
      if (this._confirmIrrigate = null, null === t || !this.hass) return;
      const i = "all" === t,
        r = i ? void 0 : this.zones.find(e => {
          var i;
          return (null === (i = e.id) || void 0 === i ? void 0 : i.toString()) === t;
        }),
        n = i ? `(${this._linkedZoneCount})` : `: ${null !== (e = null == r ? void 0 : r.name) && void 0 !== e ? e : t}`;
      try {
        await (o = this.hass, a = i ? void 0 : t, o.callWS(Object.assign({
          type: ve + "/irrigate_now"
        }, void 0 !== a ? {
          zone_id: a
        } : {}))), xi(this, `${wi("panels.zones.confirm_irrigate.toast_started", this.hass.language)} ${n}`);
      } catch (e) {
        const t = Ai(e);
        console.error("irrigate_now failed", e), xi(this, `${wi("panels.zones.confirm_irrigate.toast_failed", this.hass.language)}: ${t}`);
      }
      var o, a;
    }
    handleCalculateZone(e) {
      const t = this.zones[e];
      var i, r;
      t && null != t.id && this.hass && (this._operationError = null, this.isSaving = !0, this._scheduleUpdate(), (i = this.hass, r = t.id.toString(), i.callApi("POST", ve + "/zones", {
        id: r,
        calculate: !0,
        override_cache: !0
      })).catch(e => {
        const t = Ai(e);
        console.error("calculateZone failed:", e), this._operationError = t;
      }).finally(() => {
        this.isSaving = !1, this._fetchData().catch(e => console.error("fetchData after calc:", e));
      }));
    }
    handleUpdateZone(e) {
      const t = this.zones[e];
      var i, r;
      t && null != t.id && this.hass && (this._operationError = null, this.isSaving = !0, this._scheduleUpdate(), (i = this.hass, r = t.id.toString(), i.callApi("POST", ve + "/zones", {
        id: r,
        update: !0
      })).catch(e => {
        const t = Ai(e);
        console.error("updateZone failed:", e), this._operationError = t;
      }).finally(() => {
        this.isSaving = !1, this._fetchData().catch(e => console.error("fetchData after update:", e));
      }));
    }
    _openZoneSettings(e) {
      const t = void 0 !== e.id ? {
        params: {
          zone: String(e.id)
        }
      } : void 0;
      ki(0, t ? Ti("setup", "zones", t) : Ti("setup", "zones"));
    }
    _runTargetsZone(e, t) {
      return "all" === e.zones || !(!Array.isArray(e.zones) || void 0 === t.id) && e.zones.map(e => Number(e)).includes(Number(t.id));
    }
    get _nextIrrigateRun() {
      var e;
      return null === (e = this._outlook) || void 0 === e ? void 0 : e.upcoming_runs.find(e => "irrigate" === e.action && e.next_run_utc);
    }
    _nextIrrigateRunForZone(e) {
      var t;
      return null === (t = this._outlook) || void 0 === t ? void 0 : t.upcoming_runs.find(t => "irrigate" === t.action && t.next_run_utc && this._runTargetsZone(t, e));
    }
    get _activeGuards() {
      var e, t;
      return null !== (t = null === (e = this._outlook) || void 0 === e ? void 0 : e.skip_preview.checks.filter(e => e.enabled)) && void 0 !== t ? t : [];
    }
    get _triggeredGuards() {
      return this._activeGuards.filter(e => e.would_skip);
    }
    _zoneHasDeficit(e) {
      var t, i, r;
      const n = null !== (t = e.duration) && void 0 !== t ? t : 0,
        o = Number(null !== (i = e.bucket) && void 0 !== i ? i : 0),
        a = Number(null !== (r = e.bucket_threshold) && void 0 !== r ? r : 0);
      return n > 0 && o < a;
    }
    _formatRunTime(e) {
      if (!this.hass) return "";
      const t = this.hass.language,
        i = new Date(e),
        r = Ci(i),
        n = new Date();
      return Li(i, n) ? `${wi("panels.zones.outlook.today", t)} ${r}` : Li(i, function (e, t) {
        const i = new Date(e.getTime());
        return i.setDate(i.getDate() + t), i;
      }(n, 1)) ? `${wi("panels.zones.outlook.tomorrow", t)} ${r}` : function (e, t) {
        const i = zi(e);
        return `${new Intl.DateTimeFormat(t, {
          weekday: "short"
        }).format(i)} ${Ci(i)}`;
      }(i, t);
    }
    _guardLabel(e) {
      return wi(`panels.zones.outlook.checks.${e.id}`, this.hass.language);
    }
    _guardDetail(e) {
      var t;
      return e.available && null !== e.observed ? wi(`panels.zones.outlook.check_detail.${e.id}`, this.hass.language, "{observed}", String(e.observed), "{threshold}", String(null !== (t = e.threshold) && void 0 !== t ? t : "")) : "";
    }
    _renderSkipReasons() {
      const e = this.hass.language;
      return F`
      <div class="outlook-line outlook-skip-reasons">
        <ul class="skip-reasons">
          ${this._triggeredGuards.map(e => {
        const t = this._guardDetail(e);
        return F`<li>
              ${this._guardLabel(e)}${t ? F` — ${t}` : ""}
            </li>`;
      })}
        </ul>
      </div>
      <div class="outlook-line outlook-dim skip-reasons-note">
        ${wi("panels.zones.outlook.provisional", e)}
      </div>
    `;
    }
    _openSchedules() {
      ki(0, Ti("setup", "schedules"));
    }
    _runActionLabel(e) {
      return wi(`panels.zones.outlook.actions.${e.action}`, this.hass.language);
    }
    _runTargetsLabel(e) {
      const t = this.hass.language;
      if ("all" === e.zones) return wi("panels.zones.outlook.targets_all", t);
      const i = Array.isArray(e.zones) ? e.zones.length : 0;
      return wi("panels.zones.outlook.targets_zones", t, "{count}", String(i));
    }
    _renderOutlookBanner() {
      if (!this.hass || !this._outlook) return F``;
      const e = this.hass.language,
        t = this._nextIrrigateRun,
        i = this._triggeredGuards,
        r = this._outlook.last_skip_evaluation;
      return t && t.next_run_utc ? F`
      <ha-card class="outlook-card">
        <div class="outlook">
          <div class="outlook-line outlook-headline">
            <ha-icon icon="mdi:calendar-clock"></ha-icon>
            <span>
              <strong
                >${wi("panels.zones.outlook.next_run", e)}:</strong
              >
              ${this._runActionLabel(t)}
              ${this._formatRunTime(t.next_run_utc)}
              <span class="outlook-dim"
                >· ${t.name} · ${this._runTargetsLabel(t)}</span
              >
            </span>
          </div>

          ${i.length > 0 ? F`
                <div class="outlook-line outlook-skip">
                  <ha-icon icon="mdi:alert"></ha-icon>
                  <span
                    >${wi("panels.zones.outlook.will_skip", e)}</span
                  >
                  <button
                    class="outlook-info-btn"
                    aria-expanded="${this._skipDetailsOpen}"
                    title="${wi("panels.zones.outlook.why_skipped", e)}"
                    @click="${() => {
        this._skipDetailsOpen = !this._skipDetailsOpen;
      }}"
                  >
                    <ha-icon
                      icon="${this._skipDetailsOpen ? "mdi:chevron-up" : "mdi:information-outline"}"
                    ></ha-icon>
                    <span class="outlook-info-label"
                      >${wi("panels.zones.outlook.why_skipped", e)}</span
                    >
                  </button>
                </div>
                ${this._skipDetailsOpen ? this._renderSkipReasons() : ""}
              ` : F`
                <div class="outlook-line outlook-clear">
                  <ha-icon icon="mdi:check-circle-outline"></ha-icon>
                  <span
                    >${wi("panels.zones.outlook.will_run", e)}</span
                  >
                </div>
              `}
          ${r ? this._renderLastRunLine(r) : ""}
        </div>
      </ha-card>
    ` : F`
        <ha-card class="outlook-card">
          <div class="outlook">
            <div class="outlook-line outlook-headline">
              <ha-icon icon="mdi:calendar-alert"></ha-icon>
              <span>${wi("panels.zones.outlook.no_schedule", e)}</span>
              ${this.hideSettingsLinks ? "" : F`
                    <button
                      class="outlook-link"
                      @click="${this._openSchedules}"
                    >
                      ${wi("panels.zones.outlook.setup_schedule", e)}
                    </button>
                  `}
            </div>
            ${r ? this._renderLastRunLine(r) : ""}
          </div>
        </ha-card>
      `;
    }
    _renderLastRunLine(e) {
      const t = this.hass.language,
        i = function (e, t) {
          const i = zi(e).getTime() - Date.now(),
            r = new Intl.RelativeTimeFormat(t, {
              numeric: "auto"
            }),
            n = Math.round(i / 1e3);
          if (Math.abs(n) < 60) return r.format(n, "second");
          const o = Math.round(n / 60);
          if (Math.abs(o) < 60) return r.format(o, "minute");
          const a = Math.round(o / 60);
          if (Math.abs(a) < 24) return r.format(a, "hour");
          const s = Math.round(a / 24);
          if (Math.abs(s) < 30) return r.format(s, "day");
          const l = Math.round(s / 30);
          return Math.abs(l) < 12 ? r.format(l, "month") : r.format(Math.round(l / 12), "year");
        }(e.timestamp, t),
        r = e.checks.filter(e => e.enabled && e.would_skip).map(e => this._guardLabel(e).toLowerCase()).join(", "),
        n = e.would_skip ? `${wi("panels.zones.outlook.last_run_skipped", t)}${r ? ` (${r})` : ""}` : wi("panels.zones.outlook.last_run_ran", t);
      return F`
      <div class="outlook-line outlook-last">
        <span class="outlook-dim"
          >${wi("panels.zones.outlook.last_run", t)}:</span
        >
        <span>${n} · ${i}</span>
      </div>
    `;
    }
    _renderZoneDecision(e) {
      var t;
      if (!this.hass) return F``;
      const i = this.hass.language,
        r = null !== (t = e.duration) && void 0 !== t ? t : 0;
      let n, o, a;
      if (e.state === Se.Disabled) n = wi("panels.zones.status.decision_disabled", i), o = "neutral", a = "mdi:power-off";else if (e.last_calculated) {
        if (this._zoneHasDeficit(e)) {
          const t = function (e) {
              const t = Math.round(e);
              if (t < 60) return `${t} s`;
              const i = Math.floor(t / 60),
                r = t % 60;
              return r ? `${i} min ${r} s` : `${i} min`;
            }(r),
            s = this._triggeredGuards,
            l = this._nextIrrigateRunForZone(e);
          s.length > 0 ? (n = wi("panels.zones.status.decision_water_skip", i, "{duration}", t, "{reason}", this._guardLabel(s[0]).toLowerCase()), o = "skip", a = "mdi:weather-rainy") : l && l.next_run_utc ? (n = wi("panels.zones.status.decision_water_at", i, "{duration}", t, "{time}", this._formatRunTime(l.next_run_utc)), o = "water", a = "mdi:water") : (n = wi("panels.zones.status.decision_water_no_schedule", i, "{duration}", t), o = "water", a = "mdi:water-alert");
        } else n = wi("panels.zones.status.decision_no_water", i), o = "ok", a = "mdi:check-circle-outline";
      } else n = wi("panels.zones.status.decision_unknown", i), o = "unknown", a = "mdi:help-circle-outline";
      return F`
      <div class="zone-decision ${o}">
        <ha-icon icon="${a}"></ha-icon>
        <span>${n}</span>
      </div>
    `;
    }
    _zoneEstimate(e) {
      var t, i;
      if (void 0 !== e.id) return null === (i = null === (t = this._outlook) || void 0 === t ? void 0 : t.zone_estimates) || void 0 === i ? void 0 : i[String(e.id)];
    }
    _renderZoneEstimate(e) {
      if (!this.hass) return F``;
      const t = this._zoneEstimate(e);
      if (!t || !t.available || null == t.live_deficit) return F``;
      const i = this.hass.language,
        r = Ei(this.config, we),
        n = t.live_deficit < 0 ? "var(--warning-color)" : "var(--success-color)",
        o = wi(`panels.zones.status.estimate_method.${"proxy" === t.method ? "proxy" : "hourly"}`, i) + (t.as_of ? ` · ${Ci(t.as_of)}` : "");
      return F`
      <span class="status-sep">·</span>
      <span class="zone-estimate" title="${o}">
        ${wi("panels.zones.status.estimate_now", i)}
        <strong style="color: ${n}"
          >≈ ${t.live_deficit.toFixed(2)} ${r}</strong
        >
        <span class="estimate-tag"
          >${wi("panels.zones.status.estimate_tag", i)}</span
        >
      </span>
    `;
    }
    _renderZoneNextRun(e) {
      if (!this.hass) return F``;
      const t = this._nextIrrigateRunForZone(e);
      if (!t || !t.next_run_utc) return F``;
      return e.state !== Se.Disabled && e.last_calculated && this._zoneHasDeficit(e) && 0 === this._triggeredGuards.length ? F`` : F`
      <span class="status-sep">·</span>
      <span>
        ${wi("panels.zones.outlook.next_run", this.hass.language)}:
        <strong>${this._formatRunTime(t.next_run_utc)}</strong>
      </span>
    `;
    }
    renderZone(e, t) {
      var i, r;
      if (!this.hass) return F``;
      const n = Number(null !== (i = e.bucket) && void 0 !== i ? i : 0),
        o = n < 0 ? "var(--warning-color)" : "var(--success-color)",
        a = e.state === Se.Automatic ? "state-automatic" : e.state === Se.Manual ? "state-manual" : "state-disabled",
        s = e.last_calculated ? function (e) {
          const t = zi(e);
          return `${t.getFullYear()}-${Hi(t.getMonth() + 1)}-${Hi(t.getDate())} ${Hi(t.getHours())}:${Hi(t.getMinutes())}`;
        }(e.last_calculated) : wi("panels.zones.status.never", this.hass.language);
      return F`
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          <span class="zone-state-badge ${a}">
            ${wi(`panels.zones.labels.states.${e.state}`, this.hass.language)}
          </span>
          ${this.hideSettingsLinks ? "" : F`
                <ha-icon-button
                  .path="${"M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"}"
                  title="${wi("panels.zones.actions.open_settings", this.hass.language)}"
                  @click="${() => this._openZoneSettings(e)}"
                ></ha-icon-button>
              `}
        </div>

        <!-- AT-A-GLANCE DECISION -->
        ${this._renderZoneDecision(e)}

        <!-- COMPACT STATUS -->
        <div class="card-content">
          <div class="zone-status-line">
            <span
              title="${wi("panels.zones.help.bucket", this.hass.language)}"
            >
              ${wi("panels.zones.labels.bucket", this.hass.language)}:
              <strong style="color: ${o}"
                >${n.toFixed(2)}
                ${Ei(this.config, we)}</strong
              >
            </span>
            <span class="status-sep">·</span>
            <span>
              ${wi("panels.zones.status.last_checked", this.hass.language)}:
              <strong>${s}</strong>
            </span>
            ${this._renderZoneEstimate(e)} ${this._renderZoneNextRun(e)}
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div class="card-content zone-action-bar">
          ${"full" === this.actionsMode && e.state === Se.Automatic ? F`
                <button
                  class="action-btn"
                  title="${wi("panels.zones.help.update", this.hass.language)}"
                  @click="${() => this.handleUpdateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${wi("panels.zones.actions.update", this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${wi("panels.zones.help.calculate", this.hass.language)}"
                  @click="${() => this.handleCalculateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${wi("panels.zones.actions.calculate", this.hass.language)}
                </button>
              ` : ""}
          ${"none" !== this.actionsMode && e.linked_entity && (null !== (r = e.duration) && void 0 !== r ? r : 0) > 0 ? F`
                <button
                  class="action-btn"
                  raised
                  @click="${() => {
        void 0 !== e.id && (this._confirmIrrigate = e.id.toString());
      }}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${wi("panels.zones.labels.irrigate_now", this.hass.language)}
                </button>
              ` : e.linked_entity ? "" : F`
                  <button
                    class="action-btn"
                    disabled
                    title="${wi("panels.zones.help.irrigate_link_entity", this.hass.language)}"
                  >
                    <ha-icon icon="mdi:water"></ha-icon>
                    ${wi("panels.zones.labels.irrigate_now", this.hass.language)}
                  </button>
                  <span class="zones-top-note">
                    ${wi("panels.zones.help.irrigate_link_entity", this.hass.language)}
                  </span>
                `}
        </div>
      </ha-card>
    `;
    }
    render() {
      var e, t;
      if (!this.hass) return F``;
      if (this.isLoading) return F`
        <ha-card header="${wi("panels.zones.title", this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${wi("common.loading-messages.general", this.hass.language)}
            </div>
          </div>
        </ha-card>
      `;
      const i = this.zones.some(e => {
          var t;
          return e.linked_entity && (null !== (t = e.duration) && void 0 !== t ? t : 0) > 0;
        }),
        r = 0 === this.zones.length;
      return F`
      ${r ? this.hideSettingsLinks ? F`
              <ha-card>
                <div class="card-content description-text">
                  ${wi("panels.zones.no_items", this.hass.language)}
                </div>
              </ha-card>
            ` : F`
              <ha-card class="setup-banner-card">
                <div class="setup-banner">
                  <div class="setup-banner-icon">🌱</div>
                  <div class="setup-banner-content">
                    <div class="setup-banner-title">
                      ${wi("wizard.title", this.hass.language)}
                    </div>
                    <div class="setup-banner-desc">
                      ${wi("wizard.setup_complete_banner", this.hass.language)}
                    </div>
                  </div>
                  <button
                    class="action-btn setup-banner-btn"
                    @click="${() => {
        this.dispatchEvent(new CustomEvent("open-wizard", {
          bubbles: !0,
          composed: !0
        }));
      }}"
                  >
                    ${wi("wizard.open_wizard", this.hass.language)}
                  </button>
                </div>
              </ha-card>
            ` : ""}
      ${r ? "" : this._renderOutlookBanner()}

      <!-- Zones header card: run-all operational actions -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${wi("panels.zones.title", this.hass.language)}
          </div>
        </div>
        <div class="card-content zones-top-actions">
          ${"full" === this.actionsMode ? F`
                <button
                  class="action-btn"
                  title="${wi("panels.zones.help.update_all", this.hass.language)}"
                  @click="${this.handleUpdateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${wi("panels.zones.cards.zone-actions.actions.update-all", this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${wi("panels.zones.help.calculate_all", this.hass.language)}"
                  @click="${this.handleCalculateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${wi("panels.zones.cards.zone-actions.actions.calculate-all", this.hass.language)}
                </button>
              ` : ""}
          ${"none" !== this.actionsMode ? F`
                <button
                  class="action-btn"
                  raised
                  title="${wi("panels.zones.help.irrigate_all", this.hass.language)}"
                  @click="${() => {
        this._confirmIrrigate = "all";
      }}"
                  ?disabled="${!i || this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${wi("panels.zones.actions.irrigate_all", this.hass.language)}
                </button>
              ` : ""}
          ${i ? "" : F`<span class="zones-top-note"
                >${wi("panels.info.cards.irrigate_now.no_linked_zones", this.hass.language)}</span
              >`}
        </div>
      </ha-card>

      <!-- Irrigate confirmation dialog -->
      ${null !== this._confirmIrrigate ? F`
            <ha-dialog
              open
              @closed="${() => {
        this._confirmIrrigate = null;
      }}"
              heading="${wi("panels.zones.confirm_irrigate.title", this.hass.language)}"
            >
              <p>
                ${wi("panels.zones.confirm_irrigate.body", this.hass.language)}
              </p>
              <p>
                <strong>
                  ${"all" === this._confirmIrrigate ? `${wi("panels.zones.confirm_irrigate.all_linked_zones", this.hass.language)} (${this._linkedZoneCount})` : null !== (t = null === (e = this.zones.find(e => {
        var t;
        return (null === (t = e.id) || void 0 === t ? void 0 : t.toString()) === this._confirmIrrigate;
      })) || void 0 === e ? void 0 : e.name) && void 0 !== t ? t : this._confirmIrrigate}
                </strong>
              </p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${() => {
        this._confirmIrrigate = null;
      }}"
                >
                  ${wi("common.actions.cancel", this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._doIrrigate}"
                >
                  ${wi("panels.zones.labels.irrigate_now", this.hass.language)}
                </button>
              </div>
            </ha-dialog>
          ` : ""}

      <!-- Operation error banner -->
      ${this._operationError ? F`
            <ha-card class="error-banner-card">
              <div class="error-banner">
                <ha-icon
                  class="error-banner-icon"
                  icon="mdi:alert-circle-outline"
                ></ha-icon>
                <span class="error-banner-msg">${this._operationError}</span>
                <ha-icon-button
                  .path="${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}"
                  @click="${() => {
        this._operationError = null;
      }}"
                  aria-label="${wi("common.actions.cancel", this.hass.language)}"
                ></ha-icon-button>
              </div>
            </ha-card>
          ` : ""}

      <!-- Zone cards -->
      ${this.zones.map((e, t) => this.renderZone(e, t))}
    `;
    }
    static get styles() {
      return u`
      ${$i}

      /* At-a-glance decision line */
      .zone-decision {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0 16px 12px;
        padding: 10px 12px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 500;
        line-height: 1.35;
      }

      .zone-decision ha-icon {
        flex-shrink: 0;
        --mdc-icon-size: 22px;
      }

      .zone-decision.water {
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
        color: var(--primary-color);
      }

      .zone-decision.ok {
        background: rgba(76, 175, 80, 0.12);
        color: var(--success-color, #2e7d32);
      }

      .zone-decision.neutral {
        background: var(--secondary-background-color);
        color: var(--secondary-text-color);
      }

      .zone-decision.unknown {
        background: rgba(255, 152, 0, 0.12);
        color: var(--warning-color, #ed6c02);
      }

      .zone-decision.skip {
        background: rgba(255, 152, 0, 0.12);
        color: var(--warning-color, #ed6c02);
      }

      /* Global outlook banner — tinted like the per-zone status banners so the
         two read at the same visual weight. */
      .outlook-card {
        border-left: 4px solid var(--primary-color);
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.06);
      }

      .outlook {
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 14px 16px;
      }

      .outlook-line {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        font-size: 0.9rem;
        line-height: 1.35;
      }

      .outlook-line ha-icon {
        flex-shrink: 0;
        --mdc-icon-size: 20px;
      }

      .outlook-headline {
        font-size: 1rem;
        font-weight: 500;
      }

      .outlook-headline ha-icon {
        color: var(--primary-color);
      }

      .outlook-skip {
        color: var(--warning-color, #ed6c02);
      }

      .outlook-clear {
        color: var(--success-color, #2e7d32);
      }

      .outlook-dim {
        color: var(--secondary-text-color);
        font-weight: 400;
      }

      /* Tap-to-expand "why it will skip" toggle (works on touch + desktop) */
      .outlook-info-btn {
        display: inline-flex;
        align-items: center;
        gap: 2px;
        background: transparent;
        border: none;
        color: var(--warning-color, #ed6c02);
        cursor: pointer;
        font: inherit;
        padding: 4px 6px;
        border-radius: 6px;
      }

      .outlook-info-btn:hover {
        background: rgba(255, 152, 0, 0.12);
      }

      .outlook-info-btn ha-icon {
        --mdc-icon-size: 18px;
      }

      .outlook-info-label {
        font-size: 0.8125rem;
        text-decoration: underline;
      }

      /* Expanded skip reasons */
      .outlook-skip-reasons {
        color: var(--warning-color, #ed6c02);
      }

      .skip-reasons {
        margin: 0;
        padding-left: 18px;
        font-size: 0.85rem;
      }

      .skip-reasons li {
        margin: 2px 0;
      }

      .skip-reasons-note {
        font-size: 0.8rem;
        font-style: italic;
      }

      .outlook-link {
        background: transparent;
        border: none;
        color: var(--primary-color);
        cursor: pointer;
        font-family: inherit;
        font-size: 0.875rem;
        font-weight: 500;
        padding: 0;
        text-decoration: underline;
      }

      /* Compact one-line status */
      .zone-status-line {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px;
        font-size: 0.875rem;
        color: var(--secondary-text-color);
      }

      .zone-status-line strong {
        color: var(--primary-text-color);
        font-weight: 500;
      }

      .status-sep {
        opacity: 0.5;
      }

      /* Read-only "live" estimate chip */
      .zone-estimate {
        cursor: help;
      }

      .estimate-tag {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        opacity: 0.65;
      }

      /* Action bar */
      .zone-action-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding-top: 0;
        padding-bottom: 12px;
      }

      /* State badge */
      .zone-state-badge {
        font-size: 0.75rem;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        align-self: center;
        margin-left: auto;
      }

      .state-automatic {
        background: var(--success-color, #4caf50);
        color: white;
      }

      .state-manual {
        background: var(--accent-color, var(--primary-color));
        color: white;
      }

      .state-disabled {
        background: var(--disabled-color, #bdbdbd);
        color: white;
      }

      /* First-time setup banner */
      .setup-banner-card {
        border-left: 4px solid var(--primary-color);
      }

      .setup-banner {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px;
        flex-wrap: wrap;
      }

      .setup-banner-icon {
        font-size: 2rem;
        flex-shrink: 0;
      }

      .setup-banner-content {
        flex: 1;
        min-width: 180px;
      }

      .setup-banner-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--primary-text-color);
        margin-bottom: 4px;
      }

      .setup-banner-desc {
        font-size: 0.83rem;
        color: var(--secondary-text-color);
      }

      .setup-banner-btn {
        flex-shrink: 0;
      }

      .zones-top-actions {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
      }

      .zones-top-note {
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
        font-style: italic;
      }

      /* Dialog footer buttons */
      .dialog-footer {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        padding: 16px 0 8px;
        margin-top: 8px;
        border-top: 1px solid var(--divider-color);
      }

      .dialog-btn {
        background: transparent;
        border: 1px solid var(--primary-color);
        border-radius: 4px;
        color: var(--primary-color);
        cursor: pointer;
        font-family: inherit;
        font-size: 0.875rem;
        font-weight: 500;
        padding: 8px 16px;
        transition: background 0.15s;
      }

      .dialog-btn:hover {
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
      }

      .dialog-btn-primary {
        background: var(--primary-color);
        color: var(--text-primary-color, white);
      }

      .dialog-btn-primary:hover {
        opacity: 0.9;
        background: var(--primary-color);
      }

      /* Operation error banner */
      .error-banner-card {
        border-left: 4px solid var(--error-color, #f44336);
      }

      .error-banner {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 8px 8px 16px;
      }

      .error-banner-icon {
        color: var(--error-color, #f44336);
        flex-shrink: 0;
      }

      .error-banner-msg {
        flex: 1;
        color: var(--error-color, #f44336);
        font-size: 0.9rem;
        line-height: 1.4;
      }
    `;
    }
  }
  n([de()], Bi.prototype, "config", void 0), n([de({
    type: Boolean
  })], Bi.prototype, "hideSettingsLinks", void 0), n([de({
    attribute: !1
  })], Bi.prototype, "actionsMode", void 0), n([de({
    type: Array
  })], Bi.prototype, "zones", void 0), n([pe()], Bi.prototype, "_outlook", void 0), n([de({
    type: Boolean
  })], Bi.prototype, "isLoading", void 0), n([de({
    type: Boolean
  })], Bi.prototype, "isSaving", void 0), n([pe()], Bi.prototype, "_operationError", void 0), n([pe()], Bi.prototype, "_confirmIrrigate", void 0), n([pe()], Bi.prototype, "_skipDetailsOpen", void 0), customElements.get("smart-irrigation-view-zones") || customElements.define("smart-irrigation-view-zones", Bi);
  class Pi extends ce {
    setConfig(e) {
      this._config = e;
    }
    getCardSize() {
      return 6;
    }
    render() {
      var e;
      if (!this.hass || !this._config) return F``;
      if (!yi(this.hass.language)) return function (e) {
        const t = _i(e);
        return yi(e) ? Promise.resolve() : (vi[t] || (vi[t] = fetch(`/smart_irrigation_static/languages/${t}.json`).then(e => e.ok ? e.json() : Promise.reject(e.status)).then(e => {
          bi[t] = e;
        }).catch(() => {
          bi[t] = bi.en;
        })), vi[t]);
      }(this.hass.language).then(() => this.requestUpdate()), F``;
      const t = null !== (e = this._config.actions) && void 0 !== e ? e : "irrigate";
      return F`
      <smart-irrigation-view-zones
        .hass=${this.hass}
        .hideSettingsLinks=${!0}
        .actionsMode=${t}
      ></smart-irrigation-view-zones>
    `;
    }
  }
  n([de({
    attribute: !1
  })], Pi.prototype, "hass", void 0), n([pe()], Pi.prototype, "_config", void 0), customElements.get("smart-irrigation-zones-card-impl") || customElements.define("smart-irrigation-zones-card-impl", Pi), e.SmartIrrigationZonesCardImpl = Pi, Object.defineProperty(e, "__esModule", {
    value: !0
  });
}({});
