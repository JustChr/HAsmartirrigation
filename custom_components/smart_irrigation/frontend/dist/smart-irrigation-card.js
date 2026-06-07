!function (e) {
  "use strict";

  var t = function (e, a) {
    return t = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (e, t) {
      e.__proto__ = t;
    } || function (e, t) {
      for (var a in t) Object.prototype.hasOwnProperty.call(t, a) && (e[a] = t[a]);
    }, t(e, a);
  };
  function a(e, a) {
    if ("function" != typeof a && null !== a) throw new TypeError("Class extends value " + String(a) + " is not a constructor or null");
    function i() {
      this.constructor = e;
    }
    t(e, a), e.prototype = null === a ? Object.create(a) : (i.prototype = a.prototype, new i());
  }
  var i = function () {
    return i = Object.assign || function (e) {
      for (var t, a = 1, i = arguments.length; a < i; a++) for (var n in t = arguments[a]) Object.prototype.hasOwnProperty.call(t, n) && (e[n] = t[n]);
      return e;
    }, i.apply(this, arguments);
  };
  function n(e, t, a, i) {
    var n,
      r = arguments.length,
      o = r < 3 ? t : null === i ? i = Object.getOwnPropertyDescriptor(t, a) : i;
    if ("object" == typeof Reflect && "function" == typeof Reflect.decorate) o = Reflect.decorate(e, t, a, i);else for (var s = e.length - 1; s >= 0; s--) (n = e[s]) && (o = (r < 3 ? n(o) : r > 3 ? n(t, a, o) : n(t, a)) || o);
    return r > 3 && o && Object.defineProperty(t, a, o), o;
  }
  function r(e, t, a) {
    if (a || 2 === arguments.length) for (var i, n = 0, r = t.length; n < r; n++) !i && n in t || (i || (i = Array.prototype.slice.call(t, 0, n)), i[n] = t[n]);
    return e.concat(i || Array.prototype.slice.call(t));
  }
  "function" == typeof SuppressedError && SuppressedError;
  /**
       * @license
       * Copyright 2019 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  const o = window,
    s = o.ShadowRoot && (void 0 === o.ShadyCSS || o.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype,
    l = Symbol(),
    d = new WeakMap();
  class u {
    constructor(e, t, a) {
      if (this._$cssResult$ = !0, a !== l) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
      this.cssText = e, this.t = t;
    }
    get styleSheet() {
      let e = this.o;
      const t = this.t;
      if (s && void 0 === e) {
        const a = void 0 !== t && 1 === t.length;
        a && (e = d.get(t)), void 0 === e && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), a && d.set(t, e));
      }
      return e;
    }
    toString() {
      return this.cssText;
    }
  }
  const c = (e, ...t) => {
      const a = 1 === e.length ? e[0] : t.reduce((t, a, i) => t + (e => {
        if (!0 === e._$cssResult$) return e.cssText;
        if ("number" == typeof e) return e;
        throw Error("Value passed to 'css' function must be a 'css' function result: " + e + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
      })(a) + e[i + 1], e[0]);
      return new u(a, e, l);
    },
    p = s ? e => e : e => e instanceof CSSStyleSheet ? (e => {
      let t = "";
      for (const a of e.cssRules) t += a.cssText;
      return (e => new u("string" == typeof e ? e : e + "", void 0, l))(t);
    })(e) : e
    /**
         * @license
         * Copyright 2017 Google LLC
         * SPDX-License-Identifier: BSD-3-Clause
         */;
  var m;
  const h = window,
    g = h.trustedTypes,
    v = g ? g.emptyScript : "",
    _ = h.reactiveElementPolyfillSupport,
    f = {
      toAttribute(e, t) {
        switch (t) {
          case Boolean:
            e = e ? v : null;
            break;
          case Object:
          case Array:
            e = null == e ? e : JSON.stringify(e);
        }
        return e;
      },
      fromAttribute(e, t) {
        let a = e;
        switch (t) {
          case Boolean:
            a = null !== e;
            break;
          case Number:
            a = null === e ? null : Number(e);
            break;
          case Object:
          case Array:
            try {
              a = JSON.parse(e);
            } catch (e) {
              a = null;
            }
        }
        return a;
      }
    },
    b = (e, t) => t !== e && (t == t || e == e),
    k = {
      attribute: !0,
      type: String,
      converter: f,
      reflect: !1,
      hasChanged: b
    },
    y = "finalized";
  class z extends HTMLElement {
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
      return this.elementProperties.forEach((t, a) => {
        const i = this._$Ep(a, t);
        void 0 !== i && (this._$Ev.set(i, a), e.push(i));
      }), e;
    }
    static createProperty(e, t = k) {
      if (t.state && (t.attribute = !1), this.finalize(), this.elementProperties.set(e, t), !t.noAccessor && !this.prototype.hasOwnProperty(e)) {
        const a = "symbol" == typeof e ? Symbol() : "__" + e,
          i = this.getPropertyDescriptor(e, a, t);
        void 0 !== i && Object.defineProperty(this.prototype, e, i);
      }
    }
    static getPropertyDescriptor(e, t, a) {
      return {
        get() {
          return this[t];
        },
        set(i) {
          const n = this[e];
          this[t] = i, this.requestUpdate(e, n, a);
        },
        configurable: !0,
        enumerable: !0
      };
    }
    static getPropertyOptions(e) {
      return this.elementProperties.get(e) || k;
    }
    static finalize() {
      if (this.hasOwnProperty(y)) return !1;
      this[y] = !0;
      const e = Object.getPrototypeOf(this);
      if (e.finalize(), void 0 !== e.h && (this.h = [...e.h]), this.elementProperties = new Map(e.elementProperties), this._$Ev = new Map(), this.hasOwnProperty("properties")) {
        const e = this.properties,
          t = [...Object.getOwnPropertyNames(e), ...Object.getOwnPropertySymbols(e)];
        for (const a of t) this.createProperty(a, e[a]);
      }
      return this.elementStyles = this.finalizeStyles(this.styles), !0;
    }
    static finalizeStyles(e) {
      const t = [];
      if (Array.isArray(e)) {
        const a = new Set(e.flat(1 / 0).reverse());
        for (const e of a) t.unshift(p(e));
      } else void 0 !== e && t.push(p(e));
      return t;
    }
    static _$Ep(e, t) {
      const a = t.attribute;
      return !1 === a ? void 0 : "string" == typeof a ? a : "string" == typeof e ? e.toLowerCase() : void 0;
    }
    _$Eu() {
      var e;
      this._$E_ = new Promise(e => this.enableUpdating = e), this._$AL = new Map(), this._$Eg(), this.requestUpdate(), null === (e = this.constructor.h) || void 0 === e || e.forEach(e => e(this));
    }
    addController(e) {
      var t, a;
      (null !== (t = this._$ES) && void 0 !== t ? t : this._$ES = []).push(e), void 0 !== this.renderRoot && this.isConnected && (null === (a = e.hostConnected) || void 0 === a || a.call(e));
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
          const a = document.createElement("style"),
            i = o.litNonce;
          void 0 !== i && a.setAttribute("nonce", i), a.textContent = t.cssText, e.appendChild(a);
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
    attributeChangedCallback(e, t, a) {
      this._$AK(e, a);
    }
    _$EO(e, t, a = k) {
      var i;
      const n = this.constructor._$Ep(e, a);
      if (void 0 !== n && !0 === a.reflect) {
        const r = (void 0 !== (null === (i = a.converter) || void 0 === i ? void 0 : i.toAttribute) ? a.converter : f).toAttribute(t, a.type);
        this._$El = e, null == r ? this.removeAttribute(n) : this.setAttribute(n, r), this._$El = null;
      }
    }
    _$AK(e, t) {
      var a;
      const i = this.constructor,
        n = i._$Ev.get(e);
      if (void 0 !== n && this._$El !== n) {
        const e = i.getPropertyOptions(n),
          r = "function" == typeof e.converter ? {
            fromAttribute: e.converter
          } : void 0 !== (null === (a = e.converter) || void 0 === a ? void 0 : a.fromAttribute) ? e.converter : f;
        this._$El = n, this[n] = r.fromAttribute(t, e.type), this._$El = null;
      }
    }
    requestUpdate(e, t, a) {
      let i = !0;
      void 0 !== e && (((a = a || this.constructor.getPropertyOptions(e)).hasChanged || b)(this[e], t) ? (this._$AL.has(e) || this._$AL.set(e, t), !0 === a.reflect && this._$El !== e && (void 0 === this._$EC && (this._$EC = new Map()), this._$EC.set(e, a))) : i = !1), !this.isUpdatePending && i && (this._$E_ = this._$Ej());
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
      const a = this._$AL;
      try {
        t = this.shouldUpdate(a), t ? (this.willUpdate(a), null === (e = this._$ES) || void 0 === e || e.forEach(e => {
          var t;
          return null === (t = e.hostUpdate) || void 0 === t ? void 0 : t.call(e);
        }), this.update(a)) : this._$Ek();
      } catch (e) {
        throw t = !1, this._$Ek(), e;
      }
      t && this._$AE(a);
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
  var w;
  z[y] = !0, z.elementProperties = new Map(), z.elementStyles = [], z.shadowRootOptions = {
    mode: "open"
  }, null == _ || _({
    ReactiveElement: z
  }), (null !== (m = h.reactiveElementVersions) && void 0 !== m ? m : h.reactiveElementVersions = []).push("1.6.3");
  const S = window,
    A = S.trustedTypes,
    x = A ? A.createPolicy("lit-html", {
      createHTML: e => e
    }) : void 0,
    E = "$lit$",
    M = `lit$${(Math.random() + "").slice(9)}$`,
    T = "?" + M,
    D = `<${T}>`,
    P = document,
    j = () => P.createComment(""),
    N = e => null === e || "object" != typeof e && "function" != typeof e,
    C = Array.isArray,
    H = "[ \t\n\f\r]",
    O = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,
    L = /-->/g,
    I = />/g,
    B = RegExp(`>|${H}(?:([^\\s"'>=/]+)(${H}*=${H}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`, "g"),
    R = /'/g,
    U = /"/g,
    $ = /^(?:script|style|textarea|title)$/i,
    V = (e => (t, ...a) => ({
      _$litType$: e,
      strings: t,
      values: a
    }))(1),
    W = Symbol.for("lit-noChange"),
    F = Symbol.for("lit-nothing"),
    q = new WeakMap(),
    Z = P.createTreeWalker(P, 129, null, !1);
  function G(e, t) {
    if (!Array.isArray(e) || !e.hasOwnProperty("raw")) throw Error("invalid template strings array");
    return void 0 !== x ? x.createHTML(t) : t;
  }
  const Y = (e, t) => {
    const a = e.length - 1,
      i = [];
    let n,
      r = 2 === t ? "<svg>" : "",
      o = O;
    for (let t = 0; t < a; t++) {
      const a = e[t];
      let s,
        l,
        d = -1,
        u = 0;
      for (; u < a.length && (o.lastIndex = u, l = o.exec(a), null !== l);) u = o.lastIndex, o === O ? "!--" === l[1] ? o = L : void 0 !== l[1] ? o = I : void 0 !== l[2] ? ($.test(l[2]) && (n = RegExp("</" + l[2], "g")), o = B) : void 0 !== l[3] && (o = B) : o === B ? ">" === l[0] ? (o = null != n ? n : O, d = -1) : void 0 === l[1] ? d = -2 : (d = o.lastIndex - l[2].length, s = l[1], o = void 0 === l[3] ? B : '"' === l[3] ? U : R) : o === U || o === R ? o = B : o === L || o === I ? o = O : (o = B, n = void 0);
      const c = o === B && e[t + 1].startsWith("/>") ? " " : "";
      r += o === O ? a + D : d >= 0 ? (i.push(s), a.slice(0, d) + E + a.slice(d) + M + c) : a + M + (-2 === d ? (i.push(void 0), t) : c);
    }
    return [G(e, r + (e[a] || "<?>") + (2 === t ? "</svg>" : "")), i];
  };
  class K {
    constructor({
      strings: e,
      _$litType$: t
    }, a) {
      let i;
      this.parts = [];
      let n = 0,
        r = 0;
      const o = e.length - 1,
        s = this.parts,
        [l, d] = Y(e, t);
      if (this.el = K.createElement(l, a), Z.currentNode = this.el.content, 2 === t) {
        const e = this.el.content,
          t = e.firstChild;
        t.remove(), e.append(...t.childNodes);
      }
      for (; null !== (i = Z.nextNode()) && s.length < o;) {
        if (1 === i.nodeType) {
          if (i.hasAttributes()) {
            const e = [];
            for (const t of i.getAttributeNames()) if (t.endsWith(E) || t.startsWith(M)) {
              const a = d[r++];
              if (e.push(t), void 0 !== a) {
                const e = i.getAttribute(a.toLowerCase() + E).split(M),
                  t = /([.?@])?(.*)/.exec(a);
                s.push({
                  type: 1,
                  index: n,
                  name: t[2],
                  strings: e,
                  ctor: "." === t[1] ? te : "?" === t[1] ? ie : "@" === t[1] ? ne : ee
                });
              } else s.push({
                type: 6,
                index: n
              });
            }
            for (const t of e) i.removeAttribute(t);
          }
          if ($.test(i.tagName)) {
            const e = i.textContent.split(M),
              t = e.length - 1;
            if (t > 0) {
              i.textContent = A ? A.emptyScript : "";
              for (let a = 0; a < t; a++) i.append(e[a], j()), Z.nextNode(), s.push({
                type: 2,
                index: ++n
              });
              i.append(e[t], j());
            }
          }
        } else if (8 === i.nodeType) if (i.data === T) s.push({
          type: 2,
          index: n
        });else {
          let e = -1;
          for (; -1 !== (e = i.data.indexOf(M, e + 1));) s.push({
            type: 7,
            index: n
          }), e += M.length - 1;
        }
        n++;
      }
    }
    static createElement(e, t) {
      const a = P.createElement("template");
      return a.innerHTML = e, a;
    }
  }
  function J(e, t, a = e, i) {
    var n, r, o, s;
    if (t === W) return t;
    let l = void 0 !== i ? null === (n = a._$Co) || void 0 === n ? void 0 : n[i] : a._$Cl;
    const d = N(t) ? void 0 : t._$litDirective$;
    return (null == l ? void 0 : l.constructor) !== d && (null === (r = null == l ? void 0 : l._$AO) || void 0 === r || r.call(l, !1), void 0 === d ? l = void 0 : (l = new d(e), l._$AT(e, a, i)), void 0 !== i ? (null !== (o = (s = a)._$Co) && void 0 !== o ? o : s._$Co = [])[i] = l : a._$Cl = l), void 0 !== l && (t = J(e, l._$AS(e, t.values), l, i)), t;
  }
  class X {
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
            content: a
          },
          parts: i
        } = this._$AD,
        n = (null !== (t = null == e ? void 0 : e.creationScope) && void 0 !== t ? t : P).importNode(a, !0);
      Z.currentNode = n;
      let r = Z.nextNode(),
        o = 0,
        s = 0,
        l = i[0];
      for (; void 0 !== l;) {
        if (o === l.index) {
          let t;
          2 === l.type ? t = new Q(r, r.nextSibling, this, e) : 1 === l.type ? t = new l.ctor(r, l.name, l.strings, this, e) : 6 === l.type && (t = new re(r, this, e)), this._$AV.push(t), l = i[++s];
        }
        o !== (null == l ? void 0 : l.index) && (r = Z.nextNode(), o++);
      }
      return Z.currentNode = P, n;
    }
    v(e) {
      let t = 0;
      for (const a of this._$AV) void 0 !== a && (void 0 !== a.strings ? (a._$AI(e, a, t), t += a.strings.length - 2) : a._$AI(e[t])), t++;
    }
  }
  class Q {
    constructor(e, t, a, i) {
      var n;
      this.type = 2, this._$AH = F, this._$AN = void 0, this._$AA = e, this._$AB = t, this._$AM = a, this.options = i, this._$Cp = null === (n = null == i ? void 0 : i.isConnected) || void 0 === n || n;
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
      e = J(this, e, t), N(e) ? e === F || null == e || "" === e ? (this._$AH !== F && this._$AR(), this._$AH = F) : e !== this._$AH && e !== W && this._(e) : void 0 !== e._$litType$ ? this.g(e) : void 0 !== e.nodeType ? this.$(e) : (e => C(e) || "function" == typeof (null == e ? void 0 : e[Symbol.iterator]))(e) ? this.T(e) : this._(e);
    }
    k(e) {
      return this._$AA.parentNode.insertBefore(e, this._$AB);
    }
    $(e) {
      this._$AH !== e && (this._$AR(), this._$AH = this.k(e));
    }
    _(e) {
      this._$AH !== F && N(this._$AH) ? this._$AA.nextSibling.data = e : this.$(P.createTextNode(e)), this._$AH = e;
    }
    g(e) {
      var t;
      const {
          values: a,
          _$litType$: i
        } = e,
        n = "number" == typeof i ? this._$AC(e) : (void 0 === i.el && (i.el = K.createElement(G(i.h, i.h[0]), this.options)), i);
      if ((null === (t = this._$AH) || void 0 === t ? void 0 : t._$AD) === n) this._$AH.v(a);else {
        const e = new X(n, this),
          t = e.u(this.options);
        e.v(a), this.$(t), this._$AH = e;
      }
    }
    _$AC(e) {
      let t = q.get(e.strings);
      return void 0 === t && q.set(e.strings, t = new K(e)), t;
    }
    T(e) {
      C(this._$AH) || (this._$AH = [], this._$AR());
      const t = this._$AH;
      let a,
        i = 0;
      for (const n of e) i === t.length ? t.push(a = new Q(this.k(j()), this.k(j()), this, this.options)) : a = t[i], a._$AI(n), i++;
      i < t.length && (this._$AR(a && a._$AB.nextSibling, i), t.length = i);
    }
    _$AR(e = this._$AA.nextSibling, t) {
      var a;
      for (null === (a = this._$AP) || void 0 === a || a.call(this, !1, !0, t); e && e !== this._$AB;) {
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
    constructor(e, t, a, i, n) {
      this.type = 1, this._$AH = F, this._$AN = void 0, this.element = e, this.name = t, this._$AM = i, this.options = n, a.length > 2 || "" !== a[0] || "" !== a[1] ? (this._$AH = Array(a.length - 1).fill(new String()), this.strings = a) : this._$AH = F;
    }
    get tagName() {
      return this.element.tagName;
    }
    get _$AU() {
      return this._$AM._$AU;
    }
    _$AI(e, t = this, a, i) {
      const n = this.strings;
      let r = !1;
      if (void 0 === n) e = J(this, e, t, 0), r = !N(e) || e !== this._$AH && e !== W, r && (this._$AH = e);else {
        const i = e;
        let o, s;
        for (e = n[0], o = 0; o < n.length - 1; o++) s = J(this, i[a + o], t, o), s === W && (s = this._$AH[o]), r || (r = !N(s) || s !== this._$AH[o]), s === F ? e = F : e !== F && (e += (null != s ? s : "") + n[o + 1]), this._$AH[o] = s;
      }
      r && !i && this.j(e);
    }
    j(e) {
      e === F ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, null != e ? e : "");
    }
  }
  class te extends ee {
    constructor() {
      super(...arguments), this.type = 3;
    }
    j(e) {
      this.element[this.name] = e === F ? void 0 : e;
    }
  }
  const ae = A ? A.emptyScript : "";
  class ie extends ee {
    constructor() {
      super(...arguments), this.type = 4;
    }
    j(e) {
      e && e !== F ? this.element.setAttribute(this.name, ae) : this.element.removeAttribute(this.name);
    }
  }
  class ne extends ee {
    constructor(e, t, a, i, n) {
      super(e, t, a, i, n), this.type = 5;
    }
    _$AI(e, t = this) {
      var a;
      if ((e = null !== (a = J(this, e, t, 0)) && void 0 !== a ? a : F) === W) return;
      const i = this._$AH,
        n = e === F && i !== F || e.capture !== i.capture || e.once !== i.once || e.passive !== i.passive,
        r = e !== F && (i === F || n);
      n && this.element.removeEventListener(this.name, this, i), r && this.element.addEventListener(this.name, this, e), this._$AH = e;
    }
    handleEvent(e) {
      var t, a;
      "function" == typeof this._$AH ? this._$AH.call(null !== (a = null === (t = this.options) || void 0 === t ? void 0 : t.host) && void 0 !== a ? a : this.element, e) : this._$AH.handleEvent(e);
    }
  }
  class re {
    constructor(e, t, a) {
      this.element = e, this.type = 6, this._$AN = void 0, this._$AM = t, this.options = a;
    }
    get _$AU() {
      return this._$AM._$AU;
    }
    _$AI(e) {
      J(this, e);
    }
  }
  const oe = S.litHtmlPolyfillSupport;
  null == oe || oe(K, Q), (null !== (w = S.litHtmlVersions) && void 0 !== w ? w : S.litHtmlVersions = []).push("2.8.0");
  /**
       * @license
       * Copyright 2017 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  var se, le;
  class de extends z {
    constructor() {
      super(...arguments), this.renderOptions = {
        host: this
      }, this._$Do = void 0;
    }
    createRenderRoot() {
      var e, t;
      const a = super.createRenderRoot();
      return null !== (e = (t = this.renderOptions).renderBefore) && void 0 !== e || (t.renderBefore = a.firstChild), a;
    }
    update(e) {
      const t = this.render();
      this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(e), this._$Do = ((e, t, a) => {
        var i, n;
        const r = null !== (i = null == a ? void 0 : a.renderBefore) && void 0 !== i ? i : t;
        let o = r._$litPart$;
        if (void 0 === o) {
          const e = null !== (n = null == a ? void 0 : a.renderBefore) && void 0 !== n ? n : null;
          r._$litPart$ = o = new Q(t.insertBefore(j(), e), e, void 0, null != a ? a : {});
        }
        return o._$AI(e), o;
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
  de.finalized = !0, de._$litElement$ = !0, null === (se = globalThis.litElementHydrateSupport) || void 0 === se || se.call(globalThis, {
    LitElement: de
  });
  const ue = globalThis.litElementPolyfillSupport;
  null == ue || ue({
    LitElement: de
  }), (null !== (le = globalThis.litElementVersions) && void 0 !== le ? le : globalThis.litElementVersions = []).push("3.3.3");
  /**
       * @license
       * Copyright 2017 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  const ce = (e, t) => "method" === t.kind && t.descriptor && !("value" in t.descriptor) ? {
    ...t,
    finisher(a) {
      a.createProperty(t.key, e);
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
    finisher(a) {
      a.createProperty(t.key, e);
    }
  };
  function pe(e) {
    return (t, a) => void 0 !== a ? ((e, t, a) => {
      t.constructor.createProperty(a, e);
    })(e, t, a) : ce(e, t);
    /**
         * @license
         * Copyright 2017 Google LLC
         * SPDX-License-Identifier: BSD-3-Clause
         */
  }
  function me(e) {
    return pe({
      ...e,
      state: !0
    });
  }
  /**
       * @license
       * Copyright 2021 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  var he;
  null === (he = window.HTMLSlotElement) || void 0 === he || he.prototype.assignedElements;
  let ge = !1,
    ve = null;
  const _e = async () => {
    if (ge && ve) return ve;
    if (customElements.get("ha-checkbox") && customElements.get("ha-slider") && customElements.get("ha-panel-config") && customElements.get("ha-entity-picker")) return Promise.resolve();
    ge = !0, ve = async function () {
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
        const a = document.createElement("ha-panel-config");
        e.appendChild(a), await a.routerOptions.routes.automation.load(), customElements.get("ha-entity-picker") || (await Promise.race([customElements.whenDefined("ha-entity-picker"), new Promise(e => setTimeout(e, 3e3))])), e.textContent = "";
      } catch (e) {
        console.error("Failed to load HA form elements:", e);
      }
    }();
    try {
      await ve;
    } finally {
      ge = !1, ve = null;
    }
  };
  const fe = `v${"2026.06.14"}`,
    be = "smart_irrigation",
    ke = "metric",
    ye = "bucket",
    ze = e => e.callWS({
      type: be + "/zones"
    }),
    we = e => e.callWS({
      type: be + "/irrigation_outlook"
    }),
    Se = e => {
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
      return n([pe({
        attribute: !1
      })], t.prototype, "hass", void 0), t;
    };
  var Ae, xe, Ee, Me;
  !function (e) {
    e.Sunrise = "sunrise", e.Sunset = "sunset", e.SolarAzimuth = "solar_azimuth";
  }(Ae || (Ae = {})), function (e) {
    e.Disabled = "disabled", e.Manual = "manual", e.Automatic = "automatic";
  }(xe || (xe = {})), function (e) {
    e.language = "language", e.system = "system", e.comma_decimal = "comma_decimal", e.decimal_comma = "decimal_comma", e.space_comma = "space_comma", e.none = "none";
  }(Ee || (Ee = {})), function (e) {
    e.language = "language", e.system = "system", e.am_pm = "12", e.twenty_four = "24";
  }(Me || (Me = {}));
  /**
       * @license
       * Copyright 2017 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  const Te = 2;
  class De {
    constructor(e) {}
    get _$AU() {
      return this._$AM._$AU;
    }
    _$AT(e, t, a) {
      this._$Ct = e, this._$AM = t, this._$Ci = a;
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
  class Pe extends De {
    constructor(e) {
      if (super(e), this.et = F, e.type !== Te) throw Error(this.constructor.directiveName + "() can only be used in child bindings");
    }
    render(e) {
      if (e === F || null == e) return this.ft = void 0, this.et = e;
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
  Pe.directiveName = "unsafeHTML", Pe.resultType = 1;
  const je = (e => (...t) => ({
    _$litDirective$: e,
    values: t
  }))(Pe);
  var Ne = {
      actions: {
        delete: "Lösche",
        edit: "Bearbeiten",
        save: "Speichern",
        cancel: "Abbrechen",
        confirm_delete: "Löschen bestätigen",
        confirm_delete_zone: "Möchtest du diese Zone wirklich löschen?"
      },
      labels: {
        module: "Modul",
        no: "Nein",
        select: "Wähle",
        yes: "Ja",
        enabled: "Aktiviert",
        disabled: "Deaktiviert",
        before: "vor",
        after: "nach",
        settings: "Einstellungen",
        bulk_actions: "Sammelaktionen"
      },
      attributes: {
        size: "Größe",
        throughput: "Durchfluss",
        state: "Zustand",
        bucket: "Eimer",
        last_updated: "zuletzt aktualisiert",
        last_calculated: "zuletzt berechnet",
        number_of_data_points: "Anzahl Datenpunkte"
      },
      loading: "Laden",
      saving: "Speichern",
      units: {
        seconds: "Sekunden"
      },
      "loading-messages": {
        configuration: "Konfiguration wird geladen...",
        modules: "Module werden geladen...",
        general: "Laden..."
      },
      "saving-messages": {
        adding: "Hinzufügen...",
        saving: "Speichern..."
      },
      errors: {
        load_failed: "Daten konnten nicht geladen werden",
        save_failed: "Änderungen konnten nicht gespeichert werden",
        delete_failed: "Löschen fehlgeschlagen",
        action_failed: "Aktion fehlgeschlagen"
      }
    },
    Ce = {
      "default-zone": "Standard Zone",
      "default-mapping": "Standard Sensorgruppe"
    },
    He = {
      calculation: {
        explanation: {
          "module-returned-evapotranspiration-deficiency": "Beachte: Diese Beschreibung nutzt '.' als Dezimalzeichen und zeigt gerundete Werte. Das Modul berechnete einen Evapotranspirationsmangel von",
          "bucket-was": "Der alte Vorrat war",
          "new-bucket-values-is": "Der neue Vorrat ist",
          "old-bucket-variable": "alter_Vorrat",
          delta: "Veränderung",
          "bucket-less-than-zero-irrigation-necessary": "Wenn der Vorrat < 0 ist, ist eine Bewässerung nötig.",
          "steps-taken-to-calculate-duration": "Für eine exakte Berechnung der Dauer, wurden folgende Schritte durchgeführt",
          "precipitation-rate-defined-as": "Der Niederschlag ist",
          "duration-is-calculated-as": "Die Dauer ist",
          bucket: "Vorrat",
          "precipitation-rate-variable": "Niederschlag",
          "multiplier-is-applied": "Der Multiplikator wird angewendet. Der Multiplikator ist",
          "duration-after-multiplier-is": "also ist die Dauer",
          "maximum-duration-is-applied": "Die maximale Dauer wird angewendet. Diese ist",
          "duration-after-maximum-duration-is": "also ist die Dauer",
          "lead-time-is-applied": "Zuletzt wird die Vorlaufzeit angewendet. Die Vorlaufzeit ist",
          "duration-after-lead-time-is": "also ist die Dauer",
          "bucket-larger-than-or-equal-to-zero-no-irrigation-necessary": "Wenn der Vorrat >= 0 ist, ist keine Bewässerung nötig und die Dauer ist gleich",
          "maximum-bucket-is": "Der maximale Vorrat ist",
          "max-bucket-variable": "max_bucket",
          drainage: "Drainage",
          "drainage-rate": "Drainagerate",
          hours: "Stunden",
          "drainage-rate-is": "Drainagerate bei Sättigung (Eimer am Maximum) beträgt",
          "current-drainage-is": "Aktuelle Drainage berechnet als",
          "no-drainage": "Aktuelle Drainage ist 0, weil"
        }
      }
    },
    Oe = {
      pyeto: {
        description: "Die Berechnung der Verunstungsrate basiert auf der FAO56-Formel aus der PyETO-Bibliothek"
      },
      static: {
        description: "Modul mit einer statisch konfigurierbaren Verdunstungsrate."
      },
      passthrough: {
        description: "Pass Through übernimmt den Evapotranspirationssensor und gibt seinen Wert zurück. Auf diese Weise werden alle Berechnungen der Verdunstung umgangen, außer der Anwendung von Aggregaten wie Summe, Durchschnitt etc)."
      }
    },
    Le = {
      general: {
        cards: {
          "automatic-duration-calculation": {
            header: "Automatische Berechnung der Bewässerungsdauer",
            description: "Die Berechnung berücksichtigt die bis zu diesem Zeitpunkt gesammelten Wetterdaten und aktualisiert den Vorrat für jede automatische Zone. Anschließend wird die Dauer basierend auf dem neuen Vorrat angepasst und die gesammelten Wetterdaten entfernt.",
            labels: {
              "auto-calc-enabled": "Automatische Berechnung der Dauer pro Zone",
              "auto-calc-time": "Berechne um",
              "calc-time": "Berechnen um"
            }
          },
          "automatic-update": {
            errors: {
              "warning-update-time-on-or-after-calc-time": "Hinweis: Die automatische Aktualisierung der Wetterdaten erfolgt bei oder nach der automatischen Berechnung der Bewässerungsdauer"
            },
            header: "Automatische Aktualisierung der Wetterdaten",
            description: "Die Wetterdaten werden automatisch gesammelt und gespeichert. Zur Berechnung der Zonen und Bewässerungsdauer sind Wetterdaten erforderlich.",
            labels: {
              "auto-update-enabled": "Automatisches Update der Wetterdaten",
              "auto-update-delay": "Update Verzögerung",
              "auto-update-interval": "Update der Sensordaten alle",
              "auto-update-schedule": "Aktualisierungsplan",
              "auto-update-time": "Aktualisieren um"
            },
            options: {
              days: "Tage",
              hours: "Stunden",
              minutes: "Minuten"
            }
          },
          "automatic-clear": {
            header: "Automatisches Löschen der Wetterdaten",
            description: "Gesammelte Wetterdaten zu einem bestimmten Zeitpunkt automatisch entfernen. Damit wird sicher gestellt, dass keine Wetterdaten von vergangenen Tagen übrig bleiben. Entferne die Wetterdaten nicht vor der Berechnung und verwende diese Option nur, wenn du erwartest, dass das automatische Update Wetterdaten erfasst hat, nachdem der Tag berechnet wurde. Idealerweise sollte dieser Schnitt so spät wie möglich Tag durchgeführt werden.",
            labels: {
              "automatic-clear-enabled": "Automatisches Löschen der Wetterdaten",
              "automatic-clear-time": "Löschen der Wetterdaten um"
            }
          },
          continuousupdates: {
            header: "Kontinuierliche Sensoraktualisierungen (experimentell)",
            description: "Experimentelle Funktion für granularere Wetterdaten.",
            labels: {
              continuousupdates: "Kontinuierliche Aktualisierungen aktivieren",
              sensor_debounce: "Sensor-Entprellung",
              "sensor-debounce": "Sensor-Entprellzeit (ms)"
            }
          }
        },
        description: "Diese Seite ist für allgemeine Einstellungen.",
        title: "Allgemein",
        sections: {
          weather: "Wetter",
          automation: "Automatisierung",
          location: "Standort",
          watering: "Bewässerungsverhalten"
        }
      },
      help: {
        title: "Hilfe",
        cards: {
          "how-to-get-help": {
            title: "Hilfe bekommen",
            "first-read-the": "Lies zuerst im",
            wiki: "Dokumentation",
            "if-you-still-need-help": "Benötigst du weiterhin Hilfe, wende dich an das",
            "community-forum": "Community Forum",
            "or-open-a": "oder eröffne einen",
            "github-issue": "GitHub-Issue",
            "english-only": "nur Englisch"
          }
        }
      },
      mappings: {
        cards: {
          "add-mapping": {
            actions: {
              add: "Hinzufügen"
            },
            header: "Sensorgruppe hinzufügen"
          },
          mapping: {
            aggregates: {
              average: "Durchschnitt",
              first: "Erster",
              last: "Letzter",
              maximum: "Maximum",
              median: "Median",
              minimum: "Minimum",
              sum: "Summe",
              riemannsum: "Riemann-Summe",
              delta: "Delta"
            },
            errors: {
              "cannot-delete-mapping-because-zones-use-it": "Diese Sensorgruppe kann nicht entfernt werden, da sie von mindestens einer Zone verwendet wird.",
              invalid_source: "Ungültige Quelle",
              source_does_not_exist: "Quelle existiert nicht. Bitte gib eine gültige Quelle ein, z. B. 'sensor.mysensor'."
            },
            items: {
              dewpoint: "Taupunkt",
              evapotranspiration: "Verdunstung",
              humidity: "Feuchtigkeit",
              "maximum temperature": "Maximum-Temperatur",
              "minimum temperature": "Minimum-Temperatur",
              precipitation: "Gesamtniederschlag",
              pressure: "Luftdruck",
              "solar radiation": "Sonnenstrahlung",
              temperature: "Temperatur",
              windspeed: "Windgeschwindigkeit",
              "current precipitation": "Aktueller Niederschlag"
            },
            pressure_types: {
              absolute: "absolut",
              relative: "relativ"
            },
            "pressure-type": "Der Luftdruck ist",
            "sensor-aggregate-of-sensor-values-to-calculate": "des Sensors für die Berechnung.",
            "sensor-aggregate-use-the": "Nutze den/die/das",
            "sensor-entity": "Sensor Entität",
            static_value: "Wert",
            "input-units": "Sensor Werte in",
            source: "Quelle",
            sources: {
              none: "Keine",
              weather_service: "Wetterdienst",
              sensor: "Sensor",
              static: "Fester Wert"
            }
          }
        },
        description: "Füge eine oder mehrere Sensorgruppen hinzu, die Wetterdaten von Weather service, Sensoren oder einer Kombination daraus abrufen. Jede Sensorgruppe kann für eine oder mehrere Zonen verwendet werden",
        labels: {
          "mapping-name": "Name"
        },
        no_items: "Es ist noch keine Sensorgruppe angelegt.",
        title: "Sensorgruppen",
        "weather-records": {
          title: "Wetterdaten",
          timestamp: "Zeit",
          temperature: "Temp.",
          humidity: "Feuchte",
          dewpoint: "Taupunkt",
          wind: "Wind",
          pressure: "Druck",
          precipitation: "Niederschlag",
          "retrieval-time": "Abgerufen",
          "no-data": "Keine Wetterdaten für diese Sensorgruppe verfügbar"
        }
      },
      modules: {
        cards: {
          "add-module": {
            actions: {
              add: "Hinzufügen"
            },
            header: "Modul hinzufügen"
          },
          module: {
            errors: {
              "cannot-delete-module-because-zones-use-it": "Dieses Modul kann nicht entfernt werden, da es von mindestens einer Zone verwendet wird."
            },
            labels: {
              configuration: "Konfiguration",
              required: "Feld ist erforderlich"
            },
            "translated-options": {
              DontEstimate: "Nicht berechnen",
              EstimateFromSunHours: "Basierend auf den Sonnenstunden",
              EstimateFromTemp: "Basierend auf der Temperatur",
              EstimateFromSunHoursAndTemperature: "Basierend auf dem Durchschnitt von Sonnenstunden und Temperatur"
            }
          }
        },
        description: "Füge ein oder mehrere Module hinzu. Module berechnen die Bewässerungsdauer. Jedes Modul hat seine eigene Konfiguration und kann zur Berechnung der Bewässerungsdauer für eine oder mehrere Zonen verwendet werden.",
        no_items: "Es ist noch kein Module angelegt.",
        title: "Module"
      },
      zones: {
        actions: {
          add: "Hinzufügen",
          calculate: "Bewässerungsdauer berechnen.",
          information: "Informationen",
          update: "Wetterdaten aktualisieren.",
          "reset-bucket": "Vorrat zurücksetzen",
          "view-weather-info": "Wetterdaten anzeigen",
          "view-weather-info-message": "Wetterdaten verfügbar für",
          "view-watering-calendar": "Bewässerungskalender",
          irrigate_all: "Alle Zonen jetzt bewässern",
          open_settings: "Einstellungen bearbeiten"
        },
        cards: {
          "add-zone": {
            actions: {
              add: "Hinzufügen"
            },
            header: "Zone hinzufügen"
          },
          "zone-actions": {
            actions: {
              "calculate-all": "Dauern neu berechnen",
              "update-all": "Wetterdaten aktualisieren",
              "reset-all-buckets": "Alle Vorräte zurücksetzen",
              "clear-all-weatherdata": "Alle Wetterdaten löschen"
            },
            header: "Aktionen für alle Zonen"
          }
        },
        description: "Füge eine oder mehrere Zonen hinzu. Die Bewässerungsdauer wird pro Zone, abhängig von Größe, Durchsatz, Status, Modul und Sensorgruppe berechnet.",
        labels: {
          bucket: "Vorrat",
          duration: "Dauer",
          "lead-time": "Vorlaufzeit",
          mapping: "Sensorgruppe",
          "maximum-duration": "Maximale Dauer",
          multiplier: "Multiplikator",
          name: "Name",
          size: "Größe",
          state: "Berechnung",
          states: {
            automatic: "Automatisch",
            disabled: "Aus",
            manual: "Manuell"
          },
          throughput: "Durchfluss",
          "maximum-bucket": "Maximaler Vorrat",
          last_calculated: "Zuletzt berechnet",
          "data-last-updated": "Daten zuletzt aktualisiert",
          "data-number-of-data-points": "Anzahl der Messungen",
          drainage_rate: "Drainagerate",
          linked_entity: "Verknüpfte Schalter/Ventil-Entität",
          linked_entity_placeholder: "z.B. switch.garten_ventil",
          irrigate_now: "Jetzt bewässern",
          bucket_threshold: "Mindestdefizit für Bewässerung",
          flow_sensor: "Durchflussmesser-Sensor (optional)",
          flow_sensor_placeholder: "z. B. sensor.zone_flow_rate"
        },
        no_items: "Es ist noch keine Zone vorhanden.",
        title: "Zonen",
        confirm_irrigate: {
          title: "Bewässerung starten?",
          body: "Dies öffnet jetzt die verknüpften Ventile und umgeht alle Ausschlussbedingungen (Regen, Temperatur, Mindestabstand zwischen Bewässerungen).",
          all_linked_zones: "Alle verknüpften Zonen",
          toast_started: "Bewässerung gestartet",
          toast_failed: "Bewässerung fehlgeschlagen"
        },
        status: {
          decision_disabled: "Ausgeschaltet — diese Zone wird nicht automatisch bewässert.",
          decision_water: "Bewässerung nötig: etwa {duration} beim nächsten geplanten Lauf.",
          decision_water_at: "Bewässert etwa {duration} um {time}.",
          decision_water_skip: "Defizit ~{duration}, aber der nächste Lauf wird wahrscheinlich übersprungen ({reason}).",
          decision_water_no_schedule: "Defizit ~{duration} — kein Zeitplan bewässert diese Zone; manuell starten.",
          decision_no_water: "Derzeit keine Bewässerung nötig — der Boden hat genug Feuchtigkeit.",
          decision_unknown: "Noch nicht berechnet — auf Aktualisieren und dann Berechnen drücken.",
          last_checked: "Zuletzt geprüft",
          never: "nie",
          saved: "Gespeichert",
          estimate_now: "Jetzt",
          estimate_tag: "gesch.",
          estimate_method: {
            hourly: "Live-Schätzung aus stündlichem Wetter seit der letzten Berechnung",
            proxy: "Schätzung aus der heutigen Vorhersage seit der letzten Berechnung"
          }
        },
        help: {
          bucket: "Bodenfeuchte-Bilanz (Vorrat). Ein negativer Wert bedeutet, dass der Boden trocken ist und die Zone Wasser braucht.",
          calculate: "Berechnet aus den neuesten Daten, wie lange bewässert wird. Nach dem Aktualisieren ausführen.",
          update: "Ruft die neuesten Wetter-/Sensordaten für diese Zone ab.",
          irrigate_link_entity: "Verknüpfe in den Zoneneinstellungen einen Schalter/ein Ventil, um manuelle Bewässerung zu ermöglichen.",
          irrigate_all: "Öffnet jetzt die verknüpften Ventile für jede Zone mit Defizit. Überspring-Bedingungen (Regen, Wind, Temperatur) werden ignoriert.",
          update_all: "Sammelt die neuesten Wetter-/Sensordaten für alle Zonen. Ändert die Dauern nicht von selbst.",
          calculate_all: "Berechnet die Bewässerungsdauer jeder automatischen Zone aus den bisher gesammelten Daten neu."
        },
        outlook: {
          next_run: "Nächster Lauf",
          no_schedule: "Kein automatischer Zeitplan — Zonen bewässern nur, wenn du sie auslöst.",
          setup_schedule: "Zeitplan einrichten",
          targets_all: "alle Zonen",
          targets_zones: "{count} Zonen",
          will_skip: "Nächster Lauf wird wahrscheinlich übersprungen",
          will_run: "Bedingungen für den nächsten Lauf sehen gut aus.",
          why_skipped: "Warum?",
          provisional: "Vorhersage — kann sich ändern",
          active_guards: "Aktive Bedingungen",
          last_run: "Letzter Lauf",
          last_run_skipped: "übersprungen",
          last_run_ran: "ausgeführt",
          today: "heute",
          tomorrow: "morgen",
          actions: {
            irrigate: "Bewässern",
            calculate: "Neu berechnen",
            update: "Daten aktualisieren"
          },
          checks: {
            precipitation: "Regenvorhersage",
            days_between: "Tage zwischen Bewässerungen",
            temperature: "Niedrige Temperatur",
            wind: "Starker Wind",
            rain_sensor: "Regensensor"
          },
          check_detail: {
            precipitation: "{observed} mm (≥ {threshold} mm)",
            days_between: "{observed}/{threshold} Tage",
            temperature: "{observed}° (unter {threshold}°)",
            wind: "{observed} (über {threshold})",
            rain_sensor: "{observed}"
          }
        },
        calendar: {
          no_data: "Keine Bewässerungskalender-Daten für diese Zone verfügbar.",
          error_prefix: "Fehler beim Erstellen des Kalenders:",
          month: "Monat",
          et: "ET (mm)",
          precipitation: "Niederschlag (mm)",
          watering: "Bewässerung (L)",
          avg_temp: "Ø Temp (°C)",
          method_prefix: "Methode:"
        },
        confirm_action: {
          reset_bucket_title: "Vorrat dieser Zone zurücksetzen?",
          reset_bucket_body: "Dies setzt den Vorrat auf 0 zurück und verwirft die angesammelte Feuchtigkeitsbilanz dieser Zone.",
          reset_all_buckets_title: "Alle Vorräte zurücksetzen?",
          reset_all_buckets_body: "Dies setzt den Vorrat jeder Zone auf 0 zurück und verwirft die angesammelte Feuchtigkeitsbilanz. Die Bewässerungsberechnung beginnt beim nächsten Update neu.",
          clear_weather_title: "Alle Wetterdaten löschen?",
          clear_weather_body: "Dies löscht alle gesammelten Wetter- und Sensordaten aller Zonen. Die Zonen benötigen neue Daten, bevor sie wieder berechnen können."
        }
      },
      schedules: {
        title: "Zeitpläne",
        description: "Erstellen Sie wiederkehrende Zeitpläne für automatische Berechnung, Aktualisierung oder Bewässerung – ohne Automationen.",
        add: "Zeitplan hinzufügen",
        no_items: "Noch keine Zeitpläne konfiguriert. Klicken Sie auf 'Zeitplan hinzufügen'.",
        zones_all: "Alle Zonen",
        zones_specific: "Bestimmte Zonen",
        hours: "Stunden",
        minutes: "Min",
        types: {
          daily: "Täglich",
          weekly: "Wöchentlich",
          monthly: "Monatlich",
          interval: "Alle N Stunden",
          sunrise: "Sonnenaufgang",
          sunset: "Sonnenuntergang",
          solar_azimuth: "Sonnenazimut"
        },
        actions: {
          calculate: "Berechnen (Bewässerungsdauer aktualisieren)",
          update: "Aktualisieren (Wetterdaten sammeln)",
          irrigate: "Bewässern (Ventile direkt steuern)"
        },
        days: {
          monday: "Mo",
          tuesday: "Di",
          wednesday: "Mi",
          thursday: "Do",
          friday: "Fr",
          saturday: "Sa",
          sunday: "So"
        },
        fields: {
          name: "Name",
          type: "Zeitplantyp",
          enabled: "Aktiviert",
          time: "Uhrzeit (HH:MM)",
          days_of_week: "Wochentage",
          day_of_month: "Tag des Monats",
          interval_hours: "Intervall",
          action: "Aktion",
          zones: "Zonen",
          start_date: "Startdatum (optional)",
          end_date: "Enddatum (optional)",
          offset_minutes: "Versatz von Sonnenaufgang/-untergang",
          account_for_duration: "Früh starten, damit Bewässerung zur Zielzeit endet",
          azimuth_angle: "Sonnenazimutwinkel",
          time_anchor: "Zeitpunkt markiert"
        },
        dialog: {
          add_title: "Zeitplan hinzufügen",
          edit_title: "Zeitplan bearbeiten"
        },
        time_anchor: {
          start: "Beginn der Bewässerung",
          finish: "Ende der Bewässerung"
        }
      },
      info: {
        title: "Info",
        description: "Nächste Bewässerung und Systemstatus anzeigen.",
        "configuration-not-available": "Konfiguration nicht verfügbar.",
        cards: {
          "zone-bucket-values": {
            title: "Zoneneimerstand & Dauer",
            labels: {
              bucket: "Eimer",
              duration: "Dauer"
            },
            "no-zones": "Keine Zonen konfiguriert"
          },
          "next-irrigation": {
            title: "Nächste Bewässerung",
            labels: {
              "next-start": "Nächster Start",
              duration: "Dauer",
              zones: "Zonen"
            },
            "no-data": "Keine Daten verfügbar"
          },
          "irrigation-reason": {
            title: "Bewässerungsgrund",
            labels: {
              reason: "Grund",
              sunrise: "Sonnenaufgang",
              "total-duration": "Gesamtdauer",
              explanation: "Erklärung"
            },
            "no-data": "Keine Daten verfügbar"
          },
          irrigate_now: {
            title: "Jetzt bewässern",
            description: "Bewässerung sofort für alle Zonen mit verknüpfter Entität starten. Übersprungbedingungen werden ignoriert.",
            button_all: "Alle Zonen jetzt starten",
            no_linked_zones: "Keine Zonen haben eine verknüpfte Schalter/Ventil-Entität mit berechneter Dauer."
          }
        }
      },
      setup: {
        title: "Einrichtung"
      }
    },
    Ie = "Smart Irrigation",
    Be = {
      title: "Standortkoordinaten",
      description: "Konfigurieren Sie Standortkoordinaten für den Abruf von Wetterdaten. Sie können manuelle Koordinaten verwenden, die sich von Ihrem Home Assistant Standort unterscheiden.",
      manual_enabled: "Manuelle Koordinaten verwenden",
      use_ha_location: "Home Assistant Standort verwenden",
      latitude: "Breitengrad (Dezimalgrad)",
      longitude: "Längengrad (Dezimalgrad)",
      elevation: "Höhe (Meter über dem Meeresspiegel)",
      current_ha_coords: "Aktuelle Home Assistant Koordinaten"
    },
    Re = {
      title: "Tage zwischen Bewässerungen",
      description: "Konfigurieren Sie die Mindestanzahl an Tagen zwischen Bewässerungsereignissen.",
      label: "Minimale Tage zwischen Bewässerungen",
      help_text: "Auf 0 setzen zum Deaktivieren. Werte von 1–365 Tagen werden unterstützt."
    },
    Ue = {
      title: "Bewässerungsstart-Auslöser",
      description: "Konfiguriere, wann die Bewässerung auf Basis von Sonnenereignissen starten soll. Du kannst mehrere Auslöser für verschiedene Zeitpläne hinzufügen. Bei Sonnenaufgang-Auslösern wird mit einem Versatz von 0 automatisch die Gesamtdauer aller aktivierten Zonen verwendet.",
      add_trigger: "Auslöser hinzufügen",
      edit_trigger: "Auslöser bearbeiten",
      delete_trigger: "Auslöser löschen",
      trigger_types: {
        sunrise: "Sonnenaufgang",
        sunset: "Sonnenuntergang",
        solar_azimuth: "Sonnenazimut"
      },
      fields: {
        name: {
          name: "Auslösername",
          description: "Ein aussagekräftiger Name zur Identifizierung dieses Auslösers"
        },
        type: {
          name: "Auslösertyp",
          description: "Die Art des Sonnenereignisses, das den Auslöser auslöst"
        },
        enabled: {
          name: "Aktiviert",
          description: "Ob dieser Auslöser derzeit aktiv ist"
        },
        offset_minutes: {
          name: "Versatz (Minuten)",
          description: "Minuten vor (-) oder nach (+) dem Sonnenereignis. Verwende bei Sonnenaufgang-Auslösern 0 für eine automatische Zeitsteuerung auf Basis der gesamten Zonendauer."
        },
        azimuth_angle: {
          name: "Azimutwinkel (Grad)",
          description: "Sonnenazimutwinkel in Grad, wobei 0=Nord, 90=Ost, 180=Süd, 270=West"
        },
        account_for_duration: {
          name: "Dauer berücksichtigen",
          description: "Wenn aktiviert, startet die Bewässerung früh genug, um zum angegebenen Zeitpunkt fertig zu sein. Wenn deaktiviert, startet die Bewässerung genau zum angegebenen Zeitpunkt."
        }
      },
      dialog: {
        add_title: "Bewässerungsstart-Auslöser hinzufügen",
        edit_title: "Bewässerungsstart-Auslöser bearbeiten",
        cancel: "Abbrechen",
        save: "Speichern",
        delete: "Löschen"
      },
      no_triggers: "Keine Bewässerungsstart-Auslöser konfiguriert. Das System verwendet das Standardverhalten (Sonnenaufgang mit der Gesamtdauer aller Zonen). Füge Auslöser hinzu, um den Bewässerungsstart anzupassen.",
      offset_auto: "Automatisch (aus der Gesamtdauer aller Zonen berechnet)",
      confirm_delete: "Möchtest du den Auslöser '{name}' wirklich löschen?",
      validation: {
        name_required: "Auslösername ist erforderlich",
        azimuth_invalid: "Der Azimutwinkel muss eine gültige Zahl sein"
      },
      help: {
        sunrise_offset: "Für Sonnenaufgang-Auslöser: Verwende negative Werte, um vor Sonnenaufgang zu starten, positive, um danach zu starten. Setze auf 0, um automatisch früh genug zu starten, damit alle Zonen vor Sonnenaufgang fertig sind.",
        sunset_offset: "Für Sonnenuntergang-Auslöser: Verwende negative Werte, um vor Sonnenuntergang zu starten, positive, um nach Sonnenuntergang zu starten.",
        azimuth_explanation: "Der Sonnenazimut ist die Himmelsrichtung der Sonne. 0°=Nord, 90°=Ost, 180°=Süd, 270°=West. Du kannst einen beliebigen Winkelwert eingeben (z. B. 450° = 90°, -30° = 330°). Nutze dies, um die Bewässerung auszulösen, wenn die Sonne eine bestimmte Position erreicht.",
        multiple_triggers: "Du kannst mehrere Auslöser konfigurieren. Jeder aktivierte Auslöser plant den Bewässerungsstart unabhängig."
      }
    },
    $e = {
      title: "Übersprungbedingungen",
      description: "Bewässerung automatisch überspringen, wenn die Bedingungen ungünstig sind. Niederschlagsprüfung, Temperatur und Wind erfordern einen Wetterdienst.",
      threshold_label: "Niederschlagsschwelle",
      threshold_description: "Mindestmenge an prognostiziertem Gesamtniederschlag (in mm) über das Vorhersagefenster, um die Bewässerung zu überspringen.",
      lookahead_label: "Vorhersage-Fenster (Tage)",
      lookahead_help: "Wie viele kommende Vorhersagetage beim Regen-Check zusammengezählt werden. Die Vorhersage beginnt morgen (heute ausgeschlossen), also 1 = nur der nächste Tag, 2 = die nächsten zwei Tage usw.",
      temp_section_title: "Bei niedriger Temperatur überspringen",
      temp_threshold_label: "Überspringen wenn Temperatur unter",
      wind_section_title: "Bei hoher Windgeschwindigkeit überspringen",
      wind_threshold_label: "Überspringen wenn Windgeschwindigkeit über",
      rain_sensor_section_title: "Regenmelder-Bedingung",
      rain_sensor_label: "Regenmelder-Entität (optional)",
      rain_sensor_placeholder: "z.B. binary_sensor.regen"
    },
    Ve = {
      title: "Zonenreihenfolge",
      description: "Wenn mehrere Zonen bewässert werden müssen, legen Sie fest, ob alle gleichzeitig oder nacheinander laufen. Im sequenziellen Modus wartet das System, bis jede Zone fertig ist, bevor die nächste beginnt.",
      parallel: "Parallel (alle Zonen gleichzeitig)",
      sequential: "Sequenziell (eine Zone nach der anderen)",
      rotating: "Rotierend (Zonen wechseln sich ab)",
      max_consecutive_duration_label: "Max. ununterbrochene Laufzeit pro Zone",
      max_consecutive_duration_unit: "Minuten",
      min_absorption_time_label: "Min. Aufnahmezeit zwischen den Durchgängen",
      min_absorption_time_unit: "Minuten (0 = deaktiviert)"
    },
    We = {
      title: "Wetterdienst",
      description: "Konfiguriere, welcher Wetterdienst für ET-Berechnungen und Überspringbedingungen verwendet wird.",
      enabled_label: "Wetterdienst aktivieren",
      service_label: "Wetterdienst",
      api_key_label: "API-Schlüssel",
      api_key_placeholder: "Leer lassen, um den vorhandenen Schlüssel zu behalten",
      api_key_configured: "API-Schlüssel ist konfiguriert",
      api_key_not_configured: "Kein API-Schlüssel konfiguriert",
      api_key_help: "Ein API-Schlüssel von deinem gewählten Wetterdienstanbieter. Open-Meteo benötigt keinen Schlüssel. OpenWeatherMap und Pirate Weather bieten beide kostenlose Kontingente.",
      no_api_key_needed: "Open-Meteo ist ein kostenloser Dienst und benötigt keinen API-Schlüssel.",
      save_button: "Wettereinstellungen speichern",
      saved: "Wettereinstellungen gespeichert",
      openmeteo: "Open-Meteo (kostenlos, kein Schlüssel nötig)",
      test_button: "Verbindung testen",
      test_button_testing: "Wird getestet…",
      test_success: "✓ Verbindung erfolgreich",
      test_error_invalid_auth: "✗ Ungültiger API-Schlüssel — prüfe, ob er korrekt und aktiv ist",
      test_error_cannot_connect: "✗ Verbindung nicht möglich — prüfe deine Internetverbindung",
      test_error_no_service: "✗ Wähle zuerst einen Wetterdienst",
      test_error_unknown: "✗ Test fehlgeschlagen — unbekannter Fehler",
      owm: "OpenWeatherMap",
      pw: "Pirate Weather"
    },
    Fe = {
      zone_size: "Die gesamte bewässerte Fläche dieser Zone. Wird zusammen mit dem Durchsatz verwendet, um zu berechnen, wie viel Wasser pro Durchgang ausgebracht wird.",
      zone_throughput: "Gesamtwasserdurchfluss deines Bewässerungssystems für diese Zone (Liter/Min im metrischen System, Gal/Min im imperialen System). Prüfe das Datenblatt deiner Sprinkler oder miss, wie lange das Füllen eines bekannten Behälters dauert.",
      zone_drainage_rate: "Wie schnell überschüssiges Wasser aus dem Boden abfließt, wenn der Eimer voll ist. Typisch: Rasen 50 mm/h, sandiger Boden 100+ mm/h, Lehm 10 mm/h.",
      zone_bucket: "Aktuelles Wasserdefizit (negativ) oder -überschuss (positiv) für diese Zone. Die Bewässerung wird ausgelöst, wenn der Eimer unter den Schwellenwert fällt.",
      zone_maximum_bucket: "Maximaler Feuchtigkeitsüberschuss, den die Zone aufnehmen kann. Wasser über diesem Wert wird als Abfluss behandelt. Typischer Wert: 50 mm.",
      zone_bucket_threshold: "Die Bewässerung wird ausgelöst, wenn der Eimer unter diesen Wert fällt. Muss 0 oder negativ sein. 0 bedeutet, immer dann zu bewässern, wenn ein Defizit besteht.",
      zone_multiplier: "Skalierungsfaktor, der auf die berechnete Dauer angewendet wird. Über 1,0 erhöht, unter 1,0 verringert. Nützlich zur Feinabstimmung, ohne physische Messwerte zu ändern.",
      zone_lead_time: "Zusätzliche Sekunden vor dem Start der Bewässerung. Nutze dies für das Aufwärmen der Pumpe oder den Druckaufbau im System.",
      zone_maximum_duration: "Harte Obergrenze für einen einzelnen Bewässerungsdurchgang in Sekunden. Verhindert unkontrolliertes Bewässern. Standard: 3600 s (1 Stunde).",
      zone_linked_entity: "Die HA-Schalter- oder Ventil-Entität, die den Wasserfluss für diese Zone steuert. Diese Entität wird eingeschaltet, wenn die Bewässerung läuft.",
      zone_flow_sensor: "Optionaler Sensor zur Messung der tatsächlichen Durchflussrate. Wird nur zur Anzeige verwendet — beeinflusst die Dauerberechnung nicht.",
      general_autoupdatedelay: "Sekunden, die nach dem HA-Start bis zum ersten Abruf der Wetterdaten gewartet wird. Ermöglicht es anderen Integrationen, sich zuerst zu initialisieren.",
      general_sensor_debounce: "Mindestabstand in Millisekunden zwischen Sensormesswerten, um Rauschen von sich schnell ändernden Sensoren herauszufiltern.",
      general_calctime: "Tageszeit, zu der die Bewässerungsdauern aus den gesammelten Wetterdaten neu berechnet werden. Format: HH:MM (24-Stunden).",
      general_cleardatatime: "Tageszeit, zu der alte Wetterdaten gelöscht werden. Muss später als die Berechnungszeit eingestellt sein.",
      general_days_between: "Mindestanzahl an Tagen zwischen Bewässerungsereignissen für dieselbe Zone. Auf 0 setzen, um zu deaktivieren (bewässern, sobald ein Defizit besteht).",
      general_autoupdateinterval: "Wie oft Wetterdaten gesammelt werden. Wähle einen Wert, der frische Daten gegen API-Ratenbegrenzungen abwägt.",
      general_precipitation_threshold: "Die Bewässerung wird übersprungen, wenn der vorhergesagte Gesamtniederschlag über das Vorhersagefenster diesen Wert überschreitet.",
      general_temp_threshold: "Die Bewässerung wird übersprungen, wenn die aktuelle Temperatur unter diesem Wert liegt (z. B. zur Vermeidung von Frostschäden).",
      general_wind_threshold: "Die Bewässerung wird übersprungen, wenn die Windgeschwindigkeit diesen Wert überschreitet (starker Wind verringert die Effizienz und verursacht Abdrift)."
    },
    qe = {
      title: "Einrichtungsassistent",
      open_button: "Einrichtungsassistent",
      close: "Schließen",
      next: "Weiter",
      back: "Zurück",
      finish: "Fertigstellen",
      skip_step: "Diesen Schritt überspringen",
      step_indicator: "Schritt {current} von {total}",
      setup_complete_banner: "Einrichtung nicht abgeschlossen. Starte den Assistenten, um zu beginnen.",
      open_wizard: "Assistent öffnen",
      steps: {
        welcome: {
          title: "Willkommen bei Smart Irrigation",
          intro: "Dieser Assistent führt dich durch die vier Schritte, die nötig sind, damit deine erste Zone automatisch bewässert.",
          step1_label: "Wetterdienst — woher die Wetterdaten kommen",
          step2_label: "Berechnungsmodul — wie die Bewässerungsdauer berechnet wird",
          step3_label: "Sensorgruppe — welche Datenquellen verwendet werden",
          step4_label: "Zone — deine erste Bewässerungszone",
          tip: "Du kannst jeden Schritt überspringen und ihn später über den Tab „Einrichtung“ konfigurieren."
        },
        weather: {
          title: "Wetterdienst",
          description: "Wähle, wie Wetterdaten bezogen werden. Open-Meteo ist kostenlos und benötigt keinen API-Schlüssel — für die meisten Nutzer die einfachste Wahl."
        },
        module: {
          title: "Berechnungsmodul",
          description: "Ein Modul berechnet anhand der Evapotranspiration (ET), wie lange bewässert wird. Das PyETO-Modul (FAO-56-Methode) wird für die meisten Nutzer empfohlen.",
          pick_label: "Modultyp auswählen",
          no_modules: "Keine Modultypen verfügbar."
        },
        mapping: {
          title: "Sensorgruppe",
          description: "Eine Sensorgruppe verknüpft jede Wettervariable mit einer Datenquelle. Lege die wichtigsten Variablen unten fest — einzelne Sensorzuordnungen kannst du später über den Tab „Einrichtung → Sensorgruppen“ verfeinern.",
          name_label: "Name der Sensorgruppe",
          source_label: "Datenquelle für",
          use_weather_service: "Wetterdienst",
          use_sensor: "Sensor",
          use_static: "Statischer Wert",
          use_none: "Keine / nicht verwendet"
        },
        zone: {
          title: "Erste Zone",
          description: "Eine Zone ist ein Bewässerungsbereich (z. B. Rasen, Beet). Lege die physischen Eigenschaften fest, damit das System die korrekte Bewässerungsdauer berechnen kann.",
          name_label: "Zonenname",
          size_label: "Fläche",
          throughput_label: "Sprinkler-Durchsatz",
          entity_label: "Verknüpfter Schalter oder Ventil",
          entity_placeholder: "z. B. switch.garden_valve",
          module_label: "Berechnungsmodul",
          mapping_label: "Sensorgruppe"
        },
        done: {
          title: "Einrichtung abgeschlossen!",
          description: "Deine erste Zone ist bereit. Smart Irrigation berechnet die Bewässerungsdauern nun automatisch auf Basis der Wetterdaten.",
          next_steps: "Was du als Nächstes tun kannst:",
          tip1: "Gehe zu „Zonen“, um die berechneten Dauern und Eimerwerte anzuzeigen.",
          tip2: "Füge über den Tab „Zonen“ weitere Zonen hinzu.",
          tip3: "Verfeinere alle Einstellungen über den Tab „Einrichtung“.",
          go_zones: "Zu „Zonen“",
          go_setup: "Zur Einrichtung"
        }
      },
      stepper: {
        weather: "Wetter",
        module: "Modul",
        mapping: "Sensorgruppe",
        zone: "Zone"
      },
      confirm_close: {
        body: "Setup-Assistenten schließen? Dein bisheriger Fortschritt ist gespeichert.",
        keep: "Weiter bearbeiten",
        close: "Schließen"
      }
    },
    Ze = {
      common: Ne,
      defaults: Ce,
      module: He,
      calcmodules: Oe,
      panels: Le,
      title: Ie,
      coordinate_config: Be,
      days_between_irrigation: Re,
      irrigation_start_triggers: Ue,
      weather_skip: $e,
      zone_sequencing: Ve,
      weather_service_config: We,
      field_help: Fe,
      wizard: qe
    },
    Ge = Object.freeze({
      __proto__: null,
      common: Ne,
      defaults: Ce,
      module: He,
      calcmodules: Oe,
      panels: Le,
      title: Ie,
      coordinate_config: Be,
      days_between_irrigation: Re,
      irrigation_start_triggers: Ue,
      weather_skip: $e,
      zone_sequencing: Ve,
      weather_service_config: We,
      field_help: Fe,
      wizard: qe,
      default: Ze
    }),
    Ye = {
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
    Ke = {
      "default-zone": "Default zone",
      "default-mapping": "Default sensor group"
    },
    Je = {
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
    Xe = {
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
    Qe = {
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
    et = "Smart Irrigation",
    tt = {
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
    at = {
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
    it = {
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
    nt = {
      title: "Location Coordinates",
      description: "Configure location coordinates for weather data retrieval. You can use manual coordinates different from your Home Assistant location if needed.",
      manual_enabled: "Use manual coordinates",
      use_ha_location: "Use Home Assistant location",
      latitude: "Latitude (decimal degrees)",
      longitude: "Longitude (decimal degrees)",
      elevation: "Elevation (meters above sea level)",
      current_ha_coords: "Current Home Assistant coordinates"
    },
    rt = {
      title: "Days Between Irrigation",
      description: "Configure the minimum number of days that must pass between irrigation events. This helps control watering frequency for water conservation and plant health management.\n\nTypical real-world use cases:\n• Lawn care: 1-2 day intervals prevent overwatering\n• Drought restrictions: 6+ day intervals for weekly watering\n• Deep-rooted plants: 3-7 day intervals for less frequent watering\n• Water conservation: Customizable based on climate and soil conditions",
      label: "Minimum days between irrigation",
      help_text: "Set to 0 to disable this feature. Values from 1-365 days are supported. This setting works alongside existing precipitation forecasting logic."
    },
    ot = {
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
    st = {
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
    lt = {
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
    dt = {
      common: Ye,
      defaults: Ke,
      module: Je,
      calcmodules: Xe,
      panels: Qe,
      title: et,
      weather_service_config: tt,
      irrigation_start_triggers: at,
      weather_skip: it,
      coordinate_config: nt,
      days_between_irrigation: rt,
      zone_sequencing: ot,
      field_help: st,
      wizard: lt
    },
    ut = Object.freeze({
      __proto__: null,
      common: Ye,
      defaults: Ke,
      module: Je,
      calcmodules: Xe,
      panels: Qe,
      title: et,
      weather_service_config: tt,
      irrigation_start_triggers: at,
      weather_skip: it,
      coordinate_config: nt,
      days_between_irrigation: rt,
      zone_sequencing: ot,
      field_help: st,
      wizard: lt,
      default: dt
    }),
    ct = {
      actions: {
        delete: "Eliminar",
        edit: "Editar",
        save: "Guardar",
        cancel: "Cancelar",
        confirm_delete: "Confirmar eliminación",
        confirm_delete_zone: "¿Seguro que quieres eliminar esta zona?"
      },
      labels: {
        module: "Módulo",
        no: "No",
        select: "Seleccionar",
        yes: "Sí",
        enabled: "Activado",
        disabled: "Desactivado",
        before: "antes",
        after: "después",
        settings: "Ajustes",
        bulk_actions: "Acciones masivas"
      },
      attributes: {
        size: "Tamaño",
        throughput: "Rendimiento",
        state: "Estado",
        bucket: "depósito",
        last_updated: "última actualización",
        last_calculated: "último cálculo",
        number_of_data_points: "número de puntos de datos"
      },
      loading: "Cargando",
      saving: "Guardando",
      units: {
        seconds: "segundos"
      },
      "loading-messages": {
        configuration: "Cargando configuración...",
        modules: "Cargando módulos...",
        general: "Cargando..."
      },
      "saving-messages": {
        adding: "Añadiendo...",
        saving: "Guardando..."
      },
      errors: {
        load_failed: "No se pudieron cargar los datos",
        save_failed: "No se pudieron guardar los cambios",
        delete_failed: "No se pudo eliminar",
        action_failed: "La acción falló"
      }
    },
    pt = {
      "default-zone": "Zona de riego predeterminada",
      "default-mapping": "Grupo de sensores predeterminado"
    },
    mt = {
      calculation: {
        explanation: {
          "module-returned-evapotranspiration-deficiency": "Nota: esta explicación utiliza '.' como separador decimal y muestra valores redondeados. El módulo devuelve una deficiencia de evapotranspiración de",
          "bucket-was": "El cubo era",
          "new-bucket-values-is": "El nuevo valor del cubo es",
          "old-bucket-variable": "old_bucket",
          delta: "delta",
          "bucket-less-than-zero-irrigation-necessary": "Dado que cubo < 0, el riego es necesario",
          "steps-taken-to-calculate-duration": "Para calcular la duración exacta, se siguieron los siguientes pasos",
          "precipitation-rate-defined-as": "La tasa de precipitación se define como",
          "duration-is-calculated-as": "La duración se calcula como",
          bucket: "cubo",
          "precipitation-rate-variable": "precipitation_rate",
          "multiplier-is-applied": "A continuación, se aplica el multiplicador. El multiplicador es",
          "duration-after-multiplier-is": "por lo que la duración es",
          "maximum-duration-is-applied": "A continuación, se aplica la duración máxima. La duración máxima es",
          "duration-after-maximum-duration-is": "por lo que la duración es",
          "lead-time-is-applied": "Por último, se aplica el plazo de entrega. El plazo de entrega es",
          "duration-after-lead-time-is": "por lo que la duración final es",
          "bucket-larger-than-or-equal-to-zero-no-irrigation-necessary": "Como cubo >= 0, no es necesario regar y la duración se fija en",
          "maximum-bucket-is": "El tamaño máximo de cubo es",
          "max-bucket-variable": "max_bucket",
          drainage: "drenaje",
          "drainage-rate": "tasa de drenaje",
          hours: "horas",
          "drainage-rate-is": "La tasa de drenaje cuando está saturado (depósito al máximo) es",
          "current-drainage-is": "El drenaje actual se calcula como",
          "no-drainage": "El drenaje actual es 0 porque"
        }
      }
    },
    ht = {
      pyeto: {
        description: "Calcular la duración a partir del cálculo FAO56 de la biblioteca PyETO"
      },
      static: {
        description: "Módulo 'de prueba' con un delta estático configurable"
      },
      passthrough: {
        description: "Módulo de paso que devuelve el valor de un sensor de evapotranspiración como delta"
      }
    },
    gt = {
      general: {
        cards: {
          "automatic-duration-calculation": {
            header: "Cálculo automático de la duración",
            labels: {
              "auto-calc-enabled": "Cálculo automático de la duración de las zonas",
              "auto-calc-time": "Calcular en",
              "calc-time": "Calcular a las"
            },
            description: "El cálculo toma los datos meteorológicos recopilados hasta ese momento y actualiza el depósito de cada zona automática. Después, la duración se ajusta según el nuevo valor del depósito y se eliminan los datos meteorológicos recopilados."
          },
          "automatic-update": {
            errors: {
              "warning-update-time-on-or-after-calc-time": "Advertencia: la hora de actualización de los datos meteorológicos es igual o posterior a la hora de cálculo"
            },
            header: "Actualización automática de los datos meteorológicos",
            labels: {
              "auto-update-enabled": "Actualizar automáticamente los datos meteorológicos",
              "auto-update-first-update": "(Primer) Actualización a las",
              "auto-update-interval": "Actualizar datos del sensor cada",
              "auto-update-schedule": "Programa de actualización",
              "auto-update-time": "Actualizar a las",
              "auto-update-delay": "Retraso de actualización"
            },
            options: {
              days: "días",
              hours: "horas",
              minutes: "minutos"
            },
            description: "Recopila y almacena datos meteorológicos automáticamente. Los datos meteorológicos son necesarios para calcular los depósitos y las duraciones de las zonas."
          },
          "automatic-clear": {
            header: "Limpieza automática de datos meteorológicos",
            description: "Elimina automáticamente los datos meteorológicos recopilados a una hora configurada. Úsalo para asegurarte de que no queden datos meteorológicos de días anteriores. No elimines los datos meteorológicos antes de calcular y usa esta opción solo si esperas que la actualización automática recopile datos meteorológicos después de calcular para el día. Lo ideal es limpiar lo más tarde posible del día.",
            labels: {
              "automatic-clear-enabled": "Borrar automáticamente los datos meteorológicos recopilados",
              "automatic-clear-time": "Borrar datos meteorológicos a las"
            }
          },
          continuousupdates: {
            header: "Actualizaciones continuas de sensores (experimental)",
            description: "Función experimental para datos meteorológicos más detallados.",
            labels: {
              continuousupdates: "Activar actualizaciones continuas",
              sensor_debounce: "Antirrebote del sensor",
              "sensor-debounce": "Tiempo de antirrebote del sensor (ms)"
            }
          }
        },
        description: "Esta página provee configuraciones globales.",
        title: "General",
        sections: {
          weather: "Meteorología",
          automation: "Automatización",
          location: "Ubicación",
          watering: "Comportamiento de riego"
        }
      },
      help: {
        title: "Ayuda",
        cards: {
          "how-to-get-help": {
            title: "Cómo obtener ayuda",
            "first-read-the": "Primero lee la",
            wiki: "Documentación",
            "if-you-still-need-help": "Si aún necesitas ayuda, puedes:",
            "community-forum": "Comunidad/Foro",
            "or-open-a": "o abrir un",
            "github-issue": "Incidencia en GitHub",
            "english-only": "sólo en inglés"
          }
        }
      },
      mappings: {
        cards: {
          "add-mapping": {
            actions: {
              add: "Añadir grupo de sensores"
            },
            header: "Añadir grupos de sensores"
          },
          mapping: {
            aggregates: {
              average: "Promedio",
              first: "Primero",
              last: "Último",
              maximum: "Máximo",
              median: "Mediana",
              minimum: "Mínimo",
              sum: "Suma",
              riemannsum: "Suma de Riemann",
              delta: "Delta"
            },
            errors: {
              "cannot-delete-mapping-because-zones-use-it": "No puedes eliminar este grupo de sensores porque hay al menos una zona que lo está usando.",
              invalid_source: "Origen no válido",
              source_does_not_exist: "El origen no existe. Introduce un origen válido, como 'sensor.mysensor'."
            },
            items: {
              dewpoint: "Punto de rocío",
              evapotranspiration: "Evapotranspiración",
              humidity: "Humedad",
              "maximum temperature": "Temperatura máxima",
              "minimum temperature": "Temperatura mínima",
              precipitation: "Precipitación total",
              pressure: "Presión",
              "solar radiation": "Radiación solar",
              temperature: "Temperatura",
              windspeed: "Velocidad del viento",
              "current precipitation": "Precipitación actual"
            },
            "sensor-aggregate-of-sensor-values-to-calculate": "de los valores de los sensores para calcular la duración",
            "sensor-aggregate-use-the": "Usar la",
            "sensor-entity": "Entidad de sensor",
            static_value: "Valor estático",
            "input-units": "Unidades de entrada",
            source: "Fuente",
            sources: {
              none: "Ninguno",
              weather_service: "Servicio meteorológico",
              sensor: "Sensor",
              static: "Valor estático"
            },
            pressure_types: {
              absolute: "absoluta",
              relative: "relativa"
            },
            "pressure-type": "La presión es"
          }
        },
        description: "Añada uno o más grupos de sensores que recuperen datos meteorológicos de Weather service, de sensores o de una combinación de éstos. Puede asignar cada grupo de sensores a una o más zonas",
        labels: {
          "mapping-name": "Nombre del grupo de sensores"
        },
        no_items: "Aún no hay grupos de sensores definidos.",
        title: "Grupos de sensores",
        "weather-records": {
          title: "Registros meteorológicos",
          timestamp: "Hora",
          temperature: "Temp.",
          humidity: "Humidity",
          precipitation: "Precip.",
          "retrieval-time": "Obtenido",
          "no-data": "No hay datos meteorológicos disponibles para este grupo de sensores",
          dewpoint: "Rocío",
          wind: "Viento",
          pressure: "Presión"
        }
      },
      modules: {
        cards: {
          "add-module": {
            actions: {
              add: "Añadir módulo"
            },
            header: "Añadir módulo"
          },
          module: {
            errors: {
              "cannot-delete-module-because-zones-use-it": "No puedes eliminar este módulo porque hay al menos una zona que lo está usando."
            },
            labels: {
              configuration: "Configuración",
              required: "Requerido"
            },
            "translated-options": {
              DontEstimate: "No estimar",
              EstimateFromSunHours: "Estimar desde horas de sol",
              EstimateFromTemp: "Estimar desde temperatura",
              EstimateFromSunHoursAndTemperature: "Estimar a partir del promedio de horas de sol y temperatura"
            }
          }
        },
        description: "Añada uno o varios módulos que calculen la duración del riego. Cada módulo tiene su propia configuración y puede utilizarse para calcular la duración de una o varias zonas.",
        no_items: "Aún no hay módulos definidos.",
        title: "Módulos"
      },
      zones: {
        actions: {
          add: "Añadir",
          calculate: "Calcular",
          information: "Información",
          update: "Actualizar",
          "reset-bucket": "Resetear cubo",
          "view-weather-info": "Ver datos meteorológicos",
          "view-weather-info-message": "Datos meteorológicos disponibles para",
          "view-watering-calendar": "Calendario de riego",
          irrigate_all: "Regar todas las zonas ahora",
          open_settings: "Editar ajustes"
        },
        cards: {
          "add-zone": {
            actions: {
              add: "Añadir zona"
            },
            header: "Añadir zona"
          },
          "zone-actions": {
            actions: {
              "calculate-all": "Recalcular duraciones",
              "update-all": "Actualizar datos meteorológicos",
              "reset-all-buckets": "Resetear todos los cubos",
              "clear-all-weatherdata": "Borrar todos los datos meteorológicos"
            },
            header: "Acciones en todas las zonas"
          }
        },
        description: "Especifique aquí una o varias zonas de riego. La duración del riego se calcula por zona, en función del tamaño, el rendimiento, el estado, el módulo y el grupo de sensores.",
        labels: {
          bucket: "Cubo",
          duration: "Duración",
          "lead-time": "Tiempo de espera",
          mapping: "Grupo de sensores",
          "maximum-duration": "Duración máxima",
          multiplier: "Multiplicador",
          name: "Nombre",
          size: "Tamaño",
          state: "Estado",
          states: {
            automatic: "Automático",
            disabled: "Desactivado",
            manual: "Manual"
          },
          throughput: "Rendimiento",
          "maximum-bucket": "Cubo máximo",
          last_calculated: "Último cálculo",
          "data-last-updated": "Datos actualizados por última vez",
          "data-number-of-data-points": "Número de puntos de datos",
          drainage_rate: "Tasa de drenaje",
          linked_entity: "Entidad de interruptor/válvula vinculada",
          linked_entity_placeholder: "p.ej. switch.valvula_jardin",
          irrigate_now: "Regar ahora",
          bucket_threshold: "Déficit mínimo para regar",
          flow_sensor: "Sensor de caudalímetro (opcional)",
          flow_sensor_placeholder: "p. ej. sensor.zone_flow_rate"
        },
        no_items: "Aún no hay zonas definidas.",
        title: "Zonas",
        confirm_irrigate: {
          title: "¿Iniciar el riego?",
          body: "Esto abrirá ahora las válvulas vinculadas e ignora todas las condiciones de exclusión (lluvia, temperatura, días mínimos entre riegos).",
          all_linked_zones: "Todas las zonas vinculadas",
          toast_started: "Riego iniciado",
          toast_failed: "Error en el riego"
        },
        status: {
          decision_disabled: "Desactivada — esta zona no se regará automáticamente.",
          decision_water: "Riego necesario: unos {duration} en el próximo riego programado.",
          decision_water_at: "Regará unos {duration} a las {time}.",
          decision_water_skip: "Déficit ~{duration}, pero el próximo riego probablemente se omitirá ({reason}).",
          decision_water_no_schedule: "Déficit ~{duration} — ningún horario riega esta zona; actívala manualmente.",
          decision_no_water: "No se necesita riego ahora mismo — el suelo tiene suficiente humedad.",
          decision_unknown: "Aún sin calcular — pulsa Actualizar y luego Calcular para comprobar.",
          last_checked: "Última comprobación",
          never: "nunca",
          saved: "Guardado",
          estimate_now: "Ahora",
          estimate_tag: "est.",
          estimate_method: {
            hourly: "Estimación en vivo del tiempo horario desde el último cálculo",
            proxy: "Estimación distribuida de la previsión de hoy desde el último cálculo"
          }
        },
        help: {
          bucket: "Balance de humedad del suelo (cubo). Un valor negativo significa que el suelo está seco y la zona necesita agua.",
          calculate: "Calcula cuánto tiempo regar a partir de los últimos datos. Ejecútalo después de Actualizar.",
          update: "Obtiene los últimos datos meteorológicos/de sensores de esta zona.",
          irrigate_link_entity: "Vincula un interruptor/válvula en los ajustes de esta zona para permitir el riego manual.",
          irrigate_all: "Abre ahora las válvulas vinculadas de cada zona con déficit. Se ignoran las condiciones de exclusión (lluvia, viento, temperatura).",
          update_all: "Recoge los últimos datos meteorológicos/de sensores de todas las zonas. No cambia las duraciones por sí solo.",
          calculate_all: "Recalcula la duración de riego de cada zona automática a partir de los datos recogidos hasta ahora."
        },
        outlook: {
          next_run: "Próximo riego",
          no_schedule: "Sin horario automático — las zonas solo se riegan cuando lo activas tú.",
          setup_schedule: "Configurar un horario",
          targets_all: "todas las zonas",
          targets_zones: "{count} zonas",
          will_skip: "El próximo riego probablemente se omitirá",
          will_run: "Las condiciones parecen despejadas para el próximo riego.",
          why_skipped: "¿Por qué?",
          provisional: "previsión — puede cambiar",
          active_guards: "Condiciones activas",
          last_run: "Último riego",
          last_run_skipped: "omitido",
          last_run_ran: "ejecutado",
          today: "hoy",
          tomorrow: "mañana",
          actions: {
            irrigate: "Regar",
            calculate: "Recalcular",
            update: "Actualizar datos"
          },
          checks: {
            precipitation: "Lluvia prevista",
            days_between: "Días entre riegos",
            temperature: "Temperatura baja",
            wind: "Viento fuerte",
            rain_sensor: "Sensor de lluvia"
          },
          check_detail: {
            precipitation: "{observed} mm (≥ {threshold} mm)",
            days_between: "{observed}/{threshold} días",
            temperature: "{observed}° (por debajo de {threshold}°)",
            wind: "{observed} (por encima de {threshold})",
            rain_sensor: "{observed}"
          }
        },
        calendar: {
          no_data: "No hay datos de calendario de riego disponibles para esta zona.",
          error_prefix: "Error al generar el calendario:",
          month: "Mes",
          et: "ET (mm)",
          precipitation: "Precipitación (mm)",
          watering: "Riego (L)",
          avg_temp: "Temp. media (°C)",
          method_prefix: "Método:"
        },
        confirm_action: {
          reset_bucket_title: "¿Restablecer el cubo de esta zona?",
          reset_bucket_body: "Esto restablece el cubo a 0, descartando el balance de humedad acumulado de esta zona.",
          reset_all_buckets_title: "¿Restablecer todos los cubos?",
          reset_all_buckets_body: "Esto restablece a 0 el cubo de cada zona, descartando el balance de humedad acumulado. Los cálculos de riego empezarán de nuevo en la próxima actualización.",
          clear_weather_title: "¿Borrar todos los datos meteorológicos?",
          clear_weather_body: "Esto elimina todos los registros meteorológicos y de sensores de todas las zonas. Las zonas necesitarán datos nuevos antes de poder calcular de nuevo."
        }
      },
      schedules: {
        title: "Programas",
        description: "Cree programas recurrentes para calcular, actualizar o regar automáticamente — sin automatizaciones.",
        add: "Añadir programa",
        no_items: "Aún no hay programas configurados. Haga clic en 'Añadir programa'.",
        zones_all: "Todas las zonas",
        zones_specific: "Zonas específicas",
        hours: "horas",
        minutes: "min",
        types: {
          daily: "Diario",
          weekly: "Semanal",
          monthly: "Mensual",
          interval: "Cada N horas",
          sunrise: "Amanecer",
          sunset: "Atardecer",
          solar_azimuth: "Azimut solar"
        },
        actions: {
          calculate: "Calcular (actualizar duración de riego)",
          update: "Actualizar (recopilar datos meteorológicos)",
          irrigate: "Regar (controlar válvulas directamente)"
        },
        days: {
          monday: "Lu",
          tuesday: "Ma",
          wednesday: "Mi",
          thursday: "Ju",
          friday: "Vi",
          saturday: "Sá",
          sunday: "Do"
        },
        fields: {
          name: "Nombre",
          type: "Tipo de programa",
          enabled: "Activado",
          time: "Hora (HH:MM)",
          days_of_week: "Días de la semana",
          day_of_month: "Día del mes",
          interval_hours: "Intervalo",
          action: "Acción",
          zones: "Zonas",
          start_date: "Fecha de inicio (opcional)",
          end_date: "Fecha de fin (opcional)",
          offset_minutes: "Desplazamiento desde amanecer/atardecer",
          account_for_duration: "Iniciar antes para que el riego termine a la hora objetivo",
          azimuth_angle: "Ángulo de azimut solar",
          time_anchor: "La hora marca el"
        },
        dialog: {
          add_title: "Añadir programa",
          edit_title: "Editar programa"
        },
        time_anchor: {
          start: "Inicio del riego",
          finish: "Fin del riego"
        }
      },
      info: {
        title: "Información",
        description: "Ver información sobre el próximo riego y el estado del sistema.",
        "configuration-not-available": "Configuración no disponible.",
        cards: {
          "zone-bucket-values": {
            title: "Valores de depósito y duración",
            labels: {
              bucket: "Depósito",
              duration: "Duración"
            },
            "no-zones": "No hay zonas configuradas"
          },
          "next-irrigation": {
            title: "Próximo riego",
            labels: {
              "next-start": "Próximo inicio",
              duration: "Duración",
              zones: "Zonas"
            },
            "no-data": "No hay datos disponibles"
          },
          "irrigation-reason": {
            title: "Motivo del riego",
            labels: {
              reason: "Razón",
              sunrise: "Amanecer",
              "total-duration": "Duración total",
              explanation: "Explicación"
            },
            "no-data": "No hay datos disponibles"
          },
          irrigate_now: {
            title: "Regar ahora",
            description: "Iniciar riego inmediatamente para todas las zonas con entidad vinculada. Las condiciones de omisión se ignoran.",
            button_all: "Iniciar todas las zonas ahora",
            no_linked_zones: "Ninguna zona tiene una entidad de interruptor/válvula vinculada con duración calculada."
          }
        }
      },
      setup: {
        title: "Configuración"
      }
    },
    vt = "Smart Irrigation",
    _t = {
      title: "Coordenadas de Ubicación",
      description: "Configure las coordenadas de ubicación para obtener datos meteorológicos. Puede usar coordenadas manuales diferentes a la ubicación de Home Assistant si es necesario.",
      manual_enabled: "Usar coordenadas manuales",
      use_ha_location: "Usar ubicación de Home Assistant",
      latitude: "Latitud (grados decimales)",
      longitude: "Longitud (grados decimales)",
      elevation: "Elevación (metros sobre el nivel del mar)",
      current_ha_coords: "Coordenadas actuales de Home Assistant"
    },
    ft = {
      title: "Días entre riegos",
      description: "Configure el número mínimo de días entre eventos de riego.",
      label: "Días mínimos entre riegos",
      help_text: "Establezca 0 para desactivar. Se admiten valores de 1 a 365 días."
    },
    bt = {
      title: "Disparadores de inicio de riego",
      description: "Configura cuándo debe iniciarse el riego según eventos solares. Puedes añadir varios disparadores para diferentes horarios. Para los disparadores de amanecer, dejar el desfase en 0 usará automáticamente la duración total de todas las zonas activadas.",
      add_trigger: "Añadir disparador",
      edit_trigger: "Editar disparador",
      delete_trigger: "Eliminar disparador",
      trigger_types: {
        sunrise: "Amanecer",
        sunset: "Atardecer",
        solar_azimuth: "Acimut solar"
      },
      fields: {
        name: {
          name: "Nombre del disparador",
          description: "Un nombre descriptivo para identificar este disparador"
        },
        type: {
          name: "Tipo de disparador",
          description: "El tipo de evento solar con el que activar"
        },
        enabled: {
          name: "Activado",
          description: "Si este disparador está actualmente activo"
        },
        offset_minutes: {
          name: "Desfase (minutos)",
          description: "Minutos antes (-) o después (+) del evento solar. Para los disparadores de amanecer, usa 0 para una temporización automática basada en la duración total de las zonas."
        },
        azimuth_angle: {
          name: "Ángulo de acimut (grados)",
          description: "Ángulo de acimut solar en grados donde 0=Norte, 90=Este, 180=Sur, 270=Oeste"
        },
        account_for_duration: {
          name: "Tener en cuenta la duración",
          description: "Si está activado, el riego comenzará con suficiente antelación para terminar a la hora indicada. Si está desactivado, el riego comenzará exactamente a la hora indicada."
        }
      },
      dialog: {
        add_title: "Añadir disparador de inicio de riego",
        edit_title: "Editar disparador de inicio de riego",
        cancel: "Cancelar",
        save: "Guardar",
        delete: "Eliminar"
      },
      no_triggers: "No hay disparadores de inicio de riego configurados. El sistema usará el comportamiento predeterminado (amanecer con la duración total de las zonas). Añade disparadores para personalizar cuándo comienza el riego.",
      offset_auto: "Automático (calculado a partir de la duración total de las zonas)",
      confirm_delete: "¿Seguro que quieres eliminar el disparador '{name}'?",
      validation: {
        name_required: "El nombre del disparador es obligatorio",
        azimuth_invalid: "El ángulo de acimut debe ser un número válido"
      },
      help: {
        sunrise_offset: "Para los disparadores de amanecer: usa valores negativos para empezar antes del amanecer, positivos para empezar después. Pon 0 para empezar automáticamente con tiempo suficiente para completar todas las zonas antes del amanecer.",
        sunset_offset: "Para los disparadores de atardecer: usa valores negativos para empezar antes del atardecer, positivos para empezar después del atardecer.",
        azimuth_explanation: "El acimut solar es la dirección de la brújula del sol. 0°=Norte, 90°=Este, 180°=Sur, 270°=Oeste. Puedes introducir cualquier valor de ángulo (p. ej., 450° = 90°, -30° = 330°). Úsalo para activar el riego cuando el sol alcance una posición concreta.",
        multiple_triggers: "Puedes configurar varios disparadores. Cada disparador activado programará los inicios de riego de forma independiente."
      }
    },
    kt = {
      title: "Condiciones de omisión",
      description: "Omitir automáticamente el riego cuando las condiciones sean desfavorables. Las comprobaciones de precipitación, temperatura y viento requieren un servicio meteorológico.",
      threshold_label: "Umbral de precipitación",
      threshold_description: "Precipitación total mínima prevista (en mm) en la ventana de previsión para omitir el riego.",
      lookahead_label: "Ventana de previsión (días)",
      lookahead_help: "Cuántos días de previsión próximos se suman al comprobar la lluvia. La previsión empieza mañana (hoy se excluye), así que 1 = solo el día siguiente, 2 = los próximos dos días, etc.",
      temp_section_title: "Omitir por temperatura baja",
      temp_threshold_label: "Omitir si temperatura por debajo de",
      wind_section_title: "Omitir por viento fuerte",
      wind_threshold_label: "Omitir si velocidad del viento superior a",
      rain_sensor_section_title: "Condición del sensor de lluvia",
      rain_sensor_label: "Entidad del sensor de lluvia (opcional)",
      rain_sensor_placeholder: "p.ej. binary_sensor.lluvia"
    },
    yt = {
      title: "Secuencia de zonas",
      description: "Cuando varias zonas necesitan riego, elija si se ejecutan al mismo tiempo o una tras otra. En modo secuencial, el sistema espera a que cada zona termine antes de iniciar la siguiente.",
      parallel: "Paralelo (todas las zonas a la vez)",
      sequential: "Secuencial (una zona a la vez)",
      rotating: "Rotativo (las zonas se turnan)",
      max_consecutive_duration_label: "Tiempo máx. de ejecución consecutiva por zona",
      max_consecutive_duration_unit: "minutos",
      min_absorption_time_label: "Tiempo mín. de absorción entre turnos",
      min_absorption_time_unit: "minutos (0 = desactivado)"
    },
    zt = {
      title: "Servicio meteorológico",
      description: "Configura qué servicio meteorológico usar para los cálculos de ET y las condiciones de omisión.",
      enabled_label: "Activar servicio meteorológico",
      service_label: "Servicio meteorológico",
      api_key_label: "Clave API",
      api_key_placeholder: "Déjalo en blanco para conservar la clave existente",
      api_key_configured: "La clave API está configurada",
      api_key_not_configured: "No hay clave API configurada",
      api_key_help: "Una clave API de tu proveedor de servicio meteorológico elegido. Open-Meteo no requiere clave. OpenWeatherMap y Pirate Weather ofrecen niveles gratuitos.",
      no_api_key_needed: "Open-Meteo es un servicio gratuito y no requiere clave API.",
      save_button: "Guardar ajustes meteorológicos",
      saved: "Ajustes meteorológicos guardados",
      openmeteo: "Open-Meteo (gratis, sin clave)",
      test_button: "Probar conexión",
      test_button_testing: "Probando…",
      test_success: "✓ Conexión correcta",
      test_error_invalid_auth: "✗ Clave API no válida — comprueba que sea correcta y esté activa",
      test_error_cannot_connect: "✗ No se puede conectar — comprueba tu conexión a internet",
      test_error_no_service: "✗ Selecciona primero un servicio meteorológico",
      test_error_unknown: "✗ Prueba fallida — error desconocido",
      owm: "OpenWeatherMap",
      pw: "Pirate Weather"
    },
    wt = {
      zone_size: "La superficie total regada de esta zona. Se usa junto con el caudal para calcular cuánta agua se aplica por ciclo.",
      zone_throughput: "Flujo total de agua de tu sistema de riego para esta zona (litros/min en métrico, gal/min en imperial). Consulta la ficha técnica de tus aspersores o mídelo cronometrando cuánto tarda en llenarse un recipiente conocido.",
      zone_drainage_rate: "La rapidez con que el agua sobrante drena del suelo cuando el depósito está lleno. Típico: césped 50 mm/h, suelo arenoso 100+ mm/h, arcilla 10 mm/h.",
      zone_bucket: "Déficit (negativo) o superávit (positivo) de agua actual de esta zona. El riego se activa cuando el depósito cae por debajo del umbral.",
      zone_maximum_bucket: "Superávit máximo de humedad que la zona puede retener. El agua por encima de este nivel se trata como escorrentía. Valor típico: 50 mm.",
      zone_bucket_threshold: "El riego se activa cuando el depósito cae por debajo de este valor. Debe ser 0 o negativo. 0 significa regar siempre que haya déficit.",
      zone_multiplier: "Factor de escala aplicado a la duración calculada. Por encima de 1,0 aumenta, por debajo de 1,0 disminuye. Útil para ajustar sin cambiar las mediciones físicas.",
      zone_lead_time: "Segundos adicionales antes de que comience el riego. Úsalo para el calentamiento de la bomba o la presurización del sistema.",
      zone_maximum_duration: "Límite máximo absoluto para cualquier ciclo de riego individual en segundos. Evita el riego descontrolado. Predeterminado: 3600 s (1 hora).",
      zone_linked_entity: "La entidad de interruptor o válvula de HA que controla el flujo de agua de esta zona. Esta entidad se activa cuando se ejecuta el riego.",
      zone_flow_sensor: "Sensor opcional que mide el caudal real. Se usa solo para informes — no afecta a los cálculos de duración.",
      general_autoupdatedelay: "Segundos a esperar tras iniciar HA antes de la primera obtención de datos meteorológicos. Permite que otras integraciones se inicialicen primero.",
      general_sensor_debounce: "Intervalo mínimo en milisegundos entre lecturas del sensor para filtrar el ruido de sensores que cambian rápidamente.",
      general_calctime: "Hora del día en que se recalculan las duraciones de riego a partir de los datos meteorológicos recopilados. Formato: HH:MM (24 horas).",
      general_cleardatatime: "Hora del día en que se purgan los datos meteorológicos antiguos. Debe ser posterior a la hora de cálculo.",
      general_days_between: "Días mínimos entre eventos de riego para la misma zona. Pon 0 para desactivar (regar siempre que haya déficit).",
      general_autoupdateinterval: "Con qué frecuencia se recopilan los datos meteorológicos. Elige un valor que equilibre datos frescos con los límites de la API.",
      general_precipitation_threshold: "El riego se omite si la precipitación total prevista en la ventana de previsión supera esta cantidad.",
      general_temp_threshold: "El riego se omite si la temperatura actual es inferior a este valor (p. ej. para evitar daños por heladas).",
      general_wind_threshold: "El riego se omite si la velocidad del viento supera este valor (el viento fuerte reduce la eficiencia y causa deriva)."
    },
    St = {
      title: "Asistente de configuración",
      open_button: "Asistente de configuración",
      close: "Cerrar",
      next: "Siguiente",
      back: "Atrás",
      finish: "Finalizar",
      skip_step: "Omitir este paso",
      step_indicator: "Paso {current} de {total}",
      setup_complete_banner: "Configuración incompleta. Ejecuta el asistente para empezar.",
      open_wizard: "Abrir asistente",
      steps: {
        welcome: {
          title: "Bienvenido a Smart Irrigation",
          intro: "Este asistente te guía por los cuatro pasos necesarios para que tu primera zona riegue automáticamente.",
          step1_label: "Servicio meteorológico — de dónde obtener los datos meteorológicos",
          step2_label: "Módulo de cálculo — cómo se calcula la duración del riego",
          step3_label: "Grupo de sensores — qué fuentes de datos usar",
          step4_label: "Zona — tu primera zona de riego",
          tip: "Puedes omitir cualquier paso y configurarlo más tarde desde la pestaña Configuración."
        },
        weather: {
          title: "Servicio meteorológico",
          description: "Elige cómo obtener los datos meteorológicos. Open-Meteo es gratuito y no requiere clave API — es la opción más sencilla para la mayoría."
        },
        module: {
          title: "Módulo de cálculo",
          description: "Un módulo calcula cuánto regar según la evapotranspiración (ET). El módulo PyETO (método FAO-56) es el recomendado para la mayoría.",
          pick_label: "Seleccionar tipo de módulo",
          no_modules: "No hay tipos de módulo disponibles."
        },
        mapping: {
          title: "Grupo de sensores",
          description: "Un grupo de sensores vincula cada variable meteorológica con una fuente de datos. Define las variables clave a continuación — podrás refinar las asignaciones de sensores individuales más tarde en la pestaña Configuración → Grupos de sensores.",
          name_label: "Nombre del grupo de sensores",
          source_label: "Fuente de datos para",
          use_weather_service: "Servicio meteorológico",
          use_sensor: "Sensor",
          use_static: "Valor estático",
          use_none: "Ninguna / sin usar"
        },
        zone: {
          title: "Primera zona",
          description: "Una zona es un área de riego (p. ej. césped, parterre). Define las propiedades físicas para que el sistema pueda calcular la duración de riego correcta.",
          name_label: "Nombre de la zona",
          size_label: "Superficie",
          throughput_label: "Caudal del aspersor",
          entity_label: "Interruptor o válvula vinculados",
          entity_placeholder: "p. ej. switch.garden_valve",
          module_label: "Módulo de cálculo",
          mapping_label: "Grupo de sensores"
        },
        done: {
          title: "¡Configuración completada!",
          description: "Tu primera zona está lista. Smart Irrigation ahora calculará las duraciones de riego automáticamente según los datos meteorológicos.",
          next_steps: "Qué puedes hacer a continuación:",
          tip1: "Ve a Zonas para ver las duraciones calculadas y los valores del depósito.",
          tip2: "Añade más zonas desde la pestaña Zonas.",
          tip3: "Ajusta todos los parámetros desde la pestaña Configuración.",
          go_zones: "Ir a Zonas",
          go_setup: "Ir a Configuración"
        }
      },
      stepper: {
        weather: "Meteorología",
        module: "Módulo",
        mapping: "Grupo de sensores",
        zone: "Zona"
      },
      confirm_close: {
        body: "¿Cerrar el asistente de configuración? Tu progreso se ha guardado.",
        keep: "Seguir editando",
        close: "Cerrar"
      }
    },
    At = {
      common: ct,
      defaults: pt,
      module: mt,
      calcmodules: ht,
      panels: gt,
      title: vt,
      coordinate_config: _t,
      days_between_irrigation: ft,
      irrigation_start_triggers: bt,
      weather_skip: kt,
      zone_sequencing: yt,
      weather_service_config: zt,
      field_help: wt,
      wizard: St
    },
    xt = Object.freeze({
      __proto__: null,
      common: ct,
      defaults: pt,
      module: mt,
      calcmodules: ht,
      panels: gt,
      title: vt,
      coordinate_config: _t,
      days_between_irrigation: ft,
      irrigation_start_triggers: bt,
      weather_skip: kt,
      zone_sequencing: yt,
      weather_service_config: zt,
      field_help: wt,
      wizard: St,
      default: At
    }),
    Et = {
      actions: {
        delete: "Suppression",
        edit: "Modifier",
        save: "Enregistrer",
        cancel: "Annuler",
        confirm_delete: "Confirmer la suppression",
        confirm_delete_zone: "Voulez-vous vraiment supprimer cette zone ?"
      },
      labels: {
        module: "Module",
        no: "Non",
        select: "Sélectionner",
        yes: "Oui",
        enabled: "Activé",
        disabled: "Désactivé",
        before: "avant",
        after: "après",
        settings: "Paramètres",
        bulk_actions: "Actions groupées"
      },
      attributes: {
        size: "taille",
        throughput: "débit",
        state: "état",
        bucket: "réservoir",
        last_updated: "dernière mise à jour",
        last_calculated: "dernier calcul",
        number_of_data_points: "nombre de points de données"
      },
      loading: "Chargement",
      saving: "Enregistrement",
      units: {
        seconds: "secondes"
      },
      "loading-messages": {
        configuration: "Chargement de la configuration...",
        modules: "Chargement des modules...",
        general: "Chargement..."
      },
      "saving-messages": {
        adding: "Ajout...",
        saving: "Enregistrement..."
      },
      errors: {
        load_failed: "Impossible de charger les données",
        save_failed: "Impossible d'enregistrer les modifications",
        delete_failed: "Impossible de supprimer",
        action_failed: "Échec de l'action"
      }
    },
    Mt = {
      "default-zone": "Zone par défaut",
      "default-mapping": "Groupe de capteurs par défaut"
    },
    Tt = {
      calculation: {
        explanation: {
          "module-returned-evapotranspiration-deficiency": "NB: cette explication utilise '.' comme séparateur décimal, et affiche des valeurs arrondies. Le module a donné un manque d'Évapotranspiration de",
          "bucket-was": "Le seau (bucket) était de",
          "new-bucket-values-is": "La nouvelle valeur du seau (bucket) est",
          "old-bucket-variable": "ancien_bucket",
          delta: "delta",
          "bucket-less-than-zero-irrigation-necessary": "Puisque le seau (bucket) est < 0, l'irrigation est nécessaire",
          "steps-taken-to-calculate-duration": "Pour calculer la durée d'irrigation, les étapes suivantes ont été réalisées",
          "precipitation-rate-defined-as": "Le taux de précipitation est défini comme",
          "duration-is-calculated-as": "La durée d'irrigation est calculée avec",
          bucket: "seau (bucket)",
          "precipitation-rate-variable": "taux_precipitation",
          "multiplier-is-applied": "Le multiplicateur est appliqué. Le multiplicateur est",
          "duration-after-multiplier-is": "donc la durée d'irrigation est de",
          "maximum-duration-is-applied": "Ensuite la durée maximale est appliquée. La durée maximale est de",
          "duration-after-maximum-duration-is": "donc la durée d'irrigation est de",
          "lead-time-is-applied": "Enfin, le délai est appliqué. Le délai est de",
          "duration-after-lead-time-is": "et donc la durée finale est de",
          "bucket-larger-than-or-equal-to-zero-no-irrigation-necessary": "Puisque le seau (bucket) est >= 0, l'irrigation n'est pas nécessaire, et la durée est réglée à",
          "maximum-bucket-is": "la taille du seau (bucket) maximale est",
          "max-bucket-variable": "max_bucket",
          drainage: "drainage",
          "drainage-rate": "taux de drainage",
          hours: "heures",
          "drainage-rate-is": "Le taux de drainage à saturation (réservoir au maximum) est",
          "current-drainage-is": "Le drainage actuel est calculé comme",
          "no-drainage": "Le drainage actuel est 0 parce que"
        }
      }
    },
    Dt = {
      pyeto: {
        description: "Le calcul de durée est basée sur le calcul FAO56 de la bibliothèque PyETO"
      },
      static: {
        description: "Module 'Dummy' avec un delta statique configurable"
      },
      passthrough: {
        description: "Module passerelle qui renvoie la valeur d'un capteur d'Évapotranspiration comme delta"
      }
    },
    Pt = {
      general: {
        cards: {
          "automatic-duration-calculation": {
            header: "Calcul automatique de la durée",
            labels: {
              "auto-calc-enabled": "Calcule automatiquement la durée par zone",
              "auto-calc-time": "Calcule à",
              "calc-time": "Calculer à"
            },
            description: "Le calcul prend en compte les données météo jusqu'à ce point et met à jour le seau (bucket) pour chaque zone automatique. Ensuite, la durée est ajustée par la nouvelle valeur de seau (bucket) et les données météo sont supprimées."
          },
          "automatic-update": {
            errors: {
              "warning-update-time-on-or-after-calc-time": "Attention: mise à jour des données météo au moment du, ou après le, calcul"
            },
            header: "Mise à jour automatique des données météo",
            labels: {
              "auto-update-enabled": "Met à jour les données météo automatiquement",
              "auto-update-first-update": "(Première) Mise à jour à",
              "auto-update-interval": "Mettre à jour les données des capteurs toutes les",
              "auto-update-delay": "Délai de mise à jour",
              "auto-update-schedule": "Planning de mise à jour",
              "auto-update-time": "Mettre à jour à"
            },
            options: {
              days: "jours",
              hours: "heures",
              minutes: "minutes"
            },
            description: "Récupère et stocke les données météo automatiquement. Des données météo sont nécessaires pour calculer les seaux (buckets) par zone et les durées."
          },
          "automatic-clear": {
            header: "Délestage automatique des données météo",
            description: "Suppression automatique des données météo collectées à une heure données. Utilisez ceci pour être sûr qu'il n'y ait plus de restes des données météo des jours précédents. Ne supprimez pas les données météo avant le calcul et n'utilisez cette option que si vous vous attendez à ce que les données météo soient récupérées après le calcul du jour. Idéalement, vous voudrez \"élaguer\" les données les plus tard possible dans la journée.",
            labels: {
              "automatic-clear-enabled": "Suppression automatique des données météo collectées",
              "automatic-clear-time": "Supprimer les données météo à"
            }
          },
          continuousupdates: {
            header: "Mises à jour continues des capteurs (expérimental)",
            description: "Fonction expérimentale pour des données météo plus granulaires.",
            labels: {
              continuousupdates: "Activer les mises à jour continues",
              sensor_debounce: "Anti-rebond du capteur",
              "sensor-debounce": "Temps d'antirebond du capteur (ms)"
            }
          }
        },
        description: "Cette page fournit les réglages globaux.",
        title: "Général",
        sections: {
          weather: "Météo",
          automation: "Automatisation",
          location: "Emplacement",
          watering: "Comportement darrosage"
        }
      },
      help: {
        title: "Aide",
        cards: {
          "how-to-get-help": {
            title: "Comment obtenir de l'aide",
            "first-read-the": "Premièrement, lisez ",
            wiki: "Documentation",
            "if-you-still-need-help": "Si vous avez toujours besoin d'aide, adressez vous sur le",
            "community-forum": "forum communautaire",
            "or-open-a": "ou ouvrez un",
            "github-issue": "problème Github",
            "english-only": "en Anglais uniquement"
          }
        }
      },
      mappings: {
        cards: {
          "add-mapping": {
            actions: {
              add: "Ajouter un groupe de capteurs"
            },
            header: "Ajouter des groupes de capteurs"
          },
          mapping: {
            aggregates: {
              average: "Moyenne",
              first: "Premier",
              last: "Dernier",
              maximum: "Maximum",
              median: "Médian",
              minimum: "Minimum",
              sum: "Somme",
              riemannsum: "Somme de Riemann",
              delta: "Delta"
            },
            errors: {
              "cannot-delete-mapping-because-zones-use-it": "Vous ne pouvez pas supprimer ce groupe de capteurs car au moins une zone l'utilise.",
              invalid_source: "Source invalide",
              source_does_not_exist: "La source n'existe pas. Veuillez saisir une source valide, comme 'sensor.mysensor'."
            },
            items: {
              dewpoint: "Point de rosée",
              evapotranspiration: "Évapotranspiration",
              humidity: "Humidité",
              "maximum temperature": "Température maximale",
              "minimum temperature": "Température minimale",
              precipitation: "Précipitation totale",
              pressure: "Pression",
              "solar radiation": "Rayonnement solaire",
              temperature: "Température",
              windspeed: "Vitesse du vent",
              "current precipitation": "Précipitations actuelles"
            },
            "sensor-aggregate-of-sensor-values-to-calculate": "des valeurs des capteurs pour calculer la durée",
            "sensor-aggregate-use-the": "Utiliser les",
            "sensor-entity": "Entité capteur",
            static_value: "Valeur",
            "input-units": "L'entité fournit des entrées en",
            source: "Source",
            sources: {
              none: "Aucun",
              weather_service: "Service météo",
              sensor: "Capteur",
              static: "Valeur statique"
            },
            pressure_types: {
              relative: "relative",
              absolute: "absolue"
            },
            "pressure-type": "La pression est",
            "sensor-units": "Le capteur fournit les valeurs en"
          }
        },
        description: "Ajouter un ou plusieurs groupes de capteurs qui récupèrent les données météo de Weather service, de capteurs locaux ou d'une combinaison de tous ceux-ci. Vous pouvez associer chaque groupe de capteurs avec une ou plusieurs zones",
        labels: {
          "mapping-name": "Nom"
        },
        no_items: "Il n'y a pas encore de groupe de capteurs définis.",
        title: "Groupes de capteurs",
        "weather-records": {
          title: "Relevés météo",
          timestamp: "Heure",
          temperature: "Temp.",
          humidity: "Humidity",
          precipitation: "Précip.",
          "retrieval-time": "Récupéré",
          "no-data": "Aucune donnée météo disponible pour ce groupe de capteurs",
          dewpoint: "Rosée",
          wind: "Vent",
          pressure: "Pression"
        }
      },
      modules: {
        cards: {
          "add-module": {
            actions: {
              add: "Ajouter un module"
            },
            header: "Ajout d'un module"
          },
          module: {
            errors: {
              "cannot-delete-module-because-zones-use-it": "Vous ne pouvez pas supprimer ce module car au moins une zone l'utilise."
            },
            labels: {
              configuration: "Configuration",
              required: "indique un champ requis"
            },
            "translated-options": {
              DontEstimate: "Ne fait pas d'estimation",
              EstimateFromSunHours: "Estimation à partir des heures d'ensoleillement",
              EstimateFromTemp: "Estimation à partir de la température",
              EstimateFromSunHoursAndTemperature: "Estimer à partir de la moyenne des heures d'ensoleillement et de la température"
            }
          }
        },
        description: "Ajouter un ou plusieurs modules qui calcule la durée d'irrigation. Chaque module vient avec sa propre configuration et peut être utilisé pour calculer la durée d'irrigation d'une ou plusieurs zones.",
        no_items: "Il n'y a aucun module défini pour l'instant.",
        title: "Modules"
      },
      zones: {
        actions: {
          add: "Ajouter",
          calculate: "Calculer",
          information: "Informations",
          update: "Mise à jour",
          "reset-bucket": "Mise à zéro du seau (bucket)",
          "view-weather-info": "Voir données météo",
          "view-weather-info-message": "Données météo disponibles pour",
          "view-watering-calendar": "Calendrier d'arrosage",
          irrigate_all: "Arroser toutes les zones maintenant",
          open_settings: "Modifier les réglages"
        },
        cards: {
          "add-zone": {
            actions: {
              add: "Ajouter une zone"
            },
            header: "Ajout d'une zone"
          },
          "zone-actions": {
            actions: {
              "calculate-all": "Recalculer les durées",
              "update-all": "Actualiser les données météo",
              "reset-all-buckets": "Mise à zéro de tous les seaux (buckets)",
              "clear-all-weatherdata": "Mise à zéro de toutes les données météo"
            },
            header: "Actions sur toutes les zones"
          }
        },
        description: "Spécifiez une ou plusieurs zones d'irrigation ici. La durée d'irrigation est calculée par zone, en fonction de la taille, du débit, état, module et groupe de capteurs.",
        labels: {
          bucket: "Seau",
          duration: "Durée",
          "lead-time": "Délai",
          mapping: "Groupe de capteurs",
          "maximum-duration": "Durée maximale",
          multiplier: "Multiplicateur",
          name: "Nom",
          size: "Taille",
          state: "État",
          states: {
            automatic: "Automatique",
            disabled: "Désactivé",
            manual: "Manuel"
          },
          throughput: "Débit",
          "maximum-bucket": "Seau (bucket) maximum",
          last_calculated: "Dernier calcul",
          "data-last-updated": "Dernière mise à jour",
          "data-number-of-data-points": "Nombre de points de données",
          drainage_rate: "Taux de drainage",
          linked_entity: "Entité interrupteur/vanne liée",
          linked_entity_placeholder: "ex. switch.vanne_jardin",
          irrigate_now: "Irriguer maintenant",
          bucket_threshold: "Déficit minimum pour irriguer",
          flow_sensor: "Capteur de débitmètre (optionnel)",
          flow_sensor_placeholder: "p. ex. sensor.zone_flow_rate"
        },
        no_items: "Il n'y a pas encore de zone définie.",
        title: "Zones",
        confirm_irrigate: {
          title: "Démarrer l'arrosage ?",
          body: "Ceci ouvre maintenant la ou les vannes liées et ignore toutes les conditions d'exclusion (pluie, température, nombre minimal de jours entre les arrosages).",
          all_linked_zones: "Toutes les zones liées",
          toast_started: "Arrosage démarré",
          toast_failed: "Échec de l'arrosage"
        },
        status: {
          decision_disabled: "Désactivée — cette zone ne sera pas arrosée automatiquement.",
          decision_water: "Arrosage nécessaire : environ {duration} au prochain cycle programmé.",
          decision_water_at: "Arrosera environ {duration} à {time}.",
          decision_water_skip: "Déficit ~{duration}, mais le prochain cycle sera probablement ignoré ({reason}).",
          decision_water_no_schedule: "Déficit ~{duration} — aucun horaire n'arrose cette zone ; déclenchez-la manuellement.",
          decision_no_water: "Aucun arrosage nécessaire pour le moment — le sol a assez d'humidité.",
          decision_unknown: "Pas encore calculé — appuyez sur Mettre à jour, puis Calculer pour vérifier.",
          last_checked: "Dernière vérification",
          never: "jamais",
          saved: "Enregistré",
          estimate_now: "Maintenant",
          estimate_tag: "est.",
          estimate_method: {
            hourly: "Estimation en direct à partir de la météo horaire depuis le dernier calcul",
            proxy: "Estimation répartie à partir de la prévision du jour depuis le dernier calcul"
          }
        },
        help: {
          bucket: "Bilan d'humidité du sol (seau). Une valeur négative signifie que le sol est sec et que la zone a besoin d'eau.",
          calculate: "Calcule la durée d'arrosage à partir des dernières données. À lancer après Mettre à jour.",
          update: "Récupère les dernières données météo/capteurs pour cette zone.",
          irrigate_link_entity: "Associez un interrupteur/une vanne dans les réglages de cette zone pour activer l'arrosage manuel.",
          irrigate_all: "Ouvre maintenant les vannes liées de chaque zone en déficit. Les conditions d'exclusion (pluie, vent, température) sont ignorées.",
          update_all: "Collecte les dernières données météo/capteurs pour toutes les zones. Ne change pas les durées en soi.",
          calculate_all: "Recalcule la durée d'arrosage de chaque zone automatique à partir des données collectées jusqu'ici."
        },
        outlook: {
          next_run: "Prochain cycle",
          no_schedule: "Aucun horaire automatique — les zones ne s'arrosent que lorsque vous les déclenchez.",
          setup_schedule: "Configurer un horaire",
          targets_all: "toutes les zones",
          targets_zones: "{count} zones",
          will_skip: "Le prochain cycle sera probablement ignoré",
          will_run: "Les conditions semblent favorables pour le prochain cycle.",
          why_skipped: "Pourquoi ?",
          provisional: "prévision — peut changer",
          active_guards: "Conditions actives",
          last_run: "Dernier cycle",
          last_run_skipped: "ignoré",
          last_run_ran: "exécuté",
          today: "aujourd'hui",
          tomorrow: "demain",
          actions: {
            irrigate: "Arroser",
            calculate: "Recalculer",
            update: "Actualiser les données"
          },
          checks: {
            precipitation: "Pluie prévue",
            days_between: "Jours entre arrosages",
            temperature: "Température basse",
            wind: "Vent fort",
            rain_sensor: "Capteur de pluie"
          },
          check_detail: {
            precipitation: "{observed} mm (≥ {threshold} mm)",
            days_between: "{observed}/{threshold} jours",
            temperature: "{observed}° (sous {threshold}°)",
            wind: "{observed} (au-dessus de {threshold})",
            rain_sensor: "{observed}"
          }
        },
        calendar: {
          no_data: "Aucune donnée de calendrier d'arrosage disponible pour cette zone.",
          error_prefix: "Erreur lors de la génération du calendrier :",
          month: "Mois",
          et: "ET (mm)",
          precipitation: "Précipitations (mm)",
          watering: "Arrosage (L)",
          avg_temp: "Temp. moy. (°C)",
          method_prefix: "Méthode :"
        },
        confirm_action: {
          reset_bucket_title: "Réinitialiser le seau de cette zone ?",
          reset_bucket_body: "Cela remet le seau à 0 et supprime le bilan d'humidité accumulé pour cette zone.",
          reset_all_buckets_title: "Réinitialiser tous les seaux ?",
          reset_all_buckets_body: "Cela remet à 0 le seau de chaque zone et supprime le bilan d'humidité accumulé. Les calculs d'arrosage repartiront de zéro à la prochaine mise à jour.",
          clear_weather_title: "Effacer toutes les données météo ?",
          clear_weather_body: "Cela supprime tous les relevés météo et capteurs de toutes les zones. Les zones auront besoin de nouvelles données avant de pouvoir recalculer."
        }
      },
      schedules: {
        title: "Planifications",
        description: "Créez des planifications récurrentes pour calculer, mettre à jour ou irriguer automatiquement — sans automatisations.",
        add: "Ajouter une planification",
        no_items: "Aucune planification configurée. Cliquez sur 'Ajouter une planification'.",
        zones_all: "Toutes les zones",
        zones_specific: "Zones spécifiques",
        hours: "heures",
        minutes: "min",
        types: {
          daily: "Quotidien",
          weekly: "Hebdomadaire",
          monthly: "Mensuel",
          interval: "Toutes les N heures",
          sunrise: "Lever du soleil",
          sunset: "Coucher du soleil",
          solar_azimuth: "Azimut solaire"
        },
        actions: {
          calculate: "Calculer (mettre à jour la durée d'irrigation)",
          update: "Mettre à jour (collecter données météo)",
          irrigate: "Irriguer (contrôler les vannes directement)"
        },
        days: {
          monday: "Lu",
          tuesday: "Ma",
          wednesday: "Me",
          thursday: "Je",
          friday: "Ve",
          saturday: "Sa",
          sunday: "Di"
        },
        fields: {
          name: "Nom",
          type: "Type de planification",
          enabled: "Activé",
          time: "Heure (HH:MM)",
          days_of_week: "Jours de la semaine",
          day_of_month: "Jour du mois",
          interval_hours: "Intervalle",
          action: "Action",
          zones: "Zones",
          start_date: "Date de début (optionnel)",
          end_date: "Date de fin (optionnel)",
          offset_minutes: "Décalage par rapport au lever/coucher du soleil",
          account_for_duration: "Démarrer tôt pour que l'irrigation se termine à l'heure cible",
          azimuth_angle: "Angle d'azimut solaire",
          time_anchor: "Lheure correspond au"
        },
        dialog: {
          add_title: "Ajouter une planification",
          edit_title: "Modifier la planification"
        },
        time_anchor: {
          start: "Début de larrosage",
          finish: "Fin de larrosage"
        }
      },
      info: {
        title: "Infos",
        description: "Afficher les informations sur la prochaine irrigation et l'état du système.",
        "configuration-not-available": "Configuration non disponible.",
        cards: {
          "zone-bucket-values": {
            title: "Valeurs de réservoir et durée",
            labels: {
              bucket: "Réservoir",
              duration: "Durée"
            },
            "no-zones": "Aucune zone configurée"
          },
          "next-irrigation": {
            title: "Prochaine irrigation",
            labels: {
              "next-start": "Prochain démarrage",
              duration: "Durée",
              zones: "Zones"
            },
            "no-data": "Aucune donnée disponible"
          },
          "irrigation-reason": {
            title: "Raison d'irrigation",
            labels: {
              reason: "Raison",
              sunrise: "Lever du soleil",
              "total-duration": "Durée totale",
              explanation: "Explication"
            },
            "no-data": "Aucune donnée disponible"
          },
          irrigate_now: {
            title: "Irriguer maintenant",
            description: "Démarrer immédiatement l'irrigation pour toutes les zones avec une entité liée. Les conditions d'exclusion sont ignorées.",
            button_all: "Démarrer toutes les zones maintenant",
            no_linked_zones: "Aucune zone n'a d'entité interrupteur/vanne liée avec une durée calculée."
          }
        }
      },
      setup: {
        title: "Configuration"
      }
    },
    jt = "Smart Irrigation",
    Nt = {
      title: "Coordonnées de Localisation",
      description: "Configurez les coordonnées de localisation pour la récupération des données météo. Vous pouvez utiliser des coordonnées manuelles différentes de votre emplacement Home Assistant si nécessaire.",
      manual_enabled: "Utiliser des coordonnées manuelles",
      use_ha_location: "Utiliser l'emplacement Home Assistant",
      latitude: "Latitude (degrés décimaux)",
      longitude: "Longitude (degrés décimaux)",
      elevation: "Élévation (mètres au-dessus du niveau de la mer)",
      current_ha_coords: "Coordonnées actuelles de Home Assistant"
    },
    Ct = {
      title: "Jours entre irrigations",
      description: "Configurez le nombre minimum de jours entre les événements d'irrigation.",
      label: "Jours minimum entre irrigations",
      help_text: "Définissez 0 pour désactiver. Les valeurs de 1 à 365 jours sont supportées."
    },
    Ht = {
      title: "Déclencheurs de démarrage d'arrosage",
      description: "Configurez le moment où l'arrosage doit démarrer en fonction des événements solaires. Vous pouvez ajouter plusieurs déclencheurs pour différents horaires. Pour les déclencheurs au lever du soleil, laisser le décalage à 0 utilisera automatiquement la durée totale de toutes les zones activées.",
      add_trigger: "Ajouter un déclencheur",
      edit_trigger: "Modifier le déclencheur",
      delete_trigger: "Supprimer le déclencheur",
      trigger_types: {
        sunrise: "Lever du soleil",
        sunset: "Coucher du soleil",
        solar_azimuth: "Azimut solaire"
      },
      fields: {
        name: {
          name: "Nom du déclencheur",
          description: "Un nom descriptif pour identifier ce déclencheur"
        },
        type: {
          name: "Type de déclencheur",
          description: "Le type d'événement solaire qui déclenche"
        },
        enabled: {
          name: "Activé",
          description: "Si ce déclencheur est actuellement actif"
        },
        offset_minutes: {
          name: "Décalage (minutes)",
          description: "Minutes avant (-) ou après (+) l'événement solaire. Pour les déclencheurs au lever du soleil, utilisez 0 pour une temporisation automatique basée sur la durée totale des zones."
        },
        azimuth_angle: {
          name: "Angle d'azimut (degrés)",
          description: "Angle d'azimut solaire en degrés où 0=Nord, 90=Est, 180=Sud, 270=Ouest"
        },
        account_for_duration: {
          name: "Tenir compte de la durée",
          description: "Si activé, l'arrosage démarrera suffisamment tôt pour se terminer à l'heure indiquée. Si désactivé, l'arrosage démarrera exactement à l'heure indiquée."
        }
      },
      dialog: {
        add_title: "Ajouter un déclencheur de démarrage d'arrosage",
        edit_title: "Modifier le déclencheur de démarrage d'arrosage",
        cancel: "Annuler",
        save: "Enregistrer",
        delete: "Supprimer"
      },
      no_triggers: "Aucun déclencheur de démarrage d'arrosage configuré. Le système utilisera le comportement par défaut (lever du soleil avec la durée totale des zones). Ajoutez des déclencheurs pour personnaliser le démarrage de l'arrosage.",
      offset_auto: "Automatique (calculé à partir de la durée totale des zones)",
      confirm_delete: "Voulez-vous vraiment supprimer le déclencheur '{name}' ?",
      validation: {
        name_required: "Le nom du déclencheur est requis",
        azimuth_invalid: "L'angle d'azimut doit être un nombre valide"
      },
      help: {
        sunrise_offset: "Pour les déclencheurs au lever du soleil : utilisez des valeurs négatives pour démarrer avant le lever, positives pour démarrer après. Mettez 0 pour démarrer automatiquement assez tôt pour terminer toutes les zones avant le lever du soleil.",
        sunset_offset: "Pour les déclencheurs au coucher du soleil : utilisez des valeurs négatives pour démarrer avant le coucher, positives pour démarrer après.",
        azimuth_explanation: "L'azimut solaire est la direction de la boussole du soleil. 0°=Nord, 90°=Est, 180°=Sud, 270°=Ouest. Vous pouvez saisir n'importe quelle valeur d'angle (p. ex. 450° = 90°, -30° = 330°). Utilisez ceci pour déclencher l'arrosage lorsque le soleil atteint une position précise.",
        multiple_triggers: "Vous pouvez configurer plusieurs déclencheurs. Chaque déclencheur activé planifiera les démarrages d'arrosage de manière indépendante."
      }
    },
    Ot = {
      title: "Conditions d'exclusion",
      description: "Ignorer automatiquement l'irrigation quand les conditions sont défavorables. Les vérifications de précipitations, température et vent nécessitent un service météo.",
      threshold_label: "Seuil de précipitations",
      threshold_description: "Précipitations totales minimales prévues (en mm) sur la fenêtre de prévision pour ignorer l'irrigation.",
      lookahead_label: "Fenêtre de prévision (jours)",
      lookahead_help: "Nombre de jours de prévision à venir additionnés lors de la vérification de la pluie. La prévision commence demain (aujourd'hui est exclu), donc 1 = uniquement le lendemain, 2 = les deux prochains jours, etc.",
      temp_section_title: "Ignorer par basse température",
      temp_threshold_label: "Ignorer si température en dessous de",
      wind_section_title: "Ignorer par vent fort",
      wind_threshold_label: "Ignorer si vitesse du vent supérieure à",
      rain_sensor_section_title: "Condition du capteur de pluie",
      rain_sensor_label: "Entité capteur de pluie (optionnel)",
      rain_sensor_placeholder: "ex. binary_sensor.pluie"
    },
    Lt = {
      title: "Séquençage des zones",
      description: "Lorsque plusieurs zones ont besoin d'irrigation, choisissez si elles fonctionnent simultanément ou l'une après l'autre. En mode séquentiel, le système attend que chaque zone se termine avant de démarrer la suivante.",
      parallel: "Parallèle (toutes les zones simultanément)",
      sequential: "Séquentiel (une zone à la fois)",
      rotating: "Rotatif (les zones se relaient)",
      max_consecutive_duration_label: "Durée d'exécution consécutive max. par zone",
      max_consecutive_duration_unit: "minutes",
      min_absorption_time_label: "Temps d'absorption min. entre les passages",
      min_absorption_time_unit: "minutes (0 = désactivé)"
    },
    It = {
      title: "Service météo",
      description: "Configurez le service météo à utiliser pour les calculs d'ET et les conditions de saut.",
      enabled_label: "Activer le service météo",
      service_label: "Service météo",
      api_key_label: "Clé API",
      api_key_placeholder: "Laisser vide pour conserver la clé existante",
      api_key_configured: "La clé API est configurée",
      api_key_not_configured: "Aucune clé API configurée",
      api_key_help: "Une clé API de votre fournisseur de service météo choisi. Open-Meteo ne nécessite pas de clé. OpenWeatherMap et Pirate Weather offrent tous deux des offres gratuites.",
      no_api_key_needed: "Open-Meteo est un service gratuit et ne nécessite aucune clé API.",
      save_button: "Enregistrer les paramètres météo",
      saved: "Paramètres météo enregistrés",
      openmeteo: "Open-Meteo (gratuit, sans clé)",
      test_button: "Tester la connexion",
      test_button_testing: "Test en cours…",
      test_success: "✓ Connexion réussie",
      test_error_invalid_auth: "✗ Clé API invalide — vérifiez qu'elle est correcte et active",
      test_error_cannot_connect: "✗ Connexion impossible — vérifiez votre connexion internet",
      test_error_no_service: "✗ Sélectionnez d'abord un service météo",
      test_error_unknown: "✗ Échec du test — erreur inconnue",
      owm: "OpenWeatherMap",
      pw: "Pirate Weather"
    },
    Bt = {
      zone_size: "La surface arrosée totale de cette zone. Utilisée avec le débit pour calculer la quantité d'eau appliquée par passage.",
      zone_throughput: "Débit d'eau total de votre système d'arrosage pour cette zone (litres/min en métrique, gal/min en impérial). Consultez la fiche technique de vos arroseurs ou mesurez le temps nécessaire pour remplir un récipient de volume connu.",
      zone_drainage_rate: "La vitesse à laquelle l'eau excédentaire s'évacue du sol lorsque le réservoir est plein. Typique : pelouse 50 mm/h, sol sableux 100+ mm/h, argile 10 mm/h.",
      zone_bucket: "Déficit (négatif) ou excédent (positif) d'eau actuel de cette zone. L'arrosage se déclenche lorsque le réservoir descend sous le seuil.",
      zone_maximum_bucket: "Excédent d'humidité maximal que la zone peut retenir. L'eau au-delà de ce niveau est considérée comme du ruissellement. Valeur typique : 50 mm.",
      zone_bucket_threshold: "L'arrosage se déclenche lorsque le réservoir descend sous cette valeur. Doit être 0 ou négatif. 0 signifie arroser dès qu'il y a un déficit.",
      zone_multiplier: "Facteur d'échelle appliqué à la durée calculée. Au-dessus de 1,0 pour augmenter, en dessous de 1,0 pour diminuer. Utile pour un réglage fin sans modifier les mesures physiques.",
      zone_lead_time: "Secondes supplémentaires avant le démarrage de l'arrosage. À utiliser pour la mise en chauffe de la pompe ou la mise en pression du système.",
      zone_maximum_duration: "Plafond strict pour un seul passage d'arrosage en secondes. Empêche un arrosage incontrôlé. Par défaut : 3600 s (1 heure).",
      zone_linked_entity: "L'entité interrupteur ou vanne de HA qui contrôle le débit d'eau de cette zone. Cette entité est activée lorsque l'arrosage fonctionne.",
      zone_flow_sensor: "Capteur optionnel mesurant le débit d'eau réel. Utilisé uniquement pour le rapport — n'affecte pas les calculs de durée.",
      general_autoupdatedelay: "Secondes à attendre après le démarrage de HA avant la première récupération des données météo. Permet aux autres intégrations de s'initialiser d'abord.",
      general_sensor_debounce: "Écart minimal en millisecondes entre les lectures du capteur pour filtrer le bruit des capteurs qui changent rapidement.",
      general_calctime: "Heure de la journée à laquelle les durées d'arrosage sont recalculées à partir des données météo collectées. Format : HH:MM (24 heures).",
      general_cleardatatime: "Heure de la journée à laquelle les anciennes données météo sont purgées. Doit être réglée après l'heure de calcul.",
      general_days_between: "Nombre minimal de jours entre les arrosages d'une même zone. Mettre 0 pour désactiver (arroser dès qu'il y a un déficit).",
      general_autoupdateinterval: "Fréquence de collecte des données météo. Choisissez une valeur qui équilibre la fraîcheur des données et les limites de l'API.",
      general_precipitation_threshold: "L'arrosage est ignoré si le total des précipitations prévues sur la fenêtre de prévision dépasse cette valeur.",
      general_temp_threshold: "L'arrosage est ignoré si la température actuelle est inférieure à cette valeur (p. ex. pour éviter les dégâts du gel).",
      general_wind_threshold: "L'arrosage est ignoré si la vitesse du vent dépasse cette valeur (un vent fort réduit l'efficacité et provoque une dérive)."
    },
    Rt = {
      title: "Assistant de configuration",
      open_button: "Assistant de configuration",
      close: "Fermer",
      next: "Suivant",
      back: "Retour",
      finish: "Terminer",
      skip_step: "Ignorer cette étape",
      step_indicator: "Étape {current} sur {total}",
      setup_complete_banner: "Configuration non terminée. Lancez l'assistant pour commencer.",
      open_wizard: "Ouvrir l'assistant",
      steps: {
        welcome: {
          title: "Bienvenue dans Smart Irrigation",
          intro: "Cet assistant vous guide à travers les quatre étapes nécessaires pour que votre première zone arrose automatiquement.",
          step1_label: "Service météo — où obtenir les données météo",
          step2_label: "Module de calcul — comment la durée d'arrosage est calculée",
          step3_label: "Groupe de capteurs — quelles sources de données utiliser",
          step4_label: "Zone — votre première zone d'arrosage",
          tip: "Vous pouvez ignorer n'importe quelle étape et la configurer plus tard depuis l'onglet Configuration."
        },
        weather: {
          title: "Service météo",
          description: "Choisissez comment obtenir les données météo. Open-Meteo est gratuit et ne nécessite pas de clé API — c'est le choix le plus simple pour la plupart des utilisateurs."
        },
        module: {
          title: "Module de calcul",
          description: "Un module calcule la durée d'arrosage en fonction de l'évapotranspiration (ET). Le module PyETO (méthode FAO-56) est recommandé pour la plupart des utilisateurs.",
          pick_label: "Sélectionner le type de module",
          no_modules: "Aucun type de module disponible."
        },
        mapping: {
          title: "Groupe de capteurs",
          description: "Un groupe de capteurs relie chaque variable météo à une source de données. Définissez les variables clés ci-dessous — vous pourrez affiner chaque association de capteur plus tard depuis l'onglet Configuration → Groupes de capteurs.",
          name_label: "Nom du groupe de capteurs",
          source_label: "Source de données pour",
          use_weather_service: "Service météo",
          use_sensor: "Capteur",
          use_static: "Valeur statique",
          use_none: "Aucune / non utilisé"
        },
        zone: {
          title: "Première zone",
          description: "Une zone est une surface d'arrosage (p. ex. pelouse, massif). Définissez les propriétés physiques pour que le système puisse calculer la durée d'arrosage correcte.",
          name_label: "Nom de la zone",
          size_label: "Surface",
          throughput_label: "Débit de l'arroseur",
          entity_label: "Interrupteur ou vanne lié",
          entity_placeholder: "p. ex. switch.garden_valve",
          module_label: "Module de calcul",
          mapping_label: "Groupe de capteurs"
        },
        done: {
          title: "Configuration terminée !",
          description: "Votre première zone est prête. Smart Irrigation calculera désormais les durées d'arrosage automatiquement à partir des données météo.",
          next_steps: "Ce que vous pouvez faire ensuite :",
          tip1: "Allez dans Zones pour voir les durées calculées et les valeurs du réservoir.",
          tip2: "Ajoutez d'autres zones depuis l'onglet Zones.",
          tip3: "Affinez tous les paramètres depuis l'onglet Configuration.",
          go_zones: "Aller aux Zones",
          go_setup: "Aller à la Configuration"
        }
      },
      stepper: {
        weather: "Météo",
        module: "Module",
        mapping: "Groupe de capteurs",
        zone: "Zone"
      },
      confirm_close: {
        body: "Fermer lassistant de configuration ? Votre progression est enregistrée.",
        keep: "Continuer",
        close: "Fermer"
      }
    },
    Ut = {
      common: Et,
      defaults: Mt,
      module: Tt,
      calcmodules: Dt,
      panels: Pt,
      title: jt,
      coordinate_config: Nt,
      days_between_irrigation: Ct,
      irrigation_start_triggers: Ht,
      weather_skip: Ot,
      zone_sequencing: Lt,
      weather_service_config: It,
      field_help: Bt,
      wizard: Rt
    },
    $t = Object.freeze({
      __proto__: null,
      common: Et,
      defaults: Mt,
      module: Tt,
      calcmodules: Dt,
      panels: Pt,
      title: jt,
      coordinate_config: Nt,
      days_between_irrigation: Ct,
      irrigation_start_triggers: Ht,
      weather_skip: Ot,
      zone_sequencing: Lt,
      weather_service_config: It,
      field_help: Bt,
      wizard: Rt,
      default: Ut
    }),
    Vt = {
      actions: {
        delete: "Cancella",
        edit: "Modifica",
        save: "Salva",
        cancel: "Annulla",
        confirm_delete: "Conferma eliminazione",
        confirm_delete_zone: "Vuoi davvero eliminare questa zona?"
      },
      labels: {
        module: "Modulo",
        no: "No",
        select: "Seleziona",
        yes: "Si",
        enabled: "Abilitato",
        disabled: "Disabilitato",
        before: "prima",
        after: "dopo",
        settings: "Impostazioni",
        bulk_actions: "Azioni multiple"
      },
      units: {
        seconds: "secondi"
      },
      attributes: {
        size: "dimensione",
        throughput: "portata",
        state: "stato",
        bucket: "serbatoio",
        last_updated: "ultimo aggiornamento",
        last_calculated: "ultimo calcolo",
        number_of_data_points: "numero di punti dati"
      },
      loading: "Caricamento",
      saving: "Salvataggio",
      "loading-messages": {
        configuration: "Caricamento configurazione...",
        modules: "Caricamento moduli...",
        general: "Caricamento..."
      },
      "saving-messages": {
        adding: "Aggiungendo...",
        saving: "Salvataggio..."
      },
      errors: {
        load_failed: "Impossibile caricare i dati",
        save_failed: "Impossibile salvare le modifiche",
        delete_failed: "Impossibile eliminare",
        action_failed: "Azione non riuscita"
      }
    },
    Wt = {
      "default-zone": "Zona predefinita",
      "default-mapping": "Mappatura predefinita"
    },
    Ft = {
      calculation: {
        explanation: {
          "module-returned-evapotranspiration-deficiency": "Il modulo ha restituito un deficit di evapotraspirazione del",
          "bucket-was": "Il secchio era",
          "new-bucket-values-is": "Il nuovo valore del secchio è",
          bucket: "secchio",
          "old-bucket-variable": "old_bucket",
          "max-bucket-variable": "max_bucket",
          delta: "delta",
          "bucket-less-than-zero-irrigation-necessary": "Poiché secchio < 0, è necessaria l'irrigazione",
          "steps-taken-to-calculate-duration": "Per calcolare la durata esatta, sono stati eseguiti i seguenti passaggi",
          "precipitation-rate-defined-as": "Il tasso di precipitazione è definito come",
          "duration-is-calculated-as": "La durata viene calcolata come",
          drainage: "drenaggio",
          "drainage-rate": "tasso_di_drenaggio",
          hours: "ore",
          "precipitation-rate-variable": "tasso_di_precipitazione",
          "multiplier-is-applied": "Ora viene applicato il moltiplicatore. Il moltiplicatore è",
          "duration-after-multiplier-is": "quindi la durata è",
          "maximum-duration-is-applied": "Quindi, viene applicata la durata massima. La durata massima è",
          "duration-after-maximum-duration-is": "quindi la durata è",
          "lead-time-is-applied": "Infine, viene applicato il lead time. Il tempo di consegna è",
          "duration-after-lead-time-is": "quindi la durata finale è",
          "bucket-larger-than-or-equal-to-zero-no-irrigation-necessary": "Poiché secchio >= 0, non è necessaria alcuna irrigazione e la durata è impostata su",
          "maximum-bucket-is": "la dimensione massima del secchio è",
          "drainage-rate-is": "Il tasso di drenaggio a saturazione (serbatoio al massimo) è",
          "current-drainage-is": "Il drenaggio attuale è calcolato come",
          "no-drainage": "Il drenaggio attuale è 0 perché"
        }
      }
    },
    qt = {
      pyeto: {
        description: "Calcola la durata in base al calcolo FAO56 dalla libreria PyETO"
      },
      static: {
        description: "Modulo 'fittizio' con un delta configurabile statico"
      },
      passthrough: {
        description: "Modulo passthrough che restituisce il valore di un sensore di Evapotraspirazione sotto forma di delta"
      }
    },
    Zt = {
      general: {
        cards: {
          "automatic-duration-calculation": {
            header: "Calcolo automatico della durata",
            description: "Il calcolo prende i dati meteorologici raccolti fino a quel momento e aggiorna il bucket per ciascuna zona automatica. Quindi, la durata viene regolata in base al nuovo valore del segmento e i dati meteorologici raccolti vengono rimossi.",
            labels: {
              "auto-calc-enabled": "Calcola automaticamente la durata delle zone",
              "auto-calc-time": "Calcola a",
              "calc-time": "Calcola alle"
            }
          },
          "automatic-update": {
            errors: {
              "warning-update-time-on-or-after-calc-time": "Attenzione: ora di aggiornamento dei dati meteorologici in corrispondenza o dopo l'ora di calcolo"
            },
            header: "Aggiornamento automatico dei dati meteorologici",
            description: "Raccogli e archivia automaticamente i dati meteorologici. I dati meteorologici sono necessari per calcolare gli intervalli e le durate delle zone.",
            labels: {
              "auto-update-enabled": "Aggiorna automaticamente i dati meteorologici",
              "auto-update-first-update": "(Primo) aggiornamento alle",
              "auto-update-interval": "Aggiorna i dati del sensore ogni",
              "auto-update-schedule": "Pianificazione aggiornamento",
              "auto-update-time": "Aggiorna alle",
              "auto-update-delay": "Ritardo di aggiornamento"
            },
            options: {
              days: "giorni",
              hours: "ore",
              minutes: "minuti"
            }
          },
          "automatic-clear": {
            header: "Eliminazione automatica dei dati meteo",
            description: "Rimuovi automaticamente i dati meteo raccolti a un orario configurato. Usa questa opzione per assicurarti che non vi siano dati meteo residui dei giorni precedenti. Non rimuovere i dati meteo prima di effettuare il calcolo e utilizza questa opzione solo se prevedi che l'aggiornamento automatico raccolga i dati meteo dopo aver effettuato il calcolo giornaliero. Idealmente, la rimozione dei dati meteo dovrebbe avvenire il più tardi possibile.",
            labels: {
              "automatic-clear-enabled": "Cancella automaticamente i dati meteorologici raccolti",
              "automatic-clear-time": "Cancella dati meteo a"
            }
          },
          continuousupdates: {
            header: "Aggiornamenti continui sensori (sperimentale)",
            description: "Funzione sperimentale per dati meteo più granulari.",
            labels: {
              continuousupdates: "Abilita gli aggiornamenti continui",
              sensor_debounce: "Rimbalzo del sensore",
              "sensor-debounce": "Tempo anti-rimbalzo sensore (ms)"
            }
          }
        },
        description: "Questa pagina fornisce le impostazioni globali.",
        title: "Generale",
        sections: {
          weather: "Meteo",
          automation: "Automazione",
          location: "Posizione",
          watering: "Comportamento di irrigazione"
        }
      },
      help: {
        title: "Aiuto",
        cards: {
          "how-to-get-help": {
            title: "Come ottenere aiuto",
            "first-read-the": "Per prima cosa, leggi il",
            wiki: "Documentazione",
            "if-you-still-need-help": "Se hai ancora bisogno di aiuto, contatta il",
            "community-forum": "Forum della Comunità",
            "or-open-a": "oppure apri un",
            "github-issue": "Problema su Github",
            "english-only": "soltanto in Inglese"
          }
        }
      },
      info: {
        title: "Info",
        description: "Visualizza informazioni sulla prossima irrigazione e lo stato del sistema.",
        cards: {
          "next-irrigation": {
            title: "Prossima irrigazione",
            labels: {
              "next-start": "Prossimo avvio",
              duration: "Durata",
              zones: "Zone"
            },
            "no-data": "Nessun dato disponibile",
            "backend-todo": "TODO: API di backend necessaria per le informazioni sull'irrigazione"
          },
          "irrigation-reason": {
            title: "Motivo irrigazione",
            labels: {
              reason: "Ragione",
              sunrise: "Alba",
              "total-duration": "Durata totale",
              explanation: "Spiegazione"
            },
            "no-data": "Nessun dato disponibile",
            "backend-todo": "TODO: API di backend necessaria per le informazioni sull'irrigazione"
          },
          "zone-bucket-values": {
            title: "Valori serbatoio e durata",
            labels: {
              bucket: "Serbatoio",
              duration: "Durata"
            },
            "no-zones": "Nessuna zona configurata"
          },
          irrigate_now: {
            title: "Irriga ora",
            description: "Avvia immediatamente l'irrigazione per tutte le zone con entità collegata. Le condizioni di esclusione vengono ignorate.",
            button_all: "Avvia tutte le zone ora",
            no_linked_zones: "Nessuna zona ha un'entità interruttore/valvola collegata con durata calcolata."
          }
        },
        "configuration-not-available": "Configurazione non disponibile."
      },
      mappings: {
        cards: {
          "add-mapping": {
            actions: {
              add: "Aggiungi gruppo di sensori"
            },
            header: "Aggiungi gruppo di sensori"
          },
          mapping: {
            aggregates: {
              average: "Media",
              first: "Primo",
              last: "Ultimo",
              maximum: "Massimo",
              median: "Mediana",
              minimum: "Minimo",
              riemannsum: "Somma di Riemann",
              sum: "Somma",
              delta: "Delta"
            },
            errors: {
              "cannot-delete-mapping-because-zones-use-it": "Non è possibile eliminare questo gruppo di sensori perché almeno una zona lo utilizza.",
              invalid_source: "Fonte non valida",
              source_does_not_exist: "La fonte non esiste. Inserire una fonte valida, ad esempio 'sensor.mysensor'."
            },
            items: {
              dewpoint: "Punto di rugiada",
              evapotranspiration: "Evapotraspirazione",
              humidity: "Umidità",
              "maximum temperature": "Temperatura massima",
              "minimum temperature": "Temperatura minima",
              precipitation: "Precipitazione",
              "current precipitation": "Precipitazioni attuali",
              pressure: "Pressione",
              "solar radiation": "Irradiamento solare",
              temperature: "Temperatura",
              windspeed: "Velocità del vento"
            },
            pressure_types: {
              absolute: "assoluta",
              relative: "relativa"
            },
            "pressure-type": "La pressione è",
            "sensor-aggregate-of-sensor-values-to-calculate": "dei valori del sensore per calcolare la durata",
            "sensor-aggregate-use-the": "Usa il",
            "sensor-entity": "Entità sensore",
            static_value: "Valore",
            "input-units": "L'input fornisce valori in",
            source: "Fonte",
            sources: {
              none: "Nessuna",
              weather_service: "Servizio meteo",
              sensor: "Sensore",
              static: "Valore statico"
            }
          }
        },
        description: "Aggiungi uno o più gruppi di sensori che recuperano i dati meteorologici da Weather service, da sensori o da una combinazione di questi. È possibile mappare ciascun gruppo di sensori su una o più zone",
        labels: {
          "mapping-name": "Nome"
        },
        no_items: "Non è ancora stato definito alcun gruppo di sensori.",
        title: "Gruppi di sensori",
        "weather-records": {
          title: "Record meteo (ultimi 10)",
          timestamp: "Tempo",
          temperature: "Temp.",
          humidity: "Umidità",
          precipitation: "Precip.",
          "retrieval-time": "Recuperato",
          "no-data": "Non sono disponibili dati meteo per questo gruppo di sensori",
          dewpoint: "Rugiada",
          wind: "Vento",
          pressure: "Press."
        }
      },
      modules: {
        cards: {
          "add-module": {
            actions: {
              add: "Aggiungi modulo"
            },
            header: "Aggiungi modulo"
          },
          module: {
            errors: {
              "cannot-delete-module-because-zones-use-it": "Non puoi eliminare questo modulo perché almeno una zona lo utilizza."
            },
            labels: {
              configuration: "Configurazione",
              required: "indica un campo richiesto"
            },
            "translated-options": {
              DontEstimate: "Non stimare",
              EstimateFromSunHours: "Stima dalle ore solari",
              EstimateFromTemp: "Stima dalla temperatura",
              EstimateFromSunHoursAndTemperature: "Stima dalla media delle ore di sole e della temperatura"
            }
          }
        },
        description: "Aggiungi uno o più moduli che calcolano la durata dell'irrigazione. Ogni modulo viene fornito con la propria configurazione e può essere utilizzato per calcolare la durata di una o più zone.",
        no_items: "Non ci sono ancora moduli definiti.",
        title: "Moduli"
      },
      zones: {
        actions: {
          add: "Aggiungi",
          calculate: "Calcola",
          information: "Informazioni",
          update: "Aggiorna",
          "reset-bucket": "Reimposta il secchio",
          "view-weather-info": "Visualizza dati meteo",
          "view-weather-info-message": "Informazioni meteo disponibili per",
          "view-weather-info-todo": "TODO: Implementare la navigazione ai dettagli del gruppo di sensori",
          "view-watering-calendar": "Calendario irrigazione",
          irrigate_all: "Irriga tutte le zone ora",
          open_settings: "Modifica impostazioni"
        },
        cards: {
          "add-zone": {
            actions: {
              add: "Aggiungi zona"
            },
            header: "Aggiungi zona"
          },
          "zone-actions": {
            actions: {
              "calculate-all": "Ricalcola le durate",
              "update-all": "Aggiorna i dati meteo",
              "reset-all-buckets": "Reimposta tutte le zone",
              "clear-all-weatherdata": "Cancella tutti i dati meteo"
            },
            header: "Azioni su tutte le zone"
          }
        },
        description: "Specificare qui una o più zone di irrigazione. La durata dell'irrigazione viene calcolata per zona, a seconda delle dimensioni, della produttività, dello stato, del modulo e del gruppo di sensori.",
        labels: {
          bucket: "Secchio",
          duration: "Durata",
          "lead-time": "Tempi di esecuzione",
          mapping: "Gruppo di sensori",
          "maximum-duration": "Durata massima",
          multiplier: "Moltiplicatore",
          name: "Nome",
          size: "Misura",
          state: "Stato",
          states: {
            automatic: "Automatico",
            disabled: "Disabilitato",
            manual: "Manuale"
          },
          throughput: "Portata",
          "maximum-bucket": "Secchio massimo",
          last_calculated: "Ultimo calcolo",
          "data-last-updated": "Ultimo aggiornamento dei dati",
          "data-number-of-data-points": "Numero di dati",
          tasso_di_drenaggio: "tasso di drenaggio",
          drainage_rate: "Tasso di drenaggio",
          linked_entity: "Entità interruttore/valvola collegata",
          linked_entity_placeholder: "es. switch.valvola_giardino",
          irrigate_now: "Irriga ora",
          bucket_threshold: "Deficit minimo per irrigare",
          flow_sensor: "Sensore del flussometro (opzionale)",
          flow_sensor_placeholder: "ad es. sensor.zone_flow_rate"
        },
        no_items: "Non ci sono ancora zone definite.",
        title: "Zone",
        confirm_irrigate: {
          title: "Avviare l'irrigazione?",
          body: "Verranno aperte ora le valvole collegate, ignorando tutte le condizioni di esclusione (pioggia, temperatura, giorni minimi tra le irrigazioni).",
          all_linked_zones: "Tutte le zone collegate",
          toast_started: "Irrigazione avviata",
          toast_failed: "Irrigazione non riuscita"
        },
        status: {
          decision_disabled: "Disattivata — questa zona non verrà irrigata automaticamente.",
          decision_water: "Irrigazione necessaria: circa {duration} alla prossima esecuzione programmata.",
          decision_water_at: "Irrigherà circa {duration} alle {time}.",
          decision_water_skip: "Deficit ~{duration}, ma la prossima esecuzione sarà probabilmente saltata ({reason}).",
          decision_water_no_schedule: "Deficit ~{duration} — nessuna pianificazione irriga questa zona; avviala manualmente.",
          decision_no_water: "Nessuna irrigazione necessaria ora — il terreno ha umidità sufficiente.",
          decision_unknown: "Non ancora calcolato — premi Aggiorna, poi Calcola per verificare.",
          last_checked: "Ultimo controllo",
          never: "mai",
          saved: "Salvato",
          estimate_now: "Ora",
          estimate_tag: "stima",
          estimate_method: {
            hourly: "Stima live dai dati meteo orari dall'ultimo calcolo",
            proxy: "Stima distribuita dalla previsione di oggi dall'ultimo calcolo"
          }
        },
        help: {
          bucket: "Bilancio di umidità del suolo (secchio). Un valore negativo significa che il terreno è asciutto e la zona ha bisogno d'acqua.",
          calculate: "Calcola la durata dell'irrigazione dai dati più recenti. Eseguilo dopo Aggiorna.",
          update: "Recupera i dati meteo/sensori più recenti per questa zona.",
          irrigate_link_entity: "Collega un interruttore/una valvola nelle impostazioni di questa zona per abilitare l'irrigazione manuale.",
          irrigate_all: "Apre subito le valvole collegate per ogni zona in deficit. Le condizioni di esclusione (pioggia, vento, temperatura) vengono ignorate.",
          update_all: "Raccoglie i dati meteo/sensori più recenti per tutte le zone. Non modifica da sola le durate.",
          calculate_all: "Ricalcola la durata di irrigazione di ogni zona automatica dai dati raccolti finora."
        },
        outlook: {
          next_run: "Prossima esecuzione",
          no_schedule: "Nessuna pianificazione automatica — le zone si irrigano solo quando le avvii tu.",
          setup_schedule: "Configura una pianificazione",
          targets_all: "tutte le zone",
          targets_zones: "{count} zone",
          will_skip: "La prossima esecuzione sarà probabilmente saltata",
          will_run: "Le condizioni sembrano favorevoli per la prossima esecuzione.",
          why_skipped: "Perché?",
          provisional: "previsione — può cambiare",
          active_guards: "Condizioni attive",
          last_run: "Ultima esecuzione",
          last_run_skipped: "saltata",
          last_run_ran: "eseguita",
          today: "oggi",
          tomorrow: "domani",
          actions: {
            irrigate: "Irriga",
            calculate: "Ricalcola",
            update: "Aggiorna dati"
          },
          checks: {
            precipitation: "Pioggia prevista",
            days_between: "Giorni tra le irrigazioni",
            temperature: "Temperatura bassa",
            wind: "Vento forte",
            rain_sensor: "Sensore di pioggia"
          },
          check_detail: {
            precipitation: "{observed} mm (≥ {threshold} mm)",
            days_between: "{observed}/{threshold} giorni",
            temperature: "{observed}° (sotto {threshold}°)",
            wind: "{observed} (sopra {threshold})",
            rain_sensor: "{observed}"
          }
        },
        calendar: {
          no_data: "Nessun dato del calendario di irrigazione disponibile per questa zona.",
          error_prefix: "Errore nella generazione del calendario:",
          month: "Mese",
          et: "ET (mm)",
          precipitation: "Precipitazioni (mm)",
          watering: "Irrigazione (L)",
          avg_temp: "Temp. media (°C)",
          method_prefix: "Metodo:"
        },
        confirm_action: {
          reset_bucket_title: "Azzerare il secchio di questa zona?",
          reset_bucket_body: "Questo riporta il secchio a 0, scartando il bilancio di umidità accumulato per questa zona.",
          reset_all_buckets_title: "Azzerare tutti i secchi?",
          reset_all_buckets_body: "Questo riporta a 0 il secchio di ogni zona, scartando il bilancio di umidità accumulato. I calcoli di irrigazione ripartiranno dal prossimo aggiornamento.",
          clear_weather_title: "Cancellare tutti i dati meteo?",
          clear_weather_body: "Questo elimina tutti i record meteo e dei sensori di tutte le zone. Le zone avranno bisogno di nuovi dati prima di poter ricalcolare."
        }
      },
      schedules: {
        title: "Pianificazioni",
        description: "Crea pianificazioni ricorrenti per calcolare, aggiornare o irrigare automaticamente — senza automazioni.",
        add: "Aggiungi pianificazione",
        no_items: "Nessuna pianificazione configurata. Fare clic su 'Aggiungi pianificazione'.",
        zones_all: "Tutte le zone",
        zones_specific: "Zone specifiche",
        hours: "ore",
        minutes: "min",
        types: {
          daily: "Giornaliero",
          weekly: "Settimanale",
          monthly: "Mensile",
          interval: "Ogni N ore",
          sunrise: "Alba",
          sunset: "Tramonto",
          solar_azimuth: "Azimut solare"
        },
        actions: {
          calculate: "Calcola (aggiorna durata irrigazione)",
          update: "Aggiorna (raccogliere dati meteo)",
          irrigate: "Irriga (controllare valvole direttamente)"
        },
        days: {
          monday: "Lu",
          tuesday: "Ma",
          wednesday: "Me",
          thursday: "Gi",
          friday: "Ve",
          saturday: "Sa",
          sunday: "Do"
        },
        fields: {
          name: "Nome",
          type: "Tipo di pianificazione",
          enabled: "Abilitato",
          time: "Ora (HH:MM)",
          days_of_week: "Giorni della settimana",
          day_of_month: "Giorno del mese",
          interval_hours: "Intervallo",
          action: "Azione",
          zones: "Zone",
          start_date: "Data di inizio (opzionale)",
          end_date: "Data di fine (opzionale)",
          offset_minutes: "Offset dall'alba/tramonto",
          account_for_duration: "Iniziare prima affinché l'irrigazione finisca all'orario target",
          azimuth_angle: "Angolo di azimut solare",
          time_anchor: "Lorario indica"
        },
        dialog: {
          add_title: "Aggiungi pianificazione",
          edit_title: "Modifica pianificazione"
        },
        time_anchor: {
          start: "Inizio dellirrigazione",
          finish: "Fine dellirrigazione"
        }
      },
      setup: {
        title: "Configurazione"
      }
    },
    Gt = "Smart Irrigation",
    Yt = {
      title: "Coordinate di Posizione",
      description: "Configura le coordinate di posizione per il recupero dei dati meteorologici. Puoi usare coordinate manuali diverse dalla tua posizione Home Assistant se necessario.",
      manual_enabled: "Usa coordinate manuali",
      use_ha_location: "Usa posizione di Home Assistant",
      latitude: "Latitudine (gradi decimali)",
      longitude: "Longitudine (gradi decimali)",
      elevation: "Elevazione (metri sul livello del mare)",
      current_ha_coords: "Coordinate attuali di Home Assistant"
    },
    Kt = {
      title: "Giorni tra irrigazioni",
      description: "Configura il numero minimo di giorni tra gli eventi di irrigazione.",
      label: "Giorni minimi tra irrigazioni",
      help_text: "Impostare 0 per disabilitare. Sono supportati valori da 1 a 365 giorni."
    },
    Jt = {
      title: "Trigger di avvio irrigazione",
      description: "Configura quando deve iniziare l'irrigazione in base agli eventi solari. Puoi aggiungere più trigger per orari diversi. Per i trigger all'alba, lasciando lo scostamento a 0 verrà usata automaticamente la durata totale di tutte le zone abilitate.",
      add_trigger: "Aggiungi trigger",
      edit_trigger: "Modifica trigger",
      delete_trigger: "Elimina trigger",
      trigger_types: {
        sunrise: "Alba",
        sunset: "Tramonto",
        solar_azimuth: "Azimut solare"
      },
      fields: {
        name: {
          name: "Nome del trigger",
          description: "Un nome descrittivo per identificare questo trigger"
        },
        type: {
          name: "Tipo di trigger",
          description: "Il tipo di evento solare su cui attivare"
        },
        enabled: {
          name: "Abilitato",
          description: "Se questo trigger è attualmente attivo"
        },
        offset_minutes: {
          name: "Scostamento (minuti)",
          description: "Minuti prima (-) o dopo (+) l'evento solare. Per i trigger all'alba, usa 0 per una temporizzazione automatica basata sulla durata totale delle zone."
        },
        azimuth_angle: {
          name: "Angolo di azimut (gradi)",
          description: "Angolo di azimut solare in gradi dove 0=Nord, 90=Est, 180=Sud, 270=Ovest"
        },
        account_for_duration: {
          name: "Considera la durata",
          description: "Se abilitato, l'irrigazione inizierà abbastanza presto da terminare all'ora specificata. Se disabilitato, l'irrigazione inizierà esattamente all'ora specificata."
        }
      },
      dialog: {
        add_title: "Aggiungi trigger di avvio irrigazione",
        edit_title: "Modifica trigger di avvio irrigazione",
        cancel: "Annulla",
        save: "Salva",
        delete: "Elimina"
      },
      no_triggers: "Nessun trigger di avvio irrigazione configurato. Il sistema userà il comportamento predefinito (alba con la durata totale delle zone). Aggiungi trigger per personalizzare l'avvio dell'irrigazione.",
      offset_auto: "Automatico (calcolato dalla durata totale delle zone)",
      confirm_delete: "Vuoi davvero eliminare il trigger '{name}'?",
      validation: {
        name_required: "Il nome del trigger è obbligatorio",
        azimuth_invalid: "L'angolo di azimut deve essere un numero valido"
      },
      help: {
        sunrise_offset: "Per i trigger all'alba: usa valori negativi per iniziare prima dell'alba, positivi per iniziare dopo. Imposta 0 per iniziare automaticamente con abbastanza anticipo da completare tutte le zone prima dell'alba.",
        sunset_offset: "Per i trigger al tramonto: usa valori negativi per iniziare prima del tramonto, positivi per iniziare dopo il tramonto.",
        azimuth_explanation: "L'azimut solare è la direzione bussolare del sole. 0°=Nord, 90°=Est, 180°=Sud, 270°=Ovest. Puoi inserire qualsiasi valore di angolo (ad es. 450° = 90°, -30° = 330°). Usalo per attivare l'irrigazione quando il sole raggiunge una posizione specifica.",
        multiple_triggers: "Puoi configurare più trigger. Ogni trigger abilitato pianificherà gli avvii dell'irrigazione in modo indipendente."
      }
    },
    Xt = {
      title: "Condizioni di esclusione",
      description: "Salta automaticamente l'irrigazione quando le condizioni sono sfavorevoli. I controlli di precipitazioni, temperatura e vento richiedono un servizio meteo.",
      threshold_label: "Soglia di precipitazioni",
      threshold_description: "Precipitazione totale minima prevista (in mm) sulla finestra di previsione per saltare l'irrigazione.",
      lookahead_label: "Finestra di previsione (giorni)",
      lookahead_help: "Quanti giorni di previsione futuri sommare nel controllo della pioggia. La previsione parte da domani (oggi è escluso), quindi 1 = solo il giorno successivo, 2 = i prossimi due giorni, e così via.",
      temp_section_title: "Salta per bassa temperatura",
      temp_threshold_label: "Salta se temperatura sotto",
      wind_section_title: "Salta per vento forte",
      wind_threshold_label: "Salta se velocità del vento superiore a",
      rain_sensor_section_title: "Condizione sensore pioggia",
      rain_sensor_label: "Entità sensore pioggia (opzionale)",
      rain_sensor_placeholder: "es. binary_sensor.pioggia"
    },
    Qt = {
      title: "Sequenza zone",
      description: "Quando più zone necessitano di irrigazione, scegliere se funzionano contemporaneamente o una dopo l'altra. In modalità sequenziale, il sistema attende che ogni zona finisca prima di avviare la successiva. In modalità rotante, il sistema alterna tra le zone assegnando a ciascuna un tempo massimo consecutivo prima di passare alla successiva.",
      parallel: "Parallelo (tutte le zone insieme)",
      sequential: "Sequenziale (una zona alla volta)",
      rotating: "Rotante (le zone si alternano)",
      max_consecutive_duration_label: "Tempo massimo consecutivo per zona",
      max_consecutive_duration_unit: "minuti",
      min_absorption_time_label: "Tempo minimo di assorbimento tra slot",
      min_absorption_time_unit: "minuti (0 = disabilitato)"
    },
    ea = {
      title: "Servizio meteo",
      description: "Configura quale servizio meteo usare per i calcoli ET e le condizioni di salto.",
      enabled_label: "Abilita servizio meteo",
      service_label: "Servizio meteo",
      api_key_label: "Chiave API",
      api_key_placeholder: "Lascia vuoto per mantenere la chiave esistente",
      api_key_configured: "La chiave API è configurata",
      api_key_not_configured: "Nessuna chiave API configurata",
      api_key_help: "Una chiave API del provider di servizio meteo scelto. Open-Meteo non richiede una chiave. OpenWeatherMap e Pirate Weather offrono entrambi piani gratuiti.",
      no_api_key_needed: "Open-Meteo è un servizio gratuito e non richiede una chiave API.",
      save_button: "Salva impostazioni meteo",
      saved: "Impostazioni meteo salvate",
      openmeteo: "Open-Meteo (gratuito, senza chiave)",
      test_button: "Prova connessione",
      test_button_testing: "Test in corso…",
      test_success: "✓ Connessione riuscita",
      test_error_invalid_auth: "✗ Chiave API non valida — verifica che sia corretta e attiva",
      test_error_cannot_connect: "✗ Impossibile connettersi — controlla la connessione internet",
      test_error_no_service: "✗ Seleziona prima un servizio meteo",
      test_error_unknown: "✗ Test fallito — errore sconosciuto",
      owm: "OpenWeatherMap",
      pw: "Pirate Weather"
    },
    ta = {
      zone_size: "L'area irrigata totale di questa zona. Usata con la portata per calcolare quanta acqua viene erogata per ciclo.",
      zone_throughput: "Flusso d'acqua totale del tuo impianto di irrigazione per questa zona (litri/min in metrico, gal/min in imperiale). Controlla la scheda tecnica degli irrigatori o misura cronometrando quanto tempo serve a riempire un contenitore di volume noto.",
      zone_drainage_rate: "La velocità con cui l'acqua in eccesso drena dal terreno quando il secchio è pieno. Tipico: prato 50 mm/h, terreno sabbioso 100+ mm/h, argilla 10 mm/h.",
      zone_bucket: "Deficit (negativo) o surplus (positivo) idrico attuale di questa zona. L'irrigazione si attiva quando il secchio scende sotto la soglia.",
      zone_maximum_bucket: "Surplus di umidità massimo che la zona può trattenere. L'acqua oltre questo livello è trattata come deflusso. Valore tipico: 50 mm.",
      zone_bucket_threshold: "L'irrigazione si attiva quando il secchio scende sotto questo valore. Deve essere 0 o negativo. 0 significa irrigare ogni volta che c'è un deficit.",
      zone_multiplier: "Fattore di scala applicato alla durata calcolata. Sopra 1,0 aumenta, sotto 1,0 diminuisce. Utile per la messa a punto senza modificare le misure fisiche.",
      zone_lead_time: "Secondi aggiuntivi prima dell'avvio dell'irrigazione. Usali per il riscaldamento della pompa o la pressurizzazione dell'impianto.",
      zone_maximum_duration: "Limite massimo assoluto per un singolo ciclo di irrigazione in secondi. Previene irrigazioni incontrollate. Predefinito: 3600 s (1 ora).",
      zone_linked_entity: "L'entità interruttore o valvola di HA che controlla il flusso d'acqua per questa zona. Questa entità viene attivata quando l'irrigazione è in funzione.",
      zone_flow_sensor: "Sensore opzionale che misura la portata d'acqua effettiva. Usato solo per i report — non influisce sul calcolo della durata.",
      general_autoupdatedelay: "Secondi di attesa dopo l'avvio di HA prima del primo recupero dei dati meteo. Consente alle altre integrazioni di inizializzarsi prima.",
      general_sensor_debounce: "Intervallo minimo in millisecondi tra le letture del sensore per filtrare il rumore dei sensori che cambiano rapidamente.",
      general_calctime: "Ora del giorno in cui le durate di irrigazione vengono ricalcolate dai dati meteo raccolti. Formato: HH:MM (24 ore).",
      general_cleardatatime: "Ora del giorno in cui i vecchi dati meteo vengono eliminati. Deve essere impostata dopo l'ora di calcolo.",
      general_days_between: "Giorni minimi tra gli eventi di irrigazione per la stessa zona. Imposta 0 per disabilitare (irrigare ogni volta che c'è un deficit).",
      general_autoupdateinterval: "Con quale frequenza vengono raccolti i dati meteo. Scegli un valore che bilanci dati aggiornati e limiti dell'API.",
      general_precipitation_threshold: "L'irrigazione viene saltata se le precipitazioni totali previste sulla finestra di previsione superano questa quantità.",
      general_temp_threshold: "L'irrigazione viene saltata se la temperatura attuale è inferiore a questo valore (ad es. per prevenire danni da gelo).",
      general_wind_threshold: "L'irrigazione viene saltata se la velocità del vento supera questo valore (il vento forte riduce l'efficienza e causa deriva)."
    },
    aa = {
      title: "Configurazione guidata",
      open_button: "Configurazione guidata",
      close: "Chiudi",
      next: "Avanti",
      back: "Indietro",
      finish: "Fine",
      skip_step: "Salta questo passaggio",
      step_indicator: "Passaggio {current} di {total}",
      setup_complete_banner: "Configurazione non completata. Avvia la procedura guidata per iniziare.",
      open_wizard: "Apri procedura guidata",
      steps: {
        welcome: {
          title: "Benvenuto in Smart Irrigation",
          intro: "Questa procedura guidata ti accompagna nei quattro passaggi necessari per far irrigare automaticamente la tua prima zona.",
          step1_label: "Servizio meteo — dove ottenere i dati meteo",
          step2_label: "Modulo di calcolo — come viene calcolata la durata dell'irrigazione",
          step3_label: "Gruppo di sensori — quali fonti di dati usare",
          step4_label: "Zona — la tua prima zona di irrigazione",
          tip: "Puoi saltare qualsiasi passaggio e configurarlo in seguito dalla scheda Configurazione."
        },
        weather: {
          title: "Servizio meteo",
          description: "Scegli come ottenere i dati meteo. Open-Meteo è gratuito e non richiede una chiave API — è la scelta più semplice per la maggior parte degli utenti."
        },
        module: {
          title: "Modulo di calcolo",
          description: "Un modulo calcola quanto irrigare in base all'evapotraspirazione (ET). Il modulo PyETO (metodo FAO-56) è consigliato per la maggior parte degli utenti.",
          pick_label: "Seleziona il tipo di modulo",
          no_modules: "Nessun tipo di modulo disponibile."
        },
        mapping: {
          title: "Gruppo di sensori",
          description: "Un gruppo di sensori collega ogni variabile meteo a una fonte di dati. Imposta le variabili chiave qui sotto — potrai perfezionare le singole associazioni dei sensori in seguito dalla scheda Configurazione → Gruppi di sensori.",
          name_label: "Nome del gruppo di sensori",
          source_label: "Fonte di dati per",
          use_weather_service: "Servizio meteo",
          use_sensor: "Sensore",
          use_static: "Valore statico",
          use_none: "Nessuna / non usata"
        },
        zone: {
          title: "Prima zona",
          description: "Una zona è un'area di irrigazione (ad es. prato, aiuola). Imposta le proprietà fisiche affinché il sistema possa calcolare la durata di irrigazione corretta.",
          name_label: "Nome della zona",
          size_label: "Area",
          throughput_label: "Portata dell'irrigatore",
          entity_label: "Interruttore o valvola collegati",
          entity_placeholder: "ad es. switch.garden_valve",
          module_label: "Modulo di calcolo",
          mapping_label: "Gruppo di sensori"
        },
        done: {
          title: "Configurazione completata!",
          description: "La tua prima zona è pronta. Smart Irrigation calcolerà ora le durate di irrigazione automaticamente in base ai dati meteo.",
          next_steps: "Cosa puoi fare ora:",
          tip1: "Vai su Zone per vedere le durate calcolate e i valori del secchio.",
          tip2: "Aggiungi altre zone dalla scheda Zone.",
          tip3: "Perfeziona tutte le impostazioni dalla scheda Configurazione.",
          go_zones: "Vai a Zone",
          go_setup: "Vai a Configurazione"
        }
      },
      stepper: {
        weather: "Meteo",
        module: "Modulo",
        mapping: "Gruppo di sensori",
        zone: "Zona"
      },
      confirm_close: {
        body: "Chiudere la procedura guidata? I progressi finora sono salvati.",
        keep: "Continua",
        close: "Chiudi"
      }
    },
    ia = {
      common: Vt,
      defaults: Wt,
      module: Ft,
      calcmodules: qt,
      panels: Zt,
      title: Gt,
      coordinate_config: Yt,
      days_between_irrigation: Kt,
      irrigation_start_triggers: Jt,
      weather_skip: Xt,
      zone_sequencing: Qt,
      weather_service_config: ea,
      field_help: ta,
      wizard: aa
    },
    na = Object.freeze({
      __proto__: null,
      common: Vt,
      defaults: Wt,
      module: Ft,
      calcmodules: qt,
      panels: Zt,
      title: Gt,
      coordinate_config: Yt,
      days_between_irrigation: Kt,
      irrigation_start_triggers: Jt,
      weather_skip: Xt,
      zone_sequencing: Qt,
      weather_service_config: ea,
      field_help: ta,
      wizard: aa,
      default: ia
    }),
    ra = {
      actions: {
        delete: "Verwijderen",
        edit: "Bewerken",
        save: "Opslaan",
        cancel: "Annuleren",
        confirm_delete: "Verwijderen bevestigen",
        confirm_delete_zone: "Weet je zeker dat je deze zone wilt verwijderen?"
      },
      labels: {
        module: "Module",
        no: "Nee",
        select: "Kies",
        yes: "Ja",
        enabled: "Ingeschakeld",
        disabled: "Uitgeschakeld",
        before: "voor",
        after: "na",
        settings: "Instellingen",
        bulk_actions: "Bulkacties"
      },
      attributes: {
        size: "afmeting",
        throughput: "doorvoer",
        state: "status",
        bucket: "emmer",
        last_updated: "laatste update",
        last_calculated: "laatste berekening",
        number_of_data_points: "aantal datapunten"
      },
      loading: "Laden",
      saving: "Opslaan",
      units: {
        seconds: "seconden"
      },
      "loading-messages": {
        configuration: "Configuratie laden...",
        modules: "Modules laden...",
        general: "Laden..."
      },
      "saving-messages": {
        adding: "Toevoegen...",
        saving: "Opslaan..."
      },
      errors: {
        load_failed: "Kan gegevens niet laden",
        save_failed: "Kan wijzigingen niet opslaan",
        delete_failed: "Kan niet verwijderen",
        action_failed: "Actie mislukt"
      }
    },
    oa = {
      "default-zone": "Standaard zone",
      "default-mapping": "Standaard sensorgroep"
    },
    sa = {
      calculation: {
        explanation: {
          "module-returned-evapotranspiration-deficiency": "NB: in deze uitleg wordt de '.' as decimaalscheidingsteken gebruikt, worden afgeronde en metrische getallen getoond. Module berekende ET waarde van",
          "bucket-was": "Voorraad was",
          "new-bucket-values-is": "Nieuwe voorraad is",
          "old-bucket-variable": "oude_voorraad",
          delta: "verandering",
          "bucket-less-than-zero-irrigation-necessary": "Omdat de voorraad < 0 is, is irrigatie nodig",
          "steps-taken-to-calculate-duration": "On de exacte duur te berekenen werd het volgende gedaan",
          "precipitation-rate-defined-as": "De neerslag is",
          "duration-is-calculated-as": "De duur is",
          bucket: "voorraad",
          "precipitation-rate-variable": "neerslag",
          "multiplier-is-applied": "De vermenigvuldiger wordt toegepast. Deze is",
          "duration-after-multiplier-is": "dus de duur is",
          "maximum-duration-is-applied": "De maximum duur wordt toegepast. Deze is",
          "duration-after-maximum-duration-is": "dus de duur is",
          "lead-time-is-applied": "As laatste wordt de aanlooptijd toegepast. Deze is",
          "duration-after-lead-time-is": "dus de uiteindelijke duur is",
          "bucket-larger-than-or-equal-to-zero-no-irrigation-necessary": "Omdat de voorraad >= 0 is er geen irrigatie nodig en is de duur gelijk aan",
          "maximum-bucket-is": "maximale voorraad grootte is",
          "max-bucket-variable": "max_bucket",
          drainage: "afwatering",
          "drainage-rate": "afwateringssnelheid",
          hours: "uren",
          "drainage-rate-is": "Drainagesnelheid bij verzadiging (emmer op maximum) is",
          "current-drainage-is": "Huidige drainage berekend als",
          "no-drainage": "Huidige drainage is 0 omdat"
        }
      }
    },
    la = {
      pyeto: {
        description: "Bereken duur op basis van de FAU56 formule en de PyETO library"
      },
      static: {
        description: "Module met instelbare verandering"
      },
      passthrough: {
        description: "Geeft waarde van ET sensor as verandering terug"
      }
    },
    da = {
      general: {
        cards: {
          "automatic-duration-calculation": {
            header: "Automatische berekening van irrigatietijd",
            description: "Bij het berekenen wordt de verzamelde weersinformatie gebruikt om the voorraad en irrigatieduur per zone aan te passen. Daarna wordt de verzamelde weersinformatie verwijderd.",
            labels: {
              "auto-calc-enabled": "Automatisch irrigatietijd berekening voor elke zone",
              "auto-calc-time": "Berekenen op",
              "calc-time": "Berekenen om"
            }
          },
          "automatic-update": {
            errors: {
              "warning-update-time-on-or-after-calc-time": "Let op: het automatisch bijwerken van weersinformatie vind plaats op of na de automatische berekening van irrigatietijd"
            },
            header: "Automatisch bijwerken van weersinformatie",
            description: "Verzamel en bewaar weersinformatie automatisch. Weersinformatie is nodig om vorraad en irrigatieduur per zone te berekenen.",
            labels: {
              "auto-update-enabled": "Automatisch weersinformatie bijwerken",
              "auto-update-delay": "Vertraging",
              "auto-update-interval": "Sensor data bijwerken elke",
              "auto-update-schedule": "Updateschema",
              "auto-update-time": "Bijwerken om"
            },
            options: {
              days: "dagen",
              hours: "uren",
              minutes: "minuten"
            }
          },
          "automatic-clear": {
            header: "Automatisch weersinformatie opruimen",
            description: "Verwijder weersinformatie op het ingestelde moment. Dit zorgt ervoor dat er geen weersinformatie van de vorige dag gebruikt kan worden voor berekeningen. Let op: verwijder geen weersinformatie voordat de berekening heeft plaatsgevonden. Gebruik deze optie als je verwacht dat er weersinformatie zal worden verzameld nadat de berekeningen voor de dag gedaan zijn. Verwijder weersinformatie zo laat mogelijk op de dag.",
            labels: {
              "automatic-clear-enabled": "Automatisch weersinformatie verwijderen",
              "automatic-clear-time": "Verwijder weersinformatie om"
            }
          },
          continuousupdates: {
            header: "Continue sensorupdates (experimenteel)",
            description: "Experimentele functie voor gedetailleerdere weergegevens.",
            labels: {
              continuousupdates: "Continue updates inschakelen",
              sensor_debounce: "Sensor-debounce",
              "sensor-debounce": "Sensor-debouncetijd (ms)"
            }
          }
        },
        description: "Dit zijn de algemene instellingen.",
        title: "Algemeen",
        sections: {
          weather: "Weer",
          automation: "Automatisering",
          location: "Locatie",
          watering: "Bewateringsgedrag"
        }
      },
      help: {
        title: "Hulp",
        cards: {
          "how-to-get-help": {
            title: "Hulp vragen",
            "first-read-the": "Allereerst, lees de",
            wiki: "Documentatie",
            "if-you-still-need-help": "Als je hierna nog steeds hulp nodig hebt, laat een bericht achter op het",
            "community-forum": "Communityforum",
            "or-open-a": "of open een",
            "github-issue": "GitHub-issue",
            "english-only": "alleen Engels"
          }
        }
      },
      mappings: {
        cards: {
          "add-mapping": {
            actions: {
              add: "Toevoegen"
            },
            header: "Voeg sensorgroep toe"
          },
          mapping: {
            aggregates: {
              average: "Gemiddelde",
              first: "Eerste",
              last: "Laatste",
              maximum: "Maximum",
              median: "Mediaan",
              minimum: "Minimum",
              sum: "Totaal",
              riemannsum: "Riemann-som",
              delta: "Delta"
            },
            errors: {
              "cannot-delete-mapping-because-zones-use-it": "Deze sensorgroep kan niet worden verwijderd omdat er minimaal een zone gebruik van maakt.",
              invalid_source: "Ongeldige bron",
              source_does_not_exist: "Bron bestaat niet. Voer een geldige bron in, zoals 'sensor.mysensor'."
            },
            items: {
              dewpoint: "Dauwpunt",
              evapotranspiration: "Verdamping",
              humidity: "Vochtigheid",
              "maximum temperature": "Maximum temperatuur",
              "minimum temperature": "Minimum temperatuur",
              precipitation: "Totale neerslag",
              pressure: "Druk",
              "solar radiation": "Zonnestraling",
              temperature: "Temperatuur",
              windspeed: "Wind snelheid",
              "current precipitation": "Huidige neerslag"
            },
            pressure_types: {
              absolute: "absoluut",
              relative: "relatief"
            },
            "pressure-type": "Druk is",
            "sensor-aggregate-of-sensor-values-to-calculate": "van de sensor waardes om irrigatietijd te berekenen",
            "sensor-aggregate-use-the": "Gebruik de/het",
            "sensor-entity": "Sensor entiteit",
            "input-units": "Invoer geeft waardes in",
            static_value: "Waarde",
            source: "Bron",
            sources: {
              none: "Geen",
              weather_service: "Weerdienst",
              sensor: "Sensor",
              static: "Vaste waarde"
            }
          }
        },
        description: "Voeg een of meer sensorgroepen toe die weergegevens ophalen van Weather service, van sensoren of een combinatie. Elke sensorgroep kan worden gebruikt voor een of meerdere zones",
        labels: {
          "mapping-name": "Naam"
        },
        no_items: "Er zijn nog geen sensorgroepen.",
        title: "Sensorgroepen",
        "weather-records": {
          title: "Weerregistraties",
          timestamp: "Tijd",
          temperature: "Temp.",
          humidity: "Humidity",
          precipitation: "Neersl.",
          "retrieval-time": "Opgehaald",
          "no-data": "Geen weergegevens beschikbaar voor deze sensorgroep",
          dewpoint: "Dauw",
          wind: "Wind",
          pressure: "Druk"
        }
      },
      modules: {
        cards: {
          "add-module": {
            actions: {
              add: "Toevoegen"
            },
            header: "Voeg module toe"
          },
          module: {
            errors: {
              "cannot-delete-module-because-zones-use-it": "Deze module kan niet worden verwijderd omdat er minimaal een zone gebruik van maakt."
            },
            labels: {
              configuration: "Instellingen",
              required: "verplicht veld"
            },
            "translated-options": {
              DontEstimate: "Niet berekenen",
              EstimateFromSunHours: "Gebaseerd op zon uren",
              EstimateFromTemp: "Gebaseerd op temperatuur",
              EstimateFromSunHoursAndTemperature: "Schatten op basis van het gemiddelde van zonuren en temperatuur"
            }
          }
        },
        description: "Voeg een of meerdere modules toe. Modules berekenen irrigatietijd. Elke module heeft zijn eigen configuratie and kan worden gebruikt voor het berekening van irrigatietijd voor een of meerdere zones.",
        no_items: "Er zijn nog geen modules.",
        title: "Modules"
      },
      zones: {
        actions: {
          add: "Toevoegen",
          calculate: "Bereken",
          information: "Informatie",
          update: "Bijwerken",
          "reset-bucket": "Leeg voorraad",
          "view-weather-info": "Weergegevens bekijken",
          "view-weather-info-message": "Weergegevens beschikbaar voor",
          "view-watering-calendar": "Bewateringskalender",
          irrigate_all: "Alle zones nu bewateren",
          open_settings: "Instellingen bewerken"
        },
        cards: {
          "add-zone": {
            actions: {
              add: "Toevoegen"
            },
            header: "Voeg zone toe"
          },
          "zone-actions": {
            actions: {
              "calculate-all": "Duur herberekenen",
              "update-all": "Weergegevens vernieuwen",
              "reset-all-buckets": "Leeg alle voorraden",
              "clear-all-weatherdata": "Verwijder alle weersinformatie"
            },
            header: "Acties voor alle zones"
          }
        },
        description: "Voeg een of meerdere zones toe. Per zone wordt de irrigatietijd berekend, afhankelijk van de afmeting, doorvoer, status, module en sensorgroep.",
        labels: {
          bucket: "Voorraad",
          duration: "Irrigatieduur",
          "lead-time": "Aanlooptijd",
          mapping: "Sensorgroep",
          "maximum-duration": "Maximale duur",
          multiplier: "Vermenigvuldiger",
          name: "Naam",
          size: "Afmeting",
          state: "Status",
          states: {
            automatic: "Automatisch",
            disabled: "Uit",
            manual: "Manueel"
          },
          throughput: "Doorvoer",
          "maximum-bucket": "Maximale voorraad",
          last_calculated: "Berekend op",
          "data-last-updated": "Bijgewerkt op",
          "data-number-of-data-points": "Aantal datapunten",
          drainage_rate: "Afwateringssnelheid",
          linked_entity: "Gekoppelde schakelaar/klep-entiteit",
          linked_entity_placeholder: "bijv. switch.tuin_klep",
          irrigate_now: "Nu bewateren",
          bucket_threshold: "Minimum tekort voor bewatering",
          flow_sensor: "Doorstroommeter-sensor (optioneel)",
          flow_sensor_placeholder: "bijv. sensor.zone_flow_rate"
        },
        no_items: "Er zijn nog geen zones.",
        title: "Zones",
        confirm_irrigate: {
          title: "Irrigatie starten?",
          body: "Dit opent nu de gekoppelde klep(pen) en negeert alle uitsluitingsvoorwaarden (regen, temperatuur, minimaal aantal dagen tussen beurten).",
          all_linked_zones: "Alle gekoppelde zones",
          toast_started: "Irrigatie gestart",
          toast_failed: "Irrigatie mislukt"
        },
        status: {
          decision_disabled: "Uitgeschakeld — deze zone wordt niet automatisch bewaterd.",
          decision_water: "Bewatering nodig: ongeveer {duration} bij de volgende geplande beurt.",
          decision_water_at: "Bewatert ongeveer {duration} om {time}.",
          decision_water_skip: "Tekort ~{duration}, maar de volgende beurt wordt waarschijnlijk overgeslagen ({reason}).",
          decision_water_no_schedule: "Tekort ~{duration} — geen schema bewatert deze zone; start handmatig.",
          decision_no_water: "Nu geen bewatering nodig — de bodem heeft genoeg vocht.",
          decision_unknown: "Nog niet berekend — druk op Bijwerken en daarna Bereken om te controleren.",
          last_checked: "Laatst gecontroleerd",
          never: "nooit",
          saved: "Opgeslagen",
          estimate_now: "Nu",
          estimate_tag: "schat.",
          estimate_method: {
            hourly: "Live schatting op basis van uurlijks weer sinds de laatste berekening",
            proxy: "Schatting verdeeld op basis van de verwachting van vandaag sinds de laatste berekening"
          }
        },
        help: {
          bucket: "Bodemvochtbalans (voorraad). Een negatieve waarde betekent dat de bodem droog is en de zone water nodig heeft.",
          calculate: "Berekent op basis van de nieuwste gegevens hoe lang er bewaterd wordt. Voer dit uit na Bijwerken.",
          update: "Haalt de nieuwste weer-/sensorgegevens voor deze zone op.",
          irrigate_link_entity: "Koppel een schakelaar/klep in de instellingen van deze zone om handmatig bewateren mogelijk te maken.",
          irrigate_all: "Opent nu de gekoppelde kleppen voor elke zone met een tekort. Uitsluitingsvoorwaarden (regen, wind, temperatuur) worden genegeerd.",
          update_all: "Verzamelt de nieuwste weer-/sensorgegevens voor alle zones. Verandert op zichzelf de duur niet.",
          calculate_all: "Herberekent de bewateringsduur van elke automatische zone op basis van de tot nu toe verzamelde gegevens."
        },
        outlook: {
          next_run: "Volgende beurt",
          no_schedule: "Geen automatisch schema — zones worden alleen bewaterd wanneer je ze handmatig start.",
          setup_schedule: "Een schema instellen",
          targets_all: "alle zones",
          targets_zones: "{count} zones",
          will_skip: "Volgende beurt wordt waarschijnlijk overgeslagen",
          will_run: "De omstandigheden lijken gunstig voor de volgende beurt.",
          why_skipped: "Waarom?",
          provisional: "voorspelling — kan veranderen",
          active_guards: "Actieve voorwaarden",
          last_run: "Laatste beurt",
          last_run_skipped: "overgeslagen",
          last_run_ran: "uitgevoerd",
          today: "vandaag",
          tomorrow: "morgen",
          actions: {
            irrigate: "Bewateren",
            calculate: "Herberekenen",
            update: "Gegevens vernieuwen"
          },
          checks: {
            precipitation: "Regenverwachting",
            days_between: "Dagen tussen beurten",
            temperature: "Lage temperatuur",
            wind: "Harde wind",
            rain_sensor: "Regensensor"
          },
          check_detail: {
            precipitation: "{observed} mm (≥ {threshold} mm)",
            days_between: "{observed}/{threshold} dagen",
            temperature: "{observed}° (onder {threshold}°)",
            wind: "{observed} (boven {threshold})",
            rain_sensor: "{observed}"
          }
        },
        calendar: {
          no_data: "Geen bewateringskalendergegevens beschikbaar voor deze zone.",
          error_prefix: "Fout bij het genereren van de kalender:",
          month: "Maand",
          et: "ET (mm)",
          precipitation: "Neerslag (mm)",
          watering: "Bewatering (L)",
          avg_temp: "Gem. temp. (°C)",
          method_prefix: "Methode:"
        },
        confirm_action: {
          reset_bucket_title: "Voorraad van deze zone resetten?",
          reset_bucket_body: "Dit zet de voorraad terug op 0 en verwijdert de opgebouwde vochtbalans voor deze zone.",
          reset_all_buckets_title: "Alle voorraden resetten?",
          reset_all_buckets_body: "Dit zet de voorraad van elke zone terug op 0 en verwijdert de opgebouwde vochtbalans. De bewateringsberekening begint opnieuw bij de volgende update.",
          clear_weather_title: "Alle weergegevens wissen?",
          clear_weather_body: "Dit verwijdert alle verzamelde weer- en sensorgegevens van alle zones. De zones hebben nieuwe gegevens nodig voordat ze opnieuw kunnen berekenen."
        }
      },
      schedules: {
        title: "Schema's",
        description: "Maak terugkerende schema's voor automatisch berekenen, bijwerken of bewateren — zonder automatiseringen.",
        add: "Schema toevoegen",
        no_items: "Nog geen schema's geconfigureerd. Klik op 'Schema toevoegen'.",
        zones_all: "Alle zones",
        zones_specific: "Specifieke zones",
        hours: "uur",
        minutes: "min",
        types: {
          daily: "Dagelijks",
          weekly: "Wekelijks",
          monthly: "Maandelijks",
          interval: "Elke N uur",
          sunrise: "Zonsopgang",
          sunset: "Zonsondergang",
          solar_azimuth: "Zonneazimut"
        },
        actions: {
          calculate: "Berekenen (bewateringsduur bijwerken)",
          update: "Bijwerken (weergegevens verzamelen)",
          irrigate: "Bewateren (kleppen direct aansturen)"
        },
        days: {
          monday: "Ma",
          tuesday: "Di",
          wednesday: "Wo",
          thursday: "Do",
          friday: "Vr",
          saturday: "Za",
          sunday: "Zo"
        },
        fields: {
          name: "Naam",
          type: "Schematype",
          enabled: "Ingeschakeld",
          time: "Tijd (HH:MM)",
          days_of_week: "Weekdagen",
          day_of_month: "Dag van de maand",
          interval_hours: "Interval",
          action: "Actie",
          zones: "Zones",
          start_date: "Startdatum (optioneel)",
          end_date: "Einddatum (optioneel)",
          offset_minutes: "Offset van zonsopgang/-ondergang",
          account_for_duration: "Vroeg starten zodat bewatering eindigt op doeltijd",
          azimuth_angle: "Zonneazimuthoek",
          time_anchor: "Tijd markeert het"
        },
        dialog: {
          add_title: "Schema toevoegen",
          edit_title: "Schema bewerken"
        },
        time_anchor: {
          start: "Begin van de bewatering",
          finish: "Einde van de bewatering"
        }
      },
      info: {
        title: "Info",
        description: "Informatie bekijken over de volgende bewatering en systeemstatus.",
        "configuration-not-available": "Configuratie niet beschikbaar.",
        cards: {
          "zone-bucket-values": {
            title: "Zone-emmerwaarden & duur",
            labels: {
              bucket: "Emmer",
              duration: "Duur"
            },
            "no-zones": "Geen zones geconfigureerd"
          },
          "next-irrigation": {
            title: "Volgende bewatering",
            labels: {
              "next-start": "Volgende start",
              duration: "Duur",
              zones: "Zones"
            },
            "no-data": "Geen gegevens beschikbaar"
          },
          "irrigation-reason": {
            title: "Reden voor bewatering",
            labels: {
              reason: "Reden",
              sunrise: "Zonsopgang",
              "total-duration": "Totale duur",
              explanation: "Uitleg"
            },
            "no-data": "Geen gegevens beschikbaar"
          },
          irrigate_now: {
            title: "Nu bewateren",
            description: "Start direct bewatering voor alle zones met een gekoppelde entiteit. Overslaanvoorwaarden worden genegeerd.",
            button_all: "Alle zones nu starten",
            no_linked_zones: "Geen zones hebben een gekoppelde schakelaar/klep-entiteit met berekende duur."
          }
        }
      },
      setup: {
        title: "Instellen"
      }
    },
    ua = "Smart Irrigation",
    ca = {
      title: "Locatie Coördinaten",
      description: "Configureer locatie coördinaten voor het ophalen van weergegevens. Je kunt handmatige coördinaten gebruiken die verschillen van je Home Assistant locatie indien nodig.",
      manual_enabled: "Handmatige coördinaten gebruiken",
      use_ha_location: "Home Assistant locatie gebruiken",
      latitude: "Breedtegraad (decimale graden)",
      longitude: "Lengtegraad (decimale graden)",
      elevation: "Hoogte (meters boven zeeniveau)",
      current_ha_coords: "Huidige Home Assistant coördinaten"
    },
    pa = {
      title: "Dagen tussen bewatering",
      description: "Stel het minimum aantal dagen in tussen bewateringsgebeurtenissen.",
      label: "Minimum dagen tussen bewatering",
      help_text: "Stel in op 0 om uit te schakelen. Waarden van 1-365 dagen worden ondersteund."
    },
    ma = {
      title: "Irrigatiestart-triggers",
      description: "Configureer wanneer de irrigatie moet starten op basis van zonne-evenementen. Je kunt meerdere triggers toevoegen voor verschillende schema's. Voor zonsopkomst-triggers gebruikt een offset van 0 automatisch de totale duur van alle ingeschakelde zones.",
      add_trigger: "Trigger toevoegen",
      edit_trigger: "Trigger bewerken",
      delete_trigger: "Trigger verwijderen",
      trigger_types: {
        sunrise: "Zonsopkomst",
        sunset: "Zonsondergang",
        solar_azimuth: "Zonsazimut"
      },
      fields: {
        name: {
          name: "Triggernaam",
          description: "Een beschrijvende naam om deze trigger te identificeren"
        },
        type: {
          name: "Triggertype",
          description: "Het type zonne-evenement om op te triggeren"
        },
        enabled: {
          name: "Ingeschakeld",
          description: "Of deze trigger momenteel actief is"
        },
        offset_minutes: {
          name: "Offset (minuten)",
          description: "Minuten voor (-) of na (+) het zonne-evenement. Gebruik voor zonsopkomst-triggers 0 voor automatische timing op basis van de totale zoneduur."
        },
        azimuth_angle: {
          name: "Azimuthoek (graden)",
          description: "Zonsazimuthoek in graden waarbij 0=Noord, 90=Oost, 180=Zuid, 270=West"
        },
        account_for_duration: {
          name: "Rekening houden met duur",
          description: "Indien ingeschakeld start de irrigatie vroeg genoeg om op het opgegeven tijdstip klaar te zijn. Indien uitgeschakeld start de irrigatie precies op het opgegeven tijdstip."
        }
      },
      dialog: {
        add_title: "Irrigatiestart-trigger toevoegen",
        edit_title: "Irrigatiestart-trigger bewerken",
        cancel: "Annuleren",
        save: "Opslaan",
        delete: "Verwijderen"
      },
      no_triggers: "Geen irrigatiestart-triggers geconfigureerd. Het systeem gebruikt het standaardgedrag (zonsopkomst met de totale zoneduur). Voeg triggers toe om aan te passen wanneer de irrigatie start.",
      offset_auto: "Automatisch (berekend uit de totale zoneduur)",
      confirm_delete: "Weet je zeker dat je de trigger '{name}' wilt verwijderen?",
      validation: {
        name_required: "Triggernaam is verplicht",
        azimuth_invalid: "De azimuthoek moet een geldig getal zijn"
      },
      help: {
        sunrise_offset: "Voor zonsopkomst-triggers: gebruik negatieve waarden om vóór zonsopkomst te starten, positieve om erna te starten. Zet op 0 om automatisch vroeg genoeg te starten om alle zones vóór zonsopkomst te voltooien.",
        sunset_offset: "Voor zonsondergang-triggers: gebruik negatieve waarden om vóór zonsondergang te starten, positieve om na zonsondergang te starten.",
        azimuth_explanation: "De zonsazimut is de kompasrichting van de zon. 0°=Noord, 90°=Oost, 180°=Zuid, 270°=West. Je kunt elke hoekwaarde invoeren (bijv. 450° = 90°, -30° = 330°). Gebruik dit om de irrigatie te triggeren wanneer de zon een specifieke positie bereikt.",
        multiple_triggers: "Je kunt meerdere triggers configureren. Elke ingeschakelde trigger plant irrigatiestarts onafhankelijk."
      }
    },
    ha = {
      title: "Overslaanvoorwaarden",
      description: "Sla irrigatie automatisch over als de omstandigheden ongunstig zijn. Neerslag-, temperatuur- en windcontroles vereisen een weerdienst.",
      threshold_label: "Neerslagdrempel",
      threshold_description: "Minimale totale verwachte neerslag (in mm) over het vooruitblik-venster om irrigatie over te slaan.",
      lookahead_label: "Vooruitblik (dagen)",
      lookahead_help: "Hoeveel komende verwachtingsdagen worden opgeteld bij de regencontrole. De verwachting begint morgen (vandaag wordt uitgesloten), dus 1 = alleen de volgende dag, 2 = de volgende twee dagen, enzovoort.",
      temp_section_title: "Overslaan bij lage temperatuur",
      temp_threshold_label: "Overslaan als temperatuur onder",
      wind_section_title: "Overslaan bij hoge windsnelheid",
      wind_threshold_label: "Overslaan als windsnelheid boven",
      rain_sensor_section_title: "Regensensorvoorwaarde",
      rain_sensor_label: "Regensensor-entiteit (optioneel)",
      rain_sensor_placeholder: "bijv. binary_sensor.regen"
    },
    ga = {
      title: "Zone-volgorde",
      description: "Als meerdere zones irrigatie nodig hebben, kies of ze tegelijkertijd of na elkaar worden uitgevoerd. In sequentiële modus wacht het systeem tot elke zone klaar is voordat de volgende start.",
      parallel: "Parallel (alle zones tegelijk)",
      sequential: "Sequentieel (één zone tegelijk)",
      rotating: "Roterend (zones wisselen elkaar af)",
      max_consecutive_duration_label: "Max. aaneengesloten looptijd per zone",
      max_consecutive_duration_unit: "minuten",
      min_absorption_time_label: "Min. absorptietijd tussen runs",
      min_absorption_time_unit: "minuten (0 = uitgeschakeld)"
    },
    va = {
      title: "Weerdienst",
      description: "Configureer welke weerdienst gebruikt wordt voor ET-berekeningen en overslaan-voorwaarden.",
      enabled_label: "Weerdienst inschakelen",
      service_label: "Weerdienst",
      api_key_label: "API-sleutel",
      api_key_placeholder: "Laat leeg om de bestaande sleutel te behouden",
      api_key_configured: "API-sleutel is geconfigureerd",
      api_key_not_configured: "Geen API-sleutel geconfigureerd",
      api_key_help: "Een API-sleutel van je gekozen weerdienstaanbieder. Open-Meteo vereist geen sleutel. OpenWeatherMap en Pirate Weather bieden beide gratis niveaus.",
      no_api_key_needed: "Open-Meteo is een gratis dienst en vereist geen API-sleutel.",
      save_button: "Weerinstellingen opslaan",
      saved: "Weerinstellingen opgeslagen",
      openmeteo: "Open-Meteo (gratis, geen sleutel nodig)",
      test_button: "Verbinding testen",
      test_button_testing: "Bezig met testen…",
      test_success: "✓ Verbinding geslaagd",
      test_error_invalid_auth: "✗ Ongeldige API-sleutel — controleer of deze correct en actief is",
      test_error_cannot_connect: "✗ Kan geen verbinding maken — controleer je internetverbinding",
      test_error_no_service: "✗ Selecteer eerst een weerdienst",
      test_error_unknown: "✗ Test mislukt — onbekende fout",
      owm: "OpenWeatherMap",
      pw: "Pirate Weather"
    },
    _a = {
      zone_size: "Het totale geïrrigeerde oppervlak van deze zone. Wordt samen met de doorvoer gebruikt om te berekenen hoeveel water per run wordt toegediend.",
      zone_throughput: "Totale waterstroom van je irrigatiesysteem voor deze zone (liter/min in metriek, gal/min in imperiaal). Raadpleeg het gegevensblad van je sproeiers of meet hoe lang het duurt om een bak met bekende inhoud te vullen.",
      zone_drainage_rate: "Hoe snel overtollig water uit de bodem wegloopt als de emmer vol is. Typisch: gazon 50 mm/u, zandgrond 100+ mm/u, klei 10 mm/u.",
      zone_bucket: "Huidig watertekort (negatief) of -overschot (positief) voor deze zone. Irrigatie wordt geactiveerd wanneer de emmer onder de drempel zakt.",
      zone_maximum_bucket: "Maximaal vochtoverschot dat de zone kan vasthouden. Water boven dit niveau wordt als afstroming behandeld. Typische waarde: 50 mm.",
      zone_bucket_threshold: "Irrigatie wordt geactiveerd wanneer de emmer onder deze waarde zakt. Moet 0 of negatief zijn. 0 betekent irrigeren zodra er een tekort is.",
      zone_multiplier: "Schaalfactor toegepast op de berekende duur. Boven 1,0 verhoogt, onder 1,0 verlaagt. Handig voor fijnafstemming zonder fysieke metingen te wijzigen.",
      zone_lead_time: "Extra seconden voordat de irrigatie start. Gebruik dit voor het opwarmen van de pomp of het op druk brengen van het systeem.",
      zone_maximum_duration: "Harde bovengrens voor één enkele irrigatierun in seconden. Voorkomt ongecontroleerd water geven. Standaard: 3600 s (1 uur).",
      zone_linked_entity: "De HA-schakelaar- of klep-entiteit die de waterstroom voor deze zone regelt. Deze entiteit wordt ingeschakeld wanneer de irrigatie draait.",
      zone_flow_sensor: "Optionele sensor die het werkelijke waterdebiet meet. Alleen voor rapportage — heeft geen invloed op duurberekeningen.",
      general_autoupdatedelay: "Seconden om te wachten na het starten van HA voordat de eerste weergegevens worden opgehaald. Geeft andere integraties de kans om eerst te initialiseren.",
      general_sensor_debounce: "Minimale tussentijd in milliseconden tussen sensormetingen om ruis van snel veranderende sensoren weg te filteren.",
      general_calctime: "Tijdstip van de dag waarop de irrigatieduren opnieuw worden berekend uit de verzamelde weergegevens. Formaat: UU:MM (24-uurs).",
      general_cleardatatime: "Tijdstip van de dag waarop oude weergegevens worden gewist. Moet later worden ingesteld dan de berekeningstijd.",
      general_days_between: "Minimum aantal dagen tussen irrigatiebeurten voor dezelfde zone. Zet op 0 om uit te schakelen (irrigeren zodra er een tekort is).",
      general_autoupdateinterval: "Hoe vaak weergegevens worden verzameld. Kies een waarde die verse gegevens afweegt tegen API-limieten.",
      general_precipitation_threshold: "Irrigatie wordt overgeslagen als de totale voorspelde neerslag over het vooruitblik-venster deze hoeveelheid overschrijdt.",
      general_temp_threshold: "Irrigatie wordt overgeslagen als de huidige temperatuur onder deze waarde ligt (bijv. om vorstschade te voorkomen).",
      general_wind_threshold: "Irrigatie wordt overgeslagen als de windsnelheid deze waarde overschrijdt (harde wind vermindert de efficiëntie en veroorzaakt drift)."
    },
    fa = {
      title: "Configuratiewizard",
      open_button: "Configuratiewizard",
      close: "Sluiten",
      next: "Volgende",
      back: "Terug",
      finish: "Voltooien",
      skip_step: "Deze stap overslaan",
      step_indicator: "Stap {current} van {total}",
      setup_complete_banner: "Configuratie niet voltooid. Voer de wizard uit om te beginnen.",
      open_wizard: "Wizard openen",
      steps: {
        welcome: {
          title: "Welkom bij Smart Irrigation",
          intro: "Deze wizard leidt je door de vier stappen die nodig zijn om je eerste zone automatisch te laten irrigeren.",
          step1_label: "Weerdienst — waar de weergegevens vandaan komen",
          step2_label: "Berekeningsmodule — hoe de irrigatieduur wordt berekend",
          step3_label: "Sensorgroep — welke gegevensbronnen te gebruiken",
          step4_label: "Zone — je eerste irrigatiezone",
          tip: "Je kunt elke stap overslaan en deze later configureren via het tabblad Instellen."
        },
        weather: {
          title: "Weerdienst",
          description: "Kies hoe je weergegevens ophaalt. Open-Meteo is gratis en vereist geen API-sleutel — de eenvoudigste keuze voor de meeste gebruikers."
        },
        module: {
          title: "Berekeningsmodule",
          description: "Een module berekent hoe lang te irrigeren op basis van evapotranspiratie (ET). De PyETO-module (FAO-56-methode) wordt voor de meeste gebruikers aanbevolen.",
          pick_label: "Moduletype selecteren",
          no_modules: "Geen moduletypen beschikbaar."
        },
        mapping: {
          title: "Sensorgroep",
          description: "Een sensorgroep koppelt elke weervariabele aan een gegevensbron. Stel hieronder de belangrijkste variabelen in — afzonderlijke sensortoewijzingen kun je later verfijnen via het tabblad Instellen → Sensorgroepen.",
          name_label: "Naam van de sensorgroep",
          source_label: "Gegevensbron voor",
          use_weather_service: "Weerdienst",
          use_sensor: "Sensor",
          use_static: "Statische waarde",
          use_none: "Geen / niet gebruikt"
        },
        zone: {
          title: "Eerste zone",
          description: "Een zone is één irrigatiegebied (bijv. gazon, plantenbed). Stel de fysieke eigenschappen in zodat het systeem de juiste irrigatieduur kan berekenen.",
          name_label: "Zonenaam",
          size_label: "Oppervlak",
          throughput_label: "Sproeierdoorvoer",
          entity_label: "Gekoppelde schakelaar of klep",
          entity_placeholder: "bijv. switch.garden_valve",
          module_label: "Berekeningsmodule",
          mapping_label: "Sensorgroep"
        },
        done: {
          title: "Configuratie voltooid!",
          description: "Je eerste zone is klaar. Smart Irrigation berekent nu automatisch de irrigatieduren op basis van weergegevens.",
          next_steps: "Wat je hierna kunt doen:",
          tip1: "Ga naar Zones om de berekende duren en emmerwaarden te bekijken.",
          tip2: "Voeg meer zones toe via het tabblad Zones.",
          tip3: "Verfijn alle instellingen via het tabblad Instellen.",
          go_zones: "Naar Zones",
          go_setup: "Naar Instellen"
        }
      },
      stepper: {
        weather: "Weer",
        module: "Module",
        mapping: "Sensorgroep",
        zone: "Zone"
      },
      confirm_close: {
        body: "Configuratiewizard sluiten? Je voortgang is opgeslagen.",
        keep: "Doorgaan",
        close: "Sluiten"
      }
    },
    ba = {
      common: ra,
      defaults: oa,
      module: sa,
      calcmodules: la,
      panels: da,
      title: ua,
      coordinate_config: ca,
      days_between_irrigation: pa,
      irrigation_start_triggers: ma,
      weather_skip: ha,
      zone_sequencing: ga,
      weather_service_config: va,
      field_help: _a,
      wizard: fa
    },
    ka = Object.freeze({
      __proto__: null,
      common: ra,
      defaults: oa,
      module: sa,
      calcmodules: la,
      panels: da,
      title: ua,
      coordinate_config: ca,
      days_between_irrigation: pa,
      irrigation_start_triggers: ma,
      weather_skip: ha,
      zone_sequencing: ga,
      weather_service_config: va,
      field_help: _a,
      wizard: fa,
      default: ba
    }),
    ya = {
      actions: {
        delete: "Slett",
        edit: "Rediger",
        save: "Lagre",
        cancel: "Avbryt",
        confirm_delete: "Bekreft sletting",
        confirm_delete_zone: "Er du sikker på at du vil slette denne sonen?"
      },
      labels: {
        module: "Modul",
        no: "Nei",
        select: "Velg",
        yes: "Ja",
        enabled: "Aktivert",
        disabled: "Deaktivert",
        before: "før",
        after: "etter",
        settings: "Innstillinger",
        bulk_actions: "Masseoperasjoner"
      },
      attributes: {
        size: "størrelse",
        throughput: "kapasitet",
        state: "status",
        bucket: "beholder",
        last_updated: "sist oppdatert",
        last_calculated: "sist beregnet",
        number_of_data_points: "antall datapunkter"
      },
      loading: "Laster",
      saving: "Lagrer",
      units: {
        seconds: "sekunder"
      },
      "loading-messages": {
        configuration: "Laster konfigurasjon...",
        modules: "Laster moduler...",
        general: "Laster..."
      },
      "saving-messages": {
        adding: "Legger til...",
        saving: "Lagrer..."
      },
      errors: {
        load_failed: "Kunne ikke laste data",
        save_failed: "Kunne ikke lagre endringene",
        delete_failed: "Kunne ikke slette",
        action_failed: "Handlingen mislyktes"
      }
    },
    za = {
      "default-zone": "Standard sone",
      "default-mapping": "Standard sensorguppe"
    },
    wa = {
      calculation: {
        explanation: {
          "module-returned-evapotranspiration-deficiency": "Merk: Denne forklaringen bruker '.' som desimaltegn og viser avrundede verdier. Modulen returnerte evapotranspirasjonsunderskudd på",
          "bucket-was": "Bucket var",
          "new-bucket-values-is": "Ny bucket verdien er",
          "old-bucket-variable": "gammel_bucket",
          delta: "delta",
          "bucket-less-than-zero-irrigation-necessary": "Siden bucket < 0, Vanning er nødvendig.",
          "steps-taken-to-calculate-duration": "For å beregne nøyaktig varighet, ble følgende trinn utført",
          "precipitation-rate-defined-as": "Nedbørshastigheten er definert som",
          "duration-is-calculated-as": "Varigheten beregnes som",
          bucket: "bøtte",
          "precipitation-rate-variable": "nedbørshastighet",
          "multiplier-is-applied": "Nå blir multiplikatoren brukt. Multiplikatoren er",
          "duration-after-multiplier-is": "derfor er varigheten",
          "maximum-duration-is-applied": "Deretter blir den maksimale varigheten brukt. Den maksimale varigheten er",
          "duration-after-maximum-duration-is": "derfor er varigheten",
          "lead-time-is-applied": "Til slutt blir ledetiden brukt. Ledetiden er",
          "duration-after-lead-time-is": "derfor er den endelige varigheten",
          "bucket-larger-than-or-equal-to-zero-no-irrigation-necessary": "Siden bucket >= 0, Ingen vanning er nødvendig, og varigheten er satt til",
          "maximum-bucket-is": "maksimum bucket stærrelse er",
          "max-bucket-variable": "max_bucket",
          drainage: "drenering",
          "drainage-rate": "dreneringsrate",
          hours: "timer",
          "drainage-rate-is": "Dreneringshastigheten ved metning (beholder på maks) er",
          "current-drainage-is": "Gjeldende drenering beregnet som",
          "no-drainage": "Gjeldende drenering er 0 fordi"
        }
      }
    },
    Sa = {
      pyeto: {
        description: "Beregn varigheten basert på FAO56-beregningen fra PyETO-biblioteket"
      },
      static: {
        description: "'Dummy'-modul med en statisk konfigurerbar endring (delta)"
      },
      passthrough: {
        description: "En 'Passthrough'-modul som returnerer verdien av en Evapotranspiration-sensor som delta"
      }
    },
    Aa = {
      general: {
        cards: {
          "automatic-duration-calculation": {
            header: "Automatisk varighetsberegning",
            labels: {
              "auto-calc-enabled": "Beregn sonevarigheter automatisk",
              "auto-calc-time": "Beregn ved",
              "calc-time": "Beregn kl."
            },
            description: "Beregningen bruker værdataene som er samlet inn frem til da, og oppdaterer bøtten for hver automatiske sone. Deretter justeres varigheten basert på den nye bøtteverdien, og de innsamlede værdataene fjernes."
          },
          "automatic-update": {
            errors: {
              "warning-update-time-on-or-after-calc-time": "Advarsel: Oppdateringstidspunkt for værdata på eller etter beregningstidspunktet"
            },
            header: "Automatisk oppdatering av værdata",
            labels: {
              "auto-update-enabled": "Oppdater værdata automatisk",
              "auto-update-first-update": "(Første) Oppdatering kl",
              "auto-update-interval": "Oppdater sensordata hvert",
              "auto-update-schedule": "Oppdateringsplan",
              "auto-update-time": "Oppdater kl.",
              "auto-update-delay": "Oppdateringsforsinkelse"
            },
            options: {
              days: "dager",
              hours: "timer",
              minutes: "minutter"
            },
            description: "Samle inn og lagre værdata automatisk. Værdata kreves for å beregne sonebøtter og varigheter."
          },
          "automatic-clear": {
            header: "Automatisk rydding av værdata",
            description: "Fjern innsamlede værdata automatisk på et konfigurert tidspunkt. Bruk dette for å sikre at det ikke er igjen værdata fra tidligere dager. Ikke fjern værdataene før du beregner, og bruk bare dette alternativet hvis du forventer at den automatiske oppdateringen samler inn værdata etter at du har beregnet for dagen. Ideelt sett rydder du så sent på dagen som mulig.",
            labels: {
              "automatic-clear-enabled": "Tøm innsamlede værdata automatisk",
              "automatic-clear-time": "Tøm værdata kl."
            }
          },
          continuousupdates: {
            header: "Kontinuerlige sensoroppdateringer (eksperimentell)",
            description: "Eksperimentell funksjon for mer granulære værdata.",
            labels: {
              continuousupdates: "Aktiver kontinuerlige oppdateringer",
              sensor_debounce: "Sensor-debounce",
              "sensor-debounce": "Sensor-debouncetid (ms)"
            }
          }
        },
        description: "Denne siden gir globale innstillinger.",
        title: "Generelt",
        sections: {
          weather: "Vær",
          automation: "Automatisering",
          location: "Plassering",
          watering: "Vanningsatferd"
        }
      },
      help: {
        title: "Hjelp",
        cards: {
          "how-to-get-help": {
            title: "Hvordan få hjelp",
            "first-read-the": "Først, les",
            wiki: "Dokumentasjon",
            "if-you-still-need-help": "Hvis du fremdeles trenger hjelp, ta kontakt på",
            "community-forum": "Fellesskapsforumet",
            "or-open-a": "eller åpne en",
            "github-issue": "Github-sak",
            "english-only": "Kun på engelsk"
          }
        }
      },
      mappings: {
        cards: {
          "add-mapping": {
            actions: {
              add: "Legg til sensorguppe"
            },
            header: "Legg til sensorgupper"
          },
          mapping: {
            aggregates: {
              average: "Gjennomsnitt",
              first: "Første",
              last: "Siste",
              maximum: "Maksimum",
              median: "Median",
              minimum: "Minimum",
              sum: "Sum",
              riemannsum: "Riemann-sum",
              delta: "Delta"
            },
            errors: {
              "cannot-delete-mapping-because-zones-use-it": "Du kan ikke slette denne sensorguppen fordi minst én sone bruker den.",
              invalid_source: "Ugyldig kilde",
              source_does_not_exist: "Kilden finnes ikke. Angi en gyldig kilde, for eksempel 'sensor.mysensor'."
            },
            items: {
              dewpoint: "Duggpunkt",
              evapotranspiration: "Evapotranspirasjon",
              humidity: "Luftfuktighet",
              "maximum temperature": "Maksimumstemperatur",
              "minimum temperature": "Minimumstemperatur",
              precipitation: "Total nedbør",
              pressure: "Trykk",
              "solar radiation": "Solstråling",
              temperature: "Temperatur",
              windspeed: "Vindhastighet",
              "current precipitation": "Nåværende nedbør"
            },
            "sensor-aggregate-of-sensor-values-to-calculate": "av sensordata for å beregne varighet",
            "sensor-aggregate-use-the": "Bruk",
            "sensor-entity": "Sensorenhet",
            static_value: "Verdi",
            "input-units": "Inndata gir verdier i",
            source: "Kilde",
            sources: {
              none: "Ingen",
              weather_service: "Værtjeneste",
              sensor: "Sensor",
              static: "Statisk verdi"
            },
            pressure_types: {
              absolute: "absolutt",
              relative: "relativ"
            },
            "pressure-type": "Trykket er"
          }
        },
        description: "Legg til en eller flere sensorgupper som henter værdata fra Weather service, fra sensorer eller en kombinasjon av disse. Du kan tilordne hver sensorguppe til en eller flere soner",
        labels: {
          "mapping-name": "Navn"
        },
        no_items: "Det er ingen definerte sensorgupper ennå.",
        title: "Sensorgupper",
        "weather-records": {
          title: "Værregistreringer",
          timestamp: "Tid",
          temperature: "Temp.",
          humidity: "Humidity",
          precipitation: "Nedbør",
          "retrieval-time": "Hentet",
          "no-data": "Ingen værdata tilgjengelig for denne sensorgruppen",
          dewpoint: "Dugg",
          wind: "Vind",
          pressure: "Trykk"
        }
      },
      modules: {
        cards: {
          "add-module": {
            actions: {
              add: "Legg til modul"
            },
            header: "Legg til modul"
          },
          module: {
            errors: {
              "cannot-delete-module-because-zones-use-it": "Du kan ikke slette denne modulen fordi minst én sone bruker den."
            },
            labels: {
              configuration: "Konfigurasjon",
              required: "indikerer et obligatorisk felt"
            },
            "translated-options": {
              DontEstimate: "Ikke beregn",
              EstimateFromSunHours: "Beregn fra soltimer",
              EstimateFromTemp: "Beregn fra temperatur",
              EstimateFromSunHoursAndTemperature: "Estimer fra gjennomsnittet av soltimer og temperatur"
            }
          }
        },
        description: "Legg til en eller flere moduler som beregner vanningsvarighet. Hver modul har sin egen konfigurasjon og kan brukes til å beregne varighet for en eller flere soner.",
        no_items: "Det er ingen definerte moduler ennå.",
        title: "Moduler"
      },
      zones: {
        actions: {
          add: "Legg til",
          calculate: "Beregn",
          information: "Informasjon",
          update: "Oppdater",
          "reset-bucket": "Nullstill bøtte",
          "view-weather-info": "Se værdata",
          "view-weather-info-message": "Værdata tilgjengelig for",
          "view-watering-calendar": "Vanningskalender",
          irrigate_all: "Vann alle soner nå",
          open_settings: "Rediger innstillinger"
        },
        cards: {
          "add-zone": {
            actions: {
              add: "Legg til sone"
            },
            header: "Legg til sone"
          },
          "zone-actions": {
            actions: {
              "calculate-all": "Beregn varigheter på nytt",
              "update-all": "Oppdater værdata",
              "reset-all-buckets": "Nullstill alle bøtter",
              "clear-all-weatherdata": "Tøm alle værdata"
            },
            header: "Handlinger på alle soner"
          }
        },
        description: "Spesifiser en eller flere vanningssoner her. Vanningens varighet beregnes per sone, avhengig av størrelse, gjennomstrømning, tilstand, modul og sensorguppe.",
        labels: {
          bucket: "Bøtte",
          duration: "Varighet",
          "lead-time": "Ledetid",
          mapping: "Sensorguppe",
          "maximum-duration": "Maksimal varighet",
          multiplier: "Multiplikator",
          name: "Navn",
          size: "Størrelse",
          state: "Tilstand",
          states: {
            automatic: "Automatisk",
            disabled: "Deaktivert",
            manual: "Manuell"
          },
          throughput: "Gjennomstrømning",
          "maximum-bucket": "Maksimal bøtte",
          last_calculated: "Sist beregnet",
          "data-last-updated": "Data sist oppdatert",
          "data-number-of-data-points": "Antall datapunkter",
          drainage_rate: "Dreneringsrate",
          linked_entity: "Tilknyttet bryter/ventil-enhet",
          linked_entity_placeholder: "f.eks. switch.hage_ventil",
          irrigate_now: "Vann nå",
          bucket_threshold: "Minimum underskudd for vanning",
          flow_sensor: "Strømningsmåler-sensor (valgfritt)",
          flow_sensor_placeholder: "f.eks. sensor.zone_flow_rate"
        },
        no_items: "Det er ingen definerte soner ennå.",
        title: "Soner",
        confirm_irrigate: {
          title: "Starte vanning?",
          body: "Dette åpner nå de tilkoblede ventilene og overstyrer alle hoppe-over-betingelser (regn, temperatur, minste antall dager mellom vanninger).",
          all_linked_zones: "Alle tilkoblede soner",
          toast_started: "Vanning startet",
          toast_failed: "Vanning mislyktes"
        },
        status: {
          decision_disabled: "Avslått — denne sonen vannes ikke automatisk.",
          decision_water: "Vanning nødvendig: omtrent {duration} ved neste planlagte kjøring.",
          decision_water_at: "Vanner omtrent {duration} kl. {time}.",
          decision_water_skip: "Underskudd ~{duration}, men neste kjøring blir trolig hoppet over ({reason}).",
          decision_water_no_schedule: "Underskudd ~{duration} — ingen tidsplan vanner denne sonen; start den manuelt.",
          decision_no_water: "Ingen vanning nødvendig nå — jorda har nok fuktighet.",
          decision_unknown: "Ikke beregnet ennå — trykk Oppdater og deretter Beregn for å sjekke.",
          last_checked: "Sist sjekket",
          never: "aldri",
          saved: "Lagret",
          estimate_now: "Nå",
          estimate_tag: "est.",
          estimate_method: {
            hourly: "Sanntidsestimat fra timesvær siden forrige beregning",
            proxy: "Estimat fordelt fra dagens varsel siden forrige beregning"
          }
        },
        help: {
          bucket: "Jordfuktighetsbalanse (bøtte). En negativ verdi betyr at jorda er tørr og sonen trenger vann.",
          calculate: "Beregner hvor lenge det skal vannes ut fra de nyeste dataene. Kjør dette etter Oppdater.",
          update: "Henter de nyeste vær-/sensordataene for denne sonen.",
          irrigate_link_entity: "Koble en bryter/ventil i sonens innstillinger for å aktivere manuell vanning.",
          irrigate_all: "Åpner nå de tilkoblede ventilene for hver sone med underskudd. Hoppe-over-betingelser (regn, vind, temperatur) ignoreres.",
          update_all: "Henter de nyeste vær-/sensordataene for alle soner. Endrer ikke varighetene i seg selv.",
          calculate_all: "Beregner vanningsvarigheten for hver automatisk sone på nytt ut fra dataene som er samlet så langt."
        },
        outlook: {
          next_run: "Neste kjøring",
          no_schedule: "Ingen automatisk tidsplan — soner vannes bare når du starter dem.",
          setup_schedule: "Sett opp en tidsplan",
          targets_all: "alle soner",
          targets_zones: "{count} soner",
          will_skip: "Neste kjøring blir trolig hoppet over",
          will_run: "Forholdene ser klare ut for neste kjøring.",
          why_skipped: "Hvorfor?",
          provisional: "varsel — kan endre seg",
          active_guards: "Aktive betingelser",
          last_run: "Forrige kjøring",
          last_run_skipped: "hoppet over",
          last_run_ran: "kjørt",
          today: "i dag",
          tomorrow: "i morgen",
          actions: {
            irrigate: "Vann",
            calculate: "Beregn på nytt",
            update: "Oppdater data"
          },
          checks: {
            precipitation: "Regnvarsel",
            days_between: "Dager mellom vanninger",
            temperature: "Lav temperatur",
            wind: "Sterk vind",
            rain_sensor: "Regnsensor"
          },
          check_detail: {
            precipitation: "{observed} mm (≥ {threshold} mm)",
            days_between: "{observed}/{threshold} dager",
            temperature: "{observed}° (under {threshold}°)",
            wind: "{observed} (over {threshold})",
            rain_sensor: "{observed}"
          }
        },
        calendar: {
          no_data: "Ingen vanningskalenderdata tilgjengelig for denne sonen.",
          error_prefix: "Feil ved generering av kalender:",
          month: "Måned",
          et: "ET (mm)",
          precipitation: "Nedbør (mm)",
          watering: "Vanning (L)",
          avg_temp: "Gj.sn. temp. (°C)",
          method_prefix: "Metode:"
        },
        confirm_action: {
          reset_bucket_title: "Nullstille bøtta for denne sonen?",
          reset_bucket_body: "Dette setter bøtta tilbake til 0 og forkaster den oppsamlede fuktighetsbalansen for denne sonen.",
          reset_all_buckets_title: "Nullstille alle bøtter?",
          reset_all_buckets_body: "Dette setter bøtta for hver sone tilbake til 0 og forkaster den oppsamlede fuktighetsbalansen. Vanningsberegningene starter på nytt ved neste oppdatering.",
          clear_weather_title: "Slette alle værdata?",
          clear_weather_body: "Dette sletter alle innsamlede vær- og sensordata for alle soner. Sonene trenger nye data før de kan beregne igjen."
        }
      },
      title: "Smart vanning",
      schedules: {
        title: "Tidsplaner",
        description: "Opprett gjentakende tidsplaner for automatisk beregning, oppdatering eller vanning — uten automatiseringer.",
        add: "Legg til tidsplan",
        no_items: "Ingen tidsplaner konfigurert ennå. Klikk på 'Legg til tidsplan'.",
        zones_all: "Alle soner",
        zones_specific: "Spesifikke soner",
        hours: "timer",
        minutes: "min",
        types: {
          daily: "Daglig",
          weekly: "Ukentlig",
          monthly: "Månedlig",
          interval: "Hver N time",
          sunrise: "Soloppgang",
          sunset: "Solnedgang",
          solar_azimuth: "Solazimutt"
        },
        actions: {
          calculate: "Beregn (oppdater vanningsvarighet)",
          update: "Oppdater (samle inn værdata)",
          irrigate: "Vann (styr ventiler direkte)"
        },
        days: {
          monday: "Ma",
          tuesday: "Ti",
          wednesday: "On",
          thursday: "To",
          friday: "Fr",
          saturday: "Lø",
          sunday: "Sø"
        },
        fields: {
          name: "Navn",
          type: "Tidsplantype",
          enabled: "Aktivert",
          time: "Tid (HH:MM)",
          days_of_week: "Ukedager",
          day_of_month: "Dag i måneden",
          interval_hours: "Intervall",
          action: "Handling",
          zones: "Soner",
          start_date: "Startdato (valgfritt)",
          end_date: "Sluttdato (valgfritt)",
          offset_minutes: "Forskyvning fra soloppgang/-nedgang",
          account_for_duration: "Start tidlig slik at vanningen er ferdig til måltidspunktet",
          azimuth_angle: "Solazimutt-vinkel",
          time_anchor: "Tidspunktet angir"
        },
        dialog: {
          add_title: "Legg til tidsplan",
          edit_title: "Rediger tidsplan"
        },
        time_anchor: {
          start: "Start på vanningen",
          finish: "Slutt på vanningen"
        }
      },
      info: {
        title: "Info",
        description: "Vis informasjon om neste vanning og systemstatus.",
        "configuration-not-available": "Konfigurasjon ikke tilgjengelig.",
        cards: {
          "zone-bucket-values": {
            title: "Sone-beholderverdier og varighet",
            labels: {
              bucket: "Beholder",
              duration: "Varighet"
            },
            "no-zones": "Ingen soner konfigurert"
          },
          "next-irrigation": {
            title: "Neste vanning",
            labels: {
              "next-start": "Neste start",
              duration: "Varighet",
              zones: "Soner"
            },
            "no-data": "Ingen data tilgjengelig"
          },
          "irrigation-reason": {
            title: "Årsak til vanning",
            labels: {
              reason: "Årsak",
              sunrise: "Soloppgang",
              "total-duration": "Total varighet",
              explanation: "Forklaring"
            },
            "no-data": "Ingen data tilgjengelig"
          },
          irrigate_now: {
            title: "Vann nå",
            description: "Start vanning umiddelbart for alle soner med tilknyttet enhet. Hoppover-betingelser ignoreres.",
            button_all: "Start alle soner nå",
            no_linked_zones: "Ingen soner har en tilknyttet bryter/ventil-enhet med beregnet varighet."
          }
        }
      },
      setup: {
        title: "Oppsett"
      }
    },
    xa = {
      title: "Stedskoordinater",
      description: "Konfigurer stedskoordinater for innhenting av værdata. Du kan bruke manuelle koordinater som er forskjellige fra din Home Assistant plassering om nødvendig.",
      manual_enabled: "Bruk manuelle koordinater",
      use_ha_location: "Bruk Home Assistant plassering",
      latitude: "Breddegrad (desimalgrader)",
      longitude: "Lengdegrad (desimalgrader)",
      elevation: "Høyde (meter over havet)",
      current_ha_coords: "Gjeldende Home Assistant koordinater"
    },
    Ea = {
      title: "Dager mellom vanning",
      description: "Konfigurer minimumsantall dager mellom vanningshendelser.",
      label: "Minimum dager mellom vanning",
      help_text: "Sett til 0 for å deaktivere. Verdier fra 1-365 dager støttes."
    },
    Ma = "Smart Irrigation",
    Ta = {
      title: "Utløsere for vanningsstart",
      description: "Konfigurer når vanningen skal starte basert på solhendelser. Du kan legge til flere utløsere for ulike tidsplaner. For soloppgangsutløsere vil et forskyvning på 0 automatisk bruke den totale varigheten av alle aktiverte soner.",
      add_trigger: "Legg til utløser",
      edit_trigger: "Rediger utløser",
      delete_trigger: "Slett utløser",
      trigger_types: {
        sunrise: "Soloppgang",
        sunset: "Solnedgang",
        solar_azimuth: "Solazimut"
      },
      fields: {
        name: {
          name: "Utløsernavn",
          description: "Et beskrivende navn for å identifisere denne utløseren"
        },
        type: {
          name: "Utløsertype",
          description: "Typen solhendelse å utløse på"
        },
        enabled: {
          name: "Aktivert",
          description: "Om denne utløseren er aktiv nå"
        },
        offset_minutes: {
          name: "Forskyvning (minutter)",
          description: "Minutter før (-) eller etter (+) solhendelsen. For soloppgangsutløsere, bruk 0 for automatisk timing basert på total sonevarighet."
        },
        azimuth_angle: {
          name: "Azimutvinkel (grader)",
          description: "Solazimutvinkel i grader der 0=Nord, 90=Øst, 180=Sør, 270=Vest"
        },
        account_for_duration: {
          name: "Ta hensyn til varighet",
          description: "Når aktivert starter vanningen tidlig nok til å bli ferdig til angitt tidspunkt. Når deaktivert starter vanningen nøyaktig på angitt tidspunkt."
        }
      },
      dialog: {
        add_title: "Legg til utløser for vanningsstart",
        edit_title: "Rediger utløser for vanningsstart",
        cancel: "Avbryt",
        save: "Lagre",
        delete: "Slett"
      },
      no_triggers: "Ingen utløsere for vanningsstart konfigurert. Systemet bruker standardatferden (soloppgang med total sonevarighet). Legg til utløsere for å tilpasse når vanningen starter.",
      offset_auto: "Automatisk (beregnet fra total sonevarighet)",
      confirm_delete: "Er du sikker på at du vil slette utløseren '{name}'?",
      validation: {
        name_required: "Utløsernavn er påkrevd",
        azimuth_invalid: "Azimutvinkelen må være et gyldig tall"
      },
      help: {
        sunrise_offset: "For soloppgangsutløsere: Bruk negative verdier for å starte før soloppgang, positive for å starte etter. Sett til 0 for automatisk å starte tidlig nok til å fullføre alle soner før soloppgang.",
        sunset_offset: "For solnedgangsutløsere: Bruk negative verdier for å starte før solnedgang, positive for å starte etter solnedgang.",
        azimuth_explanation: "Solazimut er kompassretningen til solen. 0°=Nord, 90°=Øst, 180°=Sør, 270°=Vest. Du kan angi en hvilken som helst vinkelverdi (f.eks. 450° = 90°, -30° = 330°). Bruk dette til å utløse vanning når solen når en bestemt posisjon.",
        multiple_triggers: "Du kan konfigurere flere utløsere. Hver aktiverte utløser planlegger vanningsstart uavhengig."
      }
    },
    Da = {
      title: "Hoppover-betingelser",
      description: "Hopp automatisk over vanning når forholdene er ugunstige. Nedbørs-, temperatur- og vindsjekker krever en værtjeneste.",
      threshold_label: "Nedbørsterskel",
      threshold_description: "Minimum total forventet nedbør (i mm) over varslingsvinduet for å hoppe over vanning.",
      lookahead_label: "Varslingsvindu (dager)",
      lookahead_help: "Hvor mange kommende varseldøgn som summeres ved regnsjekken. Varselet starter i morgen (i dag utelates), så 1 = bare neste dag, 2 = de neste to dagene, og så videre.",
      temp_section_title: "Hopp over ved lav temperatur",
      temp_threshold_label: "Hopp over hvis temperatur under",
      wind_section_title: "Hopp over ved sterk vind",
      wind_threshold_label: "Hopp over hvis vindhastighet over",
      rain_sensor_section_title: "Regnsensorbetingelse",
      rain_sensor_label: "Regnsensor-enhet (valgfritt)",
      rain_sensor_placeholder: "f.eks. binary_sensor.regn"
    },
    Pa = {
      title: "Sonesekvens",
      description: "Når flere soner trenger vanning, velg om de kjører samtidig eller én etter én. I sekvensiell modus venter systemet til hver sone er ferdig før neste starter.",
      parallel: "Parallell (alle soner samtidig)",
      sequential: "Sekvensiell (én sone om gangen)",
      rotating: "Roterende (soner bytter på)",
      max_consecutive_duration_label: "Maks. sammenhengende kjøretid per sone",
      max_consecutive_duration_unit: "minutter",
      min_absorption_time_label: "Min. absorpsjonstid mellom økter",
      min_absorption_time_unit: "minutter (0 = deaktivert)"
    },
    ja = {
      title: "Værtjeneste",
      description: "Konfigurer hvilken værtjeneste som skal brukes for ET-beregninger og hopp over-betingelser.",
      enabled_label: "Aktiver værtjeneste",
      service_label: "Værtjeneste",
      api_key_label: "API-nøkkel",
      api_key_placeholder: "La stå tom for å beholde eksisterende nøkkel",
      api_key_configured: "API-nøkkel er konfigurert",
      api_key_not_configured: "Ingen API-nøkkel konfigurert",
      api_key_help: "En API-nøkkel fra den valgte værtjenesteleverandøren din. Open-Meteo krever ingen nøkkel. OpenWeatherMap og Pirate Weather tilbyr begge gratis nivåer.",
      no_api_key_needed: "Open-Meteo er en gratis tjeneste og krever ingen API-nøkkel.",
      save_button: "Lagre værinnstillinger",
      saved: "Værinnstillinger lagret",
      openmeteo: "Open-Meteo (gratis, ingen nøkkel nødvendig)",
      test_button: "Test tilkobling",
      test_button_testing: "Tester…",
      test_success: "✓ Tilkobling vellykket",
      test_error_invalid_auth: "✗ Ugyldig API-nøkkel — sjekk at den er riktig og aktiv",
      test_error_cannot_connect: "✗ Kan ikke koble til — sjekk internettforbindelsen din",
      test_error_no_service: "✗ Velg en værtjeneste først",
      test_error_unknown: "✗ Test mislyktes — ukjent feil",
      owm: "OpenWeatherMap",
      pw: "Pirate Weather"
    },
    Na = {
      zone_size: "Det totale vannede arealet for denne sonen. Brukes sammen med gjennomstrømningen for å beregne hvor mye vann som tilføres per kjøring.",
      zone_throughput: "Total vanngjennomstrømning for vanningssystemet ditt for denne sonen (liter/min i metrisk, gal/min i imperisk). Sjekk databladet for sprederne dine eller mål ved å ta tiden på hvor lang tid det tar å fylle en beholder med kjent volum.",
      zone_drainage_rate: "Hvor raskt overflødig vann dreneres fra jorden når bøtten er full. Typisk: plen 50 mm/t, sandjord 100+ mm/t, leire 10 mm/t.",
      zone_bucket: "Nåværende vannunderskudd (negativt) eller -overskudd (positivt) for denne sonen. Vanning utløses når bøtten faller under terskelen.",
      zone_maximum_bucket: "Maksimalt fuktoverskudd sonen kan holde på. Vann over dette nivået behandles som avrenning. Typisk verdi: 50 mm.",
      zone_bucket_threshold: "Vanning utløses når bøtten faller under denne verdien. Må være 0 eller negativ. 0 betyr å vanne så snart det er et underskudd.",
      zone_multiplier: "Skaleringsfaktor som brukes på den beregnede varigheten. Over 1,0 øker, under 1,0 reduserer. Nyttig for finjustering uten å endre fysiske målinger.",
      zone_lead_time: "Ekstra sekunder før vanningen starter. Bruk dette for oppvarming av pumpen eller trykksetting av systemet.",
      zone_maximum_duration: "Hard øvre grense for én enkelt vanningskjøring i sekunder. Hindrer ukontrollert vanning. Standard: 3600 s (1 time).",
      zone_linked_entity: "HA-bryter- eller ventilenheten som styrer vannstrømmen for denne sonen. Denne enheten slås på når vanningen kjører.",
      zone_flow_sensor: "Valgfri sensor som måler faktisk vannstrømningsrate. Brukes bare til rapportering — påvirker ikke varighetsberegninger.",
      general_autoupdatedelay: "Sekunder å vente etter at HA starter før første henting av værdata. Lar andre integrasjoner initialisere først.",
      general_sensor_debounce: "Minimum mellomrom i millisekunder mellom sensoravlesninger for å filtrere bort støy fra raskt skiftende sensorer.",
      general_calctime: "Tidspunkt på dagen da vanningsvarighetene beregnes på nytt fra innsamlede værdata. Format: TT:MM (24-timers).",
      general_cleardatatime: "Tidspunkt på dagen da gamle værdata slettes. Må settes senere enn beregningstidspunktet.",
      general_days_between: "Minimum antall dager mellom vanninger for samme sone. Sett til 0 for å deaktivere (vann så snart det er et underskudd).",
      general_autoupdateinterval: "Hvor ofte værdata samles inn. Velg en verdi som balanserer ferske data mot API-grenser.",
      general_precipitation_threshold: "Vanning hoppes over hvis total varslet nedbør over varslingsvinduet overstiger denne mengden.",
      general_temp_threshold: "Vanning hoppes over hvis nåværende temperatur er under denne verdien (f.eks. for å forhindre frostskade).",
      general_wind_threshold: "Vanning hoppes over hvis vindhastigheten overstiger denne verdien (sterk vind reduserer effektiviteten og forårsaker avdrift)."
    },
    Ca = {
      title: "Oppsettsveiviser",
      open_button: "Oppsettsveiviser",
      close: "Lukk",
      next: "Neste",
      back: "Tilbake",
      finish: "Fullfør",
      skip_step: "Hopp over dette trinnet",
      step_indicator: "Trinn {current} av {total}",
      setup_complete_banner: "Oppsett ikke fullført. Kjør veiviseren for å komme i gang.",
      open_wizard: "Åpne veiviser",
      steps: {
        welcome: {
          title: "Velkommen til Smart Irrigation",
          intro: "Denne veiviseren leder deg gjennom de fire trinnene som trengs for å få den første sonen din til å vanne automatisk.",
          step1_label: "Værtjeneste — hvor værdataene hentes fra",
          step2_label: "Beregningsmodul — hvordan vanningsvarigheten beregnes",
          step3_label: "Sensorgruppe — hvilke datakilder som skal brukes",
          step4_label: "Sone — din første vanningssone",
          tip: "Du kan hoppe over et hvilket som helst trinn og konfigurere det senere fra Oppsett-fanen."
        },
        weather: {
          title: "Værtjeneste",
          description: "Velg hvordan værdata hentes. Open-Meteo er gratis og krever ingen API-nøkkel — det enkleste valget for de fleste."
        },
        module: {
          title: "Beregningsmodul",
          description: "En modul beregner hvor lenge det skal vannes basert på evapotranspirasjon (ET). PyETO-modulen (FAO-56-metoden) anbefales for de fleste.",
          pick_label: "Velg modultype",
          no_modules: "Ingen modultyper tilgjengelig."
        },
        mapping: {
          title: "Sensorgruppe",
          description: "En sensorgruppe kobler hver værvariabel til en datakilde. Angi nøkkelvariablene nedenfor — du kan finjustere individuelle sensortilordninger senere fra Oppsett → Sensorgrupper-fanen.",
          name_label: "Navn på sensorgruppe",
          source_label: "Datakilde for",
          use_weather_service: "Værtjeneste",
          use_sensor: "Sensor",
          use_static: "Statisk verdi",
          use_none: "Ingen / ikke brukt"
        },
        zone: {
          title: "Første sone",
          description: "En sone er ett vanningsområde (f.eks. plen, bed). Angi de fysiske egenskapene slik at systemet kan beregne riktig vanningsvarighet.",
          name_label: "Sonenavn",
          size_label: "Areal",
          throughput_label: "Spredergjennomstrømning",
          entity_label: "Tilkoblet bryter eller ventil",
          entity_placeholder: "f.eks. switch.garden_valve",
          module_label: "Beregningsmodul",
          mapping_label: "Sensorgruppe"
        },
        done: {
          title: "Oppsett fullført!",
          description: "Den første sonen din er klar. Smart Irrigation vil nå beregne vanningsvarigheter automatisk basert på værdata.",
          next_steps: "Hva du kan gjøre videre:",
          tip1: "Gå til Soner for å se beregnede varigheter og bøtteverdier.",
          tip2: "Legg til flere soner fra Soner-fanen.",
          tip3: "Finjuster alle innstillinger fra Oppsett-fanen.",
          go_zones: "Gå til Soner",
          go_setup: "Gå til Oppsett"
        }
      },
      stepper: {
        weather: "Vær",
        module: "Modul",
        mapping: "Sensorgruppe",
        zone: "Sone"
      },
      confirm_close: {
        body: "Lukke oppsettsveiviseren? Fremgangen din er lagret.",
        keep: "Fortsett",
        close: "Lukk"
      }
    },
    Ha = {
      common: ya,
      defaults: za,
      module: wa,
      calcmodules: Sa,
      panels: Aa,
      coordinate_config: xa,
      days_between_irrigation: Ea,
      title: Ma,
      irrigation_start_triggers: Ta,
      weather_skip: Da,
      zone_sequencing: Pa,
      weather_service_config: ja,
      field_help: Na,
      wizard: Ca
    },
    Oa = Object.freeze({
      __proto__: null,
      common: ya,
      defaults: za,
      module: wa,
      calcmodules: Sa,
      panels: Aa,
      coordinate_config: xa,
      days_between_irrigation: Ea,
      title: Ma,
      irrigation_start_triggers: Ta,
      weather_skip: Da,
      zone_sequencing: Pa,
      weather_service_config: ja,
      field_help: Na,
      wizard: Ca,
      default: Ha
    }),
    La = {
      actions: {
        delete: "Zmazať",
        edit: "Upraviť",
        save: "Uložiť",
        cancel: "Zrušiť",
        confirm_delete: "Potvrdiť odstránenie",
        confirm_delete_zone: "Naozaj chceš odstrániť túto zónu?"
      },
      labels: {
        module: "Modul",
        no: "Nie",
        select: "Zvoliť",
        yes: "Áno",
        enabled: "Povolené",
        disabled: "Zakázané",
        before: "pred",
        after: "po",
        settings: "Nastavenia",
        bulk_actions: "Hromadné akcie"
      },
      attributes: {
        size: "veľkosť",
        throughput: "priepustnosť",
        state: "stav",
        bucket: "zásobník",
        last_updated: "posledná aktualizácia",
        last_calculated: "posledný výpočet",
        number_of_data_points: "počet dátových bodov"
      },
      loading: "Načítanie",
      saving: "Ukladanie",
      units: {
        seconds: "sekúnd"
      },
      "loading-messages": {
        configuration: "Načítanie konfigurácie...",
        modules: "Načítanie modulov...",
        general: "Načítanie..."
      },
      "saving-messages": {
        adding: "Pridávanie...",
        saving: "Ukladanie..."
      },
      errors: {
        load_failed: "Údaje sa nepodarilo načítať",
        save_failed: "Zmeny sa nepodarilo uložiť",
        delete_failed: "Nepodarilo sa odstrániť",
        action_failed: "Akcia zlyhala"
      }
    },
    Ia = {
      "default-zone": "Predvolená zóna",
      "default-mapping": "Predvolená skupina snímačov"
    },
    Ba = {
      calculation: {
        explanation: {
          "module-returned-evapotranspiration-deficiency": "Poznámka: toto vysvetlenie používa '.' ako oddeľovač desatinných miest zobrazuje zaokrúhlené a metrické hodnoty. Modul vrátil nedostatok evapotranspirácie",
          "bucket-was": "Vedro bolo",
          "new-bucket-values-is": "Hodnota nového vedra je",
          "old-bucket-variable": "staré_vedro",
          delta: "delta",
          "bucket-less-than-zero-irrigation-necessary": "Keďže vedro < 0, je potrebné zavlažovanie",
          "steps-taken-to-calculate-duration": "Na výpočet presného trvania sa vykonali nasledujúce kroky",
          "precipitation-rate-defined-as": "Miera zrážok je definovaná ako",
          "duration-is-calculated-as": "Trvanie sa vypočíta ako",
          bucket: "vedro",
          "precipitation-rate-variable": "úhrn zrážok",
          "multiplier-is-applied": "Teraz sa použije multiplikátor. Násobiteľ je",
          "duration-after-multiplier-is": "teda trvanie je",
          "maximum-duration-is-applied": "Potom sa použije maximálne trvanie. Maximálne trvanie je",
          "duration-after-maximum-duration-is": "teda trvanie je",
          "lead-time-is-applied": "Nakoniec sa použije dodacia lehota. Dodacia lehota je",
          "duration-after-lead-time-is": "teda konečné trvanie je",
          "bucket-larger-than-or-equal-to-zero-no-irrigation-necessary": "Keďže vedro >= 0, nie je potrebné žiadne zavlažovanie a trvanie je nastavené na",
          "maximum-bucket-is": "maximálna veľkosť vedra je",
          "max-bucket-variable": "max_bucket",
          drainage: "odvodnenie",
          "drainage-rate": "miera odvodnenia",
          hours: "hodiny",
          "drainage-rate-is": "Rýchlosť odtoku pri nasýtení (zásobník na maxime) je",
          "current-drainage-is": "Aktuálna drenáž vypočítaná ako",
          "no-drainage": "Aktuálna drenáž je 0, pretože"
        }
      }
    },
    Ra = {
      pyeto: {
        description: "Vypočítajte trvanie na základe výpočtu FAO56 z knižnice PyETO"
      },
      static: {
        description: "'Atrapa' modul so statickou konfigurovateľnou deltou"
      },
      passthrough: {
        description: "Priechodný modul, ktorý vracia hodnotu evapotranspiračného senzora ako delta"
      }
    },
    Ua = {
      general: {
        cards: {
          "automatic-duration-calculation": {
            header: "Automatický výpočet trvania",
            description: "Výpočet berie zhromaždené údaje o počasí až do tohto bodu a aktualizuje vedro pre každú automatickú zónu. Potom sa trvanie upraví na základe novej hodnoty segmentu a zhromaždené údaje o počasí sa odstránia.",
            labels: {
              "auto-calc-enabled": "Automaticky vypočítajte trvanie zón",
              "auto-calc-time": "Vypočítajte pri",
              "calc-time": "Vypočítať o"
            }
          },
          "automatic-update": {
            errors: {
              "warning-update-time-on-or-after-calc-time": "Upozornenie: Čas aktualizácie údajov o počasí v čase výpočtu alebo po ňom"
            },
            header: "Automatická aktualizácia poveternostných údajov",
            description: "Automaticky zbierajte a ukladajte údaje o počasí. Údaje o počasí sú potrebné na výpočet segmentov zón a trvania.",
            labels: {
              "auto-update-enabled": "Automaticky aktualizovať údaje o počasí",
              "auto-update-delay": "Oneskorenie aktualizácie",
              "auto-update-interval": "Aktualizujte údaje snímača každý",
              "auto-update-schedule": "Plán aktualizácie",
              "auto-update-time": "Aktualizovať o"
            },
            options: {
              days: "dni",
              hours: "hodiny",
              minutes: "minúty"
            }
          },
          "automatic-clear": {
            header: "Automatické orezávanie údajov o počasí",
            description: "Automaticky odstráňte zhromaždené údaje o počasí v nakonfigurovanom čase. Použite to, aby ste sa uistili, že nezostali žiadne údaje o počasí z predchádzajúcich dní. Neodstraňujte údaje o počasí pred výpočtom a túto možnosť použite iba vtedy, ak očakávate, že automatická aktualizácia bude zhromažďovať údaje o počasí až po výpočte na daný deň. V ideálnom prípade chcete prerezávať tak neskoro, ako je to možné.",
            labels: {
              "automatic-clear-enabled": "Automaticky vymazať zhromaždené údaje o počasí",
              "automatic-clear-time": "Vymazať údaje o počasí o"
            }
          },
          continuousupdates: {
            header: "Priebežné aktualizácie senzorov (experimentálne)",
            description: "Experimentálna funkcia pre podrobnejšie meteorologické dáta.",
            labels: {
              continuousupdates: "Povoliť priebežné aktualizácie",
              sensor_debounce: "Debounce senzora",
              "sensor-debounce": "Čas odrazu senzora (ms)"
            }
          }
        },
        description: "Táto stránka poskytuje globálne nastavenia.",
        title: "Všeobecné",
        sections: {
          weather: "Počasie",
          automation: "Automatizácia",
          location: "Poloha",
          watering: "Správanie zavlažovania"
        }
      },
      help: {
        title: "Pomoc",
        cards: {
          "how-to-get-help": {
            title: "Ako získať pomoc",
            "first-read-the": "Najprv si prečítajte",
            wiki: "Dokumentácia",
            "if-you-still-need-help": "Ak stále potrebujete pomoc, obráťte sa na",
            "community-forum": "komunitné fórum",
            "or-open-a": "alebo otvorte a",
            "github-issue": "Problém Github",
            "english-only": "len anglicky"
          }
        }
      },
      mappings: {
        cards: {
          "add-mapping": {
            actions: {
              add: "Pridať skupinu snímačov"
            },
            header: "Pridajte skupiny senzorov"
          },
          mapping: {
            aggregates: {
              average: "Priemer",
              first: "Prvý",
              last: "Posledný",
              maximum: "Maximum",
              median: "Medián",
              minimum: "Minimum",
              sum: "Súčet",
              riemannsum: "Riemannova suma",
              delta: "Delta"
            },
            errors: {
              "cannot-delete-mapping-because-zones-use-it": "Túto skupinu senzorov nemôžete vymazať, pretože ju používa aspoň jedna zóna.",
              invalid_source: "Neplatný zdroj",
              source_does_not_exist: "Zdroj neexistuje. Zadaj platný zdroj, napríklad 'sensor.mysensor'."
            },
            items: {
              dewpoint: "Rosný bod",
              evapotranspiration: "Evapotranspirácia",
              humidity: "Vlhkosť",
              "maximum temperature": "Maximálna teplota",
              "minimum temperature": "Minimálna teplota",
              precipitation: "Úhrn zrážok",
              pressure: "Tlak",
              "solar radiation": "Slnečné žiarenie",
              temperature: "Teplota",
              windspeed: "Rýchlosť vetra",
              "current precipitation": "Aktuálne zrážky"
            },
            pressure_types: {
              absolute: "absolútne",
              relative: "relatítne"
            },
            "pressure-type": "Tlak je",
            "sensor-aggregate-of-sensor-values-to-calculate": "hodnôt snímača na výpočet trvania",
            "sensor-aggregate-use-the": "Použiť",
            "sensor-entity": "Entita snímača",
            static_value: "Hodnota",
            "input-units": "Vstup poskytuje hodnoty v",
            source: "Zdroj",
            sources: {
              none: "Nie je",
              weather_service: "Poveternostná služba",
              sensor: "Snímač",
              static: "Statická hodnota"
            }
          }
        },
        description: "Pridajte jednu alebo viac skupín senzorov, ktoré získavajú údaje o počasí z Weather service, zo senzorov alebo ich kombinácie. Každú skupinu senzorov môžete namapovať na jednu alebo viac zón",
        labels: {
          "mapping-name": "Názov"
        },
        no_items: "Zatiaľ nie je definovaná žiadna skupina senzorov.",
        title: "Skupiny senzorov",
        "weather-records": {
          title: "Záznamy o počasí",
          timestamp: "Čas",
          temperature: "Tepl.",
          humidity: "Humidity",
          precipitation: "Zrážky",
          "retrieval-time": "Získané",
          "no-data": "Pre túto skupinu senzorov nie sú dostupné žiadne poveternostné údaje",
          dewpoint: "Rosa",
          wind: "Vietor",
          pressure: "Tlak"
        }
      },
      modules: {
        cards: {
          "add-module": {
            actions: {
              add: "Pridať modul"
            },
            header: "Pridať modul"
          },
          module: {
            errors: {
              "cannot-delete-module-because-zones-use-it": "Tento modul nemôžete vymazať, pretože ho používa aspoň jedna zóna."
            },
            labels: {
              configuration: "Konfigurácia",
              required: "označuje povinné pole"
            },
            "translated-options": {
              DontEstimate: "Bez odhadu",
              EstimateFromSunHours: "Odhad zo slnečných hodín",
              EstimateFromTemp: "Odhad z teploty",
              EstimateFromSunHoursAndTemperature: "Odhad z priemeru hodín slnečného svitu a teploty"
            }
          }
        },
        description: "Pridajte jeden alebo viac modulov, ktoré vypočítavajú trvanie zavlažovania. Každý modul sa dodáva s vlastnou konfiguráciou a možno ho použiť na výpočet trvania pre jednu alebo viac zón.",
        no_items: "Zatiaľ nie sú definované žiadne moduly.",
        title: "Moduly"
      },
      zones: {
        actions: {
          add: "Pridať",
          calculate: "Vypočítať",
          information: "Informácia",
          update: "Aktualizovať",
          "reset-bucket": "Resetovať vedro",
          "view-weather-info": "Zobraziť počasie",
          "view-weather-info-message": "Poveternostné údaje dostupné pre",
          "view-watering-calendar": "Kalendár zavlažovania",
          irrigate_all: "Zavlažiť všetky zóny teraz",
          open_settings: "Upraviť nastavenia"
        },
        cards: {
          "add-zone": {
            actions: {
              add: "Pridať zónu"
            },
            header: "Pridať zónu"
          },
          "zone-actions": {
            actions: {
              "calculate-all": "Prepočítať trvania",
              "update-all": "Obnoviť údaje o počasí",
              "reset-all-buckets": "Obnovte všetky vedrá",
              "clear-all-weatherdata": "Vymazať všetky údaje o počasí"
            },
            header: "Akcie vo všetkých zónach"
          }
        },
        description: "Tu špecifikujte jednu alebo viac zavlažovacích zón. Trvanie zavlažovania sa vypočíta pre zónu v závislosti od veľkosti, výkonu, stavu, modulu a skupiny senzorov.",
        labels: {
          bucket: "Vedro",
          duration: "Trvanie",
          "lead-time": "Dodacia lehota",
          mapping: "Skupina senzorov",
          "maximum-duration": "Maximálne trvanie",
          multiplier: "Násobiteľ",
          name: "Názov",
          size: "Veľkosť",
          state: "Stav",
          states: {
            automatic: "Automatický",
            disabled: "Zakázaný",
            manual: "Manuány"
          },
          throughput: "Priepustnosť",
          "maximum-bucket": "Maximálne vedro",
          last_calculated: "Naposledy vypočítané",
          "data-last-updated": "Údaje boli naposledy aktualizované",
          "data-number-of-data-points": "Počet údajových bodov",
          drainage_rate: "Miera odvodnenia",
          linked_entity: "Prepojená entita prepínača/ventilu",
          linked_entity_placeholder: "napr. switch.zahradny_ventil",
          irrigate_now: "Zavlažiť teraz",
          bucket_threshold: "Minimálny deficit pre závlahu",
          flow_sensor: "Senzor prietokomera (voliteľné)",
          flow_sensor_placeholder: "napr. sensor.zone_flow_rate"
        },
        no_items: "Zatiaľ nie sú definované žiadne zóny.",
        title: "Zóny",
        confirm_irrigate: {
          title: "Spustiť zavlažovanie?",
          body: "Týmto sa teraz otvoria prepojené ventily a obídu sa všetky podmienky preskočenia (dážď, teplota, minimálny počet dní medzi zavlažovaniami).",
          all_linked_zones: "Všetky prepojené zóny",
          toast_started: "Zavlažovanie spustené",
          toast_failed: "Zavlažovanie zlyhalo"
        },
        status: {
          decision_disabled: "Vypnuté — táto zóna sa nebude automaticky zavlažovať.",
          decision_water: "Potrebné zavlažovanie: približne {duration} pri ďalšom plánovanom spustení.",
          decision_water_at: "Zavlaží približne {duration} o {time}.",
          decision_water_skip: "Deficit ~{duration}, ale ďalšie spustenie sa pravdepodobne preskočí ({reason}).",
          decision_water_no_schedule: "Deficit ~{duration} — túto zónu nezavlažuje žiadny plán; spustite ju manuálne.",
          decision_no_water: "Momentálne nie je potrebné zavlažovanie — pôda má dostatok vlhkosti.",
          decision_unknown: "Ešte nevypočítané — stlačte Aktualizovať a potom Vypočítať na kontrolu.",
          last_checked: "Naposledy skontrolované",
          never: "nikdy",
          saved: "Uložené",
          estimate_now: "Teraz",
          estimate_tag: "odh.",
          estimate_method: {
            hourly: "Živý odhad z hodinového počasia od posledného výpočtu",
            proxy: "Odhad rozložený z dnešnej predpovede od posledného výpočtu"
          }
        },
        help: {
          bucket: "Bilancia vlhkosti pôdy (vedro). Záporná hodnota znamená, že pôda je suchá a zóna potrebuje vodu.",
          calculate: "Vypočíta dĺžku zavlažovania z najnovších údajov. Spustite po Aktualizovať.",
          update: "Načíta najnovšie meteorologické/senzorové údaje pre túto zónu.",
          irrigate_link_entity: "Priraďte v nastaveniach tejto zóny spínač/ventil, aby ste umožnili manuálne zavlažovanie.",
          irrigate_all: "Okamžite otvorí prepojené ventily pre každú zónu s deficitom. Podmienky preskočenia (dážď, vietor, teplota) sa ignorujú.",
          update_all: "Zhromaždí najnovšie meteorologické/senzorové údaje pre všetky zóny. Samo o sebe nemení trvania.",
          calculate_all: "Prepočíta trvanie zavlažovania každej automatickej zóny z doteraz zhromaždených údajov."
        },
        outlook: {
          next_run: "Ďalšie spustenie",
          no_schedule: "Žiadny automatický plán — zóny sa zavlažujú len keď ich spustíte.",
          setup_schedule: "Nastaviť plán",
          targets_all: "všetky zóny",
          targets_zones: "{count} zón",
          will_skip: "Ďalšie spustenie sa pravdepodobne preskočí",
          will_run: "Podmienky pre ďalšie spustenie vyzerajú priaznivo.",
          why_skipped: "Prečo?",
          provisional: "predpoveď — môže sa zmeniť",
          active_guards: "Aktívne podmienky",
          last_run: "Posledné spustenie",
          last_run_skipped: "preskočené",
          last_run_ran: "spustené",
          today: "dnes",
          tomorrow: "zajtra",
          actions: {
            irrigate: "Zavlažiť",
            calculate: "Prepočítať",
            update: "Obnoviť údaje"
          },
          checks: {
            precipitation: "Predpoveď dažďa",
            days_between: "Dni medzi zavlažovaniami",
            temperature: "Nízka teplota",
            wind: "Silný vietor",
            rain_sensor: "Senzor dažďa"
          },
          check_detail: {
            precipitation: "{observed} mm (≥ {threshold} mm)",
            days_between: "{observed}/{threshold} dní",
            temperature: "{observed}° (pod {threshold}°)",
            wind: "{observed} (nad {threshold})",
            rain_sensor: "{observed}"
          }
        },
        calendar: {
          no_data: "Pre túto zónu nie sú k dispozícii žiadne údaje kalendára zavlažovania.",
          error_prefix: "Chyba pri generovaní kalendára:",
          month: "Mesiac",
          et: "ET (mm)",
          precipitation: "Zrážky (mm)",
          watering: "Zavlažovanie (L)",
          avg_temp: "Priem. teplota (°C)",
          method_prefix: "Metóda:"
        },
        confirm_action: {
          reset_bucket_title: "Vynulovať vedro tejto zóny?",
          reset_bucket_body: "Týmto sa vedro nastaví späť na 0 a zruší sa nahromadená bilancia vlhkosti pre túto zónu.",
          reset_all_buckets_title: "Vynulovať všetky vedrá?",
          reset_all_buckets_body: "Týmto sa vedro každej zóny nastaví späť na 0 a zruší sa nahromadená bilancia vlhkosti. Výpočty zavlažovania začnú odznova pri ďalšej aktualizácii.",
          clear_weather_title: "Vymazať všetky meteorologické údaje?",
          clear_weather_body: "Týmto sa odstránia všetky zhromaždené meteorologické a senzorové záznamy pre všetky zóny. Zóny budú pred ďalším výpočtom potrebovať nové údaje."
        }
      },
      schedules: {
        title: "Plány",
        description: "Vytvorte opakujúce sa plány pre automatický výpočet, aktualizáciu alebo závlahu — bez automatizácií.",
        add: "Pridať plán",
        no_items: "Zatiaľ nie sú nakonfigurované žiadne plány. Kliknite na 'Pridať plán'.",
        zones_all: "Všetky zóny",
        zones_specific: "Konkrétne zóny",
        hours: "hodín",
        minutes: "min",
        types: {
          daily: "Denne",
          weekly: "Týždenne",
          monthly: "Mesačne",
          interval: "Každých N hodín",
          sunrise: "Východ slnka",
          sunset: "Západ slnka",
          solar_azimuth: "Slnečný azimut"
        },
        actions: {
          calculate: "Vypočítať (aktualizovať dobu závlahy)",
          update: "Aktualizovať (zbierať meteorologické dáta)",
          irrigate: "Zavlažiť (priamo ovládať ventily)"
        },
        days: {
          monday: "Po",
          tuesday: "Ut",
          wednesday: "St",
          thursday: "Št",
          friday: "Pi",
          saturday: "So",
          sunday: "Ne"
        },
        fields: {
          name: "Názov",
          type: "Typ plánu",
          enabled: "Povolené",
          time: "Čas (HH:MM)",
          days_of_week: "Dni v týždni",
          day_of_month: "Deň v mesiaci",
          interval_hours: "Interval",
          action: "Akcia",
          zones: "Zóny",
          start_date: "Dátum začiatku (voliteľné)",
          end_date: "Dátum konca (voliteľné)",
          offset_minutes: "Posun od východu/západu slnka",
          account_for_duration: "Spustiť skoro, aby závlaha skončila v cieľovom čase",
          azimuth_angle: "Uhol slnečného azimutu",
          time_anchor: "Čas označuje"
        },
        dialog: {
          add_title: "Pridať plán",
          edit_title: "Upraviť plán"
        },
        time_anchor: {
          start: "Začiatok zavlažovania",
          finish: "Koniec zavlažovania"
        }
      },
      info: {
        title: "Info",
        description: "Zobraziť informácie o ďalšej závlahe a stave systému.",
        "configuration-not-available": "Konfigurácia nie je k dispozícii.",
        cards: {
          "zone-bucket-values": {
            title: "Hodnoty zásobníka zóny a trvanie",
            labels: {
              bucket: "Zásobník",
              duration: "Trvanie"
            },
            "no-zones": "Žiadne zóny nie sú nakonfigurované"
          },
          "next-irrigation": {
            title: "Ďalšia závlaha",
            labels: {
              "next-start": "Ďalší štart",
              duration: "Trvanie",
              zones: "Zóny"
            },
            "no-data": "Žiadne dáta k dispozícii"
          },
          "irrigation-reason": {
            title: "Dôvod závlahy",
            labels: {
              reason: "Dôvod",
              sunrise: "Východ slnka",
              "total-duration": "Celková doba",
              explanation: "Vysvetlenie"
            },
            "no-data": "Žiadne dáta k dispozícii"
          },
          irrigate_now: {
            title: "Zavlažiť teraz",
            description: "Okamžite spustiť závlahu pre všetky zóny s prepojenou entitou. Podmienky preskočenia sú ignorované.",
            button_all: "Spustiť všetky zóny teraz",
            no_linked_zones: "Žiadna zóna nemá prepojenú entitu prepínača/ventilu s vypočítanou dobou."
          }
        }
      },
      setup: {
        title: "Nastavenie"
      }
    },
    $a = "Inteligentné zavlažovanie",
    Va = {
      title: "Súradnice Polohy",
      description: "Nakonfigurujte súradnice polohy pre získavanie meteorologických údajov. Môžete použiť manuálne súradnice odlišné od vašej polohy Home Assistant ak je to potrebné.",
      manual_enabled: "Použiť manuálne súradnice",
      use_ha_location: "Použiť polohu Home Assistant",
      latitude: "Zemepisná šírka (desatinné stupne)",
      longitude: "Zemepisná dĺžka (desatinné stupne)",
      elevation: "Nadmorská výška (metre nad morom)",
      current_ha_coords: "Aktuálne súradnice Home Assistant"
    },
    Wa = {
      title: "Dni medzi závlahami",
      description: "Nakonfigurujte minimálny počet dní medzi záhradnými udalosťami.",
      label: "Minimálne dni medzi závlahami",
      help_text: "Nastavte na 0 pre deaktiváciu. Podporované sú hodnoty 1-365 dní."
    },
    Fa = {
      title: "Spúšťače spustenia zavlažovania",
      description: "Nakonfiguruj, kedy sa má spustiť zavlažovanie na základe slnečných udalostí. Môžeš pridať viacero spúšťačov pre rôzne harmonogramy. Pri spúšťačoch východu slnka sa pri posune 0 automaticky použije celkové trvanie všetkých povolených zón.",
      add_trigger: "Pridať spúšťač",
      edit_trigger: "Upraviť spúšťač",
      delete_trigger: "Odstrániť spúšťač",
      trigger_types: {
        sunrise: "Východ slnka",
        sunset: "Západ slnka",
        solar_azimuth: "Slnečný azimut"
      },
      fields: {
        name: {
          name: "Názov spúšťača",
          description: "Popisný názov na identifikáciu tohto spúšťača"
        },
        type: {
          name: "Typ spúšťača",
          description: "Typ slnečnej udalosti, na ktorú sa má spustiť"
        },
        enabled: {
          name: "Povolené",
          description: "Či je tento spúšťač momentálne aktívny"
        },
        offset_minutes: {
          name: "Posun (minúty)",
          description: "Minúty pred (-) alebo po (+) slnečnej udalosti. Pri spúšťačoch východu slnka použi 0 pre automatické načasovanie na základe celkového trvania zón."
        },
        azimuth_angle: {
          name: "Uhol azimutu (stupne)",
          description: "Uhol slnečného azimutu v stupňoch, kde 0=sever, 90=východ, 180=juh, 270=západ"
        },
        account_for_duration: {
          name: "Zohľadniť trvanie",
          description: "Ak je povolené, zavlažovanie sa spustí dostatočne skoro, aby skončilo v zadanom čase. Ak je zakázané, zavlažovanie sa spustí presne v zadanom čase."
        }
      },
      dialog: {
        add_title: "Pridať spúšťač spustenia zavlažovania",
        edit_title: "Upraviť spúšťač spustenia zavlažovania",
        cancel: "Zrušiť",
        save: "Uložiť",
        delete: "Odstrániť"
      },
      no_triggers: "Nie sú nakonfigurované žiadne spúšťače spustenia zavlažovania. Systém použije predvolené správanie (východ slnka s celkovým trvaním zón). Pridaj spúšťače na prispôsobenie spustenia zavlažovania.",
      offset_auto: "Automaticky (vypočítané z celkového trvania zón)",
      confirm_delete: "Naozaj chceš odstrániť spúšťač '{name}'?",
      validation: {
        name_required: "Názov spúšťača je povinný",
        azimuth_invalid: "Uhol azimutu musí byť platné číslo"
      },
      help: {
        sunrise_offset: "Pri spúšťačoch východu slnka: použi záporné hodnoty na spustenie pred východom slnka, kladné na spustenie po ňom. Nastav na 0 na automatické spustenie dostatočne skoro, aby sa všetky zóny dokončili pred východom slnka.",
        sunset_offset: "Pri spúšťačoch západu slnka: použi záporné hodnoty na spustenie pred západom slnka, kladné na spustenie po západe slnka.",
        azimuth_explanation: "Slnečný azimut je kompasový smer slnka. 0°=sever, 90°=východ, 180°=juh, 270°=západ. Môžeš zadať ľubovoľnú hodnotu uhla (napr. 450° = 90°, -30° = 330°). Použi to na spustenie zavlažovania, keď slnko dosiahne konkrétnu polohu.",
        multiple_triggers: "Môžeš nakonfigurovať viacero spúšťačov. Každý povolený spúšťač naplánuje spustenie zavlažovania nezávisle."
      }
    },
    qa = {
      title: "Podmienky preskočenia",
      description: "Automaticky preskočiť závlahu pri nepriaznivých podmienkach. Kontroly zrážok, teploty a vetra vyžadujú počasiovú službu.",
      threshold_label: "Prah zrážok",
      threshold_description: "Minimálne celkové predpokladané zrážky (v mm) v okne predpovede na preskočenie závlahy.",
      lookahead_label: "Okno predpovede (dni)",
      lookahead_help: "Koľko nasledujúcich dní predpovede sa spočíta pri kontrole dažďa. Predpoveď začína zajtrajškom (dnešok je vylúčený), takže 1 = iba nasledujúci deň, 2 = nasledujúce dva dni atď.",
      temp_section_title: "Preskočiť pri nízkej teplote",
      temp_threshold_label: "Preskočiť ak teplota pod",
      wind_section_title: "Preskočiť pri silnom vetre",
      wind_threshold_label: "Preskočiť ak rýchlosť vetra nad",
      rain_sensor_section_title: "Podmienka dažďového senzora",
      rain_sensor_label: "Entita dažďového senzora (voliteľné)",
      rain_sensor_placeholder: "napr. binary_sensor.dazd"
    },
    Za = {
      title: "Poradie zón",
      description: "Keď viacero zón potrebuje závlahu, vyberte, či prebiehajú súčasne alebo jedna po druhej. V sekvenčnom režime systém čaká, kým každá zóna skončí, pred spustením ďalšej.",
      parallel: "Paralelne (všetky zóny súčasne)",
      sequential: "Sekvenčne (jedna zóna naraz)",
      rotating: "Rotujúce (zóny sa striedajú)",
      max_consecutive_duration_label: "Max. súvislý čas behu na zónu",
      max_consecutive_duration_unit: "minúty",
      min_absorption_time_label: "Min. čas vsiaknutia medzi cyklami",
      min_absorption_time_unit: "minúty (0 = vypnuté)"
    },
    Ga = {
      title: "Poveternostná služba",
      description: "Nakonfiguruj, ktorá poveternostná služba sa použije na výpočty ET a podmienky preskočenia.",
      enabled_label: "Povoliť poveternostnú službu",
      service_label: "Poveternostná služba",
      api_key_label: "API kľúč",
      api_key_placeholder: "Nechaj prázdne na zachovanie existujúceho kľúča",
      api_key_configured: "API kľúč je nakonfigurovaný",
      api_key_not_configured: "Nie je nakonfigurovaný žiadny API kľúč",
      api_key_help: "API kľúč od tebou zvoleného poskytovateľa poveternostnej služby. Open-Meteo nevyžaduje kľúč. OpenWeatherMap aj Pirate Weather ponúkajú bezplatné úrovne.",
      no_api_key_needed: "Open-Meteo je bezplatná služba a nevyžaduje API kľúč.",
      save_button: "Uložiť nastavenia počasia",
      saved: "Nastavenia počasia uložené",
      openmeteo: "Open-Meteo (zdarma, bez kľúča)",
      test_button: "Otestovať pripojenie",
      test_button_testing: "Testuje sa…",
      test_success: "✓ Pripojenie úspešné",
      test_error_invalid_auth: "✗ Neplatný API kľúč — skontroluj, či je správny a aktívny",
      test_error_cannot_connect: "✗ Nedá sa pripojiť — skontroluj svoje internetové pripojenie",
      test_error_no_service: "✗ Najprv vyber poveternostnú službu",
      test_error_unknown: "✗ Test zlyhal — neznáma chyba",
      owm: "OpenWeatherMap",
      pw: "Pirate Weather"
    },
    Ya = {
      zone_size: "Celková zavlažovaná plocha tejto zóny. Používa sa spolu s prietokom na výpočet množstva vody aplikovaného počas jedného cyklu.",
      zone_throughput: "Celkový prietok vody tvojho zavlažovacieho systému pre túto zónu (litre/min v metrickej sústave, gal/min v imperiálnej). Skontroluj technický list svojich postrekovačov alebo zmeraj, ako dlho trvá naplnenie nádoby známeho objemu.",
      zone_drainage_rate: "Ako rýchlo prebytočná voda odteká z pôdy, keď je vedro plné. Typicky: trávnik 50 mm/h, piesočnatá pôda 100+ mm/h, íl 10 mm/h.",
      zone_bucket: "Aktuálny deficit (záporný) alebo prebytok (kladný) vody pre túto zónu. Zavlažovanie sa spustí, keď vedro klesne pod prahovú hodnotu.",
      zone_maximum_bucket: "Maximálny prebytok vlhkosti, ktorý zóna dokáže zadržať. Voda nad touto úrovňou sa považuje za odtok. Typická hodnota: 50 mm.",
      zone_bucket_threshold: "Zavlažovanie sa spustí, keď vedro klesne pod túto hodnotu. Musí byť 0 alebo záporná. 0 znamená zavlažovať vždy, keď je deficit.",
      zone_multiplier: "Mierka aplikovaná na vypočítané trvanie. Nad 1,0 zvyšuje, pod 1,0 znižuje. Užitočné na jemné doladenie bez zmeny fyzických meraní.",
      zone_lead_time: "Sekundy navyše pred spustením zavlažovania. Použi to na zahriatie čerpadla alebo natlakovanie systému.",
      zone_maximum_duration: "Pevný horný limit pre jeden zavlažovací cyklus v sekundách. Zabraňuje nekontrolovanému zavlažovaniu. Predvolené: 3600 s (1 hodina).",
      zone_linked_entity: "Entita prepínača alebo ventilu v HA, ktorá riadi prietok vody pre túto zónu. Táto entita sa zapne, keď beží zavlažovanie.",
      zone_flow_sensor: "Voliteľný senzor merajúci skutočný prietok vody. Používa sa len na vykazovanie — neovplyvňuje výpočet trvania.",
      general_autoupdatedelay: "Sekundy čakania po spustení HA pred prvým získaním poveternostných údajov. Umožňuje ostatným integráciám sa najprv inicializovať.",
      general_sensor_debounce: "Minimálny odstup v milisekundách medzi načítaniami senzora na odfiltrovanie šumu z rýchlo sa meniacich senzorov.",
      general_calctime: "Čas dňa, kedy sa trvania zavlažovania prepočítajú zo získaných poveternostných údajov. Formát: HH:MM (24-hodinový).",
      general_cleardatatime: "Čas dňa, kedy sa odstránia staré poveternostné údaje. Musí byť nastavený neskôr ako čas výpočtu.",
      general_days_between: "Minimálny počet dní medzi zavlažovaniami tej istej zóny. Nastav na 0 na vypnutie (zavlažovať vždy, keď je deficit).",
      general_autoupdateinterval: "Ako často sa získavajú poveternostné údaje. Zvoľ hodnotu, ktorá vyvažuje čerstvé údaje a limity API.",
      general_precipitation_threshold: "Zavlažovanie sa preskočí, ak celkové predpovedané zrážky v okne predpovede prekročia toto množstvo.",
      general_temp_threshold: "Zavlažovanie sa preskočí, ak je aktuálna teplota pod touto hodnotou (napr. na zabránenie poškodeniu mrazom).",
      general_wind_threshold: "Zavlažovanie sa preskočí, ak rýchlosť vetra prekročí túto hodnotu (silný vietor znižuje účinnosť a spôsobuje úlet)."
    },
    Ka = {
      title: "Sprievodca nastavením",
      open_button: "Sprievodca nastavením",
      close: "Zavrieť",
      next: "Ďalej",
      back: "Späť",
      finish: "Dokončiť",
      skip_step: "Preskočiť tento krok",
      step_indicator: "Krok {current} z {total}",
      setup_complete_banner: "Nastavenie nie je dokončené. Spusti sprievodcu a začni.",
      open_wizard: "Otvoriť sprievodcu",
      steps: {
        welcome: {
          title: "Vitaj v Smart Irrigation",
          intro: "Tento sprievodca ťa prevedie štyrmi krokmi potrebnými na to, aby tvoja prvá zóna automaticky zavlažovala.",
          step1_label: "Poveternostná služba — odkiaľ získať poveternostné údaje",
          step2_label: "Výpočtový modul — ako sa počíta trvanie zavlažovania",
          step3_label: "Skupina senzorov — ktoré zdroje údajov použiť",
          step4_label: "Zóna — tvoja prvá zavlažovacia zóna",
          tip: "Ktorýkoľvek krok môžeš preskočiť a nakonfigurovať ho neskôr na karte Nastavenie."
        },
        weather: {
          title: "Poveternostná služba",
          description: "Vyber, ako sa získavajú poveternostné údaje. Open-Meteo je zadarmo a nevyžaduje API kľúč — pre väčšinu používateľov najjednoduchšia voľba."
        },
        module: {
          title: "Výpočtový modul",
          description: "Modul vypočíta, ako dlho zavlažovať, na základe evapotranspirácie (ET). Modul PyETO (metóda FAO-56) sa odporúča pre väčšinu používateľov.",
          pick_label: "Vyber typ modulu",
          no_modules: "Nie sú dostupné žiadne typy modulov."
        },
        mapping: {
          title: "Skupina senzorov",
          description: "Skupina senzorov prepája každú poveternostnú premennú s dátovým zdrojom. Nastav kľúčové premenné nižšie — jednotlivé priradenia senzorov môžeš spresniť neskôr na karte Nastavenie → Skupiny senzorov.",
          name_label: "Názov skupiny senzorov",
          source_label: "Zdroj údajov pre",
          use_weather_service: "Poveternostná služba",
          use_sensor: "Senzor",
          use_static: "Statická hodnota",
          use_none: "Žiadny / nepoužité"
        },
        zone: {
          title: "Prvá zóna",
          description: "Zóna je jedna zavlažovaná plocha (napr. trávnik, záhon). Nastav fyzické vlastnosti, aby systém mohol vypočítať správne trvanie zavlažovania.",
          name_label: "Názov zóny",
          size_label: "Plocha",
          throughput_label: "Prietok postrekovača",
          entity_label: "Prepojený prepínač alebo ventil",
          entity_placeholder: "napr. switch.garden_valve",
          module_label: "Výpočtový modul",
          mapping_label: "Skupina senzorov"
        },
        done: {
          title: "Nastavenie dokončené!",
          description: "Tvoja prvá zóna je pripravená. Smart Irrigation teraz bude automaticky počítať trvania zavlažovania na základe poveternostných údajov.",
          next_steps: "Čo môžeš urobiť ďalej:",
          tip1: "Prejdi na Zóny a zobraz vypočítané trvania a hodnoty vedra.",
          tip2: "Pridaj ďalšie zóny na karte Zóny.",
          tip3: "Doladi všetky nastavenia na karte Nastavenie.",
          go_zones: "Prejsť na Zóny",
          go_setup: "Prejsť na Nastavenie"
        }
      },
      stepper: {
        weather: "Počasie",
        module: "Modul",
        mapping: "Skupina senzorov",
        zone: "Zóna"
      },
      confirm_close: {
        body: "Zavrieť sprievodcu nastavením? Váš doterajší postup je uložený.",
        keep: "Pokračovať",
        close: "Zavrieť"
      }
    },
    Ja = {
      common: La,
      defaults: Ia,
      module: Ba,
      calcmodules: Ra,
      panels: Ua,
      title: $a,
      coordinate_config: Va,
      days_between_irrigation: Wa,
      irrigation_start_triggers: Fa,
      weather_skip: qa,
      zone_sequencing: Za,
      weather_service_config: Ga,
      field_help: Ya,
      wizard: Ka
    },
    Xa = Object.freeze({
      __proto__: null,
      common: La,
      defaults: Ia,
      module: Ba,
      calcmodules: Ra,
      panels: Ua,
      title: $a,
      coordinate_config: Va,
      days_between_irrigation: Wa,
      irrigation_start_triggers: Fa,
      weather_skip: qa,
      zone_sequencing: Za,
      weather_service_config: Ga,
      field_help: Ya,
      wizard: Ka,
      default: Ja
    });
  function Qa(e, t) {
    var a = t && t.cache ? t.cache : di,
      i = t && t.serializer ? t.serializer : ni;
    return (t && t.strategy ? t.strategy : ii)(e, {
      cache: a,
      serializer: i
    });
  }
  function ei(e, t, a, i) {
    var n,
      r = null == (n = i) || "number" == typeof n || "boolean" == typeof n ? i : a(i),
      o = t.get(r);
    return void 0 === o && (o = e.call(this, i), t.set(r, o)), o;
  }
  function ti(e, t, a) {
    var i = Array.prototype.slice.call(arguments, 3),
      n = a(i),
      r = t.get(n);
    return void 0 === r && (r = e.apply(this, i), t.set(n, r)), r;
  }
  function ai(e, t, a, i, n) {
    return a.bind(t, e, i, n);
  }
  function ii(e, t) {
    return ai(e, this, 1 === e.length ? ei : ti, t.cache.create(), t.serializer);
  }
  var ni = function () {
    return JSON.stringify(arguments);
  };
  function ri() {
    this.cache = Object.create(null);
  }
  ri.prototype.get = function (e) {
    return this.cache[e];
  }, ri.prototype.set = function (e, t) {
    this.cache[e] = t;
  };
  var oi,
    si,
    li,
    di = {
      create: function () {
        return new ri();
      }
    },
    ui = {
      variadic: function (e, t) {
        return ai(e, this, ti, t.cache.create(), t.serializer);
      },
      monadic: function (e, t) {
        return ai(e, this, ei, t.cache.create(), t.serializer);
      }
    };
  function ci(e) {
    return e.type === si.literal;
  }
  function pi(e) {
    return e.type === si.argument;
  }
  function mi(e) {
    return e.type === si.number;
  }
  function hi(e) {
    return e.type === si.date;
  }
  function gi(e) {
    return e.type === si.time;
  }
  function vi(e) {
    return e.type === si.select;
  }
  function _i(e) {
    return e.type === si.plural;
  }
  function fi(e) {
    return e.type === si.pound;
  }
  function bi(e) {
    return e.type === si.tag;
  }
  function ki(e) {
    return !(!e || "object" != typeof e || e.type !== li.number);
  }
  function yi(e) {
    return !(!e || "object" != typeof e || e.type !== li.dateTime);
  }
  !function (e) {
    e[e.EXPECT_ARGUMENT_CLOSING_BRACE = 1] = "EXPECT_ARGUMENT_CLOSING_BRACE", e[e.EMPTY_ARGUMENT = 2] = "EMPTY_ARGUMENT", e[e.MALFORMED_ARGUMENT = 3] = "MALFORMED_ARGUMENT", e[e.EXPECT_ARGUMENT_TYPE = 4] = "EXPECT_ARGUMENT_TYPE", e[e.INVALID_ARGUMENT_TYPE = 5] = "INVALID_ARGUMENT_TYPE", e[e.EXPECT_ARGUMENT_STYLE = 6] = "EXPECT_ARGUMENT_STYLE", e[e.INVALID_NUMBER_SKELETON = 7] = "INVALID_NUMBER_SKELETON", e[e.INVALID_DATE_TIME_SKELETON = 8] = "INVALID_DATE_TIME_SKELETON", e[e.EXPECT_NUMBER_SKELETON = 9] = "EXPECT_NUMBER_SKELETON", e[e.EXPECT_DATE_TIME_SKELETON = 10] = "EXPECT_DATE_TIME_SKELETON", e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE = 11] = "UNCLOSED_QUOTE_IN_ARGUMENT_STYLE", e[e.EXPECT_SELECT_ARGUMENT_OPTIONS = 12] = "EXPECT_SELECT_ARGUMENT_OPTIONS", e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE = 13] = "EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE", e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE = 14] = "INVALID_PLURAL_ARGUMENT_OFFSET_VALUE", e[e.EXPECT_SELECT_ARGUMENT_SELECTOR = 15] = "EXPECT_SELECT_ARGUMENT_SELECTOR", e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR = 16] = "EXPECT_PLURAL_ARGUMENT_SELECTOR", e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT = 17] = "EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT", e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT = 18] = "EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT", e[e.INVALID_PLURAL_ARGUMENT_SELECTOR = 19] = "INVALID_PLURAL_ARGUMENT_SELECTOR", e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR = 20] = "DUPLICATE_PLURAL_ARGUMENT_SELECTOR", e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR = 21] = "DUPLICATE_SELECT_ARGUMENT_SELECTOR", e[e.MISSING_OTHER_CLAUSE = 22] = "MISSING_OTHER_CLAUSE", e[e.INVALID_TAG = 23] = "INVALID_TAG", e[e.INVALID_TAG_NAME = 25] = "INVALID_TAG_NAME", e[e.UNMATCHED_CLOSING_TAG = 26] = "UNMATCHED_CLOSING_TAG", e[e.UNCLOSED_TAG = 27] = "UNCLOSED_TAG";
  }(oi || (oi = {})), function (e) {
    e[e.literal = 0] = "literal", e[e.argument = 1] = "argument", e[e.number = 2] = "number", e[e.date = 3] = "date", e[e.time = 4] = "time", e[e.select = 5] = "select", e[e.plural = 6] = "plural", e[e.pound = 7] = "pound", e[e.tag = 8] = "tag";
  }(si || (si = {})), function (e) {
    e[e.number = 0] = "number", e[e.dateTime = 1] = "dateTime";
  }(li || (li = {}));
  var zi = /[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/,
    wi = /(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;
  function Si(e) {
    var t = {};
    return e.replace(wi, function (e) {
      var a = e.length;
      switch (e[0]) {
        case "G":
          t.era = 4 === a ? "long" : 5 === a ? "narrow" : "short";
          break;
        case "y":
          t.year = 2 === a ? "2-digit" : "numeric";
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
          t.month = ["numeric", "2-digit", "short", "long", "narrow"][a - 1];
          break;
        case "w":
        case "W":
          throw new RangeError("`w/W` (week) patterns are not supported");
        case "d":
          t.day = ["numeric", "2-digit"][a - 1];
          break;
        case "D":
        case "F":
        case "g":
          throw new RangeError("`D/F/g` (day) patterns are not supported, use `d` instead");
        case "E":
          t.weekday = 4 === a ? "long" : 5 === a ? "narrow" : "short";
          break;
        case "e":
          if (a < 4) throw new RangeError("`e..eee` (weekday) patterns are not supported");
          t.weekday = ["short", "long", "narrow", "short"][a - 4];
          break;
        case "c":
          if (a < 4) throw new RangeError("`c..ccc` (weekday) patterns are not supported");
          t.weekday = ["short", "long", "narrow", "short"][a - 4];
          break;
        case "a":
          t.hour12 = !0;
          break;
        case "b":
        case "B":
          throw new RangeError("`b/B` (period) patterns are not supported, use `a` instead");
        case "h":
          t.hourCycle = "h12", t.hour = ["numeric", "2-digit"][a - 1];
          break;
        case "H":
          t.hourCycle = "h23", t.hour = ["numeric", "2-digit"][a - 1];
          break;
        case "K":
          t.hourCycle = "h11", t.hour = ["numeric", "2-digit"][a - 1];
          break;
        case "k":
          t.hourCycle = "h24", t.hour = ["numeric", "2-digit"][a - 1];
          break;
        case "j":
        case "J":
        case "C":
          throw new RangeError("`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead");
        case "m":
          t.minute = ["numeric", "2-digit"][a - 1];
          break;
        case "s":
          t.second = ["numeric", "2-digit"][a - 1];
          break;
        case "S":
        case "A":
          throw new RangeError("`S/A` (second) patterns are not supported, use `s` instead");
        case "z":
          t.timeZoneName = a < 4 ? "short" : "long";
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
  var Ai = /[\t-\r \x85\u200E\u200F\u2028\u2029]/i;
  var xi = /^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g,
    Ei = /^(@+)?(\+|#+)?[rs]?$/g,
    Mi = /(\*)(0+)|(#+)(0+)|(0+)/g,
    Ti = /^(0+)$/;
  function Di(e) {
    var t = {};
    return "r" === e[e.length - 1] ? t.roundingPriority = "morePrecision" : "s" === e[e.length - 1] && (t.roundingPriority = "lessPrecision"), e.replace(Ei, function (e, a, i) {
      return "string" != typeof i ? (t.minimumSignificantDigits = a.length, t.maximumSignificantDigits = a.length) : "+" === i ? t.minimumSignificantDigits = a.length : "#" === a[0] ? t.maximumSignificantDigits = a.length : (t.minimumSignificantDigits = a.length, t.maximumSignificantDigits = a.length + ("string" == typeof i ? i.length : 0)), "";
    }), t;
  }
  function Pi(e) {
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
  function ji(e) {
    var t;
    if ("E" === e[0] && "E" === e[1] ? (t = {
      notation: "engineering"
    }, e = e.slice(2)) : "E" === e[0] && (t = {
      notation: "scientific"
    }, e = e.slice(1)), t) {
      var a = e.slice(0, 2);
      if ("+!" === a ? (t.signDisplay = "always", e = e.slice(2)) : "+?" === a && (t.signDisplay = "exceptZero", e = e.slice(2)), !Ti.test(e)) throw new Error("Malformed concise eng/scientific notation");
      t.minimumIntegerDigits = e.length;
    }
    return t;
  }
  function Ni(e) {
    var t = Pi(e);
    return t || {};
  }
  function Ci(e) {
    for (var t = {}, a = 0, n = e; a < n.length; a++) {
      var r = n[a];
      switch (r.stem) {
        case "percent":
        case "%":
          t.style = "percent";
          continue;
        case "%x100":
          t.style = "percent", t.scale = 100;
          continue;
        case "currency":
          t.style = "currency", t.currency = r.options[0];
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
          t.style = "unit", t.unit = r.options[0].replace(/^(.*?)-/, "");
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
          t = i(i(i({}, t), {
            notation: "scientific"
          }), r.options.reduce(function (e, t) {
            return i(i({}, e), Ni(t));
          }, {}));
          continue;
        case "engineering":
          t = i(i(i({}, t), {
            notation: "engineering"
          }), r.options.reduce(function (e, t) {
            return i(i({}, e), Ni(t));
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
          t.scale = parseFloat(r.options[0]);
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
          if (r.options.length > 1) throw new RangeError("integer-width stems only accept a single optional option");
          r.options[0].replace(Mi, function (e, a, i, n, r, o) {
            if (a) t.minimumIntegerDigits = i.length;else {
              if (n && r) throw new Error("We currently do not support maximum integer digits");
              if (o) throw new Error("We currently do not support exact integer digits");
            }
            return "";
          });
          continue;
      }
      if (Ti.test(r.stem)) t.minimumIntegerDigits = r.stem.length;else if (xi.test(r.stem)) {
        if (r.options.length > 1) throw new RangeError("Fraction-precision stems only accept a single optional option");
        r.stem.replace(xi, function (e, a, i, n, r, o) {
          return "*" === i ? t.minimumFractionDigits = a.length : n && "#" === n[0] ? t.maximumFractionDigits = n.length : r && o ? (t.minimumFractionDigits = r.length, t.maximumFractionDigits = r.length + o.length) : (t.minimumFractionDigits = a.length, t.maximumFractionDigits = a.length), "";
        });
        var o = r.options[0];
        "w" === o ? t = i(i({}, t), {
          trailingZeroDisplay: "stripIfInteger"
        }) : o && (t = i(i({}, t), Di(o)));
      } else if (Ei.test(r.stem)) t = i(i({}, t), Di(r.stem));else {
        var s = Pi(r.stem);
        s && (t = i(i({}, t), s));
        var l = ji(r.stem);
        l && (t = i(i({}, t), l));
      }
    }
    return t;
  }
  var Hi,
    Oi = {
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
  function Li(e) {
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
    var a,
      i = e.language;
    return "root" !== i && (a = e.maximize().region), (Oi[a || ""] || Oi[i || ""] || Oi["".concat(i, "-001")] || Oi["001"])[0];
  }
  var Ii = new RegExp("^".concat(zi.source, "*")),
    Bi = new RegExp("".concat(zi.source, "*$"));
  function Ri(e, t) {
    return {
      start: e,
      end: t
    };
  }
  var Ui = !!String.prototype.startsWith && "_a".startsWith("a", 1),
    $i = !!String.fromCodePoint,
    Vi = !!Object.fromEntries,
    Wi = !!String.prototype.codePointAt,
    Fi = !!String.prototype.trimStart,
    qi = !!String.prototype.trimEnd,
    Zi = !!Number.isSafeInteger ? Number.isSafeInteger : function (e) {
      return "number" == typeof e && isFinite(e) && Math.floor(e) === e && Math.abs(e) <= 9007199254740991;
    },
    Gi = !0;
  try {
    Gi = "a" === (null === (Hi = an("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu").exec("a")) || void 0 === Hi ? void 0 : Hi[0]);
  } catch (L) {
    Gi = !1;
  }
  var Yi,
    Ki = Ui ? function (e, t, a) {
      return e.startsWith(t, a);
    } : function (e, t, a) {
      return e.slice(a, a + t.length) === t;
    },
    Ji = $i ? String.fromCodePoint : function () {
      for (var e = [], t = 0; t < arguments.length; t++) e[t] = arguments[t];
      for (var a, i = "", n = e.length, r = 0; n > r;) {
        if ((a = e[r++]) > 1114111) throw RangeError(a + " is not a valid code point");
        i += a < 65536 ? String.fromCharCode(a) : String.fromCharCode(55296 + ((a -= 65536) >> 10), a % 1024 + 56320);
      }
      return i;
    },
    Xi = Vi ? Object.fromEntries : function (e) {
      for (var t = {}, a = 0, i = e; a < i.length; a++) {
        var n = i[a],
          r = n[0],
          o = n[1];
        t[r] = o;
      }
      return t;
    },
    Qi = Wi ? function (e, t) {
      return e.codePointAt(t);
    } : function (e, t) {
      var a = e.length;
      if (!(t < 0 || t >= a)) {
        var i,
          n = e.charCodeAt(t);
        return n < 55296 || n > 56319 || t + 1 === a || (i = e.charCodeAt(t + 1)) < 56320 || i > 57343 ? n : i - 56320 + (n - 55296 << 10) + 65536;
      }
    },
    en = Fi ? function (e) {
      return e.trimStart();
    } : function (e) {
      return e.replace(Ii, "");
    },
    tn = qi ? function (e) {
      return e.trimEnd();
    } : function (e) {
      return e.replace(Bi, "");
    };
  function an(e, t) {
    return new RegExp(e, t);
  }
  if (Gi) {
    var nn = an("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu");
    Yi = function (e, t) {
      var a;
      return nn.lastIndex = t, null !== (a = nn.exec(e)[1]) && void 0 !== a ? a : "";
    };
  } else Yi = function (e, t) {
    for (var a = [];;) {
      var i = Qi(e, t);
      if (void 0 === i || dn(i) || un(i)) break;
      a.push(i), t += i >= 65536 ? 2 : 1;
    }
    return Ji.apply(void 0, a);
  };
  var rn,
    on = function () {
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
      }, e.prototype.parseMessage = function (e, t, a) {
        for (var i = []; !this.isEOF();) {
          var n = this.char();
          if (123 === n) {
            if ((r = this.parseArgument(e, a)).err) return r;
            i.push(r.val);
          } else {
            if (125 === n && e > 0) break;
            if (35 !== n || "plural" !== t && "selectordinal" !== t) {
              if (60 === n && !this.ignoreTag && 47 === this.peek()) {
                if (a) break;
                return this.error(oi.UNMATCHED_CLOSING_TAG, Ri(this.clonePosition(), this.clonePosition()));
              }
              if (60 === n && !this.ignoreTag && sn(this.peek() || 0)) {
                if ((r = this.parseTag(e, t)).err) return r;
                i.push(r.val);
              } else {
                var r;
                if ((r = this.parseLiteral(e, t)).err) return r;
                i.push(r.val);
              }
            } else {
              var o = this.clonePosition();
              this.bump(), i.push({
                type: si.pound,
                location: Ri(o, this.clonePosition())
              });
            }
          }
        }
        return {
          val: i,
          err: null
        };
      }, e.prototype.parseTag = function (e, t) {
        var a = this.clonePosition();
        this.bump();
        var i = this.parseTagName();
        if (this.bumpSpace(), this.bumpIf("/>")) return {
          val: {
            type: si.literal,
            value: "<".concat(i, "/>"),
            location: Ri(a, this.clonePosition())
          },
          err: null
        };
        if (this.bumpIf(">")) {
          var n = this.parseMessage(e + 1, t, !0);
          if (n.err) return n;
          var r = n.val,
            o = this.clonePosition();
          if (this.bumpIf("</")) {
            if (this.isEOF() || !sn(this.char())) return this.error(oi.INVALID_TAG, Ri(o, this.clonePosition()));
            var s = this.clonePosition();
            return i !== this.parseTagName() ? this.error(oi.UNMATCHED_CLOSING_TAG, Ri(s, this.clonePosition())) : (this.bumpSpace(), this.bumpIf(">") ? {
              val: {
                type: si.tag,
                value: i,
                children: r,
                location: Ri(a, this.clonePosition())
              },
              err: null
            } : this.error(oi.INVALID_TAG, Ri(o, this.clonePosition())));
          }
          return this.error(oi.UNCLOSED_TAG, Ri(a, this.clonePosition()));
        }
        return this.error(oi.INVALID_TAG, Ri(a, this.clonePosition()));
      }, e.prototype.parseTagName = function () {
        var e = this.offset();
        for (this.bump(); !this.isEOF() && ln(this.char());) this.bump();
        return this.message.slice(e, this.offset());
      }, e.prototype.parseLiteral = function (e, t) {
        for (var a = this.clonePosition(), i = "";;) {
          var n = this.tryParseQuote(t);
          if (n) i += n;else {
            var r = this.tryParseUnquoted(e, t);
            if (r) i += r;else {
              var o = this.tryParseLeftAngleBracket();
              if (!o) break;
              i += o;
            }
          }
        }
        var s = Ri(a, this.clonePosition());
        return {
          val: {
            type: si.literal,
            value: i,
            location: s
          },
          err: null
        };
      }, e.prototype.tryParseLeftAngleBracket = function () {
        return this.isEOF() || 60 !== this.char() || !this.ignoreTag && (sn(e = this.peek() || 0) || 47 === e) ? null : (this.bump(), "<");
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
          var a = this.char();
          if (39 === a) {
            if (39 !== this.peek()) {
              this.bump();
              break;
            }
            t.push(39), this.bump();
          } else t.push(a);
          this.bump();
        }
        return Ji.apply(void 0, t);
      }, e.prototype.tryParseUnquoted = function (e, t) {
        if (this.isEOF()) return null;
        var a = this.char();
        return 60 === a || 123 === a || 35 === a && ("plural" === t || "selectordinal" === t) || 125 === a && e > 0 ? null : (this.bump(), Ji(a));
      }, e.prototype.parseArgument = function (e, t) {
        var a = this.clonePosition();
        if (this.bump(), this.bumpSpace(), this.isEOF()) return this.error(oi.EXPECT_ARGUMENT_CLOSING_BRACE, Ri(a, this.clonePosition()));
        if (125 === this.char()) return this.bump(), this.error(oi.EMPTY_ARGUMENT, Ri(a, this.clonePosition()));
        var i = this.parseIdentifierIfPossible().value;
        if (!i) return this.error(oi.MALFORMED_ARGUMENT, Ri(a, this.clonePosition()));
        if (this.bumpSpace(), this.isEOF()) return this.error(oi.EXPECT_ARGUMENT_CLOSING_BRACE, Ri(a, this.clonePosition()));
        switch (this.char()) {
          case 125:
            return this.bump(), {
              val: {
                type: si.argument,
                value: i,
                location: Ri(a, this.clonePosition())
              },
              err: null
            };
          case 44:
            return this.bump(), this.bumpSpace(), this.isEOF() ? this.error(oi.EXPECT_ARGUMENT_CLOSING_BRACE, Ri(a, this.clonePosition())) : this.parseArgumentOptions(e, t, i, a);
          default:
            return this.error(oi.MALFORMED_ARGUMENT, Ri(a, this.clonePosition()));
        }
      }, e.prototype.parseIdentifierIfPossible = function () {
        var e = this.clonePosition(),
          t = this.offset(),
          a = Yi(this.message, t),
          i = t + a.length;
        return this.bumpTo(i), {
          value: a,
          location: Ri(e, this.clonePosition())
        };
      }, e.prototype.parseArgumentOptions = function (e, t, a, n) {
        var r,
          o = this.clonePosition(),
          s = this.parseIdentifierIfPossible().value,
          l = this.clonePosition();
        switch (s) {
          case "":
            return this.error(oi.EXPECT_ARGUMENT_TYPE, Ri(o, l));
          case "number":
          case "date":
          case "time":
            this.bumpSpace();
            var d = null;
            if (this.bumpIf(",")) {
              this.bumpSpace();
              var u = this.clonePosition();
              if ((f = this.parseSimpleArgStyleIfPossible()).err) return f;
              if (0 === (h = tn(f.val)).length) return this.error(oi.EXPECT_ARGUMENT_STYLE, Ri(this.clonePosition(), this.clonePosition()));
              d = {
                style: h,
                styleLocation: Ri(u, this.clonePosition())
              };
            }
            if ((b = this.tryParseArgumentClose(n)).err) return b;
            var c = Ri(n, this.clonePosition());
            if (d && Ki(null == d ? void 0 : d.style, "::", 0)) {
              var p = en(d.style.slice(2));
              if ("number" === s) return (f = this.parseNumberSkeletonFromString(p, d.styleLocation)).err ? f : {
                val: {
                  type: si.number,
                  value: a,
                  location: c,
                  style: f.val
                },
                err: null
              };
              if (0 === p.length) return this.error(oi.EXPECT_DATE_TIME_SKELETON, c);
              var m = p;
              this.locale && (m = function (e, t) {
                for (var a = "", i = 0; i < e.length; i++) {
                  var n = e.charAt(i);
                  if ("j" === n) {
                    for (var r = 0; i + 1 < e.length && e.charAt(i + 1) === n;) r++, i++;
                    var o = 1 + (1 & r),
                      s = r < 2 ? 1 : 3 + (r >> 1),
                      l = Li(t);
                    for ("H" != l && "k" != l || (s = 0); s-- > 0;) a += "a";
                    for (; o-- > 0;) a = l + a;
                  } else a += "J" === n ? "H" : n;
                }
                return a;
              }(p, this.locale));
              var h = {
                type: li.dateTime,
                pattern: m,
                location: d.styleLocation,
                parsedOptions: this.shouldParseSkeletons ? Si(m) : {}
              };
              return {
                val: {
                  type: "date" === s ? si.date : si.time,
                  value: a,
                  location: c,
                  style: h
                },
                err: null
              };
            }
            return {
              val: {
                type: "number" === s ? si.number : "date" === s ? si.date : si.time,
                value: a,
                location: c,
                style: null !== (r = null == d ? void 0 : d.style) && void 0 !== r ? r : null
              },
              err: null
            };
          case "plural":
          case "selectordinal":
          case "select":
            var g = this.clonePosition();
            if (this.bumpSpace(), !this.bumpIf(",")) return this.error(oi.EXPECT_SELECT_ARGUMENT_OPTIONS, Ri(g, i({}, g)));
            this.bumpSpace();
            var v = this.parseIdentifierIfPossible(),
              _ = 0;
            if ("select" !== s && "offset" === v.value) {
              if (!this.bumpIf(":")) return this.error(oi.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE, Ri(this.clonePosition(), this.clonePosition()));
              var f;
              if (this.bumpSpace(), (f = this.tryParseDecimalInteger(oi.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE, oi.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE)).err) return f;
              this.bumpSpace(), v = this.parseIdentifierIfPossible(), _ = f.val;
            }
            var b,
              k = this.tryParsePluralOrSelectOptions(e, s, t, v);
            if (k.err) return k;
            if ((b = this.tryParseArgumentClose(n)).err) return b;
            var y = Ri(n, this.clonePosition());
            return "select" === s ? {
              val: {
                type: si.select,
                value: a,
                options: Xi(k.val),
                location: y
              },
              err: null
            } : {
              val: {
                type: si.plural,
                value: a,
                options: Xi(k.val),
                offset: _,
                pluralType: "plural" === s ? "cardinal" : "ordinal",
                location: y
              },
              err: null
            };
          default:
            return this.error(oi.INVALID_ARGUMENT_TYPE, Ri(o, l));
        }
      }, e.prototype.tryParseArgumentClose = function (e) {
        return this.isEOF() || 125 !== this.char() ? this.error(oi.EXPECT_ARGUMENT_CLOSING_BRACE, Ri(e, this.clonePosition())) : (this.bump(), {
          val: !0,
          err: null
        });
      }, e.prototype.parseSimpleArgStyleIfPossible = function () {
        for (var e = 0, t = this.clonePosition(); !this.isEOF();) {
          switch (this.char()) {
            case 39:
              this.bump();
              var a = this.clonePosition();
              if (!this.bumpUntil("'")) return this.error(oi.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE, Ri(a, this.clonePosition()));
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
        var a = [];
        try {
          a = function (e) {
            if (0 === e.length) throw new Error("Number skeleton cannot be empty");
            for (var t = e.split(Ai).filter(function (e) {
                return e.length > 0;
              }), a = [], i = 0, n = t; i < n.length; i++) {
              var r = n[i].split("/");
              if (0 === r.length) throw new Error("Invalid number skeleton");
              for (var o = r[0], s = r.slice(1), l = 0, d = s; l < d.length; l++) if (0 === d[l].length) throw new Error("Invalid number skeleton");
              a.push({
                stem: o,
                options: s
              });
            }
            return a;
          }(e);
        } catch (e) {
          return this.error(oi.INVALID_NUMBER_SKELETON, t);
        }
        return {
          val: {
            type: li.number,
            tokens: a,
            location: t,
            parsedOptions: this.shouldParseSkeletons ? Ci(a) : {}
          },
          err: null
        };
      }, e.prototype.tryParsePluralOrSelectOptions = function (e, t, a, i) {
        for (var n, r = !1, o = [], s = new Set(), l = i.value, d = i.location;;) {
          if (0 === l.length) {
            var u = this.clonePosition();
            if ("select" === t || !this.bumpIf("=")) break;
            var c = this.tryParseDecimalInteger(oi.EXPECT_PLURAL_ARGUMENT_SELECTOR, oi.INVALID_PLURAL_ARGUMENT_SELECTOR);
            if (c.err) return c;
            d = Ri(u, this.clonePosition()), l = this.message.slice(u.offset, this.offset());
          }
          if (s.has(l)) return this.error("select" === t ? oi.DUPLICATE_SELECT_ARGUMENT_SELECTOR : oi.DUPLICATE_PLURAL_ARGUMENT_SELECTOR, d);
          "other" === l && (r = !0), this.bumpSpace();
          var p = this.clonePosition();
          if (!this.bumpIf("{")) return this.error("select" === t ? oi.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT : oi.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT, Ri(this.clonePosition(), this.clonePosition()));
          var m = this.parseMessage(e + 1, t, a);
          if (m.err) return m;
          var h = this.tryParseArgumentClose(p);
          if (h.err) return h;
          o.push([l, {
            value: m.val,
            location: Ri(p, this.clonePosition())
          }]), s.add(l), this.bumpSpace(), l = (n = this.parseIdentifierIfPossible()).value, d = n.location;
        }
        return 0 === o.length ? this.error("select" === t ? oi.EXPECT_SELECT_ARGUMENT_SELECTOR : oi.EXPECT_PLURAL_ARGUMENT_SELECTOR, Ri(this.clonePosition(), this.clonePosition())) : this.requiresOtherClause && !r ? this.error(oi.MISSING_OTHER_CLAUSE, Ri(this.clonePosition(), this.clonePosition())) : {
          val: o,
          err: null
        };
      }, e.prototype.tryParseDecimalInteger = function (e, t) {
        var a = 1,
          i = this.clonePosition();
        this.bumpIf("+") || this.bumpIf("-") && (a = -1);
        for (var n = !1, r = 0; !this.isEOF();) {
          var o = this.char();
          if (!(o >= 48 && o <= 57)) break;
          n = !0, r = 10 * r + (o - 48), this.bump();
        }
        var s = Ri(i, this.clonePosition());
        return n ? Zi(r *= a) ? {
          val: r,
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
        var t = Qi(this.message, e);
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
        if (Ki(this.message, e, this.offset())) {
          for (var t = 0; t < e.length; t++) this.bump();
          return !0;
        }
        return !1;
      }, e.prototype.bumpUntil = function (e) {
        var t = this.offset(),
          a = this.message.indexOf(e, t);
        return a >= 0 ? (this.bumpTo(a), !0) : (this.bumpTo(this.message.length), !1);
      }, e.prototype.bumpTo = function (e) {
        if (this.offset() > e) throw Error("targetOffset ".concat(e, " must be greater than or equal to the current offset ").concat(this.offset()));
        for (e = Math.min(e, this.message.length);;) {
          var t = this.offset();
          if (t === e) break;
          if (t > e) throw Error("targetOffset ".concat(e, " is at invalid UTF-16 code unit boundary"));
          if (this.bump(), this.isEOF()) break;
        }
      }, e.prototype.bumpSpace = function () {
        for (; !this.isEOF() && dn(this.char());) this.bump();
      }, e.prototype.peek = function () {
        if (this.isEOF()) return null;
        var e = this.char(),
          t = this.offset(),
          a = this.message.charCodeAt(t + (e >= 65536 ? 2 : 1));
        return null != a ? a : null;
      }, e;
    }();
  function sn(e) {
    return e >= 97 && e <= 122 || e >= 65 && e <= 90;
  }
  function ln(e) {
    return 45 === e || 46 === e || e >= 48 && e <= 57 || 95 === e || e >= 97 && e <= 122 || e >= 65 && e <= 90 || 183 == e || e >= 192 && e <= 214 || e >= 216 && e <= 246 || e >= 248 && e <= 893 || e >= 895 && e <= 8191 || e >= 8204 && e <= 8205 || e >= 8255 && e <= 8256 || e >= 8304 && e <= 8591 || e >= 11264 && e <= 12271 || e >= 12289 && e <= 55295 || e >= 63744 && e <= 64975 || e >= 65008 && e <= 65533 || e >= 65536 && e <= 983039;
  }
  function dn(e) {
    return e >= 9 && e <= 13 || 32 === e || 133 === e || e >= 8206 && e <= 8207 || 8232 === e || 8233 === e;
  }
  function un(e) {
    return e >= 33 && e <= 35 || 36 === e || e >= 37 && e <= 39 || 40 === e || 41 === e || 42 === e || 43 === e || 44 === e || 45 === e || e >= 46 && e <= 47 || e >= 58 && e <= 59 || e >= 60 && e <= 62 || e >= 63 && e <= 64 || 91 === e || 92 === e || 93 === e || 94 === e || 96 === e || 123 === e || 124 === e || 125 === e || 126 === e || 161 === e || e >= 162 && e <= 165 || 166 === e || 167 === e || 169 === e || 171 === e || 172 === e || 174 === e || 176 === e || 177 === e || 182 === e || 187 === e || 191 === e || 215 === e || 247 === e || e >= 8208 && e <= 8213 || e >= 8214 && e <= 8215 || 8216 === e || 8217 === e || 8218 === e || e >= 8219 && e <= 8220 || 8221 === e || 8222 === e || 8223 === e || e >= 8224 && e <= 8231 || e >= 8240 && e <= 8248 || 8249 === e || 8250 === e || e >= 8251 && e <= 8254 || e >= 8257 && e <= 8259 || 8260 === e || 8261 === e || 8262 === e || e >= 8263 && e <= 8273 || 8274 === e || 8275 === e || e >= 8277 && e <= 8286 || e >= 8592 && e <= 8596 || e >= 8597 && e <= 8601 || e >= 8602 && e <= 8603 || e >= 8604 && e <= 8607 || 8608 === e || e >= 8609 && e <= 8610 || 8611 === e || e >= 8612 && e <= 8613 || 8614 === e || e >= 8615 && e <= 8621 || 8622 === e || e >= 8623 && e <= 8653 || e >= 8654 && e <= 8655 || e >= 8656 && e <= 8657 || 8658 === e || 8659 === e || 8660 === e || e >= 8661 && e <= 8691 || e >= 8692 && e <= 8959 || e >= 8960 && e <= 8967 || 8968 === e || 8969 === e || 8970 === e || 8971 === e || e >= 8972 && e <= 8991 || e >= 8992 && e <= 8993 || e >= 8994 && e <= 9e3 || 9001 === e || 9002 === e || e >= 9003 && e <= 9083 || 9084 === e || e >= 9085 && e <= 9114 || e >= 9115 && e <= 9139 || e >= 9140 && e <= 9179 || e >= 9180 && e <= 9185 || e >= 9186 && e <= 9254 || e >= 9255 && e <= 9279 || e >= 9280 && e <= 9290 || e >= 9291 && e <= 9311 || e >= 9472 && e <= 9654 || 9655 === e || e >= 9656 && e <= 9664 || 9665 === e || e >= 9666 && e <= 9719 || e >= 9720 && e <= 9727 || e >= 9728 && e <= 9838 || 9839 === e || e >= 9840 && e <= 10087 || 10088 === e || 10089 === e || 10090 === e || 10091 === e || 10092 === e || 10093 === e || 10094 === e || 10095 === e || 10096 === e || 10097 === e || 10098 === e || 10099 === e || 10100 === e || 10101 === e || e >= 10132 && e <= 10175 || e >= 10176 && e <= 10180 || 10181 === e || 10182 === e || e >= 10183 && e <= 10213 || 10214 === e || 10215 === e || 10216 === e || 10217 === e || 10218 === e || 10219 === e || 10220 === e || 10221 === e || 10222 === e || 10223 === e || e >= 10224 && e <= 10239 || e >= 10240 && e <= 10495 || e >= 10496 && e <= 10626 || 10627 === e || 10628 === e || 10629 === e || 10630 === e || 10631 === e || 10632 === e || 10633 === e || 10634 === e || 10635 === e || 10636 === e || 10637 === e || 10638 === e || 10639 === e || 10640 === e || 10641 === e || 10642 === e || 10643 === e || 10644 === e || 10645 === e || 10646 === e || 10647 === e || 10648 === e || e >= 10649 && e <= 10711 || 10712 === e || 10713 === e || 10714 === e || 10715 === e || e >= 10716 && e <= 10747 || 10748 === e || 10749 === e || e >= 10750 && e <= 11007 || e >= 11008 && e <= 11055 || e >= 11056 && e <= 11076 || e >= 11077 && e <= 11078 || e >= 11079 && e <= 11084 || e >= 11085 && e <= 11123 || e >= 11124 && e <= 11125 || e >= 11126 && e <= 11157 || 11158 === e || e >= 11159 && e <= 11263 || e >= 11776 && e <= 11777 || 11778 === e || 11779 === e || 11780 === e || 11781 === e || e >= 11782 && e <= 11784 || 11785 === e || 11786 === e || 11787 === e || 11788 === e || 11789 === e || e >= 11790 && e <= 11798 || 11799 === e || e >= 11800 && e <= 11801 || 11802 === e || 11803 === e || 11804 === e || 11805 === e || e >= 11806 && e <= 11807 || 11808 === e || 11809 === e || 11810 === e || 11811 === e || 11812 === e || 11813 === e || 11814 === e || 11815 === e || 11816 === e || 11817 === e || e >= 11818 && e <= 11822 || 11823 === e || e >= 11824 && e <= 11833 || e >= 11834 && e <= 11835 || e >= 11836 && e <= 11839 || 11840 === e || 11841 === e || 11842 === e || e >= 11843 && e <= 11855 || e >= 11856 && e <= 11857 || 11858 === e || e >= 11859 && e <= 11903 || e >= 12289 && e <= 12291 || 12296 === e || 12297 === e || 12298 === e || 12299 === e || 12300 === e || 12301 === e || 12302 === e || 12303 === e || 12304 === e || 12305 === e || e >= 12306 && e <= 12307 || 12308 === e || 12309 === e || 12310 === e || 12311 === e || 12312 === e || 12313 === e || 12314 === e || 12315 === e || 12316 === e || 12317 === e || e >= 12318 && e <= 12319 || 12320 === e || 12336 === e || 64830 === e || 64831 === e || e >= 65093 && e <= 65094;
  }
  function cn(e) {
    e.forEach(function (e) {
      if (delete e.location, vi(e) || _i(e)) for (var t in e.options) delete e.options[t].location, cn(e.options[t].value);else mi(e) && ki(e.style) || (hi(e) || gi(e)) && yi(e.style) ? delete e.style.location : bi(e) && cn(e.children);
    });
  }
  function pn(e, t) {
    void 0 === t && (t = {}), t = i({
      shouldParseSkeletons: !0,
      requiresOtherClause: !0
    }, t);
    var a = new on(e, t).parse();
    if (a.err) {
      var n = SyntaxError(oi[a.err.kind]);
      throw n.location = a.err.location, n.originalMessage = a.err.message, n;
    }
    return (null == t ? void 0 : t.captureLocation) || cn(a.val), a.val;
  }
  !function (e) {
    e.MISSING_VALUE = "MISSING_VALUE", e.INVALID_VALUE = "INVALID_VALUE", e.MISSING_INTL_API = "MISSING_INTL_API";
  }(rn || (rn = {}));
  var mn,
    hn = function (e) {
      function t(t, a, i) {
        var n = e.call(this, t) || this;
        return n.code = a, n.originalMessage = i, n;
      }
      return a(t, e), t.prototype.toString = function () {
        return "[formatjs Error: ".concat(this.code, "] ").concat(this.message);
      }, t;
    }(Error),
    gn = function (e) {
      function t(t, a, i, n) {
        return e.call(this, 'Invalid values for "'.concat(t, '": "').concat(a, '". Options are "').concat(Object.keys(i).join('", "'), '"'), rn.INVALID_VALUE, n) || this;
      }
      return a(t, e), t;
    }(hn),
    vn = function (e) {
      function t(t, a, i) {
        return e.call(this, 'Value for "'.concat(t, '" must be of type ').concat(a), rn.INVALID_VALUE, i) || this;
      }
      return a(t, e), t;
    }(hn),
    _n = function (e) {
      function t(t, a) {
        return e.call(this, 'The intl string context variable "'.concat(t, '" was not provided to the string "').concat(a, '"'), rn.MISSING_VALUE, a) || this;
      }
      return a(t, e), t;
    }(hn);
  function fn(e) {
    return "function" == typeof e;
  }
  function bn(e, t, a, i, n, r, o) {
    if (1 === e.length && ci(e[0])) return [{
      type: mn.literal,
      value: e[0].value
    }];
    for (var s = [], l = 0, d = e; l < d.length; l++) {
      var u = d[l];
      if (ci(u)) s.push({
        type: mn.literal,
        value: u.value
      });else if (fi(u)) "number" == typeof r && s.push({
        type: mn.literal,
        value: a.getNumberFormat(t).format(r)
      });else {
        var c = u.value;
        if (!n || !(c in n)) throw new _n(c, o);
        var p = n[c];
        if (pi(u)) p && "string" != typeof p && "number" != typeof p || (p = "string" == typeof p || "number" == typeof p ? String(p) : ""), s.push({
          type: "string" == typeof p ? mn.literal : mn.object,
          value: p
        });else if (hi(u)) {
          var m = "string" == typeof u.style ? i.date[u.style] : yi(u.style) ? u.style.parsedOptions : void 0;
          s.push({
            type: mn.literal,
            value: a.getDateTimeFormat(t, m).format(p)
          });
        } else if (gi(u)) {
          m = "string" == typeof u.style ? i.time[u.style] : yi(u.style) ? u.style.parsedOptions : i.time.medium;
          s.push({
            type: mn.literal,
            value: a.getDateTimeFormat(t, m).format(p)
          });
        } else if (mi(u)) {
          (m = "string" == typeof u.style ? i.number[u.style] : ki(u.style) ? u.style.parsedOptions : void 0) && m.scale && (p *= m.scale || 1), s.push({
            type: mn.literal,
            value: a.getNumberFormat(t, m).format(p)
          });
        } else {
          if (bi(u)) {
            var h = u.children,
              g = u.value,
              v = n[g];
            if (!fn(v)) throw new vn(g, "function", o);
            var _ = v(bn(h, t, a, i, n, r).map(function (e) {
              return e.value;
            }));
            Array.isArray(_) || (_ = [_]), s.push.apply(s, _.map(function (e) {
              return {
                type: "string" == typeof e ? mn.literal : mn.object,
                value: e
              };
            }));
          }
          if (vi(u)) {
            if (!(f = u.options[p] || u.options.other)) throw new gn(u.value, p, Object.keys(u.options), o);
            s.push.apply(s, bn(f.value, t, a, i, n));
          } else if (_i(u)) {
            var f;
            if (!(f = u.options["=".concat(p)])) {
              if (!Intl.PluralRules) throw new hn('Intl.PluralRules is not available in this environment.\nTry polyfilling it using "@formatjs/intl-pluralrules"\n', rn.MISSING_INTL_API, o);
              var b = a.getPluralRules(t, {
                type: u.pluralType
              }).select(p - (u.offset || 0));
              f = u.options[b] || u.options.other;
            }
            if (!f) throw new gn(u.value, p, Object.keys(u.options), o);
            s.push.apply(s, bn(f.value, t, a, i, n, p - (u.offset || 0)));
          } else ;
        }
      }
    }
    return function (e) {
      return e.length < 2 ? e : e.reduce(function (e, t) {
        var a = e[e.length - 1];
        return a && a.type === mn.literal && t.type === mn.literal ? a.value += t.value : e.push(t), e;
      }, []);
    }(s);
  }
  function kn(e, t) {
    return t ? Object.keys(e).reduce(function (a, n) {
      var r, o;
      return a[n] = (r = e[n], (o = t[n]) ? i(i(i({}, r || {}), o || {}), Object.keys(r).reduce(function (e, t) {
        return e[t] = i(i({}, r[t]), o[t] || {}), e;
      }, {})) : r), a;
    }, i({}, e)) : e;
  }
  function yn(e) {
    return {
      create: function () {
        return {
          get: function (t) {
            return e[t];
          },
          set: function (t, a) {
            e[t] = a;
          }
        };
      }
    };
  }
  !function (e) {
    e[e.literal = 0] = "literal", e[e.object = 1] = "object";
  }(mn || (mn = {}));
  var zn = function () {
      function e(t, a, n, o) {
        void 0 === a && (a = e.defaultLocale);
        var s,
          l = this;
        if (this.formatterCache = {
          number: {},
          dateTime: {},
          pluralRules: {}
        }, this.format = function (e) {
          var t = l.formatToParts(e);
          if (1 === t.length) return t[0].value;
          var a = t.reduce(function (e, t) {
            return e.length && t.type === mn.literal && "string" == typeof e[e.length - 1] ? e[e.length - 1] += t.value : e.push(t.value), e;
          }, []);
          return a.length <= 1 ? a[0] || "" : a;
        }, this.formatToParts = function (e) {
          return bn(l.ast, l.locales, l.formatters, l.formats, e, void 0, l.message);
        }, this.resolvedOptions = function () {
          var e;
          return {
            locale: (null === (e = l.resolvedLocale) || void 0 === e ? void 0 : e.toString()) || Intl.NumberFormat.supportedLocalesOf(l.locales)[0]
          };
        }, this.getAst = function () {
          return l.ast;
        }, this.locales = a, this.resolvedLocale = e.resolveLocale(a), "string" == typeof t) {
          if (this.message = t, !e.__parse) throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");
          var d = o || {};
          d.formatters;
          var u = function (e, t) {
            var a = {};
            for (var i in e) Object.prototype.hasOwnProperty.call(e, i) && t.indexOf(i) < 0 && (a[i] = e[i]);
            if (null != e && "function" == typeof Object.getOwnPropertySymbols) {
              var n = 0;
              for (i = Object.getOwnPropertySymbols(e); n < i.length; n++) t.indexOf(i[n]) < 0 && Object.prototype.propertyIsEnumerable.call(e, i[n]) && (a[i[n]] = e[i[n]]);
            }
            return a;
          }(d, ["formatters"]);
          this.ast = e.__parse(t, i(i({}, u), {
            locale: this.resolvedLocale
          }));
        } else this.ast = t;
        if (!Array.isArray(this.ast)) throw new TypeError("A message must be provided as a String or AST.");
        this.formats = kn(e.formats, n), this.formatters = o && o.formatters || (void 0 === (s = this.formatterCache) && (s = {
          number: {},
          dateTime: {},
          pluralRules: {}
        }), {
          getNumberFormat: Qa(function () {
            for (var e, t = [], a = 0; a < arguments.length; a++) t[a] = arguments[a];
            return new ((e = Intl.NumberFormat).bind.apply(e, r([void 0], t, !1)))();
          }, {
            cache: yn(s.number),
            strategy: ui.variadic
          }),
          getDateTimeFormat: Qa(function () {
            for (var e, t = [], a = 0; a < arguments.length; a++) t[a] = arguments[a];
            return new ((e = Intl.DateTimeFormat).bind.apply(e, r([void 0], t, !1)))();
          }, {
            cache: yn(s.dateTime),
            strategy: ui.variadic
          }),
          getPluralRules: Qa(function () {
            for (var e, t = [], a = 0; a < arguments.length; a++) t[a] = arguments[a];
            return new ((e = Intl.PluralRules).bind.apply(e, r([void 0], t, !1)))();
          }, {
            cache: yn(s.pluralRules),
            strategy: ui.variadic
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
      }, e.__parse = pn, e.formats = {
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
    wn = zn;
  const Sn = {
    de: Ge,
    en: ut,
    es: xt,
    fr: $t,
    it: na,
    nl: ka,
    no: Oa,
    sk: Xa
  };
  function An(e, t, ...a) {
    const i = t.replace(/['"]+/g, "");
    let n;
    try {
      n = e.split(".").reduce((e, t) => e[t], Sn[i]);
    } catch (t) {
      n = e.split(".").reduce((e, t) => e[t], Sn.en);
    }
    if (void 0 === n && (n = e.split(".").reduce((e, t) => e[t], Sn.en)), !a.length) return n;
    const r = {};
    for (let e = 0; e < a.length; e += 2) {
      let t = a[e];
      t = t.replace(/^{([^}]+)?}$/, "$1"), r[t] = a[e + 1];
    }
    try {
      return new wn(n, t).format(r);
    } catch (e) {
      return "Translation " + e;
    }
  }
  function xn(e, t) {
    switch (t) {
      case "drainage_rate":
        return e.units == ke ? V`${je("mm/h")}` : V`${je("in/h")}`;
      case "precipitation_threshold_mm":
      case ye:
        return e.units == ke ? V`${je("mm")}` : V`${je("in")}`;
      case "size":
        return e.units == ke ? V`${je("m<sup>2</sup>")}` : V`${je("sq ft")}`;
      case "throughput":
        return e.units == ke ? V`${je("l/minute")}` : V`${je("gal/minute")}`;
      default:
        return V``;
    }
  }
  const En = (e, t, a = !1) => {
    a ? history.replaceState(null, "", t) : history.pushState(null, "", t), function (e, t, a, i) {
      i = i || {}, a = null == a ? {} : a;
      var n = new Event(t, {
        bubbles: void 0 === i.bubbles || i.bubbles,
        cancelable: Boolean(i.cancelable),
        composed: void 0 === i.composed || i.composed
      });
      n.detail = a, e.dispatchEvent(n);
    }(window, "location-changed", {
      replace: a
    });
  };
  function Mn(e) {
    var t;
    if (!e) return "Unknown error";
    if ("string" == typeof e) return e;
    const a = e;
    return (null === (t = null == a ? void 0 : a.body) || void 0 === t ? void 0 : t.message) || (null == a ? void 0 : a.message) || (null == a ? void 0 : a.error) || JSON.stringify(e);
  }
  function Tn(e, t) {
    e.dispatchEvent(new CustomEvent("hass-notification", {
      detail: {
        message: t
      },
      bubbles: !0,
      composed: !0
    }));
  }
  function Dn(e, t, a, i) {
    var n;
    Tn(e, `${An(a, null !== (n = null == t ? void 0 : t.language) && void 0 !== n ? n : "en")}: ${Mn(i)}`);
  }
  const Pn = (e, ...t) => {
      let a = {
        page: e,
        params: {}
      };
      t.forEach(e => {
        "string" == typeof e ? a = Object.assign(Object.assign({}, a), {
          subpage: e
        }) : "params" in e ? a = Object.assign(Object.assign({}, a), {
          params: e.params
        }) : "filter" in e && (a = Object.assign(Object.assign({}, a), {
          filter: e.filter
        }));
      });
      const i = e => {
        let t = Object.keys(e);
        t = t.filter(t => e[t]), t.sort();
        let a = "";
        return t.forEach(t => {
          const i = e[t];
          a = a.length ? `${a}/${t}/${i}` : `${t}/${i}`;
        }), a;
      };
      let n = `/${be}/${a.page}`;
      return a.subpage && (n = `${n}/${a.subpage}`), i(a.params).length && (n = `${n}/${i(a.params)}`), a.filter && (n = `${n}/filter/${i(a.filter)}`), n;
    },
    jn = c`
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
  function Nn(e) {
    return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e;
  }
  function Cn(e) {
    throw new Error('Could not dynamically require "' + e + '". Please configure the dynamicRequireTargets or/and ignoreDynamicRequires option of @rollup/plugin-commonjs appropriately for this require call to work.');
  }
  c`
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
  var Hn,
    On = {
      exports: {}
    };
  var Ln = (Hn || (Hn = 1, function (e) {
      e.exports = function () {
        var t, a;
        function i() {
          return t.apply(null, arguments);
        }
        function n(e) {
          t = e;
        }
        function r(e) {
          return e instanceof Array || "[object Array]" === Object.prototype.toString.call(e);
        }
        function o(e) {
          return null != e && "[object Object]" === Object.prototype.toString.call(e);
        }
        function s(e, t) {
          return Object.prototype.hasOwnProperty.call(e, t);
        }
        function l(e) {
          if (Object.getOwnPropertyNames) return 0 === Object.getOwnPropertyNames(e).length;
          var t;
          for (t in e) if (s(e, t)) return !1;
          return !0;
        }
        function d(e) {
          return void 0 === e;
        }
        function u(e) {
          return "number" == typeof e || "[object Number]" === Object.prototype.toString.call(e);
        }
        function c(e) {
          return e instanceof Date || "[object Date]" === Object.prototype.toString.call(e);
        }
        function p(e, t) {
          var a,
            i = [],
            n = e.length;
          for (a = 0; a < n; ++a) i.push(t(e[a], a));
          return i;
        }
        function m(e, t) {
          for (var a in t) s(t, a) && (e[a] = t[a]);
          return s(t, "toString") && (e.toString = t.toString), s(t, "valueOf") && (e.valueOf = t.valueOf), e;
        }
        function h(e, t, a, i) {
          return Za(e, t, a, i, !0).utc();
        }
        function g() {
          return {
            empty: !1,
            unusedTokens: [],
            unusedInput: [],
            overflow: -2,
            charsLeftOver: 0,
            nullInput: !1,
            invalidEra: null,
            invalidMonth: null,
            invalidFormat: !1,
            userInvalidated: !1,
            iso: !1,
            parsedDateParts: [],
            era: null,
            meridiem: null,
            rfc2822: !1,
            weekdayMismatch: !1
          };
        }
        function v(e) {
          return null == e._pf && (e._pf = g()), e._pf;
        }
        function _(e) {
          var t = null,
            i = !1,
            n = e._d && !isNaN(e._d.getTime());
          return n && (t = v(e), i = a.call(t.parsedDateParts, function (e) {
            return null != e;
          }), n = t.overflow < 0 && !t.empty && !t.invalidEra && !t.invalidMonth && !t.invalidWeekday && !t.weekdayMismatch && !t.nullInput && !t.invalidFormat && !t.userInvalidated && (!t.meridiem || t.meridiem && i), e._strict && (n = n && 0 === t.charsLeftOver && 0 === t.unusedTokens.length && void 0 === t.bigHour)), null != Object.isFrozen && Object.isFrozen(e) ? n : (e._isValid = n, e._isValid);
        }
        function f(e) {
          var t = h(NaN);
          return null != e ? m(v(t), e) : v(t).userInvalidated = !0, t;
        }
        a = Array.prototype.some ? Array.prototype.some : function (e) {
          var t,
            a = Object(this),
            i = a.length >>> 0;
          for (t = 0; t < i; t++) if (t in a && e.call(this, a[t], t, a)) return !0;
          return !1;
        };
        var b = i.momentProperties = [],
          k = !1;
        function y(e, t) {
          var a,
            i,
            n,
            r = b.length;
          if (d(t._isAMomentObject) || (e._isAMomentObject = t._isAMomentObject), d(t._i) || (e._i = t._i), d(t._f) || (e._f = t._f), d(t._l) || (e._l = t._l), d(t._strict) || (e._strict = t._strict), d(t._tzm) || (e._tzm = t._tzm), d(t._isUTC) || (e._isUTC = t._isUTC), d(t._offset) || (e._offset = t._offset), d(t._pf) || (e._pf = v(t)), d(t._locale) || (e._locale = t._locale), r > 0) for (a = 0; a < r; a++) d(n = t[i = b[a]]) || (e[i] = n);
          return e;
        }
        function z(e) {
          y(this, e), this._d = new Date(null != e._d ? e._d.getTime() : NaN), this.isValid() || (this._d = new Date(NaN)), !1 === k && (k = !0, i.updateOffset(this), k = !1);
        }
        function w(e) {
          return e instanceof z || null != e && null != e._isAMomentObject;
        }
        function S(e) {
          !1 === i.suppressDeprecationWarnings && "undefined" != typeof console && console.warn && console.warn("Deprecation warning: " + e);
        }
        function A(e, t) {
          var a = !0;
          return m(function () {
            if (null != i.deprecationHandler && i.deprecationHandler(null, e), a) {
              var n,
                r,
                o,
                l = [],
                d = arguments.length;
              for (r = 0; r < d; r++) {
                if (n = "", "object" == typeof arguments[r]) {
                  for (o in n += "\n[" + r + "] ", arguments[0]) s(arguments[0], o) && (n += o + ": " + arguments[0][o] + ", ");
                  n = n.slice(0, -2);
                } else n = arguments[r];
                l.push(n);
              }
              S(e + "\nArguments: " + Array.prototype.slice.call(l).join("") + "\n" + new Error().stack), a = !1;
            }
            return t.apply(this, arguments);
          }, t);
        }
        var x,
          E = {};
        function M(e, t) {
          null != i.deprecationHandler && i.deprecationHandler(e, t), E[e] || (S(t), E[e] = !0);
        }
        function T(e) {
          return "undefined" != typeof Function && e instanceof Function || "[object Function]" === Object.prototype.toString.call(e);
        }
        function D(e) {
          var t, a;
          for (a in e) s(e, a) && (T(t = e[a]) ? this[a] = t : this["_" + a] = t);
          this._config = e, this._dayOfMonthOrdinalParseLenient = new RegExp((this._dayOfMonthOrdinalParse.source || this._ordinalParse.source) + "|" + /\d{1,2}/.source);
        }
        function P(e, t) {
          var a,
            i = m({}, e);
          for (a in t) s(t, a) && (o(e[a]) && o(t[a]) ? (i[a] = {}, m(i[a], e[a]), m(i[a], t[a])) : null != t[a] ? i[a] = t[a] : delete i[a]);
          for (a in e) s(e, a) && !s(t, a) && o(e[a]) && (i[a] = m({}, i[a]));
          return i;
        }
        function j(e) {
          null != e && this.set(e);
        }
        i.suppressDeprecationWarnings = !1, i.deprecationHandler = null, x = Object.keys ? Object.keys : function (e) {
          var t,
            a = [];
          for (t in e) s(e, t) && a.push(t);
          return a;
        };
        var N = {
          sameDay: "[Today at] LT",
          nextDay: "[Tomorrow at] LT",
          nextWeek: "dddd [at] LT",
          lastDay: "[Yesterday at] LT",
          lastWeek: "[Last] dddd [at] LT",
          sameElse: "L"
        };
        function C(e, t, a) {
          var i = this._calendar[e] || this._calendar.sameElse;
          return T(i) ? i.call(t, a) : i;
        }
        function H(e, t, a) {
          var i = "" + Math.abs(e),
            n = t - i.length;
          return (e >= 0 ? a ? "+" : "" : "-") + Math.pow(10, Math.max(0, n)).toString().substr(1) + i;
        }
        var O = /(\[[^\[]*\])|(\\)?([Hh]mm(ss)?|Mo|MM?M?M?|Do|DDDo|DD?D?D?|ddd?d?|do?|w[o|w]?|W[o|W]?|Qo?|N{1,5}|YYYYYY|YYYYY|YYYY|YY|y{2,4}|yo?|gg(ggg?)?|GG(GGG?)?|e|E|a|A|hh?|HH?|kk?|mm?|ss?|S{1,9}|x|X|zz?|ZZ?|.)/g,
          L = /(\[[^\[]*\])|(\\)?(LTS|LT|LL?L?L?|l{1,4})/g,
          I = {},
          B = {};
        function R(e, t, a, i) {
          var n = i;
          "string" == typeof i && (n = function () {
            return this[i]();
          }), e && (B[e] = n), t && (B[t[0]] = function () {
            return H(n.apply(this, arguments), t[1], t[2]);
          }), a && (B[a] = function () {
            return this.localeData().ordinal(n.apply(this, arguments), e);
          });
        }
        function U(e) {
          return e.match(/\[[\s\S]/) ? e.replace(/^\[|\]$/g, "") : e.replace(/\\/g, "");
        }
        function $(e) {
          var t,
            a,
            i = e.match(O);
          for (t = 0, a = i.length; t < a; t++) B[i[t]] ? i[t] = B[i[t]] : i[t] = U(i[t]);
          return function (t) {
            var n,
              r = "";
            for (n = 0; n < a; n++) r += T(i[n]) ? i[n].call(t, e) : i[n];
            return r;
          };
        }
        function V(e, t) {
          return e.isValid() ? (t = W(t, e.localeData()), I[t] = I[t] || $(t), I[t](e)) : e.localeData().invalidDate();
        }
        function W(e, t) {
          var a = 5;
          function i(e) {
            return t.longDateFormat(e) || e;
          }
          for (L.lastIndex = 0; a >= 0 && L.test(e);) e = e.replace(L, i), L.lastIndex = 0, a -= 1;
          return e;
        }
        var F = {
          LTS: "h:mm:ss A",
          LT: "h:mm A",
          L: "MM/DD/YYYY",
          LL: "MMMM D, YYYY",
          LLL: "MMMM D, YYYY h:mm A",
          LLLL: "dddd, MMMM D, YYYY h:mm A"
        };
        function q(e) {
          var t = this._longDateFormat[e],
            a = this._longDateFormat[e.toUpperCase()];
          return t || !a ? t : (this._longDateFormat[e] = a.match(O).map(function (e) {
            return "MMMM" === e || "MM" === e || "DD" === e || "dddd" === e ? e.slice(1) : e;
          }).join(""), this._longDateFormat[e]);
        }
        var Z = "Invalid date";
        function G() {
          return this._invalidDate;
        }
        var Y = "%d",
          K = /\d{1,2}/;
        function J(e) {
          return this._ordinal.replace("%d", e);
        }
        var X = {
          future: "in %s",
          past: "%s ago",
          s: "a few seconds",
          ss: "%d seconds",
          m: "a minute",
          mm: "%d minutes",
          h: "an hour",
          hh: "%d hours",
          d: "a day",
          dd: "%d days",
          w: "a week",
          ww: "%d weeks",
          M: "a month",
          MM: "%d months",
          y: "a year",
          yy: "%d years"
        };
        function Q(e, t, a, i) {
          var n = this._relativeTime[a];
          return T(n) ? n(e, t, a, i) : n.replace(/%d/i, e);
        }
        function ee(e, t) {
          var a = this._relativeTime[e > 0 ? "future" : "past"];
          return T(a) ? a(t) : a.replace(/%s/i, t);
        }
        var te = {
          D: "date",
          dates: "date",
          date: "date",
          d: "day",
          days: "day",
          day: "day",
          e: "weekday",
          weekdays: "weekday",
          weekday: "weekday",
          E: "isoWeekday",
          isoweekdays: "isoWeekday",
          isoweekday: "isoWeekday",
          DDD: "dayOfYear",
          dayofyears: "dayOfYear",
          dayofyear: "dayOfYear",
          h: "hour",
          hours: "hour",
          hour: "hour",
          ms: "millisecond",
          milliseconds: "millisecond",
          millisecond: "millisecond",
          m: "minute",
          minutes: "minute",
          minute: "minute",
          M: "month",
          months: "month",
          month: "month",
          Q: "quarter",
          quarters: "quarter",
          quarter: "quarter",
          s: "second",
          seconds: "second",
          second: "second",
          gg: "weekYear",
          weekyears: "weekYear",
          weekyear: "weekYear",
          GG: "isoWeekYear",
          isoweekyears: "isoWeekYear",
          isoweekyear: "isoWeekYear",
          w: "week",
          weeks: "week",
          week: "week",
          W: "isoWeek",
          isoweeks: "isoWeek",
          isoweek: "isoWeek",
          y: "year",
          years: "year",
          year: "year"
        };
        function ae(e) {
          return "string" == typeof e ? te[e] || te[e.toLowerCase()] : void 0;
        }
        function ie(e) {
          var t,
            a,
            i = {};
          for (a in e) s(e, a) && (t = ae(a)) && (i[t] = e[a]);
          return i;
        }
        var ne = {
          date: 9,
          day: 11,
          weekday: 11,
          isoWeekday: 11,
          dayOfYear: 4,
          hour: 13,
          millisecond: 16,
          minute: 14,
          month: 8,
          quarter: 7,
          second: 15,
          weekYear: 1,
          isoWeekYear: 1,
          week: 5,
          isoWeek: 5,
          year: 1
        };
        function re(e) {
          var t,
            a = [];
          for (t in e) s(e, t) && a.push({
            unit: t,
            priority: ne[t]
          });
          return a.sort(function (e, t) {
            return e.priority - t.priority;
          }), a;
        }
        var oe,
          se = /\d/,
          le = /\d\d/,
          de = /\d{3}/,
          ue = /\d{4}/,
          ce = /[+-]?\d{6}/,
          pe = /\d\d?/,
          me = /\d\d\d\d?/,
          he = /\d\d\d\d\d\d?/,
          ge = /\d{1,3}/,
          ve = /\d{1,4}/,
          _e = /[+-]?\d{1,6}/,
          fe = /\d+/,
          be = /[+-]?\d+/,
          ke = /Z|[+-]\d\d:?\d\d/gi,
          ye = /Z|[+-]\d\d(?::?\d\d)?/gi,
          ze = /[+-]?\d+(\.\d{1,3})?/,
          we = /[0-9]{0,256}['a-z\u00A0-\u05FF\u0700-\uD7FF\uF900-\uFDCF\uFDF0-\uFF07\uFF10-\uFFEF]{1,256}|[\u0600-\u06FF\/]{1,256}(\s*?[\u0600-\u06FF]{1,256}){1,2}/i,
          Se = /^[1-9]\d?/,
          Ae = /^([1-9]\d|\d)/;
        function xe(e, t, a) {
          oe[e] = T(t) ? t : function (e, i) {
            return e && a ? a : t;
          };
        }
        function Ee(e, t) {
          return s(oe, e) ? oe[e](t._strict, t._locale) : new RegExp(Me(e));
        }
        function Me(e) {
          return Te(e.replace("\\", "").replace(/\\(\[)|\\(\])|\[([^\]\[]*)\]|\\(.)/g, function (e, t, a, i, n) {
            return t || a || i || n;
          }));
        }
        function Te(e) {
          return e.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&");
        }
        function De(e) {
          return e < 0 ? Math.ceil(e) || 0 : Math.floor(e);
        }
        function Pe(e) {
          var t = +e,
            a = 0;
          return 0 !== t && isFinite(t) && (a = De(t)), a;
        }
        oe = {};
        var je = {};
        function Ne(e, t) {
          var a,
            i,
            n = t;
          for ("string" == typeof e && (e = [e]), u(t) && (n = function (e, a) {
            a[t] = Pe(e);
          }), i = e.length, a = 0; a < i; a++) je[e[a]] = n;
        }
        function Ce(e, t) {
          Ne(e, function (e, a, i, n) {
            i._w = i._w || {}, t(e, i._w, i, n);
          });
        }
        function He(e, t, a) {
          null != t && s(je, e) && je[e](t, a._a, a, e);
        }
        function Oe(e) {
          return e % 4 == 0 && e % 100 != 0 || e % 400 == 0;
        }
        var Le = 0,
          Ie = 1,
          Be = 2,
          Re = 3,
          Ue = 4,
          $e = 5,
          Ve = 6,
          We = 7,
          Fe = 8;
        function qe(e) {
          return Oe(e) ? 366 : 365;
        }
        R("Y", 0, 0, function () {
          var e = this.year();
          return e <= 9999 ? H(e, 4) : "+" + e;
        }), R(0, ["YY", 2], 0, function () {
          return this.year() % 100;
        }), R(0, ["YYYY", 4], 0, "year"), R(0, ["YYYYY", 5], 0, "year"), R(0, ["YYYYYY", 6, !0], 0, "year"), xe("Y", be), xe("YY", pe, le), xe("YYYY", ve, ue), xe("YYYYY", _e, ce), xe("YYYYYY", _e, ce), Ne(["YYYYY", "YYYYYY"], Le), Ne("YYYY", function (e, t) {
          t[Le] = 2 === e.length ? i.parseTwoDigitYear(e) : Pe(e);
        }), Ne("YY", function (e, t) {
          t[Le] = i.parseTwoDigitYear(e);
        }), Ne("Y", function (e, t) {
          t[Le] = parseInt(e, 10);
        }), i.parseTwoDigitYear = function (e) {
          return Pe(e) + (Pe(e) > 68 ? 1900 : 2e3);
        };
        var Ze,
          Ge = Ke("FullYear", !0);
        function Ye() {
          return Oe(this.year());
        }
        function Ke(e, t) {
          return function (a) {
            return null != a ? (Xe(this, e, a), i.updateOffset(this, t), this) : Je(this, e);
          };
        }
        function Je(e, t) {
          if (!e.isValid()) return NaN;
          var a = e._d,
            i = e._isUTC;
          switch (t) {
            case "Milliseconds":
              return i ? a.getUTCMilliseconds() : a.getMilliseconds();
            case "Seconds":
              return i ? a.getUTCSeconds() : a.getSeconds();
            case "Minutes":
              return i ? a.getUTCMinutes() : a.getMinutes();
            case "Hours":
              return i ? a.getUTCHours() : a.getHours();
            case "Date":
              return i ? a.getUTCDate() : a.getDate();
            case "Day":
              return i ? a.getUTCDay() : a.getDay();
            case "Month":
              return i ? a.getUTCMonth() : a.getMonth();
            case "FullYear":
              return i ? a.getUTCFullYear() : a.getFullYear();
            default:
              return NaN;
          }
        }
        function Xe(e, t, a) {
          var i, n, r, o, s;
          if (e.isValid() && !isNaN(a)) {
            switch (i = e._d, n = e._isUTC, t) {
              case "Milliseconds":
                return void (n ? i.setUTCMilliseconds(a) : i.setMilliseconds(a));
              case "Seconds":
                return void (n ? i.setUTCSeconds(a) : i.setSeconds(a));
              case "Minutes":
                return void (n ? i.setUTCMinutes(a) : i.setMinutes(a));
              case "Hours":
                return void (n ? i.setUTCHours(a) : i.setHours(a));
              case "Date":
                return void (n ? i.setUTCDate(a) : i.setDate(a));
              case "FullYear":
                break;
              default:
                return;
            }
            r = a, o = e.month(), s = 29 !== (s = e.date()) || 1 !== o || Oe(r) ? s : 28, n ? i.setUTCFullYear(r, o, s) : i.setFullYear(r, o, s);
          }
        }
        function Qe(e) {
          return T(this[e = ae(e)]) ? this[e]() : this;
        }
        function et(e, t) {
          if ("object" == typeof e) {
            var a,
              i = re(e = ie(e)),
              n = i.length;
            for (a = 0; a < n; a++) this[i[a].unit](e[i[a].unit]);
          } else if (T(this[e = ae(e)])) return this[e](t);
          return this;
        }
        function tt(e, t) {
          return (e % t + t) % t;
        }
        function at(e, t) {
          if (isNaN(e) || isNaN(t)) return NaN;
          var a = tt(t, 12);
          return e += (t - a) / 12, 1 === a ? Oe(e) ? 29 : 28 : 31 - a % 7 % 2;
        }
        Ze = Array.prototype.indexOf ? Array.prototype.indexOf : function (e) {
          var t;
          for (t = 0; t < this.length; ++t) if (this[t] === e) return t;
          return -1;
        }, R("M", ["MM", 2], "Mo", function () {
          return this.month() + 1;
        }), R("MMM", 0, 0, function (e) {
          return this.localeData().monthsShort(this, e);
        }), R("MMMM", 0, 0, function (e) {
          return this.localeData().months(this, e);
        }), xe("M", pe, Se), xe("MM", pe, le), xe("MMM", function (e, t) {
          return t.monthsShortRegex(e);
        }), xe("MMMM", function (e, t) {
          return t.monthsRegex(e);
        }), Ne(["M", "MM"], function (e, t) {
          t[Ie] = Pe(e) - 1;
        }), Ne(["MMM", "MMMM"], function (e, t, a, i) {
          var n = a._locale.monthsParse(e, i, a._strict);
          null != n ? t[Ie] = n : v(a).invalidMonth = e;
        });
        var it = "January_February_March_April_May_June_July_August_September_October_November_December".split("_"),
          nt = "Jan_Feb_Mar_Apr_May_Jun_Jul_Aug_Sep_Oct_Nov_Dec".split("_"),
          rt = /D[oD]?(\[[^\[\]]*\]|\s)+MMMM?/,
          ot = we,
          st = we;
        function lt(e, t) {
          return e ? r(this._months) ? this._months[e.month()] : this._months[(this._months.isFormat || rt).test(t) ? "format" : "standalone"][e.month()] : r(this._months) ? this._months : this._months.standalone;
        }
        function dt(e, t) {
          return e ? r(this._monthsShort) ? this._monthsShort[e.month()] : this._monthsShort[rt.test(t) ? "format" : "standalone"][e.month()] : r(this._monthsShort) ? this._monthsShort : this._monthsShort.standalone;
        }
        function ut(e, t, a) {
          var i,
            n,
            r,
            o = e.toLocaleLowerCase();
          if (!this._monthsParse) for (this._monthsParse = [], this._longMonthsParse = [], this._shortMonthsParse = [], i = 0; i < 12; ++i) r = h([2e3, i]), this._shortMonthsParse[i] = this.monthsShort(r, "").toLocaleLowerCase(), this._longMonthsParse[i] = this.months(r, "").toLocaleLowerCase();
          return a ? "MMM" === t ? -1 !== (n = Ze.call(this._shortMonthsParse, o)) ? n : null : -1 !== (n = Ze.call(this._longMonthsParse, o)) ? n : null : "MMM" === t ? -1 !== (n = Ze.call(this._shortMonthsParse, o)) || -1 !== (n = Ze.call(this._longMonthsParse, o)) ? n : null : -1 !== (n = Ze.call(this._longMonthsParse, o)) || -1 !== (n = Ze.call(this._shortMonthsParse, o)) ? n : null;
        }
        function ct(e, t, a) {
          var i, n, r;
          if (this._monthsParseExact) return ut.call(this, e, t, a);
          for (this._monthsParse || (this._monthsParse = [], this._longMonthsParse = [], this._shortMonthsParse = []), i = 0; i < 12; i++) {
            if (n = h([2e3, i]), a && !this._longMonthsParse[i] && (this._longMonthsParse[i] = new RegExp("^" + this.months(n, "").replace(".", "") + "$", "i"), this._shortMonthsParse[i] = new RegExp("^" + this.monthsShort(n, "").replace(".", "") + "$", "i")), a || this._monthsParse[i] || (r = "^" + this.months(n, "") + "|^" + this.monthsShort(n, ""), this._monthsParse[i] = new RegExp(r.replace(".", ""), "i")), a && "MMMM" === t && this._longMonthsParse[i].test(e)) return i;
            if (a && "MMM" === t && this._shortMonthsParse[i].test(e)) return i;
            if (!a && this._monthsParse[i].test(e)) return i;
          }
        }
        function pt(e, t) {
          if (!e.isValid()) return e;
          if ("string" == typeof t) if (/^\d+$/.test(t)) t = Pe(t);else if (!u(t = e.localeData().monthsParse(t))) return e;
          var a = t,
            i = e.date();
          return i = i < 29 ? i : Math.min(i, at(e.year(), a)), e._isUTC ? e._d.setUTCMonth(a, i) : e._d.setMonth(a, i), e;
        }
        function mt(e) {
          return null != e ? (pt(this, e), i.updateOffset(this, !0), this) : Je(this, "Month");
        }
        function ht() {
          return at(this.year(), this.month());
        }
        function gt(e) {
          return this._monthsParseExact ? (s(this, "_monthsRegex") || _t.call(this), e ? this._monthsShortStrictRegex : this._monthsShortRegex) : (s(this, "_monthsShortRegex") || (this._monthsShortRegex = ot), this._monthsShortStrictRegex && e ? this._monthsShortStrictRegex : this._monthsShortRegex);
        }
        function vt(e) {
          return this._monthsParseExact ? (s(this, "_monthsRegex") || _t.call(this), e ? this._monthsStrictRegex : this._monthsRegex) : (s(this, "_monthsRegex") || (this._monthsRegex = st), this._monthsStrictRegex && e ? this._monthsStrictRegex : this._monthsRegex);
        }
        function _t() {
          function e(e, t) {
            return t.length - e.length;
          }
          var t,
            a,
            i,
            n,
            r = [],
            o = [],
            s = [];
          for (t = 0; t < 12; t++) a = h([2e3, t]), i = Te(this.monthsShort(a, "")), n = Te(this.months(a, "")), r.push(i), o.push(n), s.push(n), s.push(i);
          r.sort(e), o.sort(e), s.sort(e), this._monthsRegex = new RegExp("^(" + s.join("|") + ")", "i"), this._monthsShortRegex = this._monthsRegex, this._monthsStrictRegex = new RegExp("^(" + o.join("|") + ")", "i"), this._monthsShortStrictRegex = new RegExp("^(" + r.join("|") + ")", "i");
        }
        function ft(e, t, a, i, n, r, o) {
          var s;
          return e < 100 && e >= 0 ? (s = new Date(e + 400, t, a, i, n, r, o), isFinite(s.getFullYear()) && s.setFullYear(e)) : s = new Date(e, t, a, i, n, r, o), s;
        }
        function bt(e) {
          var t, a;
          return e < 100 && e >= 0 ? ((a = Array.prototype.slice.call(arguments))[0] = e + 400, t = new Date(Date.UTC.apply(null, a)), isFinite(t.getUTCFullYear()) && t.setUTCFullYear(e)) : t = new Date(Date.UTC.apply(null, arguments)), t;
        }
        function kt(e, t, a) {
          var i = 7 + t - a;
          return -(7 + bt(e, 0, i).getUTCDay() - t) % 7 + i - 1;
        }
        function yt(e, t, a, i, n) {
          var r,
            o,
            s = 1 + 7 * (t - 1) + (7 + a - i) % 7 + kt(e, i, n);
          return s <= 0 ? o = qe(r = e - 1) + s : s > qe(e) ? (r = e + 1, o = s - qe(e)) : (r = e, o = s), {
            year: r,
            dayOfYear: o
          };
        }
        function zt(e, t, a) {
          var i,
            n,
            r = kt(e.year(), t, a),
            o = Math.floor((e.dayOfYear() - r - 1) / 7) + 1;
          return o < 1 ? i = o + wt(n = e.year() - 1, t, a) : o > wt(e.year(), t, a) ? (i = o - wt(e.year(), t, a), n = e.year() + 1) : (n = e.year(), i = o), {
            week: i,
            year: n
          };
        }
        function wt(e, t, a) {
          var i = kt(e, t, a),
            n = kt(e + 1, t, a);
          return (qe(e) - i + n) / 7;
        }
        function St(e) {
          return zt(e, this._week.dow, this._week.doy).week;
        }
        R("w", ["ww", 2], "wo", "week"), R("W", ["WW", 2], "Wo", "isoWeek"), xe("w", pe, Se), xe("ww", pe, le), xe("W", pe, Se), xe("WW", pe, le), Ce(["w", "ww", "W", "WW"], function (e, t, a, i) {
          t[i.substr(0, 1)] = Pe(e);
        });
        var At = {
          dow: 0,
          doy: 6
        };
        function xt() {
          return this._week.dow;
        }
        function Et() {
          return this._week.doy;
        }
        function Mt(e) {
          var t = this.localeData().week(this);
          return null == e ? t : this.add(7 * (e - t), "d");
        }
        function Tt(e) {
          var t = zt(this, 1, 4).week;
          return null == e ? t : this.add(7 * (e - t), "d");
        }
        function Dt(e, t) {
          return "string" != typeof e ? e : isNaN(e) ? "number" == typeof (e = t.weekdaysParse(e)) ? e : null : parseInt(e, 10);
        }
        function Pt(e, t) {
          return "string" == typeof e ? t.weekdaysParse(e) % 7 || 7 : isNaN(e) ? null : e;
        }
        function jt(e, t) {
          return e.slice(t, 7).concat(e.slice(0, t));
        }
        R("d", 0, "do", "day"), R("dd", 0, 0, function (e) {
          return this.localeData().weekdaysMin(this, e);
        }), R("ddd", 0, 0, function (e) {
          return this.localeData().weekdaysShort(this, e);
        }), R("dddd", 0, 0, function (e) {
          return this.localeData().weekdays(this, e);
        }), R("e", 0, 0, "weekday"), R("E", 0, 0, "isoWeekday"), xe("d", pe), xe("e", pe), xe("E", pe), xe("dd", function (e, t) {
          return t.weekdaysMinRegex(e);
        }), xe("ddd", function (e, t) {
          return t.weekdaysShortRegex(e);
        }), xe("dddd", function (e, t) {
          return t.weekdaysRegex(e);
        }), Ce(["dd", "ddd", "dddd"], function (e, t, a, i) {
          var n = a._locale.weekdaysParse(e, i, a._strict);
          null != n ? t.d = n : v(a).invalidWeekday = e;
        }), Ce(["d", "e", "E"], function (e, t, a, i) {
          t[i] = Pe(e);
        });
        var Nt = "Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday".split("_"),
          Ct = "Sun_Mon_Tue_Wed_Thu_Fri_Sat".split("_"),
          Ht = "Su_Mo_Tu_We_Th_Fr_Sa".split("_"),
          Ot = we,
          Lt = we,
          It = we;
        function Bt(e, t) {
          var a = r(this._weekdays) ? this._weekdays : this._weekdays[e && !0 !== e && this._weekdays.isFormat.test(t) ? "format" : "standalone"];
          return !0 === e ? jt(a, this._week.dow) : e ? a[e.day()] : a;
        }
        function Rt(e) {
          return !0 === e ? jt(this._weekdaysShort, this._week.dow) : e ? this._weekdaysShort[e.day()] : this._weekdaysShort;
        }
        function Ut(e) {
          return !0 === e ? jt(this._weekdaysMin, this._week.dow) : e ? this._weekdaysMin[e.day()] : this._weekdaysMin;
        }
        function $t(e, t, a) {
          var i,
            n,
            r,
            o = e.toLocaleLowerCase();
          if (!this._weekdaysParse) for (this._weekdaysParse = [], this._shortWeekdaysParse = [], this._minWeekdaysParse = [], i = 0; i < 7; ++i) r = h([2e3, 1]).day(i), this._minWeekdaysParse[i] = this.weekdaysMin(r, "").toLocaleLowerCase(), this._shortWeekdaysParse[i] = this.weekdaysShort(r, "").toLocaleLowerCase(), this._weekdaysParse[i] = this.weekdays(r, "").toLocaleLowerCase();
          return a ? "dddd" === t ? -1 !== (n = Ze.call(this._weekdaysParse, o)) ? n : null : "ddd" === t ? -1 !== (n = Ze.call(this._shortWeekdaysParse, o)) ? n : null : -1 !== (n = Ze.call(this._minWeekdaysParse, o)) ? n : null : "dddd" === t ? -1 !== (n = Ze.call(this._weekdaysParse, o)) || -1 !== (n = Ze.call(this._shortWeekdaysParse, o)) || -1 !== (n = Ze.call(this._minWeekdaysParse, o)) ? n : null : "ddd" === t ? -1 !== (n = Ze.call(this._shortWeekdaysParse, o)) || -1 !== (n = Ze.call(this._weekdaysParse, o)) || -1 !== (n = Ze.call(this._minWeekdaysParse, o)) ? n : null : -1 !== (n = Ze.call(this._minWeekdaysParse, o)) || -1 !== (n = Ze.call(this._weekdaysParse, o)) || -1 !== (n = Ze.call(this._shortWeekdaysParse, o)) ? n : null;
        }
        function Vt(e, t, a) {
          var i, n, r;
          if (this._weekdaysParseExact) return $t.call(this, e, t, a);
          for (this._weekdaysParse || (this._weekdaysParse = [], this._minWeekdaysParse = [], this._shortWeekdaysParse = [], this._fullWeekdaysParse = []), i = 0; i < 7; i++) {
            if (n = h([2e3, 1]).day(i), a && !this._fullWeekdaysParse[i] && (this._fullWeekdaysParse[i] = new RegExp("^" + this.weekdays(n, "").replace(".", "\\.?") + "$", "i"), this._shortWeekdaysParse[i] = new RegExp("^" + this.weekdaysShort(n, "").replace(".", "\\.?") + "$", "i"), this._minWeekdaysParse[i] = new RegExp("^" + this.weekdaysMin(n, "").replace(".", "\\.?") + "$", "i")), this._weekdaysParse[i] || (r = "^" + this.weekdays(n, "") + "|^" + this.weekdaysShort(n, "") + "|^" + this.weekdaysMin(n, ""), this._weekdaysParse[i] = new RegExp(r.replace(".", ""), "i")), a && "dddd" === t && this._fullWeekdaysParse[i].test(e)) return i;
            if (a && "ddd" === t && this._shortWeekdaysParse[i].test(e)) return i;
            if (a && "dd" === t && this._minWeekdaysParse[i].test(e)) return i;
            if (!a && this._weekdaysParse[i].test(e)) return i;
          }
        }
        function Wt(e) {
          if (!this.isValid()) return null != e ? this : NaN;
          var t = Je(this, "Day");
          return null != e ? (e = Dt(e, this.localeData()), this.add(e - t, "d")) : t;
        }
        function Ft(e) {
          if (!this.isValid()) return null != e ? this : NaN;
          var t = (this.day() + 7 - this.localeData()._week.dow) % 7;
          return null == e ? t : this.add(e - t, "d");
        }
        function qt(e) {
          if (!this.isValid()) return null != e ? this : NaN;
          if (null != e) {
            var t = Pt(e, this.localeData());
            return this.day(this.day() % 7 ? t : t - 7);
          }
          return this.day() || 7;
        }
        function Zt(e) {
          return this._weekdaysParseExact ? (s(this, "_weekdaysRegex") || Kt.call(this), e ? this._weekdaysStrictRegex : this._weekdaysRegex) : (s(this, "_weekdaysRegex") || (this._weekdaysRegex = Ot), this._weekdaysStrictRegex && e ? this._weekdaysStrictRegex : this._weekdaysRegex);
        }
        function Gt(e) {
          return this._weekdaysParseExact ? (s(this, "_weekdaysRegex") || Kt.call(this), e ? this._weekdaysShortStrictRegex : this._weekdaysShortRegex) : (s(this, "_weekdaysShortRegex") || (this._weekdaysShortRegex = Lt), this._weekdaysShortStrictRegex && e ? this._weekdaysShortStrictRegex : this._weekdaysShortRegex);
        }
        function Yt(e) {
          return this._weekdaysParseExact ? (s(this, "_weekdaysRegex") || Kt.call(this), e ? this._weekdaysMinStrictRegex : this._weekdaysMinRegex) : (s(this, "_weekdaysMinRegex") || (this._weekdaysMinRegex = It), this._weekdaysMinStrictRegex && e ? this._weekdaysMinStrictRegex : this._weekdaysMinRegex);
        }
        function Kt() {
          function e(e, t) {
            return t.length - e.length;
          }
          var t,
            a,
            i,
            n,
            r,
            o = [],
            s = [],
            l = [],
            d = [];
          for (t = 0; t < 7; t++) a = h([2e3, 1]).day(t), i = Te(this.weekdaysMin(a, "")), n = Te(this.weekdaysShort(a, "")), r = Te(this.weekdays(a, "")), o.push(i), s.push(n), l.push(r), d.push(i), d.push(n), d.push(r);
          o.sort(e), s.sort(e), l.sort(e), d.sort(e), this._weekdaysRegex = new RegExp("^(" + d.join("|") + ")", "i"), this._weekdaysShortRegex = this._weekdaysRegex, this._weekdaysMinRegex = this._weekdaysRegex, this._weekdaysStrictRegex = new RegExp("^(" + l.join("|") + ")", "i"), this._weekdaysShortStrictRegex = new RegExp("^(" + s.join("|") + ")", "i"), this._weekdaysMinStrictRegex = new RegExp("^(" + o.join("|") + ")", "i");
        }
        function Jt() {
          return this.hours() % 12 || 12;
        }
        function Xt() {
          return this.hours() || 24;
        }
        function Qt(e, t) {
          R(e, 0, 0, function () {
            return this.localeData().meridiem(this.hours(), this.minutes(), t);
          });
        }
        function ea(e, t) {
          return t._meridiemParse;
        }
        function ta(e) {
          return "p" === (e + "").toLowerCase().charAt(0);
        }
        R("H", ["HH", 2], 0, "hour"), R("h", ["hh", 2], 0, Jt), R("k", ["kk", 2], 0, Xt), R("hmm", 0, 0, function () {
          return "" + Jt.apply(this) + H(this.minutes(), 2);
        }), R("hmmss", 0, 0, function () {
          return "" + Jt.apply(this) + H(this.minutes(), 2) + H(this.seconds(), 2);
        }), R("Hmm", 0, 0, function () {
          return "" + this.hours() + H(this.minutes(), 2);
        }), R("Hmmss", 0, 0, function () {
          return "" + this.hours() + H(this.minutes(), 2) + H(this.seconds(), 2);
        }), Qt("a", !0), Qt("A", !1), xe("a", ea), xe("A", ea), xe("H", pe, Ae), xe("h", pe, Se), xe("k", pe, Se), xe("HH", pe, le), xe("hh", pe, le), xe("kk", pe, le), xe("hmm", me), xe("hmmss", he), xe("Hmm", me), xe("Hmmss", he), Ne(["H", "HH"], Re), Ne(["k", "kk"], function (e, t, a) {
          var i = Pe(e);
          t[Re] = 24 === i ? 0 : i;
        }), Ne(["a", "A"], function (e, t, a) {
          a._isPm = a._locale.isPM(e), a._meridiem = e;
        }), Ne(["h", "hh"], function (e, t, a) {
          t[Re] = Pe(e), v(a).bigHour = !0;
        }), Ne("hmm", function (e, t, a) {
          var i = e.length - 2;
          t[Re] = Pe(e.substr(0, i)), t[Ue] = Pe(e.substr(i)), v(a).bigHour = !0;
        }), Ne("hmmss", function (e, t, a) {
          var i = e.length - 4,
            n = e.length - 2;
          t[Re] = Pe(e.substr(0, i)), t[Ue] = Pe(e.substr(i, 2)), t[$e] = Pe(e.substr(n)), v(a).bigHour = !0;
        }), Ne("Hmm", function (e, t, a) {
          var i = e.length - 2;
          t[Re] = Pe(e.substr(0, i)), t[Ue] = Pe(e.substr(i));
        }), Ne("Hmmss", function (e, t, a) {
          var i = e.length - 4,
            n = e.length - 2;
          t[Re] = Pe(e.substr(0, i)), t[Ue] = Pe(e.substr(i, 2)), t[$e] = Pe(e.substr(n));
        });
        var aa = /[ap]\.?m?\.?/i,
          ia = Ke("Hours", !0);
        function na(e, t, a) {
          return e > 11 ? a ? "pm" : "PM" : a ? "am" : "AM";
        }
        var ra,
          oa = {
            calendar: N,
            longDateFormat: F,
            invalidDate: Z,
            ordinal: Y,
            dayOfMonthOrdinalParse: K,
            relativeTime: X,
            months: it,
            monthsShort: nt,
            week: At,
            weekdays: Nt,
            weekdaysMin: Ht,
            weekdaysShort: Ct,
            meridiemParse: aa
          },
          sa = {},
          la = {};
        function da(e, t) {
          var a,
            i = Math.min(e.length, t.length);
          for (a = 0; a < i; a += 1) if (e[a] !== t[a]) return a;
          return i;
        }
        function ua(e) {
          return e ? e.toLowerCase().replace("_", "-") : e;
        }
        function ca(e) {
          for (var t, a, i, n, r = 0; r < e.length;) {
            for (t = (n = ua(e[r]).split("-")).length, a = (a = ua(e[r + 1])) ? a.split("-") : null; t > 0;) {
              if (i = ma(n.slice(0, t).join("-"))) return i;
              if (a && a.length >= t && da(n, a) >= t - 1) break;
              t--;
            }
            r++;
          }
          return ra;
        }
        function pa(e) {
          return !(!e || !e.match("^[^/\\\\]*$"));
        }
        function ma(t) {
          var a = null;
          if (void 0 === sa[t] && e && e.exports && pa(t)) try {
            a = ra._abbr, Cn("./locale/" + t), ha(a);
          } catch (e) {
            sa[t] = null;
          }
          return sa[t];
        }
        function ha(e, t) {
          var a;
          return e && ((a = d(t) ? _a(e) : ga(e, t)) ? ra = a : "undefined" != typeof console && console.warn && console.warn("Locale " + e + " not found. Did you forget to load it?")), ra._abbr;
        }
        function ga(e, t) {
          if (null !== t) {
            var a,
              i = oa;
            if (t.abbr = e, null != sa[e]) M("defineLocaleOverride", "use moment.updateLocale(localeName, config) to change an existing locale. moment.defineLocale(localeName, config) should only be used for creating a new locale See http://momentjs.com/guides/#/warnings/define-locale/ for more info."), i = sa[e]._config;else if (null != t.parentLocale) if (null != sa[t.parentLocale]) i = sa[t.parentLocale]._config;else {
              if (null == (a = ma(t.parentLocale))) return la[t.parentLocale] || (la[t.parentLocale] = []), la[t.parentLocale].push({
                name: e,
                config: t
              }), null;
              i = a._config;
            }
            return sa[e] = new j(P(i, t)), la[e] && la[e].forEach(function (e) {
              ga(e.name, e.config);
            }), ha(e), sa[e];
          }
          return delete sa[e], null;
        }
        function va(e, t) {
          if (null != t) {
            var a,
              i,
              n = oa;
            null != sa[e] && null != sa[e].parentLocale ? sa[e].set(P(sa[e]._config, t)) : (null != (i = ma(e)) && (n = i._config), t = P(n, t), null == i && (t.abbr = e), (a = new j(t)).parentLocale = sa[e], sa[e] = a), ha(e);
          } else null != sa[e] && (null != sa[e].parentLocale ? (sa[e] = sa[e].parentLocale, e === ha() && ha(e)) : null != sa[e] && delete sa[e]);
          return sa[e];
        }
        function _a(e) {
          var t;
          if (e && e._locale && e._locale._abbr && (e = e._locale._abbr), !e) return ra;
          if (!r(e)) {
            if (t = ma(e)) return t;
            e = [e];
          }
          return ca(e);
        }
        function fa() {
          return x(sa);
        }
        function ba(e) {
          var t,
            a = e._a;
          return a && -2 === v(e).overflow && (t = a[Ie] < 0 || a[Ie] > 11 ? Ie : a[Be] < 1 || a[Be] > at(a[Le], a[Ie]) ? Be : a[Re] < 0 || a[Re] > 24 || 24 === a[Re] && (0 !== a[Ue] || 0 !== a[$e] || 0 !== a[Ve]) ? Re : a[Ue] < 0 || a[Ue] > 59 ? Ue : a[$e] < 0 || a[$e] > 59 ? $e : a[Ve] < 0 || a[Ve] > 999 ? Ve : -1, v(e)._overflowDayOfYear && (t < Le || t > Be) && (t = Be), v(e)._overflowWeeks && -1 === t && (t = We), v(e)._overflowWeekday && -1 === t && (t = Fe), v(e).overflow = t), e;
        }
        var ka = /^\s*((?:[+-]\d{6}|\d{4})-(?:\d\d-\d\d|W\d\d-\d|W\d\d|\d\d\d|\d\d))(?:(T| )(\d\d(?::\d\d(?::\d\d(?:[.,]\d+)?)?)?)([+-]\d\d(?::?\d\d)?|\s*Z)?)?$/,
          ya = /^\s*((?:[+-]\d{6}|\d{4})(?:\d\d\d\d|W\d\d\d|W\d\d|\d\d\d|\d\d|))(?:(T| )(\d\d(?:\d\d(?:\d\d(?:[.,]\d+)?)?)?)([+-]\d\d(?::?\d\d)?|\s*Z)?)?$/,
          za = /Z|[+-]\d\d(?::?\d\d)?/,
          wa = [["YYYYYY-MM-DD", /[+-]\d{6}-\d\d-\d\d/], ["YYYY-MM-DD", /\d{4}-\d\d-\d\d/], ["GGGG-[W]WW-E", /\d{4}-W\d\d-\d/], ["GGGG-[W]WW", /\d{4}-W\d\d/, !1], ["YYYY-DDD", /\d{4}-\d{3}/], ["YYYY-MM", /\d{4}-\d\d/, !1], ["YYYYYYMMDD", /[+-]\d{10}/], ["YYYYMMDD", /\d{8}/], ["GGGG[W]WWE", /\d{4}W\d{3}/], ["GGGG[W]WW", /\d{4}W\d{2}/, !1], ["YYYYDDD", /\d{7}/], ["YYYYMM", /\d{6}/, !1], ["YYYY", /\d{4}/, !1]],
          Sa = [["HH:mm:ss.SSSS", /\d\d:\d\d:\d\d\.\d+/], ["HH:mm:ss,SSSS", /\d\d:\d\d:\d\d,\d+/], ["HH:mm:ss", /\d\d:\d\d:\d\d/], ["HH:mm", /\d\d:\d\d/], ["HHmmss.SSSS", /\d\d\d\d\d\d\.\d+/], ["HHmmss,SSSS", /\d\d\d\d\d\d,\d+/], ["HHmmss", /\d\d\d\d\d\d/], ["HHmm", /\d\d\d\d/], ["HH", /\d\d/]],
          Aa = /^\/?Date\((-?\d+)/i,
          xa = /^(?:(Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s)?(\d{1,2})\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s(\d{2,4})\s(\d\d):(\d\d)(?::(\d\d))?\s(?:(UT|GMT|[ECMP][SD]T)|([Zz])|([+-]\d{4}))$/,
          Ea = {
            UT: 0,
            GMT: 0,
            EDT: -240,
            EST: -300,
            CDT: -300,
            CST: -360,
            MDT: -360,
            MST: -420,
            PDT: -420,
            PST: -480
          };
        function Ma(e) {
          var t,
            a,
            i,
            n,
            r,
            o,
            s = e._i,
            l = ka.exec(s) || ya.exec(s),
            d = wa.length,
            u = Sa.length;
          if (l) {
            for (v(e).iso = !0, t = 0, a = d; t < a; t++) if (wa[t][1].exec(l[1])) {
              n = wa[t][0], i = !1 !== wa[t][2];
              break;
            }
            if (null == n) return void (e._isValid = !1);
            if (l[3]) {
              for (t = 0, a = u; t < a; t++) if (Sa[t][1].exec(l[3])) {
                r = (l[2] || " ") + Sa[t][0];
                break;
              }
              if (null == r) return void (e._isValid = !1);
            }
            if (!i && null != r) return void (e._isValid = !1);
            if (l[4]) {
              if (!za.exec(l[4])) return void (e._isValid = !1);
              o = "Z";
            }
            e._f = n + (r || "") + (o || ""), Ra(e);
          } else e._isValid = !1;
        }
        function Ta(e, t, a, i, n, r) {
          var o = [Da(e), nt.indexOf(t), parseInt(a, 10), parseInt(i, 10), parseInt(n, 10)];
          return r && o.push(parseInt(r, 10)), o;
        }
        function Da(e) {
          var t = parseInt(e, 10);
          return t <= 49 ? 2e3 + t : t <= 999 ? 1900 + t : t;
        }
        function Pa(e) {
          return e.replace(/\([^()]*\)|[\n\t]/g, " ").replace(/(\s\s+)/g, " ").replace(/^\s\s*/, "").replace(/\s\s*$/, "");
        }
        function ja(e, t, a) {
          return !e || Ct.indexOf(e) === new Date(t[0], t[1], t[2]).getDay() || (v(a).weekdayMismatch = !0, a._isValid = !1, !1);
        }
        function Na(e, t, a) {
          if (e) return Ea[e];
          if (t) return 0;
          var i = parseInt(a, 10),
            n = i % 100;
          return (i - n) / 100 * 60 + n;
        }
        function Ca(e) {
          var t,
            a = xa.exec(Pa(e._i));
          if (a) {
            if (t = Ta(a[4], a[3], a[2], a[5], a[6], a[7]), !ja(a[1], t, e)) return;
            e._a = t, e._tzm = Na(a[8], a[9], a[10]), e._d = bt.apply(null, e._a), e._d.setUTCMinutes(e._d.getUTCMinutes() - e._tzm), v(e).rfc2822 = !0;
          } else e._isValid = !1;
        }
        function Ha(e) {
          var t = Aa.exec(e._i);
          null === t ? (Ma(e), !1 === e._isValid && (delete e._isValid, Ca(e), !1 === e._isValid && (delete e._isValid, e._strict ? e._isValid = !1 : i.createFromInputFallback(e)))) : e._d = new Date(+t[1]);
        }
        function Oa(e, t, a) {
          return null != e ? e : null != t ? t : a;
        }
        function La(e) {
          var t = new Date(i.now());
          return e._useUTC ? [t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate()] : [t.getFullYear(), t.getMonth(), t.getDate()];
        }
        function Ia(e) {
          var t,
            a,
            i,
            n,
            r,
            o = [];
          if (!e._d) {
            for (i = La(e), e._w && null == e._a[Be] && null == e._a[Ie] && Ba(e), null != e._dayOfYear && (r = Oa(e._a[Le], i[Le]), (e._dayOfYear > qe(r) || 0 === e._dayOfYear) && (v(e)._overflowDayOfYear = !0), a = bt(r, 0, e._dayOfYear), e._a[Ie] = a.getUTCMonth(), e._a[Be] = a.getUTCDate()), t = 0; t < 3 && null == e._a[t]; ++t) e._a[t] = o[t] = i[t];
            for (; t < 7; t++) e._a[t] = o[t] = null == e._a[t] ? 2 === t ? 1 : 0 : e._a[t];
            24 === e._a[Re] && 0 === e._a[Ue] && 0 === e._a[$e] && 0 === e._a[Ve] && (e._nextDay = !0, e._a[Re] = 0), e._d = (e._useUTC ? bt : ft).apply(null, o), n = e._useUTC ? e._d.getUTCDay() : e._d.getDay(), null != e._tzm && e._d.setUTCMinutes(e._d.getUTCMinutes() - e._tzm), e._nextDay && (e._a[Re] = 24), e._w && void 0 !== e._w.d && e._w.d !== n && (v(e).weekdayMismatch = !0);
          }
        }
        function Ba(e) {
          var t, a, i, n, r, o, s, l, d;
          null != (t = e._w).GG || null != t.W || null != t.E ? (r = 1, o = 4, a = Oa(t.GG, e._a[Le], zt(Ga(), 1, 4).year), i = Oa(t.W, 1), ((n = Oa(t.E, 1)) < 1 || n > 7) && (l = !0)) : (r = e._locale._week.dow, o = e._locale._week.doy, d = zt(Ga(), r, o), a = Oa(t.gg, e._a[Le], d.year), i = Oa(t.w, d.week), null != t.d ? ((n = t.d) < 0 || n > 6) && (l = !0) : null != t.e ? (n = t.e + r, (t.e < 0 || t.e > 6) && (l = !0)) : n = r), i < 1 || i > wt(a, r, o) ? v(e)._overflowWeeks = !0 : null != l ? v(e)._overflowWeekday = !0 : (s = yt(a, i, n, r, o), e._a[Le] = s.year, e._dayOfYear = s.dayOfYear);
        }
        function Ra(e) {
          if (e._f !== i.ISO_8601) {
            if (e._f !== i.RFC_2822) {
              e._a = [], v(e).empty = !0;
              var t,
                a,
                n,
                r,
                o,
                s,
                l,
                d = "" + e._i,
                u = d.length,
                c = 0;
              for (l = (n = W(e._f, e._locale).match(O) || []).length, t = 0; t < l; t++) r = n[t], (a = (d.match(Ee(r, e)) || [])[0]) && ((o = d.substr(0, d.indexOf(a))).length > 0 && v(e).unusedInput.push(o), d = d.slice(d.indexOf(a) + a.length), c += a.length), B[r] ? (a ? v(e).empty = !1 : v(e).unusedTokens.push(r), He(r, a, e)) : e._strict && !a && v(e).unusedTokens.push(r);
              v(e).charsLeftOver = u - c, d.length > 0 && v(e).unusedInput.push(d), e._a[Re] <= 12 && !0 === v(e).bigHour && e._a[Re] > 0 && (v(e).bigHour = void 0), v(e).parsedDateParts = e._a.slice(0), v(e).meridiem = e._meridiem, e._a[Re] = Ua(e._locale, e._a[Re], e._meridiem), null !== (s = v(e).era) && (e._a[Le] = e._locale.erasConvertYear(s, e._a[Le])), Ia(e), ba(e);
            } else Ca(e);
          } else Ma(e);
        }
        function Ua(e, t, a) {
          var i;
          return null == a ? t : null != e.meridiemHour ? e.meridiemHour(t, a) : null != e.isPM ? ((i = e.isPM(a)) && t < 12 && (t += 12), i || 12 !== t || (t = 0), t) : t;
        }
        function $a(e) {
          var t,
            a,
            i,
            n,
            r,
            o,
            s = !1,
            l = e._f.length;
          if (0 === l) return v(e).invalidFormat = !0, void (e._d = new Date(NaN));
          for (n = 0; n < l; n++) r = 0, o = !1, t = y({}, e), null != e._useUTC && (t._useUTC = e._useUTC), t._f = e._f[n], Ra(t), _(t) && (o = !0), r += v(t).charsLeftOver, r += 10 * v(t).unusedTokens.length, v(t).score = r, s ? r < i && (i = r, a = t) : (null == i || r < i || o) && (i = r, a = t, o && (s = !0));
          m(e, a || t);
        }
        function Va(e) {
          if (!e._d) {
            var t = ie(e._i),
              a = void 0 === t.day ? t.date : t.day;
            e._a = p([t.year, t.month, a, t.hour, t.minute, t.second, t.millisecond], function (e) {
              return e && parseInt(e, 10);
            }), Ia(e);
          }
        }
        function Wa(e) {
          var t = new z(ba(Fa(e)));
          return t._nextDay && (t.add(1, "d"), t._nextDay = void 0), t;
        }
        function Fa(e) {
          var t = e._i,
            a = e._f;
          return e._locale = e._locale || _a(e._l), null === t || void 0 === a && "" === t ? f({
            nullInput: !0
          }) : ("string" == typeof t && (e._i = t = e._locale.preparse(t)), w(t) ? new z(ba(t)) : (c(t) ? e._d = t : r(a) ? $a(e) : a ? Ra(e) : qa(e), _(e) || (e._d = null), e));
        }
        function qa(e) {
          var t = e._i;
          d(t) ? e._d = new Date(i.now()) : c(t) ? e._d = new Date(t.valueOf()) : "string" == typeof t ? Ha(e) : r(t) ? (e._a = p(t.slice(0), function (e) {
            return parseInt(e, 10);
          }), Ia(e)) : o(t) ? Va(e) : u(t) ? e._d = new Date(t) : i.createFromInputFallback(e);
        }
        function Za(e, t, a, i, n) {
          var s = {};
          return !0 !== t && !1 !== t || (i = t, t = void 0), !0 !== a && !1 !== a || (i = a, a = void 0), (o(e) && l(e) || r(e) && 0 === e.length) && (e = void 0), s._isAMomentObject = !0, s._useUTC = s._isUTC = n, s._l = a, s._i = e, s._f = t, s._strict = i, Wa(s);
        }
        function Ga(e, t, a, i) {
          return Za(e, t, a, i, !1);
        }
        i.createFromInputFallback = A("value provided is not in a recognized RFC2822 or ISO format. moment construction falls back to js Date(), which is not reliable across all browsers and versions. Non RFC2822/ISO date formats are discouraged. Please refer to http://momentjs.com/guides/#/warnings/js-date/ for more info.", function (e) {
          e._d = new Date(e._i + (e._useUTC ? " UTC" : ""));
        }), i.ISO_8601 = function () {}, i.RFC_2822 = function () {};
        var Ya = A("moment().min is deprecated, use moment.max instead. http://momentjs.com/guides/#/warnings/min-max/", function () {
            var e = Ga.apply(null, arguments);
            return this.isValid() && e.isValid() ? e < this ? this : e : f();
          }),
          Ka = A("moment().max is deprecated, use moment.min instead. http://momentjs.com/guides/#/warnings/min-max/", function () {
            var e = Ga.apply(null, arguments);
            return this.isValid() && e.isValid() ? e > this ? this : e : f();
          });
        function Ja(e, t) {
          var a, i;
          if (1 === t.length && r(t[0]) && (t = t[0]), !t.length) return Ga();
          for (a = t[0], i = 1; i < t.length; ++i) t[i].isValid() && !t[i][e](a) || (a = t[i]);
          return a;
        }
        function Xa() {
          return Ja("isBefore", [].slice.call(arguments, 0));
        }
        function Qa() {
          return Ja("isAfter", [].slice.call(arguments, 0));
        }
        var ei = function () {
            return Date.now ? Date.now() : +new Date();
          },
          ti = ["year", "quarter", "month", "week", "day", "hour", "minute", "second", "millisecond"];
        function ai(e) {
          var t,
            a,
            i = !1,
            n = ti.length;
          for (t in e) if (s(e, t) && (-1 === Ze.call(ti, t) || null != e[t] && isNaN(e[t]))) return !1;
          for (a = 0; a < n; ++a) if (e[ti[a]]) {
            if (i) return !1;
            parseFloat(e[ti[a]]) !== Pe(e[ti[a]]) && (i = !0);
          }
          return !0;
        }
        function ii() {
          return this._isValid;
        }
        function ni() {
          return Ei(NaN);
        }
        function ri(e) {
          var t = ie(e),
            a = t.year || 0,
            i = t.quarter || 0,
            n = t.month || 0,
            r = t.week || t.isoWeek || 0,
            o = t.day || 0,
            s = t.hour || 0,
            l = t.minute || 0,
            d = t.second || 0,
            u = t.millisecond || 0;
          this._isValid = ai(t), this._milliseconds = +u + 1e3 * d + 6e4 * l + 1e3 * s * 60 * 60, this._days = +o + 7 * r, this._months = +n + 3 * i + 12 * a, this._data = {}, this._locale = _a(), this._bubble();
        }
        function oi(e) {
          return e instanceof ri;
        }
        function si(e) {
          return e < 0 ? -1 * Math.round(-1 * e) : Math.round(e);
        }
        function li(e, t, a) {
          var i,
            n = Math.min(e.length, t.length),
            r = Math.abs(e.length - t.length),
            o = 0;
          for (i = 0; i < n; i++) (a && e[i] !== t[i] || !a && Pe(e[i]) !== Pe(t[i])) && o++;
          return o + r;
        }
        function di(e, t) {
          R(e, 0, 0, function () {
            var e = this.utcOffset(),
              a = "+";
            return e < 0 && (e = -e, a = "-"), a + H(~~(e / 60), 2) + t + H(~~e % 60, 2);
          });
        }
        di("Z", ":"), di("ZZ", ""), xe("Z", ye), xe("ZZ", ye), Ne(["Z", "ZZ"], function (e, t, a) {
          a._useUTC = !0, a._tzm = ci(ye, e);
        });
        var ui = /([\+\-]|\d\d)/gi;
        function ci(e, t) {
          var a,
            i,
            n = (t || "").match(e);
          return null === n ? null : 0 === (i = 60 * (a = ((n[n.length - 1] || []) + "").match(ui) || ["-", 0, 0])[1] + Pe(a[2])) ? 0 : "+" === a[0] ? i : -i;
        }
        function pi(e, t) {
          var a, n;
          return t._isUTC ? (a = t.clone(), n = (w(e) || c(e) ? e.valueOf() : Ga(e).valueOf()) - a.valueOf(), a._d.setTime(a._d.valueOf() + n), i.updateOffset(a, !1), a) : Ga(e).local();
        }
        function mi(e) {
          return -Math.round(e._d.getTimezoneOffset());
        }
        function hi(e, t, a) {
          var n,
            r = this._offset || 0;
          if (!this.isValid()) return null != e ? this : NaN;
          if (null != e) {
            if ("string" == typeof e) {
              if (null === (e = ci(ye, e))) return this;
            } else Math.abs(e) < 16 && !a && (e *= 60);
            return !this._isUTC && t && (n = mi(this)), this._offset = e, this._isUTC = !0, null != n && this.add(n, "m"), r !== e && (!t || this._changeInProgress ? ji(this, Ei(e - r, "m"), 1, !1) : this._changeInProgress || (this._changeInProgress = !0, i.updateOffset(this, !0), this._changeInProgress = null)), this;
          }
          return this._isUTC ? r : mi(this);
        }
        function gi(e, t) {
          return null != e ? ("string" != typeof e && (e = -e), this.utcOffset(e, t), this) : -this.utcOffset();
        }
        function vi(e) {
          return this.utcOffset(0, e);
        }
        function _i(e) {
          return this._isUTC && (this.utcOffset(0, e), this._isUTC = !1, e && this.subtract(mi(this), "m")), this;
        }
        function fi() {
          if (null != this._tzm) this.utcOffset(this._tzm, !1, !0);else if ("string" == typeof this._i) {
            var e = ci(ke, this._i);
            null != e ? this.utcOffset(e) : this.utcOffset(0, !0);
          }
          return this;
        }
        function bi(e) {
          return !!this.isValid() && (e = e ? Ga(e).utcOffset() : 0, (this.utcOffset() - e) % 60 == 0);
        }
        function ki() {
          return this.utcOffset() > this.clone().month(0).utcOffset() || this.utcOffset() > this.clone().month(5).utcOffset();
        }
        function yi() {
          if (!d(this._isDSTShifted)) return this._isDSTShifted;
          var e,
            t = {};
          return y(t, this), (t = Fa(t))._a ? (e = t._isUTC ? h(t._a) : Ga(t._a), this._isDSTShifted = this.isValid() && li(t._a, e.toArray()) > 0) : this._isDSTShifted = !1, this._isDSTShifted;
        }
        function zi() {
          return !!this.isValid() && !this._isUTC;
        }
        function wi() {
          return !!this.isValid() && this._isUTC;
        }
        function Si() {
          return !!this.isValid() && this._isUTC && 0 === this._offset;
        }
        i.updateOffset = function () {};
        var Ai = /^(-|\+)?(?:(\d*)[. ])?(\d+):(\d+)(?::(\d+)(\.\d*)?)?$/,
          xi = /^(-|\+)?P(?:([-+]?[0-9,.]*)Y)?(?:([-+]?[0-9,.]*)M)?(?:([-+]?[0-9,.]*)W)?(?:([-+]?[0-9,.]*)D)?(?:T(?:([-+]?[0-9,.]*)H)?(?:([-+]?[0-9,.]*)M)?(?:([-+]?[0-9,.]*)S)?)?$/;
        function Ei(e, t) {
          var a,
            i,
            n,
            r = e,
            o = null;
          return oi(e) ? r = {
            ms: e._milliseconds,
            d: e._days,
            M: e._months
          } : u(e) || !isNaN(+e) ? (r = {}, t ? r[t] = +e : r.milliseconds = +e) : (o = Ai.exec(e)) ? (a = "-" === o[1] ? -1 : 1, r = {
            y: 0,
            d: Pe(o[Be]) * a,
            h: Pe(o[Re]) * a,
            m: Pe(o[Ue]) * a,
            s: Pe(o[$e]) * a,
            ms: Pe(si(1e3 * o[Ve])) * a
          }) : (o = xi.exec(e)) ? (a = "-" === o[1] ? -1 : 1, r = {
            y: Mi(o[2], a),
            M: Mi(o[3], a),
            w: Mi(o[4], a),
            d: Mi(o[5], a),
            h: Mi(o[6], a),
            m: Mi(o[7], a),
            s: Mi(o[8], a)
          }) : null == r ? r = {} : "object" == typeof r && ("from" in r || "to" in r) && (n = Di(Ga(r.from), Ga(r.to)), (r = {}).ms = n.milliseconds, r.M = n.months), i = new ri(r), oi(e) && s(e, "_locale") && (i._locale = e._locale), oi(e) && s(e, "_isValid") && (i._isValid = e._isValid), i;
        }
        function Mi(e, t) {
          var a = e && parseFloat(e.replace(",", "."));
          return (isNaN(a) ? 0 : a) * t;
        }
        function Ti(e, t) {
          var a = {};
          return a.months = t.month() - e.month() + 12 * (t.year() - e.year()), e.clone().add(a.months, "M").isAfter(t) && --a.months, a.milliseconds = +t - +e.clone().add(a.months, "M"), a;
        }
        function Di(e, t) {
          var a;
          return e.isValid() && t.isValid() ? (t = pi(t, e), e.isBefore(t) ? a = Ti(e, t) : ((a = Ti(t, e)).milliseconds = -a.milliseconds, a.months = -a.months), a) : {
            milliseconds: 0,
            months: 0
          };
        }
        function Pi(e, t) {
          return function (a, i) {
            var n;
            return null === i || isNaN(+i) || (M(t, "moment()." + t + "(period, number) is deprecated. Please use moment()." + t + "(number, period). See http://momentjs.com/guides/#/warnings/add-inverted-param/ for more info."), n = a, a = i, i = n), ji(this, Ei(a, i), e), this;
          };
        }
        function ji(e, t, a, n) {
          var r = t._milliseconds,
            o = si(t._days),
            s = si(t._months);
          e.isValid() && (n = null == n || n, s && pt(e, Je(e, "Month") + s * a), o && Xe(e, "Date", Je(e, "Date") + o * a), r && e._d.setTime(e._d.valueOf() + r * a), n && i.updateOffset(e, o || s));
        }
        Ei.fn = ri.prototype, Ei.invalid = ni;
        var Ni = Pi(1, "add"),
          Ci = Pi(-1, "subtract");
        function Hi(e) {
          return "string" == typeof e || e instanceof String;
        }
        function Oi(e) {
          return w(e) || c(e) || Hi(e) || u(e) || Ii(e) || Li(e) || null == e;
        }
        function Li(e) {
          var t,
            a,
            i = o(e) && !l(e),
            n = !1,
            r = ["years", "year", "y", "months", "month", "M", "days", "day", "d", "dates", "date", "D", "hours", "hour", "h", "minutes", "minute", "m", "seconds", "second", "s", "milliseconds", "millisecond", "ms"],
            d = r.length;
          for (t = 0; t < d; t += 1) a = r[t], n = n || s(e, a);
          return i && n;
        }
        function Ii(e) {
          var t = r(e),
            a = !1;
          return t && (a = 0 === e.filter(function (t) {
            return !u(t) && Hi(e);
          }).length), t && a;
        }
        function Bi(e) {
          var t,
            a,
            i = o(e) && !l(e),
            n = !1,
            r = ["sameDay", "nextDay", "lastDay", "nextWeek", "lastWeek", "sameElse"];
          for (t = 0; t < r.length; t += 1) a = r[t], n = n || s(e, a);
          return i && n;
        }
        function Ri(e, t) {
          var a = e.diff(t, "days", !0);
          return a < -6 ? "sameElse" : a < -1 ? "lastWeek" : a < 0 ? "lastDay" : a < 1 ? "sameDay" : a < 2 ? "nextDay" : a < 7 ? "nextWeek" : "sameElse";
        }
        function Ui(e, t) {
          1 === arguments.length && (arguments[0] ? Oi(arguments[0]) ? (e = arguments[0], t = void 0) : Bi(arguments[0]) && (t = arguments[0], e = void 0) : (e = void 0, t = void 0));
          var a = e || Ga(),
            n = pi(a, this).startOf("day"),
            r = i.calendarFormat(this, n) || "sameElse",
            o = t && (T(t[r]) ? t[r].call(this, a) : t[r]);
          return this.format(o || this.localeData().calendar(r, this, Ga(a)));
        }
        function $i() {
          return new z(this);
        }
        function Vi(e, t) {
          var a = w(e) ? e : Ga(e);
          return !(!this.isValid() || !a.isValid()) && ("millisecond" === (t = ae(t) || "millisecond") ? this.valueOf() > a.valueOf() : a.valueOf() < this.clone().startOf(t).valueOf());
        }
        function Wi(e, t) {
          var a = w(e) ? e : Ga(e);
          return !(!this.isValid() || !a.isValid()) && ("millisecond" === (t = ae(t) || "millisecond") ? this.valueOf() < a.valueOf() : this.clone().endOf(t).valueOf() < a.valueOf());
        }
        function Fi(e, t, a, i) {
          var n = w(e) ? e : Ga(e),
            r = w(t) ? t : Ga(t);
          return !!(this.isValid() && n.isValid() && r.isValid()) && ("(" === (i = i || "()")[0] ? this.isAfter(n, a) : !this.isBefore(n, a)) && (")" === i[1] ? this.isBefore(r, a) : !this.isAfter(r, a));
        }
        function qi(e, t) {
          var a,
            i = w(e) ? e : Ga(e);
          return !(!this.isValid() || !i.isValid()) && ("millisecond" === (t = ae(t) || "millisecond") ? this.valueOf() === i.valueOf() : (a = i.valueOf(), this.clone().startOf(t).valueOf() <= a && a <= this.clone().endOf(t).valueOf()));
        }
        function Zi(e, t) {
          return this.isSame(e, t) || this.isAfter(e, t);
        }
        function Gi(e, t) {
          return this.isSame(e, t) || this.isBefore(e, t);
        }
        function Yi(e, t, a) {
          var i, n, r;
          if (!this.isValid()) return NaN;
          if (!(i = pi(e, this)).isValid()) return NaN;
          switch (n = 6e4 * (i.utcOffset() - this.utcOffset()), t = ae(t)) {
            case "year":
              r = Ki(this, i) / 12;
              break;
            case "month":
              r = Ki(this, i);
              break;
            case "quarter":
              r = Ki(this, i) / 3;
              break;
            case "second":
              r = (this - i) / 1e3;
              break;
            case "minute":
              r = (this - i) / 6e4;
              break;
            case "hour":
              r = (this - i) / 36e5;
              break;
            case "day":
              r = (this - i - n) / 864e5;
              break;
            case "week":
              r = (this - i - n) / 6048e5;
              break;
            default:
              r = this - i;
          }
          return a ? r : De(r);
        }
        function Ki(e, t) {
          if (e.date() < t.date()) return -Ki(t, e);
          var a = 12 * (t.year() - e.year()) + (t.month() - e.month()),
            i = e.clone().add(a, "months");
          return -(a + (t - i < 0 ? (t - i) / (i - e.clone().add(a - 1, "months")) : (t - i) / (e.clone().add(a + 1, "months") - i))) || 0;
        }
        function Ji() {
          return this.clone().locale("en").format("ddd MMM DD YYYY HH:mm:ss [GMT]ZZ");
        }
        function Xi(e) {
          if (!this.isValid()) return null;
          var t = !0 !== e,
            a = t ? this.clone().utc() : this;
          return a.year() < 0 || a.year() > 9999 ? V(a, t ? "YYYYYY-MM-DD[T]HH:mm:ss.SSS[Z]" : "YYYYYY-MM-DD[T]HH:mm:ss.SSSZ") : T(Date.prototype.toISOString) ? t ? this.toDate().toISOString() : new Date(this.valueOf() + 60 * this.utcOffset() * 1e3).toISOString().replace("Z", V(a, "Z")) : V(a, t ? "YYYY-MM-DD[T]HH:mm:ss.SSS[Z]" : "YYYY-MM-DD[T]HH:mm:ss.SSSZ");
        }
        function Qi() {
          if (!this.isValid()) return "moment.invalid(/* " + this._i + " */)";
          var e,
            t,
            a,
            i,
            n = "moment",
            r = "";
          return this.isLocal() || (n = 0 === this.utcOffset() ? "moment.utc" : "moment.parseZone", r = "Z"), e = "[" + n + '("]', t = 0 <= this.year() && this.year() <= 9999 ? "YYYY" : "YYYYYY", a = "-MM-DD[T]HH:mm:ss.SSS", i = r + '[")]', this.format(e + t + a + i);
        }
        function en(e) {
          e || (e = this.isUtc() ? i.defaultFormatUtc : i.defaultFormat);
          var t = V(this, e);
          return this.localeData().postformat(t);
        }
        function tn(e, t) {
          return this.isValid() && (w(e) && e.isValid() || Ga(e).isValid()) ? Ei({
            to: this,
            from: e
          }).locale(this.locale()).humanize(!t) : this.localeData().invalidDate();
        }
        function an(e) {
          return this.from(Ga(), e);
        }
        function nn(e, t) {
          return this.isValid() && (w(e) && e.isValid() || Ga(e).isValid()) ? Ei({
            from: this,
            to: e
          }).locale(this.locale()).humanize(!t) : this.localeData().invalidDate();
        }
        function rn(e) {
          return this.to(Ga(), e);
        }
        function on(e) {
          var t;
          return void 0 === e ? this._locale._abbr : (null != (t = _a(e)) && (this._locale = t), this);
        }
        i.defaultFormat = "YYYY-MM-DDTHH:mm:ssZ", i.defaultFormatUtc = "YYYY-MM-DDTHH:mm:ss[Z]";
        var sn = A("moment().lang() is deprecated. Instead, use moment().localeData() to get the language configuration. Use moment().locale() to change languages.", function (e) {
          return void 0 === e ? this.localeData() : this.locale(e);
        });
        function ln() {
          return this._locale;
        }
        var dn = 1e3,
          un = 60 * dn,
          cn = 60 * un,
          pn = 3506328 * cn;
        function mn(e, t) {
          return (e % t + t) % t;
        }
        function hn(e, t, a) {
          return e < 100 && e >= 0 ? new Date(e + 400, t, a) - pn : new Date(e, t, a).valueOf();
        }
        function gn(e, t, a) {
          return e < 100 && e >= 0 ? Date.UTC(e + 400, t, a) - pn : Date.UTC(e, t, a);
        }
        function vn(e) {
          var t, a;
          if (void 0 === (e = ae(e)) || "millisecond" === e || !this.isValid()) return this;
          switch (a = this._isUTC ? gn : hn, e) {
            case "year":
              t = a(this.year(), 0, 1);
              break;
            case "quarter":
              t = a(this.year(), this.month() - this.month() % 3, 1);
              break;
            case "month":
              t = a(this.year(), this.month(), 1);
              break;
            case "week":
              t = a(this.year(), this.month(), this.date() - this.weekday());
              break;
            case "isoWeek":
              t = a(this.year(), this.month(), this.date() - (this.isoWeekday() - 1));
              break;
            case "day":
            case "date":
              t = a(this.year(), this.month(), this.date());
              break;
            case "hour":
              t = this._d.valueOf(), t -= mn(t + (this._isUTC ? 0 : this.utcOffset() * un), cn);
              break;
            case "minute":
              t = this._d.valueOf(), t -= mn(t, un);
              break;
            case "second":
              t = this._d.valueOf(), t -= mn(t, dn);
          }
          return this._d.setTime(t), i.updateOffset(this, !0), this;
        }
        function _n(e) {
          var t, a;
          if (void 0 === (e = ae(e)) || "millisecond" === e || !this.isValid()) return this;
          switch (a = this._isUTC ? gn : hn, e) {
            case "year":
              t = a(this.year() + 1, 0, 1) - 1;
              break;
            case "quarter":
              t = a(this.year(), this.month() - this.month() % 3 + 3, 1) - 1;
              break;
            case "month":
              t = a(this.year(), this.month() + 1, 1) - 1;
              break;
            case "week":
              t = a(this.year(), this.month(), this.date() - this.weekday() + 7) - 1;
              break;
            case "isoWeek":
              t = a(this.year(), this.month(), this.date() - (this.isoWeekday() - 1) + 7) - 1;
              break;
            case "day":
            case "date":
              t = a(this.year(), this.month(), this.date() + 1) - 1;
              break;
            case "hour":
              t = this._d.valueOf(), t += cn - mn(t + (this._isUTC ? 0 : this.utcOffset() * un), cn) - 1;
              break;
            case "minute":
              t = this._d.valueOf(), t += un - mn(t, un) - 1;
              break;
            case "second":
              t = this._d.valueOf(), t += dn - mn(t, dn) - 1;
          }
          return this._d.setTime(t), i.updateOffset(this, !0), this;
        }
        function fn() {
          return this._d.valueOf() - 6e4 * (this._offset || 0);
        }
        function bn() {
          return Math.floor(this.valueOf() / 1e3);
        }
        function kn() {
          return new Date(this.valueOf());
        }
        function yn() {
          var e = this;
          return [e.year(), e.month(), e.date(), e.hour(), e.minute(), e.second(), e.millisecond()];
        }
        function zn() {
          var e = this;
          return {
            years: e.year(),
            months: e.month(),
            date: e.date(),
            hours: e.hours(),
            minutes: e.minutes(),
            seconds: e.seconds(),
            milliseconds: e.milliseconds()
          };
        }
        function wn() {
          return this.isValid() ? this.toISOString() : null;
        }
        function Sn() {
          return _(this);
        }
        function An() {
          return m({}, v(this));
        }
        function xn() {
          return v(this).overflow;
        }
        function En() {
          return {
            input: this._i,
            format: this._f,
            locale: this._locale,
            isUTC: this._isUTC,
            strict: this._strict
          };
        }
        function Mn(e, t) {
          var a,
            n,
            r,
            o = this._eras || _a("en")._eras;
          for (a = 0, n = o.length; a < n; ++a) switch ("string" == typeof o[a].since && (r = i(o[a].since).startOf("day"), o[a].since = r.valueOf()), typeof o[a].until) {
            case "undefined":
              o[a].until = 1 / 0;
              break;
            case "string":
              r = i(o[a].until).startOf("day").valueOf(), o[a].until = r.valueOf();
          }
          return o;
        }
        function Tn(e, t, a) {
          var i,
            n,
            r,
            o,
            s,
            l = this.eras();
          for (e = e.toUpperCase(), i = 0, n = l.length; i < n; ++i) if (r = l[i].name.toUpperCase(), o = l[i].abbr.toUpperCase(), s = l[i].narrow.toUpperCase(), a) switch (t) {
            case "N":
            case "NN":
            case "NNN":
              if (o === e) return l[i];
              break;
            case "NNNN":
              if (r === e) return l[i];
              break;
            case "NNNNN":
              if (s === e) return l[i];
          } else if ([r, o, s].indexOf(e) >= 0) return l[i];
        }
        function Dn(e, t) {
          var a = e.since <= e.until ? 1 : -1;
          return void 0 === t ? i(e.since).year() : i(e.since).year() + (t - e.offset) * a;
        }
        function Pn() {
          var e,
            t,
            a,
            i = this.localeData().eras();
          for (e = 0, t = i.length; e < t; ++e) {
            if (a = this.clone().startOf("day").valueOf(), i[e].since <= a && a <= i[e].until) return i[e].name;
            if (i[e].until <= a && a <= i[e].since) return i[e].name;
          }
          return "";
        }
        function jn() {
          var e,
            t,
            a,
            i = this.localeData().eras();
          for (e = 0, t = i.length; e < t; ++e) {
            if (a = this.clone().startOf("day").valueOf(), i[e].since <= a && a <= i[e].until) return i[e].narrow;
            if (i[e].until <= a && a <= i[e].since) return i[e].narrow;
          }
          return "";
        }
        function Nn() {
          var e,
            t,
            a,
            i = this.localeData().eras();
          for (e = 0, t = i.length; e < t; ++e) {
            if (a = this.clone().startOf("day").valueOf(), i[e].since <= a && a <= i[e].until) return i[e].abbr;
            if (i[e].until <= a && a <= i[e].since) return i[e].abbr;
          }
          return "";
        }
        function Hn() {
          var e,
            t,
            a,
            n,
            r = this.localeData().eras();
          for (e = 0, t = r.length; e < t; ++e) if (a = r[e].since <= r[e].until ? 1 : -1, n = this.clone().startOf("day").valueOf(), r[e].since <= n && n <= r[e].until || r[e].until <= n && n <= r[e].since) return (this.year() - i(r[e].since).year()) * a + r[e].offset;
          return this.year();
        }
        function On(e) {
          return s(this, "_erasNameRegex") || Vn.call(this), e ? this._erasNameRegex : this._erasRegex;
        }
        function Ln(e) {
          return s(this, "_erasAbbrRegex") || Vn.call(this), e ? this._erasAbbrRegex : this._erasRegex;
        }
        function In(e) {
          return s(this, "_erasNarrowRegex") || Vn.call(this), e ? this._erasNarrowRegex : this._erasRegex;
        }
        function Bn(e, t) {
          return t.erasAbbrRegex(e);
        }
        function Rn(e, t) {
          return t.erasNameRegex(e);
        }
        function Un(e, t) {
          return t.erasNarrowRegex(e);
        }
        function $n(e, t) {
          return t._eraYearOrdinalRegex || fe;
        }
        function Vn() {
          var e,
            t,
            a,
            i,
            n,
            r = [],
            o = [],
            s = [],
            l = [],
            d = this.eras();
          for (e = 0, t = d.length; e < t; ++e) a = Te(d[e].name), i = Te(d[e].abbr), n = Te(d[e].narrow), o.push(a), r.push(i), s.push(n), l.push(a), l.push(i), l.push(n);
          this._erasRegex = new RegExp("^(" + l.join("|") + ")", "i"), this._erasNameRegex = new RegExp("^(" + o.join("|") + ")", "i"), this._erasAbbrRegex = new RegExp("^(" + r.join("|") + ")", "i"), this._erasNarrowRegex = new RegExp("^(" + s.join("|") + ")", "i");
        }
        function Wn(e, t) {
          R(0, [e, e.length], 0, t);
        }
        function Fn(e) {
          return Jn.call(this, e, this.week(), this.weekday() + this.localeData()._week.dow, this.localeData()._week.dow, this.localeData()._week.doy);
        }
        function qn(e) {
          return Jn.call(this, e, this.isoWeek(), this.isoWeekday(), 1, 4);
        }
        function Zn() {
          return wt(this.year(), 1, 4);
        }
        function Gn() {
          return wt(this.isoWeekYear(), 1, 4);
        }
        function Yn() {
          var e = this.localeData()._week;
          return wt(this.year(), e.dow, e.doy);
        }
        function Kn() {
          var e = this.localeData()._week;
          return wt(this.weekYear(), e.dow, e.doy);
        }
        function Jn(e, t, a, i, n) {
          var r;
          return null == e ? zt(this, i, n).year : (t > (r = wt(e, i, n)) && (t = r), Xn.call(this, e, t, a, i, n));
        }
        function Xn(e, t, a, i, n) {
          var r = yt(e, t, a, i, n),
            o = bt(r.year, 0, r.dayOfYear);
          return this.year(o.getUTCFullYear()), this.month(o.getUTCMonth()), this.date(o.getUTCDate()), this;
        }
        function Qn(e) {
          return null == e ? Math.ceil((this.month() + 1) / 3) : this.month(3 * (e - 1) + this.month() % 3);
        }
        R("N", 0, 0, "eraAbbr"), R("NN", 0, 0, "eraAbbr"), R("NNN", 0, 0, "eraAbbr"), R("NNNN", 0, 0, "eraName"), R("NNNNN", 0, 0, "eraNarrow"), R("y", ["y", 1], "yo", "eraYear"), R("y", ["yy", 2], 0, "eraYear"), R("y", ["yyy", 3], 0, "eraYear"), R("y", ["yyyy", 4], 0, "eraYear"), xe("N", Bn), xe("NN", Bn), xe("NNN", Bn), xe("NNNN", Rn), xe("NNNNN", Un), Ne(["N", "NN", "NNN", "NNNN", "NNNNN"], function (e, t, a, i) {
          var n = a._locale.erasParse(e, i, a._strict);
          n ? v(a).era = n : v(a).invalidEra = e;
        }), xe("y", fe), xe("yy", fe), xe("yyy", fe), xe("yyyy", fe), xe("yo", $n), Ne(["y", "yy", "yyy", "yyyy"], Le), Ne(["yo"], function (e, t, a, i) {
          var n;
          a._locale._eraYearOrdinalRegex && (n = e.match(a._locale._eraYearOrdinalRegex)), a._locale.eraYearOrdinalParse ? t[Le] = a._locale.eraYearOrdinalParse(e, n) : t[Le] = parseInt(e, 10);
        }), R(0, ["gg", 2], 0, function () {
          return this.weekYear() % 100;
        }), R(0, ["GG", 2], 0, function () {
          return this.isoWeekYear() % 100;
        }), Wn("gggg", "weekYear"), Wn("ggggg", "weekYear"), Wn("GGGG", "isoWeekYear"), Wn("GGGGG", "isoWeekYear"), xe("G", be), xe("g", be), xe("GG", pe, le), xe("gg", pe, le), xe("GGGG", ve, ue), xe("gggg", ve, ue), xe("GGGGG", _e, ce), xe("ggggg", _e, ce), Ce(["gggg", "ggggg", "GGGG", "GGGGG"], function (e, t, a, i) {
          t[i.substr(0, 2)] = Pe(e);
        }), Ce(["gg", "GG"], function (e, t, a, n) {
          t[n] = i.parseTwoDigitYear(e);
        }), R("Q", 0, "Qo", "quarter"), xe("Q", se), Ne("Q", function (e, t) {
          t[Ie] = 3 * (Pe(e) - 1);
        }), R("D", ["DD", 2], "Do", "date"), xe("D", pe, Se), xe("DD", pe, le), xe("Do", function (e, t) {
          return e ? t._dayOfMonthOrdinalParse || t._ordinalParse : t._dayOfMonthOrdinalParseLenient;
        }), Ne(["D", "DD"], Be), Ne("Do", function (e, t) {
          t[Be] = Pe(e.match(pe)[0]);
        });
        var er = Ke("Date", !0);
        function tr(e) {
          var t = Math.round((this.clone().startOf("day") - this.clone().startOf("year")) / 864e5) + 1;
          return null == e ? t : this.add(e - t, "d");
        }
        R("DDD", ["DDDD", 3], "DDDo", "dayOfYear"), xe("DDD", ge), xe("DDDD", de), Ne(["DDD", "DDDD"], function (e, t, a) {
          a._dayOfYear = Pe(e);
        }), R("m", ["mm", 2], 0, "minute"), xe("m", pe, Ae), xe("mm", pe, le), Ne(["m", "mm"], Ue);
        var ar = Ke("Minutes", !1);
        R("s", ["ss", 2], 0, "second"), xe("s", pe, Ae), xe("ss", pe, le), Ne(["s", "ss"], $e);
        var ir,
          nr,
          rr = Ke("Seconds", !1);
        for (R("S", 0, 0, function () {
          return ~~(this.millisecond() / 100);
        }), R(0, ["SS", 2], 0, function () {
          return ~~(this.millisecond() / 10);
        }), R(0, ["SSS", 3], 0, "millisecond"), R(0, ["SSSS", 4], 0, function () {
          return 10 * this.millisecond();
        }), R(0, ["SSSSS", 5], 0, function () {
          return 100 * this.millisecond();
        }), R(0, ["SSSSSS", 6], 0, function () {
          return 1e3 * this.millisecond();
        }), R(0, ["SSSSSSS", 7], 0, function () {
          return 1e4 * this.millisecond();
        }), R(0, ["SSSSSSSS", 8], 0, function () {
          return 1e5 * this.millisecond();
        }), R(0, ["SSSSSSSSS", 9], 0, function () {
          return 1e6 * this.millisecond();
        }), xe("S", ge, se), xe("SS", ge, le), xe("SSS", ge, de), ir = "SSSS"; ir.length <= 9; ir += "S") xe(ir, fe);
        function or(e, t) {
          t[Ve] = Pe(1e3 * ("0." + e));
        }
        for (ir = "S"; ir.length <= 9; ir += "S") Ne(ir, or);
        function sr() {
          return this._isUTC ? "UTC" : "";
        }
        function lr() {
          return this._isUTC ? "Coordinated Universal Time" : "";
        }
        nr = Ke("Milliseconds", !1), R("z", 0, 0, "zoneAbbr"), R("zz", 0, 0, "zoneName");
        var dr = z.prototype;
        function ur(e) {
          return Ga(1e3 * e);
        }
        function cr() {
          return Ga.apply(null, arguments).parseZone();
        }
        function pr(e) {
          return e;
        }
        dr.add = Ni, dr.calendar = Ui, dr.clone = $i, dr.diff = Yi, dr.endOf = _n, dr.format = en, dr.from = tn, dr.fromNow = an, dr.to = nn, dr.toNow = rn, dr.get = Qe, dr.invalidAt = xn, dr.isAfter = Vi, dr.isBefore = Wi, dr.isBetween = Fi, dr.isSame = qi, dr.isSameOrAfter = Zi, dr.isSameOrBefore = Gi, dr.isValid = Sn, dr.lang = sn, dr.locale = on, dr.localeData = ln, dr.max = Ka, dr.min = Ya, dr.parsingFlags = An, dr.set = et, dr.startOf = vn, dr.subtract = Ci, dr.toArray = yn, dr.toObject = zn, dr.toDate = kn, dr.toISOString = Xi, dr.inspect = Qi, "undefined" != typeof Symbol && null != Symbol.for && (dr[Symbol.for("nodejs.util.inspect.custom")] = function () {
          return "Moment<" + this.format() + ">";
        }), dr.toJSON = wn, dr.toString = Ji, dr.unix = bn, dr.valueOf = fn, dr.creationData = En, dr.eraName = Pn, dr.eraNarrow = jn, dr.eraAbbr = Nn, dr.eraYear = Hn, dr.year = Ge, dr.isLeapYear = Ye, dr.weekYear = Fn, dr.isoWeekYear = qn, dr.quarter = dr.quarters = Qn, dr.month = mt, dr.daysInMonth = ht, dr.week = dr.weeks = Mt, dr.isoWeek = dr.isoWeeks = Tt, dr.weeksInYear = Yn, dr.weeksInWeekYear = Kn, dr.isoWeeksInYear = Zn, dr.isoWeeksInISOWeekYear = Gn, dr.date = er, dr.day = dr.days = Wt, dr.weekday = Ft, dr.isoWeekday = qt, dr.dayOfYear = tr, dr.hour = dr.hours = ia, dr.minute = dr.minutes = ar, dr.second = dr.seconds = rr, dr.millisecond = dr.milliseconds = nr, dr.utcOffset = hi, dr.utc = vi, dr.local = _i, dr.parseZone = fi, dr.hasAlignedHourOffset = bi, dr.isDST = ki, dr.isLocal = zi, dr.isUtcOffset = wi, dr.isUtc = Si, dr.isUTC = Si, dr.zoneAbbr = sr, dr.zoneName = lr, dr.dates = A("dates accessor is deprecated. Use date instead.", er), dr.months = A("months accessor is deprecated. Use month instead", mt), dr.years = A("years accessor is deprecated. Use year instead", Ge), dr.zone = A("moment().zone is deprecated, use moment().utcOffset instead. http://momentjs.com/guides/#/warnings/zone/", gi), dr.isDSTShifted = A("isDSTShifted is deprecated. See http://momentjs.com/guides/#/warnings/dst-shifted/ for more information", yi);
        var mr = j.prototype;
        function hr(e, t, a, i) {
          var n = _a(),
            r = h().set(i, t);
          return n[a](r, e);
        }
        function gr(e, t, a) {
          if (u(e) && (t = e, e = void 0), e = e || "", null != t) return hr(e, t, a, "month");
          var i,
            n = [];
          for (i = 0; i < 12; i++) n[i] = hr(e, i, a, "month");
          return n;
        }
        function vr(e, t, a, i) {
          "boolean" == typeof e ? (u(t) && (a = t, t = void 0), t = t || "") : (a = t = e, e = !1, u(t) && (a = t, t = void 0), t = t || "");
          var n,
            r = _a(),
            o = e ? r._week.dow : 0,
            s = [];
          if (null != a) return hr(t, (a + o) % 7, i, "day");
          for (n = 0; n < 7; n++) s[n] = hr(t, (n + o) % 7, i, "day");
          return s;
        }
        function _r(e, t) {
          return gr(e, t, "months");
        }
        function fr(e, t) {
          return gr(e, t, "monthsShort");
        }
        function br(e, t, a) {
          return vr(e, t, a, "weekdays");
        }
        function kr(e, t, a) {
          return vr(e, t, a, "weekdaysShort");
        }
        function yr(e, t, a) {
          return vr(e, t, a, "weekdaysMin");
        }
        mr.calendar = C, mr.longDateFormat = q, mr.invalidDate = G, mr.ordinal = J, mr.preparse = pr, mr.postformat = pr, mr.relativeTime = Q, mr.pastFuture = ee, mr.set = D, mr.eras = Mn, mr.erasParse = Tn, mr.erasConvertYear = Dn, mr.erasAbbrRegex = Ln, mr.erasNameRegex = On, mr.erasNarrowRegex = In, mr.months = lt, mr.monthsShort = dt, mr.monthsParse = ct, mr.monthsRegex = vt, mr.monthsShortRegex = gt, mr.week = St, mr.firstDayOfYear = Et, mr.firstDayOfWeek = xt, mr.weekdays = Bt, mr.weekdaysMin = Ut, mr.weekdaysShort = Rt, mr.weekdaysParse = Vt, mr.weekdaysRegex = Zt, mr.weekdaysShortRegex = Gt, mr.weekdaysMinRegex = Yt, mr.isPM = ta, mr.meridiem = na, ha("en", {
          eras: [{
            since: "0001-01-01",
            until: 1 / 0,
            offset: 1,
            name: "Anno Domini",
            narrow: "AD",
            abbr: "AD"
          }, {
            since: "0000-12-31",
            until: -1 / 0,
            offset: 1,
            name: "Before Christ",
            narrow: "BC",
            abbr: "BC"
          }],
          dayOfMonthOrdinalParse: /\d{1,2}(th|st|nd|rd)/,
          ordinal: function (e) {
            var t = e % 10;
            return e + (1 === Pe(e % 100 / 10) ? "th" : 1 === t ? "st" : 2 === t ? "nd" : 3 === t ? "rd" : "th");
          }
        }), i.lang = A("moment.lang is deprecated. Use moment.locale instead.", ha), i.langData = A("moment.langData is deprecated. Use moment.localeData instead.", _a);
        var zr = Math.abs;
        function wr() {
          var e = this._data;
          return this._milliseconds = zr(this._milliseconds), this._days = zr(this._days), this._months = zr(this._months), e.milliseconds = zr(e.milliseconds), e.seconds = zr(e.seconds), e.minutes = zr(e.minutes), e.hours = zr(e.hours), e.months = zr(e.months), e.years = zr(e.years), this;
        }
        function Sr(e, t, a, i) {
          var n = Ei(t, a);
          return e._milliseconds += i * n._milliseconds, e._days += i * n._days, e._months += i * n._months, e._bubble();
        }
        function Ar(e, t) {
          return Sr(this, e, t, 1);
        }
        function xr(e, t) {
          return Sr(this, e, t, -1);
        }
        function Er(e) {
          return e < 0 ? Math.floor(e) : Math.ceil(e);
        }
        function Mr() {
          var e,
            t,
            a,
            i,
            n,
            r = this._milliseconds,
            o = this._days,
            s = this._months,
            l = this._data;
          return r >= 0 && o >= 0 && s >= 0 || r <= 0 && o <= 0 && s <= 0 || (r += 864e5 * Er(Dr(s) + o), o = 0, s = 0), l.milliseconds = r % 1e3, e = De(r / 1e3), l.seconds = e % 60, t = De(e / 60), l.minutes = t % 60, a = De(t / 60), l.hours = a % 24, o += De(a / 24), s += n = De(Tr(o)), o -= Er(Dr(n)), i = De(s / 12), s %= 12, l.days = o, l.months = s, l.years = i, this;
        }
        function Tr(e) {
          return 4800 * e / 146097;
        }
        function Dr(e) {
          return 146097 * e / 4800;
        }
        function Pr(e) {
          if (!this.isValid()) return NaN;
          var t,
            a,
            i = this._milliseconds;
          if ("month" === (e = ae(e)) || "quarter" === e || "year" === e) switch (t = this._days + i / 864e5, a = this._months + Tr(t), e) {
            case "month":
              return a;
            case "quarter":
              return a / 3;
            case "year":
              return a / 12;
          } else switch (t = this._days + Math.round(Dr(this._months)), e) {
            case "week":
              return t / 7 + i / 6048e5;
            case "day":
              return t + i / 864e5;
            case "hour":
              return 24 * t + i / 36e5;
            case "minute":
              return 1440 * t + i / 6e4;
            case "second":
              return 86400 * t + i / 1e3;
            case "millisecond":
              return Math.floor(864e5 * t) + i;
            default:
              throw new Error("Unknown unit " + e);
          }
        }
        function jr(e) {
          return function () {
            return this.as(e);
          };
        }
        var Nr = jr("ms"),
          Cr = jr("s"),
          Hr = jr("m"),
          Or = jr("h"),
          Lr = jr("d"),
          Ir = jr("w"),
          Br = jr("M"),
          Rr = jr("Q"),
          Ur = jr("y"),
          $r = Nr;
        function Vr() {
          return Ei(this);
        }
        function Wr(e) {
          return e = ae(e), this.isValid() ? this[e + "s"]() : NaN;
        }
        function Fr(e) {
          return function () {
            return this.isValid() ? this._data[e] : NaN;
          };
        }
        var qr = Fr("milliseconds"),
          Zr = Fr("seconds"),
          Gr = Fr("minutes"),
          Yr = Fr("hours"),
          Kr = Fr("days"),
          Jr = Fr("months"),
          Xr = Fr("years");
        function Qr() {
          return De(this.days() / 7);
        }
        var eo = Math.round,
          to = {
            ss: 44,
            s: 45,
            m: 45,
            h: 22,
            d: 26,
            w: null,
            M: 11
          };
        function ao(e, t, a, i, n) {
          return n.relativeTime(t || 1, !!a, e, i);
        }
        function io(e, t, a, i) {
          var n = Ei(e).abs(),
            r = eo(n.as("s")),
            o = eo(n.as("m")),
            s = eo(n.as("h")),
            l = eo(n.as("d")),
            d = eo(n.as("M")),
            u = eo(n.as("w")),
            c = eo(n.as("y")),
            p = r <= a.ss && ["s", r] || r < a.s && ["ss", r] || o <= 1 && ["m"] || o < a.m && ["mm", o] || s <= 1 && ["h"] || s < a.h && ["hh", s] || l <= 1 && ["d"] || l < a.d && ["dd", l];
          return null != a.w && (p = p || u <= 1 && ["w"] || u < a.w && ["ww", u]), (p = p || d <= 1 && ["M"] || d < a.M && ["MM", d] || c <= 1 && ["y"] || ["yy", c])[2] = t, p[3] = +e > 0, p[4] = i, ao.apply(null, p);
        }
        function no(e) {
          return void 0 === e ? eo : "function" == typeof e && (eo = e, !0);
        }
        function ro(e, t) {
          return void 0 !== to[e] && (void 0 === t ? to[e] : (to[e] = t, "s" === e && (to.ss = t - 1), !0));
        }
        function oo(e, t) {
          if (!this.isValid()) return this.localeData().invalidDate();
          var a,
            i,
            n = !1,
            r = to;
          return "object" == typeof e && (t = e, e = !1), "boolean" == typeof e && (n = e), "object" == typeof t && (r = Object.assign({}, to, t), null != t.s && null == t.ss && (r.ss = t.s - 1)), i = io(this, !n, r, a = this.localeData()), n && (i = a.pastFuture(+this, i)), a.postformat(i);
        }
        var so = Math.abs;
        function lo(e) {
          return (e > 0) - (e < 0) || +e;
        }
        function uo() {
          if (!this.isValid()) return this.localeData().invalidDate();
          var e,
            t,
            a,
            i,
            n,
            r,
            o,
            s,
            l = so(this._milliseconds) / 1e3,
            d = so(this._days),
            u = so(this._months),
            c = this.asSeconds();
          return c ? (e = De(l / 60), t = De(e / 60), l %= 60, e %= 60, a = De(u / 12), u %= 12, i = l ? l.toFixed(3).replace(/\.?0+$/, "") : "", n = c < 0 ? "-" : "", r = lo(this._months) !== lo(c) ? "-" : "", o = lo(this._days) !== lo(c) ? "-" : "", s = lo(this._milliseconds) !== lo(c) ? "-" : "", n + "P" + (a ? r + a + "Y" : "") + (u ? r + u + "M" : "") + (d ? o + d + "D" : "") + (t || e || l ? "T" : "") + (t ? s + t + "H" : "") + (e ? s + e + "M" : "") + (l ? s + i + "S" : "")) : "P0D";
        }
        var co = ri.prototype;
        return co.isValid = ii, co.abs = wr, co.add = Ar, co.subtract = xr, co.as = Pr, co.asMilliseconds = Nr, co.asSeconds = Cr, co.asMinutes = Hr, co.asHours = Or, co.asDays = Lr, co.asWeeks = Ir, co.asMonths = Br, co.asQuarters = Rr, co.asYears = Ur, co.valueOf = $r, co._bubble = Mr, co.clone = Vr, co.get = Wr, co.milliseconds = qr, co.seconds = Zr, co.minutes = Gr, co.hours = Yr, co.days = Kr, co.weeks = Qr, co.months = Jr, co.years = Xr, co.humanize = oo, co.toISOString = uo, co.toString = uo, co.toJSON = uo, co.locale = on, co.localeData = ln, co.toIsoString = A("toIsoString() is deprecated. Please use toISOString() instead (notice the capitals)", uo), co.lang = sn, R("X", 0, 0, "unix"), R("x", 0, 0, "valueOf"), xe("x", be), xe("X", ze), Ne("X", function (e, t, a) {
          a._d = new Date(1e3 * parseFloat(e));
        }), Ne("x", function (e, t, a) {
          a._d = new Date(Pe(e));
        }),
        //! moment.js
        i.version = "2.30.1", n(Ga), i.fn = dr, i.min = Xa, i.max = Qa, i.now = ei, i.utc = h, i.unix = ur, i.months = _r, i.isDate = c, i.locale = ha, i.invalid = f, i.duration = Ei, i.isMoment = w, i.weekdays = br, i.parseZone = cr, i.localeData = _a, i.isDuration = oi, i.monthsShort = fr, i.weekdaysMin = yr, i.defineLocale = ga, i.updateLocale = va, i.locales = fa, i.weekdaysShort = kr, i.normalizeUnits = ae, i.relativeTimeRounding = no, i.relativeTimeThreshold = ro, i.calendarFormat = Ri, i.prototype = dr, i.HTML5_FMT = {
          DATETIME_LOCAL: "YYYY-MM-DDTHH:mm",
          DATETIME_LOCAL_SECONDS: "YYYY-MM-DDTHH:mm:ss",
          DATETIME_LOCAL_MS: "YYYY-MM-DDTHH:mm:ss.SSS",
          DATE: "YYYY-MM-DD",
          TIME: "HH:mm",
          TIME_SECONDS: "HH:mm:ss",
          TIME_MS: "HH:mm:ss.SSS",
          WEEK: "GGGG-[W]WW",
          MONTH: "YYYY-MM"
        }, i;
      }();
    }(On)), On.exports),
    In = Nn(Ln);
  class Bn extends Se(de) {
    constructor() {
      super(...arguments), this.hideSettingsLinks = !1, this.actionsMode = "full", this.zones = [], this.isLoading = !0, this._initialLoadDone = !1, this.isSaving = !1, this._operationError = null, this._confirmIrrigate = null, this._skipDetailsOpen = !1, this._updateScheduled = !1;
    }
    _scheduleUpdate() {
      this._updateScheduled || (this._updateScheduled = !0, requestAnimationFrame(() => {
        this._updateScheduled = !1, this.requestUpdate();
      }));
    }
    firstUpdated() {
      _e().then(() => this._scheduleUpdate()).catch(e => {
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
        type: be + "_config_updated"
      })];
    }
    async _fetchData() {
      if (!this.hass) return;
      const e = !this._initialLoadDone;
      try {
        e && (this.isLoading = !0);
        const [a, i, n] = await Promise.all([(t = this.hass, t.callWS({
          type: be + "/config"
        })), ze(this.hass), we(this.hass).catch(e => {
          console.error("Failed to fetch irrigation outlook:", e);
        })]);
        this.config = a, this.zones = i, this._outlook = n, this._initialLoadDone = !0;
      } catch (e) {
        console.error("Error fetching data:", e), Dn(this, this.hass, "common.errors.load_failed", e);
      } finally {
        e && (this.isLoading = !1), this._scheduleUpdate();
      }
      var t;
    }
    handleCalculateAllZones() {
      var e;
      this.hass && (this.isSaving = !0, this._scheduleUpdate(), (e = this.hass, e.callApi("POST", be + "/zones", {
        calculate_all: !0
      })).catch(e => {
        console.error("Failed to calculate all zones:", e), Dn(this, this.hass, "common.errors.action_failed", e);
      }).finally(() => {
        this.isSaving = !1, this._fetchData().catch(e => console.error("fetchData after calc-all:", e));
      }));
    }
    handleUpdateAllZones() {
      var e;
      this.hass && (this.isSaving = !0, this._scheduleUpdate(), (e = this.hass, e.callApi("POST", be + "/zones", {
        update_all: !0
      })).catch(e => {
        console.error("Failed to update all zones:", e), Dn(this, this.hass, "common.errors.action_failed", e);
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
      const a = "all" === t,
        i = a ? void 0 : this.zones.find(e => {
          var a;
          return (null === (a = e.id) || void 0 === a ? void 0 : a.toString()) === t;
        }),
        n = a ? `(${this._linkedZoneCount})` : `: ${null !== (e = null == i ? void 0 : i.name) && void 0 !== e ? e : t}`;
      try {
        await (r = this.hass, o = a ? void 0 : t, r.callWS(Object.assign({
          type: be + "/irrigate_now"
        }, void 0 !== o ? {
          zone_id: o
        } : {}))), Tn(this, `${An("panels.zones.confirm_irrigate.toast_started", this.hass.language)} ${n}`);
      } catch (e) {
        const t = Mn(e);
        console.error("irrigate_now failed", e), Tn(this, `${An("panels.zones.confirm_irrigate.toast_failed", this.hass.language)}: ${t}`);
      }
      var r, o;
    }
    handleCalculateZone(e) {
      const t = this.zones[e];
      var a, i;
      t && null != t.id && this.hass && (this._operationError = null, this.isSaving = !0, this._scheduleUpdate(), (a = this.hass, i = t.id.toString(), a.callApi("POST", be + "/zones", {
        id: i,
        calculate: !0,
        override_cache: !0
      })).catch(e => {
        const t = Mn(e);
        console.error("calculateZone failed:", e), this._operationError = t;
      }).finally(() => {
        this.isSaving = !1, this._fetchData().catch(e => console.error("fetchData after calc:", e));
      }));
    }
    handleUpdateZone(e) {
      const t = this.zones[e];
      var a, i;
      t && null != t.id && this.hass && (this._operationError = null, this.isSaving = !0, this._scheduleUpdate(), (a = this.hass, i = t.id.toString(), a.callApi("POST", be + "/zones", {
        id: i,
        update: !0
      })).catch(e => {
        const t = Mn(e);
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
      En(0, t ? Pn("setup", "zones", t) : Pn("setup", "zones"));
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
      var t, a, i;
      const n = null !== (t = e.duration) && void 0 !== t ? t : 0,
        r = Number(null !== (a = e.bucket) && void 0 !== a ? a : 0),
        o = Number(null !== (i = e.bucket_threshold) && void 0 !== i ? i : 0);
      return n > 0 && r < o;
    }
    _formatRunTime(e) {
      if (!this.hass) return "";
      const t = this.hass.language,
        a = In(e),
        i = a.format("HH:mm"),
        n = In();
      return a.isSame(n, "day") ? `${An("panels.zones.outlook.today", t)} ${i}` : a.isSame(n.clone().add(1, "day"), "day") ? `${An("panels.zones.outlook.tomorrow", t)} ${i}` : a.format("ddd HH:mm");
    }
    _guardLabel(e) {
      return An(`panels.zones.outlook.checks.${e.id}`, this.hass.language);
    }
    _guardDetail(e) {
      var t;
      return e.available && null !== e.observed ? An(`panels.zones.outlook.check_detail.${e.id}`, this.hass.language, "{observed}", String(e.observed), "{threshold}", String(null !== (t = e.threshold) && void 0 !== t ? t : "")) : "";
    }
    _renderSkipReasons() {
      const e = this.hass.language;
      return V`
      <div class="outlook-line outlook-skip-reasons">
        <ul class="skip-reasons">
          ${this._triggeredGuards.map(e => {
        const t = this._guardDetail(e);
        return V`<li>
              ${this._guardLabel(e)}${t ? V` — ${t}` : ""}
            </li>`;
      })}
        </ul>
      </div>
      <div class="outlook-line outlook-dim skip-reasons-note">
        ${An("panels.zones.outlook.provisional", e)}
      </div>
    `;
    }
    _openSchedules() {
      En(0, Pn("setup", "schedules"));
    }
    _runActionLabel(e) {
      return An(`panels.zones.outlook.actions.${e.action}`, this.hass.language);
    }
    _runTargetsLabel(e) {
      const t = this.hass.language;
      if ("all" === e.zones) return An("panels.zones.outlook.targets_all", t);
      const a = Array.isArray(e.zones) ? e.zones.length : 0;
      return An("panels.zones.outlook.targets_zones", t, "{count}", String(a));
    }
    _renderOutlookBanner() {
      if (!this.hass || !this._outlook) return V``;
      const e = this.hass.language,
        t = this._nextIrrigateRun,
        a = this._triggeredGuards,
        i = this._outlook.last_skip_evaluation;
      return t && t.next_run_utc ? V`
      <ha-card class="outlook-card">
        <div class="outlook">
          <div class="outlook-line outlook-headline">
            <ha-icon icon="mdi:calendar-clock"></ha-icon>
            <span>
              <strong
                >${An("panels.zones.outlook.next_run", e)}:</strong
              >
              ${this._runActionLabel(t)}
              ${this._formatRunTime(t.next_run_utc)}
              <span class="outlook-dim"
                >· ${t.name} · ${this._runTargetsLabel(t)}</span
              >
            </span>
          </div>

          ${a.length > 0 ? V`
                <div class="outlook-line outlook-skip">
                  <ha-icon icon="mdi:alert"></ha-icon>
                  <span
                    >${An("panels.zones.outlook.will_skip", e)}</span
                  >
                  <button
                    class="outlook-info-btn"
                    aria-expanded="${this._skipDetailsOpen}"
                    title="${An("panels.zones.outlook.why_skipped", e)}"
                    @click="${() => {
        this._skipDetailsOpen = !this._skipDetailsOpen;
      }}"
                  >
                    <ha-icon
                      icon="${this._skipDetailsOpen ? "mdi:chevron-up" : "mdi:information-outline"}"
                    ></ha-icon>
                    <span class="outlook-info-label"
                      >${An("panels.zones.outlook.why_skipped", e)}</span
                    >
                  </button>
                </div>
                ${this._skipDetailsOpen ? this._renderSkipReasons() : ""}
              ` : V`
                <div class="outlook-line outlook-clear">
                  <ha-icon icon="mdi:check-circle-outline"></ha-icon>
                  <span
                    >${An("panels.zones.outlook.will_run", e)}</span
                  >
                </div>
              `}
          ${i ? this._renderLastRunLine(i) : ""}
        </div>
      </ha-card>
    ` : V`
        <ha-card class="outlook-card">
          <div class="outlook">
            <div class="outlook-line outlook-headline">
              <ha-icon icon="mdi:calendar-alert"></ha-icon>
              <span>${An("panels.zones.outlook.no_schedule", e)}</span>
              ${this.hideSettingsLinks ? "" : V`
                    <button
                      class="outlook-link"
                      @click="${this._openSchedules}"
                    >
                      ${An("panels.zones.outlook.setup_schedule", e)}
                    </button>
                  `}
            </div>
            ${i ? this._renderLastRunLine(i) : ""}
          </div>
        </ha-card>
      `;
    }
    _renderLastRunLine(e) {
      const t = this.hass.language,
        a = In(e.timestamp).fromNow(),
        i = e.checks.filter(e => e.enabled && e.would_skip).map(e => this._guardLabel(e).toLowerCase()).join(", "),
        n = e.would_skip ? `${An("panels.zones.outlook.last_run_skipped", t)}${i ? ` (${i})` : ""}` : An("panels.zones.outlook.last_run_ran", t);
      return V`
      <div class="outlook-line outlook-last">
        <span class="outlook-dim"
          >${An("panels.zones.outlook.last_run", t)}:</span
        >
        <span>${n} · ${a}</span>
      </div>
    `;
    }
    _renderZoneDecision(e) {
      var t;
      if (!this.hass) return V``;
      const a = this.hass.language,
        i = null !== (t = e.duration) && void 0 !== t ? t : 0;
      let n, r, o;
      if (e.state === xe.Disabled) n = An("panels.zones.status.decision_disabled", a), r = "neutral", o = "mdi:power-off";else if (e.last_calculated) {
        if (this._zoneHasDeficit(e)) {
          const t = function (e) {
              const t = Math.round(e);
              if (t < 60) return `${t} s`;
              const a = Math.floor(t / 60),
                i = t % 60;
              return i ? `${a} min ${i} s` : `${a} min`;
            }(i),
            s = this._triggeredGuards,
            l = this._nextIrrigateRunForZone(e);
          s.length > 0 ? (n = An("panels.zones.status.decision_water_skip", a, "{duration}", t, "{reason}", this._guardLabel(s[0]).toLowerCase()), r = "skip", o = "mdi:weather-rainy") : l && l.next_run_utc ? (n = An("panels.zones.status.decision_water_at", a, "{duration}", t, "{time}", this._formatRunTime(l.next_run_utc)), r = "water", o = "mdi:water") : (n = An("panels.zones.status.decision_water_no_schedule", a, "{duration}", t), r = "water", o = "mdi:water-alert");
        } else n = An("panels.zones.status.decision_no_water", a), r = "ok", o = "mdi:check-circle-outline";
      } else n = An("panels.zones.status.decision_unknown", a), r = "unknown", o = "mdi:help-circle-outline";
      return V`
      <div class="zone-decision ${r}">
        <ha-icon icon="${o}"></ha-icon>
        <span>${n}</span>
      </div>
    `;
    }
    _zoneEstimate(e) {
      var t, a;
      if (void 0 !== e.id) return null === (a = null === (t = this._outlook) || void 0 === t ? void 0 : t.zone_estimates) || void 0 === a ? void 0 : a[String(e.id)];
    }
    _renderZoneEstimate(e) {
      if (!this.hass) return V``;
      const t = this._zoneEstimate(e);
      if (!t || !t.available || null == t.live_deficit) return V``;
      const a = this.hass.language,
        i = xn(this.config, ye),
        n = t.live_deficit < 0 ? "var(--warning-color)" : "var(--success-color)",
        r = An(`panels.zones.status.estimate_method.${"proxy" === t.method ? "proxy" : "hourly"}`, a) + (t.as_of ? ` · ${In(t.as_of).format("HH:mm")}` : "");
      return V`
      <span class="status-sep">·</span>
      <span class="zone-estimate" title="${r}">
        ${An("panels.zones.status.estimate_now", a)}
        <strong style="color: ${n}"
          >≈ ${t.live_deficit.toFixed(2)} ${i}</strong
        >
        <span class="estimate-tag"
          >${An("panels.zones.status.estimate_tag", a)}</span
        >
      </span>
    `;
    }
    _renderZoneNextRun(e) {
      if (!this.hass) return V``;
      const t = this._nextIrrigateRunForZone(e);
      if (!t || !t.next_run_utc) return V``;
      return e.state !== xe.Disabled && e.last_calculated && this._zoneHasDeficit(e) && 0 === this._triggeredGuards.length ? V`` : V`
      <span class="status-sep">·</span>
      <span>
        ${An("panels.zones.outlook.next_run", this.hass.language)}:
        <strong>${this._formatRunTime(t.next_run_utc)}</strong>
      </span>
    `;
    }
    renderZone(e, t) {
      var a, i;
      if (!this.hass) return V``;
      const n = Number(null !== (a = e.bucket) && void 0 !== a ? a : 0),
        r = n < 0 ? "var(--warning-color)" : "var(--success-color)",
        o = e.state === xe.Automatic ? "state-automatic" : e.state === xe.Manual ? "state-manual" : "state-disabled",
        s = e.last_calculated ? In(e.last_calculated).format("YYYY-MM-DD HH:mm") : An("panels.zones.status.never", this.hass.language);
      return V`
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          <span class="zone-state-badge ${o}">
            ${An(`panels.zones.labels.states.${e.state}`, this.hass.language)}
          </span>
          ${this.hideSettingsLinks ? "" : V`
                <ha-icon-button
                  .path="${"M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"}"
                  title="${An("panels.zones.actions.open_settings", this.hass.language)}"
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
              title="${An("panels.zones.help.bucket", this.hass.language)}"
            >
              ${An("panels.zones.labels.bucket", this.hass.language)}:
              <strong style="color: ${r}"
                >${n.toFixed(2)}
                ${xn(this.config, ye)}</strong
              >
            </span>
            <span class="status-sep">·</span>
            <span>
              ${An("panels.zones.status.last_checked", this.hass.language)}:
              <strong>${s}</strong>
            </span>
            ${this._renderZoneEstimate(e)} ${this._renderZoneNextRun(e)}
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div class="card-content zone-action-bar">
          ${"full" === this.actionsMode && e.state === xe.Automatic ? V`
                <button
                  class="action-btn"
                  title="${An("panels.zones.help.update", this.hass.language)}"
                  @click="${() => this.handleUpdateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${An("panels.zones.actions.update", this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${An("panels.zones.help.calculate", this.hass.language)}"
                  @click="${() => this.handleCalculateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${An("panels.zones.actions.calculate", this.hass.language)}
                </button>
              ` : ""}
          ${"none" !== this.actionsMode && e.linked_entity && (null !== (i = e.duration) && void 0 !== i ? i : 0) > 0 ? V`
                <button
                  class="action-btn"
                  raised
                  @click="${() => {
        void 0 !== e.id && (this._confirmIrrigate = e.id.toString());
      }}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${An("panels.zones.labels.irrigate_now", this.hass.language)}
                </button>
              ` : e.linked_entity ? "" : V`
                  <button
                    class="action-btn"
                    disabled
                    title="${An("panels.zones.help.irrigate_link_entity", this.hass.language)}"
                  >
                    <ha-icon icon="mdi:water"></ha-icon>
                    ${An("panels.zones.labels.irrigate_now", this.hass.language)}
                  </button>
                  <span class="zones-top-note">
                    ${An("panels.zones.help.irrigate_link_entity", this.hass.language)}
                  </span>
                `}
        </div>
      </ha-card>
    `;
    }
    render() {
      var e, t;
      if (!this.hass) return V``;
      if (this.isLoading) return V`
        <ha-card header="${An("panels.zones.title", this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${An("common.loading-messages.general", this.hass.language)}
            </div>
          </div>
        </ha-card>
      `;
      const a = this.zones.some(e => {
          var t;
          return e.linked_entity && (null !== (t = e.duration) && void 0 !== t ? t : 0) > 0;
        }),
        i = 0 === this.zones.length;
      return V`
      ${i ? this.hideSettingsLinks ? V`
              <ha-card>
                <div class="card-content description-text">
                  ${An("panels.zones.no_items", this.hass.language)}
                </div>
              </ha-card>
            ` : V`
              <ha-card class="setup-banner-card">
                <div class="setup-banner">
                  <div class="setup-banner-icon">🌱</div>
                  <div class="setup-banner-content">
                    <div class="setup-banner-title">
                      ${An("wizard.title", this.hass.language)}
                    </div>
                    <div class="setup-banner-desc">
                      ${An("wizard.setup_complete_banner", this.hass.language)}
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
                    ${An("wizard.open_wizard", this.hass.language)}
                  </button>
                </div>
              </ha-card>
            ` : ""}
      ${i ? "" : this._renderOutlookBanner()}

      <!-- Zones header card: run-all operational actions -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${An("panels.zones.title", this.hass.language)}
          </div>
        </div>
        <div class="card-content zones-top-actions">
          ${"full" === this.actionsMode ? V`
                <button
                  class="action-btn"
                  title="${An("panels.zones.help.update_all", this.hass.language)}"
                  @click="${this.handleUpdateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${An("panels.zones.cards.zone-actions.actions.update-all", this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${An("panels.zones.help.calculate_all", this.hass.language)}"
                  @click="${this.handleCalculateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${An("panels.zones.cards.zone-actions.actions.calculate-all", this.hass.language)}
                </button>
              ` : ""}
          ${"none" !== this.actionsMode ? V`
                <button
                  class="action-btn"
                  raised
                  title="${An("panels.zones.help.irrigate_all", this.hass.language)}"
                  @click="${() => {
        this._confirmIrrigate = "all";
      }}"
                  ?disabled="${!a || this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${An("panels.zones.actions.irrigate_all", this.hass.language)}
                </button>
              ` : ""}
          ${a ? "" : V`<span class="zones-top-note"
                >${An("panels.info.cards.irrigate_now.no_linked_zones", this.hass.language)}</span
              >`}
        </div>
      </ha-card>

      <!-- Irrigate confirmation dialog -->
      ${null !== this._confirmIrrigate ? V`
            <ha-dialog
              open
              @closed="${() => {
        this._confirmIrrigate = null;
      }}"
              heading="${An("panels.zones.confirm_irrigate.title", this.hass.language)}"
            >
              <p>
                ${An("panels.zones.confirm_irrigate.body", this.hass.language)}
              </p>
              <p>
                <strong>
                  ${"all" === this._confirmIrrigate ? `${An("panels.zones.confirm_irrigate.all_linked_zones", this.hass.language)} (${this._linkedZoneCount})` : null !== (t = null === (e = this.zones.find(e => {
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
                  ${An("common.actions.cancel", this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._doIrrigate}"
                >
                  ${An("panels.zones.labels.irrigate_now", this.hass.language)}
                </button>
              </div>
            </ha-dialog>
          ` : ""}

      <!-- Operation error banner -->
      ${this._operationError ? V`
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
                  aria-label="${An("common.actions.cancel", this.hass.language)}"
                ></ha-icon-button>
              </div>
            </ha-card>
          ` : ""}

      <!-- Zone cards -->
      ${this.zones.map((e, t) => this.renderZone(e, t))}
    `;
    }
    static get styles() {
      return c`
      ${jn}

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

      /* Global outlook banner */
      .outlook-card {
        border-left: 4px solid var(--primary-color);
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
        font-size: 0.875rem;
        line-height: 1.35;
      }

      .outlook-line ha-icon {
        flex-shrink: 0;
        --mdc-icon-size: 20px;
      }

      .outlook-headline {
        font-size: 0.95rem;
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
  n([pe()], Bn.prototype, "config", void 0), n([pe({
    type: Boolean
  })], Bn.prototype, "hideSettingsLinks", void 0), n([pe({
    attribute: !1
  })], Bn.prototype, "actionsMode", void 0), n([pe({
    type: Array
  })], Bn.prototype, "zones", void 0), n([me()], Bn.prototype, "_outlook", void 0), n([pe({
    type: Boolean
  })], Bn.prototype, "isLoading", void 0), n([pe({
    type: Boolean
  })], Bn.prototype, "isSaving", void 0), n([me()], Bn.prototype, "_operationError", void 0), n([me()], Bn.prototype, "_confirmIrrigate", void 0), n([me()], Bn.prototype, "_skipDetailsOpen", void 0), customElements.get("smart-irrigation-view-zones") || customElements.define("smart-irrigation-view-zones", Bn);
  class Rn extends de {
    setConfig(e) {
      this._config = e;
    }
    getCardSize() {
      return 6;
    }
    static getStubConfig() {
      return {};
    }
    render() {
      var e;
      if (!this.hass || !this._config) return V``;
      const t = null !== (e = this._config.actions) && void 0 !== e ? e : "irrigate";
      return V`
      <smart-irrigation-view-zones
        .hass=${this.hass}
        .hideSettingsLinks=${!0}
        .actionsMode=${t}
      ></smart-irrigation-view-zones>
    `;
    }
  }
  n([pe({
    attribute: !1
  })], Rn.prototype, "hass", void 0), n([me()], Rn.prototype, "_config", void 0), customElements.get("smart-irrigation-zones-card") || customElements.define("smart-irrigation-zones-card", Rn);
  const Un = window;
  Un.customCards = Un.customCards || [], Un.customCards.some(e => "smart-irrigation-zones-card" === e.type) || (Un.customCards.push({
    type: "smart-irrigation-zones-card",
    name: "Smart Irrigation Zones",
    description: "Everyday zone status and manual irrigation, usable by non-admin users.",
    preview: !1
  }), console.info(`%c smart-irrigation-zones-card %c ${fe} `, "color: white; background: #3949ab; font-weight: 700;", "color: #3949ab; background: white; font-weight: 700;")), e.SmartIrrigationZonesCard = Rn, Object.defineProperty(e, "__esModule", {
    value: !0
  });
}({});
