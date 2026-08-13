!function(e){"use strict";function t(e,t,i,s){var a,n=arguments.length,o=n<3?t:null===s?s=Object.getOwnPropertyDescriptor(t,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)o=Reflect.decorate(e,t,i,s);else for(var r=e.length-1;r>=0;r--)(a=e[r])&&(o=(n<3?a(o):n>3?a(t,i,o):a(t,i))||o);return n>3&&o&&Object.defineProperty(t,i,o),o}"function"==typeof SuppressedError&&SuppressedError;
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const i=globalThis,s=i.ShadowRoot&&(void 0===i.ShadyCSS||i.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,a=Symbol(),n=new WeakMap;let o=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==a)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(s&&void 0===e){const i=void 0!==t&&1===t.length;i&&(e=n.get(t)),void 0===e&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&n.set(t,e))}return e}toString(){return this.cssText}};const r=(e,...t)=>{const i=1===e.length?e[0]:t.reduce((t,i,s)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+e[s+1],e[0]);return new o(i,e,a)},l=s?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const i of e.cssRules)t+=i.cssText;return(e=>new o("string"==typeof e?e:e+"",void 0,a))(t)})(e):e,{is:d,defineProperty:c,getOwnPropertyDescriptor:h,getOwnPropertyNames:u,getOwnPropertySymbols:p,getPrototypeOf:g}=Object,m=globalThis,v=m.trustedTypes,f=v?v.emptyScript:"",_=m.reactiveElementPolyfillSupport,b=(e,t)=>e,y={toAttribute(e,t){switch(t){case Boolean:e=e?f:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute(e,t){let i=e;switch(t){case Boolean:i=null!==e;break;case Number:i=null===e?null:Number(e);break;case Object:case Array:try{i=JSON.parse(e)}catch(e){i=null}}return i}},w=(e,t)=>!d(e,t),$={attribute:!0,type:String,converter:y,reflect:!1,useDefault:!1,hasChanged:w};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */Symbol.metadata??=Symbol("metadata"),m.litPropertyMetadata??=new WeakMap;let x=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=$){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(e,i,t);void 0!==s&&c(this.prototype,e,s)}}static getPropertyDescriptor(e,t,i){const{get:s,set:a}=h(this.prototype,e)??{get(){return this[t]},set(e){this[t]=e}};return{get:s,set(t){const n=s?.call(this);a?.call(this,t),this.requestUpdate(e,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??$}static _$Ei(){if(this.hasOwnProperty(b("elementProperties")))return;const e=g(this);e.finalize(),void 0!==e.l&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(b("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(b("properties"))){const e=this.properties,t=[...u(e),...p(e)];for(const i of t)this.createProperty(i,e[i])}const e=this[Symbol.metadata];if(null!==e){const t=litPropertyMetadata.get(e);if(void 0!==t)for(const[e,i]of t)this.elementProperties.set(e,i)}this._$Eh=new Map;for(const[e,t]of this.elementProperties){const i=this._$Eu(e,t);void 0!==i&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const i=new Set(e.flat(1/0).reverse());for(const e of i)t.unshift(l(e))}else void 0!==e&&t.push(l(e));return t}static _$Eu(e,t){const i=t.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof e?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),void 0!==this.renderRoot&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((e,t)=>{if(s)e.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(const s of t){const t=document.createElement("style"),a=i.litNonce;void 0!==a&&t.setAttribute("nonce",a),t.textContent=s.cssText,e.appendChild(t)}})(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){const i=this.constructor.elementProperties.get(e),s=this.constructor._$Eu(e,i);if(void 0!==s&&!0===i.reflect){const a=(void 0!==i.converter?.toAttribute?i.converter:y).toAttribute(t,i.type);this._$Em=e,null==a?this.removeAttribute(s):this.setAttribute(s,a),this._$Em=null}}_$AK(e,t){const i=this.constructor,s=i._$Eh.get(e);if(void 0!==s&&this._$Em!==s){const e=i.getPropertyOptions(s),a="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==e.converter?.fromAttribute?e.converter:y;this._$Em=s;const n=a.fromAttribute(t,e.type);this[s]=n??this._$Ej?.get(s)??n,this._$Em=null}}requestUpdate(e,t,i,s=!1,a){if(void 0!==e){const n=this.constructor;if(!1===s&&(a=this[e]),i??=n.getPropertyOptions(e),!((i.hasChanged??w)(a,t)||i.useDefault&&i.reflect&&a===this._$Ej?.get(e)&&!this.hasAttribute(n._$Eu(e,i))))return;this.C(e,t,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:s,wrapped:a},n){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,n??t??this[e]),!0!==a||void 0!==n)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),!0===s&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const e=this.scheduleUpdate();return null!=e&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[e,t]of this._$Ep)this[e]=t;this._$Ep=void 0}const e=this.constructor.elementProperties;if(e.size>0)for(const[t,i]of e){const{wrapped:e}=i,s=this[t];!0!==e||this._$AL.has(t)||void 0===s||this.C(t,void 0,i,s)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(e=>e.hostUpdate?.()),this.update(t)):this._$EM()}catch(t){throw e=!1,this._$EM(),t}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(e){}firstUpdated(e){}};x.elementStyles=[],x.shadowRootOptions={mode:"open"},x[b("elementProperties")]=new Map,x[b("finalized")]=new Map,_?.({ReactiveElement:x}),(m.reactiveElementVersions??=[]).push("2.1.2");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
<<<<<<< HEAD
const k=globalThis,z=e=>e,S=k.trustedTypes,A=S?S.createPolicy("lit-html",{createHTML:e=>e}):void 0,E="$lit$",C=`lit$${Math.random().toFixed(9).slice(2)}$`,T="?"+C,O=`<${T}>`,H=document,D=()=>H.createComment(""),M=e=>null===e||"object"!=typeof e&&"function"!=typeof e,I=Array.isArray,N="[ \t\n\f\r]",P=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,L=/-->/g,R=/>/g,B=RegExp(`>|${N}(?:([^\\s"'>=/]+)(${N}*=${N}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),U=/'/g,j=/"/g,F=/^(?:script|style|textarea|title)$/i,Z=e=>(t,...i)=>({_$litType$:e,strings:t,values:i}),W=Z(1),q=Z(2),G=Symbol.for("lit-noChange"),K=Symbol.for("lit-nothing"),V=new WeakMap,Y=H.createTreeWalker(H,129);function X(e,t){if(!I(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==A?A.createHTML(t):t}const J=(e,t)=>{const i=e.length-1,s=[];let a,n=2===t?"<svg>":3===t?"<math>":"",o=P;for(let t=0;t<i;t++){const i=e[t];let r,l,d=-1,c=0;for(;c<i.length&&(o.lastIndex=c,l=o.exec(i),null!==l);)c=o.lastIndex,o===P?"!--"===l[1]?o=L:void 0!==l[1]?o=R:void 0!==l[2]?(F.test(l[2])&&(a=RegExp("</"+l[2],"g")),o=B):void 0!==l[3]&&(o=B):o===B?">"===l[0]?(o=a??P,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,r=l[1],o=void 0===l[3]?B:'"'===l[3]?j:U):o===j||o===U?o=B:o===L||o===R?o=P:(o=B,a=void 0);const h=o===B&&e[t+1].startsWith("/>")?" ":"";n+=o===P?i+O:d>=0?(s.push(r),i.slice(0,d)+E+i.slice(d)+C+h):i+C+(-2===d?t:h)}return[X(e,n+(e[i]||"<?>")+(2===t?"</svg>":3===t?"</math>":"")),s]};class Q{constructor({strings:e,_$litType$:t},i){let s;this.parts=[];let a=0,n=0;const o=e.length-1,r=this.parts,[l,d]=J(e,t);if(this.el=Q.createElement(l,i),Y.currentNode=this.el.content,2===t||3===t){const e=this.el.content.firstChild;e.replaceWith(...e.childNodes)}for(;null!==(s=Y.nextNode())&&r.length<o;){if(1===s.nodeType){if(s.hasAttributes())for(const e of s.getAttributeNames())if(e.endsWith(E)){const t=d[n++],i=s.getAttribute(e).split(C),o=/([.?@])?(.*)/.exec(t);r.push({type:1,index:a,name:o[2],strings:i,ctor:"."===o[1]?ae:"?"===o[1]?ne:"@"===o[1]?oe:se}),s.removeAttribute(e)}else e.startsWith(C)&&(r.push({type:6,index:a}),s.removeAttribute(e));if(F.test(s.tagName)){const e=s.textContent.split(C),t=e.length-1;if(t>0){s.textContent=S?S.emptyScript:"";for(let i=0;i<t;i++)s.append(e[i],D()),Y.nextNode(),r.push({type:2,index:++a});s.append(e[t],D())}}}else if(8===s.nodeType)if(s.data===T)r.push({type:2,index:a});else{let e=-1;for(;-1!==(e=s.data.indexOf(C,e+1));)r.push({type:7,index:a}),e+=C.length-1}a++}}static createElement(e,t){const i=H.createElement("template");return i.innerHTML=e,i}}function ee(e,t,i=e,s){if(t===G)return t;let a=void 0!==s?i._$Co?.[s]:i._$Cl;const n=M(t)?void 0:t._$litDirective$;return a?.constructor!==n&&(a?._$AO?.(!1),void 0===n?a=void 0:(a=new n(e),a._$AT(e,i,s)),void 0!==s?(i._$Co??=[])[s]=a:i._$Cl=a),void 0!==a&&(t=ee(e,a._$AS(e,t.values),a,s)),t}class te{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:i}=this._$AD,s=(e?.creationScope??H).importNode(t,!0);Y.currentNode=s;let a=Y.nextNode(),n=0,o=0,r=i[0];for(;void 0!==r;){if(n===r.index){let t;2===r.type?t=new ie(a,a.nextSibling,this,e):1===r.type?t=new r.ctor(a,r.name,r.strings,this,e):6===r.type&&(t=new re(a,this,e)),this._$AV.push(t),r=i[++o]}n!==r?.index&&(a=Y.nextNode(),n++)}return Y.currentNode=H,s}p(e){let t=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}}class ie{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,s){this.type=2,this._$AH=K,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===e?.nodeType&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=ee(this,e,t),M(e)?e===K||null==e||""===e?(this._$AH!==K&&this._$AR(),this._$AH=K):e!==this._$AH&&e!==G&&this._(e):void 0!==e._$litType$?this.$(e):void 0!==e.nodeType?this.T(e):(e=>I(e)||"function"==typeof e?.[Symbol.iterator])(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==K&&M(this._$AH)?this._$AA.nextSibling.data=e:this.T(H.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:i}=e,s="number"==typeof i?this._$AC(e):(void 0===i.el&&(i.el=Q.createElement(X(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(t);else{const e=new te(s,this),i=e.u(this.options);e.p(t),this.T(i),this._$AH=e}}_$AC(e){let t=V.get(e.strings);return void 0===t&&V.set(e.strings,t=new Q(e)),t}k(e){I(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let i,s=0;for(const a of e)s===t.length?t.push(i=new ie(this.O(D()),this.O(D()),this,this.options)):i=t[s],i._$AI(a),s++;s<t.length&&(this._$AR(i&&i._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const t=z(e).nextSibling;z(e).remove(),e=t}}setConnected(e){void 0===this._$AM&&(this._$Cv=e,this._$AP?.(e))}}class se{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,s,a){this.type=1,this._$AH=K,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=a,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=K}_$AI(e,t=this,i,s){const a=this.strings;let n=!1;if(void 0===a)e=ee(this,e,t,0),n=!M(e)||e!==this._$AH&&e!==G,n&&(this._$AH=e);else{const s=e;let o,r;for(e=a[0],o=0;o<a.length-1;o++)r=ee(this,s[i+o],t,o),r===G&&(r=this._$AH[o]),n||=!M(r)||r!==this._$AH[o],r===K?e=K:e!==K&&(e+=(r??"")+a[o+1]),this._$AH[o]=r}n&&!s&&this.j(e)}j(e){e===K?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class ae extends se{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===K?void 0:e}}class ne extends se{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==K)}}class oe extends se{constructor(e,t,i,s,a){super(e,t,i,s,a),this.type=5}_$AI(e,t=this){if((e=ee(this,e,t,0)??K)===G)return;const i=this._$AH,s=e===K&&i!==K||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,a=e!==K&&(i===K||s);s&&this.element.removeEventListener(this.name,this,i),a&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class re{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){ee(this,e)}}const le=k.litHtmlPolyfillSupport;le?.(Q,ie),(k.litHtmlVersions??=[]).push("3.3.3");const de=globalThis;
=======
const k=globalThis,z=e=>e,S=k.trustedTypes,A=S?S.createPolicy("lit-html",{createHTML:e=>e}):void 0,C="$lit$",E=`lit$${Math.random().toFixed(9).slice(2)}$`,T="?"+E,O=`<${T}>`,D=document,M=()=>D.createComment(""),H=e=>null===e||"object"!=typeof e&&"function"!=typeof e,I=Array.isArray,N="[ \t\n\f\r]",L=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,P=/-->/g,R=/>/g,B=RegExp(`>|${N}(?:([^\\s"'>=/]+)(${N}*=${N}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),U=/'/g,j=/"/g,F=/^(?:script|style|textarea|title)$/i,Z=e=>(t,...s)=>({_$litType$:e,strings:t,values:s}),W=Z(1),q=Z(2),G=Symbol.for("lit-noChange"),K=Symbol.for("lit-nothing"),V=new WeakMap,Y=D.createTreeWalker(D,129);function X(e,t){if(!I(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==A?A.createHTML(t):t}const J=(e,t)=>{const s=e.length-1,i=[];let a,n=2===t?"<svg>":3===t?"<math>":"",o=L;for(let t=0;t<s;t++){const s=e[t];let r,l,d=-1,c=0;for(;c<s.length&&(o.lastIndex=c,l=o.exec(s),null!==l);)c=o.lastIndex,o===L?"!--"===l[1]?o=P:void 0!==l[1]?o=R:void 0!==l[2]?(F.test(l[2])&&(a=RegExp("</"+l[2],"g")),o=B):void 0!==l[3]&&(o=B):o===B?">"===l[0]?(o=a??L,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,r=l[1],o=void 0===l[3]?B:'"'===l[3]?j:U):o===j||o===U?o=B:o===P||o===R?o=L:(o=B,a=void 0);const h=o===B&&e[t+1].startsWith("/>")?" ":"";n+=o===L?s+O:d>=0?(i.push(r),s.slice(0,d)+C+s.slice(d)+E+h):s+E+(-2===d?t:h)}return[X(e,n+(e[s]||"<?>")+(2===t?"</svg>":3===t?"</math>":"")),i]};class Q{constructor({strings:e,_$litType$:t},s){let i;this.parts=[];let a=0,n=0;const o=e.length-1,r=this.parts,[l,d]=J(e,t);if(this.el=Q.createElement(l,s),Y.currentNode=this.el.content,2===t||3===t){const e=this.el.content.firstChild;e.replaceWith(...e.childNodes)}for(;null!==(i=Y.nextNode())&&r.length<o;){if(1===i.nodeType){if(i.hasAttributes())for(const e of i.getAttributeNames())if(e.endsWith(C)){const t=d[n++],s=i.getAttribute(e).split(E),o=/([.?@])?(.*)/.exec(t);r.push({type:1,index:a,name:o[2],strings:s,ctor:"."===o[1]?ae:"?"===o[1]?ne:"@"===o[1]?oe:ie}),i.removeAttribute(e)}else e.startsWith(E)&&(r.push({type:6,index:a}),i.removeAttribute(e));if(F.test(i.tagName)){const e=i.textContent.split(E),t=e.length-1;if(t>0){i.textContent=S?S.emptyScript:"";for(let s=0;s<t;s++)i.append(e[s],M()),Y.nextNode(),r.push({type:2,index:++a});i.append(e[t],M())}}}else if(8===i.nodeType)if(i.data===T)r.push({type:2,index:a});else{let e=-1;for(;-1!==(e=i.data.indexOf(E,e+1));)r.push({type:7,index:a}),e+=E.length-1}a++}}static createElement(e,t){const s=D.createElement("template");return s.innerHTML=e,s}}function ee(e,t,s=e,i){if(t===G)return t;let a=void 0!==i?s._$Co?.[i]:s._$Cl;const n=H(t)?void 0:t._$litDirective$;return a?.constructor!==n&&(a?._$AO?.(!1),void 0===n?a=void 0:(a=new n(e),a._$AT(e,s,i)),void 0!==i?(s._$Co??=[])[i]=a:s._$Cl=a),void 0!==a&&(t=ee(e,a._$AS(e,t.values),a,i)),t}class te{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:s}=this._$AD,i=(e?.creationScope??D).importNode(t,!0);Y.currentNode=i;let a=Y.nextNode(),n=0,o=0,r=s[0];for(;void 0!==r;){if(n===r.index){let t;2===r.type?t=new se(a,a.nextSibling,this,e):1===r.type?t=new r.ctor(a,r.name,r.strings,this,e):6===r.type&&(t=new re(a,this,e)),this._$AV.push(t),r=s[++o]}n!==r?.index&&(a=Y.nextNode(),n++)}return Y.currentNode=D,i}p(e){let t=0;for(const s of this._$AV)void 0!==s&&(void 0!==s.strings?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}}class se{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,i){this.type=2,this._$AH=K,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===e?.nodeType&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=ee(this,e,t),H(e)?e===K||null==e||""===e?(this._$AH!==K&&this._$AR(),this._$AH=K):e!==this._$AH&&e!==G&&this._(e):void 0!==e._$litType$?this.$(e):void 0!==e.nodeType?this.T(e):(e=>I(e)||"function"==typeof e?.[Symbol.iterator])(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==K&&H(this._$AH)?this._$AA.nextSibling.data=e:this.T(D.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:s}=e,i="number"==typeof s?this._$AC(e):(void 0===s.el&&(s.el=Q.createElement(X(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(t);else{const e=new te(i,this),s=e.u(this.options);e.p(t),this.T(s),this._$AH=e}}_$AC(e){let t=V.get(e.strings);return void 0===t&&V.set(e.strings,t=new Q(e)),t}k(e){I(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let s,i=0;for(const a of e)i===t.length?t.push(s=new se(this.O(M()),this.O(M()),this,this.options)):s=t[i],s._$AI(a),i++;i<t.length&&(this._$AR(s&&s._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const t=z(e).nextSibling;z(e).remove(),e=t}}setConnected(e){void 0===this._$AM&&(this._$Cv=e,this._$AP?.(e))}}class ie{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,i,a){this.type=1,this._$AH=K,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=a,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=K}_$AI(e,t=this,s,i){const a=this.strings;let n=!1;if(void 0===a)e=ee(this,e,t,0),n=!H(e)||e!==this._$AH&&e!==G,n&&(this._$AH=e);else{const i=e;let o,r;for(e=a[0],o=0;o<a.length-1;o++)r=ee(this,i[s+o],t,o),r===G&&(r=this._$AH[o]),n||=!H(r)||r!==this._$AH[o],r===K?e=K:e!==K&&(e+=(r??"")+a[o+1]),this._$AH[o]=r}n&&!i&&this.j(e)}j(e){e===K?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class ae extends ie{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===K?void 0:e}}class ne extends ie{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==K)}}class oe extends ie{constructor(e,t,s,i,a){super(e,t,s,i,a),this.type=5}_$AI(e,t=this){if((e=ee(this,e,t,0)??K)===G)return;const s=this._$AH,i=e===K&&s!==K||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,a=e!==K&&(s===K||i);i&&this.element.removeEventListener(this.name,this,s),a&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class re{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){ee(this,e)}}const le=k.litHtmlPolyfillSupport;le?.(Q,se),(k.litHtmlVersions??=[]).push("3.3.3");const de=globalThis;
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
<<<<<<< HEAD
     */let ce=class extends x{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,i)=>{const s=i?.renderBefore??t;let a=s._$litPart$;if(void 0===a){const e=i?.renderBefore??null;s._$litPart$=a=new ie(t.insertBefore(D(),e),e,void 0,i??{})}return a._$AI(e),a})(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return G}};ce._$litElement$=!0,ce.finalized=!0,de.litElementHydrateSupport?.({LitElement:ce});const he=de.litElementPolyfillSupport;he?.({LitElement:ce}),(de.litElementVersions??=[]).push("4.2.2");
=======
     */let ce=class extends x{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,s)=>{const i=s?.renderBefore??t;let a=i._$litPart$;if(void 0===a){const e=s?.renderBefore??null;i._$litPart$=a=new se(t.insertBefore(M(),e),e,void 0,s??{})}return a._$AI(e),a})(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return G}};ce._$litElement$=!0,ce.finalized=!0,de.litElementHydrateSupport?.({LitElement:ce});const he=de.litElementPolyfillSupport;he?.({LitElement:ce}),(de.litElementVersions??=[]).push("4.2.2");
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const ue=e=>(t,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(e,t)}):customElements.define(e,t)},pe={attribute:!0,type:String,converter:y,reflect:!1,hasChanged:w},ge=(e=pe,t,i)=>{const{kind:s,metadata:a}=i;let n=globalThis.litPropertyMetadata.get(a);if(void 0===n&&globalThis.litPropertyMetadata.set(a,n=new Map),"setter"===s&&((e=Object.create(e)).wrapped=!0),n.set(i.name,e),"accessor"===s){const{name:s}=i;return{set(i){const a=t.get.call(this);t.set.call(this,i),this.requestUpdate(s,a,e,!0,i)},init(t){return void 0!==t&&this.C(s,void 0,e,t),t}}}if("setter"===s){const{name:s}=i;return function(i){const a=this[s];t.call(this,i),this.requestUpdate(s,a,e,!0,i)}}throw Error("Unsupported decorator location: "+s)};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function me(e){return(t,i)=>"object"==typeof i?ge(e,t,i):((e,t,i)=>{const s=t.hasOwnProperty(i);return t.constructor.createProperty(i,e),s?Object.getOwnPropertyDescriptor(t,i):void 0})(e,t,i)}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function ve(e){return me({...e,state:!0,attribute:!1})}
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
<<<<<<< HEAD
function fe(e,t){return(t,i,s)=>((e,t,i)=>(i.configurable=!0,i.enumerable=!0,Reflect.decorate&&"object"!=typeof t&&Object.defineProperty(e,t,i),i))(t,i,{get(){return(t=>t.renderRoot?.querySelector(e)??null)(this)}})}const _e=`v${"2026.08.05"}`,be="smart_irrigation",ye=["de","en","es","fr","it","nl","no","sk"],we="fixed_time",$e=[we,"before_run"],xe="precipitation_threshold_mm",ke="sensor_debounce",ze="Open Weather Map",Se="Pirate Weather",Ae="Open-Meteo",Ee="Met Office",Ce="minutes",Te="hours",Oe="days",He="imperial",De="metric",Me="Dewpoint",Ie="Evapotranspiration",Ne="Humidity",Pe="Precipitation",Le="Current Precipitation",Re="Pressure",Be="Solar Radiation",Ue="Temperature",je="Windspeed",Fe="weather_service",Ze="sensor",We="static",qe="pressure_type",Ge="absolute",Ke="relative",Ve="none",Ye="source",Xe="sensorentity",Je="static_value",Qe="unit",et="aggregate",tt=["average","first","last","maximum","median","minimum","riemannsum","sum","delta"],it="sq ft",st="l/minute",at="gal/minute",nt="s",ot="mm",rt="in",lt="inch Hg",dt="mile/h",ct="meter/s",ht="mm/h",ut="in/h",pt="name",gt="size",mt="throughput",vt="state",ft="duration",_t="module",bt="bucket",yt="multiplier",wt="mapping",$t="lead_time",xt="maximum_duration",kt="maximum_bucket",zt="drainage_rate",St="kc",At="plant_type",Et="linked_entity",Ct="bucket_threshold",Tt="flow_sensor",Ot="flow_counter_type",Ht="watering_mode",Dt="run_service",Mt="duration_field",It="duration_unit",Nt="stop_service",Pt="confirm_entity",Lt="observed_entity",Rt="soil_moisture_sensor",Bt="soil_moisture_threshold",Ut={lawn:.8,vegetables:1,flowers:.9,shrubs:.5,trees:.7,xeriscape:.3},jt={sand:35,loam:20,silt:10,clay:5},Ft="zone_sequencing",Zt="sequential",Wt="parallel",qt="rotating",Gt="zone_sequencing_max_consecutive_duration",Kt="zone_sequencing_min_absorption_time",Vt="master_entity",Yt="master_settle_seconds",Xt="master_kick_enabled",Jt="master_kick_pause_seconds",Qt="master_off_after",ei="interval",ti=["daily","weekly","monthly",ei],ii="none",si="time",ai="sunrise",ni="sunset",oi="solar_azimuth",ri=[ii,si,ai,ni,oi],li="start",di="finish",ci="name",hi="watering_mode",ui="inlet_entity",pi="watch_mode",gi="run_service",mi="stop_service",vi="duration_field",fi="duration_unit",_i="confirm_entity",bi="flow_sensor",yi="notify_target",wi="commissioning_confirmed",$i=["count","warn","ignore"],xi="classic",ki="service",zi="opensprinkler",Si="distributor_id",Ai="outlet_number",Ei=e=>e.callWS({type:be+"/config"}),Ci=(e,t)=>e.callApi("POST",be+"/config",t),Ti=e=>e.callWS({type:be+"/zones"}),Oi=(e,t)=>e.callApi("POST",be+"/zones",t),Hi=e=>e.callWS({type:be+"/modules"}),Di=e=>e.callWS({type:be+"/allmodules"}),Mi=(e,t)=>e.callApi("POST",be+"/modules",t),Ii=e=>e.callWS({type:be+"/mappings"}),Ni=(e,t)=>e.callApi("POST",be+"/mappings",t),Pi=(e,t)=>e.callWS({type:be+"/watering_calendar",zone_id:t}),Li=(e,t)=>e.callWS({type:be+"/schedule_save",schedule:t}),Ri=e=>e.callWS({type:be+"/distributors"}),Bi=(e,t)=>e.callApi("POST",be+"/distributors",t),Ui=e=>e.callWS({type:be+"/weather_config"}),ji=(e,t,i,s)=>e.callWS({type:be+"/weather_config_save",use_weather_service:t,weather_service:null!=i?i:null,api_key:null!=s?s:null}),Fi=e=>e.callWS({type:be+"/coordinates"});let Zi=!1,Wi=null;const qi=async()=>{if(Zi&&Wi)return Wi;if(customElements.get("ha-checkbox")&&customElements.get("ha-slider")&&customElements.get("ha-panel-config")&&customElements.get("ha-entity-picker"))return Promise.resolve();Zi=!0,Wi=async function(){try{await new Promise(e=>{"requestIdleCallback"in window?requestIdleCallback(()=>e()):setTimeout(()=>e(),0)}),await customElements.whenDefined("partial-panel-resolver");const e=document.createDocumentFragment(),t=document.createElement("partial-panel-resolver");e.appendChild(t),t.hass={panels:[{url_path:"tmp",component_name:"config"}]},await new Promise(e=>queueMicrotask(()=>e())),t._updateRoutes(),await t.routerOptions.routes.tmp.load(),await customElements.whenDefined("ha-panel-config"),await new Promise(e=>queueMicrotask(()=>e()));const i=document.createElement("ha-panel-config");e.appendChild(i),await i.routerOptions.routes.automation.load(),customElements.get("ha-entity-picker")||await Promise.race([customElements.whenDefined("ha-entity-picker"),new Promise(e=>setTimeout(e,3e3))]),e.textContent=""}catch(e){console.error("Failed to load HA form elements:",e)}}
=======
function fe(e,t){return(t,s,i)=>((e,t,s)=>(s.configurable=!0,s.enumerable=!0,Reflect.decorate&&"object"!=typeof t&&Object.defineProperty(e,t,s),s))(t,s,{get(){return(t=>t.renderRoot?.querySelector(e)??null)(this)}})}const _e=`v${"2026.08.05"}`,be="smart_irrigation",ye=["de","en","es","fr","it","nl","no","sk"],we="fixed_time",$e=[we,"before_run"],xe="precipitation_threshold_mm",ke="sensor_debounce",ze="Open Weather Map",Se="Pirate Weather",Ae="Open-Meteo",Ce="Met Office",Ee="minutes",Te="hours",Oe="days",De="imperial",Me="metric",He="Dewpoint",Ie="Evapotranspiration",Ne="Humidity",Le="Precipitation",Pe="Current Precipitation",Re="Pressure",Be="Solar Radiation",Ue="Temperature",je="Windspeed",Fe="weather_service",Ze="sensor",We="static",qe="pressure_type",Ge="absolute",Ke="relative",Ve="none",Ye="source",Xe="sensorentity",Je="static_value",Qe="unit",et="aggregate",tt=["average","first","last","maximum","median","minimum","riemannsum","sum","delta"],st="sq ft",it="l/minute",at="gal/minute",nt="s",ot="mm",rt="in",lt="inch Hg",dt="mile/h",ct="meter/s",ht="mm/h",ut="in/h",pt="name",gt="size",mt="throughput",vt="state",ft="duration",_t="module",bt="bucket",yt="multiplier",wt="mapping",$t="lead_time",xt="maximum_duration",kt="maximum_bucket",zt="drainage_rate",St="kc",At="plant_type",Ct="linked_entity",Et="bucket_threshold",Tt="flow_sensor",Ot="flow_counter_type",Dt="watering_mode",Mt="run_service",Ht="duration_field",It="duration_unit",Nt="stop_service",Lt="confirm_entity",Pt="observed_entity",Rt="soil_moisture_sensor",Bt="soil_moisture_threshold",Ut={lawn:.8,vegetables:1,flowers:.9,shrubs:.5,trees:.7,xeriscape:.3},jt={sand:35,loam:20,silt:10,clay:5},Ft="zone_sequencing",Zt="sequential",Wt="parallel",qt="rotating",Gt="zone_sequencing_max_consecutive_duration",Kt="zone_sequencing_min_absorption_time",Vt="master_entity",Yt="master_settle_seconds",Xt="master_kick_enabled",Jt="master_kick_pause_seconds",Qt="master_off_after",es="weekly",ts="monthly",ss="interval",is=["daily",es,ts,ss],as="none",ns="time",os="sunrise",rs="sunset",ls="solar_azimuth",ds=[as,ns,os,rs,ls],cs="start",hs="finish",us="name",ps="watering_mode",gs="inlet_entity",ms="watch_mode",vs="run_service",fs="stop_service",_s="duration_field",bs="duration_unit",ys="confirm_entity",ws="flow_sensor",$s="notify_target",xs="commissioning_confirmed",ks=["count","warn","ignore"],zs="classic",Ss="service",As="opensprinkler",Cs="distributor_id",Es="outlet_number",Ts=e=>e.callWS({type:be+"/config"}),Os=(e,t)=>e.callApi("POST",be+"/config",t),Ds=e=>e.callWS({type:be+"/zones"}),Ms=(e,t)=>e.callApi("POST",be+"/zones",t),Hs=e=>e.callWS({type:be+"/modules"}),Is=e=>e.callWS({type:be+"/allmodules"}),Ns=(e,t)=>e.callApi("POST",be+"/modules",t),Ls=e=>e.callWS({type:be+"/mappings"}),Ps=(e,t)=>e.callApi("POST",be+"/mappings",t),Rs=(e,t)=>e.callWS({type:be+"/watering_calendar",zone_id:t}),Bs=(e,t)=>e.callWS({type:be+"/schedule_save",schedule:t}),Us=e=>e.callWS({type:be+"/distributors"}),js=(e,t)=>e.callApi("POST",be+"/distributors",t),Fs=e=>e.callWS({type:be+"/weather_config"}),Zs=(e,t,s,i)=>e.callWS({type:be+"/weather_config_save",use_weather_service:t,weather_service:null!=s?s:null,api_key:null!=i?i:null}),Ws=e=>e.callWS({type:be+"/coordinates"});let qs=!1,Gs=null;const Ks=async()=>{if(qs&&Gs)return Gs;if(customElements.get("ha-checkbox")&&customElements.get("ha-slider")&&customElements.get("ha-panel-config")&&customElements.get("ha-entity-picker"))return Promise.resolve();qs=!0,Gs=async function(){try{await new Promise(e=>{"requestIdleCallback"in window?requestIdleCallback(()=>e()):setTimeout(()=>e(),0)}),await customElements.whenDefined("partial-panel-resolver");const e=document.createDocumentFragment(),t=document.createElement("partial-panel-resolver");e.appendChild(t),t.hass={panels:[{url_path:"tmp",component_name:"config"}]},await new Promise(e=>queueMicrotask(()=>e())),t._updateRoutes(),await t.routerOptions.routes.tmp.load(),await customElements.whenDefined("ha-panel-config"),await new Promise(e=>queueMicrotask(()=>e()));const s=document.createElement("ha-panel-config");e.appendChild(s),await s.routerOptions.routes.automation.load(),customElements.get("ha-entity-picker")||await Promise.race([customElements.whenDefined("ha-entity-picker"),new Promise(e=>setTimeout(e,3e3))]),e.textContent=""}catch(e){console.error("Failed to load HA form elements:",e)}}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */();try{await Wi}finally{Zi=!1,Wi=null}};const Gi=1,Ki=2,Vi=3,Yi=4,Xi=e=>(...t)=>({_$litDirective$:e,values:t});class Ji{constructor(e){}get _$AU(){return this._$AM._$AU}_$AT(e,t,i){this._$Ct=e,this._$AM=t,this._$Ci=i}_$AS(e,t){return this.update(e,t)}update(e,t){return this.render(...t)}}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
<<<<<<< HEAD
<<<<<<< HEAD
     */class Qi extends Ji{constructor(e){if(super(e),this.it=K,e.type!==Ki)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(e){if(e===K||null==e)return this._t=void 0,this.it=e;if(e===G)return e;if("string"!=typeof e)throw Error(this.constructor.directiveName+"() called with a non-string value");if(e===this.it)return this._t;this.it=e;const t=[e];return t.raw=t,this._t={_$litType$:this.constructor.resultType,strings:t,values:[]}}}Qi.directiveName="unsafeHTML",Qi.resultType=1;const es=Xi(Qi);var ts={title:"Smart Irrigation: check flow rate",message_over:"Zone '{zone}' is consistently over-watering: the measured flow is ~{percent}% above the configured rate over {runs} runs. Its valve can't stop early, so consider setting the throughput to about {rate} {unit} (currently {current}).",message_under:"Zone '{zone}' is consistently under-watering: the measured flow is ~{percent}% below the configured rate over {runs} runs. Its valve can't stop early, so consider setting the throughput to about {rate} {unit} (currently {current}).",open_settings:"Open zone settings"},is={loading:"Loading",saving:"Saving",actions:{delete:"Delete",edit:"Edit",save:"Save",cancel:"Cancel",confirm_delete:"Confirm Delete",confirm_delete_zone:"Are you sure you want to delete this zone?"},labels:{module:"Module",no:"No",select:"Select",yes:"Yes",enabled:"Enabled",disabled:"Disabled",before:"before",after:"after",settings:"Settings",bulk_actions:"Bulk Actions"},units:{seconds:"seconds"},attributes:{size:"size",throughput:"throughput",state:"state",bucket:"bucket",last_updated:"last updated",last_calculated:"last calculated",number_of_data_points:"number of data points"},"loading-messages":{configuration:"Loading configuration...",modules:"Loading modules...",general:"Loading..."},"saving-messages":{adding:"Adding...",saving:"Saving..."},errors:{load_failed:"Couldn't load data",save_failed:"Couldn't save changes",delete_failed:"Couldn't delete",action_failed:"Action failed"}},ss={"default-zone":"Default zone","default-mapping":"Default sensor group"},as={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"Note: this explanation uses '.' as decimal separator, shows rounded and metric values. Module returned Evapotranspiration deficiency ( = et0 * hour_multiplier + precipitation) of","module-returned-evapotranspiration-deficiency-hourly":"Note: this explanation uses '.' as decimal separator, shows rounded and metric values. Evapotranspiration deficiency ( = sum of hourly FAO-56 et0 over the window + precipitation) of","bucket-was":"Bucket was","new-bucket-values-is":"New bucket value is",bucket:"bucket","old-bucket-variable":"old_bucket","max-bucket-variable":"max_bucket",delta:"delta","bucket-less-than-zero-irrigation-necessary":"Since bucket < 0, irrigation is necessary","steps-taken-to-calculate-duration":"To calculate the exact duration, the following steps were taken","precipitation-rate-defined-as":"The precipitation rate is defined as","duration-is-calculated-as":"The duration is calculated as",drainage:"drainage","drainage-rate":"drainage_rate",hours:"hours","precipitation-rate-variable":"precipitation_rate","multiplier-is-applied":"Now, the multiplier is applied. The multiplier is","duration-after-multiplier-is":"hence the duration is","maximum-duration-is-applied":"Then, the maximum duration is applied. The maximum duration is","duration-after-maximum-duration-is":"hence the duration is","lead-time-is-applied":"Finally, the lead time is applied. The lead time is","duration-after-lead-time-is":"hence the final duration is","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Since bucket >= 0, no irrigation is necessary and duration is set to","maximum-bucket-is":"Maximum bucket size is","drainage-rate-is":"Drainage rate when saturated (bucket at max) is","current-drainage-is":"Current drainage is calculated as","drainage-integrated":"the surplus above field capacity drains continuously over the window (Brooks–Corey), so the rate falls as it drains","no-drainage":"Current drainage is 0 because","water-balance-substepped":"The water balance was replayed across the window, so rain, drainage and the maximum bucket clamp were applied at the times they occurred rather than all at the start of the window. Number of steps:","runoff-is":"Water above the maximum bucket that was lost to runoff:","runoff-variable":"runoff","forecast-weighting-applied":"Forecast weighting reduced the deficit for the expected rain","crop-coefficient-applied":"Scaled by the crop coefficient"}}},ns={pyeto:{description:"Calculate duration based on the FAO56 calculation from the PyETO library"},static:{description:"'Dummy' module with a static configurable delta"},passthrough:{description:"Passthrough module that returns the value of an Evapotranspiration sensor as delta"}},os={general:{cards:{"automatic-duration-calculation":{header:"Automatic duration calculation",description:"Calculation takes collected weather data up to that point and updates the bucket for each automatic zone. Then, the duration is adjusted based on the new bucket value and the collected weather data is removed.",labels:{"auto-calc-enabled":"Automatically calculate irrigation durations","calc-time":"Calculate at","calc-mode":"Calculate"},modes:{fixed_time:"At a fixed time",before_run:"Before each irrigation run"},help:{"before-run":"Durations are calculated when each irrigation schedule plans its run, so a run is sized from weather data minutes old instead of hours old."}},"run-history-logging":{header:"Run history logging",description:"When on, a scheduled run that skips a zone because it currently has no water demand is recorded in that zone's history. Off by default; existing history is unaffected.",labels:{"log-no-demand":'Log "no demand" skips in the run history'}},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Warning: weather data update time on or after calculation time"},header:"Automatic weather data update",description:"Collect and store weather data automatically. Weather data is required to calculate zone buckets and durations.",labels:{"auto-update-enabled":"Automatically update weather data","auto-update-schedule":"Update schedule","auto-update-time":"Update at","auto-update-interval":"Update sensor data every","auto-update-delay":"Update delay"},options:{minutes:"minutes",hours:"hours",days:"days"}},"automatic-clear":{header:"Automatic weather data pruning",description:"Automatically remove collected weather data at a configured time. Use this to make sure that there is no left over weather data from previous days. Don't remove the weather data before you calculate and only use this option if you expect the automatic update to collect weather data after you calculated for the day. Ideally, you want to prune as late in the day as possible.",labels:{"automatic-clear-enabled":"Automatically clear collected weather data","automatic-clear-time":"Clear weather data at"}},continuousupdates:{header:"Continuous updates for sensors (experimental)",description:"This experimental feature will continuously update the sensor data. This is useful for sensor groups that use sources that provide continuous data, such as weather stations. This feature cannot be used for sensor groups that at least partly rely on weather services as continous polling of APIs will incur costs. Keep in mind that this is experimental and may not work as expected. Use at your own risk.",labels:{continuousupdates:"Enable continuous updates",sensor_debounce:"Sensor debounce"}}},description:"This page provides global settings.",title:"General",sections:{weather:"Weather",automation:"Automation",location:"Location",watering:"Watering behavior"}},schedules:{title:"Schedules",description:"Create recurring schedules to automatically irrigate your zones at specific times. No automations needed.",add:"Add Schedule",no_items:"No schedules configured yet. Click 'Add Schedule' to get started.",zones_all:"All zones",zones_specific:"Specific zones",hours:"hours",minutes:"min",types:{daily:"Daily",weekly:"Weekly",monthly:"Monthly",interval:"Every N hours"},actions:{calculate:"Calculate (update irrigation duration)",update:"Update (collect weather data)",irrigate:"Irrigate (run valves directly)"},days:{monday:"Mon",tuesday:"Tue",wednesday:"Wed",thursday:"Thu",friday:"Fri",saturday:"Sat",sunday:"Sun"},fields:{name:"Name",recurrence:"Recurrence",enabled:"Enabled",days_of_week:"Days of week",day_of_month:"Day of month",interval_hours:"Interval",action:"Action",zones:"Zones",start_mode:"Start",start_time:"Start time (optional)",finish_mode:"Finish",finish_time:"Finish time (HH:MM)",anchor:"Pinned to",start_date:"Start date (optional)",end_date:"End date (optional)",offset_by:"offset by"},dialog:{add_title:"Add Schedule",edit_title:"Edit Schedule"},bound_mode:{none:"No limit",time:"At a time",sunrise:"At sunrise",sunset:"At sunset",solar_azimuth:"At solar azimuth"},anchor:{start:"As early as possible within the window",finish:"As late as possible within the window"},help:{error:"Must set either a start or finish condition",demand_open:"Set by demand. All zones run to completion.",exact:"Exact.",demand_floored:"Set by demand, but never before this.",exact_deferred:"Exact. Zones that don't fit are deferred.",demand_capped_deferred:"Set by demand, but never later than this. Zones that don't fit are deferred."},dial:{aria_label:"Run window on a 24 hour dial",sunrise:"Sunrise {time}",sunset:"Sunset {time}",run:"Run {from} to {to}",collision:"Collides with the previous run, {from} to {to}: zones still watering are skipped",window_label:"window",run_label:"run",per_day:"{count}x per day",every_hours:"every {hours}h"}},setup:{title:"Setup",tabs:{weather_location:"Weather & Location",my_zones:"My Zones",when_to_water:"When to Water",advanced:"Advanced",experimental:"Experimental",distributors:"Distributors"},weather_data:{forecast_title:"Forecast",forecast_none:"Forecast is available when a weather service is enabled.",seasonal_title:"Seasonal outlook"},advanced:{used_by_zones:"Used by {count, plural, one {# zone} other {# zones}}",not_used:"Not used"}},experimental:{title:"Experimental features",warning:"These features are opt-in and still being refined. They change how each zone's bucket is filled, so turn them on one at a time and keep an eye on your zones — you can switch them back off at any time.",forecast_weighting:{title:"Forecast-weighted durations",description:"Instead of skipping a whole run when rain is forecast, water less. The upcoming precipitation (over the look-ahead window set under When to Water) is subtracted from the deficit used to compute the run duration, while the true deficit stays in the bucket so the real rain fills the rest. If the forecast rain misses, the next run makes up the difference. Requires a weather service.",label:"Reduce durations when rain is forecast",note:"Uses the precipitation look-ahead from When to Water. Works alongside the rain-skip guard (a skip still wins over a reduced run)."},observed_watering:{title:"Credit bucket from observed watering",description:"When a zone's linked valve runs outside Smart Irrigation — a manual tap, an automation, your own schedule — its bucket is credited for the water applied, estimated from the run time and the zone's throughput. This keeps the soil-moisture model honest when you water by other means. Smart Irrigation's own runs are already accounted for and are never double-counted.",label:"Credit the bucket when a linked valve runs externally",note:"Requires a linked valve and a throughput on the zone. Volume is estimated (run time × throughput), not metered."},live_estimate:{title:"Live-estimate watering",description:"By default a zone waters once a day, from the deficit the daily calculation produced (for example at 23:00). With this on, each scheduled run instead decides — and sizes itself — from the live intra-day deficit (the drainage-aware ET and rainfall since the last calculation). This lets a zone water more than once a day on real intra-day demand (for example pots on an every-12-hours schedule that the once-daily bucket would otherwise leave dry), and it shrinks or cancels a run that intra-day rain has already covered. The daily ledger is unchanged: after the run the bucket is credited with the water actually delivered, so the next daily calculation never double-counts. Requires a weather service.",label:"Trigger and size each run from the live deficit",note:"Affects scheduled runs only, and can start a run the daily calculation didn't approve. For frequent watering keep a sensible minimum deficit and a maximum bucket of at least a day's ET."},continuous_updates:{title:"Continuous sensor updates",description:"By default, sensor-based weather values are read once per scheduled update (hourly by default), so anything that happened in between is never recorded — the daily minimum and maximum temperature come from those spot readings, and solar radiation is integrated coarsely. With this on, a reading is recorded the moment the sensor changes, which makes the daily aggregates and the resulting evapotranspiration considerably more accurate. Sensor groups that also use a weather service keep their scheduled update for the weather-service values; only the sensor values become continuous. Small changes are ignored, so a noisy sensor does not fill the buffer.",label:"Record sensor readings when they change",debounce_label:"Group changes arriving within (milliseconds)",note:"Applies to sensor groups whose values come from Home Assistant sensors. The grouping delay only postpones the follow-up bookkeeping — no reading is ever dropped by it. Set it to 0 to disable grouping."},hourly_calculation:{title:"Hourly evapotranspiration",description:"By default the FAO-56 equation is run once, over the window's average weather, which cloud cover biases systematically: fed one identical hourly series across 362 days it returns 1.14 times the reference on overcast days and 0.93 times on clear ones. With this on, the equation is run for each hour and the hours are summed, which removes that bias, and the water balance is replayed hour by hour so rain and drainage are booked when they happened instead of all at the start of the window. Expect the daily figure to move by up to 12 percent, in either direction depending on the sky. Needs a Solar Radiation source that is measured rather than estimated, and it is not used on days where a forecast is blended in.",label:"Sum evapotranspiration hour by hour",note:"Independent of continuous sensor updates: scheduled hourly updates carry this too, and a denser buffer makes it more accurate without being required. Any window that cannot be reduced to hourly rows keeps the daily equation, so no series is ever invented."},distributors:{title:"Mechanical water distributors",description:"Drive a mechanical pressure-distributor — for example a Gardena Water Distributor — that splits one supply into several outlets and advances on water on/off pulses. Assign zones to a distributor's outlets and Smart Irrigation waters them in sequence, tracks the position, and coordinates a master valve or pump. This is a new feature that could not be fully hardware-tested, so treat it as a beta.",label:"Enable mechanical water distributors",note:"Watch the first days of use closely and keep the device's manual override handy. You can switch it back off at any time — existing zone watering is unaffected."}},help:{title:"Help",cards:{"how-to-get-help":{title:"How to get help","first-read-the":"First, read the",wiki:"Documentation","if-you-still-need-help":"If you still need help reach out on the","community-forum":"Community forum","or-open-a":"or open a","github-issue":"Github Issue","english-only":"English only"}}},info:{title:"Info",description:"View information about next irrigation and system status.","configuration-not-available":"Configuration not available.",cards:{"zone-bucket-values":{title:"Zone Bucket Values & Duration",labels:{bucket:"Bucket",duration:"Duration"},"no-zones":"No zones configured"},"next-irrigation":{title:"Next Irrigation",labels:{"next-start":"Next start",duration:"Duration",zones:"Zones"},"no-data":"No data available"},"irrigation-reason":{title:"Irrigation Reason",labels:{reason:"Reason",sunrise:"Sunrise","total-duration":"Total duration",explanation:"Explanation"},"no-data":"No data available"},irrigate_now:{title:"Irrigate Now",description:"Immediately start irrigation for all zones that have a linked entity. Skip conditions are ignored.",button_all:"Run all zones now",no_linked_zones:"No zones have a linked switch/valve entity with a calculated duration."}}},mappings:{cards:{"add-mapping":{actions:{add:"Add sensor group"},header:"Add sensor groups"},mapping:{aggregates:{average:"Average",first:"First",last:"Last",maximum:"Maximum",median:"Median",minimum:"Minimum",riemannsum:"Riemann sum",sum:"Sum",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"You cannot delete this sensor group because there is at least one zone using it.",invalid_source:"Invalid source",source_does_not_exist:"Source does not exist. Please enter a valid source, such as 'sensor.mysensor'."},items:{dewpoint:"Dewpoint",evapotranspiration:"Evapotranspiration",humidity:"Humidity","maximum temperature":"Maximum temperature","minimum temperature":"Minimum temperature",precipitation:"Total precipitation","current precipitation":"Current precipitation",pressure:"Pressure","solar radiation":"Solar radiation",temperature:"Temperature",windspeed:"Wind speed"},pressure_types:{absolute:"absolute",relative:"relative"},"pressure-type":"Pressure is","sensor-aggregate-of-sensor-values-to-calculate":"of sensor values to calculate duration","sensor-aggregate-use-the":"Use the","sensor-entity":"Sensor entity",static_value:"Value","input-units":"Input provides values in",source:"Source",sources:{none:"None",weather_service:"Weather service",sensor:"Sensor",static:"Static value"}}},description:"Add one or more sensor groups that retrieve weather data from Weather service, from sensors or a combination of these. You can map each sensor group to one or more zones",labels:{"mapping-name":"Name"},no_items:"There are no sensor group defined yet.",title:"Sensor Groups","weather-records":{title:"Weather Records",timestamp:"Time",temperature:"Temp",humidity:"Hum",dewpoint:"Dew",wind:"Wind",pressure:"Press",precipitation:"Precip","retrieval-time":"Retrieved","no-data":"No weather data available for this sensor group"}},modules:{cards:{"add-module":{actions:{add:"Add module"},header:"Add module"},module:{errors:{"cannot-delete-module-because-zones-use-it":"You cannot delete this module because there is at least one zone using it."},labels:{configuration:"Configuration",required:"indicates a required field"},"translated-options":{DontEstimate:"Do not estimate",EstimateFromSunHours:"Estimate from sun hours",EstimateFromTemp:"Estimate from temperature",EstimateFromSunHoursAndTemperature:"Estimate from average of sun hours and temperature"},fields:{coastal:{name:"Coastal",description:"Enable if the weather station is located near a coast or large body of water. Affects how atmospheric humidity is estimated."},solrad_behavior:{name:"Solar radiation estimation",description:"How solar radiation is estimated when it is not directly measured by a sensor."},forecast_days:{name:"Forecast days",description:"Number of future days to include in the ET calculation. 0 = current weather only (recommended — no extra API calls). Values > 0 average today's ET with forecasted ET for upcoming days (up to 4 days via the OWM free tier)."},delta:{name:"Delta",description:"Static evapotranspiration delta (mm) used directly without any weather-based calculation."}}}},description:"Add one or more modules that calculate irrigation duration. Each module comes with its own configuration and can be used to calculate duration for one or more zones.",no_items:"There are no modules defined yet.",title:"Modules"},zones:{actions:{add:"Add",calculate:"Calculate",information:"Information",update:"Update","reset-bucket":"Reset bucket","view-weather-info":"View weather data","view-weather-info-message":"Weather data available for","view-watering-calendar":"View watering calendar",irrigate_all:"Water all zones now",open_settings:"Edit settings"},cards:{"add-zone":{actions:{add:"Add zone"},header:"Add zone"},"zone-actions":{actions:{"calculate-all":"Recalculate durations","update-all":"Refresh weather data","reset-all-buckets":"Reset all buckets","clear-all-weatherdata":"Clear all weather data"},header:"Actions on all zones"}},description:"Specify one or more irrigation zones here. The irrigation duration is calculated per zone, depending on size, throughput, state, module and sensor group.",labels:{bucket:"Bucket",duration:"Duration","lead-time":"Lead time",mapping:"Sensor Group","maximum-duration":"Maximum duration",multiplier:"Multiplier",name:"Name",size:"Size",state:"State",states:{automatic:"Automatic",disabled:"Disabled",manual:"Manual"},throughput:"Throughput","maximum-bucket":"Maximum bucket",last_calculated:"Last calculated","data-last-updated":"Data last updated","data-number-of-data-points":"Number of data points",drainage_rate:"Drainage rate",linked_entity:"Linked switch/valve/helper entity",opensprinkler_station:"OpenSprinkler station",opensprinkler_station_help:"The station's enabled switch, e.g. switch.front_lawn_station_enabled. HASI queues the run on the controller and then watches that station's own running sensor, so a zone queued behind others is only counted as watering once it really starts. Set the controller's water level to 100% or turn its weather adjustment off, otherwise the weather correction is applied twice.",opensprinkler_no_stations:"No OpenSprinkler stations found. Check that the OpenSprinkler integration is set up and the controller is reachable. You can still type an entity id.",linked_entity_placeholder:"e.g. switch.garden_valve",flow_sensor:"Flow meter sensor (optional)",flow_sensor_placeholder:"e.g. sensor.zone_flow_rate",flow_counter_type:"Counter type",flow_counter_type_help:"How this cumulative flow sensor is read. Auto learns across runs whether the sensor resets each run. Per run: the sensor resets to ~0 each run and shows that run's total (e.g. Sonoff/Zigbee valves). Lifetime: a meter that only ever counts up across all runs (delta per run).",flow_counter_type_auto:"Auto (learn)",flow_counter_type_per_run:"Per run (resets each run)",flow_counter_type_lifetime:"Lifetime total (delta)",watering_mode:"Watering mode",watering_mode_description:"How HASI actuates this zone. Classic: HASI opens the valve and closes it itself with a software timer. Self-closing service: HASI sends the run duration to a self-closing valve via a script (see the shipped valve blueprints) and lets the hardware close itself, so an HA restart mid-run cannot cause continuous irrigation.",watering_modes:{classic:"Classic (HASI opens & closes the valve)",service:"Self-closing service (valve closes itself)",opensprinkler:"OpenSprinkler station (controller runs the queue)"},run_service:"Run service",run_service_help:"Service HASI calls to start the run (e.g. a script.* or a switch/valve service). It receives the duration field below plus zone_id and zone_name.",duration_field:"Duration field",duration_field_placeholder:"e.g. dauer",duration_field_help:"Name of the parameter that carries the run length in the call to your run service. The shipped valve blueprints use 'duration' (the default); a custom script may use another name (e.g. 'dauer').",duration_unit:"Duration unit",duration_units:{seconds:"Seconds",minutes:"Minutes"},duration_unit_help:"Unit your hardware expects for the run length. Check the device: many Zigbee/Tuya valves count in MINUTES. The wrong unit over- or under-waters by 60x. In Minutes mode HASI rounds up to whole minutes (minimum 1).",stop_service:"Stop service (optional)",stop_service_help:"Optional. Service HASI calls to close the valve when you stop the zone early, before its own timer expires. Leave empty if the valve cannot be stopped manually.",confirm_entity:"Confirm entity (optional)",confirm_entity_help:"Optional. The real valve/switch entity the run service drives (e.g. a valve or switch) — it holds a steady on-state while watering. If set, HASI verifies the open against it (poll only, it never re-actuates) and flags a problem plus skips the bucket credit if it never turns on. Leave empty to treat the run as write-only and credit optimistically (the hardware owns the close). When in doubt, leave it empty: it only helps with an entity that reports its on-state reliably — a valve that reports late (e.g. a sleepy Zigbee valve) could be read as 'off' and wrongly skip the credit, so the zone would water again next run. Do NOT point this at the run script itself — a fire-and-forget script is not a valid state signal.",observed_entity:"Observed valve/switch (optional)",observed_entity_help:"If Observed watering is on, external runs of this valve/switch (a manual tap, an automation) credit this zone's water storage. Leave empty to not observe this zone.",soil_moisture_sensor:"Soil-moisture sensor (optional)",soil_moisture_sensor_help:"Optional. A sensor reporting this zone's soil moisture in percent (higher = wetter). With a skip threshold set below, an automatic run skips this zone whenever the reading is above the threshold and resets the zone's bucket. Leave empty to disable. An unavailable or non-numeric reading never blocks watering (fail-open).",soil_moisture_threshold:"Skip above soil moisture (%)",soil_moisture_threshold_help:"On an automatic run, skip this zone (and reset its bucket to 0) when the soil-moisture sensor reads strictly above this percentage. Needs a soil-moisture sensor set above. Only affects scheduled runs; manual runs always water.",irrigate_now:"Irrigate Now",bucket_threshold:"Minimum deficit to irrigate",plant_type:"Plant type",kc:"Crop coefficient (Kc)",plant_types:{custom:"Custom (set Kc manually)",lawn:"Lawn / turf",vegetables:"Vegetable garden",flowers:"Flower bed",shrubs:"Shrubs",trees:"Trees",xeriscape:"Xeriscape / drought-tolerant"},soil_type:"Soil type",soil_types:{custom:"Custom (set rate manually)",sand:"Sandy (fast draining)",loam:"Loam (balanced)",silt:"Silt (slow draining)",clay:"Clay (very slow draining)"},distributor:"Water distributor",distributor_help:"Assign this zone to an outlet of a mechanical water distributor. The distributor's inlet valve and its pulse-advance sequence then water this zone, so the zone's own valve and schedule below are managed by the distributor.",distributor_none:"None (own valve)",outlet_number:"Outlet number",distributor_managed_note:"This zone is watered through a distributor (outlet above). Its valve, inlet control and flow sensor are managed by the distributor and hidden here — only the calculation and soil-moisture veto settings remain. To give the zone its own valve again, set the distributor above to “None (own valve)”.",outlet_number_readonly_help:"Which outlet of the distributor feeds this zone. Set on the distributor page — open it with the button.",configure_on_distributor:"Configure on distributor"},no_items:"There are no zones defined yet.",title:"Zones",status:{decision_disabled:"Turned off — this zone won't be watered automatically.",decision_water:"Watering needed: about {duration} on the next scheduled run.",decision_water_at:"Will water about {duration} at {time}.",decision_water_skip:"Deficit ~{duration}, but the next run will likely be skipped ({reason}).",decision_water_no_schedule:"Deficit ~{duration} — no schedule waters this zone; trigger it manually.",decision_no_water:"No watering needed right now — the soil has enough moisture.",decision_unknown:"Not calculated yet — press Update, then Calculate to check.",last_checked:"Last checked",never:"never",saved:"Saved",estimate_now:"Now",estimate_tag:"est.",estimate_method:{hourly:"Live estimate from hourly weather since the last calculation",hourly_sensor:"Live estimate from hourly sensor readings since the last calculation",proxy:"Estimate distributed from today's forecast since the last calculation"}},fault:{title:"Last run failed",valve_no_response:"The valve didn't respond — no water was delivered, so the bucket was left unchanged.",flow_never_started:"No flow was detected — no water was delivered, so the bucket was left unchanged.",station_never_ran:"The OpenSprinkler controller never ran the station — no water was delivered, so the bucket was left unchanged.",station_unresolved:"The OpenSprinkler station could not be found — the run was not started, so the bucket was left unchanged.",station_wrong_mode:"An OpenSprinkler station is linked, but the zone's watering mode is not OpenSprinkler station — the run was refused, so the bucket was left unchanged.",generic:"The last irrigation run failed."},skip:{title:"Skipped",soil_moisture:"Soil moisture {observed} % > {threshold} %"},clamped:{title:"Duration capped",detail:"This zone needs longer than its maximum duration of {maximum}, so part of the deficit is left unwatered on every run. Deepening the bucket threshold has no effect until the cap is raised."},help:{bucket:"Soil-moisture balance. A negative value means the soil is dry and the zone needs water.",calculate:"Works out how long to water from the latest data. Run this after Update.",update:"Fetches the latest weather/sensor data for this zone.",irrigate_link_entity:"Link a switch/valve in this zone's settings to enable manual watering.",irrigate_all:"Opens the linked valves now for every zone with a deficit. Skip conditions (rain, wind, temperature) are ignored.",update_all:"Collects the latest weather/sensor data for all zones. Does not change durations on its own.",calculate_all:"Recomputes each automatic zone's watering duration from the data collected so far."},outlook:{next_run:"Next run",estimated:"estimated",estimated_help:"The start time is still a projection: the run is sized from the water demand read shortly before it begins, so this time moves until then.",no_schedule:"No automatic schedule — zones water only when you trigger them.",setup_schedule:"Set up a schedule",targets_all:"all zones",targets_zones:"{count} zones",will_skip:"Next run will likely be skipped",will_run:"Conditions look clear for the next run.",why_skipped:"Why?",provisional:"forecast — may change",active_guards:"Active guards",last_run:"Last run",last_run_skipped:"skipped",last_run_ran:"ran",today:"today",tomorrow:"tomorrow",actions:{irrigate:"Water",calculate:"Recalculate",update:"Refresh data"},checks:{precipitation:"Rain forecast",days_between:"Days between watering",temperature:"Low temperature",wind:"High wind",rain_sensor:"Rain sensor",freeze:"Frost",paused:"Paused (rain delay)",soil_moisture:"Soil moisture",no_demand:"No water demand"},check_detail:{precipitation:"{observed} mm (≥ {threshold} mm)",days_between:"{observed}/{threshold} days",temperature:"{observed}° (below {threshold}°)",wind:"{observed} (above {threshold})",rain_sensor:"{observed}",freeze:"{observed}° (below {threshold}°)"}},calendar:{no_data:"No watering calendar data available for this zone.",error_prefix:"Error generating calendar:",month:"Month",et:"ET (mm)",precipitation:"Precipitation (mm)",watering:"Watering (L)",avg_temp:"Avg Temp (°C)",method_prefix:"Method:"},confirm_action:{reset_bucket_title:"Reset this zone's bucket?",reset_bucket_body:"This sets the bucket back to 0, discarding the accumulated moisture balance for this zone.",reset_all_buckets_title:"Reset all buckets?",reset_all_buckets_body:"This sets every zone's bucket back to 0, discarding the accumulated moisture balance. Watering calculations start fresh from the next update.",clear_weather_title:"Clear all weather data?",clear_weather_body:"This deletes all collected weather and sensor records for every zone. Zones will need fresh data before they can calculate again."},confirm_irrigate:{title:"Start irrigation?",body:"This opens the linked valve(s) now and bypasses all skip conditions (rain, temperature, minimum days between watering).",all_linked_zones:"All linked zones",toast_started:"Irrigation started",toast_failed:"Irrigation failed"},history:{title:"Run history",total_used:"Total water used",empty:"No runs recorded yet.",when:"When",result:"Result",volume:"Volume",detail:"Detail",results:{completed:"Completed",partial:"Partial",failed:"Failed",skipped:"Skipped",observed:"Observed"}},rain_delay:{title:"Pause watering",paused:"Paused",until:"until",delay_24h:"Delay 24 h",delay_48h:"Delay 48 h",resume:"Resume"},run_zone:{run:"Run",minutes:"min",help:"Water this zone for a custom time, ignoring the calculation",toast_started:"Started run",busy_hint:"Distributor is running — you can start again once it is back in its home position."},stop_zone:{stop:"Stop",watering:"Watering…",toast_stopped:"Stopped run"}},distributors:{title:"Distributors",description:"Mechanical water distributors split one supply into several outlets, advanced by pulsing the water on and off.",no_items:"No distributors configured yet.",add:{header:"Add distributor",name_placeholder:"Distributor name",actions:{add:"Add"}},status:{saved:"Saved"},confirm_delete:"Delete this distributor? Zones assigned to it keep their outlet numbers but lose their distributor link.",labels:{name:"Name",watering_mode_help:"How the distributor's inlet valve is opened and closed.",inlet_entity:"Inlet valve / switch (optional)",inlet_entity_help:"The switch or valve entity that opens the water supply into the distributor. It is also watched for foreign pulses; once a valve is selected, a setting appears below to control the reaction.",watch_inlet:"Watch inlet valve for manual pulses",watch_inlet_help:"Only detects valve switches Home Assistant can see — purely mechanical pulses at the device stay invisible.",inlet_entity_help_service:"The ring valve Home Assistant watches for foreign pulses to keep the outlet position in sync (e.g. when the valve is opened manually or by an automation outside a HASI run). Once a valve is selected, a setting appears below to control the reaction. Actuation is via the run/stop service; this field is only read, and is NOT the flow/confirm sensor. Leave empty to disable inlet watching.",watch_mode:"On a manual inlet pulse",watch_mode_help:"How to react when the inlet valve is opened outside a Home Assistant run (only pulses Home Assistant can see).",watch_mode_count:"Count it (advance the position)",watch_mode_warn:"Warn (mark position uncertain)",watch_mode_ignore:"Ignore",run_service:"Run script",run_service_help:"Script called to open the inlet. It receives the pulse duration.",stop_service:"Stop script (optional)",stop_service_help:"Script called to close the inlet.",duration_field:"Duration field",duration_field_help:"Name of the field the run script expects the duration in.",duration_field_placeholder:"duration",duration_unit:"Duration unit",duration_units:{seconds:"Seconds",minutes:"Minutes"},confirm_entity:"Confirmation sensor (optional)",confirm_entity_help:"Optional sensor on the distributor inlet confirming water actually flows (e.g. a flow or valve-position sensor). If it reports no flow when an outlet opens, the cycle halts safely and marks the distributor uncertain — this is the low-flow / fault detection.",flow_sensor:"Flow sensor (optional)",flow_sensor_help:"The shared inlet flow-rate meter (e.g. L/min, m³/h). When set, the actual delivered volume per outlet is measured and credited instead of the time estimate. Optional. Where the valve can be stopped (a classic inlet, or a self-closing stop-service), the outlet also stops early once its target volume is reached. Both an instantaneous rate meter (e.g. L/min) and a cumulative totalizer counter (e.g. m³, or state_class: total_increasing) are supported and detected automatically from the unit.",pause_seconds:"Advance pause",skip_pulse_seconds:"Skip pulse",notify_target:"Notification target (optional)",notify_target_help:"Optional additional channel. Halts always appear in the Home Assistant notifications panel; set a notify service here (e.g. notify.mobile_app_phone) to also push them there.",notify_target_placeholder:"notify.mobile_app_phone"},notify:{halted:"Distributor '{name}' halted ({reason}). Re-sync and re-confirm required.",reason:{valve_did_not_open:"valve did not open",restart_mid_advance:"restarted mid-advance",foreign_inlet_pulse:"manual inlet pulse"}},commissioning:{title:"Commissioning",outlet:"Outlet",states:{synced:"Synced",uncertain:"Uncertain"},test_run:"Test run",test_run_help:"Waters each mapped outlet for about 30 seconds in order, so you can watch the device advance and note the pause it needs.",set_outlet:"Set current outlet",set_outlet_help:"Read the outlet number shown in the device window and set it here to re-sync the tracked position.",resync_home:"Reset to outlet 1",confirm_resync:{title:"Reset to outlet 1?",body:"This sets the tracked position to outlet 1. Only confirm if the device is physically at outlet 1 — otherwise the distributor will water the wrong outlets (an undetected desync)."},confirm_set_outlet:{title:"Set current outlet?",body:"This marks the distributor as synced at the outlet you entered. Only confirm if the device's window physically shows that outlet right now — a wrong value silently waters the wrong outlets."},confirmed:"Commissioning confirmed",confirmed_help:"Arms the distributor for automatic and manual cycles. Can only be set while the position is synced, and drops to off automatically if the position ever becomes uncertain.",needs_sync:"Set the position to synced before you can arm this distributor.",run_now:"Run now",run_now_help:"Runs one full manual cycle over all mapped outlets.",run_now_active:"A cycle is already running.",confirm_dialog:{title:"Arm this distributor?",body:"Confirm the device is physically at outlet 1 and every outlet is mapped to the right zone. Automatic and manual cycles will start pulsing the inlet.",confirm:"Confirm & arm"}},hints:{pressure:"Give the distributor at least 1 bar of water pressure and 20 l/h of flow. Mechanical distributors need a firm pulse to advance reliably.",below_floor_pause:"Very short pause. The advance pulse must be long enough for the distributor to actually step; the backend enforces a minimum of 10 seconds.",below_floor_skip:"Very short skip pulse. The backend enforces a minimum of 10 seconds.",undetectable:"The device's manual selector button cannot be read back. If you turn it by hand, use “Set current outlet” afterwards so the tracked position matches.",outlet_change:"Changing an outlet mapping moves the device off its known position. Re-sync and re-confirm commissioning before the next cycle.",parallel_draw:"Parallel sequencing opens several zones at once, but a distributor feeds one outlet at a time, so its mapped zones still water in sequence. Plan the supply draw accordingly.",master_off_after:"With sequential or rotating sequencing and “master off after each zone”, the pump is switched per outlet, so expect it to cycle between every outlet of the distributor.",experimental:"Experimental feature — still being refined and not fully hardware-tested. Watch the first days of use closely and keep the device's manual override within reach."},outlets:{title:"Outlets / zones",help:"Set how many outlets the distributor has, then assign a zone to each. Only zones without their own valve or script can be assigned — a zone is either on a distributor or has its own valve. The number of outlets equals the number of assigned zones, numbered contiguously from 1.",count:"Number of outlets",none:"— none",no_zones:"No zones yet. Create zones first (Setup → Zones), then assign them here.",gap_warning:"Outlets must be filled contiguously from 1 — assign a zone to every outlet up to the highest used one."}}},rs="Smart Irrigation",ls={title:"Weather Service",description:"Configure which weather service to use for ET calculations and skip conditions.",enabled_label:"Enable weather service",service_label:"Weather service",api_key_label:"API key",api_key_placeholder:"Leave blank to keep existing key",api_key_configured:"API key is configured",api_key_not_configured:"No API key configured",api_key_help:"An API key from your chosen weather service provider. Open-Meteo does not require a key. OpenWeatherMap, Pirate Weather and the Met Office (Weather DataHub) all offer free tiers.",no_api_key_needed:"Open-Meteo is a free service and requires no API key.",save_button:"Save weather settings",saved:"Weather settings saved",owm:"OpenWeatherMap",pw:"Pirate Weather",openmeteo:"Open-Meteo (free, no key needed)",met:"Met Office (UK)",test_button:"Test Connection",test_button_testing:"Testing…",test_success:"✓ Connection successful",test_error_invalid_auth:"✗ Invalid API key — check that it is correct and active",test_error_cannot_connect:"✗ Cannot connect — check your internet connection",test_error_no_service:"✗ Select a weather service first",test_error_unknown:"✗ Test failed — unknown error"},ds={title:"Irrigation Start Triggers",description:"Configure when irrigation should start based on solar events. You can add multiple triggers for different schedules. For sunrise triggers, leaving offset at 0 will automatically use the total duration of all enabled zones.",add_trigger:"Add Trigger",edit_trigger:"Edit Trigger",delete_trigger:"Delete Trigger",trigger_types:{sunrise:"Sunrise",sunset:"Sunset",solar_azimuth:"Solar Azimuth"},fields:{name:{name:"Trigger Name",description:"A descriptive name to identify this trigger"},type:{name:"Trigger Type",description:"The type of solar event to trigger on"},enabled:{name:"Enabled",description:"Whether this trigger is currently active"},offset_minutes:{name:"Offset (minutes)",description:"Minutes before (-) or after (+) the solar event. For sunrise triggers, use 0 for automatic timing based on total zone duration."},azimuth_angle:{name:"Azimuth Angle (degrees)",description:"Solar azimuth angle in degrees where 0=North, 90=East, 180=South, 270=West"},account_for_duration:{name:"Account for Duration",description:"When enabled, irrigation will start early enough to finish at the specified time. When disabled, irrigation will start exactly at the specified time."}},dialog:{add_title:"Add Irrigation Start Trigger",edit_title:"Edit Irrigation Start Trigger",cancel:"Cancel",save:"Save",delete:"Delete"},no_triggers:"No irrigation start triggers configured. The system will use the default behavior (sunrise with total zone duration). Add triggers to customize when irrigation starts.",offset_auto:"Auto (calculated from total zone duration)",confirm_delete:"Are you sure you want to delete the trigger '{name}'?",validation:{name_required:"Trigger name is required",azimuth_invalid:"Azimuth angle must be a valid number"},help:{sunrise_offset:"For sunrise triggers: Use negative values to start before sunrise, positive to start after. Set to 0 to automatically start early enough to complete all zones before sunrise.",sunset_offset:"For sunset triggers: Use negative values to start before sunset, positive to start after sunset.",azimuth_explanation:"Solar azimuth is the compass direction of the sun. 0°=North, 90°=East, 180°=South, 270°=West. You can enter any angle value (e.g., 450° = 90°, -30° = 330°). Use this to trigger irrigation when the sun reaches a specific position.",multiple_triggers:"You can configure multiple triggers. Each enabled trigger will independently schedule irrigation starts."}},cs={title:"Skip Conditions",description:"Automatically skip irrigation when conditions are unfavorable. Precipitation check requires a weather service. Temperature and wind checks also require a weather service.",threshold_label:"Precipitation Threshold",threshold_description:"Minimum total precipitation (in mm) forecast across the look-ahead window to skip irrigation.",lookahead_label:"Forecast look-ahead (days)",lookahead_help:"How many upcoming forecast days to add up when checking for rain. The forecast starts at tomorrow (today is excluded), so 1 = just the next day, 2 = the next two days, and so on.",temp_section_title:"Skip on low temperature",temp_threshold_label:"Skip if temperature is below",wind_section_title:"Skip on high wind speed",wind_threshold_label:"Skip if wind speed is above",rain_sensor_section_title:"Skip on rain sensor",rain_sensor_label:"Rain sensor entity (optional)",rain_sensor_placeholder:"e.g. binary_sensor.rain",freeze_section_title:"Skip on frost",freeze_threshold_label:"Skip if minimum temperature is below",freeze_help:"Compares the current temperature and the coming night's forecast low; skips watering when frost is expected, to protect pipes and plants.",forecast_rain_label:"When rain is forecast",forecast_rain_options:{ignore:"Ignore it",water_less:"Water less",skip:"Skip watering"},forecast_rain_help:{ignore:"Forecast rain is ignored; runs use the calculated duration.",water_less:"Upcoming forecast rain trims the run duration (the deficit stays in the bucket for the real rain to fill).",skip:"Skip the run entirely when enough rain is forecast within the look-ahead window."}},hs={title:"Location Coordinates",description:"Configure location coordinates for weather data retrieval. You can use manual coordinates different from your Home Assistant location if needed.",manual_enabled:"Use manual coordinates",use_ha_location:"Use Home Assistant location",latitude:"Latitude (decimal degrees)",longitude:"Longitude (decimal degrees)",elevation:"Elevation (meters above sea level)",current_ha_coords:"Current Home Assistant coordinates"},us={title:"Days Between Irrigation",description:"Configure the minimum number of days that must pass between irrigation events. This helps control watering frequency for water conservation and plant health management.\n\nTypical real-world use cases:\n• Lawn care: 1-2 day intervals prevent overwatering\n• Drought restrictions: 6+ day intervals for weekly watering\n• Deep-rooted plants: 3-7 day intervals for less frequent watering\n• Water conservation: Customizable based on climate and soil conditions",label:"Minimum days between irrigation",help_text:"Set to 0 to disable this feature. Values from 1-365 days are supported. This setting works alongside existing precipitation forecasting logic."},ps={title:"Zone Sequencing",description:"When multiple zones need irrigation, choose whether they run at the same time or one after another. Sequential mode waits for each zone to finish before starting the next. Rotating mode cycles through zones, giving each one a limited consecutive run before moving to the next.",parallel:"Parallel (all zones at once)",sequential:"Sequential (one zone at a time)",rotating:"Rotating (zones take turns)",max_consecutive_duration_label:"Max consecutive run time per zone",max_consecutive_duration_unit:"minutes",min_absorption_time_label:"Min. absorption time between slots",min_absorption_time_unit:"minutes (0 = disabled)"},gs={title:"Pump / master switch",description:"Optional. Powers a shared master — a pump or main valve — on before the first zone of a watering cycle, then optionally off after the last zone. Leave the entity empty to never touch a master (e.g. a pressure-controlled waterworks that starts on its own).",entity:"Master entity (switch/valve)",kick_enabled:"Kicker: pulse off then on to force a pump start",kick_pause:"Kick pause (off before on)",settle:"Settle delay before the first zone",off_after:"Turn the master off after irrigation",seconds_unit:"seconds"},ms={zone_size:"The total irrigated area of this zone. Used with throughput to calculate how much water is applied per run.",zone_throughput:"Total water flow of your irrigation system for this zone (litres/min in metric, gal/min in imperial). Check your sprinkler datasheet or measure by timing how long it takes to fill a known container.",zone_drainage_rate:"How fast saturated soil drains excess water. ~20 mm/h suits medium/loam soil; lower (2–10) for heavy clay, higher for sandy soil.",zone_bucket:"Current water deficit (negative) or surplus (positive) for this zone. Irrigation triggers when bucket drops below the threshold.",zone_maximum_bucket:"Maximum moisture surplus the zone can hold. Water above this level is treated as runoff. Typical value: 50 mm.",zone_bucket_threshold:"Irrigation triggers when the bucket drops below this value. Must be 0 or negative. 0 means irrigate whenever there is any deficit.",zone_multiplier:"Scale factor applied to the calculated duration. Use above 1.0 to increase, below 1.0 to decrease. Useful for fine-tuning without changing physical measurements.",zone_lead_time:"Extra seconds added before irrigation starts. Use for pump warm-up or system pressurisation.",zone_maximum_duration:"Hard cap on any single irrigation run in seconds. Prevents runaway watering. Default: 3600 s (1 hour).",zone_linked_entity:"The HA switch, valve or input_boolean (helper) entity controlling water flow for this zone. This entity is turned on when irrigation runs.",zone_flow_sensor:"Optional sensor measuring actual water flow rate. Used for reporting only — does not affect duration calculations.",general_autoupdatedelay:"Seconds to wait after HA starts before the first weather data fetch. Allows other integrations to initialise first.",general_sensor_debounce:"Minimum gap in milliseconds between sensor readings to filter noise from rapidly changing sensors.",general_calctime:"Time of day when irrigation durations are recalculated from collected weather data. Format: HH:MM (24-hour).",general_cleardatatime:"Time of day when old weather data is purged. Must be set later than the calculation time.",general_days_between:"Minimum days between irrigation events for the same zone. Set to 0 to disable (irrigate whenever deficit exists).",general_autoupdateinterval:"How often weather data is collected. Choose a value that balances fresh data against API rate limits.",general_precipitation_threshold:"Irrigation is skipped if total forecast precipitation across the look-ahead window exceeds this amount.",general_temp_threshold:"Irrigation is skipped if the current temperature is below this value (e.g. to prevent frost damage).",general_wind_threshold:"Irrigation is skipped if wind speed exceeds this value (high winds reduce efficiency and cause drift).",zone_plant_type:"Pick a plant type to set a typical crop coefficient, or choose Custom to enter Kc yourself.",zone_kc:"Scales reference (grass) ET to this zone's plants. 1.0 = reference grass; lower for drought-tolerant planting, higher for thirsty crops. Only the ET term is scaled — rain is not.",zone_soil_type:"Pick a soil type to set a typical drainage rate, or leave Custom to enter it by hand below.",distributor_pause_seconds:"Off-time between outlets. This is the pulse that advances the distributor to the next outlet; set it from what you saw during the test run. Minimum 10 seconds.",distributor_skip_pulse_seconds:"Short on/off pulse used to step past an outlet that has no zone mapped, without watering it. Minimum 10 seconds."},vs={title:"Setup Wizard",open_button:"Setup Wizard",close:"Close",next:"Next",back:"Back",finish:"Finish",skip_step:"Skip this step",step_indicator:"Step {current} of {total}",stepper:{weather:"Weather",module:"Module",mapping:"Sensor Group",zone:"Zone"},setup_complete_banner:"Setup not complete. Run the wizard to get started.",open_wizard:"Open Wizard",steps:{welcome:{title:"Welcome to Smart Irrigation",intro:"This wizard guides you through the four steps needed to get your first zone irrigating automatically.",step1_label:"Weather Service — where to get weather data",step2_label:"Calculation Module — how irrigation duration is computed",step3_label:"Sensor Group — which data sources to use",step4_label:"Zone — your first irrigation zone",tip:"You can skip any step and configure it later from the Setup tab."},weather:{title:"Weather Service",description:"Choose how to get weather data. Open-Meteo is free and requires no API key — it is the easiest choice for most users."},module:{title:"Calculation Module",description:"A module calculates how long to irrigate based on evapotranspiration (ET). The PyETO module (FAO-56 method) is recommended for most users.",pick_label:"Select module type",no_modules:"No module types available."},mapping:{title:"Sensor Group",description:"A sensor group links each weather variable to a data source. Set the key variables below — you can refine individual sensor mappings later from the Setup → Sensor Groups tab.",name_label:"Sensor group name",source_label:"Data source for",use_weather_service:"Weather service",use_sensor:"Sensor",use_static:"Static value",use_none:"None / not used"},zone:{title:"First Zone",description:"A zone is one irrigation area (e.g. lawn, garden bed). Set the physical properties so the system can calculate the correct irrigation duration.",name_label:"Zone name",size_label:"Area",throughput_label:"Sprinkler throughput",entity_label:"Linked switch, valve or helper",entity_placeholder:"e.g. switch.garden_valve",module_label:"Calculation module",mapping_label:"Sensor group"},done:{title:"Setup Complete!",description:"Your first zone is ready. Smart Irrigation will now calculate irrigation durations automatically based on weather data.",next_steps:"What you can do next:",tip1:"Go to Zones to view calculated durations and bucket values.",tip2:"Add more zones from the Zones tab.",tip3:"Refine all settings from the Setup tab.",go_zones:"Go to Zones",go_setup:"Go to Setup",schedule_name:"Daily",schedule_title:"Create a watering schedule",schedule_desc:"Your system is configured, but it won't water until a schedule exists. Create a daily schedule for all zones now (you can change or remove it later under Setup → When to Water).",schedule_create:"Create daily schedule",schedule_created:"Daily schedule created."}},confirm_close:{body:"Close the setup wizard? Your progress so far is saved.",keep:"Keep editing",close:"Close"}},fs={flow_calibration:ts,common:is,defaults:ss,module:as,calcmodules:ns,panels:os,title:rs,weather_service_config:ls,irrigation_start_triggers:ds,weather_skip:cs,coordinate_config:hs,days_between_irrigation:us,zone_sequencing:ps,master:gs,field_help:ms,wizard:vs},_s=Object.freeze({__proto__:null,calcmodules:ns,common:is,coordinate_config:hs,days_between_irrigation:us,default:fs,defaults:ss,field_help:ms,flow_calibration:ts,irrigation_start_triggers:ds,master:gs,module:as,panels:os,title:rs,weather_service_config:ls,weather_skip:cs,wizard:vs,zone_sequencing:ps});function bs(e,t){const i=t&&t.cache?t.cache:Ss,s=t&&t.serializer?t.serializer:ks;return(t&&t.strategy?t.strategy:xs)(e,{cache:i,serializer:s})}function ys(e,t,i,s){const a=null==(n=s)||"number"==typeof n||"boolean"==typeof n?s:i(s);var n;let o=t.get(a);return void 0===o&&(o=e.call(this,s),t.set(a,o)),o}function ws(e,t,i){const s=Array.prototype.slice.call(arguments,3),a=i(s);let n=t.get(a);return void 0===n&&(n=e.apply(this,s),t.set(a,n)),n}function $s(e,t,i,s,a){return i.bind(t,e,s,a)}function xs(e,t){return $s(e,this,1===e.length?ys:ws,t.cache.create(),t.serializer)}const ks=function(){return JSON.stringify(arguments)};var zs=class{constructor(){this.cache=Object.create(null)}get(e){return this.cache[e]}set(e,t){this.cache[e]=t}};const Ss={create:function(){return new zs}},As={variadic:function(e,t){return $s(e,this,ws,t.cache.create(),t.serializer)}},Es=/(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;function Cs(e){const t={};return e.replace(Es,e=>{const i=e.length;switch(e[0]){case"G":t.era=4===i?"long":5===i?"narrow":"short";break;case"y":t.year=2===i?"2-digit":"numeric";break;case"Y":case"u":case"U":case"r":throw new RangeError("`Y/u/U/r` (year) patterns are not supported, use `y` instead");case"q":case"Q":throw new RangeError("`q/Q` (quarter) patterns are not supported");case"M":case"L":t.month=["numeric","2-digit","short","long","narrow"][i-1];break;case"w":case"W":throw new RangeError("`w/W` (week) patterns are not supported");case"d":t.day=["numeric","2-digit"][i-1];break;case"D":case"F":case"g":throw new RangeError("`D/F/g` (day) patterns are not supported, use `d` instead");case"E":t.weekday=4===i?"long":5===i?"narrow":"short";break;case"e":if(i<4)throw new RangeError("`e..eee` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][i-4];break;case"c":if(i<4)throw new RangeError("`c..ccc` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][i-4];break;case"a":t.hour12=!0;break;case"b":case"B":throw new RangeError("`b/B` (period) patterns are not supported, use `a` instead");case"h":t.hourCycle="h12",t.hour=["numeric","2-digit"][i-1];break;case"H":t.hourCycle="h23",t.hour=["numeric","2-digit"][i-1];break;case"K":t.hourCycle="h11",t.hour=["numeric","2-digit"][i-1];break;case"k":t.hourCycle="h24",t.hour=["numeric","2-digit"][i-1];break;case"j":case"J":case"C":throw new RangeError("`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead");case"m":t.minute=["numeric","2-digit"][i-1];break;case"s":t.second=["numeric","2-digit"][i-1];break;case"S":case"A":throw new RangeError("`S/A` (second) patterns are not supported, use `s` instead");case"z":t.timeZoneName=i<4?"short":"long";break;case"Z":case"O":case"v":case"V":case"X":case"x":throw new RangeError("`Z/O/v/V/X/x` (timeZone) patterns are not supported, use `z` instead")}return""}),t}const Ts=/[\t-\r \x85\u200E\u200F\u2028\u2029]/i;function Os(e){return e.replace(/^(.*?)-/,"")}const Hs=/^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g,Ds=/^(@+)?(\+|#+)?[rs]?$/g,Ms=/(\*)(0+)|(#+)(0+)|(0+)/g,Is=/^(0+)$/;function Ns(e){const t={};return"r"===e[e.length-1]?t.roundingPriority="morePrecision":"s"===e[e.length-1]&&(t.roundingPriority="lessPrecision"),e.replace(Ds,function(e,i,s){return"string"!=typeof s?(t.minimumSignificantDigits=i.length,t.maximumSignificantDigits=i.length):"+"===s?t.minimumSignificantDigits=i.length:"#"===i[0]?t.maximumSignificantDigits=i.length:(t.minimumSignificantDigits=i.length,t.maximumSignificantDigits=i.length+("string"==typeof s?s.length:0)),""}),t}function Ps(e){switch(e){case"sign-auto":return{signDisplay:"auto"};case"sign-accounting":case"()":return{currencySign:"accounting"};case"sign-always":case"+!":return{signDisplay:"always"};case"sign-accounting-always":case"()!":return{signDisplay:"always",currencySign:"accounting"};case"sign-except-zero":case"+?":return{signDisplay:"exceptZero"};case"sign-accounting-except-zero":case"()?":return{signDisplay:"exceptZero",currencySign:"accounting"};case"sign-never":case"+_":return{signDisplay:"never"}}}function Ls(e){let t;if("E"===e[0]&&"E"===e[1]?(t={notation:"engineering"},e=e.slice(2)):"E"===e[0]&&(t={notation:"scientific"},e=e.slice(1)),t){const i=e.slice(0,2);if("+!"===i?(t.signDisplay="always",e=e.slice(2)):"+?"===i&&(t.signDisplay="exceptZero",e=e.slice(2)),!Is.test(e))throw new Error("Malformed concise eng/scientific notation");t.minimumIntegerDigits=e.length}return t}function Rs(e){const t=Ps(e);return t||{}}function Bs(e){let t={};for(const i of e){switch(i.stem){case"percent":case"%":t.style="percent";continue;case"%x100":t.style="percent",t.scale=100;continue;case"currency":t.style="currency",t.currency=i.options[0];continue;case"group-off":case",_":t.useGrouping=!1;continue;case"precision-integer":case".":t.maximumFractionDigits=0;continue;case"measure-unit":case"unit":t.style="unit",t.unit=Os(i.options[0]);continue;case"compact-short":case"K":t.notation="compact",t.compactDisplay="short";continue;case"compact-long":case"KK":t.notation="compact",t.compactDisplay="long";continue;case"scientific":t={...t,notation:"scientific",...i.options.reduce((e,t)=>({...e,...Rs(t)}),{})};continue;case"engineering":t={...t,notation:"engineering",...i.options.reduce((e,t)=>({...e,...Rs(t)}),{})};continue;case"notation-simple":t.notation="standard";continue;case"unit-width-narrow":t.currencyDisplay="narrowSymbol",t.unitDisplay="narrow";continue;case"unit-width-short":t.currencyDisplay="code",t.unitDisplay="short";continue;case"unit-width-full-name":t.currencyDisplay="name",t.unitDisplay="long";continue;case"unit-width-iso-code":t.currencyDisplay="symbol";continue;case"scale":t.scale=parseFloat(i.options[0]);continue;case"rounding-mode-floor":t.roundingMode="floor";continue;case"rounding-mode-ceiling":t.roundingMode="ceil";continue;case"rounding-mode-down":t.roundingMode="trunc";continue;case"rounding-mode-up":t.roundingMode="expand";continue;case"rounding-mode-half-even":t.roundingMode="halfEven";continue;case"rounding-mode-half-down":t.roundingMode="halfTrunc";continue;case"rounding-mode-half-up":t.roundingMode="halfExpand";continue;case"integer-width":if(i.options.length>1)throw new RangeError("integer-width stems only accept a single optional option");i.options[0].replace(Ms,function(e,i,s,a,n,o){if(i)t.minimumIntegerDigits=s.length;else{if(a&&n)throw new Error("We currently do not support maximum integer digits");if(o)throw new Error("We currently do not support exact integer digits")}return""});continue}if(Is.test(i.stem)){t.minimumIntegerDigits=i.stem.length;continue}if(Hs.test(i.stem)){if(i.options.length>1)throw new RangeError("Fraction-precision stems only accept a single optional option");i.stem.replace(Hs,function(e,i,s,a,n,o){return"*"===s?t.minimumFractionDigits=i.length:a&&"#"===a[0]?t.maximumFractionDigits=a.length:n&&o?(t.minimumFractionDigits=n.length,t.maximumFractionDigits=n.length+o.length):(t.minimumFractionDigits=i.length,t.maximumFractionDigits=i.length),""});const e=i.options[0];"w"===e?t={...t,trailingZeroDisplay:"stripIfInteger"}:e&&(t={...t,...Ns(e)});continue}if(Ds.test(i.stem)){t={...t,...Ns(i.stem)};continue}const e=Ps(i.stem);e&&(t={...t,...e});const s=Ls(i.stem);s&&(t={...t,...s})}return t}let Us=function(e){return e[e.EXPECT_ARGUMENT_CLOSING_BRACE=1]="EXPECT_ARGUMENT_CLOSING_BRACE",e[e.EMPTY_ARGUMENT=2]="EMPTY_ARGUMENT",e[e.MALFORMED_ARGUMENT=3]="MALFORMED_ARGUMENT",e[e.EXPECT_ARGUMENT_TYPE=4]="EXPECT_ARGUMENT_TYPE",e[e.INVALID_ARGUMENT_TYPE=5]="INVALID_ARGUMENT_TYPE",e[e.EXPECT_ARGUMENT_STYLE=6]="EXPECT_ARGUMENT_STYLE",e[e.INVALID_NUMBER_SKELETON=7]="INVALID_NUMBER_SKELETON",e[e.INVALID_DATE_TIME_SKELETON=8]="INVALID_DATE_TIME_SKELETON",e[e.EXPECT_NUMBER_SKELETON=9]="EXPECT_NUMBER_SKELETON",e[e.EXPECT_DATE_TIME_SKELETON=10]="EXPECT_DATE_TIME_SKELETON",e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE=11]="UNCLOSED_QUOTE_IN_ARGUMENT_STYLE",e[e.EXPECT_SELECT_ARGUMENT_OPTIONS=12]="EXPECT_SELECT_ARGUMENT_OPTIONS",e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE=13]="EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE=14]="INVALID_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR=15]="EXPECT_SELECT_ARGUMENT_SELECTOR",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR=16]="EXPECT_PLURAL_ARGUMENT_SELECTOR",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT=17]="EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT=18]="EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT",e[e.INVALID_PLURAL_ARGUMENT_SELECTOR=19]="INVALID_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR=20]="DUPLICATE_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR=21]="DUPLICATE_SELECT_ARGUMENT_SELECTOR",e[e.MISSING_OTHER_CLAUSE=22]="MISSING_OTHER_CLAUSE",e[e.INVALID_TAG=23]="INVALID_TAG",e[e.INVALID_TAG_NAME=25]="INVALID_TAG_NAME",e[e.UNMATCHED_CLOSING_TAG=26]="UNMATCHED_CLOSING_TAG",e[e.UNCLOSED_TAG=27]="UNCLOSED_TAG",e}({});function js(e){return 0===e.type}function Fs(e){return 1===e.type}function Zs(e){return 2===e.type}function Ws(e){return 3===e.type}function qs(e){return 4===e.type}function Gs(e){return 5===e.type}function Ks(e){return 6===e.type}function Vs(e){return 7===e.type}function Ys(e){return 8===e.type}function Xs(e){return!(!e||"object"!=typeof e||0!==e.type)}function Js(e){return!(!e||"object"!=typeof e||1!==e.type)}const Qs=/[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/,ea={"001":["H","h"],419:["h","H","hB","hb"],AC:["H","h","hb","hB"],AD:["H","hB"],AE:["h","hB","hb","H"],AF:["H","hb","hB","h"],AG:["h","hb","H","hB"],AI:["H","h","hb","hB"],AL:["h","H","hB"],AM:["H","hB"],AO:["H","hB"],AR:["h","H","hB","hb"],AS:["h","H"],AT:["H","hB"],AU:["h","hb","H","hB"],AW:["H","hB"],AX:["H"],AZ:["H","hB","h"],BA:["H","hB","h"],BB:["h","hb","H","hB"],BD:["h","hB","H"],BE:["H","hB"],BF:["H","hB"],BG:["H","hB","h"],BH:["h","hB","hb","H"],BI:["H","h"],BJ:["H","hB"],BL:["H","hB"],BM:["h","hb","H","hB"],BN:["hb","hB","h","H"],BO:["h","H","hB","hb"],BQ:["H"],BR:["H","hB"],BS:["h","hb","H","hB"],BT:["h","H"],BW:["H","h","hb","hB"],BY:["H","h"],BZ:["H","h","hb","hB"],CA:["h","hb","H","hB"],CC:["H","h","hb","hB"],CD:["hB","H"],CF:["H","h","hB"],CG:["H","hB"],CH:["H","hB","h"],CI:["H","hB"],CK:["H","h","hb","hB"],CL:["h","H","hB","hb"],CM:["H","h","hB"],CN:["H","hB","hb","h"],CO:["h","H","hB","hb"],CP:["H"],CR:["h","H","hB","hb"],CU:["h","H","hB","hb"],CV:["H","hB"],CW:["H","hB"],CX:["H","h","hb","hB"],CY:["h","H","hb","hB"],CZ:["H"],DE:["H","hB"],DG:["H","h","hb","hB"],DJ:["h","H"],DK:["H"],DM:["h","hb","H","hB"],DO:["h","H","hB","hb"],DZ:["h","hB","hb","H"],EA:["H","h","hB","hb"],EC:["h","H","hB","hb"],EE:["H","hB"],EG:["h","hB","hb","H"],EH:["h","hB","hb","H"],ER:["h","H"],ES:["H","hB","h","hb"],ET:["hB","hb","h","H"],FI:["H"],FJ:["h","hb","H","hB"],FK:["H","h","hb","hB"],FM:["h","hb","H","hB"],FO:["H","h"],FR:["H","hB"],GA:["H","hB"],GB:["H","h","hb","hB"],GD:["h","hb","H","hB"],GE:["H","hB","h"],GF:["H","hB"],GG:["H","h","hb","hB"],GH:["h","H"],GI:["H","h","hb","hB"],GL:["H","h"],GM:["h","hb","H","hB"],GN:["H","hB"],GP:["H","hB"],GQ:["H","hB","h","hb"],GR:["h","H","hb","hB"],GS:["H","h","hb","hB"],GT:["h","H","hB","hb"],GU:["h","hb","H","hB"],GW:["H","hB"],GY:["h","hb","H","hB"],HK:["h","hB","hb","H"],HN:["h","H","hB","hb"],HR:["H","hB"],HU:["H","h"],IC:["H","h","hB","hb"],ID:["H"],IE:["H","h","hb","hB"],IL:["H","hB"],IM:["H","h","hb","hB"],IN:["h","H"],IO:["H","h","hb","hB"],IQ:["h","hB","hb","H"],IR:["hB","H"],IS:["H"],IT:["H","hB"],JE:["H","h","hb","hB"],JM:["h","hb","H","hB"],JO:["h","hB","hb","H"],JP:["H","K","h"],KE:["hB","hb","H","h"],KG:["H","h","hB","hb"],KH:["hB","h","H","hb"],KI:["h","hb","H","hB"],KM:["H","h","hB","hb"],KN:["h","hb","H","hB"],KP:["h","H","hB","hb"],KR:["h","H","hB","hb"],KW:["h","hB","hb","H"],KY:["h","hb","H","hB"],KZ:["H","hB"],LA:["H","hb","hB","h"],LB:["h","hB","hb","H"],LC:["h","hb","H","hB"],LI:["H","hB","h"],LK:["H","h","hB","hb"],LR:["h","hb","H","hB"],LS:["h","H"],LT:["H","h","hb","hB"],LU:["H","h","hB"],LV:["H","hB","hb","h"],LY:["h","hB","hb","H"],MA:["H","h","hB","hb"],MC:["H","hB"],MD:["H","hB"],ME:["H","hB","h"],MF:["H","hB"],MG:["H","h"],MH:["h","hb","H","hB"],MK:["H","h","hb","hB"],ML:["H"],MM:["hB","hb","H","h"],MN:["H","h","hb","hB"],MO:["h","hB","hb","H"],MP:["h","hb","H","hB"],MQ:["H","hB"],MR:["h","hB","hb","H"],MS:["H","h","hb","hB"],MT:["H","h"],MU:["H","h"],MV:["H","h"],MW:["h","hb","H","hB"],MX:["h","H","hB","hb"],MY:["hb","hB","h","H"],MZ:["H","hB"],NA:["h","H","hB","hb"],NC:["H","hB"],NE:["H"],NF:["H","h","hb","hB"],NG:["H","h","hb","hB"],NI:["h","H","hB","hb"],NL:["H","hB"],NO:["H","h"],NP:["H","h","hB"],NR:["H","h","hb","hB"],NU:["H","h","hb","hB"],NZ:["h","hb","H","hB"],OM:["h","hB","hb","H"],PA:["h","H","hB","hb"],PE:["h","H","hB","hb"],PF:["H","h","hB"],PG:["h","H"],PH:["h","hB","hb","H"],PK:["h","hB","H"],PL:["H","h"],PM:["H","hB"],PN:["H","h","hb","hB"],PR:["h","H","hB","hb"],PS:["h","hB","hb","H"],PT:["H","hB"],PW:["h","H"],PY:["h","H","hB","hb"],QA:["h","hB","hb","H"],RE:["H","hB"],RO:["H","hB"],RS:["H","hB","h"],RU:["H"],RW:["H","h"],SA:["h","hB","hb","H"],SB:["h","hb","H","hB"],SC:["H","h","hB"],SD:["h","hB","hb","H"],SE:["H"],SG:["h","hb","H","hB"],SH:["H","h","hb","hB"],SI:["H","hB"],SJ:["H"],SK:["H"],SL:["h","hb","H","hB"],SM:["H","h","hB"],SN:["H","h","hB"],SO:["h","H"],SR:["H","hB"],SS:["h","hb","H","hB"],ST:["H","hB"],SV:["h","H","hB","hb"],SX:["H","h","hb","hB"],SY:["h","hB","hb","H"],SZ:["h","hb","H","hB"],TA:["H","h","hb","hB"],TC:["h","hb","H","hB"],TD:["h","H","hB"],TF:["H","h","hB"],TG:["H","hB"],TH:["H","h"],TJ:["H","h"],TL:["H","hB","hb","h"],TM:["H","h"],TN:["h","hB","hb","H"],TO:["h","H"],TR:["H","hB"],TT:["h","hb","H","hB"],TW:["hB","hb","h","H"],TZ:["hB","hb","H","h"],UA:["H","hB","h"],UG:["hB","hb","H","h"],UM:["h","hb","H","hB"],US:["h","hb","H","hB"],UY:["h","H","hB","hb"],UZ:["H","hB","h"],VA:["H","h","hB"],VC:["h","hb","H","hB"],VE:["h","H","hB","hb"],VG:["h","hb","H","hB"],VI:["h","hb","H","hB"],VN:["H","h"],VU:["h","H"],WF:["H","hB"],WS:["h","H"],XK:["H","hB","h"],YE:["h","hB","hb","H"],YT:["H","hB"],ZA:["H","h","hb","hB"],ZM:["h","hb","H","hB"],ZW:["H","h"],"af-ZA":["H","h","hB","hb"],"ar-001":["h","hB","hb","H"],"ca-ES":["H","h","hB"],"en-001":["h","hb","H","hB"],"en-HK":["h","hb","H","hB"],"en-IL":["H","h","hb","hB"],"en-MY":["h","hb","H","hB"],"es-BR":["H","h","hB","hb"],"es-ES":["H","h","hB","hb"],"es-GQ":["H","h","hB","hb"],"fr-CA":["H","h","hB"],"gl-ES":["H","h","hB"],"gu-IN":["hB","hb","h","H"],"hi-IN":["hB","h","H"],"it-CH":["H","h","hB"],"it-IT":["H","h","hB"],"kn-IN":["hB","h","H"],"ku-SY":["H","hB"],"ml-IN":["hB","h","H"],"mr-IN":["hB","hb","h","H"],"pa-IN":["hB","hb","h","H"],"ta-IN":["hB","h","hb","H"],"te-IN":["hB","h","H"],"zu-ZA":["H","hB","hb","h"]};function ta(e){let t=e.hourCycle;if(void 0===t&&e.hourCycles&&e.hourCycles.length&&(t=e.hourCycles[0]),t)switch(t){case"h24":return"k";case"h23":return"H";case"h12":return"h";case"h11":return"K";default:throw new Error("Invalid hourCycle")}const i=e.language;let s;return"root"!==i&&(s=e.maximize().region),(ea[s||""]||ea[i||""]||ea[`${i}-001`]||ea["001"])[0]}const ia=new RegExp(`^${Qs.source}*`),sa=new RegExp(`${Qs.source}*$`);function aa(e,t){return{start:e,end:t}}const na=!!Object.fromEntries,oa=!!String.prototype.trimStart,ra=!!String.prototype.trimEnd,la=na?Object.fromEntries:function(e){const t={};for(const[i,s]of e)t[i]=s;return t},da=oa?function(e){return e.trimStart()}:function(e){return e.replace(ia,"")},ca=ra?function(e){return e.trimEnd()}:function(e){return e.replace(sa,"")},ha=new RegExp("([^\\p{White_Space}\\p{Pattern_Syntax}]*)","yu");var ua=class{constructor(e,t={}){this.message=e,this.position={offset:0,line:1,column:1},this.ignoreTag=!!t.ignoreTag,this.locale=t.locale,this.requiresOtherClause=!!t.requiresOtherClause,this.shouldParseSkeletons=!!t.shouldParseSkeletons}parse(){if(0!==this.offset())throw Error("parser can only be used once");if(this.message.length>0){const e=this.message.charCodeAt(0);if(35!==e&&39!==e&&60!==e&&123!==e&&125!==e){const e=function(e){if(0===e.length)return null;let t=1,i=1;for(let s=0;s<e.length;){const a=e.charCodeAt(s);switch(a){case 35:case 39:case 60:case 123:case 125:return null}if(10===a)t++,i=1,s++;else if(i++,a>=55296&&a<=56319&&s+1<e.length){const t=e.charCodeAt(s+1);s+=t>=56320&&t<=57343?2:1}else s++}return{offset:e.length,line:t,column:i}}(this.message);if(e){const t=this.clonePosition();return this.position=e,{val:[{type:0,value:this.message,location:aa(t,this.clonePosition())}],err:null}}}}return this.parseMessage(0,"",!1)}parseMessage(e,t,i){let s=[];for(;!this.isEOF();){const a=this.char();if(123===a){const t=this.parseArgument(e,i);if(t.err)return t;s.push(t.val)}else{if(125===a&&e>0)break;if(35!==a||"plural"!==t&&"selectordinal"!==t){if(60===a&&!this.ignoreTag&&47===this.peek()){if(i)break;return this.error(26,aa(this.clonePosition(),this.clonePosition()))}if(60===a&&!this.ignoreTag&&pa(this.peek()||0)){const i=this.parseTag(e,t);if(i.err)return i;s.push(i.val)}else{const i=this.parseLiteral(e,t);if(i.err)return i;s.push(i.val)}}else{const e=this.clonePosition();this.bump(),s.push({type:7,location:aa(e,this.clonePosition())})}}}return{val:s,err:null}}parseTag(e,t){const i=this.clonePosition();this.bump();const s=this.parseTagName();if(this.bumpSpace(),this.bumpIf("/>"))return{val:{type:0,value:`<${s}/>`,location:aa(i,this.clonePosition())},err:null};if(this.bumpIf(">")){const a=this.parseMessage(e+1,t,!0);if(a.err)return a;const n=a.val,o=this.clonePosition();if(this.bumpIf("</")){if(this.isEOF()||!pa(this.char()))return this.error(23,aa(o,this.clonePosition()));const e=this.clonePosition();return s!==this.parseTagName()?this.error(26,aa(e,this.clonePosition())):(this.bumpSpace(),this.bumpIf(">")?{val:{type:8,value:s,children:n,location:aa(i,this.clonePosition())},err:null}:this.error(23,aa(o,this.clonePosition())))}return this.error(27,aa(i,this.clonePosition()))}return this.error(23,aa(i,this.clonePosition()))}parseTagName(){const e=this.offset();for(this.bump();!this.isEOF()&&ga(this.char());)this.bump();return this.message.slice(e,this.offset())}parseLiteral(e,t){const i=this.clonePosition();let s="";for(;;){const i=this.tryParseQuote(t);if(i){s+=i;continue}const a=this.tryParseUnquoted(e,t);if(a){s+=a;continue}const n=this.tryParseLeftAngleBracket();if(!n)break;s+=n}return{val:{type:0,value:s,location:aa(i,this.clonePosition())},err:null}}tryParseLeftAngleBracket(){return this.isEOF()||60!==this.char()||!this.ignoreTag&&(pa(e=this.peek()||0)||47===e)?null:(this.bump(),"<");var e}tryParseQuote(e){if(this.isEOF()||39!==this.char())return null;switch(this.peek()){case 39:return this.bump(),this.bump(),"'";case 123:case 60:case 62:case 125:break;case 35:if("plural"===e||"selectordinal"===e)break;return null;default:return null}this.bump();const t=[this.char()];for(this.bump();!this.isEOF();){const e=this.char();if(39===e){if(39!==this.peek()){this.bump();break}t.push(39),this.bump()}else t.push(e);this.bump()}return String.fromCodePoint(...t)}tryParseUnquoted(e,t){if(this.isEOF())return null;const i=this.char();return 60===i||123===i||35===i&&("plural"===t||"selectordinal"===t)||125===i&&e>0?null:(this.bump(),String.fromCodePoint(i))}parseArgument(e,t){const i=this.clonePosition();if(this.bump(),this.bumpSpace(),this.isEOF())return this.error(1,aa(i,this.clonePosition()));if(125===this.char())return this.bump(),this.error(2,aa(i,this.clonePosition()));let s=this.parseIdentifierIfPossible().value;if(!s)return this.error(3,aa(i,this.clonePosition()));if(this.bumpSpace(),this.isEOF())return this.error(1,aa(i,this.clonePosition()));switch(this.char()){case 125:return this.bump(),{val:{type:1,value:s,location:aa(i,this.clonePosition())},err:null};case 44:return this.bump(),this.bumpSpace(),this.isEOF()?this.error(1,aa(i,this.clonePosition())):this.parseArgumentOptions(e,t,s,i);default:return this.error(3,aa(i,this.clonePosition()))}}parseIdentifierIfPossible(){const e=this.clonePosition(),t=this.offset(),i=function(e,t){return ha.lastIndex=t,ha.exec(e)[1]??""}(this.message,t),s=t+i.length;return this.bumpTo(s),{value:i,location:aa(e,this.clonePosition())}}parseArgumentOptions(e,t,i,s){let a=this.clonePosition(),n=this.parseIdentifierIfPossible().value,o=this.clonePosition();switch(n){case"":return this.error(4,aa(a,o));case"number":case"date":case"time":{this.bumpSpace();let e=null;if(this.bumpIf(",")){this.bumpSpace();const t=this.clonePosition(),i=this.parseSimpleArgStyleIfPossible();if(i.err)return i;const s=ca(i.val);if(0===s.length)return this.error(6,aa(this.clonePosition(),this.clonePosition()));e={style:s,styleLocation:aa(t,this.clonePosition())}}const t=this.tryParseArgumentClose(s);if(t.err)return t;const a=aa(s,this.clonePosition());if(e&&e.style.startsWith("::")){let t=da(e.style.slice(2));if("number"===n){const s=this.parseNumberSkeletonFromString(t,e.styleLocation);return s.err?s:{val:{type:2,value:i,location:a,style:s.val},err:null}}{if(0===t.length)return this.error(10,a);let s=t;this.locale&&(s=function(e,t){let i="";for(let s=0;s<e.length;s++){const a=e.charAt(s);if("j"===a){let n=0;for(;s+1<e.length&&e.charAt(s+1)===a;)n++,s++;let o=1+(1&n),r=n<2?1:3+(n>>1),l="a",d=ta(t);for("H"!=d&&"k"!=d||(r=0);r-- >0;)i+=l;for(;o-- >0;)i=d+i}else i+="J"===a?"H":a}return i}(t,this.locale));return{val:{type:"date"===n?3:4,value:i,location:a,style:{type:1,pattern:s,location:e.styleLocation,parsedOptions:this.shouldParseSkeletons?Cs(s):{}}},err:null}}}return{val:{type:"number"===n?2:"date"===n?3:4,value:i,location:a,style:e?.style??null},err:null}}case"plural":case"selectordinal":case"select":{const a=this.clonePosition();if(this.bumpSpace(),!this.bumpIf(","))return this.error(12,aa(a,{...a}));this.bumpSpace();let o=this.parseIdentifierIfPossible(),r=0;if("select"!==n&&"offset"===o.value){if(!this.bumpIf(":"))return this.error(13,aa(this.clonePosition(),this.clonePosition()));this.bumpSpace();const e=this.tryParseDecimalInteger(13,14);if(e.err)return e;this.bumpSpace(),o=this.parseIdentifierIfPossible(),r=e.val}const l=this.tryParsePluralOrSelectOptions(e,n,t,o);if(l.err)return l;const d=this.tryParseArgumentClose(s);if(d.err)return d;const c=aa(s,this.clonePosition());return"select"===n?{val:{type:5,value:i,options:la(l.val),location:c},err:null}:{val:{type:6,value:i,options:la(l.val),offset:r,pluralType:"plural"===n?"cardinal":"ordinal",location:c},err:null}}default:return this.error(5,aa(a,o))}}tryParseArgumentClose(e){return this.isEOF()||125!==this.char()?this.error(1,aa(e,this.clonePosition())):(this.bump(),{val:!0,err:null})}parseSimpleArgStyleIfPossible(){let e=0;const t=this.clonePosition();for(;!this.isEOF();)switch(this.char()){case 39:{this.bump();let e=this.clonePosition();if(!this.bumpUntil("'"))return this.error(11,aa(e,this.clonePosition()));this.bump();break}case 123:e+=1,this.bump();break;case 125:if(!(e>0))return{val:this.message.slice(t.offset,this.offset()),err:null};e-=1;break;default:this.bump()}return{val:this.message.slice(t.offset,this.offset()),err:null}}parseNumberSkeletonFromString(e,t){let i=[];try{i=function(e){if(0===e.length)throw new Error("Number skeleton cannot be empty");const t=e.split(Ts).filter(e=>e.length>0),i=[];for(const e of t){let t=e.split("/");if(0===t.length)throw new Error("Invalid number skeleton");const[s,...a]=t;for(const e of a)if(0===e.length)throw new Error("Invalid number skeleton");i.push({stem:s,options:a})}return i}(e)}catch{return this.error(7,t)}return{val:{type:0,tokens:i,location:t,parsedOptions:this.shouldParseSkeletons?Bs(i):{}},err:null}}tryParsePluralOrSelectOptions(e,t,i,s){let a=!1;const n=[],o=new Set;let{value:r,location:l}=s;for(;;){if(0===r.length){const e=this.clonePosition();if("select"===t||!this.bumpIf("="))break;{const t=this.tryParseDecimalInteger(16,19);if(t.err)return t;l=aa(e,this.clonePosition()),r=this.message.slice(e.offset,this.offset())}}if(o.has(r))return this.error("select"===t?21:20,l);"other"===r&&(a=!0),this.bumpSpace();const s=this.clonePosition();if(!this.bumpIf("{"))return this.error("select"===t?17:18,aa(this.clonePosition(),this.clonePosition()));const d=this.parseMessage(e+1,t,i);if(d.err)return d;const c=this.tryParseArgumentClose(s);if(c.err)return c;n.push([r,{value:d.val,location:aa(s,this.clonePosition())}]),o.add(r),this.bumpSpace(),({value:r,location:l}=this.parseIdentifierIfPossible())}return 0===n.length?this.error("select"===t?15:16,aa(this.clonePosition(),this.clonePosition())):this.requiresOtherClause&&!a?this.error(22,aa(this.clonePosition(),this.clonePosition())):{val:n,err:null}}tryParseDecimalInteger(e,t){let i=1;const s=this.clonePosition();this.bumpIf("+")||this.bumpIf("-")&&(i=-1);let a=!1,n=0;for(;!this.isEOF();){const e=this.char();if(!(e>=48&&e<=57))break;a=!0,n=10*n+(e-48),this.bump()}const o=aa(s,this.clonePosition());return a?(n*=i,Number.isSafeInteger(n)?{val:n,err:null}:this.error(t,o)):this.error(e,o)}offset(){return this.position.offset}isEOF(){return this.offset()===this.message.length}clonePosition(){return{offset:this.position.offset,line:this.position.line,column:this.position.column}}char(){const e=this.position.offset;if(e>=this.message.length)throw Error("out of bound");const t=this.message.codePointAt(e);if(void 0===t)throw Error(`Offset ${e} is at invalid UTF-16 code unit boundary`);return t}error(e,t){return{val:null,err:{kind:e,message:this.message,location:t}}}bump(){if(this.isEOF())return;const e=this.char();10===e?(this.position.line+=1,this.position.column=1,this.position.offset+=1):(this.position.column+=1,this.position.offset+=e<65536?1:2)}bumpIf(e){if(this.message.startsWith(e,this.offset())){for(let t=0;t<e.length;t++)this.bump();return!0}return!1}bumpUntil(e){const t=this.offset(),i=this.message.indexOf(e,t);return i>=0?(this.bumpTo(i),!0):(this.bumpTo(this.message.length),!1)}bumpTo(e){if(this.offset()>e)throw Error(`targetOffset ${e} must be greater than or equal to the current offset ${this.offset()}`);for(e=Math.min(e,this.message.length);;){const t=this.offset();if(t===e)break;if(t>e)throw Error(`targetOffset ${e} is at invalid UTF-16 code unit boundary`);if(this.bump(),this.isEOF())break}}bumpSpace(){for(;!this.isEOF()&&ma(this.char());)this.bump()}peek(){if(this.isEOF())return null;const e=this.char(),t=this.offset();return this.message.charCodeAt(t+(e>=65536?2:1))??null}};function pa(e){return e>=97&&e<=122||e>=65&&e<=90}function ga(e){return 45===e||46===e||e>=48&&e<=57||95===e||e>=97&&e<=122||e>=65&&e<=90||183==e||e>=192&&e<=214||e>=216&&e<=246||e>=248&&e<=893||e>=895&&e<=8191||e>=8204&&e<=8205||e>=8255&&e<=8256||e>=8304&&e<=8591||e>=11264&&e<=12271||e>=12289&&e<=55295||e>=63744&&e<=64975||e>=65008&&e<=65533||e>=65536&&e<=983039}function ma(e){return e>=9&&e<=13||32===e||133===e||e>=8206&&e<=8207||8232===e||8233===e}function va(e){e.forEach(e=>{if(delete e.location,Gs(e)||Ks(e))for(const t in e.options)delete e.options[t].location,va(e.options[t].value);else Zs(e)&&Xs(e.style)||(Ws(e)||qs(e))&&Js(e.style)?delete e.style.location:Ys(e)&&va(e.children)})}function fa(e,t={}){t={shouldParseSkeletons:!0,requiresOtherClause:!0,...t};const i=new ua(e,t).parse();if(i.err){const e=SyntaxError(Us[i.err.kind]);throw e.location=i.err.location,e.originalMessage=i.err.message,e}return t?.captureLocation||va(i.val),i.val}var _a=class extends Error{constructor(e,t,i){super(e),this.code=t,this.originalMessage=i}toString(){return`[formatjs Error: ${this.code}] ${this.message}`}},ba=class extends _a{constructor(e,t,i,s){super(`Invalid values for "${e}": "${t}". Options are "${Object.keys(i).join('", "')}"`,"INVALID_VALUE",s)}},ya=class extends _a{constructor(e,t,i){super(`Value for "${e}" must be of type ${t}`,"INVALID_VALUE",i)}},wa=class extends _a{constructor(e,t){super(`The intl string context variable "${e}" was not provided to the string "${t}"`,"MISSING_VALUE",t)}};function $a(e){return"function"==typeof e}function xa(e,t,i,s,a,n,o){if(1===e.length&&js(e[0]))return[{type:0,value:e[0].value}];const r=[];for(const l of e){if(js(l)){r.push({type:0,value:l.value});continue}if(Vs(l)){"number"==typeof n&&r.push({type:0,value:i.getNumberFormat(t).format(n)});continue}const{value:e}=l;if(!a||!(e in a))throw new wa(e,o);let d=a[e];if(Fs(l))d&&"string"!=typeof d&&"number"!=typeof d&&"bigint"!=typeof d||(d="string"==typeof d||"number"==typeof d||"bigint"==typeof d?String(d):""),r.push({type:"string"==typeof d?0:1,value:d});else{if(Ws(l)){const e="string"==typeof l.style?s.date[l.style]:Js(l.style)?l.style.parsedOptions:void 0;r.push({type:0,value:i.getDateTimeFormat(t,e).format(d)});continue}if(qs(l)){const e="string"==typeof l.style?s.time[l.style]:Js(l.style)?l.style.parsedOptions:s.time.medium;r.push({type:0,value:i.getDateTimeFormat(t,e).format(d)});continue}if(Zs(l)){const e="string"==typeof l.style?s.number[l.style]:Xs(l.style)?l.style.parsedOptions:void 0;if(e&&e.scale){const t=e.scale||1;if("bigint"==typeof d){if(!Number.isInteger(t))throw new TypeError(`Cannot apply fractional scale ${t} to bigint value. Scale must be an integer when formatting bigint.`);d*=BigInt(t)}else d*=t}r.push({type:0,value:i.getNumberFormat(t,e).format(d)});continue}if(Ys(l)){const{children:e,value:d}=l,c=a[d];if(!$a(c))throw new ya(d,"function",o);let h=c(xa(e,t,i,s,a,n).map(e=>e.value));Array.isArray(h)||(h=[h]),r.push(...h.map(e=>({type:"string"==typeof e?0:1,value:e})))}if(Gs(l)){const e=d,n=(Object.prototype.hasOwnProperty.call(l.options,e)?l.options[e]:void 0)||l.options.other;if(!n)throw new ba(l.value,d,Object.keys(l.options),o);r.push(...xa(n.value,t,i,s,a));continue}if(Ks(l)){const e=`=${d}`;let n=Object.prototype.hasOwnProperty.call(l.options,e)?l.options[e]:void 0;if(!n){if(!Intl.PluralRules)throw new _a('Intl.PluralRules is not available in this environment.\nTry polyfilling it using "@formatjs/intl-pluralrules"\n',"MISSING_INTL_API",o);const e="bigint"==typeof d?Number(d):d,s=i.getPluralRules(t,{type:l.pluralType}).select(e-(l.offset||0));n=(Object.prototype.hasOwnProperty.call(l.options,s)?l.options[s]:void 0)||l.options.other}if(!n)throw new ba(l.value,d,Object.keys(l.options),o);const c="bigint"==typeof d?Number(d):d;r.push(...xa(n.value,t,i,s,a,c-(l.offset||0)));continue}}}return(l=r).length<2?l:l.reduce((e,t)=>{const i=e[e.length-1];return i&&0===i.type&&0===t.type?i.value+=t.value:e.push(t),e},[]);var l}function ka(e,t){return t?Object.keys(e).reduce((i,s)=>{var a,n;return i[s]=(a=e[s],(n=t[s])?{...a,...n,...Object.keys(a).reduce((e,t)=>(e[t]={...a[t],...n[t]},e),{})}:a),i},{...e}):e}function za(e){return{create:()=>({get:t=>e[t],set(t,i){e[t]=i}})}}var Sa=class e{constructor(t,i=e.defaultLocale,s,a){if(this.formatterCache={number:{},dateTime:{},pluralRules:{}},this.format=e=>{const t=this.formatToParts(e);if(1===t.length)return t[0].value;const i=t.reduce((e,t)=>(e.length&&0===t.type&&"string"==typeof e[e.length-1]?e[e.length-1]+=t.value:e.push(t.value),e),[]);return i.length<=1?i[0]||"":i},this.formatToParts=e=>xa(this.ast,this.locales,this.formatters,this.formats,e,void 0,this.message),this.resolvedOptions=()=>({locale:this.resolvedLocale?.toString()||Intl.NumberFormat.supportedLocalesOf(this.locales)[0]}),this.getAst=()=>this.ast,this.locales=i,this.resolvedLocale=e.resolveLocale(i),"string"==typeof t){if(this.message=t,!e.__parse)throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");const{...i}=a||{};this.ast=e.__parse(t,{...i,locale:this.resolvedLocale})}else this.ast=t;if(!Array.isArray(this.ast))throw new TypeError("A message must be provided as a String or AST.");this.formats=ka(e.formats,s),this.formatters=a&&a.formatters||function(e={number:{},dateTime:{},pluralRules:{}}){return{getNumberFormat:bs((...e)=>new Intl.NumberFormat(...e),{cache:za(e.number),strategy:As.variadic}),getDateTimeFormat:bs((...e)=>new Intl.DateTimeFormat(...e),{cache:za(e.dateTime),strategy:As.variadic}),getPluralRules:bs((...e)=>new Intl.PluralRules(...e),{cache:za(e.pluralRules),strategy:As.variadic})}}(this.formatterCache)}static{this.memoizedDefaultLocale=null}static get defaultLocale(){return e.memoizedDefaultLocale||(e.memoizedDefaultLocale=(new Intl.NumberFormat).resolvedOptions().locale),e.memoizedDefaultLocale}static{this.resolveLocale=e=>{if(void 0===Intl.Locale)return;const t=Intl.NumberFormat.supportedLocalesOf(e);return t.length>0?new Intl.Locale(t[0]):new Intl.Locale("string"==typeof e?e:e[0])}}static{this.__parse=fa}static{this.formats={number:{integer:{maximumFractionDigits:0},currency:{style:"currency"},percent:{style:"percent"}},date:{short:{month:"numeric",day:"numeric",year:"2-digit"},medium:{month:"short",day:"numeric",year:"numeric"},long:{month:"long",day:"numeric",year:"numeric"},full:{weekday:"long",month:"long",day:"numeric",year:"numeric"}},time:{short:{hour:"numeric",minute:"numeric"},medium:{hour:"numeric",minute:"numeric",second:"numeric"},long:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"},full:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"}}}}};const Aa={en:_s},Ea={};function Ca(e){return e.replace(/['"]+/g,"").split(/[-_]/)[0].toLowerCase()}function Ta(e){const t=Ca(e);return t in Aa||!ye.includes(t)}function Oa(e,t,...i){const s=Ca(t);let a;try{a=e.split(".").reduce((e,t)=>e[t],Aa[s])}catch(t){a=e.split(".").reduce((e,t)=>e[t],Aa.en)}if(void 0===a&&(a=e.split(".").reduce((e,t)=>e[t],Aa.en)),!i.length)return a;const n={};for(let e=0;e<i.length;e+=2){let t=i[e];t=t.replace(/^{([^}]+)?}$/,"$1"),n[t]=i[e+1]}try{return new Sa(a,t).format(n)}catch(e){return"Translation "+e}}function Ha(e,t,i){e.dispatchEvent(new CustomEvent(t,{detail:i,bubbles:!0,composed:!0,cancelable:!1}))}function Da(e,t){return(e=e.toString()).split(",")[t]}function Ma(e,t){switch(t){case zt:return e.units==De?W`${es(ht)}`:W`${es(ut)}`;case xe:case bt:return e.units==De?W`${es(ot)}`:W`${es(rt)}`;case gt:return e.units==De?W`${es("m<sup>2</sup>")}`:W`${es(it)}`;case mt:return e.units==De?W`${es(st)}`:W`${es(at)}`;default:return W``}}function Ia(e,t){!function(e,t){Ha(e,"show-dialog",{dialogTag:"error-dialog",dialogImport:()=>Promise.resolve().then(function(){return io}),dialogParams:{error:t}})}(t,W`
    ${e.error}:${e.body.message?W` ${e.body.message} `:""}
  `)}const Na=(e,t,i=!1)=>{i?history.replaceState(null,"",t):history.pushState(null,"",t),Ha(window,"location-changed",{replace:i})};function Pa(e){var t;if(!e)return"Unknown error";if("string"==typeof e)return e;const i=e;return(null===(t=null==i?void 0:i.body)||void 0===t?void 0:t.message)||(null==i?void 0:i.message)||(null==i?void 0:i.error)||JSON.stringify(e)}function La(e){const t=Math.round(e);if(t<60)return`${t} s`;const i=Math.floor(t/60),s=t%60;return s?`${i} min ${s} s`:`${i} min`}function Ra(e,t){e.dispatchEvent(new CustomEvent("hass-notification",{detail:{message:t},bubbles:!0,composed:!0}))}function Ba(e,t,i,s){var a;Ra(e,`${Oa(i,null!==(a=null==t?void 0:t.language)&&void 0!==a?a:"en")}: ${Pa(s)}`)}var Ua="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",ja="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z";const Fa=e=>{class i extends e{connectedCallback(){super.connectedCallback(),this.__checkSubscribed()}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const e=this.__unsubs.pop();e instanceof Promise?e.then(e=>e()):e()}this.__unsubs=void 0}}updated(e){super.updated(e),e.has("hass")&&this.__checkSubscribed()}hassSubscribe(){return[]}__checkSubscribed(){void 0===this.__unsubs&&this.isConnected&&void 0!==this.hass&&(this.__unsubs=this.hassSubscribe())}}return t([me({attribute:!1})],i.prototype,"hass",void 0),i};var Za,Wa;!function(e){e.Sunrise="sunrise",e.Sunset="sunset",e.SolarAzimuth="solar_azimuth"}(Za||(Za={})),function(e){e.Disabled="disabled",e.Manual="manual",e.Automatic="automatic"}(Wa||(Wa={}));const qa=()=>{const e=e=>{let t={};for(let i=0;i<e.length;i+=2){const s=e[i],a=i<e.length?e[i+1]:void 0;t=Object.assign(Object.assign({},t),{[s]:a})}return t},t=window.location.pathname.split("/");let i={page:t[2]||"general",params:{}};if(t.length>3){let s=t.slice(3);if(t.includes("filter")){const t=s.findIndex(e=>"filter"==e),a=s.slice(t+1);s=s.slice(0,t),i=Object.assign(Object.assign({},i),{filter:e(a)})}s.length&&(s.length%2&&(i=Object.assign(Object.assign({},i),{subpage:s.shift()})),s.length&&(i=Object.assign(Object.assign({},i),{params:e(s)})))}return i},Ga=(e,...t)=>{let i={page:e,params:{}};t.forEach(e=>{"string"==typeof e?i=Object.assign(Object.assign({},i),{subpage:e}):"params"in e?i=Object.assign(Object.assign({},i),{params:e.params}):"filter"in e&&(i=Object.assign(Object.assign({},i),{filter:e.filter}))});const s=e=>{let t=Object.keys(e);t=t.filter(t=>e[t]),t.sort();let i="";return t.forEach(t=>{const s=e[t];i=i.length?`${i}/${t}/${s}`:`${t}/${s}`}),i};let a=`/${be}/${i.page}`;return i.subpage&&(a=`${a}/${i.subpage}`),s(i.params).length&&(a=`${a}/${s(i.params)}`),i.filter&&(a=`${a}/filter/${s(i.filter)}`),a},Ka=r`
=======
     */class ti extends ei{constructor(e){if(super(e),this.it=K,e.type!==Ys)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(e){if(e===K||null==e)return this._t=void 0,this.it=e;if(e===G)return e;if("string"!=typeof e)throw Error(this.constructor.directiveName+"() called with a non-string value");if(e===this.it)return this._t;this.it=e;const t=[e];return t.raw=t,this._t={_$litType$:this.constructor.resultType,strings:t,values:[]}}}ti.directiveName="unsafeHTML",ti.resultType=1;const si=Qs(ti);var ii={title:"Smart Irrigation: check flow rate",message_over:"Zone '{zone}' is consistently over-watering: the measured flow is ~{percent}% above the configured rate over {runs} runs. Its valve can't stop early, so consider setting the throughput to about {rate} {unit} (currently {current}).",message_under:"Zone '{zone}' is consistently under-watering: the measured flow is ~{percent}% below the configured rate over {runs} runs. Its valve can't stop early, so consider setting the throughput to about {rate} {unit} (currently {current}).",open_settings:"Open zone settings"},ai={loading:"Loading",saving:"Saving",actions:{delete:"Delete",edit:"Edit",save:"Save",cancel:"Cancel",confirm_delete:"Confirm Delete",confirm_delete_zone:"Are you sure you want to delete this zone?"},labels:{module:"Module",no:"No",select:"Select",yes:"Yes",enabled:"Enabled",disabled:"Disabled",before:"before",after:"after",settings:"Settings",bulk_actions:"Bulk Actions"},units:{seconds:"seconds"},attributes:{size:"size",throughput:"throughput",state:"state",bucket:"bucket",last_updated:"last updated",last_calculated:"last calculated",number_of_data_points:"number of data points"},"loading-messages":{configuration:"Loading configuration...",modules:"Loading modules...",general:"Loading..."},"saving-messages":{adding:"Adding...",saving:"Saving..."},errors:{load_failed:"Couldn't load data",save_failed:"Couldn't save changes",delete_failed:"Couldn't delete",action_failed:"Action failed"}},ni={"default-zone":"Default zone","default-mapping":"Default sensor group"},oi={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"Note: this explanation uses '.' as decimal separator, shows rounded and metric values. Module returned Evapotranspiration deficiency ( = et0 * hour_multiplier + precipitation) of","module-returned-evapotranspiration-deficiency-hourly":"Note: this explanation uses '.' as decimal separator, shows rounded and metric values. Evapotranspiration deficiency ( = sum of hourly FAO-56 et0 over the window + precipitation) of","bucket-was":"Bucket was","new-bucket-values-is":"New bucket value is",bucket:"bucket","old-bucket-variable":"old_bucket","max-bucket-variable":"max_bucket",delta:"delta","bucket-less-than-zero-irrigation-necessary":"Since bucket < 0, irrigation is necessary","steps-taken-to-calculate-duration":"To calculate the exact duration, the following steps were taken","precipitation-rate-defined-as":"The precipitation rate is defined as","duration-is-calculated-as":"The duration is calculated as",drainage:"drainage","drainage-rate":"drainage_rate",hours:"hours","precipitation-rate-variable":"precipitation_rate","multiplier-is-applied":"Now, the multiplier is applied. The multiplier is","duration-after-multiplier-is":"hence the duration is","maximum-duration-is-applied":"Then, the maximum duration is applied. The maximum duration is","duration-after-maximum-duration-is":"hence the duration is","lead-time-is-applied":"Finally, the lead time is applied. The lead time is","duration-after-lead-time-is":"hence the final duration is","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Since bucket >= 0, no irrigation is necessary and duration is set to","maximum-bucket-is":"Maximum bucket size is","drainage-rate-is":"Drainage rate when saturated (bucket at max) is","current-drainage-is":"Current drainage is calculated as","drainage-integrated":"the surplus above field capacity drains continuously over the window (Brooks–Corey), so the rate falls as it drains","no-drainage":"Current drainage is 0 because","water-balance-substepped":"The water balance was replayed across the window, so rain, drainage and the maximum bucket clamp were applied at the times they occurred rather than all at the start of the window. Number of steps:","runoff-is":"Water above the maximum bucket that was lost to runoff:","runoff-variable":"runoff","forecast-weighting-applied":"Forecast weighting reduced the deficit for the expected rain","crop-coefficient-applied":"Scaled by the crop coefficient"}}},ri={pyeto:{description:"Calculate duration based on the FAO56 calculation from the PyETO library"},static:{description:"'Dummy' module with a static configurable delta"},passthrough:{description:"Passthrough module that returns the value of an Evapotranspiration sensor as delta"}},li={general:{cards:{"automatic-duration-calculation":{header:"Automatic duration calculation",description:"Calculation takes collected weather data up to that point and updates the bucket for each automatic zone. Then, the duration is adjusted based on the new bucket value and the collected weather data is removed.",labels:{"auto-calc-enabled":"Automatically calculate irrigation durations","calc-time":"Calculate at","calc-mode":"Calculate"},modes:{fixed_time:"At a fixed time",before_run:"Before each irrigation run"},help:{"before-run":"Durations are calculated when each irrigation schedule plans its run, so a run is sized from weather data minutes old instead of hours old."}},"run-history-logging":{header:"Run history logging",description:"When on, a scheduled run that skips a zone because it currently has no water demand is recorded in that zone's history. Off by default; existing history is unaffected.",labels:{"log-no-demand":'Log "no demand" skips in the run history'}},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Warning: weather data update time on or after calculation time"},header:"Automatic weather data update",description:"Collect and store weather data automatically. Weather data is required to calculate zone buckets and durations.",labels:{"auto-update-enabled":"Automatically update weather data","auto-update-schedule":"Update schedule","auto-update-time":"Update at","auto-update-interval":"Update sensor data every","auto-update-delay":"Update delay"},options:{minutes:"minutes",hours:"hours",days:"days"}},"automatic-clear":{header:"Automatic weather data pruning",description:"Automatically remove collected weather data at a configured time. Use this to make sure that there is no left over weather data from previous days. Don't remove the weather data before you calculate and only use this option if you expect the automatic update to collect weather data after you calculated for the day. Ideally, you want to prune as late in the day as possible.",labels:{"automatic-clear-enabled":"Automatically clear collected weather data","automatic-clear-time":"Clear weather data at"}},continuousupdates:{header:"Continuous updates for sensors (experimental)",description:"This experimental feature will continuously update the sensor data. This is useful for sensor groups that use sources that provide continuous data, such as weather stations. This feature cannot be used for sensor groups that at least partly rely on weather services as continous polling of APIs will incur costs. Keep in mind that this is experimental and may not work as expected. Use at your own risk.",labels:{continuousupdates:"Enable continuous updates",sensor_debounce:"Sensor debounce"}}},description:"This page provides global settings.",title:"General",sections:{weather:"Weather",automation:"Automation",location:"Location",watering:"Watering behavior"}},schedules:{title:"Schedules",description:"Create recurring schedules to automatically irrigate your zones at specific times. No automations needed.",add:"Add Schedule",no_items:"No schedules configured yet. Click 'Add Schedule' to get started.",zones_all:"All zones",zones_specific:"Specific zones",hours:"hours",minutes:"min",types:{daily:"Daily",weekly:"Weekly",monthly:"Monthly",interval:"Every N hours"},actions:{calculate:"Calculate (update irrigation duration)",update:"Update (collect weather data)",irrigate:"Irrigate (run valves directly)"},days:{monday:"Mon",tuesday:"Tue",wednesday:"Wed",thursday:"Thu",friday:"Fri",saturday:"Sat",sunday:"Sun"},fields:{name:"Name",recurrence:"Recurrence",enabled:"Enabled",days_of_week:"Days of week",day_of_month:"Day of month",interval_hours:"Interval",action:"Action",zones:"Zones",start_mode:"Start",start_time:"Start time (optional)",finish_mode:"Finish",finish_time:"Finish time (HH:MM)",anchor:"Pinned to",offset_by:"offset by"},dialog:{add_title:"Add Schedule",edit_title:"Edit Schedule"},sections:{when:"When",zones:"Zones",season:"Season"},season:{label:"Date range",to:"to",note:"Leave both blank to run all year."},summary:{invalid:"This schedule has no start or finish set, so it never runs.",recurrence_daily:"Runs daily",recurrence_weekly:"Runs weekly on {days}",recurrence_monthly:"Runs monthly on day {day}",recurrence_interval:"Runs every {hours} hours",recurrence_interval_at:"Runs every {hours} hours, starting at {time}",zones_all:"all zones",zones_some:"{count, plural, one {# selected zone} other {# selected zones}}",watering:"watering {zones}",start_only:"starting at {when}; every zone runs to completion",finish_only:"finishing at {when}; every zone runs to completion",anchor_finish:"finishing at {finish}, starting as late as possible but never before {start}; zones that don't fit wait for the next run",anchor_start:"starting at {start}, finishing by {finish} at the latest; zones that don't fit wait for the next run",sunrise:"sunrise",sunset:"sunset",offset_before:"{minutes} min before {event}",offset_after:"{minutes} min after {event}",at_azimuth:"solar azimuth {degrees}°"},bound_mode:{none:"No limit",time:"At a time",sunrise:"At sunrise",sunset:"At sunset",solar_azimuth:"At solar azimuth"},anchor:{start:"As early as possible within the window",finish:"As late as possible within the window"},help:{error:"Must set either a start or finish condition",demand_open:"Set by demand. All zones run to completion.",exact:"Exact.",demand_floored:"Set by demand, but never before this.",exact_deferred:"Exact. Zones that don't fit are deferred.",demand_capped_deferred:"Set by demand, but never later than this. Zones that don't fit are deferred."},dial:{aria_label:"Run window on a 24 hour dial",sunrise:"Sunrise {time}",sunset:"Sunset {time}",run:"Run {from} to {to}",collision:"Collides with the previous run, {from} to {to}: zones still watering are skipped",window_label:"window",run_label:"run",per_day:"{count}x per day",every_hours:"every {hours}h"}},setup:{title:"Setup",tabs:{weather_location:"Weather & Location",my_zones:"My Zones",when_to_water:"When to Water",advanced:"Advanced",experimental:"Experimental",distributors:"Distributors"},weather_data:{forecast_title:"Forecast",forecast_none:"Forecast is available when a weather service is enabled.",seasonal_title:"Seasonal outlook"},advanced:{used_by_zones:"Used by {count, plural, one {# zone} other {# zones}}",not_used:"Not used"}},experimental:{title:"Experimental features",warning:"These features are opt-in and still being refined. They change how each zone's bucket is filled, so turn them on one at a time and keep an eye on your zones — you can switch them back off at any time.",forecast_weighting:{title:"Forecast-weighted durations",description:"Instead of skipping a whole run when rain is forecast, water less. The upcoming precipitation (over the look-ahead window set under When to Water) is subtracted from the deficit used to compute the run duration, while the true deficit stays in the bucket so the real rain fills the rest. If the forecast rain misses, the next run makes up the difference. Requires a weather service.",label:"Reduce durations when rain is forecast",note:"Uses the precipitation look-ahead from When to Water. Works alongside the rain-skip guard (a skip still wins over a reduced run)."},observed_watering:{title:"Credit bucket from observed watering",description:"When a zone's linked valve runs outside Smart Irrigation — a manual tap, an automation, your own schedule — its bucket is credited for the water applied, estimated from the run time and the zone's throughput. This keeps the soil-moisture model honest when you water by other means. Smart Irrigation's own runs are already accounted for and are never double-counted.",label:"Credit the bucket when a linked valve runs externally",note:"Requires a linked valve and a throughput on the zone. Volume is estimated (run time × throughput), not metered."},live_estimate:{title:"Live-estimate watering",description:"By default a zone waters once a day, from the deficit the daily calculation produced (for example at 23:00). With this on, each scheduled run instead decides — and sizes itself — from the live intra-day deficit (the drainage-aware ET and rainfall since the last calculation). This lets a zone water more than once a day on real intra-day demand (for example pots on an every-12-hours schedule that the once-daily bucket would otherwise leave dry), and it shrinks or cancels a run that intra-day rain has already covered. The daily ledger is unchanged: after the run the bucket is credited with the water actually delivered, so the next daily calculation never double-counts. Requires a weather service.",label:"Trigger and size each run from the live deficit",note:"Affects scheduled runs only, and can start a run the daily calculation didn't approve. For frequent watering keep a sensible minimum deficit and a maximum bucket of at least a day's ET."},continuous_updates:{title:"Continuous sensor updates",description:"By default, sensor-based weather values are read once per scheduled update (hourly by default), so anything that happened in between is never recorded — the daily minimum and maximum temperature come from those spot readings, and solar radiation is integrated coarsely. With this on, a reading is recorded the moment the sensor changes, which makes the daily aggregates and the resulting evapotranspiration considerably more accurate. Sensor groups that also use a weather service keep their scheduled update for the weather-service values; only the sensor values become continuous. Small changes are ignored, so a noisy sensor does not fill the buffer.",label:"Record sensor readings when they change",debounce_label:"Group changes arriving within (milliseconds)",note:"Applies to sensor groups whose values come from Home Assistant sensors. The grouping delay only postpones the follow-up bookkeeping — no reading is ever dropped by it. Set it to 0 to disable grouping."},hourly_calculation:{title:"Hourly evapotranspiration",description:"By default the FAO-56 equation is run once, over the window's average weather, which cloud cover biases systematically: fed one identical hourly series across 362 days it returns 1.14 times the reference on overcast days and 0.93 times on clear ones. With this on, the equation is run for each hour and the hours are summed, which removes that bias, and the water balance is replayed hour by hour so rain and drainage are booked when they happened instead of all at the start of the window. Expect the daily figure to move by up to 12 percent, in either direction depending on the sky. Needs a Solar Radiation source that is measured rather than estimated, and it is not used on days where a forecast is blended in.",label:"Sum evapotranspiration hour by hour",note:"Independent of continuous sensor updates: scheduled hourly updates carry this too, and a denser buffer makes it more accurate without being required. Any window that cannot be reduced to hourly rows keeps the daily equation, so no series is ever invented."},distributors:{title:"Mechanical water distributors",description:"Drive a mechanical pressure-distributor — for example a Gardena Water Distributor — that splits one supply into several outlets and advances on water on/off pulses. Assign zones to a distributor's outlets and Smart Irrigation waters them in sequence, tracks the position, and coordinates a master valve or pump. This is a new feature that could not be fully hardware-tested, so treat it as a beta.",label:"Enable mechanical water distributors",note:"Watch the first days of use closely and keep the device's manual override handy. You can switch it back off at any time — existing zone watering is unaffected."}},help:{title:"Help",cards:{"how-to-get-help":{title:"How to get help","first-read-the":"First, read the",wiki:"Documentation","if-you-still-need-help":"If you still need help reach out on the","community-forum":"Community forum","or-open-a":"or open a","github-issue":"Github Issue","english-only":"English only"}}},info:{title:"Info",description:"View information about next irrigation and system status.","configuration-not-available":"Configuration not available.",cards:{"zone-bucket-values":{title:"Zone Bucket Values & Duration",labels:{bucket:"Bucket",duration:"Duration"},"no-zones":"No zones configured"},"next-irrigation":{title:"Next Irrigation",labels:{"next-start":"Next start",duration:"Duration",zones:"Zones"},"no-data":"No data available"},"irrigation-reason":{title:"Irrigation Reason",labels:{reason:"Reason",sunrise:"Sunrise","total-duration":"Total duration",explanation:"Explanation"},"no-data":"No data available"},irrigate_now:{title:"Irrigate Now",description:"Immediately start irrigation for all zones that have a linked entity. Skip conditions are ignored.",button_all:"Run all zones now",no_linked_zones:"No zones have a linked switch/valve entity with a calculated duration."}}},mappings:{cards:{"add-mapping":{actions:{add:"Add sensor group"},header:"Add sensor groups"},mapping:{aggregates:{average:"Average",first:"First",last:"Last",maximum:"Maximum",median:"Median",minimum:"Minimum",riemannsum:"Riemann sum",sum:"Sum",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"You cannot delete this sensor group because there is at least one zone using it.",invalid_source:"Invalid source",source_does_not_exist:"Source does not exist. Please enter a valid source, such as 'sensor.mysensor'."},items:{dewpoint:"Dewpoint",evapotranspiration:"Evapotranspiration",humidity:"Humidity","maximum temperature":"Maximum temperature","minimum temperature":"Minimum temperature",precipitation:"Total precipitation","current precipitation":"Current precipitation",pressure:"Pressure","solar radiation":"Solar radiation",temperature:"Temperature",windspeed:"Wind speed"},pressure_types:{absolute:"absolute",relative:"relative"},"pressure-type":"Pressure is","sensor-aggregate-of-sensor-values-to-calculate":"of sensor values to calculate duration","sensor-aggregate-use-the":"Use the","sensor-entity":"Sensor entity",static_value:"Value","input-units":"Input provides values in",source:"Source",sources:{none:"None",weather_service:"Weather service",sensor:"Sensor",static:"Static value"}}},description:"Add one or more sensor groups that retrieve weather data from Weather service, from sensors or a combination of these. You can map each sensor group to one or more zones",labels:{"mapping-name":"Name"},no_items:"There are no sensor group defined yet.",title:"Sensor Groups","weather-records":{title:"Weather Records",timestamp:"Time",temperature:"Temp",humidity:"Hum",dewpoint:"Dew",wind:"Wind",pressure:"Press",precipitation:"Precip","retrieval-time":"Retrieved","no-data":"No weather data available for this sensor group"}},modules:{cards:{"add-module":{actions:{add:"Add module"},header:"Add module"},module:{errors:{"cannot-delete-module-because-zones-use-it":"You cannot delete this module because there is at least one zone using it."},labels:{configuration:"Configuration",required:"indicates a required field"},"translated-options":{DontEstimate:"Do not estimate",EstimateFromSunHours:"Estimate from sun hours",EstimateFromTemp:"Estimate from temperature",EstimateFromSunHoursAndTemperature:"Estimate from average of sun hours and temperature"},fields:{coastal:{name:"Coastal",description:"Enable if the weather station is located near a coast or large body of water. Affects how atmospheric humidity is estimated."},solrad_behavior:{name:"Solar radiation estimation",description:"How solar radiation is estimated when it is not directly measured by a sensor."},forecast_days:{name:"Forecast days",description:"Number of future days to include in the ET calculation. 0 = current weather only (recommended — no extra API calls). Values > 0 average today's ET with forecasted ET for upcoming days (up to 4 days via the OWM free tier)."},delta:{name:"Delta",description:"Static evapotranspiration delta (mm) used directly without any weather-based calculation."}}}},description:"Add one or more modules that calculate irrigation duration. Each module comes with its own configuration and can be used to calculate duration for one or more zones.",no_items:"There are no modules defined yet.",title:"Modules"},zones:{actions:{add:"Add",calculate:"Calculate",information:"Information",update:"Update","reset-bucket":"Reset bucket","view-weather-info":"View weather data","view-weather-info-message":"Weather data available for","view-watering-calendar":"View watering calendar",irrigate_all:"Water all zones now",open_settings:"Edit settings"},cards:{"add-zone":{actions:{add:"Add zone"},header:"Add zone"},"zone-actions":{actions:{"calculate-all":"Recalculate durations","update-all":"Refresh weather data","reset-all-buckets":"Reset all buckets","clear-all-weatherdata":"Clear all weather data"},header:"Actions on all zones"}},description:"Specify one or more irrigation zones here. The irrigation duration is calculated per zone, depending on size, throughput, state, module and sensor group.",labels:{bucket:"Bucket",duration:"Duration","lead-time":"Lead time",mapping:"Sensor Group","maximum-duration":"Maximum duration",multiplier:"Multiplier",name:"Name",size:"Size",state:"State",states:{automatic:"Automatic",disabled:"Disabled",manual:"Manual"},throughput:"Throughput","maximum-bucket":"Maximum bucket",last_calculated:"Last calculated","data-last-updated":"Data last updated","data-number-of-data-points":"Number of data points",drainage_rate:"Drainage rate",linked_entity:"Linked switch/valve/helper entity",opensprinkler_station:"OpenSprinkler station",opensprinkler_station_help:"The station's enabled switch, e.g. switch.front_lawn_station_enabled. HASI queues the run on the controller and then watches that station's own running sensor, so a zone queued behind others is only counted as watering once it really starts. Set the controller's water level to 100% or turn its weather adjustment off, otherwise the weather correction is applied twice.",opensprinkler_no_stations:"No OpenSprinkler stations found. Check that the OpenSprinkler integration is set up and the controller is reachable. You can still type an entity id.",linked_entity_placeholder:"e.g. switch.garden_valve",flow_sensor:"Flow meter sensor (optional)",flow_sensor_placeholder:"e.g. sensor.zone_flow_rate",flow_counter_type:"Counter type",flow_counter_type_help:"How this cumulative flow sensor is read. Auto learns across runs whether the sensor resets each run. Per run: the sensor resets to ~0 each run and shows that run's total (e.g. Sonoff/Zigbee valves). Lifetime: a meter that only ever counts up across all runs (delta per run).",flow_counter_type_auto:"Auto (learn)",flow_counter_type_per_run:"Per run (resets each run)",flow_counter_type_lifetime:"Lifetime total (delta)",watering_mode:"Watering mode",watering_mode_description:"How HASI actuates this zone. Classic: HASI opens the valve and closes it itself with a software timer. Self-closing service: HASI sends the run duration to a self-closing valve via a script (see the shipped valve blueprints) and lets the hardware close itself, so an HA restart mid-run cannot cause continuous irrigation.",watering_modes:{classic:"Classic (HASI opens & closes the valve)",service:"Self-closing service (valve closes itself)",opensprinkler:"OpenSprinkler station (controller runs the queue)"},run_service:"Run service",run_service_help:"Service HASI calls to start the run (e.g. a script.* or a switch/valve service). It receives the duration field below plus zone_id and zone_name.",duration_field:"Duration field",duration_field_placeholder:"e.g. dauer",duration_field_help:"Name of the parameter that carries the run length in the call to your run service. The shipped valve blueprints use 'duration' (the default); a custom script may use another name (e.g. 'dauer').",duration_unit:"Duration unit",duration_units:{seconds:"Seconds",minutes:"Minutes"},duration_unit_help:"Unit your hardware expects for the run length. Check the device: many Zigbee/Tuya valves count in MINUTES. The wrong unit over- or under-waters by 60x. In Minutes mode HASI rounds up to whole minutes (minimum 1).",stop_service:"Stop service (optional)",stop_service_help:"Optional. Service HASI calls to close the valve when you stop the zone early, before its own timer expires. Leave empty if the valve cannot be stopped manually.",confirm_entity:"Confirm entity (optional)",confirm_entity_help:"Optional. The real valve/switch entity the run service drives (e.g. a valve or switch) — it holds a steady on-state while watering. If set, HASI verifies the open against it (poll only, it never re-actuates) and flags a problem plus skips the bucket credit if it never turns on. Leave empty to treat the run as write-only and credit optimistically (the hardware owns the close). When in doubt, leave it empty: it only helps with an entity that reports its on-state reliably — a valve that reports late (e.g. a sleepy Zigbee valve) could be read as 'off' and wrongly skip the credit, so the zone would water again next run. Do NOT point this at the run script itself — a fire-and-forget script is not a valid state signal.",observed_entity:"Observed valve/switch (optional)",observed_entity_help:"If Observed watering is on, external runs of this valve/switch (a manual tap, an automation) credit this zone's water storage. Leave empty to not observe this zone.",soil_moisture_sensor:"Soil-moisture sensor (optional)",soil_moisture_sensor_help:"Optional. A sensor reporting this zone's soil moisture in percent (higher = wetter). With a skip threshold set below, an automatic run skips this zone whenever the reading is above the threshold and resets the zone's bucket. Leave empty to disable. An unavailable or non-numeric reading never blocks watering (fail-open).",soil_moisture_threshold:"Skip above soil moisture (%)",soil_moisture_threshold_help:"On an automatic run, skip this zone (and reset its bucket to 0) when the soil-moisture sensor reads strictly above this percentage. Needs a soil-moisture sensor set above. Only affects scheduled runs; manual runs always water.",irrigate_now:"Irrigate Now",bucket_threshold:"Minimum deficit to irrigate",plant_type:"Plant type",kc:"Crop coefficient (Kc)",plant_types:{custom:"Custom (set Kc manually)",lawn:"Lawn / turf",vegetables:"Vegetable garden",flowers:"Flower bed",shrubs:"Shrubs",trees:"Trees",xeriscape:"Xeriscape / drought-tolerant"},soil_type:"Soil type",soil_types:{custom:"Custom (set rate manually)",sand:"Sandy (fast draining)",loam:"Loam (balanced)",silt:"Silt (slow draining)",clay:"Clay (very slow draining)"},distributor:"Water distributor",distributor_help:"Assign this zone to an outlet of a mechanical water distributor. The distributor's inlet valve and its pulse-advance sequence then water this zone, so the zone's own valve and schedule below are managed by the distributor.",distributor_none:"None (own valve)",outlet_number:"Outlet number",distributor_managed_note:"This zone is watered through a distributor (outlet above). Its valve, inlet control and flow sensor are managed by the distributor and hidden here — only the calculation and soil-moisture veto settings remain. To give the zone its own valve again, set the distributor above to “None (own valve)”.",outlet_number_readonly_help:"Which outlet of the distributor feeds this zone. Set on the distributor page — open it with the button.",configure_on_distributor:"Configure on distributor"},no_items:"There are no zones defined yet.",title:"Zones",status:{decision_disabled:"Turned off — this zone won't be watered automatically.",decision_water:"Watering needed: about {duration} on the next scheduled run.",decision_water_at:"Will water about {duration} at {time}.",decision_water_skip:"Deficit ~{duration}, but the next run will likely be skipped ({reason}).",decision_water_no_schedule:"Deficit ~{duration} — no schedule waters this zone; trigger it manually.",decision_no_water:"No watering needed right now — the soil has enough moisture.",decision_unknown:"Not calculated yet — press Update, then Calculate to check.",last_checked:"Last checked",never:"never",saved:"Saved",estimate_now:"Now",estimate_tag:"est.",estimate_method:{hourly:"Live estimate from hourly weather since the last calculation",hourly_sensor:"Live estimate from hourly sensor readings since the last calculation",proxy:"Estimate distributed from today's forecast since the last calculation"}},fault:{title:"Last run failed",valve_no_response:"The valve didn't respond — no water was delivered, so the bucket was left unchanged.",flow_never_started:"No flow was detected — no water was delivered, so the bucket was left unchanged.",station_never_ran:"The OpenSprinkler controller never ran the station — no water was delivered, so the bucket was left unchanged.",station_unresolved:"The OpenSprinkler station could not be found — the run was not started, so the bucket was left unchanged.",station_wrong_mode:"An OpenSprinkler station is linked, but the zone's watering mode is not OpenSprinkler station — the run was refused, so the bucket was left unchanged.",generic:"The last irrigation run failed."},skip:{title:"Skipped",soil_moisture:"Soil moisture {observed} % > {threshold} %"},clamped:{title:"Duration capped",detail:"This zone needs longer than its maximum duration of {maximum}, so part of the deficit is left unwatered on every run. Deepening the bucket threshold has no effect until the cap is raised."},help:{bucket:"Soil-moisture balance. A negative value means the soil is dry and the zone needs water.",calculate:"Works out how long to water from the latest data. Run this after Update.",update:"Fetches the latest weather/sensor data for this zone.",irrigate_link_entity:"Link a switch/valve in this zone's settings to enable manual watering.",irrigate_all:"Opens the linked valves now for every zone with a deficit. Skip conditions (rain, wind, temperature) are ignored.",update_all:"Collects the latest weather/sensor data for all zones. Does not change durations on its own.",calculate_all:"Recomputes each automatic zone's watering duration from the data collected so far."},outlook:{next_run:"Next run",estimated:"estimated",estimated_help:"The start time is still a projection: the run is sized from the water demand read shortly before it begins, so this time moves until then.",no_schedule:"No automatic schedule — zones water only when you trigger them.",setup_schedule:"Set up a schedule",targets_all:"all zones",targets_zones:"{count} zones",will_skip:"Next run will likely be skipped",will_run:"Conditions look clear for the next run.",why_skipped:"Why?",provisional:"forecast — may change",active_guards:"Active guards",last_run:"Last run",last_run_skipped:"skipped",last_run_ran:"ran",today:"today",tomorrow:"tomorrow",actions:{irrigate:"Water",calculate:"Recalculate",update:"Refresh data"},checks:{precipitation:"Rain forecast",days_between:"Days between watering",temperature:"Low temperature",wind:"High wind",rain_sensor:"Rain sensor",freeze:"Frost",paused:"Paused (rain delay)",soil_moisture:"Soil moisture",no_demand:"No water demand"},check_detail:{precipitation:"{observed} mm (≥ {threshold} mm)",days_between:"{observed}/{threshold} days",temperature:"{observed}° (below {threshold}°)",wind:"{observed} (above {threshold})",rain_sensor:"{observed}",freeze:"{observed}° (below {threshold}°)"}},calendar:{no_data:"No watering calendar data available for this zone.",error_prefix:"Error generating calendar:",month:"Month",et:"ET (mm)",precipitation:"Precipitation (mm)",watering:"Watering (L)",avg_temp:"Avg Temp (°C)",method_prefix:"Method:"},confirm_action:{reset_bucket_title:"Reset this zone's bucket?",reset_bucket_body:"This sets the bucket back to 0, discarding the accumulated moisture balance for this zone.",reset_all_buckets_title:"Reset all buckets?",reset_all_buckets_body:"This sets every zone's bucket back to 0, discarding the accumulated moisture balance. Watering calculations start fresh from the next update.",clear_weather_title:"Clear all weather data?",clear_weather_body:"This deletes all collected weather and sensor records for every zone. Zones will need fresh data before they can calculate again."},confirm_irrigate:{title:"Start irrigation?",body:"This opens the linked valve(s) now and bypasses all skip conditions (rain, temperature, minimum days between watering).",all_linked_zones:"All linked zones",toast_started:"Irrigation started",toast_failed:"Irrigation failed"},history:{title:"Run history",total_used:"Total water used",empty:"No runs recorded yet.",when:"When",result:"Result",volume:"Volume",detail:"Detail",results:{completed:"Completed",partial:"Partial",failed:"Failed",skipped:"Skipped",observed:"Observed"}},rain_delay:{title:"Pause watering",paused:"Paused",until:"until",delay_24h:"Delay 24 h",delay_48h:"Delay 48 h",resume:"Resume"},run_zone:{run:"Run",minutes:"min",help:"Water this zone for a custom time, ignoring the calculation",toast_started:"Started run",busy_hint:"Distributor is running — you can start again once it is back in its home position."},stop_zone:{stop:"Stop",watering:"Watering…",toast_stopped:"Stopped run"}},distributors:{title:"Distributors",description:"Mechanical water distributors split one supply into several outlets, advanced by pulsing the water on and off.",no_items:"No distributors configured yet.",add:{header:"Add distributor",name_placeholder:"Distributor name",actions:{add:"Add"}},status:{saved:"Saved"},confirm_delete:"Delete this distributor? Zones assigned to it keep their outlet numbers but lose their distributor link.",labels:{name:"Name",watering_mode_help:"How the distributor's inlet valve is opened and closed.",inlet_entity:"Inlet valve / switch (optional)",inlet_entity_help:"The switch or valve entity that opens the water supply into the distributor. It is also watched for foreign pulses; once a valve is selected, a setting appears below to control the reaction.",watch_inlet:"Watch inlet valve for manual pulses",watch_inlet_help:"Only detects valve switches Home Assistant can see — purely mechanical pulses at the device stay invisible.",inlet_entity_help_service:"The ring valve Home Assistant watches for foreign pulses to keep the outlet position in sync (e.g. when the valve is opened manually or by an automation outside a HASI run). Once a valve is selected, a setting appears below to control the reaction. Actuation is via the run/stop service; this field is only read, and is NOT the flow/confirm sensor. Leave empty to disable inlet watching.",watch_mode:"On a manual inlet pulse",watch_mode_help:"How to react when the inlet valve is opened outside a Home Assistant run (only pulses Home Assistant can see).",watch_mode_count:"Count it (advance the position)",watch_mode_warn:"Warn (mark position uncertain)",watch_mode_ignore:"Ignore",run_service:"Run script",run_service_help:"Script called to open the inlet. It receives the pulse duration.",stop_service:"Stop script (optional)",stop_service_help:"Script called to close the inlet.",duration_field:"Duration field",duration_field_help:"Name of the field the run script expects the duration in.",duration_field_placeholder:"duration",duration_unit:"Duration unit",duration_units:{seconds:"Seconds",minutes:"Minutes"},confirm_entity:"Confirmation sensor (optional)",confirm_entity_help:"Optional sensor on the distributor inlet confirming water actually flows (e.g. a flow or valve-position sensor). If it reports no flow when an outlet opens, the cycle halts safely and marks the distributor uncertain — this is the low-flow / fault detection.",flow_sensor:"Flow sensor (optional)",flow_sensor_help:"The shared inlet flow-rate meter (e.g. L/min, m³/h). When set, the actual delivered volume per outlet is measured and credited instead of the time estimate. Optional. Where the valve can be stopped (a classic inlet, or a self-closing stop-service), the outlet also stops early once its target volume is reached. Both an instantaneous rate meter (e.g. L/min) and a cumulative totalizer counter (e.g. m³, or state_class: total_increasing) are supported and detected automatically from the unit.",pause_seconds:"Advance pause",skip_pulse_seconds:"Skip pulse",notify_target:"Notification target (optional)",notify_target_help:"Optional additional channel. Halts always appear in the Home Assistant notifications panel; set a notify service here (e.g. notify.mobile_app_phone) to also push them there.",notify_target_placeholder:"notify.mobile_app_phone"},notify:{halted:"Distributor '{name}' halted ({reason}). Re-sync and re-confirm required.",reason:{valve_did_not_open:"valve did not open",restart_mid_advance:"restarted mid-advance",foreign_inlet_pulse:"manual inlet pulse"}},commissioning:{title:"Commissioning",outlet:"Outlet",states:{synced:"Synced",uncertain:"Uncertain"},test_run:"Test run",test_run_help:"Waters each mapped outlet for about 30 seconds in order, so you can watch the device advance and note the pause it needs.",set_outlet:"Set current outlet",set_outlet_help:"Read the outlet number shown in the device window and set it here to re-sync the tracked position.",resync_home:"Reset to outlet 1",confirm_resync:{title:"Reset to outlet 1?",body:"This sets the tracked position to outlet 1. Only confirm if the device is physically at outlet 1 — otherwise the distributor will water the wrong outlets (an undetected desync)."},confirm_set_outlet:{title:"Set current outlet?",body:"This marks the distributor as synced at the outlet you entered. Only confirm if the device's window physically shows that outlet right now — a wrong value silently waters the wrong outlets."},confirmed:"Commissioning confirmed",confirmed_help:"Arms the distributor for automatic and manual cycles. Can only be set while the position is synced, and drops to off automatically if the position ever becomes uncertain.",needs_sync:"Set the position to synced before you can arm this distributor.",run_now:"Run now",run_now_help:"Runs one full manual cycle over all mapped outlets.",run_now_active:"A cycle is already running.",confirm_dialog:{title:"Arm this distributor?",body:"Confirm the device is physically at outlet 1 and every outlet is mapped to the right zone. Automatic and manual cycles will start pulsing the inlet.",confirm:"Confirm & arm"}},hints:{pressure:"Give the distributor at least 1 bar of water pressure and 20 l/h of flow. Mechanical distributors need a firm pulse to advance reliably.",below_floor_pause:"Very short pause. The advance pulse must be long enough for the distributor to actually step; the backend enforces a minimum of 10 seconds.",below_floor_skip:"Very short skip pulse. The backend enforces a minimum of 10 seconds.",undetectable:"The device's manual selector button cannot be read back. If you turn it by hand, use “Set current outlet” afterwards so the tracked position matches.",outlet_change:"Changing an outlet mapping moves the device off its known position. Re-sync and re-confirm commissioning before the next cycle.",parallel_draw:"Parallel sequencing opens several zones at once, but a distributor feeds one outlet at a time, so its mapped zones still water in sequence. Plan the supply draw accordingly.",master_off_after:"With sequential or rotating sequencing and “master off after each zone”, the pump is switched per outlet, so expect it to cycle between every outlet of the distributor.",experimental:"Experimental feature — still being refined and not fully hardware-tested. Watch the first days of use closely and keep the device's manual override within reach."},outlets:{title:"Outlets / zones",help:"Set how many outlets the distributor has, then assign a zone to each. Only zones without their own valve or script can be assigned — a zone is either on a distributor or has its own valve. The number of outlets equals the number of assigned zones, numbered contiguously from 1.",count:"Number of outlets",none:"— none",no_zones:"No zones yet. Create zones first (Setup → Zones), then assign them here.",gap_warning:"Outlets must be filled contiguously from 1 — assign a zone to every outlet up to the highest used one."}}},di="Smart Irrigation",ci={title:"Weather Service",description:"Configure which weather service to use for ET calculations and skip conditions.",enabled_label:"Enable weather service",service_label:"Weather service",api_key_label:"API key",api_key_placeholder:"Leave blank to keep existing key",api_key_configured:"API key is configured",api_key_not_configured:"No API key configured",api_key_help:"An API key from your chosen weather service provider. Open-Meteo does not require a key. OpenWeatherMap, Pirate Weather and the Met Office (Weather DataHub) all offer free tiers.",no_api_key_needed:"Open-Meteo is a free service and requires no API key.",save_button:"Save weather settings",saved:"Weather settings saved",owm:"OpenWeatherMap",pw:"Pirate Weather",openmeteo:"Open-Meteo (free, no key needed)",met:"Met Office (UK)",test_button:"Test Connection",test_button_testing:"Testing…",test_success:"✓ Connection successful",test_error_invalid_auth:"✗ Invalid API key — check that it is correct and active",test_error_cannot_connect:"✗ Cannot connect — check your internet connection",test_error_no_service:"✗ Select a weather service first",test_error_unknown:"✗ Test failed — unknown error"},hi={title:"Irrigation Start Triggers",description:"Configure when irrigation should start based on solar events. You can add multiple triggers for different schedules. For sunrise triggers, leaving offset at 0 will automatically use the total duration of all enabled zones.",add_trigger:"Add Trigger",edit_trigger:"Edit Trigger",delete_trigger:"Delete Trigger",trigger_types:{sunrise:"Sunrise",sunset:"Sunset",solar_azimuth:"Solar Azimuth"},fields:{name:{name:"Trigger Name",description:"A descriptive name to identify this trigger"},type:{name:"Trigger Type",description:"The type of solar event to trigger on"},enabled:{name:"Enabled",description:"Whether this trigger is currently active"},offset_minutes:{name:"Offset (minutes)",description:"Minutes before (-) or after (+) the solar event. For sunrise triggers, use 0 for automatic timing based on total zone duration."},azimuth_angle:{name:"Azimuth Angle (degrees)",description:"Solar azimuth angle in degrees where 0=North, 90=East, 180=South, 270=West"},account_for_duration:{name:"Account for Duration",description:"When enabled, irrigation will start early enough to finish at the specified time. When disabled, irrigation will start exactly at the specified time."}},dialog:{add_title:"Add Irrigation Start Trigger",edit_title:"Edit Irrigation Start Trigger",cancel:"Cancel",save:"Save",delete:"Delete"},no_triggers:"No irrigation start triggers configured. The system will use the default behavior (sunrise with total zone duration). Add triggers to customize when irrigation starts.",offset_auto:"Auto (calculated from total zone duration)",confirm_delete:"Are you sure you want to delete the trigger '{name}'?",validation:{name_required:"Trigger name is required",azimuth_invalid:"Azimuth angle must be a valid number"},help:{sunrise_offset:"For sunrise triggers: Use negative values to start before sunrise, positive to start after. Set to 0 to automatically start early enough to complete all zones before sunrise.",sunset_offset:"For sunset triggers: Use negative values to start before sunset, positive to start after sunset.",azimuth_explanation:"Solar azimuth is the compass direction of the sun. 0°=North, 90°=East, 180°=South, 270°=West. You can enter any angle value (e.g., 450° = 90°, -30° = 330°). Use this to trigger irrigation when the sun reaches a specific position.",multiple_triggers:"You can configure multiple triggers. Each enabled trigger will independently schedule irrigation starts."}},ui={title:"Skip Conditions",description:"Automatically skip irrigation when conditions are unfavorable. Precipitation check requires a weather service. Temperature and wind checks also require a weather service.",threshold_label:"Precipitation Threshold",threshold_description:"Minimum total precipitation (in mm) forecast across the look-ahead window to skip irrigation.",lookahead_label:"Forecast look-ahead (days)",lookahead_help:"How many upcoming forecast days to add up when checking for rain. The forecast starts at tomorrow (today is excluded), so 1 = just the next day, 2 = the next two days, and so on.",temp_section_title:"Skip on low temperature",temp_threshold_label:"Skip if temperature is below",wind_section_title:"Skip on high wind speed",wind_threshold_label:"Skip if wind speed is above",rain_sensor_section_title:"Skip on rain sensor",rain_sensor_label:"Rain sensor entity (optional)",rain_sensor_placeholder:"e.g. binary_sensor.rain",freeze_section_title:"Skip on frost",freeze_threshold_label:"Skip if minimum temperature is below",freeze_help:"Compares the current temperature and the coming night's forecast low; skips watering when frost is expected, to protect pipes and plants.",forecast_rain_label:"When rain is forecast",forecast_rain_options:{ignore:"Ignore it",water_less:"Water less",skip:"Skip watering"},forecast_rain_help:{ignore:"Forecast rain is ignored; runs use the calculated duration.",water_less:"Upcoming forecast rain trims the run duration (the deficit stays in the bucket for the real rain to fill).",skip:"Skip the run entirely when enough rain is forecast within the look-ahead window."}},pi={title:"Location Coordinates",description:"Configure location coordinates for weather data retrieval. You can use manual coordinates different from your Home Assistant location if needed.",manual_enabled:"Use manual coordinates",use_ha_location:"Use Home Assistant location",latitude:"Latitude (decimal degrees)",longitude:"Longitude (decimal degrees)",elevation:"Elevation (meters above sea level)",current_ha_coords:"Current Home Assistant coordinates"},gi={title:"Days Between Irrigation",description:"Configure the minimum number of days that must pass between irrigation events. This helps control watering frequency for water conservation and plant health management.\n\nTypical real-world use cases:\n• Lawn care: 1-2 day intervals prevent overwatering\n• Drought restrictions: 6+ day intervals for weekly watering\n• Deep-rooted plants: 3-7 day intervals for less frequent watering\n• Water conservation: Customizable based on climate and soil conditions",label:"Minimum days between irrigation",help_text:"Set to 0 to disable this feature. Values from 1-365 days are supported. This setting works alongside existing precipitation forecasting logic."},mi={title:"Zone Sequencing",description:"When multiple zones need irrigation, choose whether they run at the same time or one after another. Sequential mode waits for each zone to finish before starting the next. Rotating mode cycles through zones, giving each one a limited consecutive run before moving to the next.",parallel:"Parallel (all zones at once)",sequential:"Sequential (one zone at a time)",rotating:"Rotating (zones take turns)",max_consecutive_duration_label:"Max consecutive run time per zone",max_consecutive_duration_unit:"minutes",min_absorption_time_label:"Min. absorption time between slots",min_absorption_time_unit:"minutes (0 = disabled)"},vi={title:"Pump / master switch",description:"Optional. Powers a shared master — a pump or main valve — on before the first zone of a watering cycle, then optionally off after the last zone. Leave the entity empty to never touch a master (e.g. a pressure-controlled waterworks that starts on its own).",entity:"Master entity (switch/valve)",kick_enabled:"Kicker: pulse off then on to force a pump start",kick_pause:"Kick pause (off before on)",settle:"Settle delay before the first zone",off_after:"Turn the master off after irrigation",seconds_unit:"seconds"},fi={zone_size:"The total irrigated area of this zone. Used with throughput to calculate how much water is applied per run.",zone_throughput:"Total water flow of your irrigation system for this zone (litres/min in metric, gal/min in imperial). Check your sprinkler datasheet or measure by timing how long it takes to fill a known container.",zone_drainage_rate:"How fast saturated soil drains excess water. ~20 mm/h suits medium/loam soil; lower (2–10) for heavy clay, higher for sandy soil.",zone_bucket:"Current water deficit (negative) or surplus (positive) for this zone. Irrigation triggers when bucket drops below the threshold.",zone_maximum_bucket:"Maximum moisture surplus the zone can hold. Water above this level is treated as runoff. Typical value: 50 mm.",zone_bucket_threshold:"Irrigation triggers when the bucket drops below this value. Must be 0 or negative. 0 means irrigate whenever there is any deficit.",zone_multiplier:"Scale factor applied to the calculated duration. Use above 1.0 to increase, below 1.0 to decrease. Useful for fine-tuning without changing physical measurements.",zone_lead_time:"Extra seconds added before irrigation starts. Use for pump warm-up or system pressurisation.",zone_maximum_duration:"Hard cap on any single irrigation run in seconds. Prevents runaway watering. Default: 3600 s (1 hour).",zone_linked_entity:"The HA switch, valve or input_boolean (helper) entity controlling water flow for this zone. This entity is turned on when irrigation runs.",zone_flow_sensor:"Optional sensor measuring actual water flow rate. Used for reporting only — does not affect duration calculations.",general_autoupdatedelay:"Seconds to wait after HA starts before the first weather data fetch. Allows other integrations to initialise first.",general_sensor_debounce:"Minimum gap in milliseconds between sensor readings to filter noise from rapidly changing sensors.",general_calctime:"Time of day when irrigation durations are recalculated from collected weather data. Format: HH:MM (24-hour).",general_cleardatatime:"Time of day when old weather data is purged. Must be set later than the calculation time.",general_days_between:"Minimum days between irrigation events for the same zone. Set to 0 to disable (irrigate whenever deficit exists).",general_autoupdateinterval:"How often weather data is collected. Choose a value that balances fresh data against API rate limits.",general_precipitation_threshold:"Irrigation is skipped if total forecast precipitation across the look-ahead window exceeds this amount.",general_temp_threshold:"Irrigation is skipped if the current temperature is below this value (e.g. to prevent frost damage).",general_wind_threshold:"Irrigation is skipped if wind speed exceeds this value (high winds reduce efficiency and cause drift).",zone_plant_type:"Pick a plant type to set a typical crop coefficient, or choose Custom to enter Kc yourself.",zone_kc:"Scales reference (grass) ET to this zone's plants. 1.0 = reference grass; lower for drought-tolerant planting, higher for thirsty crops. Only the ET term is scaled — rain is not.",zone_soil_type:"Pick a soil type to set a typical drainage rate, or leave Custom to enter it by hand below.",distributor_pause_seconds:"Off-time between outlets. This is the pulse that advances the distributor to the next outlet; set it from what you saw during the test run. Minimum 10 seconds.",distributor_skip_pulse_seconds:"Short on/off pulse used to step past an outlet that has no zone mapped, without watering it. Minimum 10 seconds."},_i={title:"Setup Wizard",open_button:"Setup Wizard",close:"Close",next:"Next",back:"Back",finish:"Finish",skip_step:"Skip this step",step_indicator:"Step {current} of {total}",stepper:{weather:"Weather",module:"Module",mapping:"Sensor Group",zone:"Zone"},setup_complete_banner:"Setup not complete. Run the wizard to get started.",open_wizard:"Open Wizard",steps:{welcome:{title:"Welcome to Smart Irrigation",intro:"This wizard guides you through the four steps needed to get your first zone irrigating automatically.",step1_label:"Weather Service — where to get weather data",step2_label:"Calculation Module — how irrigation duration is computed",step3_label:"Sensor Group — which data sources to use",step4_label:"Zone — your first irrigation zone",tip:"You can skip any step and configure it later from the Setup tab."},weather:{title:"Weather Service",description:"Choose how to get weather data. Open-Meteo is free and requires no API key — it is the easiest choice for most users."},module:{title:"Calculation Module",description:"A module calculates how long to irrigate based on evapotranspiration (ET). The PyETO module (FAO-56 method) is recommended for most users.",pick_label:"Select module type",no_modules:"No module types available."},mapping:{title:"Sensor Group",description:"A sensor group links each weather variable to a data source. Set the key variables below — you can refine individual sensor mappings later from the Setup → Sensor Groups tab.",name_label:"Sensor group name",source_label:"Data source for",use_weather_service:"Weather service",use_sensor:"Sensor",use_static:"Static value",use_none:"None / not used"},zone:{title:"First Zone",description:"A zone is one irrigation area (e.g. lawn, garden bed). Set the physical properties so the system can calculate the correct irrigation duration.",name_label:"Zone name",size_label:"Area",throughput_label:"Sprinkler throughput",entity_label:"Linked switch, valve or helper",entity_placeholder:"e.g. switch.garden_valve",module_label:"Calculation module",mapping_label:"Sensor group"},done:{title:"Setup Complete!",description:"Your first zone is ready. Smart Irrigation will now calculate irrigation durations automatically based on weather data.",next_steps:"What you can do next:",tip1:"Go to Zones to view calculated durations and bucket values.",tip2:"Add more zones from the Zones tab.",tip3:"Refine all settings from the Setup tab.",go_zones:"Go to Zones",go_setup:"Go to Setup",schedule_name:"Daily",schedule_title:"Create a watering schedule",schedule_desc:"Your system is configured, but it won't water until a schedule exists. Create a daily schedule for all zones now (you can change or remove it later under Setup → When to Water).",schedule_create:"Create daily schedule",schedule_created:"Daily schedule created."}},confirm_close:{body:"Close the setup wizard? Your progress so far is saved.",keep:"Keep editing",close:"Close"}},bi={flow_calibration:ii,common:ai,defaults:ni,module:oi,calcmodules:ri,panels:li,title:di,weather_service_config:ci,irrigation_start_triggers:hi,weather_skip:ui,coordinate_config:pi,days_between_irrigation:gi,zone_sequencing:mi,master:vi,field_help:fi,wizard:_i},yi=Object.freeze({__proto__:null,calcmodules:ri,common:ai,coordinate_config:pi,days_between_irrigation:gi,default:bi,defaults:ni,field_help:fi,flow_calibration:ii,irrigation_start_triggers:hi,master:vi,module:oi,panels:li,title:di,weather_service_config:ci,weather_skip:ui,wizard:_i,zone_sequencing:mi});function wi(e,t){const s=t&&t.cache?t.cache:Ci,i=t&&t.serializer?t.serializer:Si;return(t&&t.strategy?t.strategy:zi)(e,{cache:s,serializer:i})}function $i(e,t,s,i){const a=null==(n=i)||"number"==typeof n||"boolean"==typeof n?i:s(i);var n;let o=t.get(a);return void 0===o&&(o=e.call(this,i),t.set(a,o)),o}function xi(e,t,s){const i=Array.prototype.slice.call(arguments,3),a=s(i);let n=t.get(a);return void 0===n&&(n=e.apply(this,i),t.set(a,n)),n}function ki(e,t,s,i,a){return s.bind(t,e,i,a)}function zi(e,t){return ki(e,this,1===e.length?$i:xi,t.cache.create(),t.serializer)}const Si=function(){return JSON.stringify(arguments)};var Ai=class{constructor(){this.cache=Object.create(null)}get(e){return this.cache[e]}set(e,t){this.cache[e]=t}};const Ci={create:function(){return new Ai}},Ei={variadic:function(e,t){return ki(e,this,xi,t.cache.create(),t.serializer)}},Ti=/(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;function Oi(e){const t={};return e.replace(Ti,e=>{const s=e.length;switch(e[0]){case"G":t.era=4===s?"long":5===s?"narrow":"short";break;case"y":t.year=2===s?"2-digit":"numeric";break;case"Y":case"u":case"U":case"r":throw new RangeError("`Y/u/U/r` (year) patterns are not supported, use `y` instead");case"q":case"Q":throw new RangeError("`q/Q` (quarter) patterns are not supported");case"M":case"L":t.month=["numeric","2-digit","short","long","narrow"][s-1];break;case"w":case"W":throw new RangeError("`w/W` (week) patterns are not supported");case"d":t.day=["numeric","2-digit"][s-1];break;case"D":case"F":case"g":throw new RangeError("`D/F/g` (day) patterns are not supported, use `d` instead");case"E":t.weekday=4===s?"long":5===s?"narrow":"short";break;case"e":if(s<4)throw new RangeError("`e..eee` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][s-4];break;case"c":if(s<4)throw new RangeError("`c..ccc` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][s-4];break;case"a":t.hour12=!0;break;case"b":case"B":throw new RangeError("`b/B` (period) patterns are not supported, use `a` instead");case"h":t.hourCycle="h12",t.hour=["numeric","2-digit"][s-1];break;case"H":t.hourCycle="h23",t.hour=["numeric","2-digit"][s-1];break;case"K":t.hourCycle="h11",t.hour=["numeric","2-digit"][s-1];break;case"k":t.hourCycle="h24",t.hour=["numeric","2-digit"][s-1];break;case"j":case"J":case"C":throw new RangeError("`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead");case"m":t.minute=["numeric","2-digit"][s-1];break;case"s":t.second=["numeric","2-digit"][s-1];break;case"S":case"A":throw new RangeError("`S/A` (second) patterns are not supported, use `s` instead");case"z":t.timeZoneName=s<4?"short":"long";break;case"Z":case"O":case"v":case"V":case"X":case"x":throw new RangeError("`Z/O/v/V/X/x` (timeZone) patterns are not supported, use `z` instead")}return""}),t}const Di=/[\t-\r \x85\u200E\u200F\u2028\u2029]/i;function Mi(e){return e.replace(/^(.*?)-/,"")}const Hi=/^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g,Ii=/^(@+)?(\+|#+)?[rs]?$/g,Ni=/(\*)(0+)|(#+)(0+)|(0+)/g,Li=/^(0+)$/;function Pi(e){const t={};return"r"===e[e.length-1]?t.roundingPriority="morePrecision":"s"===e[e.length-1]&&(t.roundingPriority="lessPrecision"),e.replace(Ii,function(e,s,i){return"string"!=typeof i?(t.minimumSignificantDigits=s.length,t.maximumSignificantDigits=s.length):"+"===i?t.minimumSignificantDigits=s.length:"#"===s[0]?t.maximumSignificantDigits=s.length:(t.minimumSignificantDigits=s.length,t.maximumSignificantDigits=s.length+("string"==typeof i?i.length:0)),""}),t}function Ri(e){switch(e){case"sign-auto":return{signDisplay:"auto"};case"sign-accounting":case"()":return{currencySign:"accounting"};case"sign-always":case"+!":return{signDisplay:"always"};case"sign-accounting-always":case"()!":return{signDisplay:"always",currencySign:"accounting"};case"sign-except-zero":case"+?":return{signDisplay:"exceptZero"};case"sign-accounting-except-zero":case"()?":return{signDisplay:"exceptZero",currencySign:"accounting"};case"sign-never":case"+_":return{signDisplay:"never"}}}function Bi(e){let t;if("E"===e[0]&&"E"===e[1]?(t={notation:"engineering"},e=e.slice(2)):"E"===e[0]&&(t={notation:"scientific"},e=e.slice(1)),t){const s=e.slice(0,2);if("+!"===s?(t.signDisplay="always",e=e.slice(2)):"+?"===s&&(t.signDisplay="exceptZero",e=e.slice(2)),!Li.test(e))throw new Error("Malformed concise eng/scientific notation");t.minimumIntegerDigits=e.length}return t}function Ui(e){const t=Ri(e);return t||{}}function ji(e){let t={};for(const s of e){switch(s.stem){case"percent":case"%":t.style="percent";continue;case"%x100":t.style="percent",t.scale=100;continue;case"currency":t.style="currency",t.currency=s.options[0];continue;case"group-off":case",_":t.useGrouping=!1;continue;case"precision-integer":case".":t.maximumFractionDigits=0;continue;case"measure-unit":case"unit":t.style="unit",t.unit=Mi(s.options[0]);continue;case"compact-short":case"K":t.notation="compact",t.compactDisplay="short";continue;case"compact-long":case"KK":t.notation="compact",t.compactDisplay="long";continue;case"scientific":t={...t,notation:"scientific",...s.options.reduce((e,t)=>({...e,...Ui(t)}),{})};continue;case"engineering":t={...t,notation:"engineering",...s.options.reduce((e,t)=>({...e,...Ui(t)}),{})};continue;case"notation-simple":t.notation="standard";continue;case"unit-width-narrow":t.currencyDisplay="narrowSymbol",t.unitDisplay="narrow";continue;case"unit-width-short":t.currencyDisplay="code",t.unitDisplay="short";continue;case"unit-width-full-name":t.currencyDisplay="name",t.unitDisplay="long";continue;case"unit-width-iso-code":t.currencyDisplay="symbol";continue;case"scale":t.scale=parseFloat(s.options[0]);continue;case"rounding-mode-floor":t.roundingMode="floor";continue;case"rounding-mode-ceiling":t.roundingMode="ceil";continue;case"rounding-mode-down":t.roundingMode="trunc";continue;case"rounding-mode-up":t.roundingMode="expand";continue;case"rounding-mode-half-even":t.roundingMode="halfEven";continue;case"rounding-mode-half-down":t.roundingMode="halfTrunc";continue;case"rounding-mode-half-up":t.roundingMode="halfExpand";continue;case"integer-width":if(s.options.length>1)throw new RangeError("integer-width stems only accept a single optional option");s.options[0].replace(Ni,function(e,s,i,a,n,o){if(s)t.minimumIntegerDigits=i.length;else{if(a&&n)throw new Error("We currently do not support maximum integer digits");if(o)throw new Error("We currently do not support exact integer digits")}return""});continue}if(Li.test(s.stem)){t.minimumIntegerDigits=s.stem.length;continue}if(Hi.test(s.stem)){if(s.options.length>1)throw new RangeError("Fraction-precision stems only accept a single optional option");s.stem.replace(Hi,function(e,s,i,a,n,o){return"*"===i?t.minimumFractionDigits=s.length:a&&"#"===a[0]?t.maximumFractionDigits=a.length:n&&o?(t.minimumFractionDigits=n.length,t.maximumFractionDigits=n.length+o.length):(t.minimumFractionDigits=s.length,t.maximumFractionDigits=s.length),""});const e=s.options[0];"w"===e?t={...t,trailingZeroDisplay:"stripIfInteger"}:e&&(t={...t,...Pi(e)});continue}if(Ii.test(s.stem)){t={...t,...Pi(s.stem)};continue}const e=Ri(s.stem);e&&(t={...t,...e});const i=Bi(s.stem);i&&(t={...t,...i})}return t}let Fi=function(e){return e[e.EXPECT_ARGUMENT_CLOSING_BRACE=1]="EXPECT_ARGUMENT_CLOSING_BRACE",e[e.EMPTY_ARGUMENT=2]="EMPTY_ARGUMENT",e[e.MALFORMED_ARGUMENT=3]="MALFORMED_ARGUMENT",e[e.EXPECT_ARGUMENT_TYPE=4]="EXPECT_ARGUMENT_TYPE",e[e.INVALID_ARGUMENT_TYPE=5]="INVALID_ARGUMENT_TYPE",e[e.EXPECT_ARGUMENT_STYLE=6]="EXPECT_ARGUMENT_STYLE",e[e.INVALID_NUMBER_SKELETON=7]="INVALID_NUMBER_SKELETON",e[e.INVALID_DATE_TIME_SKELETON=8]="INVALID_DATE_TIME_SKELETON",e[e.EXPECT_NUMBER_SKELETON=9]="EXPECT_NUMBER_SKELETON",e[e.EXPECT_DATE_TIME_SKELETON=10]="EXPECT_DATE_TIME_SKELETON",e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE=11]="UNCLOSED_QUOTE_IN_ARGUMENT_STYLE",e[e.EXPECT_SELECT_ARGUMENT_OPTIONS=12]="EXPECT_SELECT_ARGUMENT_OPTIONS",e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE=13]="EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE=14]="INVALID_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR=15]="EXPECT_SELECT_ARGUMENT_SELECTOR",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR=16]="EXPECT_PLURAL_ARGUMENT_SELECTOR",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT=17]="EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT=18]="EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT",e[e.INVALID_PLURAL_ARGUMENT_SELECTOR=19]="INVALID_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR=20]="DUPLICATE_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR=21]="DUPLICATE_SELECT_ARGUMENT_SELECTOR",e[e.MISSING_OTHER_CLAUSE=22]="MISSING_OTHER_CLAUSE",e[e.INVALID_TAG=23]="INVALID_TAG",e[e.INVALID_TAG_NAME=25]="INVALID_TAG_NAME",e[e.UNMATCHED_CLOSING_TAG=26]="UNMATCHED_CLOSING_TAG",e[e.UNCLOSED_TAG=27]="UNCLOSED_TAG",e}({});function Zi(e){return 0===e.type}function Wi(e){return 1===e.type}function qi(e){return 2===e.type}function Gi(e){return 3===e.type}function Ki(e){return 4===e.type}function Vi(e){return 5===e.type}function Yi(e){return 6===e.type}function Xi(e){return 7===e.type}function Ji(e){return 8===e.type}function Qi(e){return!(!e||"object"!=typeof e||0!==e.type)}function ea(e){return!(!e||"object"!=typeof e||1!==e.type)}const ta=/[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/,sa={"001":["H","h"],419:["h","H","hB","hb"],AC:["H","h","hb","hB"],AD:["H","hB"],AE:["h","hB","hb","H"],AF:["H","hb","hB","h"],AG:["h","hb","H","hB"],AI:["H","h","hb","hB"],AL:["h","H","hB"],AM:["H","hB"],AO:["H","hB"],AR:["h","H","hB","hb"],AS:["h","H"],AT:["H","hB"],AU:["h","hb","H","hB"],AW:["H","hB"],AX:["H"],AZ:["H","hB","h"],BA:["H","hB","h"],BB:["h","hb","H","hB"],BD:["h","hB","H"],BE:["H","hB"],BF:["H","hB"],BG:["H","hB","h"],BH:["h","hB","hb","H"],BI:["H","h"],BJ:["H","hB"],BL:["H","hB"],BM:["h","hb","H","hB"],BN:["hb","hB","h","H"],BO:["h","H","hB","hb"],BQ:["H"],BR:["H","hB"],BS:["h","hb","H","hB"],BT:["h","H"],BW:["H","h","hb","hB"],BY:["H","h"],BZ:["H","h","hb","hB"],CA:["h","hb","H","hB"],CC:["H","h","hb","hB"],CD:["hB","H"],CF:["H","h","hB"],CG:["H","hB"],CH:["H","hB","h"],CI:["H","hB"],CK:["H","h","hb","hB"],CL:["h","H","hB","hb"],CM:["H","h","hB"],CN:["H","hB","hb","h"],CO:["h","H","hB","hb"],CP:["H"],CR:["h","H","hB","hb"],CU:["h","H","hB","hb"],CV:["H","hB"],CW:["H","hB"],CX:["H","h","hb","hB"],CY:["h","H","hb","hB"],CZ:["H"],DE:["H","hB"],DG:["H","h","hb","hB"],DJ:["h","H"],DK:["H"],DM:["h","hb","H","hB"],DO:["h","H","hB","hb"],DZ:["h","hB","hb","H"],EA:["H","h","hB","hb"],EC:["h","H","hB","hb"],EE:["H","hB"],EG:["h","hB","hb","H"],EH:["h","hB","hb","H"],ER:["h","H"],ES:["H","hB","h","hb"],ET:["hB","hb","h","H"],FI:["H"],FJ:["h","hb","H","hB"],FK:["H","h","hb","hB"],FM:["h","hb","H","hB"],FO:["H","h"],FR:["H","hB"],GA:["H","hB"],GB:["H","h","hb","hB"],GD:["h","hb","H","hB"],GE:["H","hB","h"],GF:["H","hB"],GG:["H","h","hb","hB"],GH:["h","H"],GI:["H","h","hb","hB"],GL:["H","h"],GM:["h","hb","H","hB"],GN:["H","hB"],GP:["H","hB"],GQ:["H","hB","h","hb"],GR:["h","H","hb","hB"],GS:["H","h","hb","hB"],GT:["h","H","hB","hb"],GU:["h","hb","H","hB"],GW:["H","hB"],GY:["h","hb","H","hB"],HK:["h","hB","hb","H"],HN:["h","H","hB","hb"],HR:["H","hB"],HU:["H","h"],IC:["H","h","hB","hb"],ID:["H"],IE:["H","h","hb","hB"],IL:["H","hB"],IM:["H","h","hb","hB"],IN:["h","H"],IO:["H","h","hb","hB"],IQ:["h","hB","hb","H"],IR:["hB","H"],IS:["H"],IT:["H","hB"],JE:["H","h","hb","hB"],JM:["h","hb","H","hB"],JO:["h","hB","hb","H"],JP:["H","K","h"],KE:["hB","hb","H","h"],KG:["H","h","hB","hb"],KH:["hB","h","H","hb"],KI:["h","hb","H","hB"],KM:["H","h","hB","hb"],KN:["h","hb","H","hB"],KP:["h","H","hB","hb"],KR:["h","H","hB","hb"],KW:["h","hB","hb","H"],KY:["h","hb","H","hB"],KZ:["H","hB"],LA:["H","hb","hB","h"],LB:["h","hB","hb","H"],LC:["h","hb","H","hB"],LI:["H","hB","h"],LK:["H","h","hB","hb"],LR:["h","hb","H","hB"],LS:["h","H"],LT:["H","h","hb","hB"],LU:["H","h","hB"],LV:["H","hB","hb","h"],LY:["h","hB","hb","H"],MA:["H","h","hB","hb"],MC:["H","hB"],MD:["H","hB"],ME:["H","hB","h"],MF:["H","hB"],MG:["H","h"],MH:["h","hb","H","hB"],MK:["H","h","hb","hB"],ML:["H"],MM:["hB","hb","H","h"],MN:["H","h","hb","hB"],MO:["h","hB","hb","H"],MP:["h","hb","H","hB"],MQ:["H","hB"],MR:["h","hB","hb","H"],MS:["H","h","hb","hB"],MT:["H","h"],MU:["H","h"],MV:["H","h"],MW:["h","hb","H","hB"],MX:["h","H","hB","hb"],MY:["hb","hB","h","H"],MZ:["H","hB"],NA:["h","H","hB","hb"],NC:["H","hB"],NE:["H"],NF:["H","h","hb","hB"],NG:["H","h","hb","hB"],NI:["h","H","hB","hb"],NL:["H","hB"],NO:["H","h"],NP:["H","h","hB"],NR:["H","h","hb","hB"],NU:["H","h","hb","hB"],NZ:["h","hb","H","hB"],OM:["h","hB","hb","H"],PA:["h","H","hB","hb"],PE:["h","H","hB","hb"],PF:["H","h","hB"],PG:["h","H"],PH:["h","hB","hb","H"],PK:["h","hB","H"],PL:["H","h"],PM:["H","hB"],PN:["H","h","hb","hB"],PR:["h","H","hB","hb"],PS:["h","hB","hb","H"],PT:["H","hB"],PW:["h","H"],PY:["h","H","hB","hb"],QA:["h","hB","hb","H"],RE:["H","hB"],RO:["H","hB"],RS:["H","hB","h"],RU:["H"],RW:["H","h"],SA:["h","hB","hb","H"],SB:["h","hb","H","hB"],SC:["H","h","hB"],SD:["h","hB","hb","H"],SE:["H"],SG:["h","hb","H","hB"],SH:["H","h","hb","hB"],SI:["H","hB"],SJ:["H"],SK:["H"],SL:["h","hb","H","hB"],SM:["H","h","hB"],SN:["H","h","hB"],SO:["h","H"],SR:["H","hB"],SS:["h","hb","H","hB"],ST:["H","hB"],SV:["h","H","hB","hb"],SX:["H","h","hb","hB"],SY:["h","hB","hb","H"],SZ:["h","hb","H","hB"],TA:["H","h","hb","hB"],TC:["h","hb","H","hB"],TD:["h","H","hB"],TF:["H","h","hB"],TG:["H","hB"],TH:["H","h"],TJ:["H","h"],TL:["H","hB","hb","h"],TM:["H","h"],TN:["h","hB","hb","H"],TO:["h","H"],TR:["H","hB"],TT:["h","hb","H","hB"],TW:["hB","hb","h","H"],TZ:["hB","hb","H","h"],UA:["H","hB","h"],UG:["hB","hb","H","h"],UM:["h","hb","H","hB"],US:["h","hb","H","hB"],UY:["h","H","hB","hb"],UZ:["H","hB","h"],VA:["H","h","hB"],VC:["h","hb","H","hB"],VE:["h","H","hB","hb"],VG:["h","hb","H","hB"],VI:["h","hb","H","hB"],VN:["H","h"],VU:["h","H"],WF:["H","hB"],WS:["h","H"],XK:["H","hB","h"],YE:["h","hB","hb","H"],YT:["H","hB"],ZA:["H","h","hb","hB"],ZM:["h","hb","H","hB"],ZW:["H","h"],"af-ZA":["H","h","hB","hb"],"ar-001":["h","hB","hb","H"],"ca-ES":["H","h","hB"],"en-001":["h","hb","H","hB"],"en-HK":["h","hb","H","hB"],"en-IL":["H","h","hb","hB"],"en-MY":["h","hb","H","hB"],"es-BR":["H","h","hB","hb"],"es-ES":["H","h","hB","hb"],"es-GQ":["H","h","hB","hb"],"fr-CA":["H","h","hB"],"gl-ES":["H","h","hB"],"gu-IN":["hB","hb","h","H"],"hi-IN":["hB","h","H"],"it-CH":["H","h","hB"],"it-IT":["H","h","hB"],"kn-IN":["hB","h","H"],"ku-SY":["H","hB"],"ml-IN":["hB","h","H"],"mr-IN":["hB","hb","h","H"],"pa-IN":["hB","hb","h","H"],"ta-IN":["hB","h","hb","H"],"te-IN":["hB","h","H"],"zu-ZA":["H","hB","hb","h"]};function ia(e){let t=e.hourCycle;if(void 0===t&&e.hourCycles&&e.hourCycles.length&&(t=e.hourCycles[0]),t)switch(t){case"h24":return"k";case"h23":return"H";case"h12":return"h";case"h11":return"K";default:throw new Error("Invalid hourCycle")}const s=e.language;let i;return"root"!==s&&(i=e.maximize().region),(sa[i||""]||sa[s||""]||sa[`${s}-001`]||sa["001"])[0]}const aa=new RegExp(`^${ta.source}*`),na=new RegExp(`${ta.source}*$`);function oa(e,t){return{start:e,end:t}}const ra=!!Object.fromEntries,la=!!String.prototype.trimStart,da=!!String.prototype.trimEnd,ca=ra?Object.fromEntries:function(e){const t={};for(const[s,i]of e)t[s]=i;return t},ha=la?function(e){return e.trimStart()}:function(e){return e.replace(aa,"")},ua=da?function(e){return e.trimEnd()}:function(e){return e.replace(na,"")},pa=new RegExp("([^\\p{White_Space}\\p{Pattern_Syntax}]*)","yu");var ga=class{constructor(e,t={}){this.message=e,this.position={offset:0,line:1,column:1},this.ignoreTag=!!t.ignoreTag,this.locale=t.locale,this.requiresOtherClause=!!t.requiresOtherClause,this.shouldParseSkeletons=!!t.shouldParseSkeletons}parse(){if(0!==this.offset())throw Error("parser can only be used once");if(this.message.length>0){const e=this.message.charCodeAt(0);if(35!==e&&39!==e&&60!==e&&123!==e&&125!==e){const e=function(e){if(0===e.length)return null;let t=1,s=1;for(let i=0;i<e.length;){const a=e.charCodeAt(i);switch(a){case 35:case 39:case 60:case 123:case 125:return null}if(10===a)t++,s=1,i++;else if(s++,a>=55296&&a<=56319&&i+1<e.length){const t=e.charCodeAt(i+1);i+=t>=56320&&t<=57343?2:1}else i++}return{offset:e.length,line:t,column:s}}(this.message);if(e){const t=this.clonePosition();return this.position=e,{val:[{type:0,value:this.message,location:oa(t,this.clonePosition())}],err:null}}}}return this.parseMessage(0,"",!1)}parseMessage(e,t,s){let i=[];for(;!this.isEOF();){const a=this.char();if(123===a){const t=this.parseArgument(e,s);if(t.err)return t;i.push(t.val)}else{if(125===a&&e>0)break;if(35!==a||"plural"!==t&&"selectordinal"!==t){if(60===a&&!this.ignoreTag&&47===this.peek()){if(s)break;return this.error(26,oa(this.clonePosition(),this.clonePosition()))}if(60===a&&!this.ignoreTag&&ma(this.peek()||0)){const s=this.parseTag(e,t);if(s.err)return s;i.push(s.val)}else{const s=this.parseLiteral(e,t);if(s.err)return s;i.push(s.val)}}else{const e=this.clonePosition();this.bump(),i.push({type:7,location:oa(e,this.clonePosition())})}}}return{val:i,err:null}}parseTag(e,t){const s=this.clonePosition();this.bump();const i=this.parseTagName();if(this.bumpSpace(),this.bumpIf("/>"))return{val:{type:0,value:`<${i}/>`,location:oa(s,this.clonePosition())},err:null};if(this.bumpIf(">")){const a=this.parseMessage(e+1,t,!0);if(a.err)return a;const n=a.val,o=this.clonePosition();if(this.bumpIf("</")){if(this.isEOF()||!ma(this.char()))return this.error(23,oa(o,this.clonePosition()));const e=this.clonePosition();return i!==this.parseTagName()?this.error(26,oa(e,this.clonePosition())):(this.bumpSpace(),this.bumpIf(">")?{val:{type:8,value:i,children:n,location:oa(s,this.clonePosition())},err:null}:this.error(23,oa(o,this.clonePosition())))}return this.error(27,oa(s,this.clonePosition()))}return this.error(23,oa(s,this.clonePosition()))}parseTagName(){const e=this.offset();for(this.bump();!this.isEOF()&&va(this.char());)this.bump();return this.message.slice(e,this.offset())}parseLiteral(e,t){const s=this.clonePosition();let i="";for(;;){const s=this.tryParseQuote(t);if(s){i+=s;continue}const a=this.tryParseUnquoted(e,t);if(a){i+=a;continue}const n=this.tryParseLeftAngleBracket();if(!n)break;i+=n}return{val:{type:0,value:i,location:oa(s,this.clonePosition())},err:null}}tryParseLeftAngleBracket(){return this.isEOF()||60!==this.char()||!this.ignoreTag&&(ma(e=this.peek()||0)||47===e)?null:(this.bump(),"<");var e}tryParseQuote(e){if(this.isEOF()||39!==this.char())return null;switch(this.peek()){case 39:return this.bump(),this.bump(),"'";case 123:case 60:case 62:case 125:break;case 35:if("plural"===e||"selectordinal"===e)break;return null;default:return null}this.bump();const t=[this.char()];for(this.bump();!this.isEOF();){const e=this.char();if(39===e){if(39!==this.peek()){this.bump();break}t.push(39),this.bump()}else t.push(e);this.bump()}return String.fromCodePoint(...t)}tryParseUnquoted(e,t){if(this.isEOF())return null;const s=this.char();return 60===s||123===s||35===s&&("plural"===t||"selectordinal"===t)||125===s&&e>0?null:(this.bump(),String.fromCodePoint(s))}parseArgument(e,t){const s=this.clonePosition();if(this.bump(),this.bumpSpace(),this.isEOF())return this.error(1,oa(s,this.clonePosition()));if(125===this.char())return this.bump(),this.error(2,oa(s,this.clonePosition()));let i=this.parseIdentifierIfPossible().value;if(!i)return this.error(3,oa(s,this.clonePosition()));if(this.bumpSpace(),this.isEOF())return this.error(1,oa(s,this.clonePosition()));switch(this.char()){case 125:return this.bump(),{val:{type:1,value:i,location:oa(s,this.clonePosition())},err:null};case 44:return this.bump(),this.bumpSpace(),this.isEOF()?this.error(1,oa(s,this.clonePosition())):this.parseArgumentOptions(e,t,i,s);default:return this.error(3,oa(s,this.clonePosition()))}}parseIdentifierIfPossible(){const e=this.clonePosition(),t=this.offset(),s=function(e,t){return pa.lastIndex=t,pa.exec(e)[1]??""}(this.message,t),i=t+s.length;return this.bumpTo(i),{value:s,location:oa(e,this.clonePosition())}}parseArgumentOptions(e,t,s,i){let a=this.clonePosition(),n=this.parseIdentifierIfPossible().value,o=this.clonePosition();switch(n){case"":return this.error(4,oa(a,o));case"number":case"date":case"time":{this.bumpSpace();let e=null;if(this.bumpIf(",")){this.bumpSpace();const t=this.clonePosition(),s=this.parseSimpleArgStyleIfPossible();if(s.err)return s;const i=ua(s.val);if(0===i.length)return this.error(6,oa(this.clonePosition(),this.clonePosition()));e={style:i,styleLocation:oa(t,this.clonePosition())}}const t=this.tryParseArgumentClose(i);if(t.err)return t;const a=oa(i,this.clonePosition());if(e&&e.style.startsWith("::")){let t=ha(e.style.slice(2));if("number"===n){const i=this.parseNumberSkeletonFromString(t,e.styleLocation);return i.err?i:{val:{type:2,value:s,location:a,style:i.val},err:null}}{if(0===t.length)return this.error(10,a);let i=t;this.locale&&(i=function(e,t){let s="";for(let i=0;i<e.length;i++){const a=e.charAt(i);if("j"===a){let n=0;for(;i+1<e.length&&e.charAt(i+1)===a;)n++,i++;let o=1+(1&n),r=n<2?1:3+(n>>1),l="a",d=ia(t);for("H"!=d&&"k"!=d||(r=0);r-- >0;)s+=l;for(;o-- >0;)s=d+s}else s+="J"===a?"H":a}return s}(t,this.locale));return{val:{type:"date"===n?3:4,value:s,location:a,style:{type:1,pattern:i,location:e.styleLocation,parsedOptions:this.shouldParseSkeletons?Oi(i):{}}},err:null}}}return{val:{type:"number"===n?2:"date"===n?3:4,value:s,location:a,style:e?.style??null},err:null}}case"plural":case"selectordinal":case"select":{const a=this.clonePosition();if(this.bumpSpace(),!this.bumpIf(","))return this.error(12,oa(a,{...a}));this.bumpSpace();let o=this.parseIdentifierIfPossible(),r=0;if("select"!==n&&"offset"===o.value){if(!this.bumpIf(":"))return this.error(13,oa(this.clonePosition(),this.clonePosition()));this.bumpSpace();const e=this.tryParseDecimalInteger(13,14);if(e.err)return e;this.bumpSpace(),o=this.parseIdentifierIfPossible(),r=e.val}const l=this.tryParsePluralOrSelectOptions(e,n,t,o);if(l.err)return l;const d=this.tryParseArgumentClose(i);if(d.err)return d;const c=oa(i,this.clonePosition());return"select"===n?{val:{type:5,value:s,options:ca(l.val),location:c},err:null}:{val:{type:6,value:s,options:ca(l.val),offset:r,pluralType:"plural"===n?"cardinal":"ordinal",location:c},err:null}}default:return this.error(5,oa(a,o))}}tryParseArgumentClose(e){return this.isEOF()||125!==this.char()?this.error(1,oa(e,this.clonePosition())):(this.bump(),{val:!0,err:null})}parseSimpleArgStyleIfPossible(){let e=0;const t=this.clonePosition();for(;!this.isEOF();)switch(this.char()){case 39:{this.bump();let e=this.clonePosition();if(!this.bumpUntil("'"))return this.error(11,oa(e,this.clonePosition()));this.bump();break}case 123:e+=1,this.bump();break;case 125:if(!(e>0))return{val:this.message.slice(t.offset,this.offset()),err:null};e-=1;break;default:this.bump()}return{val:this.message.slice(t.offset,this.offset()),err:null}}parseNumberSkeletonFromString(e,t){let s=[];try{s=function(e){if(0===e.length)throw new Error("Number skeleton cannot be empty");const t=e.split(Di).filter(e=>e.length>0),s=[];for(const e of t){let t=e.split("/");if(0===t.length)throw new Error("Invalid number skeleton");const[i,...a]=t;for(const e of a)if(0===e.length)throw new Error("Invalid number skeleton");s.push({stem:i,options:a})}return s}(e)}catch{return this.error(7,t)}return{val:{type:0,tokens:s,location:t,parsedOptions:this.shouldParseSkeletons?ji(s):{}},err:null}}tryParsePluralOrSelectOptions(e,t,s,i){let a=!1;const n=[],o=new Set;let{value:r,location:l}=i;for(;;){if(0===r.length){const e=this.clonePosition();if("select"===t||!this.bumpIf("="))break;{const t=this.tryParseDecimalInteger(16,19);if(t.err)return t;l=oa(e,this.clonePosition()),r=this.message.slice(e.offset,this.offset())}}if(o.has(r))return this.error("select"===t?21:20,l);"other"===r&&(a=!0),this.bumpSpace();const i=this.clonePosition();if(!this.bumpIf("{"))return this.error("select"===t?17:18,oa(this.clonePosition(),this.clonePosition()));const d=this.parseMessage(e+1,t,s);if(d.err)return d;const c=this.tryParseArgumentClose(i);if(c.err)return c;n.push([r,{value:d.val,location:oa(i,this.clonePosition())}]),o.add(r),this.bumpSpace(),({value:r,location:l}=this.parseIdentifierIfPossible())}return 0===n.length?this.error("select"===t?15:16,oa(this.clonePosition(),this.clonePosition())):this.requiresOtherClause&&!a?this.error(22,oa(this.clonePosition(),this.clonePosition())):{val:n,err:null}}tryParseDecimalInteger(e,t){let s=1;const i=this.clonePosition();this.bumpIf("+")||this.bumpIf("-")&&(s=-1);let a=!1,n=0;for(;!this.isEOF();){const e=this.char();if(!(e>=48&&e<=57))break;a=!0,n=10*n+(e-48),this.bump()}const o=oa(i,this.clonePosition());return a?(n*=s,Number.isSafeInteger(n)?{val:n,err:null}:this.error(t,o)):this.error(e,o)}offset(){return this.position.offset}isEOF(){return this.offset()===this.message.length}clonePosition(){return{offset:this.position.offset,line:this.position.line,column:this.position.column}}char(){const e=this.position.offset;if(e>=this.message.length)throw Error("out of bound");const t=this.message.codePointAt(e);if(void 0===t)throw Error(`Offset ${e} is at invalid UTF-16 code unit boundary`);return t}error(e,t){return{val:null,err:{kind:e,message:this.message,location:t}}}bump(){if(this.isEOF())return;const e=this.char();10===e?(this.position.line+=1,this.position.column=1,this.position.offset+=1):(this.position.column+=1,this.position.offset+=e<65536?1:2)}bumpIf(e){if(this.message.startsWith(e,this.offset())){for(let t=0;t<e.length;t++)this.bump();return!0}return!1}bumpUntil(e){const t=this.offset(),s=this.message.indexOf(e,t);return s>=0?(this.bumpTo(s),!0):(this.bumpTo(this.message.length),!1)}bumpTo(e){if(this.offset()>e)throw Error(`targetOffset ${e} must be greater than or equal to the current offset ${this.offset()}`);for(e=Math.min(e,this.message.length);;){const t=this.offset();if(t===e)break;if(t>e)throw Error(`targetOffset ${e} is at invalid UTF-16 code unit boundary`);if(this.bump(),this.isEOF())break}}bumpSpace(){for(;!this.isEOF()&&fa(this.char());)this.bump()}peek(){if(this.isEOF())return null;const e=this.char(),t=this.offset();return this.message.charCodeAt(t+(e>=65536?2:1))??null}};function ma(e){return e>=97&&e<=122||e>=65&&e<=90}function va(e){return 45===e||46===e||e>=48&&e<=57||95===e||e>=97&&e<=122||e>=65&&e<=90||183==e||e>=192&&e<=214||e>=216&&e<=246||e>=248&&e<=893||e>=895&&e<=8191||e>=8204&&e<=8205||e>=8255&&e<=8256||e>=8304&&e<=8591||e>=11264&&e<=12271||e>=12289&&e<=55295||e>=63744&&e<=64975||e>=65008&&e<=65533||e>=65536&&e<=983039}function fa(e){return e>=9&&e<=13||32===e||133===e||e>=8206&&e<=8207||8232===e||8233===e}function _a(e){e.forEach(e=>{if(delete e.location,Vi(e)||Yi(e))for(const t in e.options)delete e.options[t].location,_a(e.options[t].value);else qi(e)&&Qi(e.style)||(Gi(e)||Ki(e))&&ea(e.style)?delete e.style.location:Ji(e)&&_a(e.children)})}function ba(e,t={}){t={shouldParseSkeletons:!0,requiresOtherClause:!0,...t};const s=new ga(e,t).parse();if(s.err){const e=SyntaxError(Fi[s.err.kind]);throw e.location=s.err.location,e.originalMessage=s.err.message,e}return t?.captureLocation||_a(s.val),s.val}var ya=class extends Error{constructor(e,t,s){super(e),this.code=t,this.originalMessage=s}toString(){return`[formatjs Error: ${this.code}] ${this.message}`}},wa=class extends ya{constructor(e,t,s,i){super(`Invalid values for "${e}": "${t}". Options are "${Object.keys(s).join('", "')}"`,"INVALID_VALUE",i)}},$a=class extends ya{constructor(e,t,s){super(`Value for "${e}" must be of type ${t}`,"INVALID_VALUE",s)}},xa=class extends ya{constructor(e,t){super(`The intl string context variable "${e}" was not provided to the string "${t}"`,"MISSING_VALUE",t)}};function ka(e){return"function"==typeof e}function za(e,t,s,i,a,n,o){if(1===e.length&&Zi(e[0]))return[{type:0,value:e[0].value}];const r=[];for(const l of e){if(Zi(l)){r.push({type:0,value:l.value});continue}if(Xi(l)){"number"==typeof n&&r.push({type:0,value:s.getNumberFormat(t).format(n)});continue}const{value:e}=l;if(!a||!(e in a))throw new xa(e,o);let d=a[e];if(Wi(l))d&&"string"!=typeof d&&"number"!=typeof d&&"bigint"!=typeof d||(d="string"==typeof d||"number"==typeof d||"bigint"==typeof d?String(d):""),r.push({type:"string"==typeof d?0:1,value:d});else{if(Gi(l)){const e="string"==typeof l.style?i.date[l.style]:ea(l.style)?l.style.parsedOptions:void 0;r.push({type:0,value:s.getDateTimeFormat(t,e).format(d)});continue}if(Ki(l)){const e="string"==typeof l.style?i.time[l.style]:ea(l.style)?l.style.parsedOptions:i.time.medium;r.push({type:0,value:s.getDateTimeFormat(t,e).format(d)});continue}if(qi(l)){const e="string"==typeof l.style?i.number[l.style]:Qi(l.style)?l.style.parsedOptions:void 0;if(e&&e.scale){const t=e.scale||1;if("bigint"==typeof d){if(!Number.isInteger(t))throw new TypeError(`Cannot apply fractional scale ${t} to bigint value. Scale must be an integer when formatting bigint.`);d*=BigInt(t)}else d*=t}r.push({type:0,value:s.getNumberFormat(t,e).format(d)});continue}if(Ji(l)){const{children:e,value:d}=l,c=a[d];if(!ka(c))throw new $a(d,"function",o);let h=c(za(e,t,s,i,a,n).map(e=>e.value));Array.isArray(h)||(h=[h]),r.push(...h.map(e=>({type:"string"==typeof e?0:1,value:e})))}if(Vi(l)){const e=d,n=(Object.prototype.hasOwnProperty.call(l.options,e)?l.options[e]:void 0)||l.options.other;if(!n)throw new wa(l.value,d,Object.keys(l.options),o);r.push(...za(n.value,t,s,i,a));continue}if(Yi(l)){const e=`=${d}`;let n=Object.prototype.hasOwnProperty.call(l.options,e)?l.options[e]:void 0;if(!n){if(!Intl.PluralRules)throw new ya('Intl.PluralRules is not available in this environment.\nTry polyfilling it using "@formatjs/intl-pluralrules"\n',"MISSING_INTL_API",o);const e="bigint"==typeof d?Number(d):d,i=s.getPluralRules(t,{type:l.pluralType}).select(e-(l.offset||0));n=(Object.prototype.hasOwnProperty.call(l.options,i)?l.options[i]:void 0)||l.options.other}if(!n)throw new wa(l.value,d,Object.keys(l.options),o);const c="bigint"==typeof d?Number(d):d;r.push(...za(n.value,t,s,i,a,c-(l.offset||0)));continue}}}return(l=r).length<2?l:l.reduce((e,t)=>{const s=e[e.length-1];return s&&0===s.type&&0===t.type?s.value+=t.value:e.push(t),e},[]);var l}function Sa(e,t){return t?Object.keys(e).reduce((s,i)=>{var a,n;return s[i]=(a=e[i],(n=t[i])?{...a,...n,...Object.keys(a).reduce((e,t)=>(e[t]={...a[t],...n[t]},e),{})}:a),s},{...e}):e}function Aa(e){return{create:()=>({get:t=>e[t],set(t,s){e[t]=s}})}}var Ca=class e{constructor(t,s=e.defaultLocale,i,a){if(this.formatterCache={number:{},dateTime:{},pluralRules:{}},this.format=e=>{const t=this.formatToParts(e);if(1===t.length)return t[0].value;const s=t.reduce((e,t)=>(e.length&&0===t.type&&"string"==typeof e[e.length-1]?e[e.length-1]+=t.value:e.push(t.value),e),[]);return s.length<=1?s[0]||"":s},this.formatToParts=e=>za(this.ast,this.locales,this.formatters,this.formats,e,void 0,this.message),this.resolvedOptions=()=>({locale:this.resolvedLocale?.toString()||Intl.NumberFormat.supportedLocalesOf(this.locales)[0]}),this.getAst=()=>this.ast,this.locales=s,this.resolvedLocale=e.resolveLocale(s),"string"==typeof t){if(this.message=t,!e.__parse)throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");const{...s}=a||{};this.ast=e.__parse(t,{...s,locale:this.resolvedLocale})}else this.ast=t;if(!Array.isArray(this.ast))throw new TypeError("A message must be provided as a String or AST.");this.formats=Sa(e.formats,i),this.formatters=a&&a.formatters||function(e={number:{},dateTime:{},pluralRules:{}}){return{getNumberFormat:wi((...e)=>new Intl.NumberFormat(...e),{cache:Aa(e.number),strategy:Ei.variadic}),getDateTimeFormat:wi((...e)=>new Intl.DateTimeFormat(...e),{cache:Aa(e.dateTime),strategy:Ei.variadic}),getPluralRules:wi((...e)=>new Intl.PluralRules(...e),{cache:Aa(e.pluralRules),strategy:Ei.variadic})}}(this.formatterCache)}static{this.memoizedDefaultLocale=null}static get defaultLocale(){return e.memoizedDefaultLocale||(e.memoizedDefaultLocale=(new Intl.NumberFormat).resolvedOptions().locale),e.memoizedDefaultLocale}static{this.resolveLocale=e=>{if(void 0===Intl.Locale)return;const t=Intl.NumberFormat.supportedLocalesOf(e);return t.length>0?new Intl.Locale(t[0]):new Intl.Locale("string"==typeof e?e:e[0])}}static{this.__parse=ba}static{this.formats={number:{integer:{maximumFractionDigits:0},currency:{style:"currency"},percent:{style:"percent"}},date:{short:{month:"numeric",day:"numeric",year:"2-digit"},medium:{month:"short",day:"numeric",year:"numeric"},long:{month:"long",day:"numeric",year:"numeric"},full:{weekday:"long",month:"long",day:"numeric",year:"numeric"}},time:{short:{hour:"numeric",minute:"numeric"},medium:{hour:"numeric",minute:"numeric",second:"numeric"},long:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"},full:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"}}}}};const Ea={en:yi},Ta={};function Oa(e){return e.replace(/['"]+/g,"").split(/[-_]/)[0].toLowerCase()}function Da(e){const t=Oa(e);return t in Ea||!ye.includes(t)}function Ma(e,t,...s){const i=Oa(t);let a;try{a=e.split(".").reduce((e,t)=>e[t],Ea[i])}catch(t){a=e.split(".").reduce((e,t)=>e[t],Ea.en)}if(void 0===a&&(a=e.split(".").reduce((e,t)=>e[t],Ea.en)),!s.length)return a;const n={};for(let e=0;e<s.length;e+=2){let t=s[e];t=t.replace(/^{([^}]+)?}$/,"$1"),n[t]=s[e+1]}try{return new Ca(a,t).format(n)}catch(e){return"Translation "+e}}function Ha(e,t,s){e.dispatchEvent(new CustomEvent(t,{detail:s,bubbles:!0,composed:!0,cancelable:!1}))}function Ia(e,t){return(e=e.toString()).split(",")[t]}function Na(e,t){switch(t){case zt:return e.units==Me?W`${si(ht)}`:W`${si(ut)}`;case xe:case bt:return e.units==Me?W`${si(ot)}`:W`${si(rt)}`;case gt:return e.units==Me?W`${si("m<sup>2</sup>")}`:W`${si(st)}`;case mt:return e.units==Me?W`${si(it)}`:W`${si(at)}`;default:return W``}}function La(e,t){!function(e,t){Ha(e,"show-dialog",{dialogTag:"error-dialog",dialogImport:()=>Promise.resolve().then(function(){return _o}),dialogParams:{error:t}})}(t,W`
=======
     */class ti extends ei{constructor(e){if(super(e),this.it=K,e.type!==Ys)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(e){if(e===K||null==e)return this._t=void 0,this.it=e;if(e===G)return e;if("string"!=typeof e)throw Error(this.constructor.directiveName+"() called with a non-string value");if(e===this.it)return this._t;this.it=e;const t=[e];return t.raw=t,this._t={_$litType$:this.constructor.resultType,strings:t,values:[]}}}ti.directiveName="unsafeHTML",ti.resultType=1;const si=Qs(ti);var ii={title:"Smart Irrigation: check flow rate",message_over:"Zone '{zone}' is consistently over-watering: the measured flow is ~{percent}% above the configured rate over {runs} runs. Its valve can't stop early, so consider setting the throughput to about {rate} {unit} (currently {current}).",message_under:"Zone '{zone}' is consistently under-watering: the measured flow is ~{percent}% below the configured rate over {runs} runs. Its valve can't stop early, so consider setting the throughput to about {rate} {unit} (currently {current}).",open_settings:"Open zone settings"},ai={loading:"Loading",saving:"Saving",actions:{delete:"Delete",edit:"Edit",save:"Save",cancel:"Cancel",confirm_delete:"Confirm Delete",confirm_delete_zone:"Are you sure you want to delete this zone?"},labels:{module:"Module",no:"No",select:"Select",yes:"Yes",enabled:"Enabled",disabled:"Disabled",before:"before",after:"after",settings:"Settings",bulk_actions:"Bulk Actions"},units:{seconds:"seconds"},attributes:{size:"size",throughput:"throughput",state:"state",bucket:"bucket",last_updated:"last updated",last_calculated:"last calculated",number_of_data_points:"number of data points"},"loading-messages":{configuration:"Loading configuration...",modules:"Loading modules...",general:"Loading..."},"saving-messages":{adding:"Adding...",saving:"Saving..."},errors:{load_failed:"Couldn't load data",save_failed:"Couldn't save changes",delete_failed:"Couldn't delete",action_failed:"Action failed"}},ni={"default-zone":"Default zone","default-mapping":"Default sensor group"},oi={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"Note: this explanation uses '.' as decimal separator, shows rounded and metric values. Module returned Evapotranspiration deficiency ( = et0 * hour_multiplier + precipitation) of","module-returned-evapotranspiration-deficiency-hourly":"Note: this explanation uses '.' as decimal separator, shows rounded and metric values. Evapotranspiration deficiency ( = sum of hourly FAO-56 et0 over the window + precipitation) of","bucket-was":"Bucket was","new-bucket-values-is":"New bucket value is",bucket:"bucket","old-bucket-variable":"old_bucket","max-bucket-variable":"max_bucket",delta:"delta","bucket-less-than-zero-irrigation-necessary":"Since bucket < 0, irrigation is necessary","steps-taken-to-calculate-duration":"To calculate the exact duration, the following steps were taken","precipitation-rate-defined-as":"The precipitation rate is defined as","duration-is-calculated-as":"The duration is calculated as",drainage:"drainage","drainage-rate":"drainage_rate",hours:"hours","precipitation-rate-variable":"precipitation_rate","multiplier-is-applied":"Now, the multiplier is applied. The multiplier is","duration-after-multiplier-is":"hence the duration is","maximum-duration-is-applied":"Then, the maximum duration is applied. The maximum duration is","duration-after-maximum-duration-is":"hence the duration is","lead-time-is-applied":"Finally, the lead time is applied. The lead time is","duration-after-lead-time-is":"hence the final duration is","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Since bucket >= 0, no irrigation is necessary and duration is set to","maximum-bucket-is":"Maximum bucket size is","drainage-rate-is":"Drainage rate when saturated (bucket at max) is","current-drainage-is":"Current drainage is calculated as","drainage-integrated":"the surplus above field capacity drains continuously over the window (Brooks–Corey), so the rate falls as it drains","no-drainage":"Current drainage is 0 because","water-balance-substepped":"The water balance was replayed across the window, so rain, drainage and the maximum bucket clamp were applied at the times they occurred rather than all at the start of the window. Number of steps:","runoff-is":"Water above the maximum bucket that was lost to runoff:","runoff-variable":"runoff","forecast-weighting-applied":"Forecast weighting reduced the deficit for the expected rain","crop-coefficient-applied":"Scaled by the crop coefficient"}}},ri={pyeto:{description:"Calculate duration based on the FAO56 calculation from the PyETO library"},static:{description:"'Dummy' module with a static configurable delta"},passthrough:{description:"Passthrough module that returns the value of an Evapotranspiration sensor as delta"}},li={general:{cards:{"automatic-duration-calculation":{header:"Automatic duration calculation",description:"Calculation takes collected weather data up to that point and updates the bucket for each automatic zone. Then, the duration is adjusted based on the new bucket value and the collected weather data is removed.",labels:{"auto-calc-enabled":"Automatically calculate irrigation durations","calc-time":"Calculate at","calc-mode":"Calculate"},modes:{fixed_time:"At a fixed time",before_run:"Before each irrigation run"},help:{"before-run":"Durations are calculated when each irrigation schedule plans its run, so a run is sized from weather data minutes old instead of hours old."}},"run-history-logging":{header:"Run history logging",description:"When on, a scheduled run that skips a zone because it currently has no water demand is recorded in that zone's history. Off by default; existing history is unaffected.",labels:{"log-no-demand":'Log "no demand" skips in the run history'}},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Warning: weather data update time on or after calculation time"},header:"Automatic weather data update",description:"Collect and store weather data automatically. Weather data is required to calculate zone buckets and durations.",labels:{"auto-update-enabled":"Automatically update weather data","auto-update-schedule":"Update schedule","auto-update-time":"Update at","auto-update-interval":"Update sensor data every","auto-update-delay":"Update delay"},options:{minutes:"minutes",hours:"hours",days:"days"}},"automatic-clear":{header:"Automatic weather data pruning",description:"Automatically remove collected weather data at a configured time. Use this to make sure that there is no left over weather data from previous days. Don't remove the weather data before you calculate and only use this option if you expect the automatic update to collect weather data after you calculated for the day. Ideally, you want to prune as late in the day as possible.",labels:{"automatic-clear-enabled":"Automatically clear collected weather data","automatic-clear-time":"Clear weather data at"}},continuousupdates:{header:"Continuous updates for sensors (experimental)",description:"This experimental feature will continuously update the sensor data. This is useful for sensor groups that use sources that provide continuous data, such as weather stations. This feature cannot be used for sensor groups that at least partly rely on weather services as continous polling of APIs will incur costs. Keep in mind that this is experimental and may not work as expected. Use at your own risk.",labels:{continuousupdates:"Enable continuous updates",sensor_debounce:"Sensor debounce"}}},description:"This page provides global settings.",title:"General",sections:{weather:"Weather",automation:"Automation",location:"Location",watering:"Watering behavior"}},schedules:{title:"Schedules",description:"Create recurring schedules to automatically irrigate your zones at specific times. No automations needed.",add:"Add Schedule",no_items:"No schedules configured yet. Click 'Add Schedule' to get started.",zones_all:"All zones",zones_specific:"Specific zones",hours:"hours",minutes:"min",types:{daily:"Daily",weekly:"Weekly",monthly:"Monthly",interval:"Every N hours"},actions:{calculate:"Calculate (update irrigation duration)",update:"Update (collect weather data)",irrigate:"Irrigate (run valves directly)"},days:{monday:"Mon",tuesday:"Tue",wednesday:"Wed",thursday:"Thu",friday:"Fri",saturday:"Sat",sunday:"Sun"},fields:{name:"Name",recurrence:"Recurrence",enabled:"Enabled",days_of_week:"Days of week",day_of_month:"Day of month",interval_hours:"Interval",action:"Action",zones:"Zones",start_mode:"Start",start_time:"Start time (optional)",finish_mode:"Finish",finish_time:"Finish time (HH:MM)",anchor:"Pinned to",offset_by:"offset by"},dialog:{add_title:"Add Schedule",edit_title:"Edit Schedule"},sections:{when:"When",zones:"Zones",season:"Season"},season:{label:"Date range",to:"to",note:"Leave both blank to run all year."},summary:{invalid:"This schedule has no start or finish set, so it never runs.",recurrence_daily:"Runs daily",recurrence_weekly:"Runs weekly on {days}",recurrence_monthly:"Runs monthly on day {day}",recurrence_interval:"Runs every {hours} hours",recurrence_interval_at:"Runs every {hours} hours, starting at {time}",zones_all:"all zones",zones_some:"{count, plural, one {# selected zone} other {# selected zones}}",watering:"watering {zones}",start_only:"starting at {when}; every zone runs to completion",finish_only:"finishing at {when}; every zone runs to completion",anchor_finish:"finishing at {finish}, starting as late as possible but never before {start}; zones that don't fit wait for the next run",anchor_start:"starting at {start}, finishing by {finish} at the latest; zones that don't fit wait for the next run",sunrise:"sunrise",sunset:"sunset",offset_before:"{minutes} min before {event}",offset_after:"{minutes} min after {event}",at_azimuth:"solar azimuth {degrees}°"},bound_mode:{none:"No limit",time:"At a time",sunrise:"At sunrise",sunset:"At sunset",solar_azimuth:"At solar azimuth"},anchor:{start:"As early as possible within the window",finish:"As late as possible within the window"},help:{error:"Must set either a start or finish condition",demand_open:"Set by demand. All zones run to completion.",exact:"Exact.",demand_floored:"Set by demand, but never before this.",exact_deferred:"Exact. Zones that don't fit are deferred.",demand_capped_deferred:"Set by demand, but never later than this. Zones that don't fit are deferred.",unreachable_no_run:"The sun never reaches this bearing here, so this schedule will not run.",unreachable_ignored:"The sun never reaches this bearing here, so this limit is ignored."},dial:{aria_label:"Run window on a 24 hour dial",sunrise:"Sunrise {time}",sunset:"Sunset {time}",run:"Run {from} to {to}",collision:"Collides with the previous run, {from} to {to}: zones still watering are skipped",window_label:"window",run_label:"run",per_day:"{count}x per day",every_hours:"every {hours}h"}},setup:{title:"Setup",tabs:{weather_location:"Weather & Location",my_zones:"My Zones",when_to_water:"When to Water",advanced:"Advanced",experimental:"Experimental",distributors:"Distributors"},weather_data:{forecast_title:"Forecast",forecast_none:"Forecast is available when a weather service is enabled.",seasonal_title:"Seasonal outlook"},advanced:{used_by_zones:"Used by {count, plural, one {# zone} other {# zones}}",not_used:"Not used"}},experimental:{title:"Experimental features",warning:"These features are opt-in and still being refined. They change how each zone's bucket is filled, so turn them on one at a time and keep an eye on your zones — you can switch them back off at any time.",forecast_weighting:{title:"Forecast-weighted durations",description:"Instead of skipping a whole run when rain is forecast, water less. The upcoming precipitation (over the look-ahead window set under When to Water) is subtracted from the deficit used to compute the run duration, while the true deficit stays in the bucket so the real rain fills the rest. If the forecast rain misses, the next run makes up the difference. Requires a weather service.",label:"Reduce durations when rain is forecast",note:"Uses the precipitation look-ahead from When to Water. Works alongside the rain-skip guard (a skip still wins over a reduced run)."},observed_watering:{title:"Credit bucket from observed watering",description:"When a zone's linked valve runs outside Smart Irrigation — a manual tap, an automation, your own schedule — its bucket is credited for the water applied, estimated from the run time and the zone's throughput. This keeps the soil-moisture model honest when you water by other means. Smart Irrigation's own runs are already accounted for and are never double-counted.",label:"Credit the bucket when a linked valve runs externally",note:"Requires a linked valve and a throughput on the zone. Volume is estimated (run time × throughput), not metered."},live_estimate:{title:"Live-estimate watering",description:"By default a zone waters once a day, from the deficit the daily calculation produced (for example at 23:00). With this on, each scheduled run instead decides — and sizes itself — from the live intra-day deficit (the drainage-aware ET and rainfall since the last calculation). This lets a zone water more than once a day on real intra-day demand (for example pots on an every-12-hours schedule that the once-daily bucket would otherwise leave dry), and it shrinks or cancels a run that intra-day rain has already covered. The daily ledger is unchanged: after the run the bucket is credited with the water actually delivered, so the next daily calculation never double-counts. Requires a weather service.",label:"Trigger and size each run from the live deficit",note:"Affects scheduled runs only, and can start a run the daily calculation didn't approve. For frequent watering keep a sensible minimum deficit and a maximum bucket of at least a day's ET."},continuous_updates:{title:"Continuous sensor updates",description:"By default, sensor-based weather values are read once per scheduled update (hourly by default), so anything that happened in between is never recorded — the daily minimum and maximum temperature come from those spot readings, and solar radiation is integrated coarsely. With this on, a reading is recorded the moment the sensor changes, which makes the daily aggregates and the resulting evapotranspiration considerably more accurate. Sensor groups that also use a weather service keep their scheduled update for the weather-service values; only the sensor values become continuous. Small changes are ignored, so a noisy sensor does not fill the buffer.",label:"Record sensor readings when they change",debounce_label:"Group changes arriving within (milliseconds)",note:"Applies to sensor groups whose values come from Home Assistant sensors. The grouping delay only postpones the follow-up bookkeeping — no reading is ever dropped by it. Set it to 0 to disable grouping."},hourly_calculation:{title:"Hourly evapotranspiration",description:"By default the FAO-56 equation is run once, over the window's average weather, which cloud cover biases systematically: fed one identical hourly series across 362 days it returns 1.14 times the reference on overcast days and 0.93 times on clear ones. With this on, the equation is run for each hour and the hours are summed, which removes that bias, and the water balance is replayed hour by hour so rain and drainage are booked when they happened instead of all at the start of the window. Expect the daily figure to move by up to 12 percent, in either direction depending on the sky. Needs a Solar Radiation source that is measured rather than estimated, and it is not used on days where a forecast is blended in.",label:"Sum evapotranspiration hour by hour",note:"Independent of continuous sensor updates: scheduled hourly updates carry this too, and a denser buffer makes it more accurate without being required. Any window that cannot be reduced to hourly rows keeps the daily equation, so no series is ever invented."},distributors:{title:"Mechanical water distributors",description:"Drive a mechanical pressure-distributor — for example a Gardena Water Distributor — that splits one supply into several outlets and advances on water on/off pulses. Assign zones to a distributor's outlets and Smart Irrigation waters them in sequence, tracks the position, and coordinates a master valve or pump. This is a new feature that could not be fully hardware-tested, so treat it as a beta.",label:"Enable mechanical water distributors",note:"Watch the first days of use closely and keep the device's manual override handy. You can switch it back off at any time — existing zone watering is unaffected."}},help:{title:"Help",cards:{"how-to-get-help":{title:"How to get help","first-read-the":"First, read the",wiki:"Documentation","if-you-still-need-help":"If you still need help reach out on the","community-forum":"Community forum","or-open-a":"or open a","github-issue":"Github Issue","english-only":"English only"}}},info:{title:"Info",description:"View information about next irrigation and system status.","configuration-not-available":"Configuration not available.",cards:{"zone-bucket-values":{title:"Zone Bucket Values & Duration",labels:{bucket:"Bucket",duration:"Duration"},"no-zones":"No zones configured"},"next-irrigation":{title:"Next Irrigation",labels:{"next-start":"Next start",duration:"Duration",zones:"Zones"},"no-data":"No data available"},"irrigation-reason":{title:"Irrigation Reason",labels:{reason:"Reason",sunrise:"Sunrise","total-duration":"Total duration",explanation:"Explanation"},"no-data":"No data available"},irrigate_now:{title:"Irrigate Now",description:"Immediately start irrigation for all zones that have a linked entity. Skip conditions are ignored.",button_all:"Run all zones now",no_linked_zones:"No zones have a linked switch/valve entity with a calculated duration."}}},mappings:{cards:{"add-mapping":{actions:{add:"Add sensor group"},header:"Add sensor groups"},mapping:{aggregates:{average:"Average",first:"First",last:"Last",maximum:"Maximum",median:"Median",minimum:"Minimum",riemannsum:"Riemann sum",sum:"Sum",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"You cannot delete this sensor group because there is at least one zone using it.",invalid_source:"Invalid source",source_does_not_exist:"Source does not exist. Please enter a valid source, such as 'sensor.mysensor'."},items:{dewpoint:"Dewpoint",evapotranspiration:"Evapotranspiration",humidity:"Humidity","maximum temperature":"Maximum temperature","minimum temperature":"Minimum temperature",precipitation:"Total precipitation","current precipitation":"Current precipitation",pressure:"Pressure","solar radiation":"Solar radiation",temperature:"Temperature",windspeed:"Wind speed"},pressure_types:{absolute:"absolute",relative:"relative"},"pressure-type":"Pressure is","sensor-aggregate-of-sensor-values-to-calculate":"of sensor values to calculate duration","sensor-aggregate-use-the":"Use the","sensor-entity":"Sensor entity",static_value:"Value","input-units":"Input provides values in",source:"Source",sources:{none:"None",weather_service:"Weather service",sensor:"Sensor",static:"Static value"}}},description:"Add one or more sensor groups that retrieve weather data from Weather service, from sensors or a combination of these. You can map each sensor group to one or more zones",labels:{"mapping-name":"Name"},no_items:"There are no sensor group defined yet.",title:"Sensor Groups","weather-records":{title:"Weather Records",timestamp:"Time",temperature:"Temp",humidity:"Hum",dewpoint:"Dew",wind:"Wind",pressure:"Press",precipitation:"Precip","retrieval-time":"Retrieved","no-data":"No weather data available for this sensor group"}},modules:{cards:{"add-module":{actions:{add:"Add module"},header:"Add module"},module:{errors:{"cannot-delete-module-because-zones-use-it":"You cannot delete this module because there is at least one zone using it."},labels:{configuration:"Configuration",required:"indicates a required field"},"translated-options":{DontEstimate:"Do not estimate",EstimateFromSunHours:"Estimate from sun hours",EstimateFromTemp:"Estimate from temperature",EstimateFromSunHoursAndTemperature:"Estimate from average of sun hours and temperature"},fields:{coastal:{name:"Coastal",description:"Enable if the weather station is located near a coast or large body of water. Affects how atmospheric humidity is estimated."},solrad_behavior:{name:"Solar radiation estimation",description:"How solar radiation is estimated when it is not directly measured by a sensor."},forecast_days:{name:"Forecast days",description:"Number of future days to include in the ET calculation. 0 = current weather only (recommended — no extra API calls). Values > 0 average today's ET with forecasted ET for upcoming days (up to 4 days via the OWM free tier)."},delta:{name:"Delta",description:"Static evapotranspiration delta (mm) used directly without any weather-based calculation."}}}},description:"Add one or more modules that calculate irrigation duration. Each module comes with its own configuration and can be used to calculate duration for one or more zones.",no_items:"There are no modules defined yet.",title:"Modules"},zones:{actions:{add:"Add",calculate:"Calculate",information:"Information",update:"Update","reset-bucket":"Reset bucket","view-weather-info":"View weather data","view-weather-info-message":"Weather data available for","view-watering-calendar":"View watering calendar",irrigate_all:"Water all zones now",open_settings:"Edit settings"},cards:{"add-zone":{actions:{add:"Add zone"},header:"Add zone"},"zone-actions":{actions:{"calculate-all":"Recalculate durations","update-all":"Refresh weather data","reset-all-buckets":"Reset all buckets","clear-all-weatherdata":"Clear all weather data"},header:"Actions on all zones"}},description:"Specify one or more irrigation zones here. The irrigation duration is calculated per zone, depending on size, throughput, state, module and sensor group.",labels:{bucket:"Bucket",duration:"Duration","lead-time":"Lead time",mapping:"Sensor Group","maximum-duration":"Maximum duration",multiplier:"Multiplier",name:"Name",size:"Size",state:"State",states:{automatic:"Automatic",disabled:"Disabled",manual:"Manual"},throughput:"Throughput","maximum-bucket":"Maximum bucket",last_calculated:"Last calculated","data-last-updated":"Data last updated","data-number-of-data-points":"Number of data points",drainage_rate:"Drainage rate",linked_entity:"Linked switch/valve/helper entity",opensprinkler_station:"OpenSprinkler station",opensprinkler_station_help:"The station's enabled switch, e.g. switch.front_lawn_station_enabled. HASI queues the run on the controller and then watches that station's own running sensor, so a zone queued behind others is only counted as watering once it really starts. Set the controller's water level to 100% or turn its weather adjustment off, otherwise the weather correction is applied twice.",opensprinkler_no_stations:"No OpenSprinkler stations found. Check that the OpenSprinkler integration is set up and the controller is reachable. You can still type an entity id.",linked_entity_placeholder:"e.g. switch.garden_valve",flow_sensor:"Flow meter sensor (optional)",flow_sensor_placeholder:"e.g. sensor.zone_flow_rate",flow_counter_type:"Counter type",flow_counter_type_help:"How this cumulative flow sensor is read. Auto learns across runs whether the sensor resets each run. Per run: the sensor resets to ~0 each run and shows that run's total (e.g. Sonoff/Zigbee valves). Lifetime: a meter that only ever counts up across all runs (delta per run).",flow_counter_type_auto:"Auto (learn)",flow_counter_type_per_run:"Per run (resets each run)",flow_counter_type_lifetime:"Lifetime total (delta)",watering_mode:"Watering mode",watering_mode_description:"How HASI actuates this zone. Classic: HASI opens the valve and closes it itself with a software timer. Self-closing service: HASI sends the run duration to a self-closing valve via a script (see the shipped valve blueprints) and lets the hardware close itself, so an HA restart mid-run cannot cause continuous irrigation.",watering_modes:{classic:"Classic (HASI opens & closes the valve)",service:"Self-closing service (valve closes itself)",opensprinkler:"OpenSprinkler station (controller runs the queue)"},run_service:"Run service",run_service_help:"Service HASI calls to start the run (e.g. a script.* or a switch/valve service). It receives the duration field below plus zone_id and zone_name.",duration_field:"Duration field",duration_field_placeholder:"e.g. dauer",duration_field_help:"Name of the parameter that carries the run length in the call to your run service. The shipped valve blueprints use 'duration' (the default); a custom script may use another name (e.g. 'dauer').",duration_unit:"Duration unit",duration_units:{seconds:"Seconds",minutes:"Minutes"},duration_unit_help:"Unit your hardware expects for the run length. Check the device: many Zigbee/Tuya valves count in MINUTES. The wrong unit over- or under-waters by 60x. In Minutes mode HASI rounds up to whole minutes (minimum 1).",stop_service:"Stop service (optional)",stop_service_help:"Optional. Service HASI calls to close the valve when you stop the zone early, before its own timer expires. Leave empty if the valve cannot be stopped manually.",confirm_entity:"Confirm entity (optional)",confirm_entity_help:"Optional. The real valve/switch entity the run service drives (e.g. a valve or switch) — it holds a steady on-state while watering. If set, HASI verifies the open against it (poll only, it never re-actuates) and flags a problem plus skips the bucket credit if it never turns on. Leave empty to treat the run as write-only and credit optimistically (the hardware owns the close). When in doubt, leave it empty: it only helps with an entity that reports its on-state reliably — a valve that reports late (e.g. a sleepy Zigbee valve) could be read as 'off' and wrongly skip the credit, so the zone would water again next run. Do NOT point this at the run script itself — a fire-and-forget script is not a valid state signal.",observed_entity:"Observed valve/switch (optional)",observed_entity_help:"If Observed watering is on, external runs of this valve/switch (a manual tap, an automation) credit this zone's water storage. Leave empty to not observe this zone.",soil_moisture_sensor:"Soil-moisture sensor (optional)",soil_moisture_sensor_help:"Optional. A sensor reporting this zone's soil moisture in percent (higher = wetter). With a skip threshold set below, an automatic run skips this zone whenever the reading is above the threshold and resets the zone's bucket. Leave empty to disable. An unavailable or non-numeric reading never blocks watering (fail-open).",soil_moisture_threshold:"Skip above soil moisture (%)",soil_moisture_threshold_help:"On an automatic run, skip this zone (and reset its bucket to 0) when the soil-moisture sensor reads strictly above this percentage. Needs a soil-moisture sensor set above. Only affects scheduled runs; manual runs always water.",irrigate_now:"Irrigate Now",bucket_threshold:"Minimum deficit to irrigate",plant_type:"Plant type",kc:"Crop coefficient (Kc)",plant_types:{custom:"Custom (set Kc manually)",lawn:"Lawn / turf",vegetables:"Vegetable garden",flowers:"Flower bed",shrubs:"Shrubs",trees:"Trees",xeriscape:"Xeriscape / drought-tolerant"},soil_type:"Soil type",soil_types:{custom:"Custom (set rate manually)",sand:"Sandy (fast draining)",loam:"Loam (balanced)",silt:"Silt (slow draining)",clay:"Clay (very slow draining)"},distributor:"Water distributor",distributor_help:"Assign this zone to an outlet of a mechanical water distributor. The distributor's inlet valve and its pulse-advance sequence then water this zone, so the zone's own valve and schedule below are managed by the distributor.",distributor_none:"None (own valve)",outlet_number:"Outlet number",distributor_managed_note:"This zone is watered through a distributor (outlet above). Its valve, inlet control and flow sensor are managed by the distributor and hidden here — only the calculation and soil-moisture veto settings remain. To give the zone its own valve again, set the distributor above to “None (own valve)”.",outlet_number_readonly_help:"Which outlet of the distributor feeds this zone. Set on the distributor page — open it with the button.",configure_on_distributor:"Configure on distributor"},no_items:"There are no zones defined yet.",title:"Zones",status:{decision_disabled:"Turned off — this zone won't be watered automatically.",decision_water:"Watering needed: about {duration} on the next scheduled run.",decision_water_at:"Will water about {duration} at {time}.",decision_water_skip:"Deficit ~{duration}, but the next run will likely be skipped ({reason}).",decision_water_no_schedule:"Deficit ~{duration} — no schedule waters this zone; trigger it manually.",decision_no_water:"No watering needed right now — the soil has enough moisture.",decision_unknown:"Not calculated yet — press Update, then Calculate to check.",last_checked:"Last checked",never:"never",saved:"Saved",estimate_now:"Now",estimate_tag:"est.",estimate_method:{hourly:"Live estimate from hourly weather since the last calculation",hourly_sensor:"Live estimate from hourly sensor readings since the last calculation",proxy:"Estimate distributed from today's forecast since the last calculation"}},fault:{title:"Last run failed",valve_no_response:"The valve didn't respond — no water was delivered, so the bucket was left unchanged.",flow_never_started:"No flow was detected — no water was delivered, so the bucket was left unchanged.",station_never_ran:"The OpenSprinkler controller never ran the station — no water was delivered, so the bucket was left unchanged.",station_unresolved:"The OpenSprinkler station could not be found — the run was not started, so the bucket was left unchanged.",station_wrong_mode:"An OpenSprinkler station is linked, but the zone's watering mode is not OpenSprinkler station — the run was refused, so the bucket was left unchanged.",generic:"The last irrigation run failed."},skip:{title:"Skipped",soil_moisture:"Soil moisture {observed} % > {threshold} %"},clamped:{title:"Duration capped",detail:"This zone needs longer than its maximum duration of {maximum}, so part of the deficit is left unwatered on every run. Deepening the bucket threshold has no effect until the cap is raised."},help:{bucket:"Soil-moisture balance. A negative value means the soil is dry and the zone needs water.",calculate:"Works out how long to water from the latest data. Run this after Update.",update:"Fetches the latest weather/sensor data for this zone.",irrigate_link_entity:"Link a switch/valve in this zone's settings to enable manual watering.",irrigate_all:"Opens the linked valves now for every zone with a deficit. Skip conditions (rain, wind, temperature) are ignored.",update_all:"Collects the latest weather/sensor data for all zones. Does not change durations on its own.",calculate_all:"Recomputes each automatic zone's watering duration from the data collected so far."},outlook:{next_run:"Next run",estimated:"estimated",estimated_help:"The start time is still a projection: the run is sized from the water demand read shortly before it begins, so this time moves until then.",no_schedule:"No automatic schedule — zones water only when you trigger them.",setup_schedule:"Set up a schedule",targets_all:"all zones",targets_zones:"{count} zones",will_skip:"Next run will likely be skipped",will_run:"Conditions look clear for the next run.",why_skipped:"Why?",provisional:"forecast — may change",active_guards:"Active guards",last_run:"Last run",last_run_skipped:"skipped",last_run_ran:"ran",today:"today",tomorrow:"tomorrow",actions:{irrigate:"Water",calculate:"Recalculate",update:"Refresh data"},checks:{precipitation:"Rain forecast",days_between:"Days between watering",temperature:"Low temperature",wind:"High wind",rain_sensor:"Rain sensor",freeze:"Frost",paused:"Paused (rain delay)",soil_moisture:"Soil moisture",no_demand:"No water demand"},check_detail:{precipitation:"{observed} mm (≥ {threshold} mm)",days_between:"{observed}/{threshold} days",temperature:"{observed}° (below {threshold}°)",wind:"{observed} (above {threshold})",rain_sensor:"{observed}",freeze:"{observed}° (below {threshold}°)"}},calendar:{no_data:"No watering calendar data available for this zone.",error_prefix:"Error generating calendar:",month:"Month",et:"ET (mm)",precipitation:"Precipitation (mm)",watering:"Watering (L)",avg_temp:"Avg Temp (°C)",method_prefix:"Method:"},confirm_action:{reset_bucket_title:"Reset this zone's bucket?",reset_bucket_body:"This sets the bucket back to 0, discarding the accumulated moisture balance for this zone.",reset_all_buckets_title:"Reset all buckets?",reset_all_buckets_body:"This sets every zone's bucket back to 0, discarding the accumulated moisture balance. Watering calculations start fresh from the next update.",clear_weather_title:"Clear all weather data?",clear_weather_body:"This deletes all collected weather and sensor records for every zone. Zones will need fresh data before they can calculate again."},confirm_irrigate:{title:"Start irrigation?",body:"This opens the linked valve(s) now and bypasses all skip conditions (rain, temperature, minimum days between watering).",all_linked_zones:"All linked zones",toast_started:"Irrigation started",toast_failed:"Irrigation failed"},history:{title:"Run history",total_used:"Total water used",empty:"No runs recorded yet.",when:"When",result:"Result",volume:"Volume",detail:"Detail",results:{completed:"Completed",partial:"Partial",failed:"Failed",skipped:"Skipped",observed:"Observed"}},rain_delay:{title:"Pause watering",paused:"Paused",until:"until",delay_24h:"Delay 24 h",delay_48h:"Delay 48 h",resume:"Resume"},run_zone:{run:"Run",minutes:"min",help:"Water this zone for a custom time, ignoring the calculation",toast_started:"Started run",busy_hint:"Distributor is running — you can start again once it is back in its home position."},stop_zone:{stop:"Stop",watering:"Watering…",toast_stopped:"Stopped run"}},distributors:{title:"Distributors",description:"Mechanical water distributors split one supply into several outlets, advanced by pulsing the water on and off.",no_items:"No distributors configured yet.",add:{header:"Add distributor",name_placeholder:"Distributor name",actions:{add:"Add"}},status:{saved:"Saved"},confirm_delete:"Delete this distributor? Zones assigned to it keep their outlet numbers but lose their distributor link.",labels:{name:"Name",watering_mode_help:"How the distributor's inlet valve is opened and closed.",inlet_entity:"Inlet valve / switch (optional)",inlet_entity_help:"The switch or valve entity that opens the water supply into the distributor. It is also watched for foreign pulses; once a valve is selected, a setting appears below to control the reaction.",watch_inlet:"Watch inlet valve for manual pulses",watch_inlet_help:"Only detects valve switches Home Assistant can see — purely mechanical pulses at the device stay invisible.",inlet_entity_help_service:"The ring valve Home Assistant watches for foreign pulses to keep the outlet position in sync (e.g. when the valve is opened manually or by an automation outside a HASI run). Once a valve is selected, a setting appears below to control the reaction. Actuation is via the run/stop service; this field is only read, and is NOT the flow/confirm sensor. Leave empty to disable inlet watching.",watch_mode:"On a manual inlet pulse",watch_mode_help:"How to react when the inlet valve is opened outside a Home Assistant run (only pulses Home Assistant can see).",watch_mode_count:"Count it (advance the position)",watch_mode_warn:"Warn (mark position uncertain)",watch_mode_ignore:"Ignore",run_service:"Run script",run_service_help:"Script called to open the inlet. It receives the pulse duration.",stop_service:"Stop script (optional)",stop_service_help:"Script called to close the inlet.",duration_field:"Duration field",duration_field_help:"Name of the field the run script expects the duration in.",duration_field_placeholder:"duration",duration_unit:"Duration unit",duration_units:{seconds:"Seconds",minutes:"Minutes"},confirm_entity:"Confirmation sensor (optional)",confirm_entity_help:"Optional sensor on the distributor inlet confirming water actually flows (e.g. a flow or valve-position sensor). If it reports no flow when an outlet opens, the cycle halts safely and marks the distributor uncertain — this is the low-flow / fault detection.",flow_sensor:"Flow sensor (optional)",flow_sensor_help:"The shared inlet flow-rate meter (e.g. L/min, m³/h). When set, the actual delivered volume per outlet is measured and credited instead of the time estimate. Optional. Where the valve can be stopped (a classic inlet, or a self-closing stop-service), the outlet also stops early once its target volume is reached. Both an instantaneous rate meter (e.g. L/min) and a cumulative totalizer counter (e.g. m³, or state_class: total_increasing) are supported and detected automatically from the unit.",pause_seconds:"Advance pause",skip_pulse_seconds:"Skip pulse",notify_target:"Notification target (optional)",notify_target_help:"Optional additional channel. Halts always appear in the Home Assistant notifications panel; set a notify service here (e.g. notify.mobile_app_phone) to also push them there.",notify_target_placeholder:"notify.mobile_app_phone"},notify:{halted:"Distributor '{name}' halted ({reason}). Re-sync and re-confirm required.",reason:{valve_did_not_open:"valve did not open",restart_mid_advance:"restarted mid-advance",foreign_inlet_pulse:"manual inlet pulse"}},commissioning:{title:"Commissioning",outlet:"Outlet",states:{synced:"Synced",uncertain:"Uncertain"},test_run:"Test run",test_run_help:"Waters each mapped outlet for about 30 seconds in order, so you can watch the device advance and note the pause it needs.",set_outlet:"Set current outlet",set_outlet_help:"Read the outlet number shown in the device window and set it here to re-sync the tracked position.",resync_home:"Reset to outlet 1",confirm_resync:{title:"Reset to outlet 1?",body:"This sets the tracked position to outlet 1. Only confirm if the device is physically at outlet 1 — otherwise the distributor will water the wrong outlets (an undetected desync)."},confirm_set_outlet:{title:"Set current outlet?",body:"This marks the distributor as synced at the outlet you entered. Only confirm if the device's window physically shows that outlet right now — a wrong value silently waters the wrong outlets."},confirmed:"Commissioning confirmed",confirmed_help:"Arms the distributor for automatic and manual cycles. Can only be set while the position is synced, and drops to off automatically if the position ever becomes uncertain.",needs_sync:"Set the position to synced before you can arm this distributor.",run_now:"Run now",run_now_help:"Runs one full manual cycle over all mapped outlets.",run_now_active:"A cycle is already running.",confirm_dialog:{title:"Arm this distributor?",body:"Confirm the device is physically at outlet 1 and every outlet is mapped to the right zone. Automatic and manual cycles will start pulsing the inlet.",confirm:"Confirm & arm"}},hints:{pressure:"Give the distributor at least 1 bar of water pressure and 20 l/h of flow. Mechanical distributors need a firm pulse to advance reliably.",below_floor_pause:"Very short pause. The advance pulse must be long enough for the distributor to actually step; the backend enforces a minimum of 10 seconds.",below_floor_skip:"Very short skip pulse. The backend enforces a minimum of 10 seconds.",undetectable:"The device's manual selector button cannot be read back. If you turn it by hand, use “Set current outlet” afterwards so the tracked position matches.",outlet_change:"Changing an outlet mapping moves the device off its known position. Re-sync and re-confirm commissioning before the next cycle.",parallel_draw:"Parallel sequencing opens several zones at once, but a distributor feeds one outlet at a time, so its mapped zones still water in sequence. Plan the supply draw accordingly.",master_off_after:"With sequential or rotating sequencing and “master off after each zone”, the pump is switched per outlet, so expect it to cycle between every outlet of the distributor.",experimental:"Experimental feature — still being refined and not fully hardware-tested. Watch the first days of use closely and keep the device's manual override within reach."},outlets:{title:"Outlets / zones",help:"Set how many outlets the distributor has, then assign a zone to each. Only zones without their own valve or script can be assigned — a zone is either on a distributor or has its own valve. The number of outlets equals the number of assigned zones, numbered contiguously from 1.",count:"Number of outlets",none:"— none",no_zones:"No zones yet. Create zones first (Setup → Zones), then assign them here.",gap_warning:"Outlets must be filled contiguously from 1 — assign a zone to every outlet up to the highest used one."}}},di="Smart Irrigation",ci={title:"Weather Service",description:"Configure which weather service to use for ET calculations and skip conditions.",enabled_label:"Enable weather service",service_label:"Weather service",api_key_label:"API key",api_key_placeholder:"Leave blank to keep existing key",api_key_configured:"API key is configured",api_key_not_configured:"No API key configured",api_key_help:"An API key from your chosen weather service provider. Open-Meteo does not require a key. OpenWeatherMap, Pirate Weather and the Met Office (Weather DataHub) all offer free tiers.",no_api_key_needed:"Open-Meteo is a free service and requires no API key.",save_button:"Save weather settings",saved:"Weather settings saved",owm:"OpenWeatherMap",pw:"Pirate Weather",openmeteo:"Open-Meteo (free, no key needed)",met:"Met Office (UK)",test_button:"Test Connection",test_button_testing:"Testing…",test_success:"✓ Connection successful",test_error_invalid_auth:"✗ Invalid API key — check that it is correct and active",test_error_cannot_connect:"✗ Cannot connect — check your internet connection",test_error_no_service:"✗ Select a weather service first",test_error_unknown:"✗ Test failed — unknown error"},hi={title:"Irrigation Start Triggers",description:"Configure when irrigation should start based on solar events. You can add multiple triggers for different schedules. For sunrise triggers, leaving offset at 0 will automatically use the total duration of all enabled zones.",add_trigger:"Add Trigger",edit_trigger:"Edit Trigger",delete_trigger:"Delete Trigger",trigger_types:{sunrise:"Sunrise",sunset:"Sunset",solar_azimuth:"Solar Azimuth"},fields:{name:{name:"Trigger Name",description:"A descriptive name to identify this trigger"},type:{name:"Trigger Type",description:"The type of solar event to trigger on"},enabled:{name:"Enabled",description:"Whether this trigger is currently active"},offset_minutes:{name:"Offset (minutes)",description:"Minutes before (-) or after (+) the solar event. For sunrise triggers, use 0 for automatic timing based on total zone duration."},azimuth_angle:{name:"Azimuth Angle (degrees)",description:"Solar azimuth angle in degrees where 0=North, 90=East, 180=South, 270=West"},account_for_duration:{name:"Account for Duration",description:"When enabled, irrigation will start early enough to finish at the specified time. When disabled, irrigation will start exactly at the specified time."}},dialog:{add_title:"Add Irrigation Start Trigger",edit_title:"Edit Irrigation Start Trigger",cancel:"Cancel",save:"Save",delete:"Delete"},no_triggers:"No irrigation start triggers configured. The system will use the default behavior (sunrise with total zone duration). Add triggers to customize when irrigation starts.",offset_auto:"Auto (calculated from total zone duration)",confirm_delete:"Are you sure you want to delete the trigger '{name}'?",validation:{name_required:"Trigger name is required",azimuth_invalid:"Azimuth angle must be a valid number"},help:{sunrise_offset:"For sunrise triggers: Use negative values to start before sunrise, positive to start after. Set to 0 to automatically start early enough to complete all zones before sunrise.",sunset_offset:"For sunset triggers: Use negative values to start before sunset, positive to start after sunset.",azimuth_explanation:"Solar azimuth is the compass direction of the sun. 0°=North, 90°=East, 180°=South, 270°=West. You can enter any angle value (e.g., 450° = 90°, -30° = 330°). Use this to trigger irrigation when the sun reaches a specific position.",multiple_triggers:"You can configure multiple triggers. Each enabled trigger will independently schedule irrigation starts."}},ui={title:"Skip Conditions",description:"Automatically skip irrigation when conditions are unfavorable. Precipitation check requires a weather service. Temperature and wind checks also require a weather service.",threshold_label:"Precipitation Threshold",threshold_description:"Minimum total precipitation (in mm) forecast across the look-ahead window to skip irrigation.",lookahead_label:"Forecast look-ahead (days)",lookahead_help:"How many upcoming forecast days to add up when checking for rain. The forecast starts at tomorrow (today is excluded), so 1 = just the next day, 2 = the next two days, and so on.",temp_section_title:"Skip on low temperature",temp_threshold_label:"Skip if temperature is below",wind_section_title:"Skip on high wind speed",wind_threshold_label:"Skip if wind speed is above",rain_sensor_section_title:"Skip on rain sensor",rain_sensor_label:"Rain sensor entity (optional)",rain_sensor_placeholder:"e.g. binary_sensor.rain",freeze_section_title:"Skip on frost",freeze_threshold_label:"Skip if minimum temperature is below",freeze_help:"Compares the current temperature and the coming night's forecast low; skips watering when frost is expected, to protect pipes and plants.",forecast_rain_label:"When rain is forecast",forecast_rain_options:{ignore:"Ignore it",water_less:"Water less",skip:"Skip watering"},forecast_rain_help:{ignore:"Forecast rain is ignored; runs use the calculated duration.",water_less:"Upcoming forecast rain trims the run duration (the deficit stays in the bucket for the real rain to fill).",skip:"Skip the run entirely when enough rain is forecast within the look-ahead window."}},pi={title:"Location Coordinates",description:"Configure location coordinates for weather data retrieval. You can use manual coordinates different from your Home Assistant location if needed.",manual_enabled:"Use manual coordinates",use_ha_location:"Use Home Assistant location",latitude:"Latitude (decimal degrees)",longitude:"Longitude (decimal degrees)",elevation:"Elevation (meters above sea level)",current_ha_coords:"Current Home Assistant coordinates"},gi={title:"Days Between Irrigation",description:"Configure the minimum number of days that must pass between irrigation events. This helps control watering frequency for water conservation and plant health management.\n\nTypical real-world use cases:\n• Lawn care: 1-2 day intervals prevent overwatering\n• Drought restrictions: 6+ day intervals for weekly watering\n• Deep-rooted plants: 3-7 day intervals for less frequent watering\n• Water conservation: Customizable based on climate and soil conditions",label:"Minimum days between irrigation",help_text:"Set to 0 to disable this feature. Values from 1-365 days are supported. This setting works alongside existing precipitation forecasting logic."},mi={title:"Zone Sequencing",description:"When multiple zones need irrigation, choose whether they run at the same time or one after another. Sequential mode waits for each zone to finish before starting the next. Rotating mode cycles through zones, giving each one a limited consecutive run before moving to the next.",parallel:"Parallel (all zones at once)",sequential:"Sequential (one zone at a time)",rotating:"Rotating (zones take turns)",max_consecutive_duration_label:"Max consecutive run time per zone",max_consecutive_duration_unit:"minutes",min_absorption_time_label:"Min. absorption time between slots",min_absorption_time_unit:"minutes (0 = disabled)"},vi={title:"Pump / master switch",description:"Optional. Powers a shared master — a pump or main valve — on before the first zone of a watering cycle, then optionally off after the last zone. Leave the entity empty to never touch a master (e.g. a pressure-controlled waterworks that starts on its own).",entity:"Master entity (switch/valve)",kick_enabled:"Kicker: pulse off then on to force a pump start",kick_pause:"Kick pause (off before on)",settle:"Settle delay before the first zone",off_after:"Turn the master off after irrigation",seconds_unit:"seconds"},fi={zone_size:"The total irrigated area of this zone. Used with throughput to calculate how much water is applied per run.",zone_throughput:"Total water flow of your irrigation system for this zone (litres/min in metric, gal/min in imperial). Check your sprinkler datasheet or measure by timing how long it takes to fill a known container.",zone_drainage_rate:"How fast saturated soil drains excess water. ~20 mm/h suits medium/loam soil; lower (2–10) for heavy clay, higher for sandy soil.",zone_bucket:"Current water deficit (negative) or surplus (positive) for this zone. Irrigation triggers when bucket drops below the threshold.",zone_maximum_bucket:"Maximum moisture surplus the zone can hold. Water above this level is treated as runoff. Typical value: 50 mm.",zone_bucket_threshold:"Irrigation triggers when the bucket drops below this value. Must be 0 or negative. 0 means irrigate whenever there is any deficit.",zone_multiplier:"Scale factor applied to the calculated duration. Use above 1.0 to increase, below 1.0 to decrease. Useful for fine-tuning without changing physical measurements.",zone_lead_time:"Extra seconds added before irrigation starts. Use for pump warm-up or system pressurisation.",zone_maximum_duration:"Hard cap on any single irrigation run in seconds. Prevents runaway watering. Default: 3600 s (1 hour).",zone_linked_entity:"The HA switch, valve or input_boolean (helper) entity controlling water flow for this zone. This entity is turned on when irrigation runs.",zone_flow_sensor:"Optional sensor measuring actual water flow rate. Used for reporting only — does not affect duration calculations.",general_autoupdatedelay:"Seconds to wait after HA starts before the first weather data fetch. Allows other integrations to initialise first.",general_sensor_debounce:"Minimum gap in milliseconds between sensor readings to filter noise from rapidly changing sensors.",general_calctime:"Time of day when irrigation durations are recalculated from collected weather data. Format: HH:MM (24-hour).",general_cleardatatime:"Time of day when old weather data is purged. Must be set later than the calculation time.",general_days_between:"Minimum days between irrigation events for the same zone. Set to 0 to disable (irrigate whenever deficit exists).",general_autoupdateinterval:"How often weather data is collected. Choose a value that balances fresh data against API rate limits.",general_precipitation_threshold:"Irrigation is skipped if total forecast precipitation across the look-ahead window exceeds this amount.",general_temp_threshold:"Irrigation is skipped if the current temperature is below this value (e.g. to prevent frost damage).",general_wind_threshold:"Irrigation is skipped if wind speed exceeds this value (high winds reduce efficiency and cause drift).",zone_plant_type:"Pick a plant type to set a typical crop coefficient, or choose Custom to enter Kc yourself.",zone_kc:"Scales reference (grass) ET to this zone's plants. 1.0 = reference grass; lower for drought-tolerant planting, higher for thirsty crops. Only the ET term is scaled — rain is not.",zone_soil_type:"Pick a soil type to set a typical drainage rate, or leave Custom to enter it by hand below.",distributor_pause_seconds:"Off-time between outlets. This is the pulse that advances the distributor to the next outlet; set it from what you saw during the test run. Minimum 10 seconds.",distributor_skip_pulse_seconds:"Short on/off pulse used to step past an outlet that has no zone mapped, without watering it. Minimum 10 seconds."},_i={title:"Setup Wizard",open_button:"Setup Wizard",close:"Close",next:"Next",back:"Back",finish:"Finish",skip_step:"Skip this step",step_indicator:"Step {current} of {total}",stepper:{weather:"Weather",module:"Module",mapping:"Sensor Group",zone:"Zone"},setup_complete_banner:"Setup not complete. Run the wizard to get started.",open_wizard:"Open Wizard",steps:{welcome:{title:"Welcome to Smart Irrigation",intro:"This wizard guides you through the four steps needed to get your first zone irrigating automatically.",step1_label:"Weather Service — where to get weather data",step2_label:"Calculation Module — how irrigation duration is computed",step3_label:"Sensor Group — which data sources to use",step4_label:"Zone — your first irrigation zone",tip:"You can skip any step and configure it later from the Setup tab."},weather:{title:"Weather Service",description:"Choose how to get weather data. Open-Meteo is free and requires no API key — it is the easiest choice for most users."},module:{title:"Calculation Module",description:"A module calculates how long to irrigate based on evapotranspiration (ET). The PyETO module (FAO-56 method) is recommended for most users.",pick_label:"Select module type",no_modules:"No module types available."},mapping:{title:"Sensor Group",description:"A sensor group links each weather variable to a data source. Set the key variables below — you can refine individual sensor mappings later from the Setup → Sensor Groups tab.",name_label:"Sensor group name",source_label:"Data source for",use_weather_service:"Weather service",use_sensor:"Sensor",use_static:"Static value",use_none:"None / not used"},zone:{title:"First Zone",description:"A zone is one irrigation area (e.g. lawn, garden bed). Set the physical properties so the system can calculate the correct irrigation duration.",name_label:"Zone name",size_label:"Area",throughput_label:"Sprinkler throughput",entity_label:"Linked switch, valve or helper",entity_placeholder:"e.g. switch.garden_valve",module_label:"Calculation module",mapping_label:"Sensor group"},done:{title:"Setup Complete!",description:"Your first zone is ready. Smart Irrigation will now calculate irrigation durations automatically based on weather data.",next_steps:"What you can do next:",tip1:"Go to Zones to view calculated durations and bucket values.",tip2:"Add more zones from the Zones tab.",tip3:"Refine all settings from the Setup tab.",go_zones:"Go to Zones",go_setup:"Go to Setup",schedule_name:"Daily",schedule_title:"Create a watering schedule",schedule_desc:"Your system is configured, but it won't water until a schedule exists. Create a daily schedule for all zones now (you can change or remove it later under Setup → When to Water).",schedule_create:"Create daily schedule",schedule_created:"Daily schedule created."}},confirm_close:{body:"Close the setup wizard? Your progress so far is saved.",keep:"Keep editing",close:"Close"}},bi={flow_calibration:ii,common:ai,defaults:ni,module:oi,calcmodules:ri,panels:li,title:di,weather_service_config:ci,irrigation_start_triggers:hi,weather_skip:ui,coordinate_config:pi,days_between_irrigation:gi,zone_sequencing:mi,master:vi,field_help:fi,wizard:_i},yi=Object.freeze({__proto__:null,calcmodules:ri,common:ai,coordinate_config:pi,days_between_irrigation:gi,default:bi,defaults:ni,field_help:fi,flow_calibration:ii,irrigation_start_triggers:hi,master:vi,module:oi,panels:li,title:di,weather_service_config:ci,weather_skip:ui,wizard:_i,zone_sequencing:mi});function wi(e,t){const s=t&&t.cache?t.cache:Ci,i=t&&t.serializer?t.serializer:Si;return(t&&t.strategy?t.strategy:zi)(e,{cache:s,serializer:i})}function $i(e,t,s,i){const a=null==(n=i)||"number"==typeof n||"boolean"==typeof n?i:s(i);var n;let o=t.get(a);return void 0===o&&(o=e.call(this,i),t.set(a,o)),o}function xi(e,t,s){const i=Array.prototype.slice.call(arguments,3),a=s(i);let n=t.get(a);return void 0===n&&(n=e.apply(this,i),t.set(a,n)),n}function ki(e,t,s,i,a){return s.bind(t,e,i,a)}function zi(e,t){return ki(e,this,1===e.length?$i:xi,t.cache.create(),t.serializer)}const Si=function(){return JSON.stringify(arguments)};var Ai=class{constructor(){this.cache=Object.create(null)}get(e){return this.cache[e]}set(e,t){this.cache[e]=t}};const Ci={create:function(){return new Ai}},Ei={variadic:function(e,t){return ki(e,this,xi,t.cache.create(),t.serializer)}},Ti=/(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;function Oi(e){const t={};return e.replace(Ti,e=>{const s=e.length;switch(e[0]){case"G":t.era=4===s?"long":5===s?"narrow":"short";break;case"y":t.year=2===s?"2-digit":"numeric";break;case"Y":case"u":case"U":case"r":throw new RangeError("`Y/u/U/r` (year) patterns are not supported, use `y` instead");case"q":case"Q":throw new RangeError("`q/Q` (quarter) patterns are not supported");case"M":case"L":t.month=["numeric","2-digit","short","long","narrow"][s-1];break;case"w":case"W":throw new RangeError("`w/W` (week) patterns are not supported");case"d":t.day=["numeric","2-digit"][s-1];break;case"D":case"F":case"g":throw new RangeError("`D/F/g` (day) patterns are not supported, use `d` instead");case"E":t.weekday=4===s?"long":5===s?"narrow":"short";break;case"e":if(s<4)throw new RangeError("`e..eee` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][s-4];break;case"c":if(s<4)throw new RangeError("`c..ccc` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][s-4];break;case"a":t.hour12=!0;break;case"b":case"B":throw new RangeError("`b/B` (period) patterns are not supported, use `a` instead");case"h":t.hourCycle="h12",t.hour=["numeric","2-digit"][s-1];break;case"H":t.hourCycle="h23",t.hour=["numeric","2-digit"][s-1];break;case"K":t.hourCycle="h11",t.hour=["numeric","2-digit"][s-1];break;case"k":t.hourCycle="h24",t.hour=["numeric","2-digit"][s-1];break;case"j":case"J":case"C":throw new RangeError("`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead");case"m":t.minute=["numeric","2-digit"][s-1];break;case"s":t.second=["numeric","2-digit"][s-1];break;case"S":case"A":throw new RangeError("`S/A` (second) patterns are not supported, use `s` instead");case"z":t.timeZoneName=s<4?"short":"long";break;case"Z":case"O":case"v":case"V":case"X":case"x":throw new RangeError("`Z/O/v/V/X/x` (timeZone) patterns are not supported, use `z` instead")}return""}),t}const Di=/[\t-\r \x85\u200E\u200F\u2028\u2029]/i;function Mi(e){return e.replace(/^(.*?)-/,"")}const Hi=/^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g,Ii=/^(@+)?(\+|#+)?[rs]?$/g,Ni=/(\*)(0+)|(#+)(0+)|(0+)/g,Li=/^(0+)$/;function Pi(e){const t={};return"r"===e[e.length-1]?t.roundingPriority="morePrecision":"s"===e[e.length-1]&&(t.roundingPriority="lessPrecision"),e.replace(Ii,function(e,s,i){return"string"!=typeof i?(t.minimumSignificantDigits=s.length,t.maximumSignificantDigits=s.length):"+"===i?t.minimumSignificantDigits=s.length:"#"===s[0]?t.maximumSignificantDigits=s.length:(t.minimumSignificantDigits=s.length,t.maximumSignificantDigits=s.length+("string"==typeof i?i.length:0)),""}),t}function Ri(e){switch(e){case"sign-auto":return{signDisplay:"auto"};case"sign-accounting":case"()":return{currencySign:"accounting"};case"sign-always":case"+!":return{signDisplay:"always"};case"sign-accounting-always":case"()!":return{signDisplay:"always",currencySign:"accounting"};case"sign-except-zero":case"+?":return{signDisplay:"exceptZero"};case"sign-accounting-except-zero":case"()?":return{signDisplay:"exceptZero",currencySign:"accounting"};case"sign-never":case"+_":return{signDisplay:"never"}}}function Bi(e){let t;if("E"===e[0]&&"E"===e[1]?(t={notation:"engineering"},e=e.slice(2)):"E"===e[0]&&(t={notation:"scientific"},e=e.slice(1)),t){const s=e.slice(0,2);if("+!"===s?(t.signDisplay="always",e=e.slice(2)):"+?"===s&&(t.signDisplay="exceptZero",e=e.slice(2)),!Li.test(e))throw new Error("Malformed concise eng/scientific notation");t.minimumIntegerDigits=e.length}return t}function Ui(e){const t=Ri(e);return t||{}}function ji(e){let t={};for(const s of e){switch(s.stem){case"percent":case"%":t.style="percent";continue;case"%x100":t.style="percent",t.scale=100;continue;case"currency":t.style="currency",t.currency=s.options[0];continue;case"group-off":case",_":t.useGrouping=!1;continue;case"precision-integer":case".":t.maximumFractionDigits=0;continue;case"measure-unit":case"unit":t.style="unit",t.unit=Mi(s.options[0]);continue;case"compact-short":case"K":t.notation="compact",t.compactDisplay="short";continue;case"compact-long":case"KK":t.notation="compact",t.compactDisplay="long";continue;case"scientific":t={...t,notation:"scientific",...s.options.reduce((e,t)=>({...e,...Ui(t)}),{})};continue;case"engineering":t={...t,notation:"engineering",...s.options.reduce((e,t)=>({...e,...Ui(t)}),{})};continue;case"notation-simple":t.notation="standard";continue;case"unit-width-narrow":t.currencyDisplay="narrowSymbol",t.unitDisplay="narrow";continue;case"unit-width-short":t.currencyDisplay="code",t.unitDisplay="short";continue;case"unit-width-full-name":t.currencyDisplay="name",t.unitDisplay="long";continue;case"unit-width-iso-code":t.currencyDisplay="symbol";continue;case"scale":t.scale=parseFloat(s.options[0]);continue;case"rounding-mode-floor":t.roundingMode="floor";continue;case"rounding-mode-ceiling":t.roundingMode="ceil";continue;case"rounding-mode-down":t.roundingMode="trunc";continue;case"rounding-mode-up":t.roundingMode="expand";continue;case"rounding-mode-half-even":t.roundingMode="halfEven";continue;case"rounding-mode-half-down":t.roundingMode="halfTrunc";continue;case"rounding-mode-half-up":t.roundingMode="halfExpand";continue;case"integer-width":if(s.options.length>1)throw new RangeError("integer-width stems only accept a single optional option");s.options[0].replace(Ni,function(e,s,i,a,n,o){if(s)t.minimumIntegerDigits=i.length;else{if(a&&n)throw new Error("We currently do not support maximum integer digits");if(o)throw new Error("We currently do not support exact integer digits")}return""});continue}if(Li.test(s.stem)){t.minimumIntegerDigits=s.stem.length;continue}if(Hi.test(s.stem)){if(s.options.length>1)throw new RangeError("Fraction-precision stems only accept a single optional option");s.stem.replace(Hi,function(e,s,i,a,n,o){return"*"===i?t.minimumFractionDigits=s.length:a&&"#"===a[0]?t.maximumFractionDigits=a.length:n&&o?(t.minimumFractionDigits=n.length,t.maximumFractionDigits=n.length+o.length):(t.minimumFractionDigits=s.length,t.maximumFractionDigits=s.length),""});const e=s.options[0];"w"===e?t={...t,trailingZeroDisplay:"stripIfInteger"}:e&&(t={...t,...Pi(e)});continue}if(Ii.test(s.stem)){t={...t,...Pi(s.stem)};continue}const e=Ri(s.stem);e&&(t={...t,...e});const i=Bi(s.stem);i&&(t={...t,...i})}return t}let Fi=function(e){return e[e.EXPECT_ARGUMENT_CLOSING_BRACE=1]="EXPECT_ARGUMENT_CLOSING_BRACE",e[e.EMPTY_ARGUMENT=2]="EMPTY_ARGUMENT",e[e.MALFORMED_ARGUMENT=3]="MALFORMED_ARGUMENT",e[e.EXPECT_ARGUMENT_TYPE=4]="EXPECT_ARGUMENT_TYPE",e[e.INVALID_ARGUMENT_TYPE=5]="INVALID_ARGUMENT_TYPE",e[e.EXPECT_ARGUMENT_STYLE=6]="EXPECT_ARGUMENT_STYLE",e[e.INVALID_NUMBER_SKELETON=7]="INVALID_NUMBER_SKELETON",e[e.INVALID_DATE_TIME_SKELETON=8]="INVALID_DATE_TIME_SKELETON",e[e.EXPECT_NUMBER_SKELETON=9]="EXPECT_NUMBER_SKELETON",e[e.EXPECT_DATE_TIME_SKELETON=10]="EXPECT_DATE_TIME_SKELETON",e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE=11]="UNCLOSED_QUOTE_IN_ARGUMENT_STYLE",e[e.EXPECT_SELECT_ARGUMENT_OPTIONS=12]="EXPECT_SELECT_ARGUMENT_OPTIONS",e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE=13]="EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE=14]="INVALID_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR=15]="EXPECT_SELECT_ARGUMENT_SELECTOR",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR=16]="EXPECT_PLURAL_ARGUMENT_SELECTOR",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT=17]="EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT=18]="EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT",e[e.INVALID_PLURAL_ARGUMENT_SELECTOR=19]="INVALID_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR=20]="DUPLICATE_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR=21]="DUPLICATE_SELECT_ARGUMENT_SELECTOR",e[e.MISSING_OTHER_CLAUSE=22]="MISSING_OTHER_CLAUSE",e[e.INVALID_TAG=23]="INVALID_TAG",e[e.INVALID_TAG_NAME=25]="INVALID_TAG_NAME",e[e.UNMATCHED_CLOSING_TAG=26]="UNMATCHED_CLOSING_TAG",e[e.UNCLOSED_TAG=27]="UNCLOSED_TAG",e}({});function Zi(e){return 0===e.type}function Wi(e){return 1===e.type}function qi(e){return 2===e.type}function Gi(e){return 3===e.type}function Ki(e){return 4===e.type}function Vi(e){return 5===e.type}function Yi(e){return 6===e.type}function Xi(e){return 7===e.type}function Ji(e){return 8===e.type}function Qi(e){return!(!e||"object"!=typeof e||0!==e.type)}function ea(e){return!(!e||"object"!=typeof e||1!==e.type)}const ta=/[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/,sa={"001":["H","h"],419:["h","H","hB","hb"],AC:["H","h","hb","hB"],AD:["H","hB"],AE:["h","hB","hb","H"],AF:["H","hb","hB","h"],AG:["h","hb","H","hB"],AI:["H","h","hb","hB"],AL:["h","H","hB"],AM:["H","hB"],AO:["H","hB"],AR:["h","H","hB","hb"],AS:["h","H"],AT:["H","hB"],AU:["h","hb","H","hB"],AW:["H","hB"],AX:["H"],AZ:["H","hB","h"],BA:["H","hB","h"],BB:["h","hb","H","hB"],BD:["h","hB","H"],BE:["H","hB"],BF:["H","hB"],BG:["H","hB","h"],BH:["h","hB","hb","H"],BI:["H","h"],BJ:["H","hB"],BL:["H","hB"],BM:["h","hb","H","hB"],BN:["hb","hB","h","H"],BO:["h","H","hB","hb"],BQ:["H"],BR:["H","hB"],BS:["h","hb","H","hB"],BT:["h","H"],BW:["H","h","hb","hB"],BY:["H","h"],BZ:["H","h","hb","hB"],CA:["h","hb","H","hB"],CC:["H","h","hb","hB"],CD:["hB","H"],CF:["H","h","hB"],CG:["H","hB"],CH:["H","hB","h"],CI:["H","hB"],CK:["H","h","hb","hB"],CL:["h","H","hB","hb"],CM:["H","h","hB"],CN:["H","hB","hb","h"],CO:["h","H","hB","hb"],CP:["H"],CR:["h","H","hB","hb"],CU:["h","H","hB","hb"],CV:["H","hB"],CW:["H","hB"],CX:["H","h","hb","hB"],CY:["h","H","hb","hB"],CZ:["H"],DE:["H","hB"],DG:["H","h","hb","hB"],DJ:["h","H"],DK:["H"],DM:["h","hb","H","hB"],DO:["h","H","hB","hb"],DZ:["h","hB","hb","H"],EA:["H","h","hB","hb"],EC:["h","H","hB","hb"],EE:["H","hB"],EG:["h","hB","hb","H"],EH:["h","hB","hb","H"],ER:["h","H"],ES:["H","hB","h","hb"],ET:["hB","hb","h","H"],FI:["H"],FJ:["h","hb","H","hB"],FK:["H","h","hb","hB"],FM:["h","hb","H","hB"],FO:["H","h"],FR:["H","hB"],GA:["H","hB"],GB:["H","h","hb","hB"],GD:["h","hb","H","hB"],GE:["H","hB","h"],GF:["H","hB"],GG:["H","h","hb","hB"],GH:["h","H"],GI:["H","h","hb","hB"],GL:["H","h"],GM:["h","hb","H","hB"],GN:["H","hB"],GP:["H","hB"],GQ:["H","hB","h","hb"],GR:["h","H","hb","hB"],GS:["H","h","hb","hB"],GT:["h","H","hB","hb"],GU:["h","hb","H","hB"],GW:["H","hB"],GY:["h","hb","H","hB"],HK:["h","hB","hb","H"],HN:["h","H","hB","hb"],HR:["H","hB"],HU:["H","h"],IC:["H","h","hB","hb"],ID:["H"],IE:["H","h","hb","hB"],IL:["H","hB"],IM:["H","h","hb","hB"],IN:["h","H"],IO:["H","h","hb","hB"],IQ:["h","hB","hb","H"],IR:["hB","H"],IS:["H"],IT:["H","hB"],JE:["H","h","hb","hB"],JM:["h","hb","H","hB"],JO:["h","hB","hb","H"],JP:["H","K","h"],KE:["hB","hb","H","h"],KG:["H","h","hB","hb"],KH:["hB","h","H","hb"],KI:["h","hb","H","hB"],KM:["H","h","hB","hb"],KN:["h","hb","H","hB"],KP:["h","H","hB","hb"],KR:["h","H","hB","hb"],KW:["h","hB","hb","H"],KY:["h","hb","H","hB"],KZ:["H","hB"],LA:["H","hb","hB","h"],LB:["h","hB","hb","H"],LC:["h","hb","H","hB"],LI:["H","hB","h"],LK:["H","h","hB","hb"],LR:["h","hb","H","hB"],LS:["h","H"],LT:["H","h","hb","hB"],LU:["H","h","hB"],LV:["H","hB","hb","h"],LY:["h","hB","hb","H"],MA:["H","h","hB","hb"],MC:["H","hB"],MD:["H","hB"],ME:["H","hB","h"],MF:["H","hB"],MG:["H","h"],MH:["h","hb","H","hB"],MK:["H","h","hb","hB"],ML:["H"],MM:["hB","hb","H","h"],MN:["H","h","hb","hB"],MO:["h","hB","hb","H"],MP:["h","hb","H","hB"],MQ:["H","hB"],MR:["h","hB","hb","H"],MS:["H","h","hb","hB"],MT:["H","h"],MU:["H","h"],MV:["H","h"],MW:["h","hb","H","hB"],MX:["h","H","hB","hb"],MY:["hb","hB","h","H"],MZ:["H","hB"],NA:["h","H","hB","hb"],NC:["H","hB"],NE:["H"],NF:["H","h","hb","hB"],NG:["H","h","hb","hB"],NI:["h","H","hB","hb"],NL:["H","hB"],NO:["H","h"],NP:["H","h","hB"],NR:["H","h","hb","hB"],NU:["H","h","hb","hB"],NZ:["h","hb","H","hB"],OM:["h","hB","hb","H"],PA:["h","H","hB","hb"],PE:["h","H","hB","hb"],PF:["H","h","hB"],PG:["h","H"],PH:["h","hB","hb","H"],PK:["h","hB","H"],PL:["H","h"],PM:["H","hB"],PN:["H","h","hb","hB"],PR:["h","H","hB","hb"],PS:["h","hB","hb","H"],PT:["H","hB"],PW:["h","H"],PY:["h","H","hB","hb"],QA:["h","hB","hb","H"],RE:["H","hB"],RO:["H","hB"],RS:["H","hB","h"],RU:["H"],RW:["H","h"],SA:["h","hB","hb","H"],SB:["h","hb","H","hB"],SC:["H","h","hB"],SD:["h","hB","hb","H"],SE:["H"],SG:["h","hb","H","hB"],SH:["H","h","hb","hB"],SI:["H","hB"],SJ:["H"],SK:["H"],SL:["h","hb","H","hB"],SM:["H","h","hB"],SN:["H","h","hB"],SO:["h","H"],SR:["H","hB"],SS:["h","hb","H","hB"],ST:["H","hB"],SV:["h","H","hB","hb"],SX:["H","h","hb","hB"],SY:["h","hB","hb","H"],SZ:["h","hb","H","hB"],TA:["H","h","hb","hB"],TC:["h","hb","H","hB"],TD:["h","H","hB"],TF:["H","h","hB"],TG:["H","hB"],TH:["H","h"],TJ:["H","h"],TL:["H","hB","hb","h"],TM:["H","h"],TN:["h","hB","hb","H"],TO:["h","H"],TR:["H","hB"],TT:["h","hb","H","hB"],TW:["hB","hb","h","H"],TZ:["hB","hb","H","h"],UA:["H","hB","h"],UG:["hB","hb","H","h"],UM:["h","hb","H","hB"],US:["h","hb","H","hB"],UY:["h","H","hB","hb"],UZ:["H","hB","h"],VA:["H","h","hB"],VC:["h","hb","H","hB"],VE:["h","H","hB","hb"],VG:["h","hb","H","hB"],VI:["h","hb","H","hB"],VN:["H","h"],VU:["h","H"],WF:["H","hB"],WS:["h","H"],XK:["H","hB","h"],YE:["h","hB","hb","H"],YT:["H","hB"],ZA:["H","h","hb","hB"],ZM:["h","hb","H","hB"],ZW:["H","h"],"af-ZA":["H","h","hB","hb"],"ar-001":["h","hB","hb","H"],"ca-ES":["H","h","hB"],"en-001":["h","hb","H","hB"],"en-HK":["h","hb","H","hB"],"en-IL":["H","h","hb","hB"],"en-MY":["h","hb","H","hB"],"es-BR":["H","h","hB","hb"],"es-ES":["H","h","hB","hb"],"es-GQ":["H","h","hB","hb"],"fr-CA":["H","h","hB"],"gl-ES":["H","h","hB"],"gu-IN":["hB","hb","h","H"],"hi-IN":["hB","h","H"],"it-CH":["H","h","hB"],"it-IT":["H","h","hB"],"kn-IN":["hB","h","H"],"ku-SY":["H","hB"],"ml-IN":["hB","h","H"],"mr-IN":["hB","hb","h","H"],"pa-IN":["hB","hb","h","H"],"ta-IN":["hB","h","hb","H"],"te-IN":["hB","h","H"],"zu-ZA":["H","hB","hb","h"]};function ia(e){let t=e.hourCycle;if(void 0===t&&e.hourCycles&&e.hourCycles.length&&(t=e.hourCycles[0]),t)switch(t){case"h24":return"k";case"h23":return"H";case"h12":return"h";case"h11":return"K";default:throw new Error("Invalid hourCycle")}const s=e.language;let i;return"root"!==s&&(i=e.maximize().region),(sa[i||""]||sa[s||""]||sa[`${s}-001`]||sa["001"])[0]}const aa=new RegExp(`^${ta.source}*`),na=new RegExp(`${ta.source}*$`);function oa(e,t){return{start:e,end:t}}const ra=!!Object.fromEntries,la=!!String.prototype.trimStart,da=!!String.prototype.trimEnd,ca=ra?Object.fromEntries:function(e){const t={};for(const[s,i]of e)t[s]=i;return t},ha=la?function(e){return e.trimStart()}:function(e){return e.replace(aa,"")},ua=da?function(e){return e.trimEnd()}:function(e){return e.replace(na,"")},pa=new RegExp("([^\\p{White_Space}\\p{Pattern_Syntax}]*)","yu");var ga=class{constructor(e,t={}){this.message=e,this.position={offset:0,line:1,column:1},this.ignoreTag=!!t.ignoreTag,this.locale=t.locale,this.requiresOtherClause=!!t.requiresOtherClause,this.shouldParseSkeletons=!!t.shouldParseSkeletons}parse(){if(0!==this.offset())throw Error("parser can only be used once");if(this.message.length>0){const e=this.message.charCodeAt(0);if(35!==e&&39!==e&&60!==e&&123!==e&&125!==e){const e=function(e){if(0===e.length)return null;let t=1,s=1;for(let i=0;i<e.length;){const a=e.charCodeAt(i);switch(a){case 35:case 39:case 60:case 123:case 125:return null}if(10===a)t++,s=1,i++;else if(s++,a>=55296&&a<=56319&&i+1<e.length){const t=e.charCodeAt(i+1);i+=t>=56320&&t<=57343?2:1}else i++}return{offset:e.length,line:t,column:s}}(this.message);if(e){const t=this.clonePosition();return this.position=e,{val:[{type:0,value:this.message,location:oa(t,this.clonePosition())}],err:null}}}}return this.parseMessage(0,"",!1)}parseMessage(e,t,s){let i=[];for(;!this.isEOF();){const a=this.char();if(123===a){const t=this.parseArgument(e,s);if(t.err)return t;i.push(t.val)}else{if(125===a&&e>0)break;if(35!==a||"plural"!==t&&"selectordinal"!==t){if(60===a&&!this.ignoreTag&&47===this.peek()){if(s)break;return this.error(26,oa(this.clonePosition(),this.clonePosition()))}if(60===a&&!this.ignoreTag&&ma(this.peek()||0)){const s=this.parseTag(e,t);if(s.err)return s;i.push(s.val)}else{const s=this.parseLiteral(e,t);if(s.err)return s;i.push(s.val)}}else{const e=this.clonePosition();this.bump(),i.push({type:7,location:oa(e,this.clonePosition())})}}}return{val:i,err:null}}parseTag(e,t){const s=this.clonePosition();this.bump();const i=this.parseTagName();if(this.bumpSpace(),this.bumpIf("/>"))return{val:{type:0,value:`<${i}/>`,location:oa(s,this.clonePosition())},err:null};if(this.bumpIf(">")){const a=this.parseMessage(e+1,t,!0);if(a.err)return a;const n=a.val,o=this.clonePosition();if(this.bumpIf("</")){if(this.isEOF()||!ma(this.char()))return this.error(23,oa(o,this.clonePosition()));const e=this.clonePosition();return i!==this.parseTagName()?this.error(26,oa(e,this.clonePosition())):(this.bumpSpace(),this.bumpIf(">")?{val:{type:8,value:i,children:n,location:oa(s,this.clonePosition())},err:null}:this.error(23,oa(o,this.clonePosition())))}return this.error(27,oa(s,this.clonePosition()))}return this.error(23,oa(s,this.clonePosition()))}parseTagName(){const e=this.offset();for(this.bump();!this.isEOF()&&va(this.char());)this.bump();return this.message.slice(e,this.offset())}parseLiteral(e,t){const s=this.clonePosition();let i="";for(;;){const s=this.tryParseQuote(t);if(s){i+=s;continue}const a=this.tryParseUnquoted(e,t);if(a){i+=a;continue}const n=this.tryParseLeftAngleBracket();if(!n)break;i+=n}return{val:{type:0,value:i,location:oa(s,this.clonePosition())},err:null}}tryParseLeftAngleBracket(){return this.isEOF()||60!==this.char()||!this.ignoreTag&&(ma(e=this.peek()||0)||47===e)?null:(this.bump(),"<");var e}tryParseQuote(e){if(this.isEOF()||39!==this.char())return null;switch(this.peek()){case 39:return this.bump(),this.bump(),"'";case 123:case 60:case 62:case 125:break;case 35:if("plural"===e||"selectordinal"===e)break;return null;default:return null}this.bump();const t=[this.char()];for(this.bump();!this.isEOF();){const e=this.char();if(39===e){if(39!==this.peek()){this.bump();break}t.push(39),this.bump()}else t.push(e);this.bump()}return String.fromCodePoint(...t)}tryParseUnquoted(e,t){if(this.isEOF())return null;const s=this.char();return 60===s||123===s||35===s&&("plural"===t||"selectordinal"===t)||125===s&&e>0?null:(this.bump(),String.fromCodePoint(s))}parseArgument(e,t){const s=this.clonePosition();if(this.bump(),this.bumpSpace(),this.isEOF())return this.error(1,oa(s,this.clonePosition()));if(125===this.char())return this.bump(),this.error(2,oa(s,this.clonePosition()));let i=this.parseIdentifierIfPossible().value;if(!i)return this.error(3,oa(s,this.clonePosition()));if(this.bumpSpace(),this.isEOF())return this.error(1,oa(s,this.clonePosition()));switch(this.char()){case 125:return this.bump(),{val:{type:1,value:i,location:oa(s,this.clonePosition())},err:null};case 44:return this.bump(),this.bumpSpace(),this.isEOF()?this.error(1,oa(s,this.clonePosition())):this.parseArgumentOptions(e,t,i,s);default:return this.error(3,oa(s,this.clonePosition()))}}parseIdentifierIfPossible(){const e=this.clonePosition(),t=this.offset(),s=function(e,t){return pa.lastIndex=t,pa.exec(e)[1]??""}(this.message,t),i=t+s.length;return this.bumpTo(i),{value:s,location:oa(e,this.clonePosition())}}parseArgumentOptions(e,t,s,i){let a=this.clonePosition(),n=this.parseIdentifierIfPossible().value,o=this.clonePosition();switch(n){case"":return this.error(4,oa(a,o));case"number":case"date":case"time":{this.bumpSpace();let e=null;if(this.bumpIf(",")){this.bumpSpace();const t=this.clonePosition(),s=this.parseSimpleArgStyleIfPossible();if(s.err)return s;const i=ua(s.val);if(0===i.length)return this.error(6,oa(this.clonePosition(),this.clonePosition()));e={style:i,styleLocation:oa(t,this.clonePosition())}}const t=this.tryParseArgumentClose(i);if(t.err)return t;const a=oa(i,this.clonePosition());if(e&&e.style.startsWith("::")){let t=ha(e.style.slice(2));if("number"===n){const i=this.parseNumberSkeletonFromString(t,e.styleLocation);return i.err?i:{val:{type:2,value:s,location:a,style:i.val},err:null}}{if(0===t.length)return this.error(10,a);let i=t;this.locale&&(i=function(e,t){let s="";for(let i=0;i<e.length;i++){const a=e.charAt(i);if("j"===a){let n=0;for(;i+1<e.length&&e.charAt(i+1)===a;)n++,i++;let o=1+(1&n),r=n<2?1:3+(n>>1),l="a",d=ia(t);for("H"!=d&&"k"!=d||(r=0);r-- >0;)s+=l;for(;o-- >0;)s=d+s}else s+="J"===a?"H":a}return s}(t,this.locale));return{val:{type:"date"===n?3:4,value:s,location:a,style:{type:1,pattern:i,location:e.styleLocation,parsedOptions:this.shouldParseSkeletons?Oi(i):{}}},err:null}}}return{val:{type:"number"===n?2:"date"===n?3:4,value:s,location:a,style:e?.style??null},err:null}}case"plural":case"selectordinal":case"select":{const a=this.clonePosition();if(this.bumpSpace(),!this.bumpIf(","))return this.error(12,oa(a,{...a}));this.bumpSpace();let o=this.parseIdentifierIfPossible(),r=0;if("select"!==n&&"offset"===o.value){if(!this.bumpIf(":"))return this.error(13,oa(this.clonePosition(),this.clonePosition()));this.bumpSpace();const e=this.tryParseDecimalInteger(13,14);if(e.err)return e;this.bumpSpace(),o=this.parseIdentifierIfPossible(),r=e.val}const l=this.tryParsePluralOrSelectOptions(e,n,t,o);if(l.err)return l;const d=this.tryParseArgumentClose(i);if(d.err)return d;const c=oa(i,this.clonePosition());return"select"===n?{val:{type:5,value:s,options:ca(l.val),location:c},err:null}:{val:{type:6,value:s,options:ca(l.val),offset:r,pluralType:"plural"===n?"cardinal":"ordinal",location:c},err:null}}default:return this.error(5,oa(a,o))}}tryParseArgumentClose(e){return this.isEOF()||125!==this.char()?this.error(1,oa(e,this.clonePosition())):(this.bump(),{val:!0,err:null})}parseSimpleArgStyleIfPossible(){let e=0;const t=this.clonePosition();for(;!this.isEOF();)switch(this.char()){case 39:{this.bump();let e=this.clonePosition();if(!this.bumpUntil("'"))return this.error(11,oa(e,this.clonePosition()));this.bump();break}case 123:e+=1,this.bump();break;case 125:if(!(e>0))return{val:this.message.slice(t.offset,this.offset()),err:null};e-=1;break;default:this.bump()}return{val:this.message.slice(t.offset,this.offset()),err:null}}parseNumberSkeletonFromString(e,t){let s=[];try{s=function(e){if(0===e.length)throw new Error("Number skeleton cannot be empty");const t=e.split(Di).filter(e=>e.length>0),s=[];for(const e of t){let t=e.split("/");if(0===t.length)throw new Error("Invalid number skeleton");const[i,...a]=t;for(const e of a)if(0===e.length)throw new Error("Invalid number skeleton");s.push({stem:i,options:a})}return s}(e)}catch{return this.error(7,t)}return{val:{type:0,tokens:s,location:t,parsedOptions:this.shouldParseSkeletons?ji(s):{}},err:null}}tryParsePluralOrSelectOptions(e,t,s,i){let a=!1;const n=[],o=new Set;let{value:r,location:l}=i;for(;;){if(0===r.length){const e=this.clonePosition();if("select"===t||!this.bumpIf("="))break;{const t=this.tryParseDecimalInteger(16,19);if(t.err)return t;l=oa(e,this.clonePosition()),r=this.message.slice(e.offset,this.offset())}}if(o.has(r))return this.error("select"===t?21:20,l);"other"===r&&(a=!0),this.bumpSpace();const i=this.clonePosition();if(!this.bumpIf("{"))return this.error("select"===t?17:18,oa(this.clonePosition(),this.clonePosition()));const d=this.parseMessage(e+1,t,s);if(d.err)return d;const c=this.tryParseArgumentClose(i);if(c.err)return c;n.push([r,{value:d.val,location:oa(i,this.clonePosition())}]),o.add(r),this.bumpSpace(),({value:r,location:l}=this.parseIdentifierIfPossible())}return 0===n.length?this.error("select"===t?15:16,oa(this.clonePosition(),this.clonePosition())):this.requiresOtherClause&&!a?this.error(22,oa(this.clonePosition(),this.clonePosition())):{val:n,err:null}}tryParseDecimalInteger(e,t){let s=1;const i=this.clonePosition();this.bumpIf("+")||this.bumpIf("-")&&(s=-1);let a=!1,n=0;for(;!this.isEOF();){const e=this.char();if(!(e>=48&&e<=57))break;a=!0,n=10*n+(e-48),this.bump()}const o=oa(i,this.clonePosition());return a?(n*=s,Number.isSafeInteger(n)?{val:n,err:null}:this.error(t,o)):this.error(e,o)}offset(){return this.position.offset}isEOF(){return this.offset()===this.message.length}clonePosition(){return{offset:this.position.offset,line:this.position.line,column:this.position.column}}char(){const e=this.position.offset;if(e>=this.message.length)throw Error("out of bound");const t=this.message.codePointAt(e);if(void 0===t)throw Error(`Offset ${e} is at invalid UTF-16 code unit boundary`);return t}error(e,t){return{val:null,err:{kind:e,message:this.message,location:t}}}bump(){if(this.isEOF())return;const e=this.char();10===e?(this.position.line+=1,this.position.column=1,this.position.offset+=1):(this.position.column+=1,this.position.offset+=e<65536?1:2)}bumpIf(e){if(this.message.startsWith(e,this.offset())){for(let t=0;t<e.length;t++)this.bump();return!0}return!1}bumpUntil(e){const t=this.offset(),s=this.message.indexOf(e,t);return s>=0?(this.bumpTo(s),!0):(this.bumpTo(this.message.length),!1)}bumpTo(e){if(this.offset()>e)throw Error(`targetOffset ${e} must be greater than or equal to the current offset ${this.offset()}`);for(e=Math.min(e,this.message.length);;){const t=this.offset();if(t===e)break;if(t>e)throw Error(`targetOffset ${e} is at invalid UTF-16 code unit boundary`);if(this.bump(),this.isEOF())break}}bumpSpace(){for(;!this.isEOF()&&fa(this.char());)this.bump()}peek(){if(this.isEOF())return null;const e=this.char(),t=this.offset();return this.message.charCodeAt(t+(e>=65536?2:1))??null}};function ma(e){return e>=97&&e<=122||e>=65&&e<=90}function va(e){return 45===e||46===e||e>=48&&e<=57||95===e||e>=97&&e<=122||e>=65&&e<=90||183==e||e>=192&&e<=214||e>=216&&e<=246||e>=248&&e<=893||e>=895&&e<=8191||e>=8204&&e<=8205||e>=8255&&e<=8256||e>=8304&&e<=8591||e>=11264&&e<=12271||e>=12289&&e<=55295||e>=63744&&e<=64975||e>=65008&&e<=65533||e>=65536&&e<=983039}function fa(e){return e>=9&&e<=13||32===e||133===e||e>=8206&&e<=8207||8232===e||8233===e}function _a(e){e.forEach(e=>{if(delete e.location,Vi(e)||Yi(e))for(const t in e.options)delete e.options[t].location,_a(e.options[t].value);else qi(e)&&Qi(e.style)||(Gi(e)||Ki(e))&&ea(e.style)?delete e.style.location:Ji(e)&&_a(e.children)})}function ba(e,t={}){t={shouldParseSkeletons:!0,requiresOtherClause:!0,...t};const s=new ga(e,t).parse();if(s.err){const e=SyntaxError(Fi[s.err.kind]);throw e.location=s.err.location,e.originalMessage=s.err.message,e}return t?.captureLocation||_a(s.val),s.val}var ya=class extends Error{constructor(e,t,s){super(e),this.code=t,this.originalMessage=s}toString(){return`[formatjs Error: ${this.code}] ${this.message}`}},wa=class extends ya{constructor(e,t,s,i){super(`Invalid values for "${e}": "${t}". Options are "${Object.keys(s).join('", "')}"`,"INVALID_VALUE",i)}},$a=class extends ya{constructor(e,t,s){super(`Value for "${e}" must be of type ${t}`,"INVALID_VALUE",s)}},xa=class extends ya{constructor(e,t){super(`The intl string context variable "${e}" was not provided to the string "${t}"`,"MISSING_VALUE",t)}};function ka(e){return"function"==typeof e}function za(e,t,s,i,a,n,o){if(1===e.length&&Zi(e[0]))return[{type:0,value:e[0].value}];const r=[];for(const l of e){if(Zi(l)){r.push({type:0,value:l.value});continue}if(Xi(l)){"number"==typeof n&&r.push({type:0,value:s.getNumberFormat(t).format(n)});continue}const{value:e}=l;if(!a||!(e in a))throw new xa(e,o);let d=a[e];if(Wi(l))d&&"string"!=typeof d&&"number"!=typeof d&&"bigint"!=typeof d||(d="string"==typeof d||"number"==typeof d||"bigint"==typeof d?String(d):""),r.push({type:"string"==typeof d?0:1,value:d});else{if(Gi(l)){const e="string"==typeof l.style?i.date[l.style]:ea(l.style)?l.style.parsedOptions:void 0;r.push({type:0,value:s.getDateTimeFormat(t,e).format(d)});continue}if(Ki(l)){const e="string"==typeof l.style?i.time[l.style]:ea(l.style)?l.style.parsedOptions:i.time.medium;r.push({type:0,value:s.getDateTimeFormat(t,e).format(d)});continue}if(qi(l)){const e="string"==typeof l.style?i.number[l.style]:Qi(l.style)?l.style.parsedOptions:void 0;if(e&&e.scale){const t=e.scale||1;if("bigint"==typeof d){if(!Number.isInteger(t))throw new TypeError(`Cannot apply fractional scale ${t} to bigint value. Scale must be an integer when formatting bigint.`);d*=BigInt(t)}else d*=t}r.push({type:0,value:s.getNumberFormat(t,e).format(d)});continue}if(Ji(l)){const{children:e,value:d}=l,c=a[d];if(!ka(c))throw new $a(d,"function",o);let h=c(za(e,t,s,i,a,n).map(e=>e.value));Array.isArray(h)||(h=[h]),r.push(...h.map(e=>({type:"string"==typeof e?0:1,value:e})))}if(Vi(l)){const e=d,n=(Object.prototype.hasOwnProperty.call(l.options,e)?l.options[e]:void 0)||l.options.other;if(!n)throw new wa(l.value,d,Object.keys(l.options),o);r.push(...za(n.value,t,s,i,a));continue}if(Yi(l)){const e=`=${d}`;let n=Object.prototype.hasOwnProperty.call(l.options,e)?l.options[e]:void 0;if(!n){if(!Intl.PluralRules)throw new ya('Intl.PluralRules is not available in this environment.\nTry polyfilling it using "@formatjs/intl-pluralrules"\n',"MISSING_INTL_API",o);const e="bigint"==typeof d?Number(d):d,i=s.getPluralRules(t,{type:l.pluralType}).select(e-(l.offset||0));n=(Object.prototype.hasOwnProperty.call(l.options,i)?l.options[i]:void 0)||l.options.other}if(!n)throw new wa(l.value,d,Object.keys(l.options),o);const c="bigint"==typeof d?Number(d):d;r.push(...za(n.value,t,s,i,a,c-(l.offset||0)));continue}}}return(l=r).length<2?l:l.reduce((e,t)=>{const s=e[e.length-1];return s&&0===s.type&&0===t.type?s.value+=t.value:e.push(t),e},[]);var l}function Sa(e,t){return t?Object.keys(e).reduce((s,i)=>{var a,n;return s[i]=(a=e[i],(n=t[i])?{...a,...n,...Object.keys(a).reduce((e,t)=>(e[t]={...a[t],...n[t]},e),{})}:a),s},{...e}):e}function Aa(e){return{create:()=>({get:t=>e[t],set(t,s){e[t]=s}})}}var Ca=class e{constructor(t,s=e.defaultLocale,i,a){if(this.formatterCache={number:{},dateTime:{},pluralRules:{}},this.format=e=>{const t=this.formatToParts(e);if(1===t.length)return t[0].value;const s=t.reduce((e,t)=>(e.length&&0===t.type&&"string"==typeof e[e.length-1]?e[e.length-1]+=t.value:e.push(t.value),e),[]);return s.length<=1?s[0]||"":s},this.formatToParts=e=>za(this.ast,this.locales,this.formatters,this.formats,e,void 0,this.message),this.resolvedOptions=()=>({locale:this.resolvedLocale?.toString()||Intl.NumberFormat.supportedLocalesOf(this.locales)[0]}),this.getAst=()=>this.ast,this.locales=s,this.resolvedLocale=e.resolveLocale(s),"string"==typeof t){if(this.message=t,!e.__parse)throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");const{...s}=a||{};this.ast=e.__parse(t,{...s,locale:this.resolvedLocale})}else this.ast=t;if(!Array.isArray(this.ast))throw new TypeError("A message must be provided as a String or AST.");this.formats=Sa(e.formats,i),this.formatters=a&&a.formatters||function(e={number:{},dateTime:{},pluralRules:{}}){return{getNumberFormat:wi((...e)=>new Intl.NumberFormat(...e),{cache:Aa(e.number),strategy:Ei.variadic}),getDateTimeFormat:wi((...e)=>new Intl.DateTimeFormat(...e),{cache:Aa(e.dateTime),strategy:Ei.variadic}),getPluralRules:wi((...e)=>new Intl.PluralRules(...e),{cache:Aa(e.pluralRules),strategy:Ei.variadic})}}(this.formatterCache)}static{this.memoizedDefaultLocale=null}static get defaultLocale(){return e.memoizedDefaultLocale||(e.memoizedDefaultLocale=(new Intl.NumberFormat).resolvedOptions().locale),e.memoizedDefaultLocale}static{this.resolveLocale=e=>{if(void 0===Intl.Locale)return;const t=Intl.NumberFormat.supportedLocalesOf(e);return t.length>0?new Intl.Locale(t[0]):new Intl.Locale("string"==typeof e?e:e[0])}}static{this.__parse=ba}static{this.formats={number:{integer:{maximumFractionDigits:0},currency:{style:"currency"},percent:{style:"percent"}},date:{short:{month:"numeric",day:"numeric",year:"2-digit"},medium:{month:"short",day:"numeric",year:"numeric"},long:{month:"long",day:"numeric",year:"numeric"},full:{weekday:"long",month:"long",day:"numeric",year:"numeric"}},time:{short:{hour:"numeric",minute:"numeric"},medium:{hour:"numeric",minute:"numeric",second:"numeric"},long:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"},full:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"}}}}};const Ea={en:yi},Ta={};function Oa(e){return e.replace(/['"]+/g,"").split(/[-_]/)[0].toLowerCase()}function Da(e){const t=Oa(e);return t in Ea||!ye.includes(t)}function Ma(e,t,...s){const i=Oa(t);let a;try{a=e.split(".").reduce((e,t)=>e[t],Ea[i])}catch(t){a=e.split(".").reduce((e,t)=>e[t],Ea.en)}if(void 0===a&&(a=e.split(".").reduce((e,t)=>e[t],Ea.en)),!s.length)return a;const n={};for(let e=0;e<s.length;e+=2){let t=s[e];t=t.replace(/^{([^}]+)?}$/,"$1"),n[t]=s[e+1]}try{return new Ca(a,t).format(n)}catch(e){return"Translation "+e}}function Ha(e,t,s){e.dispatchEvent(new CustomEvent(t,{detail:s,bubbles:!0,composed:!0,cancelable:!1}))}function Ia(e,t){return(e=e.toString()).split(",")[t]}function Na(e,t){switch(t){case zt:return e.units==Me?W`${si(ht)}`:W`${si(ut)}`;case xe:case bt:return e.units==Me?W`${si(ot)}`:W`${si(rt)}`;case gt:return e.units==Me?W`${si("m<sup>2</sup>")}`:W`${si(st)}`;case mt:return e.units==Me?W`${si(it)}`:W`${si(at)}`;default:return W``}}function La(e,t){!function(e,t){Ha(e,"show-dialog",{dialogTag:"error-dialog",dialogImport:()=>Promise.resolve().then(function(){return _o}),dialogParams:{error:t}})}(t,W`
>>>>>>> f4290c2 (feat(schedules): warn when a solar-azimuth bearing the sun never reaches is set)
    ${e.error}:${e.body.message?W` ${e.body.message} `:""}
  `)}const Pa=(e,t,s=!1)=>{s?history.replaceState(null,"",t):history.pushState(null,"",t),Ha(window,"location-changed",{replace:s})};function Ra(e){var t;if(!e)return"Unknown error";if("string"==typeof e)return e;const s=e;return(null===(t=null==s?void 0:s.body)||void 0===t?void 0:t.message)||(null==s?void 0:s.message)||(null==s?void 0:s.error)||JSON.stringify(e)}function Ba(e){const t=Math.round(e);if(t<60)return`${t} s`;const s=Math.floor(t/60),i=t%60;return i?`${s} min ${i} s`:`${s} min`}function Ua(e,t){e.dispatchEvent(new CustomEvent("hass-notification",{detail:{message:t},bubbles:!0,composed:!0}))}function ja(e,t,s,i){var a;Ua(e,`${Ma(s,null!==(a=null==t?void 0:t.language)&&void 0!==a?a:"en")}: ${Ra(i)}`)}var Fa="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",Za="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z";const Wa=e=>{class s extends e{connectedCallback(){super.connectedCallback(),this.__checkSubscribed()}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const e=this.__unsubs.pop();e instanceof Promise?e.then(e=>e()):e()}this.__unsubs=void 0}}updated(e){super.updated(e),e.has("hass")&&this.__checkSubscribed()}hassSubscribe(){return[]}__checkSubscribed(){void 0===this.__unsubs&&this.isConnected&&void 0!==this.hass&&(this.__unsubs=this.hassSubscribe())}}return t([me({attribute:!1})],s.prototype,"hass",void 0),s};var qa,Ga;!function(e){e.Sunrise="sunrise",e.Sunset="sunset",e.SolarAzimuth="solar_azimuth"}(qa||(qa={})),function(e){e.Disabled="disabled",e.Manual="manual",e.Automatic="automatic"}(Ga||(Ga={}));const Ka=()=>{const e=e=>{let t={};for(let s=0;s<e.length;s+=2){const i=e[s],a=s<e.length?e[s+1]:void 0;t=Object.assign(Object.assign({},t),{[i]:a})}return t},t=window.location.pathname.split("/");let s={page:t[2]||"general",params:{}};if(t.length>3){let i=t.slice(3);if(t.includes("filter")){const t=i.findIndex(e=>"filter"==e),a=i.slice(t+1);i=i.slice(0,t),s=Object.assign(Object.assign({},s),{filter:e(a)})}i.length&&(i.length%2&&(s=Object.assign(Object.assign({},s),{subpage:i.shift()})),i.length&&(s=Object.assign(Object.assign({},s),{params:e(i)})))}return s},Va=(e,...t)=>{let s={page:e,params:{}};t.forEach(e=>{"string"==typeof e?s=Object.assign(Object.assign({},s),{subpage:e}):"params"in e?s=Object.assign(Object.assign({},s),{params:e.params}):"filter"in e&&(s=Object.assign(Object.assign({},s),{filter:e.filter}))});const i=e=>{let t=Object.keys(e);t=t.filter(t=>e[t]),t.sort();let s="";return t.forEach(t=>{const i=e[t];s=s.length?`${s}/${t}/${i}`:`${t}/${i}`}),s};let a=`/${be}/${s.page}`;return s.subpage&&(a=`${a}/${s.subpage}`),i(s.params).length&&(a=`${a}/${i(s.params)}`),s.filter&&(a=`${a}/filter/${i(s.filter)}`),a},Ya=r`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
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

  /* ---- Shared "item card" chrome (Advanced: modules / sensor groups) ---- */

  /* Danger variant of the shared action button (destructive actions) */
  button.action-btn.danger {
    background: transparent;
    border: 1px solid var(--error-color);
    color: var(--error-color);
  }

  button.action-btn.danger:hover {
    background: rgba(var(--rgb-error-color, 244, 67, 54), 0.08);
    opacity: 1;
  }

  /* Usage chip shown in item card headers ("Used by 2 zones" / "Not used") */
  .usage-chip {
    flex-shrink: 0;
    align-self: center;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 2px 10px;
    border-radius: 10px;
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12);
    color: var(--primary-color);
    white-space: nowrap;
  }

  .usage-chip.unused {
    background: var(--secondary-background-color);
    color: var(--secondary-text-color);
  }

  /* Muted one-liner under an item card header */
  .item-description {
    color: var(--secondary-text-color);
    font-size: 0.9em;
    margin-bottom: 8px;
  }

  /* Inline "add new item" row inside the intro card */
  .add-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--divider-color);
  }

  .add-row > input,
  .add-row > select {
    flex: 1 1 220px;
    max-width: 320px;
  }

  /* Item card footer hosting the destructive action / in-use note */
  .card-footer {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--divider-color);
  }

  /* Shared input look (matches the zone-settings .settings-input) */
  .settings-input {
    background: var(--input-fill-color, var(--secondary-background-color));
    border: 1px solid var(--input-ink-color, var(--secondary-text-color));
    border-radius: 4px;
    color: var(--primary-text-color);
    padding: 6px 10px;
    font-family: var(--mdc-typography-body1-font-family, Roboto, sans-serif);
    font-size: 0.9375rem;
    box-sizing: border-box;
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
`;r`
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
<<<<<<< HEAD
`;const Va=e=>String(e).padStart(2,"0");function Ya(e){return e instanceof Date?e:new Date(e)}function Xa(e){const t=Ya(e);return`${Va(t.getHours())}:${Va(t.getMinutes())}`}function Ja(e){const t=Ya(e);return`${t.getFullYear()}-${Va(t.getMonth()+1)}-${Va(t.getDate())} ${Va(t.getHours())}:${Va(t.getMinutes())}`}function Qa(e,t){return e.getFullYear()===t.getFullYear()&&e.getMonth()===t.getMonth()&&e.getDate()===t.getDate()}class en extends(Fa(ce)){constructor(){super(...arguments),this.hideSettingsLinks=!1,this.actionsMode="full",this.zones=[],this._distributors=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._operationError=null,this._confirmIrrigate=null,this._skipDetailsOpen=!1,this._runMinutes={},this._now=Date.now(),this._countdownTimer=null,this._updateScheduled=!1}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}firstUpdated(){qi().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}disconnectedCallback(){super.disconnectedCallback(),this._stopCountdownTicker()}_syncCountdownTicker(){var e,t;const i=Object.keys(null!==(t=null===(e=this._outlook)||void 0===e?void 0:e.active_runs)&&void 0!==t?t:{}).length>0;i&&null===this._countdownTimer?this._countdownTimer=window.setInterval(()=>{this._now=Date.now()},1e3):i||this._stopCountdownTicker()}_stopCountdownTicker(){null!==this._countdownTimer&&(window.clearInterval(this._countdownTimer),this._countdownTimer=null)}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:be+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[i,s,a,n]=await Promise.all([Ei(this.hass),Ti(this.hass),(t=this.hass,t.callWS({type:be+"/irrigation_outlook"})).catch(e=>{console.error("Failed to fetch irrigation outlook:",e)}),Ri(this.hass).catch(e=>(console.error("Failed to fetch distributors:",e),[]))]);this.config=i,this.zones=s,this._outlook=a,this._distributors=n,this._initialLoadDone=!0,this._syncCountdownTicker()}catch(e){console.error("Error fetching data:",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}var t}handleCalculateAllZones(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",be+"/zones",{calculate_all:!0})).catch(e=>{console.error("Failed to calculate all zones:",e),Ba(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after calc-all:",e))}))}handleUpdateAllZones(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",be+"/zones",{update_all:!0})).catch(e=>{console.error("Failed to update all zones:",e),Ba(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after update-all:",e))}))}_canActuate(e){return!!(e.linked_entity||"service"===e.watering_mode&&e.run_service||null!=e.distributor_id)}get _linkedZoneCount(){return this.zones.filter(e=>{var t;return this._canActuate(e)&&(null!==(t=e.duration)&&void 0!==t?t:0)>0}).length}async _doIrrigate(){var e;const t=this._confirmIrrigate;if(this._confirmIrrigate=null,null===t||!this.hass)return;const i="all"===t,s=i?void 0:this.zones.find(e=>{var i;return(null===(i=e.id)||void 0===i?void 0:i.toString())===t}),a=i?`(${this._linkedZoneCount})`:`: ${null!==(e=null==s?void 0:s.name)&&void 0!==e?e:t}`;try{await(n=this.hass,o=i?void 0:t,n.callWS(Object.assign({type:be+"/irrigate_now"},void 0!==o?{zone_id:o}:{}))),Ra(this,`${Oa("panels.zones.confirm_irrigate.toast_started",this.hass.language)} ${a}`)}catch(e){const t=Pa(e);console.error("irrigate_now failed",e),Ra(this,`${Oa("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}var n,o}get _rainDelayUntil(){var e;const t=null===(e=this._outlook)||void 0===e?void 0:e.rain_delay_until;if(!t)return null;const i=new Date(t);return i.getTime()>Date.now()?i:null}async _setRainDelay(e){if(this.hass)try{await((e,t)=>e.callWS({type:be+"/set_rain_delay",hours:t}))(this.hass,e),await this._fetchData()}catch(e){console.error("set_rain_delay failed",e),Ba(this,this.hass,"common.errors.action_failed",e)}}async _clearRainDelay(){var e;if(this.hass)try{await(e=this.hass,e.callWS({type:be+"/clear_rain_delay"})),await this._fetchData()}catch(e){console.error("clear_rain_delay failed",e),Ba(this,this.hass,"common.errors.action_failed",e)}}_zoneRunMinutes(e){var t,i;const s=String(null!==(t=e.id)&&void 0!==t?t:"");return null!==(i=this._runMinutes[s])&&void 0!==i?i:10}_zoneDistributor(e){if(null!=e.distributor_id)return this._distributors.find(t=>t.id===e.distributor_id)}_distributorBusy(e){var t;const i=this._zoneDistributor(e);return!!i&&Object.keys(null!==(t=i.active_cycle)&&void 0!==t?t:{}).length>0}async _runZoneFor(e){if(!this.hass||!this._canActuate(e)||void 0===e.id)return;if(this._distributorBusy(e))return;const t=this._zoneRunMinutes(e);var i,s,a;if(t>0)try{await(i=this.hass,s=e.id.toString(),a=t,i.callWS({type:be+"/run_zone",zone_id:s,duration:a})),Ra(this,`${Oa("panels.zones.run_zone.toast_started",this.hass.language)}: ${e.name} (${t} min)`)}catch(e){const t=Pa(e);console.error("run_zone failed",e),Ra(this,`${Oa("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}}_activeRun(e){var t,i;if(void 0!==e.id)return null===(i=null===(t=this._outlook)||void 0===t?void 0:t.active_runs)||void 0===i?void 0:i[String(e.id)]}_runSecondsLeft(e){if(!e.ends_at)return null;const t=Math.round((new Date(e.ends_at).getTime()-this._now)/1e3);return t>0?t:0}async _stopZone(e){var t,i;if(this.hass&&void 0!==e.id)try{await(t=this.hass,i=e.id.toString(),t.callWS({type:be+"/stop_zone",zone_id:i})),Ra(this,`${Oa("panels.zones.stop_zone.toast_stopped",this.hass.language)}: ${e.name}`),await this._fetchData()}catch(e){const t=Pa(e);console.error("stop_zone failed",e),Ra(this,`${Oa("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}}handleCalculateZone(e){const t=this.zones[e];var i,s;t&&null!=t.id&&this.hass&&(this._operationError=null,this.isSaving=!0,this._scheduleUpdate(),(i=this.hass,s=t.id.toString(),i.callApi("POST",be+"/zones",{id:s,calculate:!0,override_cache:!0})).catch(e=>{const t=Pa(e);console.error("calculateZone failed:",e),this._operationError=t}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after calc:",e))}))}handleUpdateZone(e){const t=this.zones[e];var i,s;t&&null!=t.id&&this.hass&&(this._operationError=null,this.isSaving=!0,this._scheduleUpdate(),(i=this.hass,s=t.id.toString(),i.callApi("POST",be+"/zones",{id:s,update:!0})).catch(e=>{const t=Pa(e);console.error("updateZone failed:",e),this._operationError=t}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after update:",e))}))}_openZoneSettings(e){const t=void 0!==e.id?{params:{zone:String(e.id)}}:void 0;Na(0,t?Ga("setup","zones",t):Ga("setup","zones"))}_runTargetsZone(e,t){return"all"===e.zones||!(!Array.isArray(e.zones)||void 0===t.id)&&e.zones.map(e=>Number(e)).includes(Number(t.id))}get _nextIrrigateRun(){var e;return null===(e=this._outlook)||void 0===e?void 0:e.upcoming_runs.find(e=>"irrigate"===e.action&&e.next_run_utc)}_nextIrrigateRunForZone(e){var t;return null===(t=this._outlook)||void 0===t?void 0:t.upcoming_runs.find(t=>"irrigate"===t.action&&t.next_run_utc&&this._runTargetsZone(t,e))}get _activeGuards(){var e,t;return null!==(t=null===(e=this._outlook)||void 0===e?void 0:e.skip_preview.checks.filter(e=>e.enabled))&&void 0!==t?t:[]}get _triggeredGuards(){return this._activeGuards.filter(e=>e.would_skip)}_zoneHasDeficit(e){var t,i,s;const a=null!==(t=e.duration)&&void 0!==t?t:0,n=Number(null!==(i=e.bucket_threshold)&&void 0!==i?i:0),o=this._zoneEstimate(e),r=o&&o.available&&null!=o.live_deficit?o.live_deficit:Number(null!==(s=e.bucket)&&void 0!==s?s:0);return a>0&&r<n}_formatRunTime(e){if(!this.hass)return"";const t=this.hass.language,i=new Date(e),s=Xa(i),a=new Date;return Qa(i,a)?`${Oa("panels.zones.outlook.today",t)} ${s}`:Qa(i,function(e,t){const i=new Date(e.getTime());return i.setDate(i.getDate()+t),i}(a,1))?`${Oa("panels.zones.outlook.tomorrow",t)} ${s}`:function(e,t){const i=Ya(e);return`${new Intl.DateTimeFormat(t,{weekday:"short"}).format(i)} ${Xa(i)}`}(i,t)}_renderEstimatedTag(e){if(!this.hass||!e.estimated)return W``;const t=this.hass.language;return W`<span
      class="estimate-tag"
      title="${Oa("panels.zones.outlook.estimated_help",t)}"
      >${Oa("panels.zones.outlook.estimated",t)}<ha-icon
        icon="mdi:information-outline"
      ></ha-icon
    ></span>`}_guardLabel(e){return Oa(`panels.zones.outlook.checks.${e.id}`,this.hass.language)}_guardDetail(e){var t;return e.available&&null!==e.observed?Oa(`panels.zones.outlook.check_detail.${e.id}`,this.hass.language,"{observed}",String(e.observed),"{threshold}",String(null!==(t=e.threshold)&&void 0!==t?t:"")):""}_renderSkipReasons(){const e=this.hass.language;return W`
=======
`;const Xa=e=>String(e).padStart(2,"0");function Ja(e){return e instanceof Date?e:new Date(e)}function Qa(e){const t=Ja(e);return`${Xa(t.getHours())}:${Xa(t.getMinutes())}`}function en(e){const t=Ja(e);return`${t.getFullYear()}-${Xa(t.getMonth()+1)}-${Xa(t.getDate())} ${Xa(t.getHours())}:${Xa(t.getMinutes())}`}function tn(e,t){return e.getFullYear()===t.getFullYear()&&e.getMonth()===t.getMonth()&&e.getDate()===t.getDate()}class sn extends(Wa(ce)){constructor(){super(...arguments),this.hideSettingsLinks=!1,this.actionsMode="full",this.zones=[],this._distributors=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._operationError=null,this._confirmIrrigate=null,this._skipDetailsOpen=!1,this._runMinutes={},this._now=Date.now(),this._countdownTimer=null,this._updateScheduled=!1}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}firstUpdated(){Ks().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}disconnectedCallback(){super.disconnectedCallback(),this._stopCountdownTicker()}_syncCountdownTicker(){var e,t;const s=Object.keys(null!==(t=null===(e=this._outlook)||void 0===e?void 0:e.active_runs)&&void 0!==t?t:{}).length>0;s&&null===this._countdownTimer?this._countdownTimer=window.setInterval(()=>{this._now=Date.now()},1e3):s||this._stopCountdownTicker()}_stopCountdownTicker(){null!==this._countdownTimer&&(window.clearInterval(this._countdownTimer),this._countdownTimer=null)}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:be+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[s,i,a,n]=await Promise.all([Ts(this.hass),Ds(this.hass),(t=this.hass,t.callWS({type:be+"/irrigation_outlook"})).catch(e=>{console.error("Failed to fetch irrigation outlook:",e)}),Us(this.hass).catch(e=>(console.error("Failed to fetch distributors:",e),[]))]);this.config=s,this.zones=i,this._outlook=a,this._distributors=n,this._initialLoadDone=!0,this._syncCountdownTicker()}catch(e){console.error("Error fetching data:",e),ja(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}var t}handleCalculateAllZones(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",be+"/zones",{calculate_all:!0})).catch(e=>{console.error("Failed to calculate all zones:",e),ja(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after calc-all:",e))}))}handleUpdateAllZones(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",be+"/zones",{update_all:!0})).catch(e=>{console.error("Failed to update all zones:",e),ja(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after update-all:",e))}))}_canActuate(e){return!!(e.linked_entity||"service"===e.watering_mode&&e.run_service||null!=e.distributor_id)}get _linkedZoneCount(){return this.zones.filter(e=>{var t;return this._canActuate(e)&&(null!==(t=e.duration)&&void 0!==t?t:0)>0}).length}async _doIrrigate(){var e;const t=this._confirmIrrigate;if(this._confirmIrrigate=null,null===t||!this.hass)return;const s="all"===t,i=s?void 0:this.zones.find(e=>{var s;return(null===(s=e.id)||void 0===s?void 0:s.toString())===t}),a=s?`(${this._linkedZoneCount})`:`: ${null!==(e=null==i?void 0:i.name)&&void 0!==e?e:t}`;try{await(n=this.hass,o=s?void 0:t,n.callWS(Object.assign({type:be+"/irrigate_now"},void 0!==o?{zone_id:o}:{}))),Ua(this,`${Ma("panels.zones.confirm_irrigate.toast_started",this.hass.language)} ${a}`)}catch(e){const t=Ra(e);console.error("irrigate_now failed",e),Ua(this,`${Ma("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}var n,o}get _rainDelayUntil(){var e;const t=null===(e=this._outlook)||void 0===e?void 0:e.rain_delay_until;if(!t)return null;const s=new Date(t);return s.getTime()>Date.now()?s:null}async _setRainDelay(e){if(this.hass)try{await((e,t)=>e.callWS({type:be+"/set_rain_delay",hours:t}))(this.hass,e),await this._fetchData()}catch(e){console.error("set_rain_delay failed",e),ja(this,this.hass,"common.errors.action_failed",e)}}async _clearRainDelay(){var e;if(this.hass)try{await(e=this.hass,e.callWS({type:be+"/clear_rain_delay"})),await this._fetchData()}catch(e){console.error("clear_rain_delay failed",e),ja(this,this.hass,"common.errors.action_failed",e)}}_zoneRunMinutes(e){var t,s;const i=String(null!==(t=e.id)&&void 0!==t?t:"");return null!==(s=this._runMinutes[i])&&void 0!==s?s:10}_zoneDistributor(e){if(null!=e.distributor_id)return this._distributors.find(t=>t.id===e.distributor_id)}_distributorBusy(e){var t;const s=this._zoneDistributor(e);return!!s&&Object.keys(null!==(t=s.active_cycle)&&void 0!==t?t:{}).length>0}async _runZoneFor(e){if(!this.hass||!this._canActuate(e)||void 0===e.id)return;if(this._distributorBusy(e))return;const t=this._zoneRunMinutes(e);var s,i,a;if(t>0)try{await(s=this.hass,i=e.id.toString(),a=t,s.callWS({type:be+"/run_zone",zone_id:i,duration:a})),Ua(this,`${Ma("panels.zones.run_zone.toast_started",this.hass.language)}: ${e.name} (${t} min)`)}catch(e){const t=Ra(e);console.error("run_zone failed",e),Ua(this,`${Ma("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}}_activeRun(e){var t,s;if(void 0!==e.id)return null===(s=null===(t=this._outlook)||void 0===t?void 0:t.active_runs)||void 0===s?void 0:s[String(e.id)]}_runSecondsLeft(e){if(!e.ends_at)return null;const t=Math.round((new Date(e.ends_at).getTime()-this._now)/1e3);return t>0?t:0}async _stopZone(e){var t,s;if(this.hass&&void 0!==e.id)try{await(t=this.hass,s=e.id.toString(),t.callWS({type:be+"/stop_zone",zone_id:s})),Ua(this,`${Ma("panels.zones.stop_zone.toast_stopped",this.hass.language)}: ${e.name}`),await this._fetchData()}catch(e){const t=Ra(e);console.error("stop_zone failed",e),Ua(this,`${Ma("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}}handleCalculateZone(e){const t=this.zones[e];var s,i;t&&null!=t.id&&this.hass&&(this._operationError=null,this.isSaving=!0,this._scheduleUpdate(),(s=this.hass,i=t.id.toString(),s.callApi("POST",be+"/zones",{id:i,calculate:!0,override_cache:!0})).catch(e=>{const t=Ra(e);console.error("calculateZone failed:",e),this._operationError=t}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after calc:",e))}))}handleUpdateZone(e){const t=this.zones[e];var s,i;t&&null!=t.id&&this.hass&&(this._operationError=null,this.isSaving=!0,this._scheduleUpdate(),(s=this.hass,i=t.id.toString(),s.callApi("POST",be+"/zones",{id:i,update:!0})).catch(e=>{const t=Ra(e);console.error("updateZone failed:",e),this._operationError=t}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after update:",e))}))}_openZoneSettings(e){const t=void 0!==e.id?{params:{zone:String(e.id)}}:void 0;Pa(0,t?Va("setup","zones",t):Va("setup","zones"))}_runTargetsZone(e,t){return"all"===e.zones||!(!Array.isArray(e.zones)||void 0===t.id)&&e.zones.map(e=>Number(e)).includes(Number(t.id))}get _nextIrrigateRun(){var e;return null===(e=this._outlook)||void 0===e?void 0:e.upcoming_runs.find(e=>"irrigate"===e.action&&e.next_run_utc)}_nextIrrigateRunForZone(e){var t;return null===(t=this._outlook)||void 0===t?void 0:t.upcoming_runs.find(t=>"irrigate"===t.action&&t.next_run_utc&&this._runTargetsZone(t,e))}get _activeGuards(){var e,t;return null!==(t=null===(e=this._outlook)||void 0===e?void 0:e.skip_preview.checks.filter(e=>e.enabled))&&void 0!==t?t:[]}get _triggeredGuards(){return this._activeGuards.filter(e=>e.would_skip)}_zoneHasDeficit(e){var t,s,i;const a=null!==(t=e.duration)&&void 0!==t?t:0,n=Number(null!==(s=e.bucket_threshold)&&void 0!==s?s:0),o=this._zoneEstimate(e),r=o&&o.available&&null!=o.live_deficit?o.live_deficit:Number(null!==(i=e.bucket)&&void 0!==i?i:0);return a>0&&r<n}_formatRunTime(e){if(!this.hass)return"";const t=this.hass.language,s=new Date(e),i=Qa(s),a=new Date;return tn(s,a)?`${Ma("panels.zones.outlook.today",t)} ${i}`:tn(s,function(e,t){const s=new Date(e.getTime());return s.setDate(s.getDate()+t),s}(a,1))?`${Ma("panels.zones.outlook.tomorrow",t)} ${i}`:function(e,t){const s=Ja(e);return`${new Intl.DateTimeFormat(t,{weekday:"short"}).format(s)} ${Qa(s)}`}(s,t)}_renderEstimatedTag(e){if(!this.hass||!e.estimated)return W``;const t=this.hass.language;return W`<span
      class="estimate-tag"
      title="${Ma("panels.zones.outlook.estimated_help",t)}"
      >${Ma("panels.zones.outlook.estimated",t)}<ha-icon
        icon="mdi:information-outline"
      ></ha-icon
    ></span>`}_guardLabel(e){return Ma(`panels.zones.outlook.checks.${e.id}`,this.hass.language)}_guardDetail(e){var t;return e.available&&null!==e.observed?Ma(`panels.zones.outlook.check_detail.${e.id}`,this.hass.language,"{observed}",String(e.observed),"{threshold}",String(null!==(t=e.threshold)&&void 0!==t?t:"")):""}_renderSkipReasons(){const e=this.hass.language;return W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      <div class="outlook-line outlook-skip-reasons">
        <ul class="skip-reasons">
          ${this._triggeredGuards.map(e=>{const t=this._guardDetail(e);return W`<li>
              ${this._guardLabel(e)}${t?W` — ${t}`:""}
            </li>`})}
        </ul>
      </div>
      <div class="outlook-line outlook-dim skip-reasons-note">
<<<<<<< HEAD
        ${Oa("panels.zones.outlook.provisional",e)}
      </div>
    `}_openSchedules(){Na(0,Ga("setup","when-to-water"))}_runActionLabel(e){return Oa(`panels.zones.outlook.actions.${e.action}`,this.hass.language)}_runTargetsLabel(e){const t=this.hass.language;if("all"===e.zones)return Oa("panels.zones.outlook.targets_all",t);const i=Array.isArray(e.zones)?e.zones.length:0;return Oa("panels.zones.outlook.targets_zones",t,"{count}",String(i))}_renderOutlookBanner(){if(!this.hass||!this._outlook)return W``;const e=this.hass.language,t=this._nextIrrigateRun,i=this._triggeredGuards,s=this._outlook.last_skip_evaluation;return t&&t.next_run_utc?W`
=======
        ${Ma("panels.zones.outlook.provisional",e)}
      </div>
    `}_openSchedules(){Pa(0,Va("setup","when-to-water"))}_runActionLabel(e){return Ma(`panels.zones.outlook.actions.${e.action}`,this.hass.language)}_runTargetsLabel(e){const t=this.hass.language;if("all"===e.zones)return Ma("panels.zones.outlook.targets_all",t);const s=Array.isArray(e.zones)?e.zones.length:0;return Ma("panels.zones.outlook.targets_zones",t,"{count}",String(s))}_renderOutlookBanner(){if(!this.hass||!this._outlook)return W``;const e=this.hass.language,t=this._nextIrrigateRun,s=this._triggeredGuards,i=this._outlook.last_skip_evaluation;return t&&t.next_run_utc?W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      <ha-card class="outlook-card">
        <div class="outlook">
          <div class="outlook-line outlook-headline">
            <ha-icon icon="mdi:calendar-clock"></ha-icon>
            <span>
              <strong
<<<<<<< HEAD
                >${Oa("panels.zones.outlook.next_run",e)}:</strong
=======
                >${Ma("panels.zones.outlook.next_run",e)}:</strong
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              >
              ${this._runActionLabel(t)}
              ${this._formatRunTime(t.next_run_utc)}
              ${this._renderEstimatedTag(t)}
              <span class="outlook-dim"
                >· ${t.name} · ${this._runTargetsLabel(t)}</span
              >
            </span>
          </div>

          ${i.length>0?W`
                <div class="outlook-line outlook-skip">
                  <ha-icon icon="mdi:alert"></ha-icon>
                  <span
<<<<<<< HEAD
                    >${Oa("panels.zones.outlook.will_skip",e)}</span
=======
                    >${Ma("panels.zones.outlook.will_skip",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <button
                    class="outlook-info-btn"
                    aria-expanded="${this._skipDetailsOpen}"
<<<<<<< HEAD
                    title="${Oa("panels.zones.outlook.why_skipped",e)}"
=======
                    title="${Ma("panels.zones.outlook.why_skipped",e)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    @click="${()=>{this._skipDetailsOpen=!this._skipDetailsOpen}}"
                  >
                    <ha-icon
                      icon="${this._skipDetailsOpen?"mdi:chevron-up":"mdi:information-outline"}"
                    ></ha-icon>
                    <span class="outlook-info-label"
<<<<<<< HEAD
                      >${Oa("panels.zones.outlook.why_skipped",e)}</span
=======
                      >${Ma("panels.zones.outlook.why_skipped",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    >
                  </button>
                </div>
                ${this._skipDetailsOpen?this._renderSkipReasons():""}
              `:W`
                <div class="outlook-line outlook-clear">
                  <ha-icon icon="mdi:check-circle-outline"></ha-icon>
                  <span
<<<<<<< HEAD
                    >${Oa("panels.zones.outlook.will_run",e)}</span
=======
                    >${Ma("panels.zones.outlook.will_run",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                </div>
              `}
          ${s?this._renderLastRunLine(s):""}
        </div>
      </ha-card>
    `:W`
        <ha-card class="outlook-card">
          <div class="outlook">
            <div class="outlook-line outlook-headline">
              <ha-icon icon="mdi:calendar-alert"></ha-icon>
<<<<<<< HEAD
              <span>${Oa("panels.zones.outlook.no_schedule",e)}</span>
=======
              <span>${Ma("panels.zones.outlook.no_schedule",e)}</span>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              ${this.hideSettingsLinks?"":W`
                    <button
                      class="outlook-link"
                      @click="${this._openSchedules}"
                    >
<<<<<<< HEAD
                      ${Oa("panels.zones.outlook.setup_schedule",e)}
=======
                      ${Ma("panels.zones.outlook.setup_schedule",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    </button>
                  `}
            </div>
            ${s?this._renderLastRunLine(s):""}
          </div>
        </ha-card>
      `}_renderRainDelay(){if(!this.hass||"none"===this.actionsMode)return W``;const e=this.hass.language,t=this._rainDelayUntil;return t?W`
        <ha-card class="rain-delay-card paused">
          <div class="rain-delay">
            <ha-icon icon="mdi:pause-circle"></ha-icon>
            <span class="rain-delay-msg">
              <strong
<<<<<<< HEAD
                >${Oa("panels.zones.rain_delay.paused",e)}</strong
              >
              ${Oa("panels.zones.rain_delay.until",e)}
              ${Ja(t.toISOString())}
            </span>
            <button class="action-btn" @click="${()=>this._clearRainDelay()}">
              <ha-icon icon="mdi:play"></ha-icon>
              ${Oa("panels.zones.rain_delay.resume",e)}
=======
                >${Ma("panels.zones.rain_delay.paused",e)}</strong
              >
              ${Ma("panels.zones.rain_delay.until",e)}
              ${en(t.toISOString())}
            </span>
            <button class="action-btn" @click="${()=>this._clearRainDelay()}">
              <ha-icon icon="mdi:play"></ha-icon>
              ${Ma("panels.zones.rain_delay.resume",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </button>
          </div>
        </ha-card>
      `:W`
      <div class="rain-delay-row">
        <span class="rain-delay-label">
          <ha-icon icon="mdi:weather-rainy"></ha-icon>
<<<<<<< HEAD
          ${Oa("panels.zones.rain_delay.title",e)}
        </span>
        <button class="action-btn" @click="${()=>this._setRainDelay(24)}">
          ${Oa("panels.zones.rain_delay.delay_24h",e)}
        </button>
        <button class="action-btn" @click="${()=>this._setRainDelay(48)}">
          ${Oa("panels.zones.rain_delay.delay_48h",e)}
        </button>
      </div>
    `}_renderLastRunLine(e){const t=this.hass.language,i=function(e,t){const i=Ya(e).getTime()-Date.now(),s=new Intl.RelativeTimeFormat(t,{numeric:"auto"}),a=Math.round(i/1e3);if(Math.abs(a)<60)return s.format(a,"second");const n=Math.round(a/60);if(Math.abs(n)<60)return s.format(n,"minute");const o=Math.round(n/60);if(Math.abs(o)<24)return s.format(o,"hour");const r=Math.round(o/24);if(Math.abs(r)<30)return s.format(r,"day");const l=Math.round(r/30);return Math.abs(l)<12?s.format(l,"month"):s.format(Math.round(l/12),"year")}(e.timestamp,t),s=e.checks.filter(e=>e.enabled&&e.would_skip).map(e=>this._guardLabel(e).toLowerCase()).join(", "),a=e.would_skip?`${Oa("panels.zones.outlook.last_run_skipped",t)}${s?` (${s})`:""}`:Oa("panels.zones.outlook.last_run_ran",t);return W`
      <div class="outlook-line outlook-last">
        <span class="outlook-dim"
          >${Oa("panels.zones.outlook.last_run",t)}:</span
=======
          ${Ma("panels.zones.rain_delay.title",e)}
        </span>
        <button class="action-btn" @click="${()=>this._setRainDelay(24)}">
          ${Ma("panels.zones.rain_delay.delay_24h",e)}
        </button>
        <button class="action-btn" @click="${()=>this._setRainDelay(48)}">
          ${Ma("panels.zones.rain_delay.delay_48h",e)}
        </button>
      </div>
    `}_renderLastRunLine(e){const t=this.hass.language,s=function(e,t){const s=Ja(e).getTime()-Date.now(),i=new Intl.RelativeTimeFormat(t,{numeric:"auto"}),a=Math.round(s/1e3);if(Math.abs(a)<60)return i.format(a,"second");const n=Math.round(a/60);if(Math.abs(n)<60)return i.format(n,"minute");const o=Math.round(n/60);if(Math.abs(o)<24)return i.format(o,"hour");const r=Math.round(o/24);if(Math.abs(r)<30)return i.format(r,"day");const l=Math.round(r/30);return Math.abs(l)<12?i.format(l,"month"):i.format(Math.round(l/12),"year")}(e.timestamp,t),i=e.checks.filter(e=>e.enabled&&e.would_skip).map(e=>this._guardLabel(e).toLowerCase()).join(", "),a=e.would_skip?`${Ma("panels.zones.outlook.last_run_skipped",t)}${i?` (${i})`:""}`:Ma("panels.zones.outlook.last_run_ran",t);return W`
      <div class="outlook-line outlook-last">
        <span class="outlook-dim"
          >${Ma("panels.zones.outlook.last_run",t)}:</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <span>${a} · ${i}</span>
      </div>
<<<<<<< HEAD
    `}_renderZoneDecision(e){var t;if(!this.hass)return W``;const i=this.hass.language,s=null!==(t=e.duration)&&void 0!==t?t:0;let a,n,o,r;if(e.state===Wa.Disabled)a=Oa("panels.zones.status.decision_disabled",i),n="neutral",o="mdi:power-off";else if(e.last_calculated)if(this._zoneHasDeficit(e)){const t=La(s),l=this._triggeredGuards,d=this._nextIrrigateRunForZone(e);l.length>0?(a=Oa("panels.zones.status.decision_water_skip",i,"{duration}",t,"{reason}",this._guardLabel(l[0]).toLowerCase()),n="skip",o="mdi:weather-rainy"):d&&d.next_run_utc?(a=Oa("panels.zones.status.decision_water_at",i,"{duration}",t,"{time}",this._formatRunTime(d.next_run_utc)),n="water",o="mdi:water",r=d):(a=Oa("panels.zones.status.decision_water_no_schedule",i,"{duration}",t),n="water",o="mdi:water-alert")}else a=Oa("panels.zones.status.decision_no_water",i),n="ok",o="mdi:check-circle-outline";else a=Oa("panels.zones.status.decision_unknown",i),n="unknown",o="mdi:help-circle-outline";return W`
=======
    `}_renderZoneDecision(e){var t;if(!this.hass)return W``;const s=this.hass.language,i=null!==(t=e.duration)&&void 0!==t?t:0;let a,n,o,r;if(e.state===Ga.Disabled)a=Ma("panels.zones.status.decision_disabled",s),n="neutral",o="mdi:power-off";else if(e.last_calculated)if(this._zoneHasDeficit(e)){const t=Ba(i),l=this._triggeredGuards,d=this._nextIrrigateRunForZone(e);l.length>0?(a=Ma("panels.zones.status.decision_water_skip",s,"{duration}",t,"{reason}",this._guardLabel(l[0]).toLowerCase()),n="skip",o="mdi:weather-rainy"):d&&d.next_run_utc?(a=Ma("panels.zones.status.decision_water_at",s,"{duration}",t,"{time}",this._formatRunTime(d.next_run_utc)),n="water",o="mdi:water",r=d):(a=Ma("panels.zones.status.decision_water_no_schedule",s,"{duration}",t),n="water",o="mdi:water-alert")}else a=Ma("panels.zones.status.decision_no_water",s),n="ok",o="mdi:check-circle-outline";else a=Ma("panels.zones.status.decision_unknown",s),n="unknown",o="mdi:help-circle-outline";return W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      <div class="zone-decision ${n}">
        <ha-icon icon="${o}"></ha-icon>
        <span>${a}</span>
        ${r?this._renderEstimatedTag(r):""}
      </div>
<<<<<<< HEAD
    `}_zoneEstimate(e){var t,i;if(void 0!==e.id)return null===(i=null===(t=this._outlook)||void 0===t?void 0:t.zone_estimates)||void 0===i?void 0:i[String(e.id)]}_zoneFault(e){var t,i;if(void 0!==e.id)return null===(i=null===(t=this._outlook)||void 0===t?void 0:t.zone_faults)||void 0===i?void 0:i[String(e.id)]}_renderZoneFault(e){if(!this.hass)return W``;const t=this._zoneFault(e);if(!t)return W``;const i=this.hass.language,s=Oa(`panels.zones.fault.${t.reason}`,i)||Oa("panels.zones.fault.generic",i),a=t.timestamp?Ja(t.timestamp):"";return W`
      <div class="zone-fault" title="${a}">
        <ha-icon icon="mdi:alert-circle"></ha-icon>
        <span>
          <strong>${Oa("panels.zones.fault.title",i)}</strong>
          — ${s}
        </span>
      </div>
    `}_zoneSkip(e){var t,i;if(void 0!==e.id)return null===(i=null===(t=this._outlook)||void 0===t?void 0:t.zone_skips)||void 0===i?void 0:i[String(e.id)]}_renderZoneSkip(e){if(!this.hass)return W``;const t=this._zoneSkip(e);if(!t)return W``;const i=this.hass.language,s=Oa("panels.zones.skip.soil_moisture",i,"{observed}",String(t.observed),"{threshold}",String(t.threshold)),a=t.timestamp?Ja(t.timestamp):"";return W`
      <div class="zone-skip" title="${a}">
        <ha-icon icon="mdi:water-off"></ha-icon>
        <span>
          <strong>${Oa("panels.zones.skip.title",i)}</strong>
          — ${s}
        </span>
      </div>
    `}_durationClamped(e){var t,i;if(e.state!==Wa.Automatic)return!1;const s=e.maximum_duration;if(null==s||s<0)return!1;const a=null!==(t=e.duration)&&void 0!==t?t:0;return!(a<=0)&&a-(null!==(i=e.lead_time)&&void 0!==i?i:0)>=s}_renderDurationClamped(e){var t;if(!this.hass||!this._durationClamped(e))return W``;const i=this.hass.language,s=Oa("panels.zones.clamped.detail",i,"{maximum}",La(null!==(t=e.maximum_duration)&&void 0!==t?t:0));return W`
      <div class="zone-clamped" title="${s}">
        <ha-icon icon="mdi:timer-alert-outline"></ha-icon>
        <span>
          <strong>${Oa("panels.zones.clamped.title",i)}</strong>
=======
    `}_zoneEstimate(e){var t,s;if(void 0!==e.id)return null===(s=null===(t=this._outlook)||void 0===t?void 0:t.zone_estimates)||void 0===s?void 0:s[String(e.id)]}_zoneFault(e){var t,s;if(void 0!==e.id)return null===(s=null===(t=this._outlook)||void 0===t?void 0:t.zone_faults)||void 0===s?void 0:s[String(e.id)]}_renderZoneFault(e){if(!this.hass)return W``;const t=this._zoneFault(e);if(!t)return W``;const s=this.hass.language,i=Ma(`panels.zones.fault.${t.reason}`,s)||Ma("panels.zones.fault.generic",s),a=t.timestamp?en(t.timestamp):"";return W`
      <div class="zone-fault" title="${a}">
        <ha-icon icon="mdi:alert-circle"></ha-icon>
        <span>
          <strong>${Ma("panels.zones.fault.title",s)}</strong>
          — ${i}
        </span>
      </div>
    `}_zoneSkip(e){var t,s;if(void 0!==e.id)return null===(s=null===(t=this._outlook)||void 0===t?void 0:t.zone_skips)||void 0===s?void 0:s[String(e.id)]}_renderZoneSkip(e){if(!this.hass)return W``;const t=this._zoneSkip(e);if(!t)return W``;const s=this.hass.language,i=Ma("panels.zones.skip.soil_moisture",s,"{observed}",String(t.observed),"{threshold}",String(t.threshold)),a=t.timestamp?en(t.timestamp):"";return W`
      <div class="zone-skip" title="${a}">
        <ha-icon icon="mdi:water-off"></ha-icon>
        <span>
          <strong>${Ma("panels.zones.skip.title",s)}</strong>
          — ${i}
        </span>
      </div>
    `}_durationClamped(e){var t,s;if(e.state!==Ga.Automatic)return!1;const i=e.maximum_duration;if(null==i||i<0)return!1;const a=null!==(t=e.duration)&&void 0!==t?t:0;return!(a<=0)&&a-(null!==(s=e.lead_time)&&void 0!==s?s:0)>=i}_renderDurationClamped(e){var t;if(!this.hass||!this._durationClamped(e))return W``;const s=this.hass.language,i=Ma("panels.zones.clamped.detail",s,"{maximum}",Ba(null!==(t=e.maximum_duration)&&void 0!==t?t:0));return W`
      <div class="zone-clamped" title="${i}">
        <ha-icon icon="mdi:timer-alert-outline"></ha-icon>
        <span>
          <strong>${Ma("panels.zones.clamped.title",s)}</strong>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          <ha-icon
            class="clamped-hint"
            icon="mdi:information-outline"
          ></ha-icon>
        </span>
      </div>
<<<<<<< HEAD
    `}_renderZoneEstimate(e){if(!this.hass)return W``;const t=this._zoneEstimate(e);if(!t||!t.available||null==t.live_deficit)return W``;const i=this.hass.language,s=Ma(this.config,bt),a=t.live_deficit<0?"var(--warning-color)":"var(--success-color)",n=Oa(`panels.zones.status.estimate_method.${"proxy"===t.method||"hourly_sensor"===t.method?t.method:"hourly"}`,i)+(t.as_of?` · ${Xa(t.as_of)}`:"");return W`
      <span class="status-sep">·</span>
      <span class="zone-estimate" title="${n}">
        ${Oa("panels.zones.status.estimate_now",i)}
=======
    `}_renderZoneEstimate(e){if(!this.hass)return W``;const t=this._zoneEstimate(e);if(!t||!t.available||null==t.live_deficit)return W``;const s=this.hass.language,i=Na(this.config,bt),a=t.live_deficit<0?"var(--warning-color)":"var(--success-color)",n=Ma(`panels.zones.status.estimate_method.${"proxy"===t.method||"hourly_sensor"===t.method?t.method:"hourly"}`,s)+(t.as_of?` · ${Qa(t.as_of)}`:"");return W`
      <span class="status-sep">·</span>
      <span class="zone-estimate" title="${n}">
        ${Ma("panels.zones.status.estimate_now",s)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        <strong style="color: ${a}"
          >≈ ${t.live_deficit.toFixed(2)} ${s}</strong
        >
        <span class="estimate-tag"
<<<<<<< HEAD
          >${Oa("panels.zones.status.estimate_tag",i)}</span
=======
          >${Ma("panels.zones.status.estimate_tag",s)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
      </span>
    `}_renderZoneNextRun(e){if(!this.hass)return W``;const t=this._nextIrrigateRunForZone(e);if(!t||!t.next_run_utc)return W``;return e.state!==Wa.Disabled&&e.last_calculated&&this._zoneHasDeficit(e)&&0===this._triggeredGuards.length?W``:W`
      <span class="status-sep">·</span>
      <span>
<<<<<<< HEAD
        ${Oa("panels.zones.outlook.next_run",this.hass.language)}:
        <strong>${this._formatRunTime(t.next_run_utc)}</strong>
        ${this._renderEstimatedTag(t)}
      </span>
    `}renderZone(e,t){var i;if(!this.hass)return W``;const s=Number(null!==(i=e.bucket)&&void 0!==i?i:0),a=s<0?"var(--warning-color)":"var(--success-color)",n=e.state===Wa.Automatic?"state-automatic":e.state===Wa.Manual?"state-manual":"state-disabled",o=e.last_calculated?Ja(e.last_calculated):Oa("panels.zones.status.never",this.hass.language);return W`
=======
        ${Ma("panels.zones.outlook.next_run",this.hass.language)}:
        <strong>${this._formatRunTime(t.next_run_utc)}</strong>
        ${this._renderEstimatedTag(t)}
      </span>
    `}renderZone(e,t){var s;if(!this.hass)return W``;const i=Number(null!==(s=e.bucket)&&void 0!==s?s:0),a=i<0?"var(--warning-color)":"var(--success-color)",n=e.state===Ga.Automatic?"state-automatic":e.state===Ga.Manual?"state-manual":"state-disabled",o=e.last_calculated?en(e.last_calculated):Ma("panels.zones.status.never",this.hass.language);return W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          <span class="zone-state-badge ${n}">
<<<<<<< HEAD
            ${Oa(`panels.zones.labels.states.${e.state}`,this.hass.language)}
=======
            ${Ma(`panels.zones.labels.states.${e.state}`,this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </span>
          ${this.hideSettingsLinks?"":W`
                <ha-icon-button
                  .path="${"M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"}"
<<<<<<< HEAD
                  title="${Oa("panels.zones.actions.open_settings",this.hass.language)}"
=======
                  title="${Ma("panels.zones.actions.open_settings",this.hass.language)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  @click="${()=>this._openZoneSettings(e)}"
                ></ha-icon-button>
              `}
        </div>

        <!-- RUN FAULT (e.g. valve didn't open) -->
        ${this._renderZoneFault(e)}

        <!-- SOIL-MOISTURE SKIP (wet-veto) -->
        ${this._renderZoneSkip(e)}

        <!-- DURATION CUT BY maximum_duration -->
        ${this._renderDurationClamped(e)}

        <!-- AT-A-GLANCE DECISION -->
        ${this._renderZoneDecision(e)}

        <!-- COMPACT STATUS -->
        <div class="card-content">
          <div class="zone-status-line">
            <span
<<<<<<< HEAD
              title="${Oa("panels.zones.help.bucket",this.hass.language)}"
            >
              ${Oa("panels.zones.labels.bucket",this.hass.language)}:
=======
              title="${Ma("panels.zones.help.bucket",this.hass.language)}"
            >
              ${Ma("panels.zones.labels.bucket",this.hass.language)}:
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              <strong style="color: ${a}"
                >${s.toFixed(2)}
                ${Ma(this.config,bt)}</strong
              >
            </span>
            <span class="status-sep">·</span>
            <span>
<<<<<<< HEAD
              ${Oa("panels.zones.status.last_checked",this.hass.language)}:
=======
              ${Ma("panels.zones.status.last_checked",this.hass.language)}:
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              <strong>${o}</strong>
            </span>
            ${this._renderZoneEstimate(e)} ${this._renderZoneNextRun(e)}
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div class="card-content zone-action-bar">
          ${"full"===this.actionsMode&&e.state===Wa.Automatic?W`
                <button
                  class="action-btn"
<<<<<<< HEAD
                  title="${Oa("panels.zones.help.update",this.hass.language)}"
=======
                  title="${Ma("panels.zones.help.update",this.hass.language)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  @click="${()=>this.handleUpdateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
<<<<<<< HEAD
                  ${Oa("panels.zones.actions.update",this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${Oa("panels.zones.help.calculate",this.hass.language)}"
=======
                  ${Ma("panels.zones.actions.update",this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${Ma("panels.zones.help.calculate",this.hass.language)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  @click="${()=>this.handleCalculateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
<<<<<<< HEAD
                  ${Oa("panels.zones.actions.calculate",this.hass.language)}
=======
                  ${Ma("panels.zones.actions.calculate",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
              `:""}
          ${"none"!==this.actionsMode&&this._canActuate(e)&&this._zoneHasDeficit(e)?W`
                <button
                  class="action-btn"
                  raised
                  @click="${()=>{void 0!==e.id&&(this._confirmIrrigate=e.id.toString())}}"
                  ?disabled="${this.isSaving||this._distributorBusy(e)}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
<<<<<<< HEAD
                  ${Oa("panels.zones.labels.irrigate_now",this.hass.language)}
=======
                  ${Ma("panels.zones.labels.irrigate_now",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
              `:this._canActuate(e)?"":W`
                  <button
                    class="action-btn"
                    disabled
<<<<<<< HEAD
                    title="${Oa("panels.zones.help.irrigate_link_entity",this.hass.language)}"
                  >
                    <ha-icon icon="mdi:water"></ha-icon>
                    ${Oa("panels.zones.labels.irrigate_now",this.hass.language)}
                  </button>
                  <span class="zones-top-note">
                    ${Oa("panels.zones.help.irrigate_link_entity",this.hass.language)}
=======
                    title="${Ma("panels.zones.help.irrigate_link_entity",this.hass.language)}"
                  >
                    <ha-icon icon="mdi:water"></ha-icon>
                    ${Ma("panels.zones.labels.irrigate_now",this.hass.language)}
                  </button>
                  <span class="zones-top-note">
                    ${Ma("panels.zones.help.irrigate_link_entity",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </span>
                `}
          ${this._renderRunZoneControl(e)}
        </div>
      </ha-card>
    `}_renderRunZoneControl(e){if(!this.hass||"none"===this.actionsMode||!this._canActuate(e)||void 0===e.id)return W``;const t=this.hass.language,i=String(e.id),s=this._activeRun(e);if(s){const i=this._runSecondsLeft(s);return W`
        <div class="run-zone-control running">
          <span class="run-zone-countdown">
            <ha-icon icon="mdi:water-pump"></ha-icon>
<<<<<<< HEAD
            ${null===i?Oa("panels.zones.stop_zone.watering",t):this._formatCountdown(i)}
=======
            ${null===s?Ma("panels.zones.stop_zone.watering",t):this._formatCountdown(s)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </span>
          <button
            class="action-btn stop-btn"
            @click="${()=>this._stopZone(e)}"
          >
            <ha-icon icon="mdi:stop"></ha-icon>
<<<<<<< HEAD
            ${Oa("panels.zones.stop_zone.stop",t)}
=======
            ${Ma("panels.zones.stop_zone.stop",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </button>
        </div>
      `}const a=this._distributorBusy(e);return W`
      <div class="run-zone-control-wrap">
        <div
          class="run-zone-control"
<<<<<<< HEAD
          title="${Oa("panels.zones.run_zone.help",t)}"
=======
          title="${Ma("panels.zones.run_zone.help",t)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
          <input
            class="run-zone-input"
            type="number"
            min="1"
            max="600"
            .value="${String(this._zoneRunMinutes(e))}"
            ?disabled="${a}"
            @input="${e=>{const t=Number(e.target.value);this._runMinutes=Object.assign(Object.assign({},this._runMinutes),{[i]:t})}}"
          />
          <span class="run-zone-unit"
<<<<<<< HEAD
            >${Oa("panels.zones.run_zone.minutes",t)}</span
=======
            >${Ma("panels.zones.run_zone.minutes",t)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          >
          <button
            class="action-btn"
            @click="${()=>this._runZoneFor(e)}"
            ?disabled="${this.isSaving||a}"
          >
            <ha-icon icon="mdi:timer-play-outline"></ha-icon>
<<<<<<< HEAD
            ${Oa("panels.zones.run_zone.run",t)}
          </button>
        </div>
        ${a?W`<span class="run-zone-busy-hint">
              ${Oa("panels.zones.run_zone.busy_hint",t)}
            </span>`:""}
      </div>
    `}_formatCountdown(e){const t=Math.max(0,e),i=Math.floor(t/3600),s=Math.floor(t%3600/60),a=t%60,n=e=>String(e).padStart(2,"0");return i>0?`${i}:${n(s)}:${n(a)}`:`${s}:${n(a)}`}render(){var e,t;if(!this.hass)return W``;if(this.isLoading)return W`
        <ha-card header="${Oa("panels.zones.title",this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Oa("common.loading-messages.general",this.hass.language)}
=======
            ${Ma("panels.zones.run_zone.run",t)}
          </button>
        </div>
        ${a?W`<span class="run-zone-busy-hint">
              ${Ma("panels.zones.run_zone.busy_hint",t)}
            </span>`:""}
      </div>
    `}_formatCountdown(e){const t=Math.max(0,e),s=Math.floor(t/3600),i=Math.floor(t%3600/60),a=t%60,n=e=>String(e).padStart(2,"0");return s>0?`${s}:${n(i)}:${n(a)}`:`${i}:${n(a)}`}render(){var e,t;if(!this.hass)return W``;if(this.isLoading)return W`
        <ha-card header="${Ma("panels.zones.title",this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Ma("common.loading-messages.general",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </div>
          </div>
        </ha-card>
      `;const i=this.zones.some(e=>{var t;return this._canActuate(e)&&(null!==(t=e.duration)&&void 0!==t?t:0)>0}),s=0===this.zones.length;return W`
      ${s?this.hideSettingsLinks?W`
              <ha-card>
                <div class="card-content description-text">
<<<<<<< HEAD
                  ${Oa("panels.zones.no_items",this.hass.language)}
=======
                  ${Ma("panels.zones.no_items",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </div>
              </ha-card>
            `:W`
              <ha-card class="setup-banner-card">
                <div class="setup-banner">
                  <div class="setup-banner-icon">🌱</div>
                  <div class="setup-banner-content">
                    <div class="setup-banner-title">
<<<<<<< HEAD
                      ${Oa("wizard.title",this.hass.language)}
                    </div>
                    <div class="setup-banner-desc">
                      ${Oa("wizard.setup_complete_banner",this.hass.language)}
=======
                      ${Ma("wizard.title",this.hass.language)}
                    </div>
                    <div class="setup-banner-desc">
                      ${Ma("wizard.setup_complete_banner",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    </div>
                  </div>
                  <button
                    class="action-btn setup-banner-btn"
                    @click="${()=>{this.dispatchEvent(new CustomEvent("open-wizard",{bubbles:!0,composed:!0}))}}"
                  >
<<<<<<< HEAD
                    ${Oa("wizard.open_wizard",this.hass.language)}
=======
                    ${Ma("wizard.open_wizard",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </button>
                </div>
              </ha-card>
            `:""}
      ${s?"":this._renderOutlookBanner()}
      ${s?"":this._renderRainDelay()}

      <!-- Zones header card: run-all operational actions -->
      <ha-card>
        <div class="card-header">
          <div class="name">
<<<<<<< HEAD
            ${Oa("panels.zones.title",this.hass.language)}
=======
            ${Ma("panels.zones.title",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </div>
        </div>
        <div class="card-content zones-top-actions">
          ${"full"===this.actionsMode?W`
                <button
                  class="action-btn"
<<<<<<< HEAD
                  title="${Oa("panels.zones.help.update_all",this.hass.language)}"
=======
                  title="${Ma("panels.zones.help.update_all",this.hass.language)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  @click="${this.handleUpdateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
<<<<<<< HEAD
                  ${Oa("panels.zones.cards.zone-actions.actions.update-all",this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${Oa("panels.zones.help.calculate_all",this.hass.language)}"
=======
                  ${Ma("panels.zones.cards.zone-actions.actions.update-all",this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${Ma("panels.zones.help.calculate_all",this.hass.language)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  @click="${this.handleCalculateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
<<<<<<< HEAD
                  ${Oa("panels.zones.cards.zone-actions.actions.calculate-all",this.hass.language)}
=======
                  ${Ma("panels.zones.cards.zone-actions.actions.calculate-all",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
              `:""}
          ${"none"!==this.actionsMode?W`
                <button
                  class="action-btn"
                  raised
<<<<<<< HEAD
                  title="${Oa("panels.zones.help.irrigate_all",this.hass.language)}"
=======
                  title="${Ma("panels.zones.help.irrigate_all",this.hass.language)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  @click="${()=>{this._confirmIrrigate="all"}}"
                  ?disabled="${!i||this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
<<<<<<< HEAD
                  ${Oa("panels.zones.actions.irrigate_all",this.hass.language)}
                </button>
              `:""}
          ${i?"":W`<span class="zones-top-note"
                >${Oa("panels.info.cards.irrigate_now.no_linked_zones",this.hass.language)}</span
=======
                  ${Ma("panels.zones.actions.irrigate_all",this.hass.language)}
                </button>
              `:""}
          ${s?"":W`<span class="zones-top-note"
                >${Ma("panels.info.cards.irrigate_now.no_linked_zones",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              >`}
        </div>
      </ha-card>

      <!-- Irrigate confirmation dialog -->
      ${null!==this._confirmIrrigate?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmIrrigate=null}}"
<<<<<<< HEAD
              heading="${Oa("panels.zones.confirm_irrigate.title",this.hass.language)}"
            >
              <p>
                ${Oa("panels.zones.confirm_irrigate.body",this.hass.language)}
              </p>
              <p>
                <strong>
                  ${"all"===this._confirmIrrigate?`${Oa("panels.zones.confirm_irrigate.all_linked_zones",this.hass.language)} (${this._linkedZoneCount})`:null!==(t=null===(e=this.zones.find(e=>{var t;return(null===(t=e.id)||void 0===t?void 0:t.toString())===this._confirmIrrigate}))||void 0===e?void 0:e.name)&&void 0!==t?t:this._confirmIrrigate}
=======
              heading="${Ma("panels.zones.confirm_irrigate.title",this.hass.language)}"
            >
              <p>
                ${Ma("panels.zones.confirm_irrigate.body",this.hass.language)}
              </p>
              <p>
                <strong>
                  ${"all"===this._confirmIrrigate?`${Ma("panels.zones.confirm_irrigate.all_linked_zones",this.hass.language)} (${this._linkedZoneCount})`:null!==(t=null===(e=this.zones.find(e=>{var t;return(null===(t=e.id)||void 0===t?void 0:t.toString())===this._confirmIrrigate}))||void 0===e?void 0:e.name)&&void 0!==t?t:this._confirmIrrigate}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </strong>
              </p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmIrrigate=null}}"
                >
<<<<<<< HEAD
                  ${Oa("common.actions.cancel",this.hass.language)}
=======
                  ${Ma("common.actions.cancel",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._doIrrigate}"
                >
<<<<<<< HEAD
                  ${Oa("panels.zones.labels.irrigate_now",this.hass.language)}
=======
                  ${Ma("panels.zones.labels.irrigate_now",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Operation error banner -->
      ${this._operationError?W`
            <ha-card class="error-banner-card">
              <div class="error-banner">
                <ha-icon
                  class="error-banner-icon"
                  icon="mdi:alert-circle-outline"
                ></ha-icon>
                <span class="error-banner-msg">${this._operationError}</span>
                <ha-icon-button
                  .path="${Ua}"
                  @click="${()=>{this._operationError=null}}"
<<<<<<< HEAD
                  aria-label="${Oa("common.actions.cancel",this.hass.language)}"
=======
                  aria-label="${Ma("common.actions.cancel",this.hass.language)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                ></ha-icon-button>
              </div>
            </ha-card>
          `:""}

      <!-- Zone cards -->
      ${this.zones.map((e,t)=>this.renderZone(e,t))}
    `}static get styles(){return r`
      ${Ka}

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

      /* Run fault — the strongest per-zone state (a run failed). */
      .zone-fault {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0 16px 12px;
        padding: 10px 12px;
        border-radius: 8px;
        font-size: 0.9rem;
        line-height: 1.35;
        background: rgba(244, 67, 54, 0.12);
        color: var(--error-color, #f44336);
        border-left: 4px solid var(--error-color, #f44336);
      }

      .zone-fault ha-icon {
        flex-shrink: 0;
        --mdc-icon-size: 22px;
      }

      /* Soil-moisture skip — informational, not an error. Same shape as the
         fault banner but a calm, muted blue tone (a skip is intended). */
      .zone-skip {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0 16px 12px;
        padding: 10px 12px;
        border-radius: 8px;
        font-size: 0.9rem;
        line-height: 1.35;
        background: rgba(var(--rgb-info-color, 3, 169, 244), 0.1);
        color: var(--info-color, var(--primary-color, #039be5));
        border-left: 4px solid var(--info-color, var(--primary-color, #039be5));
      }

      .zone-skip ha-icon {
        flex-shrink: 0;
        --mdc-icon-size: 22px;
      }

      /* Duration cut by maximum_duration — a standing configuration problem,
         so warning-tinted rather than informational like the wet-veto chip. */
      .zone-clamped {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0 16px 12px;
        padding: 10px 12px;
        border-radius: 8px;
        font-size: 0.9rem;
        line-height: 1.35;
        background: rgba(var(--rgb-warning-color, 237, 108, 2), 0.1);
        color: var(--warning-color, #ed6c02);
        border-left: 4px solid var(--warning-color, #ed6c02);
        cursor: help;
      }

      .zone-clamped ha-icon {
        flex-shrink: 0;
        --mdc-icon-size: 22px;
      }

      .zone-clamped span {
        display: inline-flex;
        align-items: center;
        gap: 4px;
      }

      /* The hint, not the warning's own icon: sized to the text so the banner
         still reads as one line rather than two competing symbols. */
      .zone-clamped ha-icon.clamped-hint {
        --mdc-icon-size: 16px;
        width: 16px;
        height: 16px;
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

      /* The marker carries an explanation on hover, so it needs to look like it
         has one: bare uppercase text reads as a label nobody would think to
         point at. Icon + cursor match how the rest of the panel signals help. */
      .estimate-tag {
        display: inline-flex;
        align-items: center;
        gap: 2px;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        opacity: 0.65;
        cursor: help;
      }

      .estimate-tag ha-icon {
        --mdc-icon-size: 14px;
        width: 14px;
        height: 14px;
      }

      /* Action bar */
      .zone-action-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding-top: 0;
        padding-bottom: 12px;
      }

      /* Custom-duration run control (WS-5) */
      .run-zone-control-wrap {
        display: inline-flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 4px;
        margin-left: auto;
      }

      .run-zone-control {
        display: inline-flex;
        align-items: center;
        gap: 6px;
      }

      /* The in-progress countdown branch isn't inside the wrap, so it keeps the
         right-alignment the wrap otherwise provides. */
      .run-zone-control.running {
        margin-left: auto;
      }

      /* Member busy-hint: the distributor is mid-cycle, so the run is blocked. */
      .run-zone-busy-hint {
        font-size: 0.8125rem;
        font-style: italic;
        color: var(--secondary-text-color);
        text-align: right;
        max-width: 320px;
        line-height: 1.3;
      }

      .run-zone-input {
        width: 56px;
        padding: 6px 8px;
        border: 1px solid var(--divider-color);
        border-radius: 6px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        font: inherit;
        text-align: right;
      }

      .run-zone-unit {
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
      }

      /* In-progress run: countdown + Stop */
      .run-zone-countdown {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-variant-numeric: tabular-nums;
        font-weight: 600;
        color: var(--primary-color);
      }

      .run-zone-countdown ha-icon {
        --mdc-icon-size: 18px;
      }

      .action-btn.stop-btn {
        color: var(--error-color, #db4437);
        border-color: var(--error-color, #db4437);
      }

      /* Rain delay / vacation hold (WS-5) */
      .rain-delay-card.paused {
        border-left: 4px solid var(--warning-color, #ed6c02);
        background: rgba(255, 152, 0, 0.08);
      }

      .rain-delay {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        padding: 12px 16px;
      }

      .rain-delay ha-icon {
        flex-shrink: 0;
        color: var(--warning-color, #ed6c02);
        --mdc-icon-size: 22px;
      }

      .rain-delay-msg {
        flex: 1;
        font-size: 0.9rem;
        line-height: 1.35;
      }

      .rain-delay-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin: 0 4px 4px;
        padding: 4px 0;
      }

      .rain-delay-label {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
      }

      .rain-delay-label ha-icon {
        --mdc-icon-size: 18px;
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
    `}}t([me()],en.prototype,"config",void 0),t([me({type:Boolean})],en.prototype,"hideSettingsLinks",void 0),t([me({attribute:!1})],en.prototype,"actionsMode",void 0),t([me({type:Array})],en.prototype,"zones",void 0),t([ve()],en.prototype,"_outlook",void 0),t([ve()],en.prototype,"_distributors",void 0),t([me({type:Boolean})],en.prototype,"isLoading",void 0),t([me({type:Boolean})],en.prototype,"isSaving",void 0),t([ve()],en.prototype,"_operationError",void 0),t([ve()],en.prototype,"_confirmIrrigate",void 0),t([ve()],en.prototype,"_skipDetailsOpen",void 0),t([ve()],en.prototype,"_runMinutes",void 0),t([ve()],en.prototype,"_now",void 0),customElements.get("smart-irrigation-view-zones")||customElements.define("smart-irrigation-view-zones",en)
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */;const tn={},sn=Xi(class extends Ji{constructor(e){if(super(e),e.type!==Vi&&e.type!==Gi&&e.type!==Yi)throw Error("The `live` directive is not allowed on child or event bindings");if(!(e=>void 0===e.strings)(e))throw Error("`live` bindings can only contain a single expression")}render(e){return e}update(e,[t]){if(t===G||t===K)return t;const i=e.element,s=e.name;if(e.type===Vi){if(t===i[s])return G}else if(e.type===Yi){if(!!t===i.hasAttribute(s))return G}else if(e.type===Gi&&i.getAttribute(s)===t+"")return G;return((e,t=tn)=>{e._$AH=t;
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */})(e),t}});let an=class extends ce{constructor(){super(...arguments),this.label="",this.unit="",this.help="",this.required=!1,this._helpOpen=!1}_toggleHelp(){this._helpOpen=!this._helpOpen}render(){return W`
      <div class="si-field">
        <div class="si-field-header">
          <span class="si-field-label">
            ${this.label}${this.required?W`<span class="si-field-required" aria-label="required">
                  *</span
                >`:""}
          </span>
          <span class="si-field-meta">
            ${this.unit?W`<span class="si-field-unit">${this.unit}</span>`:""}
            ${this.help?W`
                  <button
                    class="si-field-help-btn ${this._helpOpen?"open":""}"
                    type="button"
                    aria-label="Toggle help"
                    @click="${this._toggleHelp}"
                  >
                    ⓘ
                  </button>
                `:""}
          </span>
        </div>
        <slot></slot>
        ${this._helpOpen&&this.help?W`<div class="si-field-help-text">${this.help}</div>`:""}
      </div>
    `}static get styles(){return r`
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
<<<<<<< HEAD
    `}};t([me()],an.prototype,"label",void 0),t([me()],an.prototype,"unit",void 0),t([me()],an.prototype,"help",void 0),t([me({type:Boolean})],an.prototype,"required",void 0),t([ve()],an.prototype,"_helpOpen",void 0),an=t([ue("si-field")],an);let nn=class extends ce{constructor(){super(...arguments),this.useWeather=!1,this.service=Ae,this.apiKey="",this.weatherConfig=null,this._testing=!1,this._testResult=null,this._testResultTimer=null}disconnectedCallback(){super.disconnectedCallback(),this._testResultTimer&&(clearTimeout(this._testResultTimer),this._testResultTimer=null)}_emit(e,t){this.dispatchEvent(new CustomEvent(e,{detail:{value:t},bubbles:!0,composed:!0}))}get _noApiKeyServices(){var e,t;return null!==(t=null===(e=this.weatherConfig)||void 0===e?void 0:e.no_api_key_services)&&void 0!==t?t:[Ae]}get _needsKey(){return this.useWeather&&!!this.service&&!this._noApiKeyServices.includes(this.service)}get _hasStoredKey(){const e=this.weatherConfig;return this.service===ze?!!(null==e?void 0:e.has_owm_api_key):this.service===Se?!!(null==e?void 0:e.has_pw_api_key):this.service===Ee&&!!(null==e?void 0:e.has_met_api_key)}async _testApiKey(){if(this.hass&&!this._testing){this._testing=!0,this._testResult=null,this._testResultTimer&&(clearTimeout(this._testResultTimer),this._testResultTimer=null);try{this._testResult=await(e=this.hass,t=this.service,i=this.apiKey||null,e.callWS({type:be+"/weather_config_test",weather_service:null!=t?t:null,api_key:null!=i?i:null})),this._testResultTimer=window.setTimeout(()=>{this._testResult=null,this._testResultTimer=null},12e3)}catch(e){this._testResult={success:!1,error:"unknown"}}finally{this._testing=!1}var e,t,i}}render(){var e,t;const i=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";return W`
      <si-field
        label="${Oa("weather_service_config.enabled_label",i)}"
=======
    `}};t([me()],on.prototype,"label",void 0),t([me()],on.prototype,"unit",void 0),t([me()],on.prototype,"help",void 0),t([me({type:Boolean})],on.prototype,"required",void 0),t([ve()],on.prototype,"_helpOpen",void 0),on=t([ue("si-field")],on);let rn=class extends ce{constructor(){super(...arguments),this.useWeather=!1,this.service=Ae,this.apiKey="",this.weatherConfig=null,this._testing=!1,this._testResult=null,this._testResultTimer=null}disconnectedCallback(){super.disconnectedCallback(),this._testResultTimer&&(clearTimeout(this._testResultTimer),this._testResultTimer=null)}_emit(e,t){this.dispatchEvent(new CustomEvent(e,{detail:{value:t},bubbles:!0,composed:!0}))}get _noApiKeyServices(){var e,t;return null!==(t=null===(e=this.weatherConfig)||void 0===e?void 0:e.no_api_key_services)&&void 0!==t?t:[Ae]}get _needsKey(){return this.useWeather&&!!this.service&&!this._noApiKeyServices.includes(this.service)}get _hasStoredKey(){const e=this.weatherConfig;return this.service===ze?!!(null==e?void 0:e.has_owm_api_key):this.service===Se?!!(null==e?void 0:e.has_pw_api_key):this.service===Ce&&!!(null==e?void 0:e.has_met_api_key)}async _testApiKey(){if(this.hass&&!this._testing){this._testing=!0,this._testResult=null,this._testResultTimer&&(clearTimeout(this._testResultTimer),this._testResultTimer=null);try{this._testResult=await(e=this.hass,t=this.service,s=this.apiKey||null,e.callWS({type:be+"/weather_config_test",weather_service:null!=t?t:null,api_key:null!=s?s:null})),this._testResultTimer=window.setTimeout(()=>{this._testResult=null,this._testResultTimer=null},12e3)}catch(e){this._testResult={success:!1,error:"unknown"}}finally{this._testing=!1}var e,t,s}}render(){var e,t;const s=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";return W`
      <si-field
        label="${Ma("weather_service_config.enabled_label",s)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      >
        <ha-switch
          .checked="${this.useWeather}"
          @change="${e=>this._emit("useweather-changed",e.target.checked)}"
        ></ha-switch>
      </si-field>

      ${this.useWeather?this._renderServiceAndKey(i):""}
    `}_renderServiceAndKey(e){return W`
      <si-field
<<<<<<< HEAD
        label="${Oa("weather_service_config.service_label",e)}"
=======
        label="${Ma("weather_service_config.service_label",e)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      >
        <select
          class="si-input"
          .value="${sn(this.service||Ae)}"
          @change="${e=>{this._testResult=null,this._emit("service-changed",e.target.value)}}"
        >
          <option
            value="${Ae}"
            ?selected="${(this.service||Ae)===Ae}"
          >
<<<<<<< HEAD
            ${Oa("weather_service_config.openmeteo",e)}
=======
            ${Ma("weather_service_config.openmeteo",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </option>
          <option
            value="${ze}"
            ?selected="${this.service===ze}"
          >
<<<<<<< HEAD
            ${Oa("weather_service_config.owm",e)}
=======
            ${Ma("weather_service_config.owm",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </option>
          <option
            value="${Se}"
            ?selected="${this.service===Se}"
          >
<<<<<<< HEAD
            ${Oa("weather_service_config.pw",e)}
=======
            ${Ma("weather_service_config.pw",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </option>
          <option
            value="${Ce}"
            ?selected="${this.service===Ce}"
          >
<<<<<<< HEAD
            ${Oa("weather_service_config.met",e)}
=======
            ${Ma("weather_service_config.met",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </option>
        </select>
      </si-field>

      ${this._needsKey?this._renderKeyField(e):W`<div class="info-note">
<<<<<<< HEAD
            ${Oa("weather_service_config.no_api_key_needed",e)}
=======
            ${Ma("weather_service_config.no_api_key_needed",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </div>`}
    `}_renderKeyField(e){var t;const i=this._hasStoredKey;return W`
      <si-field
<<<<<<< HEAD
        label="${Oa("weather_service_config.api_key_label",e)}"
        help="${Oa("weather_service_config.api_key_help",e)}"
      >
        <span class="api-badge ${i?"configured":"missing"}"
          >${Oa(i?"weather_service_config.api_key_configured":"weather_service_config.api_key_not_configured",e)}</span
=======
        label="${Ma("weather_service_config.api_key_label",e)}"
        help="${Ma("weather_service_config.api_key_help",e)}"
      >
        <span class="api-badge ${s?"configured":"missing"}"
          >${Ma(s?"weather_service_config.api_key_configured":"weather_service_config.api_key_not_configured",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <div class="api-row">
          <input
            type="password"
            class="si-input flex1"
<<<<<<< HEAD
            placeholder="${Oa("weather_service_config.api_key_placeholder",e)}"
=======
            placeholder="${Ma("weather_service_config.api_key_placeholder",e)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            .value="${this.apiKey}"
            @input="${e=>{this._testResult=null,this._emit("apikey-changed",e.target.value)}}"
          />
          <button
            class="test-btn"
            type="button"
            ?disabled="${this._testing||!this.apiKey&&!i}"
            @click="${this._testApiKey}"
          >
<<<<<<< HEAD
            ${this._testing?Oa("weather_service_config.test_button_testing",e):Oa("weather_service_config.test_button",e)}
=======
            ${this._testing?Ma("weather_service_config.test_button_testing",e):Ma("weather_service_config.test_button",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </button>
        </div>
        ${null!==this._testResult?W`<div
              class="test-result ${this._testResult.success?"success":"error"}"
            >
<<<<<<< HEAD
              ${this._testResult.success?Oa("weather_service_config.test_success",e):Oa("weather_service_config.test_error_"+(null!==(t=this._testResult.error)&&void 0!==t?t:"unknown"),e)}
=======
              ${this._testResult.success?Ma("weather_service_config.test_success",e):Ma("weather_service_config.test_error_"+(null!==(t=this._testResult.error)&&void 0!==t?t:"unknown"),e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </div>`:""}
      </si-field>
    `}static get styles(){return r`
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
<<<<<<< HEAD
    `}};t([me({attribute:!1})],nn.prototype,"hass",void 0),t([me({type:Boolean})],nn.prototype,"useWeather",void 0),t([me()],nn.prototype,"service",void 0),t([me()],nn.prototype,"apiKey",void 0),t([me({attribute:!1})],nn.prototype,"weatherConfig",void 0),t([ve()],nn.prototype,"_testing",void 0),t([ve()],nn.prototype,"_testResult",void 0),nn=t([ue("si-weather-source-config")],nn);let on=class extends(Fa(ce)){constructor(){super(...arguments),this.section="all",this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._weatherConfig=null,this._weatherService=null,this._useWeatherService=!1,this._newApiKey="",this._weatherSaving=!1,this._coords=null,this._coordsEnabled=!1,this._coordsLat="",this._coordsLon="",this._coordsElev="",this._coordsSaving=!1,this._saveStatus="idle",this._savedResetTimer=null,this._updateScheduled=!1,this.debouncedSave=(()=>{let e=null,t={};return i=>{t=Object.assign(Object.assign({},t),i),e&&clearTimeout(e),e=window.setTimeout(()=>{const i=t;t={},e=null,this.saveData(i)},500)}})()}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:be+"_config_updated"})]}async _fetchData(){var e;if(!this.hass)return;const t=!this._initialLoadDone;t&&(this.isLoading=!0,this._scheduleUpdate());try{const[t,a,n]=await Promise.all([Ei(this.hass),Ui(this.hass),Fi(this.hass)]);this.config=t,this._weatherConfig=a,this._useWeatherService=a.use_weather_service,this._weatherService=null!==(e=a.weather_service)&&void 0!==e?e:Ae,this._applyCoordinates(n),this.data=(i=this.config,s=["calctime","autocalcenabled","autocalcmode","autoupdateenabled","autoupdateschedule","autoupdatefirsttime","autoupdateinterval","days_between_irrigation"],i?Object.entries(i).filter(([e])=>s.includes(e)).reduce((e,[t,i])=>Object.assign(e,{[t]:i}),{}):{}),this._initialLoadDone=!0}catch(e){console.error("Error fetching data:",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{t&&(this.isLoading=!1),this._scheduleUpdate()}var i,s}firstUpdated(){qi().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}render(){var e,t;return this.hass&&this.config&&this.data?this.isLoading?W`<div class="loading-indicator">
        ${Oa("common.loading-messages.general",this.hass.language)}
      </div>`:W`${this._renderSaveStatus()} ${this._renderCards()}`:W`<div class="loading-indicator">
        ${Oa("common.loading-messages.configuration",null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en")}
=======
    `}};t([me({attribute:!1})],rn.prototype,"hass",void 0),t([me({type:Boolean})],rn.prototype,"useWeather",void 0),t([me()],rn.prototype,"service",void 0),t([me()],rn.prototype,"apiKey",void 0),t([me({attribute:!1})],rn.prototype,"weatherConfig",void 0),t([ve()],rn.prototype,"_testing",void 0),t([ve()],rn.prototype,"_testResult",void 0),rn=t([ue("si-weather-source-config")],rn);let ln=class extends(Wa(ce)){constructor(){super(...arguments),this.section="all",this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._weatherConfig=null,this._weatherService=null,this._useWeatherService=!1,this._newApiKey="",this._weatherSaving=!1,this._coords=null,this._coordsEnabled=!1,this._coordsLat="",this._coordsLon="",this._coordsElev="",this._coordsSaving=!1,this._saveStatus="idle",this._savedResetTimer=null,this._updateScheduled=!1,this.debouncedSave=(()=>{let e=null,t={};return s=>{t=Object.assign(Object.assign({},t),s),e&&clearTimeout(e),e=window.setTimeout(()=>{const s=t;t={},e=null,this.saveData(s)},500)}})()}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:be+"_config_updated"})]}async _fetchData(){var e;if(!this.hass)return;const t=!this._initialLoadDone;t&&(this.isLoading=!0,this._scheduleUpdate());try{const[t,a,n]=await Promise.all([Ts(this.hass),Fs(this.hass),Ws(this.hass)]);this.config=t,this._weatherConfig=a,this._useWeatherService=a.use_weather_service,this._weatherService=null!==(e=a.weather_service)&&void 0!==e?e:Ae,this._applyCoordinates(n),this.data=(s=this.config,i=["calctime","autocalcenabled","autocalcmode","autoupdateenabled","autoupdateschedule","autoupdatefirsttime","autoupdateinterval","days_between_irrigation"],s?Object.entries(s).filter(([e])=>i.includes(e)).reduce((e,[t,s])=>Object.assign(e,{[t]:s}),{}):{}),this._initialLoadDone=!0}catch(e){console.error("Error fetching data:",e),ja(this,this.hass,"common.errors.load_failed",e)}finally{t&&(this.isLoading=!1),this._scheduleUpdate()}var s,i}firstUpdated(){Ks().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}render(){var e,t;return this.hass&&this.config&&this.data?this.isLoading?W`<div class="loading-indicator">
        ${Ma("common.loading-messages.general",this.hass.language)}
      </div>`:W`${this._renderSaveStatus()} ${this._renderCards()}`:W`<div class="loading-indicator">
        ${Ma("common.loading-messages.configuration",null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en")}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      </div>`}_renderCards(){switch(this.section){case"weather-location":return W`
          ${this._renderSection("weather")} ${this._renderWeatherServiceCard()}
          ${this._renderSection("location")} ${this._renderCoordinateCard()}
        `;case"when-to-water":return W`
          ${this._renderSection("automation")} ${this._renderAutoUpdateCard()}
          ${this._renderAutoCalcCard()} ${this._renderRunHistoryLoggingCard()}
          ${this._renderWeatherSkipCard()} ${this._renderSection("watering")}
          ${this._renderDaysBetweenIrrigationCard()}
          ${this._renderZoneSequencingCard()} ${this._renderMasterSwitchCard()}
        `;default:return W`
          ${this._renderSection("weather")} ${this._renderWeatherServiceCard()}
          ${this._renderWeatherSkipCard()} ${this._renderSection("automation")}
          ${this._renderAutoUpdateCard()} ${this._renderAutoCalcCard()}
          ${this._renderRunHistoryLoggingCard()}
          ${this._renderSection("location")} ${this._renderCoordinateCard()}
          ${this._renderSection("watering")}
          ${this._renderDaysBetweenIrrigationCard()}
          ${this._renderZoneSequencingCard()} ${this._renderMasterSwitchCard()}
        `}}_renderSection(e){return this.hass?W`
      <div class="settings-section-header">
<<<<<<< HEAD
        ${Oa(`panels.general.sections.${e}`,this.hass.language)}
=======
        ${Ma(`panels.general.sections.${e}`,this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      </div>
    `:W``}async _saveWeatherConfig(){if(this.hass){this._weatherSaving=!0,this._scheduleUpdate();try{await ji(this.hass,this._useWeatherService,this._useWeatherService?this._weatherService:null,this._newApiKey||null),this._newApiKey="",await this._fetchData()}catch(e){console.error("Failed to save weather config:",e),Ba(this,this.hass,"common.errors.save_failed",e)}finally{this._weatherSaving=!1,this._scheduleUpdate()}}}_renderWeatherServiceCard(){var e;return this.hass?W`
      <ha-card
<<<<<<< HEAD
        header="${Oa("weather_service_config.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("weather_service_config.description",this.hass.language)}
=======
        header="${Ma("weather_service_config.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ma("weather_service_config.description",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>
        <div class="card-content">
          <si-weather-source-config
            .hass="${this.hass}"
            .useWeather="${this._useWeatherService}"
            .service="${null!==(e=this._weatherService)&&void 0!==e?e:Ae}"
            .apiKey="${this._newApiKey}"
            .weatherConfig="${this._weatherConfig}"
            @useweather-changed="${e=>{this._useWeatherService=e.detail.value}}"
            @service-changed="${e=>{this._weatherService=e.detail.value}}"
            @apikey-changed="${e=>{this._newApiKey=e.detail.value}}"
          ></si-weather-source-config>
          <div style="margin-top: 12px;">
            <button
              class="action-btn"
              raised
              ?disabled="${this._weatherSaving}"
              @click="${this._saveWeatherConfig}"
            >
<<<<<<< HEAD
              ${this._weatherSaving?Oa("common.saving-messages.saving",this.hass.language):Oa("weather_service_config.save_button",this.hass.language)}
=======
              ${this._weatherSaving?Ma("common.saving-messages.saving",this.hass.language):Ma("weather_service_config.save_button",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </button>
          </div>
        </div>
      </ha-card>
    `:W``}_renderAutoUpdateCard(){var e,t;return this.hass&&this.config&&this.data?W`
      <ha-card
<<<<<<< HEAD
        header="${Oa("panels.general.cards.automatic-update.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("panels.general.cards.automatic-update.description",this.hass.language)}
=======
        header="${Ma("panels.general.cards.automatic-update.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ma("panels.general.cards.automatic-update.description",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
<<<<<<< HEAD
              ${Oa("panels.general.cards.automatic-update.labels.auto-update-enabled",this.hass.language)}
=======
              ${Ma("panels.general.cards.automatic-update.labels.auto-update-enabled",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </label>
            <ha-switch
              .checked="${this.config.autoupdateenabled}"
              @change="${e=>this.handleConfigChange({autoupdateenabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.data.autoupdateenabled?W`
                <div class="setting-row">
                  <label>
<<<<<<< HEAD
                    ${Oa("panels.general.cards.automatic-update.labels.auto-update-interval",this.hass.language)}
=======
                    ${Ma("panels.general.cards.automatic-update.labels.auto-update-interval",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </label>
                  <div class="inline-row">
                    <input
                      type="number"
                      class="settings-input shortfield"
                      min="1"
                      step="1"
                      inputmode="numeric"
                      .value="${null!==(e=this.data.autoupdateinterval)&&void 0!==e?e:1}"
                      @input="${e=>{const t=parseInt(e.target.value);isNaN(t)||this.handleConfigChange({autoupdateinterval:t})}}"
                    />
                    <select
                      class="settings-input"
                      .value="${sn(this.data.autoupdateschedule||Te)}"
                      @change="${e=>this.handleConfigChange({autoupdateschedule:e.target.value})}"
                    >
                      <option
                        value="${Ee}"
                        ?selected="${(this.data.autoupdateschedule||Te)===Ee}"
                      >
<<<<<<< HEAD
                        ${Oa("panels.general.cards.automatic-update.options.minutes",this.hass.language)}
=======
                        ${Ma("panels.general.cards.automatic-update.options.minutes",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                      </option>
                      <option
                        value="${Te}"
                        ?selected="${(this.data.autoupdateschedule||Te)===Te}"
                      >
<<<<<<< HEAD
                        ${Oa("panels.general.cards.automatic-update.options.hours",this.hass.language)}
=======
                        ${Ma("panels.general.cards.automatic-update.options.hours",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                      </option>
                      <option
                        value="${Oe}"
                        ?selected="${this.data.autoupdateschedule===Oe}"
                      >
<<<<<<< HEAD
                        ${Oa("panels.general.cards.automatic-update.options.days",this.hass.language)}
=======
                        ${Ma("panels.general.cards.automatic-update.options.days",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                      </option>
                    </select>
                  </div>
                </div>
                <div class="setting-row">
                  <label>
<<<<<<< HEAD
                    ${Oa("panels.general.cards.automatic-update.labels.auto-update-delay",this.hass.language)}
=======
                    ${Ma("panels.general.cards.automatic-update.labels.auto-update-delay",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    (s)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="1"
                    inputmode="numeric"
                    .value="${null!==(t=this.config.autoupdatedelay)&&void 0!==t?t:0}"
                    @input="${e=>{const t=parseInt(e.target.value);isNaN(t)||this.handleConfigChange({autoupdatedelay:t})}}"
                  />
                </div>
              `:""}
        </div>
      </ha-card>
    `:W``}_renderAutoCalcCard(){return this.hass&&this.config&&this.data?W`
      <ha-card
<<<<<<< HEAD
        header="${Oa("panels.general.cards.automatic-duration-calculation.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("panels.general.cards.automatic-duration-calculation.description",this.hass.language)}
=======
        header="${Ma("panels.general.cards.automatic-duration-calculation.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ma("panels.general.cards.automatic-duration-calculation.description",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
<<<<<<< HEAD
              ${Oa("panels.general.cards.automatic-duration-calculation.labels.auto-calc-enabled",this.hass.language)}
=======
              ${Ma("panels.general.cards.automatic-duration-calculation.labels.auto-calc-enabled",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </label>
            <ha-switch
              .checked="${this.config.autocalcenabled}"
              @change="${e=>this.handleConfigChange({autocalcenabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.data.autocalcenabled?this._renderAutoCalcMode():""}
        </div>
      </ha-card>
    `:W``}_renderAutoCalcMode(){if(!this.hass||!this.config)return W``;const e=this.hass.language,t=$e.includes(this.config.autocalcmode)?this.config.autocalcmode:we;return W`
      <div class="setting-row">
        <label>
<<<<<<< HEAD
          ${Oa("panels.general.cards.automatic-duration-calculation.labels.calc-mode",e)}
=======
          ${Ma("panels.general.cards.automatic-duration-calculation.labels.calc-mode",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </label>
        <select
          class="settings-input"
          .value="${sn(t)}"
          @change="${e=>this.handleConfigChange({autocalcmode:e.target.value,autocalcenabled:!0})}"
        >
<<<<<<< HEAD
          ${$e.map(i=>W`
              <option value="${i}" ?selected="${t===i}">
                ${Oa(`panels.general.cards.automatic-duration-calculation.modes.${i}`,e)}
=======
          ${$e.map(s=>W`
              <option value="${s}" ?selected="${t===s}">
                ${Ma(`panels.general.cards.automatic-duration-calculation.modes.${s}`,e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </option>
            `)}
        </select>
      </div>
      ${t===we?W`
            <div class="setting-row">
              <label>
<<<<<<< HEAD
                ${Oa("panels.general.cards.automatic-duration-calculation.labels.calc-time",e)}
=======
                ${Ma("panels.general.cards.automatic-duration-calculation.labels.calc-time",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </label>
              <input
                type="text"
                class="settings-input shortfield"
                .value="${this.config.calctime}"
                @input="${e=>this.handleConfigChange({calctime:e.target.value})}"
              />
            </div>
          `:W`
            <div class="card-content description-text">
<<<<<<< HEAD
              ${Oa("panels.general.cards.automatic-duration-calculation.help.before-run",e)}
=======
              ${Ma("panels.general.cards.automatic-duration-calculation.help.before-run",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </div>
          `}
    `}_renderRunHistoryLoggingCard(){return this.hass&&this.config?W`
      <ha-card
<<<<<<< HEAD
        header="${Oa("panels.general.cards.run-history-logging.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("panels.general.cards.run-history-logging.description",this.hass.language)}
=======
        header="${Ma("panels.general.cards.run-history-logging.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ma("panels.general.cards.run-history-logging.description",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
<<<<<<< HEAD
              ${Oa("panels.general.cards.run-history-logging.labels.log-no-demand",this.hass.language)}
=======
              ${Ma("panels.general.cards.run-history-logging.labels.log-no-demand",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </label>
            <ha-switch
              .checked="${this.config.log_no_demand}"
              @change="${e=>this.handleConfigChange({log_no_demand:e.target.checked})}"
            ></ha-switch>
          </div>
        </div>
      </ha-card>
<<<<<<< HEAD
    `:W``}_renderWeatherSkipCard(){var e,t,i,s,a;if(!this.hass||!this.config||!this.data)return W``;const n=this.hass.language,o=this.config.skip_irrigation_on_precipitation?"skip":this.config.forecast_weighting_enabled?"water_less":"ignore";return W`
      <ha-card header="${Oa("weather_skip.title",this.hass.language)}">
        <div class="card-content description-text">
          ${Oa("weather_skip.description",this.hass.language)}
=======
    `:W``}_renderWeatherSkipCard(){var e,t,s,i,a;if(!this.hass||!this.config||!this.data)return W``;const n=this.hass.language,o=this.config.skip_irrigation_on_precipitation?"skip":this.config.forecast_weighting_enabled?"water_less":"ignore";return W`
      <ha-card header="${Ma("weather_skip.title",this.hass.language)}">
        <div class="card-content description-text">
          ${Ma("weather_skip.description",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
<<<<<<< HEAD
              ${Oa("weather_skip.forecast_rain_label",n)}
=======
              ${Ma("weather_skip.forecast_rain_label",n)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </label>
            <select
              class="settings-input"
              .value="${sn(o)}"
              @change="${e=>{const t=e.target.value;this.handleConfigChange({skip_irrigation_on_precipitation:"skip"===t,forecast_weighting_enabled:"water_less"===t})}}"
            >
              ${["ignore","water_less","skip"].map(e=>W`
                  <option value="${e}" ?selected="${o===e}">
<<<<<<< HEAD
                    ${Oa(`weather_skip.forecast_rain_options.${e}`,n)}
=======
                    ${Ma(`weather_skip.forecast_rain_options.${e}`,n)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </option>
                `)}
            </select>
          </div>
          <div class="description-text">
<<<<<<< HEAD
            ${Oa(`weather_skip.forecast_rain_help.${o}`,n)}
=======
            ${Ma(`weather_skip.forecast_rain_help.${o}`,n)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </div>
          ${"ignore"!==o?W`
                <div class="setting-row">
                  <label>
<<<<<<< HEAD
                    ${Oa("weather_skip.lookahead_label",n)}
=======
                    ${Ma("weather_skip.lookahead_label",n)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="1"
                    max="5"
                    step="1"
                    inputmode="numeric"
                    .value="${null!==(e=this.config.precipitation_forecast_days)&&void 0!==e?e:1}"
                    @input="${e=>{const t=parseInt(e.target.value,10);!isNaN(t)&&t>=1&&this.handleConfigChange({precipitation_forecast_days:t})}}"
                  />
                </div>
                <div class="description-text">
<<<<<<< HEAD
                  ${Oa("weather_skip.lookahead_help",n)}
=======
                  ${Ma("weather_skip.lookahead_help",n)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </div>
              `:""}
          ${"skip"===o?W`
                <div class="setting-row">
                  <label>
<<<<<<< HEAD
                    ${Oa("weather_skip.threshold_label",n)}
                    (${Ma(this.config,xe)})
=======
                    ${Ma("weather_skip.threshold_label",n)}
                    (${Na(this.config,xe)})
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="0.1"
                    inputmode="decimal"
                    .value="${null!==(t=this.config.precipitation_threshold_mm)&&void 0!==t?t:2}"
                    @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({precipitation_threshold_mm:t})}}"
                  />
                </div>
              `:""}

          <div class="section-divider">
<<<<<<< HEAD
            ${Oa("weather_skip.temp_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Oa("weather_skip.temp_section_title",this.hass.language)}
=======
            ${Ma("weather_skip.temp_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Ma("weather_skip.temp_section_title",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </label>
            <ha-switch
              .checked="${this.config.skip_on_temp_enabled}"
              @change="${e=>this.handleConfigChange({skip_on_temp_enabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_temp_enabled?W`
                <div class="setting-row">
                  <label>
<<<<<<< HEAD
                    ${Oa("weather_skip.temp_threshold_label",this.hass.language)}
=======
                    ${Ma("weather_skip.temp_threshold_label",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    (°C)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.5"
                    .value="${null!==(i=this.config.temp_threshold)&&void 0!==i?i:5}"
                    @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({temp_threshold:t})}}"
                  />
                </div>
              `:""}

          <div class="section-divider">
<<<<<<< HEAD
            ${Oa("weather_skip.wind_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Oa("weather_skip.wind_section_title",this.hass.language)}
=======
            ${Ma("weather_skip.wind_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Ma("weather_skip.wind_section_title",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </label>
            <ha-switch
              .checked="${this.config.skip_on_wind_enabled}"
              @change="${e=>this.handleConfigChange({skip_on_wind_enabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_wind_enabled?W`
                <div class="setting-row">
                  <label>
<<<<<<< HEAD
                    ${Oa("weather_skip.wind_threshold_label",this.hass.language)}
=======
                    ${Ma("weather_skip.wind_threshold_label",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    (m/s)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="0.1"
                    inputmode="decimal"
                    .value="${null!==(s=this.config.wind_threshold)&&void 0!==s?s:6.9}"
                    @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({wind_threshold:t})}}"
                  />
                </div>
              `:""}

          <div class="section-divider">
<<<<<<< HEAD
            ${Oa("weather_skip.freeze_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Oa("weather_skip.freeze_section_title",this.hass.language)}
=======
            ${Ma("weather_skip.freeze_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Ma("weather_skip.freeze_section_title",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </label>
            <ha-switch
              .checked="${this.config.skip_on_freeze_enabled}"
              @change="${e=>this.handleConfigChange({skip_on_freeze_enabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_freeze_enabled?W`
                <div class="setting-row">
                  <label>
<<<<<<< HEAD
                    ${Oa("weather_skip.freeze_threshold_label",this.hass.language)}
=======
                    ${Ma("weather_skip.freeze_threshold_label",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    (°C)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.5"
                    .value="${null!==(a=this.config.freeze_threshold)&&void 0!==a?a:1}"
                    @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({freeze_threshold:t})}}"
                  />
                </div>
                <div class="description-text">
<<<<<<< HEAD
                  ${Oa("weather_skip.freeze_help",this.hass.language)}
=======
                  ${Ma("weather_skip.freeze_help",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </div>
              `:""}

          <div class="section-divider">
<<<<<<< HEAD
            ${Oa("weather_skip.rain_sensor_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Oa("weather_skip.rain_sensor_label",this.hass.language)}
=======
            ${Ma("weather_skip.rain_sensor_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Ma("weather_skip.rain_sensor_label",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </label>
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${this.config.rain_sensor||""}"
              .includeDomains="${["binary_sensor"]}"
              allow-custom-entity
              @value-changed="${e=>this.handleConfigChange({rain_sensor:e.detail.value||null})}"
            ></ha-entity-picker>
          </div>
        </div>
      </ha-card>
    `}_applyCoordinates(e){this._coords=e,this._coordsEnabled=e.manual_coordinates_enabled;const t=(e,t)=>null!=e?String(e):null!=t?String(t):"";this._coordsLat=t(e.manual_latitude,e.ha_latitude),this._coordsLon=t(e.manual_longitude,e.ha_longitude),this._coordsElev=t(e.manual_elevation,e.ha_elevation)}async _saveCoordinates(){if(this.hass){this._coordsSaving=!0,this._scheduleUpdate();try{await(e=this.hass,t=this._coordsEnabled,i=this._coordsEnabled?parseFloat(this._coordsLat):null,s=this._coordsEnabled?parseFloat(this._coordsLon):null,a=this._coordsEnabled?parseFloat(this._coordsElev):null,e.callWS({type:be+"/coordinates_save",manual_coordinates_enabled:t,manual_latitude:null!=i?i:null,manual_longitude:null!=s?s:null,manual_elevation:null!=a?a:null})),this._applyCoordinates(await Fi(this.hass))}catch(e){console.error("Failed to save coordinates:",e),Ba(this,this.hass,"common.errors.save_failed",e)}finally{this._coordsSaving=!1,this._scheduleUpdate()}var e,t,i,s,a}}_renderCoordinateCard(){var e,t,i;if(!this.hass||!this._coords)return W``;const s=this._coords;return W`
      <ha-card
<<<<<<< HEAD
        header="${Oa("coordinate_config.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("coordinate_config.description",this.hass.language)}
=======
        header="${Ma("coordinate_config.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ma("coordinate_config.description",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
<<<<<<< HEAD
              ${Oa("coordinate_config.manual_enabled",this.hass.language)}
=======
              ${Ma("coordinate_config.manual_enabled",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </label>
            <ha-switch
              .checked="${this._coordsEnabled}"
              @change="${e=>{this._coordsEnabled=e.target.checked}}"
            ></ha-switch>
          </div>
          ${this._coordsEnabled?W`
                <div class="setting-row">
                  <label>
<<<<<<< HEAD
                    ${Oa("coordinate_config.latitude",this.hass.language)}
=======
                    ${Ma("coordinate_config.latitude",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="-90"
                    max="90"
                    step="0.000001"
                    inputmode="decimal"
                    .value="${this._coordsLat}"
                    @input="${e=>{this._coordsLat=e.target.value}}"
                  />
                </div>
                <div class="setting-row">
                  <label>
<<<<<<< HEAD
                    ${Oa("coordinate_config.longitude",this.hass.language)}
=======
                    ${Ma("coordinate_config.longitude",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="-180"
                    max="180"
                    step="0.000001"
                    inputmode="decimal"
                    .value="${this._coordsLon}"
                    @input="${e=>{this._coordsLon=e.target.value}}"
                  />
                </div>
                <div class="setting-row">
                  <label>
<<<<<<< HEAD
                    ${Oa("coordinate_config.elevation",this.hass.language)}
=======
                    ${Ma("coordinate_config.elevation",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="-1000"
                    max="9000"
                    step="1"
                    inputmode="numeric"
                    .value="${this._coordsElev}"
                    @input="${e=>{this._coordsElev=e.target.value}}"
                  />
                </div>
              `:W`
                <div
                  class="card-content"
                  style="color: var(--secondary-text-color); font-style: italic;"
                >
<<<<<<< HEAD
                  ${Oa("coordinate_config.current_ha_coords",this.hass.language)}:
                  ${Oa("coordinate_config.latitude",this.hass.language)}:
                  ${null!==(e=s.ha_latitude)&&void 0!==e?e:0},
                  ${Oa("coordinate_config.longitude",this.hass.language)}:
                  ${null!==(t=s.ha_longitude)&&void 0!==t?t:0},
                  ${Oa("coordinate_config.elevation",this.hass.language)}:
                  ${null!==(i=s.ha_elevation)&&void 0!==i?i:0}m
=======
                  ${Ma("coordinate_config.current_ha_coords",this.hass.language)}:
                  ${Ma("coordinate_config.latitude",this.hass.language)}:
                  ${null!==(e=i.ha_latitude)&&void 0!==e?e:0},
                  ${Ma("coordinate_config.longitude",this.hass.language)}:
                  ${null!==(t=i.ha_longitude)&&void 0!==t?t:0},
                  ${Ma("coordinate_config.elevation",this.hass.language)}:
                  ${null!==(s=i.ha_elevation)&&void 0!==s?s:0}m
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </div>
              `}
          <div style="margin-top: 12px;">
            <button
              class="action-btn"
              raised
              ?disabled="${this._coordsSaving}"
              @click="${this._saveCoordinates}"
            >
<<<<<<< HEAD
              ${this._coordsSaving?Oa("common.saving-messages.saving",this.hass.language):Oa("common.actions.save",this.hass.language)}
=======
              ${this._coordsSaving?Ma("common.saving-messages.saving",this.hass.language):Ma("common.actions.save",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </button>
          </div>
        </div>
      </ha-card>
    `}_renderDaysBetweenIrrigationCard(){var e;return this.hass&&this.config&&this.data?W`
      <ha-card
<<<<<<< HEAD
        header="${Oa("days_between_irrigation.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("days_between_irrigation.description",this.hass.language)}
=======
        header="${Ma("days_between_irrigation.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ma("days_between_irrigation.description",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
<<<<<<< HEAD
              ${Oa("days_between_irrigation.label",this.hass.language)}
              <div class="setting-description">
                ${Oa("days_between_irrigation.help_text",this.hass.language)}
=======
              ${Ma("days_between_irrigation.label",this.hass.language)}
              <div class="setting-description">
                ${Ma("days_between_irrigation.help_text",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </div>
            </label>
            <input
              type="number"
              class="settings-input shortfield"
              min="0"
              max="365"
              step="1"
              inputmode="numeric"
              .value="${null!==(e=this.config.days_between_irrigation)&&void 0!==e?e:0}"
              @input="${e=>{const t=e.target.valueAsNumber;isNaN(t)||this.handleConfigChange({days_between_irrigation:Math.round(t)})}}"
            />
          </div>
        </div>
      </ha-card>
    `:W``}_renderZoneSequencingCard(){var e,t;if(!this.hass||!this.config||!this.data)return W``;const i=(this.config.zone_sequencing||Wt)===qt;return W`
      <ha-card
<<<<<<< HEAD
        header="${Oa("zone_sequencing.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("zone_sequencing.description",this.hass.language)}
=======
        header="${Ma("zone_sequencing.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Ma("zone_sequencing.description",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
<<<<<<< HEAD
              ${Oa("zone_sequencing.title",this.hass.language)}
=======
              ${Ma("zone_sequencing.title",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </label>
            <select
              class="settings-input"
              .value="${sn(this.config.zone_sequencing||Wt)}"
              @change="${e=>this.handleConfigChange({[Ft]:e.target.value})}"
            >
              <option
                value="${Wt}"
                ?selected="${(this.config.zone_sequencing||Wt)===Wt}"
              >
<<<<<<< HEAD
                ${Oa("zone_sequencing.parallel",this.hass.language)}
=======
                ${Ma("zone_sequencing.parallel",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </option>
              <option
                value="${Zt}"
                ?selected="${this.config.zone_sequencing===Zt}"
              >
<<<<<<< HEAD
                ${Oa("zone_sequencing.sequential",this.hass.language)}
=======
                ${Ma("zone_sequencing.sequential",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </option>
              <option
                value="${qt}"
                ?selected="${this.config.zone_sequencing===qt}"
              >
<<<<<<< HEAD
                ${Oa("zone_sequencing.rotating",this.hass.language)}
=======
                ${Ma("zone_sequencing.rotating",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </option>
            </select>
          </div>
          ${i?W`
                <div class="setting-row">
                  <label>
<<<<<<< HEAD
                    ${Oa("zone_sequencing.max_consecutive_duration_label",this.hass.language)}
=======
                    ${Ma("zone_sequencing.max_consecutive_duration_label",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </label>
                  <input
                    type="number"
                    min="1"
                    class="settings-input"
                    .value="${null!==(e=this.config.zone_sequencing_max_consecutive_duration)&&void 0!==e?e:5}"
                    @input="${e=>{const t=parseInt(e.target.value,10);isNaN(t)||this.handleConfigChange({[Gt]:t})}}"
                  />
                  <span class="unit-label">
<<<<<<< HEAD
                    ${Oa("zone_sequencing.max_consecutive_duration_unit",this.hass.language)}
=======
                    ${Ma("zone_sequencing.max_consecutive_duration_unit",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </span>
                </div>
                <div class="setting-row">
                  <label>
<<<<<<< HEAD
                    ${Oa("zone_sequencing.min_absorption_time_label",this.hass.language)}
=======
                    ${Ma("zone_sequencing.min_absorption_time_label",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </label>
                  <input
                    type="number"
                    min="0"
                    class="settings-input"
                    .value="${null!==(t=this.config.zone_sequencing_min_absorption_time)&&void 0!==t?t:0}"
                    @input="${e=>{const t=parseInt(e.target.value,10);isNaN(t)||this.handleConfigChange({[Kt]:t})}}"
                  />
                  <span class="unit-label">
<<<<<<< HEAD
                    ${Oa("zone_sequencing.min_absorption_time_unit",this.hass.language)}
=======
                    ${Ma("zone_sequencing.min_absorption_time_unit",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </span>
                </div>
              `:""}
        </div>
      </ha-card>
<<<<<<< HEAD
    `}_renderMasterSwitchCard(){var e,t;if(!this.hass||!this.config)return W``;const i=!!this.config.master_kick_enabled;return W`
      <ha-card header="${Oa("master.title",this.hass.language)}">
        <div class="card-content description-text">
          ${Oa("master.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>${Oa("master.entity",this.hass.language)}</label>
=======
    `}_renderMasterSwitchCard(){var e,t;if(!this.hass||!this.config)return W``;const s=!!this.config.master_kick_enabled;return W`
      <ha-card header="${Ma("master.title",this.hass.language)}">
        <div class="card-content description-text">
          ${Ma("master.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>${Ma("master.entity",this.hass.language)}</label>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${this.config.master_entity||""}"
              .includeDomains="${["switch","valve","input_boolean"]}"
              allow-custom-entity
              @value-changed="${e=>this.handleConfigChange({[Vt]:e.detail.value||null})}"
            ></ha-entity-picker>
          </div>
          ${this.config.master_entity?W`
                <div class="setting-row">
                  <label
<<<<<<< HEAD
                    >${Oa("master.kick_enabled",this.hass.language)}</label
=======
                    >${Ma("master.kick_enabled",this.hass.language)}</label
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <ha-switch
                    .checked="${i}"
                    @change="${e=>this.handleConfigChange({[Xt]:e.target.checked})}"
                  ></ha-switch>
                </div>
                ${i?W`
                      <div class="setting-row">
                        <label>
<<<<<<< HEAD
                          ${Oa("master.kick_pause",this.hass.language)}
=======
                          ${Ma("master.kick_pause",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                        </label>
                        <input
                          type="number"
                          min="0"
                          step="0.1"
                          class="settings-input"
                          .value="${null!==(e=this.config.master_kick_pause_seconds)&&void 0!==e?e:1}"
                          @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({[Jt]:t})}}"
                        />
                        <span class="unit-label">
<<<<<<< HEAD
                          ${Oa("master.seconds_unit",this.hass.language)}
=======
                          ${Ma("master.seconds_unit",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                        </span>
                      </div>
                    `:""}
                <div class="setting-row">
                  <label
<<<<<<< HEAD
                    >${Oa("master.settle",this.hass.language)}</label
=======
                    >${Ma("master.settle",this.hass.language)}</label
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <input
                    type="number"
                    min="0"
                    class="settings-input"
                    .value="${null!==(t=this.config.master_settle_seconds)&&void 0!==t?t:10}"
                    @input="${e=>{const t=parseInt(e.target.value,10);isNaN(t)||this.handleConfigChange({[Yt]:t})}}"
                  />
                  <span class="unit-label">
<<<<<<< HEAD
                    ${Oa("master.seconds_unit",this.hass.language)}
=======
                    ${Ma("master.seconds_unit",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </span>
                </div>
                <div class="setting-row">
                  <label
<<<<<<< HEAD
                    >${Oa("master.off_after",this.hass.language)}</label
=======
                    >${Ma("master.off_after",this.hass.language)}</label
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <ha-switch
                    .checked="${!!this.config.master_off_after}"
                    @change="${e=>this.handleConfigChange({[Qt]:e.target.checked})}"
                  ></ha-switch>
                </div>
              `:""}
        </div>
      </ha-card>
    `}async saveData(e){if(this.hass&&this.data){this.isSaving=!0,this._saveStatus="saving",this._scheduleUpdate();try{this.data=Object.assign(Object.assign({},this.data),e),this._scheduleUpdate(),await Ci(this.hass,this.data),this._markSaved()}catch(e){console.error("Error saving config:",e),this._saveStatus="idle",Ba(this,this.hass,"common.errors.save_failed",e),await this._fetchData()}finally{this.isSaving=!1,this._scheduleUpdate()}}}_markSaved(){this._saveStatus="saved",this._savedResetTimer&&clearTimeout(this._savedResetTimer),this._savedResetTimer=window.setTimeout(()=>{this._saveStatus="idle",this._scheduleUpdate()},2e3)}_renderSaveStatus(){if(!this.hass||"idle"===this._saveStatus)return W``;const e="saving"===this._saveStatus;return W`
      <div class="save-status-float ${this._saveStatus}">
        <ha-icon
          icon="${e?"mdi:content-save-outline":"mdi:check-circle"}"
        ></ha-icon>
<<<<<<< HEAD
        ${Oa(e?"common.saving-messages.saving":"panels.zones.status.saved",this.hass.language)}
=======
        ${Ma(e?"common.saving-messages.saving":"panels.zones.status.saved",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      </div>
    `}handleConfigChange(e){this.config&&(this.config=Object.assign(Object.assign({},this.config),e)),this.debouncedSave(e)}disconnectedCallback(){super.disconnectedCallback(),this._savedResetTimer&&(clearTimeout(this._savedResetTimer),this._savedResetTimer=null)}static get styles(){return r`
      ${Ka}

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
<<<<<<< HEAD
    `}};t([me()],on.prototype,"narrow",void 0),t([me()],on.prototype,"path",void 0),t([me()],on.prototype,"section",void 0),t([me()],on.prototype,"data",void 0),t([me()],on.prototype,"config",void 0),t([me({type:Boolean})],on.prototype,"isLoading",void 0),t([me({type:Boolean})],on.prototype,"isSaving",void 0),t([me()],on.prototype,"_weatherConfig",void 0),t([me()],on.prototype,"_weatherService",void 0),t([me({type:Boolean})],on.prototype,"_useWeatherService",void 0),t([me()],on.prototype,"_newApiKey",void 0),t([me({type:Boolean})],on.prototype,"_weatherSaving",void 0),t([ve()],on.prototype,"_coords",void 0),t([ve()],on.prototype,"_coordsEnabled",void 0),t([ve()],on.prototype,"_coordsLat",void 0),t([ve()],on.prototype,"_coordsLon",void 0),t([ve()],on.prototype,"_coordsElev",void 0),t([ve()],on.prototype,"_coordsSaving",void 0),t([ve()],on.prototype,"_saveStatus",void 0),on=t([ue("smart-irrigation-view-general")],on);const rn=e=>9*e/5+32;function ln(e,t,i){if(null==e||Number.isNaN(e))return null;switch(t){case"temperature":return i?{value:e,unit:"°C"}:{value:rn(e),unit:"°F"};case"precipitation":return i?{value:e,unit:ot}:{value:(n=e,n/25.4),unit:rt};case"windspeed":return i?{value:e,unit:ct}:{value:(a=e,2.2369362920544*a),unit:dt};case"pressure":return i?{value:e,unit:"hPa"}:{value:(s=e,.0295299830714*s),unit:lt}}var s,a,n}function dn(e,t,i,s){const a=ln(e,t,i);if(!a)return"-";const n=function(e,t){return"pressure"===e?t?0:2:"precipitation"===e?t?1:2:1}(t,i);return`${a.value.toFixed(n)} ${a.unit}`}function cn(e,t){return null==e||Number.isNaN(e)?"-":t?`${e.toFixed(0)} L`:`${(e=>.264172052*e)(e).toFixed(1)} gal`}let hn=class extends ce{constructor(){super(...arguments),this.metric=!0,this.name="",this.size="",this.throughput="",this.linkedEntity="",this.showEntity=!1}_emit(e,t){this.dispatchEvent(new CustomEvent(e,{detail:{value:t},bubbles:!0,composed:!0}))}render(){var e,t;const i=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en",s=this.metric?"m²":it,a=this.metric?st:at;return W`
      <si-field label="${Oa("panels.zones.labels.name",i)}" required>
=======
    `}};t([me()],ln.prototype,"narrow",void 0),t([me()],ln.prototype,"path",void 0),t([me()],ln.prototype,"section",void 0),t([me()],ln.prototype,"data",void 0),t([me()],ln.prototype,"config",void 0),t([me({type:Boolean})],ln.prototype,"isLoading",void 0),t([me({type:Boolean})],ln.prototype,"isSaving",void 0),t([me()],ln.prototype,"_weatherConfig",void 0),t([me()],ln.prototype,"_weatherService",void 0),t([me({type:Boolean})],ln.prototype,"_useWeatherService",void 0),t([me()],ln.prototype,"_newApiKey",void 0),t([me({type:Boolean})],ln.prototype,"_weatherSaving",void 0),t([ve()],ln.prototype,"_coords",void 0),t([ve()],ln.prototype,"_coordsEnabled",void 0),t([ve()],ln.prototype,"_coordsLat",void 0),t([ve()],ln.prototype,"_coordsLon",void 0),t([ve()],ln.prototype,"_coordsElev",void 0),t([ve()],ln.prototype,"_coordsSaving",void 0),t([ve()],ln.prototype,"_saveStatus",void 0),ln=t([ue("smart-irrigation-view-general")],ln);const dn=e=>9*e/5+32;function cn(e,t,s){if(null==e||Number.isNaN(e))return null;switch(t){case"temperature":return s?{value:e,unit:"°C"}:{value:dn(e),unit:"°F"};case"precipitation":return s?{value:e,unit:ot}:{value:(n=e,n/25.4),unit:rt};case"windspeed":return s?{value:e,unit:ct}:{value:(a=e,2.2369362920544*a),unit:dt};case"pressure":return s?{value:e,unit:"hPa"}:{value:(i=e,.0295299830714*i),unit:lt}}var i,a,n}function hn(e,t,s,i){const a=cn(e,t,s);if(!a)return"-";const n=function(e,t){return"pressure"===e?t?0:2:"precipitation"===e?t?1:2:1}(t,s);return`${a.value.toFixed(n)} ${a.unit}`}function un(e,t){return null==e||Number.isNaN(e)?"-":t?`${e.toFixed(0)} L`:`${(e=>.264172052*e)(e).toFixed(1)} gal`}let pn=class extends ce{constructor(){super(...arguments),this.metric=!0,this.name="",this.size="",this.throughput="",this.linkedEntity="",this.showEntity=!1}_emit(e,t){this.dispatchEvent(new CustomEvent(e,{detail:{value:t},bubbles:!0,composed:!0}))}render(){var e,t;const s=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en",i=this.metric?"m²":st,a=this.metric?it:at;return W`
      <si-field label="${Ma("panels.zones.labels.name",s)}" required>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        <input
          type="text"
          class="si-input"
          .value="${this.name}"
          @input="${e=>this._emit("name-changed",e.target.value)}"
        />
      </si-field>

      <si-field
<<<<<<< HEAD
        label="${Oa("panels.zones.labels.size",i)}"
        unit="${s}"
        help="${Oa("field_help.zone_size",i)}"
=======
        label="${Ma("panels.zones.labels.size",s)}"
        unit="${i}"
        help="${Ma("field_help.zone_size",s)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      >
        <input
          type="number"
          class="si-input"
          min="0"
          step="0.1"
          inputmode="decimal"
          .value="${this.size}"
          @input="${e=>this._emit("size-changed",e.target.value)}"
        />
      </si-field>

      <si-field
<<<<<<< HEAD
        label="${Oa("panels.zones.labels.throughput",i)}"
        unit="${a}"
        help="${Oa("field_help.zone_throughput",i)}"
=======
        label="${Ma("panels.zones.labels.throughput",s)}"
        unit="${a}"
        help="${Ma("field_help.zone_throughput",s)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      >
        <input
          type="number"
          class="si-input"
          min="0"
          step="0.1"
          inputmode="decimal"
          .value="${this.throughput}"
          @input="${e=>this._emit("throughput-changed",e.target.value)}"
        />
      </si-field>

      ${this.showEntity?W`
            <si-field
<<<<<<< HEAD
              label="${Oa("panels.zones.labels.linked_entity",i)}"
              help="${Oa("field_help.zone_linked_entity",i)}"
=======
              label="${Ma("panels.zones.labels.linked_entity",s)}"
              help="${Ma("field_help.zone_linked_entity",s)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            >
              <ha-entity-picker
                .hass="${this.hass}"
                .value="${this.linkedEntity}"
                .includeDomains="${["switch","valve","input_boolean"]}"
                allow-custom-entity
                @value-changed="${e=>this._emit("entity-changed",e.detail.value||"")}"
              ></ha-entity-picker>
            </si-field>
          `:""}
    `}static get styles(){return r`
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
<<<<<<< HEAD
    `}};t([me({attribute:!1})],hn.prototype,"hass",void 0),t([me({type:Boolean})],hn.prototype,"metric",void 0),t([me()],hn.prototype,"name",void 0),t([me()],hn.prototype,"size",void 0),t([me()],hn.prototype,"throughput",void 0),t([me()],hn.prototype,"linkedEntity",void 0),t([me({type:Boolean})],hn.prototype,"showEntity",void 0),hn=t([ue("si-zone-form")],hn);let un=class extends(Fa(ce)){constructor(){super(...arguments),this.zones=[],this.modules=[],this.mappings=[],this.distributors=[],this.isLoading=!0,this._initialLoadDone=!1,this._scrolledTo=null,this._osStationFilter=e=>"station"===e.attributes.opensprinkler_type&&!e.attributes.is_master,this._expanded=new Set,this.isSaving=!1,this._showAddZone=!1,this._pendingConfirm=null,this._saveStatus="idle",this._savedResetTimer=null,this._confirmDeleteZoneId=null,this._newZoneName="",this._newZoneSize="",this._newZoneThroughput="",this._newZoneEntity="",this._updateScheduled=!1,this.globalDebounceTimer=null}_hasOpenSprinklerStations(){var e,t;const i=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.states)&&void 0!==t?t:{};return Object.keys(i).some(e=>e.startsWith("switch.")&&this._osStationFilter(i[e]))}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}get _targetZoneId(){var e,t;const i=null===(t=null===(e=this.path)||void 0===e?void 0:e.params)||void 0===t?void 0:t.zone;return null!=i&&""!==i?Number(i):null}_isExpanded(e){return void 0!==e.id&&this._expanded.has(e.id)}_toggleZone(e){const t=new Set(this._expanded);t.has(e)?t.delete(e):t.add(e),this._expanded=t}_flowSensorIsTotalizer(e){var t,i;const s=e.flow_sensor;if(!s)return!1;if(!this.hass)return!1;const a=this.hass.states[s];if(!a)return!1;const n=((null===(t=a.attributes)||void 0===t?void 0:t.unit_of_measurement)||"").trim();return"total_increasing"===(null===(i=a.attributes)||void 0===i?void 0:i.state_class)||!(!n||n.includes("/"))&&!["gpm","lpm","gph","lph"].includes(n.toLowerCase())}firstUpdated(){qi().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}updated(){var e;const t=this._targetZoneId;if(null===t||this.isLoading)return;if(this._scrolledTo===t)return;if(!this._expanded.has(t))return void(this._expanded=new Set(this._expanded).add(t));const i=null===(e=this.shadowRoot)||void 0===e?void 0:e.querySelector(`#zone-${t}`);i&&(this._scrolledTo=t,requestAnimationFrame(()=>i.scrollIntoView({behavior:"smooth",block:"start"})))}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:be+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[t,i,s,a,n]=await Promise.all([Ei(this.hass),Ti(this.hass),Hi(this.hass),Ii(this.hass),Ri(this.hass)]);this.config=t,this.zones=i,this.modules=s,this.mappings=a,this.distributors=n,this._initialLoadDone=!0}catch(e){console.error("Error fetching data:",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}handleResetAllBuckets(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",be+"/zones",{reset_all_buckets:!0})).catch(e=>{console.error("Failed to reset all buckets:",e),Ba(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after reset:",e))}))}handleClearAllWeatherdata(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",be+"/zones",{clear_all_weatherdata:!0})).catch(e=>{console.error("Failed to clear all weather data:",e),Ba(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after clear-weather:",e))}))}handleAddZone(){var e;if(!this._newZoneName.trim())return;const t=null!==(e=this.modules.find(e=>"PyETO"===e.name))&&void 0!==e?e:this.modules[0],i=this.mappings[0],s={name:this._newZoneName.trim(),size:Math.round(100*(parseFloat(this._newZoneSize)||0))/100,throughput:Math.round(100*(parseFloat(this._newZoneThroughput)||0))/100,state:Wa.Automatic,duration:0,bucket:0,module:null==t?void 0:t.id,delta:0,explanation:"",multiplier:1,mapping:null==i?void 0:i.id,lead_time:0,maximum_duration:void 0,maximum_bucket:void 0,drainage_rate:void 0,current_drainage:0,linked_entity:this._newZoneEntity||void 0};this.zones=[...this.zones,s],this.isSaving=!0,this._showAddZone=!1,this.saveToHA(s).then(()=>(this._newZoneName="",this._newZoneSize="",this._newZoneThroughput="",this._newZoneEntity="",this._fetchData())).catch(e=>{console.error("Failed to add zone:",e),this.zones=this.zones.slice(0,-1),Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()})}handleEditZone(e,t){this.hass&&(this.zones=this.zones.map((i,s)=>s===e?t:i),this.globalDebounceTimer&&clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=window.setTimeout(()=>{this.isSaving=!0,this._saveStatus="saving",this.saveToHA(t).then(()=>this._markSaved()).catch(e=>{console.error("Failed to save zone:",e),this._saveStatus="idle",Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}),this.globalDebounceTimer=null},500),this._scheduleUpdate())}handleRemoveZone(e){this._confirmDeleteZoneId=e}_confirmDelete(){const e=this._confirmDeleteZoneId;if(null===e||!this.hass)return;const t=this.zones.findIndex(t=>t.id===e);if(-1===t)return;const i=[...this.zones];var s,a;this.zones=this.zones.filter(t=>t.id!==e),this._confirmDeleteZoneId=null,this.isSaving=!0,(s=this.hass,a=e.toString(),s.callApi("POST",be+"/zones",{id:a,remove:!0})).catch(e=>{console.error("Failed to delete zone:",e),Ba(this,this.hass,"common.errors.delete_failed",e),this.zones=i,this._fetchData().catch(e=>console.error("Failed to refresh data after delete error:",e))}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()})}_runPendingConfirm(){const e=this._pendingConfirm;this._pendingConfirm=null,null==e||e.onConfirm()}_markSaved(){this._saveStatus="saved",this._savedResetTimer&&clearTimeout(this._savedResetTimer),this._savedResetTimer=window.setTimeout(()=>{this._saveStatus="idle",this._scheduleUpdate()},2e3),this._scheduleUpdate()}_renderSaveStatus(){if(!this.hass||"idle"===this._saveStatus)return W``;const e="saving"===this._saveStatus;return W`
=======
    `}};t([me({attribute:!1})],pn.prototype,"hass",void 0),t([me({type:Boolean})],pn.prototype,"metric",void 0),t([me()],pn.prototype,"name",void 0),t([me()],pn.prototype,"size",void 0),t([me()],pn.prototype,"throughput",void 0),t([me()],pn.prototype,"linkedEntity",void 0),t([me({type:Boolean})],pn.prototype,"showEntity",void 0),pn=t([ue("si-zone-form")],pn);let gn=class extends(Wa(ce)){constructor(){super(...arguments),this.zones=[],this.modules=[],this.mappings=[],this.distributors=[],this.isLoading=!0,this._initialLoadDone=!1,this._scrolledTo=null,this._osStationFilter=e=>"station"===e.attributes.opensprinkler_type&&!e.attributes.is_master,this._expanded=new Set,this.isSaving=!1,this._showAddZone=!1,this._pendingConfirm=null,this._saveStatus="idle",this._savedResetTimer=null,this._confirmDeleteZoneId=null,this._newZoneName="",this._newZoneSize="",this._newZoneThroughput="",this._newZoneEntity="",this._updateScheduled=!1,this.globalDebounceTimer=null}_hasOpenSprinklerStations(){var e,t;const s=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.states)&&void 0!==t?t:{};return Object.keys(s).some(e=>e.startsWith("switch.")&&this._osStationFilter(s[e]))}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}get _targetZoneId(){var e,t;const s=null===(t=null===(e=this.path)||void 0===e?void 0:e.params)||void 0===t?void 0:t.zone;return null!=s&&""!==s?Number(s):null}_isExpanded(e){return void 0!==e.id&&this._expanded.has(e.id)}_toggleZone(e){const t=new Set(this._expanded);t.has(e)?t.delete(e):t.add(e),this._expanded=t}_flowSensorIsTotalizer(e){var t,s;const i=e.flow_sensor;if(!i)return!1;if(!this.hass)return!1;const a=this.hass.states[i];if(!a)return!1;const n=((null===(t=a.attributes)||void 0===t?void 0:t.unit_of_measurement)||"").trim();return"total_increasing"===(null===(s=a.attributes)||void 0===s?void 0:s.state_class)||!(!n||n.includes("/"))&&!["gpm","lpm","gph","lph"].includes(n.toLowerCase())}firstUpdated(){Ks().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}updated(){var e;const t=this._targetZoneId;if(null===t||this.isLoading)return;if(this._scrolledTo===t)return;if(!this._expanded.has(t))return void(this._expanded=new Set(this._expanded).add(t));const s=null===(e=this.shadowRoot)||void 0===e?void 0:e.querySelector(`#zone-${t}`);s&&(this._scrolledTo=t,requestAnimationFrame(()=>s.scrollIntoView({behavior:"smooth",block:"start"})))}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:be+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[t,s,i,a,n]=await Promise.all([Ts(this.hass),Ds(this.hass),Hs(this.hass),Ls(this.hass),Us(this.hass)]);this.config=t,this.zones=s,this.modules=i,this.mappings=a,this.distributors=n,this._initialLoadDone=!0}catch(e){console.error("Error fetching data:",e),ja(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}handleResetAllBuckets(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",be+"/zones",{reset_all_buckets:!0})).catch(e=>{console.error("Failed to reset all buckets:",e),ja(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after reset:",e))}))}handleClearAllWeatherdata(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",be+"/zones",{clear_all_weatherdata:!0})).catch(e=>{console.error("Failed to clear all weather data:",e),ja(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after clear-weather:",e))}))}handleAddZone(){var e;if(!this._newZoneName.trim())return;const t=null!==(e=this.modules.find(e=>"PyETO"===e.name))&&void 0!==e?e:this.modules[0],s=this.mappings[0],i={name:this._newZoneName.trim(),size:Math.round(100*(parseFloat(this._newZoneSize)||0))/100,throughput:Math.round(100*(parseFloat(this._newZoneThroughput)||0))/100,state:Ga.Automatic,duration:0,bucket:0,module:null==t?void 0:t.id,delta:0,explanation:"",multiplier:1,mapping:null==s?void 0:s.id,lead_time:0,maximum_duration:void 0,maximum_bucket:void 0,drainage_rate:void 0,current_drainage:0,linked_entity:this._newZoneEntity||void 0};this.zones=[...this.zones,i],this.isSaving=!0,this._showAddZone=!1,this.saveToHA(i).then(()=>(this._newZoneName="",this._newZoneSize="",this._newZoneThroughput="",this._newZoneEntity="",this._fetchData())).catch(e=>{console.error("Failed to add zone:",e),this.zones=this.zones.slice(0,-1),ja(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()})}handleEditZone(e,t){this.hass&&(this.zones=this.zones.map((s,i)=>i===e?t:s),this.globalDebounceTimer&&clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=window.setTimeout(()=>{this.isSaving=!0,this._saveStatus="saving",this.saveToHA(t).then(()=>this._markSaved()).catch(e=>{console.error("Failed to save zone:",e),this._saveStatus="idle",ja(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}),this.globalDebounceTimer=null},500),this._scheduleUpdate())}handleRemoveZone(e){this._confirmDeleteZoneId=e}_confirmDelete(){const e=this._confirmDeleteZoneId;if(null===e||!this.hass)return;const t=this.zones.findIndex(t=>t.id===e);if(-1===t)return;const s=[...this.zones];var i,a;this.zones=this.zones.filter(t=>t.id!==e),this._confirmDeleteZoneId=null,this.isSaving=!0,(i=this.hass,a=e.toString(),i.callApi("POST",be+"/zones",{id:a,remove:!0})).catch(e=>{console.error("Failed to delete zone:",e),ja(this,this.hass,"common.errors.delete_failed",e),this.zones=s,this._fetchData().catch(e=>console.error("Failed to refresh data after delete error:",e))}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()})}_runPendingConfirm(){const e=this._pendingConfirm;this._pendingConfirm=null,null==e||e.onConfirm()}_markSaved(){this._saveStatus="saved",this._savedResetTimer&&clearTimeout(this._savedResetTimer),this._savedResetTimer=window.setTimeout(()=>{this._saveStatus="idle",this._scheduleUpdate()},2e3),this._scheduleUpdate()}_renderSaveStatus(){if(!this.hass||"idle"===this._saveStatus)return W``;const e="saving"===this._saveStatus;return W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      <span class="save-status ${this._saveStatus}">
        <ha-icon
          icon="${e?"mdi:content-save-outline":"mdi:check-circle"}"
        ></ha-icon>
<<<<<<< HEAD
        ${Oa(e?"common.saving-messages.saving":"panels.zones.status.saved",this.hass.language)}
      </span>
    `}async saveToHA(e){if(!this.hass)throw new Error("Home Assistant connection not available");await Oi(this.hass,e)}_renderModuleOptions(e){if(!this.hass)return W``;const t=null!=e?String(e):"";return W`
      <option value="" ?selected="${""===t}">
        ---${Oa("common.labels.select",this.hass.language)}---
=======
        ${Ma(e?"common.saving-messages.saving":"panels.zones.status.saved",this.hass.language)}
      </span>
    `}async saveToHA(e){if(!this.hass)throw new Error("Home Assistant connection not available");await Ms(this.hass,e)}_renderModuleOptions(e){if(!this.hass)return W``;const t=null!=e?String(e):"";return W`
      <option value="" ?selected="${""===t}">
        ---${Ma("common.labels.select",this.hass.language)}---
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      </option>
      ${this.modules.map(e=>W`
          <option value="${e.id}" ?selected="${t===String(e.id)}">
            ${e.id}: ${e.name}
          </option>
        `)}
    `}_renderMappingOptions(e){if(!this.hass)return W``;const t=null!=e?String(e):"";return W`
      <option value="" ?selected="${""===t}">
<<<<<<< HEAD
        ---${Oa("common.labels.select",this.hass.language)}---
=======
        ---${Ma("common.labels.select",this.hass.language)}---
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      </option>
      ${this.mappings.map(e=>W`
          <option value="${e.id}" ?selected="${t===String(e.id)}">
            ${e.id}: ${e.name}
          </option>
        `)}
    `}_renderDistributorSelector(e,t){var i,s;if(!this.hass)return W``;if(!(null===(i=this.config)||void 0===i?void 0:i.distributors_enabled))return W``;const a=this.hass.language,n=null!=e.distributor_id;return W`
      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.zones.labels.distributor",a)}</span
        >
        <span slot="description"
          >${Oa("panels.zones.labels.distributor_help",a)}</span
=======
          >${Ma("panels.zones.labels.distributor",a)}</span
        >
        <span slot="description"
          >${Ma("panels.zones.labels.distributor_help",a)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <select
          class="settings-input"
          .value="${sn(n?String(e.distributor_id):"")}"
          @change="${i=>this._onZoneDistributorChange(t,e,i)}"
        >
          <option value="" ?selected="${!n}">
<<<<<<< HEAD
            ${Oa("panels.zones.labels.distributor_none",a)}
=======
            ${Ma("panels.zones.labels.distributor_none",a)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </option>
          ${this.distributors.map(t=>W`
              <option
                value="${t.id}"
                ?selected="${e.distributor_id===t.id}"
              >
                ${t.name}
              </option>
            `)}
        </select>
      </ha-settings-row>
      ${n?W`
            <ha-settings-row>
              <span slot="heading"
<<<<<<< HEAD
                >${Oa("panels.zones.labels.outlet_number",a)}</span
              >
              <span slot="description"
                >${Oa("panels.zones.labels.outlet_number_readonly_help",a)}</span
=======
                >${Ma("panels.zones.labels.outlet_number",a)}</span
              >
              <span slot="description"
                >${Ma("panels.zones.labels.outlet_number_readonly_help",a)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              >
              <div class="outlet-readonly">
                <span class="outlet-readonly-value"
                  >${null!==(s=e.outlet_number)&&void 0!==s?s:"—"}</span
                >
                <button
                  class="action-btn secondary"
                  @click="${()=>this._gotoDistributor(e.distributor_id)}"
                >
                  <ha-icon icon="mdi:open-in-new"></ha-icon>
<<<<<<< HEAD
                  ${Oa("panels.zones.labels.configure_on_distributor",a)}
=======
                  ${Ma("panels.zones.labels.configure_on_distributor",a)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
              </div>
            </ha-settings-row>
          `:""}
<<<<<<< HEAD
    `}_onZoneDistributorChange(e,t,i){var s;const a=i.target.value;if(!a)return void this.handleEditZone(e,Object.assign(Object.assign({},t),{[Si]:null,[Ai]:null}));const n=parseInt(a);let o=null!==(s=t.outlet_number)&&void 0!==s?s:null;if(t.distributor_id!==n||null==o){const e=this.zones.filter(e=>e.distributor_id===n&&e.id!==t.id&&null!=e.outlet_number).map(e=>e.outlet_number),i=e.length?Math.max(...e):0;o=Math.min(i+1,6)}this.handleEditZone(e,Object.assign(Object.assign({},t),{[Si]:n,[Ai]:o}))}_gotoDistributor(e){Na(0,Ga("setup","distributors",{params:{distributor:String(e)}}))}renderZone(e,t){var i,s,a,n,o,r,l,d,c,h,u,p,g,m,v,f,_;if(!this.hass)return W``;const b=this._isExpanded(e);return W`
      <ha-card id="zone-${null!==(i=e.id)&&void 0!==i?i:"new"}">
=======
    `}_onZoneDistributorChange(e,t,s){var i;const a=s.target.value;if(!a)return void this.handleEditZone(e,Object.assign(Object.assign({},t),{[Cs]:null,[Es]:null}));const n=parseInt(a);let o=null!==(i=t.outlet_number)&&void 0!==i?i:null;if(t.distributor_id!==n||null==o){const e=this.zones.filter(e=>e.distributor_id===n&&e.id!==t.id&&null!=e.outlet_number).map(e=>e.outlet_number),s=e.length?Math.max(...e):0;o=Math.min(s+1,6)}this.handleEditZone(e,Object.assign(Object.assign({},t),{[Cs]:n,[Es]:o}))}_gotoDistributor(e){Pa(0,Va("setup","distributors",{params:{distributor:String(e)}}))}renderZone(e,t){var s,i,a,n,o,r,l,d,c,h,u,p,g,m,v,f,_;if(!this.hass)return W``;const b=this._isExpanded(e);return W`
      <ha-card id="zone-${null!==(s=e.id)&&void 0!==s?s:"new"}">
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        <div
          class="card-header zone-toggle"
          role="button"
          tabindex="0"
          aria-expanded="${b?"true":"false"}"
          @click="${()=>void 0!==e.id&&this._toggleZone(e.id)}"
          @keydown="${t=>{"Enter"!==t.key&&" "!==t.key||void 0===e.id||(t.preventDefault(),this._toggleZone(e.id))}}"
        >
          <div class="name">${e.name}</div>
          <ha-icon
            class="zone-chevron"
            icon="${b?"mdi:chevron-up":"mdi:chevron-down"}"
          ></ha-icon>
        </div>
        ${b?W`
              <!-- Settings shown directly (no longer collapsible — the calendar that
             used to sit alongside it moved to the Weather & Location tab). -->
              <div class="card-content zone-settings">
                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.name",this.hass.language)}</span
=======
                    >${Ma("panels.zones.labels.name",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <input
                    type="text"
                    class="settings-input"
                    .value="${e.name}"
                    @input="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[pt]:i.target.value}))}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.size",this.hass.language)}
                    (${Ma(this.config,gt)})</span
=======
                    >${Ma("panels.zones.labels.size",this.hass.language)}
                    (${Na(this.config,gt)})</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat(e.size.toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[gt]:s}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.throughput",this.hass.language)}
                    (${Ma(this.config,mt)})</span
=======
                    >${Ma("panels.zones.labels.throughput",this.hass.language)}
                    (${Na(this.config,mt)})</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat(e.throughput.toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[mt]:s}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.soil_type",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Oa("field_help.zone_soil_type",this.hass.language)}</span
=======
                    >${Ma("panels.zones.labels.soil_type",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Ma("field_help.zone_soil_type",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <select
                    class="settings-input"
                    .value="${sn(null!==(s=Object.keys(jt).find(t=>jt[t]===e.drainage_rate))&&void 0!==s?s:"custom")}"
                    @change="${i=>{const s=i.target.value;"custom"!==s&&void 0!==jt[s]&&this.handleEditZone(t,Object.assign(Object.assign({},e),{[zt]:jt[s]}))}}"
                  >
                    <option
                      value="custom"
                      ?selected="${!Object.values(jt).includes(null!==(a=e.drainage_rate)&&void 0!==a?a:-1)}"
                    >
<<<<<<< HEAD
                      ${Oa("panels.zones.labels.soil_types.custom",this.hass.language)}
=======
                      ${Ma("panels.zones.labels.soil_types.custom",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    </option>
                    ${Object.keys(jt).map(t=>W`
                        <option
                          value="${t}"
                          ?selected="${jt[t]===e.drainage_rate}"
                        >
<<<<<<< HEAD
                          ${Oa(`panels.zones.labels.soil_types.${t}`,this.hass.language)}
=======
                          ${Ma(`panels.zones.labels.soil_types.${t}`,this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                        </option>
                      `)}
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.drainage_rate",this.hass.language)}
                    (${Ma(this.config,zt)})</span
                  >
                  <span slot="description"
                    >${Oa("field_help.zone_drainage_rate",this.hass.language)}</span
=======
                    >${Ma("panels.zones.labels.drainage_rate",this.hass.language)}
                    (${Na(this.config,zt)})</span
                  >
                  <span slot="description"
                    >${Ma("field_help.zone_drainage_rate",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat((null!==(n=e.drainage_rate)&&void 0!==n?n:0).toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[zt]:s}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.plant_type",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Oa("field_help.zone_plant_type",this.hass.language)}</span
=======
                    >${Ma("panels.zones.labels.plant_type",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Ma("field_help.zone_plant_type",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <select
                    class="settings-input"
                    .value="${sn(null!==(o=e.plant_type)&&void 0!==o?o:"custom")}"
                    @change="${i=>{const s=i.target.value,a={[At]:s};"custom"!==s&&void 0!==Ut[s]&&(a.kc=Ut[s]),this.handleEditZone(t,Object.assign(Object.assign({},e),a))}}"
                  >
                    <option
                      value="custom"
                      ?selected="${"custom"===(null!==(r=e.plant_type)&&void 0!==r?r:"custom")}"
                    >
<<<<<<< HEAD
                      ${Oa("panels.zones.labels.plant_types.custom",this.hass.language)}
=======
                      ${Ma("panels.zones.labels.plant_types.custom",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    </option>
                    ${Object.keys(Ut).map(t=>W`
                        <option
                          value="${t}"
                          ?selected="${e.plant_type===t}"
                        >
<<<<<<< HEAD
                          ${Oa(`panels.zones.labels.plant_types.${t}`,this.hass.language)}
=======
                          ${Ma(`panels.zones.labels.plant_types.${t}`,this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                        </option>
                      `)}
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.kc",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Oa("field_help.zone_kc",this.hass.language)}</span
=======
                    >${Ma("panels.zones.labels.kc",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Ma("field_help.zone_kc",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.05"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat((null!==(l=e.kc)&&void 0!==l?l:1).toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[St]:s,[At]:"custom"}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.state",this.hass.language)}</span
=======
                    >${Ma("panels.zones.labels.state",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <select
                    class="settings-input"
                    .value="${sn(e.state)}"
                    @change="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[vt]:i.target.value,[ft]:0}))}"
                  >
                    <option
                      value="${Wa.Automatic}"
                      ?selected="${e.state===Wa.Automatic}"
                    >
<<<<<<< HEAD
                      ${Oa("panels.zones.labels.states.automatic",this.hass.language)}
=======
                      ${Ma("panels.zones.labels.states.automatic",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    </option>
                    <option
                      value="${Wa.Manual}"
                      ?selected="${e.state===Wa.Manual}"
                    >
<<<<<<< HEAD
                      ${Oa("panels.zones.labels.states.manual",this.hass.language)}
=======
                      ${Ma("panels.zones.labels.states.manual",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    </option>
                    <option
                      value="${Wa.Disabled}"
                      ?selected="${e.state===Wa.Disabled}"
                    >
<<<<<<< HEAD
                      ${Oa("panels.zones.labels.states.disabled",this.hass.language)}
=======
                      ${Ma("panels.zones.labels.states.disabled",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    </option>
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("common.labels.module",this.hass.language)}</span
=======
                    >${Ma("common.labels.module",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <select
                    class="settings-input"
                    .value="${sn(void 0!==e.module?String(e.module):"")}"
                    @change="${i=>{const s=i.target.value;this.handleEditZone(t,Object.assign(Object.assign({},e),{[_t]:s?parseInt(s):void 0}))}}"
                  >
                    ${this._renderModuleOptions(e.module)}
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.mapping",this.hass.language)}</span
=======
                    >${Ma("panels.zones.labels.mapping",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <select
                    class="settings-input"
                    .value="${sn(void 0!==e.mapping?String(e.mapping):"")}"
                    @change="${i=>{const s=i.target.value;this.handleEditZone(t,Object.assign(Object.assign({},e),{[wt]:s?parseInt(s):void 0}))}}"
                  >
                    ${this._renderMappingOptions(e.mapping)}
                  </select>
                </ha-settings-row>

                ${this._renderDistributorSelector(e,t)}
                ${null!=e.distributor_id?W`<div class="distributor-managed">
<<<<<<< HEAD
                      ${Oa("panels.zones.labels.distributor_managed_note",this.hass.language)}
                    </div>`:W`
                      <ha-settings-row>
                        <span slot="heading"
                          >${Oa("panels.zones.labels.watering_mode",this.hass.language)}</span
                        >
                        <span slot="description"
                          >${Oa("panels.zones.labels.watering_mode_description",this.hass.language)}</span
=======
                      ${Ma("panels.zones.labels.distributor_managed_note",this.hass.language)}
                    </div>`:W`
                      <ha-settings-row>
                        <span slot="heading"
                          >${Ma("panels.zones.labels.watering_mode",this.hass.language)}</span
                        >
                        <span slot="description"
                          >${Ma("panels.zones.labels.watering_mode_description",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                        >
                        <select
                          class="settings-input"
                          .value="${sn(null!==(d=e.watering_mode)&&void 0!==d?d:"classic")}"
                          @change="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Ht]:i.target.value}))}"
                        >
                          <option
                            value="classic"
                            ?selected="${"classic"===(null!==(c=e.watering_mode)&&void 0!==c?c:"classic")}"
                          >
<<<<<<< HEAD
                            ${Oa("panels.zones.labels.watering_modes.classic",this.hass.language)}
=======
                            ${Ma("panels.zones.labels.watering_modes.classic",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                          </option>
                          <option
                            value="service"
                            ?selected="${"service"===e.watering_mode}"
                          >
<<<<<<< HEAD
                            ${Oa("panels.zones.labels.watering_modes.service",this.hass.language)}
=======
                            ${Ma("panels.zones.labels.watering_modes.service",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                          </option>
                          <option
                            value="${zi}"
                            ?selected="${e.watering_mode===zi}"
                          >
<<<<<<< HEAD
                            ${Oa("panels.zones.labels.watering_modes.opensprinkler",this.hass.language)}
=======
                            ${Ma("panels.zones.labels.watering_modes.opensprinkler",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                          </option>
                        </select>
                      </ha-settings-row>

                      ${"service"===e.watering_mode?W`
                            <ha-settings-row>
                              <span slot="heading"
<<<<<<< HEAD
                                >${Oa("panels.zones.labels.run_service",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.run_service_help",this.hass.language)}</span
=======
                                >${Ma("panels.zones.labels.run_service",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Ma("panels.zones.labels.run_service_help",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                              >
                              <ha-entity-picker
                                .hass="${this.hass}"
                                .value="${e.run_service||""}"
                                .includeDomains="${["script"]}"
                                allow-custom-entity
<<<<<<< HEAD
                                @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Dt]:i.detail.value||null}))}"
=======
                                @value-changed="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Mt]:s.detail.value||null}))}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                              ></ha-entity-picker>
                            </ha-settings-row>
                            <ha-settings-row>
                              <span slot="heading"
<<<<<<< HEAD
                                >${Oa("panels.zones.labels.duration_field",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.duration_field_help",this.hass.language)}</span
=======
                                >${Ma("panels.zones.labels.duration_field",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Ma("panels.zones.labels.duration_field_help",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                              >
                              <input
                                type="text"
                                class="settings-input"
<<<<<<< HEAD
                                placeholder="${Oa("panels.zones.labels.duration_field_placeholder",this.hass.language)}"
                                .value="${e.duration_field||"duration"}"
                                @input="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Mt]:i.target.value||void 0}))}"
=======
                                placeholder="${Ma("panels.zones.labels.duration_field_placeholder",this.hass.language)}"
                                .value="${e.duration_field||"duration"}"
                                @input="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Ht]:s.target.value||void 0}))}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                              />
                            </ha-settings-row>
                            <ha-settings-row>
                              <span slot="heading"
<<<<<<< HEAD
                                >${Oa("panels.zones.labels.duration_unit",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.duration_unit_help",this.hass.language)}</span
=======
                                >${Ma("panels.zones.labels.duration_unit",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Ma("panels.zones.labels.duration_unit_help",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                              >
                              <select
                                class="settings-input"
                                .value="${sn(null!==(h=e.duration_unit)&&void 0!==h?h:"seconds")}"
                                @change="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[It]:i.target.value}))}"
                              >
                                <option
                                  value="seconds"
                                  ?selected="${"seconds"===(null!==(u=e.duration_unit)&&void 0!==u?u:"seconds")}"
                                >
<<<<<<< HEAD
                                  ${Oa("panels.zones.labels.duration_units.seconds",this.hass.language)}
=======
                                  ${Ma("panels.zones.labels.duration_units.seconds",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                                </option>
                                <option
                                  value="minutes"
                                  ?selected="${"minutes"===e.duration_unit}"
                                >
<<<<<<< HEAD
                                  ${Oa("panels.zones.labels.duration_units.minutes",this.hass.language)}
=======
                                  ${Ma("panels.zones.labels.duration_units.minutes",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                                </option>
                              </select>
                            </ha-settings-row>
                            <ha-settings-row>
                              <span slot="heading"
<<<<<<< HEAD
                                >${Oa("panels.zones.labels.stop_service",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.stop_service_help",this.hass.language)}</span
=======
                                >${Ma("panels.zones.labels.stop_service",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Ma("panels.zones.labels.stop_service_help",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                              >
                              <ha-entity-picker
                                .hass="${this.hass}"
                                .value="${e.stop_service||""}"
                                .includeDomains="${["script"]}"
                                allow-custom-entity
                                @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Nt]:i.detail.value||null}))}"
                              ></ha-entity-picker>
                            </ha-settings-row>
                            <ha-settings-row>
                              <span slot="heading"
<<<<<<< HEAD
                                >${Oa("panels.zones.labels.confirm_entity",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.confirm_entity_help",this.hass.language)}</span
=======
                                >${Ma("panels.zones.labels.confirm_entity",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Ma("panels.zones.labels.confirm_entity_help",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                              >
                              <ha-entity-picker
                                .hass="${this.hass}"
                                .value="${e.confirm_entity||""}"
                                .includeDomains="${["valve","switch","input_boolean","number","binary_sensor"]}"
                                allow-custom-entity
                                @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Pt]:i.detail.value||null}))}"
                              ></ha-entity-picker>
                            </ha-settings-row>
                            ${(null===(p=this.config)||void 0===p?void 0:p.observed_watering_enabled)?W`
                                  <ha-settings-row>
                                    <span slot="heading"
<<<<<<< HEAD
                                      >${Oa("panels.zones.labels.observed_entity",this.hass.language)}</span
                                    >
                                    <span slot="description"
                                      >${Oa("panels.zones.labels.observed_entity_help",this.hass.language)}</span
=======
                                      >${Ma("panels.zones.labels.observed_entity",this.hass.language)}</span
                                    >
                                    <span slot="description"
                                      >${Ma("panels.zones.labels.observed_entity_help",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                                    >
                                    <ha-entity-picker
                                      .hass="${this.hass}"
                                      .value="${e.observed_entity||""}"
                                      .includeDomains="${["valve","switch","input_boolean"]}"
                                      allow-custom-entity
                                      @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Lt]:i.detail.value||null}))}"
                                    ></ha-entity-picker>
                                  </ha-settings-row>
                                `:""}
                          `:""}
                      ${e.watering_mode===zi?W`
                            <ha-settings-row>
                              <span slot="heading"
<<<<<<< HEAD
                                >${Oa("panels.zones.labels.opensprinkler_station",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.opensprinkler_station_help",this.hass.language)}</span
=======
                                >${Ma("panels.zones.labels.opensprinkler_station",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Ma("panels.zones.labels.opensprinkler_station_help",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                              >
                              <ha-entity-picker
                                .hass="${this.hass}"
                                .value="${e.linked_entity||""}"
                                .includeDomains="${["switch"]}"
                                .entityFilter="${this._osStationFilter}"
                                allow-custom-entity
<<<<<<< HEAD
                                @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Et]:i.detail.value||null}))}"
                              ></ha-entity-picker>
                            </ha-settings-row>
                            ${this._hasOpenSprinklerStations()?"":W`<div class="distributor-managed">
                                  ${Oa("panels.zones.labels.opensprinkler_no_stations",this.hass.language)}
=======
                                @value-changed="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Ct]:s.detail.value||null}))}"
                              ></ha-entity-picker>
                            </ha-settings-row>
                            ${this._hasOpenSprinklerStations()?"":W`<div class="distributor-managed">
                                  ${Ma("panels.zones.labels.opensprinkler_no_stations",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                                </div>`}
                          `:"service"!==e.watering_mode?W`
                              <ha-settings-row>
                                <span slot="heading"
<<<<<<< HEAD
                                  >${Oa("panels.zones.labels.linked_entity",this.hass.language)}</span
=======
                                  >${Ma("panels.zones.labels.linked_entity",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                                >
                                <ha-entity-picker
                                  .hass="${this.hass}"
                                  .value="${e.linked_entity||""}"
                                  .includeDomains="${["switch","valve","input_boolean"]}"
                                  allow-custom-entity
<<<<<<< HEAD
                                  @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Et]:i.detail.value||null}))}"
=======
                                  @value-changed="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Ct]:s.detail.value||null}))}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                                ></ha-entity-picker>
                              </ha-settings-row>
                            `:""}
                    `}

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.soil_moisture_sensor",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Oa("panels.zones.labels.soil_moisture_sensor_help",this.hass.language)}</span
=======
                    >${Ma("panels.zones.labels.soil_moisture_sensor",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Ma("panels.zones.labels.soil_moisture_sensor_help",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <ha-entity-picker
                    .hass="${this.hass}"
                    .value="${e.soil_moisture_sensor||""}"
                    .includeDomains="${["sensor"]}"
                    .includeDeviceClasses="${["moisture"]}"
                    allow-custom-entity
                    @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Rt]:i.detail.value||null}))}"
                  ></ha-entity-picker>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.soil_moisture_threshold",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Oa("panels.zones.labels.soil_moisture_threshold_help",this.hass.language)}</span
=======
                    >${Ma("panels.zones.labels.soil_moisture_threshold",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Ma("panels.zones.labels.soil_moisture_threshold_help",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="1"
                    min="0"
                    max="100"
                    inputmode="decimal"
                    .value="${null!==(g=e.soil_moisture_threshold)&&void 0!==g?g:""}"
                    @input="${i=>{const s=i.target.value,a=""===s?null:Number(s);this.handleEditZone(t,Object.assign(Object.assign({},e),{[Bt]:null===a||isNaN(a)?null:a}))}}"
                  />
                </ha-settings-row>

                ${null==e.distributor_id?W`
                      <ha-settings-row>
                        <span slot="heading"
<<<<<<< HEAD
                          >${Oa("panels.zones.labels.flow_sensor",this.hass.language)}</span
=======
                          >${Ma("panels.zones.labels.flow_sensor",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                        >
                        <ha-entity-picker
                          .hass="${this.hass}"
                          .value="${e.flow_sensor||""}"
                          .includeDomains="${["sensor"]}"
                          allow-custom-entity
                          @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Tt]:i.detail.value||null}))}"
                        ></ha-entity-picker>
                      </ha-settings-row>

                      ${this._flowSensorIsTotalizer(e)?W`
                            <ha-settings-row>
                              <span slot="heading"
<<<<<<< HEAD
                                >${Oa("panels.zones.labels.flow_counter_type",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.flow_counter_type_help",this.hass.language)}</span
=======
                                >${Ma("panels.zones.labels.flow_counter_type",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Ma("panels.zones.labels.flow_counter_type_help",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                              >
                              <select
                                class="settings-input"
                                .value="${sn(e.flow_counter_type||"auto")}"
                                @change="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Ot]:i.target.value||"auto"}))}"
                              >
                                ${["auto","per_run","lifetime"].map(t=>W`
                                    <option
                                      value="${t}"
                                      ?selected="${(e.flow_counter_type||"auto")===t}"
                                    >
<<<<<<< HEAD
                                      ${Oa(`panels.zones.labels.flow_counter_type_${t}`,this.hass.language)}
=======
                                      ${Ma(`panels.zones.labels.flow_counter_type_${t}`,this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                                    </option>
                                  `)}
                              </select>
                            </ha-settings-row>
                          `:""}
                    `:""}

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.bucket",this.hass.language)}
                    (${Ma(this.config,bt)})</span
=======
                    >${Ma("panels.zones.labels.bucket",this.hass.language)}
                    (${Na(this.config,bt)})</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    inputmode="decimal"
                    .value="${parseFloat(Number(e.bucket).toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[bt]:s}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.maximum-bucket",this.hass.language)}
                    (${Ma(this.config,bt)})</span
=======
                    >${Ma("panels.zones.labels.maximum-bucket",this.hass.language)}
                    (${Na(this.config,bt)})</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat(Number(e.maximum_bucket).toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[kt]:s}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.multiplier",this.hass.language)}</span
=======
                    >${Ma("panels.zones.labels.multiplier",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat(e.multiplier.toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[yt]:s}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.lead-time",this.hass.language)}
=======
                    >${Ma("panels.zones.labels.lead-time",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    (${nt})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="1"
                    min="0"
                    inputmode="numeric"
                    .value="${null!==(m=e.lead_time)&&void 0!==m?m:0}"
                    @input="${i=>{const s=i.target.valueAsNumber;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[$t]:Math.round(s)}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.maximum-duration",this.hass.language)}
=======
                    >${Ma("panels.zones.labels.maximum-duration",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    (${nt})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="1"
                    min="0"
                    inputmode="numeric"
                    .value="${null!==(v=e.maximum_duration)&&void 0!==v?v:""}"
                    @input="${i=>{const s=i.target.valueAsNumber;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[xt]:Math.round(s)}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
<<<<<<< HEAD
                    >${Oa("panels.zones.labels.bucket_threshold",this.hass.language)}
                    (${Ma(this.config,bt)})</span
=======
                    >${Ma("panels.zones.labels.bucket_threshold",this.hass.language)}
                    (${Na(this.config,bt)})</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.5"
                    max="0"
                    inputmode="decimal"
                    .value="${parseFloat((null!==(f=e.bucket_threshold)&&void 0!==f?f:0).toFixed(1))}"
<<<<<<< HEAD
                    @input="${i=>{const s=Math.round(10*i.target.valueAsNumber)/10;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[Ct]:Math.min(s,0)}))}}"
=======
                    @input="${s=>{const i=Math.round(10*s.target.valueAsNumber)/10;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[Et]:Math.min(i,0)}))}}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  />
                </ha-settings-row>

                ${e.state===Wa.Manual?W`
                      <ha-settings-row>
                        <span slot="heading"
<<<<<<< HEAD
                          >${Oa("panels.zones.labels.duration",this.hass.language)}
=======
                          >${Ma("panels.zones.labels.duration",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                          (${nt})</span
                        >
                        <input
                          type="number"
                          class="settings-input shortfield"
                          step="1"
                          min="0"
                          inputmode="numeric"
                          .value="${null!==(_=e.duration)&&void 0!==_?_:0}"
                          @input="${i=>{const s=i.target.valueAsNumber;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[ft]:Math.round(s)}))}}"
                        />
                      </ha-settings-row>
                    `:""}

                <!-- Danger row -->
                <div class="settings-danger-row">
                  <button
                    class="action-btn"
<<<<<<< HEAD
                    @click="${()=>{this._pendingConfirm={title:Oa("panels.zones.confirm_action.reset_bucket_title",this.hass.language),body:Oa("panels.zones.confirm_action.reset_bucket_body",this.hass.language),confirmLabel:Oa("panels.zones.actions.reset-bucket",this.hass.language),onConfirm:()=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[bt]:0}))}}}"
                    ?disabled="${this.isSaving}"
                  >
                    ${Oa("panels.zones.actions.reset-bucket",this.hass.language)}
=======
                    @click="${()=>{this._pendingConfirm={title:Ma("panels.zones.confirm_action.reset_bucket_title",this.hass.language),body:Ma("panels.zones.confirm_action.reset_bucket_body",this.hass.language),confirmLabel:Ma("panels.zones.actions.reset-bucket",this.hass.language),onConfirm:()=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[bt]:0}))}}}"
                    ?disabled="${this.isSaving}"
                  >
                    ${Ma("panels.zones.actions.reset-bucket",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </button>
                  <button
                    class="action-btn danger-button"
                    @click="${()=>this.handleRemoveZone(void 0!==e.id?e.id:-1)}"
                    ?disabled="${this.isSaving||void 0===e.id}"
                  >
                    <ha-icon slot="icon" icon="mdi:delete"></ha-icon>
<<<<<<< HEAD
                    ${Oa("common.actions.delete",this.hass.language)}
=======
                    ${Ma("common.actions.delete",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </button>
                </div>
              </div>

              <!-- EXPLANATION EXPANSION -->
              ${e.explanation&&e.explanation.length>0?W`
                    <ha-expansion-panel
<<<<<<< HEAD
                      .header="${Oa("panels.zones.actions.information",this.hass.language)}"
=======
                      .header="${Ma("panels.zones.actions.information",this.hass.language)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    >
                      <div class="card-content">
                        ${es(e.explanation)}
                      </div>
                    </ha-expansion-panel>
                  `:""}

              <!-- Run history + cumulative water usage (WS-2) -->
              ${this._renderRunHistory(e)}

              <!-- Weather records + the watering/seasonal calendar now live on the
             Weather & Location tab (climate is the same for every zone). -->
            `:""}
      </ha-card>
<<<<<<< HEAD
    `}_renderRunHistory(e){var t,i,s;if(!this.hass)return W``;const a=(null===(t=this.config)||void 0===t?void 0:t.units)===De,n=null!==(i=e.run_log)&&void 0!==i?i:[],o=this.hass.language;return W`
      <ha-expansion-panel
        .header="${Oa("panels.zones.history.title",o)}"
=======
    `}_renderRunHistory(e){var t,s,i;if(!this.hass)return W``;const a=(null===(t=this.config)||void 0===t?void 0:t.units)===Me,n=null!==(s=e.run_log)&&void 0!==s?s:[],o=this.hass.language;return W`
      <ha-expansion-panel
        .header="${Ma("panels.zones.history.title",o)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      >
        <div class="card-content">
          <div class="history-usage">
            <span class="history-usage-label"
<<<<<<< HEAD
              >${Oa("panels.zones.history.total_used",o)}</span
=======
              >${Ma("panels.zones.history.total_used",o)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            >
            <span class="history-usage-value"
              >${cn(null!==(s=e.water_used_total)&&void 0!==s?s:0,a)}</span
            >
          </div>
          ${0===n.length?W`<div class="weather-note">
<<<<<<< HEAD
                ${Oa("panels.zones.history.empty",o)}
=======
                ${Ma("panels.zones.history.empty",o)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </div>`:W`
                <table class="history-table">
                  <thead>
                    <tr>
<<<<<<< HEAD
                      <th>${Oa("panels.zones.history.when",o)}</th>
                      <th>${Oa("panels.zones.history.result",o)}</th>
                      <th class="num">
                        ${Oa("panels.zones.history.volume",o)}
                      </th>
                      <th>${Oa("panels.zones.history.detail",o)}</th>
=======
                      <th>${Ma("panels.zones.history.when",o)}</th>
                      <th>${Ma("panels.zones.history.result",o)}</th>
                      <th class="num">
                        ${Ma("panels.zones.history.volume",o)}
                      </th>
                      <th>${Ma("panels.zones.history.detail",o)}</th>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    </tr>
                  </thead>
                  <tbody>
                    ${n.map(e=>this._renderRunLogRow(e,a))}
                  </tbody>
                </table>
              `}
        </div>
      </ha-expansion-panel>
<<<<<<< HEAD
    `}_renderRunLogRow(e,t){const i=this.hass.language,s=Oa(`panels.zones.history.results.${e.result}`,i);let a="";return e.detail&&(a="skipped"===e.result?e.detail.split(",").map(e=>Oa(`panels.zones.outlook.checks.${e}`,i)||e).join(", "):Oa(`panels.zones.fault.${e.detail}`,i)||e.detail),W`
=======
    `}_renderRunLogRow(e,t){const s=this.hass.language,i=Ma(`panels.zones.history.results.${e.result}`,s);let a="";return e.detail&&(a="skipped"===e.result?e.detail.split(",").map(e=>Ma(`panels.zones.outlook.checks.${e}`,s)||e).join(", "):Ma(`panels.zones.fault.${e.detail}`,s)||e.detail),W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      <tr>
        <td>${Ja(e.ts)}</td>
        <td>
          <span class="history-chip history-${e.result}"
            >${s||e.result}</span
          >
        </td>
        <td class="num">
          ${e.volume_l>0?cn(e.volume_l,t):"-"}
        </td>
        <td class="history-detail">${es(a)}</td>
      </tr>
    `}render(){var e;if(!this.hass)return W``;if(this.isLoading)return W`
<<<<<<< HEAD
        <ha-card header="${Oa("panels.zones.title",this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Oa("common.loading-messages.general",this.hass.language)}
=======
        <ha-card header="${Ma("panels.zones.title",this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Ma("common.loading-messages.general",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </div>
          </div>
        </ha-card>
      `;const t=null!==this._confirmDeleteZoneId?this.zones.find(e=>e.id===this._confirmDeleteZoneId):null;return W`
      <!-- Header: title + save chip + add zone -->
      <ha-card>
        <div class="card-header">
          <div class="name">
<<<<<<< HEAD
            ${Oa("panels.zones.title",this.hass.language)}
          </div>
          ${this._renderSaveStatus()}
          <ha-icon-button
            .path="${ja}"
            title="${Oa("panels.zones.cards.add-zone.header",this.hass.language)}"
=======
            ${Ma("panels.zones.title",this.hass.language)}
          </div>
          ${this._renderSaveStatus()}
          <ha-icon-button
            .path="${Za}"
            title="${Ma("panels.zones.cards.add-zone.header",this.hass.language)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            @click="${()=>{this._showAddZone=!0}}"
          ></ha-icon-button>
        </div>
        ${0===this.zones.length?W`<div class="card-content">
              <div class="weather-note">
<<<<<<< HEAD
                ${Oa("panels.zones.no_items",this.hass.language)}
=======
                ${Ma("panels.zones.no_items",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </div>
            </div>`:""}
      </ha-card>

      <!-- Add Zone dialog -->
      <ha-dialog
        .open="${this._showAddZone}"
        @closed="${()=>{this._showAddZone=!1}}"
<<<<<<< HEAD
        heading="${Oa("panels.zones.cards.add-zone.header",this.hass.language)}"
=======
        heading="${Ma("panels.zones.cards.add-zone.header",this.hass.language)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      >
        <div class="add-zone-form">
          <si-zone-form
            .hass="${this.hass}"
<<<<<<< HEAD
            .metric="${(null===(e=this.config)||void 0===e?void 0:e.units)===De}"
=======
            .metric="${(null===(e=this.config)||void 0===e?void 0:e.units)===Me}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            .name="${this._newZoneName}"
            .size="${this._newZoneSize}"
            .throughput="${this._newZoneThroughput}"
            .linkedEntity="${this._newZoneEntity}"
            showEntity
            @name-changed="${e=>{this._newZoneName=e.detail.value}}"
            @size-changed="${e=>{this._newZoneSize=e.detail.value}}"
            @throughput-changed="${e=>{this._newZoneThroughput=e.detail.value}}"
            @entity-changed="${e=>{this._newZoneEntity=e.detail.value}}"
          ></si-zone-form>
        </div>
        <div class="dialog-footer">
          <button
            class="dialog-btn"
            @click="${()=>{this._showAddZone=!1}}"
          >
<<<<<<< HEAD
            ${Oa("common.actions.cancel",this.hass.language)}
=======
            ${Ma("common.actions.cancel",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </button>
          <button
            class="dialog-btn dialog-btn-primary"
            @click="${this.handleAddZone}"
            ?disabled="${!this._newZoneName.trim()||this.isSaving}"
          >
<<<<<<< HEAD
            ${this.isSaving?Oa("common.saving-messages.adding",this.hass.language):Oa("panels.zones.cards.add-zone.actions.add",this.hass.language)}
=======
            ${this.isSaving?Ma("common.saving-messages.adding",this.hass.language):Ma("panels.zones.cards.add-zone.actions.add",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </button>
        </div>
      </ha-dialog>

      <!-- Delete confirmation dialog -->
      ${t?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmDeleteZoneId=null}}"
<<<<<<< HEAD
              heading="${Oa("common.actions.confirm_delete",this.hass.language)}"
            >
              <p>
                ${Oa("common.actions.confirm_delete_zone",this.hass.language)}
=======
              heading="${Ma("common.actions.confirm_delete",this.hass.language)}"
            >
              <p>
                ${Ma("common.actions.confirm_delete_zone",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </p>
              <p><strong>${t.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmDeleteZoneId=null}}"
                >
<<<<<<< HEAD
                  ${Oa("common.actions.cancel",this.hass.language)}
=======
                  ${Ma("common.actions.cancel",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
                <button
                  class="dialog-btn dialog-btn-danger"
                  @click="${this._confirmDelete}"
                >
<<<<<<< HEAD
                  ${Oa("common.actions.delete",this.hass.language)}
=======
                  ${Ma("common.actions.delete",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Generic destructive-action confirmation dialog -->
      ${this._pendingConfirm?W`
            <ha-dialog
              open
              @closed="${()=>{this._pendingConfirm=null}}"
              heading="${this._pendingConfirm.title}"
            >
              <p>${this._pendingConfirm.body}</p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._pendingConfirm=null}}"
                >
<<<<<<< HEAD
                  ${Oa("common.actions.cancel",this.hass.language)}
=======
                  ${Ma("common.actions.cancel",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
                <button
                  class="dialog-btn dialog-btn-danger"
                  @click="${this._runPendingConfirm}"
                >
                  ${this._pendingConfirm.confirmLabel}
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Zone cards -->
      ${this.zones.map((e,t)=>this.renderZone(e,t))}

      <!-- Maintenance (destructive) -->
      <ha-card>
        <div class="card-header">
          <div class="name">
<<<<<<< HEAD
            ${Oa("common.labels.bulk_actions",this.hass.language)}
=======
            ${Ma("common.labels.bulk_actions",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </div>
        </div>
        <div class="card-content bulk-actions">
          <button
            class="action-btn danger-button"
<<<<<<< HEAD
            @click="${()=>{this._pendingConfirm={title:Oa("panels.zones.confirm_action.reset_all_buckets_title",this.hass.language),body:Oa("panels.zones.confirm_action.reset_all_buckets_body",this.hass.language),confirmLabel:Oa("panels.zones.cards.zone-actions.actions.reset-all-buckets",this.hass.language),onConfirm:()=>this.handleResetAllBuckets()}}}"
            ?disabled="${this.isSaving}"
          >
            ${Oa("panels.zones.cards.zone-actions.actions.reset-all-buckets",this.hass.language)}
          </button>
          <button
            class="action-btn danger-button"
            @click="${()=>{this._pendingConfirm={title:Oa("panels.zones.confirm_action.clear_weather_title",this.hass.language),body:Oa("panels.zones.confirm_action.clear_weather_body",this.hass.language),confirmLabel:Oa("panels.zones.cards.zone-actions.actions.clear-all-weatherdata",this.hass.language),onConfirm:()=>this.handleClearAllWeatherdata()}}}"
            ?disabled="${this.isSaving}"
          >
            ${Oa("panels.zones.cards.zone-actions.actions.clear-all-weatherdata",this.hass.language)}
=======
            @click="${()=>{this._pendingConfirm={title:Ma("panels.zones.confirm_action.reset_all_buckets_title",this.hass.language),body:Ma("panels.zones.confirm_action.reset_all_buckets_body",this.hass.language),confirmLabel:Ma("panels.zones.cards.zone-actions.actions.reset-all-buckets",this.hass.language),onConfirm:()=>this.handleResetAllBuckets()}}}"
            ?disabled="${this.isSaving}"
          >
            ${Ma("panels.zones.cards.zone-actions.actions.reset-all-buckets",this.hass.language)}
          </button>
          <button
            class="action-btn danger-button"
            @click="${()=>{this._pendingConfirm={title:Ma("panels.zones.confirm_action.clear_weather_title",this.hass.language),body:Ma("panels.zones.confirm_action.clear_weather_body",this.hass.language),confirmLabel:Ma("panels.zones.cards.zone-actions.actions.clear-all-weatherdata",this.hass.language),onConfirm:()=>this.handleClearAllWeatherdata()}}}"
            ?disabled="${this.isSaving}"
          >
            ${Ma("panels.zones.cards.zone-actions.actions.clear-all-weatherdata",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </button>
        </div>
      </ha-card>
    `}disconnectedCallback(){super.disconnectedCallback(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null),this._savedResetTimer&&(clearTimeout(this._savedResetTimer),this._savedResetTimer=null)}static get styles(){return r`
      ${Ka}

      .card-header.zone-toggle {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        user-select: none;
      }
      .card-header.zone-toggle:hover {
        background: var(--secondary-background-color);
      }
      .card-header .zone-chevron {
        color: var(--secondary-text-color);
        flex: 0 0 auto;
      }

      ha-settings-row {
        padding: 0 16px;
      }

      ha-expansion-panel {
        border-top: 1px solid var(--divider-color);
      }

      .shortfield {
        width: 120px;
      }

      /* Note shown in place of the actuation rows when a zone is watered
         through a distributor outlet (Plan F). */
      .distributor-managed {
        margin: 6px 16px;
        padding: 8px 10px;
        font-size: 0.85rem;
        line-height: 1.45;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border-left: 3px solid var(--primary-color);
        border-radius: 0 3px 3px 0;
      }

      /* Read-only outlet number + deep-link to the distributor page (FB). */
      .outlet-readonly {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .outlet-readonly-value {
        font-size: 0.9375rem;
        font-weight: 600;
        min-width: 20px;
      }

      /* Run history (WS-2) */
      .history-usage {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 12px;
      }
      .history-usage-value {
        font-size: 1.25rem;
        font-weight: 600;
      }
      .history-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.875rem;
      }
      .history-table th,
      .history-table td {
        text-align: left;
        padding: 4px 8px;
        border-bottom: 1px solid var(--divider-color);
        vertical-align: top;
      }
      .history-table th.num,
      .history-table td.num {
        text-align: right;
        white-space: nowrap;
      }
      .history-detail {
        color: var(--secondary-text-color);
      }
      .history-chip {
        display: inline-block;
        padding: 1px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 600;
        white-space: nowrap;
        color: #fff;
        background: var(--secondary-text-color);
      }
      .history-completed {
        background: var(--success-color, #2e7d32);
      }
      .history-partial {
        background: var(--warning-color, #f9a825);
      }
      .history-failed {
        background: var(--error-color, #c62828);
      }
      .history-skipped {
        background: var(--info-color, #0277bd);
      }
      .history-observed {
        background: #00897b;
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
    `}};t([me()],un.prototype,"config",void 0),t([me({attribute:!1})],un.prototype,"path",void 0),t([me({type:Array})],un.prototype,"zones",void 0),t([me({type:Array})],un.prototype,"modules",void 0),t([me({type:Array})],un.prototype,"mappings",void 0),t([me({type:Array})],un.prototype,"distributors",void 0),t([me({type:Boolean})],un.prototype,"isLoading",void 0),t([ve()],un.prototype,"_expanded",void 0),t([me({type:Boolean})],un.prototype,"isSaving",void 0),t([me({type:Boolean})],un.prototype,"_showAddZone",void 0),t([ve()],un.prototype,"_pendingConfirm",void 0),t([ve()],un.prototype,"_saveStatus",void 0),t([me()],un.prototype,"_confirmDeleteZoneId",void 0),t([me()],un.prototype,"_newZoneName",void 0),t([me()],un.prototype,"_newZoneSize",void 0),t([me()],un.prototype,"_newZoneThroughput",void 0),t([me()],un.prototype,"_newZoneEntity",void 0),un=t([ue("smart-irrigation-view-zone-settings")],un);let pn=class extends ce{_emit(e){this.dispatchEvent(new CustomEvent("distributor-changed",{detail:{value:Object.assign(Object.assign({},this.distributor),e)},bubbles:!0,composed:!0}))}_onNumber(e,t){const i=t.target.valueAsNumber;isNaN(i)||this._emit({[e]:Math.max(0,Math.round(i))})}render(){var e,t,i,s;if(!this.hass||!this.distributor)return W``;const a=this.hass.language,n=this.distributor,o=n.watering_mode===ki;return W`
      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.distributors.labels.name",a)}</span
=======
          >${Ma("panels.distributors.labels.name",a)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <input
          type="text"
          class="settings-input"
          .value="${null!==(e=n.name)&&void 0!==e?e:""}"
          @input="${e=>this._emit({[ci]:e.target.value})}"
        />
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.zones.labels.watering_mode",a)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.watering_mode_help",a)}</span
=======
          >${Ma("panels.zones.labels.watering_mode",a)}</span
        >
        <span slot="description"
          >${Ma("panels.distributors.labels.watering_mode_help",a)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <select
          class="settings-input"
          .value="${sn(null!==(t=n.watering_mode)&&void 0!==t?t:xi)}"
          @change="${e=>this._emit({[hi]:e.target.value})}"
        >
          <option
            value="${xi}"
            ?selected="${(null!==(i=n.watering_mode)&&void 0!==i?i:xi)===xi}"
          >
<<<<<<< HEAD
            ${Oa("panels.zones.labels.watering_modes.classic",a)}
=======
            ${Ma("panels.zones.labels.watering_modes.classic",a)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </option>
          <option
            value="${ki}"
            ?selected="${n.watering_mode===ki}"
          >
<<<<<<< HEAD
            ${Oa("panels.zones.labels.watering_modes.service",a)}
=======
            ${Ma("panels.zones.labels.watering_modes.service",a)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </option>
        </select>
      </ha-settings-row>

      ${o?this._renderServiceRows(a):""}
      ${this._renderInletWatchRows(a)} ${this._renderSensorRows(a)}
      ${this._renderTimingRows(a)}

      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.distributors.labels.notify_target",a)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.notify_target_help",a)}</span
=======
          >${Ma("panels.distributors.labels.notify_target",a)}</span
        >
        <span slot="description"
          >${Ma("panels.distributors.labels.notify_target_help",a)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <input
          type="text"
          class="settings-input"
<<<<<<< HEAD
          placeholder="${Oa("panels.distributors.labels.notify_target_placeholder",a)}"
          .value="${null!==(s=n.notify_target)&&void 0!==s?s:""}"
          @input="${e=>this._emit({[yi]:e.target.value||null})}"
=======
          placeholder="${Ma("panels.distributors.labels.notify_target_placeholder",a)}"
          .value="${null!==(i=n.notify_target)&&void 0!==i?i:""}"
          @input="${e=>this._emit({[$s]:e.target.value||null})}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        />
      </ha-settings-row>
    `}_renderInletWatchRows(e){var t;const i=this.distributor,s=i.watering_mode===ki?"panels.distributors.labels.inlet_entity_help_service":"panels.distributors.labels.inlet_entity_help",a=null!==(t=i.watch_mode)&&void 0!==t?t:"ignore";return W`
      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.distributors.labels.inlet_entity",e)}</span
        >
        <span slot="description">${Oa(s,e)}</span>
=======
          >${Ma("panels.distributors.labels.inlet_entity",e)}</span
        >
        <span slot="description">${Ma(i,e)}</span>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${i.inlet_entity||""}"
          .includeDomains="${["switch","valve","input_boolean"]}"
          allow-custom-entity
          @value-changed="${e=>this._emit({[ui]:e.detail.value||null})}"
        ></ha-entity-picker>
      </ha-settings-row>

      <!-- No inlet_entity => nothing to watch => the watch_mode row is hidden. -->
      ${i.inlet_entity?W`
            <ha-settings-row>
              <span slot="heading"
<<<<<<< HEAD
                >${Oa("panels.distributors.labels.watch_mode",e)}</span
              >
              <span slot="description"
                >${Oa("panels.distributors.labels.watch_mode_help",e)}</span
=======
                >${Ma("panels.distributors.labels.watch_mode",e)}</span
              >
              <span slot="description"
                >${Ma("panels.distributors.labels.watch_mode_help",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              >
              <select
                class="settings-input"
                .value="${sn(a)}"
                @change="${e=>this._emit({[pi]:e.target.value})}"
              >
                ${$i.map(t=>W`
                    <option value="${t}" ?selected="${a===t}">
<<<<<<< HEAD
                      ${Oa(`panels.distributors.labels.watch_mode_${t}`,e)}
=======
                      ${Ma(`panels.distributors.labels.watch_mode_${t}`,e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    </option>
                  `)}
              </select>
            </ha-settings-row>
          `:""}
    `}_renderServiceRows(e){var t,i;const s=this.distributor;return W`
      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.distributors.labels.run_service",e)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.run_service_help",e)}</span
=======
          >${Ma("panels.distributors.labels.run_service",e)}</span
        >
        <span slot="description"
          >${Ma("panels.distributors.labels.run_service_help",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${s.run_service||""}"
          .includeDomains="${["script"]}"
          allow-custom-entity
          @value-changed="${e=>this._emit({[gi]:e.detail.value||null})}"
        ></ha-entity-picker>
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.distributors.labels.duration_field",e)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.duration_field_help",e)}</span
=======
          >${Ma("panels.distributors.labels.duration_field",e)}</span
        >
        <span slot="description"
          >${Ma("panels.distributors.labels.duration_field_help",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <input
          type="text"
          class="settings-input"
<<<<<<< HEAD
          placeholder="${Oa("panels.distributors.labels.duration_field_placeholder",e)}"
          .value="${s.duration_field||"duration"}"
          @input="${e=>this._emit({[vi]:e.target.value||"duration"})}"
=======
          placeholder="${Ma("panels.distributors.labels.duration_field_placeholder",e)}"
          .value="${i.duration_field||"duration"}"
          @input="${e=>this._emit({[_s]:e.target.value||"duration"})}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        />
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.distributors.labels.duration_unit",e)}</span
=======
          >${Ma("panels.distributors.labels.duration_unit",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <select
          class="settings-input"
          .value="${sn(null!==(t=s.duration_unit)&&void 0!==t?t:"seconds")}"
          @change="${e=>this._emit({[fi]:e.target.value})}"
        >
          <option
            value="seconds"
            ?selected="${"seconds"===(null!==(i=s.duration_unit)&&void 0!==i?i:"seconds")}"
          >
<<<<<<< HEAD
            ${Oa("panels.distributors.labels.duration_units.seconds",e)}
          </option>
          <option value="minutes" ?selected="${"minutes"===s.duration_unit}">
            ${Oa("panels.distributors.labels.duration_units.minutes",e)}
=======
            ${Ma("panels.distributors.labels.duration_units.seconds",e)}
          </option>
          <option value="minutes" ?selected="${"minutes"===i.duration_unit}">
            ${Ma("panels.distributors.labels.duration_units.minutes",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </option>
        </select>
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.distributors.labels.stop_service",e)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.stop_service_help",e)}</span
=======
          >${Ma("panels.distributors.labels.stop_service",e)}</span
        >
        <span slot="description"
          >${Ma("panels.distributors.labels.stop_service_help",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${s.stop_service||""}"
          .includeDomains="${["script"]}"
          allow-custom-entity
          @value-changed="${e=>this._emit({[mi]:e.detail.value||null})}"
        ></ha-entity-picker>
      </ha-settings-row>
    `}_renderSensorRows(e){const t=this.distributor;return W`
      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.distributors.labels.confirm_entity",e)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.confirm_entity_help",e)}</span
=======
          >${Ma("panels.distributors.labels.confirm_entity",e)}</span
        >
        <span slot="description"
          >${Ma("panels.distributors.labels.confirm_entity_help",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${t.confirm_entity||""}"
          .includeDomains="${["binary_sensor","sensor","switch","valve","input_boolean"]}"
          allow-custom-entity
          @value-changed="${e=>this._emit({[_i]:e.detail.value||null})}"
        ></ha-entity-picker>
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.distributors.labels.flow_sensor",e)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.flow_sensor_help",e)}</span
=======
          >${Ma("panels.distributors.labels.flow_sensor",e)}</span
        >
        <span slot="description"
          >${Ma("panels.distributors.labels.flow_sensor_help",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${t.flow_sensor||""}"
          .includeDomains="${["sensor"]}"
          allow-custom-entity
          @value-changed="${e=>this._emit({[bi]:e.detail.value||null})}"
        ></ha-entity-picker>
      </ha-settings-row>
    `}_renderTimingRows(e){var t,i,s,a;const n=this.distributor,o=(null!==(t=n.pause_seconds)&&void 0!==t?t:0)<10,r=(null!==(i=n.skip_pulse_seconds)&&void 0!==i?i:0)<10;return W`
      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.distributors.labels.pause_seconds",e)}
          (${nt})</span
        >
        <span slot="description"
          >${Oa("field_help.distributor_pause_seconds",e)}</span
=======
          >${Ma("panels.distributors.labels.pause_seconds",e)}
          (${nt})</span
        >
        <span slot="description"
          >${Ma("field_help.distributor_pause_seconds",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <input
          type="number"
          class="settings-input shortfield"
          step="1"
          min="${10}"
          inputmode="numeric"
          .value="${null!==(s=n.pause_seconds)&&void 0!==s?s:""}"
          @input="${e=>this._onNumber("pause_seconds",e)}"
        />
      </ha-settings-row>
      ${o?W`<div class="timing-warning">
<<<<<<< HEAD
            ${Oa("panels.distributors.hints.below_floor_pause",e)}
=======
            ${Ma("panels.distributors.hints.below_floor_pause",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </div>`:""}

      <ha-settings-row>
        <span slot="heading"
<<<<<<< HEAD
          >${Oa("panels.distributors.labels.skip_pulse_seconds",e)}
          (${nt})</span
        >
        <span slot="description"
          >${Oa("field_help.distributor_skip_pulse_seconds",e)}</span
=======
          >${Ma("panels.distributors.labels.skip_pulse_seconds",e)}
          (${nt})</span
        >
        <span slot="description"
          >${Ma("field_help.distributor_skip_pulse_seconds",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
        <input
          type="number"
          class="settings-input shortfield"
          step="1"
          min="${10}"
          inputmode="numeric"
          .value="${null!==(a=n.skip_pulse_seconds)&&void 0!==a?a:""}"
          @input="${e=>this._onNumber("skip_pulse_seconds",e)}"
        />
      </ha-settings-row>
      ${r?W`<div class="timing-warning">
<<<<<<< HEAD
            ${Oa("panels.distributors.hints.below_floor_skip",e)}
=======
            ${Ma("panels.distributors.hints.below_floor_skip",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </div>`:""}
    `}static get styles(){return r`
      ${Ka}

      :host {
        display: block;
      }

      ha-settings-row {
        padding: 0 16px;
      }

      .settings-input {
        height: 36px;
      }

      .json-input {
        width: 100%;
        min-width: 220px;
        height: auto;
        font-family: var(--code-font-family, monospace);
        font-size: 0.85rem;
        resize: vertical;
      }

      .json-input.invalid {
        border-color: var(--error-color);
      }

      .json-error {
        color: var(--error-color);
        font-size: 0.8rem;
        padding: 0 16px 6px;
      }

      /* Live "below the enforced floor" note under a timing field. */
      .timing-warning {
        color: var(--warning-color, #f9a825);
        background: var(--secondary-background-color);
        border-left: 3px solid var(--warning-color, #f9a825);
        border-radius: 0 3px 3px 0;
        font-size: 0.82rem;
        line-height: 1.45;
        margin: 0 16px 6px;
        padding: 6px 10px;
      }
    `}};t([me({attribute:!1})],pn.prototype,"hass",void 0),t([me({attribute:!1})],pn.prototype,"distributor",void 0),pn=t([ue("si-distributor-form")],pn);let gn=class extends(Fa(ce)){constructor(){super(...arguments),this.distributors=[],this.zones=[],this.isLoading=!0,this.isSaving=!1,this._initialLoadDone=!1,this._scrolledToDist=null,this._expanded=new Set,this._showAdd=!1,this._newName="",this._confirmDeleteId=null,this._armConfirmId=null,this._confirmResyncHomeId=null,this._confirmSetOutletId=null,this._outletDraft={},this._outletRows={},this._saveStatus="idle",this._savedResetTimer=null,this.globalDebounceTimer=null,this._updateScheduled=!1}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}_isExpanded(e){return void 0!==e.id&&this._expanded.has(e.id)}_toggle(e){const t=new Set(this._expanded);t.has(e)?t.delete(e):t.add(e),this._expanded=t}firstUpdated(){qi().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}updated(){var e,t,i;const s=null===(t=null===(e=this.path)||void 0===e?void 0:e.params)||void 0===t?void 0:t.distributor;if(null==s||""===s||this.isLoading)return;const a=Number(s);if(Number.isNaN(a)||this._scrolledToDist===a)return;if(!this._expanded.has(a))return void(this._expanded=new Set(this._expanded).add(a));const n=null===(i=this.shadowRoot)||void 0===i?void 0:i.querySelector(`#distributor-${a}`);n&&(this._scrolledToDist=a,requestAnimationFrame(()=>n.scrollIntoView({behavior:"smooth",block:"start"})))}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial distributor data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to refetch on config update:",e)})},{type:be+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[t,i,s]=await Promise.all([Ei(this.hass),Ri(this.hass),Ti(this.hass)]);this.config=t,this.distributors=i,this.zones=s,this._initialLoadDone=!0}catch(e){console.error("Error fetching distributor data:",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}handleAdd(){this.hass&&this._newName.trim()&&(this.isSaving=!0,this._showAdd=!1,Bi(this.hass,{name:this._newName.trim()}).then(()=>(this._newName="",this._fetchData())).catch(e=>{console.error("Failed to add distributor:",e),Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}))}_configPayload(e){var t,i,s,a,n,o,r;return{id:e.id,name:e.name,watering_mode:e.watering_mode,inlet_entity:null!==(t=e.inlet_entity)&&void 0!==t?t:null,watch_mode:null!==(i=e.watch_mode)&&void 0!==i?i:"ignore",run_service:null!==(s=e.run_service)&&void 0!==s?s:null,stop_service:null!==(a=e.stop_service)&&void 0!==a?a:null,duration_field:e.duration_field,duration_unit:e.duration_unit,confirm_entity:null!==(n=e.confirm_entity)&&void 0!==n?n:null,flow_sensor:null!==(o=e.flow_sensor)&&void 0!==o?o:null,pause_seconds:e.pause_seconds,skip_pulse_seconds:e.skip_pulse_seconds,notify_target:null!==(r=e.notify_target)&&void 0!==r?r:null,use_master:e.use_master}}handleEditDistributor(e,t){this.hass&&(this.distributors=this.distributors.map((i,s)=>s===e?t:i),this.globalDebounceTimer&&clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=window.setTimeout(()=>{this.isSaving=!0,this._saveStatus="saving",Bi(this.hass,this._configPayload(t)).then(()=>this._markSaved()).catch(e=>{console.error("Failed to save distributor:",e),this._saveStatus="idle",Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}),this.globalDebounceTimer=null},500),this._scheduleUpdate())}_confirmDelete(){const e=this._confirmDeleteId;if(null===e||!this.hass)return;const t=[...this.distributors];var i,s;this.distributors=this.distributors.filter(t=>t.id!==e),this._confirmDeleteId=null,this.isSaving=!0,(i=this.hass,s=e,i.callApi("POST",be+"/distributors",{id:s,remove:!0})).catch(e=>{console.error("Failed to delete distributor:",e),Ba(this,this.hass,"common.errors.delete_failed",e),this.distributors=t}).finally(()=>{this.isSaving=!1,this._fetchData().catch(()=>{})})}_callAction(e){this.hass&&(this.isSaving=!0,this._scheduleUpdate(),e.catch(e=>{console.error("Distributor action failed:",e),Ba(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(()=>{})}))}_testRun(e){var t,i;this._callAction((t=this.hass,i=e,t.callService(be,"distributor_test_run",{distributor_id:i})))}_setOutlet(e,t){var i;const s=null!==(i=this._outletDraft[e])&&void 0!==i?i:t;this._callAction(((e,t,i)=>e.callService(be,"distributor_set_outlet",{distributor_id:t,outlet:i}))(this.hass,e,s))}_confirmSetOutlet(){const e=this._confirmSetOutletId;if(this._confirmSetOutletId=null,null===e)return;const t=this.distributors.find(t=>t.id===e);t&&this._setOutlet(e,t.current_outlet)}_resyncHome(e){var t,i;this._callAction((t=this.hass,i=e,t.callService(be,"distributor_resync_home",{distributor_id:i})))}_confirmResyncHome(){const e=this._confirmResyncHomeId;this._confirmResyncHomeId=null,null!==e&&this._resyncHome(e)}_runNow(e){var t,i;this._callAction((t=this.hass,i=e,t.callService(be,"distributor_run_now",{distributor_id:i})))}_setArmed(e,t){this.hass&&(this._armConfirmId=null,this.distributors=this.distributors.map(i=>i.id===e?Object.assign(Object.assign({},i),{commissioning_confirmed:t}):i),this.isSaving=!0,Bi(this.hass,{id:e,[wi]:t}).catch(e=>{console.error("Failed to set commissioning state:",e),Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(()=>{})}))}_onArmToggle(e,t){void 0!==e.id&&(t?this._armConfirmId=e.id:this._setArmed(e.id,!1))}_markSaved(){this._saveStatus="saved",this._savedResetTimer&&clearTimeout(this._savedResetTimer),this._savedResetTimer=window.setTimeout(()=>{this._saveStatus="idle",this._scheduleUpdate()},2e3),this._scheduleUpdate()}_renderSaveStatus(){if(!this.hass||"idle"===this._saveStatus)return W``;const e="saving"===this._saveStatus;return W`
      <span class="save-status ${this._saveStatus}">
        <ha-icon
          icon="${e?"mdi:content-save-outline":"mdi:check-circle"}"
        ></ha-icon>
<<<<<<< HEAD
        ${Oa(e?"common.saving-messages.saving":"panels.distributors.status.saved",this.hass.language)}
      </span>
    `}_hasOwnActuation(e){return!!(e.linked_entity||e.run_service||e.stop_service)}_membersByOutlet(e){const t=new Map;if(void 0===e)return t;for(const i of this.zones)i.distributor_id===e&&null!=i.outlet_number&&void 0!==i.id&&t.set(i.outlet_number,i);return t}_outletCount(e){const t=this._membersByOutlet(e.id),i=t.size?Math.max(...t.keys()):0,s=Math.max(2,i),a=void 0!==e.id?this._outletRows[e.id]:void 0;return Math.min(6,Math.max(s,null!=a?a:s))}_assignZone(e,t,i){return Oi(this.hass,{id:e.id,[Si]:t,[Ai]:i})}_optimisticZone(e,t,i){void 0!==e&&(this.zones=this.zones.map(s=>s.id===e?Object.assign(Object.assign({},s),{distributor_id:t,outlet_number:i}):s))}_runAssign(e){e.length&&(this.isSaving=!0,this._saveStatus="saving",this._scheduleUpdate(),Promise.all(e).then(()=>this._markSaved()).catch(e=>{console.error("Failed to assign zone to outlet:",e),this._saveStatus="idle",Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(()=>{})}))}_setOutletCount(e,t){if(void 0===e.id)return;const i=this._membersByOutlet(e.id),s=[];for(const[e,a]of i)e>t&&s.push(a);this._outletRows=Object.assign(Object.assign({},this._outletRows),{[e.id]:t}),s.length?(s.forEach(e=>this._optimisticZone(e.id,null,null)),this._runAssign(s.map(e=>this._assignZone(e,null,null)))):this._scheduleUpdate()}_onOutletZoneChange(e,t,i){const s=i.target.value,a=s?parseInt(s):null,n=this._membersByOutlet(e.id).get(t),o=null!==a?this.zones.find(e=>e.id===a):null,r=[];n&&n.id!==a&&(r.push(this._assignZone(n,null,null)),this._optimisticZone(n.id,null,null)),o&&(r.push(this._assignZone(o,e.id,t)),this._optimisticZone(o.id,e.id,t)),this._runAssign(r)}_renderOutletConfig(e){if(!this.hass)return W``;const t=this.hass.language,i=this._membersByOutlet(e.id),s=this._outletCount(e),a=this.zones.filter(e=>void 0!==e.id&&null==e.distributor_id&&!this._hasOwnActuation(e)),n=[...i.keys()].sort((e,t)=>e-t),o=n.some((e,t)=>e!==t+1),r=[];for(let n=1;n<=s;n++){const s=i.get(n),o=s?[...a,s]:[...a];o.sort((e,t)=>(e.name||"").localeCompare(t.name||"")),r.push(W`
        <div class="outlet-row">
          <span class="outlet-label"
            >${Oa("panels.distributors.commissioning.outlet",t)}
=======
        ${Ma(e?"common.saving-messages.saving":"panels.distributors.status.saved",this.hass.language)}
      </span>
    `}_hasOwnActuation(e){return!!(e.linked_entity||e.run_service||e.stop_service)}_membersByOutlet(e){const t=new Map;if(void 0===e)return t;for(const s of this.zones)s.distributor_id===e&&null!=s.outlet_number&&void 0!==s.id&&t.set(s.outlet_number,s);return t}_outletCount(e){const t=this._membersByOutlet(e.id),s=t.size?Math.max(...t.keys()):0,i=Math.max(2,s),a=void 0!==e.id?this._outletRows[e.id]:void 0;return Math.min(6,Math.max(i,null!=a?a:i))}_assignZone(e,t,s){return Ms(this.hass,{id:e.id,[Cs]:t,[Es]:s})}_optimisticZone(e,t,s){void 0!==e&&(this.zones=this.zones.map(i=>i.id===e?Object.assign(Object.assign({},i),{distributor_id:t,outlet_number:s}):i))}_runAssign(e){e.length&&(this.isSaving=!0,this._saveStatus="saving",this._scheduleUpdate(),Promise.all(e).then(()=>this._markSaved()).catch(e=>{console.error("Failed to assign zone to outlet:",e),this._saveStatus="idle",ja(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(()=>{})}))}_setOutletCount(e,t){if(void 0===e.id)return;const s=this._membersByOutlet(e.id),i=[];for(const[e,a]of s)e>t&&i.push(a);this._outletRows=Object.assign(Object.assign({},this._outletRows),{[e.id]:t}),i.length?(i.forEach(e=>this._optimisticZone(e.id,null,null)),this._runAssign(i.map(e=>this._assignZone(e,null,null)))):this._scheduleUpdate()}_onOutletZoneChange(e,t,s){const i=s.target.value,a=i?parseInt(i):null,n=this._membersByOutlet(e.id).get(t),o=null!==a?this.zones.find(e=>e.id===a):null,r=[];n&&n.id!==a&&(r.push(this._assignZone(n,null,null)),this._optimisticZone(n.id,null,null)),o&&(r.push(this._assignZone(o,e.id,t)),this._optimisticZone(o.id,e.id,t)),this._runAssign(r)}_renderOutletConfig(e){if(!this.hass)return W``;const t=this.hass.language,s=this._membersByOutlet(e.id),i=this._outletCount(e),a=this.zones.filter(e=>void 0!==e.id&&null==e.distributor_id&&!this._hasOwnActuation(e)),n=[...s.keys()].sort((e,t)=>e-t),o=n.some((e,t)=>e!==t+1),r=[];for(let n=1;n<=i;n++){const i=s.get(n),o=i?[...a,i]:[...a];o.sort((e,t)=>(e.name||"").localeCompare(t.name||"")),r.push(W`
        <div class="outlet-row">
          <span class="outlet-label"
            >${Ma("panels.distributors.commissioning.outlet",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            ${n}</span
          >
          <select
            class="settings-input"
            .value="${sn(null!=(null==s?void 0:s.id)?String(s.id):"")}"
            @change="${t=>this._onOutletZoneChange(e,n,t)}"
            ?disabled="${this.isSaving}"
          >
<<<<<<< HEAD
            <option value="" ?selected="${!s}">
              ${Oa("panels.distributors.outlets.none",t)}
=======
            <option value="" ?selected="${!i}">
              ${Ma("panels.distributors.outlets.none",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </option>
            ${o.map(e=>W`
                <option value="${e.id}" ?selected="${(null==s?void 0:s.id)===e.id}">
                  ${e.name}
                </option>
              `)}
          </select>
        </div>
      `)}return W`
      <div class="outlet-config">
        <div class="commissioning-head">
          <span class="section-title"
<<<<<<< HEAD
            >${Oa("panels.distributors.outlets.title",t)}</span
          >
        </div>
        <div class="item-description">
          ${Oa("panels.distributors.outlets.help",t)}
        </div>
        ${0===this.zones.length?W`<div class="weather-note">
              ${Oa("panels.distributors.outlets.no_zones",t)}
            </div>`:W`
              <ha-settings-row>
                <span slot="heading"
                  >${Oa("panels.distributors.outlets.count",t)}</span
=======
            >${Ma("panels.distributors.outlets.title",t)}</span
          >
        </div>
        <div class="item-description">
          ${Ma("panels.distributors.outlets.help",t)}
        </div>
        ${0===this.zones.length?W`<div class="weather-note">
              ${Ma("panels.distributors.outlets.no_zones",t)}
            </div>`:W`
              <ha-settings-row>
                <span slot="heading"
                  >${Ma("panels.distributors.outlets.count",t)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                >
                <select
                  class="settings-input shortfield"
                  .value="${sn(String(s))}"
                  @change="${t=>this._setOutletCount(e,parseInt(t.target.value))}"
                  ?disabled="${this.isSaving}"
                >
                  ${Array.from({length:5},(e,t)=>2+t).map(e=>W`<option value="${e}" ?selected="${e===s}">
                        ${e}
                      </option>`)}
                </select>
              </ha-settings-row>
              <div class="outlet-rows">${r}</div>
              ${o?W`<div class="timing-warning">
<<<<<<< HEAD
                    ${Oa("panels.distributors.outlets.gap_warning",t)}
                  </div>`:""}
              <div class="commissioning-note">
                ${Oa("panels.distributors.hints.outlet_change",t)}
=======
                    ${Ma("panels.distributors.outlets.gap_warning",t)}
                  </div>`:""}
              <div class="commissioning-note">
                ${Ma("panels.distributors.hints.outlet_change",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </div>
            `}
      </div>
    `}_renderAdvisories(){var e,t;if(!this.hass)return W``;const i=this.hass.language,s=null===(e=this.config)||void 0===e?void 0:e.zone_sequencing,a=s===Wt,n=s===Zt||s===qt,o=!!(null===(t=this.config)||void 0===t?void 0:t.master_off_after);return W`
      <div class="advisories">
        <div class="advisory">
          <ha-icon icon="mdi:flask-outline"></ha-icon>
          <span
<<<<<<< HEAD
            >${Oa("panels.distributors.hints.experimental",i)}</span
=======
            >${Ma("panels.distributors.hints.experimental",s)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          >
        </div>
        <div class="advisory">
          <ha-icon icon="mdi:water-alert-outline"></ha-icon>
<<<<<<< HEAD
          <span>${Oa("panels.distributors.hints.pressure",i)}</span>
=======
          <span>${Ma("panels.distributors.hints.pressure",s)}</span>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>
        ${a?W`<div class="advisory">
              <ha-icon icon="mdi:information-outline"></ha-icon>
              <span
<<<<<<< HEAD
                >${Oa("panels.distributors.hints.parallel_draw",i)}</span
=======
                >${Ma("panels.distributors.hints.parallel_draw",s)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              >
            </div>`:""}
        ${n&&o?W`<div class="advisory">
              <ha-icon icon="mdi:information-outline"></ha-icon>
              <span
<<<<<<< HEAD
                >${Oa("panels.distributors.hints.master_off_after",i)}</span
=======
                >${Ma("panels.distributors.hints.master_off_after",s)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              >
            </div>`:""}
      </div>
    `}_renderCommissioning(e){var t;if(!this.hass)return W``;const i=this.hass.language,s="synced"===e.position_state,a=!!e.commissioning_confirmed,n=!!e.active_cycle&&Object.keys(e.active_cycle).length>0,o=e.id;return W`
      <div class="commissioning">
        <div class="commissioning-head">
          <span class="section-title"
<<<<<<< HEAD
            >${Oa("panels.distributors.commissioning.title",i)}</span
          >
          <span class="pos-badge pos-${e.position_state}">
            ${Oa("panels.distributors.commissioning.outlet",i)}
            ${e.current_outlet} ·
            ${Oa(`panels.distributors.commissioning.states.${e.position_state}`,i)}
=======
            >${Ma("panels.distributors.commissioning.title",s)}</span
          >
          <span class="pos-badge pos-${e.position_state}">
            ${Ma("panels.distributors.commissioning.outlet",s)}
            ${e.current_outlet} ·
            ${Ma(`panels.distributors.commissioning.states.${e.position_state}`,s)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </span>
        </div>

        <!-- Re-sync controls -->
        <ha-settings-row>
          <span slot="heading"
<<<<<<< HEAD
            >${Oa("panels.distributors.commissioning.set_outlet",i)}</span
          >
          <span slot="description"
            >${Oa("panels.distributors.commissioning.set_outlet_help",i)}</span
=======
            >${Ma("panels.distributors.commissioning.set_outlet",s)}</span
          >
          <span slot="description"
            >${Ma("panels.distributors.commissioning.set_outlet_help",s)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          >
          <div class="inline-controls">
            <input
              type="number"
              class="settings-input shortfield"
              min="1"
              max="${6}"
              step="1"
              .value="${sn(String(null!==(t=this._outletDraft[o])&&void 0!==t?t:e.current_outlet))}"
              @input="${e=>{const t=e.target.valueAsNumber;isNaN(t)||(this._outletDraft=Object.assign(Object.assign({},this._outletDraft),{[o]:t}))}}"
            />
            <button
              class="action-btn secondary"
              ?disabled="${this.isSaving}"
              @click="${()=>{this._confirmSetOutletId=o}}"
            >
<<<<<<< HEAD
              ${Oa("panels.distributors.commissioning.set_outlet",i)}
=======
              ${Ma("panels.distributors.commissioning.set_outlet",s)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </button>
            <button
              class="action-btn secondary"
              ?disabled="${this.isSaving}"
              @click="${()=>{this._confirmResyncHomeId=o}}"
            >
<<<<<<< HEAD
              ${Oa("panels.distributors.commissioning.resync_home",i)}
=======
              ${Ma("panels.distributors.commissioning.resync_home",s)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </button>
          </div>
        </ha-settings-row>
        <div class="commissioning-note">
<<<<<<< HEAD
          ${Oa("panels.distributors.hints.undetectable",i)}
=======
          ${Ma("panels.distributors.hints.undetectable",s)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>

        <!-- Test run -->
        <ha-settings-row>
          <span slot="heading"
<<<<<<< HEAD
            >${Oa("panels.distributors.commissioning.test_run",i)}</span
          >
          <span slot="description"
            >${Oa("panels.distributors.commissioning.test_run_help",i)}</span
=======
            >${Ma("panels.distributors.commissioning.test_run",s)}</span
          >
          <span slot="description"
            >${Ma("panels.distributors.commissioning.test_run_help",s)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          >
          <button
            class="action-btn secondary"
            ?disabled="${this.isSaving||!s}"
            @click="${()=>this._testRun(o)}"
          >
            <ha-icon icon="mdi:play-circle-outline"></ha-icon>
<<<<<<< HEAD
            ${Oa("panels.distributors.commissioning.test_run",i)}
=======
            ${Ma("panels.distributors.commissioning.test_run",s)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </button>
        </ha-settings-row>

        <!-- Arm switch -->
        <ha-settings-row>
          <span slot="heading"
<<<<<<< HEAD
            >${Oa("panels.distributors.commissioning.confirmed",i)}</span
          >
          <span slot="description"
            >${Oa(s?"panels.distributors.commissioning.confirmed_help":"panels.distributors.commissioning.needs_sync",i)}</span
=======
            >${Ma("panels.distributors.commissioning.confirmed",s)}</span
          >
          <span slot="description"
            >${Ma(i?"panels.distributors.commissioning.confirmed_help":"panels.distributors.commissioning.needs_sync",s)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          >
          <ha-switch
            .checked="${sn(a)}"
            .disabled="${this.isSaving||!s&&!a}"
            @change="${t=>this._onArmToggle(e,t.target.checked)}"
          ></ha-switch>
        </ha-settings-row>

        <!-- Run now -->
        <div class="run-now-row">
          <button
            class="action-btn"
            ?disabled="${this.isSaving||!s||!a||n}"
            @click="${()=>this._runNow(o)}"
          >
            <ha-icon icon="mdi:play"></ha-icon>
<<<<<<< HEAD
            ${Oa("panels.distributors.commissioning.run_now",i)}
          </button>
          <span class="run-now-hint">
            ${Oa(n?"panels.distributors.commissioning.run_now_active":"panels.distributors.commissioning.run_now_help",i)}
=======
            ${Ma("panels.distributors.commissioning.run_now",s)}
          </button>
          <span class="run-now-hint">
            ${Ma(n?"panels.distributors.commissioning.run_now_active":"panels.distributors.commissioning.run_now_help",s)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </span>
        </div>
      </div>
    `}renderDistributor(e,t){var i;if(!this.hass)return W``;const s=this._isExpanded(e),a=this.hass.language;return W`
      <ha-card id="distributor-${null!==(i=e.id)&&void 0!==i?i:"new"}">
        <div
          class="card-header dist-toggle"
          role="button"
          tabindex="0"
          aria-expanded="${s?"true":"false"}"
          @click="${()=>void 0!==e.id&&this._toggle(e.id)}"
          @keydown="${t=>{"Enter"!==t.key&&" "!==t.key||void 0===e.id||(t.preventDefault(),this._toggle(e.id))}}"
        >
          <div class="name">${e.name}</div>
          <span class="pos-badge pos-${e.position_state}">
<<<<<<< HEAD
            ${Oa(`panels.distributors.commissioning.states.${e.position_state}`,a)}
=======
            ${Ma(`panels.distributors.commissioning.states.${e.position_state}`,a)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </span>
          <ha-icon
            class="dist-chevron"
            icon="${s?"mdi:chevron-up":"mdi:chevron-down"}"
          ></ha-icon>
        </div>
        ${s?W`
              <div class="card-content">
                <si-distributor-form
                  .hass="${this.hass}"
                  .distributor="${e}"
                  @distributor-changed="${e=>this.handleEditDistributor(t,e.detail.value)}"
                ></si-distributor-form>

                ${this._renderOutletConfig(e)} ${this._renderCommissioning(e)}

                <div class="settings-danger-row">
                  <button
                    class="action-btn danger"
                    ?disabled="${this.isSaving||void 0===e.id}"
                    @click="${()=>{var t;this._confirmDeleteId=null!==(t=e.id)&&void 0!==t?t:null}}"
                  >
                    <ha-icon icon="mdi:delete"></ha-icon>
<<<<<<< HEAD
                    ${Oa("common.actions.delete",a)}
=======
                    ${Ma("common.actions.delete",a)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </button>
                </div>
              </div>
            `:""}
      </ha-card>
    `}render(){var e;if(!this.hass)return W``;const t=this.hass.language;if(this.isLoading)return W`
<<<<<<< HEAD
        <ha-card header="${Oa("panels.distributors.title",t)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Oa("common.loading-messages.general",t)}
=======
        <ha-card header="${Ma("panels.distributors.title",t)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Ma("common.loading-messages.general",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </div>
          </div>
        </ha-card>
      `;const i=null!==this._confirmDeleteId?this.distributors.find(e=>e.id===this._confirmDeleteId):null,s=null!==this._armConfirmId?this.distributors.find(e=>e.id===this._armConfirmId):null,a=null!==this._confirmResyncHomeId?this.distributors.find(e=>e.id===this._confirmResyncHomeId):null,n=null!==this._confirmSetOutletId?this.distributors.find(e=>e.id===this._confirmSetOutletId):null,o=n&&void 0!==n.id?null!==(e=this._outletDraft[n.id])&&void 0!==e?e:n.current_outlet:null;return W`
      <ha-card>
        <div class="card-header">
<<<<<<< HEAD
          <div class="name">${Oa("panels.distributors.title",t)}</div>
          ${this._renderSaveStatus()}
          <ha-icon-button
            .path="${ja}"
            title="${Oa("panels.distributors.add.header",t)}"
=======
          <div class="name">${Ma("panels.distributors.title",t)}</div>
          ${this._renderSaveStatus()}
          <ha-icon-button
            .path="${Za}"
            title="${Ma("panels.distributors.add.header",t)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            @click="${()=>{this._showAdd=!0}}"
          ></ha-icon-button>
        </div>
        <div class="card-content">
          <div class="item-description">
<<<<<<< HEAD
            ${Oa("panels.distributors.description",t)}
          </div>
          ${this._renderAdvisories()}
          ${0===this.distributors.length?W`<div class="weather-note">
                ${Oa("panels.distributors.no_items",t)}
=======
            ${Ma("panels.distributors.description",t)}
          </div>
          ${this._renderAdvisories()}
          ${0===this.distributors.length?W`<div class="weather-note">
                ${Ma("panels.distributors.no_items",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </div>`:""}
        </div>
      </ha-card>

      <!-- Add dialog -->
      <ha-dialog
        .open="${this._showAdd}"
        @closed="${()=>{this._showAdd=!1}}"
<<<<<<< HEAD
        heading="${Oa("panels.distributors.add.header",t)}"
      >
        <div class="add-form">
          <si-field
            label="${Oa("panels.distributors.labels.name",t)}"
=======
        heading="${Ma("panels.distributors.add.header",t)}"
      >
        <div class="add-form">
          <si-field
            label="${Ma("panels.distributors.labels.name",t)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            required
          >
            <input
              type="text"
              class="settings-input"
<<<<<<< HEAD
              placeholder="${Oa("panels.distributors.add.name_placeholder",t)}"
=======
              placeholder="${Ma("panels.distributors.add.name_placeholder",t)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              .value="${this._newName}"
              @input="${e=>{this._newName=e.target.value}}"
            />
          </si-field>
        </div>
        <div class="dialog-footer">
          <button
            class="dialog-btn"
            @click="${()=>{this._showAdd=!1}}"
          >
<<<<<<< HEAD
            ${Oa("common.actions.cancel",t)}
=======
            ${Ma("common.actions.cancel",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </button>
          <button
            class="dialog-btn dialog-btn-primary"
            ?disabled="${!this._newName.trim()||this.isSaving}"
            @click="${this.handleAdd}"
          >
<<<<<<< HEAD
            ${this.isSaving?Oa("common.saving-messages.adding",t):Oa("panels.distributors.add.actions.add",t)}
=======
            ${this.isSaving?Ma("common.saving-messages.adding",t):Ma("panels.distributors.add.actions.add",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </button>
        </div>
      </ha-dialog>

      <!-- Delete confirm -->
      ${i?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmDeleteId=null}}"
<<<<<<< HEAD
              heading="${Oa("common.actions.confirm_delete",t)}"
            >
              <p>${Oa("panels.distributors.confirm_delete",t)}</p>
              <p><strong>${i.name}</strong></p>
=======
              heading="${Ma("common.actions.confirm_delete",t)}"
            >
              <p>${Ma("panels.distributors.confirm_delete",t)}</p>
              <p><strong>${s.name}</strong></p>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmDeleteId=null}}"
                >
<<<<<<< HEAD
                  ${Oa("common.actions.cancel",t)}
=======
                  ${Ma("common.actions.cancel",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
                <button
                  class="dialog-btn dialog-btn-danger"
                  @click="${this._confirmDelete}"
                >
<<<<<<< HEAD
                  ${Oa("common.actions.delete",t)}
=======
                  ${Ma("common.actions.delete",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Arm confirm -->
      ${s?W`
            <ha-dialog
              open
              @closed="${()=>{this._armConfirmId=null}}"
<<<<<<< HEAD
              heading="${Oa("panels.distributors.commissioning.confirm_dialog.title",t)}"
            >
              <p>
                ${Oa("panels.distributors.commissioning.confirm_dialog.body",t)}
=======
              heading="${Ma("panels.distributors.commissioning.confirm_dialog.title",t)}"
            >
              <p>
                ${Ma("panels.distributors.commissioning.confirm_dialog.body",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </p>
              <p><strong>${s.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._armConfirmId=null}}"
                >
<<<<<<< HEAD
                  ${Oa("common.actions.cancel",t)}
=======
                  ${Ma("common.actions.cancel",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${()=>void 0!==s.id&&this._setArmed(s.id,!0)}"
                >
<<<<<<< HEAD
                  ${Oa("panels.distributors.commissioning.confirm_dialog.confirm",t)}
=======
                  ${Ma("panels.distributors.commissioning.confirm_dialog.confirm",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Reset-to-outlet-1 confirm (safety: a stray click would falsely mark synced) -->
      ${a?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmResyncHomeId=null}}"
<<<<<<< HEAD
              heading="${Oa("panels.distributors.commissioning.confirm_resync.title",t)}"
            >
              <p>
                ${Oa("panels.distributors.commissioning.confirm_resync.body",t)}
=======
              heading="${Ma("panels.distributors.commissioning.confirm_resync.title",t)}"
            >
              <p>
                ${Ma("panels.distributors.commissioning.confirm_resync.body",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </p>
              <p><strong>${a.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmResyncHomeId=null}}"
                >
<<<<<<< HEAD
                  ${Oa("common.actions.cancel",t)}
=======
                  ${Ma("common.actions.cancel",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._confirmResyncHome}"
                >
<<<<<<< HEAD
                  ${Oa("panels.distributors.commissioning.resync_home",t)}
=======
                  ${Ma("panels.distributors.commissioning.resync_home",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Set-current-outlet confirm (safety: a stray click would falsely mark synced at the entered outlet) -->
      ${n?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmSetOutletId=null}}"
<<<<<<< HEAD
              heading="${Oa("panels.distributors.commissioning.confirm_set_outlet.title",t)}"
            >
              <p>
                ${Oa("panels.distributors.commissioning.confirm_set_outlet.body",t)}
=======
              heading="${Ma("panels.distributors.commissioning.confirm_set_outlet.title",t)}"
            >
              <p>
                ${Ma("panels.distributors.commissioning.confirm_set_outlet.body",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </p>
              <p>
                <strong
                  >${n.name} ·
<<<<<<< HEAD
                  ${Oa("panels.distributors.commissioning.outlet",t)}
=======
                  ${Ma("panels.distributors.commissioning.outlet",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  ${o}</strong
                >
              </p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmSetOutletId=null}}"
                >
<<<<<<< HEAD
                  ${Oa("common.actions.cancel",t)}
=======
                  ${Ma("common.actions.cancel",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._confirmSetOutlet}"
                >
<<<<<<< HEAD
                  ${Oa("panels.distributors.commissioning.set_outlet",t)}
=======
                  ${Ma("panels.distributors.commissioning.set_outlet",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>
              </div>
            </ha-dialog>
          `:""}
      ${this.distributors.map((e,t)=>this.renderDistributor(e,t))}
    `}disconnectedCallback(){super.disconnectedCallback(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null),this._savedResetTimer&&(clearTimeout(this._savedResetTimer),this._savedResetTimer=null)}static get styles(){return r`
      ${Ka}

      .card-header.dist-toggle {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        user-select: none;
      }
      .card-header.dist-toggle:hover {
        background: var(--secondary-background-color);
      }
      .card-header.dist-toggle .name {
        flex: 1 1 auto;
      }
      .dist-chevron {
        color: var(--secondary-text-color);
        flex: 0 0 auto;
      }

      ha-settings-row {
        padding: 0 16px;
      }

      .settings-input {
        height: 36px;
      }

      /* Position / state badge */
      .pos-badge {
        display: inline-block;
        padding: 1px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 600;
        white-space: nowrap;
        color: #fff;
        background: var(--secondary-text-color);
        flex: 0 0 auto;
      }
      .pos-badge.pos-synced {
        background: var(--success-color, #2e7d32);
      }
      .pos-badge.pos-uncertain {
        background: var(--warning-color, #f9a825);
      }

      .commissioning {
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
        padding-top: 8px;
      }
      .commissioning-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        padding: 0 16px 4px;
      }
      .section-title {
        font-weight: 600;
        color: var(--primary-text-color);
      }

      /* Outlet -> zone assignment (FB5) */
      .outlet-config {
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
        padding-top: 8px;
      }
      .outlet-config .item-description {
        padding: 0 16px;
      }
      .outlet-rows {
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 4px 16px 8px;
      }
      .outlet-row {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .outlet-label {
        flex: 0 0 90px;
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }
      .outlet-row select {
        flex: 1 1 auto;
        min-width: 140px;
      }

      .inline-controls {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
      }

      .run-now-row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 12px;
        padding: 12px 16px 4px;
      }
      .run-now-hint {
        color: var(--secondary-text-color);
        font-size: 0.82rem;
      }

      /* Instance-level safety advisories in the intro card. */
      .advisories {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin: 8px 0 4px;
      }
      .advisory {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        font-size: 0.85rem;
        line-height: 1.45;
        color: var(--secondary-text-color);
        background: var(--secondary-background-color);
        border-left: 3px solid var(--primary-color);
        border-radius: 0 3px 3px 0;
        padding: 6px 10px;
      }
      .advisory ha-icon {
        --mdc-icon-size: 18px;
        flex: 0 0 auto;
        color: var(--primary-color);
      }

      /* Muted one-liner under the re-sync controls. */
      .commissioning-note {
        color: var(--secondary-text-color);
        font-size: 0.8rem;
        line-height: 1.4;
        padding: 2px 16px 6px;
      }

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

      .settings-danger-row {
        display: flex;
        justify-content: flex-end;
        padding: 12px 16px;
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
      }

      .add-form {
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 8px 0;
        min-width: 300px;
      }
      .add-form .settings-input {
        width: 100%;
        height: 36px;
      }
<<<<<<< HEAD
    `}};t([me()],gn.prototype,"config",void 0),t([me({attribute:!1})],gn.prototype,"path",void 0),t([me({type:Array})],gn.prototype,"distributors",void 0),t([me({type:Array})],gn.prototype,"zones",void 0),t([me({type:Boolean})],gn.prototype,"isLoading",void 0),t([me({type:Boolean})],gn.prototype,"isSaving",void 0),t([ve()],gn.prototype,"_expanded",void 0),t([me({type:Boolean})],gn.prototype,"_showAdd",void 0),t([me()],gn.prototype,"_newName",void 0),t([me()],gn.prototype,"_confirmDeleteId",void 0),t([ve()],gn.prototype,"_armConfirmId",void 0),t([ve()],gn.prototype,"_confirmResyncHomeId",void 0),t([ve()],gn.prototype,"_confirmSetOutletId",void 0),t([ve()],gn.prototype,"_outletDraft",void 0),t([ve()],gn.prototype,"_outletRows",void 0),t([ve()],gn.prototype,"_saveStatus",void 0),gn=t([ue("smart-irrigation-view-distributor-settings")],gn);let mn=class extends(Fa(ce)){constructor(){super(...arguments),this.zones=[],this.modules=[],this.allmodules=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._updateScheduled=!1,this.globalDebounceTimer=null,this.moduleCache=new Map,this.debouncedSave=(()=>{let e=null;return t=>{e&&clearTimeout(e),e=window.setTimeout(()=>{this.saveToHA(t),e=null},500)}})()}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}firstUpdated(){qi().catch(e=>{console.error("Failed to load HA form:",e)})}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:be+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;e&&(this.isLoading=!0,this._scheduleUpdate());try{const[e,t,i,s]=await Promise.all([Ei(this.hass),Ti(this.hass),Hi(this.hass),Di(this.hass)]);this.config=e,this.zones=t,this.modules=i,this.allmodules=s,this._initialLoadDone=!0,this.moduleCache.clear()}catch(e){console.error("Error fetching data:",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}async handleAddModule(){var e,t;if((null===(t=null===(e=this.moduleInput)||void 0===e?void 0:e.selectedOptions)||void 0===t?void 0:t[0])&&!this.isSaving){this.isSaving=!0,this._scheduleUpdate();try{const e=this.moduleInput.selectedOptions[0].text,t=this.allmodules.find(t=>t.name===e);if(!t)return;const i={name:e,description:t.description,config:t.config,schema:t.schema};this.modules=[...this.modules,i],this.moduleCache.clear(),this._scheduleUpdate(),await this.saveToHA(i),await this._fetchData()}catch(e){console.error("Error adding module:",e),await this._fetchData()}finally{this.isSaving=!1,this._scheduleUpdate()}}}async handleRemoveModule(e,t){if(!this.isSaving){this.isSaving=!0,this._scheduleUpdate();try{const e=this.modules[t],a=null==e?void 0:e.id;this.modules;this.modules=this.modules.filter((e,i)=>i!==t),this.moduleCache.clear(),this._scheduleUpdate(),this.hass&&void 0!==a&&await(i=this.hass,s=a.toString(),i.callApi("POST",be+"/modules",{id:s,remove:!0}))}catch(e){console.error("Error removing module:",e),Ba(this,this.hass,"common.errors.delete_failed",e),await this._fetchData()}finally{this.isSaving=!1,this._scheduleUpdate()}var i,s}}async saveToHA(e){if(this.hass)try{await Mi(this.hass,e)}catch(e){throw console.error("Error saving module:",e),Ba(this,this.hass,"common.errors.save_failed",e),e}}renderModule(e,t){if(!this.hass)return W``;const i=this.zones.filter(t=>t.module===e.id).length,s=`module-${e.id||t}-${i}-${JSON.stringify(e)}`;if(this.moduleCache.has(s))return this.moduleCache.get(s);const a=W`
=======
    `}};t([me()],vn.prototype,"config",void 0),t([me({attribute:!1})],vn.prototype,"path",void 0),t([me({type:Array})],vn.prototype,"distributors",void 0),t([me({type:Array})],vn.prototype,"zones",void 0),t([me({type:Boolean})],vn.prototype,"isLoading",void 0),t([me({type:Boolean})],vn.prototype,"isSaving",void 0),t([ve()],vn.prototype,"_expanded",void 0),t([me({type:Boolean})],vn.prototype,"_showAdd",void 0),t([me()],vn.prototype,"_newName",void 0),t([me()],vn.prototype,"_confirmDeleteId",void 0),t([ve()],vn.prototype,"_armConfirmId",void 0),t([ve()],vn.prototype,"_confirmResyncHomeId",void 0),t([ve()],vn.prototype,"_confirmSetOutletId",void 0),t([ve()],vn.prototype,"_outletDraft",void 0),t([ve()],vn.prototype,"_outletRows",void 0),t([ve()],vn.prototype,"_saveStatus",void 0),vn=t([ue("smart-irrigation-view-distributor-settings")],vn);let fn=class extends(Wa(ce)){constructor(){super(...arguments),this.zones=[],this.modules=[],this.allmodules=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._updateScheduled=!1,this.globalDebounceTimer=null,this.moduleCache=new Map,this.debouncedSave=(()=>{let e=null;return t=>{e&&clearTimeout(e),e=window.setTimeout(()=>{this.saveToHA(t),e=null},500)}})()}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}firstUpdated(){Ks().catch(e=>{console.error("Failed to load HA form:",e)})}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:be+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;e&&(this.isLoading=!0,this._scheduleUpdate());try{const[e,t,s,i]=await Promise.all([Ts(this.hass),Ds(this.hass),Hs(this.hass),Is(this.hass)]);this.config=e,this.zones=t,this.modules=s,this.allmodules=i,this._initialLoadDone=!0,this.moduleCache.clear()}catch(e){console.error("Error fetching data:",e),ja(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}async handleAddModule(){var e,t;if((null===(t=null===(e=this.moduleInput)||void 0===e?void 0:e.selectedOptions)||void 0===t?void 0:t[0])&&!this.isSaving){this.isSaving=!0,this._scheduleUpdate();try{const e=this.moduleInput.selectedOptions[0].text,t=this.allmodules.find(t=>t.name===e);if(!t)return;const s={name:e,description:t.description,config:t.config,schema:t.schema};this.modules=[...this.modules,s],this.moduleCache.clear(),this._scheduleUpdate(),await this.saveToHA(s),await this._fetchData()}catch(e){console.error("Error adding module:",e),await this._fetchData()}finally{this.isSaving=!1,this._scheduleUpdate()}}}async handleRemoveModule(e,t){if(!this.isSaving){this.isSaving=!0,this._scheduleUpdate();try{const e=this.modules[t],a=null==e?void 0:e.id;this.modules;this.modules=this.modules.filter((e,s)=>s!==t),this.moduleCache.clear(),this._scheduleUpdate(),this.hass&&void 0!==a&&await(s=this.hass,i=a.toString(),s.callApi("POST",be+"/modules",{id:i,remove:!0}))}catch(e){console.error("Error removing module:",e),ja(this,this.hass,"common.errors.delete_failed",e),await this._fetchData()}finally{this.isSaving=!1,this._scheduleUpdate()}var s,i}}async saveToHA(e){if(this.hass)try{await Ns(this.hass,e)}catch(e){throw console.error("Error saving module:",e),ja(this,this.hass,"common.errors.save_failed",e),e}}renderModule(e,t){if(!this.hass)return W``;const s=this.zones.filter(t=>t.module===e.id).length,i=`module-${e.id||t}-${s}-${JSON.stringify(e)}`;if(this.moduleCache.has(i))return this.moduleCache.get(i);const a=W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          ${this.renderUsageChip(i)}
        </div>
        <div class="card-content">
          <div class="item-description">${e.description}</div>
          <div class="moduleconfig">
            <label class="subheader"
<<<<<<< HEAD
              >${Oa("panels.modules.cards.module.labels.configuration",this.hass.language)}
              (*
              ${Oa("panels.modules.cards.module.labels.required",this.hass.language)})</label
=======
              >${Ma("panels.modules.cards.module.labels.configuration",this.hass.language)}
              (*
              ${Ma("panels.modules.cards.module.labels.required",this.hass.language)})</label
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            >
            ${e.schema?Object.entries(e.schema).map(([e])=>this.renderConfig(t,e)):null}
          </div>
          <div class="card-footer">
<<<<<<< HEAD
            ${i?W`<div class="weather-note">
                  ${Oa("panels.modules.cards.module.errors.cannot-delete-module-because-zones-use-it",this.hass.language)}
=======
            ${s?W`<div class="weather-note">
                  ${Ma("panels.modules.cards.module.errors.cannot-delete-module-because-zones-use-it",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </div>`:W`<button
                  class="action-btn danger"
                  @click="${e=>this.handleRemoveModule(e,t)}"
                >
                  <ha-icon icon="mdi:delete"></ha-icon>
<<<<<<< HEAD
                  ${Oa("common.actions.delete",this.hass.language)}
=======
                  ${Ma("common.actions.delete",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>`}
          </div>
        </div>
      </ha-card>
<<<<<<< HEAD
    `;return this.moduleCache.set(s,a),a}renderUsageChip(e){return this.hass?e?W`<span class="usage-chip"
          >${Oa("panels.setup.advanced.used_by_zones",this.hass.language,"{count}",e)}</span
        >`:W`<span class="usage-chip unused"
          >${Oa("panels.setup.advanced.not_used",this.hass.language)}</span
        >`:W``}renderConfig(e,t){var i,s;const a=Object.values(this.modules).at(e);if(!a||!this.hass)return;const n=a.schema[t],o=n.name,r=e=>{try{const t=Oa(e,this.hass.language);return null==t?void 0:t}catch(e){return}},l="panels.modules.cards.module.fields."+o,d=null!==(i=r(l+".name"))&&void 0!==i?i:function(e){if(e)return(e=e.replace("_"," ")).charAt(0).toUpperCase()+e.slice(1)}(o),c=null!==(s=r(l+".description"))&&void 0!==s?s:n.description;let h="";null==a.config&&(a.config=[]),o in a.config&&(h=a.config[o]);let u=W``;if("boolean"==n.type)u=W`<input
=======
    `;return this.moduleCache.set(i,a),a}renderUsageChip(e){return this.hass?e?W`<span class="usage-chip"
          >${Ma("panels.setup.advanced.used_by_zones",this.hass.language,"{count}",e)}</span
        >`:W`<span class="usage-chip unused"
          >${Ma("panels.setup.advanced.not_used",this.hass.language)}</span
        >`:W``}renderConfig(e,t){var s,i;const a=Object.values(this.modules).at(e);if(!a||!this.hass)return;const n=a.schema[t],o=n.name,r=e=>{try{const t=Ma(e,this.hass.language);return null==t?void 0:t}catch(e){return}},l="panels.modules.cards.module.fields."+o,d=null!==(s=r(l+".name"))&&void 0!==s?s:function(e){if(e)return(e=e.replace("_"," ")).charAt(0).toUpperCase()+e.slice(1)}(o),c=null!==(i=r(l+".description"))&&void 0!==i?i:n.description;let h="";null==a.config&&(a.config=[]),o in a.config&&(h=a.config[o]);let u=W``;if("boolean"==n.type)u=W`<input
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        type="checkbox"
        id="${o+e}"
        .checked=${h}
        @input="${t=>this.handleEditConfig(e,Object.assign(Object.assign({},a),{config:Object.assign(Object.assign({},a.config),{[o]:t.target.checked})}))}"
      />`;else if("float"==n.type||"integer"==n.type)u=W`<input
        type="number"
        class="settings-input shortfield"
        id="${n.name+e}"
        .value="${a.config[n.name]}"
        @input="${t=>this.handleEditConfig(e,Object.assign(Object.assign({},a),{config:Object.assign(Object.assign({},a.config),{[o]:t.target.value})}))}"
      />`;else if("string"==n.type)u=W`<input
        type="text"
        class="settings-input"
        id="${o+e}"
        .value="${h}"
        @input="${t=>this.handleEditConfig(e,Object.assign(Object.assign({},a),{config:Object.assign(Object.assign({},a.config),{[o]:t.target.value})}))}"
      />`;else if("select"==n.type){const t=this.hass.language;u=W`<select
        class="settings-input"
        id="${o+e}"
        .value="${sn(h)}"
        @change="${t=>this.handleEditConfig(e,Object.assign(Object.assign({},a),{config:Object.assign(Object.assign({},a.config),{[o]:t.target.value})}))}"
      >
        ${Object.entries(n.options).map(([e,i])=>W`<option
              value="${Da(i,0)}"
              ?selected="${h===Da(i,0)}"
            >
<<<<<<< HEAD
              ${Oa("panels.modules.cards.module.translated-options."+Da(i,1),t)}
=======
              ${Ma("panels.modules.cards.module.translated-options."+Ia(s,1),t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </option>`)}
      </select>`}return W`<ha-settings-row>
      <span slot="heading"
        >${d}${n.required?" *":""}</span
      >
      ${c?W`<span slot="description">${c}</span>`:""}
      ${u}
<<<<<<< HEAD
    </ha-settings-row>`}handleEditConfig(e,t){this.modules=Object.values(this.modules).map((i,s)=>s===e?t:i),this.moduleCache.clear(),this._scheduleUpdate(),this.debouncedSave(t)}render(){return this.hass?W`
      <ha-card header="${Oa("panels.modules.title",this.hass.language)}">
        <div class="card-content">
          ${Oa("panels.modules.description",this.hass.language)}
          ${this.isLoading?W`<div class="loading-indicator">
                ${Oa("common.loading-messages.general",this.hass.language)}
=======
    </ha-settings-row>`}handleEditConfig(e,t){this.modules=Object.values(this.modules).map((s,i)=>i===e?t:s),this.moduleCache.clear(),this._scheduleUpdate(),this.debouncedSave(t)}render(){return this.hass?W`
      <ha-card header="${Ma("panels.modules.title",this.hass.language)}">
        <div class="card-content">
          ${Ma("panels.modules.description",this.hass.language)}
          ${this.isLoading?W`<div class="loading-indicator">
                ${Ma("common.loading-messages.general",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </div>`:W`
                <div class="add-row">
                  <select
                    id="moduleInput"
                    class="settings-input"
<<<<<<< HEAD
                    aria-label="${Oa("common.labels.module",this.hass.language)}"
=======
                    aria-label="${Ma("common.labels.module",this.hass.language)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    ?disabled="${this.isSaving}"
                  >
                    ${Object.entries(this.allmodules).map(([e,t])=>W`<option value="${t.id}">
                          ${t.name}
                        </option>`)}
                  </select>
                  <button
                    @click="${this.handleAddModule}"
                    ?disabled="${this.isSaving}"
                    class="action-btn ${this.isSaving?"saving":""}"
                  >
                    <ha-icon icon="mdi:plus"></ha-icon>
<<<<<<< HEAD
                    ${this.isSaving?Oa("common.saving-messages.adding",this.hass.language):Oa("panels.modules.cards.add-module.actions.add",this.hass.language)}
=======
                    ${this.isSaving?Ma("common.saving-messages.adding",this.hass.language):Ma("panels.modules.cards.add-module.actions.add",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </button>
                </div>
              `}
        </div>
      </ha-card>

      ${this.isLoading?W``:Object.entries(this.modules).map(([e,t])=>this.renderModule(t,parseInt(e)))}
    `:W``}disconnectedCallback(){super.disconnectedCallback(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null),this.moduleCache.clear()}static get styles(){return r`
      ${Ka}

      .field-hint {
        font-size: 0.8rem;
        color: var(--secondary-text-color);
        line-height: 1.4;
        margin-top: 3px;
        padding-left: 2px;
      }
<<<<<<< HEAD
    `}};t([me()],mn.prototype,"config",void 0),t([me({type:Array})],mn.prototype,"zones",void 0),t([me({type:Array})],mn.prototype,"modules",void 0),t([me({type:Array})],mn.prototype,"allmodules",void 0),t([me({type:Boolean})],mn.prototype,"isLoading",void 0),t([me({type:Boolean})],mn.prototype,"isSaving",void 0),t([fe("#moduleInput")],mn.prototype,"moduleInput",void 0),mn=t([ue("smart-irrigation-view-modules")],mn);let vn=class extends(Fa(ce)){constructor(){super(...arguments),this.zones=[],this.mappings=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this.debounceTimers=new Map,this.globalDebounceTimer=null,this.mappingCache=new Map,this._updateScheduled=!1,this._lastUpdateTime=0,this._updateThrottleDelay=16}_scheduleUpdate(){if(this._updateScheduled)return;const e=performance.now()-this._lastUpdateTime;e<this._updateThrottleDelay?setTimeout(()=>{this._updateScheduled=!1,this._lastUpdateTime=performance.now(),this.requestUpdate()},this._updateThrottleDelay-e):(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this._lastUpdateTime=performance.now(),this.requestUpdate()}))}firstUpdated(){qi().catch(e=>{console.error("Failed to load HA form:",e)})}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:be+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[t,i,s]=await Promise.all([Ei(this.hass),Ti(this.hass),Ii(this.hass)]);this.config=t,this.zones=i,this.mappings=s,this._initialLoadDone=!0,this.mappingCache.clear()}catch(e){console.error("Error fetching data:",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}handleAddMapping(){if(!this.mappingNameInput.value.trim())return;const e={[Me]:"",[Ie]:"",[Ne]:"",[Pe]:"",[Le]:"",[Re]:"",[Be]:"",[Ue]:"",[je]:""},t={name:this.mappingNameInput.value.trim(),mappings:e};this.mappings=[...this.mappings,t],this.isSaving=!0,this.saveToHA(t).then(()=>(this.mappingNameInput.value="",this._fetchData())).catch(e=>{console.error("Failed to add mapping:",e),Ba(this,this.hass,"common.errors.save_failed",e),this.mappings=this.mappings.slice(0,-1)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()})}handleRemoveMapping(e,t){const i=this.mappings[t].id;if(null==i)return;const s=[...this.mappings];var a,n;(this.mappings=this.mappings.filter((e,i)=>i!==t),this.mappingCache.delete(i.toString()),this.hass)&&(this.isSaving=!0,(a=this.hass,n=i.toString(),a.callApi("POST",be+"/mappings",{id:n,remove:!0})).catch(e=>{console.error("Failed to delete mapping:",e),Ba(this,this.hass,"common.errors.delete_failed",e),this.mappings=s,this._fetchData().catch(e=>{console.error("Failed to refresh data after delete error:",e)})}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}))}handleEditMapping(e,t){this.mappings[e]=t,t.id&&this.mappingCache.delete(t.id.toString()),this.globalDebounceTimer&&clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=window.setTimeout(()=>{this.isSaving=!0,this.saveToHA(t).catch(e=>{console.error("Failed to save mapping:",e),Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}),this.globalDebounceTimer=null},500),this._scheduleUpdate()}async saveToHA(e){var t;if(!this.hass)throw new Error("Home Assistant connection not available");const i=[],s=this.hass.states;for(const t in e.mappings){const a=e.mappings[t].sensorentity;if(a&&""!==a.trim()){const n=a.trim();e.mappings[t].sensorentity=n,n in s||i.push(n)}}if(i.length>0){const e=null===(t=this.shadowRoot)||void 0===t?void 0:t.querySelector("ha-card");throw e&&Ia({body:{message:Oa("panels.mappings.cards.mapping.errors.source_does_not_exist",this.hass.language)+": "+i.join(", ")},error:Oa("panels.mappings.cards.mapping.errors.invalid_source",this.hass.language)},e),new Error("Invalid sensor entities found")}const{id:a,name:n,mappings:o}=e;await Ni(this.hass,{id:a,name:n,mappings:o})}renderMappingSetting(e,t){const i=this.mappings[e];if(!i||!this.hass)return W``;const s=i.mappings[t];return W`
      <div class="mappingline">
        <div class="mappingsettingname">
          <label for="${`${t}_${e}`}">
            ${Oa(`panels.mappings.cards.mapping.items.${t.toLowerCase()}`,this.hass.language)}
=======
    `}};t([me()],fn.prototype,"config",void 0),t([me({type:Array})],fn.prototype,"zones",void 0),t([me({type:Array})],fn.prototype,"modules",void 0),t([me({type:Array})],fn.prototype,"allmodules",void 0),t([me({type:Boolean})],fn.prototype,"isLoading",void 0),t([me({type:Boolean})],fn.prototype,"isSaving",void 0),t([fe("#moduleInput")],fn.prototype,"moduleInput",void 0),fn=t([ue("smart-irrigation-view-modules")],fn);let _n=class extends(Wa(ce)){constructor(){super(...arguments),this.zones=[],this.mappings=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this.debounceTimers=new Map,this.globalDebounceTimer=null,this.mappingCache=new Map,this._updateScheduled=!1,this._lastUpdateTime=0,this._updateThrottleDelay=16}_scheduleUpdate(){if(this._updateScheduled)return;const e=performance.now()-this._lastUpdateTime;e<this._updateThrottleDelay?setTimeout(()=>{this._updateScheduled=!1,this._lastUpdateTime=performance.now(),this.requestUpdate()},this._updateThrottleDelay-e):(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this._lastUpdateTime=performance.now(),this.requestUpdate()}))}firstUpdated(){Ks().catch(e=>{console.error("Failed to load HA form:",e)})}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:be+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[t,s,i]=await Promise.all([Ts(this.hass),Ds(this.hass),Ls(this.hass)]);this.config=t,this.zones=s,this.mappings=i,this._initialLoadDone=!0,this.mappingCache.clear()}catch(e){console.error("Error fetching data:",e),ja(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}handleAddMapping(){if(!this.mappingNameInput.value.trim())return;const e={[He]:"",[Ie]:"",[Ne]:"",[Le]:"",[Pe]:"",[Re]:"",[Be]:"",[Ue]:"",[je]:""},t={name:this.mappingNameInput.value.trim(),mappings:e};this.mappings=[...this.mappings,t],this.isSaving=!0,this.saveToHA(t).then(()=>(this.mappingNameInput.value="",this._fetchData())).catch(e=>{console.error("Failed to add mapping:",e),ja(this,this.hass,"common.errors.save_failed",e),this.mappings=this.mappings.slice(0,-1)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()})}handleRemoveMapping(e,t){const s=this.mappings[t].id;if(null==s)return;const i=[...this.mappings];var a,n;(this.mappings=this.mappings.filter((e,s)=>s!==t),this.mappingCache.delete(s.toString()),this.hass)&&(this.isSaving=!0,(a=this.hass,n=s.toString(),a.callApi("POST",be+"/mappings",{id:n,remove:!0})).catch(e=>{console.error("Failed to delete mapping:",e),ja(this,this.hass,"common.errors.delete_failed",e),this.mappings=i,this._fetchData().catch(e=>{console.error("Failed to refresh data after delete error:",e)})}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}))}handleEditMapping(e,t){this.mappings[e]=t,t.id&&this.mappingCache.delete(t.id.toString()),this.globalDebounceTimer&&clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=window.setTimeout(()=>{this.isSaving=!0,this.saveToHA(t).catch(e=>{console.error("Failed to save mapping:",e),ja(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}),this.globalDebounceTimer=null},500),this._scheduleUpdate()}async saveToHA(e){var t;if(!this.hass)throw new Error("Home Assistant connection not available");const s=[],i=this.hass.states;for(const t in e.mappings){const a=e.mappings[t].sensorentity;if(a&&""!==a.trim()){const n=a.trim();e.mappings[t].sensorentity=n,n in i||s.push(n)}}if(s.length>0){const e=null===(t=this.shadowRoot)||void 0===t?void 0:t.querySelector("ha-card");throw e&&La({body:{message:Ma("panels.mappings.cards.mapping.errors.source_does_not_exist",this.hass.language)+": "+s.join(", ")},error:Ma("panels.mappings.cards.mapping.errors.invalid_source",this.hass.language)},e),new Error("Invalid sensor entities found")}const{id:a,name:n,mappings:o}=e;await Ps(this.hass,{id:a,name:n,mappings:o})}renderMappingSetting(e,t){const s=this.mappings[e];if(!s||!this.hass)return W``;const i=s.mappings[t];return W`
      <div class="mappingline">
        <div class="mappingsettingname">
          <label for="${`${t}_${e}`}">
            ${Ma(`panels.mappings.cards.mapping.items.${t.toLowerCase()}`,this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </label>
        </div>
        <div class="mappingsettingline">
          <label
<<<<<<< HEAD
            >${Oa("panels.mappings.cards.mapping.source",this.hass.language)}:</label
=======
            >${Ma("panels.mappings.cards.mapping.source",this.hass.language)}:</label
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          >
          <div class="radio-group">
            ${this.renderSimpleRadioOptions(e,t,s)}
          </div>
        </div>
        ${this.renderMappingInputs(e,t,s)}
      </div>
    `}renderSimpleRadioOptions(e,t,i){if(!this.hass||!this.config)return W``;const s=t===Ie||t===Be,a=i[Ye];return W`
      ${!s&&this.config.use_weather_service?W`
            <label>
              <input
                type="radio"
                name="${t}_${e}_source"
                value="${Fe}"
                ?checked="${a===Fe}"
                @change="${i=>this.handleSimpleSourceChange(e,t,i)}"
              />
<<<<<<< HEAD
              ${Oa("panels.mappings.cards.mapping.sources.weather_service",this.hass.language)}
=======
              ${Ma("panels.mappings.cards.mapping.sources.weather_service",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </label>
          `:""}
      ${s?W`
            <label>
              <input
                type="radio"
                name="${t}_${e}_source"
                value="${Ve}"
                ?checked="${a===Ve}"
                @change="${i=>this.handleSimpleSourceChange(e,t,i)}"
              />
<<<<<<< HEAD
              ${Oa("panels.mappings.cards.mapping.sources.none",this.hass.language)}
=======
              ${Ma("panels.mappings.cards.mapping.sources.none",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </label>
          `:""}

      <label>
        <input
          type="radio"
          name="${t}_${e}_source"
          value="${Ze}"
          ?checked="${a===Ze}"
          @change="${i=>this.handleSimpleSourceChange(e,t,i)}"
        />
<<<<<<< HEAD
        ${Oa("panels.mappings.cards.mapping.sources.sensor",this.hass.language)}
=======
        ${Ma("panels.mappings.cards.mapping.sources.sensor",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      </label>

      <label>
        <input
          type="radio"
          name="${t}_${e}_source"
          value="${We}"
          ?checked="${a===We}"
          @change="${i=>this.handleSimpleSourceChange(e,t,i)}"
        />
<<<<<<< HEAD
        ${Oa("panels.mappings.cards.mapping.sources.static",this.hass.language)}
=======
        ${Ma("panels.mappings.cards.mapping.sources.static",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      </label>
    `}handleSimpleSourceChange(e,t,i){const s=this.mappings[e],a=i.target.value;this.handleEditMapping(e,Object.assign(Object.assign({},s),{mappings:Object.assign(Object.assign({},s.mappings),{[t]:Object.assign(Object.assign({},s.mappings[t]),{[Ye]:a,[Xe]:""})})}))}handleSimpleInputChange(e,t,i,s){const a=this.mappings[e],n=s.target.value;this.handleEditMapping(e,Object.assign(Object.assign({},a),{mappings:Object.assign(Object.assign({},a.mappings),{[t]:Object.assign(Object.assign({},a.mappings[t]),{[i]:n})})}))}renderMappingInputs(e,t,i){if(!this.hass)return W``;const s=i[Ye];return W`
      ${s===Ze?this.renderSensorInput(e,t,i):""}
      ${s===We?this.renderStaticValueInput(e,t,i):""}
      ${s===Ze||s===We?this.renderUnitSelect(e,t,i):""}
      ${t!==Re||s!==Ze&&s!==We?"":this.renderPressureTypeSelect(e,t,i)}
      ${s===Ze?this.renderAggregateSelect(e,t,i):""}
    `}renderSensorInput(e,t,i){if(!this.hass)return W``;const s=`${t}_${e}`;return W`
      <div class="mappingsettingline">
<<<<<<< HEAD
        <label for="${s}_sensor_entity">
          ${Oa("panels.mappings.cards.mapping.sensor-entity",this.hass.language)}:
=======
        <label for="${i}_sensor_entity">
          ${Ma("panels.mappings.cards.mapping.sensor-entity",this.hass.language)}:
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </label>
        <input
          type="text"
          class="settings-input"
          id="${s}_sensor_entity"
          .value="${i[Xe]||""}"
          @change="${i=>this.handleSensorChange(e,t,i)}"
        />
      </div>
    `}renderStaticValueInput(e,t,i){if(!this.hass)return W``;const s=`${t}_${e}`;return W`
      <div class="mappingsettingline">
<<<<<<< HEAD
        <label for="${s}_static_value">
          ${Oa("panels.mappings.cards.mapping.static_value",this.hass.language)}:
=======
        <label for="${i}_static_value">
          ${Ma("panels.mappings.cards.mapping.static_value",this.hass.language)}:
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </label>
        <input
          type="text"
          class="settings-input"
          id="${s}_static_value"
          .value="${i[Je]||""}"
          @input="${i=>this.handleStaticValueChange(e,t,i)}"
        />
      </div>
    `}renderUnitSelect(e,t,i){if(!this.hass||!this.config)return W``;const s=`${t}_${e}`;return W`
      <div class="mappingsettingline">
<<<<<<< HEAD
        <label for="${s}_unit">
          ${Oa("panels.mappings.cards.mapping.input-units",this.hass.language)}:
=======
        <label for="${i}_unit">
          ${Ma("panels.mappings.cards.mapping.input-units",this.hass.language)}:
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </label>
        <select
          id="${s}_unit"
          class="settings-input"
          @change="${i=>this.handleUnitChange(e,t,i)}"
        >
          ${this.renderUnitOptionsForMapping(t,i)}
        </select>
      </div>
    `}renderPressureTypeSelect(e,t,i){if(!this.hass)return W``;const s=`${t}_${e}`;return W`
      <div class="mappingsettingline">
<<<<<<< HEAD
        <label for="${s}_pressure_type">
          ${Oa("panels.mappings.cards.mapping.pressure-type",this.hass.language)}:
=======
        <label for="${i}_pressure_type">
          ${Ma("panels.mappings.cards.mapping.pressure-type",this.hass.language)}:
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </label>
        <select
          id="${s}_pressure_type"
          class="settings-input"
          @change="${i=>this.handlePressureTypeChange(e,t,i)}"
        >
          ${this.renderPressureTypes(t,i)}
        </select>
      </div>
    `}renderAggregateSelect(e,t,i){if(!this.hass)return W``;const s=`${t}_${e}`;return W`
      <div class="mappingsettingline">
<<<<<<< HEAD
        <label for="${s}_aggregate">
          ${Oa("panels.mappings.cards.mapping.sensor-aggregate-use-the",this.hass.language)}
=======
        <label for="${i}_aggregate">
          ${Ma("panels.mappings.cards.mapping.sensor-aggregate-use-the",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </label>
        <select
          id="${s}_aggregate"
          class="settings-input"
          @change="${i=>this.handleAggregateChange(e,t,i)}"
        >
          ${this.renderAggregateOptionsForMapping(t,i)}
        </select>
<<<<<<< HEAD
        <label for="${s}_aggregate">
          ${Oa("panels.mappings.cards.mapping.sensor-aggregate-of-sensor-values-to-calculate",this.hass.language)}
=======
        <label for="${i}_aggregate">
          ${Ma("panels.mappings.cards.mapping.sensor-aggregate-of-sensor-values-to-calculate",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </label>
      </div>
    `}handleSensorChange(e,t,i){const s=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},s),{mappings:Object.assign(Object.assign({},s.mappings),{[t]:Object.assign(Object.assign({},s.mappings[t]),{[Xe]:i.target.value})})}))}handleStaticValueChange(e,t,i){const s=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},s),{mappings:Object.assign(Object.assign({},s.mappings),{[t]:Object.assign(Object.assign({},s.mappings[t]),{[Je]:i.target.value})})}))}handleUnitChange(e,t,i){const s=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},s),{mappings:Object.assign(Object.assign({},s.mappings),{[t]:Object.assign(Object.assign({},s.mappings[t]),{[Qe]:i.target.value})})}))}handlePressureTypeChange(e,t,i){const s=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},s),{mappings:Object.assign(Object.assign({},s.mappings),{[t]:Object.assign(Object.assign({},s.mappings[t]),{[qe]:i.target.value})})}))}handleAggregateChange(e,t,i){const s=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},s),{mappings:Object.assign(Object.assign({},s.mappings),{[t]:Object.assign(Object.assign({},s.mappings[t]),{[et]:i.target.value})})}))}renderAggregateOptionsForMapping(e,t){if(!this.hass||!this.config)return W``;let i="average";return e===Pe&&(i="delta"),e===Le&&(i="average"),t[et]&&(i=t[et]),W`
      ${tt.map(e=>this.renderAggregateOption(e,i))}
    `}renderAggregateOption(e,t){if(this.hass&&this.config){return W`<option value="${e}" ?selected="${e===t}">
<<<<<<< HEAD
        ${Oa("panels.mappings.cards.mapping.aggregates."+e,this.hass.language)}
      </option>`}return W``}renderPressureTypes(e,t){if(this.hass&&this.config){let e=W``;const i=t[qe];return e=W`${e}
=======
        ${Ma("panels.mappings.cards.mapping.aggregates."+e,this.hass.language)}
      </option>`}return W``}renderPressureTypes(e,t){if(this.hass&&this.config){let e=W``;const s=t[qe];return e=W`${e}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        <option
          value="${Ge}"
          ?selected="${i===Ge}"
        >
<<<<<<< HEAD
          ${Oa("panels.mappings.cards.mapping.pressure_types."+Ge,this.hass.language)}
=======
          ${Ma("panels.mappings.cards.mapping.pressure_types."+Ge,this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </option>
        <option
          value="${Ke}"
          ?selected="${i===Ke}"
        >
<<<<<<< HEAD
          ${Oa("panels.mappings.cards.mapping.pressure_types."+Ke,this.hass.language)}
        </option>`,e}return W``}renderUnitOptionsForMapping(e,t){if(!this.hass||!this.config)return W``;const i=function(e){switch(e){case Me:case Ue:return[{unit:"°C",system:De},{unit:"°F",system:He}];case Pe:case Ie:return[{unit:ot,system:De},{unit:rt,system:He}];case Le:return[{unit:ht,system:De},{unit:ut,system:He}];case Ne:return[{unit:"%",system:[De,He]}];case Re:return[{unit:"millibar",system:De},{unit:"hPa",system:De},{unit:"psi",system:He},{unit:lt,system:He}];case je:return[{unit:"km/h",system:De},{unit:ct,system:De},{unit:dt,system:He}];case Be:return[{unit:"W/m2",system:De},{unit:"MJ/day/m2",system:De},{unit:"W/sq ft",system:He},{unit:"MJ/day/sq ft",system:He}];default:return[]}}(e);let s=t[Qe];const a=this.config.units;if(!t[Qe])for(const e of i)if("string"==typeof e.system){if(a===e.system){s=e.unit;break}}else{for(const t of e.system)if(a===t.system){s=e.unit;break}if(s===e.unit)break}return W`
      ${i.map(e=>W`
          <option value="${e.unit}" ?selected="${s===e.unit}">
=======
          ${Ma("panels.mappings.cards.mapping.pressure_types."+Ke,this.hass.language)}
        </option>`,e}return W``}renderUnitOptionsForMapping(e,t){if(!this.hass||!this.config)return W``;const s=function(e){switch(e){case He:case Ue:return[{unit:"°C",system:Me},{unit:"°F",system:De}];case Le:case Ie:return[{unit:ot,system:Me},{unit:rt,system:De}];case Pe:return[{unit:ht,system:Me},{unit:ut,system:De}];case Ne:return[{unit:"%",system:[Me,De]}];case Re:return[{unit:"millibar",system:Me},{unit:"hPa",system:Me},{unit:"psi",system:De},{unit:lt,system:De}];case je:return[{unit:"km/h",system:Me},{unit:ct,system:Me},{unit:dt,system:De}];case Be:return[{unit:"W/m2",system:Me},{unit:"MJ/day/m2",system:Me},{unit:"W/sq ft",system:De},{unit:"MJ/day/sq ft",system:De}];default:return[]}}(e);let i=t[Qe];const a=this.config.units;if(!t[Qe])for(const e of s)if("string"==typeof e.system){if(a===e.system){i=e.unit;break}}else{for(const t of e.system)if(a===t.system){i=e.unit;break}if(i===e.unit)break}return W`
      ${s.map(e=>W`
          <option value="${e.unit}" ?selected="${i===e.unit}">
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            ${e.unit}
          </option>
        `)}
    `}render(){return this.hass?this.isLoading?W`
        <ha-card
<<<<<<< HEAD
          header="${Oa("panels.mappings.title",this.hass.language)}"
        >
          <div class="card-content">
            <div class="loading-indicator">
              ${Oa("common.loading-messages.general",this.hass.language)}
=======
          header="${Ma("panels.mappings.title",this.hass.language)}"
        >
          <div class="card-content">
            <div class="loading-indicator">
              ${Ma("common.loading-messages.general",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </div>
          </div>
        </ha-card>
      `:W`
      <ha-card
<<<<<<< HEAD
        header="${Oa("panels.mappings.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Oa("panels.mappings.description",this.hass.language)}
=======
        header="${Ma("panels.mappings.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Ma("panels.mappings.description",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          <div class="add-row">
            <input
              id="mappingNameInput"
              class="settings-input"
              type="text"
<<<<<<< HEAD
              placeholder="${Oa("panels.mappings.labels.mapping-name",this.hass.language)}"
=======
              placeholder="${Ma("panels.mappings.labels.mapping-name",this.hass.language)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            />
            <button
              class="action-btn ${this.isSaving?"saving":""}"
              ?disabled="${this.isSaving}"
              @click="${this.handleAddMapping}"
            >
              <ha-icon icon="mdi:plus"></ha-icon>
<<<<<<< HEAD
              ${Oa("panels.mappings.cards.add-mapping.actions.add",this.hass.language)}
=======
              ${Ma("panels.mappings.cards.add-mapping.actions.add",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </button>
          </div>
        </div>
      </ha-card>

      ${this.renderMappingsList()}
    `:W``}renderUsageChip(e){return this.hass?e?W`<span class="usage-chip"
<<<<<<< HEAD
          >${Oa("panels.setup.advanced.used_by_zones",this.hass.language,"{count}",e)}</span
        >`:W`<span class="usage-chip unused"
          >${Oa("panels.setup.advanced.not_used",this.hass.language)}</span
=======
          >${Ma("panels.setup.advanced.used_by_zones",this.hass.language,"{count}",e)}</span
        >`:W`<span class="usage-chip unused"
          >${Ma("panels.setup.advanced.not_used",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >`:W``}renderMappingsList(){const e=this.mappings.slice(0,Math.min(this.mappings.length,10)),t=this.mappings.slice(10);return W`
      ${e.map((e,t)=>this.renderMappingCard(e,t))}
      ${t.length>0?W`
            <div class="load-more">
              <button @click="${this.loadMoreMappings}">
                Load ${t.length} more mappings...
              </button>
            </div>
          `:""}
    `}renderMappingCard(e,t){if(!this.hass)return W``;const i=this.zones.filter(t=>t.mapping===e.id).length;return W`
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          ${this.renderUsageChip(i)}
        </div>
        <div class="card-content">
          <ha-settings-row>
            <span slot="heading"
<<<<<<< HEAD
              >${Oa("panels.mappings.labels.mapping-name",this.hass.language)}</span
=======
              >${Ma("panels.mappings.labels.mapping-name",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            >
            <input
              id="name${e.id}"
              class="settings-input"
              type="text"
              .value="${e.name}"
              @input="${i=>this.handleEditMapping(t,Object.assign(Object.assign({},e),{name:i.target.value}))}"
            />
          </ha-settings-row>
          ${this.renderMappingSettings(e,t)}
          <div class="card-footer">
<<<<<<< HEAD
            ${i?W`<div class="weather-note">
                  ${Oa("panels.mappings.cards.mapping.errors.cannot-delete-mapping-because-zones-use-it",this.hass.language)}
=======
            ${s?W`<div class="weather-note">
                  ${Ma("panels.mappings.cards.mapping.errors.cannot-delete-mapping-because-zones-use-it",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </div>`:W`<button
                  class="action-btn danger"
                  @click="${e=>this.handleRemoveMapping(e,t)}"
                >
                  <ha-icon icon="mdi:delete"></ha-icon>
<<<<<<< HEAD
                  ${Oa("common.actions.delete",this.hass.language)}
=======
                  ${Ma("common.actions.delete",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </button>`}
          </div>
        </div>
      </ha-card>
    `}renderMappingSettings(e,t){const i=Object.entries(e.mappings);return W`
      ${i.map(([e])=>this.renderMappingSetting(t,e))}
    `}loadMoreMappings(){this._scheduleUpdate()}static get styles(){return r`
      ${Ka}

      /* Parameter section header inside a sensor-group card */
      .mappingsettingname {
        font-weight: 500;
        font-size: 0.95rem;
        color: var(--primary-text-color);
        padding-bottom: 6px;
        margin-bottom: 4px;
        border-bottom: 1px solid var(--divider-color);
      }
<<<<<<< HEAD
<<<<<<< HEAD
    `}disconnectedCallback(){super.disconnectedCallback(),this.debounceTimers.forEach(e=>{clearTimeout(e)}),this.debounceTimers.clear(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null),this.mappingCache.clear()}};t([me()],vn.prototype,"config",void 0),t([me({type:Array})],vn.prototype,"zones",void 0),t([me({type:Array})],vn.prototype,"mappings",void 0),t([me({type:Boolean})],vn.prototype,"isLoading",void 0),t([me({type:Boolean})],vn.prototype,"isSaving",void 0),t([fe("#mappingNameInput")],vn.prototype,"mappingNameInput",void 0),vn=t([ue("smart-irrigation-view-mappings")],vn);const fn="06:00";function _n(e){switch(e){case si:return{mode:e,time:fn};case ai:case ni:return{mode:e,offset:0};case oi:return{mode:e,azimuth:90};default:return{mode:ii}}}function bn(e,t,i,s){const a=function(e){return e===ii||e===si||e===ai||e===ni||e===oi}(e)?e:ii,n=_n(a);return a===si&&void 0!==t&&(n.time=t),a!==ai&&a!==ni||void 0===i||(n.offset=i),a===oi&&void 0!==s&&(n.azimuth=s),n}function yn(e){var t,i,s;return{mode:e.mode,time:e.mode===si?null!==(t=e.time)&&void 0!==t?t:fn:void 0,offset:e.mode===ai||e.mode===ni?null!==(i=e.offset)&&void 0!==i?i:0:void 0,azimuth:e.mode===oi?null!==(s=e.azimuth)&&void 0!==s?s:90:void 0}}function wn(e){return{start:bn(e.start_mode,e.start_time,e.start_offset,e.start_azimuth),finish:bn(e.finish_mode,e.finish_time,e.finish_offset,e.finish_azimuth),anchor:e.anchor===li?li:di}}function $n(e){const t=e.start.mode!==ii,i=e.finish.mode!==ii;return t||i?t?i?e.anchor===di?{start:"demand_floored",finish:"exact_deferred",valid:!0}:{start:"exact",finish:"demand_capped_deferred",valid:!0}:{start:"exact",finish:"demand_open",valid:!0}:{start:"demand_open",finish:"exact",valid:!0}:{start:"error",finish:"error",valid:!1}}const xn=1440,kn=44,zn=260;function Sn(e){return(e%xn+xn)%xn}function An(e){const t=Math.round(Sn(e)),i=Math.floor(t/60),s=t%60;return`${String(i).padStart(2,"0")}:${String(s).padStart(2,"0")}`}function En(e){const t=Math.floor(e/60),i=Math.round(e%60);return t?`${t}h ${i}m`:`${i}m`}function Cn(e,t){const i=t/xn*2*Math.PI+Math.PI/2;return[66+e*Math.cos(i),66+e*Math.sin(i)]}function Tn(e,t,i){const s=i-t>=xn?t+xn-.5:i,[a,n]=Cn(e,t),[o,r]=Cn(e,s),l=s-t>720?1:0;return`M ${a.toFixed(2)} ${n.toFixed(2)} A ${e} ${e} 0 ${l} 1 ${o.toFixed(2)} ${r.toFixed(2)}`}function On(e,t,i,s,a){const n=2*Math.PI*e/xn,o=[[0,i]];for(let e=0;e<=10;e++){const t=Math.PI/2+e/10*(Math.PI/2);o.push([s*Math.cos(t),i-s+s*Math.sin(t)])}for(let e=0;e<=10;e++){const t=Math.PI+e/10*(Math.PI/2);o.push([s*Math.cos(t),s*Math.sin(t)-3.2])}return o.push([0,-i]),o.map(([i,s],o)=>{const[r,l]=Cn(e+s,(e=>t-a*e/n)(i));return`${o?"L":"M"} ${r.toFixed(2)} ${l.toFixed(2)}`}).join(" ")+" Z"}function Hn(e,t,i,s,a){const n=(t-e)/48,o=[];for(let r=0;r<48;r++){const l=e+r*n,d=l+n/2;let c=1;i>0&&(c=Math.min(c,(d-e)/i)),s>0&&(c=Math.min(c,(t-d)/s)),c=Math.max(0,Math.min(1,c)),o.push({d:Tn(a,l,l+1.25*n),opacity:c})}return o}function Dn(e){const[t,i]=e.split(":").map(e=>parseInt(e,10));return 60*(t||0)+(i||0)}function Mn(e,t,i){var s,a,n;switch(e.mode){case si:return Sn(Dn(null!==(s=e.time)&&void 0!==s?s:"06:00"));case ai:return Sn(t+(null!==(a=e.offset)&&void 0!==a?a:0));case ni:return Sn(i+(null!==(n=e.offset)&&void 0!==n?n:0));default:return null}}function In(e,t){return{wraps:!1,arc:Tn(kn,e,t),capStart:On(kn,e,5,1.8,-1),capEnd:On(kn,t,5,1.8,1)}}function Nn(e){const{rows:t,recurrence:i,intervalHours:s,intervalStartTime:a,nominalDemandMinutes:n,sunriseMinutes:o,sunsetMinutes:r}=e,l=Tn(kn,0,xn),d=[0,360,720,1080].map(e=>{const[t,i]=Cn(38,e),[s,a]=Cn(50,e);return{x1:t,y1:i,x2:s,y2:a}}),[c,h]=Cn(57,o),[u,p]=Cn(57,r);if(i===ei){const{runs:e,overlaps:t,wrapAt:i}=function(e,t,i){const s=60*Math.max(1,Number(t)||24),a=i?Dn(i):0,n=[];for(let t=a;t<a+xn&&n.length<24;t+=s)n.push([t,t+e]);const o=[];for(let e=0;e+1<n.length;e++)n[e][1]>n[e+1][0]&&o.push([n[e+1][0],Math.min(n[e][1],n[e+1][1])]);return{runs:n,overlaps:o,wrapAt:a+xn}}(n,s,a),g=e.map(([e,t])=>{if(t<=i)return In(e,t);const s=i-8,a=s-e,n=Math.min(a,120);return{wraps:!0,capStart:On(kn,e,5,1.8,-1),fade:Hn(e,s,0,n,kn)}});return{trackPath:l,windowArc:null,dottedPath:null,runs:g,overlaps:t.map(([e,t])=>({d:Tn(kn,e,t),fromMinutes:e,toMinutes:t})),ticks:d,sun:{x:c,y:h,minutes:o},moon:{x:u,y:p,minutes:r},drops:e.map(([e,t])=>{const[i,s]=Cn(57,(e+t)/2);return{x:i,y:s,fromMinutes:e,toMinutes:t}}),centre:{kind:"interval",perDay:e.length,intervalHours:Math.max(1,Number(s)||24)}}}const g=Mn(t.start,o,r),m=Mn(t.finish,o,r);if(null===g&&null===m)return{trackPath:l,windowArc:null,dottedPath:null,runs:[],overlaps:[],ticks:d,sun:{x:c,y:h,minutes:o},moon:{x:u,y:p,minutes:r},drops:[],centre:{kind:"invalid"}};const v=null!==g&&null!==m?(()=>{const e=Sn(m-g);return 0===e?xn:e})():null;let f,_,b=0;if(null!==g&&null!==m){const e=v;_=Math.min(n,e),b=Math.max(0,n-e),f=t.anchor===di?g+Sn(m-g)-_:g}else null!==g?(f=g,_=n):(_=n,f=m-_);const y=f+_;let w=null!=g?g:f,$=null!=m?m:y,x=0,k=0;null===g&&(w=f-zn,x=zn),null===m&&($=y+zn,k=zn);const z=null!==v&&v<60,S=null===g||null===m?{kind:"faded",segments:Hn(w,$,x,k,kn)}:{kind:"solid",d:Tn(kn,w,z?w+60:$)},A=b>1?Tn(kn,f-b,f):null,[E,C]=Cn(57,(f+y)/2),T=null===v?{kind:"run",minutes:_}:{kind:"window",minutes:v};return{trackPath:l,windowArc:S,dottedPath:A,runs:[In(f,y)],overlaps:[],ticks:d,sun:{x:c,y:h,minutes:o},moon:{x:u,y:p,minutes:r},drops:[{x:E,y:C,fromMinutes:f,toMinutes:y}],centre:T}}const Pn=q`<circle cx="12" cy="12" r="4.4" />
  ${Array.from({length:8},(e,t)=>{const i=t*Math.PI/4,s=(12+6.6*Math.cos(i)).toFixed(1),a=(12+6.6*Math.sin(i)).toFixed(1),n=(12+9.2*Math.cos(i)).toFixed(1),o=(12+9.2*Math.sin(i)).toFixed(1);return q`<line x1="${s}" y1="${a}" x2="${n}" y2="${o}" />`})}`,Ln=q`<path d="M13.5,2.5A9.5,9.5 0 1,0 21.5,14 7.6,7.6 0 0,1 13.5,2.5Z" />`,Rn=q`<path d="M12,2.6C12,2.6 18.6,9.4 18.6,13.7A6.6,6.6 0 0,1 5.4,13.7C5.4,9.4 12,2.6 12,2.6Z" />`;let Bn=class extends ce{constructor(){super(...arguments),this.recurrence="daily",this.nominalDemandSeconds=0}_sunTimes(){var e,t,i,s;const a=null===(t=null===(e=this.hass)||void 0===e?void 0:e.states)||void 0===t?void 0:t["sun.sun"],n=null===(i=null==a?void 0:a.attributes)||void 0===i?void 0:i.next_rising,o=null===(s=null==a?void 0:a.attributes)||void 0===s?void 0:s.next_setting,r=(e,t)=>{if(!e)return t;const i=new Date(e);return isNaN(i.getTime())?t:60*i.getHours()+i.getMinutes()};return{sunrise:r(n,360),sunset:r(o,1200)}}_renderRun(e,t){return e.wraps?q`
=======
    `}disconnectedCallback(){super.disconnectedCallback(),this.debounceTimers.forEach(e=>{clearTimeout(e)}),this.debounceTimers.clear(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null),this.mappingCache.clear()}};t([me()],_n.prototype,"config",void 0),t([me({type:Array})],_n.prototype,"zones",void 0),t([me({type:Array})],_n.prototype,"mappings",void 0),t([me({type:Boolean})],_n.prototype,"isLoading",void 0),t([me({type:Boolean})],_n.prototype,"isSaving",void 0),t([fe("#mappingNameInput")],_n.prototype,"mappingNameInput",void 0),_n=t([ue("smart-irrigation-view-mappings")],_n);const bn="06:00",yn=90;function wn(e){switch(e){case ns:return{mode:e,time:bn};case os:case rs:return{mode:e,offset:0};case ls:return{mode:e,azimuth:yn};default:return{mode:as}}}function $n(e,t,s,i){const a=function(e){return e===as||e===ns||e===os||e===rs||e===ls}(e)?e:as,n=wn(a);return a===ns&&void 0!==t&&(n.time=t),a!==os&&a!==rs||void 0===s||(n.offset=s),a===ls&&void 0!==i&&(n.azimuth=i),n}function xn(e){var t,s,i;return{mode:e.mode,time:e.mode===ns?null!==(t=e.time)&&void 0!==t?t:bn:void 0,offset:e.mode===os||e.mode===rs?null!==(s=e.offset)&&void 0!==s?s:0:void 0,azimuth:e.mode===ls?null!==(i=e.azimuth)&&void 0!==i?i:yn:void 0}}function kn(e){return{start:$n(e.start_mode,e.start_time,e.start_offset,e.start_azimuth),finish:$n(e.finish_mode,e.finish_time,e.finish_offset,e.finish_azimuth),anchor:e.anchor===cs?cs:hs}}function zn(e){const t=e.start.mode!==as,s=e.finish.mode!==as;return t||s?t?s?e.anchor===hs?{start:"demand_floored",finish:"exact_deferred",valid:!0}:{start:"exact",finish:"demand_capped_deferred",valid:!0}:{start:"exact",finish:"demand_open",valid:!0}:{start:"demand_open",finish:"exact",valid:!0}:{start:"error",finish:"error",valid:!1}}function Sn(e,t){const s=function(e,t){if("all"===e||!Array.isArray(e))return Ma("panels.schedules.summary.zones_all",t);return Ma("panels.schedules.summary.zones_some",t,"count",e.length)}(e.zones,t),i=function(e,t){switch(e.recurrence){case es:{const s=(e.days_of_week||[]).map(e=>Ma(`panels.schedules.days.${e}`,t)).join(", ");return Ma("panels.schedules.summary.recurrence_weekly",t,"days",s)}case ts:return Ma("panels.schedules.summary.recurrence_monthly",t,"day",e.day_of_month||1);case ss:{const s=e.interval_hours||24;return e.start_time?Ma("panels.schedules.summary.recurrence_interval_at",t,"hours",s,"time",e.start_time):Ma("panels.schedules.summary.recurrence_interval",t,"hours",s)}default:return Ma("panels.schedules.summary.recurrence_daily",t)}}(e,t);if(e.recurrence===ss){return{text:`${i}, ${Ma("panels.schedules.summary.watering",t,"zones",s)}.`,isError:!1}}const a=kn(e),n=a.start.mode!==as,o=a.finish.mode!==as;if(!n&&!o)return{text:Ma("panels.schedules.summary.invalid",t),isError:!0};const r=Ma("panels.schedules.summary.watering",t,"zones",s);let l;return l=n?o?a.anchor===hs?Ma("panels.schedules.summary.anchor_finish",t,"finish",An(a.finish,t),"start",An(a.start,t)):Ma("panels.schedules.summary.anchor_start",t,"start",An(a.start,t),"finish",An(a.finish,t)):Ma("panels.schedules.summary.start_only",t,"when",An(a.start,t)):Ma("panels.schedules.summary.finish_only",t,"when",An(a.finish,t)),{text:`${i}, ${r}, ${l}.`,isError:!1}}function An(e,t){var s,i,a;switch(e.mode){case ns:return null!==(s=e.time)&&void 0!==s?s:"";case os:case rs:{const s=Ma(`panels.schedules.summary.${e.mode}`,t),a=null!==(i=e.offset)&&void 0!==i?i:0;if(0===a)return s;return Ma(a<0?"panels.schedules.summary.offset_before":"panels.schedules.summary.offset_after",t,"minutes",Math.abs(a),"event",s)}case ls:return Ma("panels.schedules.summary.at_azimuth",t,"degrees",null!==(a=e.azimuth)&&void 0!==a?a:yn);default:return""}}const Cn=1440,En=44,Tn=260;function On(e){return(e%Cn+Cn)%Cn}function Dn(e){const t=Math.round(On(e)),s=Math.floor(t/60),i=t%60;return`${String(s).padStart(2,"0")}:${String(i).padStart(2,"0")}`}function Mn(e){const t=Math.floor(e/60),s=Math.round(e%60);return t?`${t}h ${s}m`:`${s}m`}function Hn(e,t){const s=t/Cn*2*Math.PI+Math.PI/2;return[66+e*Math.cos(s),66+e*Math.sin(s)]}function In(e,t,s){const i=s-t>=Cn?t+Cn-.5:s,[a,n]=Hn(e,t),[o,r]=Hn(e,i),l=i-t>720?1:0;return`M ${a.toFixed(2)} ${n.toFixed(2)} A ${e} ${e} 0 ${l} 1 ${o.toFixed(2)} ${r.toFixed(2)}`}function Nn(e,t,s,i,a){const n=2*Math.PI*e/Cn,o=[[0,s]];for(let e=0;e<=10;e++){const t=Math.PI/2+e/10*(Math.PI/2);o.push([i*Math.cos(t),s-i+i*Math.sin(t)])}for(let e=0;e<=10;e++){const t=Math.PI+e/10*(Math.PI/2);o.push([i*Math.cos(t),i*Math.sin(t)-3.2])}return o.push([0,-s]),o.map(([s,i],o)=>{const[r,l]=Hn(e+i,(e=>t-a*e/n)(s));return`${o?"L":"M"} ${r.toFixed(2)} ${l.toFixed(2)}`}).join(" ")+" Z"}function Ln(e,t,s,i,a){const n=(t-e)/48,o=[];for(let r=0;r<48;r++){const l=e+r*n,d=l+n/2;let c=1;s>0&&(c=Math.min(c,(d-e)/s)),i>0&&(c=Math.min(c,(t-d)/i)),c=Math.max(0,Math.min(1,c)),o.push({d:In(a,l,l+1.25*n),opacity:c})}return o}function Pn(e){const[t,s]=e.split(":").map(e=>parseInt(e,10));return 60*(t||0)+(s||0)}function Rn(e,t,s,i){var a,n,o,r;switch(e.mode){case ns:return On(Pn(null!==(a=e.time)&&void 0!==a?a:"06:00"));case os:return On(t+(null!==(n=e.offset)&&void 0!==n?n:0));case rs:return On(s+(null!==(o=e.offset)&&void 0!==o?o:0));case ls:{if(!i)return null;const t=i(null!==(r=e.azimuth)&&void 0!==r?r:yn);return null===t?null:On(t)}default:return null}}function Bn(e,t){return{wraps:!1,arc:In(En,e,t),capStart:Nn(En,e,5,1.8,-1),capEnd:Nn(En,t,5,1.8,1)}}function Un(e){const{rows:t,recurrence:s,intervalHours:i,intervalStartTime:a,nominalDemandMinutes:n,sunriseMinutes:o,sunsetMinutes:r,azimuthResolver:l}=e,d=In(En,0,Cn),c=[0,360,720,1080].map(e=>{const[t,s]=Hn(38,e),[i,a]=Hn(50,e);return{x1:t,y1:s,x2:i,y2:a}}),[h,u]=Hn(57,o),[p,g]=Hn(57,r);if(s===ss){const{runs:e,overlaps:t,wrapAt:s}=function(e,t,s){const i=60*Math.max(1,Number(t)||24),a=s?Pn(s):0,n=[];for(let t=a;t<a+Cn&&n.length<24;t+=i)n.push([t,t+e]);const o=[];for(let e=0;e+1<n.length;e++)n[e][1]>n[e+1][0]&&o.push([n[e+1][0],Math.min(n[e][1],n[e+1][1])]);return{runs:n,overlaps:o,wrapAt:a+Cn}}(n,i,a),l=e.map(([e,t])=>{if(t<=s)return Bn(e,t);const i=s-8,a=i-e,n=Math.min(a,120);return{wraps:!0,capStart:Nn(En,e,5,1.8,-1),fade:Ln(e,i,0,n,En)}});return{trackPath:d,windowArc:null,dottedPath:null,runs:l,overlaps:t.map(([e,t])=>({d:In(En,e,t),fromMinutes:e,toMinutes:t})),ticks:c,sun:{x:h,y:u,minutes:o},moon:{x:p,y:g,minutes:r},drops:e.map(([e,t])=>{const[s,i]=Hn(57,(e+t)/2);return{x:s,y:i,fromMinutes:e,toMinutes:t}}),centre:{kind:"interval",perDay:e.length,intervalHours:Math.max(1,Number(i)||24)}}}const m=Rn(t.start,o,r,l),v=Rn(t.finish,o,r,l);if(null===m&&null===v)return{trackPath:d,windowArc:null,dottedPath:null,runs:[],overlaps:[],ticks:c,sun:{x:h,y:u,minutes:o},moon:{x:p,y:g,minutes:r},drops:[],centre:{kind:"invalid"}};const f=null!==m&&null!==v?(()=>{const e=On(v-m);return 0===e?Cn:e})():null;let _,b,y=0;if(null!==m&&null!==v){const e=f;b=Math.min(n,e),y=Math.max(0,n-e),_=t.anchor===hs?m+On(v-m)-b:m}else null!==m?(_=m,b=n):(b=n,_=v-b);const w=_+b;let $=null!=m?m:_,x=null!=v?v:w,k=0,z=0;null===m&&($=_-Tn,k=Tn),null===v&&(x=w+Tn,z=Tn);const S=null!==f&&f<60,A=null===m||null===v?{kind:"faded",segments:Ln($,x,k,z,En)}:{kind:"solid",d:In(En,$,S?$+60:x)},C=y>1?In(En,_-y,_):null,[E,T]=Hn(57,(_+w)/2),O=null===f?{kind:"run",minutes:b}:{kind:"window",minutes:f};return{trackPath:d,windowArc:A,dottedPath:C,runs:[Bn(_,w)],overlaps:[],ticks:c,sun:{x:h,y:u,minutes:o},moon:{x:p,y:g,minutes:r},drops:[{x:E,y:T,fromMinutes:_,toMinutes:w}],centre:O}}function jn(e){return(e%360+360)%360}const Fn=Math.PI/180;function Zn(e,t,s){const i=e*Fn,a=23.45*Math.sin(360*(284+function(e){const t=Date.UTC(e.getUTCFullYear(),0,1),s=Date.UTC(e.getUTCFullYear(),e.getUTCMonth(),e.getUTCDate());return Math.floor((s-t)/864e5)+1}(s))/365*Fn)*Fn,n=15*(s.getUTCHours()+s.getUTCMinutes()/60+s.getUTCSeconds()/3600-t/15-12)*Fn;return jn(Math.atan2(Math.sin(n),Math.cos(n)*Math.sin(i)-Math.tan(a)*Math.cos(i))/Fn+180)}function Wn(e,t,s){return Math.abs(e-t)>180?e>t?s>=e||s<=t:s<=e||s>=t:Math.min(e,t)<=s&&s<=Math.max(e,t)}const qn=9e5;function Gn(e,t,s,i,a){let n=i,o=a;for(;o-n>6e4;){const i=n+(o-n)/2,a=Zn(e,t,new Date(i));Wn(Zn(e,t,new Date(n)),a,s)?o=i:n=i}return new Date(n)}const Kn={hour12:!1,year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit"};function Vn(e,t){if(!e)return Yn(t);let s;try{s=new Intl.DateTimeFormat("en-US",Object.assign(Object.assign({},Kn),{timeZone:e})).formatToParts(t)}catch(e){return Yn(t)}const i=e=>{var t,i;return parseInt(null!==(i=null===(t=s.find(t=>t.type===e))||void 0===t?void 0:t.value)&&void 0!==i?i:"0",10)},a=i("hour")%24;return new Date(Date.UTC(i("year"),i("month")-1,i("day"),a,i("minute"),i("second")))}function Yn(e){return new Date(Date.UTC(e.getFullYear(),e.getMonth(),e.getDate(),e.getHours(),e.getMinutes(),e.getSeconds()))}function Xn(e,t,s,i,a){const n=Vn(i,a),o=new Date(Date.UTC(n.getUTCFullYear(),n.getUTCMonth(),n.getUTCDate())),r=function(e,t,s,i,a=1){const n=i.getTime(),o=n+864e5*a;let r=n,l=Zn(e,t,i);for(;r<o;){r+=qn;const i=Zn(e,t,new Date(r));if(Wn(l,i,s))return Gn(e,t,s,r-qn,r);l=i}return null}(e,t,jn(s),o);return null===r?null:function(e,t){let s=e.getTime();for(let i=0;i<2;i++){const i=Vn(t,new Date(s)).getTime()-s;s=e.getTime()-i}const i=new Date(s);return 60*i.getHours()+i.getMinutes()}(r,i)}const Jn=q`<circle cx="12" cy="12" r="4.4" />
  ${Array.from({length:8},(e,t)=>{const s=t*Math.PI/4,i=(12+6.6*Math.cos(s)).toFixed(1),a=(12+6.6*Math.sin(s)).toFixed(1),n=(12+9.2*Math.cos(s)).toFixed(1),o=(12+9.2*Math.sin(s)).toFixed(1);return q`<line x1="${i}" y1="${a}" x2="${n}" y2="${o}" />`})}`,Qn=q`<path d="M13.5,2.5A9.5,9.5 0 1,0 21.5,14 7.6,7.6 0 0,1 13.5,2.5Z" />`,eo=q`<path d="M12,2.6C12,2.6 18.6,9.4 18.6,13.7A6.6,6.6 0 0,1 5.4,13.7C5.4,9.4 12,2.6 12,2.6Z" />`;let to=class extends ce{constructor(){super(...arguments),this.recurrence="daily",this.nominalDemandSeconds=0}_sunTimes(){var e,t,s,i;const a=null===(t=null===(e=this.hass)||void 0===e?void 0:e.states)||void 0===t?void 0:t["sun.sun"],n=null===(s=null==a?void 0:a.attributes)||void 0===s?void 0:s.next_rising,o=null===(i=null==a?void 0:a.attributes)||void 0===i?void 0:i.next_setting,r=(e,t)=>{if(!e)return t;const s=new Date(e);return isNaN(s.getTime())?t:60*s.getHours()+s.getMinutes()};return{sunrise:r(n,360),sunset:r(o,1200)}}_azimuthResolver(){var e;const t=null===(e=this.hass)||void 0===e?void 0:e.config;if("number"!=typeof(null==t?void 0:t.latitude)||"number"!=typeof(null==t?void 0:t.longitude))return;const{latitude:s,longitude:i,time_zone:a}=t,n=new Date;return e=>Xn(s,i,e,a,n)}_renderRun(e,t){return e.wraps?q`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
=======
    `}disconnectedCallback(){super.disconnectedCallback(),this.debounceTimers.forEach(e=>{clearTimeout(e)}),this.debounceTimers.clear(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null),this.mappingCache.clear()}};t([me()],_n.prototype,"config",void 0),t([me({type:Array})],_n.prototype,"zones",void 0),t([me({type:Array})],_n.prototype,"mappings",void 0),t([me({type:Boolean})],_n.prototype,"isLoading",void 0),t([me({type:Boolean})],_n.prototype,"isSaving",void 0),t([fe("#mappingNameInput")],_n.prototype,"mappingNameInput",void 0),_n=t([ue("smart-irrigation-view-mappings")],_n);const bn="06:00",yn=90;function wn(e){switch(e){case ns:return{mode:e,time:bn};case os:case rs:return{mode:e,offset:0};case ls:return{mode:e,azimuth:yn};default:return{mode:as}}}function $n(e,t,s,i){const a=function(e){return e===as||e===ns||e===os||e===rs||e===ls}(e)?e:as,n=wn(a);return a===ns&&void 0!==t&&(n.time=t),a!==os&&a!==rs||void 0===s||(n.offset=s),a===ls&&void 0!==i&&(n.azimuth=i),n}function xn(e){var t,s,i;return{mode:e.mode,time:e.mode===ns?null!==(t=e.time)&&void 0!==t?t:bn:void 0,offset:e.mode===os||e.mode===rs?null!==(s=e.offset)&&void 0!==s?s:0:void 0,azimuth:e.mode===ls?null!==(i=e.azimuth)&&void 0!==i?i:yn:void 0}}function kn(e){return{start:$n(e.start_mode,e.start_time,e.start_offset,e.start_azimuth),finish:$n(e.finish_mode,e.finish_time,e.finish_offset,e.finish_azimuth),anchor:e.anchor===cs?cs:hs}}function zn(e,t){const s=e.start.mode!==as,i=e.finish.mode!==as;if(!s&&!i)return{start:"error",finish:"error",valid:!1};return function(e,t,s){if(!(null==s?void 0:s.start)&&!(null==s?void 0:s.finish))return t;const i=e.start.mode!==as,a=e.finish.mode!==as,n=i&&a?e.anchor:i?cs:hs,o=e=>e===n?"unreachable_no_run":"unreachable_ignored";return Object.assign(Object.assign({},t),{start:s.start?o(cs):t.start,finish:s.finish?o(hs):t.finish})}(e,s?i?e.anchor===hs?{start:"demand_floored",finish:"exact_deferred",valid:!0}:{start:"exact",finish:"demand_capped_deferred",valid:!0}:{start:"exact",finish:"demand_open",valid:!0}:{start:"demand_open",finish:"exact",valid:!0},t)}function Sn(e,t){const s=function(e,t){if("all"===e||!Array.isArray(e))return Ma("panels.schedules.summary.zones_all",t);return Ma("panels.schedules.summary.zones_some",t,"count",e.length)}(e.zones,t),i=function(e,t){switch(e.recurrence){case es:{const s=(e.days_of_week||[]).map(e=>Ma(`panels.schedules.days.${e}`,t)).join(", ");return Ma("panels.schedules.summary.recurrence_weekly",t,"days",s)}case ts:return Ma("panels.schedules.summary.recurrence_monthly",t,"day",e.day_of_month||1);case ss:{const s=e.interval_hours||24;return e.start_time?Ma("panels.schedules.summary.recurrence_interval_at",t,"hours",s,"time",e.start_time):Ma("panels.schedules.summary.recurrence_interval",t,"hours",s)}default:return Ma("panels.schedules.summary.recurrence_daily",t)}}(e,t);if(e.recurrence===ss){return{text:`${i}, ${Ma("panels.schedules.summary.watering",t,"zones",s)}.`,isError:!1}}const a=kn(e),n=a.start.mode!==as,o=a.finish.mode!==as;if(!n&&!o)return{text:Ma("panels.schedules.summary.invalid",t),isError:!0};const r=Ma("panels.schedules.summary.watering",t,"zones",s);let l;return l=n?o?a.anchor===hs?Ma("panels.schedules.summary.anchor_finish",t,"finish",An(a.finish,t),"start",An(a.start,t)):Ma("panels.schedules.summary.anchor_start",t,"start",An(a.start,t),"finish",An(a.finish,t)):Ma("panels.schedules.summary.start_only",t,"when",An(a.start,t)):Ma("panels.schedules.summary.finish_only",t,"when",An(a.finish,t)),{text:`${i}, ${r}, ${l}.`,isError:!1}}function An(e,t){var s,i,a;switch(e.mode){case ns:return null!==(s=e.time)&&void 0!==s?s:"";case os:case rs:{const s=Ma(`panels.schedules.summary.${e.mode}`,t),a=null!==(i=e.offset)&&void 0!==i?i:0;if(0===a)return s;return Ma(a<0?"panels.schedules.summary.offset_before":"panels.schedules.summary.offset_after",t,"minutes",Math.abs(a),"event",s)}case ls:return Ma("panels.schedules.summary.at_azimuth",t,"degrees",null!==(a=e.azimuth)&&void 0!==a?a:yn);default:return""}}function Cn(e){return(e%360+360)%360}const En=Math.PI/180;function Tn(e,t,s){const i=e*En,a=23.45*Math.sin(360*(284+function(e){const t=Date.UTC(e.getUTCFullYear(),0,1),s=Date.UTC(e.getUTCFullYear(),e.getUTCMonth(),e.getUTCDate());return Math.floor((s-t)/864e5)+1}(s))/365*En)*En,n=15*(s.getUTCHours()+s.getUTCMinutes()/60+s.getUTCSeconds()/3600-t/15-12)*En;return Cn(Math.atan2(Math.sin(n),Math.cos(n)*Math.sin(i)-Math.tan(a)*Math.cos(i))/En+180)}function On(e,t,s){return Math.abs(e-t)>180?e>t?s>=e||s<=t:s<=e||s>=t:Math.min(e,t)<=s&&s<=Math.max(e,t)}const Dn=9e5;function Mn(e,t,s,i,a){let n=i,o=a;for(;o-n>6e4;){const i=n+(o-n)/2,a=Tn(e,t,new Date(i));On(Tn(e,t,new Date(n)),a,s)?o=i:n=i}return new Date(n)}const Hn={hour12:!1,year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit"};function In(e,t){if(!e)return Nn(t);let s;try{s=new Intl.DateTimeFormat("en-US",Object.assign(Object.assign({},Hn),{timeZone:e})).formatToParts(t)}catch(e){return Nn(t)}const i=e=>{var t,i;return parseInt(null!==(i=null===(t=s.find(t=>t.type===e))||void 0===t?void 0:t.value)&&void 0!==i?i:"0",10)},a=i("hour")%24;return new Date(Date.UTC(i("year"),i("month")-1,i("day"),a,i("minute"),i("second")))}function Nn(e){return new Date(Date.UTC(e.getFullYear(),e.getMonth(),e.getDate(),e.getHours(),e.getMinutes(),e.getSeconds()))}function Ln(e,t){if("number"!=typeof(null==e?void 0:e.latitude)||"number"!=typeof(null==e?void 0:e.longitude))return;const{latitude:s,longitude:i,time_zone:a}=e;return e=>function(e,t,s,i,a){const n=In(i,a),o=new Date(Date.UTC(n.getUTCFullYear(),n.getUTCMonth(),n.getUTCDate())),r=function(e,t,s,i,a=1){const n=i.getTime(),o=n+864e5*a;let r=n,l=Tn(e,t,i);for(;r<o;){r+=Dn;const i=Tn(e,t,new Date(r));if(On(l,i,s))return Mn(e,t,s,r-Dn,r);l=i}return null}(e,t,Cn(s),o);return null===r?null:function(e,t){let s=e.getTime();for(let i=0;i<2;i++){const i=In(t,new Date(s)).getTime()-s;s=e.getTime()-i}const i=new Date(s);return 60*i.getHours()+i.getMinutes()}(r,i)}(s,i,e,a,t)}const Pn=1440,Rn=44,Bn=260;function Un(e){return(e%Pn+Pn)%Pn}function jn(e){const t=Math.round(Un(e)),s=Math.floor(t/60),i=t%60;return`${String(s).padStart(2,"0")}:${String(i).padStart(2,"0")}`}function Fn(e){const t=Math.floor(e/60),s=Math.round(e%60);return t?`${t}h ${s}m`:`${s}m`}function Zn(e,t){const s=t/Pn*2*Math.PI+Math.PI/2;return[66+e*Math.cos(s),66+e*Math.sin(s)]}function Wn(e,t,s){const i=s-t>=Pn?t+Pn-.5:s,[a,n]=Zn(e,t),[o,r]=Zn(e,i),l=i-t>720?1:0;return`M ${a.toFixed(2)} ${n.toFixed(2)} A ${e} ${e} 0 ${l} 1 ${o.toFixed(2)} ${r.toFixed(2)}`}function qn(e,t,s,i,a){const n=2*Math.PI*e/Pn,o=[[0,s]];for(let e=0;e<=10;e++){const t=Math.PI/2+e/10*(Math.PI/2);o.push([i*Math.cos(t),s-i+i*Math.sin(t)])}for(let e=0;e<=10;e++){const t=Math.PI+e/10*(Math.PI/2);o.push([i*Math.cos(t),i*Math.sin(t)-3.2])}return o.push([0,-s]),o.map(([s,i],o)=>{const[r,l]=Zn(e+i,(e=>t-a*e/n)(s));return`${o?"L":"M"} ${r.toFixed(2)} ${l.toFixed(2)}`}).join(" ")+" Z"}function Gn(e,t,s,i,a){const n=(t-e)/48,o=[];for(let r=0;r<48;r++){const l=e+r*n,d=l+n/2;let c=1;s>0&&(c=Math.min(c,(d-e)/s)),i>0&&(c=Math.min(c,(t-d)/i)),c=Math.max(0,Math.min(1,c)),o.push({d:Wn(a,l,l+1.25*n),opacity:c})}return o}function Kn(e){const[t,s]=e.split(":").map(e=>parseInt(e,10));return 60*(t||0)+(s||0)}function Vn(e,t,s,i){var a,n,o,r;switch(e.mode){case ns:return Un(Kn(null!==(a=e.time)&&void 0!==a?a:"06:00"));case os:return Un(t+(null!==(n=e.offset)&&void 0!==n?n:0));case rs:return Un(s+(null!==(o=e.offset)&&void 0!==o?o:0));case ls:{if(!i)return null;const t=i(null!==(r=e.azimuth)&&void 0!==r?r:yn);return null===t?null:Un(t)}default:return null}}function Yn(e,t){return{wraps:!1,arc:Wn(Rn,e,t),capStart:qn(Rn,e,5,1.8,-1),capEnd:qn(Rn,t,5,1.8,1)}}function Xn(e){const{rows:t,recurrence:s,intervalHours:i,intervalStartTime:a,nominalDemandMinutes:n,sunriseMinutes:o,sunsetMinutes:r,azimuthResolver:l}=e,d=Wn(Rn,0,Pn),c=[0,360,720,1080].map(e=>{const[t,s]=Zn(38,e),[i,a]=Zn(50,e);return{x1:t,y1:s,x2:i,y2:a}}),[h,u]=Zn(57,o),[p,g]=Zn(57,r);if(s===ss){const{runs:e,overlaps:t,wrapAt:s}=function(e,t,s){const i=60*Math.max(1,Number(t)||24),a=s?Kn(s):0,n=[];for(let t=a;t<a+Pn&&n.length<24;t+=i)n.push([t,t+e]);const o=[];for(let e=0;e+1<n.length;e++)n[e][1]>n[e+1][0]&&o.push([n[e+1][0],Math.min(n[e][1],n[e+1][1])]);return{runs:n,overlaps:o,wrapAt:a+Pn}}(n,i,a),l=e.map(([e,t])=>{if(t<=s)return Yn(e,t);const i=s-8,a=i-e,n=Math.min(a,120);return{wraps:!0,capStart:qn(Rn,e,5,1.8,-1),fade:Gn(e,i,0,n,Rn)}});return{trackPath:d,windowArc:null,dottedPath:null,runs:l,overlaps:t.map(([e,t])=>({d:Wn(Rn,e,t),fromMinutes:e,toMinutes:t})),ticks:c,sun:{x:h,y:u,minutes:o},moon:{x:p,y:g,minutes:r},drops:e.map(([e,t])=>{const[s,i]=Zn(57,(e+t)/2);return{x:s,y:i,fromMinutes:e,toMinutes:t}}),centre:{kind:"interval",perDay:e.length,intervalHours:Math.max(1,Number(i)||24)}}}const m=Vn(t.start,o,r,l),v=Vn(t.finish,o,r,l);if(null===m&&null===v)return{trackPath:d,windowArc:null,dottedPath:null,runs:[],overlaps:[],ticks:c,sun:{x:h,y:u,minutes:o},moon:{x:p,y:g,minutes:r},drops:[],centre:{kind:"invalid"}};const f=null!==m&&null!==v?(()=>{const e=Un(v-m);return 0===e?Pn:e})():null;let _,b,y=0;if(null!==m&&null!==v){const e=f;b=Math.min(n,e),y=Math.max(0,n-e),_=t.anchor===hs?m+Un(v-m)-b:m}else null!==m?(_=m,b=n):(b=n,_=v-b);const w=_+b;let $=null!=m?m:_,x=null!=v?v:w,k=0,z=0;null===m&&($=_-Bn,k=Bn),null===v&&(x=w+Bn,z=Bn);const S=null!==f&&f<60,A=null===m||null===v?{kind:"faded",segments:Gn($,x,k,z,Rn)}:{kind:"solid",d:Wn(Rn,$,S?$+60:x)},C=y>1?Wn(Rn,_-y,_):null,[E,T]=Zn(57,(_+w)/2),O=null===f?{kind:"run",minutes:b}:{kind:"window",minutes:f};return{trackPath:d,windowArc:A,dottedPath:C,runs:[Yn(_,w)],overlaps:[],ticks:c,sun:{x:h,y:u,minutes:o},moon:{x:p,y:g,minutes:r},drops:[{x:E,y:T,fromMinutes:_,toMinutes:w}],centre:O}}const Jn=q`<circle cx="12" cy="12" r="4.4" />
  ${Array.from({length:8},(e,t)=>{const s=t*Math.PI/4,i=(12+6.6*Math.cos(s)).toFixed(1),a=(12+6.6*Math.sin(s)).toFixed(1),n=(12+9.2*Math.cos(s)).toFixed(1),o=(12+9.2*Math.sin(s)).toFixed(1);return q`<line x1="${i}" y1="${a}" x2="${n}" y2="${o}" />`})}`,Qn=q`<path d="M13.5,2.5A9.5,9.5 0 1,0 21.5,14 7.6,7.6 0 0,1 13.5,2.5Z" />`,eo=q`<path d="M12,2.6C12,2.6 18.6,9.4 18.6,13.7A6.6,6.6 0 0,1 5.4,13.7C5.4,9.4 12,2.6 12,2.6Z" />`;let to=class extends ce{constructor(){super(...arguments),this.recurrence="daily",this.nominalDemandSeconds=0}_sunTimes(){var e,t,s,i;const a=null===(t=null===(e=this.hass)||void 0===e?void 0:e.states)||void 0===t?void 0:t["sun.sun"],n=null===(s=null==a?void 0:a.attributes)||void 0===s?void 0:s.next_rising,o=null===(i=null==a?void 0:a.attributes)||void 0===i?void 0:i.next_setting,r=(e,t)=>{if(!e)return t;const s=new Date(e);return isNaN(s.getTime())?t:60*s.getHours()+s.getMinutes()};return{sunrise:r(n,360),sunset:r(o,1200)}}_azimuthResolver(){var e;return Ln(null===(e=this.hass)||void 0===e?void 0:e.config,new Date)}_renderRun(e,t){return e.wraps?q`
>>>>>>> f4290c2 (feat(schedules): warn when a solar-azimuth bearing the sun never reaches is set)
      <path d="${e.capStart}" class="cap-run" />
      ${e.fade.map(e=>q`
          <path
            d="${e.d}"
            class="d-run"
            style="stroke-linecap:butt"
            stroke-opacity="${e.opacity.toFixed(2)}"
          />
        `)}
    `:q`
        <path d="${e.arc}" class="d-run" style="stroke-linecap:butt" />
        <path d="${e.capStart}" class="cap-run" />
        <path d="${e.capEnd}" class="cap-run" />
<<<<<<< HEAD
<<<<<<< HEAD
      `}_centreText(e,t){var i,s;const a=e.centre;switch(a.kind){case"invalid":return{val:"—",lbl:""};case"interval":return{val:Oa("panels.schedules.dial.every_hours",t,"{hours}",a.intervalHours),lbl:Oa("panels.schedules.dial.per_day",t,"{count}",a.perDay)};case"run":return{val:En(null!==(i=a.minutes)&&void 0!==i?i:0),lbl:Oa("panels.schedules.dial.run_label",t)};default:return{val:En(null!==(s=a.minutes)&&void 0!==s?s:0),lbl:Oa("panels.schedules.dial.window_label",t)}}}render(){if(!this.hass||!this.rows)return W``;const e=this.hass.language,{sunrise:t,sunset:i}=this._sunTimes(),s=Nn({rows:this.rows,recurrence:this.recurrence,intervalHours:this.intervalHours,intervalStartTime:this.intervalStartTime,nominalDemandMinutes:this.nominalDemandSeconds/60,sunriseMinutes:t,sunsetMinutes:i}),{val:a,lbl:n}=this._centreText(s,e);return W`
=======
      `}_centreText(e,t){var s,i;const a=e.centre;switch(a.kind){case"invalid":return{val:"—",lbl:""};case"interval":return{val:Ma("panels.schedules.dial.every_hours",t,"{hours}",a.intervalHours),lbl:Ma("panels.schedules.dial.per_day",t,"{count}",a.perDay)};case"run":return{val:Mn(null!==(s=a.minutes)&&void 0!==s?s:0),lbl:Ma("panels.schedules.dial.run_label",t)};default:return{val:Mn(null!==(i=a.minutes)&&void 0!==i?i:0),lbl:Ma("panels.schedules.dial.window_label",t)}}}render(){if(!this.hass||!this.rows)return W``;const e=this.hass.language,{sunrise:t,sunset:s}=this._sunTimes(),i=Un({rows:this.rows,recurrence:this.recurrence,intervalHours:this.intervalHours,intervalStartTime:this.intervalStartTime,nominalDemandMinutes:this.nominalDemandSeconds/60,sunriseMinutes:t,sunsetMinutes:s,azimuthResolver:this._azimuthResolver()}),{val:a,lbl:n}=this._centreText(i,e);return W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
=======
      `}_centreText(e,t){var s,i;const a=e.centre;switch(a.kind){case"invalid":return{val:"—",lbl:""};case"interval":return{val:Ma("panels.schedules.dial.every_hours",t,"{hours}",a.intervalHours),lbl:Ma("panels.schedules.dial.per_day",t,"{count}",a.perDay)};case"run":return{val:Fn(null!==(s=a.minutes)&&void 0!==s?s:0),lbl:Ma("panels.schedules.dial.run_label",t)};default:return{val:Fn(null!==(i=a.minutes)&&void 0!==i?i:0),lbl:Ma("panels.schedules.dial.window_label",t)}}}render(){if(!this.hass||!this.rows)return W``;const e=this.hass.language,{sunrise:t,sunset:s}=this._sunTimes(),i=Xn({rows:this.rows,recurrence:this.recurrence,intervalHours:this.intervalHours,intervalStartTime:this.intervalStartTime,nominalDemandMinutes:this.nominalDemandSeconds/60,sunriseMinutes:t,sunsetMinutes:s,azimuthResolver:this._azimuthResolver()}),{val:a,lbl:n}=this._centreText(i,e);return W`
>>>>>>> f4290c2 (feat(schedules): warn when a solar-azimuth bearing the sun never reaches is set)
      <div class="viz-dial">
        <div class="d-wrap">
          <svg
            viewBox="0 0 132 132"
            role="img"
<<<<<<< HEAD
            aria-label="${Oa("panels.schedules.dial.aria_label",e)}"
=======
            aria-label="${Ma("panels.schedules.dial.aria_label",e)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          >
            <path d="${s.trackPath}" class="d-track" />
            ${s.windowArc?"solid"===s.windowArc.kind?q`<path d="${s.windowArc.d}" class="d-win" />`:s.windowArc.segments.map(e=>q`
                      <path
                        d="${e.d}"
                        class="d-win"
                        style="stroke-linecap:butt"
                        stroke-opacity="${e.opacity.toFixed(2)}"
                      />
                    `):""}
            ${s.dottedPath?q`<path d="${s.dottedPath}" class="d-dotted" />`:""}
            ${s.runs.map(t=>this._renderRun(t,e))}
            ${s.overlaps.map(t=>q`
                <path d="${t.d}" class="d-overlap">
                  <title>
<<<<<<< HEAD
<<<<<<< HEAD
                    ${Oa("panels.schedules.dial.collision",e,"{from}",An(t.fromMinutes),"{to}",An(t.toMinutes))}
=======
                    ${Ma("panels.schedules.dial.collision",e,"{from}",Dn(t.fromMinutes),"{to}",Dn(t.toMinutes))}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
=======
                    ${Ma("panels.schedules.dial.collision",e,"{from}",jn(t.fromMinutes),"{to}",jn(t.toMinutes))}
>>>>>>> f4290c2 (feat(schedules): warn when a solar-azimuth bearing the sun never reaches is set)
                  </title>
                </path>
              `)}
            ${s.ticks.map(e=>q`
                <line
                  x1="${e.x1.toFixed(1)}"
                  y1="${e.y1.toFixed(1)}"
                  x2="${e.x2.toFixed(1)}"
                  y2="${e.y2.toFixed(1)}"
                  class="d-tick"
                />
              `)}
            <g
              class="g-sun"
              transform="translate(${(s.sun.x-5.04).toFixed(1)},${(s.sun.y-5.04).toFixed(1)}) scale(0.42)"
            >
              <title>
<<<<<<< HEAD
<<<<<<< HEAD
                ${Oa("panels.schedules.dial.sunrise",e,"{time}",An(s.sun.minutes))}
              </title>
              ${Pn}
=======
                ${Ma("panels.schedules.dial.sunrise",e,"{time}",Dn(i.sun.minutes))}
=======
                ${Ma("panels.schedules.dial.sunrise",e,"{time}",jn(i.sun.minutes))}
>>>>>>> f4290c2 (feat(schedules): warn when a solar-azimuth bearing the sun never reaches is set)
              </title>
              ${Jn}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </g>
            <g
              class="g-moon"
              transform="translate(${(s.moon.x-5.04).toFixed(1)},${(s.moon.y-5.04).toFixed(1)}) scale(0.42)"
            >
              <title>
<<<<<<< HEAD
<<<<<<< HEAD
                ${Oa("panels.schedules.dial.sunset",e,"{time}",An(s.moon.minutes))}
              </title>
              ${Ln}
=======
                ${Ma("panels.schedules.dial.sunset",e,"{time}",Dn(i.moon.minutes))}
=======
                ${Ma("panels.schedules.dial.sunset",e,"{time}",jn(i.moon.minutes))}
>>>>>>> f4290c2 (feat(schedules): warn when a solar-azimuth bearing the sun never reaches is set)
              </title>
              ${Qn}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </g>
            ${s.drops.map(t=>q`
                <g
                  class="g-drop"
                  transform="translate(${(t.x-12*.38).toFixed(1)},${(t.y-12*.38).toFixed(1)}) scale(0.38)"
                >
                  <title>
<<<<<<< HEAD
<<<<<<< HEAD
                    ${Oa("panels.schedules.dial.run",e,"{from}",An(t.fromMinutes),"{to}",An(t.toMinutes))}
                  </title>
                  ${Rn}
=======
                    ${Ma("panels.schedules.dial.run",e,"{from}",Dn(t.fromMinutes),"{to}",Dn(t.toMinutes))}
=======
                    ${Ma("panels.schedules.dial.run",e,"{from}",jn(t.fromMinutes),"{to}",jn(t.toMinutes))}
>>>>>>> f4290c2 (feat(schedules): warn when a solar-azimuth bearing the sun never reaches is set)
                  </title>
                  ${eo}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </g>
              `)}
          </svg>
          <div class="d-centre">
            <div class="d-val">${a}</div>
            <div class="d-lbl">${n}</div>
          </div>
        </div>
      </div>
    `}static get styles(){return r`
      /* Ring colors are mixed against the card background rather than kept
         as a fixed alpha over an assumed background: an alpha-based color
         resolves to a different actual color per theme (light vs dark card
         background), which was a real bug in the prototype's first pass. */
      .viz-dial {
        text-align: center;
        --dial-win: color-mix(
          in srgb,
          var(--primary-color) 34%,
          var(--card-background-color)
        );
        --dial-track: color-mix(
          in srgb,
          var(--primary-text-color) 9%,
          var(--card-background-color)
        );
      }
      .viz-dial .d-wrap {
        position: relative;
        display: inline-block;
        width: 100%;
        max-width: 156px;
      }
      .viz-dial svg {
        width: 100%;
        height: auto;
        display: block;
      }
      .viz-dial .d-track {
        fill: none;
        stroke: var(--dial-track);
        stroke-width: 10;
      }
      .viz-dial .d-win {
        fill: none;
        stroke: var(--dial-win);
        stroke-width: 10;
      }
      .viz-dial .d-dotted {
        fill: none;
        stroke: var(--accent-color);
        stroke-width: 3.5;
        opacity: 0.7;
        stroke-dasharray: 0.1 5;
        stroke-linecap: round;
      }
      .viz-dial .d-run {
        fill: none;
        stroke: var(--primary-color);
        stroke-width: 10;
      }
      .viz-dial .d-overlap {
        fill: none;
        stroke: var(--accent-color);
        stroke-width: 10;
      }
      .viz-dial .cap-run {
        fill: var(--primary-color);
        stroke: none;
      }
      .viz-dial .d-tick {
        stroke: color-mix(in srgb, var(--primary-text-color) 22%, transparent);
        stroke-width: 1;
      }
      .viz-dial .g-sun {
        fill: none;
        stroke: #f6b21b;
        stroke-width: 1.7;
        stroke-linecap: round;
      }
      .viz-dial .g-sun circle {
        fill: #f6b21b;
      }
      .viz-dial .g-moon {
        fill: #7e8cc4;
        stroke: none;
      }
      .viz-dial .g-drop {
        fill: var(--primary-color);
        stroke: none;
      }
      .viz-dial g[class^="g-"] {
        cursor: help;
      }
      .viz-dial .d-centre {
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        pointer-events: none;
      }
      .viz-dial .d-val {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 15px;
        font-weight: 500;
        font-variant-numeric: tabular-nums;
        color: var(--primary-text-color);
      }
      .viz-dial .d-lbl {
        font-size: 9.5px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--secondary-text-color);
        margin-top: 1px;
      }
<<<<<<< HEAD
    `}};t([me({attribute:!1})],Bn.prototype,"hass",void 0),t([me({attribute:!1})],Bn.prototype,"rows",void 0),t([me({attribute:!1})],Bn.prototype,"recurrence",void 0),t([me({attribute:!1})],Bn.prototype,"intervalHours",void 0),t([me({attribute:!1})],Bn.prototype,"intervalStartTime",void 0),t([me({attribute:!1})],Bn.prototype,"nominalDemandSeconds",void 0),Bn=t([ue("si-run-window-dial")],Bn);const Un=["monday","tuesday","wednesday","thursday","friday","saturday","sunday"];function jn(){return{name:"",recurrence:"daily",enabled:!0,start_mode:si,start_time:"06:00",finish_mode:ii,action:"irrigate",zones:"all"}}function Fn(e,t){return Oa(`panels.schedules.types.${e}`,t)||e}let Zn=class extends ce{constructor(){super(...arguments),this.zones=[],this.heading="",this._save=()=>{this.dispatchEvent(new CustomEvent("save",{detail:{value:this.schedule},bubbles:!0,composed:!0}))},this._cancel=()=>{this.dispatchEvent(new CustomEvent("cancel",{bubbles:!0,composed:!0}))}}_emitChanged(e){this.dispatchEvent(new CustomEvent("schedule-changed",{detail:{value:Object.assign(Object.assign({},this.schedule),e)},bubbles:!0,composed:!0}))}_renderZonePicker(){const e="all"===this.schedule.zones||!Array.isArray(this.schedule.zones),t=e?[]:this.schedule.zones.map(String);return W`
=======
    `}};t([me({attribute:!1})],to.prototype,"hass",void 0),t([me({attribute:!1})],to.prototype,"rows",void 0),t([me({attribute:!1})],to.prototype,"recurrence",void 0),t([me({attribute:!1})],to.prototype,"intervalHours",void 0),t([me({attribute:!1})],to.prototype,"intervalStartTime",void 0),t([me({attribute:!1})],to.prototype,"nominalDemandSeconds",void 0),to=t([ue("si-run-window-dial")],to);const so=["monday","tuesday","wednesday","thursday","friday","saturday","sunday"];function io(){return{name:"",recurrence:"daily",enabled:!0,start_mode:ns,start_time:"06:00",finish_mode:as,action:"irrigate",zones:"all"}}function ao(e,t){return Ma(`panels.schedules.types.${e}`,t)||e}let no=class extends ce{constructor(){super(...arguments),this.zones=[],this.heading="",this._save=()=>{this.dispatchEvent(new CustomEvent("save",{detail:{value:this.schedule},bubbles:!0,composed:!0}))},this._cancel=()=>{this.dispatchEvent(new CustomEvent("cancel",{bubbles:!0,composed:!0}))}}_emitChanged(e){this.dispatchEvent(new CustomEvent("schedule-changed",{detail:{value:Object.assign(Object.assign({},this.schedule),e)},bubbles:!0,composed:!0}))}_renderZonePicker(){const e="all"===this.schedule.zones||!Array.isArray(this.schedule.zones),t=e?[]:this.schedule.zones.map(String);return W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      <div class="field">
        <label
          >${Oa("panels.schedules.fields.zones",this.hass.language)}</label
        >
        <div class="switch-container">
          <input
            type="radio"
            id="zones_all"
            name="zones_mode"
            ?checked="${e}"
            @change=${()=>this._emitChanged({zones:"all"})}
          />
          <label for="zones_all"
<<<<<<< HEAD
            >${Oa("panels.schedules.zones_all",this.hass.language)}</label
=======
            >${Ma("panels.schedules.zones_all",this.hass.language)}</label
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          >
          <input
            type="radio"
            id="zones_specific"
            name="zones_mode"
            ?checked="${!e}"
            @change=${()=>this._emitChanged({zones:[]})}
          />
          <label for="zones_specific"
<<<<<<< HEAD
            >${Oa("panels.schedules.zones_specific",this.hass.language)}</label
=======
            >${Ma("panels.schedules.zones_specific",this.hass.language)}</label
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          >
        </div>
        ${e?"":W`
              <div class="zone-checkboxes">
                ${this.zones.map(e=>W`
                    <label class="zone-check">
                      <input
                        type="checkbox"
                        ?checked="${t.includes(String(e.id))}"
                        @change=${t=>{const i=t.target.checked,s=String(e.id),a=Array.isArray(this.schedule.zones)?[...this.schedule.zones]:[],n=i?[...a,s]:a.filter(e=>e!==s);this._emitChanged({zones:n})}}
                      />
                      ${e.name}
                    </label>
                  `)}
              </div>
            `}
      </div>
    `}_renderRecurrenceFields(){const e=this.schedule,t=this.hass.language;switch(e.recurrence){case"weekly":return W`
          <div class="field">
            <label
<<<<<<< HEAD
              >${Oa("panels.schedules.fields.days_of_week",t)}</label
            >
            <div class="day-checkboxes">
              ${Un.map(i=>W`
=======
              >${Ma("panels.schedules.fields.days_of_week",t)}</label
            >
            <div class="day-checkboxes">
              ${so.map(s=>W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  <label class="day-check">
                    <input
                      type="checkbox"
                      ?checked="${(e.days_of_week||[]).includes(i)}"
                      @change=${t=>{const s=t.target.checked,a=e.days_of_week||[],n=s?[...a,i]:a.filter(e=>e!==i);this._emitChanged({days_of_week:n})}}
                    />
<<<<<<< HEAD
                    ${Oa(`panels.schedules.days.${i}`,t)}
=======
                    ${Ma(`panels.schedules.days.${s}`,t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </label>
                `)}
            </div>
          </div>
        `;case"monthly":return W`
          <div class="field">
            <label
<<<<<<< HEAD
              >${Oa("panels.schedules.fields.day_of_month",t)}</label
=======
              >${Ma("panels.schedules.fields.day_of_month",t)}</label
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            >
            <input
              type="number"
              min="1"
              max="31"
              .value="${String(e.day_of_month||1)}"
              @input=${e=>this._emitChanged({day_of_month:parseInt(e.target.value)})}
            />
          </div>
        `;case"interval":return W`
          <div class="field">
            <label
<<<<<<< HEAD
              >${Oa("panels.schedules.fields.interval_hours",t)}</label
=======
              >${Ma("panels.schedules.fields.interval_hours",t)}</label
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            >
            <div class="input-suffix-row">
              <input
                type="number"
                min="1"
                .value="${String(e.interval_hours||24)}"
                @input=${e=>this._emitChanged({interval_hours:parseInt(e.target.value)})}
              />
              <span class="suffix"
<<<<<<< HEAD
                >${Oa("panels.schedules.hours",t)}</span
=======
                >${Ma("panels.schedules.hours",t)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              >
            </div>
          </div>
          <div class="field">
            <label
<<<<<<< HEAD
              >${Oa("panels.schedules.fields.start_time",t)}</label
=======
              >${Ma("panels.schedules.fields.start_time",t)}</label
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            >
            <input
              type="time"
              .value="${e.start_time||""}"
              @change=${e=>this._emitChanged({start_time:e.target.value||void 0})}
            />
          </div>
        `;default:return W``}}_renderRowStepper(e,t){var i,s,a;const n=this.hass.language;switch(e.mode){case si:return W`
          <input
            type="time"
            .value="${null!==(i=e.time)&&void 0!==i?i:"06:00"}"
            @change=${i=>t(Object.assign(Object.assign({},e),{time:i.target.value}))}
          />
        `;case ai:case ni:return W`
          <span class="row-inline"
<<<<<<< HEAD
            >${Oa("panels.schedules.fields.offset_by",n)}</span
=======
            >${Ma("panels.schedules.fields.offset_by",n)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          >
          <input
            type="number"
            step="1"
            .value="${String(null!==(s=e.offset)&&void 0!==s?s:0)}"
            @input=${i=>{const s=parseInt(i.target.value);t(Object.assign(Object.assign({},e),{offset:isNaN(s)?0:s}))}}
          />
          <span class="row-inline"
<<<<<<< HEAD
            >${Oa("panels.schedules.minutes",n)}</span
=======
            >${Ma("panels.schedules.minutes",n)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          >
        `;case oi:return W`
          <input
            type="number"
            min="0"
            max="359"
            step="1"
<<<<<<< HEAD
            .value="${String(null!==(a=e.azimuth)&&void 0!==a?a:90)}"
            @input=${i=>{var s;const a=parseInt(i.target.value);t(Object.assign(Object.assign({},e),{azimuth:isNaN(a)?null!==(s=e.azimuth)&&void 0!==s?s:90:a}))}}
=======
            .value="${String(null!==(a=e.azimuth)&&void 0!==a?a:yn)}"
            @input=${s=>{var i;const a=parseInt(s.target.value);t(Object.assign(Object.assign({},e),{azimuth:isNaN(a)?null!==(i=e.azimuth)&&void 0!==i?i:yn:a}))}}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          />
          <span class="row-inline">°</span>
        `;default:return W``}}_renderWindowRow(e,t,i,s){const a=this.hass.language;return W`
      <div class="window-row">
<<<<<<< HEAD
        <label>${Oa(`panels.schedules.fields.${e}_mode`,a)}</label>
        <select
          @change=${e=>s(_n(e.target.value))}
=======
        <label>${Ma(`panels.schedules.fields.${e}_mode`,a)}</label>
        <select
          @change=${e=>i(wn(e.target.value))}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
          ${ri.map(e=>W`
              <option value="${e}" ?selected="${t.mode===e}">
<<<<<<< HEAD
                ${Oa(`panels.schedules.bound_mode.${e}`,a)}
=======
                ${Ma(`panels.schedules.bound_mode.${e}`,a)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </option>
            `)}
        </select>
        ${this._renderRowStepper(t,s)}
      </div>
<<<<<<< HEAD
      <div class="window-row-help ${"error"===i?"is-error":""}">
=======
      <div
        class="window-row-help ${"error"===s?"is-error":(n=s,"unreachable_no_run"===n||"unreachable_ignored"===n?"is-warning":"")}"
      >
>>>>>>> f4290c2 (feat(schedules): warn when a solar-azimuth bearing the sun never reaches is set)
        <span class="help-arrow" aria-hidden="true">↳</span>
        <span class="help-text"
<<<<<<< HEAD
          >${Oa(`panels.schedules.help.${i}`,a)}</span
=======
          >${Ma(`panels.schedules.help.${s}`,a)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        >
      </div>
<<<<<<< HEAD
    `}_renderAnchorRow(e,t){const i=this.hass.language;return W`
=======
    `;var n}_renderAnchorRow(e,t){const s=this.hass.language;return W`
>>>>>>> f4290c2 (feat(schedules): warn when a solar-azimuth bearing the sun never reaches is set)
      <div class="window-row">
<<<<<<< HEAD
        <label>${Oa("panels.schedules.fields.anchor",i)}</label>
=======
        <label>${Ma("panels.schedules.fields.anchor",s)}</label>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        <select
          @change=${i=>t(Object.assign(Object.assign({},e),{anchor:i.target.value}))}
        >
          ${[li,di].map(t=>W`
              <option value="${t}" ?selected="${e.anchor===t}">
<<<<<<< HEAD
                ${Oa(`panels.schedules.anchor.${t}`,i)}
=======
                ${Ma(`panels.schedules.anchor.${t}`,s)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </option>
            `)}
        </select>
      </div>
<<<<<<< HEAD
<<<<<<< HEAD
    `}_renderWindowRows(){const e=this.schedule;if(e.recurrence===ei)return W``;const t=wn(e),i=$n(t),s=e=>this._emitChanged(function(e){const t=yn(e.start),i=yn(e.finish);return{start_mode:t.mode,start_time:t.time,start_offset:t.offset,start_azimuth:t.azimuth,finish_mode:i.mode,finish_time:i.time,finish_offset:i.offset,finish_azimuth:i.azimuth,anchor:e.anchor}}(e)),a=t.start.mode!==ii&&t.finish.mode!==ii;return W`
      ${this._renderWindowRow("start",t.start,i.start,e=>s(Object.assign(Object.assign({},t),{start:e})))}
      ${this._renderWindowRow("finish",t.finish,i.finish,e=>s(Object.assign(Object.assign({},t),{finish:e})))}
      ${a?this._renderAnchorRow(t,s):""}
    `}_canSave(){const e=this.schedule;return e.recurrence===ei||$n(wn(e)).valid}render(){var e;if(!this.hass||!this.schedule)return W``;const t=this.schedule;return W`
      <ha-dialog open heading="${this.heading}" @closed=${this._cancel}>
=======
    `}_renderWindowRows(){const e=this.schedule;if(e.recurrence===ss)return W``;const t=kn(e),s=zn(t),i=e=>this._emitChanged(function(e){const t=xn(e.start),s=xn(e.finish);return{start_mode:t.mode,start_time:t.time,start_offset:t.offset,start_azimuth:t.azimuth,finish_mode:s.mode,finish_time:s.time,finish_offset:s.offset,finish_azimuth:s.azimuth,anchor:e.anchor}}(e)),a=t.start.mode!==as&&t.finish.mode!==as;return W`
=======
    `}_unresolvableEnds(e){var t;const s=Ln(null===(t=this.hass)||void 0===t?void 0:t.config,new Date);if(!s)return{};const i=e=>{var t;return e.mode===ls&&null===s(null!==(t=e.azimuth)&&void 0!==t?t:yn)};return{start:i(e.start),finish:i(e.finish)}}_renderWindowRows(){const e=this.schedule;if(e.recurrence===ss)return W``;const t=kn(e),s=zn(t,this._unresolvableEnds(t)),i=e=>this._emitChanged(function(e){const t=xn(e.start),s=xn(e.finish);return{start_mode:t.mode,start_time:t.time,start_offset:t.offset,start_azimuth:t.azimuth,finish_mode:s.mode,finish_time:s.time,finish_offset:s.offset,finish_azimuth:s.azimuth,anchor:e.anchor}}(e)),a=t.start.mode!==as&&t.finish.mode!==as;return W`
>>>>>>> f4290c2 (feat(schedules): warn when a solar-azimuth bearing the sun never reaches is set)
      ${this._renderWindowRow("start",t.start,s.start,e=>i(Object.assign(Object.assign({},t),{start:e})))}
      ${this._renderWindowRow("finish",t.finish,s.finish,e=>i(Object.assign(Object.assign({},t),{finish:e})))}
      ${a?this._renderAnchorRow(t,i):""}
    `}_canSave(){const e=this.schedule;return e.recurrence===ss||zn(kn(e)).valid}_renderSection(e,t){return W`
      <div class="sect-card">
        <h4>
          ${Ma(`panels.schedules.sections.${e}`,this.hass.language)}
        </h4>
        ${t}
      </div>
    `}_renderSummary(){const e=Sn(this.schedule,this.hass.language);return W`
      <div class="summary ${e.isError?"is-error":""}">
        ${e.text}
      </div>
    `}_renderSeasonSection(){const e=this.schedule,t=this.hass.language;return W`
      <div class="field">
        <label>${Ma("panels.schedules.season.label",t)}</label>
        <div class="rowfields">
          <input
            type="date"
            .value="${e.start_date||""}"
            @change=${e=>this._emitChanged({start_date:e.target.value||void 0})}
          />
          <span class="suffix"
            >${Ma("panels.schedules.season.to",t)}</span
          >
          <input
            type="date"
            .value="${e.end_date||""}"
            @change=${e=>this._emitChanged({end_date:e.target.value||void 0})}
          />
        </div>
        <span class="field-help"
          >${Ma("panels.schedules.season.note",t)}</span
        >
      </div>
    `}render(){var e;if(!this.hass||!this.schedule)return W``;const t=this.schedule,s=this.hass.language;return W`
      <ha-dialog open @closed=${this._cancel}>
        <div slot="heading" class="dialog-heading-row">
          <span>${this.heading}</span>
          <label class="enabled-toggle">
            <input
              type="checkbox"
              ?checked="${t.enabled}"
              @change=${e=>this._emitChanged({enabled:e.target.checked})}
            />
            ${Ma("panels.schedules.fields.enabled",s)}
          </label>
        </div>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        <div class="dialog-content">
          <div class="field">
<<<<<<< HEAD
            <label
              >${Oa("panels.schedules.fields.name",this.hass.language)}</label
            >
=======
            <label>${Ma("panels.schedules.fields.name",s)}</label>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            <input
              type="text"
              .value="${t.name}"
              @input=${e=>this._emitChanged({name:e.target.value})}
              required
            />
          </div>

<<<<<<< HEAD
          <div class="field">
            <label
              >${Oa("panels.schedules.fields.recurrence",this.hass.language)}</label
            >
            <select
              @change=${e=>this._emitChanged({recurrence:e.target.value})}
            >
              ${ti.map(e=>W`
                  <option value="${e}" ?selected="${t.recurrence===e}">
                    ${Fn(e,this.hass.language)}
                  </option>
                `)}
            </select>
          </div>

          ${this._renderRecurrenceFields()}
          <div class="when-row">
            <div class="when-rows-col">${this._renderWindowRows()}</div>
            <si-run-window-dial
              .hass="${this.hass}"
              .rows="${wn(t)}"
              .recurrence="${t.recurrence}"
              .intervalHours="${t.interval_hours}"
              .intervalStartTime="${t.start_time}"
              .nominalDemandSeconds="${null!==(e=t.nominal_demand_seconds)&&void 0!==e?e:0}"
            ></si-run-window-dial>
          </div>
          ${this._renderZonePicker()}

          <div class="field-row">
            <label
              >${Oa("panels.schedules.fields.enabled",this.hass.language)}</label
            >
            <input
              type="checkbox"
              ?checked="${t.enabled}"
              @change=${e=>this._emitChanged({enabled:e.target.checked})}
            />
          </div>

          <div class="field">
            <label
              >${Oa("panels.schedules.fields.start_date",this.hass.language)}</label
            >
            <input
              type="date"
              .value="${t.start_date||""}"
              @change=${e=>this._emitChanged({start_date:e.target.value||void 0})}
            />
          </div>

          <div class="field">
            <label
              >${Oa("panels.schedules.fields.end_date",this.hass.language)}</label
            >
            <input
              type="date"
              .value="${t.end_date||""}"
              @change=${e=>this._emitChanged({end_date:e.target.value||void 0})}
            />
          </div>
=======
          ${this._renderSection("when",W`
              <div class="field">
                <select
                  aria-label="${Ma("panels.schedules.fields.recurrence",s)}"
                  @change=${e=>this._emitChanged({recurrence:e.target.value})}
                >
                  ${is.map(e=>W`
                      <option value="${e}" ?selected="${t.recurrence===e}">
                        ${ao(e,s)}
                      </option>
                    `)}
                </select>
              </div>
              ${this._renderRecurrenceFields()}
              <div class="when-row">
                <div class="when-rows-col">${this._renderWindowRows()}</div>
                <si-run-window-dial
                  .hass="${this.hass}"
                  .rows="${kn(t)}"
                  .recurrence="${t.recurrence}"
                  .intervalHours="${t.interval_hours}"
                  .intervalStartTime="${t.start_time}"
                  .nominalDemandSeconds="${null!==(e=t.nominal_demand_seconds)&&void 0!==e?e:0}"
                ></si-run-window-dial>
              </div>
            `)}
          ${this._renderSection("zones",this._renderZonePicker())}
          ${this._renderSection("season",this._renderSeasonSection())}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>

        <button
          slot="secondaryAction"
          class="dialog-btn"
          @click=${this._cancel}
        >
<<<<<<< HEAD
          ${Oa("common.actions.cancel",this.hass.language)}
=======
          ${Ma("common.actions.cancel",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </button>
        <button
          slot="primaryAction"
          class="dialog-btn dialog-btn-primary"
          ?disabled="${!this._canSave()}"
          @click=${this._save}
        >
<<<<<<< HEAD
          ${Oa("common.actions.save",this.hass.language)}
=======
          ${Ma("common.actions.save",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </button>
      </ha-dialog>
    `}static get styles(){return[Ka,r`
        /* The buttons sit in ha-dialog's own action slots rather than in a
           footer inside the content, so the actions bar it always renders is
           the one holding them instead of an empty 52px strip below them. */
        .dialog-content {
          display: flex;
          flex-direction: column;
          gap: 14px;
          padding: 4px 0 8px;
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
        .field-help {
          font-size: 0.8125rem;
          line-height: 1.35;
          color: var(--secondary-text-color);
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
        /* Start/Finish/pinned-end rows (GitLab #29): a mode select plus at
           most one stepper, all inline, so the pair reads as one control
           rather than a stack of unrelated fields. */
        .window-row {
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 8px;
        }
        .window-row > label {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--secondary-text-color);
          min-width: 44px;
        }
        .window-row select,
        .window-row input[type="time"],
        .window-row input[type="number"] {
          padding: 8px 10px;
          border: 1px solid var(--divider-color, #e0e0e0);
          border-radius: 4px;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
          font-size: 1rem;
          font-family: inherit;
          box-sizing: border-box;
        }
        .window-row input[type="number"] {
          width: 76px;
        }
        /* Part of the row rather than chrome, so these read as primary text
           rather than a muted label. */
        .row-inline {
          color: var(--primary-text-color);
          font-size: 0.9375rem;
        }
        /* Help is a child of its row: indented, with an arrow glyph in the
           gap pointing back up at the control it explains. */
        .window-row-help {
          display: flex;
          align-items: baseline;
          gap: 6px;
          padding-left: 20px;
          margin-top: -4px;
        }
        .help-arrow {
          opacity: 0.5;
        }
        .window-row-help .help-text {
          font-size: 0.8125rem;
          line-height: 1.35;
          color: var(--secondary-text-color);
        }
        .window-row-help.is-error .help-text {
          color: var(--error-color, #db4437);
        }
<<<<<<< HEAD
        /* Placeholder layout only — GitLab #30 is concurrently reshaping
           this dialog into WHEN/ZONES/SEASON cards, whose WHEN card's
           right-hand column is where si-run-window-dial is meant to live.
           Until that lands, sit the dial beside the Start/Finish/pinned-end
           rows so it is visibly wired in rather than orphaned. */
=======
        /* Amber, not red: an unreachable bearing still saves and the backend
           still accepts it — the schedule just will not behave the way the
           row reads. See describeWindow's unresolvable handling. */
        .window-row-help.is-warning .help-text {
          color: var(--warning-color, #ffa600);
        }
        /* Two-column layout inside the WHEN card (GitLab #31): the
           Start/Finish/pinned-end rows on the left, the run-window dial in
           a fixed-width right column, collapsing to one column on narrow
           dialogs. */
>>>>>>> f4290c2 (feat(schedules): warn when a solar-azimuth bearing the sun never reaches is set)
        .when-row {
          display: flex;
          flex-wrap: wrap;
          gap: 16px;
          align-items: flex-start;
        }
        .when-rows-col {
          flex: 1 1 240px;
          display: flex;
          flex-direction: column;
          gap: 14px;
          min-width: 0;
        }
        .when-row si-run-window-dial {
          flex: 0 0 156px;
        }
<<<<<<< HEAD
      `]}};t([me({attribute:!1})],Zn.prototype,"hass",void 0),t([me({attribute:!1})],Zn.prototype,"schedule",void 0),t([me({attribute:!1})],Zn.prototype,"zones",void 0),t([me({attribute:!1})],Zn.prototype,"heading",void 0),Zn=t([ue("si-schedule-dialog")],Zn);let Wn=class extends(Fa(ce)){constructor(){super(...arguments),this._schedules=[],this._zones=[],this._isLoading=!0,this._showDialog=!1,this._editingSchedule=jn(),this._editingId=null}hassSubscribe(){return this._load(),[this.hass.connection.subscribeMessage(()=>this._load(),{type:be+"_config_updated"})]}async _load(){var e;if(this.hass)try{const[t,i]=await Promise.all([(e=this.hass,e.callWS({type:be+"/schedules"})),Ti(this.hass)]);this._schedules=t||[],this._zones=i||[]}catch(e){console.error("Failed to load schedules",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{this._isLoading=!1}}_openAdd(){this._editingSchedule=jn(),this._editingId=null,this._showDialog=!0}_openEdit(e){var t;this._editingSchedule=Object.assign({},e),this._editingId=null!==(t=e.id)&&void 0!==t?t:null,this._showDialog=!0}_closeDialog(){this._showDialog=!1}async _save(){const e=Object.assign({},this._editingSchedule);this._editingId&&(e.id=this._editingId);try{const t=await Li(this.hass,e);if(t&&!1===t.success)throw new Error(t.error||"");this._closeDialog(),await this._load()}catch(e){console.error("Failed to save schedule",e),Ba(this,this.hass,"common.errors.save_failed",e)}}async _delete(e){try{await(t=this.hass,i=e,t.callWS({type:be+"/schedule_delete",schedule_id:i})),await this._load()}catch(e){console.error("Failed to delete schedule",e),Ba(this,this.hass,"common.errors.delete_failed",e)}var t,i}_onScheduleChanged(e){this._editingSchedule=e.detail.value}_zonesLabel(e){if("all"===e)return Oa("panels.schedules.zones_all",this.hass.language);if(Array.isArray(e)){const t=e.map(e=>{const t=this._zones.find(t=>String(t.id)===String(e));return t?t.name:e}).join(", ");return t||e.join(", ")}return String(e)}_dialogTitle(){return this._editingId?Oa("panels.schedules.dialog.edit_title",this.hass.language):Oa("panels.schedules.dialog.add_title",this.hass.language)}render(){return this.hass?this._isLoading?W`
        <ha-card
          header="${Oa("panels.schedules.title",this.hass.language)}"
        >
          <div class="card-content">
            ${Oa("common.loading",this.hass.language)}...
=======
      `]}};t([me({attribute:!1})],no.prototype,"hass",void 0),t([me({attribute:!1})],no.prototype,"schedule",void 0),t([me({attribute:!1})],no.prototype,"zones",void 0),t([me({attribute:!1})],no.prototype,"heading",void 0),no=t([ue("si-schedule-dialog")],no);let oo=class extends(Wa(ce)){constructor(){super(...arguments),this._schedules=[],this._zones=[],this._isLoading=!0,this._showDialog=!1,this._editingSchedule=io(),this._editingId=null}hassSubscribe(){return this._load(),[this.hass.connection.subscribeMessage(()=>this._load(),{type:be+"_config_updated"})]}async _load(){var e;if(this.hass)try{const[t,s]=await Promise.all([(e=this.hass,e.callWS({type:be+"/schedules"})),Ds(this.hass)]);this._schedules=t||[],this._zones=s||[]}catch(e){console.error("Failed to load schedules",e),ja(this,this.hass,"common.errors.load_failed",e)}finally{this._isLoading=!1}}_openAdd(){this._editingSchedule=io(),this._editingId=null,this._showDialog=!0}_openEdit(e){var t;this._editingSchedule=Object.assign({},e),this._editingId=null!==(t=e.id)&&void 0!==t?t:null,this._showDialog=!0}_closeDialog(){this._showDialog=!1}async _save(){const e=Object.assign({},this._editingSchedule);this._editingId&&(e.id=this._editingId);try{const t=await Bs(this.hass,e);if(t&&!1===t.success)throw new Error(t.error||"");this._closeDialog(),await this._load()}catch(e){console.error("Failed to save schedule",e),ja(this,this.hass,"common.errors.save_failed",e)}}async _delete(e){try{await(t=this.hass,s=e,t.callWS({type:be+"/schedule_delete",schedule_id:s})),await this._load()}catch(e){console.error("Failed to delete schedule",e),ja(this,this.hass,"common.errors.delete_failed",e)}var t,s}_onScheduleChanged(e){this._editingSchedule=e.detail.value}_zonesLabel(e){if("all"===e)return Ma("panels.schedules.zones_all",this.hass.language);if(Array.isArray(e)){const t=e.map(e=>{const t=this._zones.find(t=>String(t.id)===String(e));return t?t.name:e}).join(", ");return t||e.join(", ")}return String(e)}_dialogTitle(){return this._editingId?Ma("panels.schedules.dialog.edit_title",this.hass.language):Ma("panels.schedules.dialog.add_title",this.hass.language)}render(){return this.hass?this._isLoading?W`
        <ha-card
          header="${Ma("panels.schedules.title",this.hass.language)}"
        >
          <div class="card-content">
            ${Ma("common.loading",this.hass.language)}...
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </div>
        </ha-card>
      `:W`
      ${this._showDialog?W`
            <si-schedule-dialog
              .hass=${this.hass}
              .schedule=${this._editingSchedule}
              .zones=${this._zones}
              .heading=${this._dialogTitle()}
              @schedule-changed=${this._onScheduleChanged}
              @save=${this._save}
              @cancel=${this._closeDialog}
            ></si-schedule-dialog>
          `:""}

      <ha-card
<<<<<<< HEAD
        header="${Oa("panels.schedules.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Oa("panels.schedules.description",this.hass.language)}
=======
        header="${Ma("panels.schedules.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Ma("panels.schedules.description",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>
        <div class="card-content">
          <button class="add-btn" @click=${this._openAdd}>
            <svg style="width:20px;height:20px" viewBox="0 0 24 24">
              <path fill="currentColor" d="${ja}" />
            </svg>
<<<<<<< HEAD
            ${Oa("panels.schedules.add",this.hass.language)}
=======
            ${Ma("panels.schedules.add",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </button>
        </div>
      </ha-card>

      ${0===this._schedules.length?W`
            <ha-card>
              <div class="card-content">
<<<<<<< HEAD
                ${Oa("panels.schedules.no_items",this.hass.language)}
=======
                ${Ma("panels.schedules.no_items",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </div>
            </ha-card>
          `:this._schedules.map(e=>W`
              <ha-card header="${e.name}">
                <div class="card-content">
<<<<<<< HEAD
                  <div class="info-row">
                    <span class="info-label"
                      >${Oa("panels.schedules.fields.recurrence",this.hass.language)}:</span
                    >
                    <span
                      >${Fn(e.recurrence,this.hass.language)}</span
=======
                  <div class="summary">
                    ${Sn(e,this.hass.language).text}
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${Ma("panels.schedules.fields.recurrence",this.hass.language)}:</span
                    >
                    <span
                      >${ao(e.recurrence,this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    >
                  </div>
                  ${"interval"!==e.recurrence&&"time"===e.start_mode&&e.start_time?W`
                        <div class="info-row">
                          <span class="info-label"
<<<<<<< HEAD
                            >${Oa("panels.schedules.fields.start_time",this.hass.language)}:</span
=======
                            >${Ma("panels.schedules.fields.start_time",this.hass.language)}:</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                          >
                          <span>${e.start_time}</span>
                        </div>
                      `:""}
                  ${"interval"!==e.recurrence&&"time"===e.finish_mode&&e.finish_time?W`
                        <div class="info-row">
                          <span class="info-label"
<<<<<<< HEAD
                            >${Oa("panels.schedules.fields.finish_time",this.hass.language)}:</span
=======
                            >${Ma("panels.schedules.fields.finish_time",this.hass.language)}:</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                          >
                          <span>${e.finish_time}</span>
                        </div>
                      `:""}
                  ${e.interval_hours?W`
                        <div class="info-row">
                          <span class="info-label"
<<<<<<< HEAD
                            >${Oa("panels.schedules.fields.interval_hours",this.hass.language)}:</span
                          >
                          <span
                            >${e.interval_hours}
                            ${Oa("panels.schedules.hours",this.hass.language)}</span
=======
                            >${Ma("panels.schedules.fields.interval_hours",this.hass.language)}:</span
                          >
                          <span
                            >${e.interval_hours}
                            ${Ma("panels.schedules.hours",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                          >
                        </div>
                      `:""}
                  ${"interval"===e.recurrence&&e.start_time?W`
                        <div class="info-row">
                          <span class="info-label"
<<<<<<< HEAD
                            >${Oa("panels.schedules.fields.start_time",this.hass.language)}:</span
=======
                            >${Ma("panels.schedules.fields.start_time",this.hass.language)}:</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                          >
                          <span>${e.start_time}</span>
                        </div>
                      `:""}
                  <div class="info-row">
                    <span class="info-label"
<<<<<<< HEAD
                      >${Oa("panels.schedules.fields.zones",this.hass.language)}:</span
=======
                      >${Ma("panels.schedules.fields.zones",this.hass.language)}:</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    >
                    <span>${this._zonesLabel(e.zones)}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
<<<<<<< HEAD
                      >${Oa("panels.schedules.fields.enabled",this.hass.language)}:</span
                    >
                    <span
                      >${e.enabled?Oa("common.labels.yes",this.hass.language):Oa("common.labels.no",this.hass.language)}</span
=======
                      >${Ma("panels.schedules.fields.enabled",this.hass.language)}:</span
                    >
                    <span
                      >${e.enabled?Ma("common.labels.yes",this.hass.language):Ma("common.labels.no",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    >
                  </div>
                </div>
                <div class="card-content action-buttons">
                  <div class="action-buttons-left">
                    <div
                      class="action-button-left"
                      @click=${()=>this._openEdit(e)}
                    >
                      <svg style="width:20px;height:20px" viewBox="0 0 24 24">
                        <path fill="#404040" d="${"M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z"}" />
                      </svg>
                      <span class="action-button-label"
<<<<<<< HEAD
                        >${Oa("common.actions.edit",this.hass.language)}</span
=======
                        >${Ma("common.actions.edit",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                      >
                    </div>
                  </div>
                  <div class="action-buttons-right">
                    <div
                      class="action-button-right"
                      @click=${()=>e.id&&this._delete(e.id)}
                    >
                      <span class="action-button-label"
<<<<<<< HEAD
                        >${Oa("common.actions.delete",this.hass.language)}</span
=======
                        >${Ma("common.actions.delete",this.hass.language)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                      >
                      <svg style="width:20px;height:20px" viewBox="0 0 24 24">
                        <path fill="#404040" d="${"M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"}" />
                      </svg>
                    </div>
                  </div>
                </div>
              </ha-card>
            `)}
    `:W``}static get styles(){return[Ka,r`
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
<<<<<<< HEAD
      `]}};t([me({attribute:!1})],Wn.prototype,"hass",void 0),t([ve()],Wn.prototype,"_schedules",void 0),t([ve()],Wn.prototype,"_zones",void 0),t([ve()],Wn.prototype,"_isLoading",void 0),t([ve()],Wn.prototype,"_showDialog",void 0),t([ve()],Wn.prototype,"_editingSchedule",void 0),t([ve()],Wn.prototype,"_editingId",void 0),Wn=t([ue("smart-irrigation-view-schedules")],Wn);let qn=class extends(Fa(ce)){constructor(){super(...arguments),this._forecast=null,this._mappings=[],this._records=new Map,this._loading=!0,this._metric=!0,this._climate=[]}hassSubscribe(){return this._fetch(),[this.hass.connection.subscribeMessage(()=>this._fetch(),{type:be+"_config_updated"})]}async _fetch(){var e,t;if(this.hass)try{const[i,s,a,n]=await Promise.all([(t=this.hass,t.callWS({type:be+"/weather_forecast"})),Ii(this.hass),Ei(this.hass),Pi(this.hass)]);this._forecast=i,this._mappings=s||[],this._metric=(null==a?void 0:a.units)!==He;const o=n?Object.values(n):[];this._climate=o.length>0&&(null===(e=o[0])||void 0===e?void 0:e.monthly_estimates)||[];const r=new Map;await Promise.all(this._mappings.map(async e=>{if(void 0!==e.id)try{r.set(e.id,await((e,t,i=10)=>e.callWS({type:be+"/weather_records",mapping_id:t,limit:i}))(this.hass,e.id.toString(),0)||[])}catch(e){}})),this._records=r}catch(e){console.error("Failed to fetch weather data",e)}finally{this._loading=!1}}render(){return this.hass?W`${this._renderForecast()} ${this._renderRecords()}
    ${this._renderSeasonal()}`:W``}_renderSeasonal(){if(!this.hass)return W``;const e=this.hass.language;return W`
      <ha-card
        header="${Oa("panels.setup.weather_data.seasonal_title",e)}"
      >
        <div class="card-content">
          ${0===this._climate.length?W`<div class="weather-note">
                ${Oa("panels.zones.calendar.no_data",e)}
=======
      `]}};t([me({attribute:!1})],oo.prototype,"hass",void 0),t([ve()],oo.prototype,"_schedules",void 0),t([ve()],oo.prototype,"_zones",void 0),t([ve()],oo.prototype,"_isLoading",void 0),t([ve()],oo.prototype,"_showDialog",void 0),t([ve()],oo.prototype,"_editingSchedule",void 0),t([ve()],oo.prototype,"_editingId",void 0),oo=t([ue("smart-irrigation-view-schedules")],oo);let ro=class extends(Wa(ce)){constructor(){super(...arguments),this._forecast=null,this._mappings=[],this._records=new Map,this._loading=!0,this._metric=!0,this._climate=[]}hassSubscribe(){return this._fetch(),[this.hass.connection.subscribeMessage(()=>this._fetch(),{type:be+"_config_updated"})]}async _fetch(){var e,t;if(this.hass)try{const[s,i,a,n]=await Promise.all([(t=this.hass,t.callWS({type:be+"/weather_forecast"})),Ls(this.hass),Ts(this.hass),Rs(this.hass)]);this._forecast=s,this._mappings=i||[],this._metric=(null==a?void 0:a.units)!==De;const o=n?Object.values(n):[];this._climate=o.length>0&&(null===(e=o[0])||void 0===e?void 0:e.monthly_estimates)||[];const r=new Map;await Promise.all(this._mappings.map(async e=>{if(void 0!==e.id)try{r.set(e.id,await((e,t,s=10)=>e.callWS({type:be+"/weather_records",mapping_id:t,limit:s}))(this.hass,e.id.toString(),0)||[])}catch(e){}})),this._records=r}catch(e){console.error("Failed to fetch weather data",e)}finally{this._loading=!1}}render(){return this.hass?W`${this._renderForecast()} ${this._renderRecords()}
    ${this._renderSeasonal()}`:W``}_renderSeasonal(){if(!this.hass)return W``;const e=this.hass.language;return W`
      <ha-card
        header="${Ma("panels.setup.weather_data.seasonal_title",e)}"
      >
        <div class="card-content">
          ${0===this._climate.length?W`<div class="weather-note">
                ${Ma("panels.zones.calendar.no_data",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </div>`:W`
                <div class="seasonal-table">
                  <div class="weather-header">
                    <span
<<<<<<< HEAD
                      >${Oa("panels.zones.calendar.month",e)}</span
                    >
                    <span>${Oa("panels.zones.calendar.et",e)}</span>
                    <span
                      >${Oa("panels.zones.calendar.precipitation",e)}</span
                    >
                    <span
                      >${Oa("panels.zones.calendar.avg_temp",e)}</span
=======
                      >${Ma("panels.zones.calendar.month",e)}</span
                    >
                    <span>${Ma("panels.zones.calendar.et",e)}</span>
                    <span
                      >${Ma("panels.zones.calendar.precipitation",e)}</span
                    >
                    <span
                      >${Ma("panels.zones.calendar.avg_temp",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    >
                  </div>
                  ${this._climate.map(e=>W`
                      <div class="weather-row">
                        <span
                          >${e.month_name||`Month ${e.month}`||"-"}</span
                        >
                        <span
                          >${dn(e.estimated_et_mm,"precipitation",this._metric)}</span
                        >
                        <span
                          >${dn(e.average_precipitation_mm,"precipitation",this._metric)}</span
                        >
                        <span
                          >${dn(e.average_temperature_c,"temperature",this._metric)}</span
                        >
                      </div>
                    `)}
                </div>
              `}
        </div>
      </ha-card>
    `}_renderForecast(){if(!this.hass)return W``;const e=this.hass.language,t=this._forecast;return W`
      <ha-card
<<<<<<< HEAD
        header="${Oa("panels.setup.weather_data.forecast_title",e)}"
=======
        header="${Ma("panels.setup.weather_data.forecast_title",e)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      >
        <div class="card-content">
          ${t&&t.available&&0!==t.days.length?W`
                <div class="forecast-row">
                  ${t.days.map(t=>this._renderForecastDay(t,e))}
                </div>
              `:W`<div class="weather-note">
<<<<<<< HEAD
                ${Oa("panels.setup.weather_data.forecast_none",e)}
=======
                ${Ma("panels.setup.weather_data.forecast_none",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </div>`}
        </div>
      </ha-card>
    `}_renderForecastDay(e,t){const i=(()=>{try{return new Intl.DateTimeFormat(t,{weekday:"short",month:"short",day:"numeric"}).format(new Date(e.date+"T00:00:00"))}catch(t){return e.date}})(),s=e=>{const t=ln(e,"temperature",this._metric);return t?`${Math.round(t.value)}°`:"-"};return W`
      <div class="forecast-day">
        <div class="forecast-date">${i}</div>
        <div class="forecast-temps">
          <span class="hi">${s(e.temp_max)}</span>
          <span class="lo">${s(e.temp_min)}</span>
        </div>
        <div class="forecast-meta">
          <ha-icon icon="mdi:weather-rainy"></ha-icon>${dn(e.precipitation,"precipitation",this._metric)}
        </div>
        <div class="forecast-meta">
          <ha-icon icon="mdi:weather-windy"></ha-icon>${dn(e.windspeed,"windspeed",this._metric)}
        </div>
      </div>
    `}_renderRecords(){if(!this.hass)return W``;const e=this.hass.language;return this._loading&&0===this._mappings.length?W`<ha-card
<<<<<<< HEAD
        header="${Oa("panels.mappings.weather-records.title",e)}"
      >
        <div class="card-content">
          <div class="loading-indicator">
            ${Oa("common.loading-messages.general",e)}
          </div>
        </div>
      </ha-card>`:0===this._mappings.length?W`<ha-card
        header="${Oa("panels.mappings.weather-records.title",e)}"
      >
        <div class="card-content">
          <div class="weather-note">
            ${Oa("panels.mappings.no_items",e)}
          </div>
        </div>
      </ha-card>`:W`${this._mappings.map(t=>this._renderMappingRecords(t,e))}`}_renderMappingRecords(e,t){const i=void 0!==e.id&&this._records.get(e.id)||[],s=`${Oa("panels.mappings.weather-records.title",t)} — ${e.name}`,a=e=>{try{return t=e,Number.isNaN(Ya(t).getTime())?"-":function(e){const t=Ya(e);return`${Va(t.getMonth()+1)}-${Va(t.getDate())} ${Va(t.getHours())}:${Va(t.getMinutes())}`}(e)}catch(e){return"-"}var t};return W`
      <ha-card header="${s}">
        <div class="card-content">
          ${0===i.length?W`<div class="weather-note">
                ${Oa("panels.mappings.weather-records.no-data",t)}
=======
        header="${Ma("panels.mappings.weather-records.title",e)}"
      >
        <div class="card-content">
          <div class="loading-indicator">
            ${Ma("common.loading-messages.general",e)}
          </div>
        </div>
      </ha-card>`:0===this._mappings.length?W`<ha-card
        header="${Ma("panels.mappings.weather-records.title",e)}"
      >
        <div class="card-content">
          <div class="weather-note">
            ${Ma("panels.mappings.no_items",e)}
          </div>
        </div>
      </ha-card>`:W`${this._mappings.map(t=>this._renderMappingRecords(t,e))}`}_renderMappingRecords(e,t){const s=void 0!==e.id&&this._records.get(e.id)||[],i=`${Ma("panels.mappings.weather-records.title",t)} — ${e.name}`,a=e=>{try{return t=e,Number.isNaN(Ja(t).getTime())?"-":function(e){const t=Ja(e);return`${Xa(t.getMonth()+1)}-${Xa(t.getDate())} ${Xa(t.getHours())}:${Xa(t.getMinutes())}`}(e)}catch(e){return"-"}var t};return W`
      <ha-card header="${i}">
        <div class="card-content">
          ${0===s.length?W`<div class="weather-note">
                ${Ma("panels.mappings.weather-records.no-data",t)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </div>`:W`
                <div class="weather-table">
                  <div class="weather-header">
                    <span
<<<<<<< HEAD
                      >${Oa("panels.mappings.weather-records.timestamp",t)}</span
                    >
                    <span
                      >${Oa("panels.mappings.weather-records.temperature",t)}</span
                    >
                    <span
                      >${Oa("panels.mappings.weather-records.humidity",t)}</span
                    >
                    <span
                      >${Oa("panels.mappings.weather-records.dewpoint",t)}</span
                    >
                    <span
                      >${Oa("panels.mappings.weather-records.wind",t)}</span
                    >
                    <span
                      >${Oa("panels.mappings.weather-records.pressure",t)}</span
                    >
                    <span
                      >${Oa("panels.mappings.weather-records.precipitation",t)}</span
                    >
                    <span
                      >${Oa("panels.mappings.weather-records.retrieval-time",t)}</span
=======
                      >${Ma("panels.mappings.weather-records.timestamp",t)}</span
                    >
                    <span
                      >${Ma("panels.mappings.weather-records.temperature",t)}</span
                    >
                    <span
                      >${Ma("panels.mappings.weather-records.humidity",t)}</span
                    >
                    <span
                      >${Ma("panels.mappings.weather-records.dewpoint",t)}</span
                    >
                    <span
                      >${Ma("panels.mappings.weather-records.wind",t)}</span
                    >
                    <span
                      >${Ma("panels.mappings.weather-records.pressure",t)}</span
                    >
                    <span
                      >${Ma("panels.mappings.weather-records.precipitation",t)}</span
                    >
                    <span
                      >${Ma("panels.mappings.weather-records.retrieval-time",t)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    >
                  </div>
                  ${i.map(e=>W`
                      <div class="weather-row">
                        <span>${a(e.timestamp)}</span>
                        <span
                          >${dn(e.temperature,"temperature",this._metric)}</span
                        >
                        <span>${(e=>null!=e?e.toFixed(1)+" %":"-")(e.humidity)}</span>
                        <span
                          >${dn(e.dewpoint,"temperature",this._metric)}</span
                        >
                        <span
                          >${dn(e.wind_speed,"windspeed",this._metric)}</span
                        >
                        <span
                          >${dn(e.pressure,"pressure",this._metric)}</span
                        >
                        <span
                          >${dn(e.precipitation,"precipitation",this._metric)}</span
                        >
                        <span>${a(e.retrieval_time)}</span>
                      </div>
                    `)}
                </div>
              `}
        </div>
      </ha-card>
    `}static get styles(){return r`
      ${Ka}

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

      /* 4-column seasonal/climate table (month + ET + precip + temp). Reuses the
         globalStyle .weather-header / .weather-row (display:contents) cells. */
      .seasonal-table {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 8px;
        font-size: 0.85em;
      }
<<<<<<< HEAD
    `}};t([me()],qn.prototype,"narrow",void 0),t([ve()],qn.prototype,"_forecast",void 0),t([ve()],qn.prototype,"_mappings",void 0),t([ve()],qn.prototype,"_records",void 0),t([ve()],qn.prototype,"_loading",void 0),t([ve()],qn.prototype,"_metric",void 0),t([ve()],qn.prototype,"_climate",void 0),qn=t([ue("smart-irrigation-view-weather-data")],qn);let Gn=class extends(Fa(ce)){constructor(){super(...arguments),this._saving=!1}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch experimental config:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to refresh experimental config:",e)})},{type:be+"_config_updated"})]}async _fetchData(){if(this.hass)try{this.config=await Ei(this.hass)}catch(e){console.error("Error fetching config:",e),Ba(this,this.hass,"common.errors.load_failed",e)}}async _toggle(e,t){if(this.hass&&this.config){this.config=Object.assign(Object.assign({},this.config),{[e]:t}),this._saving=!0;try{await Ci(this.hass,{[e]:t})}catch(e){console.error("Error saving experimental config:",e),Ba(this,this.hass,"common.errors.save_failed",e),await this._fetchData()}finally{this._saving=!1}}}render(){var e,t;return this.hass&&this.config?W`
=======
    `}};t([me()],ro.prototype,"narrow",void 0),t([ve()],ro.prototype,"_forecast",void 0),t([ve()],ro.prototype,"_mappings",void 0),t([ve()],ro.prototype,"_records",void 0),t([ve()],ro.prototype,"_loading",void 0),t([ve()],ro.prototype,"_metric",void 0),t([ve()],ro.prototype,"_climate",void 0),ro=t([ue("smart-irrigation-view-weather-data")],ro);let lo=class extends(Wa(ce)){constructor(){super(...arguments),this._saving=!1}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch experimental config:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to refresh experimental config:",e)})},{type:be+"_config_updated"})]}async _fetchData(){if(this.hass)try{this.config=await Ts(this.hass)}catch(e){console.error("Error fetching config:",e),ja(this,this.hass,"common.errors.load_failed",e)}}async _toggle(e,t){if(this.hass&&this.config){this.config=Object.assign(Object.assign({},this.config),{[e]:t}),this._saving=!0;try{await Os(this.hass,{[e]:t})}catch(e){console.error("Error saving experimental config:",e),ja(this,this.hass,"common.errors.save_failed",e),await this._fetchData()}finally{this._saving=!1}}}render(){var e,t;return this.hass&&this.config?W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      ${this._renderIntro()}
      ${this._renderToggleCard("observed_watering","observed_watering_enabled",this.config.observed_watering_enabled)}
      ${this._renderToggleCard("live_estimate","live_estimate_enabled",this.config.live_estimate_enabled)}
      ${this._renderToggleCard("distributors","distributors_enabled",this.config.distributors_enabled)}
      ${this._renderContinuousUpdatesCard()}
      ${this._renderToggleCard("hourly_calculation","hourlycalculation",this.config.hourlycalculation)}
    `:W`<div class="loading-indicator">
<<<<<<< HEAD
        ${Oa("common.loading-messages.configuration",null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en")}
      </div>`}_renderContinuousUpdatesCard(){if(!this.hass||!this.config)return W``;const e="panels.experimental.continuous_updates",t=this.config.continuousupdates;return W`
      <ha-card header="${Oa(`${e}.title`,this.hass.language)}">
        <div class="card-content description-text">
          ${Oa(`${e}.description`,this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>${Oa(`${e}.label`,this.hass.language)}</label>
=======
        ${Ma("common.loading-messages.configuration",null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en")}
      </div>`}_renderContinuousUpdatesCard(){if(!this.hass||!this.config)return W``;const e="panels.experimental.continuous_updates",t=this.config.continuousupdates;return W`
      <ha-card header="${Ma(`${e}.title`,this.hass.language)}">
        <div class="card-content description-text">
          ${Ma(`${e}.description`,this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>${Ma(`${e}.label`,this.hass.language)}</label>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            <ha-switch
              .checked="${t}"
              ?disabled="${this._saving}"
              @change="${e=>this._toggle("continuousupdates",e.target.checked)}"
            ></ha-switch>
          </div>
          ${t?W`<div class="setting-row">
                <label>
<<<<<<< HEAD
                  ${Oa(`${e}.debounce_label`,this.hass.language)}
=======
                  ${Ma(`${e}.debounce_label`,this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </label>
                <input
                  type="number"
                  class="settings-input shortfield"
                  min="0"
                  step="500"
                  inputmode="numeric"
                  .value="${this.config.sensor_debounce}"
                  ?disabled="${this._saving}"
                  @change="${e=>this._saveDebounce(e.target.value)}"
                />
              </div>`:""}
          <div class="setting-note">
<<<<<<< HEAD
            ${Oa(`${e}.note`,this.hass.language)}
=======
            ${Ma(`${e}.note`,this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </div>
        </div>
      </ha-card>
    `}async _saveDebounce(e){if(!this.hass||!this.config)return;const t=Number.parseInt(e,10);if(Number.isNaN(t)||t<0)await this._fetchData();else{this.config=Object.assign(Object.assign({},this.config),{[ke]:t}),this._saving=!0;try{await Ci(this.hass,{[ke]:t})}catch(e){console.error("Error saving sensor debounce:",e),Ba(this,this.hass,"common.errors.save_failed",e),await this._fetchData()}finally{this._saving=!1}}}_renderIntro(){return this.hass?W`
      <div class="experimental-banner">
        <ha-icon icon="mdi:flask-outline"></ha-icon>
        <div>
          <div class="experimental-banner-title">
<<<<<<< HEAD
            ${Oa("panels.experimental.title",this.hass.language)}
          </div>
          <div class="experimental-banner-text">
            ${Oa("panels.experimental.warning",this.hass.language)}
          </div>
        </div>
      </div>
    `:W``}_renderToggleCard(e,t,i){if(!this.hass)return W``;const s=`panels.experimental.${e}`;return W`
      <ha-card header="${Oa(`${s}.title`,this.hass.language)}">
        <div class="card-content description-text">
          ${Oa(`${s}.description`,this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>${Oa(`${s}.label`,this.hass.language)}</label>
=======
            ${Ma("panels.experimental.title",this.hass.language)}
          </div>
          <div class="experimental-banner-text">
            ${Ma("panels.experimental.warning",this.hass.language)}
          </div>
        </div>
      </div>
    `:W``}_renderToggleCard(e,t,s){if(!this.hass)return W``;const i=`panels.experimental.${e}`;return W`
      <ha-card header="${Ma(`${i}.title`,this.hass.language)}">
        <div class="card-content description-text">
          ${Ma(`${i}.description`,this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>${Ma(`${i}.label`,this.hass.language)}</label>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            <ha-switch
              .checked="${i}"
              ?disabled="${this._saving}"
              @change="${e=>this._toggle(t,e.target.checked)}"
            ></ha-switch>
          </div>
          <div class="setting-note">
<<<<<<< HEAD
            ${Oa(`${s}.note`,this.hass.language)}
=======
            ${Ma(`${i}.note`,this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </div>
        </div>
      </ha-card>
    `}static get styles(){return r`
      ${Ka}

      .experimental-banner {
        display: flex;
        gap: 12px;
        align-items: flex-start;
        padding: 12px 16px;
        margin-bottom: 12px;
        border-radius: 8px;
        background: rgba(var(--rgb-warning-color, 255, 152, 0), 0.12);
        color: var(--primary-text-color);
      }

      .experimental-banner ha-icon {
        color: var(--warning-color, #ff9800);
        --mdc-icon-size: 24px;
        flex-shrink: 0;
      }

      .experimental-banner-title {
        font-weight: 600;
        margin-bottom: 2px;
      }

      .experimental-banner-text {
        font-size: 0.875rem;
        color: var(--secondary-text-color);
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
        gap: 16px;
      }

      .setting-row label {
        flex: 1;
        color: var(--primary-text-color);
        font-size: 0.9375rem;
      }

      .setting-note {
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
        font-style: italic;
        padding-top: 4px;
        border-top: 1px solid var(--divider-color);
      }
<<<<<<< HEAD
    `}};t([me()],Gn.prototype,"narrow",void 0),t([ve()],Gn.prototype,"config",void 0),t([ve()],Gn.prototype,"_saving",void 0),Gn=t([ue("smart-irrigation-view-experimental")],Gn);var Kn;!function(e){e.WeatherLocation="weather-location",e.Zones="zones",e.Distributors="distributors",e.WhenToWater="when-to-water",e.Advanced="advanced",e.Experimental="experimental",e.Help="help"}(Kn||(Kn={}));const Vn={[Kn.WeatherLocation]:"panels.setup.tabs.weather_location",[Kn.Zones]:"panels.setup.tabs.my_zones",[Kn.Distributors]:"panels.setup.tabs.distributors",[Kn.WhenToWater]:"panels.setup.tabs.when_to_water",[Kn.Advanced]:"panels.setup.tabs.advanced",[Kn.Experimental]:"panels.setup.tabs.experimental",[Kn.Help]:"panels.help.title"};let Yn=class extends(Fa(ce)){hassSubscribe(){return this._fetchConfig(),[this.hass.connection.subscribeMessage(()=>this._fetchConfig(),{type:be+"_config_updated"})]}async _fetchConfig(){if(this.hass)try{this.config=await Ei(this.hass)}catch(e){console.error("Failed to fetch setup config:",e)}}get _distributorsEnabled(){var e,t;return null!==(t=null===(e=this.config)||void 0===e?void 0:e.distributors_enabled)&&void 0!==t&&t}get _activeTab(){var e;const t=null===(e=this.path)||void 0===e?void 0:e.subpage;return Object.values(Kn).includes(null!=t?t:"")?t:Kn.WeatherLocation}_selectTab(e){Na(0,Ga("setup",e))}_openWizard(){this.dispatchEvent(new CustomEvent("open-wizard",{bubbles:!0,composed:!0}))}render(){if(!this.hass)return W``;const e=this._distributorsEnabled,t=Object.values(Kn).filter(t=>t!==Kn.Distributors||e);let i=this._activeTab;return i!==Kn.Distributors||e||(i=Kn.WeatherLocation),W`
=======
    `}};t([me()],lo.prototype,"narrow",void 0),t([ve()],lo.prototype,"config",void 0),t([ve()],lo.prototype,"_saving",void 0),lo=t([ue("smart-irrigation-view-experimental")],lo);var co;!function(e){e.WeatherLocation="weather-location",e.Zones="zones",e.Distributors="distributors",e.WhenToWater="when-to-water",e.Advanced="advanced",e.Experimental="experimental",e.Help="help"}(co||(co={}));const ho={[co.WeatherLocation]:"panels.setup.tabs.weather_location",[co.Zones]:"panels.setup.tabs.my_zones",[co.Distributors]:"panels.setup.tabs.distributors",[co.WhenToWater]:"panels.setup.tabs.when_to_water",[co.Advanced]:"panels.setup.tabs.advanced",[co.Experimental]:"panels.setup.tabs.experimental",[co.Help]:"panels.help.title"};let uo=class extends(Wa(ce)){hassSubscribe(){return this._fetchConfig(),[this.hass.connection.subscribeMessage(()=>this._fetchConfig(),{type:be+"_config_updated"})]}async _fetchConfig(){if(this.hass)try{this.config=await Ts(this.hass)}catch(e){console.error("Failed to fetch setup config:",e)}}get _distributorsEnabled(){var e,t;return null!==(t=null===(e=this.config)||void 0===e?void 0:e.distributors_enabled)&&void 0!==t&&t}get _activeTab(){var e;const t=null===(e=this.path)||void 0===e?void 0:e.subpage;return Object.values(co).includes(null!=t?t:"")?t:co.WeatherLocation}_selectTab(e){Pa(0,Va("setup",e))}_openWizard(){this.dispatchEvent(new CustomEvent("open-wizard",{bubbles:!0,composed:!0}))}render(){if(!this.hass)return W``;const e=this._distributorsEnabled,t=Object.values(co).filter(t=>t!==co.Distributors||e);let s=this._activeTab;return s!==co.Distributors||e||(s=co.WeatherLocation),W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      <div class="setup-container">
        <nav class="setup-nav">
          ${t.map(e=>W`
              <button
                class="setup-nav-btn ${i===e?"active":""}"
                @click="${()=>this._selectTab(e)}"
              >
<<<<<<< HEAD
                ${Oa(Vn[e],this.hass.language)}
=======
                ${Ma(ho[e],this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              </button>
            `)}
          <button
            class="setup-nav-btn wizard-btn"
            @click="${this._openWizard}"
<<<<<<< HEAD
            title="${Oa("wizard.title",this.hass.language)}"
          >
            <ha-icon icon="mdi:creation"></ha-icon>
            ${Oa("wizard.open_button",this.hass.language)}
=======
            title="${Ma("wizard.title",this.hass.language)}"
          >
            <ha-icon icon="mdi:creation"></ha-icon>
            ${Ma("wizard.open_button",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </button>
        </nav>
        <div class="setup-content">${this._renderContent(i)}</div>
      </div>
<<<<<<< HEAD
    `}_renderContent(e){if(!this.hass)return W``;switch(e){case Kn.WeatherLocation:return W`
=======
    `}_renderContent(e){if(!this.hass)return W``;switch(e){case co.WeatherLocation:return W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          <smart-irrigation-view-general
            .hass="${this.hass}"
            .narrow="${this.narrow}"
            section="weather-location"
          ></smart-irrigation-view-general>
          <smart-irrigation-view-weather-data
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-weather-data>
<<<<<<< HEAD
        `;case Kn.Zones:return W`<smart-irrigation-view-zone-settings
          .hass="${this.hass}"
          .narrow="${this.narrow}"
          .path="${this.path}"
        ></smart-irrigation-view-zone-settings>`;case Kn.Distributors:return W`<smart-irrigation-view-distributor-settings
          .hass="${this.hass}"
          .narrow="${this.narrow}"
          .path="${this.path}"
        ></smart-irrigation-view-distributor-settings>`;case Kn.WhenToWater:return W`
=======
        `;case co.Zones:return W`<smart-irrigation-view-zone-settings
          .hass="${this.hass}"
          .narrow="${this.narrow}"
          .path="${this.path}"
        ></smart-irrigation-view-zone-settings>`;case co.Distributors:return W`<smart-irrigation-view-distributor-settings
          .hass="${this.hass}"
          .narrow="${this.narrow}"
          .path="${this.path}"
        ></smart-irrigation-view-distributor-settings>`;case co.WhenToWater:return W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          <smart-irrigation-view-general
            .hass="${this.hass}"
            .narrow="${this.narrow}"
            section="when-to-water"
          ></smart-irrigation-view-general>
          <smart-irrigation-view-schedules
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-schedules>
<<<<<<< HEAD
        `;case Kn.Advanced:return W`
=======
        `;case co.Advanced:return W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          <smart-irrigation-view-modules
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-modules>
          <smart-irrigation-view-mappings
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-mappings>
<<<<<<< HEAD
        `;case Kn.Experimental:return W`<smart-irrigation-view-experimental
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-experimental>`;case Kn.Help:return this._renderHelp()}}_renderHelp(){return this.hass?W`
      <ha-card
        header="${Oa("panels.help.cards.how-to-get-help.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Oa("panels.help.cards.how-to-get-help.first-read-the",this.hass.language)}
          <a href="${"https://justchr.github.io/HAsmartirrigation/"}" target="_blank" rel="noopener noreferrer"
            >${Oa("panels.help.cards.how-to-get-help.wiki",this.hass.language)}</a
          >.
          ${Oa("panels.help.cards.how-to-get-help.if-you-still-need-help",this.hass.language)}
=======
        `;case co.Experimental:return W`<smart-irrigation-view-experimental
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-experimental>`;case co.Help:return this._renderHelp()}}_renderHelp(){return this.hass?W`
      <ha-card
        header="${Ma("panels.help.cards.how-to-get-help.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Ma("panels.help.cards.how-to-get-help.first-read-the",this.hass.language)}
          <a href="${"https://justchr.github.io/HAsmartirrigation/"}" target="_blank" rel="noopener noreferrer"
            >${Ma("panels.help.cards.how-to-get-help.wiki",this.hass.language)}</a
          >.
          ${Ma("panels.help.cards.how-to-get-help.if-you-still-need-help",this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          <a
            href="https://community.home-assistant.io/t/smart-irrigation-save-water-by-precisely-watering-your-lawn-garden"
            target="_blank"
            rel="noopener noreferrer"
<<<<<<< HEAD
            >${Oa("panels.help.cards.how-to-get-help.community-forum",this.hass.language)}</a
          >
          ${Oa("panels.help.cards.how-to-get-help.or-open-a",this.hass.language)}
          <a href="${"https://github.com/JustChr/HAsmartirrigation/issues"}" target="_blank" rel="noopener noreferrer"
            >${Oa("panels.help.cards.how-to-get-help.github-issue",this.hass.language)}</a
          >
          (${Oa("panels.help.cards.how-to-get-help.english-only",this.hass.language)}).
=======
            >${Ma("panels.help.cards.how-to-get-help.community-forum",this.hass.language)}</a
          >
          ${Ma("panels.help.cards.how-to-get-help.or-open-a",this.hass.language)}
          <a href="${"https://github.com/JustChr/HAsmartirrigation/issues"}" target="_blank" rel="noopener noreferrer"
            >${Ma("panels.help.cards.how-to-get-help.github-issue",this.hass.language)}</a
          >
          (${Ma("panels.help.cards.how-to-get-help.english-only",this.hass.language)}).
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </div>
      </ha-card>
    `:W``}static get styles(){return r`
      ${Ka}

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
<<<<<<< HEAD
    `}};var Xn;t([me({attribute:!1})],Yn.prototype,"hass",void 0),t([me({type:Boolean})],Yn.prototype,"narrow",void 0),t([me({attribute:!1})],Yn.prototype,"path",void 0),t([ve()],Yn.prototype,"config",void 0),Yn=t([ue("smart-irrigation-view-setup")],Yn),function(e){e[e.Welcome=0]="Welcome",e[e.Weather=1]="Weather",e[e.Module=2]="Module",e[e.Mapping=3]="Mapping",e[e.Zone=4]="Zone",e[e.Done=5]="Done"}(Xn||(Xn={}));let Jn=class extends ce{constructor(){super(...arguments),this._step=Xn.Welcome,this._saving=!1,this._error="",this._confirmClose=!1,this._siConfig=null,this._useWeather=!1,this._weatherService=Ae,this._apiKey="",this._weatherConfig=null,this._availableModules=[],this._selectedModuleIndex=0,this._moduleConfig={},this._mappingName="My Sensor Group",this._tempSource=Fe,this._humiditySource=Fe,this._precipSource=Fe,this._zoneName="My Zone",this._zoneSize="",this._zoneThroughput="",this._zoneEntity="",this._scheduleTime="06:00",this._scheduleCreated=!1,this._creatingSchedule=!1}async connectedCallback(){super.connectedCallback(),await this._loadInitialData()}async _loadInitialData(){var e;if(this.hass){try{const[t,i,s]=await Promise.all([Di(this.hass),Ui(this.hass),Ei(this.hass)]);this._availableModules=t,this._weatherConfig=i,this._siConfig=s,this._useWeather=i.use_weather_service,this._weatherService=null!==(e=i.weather_service)&&void 0!==e?e:Ae}catch(e){console.error("Wizard: failed to load initial data",e),this._error=Pa(e)}this.requestUpdate()}}_close(){this.dispatchEvent(new CustomEvent("wizard-close",{bubbles:!0,composed:!0}))}_navigate(e){this.dispatchEvent(new CustomEvent("wizard-navigate",{detail:{page:e},bubbles:!0,composed:!0}))}async _next(){this._error="";try{switch(this._saving=!0,this._step){case Xn.Welcome:this._step=Xn.Weather;break;case Xn.Weather:await this._saveWeather(),this._step=Xn.Module;break;case Xn.Module:await this._saveModule(),this._step=Xn.Mapping;break;case Xn.Mapping:await this._saveMapping(),this._step=Xn.Zone;break;case Xn.Zone:await this._saveZone(),this._step=Xn.Done;break;case Xn.Done:this._close()}}catch(e){this._error=e instanceof Error?e.message:String(e)}finally{this._saving=!1,this.requestUpdate()}}_back(){this._step>Xn.Welcome&&(this._step=this._step-1,this._error="")}get _canSkipCurrentStep(){return this._step===Xn.Weather}_skipStep(){this._canSkipCurrentStep&&this._step<Xn.Done&&(this._step=this._step+1,this._error="")}async _saveWeather(){await ji(this.hass,this._useWeather,this._useWeather?this._weatherService:null,this._apiKey||null)}async _resolveSavedId(e,t){if("number"==typeof(null==e?void 0:e.id))return e.id;try{const e=(await t()).map(e=>e.id).filter(e=>"number"==typeof e);return e.length?Math.max(...e):void 0}catch(e){return}}async _saveModule(){if(0===this._availableModules.length)throw new Error("No calculation module is available to configure. Cannot continue.");const e=this._availableModules[this._selectedModuleIndex],t=await Mi(this.hass,{name:e.name,description:e.description,config:Object.assign(Object.assign({},e.config),this._moduleConfig),schema:e.schema});if(this._savedModuleId=await this._resolveSavedId(t,()=>Hi(this.hass)),void 0===this._savedModuleId)throw new Error("The calculation module was saved but could not be linked. Please try again.")}async _saveMapping(){const e=this._useWeather?Fe:Ve,t={[Ue]:{[Ye]:this._tempSource},[Ne]:{[Ye]:this._humiditySource},[Pe]:{[Ye]:this._precipSource}},i=["Dewpoint","Evapotranspiration","Maximum Temperature","Minimum Temperature","Current Precipitation","Pressure","Solar Radiation","Windspeed"];for(const s of i)t[s]={[Ye]:e};const s=await Ni(this.hass,{name:this._mappingName,mappings:t});if(this._savedMappingId=await this._resolveSavedId(s,()=>Ii(this.hass)),void 0===this._savedMappingId)throw new Error("The sensor group was saved but could not be linked. Please try again.")}async _saveZone(){if(!this._zoneName.trim())throw new Error("Zone name is required");const e=parseFloat(this._zoneSize),t=parseFloat(this._zoneThroughput);if(!(e>0))throw new Error("Zone size must be greater than 0.");if(!(t>0))throw new Error("Throughput must be greater than 0 (zones can't water otherwise).");await Oi(this.hass,{name:this._zoneName.trim(),size:e,throughput:t,state:Wa.Automatic,duration:0,bucket:0,delta:0,explanation:"",multiplier:1,module:this._savedModuleId,mapping:this._savedMappingId,lead_time:0,linked_entity:this._zoneEntity||void 0})}async _createDefaultSchedule(){var e,t;if(!this._scheduleCreated&&!this._creatingSchedule){this._error="",this._creatingSchedule=!0;try{const i=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";await Li(this.hass,{name:Oa("wizard.steps.done.schedule_name",i)||"Daily",type:"daily",enabled:!0,time:this._scheduleTime||"06:00",action:"irrigate",zones:"all"}),this._scheduleCreated=!0}catch(e){this._error=e instanceof Error?e.message:String(e)}finally{this._creatingSchedule=!1,this.requestUpdate()}}}render(){var e,t;const i=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";return W`
=======
    `}};var po;t([me({attribute:!1})],uo.prototype,"hass",void 0),t([me({type:Boolean})],uo.prototype,"narrow",void 0),t([me({attribute:!1})],uo.prototype,"path",void 0),t([ve()],uo.prototype,"config",void 0),uo=t([ue("smart-irrigation-view-setup")],uo),function(e){e[e.Welcome=0]="Welcome",e[e.Weather=1]="Weather",e[e.Module=2]="Module",e[e.Mapping=3]="Mapping",e[e.Zone=4]="Zone",e[e.Done=5]="Done"}(po||(po={}));let go=class extends ce{constructor(){super(...arguments),this._step=po.Welcome,this._saving=!1,this._error="",this._confirmClose=!1,this._siConfig=null,this._useWeather=!1,this._weatherService=Ae,this._apiKey="",this._weatherConfig=null,this._availableModules=[],this._selectedModuleIndex=0,this._moduleConfig={},this._mappingName="My Sensor Group",this._tempSource=Fe,this._humiditySource=Fe,this._precipSource=Fe,this._zoneName="My Zone",this._zoneSize="",this._zoneThroughput="",this._zoneEntity="",this._scheduleTime="06:00",this._scheduleCreated=!1,this._creatingSchedule=!1}async connectedCallback(){super.connectedCallback(),await this._loadInitialData()}async _loadInitialData(){var e;if(this.hass){try{const[t,s,i]=await Promise.all([Is(this.hass),Fs(this.hass),Ts(this.hass)]);this._availableModules=t,this._weatherConfig=s,this._siConfig=i,this._useWeather=s.use_weather_service,this._weatherService=null!==(e=s.weather_service)&&void 0!==e?e:Ae}catch(e){console.error("Wizard: failed to load initial data",e),this._error=Ra(e)}this.requestUpdate()}}_close(){this.dispatchEvent(new CustomEvent("wizard-close",{bubbles:!0,composed:!0}))}_navigate(e){this.dispatchEvent(new CustomEvent("wizard-navigate",{detail:{page:e},bubbles:!0,composed:!0}))}async _next(){this._error="";try{switch(this._saving=!0,this._step){case po.Welcome:this._step=po.Weather;break;case po.Weather:await this._saveWeather(),this._step=po.Module;break;case po.Module:await this._saveModule(),this._step=po.Mapping;break;case po.Mapping:await this._saveMapping(),this._step=po.Zone;break;case po.Zone:await this._saveZone(),this._step=po.Done;break;case po.Done:this._close()}}catch(e){this._error=e instanceof Error?e.message:String(e)}finally{this._saving=!1,this.requestUpdate()}}_back(){this._step>po.Welcome&&(this._step=this._step-1,this._error="")}get _canSkipCurrentStep(){return this._step===po.Weather}_skipStep(){this._canSkipCurrentStep&&this._step<po.Done&&(this._step=this._step+1,this._error="")}async _saveWeather(){await Zs(this.hass,this._useWeather,this._useWeather?this._weatherService:null,this._apiKey||null)}async _resolveSavedId(e,t){if("number"==typeof(null==e?void 0:e.id))return e.id;try{const e=(await t()).map(e=>e.id).filter(e=>"number"==typeof e);return e.length?Math.max(...e):void 0}catch(e){return}}async _saveModule(){if(0===this._availableModules.length)throw new Error("No calculation module is available to configure. Cannot continue.");const e=this._availableModules[this._selectedModuleIndex],t=await Ns(this.hass,{name:e.name,description:e.description,config:Object.assign(Object.assign({},e.config),this._moduleConfig),schema:e.schema});if(this._savedModuleId=await this._resolveSavedId(t,()=>Hs(this.hass)),void 0===this._savedModuleId)throw new Error("The calculation module was saved but could not be linked. Please try again.")}async _saveMapping(){const e=this._useWeather?Fe:Ve,t={[Ue]:{[Ye]:this._tempSource},[Ne]:{[Ye]:this._humiditySource},[Le]:{[Ye]:this._precipSource}},s=["Dewpoint","Evapotranspiration","Maximum Temperature","Minimum Temperature","Current Precipitation","Pressure","Solar Radiation","Windspeed"];for(const i of s)t[i]={[Ye]:e};const i=await Ps(this.hass,{name:this._mappingName,mappings:t});if(this._savedMappingId=await this._resolveSavedId(i,()=>Ls(this.hass)),void 0===this._savedMappingId)throw new Error("The sensor group was saved but could not be linked. Please try again.")}async _saveZone(){if(!this._zoneName.trim())throw new Error("Zone name is required");const e=parseFloat(this._zoneSize),t=parseFloat(this._zoneThroughput);if(!(e>0))throw new Error("Zone size must be greater than 0.");if(!(t>0))throw new Error("Throughput must be greater than 0 (zones can't water otherwise).");await Ms(this.hass,{name:this._zoneName.trim(),size:e,throughput:t,state:Ga.Automatic,duration:0,bucket:0,delta:0,explanation:"",multiplier:1,module:this._savedModuleId,mapping:this._savedMappingId,lead_time:0,linked_entity:this._zoneEntity||void 0})}async _createDefaultSchedule(){var e,t;if(!this._scheduleCreated&&!this._creatingSchedule){this._error="",this._creatingSchedule=!0;try{const s=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";await Bs(this.hass,{name:Ma("wizard.steps.done.schedule_name",s)||"Daily",type:"daily",enabled:!0,time:this._scheduleTime||"06:00",action:"irrigate",zones:"all"}),this._scheduleCreated=!0}catch(e){this._error=e instanceof Error?e.message:String(e)}finally{this._creatingSchedule=!1,this.requestUpdate()}}}render(){var e,t;const s=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";return W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      <div class="wizard-overlay" @click="${this._onOverlayClick}">
        <div
          class="wizard-dialog"
          @click="${e=>e.stopPropagation()}"
        >
          <div class="wizard-header">
<<<<<<< HEAD
            <span class="wizard-title">${Oa("wizard.title",i)}</span>
            <button
              class="wizard-close-btn"
              @click="${this._close}"
              title="${Oa("wizard.close",i)}"
              aria-label="${Oa("wizard.close",i)}"
=======
            <span class="wizard-title">${Ma("wizard.title",s)}</span>
            <button
              class="wizard-close-btn"
              @click="${this._close}"
              title="${Ma("wizard.close",s)}"
              aria-label="${Ma("wizard.close",s)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            >
              <ha-icon icon="mdi:close"></ha-icon>
            </button>
          </div>
<<<<<<< HEAD
          ${this._step!==Xn.Welcome&&this._step!==Xn.Done?W`<div class="wizard-stepper">${this._renderStepper()}</div>`:""}
=======
          ${this._step!==po.Welcome&&this._step!==po.Done?W`<div class="wizard-stepper">${this._renderStepper()}</div>`:""}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          <div class="wizard-body">
            ${this._renderStep(i)}
            ${this._error?W`<div class="wizard-error">${this._error}</div>`:""}
          </div>
          <div class="wizard-footer">${this._renderFooter(i)}</div>
          ${this._confirmClose?W`
                <div class="wizard-confirm-close">
                  <div class="wizard-confirm-box">
<<<<<<< HEAD
                    <p>${Oa("wizard.confirm_close.body",i)}</p>
=======
                    <p>${Ma("wizard.confirm_close.body",s)}</p>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    <div class="wizard-confirm-actions">
                      <button
                        class="wizard-btn secondary"
                        @click="${()=>{this._confirmClose=!1}}"
                      >
<<<<<<< HEAD
                        ${Oa("wizard.confirm_close.keep",i)}
=======
                        ${Ma("wizard.confirm_close.keep",s)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                      </button>
                      <button
                        class="wizard-btn primary"
                        @click="${()=>{this._confirmClose=!1,this._close()}}"
                      >
<<<<<<< HEAD
                        ${Oa("wizard.confirm_close.close",i)}
=======
                        ${Ma("wizard.confirm_close.close",s)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                      </button>
                    </div>
                  </div>
                </div>
              `:""}
        </div>
      </div>
<<<<<<< HEAD
    `}_onOverlayClick(e){e.target===e.currentTarget&&(this._step>Xn.Welcome&&this._step<Xn.Done?this._confirmClose=!0:this._close())}_renderStepper(){var e,t;const i=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en",s=[Oa("wizard.stepper.weather",i),Oa("wizard.stepper.module",i),Oa("wizard.stepper.mapping",i),Oa("wizard.stepper.zone",i)];return W`
      ${s.map((e,t)=>{const i=t+1,a=this._step===i,n=this._step>i;return W`
=======
    `}_onOverlayClick(e){e.target===e.currentTarget&&(this._step>po.Welcome&&this._step<po.Done?this._confirmClose=!0:this._close())}_renderStepper(){var e,t;const s=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en",i=[Ma("wizard.stepper.weather",s),Ma("wizard.stepper.module",s),Ma("wizard.stepper.mapping",s),Ma("wizard.stepper.zone",s)];return W`
      ${i.map((e,t)=>{const s=t+1,a=this._step===s,n=this._step>s;return W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          <div
            class="stepper-step ${a?"active":""} ${n?"done":""}"
          >
            <div class="stepper-circle">${n?"✓":i}</div>
            <span class="stepper-label">${e}</span>
          </div>
          ${t<s.length-1?W`<div class="stepper-line ${n?"done":""}"></div>`:""}
        `})}
<<<<<<< HEAD
    `}_renderStep(e){switch(this._step){case Xn.Welcome:return this._renderWelcome(e);case Xn.Weather:return this._renderWeather(e);case Xn.Module:return this._renderModule(e);case Xn.Mapping:return this._renderMapping(e);case Xn.Zone:return this._renderZone(e);case Xn.Done:return this._renderDone(e);default:return W``}}_renderFooter(e){return this._step===Xn.Done?W``:W`
      <div class="footer-left">
        ${this._step>Xn.Welcome?W`<button
=======
    `}_renderStep(e){switch(this._step){case po.Welcome:return this._renderWelcome(e);case po.Weather:return this._renderWeather(e);case po.Module:return this._renderModule(e);case po.Mapping:return this._renderMapping(e);case po.Zone:return this._renderZone(e);case po.Done:return this._renderDone(e);default:return W``}}_renderFooter(e){return this._step===po.Done?W``:W`
      <div class="footer-left">
        ${this._step>po.Welcome?W`<button
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
              class="wizard-btn secondary"
              @click="${this._back}"
              ?disabled="${this._saving}"
            >
<<<<<<< HEAD
              ${Oa("wizard.back",e)}
=======
              ${Ma("wizard.back",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </button>`:""}
        ${this._canSkipCurrentStep?W`<button
              class="wizard-btn ghost"
              @click="${this._skipStep}"
              ?disabled="${this._saving}"
            >
<<<<<<< HEAD
              ${Oa("wizard.skip_step",e)}
=======
              ${Ma("wizard.skip_step",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
            </button>`:""}
      </div>
      <button
        class="wizard-btn primary"
        @click="${this._next}"
        ?disabled="${this._saving}"
      >
<<<<<<< HEAD
        ${this._saving?Oa("common.saving-messages.saving",e):this._step===Xn.Welcome||this._step<Xn.Zone?Oa("wizard.next",e):Oa("wizard.finish",e)}
      </button>
    `}_renderWelcome(e){return W`
      <h2 class="step-title">
        ${Oa("wizard.steps.welcome.title",e)}
      </h2>
      <p class="step-desc">${Oa("wizard.steps.welcome.intro",e)}</p>
      <ul class="step-list">
        <li>① ${Oa("wizard.steps.welcome.step1_label",e)}</li>
        <li>② ${Oa("wizard.steps.welcome.step2_label",e)}</li>
        <li>③ ${Oa("wizard.steps.welcome.step3_label",e)}</li>
        <li>④ ${Oa("wizard.steps.welcome.step4_label",e)}</li>
      </ul>
      <p class="step-tip">${Oa("wizard.steps.welcome.tip",e)}</p>
    `}_renderWeather(e){return W`
      <h2 class="step-title">
        ${Oa("wizard.steps.weather.title",e)}
      </h2>
      <p class="step-desc">
        ${Oa("wizard.steps.weather.description",e)}
=======
        ${this._saving?Ma("common.saving-messages.saving",e):this._step===po.Welcome||this._step<po.Zone?Ma("wizard.next",e):Ma("wizard.finish",e)}
      </button>
    `}_renderWelcome(e){return W`
      <h2 class="step-title">
        ${Ma("wizard.steps.welcome.title",e)}
      </h2>
      <p class="step-desc">${Ma("wizard.steps.welcome.intro",e)}</p>
      <ul class="step-list">
        <li>① ${Ma("wizard.steps.welcome.step1_label",e)}</li>
        <li>② ${Ma("wizard.steps.welcome.step2_label",e)}</li>
        <li>③ ${Ma("wizard.steps.welcome.step3_label",e)}</li>
        <li>④ ${Ma("wizard.steps.welcome.step4_label",e)}</li>
      </ul>
      <p class="step-tip">${Ma("wizard.steps.welcome.tip",e)}</p>
    `}_renderWeather(e){return W`
      <h2 class="step-title">
        ${Ma("wizard.steps.weather.title",e)}
      </h2>
      <p class="step-desc">
        ${Ma("wizard.steps.weather.description",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      </p>

      <si-weather-source-config
        .hass="${this.hass}"
        .useWeather="${this._useWeather}"
        .service="${this._weatherService}"
        .apiKey="${this._apiKey}"
        .weatherConfig="${this._weatherConfig}"
        @useweather-changed="${e=>{this._useWeather=e.detail.value}}"
        @service-changed="${e=>{this._weatherService=e.detail.value}}"
        @apikey-changed="${e=>{this._apiKey=e.detail.value}}"
      ></si-weather-source-config>
    `}_renderModule(e){if(0===this._availableModules.length)return W`
        <h2 class="step-title">
<<<<<<< HEAD
          ${Oa("wizard.steps.module.title",e)}
        </h2>
        <p class="step-desc">
          ${Oa("wizard.steps.module.no_modules",e)}
        </p>
      `;const t=this._availableModules[this._selectedModuleIndex];return W`
      <h2 class="step-title">${Oa("wizard.steps.module.title",e)}</h2>
      <p class="step-desc">
        ${Oa("wizard.steps.module.description",e)}
      </p>

      <si-field
        label="${Oa("wizard.steps.module.pick_label",e)}"
=======
          ${Ma("wizard.steps.module.title",e)}
        </h2>
        <p class="step-desc">
          ${Ma("wizard.steps.module.no_modules",e)}
        </p>
      `;const t=this._availableModules[this._selectedModuleIndex];return W`
      <h2 class="step-title">${Ma("wizard.steps.module.title",e)}</h2>
      <p class="step-desc">
        ${Ma("wizard.steps.module.description",e)}
      </p>

      <si-field
        label="${Ma("wizard.steps.module.pick_label",e)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        required
      >
        <select
          class="wizard-input"
          @change="${e=>{this._selectedModuleIndex=parseInt(e.target.value),this._moduleConfig={}}}"
        >
          ${this._availableModules.map((e,t)=>W`
              <option
                value="${t}"
                ?selected="${t===this._selectedModuleIndex}"
              >
                ${e.name}
              </option>
            `)}
        </select>
      </si-field>

      ${(null==t?void 0:t.description)?W`<p class="module-desc">${t.description}</p>`:""}
      ${(null==t?void 0:t.schema)&&Array.isArray(t.schema)&&t.schema.length>0?W`
            <div class="schema-fields">
              ${t.schema.map(e=>this._renderModuleField(e.name,e))}
            </div>
          `:""}
    `}_renderModuleField(e,t){var i,s;const a=e.replace(/_/g," ").replace(/\b\w/g,e=>e.toUpperCase()),n=null!==(s=null!==(i=this._moduleConfig[e])&&void 0!==i?i:t.default)&&void 0!==s?s:"",o=t.description;return"boolean"===t.type?W`
        <si-field label="${a}" help="${null!=o?o:""}">
          <ha-switch
            .checked="${Boolean(n)}"
            @change="${t=>{this._moduleConfig=Object.assign(Object.assign({},this._moduleConfig),{[e]:t.target.checked})}}"
          ></ha-switch>
        </si-field>
      `:"select"===t.type&&t.options?W`
        <si-field label="${a}" help="${null!=o?o:""}">
          <select
            class="wizard-input"
            @change="${t=>{this._moduleConfig=Object.assign(Object.assign({},this._moduleConfig),{[e]:t.target.value})}}"
          >
            ${t.options.map(([e,t])=>W`<option
                  value="${e}"
                  ?selected="${e===String(n)}"
                >
                  ${t}
                </option>`)}
          </select>
        </si-field>
      `:W`
      <si-field label="${a}" help="${null!=o?o:""}">
        <input
          type="${"float"===t.type||"integer"===t.type?"number":"text"}"
          class="wizard-input"
          step="${"float"===t.type?"0.01":"1"}"
          .value="${String(n)}"
          @input="${i=>{const s=i.target.value,a="float"===t.type?parseFloat(s):"integer"===t.type?parseInt(s):s;this._moduleConfig=Object.assign(Object.assign({},this._moduleConfig),{[e]:a})}}"
        />
      </si-field>
<<<<<<< HEAD
    `}_renderMapping(e){const t=[{value:Fe,label:Oa("wizard.steps.mapping.use_weather_service",e)},{value:"sensor",label:Oa("wizard.steps.mapping.use_sensor",e)},{value:"static",label:Oa("wizard.steps.mapping.use_static",e)},{value:Ve,label:Oa("wizard.steps.mapping.use_none",e)}],i=(i,s,a)=>W`
      <si-field
        label="${Oa("wizard.steps.mapping.source_label",e)} ${i}"
=======
    `}_renderMapping(e){const t=[{value:Fe,label:Ma("wizard.steps.mapping.use_weather_service",e)},{value:"sensor",label:Ma("wizard.steps.mapping.use_sensor",e)},{value:"static",label:Ma("wizard.steps.mapping.use_static",e)},{value:Ve,label:Ma("wizard.steps.mapping.use_none",e)}],s=(s,i,a)=>W`
      <si-field
        label="${Ma("wizard.steps.mapping.source_label",e)} ${s}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      >
        <select
          class="wizard-input"
          @change="${e=>a(e.target.value)}"
        >
          ${t.map(e=>W`<option value="${e.value}" ?selected="${e.value===s}">
                ${e.label}
              </option>`)}
        </select>
      </si-field>
    `;return W`
      <h2 class="step-title">
<<<<<<< HEAD
        ${Oa("wizard.steps.mapping.title",e)}
      </h2>
      <p class="step-desc">
        ${Oa("wizard.steps.mapping.description",e)}
      </p>

      <si-field
        label="${Oa("wizard.steps.mapping.name_label",e)}"
=======
        ${Ma("wizard.steps.mapping.title",e)}
      </h2>
      <p class="step-desc">
        ${Ma("wizard.steps.mapping.description",e)}
      </p>

      <si-field
        label="${Ma("wizard.steps.mapping.name_label",e)}"
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        required
      >
        <input
          type="text"
          class="wizard-input"
          .value="${this._mappingName}"
          @input="${e=>{this._mappingName=e.target.value}}"
        />
      </si-field>

<<<<<<< HEAD
      ${i(Oa("panels.mappings.cards.mapping.items.temperature",e)||"Temperature",this._tempSource,e=>{this._tempSource=e,this.requestUpdate()})}
      ${i(Oa("panels.mappings.cards.mapping.items.humidity",e)||"Humidity",this._humiditySource,e=>{this._humiditySource=e,this.requestUpdate()})}
      ${i(Oa("panels.mappings.cards.mapping.items.precipitation",e)||"Precipitation",this._precipSource,e=>{this._precipSource=e,this.requestUpdate()})}

      <p class="step-tip">
        ${Oa("wizard.steps.mapping.description",e)}
      </p>
    `}_renderZone(e){var t;const i="imperial"!==(null===(t=this._siConfig)||void 0===t?void 0:t.units);return W`
      <h2 class="step-title">${Oa("wizard.steps.zone.title",e)}</h2>
      <p class="step-desc">
        ${Oa("wizard.steps.zone.description",e)}
=======
      ${s(Ma("panels.mappings.cards.mapping.items.temperature",e)||"Temperature",this._tempSource,e=>{this._tempSource=e,this.requestUpdate()})}
      ${s(Ma("panels.mappings.cards.mapping.items.humidity",e)||"Humidity",this._humiditySource,e=>{this._humiditySource=e,this.requestUpdate()})}
      ${s(Ma("panels.mappings.cards.mapping.items.precipitation",e)||"Precipitation",this._precipSource,e=>{this._precipSource=e,this.requestUpdate()})}

      <p class="step-tip">
        ${Ma("wizard.steps.mapping.description",e)}
      </p>
    `}_renderZone(e){var t;const s="imperial"!==(null===(t=this._siConfig)||void 0===t?void 0:t.units);return W`
      <h2 class="step-title">${Ma("wizard.steps.zone.title",e)}</h2>
      <p class="step-desc">
        ${Ma("wizard.steps.zone.description",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      </p>

      <si-zone-form
        .hass="${this.hass}"
        .metric="${i}"
        .name="${this._zoneName}"
        .size="${this._zoneSize}"
        .throughput="${this._zoneThroughput}"
        .linkedEntity="${this._zoneEntity}"
        showEntity
        @name-changed="${e=>{this._zoneName=e.detail.value}}"
        @size-changed="${e=>{this._zoneSize=e.detail.value}}"
        @throughput-changed="${e=>{this._zoneThroughput=e.detail.value}}"
        @entity-changed="${e=>{this._zoneEntity=e.detail.value}}"
      ></si-zone-form>
    `}_renderDone(e){return W`
      <div class="done-wrapper">
        <div class="done-icon">
          <ha-icon icon="mdi:check-circle"></ha-icon>
        </div>
<<<<<<< HEAD
        <h2 class="step-title">${Oa("wizard.steps.done.title",e)}</h2>
        <p class="step-desc">
          ${Oa("wizard.steps.done.description",e)}
        </p>
        <ul class="step-list">
          <li>${Oa("wizard.steps.done.tip1",e)}</li>
          <li>${Oa("wizard.steps.done.tip2",e)}</li>
          <li>${Oa("wizard.steps.done.tip3",e)}</li>
=======
        <h2 class="step-title">${Ma("wizard.steps.done.title",e)}</h2>
        <p class="step-desc">
          ${Ma("wizard.steps.done.description",e)}
        </p>
        <ul class="step-list">
          <li>${Ma("wizard.steps.done.tip1",e)}</li>
          <li>${Ma("wizard.steps.done.tip2",e)}</li>
          <li>${Ma("wizard.steps.done.tip3",e)}</li>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
        </ul>

        <div class="schedule-offer">
          ${this._scheduleCreated?W`
                <div class="schedule-created">
                  <ha-icon icon="mdi:calendar-check"></ha-icon>
                  <span
<<<<<<< HEAD
                    >${Oa("wizard.steps.done.schedule_created",e)}</span
=======
                    >${Ma("wizard.steps.done.schedule_created",e)}</span
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  >
                </div>
              `:W`
                <p class="schedule-offer-title">
<<<<<<< HEAD
                  ${Oa("wizard.steps.done.schedule_title",e)}
                </p>
                <p class="schedule-offer-desc">
                  ${Oa("wizard.steps.done.schedule_desc",e)}
=======
                  ${Ma("wizard.steps.done.schedule_title",e)}
                </p>
                <p class="schedule-offer-desc">
                  ${Ma("wizard.steps.done.schedule_desc",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                </p>
                <div class="schedule-offer-row">
                  <input
                    type="time"
                    class="wizard-input"
                    .value="${this._scheduleTime}"
                    @change="${e=>{this._scheduleTime=e.target.value}}"
                  />
                  <button
                    class="wizard-btn primary"
                    @click="${this._createDefaultSchedule}"
                    ?disabled="${this._creatingSchedule}"
                  >
<<<<<<< HEAD
                    ${this._creatingSchedule?Oa("common.saving-messages.saving",e):Oa("wizard.steps.done.schedule_create",e)}
=======
                    ${this._creatingSchedule?Ma("common.saving-messages.saving",e):Ma("wizard.steps.done.schedule_create",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                  </button>
                </div>
              `}
        </div>

        <div class="done-actions">
          <button
            class="wizard-btn primary"
            @click="${()=>{this._close(),this._navigate("zones")}}"
          >
<<<<<<< HEAD
            ${Oa("wizard.steps.done.go_zones",e)}
=======
            ${Ma("wizard.steps.done.go_zones",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </button>
          <button
            class="wizard-btn secondary"
            @click="${()=>{this._close(),this._navigate("setup")}}"
          >
<<<<<<< HEAD
            ${Oa("wizard.steps.done.go_setup",e)}
=======
            ${Ma("wizard.steps.done.go_setup",e)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          </button>
        </div>
      </div>
    `}static get styles(){return r`
      ${Ka}

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

      /* Default-schedule offer on the Done step */
      .schedule-offer {
        text-align: left;
        background: var(--secondary-background-color);
        border-radius: 8px;
        padding: 14px 16px;
        margin-top: 8px;
      }

      .schedule-offer-title {
        margin: 0 0 4px;
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--primary-text-color);
      }

      .schedule-offer-desc {
        margin: 0 0 12px;
        font-size: 0.83rem;
        color: var(--secondary-text-color);
        line-height: 1.45;
      }

      .schedule-offer-row {
        display: flex;
        gap: 10px;
        align-items: center;
        flex-wrap: wrap;
      }

      .schedule-offer-row .wizard-input {
        width: auto;
        flex: 0 0 auto;
      }

      .schedule-created {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #2e7d32;
        font-weight: 500;
        font-size: 0.9rem;
      }

      .schedule-created ha-icon {
        --mdc-icon-size: 22px;
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
<<<<<<< HEAD
    `}};t([me({attribute:!1})],Jn.prototype,"hass",void 0),t([ve()],Jn.prototype,"_step",void 0),t([ve()],Jn.prototype,"_saving",void 0),t([ve()],Jn.prototype,"_error",void 0),t([ve()],Jn.prototype,"_confirmClose",void 0),t([ve()],Jn.prototype,"_siConfig",void 0),t([ve()],Jn.prototype,"_useWeather",void 0),t([ve()],Jn.prototype,"_weatherService",void 0),t([ve()],Jn.prototype,"_apiKey",void 0),t([ve()],Jn.prototype,"_weatherConfig",void 0),t([ve()],Jn.prototype,"_availableModules",void 0),t([ve()],Jn.prototype,"_selectedModuleIndex",void 0),t([ve()],Jn.prototype,"_moduleConfig",void 0),t([ve()],Jn.prototype,"_mappingName",void 0),t([ve()],Jn.prototype,"_tempSource",void 0),t([ve()],Jn.prototype,"_humiditySource",void 0),t([ve()],Jn.prototype,"_precipSource",void 0),t([ve()],Jn.prototype,"_zoneName",void 0),t([ve()],Jn.prototype,"_zoneSize",void 0),t([ve()],Jn.prototype,"_zoneThroughput",void 0),t([ve()],Jn.prototype,"_zoneEntity",void 0),t([ve()],Jn.prototype,"_scheduleTime",void 0),t([ve()],Jn.prototype,"_scheduleCreated",void 0),t([ve()],Jn.prototype,"_creatingSchedule",void 0),Jn=t([ue("si-setup-wizard")],Jn);const Qn=Ka;var eo;!function(e){e.Zones="zones",e.Setup="setup"}(eo||(eo={})),e.SmartIrrigationPanel=class extends ce{constructor(){super(...arguments),this._wizardOpen=!1,this._updateScheduled=!1,this._lastNavigationTime=0,this._navigationThrottleDelay=100}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}async firstUpdated(){const e=qa().page;Object.values(eo).includes(e)||Na(0,Ga(eo.Zones)),window.addEventListener("location-changed",()=>{if(!window.location.pathname.includes("smart-irrigation"))return;const e=performance.now();e-this._lastNavigationTime<this._navigationThrottleDelay||(this._lastNavigationTime=e,this._scheduleUpdate())}),qi().then(()=>{this._scheduleUpdate()}).catch(e=>{console.error("Failed to load HA form elements:",e),this._scheduleUpdate()}),this.hass&&Ei(this.hass).then(e=>{this._config=e,this._scheduleUpdate()}).catch(e=>{console.error("Failed to fetch config for version display:",e)})}_ensureLanguage(){this.hass&&!Ta(this.hass.language)&&function(e){const t=Ca(e);return Ta(e)?Promise.resolve():(Ea[t]||(Ea[t]=fetch(`/smart_irrigation_static/languages/${t}.json?v=${_e}`).then(e=>e.ok?e.json():Promise.reject(e.status)).then(e=>{Aa[t]=e}).catch(()=>{Aa[t]=Aa.en})),Ea[t])}(this.hass.language).then(()=>this.requestUpdate())}render(){var e,t;if(this.hass&&!Ta(this.hass.language))return this._ensureLanguage(),W``;const i=qa(),s=!!customElements.get("ha-tab-group"),a=!!customElements.get("ha-tab-group-tab");return W`
=======
    `}};t([me({attribute:!1})],go.prototype,"hass",void 0),t([ve()],go.prototype,"_step",void 0),t([ve()],go.prototype,"_saving",void 0),t([ve()],go.prototype,"_error",void 0),t([ve()],go.prototype,"_confirmClose",void 0),t([ve()],go.prototype,"_siConfig",void 0),t([ve()],go.prototype,"_useWeather",void 0),t([ve()],go.prototype,"_weatherService",void 0),t([ve()],go.prototype,"_apiKey",void 0),t([ve()],go.prototype,"_weatherConfig",void 0),t([ve()],go.prototype,"_availableModules",void 0),t([ve()],go.prototype,"_selectedModuleIndex",void 0),t([ve()],go.prototype,"_moduleConfig",void 0),t([ve()],go.prototype,"_mappingName",void 0),t([ve()],go.prototype,"_tempSource",void 0),t([ve()],go.prototype,"_humiditySource",void 0),t([ve()],go.prototype,"_precipSource",void 0),t([ve()],go.prototype,"_zoneName",void 0),t([ve()],go.prototype,"_zoneSize",void 0),t([ve()],go.prototype,"_zoneThroughput",void 0),t([ve()],go.prototype,"_zoneEntity",void 0),t([ve()],go.prototype,"_scheduleTime",void 0),t([ve()],go.prototype,"_scheduleCreated",void 0),t([ve()],go.prototype,"_creatingSchedule",void 0),go=t([ue("si-setup-wizard")],go);const mo=Ya;var vo;!function(e){e.Zones="zones",e.Setup="setup"}(vo||(vo={})),e.SmartIrrigationPanel=class extends ce{constructor(){super(...arguments),this._wizardOpen=!1,this._updateScheduled=!1,this._lastNavigationTime=0,this._navigationThrottleDelay=100}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}async firstUpdated(){const e=Ka().page;Object.values(vo).includes(e)||Pa(0,Va(vo.Zones)),window.addEventListener("location-changed",()=>{if(!window.location.pathname.includes("smart-irrigation"))return;const e=performance.now();e-this._lastNavigationTime<this._navigationThrottleDelay||(this._lastNavigationTime=e,this._scheduleUpdate())}),Ks().then(()=>{this._scheduleUpdate()}).catch(e=>{console.error("Failed to load HA form elements:",e),this._scheduleUpdate()}),this.hass&&Ts(this.hass).then(e=>{this._config=e,this._scheduleUpdate()}).catch(e=>{console.error("Failed to fetch config for version display:",e)})}_ensureLanguage(){this.hass&&!Da(this.hass.language)&&function(e){const t=Oa(e);return Da(e)?Promise.resolve():(Ta[t]||(Ta[t]=fetch(`/smart_irrigation_static/languages/${t}.json?v=${_e}`).then(e=>e.ok?e.json():Promise.reject(e.status)).then(e=>{Ea[t]=e}).catch(()=>{Ea[t]=Ea.en})),Ta[t])}(this.hass.language).then(()=>this.requestUpdate())}render(){var e,t;if(this.hass&&!Da(this.hass.language))return this._ensureLanguage(),W``;const s=Ka(),i=!!customElements.get("ha-tab-group"),a=!!customElements.get("ha-tab-group-tab");return W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
      <div class="header">
        <div class="toolbar">
          <ha-menu-button
            .hass=${this.hass}
            .narrow=${this.narrow}
          ></ha-menu-button>
<<<<<<< HEAD
          <div class="main-title">${Oa("title",this.hass.language)}</div>
=======
          <div class="main-title">${Ma("title",this.hass.language)}</div>
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
          <div class="version">${null!==(t=null===(e=this._config)||void 0===e?void 0:e.version)&&void 0!==t?t:_e}</div>
        </div>

        ${s&&a?W`
              <ha-tab-group @wa-tab-show=${this.handlePageSelected}>
<<<<<<< HEAD
                ${Object.values(eo).map(e=>W`
=======
                ${Object.values(vo).map(e=>W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    <ha-tab-group-tab
                      slot="nav"
                      panel="${e}"
                      .active=${i.page===e}
                    >
<<<<<<< HEAD
                      ${Oa(`panels.${e}.title`,this.hass.language)}
=======
                      ${Ma(`panels.${e}.title`,this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    </ha-tab-group-tab>
                  `)}
              </ha-tab-group>
            `:W`
              <div class="custom-tabs">
<<<<<<< HEAD
                ${Object.values(eo).map(e=>W`
=======
                ${Object.values(vo).map(e=>W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    <button
                      class="custom-tab ${i.page===e?"active":""}"
                      @click=${()=>this.navigateToPage(e)}
                    >
<<<<<<< HEAD
                      ${Oa(`panels.${e}.title`,this.hass.language)}
=======
                      ${Ma(`panels.${e}.title`,this.hass.language)}
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
                    </button>
                  `)}
              </div>
            `}
      </div>
      <div class="view">${this.getView(i)}</div>
      ${this._wizardOpen?W`
            <si-setup-wizard
              .hass="${this.hass}"
              @wizard-close="${()=>{this._wizardOpen=!1}}"
              @wizard-navigate="${e=>{var t,i;const s=null!==(i=null===(t=e.detail)||void 0===t?void 0:t.page)&&void 0!==i?i:"zones";this._wizardOpen=!1,this.navigateToPage(s)}}"
            ></si-setup-wizard>
          `:""}
    `}getView(e){switch(e.page){case"zones":default:return W`
          <smart-irrigation-view-zones
            .hass=${this.hass}
            .narrow=${this.narrow}
            .path=${e}
            @open-wizard="${()=>{this._wizardOpen=!0}}"
          ></smart-irrigation-view-zones>
        `;case"setup":return W`
          <smart-irrigation-view-setup
            .hass=${this.hass}
            .narrow=${this.narrow}
            .path=${e}
            @open-wizard="${()=>{this._wizardOpen=!0}}"
          ></smart-irrigation-view-setup>
<<<<<<< HEAD
        `}}navigateToPage(e){if(e!==qa().page){const t=Ga(e);Na(0,t),this.requestUpdate()}else scrollTo(0,0)}handlePageSelected(e){const t=e.detail.name;if(t!==qa().page){const e=Ga(t);Na(0,e),this.requestUpdate()}else scrollTo(0,0)}static get styles(){return[Qn,r`
=======
        `}}navigateToPage(e){if(e!==Ka().page){const t=Va(e);Pa(0,t),this.requestUpdate()}else scrollTo(0,0)}handlePageSelected(e){const t=e.detail.name;if(t!==Ka().page){const e=Va(t);Pa(0,e),this.requestUpdate()}else scrollTo(0,0)}static get styles(){return[mo,r`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
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
<<<<<<< HEAD
      `]}},t([me({attribute:!1})],e.SmartIrrigationPanel.prototype,"hass",void 0),t([me({type:Boolean,reflect:!0})],e.SmartIrrigationPanel.prototype,"narrow",void 0),t([ve()],e.SmartIrrigationPanel.prototype,"_wizardOpen",void 0),t([ve()],e.SmartIrrigationPanel.prototype,"_config",void 0),e.SmartIrrigationPanel=t([ue("smart-irrigation")],e.SmartIrrigationPanel);let to=class extends ce{async showDialog(e){this._params=e,await this.updateComplete}async closeDialog(){this._params=void 0}render(){return this._params?W`
=======
      `]}},t([me({attribute:!1})],e.SmartIrrigationPanel.prototype,"hass",void 0),t([me({type:Boolean,reflect:!0})],e.SmartIrrigationPanel.prototype,"narrow",void 0),t([ve()],e.SmartIrrigationPanel.prototype,"_wizardOpen",void 0),t([ve()],e.SmartIrrigationPanel.prototype,"_config",void 0),e.SmartIrrigationPanel=t([ue("smart-irrigation")],e.SmartIrrigationPanel);let fo=class extends ce{async showDialog(e){this._params=e,await this.updateComplete}async closeDialog(){this._params=void 0}render(){return this._params?W`
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
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
              .path=${Ua}
            ></ha-icon-button>
            <span class="errortitle" slot="title">
              ${this.hass.localize("state_badge.default.error")}
            </span>
          </ha-header-bar>
        </div>
        <div class="wrapper">${this._params.error||""}</div>

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
    `:W``}static get styles(){return r`
      div.wrapper {
        color: var(--primary-text-color);
      }
      span.errortitle {
        font-size: 2em;
        font-weight: bold;
        vertical-align: bottom;
      }
<<<<<<< HEAD
    `}};t([me({attribute:!1})],to.prototype,"hass",void 0),t([ve()],to.prototype,"_params",void 0),to=t([ue("error-dialog")],to);var io=Object.freeze({__proto__:null,get ErrorDialog(){return to}})}({});
=======
    `}};t([me({attribute:!1})],fo.prototype,"hass",void 0),t([ve()],fo.prototype,"_params",void 0),fo=t([ue("error-dialog")],fo);var _o=Object.freeze({__proto__:null,get ErrorDialog(){return fo}})}({});
>>>>>>> d1b69a7 (feat(schedules): resolve solar-azimuth bounds on the run-window dial)
