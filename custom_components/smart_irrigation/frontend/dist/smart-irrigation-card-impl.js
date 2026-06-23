!function(e){"use strict";function t(e,t,i,n){var r,a=arguments.length,o=a<3?t:null===n?n=Object.getOwnPropertyDescriptor(t,i):n;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)o=Reflect.decorate(e,t,i,n);else for(var s=e.length-1;s>=0;s--)(r=e[s])&&(o=(a<3?r(o):a>3?r(t,i,o):r(t,i))||o);return a>3&&o&&Object.defineProperty(t,i,o),o}"function"==typeof SuppressedError&&SuppressedError;
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const i=globalThis,n=i.ShadowRoot&&(void 0===i.ShadyCSS||i.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,r=Symbol(),a=new WeakMap;let o=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==r)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(n&&void 0===e){const i=void 0!==t&&1===t.length;i&&(e=a.get(t)),void 0===e&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&a.set(t,e))}return e}toString(){return this.cssText}};const s=(e,...t)=>{const i=1===e.length?e[0]:t.reduce((t,i,n)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+e[n+1],e[0]);return new o(i,e,r)},l=n?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const i of e.cssRules)t+=i.cssText;return(e=>new o("string"==typeof e?e:e+"",void 0,r))(t)})(e):e,{is:c,defineProperty:h,getOwnPropertyDescriptor:u,getOwnPropertyNames:d,getOwnPropertySymbols:p,getPrototypeOf:g}=Object,m=globalThis,f=m.trustedTypes,b=f?f.emptyScript:"",_=m.reactiveElementPolyfillSupport,y=(e,t)=>e,v={toAttribute(e,t){switch(t){case Boolean:e=e?b:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute(e,t){let i=e;switch(t){case Boolean:i=null!==e;break;case Number:i=null===e?null:Number(e);break;case Object:case Array:try{i=JSON.parse(e)}catch(e){i=null}}return i}},w=(e,t)=>!c(e,t),k={attribute:!0,type:String,converter:v,reflect:!1,useDefault:!1,hasChanged:w};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */Symbol.metadata??=Symbol("metadata"),m.litPropertyMetadata??=new WeakMap;let x=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=k){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const i=Symbol(),n=this.getPropertyDescriptor(e,i,t);void 0!==n&&h(this.prototype,e,n)}}static getPropertyDescriptor(e,t,i){const{get:n,set:r}=u(this.prototype,e)??{get(){return this[t]},set(e){this[t]=e}};return{get:n,set(t){const a=n?.call(this);r?.call(this,t),this.requestUpdate(e,a,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??k}static _$Ei(){if(this.hasOwnProperty(y("elementProperties")))return;const e=g(this);e.finalize(),void 0!==e.l&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(y("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(y("properties"))){const e=this.properties,t=[...d(e),...p(e)];for(const i of t)this.createProperty(i,e[i])}const e=this[Symbol.metadata];if(null!==e){const t=litPropertyMetadata.get(e);if(void 0!==t)for(const[e,i]of t)this.elementProperties.set(e,i)}this._$Eh=new Map;for(const[e,t]of this.elementProperties){const i=this._$Eu(e,t);void 0!==i&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const i=new Set(e.flat(1/0).reverse());for(const e of i)t.unshift(l(e))}else void 0!==e&&t.push(l(e));return t}static _$Eu(e,t){const i=t.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof e?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),void 0!==this.renderRoot&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((e,t)=>{if(n)e.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(const n of t){const t=document.createElement("style"),r=i.litNonce;void 0!==r&&t.setAttribute("nonce",r),t.textContent=n.cssText,e.appendChild(t)}})(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){const i=this.constructor.elementProperties.get(e),n=this.constructor._$Eu(e,i);if(void 0!==n&&!0===i.reflect){const r=(void 0!==i.converter?.toAttribute?i.converter:v).toAttribute(t,i.type);this._$Em=e,null==r?this.removeAttribute(n):this.setAttribute(n,r),this._$Em=null}}_$AK(e,t){const i=this.constructor,n=i._$Eh.get(e);if(void 0!==n&&this._$Em!==n){const e=i.getPropertyOptions(n),r="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==e.converter?.fromAttribute?e.converter:v;this._$Em=n;const a=r.fromAttribute(t,e.type);this[n]=a??this._$Ej?.get(n)??a,this._$Em=null}}requestUpdate(e,t,i,n=!1,r){if(void 0!==e){const a=this.constructor;if(!1===n&&(r=this[e]),i??=a.getPropertyOptions(e),!((i.hasChanged??w)(r,t)||i.useDefault&&i.reflect&&r===this._$Ej?.get(e)&&!this.hasAttribute(a._$Eu(e,i))))return;this.C(e,t,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:n,wrapped:r},a){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,a??t??this[e]),!0!==r||void 0!==a)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),!0===n&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const e=this.scheduleUpdate();return null!=e&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[e,t]of this._$Ep)this[e]=t;this._$Ep=void 0}const e=this.constructor.elementProperties;if(e.size>0)for(const[t,i]of e){const{wrapped:e}=i,n=this[t];!0!==e||this._$AL.has(t)||void 0===n||this.C(t,void 0,i,n)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(e=>e.hostUpdate?.()),this.update(t)):this._$EM()}catch(t){throw e=!1,this._$EM(),t}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(e){}firstUpdated(e){}};x.elementStyles=[],x.shadowRootOptions={mode:"open"},x[y("elementProperties")]=new Map,x[y("finalized")]=new Map,_?.({ReactiveElement:x}),(m.reactiveElementVersions??=[]).push("2.1.2");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const E=globalThis,S=e=>e,$=E.trustedTypes,A=$?$.createPolicy("lit-html",{createHTML:e=>e}):void 0,z="$lit$",H=`lit$${Math.random().toFixed(9).slice(2)}$`,T="?"+H,C=`<${T}>`,B=document,P=()=>B.createComment(""),L=e=>null===e||"object"!=typeof e&&"function"!=typeof e,M=Array.isArray,I="[ \t\n\f\r]",N=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,D=/-->/g,R=/>/g,O=RegExp(`>|${I}(?:([^\\s"'>=/]+)(${I}*=${I}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),U=/'/g,F=/"/g,G=/^(?:script|style|textarea|title)$/i,W=(e=>(t,...i)=>({_$litType$:e,strings:t,values:i}))(1),Z=Symbol.for("lit-noChange"),j=Symbol.for("lit-nothing"),V=new WeakMap,q=B.createTreeWalker(B,129);function K(e,t){if(!M(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==A?A.createHTML(t):t}const Y=(e,t)=>{const i=e.length-1,n=[];let r,a=2===t?"<svg>":3===t?"<math>":"",o=N;for(let t=0;t<i;t++){const i=e[t];let s,l,c=-1,h=0;for(;h<i.length&&(o.lastIndex=h,l=o.exec(i),null!==l);)h=o.lastIndex,o===N?"!--"===l[1]?o=D:void 0!==l[1]?o=R:void 0!==l[2]?(G.test(l[2])&&(r=RegExp("</"+l[2],"g")),o=O):void 0!==l[3]&&(o=O):o===O?">"===l[0]?(o=r??N,c=-1):void 0===l[1]?c=-2:(c=o.lastIndex-l[2].length,s=l[1],o=void 0===l[3]?O:'"'===l[3]?F:U):o===F||o===U?o=O:o===D||o===R?o=N:(o=O,r=void 0);const u=o===O&&e[t+1].startsWith("/>")?" ":"";a+=o===N?i+C:c>=0?(n.push(s),i.slice(0,c)+z+i.slice(c)+H+u):i+H+(-2===c?t:u)}return[K(e,a+(e[i]||"<?>")+(2===t?"</svg>":3===t?"</math>":"")),n]};class X{constructor({strings:e,_$litType$:t},i){let n;this.parts=[];let r=0,a=0;const o=e.length-1,s=this.parts,[l,c]=Y(e,t);if(this.el=X.createElement(l,i),q.currentNode=this.el.content,2===t||3===t){const e=this.el.content.firstChild;e.replaceWith(...e.childNodes)}for(;null!==(n=q.nextNode())&&s.length<o;){if(1===n.nodeType){if(n.hasAttributes())for(const e of n.getAttributeNames())if(e.endsWith(z)){const t=c[a++],i=n.getAttribute(e).split(H),o=/([.?@])?(.*)/.exec(t);s.push({type:1,index:r,name:o[2],strings:i,ctor:"."===o[1]?ie:"?"===o[1]?ne:"@"===o[1]?re:te}),n.removeAttribute(e)}else e.startsWith(H)&&(s.push({type:6,index:r}),n.removeAttribute(e));if(G.test(n.tagName)){const e=n.textContent.split(H),t=e.length-1;if(t>0){n.textContent=$?$.emptyScript:"";for(let i=0;i<t;i++)n.append(e[i],P()),q.nextNode(),s.push({type:2,index:++r});n.append(e[t],P())}}}else if(8===n.nodeType)if(n.data===T)s.push({type:2,index:r});else{let e=-1;for(;-1!==(e=n.data.indexOf(H,e+1));)s.push({type:7,index:r}),e+=H.length-1}r++}}static createElement(e,t){const i=B.createElement("template");return i.innerHTML=e,i}}function J(e,t,i=e,n){if(t===Z)return t;let r=void 0!==n?i._$Co?.[n]:i._$Cl;const a=L(t)?void 0:t._$litDirective$;return r?.constructor!==a&&(r?._$AO?.(!1),void 0===a?r=void 0:(r=new a(e),r._$AT(e,i,n)),void 0!==n?(i._$Co??=[])[n]=r:i._$Cl=r),void 0!==r&&(t=J(e,r._$AS(e,t.values),r,n)),t}class Q{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:i}=this._$AD,n=(e?.creationScope??B).importNode(t,!0);q.currentNode=n;let r=q.nextNode(),a=0,o=0,s=i[0];for(;void 0!==s;){if(a===s.index){let t;2===s.type?t=new ee(r,r.nextSibling,this,e):1===s.type?t=new s.ctor(r,s.name,s.strings,this,e):6===s.type&&(t=new ae(r,this,e)),this._$AV.push(t),s=i[++o]}a!==s?.index&&(r=q.nextNode(),a++)}return q.currentNode=B,n}p(e){let t=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}}class ee{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,n){this.type=2,this._$AH=j,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=n,this._$Cv=n?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===e?.nodeType&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=J(this,e,t),L(e)?e===j||null==e||""===e?(this._$AH!==j&&this._$AR(),this._$AH=j):e!==this._$AH&&e!==Z&&this._(e):void 0!==e._$litType$?this.$(e):void 0!==e.nodeType?this.T(e):(e=>M(e)||"function"==typeof e?.[Symbol.iterator])(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==j&&L(this._$AH)?this._$AA.nextSibling.data=e:this.T(B.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:i}=e,n="number"==typeof i?this._$AC(e):(void 0===i.el&&(i.el=X.createElement(K(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===n)this._$AH.p(t);else{const e=new Q(n,this),i=e.u(this.options);e.p(t),this.T(i),this._$AH=e}}_$AC(e){let t=V.get(e.strings);return void 0===t&&V.set(e.strings,t=new X(e)),t}k(e){M(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let i,n=0;for(const r of e)n===t.length?t.push(i=new ee(this.O(P()),this.O(P()),this,this.options)):i=t[n],i._$AI(r),n++;n<t.length&&(this._$AR(i&&i._$AB.nextSibling,n),t.length=n)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const t=S(e).nextSibling;S(e).remove(),e=t}}setConnected(e){void 0===this._$AM&&(this._$Cv=e,this._$AP?.(e))}}class te{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,n,r){this.type=1,this._$AH=j,this._$AN=void 0,this.element=e,this.name=t,this._$AM=n,this.options=r,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=j}_$AI(e,t=this,i,n){const r=this.strings;let a=!1;if(void 0===r)e=J(this,e,t,0),a=!L(e)||e!==this._$AH&&e!==Z,a&&(this._$AH=e);else{const n=e;let o,s;for(e=r[0],o=0;o<r.length-1;o++)s=J(this,n[i+o],t,o),s===Z&&(s=this._$AH[o]),a||=!L(s)||s!==this._$AH[o],s===j?e=j:e!==j&&(e+=(s??"")+r[o+1]),this._$AH[o]=s}a&&!n&&this.j(e)}j(e){e===j?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class ie extends te{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===j?void 0:e}}class ne extends te{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==j)}}class re extends te{constructor(e,t,i,n,r){super(e,t,i,n,r),this.type=5}_$AI(e,t=this){if((e=J(this,e,t,0)??j)===Z)return;const i=this._$AH,n=e===j&&i!==j||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,r=e!==j&&(i===j||n);n&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class ae{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){J(this,e)}}const oe=E.litHtmlPolyfillSupport;oe?.(X,ee),(E.litHtmlVersions??=[]).push("3.3.3");const se=globalThis;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */let le=class extends x{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,i)=>{const n=i?.renderBefore??t;let r=n._$litPart$;if(void 0===r){const e=i?.renderBefore??null;n._$litPart$=r=new ee(t.insertBefore(P(),e),e,void 0,i??{})}return r._$AI(e),r})(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return Z}};le._$litElement$=!0,le.finalized=!0,se.litElementHydrateSupport?.({LitElement:le});const ce=se.litElementPolyfillSupport;ce?.({LitElement:le}),(se.litElementVersions??=[]).push("4.2.2");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const he={attribute:!0,type:String,converter:v,reflect:!1,hasChanged:w},ue=(e=he,t,i)=>{const{kind:n,metadata:r}=i;let a=globalThis.litPropertyMetadata.get(r);if(void 0===a&&globalThis.litPropertyMetadata.set(r,a=new Map),"setter"===n&&((e=Object.create(e)).wrapped=!0),a.set(i.name,e),"accessor"===n){const{name:n}=i;return{set(i){const r=t.get.call(this);t.set.call(this,i),this.requestUpdate(n,r,e,!0,i)},init(t){return void 0!==t&&this.C(n,void 0,e,t),t}}}if("setter"===n){const{name:n}=i;return function(i){const r=this[n];t.call(this,i),this.requestUpdate(n,r,e,!0,i)}}throw Error("Unsupported decorator location: "+n)};function de(e){return(t,i)=>"object"==typeof i?ue(e,t,i):((e,t,i)=>{const n=t.hasOwnProperty(i);return t.constructor.createProperty(i,e),n?Object.getOwnPropertyDescriptor(t,i):void 0})(e,t,i)}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function pe(e){return de({...e,state:!0,attribute:!1})}let ge=!1,me=null;const fe=async()=>{if(ge&&me)return me;if(customElements.get("ha-checkbox")&&customElements.get("ha-slider")&&customElements.get("ha-panel-config")&&customElements.get("ha-entity-picker"))return Promise.resolve();ge=!0,me=async function(){try{await new Promise(e=>{"requestIdleCallback"in window?requestIdleCallback(()=>e()):setTimeout(()=>e(),0)}),await customElements.whenDefined("partial-panel-resolver");const e=document.createDocumentFragment(),t=document.createElement("partial-panel-resolver");e.appendChild(t),t.hass={panels:[{url_path:"tmp",component_name:"config"}]},await new Promise(e=>queueMicrotask(()=>e())),t._updateRoutes(),await t.routerOptions.routes.tmp.load(),await customElements.whenDefined("ha-panel-config"),await new Promise(e=>queueMicrotask(()=>e()));const i=document.createElement("ha-panel-config");e.appendChild(i),await i.routerOptions.routes.automation.load(),customElements.get("ha-entity-picker")||await Promise.race([customElements.whenDefined("ha-entity-picker"),new Promise(e=>setTimeout(e,3e3))]),e.textContent=""}catch(e){console.error("Failed to load HA form elements:",e)}}();try{await me}finally{ge=!1,me=null}};const be="smart_irrigation",_e=["de","en","es","fr","it","nl","no","sk"],ye="metric",ve="bucket",we=e=>e.callWS({type:be+"/zones"}),ke=e=>e.callWS({type:be+"/irrigation_outlook"}),xe=e=>{class i extends e{connectedCallback(){super.connectedCallback(),this.__checkSubscribed()}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const e=this.__unsubs.pop();e instanceof Promise?e.then(e=>e()):e()}this.__unsubs=void 0}}updated(e){super.updated(e),e.has("hass")&&this.__checkSubscribed()}hassSubscribe(){return[]}__checkSubscribed(){void 0===this.__unsubs&&this.isConnected&&void 0!==this.hass&&(this.__unsubs=this.hassSubscribe())}}return t([de({attribute:!1})],i.prototype,"hass",void 0),i};var Ee,Se;!function(e){e.Sunrise="sunrise",e.Sunset="sunset",e.SolarAzimuth="solar_azimuth"}(Ee||(Ee={})),function(e){e.Disabled="disabled",e.Manual="manual",e.Automatic="automatic"}(Se||(Se={}));
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const $e=2;class Ae{constructor(e){}get _$AU(){return this._$AM._$AU}_$AT(e,t,i){this._$Ct=e,this._$AM=t,this._$Ci=i}_$AS(e,t){return this.update(e,t)}update(e,t){return this.render(...t)}}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */class ze extends Ae{constructor(e){if(super(e),this.it=j,e.type!==$e)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(e){if(e===j||null==e)return this._t=void 0,this.it=e;if(e===Z)return e;if("string"!=typeof e)throw Error(this.constructor.directiveName+"() called with a non-string value");if(e===this.it)return this._t;this.it=e;const t=[e];return t.raw=t,this._t={_$litType$:this.constructor.resultType,strings:t,values:[]}}}ze.directiveName="unsafeHTML",ze.resultType=1;const He=(e=>(...t)=>({_$litDirective$:e,values:t}))(ze);var Te={loading:"Loading",saving:"Saving",actions:{delete:"Delete",edit:"Edit",save:"Save",cancel:"Cancel",confirm_delete:"Confirm Delete",confirm_delete_zone:"Are you sure you want to delete this zone?"},labels:{module:"Module",no:"No",select:"Select",yes:"Yes",enabled:"Enabled",disabled:"Disabled",before:"before",after:"after",settings:"Settings",bulk_actions:"Bulk Actions"},units:{seconds:"seconds"},attributes:{size:"size",throughput:"throughput",state:"state",bucket:"bucket",last_updated:"last updated",last_calculated:"last calculated",number_of_data_points:"number of data points"},"loading-messages":{configuration:"Loading configuration...",modules:"Loading modules...",general:"Loading..."},"saving-messages":{adding:"Adding...",saving:"Saving..."},errors:{load_failed:"Couldn't load data",save_failed:"Couldn't save changes",delete_failed:"Couldn't delete",action_failed:"Action failed"}},Ce={"default-zone":"Default zone","default-mapping":"Default sensor group"},Be={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"Note: this explanation uses '.' as decimal separator, shows rounded and metric values. Module returned Evapotranspiration deficiency ( = et0 * hour_multiplier + precipitation) of","bucket-was":"Bucket was","new-bucket-values-is":"New bucket value is",bucket:"bucket","old-bucket-variable":"old_bucket","max-bucket-variable":"max_bucket",delta:"delta","bucket-less-than-zero-irrigation-necessary":"Since bucket < 0, irrigation is necessary","steps-taken-to-calculate-duration":"To calculate the exact duration, the following steps were taken","precipitation-rate-defined-as":"The precipitation rate is defined as","duration-is-calculated-as":"The duration is calculated as",drainage:"drainage","drainage-rate":"drainage_rate",hours:"hours","precipitation-rate-variable":"precipitation_rate","multiplier-is-applied":"Now, the multiplier is applied. The multiplier is","duration-after-multiplier-is":"hence the duration is","maximum-duration-is-applied":"Then, the maximum duration is applied. The maximum duration is","duration-after-maximum-duration-is":"hence the duration is","lead-time-is-applied":"Finally, the lead time is applied. The lead time is","duration-after-lead-time-is":"hence the final duration is","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Since bucket >= 0, no irrigation is necessary and duration is set to","maximum-bucket-is":"Maximum bucket size is","drainage-rate-is":"Drainage rate when saturated (bucket at max) is","current-drainage-is":"Current drainage is calculated as","drainage-integrated":"the surplus above field capacity drains continuously over the window (Brooks–Corey), so the rate falls as it drains","no-drainage":"Current drainage is 0 because","forecast-weighting-applied":"Forecast weighting reduced the deficit for the expected rain","crop-coefficient-applied":"Scaled by the crop coefficient"}}},Pe={pyeto:{description:"Calculate duration based on the FAO56 calculation from the PyETO library"},static:{description:"'Dummy' module with a static configurable delta"},passthrough:{description:"Passthrough module that returns the value of an Evapotranspiration sensor as delta"}},Le={general:{cards:{"automatic-duration-calculation":{header:"Automatic duration calculation",description:"Calculation takes collected weather data up to that point and updates the bucket for each automatic zone. Then, the duration is adjusted based on the new bucket value and the collected weather data is removed.",labels:{"auto-calc-enabled":"Automatically calculate irrigation durations","calc-time":"Calculate at"}},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Warning: weather data update time on or after calculation time"},header:"Automatic weather data update",description:"Collect and store weather data automatically. Weather data is required to calculate zone buckets and durations.",labels:{"auto-update-enabled":"Automatically update weather data","auto-update-schedule":"Update schedule","auto-update-time":"Update at","auto-update-interval":"Update sensor data every","auto-update-delay":"Update delay"},options:{minutes:"minutes",hours:"hours",days:"days"}},"automatic-clear":{header:"Automatic weather data pruning",description:"Automatically remove collected weather data at a configured time. Use this to make sure that there is no left over weather data from previous days. Don't remove the weather data before you calculate and only use this option if you expect the automatic update to collect weather data after you calculated for the day. Ideally, you want to prune as late in the day as possible.",labels:{"automatic-clear-enabled":"Automatically clear collected weather data","automatic-clear-time":"Clear weather data at"}},continuousupdates:{header:"Continuous updates for sensors (experimental)",description:"This experimental feature will continuously update the sensor data. This is useful for sensor groups that use sources that provide continuous data, such as weather stations. This feature cannot be used for sensor groups that at least partly rely on weather services as continous polling of APIs will incur costs. Keep in mind that this is experimental and may not work as expected. Use at your own risk.",labels:{continuousupdates:"Enable continuous updates",sensor_debounce:"Sensor debounce"}}},description:"This page provides global settings.",title:"General",sections:{weather:"Weather",automation:"Automation",location:"Location",watering:"Watering behavior"}},schedules:{title:"Schedules",description:"Create recurring schedules to automatically irrigate your zones at specific times. No automations needed.",add:"Add Schedule",no_items:"No schedules configured yet. Click 'Add Schedule' to get started.",zones_all:"All zones",zones_specific:"Specific zones",hours:"hours",minutes:"min",types:{daily:"Daily",weekly:"Weekly",monthly:"Monthly",interval:"Every N hours",sunrise:"Sunrise",sunset:"Sunset",solar_azimuth:"Solar azimuth"},actions:{calculate:"Calculate (update irrigation duration)",update:"Update (collect weather data)",irrigate:"Irrigate (run valves directly)"},days:{monday:"Mon",tuesday:"Tue",wednesday:"Wed",thursday:"Thu",friday:"Fri",saturday:"Sat",sunday:"Sun"},fields:{name:"Name",type:"Schedule type",enabled:"Enabled",time:"Time (HH:MM)",days_of_week:"Days of week",day_of_month:"Day of month",interval_hours:"Interval",action:"Action",zones:"Zones",start_date:"Start date (optional)",end_date:"End date (optional)",offset_minutes:"Offset from sunrise/sunset",account_for_duration:"Start early so irrigation finishes at trigger time",azimuth_angle:"Solar azimuth angle",time_anchor:"Time marks the"},dialog:{add_title:"Add Schedule",edit_title:"Edit Schedule"},time_anchor:{start:"Start of irrigation",finish:"End of irrigation"}},setup:{title:"Setup",tabs:{weather_location:"Weather & Location",my_zones:"My Zones",when_to_water:"When to Water",advanced:"Advanced",experimental:"Experimental"},weather_data:{forecast_title:"Forecast",forecast_none:"Forecast is available when a weather service is enabled.",seasonal_title:"Seasonal outlook"},advanced:{used_by_zones:"Used by {count, plural, one {# zone} other {# zones}}",not_used:"Not used"}},experimental:{title:"Experimental features",warning:"These features are opt-in and still being refined. They change how each zone's bucket is filled, so turn them on one at a time and keep an eye on your zones — you can switch them back off at any time.",forecast_weighting:{title:"Forecast-weighted durations",description:"Instead of skipping a whole run when rain is forecast, water less. The upcoming precipitation (over the look-ahead window set under When to Water) is subtracted from the deficit used to compute the run duration, while the true deficit stays in the bucket so the real rain fills the rest. If the forecast rain misses, the next run makes up the difference. Requires a weather service.",label:"Reduce durations when rain is forecast",note:"Uses the precipitation look-ahead from When to Water. Works alongside the rain-skip guard (a skip still wins over a reduced run)."},observed_watering:{title:"Credit bucket from observed watering",description:"When a zone's linked valve runs outside Smart Irrigation — a manual tap, an automation, your own schedule — its bucket is credited for the water applied, estimated from the run time and the zone's throughput. This keeps the soil-moisture model honest when you water by other means. Smart Irrigation's own runs are already accounted for and are never double-counted.",label:"Credit the bucket when a linked valve runs externally",note:"Requires a linked valve and a throughput on the zone. Volume is estimated (run time × throughput), not metered."},live_duration:{title:"Live-estimate run durations",description:"By default each zone's watering duration is fixed when the daily calculation runs (for example at 23:00), hours before the valve actually opens. With this on, the duration is recomputed at run time from the live intra-day deficit (the drainage-aware ET and rainfall since the last calculation), so overnight and early-morning weather is taken into account. The daily ledger is unchanged: after the run the bucket is credited with the water actually delivered, so the next daily calculation never double-counts. Requires a weather service.",label:"Recompute the run duration at watering time",note:"Affects scheduled runs only. A zone that intra-day rain has already covered is skipped for that run."}},help:{title:"Help",cards:{"how-to-get-help":{title:"How to get help","first-read-the":"First, read the",wiki:"Documentation","if-you-still-need-help":"If you still need help reach out on the","community-forum":"Community forum","or-open-a":"or open a","github-issue":"Github Issue","english-only":"English only"}}},info:{title:"Info",description:"View information about next irrigation and system status.","configuration-not-available":"Configuration not available.",cards:{"zone-bucket-values":{title:"Zone Bucket Values & Duration",labels:{bucket:"Bucket",duration:"Duration"},"no-zones":"No zones configured"},"next-irrigation":{title:"Next Irrigation",labels:{"next-start":"Next start",duration:"Duration",zones:"Zones"},"no-data":"No data available"},"irrigation-reason":{title:"Irrigation Reason",labels:{reason:"Reason",sunrise:"Sunrise","total-duration":"Total duration",explanation:"Explanation"},"no-data":"No data available"},irrigate_now:{title:"Irrigate Now",description:"Immediately start irrigation for all zones that have a linked entity. Skip conditions are ignored.",button_all:"Run all zones now",no_linked_zones:"No zones have a linked switch/valve entity with a calculated duration."}}},mappings:{cards:{"add-mapping":{actions:{add:"Add sensor group"},header:"Add sensor groups"},mapping:{aggregates:{average:"Average",first:"First",last:"Last",maximum:"Maximum",median:"Median",minimum:"Minimum",riemannsum:"Riemann sum",sum:"Sum",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"You cannot delete this sensor group because there is at least one zone using it.",invalid_source:"Invalid source",source_does_not_exist:"Source does not exist. Please enter a valid source, such as 'sensor.mysensor'."},items:{dewpoint:"Dewpoint",evapotranspiration:"Evapotranspiration",humidity:"Humidity","maximum temperature":"Maximum temperature","minimum temperature":"Minimum temperature",precipitation:"Total precipitation","current precipitation":"Current precipitation",pressure:"Pressure","solar radiation":"Solar radiation",temperature:"Temperature",windspeed:"Wind speed"},pressure_types:{absolute:"absolute",relative:"relative"},"pressure-type":"Pressure is","sensor-aggregate-of-sensor-values-to-calculate":"of sensor values to calculate duration","sensor-aggregate-use-the":"Use the","sensor-entity":"Sensor entity",static_value:"Value","input-units":"Input provides values in",source:"Source",sources:{none:"None",weather_service:"Weather service",sensor:"Sensor",static:"Static value"}}},description:"Add one or more sensor groups that retrieve weather data from Weather service, from sensors or a combination of these. You can map each sensor group to one or more zones",labels:{"mapping-name":"Name"},no_items:"There are no sensor group defined yet.",title:"Sensor Groups","weather-records":{title:"Weather Records",timestamp:"Time",temperature:"Temp",humidity:"Hum",dewpoint:"Dew",wind:"Wind",pressure:"Press",precipitation:"Precip","retrieval-time":"Retrieved","no-data":"No weather data available for this sensor group"}},modules:{cards:{"add-module":{actions:{add:"Add module"},header:"Add module"},module:{errors:{"cannot-delete-module-because-zones-use-it":"You cannot delete this module because there is at least one zone using it."},labels:{configuration:"Configuration",required:"indicates a required field"},"translated-options":{DontEstimate:"Do not estimate",EstimateFromSunHours:"Estimate from sun hours",EstimateFromTemp:"Estimate from temperature",EstimateFromSunHoursAndTemperature:"Estimate from average of sun hours and temperature"},fields:{coastal:{name:"Coastal",description:"Enable if the weather station is located near a coast or large body of water. Affects how atmospheric humidity is estimated."},solrad_behavior:{name:"Solar radiation estimation",description:"How solar radiation is estimated when it is not directly measured by a sensor."},forecast_days:{name:"Forecast days",description:"Number of future days to include in the ET calculation. 0 = current weather only (recommended — no extra API calls). Values > 0 average today's ET with forecasted ET for upcoming days (up to 4 days via the OWM free tier)."},delta:{name:"Delta",description:"Static evapotranspiration delta (mm) used directly without any weather-based calculation."}}}},description:"Add one or more modules that calculate irrigation duration. Each module comes with its own configuration and can be used to calculate duration for one or more zones.",no_items:"There are no modules defined yet.",title:"Modules"},zones:{actions:{add:"Add",calculate:"Calculate",information:"Information",update:"Update","reset-bucket":"Reset bucket","view-weather-info":"View weather data","view-weather-info-message":"Weather data available for","view-watering-calendar":"View watering calendar",irrigate_all:"Water all zones now",open_settings:"Edit settings"},cards:{"add-zone":{actions:{add:"Add zone"},header:"Add zone"},"zone-actions":{actions:{"calculate-all":"Recalculate durations","update-all":"Refresh weather data","reset-all-buckets":"Reset all buckets","clear-all-weatherdata":"Clear all weather data"},header:"Actions on all zones"}},description:"Specify one or more irrigation zones here. The irrigation duration is calculated per zone, depending on size, throughput, state, module and sensor group.",labels:{bucket:"Bucket",duration:"Duration","lead-time":"Lead time",mapping:"Sensor Group","maximum-duration":"Maximum duration",multiplier:"Multiplier",name:"Name",size:"Size",state:"State",states:{automatic:"Automatic",disabled:"Disabled",manual:"Manual"},throughput:"Throughput","maximum-bucket":"Maximum bucket",last_calculated:"Last calculated","data-last-updated":"Data last updated","data-number-of-data-points":"Number of data points",drainage_rate:"Drainage rate",linked_entity:"Linked switch/valve/helper entity",linked_entity_placeholder:"e.g. switch.garden_valve",flow_sensor:"Flow meter sensor (optional)",flow_sensor_placeholder:"e.g. sensor.zone_flow_rate",irrigate_now:"Irrigate Now",bucket_threshold:"Minimum deficit to irrigate",plant_type:"Plant type",kc:"Crop coefficient (Kc)",plant_types:{custom:"Custom (set Kc manually)",lawn:"Lawn / turf",vegetables:"Vegetable garden",flowers:"Flower bed",shrubs:"Shrubs",trees:"Trees",xeriscape:"Xeriscape / drought-tolerant"},soil_type:"Soil type",soil_types:{custom:"Custom (set rate manually)",sand:"Sandy (fast draining)",loam:"Loam (balanced)",silt:"Silt (slow draining)",clay:"Clay (very slow draining)"}},no_items:"There are no zones defined yet.",title:"Zones",status:{decision_disabled:"Turned off — this zone won't be watered automatically.",decision_water:"Watering needed: about {duration} on the next scheduled run.",decision_water_at:"Will water about {duration} at {time}.",decision_water_skip:"Deficit ~{duration}, but the next run will likely be skipped ({reason}).",decision_water_no_schedule:"Deficit ~{duration} — no schedule waters this zone; trigger it manually.",decision_no_water:"No watering needed right now — the soil has enough moisture.",decision_unknown:"Not calculated yet — press Update, then Calculate to check.",last_checked:"Last checked",never:"never",saved:"Saved",estimate_now:"Now",estimate_tag:"est.",estimate_method:{hourly:"Live estimate from hourly weather since the last calculation",proxy:"Estimate distributed from today's forecast since the last calculation"}},fault:{title:"Last run failed",valve_no_response:"The valve didn't respond — no water was delivered, so the bucket was left unchanged.",flow_never_started:"No flow was detected — no water was delivered, so the bucket was left unchanged.",generic:"The last irrigation run failed."},help:{bucket:"Soil-moisture balance. A negative value means the soil is dry and the zone needs water.",calculate:"Works out how long to water from the latest data. Run this after Update.",update:"Fetches the latest weather/sensor data for this zone.",irrigate_link_entity:"Link a switch/valve in this zone's settings to enable manual watering.",irrigate_all:"Opens the linked valves now for every zone with a deficit. Skip conditions (rain, wind, temperature) are ignored.",update_all:"Collects the latest weather/sensor data for all zones. Does not change durations on its own.",calculate_all:"Recomputes each automatic zone's watering duration from the data collected so far."},outlook:{next_run:"Next run",no_schedule:"No automatic schedule — zones water only when you trigger them.",setup_schedule:"Set up a schedule",targets_all:"all zones",targets_zones:"{count} zones",will_skip:"Next run will likely be skipped",will_run:"Conditions look clear for the next run.",why_skipped:"Why?",provisional:"forecast — may change",active_guards:"Active guards",last_run:"Last run",last_run_skipped:"skipped",last_run_ran:"ran",today:"today",tomorrow:"tomorrow",actions:{irrigate:"Water",calculate:"Recalculate",update:"Refresh data"},checks:{precipitation:"Rain forecast",days_between:"Days between watering",temperature:"Low temperature",wind:"High wind",rain_sensor:"Rain sensor",freeze:"Frost",paused:"Paused (rain delay)"},check_detail:{precipitation:"{observed} mm (≥ {threshold} mm)",days_between:"{observed}/{threshold} days",temperature:"{observed}° (below {threshold}°)",wind:"{observed} (above {threshold})",rain_sensor:"{observed}",freeze:"{observed}° (below {threshold}°)"}},calendar:{no_data:"No watering calendar data available for this zone.",error_prefix:"Error generating calendar:",month:"Month",et:"ET (mm)",precipitation:"Precipitation (mm)",watering:"Watering (L)",avg_temp:"Avg Temp (°C)",method_prefix:"Method:"},confirm_action:{reset_bucket_title:"Reset this zone's bucket?",reset_bucket_body:"This sets the bucket back to 0, discarding the accumulated moisture balance for this zone.",reset_all_buckets_title:"Reset all buckets?",reset_all_buckets_body:"This sets every zone's bucket back to 0, discarding the accumulated moisture balance. Watering calculations start fresh from the next update.",clear_weather_title:"Clear all weather data?",clear_weather_body:"This deletes all collected weather and sensor records for every zone. Zones will need fresh data before they can calculate again."},confirm_irrigate:{title:"Start irrigation?",body:"This opens the linked valve(s) now and bypasses all skip conditions (rain, temperature, minimum days between watering).",all_linked_zones:"All linked zones",toast_started:"Irrigation started",toast_failed:"Irrigation failed"},history:{title:"Run history",total_used:"Total water used",empty:"No runs recorded yet.",when:"When",result:"Result",volume:"Volume",detail:"Detail",results:{completed:"Completed",partial:"Partial",failed:"Failed",skipped:"Skipped"}},rain_delay:{title:"Pause watering",paused:"Paused",until:"until",delay_24h:"Delay 24 h",delay_48h:"Delay 48 h",resume:"Resume"},run_zone:{run:"Run",minutes:"min",help:"Water this zone for a custom time, ignoring the calculation",toast_started:"Started run"}}},Me="Smart Irrigation",Ie={title:"Weather Service",description:"Configure which weather service to use for ET calculations and skip conditions.",enabled_label:"Enable weather service",service_label:"Weather service",api_key_label:"API key",api_key_placeholder:"Leave blank to keep existing key",api_key_configured:"API key is configured",api_key_not_configured:"No API key configured",api_key_help:"An API key from your chosen weather service provider. Open-Meteo does not require a key. OpenWeatherMap, Pirate Weather and the Met Office (Weather DataHub) all offer free tiers.",no_api_key_needed:"Open-Meteo is a free service and requires no API key.",save_button:"Save weather settings",saved:"Weather settings saved",owm:"OpenWeatherMap",pw:"Pirate Weather",openmeteo:"Open-Meteo (free, no key needed)",met:"Met Office (UK)",test_button:"Test Connection",test_button_testing:"Testing…",test_success:"✓ Connection successful",test_error_invalid_auth:"✗ Invalid API key — check that it is correct and active",test_error_cannot_connect:"✗ Cannot connect — check your internet connection",test_error_no_service:"✗ Select a weather service first",test_error_unknown:"✗ Test failed — unknown error"},Ne={title:"Irrigation Start Triggers",description:"Configure when irrigation should start based on solar events. You can add multiple triggers for different schedules. For sunrise triggers, leaving offset at 0 will automatically use the total duration of all enabled zones.",add_trigger:"Add Trigger",edit_trigger:"Edit Trigger",delete_trigger:"Delete Trigger",trigger_types:{sunrise:"Sunrise",sunset:"Sunset",solar_azimuth:"Solar Azimuth"},fields:{name:{name:"Trigger Name",description:"A descriptive name to identify this trigger"},type:{name:"Trigger Type",description:"The type of solar event to trigger on"},enabled:{name:"Enabled",description:"Whether this trigger is currently active"},offset_minutes:{name:"Offset (minutes)",description:"Minutes before (-) or after (+) the solar event. For sunrise triggers, use 0 for automatic timing based on total zone duration."},azimuth_angle:{name:"Azimuth Angle (degrees)",description:"Solar azimuth angle in degrees where 0=North, 90=East, 180=South, 270=West"},account_for_duration:{name:"Account for Duration",description:"When enabled, irrigation will start early enough to finish at the specified time. When disabled, irrigation will start exactly at the specified time."}},dialog:{add_title:"Add Irrigation Start Trigger",edit_title:"Edit Irrigation Start Trigger",cancel:"Cancel",save:"Save",delete:"Delete"},no_triggers:"No irrigation start triggers configured. The system will use the default behavior (sunrise with total zone duration). Add triggers to customize when irrigation starts.",offset_auto:"Auto (calculated from total zone duration)",confirm_delete:"Are you sure you want to delete the trigger '{name}'?",validation:{name_required:"Trigger name is required",azimuth_invalid:"Azimuth angle must be a valid number"},help:{sunrise_offset:"For sunrise triggers: Use negative values to start before sunrise, positive to start after. Set to 0 to automatically start early enough to complete all zones before sunrise.",sunset_offset:"For sunset triggers: Use negative values to start before sunset, positive to start after sunset.",azimuth_explanation:"Solar azimuth is the compass direction of the sun. 0°=North, 90°=East, 180°=South, 270°=West. You can enter any angle value (e.g., 450° = 90°, -30° = 330°). Use this to trigger irrigation when the sun reaches a specific position.",multiple_triggers:"You can configure multiple triggers. Each enabled trigger will independently schedule irrigation starts."}},De={title:"Skip Conditions",description:"Automatically skip irrigation when conditions are unfavorable. Precipitation check requires a weather service. Temperature and wind checks also require a weather service.",threshold_label:"Precipitation Threshold",threshold_description:"Minimum total precipitation (in mm) forecast across the look-ahead window to skip irrigation.",lookahead_label:"Forecast look-ahead (days)",lookahead_help:"How many upcoming forecast days to add up when checking for rain. The forecast starts at tomorrow (today is excluded), so 1 = just the next day, 2 = the next two days, and so on.",temp_section_title:"Skip on low temperature",temp_threshold_label:"Skip if temperature is below",wind_section_title:"Skip on high wind speed",wind_threshold_label:"Skip if wind speed is above",rain_sensor_section_title:"Skip on rain sensor",rain_sensor_label:"Rain sensor entity (optional)",rain_sensor_placeholder:"e.g. binary_sensor.rain",freeze_section_title:"Skip on frost",freeze_threshold_label:"Skip if minimum temperature is below",freeze_help:"Compares the current temperature and the coming night's forecast low; skips watering when frost is expected, to protect pipes and plants.",forecast_rain_label:"When rain is forecast",forecast_rain_options:{ignore:"Ignore it",water_less:"Water less",skip:"Skip watering"},forecast_rain_help:{ignore:"Forecast rain is ignored; runs use the calculated duration.",water_less:"Upcoming forecast rain trims the run duration (the deficit stays in the bucket for the real rain to fill).",skip:"Skip the run entirely when enough rain is forecast within the look-ahead window."}},Re={title:"Location Coordinates",description:"Configure location coordinates for weather data retrieval. You can use manual coordinates different from your Home Assistant location if needed.",manual_enabled:"Use manual coordinates",use_ha_location:"Use Home Assistant location",latitude:"Latitude (decimal degrees)",longitude:"Longitude (decimal degrees)",elevation:"Elevation (meters above sea level)",current_ha_coords:"Current Home Assistant coordinates"},Oe={title:"Days Between Irrigation",description:"Configure the minimum number of days that must pass between irrigation events. This helps control watering frequency for water conservation and plant health management.\n\nTypical real-world use cases:\n• Lawn care: 1-2 day intervals prevent overwatering\n• Drought restrictions: 6+ day intervals for weekly watering\n• Deep-rooted plants: 3-7 day intervals for less frequent watering\n• Water conservation: Customizable based on climate and soil conditions",label:"Minimum days between irrigation",help_text:"Set to 0 to disable this feature. Values from 1-365 days are supported. This setting works alongside existing precipitation forecasting logic."},Ue={title:"Zone Sequencing",description:"When multiple zones need irrigation, choose whether they run at the same time or one after another. Sequential mode waits for each zone to finish before starting the next. Rotating mode cycles through zones, giving each one a limited consecutive run before moving to the next.",parallel:"Parallel (all zones at once)",sequential:"Sequential (one zone at a time)",rotating:"Rotating (zones take turns)",max_consecutive_duration_label:"Max consecutive run time per zone",max_consecutive_duration_unit:"minutes",min_absorption_time_label:"Min. absorption time between slots",min_absorption_time_unit:"minutes (0 = disabled)"},Fe={zone_size:"The total irrigated area of this zone. Used with throughput to calculate how much water is applied per run.",zone_throughput:"Total water flow of your irrigation system for this zone (litres/min in metric, gal/min in imperial). Check your sprinkler datasheet or measure by timing how long it takes to fill a known container.",zone_drainage_rate:"How fast saturated soil drains excess water. ~20 mm/h suits medium/loam soil; lower (2–10) for heavy clay, higher for sandy soil.",zone_bucket:"Current water deficit (negative) or surplus (positive) for this zone. Irrigation triggers when bucket drops below the threshold.",zone_maximum_bucket:"Maximum moisture surplus the zone can hold. Water above this level is treated as runoff. Typical value: 50 mm.",zone_bucket_threshold:"Irrigation triggers when the bucket drops below this value. Must be 0 or negative. 0 means irrigate whenever there is any deficit.",zone_multiplier:"Scale factor applied to the calculated duration. Use above 1.0 to increase, below 1.0 to decrease. Useful for fine-tuning without changing physical measurements.",zone_lead_time:"Extra seconds added before irrigation starts. Use for pump warm-up or system pressurisation.",zone_maximum_duration:"Hard cap on any single irrigation run in seconds. Prevents runaway watering. Default: 3600 s (1 hour).",zone_linked_entity:"The HA switch, valve or input_boolean (helper) entity controlling water flow for this zone. This entity is turned on when irrigation runs.",zone_flow_sensor:"Optional sensor measuring actual water flow rate. Used for reporting only — does not affect duration calculations.",general_autoupdatedelay:"Seconds to wait after HA starts before the first weather data fetch. Allows other integrations to initialise first.",general_sensor_debounce:"Minimum gap in milliseconds between sensor readings to filter noise from rapidly changing sensors.",general_calctime:"Time of day when irrigation durations are recalculated from collected weather data. Format: HH:MM (24-hour).",general_cleardatatime:"Time of day when old weather data is purged. Must be set later than the calculation time.",general_days_between:"Minimum days between irrigation events for the same zone. Set to 0 to disable (irrigate whenever deficit exists).",general_autoupdateinterval:"How often weather data is collected. Choose a value that balances fresh data against API rate limits.",general_precipitation_threshold:"Irrigation is skipped if total forecast precipitation across the look-ahead window exceeds this amount.",general_temp_threshold:"Irrigation is skipped if the current temperature is below this value (e.g. to prevent frost damage).",general_wind_threshold:"Irrigation is skipped if wind speed exceeds this value (high winds reduce efficiency and cause drift).",zone_plant_type:"Pick a plant type to set a typical crop coefficient, or choose Custom to enter Kc yourself.",zone_kc:"Scales reference (grass) ET to this zone's plants. 1.0 = reference grass; lower for drought-tolerant planting, higher for thirsty crops. Only the ET term is scaled — rain is not.",zone_soil_type:"Pick a soil type to set a typical drainage rate, or leave Custom to enter it by hand below."},Ge={title:"Setup Wizard",open_button:"Setup Wizard",close:"Close",next:"Next",back:"Back",finish:"Finish",skip_step:"Skip this step",step_indicator:"Step {current} of {total}",stepper:{weather:"Weather",module:"Module",mapping:"Sensor Group",zone:"Zone"},setup_complete_banner:"Setup not complete. Run the wizard to get started.",open_wizard:"Open Wizard",steps:{welcome:{title:"Welcome to Smart Irrigation",intro:"This wizard guides you through the four steps needed to get your first zone irrigating automatically.",step1_label:"Weather Service — where to get weather data",step2_label:"Calculation Module — how irrigation duration is computed",step3_label:"Sensor Group — which data sources to use",step4_label:"Zone — your first irrigation zone",tip:"You can skip any step and configure it later from the Setup tab."},weather:{title:"Weather Service",description:"Choose how to get weather data. Open-Meteo is free and requires no API key — it is the easiest choice for most users."},module:{title:"Calculation Module",description:"A module calculates how long to irrigate based on evapotranspiration (ET). The PyETO module (FAO-56 method) is recommended for most users.",pick_label:"Select module type",no_modules:"No module types available."},mapping:{title:"Sensor Group",description:"A sensor group links each weather variable to a data source. Set the key variables below — you can refine individual sensor mappings later from the Setup → Sensor Groups tab.",name_label:"Sensor group name",source_label:"Data source for",use_weather_service:"Weather service",use_sensor:"Sensor",use_static:"Static value",use_none:"None / not used"},zone:{title:"First Zone",description:"A zone is one irrigation area (e.g. lawn, garden bed). Set the physical properties so the system can calculate the correct irrigation duration.",name_label:"Zone name",size_label:"Area",throughput_label:"Sprinkler throughput",entity_label:"Linked switch, valve or helper",entity_placeholder:"e.g. switch.garden_valve",module_label:"Calculation module",mapping_label:"Sensor group"},done:{title:"Setup Complete!",description:"Your first zone is ready. Smart Irrigation will now calculate irrigation durations automatically based on weather data.",next_steps:"What you can do next:",tip1:"Go to Zones to view calculated durations and bucket values.",tip2:"Add more zones from the Zones tab.",tip3:"Refine all settings from the Setup tab.",go_zones:"Go to Zones",go_setup:"Go to Setup",schedule_name:"Daily",schedule_title:"Create a watering schedule",schedule_desc:"Your system is configured, but it won't water until a schedule exists. Create a daily schedule for all zones now (you can change or remove it later under Setup → When to Water).",schedule_create:"Create daily schedule",schedule_created:"Daily schedule created."}},confirm_close:{body:"Close the setup wizard? Your progress so far is saved.",keep:"Keep editing",close:"Close"}},We={common:Te,defaults:Ce,module:Be,calcmodules:Pe,panels:Le,title:Me,weather_service_config:Ie,irrigation_start_triggers:Ne,weather_skip:De,coordinate_config:Re,days_between_irrigation:Oe,zone_sequencing:Ue,field_help:Fe,wizard:Ge},Ze=Object.freeze({__proto__:null,calcmodules:Pe,common:Te,coordinate_config:Re,days_between_irrigation:Oe,default:We,defaults:Ce,field_help:Fe,irrigation_start_triggers:Ne,module:Be,panels:Le,title:Me,weather_service_config:Ie,weather_skip:De,wizard:Ge,zone_sequencing:Ue});function je(e,t){const i=t&&t.cache?t.cache:Qe,n=t&&t.serializer?t.serializer:Xe;return(t&&t.strategy?t.strategy:Ye)(e,{cache:i,serializer:n})}function Ve(e,t,i,n){const r=null==(a=n)||"number"==typeof a||"boolean"==typeof a?n:i(n);var a;let o=t.get(r);return void 0===o&&(o=e.call(this,n),t.set(r,o)),o}function qe(e,t,i){const n=Array.prototype.slice.call(arguments,3),r=i(n);let a=t.get(r);return void 0===a&&(a=e.apply(this,n),t.set(r,a)),a}function Ke(e,t,i,n,r){return i.bind(t,e,n,r)}function Ye(e,t){return Ke(e,this,1===e.length?Ve:qe,t.cache.create(),t.serializer)}const Xe=function(){return JSON.stringify(arguments)};var Je=class{constructor(){this.cache=Object.create(null)}get(e){return this.cache[e]}set(e,t){this.cache[e]=t}};const Qe={create:function(){return new Je}},et={variadic:function(e,t){return Ke(e,this,qe,t.cache.create(),t.serializer)}},tt=/(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;function it(e){const t={};return e.replace(tt,e=>{const i=e.length;switch(e[0]){case"G":t.era=4===i?"long":5===i?"narrow":"short";break;case"y":t.year=2===i?"2-digit":"numeric";break;case"Y":case"u":case"U":case"r":throw new RangeError("`Y/u/U/r` (year) patterns are not supported, use `y` instead");case"q":case"Q":throw new RangeError("`q/Q` (quarter) patterns are not supported");case"M":case"L":t.month=["numeric","2-digit","short","long","narrow"][i-1];break;case"w":case"W":throw new RangeError("`w/W` (week) patterns are not supported");case"d":t.day=["numeric","2-digit"][i-1];break;case"D":case"F":case"g":throw new RangeError("`D/F/g` (day) patterns are not supported, use `d` instead");case"E":t.weekday=4===i?"long":5===i?"narrow":"short";break;case"e":if(i<4)throw new RangeError("`e..eee` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][i-4];break;case"c":if(i<4)throw new RangeError("`c..ccc` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][i-4];break;case"a":t.hour12=!0;break;case"b":case"B":throw new RangeError("`b/B` (period) patterns are not supported, use `a` instead");case"h":t.hourCycle="h12",t.hour=["numeric","2-digit"][i-1];break;case"H":t.hourCycle="h23",t.hour=["numeric","2-digit"][i-1];break;case"K":t.hourCycle="h11",t.hour=["numeric","2-digit"][i-1];break;case"k":t.hourCycle="h24",t.hour=["numeric","2-digit"][i-1];break;case"j":case"J":case"C":throw new RangeError("`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead");case"m":t.minute=["numeric","2-digit"][i-1];break;case"s":t.second=["numeric","2-digit"][i-1];break;case"S":case"A":throw new RangeError("`S/A` (second) patterns are not supported, use `s` instead");case"z":t.timeZoneName=i<4?"short":"long";break;case"Z":case"O":case"v":case"V":case"X":case"x":throw new RangeError("`Z/O/v/V/X/x` (timeZone) patterns are not supported, use `z` instead")}return""}),t}const nt=/[\t-\r \x85\u200E\u200F\u2028\u2029]/i;function rt(e){return e.replace(/^(.*?)-/,"")}const at=/^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g,ot=/^(@+)?(\+|#+)?[rs]?$/g,st=/(\*)(0+)|(#+)(0+)|(0+)/g,lt=/^(0+)$/;function ct(e){const t={};return"r"===e[e.length-1]?t.roundingPriority="morePrecision":"s"===e[e.length-1]&&(t.roundingPriority="lessPrecision"),e.replace(ot,function(e,i,n){return"string"!=typeof n?(t.minimumSignificantDigits=i.length,t.maximumSignificantDigits=i.length):"+"===n?t.minimumSignificantDigits=i.length:"#"===i[0]?t.maximumSignificantDigits=i.length:(t.minimumSignificantDigits=i.length,t.maximumSignificantDigits=i.length+("string"==typeof n?n.length:0)),""}),t}function ht(e){switch(e){case"sign-auto":return{signDisplay:"auto"};case"sign-accounting":case"()":return{currencySign:"accounting"};case"sign-always":case"+!":return{signDisplay:"always"};case"sign-accounting-always":case"()!":return{signDisplay:"always",currencySign:"accounting"};case"sign-except-zero":case"+?":return{signDisplay:"exceptZero"};case"sign-accounting-except-zero":case"()?":return{signDisplay:"exceptZero",currencySign:"accounting"};case"sign-never":case"+_":return{signDisplay:"never"}}}function ut(e){let t;if("E"===e[0]&&"E"===e[1]?(t={notation:"engineering"},e=e.slice(2)):"E"===e[0]&&(t={notation:"scientific"},e=e.slice(1)),t){const i=e.slice(0,2);if("+!"===i?(t.signDisplay="always",e=e.slice(2)):"+?"===i&&(t.signDisplay="exceptZero",e=e.slice(2)),!lt.test(e))throw new Error("Malformed concise eng/scientific notation");t.minimumIntegerDigits=e.length}return t}function dt(e){const t=ht(e);return t||{}}function pt(e){let t={};for(const i of e){switch(i.stem){case"percent":case"%":t.style="percent";continue;case"%x100":t.style="percent",t.scale=100;continue;case"currency":t.style="currency",t.currency=i.options[0];continue;case"group-off":case",_":t.useGrouping=!1;continue;case"precision-integer":case".":t.maximumFractionDigits=0;continue;case"measure-unit":case"unit":t.style="unit",t.unit=rt(i.options[0]);continue;case"compact-short":case"K":t.notation="compact",t.compactDisplay="short";continue;case"compact-long":case"KK":t.notation="compact",t.compactDisplay="long";continue;case"scientific":t={...t,notation:"scientific",...i.options.reduce((e,t)=>({...e,...dt(t)}),{})};continue;case"engineering":t={...t,notation:"engineering",...i.options.reduce((e,t)=>({...e,...dt(t)}),{})};continue;case"notation-simple":t.notation="standard";continue;case"unit-width-narrow":t.currencyDisplay="narrowSymbol",t.unitDisplay="narrow";continue;case"unit-width-short":t.currencyDisplay="code",t.unitDisplay="short";continue;case"unit-width-full-name":t.currencyDisplay="name",t.unitDisplay="long";continue;case"unit-width-iso-code":t.currencyDisplay="symbol";continue;case"scale":t.scale=parseFloat(i.options[0]);continue;case"rounding-mode-floor":t.roundingMode="floor";continue;case"rounding-mode-ceiling":t.roundingMode="ceil";continue;case"rounding-mode-down":t.roundingMode="trunc";continue;case"rounding-mode-up":t.roundingMode="expand";continue;case"rounding-mode-half-even":t.roundingMode="halfEven";continue;case"rounding-mode-half-down":t.roundingMode="halfTrunc";continue;case"rounding-mode-half-up":t.roundingMode="halfExpand";continue;case"integer-width":if(i.options.length>1)throw new RangeError("integer-width stems only accept a single optional option");i.options[0].replace(st,function(e,i,n,r,a,o){if(i)t.minimumIntegerDigits=n.length;else{if(r&&a)throw new Error("We currently do not support maximum integer digits");if(o)throw new Error("We currently do not support exact integer digits")}return""});continue}if(lt.test(i.stem)){t.minimumIntegerDigits=i.stem.length;continue}if(at.test(i.stem)){if(i.options.length>1)throw new RangeError("Fraction-precision stems only accept a single optional option");i.stem.replace(at,function(e,i,n,r,a,o){return"*"===n?t.minimumFractionDigits=i.length:r&&"#"===r[0]?t.maximumFractionDigits=r.length:a&&o?(t.minimumFractionDigits=a.length,t.maximumFractionDigits=a.length+o.length):(t.minimumFractionDigits=i.length,t.maximumFractionDigits=i.length),""});const e=i.options[0];"w"===e?t={...t,trailingZeroDisplay:"stripIfInteger"}:e&&(t={...t,...ct(e)});continue}if(ot.test(i.stem)){t={...t,...ct(i.stem)};continue}const e=ht(i.stem);e&&(t={...t,...e});const n=ut(i.stem);n&&(t={...t,...n})}return t}let gt=function(e){return e[e.EXPECT_ARGUMENT_CLOSING_BRACE=1]="EXPECT_ARGUMENT_CLOSING_BRACE",e[e.EMPTY_ARGUMENT=2]="EMPTY_ARGUMENT",e[e.MALFORMED_ARGUMENT=3]="MALFORMED_ARGUMENT",e[e.EXPECT_ARGUMENT_TYPE=4]="EXPECT_ARGUMENT_TYPE",e[e.INVALID_ARGUMENT_TYPE=5]="INVALID_ARGUMENT_TYPE",e[e.EXPECT_ARGUMENT_STYLE=6]="EXPECT_ARGUMENT_STYLE",e[e.INVALID_NUMBER_SKELETON=7]="INVALID_NUMBER_SKELETON",e[e.INVALID_DATE_TIME_SKELETON=8]="INVALID_DATE_TIME_SKELETON",e[e.EXPECT_NUMBER_SKELETON=9]="EXPECT_NUMBER_SKELETON",e[e.EXPECT_DATE_TIME_SKELETON=10]="EXPECT_DATE_TIME_SKELETON",e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE=11]="UNCLOSED_QUOTE_IN_ARGUMENT_STYLE",e[e.EXPECT_SELECT_ARGUMENT_OPTIONS=12]="EXPECT_SELECT_ARGUMENT_OPTIONS",e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE=13]="EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE=14]="INVALID_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR=15]="EXPECT_SELECT_ARGUMENT_SELECTOR",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR=16]="EXPECT_PLURAL_ARGUMENT_SELECTOR",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT=17]="EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT=18]="EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT",e[e.INVALID_PLURAL_ARGUMENT_SELECTOR=19]="INVALID_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR=20]="DUPLICATE_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR=21]="DUPLICATE_SELECT_ARGUMENT_SELECTOR",e[e.MISSING_OTHER_CLAUSE=22]="MISSING_OTHER_CLAUSE",e[e.INVALID_TAG=23]="INVALID_TAG",e[e.INVALID_TAG_NAME=25]="INVALID_TAG_NAME",e[e.UNMATCHED_CLOSING_TAG=26]="UNMATCHED_CLOSING_TAG",e[e.UNCLOSED_TAG=27]="UNCLOSED_TAG",e}({});function mt(e){return 0===e.type}function ft(e){return 1===e.type}function bt(e){return 2===e.type}function _t(e){return 3===e.type}function yt(e){return 4===e.type}function vt(e){return 5===e.type}function wt(e){return 6===e.type}function kt(e){return 7===e.type}function xt(e){return 8===e.type}function Et(e){return!(!e||"object"!=typeof e||0!==e.type)}function St(e){return!(!e||"object"!=typeof e||1!==e.type)}const $t=/[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/,At={"001":["H","h"],419:["h","H","hB","hb"],AC:["H","h","hb","hB"],AD:["H","hB"],AE:["h","hB","hb","H"],AF:["H","hb","hB","h"],AG:["h","hb","H","hB"],AI:["H","h","hb","hB"],AL:["h","H","hB"],AM:["H","hB"],AO:["H","hB"],AR:["h","H","hB","hb"],AS:["h","H"],AT:["H","hB"],AU:["h","hb","H","hB"],AW:["H","hB"],AX:["H"],AZ:["H","hB","h"],BA:["H","hB","h"],BB:["h","hb","H","hB"],BD:["h","hB","H"],BE:["H","hB"],BF:["H","hB"],BG:["H","hB","h"],BH:["h","hB","hb","H"],BI:["H","h"],BJ:["H","hB"],BL:["H","hB"],BM:["h","hb","H","hB"],BN:["hb","hB","h","H"],BO:["h","H","hB","hb"],BQ:["H"],BR:["H","hB"],BS:["h","hb","H","hB"],BT:["h","H"],BW:["H","h","hb","hB"],BY:["H","h"],BZ:["H","h","hb","hB"],CA:["h","hb","H","hB"],CC:["H","h","hb","hB"],CD:["hB","H"],CF:["H","h","hB"],CG:["H","hB"],CH:["H","hB","h"],CI:["H","hB"],CK:["H","h","hb","hB"],CL:["h","H","hB","hb"],CM:["H","h","hB"],CN:["H","hB","hb","h"],CO:["h","H","hB","hb"],CP:["H"],CR:["h","H","hB","hb"],CU:["h","H","hB","hb"],CV:["H","hB"],CW:["H","hB"],CX:["H","h","hb","hB"],CY:["h","H","hb","hB"],CZ:["H"],DE:["H","hB"],DG:["H","h","hb","hB"],DJ:["h","H"],DK:["H"],DM:["h","hb","H","hB"],DO:["h","H","hB","hb"],DZ:["h","hB","hb","H"],EA:["H","h","hB","hb"],EC:["h","H","hB","hb"],EE:["H","hB"],EG:["h","hB","hb","H"],EH:["h","hB","hb","H"],ER:["h","H"],ES:["H","hB","h","hb"],ET:["hB","hb","h","H"],FI:["H"],FJ:["h","hb","H","hB"],FK:["H","h","hb","hB"],FM:["h","hb","H","hB"],FO:["H","h"],FR:["H","hB"],GA:["H","hB"],GB:["H","h","hb","hB"],GD:["h","hb","H","hB"],GE:["H","hB","h"],GF:["H","hB"],GG:["H","h","hb","hB"],GH:["h","H"],GI:["H","h","hb","hB"],GL:["H","h"],GM:["h","hb","H","hB"],GN:["H","hB"],GP:["H","hB"],GQ:["H","hB","h","hb"],GR:["h","H","hb","hB"],GS:["H","h","hb","hB"],GT:["h","H","hB","hb"],GU:["h","hb","H","hB"],GW:["H","hB"],GY:["h","hb","H","hB"],HK:["h","hB","hb","H"],HN:["h","H","hB","hb"],HR:["H","hB"],HU:["H","h"],IC:["H","h","hB","hb"],ID:["H"],IE:["H","h","hb","hB"],IL:["H","hB"],IM:["H","h","hb","hB"],IN:["h","H"],IO:["H","h","hb","hB"],IQ:["h","hB","hb","H"],IR:["hB","H"],IS:["H"],IT:["H","hB"],JE:["H","h","hb","hB"],JM:["h","hb","H","hB"],JO:["h","hB","hb","H"],JP:["H","K","h"],KE:["hB","hb","H","h"],KG:["H","h","hB","hb"],KH:["hB","h","H","hb"],KI:["h","hb","H","hB"],KM:["H","h","hB","hb"],KN:["h","hb","H","hB"],KP:["h","H","hB","hb"],KR:["h","H","hB","hb"],KW:["h","hB","hb","H"],KY:["h","hb","H","hB"],KZ:["H","hB"],LA:["H","hb","hB","h"],LB:["h","hB","hb","H"],LC:["h","hb","H","hB"],LI:["H","hB","h"],LK:["H","h","hB","hb"],LR:["h","hb","H","hB"],LS:["h","H"],LT:["H","h","hb","hB"],LU:["H","h","hB"],LV:["H","hB","hb","h"],LY:["h","hB","hb","H"],MA:["H","h","hB","hb"],MC:["H","hB"],MD:["H","hB"],ME:["H","hB","h"],MF:["H","hB"],MG:["H","h"],MH:["h","hb","H","hB"],MK:["H","h","hb","hB"],ML:["H"],MM:["hB","hb","H","h"],MN:["H","h","hb","hB"],MO:["h","hB","hb","H"],MP:["h","hb","H","hB"],MQ:["H","hB"],MR:["h","hB","hb","H"],MS:["H","h","hb","hB"],MT:["H","h"],MU:["H","h"],MV:["H","h"],MW:["h","hb","H","hB"],MX:["h","H","hB","hb"],MY:["hb","hB","h","H"],MZ:["H","hB"],NA:["h","H","hB","hb"],NC:["H","hB"],NE:["H"],NF:["H","h","hb","hB"],NG:["H","h","hb","hB"],NI:["h","H","hB","hb"],NL:["H","hB"],NO:["H","h"],NP:["H","h","hB"],NR:["H","h","hb","hB"],NU:["H","h","hb","hB"],NZ:["h","hb","H","hB"],OM:["h","hB","hb","H"],PA:["h","H","hB","hb"],PE:["h","H","hB","hb"],PF:["H","h","hB"],PG:["h","H"],PH:["h","hB","hb","H"],PK:["h","hB","H"],PL:["H","h"],PM:["H","hB"],PN:["H","h","hb","hB"],PR:["h","H","hB","hb"],PS:["h","hB","hb","H"],PT:["H","hB"],PW:["h","H"],PY:["h","H","hB","hb"],QA:["h","hB","hb","H"],RE:["H","hB"],RO:["H","hB"],RS:["H","hB","h"],RU:["H"],RW:["H","h"],SA:["h","hB","hb","H"],SB:["h","hb","H","hB"],SC:["H","h","hB"],SD:["h","hB","hb","H"],SE:["H"],SG:["h","hb","H","hB"],SH:["H","h","hb","hB"],SI:["H","hB"],SJ:["H"],SK:["H"],SL:["h","hb","H","hB"],SM:["H","h","hB"],SN:["H","h","hB"],SO:["h","H"],SR:["H","hB"],SS:["h","hb","H","hB"],ST:["H","hB"],SV:["h","H","hB","hb"],SX:["H","h","hb","hB"],SY:["h","hB","hb","H"],SZ:["h","hb","H","hB"],TA:["H","h","hb","hB"],TC:["h","hb","H","hB"],TD:["h","H","hB"],TF:["H","h","hB"],TG:["H","hB"],TH:["H","h"],TJ:["H","h"],TL:["H","hB","hb","h"],TM:["H","h"],TN:["h","hB","hb","H"],TO:["h","H"],TR:["H","hB"],TT:["h","hb","H","hB"],TW:["hB","hb","h","H"],TZ:["hB","hb","H","h"],UA:["H","hB","h"],UG:["hB","hb","H","h"],UM:["h","hb","H","hB"],US:["h","hb","H","hB"],UY:["h","H","hB","hb"],UZ:["H","hB","h"],VA:["H","h","hB"],VC:["h","hb","H","hB"],VE:["h","H","hB","hb"],VG:["h","hb","H","hB"],VI:["h","hb","H","hB"],VN:["H","h"],VU:["h","H"],WF:["H","hB"],WS:["h","H"],XK:["H","hB","h"],YE:["h","hB","hb","H"],YT:["H","hB"],ZA:["H","h","hb","hB"],ZM:["h","hb","H","hB"],ZW:["H","h"],"af-ZA":["H","h","hB","hb"],"ar-001":["h","hB","hb","H"],"ca-ES":["H","h","hB"],"en-001":["h","hb","H","hB"],"en-HK":["h","hb","H","hB"],"en-IL":["H","h","hb","hB"],"en-MY":["h","hb","H","hB"],"es-BR":["H","h","hB","hb"],"es-ES":["H","h","hB","hb"],"es-GQ":["H","h","hB","hb"],"fr-CA":["H","h","hB"],"gl-ES":["H","h","hB"],"gu-IN":["hB","hb","h","H"],"hi-IN":["hB","h","H"],"it-CH":["H","h","hB"],"it-IT":["H","h","hB"],"kn-IN":["hB","h","H"],"ku-SY":["H","hB"],"ml-IN":["hB","h","H"],"mr-IN":["hB","hb","h","H"],"pa-IN":["hB","hb","h","H"],"ta-IN":["hB","h","hb","H"],"te-IN":["hB","h","H"],"zu-ZA":["H","hB","hb","h"]};function zt(e){let t=e.hourCycle;if(void 0===t&&e.hourCycles&&e.hourCycles.length&&(t=e.hourCycles[0]),t)switch(t){case"h24":return"k";case"h23":return"H";case"h12":return"h";case"h11":return"K";default:throw new Error("Invalid hourCycle")}const i=e.language;let n;return"root"!==i&&(n=e.maximize().region),(At[n||""]||At[i||""]||At[`${i}-001`]||At["001"])[0]}const Ht=new RegExp(`^${$t.source}*`),Tt=new RegExp(`${$t.source}*$`);function Ct(e,t){return{start:e,end:t}}const Bt=!!Object.fromEntries,Pt=!!String.prototype.trimStart,Lt=!!String.prototype.trimEnd,Mt=Bt?Object.fromEntries:function(e){const t={};for(const[i,n]of e)t[i]=n;return t},It=Pt?function(e){return e.trimStart()}:function(e){return e.replace(Ht,"")},Nt=Lt?function(e){return e.trimEnd()}:function(e){return e.replace(Tt,"")},Dt=new RegExp("([^\\p{White_Space}\\p{Pattern_Syntax}]*)","yu");var Rt=class{constructor(e,t={}){this.message=e,this.position={offset:0,line:1,column:1},this.ignoreTag=!!t.ignoreTag,this.locale=t.locale,this.requiresOtherClause=!!t.requiresOtherClause,this.shouldParseSkeletons=!!t.shouldParseSkeletons}parse(){if(0!==this.offset())throw Error("parser can only be used once");if(this.message.length>0){const e=this.message.charCodeAt(0);if(35!==e&&39!==e&&60!==e&&123!==e&&125!==e){const e=function(e){if(0===e.length)return null;let t=1,i=1;for(let n=0;n<e.length;){const r=e.charCodeAt(n);switch(r){case 35:case 39:case 60:case 123:case 125:return null}if(10===r)t++,i=1,n++;else if(i++,r>=55296&&r<=56319&&n+1<e.length){const t=e.charCodeAt(n+1);n+=t>=56320&&t<=57343?2:1}else n++}return{offset:e.length,line:t,column:i}}(this.message);if(e){const t=this.clonePosition();return this.position=e,{val:[{type:0,value:this.message,location:Ct(t,this.clonePosition())}],err:null}}}}return this.parseMessage(0,"",!1)}parseMessage(e,t,i){let n=[];for(;!this.isEOF();){const r=this.char();if(123===r){const t=this.parseArgument(e,i);if(t.err)return t;n.push(t.val)}else{if(125===r&&e>0)break;if(35!==r||"plural"!==t&&"selectordinal"!==t){if(60===r&&!this.ignoreTag&&47===this.peek()){if(i)break;return this.error(26,Ct(this.clonePosition(),this.clonePosition()))}if(60===r&&!this.ignoreTag&&Ot(this.peek()||0)){const i=this.parseTag(e,t);if(i.err)return i;n.push(i.val)}else{const i=this.parseLiteral(e,t);if(i.err)return i;n.push(i.val)}}else{const e=this.clonePosition();this.bump(),n.push({type:7,location:Ct(e,this.clonePosition())})}}}return{val:n,err:null}}parseTag(e,t){const i=this.clonePosition();this.bump();const n=this.parseTagName();if(this.bumpSpace(),this.bumpIf("/>"))return{val:{type:0,value:`<${n}/>`,location:Ct(i,this.clonePosition())},err:null};if(this.bumpIf(">")){const r=this.parseMessage(e+1,t,!0);if(r.err)return r;const a=r.val,o=this.clonePosition();if(this.bumpIf("</")){if(this.isEOF()||!Ot(this.char()))return this.error(23,Ct(o,this.clonePosition()));const e=this.clonePosition();return n!==this.parseTagName()?this.error(26,Ct(e,this.clonePosition())):(this.bumpSpace(),this.bumpIf(">")?{val:{type:8,value:n,children:a,location:Ct(i,this.clonePosition())},err:null}:this.error(23,Ct(o,this.clonePosition())))}return this.error(27,Ct(i,this.clonePosition()))}return this.error(23,Ct(i,this.clonePosition()))}parseTagName(){const e=this.offset();for(this.bump();!this.isEOF()&&Ut(this.char());)this.bump();return this.message.slice(e,this.offset())}parseLiteral(e,t){const i=this.clonePosition();let n="";for(;;){const i=this.tryParseQuote(t);if(i){n+=i;continue}const r=this.tryParseUnquoted(e,t);if(r){n+=r;continue}const a=this.tryParseLeftAngleBracket();if(!a)break;n+=a}return{val:{type:0,value:n,location:Ct(i,this.clonePosition())},err:null}}tryParseLeftAngleBracket(){return this.isEOF()||60!==this.char()||!this.ignoreTag&&(Ot(e=this.peek()||0)||47===e)?null:(this.bump(),"<");var e}tryParseQuote(e){if(this.isEOF()||39!==this.char())return null;switch(this.peek()){case 39:return this.bump(),this.bump(),"'";case 123:case 60:case 62:case 125:break;case 35:if("plural"===e||"selectordinal"===e)break;return null;default:return null}this.bump();const t=[this.char()];for(this.bump();!this.isEOF();){const e=this.char();if(39===e){if(39!==this.peek()){this.bump();break}t.push(39),this.bump()}else t.push(e);this.bump()}return String.fromCodePoint(...t)}tryParseUnquoted(e,t){if(this.isEOF())return null;const i=this.char();return 60===i||123===i||35===i&&("plural"===t||"selectordinal"===t)||125===i&&e>0?null:(this.bump(),String.fromCodePoint(i))}parseArgument(e,t){const i=this.clonePosition();if(this.bump(),this.bumpSpace(),this.isEOF())return this.error(1,Ct(i,this.clonePosition()));if(125===this.char())return this.bump(),this.error(2,Ct(i,this.clonePosition()));let n=this.parseIdentifierIfPossible().value;if(!n)return this.error(3,Ct(i,this.clonePosition()));if(this.bumpSpace(),this.isEOF())return this.error(1,Ct(i,this.clonePosition()));switch(this.char()){case 125:return this.bump(),{val:{type:1,value:n,location:Ct(i,this.clonePosition())},err:null};case 44:return this.bump(),this.bumpSpace(),this.isEOF()?this.error(1,Ct(i,this.clonePosition())):this.parseArgumentOptions(e,t,n,i);default:return this.error(3,Ct(i,this.clonePosition()))}}parseIdentifierIfPossible(){const e=this.clonePosition(),t=this.offset(),i=function(e,t){return Dt.lastIndex=t,Dt.exec(e)[1]??""}(this.message,t),n=t+i.length;return this.bumpTo(n),{value:i,location:Ct(e,this.clonePosition())}}parseArgumentOptions(e,t,i,n){let r=this.clonePosition(),a=this.parseIdentifierIfPossible().value,o=this.clonePosition();switch(a){case"":return this.error(4,Ct(r,o));case"number":case"date":case"time":{this.bumpSpace();let e=null;if(this.bumpIf(",")){this.bumpSpace();const t=this.clonePosition(),i=this.parseSimpleArgStyleIfPossible();if(i.err)return i;const n=Nt(i.val);if(0===n.length)return this.error(6,Ct(this.clonePosition(),this.clonePosition()));e={style:n,styleLocation:Ct(t,this.clonePosition())}}const t=this.tryParseArgumentClose(n);if(t.err)return t;const r=Ct(n,this.clonePosition());if(e&&e.style.startsWith("::")){let t=It(e.style.slice(2));if("number"===a){const n=this.parseNumberSkeletonFromString(t,e.styleLocation);return n.err?n:{val:{type:2,value:i,location:r,style:n.val},err:null}}{if(0===t.length)return this.error(10,r);let n=t;this.locale&&(n=function(e,t){let i="";for(let n=0;n<e.length;n++){const r=e.charAt(n);if("j"===r){let a=0;for(;n+1<e.length&&e.charAt(n+1)===r;)a++,n++;let o=1+(1&a),s=a<2?1:3+(a>>1),l="a",c=zt(t);for("H"!=c&&"k"!=c||(s=0);s-- >0;)i+=l;for(;o-- >0;)i=c+i}else i+="J"===r?"H":r}return i}(t,this.locale));return{val:{type:"date"===a?3:4,value:i,location:r,style:{type:1,pattern:n,location:e.styleLocation,parsedOptions:this.shouldParseSkeletons?it(n):{}}},err:null}}}return{val:{type:"number"===a?2:"date"===a?3:4,value:i,location:r,style:e?.style??null},err:null}}case"plural":case"selectordinal":case"select":{const r=this.clonePosition();if(this.bumpSpace(),!this.bumpIf(","))return this.error(12,Ct(r,{...r}));this.bumpSpace();let o=this.parseIdentifierIfPossible(),s=0;if("select"!==a&&"offset"===o.value){if(!this.bumpIf(":"))return this.error(13,Ct(this.clonePosition(),this.clonePosition()));this.bumpSpace();const e=this.tryParseDecimalInteger(13,14);if(e.err)return e;this.bumpSpace(),o=this.parseIdentifierIfPossible(),s=e.val}const l=this.tryParsePluralOrSelectOptions(e,a,t,o);if(l.err)return l;const c=this.tryParseArgumentClose(n);if(c.err)return c;const h=Ct(n,this.clonePosition());return"select"===a?{val:{type:5,value:i,options:Mt(l.val),location:h},err:null}:{val:{type:6,value:i,options:Mt(l.val),offset:s,pluralType:"plural"===a?"cardinal":"ordinal",location:h},err:null}}default:return this.error(5,Ct(r,o))}}tryParseArgumentClose(e){return this.isEOF()||125!==this.char()?this.error(1,Ct(e,this.clonePosition())):(this.bump(),{val:!0,err:null})}parseSimpleArgStyleIfPossible(){let e=0;const t=this.clonePosition();for(;!this.isEOF();)switch(this.char()){case 39:{this.bump();let e=this.clonePosition();if(!this.bumpUntil("'"))return this.error(11,Ct(e,this.clonePosition()));this.bump();break}case 123:e+=1,this.bump();break;case 125:if(!(e>0))return{val:this.message.slice(t.offset,this.offset()),err:null};e-=1;break;default:this.bump()}return{val:this.message.slice(t.offset,this.offset()),err:null}}parseNumberSkeletonFromString(e,t){let i=[];try{i=function(e){if(0===e.length)throw new Error("Number skeleton cannot be empty");const t=e.split(nt).filter(e=>e.length>0),i=[];for(const e of t){let t=e.split("/");if(0===t.length)throw new Error("Invalid number skeleton");const[n,...r]=t;for(const e of r)if(0===e.length)throw new Error("Invalid number skeleton");i.push({stem:n,options:r})}return i}(e)}catch{return this.error(7,t)}return{val:{type:0,tokens:i,location:t,parsedOptions:this.shouldParseSkeletons?pt(i):{}},err:null}}tryParsePluralOrSelectOptions(e,t,i,n){let r=!1;const a=[],o=new Set;let{value:s,location:l}=n;for(;;){if(0===s.length){const e=this.clonePosition();if("select"===t||!this.bumpIf("="))break;{const t=this.tryParseDecimalInteger(16,19);if(t.err)return t;l=Ct(e,this.clonePosition()),s=this.message.slice(e.offset,this.offset())}}if(o.has(s))return this.error("select"===t?21:20,l);"other"===s&&(r=!0),this.bumpSpace();const n=this.clonePosition();if(!this.bumpIf("{"))return this.error("select"===t?17:18,Ct(this.clonePosition(),this.clonePosition()));const c=this.parseMessage(e+1,t,i);if(c.err)return c;const h=this.tryParseArgumentClose(n);if(h.err)return h;a.push([s,{value:c.val,location:Ct(n,this.clonePosition())}]),o.add(s),this.bumpSpace(),({value:s,location:l}=this.parseIdentifierIfPossible())}return 0===a.length?this.error("select"===t?15:16,Ct(this.clonePosition(),this.clonePosition())):this.requiresOtherClause&&!r?this.error(22,Ct(this.clonePosition(),this.clonePosition())):{val:a,err:null}}tryParseDecimalInteger(e,t){let i=1;const n=this.clonePosition();this.bumpIf("+")||this.bumpIf("-")&&(i=-1);let r=!1,a=0;for(;!this.isEOF();){const e=this.char();if(!(e>=48&&e<=57))break;r=!0,a=10*a+(e-48),this.bump()}const o=Ct(n,this.clonePosition());return r?(a*=i,Number.isSafeInteger(a)?{val:a,err:null}:this.error(t,o)):this.error(e,o)}offset(){return this.position.offset}isEOF(){return this.offset()===this.message.length}clonePosition(){return{offset:this.position.offset,line:this.position.line,column:this.position.column}}char(){const e=this.position.offset;if(e>=this.message.length)throw Error("out of bound");const t=this.message.codePointAt(e);if(void 0===t)throw Error(`Offset ${e} is at invalid UTF-16 code unit boundary`);return t}error(e,t){return{val:null,err:{kind:e,message:this.message,location:t}}}bump(){if(this.isEOF())return;const e=this.char();10===e?(this.position.line+=1,this.position.column=1,this.position.offset+=1):(this.position.column+=1,this.position.offset+=e<65536?1:2)}bumpIf(e){if(this.message.startsWith(e,this.offset())){for(let t=0;t<e.length;t++)this.bump();return!0}return!1}bumpUntil(e){const t=this.offset(),i=this.message.indexOf(e,t);return i>=0?(this.bumpTo(i),!0):(this.bumpTo(this.message.length),!1)}bumpTo(e){if(this.offset()>e)throw Error(`targetOffset ${e} must be greater than or equal to the current offset ${this.offset()}`);for(e=Math.min(e,this.message.length);;){const t=this.offset();if(t===e)break;if(t>e)throw Error(`targetOffset ${e} is at invalid UTF-16 code unit boundary`);if(this.bump(),this.isEOF())break}}bumpSpace(){for(;!this.isEOF()&&Ft(this.char());)this.bump()}peek(){if(this.isEOF())return null;const e=this.char(),t=this.offset();return this.message.charCodeAt(t+(e>=65536?2:1))??null}};function Ot(e){return e>=97&&e<=122||e>=65&&e<=90}function Ut(e){return 45===e||46===e||e>=48&&e<=57||95===e||e>=97&&e<=122||e>=65&&e<=90||183==e||e>=192&&e<=214||e>=216&&e<=246||e>=248&&e<=893||e>=895&&e<=8191||e>=8204&&e<=8205||e>=8255&&e<=8256||e>=8304&&e<=8591||e>=11264&&e<=12271||e>=12289&&e<=55295||e>=63744&&e<=64975||e>=65008&&e<=65533||e>=65536&&e<=983039}function Ft(e){return e>=9&&e<=13||32===e||133===e||e>=8206&&e<=8207||8232===e||8233===e}function Gt(e){e.forEach(e=>{if(delete e.location,vt(e)||wt(e))for(const t in e.options)delete e.options[t].location,Gt(e.options[t].value);else bt(e)&&Et(e.style)||(_t(e)||yt(e))&&St(e.style)?delete e.style.location:xt(e)&&Gt(e.children)})}function Wt(e,t={}){t={shouldParseSkeletons:!0,requiresOtherClause:!0,...t};const i=new Rt(e,t).parse();if(i.err){const e=SyntaxError(gt[i.err.kind]);throw e.location=i.err.location,e.originalMessage=i.err.message,e}return t?.captureLocation||Gt(i.val),i.val}var Zt=class extends Error{constructor(e,t,i){super(e),this.code=t,this.originalMessage=i}toString(){return`[formatjs Error: ${this.code}] ${this.message}`}},jt=class extends Zt{constructor(e,t,i,n){super(`Invalid values for "${e}": "${t}". Options are "${Object.keys(i).join('", "')}"`,"INVALID_VALUE",n)}},Vt=class extends Zt{constructor(e,t,i){super(`Value for "${e}" must be of type ${t}`,"INVALID_VALUE",i)}},qt=class extends Zt{constructor(e,t){super(`The intl string context variable "${e}" was not provided to the string "${t}"`,"MISSING_VALUE",t)}};function Kt(e){return"function"==typeof e}function Yt(e,t,i,n,r,a,o){if(1===e.length&&mt(e[0]))return[{type:0,value:e[0].value}];const s=[];for(const l of e){if(mt(l)){s.push({type:0,value:l.value});continue}if(kt(l)){"number"==typeof a&&s.push({type:0,value:i.getNumberFormat(t).format(a)});continue}const{value:e}=l;if(!r||!(e in r))throw new qt(e,o);let c=r[e];if(ft(l))c&&"string"!=typeof c&&"number"!=typeof c&&"bigint"!=typeof c||(c="string"==typeof c||"number"==typeof c||"bigint"==typeof c?String(c):""),s.push({type:"string"==typeof c?0:1,value:c});else{if(_t(l)){const e="string"==typeof l.style?n.date[l.style]:St(l.style)?l.style.parsedOptions:void 0;s.push({type:0,value:i.getDateTimeFormat(t,e).format(c)});continue}if(yt(l)){const e="string"==typeof l.style?n.time[l.style]:St(l.style)?l.style.parsedOptions:n.time.medium;s.push({type:0,value:i.getDateTimeFormat(t,e).format(c)});continue}if(bt(l)){const e="string"==typeof l.style?n.number[l.style]:Et(l.style)?l.style.parsedOptions:void 0;if(e&&e.scale){const t=e.scale||1;if("bigint"==typeof c){if(!Number.isInteger(t))throw new TypeError(`Cannot apply fractional scale ${t} to bigint value. Scale must be an integer when formatting bigint.`);c*=BigInt(t)}else c*=t}s.push({type:0,value:i.getNumberFormat(t,e).format(c)});continue}if(xt(l)){const{children:e,value:c}=l,h=r[c];if(!Kt(h))throw new Vt(c,"function",o);let u=h(Yt(e,t,i,n,r,a).map(e=>e.value));Array.isArray(u)||(u=[u]),s.push(...u.map(e=>({type:"string"==typeof e?0:1,value:e})))}if(vt(l)){const e=c,a=(Object.prototype.hasOwnProperty.call(l.options,e)?l.options[e]:void 0)||l.options.other;if(!a)throw new jt(l.value,c,Object.keys(l.options),o);s.push(...Yt(a.value,t,i,n,r));continue}if(wt(l)){const e=`=${c}`;let a=Object.prototype.hasOwnProperty.call(l.options,e)?l.options[e]:void 0;if(!a){if(!Intl.PluralRules)throw new Zt('Intl.PluralRules is not available in this environment.\nTry polyfilling it using "@formatjs/intl-pluralrules"\n',"MISSING_INTL_API",o);const e="bigint"==typeof c?Number(c):c,n=i.getPluralRules(t,{type:l.pluralType}).select(e-(l.offset||0));a=(Object.prototype.hasOwnProperty.call(l.options,n)?l.options[n]:void 0)||l.options.other}if(!a)throw new jt(l.value,c,Object.keys(l.options),o);const h="bigint"==typeof c?Number(c):c;s.push(...Yt(a.value,t,i,n,r,h-(l.offset||0)));continue}}}return(l=s).length<2?l:l.reduce((e,t)=>{const i=e[e.length-1];return i&&0===i.type&&0===t.type?i.value+=t.value:e.push(t),e},[]);var l}function Xt(e,t){return t?Object.keys(e).reduce((i,n)=>{var r,a;return i[n]=(r=e[n],(a=t[n])?{...r,...a,...Object.keys(r).reduce((e,t)=>(e[t]={...r[t],...a[t]},e),{})}:r),i},{...e}):e}function Jt(e){return{create:()=>({get:t=>e[t],set(t,i){e[t]=i}})}}var Qt=class e{constructor(t,i=e.defaultLocale,n,r){if(this.formatterCache={number:{},dateTime:{},pluralRules:{}},this.format=e=>{const t=this.formatToParts(e);if(1===t.length)return t[0].value;const i=t.reduce((e,t)=>(e.length&&0===t.type&&"string"==typeof e[e.length-1]?e[e.length-1]+=t.value:e.push(t.value),e),[]);return i.length<=1?i[0]||"":i},this.formatToParts=e=>Yt(this.ast,this.locales,this.formatters,this.formats,e,void 0,this.message),this.resolvedOptions=()=>({locale:this.resolvedLocale?.toString()||Intl.NumberFormat.supportedLocalesOf(this.locales)[0]}),this.getAst=()=>this.ast,this.locales=i,this.resolvedLocale=e.resolveLocale(i),"string"==typeof t){if(this.message=t,!e.__parse)throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");const{...i}=r||{};this.ast=e.__parse(t,{...i,locale:this.resolvedLocale})}else this.ast=t;if(!Array.isArray(this.ast))throw new TypeError("A message must be provided as a String or AST.");this.formats=Xt(e.formats,n),this.formatters=r&&r.formatters||function(e={number:{},dateTime:{},pluralRules:{}}){return{getNumberFormat:je((...e)=>new Intl.NumberFormat(...e),{cache:Jt(e.number),strategy:et.variadic}),getDateTimeFormat:je((...e)=>new Intl.DateTimeFormat(...e),{cache:Jt(e.dateTime),strategy:et.variadic}),getPluralRules:je((...e)=>new Intl.PluralRules(...e),{cache:Jt(e.pluralRules),strategy:et.variadic})}}(this.formatterCache)}static{this.memoizedDefaultLocale=null}static get defaultLocale(){return e.memoizedDefaultLocale||(e.memoizedDefaultLocale=(new Intl.NumberFormat).resolvedOptions().locale),e.memoizedDefaultLocale}static{this.resolveLocale=e=>{if(void 0===Intl.Locale)return;const t=Intl.NumberFormat.supportedLocalesOf(e);return t.length>0?new Intl.Locale(t[0]):new Intl.Locale("string"==typeof e?e:e[0])}}static{this.__parse=Wt}static{this.formats={number:{integer:{maximumFractionDigits:0},currency:{style:"currency"},percent:{style:"percent"}},date:{short:{month:"numeric",day:"numeric",year:"2-digit"},medium:{month:"short",day:"numeric",year:"numeric"},long:{month:"long",day:"numeric",year:"numeric"},full:{weekday:"long",month:"long",day:"numeric",year:"numeric"}},time:{short:{hour:"numeric",minute:"numeric"},medium:{hour:"numeric",minute:"numeric",second:"numeric"},long:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"},full:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"}}}}};const ei={en:Ze},ti={};function ii(e){return e.replace(/['"]+/g,"").split(/[-_]/)[0].toLowerCase()}function ni(e){const t=ii(e);return t in ei||!_e.includes(t)}function ri(e,t,...i){const n=ii(t);let r;try{r=e.split(".").reduce((e,t)=>e[t],ei[n])}catch(t){r=e.split(".").reduce((e,t)=>e[t],ei.en)}if(void 0===r&&(r=e.split(".").reduce((e,t)=>e[t],ei.en)),!i.length)return r;const a={};for(let e=0;e<i.length;e+=2){let t=i[e];t=t.replace(/^{([^}]+)?}$/,"$1"),a[t]=i[e+1]}try{return new Qt(r,t).format(a)}catch(e){return"Translation "+e}}function ai(e,t){switch(t){case"drainage_rate":return e.units==ye?W`${He("mm/h")}`:W`${He("in/h")}`;case"precipitation_threshold_mm":case ve:return e.units==ye?W`${He("mm")}`:W`${He("in")}`;case"size":return e.units==ye?W`${He("m<sup>2</sup>")}`:W`${He("sq ft")}`;case"throughput":return e.units==ye?W`${He("l/minute")}`:W`${He("gal/minute")}`;default:return W``}}const oi=(e,t,i=!1)=>{var n,r,a;i?history.replaceState(null,"",t):history.pushState(null,"",t),n=window,r="location-changed",a={replace:i},n.dispatchEvent(new CustomEvent(r,{detail:a,bubbles:!0,composed:!0,cancelable:!1}))};function si(e){var t;if(!e)return"Unknown error";if("string"==typeof e)return e;const i=e;return(null===(t=null==i?void 0:i.body)||void 0===t?void 0:t.message)||(null==i?void 0:i.message)||(null==i?void 0:i.error)||JSON.stringify(e)}function li(e,t){e.dispatchEvent(new CustomEvent("hass-notification",{detail:{message:t},bubbles:!0,composed:!0}))}function ci(e,t,i,n){var r;li(e,`${ri(i,null!==(r=null==t?void 0:t.language)&&void 0!==r?r:"en")}: ${si(n)}`)}const hi=(e,...t)=>{let i={page:e,params:{}};t.forEach(e=>{"string"==typeof e?i=Object.assign(Object.assign({},i),{subpage:e}):"params"in e?i=Object.assign(Object.assign({},i),{params:e.params}):"filter"in e&&(i=Object.assign(Object.assign({},i),{filter:e.filter}))});const n=e=>{let t=Object.keys(e);t=t.filter(t=>e[t]),t.sort();let i="";return t.forEach(t=>{const n=e[t];i=i.length?`${i}/${t}/${n}`:`${t}/${n}`}),i};let r=`/${be}/${i.page}`;return i.subpage&&(r=`${r}/${i.subpage}`),n(i.params).length&&(r=`${r}/${n(i.params)}`),i.filter&&(r=`${r}/filter/${n(i.filter)}`),r},ui=s`
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
`;s`
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
`;const di=e=>String(e).padStart(2,"0");function pi(e){return e instanceof Date?e:new Date(e)}function gi(e){const t=pi(e);return`${di(t.getHours())}:${di(t.getMinutes())}`}function mi(e){const t=pi(e);return`${t.getFullYear()}-${di(t.getMonth()+1)}-${di(t.getDate())} ${di(t.getHours())}:${di(t.getMinutes())}`}function fi(e,t){return e.getFullYear()===t.getFullYear()&&e.getMonth()===t.getMonth()&&e.getDate()===t.getDate()}class bi extends(xe(le)){constructor(){super(...arguments),this.hideSettingsLinks=!1,this.actionsMode="full",this.zones=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._operationError=null,this._confirmIrrigate=null,this._skipDetailsOpen=!1,this._runMinutes={},this._updateScheduled=!1}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}firstUpdated(){fe().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:be+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[i,n,r]=await Promise.all([(t=this.hass,t.callWS({type:be+"/config"})),we(this.hass),ke(this.hass).catch(e=>{console.error("Failed to fetch irrigation outlook:",e)})]);this.config=i,this.zones=n,this._outlook=r,this._initialLoadDone=!0}catch(e){console.error("Error fetching data:",e),ci(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}var t}handleCalculateAllZones(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",be+"/zones",{calculate_all:!0})).catch(e=>{console.error("Failed to calculate all zones:",e),ci(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after calc-all:",e))}))}handleUpdateAllZones(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",be+"/zones",{update_all:!0})).catch(e=>{console.error("Failed to update all zones:",e),ci(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after update-all:",e))}))}get _linkedZoneCount(){return this.zones.filter(e=>{var t;return e.linked_entity&&(null!==(t=e.duration)&&void 0!==t?t:0)>0}).length}async _doIrrigate(){var e;const t=this._confirmIrrigate;if(this._confirmIrrigate=null,null===t||!this.hass)return;const i="all"===t,n=i?void 0:this.zones.find(e=>{var i;return(null===(i=e.id)||void 0===i?void 0:i.toString())===t}),r=i?`(${this._linkedZoneCount})`:`: ${null!==(e=null==n?void 0:n.name)&&void 0!==e?e:t}`;try{await(a=this.hass,o=i?void 0:t,a.callWS(Object.assign({type:be+"/irrigate_now"},void 0!==o?{zone_id:o}:{}))),li(this,`${ri("panels.zones.confirm_irrigate.toast_started",this.hass.language)} ${r}`)}catch(e){const t=si(e);console.error("irrigate_now failed",e),li(this,`${ri("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}var a,o}get _rainDelayUntil(){var e;const t=null===(e=this._outlook)||void 0===e?void 0:e.rain_delay_until;if(!t)return null;const i=new Date(t);return i.getTime()>Date.now()?i:null}async _setRainDelay(e){if(this.hass)try{await((e,t)=>e.callWS({type:be+"/set_rain_delay",hours:t}))(this.hass,e),await this._fetchData()}catch(e){console.error("set_rain_delay failed",e),ci(this,this.hass,"common.errors.action_failed",e)}}async _clearRainDelay(){var e;if(this.hass)try{await(e=this.hass,e.callWS({type:be+"/clear_rain_delay"})),await this._fetchData()}catch(e){console.error("clear_rain_delay failed",e),ci(this,this.hass,"common.errors.action_failed",e)}}_zoneRunMinutes(e){var t,i;const n=String(null!==(t=e.id)&&void 0!==t?t:"");return null!==(i=this._runMinutes[n])&&void 0!==i?i:10}async _runZoneFor(e){if(!this.hass||!e.linked_entity||void 0===e.id)return;const t=this._zoneRunMinutes(e);var i,n,r;if(t>0)try{await(i=this.hass,n=e.id.toString(),r=t,i.callWS({type:be+"/run_zone",zone_id:n,duration:r})),li(this,`${ri("panels.zones.run_zone.toast_started",this.hass.language)}: ${e.name} (${t} min)`)}catch(e){const t=si(e);console.error("run_zone failed",e),li(this,`${ri("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}}handleCalculateZone(e){const t=this.zones[e];var i,n;t&&null!=t.id&&this.hass&&(this._operationError=null,this.isSaving=!0,this._scheduleUpdate(),(i=this.hass,n=t.id.toString(),i.callApi("POST",be+"/zones",{id:n,calculate:!0,override_cache:!0})).catch(e=>{const t=si(e);console.error("calculateZone failed:",e),this._operationError=t}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after calc:",e))}))}handleUpdateZone(e){const t=this.zones[e];var i,n;t&&null!=t.id&&this.hass&&(this._operationError=null,this.isSaving=!0,this._scheduleUpdate(),(i=this.hass,n=t.id.toString(),i.callApi("POST",be+"/zones",{id:n,update:!0})).catch(e=>{const t=si(e);console.error("updateZone failed:",e),this._operationError=t}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after update:",e))}))}_openZoneSettings(e){const t=void 0!==e.id?{params:{zone:String(e.id)}}:void 0;oi(0,t?hi("setup","zones",t):hi("setup","zones"))}_runTargetsZone(e,t){return"all"===e.zones||!(!Array.isArray(e.zones)||void 0===t.id)&&e.zones.map(e=>Number(e)).includes(Number(t.id))}get _nextIrrigateRun(){var e;return null===(e=this._outlook)||void 0===e?void 0:e.upcoming_runs.find(e=>"irrigate"===e.action&&e.next_run_utc)}_nextIrrigateRunForZone(e){var t;return null===(t=this._outlook)||void 0===t?void 0:t.upcoming_runs.find(t=>"irrigate"===t.action&&t.next_run_utc&&this._runTargetsZone(t,e))}get _activeGuards(){var e,t;return null!==(t=null===(e=this._outlook)||void 0===e?void 0:e.skip_preview.checks.filter(e=>e.enabled))&&void 0!==t?t:[]}get _triggeredGuards(){return this._activeGuards.filter(e=>e.would_skip)}_zoneHasDeficit(e){var t,i,n;const r=null!==(t=e.duration)&&void 0!==t?t:0,a=Number(null!==(i=e.bucket_threshold)&&void 0!==i?i:0),o=this._zoneEstimate(e),s=o&&o.available&&null!=o.live_deficit?o.live_deficit:Number(null!==(n=e.bucket)&&void 0!==n?n:0);return r>0&&s<a}_formatRunTime(e){if(!this.hass)return"";const t=this.hass.language,i=new Date(e),n=gi(i),r=new Date;return fi(i,r)?`${ri("panels.zones.outlook.today",t)} ${n}`:fi(i,function(e,t){const i=new Date(e.getTime());return i.setDate(i.getDate()+t),i}(r,1))?`${ri("panels.zones.outlook.tomorrow",t)} ${n}`:function(e,t){const i=pi(e);return`${new Intl.DateTimeFormat(t,{weekday:"short"}).format(i)} ${gi(i)}`}(i,t)}_guardLabel(e){return ri(`panels.zones.outlook.checks.${e.id}`,this.hass.language)}_guardDetail(e){var t;return e.available&&null!==e.observed?ri(`panels.zones.outlook.check_detail.${e.id}`,this.hass.language,"{observed}",String(e.observed),"{threshold}",String(null!==(t=e.threshold)&&void 0!==t?t:"")):""}_renderSkipReasons(){const e=this.hass.language;return W`
      <div class="outlook-line outlook-skip-reasons">
        <ul class="skip-reasons">
          ${this._triggeredGuards.map(e=>{const t=this._guardDetail(e);return W`<li>
              ${this._guardLabel(e)}${t?W` — ${t}`:""}
            </li>`})}
        </ul>
      </div>
      <div class="outlook-line outlook-dim skip-reasons-note">
        ${ri("panels.zones.outlook.provisional",e)}
      </div>
    `}_openSchedules(){oi(0,hi("setup","when-to-water"))}_runActionLabel(e){return ri(`panels.zones.outlook.actions.${e.action}`,this.hass.language)}_runTargetsLabel(e){const t=this.hass.language;if("all"===e.zones)return ri("panels.zones.outlook.targets_all",t);const i=Array.isArray(e.zones)?e.zones.length:0;return ri("panels.zones.outlook.targets_zones",t,"{count}",String(i))}_renderOutlookBanner(){if(!this.hass||!this._outlook)return W``;const e=this.hass.language,t=this._nextIrrigateRun,i=this._triggeredGuards,n=this._outlook.last_skip_evaluation;return t&&t.next_run_utc?W`
      <ha-card class="outlook-card">
        <div class="outlook">
          <div class="outlook-line outlook-headline">
            <ha-icon icon="mdi:calendar-clock"></ha-icon>
            <span>
              <strong
                >${ri("panels.zones.outlook.next_run",e)}:</strong
              >
              ${this._runActionLabel(t)}
              ${this._formatRunTime(t.next_run_utc)}
              <span class="outlook-dim"
                >· ${t.name} · ${this._runTargetsLabel(t)}</span
              >
            </span>
          </div>

          ${i.length>0?W`
                <div class="outlook-line outlook-skip">
                  <ha-icon icon="mdi:alert"></ha-icon>
                  <span
                    >${ri("panels.zones.outlook.will_skip",e)}</span
                  >
                  <button
                    class="outlook-info-btn"
                    aria-expanded="${this._skipDetailsOpen}"
                    title="${ri("panels.zones.outlook.why_skipped",e)}"
                    @click="${()=>{this._skipDetailsOpen=!this._skipDetailsOpen}}"
                  >
                    <ha-icon
                      icon="${this._skipDetailsOpen?"mdi:chevron-up":"mdi:information-outline"}"
                    ></ha-icon>
                    <span class="outlook-info-label"
                      >${ri("panels.zones.outlook.why_skipped",e)}</span
                    >
                  </button>
                </div>
                ${this._skipDetailsOpen?this._renderSkipReasons():""}
              `:W`
                <div class="outlook-line outlook-clear">
                  <ha-icon icon="mdi:check-circle-outline"></ha-icon>
                  <span
                    >${ri("panels.zones.outlook.will_run",e)}</span
                  >
                </div>
              `}
          ${n?this._renderLastRunLine(n):""}
        </div>
      </ha-card>
    `:W`
        <ha-card class="outlook-card">
          <div class="outlook">
            <div class="outlook-line outlook-headline">
              <ha-icon icon="mdi:calendar-alert"></ha-icon>
              <span>${ri("panels.zones.outlook.no_schedule",e)}</span>
              ${this.hideSettingsLinks?"":W`
                    <button
                      class="outlook-link"
                      @click="${this._openSchedules}"
                    >
                      ${ri("panels.zones.outlook.setup_schedule",e)}
                    </button>
                  `}
            </div>
            ${n?this._renderLastRunLine(n):""}
          </div>
        </ha-card>
      `}_renderRainDelay(){if(!this.hass||"none"===this.actionsMode)return W``;const e=this.hass.language,t=this._rainDelayUntil;return t?W`
        <ha-card class="rain-delay-card paused">
          <div class="rain-delay">
            <ha-icon icon="mdi:pause-circle"></ha-icon>
            <span class="rain-delay-msg">
              <strong
                >${ri("panels.zones.rain_delay.paused",e)}</strong
              >
              ${ri("panels.zones.rain_delay.until",e)}
              ${mi(t.toISOString())}
            </span>
            <button class="action-btn" @click="${()=>this._clearRainDelay()}">
              <ha-icon icon="mdi:play"></ha-icon>
              ${ri("panels.zones.rain_delay.resume",e)}
            </button>
          </div>
        </ha-card>
      `:W`
      <div class="rain-delay-row">
        <span class="rain-delay-label">
          <ha-icon icon="mdi:weather-rainy"></ha-icon>
          ${ri("panels.zones.rain_delay.title",e)}
        </span>
        <button class="action-btn" @click="${()=>this._setRainDelay(24)}">
          ${ri("panels.zones.rain_delay.delay_24h",e)}
        </button>
        <button class="action-btn" @click="${()=>this._setRainDelay(48)}">
          ${ri("panels.zones.rain_delay.delay_48h",e)}
        </button>
      </div>
    `}_renderLastRunLine(e){const t=this.hass.language,i=function(e,t){const i=pi(e).getTime()-Date.now(),n=new Intl.RelativeTimeFormat(t,{numeric:"auto"}),r=Math.round(i/1e3);if(Math.abs(r)<60)return n.format(r,"second");const a=Math.round(r/60);if(Math.abs(a)<60)return n.format(a,"minute");const o=Math.round(a/60);if(Math.abs(o)<24)return n.format(o,"hour");const s=Math.round(o/24);if(Math.abs(s)<30)return n.format(s,"day");const l=Math.round(s/30);return Math.abs(l)<12?n.format(l,"month"):n.format(Math.round(l/12),"year")}(e.timestamp,t),n=e.checks.filter(e=>e.enabled&&e.would_skip).map(e=>this._guardLabel(e).toLowerCase()).join(", "),r=e.would_skip?`${ri("panels.zones.outlook.last_run_skipped",t)}${n?` (${n})`:""}`:ri("panels.zones.outlook.last_run_ran",t);return W`
      <div class="outlook-line outlook-last">
        <span class="outlook-dim"
          >${ri("panels.zones.outlook.last_run",t)}:</span
        >
        <span>${r} · ${i}</span>
      </div>
    `}_renderZoneDecision(e){var t;if(!this.hass)return W``;const i=this.hass.language,n=null!==(t=e.duration)&&void 0!==t?t:0;let r,a,o;if(e.state===Se.Disabled)r=ri("panels.zones.status.decision_disabled",i),a="neutral",o="mdi:power-off";else if(e.last_calculated)if(this._zoneHasDeficit(e)){const t=function(e){const t=Math.round(e);if(t<60)return`${t} s`;const i=Math.floor(t/60),n=t%60;return n?`${i} min ${n} s`:`${i} min`}(n),s=this._triggeredGuards,l=this._nextIrrigateRunForZone(e);s.length>0?(r=ri("panels.zones.status.decision_water_skip",i,"{duration}",t,"{reason}",this._guardLabel(s[0]).toLowerCase()),a="skip",o="mdi:weather-rainy"):l&&l.next_run_utc?(r=ri("panels.zones.status.decision_water_at",i,"{duration}",t,"{time}",this._formatRunTime(l.next_run_utc)),a="water",o="mdi:water"):(r=ri("panels.zones.status.decision_water_no_schedule",i,"{duration}",t),a="water",o="mdi:water-alert")}else r=ri("panels.zones.status.decision_no_water",i),a="ok",o="mdi:check-circle-outline";else r=ri("panels.zones.status.decision_unknown",i),a="unknown",o="mdi:help-circle-outline";return W`
      <div class="zone-decision ${a}">
        <ha-icon icon="${o}"></ha-icon>
        <span>${r}</span>
      </div>
    `}_zoneEstimate(e){var t,i;if(void 0!==e.id)return null===(i=null===(t=this._outlook)||void 0===t?void 0:t.zone_estimates)||void 0===i?void 0:i[String(e.id)]}_zoneFault(e){var t,i;if(void 0!==e.id)return null===(i=null===(t=this._outlook)||void 0===t?void 0:t.zone_faults)||void 0===i?void 0:i[String(e.id)]}_renderZoneFault(e){if(!this.hass)return W``;const t=this._zoneFault(e);if(!t)return W``;const i=this.hass.language,n=ri(`panels.zones.fault.${t.reason}`,i)||ri("panels.zones.fault.generic",i),r=t.timestamp?mi(t.timestamp):"";return W`
      <div class="zone-fault" title="${r}">
        <ha-icon icon="mdi:alert-circle"></ha-icon>
        <span>
          <strong>${ri("panels.zones.fault.title",i)}</strong>
          — ${n}
        </span>
      </div>
    `}_renderZoneEstimate(e){if(!this.hass)return W``;const t=this._zoneEstimate(e);if(!t||!t.available||null==t.live_deficit)return W``;const i=this.hass.language,n=ai(this.config,ve),r=t.live_deficit<0?"var(--warning-color)":"var(--success-color)",a=ri(`panels.zones.status.estimate_method.${"proxy"===t.method?"proxy":"hourly"}`,i)+(t.as_of?` · ${gi(t.as_of)}`:"");return W`
      <span class="status-sep">·</span>
      <span class="zone-estimate" title="${a}">
        ${ri("panels.zones.status.estimate_now",i)}
        <strong style="color: ${r}"
          >≈ ${t.live_deficit.toFixed(2)} ${n}</strong
        >
        <span class="estimate-tag"
          >${ri("panels.zones.status.estimate_tag",i)}</span
        >
      </span>
    `}_renderZoneNextRun(e){if(!this.hass)return W``;const t=this._nextIrrigateRunForZone(e);if(!t||!t.next_run_utc)return W``;return e.state!==Se.Disabled&&e.last_calculated&&this._zoneHasDeficit(e)&&0===this._triggeredGuards.length?W``:W`
      <span class="status-sep">·</span>
      <span>
        ${ri("panels.zones.outlook.next_run",this.hass.language)}:
        <strong>${this._formatRunTime(t.next_run_utc)}</strong>
      </span>
    `}renderZone(e,t){var i,n;if(!this.hass)return W``;const r=Number(null!==(i=e.bucket)&&void 0!==i?i:0),a=r<0?"var(--warning-color)":"var(--success-color)",o=e.state===Se.Automatic?"state-automatic":e.state===Se.Manual?"state-manual":"state-disabled",s=e.last_calculated?mi(e.last_calculated):ri("panels.zones.status.never",this.hass.language);return W`
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          <span class="zone-state-badge ${o}">
            ${ri(`panels.zones.labels.states.${e.state}`,this.hass.language)}
          </span>
          ${this.hideSettingsLinks?"":W`
                <ha-icon-button
                  .path="${"M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"}"
                  title="${ri("panels.zones.actions.open_settings",this.hass.language)}"
                  @click="${()=>this._openZoneSettings(e)}"
                ></ha-icon-button>
              `}
        </div>

        <!-- RUN FAULT (e.g. valve didn't open) -->
        ${this._renderZoneFault(e)}

        <!-- AT-A-GLANCE DECISION -->
        ${this._renderZoneDecision(e)}

        <!-- COMPACT STATUS -->
        <div class="card-content">
          <div class="zone-status-line">
            <span
              title="${ri("panels.zones.help.bucket",this.hass.language)}"
            >
              ${ri("panels.zones.labels.bucket",this.hass.language)}:
              <strong style="color: ${a}"
                >${r.toFixed(2)}
                ${ai(this.config,ve)}</strong
              >
            </span>
            <span class="status-sep">·</span>
            <span>
              ${ri("panels.zones.status.last_checked",this.hass.language)}:
              <strong>${s}</strong>
            </span>
            ${this._renderZoneEstimate(e)} ${this._renderZoneNextRun(e)}
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div class="card-content zone-action-bar">
          ${"full"===this.actionsMode&&e.state===Se.Automatic?W`
                <button
                  class="action-btn"
                  title="${ri("panels.zones.help.update",this.hass.language)}"
                  @click="${()=>this.handleUpdateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${ri("panels.zones.actions.update",this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${ri("panels.zones.help.calculate",this.hass.language)}"
                  @click="${()=>this.handleCalculateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${ri("panels.zones.actions.calculate",this.hass.language)}
                </button>
              `:""}
          ${"none"!==this.actionsMode&&e.linked_entity&&(null!==(n=e.duration)&&void 0!==n?n:0)>0?W`
                <button
                  class="action-btn"
                  raised
                  @click="${()=>{void 0!==e.id&&(this._confirmIrrigate=e.id.toString())}}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${ri("panels.zones.labels.irrigate_now",this.hass.language)}
                </button>
              `:e.linked_entity?"":W`
                  <button
                    class="action-btn"
                    disabled
                    title="${ri("panels.zones.help.irrigate_link_entity",this.hass.language)}"
                  >
                    <ha-icon icon="mdi:water"></ha-icon>
                    ${ri("panels.zones.labels.irrigate_now",this.hass.language)}
                  </button>
                  <span class="zones-top-note">
                    ${ri("panels.zones.help.irrigate_link_entity",this.hass.language)}
                  </span>
                `}
          ${this._renderRunZoneControl(e)}
        </div>
      </ha-card>
    `}_renderRunZoneControl(e){if(!this.hass||"none"===this.actionsMode||!e.linked_entity||void 0===e.id)return W``;const t=this.hass.language,i=String(e.id);return W`
      <div
        class="run-zone-control"
        title="${ri("panels.zones.run_zone.help",t)}"
      >
        <input
          class="run-zone-input"
          type="number"
          min="1"
          max="600"
          .value="${String(this._zoneRunMinutes(e))}"
          @input="${e=>{const t=Number(e.target.value);this._runMinutes=Object.assign(Object.assign({},this._runMinutes),{[i]:t})}}"
        />
        <span class="run-zone-unit"
          >${ri("panels.zones.run_zone.minutes",t)}</span
        >
        <button
          class="action-btn"
          @click="${()=>this._runZoneFor(e)}"
          ?disabled="${this.isSaving}"
        >
          <ha-icon icon="mdi:timer-play-outline"></ha-icon>
          ${ri("panels.zones.run_zone.run",t)}
        </button>
      </div>
    `}render(){var e,t;if(!this.hass)return W``;if(this.isLoading)return W`
        <ha-card header="${ri("panels.zones.title",this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${ri("common.loading-messages.general",this.hass.language)}
            </div>
          </div>
        </ha-card>
      `;const i=this.zones.some(e=>{var t;return e.linked_entity&&(null!==(t=e.duration)&&void 0!==t?t:0)>0}),n=0===this.zones.length;return W`
      ${n?this.hideSettingsLinks?W`
              <ha-card>
                <div class="card-content description-text">
                  ${ri("panels.zones.no_items",this.hass.language)}
                </div>
              </ha-card>
            `:W`
              <ha-card class="setup-banner-card">
                <div class="setup-banner">
                  <div class="setup-banner-icon">🌱</div>
                  <div class="setup-banner-content">
                    <div class="setup-banner-title">
                      ${ri("wizard.title",this.hass.language)}
                    </div>
                    <div class="setup-banner-desc">
                      ${ri("wizard.setup_complete_banner",this.hass.language)}
                    </div>
                  </div>
                  <button
                    class="action-btn setup-banner-btn"
                    @click="${()=>{this.dispatchEvent(new CustomEvent("open-wizard",{bubbles:!0,composed:!0}))}}"
                  >
                    ${ri("wizard.open_wizard",this.hass.language)}
                  </button>
                </div>
              </ha-card>
            `:""}
      ${n?"":this._renderOutlookBanner()}
      ${n?"":this._renderRainDelay()}

      <!-- Zones header card: run-all operational actions -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${ri("panels.zones.title",this.hass.language)}
          </div>
        </div>
        <div class="card-content zones-top-actions">
          ${"full"===this.actionsMode?W`
                <button
                  class="action-btn"
                  title="${ri("panels.zones.help.update_all",this.hass.language)}"
                  @click="${this.handleUpdateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${ri("panels.zones.cards.zone-actions.actions.update-all",this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${ri("panels.zones.help.calculate_all",this.hass.language)}"
                  @click="${this.handleCalculateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${ri("panels.zones.cards.zone-actions.actions.calculate-all",this.hass.language)}
                </button>
              `:""}
          ${"none"!==this.actionsMode?W`
                <button
                  class="action-btn"
                  raised
                  title="${ri("panels.zones.help.irrigate_all",this.hass.language)}"
                  @click="${()=>{this._confirmIrrigate="all"}}"
                  ?disabled="${!i||this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${ri("panels.zones.actions.irrigate_all",this.hass.language)}
                </button>
              `:""}
          ${i?"":W`<span class="zones-top-note"
                >${ri("panels.info.cards.irrigate_now.no_linked_zones",this.hass.language)}</span
              >`}
        </div>
      </ha-card>

      <!-- Irrigate confirmation dialog -->
      ${null!==this._confirmIrrigate?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmIrrigate=null}}"
              heading="${ri("panels.zones.confirm_irrigate.title",this.hass.language)}"
            >
              <p>
                ${ri("panels.zones.confirm_irrigate.body",this.hass.language)}
              </p>
              <p>
                <strong>
                  ${"all"===this._confirmIrrigate?`${ri("panels.zones.confirm_irrigate.all_linked_zones",this.hass.language)} (${this._linkedZoneCount})`:null!==(t=null===(e=this.zones.find(e=>{var t;return(null===(t=e.id)||void 0===t?void 0:t.toString())===this._confirmIrrigate}))||void 0===e?void 0:e.name)&&void 0!==t?t:this._confirmIrrigate}
                </strong>
              </p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmIrrigate=null}}"
                >
                  ${ri("common.actions.cancel",this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._doIrrigate}"
                >
                  ${ri("panels.zones.labels.irrigate_now",this.hass.language)}
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
                  .path="${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}"
                  @click="${()=>{this._operationError=null}}"
                  aria-label="${ri("common.actions.cancel",this.hass.language)}"
                ></ha-icon-button>
              </div>
            </ha-card>
          `:""}

      <!-- Zone cards -->
      ${this.zones.map((e,t)=>this.renderZone(e,t))}
    `}static get styles(){return s`
      ${ui}

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

      /* Custom-duration run control (WS-5) */
      .run-zone-control {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-left: auto;
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
    `}}t([de()],bi.prototype,"config",void 0),t([de({type:Boolean})],bi.prototype,"hideSettingsLinks",void 0),t([de({attribute:!1})],bi.prototype,"actionsMode",void 0),t([de({type:Array})],bi.prototype,"zones",void 0),t([pe()],bi.prototype,"_outlook",void 0),t([de({type:Boolean})],bi.prototype,"isLoading",void 0),t([de({type:Boolean})],bi.prototype,"isSaving",void 0),t([pe()],bi.prototype,"_operationError",void 0),t([pe()],bi.prototype,"_confirmIrrigate",void 0),t([pe()],bi.prototype,"_skipDetailsOpen",void 0),t([pe()],bi.prototype,"_runMinutes",void 0),customElements.get("smart-irrigation-view-zones")||customElements.define("smart-irrigation-view-zones",bi);class _i extends le{setConfig(e){this._config=e}getCardSize(){return 6}render(){var e;if(!this.hass||!this._config)return W``;if(!ni(this.hass.language))return function(e){const t=ii(e);return ni(e)?Promise.resolve():(ti[t]||(ti[t]=fetch(`/smart_irrigation_static/languages/${t}.json`).then(e=>e.ok?e.json():Promise.reject(e.status)).then(e=>{ei[t]=e}).catch(()=>{ei[t]=ei.en})),ti[t])}(this.hass.language).then(()=>this.requestUpdate()),W``;const t=null!==(e=this._config.actions)&&void 0!==e?e:"irrigate";return W`
      <smart-irrigation-view-zones
        .hass=${this.hass}
        .hideSettingsLinks=${!0}
        .actionsMode=${t}
      ></smart-irrigation-view-zones>
    `}}t([de({attribute:!1})],_i.prototype,"hass",void 0),t([pe()],_i.prototype,"_config",void 0),customElements.get("smart-irrigation-zones-card-impl")||customElements.define("smart-irrigation-zones-card-impl",_i),e.SmartIrrigationZonesCardImpl=_i}({});
