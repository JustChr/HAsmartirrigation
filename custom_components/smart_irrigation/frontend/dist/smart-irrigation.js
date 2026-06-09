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
    function a() {
      this.constructor = e;
    }
    t(e, i), e.prototype = null === i ? Object.create(i) : (a.prototype = i.prototype, new a());
  }
  var a = function () {
    return a = Object.assign || function (e) {
      for (var t, i = 1, a = arguments.length; i < a; i++) for (var s in t = arguments[i]) Object.prototype.hasOwnProperty.call(t, s) && (e[s] = t[s]);
      return e;
    }, a.apply(this, arguments);
  };
  function s(e, t, i, a) {
    var s,
      n = arguments.length,
      r = n < 3 ? t : null === a ? a = Object.getOwnPropertyDescriptor(t, i) : a;
    if ("object" == typeof Reflect && "function" == typeof Reflect.decorate) r = Reflect.decorate(e, t, i, a);else for (var o = e.length - 1; o >= 0; o--) (s = e[o]) && (r = (n < 3 ? s(r) : n > 3 ? s(t, i, r) : s(t, i)) || r);
    return n > 3 && r && Object.defineProperty(t, i, r), r;
  }
  function n(e, t, i) {
    if (i || 2 === arguments.length) for (var a, s = 0, n = t.length; s < n; s++) !a && s in t || (a || (a = Array.prototype.slice.call(t, 0, s)), a[s] = t[s]);
    return e.concat(a || Array.prototype.slice.call(t));
  }
  "function" == typeof SuppressedError && SuppressedError;
  /**
       * @license
       * Copyright 2019 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  const r = window,
    o = r.ShadowRoot && (void 0 === r.ShadyCSS || r.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype,
    l = Symbol(),
    c = new WeakMap();
  class d {
    constructor(e, t, i) {
      if (this._$cssResult$ = !0, i !== l) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
      this.cssText = e, this.t = t;
    }
    get styleSheet() {
      let e = this.o;
      const t = this.t;
      if (o && void 0 === e) {
        const i = void 0 !== t && 1 === t.length;
        i && (e = c.get(t)), void 0 === e && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), i && c.set(t, e));
      }
      return e;
    }
    toString() {
      return this.cssText;
    }
  }
  const h = (e, ...t) => {
      const i = 1 === e.length ? e[0] : t.reduce((t, i, a) => t + (e => {
        if (!0 === e._$cssResult$) return e.cssText;
        if ("number" == typeof e) return e;
        throw Error("Value passed to 'css' function must be a 'css' function result: " + e + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
      })(i) + e[a + 1], e[0]);
      return new d(i, e, l);
    },
    u = o ? e => e : e => e instanceof CSSStyleSheet ? (e => {
      let t = "";
      for (const i of e.cssRules) t += i.cssText;
      return (e => new d("string" == typeof e ? e : e + "", void 0, l))(t);
    })(e) : e
    /**
         * @license
         * Copyright 2017 Google LLC
         * SPDX-License-Identifier: BSD-3-Clause
         */;
  var p;
  const g = window,
    m = g.trustedTypes,
    v = m ? m.emptyScript : "",
    f = g.reactiveElementPolyfillSupport,
    _ = {
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
    b = (e, t) => t !== e && (t == t || e == e),
    y = {
      attribute: !0,
      type: String,
      converter: _,
      reflect: !1,
      hasChanged: b
    },
    w = "finalized";
  class $ extends HTMLElement {
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
        const a = this._$Ep(i, t);
        void 0 !== a && (this._$Ev.set(a, i), e.push(a));
      }), e;
    }
    static createProperty(e, t = y) {
      if (t.state && (t.attribute = !1), this.finalize(), this.elementProperties.set(e, t), !t.noAccessor && !this.prototype.hasOwnProperty(e)) {
        const i = "symbol" == typeof e ? Symbol() : "__" + e,
          a = this.getPropertyDescriptor(e, i, t);
        void 0 !== a && Object.defineProperty(this.prototype, e, a);
      }
    }
    static getPropertyDescriptor(e, t, i) {
      return {
        get() {
          return this[t];
        },
        set(a) {
          const s = this[e];
          this[t] = a, this.requestUpdate(e, s, i);
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
        for (const e of i) t.unshift(u(e));
      } else void 0 !== e && t.push(u(e));
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
        o ? e.adoptedStyleSheets = t.map(e => e instanceof CSSStyleSheet ? e : e.styleSheet) : t.forEach(t => {
          const i = document.createElement("style"),
            a = r.litNonce;
          void 0 !== a && i.setAttribute("nonce", a), i.textContent = t.cssText, e.appendChild(i);
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
      var a;
      const s = this.constructor._$Ep(e, i);
      if (void 0 !== s && !0 === i.reflect) {
        const n = (void 0 !== (null === (a = i.converter) || void 0 === a ? void 0 : a.toAttribute) ? i.converter : _).toAttribute(t, i.type);
        this._$El = e, null == n ? this.removeAttribute(s) : this.setAttribute(s, n), this._$El = null;
      }
    }
    _$AK(e, t) {
      var i;
      const a = this.constructor,
        s = a._$Ev.get(e);
      if (void 0 !== s && this._$El !== s) {
        const e = a.getPropertyOptions(s),
          n = "function" == typeof e.converter ? {
            fromAttribute: e.converter
          } : void 0 !== (null === (i = e.converter) || void 0 === i ? void 0 : i.fromAttribute) ? e.converter : _;
        this._$El = s, this[s] = n.fromAttribute(t, e.type), this._$El = null;
      }
    }
    requestUpdate(e, t, i) {
      let a = !0;
      void 0 !== e && (((i = i || this.constructor.getPropertyOptions(e)).hasChanged || b)(this[e], t) ? (this._$AL.has(e) || this._$AL.set(e, t), !0 === i.reflect && this._$El !== e && (void 0 === this._$EC && (this._$EC = new Map()), this._$EC.set(e, i))) : a = !1), !this.isUpdatePending && a && (this._$E_ = this._$Ej());
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
  var x;
  $[w] = !0, $.elementProperties = new Map(), $.elementStyles = [], $.shadowRootOptions = {
    mode: "open"
  }, null == f || f({
    ReactiveElement: $
  }), (null !== (p = g.reactiveElementVersions) && void 0 !== p ? p : g.reactiveElementVersions = []).push("1.6.3");
  const k = window,
    S = k.trustedTypes,
    z = S ? S.createPolicy("lit-html", {
      createHTML: e => e
    }) : void 0,
    E = "$lit$",
    A = `lit$${(Math.random() + "").slice(9)}$`,
    T = "?" + A,
    C = `<${T}>`,
    O = document,
    H = () => O.createComment(""),
    L = e => null === e || "object" != typeof e && "function" != typeof e,
    M = Array.isArray,
    N = "[ \t\n\f\r]",
    I = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,
    P = /-->/g,
    D = />/g,
    B = RegExp(`>|${N}(?:([^\\s"'>=/]+)(${N}*=${N}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`, "g"),
    U = /'/g,
    R = /"/g,
    j = /^(?:script|style|textarea|title)$/i,
    F = (e => (t, ...i) => ({
      _$litType$: e,
      strings: t,
      values: i
    }))(1),
    W = Symbol.for("lit-noChange"),
    Z = Symbol.for("lit-nothing"),
    G = new WeakMap(),
    q = O.createTreeWalker(O, 129, null, !1);
  function V(e, t) {
    if (!Array.isArray(e) || !e.hasOwnProperty("raw")) throw Error("invalid template strings array");
    return void 0 !== z ? z.createHTML(t) : t;
  }
  const K = (e, t) => {
    const i = e.length - 1,
      a = [];
    let s,
      n = 2 === t ? "<svg>" : "",
      r = I;
    for (let t = 0; t < i; t++) {
      const i = e[t];
      let o,
        l,
        c = -1,
        d = 0;
      for (; d < i.length && (r.lastIndex = d, l = r.exec(i), null !== l);) d = r.lastIndex, r === I ? "!--" === l[1] ? r = P : void 0 !== l[1] ? r = D : void 0 !== l[2] ? (j.test(l[2]) && (s = RegExp("</" + l[2], "g")), r = B) : void 0 !== l[3] && (r = B) : r === B ? ">" === l[0] ? (r = null != s ? s : I, c = -1) : void 0 === l[1] ? c = -2 : (c = r.lastIndex - l[2].length, o = l[1], r = void 0 === l[3] ? B : '"' === l[3] ? R : U) : r === R || r === U ? r = B : r === P || r === D ? r = I : (r = B, s = void 0);
      const h = r === B && e[t + 1].startsWith("/>") ? " " : "";
      n += r === I ? i + C : c >= 0 ? (a.push(o), i.slice(0, c) + E + i.slice(c) + A + h) : i + A + (-2 === c ? (a.push(void 0), t) : h);
    }
    return [V(e, n + (e[i] || "<?>") + (2 === t ? "</svg>" : "")), a];
  };
  class X {
    constructor({
      strings: e,
      _$litType$: t
    }, i) {
      let a;
      this.parts = [];
      let s = 0,
        n = 0;
      const r = e.length - 1,
        o = this.parts,
        [l, c] = K(e, t);
      if (this.el = X.createElement(l, i), q.currentNode = this.el.content, 2 === t) {
        const e = this.el.content,
          t = e.firstChild;
        t.remove(), e.append(...t.childNodes);
      }
      for (; null !== (a = q.nextNode()) && o.length < r;) {
        if (1 === a.nodeType) {
          if (a.hasAttributes()) {
            const e = [];
            for (const t of a.getAttributeNames()) if (t.endsWith(E) || t.startsWith(A)) {
              const i = c[n++];
              if (e.push(t), void 0 !== i) {
                const e = a.getAttribute(i.toLowerCase() + E).split(A),
                  t = /([.?@])?(.*)/.exec(i);
                o.push({
                  type: 1,
                  index: s,
                  name: t[2],
                  strings: e,
                  ctor: "." === t[1] ? te : "?" === t[1] ? ae : "@" === t[1] ? se : ee
                });
              } else o.push({
                type: 6,
                index: s
              });
            }
            for (const t of e) a.removeAttribute(t);
          }
          if (j.test(a.tagName)) {
            const e = a.textContent.split(A),
              t = e.length - 1;
            if (t > 0) {
              a.textContent = S ? S.emptyScript : "";
              for (let i = 0; i < t; i++) a.append(e[i], H()), q.nextNode(), o.push({
                type: 2,
                index: ++s
              });
              a.append(e[t], H());
            }
          }
        } else if (8 === a.nodeType) if (a.data === T) o.push({
          type: 2,
          index: s
        });else {
          let e = -1;
          for (; -1 !== (e = a.data.indexOf(A, e + 1));) o.push({
            type: 7,
            index: s
          }), e += A.length - 1;
        }
        s++;
      }
    }
    static createElement(e, t) {
      const i = O.createElement("template");
      return i.innerHTML = e, i;
    }
  }
  function Y(e, t, i = e, a) {
    var s, n, r, o;
    if (t === W) return t;
    let l = void 0 !== a ? null === (s = i._$Co) || void 0 === s ? void 0 : s[a] : i._$Cl;
    const c = L(t) ? void 0 : t._$litDirective$;
    return (null == l ? void 0 : l.constructor) !== c && (null === (n = null == l ? void 0 : l._$AO) || void 0 === n || n.call(l, !1), void 0 === c ? l = void 0 : (l = new c(e), l._$AT(e, i, a)), void 0 !== a ? (null !== (r = (o = i)._$Co) && void 0 !== r ? r : o._$Co = [])[a] = l : i._$Cl = l), void 0 !== l && (t = Y(e, l._$AS(e, t.values), l, a)), t;
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
          parts: a
        } = this._$AD,
        s = (null !== (t = null == e ? void 0 : e.creationScope) && void 0 !== t ? t : O).importNode(i, !0);
      q.currentNode = s;
      let n = q.nextNode(),
        r = 0,
        o = 0,
        l = a[0];
      for (; void 0 !== l;) {
        if (r === l.index) {
          let t;
          2 === l.type ? t = new Q(n, n.nextSibling, this, e) : 1 === l.type ? t = new l.ctor(n, l.name, l.strings, this, e) : 6 === l.type && (t = new ne(n, this, e)), this._$AV.push(t), l = a[++o];
        }
        r !== (null == l ? void 0 : l.index) && (n = q.nextNode(), r++);
      }
      return q.currentNode = O, s;
    }
    v(e) {
      let t = 0;
      for (const i of this._$AV) void 0 !== i && (void 0 !== i.strings ? (i._$AI(e, i, t), t += i.strings.length - 2) : i._$AI(e[t])), t++;
    }
  }
  class Q {
    constructor(e, t, i, a) {
      var s;
      this.type = 2, this._$AH = Z, this._$AN = void 0, this._$AA = e, this._$AB = t, this._$AM = i, this.options = a, this._$Cp = null === (s = null == a ? void 0 : a.isConnected) || void 0 === s || s;
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
      e = Y(this, e, t), L(e) ? e === Z || null == e || "" === e ? (this._$AH !== Z && this._$AR(), this._$AH = Z) : e !== this._$AH && e !== W && this._(e) : void 0 !== e._$litType$ ? this.g(e) : void 0 !== e.nodeType ? this.$(e) : (e => M(e) || "function" == typeof (null == e ? void 0 : e[Symbol.iterator]))(e) ? this.T(e) : this._(e);
    }
    k(e) {
      return this._$AA.parentNode.insertBefore(e, this._$AB);
    }
    $(e) {
      this._$AH !== e && (this._$AR(), this._$AH = this.k(e));
    }
    _(e) {
      this._$AH !== Z && L(this._$AH) ? this._$AA.nextSibling.data = e : this.$(O.createTextNode(e)), this._$AH = e;
    }
    g(e) {
      var t;
      const {
          values: i,
          _$litType$: a
        } = e,
        s = "number" == typeof a ? this._$AC(e) : (void 0 === a.el && (a.el = X.createElement(V(a.h, a.h[0]), this.options)), a);
      if ((null === (t = this._$AH) || void 0 === t ? void 0 : t._$AD) === s) this._$AH.v(i);else {
        const e = new J(s, this),
          t = e.u(this.options);
        e.v(i), this.$(t), this._$AH = e;
      }
    }
    _$AC(e) {
      let t = G.get(e.strings);
      return void 0 === t && G.set(e.strings, t = new X(e)), t;
    }
    T(e) {
      M(this._$AH) || (this._$AH = [], this._$AR());
      const t = this._$AH;
      let i,
        a = 0;
      for (const s of e) a === t.length ? t.push(i = new Q(this.k(H()), this.k(H()), this, this.options)) : i = t[a], i._$AI(s), a++;
      a < t.length && (this._$AR(i && i._$AB.nextSibling, a), t.length = a);
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
    constructor(e, t, i, a, s) {
      this.type = 1, this._$AH = Z, this._$AN = void 0, this.element = e, this.name = t, this._$AM = a, this.options = s, i.length > 2 || "" !== i[0] || "" !== i[1] ? (this._$AH = Array(i.length - 1).fill(new String()), this.strings = i) : this._$AH = Z;
    }
    get tagName() {
      return this.element.tagName;
    }
    get _$AU() {
      return this._$AM._$AU;
    }
    _$AI(e, t = this, i, a) {
      const s = this.strings;
      let n = !1;
      if (void 0 === s) e = Y(this, e, t, 0), n = !L(e) || e !== this._$AH && e !== W, n && (this._$AH = e);else {
        const a = e;
        let r, o;
        for (e = s[0], r = 0; r < s.length - 1; r++) o = Y(this, a[i + r], t, r), o === W && (o = this._$AH[r]), n || (n = !L(o) || o !== this._$AH[r]), o === Z ? e = Z : e !== Z && (e += (null != o ? o : "") + s[r + 1]), this._$AH[r] = o;
      }
      n && !a && this.j(e);
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
  const ie = S ? S.emptyScript : "";
  class ae extends ee {
    constructor() {
      super(...arguments), this.type = 4;
    }
    j(e) {
      e && e !== Z ? this.element.setAttribute(this.name, ie) : this.element.removeAttribute(this.name);
    }
  }
  class se extends ee {
    constructor(e, t, i, a, s) {
      super(e, t, i, a, s), this.type = 5;
    }
    _$AI(e, t = this) {
      var i;
      if ((e = null !== (i = Y(this, e, t, 0)) && void 0 !== i ? i : Z) === W) return;
      const a = this._$AH,
        s = e === Z && a !== Z || e.capture !== a.capture || e.once !== a.once || e.passive !== a.passive,
        n = e !== Z && (a === Z || s);
      s && this.element.removeEventListener(this.name, this, a), n && this.element.addEventListener(this.name, this, e), this._$AH = e;
    }
    handleEvent(e) {
      var t, i;
      "function" == typeof this._$AH ? this._$AH.call(null !== (i = null === (t = this.options) || void 0 === t ? void 0 : t.host) && void 0 !== i ? i : this.element, e) : this._$AH.handleEvent(e);
    }
  }
  class ne {
    constructor(e, t, i) {
      this.element = e, this.type = 6, this._$AN = void 0, this._$AM = t, this.options = i;
    }
    get _$AU() {
      return this._$AM._$AU;
    }
    _$AI(e) {
      Y(this, e);
    }
  }
  const re = k.litHtmlPolyfillSupport;
  null == re || re(X, Q), (null !== (x = k.litHtmlVersions) && void 0 !== x ? x : k.litHtmlVersions = []).push("2.8.0");
  /**
       * @license
       * Copyright 2017 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  var oe, le;
  class ce extends $ {
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
        var a, s;
        const n = null !== (a = null == i ? void 0 : i.renderBefore) && void 0 !== a ? a : t;
        let r = n._$litPart$;
        if (void 0 === r) {
          const e = null !== (s = null == i ? void 0 : i.renderBefore) && void 0 !== s ? s : null;
          n._$litPart$ = r = new Q(t.insertBefore(H(), e), e, void 0, null != i ? i : {});
        }
        return r._$AI(e), r;
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
  ce.finalized = !0, ce._$litElement$ = !0, null === (oe = globalThis.litElementHydrateSupport) || void 0 === oe || oe.call(globalThis, {
    LitElement: ce
  });
  const de = globalThis.litElementPolyfillSupport;
  null == de || de({
    LitElement: ce
  }), (null !== (le = globalThis.litElementVersions) && void 0 !== le ? le : globalThis.litElementVersions = []).push("3.3.3");
  /**
       * @license
       * Copyright 2017 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  const he = e => t => "function" == typeof t ? ((e, t) => (customElements.define(e, t), t))(e, t) : ((e, t) => {
      const {
        kind: i,
        elements: a
      } = t;
      return {
        kind: i,
        elements: a,
        finisher(t) {
          customElements.define(e, t);
        }
      };
    })(e, t)
    /**
         * @license
         * Copyright 2017 Google LLC
         * SPDX-License-Identifier: BSD-3-Clause
         */,
    ue = (e, t) => "method" === t.kind && t.descriptor && !("value" in t.descriptor) ? {
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
  function pe(e) {
    return (t, i) => void 0 !== i ? ((e, t, i) => {
      t.constructor.createProperty(i, e);
    })(e, t, i) : ue(e, t);
    /**
         * @license
         * Copyright 2017 Google LLC
         * SPDX-License-Identifier: BSD-3-Clause
         */
  }
  function ge(e) {
    return pe({
      ...e,
      state: !0
    });
  }
  /**
       * @license
       * Copyright 2017 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  /**
       * @license
       * Copyright 2017 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  function me(e, t) {
    return (({
      finisher: e,
      descriptor: t
    }) => (i, a) => {
      var s;
      if (void 0 === a) {
        const a = null !== (s = i.originalKey) && void 0 !== s ? s : i.key,
          n = null != t ? {
            kind: "method",
            placement: "prototype",
            key: a,
            descriptor: t(i.key)
          } : {
            ...i,
            key: a
          };
        return null != e && (n.finisher = function (t) {
          e(t, a);
        }), n;
      }
      {
        const s = i.constructor;
        void 0 !== t && Object.defineProperty(i, a, t(a)), null == e || e(s, a);
      }
    })({
      descriptor: i => {
        const a = {
          get() {
            var t, i;
            return null !== (i = null === (t = this.renderRoot) || void 0 === t ? void 0 : t.querySelector(e)) && void 0 !== i ? i : null;
          },
          enumerable: !0,
          configurable: !0
        };
        if (t) {
          const t = "symbol" == typeof i ? Symbol() : "__" + i;
          a.get = function () {
            var i, a;
            return void 0 === this[t] && (this[t] = null !== (a = null === (i = this.renderRoot) || void 0 === i ? void 0 : i.querySelector(e)) && void 0 !== a ? a : null), this[t];
          };
        }
        return a;
      }
    });
  }
  /**
       * @license
       * Copyright 2021 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */
  var ve;
  null === (ve = window.HTMLSlotElement) || void 0 === ve || ve.prototype.assignedElements;
  let fe = !1,
    _e = null;
  const be = async () => {
    if (fe && _e) return _e;
    if (customElements.get("ha-checkbox") && customElements.get("ha-slider") && customElements.get("ha-panel-config") && customElements.get("ha-entity-picker")) return Promise.resolve();
    fe = !0, _e = async function () {
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
      await _e;
    } finally {
      fe = !1, _e = null;
    }
  };
  const ye = `v${"2026.06.18"}`,
    we = "smart_irrigation",
    $e = ["de", "en", "es", "fr", "it", "nl", "no", "sk"],
    xe = "precipitation_threshold_mm",
    ke = "Open Weather Map",
    Se = "Pirate Weather",
    ze = "Open-Meteo",
    Ee = "minutes",
    Ae = "hours",
    Te = "days",
    Ce = "imperial",
    Oe = "metric",
    He = "Dewpoint",
    Le = "Evapotranspiration",
    Me = "Humidity",
    Ne = "Precipitation",
    Ie = "Current Precipitation",
    Pe = "Pressure",
    De = "Solar Radiation",
    Be = "Temperature",
    Ue = "Windspeed",
    Re = "weather_service",
    je = "sensor",
    Fe = "static",
    We = "pressure_type",
    Ze = "absolute",
    Ge = "relative",
    qe = "none",
    Ve = "source",
    Ke = "sensorentity",
    Xe = "static_value",
    Ye = "unit",
    Je = "aggregate",
    Qe = ["average", "first", "last", "maximum", "median", "minimum", "riemannsum", "sum", "delta"],
    et = "sq ft",
    tt = "l/minute",
    it = "gal/minute",
    at = "mm",
    st = "in",
    nt = "inch Hg",
    rt = "mile/h",
    ot = "meter/s",
    lt = "mm/h",
    ct = "in/h",
    dt = "name",
    ht = "size",
    ut = "throughput",
    pt = "state",
    gt = "duration",
    mt = "module",
    vt = "bucket",
    ft = "multiplier",
    _t = "mapping",
    bt = "lead_time",
    yt = "maximum_duration",
    wt = "maximum_bucket",
    $t = "drainage_rate",
    xt = "linked_entity",
    kt = "bucket_threshold",
    St = "flow_sensor",
    zt = "zone_sequencing",
    Et = "sequential",
    At = "parallel",
    Tt = "rotating",
    Ct = "zone_sequencing_max_consecutive_duration",
    Ot = "zone_sequencing_min_absorption_time",
    Ht = 1,
    Lt = 2,
    Mt = 3,
    Nt = 4,
    It = e => (...t) => ({
      _$litDirective$: e,
      values: t
    });
  class Pt {
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
  class Dt extends Pt {
    constructor(e) {
      if (super(e), this.et = Z, e.type !== Lt) throw Error(this.constructor.directiveName + "() can only be used in child bindings");
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
  Dt.directiveName = "unsafeHTML", Dt.resultType = 1;
  const Bt = It(Dt);
  var Ut = {
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
    Rt = {
      "default-zone": "Default zone",
      "default-mapping": "Default sensor group"
    },
    jt = {
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
    Ft = {
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
    Wt = {
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
        description: "Create recurring schedules to automatically irrigate your zones at specific times. No automations needed.",
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
        title: "Setup",
        tabs: {
          weather_location: "Weather & Location",
          my_zones: "My Zones",
          when_to_water: "When to Water",
          advanced: "Advanced"
        },
        weather_data: {
          forecast_title: "Forecast",
          forecast_none: "Forecast is available when a weather service is enabled."
        }
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
    Zt = "Smart Irrigation",
    Gt = {
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
    qt = {
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
    Vt = {
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
    Kt = {
      title: "Location Coordinates",
      description: "Configure location coordinates for weather data retrieval. You can use manual coordinates different from your Home Assistant location if needed.",
      manual_enabled: "Use manual coordinates",
      use_ha_location: "Use Home Assistant location",
      latitude: "Latitude (decimal degrees)",
      longitude: "Longitude (decimal degrees)",
      elevation: "Elevation (meters above sea level)",
      current_ha_coords: "Current Home Assistant coordinates"
    },
    Xt = {
      title: "Days Between Irrigation",
      description: "Configure the minimum number of days that must pass between irrigation events. This helps control watering frequency for water conservation and plant health management.\n\nTypical real-world use cases:\n• Lawn care: 1-2 day intervals prevent overwatering\n• Drought restrictions: 6+ day intervals for weekly watering\n• Deep-rooted plants: 3-7 day intervals for less frequent watering\n• Water conservation: Customizable based on climate and soil conditions",
      label: "Minimum days between irrigation",
      help_text: "Set to 0 to disable this feature. Values from 1-365 days are supported. This setting works alongside existing precipitation forecasting logic."
    },
    Yt = {
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
    Jt = {
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
    Qt = {
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
    ei = {
      common: Ut,
      defaults: Rt,
      module: jt,
      calcmodules: Ft,
      panels: Wt,
      title: Zt,
      weather_service_config: Gt,
      irrigation_start_triggers: qt,
      weather_skip: Vt,
      coordinate_config: Kt,
      days_between_irrigation: Xt,
      zone_sequencing: Yt,
      field_help: Jt,
      wizard: Qt
    },
    ti = Object.freeze({
      __proto__: null,
      common: Ut,
      defaults: Rt,
      module: jt,
      calcmodules: Ft,
      panels: Wt,
      title: Zt,
      weather_service_config: Gt,
      irrigation_start_triggers: qt,
      weather_skip: Vt,
      coordinate_config: Kt,
      days_between_irrigation: Xt,
      zone_sequencing: Yt,
      field_help: Jt,
      wizard: Qt,
      default: ei
    });
  function ii(e, t) {
    var i = t && t.cache ? t.cache : ui,
      a = t && t.serializer ? t.serializer : oi;
    return (t && t.strategy ? t.strategy : ri)(e, {
      cache: i,
      serializer: a
    });
  }
  function ai(e, t, i, a) {
    var s,
      n = null == (s = a) || "number" == typeof s || "boolean" == typeof s ? a : i(a),
      r = t.get(n);
    return void 0 === r && (r = e.call(this, a), t.set(n, r)), r;
  }
  function si(e, t, i) {
    var a = Array.prototype.slice.call(arguments, 3),
      s = i(a),
      n = t.get(s);
    return void 0 === n && (n = e.apply(this, a), t.set(s, n)), n;
  }
  function ni(e, t, i, a, s) {
    return i.bind(t, e, a, s);
  }
  function ri(e, t) {
    return ni(e, this, 1 === e.length ? ai : si, t.cache.create(), t.serializer);
  }
  var oi = function () {
    return JSON.stringify(arguments);
  };
  function li() {
    this.cache = Object.create(null);
  }
  li.prototype.get = function (e) {
    return this.cache[e];
  }, li.prototype.set = function (e, t) {
    this.cache[e] = t;
  };
  var ci,
    di,
    hi,
    ui = {
      create: function () {
        return new li();
      }
    },
    pi = {
      variadic: function (e, t) {
        return ni(e, this, si, t.cache.create(), t.serializer);
      },
      monadic: function (e, t) {
        return ni(e, this, ai, t.cache.create(), t.serializer);
      }
    };
  function gi(e) {
    return e.type === di.literal;
  }
  function mi(e) {
    return e.type === di.argument;
  }
  function vi(e) {
    return e.type === di.number;
  }
  function fi(e) {
    return e.type === di.date;
  }
  function _i(e) {
    return e.type === di.time;
  }
  function bi(e) {
    return e.type === di.select;
  }
  function yi(e) {
    return e.type === di.plural;
  }
  function wi(e) {
    return e.type === di.pound;
  }
  function $i(e) {
    return e.type === di.tag;
  }
  function xi(e) {
    return !(!e || "object" != typeof e || e.type !== hi.number);
  }
  function ki(e) {
    return !(!e || "object" != typeof e || e.type !== hi.dateTime);
  }
  !function (e) {
    e[e.EXPECT_ARGUMENT_CLOSING_BRACE = 1] = "EXPECT_ARGUMENT_CLOSING_BRACE", e[e.EMPTY_ARGUMENT = 2] = "EMPTY_ARGUMENT", e[e.MALFORMED_ARGUMENT = 3] = "MALFORMED_ARGUMENT", e[e.EXPECT_ARGUMENT_TYPE = 4] = "EXPECT_ARGUMENT_TYPE", e[e.INVALID_ARGUMENT_TYPE = 5] = "INVALID_ARGUMENT_TYPE", e[e.EXPECT_ARGUMENT_STYLE = 6] = "EXPECT_ARGUMENT_STYLE", e[e.INVALID_NUMBER_SKELETON = 7] = "INVALID_NUMBER_SKELETON", e[e.INVALID_DATE_TIME_SKELETON = 8] = "INVALID_DATE_TIME_SKELETON", e[e.EXPECT_NUMBER_SKELETON = 9] = "EXPECT_NUMBER_SKELETON", e[e.EXPECT_DATE_TIME_SKELETON = 10] = "EXPECT_DATE_TIME_SKELETON", e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE = 11] = "UNCLOSED_QUOTE_IN_ARGUMENT_STYLE", e[e.EXPECT_SELECT_ARGUMENT_OPTIONS = 12] = "EXPECT_SELECT_ARGUMENT_OPTIONS", e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE = 13] = "EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE", e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE = 14] = "INVALID_PLURAL_ARGUMENT_OFFSET_VALUE", e[e.EXPECT_SELECT_ARGUMENT_SELECTOR = 15] = "EXPECT_SELECT_ARGUMENT_SELECTOR", e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR = 16] = "EXPECT_PLURAL_ARGUMENT_SELECTOR", e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT = 17] = "EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT", e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT = 18] = "EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT", e[e.INVALID_PLURAL_ARGUMENT_SELECTOR = 19] = "INVALID_PLURAL_ARGUMENT_SELECTOR", e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR = 20] = "DUPLICATE_PLURAL_ARGUMENT_SELECTOR", e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR = 21] = "DUPLICATE_SELECT_ARGUMENT_SELECTOR", e[e.MISSING_OTHER_CLAUSE = 22] = "MISSING_OTHER_CLAUSE", e[e.INVALID_TAG = 23] = "INVALID_TAG", e[e.INVALID_TAG_NAME = 25] = "INVALID_TAG_NAME", e[e.UNMATCHED_CLOSING_TAG = 26] = "UNMATCHED_CLOSING_TAG", e[e.UNCLOSED_TAG = 27] = "UNCLOSED_TAG";
  }(ci || (ci = {})), function (e) {
    e[e.literal = 0] = "literal", e[e.argument = 1] = "argument", e[e.number = 2] = "number", e[e.date = 3] = "date", e[e.time = 4] = "time", e[e.select = 5] = "select", e[e.plural = 6] = "plural", e[e.pound = 7] = "pound", e[e.tag = 8] = "tag";
  }(di || (di = {})), function (e) {
    e[e.number = 0] = "number", e[e.dateTime = 1] = "dateTime";
  }(hi || (hi = {}));
  var Si = /[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/,
    zi = /(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;
  function Ei(e) {
    var t = {};
    return e.replace(zi, function (e) {
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
  var Ai = /[\t-\r \x85\u200E\u200F\u2028\u2029]/i;
  var Ti = /^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g,
    Ci = /^(@+)?(\+|#+)?[rs]?$/g,
    Oi = /(\*)(0+)|(#+)(0+)|(0+)/g,
    Hi = /^(0+)$/;
  function Li(e) {
    var t = {};
    return "r" === e[e.length - 1] ? t.roundingPriority = "morePrecision" : "s" === e[e.length - 1] && (t.roundingPriority = "lessPrecision"), e.replace(Ci, function (e, i, a) {
      return "string" != typeof a ? (t.minimumSignificantDigits = i.length, t.maximumSignificantDigits = i.length) : "+" === a ? t.minimumSignificantDigits = i.length : "#" === i[0] ? t.maximumSignificantDigits = i.length : (t.minimumSignificantDigits = i.length, t.maximumSignificantDigits = i.length + ("string" == typeof a ? a.length : 0)), "";
    }), t;
  }
  function Mi(e) {
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
  function Ni(e) {
    var t;
    if ("E" === e[0] && "E" === e[1] ? (t = {
      notation: "engineering"
    }, e = e.slice(2)) : "E" === e[0] && (t = {
      notation: "scientific"
    }, e = e.slice(1)), t) {
      var i = e.slice(0, 2);
      if ("+!" === i ? (t.signDisplay = "always", e = e.slice(2)) : "+?" === i && (t.signDisplay = "exceptZero", e = e.slice(2)), !Hi.test(e)) throw new Error("Malformed concise eng/scientific notation");
      t.minimumIntegerDigits = e.length;
    }
    return t;
  }
  function Ii(e) {
    var t = Mi(e);
    return t || {};
  }
  function Pi(e) {
    for (var t = {}, i = 0, s = e; i < s.length; i++) {
      var n = s[i];
      switch (n.stem) {
        case "percent":
        case "%":
          t.style = "percent";
          continue;
        case "%x100":
          t.style = "percent", t.scale = 100;
          continue;
        case "currency":
          t.style = "currency", t.currency = n.options[0];
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
          t.style = "unit", t.unit = n.options[0].replace(/^(.*?)-/, "");
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
          t = a(a(a({}, t), {
            notation: "scientific"
          }), n.options.reduce(function (e, t) {
            return a(a({}, e), Ii(t));
          }, {}));
          continue;
        case "engineering":
          t = a(a(a({}, t), {
            notation: "engineering"
          }), n.options.reduce(function (e, t) {
            return a(a({}, e), Ii(t));
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
          t.scale = parseFloat(n.options[0]);
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
          if (n.options.length > 1) throw new RangeError("integer-width stems only accept a single optional option");
          n.options[0].replace(Oi, function (e, i, a, s, n, r) {
            if (i) t.minimumIntegerDigits = a.length;else {
              if (s && n) throw new Error("We currently do not support maximum integer digits");
              if (r) throw new Error("We currently do not support exact integer digits");
            }
            return "";
          });
          continue;
      }
      if (Hi.test(n.stem)) t.minimumIntegerDigits = n.stem.length;else if (Ti.test(n.stem)) {
        if (n.options.length > 1) throw new RangeError("Fraction-precision stems only accept a single optional option");
        n.stem.replace(Ti, function (e, i, a, s, n, r) {
          return "*" === a ? t.minimumFractionDigits = i.length : s && "#" === s[0] ? t.maximumFractionDigits = s.length : n && r ? (t.minimumFractionDigits = n.length, t.maximumFractionDigits = n.length + r.length) : (t.minimumFractionDigits = i.length, t.maximumFractionDigits = i.length), "";
        });
        var r = n.options[0];
        "w" === r ? t = a(a({}, t), {
          trailingZeroDisplay: "stripIfInteger"
        }) : r && (t = a(a({}, t), Li(r)));
      } else if (Ci.test(n.stem)) t = a(a({}, t), Li(n.stem));else {
        var o = Mi(n.stem);
        o && (t = a(a({}, t), o));
        var l = Ni(n.stem);
        l && (t = a(a({}, t), l));
      }
    }
    return t;
  }
  var Di,
    Bi = {
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
  function Ui(e) {
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
      a = e.language;
    return "root" !== a && (i = e.maximize().region), (Bi[i || ""] || Bi[a || ""] || Bi["".concat(a, "-001")] || Bi["001"])[0];
  }
  var Ri = new RegExp("^".concat(Si.source, "*")),
    ji = new RegExp("".concat(Si.source, "*$"));
  function Fi(e, t) {
    return {
      start: e,
      end: t
    };
  }
  var Wi = !!String.prototype.startsWith && "_a".startsWith("a", 1),
    Zi = !!String.fromCodePoint,
    Gi = !!Object.fromEntries,
    qi = !!String.prototype.codePointAt,
    Vi = !!String.prototype.trimStart,
    Ki = !!String.prototype.trimEnd,
    Xi = !!Number.isSafeInteger ? Number.isSafeInteger : function (e) {
      return "number" == typeof e && isFinite(e) && Math.floor(e) === e && Math.abs(e) <= 9007199254740991;
    },
    Yi = !0;
  try {
    Yi = "a" === (null === (Di = na("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu").exec("a")) || void 0 === Di ? void 0 : Di[0]);
  } catch (P) {
    Yi = !1;
  }
  var Ji,
    Qi = Wi ? function (e, t, i) {
      return e.startsWith(t, i);
    } : function (e, t, i) {
      return e.slice(i, i + t.length) === t;
    },
    ea = Zi ? String.fromCodePoint : function () {
      for (var e = [], t = 0; t < arguments.length; t++) e[t] = arguments[t];
      for (var i, a = "", s = e.length, n = 0; s > n;) {
        if ((i = e[n++]) > 1114111) throw RangeError(i + " is not a valid code point");
        a += i < 65536 ? String.fromCharCode(i) : String.fromCharCode(55296 + ((i -= 65536) >> 10), i % 1024 + 56320);
      }
      return a;
    },
    ta = Gi ? Object.fromEntries : function (e) {
      for (var t = {}, i = 0, a = e; i < a.length; i++) {
        var s = a[i],
          n = s[0],
          r = s[1];
        t[n] = r;
      }
      return t;
    },
    ia = qi ? function (e, t) {
      return e.codePointAt(t);
    } : function (e, t) {
      var i = e.length;
      if (!(t < 0 || t >= i)) {
        var a,
          s = e.charCodeAt(t);
        return s < 55296 || s > 56319 || t + 1 === i || (a = e.charCodeAt(t + 1)) < 56320 || a > 57343 ? s : a - 56320 + (s - 55296 << 10) + 65536;
      }
    },
    aa = Vi ? function (e) {
      return e.trimStart();
    } : function (e) {
      return e.replace(Ri, "");
    },
    sa = Ki ? function (e) {
      return e.trimEnd();
    } : function (e) {
      return e.replace(ji, "");
    };
  function na(e, t) {
    return new RegExp(e, t);
  }
  if (Yi) {
    var ra = na("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu");
    Ji = function (e, t) {
      var i;
      return ra.lastIndex = t, null !== (i = ra.exec(e)[1]) && void 0 !== i ? i : "";
    };
  } else Ji = function (e, t) {
    for (var i = [];;) {
      var a = ia(e, t);
      if (void 0 === a || ha(a) || ua(a)) break;
      i.push(a), t += a >= 65536 ? 2 : 1;
    }
    return ea.apply(void 0, i);
  };
  var oa,
    la = function () {
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
        for (var a = []; !this.isEOF();) {
          var s = this.char();
          if (123 === s) {
            if ((n = this.parseArgument(e, i)).err) return n;
            a.push(n.val);
          } else {
            if (125 === s && e > 0) break;
            if (35 !== s || "plural" !== t && "selectordinal" !== t) {
              if (60 === s && !this.ignoreTag && 47 === this.peek()) {
                if (i) break;
                return this.error(ci.UNMATCHED_CLOSING_TAG, Fi(this.clonePosition(), this.clonePosition()));
              }
              if (60 === s && !this.ignoreTag && ca(this.peek() || 0)) {
                if ((n = this.parseTag(e, t)).err) return n;
                a.push(n.val);
              } else {
                var n;
                if ((n = this.parseLiteral(e, t)).err) return n;
                a.push(n.val);
              }
            } else {
              var r = this.clonePosition();
              this.bump(), a.push({
                type: di.pound,
                location: Fi(r, this.clonePosition())
              });
            }
          }
        }
        return {
          val: a,
          err: null
        };
      }, e.prototype.parseTag = function (e, t) {
        var i = this.clonePosition();
        this.bump();
        var a = this.parseTagName();
        if (this.bumpSpace(), this.bumpIf("/>")) return {
          val: {
            type: di.literal,
            value: "<".concat(a, "/>"),
            location: Fi(i, this.clonePosition())
          },
          err: null
        };
        if (this.bumpIf(">")) {
          var s = this.parseMessage(e + 1, t, !0);
          if (s.err) return s;
          var n = s.val,
            r = this.clonePosition();
          if (this.bumpIf("</")) {
            if (this.isEOF() || !ca(this.char())) return this.error(ci.INVALID_TAG, Fi(r, this.clonePosition()));
            var o = this.clonePosition();
            return a !== this.parseTagName() ? this.error(ci.UNMATCHED_CLOSING_TAG, Fi(o, this.clonePosition())) : (this.bumpSpace(), this.bumpIf(">") ? {
              val: {
                type: di.tag,
                value: a,
                children: n,
                location: Fi(i, this.clonePosition())
              },
              err: null
            } : this.error(ci.INVALID_TAG, Fi(r, this.clonePosition())));
          }
          return this.error(ci.UNCLOSED_TAG, Fi(i, this.clonePosition()));
        }
        return this.error(ci.INVALID_TAG, Fi(i, this.clonePosition()));
      }, e.prototype.parseTagName = function () {
        var e = this.offset();
        for (this.bump(); !this.isEOF() && da(this.char());) this.bump();
        return this.message.slice(e, this.offset());
      }, e.prototype.parseLiteral = function (e, t) {
        for (var i = this.clonePosition(), a = "";;) {
          var s = this.tryParseQuote(t);
          if (s) a += s;else {
            var n = this.tryParseUnquoted(e, t);
            if (n) a += n;else {
              var r = this.tryParseLeftAngleBracket();
              if (!r) break;
              a += r;
            }
          }
        }
        var o = Fi(i, this.clonePosition());
        return {
          val: {
            type: di.literal,
            value: a,
            location: o
          },
          err: null
        };
      }, e.prototype.tryParseLeftAngleBracket = function () {
        return this.isEOF() || 60 !== this.char() || !this.ignoreTag && (ca(e = this.peek() || 0) || 47 === e) ? null : (this.bump(), "<");
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
        return ea.apply(void 0, t);
      }, e.prototype.tryParseUnquoted = function (e, t) {
        if (this.isEOF()) return null;
        var i = this.char();
        return 60 === i || 123 === i || 35 === i && ("plural" === t || "selectordinal" === t) || 125 === i && e > 0 ? null : (this.bump(), ea(i));
      }, e.prototype.parseArgument = function (e, t) {
        var i = this.clonePosition();
        if (this.bump(), this.bumpSpace(), this.isEOF()) return this.error(ci.EXPECT_ARGUMENT_CLOSING_BRACE, Fi(i, this.clonePosition()));
        if (125 === this.char()) return this.bump(), this.error(ci.EMPTY_ARGUMENT, Fi(i, this.clonePosition()));
        var a = this.parseIdentifierIfPossible().value;
        if (!a) return this.error(ci.MALFORMED_ARGUMENT, Fi(i, this.clonePosition()));
        if (this.bumpSpace(), this.isEOF()) return this.error(ci.EXPECT_ARGUMENT_CLOSING_BRACE, Fi(i, this.clonePosition()));
        switch (this.char()) {
          case 125:
            return this.bump(), {
              val: {
                type: di.argument,
                value: a,
                location: Fi(i, this.clonePosition())
              },
              err: null
            };
          case 44:
            return this.bump(), this.bumpSpace(), this.isEOF() ? this.error(ci.EXPECT_ARGUMENT_CLOSING_BRACE, Fi(i, this.clonePosition())) : this.parseArgumentOptions(e, t, a, i);
          default:
            return this.error(ci.MALFORMED_ARGUMENT, Fi(i, this.clonePosition()));
        }
      }, e.prototype.parseIdentifierIfPossible = function () {
        var e = this.clonePosition(),
          t = this.offset(),
          i = Ji(this.message, t),
          a = t + i.length;
        return this.bumpTo(a), {
          value: i,
          location: Fi(e, this.clonePosition())
        };
      }, e.prototype.parseArgumentOptions = function (e, t, i, s) {
        var n,
          r = this.clonePosition(),
          o = this.parseIdentifierIfPossible().value,
          l = this.clonePosition();
        switch (o) {
          case "":
            return this.error(ci.EXPECT_ARGUMENT_TYPE, Fi(r, l));
          case "number":
          case "date":
          case "time":
            this.bumpSpace();
            var c = null;
            if (this.bumpIf(",")) {
              this.bumpSpace();
              var d = this.clonePosition();
              if ((_ = this.parseSimpleArgStyleIfPossible()).err) return _;
              if (0 === (g = sa(_.val)).length) return this.error(ci.EXPECT_ARGUMENT_STYLE, Fi(this.clonePosition(), this.clonePosition()));
              c = {
                style: g,
                styleLocation: Fi(d, this.clonePosition())
              };
            }
            if ((b = this.tryParseArgumentClose(s)).err) return b;
            var h = Fi(s, this.clonePosition());
            if (c && Qi(null == c ? void 0 : c.style, "::", 0)) {
              var u = aa(c.style.slice(2));
              if ("number" === o) return (_ = this.parseNumberSkeletonFromString(u, c.styleLocation)).err ? _ : {
                val: {
                  type: di.number,
                  value: i,
                  location: h,
                  style: _.val
                },
                err: null
              };
              if (0 === u.length) return this.error(ci.EXPECT_DATE_TIME_SKELETON, h);
              var p = u;
              this.locale && (p = function (e, t) {
                for (var i = "", a = 0; a < e.length; a++) {
                  var s = e.charAt(a);
                  if ("j" === s) {
                    for (var n = 0; a + 1 < e.length && e.charAt(a + 1) === s;) n++, a++;
                    var r = 1 + (1 & n),
                      o = n < 2 ? 1 : 3 + (n >> 1),
                      l = Ui(t);
                    for ("H" != l && "k" != l || (o = 0); o-- > 0;) i += "a";
                    for (; r-- > 0;) i = l + i;
                  } else i += "J" === s ? "H" : s;
                }
                return i;
              }(u, this.locale));
              var g = {
                type: hi.dateTime,
                pattern: p,
                location: c.styleLocation,
                parsedOptions: this.shouldParseSkeletons ? Ei(p) : {}
              };
              return {
                val: {
                  type: "date" === o ? di.date : di.time,
                  value: i,
                  location: h,
                  style: g
                },
                err: null
              };
            }
            return {
              val: {
                type: "number" === o ? di.number : "date" === o ? di.date : di.time,
                value: i,
                location: h,
                style: null !== (n = null == c ? void 0 : c.style) && void 0 !== n ? n : null
              },
              err: null
            };
          case "plural":
          case "selectordinal":
          case "select":
            var m = this.clonePosition();
            if (this.bumpSpace(), !this.bumpIf(",")) return this.error(ci.EXPECT_SELECT_ARGUMENT_OPTIONS, Fi(m, a({}, m)));
            this.bumpSpace();
            var v = this.parseIdentifierIfPossible(),
              f = 0;
            if ("select" !== o && "offset" === v.value) {
              if (!this.bumpIf(":")) return this.error(ci.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE, Fi(this.clonePosition(), this.clonePosition()));
              var _;
              if (this.bumpSpace(), (_ = this.tryParseDecimalInteger(ci.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE, ci.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE)).err) return _;
              this.bumpSpace(), v = this.parseIdentifierIfPossible(), f = _.val;
            }
            var b,
              y = this.tryParsePluralOrSelectOptions(e, o, t, v);
            if (y.err) return y;
            if ((b = this.tryParseArgumentClose(s)).err) return b;
            var w = Fi(s, this.clonePosition());
            return "select" === o ? {
              val: {
                type: di.select,
                value: i,
                options: ta(y.val),
                location: w
              },
              err: null
            } : {
              val: {
                type: di.plural,
                value: i,
                options: ta(y.val),
                offset: f,
                pluralType: "plural" === o ? "cardinal" : "ordinal",
                location: w
              },
              err: null
            };
          default:
            return this.error(ci.INVALID_ARGUMENT_TYPE, Fi(r, l));
        }
      }, e.prototype.tryParseArgumentClose = function (e) {
        return this.isEOF() || 125 !== this.char() ? this.error(ci.EXPECT_ARGUMENT_CLOSING_BRACE, Fi(e, this.clonePosition())) : (this.bump(), {
          val: !0,
          err: null
        });
      }, e.prototype.parseSimpleArgStyleIfPossible = function () {
        for (var e = 0, t = this.clonePosition(); !this.isEOF();) {
          switch (this.char()) {
            case 39:
              this.bump();
              var i = this.clonePosition();
              if (!this.bumpUntil("'")) return this.error(ci.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE, Fi(i, this.clonePosition()));
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
            for (var t = e.split(Ai).filter(function (e) {
                return e.length > 0;
              }), i = [], a = 0, s = t; a < s.length; a++) {
              var n = s[a].split("/");
              if (0 === n.length) throw new Error("Invalid number skeleton");
              for (var r = n[0], o = n.slice(1), l = 0, c = o; l < c.length; l++) if (0 === c[l].length) throw new Error("Invalid number skeleton");
              i.push({
                stem: r,
                options: o
              });
            }
            return i;
          }(e);
        } catch (e) {
          return this.error(ci.INVALID_NUMBER_SKELETON, t);
        }
        return {
          val: {
            type: hi.number,
            tokens: i,
            location: t,
            parsedOptions: this.shouldParseSkeletons ? Pi(i) : {}
          },
          err: null
        };
      }, e.prototype.tryParsePluralOrSelectOptions = function (e, t, i, a) {
        for (var s, n = !1, r = [], o = new Set(), l = a.value, c = a.location;;) {
          if (0 === l.length) {
            var d = this.clonePosition();
            if ("select" === t || !this.bumpIf("=")) break;
            var h = this.tryParseDecimalInteger(ci.EXPECT_PLURAL_ARGUMENT_SELECTOR, ci.INVALID_PLURAL_ARGUMENT_SELECTOR);
            if (h.err) return h;
            c = Fi(d, this.clonePosition()), l = this.message.slice(d.offset, this.offset());
          }
          if (o.has(l)) return this.error("select" === t ? ci.DUPLICATE_SELECT_ARGUMENT_SELECTOR : ci.DUPLICATE_PLURAL_ARGUMENT_SELECTOR, c);
          "other" === l && (n = !0), this.bumpSpace();
          var u = this.clonePosition();
          if (!this.bumpIf("{")) return this.error("select" === t ? ci.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT : ci.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT, Fi(this.clonePosition(), this.clonePosition()));
          var p = this.parseMessage(e + 1, t, i);
          if (p.err) return p;
          var g = this.tryParseArgumentClose(u);
          if (g.err) return g;
          r.push([l, {
            value: p.val,
            location: Fi(u, this.clonePosition())
          }]), o.add(l), this.bumpSpace(), l = (s = this.parseIdentifierIfPossible()).value, c = s.location;
        }
        return 0 === r.length ? this.error("select" === t ? ci.EXPECT_SELECT_ARGUMENT_SELECTOR : ci.EXPECT_PLURAL_ARGUMENT_SELECTOR, Fi(this.clonePosition(), this.clonePosition())) : this.requiresOtherClause && !n ? this.error(ci.MISSING_OTHER_CLAUSE, Fi(this.clonePosition(), this.clonePosition())) : {
          val: r,
          err: null
        };
      }, e.prototype.tryParseDecimalInteger = function (e, t) {
        var i = 1,
          a = this.clonePosition();
        this.bumpIf("+") || this.bumpIf("-") && (i = -1);
        for (var s = !1, n = 0; !this.isEOF();) {
          var r = this.char();
          if (!(r >= 48 && r <= 57)) break;
          s = !0, n = 10 * n + (r - 48), this.bump();
        }
        var o = Fi(a, this.clonePosition());
        return s ? Xi(n *= i) ? {
          val: n,
          err: null
        } : this.error(t, o) : this.error(e, o);
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
        var t = ia(this.message, e);
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
        if (Qi(this.message, e, this.offset())) {
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
        for (; !this.isEOF() && ha(this.char());) this.bump();
      }, e.prototype.peek = function () {
        if (this.isEOF()) return null;
        var e = this.char(),
          t = this.offset(),
          i = this.message.charCodeAt(t + (e >= 65536 ? 2 : 1));
        return null != i ? i : null;
      }, e;
    }();
  function ca(e) {
    return e >= 97 && e <= 122 || e >= 65 && e <= 90;
  }
  function da(e) {
    return 45 === e || 46 === e || e >= 48 && e <= 57 || 95 === e || e >= 97 && e <= 122 || e >= 65 && e <= 90 || 183 == e || e >= 192 && e <= 214 || e >= 216 && e <= 246 || e >= 248 && e <= 893 || e >= 895 && e <= 8191 || e >= 8204 && e <= 8205 || e >= 8255 && e <= 8256 || e >= 8304 && e <= 8591 || e >= 11264 && e <= 12271 || e >= 12289 && e <= 55295 || e >= 63744 && e <= 64975 || e >= 65008 && e <= 65533 || e >= 65536 && e <= 983039;
  }
  function ha(e) {
    return e >= 9 && e <= 13 || 32 === e || 133 === e || e >= 8206 && e <= 8207 || 8232 === e || 8233 === e;
  }
  function ua(e) {
    return e >= 33 && e <= 35 || 36 === e || e >= 37 && e <= 39 || 40 === e || 41 === e || 42 === e || 43 === e || 44 === e || 45 === e || e >= 46 && e <= 47 || e >= 58 && e <= 59 || e >= 60 && e <= 62 || e >= 63 && e <= 64 || 91 === e || 92 === e || 93 === e || 94 === e || 96 === e || 123 === e || 124 === e || 125 === e || 126 === e || 161 === e || e >= 162 && e <= 165 || 166 === e || 167 === e || 169 === e || 171 === e || 172 === e || 174 === e || 176 === e || 177 === e || 182 === e || 187 === e || 191 === e || 215 === e || 247 === e || e >= 8208 && e <= 8213 || e >= 8214 && e <= 8215 || 8216 === e || 8217 === e || 8218 === e || e >= 8219 && e <= 8220 || 8221 === e || 8222 === e || 8223 === e || e >= 8224 && e <= 8231 || e >= 8240 && e <= 8248 || 8249 === e || 8250 === e || e >= 8251 && e <= 8254 || e >= 8257 && e <= 8259 || 8260 === e || 8261 === e || 8262 === e || e >= 8263 && e <= 8273 || 8274 === e || 8275 === e || e >= 8277 && e <= 8286 || e >= 8592 && e <= 8596 || e >= 8597 && e <= 8601 || e >= 8602 && e <= 8603 || e >= 8604 && e <= 8607 || 8608 === e || e >= 8609 && e <= 8610 || 8611 === e || e >= 8612 && e <= 8613 || 8614 === e || e >= 8615 && e <= 8621 || 8622 === e || e >= 8623 && e <= 8653 || e >= 8654 && e <= 8655 || e >= 8656 && e <= 8657 || 8658 === e || 8659 === e || 8660 === e || e >= 8661 && e <= 8691 || e >= 8692 && e <= 8959 || e >= 8960 && e <= 8967 || 8968 === e || 8969 === e || 8970 === e || 8971 === e || e >= 8972 && e <= 8991 || e >= 8992 && e <= 8993 || e >= 8994 && e <= 9e3 || 9001 === e || 9002 === e || e >= 9003 && e <= 9083 || 9084 === e || e >= 9085 && e <= 9114 || e >= 9115 && e <= 9139 || e >= 9140 && e <= 9179 || e >= 9180 && e <= 9185 || e >= 9186 && e <= 9254 || e >= 9255 && e <= 9279 || e >= 9280 && e <= 9290 || e >= 9291 && e <= 9311 || e >= 9472 && e <= 9654 || 9655 === e || e >= 9656 && e <= 9664 || 9665 === e || e >= 9666 && e <= 9719 || e >= 9720 && e <= 9727 || e >= 9728 && e <= 9838 || 9839 === e || e >= 9840 && e <= 10087 || 10088 === e || 10089 === e || 10090 === e || 10091 === e || 10092 === e || 10093 === e || 10094 === e || 10095 === e || 10096 === e || 10097 === e || 10098 === e || 10099 === e || 10100 === e || 10101 === e || e >= 10132 && e <= 10175 || e >= 10176 && e <= 10180 || 10181 === e || 10182 === e || e >= 10183 && e <= 10213 || 10214 === e || 10215 === e || 10216 === e || 10217 === e || 10218 === e || 10219 === e || 10220 === e || 10221 === e || 10222 === e || 10223 === e || e >= 10224 && e <= 10239 || e >= 10240 && e <= 10495 || e >= 10496 && e <= 10626 || 10627 === e || 10628 === e || 10629 === e || 10630 === e || 10631 === e || 10632 === e || 10633 === e || 10634 === e || 10635 === e || 10636 === e || 10637 === e || 10638 === e || 10639 === e || 10640 === e || 10641 === e || 10642 === e || 10643 === e || 10644 === e || 10645 === e || 10646 === e || 10647 === e || 10648 === e || e >= 10649 && e <= 10711 || 10712 === e || 10713 === e || 10714 === e || 10715 === e || e >= 10716 && e <= 10747 || 10748 === e || 10749 === e || e >= 10750 && e <= 11007 || e >= 11008 && e <= 11055 || e >= 11056 && e <= 11076 || e >= 11077 && e <= 11078 || e >= 11079 && e <= 11084 || e >= 11085 && e <= 11123 || e >= 11124 && e <= 11125 || e >= 11126 && e <= 11157 || 11158 === e || e >= 11159 && e <= 11263 || e >= 11776 && e <= 11777 || 11778 === e || 11779 === e || 11780 === e || 11781 === e || e >= 11782 && e <= 11784 || 11785 === e || 11786 === e || 11787 === e || 11788 === e || 11789 === e || e >= 11790 && e <= 11798 || 11799 === e || e >= 11800 && e <= 11801 || 11802 === e || 11803 === e || 11804 === e || 11805 === e || e >= 11806 && e <= 11807 || 11808 === e || 11809 === e || 11810 === e || 11811 === e || 11812 === e || 11813 === e || 11814 === e || 11815 === e || 11816 === e || 11817 === e || e >= 11818 && e <= 11822 || 11823 === e || e >= 11824 && e <= 11833 || e >= 11834 && e <= 11835 || e >= 11836 && e <= 11839 || 11840 === e || 11841 === e || 11842 === e || e >= 11843 && e <= 11855 || e >= 11856 && e <= 11857 || 11858 === e || e >= 11859 && e <= 11903 || e >= 12289 && e <= 12291 || 12296 === e || 12297 === e || 12298 === e || 12299 === e || 12300 === e || 12301 === e || 12302 === e || 12303 === e || 12304 === e || 12305 === e || e >= 12306 && e <= 12307 || 12308 === e || 12309 === e || 12310 === e || 12311 === e || 12312 === e || 12313 === e || 12314 === e || 12315 === e || 12316 === e || 12317 === e || e >= 12318 && e <= 12319 || 12320 === e || 12336 === e || 64830 === e || 64831 === e || e >= 65093 && e <= 65094;
  }
  function pa(e) {
    e.forEach(function (e) {
      if (delete e.location, bi(e) || yi(e)) for (var t in e.options) delete e.options[t].location, pa(e.options[t].value);else vi(e) && xi(e.style) || (fi(e) || _i(e)) && ki(e.style) ? delete e.style.location : $i(e) && pa(e.children);
    });
  }
  function ga(e, t) {
    void 0 === t && (t = {}), t = a({
      shouldParseSkeletons: !0,
      requiresOtherClause: !0
    }, t);
    var i = new la(e, t).parse();
    if (i.err) {
      var s = SyntaxError(ci[i.err.kind]);
      throw s.location = i.err.location, s.originalMessage = i.err.message, s;
    }
    return (null == t ? void 0 : t.captureLocation) || pa(i.val), i.val;
  }
  !function (e) {
    e.MISSING_VALUE = "MISSING_VALUE", e.INVALID_VALUE = "INVALID_VALUE", e.MISSING_INTL_API = "MISSING_INTL_API";
  }(oa || (oa = {}));
  var ma,
    va = function (e) {
      function t(t, i, a) {
        var s = e.call(this, t) || this;
        return s.code = i, s.originalMessage = a, s;
      }
      return i(t, e), t.prototype.toString = function () {
        return "[formatjs Error: ".concat(this.code, "] ").concat(this.message);
      }, t;
    }(Error),
    fa = function (e) {
      function t(t, i, a, s) {
        return e.call(this, 'Invalid values for "'.concat(t, '": "').concat(i, '". Options are "').concat(Object.keys(a).join('", "'), '"'), oa.INVALID_VALUE, s) || this;
      }
      return i(t, e), t;
    }(va),
    _a = function (e) {
      function t(t, i, a) {
        return e.call(this, 'Value for "'.concat(t, '" must be of type ').concat(i), oa.INVALID_VALUE, a) || this;
      }
      return i(t, e), t;
    }(va),
    ba = function (e) {
      function t(t, i) {
        return e.call(this, 'The intl string context variable "'.concat(t, '" was not provided to the string "').concat(i, '"'), oa.MISSING_VALUE, i) || this;
      }
      return i(t, e), t;
    }(va);
  function ya(e) {
    return "function" == typeof e;
  }
  function wa(e, t, i, a, s, n, r) {
    if (1 === e.length && gi(e[0])) return [{
      type: ma.literal,
      value: e[0].value
    }];
    for (var o = [], l = 0, c = e; l < c.length; l++) {
      var d = c[l];
      if (gi(d)) o.push({
        type: ma.literal,
        value: d.value
      });else if (wi(d)) "number" == typeof n && o.push({
        type: ma.literal,
        value: i.getNumberFormat(t).format(n)
      });else {
        var h = d.value;
        if (!s || !(h in s)) throw new ba(h, r);
        var u = s[h];
        if (mi(d)) u && "string" != typeof u && "number" != typeof u || (u = "string" == typeof u || "number" == typeof u ? String(u) : ""), o.push({
          type: "string" == typeof u ? ma.literal : ma.object,
          value: u
        });else if (fi(d)) {
          var p = "string" == typeof d.style ? a.date[d.style] : ki(d.style) ? d.style.parsedOptions : void 0;
          o.push({
            type: ma.literal,
            value: i.getDateTimeFormat(t, p).format(u)
          });
        } else if (_i(d)) {
          p = "string" == typeof d.style ? a.time[d.style] : ki(d.style) ? d.style.parsedOptions : a.time.medium;
          o.push({
            type: ma.literal,
            value: i.getDateTimeFormat(t, p).format(u)
          });
        } else if (vi(d)) {
          (p = "string" == typeof d.style ? a.number[d.style] : xi(d.style) ? d.style.parsedOptions : void 0) && p.scale && (u *= p.scale || 1), o.push({
            type: ma.literal,
            value: i.getNumberFormat(t, p).format(u)
          });
        } else {
          if ($i(d)) {
            var g = d.children,
              m = d.value,
              v = s[m];
            if (!ya(v)) throw new _a(m, "function", r);
            var f = v(wa(g, t, i, a, s, n).map(function (e) {
              return e.value;
            }));
            Array.isArray(f) || (f = [f]), o.push.apply(o, f.map(function (e) {
              return {
                type: "string" == typeof e ? ma.literal : ma.object,
                value: e
              };
            }));
          }
          if (bi(d)) {
            if (!(_ = d.options[u] || d.options.other)) throw new fa(d.value, u, Object.keys(d.options), r);
            o.push.apply(o, wa(_.value, t, i, a, s));
          } else if (yi(d)) {
            var _;
            if (!(_ = d.options["=".concat(u)])) {
              if (!Intl.PluralRules) throw new va('Intl.PluralRules is not available in this environment.\nTry polyfilling it using "@formatjs/intl-pluralrules"\n', oa.MISSING_INTL_API, r);
              var b = i.getPluralRules(t, {
                type: d.pluralType
              }).select(u - (d.offset || 0));
              _ = d.options[b] || d.options.other;
            }
            if (!_) throw new fa(d.value, u, Object.keys(d.options), r);
            o.push.apply(o, wa(_.value, t, i, a, s, u - (d.offset || 0)));
          } else ;
        }
      }
    }
    return function (e) {
      return e.length < 2 ? e : e.reduce(function (e, t) {
        var i = e[e.length - 1];
        return i && i.type === ma.literal && t.type === ma.literal ? i.value += t.value : e.push(t), e;
      }, []);
    }(o);
  }
  function $a(e, t) {
    return t ? Object.keys(e).reduce(function (i, s) {
      var n, r;
      return i[s] = (n = e[s], (r = t[s]) ? a(a(a({}, n || {}), r || {}), Object.keys(n).reduce(function (e, t) {
        return e[t] = a(a({}, n[t]), r[t] || {}), e;
      }, {})) : n), i;
    }, a({}, e)) : e;
  }
  function xa(e) {
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
  }(ma || (ma = {}));
  var ka = function () {
      function e(t, i, s, r) {
        void 0 === i && (i = e.defaultLocale);
        var o,
          l = this;
        if (this.formatterCache = {
          number: {},
          dateTime: {},
          pluralRules: {}
        }, this.format = function (e) {
          var t = l.formatToParts(e);
          if (1 === t.length) return t[0].value;
          var i = t.reduce(function (e, t) {
            return e.length && t.type === ma.literal && "string" == typeof e[e.length - 1] ? e[e.length - 1] += t.value : e.push(t.value), e;
          }, []);
          return i.length <= 1 ? i[0] || "" : i;
        }, this.formatToParts = function (e) {
          return wa(l.ast, l.locales, l.formatters, l.formats, e, void 0, l.message);
        }, this.resolvedOptions = function () {
          var e;
          return {
            locale: (null === (e = l.resolvedLocale) || void 0 === e ? void 0 : e.toString()) || Intl.NumberFormat.supportedLocalesOf(l.locales)[0]
          };
        }, this.getAst = function () {
          return l.ast;
        }, this.locales = i, this.resolvedLocale = e.resolveLocale(i), "string" == typeof t) {
          if (this.message = t, !e.__parse) throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");
          var c = r || {};
          c.formatters;
          var d = function (e, t) {
            var i = {};
            for (var a in e) Object.prototype.hasOwnProperty.call(e, a) && t.indexOf(a) < 0 && (i[a] = e[a]);
            if (null != e && "function" == typeof Object.getOwnPropertySymbols) {
              var s = 0;
              for (a = Object.getOwnPropertySymbols(e); s < a.length; s++) t.indexOf(a[s]) < 0 && Object.prototype.propertyIsEnumerable.call(e, a[s]) && (i[a[s]] = e[a[s]]);
            }
            return i;
          }(c, ["formatters"]);
          this.ast = e.__parse(t, a(a({}, d), {
            locale: this.resolvedLocale
          }));
        } else this.ast = t;
        if (!Array.isArray(this.ast)) throw new TypeError("A message must be provided as a String or AST.");
        this.formats = $a(e.formats, s), this.formatters = r && r.formatters || (void 0 === (o = this.formatterCache) && (o = {
          number: {},
          dateTime: {},
          pluralRules: {}
        }), {
          getNumberFormat: ii(function () {
            for (var e, t = [], i = 0; i < arguments.length; i++) t[i] = arguments[i];
            return new ((e = Intl.NumberFormat).bind.apply(e, n([void 0], t, !1)))();
          }, {
            cache: xa(o.number),
            strategy: pi.variadic
          }),
          getDateTimeFormat: ii(function () {
            for (var e, t = [], i = 0; i < arguments.length; i++) t[i] = arguments[i];
            return new ((e = Intl.DateTimeFormat).bind.apply(e, n([void 0], t, !1)))();
          }, {
            cache: xa(o.dateTime),
            strategy: pi.variadic
          }),
          getPluralRules: ii(function () {
            for (var e, t = [], i = 0; i < arguments.length; i++) t[i] = arguments[i];
            return new ((e = Intl.PluralRules).bind.apply(e, n([void 0], t, !1)))();
          }, {
            cache: xa(o.pluralRules),
            strategy: pi.variadic
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
      }, e.__parse = ga, e.formats = {
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
    Sa = ka;
  const za = {
      en: ti
    },
    Ea = {};
  function Aa(e) {
    return e.replace(/['"]+/g, "").split(/[-_]/)[0].toLowerCase();
  }
  function Ta(e) {
    const t = Aa(e);
    return t in za || !$e.includes(t);
  }
  function Ca(e, t, ...i) {
    const a = Aa(t);
    let s;
    try {
      s = e.split(".").reduce((e, t) => e[t], za[a]);
    } catch (t) {
      s = e.split(".").reduce((e, t) => e[t], za.en);
    }
    if (void 0 === s && (s = e.split(".").reduce((e, t) => e[t], za.en)), !i.length) return s;
    const n = {};
    for (let e = 0; e < i.length; e += 2) {
      let t = i[e];
      t = t.replace(/^{([^}]+)?}$/, "$1"), n[t] = i[e + 1];
    }
    try {
      return new Sa(s, t).format(n);
    } catch (e) {
      return "Translation " + e;
    }
  }
  function Oa(e, t, i) {
    e.dispatchEvent(new CustomEvent(t, {
      detail: i,
      bubbles: !0,
      composed: !0,
      cancelable: !1
    }));
  }
  function Ha(e, t) {
    return (e = e.toString()).split(",")[t];
  }
  function La(e, t) {
    switch (t) {
      case $t:
        return e.units == Oe ? F`${Bt(lt)}` : F`${Bt(ct)}`;
      case xe:
      case vt:
        return e.units == Oe ? F`${Bt(at)}` : F`${Bt(st)}`;
      case ht:
        return e.units == Oe ? F`${Bt("m<sup>2</sup>")}` : F`${Bt(et)}`;
      case ut:
        return e.units == Oe ? F`${Bt(tt)}` : F`${Bt(it)}`;
      default:
        return F``;
    }
  }
  function Ma(e, t) {
    !function (e, t) {
      Oa(e, "show-dialog", {
        dialogTag: "error-dialog",
        dialogImport: () => Promise.resolve().then(function () {
          return Ls;
        }),
        dialogParams: {
          error: t
        }
      });
    }(t, F`
    ${e.error}:${e.body.message ? F` ${e.body.message} ` : ""}
  `);
  }
  const Na = (e, t, i = !1) => {
    i ? history.replaceState(null, "", t) : history.pushState(null, "", t), Oa(window, "location-changed", {
      replace: i
    });
  };
  function Ia(e) {
    var t;
    if (!e) return "Unknown error";
    if ("string" == typeof e) return e;
    const i = e;
    return (null === (t = null == i ? void 0 : i.body) || void 0 === t ? void 0 : t.message) || (null == i ? void 0 : i.message) || (null == i ? void 0 : i.error) || JSON.stringify(e);
  }
  function Pa(e, t) {
    e.dispatchEvent(new CustomEvent("hass-notification", {
      detail: {
        message: t
      },
      bubbles: !0,
      composed: !0
    }));
  }
  function Da(e, t, i, a) {
    var s;
    Pa(e, `${Ca(i, null !== (s = null == t ? void 0 : t.language) && void 0 !== s ? s : "en")}: ${Ia(a)}`);
  }
  var Ba = "M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",
    Ua = "M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",
    Ra = "M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z";
  const ja = e => e.callWS({
      type: we + "/config"
    }),
    Fa = e => e.callWS({
      type: we + "/zones"
    }),
    Wa = (e, t) => e.callApi("POST", we + "/zones", t),
    Za = e => e.callWS({
      type: we + "/modules"
    }),
    Ga = e => e.callWS({
      type: we + "/allmodules"
    }),
    qa = (e, t) => e.callApi("POST", we + "/modules", t),
    Va = e => e.callWS({
      type: we + "/mappings"
    }),
    Ka = (e, t) => e.callApi("POST", we + "/mappings", t),
    Xa = e => e.callWS({
      type: we + "/weather_config"
    }),
    Ya = (e, t, i, a) => e.callWS({
      type: we + "/weather_config_save",
      use_weather_service: t,
      weather_service: null != i ? i : null,
      api_key: null != a ? a : null
    }),
    Ja = e => e.callWS({
      type: we + "/coordinates"
    }),
    Qa = e => {
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
      return s([pe({
        attribute: !1
      })], t.prototype, "hass", void 0), t;
    };
  var es, ts;
  !function (e) {
    e.Sunrise = "sunrise", e.Sunset = "sunset", e.SolarAzimuth = "solar_azimuth";
  }(es || (es = {})), function (e) {
    e.Disabled = "disabled", e.Manual = "manual", e.Automatic = "automatic";
  }(ts || (ts = {}));
  const is = () => {
      const e = e => {
          let t = {};
          for (let i = 0; i < e.length; i += 2) {
            const a = e[i],
              s = i < e.length ? e[i + 1] : void 0;
            t = Object.assign(Object.assign({}, t), {
              [a]: s
            });
          }
          return t;
        },
        t = window.location.pathname.split("/");
      let i = {
        page: t[2] || "general",
        params: {}
      };
      if (t.length > 3) {
        let a = t.slice(3);
        if (t.includes("filter")) {
          const t = a.findIndex(e => "filter" == e),
            s = a.slice(t + 1);
          a = a.slice(0, t), i = Object.assign(Object.assign({}, i), {
            filter: e(s)
          });
        }
        a.length && (a.length % 2 && (i = Object.assign(Object.assign({}, i), {
          subpage: a.shift()
        })), a.length && (i = Object.assign(Object.assign({}, i), {
          params: e(a)
        })));
      }
      return i;
    },
    as = (e, ...t) => {
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
      const a = e => {
        let t = Object.keys(e);
        t = t.filter(t => e[t]), t.sort();
        let i = "";
        return t.forEach(t => {
          const a = e[t];
          i = i.length ? `${i}/${t}/${a}` : `${t}/${a}`;
        }), i;
      };
      let s = `/${we}/${i.page}`;
      return i.subpage && (s = `${s}/${i.subpage}`), a(i.params).length && (s = `${s}/${a(i.params)}`), i.filter && (s = `${s}/filter/${a(i.filter)}`), s;
    },
    ss = h`
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
  h`
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
  const ns = e => String(e).padStart(2, "0");
  function rs(e) {
    return e instanceof Date ? e : new Date(e);
  }
  function os(e) {
    const t = rs(e);
    return `${ns(t.getHours())}:${ns(t.getMinutes())}`;
  }
  function ls(e, t) {
    return e.getFullYear() === t.getFullYear() && e.getMonth() === t.getMonth() && e.getDate() === t.getDate();
  }
  class cs extends Qa(ce) {
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
        type: we + "_config_updated"
      })];
    }
    async _fetchData() {
      if (!this.hass) return;
      const e = !this._initialLoadDone;
      try {
        e && (this.isLoading = !0);
        const [i, a, s] = await Promise.all([ja(this.hass), Fa(this.hass), (t = this.hass, t.callWS({
          type: we + "/irrigation_outlook"
        })).catch(e => {
          console.error("Failed to fetch irrigation outlook:", e);
        })]);
        this.config = i, this.zones = a, this._outlook = s, this._initialLoadDone = !0;
      } catch (e) {
        console.error("Error fetching data:", e), Da(this, this.hass, "common.errors.load_failed", e);
      } finally {
        e && (this.isLoading = !1), this._scheduleUpdate();
      }
      var t;
    }
    handleCalculateAllZones() {
      var e;
      this.hass && (this.isSaving = !0, this._scheduleUpdate(), (e = this.hass, e.callApi("POST", we + "/zones", {
        calculate_all: !0
      })).catch(e => {
        console.error("Failed to calculate all zones:", e), Da(this, this.hass, "common.errors.action_failed", e);
      }).finally(() => {
        this.isSaving = !1, this._fetchData().catch(e => console.error("fetchData after calc-all:", e));
      }));
    }
    handleUpdateAllZones() {
      var e;
      this.hass && (this.isSaving = !0, this._scheduleUpdate(), (e = this.hass, e.callApi("POST", we + "/zones", {
        update_all: !0
      })).catch(e => {
        console.error("Failed to update all zones:", e), Da(this, this.hass, "common.errors.action_failed", e);
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
        a = i ? void 0 : this.zones.find(e => {
          var i;
          return (null === (i = e.id) || void 0 === i ? void 0 : i.toString()) === t;
        }),
        s = i ? `(${this._linkedZoneCount})` : `: ${null !== (e = null == a ? void 0 : a.name) && void 0 !== e ? e : t}`;
      try {
        await (n = this.hass, r = i ? void 0 : t, n.callWS(Object.assign({
          type: we + "/irrigate_now"
        }, void 0 !== r ? {
          zone_id: r
        } : {}))), Pa(this, `${Ca("panels.zones.confirm_irrigate.toast_started", this.hass.language)} ${s}`);
      } catch (e) {
        const t = Ia(e);
        console.error("irrigate_now failed", e), Pa(this, `${Ca("panels.zones.confirm_irrigate.toast_failed", this.hass.language)}: ${t}`);
      }
      var n, r;
    }
    handleCalculateZone(e) {
      const t = this.zones[e];
      var i, a;
      t && null != t.id && this.hass && (this._operationError = null, this.isSaving = !0, this._scheduleUpdate(), (i = this.hass, a = t.id.toString(), i.callApi("POST", we + "/zones", {
        id: a,
        calculate: !0,
        override_cache: !0
      })).catch(e => {
        const t = Ia(e);
        console.error("calculateZone failed:", e), this._operationError = t;
      }).finally(() => {
        this.isSaving = !1, this._fetchData().catch(e => console.error("fetchData after calc:", e));
      }));
    }
    handleUpdateZone(e) {
      const t = this.zones[e];
      var i, a;
      t && null != t.id && this.hass && (this._operationError = null, this.isSaving = !0, this._scheduleUpdate(), (i = this.hass, a = t.id.toString(), i.callApi("POST", we + "/zones", {
        id: a,
        update: !0
      })).catch(e => {
        const t = Ia(e);
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
      Na(0, t ? as("setup", "zones", t) : as("setup", "zones"));
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
      var t, i, a;
      const s = null !== (t = e.duration) && void 0 !== t ? t : 0,
        n = Number(null !== (i = e.bucket) && void 0 !== i ? i : 0),
        r = Number(null !== (a = e.bucket_threshold) && void 0 !== a ? a : 0);
      return s > 0 && n < r;
    }
    _formatRunTime(e) {
      if (!this.hass) return "";
      const t = this.hass.language,
        i = new Date(e),
        a = os(i),
        s = new Date();
      return ls(i, s) ? `${Ca("panels.zones.outlook.today", t)} ${a}` : ls(i, function (e, t) {
        const i = new Date(e.getTime());
        return i.setDate(i.getDate() + t), i;
      }(s, 1)) ? `${Ca("panels.zones.outlook.tomorrow", t)} ${a}` : function (e, t) {
        const i = rs(e);
        return `${new Intl.DateTimeFormat(t, {
          weekday: "short"
        }).format(i)} ${os(i)}`;
      }(i, t);
    }
    _guardLabel(e) {
      return Ca(`panels.zones.outlook.checks.${e.id}`, this.hass.language);
    }
    _guardDetail(e) {
      var t;
      return e.available && null !== e.observed ? Ca(`panels.zones.outlook.check_detail.${e.id}`, this.hass.language, "{observed}", String(e.observed), "{threshold}", String(null !== (t = e.threshold) && void 0 !== t ? t : "")) : "";
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
        ${Ca("panels.zones.outlook.provisional", e)}
      </div>
    `;
    }
    _openSchedules() {
      Na(0, as("setup", "when-to-water"));
    }
    _runActionLabel(e) {
      return Ca(`panels.zones.outlook.actions.${e.action}`, this.hass.language);
    }
    _runTargetsLabel(e) {
      const t = this.hass.language;
      if ("all" === e.zones) return Ca("panels.zones.outlook.targets_all", t);
      const i = Array.isArray(e.zones) ? e.zones.length : 0;
      return Ca("panels.zones.outlook.targets_zones", t, "{count}", String(i));
    }
    _renderOutlookBanner() {
      if (!this.hass || !this._outlook) return F``;
      const e = this.hass.language,
        t = this._nextIrrigateRun,
        i = this._triggeredGuards,
        a = this._outlook.last_skip_evaluation;
      return t && t.next_run_utc ? F`
      <ha-card class="outlook-card">
        <div class="outlook">
          <div class="outlook-line outlook-headline">
            <ha-icon icon="mdi:calendar-clock"></ha-icon>
            <span>
              <strong
                >${Ca("panels.zones.outlook.next_run", e)}:</strong
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
                    >${Ca("panels.zones.outlook.will_skip", e)}</span
                  >
                  <button
                    class="outlook-info-btn"
                    aria-expanded="${this._skipDetailsOpen}"
                    title="${Ca("panels.zones.outlook.why_skipped", e)}"
                    @click="${() => {
        this._skipDetailsOpen = !this._skipDetailsOpen;
      }}"
                  >
                    <ha-icon
                      icon="${this._skipDetailsOpen ? "mdi:chevron-up" : "mdi:information-outline"}"
                    ></ha-icon>
                    <span class="outlook-info-label"
                      >${Ca("panels.zones.outlook.why_skipped", e)}</span
                    >
                  </button>
                </div>
                ${this._skipDetailsOpen ? this._renderSkipReasons() : ""}
              ` : F`
                <div class="outlook-line outlook-clear">
                  <ha-icon icon="mdi:check-circle-outline"></ha-icon>
                  <span
                    >${Ca("panels.zones.outlook.will_run", e)}</span
                  >
                </div>
              `}
          ${a ? this._renderLastRunLine(a) : ""}
        </div>
      </ha-card>
    ` : F`
        <ha-card class="outlook-card">
          <div class="outlook">
            <div class="outlook-line outlook-headline">
              <ha-icon icon="mdi:calendar-alert"></ha-icon>
              <span>${Ca("panels.zones.outlook.no_schedule", e)}</span>
              ${this.hideSettingsLinks ? "" : F`
                    <button
                      class="outlook-link"
                      @click="${this._openSchedules}"
                    >
                      ${Ca("panels.zones.outlook.setup_schedule", e)}
                    </button>
                  `}
            </div>
            ${a ? this._renderLastRunLine(a) : ""}
          </div>
        </ha-card>
      `;
    }
    _renderLastRunLine(e) {
      const t = this.hass.language,
        i = function (e, t) {
          const i = rs(e).getTime() - Date.now(),
            a = new Intl.RelativeTimeFormat(t, {
              numeric: "auto"
            }),
            s = Math.round(i / 1e3);
          if (Math.abs(s) < 60) return a.format(s, "second");
          const n = Math.round(s / 60);
          if (Math.abs(n) < 60) return a.format(n, "minute");
          const r = Math.round(n / 60);
          if (Math.abs(r) < 24) return a.format(r, "hour");
          const o = Math.round(r / 24);
          if (Math.abs(o) < 30) return a.format(o, "day");
          const l = Math.round(o / 30);
          return Math.abs(l) < 12 ? a.format(l, "month") : a.format(Math.round(l / 12), "year");
        }(e.timestamp, t),
        a = e.checks.filter(e => e.enabled && e.would_skip).map(e => this._guardLabel(e).toLowerCase()).join(", "),
        s = e.would_skip ? `${Ca("panels.zones.outlook.last_run_skipped", t)}${a ? ` (${a})` : ""}` : Ca("panels.zones.outlook.last_run_ran", t);
      return F`
      <div class="outlook-line outlook-last">
        <span class="outlook-dim"
          >${Ca("panels.zones.outlook.last_run", t)}:</span
        >
        <span>${s} · ${i}</span>
      </div>
    `;
    }
    _renderZoneDecision(e) {
      var t;
      if (!this.hass) return F``;
      const i = this.hass.language,
        a = null !== (t = e.duration) && void 0 !== t ? t : 0;
      let s, n, r;
      if (e.state === ts.Disabled) s = Ca("panels.zones.status.decision_disabled", i), n = "neutral", r = "mdi:power-off";else if (e.last_calculated) {
        if (this._zoneHasDeficit(e)) {
          const t = function (e) {
              const t = Math.round(e);
              if (t < 60) return `${t} s`;
              const i = Math.floor(t / 60),
                a = t % 60;
              return a ? `${i} min ${a} s` : `${i} min`;
            }(a),
            o = this._triggeredGuards,
            l = this._nextIrrigateRunForZone(e);
          o.length > 0 ? (s = Ca("panels.zones.status.decision_water_skip", i, "{duration}", t, "{reason}", this._guardLabel(o[0]).toLowerCase()), n = "skip", r = "mdi:weather-rainy") : l && l.next_run_utc ? (s = Ca("panels.zones.status.decision_water_at", i, "{duration}", t, "{time}", this._formatRunTime(l.next_run_utc)), n = "water", r = "mdi:water") : (s = Ca("panels.zones.status.decision_water_no_schedule", i, "{duration}", t), n = "water", r = "mdi:water-alert");
        } else s = Ca("panels.zones.status.decision_no_water", i), n = "ok", r = "mdi:check-circle-outline";
      } else s = Ca("panels.zones.status.decision_unknown", i), n = "unknown", r = "mdi:help-circle-outline";
      return F`
      <div class="zone-decision ${n}">
        <ha-icon icon="${r}"></ha-icon>
        <span>${s}</span>
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
        a = La(this.config, vt),
        s = t.live_deficit < 0 ? "var(--warning-color)" : "var(--success-color)",
        n = Ca(`panels.zones.status.estimate_method.${"proxy" === t.method ? "proxy" : "hourly"}`, i) + (t.as_of ? ` · ${os(t.as_of)}` : "");
      return F`
      <span class="status-sep">·</span>
      <span class="zone-estimate" title="${n}">
        ${Ca("panels.zones.status.estimate_now", i)}
        <strong style="color: ${s}"
          >≈ ${t.live_deficit.toFixed(2)} ${a}</strong
        >
        <span class="estimate-tag"
          >${Ca("panels.zones.status.estimate_tag", i)}</span
        >
      </span>
    `;
    }
    _renderZoneNextRun(e) {
      if (!this.hass) return F``;
      const t = this._nextIrrigateRunForZone(e);
      if (!t || !t.next_run_utc) return F``;
      return e.state !== ts.Disabled && e.last_calculated && this._zoneHasDeficit(e) && 0 === this._triggeredGuards.length ? F`` : F`
      <span class="status-sep">·</span>
      <span>
        ${Ca("panels.zones.outlook.next_run", this.hass.language)}:
        <strong>${this._formatRunTime(t.next_run_utc)}</strong>
      </span>
    `;
    }
    renderZone(e, t) {
      var i, a;
      if (!this.hass) return F``;
      const s = Number(null !== (i = e.bucket) && void 0 !== i ? i : 0),
        n = s < 0 ? "var(--warning-color)" : "var(--success-color)",
        r = e.state === ts.Automatic ? "state-automatic" : e.state === ts.Manual ? "state-manual" : "state-disabled",
        o = e.last_calculated ? function (e) {
          const t = rs(e);
          return `${t.getFullYear()}-${ns(t.getMonth() + 1)}-${ns(t.getDate())} ${ns(t.getHours())}:${ns(t.getMinutes())}`;
        }(e.last_calculated) : Ca("panels.zones.status.never", this.hass.language);
      return F`
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          <span class="zone-state-badge ${r}">
            ${Ca(`panels.zones.labels.states.${e.state}`, this.hass.language)}
          </span>
          ${this.hideSettingsLinks ? "" : F`
                <ha-icon-button
                  .path="${"M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"}"
                  title="${Ca("panels.zones.actions.open_settings", this.hass.language)}"
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
              title="${Ca("panels.zones.help.bucket", this.hass.language)}"
            >
              ${Ca("panels.zones.labels.bucket", this.hass.language)}:
              <strong style="color: ${n}"
                >${s.toFixed(2)}
                ${La(this.config, vt)}</strong
              >
            </span>
            <span class="status-sep">·</span>
            <span>
              ${Ca("panels.zones.status.last_checked", this.hass.language)}:
              <strong>${o}</strong>
            </span>
            ${this._renderZoneEstimate(e)} ${this._renderZoneNextRun(e)}
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div class="card-content zone-action-bar">
          ${"full" === this.actionsMode && e.state === ts.Automatic ? F`
                <button
                  class="action-btn"
                  title="${Ca("panels.zones.help.update", this.hass.language)}"
                  @click="${() => this.handleUpdateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${Ca("panels.zones.actions.update", this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${Ca("panels.zones.help.calculate", this.hass.language)}"
                  @click="${() => this.handleCalculateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${Ca("panels.zones.actions.calculate", this.hass.language)}
                </button>
              ` : ""}
          ${"none" !== this.actionsMode && e.linked_entity && (null !== (a = e.duration) && void 0 !== a ? a : 0) > 0 ? F`
                <button
                  class="action-btn"
                  raised
                  @click="${() => {
        void 0 !== e.id && (this._confirmIrrigate = e.id.toString());
      }}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${Ca("panels.zones.labels.irrigate_now", this.hass.language)}
                </button>
              ` : e.linked_entity ? "" : F`
                  <button
                    class="action-btn"
                    disabled
                    title="${Ca("panels.zones.help.irrigate_link_entity", this.hass.language)}"
                  >
                    <ha-icon icon="mdi:water"></ha-icon>
                    ${Ca("panels.zones.labels.irrigate_now", this.hass.language)}
                  </button>
                  <span class="zones-top-note">
                    ${Ca("panels.zones.help.irrigate_link_entity", this.hass.language)}
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
        <ha-card header="${Ca("panels.zones.title", this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Ca("common.loading-messages.general", this.hass.language)}
            </div>
          </div>
        </ha-card>
      `;
      const i = this.zones.some(e => {
          var t;
          return e.linked_entity && (null !== (t = e.duration) && void 0 !== t ? t : 0) > 0;
        }),
        a = 0 === this.zones.length;
      return F`
      ${a ? this.hideSettingsLinks ? F`
              <ha-card>
                <div class="card-content description-text">
                  ${Ca("panels.zones.no_items", this.hass.language)}
                </div>
              </ha-card>
            ` : F`
              <ha-card class="setup-banner-card">
                <div class="setup-banner">
                  <div class="setup-banner-icon">🌱</div>
                  <div class="setup-banner-content">
                    <div class="setup-banner-title">
                      ${Ca("wizard.title", this.hass.language)}
                    </div>
                    <div class="setup-banner-desc">
                      ${Ca("wizard.setup_complete_banner", this.hass.language)}
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
                    ${Ca("wizard.open_wizard", this.hass.language)}
                  </button>
                </div>
              </ha-card>
            ` : ""}
      ${a ? "" : this._renderOutlookBanner()}

      <!-- Zones header card: run-all operational actions -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${Ca("panels.zones.title", this.hass.language)}
          </div>
        </div>
        <div class="card-content zones-top-actions">
          ${"full" === this.actionsMode ? F`
                <button
                  class="action-btn"
                  title="${Ca("panels.zones.help.update_all", this.hass.language)}"
                  @click="${this.handleUpdateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${Ca("panels.zones.cards.zone-actions.actions.update-all", this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${Ca("panels.zones.help.calculate_all", this.hass.language)}"
                  @click="${this.handleCalculateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${Ca("panels.zones.cards.zone-actions.actions.calculate-all", this.hass.language)}
                </button>
              ` : ""}
          ${"none" !== this.actionsMode ? F`
                <button
                  class="action-btn"
                  raised
                  title="${Ca("panels.zones.help.irrigate_all", this.hass.language)}"
                  @click="${() => {
        this._confirmIrrigate = "all";
      }}"
                  ?disabled="${!i || this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${Ca("panels.zones.actions.irrigate_all", this.hass.language)}
                </button>
              ` : ""}
          ${i ? "" : F`<span class="zones-top-note"
                >${Ca("panels.info.cards.irrigate_now.no_linked_zones", this.hass.language)}</span
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
              heading="${Ca("panels.zones.confirm_irrigate.title", this.hass.language)}"
            >
              <p>
                ${Ca("panels.zones.confirm_irrigate.body", this.hass.language)}
              </p>
              <p>
                <strong>
                  ${"all" === this._confirmIrrigate ? `${Ca("panels.zones.confirm_irrigate.all_linked_zones", this.hass.language)} (${this._linkedZoneCount})` : null !== (t = null === (e = this.zones.find(e => {
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
                  ${Ca("common.actions.cancel", this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._doIrrigate}"
                >
                  ${Ca("panels.zones.labels.irrigate_now", this.hass.language)}
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
                  .path="${Ba}"
                  @click="${() => {
        this._operationError = null;
      }}"
                  aria-label="${Ca("common.actions.cancel", this.hass.language)}"
                ></ha-icon-button>
              </div>
            </ha-card>
          ` : ""}

      <!-- Zone cards -->
      ${this.zones.map((e, t) => this.renderZone(e, t))}
    `;
    }
    static get styles() {
      return h`
      ${ss}

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
  s([pe()], cs.prototype, "config", void 0), s([pe({
    type: Boolean
  })], cs.prototype, "hideSettingsLinks", void 0), s([pe({
    attribute: !1
  })], cs.prototype, "actionsMode", void 0), s([pe({
    type: Array
  })], cs.prototype, "zones", void 0), s([ge()], cs.prototype, "_outlook", void 0), s([pe({
    type: Boolean
  })], cs.prototype, "isLoading", void 0), s([pe({
    type: Boolean
  })], cs.prototype, "isSaving", void 0), s([ge()], cs.prototype, "_operationError", void 0), s([ge()], cs.prototype, "_confirmIrrigate", void 0), s([ge()], cs.prototype, "_skipDetailsOpen", void 0), customElements.get("smart-irrigation-view-zones") || customElements.define("smart-irrigation-view-zones", cs)
  /**
       * @license
       * Copyright 2020 Google LLC
       * SPDX-License-Identifier: BSD-3-Clause
       */;
  const ds = {},
    hs = It(class extends Pt {
      constructor(e) {
        if (super(e), e.type !== Mt && e.type !== Ht && e.type !== Nt) throw Error("The `live` directive is not allowed on child or event bindings");
        if (!(e => void 0 === e.strings)(e)) throw Error("`live` bindings can only contain a single expression");
      }
      render(e) {
        return e;
      }
      update(e, [t]) {
        if (t === W || t === Z) return t;
        const i = e.element,
          a = e.name;
        if (e.type === Mt) {
          if (t === i[a]) return W;
        } else if (e.type === Nt) {
          if (!!t === i.hasAttribute(a)) return W;
        } else if (e.type === Ht && i.getAttribute(a) === t + "") return W;
        return ((e, t = ds) => {
          e._$AH = t;
          /**
               * @license
               * Copyright 2020 Google LLC
               * SPDX-License-Identifier: BSD-3-Clause
               */
        })(e), t;
      }
    });
  let us = class extends ce {
    constructor() {
      super(...arguments), this.label = "", this.unit = "", this.help = "", this.required = !1, this._helpOpen = !1;
    }
    _toggleHelp() {
      this._helpOpen = !this._helpOpen;
    }
    render() {
      return F`
      <div class="si-field">
        <div class="si-field-header">
          <span class="si-field-label">
            ${this.label}${this.required ? F`<span class="si-field-required" aria-label="required">
                  *</span
                >` : ""}
          </span>
          <span class="si-field-meta">
            ${this.unit ? F`<span class="si-field-unit">${this.unit}</span>` : ""}
            ${this.help ? F`
                  <button
                    class="si-field-help-btn ${this._helpOpen ? "open" : ""}"
                    type="button"
                    aria-label="Toggle help"
                    @click="${this._toggleHelp}"
                  >
                    ⓘ
                  </button>
                ` : ""}
          </span>
        </div>
        <slot></slot>
        ${this._helpOpen && this.help ? F`<div class="si-field-help-text">${this.help}</div>` : ""}
      </div>
    `;
    }
    static get styles() {
      return h`
      :host {
        display: block;
      }

      .si-field {
        display: flex;
        flex-direction: column;
        gap: 4px;
        margin: 6px 0;
      }

      .si-field-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
      }

      .si-field-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }

      .si-field-required {
        color: var(--error-color, #b00020);
        font-weight: 700;
      }

      .si-field-meta {
        display: flex;
        align-items: center;
        gap: 6px;
        flex-shrink: 0;
      }

      .si-field-unit {
        font-size: 0.78rem;
        font-weight: 500;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border: 1px solid var(--divider-color);
        border-radius: 3px;
        padding: 1px 5px;
        white-space: nowrap;
      }

      .si-field-help-btn {
        background: none;
        border: none;
        cursor: pointer;
        color: var(--secondary-text-color);
        font-size: 0.95rem;
        padding: 0 2px;
        line-height: 1;
        transition: color 0.15s;
        user-select: none;
      }

      .si-field-help-btn:hover,
      .si-field-help-btn.open {
        color: var(--primary-color);
      }

      .si-field-help-text {
        font-size: 0.82rem;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border-left: 3px solid var(--primary-color);
        border-radius: 0 3px 3px 0;
        padding: 6px 10px;
        line-height: 1.45;
        margin-top: 2px;
      }
    `;
    }
  };
  s([pe()], us.prototype, "label", void 0), s([pe()], us.prototype, "unit", void 0), s([pe()], us.prototype, "help", void 0), s([pe({
    type: Boolean
  })], us.prototype, "required", void 0), s([ge()], us.prototype, "_helpOpen", void 0), us = s([he("si-field")], us);
  let ps = class extends ce {
    constructor() {
      super(...arguments), this.useWeather = !1, this.service = ze, this.apiKey = "", this.weatherConfig = null, this._testing = !1, this._testResult = null, this._testResultTimer = null;
    }
    disconnectedCallback() {
      super.disconnectedCallback(), this._testResultTimer && (clearTimeout(this._testResultTimer), this._testResultTimer = null);
    }
    _emit(e, t) {
      this.dispatchEvent(new CustomEvent(e, {
        detail: {
          value: t
        },
        bubbles: !0,
        composed: !0
      }));
    }
    get _noApiKeyServices() {
      var e, t;
      return null !== (t = null === (e = this.weatherConfig) || void 0 === e ? void 0 : e.no_api_key_services) && void 0 !== t ? t : [ze];
    }
    get _needsKey() {
      return this.useWeather && !!this.service && !this._noApiKeyServices.includes(this.service);
    }
    get _hasStoredKey() {
      const e = this.weatherConfig;
      return this.service === ke ? !!(null == e ? void 0 : e.has_owm_api_key) : this.service === Se && !!(null == e ? void 0 : e.has_pw_api_key);
    }
    async _testApiKey() {
      if (this.hass && !this._testing) {
        this._testing = !0, this._testResult = null, this._testResultTimer && (clearTimeout(this._testResultTimer), this._testResultTimer = null);
        try {
          this._testResult = await (e = this.hass, t = this.service, i = this.apiKey || null, e.callWS({
            type: we + "/weather_config_test",
            weather_service: null != t ? t : null,
            api_key: null != i ? i : null
          })), this._testResultTimer = window.setTimeout(() => {
            this._testResult = null, this._testResultTimer = null;
          }, 12e3);
        } catch (e) {
          this._testResult = {
            success: !1,
            error: "unknown"
          };
        } finally {
          this._testing = !1;
        }
        var e, t, i;
      }
    }
    render() {
      var e, t;
      const i = null !== (t = null === (e = this.hass) || void 0 === e ? void 0 : e.language) && void 0 !== t ? t : "en";
      return F`
      <si-field
        label="${Ca("weather_service_config.enabled_label", i)}"
      >
        <ha-switch
          .checked="${this.useWeather}"
          @change="${e => this._emit("useweather-changed", e.target.checked)}"
        ></ha-switch>
      </si-field>

      ${this.useWeather ? this._renderServiceAndKey(i) : ""}
    `;
    }
    _renderServiceAndKey(e) {
      return F`
      <si-field
        label="${Ca("weather_service_config.service_label", e)}"
      >
        <select
          class="si-input"
          .value="${hs(this.service || ze)}"
          @change="${e => {
        this._testResult = null, this._emit("service-changed", e.target.value);
      }}"
        >
          <option
            value="${ze}"
            ?selected="${(this.service || ze) === ze}"
          >
            ${Ca("weather_service_config.openmeteo", e)}
          </option>
          <option
            value="${ke}"
            ?selected="${this.service === ke}"
          >
            ${Ca("weather_service_config.owm", e)}
          </option>
          <option
            value="${Se}"
            ?selected="${this.service === Se}"
          >
            ${Ca("weather_service_config.pw", e)}
          </option>
        </select>
      </si-field>

      ${this._needsKey ? this._renderKeyField(e) : F`<div class="info-note">
            ${Ca("weather_service_config.no_api_key_needed", e)}
          </div>`}
    `;
    }
    _renderKeyField(e) {
      var t;
      const i = this._hasStoredKey;
      return F`
      <si-field
        label="${Ca("weather_service_config.api_key_label", e)}"
        help="${Ca("weather_service_config.api_key_help", e)}"
      >
        <span class="api-badge ${i ? "configured" : "missing"}"
          >${Ca(i ? "weather_service_config.api_key_configured" : "weather_service_config.api_key_not_configured", e)}</span
        >
        <div class="api-row">
          <input
            type="password"
            class="si-input flex1"
            placeholder="${Ca("weather_service_config.api_key_placeholder", e)}"
            .value="${this.apiKey}"
            @input="${e => {
        this._testResult = null, this._emit("apikey-changed", e.target.value);
      }}"
          />
          <button
            class="test-btn"
            type="button"
            ?disabled="${this._testing || !this.apiKey && !i}"
            @click="${this._testApiKey}"
          >
            ${this._testing ? Ca("weather_service_config.test_button_testing", e) : Ca("weather_service_config.test_button", e)}
          </button>
        </div>
        ${null !== this._testResult ? F`<div
              class="test-result ${this._testResult.success ? "success" : "error"}"
            >
              ${this._testResult.success ? Ca("weather_service_config.test_success", e) : Ca("weather_service_config.test_error_" + (null !== (t = this._testResult.error) && void 0 !== t ? t : "unknown"), e)}
            </div>` : ""}
      </si-field>
    `;
    }
    static get styles() {
      return h`
      :host {
        display: block;
      }

      .si-input {
        width: 100%;
        background: var(--input-fill-color, var(--secondary-background-color));
        border: 1px solid var(--input-ink-color, var(--secondary-text-color));
        border-radius: 4px;
        color: var(--primary-text-color);
        padding: 6px 10px;
        font-family: inherit;
        font-size: 0.9375rem;
        box-sizing: border-box;
        height: 36px;
      }

      .si-input:focus {
        border-color: var(--primary-color);
        outline: none;
      }

      select.si-input {
        cursor: pointer;
      }

      .si-input.flex1 {
        flex: 1;
      }

      .api-row {
        display: flex;
        gap: 8px;
        align-items: center;
        flex-wrap: wrap;
        margin-top: 4px;
      }

      .api-badge {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 10px;
        margin-bottom: 4px;
      }

      .api-badge.configured {
        background: rgba(76, 175, 80, 0.15);
        color: #2e7d32;
      }

      .api-badge.missing {
        background: rgba(var(--rgb-warning-color, 255, 152, 0), 0.15);
        color: var(--warning-color, #ef6c00);
      }

      .test-btn {
        background: transparent;
        border: 1px solid var(--primary-color);
        border-radius: 4px;
        color: var(--primary-color);
        cursor: pointer;
        font-family: inherit;
        font-size: 0.875rem;
        font-weight: 500;
        padding: 8px 14px;
        white-space: nowrap;
        flex-shrink: 0;
      }

      .test-btn:hover:not(:disabled) {
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
      }

      .test-btn:disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }

      .test-result {
        font-size: 0.83rem;
        font-weight: 500;
        margin-top: 6px;
        padding: 5px 10px;
        border-radius: 4px;
      }

      .test-result.success {
        background: rgba(76, 175, 80, 0.12);
        color: #2e7d32;
      }

      .test-result.error {
        background: rgba(var(--rgb-error-color, 176, 0, 32), 0.1);
        color: var(--error-color, #b00020);
      }

      .info-note {
        font-size: 0.83rem;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border-radius: 4px;
        padding: 8px 12px;
        margin-top: 8px;
      }
    `;
    }
  };
  s([pe({
    attribute: !1
  })], ps.prototype, "hass", void 0), s([pe({
    type: Boolean
  })], ps.prototype, "useWeather", void 0), s([pe()], ps.prototype, "service", void 0), s([pe()], ps.prototype, "apiKey", void 0), s([pe({
    attribute: !1
  })], ps.prototype, "weatherConfig", void 0), s([ge()], ps.prototype, "_testing", void 0), s([ge()], ps.prototype, "_testResult", void 0), ps = s([he("si-weather-source-config")], ps);
  let gs = class extends Qa(ce) {
    constructor() {
      super(...arguments), this.section = "all", this.isLoading = !0, this._initialLoadDone = !1, this.isSaving = !1, this._weatherConfig = null, this._weatherService = null, this._useWeatherService = !1, this._newApiKey = "", this._weatherSaving = !1, this._coords = null, this._coordsEnabled = !1, this._coordsLat = "", this._coordsLon = "", this._coordsElev = "", this._coordsSaving = !1, this._saveStatus = "idle", this._savedResetTimer = null, this._updateScheduled = !1, this.debouncedSave = (() => {
        let e = null;
        return t => {
          e && clearTimeout(e), e = window.setTimeout(() => {
            this.saveData(t), e = null;
          }, 500);
        };
      })();
    }
    _scheduleUpdate() {
      this._updateScheduled || (this._updateScheduled = !0, requestAnimationFrame(() => {
        this._updateScheduled = !1, this.requestUpdate();
      }));
    }
    hassSubscribe() {
      return this._fetchData().catch(e => {
        console.error("Failed to fetch initial data:", e);
      }), [this.hass.connection.subscribeMessage(() => {
        this._fetchData().catch(e => {
          console.error("Failed to fetch data on config update:", e);
        });
      }, {
        type: we + "_config_updated"
      })];
    }
    async _fetchData() {
      var e;
      if (!this.hass) return;
      const t = !this._initialLoadDone;
      t && (this.isLoading = !0, this._scheduleUpdate());
      try {
        const [t, s, n] = await Promise.all([ja(this.hass), Xa(this.hass), Ja(this.hass)]);
        this.config = t, this._weatherConfig = s, this._useWeatherService = s.use_weather_service, this._weatherService = null !== (e = s.weather_service) && void 0 !== e ? e : ze, this._applyCoordinates(n), this.data = (i = this.config, a = ["calctime", "autocalcenabled", "autoupdateenabled", "autoupdateschedule", "autoupdatefirsttime", "autoupdateinterval", "days_between_irrigation"], i ? Object.entries(i).filter(([e]) => a.includes(e)).reduce((e, [t, i]) => Object.assign(e, {
          [t]: i
        }), {}) : {}), this._initialLoadDone = !0;
      } catch (e) {
        console.error("Error fetching data:", e), Da(this, this.hass, "common.errors.load_failed", e);
      } finally {
        t && (this.isLoading = !1), this._scheduleUpdate();
      }
      var i, a;
    }
    firstUpdated() {
      be().then(() => this._scheduleUpdate()).catch(e => {
        console.error("Failed to load HA form:", e), this._scheduleUpdate();
      });
    }
    render() {
      var e, t;
      return this.hass && this.config && this.data ? this.isLoading ? F`<div class="loading-indicator">
        ${Ca("common.loading-messages.general", this.hass.language)}
      </div>` : F`${this._renderSaveStatus()} ${this._renderCards()}` : F`<div class="loading-indicator">
        ${Ca("common.loading-messages.configuration", null !== (t = null === (e = this.hass) || void 0 === e ? void 0 : e.language) && void 0 !== t ? t : "en")}
      </div>`;
    }
    _renderCards() {
      switch (this.section) {
        case "weather-location":
          return F`
          ${this._renderSection("weather")} ${this._renderWeatherServiceCard()}
          ${this._renderSection("location")} ${this._renderCoordinateCard()}
        `;
        case "when-to-water":
          return F`
          ${this._renderSection("automation")} ${this._renderAutoUpdateCard()}
          ${this._renderAutoCalcCard()} ${this._renderWeatherSkipCard()}
          ${this._renderSection("watering")}
          ${this._renderDaysBetweenIrrigationCard()}
          ${this._renderZoneSequencingCard()}
        `;
        default:
          return F`
          ${this._renderSection("weather")} ${this._renderWeatherServiceCard()}
          ${this._renderWeatherSkipCard()} ${this._renderSection("automation")}
          ${this._renderAutoUpdateCard()} ${this._renderAutoCalcCard()}
          ${this._renderSection("location")} ${this._renderCoordinateCard()}
          ${this._renderSection("watering")}
          ${this._renderDaysBetweenIrrigationCard()}
          ${this._renderZoneSequencingCard()}
        `;
      }
    }
    _renderSection(e) {
      return this.hass ? F`
      <div class="settings-section-header">
        ${Ca(`panels.general.sections.${e}`, this.hass.language)}
      </div>
    ` : F``;
    }
    async _saveWeatherConfig() {
      if (this.hass) {
        this._weatherSaving = !0, this._scheduleUpdate();
        try {
          await Ya(this.hass, this._useWeatherService, this._useWeatherService ? this._weatherService : null, this._newApiKey || null), this._newApiKey = "", await this._fetchData();
        } catch (e) {
          console.error("Failed to save weather config:", e), Da(this, this.hass, "common.errors.save_failed", e);
        } finally {
          this._weatherSaving = !1, this._scheduleUpdate();
        }
      }
    }
    _renderWeatherServiceCard() {
      var e;
      return this.hass ? F`
      <ha-card
        header="${Ca("weather_service_config.title", this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ca("weather_service_config.description", this.hass.language)}
        </div>
        <div class="card-content">
          <si-weather-source-config
            .hass="${this.hass}"
            .useWeather="${this._useWeatherService}"
            .service="${null !== (e = this._weatherService) && void 0 !== e ? e : ze}"
            .apiKey="${this._newApiKey}"
            .weatherConfig="${this._weatherConfig}"
            @useweather-changed="${e => {
        this._useWeatherService = e.detail.value;
      }}"
            @service-changed="${e => {
        this._weatherService = e.detail.value;
      }}"
            @apikey-changed="${e => {
        this._newApiKey = e.detail.value;
      }}"
          ></si-weather-source-config>
          <div style="margin-top: 12px;">
            <button
              class="action-btn"
              raised
              ?disabled="${this._weatherSaving}"
              @click="${this._saveWeatherConfig}"
            >
              ${this._weatherSaving ? Ca("common.saving-messages.saving", this.hass.language) : Ca("weather_service_config.save_button", this.hass.language)}
            </button>
          </div>
        </div>
      </ha-card>
    ` : F``;
    }
    _renderAutoUpdateCard() {
      var e, t;
      return this.hass && this.config && this.data ? F`
      <ha-card
        header="${Ca("panels.general.cards.automatic-update.header", this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ca("panels.general.cards.automatic-update.description", this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Ca("panels.general.cards.automatic-update.labels.auto-update-enabled", this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.autoupdateenabled}"
              @change="${e => this.handleConfigChange({
        autoupdateenabled: e.target.checked
      })}"
            ></ha-switch>
          </div>
          ${this.data.autoupdateenabled ? F`
                <div class="setting-row">
                  <label>
                    ${Ca("panels.general.cards.automatic-update.labels.auto-update-interval", this.hass.language)}
                  </label>
                  <div class="inline-row">
                    <input
                      type="number"
                      class="settings-input shortfield"
                      min="1"
                      step="1"
                      inputmode="numeric"
                      .value="${null !== (e = this.data.autoupdateinterval) && void 0 !== e ? e : 1}"
                      @input="${e => {
        const t = parseInt(e.target.value);
        isNaN(t) || this.handleConfigChange({
          autoupdateinterval: t
        });
      }}"
                    />
                    <select
                      class="settings-input"
                      .value="${hs(this.data.autoupdateschedule || Ae)}"
                      @change="${e => this.handleConfigChange({
        autoupdateschedule: e.target.value
      })}"
                    >
                      <option
                        value="${Ee}"
                        ?selected="${(this.data.autoupdateschedule || Ae) === Ee}"
                      >
                        ${Ca("panels.general.cards.automatic-update.options.minutes", this.hass.language)}
                      </option>
                      <option
                        value="${Ae}"
                        ?selected="${(this.data.autoupdateschedule || Ae) === Ae}"
                      >
                        ${Ca("panels.general.cards.automatic-update.options.hours", this.hass.language)}
                      </option>
                      <option
                        value="${Te}"
                        ?selected="${this.data.autoupdateschedule === Te}"
                      >
                        ${Ca("panels.general.cards.automatic-update.options.days", this.hass.language)}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="setting-row">
                  <label>
                    ${Ca("panels.general.cards.automatic-update.labels.auto-update-delay", this.hass.language)}
                    (s)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="1"
                    inputmode="numeric"
                    .value="${null !== (t = this.config.autoupdatedelay) && void 0 !== t ? t : 0}"
                    @input="${e => {
        const t = parseInt(e.target.value);
        isNaN(t) || this.handleConfigChange({
          autoupdatedelay: t
        });
      }}"
                  />
                </div>
              ` : ""}
        </div>
      </ha-card>
    ` : F``;
    }
    _renderAutoCalcCard() {
      return this.hass && this.config && this.data ? F`
      <ha-card
        header="${Ca("panels.general.cards.automatic-duration-calculation.header", this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ca("panels.general.cards.automatic-duration-calculation.description", this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Ca("panels.general.cards.automatic-duration-calculation.labels.auto-calc-enabled", this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.autocalcenabled}"
              @change="${e => this.handleConfigChange({
        autocalcenabled: e.target.checked
      })}"
            ></ha-switch>
          </div>
          ${this.data.autocalcenabled ? F`
                <div class="setting-row">
                  <label>
                    ${Ca("panels.general.cards.automatic-duration-calculation.labels.calc-time", this.hass.language)}
                  </label>
                  <input
                    type="text"
                    class="settings-input shortfield"
                    .value="${this.config.calctime}"
                    @input="${e => this.handleConfigChange({
        calctime: e.target.value
      })}"
                  />
                </div>
              ` : ""}
        </div>
      </ha-card>
    ` : F``;
    }
    _renderWeatherSkipCard() {
      var e, t, i, a;
      return this.hass && this.config && this.data ? F`
      <ha-card header="${Ca("weather_skip.title", this.hass.language)}">
        <div class="card-content description-text">
          ${Ca("weather_skip.description", this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Ca("weather_skip.threshold_label", this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_irrigation_on_precipitation}"
              @change="${e => this.handleConfigChange({
        skip_irrigation_on_precipitation: e.target.checked
      })}"
            ></ha-switch>
          </div>
          ${this.config.skip_irrigation_on_precipitation ? F`
                <div class="setting-row">
                  <label>
                    ${Ca("weather_skip.threshold_label", this.hass.language)}
                    (${La(this.config, xe)})
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="0.1"
                    inputmode="decimal"
                    .value="${null !== (e = this.config.precipitation_threshold_mm) && void 0 !== e ? e : 2}"
                    @input="${e => {
        const t = parseFloat(e.target.value);
        isNaN(t) || this.handleConfigChange({
          precipitation_threshold_mm: t
        });
      }}"
                  />
                </div>
                <div class="setting-row">
                  <label>
                    ${Ca("weather_skip.lookahead_label", this.hass.language)}
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="1"
                    max="5"
                    step="1"
                    inputmode="numeric"
                    .value="${null !== (t = this.config.precipitation_forecast_days) && void 0 !== t ? t : 1}"
                    @input="${e => {
        const t = parseInt(e.target.value, 10);
        !isNaN(t) && t >= 1 && this.handleConfigChange({
          precipitation_forecast_days: t
        });
      }}"
                  />
                </div>
                <div class="description-text">
                  ${Ca("weather_skip.lookahead_help", this.hass.language)}
                </div>
              ` : ""}

          <div class="section-divider">
            ${Ca("weather_skip.temp_section_title", this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Ca("weather_skip.temp_section_title", this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_on_temp_enabled}"
              @change="${e => this.handleConfigChange({
        skip_on_temp_enabled: e.target.checked
      })}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_temp_enabled ? F`
                <div class="setting-row">
                  <label>
                    ${Ca("weather_skip.temp_threshold_label", this.hass.language)}
                    (°C)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.5"
                    .value="${null !== (i = this.config.temp_threshold) && void 0 !== i ? i : 5}"
                    @input="${e => {
        const t = parseFloat(e.target.value);
        isNaN(t) || this.handleConfigChange({
          temp_threshold: t
        });
      }}"
                  />
                </div>
              ` : ""}

          <div class="section-divider">
            ${Ca("weather_skip.wind_section_title", this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Ca("weather_skip.wind_section_title", this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_on_wind_enabled}"
              @change="${e => this.handleConfigChange({
        skip_on_wind_enabled: e.target.checked
      })}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_wind_enabled ? F`
                <div class="setting-row">
                  <label>
                    ${Ca("weather_skip.wind_threshold_label", this.hass.language)}
                    (m/s)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="0.1"
                    inputmode="decimal"
                    .value="${null !== (a = this.config.wind_threshold) && void 0 !== a ? a : 6.9}"
                    @input="${e => {
        const t = parseFloat(e.target.value);
        isNaN(t) || this.handleConfigChange({
          wind_threshold: t
        });
      }}"
                  />
                </div>
              ` : ""}

          <div class="section-divider">
            ${Ca("weather_skip.rain_sensor_section_title", this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Ca("weather_skip.rain_sensor_label", this.hass.language)}
            </label>
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${this.config.rain_sensor || ""}"
              .includeDomains="${["binary_sensor"]}"
              allow-custom-entity
              @value-changed="${e => this.handleConfigChange({
        rain_sensor: e.detail.value || null
      })}"
            ></ha-entity-picker>
          </div>
        </div>
      </ha-card>
    ` : F``;
    }
    _applyCoordinates(e) {
      this._coords = e, this._coordsEnabled = e.manual_coordinates_enabled;
      const t = (e, t) => null != e ? String(e) : null != t ? String(t) : "";
      this._coordsLat = t(e.manual_latitude, e.ha_latitude), this._coordsLon = t(e.manual_longitude, e.ha_longitude), this._coordsElev = t(e.manual_elevation, e.ha_elevation);
    }
    async _saveCoordinates() {
      if (this.hass) {
        this._coordsSaving = !0, this._scheduleUpdate();
        try {
          await (e = this.hass, t = this._coordsEnabled, i = this._coordsEnabled ? parseFloat(this._coordsLat) : null, a = this._coordsEnabled ? parseFloat(this._coordsLon) : null, s = this._coordsEnabled ? parseFloat(this._coordsElev) : null, e.callWS({
            type: we + "/coordinates_save",
            manual_coordinates_enabled: t,
            manual_latitude: null != i ? i : null,
            manual_longitude: null != a ? a : null,
            manual_elevation: null != s ? s : null
          })), this._applyCoordinates(await Ja(this.hass));
        } catch (e) {
          console.error("Failed to save coordinates:", e), Da(this, this.hass, "common.errors.save_failed", e);
        } finally {
          this._coordsSaving = !1, this._scheduleUpdate();
        }
        var e, t, i, a, s;
      }
    }
    _renderCoordinateCard() {
      var e, t, i;
      if (!this.hass || !this._coords) return F``;
      const a = this._coords;
      return F`
      <ha-card
        header="${Ca("coordinate_config.title", this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ca("coordinate_config.description", this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Ca("coordinate_config.manual_enabled", this.hass.language)}
            </label>
            <ha-switch
              .checked="${this._coordsEnabled}"
              @change="${e => {
        this._coordsEnabled = e.target.checked;
      }}"
            ></ha-switch>
          </div>
          ${this._coordsEnabled ? F`
                <div class="setting-row">
                  <label>
                    ${Ca("coordinate_config.latitude", this.hass.language)}
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="-90"
                    max="90"
                    step="0.000001"
                    inputmode="decimal"
                    .value="${this._coordsLat}"
                    @input="${e => {
        this._coordsLat = e.target.value;
      }}"
                  />
                </div>
                <div class="setting-row">
                  <label>
                    ${Ca("coordinate_config.longitude", this.hass.language)}
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="-180"
                    max="180"
                    step="0.000001"
                    inputmode="decimal"
                    .value="${this._coordsLon}"
                    @input="${e => {
        this._coordsLon = e.target.value;
      }}"
                  />
                </div>
                <div class="setting-row">
                  <label>
                    ${Ca("coordinate_config.elevation", this.hass.language)}
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="-1000"
                    max="9000"
                    step="1"
                    inputmode="numeric"
                    .value="${this._coordsElev}"
                    @input="${e => {
        this._coordsElev = e.target.value;
      }}"
                  />
                </div>
              ` : F`
                <div
                  class="card-content"
                  style="color: var(--secondary-text-color); font-style: italic;"
                >
                  ${Ca("coordinate_config.current_ha_coords", this.hass.language)}:
                  ${Ca("coordinate_config.latitude", this.hass.language)}:
                  ${null !== (e = a.ha_latitude) && void 0 !== e ? e : 0},
                  ${Ca("coordinate_config.longitude", this.hass.language)}:
                  ${null !== (t = a.ha_longitude) && void 0 !== t ? t : 0},
                  ${Ca("coordinate_config.elevation", this.hass.language)}:
                  ${null !== (i = a.ha_elevation) && void 0 !== i ? i : 0}m
                </div>
              `}
          <div style="margin-top: 12px;">
            <button
              class="action-btn"
              raised
              ?disabled="${this._coordsSaving}"
              @click="${this._saveCoordinates}"
            >
              ${this._coordsSaving ? Ca("common.saving-messages.saving", this.hass.language) : Ca("common.actions.save", this.hass.language)}
            </button>
          </div>
        </div>
      </ha-card>
    `;
    }
    _renderDaysBetweenIrrigationCard() {
      var e;
      return this.hass && this.config && this.data ? F`
      <ha-card
        header="${Ca("days_between_irrigation.title", this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ca("days_between_irrigation.description", this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Ca("days_between_irrigation.label", this.hass.language)}
              <div class="setting-description">
                ${Ca("days_between_irrigation.help_text", this.hass.language)}
              </div>
            </label>
            <input
              type="number"
              class="settings-input shortfield"
              min="0"
              max="365"
              step="1"
              inputmode="numeric"
              .value="${null !== (e = this.config.days_between_irrigation) && void 0 !== e ? e : 0}"
              @input="${e => {
        const t = e.target.valueAsNumber;
        isNaN(t) || this.handleConfigChange({
          days_between_irrigation: Math.round(t)
        });
      }}"
            />
          </div>
        </div>
      </ha-card>
    ` : F``;
    }
    _renderZoneSequencingCard() {
      var e, t;
      if (!this.hass || !this.config || !this.data) return F``;
      const i = (this.config.zone_sequencing || At) === Tt;
      return F`
      <ha-card
        header="${Ca("zone_sequencing.title", this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ca("zone_sequencing.description", this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Ca("zone_sequencing.title", this.hass.language)}
            </label>
            <select
              class="settings-input"
              .value="${hs(this.config.zone_sequencing || At)}"
              @change="${e => this.handleConfigChange({
        [zt]: e.target.value
      })}"
            >
              <option
                value="${At}"
                ?selected="${(this.config.zone_sequencing || At) === At}"
              >
                ${Ca("zone_sequencing.parallel", this.hass.language)}
              </option>
              <option
                value="${Et}"
                ?selected="${this.config.zone_sequencing === Et}"
              >
                ${Ca("zone_sequencing.sequential", this.hass.language)}
              </option>
              <option
                value="${Tt}"
                ?selected="${this.config.zone_sequencing === Tt}"
              >
                ${Ca("zone_sequencing.rotating", this.hass.language)}
              </option>
            </select>
          </div>
          ${i ? F`
                <div class="setting-row">
                  <label>
                    ${Ca("zone_sequencing.max_consecutive_duration_label", this.hass.language)}
                  </label>
                  <input
                    type="number"
                    min="1"
                    class="settings-input"
                    .value="${hs(null !== (e = this.config.zone_sequencing_max_consecutive_duration) && void 0 !== e ? e : 5)}"
                    @change="${e => this.handleConfigChange({
        [Ct]: parseInt(e.target.value, 10) || 5
      })}"
                  />
                  <span class="unit-label">
                    ${Ca("zone_sequencing.max_consecutive_duration_unit", this.hass.language)}
                  </span>
                </div>
                <div class="setting-row">
                  <label>
                    ${Ca("zone_sequencing.min_absorption_time_label", this.hass.language)}
                  </label>
                  <input
                    type="number"
                    min="0"
                    class="settings-input"
                    .value="${hs(null !== (t = this.config.zone_sequencing_min_absorption_time) && void 0 !== t ? t : 0)}"
                    @change="${e => this.handleConfigChange({
        [Ot]: parseInt(e.target.value, 10) || 0
      })}"
                  />
                  <span class="unit-label">
                    ${Ca("zone_sequencing.min_absorption_time_unit", this.hass.language)}
                  </span>
                </div>
              ` : ""}
        </div>
      </ha-card>
    `;
    }
    async saveData(e) {
      if (this.hass && this.data) {
        this.isSaving = !0, this._saveStatus = "saving", this._scheduleUpdate();
        try {
          this.data = Object.assign(Object.assign({}, this.data), e), this._scheduleUpdate(), await (t = this.hass, i = this.data, t.callApi("POST", we + "/config", i)), this._markSaved();
        } catch (e) {
          console.error("Error saving config:", e), this._saveStatus = "idle", Da(this, this.hass, "common.errors.save_failed", e), await this._fetchData();
        } finally {
          this.isSaving = !1, this._scheduleUpdate();
        }
        var t, i;
      }
    }
    _markSaved() {
      this._saveStatus = "saved", this._savedResetTimer && clearTimeout(this._savedResetTimer), this._savedResetTimer = window.setTimeout(() => {
        this._saveStatus = "idle", this._scheduleUpdate();
      }, 2e3);
    }
    _renderSaveStatus() {
      if (!this.hass || "idle" === this._saveStatus) return F``;
      const e = "saving" === this._saveStatus;
      return F`
      <div class="save-status-float ${this._saveStatus}">
        <ha-icon
          icon="${e ? "mdi:content-save-outline" : "mdi:check-circle"}"
        ></ha-icon>
        ${Ca(e ? "common.saving-messages.saving" : "panels.zones.status.saved", this.hass.language)}
      </div>
    `;
    }
    handleConfigChange(e) {
      this.debouncedSave(e);
    }
    disconnectedCallback() {
      super.disconnectedCallback(), this._savedResetTimer && (clearTimeout(this._savedResetTimer), this._savedResetTimer = null);
    }
    static get styles() {
      return h`
      ${ss}

      /* Floating auto-save status chip (UX H3) */
      .save-status-float {
        position: sticky;
        top: 8px;
        z-index: 2;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin: 0 0 8px auto;
        width: fit-content;
        padding: 4px 10px;
        border-radius: 14px;
        background: var(--card-background-color);
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
        font-size: 0.8125rem;
        font-weight: 500;
      }

      .save-status-float ha-icon {
        --mdc-icon-size: 18px;
      }

      .save-status-float.saving {
        color: var(--secondary-text-color);
      }

      .save-status-float.saved {
        color: var(--success-color, #2e7d32);
      }

      /* Section divider (UX N5) */
      .settings-section-header {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--primary-color);
        margin: 16px 4px 4px;
      }

      .description-text {
        font-size: 0.875rem;
        color: var(--secondary-text-color);
        padding-bottom: 4px;
      }

      .setting-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid var(--divider-color);
        gap: 16px;
      }

      .setting-row:last-child {
        border-bottom: none;
      }

      .setting-row label {
        flex: 1;
        color: var(--primary-text-color);
        font-size: 0.9375rem;
      }

      .setting-description {
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
        margin-top: 2px;
      }

      .inline-row {
        display: flex;
        gap: 8px;
        align-items: center;
      }

      .section-divider {
        padding: 12px 0 4px;
        font-weight: 500;
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
      }

      /* Native input styled to match HA */
      .settings-input {
        background: var(--input-fill-color, var(--secondary-background-color));
        border: 1px solid var(--input-ink-color, var(--secondary-text-color));
        border-radius: 4px;
        color: var(--primary-text-color);
        padding: 6px 10px;
        font-family: var(
          --mdc-typography-body1-font-family,
          Roboto,
          sans-serif
        );
        font-size: 0.9375rem;
        box-sizing: border-box;
        height: 36px;
      }

      .settings-input:focus {
        border-color: var(--primary-color);
        outline: none;
      }

      .settings-input.shortfield {
        width: 110px;
      }

      select.settings-input {
        cursor: pointer;
        min-width: 140px;
      }

      /* API key test UI */
      .api-key-status {
        margin-bottom: 4px;
      }

      .api-key-badge {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 10px;
      }

      .api-key-badge.configured {
        background: rgba(76, 175, 80, 0.15);
        color: #2e7d32;
      }

      .api-key-badge.missing {
        background: rgba(var(--rgb-warning-color, 255, 152, 0), 0.15);
        color: var(--warning-color);
      }

      .api-key-row {
        display: flex;
        gap: 8px;
        align-items: center;
        flex-wrap: wrap;
      }

      .api-key-input {
        flex: 1;
        min-width: 180px;
      }

      .test-btn {
        white-space: nowrap;
        flex-shrink: 0;
      }

      .test-result {
        font-size: 0.83rem;
        font-weight: 500;
        margin-top: 6px;
        padding: 5px 10px;
        border-radius: 4px;
      }

      .test-result.success {
        background: rgba(76, 175, 80, 0.12);
        color: #2e7d32;
      }

      .test-result.error {
        background: rgba(var(--rgb-error-color, 176, 0, 32), 0.1);
        color: var(--error-color, #b00020);
      }
    `;
    }
  };
  s([pe()], gs.prototype, "narrow", void 0), s([pe()], gs.prototype, "path", void 0), s([pe()], gs.prototype, "section", void 0), s([pe()], gs.prototype, "data", void 0), s([pe()], gs.prototype, "config", void 0), s([pe({
    type: Boolean
  })], gs.prototype, "isLoading", void 0), s([pe({
    type: Boolean
  })], gs.prototype, "isSaving", void 0), s([pe()], gs.prototype, "_weatherConfig", void 0), s([pe()], gs.prototype, "_weatherService", void 0), s([pe({
    type: Boolean
  })], gs.prototype, "_useWeatherService", void 0), s([pe()], gs.prototype, "_newApiKey", void 0), s([pe({
    type: Boolean
  })], gs.prototype, "_weatherSaving", void 0), s([ge()], gs.prototype, "_coords", void 0), s([ge()], gs.prototype, "_coordsEnabled", void 0), s([ge()], gs.prototype, "_coordsLat", void 0), s([ge()], gs.prototype, "_coordsLon", void 0), s([ge()], gs.prototype, "_coordsElev", void 0), s([ge()], gs.prototype, "_coordsSaving", void 0), s([ge()], gs.prototype, "_saveStatus", void 0), gs = s([he("smart-irrigation-view-general")], gs);
  const ms = e => 9 * e / 5 + 32;
  function vs(e, t, i) {
    if (null == e || Number.isNaN(e)) return null;
    switch (t) {
      case "temperature":
        return i ? {
          value: e,
          unit: "°C"
        } : {
          value: ms(e),
          unit: "°F"
        };
      case "precipitation":
        return i ? {
          value: e,
          unit: at
        } : {
          value: (n = e, n / 25.4),
          unit: st
        };
      case "windspeed":
        return i ? {
          value: e,
          unit: ot
        } : {
          value: (s = e, 2.2369362920544 * s),
          unit: rt
        };
      case "pressure":
        return i ? {
          value: e,
          unit: "hPa"
        } : {
          value: (a = e, .0295299830714 * a),
          unit: nt
        };
    }
    var a, s, n;
  }
  function fs(e, t, i, a) {
    const s = vs(e, t, i);
    if (!s) return "-";
    const n = null != a ? a : function (e, t) {
      return "pressure" === e ? t ? 0 : 2 : "precipitation" === e ? t ? 1 : 2 : 1;
    }(t, i);
    return `${s.value.toFixed(n)} ${s.unit}`;
  }
  let _s = class extends ce {
    constructor() {
      super(...arguments), this.metric = !0, this.name = "", this.size = "", this.throughput = "", this.linkedEntity = "", this.showEntity = !1;
    }
    _emit(e, t) {
      this.dispatchEvent(new CustomEvent(e, {
        detail: {
          value: t
        },
        bubbles: !0,
        composed: !0
      }));
    }
    render() {
      var e, t;
      const i = null !== (t = null === (e = this.hass) || void 0 === e ? void 0 : e.language) && void 0 !== t ? t : "en",
        a = this.metric ? "m²" : et,
        s = this.metric ? tt : it;
      return F`
      <si-field label="${Ca("panels.zones.labels.name", i)}" required>
        <input
          type="text"
          class="si-input"
          .value="${this.name}"
          @input="${e => this._emit("name-changed", e.target.value)}"
        />
      </si-field>

      <si-field
        label="${Ca("panels.zones.labels.size", i)}"
        unit="${a}"
        help="${Ca("field_help.zone_size", i)}"
      >
        <input
          type="number"
          class="si-input"
          min="0"
          step="0.1"
          inputmode="decimal"
          .value="${this.size}"
          @input="${e => this._emit("size-changed", e.target.value)}"
        />
      </si-field>

      <si-field
        label="${Ca("panels.zones.labels.throughput", i)}"
        unit="${s}"
        help="${Ca("field_help.zone_throughput", i)}"
      >
        <input
          type="number"
          class="si-input"
          min="0"
          step="0.1"
          inputmode="decimal"
          .value="${this.throughput}"
          @input="${e => this._emit("throughput-changed", e.target.value)}"
        />
      </si-field>

      ${this.showEntity ? F`
            <si-field
              label="${Ca("panels.zones.labels.linked_entity", i)}"
              help="${Ca("field_help.zone_linked_entity", i)}"
            >
              <ha-entity-picker
                .hass="${this.hass}"
                .value="${this.linkedEntity}"
                .includeDomains="${["switch", "valve"]}"
                allow-custom-entity
                @value-changed="${e => this._emit("entity-changed", e.detail.value || "")}"
              ></ha-entity-picker>
            </si-field>
          ` : ""}
    `;
    }
    static get styles() {
      return h`
      :host {
        display: block;
      }

      .si-input {
        width: 100%;
        background: var(--input-fill-color, var(--secondary-background-color));
        border: 1px solid var(--input-ink-color, var(--secondary-text-color));
        border-radius: 4px;
        color: var(--primary-text-color);
        padding: 6px 10px;
        font-family: inherit;
        font-size: 0.9375rem;
        box-sizing: border-box;
        height: 36px;
      }

      .si-input:focus {
        border-color: var(--primary-color);
        outline: none;
      }
    `;
    }
  };
  s([pe({
    attribute: !1
  })], _s.prototype, "hass", void 0), s([pe({
    type: Boolean
  })], _s.prototype, "metric", void 0), s([pe()], _s.prototype, "name", void 0), s([pe()], _s.prototype, "size", void 0), s([pe()], _s.prototype, "throughput", void 0), s([pe()], _s.prototype, "linkedEntity", void 0), s([pe({
    type: Boolean
  })], _s.prototype, "showEntity", void 0), _s = s([he("si-zone-form")], _s);
  let bs = class extends Qa(ce) {
    constructor() {
      super(...arguments), this.zones = [], this.modules = [], this.mappings = [], this.wateringCalendars = new Map(), this.isLoading = !0, this._initialLoadDone = !1, this._scrolledToTarget = !1, this.isSaving = !1, this._showAddZone = !1, this._pendingConfirm = null, this._saveStatus = "idle", this._savedResetTimer = null, this._confirmDeleteZoneId = null, this._newZoneName = "", this._newZoneSize = "", this._newZoneThroughput = "", this._updateScheduled = !1, this.globalDebounceTimer = null;
    }
    _scheduleUpdate() {
      this._updateScheduled || (this._updateScheduled = !0, requestAnimationFrame(() => {
        this._updateScheduled = !1, this.requestUpdate();
      }));
    }
    get _targetZoneId() {
      var e, t;
      const i = null === (t = null === (e = this.path) || void 0 === e ? void 0 : e.params) || void 0 === t ? void 0 : t.zone;
      return null != i && "" !== i ? Number(i) : null;
    }
    firstUpdated() {
      be().then(() => this._scheduleUpdate()).catch(e => {
        console.error("Failed to load HA form:", e), this._scheduleUpdate();
      });
    }
    updated() {
      var e;
      if (this._scrolledToTarget || this.isLoading) return;
      const t = this._targetZoneId;
      if (null === t) return;
      const i = null === (e = this.shadowRoot) || void 0 === e ? void 0 : e.querySelector(`#zone-${t}`);
      i && (this._scrolledToTarget = !0, i.scrollIntoView({
        behavior: "smooth",
        block: "start"
      }));
    }
    hassSubscribe() {
      return this._fetchData().catch(e => {
        console.error("Failed to fetch initial data:", e);
      }), [this.hass.connection.subscribeMessage(() => {
        this._fetchData().catch(e => {
          console.error("Failed to fetch data on config update:", e);
        });
      }, {
        type: we + "_config_updated"
      })];
    }
    async _fetchData() {
      if (!this.hass) return;
      const e = !this._initialLoadDone;
      try {
        e && (this.isLoading = !0);
        const [t, i, a, s] = await Promise.all([ja(this.hass), Fa(this.hass), Za(this.hass), Va(this.hass)]);
        this.config = t, this.zones = i, this.modules = a, this.mappings = s, this._initialLoadDone = !0, this._fetchWateringCalendars();
      } catch (e) {
        console.error("Error fetching data:", e), Da(this, this.hass, "common.errors.load_failed", e);
      } finally {
        e && (this.isLoading = !1), this._scheduleUpdate();
      }
    }
    handleResetAllBuckets() {
      var e;
      this.hass && (this.isSaving = !0, this._scheduleUpdate(), (e = this.hass, e.callApi("POST", we + "/zones", {
        reset_all_buckets: !0
      })).catch(e => {
        console.error("Failed to reset all buckets:", e), Da(this, this.hass, "common.errors.action_failed", e);
      }).finally(() => {
        this.isSaving = !1, this._fetchData().catch(e => console.error("fetchData after reset:", e));
      }));
    }
    handleClearAllWeatherdata() {
      var e;
      this.hass && (this.isSaving = !0, this._scheduleUpdate(), (e = this.hass, e.callApi("POST", we + "/zones", {
        clear_all_weatherdata: !0
      })).catch(e => {
        console.error("Failed to clear all weather data:", e), Da(this, this.hass, "common.errors.action_failed", e);
      }).finally(() => {
        this.isSaving = !1, this._fetchData().catch(e => console.error("fetchData after clear-weather:", e));
      }));
    }
    handleAddZone() {
      if (!this._newZoneName.trim()) return;
      const e = {
        name: this._newZoneName.trim(),
        size: Math.round(100 * (parseFloat(this._newZoneSize) || 0)) / 100,
        throughput: Math.round(100 * (parseFloat(this._newZoneThroughput) || 0)) / 100,
        state: ts.Automatic,
        duration: 0,
        bucket: 0,
        module: void 0,
        delta: 0,
        explanation: "",
        multiplier: 1,
        mapping: void 0,
        lead_time: 0,
        maximum_duration: void 0,
        maximum_bucket: void 0,
        drainage_rate: void 0,
        current_drainage: 0
      };
      this.zones = [...this.zones, e], this.isSaving = !0, this._showAddZone = !1, this.saveToHA(e).then(() => (this._newZoneName = "", this._newZoneSize = "", this._newZoneThroughput = "", this._fetchData())).catch(e => {
        console.error("Failed to add zone:", e), this.zones = this.zones.slice(0, -1), Da(this, this.hass, "common.errors.save_failed", e);
      }).finally(() => {
        this.isSaving = !1, this._scheduleUpdate();
      });
    }
    handleEditZone(e, t) {
      this.hass && (this.zones = this.zones.map((i, a) => a === e ? t : i), this.globalDebounceTimer && clearTimeout(this.globalDebounceTimer), this.globalDebounceTimer = window.setTimeout(() => {
        this.isSaving = !0, this._saveStatus = "saving", this.saveToHA(t).then(() => this._markSaved()).catch(e => {
          console.error("Failed to save zone:", e), this._saveStatus = "idle", Da(this, this.hass, "common.errors.save_failed", e);
        }).finally(() => {
          this.isSaving = !1, this._scheduleUpdate();
        }), this.globalDebounceTimer = null;
      }, 500), this._scheduleUpdate());
    }
    handleRemoveZone(e) {
      this._confirmDeleteZoneId = e;
    }
    _confirmDelete() {
      const e = this._confirmDeleteZoneId;
      if (null === e || !this.hass) return;
      const t = this.zones.findIndex(t => t.id === e);
      if (-1 === t) return;
      const i = [...this.zones];
      var a, s;
      this.zones = this.zones.filter(t => t.id !== e), this._confirmDeleteZoneId = null, this.isSaving = !0, (a = this.hass, s = e.toString(), a.callApi("POST", we + "/zones", {
        id: s,
        remove: !0
      })).catch(e => {
        console.error("Failed to delete zone:", e), Da(this, this.hass, "common.errors.delete_failed", e), this.zones = i, this._fetchData().catch(e => console.error("Failed to refresh data after delete error:", e));
      }).finally(() => {
        this.isSaving = !1, this._scheduleUpdate();
      });
    }
    _runPendingConfirm() {
      const e = this._pendingConfirm;
      this._pendingConfirm = null, null == e || e.onConfirm();
    }
    _markSaved() {
      this._saveStatus = "saved", this._savedResetTimer && clearTimeout(this._savedResetTimer), this._savedResetTimer = window.setTimeout(() => {
        this._saveStatus = "idle", this._scheduleUpdate();
      }, 2e3), this._scheduleUpdate();
    }
    _renderSaveStatus() {
      if (!this.hass || "idle" === this._saveStatus) return F``;
      const e = "saving" === this._saveStatus;
      return F`
      <span class="save-status ${this._saveStatus}">
        <ha-icon
          icon="${e ? "mdi:content-save-outline" : "mdi:check-circle"}"
        ></ha-icon>
        ${Ca(e ? "common.saving-messages.saving" : "panels.zones.status.saved", this.hass.language)}
      </span>
    `;
    }
    async _fetchWateringCalendars() {
      if (this.hass) {
        for (const i of this.zones) if (void 0 !== i.id) try {
          const a = await (e = this.hass, t = i.id.toString(), e.callWS({
            type: we + "/watering_calendar",
            zone_id: t
          }));
          this.wateringCalendars.set(i.id, a);
        } catch (e) {
          console.error(`Failed to fetch watering calendar for zone ${i.id}:`, e);
        }
        var e, t;
        this._scheduleUpdate();
      }
    }
    renderWateringCalendar(e) {
      if (!this.hass || "number" != typeof e.id) return F``;
      const t = this.wateringCalendars.get(e.id),
        i = t && e.id in t ? t[e.id] : null,
        a = (null == i ? void 0 : i.monthly_estimates) || [];
      return F`
      <div class="card-content">
        ${0 === a.length ? F`
              <div class="calendar-note">
                ${(null == i ? void 0 : i.error) ? `${Ca("panels.zones.calendar.error_prefix", this.hass.language)} ${i.error}` : Ca("panels.zones.calendar.no_data", this.hass.language)}
              </div>
            ` : F`
              <div class="calendar-table">
                <div class="calendar-header">
                  <span
                    >${Ca("panels.zones.calendar.month", this.hass.language)}</span
                  >
                  <span
                    >${Ca("panels.zones.calendar.et", this.hass.language)}</span
                  >
                  <span
                    >${Ca("panels.zones.calendar.precipitation", this.hass.language)}</span
                  >
                  <span
                    >${Ca("panels.zones.calendar.watering", this.hass.language)}</span
                  >
                  <span
                    >${Ca("panels.zones.calendar.avg_temp", this.hass.language)}</span
                  >
                </div>
                ${a.map(e => {
        var t;
        const i = (null === (t = this.config) || void 0 === t ? void 0 : t.units) !== Ce;
        return F`
                    <div class="calendar-row">
                      <span
                        >${e.month_name || `Month ${e.month}` || "-"}</span
                      >
                      <span
                        >${fs(e.estimated_et_mm, "precipitation", i)}</span
                      >
                      <span
                        >${fs(e.average_precipitation_mm, "precipitation", i)}</span
                      >
                      <span
                        >${function (e, t) {
          return null == e || Number.isNaN(e) ? "-" : t ? `${e.toFixed(0)} L` : `${(e => .264172052 * e)(e).toFixed(1)} gal`;
        }(e.estimated_watering_volume_liters, i)}</span
                      >
                      <span
                        >${fs(e.average_temperature_c, "temperature", i)}</span
                      >
                    </div>
                  `;
      })}
              </div>
              ${(null == i ? void 0 : i.calculation_method) ? F`
                    <div class="calendar-info">
                      ${Ca("panels.zones.calendar.method_prefix", this.hass.language)}
                      ${i.calculation_method}
                    </div>
                  ` : ""}
            `}
      </div>
    `;
    }
    async saveToHA(e) {
      if (!this.hass) throw new Error("Home Assistant connection not available");
      await Wa(this.hass, e);
    }
    _renderModuleOptions(e) {
      if (!this.hass) return F``;
      const t = null != e ? String(e) : "";
      return F`
      <option value="" ?selected="${"" === t}">
        ---${Ca("common.labels.select", this.hass.language)}---
      </option>
      ${this.modules.map(e => F`
          <option value="${e.id}" ?selected="${t === String(e.id)}">
            ${e.id}: ${e.name}
          </option>
        `)}
    `;
    }
    _renderMappingOptions(e) {
      if (!this.hass) return F``;
      const t = null != e ? String(e) : "";
      return F`
      <option value="" ?selected="${"" === t}">
        ---${Ca("common.labels.select", this.hass.language)}---
      </option>
      ${this.mappings.map(e => F`
          <option value="${e.id}" ?selected="${t === String(e.id)}">
            ${e.id}: ${e.name}
          </option>
        `)}
    `;
    }
    renderZone(e, t) {
      var i, a, s, n, r, o;
      if (!this.hass) return F``;
      const l = void 0 !== e.id && e.id === this._targetZoneId;
      return F`
      <ha-card id="zone-${null !== (i = e.id) && void 0 !== i ? i : "new"}">
        <div class="card-header">
          <div class="name">${e.name}</div>
        </div>

        <!-- SETTINGS EXPANSION -->
        <ha-expansion-panel
          ?expanded="${l}"
          .header="${Ca("common.labels.settings", this.hass.language)}"
        >
          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.name", this.hass.language)}</span
            >
            <input
              type="text"
              class="settings-input"
              .value="${e.name}"
              @input="${i => this.handleEditZone(t, Object.assign(Object.assign({}, e), {
        [dt]: i.target.value
      }))}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.size", this.hass.language)}
              (${La(this.config, ht)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat(e.size.toFixed(2))}"
              @input="${i => {
        const a = Math.round(100 * i.target.valueAsNumber) / 100;
        isNaN(a) || this.handleEditZone(t, Object.assign(Object.assign({}, e), {
          [ht]: a
        }));
      }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.throughput", this.hass.language)}
              (${La(this.config, ut)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat(e.throughput.toFixed(2))}"
              @input="${i => {
        const a = Math.round(100 * i.target.valueAsNumber) / 100;
        isNaN(a) || this.handleEditZone(t, Object.assign(Object.assign({}, e), {
          [ut]: a
        }));
      }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.drainage_rate", this.hass.language)}
              (${La(this.config, $t)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat((null !== (a = e.drainage_rate) && void 0 !== a ? a : 0).toFixed(2))}"
              @input="${i => {
        const a = Math.round(100 * i.target.valueAsNumber) / 100;
        isNaN(a) || this.handleEditZone(t, Object.assign(Object.assign({}, e), {
          [$t]: a
        }));
      }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.state", this.hass.language)}</span
            >
            <select
              class="settings-input"
              .value="${hs(e.state)}"
              @change="${i => this.handleEditZone(t, Object.assign(Object.assign({}, e), {
        [pt]: i.target.value,
        [gt]: 0
      }))}"
            >
              <option
                value="${ts.Automatic}"
                ?selected="${e.state === ts.Automatic}"
              >
                ${Ca("panels.zones.labels.states.automatic", this.hass.language)}
              </option>
              <option
                value="${ts.Manual}"
                ?selected="${e.state === ts.Manual}"
              >
                ${Ca("panels.zones.labels.states.manual", this.hass.language)}
              </option>
              <option
                value="${ts.Disabled}"
                ?selected="${e.state === ts.Disabled}"
              >
                ${Ca("panels.zones.labels.states.disabled", this.hass.language)}
              </option>
            </select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("common.labels.module", this.hass.language)}</span
            >
            <select
              class="settings-input"
              .value="${hs(void 0 !== e.module ? String(e.module) : "")}"
              @change="${i => {
        const a = i.target.value;
        this.handleEditZone(t, Object.assign(Object.assign({}, e), {
          [mt]: a ? parseInt(a) : void 0
        }));
      }}"
            >
              ${this._renderModuleOptions(e.module)}
            </select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.mapping", this.hass.language)}</span
            >
            <select
              class="settings-input"
              .value="${hs(void 0 !== e.mapping ? String(e.mapping) : "")}"
              @change="${i => {
        const a = i.target.value;
        this.handleEditZone(t, Object.assign(Object.assign({}, e), {
          [_t]: a ? parseInt(a) : void 0
        }));
      }}"
            >
              ${this._renderMappingOptions(e.mapping)}
            </select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.linked_entity", this.hass.language)}</span
            >
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${e.linked_entity || ""}"
              .includeDomains="${["switch", "valve"]}"
              allow-custom-entity
              @value-changed="${i => this.handleEditZone(t, Object.assign(Object.assign({}, e), {
        [xt]: i.detail.value || void 0
      }))}"
            ></ha-entity-picker>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.flow_sensor", this.hass.language)}</span
            >
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${e.flow_sensor || ""}"
              .includeDomains="${["sensor"]}"
              allow-custom-entity
              @value-changed="${i => this.handleEditZone(t, Object.assign(Object.assign({}, e), {
        [St]: i.detail.value || null
      }))}"
            ></ha-entity-picker>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.bucket", this.hass.language)}
              (${La(this.config, vt)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              inputmode="decimal"
              .value="${parseFloat(Number(e.bucket).toFixed(2))}"
              @input="${i => {
        const a = Math.round(100 * i.target.valueAsNumber) / 100;
        isNaN(a) || this.handleEditZone(t, Object.assign(Object.assign({}, e), {
          [vt]: a
        }));
      }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.maximum-bucket", this.hass.language)}
              (${La(this.config, vt)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat(Number(e.maximum_bucket).toFixed(2))}"
              @input="${i => {
        const a = Math.round(100 * i.target.valueAsNumber) / 100;
        isNaN(a) || this.handleEditZone(t, Object.assign(Object.assign({}, e), {
          [wt]: a
        }));
      }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.multiplier", this.hass.language)}</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat(e.multiplier.toFixed(2))}"
              @input="${i => {
        const a = Math.round(100 * i.target.valueAsNumber) / 100;
        isNaN(a) || this.handleEditZone(t, Object.assign(Object.assign({}, e), {
          [ft]: a
        }));
      }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.lead-time", this.hass.language)}
              (${"s"})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="1"
              min="0"
              inputmode="numeric"
              .value="${null !== (s = e.lead_time) && void 0 !== s ? s : 0}"
              @input="${i => {
        const a = i.target.valueAsNumber;
        isNaN(a) || this.handleEditZone(t, Object.assign(Object.assign({}, e), {
          [bt]: Math.round(a)
        }));
      }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.maximum-duration", this.hass.language)}
              (${"s"})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="1"
              min="0"
              inputmode="numeric"
              .value="${null !== (n = e.maximum_duration) && void 0 !== n ? n : ""}"
              @input="${i => {
        const a = i.target.valueAsNumber;
        isNaN(a) || this.handleEditZone(t, Object.assign(Object.assign({}, e), {
          [yt]: Math.round(a)
        }));
      }}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Ca("panels.zones.labels.bucket_threshold", this.hass.language)}
              (${La(this.config, vt)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.5"
              max="0"
              inputmode="decimal"
              .value="${parseFloat((null !== (r = e.bucket_threshold) && void 0 !== r ? r : 0).toFixed(1))}"
              @input="${i => {
        const a = Math.round(10 * i.target.valueAsNumber) / 10;
        isNaN(a) || this.handleEditZone(t, Object.assign(Object.assign({}, e), {
          [kt]: Math.min(a, 0)
        }));
      }}"
            />
          </ha-settings-row>

          ${e.state === ts.Manual ? F`
                <ha-settings-row>
                  <span slot="heading"
                    >${Ca("panels.zones.labels.duration", this.hass.language)}
                    (${"s"})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="1"
                    min="0"
                    inputmode="numeric"
                    .value="${null !== (o = e.duration) && void 0 !== o ? o : 0}"
                    @input="${i => {
        const a = i.target.valueAsNumber;
        isNaN(a) || this.handleEditZone(t, Object.assign(Object.assign({}, e), {
          [gt]: Math.round(a)
        }));
      }}"
                  />
                </ha-settings-row>
              ` : ""}

          <!-- Danger row -->
          <div class="settings-danger-row">
            <button
              class="action-btn"
              @click="${() => {
        this._pendingConfirm = {
          title: Ca("panels.zones.confirm_action.reset_bucket_title", this.hass.language),
          body: Ca("panels.zones.confirm_action.reset_bucket_body", this.hass.language),
          confirmLabel: Ca("panels.zones.actions.reset-bucket", this.hass.language),
          onConfirm: () => this.handleEditZone(t, Object.assign(Object.assign({}, e), {
            [vt]: 0
          }))
        };
      }}"
              ?disabled="${this.isSaving}"
            >
              ${Ca("panels.zones.actions.reset-bucket", this.hass.language)}
            </button>
            <button
              class="action-btn danger-button"
              @click="${() => this.handleRemoveZone(void 0 !== e.id ? e.id : -1)}"
              ?disabled="${this.isSaving || void 0 === e.id}"
            >
              <ha-icon slot="icon" icon="mdi:delete"></ha-icon>
              ${Ca("common.actions.delete", this.hass.language)}
            </button>
          </div>
        </ha-expansion-panel>

        <!-- EXPLANATION EXPANSION -->
        ${e.explanation && e.explanation.length > 0 ? F`
              <ha-expansion-panel
                .header="${Ca("panels.zones.actions.information", this.hass.language)}"
              >
                <div class="card-content">${Bt(e.explanation)}</div>
              </ha-expansion-panel>
            ` : ""}

        <!-- Weather records now live on the Weather & Location tab (shown per
             sensor group, not repeated per zone). -->

        <!-- CALENDAR EXPANSION -->
        <ha-expansion-panel
          .header="${Ca("panels.zones.actions.view-watering-calendar", this.hass.language)}"
        >
          ${this.renderWateringCalendar(e)}
        </ha-expansion-panel>
      </ha-card>
    `;
    }
    render() {
      var e;
      if (!this.hass) return F``;
      if (this.isLoading) return F`
        <ha-card header="${Ca("panels.zones.title", this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Ca("common.loading-messages.general", this.hass.language)}
            </div>
          </div>
        </ha-card>
      `;
      const t = null !== this._confirmDeleteZoneId ? this.zones.find(e => e.id === this._confirmDeleteZoneId) : null;
      return F`
      <!-- Header: title + save chip + add zone -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${Ca("panels.zones.title", this.hass.language)}
          </div>
          ${this._renderSaveStatus()}
          <ha-icon-button
            .path="${Ra}"
            title="${Ca("panels.zones.cards.add-zone.header", this.hass.language)}"
            @click="${() => {
        this._showAddZone = !0;
      }}"
          ></ha-icon-button>
        </div>
        ${0 === this.zones.length ? F`<div class="card-content">
              <div class="weather-note">
                ${Ca("panels.zones.no_items", this.hass.language)}
              </div>
            </div>` : ""}
      </ha-card>

      <!-- Add Zone dialog -->
      <ha-dialog
        .open="${this._showAddZone}"
        @closed="${() => {
        this._showAddZone = !1;
      }}"
        heading="${Ca("panels.zones.cards.add-zone.header", this.hass.language)}"
      >
        <div class="add-zone-form">
          <si-zone-form
            .hass="${this.hass}"
            .metric="${(null === (e = this.config) || void 0 === e ? void 0 : e.units) === Oe}"
            .name="${this._newZoneName}"
            .size="${this._newZoneSize}"
            .throughput="${this._newZoneThroughput}"
            @name-changed="${e => {
        this._newZoneName = e.detail.value;
      }}"
            @size-changed="${e => {
        this._newZoneSize = e.detail.value;
      }}"
            @throughput-changed="${e => {
        this._newZoneThroughput = e.detail.value;
      }}"
          ></si-zone-form>
        </div>
        <div class="dialog-footer">
          <button
            class="dialog-btn"
            @click="${() => {
        this._showAddZone = !1;
      }}"
          >
            ${Ca("common.actions.cancel", this.hass.language)}
          </button>
          <button
            class="dialog-btn dialog-btn-primary"
            @click="${this.handleAddZone}"
            ?disabled="${!this._newZoneName.trim() || this.isSaving}"
          >
            ${this.isSaving ? Ca("common.saving-messages.adding", this.hass.language) : Ca("panels.zones.cards.add-zone.actions.add", this.hass.language)}
          </button>
        </div>
      </ha-dialog>

      <!-- Delete confirmation dialog -->
      ${t ? F`
            <ha-dialog
              open
              @closed="${() => {
        this._confirmDeleteZoneId = null;
      }}"
              heading="${Ca("common.actions.confirm_delete", this.hass.language)}"
            >
              <p>
                ${Ca("common.actions.confirm_delete_zone", this.hass.language)}
              </p>
              <p><strong>${t.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${() => {
        this._confirmDeleteZoneId = null;
      }}"
                >
                  ${Ca("common.actions.cancel", this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-danger"
                  @click="${this._confirmDelete}"
                >
                  ${Ca("common.actions.delete", this.hass.language)}
                </button>
              </div>
            </ha-dialog>
          ` : ""}

      <!-- Generic destructive-action confirmation dialog -->
      ${this._pendingConfirm ? F`
            <ha-dialog
              open
              @closed="${() => {
        this._pendingConfirm = null;
      }}"
              heading="${this._pendingConfirm.title}"
            >
              <p>${this._pendingConfirm.body}</p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${() => {
        this._pendingConfirm = null;
      }}"
                >
                  ${Ca("common.actions.cancel", this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-danger"
                  @click="${this._runPendingConfirm}"
                >
                  ${this._pendingConfirm.confirmLabel}
                </button>
              </div>
            </ha-dialog>
          ` : ""}

      <!-- Zone cards -->
      ${this.zones.map((e, t) => this.renderZone(e, t))}

      <!-- Maintenance (destructive) -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${Ca("common.labels.bulk_actions", this.hass.language)}
          </div>
        </div>
        <div class="card-content bulk-actions">
          <button
            class="action-btn danger-button"
            @click="${() => {
        this._pendingConfirm = {
          title: Ca("panels.zones.confirm_action.reset_all_buckets_title", this.hass.language),
          body: Ca("panels.zones.confirm_action.reset_all_buckets_body", this.hass.language),
          confirmLabel: Ca("panels.zones.cards.zone-actions.actions.reset-all-buckets", this.hass.language),
          onConfirm: () => this.handleResetAllBuckets()
        };
      }}"
            ?disabled="${this.isSaving}"
          >
            ${Ca("panels.zones.cards.zone-actions.actions.reset-all-buckets", this.hass.language)}
          </button>
          <button
            class="action-btn danger-button"
            @click="${() => {
        this._pendingConfirm = {
          title: Ca("panels.zones.confirm_action.clear_weather_title", this.hass.language),
          body: Ca("panels.zones.confirm_action.clear_weather_body", this.hass.language),
          confirmLabel: Ca("panels.zones.cards.zone-actions.actions.clear-all-weatherdata", this.hass.language),
          onConfirm: () => this.handleClearAllWeatherdata()
        };
      }}"
            ?disabled="${this.isSaving}"
          >
            ${Ca("panels.zones.cards.zone-actions.actions.clear-all-weatherdata", this.hass.language)}
          </button>
        </div>
      </ha-card>
    `;
    }
    disconnectedCallback() {
      super.disconnectedCallback(), this.globalDebounceTimer && (clearTimeout(this.globalDebounceTimer), this.globalDebounceTimer = null), this._savedResetTimer && (clearTimeout(this._savedResetTimer), this._savedResetTimer = null);
    }
    static get styles() {
      return h`
      ${ss}

      ha-settings-row {
        padding: 0 16px;
      }

      ha-expansion-panel {
        border-top: 1px solid var(--divider-color);
      }

      .shortfield {
        width: 120px;
      }

      /* Auto-save status chip */
      .save-status {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-left: auto;
        margin-right: 8px;
        font-size: 0.8125rem;
        font-weight: 500;
      }

      .save-status ha-icon {
        --mdc-icon-size: 18px;
      }

      .save-status.saving {
        color: var(--secondary-text-color);
      }

      .save-status.saved {
        color: var(--success-color, #2e7d32);
      }

      /* Danger row in settings */
      .settings-danger-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 16px;
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
      }

      .danger-button {
        --mdc-theme-primary: var(--error-color);
        color: var(--error-color);
      }

      .action-btn.danger-button {
        color: var(--error-color);
        border-color: var(--error-color);
      }

      /* Native input styled to match HA */
      .settings-input {
        background: var(--input-fill-color, var(--secondary-background-color));
        border: 1px solid var(--input-ink-color, var(--secondary-text-color));
        border-radius: 4px;
        color: var(--primary-text-color);
        padding: 6px 10px;
        font-family: var(
          --mdc-typography-body1-font-family,
          Roboto,
          sans-serif
        );
        font-size: 0.9375rem;
        box-sizing: border-box;
        height: 36px;
      }

      .settings-input:focus {
        border-color: var(--primary-color);
        outline: none;
      }

      .settings-input.shortfield {
        width: 110px;
      }

      select.settings-input {
        cursor: pointer;
        min-width: 140px;
      }

      /* Add zone dialog form */
      .add-zone-form {
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 8px 0;
        min-width: 300px;
      }

      .add-zone-input {
        width: 100%;
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

      /* Bulk actions */
      .bulk-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
    `;
    }
  };
  s([pe()], bs.prototype, "config", void 0), s([pe({
    attribute: !1
  })], bs.prototype, "path", void 0), s([pe({
    type: Array
  })], bs.prototype, "zones", void 0), s([pe({
    type: Array
  })], bs.prototype, "modules", void 0), s([pe({
    type: Array
  })], bs.prototype, "mappings", void 0), s([pe({
    type: Map
  })], bs.prototype, "wateringCalendars", void 0), s([pe({
    type: Boolean
  })], bs.prototype, "isLoading", void 0), s([pe({
    type: Boolean
  })], bs.prototype, "isSaving", void 0), s([pe({
    type: Boolean
  })], bs.prototype, "_showAddZone", void 0), s([ge()], bs.prototype, "_pendingConfirm", void 0), s([ge()], bs.prototype, "_saveStatus", void 0), s([pe()], bs.prototype, "_confirmDeleteZoneId", void 0), s([pe()], bs.prototype, "_newZoneName", void 0), s([pe()], bs.prototype, "_newZoneSize", void 0), s([pe()], bs.prototype, "_newZoneThroughput", void 0), bs = s([he("smart-irrigation-view-zone-settings")], bs);
  let ys = class extends Qa(ce) {
    constructor() {
      super(...arguments), this.zones = [], this.modules = [], this.allmodules = [], this.isLoading = !0, this._initialLoadDone = !1, this.isSaving = !1, this._updateScheduled = !1, this.globalDebounceTimer = null, this.moduleCache = new Map(), this.debouncedSave = (() => {
        let e = null;
        return t => {
          e && clearTimeout(e), e = window.setTimeout(() => {
            this.saveToHA(t), e = null;
          }, 500);
        };
      })();
    }
    _scheduleUpdate() {
      this._updateScheduled || (this._updateScheduled = !0, requestAnimationFrame(() => {
        this._updateScheduled = !1, this.requestUpdate();
      }));
    }
    firstUpdated() {
      be().catch(e => {
        console.error("Failed to load HA form:", e);
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
        type: we + "_config_updated"
      })];
    }
    async _fetchData() {
      if (!this.hass) return;
      const e = !this._initialLoadDone;
      e && (this.isLoading = !0, this._scheduleUpdate());
      try {
        const [e, t, i, a] = await Promise.all([ja(this.hass), Fa(this.hass), Za(this.hass), Ga(this.hass)]);
        this.config = e, this.zones = t, this.modules = i, this.allmodules = a, this._initialLoadDone = !0, this.moduleCache.clear();
      } catch (e) {
        console.error("Error fetching data:", e), Da(this, this.hass, "common.errors.load_failed", e);
      } finally {
        e && (this.isLoading = !1), this._scheduleUpdate();
      }
    }
    async handleAddModule() {
      var e, t;
      if ((null === (t = null === (e = this.moduleInput) || void 0 === e ? void 0 : e.selectedOptions) || void 0 === t ? void 0 : t[0]) && !this.isSaving) {
        this.isSaving = !0, this._scheduleUpdate();
        try {
          const e = this.moduleInput.selectedOptions[0].text,
            t = this.allmodules.find(t => t.name === e);
          if (!t) return;
          const i = {
            name: e,
            description: t.description,
            config: t.config,
            schema: t.schema
          };
          this.modules = [...this.modules, i], this.moduleCache.clear(), this._scheduleUpdate(), await this.saveToHA(i), await this._fetchData();
        } catch (e) {
          console.error("Error adding module:", e), await this._fetchData();
        } finally {
          this.isSaving = !1, this._scheduleUpdate();
        }
      }
    }
    async handleRemoveModule(e, t) {
      if (!this.isSaving) {
        this.isSaving = !0, this._scheduleUpdate();
        try {
          const e = this.modules[t],
            s = null == e ? void 0 : e.id;
          this.modules;
          this.modules = this.modules.filter((e, i) => i !== t), this.moduleCache.clear(), this._scheduleUpdate(), this.hass && void 0 !== s && (await (i = this.hass, a = s.toString(), i.callApi("POST", we + "/modules", {
            id: a,
            remove: !0
          })));
        } catch (e) {
          console.error("Error removing module:", e), Da(this, this.hass, "common.errors.delete_failed", e), await this._fetchData();
        } finally {
          this.isSaving = !1, this._scheduleUpdate();
        }
        var i, a;
      }
    }
    async saveToHA(e) {
      if (this.hass) try {
        await qa(this.hass, e);
      } catch (e) {
        throw console.error("Error saving module:", e), Da(this, this.hass, "common.errors.save_failed", e), e;
      }
    }
    renderModule(e, t) {
      if (!this.hass) return F``;
      const i = `module-${e.id || t}-${JSON.stringify(e)}`;
      if (this.moduleCache.has(i)) return this.moduleCache.get(i);
      const a = this.zones.filter(t => t.module === e.id).length,
        s = F`
      <ha-card header="${e.id}: ${e.name}">
        <div class="card-content">
          <div class="moduledescription${t}">${e.description}</div>
          <div class="moduleconfig">
            <label class="subheader"
              >${Ca("panels.modules.cards.module.labels.configuration", this.hass.language)}
              (*
              ${Ca("panels.modules.cards.module.labels.required", this.hass.language)})</label
            >
            ${e.schema ? Object.entries(e.schema).map(([e]) => this.renderConfig(t, e)) : null}
          </div>
          ${a ? F`<div class="weather-note">
                ${Ca("panels.modules.cards.module.errors.cannot-delete-module-because-zones-use-it", this.hass.language)}
              </div>` : F` <div
                class="action-button"
                @click="${e => this.handleRemoveModule(e, t)}"
              >
                <svg style="width:24px;height:24px" viewBox="0 0 24 24">
                  <path fill="#404040" d="${Ua}" />
                </svg>
                <span class="action-button-label">
                  ${Ca("common.actions.delete", this.hass.language)}
                </span>
              </div>`}
        </div>
      </ha-card>
    `;
      return this.moduleCache.set(i, s), s;
    }
    renderConfig(e, t) {
      const i = Object.values(this.modules).at(e);
      if (!i || !this.hass) return;
      const a = i.schema[t],
        s = a.name,
        n = function (e) {
          if (e) return (e = e.replace("_", " ")).charAt(0).toUpperCase() + e.slice(1);
        }(s);
      let r = "";
      null == i.config && (i.config = []), s in i.config && (r = i.config[s]);
      let o = F`<label for="${s + e}"
      >${n} </label
    `;
      if ("boolean" == a.type) o = F`${o}<input
          type="checkbox"
          id="${s + e}"
          .checked=${r}
          @input="${t => this.handleEditConfig(e, Object.assign(Object.assign({}, i), {
        config: Object.assign(Object.assign({}, i.config), {
          [s]: t.target.checked
        })
      }))}"
        />`;else if ("float" == a.type || "integer" == a.type) o = F`${o}<input
          type="number"
          class="shortinput"
          id="${a.name + e}"
          .value="${i.config[a.name]}"
          @input="${t => this.handleEditConfig(e, Object.assign(Object.assign({}, i), {
        config: Object.assign(Object.assign({}, i.config), {
          [s]: t.target.value
        })
      }))}"
        />`;else if ("string" == a.type) o = F`${o}<input
          type="text"
          id="${s + e}"
          .value="${r}"
          @input="${t => this.handleEditConfig(e, Object.assign(Object.assign({}, i), {
        config: Object.assign(Object.assign({}, i.config), {
          [s]: t.target.value
        })
      }))}"
        />`;else if ("select" == a.type) {
        const t = this.hass.language;
        o = F`${o}<select
          id="${s + e}"
          .value="${hs(r)}"
          @change="${t => this.handleEditConfig(e, Object.assign(Object.assign({}, i), {
          config: Object.assign(Object.assign({}, i.config), {
            [s]: t.target.value
          })
        }))}"
        >
          ${Object.entries(a.options).map(([e, i]) => F`<option
                value="${Ha(i, 0)}"
                ?selected="${r === Ha(i, 0)}"
              >
                ${Ca("panels.modules.cards.module.translated-options." + Ha(i, 1), t)}
              </option>`)}
        </select>`;
      }
      a.required && (o = F`${o}`);
      const l = a.description ? F`<div class="field-hint">${a.description}</div>` : F``;
      return o = F`<div class="schemaline">${o}${l}</div>`, o;
    }
    handleEditConfig(e, t) {
      this.modules = Object.values(this.modules).map((i, a) => a === e ? t : i), this.moduleCache.clear(), this._scheduleUpdate(), this.debouncedSave(t);
    }
    renderOption(e, t) {
      return this.hass ? F`<option value="${e}>${t}</option>` : F``;
    }
    render() {
      return this.hass ? F`
      <ha-card header="${Ca("panels.modules.title", this.hass.language)}">
        <div class="card-content">
          ${Ca("panels.modules.description", this.hass.language)}
        </div>
      </ha-card>

      <ha-card
        header="${Ca("panels.modules.cards.add-module.header", this.hass.language)}"
      >
        <div class="card-content">
          ${this.isLoading ? F`<div class="loading-indicator">
                ${Ca("common.loading-messages.general", this.hass.language)}
              </div>` : F`
                <div class="zoneline">
                  <label for="moduleInput"
                    >${Ca("common.labels.module", this.hass.language)}:</label
                  >
                  <select id="moduleInput" ?disabled="${this.isSaving}">
                    ${Object.entries(this.allmodules).map(([e, t]) => F`<option value="${t.id}">
                          ${t.name}
                        </option>`)}
                  </select>
                </div>
                <div class="zoneline">
                  <span></span>
                  <button
                    @click="${this.handleAddModule}"
                    ?disabled="${this.isSaving}"
                    class="${this.isSaving ? "saving" : ""}"
                  >
                    ${this.isSaving ? Ca("common.saving-messages.adding", this.hass.language) : Ca("panels.modules.cards.add-module.actions.add", this.hass.language)}
                  </button>
                </div>
              `}
        </div>
      </ha-card>

      ${this.isLoading ? F`<div class="loading-indicator">
            ${Ca("common.loading-messages.modules", this.hass.language)}
          </div>` : Object.entries(this.modules).map(([e, t]) => this.renderModule(t, parseInt(e)))}
    ` : F``;
    }
    disconnectedCallback() {
      super.disconnectedCallback(), this.globalDebounceTimer && (clearTimeout(this.globalDebounceTimer), this.globalDebounceTimer = null), this.moduleCache.clear();
    }
    static get styles() {
      return h`
      ${ss}

      .field-hint {
        font-size: 0.8rem;
        color: var(--secondary-text-color);
        line-height: 1.4;
        margin-top: 3px;
        padding-left: 2px;
      }
    `;
    }
  };
  s([pe()], ys.prototype, "config", void 0), s([pe({
    type: Array
  })], ys.prototype, "zones", void 0), s([pe({
    type: Array
  })], ys.prototype, "modules", void 0), s([pe({
    type: Array
  })], ys.prototype, "allmodules", void 0), s([pe({
    type: Boolean
  })], ys.prototype, "isLoading", void 0), s([pe({
    type: Boolean
  })], ys.prototype, "isSaving", void 0), s([me("#moduleInput")], ys.prototype, "moduleInput", void 0), ys = s([he("smart-irrigation-view-modules")], ys);
  let ws = class extends Qa(ce) {
    constructor() {
      super(...arguments), this.zones = [], this.mappings = [], this.isLoading = !0, this._initialLoadDone = !1, this.isSaving = !1, this.debounceTimers = new Map(), this.globalDebounceTimer = null, this.mappingCache = new Map(), this._updateScheduled = !1, this._lastUpdateTime = 0, this._updateThrottleDelay = 16;
    }
    _scheduleUpdate() {
      if (this._updateScheduled) return;
      const e = performance.now() - this._lastUpdateTime;
      e < this._updateThrottleDelay ? setTimeout(() => {
        this._updateScheduled = !1, this._lastUpdateTime = performance.now(), this.requestUpdate();
      }, this._updateThrottleDelay - e) : (this._updateScheduled = !0, requestAnimationFrame(() => {
        this._updateScheduled = !1, this._lastUpdateTime = performance.now(), this.requestUpdate();
      }));
    }
    firstUpdated() {
      be().catch(e => {
        console.error("Failed to load HA form:", e);
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
        type: we + "_config_updated"
      })];
    }
    async _fetchData() {
      if (!this.hass) return;
      const e = !this._initialLoadDone;
      try {
        e && (this.isLoading = !0);
        const [t, i, a] = await Promise.all([ja(this.hass), Fa(this.hass), Va(this.hass)]);
        this.config = t, this.zones = i, this.mappings = a, this._initialLoadDone = !0, this.mappingCache.clear();
      } catch (e) {
        console.error("Error fetching data:", e), Da(this, this.hass, "common.errors.load_failed", e);
      } finally {
        e && (this.isLoading = !1), this._scheduleUpdate();
      }
    }
    handleAddMapping() {
      if (!this.mappingNameInput.value.trim()) return;
      const e = {
          [He]: "",
          [Le]: "",
          [Me]: "",
          [Ne]: "",
          [Ie]: "",
          [Pe]: "",
          [De]: "",
          [Be]: "",
          [Ue]: ""
        },
        t = {
          name: this.mappingNameInput.value.trim(),
          mappings: e
        };
      this.mappings = [...this.mappings, t], this.isSaving = !0, this.saveToHA(t).then(() => (this.mappingNameInput.value = "", this._fetchData())).catch(e => {
        console.error("Failed to add mapping:", e), Da(this, this.hass, "common.errors.save_failed", e), this.mappings = this.mappings.slice(0, -1);
      }).finally(() => {
        this.isSaving = !1, this._scheduleUpdate();
      });
    }
    handleRemoveMapping(e, t) {
      const i = this.mappings[t].id;
      if (null == i) return;
      const a = [...this.mappings];
      var s, n;
      (this.mappings = this.mappings.filter((e, i) => i !== t), this.mappingCache.delete(i.toString()), this.hass) && (this.isSaving = !0, (s = this.hass, n = i.toString(), s.callApi("POST", we + "/mappings", {
        id: n,
        remove: !0
      })).catch(e => {
        console.error("Failed to delete mapping:", e), Da(this, this.hass, "common.errors.delete_failed", e), this.mappings = a, this._fetchData().catch(e => {
          console.error("Failed to refresh data after delete error:", e);
        });
      }).finally(() => {
        this.isSaving = !1, this._scheduleUpdate();
      }));
    }
    handleEditMapping(e, t) {
      this.mappings[e] = t, t.id && this.mappingCache.delete(t.id.toString()), this.globalDebounceTimer && clearTimeout(this.globalDebounceTimer), this.globalDebounceTimer = window.setTimeout(() => {
        this.isSaving = !0, this.saveToHA(t).catch(e => {
          console.error("Failed to save mapping:", e), Da(this, this.hass, "common.errors.save_failed", e);
        }).finally(() => {
          this.isSaving = !1, this._scheduleUpdate();
        }), this.globalDebounceTimer = null;
      }, 500), this._scheduleUpdate();
    }
    async saveToHA(e) {
      var t;
      if (!this.hass) throw new Error("Home Assistant connection not available");
      const i = [],
        a = this.hass.states;
      for (const t in e.mappings) {
        const s = e.mappings[t].sensorentity;
        if (s && "" !== s.trim()) {
          const n = s.trim();
          e.mappings[t].sensorentity = n, n in a || i.push(n);
        }
      }
      if (i.length > 0) {
        const e = null === (t = this.shadowRoot) || void 0 === t ? void 0 : t.querySelector("ha-card");
        throw e && Ma({
          body: {
            message: Ca("panels.mappings.cards.mapping.errors.source_does_not_exist", this.hass.language) + ": " + i.join(", ")
          },
          error: Ca("panels.mappings.cards.mapping.errors.invalid_source", this.hass.language)
        }, e), new Error("Invalid sensor entities found");
      }
      const {
        id: s,
        name: n,
        mappings: r
      } = e;
      await Ka(this.hass, {
        id: s,
        name: n,
        mappings: r
      });
    }
    renderMapping(e, t) {
      if (!this.hass) return F``;
      const i = `${e.id}_${JSON.stringify(e).slice(0, 100)}`;
      if (this.mappingCache.has(i)) return this.mappingCache.get(i);
      const a = this.zones.filter(t => t.mapping === e.id).length,
        s = F`
      <ha-card header="${e.id}: ${e.name}">
        <div class="card-content">
          <div class="card-content">
            <label for="name${e.id}"
              >${Ca("panels.mappings.labels.mapping-name", this.hass.language)}:</label
            >
            <input
              id="name${e.id}"
              type="text"
              .value="${e.name}"
              @input="${i => this.handleEditMapping(t, Object.assign(Object.assign({}, e), {
          name: i.target.value
        }))}"
            />
            ${Object.entries(e.mappings).map(([e]) => this.renderMappingSetting(t, e))}
            ${a ? F`<div class="weather-note">
                  ${Ca("panels.mappings.cards.mapping.errors.cannot-delete-mapping-because-zones-use-it", this.hass.language)}
                </div>` : F` <div
                  class="action-button"
                  @click="${e => this.handleRemoveMapping(e, t)}"
                >
                  <svg style="width:24px;height:24px" viewBox="0 0 24 24">
                    <path fill="#404040" d="${Ua}" />
                  </svg>
                  <span class="action-button-label">
                    ${Ca("common.actions.delete", this.hass.language)}
                  </span>
                </div>`}
          </div>
        </div>
      </ha-card>
    `;
      return this.mappingCache.set(i, s), s;
    }
    renderMappingSetting(e, t) {
      const i = this.mappings[e];
      if (!i || !this.hass) return F``;
      const a = i.mappings[t];
      return F`
      <div class="mappingline">
        <div class="mappingsettingname">
          <label for="${`${t}_${e}`}">
            ${Ca(`panels.mappings.cards.mapping.items.${t.toLowerCase()}`, this.hass.language)}
          </label>
        </div>
        <div class="mappingsettingline">
          <label
            >${Ca("panels.mappings.cards.mapping.source", this.hass.language)}:</label
          >
          <div class="radio-group">
            ${this.renderSimpleRadioOptions(e, t, a)}
          </div>
        </div>
        ${this.renderMappingInputs(e, t, a)}
      </div>
    `;
    }
    renderSimpleRadioOptions(e, t, i) {
      if (!this.hass || !this.config) return F``;
      const a = t === Le || t === De,
        s = i[Ve];
      return F`
      ${!a && this.config.use_weather_service ? F`
            <label>
              <input
                type="radio"
                name="${t}_${e}_source"
                value="${Re}"
                ?checked="${s === Re}"
                @change="${i => this.handleSimpleSourceChange(e, t, i)}"
              />
              ${Ca("panels.mappings.cards.mapping.sources.weather_service", this.hass.language)}
            </label>
          ` : ""}
      ${a ? F`
            <label>
              <input
                type="radio"
                name="${t}_${e}_source"
                value="${qe}"
                ?checked="${s === qe}"
                @change="${i => this.handleSimpleSourceChange(e, t, i)}"
              />
              ${Ca("panels.mappings.cards.mapping.sources.none", this.hass.language)}
            </label>
          ` : ""}

      <label>
        <input
          type="radio"
          name="${t}_${e}_source"
          value="${je}"
          ?checked="${s === je}"
          @change="${i => this.handleSimpleSourceChange(e, t, i)}"
        />
        ${Ca("panels.mappings.cards.mapping.sources.sensor", this.hass.language)}
      </label>

      <label>
        <input
          type="radio"
          name="${t}_${e}_source"
          value="${Fe}"
          ?checked="${s === Fe}"
          @change="${i => this.handleSimpleSourceChange(e, t, i)}"
        />
        ${Ca("panels.mappings.cards.mapping.sources.static", this.hass.language)}
      </label>
    `;
    }
    handleSimpleSourceChange(e, t, i) {
      const a = this.mappings[e],
        s = i.target.value;
      this.handleEditMapping(e, Object.assign(Object.assign({}, a), {
        mappings: Object.assign(Object.assign({}, a.mappings), {
          [t]: Object.assign(Object.assign({}, a.mappings[t]), {
            [Ve]: s,
            [Ke]: ""
          })
        })
      }));
    }
    handleSimpleInputChange(e, t, i, a) {
      const s = this.mappings[e],
        n = a.target.value;
      this.handleEditMapping(e, Object.assign(Object.assign({}, s), {
        mappings: Object.assign(Object.assign({}, s.mappings), {
          [t]: Object.assign(Object.assign({}, s.mappings[t]), {
            [i]: n
          })
        })
      }));
    }
    renderSourceOptions(e, t, i) {
      if (!this.hass) return F``;
      const a = t === Le || t === De;
      return F`
      <div class="mappingsettingline">
        <label for="${`${t}_${e}`}_source">
          ${Ca("panels.mappings.cards.mapping.source", this.hass.language)}:
        </label>
      </div>
      <div class="radio-group">
        ${a ? "" : this.renderWeatherServiceOption(e, t, i)}
        ${a ? this.renderNoneOption(e, t, i) : ""}
        ${this.renderSensorOption(e, t, i)}
        ${this.renderStaticValueOption(e, t, i)}
      </div>
    `;
    }
    renderWeatherServiceOption(e, t, i) {
      if (!this.hass || !this.config) return F``;
      const a = `${t}_${e}`,
        s = !this.config.use_weather_service,
        n = this.config.use_weather_service && i[Ve] === Re;
      return F`
      <label class="${s ? "strikethrough" : ""}">
        <input
          type="radio"
          id="${a}_weather"
          value="${Re}"
          name="${a}_source"
          ?checked="${n}"
          ?disabled="${s}"
          @change="${i => this.handleSourceChange(e, t, i)}"
        />
        ${Ca("panels.mappings.cards.mapping.sources.weather_service", this.hass.language)}
      </label>
    `;
    }
    renderNoneOption(e, t, i) {
      if (!this.hass) return F``;
      const a = `${t}_${e}`,
        s = i[Ve] === qe;
      return F`
      <label>
        <input
          type="radio"
          id="${a}_none"
          value="${qe}"
          name="${a}_source"
          ?checked="${s}"
          @change="${i => this.handleSourceChange(e, t, i)}"
        />
        ${Ca("panels.mappings.cards.mapping.sources.none", this.hass.language)}
      </label>
    `;
    }
    renderSensorOption(e, t, i) {
      if (!this.hass) return F``;
      const a = `${t}_${e}`,
        s = i[Ve] === je;
      return F`
      <label>
        <input
          type="radio"
          id="${a}_sensor"
          value="${je}"
          name="${a}_source"
          ?checked="${s}"
          @change="${i => this.handleSourceChange(e, t, i)}"
        />
        ${Ca("panels.mappings.cards.mapping.sources.sensor", this.hass.language)}
      </label>
    `;
    }
    renderStaticValueOption(e, t, i) {
      if (!this.hass) return F``;
      const a = `${t}_${e}`,
        s = i[Ve] === Fe;
      return F`
      <label>
        <input
          type="radio"
          id="${a}_static"
          value="${Fe}"
          name="${a}_source"
          ?checked="${s}"
          @change="${i => this.handleSourceChange(e, t, i)}"
        />
        ${Ca("panels.mappings.cards.mapping.sources.static", this.hass.language)}
      </label>
    `;
    }
    handleSourceChange(e, t, i) {
      const a = this.mappings[e],
        s = i.target.value;
      this.handleEditMapping(e, Object.assign(Object.assign({}, a), {
        mappings: Object.assign(Object.assign({}, a.mappings), {
          [t]: Object.assign(Object.assign({}, a.mappings[t]), {
            [Ve]: s,
            [Ke]: ""
          })
        })
      }));
    }
    renderMappingInputs(e, t, i) {
      if (!this.hass) return F``;
      const a = i[Ve];
      return F`
      ${a === je ? this.renderSensorInput(e, t, i) : ""}
      ${a === Fe ? this.renderStaticValueInput(e, t, i) : ""}
      ${a === je || a === Fe ? this.renderUnitSelect(e, t, i) : ""}
      ${t !== Pe || a !== je && a !== Fe ? "" : this.renderPressureTypeSelect(e, t, i)}
      ${a === je ? this.renderAggregateSelect(e, t, i) : ""}
    `;
    }
    renderSensorInput(e, t, i) {
      if (!this.hass) return F``;
      const a = `${t}_${e}`;
      return F`
      <div class="mappingsettingline">
        <label for="${a}_sensor_entity">
          ${Ca("panels.mappings.cards.mapping.sensor-entity", this.hass.language)}:
        </label>
        <input
          type="text"
          id="${a}_sensor_entity"
          .value="${i[Ke] || ""}"
          @change="${i => this.handleSensorChange(e, t, i)}"
        />
      </div>
    `;
    }
    renderStaticValueInput(e, t, i) {
      if (!this.hass) return F``;
      const a = `${t}_${e}`;
      return F`
      <div class="mappingsettingline">
        <label for="${a}_static_value">
          ${Ca("panels.mappings.cards.mapping.static_value", this.hass.language)}:
        </label>
        <input
          type="text"
          id="${a}_static_value"
          .value="${i[Xe] || ""}"
          @input="${i => this.handleStaticValueChange(e, t, i)}"
        />
      </div>
    `;
    }
    renderUnitSelect(e, t, i) {
      if (!this.hass || !this.config) return F``;
      const a = `${t}_${e}`;
      return F`
      <div class="mappingsettingline">
        <label for="${a}_unit">
          ${Ca("panels.mappings.cards.mapping.input-units", this.hass.language)}:
        </label>
        <select
          id="${a}_unit"
          @change="${i => this.handleUnitChange(e, t, i)}"
        >
          ${this.renderUnitOptionsForMapping(t, i)}
        </select>
      </div>
    `;
    }
    renderPressureTypeSelect(e, t, i) {
      if (!this.hass) return F``;
      const a = `${t}_${e}`;
      return F`
      <div class="mappingsettingline">
        <label for="${a}_pressure_type">
          ${Ca("panels.mappings.cards.mapping.pressure-type", this.hass.language)}:
        </label>
        <select
          id="${a}_pressure_type"
          @change="${i => this.handlePressureTypeChange(e, t, i)}"
        >
          ${this.renderPressureTypes(t, i)}
        </select>
      </div>
    `;
    }
    renderAggregateSelect(e, t, i) {
      if (!this.hass) return F``;
      const a = `${t}_${e}`;
      return F`
      <div class="mappingsettingline">
        <label for="${a}_aggregate">
          ${Ca("panels.mappings.cards.mapping.sensor-aggregate-use-the", this.hass.language)}
        </label>
        <select
          id="${a}_aggregate"
          @change="${i => this.handleAggregateChange(e, t, i)}"
        >
          ${this.renderAggregateOptionsForMapping(t, i)}
        </select>
        <label for="${a}_aggregate">
          ${Ca("panels.mappings.cards.mapping.sensor-aggregate-of-sensor-values-to-calculate", this.hass.language)}
        </label>
      </div>
    `;
    }
    handleSensorChange(e, t, i) {
      const a = this.mappings[e];
      this.handleEditMapping(e, Object.assign(Object.assign({}, a), {
        mappings: Object.assign(Object.assign({}, a.mappings), {
          [t]: Object.assign(Object.assign({}, a.mappings[t]), {
            [Ke]: i.target.value
          })
        })
      }));
    }
    handleStaticValueChange(e, t, i) {
      const a = this.mappings[e];
      this.handleEditMapping(e, Object.assign(Object.assign({}, a), {
        mappings: Object.assign(Object.assign({}, a.mappings), {
          [t]: Object.assign(Object.assign({}, a.mappings[t]), {
            [Xe]: i.target.value
          })
        })
      }));
    }
    handleUnitChange(e, t, i) {
      const a = this.mappings[e];
      this.handleEditMapping(e, Object.assign(Object.assign({}, a), {
        mappings: Object.assign(Object.assign({}, a.mappings), {
          [t]: Object.assign(Object.assign({}, a.mappings[t]), {
            [Ye]: i.target.value
          })
        })
      }));
    }
    handlePressureTypeChange(e, t, i) {
      const a = this.mappings[e];
      this.handleEditMapping(e, Object.assign(Object.assign({}, a), {
        mappings: Object.assign(Object.assign({}, a.mappings), {
          [t]: Object.assign(Object.assign({}, a.mappings[t]), {
            [We]: i.target.value
          })
        })
      }));
    }
    handleAggregateChange(e, t, i) {
      const a = this.mappings[e];
      this.handleEditMapping(e, Object.assign(Object.assign({}, a), {
        mappings: Object.assign(Object.assign({}, a.mappings), {
          [t]: Object.assign(Object.assign({}, a.mappings[t]), {
            [Je]: i.target.value
          })
        })
      }));
    }
    renderAggregateOptionsForMapping(e, t) {
      if (!this.hass || !this.config) return F``;
      let i = "average";
      return e === Ne && (i = "delta"), e === Ie && (i = "average"), t[Je] && (i = t[Je]), F`
      ${Qe.map(e => this.renderAggregateOption(e, i))}
    `;
    }
    renderAggregateOption(e, t) {
      if (this.hass && this.config) {
        return F`<option value="${e}" ?selected="${e === t}">
        ${Ca("panels.mappings.cards.mapping.aggregates." + e, this.hass.language)}
      </option>`;
      }
      return F``;
    }
    renderPressureTypes(e, t) {
      if (this.hass && this.config) {
        let e = F``;
        const i = t[We];
        return e = F`${e}
        <option
          value="${Ze}"
          ?selected="${i === Ze}"
        >
          ${Ca("panels.mappings.cards.mapping.pressure_types." + Ze, this.hass.language)}
        </option>
        <option
          value="${Ge}"
          ?selected="${i === Ge}"
        >
          ${Ca("panels.mappings.cards.mapping.pressure_types." + Ge, this.hass.language)}
        </option>`, e;
      }
      return F``;
    }
    renderUnitOptionsForMapping(e, t) {
      if (!this.hass || !this.config) return F``;
      const i = function (e) {
        switch (e) {
          case He:
          case Be:
            return [{
              unit: "°C",
              system: Oe
            }, {
              unit: "°F",
              system: Ce
            }];
          case Ne:
          case Le:
            return [{
              unit: at,
              system: Oe
            }, {
              unit: st,
              system: Ce
            }];
          case Ie:
            return [{
              unit: lt,
              system: Oe
            }, {
              unit: ct,
              system: Ce
            }];
          case Me:
            return [{
              unit: "%",
              system: [Oe, Ce]
            }];
          case Pe:
            return [{
              unit: "millibar",
              system: Oe
            }, {
              unit: "hPa",
              system: Oe
            }, {
              unit: "psi",
              system: Ce
            }, {
              unit: nt,
              system: Ce
            }];
          case Ue:
            return [{
              unit: "km/h",
              system: Oe
            }, {
              unit: ot,
              system: Oe
            }, {
              unit: rt,
              system: Ce
            }];
          case De:
            return [{
              unit: "W/m2",
              system: Oe
            }, {
              unit: "MJ/day/m2",
              system: Oe
            }, {
              unit: "W/sq ft",
              system: Ce
            }, {
              unit: "MJ/day/sq ft",
              system: Ce
            }];
          default:
            return [];
        }
      }(e);
      let a = t[Ye];
      const s = this.config.units;
      if (!t[Ye]) for (const e of i) if ("string" == typeof e.system) {
        if (s === e.system) {
          a = e.unit;
          break;
        }
      } else {
        for (const t of e.system) if (s === t.system) {
          a = e.unit;
          break;
        }
        if (a === e.unit) break;
      }
      return F`
      ${i.map(e => F`
          <option value="${e.unit}" ?selected="${a === e.unit}">
            ${e.unit}
          </option>
        `)}
    `;
    }
    render() {
      return this.hass ? this.isLoading ? F`
        <ha-card
          header="${Ca("panels.mappings.title", this.hass.language)}"
        >
          <div class="card-content">
            <div class="loading-indicator">
              ${Ca("common.loading-messages.general", this.hass.language)}
            </div>
          </div>
        </ha-card>
      ` : F`
      <ha-card
        header="${Ca("panels.mappings.title", this.hass.language)}"
      >
        <div class="card-content">
          ${Ca("panels.mappings.description", this.hass.language)}
        </div>
      </ha-card>

      <ha-card
        header="${Ca("panels.mappings.cards.add-mapping.header", this.hass.language)}"
      >
        <div class="card-content">
          <div class="zoneline">
            <label for="mappingNameInput"
              >${Ca("panels.mappings.labels.mapping-name", this.hass.language)}:</label
            >
            <input id="mappingNameInput" type="text" />
          </div>
          <div class="zoneline">
            <span></span>
            <button @click="${this.handleAddMapping}">
              ${Ca("panels.mappings.cards.add-mapping.actions.add", this.hass.language)}
            </button>
          </div>
        </div>
      </ha-card>

      ${this.renderMappingsList()}
    ` : F``;
    }
    renderMappingsList() {
      const e = this.mappings.slice(0, Math.min(this.mappings.length, 10)),
        t = this.mappings.slice(10);
      return F`
      ${e.map((e, t) => this.renderMappingCard(e, t))}
      ${t.length > 0 ? F`
            <div class="load-more">
              <button @click="${this.loadMoreMappings}">
                Load ${t.length} more mappings...
              </button>
            </div>
          ` : ""}
    `;
    }
    renderMappingCard(e, t) {
      if (!this.hass) return F``;
      const i = this.zones.filter(t => t.mapping === e.id).length;
      return F`
      <ha-card header="${e.id}: ${e.name}">
        <div class="card-content">
          <div class="card-content">
            <label for="name${e.id}"
              >${Ca("panels.mappings.labels.mapping-name", this.hass.language)}:</label
            >
            <input
              id="name${e.id}"
              type="text"
              .value="${e.name}"
              @input="${i => this.handleEditMapping(t, Object.assign(Object.assign({}, e), {
        name: i.target.value
      }))}"
            />
            ${this.renderMappingSettings(e, t)}
            ${i ? F`<div class="weather-note">
                  ${Ca("panels.mappings.cards.mapping.errors.cannot-delete-mapping-because-zones-use-it", this.hass.language)}
                </div>` : F` <div
                  class="action-button"
                  @click="${e => this.handleRemoveMapping(e, t)}"
                >
                  <svg style="width:24px;height:24px" viewBox="0 0 24 24">
                    <path fill="#404040" d="${Ua}" />
                  </svg>
                  <span class="action-button-label">
                    ${Ca("common.actions.delete", this.hass.language)}
                  </span>
                </div>`}
          </div>
        </div>
      </ha-card>
    `;
    }
    renderMappingSettings(e, t) {
      const i = Object.entries(e.mappings);
      return F`
      ${i.map(([e]) => this.renderMappingSetting(t, e))}
    `;
    }
    loadMoreMappings() {
      this._scheduleUpdate();
    }
    static get styles() {
      return h`
      ${ss}/* View-specific styles only - most common styles are now in globalStyle */
    `;
    }
    disconnectedCallback() {
      super.disconnectedCallback(), this.debounceTimers.forEach(e => {
        clearTimeout(e);
      }), this.debounceTimers.clear(), this.globalDebounceTimer && (clearTimeout(this.globalDebounceTimer), this.globalDebounceTimer = null), this.mappingCache.clear();
    }
  };
  s([pe()], ws.prototype, "config", void 0), s([pe({
    type: Array
  })], ws.prototype, "zones", void 0), s([pe({
    type: Array
  })], ws.prototype, "mappings", void 0), s([pe({
    type: Boolean
  })], ws.prototype, "isLoading", void 0), s([pe({
    type: Boolean
  })], ws.prototype, "isSaving", void 0), s([me("#mappingNameInput")], ws.prototype, "mappingNameInput", void 0), ws = s([he("smart-irrigation-view-mappings")], ws);
  const $s = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];
  let xs = class extends Qa(ce) {
    constructor() {
      super(...arguments), this._schedules = [], this._zones = [], this._isLoading = !0, this._showDialog = !1, this._editingSchedule = {
        name: "",
        type: "daily",
        enabled: !0,
        time: "06:00",
        action: "irrigate",
        zones: "all"
      }, this._editingId = null;
    }
    hassSubscribe() {
      return this._load(), [this.hass.connection.subscribeMessage(() => this._load(), {
        type: we + "_config_updated"
      })];
    }
    async _load() {
      var e;
      if (this.hass) try {
        const [t, i] = await Promise.all([(e = this.hass, e.callWS({
          type: we + "/schedules"
        })), Fa(this.hass)]);
        this._schedules = t || [], this._zones = i || [];
      } catch (e) {
        console.error("Failed to load schedules", e), Da(this, this.hass, "common.errors.load_failed", e);
      } finally {
        this._isLoading = !1;
      }
    }
    _openAdd() {
      this._editingSchedule = {
        name: "",
        type: "daily",
        enabled: !0,
        time: "06:00",
        action: "irrigate",
        zones: "all"
      }, this._editingId = null, this._showDialog = !0;
    }
    _openEdit(e) {
      var t;
      this._editingSchedule = Object.assign({}, e), this._editingId = null !== (t = e.id) && void 0 !== t ? t : null, this._showDialog = !0;
    }
    _closeDialog() {
      this._showDialog = !1;
    }
    async _save() {
      const e = Object.assign({}, this._editingSchedule);
      this._editingId && (e.id = this._editingId);
      try {
        await ((e, t) => e.callWS({
          type: we + "/schedule_save",
          schedule: t
        }))(this.hass, e), this._closeDialog(), await this._load();
      } catch (e) {
        console.error("Failed to save schedule", e), Da(this, this.hass, "common.errors.save_failed", e);
      }
    }
    async _delete(e) {
      try {
        await (t = this.hass, i = e, t.callWS({
          type: we + "/schedule_delete",
          schedule_id: i
        })), await this._load();
      } catch (e) {
        console.error("Failed to delete schedule", e), Da(this, this.hass, "common.errors.delete_failed", e);
      }
      var t, i;
    }
    _update(e) {
      this._editingSchedule = Object.assign(Object.assign({}, this._editingSchedule), e);
    }
    _typeLabel(e) {
      return Ca(`panels.schedules.types.${e}`, this.hass.language) || e;
    }
    _zonesLabel(e) {
      if ("all" === e) return Ca("panels.schedules.zones_all", this.hass.language);
      if (Array.isArray(e)) {
        const t = e.map(e => {
          const t = this._zones.find(t => String(t.id) === String(e));
          return t ? t.name : e;
        }).join(", ");
        return t || e.join(", ");
      }
      return String(e);
    }
    _renderZonePicker() {
      const e = "all" === this._editingSchedule.zones || !Array.isArray(this._editingSchedule.zones),
        t = e ? [] : this._editingSchedule.zones.map(String);
      return F`
      <div class="field">
        <label
          >${Ca("panels.schedules.fields.zones", this.hass.language)}</label
        >
        <div class="switch-container">
          <input
            type="radio"
            id="zones_all"
            name="zones_mode"
            ?checked="${e}"
            @change=${() => this._update({
        zones: "all"
      })}
          />
          <label for="zones_all"
            >${Ca("panels.schedules.zones_all", this.hass.language)}</label
          >
          <input
            type="radio"
            id="zones_specific"
            name="zones_mode"
            ?checked="${!e}"
            @change=${() => this._update({
        zones: []
      })}
          />
          <label for="zones_specific"
            >${Ca("panels.schedules.zones_specific", this.hass.language)}</label
          >
        </div>
        ${e ? "" : F`
              <div class="zone-checkboxes">
                ${this._zones.map(e => F`
                    <label class="zone-check">
                      <input
                        type="checkbox"
                        ?checked="${t.includes(String(e.id))}"
                        @change=${t => {
        const i = t.target.checked,
          a = String(e.id),
          s = Array.isArray(this._editingSchedule.zones) ? [...this._editingSchedule.zones] : [],
          n = i ? [...s, a] : s.filter(e => e !== a);
        this._update({
          zones: n
        });
      }}
                      />
                      ${e.name}
                    </label>
                  `)}
              </div>
            `}
      </div>
    `;
    }
    _renderTypeFields() {
      var e;
      const t = this._editingSchedule;
      switch (t.type) {
        case "daily":
          return F`
          <div class="field">
            <label
              >${Ca("panels.schedules.fields.time", this.hass.language)}</label
            >
            <input
              type="time"
              .value="${t.time || "06:00"}"
              @change=${e => this._update({
            time: e.target.value
          })}
            />
          </div>
        `;
        case "weekly":
          return F`
          <div class="field">
            <label
              >${Ca("panels.schedules.fields.time", this.hass.language)}</label
            >
            <input
              type="time"
              .value="${t.time || "06:00"}"
              @change=${e => this._update({
            time: e.target.value
          })}
            />
          </div>
          <div class="field">
            <label
              >${Ca("panels.schedules.fields.days_of_week", this.hass.language)}</label
            >
            <div class="day-checkboxes">
              ${$s.map(e => F`
                  <label class="day-check">
                    <input
                      type="checkbox"
                      ?checked="${(t.days_of_week || []).includes(e)}"
                      @change=${i => {
            const a = i.target.checked,
              s = t.days_of_week || [],
              n = a ? [...s, e] : s.filter(t => t !== e);
            this._update({
              days_of_week: n
            });
          }}
                    />
                    ${Ca(`panels.schedules.days.${e}`, this.hass.language)}
                  </label>
                `)}
            </div>
          </div>
        `;
        case "monthly":
          return F`
          <div class="field">
            <label
              >${Ca("panels.schedules.fields.time", this.hass.language)}</label
            >
            <input
              type="time"
              .value="${t.time || "06:00"}"
              @change=${e => this._update({
            time: e.target.value
          })}
            />
          </div>
          <div class="field">
            <label
              >${Ca("panels.schedules.fields.day_of_month", this.hass.language)}</label
            >
            <input
              type="number"
              min="1"
              max="31"
              .value="${String(t.day_of_month || 1)}"
              @input=${e => this._update({
            day_of_month: parseInt(e.target.value)
          })}
            />
          </div>
        `;
        case "interval":
          return F`
          <div class="field">
            <label
              >${Ca("panels.schedules.fields.interval_hours", this.hass.language)}</label
            >
            <div class="input-suffix-row">
              <input
                type="number"
                min="1"
                .value="${String(t.interval_hours || 24)}"
                @input=${e => this._update({
            interval_hours: parseInt(e.target.value)
          })}
              />
              <span class="suffix"
                >${Ca("panels.schedules.hours", this.hass.language)}</span
              >
            </div>
          </div>
        `;
        case "sunrise":
        case "sunset":
          return F`${this._renderSunOffsetFields()}`;
        case "solar_azimuth":
          return F`
          <div class="field">
            <label
              >${Ca("panels.schedules.fields.azimuth_angle", this.hass.language)}</label
            >
            <div class="input-suffix-row">
              <input
                type="number"
                min="0"
                max="359"
                step="1"
                .value="${String(null !== (e = t.azimuth_angle) && void 0 !== e ? e : 90)}"
                @input=${e => this._update({
            azimuth_angle: parseInt(e.target.value)
          })}
              />
              <span class="suffix">°</span>
            </div>
          </div>
          ${this._renderSunOffsetFields()}
        `;
        default:
          return F``;
      }
    }
    _renderSunOffsetFields() {
      var e;
      const t = this._editingSchedule;
      return F`
      <div class="field">
        <label
          >${Ca("panels.schedules.fields.offset_minutes", this.hass.language)}</label
        >
        <div class="input-suffix-row">
          <input
            type="number"
            step="1"
            .value="${String(null !== (e = t.offset_minutes) && void 0 !== e ? e : 0)}"
            @input=${e => this._update({
        offset_minutes: parseInt(e.target.value)
      })}
          />
          <span class="suffix"
            >${Ca("panels.schedules.minutes", this.hass.language)}</span
          >
        </div>
      </div>
    `;
    }
    _renderTimeAnchorField() {
      var e;
      const t = this._editingSchedule;
      if ("irrigate" !== t.action || "interval" === t.type) return F``;
      const i = ["sunrise", "sunset", "solar_azimuth"].includes(t.type) && !1 !== t.account_for_duration,
        a = null !== (e = t.time_anchor) && void 0 !== e ? e : i ? "finish" : "start";
      return F`
      <div class="field">
        <label
          >${Ca("panels.schedules.fields.time_anchor", this.hass.language)}</label
        >
        <select
          @change=${e => this._update({
        time_anchor: e.target.value
      })}
        >
          ${["start", "finish"].map(e => F`
              <option value="${e}" ?selected="${a === e}">
                ${Ca(`panels.schedules.time_anchor.${e}`, this.hass.language)}
              </option>
            `)}
        </select>
      </div>
    `;
    }
    _renderDialog() {
      if (!this._showDialog) return F``;
      const e = this._editingSchedule,
        t = this._editingId ? Ca("panels.schedules.dialog.edit_title", this.hass.language) : Ca("panels.schedules.dialog.add_title", this.hass.language);
      return F`
      <ha-dialog open .heading=${!0} @closed=${this._closeDialog}>
        <div slot="heading">
          <ha-header-bar>
            <ha-icon-button
              slot="navigationIcon"
              .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
            ></ha-icon-button>
            <span slot="title">${t}</span>
          </ha-header-bar>
        </div>

        <div class="dialog-content">
          <div class="field">
            <label
              >${Ca("panels.schedules.fields.name", this.hass.language)}</label
            >
            <input
              type="text"
              .value="${e.name}"
              @input=${e => this._update({
        name: e.target.value
      })}
              required
            />
          </div>

          <div class="field">
            <label
              >${Ca("panels.schedules.fields.type", this.hass.language)}</label
            >
            <select
              @change=${e => this._update({
        type: e.target.value
      })}
            >
              ${["daily", "weekly", "monthly", "interval", "sunrise", "sunset", "solar_azimuth"].map(t => F`
                  <option value="${t}" ?selected="${e.type === t}">
                    ${this._typeLabel(t)}
                  </option>
                `)}
            </select>
          </div>

          ${this._renderTypeFields()} ${this._renderTimeAnchorField()}
          ${this._renderZonePicker()}

          <div class="field-row">
            <label
              >${Ca("panels.schedules.fields.enabled", this.hass.language)}</label
            >
            <input
              type="checkbox"
              ?checked="${e.enabled}"
              @change=${e => this._update({
        enabled: e.target.checked
      })}
            />
          </div>

          <div class="field">
            <label
              >${Ca("panels.schedules.fields.start_date", this.hass.language)}</label
            >
            <input
              type="date"
              .value="${e.start_date || ""}"
              @change=${e => this._update({
        start_date: e.target.value || void 0
      })}
            />
          </div>

          <div class="field">
            <label
              >${Ca("panels.schedules.fields.end_date", this.hass.language)}</label
            >
            <input
              type="date"
              .value="${e.end_date || ""}"
              @change=${e => this._update({
        end_date: e.target.value || void 0
      })}
            />
          </div>
        </div>

        <div class="dialog-footer">
          <button class="dialog-btn" @click=${this._closeDialog}>
            ${Ca("common.actions.cancel", this.hass.language)}
          </button>
          <button class="dialog-btn dialog-btn-primary" @click=${this._save}>
            ${Ca("common.actions.save", this.hass.language)}
          </button>
        </div>
      </ha-dialog>
    `;
    }
    render() {
      return this.hass ? this._isLoading ? F`
        <ha-card
          header="${Ca("panels.schedules.title", this.hass.language)}"
        >
          <div class="card-content">
            ${Ca("common.loading", this.hass.language)}...
          </div>
        </ha-card>
      ` : F`
      ${this._renderDialog()}

      <ha-card
        header="${Ca("panels.schedules.title", this.hass.language)}"
      >
        <div class="card-content">
          ${Ca("panels.schedules.description", this.hass.language)}
        </div>
        <div class="card-content">
          <button class="add-btn" @click=${this._openAdd}>
            <svg style="width:20px;height:20px" viewBox="0 0 24 24">
              <path fill="currentColor" d="${Ra}" />
            </svg>
            ${Ca("panels.schedules.add", this.hass.language)}
          </button>
        </div>
      </ha-card>

      ${0 === this._schedules.length ? F`
            <ha-card>
              <div class="card-content">
                ${Ca("panels.schedules.no_items", this.hass.language)}
              </div>
            </ha-card>
          ` : this._schedules.map(e => F`
              <ha-card header="${e.name}">
                <div class="card-content">
                  <div class="info-row">
                    <span class="info-label"
                      >${Ca("panels.schedules.fields.type", this.hass.language)}:</span
                    >
                    <span>${this._typeLabel(e.type)}</span>
                  </div>
                  ${e.time && ["daily", "weekly", "monthly"].includes(e.type) ? F`
                        <div class="info-row">
                          <span class="info-label"
                            >${Ca("panels.schedules.fields.time", this.hass.language)}:</span
                          >
                          <span>${e.time}</span>
                        </div>
                      ` : ""}
                  ${e.interval_hours ? F`
                        <div class="info-row">
                          <span class="info-label"
                            >${Ca("panels.schedules.fields.interval_hours", this.hass.language)}:</span
                          >
                          <span
                            >${e.interval_hours}
                            ${Ca("panels.schedules.hours", this.hass.language)}</span
                          >
                        </div>
                      ` : ""}
                  <div class="info-row">
                    <span class="info-label"
                      >${Ca("panels.schedules.fields.zones", this.hass.language)}:</span
                    >
                    <span>${this._zonesLabel(e.zones)}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${Ca("panels.schedules.fields.enabled", this.hass.language)}:</span
                    >
                    <span
                      >${e.enabled ? Ca("common.labels.yes", this.hass.language) : Ca("common.labels.no", this.hass.language)}</span
                    >
                  </div>
                </div>
                <div class="card-content action-buttons">
                  <div class="action-buttons-left">
                    <div
                      class="action-button-left"
                      @click=${() => this._openEdit(e)}
                    >
                      <svg style="width:20px;height:20px" viewBox="0 0 24 24">
                        <path fill="#404040" d="${"M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z"}" />
                      </svg>
                      <span class="action-button-label"
                        >${Ca("common.actions.edit", this.hass.language)}</span
                      >
                    </div>
                  </div>
                  <div class="action-buttons-right">
                    <div
                      class="action-button-right"
                      @click=${() => e.id && this._delete(e.id)}
                    >
                      <span class="action-button-label"
                        >${Ca("common.actions.delete", this.hass.language)}</span
                      >
                      <svg style="width:20px;height:20px" viewBox="0 0 24 24">
                        <path fill="#404040" d="${Ua}" />
                      </svg>
                    </div>
                  </div>
                </div>
              </ha-card>
            `)}
    ` : F``;
    }
    static get styles() {
      return [ss, h`
        .dialog-content {
          display: flex;
          flex-direction: column;
          gap: 14px;
          padding: 4px 0;
          color: var(--primary-text-color);
        }
        .field {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }
        .field label,
        .field-row label {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--secondary-text-color);
        }
        .field input[type="text"],
        .field input[type="time"],
        .field input[type="date"],
        .field input[type="number"],
        .field select {
          padding: 8px 10px;
          border: 1px solid var(--divider-color, #e0e0e0);
          border-radius: 4px;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
          font-size: 1rem;
          font-family: inherit;
          box-sizing: border-box;
        }
        .field-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          min-height: 36px;
        }
        .field-row input[type="checkbox"] {
          width: 18px;
          height: 18px;
          accent-color: var(--primary-color);
        }
        .day-checkboxes,
        .zone-checkboxes {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 4px;
        }
        .day-check,
        .zone-check {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 0.875rem;
          cursor: pointer;
        }
        .input-suffix-row {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .input-suffix-row input {
          flex: 1;
          padding: 8px 10px;
          border: 1px solid var(--divider-color, #e0e0e0);
          border-radius: 4px;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
          font-size: 1rem;
          font-family: inherit;
        }
        .suffix {
          color: var(--secondary-text-color);
          font-size: 0.875rem;
        }
        .info-row {
          display: flex;
          gap: 8px;
          margin-bottom: 4px;
          font-size: 0.9rem;
        }
        .info-label {
          font-weight: 500;
          color: var(--secondary-text-color);
          min-width: 80px;
        }
        .add-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          background: var(--primary-color);
          color: var(--text-primary-color, #fff);
          border: none;
          border-radius: 4px;
          font-size: 0.95rem;
          cursor: pointer;
        }
      `];
    }
  };
  s([pe({
    attribute: !1
  })], xs.prototype, "hass", void 0), s([ge()], xs.prototype, "_schedules", void 0), s([ge()], xs.prototype, "_zones", void 0), s([ge()], xs.prototype, "_isLoading", void 0), s([ge()], xs.prototype, "_showDialog", void 0), s([ge()], xs.prototype, "_editingSchedule", void 0), s([ge()], xs.prototype, "_editingId", void 0), xs = s([he("smart-irrigation-view-schedules")], xs);
  let ks = class extends Qa(ce) {
    constructor() {
      super(...arguments), this._forecast = null, this._mappings = [], this._records = new Map(), this._loading = !0, this._metric = !0;
    }
    hassSubscribe() {
      return this._fetch(), [this.hass.connection.subscribeMessage(() => this._fetch(), {
        type: we + "_config_updated"
      })];
    }
    async _fetch() {
      var e;
      if (this.hass) try {
        const [t, i, a] = await Promise.all([(e = this.hass, e.callWS({
          type: we + "/weather_forecast"
        })), Va(this.hass), ja(this.hass)]);
        this._forecast = t, this._mappings = i || [], this._metric = (null == a ? void 0 : a.units) !== Ce;
        const s = new Map();
        await Promise.all(this._mappings.map(async e => {
          if (void 0 !== e.id) try {
            s.set(e.id, (await ((e, t, i = 10) => e.callWS({
              type: we + "/weather_records",
              mapping_id: t,
              limit: i
            }))(this.hass, e.id.toString(), 0)) || []);
          } catch (e) {}
        })), this._records = s;
      } catch (e) {
        console.error("Failed to fetch weather data", e);
      } finally {
        this._loading = !1;
      }
    }
    render() {
      return this.hass ? F`${this._renderForecast()} ${this._renderRecords()}` : F``;
    }
    _renderForecast() {
      if (!this.hass) return F``;
      const e = this.hass.language,
        t = this._forecast;
      return F`
      <ha-card
        header="${Ca("panels.setup.weather_data.forecast_title", e)}"
      >
        <div class="card-content">
          ${t && t.available && 0 !== t.days.length ? F`
                <div class="forecast-row">
                  ${t.days.map(t => this._renderForecastDay(t, e))}
                </div>
              ` : F`<div class="weather-note">
                ${Ca("panels.setup.weather_data.forecast_none", e)}
              </div>`}
        </div>
      </ha-card>
    `;
    }
    _renderForecastDay(e, t) {
      const i = (() => {
          try {
            return new Intl.DateTimeFormat(t, {
              weekday: "short",
              month: "short",
              day: "numeric"
            }).format(new Date(e.date + "T00:00:00"));
          } catch (t) {
            return e.date;
          }
        })(),
        a = e => {
          const t = vs(e, "temperature", this._metric);
          return t ? `${Math.round(t.value)}°` : "-";
        };
      return F`
      <div class="forecast-day">
        <div class="forecast-date">${i}</div>
        <div class="forecast-temps">
          <span class="hi">${a(e.temp_max)}</span>
          <span class="lo">${a(e.temp_min)}</span>
        </div>
        <div class="forecast-meta">
          <ha-icon icon="mdi:weather-rainy"></ha-icon>${fs(e.precipitation, "precipitation", this._metric)}
        </div>
        <div class="forecast-meta">
          <ha-icon icon="mdi:weather-windy"></ha-icon>${fs(e.windspeed, "windspeed", this._metric)}
        </div>
      </div>
    `;
    }
    _renderRecords() {
      if (!this.hass) return F``;
      const e = this.hass.language;
      return this._loading && 0 === this._mappings.length ? F`<ha-card
        header="${Ca("panels.mappings.weather-records.title", e)}"
      >
        <div class="card-content">
          <div class="loading-indicator">
            ${Ca("common.loading-messages.general", e)}
          </div>
        </div>
      </ha-card>` : 0 === this._mappings.length ? F`<ha-card
        header="${Ca("panels.mappings.weather-records.title", e)}"
      >
        <div class="card-content">
          <div class="weather-note">
            ${Ca("panels.mappings.no_items", e)}
          </div>
        </div>
      </ha-card>` : F`${this._mappings.map(t => this._renderMappingRecords(t, e))}`;
    }
    _renderMappingRecords(e, t) {
      const i = void 0 !== e.id && this._records.get(e.id) || [],
        a = `${Ca("panels.mappings.weather-records.title", t)} — ${e.name}`,
        s = e => {
          try {
            return t = e, Number.isNaN(rs(t).getTime()) ? "-" : function (e) {
              const t = rs(e);
              return `${ns(t.getMonth() + 1)}-${ns(t.getDate())} ${ns(t.getHours())}:${ns(t.getMinutes())}`;
            }(e);
          } catch (e) {
            return "-";
          }
          var t;
        };
      return F`
      <ha-card header="${a}">
        <div class="card-content">
          ${0 === i.length ? F`<div class="weather-note">
                ${Ca("panels.mappings.weather-records.no-data", t)}
              </div>` : F`
                <div class="weather-table">
                  <div class="weather-header">
                    <span
                      >${Ca("panels.mappings.weather-records.timestamp", t)}</span
                    >
                    <span
                      >${Ca("panels.mappings.weather-records.temperature", t)}</span
                    >
                    <span
                      >${Ca("panels.mappings.weather-records.humidity", t)}</span
                    >
                    <span
                      >${Ca("panels.mappings.weather-records.dewpoint", t)}</span
                    >
                    <span
                      >${Ca("panels.mappings.weather-records.wind", t)}</span
                    >
                    <span
                      >${Ca("panels.mappings.weather-records.pressure", t)}</span
                    >
                    <span
                      >${Ca("panels.mappings.weather-records.precipitation", t)}</span
                    >
                    <span
                      >${Ca("panels.mappings.weather-records.retrieval-time", t)}</span
                    >
                  </div>
                  ${i.map(e => F`
                      <div class="weather-row">
                        <span>${s(e.timestamp)}</span>
                        <span
                          >${fs(e.temperature, "temperature", this._metric)}</span
                        >
                        <span>${(e => null != e ? e.toFixed(1) + " %" : "-")(e.humidity)}</span>
                        <span
                          >${fs(e.dewpoint, "temperature", this._metric)}</span
                        >
                        <span
                          >${fs(e.wind_speed, "windspeed", this._metric)}</span
                        >
                        <span
                          >${fs(e.pressure, "pressure", this._metric)}</span
                        >
                        <span
                          >${fs(e.precipitation, "precipitation", this._metric)}</span
                        >
                        <span>${s(e.retrieval_time)}</span>
                      </div>
                    `)}
                </div>
              `}
        </div>
      </ha-card>
    `;
    }
    static get styles() {
      return h`
      ${ss}

      :host {
        display: block;
        width: 100%;
      }

      .forecast-row {
        display: flex;
        gap: 8px;
        overflow-x: auto;
        padding-bottom: 4px;
      }

      .forecast-day {
        flex: 0 0 auto;
        min-width: 92px;
        display: flex;
        flex-direction: column;
        gap: 4px;
        padding: 10px 12px;
        border: 1px solid var(--divider-color);
        border-radius: 8px;
        background: var(--secondary-background-color);
      }

      .forecast-date {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--primary-text-color);
      }

      .forecast-temps {
        display: flex;
        gap: 8px;
        align-items: baseline;
      }

      .forecast-temps .hi {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--primary-text-color);
      }

      .forecast-temps .lo {
        font-size: 0.9rem;
        color: var(--secondary-text-color);
      }

      .forecast-meta {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 0.8rem;
        color: var(--secondary-text-color);
      }

      .forecast-meta ha-icon {
        --mdc-icon-size: 16px;
        color: var(--secondary-text-color);
      }
    `;
    }
  };
  s([pe()], ks.prototype, "narrow", void 0), s([ge()], ks.prototype, "_forecast", void 0), s([ge()], ks.prototype, "_mappings", void 0), s([ge()], ks.prototype, "_records", void 0), s([ge()], ks.prototype, "_loading", void 0), s([ge()], ks.prototype, "_metric", void 0), ks = s([he("smart-irrigation-view-weather-data")], ks);
  var Ss;
  !function (e) {
    e.WeatherLocation = "weather-location", e.Zones = "zones", e.WhenToWater = "when-to-water", e.Advanced = "advanced", e.Help = "help";
  }(Ss || (Ss = {}));
  const zs = {
    [Ss.WeatherLocation]: "panels.setup.tabs.weather_location",
    [Ss.Zones]: "panels.setup.tabs.my_zones",
    [Ss.WhenToWater]: "panels.setup.tabs.when_to_water",
    [Ss.Advanced]: "panels.setup.tabs.advanced",
    [Ss.Help]: "panels.help.title"
  };
  let Es = class extends ce {
    get _activeTab() {
      var e;
      const t = null === (e = this.path) || void 0 === e ? void 0 : e.subpage;
      return Object.values(Ss).includes(null != t ? t : "") ? t : Ss.WeatherLocation;
    }
    _selectTab(e) {
      Na(0, as("setup", e));
    }
    _openWizard() {
      this.dispatchEvent(new CustomEvent("open-wizard", {
        bubbles: !0,
        composed: !0
      }));
    }
    render() {
      if (!this.hass) return F``;
      const e = this._activeTab;
      return F`
      <div class="setup-container">
        <nav class="setup-nav">
          ${Object.values(Ss).map(t => F`
              <button
                class="setup-nav-btn ${e === t ? "active" : ""}"
                @click="${() => this._selectTab(t)}"
              >
                ${Ca(zs[t], this.hass.language)}
              </button>
            `)}
          <button
            class="setup-nav-btn wizard-btn"
            @click="${this._openWizard}"
            title="${Ca("wizard.title", this.hass.language)}"
          >
            <ha-icon icon="mdi:creation"></ha-icon>
            ${Ca("wizard.open_button", this.hass.language)}
          </button>
        </nav>
        <div class="setup-content">${this._renderContent(e)}</div>
      </div>
    `;
    }
    _renderContent(e) {
      if (!this.hass) return F``;
      switch (e) {
        case Ss.WeatherLocation:
          return F`
          <smart-irrigation-view-general
            .hass="${this.hass}"
            .narrow="${this.narrow}"
            section="weather-location"
          ></smart-irrigation-view-general>
          <smart-irrigation-view-weather-data
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-weather-data>
        `;
        case Ss.Zones:
          return F`<smart-irrigation-view-zone-settings
          .hass="${this.hass}"
          .narrow="${this.narrow}"
          .path="${this.path}"
        ></smart-irrigation-view-zone-settings>`;
        case Ss.WhenToWater:
          return F`
          <smart-irrigation-view-general
            .hass="${this.hass}"
            .narrow="${this.narrow}"
            section="when-to-water"
          ></smart-irrigation-view-general>
          <smart-irrigation-view-schedules
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-schedules>
        `;
        case Ss.Advanced:
          return F`
          <smart-irrigation-view-modules
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-modules>
          <smart-irrigation-view-mappings
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-mappings>
        `;
        case Ss.Help:
          return this._renderHelp();
      }
    }
    _renderHelp() {
      return this.hass ? F`
      <ha-card
        header="${Ca("panels.help.cards.how-to-get-help.title", this.hass.language)}"
      >
        <div class="card-content">
          ${Ca("panels.help.cards.how-to-get-help.first-read-the", this.hass.language)}
          <a href="${"https://justchr.github.io/HAsmartirrigation/"}"
            >${Ca("panels.help.cards.how-to-get-help.wiki", this.hass.language)}</a
          >.
          ${Ca("panels.help.cards.how-to-get-help.if-you-still-need-help", this.hass.language)}
          <a
            href="https://community.home-assistant.io/t/smart-irrigation-save-water-by-precisely-watering-your-lawn-garden"
            >${Ca("panels.help.cards.how-to-get-help.community-forum", this.hass.language)}</a
          >
          ${Ca("panels.help.cards.how-to-get-help.or-open-a", this.hass.language)}
          <a href="${"https://github.com/JustChr/HAsmartirrigation/issues"}"
            >${Ca("panels.help.cards.how-to-get-help.github-issue", this.hass.language)}</a
          >
          (${Ca("panels.help.cards.how-to-get-help.english-only", this.hass.language)}).
        </div>
      </ha-card>
    ` : F``;
    }
    static get styles() {
      return h`
      ${ss}

      :host {
        display: block;
        width: 100%;
      }

      .setup-container {
        display: flex;
        flex-direction: column;
        width: 100%;
      }

      .setup-nav {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        padding: 8px 16px 0;
        border-bottom: 1px solid var(--divider-color);
        background: var(--card-background-color);
        position: sticky;
        top: 0;
        z-index: 1;
      }

      .setup-nav-btn {
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        color: var(--secondary-text-color);
        cursor: pointer;
        font-family: inherit;
        font-size: 0.8125rem;
        font-weight: 500;
        letter-spacing: 0.05em;
        padding: 8px 12px;
        text-transform: uppercase;
        transition:
          color 0.15s,
          border-color 0.15s;
        white-space: nowrap;
        margin-bottom: -1px;
      }

      .setup-nav-btn:hover {
        color: var(--primary-text-color);
      }

      .setup-nav-btn.active {
        border-bottom-color: var(--primary-color);
        color: var(--primary-color);
      }

      .setup-nav-btn.wizard-btn {
        margin-left: auto;
        color: var(--primary-color);
        border-bottom-color: transparent;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        --mdc-icon-size: 18px;
      }

      .setup-nav-btn.wizard-btn:hover {
        color: var(--primary-color);
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
      }

      .setup-content {
        padding-top: 4px;
      }

      .setup-content > * {
        display: block;
        width: 100%;
      }
    `;
    }
  };
  var As;
  s([pe({
    attribute: !1
  })], Es.prototype, "hass", void 0), s([pe({
    type: Boolean
  })], Es.prototype, "narrow", void 0), s([pe({
    attribute: !1
  })], Es.prototype, "path", void 0), Es = s([he("smart-irrigation-view-setup")], Es), function (e) {
    e[e.Welcome = 0] = "Welcome", e[e.Weather = 1] = "Weather", e[e.Module = 2] = "Module", e[e.Mapping = 3] = "Mapping", e[e.Zone = 4] = "Zone", e[e.Done = 5] = "Done";
  }(As || (As = {}));
  let Ts = class extends ce {
    constructor() {
      super(...arguments), this._step = As.Welcome, this._saving = !1, this._error = "", this._confirmClose = !1, this._siConfig = null, this._useWeather = !1, this._weatherService = ze, this._apiKey = "", this._weatherConfig = null, this._availableModules = [], this._selectedModuleIndex = 0, this._moduleConfig = {}, this._mappingName = "My Sensor Group", this._tempSource = Re, this._humiditySource = Re, this._precipSource = Re, this._zoneName = "My Zone", this._zoneSize = "", this._zoneThroughput = "", this._zoneEntity = "";
    }
    async connectedCallback() {
      super.connectedCallback(), await this._loadInitialData();
    }
    async _loadInitialData() {
      var e;
      if (this.hass) {
        try {
          const [t, i, a] = await Promise.all([Ga(this.hass), Xa(this.hass), ja(this.hass)]);
          this._availableModules = t, this._weatherConfig = i, this._siConfig = a, this._useWeather = i.use_weather_service, this._weatherService = null !== (e = i.weather_service) && void 0 !== e ? e : ze;
        } catch (e) {
          console.error("Wizard: failed to load initial data", e), this._error = Ia(e);
        }
        this.requestUpdate();
      }
    }
    _close() {
      this.dispatchEvent(new CustomEvent("wizard-close", {
        bubbles: !0,
        composed: !0
      }));
    }
    _navigate(e) {
      this.dispatchEvent(new CustomEvent("wizard-navigate", {
        detail: {
          page: e
        },
        bubbles: !0,
        composed: !0
      }));
    }
    async _next() {
      this._error = "";
      try {
        switch (this._saving = !0, this._step) {
          case As.Welcome:
            this._step = As.Weather;
            break;
          case As.Weather:
            await this._saveWeather(), this._step = As.Module;
            break;
          case As.Module:
            await this._saveModule(), this._step = As.Mapping;
            break;
          case As.Mapping:
            await this._saveMapping(), this._step = As.Zone;
            break;
          case As.Zone:
            await this._saveZone(), this._step = As.Done;
            break;
          case As.Done:
            this._close();
        }
      } catch (e) {
        this._error = e instanceof Error ? e.message : String(e);
      } finally {
        this._saving = !1, this.requestUpdate();
      }
    }
    _back() {
      this._step > As.Welcome && (this._step = this._step - 1, this._error = "");
    }
    get _canSkipCurrentStep() {
      return this._step === As.Weather;
    }
    _skipStep() {
      this._canSkipCurrentStep && this._step < As.Done && (this._step = this._step + 1, this._error = "");
    }
    async _saveWeather() {
      await Ya(this.hass, this._useWeather, this._useWeather ? this._weatherService : null, this._apiKey || null);
    }
    async _resolveSavedId(e, t) {
      if ("number" == typeof (null == e ? void 0 : e.id)) return e.id;
      try {
        const e = (await t()).map(e => e.id).filter(e => "number" == typeof e);
        return e.length ? Math.max(...e) : void 0;
      } catch (e) {
        return;
      }
    }
    async _saveModule() {
      if (0 === this._availableModules.length) throw new Error("No calculation module is available to configure. Cannot continue.");
      const e = this._availableModules[this._selectedModuleIndex],
        t = await qa(this.hass, {
          name: e.name,
          description: e.description,
          config: Object.assign(Object.assign({}, e.config), this._moduleConfig),
          schema: e.schema
        });
      if (this._savedModuleId = await this._resolveSavedId(t, () => Za(this.hass)), void 0 === this._savedModuleId) throw new Error("The calculation module was saved but could not be linked. Please try again.");
    }
    async _saveMapping() {
      const e = this._useWeather ? Re : qe,
        t = {
          [Be]: {
            [Ve]: this._tempSource
          },
          [Me]: {
            [Ve]: this._humiditySource
          },
          [Ne]: {
            [Ve]: this._precipSource
          }
        },
        i = ["Dewpoint", "Evapotranspiration", "Maximum Temperature", "Minimum Temperature", "Current Precipitation", "Pressure", "Solar Radiation", "Windspeed"];
      for (const a of i) t[a] = {
        [Ve]: e
      };
      const a = await Ka(this.hass, {
        name: this._mappingName,
        mappings: t
      });
      if (this._savedMappingId = await this._resolveSavedId(a, () => Va(this.hass)), void 0 === this._savedMappingId) throw new Error("The sensor group was saved but could not be linked. Please try again.");
    }
    async _saveZone() {
      if (!this._zoneName.trim()) throw new Error("Zone name is required");
      const e = parseFloat(this._zoneSize),
        t = parseFloat(this._zoneThroughput);
      if (!(e > 0)) throw new Error("Zone size must be greater than 0.");
      if (!(t > 0)) throw new Error("Throughput must be greater than 0 (zones can't water otherwise).");
      await Wa(this.hass, {
        name: this._zoneName.trim(),
        size: e,
        throughput: t,
        state: ts.Automatic,
        duration: 0,
        bucket: 0,
        delta: 0,
        explanation: "",
        multiplier: 1,
        module: this._savedModuleId,
        mapping: this._savedMappingId,
        lead_time: 0,
        linked_entity: this._zoneEntity || void 0
      });
    }
    render() {
      var e, t;
      const i = null !== (t = null === (e = this.hass) || void 0 === e ? void 0 : e.language) && void 0 !== t ? t : "en";
      return F`
      <div class="wizard-overlay" @click="${this._onOverlayClick}">
        <div
          class="wizard-dialog"
          @click="${e => e.stopPropagation()}"
        >
          <div class="wizard-header">
            <span class="wizard-title">${Ca("wizard.title", i)}</span>
            <button
              class="wizard-close-btn"
              @click="${this._close}"
              title="${Ca("wizard.close", i)}"
              aria-label="${Ca("wizard.close", i)}"
            >
              <ha-icon icon="mdi:close"></ha-icon>
            </button>
          </div>
          ${this._step !== As.Welcome && this._step !== As.Done ? F`<div class="wizard-stepper">${this._renderStepper()}</div>` : ""}
          <div class="wizard-body">
            ${this._renderStep(i)}
            ${this._error ? F`<div class="wizard-error">${this._error}</div>` : ""}
          </div>
          <div class="wizard-footer">${this._renderFooter(i)}</div>
          ${this._confirmClose ? F`
                <div class="wizard-confirm-close">
                  <div class="wizard-confirm-box">
                    <p>${Ca("wizard.confirm_close.body", i)}</p>
                    <div class="wizard-confirm-actions">
                      <button
                        class="wizard-btn secondary"
                        @click="${() => {
        this._confirmClose = !1;
      }}"
                      >
                        ${Ca("wizard.confirm_close.keep", i)}
                      </button>
                      <button
                        class="wizard-btn primary"
                        @click="${() => {
        this._confirmClose = !1, this._close();
      }}"
                      >
                        ${Ca("wizard.confirm_close.close", i)}
                      </button>
                    </div>
                  </div>
                </div>
              ` : ""}
        </div>
      </div>
    `;
    }
    _onOverlayClick(e) {
      e.target === e.currentTarget && (this._step > As.Welcome && this._step < As.Done ? this._confirmClose = !0 : this._close());
    }
    _renderStepper() {
      var e, t;
      const i = null !== (t = null === (e = this.hass) || void 0 === e ? void 0 : e.language) && void 0 !== t ? t : "en",
        a = [Ca("wizard.stepper.weather", i), Ca("wizard.stepper.module", i), Ca("wizard.stepper.mapping", i), Ca("wizard.stepper.zone", i)];
      return F`
      ${a.map((e, t) => {
        const i = t + 1,
          s = this._step === i,
          n = this._step > i;
        return F`
          <div
            class="stepper-step ${s ? "active" : ""} ${n ? "done" : ""}"
          >
            <div class="stepper-circle">${n ? "✓" : i}</div>
            <span class="stepper-label">${e}</span>
          </div>
          ${t < a.length - 1 ? F`<div class="stepper-line ${n ? "done" : ""}"></div>` : ""}
        `;
      })}
    `;
    }
    _renderStep(e) {
      switch (this._step) {
        case As.Welcome:
          return this._renderWelcome(e);
        case As.Weather:
          return this._renderWeather(e);
        case As.Module:
          return this._renderModule(e);
        case As.Mapping:
          return this._renderMapping(e);
        case As.Zone:
          return this._renderZone(e);
        case As.Done:
          return this._renderDone(e);
        default:
          return F``;
      }
    }
    _renderFooter(e) {
      return this._step === As.Done ? F`` : F`
      <div class="footer-left">
        ${this._step > As.Welcome ? F`<button
              class="wizard-btn secondary"
              @click="${this._back}"
              ?disabled="${this._saving}"
            >
              ${Ca("wizard.back", e)}
            </button>` : ""}
        ${this._canSkipCurrentStep ? F`<button
              class="wizard-btn ghost"
              @click="${this._skipStep}"
              ?disabled="${this._saving}"
            >
              ${Ca("wizard.skip_step", e)}
            </button>` : ""}
      </div>
      <button
        class="wizard-btn primary"
        @click="${this._next}"
        ?disabled="${this._saving}"
      >
        ${this._saving ? Ca("common.saving-messages.saving", e) : this._step === As.Welcome || this._step < As.Zone ? Ca("wizard.next", e) : Ca("wizard.finish", e)}
      </button>
    `;
    }
    _renderWelcome(e) {
      return F`
      <h2 class="step-title">
        ${Ca("wizard.steps.welcome.title", e)}
      </h2>
      <p class="step-desc">${Ca("wizard.steps.welcome.intro", e)}</p>
      <ul class="step-list">
        <li>① ${Ca("wizard.steps.welcome.step1_label", e)}</li>
        <li>② ${Ca("wizard.steps.welcome.step2_label", e)}</li>
        <li>③ ${Ca("wizard.steps.welcome.step3_label", e)}</li>
        <li>④ ${Ca("wizard.steps.welcome.step4_label", e)}</li>
      </ul>
      <p class="step-tip">${Ca("wizard.steps.welcome.tip", e)}</p>
    `;
    }
    _renderWeather(e) {
      return F`
      <h2 class="step-title">
        ${Ca("wizard.steps.weather.title", e)}
      </h2>
      <p class="step-desc">
        ${Ca("wizard.steps.weather.description", e)}
      </p>

      <si-weather-source-config
        .hass="${this.hass}"
        .useWeather="${this._useWeather}"
        .service="${this._weatherService}"
        .apiKey="${this._apiKey}"
        .weatherConfig="${this._weatherConfig}"
        @useweather-changed="${e => {
        this._useWeather = e.detail.value;
      }}"
        @service-changed="${e => {
        this._weatherService = e.detail.value;
      }}"
        @apikey-changed="${e => {
        this._apiKey = e.detail.value;
      }}"
      ></si-weather-source-config>
    `;
    }
    _renderModule(e) {
      if (0 === this._availableModules.length) return F`
        <h2 class="step-title">
          ${Ca("wizard.steps.module.title", e)}
        </h2>
        <p class="step-desc">
          ${Ca("wizard.steps.module.no_modules", e)}
        </p>
      `;
      const t = this._availableModules[this._selectedModuleIndex];
      return F`
      <h2 class="step-title">${Ca("wizard.steps.module.title", e)}</h2>
      <p class="step-desc">
        ${Ca("wizard.steps.module.description", e)}
      </p>

      <si-field
        label="${Ca("wizard.steps.module.pick_label", e)}"
        required
      >
        <select
          class="wizard-input"
          @change="${e => {
        this._selectedModuleIndex = parseInt(e.target.value), this._moduleConfig = {};
      }}"
        >
          ${this._availableModules.map((e, t) => F`
              <option
                value="${t}"
                ?selected="${t === this._selectedModuleIndex}"
              >
                ${e.name}
              </option>
            `)}
        </select>
      </si-field>

      ${(null == t ? void 0 : t.description) ? F`<p class="module-desc">${t.description}</p>` : ""}
      ${(null == t ? void 0 : t.schema) && Array.isArray(t.schema) && t.schema.length > 0 ? F`
            <div class="schema-fields">
              ${t.schema.map(e => this._renderModuleField(e.name, e))}
            </div>
          ` : ""}
    `;
    }
    _renderModuleField(e, t) {
      var i, a;
      const s = e.replace(/_/g, " ").replace(/\b\w/g, e => e.toUpperCase()),
        n = null !== (a = null !== (i = this._moduleConfig[e]) && void 0 !== i ? i : t.default) && void 0 !== a ? a : "",
        r = t.description;
      return "boolean" === t.type ? F`
        <si-field label="${s}" help="${null != r ? r : ""}">
          <ha-switch
            .checked="${Boolean(n)}"
            @change="${t => {
        this._moduleConfig = Object.assign(Object.assign({}, this._moduleConfig), {
          [e]: t.target.checked
        });
      }}"
          ></ha-switch>
        </si-field>
      ` : "select" === t.type && t.options ? F`
        <si-field label="${s}" help="${null != r ? r : ""}">
          <select
            class="wizard-input"
            @change="${t => {
        this._moduleConfig = Object.assign(Object.assign({}, this._moduleConfig), {
          [e]: t.target.value
        });
      }}"
          >
            ${t.options.map(([e, t]) => F`<option
                  value="${e}"
                  ?selected="${e === String(n)}"
                >
                  ${t}
                </option>`)}
          </select>
        </si-field>
      ` : F`
      <si-field label="${s}" help="${null != r ? r : ""}">
        <input
          type="${"float" === t.type || "integer" === t.type ? "number" : "text"}"
          class="wizard-input"
          step="${"float" === t.type ? "0.01" : "1"}"
          .value="${String(n)}"
          @input="${i => {
        const a = i.target.value,
          s = "float" === t.type ? parseFloat(a) : "integer" === t.type ? parseInt(a) : a;
        this._moduleConfig = Object.assign(Object.assign({}, this._moduleConfig), {
          [e]: s
        });
      }}"
        />
      </si-field>
    `;
    }
    _renderMapping(e) {
      const t = [{
          value: Re,
          label: Ca("wizard.steps.mapping.use_weather_service", e)
        }, {
          value: "sensor",
          label: Ca("wizard.steps.mapping.use_sensor", e)
        }, {
          value: "static",
          label: Ca("wizard.steps.mapping.use_static", e)
        }, {
          value: qe,
          label: Ca("wizard.steps.mapping.use_none", e)
        }],
        i = (i, a, s) => F`
      <si-field
        label="${Ca("wizard.steps.mapping.source_label", e)} ${i}"
      >
        <select
          class="wizard-input"
          @change="${e => s(e.target.value)}"
        >
          ${t.map(e => F`<option value="${e.value}" ?selected="${e.value === a}">
                ${e.label}
              </option>`)}
        </select>
      </si-field>
    `;
      return F`
      <h2 class="step-title">
        ${Ca("wizard.steps.mapping.title", e)}
      </h2>
      <p class="step-desc">
        ${Ca("wizard.steps.mapping.description", e)}
      </p>

      <si-field
        label="${Ca("wizard.steps.mapping.name_label", e)}"
        required
      >
        <input
          type="text"
          class="wizard-input"
          .value="${this._mappingName}"
          @input="${e => {
        this._mappingName = e.target.value;
      }}"
        />
      </si-field>

      ${i(Ca("panels.mappings.cards.mapping.items.temperature", e) || "Temperature", this._tempSource, e => {
        this._tempSource = e, this.requestUpdate();
      })}
      ${i(Ca("panels.mappings.cards.mapping.items.humidity", e) || "Humidity", this._humiditySource, e => {
        this._humiditySource = e, this.requestUpdate();
      })}
      ${i(Ca("panels.mappings.cards.mapping.items.precipitation", e) || "Precipitation", this._precipSource, e => {
        this._precipSource = e, this.requestUpdate();
      })}

      <p class="step-tip">
        ${Ca("wizard.steps.mapping.description", e)}
      </p>
    `;
    }
    _renderZone(e) {
      var t;
      const i = "imperial" !== (null === (t = this._siConfig) || void 0 === t ? void 0 : t.units);
      return F`
      <h2 class="step-title">${Ca("wizard.steps.zone.title", e)}</h2>
      <p class="step-desc">
        ${Ca("wizard.steps.zone.description", e)}
      </p>

      <si-zone-form
        .hass="${this.hass}"
        .metric="${i}"
        .name="${this._zoneName}"
        .size="${this._zoneSize}"
        .throughput="${this._zoneThroughput}"
        .linkedEntity="${this._zoneEntity}"
        showEntity
        @name-changed="${e => {
        this._zoneName = e.detail.value;
      }}"
        @size-changed="${e => {
        this._zoneSize = e.detail.value;
      }}"
        @throughput-changed="${e => {
        this._zoneThroughput = e.detail.value;
      }}"
        @entity-changed="${e => {
        this._zoneEntity = e.detail.value;
      }}"
      ></si-zone-form>
    `;
    }
    _renderDone(e) {
      return F`
      <div class="done-wrapper">
        <div class="done-icon">
          <ha-icon icon="mdi:check-circle"></ha-icon>
        </div>
        <h2 class="step-title">${Ca("wizard.steps.done.title", e)}</h2>
        <p class="step-desc">
          ${Ca("wizard.steps.done.description", e)}
        </p>
        <ul class="step-list">
          <li>${Ca("wizard.steps.done.tip1", e)}</li>
          <li>${Ca("wizard.steps.done.tip2", e)}</li>
          <li>${Ca("wizard.steps.done.tip3", e)}</li>
        </ul>
        <div class="done-actions">
          <button
            class="wizard-btn primary"
            @click="${() => {
        this._close(), this._navigate("zones");
      }}"
          >
            ${Ca("wizard.steps.done.go_zones", e)}
          </button>
          <button
            class="wizard-btn secondary"
            @click="${() => {
        this._close(), this._navigate("setup");
      }}"
          >
            ${Ca("wizard.steps.done.go_setup", e)}
          </button>
        </div>
      </div>
    `;
    }
    static get styles() {
      return h`
      ${ss}

      :host {
        display: block;
      }

      /* Full-screen overlay */
      .wizard-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.55);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 16px;
        box-sizing: border-box;
      }

      /* Dialog box */
      .wizard-dialog {
        position: relative;
        background: var(--card-background-color);
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        display: flex;
        flex-direction: column;
        max-height: 90vh;
        width: 100%;
        max-width: 540px;
        overflow: hidden;
      }

      /* Header */
      .wizard-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        border-bottom: 1px solid var(--divider-color);
        flex-shrink: 0;
      }

      .wizard-title {
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }

      .wizard-close-btn {
        background: none;
        border: none;
        cursor: pointer;
        color: var(--secondary-text-color);
        display: inline-flex;
        align-items: center;
        padding: 4px 8px;
        border-radius: 4px;
        transition: background 0.15s;
        --mdc-icon-size: 20px;
      }

      .wizard-close-btn:hover {
        background: var(--secondary-background-color);
        color: var(--primary-text-color);
      }

      /* Confirm-before-close overlay (UX N4) */
      .wizard-confirm-close {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.45);
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        padding: 16px;
        box-sizing: border-box;
      }

      .wizard-confirm-box {
        background: var(--card-background-color);
        border-radius: 10px;
        padding: 20px;
        max-width: 360px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
      }

      .wizard-confirm-box p {
        margin: 0 0 16px;
        font-size: 0.9rem;
        color: var(--primary-text-color);
        line-height: 1.5;
      }

      .wizard-confirm-actions {
        display: flex;
        gap: 12px;
        justify-content: flex-end;
      }

      /* Stepper */
      .wizard-stepper {
        display: flex;
        align-items: center;
        padding: 12px 20px;
        border-bottom: 1px solid var(--divider-color);
        flex-shrink: 0;
        overflow-x: auto;
      }

      .stepper-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        flex-shrink: 0;
      }

      .stepper-circle {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        border: 2px solid var(--divider-color);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--secondary-text-color);
        background: var(--card-background-color);
        transition: all 0.2s;
      }

      .stepper-step.active .stepper-circle {
        border-color: var(--primary-color);
        color: var(--primary-color);
      }

      .stepper-step.done .stepper-circle {
        border-color: var(--primary-color);
        background: var(--primary-color);
        color: white;
      }

      .stepper-label {
        font-size: 0.68rem;
        color: var(--secondary-text-color);
        white-space: nowrap;
      }

      .stepper-step.active .stepper-label {
        color: var(--primary-color);
        font-weight: 600;
      }

      .stepper-line {
        flex: 1;
        height: 2px;
        background: var(--divider-color);
        min-width: 16px;
        margin-bottom: 18px;
        transition: background 0.2s;
      }

      .stepper-line.done {
        background: var(--primary-color);
      }

      /* Body */
      .wizard-body {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
      }

      .step-title {
        margin: 0 0 8px;
        font-size: 1.05rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }

      .step-desc {
        margin: 0 0 16px;
        font-size: 0.875rem;
        color: var(--secondary-text-color);
        line-height: 1.5;
      }

      .step-list {
        margin: 0 0 16px;
        padding-left: 20px;
        font-size: 0.875rem;
        color: var(--secondary-text-color);
        line-height: 1.8;
      }

      .step-tip {
        font-size: 0.8rem;
        color: var(--secondary-text-color);
        font-style: italic;
        margin: 8px 0 0;
      }

      .module-desc {
        font-size: 0.83rem;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border-radius: 4px;
        padding: 8px 12px;
        margin: 8px 0;
        line-height: 1.45;
      }

      .schema-fields {
        margin-top: 8px;
      }

      /* Common input */
      .wizard-input {
        width: 100%;
        background: var(--input-fill-color, var(--secondary-background-color));
        border: 1px solid var(--input-ink-color, var(--secondary-text-color));
        border-radius: 4px;
        color: var(--primary-text-color);
        padding: 6px 10px;
        font-family: inherit;
        font-size: 0.9375rem;
        box-sizing: border-box;
        height: 36px;
      }

      .wizard-input:focus {
        border-color: var(--primary-color);
        outline: none;
      }

      .wizard-input.flex1 {
        flex: 1;
      }

      select.wizard-input {
        cursor: pointer;
      }

      /* API key row */
      .api-row {
        display: flex;
        gap: 8px;
        align-items: center;
        flex-wrap: wrap;
        margin-top: 4px;
      }

      .api-badge {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 10px;
        margin-bottom: 4px;
      }

      .api-badge.configured {
        background: rgba(76, 175, 80, 0.15);
        color: #2e7d32;
      }

      .test-result {
        font-size: 0.83rem;
        font-weight: 500;
        margin-top: 6px;
        padding: 5px 10px;
        border-radius: 4px;
      }

      .test-result.success {
        background: rgba(76, 175, 80, 0.12);
        color: #2e7d32;
      }

      .test-result.error {
        background: rgba(176, 0, 32, 0.1);
        color: var(--error-color, #b00020);
      }

      .info-note {
        font-size: 0.83rem;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border-radius: 4px;
        padding: 8px 12px;
        margin-top: 8px;
      }

      /* Done step */
      .done-wrapper {
        text-align: center;
        padding: 8px 0;
      }

      .done-icon {
        color: #4caf50;
        margin-bottom: 12px;
        --mdc-icon-size: 56px;
      }

      .done-actions {
        display: flex;
        gap: 12px;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 24px;
      }

      /* Error */
      .wizard-error {
        background: rgba(176, 0, 32, 0.1);
        color: var(--error-color, #b00020);
        border-radius: 4px;
        padding: 8px 12px;
        font-size: 0.875rem;
        margin-top: 12px;
      }

      /* Footer */
      .wizard-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 20px;
        border-top: 1px solid var(--divider-color);
        flex-shrink: 0;
        gap: 8px;
      }

      .footer-left {
        display: flex;
        gap: 8px;
        align-items: center;
      }

      /* Buttons */
      .wizard-btn {
        background: var(--primary-color);
        border: none;
        border-radius: 4px;
        color: var(--text-primary-color, white);
        cursor: pointer;
        font-family: inherit;
        font-size: 0.875rem;
        font-weight: 500;
        letter-spacing: 0.04em;
        padding: 8px 18px;
        text-transform: uppercase;
        transition: opacity 0.15s;
        white-space: nowrap;
      }

      .wizard-btn:hover {
        opacity: 0.9;
      }

      .wizard-btn:disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }

      .wizard-btn.secondary {
        background: transparent;
        border: 1px solid var(--primary-color);
        color: var(--primary-color);
      }

      .wizard-btn.secondary:hover {
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
        opacity: 1;
      }

      .wizard-btn.ghost {
        background: transparent;
        border: none;
        color: var(--secondary-text-color);
        font-size: 0.8rem;
        text-transform: none;
        letter-spacing: 0;
        padding: 8px 10px;
      }

      .wizard-btn.ghost:hover {
        color: var(--primary-text-color);
        background: var(--secondary-background-color);
        opacity: 1;
      }
    `;
    }
  };
  s([pe({
    attribute: !1
  })], Ts.prototype, "hass", void 0), s([ge()], Ts.prototype, "_step", void 0), s([ge()], Ts.prototype, "_saving", void 0), s([ge()], Ts.prototype, "_error", void 0), s([ge()], Ts.prototype, "_confirmClose", void 0), s([ge()], Ts.prototype, "_siConfig", void 0), s([ge()], Ts.prototype, "_useWeather", void 0), s([ge()], Ts.prototype, "_weatherService", void 0), s([ge()], Ts.prototype, "_apiKey", void 0), s([ge()], Ts.prototype, "_weatherConfig", void 0), s([ge()], Ts.prototype, "_availableModules", void 0), s([ge()], Ts.prototype, "_selectedModuleIndex", void 0), s([ge()], Ts.prototype, "_moduleConfig", void 0), s([ge()], Ts.prototype, "_mappingName", void 0), s([ge()], Ts.prototype, "_tempSource", void 0), s([ge()], Ts.prototype, "_humiditySource", void 0), s([ge()], Ts.prototype, "_precipSource", void 0), s([ge()], Ts.prototype, "_zoneName", void 0), s([ge()], Ts.prototype, "_zoneSize", void 0), s([ge()], Ts.prototype, "_zoneThroughput", void 0), s([ge()], Ts.prototype, "_zoneEntity", void 0), Ts = s([he("si-setup-wizard")], Ts);
  const Cs = ss;
  var Os;
  !function (e) {
    e.Zones = "zones", e.Setup = "setup";
  }(Os || (Os = {})), e.SmartIrrigationPanel = class extends ce {
    constructor() {
      super(...arguments), this._wizardOpen = !1, this._updateScheduled = !1, this._lastNavigationTime = 0, this._navigationThrottleDelay = 100;
    }
    _scheduleUpdate() {
      this._updateScheduled || (this._updateScheduled = !0, requestAnimationFrame(() => {
        this._updateScheduled = !1, this.requestUpdate();
      }));
    }
    async firstUpdated() {
      const e = is().page;
      Object.values(Os).includes(e) || Na(0, as(Os.Zones)), window.addEventListener("location-changed", () => {
        if (!window.location.pathname.includes("smart-irrigation")) return;
        const e = performance.now();
        e - this._lastNavigationTime < this._navigationThrottleDelay || (this._lastNavigationTime = e, this._scheduleUpdate());
      }), be().then(() => {
        this._scheduleUpdate();
      }).catch(e => {
        console.error("Failed to load HA form elements:", e), this._scheduleUpdate();
      });
    }
    _ensureLanguage() {
      this.hass && !Ta(this.hass.language) && function (e) {
        const t = Aa(e);
        return Ta(e) ? Promise.resolve() : (Ea[t] || (Ea[t] = fetch(`/smart_irrigation_static/languages/${t}.json`).then(e => e.ok ? e.json() : Promise.reject(e.status)).then(e => {
          za[t] = e;
        }).catch(() => {
          za[t] = za.en;
        })), Ea[t]);
      }(this.hass.language).then(() => this.requestUpdate());
    }
    render() {
      if (this.hass && !Ta(this.hass.language)) return this._ensureLanguage(), F``;
      const e = is(),
        t = !!customElements.get("ha-tab-group"),
        i = !!customElements.get("ha-tab-group-tab");
      return F`
      <div class="header">
        <div class="toolbar">
          <ha-menu-button
            .hass=${this.hass}
            .narrow=${this.narrow}
          ></ha-menu-button>
          <div class="main-title">${Ca("title", this.hass.language)}</div>
          <div class="version">${ye}</div>
        </div>

        ${t && i ? F`
              <ha-tab-group @wa-tab-show=${this.handlePageSelected}>
                ${Object.values(Os).map(t => F`
                    <ha-tab-group-tab
                      slot="nav"
                      panel="${t}"
                      .active=${e.page === t}
                    >
                      ${Ca(`panels.${t}.title`, this.hass.language)}
                    </ha-tab-group-tab>
                  `)}
              </ha-tab-group>
            ` : F`
              <div class="custom-tabs">
                ${Object.values(Os).map(t => F`
                    <button
                      class="custom-tab ${e.page === t ? "active" : ""}"
                      @click=${() => this.navigateToPage(t)}
                    >
                      ${Ca(`panels.${t}.title`, this.hass.language)}
                    </button>
                  `)}
              </div>
            `}
      </div>
      <div class="view">${this.getView(e)}</div>
      ${this._wizardOpen ? F`
            <si-setup-wizard
              .hass="${this.hass}"
              @wizard-close="${() => {
        this._wizardOpen = !1;
      }}"
              @wizard-navigate="${e => {
        var t, i;
        const a = null !== (i = null === (t = e.detail) || void 0 === t ? void 0 : t.page) && void 0 !== i ? i : "zones";
        this._wizardOpen = !1, this.navigateToPage(a);
      }}"
            ></si-setup-wizard>
          ` : ""}
    `;
    }
    getView(e) {
      switch (e.page) {
        case "zones":
        default:
          return F`
          <smart-irrigation-view-zones
            .hass=${this.hass}
            .narrow=${this.narrow}
            .path=${e}
            @open-wizard="${() => {
            this._wizardOpen = !0;
          }}"
          ></smart-irrigation-view-zones>
        `;
        case "setup":
          return F`
          <smart-irrigation-view-setup
            .hass=${this.hass}
            .narrow=${this.narrow}
            .path=${e}
            @open-wizard="${() => {
            this._wizardOpen = !0;
          }}"
          ></smart-irrigation-view-setup>
        `;
      }
    }
    navigateToPage(e) {
      if (e !== is().page) {
        const t = as(e);
        Na(0, t), this.requestUpdate();
      } else scrollTo(0, 0);
    }
    handlePageSelected(e) {
      const t = e.detail.name;
      if (t !== is().page) {
        const e = as(t);
        Na(0, e), this.requestUpdate();
      } else scrollTo(0, 0);
    }
    static get styles() {
      return [Cs, h`
        :host {
          color: var(--primary-text-color);
          --paper-card-header-color: var(--primary-text-color);
        }
        .header {
          background-color: var(--app-header-background-color);
          color: var(--app-header-text-color, white);
          border-bottom: var(--app-header-border-bottom, none);
        }
        .toolbar {
          height: var(--header-height);
          display: flex;
          align-items: center;
          font-size: 20px;
          padding: 0 16px;
          font-weight: 400;
          box-sizing: border-box;
        }
        .main-title {
          margin: 0 0 0 24px;
          line-height: 20px;
          flex-grow: 1;
        }
        ha-tab-group {
          margin-left: max(env(safe-area-inset-left), 24px);
          margin-right: max(env(safe-area-inset-right), 24px);
          --ha-tab-active-text-color: var(--app-header-text-color, white);
          --ha-tab-indicator-color: var(--app-header-text-color, white);
          --ha-tab-track-color: transparent;
        }

        .custom-tabs {
          display: flex;
          margin-left: max(env(safe-area-inset-left), 24px);
          margin-right: max(env(safe-area-inset-right), 24px);
          border-bottom: 1px solid
            rgba(
              var(--rgb-app-header-text-color, var(--rgb-text-primary-color)),
              0.12
            );
          overflow-x: auto;
        }

        .custom-tab {
          background: transparent;
          border: none;
          color: rgba(
            var(--rgb-app-header-text-color, var(--rgb-text-primary-color)),
            0.7
          );
          cursor: pointer;
          font-family: inherit;
          font-size: 14px;
          font-weight: 500;
          line-height: 48px;
          margin: 0;
          min-width: 72px;
          outline: none;
          padding: 0 12px;
          position: relative;
          text-transform: uppercase;
          transition: color 0.15s ease-in-out;
          white-space: nowrap;
          letter-spacing: 0.1em;
        }

        .custom-tab:hover {
          color: var(--app-header-text-color, white);
          background-color: rgba(
            var(--rgb-app-header-text-color, var(--rgb-text-primary-color)),
            0.04
          );
        }

        .custom-tab.active {
          color: var(--app-header-text-color, white);
        }

        .custom-tab.active::after {
          background-color: var(--app-header-text-color, white);
          bottom: 0;
          content: "";
          height: 2px;
          left: 0;
          position: absolute;
          right: 0;
        }

        .view {
          height: calc(100vh - 112px);
          display: flex;
          justify-content: center;
          overflow-y: auto;
        }

        .view > * {
          width: 100%;
          /* Use the available width on wide screens; cap only so text lines
             don't get uncomfortably long on ultra-wide monitors. */
          max-width: 1400px;
        }

        .view > *:last-child {
          margin-bottom: 20px;
        }

        .version {
          font-size: 14px;
          font-weight: 500;
          color: rgba(var(--rgb-text-primary-color), 0.9);
        }
      `];
    }
  }, s([pe({
    attribute: !1
  })], e.SmartIrrigationPanel.prototype, "hass", void 0), s([pe({
    type: Boolean,
    reflect: !0
  })], e.SmartIrrigationPanel.prototype, "narrow", void 0), s([ge()], e.SmartIrrigationPanel.prototype, "_wizardOpen", void 0), e.SmartIrrigationPanel = s([he("smart-irrigation")], e.SmartIrrigationPanel);
  let Hs = class extends ce {
    async showDialog(e) {
      this._params = e, await this.updateComplete;
    }
    async closeDialog() {
      this._params = void 0;
    }
    render() {
      return this._params ? F`
      <ha-dialog
        open
        .heading=${!0}
        @closed=${this.closeDialog}
        @close-dialog=${this.closeDialog}
      >
        <div slot="heading">
          <ha-header-bar>
            <ha-icon-button
              slot="navigationIcon"
              dialogAction="cancel"
              .path=${Ba}
            ></ha-icon-button>
            <span class="errortitle" slot="title">
              ${this.hass.localize("state_badge.default.error")}
            </span>
          </ha-header-bar>
        </div>
        <div class="wrapper">${this._params.error || ""}</div>

        <ha-dialog-footer slot="footer">
          <ha-button
            slot="primaryAction"
            appearance="accent"
            @click=${this.closeDialog}
            dialogAction="close"
          >
            ${this.hass.localize("ui.dialogs.generic.ok")}
          </ha-button>
        </ha-dialog-footer>
      </ha-dialog>
    ` : F``;
    }
    static get styles() {
      return h`
      div.wrapper {
        color: var(--primary-text-color);
      }
      span.errortitle {
        font-size: 2em;
        font-weight: bold;
        vertical-align: bottom;
      }
    `;
    }
  };
  s([pe({
    attribute: !1
  })], Hs.prototype, "hass", void 0), s([ge()], Hs.prototype, "_params", void 0), Hs = s([he("error-dialog")], Hs);
  var Ls = Object.freeze({
    __proto__: null,
    get ErrorDialog() {
      return Hs;
    }
  });
  Object.defineProperty(e, "__esModule", {
    value: !0
  });
}({});
