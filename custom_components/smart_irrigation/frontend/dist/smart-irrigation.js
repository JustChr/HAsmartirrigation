!function(e){"use strict";function t(e,t,i,s){var a,n=arguments.length,o=n<3?t:null===s?s=Object.getOwnPropertyDescriptor(t,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)o=Reflect.decorate(e,t,i,s);else for(var r=e.length-1;r>=0;r--)(a=e[r])&&(o=(n<3?a(o):n>3?a(t,i,o):a(t,i))||o);return n>3&&o&&Object.defineProperty(t,i,o),o}"function"==typeof SuppressedError&&SuppressedError;
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const i=globalThis,s=i.ShadowRoot&&(void 0===i.ShadyCSS||i.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,a=Symbol(),n=new WeakMap;let o=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==a)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(s&&void 0===e){const i=void 0!==t&&1===t.length;i&&(e=n.get(t)),void 0===e&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&n.set(t,e))}return e}toString(){return this.cssText}};const r=(e,...t)=>{const i=1===e.length?e[0]:t.reduce((t,i,s)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+e[s+1],e[0]);return new o(i,e,a)},l=s?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const i of e.cssRules)t+=i.cssText;return(e=>new o("string"==typeof e?e:e+"",void 0,a))(t)})(e):e,{is:c,defineProperty:d,getOwnPropertyDescriptor:h,getOwnPropertyNames:u,getOwnPropertySymbols:p,getPrototypeOf:g}=Object,m=globalThis,v=m.trustedTypes,f=v?v.emptyScript:"",_=m.reactiveElementPolyfillSupport,b=(e,t)=>e,y={toAttribute(e,t){switch(t){case Boolean:e=e?f:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute(e,t){let i=e;switch(t){case Boolean:i=null!==e;break;case Number:i=null===e?null:Number(e);break;case Object:case Array:try{i=JSON.parse(e)}catch(e){i=null}}return i}},w=(e,t)=>!c(e,t),$={attribute:!0,type:String,converter:y,reflect:!1,useDefault:!1,hasChanged:w};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */Symbol.metadata??=Symbol("metadata"),m.litPropertyMetadata??=new WeakMap;let x=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=$){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(e,i,t);void 0!==s&&d(this.prototype,e,s)}}static getPropertyDescriptor(e,t,i){const{get:s,set:a}=h(this.prototype,e)??{get(){return this[t]},set(e){this[t]=e}};return{get:s,set(t){const n=s?.call(this);a?.call(this,t),this.requestUpdate(e,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??$}static _$Ei(){if(this.hasOwnProperty(b("elementProperties")))return;const e=g(this);e.finalize(),void 0!==e.l&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(b("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(b("properties"))){const e=this.properties,t=[...u(e),...p(e)];for(const i of t)this.createProperty(i,e[i])}const e=this[Symbol.metadata];if(null!==e){const t=litPropertyMetadata.get(e);if(void 0!==t)for(const[e,i]of t)this.elementProperties.set(e,i)}this._$Eh=new Map;for(const[e,t]of this.elementProperties){const i=this._$Eu(e,t);void 0!==i&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const i=new Set(e.flat(1/0).reverse());for(const e of i)t.unshift(l(e))}else void 0!==e&&t.push(l(e));return t}static _$Eu(e,t){const i=t.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof e?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),void 0!==this.renderRoot&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((e,t)=>{if(s)e.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(const s of t){const t=document.createElement("style"),a=i.litNonce;void 0!==a&&t.setAttribute("nonce",a),t.textContent=s.cssText,e.appendChild(t)}})(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){const i=this.constructor.elementProperties.get(e),s=this.constructor._$Eu(e,i);if(void 0!==s&&!0===i.reflect){const a=(void 0!==i.converter?.toAttribute?i.converter:y).toAttribute(t,i.type);this._$Em=e,null==a?this.removeAttribute(s):this.setAttribute(s,a),this._$Em=null}}_$AK(e,t){const i=this.constructor,s=i._$Eh.get(e);if(void 0!==s&&this._$Em!==s){const e=i.getPropertyOptions(s),a="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==e.converter?.fromAttribute?e.converter:y;this._$Em=s;const n=a.fromAttribute(t,e.type);this[s]=n??this._$Ej?.get(s)??n,this._$Em=null}}requestUpdate(e,t,i,s=!1,a){if(void 0!==e){const n=this.constructor;if(!1===s&&(a=this[e]),i??=n.getPropertyOptions(e),!((i.hasChanged??w)(a,t)||i.useDefault&&i.reflect&&a===this._$Ej?.get(e)&&!this.hasAttribute(n._$Eu(e,i))))return;this.C(e,t,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:s,wrapped:a},n){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,n??t??this[e]),!0!==a||void 0!==n)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),!0===s&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const e=this.scheduleUpdate();return null!=e&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[e,t]of this._$Ep)this[e]=t;this._$Ep=void 0}const e=this.constructor.elementProperties;if(e.size>0)for(const[t,i]of e){const{wrapped:e}=i,s=this[t];!0!==e||this._$AL.has(t)||void 0===s||this.C(t,void 0,i,s)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(e=>e.hostUpdate?.()),this.update(t)):this._$EM()}catch(t){throw e=!1,this._$EM(),t}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(e){}firstUpdated(e){}};x.elementStyles=[],x.shadowRootOptions={mode:"open"},x[b("elementProperties")]=new Map,x[b("finalized")]=new Map,_?.({ReactiveElement:x}),(m.reactiveElementVersions??=[]).push("2.1.2");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const k=globalThis,z=e=>e,S=k.trustedTypes,E=S?S.createPolicy("lit-html",{createHTML:e=>e}):void 0,A="$lit$",C=`lit$${Math.random().toFixed(9).slice(2)}$`,T="?"+C,O=`<${T}>`,H=document,M=()=>H.createComment(""),D=e=>null===e||"object"!=typeof e&&"function"!=typeof e,L=Array.isArray,N="[ \t\n\f\r]",I=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,P=/-->/g,B=/>/g,R=RegExp(`>|${N}(?:([^\\s"'>=/]+)(${N}*=${N}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),U=/'/g,j=/"/g,F=/^(?:script|style|textarea|title)$/i,Z=(e=>(t,...i)=>({_$litType$:e,strings:t,values:i}))(1),W=Symbol.for("lit-noChange"),q=Symbol.for("lit-nothing"),G=new WeakMap,K=H.createTreeWalker(H,129);function V(e,t){if(!L(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==E?E.createHTML(t):t}const Y=(e,t)=>{const i=e.length-1,s=[];let a,n=2===t?"<svg>":3===t?"<math>":"",o=I;for(let t=0;t<i;t++){const i=e[t];let r,l,c=-1,d=0;for(;d<i.length&&(o.lastIndex=d,l=o.exec(i),null!==l);)d=o.lastIndex,o===I?"!--"===l[1]?o=P:void 0!==l[1]?o=B:void 0!==l[2]?(F.test(l[2])&&(a=RegExp("</"+l[2],"g")),o=R):void 0!==l[3]&&(o=R):o===R?">"===l[0]?(o=a??I,c=-1):void 0===l[1]?c=-2:(c=o.lastIndex-l[2].length,r=l[1],o=void 0===l[3]?R:'"'===l[3]?j:U):o===j||o===U?o=R:o===P||o===B?o=I:(o=R,a=void 0);const h=o===R&&e[t+1].startsWith("/>")?" ":"";n+=o===I?i+O:c>=0?(s.push(r),i.slice(0,c)+A+i.slice(c)+C+h):i+C+(-2===c?t:h)}return[V(e,n+(e[i]||"<?>")+(2===t?"</svg>":3===t?"</math>":"")),s]};class X{constructor({strings:e,_$litType$:t},i){let s;this.parts=[];let a=0,n=0;const o=e.length-1,r=this.parts,[l,c]=Y(e,t);if(this.el=X.createElement(l,i),K.currentNode=this.el.content,2===t||3===t){const e=this.el.content.firstChild;e.replaceWith(...e.childNodes)}for(;null!==(s=K.nextNode())&&r.length<o;){if(1===s.nodeType){if(s.hasAttributes())for(const e of s.getAttributeNames())if(e.endsWith(A)){const t=c[n++],i=s.getAttribute(e).split(C),o=/([.?@])?(.*)/.exec(t);r.push({type:1,index:a,name:o[2],strings:i,ctor:"."===o[1]?ie:"?"===o[1]?se:"@"===o[1]?ae:te}),s.removeAttribute(e)}else e.startsWith(C)&&(r.push({type:6,index:a}),s.removeAttribute(e));if(F.test(s.tagName)){const e=s.textContent.split(C),t=e.length-1;if(t>0){s.textContent=S?S.emptyScript:"";for(let i=0;i<t;i++)s.append(e[i],M()),K.nextNode(),r.push({type:2,index:++a});s.append(e[t],M())}}}else if(8===s.nodeType)if(s.data===T)r.push({type:2,index:a});else{let e=-1;for(;-1!==(e=s.data.indexOf(C,e+1));)r.push({type:7,index:a}),e+=C.length-1}a++}}static createElement(e,t){const i=H.createElement("template");return i.innerHTML=e,i}}function J(e,t,i=e,s){if(t===W)return t;let a=void 0!==s?i._$Co?.[s]:i._$Cl;const n=D(t)?void 0:t._$litDirective$;return a?.constructor!==n&&(a?._$AO?.(!1),void 0===n?a=void 0:(a=new n(e),a._$AT(e,i,s)),void 0!==s?(i._$Co??=[])[s]=a:i._$Cl=a),void 0!==a&&(t=J(e,a._$AS(e,t.values),a,s)),t}class Q{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:i}=this._$AD,s=(e?.creationScope??H).importNode(t,!0);K.currentNode=s;let a=K.nextNode(),n=0,o=0,r=i[0];for(;void 0!==r;){if(n===r.index){let t;2===r.type?t=new ee(a,a.nextSibling,this,e):1===r.type?t=new r.ctor(a,r.name,r.strings,this,e):6===r.type&&(t=new ne(a,this,e)),this._$AV.push(t),r=i[++o]}n!==r?.index&&(a=K.nextNode(),n++)}return K.currentNode=H,s}p(e){let t=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}}class ee{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,s){this.type=2,this._$AH=q,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===e?.nodeType&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=J(this,e,t),D(e)?e===q||null==e||""===e?(this._$AH!==q&&this._$AR(),this._$AH=q):e!==this._$AH&&e!==W&&this._(e):void 0!==e._$litType$?this.$(e):void 0!==e.nodeType?this.T(e):(e=>L(e)||"function"==typeof e?.[Symbol.iterator])(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==q&&D(this._$AH)?this._$AA.nextSibling.data=e:this.T(H.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:i}=e,s="number"==typeof i?this._$AC(e):(void 0===i.el&&(i.el=X.createElement(V(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(t);else{const e=new Q(s,this),i=e.u(this.options);e.p(t),this.T(i),this._$AH=e}}_$AC(e){let t=G.get(e.strings);return void 0===t&&G.set(e.strings,t=new X(e)),t}k(e){L(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let i,s=0;for(const a of e)s===t.length?t.push(i=new ee(this.O(M()),this.O(M()),this,this.options)):i=t[s],i._$AI(a),s++;s<t.length&&(this._$AR(i&&i._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const t=z(e).nextSibling;z(e).remove(),e=t}}setConnected(e){void 0===this._$AM&&(this._$Cv=e,this._$AP?.(e))}}class te{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,s,a){this.type=1,this._$AH=q,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=a,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=q}_$AI(e,t=this,i,s){const a=this.strings;let n=!1;if(void 0===a)e=J(this,e,t,0),n=!D(e)||e!==this._$AH&&e!==W,n&&(this._$AH=e);else{const s=e;let o,r;for(e=a[0],o=0;o<a.length-1;o++)r=J(this,s[i+o],t,o),r===W&&(r=this._$AH[o]),n||=!D(r)||r!==this._$AH[o],r===q?e=q:e!==q&&(e+=(r??"")+a[o+1]),this._$AH[o]=r}n&&!s&&this.j(e)}j(e){e===q?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class ie extends te{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===q?void 0:e}}class se extends te{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==q)}}class ae extends te{constructor(e,t,i,s,a){super(e,t,i,s,a),this.type=5}_$AI(e,t=this){if((e=J(this,e,t,0)??q)===W)return;const i=this._$AH,s=e===q&&i!==q||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,a=e!==q&&(i===q||s);s&&this.element.removeEventListener(this.name,this,i),a&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class ne{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){J(this,e)}}const oe=k.litHtmlPolyfillSupport;oe?.(X,ee),(k.litHtmlVersions??=[]).push("3.3.3");const re=globalThis;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */let le=class extends x{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,i)=>{const s=i?.renderBefore??t;let a=s._$litPart$;if(void 0===a){const e=i?.renderBefore??null;s._$litPart$=a=new ee(t.insertBefore(M(),e),e,void 0,i??{})}return a._$AI(e),a})(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return W}};le._$litElement$=!0,le.finalized=!0,re.litElementHydrateSupport?.({LitElement:le});const ce=re.litElementPolyfillSupport;ce?.({LitElement:le}),(re.litElementVersions??=[]).push("4.2.2");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const de=e=>(t,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(e,t)}):customElements.define(e,t)},he={attribute:!0,type:String,converter:y,reflect:!1,hasChanged:w},ue=(e=he,t,i)=>{const{kind:s,metadata:a}=i;let n=globalThis.litPropertyMetadata.get(a);if(void 0===n&&globalThis.litPropertyMetadata.set(a,n=new Map),"setter"===s&&((e=Object.create(e)).wrapped=!0),n.set(i.name,e),"accessor"===s){const{name:s}=i;return{set(i){const a=t.get.call(this);t.set.call(this,i),this.requestUpdate(s,a,e,!0,i)},init(t){return void 0!==t&&this.C(s,void 0,e,t),t}}}if("setter"===s){const{name:s}=i;return function(i){const a=this[s];t.call(this,i),this.requestUpdate(s,a,e,!0,i)}}throw Error("Unsupported decorator location: "+s)};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function pe(e){return(t,i)=>"object"==typeof i?ue(e,t,i):((e,t,i)=>{const s=t.hasOwnProperty(i);return t.constructor.createProperty(i,e),s?Object.getOwnPropertyDescriptor(t,i):void 0})(e,t,i)}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function ge(e){return pe({...e,state:!0,attribute:!1})}
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
function me(e,t){return(t,i,s)=>((e,t,i)=>(i.configurable=!0,i.enumerable=!0,Reflect.decorate&&"object"!=typeof t&&Object.defineProperty(e,t,i),i))(t,i,{get(){return(t=>t.renderRoot?.querySelector(e)??null)(this)}})}let ve=!1,fe=null;const _e=async()=>{if(ve&&fe)return fe;if(customElements.get("ha-checkbox")&&customElements.get("ha-slider")&&customElements.get("ha-panel-config")&&customElements.get("ha-entity-picker"))return Promise.resolve();ve=!0,fe=async function(){try{await new Promise(e=>{"requestIdleCallback"in window?requestIdleCallback(()=>e()):setTimeout(()=>e(),0)}),await customElements.whenDefined("partial-panel-resolver");const e=document.createDocumentFragment(),t=document.createElement("partial-panel-resolver");e.appendChild(t),t.hass={panels:[{url_path:"tmp",component_name:"config"}]},await new Promise(e=>queueMicrotask(()=>e())),t._updateRoutes(),await t.routerOptions.routes.tmp.load(),await customElements.whenDefined("ha-panel-config"),await new Promise(e=>queueMicrotask(()=>e()));const i=document.createElement("ha-panel-config");e.appendChild(i),await i.routerOptions.routes.automation.load(),customElements.get("ha-entity-picker")||await Promise.race([customElements.whenDefined("ha-entity-picker"),new Promise(e=>setTimeout(e,3e3))]),e.textContent=""}catch(e){console.error("Failed to load HA form elements:",e)}}();try{await fe}finally{ve=!1,fe=null}};const be=`v${"2026.07.03"}`,ye="smart_irrigation",we=["de","en","es","fr","it","nl","no","sk"],$e="precipitation_threshold_mm",xe="Open Weather Map",ke="Pirate Weather",ze="Open-Meteo",Se="Met Office",Ee="minutes",Ae="hours",Ce="days",Te="imperial",Oe="metric",He="Dewpoint",Me="Evapotranspiration",De="Humidity",Le="Precipitation",Ne="Current Precipitation",Ie="Pressure",Pe="Solar Radiation",Be="Temperature",Re="Windspeed",Ue="weather_service",je="sensor",Fe="static",Ze="pressure_type",We="absolute",qe="relative",Ge="none",Ke="source",Ve="sensorentity",Ye="static_value",Xe="unit",Je="aggregate",Qe=["average","first","last","maximum","median","minimum","riemannsum","sum","delta"],et="sq ft",tt="l/minute",it="gal/minute",st="mm",at="in",nt="inch Hg",ot="mile/h",rt="meter/s",lt="mm/h",ct="in/h",dt="name",ht="size",ut="throughput",pt="state",gt="duration",mt="module",vt="bucket",ft="multiplier",_t="mapping",bt="lead_time",yt="maximum_duration",wt="maximum_bucket",$t="drainage_rate",xt="kc",kt="plant_type",zt="linked_entity",St="bucket_threshold",Et="flow_sensor",At="watering_mode",Ct="run_service",Tt="duration_field",Ot="duration_unit",Ht="stop_service",Mt="confirm_entity",Dt="soil_moisture_sensor",Lt="soil_moisture_threshold",Nt={lawn:.8,vegetables:1,flowers:.9,shrubs:.5,trees:.7,xeriscape:.3},It={sand:35,loam:20,silt:10,clay:5},Pt="zone_sequencing",Bt="sequential",Rt="parallel",Ut="rotating",jt="zone_sequencing_max_consecutive_duration",Ft="zone_sequencing_min_absorption_time",Zt="master_entity",Wt="master_settle_seconds",qt="master_kick_enabled",Gt="master_kick_pause_seconds",Kt="master_off_after",Vt=1,Yt=2,Xt=3,Jt=4,Qt=e=>(...t)=>({_$litDirective$:e,values:t});class ei{constructor(e){}get _$AU(){return this._$AM._$AU}_$AT(e,t,i){this._$Ct=e,this._$AM=t,this._$Ci=i}_$AS(e,t){return this.update(e,t)}update(e,t){return this.render(...t)}}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */class ti extends ei{constructor(e){if(super(e),this.it=q,e.type!==Yt)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(e){if(e===q||null==e)return this._t=void 0,this.it=e;if(e===W)return e;if("string"!=typeof e)throw Error(this.constructor.directiveName+"() called with a non-string value");if(e===this.it)return this._t;this.it=e;const t=[e];return t.raw=t,this._t={_$litType$:this.constructor.resultType,strings:t,values:[]}}}ti.directiveName="unsafeHTML",ti.resultType=1;const ii=Qt(ti);var si={loading:"Loading",saving:"Saving",actions:{delete:"Delete",edit:"Edit",save:"Save",cancel:"Cancel",confirm_delete:"Confirm Delete",confirm_delete_zone:"Are you sure you want to delete this zone?"},labels:{module:"Module",no:"No",select:"Select",yes:"Yes",enabled:"Enabled",disabled:"Disabled",before:"before",after:"after",settings:"Settings",bulk_actions:"Bulk Actions"},units:{seconds:"seconds"},attributes:{size:"size",throughput:"throughput",state:"state",bucket:"bucket",last_updated:"last updated",last_calculated:"last calculated",number_of_data_points:"number of data points"},"loading-messages":{configuration:"Loading configuration...",modules:"Loading modules...",general:"Loading..."},"saving-messages":{adding:"Adding...",saving:"Saving..."},errors:{load_failed:"Couldn't load data",save_failed:"Couldn't save changes",delete_failed:"Couldn't delete",action_failed:"Action failed"}},ai={"default-zone":"Default zone","default-mapping":"Default sensor group"},ni={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"Note: this explanation uses '.' as decimal separator, shows rounded and metric values. Module returned Evapotranspiration deficiency ( = et0 * hour_multiplier + precipitation) of","bucket-was":"Bucket was","new-bucket-values-is":"New bucket value is",bucket:"bucket","old-bucket-variable":"old_bucket","max-bucket-variable":"max_bucket",delta:"delta","bucket-less-than-zero-irrigation-necessary":"Since bucket < 0, irrigation is necessary","steps-taken-to-calculate-duration":"To calculate the exact duration, the following steps were taken","precipitation-rate-defined-as":"The precipitation rate is defined as","duration-is-calculated-as":"The duration is calculated as",drainage:"drainage","drainage-rate":"drainage_rate",hours:"hours","precipitation-rate-variable":"precipitation_rate","multiplier-is-applied":"Now, the multiplier is applied. The multiplier is","duration-after-multiplier-is":"hence the duration is","maximum-duration-is-applied":"Then, the maximum duration is applied. The maximum duration is","duration-after-maximum-duration-is":"hence the duration is","lead-time-is-applied":"Finally, the lead time is applied. The lead time is","duration-after-lead-time-is":"hence the final duration is","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Since bucket >= 0, no irrigation is necessary and duration is set to","maximum-bucket-is":"Maximum bucket size is","drainage-rate-is":"Drainage rate when saturated (bucket at max) is","current-drainage-is":"Current drainage is calculated as","drainage-integrated":"the surplus above field capacity drains continuously over the window (Brooks–Corey), so the rate falls as it drains","no-drainage":"Current drainage is 0 because","forecast-weighting-applied":"Forecast weighting reduced the deficit for the expected rain","crop-coefficient-applied":"Scaled by the crop coefficient"}}},oi={pyeto:{description:"Calculate duration based on the FAO56 calculation from the PyETO library"},static:{description:"'Dummy' module with a static configurable delta"},passthrough:{description:"Passthrough module that returns the value of an Evapotranspiration sensor as delta"}},ri={general:{cards:{"automatic-duration-calculation":{header:"Automatic duration calculation",description:"Calculation takes collected weather data up to that point and updates the bucket for each automatic zone. Then, the duration is adjusted based on the new bucket value and the collected weather data is removed.",labels:{"auto-calc-enabled":"Automatically calculate irrigation durations","calc-time":"Calculate at"}},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Warning: weather data update time on or after calculation time"},header:"Automatic weather data update",description:"Collect and store weather data automatically. Weather data is required to calculate zone buckets and durations.",labels:{"auto-update-enabled":"Automatically update weather data","auto-update-schedule":"Update schedule","auto-update-time":"Update at","auto-update-interval":"Update sensor data every","auto-update-delay":"Update delay"},options:{minutes:"minutes",hours:"hours",days:"days"}},"automatic-clear":{header:"Automatic weather data pruning",description:"Automatically remove collected weather data at a configured time. Use this to make sure that there is no left over weather data from previous days. Don't remove the weather data before you calculate and only use this option if you expect the automatic update to collect weather data after you calculated for the day. Ideally, you want to prune as late in the day as possible.",labels:{"automatic-clear-enabled":"Automatically clear collected weather data","automatic-clear-time":"Clear weather data at"}},continuousupdates:{header:"Continuous updates for sensors (experimental)",description:"This experimental feature will continuously update the sensor data. This is useful for sensor groups that use sources that provide continuous data, such as weather stations. This feature cannot be used for sensor groups that at least partly rely on weather services as continous polling of APIs will incur costs. Keep in mind that this is experimental and may not work as expected. Use at your own risk.",labels:{continuousupdates:"Enable continuous updates",sensor_debounce:"Sensor debounce"}}},description:"This page provides global settings.",title:"General",sections:{weather:"Weather",automation:"Automation",location:"Location",watering:"Watering behavior"}},schedules:{title:"Schedules",description:"Create recurring schedules to automatically irrigate your zones at specific times. No automations needed.",add:"Add Schedule",no_items:"No schedules configured yet. Click 'Add Schedule' to get started.",zones_all:"All zones",zones_specific:"Specific zones",hours:"hours",minutes:"min",types:{daily:"Daily",weekly:"Weekly",monthly:"Monthly",interval:"Every N hours",sunrise:"Sunrise",sunset:"Sunset",solar_azimuth:"Solar azimuth"},actions:{calculate:"Calculate (update irrigation duration)",update:"Update (collect weather data)",irrigate:"Irrigate (run valves directly)"},days:{monday:"Mon",tuesday:"Tue",wednesday:"Wed",thursday:"Thu",friday:"Fri",saturday:"Sat",sunday:"Sun"},fields:{name:"Name",type:"Schedule type",enabled:"Enabled",time:"Time (HH:MM)",days_of_week:"Days of week",day_of_month:"Day of month",interval_hours:"Interval",action:"Action",zones:"Zones",start_time:"Start time (optional)",start_date:"Start date (optional)",end_date:"End date (optional)",offset_minutes:"Offset from sunrise/sunset",account_for_duration:"Start early so irrigation finishes at trigger time",azimuth_angle:"Solar azimuth angle",time_anchor:"Time marks the"},dialog:{add_title:"Add Schedule",edit_title:"Edit Schedule"},time_anchor:{start:"Start of irrigation",finish:"End of irrigation"}},setup:{title:"Setup",tabs:{weather_location:"Weather & Location",my_zones:"My Zones",when_to_water:"When to Water",advanced:"Advanced",experimental:"Experimental"},weather_data:{forecast_title:"Forecast",forecast_none:"Forecast is available when a weather service is enabled.",seasonal_title:"Seasonal outlook"},advanced:{used_by_zones:"Used by {count, plural, one {# zone} other {# zones}}",not_used:"Not used"}},experimental:{title:"Experimental features",warning:"These features are opt-in and still being refined. They change how each zone's bucket is filled, so turn them on one at a time and keep an eye on your zones — you can switch them back off at any time.",forecast_weighting:{title:"Forecast-weighted durations",description:"Instead of skipping a whole run when rain is forecast, water less. The upcoming precipitation (over the look-ahead window set under When to Water) is subtracted from the deficit used to compute the run duration, while the true deficit stays in the bucket so the real rain fills the rest. If the forecast rain misses, the next run makes up the difference. Requires a weather service.",label:"Reduce durations when rain is forecast",note:"Uses the precipitation look-ahead from When to Water. Works alongside the rain-skip guard (a skip still wins over a reduced run)."},observed_watering:{title:"Credit bucket from observed watering",description:"When a zone's linked valve runs outside Smart Irrigation — a manual tap, an automation, your own schedule — its bucket is credited for the water applied, estimated from the run time and the zone's throughput. This keeps the soil-moisture model honest when you water by other means. Smart Irrigation's own runs are already accounted for and are never double-counted.",label:"Credit the bucket when a linked valve runs externally",note:"Requires a linked valve and a throughput on the zone. Volume is estimated (run time × throughput), not metered."},live_estimate:{title:"Live-estimate watering",description:"By default a zone waters once a day, from the deficit the daily calculation produced (for example at 23:00). With this on, each scheduled run instead decides — and sizes itself — from the live intra-day deficit (the drainage-aware ET and rainfall since the last calculation). This lets a zone water more than once a day on real intra-day demand (for example pots on an every-12-hours schedule that the once-daily bucket would otherwise leave dry), and it shrinks or cancels a run that intra-day rain has already covered. The daily ledger is unchanged: after the run the bucket is credited with the water actually delivered, so the next daily calculation never double-counts. Requires a weather service.",label:"Trigger and size each run from the live deficit",note:"Affects scheduled runs only, and can start a run the daily calculation didn't approve. For frequent watering keep a sensible minimum deficit and a maximum bucket of at least a day's ET."}},help:{title:"Help",cards:{"how-to-get-help":{title:"How to get help","first-read-the":"First, read the",wiki:"Documentation","if-you-still-need-help":"If you still need help reach out on the","community-forum":"Community forum","or-open-a":"or open a","github-issue":"Github Issue","english-only":"English only"}}},info:{title:"Info",description:"View information about next irrigation and system status.","configuration-not-available":"Configuration not available.",cards:{"zone-bucket-values":{title:"Zone Bucket Values & Duration",labels:{bucket:"Bucket",duration:"Duration"},"no-zones":"No zones configured"},"next-irrigation":{title:"Next Irrigation",labels:{"next-start":"Next start",duration:"Duration",zones:"Zones"},"no-data":"No data available"},"irrigation-reason":{title:"Irrigation Reason",labels:{reason:"Reason",sunrise:"Sunrise","total-duration":"Total duration",explanation:"Explanation"},"no-data":"No data available"},irrigate_now:{title:"Irrigate Now",description:"Immediately start irrigation for all zones that have a linked entity. Skip conditions are ignored.",button_all:"Run all zones now",no_linked_zones:"No zones have a linked switch/valve entity with a calculated duration."}}},mappings:{cards:{"add-mapping":{actions:{add:"Add sensor group"},header:"Add sensor groups"},mapping:{aggregates:{average:"Average",first:"First",last:"Last",maximum:"Maximum",median:"Median",minimum:"Minimum",riemannsum:"Riemann sum",sum:"Sum",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"You cannot delete this sensor group because there is at least one zone using it.",invalid_source:"Invalid source",source_does_not_exist:"Source does not exist. Please enter a valid source, such as 'sensor.mysensor'."},items:{dewpoint:"Dewpoint",evapotranspiration:"Evapotranspiration",humidity:"Humidity","maximum temperature":"Maximum temperature","minimum temperature":"Minimum temperature",precipitation:"Total precipitation","current precipitation":"Current precipitation",pressure:"Pressure","solar radiation":"Solar radiation",temperature:"Temperature",windspeed:"Wind speed"},pressure_types:{absolute:"absolute",relative:"relative"},"pressure-type":"Pressure is","sensor-aggregate-of-sensor-values-to-calculate":"of sensor values to calculate duration","sensor-aggregate-use-the":"Use the","sensor-entity":"Sensor entity",static_value:"Value","input-units":"Input provides values in",source:"Source",sources:{none:"None",weather_service:"Weather service",sensor:"Sensor",static:"Static value"}}},description:"Add one or more sensor groups that retrieve weather data from Weather service, from sensors or a combination of these. You can map each sensor group to one or more zones",labels:{"mapping-name":"Name"},no_items:"There are no sensor group defined yet.",title:"Sensor Groups","weather-records":{title:"Weather Records",timestamp:"Time",temperature:"Temp",humidity:"Hum",dewpoint:"Dew",wind:"Wind",pressure:"Press",precipitation:"Precip","retrieval-time":"Retrieved","no-data":"No weather data available for this sensor group"}},modules:{cards:{"add-module":{actions:{add:"Add module"},header:"Add module"},module:{errors:{"cannot-delete-module-because-zones-use-it":"You cannot delete this module because there is at least one zone using it."},labels:{configuration:"Configuration",required:"indicates a required field"},"translated-options":{DontEstimate:"Do not estimate",EstimateFromSunHours:"Estimate from sun hours",EstimateFromTemp:"Estimate from temperature",EstimateFromSunHoursAndTemperature:"Estimate from average of sun hours and temperature"},fields:{coastal:{name:"Coastal",description:"Enable if the weather station is located near a coast or large body of water. Affects how atmospheric humidity is estimated."},solrad_behavior:{name:"Solar radiation estimation",description:"How solar radiation is estimated when it is not directly measured by a sensor."},forecast_days:{name:"Forecast days",description:"Number of future days to include in the ET calculation. 0 = current weather only (recommended — no extra API calls). Values > 0 average today's ET with forecasted ET for upcoming days (up to 4 days via the OWM free tier)."},delta:{name:"Delta",description:"Static evapotranspiration delta (mm) used directly without any weather-based calculation."}}}},description:"Add one or more modules that calculate irrigation duration. Each module comes with its own configuration and can be used to calculate duration for one or more zones.",no_items:"There are no modules defined yet.",title:"Modules"},zones:{actions:{add:"Add",calculate:"Calculate",information:"Information",update:"Update","reset-bucket":"Reset bucket","view-weather-info":"View weather data","view-weather-info-message":"Weather data available for","view-watering-calendar":"View watering calendar",irrigate_all:"Water all zones now",open_settings:"Edit settings"},cards:{"add-zone":{actions:{add:"Add zone"},header:"Add zone"},"zone-actions":{actions:{"calculate-all":"Recalculate durations","update-all":"Refresh weather data","reset-all-buckets":"Reset all buckets","clear-all-weatherdata":"Clear all weather data"},header:"Actions on all zones"}},description:"Specify one or more irrigation zones here. The irrigation duration is calculated per zone, depending on size, throughput, state, module and sensor group.",labels:{bucket:"Bucket",duration:"Duration","lead-time":"Lead time",mapping:"Sensor Group","maximum-duration":"Maximum duration",multiplier:"Multiplier",name:"Name",size:"Size",state:"State",states:{automatic:"Automatic",disabled:"Disabled",manual:"Manual"},throughput:"Throughput","maximum-bucket":"Maximum bucket",last_calculated:"Last calculated","data-last-updated":"Data last updated","data-number-of-data-points":"Number of data points",drainage_rate:"Drainage rate",linked_entity:"Linked switch/valve/helper entity",linked_entity_placeholder:"e.g. switch.garden_valve",flow_sensor:"Flow meter sensor (optional)",flow_sensor_placeholder:"e.g. sensor.zone_flow_rate",watering_mode:"Watering mode",watering_mode_description:"How HASI actuates this zone. Classic: HASI opens the valve and closes it itself with a software timer. Self-closing service: HASI sends the run duration to a self-closing valve via a script (see the shipped valve blueprints) and lets the hardware close itself, so an HA restart mid-run cannot cause continuous irrigation.",watering_modes:{classic:"Classic (HASI opens & closes the valve)",service:"Self-closing service (valve closes itself)"},run_service:"Run service",run_service_help:"Service HASI calls to start the run (e.g. a script.* or a switch/valve service). It receives the duration field below plus zone_id and zone_name.",duration_field:"Duration field",duration_field_placeholder:"e.g. dauer",duration_field_help:"Name of the parameter that carries the run length in the call to your run service. The shipped valve blueprints use 'duration' (the default); a custom script may use another name (e.g. 'dauer').",duration_unit:"Duration unit",duration_units:{seconds:"Seconds",minutes:"Minutes"},duration_unit_help:"Unit your hardware expects for the run length. Check the device: many Zigbee/Tuya valves count in MINUTES. The wrong unit over- or under-waters by 60x. In Minutes mode HASI rounds up to whole minutes (minimum 1).",stop_service:"Stop service (optional)",stop_service_help:"Optional. Service HASI calls to close the valve when you stop the zone early, before its own timer expires. Leave empty if the valve cannot be stopped manually.",confirm_entity:"Confirm entity (optional)",confirm_entity_help:"Optional. The real valve/switch entity the run service drives (e.g. a valve or switch) — it holds a steady on-state while watering. If set, HASI verifies the open against it (poll only, it never re-actuates) and flags a problem plus skips the bucket credit if it never turns on. Leave empty to treat the run as write-only and credit optimistically (the hardware owns the close). When in doubt, leave it empty: it only helps with an entity that reports its on-state reliably — a valve that reports late (e.g. a sleepy Zigbee valve) could be read as 'off' and wrongly skip the credit, so the zone would water again next run. Do NOT point this at the run script itself — a fire-and-forget script is not a valid state signal.",soil_moisture_sensor:"Soil-moisture sensor (optional)",soil_moisture_sensor_help:"Optional. A sensor reporting this zone's soil moisture in percent (higher = wetter). With a skip threshold set below, an automatic run skips this zone whenever the reading is above the threshold and resets the zone's bucket. Leave empty to disable. An unavailable or non-numeric reading never blocks watering (fail-open).",soil_moisture_threshold:"Skip above soil moisture (%)",soil_moisture_threshold_help:"On an automatic run, skip this zone (and reset its bucket to 0) when the soil-moisture sensor reads strictly above this percentage. Needs a soil-moisture sensor set above. Only affects scheduled runs; manual runs always water.",irrigate_now:"Irrigate Now",bucket_threshold:"Minimum deficit to irrigate",plant_type:"Plant type",kc:"Crop coefficient (Kc)",plant_types:{custom:"Custom (set Kc manually)",lawn:"Lawn / turf",vegetables:"Vegetable garden",flowers:"Flower bed",shrubs:"Shrubs",trees:"Trees",xeriscape:"Xeriscape / drought-tolerant"},soil_type:"Soil type",soil_types:{custom:"Custom (set rate manually)",sand:"Sandy (fast draining)",loam:"Loam (balanced)",silt:"Silt (slow draining)",clay:"Clay (very slow draining)"}},no_items:"There are no zones defined yet.",title:"Zones",status:{decision_disabled:"Turned off — this zone won't be watered automatically.",decision_water:"Watering needed: about {duration} on the next scheduled run.",decision_water_at:"Will water about {duration} at {time}.",decision_water_skip:"Deficit ~{duration}, but the next run will likely be skipped ({reason}).",decision_water_no_schedule:"Deficit ~{duration} — no schedule waters this zone; trigger it manually.",decision_no_water:"No watering needed right now — the soil has enough moisture.",decision_unknown:"Not calculated yet — press Update, then Calculate to check.",last_checked:"Last checked",never:"never",saved:"Saved",estimate_now:"Now",estimate_tag:"est.",estimate_method:{hourly:"Live estimate from hourly weather since the last calculation",proxy:"Estimate distributed from today's forecast since the last calculation"}},fault:{title:"Last run failed",valve_no_response:"The valve didn't respond — no water was delivered, so the bucket was left unchanged.",flow_never_started:"No flow was detected — no water was delivered, so the bucket was left unchanged.",generic:"The last irrigation run failed."},skip:{title:"Skipped",soil_moisture:"Soil moisture {observed} % > {threshold} %"},help:{bucket:"Soil-moisture balance. A negative value means the soil is dry and the zone needs water.",calculate:"Works out how long to water from the latest data. Run this after Update.",update:"Fetches the latest weather/sensor data for this zone.",irrigate_link_entity:"Link a switch/valve in this zone's settings to enable manual watering.",irrigate_all:"Opens the linked valves now for every zone with a deficit. Skip conditions (rain, wind, temperature) are ignored.",update_all:"Collects the latest weather/sensor data for all zones. Does not change durations on its own.",calculate_all:"Recomputes each automatic zone's watering duration from the data collected so far."},outlook:{next_run:"Next run",no_schedule:"No automatic schedule — zones water only when you trigger them.",setup_schedule:"Set up a schedule",targets_all:"all zones",targets_zones:"{count} zones",will_skip:"Next run will likely be skipped",will_run:"Conditions look clear for the next run.",why_skipped:"Why?",provisional:"forecast — may change",active_guards:"Active guards",last_run:"Last run",last_run_skipped:"skipped",last_run_ran:"ran",today:"today",tomorrow:"tomorrow",actions:{irrigate:"Water",calculate:"Recalculate",update:"Refresh data"},checks:{precipitation:"Rain forecast",days_between:"Days between watering",temperature:"Low temperature",wind:"High wind",rain_sensor:"Rain sensor",freeze:"Frost",paused:"Paused (rain delay)",soil_moisture:"Soil moisture"},check_detail:{precipitation:"{observed} mm (≥ {threshold} mm)",days_between:"{observed}/{threshold} days",temperature:"{observed}° (below {threshold}°)",wind:"{observed} (above {threshold})",rain_sensor:"{observed}",freeze:"{observed}° (below {threshold}°)"}},calendar:{no_data:"No watering calendar data available for this zone.",error_prefix:"Error generating calendar:",month:"Month",et:"ET (mm)",precipitation:"Precipitation (mm)",watering:"Watering (L)",avg_temp:"Avg Temp (°C)",method_prefix:"Method:"},confirm_action:{reset_bucket_title:"Reset this zone's bucket?",reset_bucket_body:"This sets the bucket back to 0, discarding the accumulated moisture balance for this zone.",reset_all_buckets_title:"Reset all buckets?",reset_all_buckets_body:"This sets every zone's bucket back to 0, discarding the accumulated moisture balance. Watering calculations start fresh from the next update.",clear_weather_title:"Clear all weather data?",clear_weather_body:"This deletes all collected weather and sensor records for every zone. Zones will need fresh data before they can calculate again."},confirm_irrigate:{title:"Start irrigation?",body:"This opens the linked valve(s) now and bypasses all skip conditions (rain, temperature, minimum days between watering).",all_linked_zones:"All linked zones",toast_started:"Irrigation started",toast_failed:"Irrigation failed"},history:{title:"Run history",total_used:"Total water used",empty:"No runs recorded yet.",when:"When",result:"Result",volume:"Volume",detail:"Detail",results:{completed:"Completed",partial:"Partial",failed:"Failed",skipped:"Skipped"}},rain_delay:{title:"Pause watering",paused:"Paused",until:"until",delay_24h:"Delay 24 h",delay_48h:"Delay 48 h",resume:"Resume"},run_zone:{run:"Run",minutes:"min",help:"Water this zone for a custom time, ignoring the calculation",toast_started:"Started run"},stop_zone:{stop:"Stop",watering:"Watering…",toast_stopped:"Stopped run"}}},li="Smart Irrigation",ci={title:"Weather Service",description:"Configure which weather service to use for ET calculations and skip conditions.",enabled_label:"Enable weather service",service_label:"Weather service",api_key_label:"API key",api_key_placeholder:"Leave blank to keep existing key",api_key_configured:"API key is configured",api_key_not_configured:"No API key configured",api_key_help:"An API key from your chosen weather service provider. Open-Meteo does not require a key. OpenWeatherMap, Pirate Weather and the Met Office (Weather DataHub) all offer free tiers.",no_api_key_needed:"Open-Meteo is a free service and requires no API key.",save_button:"Save weather settings",saved:"Weather settings saved",owm:"OpenWeatherMap",pw:"Pirate Weather",openmeteo:"Open-Meteo (free, no key needed)",met:"Met Office (UK)",test_button:"Test Connection",test_button_testing:"Testing…",test_success:"✓ Connection successful",test_error_invalid_auth:"✗ Invalid API key — check that it is correct and active",test_error_cannot_connect:"✗ Cannot connect — check your internet connection",test_error_no_service:"✗ Select a weather service first",test_error_unknown:"✗ Test failed — unknown error"},di={title:"Irrigation Start Triggers",description:"Configure when irrigation should start based on solar events. You can add multiple triggers for different schedules. For sunrise triggers, leaving offset at 0 will automatically use the total duration of all enabled zones.",add_trigger:"Add Trigger",edit_trigger:"Edit Trigger",delete_trigger:"Delete Trigger",trigger_types:{sunrise:"Sunrise",sunset:"Sunset",solar_azimuth:"Solar Azimuth"},fields:{name:{name:"Trigger Name",description:"A descriptive name to identify this trigger"},type:{name:"Trigger Type",description:"The type of solar event to trigger on"},enabled:{name:"Enabled",description:"Whether this trigger is currently active"},offset_minutes:{name:"Offset (minutes)",description:"Minutes before (-) or after (+) the solar event. For sunrise triggers, use 0 for automatic timing based on total zone duration."},azimuth_angle:{name:"Azimuth Angle (degrees)",description:"Solar azimuth angle in degrees where 0=North, 90=East, 180=South, 270=West"},account_for_duration:{name:"Account for Duration",description:"When enabled, irrigation will start early enough to finish at the specified time. When disabled, irrigation will start exactly at the specified time."}},dialog:{add_title:"Add Irrigation Start Trigger",edit_title:"Edit Irrigation Start Trigger",cancel:"Cancel",save:"Save",delete:"Delete"},no_triggers:"No irrigation start triggers configured. The system will use the default behavior (sunrise with total zone duration). Add triggers to customize when irrigation starts.",offset_auto:"Auto (calculated from total zone duration)",confirm_delete:"Are you sure you want to delete the trigger '{name}'?",validation:{name_required:"Trigger name is required",azimuth_invalid:"Azimuth angle must be a valid number"},help:{sunrise_offset:"For sunrise triggers: Use negative values to start before sunrise, positive to start after. Set to 0 to automatically start early enough to complete all zones before sunrise.",sunset_offset:"For sunset triggers: Use negative values to start before sunset, positive to start after sunset.",azimuth_explanation:"Solar azimuth is the compass direction of the sun. 0°=North, 90°=East, 180°=South, 270°=West. You can enter any angle value (e.g., 450° = 90°, -30° = 330°). Use this to trigger irrigation when the sun reaches a specific position.",multiple_triggers:"You can configure multiple triggers. Each enabled trigger will independently schedule irrigation starts."}},hi={title:"Skip Conditions",description:"Automatically skip irrigation when conditions are unfavorable. Precipitation check requires a weather service. Temperature and wind checks also require a weather service.",threshold_label:"Precipitation Threshold",threshold_description:"Minimum total precipitation (in mm) forecast across the look-ahead window to skip irrigation.",lookahead_label:"Forecast look-ahead (days)",lookahead_help:"How many upcoming forecast days to add up when checking for rain. The forecast starts at tomorrow (today is excluded), so 1 = just the next day, 2 = the next two days, and so on.",temp_section_title:"Skip on low temperature",temp_threshold_label:"Skip if temperature is below",wind_section_title:"Skip on high wind speed",wind_threshold_label:"Skip if wind speed is above",rain_sensor_section_title:"Skip on rain sensor",rain_sensor_label:"Rain sensor entity (optional)",rain_sensor_placeholder:"e.g. binary_sensor.rain",freeze_section_title:"Skip on frost",freeze_threshold_label:"Skip if minimum temperature is below",freeze_help:"Compares the current temperature and the coming night's forecast low; skips watering when frost is expected, to protect pipes and plants.",forecast_rain_label:"When rain is forecast",forecast_rain_options:{ignore:"Ignore it",water_less:"Water less",skip:"Skip watering"},forecast_rain_help:{ignore:"Forecast rain is ignored; runs use the calculated duration.",water_less:"Upcoming forecast rain trims the run duration (the deficit stays in the bucket for the real rain to fill).",skip:"Skip the run entirely when enough rain is forecast within the look-ahead window."}},ui={title:"Location Coordinates",description:"Configure location coordinates for weather data retrieval. You can use manual coordinates different from your Home Assistant location if needed.",manual_enabled:"Use manual coordinates",use_ha_location:"Use Home Assistant location",latitude:"Latitude (decimal degrees)",longitude:"Longitude (decimal degrees)",elevation:"Elevation (meters above sea level)",current_ha_coords:"Current Home Assistant coordinates"},pi={title:"Days Between Irrigation",description:"Configure the minimum number of days that must pass between irrigation events. This helps control watering frequency for water conservation and plant health management.\n\nTypical real-world use cases:\n• Lawn care: 1-2 day intervals prevent overwatering\n• Drought restrictions: 6+ day intervals for weekly watering\n• Deep-rooted plants: 3-7 day intervals for less frequent watering\n• Water conservation: Customizable based on climate and soil conditions",label:"Minimum days between irrigation",help_text:"Set to 0 to disable this feature. Values from 1-365 days are supported. This setting works alongside existing precipitation forecasting logic."},gi={title:"Zone Sequencing",description:"When multiple zones need irrigation, choose whether they run at the same time or one after another. Sequential mode waits for each zone to finish before starting the next. Rotating mode cycles through zones, giving each one a limited consecutive run before moving to the next.",parallel:"Parallel (all zones at once)",sequential:"Sequential (one zone at a time)",rotating:"Rotating (zones take turns)",max_consecutive_duration_label:"Max consecutive run time per zone",max_consecutive_duration_unit:"minutes",min_absorption_time_label:"Min. absorption time between slots",min_absorption_time_unit:"minutes (0 = disabled)"},mi={title:"Pump / master switch",description:"Optional. Powers a shared master — a pump or main valve — on before the first zone of a watering cycle, then optionally off after the last zone. Leave the entity empty to never touch a master (e.g. a pressure-controlled waterworks that starts on its own).",entity:"Master entity (switch/valve)",kick_enabled:"Kicker: pulse off then on to force a pump start",kick_pause:"Kick pause (off before on)",settle:"Settle delay before the first zone",off_after:"Turn the master off after irrigation",seconds_unit:"seconds"},vi={zone_size:"The total irrigated area of this zone. Used with throughput to calculate how much water is applied per run.",zone_throughput:"Total water flow of your irrigation system for this zone (litres/min in metric, gal/min in imperial). Check your sprinkler datasheet or measure by timing how long it takes to fill a known container.",zone_drainage_rate:"How fast saturated soil drains excess water. ~20 mm/h suits medium/loam soil; lower (2–10) for heavy clay, higher for sandy soil.",zone_bucket:"Current water deficit (negative) or surplus (positive) for this zone. Irrigation triggers when bucket drops below the threshold.",zone_maximum_bucket:"Maximum moisture surplus the zone can hold. Water above this level is treated as runoff. Typical value: 50 mm.",zone_bucket_threshold:"Irrigation triggers when the bucket drops below this value. Must be 0 or negative. 0 means irrigate whenever there is any deficit.",zone_multiplier:"Scale factor applied to the calculated duration. Use above 1.0 to increase, below 1.0 to decrease. Useful for fine-tuning without changing physical measurements.",zone_lead_time:"Extra seconds added before irrigation starts. Use for pump warm-up or system pressurisation.",zone_maximum_duration:"Hard cap on any single irrigation run in seconds. Prevents runaway watering. Default: 3600 s (1 hour).",zone_linked_entity:"The HA switch, valve or input_boolean (helper) entity controlling water flow for this zone. This entity is turned on when irrigation runs.",zone_flow_sensor:"Optional sensor measuring actual water flow rate. Used for reporting only — does not affect duration calculations.",general_autoupdatedelay:"Seconds to wait after HA starts before the first weather data fetch. Allows other integrations to initialise first.",general_sensor_debounce:"Minimum gap in milliseconds between sensor readings to filter noise from rapidly changing sensors.",general_calctime:"Time of day when irrigation durations are recalculated from collected weather data. Format: HH:MM (24-hour).",general_cleardatatime:"Time of day when old weather data is purged. Must be set later than the calculation time.",general_days_between:"Minimum days between irrigation events for the same zone. Set to 0 to disable (irrigate whenever deficit exists).",general_autoupdateinterval:"How often weather data is collected. Choose a value that balances fresh data against API rate limits.",general_precipitation_threshold:"Irrigation is skipped if total forecast precipitation across the look-ahead window exceeds this amount.",general_temp_threshold:"Irrigation is skipped if the current temperature is below this value (e.g. to prevent frost damage).",general_wind_threshold:"Irrigation is skipped if wind speed exceeds this value (high winds reduce efficiency and cause drift).",zone_plant_type:"Pick a plant type to set a typical crop coefficient, or choose Custom to enter Kc yourself.",zone_kc:"Scales reference (grass) ET to this zone's plants. 1.0 = reference grass; lower for drought-tolerant planting, higher for thirsty crops. Only the ET term is scaled — rain is not.",zone_soil_type:"Pick a soil type to set a typical drainage rate, or leave Custom to enter it by hand below."},fi={title:"Setup Wizard",open_button:"Setup Wizard",close:"Close",next:"Next",back:"Back",finish:"Finish",skip_step:"Skip this step",step_indicator:"Step {current} of {total}",stepper:{weather:"Weather",module:"Module",mapping:"Sensor Group",zone:"Zone"},setup_complete_banner:"Setup not complete. Run the wizard to get started.",open_wizard:"Open Wizard",steps:{welcome:{title:"Welcome to Smart Irrigation",intro:"This wizard guides you through the four steps needed to get your first zone irrigating automatically.",step1_label:"Weather Service — where to get weather data",step2_label:"Calculation Module — how irrigation duration is computed",step3_label:"Sensor Group — which data sources to use",step4_label:"Zone — your first irrigation zone",tip:"You can skip any step and configure it later from the Setup tab."},weather:{title:"Weather Service",description:"Choose how to get weather data. Open-Meteo is free and requires no API key — it is the easiest choice for most users."},module:{title:"Calculation Module",description:"A module calculates how long to irrigate based on evapotranspiration (ET). The PyETO module (FAO-56 method) is recommended for most users.",pick_label:"Select module type",no_modules:"No module types available."},mapping:{title:"Sensor Group",description:"A sensor group links each weather variable to a data source. Set the key variables below — you can refine individual sensor mappings later from the Setup → Sensor Groups tab.",name_label:"Sensor group name",source_label:"Data source for",use_weather_service:"Weather service",use_sensor:"Sensor",use_static:"Static value",use_none:"None / not used"},zone:{title:"First Zone",description:"A zone is one irrigation area (e.g. lawn, garden bed). Set the physical properties so the system can calculate the correct irrigation duration.",name_label:"Zone name",size_label:"Area",throughput_label:"Sprinkler throughput",entity_label:"Linked switch, valve or helper",entity_placeholder:"e.g. switch.garden_valve",module_label:"Calculation module",mapping_label:"Sensor group"},done:{title:"Setup Complete!",description:"Your first zone is ready. Smart Irrigation will now calculate irrigation durations automatically based on weather data.",next_steps:"What you can do next:",tip1:"Go to Zones to view calculated durations and bucket values.",tip2:"Add more zones from the Zones tab.",tip3:"Refine all settings from the Setup tab.",go_zones:"Go to Zones",go_setup:"Go to Setup",schedule_name:"Daily",schedule_title:"Create a watering schedule",schedule_desc:"Your system is configured, but it won't water until a schedule exists. Create a daily schedule for all zones now (you can change or remove it later under Setup → When to Water).",schedule_create:"Create daily schedule",schedule_created:"Daily schedule created."}},confirm_close:{body:"Close the setup wizard? Your progress so far is saved.",keep:"Keep editing",close:"Close"}},_i={common:si,defaults:ai,module:ni,calcmodules:oi,panels:ri,title:li,weather_service_config:ci,irrigation_start_triggers:di,weather_skip:hi,coordinate_config:ui,days_between_irrigation:pi,zone_sequencing:gi,master:mi,field_help:vi,wizard:fi},bi=Object.freeze({__proto__:null,calcmodules:oi,common:si,coordinate_config:ui,days_between_irrigation:pi,default:_i,defaults:ai,field_help:vi,irrigation_start_triggers:di,master:mi,module:ni,panels:ri,title:li,weather_service_config:ci,weather_skip:hi,wizard:fi,zone_sequencing:gi});function yi(e,t){const i=t&&t.cache?t.cache:Ei,s=t&&t.serializer?t.serializer:zi;return(t&&t.strategy?t.strategy:ki)(e,{cache:i,serializer:s})}function wi(e,t,i,s){const a=null==(n=s)||"number"==typeof n||"boolean"==typeof n?s:i(s);var n;let o=t.get(a);return void 0===o&&(o=e.call(this,s),t.set(a,o)),o}function $i(e,t,i){const s=Array.prototype.slice.call(arguments,3),a=i(s);let n=t.get(a);return void 0===n&&(n=e.apply(this,s),t.set(a,n)),n}function xi(e,t,i,s,a){return i.bind(t,e,s,a)}function ki(e,t){return xi(e,this,1===e.length?wi:$i,t.cache.create(),t.serializer)}const zi=function(){return JSON.stringify(arguments)};var Si=class{constructor(){this.cache=Object.create(null)}get(e){return this.cache[e]}set(e,t){this.cache[e]=t}};const Ei={create:function(){return new Si}},Ai={variadic:function(e,t){return xi(e,this,$i,t.cache.create(),t.serializer)}},Ci=/(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;function Ti(e){const t={};return e.replace(Ci,e=>{const i=e.length;switch(e[0]){case"G":t.era=4===i?"long":5===i?"narrow":"short";break;case"y":t.year=2===i?"2-digit":"numeric";break;case"Y":case"u":case"U":case"r":throw new RangeError("`Y/u/U/r` (year) patterns are not supported, use `y` instead");case"q":case"Q":throw new RangeError("`q/Q` (quarter) patterns are not supported");case"M":case"L":t.month=["numeric","2-digit","short","long","narrow"][i-1];break;case"w":case"W":throw new RangeError("`w/W` (week) patterns are not supported");case"d":t.day=["numeric","2-digit"][i-1];break;case"D":case"F":case"g":throw new RangeError("`D/F/g` (day) patterns are not supported, use `d` instead");case"E":t.weekday=4===i?"long":5===i?"narrow":"short";break;case"e":if(i<4)throw new RangeError("`e..eee` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][i-4];break;case"c":if(i<4)throw new RangeError("`c..ccc` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][i-4];break;case"a":t.hour12=!0;break;case"b":case"B":throw new RangeError("`b/B` (period) patterns are not supported, use `a` instead");case"h":t.hourCycle="h12",t.hour=["numeric","2-digit"][i-1];break;case"H":t.hourCycle="h23",t.hour=["numeric","2-digit"][i-1];break;case"K":t.hourCycle="h11",t.hour=["numeric","2-digit"][i-1];break;case"k":t.hourCycle="h24",t.hour=["numeric","2-digit"][i-1];break;case"j":case"J":case"C":throw new RangeError("`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead");case"m":t.minute=["numeric","2-digit"][i-1];break;case"s":t.second=["numeric","2-digit"][i-1];break;case"S":case"A":throw new RangeError("`S/A` (second) patterns are not supported, use `s` instead");case"z":t.timeZoneName=i<4?"short":"long";break;case"Z":case"O":case"v":case"V":case"X":case"x":throw new RangeError("`Z/O/v/V/X/x` (timeZone) patterns are not supported, use `z` instead")}return""}),t}const Oi=/[\t-\r \x85\u200E\u200F\u2028\u2029]/i;function Hi(e){return e.replace(/^(.*?)-/,"")}const Mi=/^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g,Di=/^(@+)?(\+|#+)?[rs]?$/g,Li=/(\*)(0+)|(#+)(0+)|(0+)/g,Ni=/^(0+)$/;function Ii(e){const t={};return"r"===e[e.length-1]?t.roundingPriority="morePrecision":"s"===e[e.length-1]&&(t.roundingPriority="lessPrecision"),e.replace(Di,function(e,i,s){return"string"!=typeof s?(t.minimumSignificantDigits=i.length,t.maximumSignificantDigits=i.length):"+"===s?t.minimumSignificantDigits=i.length:"#"===i[0]?t.maximumSignificantDigits=i.length:(t.minimumSignificantDigits=i.length,t.maximumSignificantDigits=i.length+("string"==typeof s?s.length:0)),""}),t}function Pi(e){switch(e){case"sign-auto":return{signDisplay:"auto"};case"sign-accounting":case"()":return{currencySign:"accounting"};case"sign-always":case"+!":return{signDisplay:"always"};case"sign-accounting-always":case"()!":return{signDisplay:"always",currencySign:"accounting"};case"sign-except-zero":case"+?":return{signDisplay:"exceptZero"};case"sign-accounting-except-zero":case"()?":return{signDisplay:"exceptZero",currencySign:"accounting"};case"sign-never":case"+_":return{signDisplay:"never"}}}function Bi(e){let t;if("E"===e[0]&&"E"===e[1]?(t={notation:"engineering"},e=e.slice(2)):"E"===e[0]&&(t={notation:"scientific"},e=e.slice(1)),t){const i=e.slice(0,2);if("+!"===i?(t.signDisplay="always",e=e.slice(2)):"+?"===i&&(t.signDisplay="exceptZero",e=e.slice(2)),!Ni.test(e))throw new Error("Malformed concise eng/scientific notation");t.minimumIntegerDigits=e.length}return t}function Ri(e){const t=Pi(e);return t||{}}function Ui(e){let t={};for(const i of e){switch(i.stem){case"percent":case"%":t.style="percent";continue;case"%x100":t.style="percent",t.scale=100;continue;case"currency":t.style="currency",t.currency=i.options[0];continue;case"group-off":case",_":t.useGrouping=!1;continue;case"precision-integer":case".":t.maximumFractionDigits=0;continue;case"measure-unit":case"unit":t.style="unit",t.unit=Hi(i.options[0]);continue;case"compact-short":case"K":t.notation="compact",t.compactDisplay="short";continue;case"compact-long":case"KK":t.notation="compact",t.compactDisplay="long";continue;case"scientific":t={...t,notation:"scientific",...i.options.reduce((e,t)=>({...e,...Ri(t)}),{})};continue;case"engineering":t={...t,notation:"engineering",...i.options.reduce((e,t)=>({...e,...Ri(t)}),{})};continue;case"notation-simple":t.notation="standard";continue;case"unit-width-narrow":t.currencyDisplay="narrowSymbol",t.unitDisplay="narrow";continue;case"unit-width-short":t.currencyDisplay="code",t.unitDisplay="short";continue;case"unit-width-full-name":t.currencyDisplay="name",t.unitDisplay="long";continue;case"unit-width-iso-code":t.currencyDisplay="symbol";continue;case"scale":t.scale=parseFloat(i.options[0]);continue;case"rounding-mode-floor":t.roundingMode="floor";continue;case"rounding-mode-ceiling":t.roundingMode="ceil";continue;case"rounding-mode-down":t.roundingMode="trunc";continue;case"rounding-mode-up":t.roundingMode="expand";continue;case"rounding-mode-half-even":t.roundingMode="halfEven";continue;case"rounding-mode-half-down":t.roundingMode="halfTrunc";continue;case"rounding-mode-half-up":t.roundingMode="halfExpand";continue;case"integer-width":if(i.options.length>1)throw new RangeError("integer-width stems only accept a single optional option");i.options[0].replace(Li,function(e,i,s,a,n,o){if(i)t.minimumIntegerDigits=s.length;else{if(a&&n)throw new Error("We currently do not support maximum integer digits");if(o)throw new Error("We currently do not support exact integer digits")}return""});continue}if(Ni.test(i.stem)){t.minimumIntegerDigits=i.stem.length;continue}if(Mi.test(i.stem)){if(i.options.length>1)throw new RangeError("Fraction-precision stems only accept a single optional option");i.stem.replace(Mi,function(e,i,s,a,n,o){return"*"===s?t.minimumFractionDigits=i.length:a&&"#"===a[0]?t.maximumFractionDigits=a.length:n&&o?(t.minimumFractionDigits=n.length,t.maximumFractionDigits=n.length+o.length):(t.minimumFractionDigits=i.length,t.maximumFractionDigits=i.length),""});const e=i.options[0];"w"===e?t={...t,trailingZeroDisplay:"stripIfInteger"}:e&&(t={...t,...Ii(e)});continue}if(Di.test(i.stem)){t={...t,...Ii(i.stem)};continue}const e=Pi(i.stem);e&&(t={...t,...e});const s=Bi(i.stem);s&&(t={...t,...s})}return t}let ji=function(e){return e[e.EXPECT_ARGUMENT_CLOSING_BRACE=1]="EXPECT_ARGUMENT_CLOSING_BRACE",e[e.EMPTY_ARGUMENT=2]="EMPTY_ARGUMENT",e[e.MALFORMED_ARGUMENT=3]="MALFORMED_ARGUMENT",e[e.EXPECT_ARGUMENT_TYPE=4]="EXPECT_ARGUMENT_TYPE",e[e.INVALID_ARGUMENT_TYPE=5]="INVALID_ARGUMENT_TYPE",e[e.EXPECT_ARGUMENT_STYLE=6]="EXPECT_ARGUMENT_STYLE",e[e.INVALID_NUMBER_SKELETON=7]="INVALID_NUMBER_SKELETON",e[e.INVALID_DATE_TIME_SKELETON=8]="INVALID_DATE_TIME_SKELETON",e[e.EXPECT_NUMBER_SKELETON=9]="EXPECT_NUMBER_SKELETON",e[e.EXPECT_DATE_TIME_SKELETON=10]="EXPECT_DATE_TIME_SKELETON",e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE=11]="UNCLOSED_QUOTE_IN_ARGUMENT_STYLE",e[e.EXPECT_SELECT_ARGUMENT_OPTIONS=12]="EXPECT_SELECT_ARGUMENT_OPTIONS",e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE=13]="EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE=14]="INVALID_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR=15]="EXPECT_SELECT_ARGUMENT_SELECTOR",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR=16]="EXPECT_PLURAL_ARGUMENT_SELECTOR",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT=17]="EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT=18]="EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT",e[e.INVALID_PLURAL_ARGUMENT_SELECTOR=19]="INVALID_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR=20]="DUPLICATE_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR=21]="DUPLICATE_SELECT_ARGUMENT_SELECTOR",e[e.MISSING_OTHER_CLAUSE=22]="MISSING_OTHER_CLAUSE",e[e.INVALID_TAG=23]="INVALID_TAG",e[e.INVALID_TAG_NAME=25]="INVALID_TAG_NAME",e[e.UNMATCHED_CLOSING_TAG=26]="UNMATCHED_CLOSING_TAG",e[e.UNCLOSED_TAG=27]="UNCLOSED_TAG",e}({});function Fi(e){return 0===e.type}function Zi(e){return 1===e.type}function Wi(e){return 2===e.type}function qi(e){return 3===e.type}function Gi(e){return 4===e.type}function Ki(e){return 5===e.type}function Vi(e){return 6===e.type}function Yi(e){return 7===e.type}function Xi(e){return 8===e.type}function Ji(e){return!(!e||"object"!=typeof e||0!==e.type)}function Qi(e){return!(!e||"object"!=typeof e||1!==e.type)}const es=/[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/,ts={"001":["H","h"],419:["h","H","hB","hb"],AC:["H","h","hb","hB"],AD:["H","hB"],AE:["h","hB","hb","H"],AF:["H","hb","hB","h"],AG:["h","hb","H","hB"],AI:["H","h","hb","hB"],AL:["h","H","hB"],AM:["H","hB"],AO:["H","hB"],AR:["h","H","hB","hb"],AS:["h","H"],AT:["H","hB"],AU:["h","hb","H","hB"],AW:["H","hB"],AX:["H"],AZ:["H","hB","h"],BA:["H","hB","h"],BB:["h","hb","H","hB"],BD:["h","hB","H"],BE:["H","hB"],BF:["H","hB"],BG:["H","hB","h"],BH:["h","hB","hb","H"],BI:["H","h"],BJ:["H","hB"],BL:["H","hB"],BM:["h","hb","H","hB"],BN:["hb","hB","h","H"],BO:["h","H","hB","hb"],BQ:["H"],BR:["H","hB"],BS:["h","hb","H","hB"],BT:["h","H"],BW:["H","h","hb","hB"],BY:["H","h"],BZ:["H","h","hb","hB"],CA:["h","hb","H","hB"],CC:["H","h","hb","hB"],CD:["hB","H"],CF:["H","h","hB"],CG:["H","hB"],CH:["H","hB","h"],CI:["H","hB"],CK:["H","h","hb","hB"],CL:["h","H","hB","hb"],CM:["H","h","hB"],CN:["H","hB","hb","h"],CO:["h","H","hB","hb"],CP:["H"],CR:["h","H","hB","hb"],CU:["h","H","hB","hb"],CV:["H","hB"],CW:["H","hB"],CX:["H","h","hb","hB"],CY:["h","H","hb","hB"],CZ:["H"],DE:["H","hB"],DG:["H","h","hb","hB"],DJ:["h","H"],DK:["H"],DM:["h","hb","H","hB"],DO:["h","H","hB","hb"],DZ:["h","hB","hb","H"],EA:["H","h","hB","hb"],EC:["h","H","hB","hb"],EE:["H","hB"],EG:["h","hB","hb","H"],EH:["h","hB","hb","H"],ER:["h","H"],ES:["H","hB","h","hb"],ET:["hB","hb","h","H"],FI:["H"],FJ:["h","hb","H","hB"],FK:["H","h","hb","hB"],FM:["h","hb","H","hB"],FO:["H","h"],FR:["H","hB"],GA:["H","hB"],GB:["H","h","hb","hB"],GD:["h","hb","H","hB"],GE:["H","hB","h"],GF:["H","hB"],GG:["H","h","hb","hB"],GH:["h","H"],GI:["H","h","hb","hB"],GL:["H","h"],GM:["h","hb","H","hB"],GN:["H","hB"],GP:["H","hB"],GQ:["H","hB","h","hb"],GR:["h","H","hb","hB"],GS:["H","h","hb","hB"],GT:["h","H","hB","hb"],GU:["h","hb","H","hB"],GW:["H","hB"],GY:["h","hb","H","hB"],HK:["h","hB","hb","H"],HN:["h","H","hB","hb"],HR:["H","hB"],HU:["H","h"],IC:["H","h","hB","hb"],ID:["H"],IE:["H","h","hb","hB"],IL:["H","hB"],IM:["H","h","hb","hB"],IN:["h","H"],IO:["H","h","hb","hB"],IQ:["h","hB","hb","H"],IR:["hB","H"],IS:["H"],IT:["H","hB"],JE:["H","h","hb","hB"],JM:["h","hb","H","hB"],JO:["h","hB","hb","H"],JP:["H","K","h"],KE:["hB","hb","H","h"],KG:["H","h","hB","hb"],KH:["hB","h","H","hb"],KI:["h","hb","H","hB"],KM:["H","h","hB","hb"],KN:["h","hb","H","hB"],KP:["h","H","hB","hb"],KR:["h","H","hB","hb"],KW:["h","hB","hb","H"],KY:["h","hb","H","hB"],KZ:["H","hB"],LA:["H","hb","hB","h"],LB:["h","hB","hb","H"],LC:["h","hb","H","hB"],LI:["H","hB","h"],LK:["H","h","hB","hb"],LR:["h","hb","H","hB"],LS:["h","H"],LT:["H","h","hb","hB"],LU:["H","h","hB"],LV:["H","hB","hb","h"],LY:["h","hB","hb","H"],MA:["H","h","hB","hb"],MC:["H","hB"],MD:["H","hB"],ME:["H","hB","h"],MF:["H","hB"],MG:["H","h"],MH:["h","hb","H","hB"],MK:["H","h","hb","hB"],ML:["H"],MM:["hB","hb","H","h"],MN:["H","h","hb","hB"],MO:["h","hB","hb","H"],MP:["h","hb","H","hB"],MQ:["H","hB"],MR:["h","hB","hb","H"],MS:["H","h","hb","hB"],MT:["H","h"],MU:["H","h"],MV:["H","h"],MW:["h","hb","H","hB"],MX:["h","H","hB","hb"],MY:["hb","hB","h","H"],MZ:["H","hB"],NA:["h","H","hB","hb"],NC:["H","hB"],NE:["H"],NF:["H","h","hb","hB"],NG:["H","h","hb","hB"],NI:["h","H","hB","hb"],NL:["H","hB"],NO:["H","h"],NP:["H","h","hB"],NR:["H","h","hb","hB"],NU:["H","h","hb","hB"],NZ:["h","hb","H","hB"],OM:["h","hB","hb","H"],PA:["h","H","hB","hb"],PE:["h","H","hB","hb"],PF:["H","h","hB"],PG:["h","H"],PH:["h","hB","hb","H"],PK:["h","hB","H"],PL:["H","h"],PM:["H","hB"],PN:["H","h","hb","hB"],PR:["h","H","hB","hb"],PS:["h","hB","hb","H"],PT:["H","hB"],PW:["h","H"],PY:["h","H","hB","hb"],QA:["h","hB","hb","H"],RE:["H","hB"],RO:["H","hB"],RS:["H","hB","h"],RU:["H"],RW:["H","h"],SA:["h","hB","hb","H"],SB:["h","hb","H","hB"],SC:["H","h","hB"],SD:["h","hB","hb","H"],SE:["H"],SG:["h","hb","H","hB"],SH:["H","h","hb","hB"],SI:["H","hB"],SJ:["H"],SK:["H"],SL:["h","hb","H","hB"],SM:["H","h","hB"],SN:["H","h","hB"],SO:["h","H"],SR:["H","hB"],SS:["h","hb","H","hB"],ST:["H","hB"],SV:["h","H","hB","hb"],SX:["H","h","hb","hB"],SY:["h","hB","hb","H"],SZ:["h","hb","H","hB"],TA:["H","h","hb","hB"],TC:["h","hb","H","hB"],TD:["h","H","hB"],TF:["H","h","hB"],TG:["H","hB"],TH:["H","h"],TJ:["H","h"],TL:["H","hB","hb","h"],TM:["H","h"],TN:["h","hB","hb","H"],TO:["h","H"],TR:["H","hB"],TT:["h","hb","H","hB"],TW:["hB","hb","h","H"],TZ:["hB","hb","H","h"],UA:["H","hB","h"],UG:["hB","hb","H","h"],UM:["h","hb","H","hB"],US:["h","hb","H","hB"],UY:["h","H","hB","hb"],UZ:["H","hB","h"],VA:["H","h","hB"],VC:["h","hb","H","hB"],VE:["h","H","hB","hb"],VG:["h","hb","H","hB"],VI:["h","hb","H","hB"],VN:["H","h"],VU:["h","H"],WF:["H","hB"],WS:["h","H"],XK:["H","hB","h"],YE:["h","hB","hb","H"],YT:["H","hB"],ZA:["H","h","hb","hB"],ZM:["h","hb","H","hB"],ZW:["H","h"],"af-ZA":["H","h","hB","hb"],"ar-001":["h","hB","hb","H"],"ca-ES":["H","h","hB"],"en-001":["h","hb","H","hB"],"en-HK":["h","hb","H","hB"],"en-IL":["H","h","hb","hB"],"en-MY":["h","hb","H","hB"],"es-BR":["H","h","hB","hb"],"es-ES":["H","h","hB","hb"],"es-GQ":["H","h","hB","hb"],"fr-CA":["H","h","hB"],"gl-ES":["H","h","hB"],"gu-IN":["hB","hb","h","H"],"hi-IN":["hB","h","H"],"it-CH":["H","h","hB"],"it-IT":["H","h","hB"],"kn-IN":["hB","h","H"],"ku-SY":["H","hB"],"ml-IN":["hB","h","H"],"mr-IN":["hB","hb","h","H"],"pa-IN":["hB","hb","h","H"],"ta-IN":["hB","h","hb","H"],"te-IN":["hB","h","H"],"zu-ZA":["H","hB","hb","h"]};function is(e){let t=e.hourCycle;if(void 0===t&&e.hourCycles&&e.hourCycles.length&&(t=e.hourCycles[0]),t)switch(t){case"h24":return"k";case"h23":return"H";case"h12":return"h";case"h11":return"K";default:throw new Error("Invalid hourCycle")}const i=e.language;let s;return"root"!==i&&(s=e.maximize().region),(ts[s||""]||ts[i||""]||ts[`${i}-001`]||ts["001"])[0]}const ss=new RegExp(`^${es.source}*`),as=new RegExp(`${es.source}*$`);function ns(e,t){return{start:e,end:t}}const os=!!Object.fromEntries,rs=!!String.prototype.trimStart,ls=!!String.prototype.trimEnd,cs=os?Object.fromEntries:function(e){const t={};for(const[i,s]of e)t[i]=s;return t},ds=rs?function(e){return e.trimStart()}:function(e){return e.replace(ss,"")},hs=ls?function(e){return e.trimEnd()}:function(e){return e.replace(as,"")},us=new RegExp("([^\\p{White_Space}\\p{Pattern_Syntax}]*)","yu");var ps=class{constructor(e,t={}){this.message=e,this.position={offset:0,line:1,column:1},this.ignoreTag=!!t.ignoreTag,this.locale=t.locale,this.requiresOtherClause=!!t.requiresOtherClause,this.shouldParseSkeletons=!!t.shouldParseSkeletons}parse(){if(0!==this.offset())throw Error("parser can only be used once");if(this.message.length>0){const e=this.message.charCodeAt(0);if(35!==e&&39!==e&&60!==e&&123!==e&&125!==e){const e=function(e){if(0===e.length)return null;let t=1,i=1;for(let s=0;s<e.length;){const a=e.charCodeAt(s);switch(a){case 35:case 39:case 60:case 123:case 125:return null}if(10===a)t++,i=1,s++;else if(i++,a>=55296&&a<=56319&&s+1<e.length){const t=e.charCodeAt(s+1);s+=t>=56320&&t<=57343?2:1}else s++}return{offset:e.length,line:t,column:i}}(this.message);if(e){const t=this.clonePosition();return this.position=e,{val:[{type:0,value:this.message,location:ns(t,this.clonePosition())}],err:null}}}}return this.parseMessage(0,"",!1)}parseMessage(e,t,i){let s=[];for(;!this.isEOF();){const a=this.char();if(123===a){const t=this.parseArgument(e,i);if(t.err)return t;s.push(t.val)}else{if(125===a&&e>0)break;if(35!==a||"plural"!==t&&"selectordinal"!==t){if(60===a&&!this.ignoreTag&&47===this.peek()){if(i)break;return this.error(26,ns(this.clonePosition(),this.clonePosition()))}if(60===a&&!this.ignoreTag&&gs(this.peek()||0)){const i=this.parseTag(e,t);if(i.err)return i;s.push(i.val)}else{const i=this.parseLiteral(e,t);if(i.err)return i;s.push(i.val)}}else{const e=this.clonePosition();this.bump(),s.push({type:7,location:ns(e,this.clonePosition())})}}}return{val:s,err:null}}parseTag(e,t){const i=this.clonePosition();this.bump();const s=this.parseTagName();if(this.bumpSpace(),this.bumpIf("/>"))return{val:{type:0,value:`<${s}/>`,location:ns(i,this.clonePosition())},err:null};if(this.bumpIf(">")){const a=this.parseMessage(e+1,t,!0);if(a.err)return a;const n=a.val,o=this.clonePosition();if(this.bumpIf("</")){if(this.isEOF()||!gs(this.char()))return this.error(23,ns(o,this.clonePosition()));const e=this.clonePosition();return s!==this.parseTagName()?this.error(26,ns(e,this.clonePosition())):(this.bumpSpace(),this.bumpIf(">")?{val:{type:8,value:s,children:n,location:ns(i,this.clonePosition())},err:null}:this.error(23,ns(o,this.clonePosition())))}return this.error(27,ns(i,this.clonePosition()))}return this.error(23,ns(i,this.clonePosition()))}parseTagName(){const e=this.offset();for(this.bump();!this.isEOF()&&ms(this.char());)this.bump();return this.message.slice(e,this.offset())}parseLiteral(e,t){const i=this.clonePosition();let s="";for(;;){const i=this.tryParseQuote(t);if(i){s+=i;continue}const a=this.tryParseUnquoted(e,t);if(a){s+=a;continue}const n=this.tryParseLeftAngleBracket();if(!n)break;s+=n}return{val:{type:0,value:s,location:ns(i,this.clonePosition())},err:null}}tryParseLeftAngleBracket(){return this.isEOF()||60!==this.char()||!this.ignoreTag&&(gs(e=this.peek()||0)||47===e)?null:(this.bump(),"<");var e}tryParseQuote(e){if(this.isEOF()||39!==this.char())return null;switch(this.peek()){case 39:return this.bump(),this.bump(),"'";case 123:case 60:case 62:case 125:break;case 35:if("plural"===e||"selectordinal"===e)break;return null;default:return null}this.bump();const t=[this.char()];for(this.bump();!this.isEOF();){const e=this.char();if(39===e){if(39!==this.peek()){this.bump();break}t.push(39),this.bump()}else t.push(e);this.bump()}return String.fromCodePoint(...t)}tryParseUnquoted(e,t){if(this.isEOF())return null;const i=this.char();return 60===i||123===i||35===i&&("plural"===t||"selectordinal"===t)||125===i&&e>0?null:(this.bump(),String.fromCodePoint(i))}parseArgument(e,t){const i=this.clonePosition();if(this.bump(),this.bumpSpace(),this.isEOF())return this.error(1,ns(i,this.clonePosition()));if(125===this.char())return this.bump(),this.error(2,ns(i,this.clonePosition()));let s=this.parseIdentifierIfPossible().value;if(!s)return this.error(3,ns(i,this.clonePosition()));if(this.bumpSpace(),this.isEOF())return this.error(1,ns(i,this.clonePosition()));switch(this.char()){case 125:return this.bump(),{val:{type:1,value:s,location:ns(i,this.clonePosition())},err:null};case 44:return this.bump(),this.bumpSpace(),this.isEOF()?this.error(1,ns(i,this.clonePosition())):this.parseArgumentOptions(e,t,s,i);default:return this.error(3,ns(i,this.clonePosition()))}}parseIdentifierIfPossible(){const e=this.clonePosition(),t=this.offset(),i=function(e,t){return us.lastIndex=t,us.exec(e)[1]??""}(this.message,t),s=t+i.length;return this.bumpTo(s),{value:i,location:ns(e,this.clonePosition())}}parseArgumentOptions(e,t,i,s){let a=this.clonePosition(),n=this.parseIdentifierIfPossible().value,o=this.clonePosition();switch(n){case"":return this.error(4,ns(a,o));case"number":case"date":case"time":{this.bumpSpace();let e=null;if(this.bumpIf(",")){this.bumpSpace();const t=this.clonePosition(),i=this.parseSimpleArgStyleIfPossible();if(i.err)return i;const s=hs(i.val);if(0===s.length)return this.error(6,ns(this.clonePosition(),this.clonePosition()));e={style:s,styleLocation:ns(t,this.clonePosition())}}const t=this.tryParseArgumentClose(s);if(t.err)return t;const a=ns(s,this.clonePosition());if(e&&e.style.startsWith("::")){let t=ds(e.style.slice(2));if("number"===n){const s=this.parseNumberSkeletonFromString(t,e.styleLocation);return s.err?s:{val:{type:2,value:i,location:a,style:s.val},err:null}}{if(0===t.length)return this.error(10,a);let s=t;this.locale&&(s=function(e,t){let i="";for(let s=0;s<e.length;s++){const a=e.charAt(s);if("j"===a){let n=0;for(;s+1<e.length&&e.charAt(s+1)===a;)n++,s++;let o=1+(1&n),r=n<2?1:3+(n>>1),l="a",c=is(t);for("H"!=c&&"k"!=c||(r=0);r-- >0;)i+=l;for(;o-- >0;)i=c+i}else i+="J"===a?"H":a}return i}(t,this.locale));return{val:{type:"date"===n?3:4,value:i,location:a,style:{type:1,pattern:s,location:e.styleLocation,parsedOptions:this.shouldParseSkeletons?Ti(s):{}}},err:null}}}return{val:{type:"number"===n?2:"date"===n?3:4,value:i,location:a,style:e?.style??null},err:null}}case"plural":case"selectordinal":case"select":{const a=this.clonePosition();if(this.bumpSpace(),!this.bumpIf(","))return this.error(12,ns(a,{...a}));this.bumpSpace();let o=this.parseIdentifierIfPossible(),r=0;if("select"!==n&&"offset"===o.value){if(!this.bumpIf(":"))return this.error(13,ns(this.clonePosition(),this.clonePosition()));this.bumpSpace();const e=this.tryParseDecimalInteger(13,14);if(e.err)return e;this.bumpSpace(),o=this.parseIdentifierIfPossible(),r=e.val}const l=this.tryParsePluralOrSelectOptions(e,n,t,o);if(l.err)return l;const c=this.tryParseArgumentClose(s);if(c.err)return c;const d=ns(s,this.clonePosition());return"select"===n?{val:{type:5,value:i,options:cs(l.val),location:d},err:null}:{val:{type:6,value:i,options:cs(l.val),offset:r,pluralType:"plural"===n?"cardinal":"ordinal",location:d},err:null}}default:return this.error(5,ns(a,o))}}tryParseArgumentClose(e){return this.isEOF()||125!==this.char()?this.error(1,ns(e,this.clonePosition())):(this.bump(),{val:!0,err:null})}parseSimpleArgStyleIfPossible(){let e=0;const t=this.clonePosition();for(;!this.isEOF();)switch(this.char()){case 39:{this.bump();let e=this.clonePosition();if(!this.bumpUntil("'"))return this.error(11,ns(e,this.clonePosition()));this.bump();break}case 123:e+=1,this.bump();break;case 125:if(!(e>0))return{val:this.message.slice(t.offset,this.offset()),err:null};e-=1;break;default:this.bump()}return{val:this.message.slice(t.offset,this.offset()),err:null}}parseNumberSkeletonFromString(e,t){let i=[];try{i=function(e){if(0===e.length)throw new Error("Number skeleton cannot be empty");const t=e.split(Oi).filter(e=>e.length>0),i=[];for(const e of t){let t=e.split("/");if(0===t.length)throw new Error("Invalid number skeleton");const[s,...a]=t;for(const e of a)if(0===e.length)throw new Error("Invalid number skeleton");i.push({stem:s,options:a})}return i}(e)}catch{return this.error(7,t)}return{val:{type:0,tokens:i,location:t,parsedOptions:this.shouldParseSkeletons?Ui(i):{}},err:null}}tryParsePluralOrSelectOptions(e,t,i,s){let a=!1;const n=[],o=new Set;let{value:r,location:l}=s;for(;;){if(0===r.length){const e=this.clonePosition();if("select"===t||!this.bumpIf("="))break;{const t=this.tryParseDecimalInteger(16,19);if(t.err)return t;l=ns(e,this.clonePosition()),r=this.message.slice(e.offset,this.offset())}}if(o.has(r))return this.error("select"===t?21:20,l);"other"===r&&(a=!0),this.bumpSpace();const s=this.clonePosition();if(!this.bumpIf("{"))return this.error("select"===t?17:18,ns(this.clonePosition(),this.clonePosition()));const c=this.parseMessage(e+1,t,i);if(c.err)return c;const d=this.tryParseArgumentClose(s);if(d.err)return d;n.push([r,{value:c.val,location:ns(s,this.clonePosition())}]),o.add(r),this.bumpSpace(),({value:r,location:l}=this.parseIdentifierIfPossible())}return 0===n.length?this.error("select"===t?15:16,ns(this.clonePosition(),this.clonePosition())):this.requiresOtherClause&&!a?this.error(22,ns(this.clonePosition(),this.clonePosition())):{val:n,err:null}}tryParseDecimalInteger(e,t){let i=1;const s=this.clonePosition();this.bumpIf("+")||this.bumpIf("-")&&(i=-1);let a=!1,n=0;for(;!this.isEOF();){const e=this.char();if(!(e>=48&&e<=57))break;a=!0,n=10*n+(e-48),this.bump()}const o=ns(s,this.clonePosition());return a?(n*=i,Number.isSafeInteger(n)?{val:n,err:null}:this.error(t,o)):this.error(e,o)}offset(){return this.position.offset}isEOF(){return this.offset()===this.message.length}clonePosition(){return{offset:this.position.offset,line:this.position.line,column:this.position.column}}char(){const e=this.position.offset;if(e>=this.message.length)throw Error("out of bound");const t=this.message.codePointAt(e);if(void 0===t)throw Error(`Offset ${e} is at invalid UTF-16 code unit boundary`);return t}error(e,t){return{val:null,err:{kind:e,message:this.message,location:t}}}bump(){if(this.isEOF())return;const e=this.char();10===e?(this.position.line+=1,this.position.column=1,this.position.offset+=1):(this.position.column+=1,this.position.offset+=e<65536?1:2)}bumpIf(e){if(this.message.startsWith(e,this.offset())){for(let t=0;t<e.length;t++)this.bump();return!0}return!1}bumpUntil(e){const t=this.offset(),i=this.message.indexOf(e,t);return i>=0?(this.bumpTo(i),!0):(this.bumpTo(this.message.length),!1)}bumpTo(e){if(this.offset()>e)throw Error(`targetOffset ${e} must be greater than or equal to the current offset ${this.offset()}`);for(e=Math.min(e,this.message.length);;){const t=this.offset();if(t===e)break;if(t>e)throw Error(`targetOffset ${e} is at invalid UTF-16 code unit boundary`);if(this.bump(),this.isEOF())break}}bumpSpace(){for(;!this.isEOF()&&vs(this.char());)this.bump()}peek(){if(this.isEOF())return null;const e=this.char(),t=this.offset();return this.message.charCodeAt(t+(e>=65536?2:1))??null}};function gs(e){return e>=97&&e<=122||e>=65&&e<=90}function ms(e){return 45===e||46===e||e>=48&&e<=57||95===e||e>=97&&e<=122||e>=65&&e<=90||183==e||e>=192&&e<=214||e>=216&&e<=246||e>=248&&e<=893||e>=895&&e<=8191||e>=8204&&e<=8205||e>=8255&&e<=8256||e>=8304&&e<=8591||e>=11264&&e<=12271||e>=12289&&e<=55295||e>=63744&&e<=64975||e>=65008&&e<=65533||e>=65536&&e<=983039}function vs(e){return e>=9&&e<=13||32===e||133===e||e>=8206&&e<=8207||8232===e||8233===e}function fs(e){e.forEach(e=>{if(delete e.location,Ki(e)||Vi(e))for(const t in e.options)delete e.options[t].location,fs(e.options[t].value);else Wi(e)&&Ji(e.style)||(qi(e)||Gi(e))&&Qi(e.style)?delete e.style.location:Xi(e)&&fs(e.children)})}function _s(e,t={}){t={shouldParseSkeletons:!0,requiresOtherClause:!0,...t};const i=new ps(e,t).parse();if(i.err){const e=SyntaxError(ji[i.err.kind]);throw e.location=i.err.location,e.originalMessage=i.err.message,e}return t?.captureLocation||fs(i.val),i.val}var bs=class extends Error{constructor(e,t,i){super(e),this.code=t,this.originalMessage=i}toString(){return`[formatjs Error: ${this.code}] ${this.message}`}},ys=class extends bs{constructor(e,t,i,s){super(`Invalid values for "${e}": "${t}". Options are "${Object.keys(i).join('", "')}"`,"INVALID_VALUE",s)}},ws=class extends bs{constructor(e,t,i){super(`Value for "${e}" must be of type ${t}`,"INVALID_VALUE",i)}},$s=class extends bs{constructor(e,t){super(`The intl string context variable "${e}" was not provided to the string "${t}"`,"MISSING_VALUE",t)}};function xs(e){return"function"==typeof e}function ks(e,t,i,s,a,n,o){if(1===e.length&&Fi(e[0]))return[{type:0,value:e[0].value}];const r=[];for(const l of e){if(Fi(l)){r.push({type:0,value:l.value});continue}if(Yi(l)){"number"==typeof n&&r.push({type:0,value:i.getNumberFormat(t).format(n)});continue}const{value:e}=l;if(!a||!(e in a))throw new $s(e,o);let c=a[e];if(Zi(l))c&&"string"!=typeof c&&"number"!=typeof c&&"bigint"!=typeof c||(c="string"==typeof c||"number"==typeof c||"bigint"==typeof c?String(c):""),r.push({type:"string"==typeof c?0:1,value:c});else{if(qi(l)){const e="string"==typeof l.style?s.date[l.style]:Qi(l.style)?l.style.parsedOptions:void 0;r.push({type:0,value:i.getDateTimeFormat(t,e).format(c)});continue}if(Gi(l)){const e="string"==typeof l.style?s.time[l.style]:Qi(l.style)?l.style.parsedOptions:s.time.medium;r.push({type:0,value:i.getDateTimeFormat(t,e).format(c)});continue}if(Wi(l)){const e="string"==typeof l.style?s.number[l.style]:Ji(l.style)?l.style.parsedOptions:void 0;if(e&&e.scale){const t=e.scale||1;if("bigint"==typeof c){if(!Number.isInteger(t))throw new TypeError(`Cannot apply fractional scale ${t} to bigint value. Scale must be an integer when formatting bigint.`);c*=BigInt(t)}else c*=t}r.push({type:0,value:i.getNumberFormat(t,e).format(c)});continue}if(Xi(l)){const{children:e,value:c}=l,d=a[c];if(!xs(d))throw new ws(c,"function",o);let h=d(ks(e,t,i,s,a,n).map(e=>e.value));Array.isArray(h)||(h=[h]),r.push(...h.map(e=>({type:"string"==typeof e?0:1,value:e})))}if(Ki(l)){const e=c,n=(Object.prototype.hasOwnProperty.call(l.options,e)?l.options[e]:void 0)||l.options.other;if(!n)throw new ys(l.value,c,Object.keys(l.options),o);r.push(...ks(n.value,t,i,s,a));continue}if(Vi(l)){const e=`=${c}`;let n=Object.prototype.hasOwnProperty.call(l.options,e)?l.options[e]:void 0;if(!n){if(!Intl.PluralRules)throw new bs('Intl.PluralRules is not available in this environment.\nTry polyfilling it using "@formatjs/intl-pluralrules"\n',"MISSING_INTL_API",o);const e="bigint"==typeof c?Number(c):c,s=i.getPluralRules(t,{type:l.pluralType}).select(e-(l.offset||0));n=(Object.prototype.hasOwnProperty.call(l.options,s)?l.options[s]:void 0)||l.options.other}if(!n)throw new ys(l.value,c,Object.keys(l.options),o);const d="bigint"==typeof c?Number(c):c;r.push(...ks(n.value,t,i,s,a,d-(l.offset||0)));continue}}}return(l=r).length<2?l:l.reduce((e,t)=>{const i=e[e.length-1];return i&&0===i.type&&0===t.type?i.value+=t.value:e.push(t),e},[]);var l}function zs(e,t){return t?Object.keys(e).reduce((i,s)=>{var a,n;return i[s]=(a=e[s],(n=t[s])?{...a,...n,...Object.keys(a).reduce((e,t)=>(e[t]={...a[t],...n[t]},e),{})}:a),i},{...e}):e}function Ss(e){return{create:()=>({get:t=>e[t],set(t,i){e[t]=i}})}}var Es=class e{constructor(t,i=e.defaultLocale,s,a){if(this.formatterCache={number:{},dateTime:{},pluralRules:{}},this.format=e=>{const t=this.formatToParts(e);if(1===t.length)return t[0].value;const i=t.reduce((e,t)=>(e.length&&0===t.type&&"string"==typeof e[e.length-1]?e[e.length-1]+=t.value:e.push(t.value),e),[]);return i.length<=1?i[0]||"":i},this.formatToParts=e=>ks(this.ast,this.locales,this.formatters,this.formats,e,void 0,this.message),this.resolvedOptions=()=>({locale:this.resolvedLocale?.toString()||Intl.NumberFormat.supportedLocalesOf(this.locales)[0]}),this.getAst=()=>this.ast,this.locales=i,this.resolvedLocale=e.resolveLocale(i),"string"==typeof t){if(this.message=t,!e.__parse)throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");const{...i}=a||{};this.ast=e.__parse(t,{...i,locale:this.resolvedLocale})}else this.ast=t;if(!Array.isArray(this.ast))throw new TypeError("A message must be provided as a String or AST.");this.formats=zs(e.formats,s),this.formatters=a&&a.formatters||function(e={number:{},dateTime:{},pluralRules:{}}){return{getNumberFormat:yi((...e)=>new Intl.NumberFormat(...e),{cache:Ss(e.number),strategy:Ai.variadic}),getDateTimeFormat:yi((...e)=>new Intl.DateTimeFormat(...e),{cache:Ss(e.dateTime),strategy:Ai.variadic}),getPluralRules:yi((...e)=>new Intl.PluralRules(...e),{cache:Ss(e.pluralRules),strategy:Ai.variadic})}}(this.formatterCache)}static{this.memoizedDefaultLocale=null}static get defaultLocale(){return e.memoizedDefaultLocale||(e.memoizedDefaultLocale=(new Intl.NumberFormat).resolvedOptions().locale),e.memoizedDefaultLocale}static{this.resolveLocale=e=>{if(void 0===Intl.Locale)return;const t=Intl.NumberFormat.supportedLocalesOf(e);return t.length>0?new Intl.Locale(t[0]):new Intl.Locale("string"==typeof e?e:e[0])}}static{this.__parse=_s}static{this.formats={number:{integer:{maximumFractionDigits:0},currency:{style:"currency"},percent:{style:"percent"}},date:{short:{month:"numeric",day:"numeric",year:"2-digit"},medium:{month:"short",day:"numeric",year:"numeric"},long:{month:"long",day:"numeric",year:"numeric"},full:{weekday:"long",month:"long",day:"numeric",year:"numeric"}},time:{short:{hour:"numeric",minute:"numeric"},medium:{hour:"numeric",minute:"numeric",second:"numeric"},long:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"},full:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"}}}}};const As={en:bi},Cs={};function Ts(e){return e.replace(/['"]+/g,"").split(/[-_]/)[0].toLowerCase()}function Os(e){const t=Ts(e);return t in As||!we.includes(t)}function Hs(e,t,...i){const s=Ts(t);let a;try{a=e.split(".").reduce((e,t)=>e[t],As[s])}catch(t){a=e.split(".").reduce((e,t)=>e[t],As.en)}if(void 0===a&&(a=e.split(".").reduce((e,t)=>e[t],As.en)),!i.length)return a;const n={};for(let e=0;e<i.length;e+=2){let t=i[e];t=t.replace(/^{([^}]+)?}$/,"$1"),n[t]=i[e+1]}try{return new Es(a,t).format(n)}catch(e){return"Translation "+e}}function Ms(e,t,i){e.dispatchEvent(new CustomEvent(t,{detail:i,bubbles:!0,composed:!0,cancelable:!1}))}function Ds(e,t){return(e=e.toString()).split(",")[t]}function Ls(e,t){switch(t){case $t:return e.units==Oe?Z`${ii(lt)}`:Z`${ii(ct)}`;case $e:case vt:return e.units==Oe?Z`${ii(st)}`:Z`${ii(at)}`;case ht:return e.units==Oe?Z`${ii("m<sup>2</sup>")}`:Z`${ii(et)}`;case ut:return e.units==Oe?Z`${ii(tt)}`:Z`${ii(it)}`;default:return Z``}}function Ns(e,t){!function(e,t){Ms(e,"show-dialog",{dialogTag:"error-dialog",dialogImport:()=>Promise.resolve().then(function(){return Ra}),dialogParams:{error:t}})}(t,Z`
    ${e.error}:${e.body.message?Z` ${e.body.message} `:""}
  `)}const Is=(e,t,i=!1)=>{i?history.replaceState(null,"",t):history.pushState(null,"",t),Ms(window,"location-changed",{replace:i})};function Ps(e){var t;if(!e)return"Unknown error";if("string"==typeof e)return e;const i=e;return(null===(t=null==i?void 0:i.body)||void 0===t?void 0:t.message)||(null==i?void 0:i.message)||(null==i?void 0:i.error)||JSON.stringify(e)}function Bs(e,t){e.dispatchEvent(new CustomEvent("hass-notification",{detail:{message:t},bubbles:!0,composed:!0}))}function Rs(e,t,i,s){var a;Bs(e,`${Hs(i,null!==(a=null==t?void 0:t.language)&&void 0!==a?a:"en")}: ${Ps(s)}`)}var Us="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",js="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z";const Fs=e=>e.callWS({type:ye+"/config"}),Zs=(e,t)=>e.callApi("POST",ye+"/config",t),Ws=e=>e.callWS({type:ye+"/zones"}),qs=(e,t)=>e.callApi("POST",ye+"/zones",t),Gs=e=>e.callWS({type:ye+"/modules"}),Ks=e=>e.callWS({type:ye+"/allmodules"}),Vs=(e,t)=>e.callApi("POST",ye+"/modules",t),Ys=e=>e.callWS({type:ye+"/mappings"}),Xs=(e,t)=>e.callApi("POST",ye+"/mappings",t),Js=(e,t)=>e.callWS({type:ye+"/watering_calendar",zone_id:t}),Qs=(e,t)=>e.callWS({type:ye+"/schedule_save",schedule:t}),ea=e=>e.callWS({type:ye+"/weather_config"}),ta=(e,t,i,s)=>e.callWS({type:ye+"/weather_config_save",use_weather_service:t,weather_service:null!=i?i:null,api_key:null!=s?s:null}),ia=e=>e.callWS({type:ye+"/coordinates"}),sa=e=>{class i extends e{connectedCallback(){super.connectedCallback(),this.__checkSubscribed()}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const e=this.__unsubs.pop();e instanceof Promise?e.then(e=>e()):e()}this.__unsubs=void 0}}updated(e){super.updated(e),e.has("hass")&&this.__checkSubscribed()}hassSubscribe(){return[]}__checkSubscribed(){void 0===this.__unsubs&&this.isConnected&&void 0!==this.hass&&(this.__unsubs=this.hassSubscribe())}}return t([pe({attribute:!1})],i.prototype,"hass",void 0),i};var aa,na;!function(e){e.Sunrise="sunrise",e.Sunset="sunset",e.SolarAzimuth="solar_azimuth"}(aa||(aa={})),function(e){e.Disabled="disabled",e.Manual="manual",e.Automatic="automatic"}(na||(na={}));const oa=()=>{const e=e=>{let t={};for(let i=0;i<e.length;i+=2){const s=e[i],a=i<e.length?e[i+1]:void 0;t=Object.assign(Object.assign({},t),{[s]:a})}return t},t=window.location.pathname.split("/");let i={page:t[2]||"general",params:{}};if(t.length>3){let s=t.slice(3);if(t.includes("filter")){const t=s.findIndex(e=>"filter"==e),a=s.slice(t+1);s=s.slice(0,t),i=Object.assign(Object.assign({},i),{filter:e(a)})}s.length&&(s.length%2&&(i=Object.assign(Object.assign({},i),{subpage:s.shift()})),s.length&&(i=Object.assign(Object.assign({},i),{params:e(s)})))}return i},ra=(e,...t)=>{let i={page:e,params:{}};t.forEach(e=>{"string"==typeof e?i=Object.assign(Object.assign({},i),{subpage:e}):"params"in e?i=Object.assign(Object.assign({},i),{params:e.params}):"filter"in e&&(i=Object.assign(Object.assign({},i),{filter:e.filter}))});const s=e=>{let t=Object.keys(e);t=t.filter(t=>e[t]),t.sort();let i="";return t.forEach(t=>{const s=e[t];i=i.length?`${i}/${t}/${s}`:`${t}/${s}`}),i};let a=`/${ye}/${i.page}`;return i.subpage&&(a=`${a}/${i.subpage}`),s(i.params).length&&(a=`${a}/${s(i.params)}`),i.filter&&(a=`${a}/filter/${s(i.filter)}`),a},la=r`
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
`;const ca=e=>String(e).padStart(2,"0");function da(e){return e instanceof Date?e:new Date(e)}function ha(e){const t=da(e);return`${ca(t.getHours())}:${ca(t.getMinutes())}`}function ua(e){const t=da(e);return`${t.getFullYear()}-${ca(t.getMonth()+1)}-${ca(t.getDate())} ${ca(t.getHours())}:${ca(t.getMinutes())}`}function pa(e,t){return e.getFullYear()===t.getFullYear()&&e.getMonth()===t.getMonth()&&e.getDate()===t.getDate()}class ga extends(sa(le)){constructor(){super(...arguments),this.hideSettingsLinks=!1,this.actionsMode="full",this.zones=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._operationError=null,this._confirmIrrigate=null,this._skipDetailsOpen=!1,this._runMinutes={},this._now=Date.now(),this._countdownTimer=null,this._updateScheduled=!1}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}firstUpdated(){_e().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}disconnectedCallback(){super.disconnectedCallback(),this._stopCountdownTicker()}_syncCountdownTicker(){var e,t;const i=Object.keys(null!==(t=null===(e=this._outlook)||void 0===e?void 0:e.active_runs)&&void 0!==t?t:{}).length>0;i&&null===this._countdownTimer?this._countdownTimer=window.setInterval(()=>{this._now=Date.now()},1e3):i||this._stopCountdownTicker()}_stopCountdownTicker(){null!==this._countdownTimer&&(window.clearInterval(this._countdownTimer),this._countdownTimer=null)}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:ye+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[i,s,a]=await Promise.all([Fs(this.hass),Ws(this.hass),(t=this.hass,t.callWS({type:ye+"/irrigation_outlook"})).catch(e=>{console.error("Failed to fetch irrigation outlook:",e)})]);this.config=i,this.zones=s,this._outlook=a,this._initialLoadDone=!0,this._syncCountdownTicker()}catch(e){console.error("Error fetching data:",e),Rs(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}var t}handleCalculateAllZones(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",ye+"/zones",{calculate_all:!0})).catch(e=>{console.error("Failed to calculate all zones:",e),Rs(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after calc-all:",e))}))}handleUpdateAllZones(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",ye+"/zones",{update_all:!0})).catch(e=>{console.error("Failed to update all zones:",e),Rs(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after update-all:",e))}))}_canActuate(e){return!!(e.linked_entity||"service"===e.watering_mode&&e.run_service)}get _linkedZoneCount(){return this.zones.filter(e=>{var t;return this._canActuate(e)&&(null!==(t=e.duration)&&void 0!==t?t:0)>0}).length}async _doIrrigate(){var e;const t=this._confirmIrrigate;if(this._confirmIrrigate=null,null===t||!this.hass)return;const i="all"===t,s=i?void 0:this.zones.find(e=>{var i;return(null===(i=e.id)||void 0===i?void 0:i.toString())===t}),a=i?`(${this._linkedZoneCount})`:`: ${null!==(e=null==s?void 0:s.name)&&void 0!==e?e:t}`;try{await(n=this.hass,o=i?void 0:t,n.callWS(Object.assign({type:ye+"/irrigate_now"},void 0!==o?{zone_id:o}:{}))),Bs(this,`${Hs("panels.zones.confirm_irrigate.toast_started",this.hass.language)} ${a}`)}catch(e){const t=Ps(e);console.error("irrigate_now failed",e),Bs(this,`${Hs("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}var n,o}get _rainDelayUntil(){var e;const t=null===(e=this._outlook)||void 0===e?void 0:e.rain_delay_until;if(!t)return null;const i=new Date(t);return i.getTime()>Date.now()?i:null}async _setRainDelay(e){if(this.hass)try{await((e,t)=>e.callWS({type:ye+"/set_rain_delay",hours:t}))(this.hass,e),await this._fetchData()}catch(e){console.error("set_rain_delay failed",e),Rs(this,this.hass,"common.errors.action_failed",e)}}async _clearRainDelay(){var e;if(this.hass)try{await(e=this.hass,e.callWS({type:ye+"/clear_rain_delay"})),await this._fetchData()}catch(e){console.error("clear_rain_delay failed",e),Rs(this,this.hass,"common.errors.action_failed",e)}}_zoneRunMinutes(e){var t,i;const s=String(null!==(t=e.id)&&void 0!==t?t:"");return null!==(i=this._runMinutes[s])&&void 0!==i?i:10}async _runZoneFor(e){if(!this.hass||!this._canActuate(e)||void 0===e.id)return;const t=this._zoneRunMinutes(e);var i,s,a;if(t>0)try{await(i=this.hass,s=e.id.toString(),a=t,i.callWS({type:ye+"/run_zone",zone_id:s,duration:a})),Bs(this,`${Hs("panels.zones.run_zone.toast_started",this.hass.language)}: ${e.name} (${t} min)`)}catch(e){const t=Ps(e);console.error("run_zone failed",e),Bs(this,`${Hs("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}}_activeRun(e){var t,i;if(void 0!==e.id)return null===(i=null===(t=this._outlook)||void 0===t?void 0:t.active_runs)||void 0===i?void 0:i[String(e.id)]}_runSecondsLeft(e){if(!e.ends_at)return null;const t=Math.round((new Date(e.ends_at).getTime()-this._now)/1e3);return t>0?t:0}async _stopZone(e){var t,i;if(this.hass&&void 0!==e.id)try{await(t=this.hass,i=e.id.toString(),t.callWS({type:ye+"/stop_zone",zone_id:i})),Bs(this,`${Hs("panels.zones.stop_zone.toast_stopped",this.hass.language)}: ${e.name}`),await this._fetchData()}catch(e){const t=Ps(e);console.error("stop_zone failed",e),Bs(this,`${Hs("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}}handleCalculateZone(e){const t=this.zones[e];var i,s;t&&null!=t.id&&this.hass&&(this._operationError=null,this.isSaving=!0,this._scheduleUpdate(),(i=this.hass,s=t.id.toString(),i.callApi("POST",ye+"/zones",{id:s,calculate:!0,override_cache:!0})).catch(e=>{const t=Ps(e);console.error("calculateZone failed:",e),this._operationError=t}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after calc:",e))}))}handleUpdateZone(e){const t=this.zones[e];var i,s;t&&null!=t.id&&this.hass&&(this._operationError=null,this.isSaving=!0,this._scheduleUpdate(),(i=this.hass,s=t.id.toString(),i.callApi("POST",ye+"/zones",{id:s,update:!0})).catch(e=>{const t=Ps(e);console.error("updateZone failed:",e),this._operationError=t}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after update:",e))}))}_openZoneSettings(e){const t=void 0!==e.id?{params:{zone:String(e.id)}}:void 0;Is(0,t?ra("setup","zones",t):ra("setup","zones"))}_runTargetsZone(e,t){return"all"===e.zones||!(!Array.isArray(e.zones)||void 0===t.id)&&e.zones.map(e=>Number(e)).includes(Number(t.id))}get _nextIrrigateRun(){var e;return null===(e=this._outlook)||void 0===e?void 0:e.upcoming_runs.find(e=>"irrigate"===e.action&&e.next_run_utc)}_nextIrrigateRunForZone(e){var t;return null===(t=this._outlook)||void 0===t?void 0:t.upcoming_runs.find(t=>"irrigate"===t.action&&t.next_run_utc&&this._runTargetsZone(t,e))}get _activeGuards(){var e,t;return null!==(t=null===(e=this._outlook)||void 0===e?void 0:e.skip_preview.checks.filter(e=>e.enabled))&&void 0!==t?t:[]}get _triggeredGuards(){return this._activeGuards.filter(e=>e.would_skip)}_zoneHasDeficit(e){var t,i,s;const a=null!==(t=e.duration)&&void 0!==t?t:0,n=Number(null!==(i=e.bucket_threshold)&&void 0!==i?i:0),o=this._zoneEstimate(e),r=o&&o.available&&null!=o.live_deficit?o.live_deficit:Number(null!==(s=e.bucket)&&void 0!==s?s:0);return a>0&&r<n}_formatRunTime(e){if(!this.hass)return"";const t=this.hass.language,i=new Date(e),s=ha(i),a=new Date;return pa(i,a)?`${Hs("panels.zones.outlook.today",t)} ${s}`:pa(i,function(e,t){const i=new Date(e.getTime());return i.setDate(i.getDate()+t),i}(a,1))?`${Hs("panels.zones.outlook.tomorrow",t)} ${s}`:function(e,t){const i=da(e);return`${new Intl.DateTimeFormat(t,{weekday:"short"}).format(i)} ${ha(i)}`}(i,t)}_guardLabel(e){return Hs(`panels.zones.outlook.checks.${e.id}`,this.hass.language)}_guardDetail(e){var t;return e.available&&null!==e.observed?Hs(`panels.zones.outlook.check_detail.${e.id}`,this.hass.language,"{observed}",String(e.observed),"{threshold}",String(null!==(t=e.threshold)&&void 0!==t?t:"")):""}_renderSkipReasons(){const e=this.hass.language;return Z`
      <div class="outlook-line outlook-skip-reasons">
        <ul class="skip-reasons">
          ${this._triggeredGuards.map(e=>{const t=this._guardDetail(e);return Z`<li>
              ${this._guardLabel(e)}${t?Z` — ${t}`:""}
            </li>`})}
        </ul>
      </div>
      <div class="outlook-line outlook-dim skip-reasons-note">
        ${Hs("panels.zones.outlook.provisional",e)}
      </div>
    `}_openSchedules(){Is(0,ra("setup","when-to-water"))}_runActionLabel(e){return Hs(`panels.zones.outlook.actions.${e.action}`,this.hass.language)}_runTargetsLabel(e){const t=this.hass.language;if("all"===e.zones)return Hs("panels.zones.outlook.targets_all",t);const i=Array.isArray(e.zones)?e.zones.length:0;return Hs("panels.zones.outlook.targets_zones",t,"{count}",String(i))}_renderOutlookBanner(){if(!this.hass||!this._outlook)return Z``;const e=this.hass.language,t=this._nextIrrigateRun,i=this._triggeredGuards,s=this._outlook.last_skip_evaluation;return t&&t.next_run_utc?Z`
      <ha-card class="outlook-card">
        <div class="outlook">
          <div class="outlook-line outlook-headline">
            <ha-icon icon="mdi:calendar-clock"></ha-icon>
            <span>
              <strong
                >${Hs("panels.zones.outlook.next_run",e)}:</strong
              >
              ${this._runActionLabel(t)}
              ${this._formatRunTime(t.next_run_utc)}
              <span class="outlook-dim"
                >· ${t.name} · ${this._runTargetsLabel(t)}</span
              >
            </span>
          </div>

          ${i.length>0?Z`
                <div class="outlook-line outlook-skip">
                  <ha-icon icon="mdi:alert"></ha-icon>
                  <span
                    >${Hs("panels.zones.outlook.will_skip",e)}</span
                  >
                  <button
                    class="outlook-info-btn"
                    aria-expanded="${this._skipDetailsOpen}"
                    title="${Hs("panels.zones.outlook.why_skipped",e)}"
                    @click="${()=>{this._skipDetailsOpen=!this._skipDetailsOpen}}"
                  >
                    <ha-icon
                      icon="${this._skipDetailsOpen?"mdi:chevron-up":"mdi:information-outline"}"
                    ></ha-icon>
                    <span class="outlook-info-label"
                      >${Hs("panels.zones.outlook.why_skipped",e)}</span
                    >
                  </button>
                </div>
                ${this._skipDetailsOpen?this._renderSkipReasons():""}
              `:Z`
                <div class="outlook-line outlook-clear">
                  <ha-icon icon="mdi:check-circle-outline"></ha-icon>
                  <span
                    >${Hs("panels.zones.outlook.will_run",e)}</span
                  >
                </div>
              `}
          ${s?this._renderLastRunLine(s):""}
        </div>
      </ha-card>
    `:Z`
        <ha-card class="outlook-card">
          <div class="outlook">
            <div class="outlook-line outlook-headline">
              <ha-icon icon="mdi:calendar-alert"></ha-icon>
              <span>${Hs("panels.zones.outlook.no_schedule",e)}</span>
              ${this.hideSettingsLinks?"":Z`
                    <button
                      class="outlook-link"
                      @click="${this._openSchedules}"
                    >
                      ${Hs("panels.zones.outlook.setup_schedule",e)}
                    </button>
                  `}
            </div>
            ${s?this._renderLastRunLine(s):""}
          </div>
        </ha-card>
      `}_renderRainDelay(){if(!this.hass||"none"===this.actionsMode)return Z``;const e=this.hass.language,t=this._rainDelayUntil;return t?Z`
        <ha-card class="rain-delay-card paused">
          <div class="rain-delay">
            <ha-icon icon="mdi:pause-circle"></ha-icon>
            <span class="rain-delay-msg">
              <strong
                >${Hs("panels.zones.rain_delay.paused",e)}</strong
              >
              ${Hs("panels.zones.rain_delay.until",e)}
              ${ua(t.toISOString())}
            </span>
            <button class="action-btn" @click="${()=>this._clearRainDelay()}">
              <ha-icon icon="mdi:play"></ha-icon>
              ${Hs("panels.zones.rain_delay.resume",e)}
            </button>
          </div>
        </ha-card>
      `:Z`
      <div class="rain-delay-row">
        <span class="rain-delay-label">
          <ha-icon icon="mdi:weather-rainy"></ha-icon>
          ${Hs("panels.zones.rain_delay.title",e)}
        </span>
        <button class="action-btn" @click="${()=>this._setRainDelay(24)}">
          ${Hs("panels.zones.rain_delay.delay_24h",e)}
        </button>
        <button class="action-btn" @click="${()=>this._setRainDelay(48)}">
          ${Hs("panels.zones.rain_delay.delay_48h",e)}
        </button>
      </div>
    `}_renderLastRunLine(e){const t=this.hass.language,i=function(e,t){const i=da(e).getTime()-Date.now(),s=new Intl.RelativeTimeFormat(t,{numeric:"auto"}),a=Math.round(i/1e3);if(Math.abs(a)<60)return s.format(a,"second");const n=Math.round(a/60);if(Math.abs(n)<60)return s.format(n,"minute");const o=Math.round(n/60);if(Math.abs(o)<24)return s.format(o,"hour");const r=Math.round(o/24);if(Math.abs(r)<30)return s.format(r,"day");const l=Math.round(r/30);return Math.abs(l)<12?s.format(l,"month"):s.format(Math.round(l/12),"year")}(e.timestamp,t),s=e.checks.filter(e=>e.enabled&&e.would_skip).map(e=>this._guardLabel(e).toLowerCase()).join(", "),a=e.would_skip?`${Hs("panels.zones.outlook.last_run_skipped",t)}${s?` (${s})`:""}`:Hs("panels.zones.outlook.last_run_ran",t);return Z`
      <div class="outlook-line outlook-last">
        <span class="outlook-dim"
          >${Hs("panels.zones.outlook.last_run",t)}:</span
        >
        <span>${a} · ${i}</span>
      </div>
    `}_renderZoneDecision(e){var t;if(!this.hass)return Z``;const i=this.hass.language,s=null!==(t=e.duration)&&void 0!==t?t:0;let a,n,o;if(e.state===na.Disabled)a=Hs("panels.zones.status.decision_disabled",i),n="neutral",o="mdi:power-off";else if(e.last_calculated)if(this._zoneHasDeficit(e)){const t=function(e){const t=Math.round(e);if(t<60)return`${t} s`;const i=Math.floor(t/60),s=t%60;return s?`${i} min ${s} s`:`${i} min`}(s),r=this._triggeredGuards,l=this._nextIrrigateRunForZone(e);r.length>0?(a=Hs("panels.zones.status.decision_water_skip",i,"{duration}",t,"{reason}",this._guardLabel(r[0]).toLowerCase()),n="skip",o="mdi:weather-rainy"):l&&l.next_run_utc?(a=Hs("panels.zones.status.decision_water_at",i,"{duration}",t,"{time}",this._formatRunTime(l.next_run_utc)),n="water",o="mdi:water"):(a=Hs("panels.zones.status.decision_water_no_schedule",i,"{duration}",t),n="water",o="mdi:water-alert")}else a=Hs("panels.zones.status.decision_no_water",i),n="ok",o="mdi:check-circle-outline";else a=Hs("panels.zones.status.decision_unknown",i),n="unknown",o="mdi:help-circle-outline";return Z`
      <div class="zone-decision ${n}">
        <ha-icon icon="${o}"></ha-icon>
        <span>${a}</span>
      </div>
    `}_zoneEstimate(e){var t,i;if(void 0!==e.id)return null===(i=null===(t=this._outlook)||void 0===t?void 0:t.zone_estimates)||void 0===i?void 0:i[String(e.id)]}_zoneFault(e){var t,i;if(void 0!==e.id)return null===(i=null===(t=this._outlook)||void 0===t?void 0:t.zone_faults)||void 0===i?void 0:i[String(e.id)]}_renderZoneFault(e){if(!this.hass)return Z``;const t=this._zoneFault(e);if(!t)return Z``;const i=this.hass.language,s=Hs(`panels.zones.fault.${t.reason}`,i)||Hs("panels.zones.fault.generic",i),a=t.timestamp?ua(t.timestamp):"";return Z`
      <div class="zone-fault" title="${a}">
        <ha-icon icon="mdi:alert-circle"></ha-icon>
        <span>
          <strong>${Hs("panels.zones.fault.title",i)}</strong>
          — ${s}
        </span>
      </div>
    `}_zoneSkip(e){var t,i;if(void 0!==e.id)return null===(i=null===(t=this._outlook)||void 0===t?void 0:t.zone_skips)||void 0===i?void 0:i[String(e.id)]}_renderZoneSkip(e){if(!this.hass)return Z``;const t=this._zoneSkip(e);if(!t)return Z``;const i=this.hass.language,s=Hs("panels.zones.skip.soil_moisture",i,"{observed}",String(t.observed),"{threshold}",String(t.threshold)),a=t.timestamp?ua(t.timestamp):"";return Z`
      <div class="zone-skip" title="${a}">
        <ha-icon icon="mdi:water-off"></ha-icon>
        <span>
          <strong>${Hs("panels.zones.skip.title",i)}</strong>
          — ${s}
        </span>
      </div>
    `}_renderZoneEstimate(e){if(!this.hass)return Z``;const t=this._zoneEstimate(e);if(!t||!t.available||null==t.live_deficit)return Z``;const i=this.hass.language,s=Ls(this.config,vt),a=t.live_deficit<0?"var(--warning-color)":"var(--success-color)",n=Hs(`panels.zones.status.estimate_method.${"proxy"===t.method?"proxy":"hourly"}`,i)+(t.as_of?` · ${ha(t.as_of)}`:"");return Z`
      <span class="status-sep">·</span>
      <span class="zone-estimate" title="${n}">
        ${Hs("panels.zones.status.estimate_now",i)}
        <strong style="color: ${a}"
          >≈ ${t.live_deficit.toFixed(2)} ${s}</strong
        >
        <span class="estimate-tag"
          >${Hs("panels.zones.status.estimate_tag",i)}</span
        >
      </span>
    `}_renderZoneNextRun(e){if(!this.hass)return Z``;const t=this._nextIrrigateRunForZone(e);if(!t||!t.next_run_utc)return Z``;return e.state!==na.Disabled&&e.last_calculated&&this._zoneHasDeficit(e)&&0===this._triggeredGuards.length?Z``:Z`
      <span class="status-sep">·</span>
      <span>
        ${Hs("panels.zones.outlook.next_run",this.hass.language)}:
        <strong>${this._formatRunTime(t.next_run_utc)}</strong>
      </span>
    `}renderZone(e,t){var i,s;if(!this.hass)return Z``;const a=Number(null!==(i=e.bucket)&&void 0!==i?i:0),n=a<0?"var(--warning-color)":"var(--success-color)",o=e.state===na.Automatic?"state-automatic":e.state===na.Manual?"state-manual":"state-disabled",r=e.last_calculated?ua(e.last_calculated):Hs("panels.zones.status.never",this.hass.language);return Z`
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          <span class="zone-state-badge ${o}">
            ${Hs(`panels.zones.labels.states.${e.state}`,this.hass.language)}
          </span>
          ${this.hideSettingsLinks?"":Z`
                <ha-icon-button
                  .path="${"M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"}"
                  title="${Hs("panels.zones.actions.open_settings",this.hass.language)}"
                  @click="${()=>this._openZoneSettings(e)}"
                ></ha-icon-button>
              `}
        </div>

        <!-- RUN FAULT (e.g. valve didn't open) -->
        ${this._renderZoneFault(e)}

        <!-- SOIL-MOISTURE SKIP (wet-veto) -->
        ${this._renderZoneSkip(e)}

        <!-- AT-A-GLANCE DECISION -->
        ${this._renderZoneDecision(e)}

        <!-- COMPACT STATUS -->
        <div class="card-content">
          <div class="zone-status-line">
            <span
              title="${Hs("panels.zones.help.bucket",this.hass.language)}"
            >
              ${Hs("panels.zones.labels.bucket",this.hass.language)}:
              <strong style="color: ${n}"
                >${a.toFixed(2)}
                ${Ls(this.config,vt)}</strong
              >
            </span>
            <span class="status-sep">·</span>
            <span>
              ${Hs("panels.zones.status.last_checked",this.hass.language)}:
              <strong>${r}</strong>
            </span>
            ${this._renderZoneEstimate(e)} ${this._renderZoneNextRun(e)}
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div class="card-content zone-action-bar">
          ${"full"===this.actionsMode&&e.state===na.Automatic?Z`
                <button
                  class="action-btn"
                  title="${Hs("panels.zones.help.update",this.hass.language)}"
                  @click="${()=>this.handleUpdateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${Hs("panels.zones.actions.update",this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${Hs("panels.zones.help.calculate",this.hass.language)}"
                  @click="${()=>this.handleCalculateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${Hs("panels.zones.actions.calculate",this.hass.language)}
                </button>
              `:""}
          ${"none"!==this.actionsMode&&this._canActuate(e)&&(null!==(s=e.duration)&&void 0!==s?s:0)>0?Z`
                <button
                  class="action-btn"
                  raised
                  @click="${()=>{void 0!==e.id&&(this._confirmIrrigate=e.id.toString())}}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${Hs("panels.zones.labels.irrigate_now",this.hass.language)}
                </button>
              `:this._canActuate(e)?"":Z`
                  <button
                    class="action-btn"
                    disabled
                    title="${Hs("panels.zones.help.irrigate_link_entity",this.hass.language)}"
                  >
                    <ha-icon icon="mdi:water"></ha-icon>
                    ${Hs("panels.zones.labels.irrigate_now",this.hass.language)}
                  </button>
                  <span class="zones-top-note">
                    ${Hs("panels.zones.help.irrigate_link_entity",this.hass.language)}
                  </span>
                `}
          ${this._renderRunZoneControl(e)}
        </div>
      </ha-card>
    `}_renderRunZoneControl(e){if(!this.hass||"none"===this.actionsMode||!this._canActuate(e)||void 0===e.id)return Z``;const t=this.hass.language,i=String(e.id),s=this._activeRun(e);if(s){const i=this._runSecondsLeft(s);return Z`
        <div class="run-zone-control running">
          <span class="run-zone-countdown">
            <ha-icon icon="mdi:water-pump"></ha-icon>
            ${null===i?Hs("panels.zones.stop_zone.watering",t):this._formatCountdown(i)}
          </span>
          <button
            class="action-btn stop-btn"
            @click="${()=>this._stopZone(e)}"
          >
            <ha-icon icon="mdi:stop"></ha-icon>
            ${Hs("panels.zones.stop_zone.stop",t)}
          </button>
        </div>
      `}return Z`
      <div
        class="run-zone-control"
        title="${Hs("panels.zones.run_zone.help",t)}"
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
          >${Hs("panels.zones.run_zone.minutes",t)}</span
        >
        <button
          class="action-btn"
          @click="${()=>this._runZoneFor(e)}"
          ?disabled="${this.isSaving}"
        >
          <ha-icon icon="mdi:timer-play-outline"></ha-icon>
          ${Hs("panels.zones.run_zone.run",t)}
        </button>
      </div>
    `}_formatCountdown(e){const t=Math.max(0,e),i=Math.floor(t/3600),s=Math.floor(t%3600/60),a=t%60,n=e=>String(e).padStart(2,"0");return i>0?`${i}:${n(s)}:${n(a)}`:`${s}:${n(a)}`}render(){var e,t;if(!this.hass)return Z``;if(this.isLoading)return Z`
        <ha-card header="${Hs("panels.zones.title",this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Hs("common.loading-messages.general",this.hass.language)}
            </div>
          </div>
        </ha-card>
      `;const i=this.zones.some(e=>{var t;return this._canActuate(e)&&(null!==(t=e.duration)&&void 0!==t?t:0)>0}),s=0===this.zones.length;return Z`
      ${s?this.hideSettingsLinks?Z`
              <ha-card>
                <div class="card-content description-text">
                  ${Hs("panels.zones.no_items",this.hass.language)}
                </div>
              </ha-card>
            `:Z`
              <ha-card class="setup-banner-card">
                <div class="setup-banner">
                  <div class="setup-banner-icon">🌱</div>
                  <div class="setup-banner-content">
                    <div class="setup-banner-title">
                      ${Hs("wizard.title",this.hass.language)}
                    </div>
                    <div class="setup-banner-desc">
                      ${Hs("wizard.setup_complete_banner",this.hass.language)}
                    </div>
                  </div>
                  <button
                    class="action-btn setup-banner-btn"
                    @click="${()=>{this.dispatchEvent(new CustomEvent("open-wizard",{bubbles:!0,composed:!0}))}}"
                  >
                    ${Hs("wizard.open_wizard",this.hass.language)}
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
            ${Hs("panels.zones.title",this.hass.language)}
          </div>
        </div>
        <div class="card-content zones-top-actions">
          ${"full"===this.actionsMode?Z`
                <button
                  class="action-btn"
                  title="${Hs("panels.zones.help.update_all",this.hass.language)}"
                  @click="${this.handleUpdateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${Hs("panels.zones.cards.zone-actions.actions.update-all",this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${Hs("panels.zones.help.calculate_all",this.hass.language)}"
                  @click="${this.handleCalculateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${Hs("panels.zones.cards.zone-actions.actions.calculate-all",this.hass.language)}
                </button>
              `:""}
          ${"none"!==this.actionsMode?Z`
                <button
                  class="action-btn"
                  raised
                  title="${Hs("panels.zones.help.irrigate_all",this.hass.language)}"
                  @click="${()=>{this._confirmIrrigate="all"}}"
                  ?disabled="${!i||this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${Hs("panels.zones.actions.irrigate_all",this.hass.language)}
                </button>
              `:""}
          ${i?"":Z`<span class="zones-top-note"
                >${Hs("panels.info.cards.irrigate_now.no_linked_zones",this.hass.language)}</span
              >`}
        </div>
      </ha-card>

      <!-- Irrigate confirmation dialog -->
      ${null!==this._confirmIrrigate?Z`
            <ha-dialog
              open
              @closed="${()=>{this._confirmIrrigate=null}}"
              heading="${Hs("panels.zones.confirm_irrigate.title",this.hass.language)}"
            >
              <p>
                ${Hs("panels.zones.confirm_irrigate.body",this.hass.language)}
              </p>
              <p>
                <strong>
                  ${"all"===this._confirmIrrigate?`${Hs("panels.zones.confirm_irrigate.all_linked_zones",this.hass.language)} (${this._linkedZoneCount})`:null!==(t=null===(e=this.zones.find(e=>{var t;return(null===(t=e.id)||void 0===t?void 0:t.toString())===this._confirmIrrigate}))||void 0===e?void 0:e.name)&&void 0!==t?t:this._confirmIrrigate}
                </strong>
              </p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmIrrigate=null}}"
                >
                  ${Hs("common.actions.cancel",this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._doIrrigate}"
                >
                  ${Hs("panels.zones.labels.irrigate_now",this.hass.language)}
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Operation error banner -->
      ${this._operationError?Z`
            <ha-card class="error-banner-card">
              <div class="error-banner">
                <ha-icon
                  class="error-banner-icon"
                  icon="mdi:alert-circle-outline"
                ></ha-icon>
                <span class="error-banner-msg">${this._operationError}</span>
                <ha-icon-button
                  .path="${Us}"
                  @click="${()=>{this._operationError=null}}"
                  aria-label="${Hs("common.actions.cancel",this.hass.language)}"
                ></ha-icon-button>
              </div>
            </ha-card>
          `:""}

      <!-- Zone cards -->
      ${this.zones.map((e,t)=>this.renderZone(e,t))}
    `}static get styles(){return r`
      ${la}

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
    `}}t([pe()],ga.prototype,"config",void 0),t([pe({type:Boolean})],ga.prototype,"hideSettingsLinks",void 0),t([pe({attribute:!1})],ga.prototype,"actionsMode",void 0),t([pe({type:Array})],ga.prototype,"zones",void 0),t([ge()],ga.prototype,"_outlook",void 0),t([pe({type:Boolean})],ga.prototype,"isLoading",void 0),t([pe({type:Boolean})],ga.prototype,"isSaving",void 0),t([ge()],ga.prototype,"_operationError",void 0),t([ge()],ga.prototype,"_confirmIrrigate",void 0),t([ge()],ga.prototype,"_skipDetailsOpen",void 0),t([ge()],ga.prototype,"_runMinutes",void 0),t([ge()],ga.prototype,"_now",void 0),customElements.get("smart-irrigation-view-zones")||customElements.define("smart-irrigation-view-zones",ga)
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */;const ma={},va=Qt(class extends ei{constructor(e){if(super(e),e.type!==Xt&&e.type!==Vt&&e.type!==Jt)throw Error("The `live` directive is not allowed on child or event bindings");if(!(e=>void 0===e.strings)(e))throw Error("`live` bindings can only contain a single expression")}render(e){return e}update(e,[t]){if(t===W||t===q)return t;const i=e.element,s=e.name;if(e.type===Xt){if(t===i[s])return W}else if(e.type===Jt){if(!!t===i.hasAttribute(s))return W}else if(e.type===Vt&&i.getAttribute(s)===t+"")return W;return((e,t=ma)=>{e._$AH=t;
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */})(e),t}});let fa=class extends le{constructor(){super(...arguments),this.label="",this.unit="",this.help="",this.required=!1,this._helpOpen=!1}_toggleHelp(){this._helpOpen=!this._helpOpen}render(){return Z`
      <div class="si-field">
        <div class="si-field-header">
          <span class="si-field-label">
            ${this.label}${this.required?Z`<span class="si-field-required" aria-label="required">
                  *</span
                >`:""}
          </span>
          <span class="si-field-meta">
            ${this.unit?Z`<span class="si-field-unit">${this.unit}</span>`:""}
            ${this.help?Z`
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
        ${this._helpOpen&&this.help?Z`<div class="si-field-help-text">${this.help}</div>`:""}
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
    `}};t([pe()],fa.prototype,"label",void 0),t([pe()],fa.prototype,"unit",void 0),t([pe()],fa.prototype,"help",void 0),t([pe({type:Boolean})],fa.prototype,"required",void 0),t([ge()],fa.prototype,"_helpOpen",void 0),fa=t([de("si-field")],fa);let _a=class extends le{constructor(){super(...arguments),this.useWeather=!1,this.service=ze,this.apiKey="",this.weatherConfig=null,this._testing=!1,this._testResult=null,this._testResultTimer=null}disconnectedCallback(){super.disconnectedCallback(),this._testResultTimer&&(clearTimeout(this._testResultTimer),this._testResultTimer=null)}_emit(e,t){this.dispatchEvent(new CustomEvent(e,{detail:{value:t},bubbles:!0,composed:!0}))}get _noApiKeyServices(){var e,t;return null!==(t=null===(e=this.weatherConfig)||void 0===e?void 0:e.no_api_key_services)&&void 0!==t?t:[ze]}get _needsKey(){return this.useWeather&&!!this.service&&!this._noApiKeyServices.includes(this.service)}get _hasStoredKey(){const e=this.weatherConfig;return this.service===xe?!!(null==e?void 0:e.has_owm_api_key):this.service===ke?!!(null==e?void 0:e.has_pw_api_key):this.service===Se&&!!(null==e?void 0:e.has_met_api_key)}async _testApiKey(){if(this.hass&&!this._testing){this._testing=!0,this._testResult=null,this._testResultTimer&&(clearTimeout(this._testResultTimer),this._testResultTimer=null);try{this._testResult=await(e=this.hass,t=this.service,i=this.apiKey||null,e.callWS({type:ye+"/weather_config_test",weather_service:null!=t?t:null,api_key:null!=i?i:null})),this._testResultTimer=window.setTimeout(()=>{this._testResult=null,this._testResultTimer=null},12e3)}catch(e){this._testResult={success:!1,error:"unknown"}}finally{this._testing=!1}var e,t,i}}render(){var e,t;const i=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";return Z`
      <si-field
        label="${Hs("weather_service_config.enabled_label",i)}"
      >
        <ha-switch
          .checked="${this.useWeather}"
          @change="${e=>this._emit("useweather-changed",e.target.checked)}"
        ></ha-switch>
      </si-field>

      ${this.useWeather?this._renderServiceAndKey(i):""}
    `}_renderServiceAndKey(e){return Z`
      <si-field
        label="${Hs("weather_service_config.service_label",e)}"
      >
        <select
          class="si-input"
          .value="${va(this.service||ze)}"
          @change="${e=>{this._testResult=null,this._emit("service-changed",e.target.value)}}"
        >
          <option
            value="${ze}"
            ?selected="${(this.service||ze)===ze}"
          >
            ${Hs("weather_service_config.openmeteo",e)}
          </option>
          <option
            value="${xe}"
            ?selected="${this.service===xe}"
          >
            ${Hs("weather_service_config.owm",e)}
          </option>
          <option
            value="${ke}"
            ?selected="${this.service===ke}"
          >
            ${Hs("weather_service_config.pw",e)}
          </option>
          <option
            value="${Se}"
            ?selected="${this.service===Se}"
          >
            ${Hs("weather_service_config.met",e)}
          </option>
        </select>
      </si-field>

      ${this._needsKey?this._renderKeyField(e):Z`<div class="info-note">
            ${Hs("weather_service_config.no_api_key_needed",e)}
          </div>`}
    `}_renderKeyField(e){var t;const i=this._hasStoredKey;return Z`
      <si-field
        label="${Hs("weather_service_config.api_key_label",e)}"
        help="${Hs("weather_service_config.api_key_help",e)}"
      >
        <span class="api-badge ${i?"configured":"missing"}"
          >${Hs(i?"weather_service_config.api_key_configured":"weather_service_config.api_key_not_configured",e)}</span
        >
        <div class="api-row">
          <input
            type="password"
            class="si-input flex1"
            placeholder="${Hs("weather_service_config.api_key_placeholder",e)}"
            .value="${this.apiKey}"
            @input="${e=>{this._testResult=null,this._emit("apikey-changed",e.target.value)}}"
          />
          <button
            class="test-btn"
            type="button"
            ?disabled="${this._testing||!this.apiKey&&!i}"
            @click="${this._testApiKey}"
          >
            ${this._testing?Hs("weather_service_config.test_button_testing",e):Hs("weather_service_config.test_button",e)}
          </button>
        </div>
        ${null!==this._testResult?Z`<div
              class="test-result ${this._testResult.success?"success":"error"}"
            >
              ${this._testResult.success?Hs("weather_service_config.test_success",e):Hs("weather_service_config.test_error_"+(null!==(t=this._testResult.error)&&void 0!==t?t:"unknown"),e)}
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
    `}};t([pe({attribute:!1})],_a.prototype,"hass",void 0),t([pe({type:Boolean})],_a.prototype,"useWeather",void 0),t([pe()],_a.prototype,"service",void 0),t([pe()],_a.prototype,"apiKey",void 0),t([pe({attribute:!1})],_a.prototype,"weatherConfig",void 0),t([ge()],_a.prototype,"_testing",void 0),t([ge()],_a.prototype,"_testResult",void 0),_a=t([de("si-weather-source-config")],_a);let ba=class extends(sa(le)){constructor(){super(...arguments),this.section="all",this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._weatherConfig=null,this._weatherService=null,this._useWeatherService=!1,this._newApiKey="",this._weatherSaving=!1,this._coords=null,this._coordsEnabled=!1,this._coordsLat="",this._coordsLon="",this._coordsElev="",this._coordsSaving=!1,this._saveStatus="idle",this._savedResetTimer=null,this._updateScheduled=!1,this.debouncedSave=(()=>{let e=null;return t=>{e&&clearTimeout(e),e=window.setTimeout(()=>{this.saveData(t),e=null},500)}})()}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:ye+"_config_updated"})]}async _fetchData(){var e;if(!this.hass)return;const t=!this._initialLoadDone;t&&(this.isLoading=!0,this._scheduleUpdate());try{const[t,a,n]=await Promise.all([Fs(this.hass),ea(this.hass),ia(this.hass)]);this.config=t,this._weatherConfig=a,this._useWeatherService=a.use_weather_service,this._weatherService=null!==(e=a.weather_service)&&void 0!==e?e:ze,this._applyCoordinates(n),this.data=(i=this.config,s=["calctime","autocalcenabled","autoupdateenabled","autoupdateschedule","autoupdatefirsttime","autoupdateinterval","days_between_irrigation"],i?Object.entries(i).filter(([e])=>s.includes(e)).reduce((e,[t,i])=>Object.assign(e,{[t]:i}),{}):{}),this._initialLoadDone=!0}catch(e){console.error("Error fetching data:",e),Rs(this,this.hass,"common.errors.load_failed",e)}finally{t&&(this.isLoading=!1),this._scheduleUpdate()}var i,s}firstUpdated(){_e().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}render(){var e,t;return this.hass&&this.config&&this.data?this.isLoading?Z`<div class="loading-indicator">
        ${Hs("common.loading-messages.general",this.hass.language)}
      </div>`:Z`${this._renderSaveStatus()} ${this._renderCards()}`:Z`<div class="loading-indicator">
        ${Hs("common.loading-messages.configuration",null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en")}
      </div>`}_renderCards(){switch(this.section){case"weather-location":return Z`
          ${this._renderSection("weather")} ${this._renderWeatherServiceCard()}
          ${this._renderSection("location")} ${this._renderCoordinateCard()}
        `;case"when-to-water":return Z`
          ${this._renderSection("automation")} ${this._renderAutoUpdateCard()}
          ${this._renderAutoCalcCard()} ${this._renderWeatherSkipCard()}
          ${this._renderSection("watering")}
          ${this._renderDaysBetweenIrrigationCard()}
          ${this._renderZoneSequencingCard()} ${this._renderMasterSwitchCard()}
        `;default:return Z`
          ${this._renderSection("weather")} ${this._renderWeatherServiceCard()}
          ${this._renderWeatherSkipCard()} ${this._renderSection("automation")}
          ${this._renderAutoUpdateCard()} ${this._renderAutoCalcCard()}
          ${this._renderSection("location")} ${this._renderCoordinateCard()}
          ${this._renderSection("watering")}
          ${this._renderDaysBetweenIrrigationCard()}
          ${this._renderZoneSequencingCard()} ${this._renderMasterSwitchCard()}
        `}}_renderSection(e){return this.hass?Z`
      <div class="settings-section-header">
        ${Hs(`panels.general.sections.${e}`,this.hass.language)}
      </div>
    `:Z``}async _saveWeatherConfig(){if(this.hass){this._weatherSaving=!0,this._scheduleUpdate();try{await ta(this.hass,this._useWeatherService,this._useWeatherService?this._weatherService:null,this._newApiKey||null),this._newApiKey="",await this._fetchData()}catch(e){console.error("Failed to save weather config:",e),Rs(this,this.hass,"common.errors.save_failed",e)}finally{this._weatherSaving=!1,this._scheduleUpdate()}}}_renderWeatherServiceCard(){var e;return this.hass?Z`
      <ha-card
        header="${Hs("weather_service_config.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Hs("weather_service_config.description",this.hass.language)}
        </div>
        <div class="card-content">
          <si-weather-source-config
            .hass="${this.hass}"
            .useWeather="${this._useWeatherService}"
            .service="${null!==(e=this._weatherService)&&void 0!==e?e:ze}"
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
              ${this._weatherSaving?Hs("common.saving-messages.saving",this.hass.language):Hs("weather_service_config.save_button",this.hass.language)}
            </button>
          </div>
        </div>
      </ha-card>
    `:Z``}_renderAutoUpdateCard(){var e,t;return this.hass&&this.config&&this.data?Z`
      <ha-card
        header="${Hs("panels.general.cards.automatic-update.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Hs("panels.general.cards.automatic-update.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Hs("panels.general.cards.automatic-update.labels.auto-update-enabled",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.autoupdateenabled}"
              @change="${e=>this.handleConfigChange({autoupdateenabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.data.autoupdateenabled?Z`
                <div class="setting-row">
                  <label>
                    ${Hs("panels.general.cards.automatic-update.labels.auto-update-interval",this.hass.language)}
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
                      .value="${va(this.data.autoupdateschedule||Ae)}"
                      @change="${e=>this.handleConfigChange({autoupdateschedule:e.target.value})}"
                    >
                      <option
                        value="${Ee}"
                        ?selected="${(this.data.autoupdateschedule||Ae)===Ee}"
                      >
                        ${Hs("panels.general.cards.automatic-update.options.minutes",this.hass.language)}
                      </option>
                      <option
                        value="${Ae}"
                        ?selected="${(this.data.autoupdateschedule||Ae)===Ae}"
                      >
                        ${Hs("panels.general.cards.automatic-update.options.hours",this.hass.language)}
                      </option>
                      <option
                        value="${Ce}"
                        ?selected="${this.data.autoupdateschedule===Ce}"
                      >
                        ${Hs("panels.general.cards.automatic-update.options.days",this.hass.language)}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="setting-row">
                  <label>
                    ${Hs("panels.general.cards.automatic-update.labels.auto-update-delay",this.hass.language)}
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
    `:Z``}_renderAutoCalcCard(){return this.hass&&this.config&&this.data?Z`
      <ha-card
        header="${Hs("panels.general.cards.automatic-duration-calculation.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Hs("panels.general.cards.automatic-duration-calculation.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Hs("panels.general.cards.automatic-duration-calculation.labels.auto-calc-enabled",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.autocalcenabled}"
              @change="${e=>this.handleConfigChange({autocalcenabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.data.autocalcenabled?Z`
                <div class="setting-row">
                  <label>
                    ${Hs("panels.general.cards.automatic-duration-calculation.labels.calc-time",this.hass.language)}
                  </label>
                  <input
                    type="text"
                    class="settings-input shortfield"
                    .value="${this.config.calctime}"
                    @input="${e=>this.handleConfigChange({calctime:e.target.value})}"
                  />
                </div>
              `:""}
        </div>
      </ha-card>
    `:Z``}_renderWeatherSkipCard(){var e,t,i,s,a;if(!this.hass||!this.config||!this.data)return Z``;const n=this.hass.language,o=this.config.skip_irrigation_on_precipitation?"skip":this.config.forecast_weighting_enabled?"water_less":"ignore";return Z`
      <ha-card header="${Hs("weather_skip.title",this.hass.language)}">
        <div class="card-content description-text">
          ${Hs("weather_skip.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Hs("weather_skip.forecast_rain_label",n)}
            </label>
            <select
              class="settings-input"
              .value="${va(o)}"
              @change="${e=>{const t=e.target.value;this.handleConfigChange({skip_irrigation_on_precipitation:"skip"===t,forecast_weighting_enabled:"water_less"===t})}}"
            >
              ${["ignore","water_less","skip"].map(e=>Z`
                  <option value="${e}" ?selected="${o===e}">
                    ${Hs(`weather_skip.forecast_rain_options.${e}`,n)}
                  </option>
                `)}
            </select>
          </div>
          <div class="description-text">
            ${Hs(`weather_skip.forecast_rain_help.${o}`,n)}
          </div>
          ${"ignore"!==o?Z`
                <div class="setting-row">
                  <label>
                    ${Hs("weather_skip.lookahead_label",n)}
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
                  ${Hs("weather_skip.lookahead_help",n)}
                </div>
              `:""}
          ${"skip"===o?Z`
                <div class="setting-row">
                  <label>
                    ${Hs("weather_skip.threshold_label",n)}
                    (${Ls(this.config,$e)})
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
            ${Hs("weather_skip.temp_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Hs("weather_skip.temp_section_title",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_on_temp_enabled}"
              @change="${e=>this.handleConfigChange({skip_on_temp_enabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_temp_enabled?Z`
                <div class="setting-row">
                  <label>
                    ${Hs("weather_skip.temp_threshold_label",this.hass.language)}
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
            ${Hs("weather_skip.wind_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Hs("weather_skip.wind_section_title",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_on_wind_enabled}"
              @change="${e=>this.handleConfigChange({skip_on_wind_enabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_wind_enabled?Z`
                <div class="setting-row">
                  <label>
                    ${Hs("weather_skip.wind_threshold_label",this.hass.language)}
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
            ${Hs("weather_skip.freeze_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Hs("weather_skip.freeze_section_title",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_on_freeze_enabled}"
              @change="${e=>this.handleConfigChange({skip_on_freeze_enabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_freeze_enabled?Z`
                <div class="setting-row">
                  <label>
                    ${Hs("weather_skip.freeze_threshold_label",this.hass.language)}
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
                  ${Hs("weather_skip.freeze_help",this.hass.language)}
                </div>
              `:""}

          <div class="section-divider">
            ${Hs("weather_skip.rain_sensor_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Hs("weather_skip.rain_sensor_label",this.hass.language)}
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
    `}_applyCoordinates(e){this._coords=e,this._coordsEnabled=e.manual_coordinates_enabled;const t=(e,t)=>null!=e?String(e):null!=t?String(t):"";this._coordsLat=t(e.manual_latitude,e.ha_latitude),this._coordsLon=t(e.manual_longitude,e.ha_longitude),this._coordsElev=t(e.manual_elevation,e.ha_elevation)}async _saveCoordinates(){if(this.hass){this._coordsSaving=!0,this._scheduleUpdate();try{await(e=this.hass,t=this._coordsEnabled,i=this._coordsEnabled?parseFloat(this._coordsLat):null,s=this._coordsEnabled?parseFloat(this._coordsLon):null,a=this._coordsEnabled?parseFloat(this._coordsElev):null,e.callWS({type:ye+"/coordinates_save",manual_coordinates_enabled:t,manual_latitude:null!=i?i:null,manual_longitude:null!=s?s:null,manual_elevation:null!=a?a:null})),this._applyCoordinates(await ia(this.hass))}catch(e){console.error("Failed to save coordinates:",e),Rs(this,this.hass,"common.errors.save_failed",e)}finally{this._coordsSaving=!1,this._scheduleUpdate()}var e,t,i,s,a}}_renderCoordinateCard(){var e,t,i;if(!this.hass||!this._coords)return Z``;const s=this._coords;return Z`
      <ha-card
        header="${Hs("coordinate_config.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Hs("coordinate_config.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Hs("coordinate_config.manual_enabled",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this._coordsEnabled}"
              @change="${e=>{this._coordsEnabled=e.target.checked}}"
            ></ha-switch>
          </div>
          ${this._coordsEnabled?Z`
                <div class="setting-row">
                  <label>
                    ${Hs("coordinate_config.latitude",this.hass.language)}
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
                    ${Hs("coordinate_config.longitude",this.hass.language)}
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
                    ${Hs("coordinate_config.elevation",this.hass.language)}
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
              `:Z`
                <div
                  class="card-content"
                  style="color: var(--secondary-text-color); font-style: italic;"
                >
                  ${Hs("coordinate_config.current_ha_coords",this.hass.language)}:
                  ${Hs("coordinate_config.latitude",this.hass.language)}:
                  ${null!==(e=s.ha_latitude)&&void 0!==e?e:0},
                  ${Hs("coordinate_config.longitude",this.hass.language)}:
                  ${null!==(t=s.ha_longitude)&&void 0!==t?t:0},
                  ${Hs("coordinate_config.elevation",this.hass.language)}:
                  ${null!==(i=s.ha_elevation)&&void 0!==i?i:0}m
                </div>
              `}
          <div style="margin-top: 12px;">
            <button
              class="action-btn"
              raised
              ?disabled="${this._coordsSaving}"
              @click="${this._saveCoordinates}"
            >
              ${this._coordsSaving?Hs("common.saving-messages.saving",this.hass.language):Hs("common.actions.save",this.hass.language)}
            </button>
          </div>
        </div>
      </ha-card>
    `}_renderDaysBetweenIrrigationCard(){var e;return this.hass&&this.config&&this.data?Z`
      <ha-card
        header="${Hs("days_between_irrigation.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Hs("days_between_irrigation.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Hs("days_between_irrigation.label",this.hass.language)}
              <div class="setting-description">
                ${Hs("days_between_irrigation.help_text",this.hass.language)}
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
    `:Z``}_renderZoneSequencingCard(){var e,t;if(!this.hass||!this.config||!this.data)return Z``;const i=(this.config.zone_sequencing||Rt)===Ut;return Z`
      <ha-card
        header="${Hs("zone_sequencing.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Hs("zone_sequencing.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Hs("zone_sequencing.title",this.hass.language)}
            </label>
            <select
              class="settings-input"
              .value="${va(this.config.zone_sequencing||Rt)}"
              @change="${e=>this.handleConfigChange({[Pt]:e.target.value})}"
            >
              <option
                value="${Rt}"
                ?selected="${(this.config.zone_sequencing||Rt)===Rt}"
              >
                ${Hs("zone_sequencing.parallel",this.hass.language)}
              </option>
              <option
                value="${Bt}"
                ?selected="${this.config.zone_sequencing===Bt}"
              >
                ${Hs("zone_sequencing.sequential",this.hass.language)}
              </option>
              <option
                value="${Ut}"
                ?selected="${this.config.zone_sequencing===Ut}"
              >
                ${Hs("zone_sequencing.rotating",this.hass.language)}
              </option>
            </select>
          </div>
          ${i?Z`
                <div class="setting-row">
                  <label>
                    ${Hs("zone_sequencing.max_consecutive_duration_label",this.hass.language)}
                  </label>
                  <input
                    type="number"
                    min="1"
                    class="settings-input"
                    .value="${null!==(e=this.config.zone_sequencing_max_consecutive_duration)&&void 0!==e?e:5}"
                    @input="${e=>{const t=parseInt(e.target.value,10);isNaN(t)||this.handleConfigChange({[jt]:t})}}"
                  />
                  <span class="unit-label">
                    ${Hs("zone_sequencing.max_consecutive_duration_unit",this.hass.language)}
                  </span>
                </div>
                <div class="setting-row">
                  <label>
                    ${Hs("zone_sequencing.min_absorption_time_label",this.hass.language)}
                  </label>
                  <input
                    type="number"
                    min="0"
                    class="settings-input"
                    .value="${null!==(t=this.config.zone_sequencing_min_absorption_time)&&void 0!==t?t:0}"
                    @input="${e=>{const t=parseInt(e.target.value,10);isNaN(t)||this.handleConfigChange({[Ft]:t})}}"
                  />
                  <span class="unit-label">
                    ${Hs("zone_sequencing.min_absorption_time_unit",this.hass.language)}
                  </span>
                </div>
              `:""}
        </div>
      </ha-card>
    `}_renderMasterSwitchCard(){var e,t;if(!this.hass||!this.config)return Z``;const i=!!this.config.master_kick_enabled;return Z`
      <ha-card header="${Hs("master.title",this.hass.language)}">
        <div class="card-content description-text">
          ${Hs("master.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>${Hs("master.entity",this.hass.language)}</label>
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${this.config.master_entity||""}"
              .includeDomains="${["switch","valve","input_boolean"]}"
              allow-custom-entity
              @value-changed="${e=>this.handleConfigChange({[Zt]:e.detail.value||null})}"
            ></ha-entity-picker>
          </div>
          ${this.config.master_entity?Z`
                <div class="setting-row">
                  <label
                    >${Hs("master.kick_enabled",this.hass.language)}</label
                  >
                  <ha-switch
                    .checked="${i}"
                    @change="${e=>this.handleConfigChange({[qt]:e.target.checked})}"
                  ></ha-switch>
                </div>
                ${i?Z`
                      <div class="setting-row">
                        <label>
                          ${Hs("master.kick_pause",this.hass.language)}
                        </label>
                        <input
                          type="number"
                          min="0"
                          step="0.1"
                          class="settings-input"
                          .value="${null!==(e=this.config.master_kick_pause_seconds)&&void 0!==e?e:1}"
                          @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({[Gt]:t})}}"
                        />
                        <span class="unit-label">
                          ${Hs("master.seconds_unit",this.hass.language)}
                        </span>
                      </div>
                    `:""}
                <div class="setting-row">
                  <label
                    >${Hs("master.settle",this.hass.language)}</label
                  >
                  <input
                    type="number"
                    min="0"
                    class="settings-input"
                    .value="${null!==(t=this.config.master_settle_seconds)&&void 0!==t?t:10}"
                    @input="${e=>{const t=parseInt(e.target.value,10);isNaN(t)||this.handleConfigChange({[Wt]:t})}}"
                  />
                  <span class="unit-label">
                    ${Hs("master.seconds_unit",this.hass.language)}
                  </span>
                </div>
                <div class="setting-row">
                  <label
                    >${Hs("master.off_after",this.hass.language)}</label
                  >
                  <ha-switch
                    .checked="${!!this.config.master_off_after}"
                    @change="${e=>this.handleConfigChange({[Kt]:e.target.checked})}"
                  ></ha-switch>
                </div>
              `:""}
        </div>
      </ha-card>
    `}async saveData(e){if(this.hass&&this.data){this.isSaving=!0,this._saveStatus="saving",this._scheduleUpdate();try{this.data=Object.assign(Object.assign({},this.data),e),this._scheduleUpdate(),await Zs(this.hass,this.data),this._markSaved()}catch(e){console.error("Error saving config:",e),this._saveStatus="idle",Rs(this,this.hass,"common.errors.save_failed",e),await this._fetchData()}finally{this.isSaving=!1,this._scheduleUpdate()}}}_markSaved(){this._saveStatus="saved",this._savedResetTimer&&clearTimeout(this._savedResetTimer),this._savedResetTimer=window.setTimeout(()=>{this._saveStatus="idle",this._scheduleUpdate()},2e3)}_renderSaveStatus(){if(!this.hass||"idle"===this._saveStatus)return Z``;const e="saving"===this._saveStatus;return Z`
      <div class="save-status-float ${this._saveStatus}">
        <ha-icon
          icon="${e?"mdi:content-save-outline":"mdi:check-circle"}"
        ></ha-icon>
        ${Hs(e?"common.saving-messages.saving":"panels.zones.status.saved",this.hass.language)}
      </div>
    `}handleConfigChange(e){this.config&&(this.config=Object.assign(Object.assign({},this.config),e)),this.debouncedSave(e)}disconnectedCallback(){super.disconnectedCallback(),this._savedResetTimer&&(clearTimeout(this._savedResetTimer),this._savedResetTimer=null)}static get styles(){return r`
      ${la}

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
    `}};t([pe()],ba.prototype,"narrow",void 0),t([pe()],ba.prototype,"path",void 0),t([pe()],ba.prototype,"section",void 0),t([pe()],ba.prototype,"data",void 0),t([pe()],ba.prototype,"config",void 0),t([pe({type:Boolean})],ba.prototype,"isLoading",void 0),t([pe({type:Boolean})],ba.prototype,"isSaving",void 0),t([pe()],ba.prototype,"_weatherConfig",void 0),t([pe()],ba.prototype,"_weatherService",void 0),t([pe({type:Boolean})],ba.prototype,"_useWeatherService",void 0),t([pe()],ba.prototype,"_newApiKey",void 0),t([pe({type:Boolean})],ba.prototype,"_weatherSaving",void 0),t([ge()],ba.prototype,"_coords",void 0),t([ge()],ba.prototype,"_coordsEnabled",void 0),t([ge()],ba.prototype,"_coordsLat",void 0),t([ge()],ba.prototype,"_coordsLon",void 0),t([ge()],ba.prototype,"_coordsElev",void 0),t([ge()],ba.prototype,"_coordsSaving",void 0),t([ge()],ba.prototype,"_saveStatus",void 0),ba=t([de("smart-irrigation-view-general")],ba);const ya=e=>9*e/5+32;function wa(e,t,i){if(null==e||Number.isNaN(e))return null;switch(t){case"temperature":return i?{value:e,unit:"°C"}:{value:ya(e),unit:"°F"};case"precipitation":return i?{value:e,unit:st}:{value:(n=e,n/25.4),unit:at};case"windspeed":return i?{value:e,unit:rt}:{value:(a=e,2.2369362920544*a),unit:ot};case"pressure":return i?{value:e,unit:"hPa"}:{value:(s=e,.0295299830714*s),unit:nt}}var s,a,n}function $a(e,t,i,s){const a=wa(e,t,i);if(!a)return"-";const n=function(e,t){return"pressure"===e?t?0:2:"precipitation"===e?t?1:2:1}(t,i);return`${a.value.toFixed(n)} ${a.unit}`}function xa(e,t){return null==e||Number.isNaN(e)?"-":t?`${e.toFixed(0)} L`:`${(e=>.264172052*e)(e).toFixed(1)} gal`}let ka=class extends le{constructor(){super(...arguments),this.metric=!0,this.name="",this.size="",this.throughput="",this.linkedEntity="",this.showEntity=!1}_emit(e,t){this.dispatchEvent(new CustomEvent(e,{detail:{value:t},bubbles:!0,composed:!0}))}render(){var e,t;const i=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en",s=this.metric?"m²":et,a=this.metric?tt:it;return Z`
      <si-field label="${Hs("panels.zones.labels.name",i)}" required>
        <input
          type="text"
          class="si-input"
          .value="${this.name}"
          @input="${e=>this._emit("name-changed",e.target.value)}"
        />
      </si-field>

      <si-field
        label="${Hs("panels.zones.labels.size",i)}"
        unit="${s}"
        help="${Hs("field_help.zone_size",i)}"
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
        label="${Hs("panels.zones.labels.throughput",i)}"
        unit="${a}"
        help="${Hs("field_help.zone_throughput",i)}"
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

      ${this.showEntity?Z`
            <si-field
              label="${Hs("panels.zones.labels.linked_entity",i)}"
              help="${Hs("field_help.zone_linked_entity",i)}"
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
    `}};t([pe({attribute:!1})],ka.prototype,"hass",void 0),t([pe({type:Boolean})],ka.prototype,"metric",void 0),t([pe()],ka.prototype,"name",void 0),t([pe()],ka.prototype,"size",void 0),t([pe()],ka.prototype,"throughput",void 0),t([pe()],ka.prototype,"linkedEntity",void 0),t([pe({type:Boolean})],ka.prototype,"showEntity",void 0),ka=t([de("si-zone-form")],ka);let za=class extends(sa(le)){constructor(){super(...arguments),this.zones=[],this.modules=[],this.mappings=[],this.isLoading=!0,this._initialLoadDone=!1,this._scrolledTo=null,this._expanded=new Set,this.isSaving=!1,this._showAddZone=!1,this._pendingConfirm=null,this._saveStatus="idle",this._savedResetTimer=null,this._confirmDeleteZoneId=null,this._newZoneName="",this._newZoneSize="",this._newZoneThroughput="",this._newZoneEntity="",this._updateScheduled=!1,this.globalDebounceTimer=null}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}get _targetZoneId(){var e,t;const i=null===(t=null===(e=this.path)||void 0===e?void 0:e.params)||void 0===t?void 0:t.zone;return null!=i&&""!==i?Number(i):null}_isExpanded(e){return void 0!==e.id&&this._expanded.has(e.id)}_toggleZone(e){const t=new Set(this._expanded);t.has(e)?t.delete(e):t.add(e),this._expanded=t}firstUpdated(){_e().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}updated(){var e;const t=this._targetZoneId;if(null===t||this.isLoading)return;if(this._scrolledTo===t)return;if(!this._expanded.has(t))return void(this._expanded=new Set(this._expanded).add(t));const i=null===(e=this.shadowRoot)||void 0===e?void 0:e.querySelector(`#zone-${t}`);i&&(this._scrolledTo=t,requestAnimationFrame(()=>i.scrollIntoView({behavior:"smooth",block:"start"})))}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:ye+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[t,i,s,a]=await Promise.all([Fs(this.hass),Ws(this.hass),Gs(this.hass),Ys(this.hass)]);this.config=t,this.zones=i,this.modules=s,this.mappings=a,this._initialLoadDone=!0}catch(e){console.error("Error fetching data:",e),Rs(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}handleResetAllBuckets(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",ye+"/zones",{reset_all_buckets:!0})).catch(e=>{console.error("Failed to reset all buckets:",e),Rs(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after reset:",e))}))}handleClearAllWeatherdata(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",ye+"/zones",{clear_all_weatherdata:!0})).catch(e=>{console.error("Failed to clear all weather data:",e),Rs(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after clear-weather:",e))}))}handleAddZone(){var e;if(!this._newZoneName.trim())return;const t=null!==(e=this.modules.find(e=>"PyETO"===e.name))&&void 0!==e?e:this.modules[0],i=this.mappings[0],s={name:this._newZoneName.trim(),size:Math.round(100*(parseFloat(this._newZoneSize)||0))/100,throughput:Math.round(100*(parseFloat(this._newZoneThroughput)||0))/100,state:na.Automatic,duration:0,bucket:0,module:null==t?void 0:t.id,delta:0,explanation:"",multiplier:1,mapping:null==i?void 0:i.id,lead_time:0,maximum_duration:void 0,maximum_bucket:void 0,drainage_rate:void 0,current_drainage:0,linked_entity:this._newZoneEntity||void 0};this.zones=[...this.zones,s],this.isSaving=!0,this._showAddZone=!1,this.saveToHA(s).then(()=>(this._newZoneName="",this._newZoneSize="",this._newZoneThroughput="",this._newZoneEntity="",this._fetchData())).catch(e=>{console.error("Failed to add zone:",e),this.zones=this.zones.slice(0,-1),Rs(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()})}handleEditZone(e,t){this.hass&&(this.zones=this.zones.map((i,s)=>s===e?t:i),this.globalDebounceTimer&&clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=window.setTimeout(()=>{this.isSaving=!0,this._saveStatus="saving",this.saveToHA(t).then(()=>this._markSaved()).catch(e=>{console.error("Failed to save zone:",e),this._saveStatus="idle",Rs(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}),this.globalDebounceTimer=null},500),this._scheduleUpdate())}handleRemoveZone(e){this._confirmDeleteZoneId=e}_confirmDelete(){const e=this._confirmDeleteZoneId;if(null===e||!this.hass)return;const t=this.zones.findIndex(t=>t.id===e);if(-1===t)return;const i=[...this.zones];var s,a;this.zones=this.zones.filter(t=>t.id!==e),this._confirmDeleteZoneId=null,this.isSaving=!0,(s=this.hass,a=e.toString(),s.callApi("POST",ye+"/zones",{id:a,remove:!0})).catch(e=>{console.error("Failed to delete zone:",e),Rs(this,this.hass,"common.errors.delete_failed",e),this.zones=i,this._fetchData().catch(e=>console.error("Failed to refresh data after delete error:",e))}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()})}_runPendingConfirm(){const e=this._pendingConfirm;this._pendingConfirm=null,null==e||e.onConfirm()}_markSaved(){this._saveStatus="saved",this._savedResetTimer&&clearTimeout(this._savedResetTimer),this._savedResetTimer=window.setTimeout(()=>{this._saveStatus="idle",this._scheduleUpdate()},2e3),this._scheduleUpdate()}_renderSaveStatus(){if(!this.hass||"idle"===this._saveStatus)return Z``;const e="saving"===this._saveStatus;return Z`
      <span class="save-status ${this._saveStatus}">
        <ha-icon
          icon="${e?"mdi:content-save-outline":"mdi:check-circle"}"
        ></ha-icon>
        ${Hs(e?"common.saving-messages.saving":"panels.zones.status.saved",this.hass.language)}
      </span>
    `}async saveToHA(e){if(!this.hass)throw new Error("Home Assistant connection not available");await qs(this.hass,e)}_renderModuleOptions(e){if(!this.hass)return Z``;const t=null!=e?String(e):"";return Z`
      <option value="" ?selected="${""===t}">
        ---${Hs("common.labels.select",this.hass.language)}---
      </option>
      ${this.modules.map(e=>Z`
          <option value="${e.id}" ?selected="${t===String(e.id)}">
            ${e.id}: ${e.name}
          </option>
        `)}
    `}_renderMappingOptions(e){if(!this.hass)return Z``;const t=null!=e?String(e):"";return Z`
      <option value="" ?selected="${""===t}">
        ---${Hs("common.labels.select",this.hass.language)}---
      </option>
      ${this.mappings.map(e=>Z`
          <option value="${e.id}" ?selected="${t===String(e.id)}">
            ${e.id}: ${e.name}
          </option>
        `)}
    `}renderZone(e,t){var i,s,a,n,o,r,l,c,d,h,u,p,g,m,v,f;if(!this.hass)return Z``;const _=this._isExpanded(e);return Z`
      <ha-card id="zone-${null!==(i=e.id)&&void 0!==i?i:"new"}">
        <div
          class="card-header zone-toggle"
          role="button"
          tabindex="0"
          aria-expanded="${_?"true":"false"}"
          @click="${()=>void 0!==e.id&&this._toggleZone(e.id)}"
          @keydown="${t=>{"Enter"!==t.key&&" "!==t.key||void 0===e.id||(t.preventDefault(),this._toggleZone(e.id))}}"
        >
          <div class="name">${e.name}</div>
          <ha-icon
            class="zone-chevron"
            icon="${_?"mdi:chevron-up":"mdi:chevron-down"}"
          ></ha-icon>
        </div>
        ${_?Z`
              <!-- Settings shown directly (no longer collapsible — the calendar that
             used to sit alongside it moved to the Weather & Location tab). -->
              <div class="card-content zone-settings">
                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.name",this.hass.language)}</span
                  >
                  <input
                    type="text"
                    class="settings-input"
                    .value="${e.name}"
                    @input="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[dt]:i.target.value}))}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.size",this.hass.language)}
                    (${Ls(this.config,ht)})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat(e.size.toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[ht]:s}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.throughput",this.hass.language)}
                    (${Ls(this.config,ut)})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat(e.throughput.toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[ut]:s}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.soil_type",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Hs("field_help.zone_soil_type",this.hass.language)}</span
                  >
                  <select
                    class="settings-input"
                    .value="${va(null!==(s=Object.keys(It).find(t=>It[t]===e.drainage_rate))&&void 0!==s?s:"custom")}"
                    @change="${i=>{const s=i.target.value;"custom"!==s&&void 0!==It[s]&&this.handleEditZone(t,Object.assign(Object.assign({},e),{[$t]:It[s]}))}}"
                  >
                    <option
                      value="custom"
                      ?selected="${!Object.values(It).includes(null!==(a=e.drainage_rate)&&void 0!==a?a:-1)}"
                    >
                      ${Hs("panels.zones.labels.soil_types.custom",this.hass.language)}
                    </option>
                    ${Object.keys(It).map(t=>Z`
                        <option
                          value="${t}"
                          ?selected="${It[t]===e.drainage_rate}"
                        >
                          ${Hs(`panels.zones.labels.soil_types.${t}`,this.hass.language)}
                        </option>
                      `)}
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.drainage_rate",this.hass.language)}
                    (${Ls(this.config,$t)})</span
                  >
                  <span slot="description"
                    >${Hs("field_help.zone_drainage_rate",this.hass.language)}</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat((null!==(n=e.drainage_rate)&&void 0!==n?n:0).toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[$t]:s}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.plant_type",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Hs("field_help.zone_plant_type",this.hass.language)}</span
                  >
                  <select
                    class="settings-input"
                    .value="${va(null!==(o=e.plant_type)&&void 0!==o?o:"custom")}"
                    @change="${i=>{const s=i.target.value,a={[kt]:s};"custom"!==s&&void 0!==Nt[s]&&(a.kc=Nt[s]),this.handleEditZone(t,Object.assign(Object.assign({},e),a))}}"
                  >
                    <option
                      value="custom"
                      ?selected="${"custom"===(null!==(r=e.plant_type)&&void 0!==r?r:"custom")}"
                    >
                      ${Hs("panels.zones.labels.plant_types.custom",this.hass.language)}
                    </option>
                    ${Object.keys(Nt).map(t=>Z`
                        <option
                          value="${t}"
                          ?selected="${e.plant_type===t}"
                        >
                          ${Hs(`panels.zones.labels.plant_types.${t}`,this.hass.language)}
                        </option>
                      `)}
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.kc",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Hs("field_help.zone_kc",this.hass.language)}</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.05"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat((null!==(l=e.kc)&&void 0!==l?l:1).toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[xt]:s,[kt]:"custom"}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.state",this.hass.language)}</span
                  >
                  <select
                    class="settings-input"
                    .value="${va(e.state)}"
                    @change="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[pt]:i.target.value,[gt]:0}))}"
                  >
                    <option
                      value="${na.Automatic}"
                      ?selected="${e.state===na.Automatic}"
                    >
                      ${Hs("panels.zones.labels.states.automatic",this.hass.language)}
                    </option>
                    <option
                      value="${na.Manual}"
                      ?selected="${e.state===na.Manual}"
                    >
                      ${Hs("panels.zones.labels.states.manual",this.hass.language)}
                    </option>
                    <option
                      value="${na.Disabled}"
                      ?selected="${e.state===na.Disabled}"
                    >
                      ${Hs("panels.zones.labels.states.disabled",this.hass.language)}
                    </option>
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("common.labels.module",this.hass.language)}</span
                  >
                  <select
                    class="settings-input"
                    .value="${va(void 0!==e.module?String(e.module):"")}"
                    @change="${i=>{const s=i.target.value;this.handleEditZone(t,Object.assign(Object.assign({},e),{[mt]:s?parseInt(s):void 0}))}}"
                  >
                    ${this._renderModuleOptions(e.module)}
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.mapping",this.hass.language)}</span
                  >
                  <select
                    class="settings-input"
                    .value="${va(void 0!==e.mapping?String(e.mapping):"")}"
                    @change="${i=>{const s=i.target.value;this.handleEditZone(t,Object.assign(Object.assign({},e),{[_t]:s?parseInt(s):void 0}))}}"
                  >
                    ${this._renderMappingOptions(e.mapping)}
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.watering_mode",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Hs("panels.zones.labels.watering_mode_description",this.hass.language)}</span
                  >
                  <select
                    class="settings-input"
                    .value="${va(null!==(c=e.watering_mode)&&void 0!==c?c:"classic")}"
                    @change="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[At]:i.target.value}))}"
                  >
                    <option
                      value="classic"
                      ?selected="${"classic"===(null!==(d=e.watering_mode)&&void 0!==d?d:"classic")}"
                    >
                      ${Hs("panels.zones.labels.watering_modes.classic",this.hass.language)}
                    </option>
                    <option
                      value="service"
                      ?selected="${"service"===e.watering_mode}"
                    >
                      ${Hs("panels.zones.labels.watering_modes.service",this.hass.language)}
                    </option>
                  </select>
                </ha-settings-row>

                ${"service"===e.watering_mode?Z`
                      <ha-settings-row>
                        <span slot="heading"
                          >${Hs("panels.zones.labels.run_service",this.hass.language)}</span
                        >
                        <span slot="description"
                          >${Hs("panels.zones.labels.run_service_help",this.hass.language)}</span
                        >
                        <ha-entity-picker
                          .hass="${this.hass}"
                          .value="${e.run_service||""}"
                          .includeDomains="${["script"]}"
                          allow-custom-entity
                          @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Ct]:i.detail.value||null}))}"
                        ></ha-entity-picker>
                      </ha-settings-row>
                      <ha-settings-row>
                        <span slot="heading"
                          >${Hs("panels.zones.labels.duration_field",this.hass.language)}</span
                        >
                        <span slot="description"
                          >${Hs("panels.zones.labels.duration_field_help",this.hass.language)}</span
                        >
                        <input
                          type="text"
                          class="settings-input"
                          placeholder="${Hs("panels.zones.labels.duration_field_placeholder",this.hass.language)}"
                          .value="${e.duration_field||"duration"}"
                          @input="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Tt]:i.target.value||void 0}))}"
                        />
                      </ha-settings-row>
                      <ha-settings-row>
                        <span slot="heading"
                          >${Hs("panels.zones.labels.duration_unit",this.hass.language)}</span
                        >
                        <span slot="description"
                          >${Hs("panels.zones.labels.duration_unit_help",this.hass.language)}</span
                        >
                        <select
                          class="settings-input"
                          .value="${va(null!==(h=e.duration_unit)&&void 0!==h?h:"seconds")}"
                          @change="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Ot]:i.target.value}))}"
                        >
                          <option
                            value="seconds"
                            ?selected="${"seconds"===(null!==(u=e.duration_unit)&&void 0!==u?u:"seconds")}"
                          >
                            ${Hs("panels.zones.labels.duration_units.seconds",this.hass.language)}
                          </option>
                          <option
                            value="minutes"
                            ?selected="${"minutes"===e.duration_unit}"
                          >
                            ${Hs("panels.zones.labels.duration_units.minutes",this.hass.language)}
                          </option>
                        </select>
                      </ha-settings-row>
                      <ha-settings-row>
                        <span slot="heading"
                          >${Hs("panels.zones.labels.stop_service",this.hass.language)}</span
                        >
                        <span slot="description"
                          >${Hs("panels.zones.labels.stop_service_help",this.hass.language)}</span
                        >
                        <ha-entity-picker
                          .hass="${this.hass}"
                          .value="${e.stop_service||""}"
                          .includeDomains="${["script"]}"
                          allow-custom-entity
                          @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Ht]:i.detail.value||null}))}"
                        ></ha-entity-picker>
                      </ha-settings-row>
                      <ha-settings-row>
                        <span slot="heading"
                          >${Hs("panels.zones.labels.confirm_entity",this.hass.language)}</span
                        >
                        <span slot="description"
                          >${Hs("panels.zones.labels.confirm_entity_help",this.hass.language)}</span
                        >
                        <ha-entity-picker
                          .hass="${this.hass}"
                          .value="${e.confirm_entity||""}"
                          .includeDomains="${["valve","switch","input_boolean","number","binary_sensor"]}"
                          allow-custom-entity
                          @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Mt]:i.detail.value||null}))}"
                        ></ha-entity-picker>
                      </ha-settings-row>
                    `:""}
                ${"service"!==e.watering_mode?Z`
                      <ha-settings-row>
                        <span slot="heading"
                          >${Hs("panels.zones.labels.linked_entity",this.hass.language)}</span
                        >
                        <ha-entity-picker
                          .hass="${this.hass}"
                          .value="${e.linked_entity||""}"
                          .includeDomains="${["switch","valve","input_boolean"]}"
                          allow-custom-entity
                          @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[zt]:i.detail.value||null}))}"
                        ></ha-entity-picker>
                      </ha-settings-row>
                    `:""}

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.soil_moisture_sensor",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Hs("panels.zones.labels.soil_moisture_sensor_help",this.hass.language)}</span
                  >
                  <ha-entity-picker
                    .hass="${this.hass}"
                    .value="${e.soil_moisture_sensor||""}"
                    .includeDomains="${["sensor"]}"
                    .includeDeviceClasses="${["moisture"]}"
                    allow-custom-entity
                    @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Dt]:i.detail.value||null}))}"
                  ></ha-entity-picker>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.soil_moisture_threshold",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Hs("panels.zones.labels.soil_moisture_threshold_help",this.hass.language)}</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="1"
                    min="0"
                    max="100"
                    inputmode="decimal"
                    .value="${null!==(p=e.soil_moisture_threshold)&&void 0!==p?p:""}"
                    @input="${i=>{const s=i.target.value,a=""===s?null:Number(s);this.handleEditZone(t,Object.assign(Object.assign({},e),{[Lt]:null===a||isNaN(a)?null:a}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.flow_sensor",this.hass.language)}</span
                  >
                  <ha-entity-picker
                    .hass="${this.hass}"
                    .value="${e.flow_sensor||""}"
                    .includeDomains="${["sensor"]}"
                    allow-custom-entity
                    @value-changed="${i=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Et]:i.detail.value||null}))}"
                  ></ha-entity-picker>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.bucket",this.hass.language)}
                    (${Ls(this.config,vt)})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    inputmode="decimal"
                    .value="${parseFloat(Number(e.bucket).toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[vt]:s}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.maximum-bucket",this.hass.language)}
                    (${Ls(this.config,vt)})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat(Number(e.maximum_bucket).toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[wt]:s}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.multiplier",this.hass.language)}</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat(e.multiplier.toFixed(2))}"
                    @input="${i=>{const s=Math.round(100*i.target.valueAsNumber)/100;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[ft]:s}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.lead-time",this.hass.language)}
                    (${"s"})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="1"
                    min="0"
                    inputmode="numeric"
                    .value="${null!==(g=e.lead_time)&&void 0!==g?g:0}"
                    @input="${i=>{const s=i.target.valueAsNumber;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[bt]:Math.round(s)}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.maximum-duration",this.hass.language)}
                    (${"s"})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="1"
                    min="0"
                    inputmode="numeric"
                    .value="${null!==(m=e.maximum_duration)&&void 0!==m?m:""}"
                    @input="${i=>{const s=i.target.valueAsNumber;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[yt]:Math.round(s)}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Hs("panels.zones.labels.bucket_threshold",this.hass.language)}
                    (${Ls(this.config,vt)})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.5"
                    max="0"
                    inputmode="decimal"
                    .value="${parseFloat((null!==(v=e.bucket_threshold)&&void 0!==v?v:0).toFixed(1))}"
                    @input="${i=>{const s=Math.round(10*i.target.valueAsNumber)/10;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[St]:Math.min(s,0)}))}}"
                  />
                </ha-settings-row>

                ${e.state===na.Manual?Z`
                      <ha-settings-row>
                        <span slot="heading"
                          >${Hs("panels.zones.labels.duration",this.hass.language)}
                          (${"s"})</span
                        >
                        <input
                          type="number"
                          class="settings-input shortfield"
                          step="1"
                          min="0"
                          inputmode="numeric"
                          .value="${null!==(f=e.duration)&&void 0!==f?f:0}"
                          @input="${i=>{const s=i.target.valueAsNumber;isNaN(s)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[gt]:Math.round(s)}))}}"
                        />
                      </ha-settings-row>
                    `:""}

                <!-- Danger row -->
                <div class="settings-danger-row">
                  <button
                    class="action-btn"
                    @click="${()=>{this._pendingConfirm={title:Hs("panels.zones.confirm_action.reset_bucket_title",this.hass.language),body:Hs("panels.zones.confirm_action.reset_bucket_body",this.hass.language),confirmLabel:Hs("panels.zones.actions.reset-bucket",this.hass.language),onConfirm:()=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[vt]:0}))}}}"
                    ?disabled="${this.isSaving}"
                  >
                    ${Hs("panels.zones.actions.reset-bucket",this.hass.language)}
                  </button>
                  <button
                    class="action-btn danger-button"
                    @click="${()=>this.handleRemoveZone(void 0!==e.id?e.id:-1)}"
                    ?disabled="${this.isSaving||void 0===e.id}"
                  >
                    <ha-icon slot="icon" icon="mdi:delete"></ha-icon>
                    ${Hs("common.actions.delete",this.hass.language)}
                  </button>
                </div>
              </div>

              <!-- EXPLANATION EXPANSION -->
              ${e.explanation&&e.explanation.length>0?Z`
                    <ha-expansion-panel
                      .header="${Hs("panels.zones.actions.information",this.hass.language)}"
                    >
                      <div class="card-content">
                        ${ii(e.explanation)}
                      </div>
                    </ha-expansion-panel>
                  `:""}

              <!-- Run history + cumulative water usage (WS-2) -->
              ${this._renderRunHistory(e)}

              <!-- Weather records + the watering/seasonal calendar now live on the
             Weather & Location tab (climate is the same for every zone). -->
            `:""}
      </ha-card>
    `}_renderRunHistory(e){var t,i,s;if(!this.hass)return Z``;const a=(null===(t=this.config)||void 0===t?void 0:t.units)===Oe,n=null!==(i=e.run_log)&&void 0!==i?i:[],o=this.hass.language;return Z`
      <ha-expansion-panel
        .header="${Hs("panels.zones.history.title",o)}"
      >
        <div class="card-content">
          <div class="history-usage">
            <span class="history-usage-label"
              >${Hs("panels.zones.history.total_used",o)}</span
            >
            <span class="history-usage-value"
              >${xa(null!==(s=e.water_used_total)&&void 0!==s?s:0,a)}</span
            >
          </div>
          ${0===n.length?Z`<div class="weather-note">
                ${Hs("panels.zones.history.empty",o)}
              </div>`:Z`
                <table class="history-table">
                  <thead>
                    <tr>
                      <th>${Hs("panels.zones.history.when",o)}</th>
                      <th>${Hs("panels.zones.history.result",o)}</th>
                      <th class="num">
                        ${Hs("panels.zones.history.volume",o)}
                      </th>
                      <th>${Hs("panels.zones.history.detail",o)}</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${n.map(e=>this._renderRunLogRow(e,a))}
                  </tbody>
                </table>
              `}
        </div>
      </ha-expansion-panel>
    `}_renderRunLogRow(e,t){const i=this.hass.language,s=Hs(`panels.zones.history.results.${e.result}`,i);let a="";return e.detail&&(a="skipped"===e.result?e.detail.split(",").map(e=>Hs(`panels.zones.outlook.checks.${e}`,i)||e).join(", "):"failed"===e.result&&Hs(`panels.zones.fault.${e.detail}`,i)||e.detail),Z`
      <tr>
        <td>${ua(e.ts)}</td>
        <td>
          <span class="history-chip history-${e.result}"
            >${s||e.result}</span
          >
        </td>
        <td class="num">
          ${e.volume_l>0?xa(e.volume_l,t):"-"}
        </td>
        <td class="history-detail">${ii(a)}</td>
      </tr>
    `}render(){var e;if(!this.hass)return Z``;if(this.isLoading)return Z`
        <ha-card header="${Hs("panels.zones.title",this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Hs("common.loading-messages.general",this.hass.language)}
            </div>
          </div>
        </ha-card>
      `;const t=null!==this._confirmDeleteZoneId?this.zones.find(e=>e.id===this._confirmDeleteZoneId):null;return Z`
      <!-- Header: title + save chip + add zone -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${Hs("panels.zones.title",this.hass.language)}
          </div>
          ${this._renderSaveStatus()}
          <ha-icon-button
            .path="${js}"
            title="${Hs("panels.zones.cards.add-zone.header",this.hass.language)}"
            @click="${()=>{this._showAddZone=!0}}"
          ></ha-icon-button>
        </div>
        ${0===this.zones.length?Z`<div class="card-content">
              <div class="weather-note">
                ${Hs("panels.zones.no_items",this.hass.language)}
              </div>
            </div>`:""}
      </ha-card>

      <!-- Add Zone dialog -->
      <ha-dialog
        .open="${this._showAddZone}"
        @closed="${()=>{this._showAddZone=!1}}"
        heading="${Hs("panels.zones.cards.add-zone.header",this.hass.language)}"
      >
        <div class="add-zone-form">
          <si-zone-form
            .hass="${this.hass}"
            .metric="${(null===(e=this.config)||void 0===e?void 0:e.units)===Oe}"
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
            ${Hs("common.actions.cancel",this.hass.language)}
          </button>
          <button
            class="dialog-btn dialog-btn-primary"
            @click="${this.handleAddZone}"
            ?disabled="${!this._newZoneName.trim()||this.isSaving}"
          >
            ${this.isSaving?Hs("common.saving-messages.adding",this.hass.language):Hs("panels.zones.cards.add-zone.actions.add",this.hass.language)}
          </button>
        </div>
      </ha-dialog>

      <!-- Delete confirmation dialog -->
      ${t?Z`
            <ha-dialog
              open
              @closed="${()=>{this._confirmDeleteZoneId=null}}"
              heading="${Hs("common.actions.confirm_delete",this.hass.language)}"
            >
              <p>
                ${Hs("common.actions.confirm_delete_zone",this.hass.language)}
              </p>
              <p><strong>${t.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmDeleteZoneId=null}}"
                >
                  ${Hs("common.actions.cancel",this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-danger"
                  @click="${this._confirmDelete}"
                >
                  ${Hs("common.actions.delete",this.hass.language)}
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Generic destructive-action confirmation dialog -->
      ${this._pendingConfirm?Z`
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
                  ${Hs("common.actions.cancel",this.hass.language)}
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
            ${Hs("common.labels.bulk_actions",this.hass.language)}
          </div>
        </div>
        <div class="card-content bulk-actions">
          <button
            class="action-btn danger-button"
            @click="${()=>{this._pendingConfirm={title:Hs("panels.zones.confirm_action.reset_all_buckets_title",this.hass.language),body:Hs("panels.zones.confirm_action.reset_all_buckets_body",this.hass.language),confirmLabel:Hs("panels.zones.cards.zone-actions.actions.reset-all-buckets",this.hass.language),onConfirm:()=>this.handleResetAllBuckets()}}}"
            ?disabled="${this.isSaving}"
          >
            ${Hs("panels.zones.cards.zone-actions.actions.reset-all-buckets",this.hass.language)}
          </button>
          <button
            class="action-btn danger-button"
            @click="${()=>{this._pendingConfirm={title:Hs("panels.zones.confirm_action.clear_weather_title",this.hass.language),body:Hs("panels.zones.confirm_action.clear_weather_body",this.hass.language),confirmLabel:Hs("panels.zones.cards.zone-actions.actions.clear-all-weatherdata",this.hass.language),onConfirm:()=>this.handleClearAllWeatherdata()}}}"
            ?disabled="${this.isSaving}"
          >
            ${Hs("panels.zones.cards.zone-actions.actions.clear-all-weatherdata",this.hass.language)}
          </button>
        </div>
      </ha-card>
    `}disconnectedCallback(){super.disconnectedCallback(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null),this._savedResetTimer&&(clearTimeout(this._savedResetTimer),this._savedResetTimer=null)}static get styles(){return r`
      ${la}

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
    `}};t([pe()],za.prototype,"config",void 0),t([pe({attribute:!1})],za.prototype,"path",void 0),t([pe({type:Array})],za.prototype,"zones",void 0),t([pe({type:Array})],za.prototype,"modules",void 0),t([pe({type:Array})],za.prototype,"mappings",void 0),t([pe({type:Boolean})],za.prototype,"isLoading",void 0),t([ge()],za.prototype,"_expanded",void 0),t([pe({type:Boolean})],za.prototype,"isSaving",void 0),t([pe({type:Boolean})],za.prototype,"_showAddZone",void 0),t([ge()],za.prototype,"_pendingConfirm",void 0),t([ge()],za.prototype,"_saveStatus",void 0),t([pe()],za.prototype,"_confirmDeleteZoneId",void 0),t([pe()],za.prototype,"_newZoneName",void 0),t([pe()],za.prototype,"_newZoneSize",void 0),t([pe()],za.prototype,"_newZoneThroughput",void 0),t([pe()],za.prototype,"_newZoneEntity",void 0),za=t([de("smart-irrigation-view-zone-settings")],za);let Sa=class extends(sa(le)){constructor(){super(...arguments),this.zones=[],this.modules=[],this.allmodules=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._updateScheduled=!1,this.globalDebounceTimer=null,this.moduleCache=new Map,this.debouncedSave=(()=>{let e=null;return t=>{e&&clearTimeout(e),e=window.setTimeout(()=>{this.saveToHA(t),e=null},500)}})()}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}firstUpdated(){_e().catch(e=>{console.error("Failed to load HA form:",e)})}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:ye+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;e&&(this.isLoading=!0,this._scheduleUpdate());try{const[e,t,i,s]=await Promise.all([Fs(this.hass),Ws(this.hass),Gs(this.hass),Ks(this.hass)]);this.config=e,this.zones=t,this.modules=i,this.allmodules=s,this._initialLoadDone=!0,this.moduleCache.clear()}catch(e){console.error("Error fetching data:",e),Rs(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}async handleAddModule(){var e,t;if((null===(t=null===(e=this.moduleInput)||void 0===e?void 0:e.selectedOptions)||void 0===t?void 0:t[0])&&!this.isSaving){this.isSaving=!0,this._scheduleUpdate();try{const e=this.moduleInput.selectedOptions[0].text,t=this.allmodules.find(t=>t.name===e);if(!t)return;const i={name:e,description:t.description,config:t.config,schema:t.schema};this.modules=[...this.modules,i],this.moduleCache.clear(),this._scheduleUpdate(),await this.saveToHA(i),await this._fetchData()}catch(e){console.error("Error adding module:",e),await this._fetchData()}finally{this.isSaving=!1,this._scheduleUpdate()}}}async handleRemoveModule(e,t){if(!this.isSaving){this.isSaving=!0,this._scheduleUpdate();try{const e=this.modules[t],a=null==e?void 0:e.id;this.modules;this.modules=this.modules.filter((e,i)=>i!==t),this.moduleCache.clear(),this._scheduleUpdate(),this.hass&&void 0!==a&&await(i=this.hass,s=a.toString(),i.callApi("POST",ye+"/modules",{id:s,remove:!0}))}catch(e){console.error("Error removing module:",e),Rs(this,this.hass,"common.errors.delete_failed",e),await this._fetchData()}finally{this.isSaving=!1,this._scheduleUpdate()}var i,s}}async saveToHA(e){if(this.hass)try{await Vs(this.hass,e)}catch(e){throw console.error("Error saving module:",e),Rs(this,this.hass,"common.errors.save_failed",e),e}}renderModule(e,t){if(!this.hass)return Z``;const i=this.zones.filter(t=>t.module===e.id).length,s=`module-${e.id||t}-${i}-${JSON.stringify(e)}`;if(this.moduleCache.has(s))return this.moduleCache.get(s);const a=Z`
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          ${this.renderUsageChip(i)}
        </div>
        <div class="card-content">
          <div class="item-description">${e.description}</div>
          <div class="moduleconfig">
            <label class="subheader"
              >${Hs("panels.modules.cards.module.labels.configuration",this.hass.language)}
              (*
              ${Hs("panels.modules.cards.module.labels.required",this.hass.language)})</label
            >
            ${e.schema?Object.entries(e.schema).map(([e])=>this.renderConfig(t,e)):null}
          </div>
          <div class="card-footer">
            ${i?Z`<div class="weather-note">
                  ${Hs("panels.modules.cards.module.errors.cannot-delete-module-because-zones-use-it",this.hass.language)}
                </div>`:Z`<button
                  class="action-btn danger"
                  @click="${e=>this.handleRemoveModule(e,t)}"
                >
                  <ha-icon icon="mdi:delete"></ha-icon>
                  ${Hs("common.actions.delete",this.hass.language)}
                </button>`}
          </div>
        </div>
      </ha-card>
    `;return this.moduleCache.set(s,a),a}renderUsageChip(e){return this.hass?e?Z`<span class="usage-chip"
          >${Hs("panels.setup.advanced.used_by_zones",this.hass.language,"{count}",e)}</span
        >`:Z`<span class="usage-chip unused"
          >${Hs("panels.setup.advanced.not_used",this.hass.language)}</span
        >`:Z``}renderConfig(e,t){var i,s;const a=Object.values(this.modules).at(e);if(!a||!this.hass)return;const n=a.schema[t],o=n.name,r=e=>{try{const t=Hs(e,this.hass.language);return null==t?void 0:t}catch(e){return}},l="panels.modules.cards.module.fields."+o,c=null!==(i=r(l+".name"))&&void 0!==i?i:function(e){if(e)return(e=e.replace("_"," ")).charAt(0).toUpperCase()+e.slice(1)}(o),d=null!==(s=r(l+".description"))&&void 0!==s?s:n.description;let h="";null==a.config&&(a.config=[]),o in a.config&&(h=a.config[o]);let u=Z``;if("boolean"==n.type)u=Z`<input
        type="checkbox"
        id="${o+e}"
        .checked=${h}
        @input="${t=>this.handleEditConfig(e,Object.assign(Object.assign({},a),{config:Object.assign(Object.assign({},a.config),{[o]:t.target.checked})}))}"
      />`;else if("float"==n.type||"integer"==n.type)u=Z`<input
        type="number"
        class="settings-input shortfield"
        id="${n.name+e}"
        .value="${a.config[n.name]}"
        @input="${t=>this.handleEditConfig(e,Object.assign(Object.assign({},a),{config:Object.assign(Object.assign({},a.config),{[o]:t.target.value})}))}"
      />`;else if("string"==n.type)u=Z`<input
        type="text"
        class="settings-input"
        id="${o+e}"
        .value="${h}"
        @input="${t=>this.handleEditConfig(e,Object.assign(Object.assign({},a),{config:Object.assign(Object.assign({},a.config),{[o]:t.target.value})}))}"
      />`;else if("select"==n.type){const t=this.hass.language;u=Z`<select
        class="settings-input"
        id="${o+e}"
        .value="${va(h)}"
        @change="${t=>this.handleEditConfig(e,Object.assign(Object.assign({},a),{config:Object.assign(Object.assign({},a.config),{[o]:t.target.value})}))}"
      >
        ${Object.entries(n.options).map(([e,i])=>Z`<option
              value="${Ds(i,0)}"
              ?selected="${h===Ds(i,0)}"
            >
              ${Hs("panels.modules.cards.module.translated-options."+Ds(i,1),t)}
            </option>`)}
      </select>`}return Z`<ha-settings-row>
      <span slot="heading"
        >${c}${n.required?" *":""}</span
      >
      ${d?Z`<span slot="description">${d}</span>`:""}
      ${u}
    </ha-settings-row>`}handleEditConfig(e,t){this.modules=Object.values(this.modules).map((i,s)=>s===e?t:i),this.moduleCache.clear(),this._scheduleUpdate(),this.debouncedSave(t)}render(){return this.hass?Z`
      <ha-card header="${Hs("panels.modules.title",this.hass.language)}">
        <div class="card-content">
          ${Hs("panels.modules.description",this.hass.language)}
          ${this.isLoading?Z`<div class="loading-indicator">
                ${Hs("common.loading-messages.general",this.hass.language)}
              </div>`:Z`
                <div class="add-row">
                  <select
                    id="moduleInput"
                    class="settings-input"
                    aria-label="${Hs("common.labels.module",this.hass.language)}"
                    ?disabled="${this.isSaving}"
                  >
                    ${Object.entries(this.allmodules).map(([e,t])=>Z`<option value="${t.id}">
                          ${t.name}
                        </option>`)}
                  </select>
                  <button
                    @click="${this.handleAddModule}"
                    ?disabled="${this.isSaving}"
                    class="action-btn ${this.isSaving?"saving":""}"
                  >
                    <ha-icon icon="mdi:plus"></ha-icon>
                    ${this.isSaving?Hs("common.saving-messages.adding",this.hass.language):Hs("panels.modules.cards.add-module.actions.add",this.hass.language)}
                  </button>
                </div>
              `}
        </div>
      </ha-card>

      ${this.isLoading?Z``:Object.entries(this.modules).map(([e,t])=>this.renderModule(t,parseInt(e)))}
    `:Z``}disconnectedCallback(){super.disconnectedCallback(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null),this.moduleCache.clear()}static get styles(){return r`
      ${la}

      .field-hint {
        font-size: 0.8rem;
        color: var(--secondary-text-color);
        line-height: 1.4;
        margin-top: 3px;
        padding-left: 2px;
      }
    `}};t([pe()],Sa.prototype,"config",void 0),t([pe({type:Array})],Sa.prototype,"zones",void 0),t([pe({type:Array})],Sa.prototype,"modules",void 0),t([pe({type:Array})],Sa.prototype,"allmodules",void 0),t([pe({type:Boolean})],Sa.prototype,"isLoading",void 0),t([pe({type:Boolean})],Sa.prototype,"isSaving",void 0),t([me("#moduleInput")],Sa.prototype,"moduleInput",void 0),Sa=t([de("smart-irrigation-view-modules")],Sa);let Ea=class extends(sa(le)){constructor(){super(...arguments),this.zones=[],this.mappings=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this.debounceTimers=new Map,this.globalDebounceTimer=null,this.mappingCache=new Map,this._updateScheduled=!1,this._lastUpdateTime=0,this._updateThrottleDelay=16}_scheduleUpdate(){if(this._updateScheduled)return;const e=performance.now()-this._lastUpdateTime;e<this._updateThrottleDelay?setTimeout(()=>{this._updateScheduled=!1,this._lastUpdateTime=performance.now(),this.requestUpdate()},this._updateThrottleDelay-e):(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this._lastUpdateTime=performance.now(),this.requestUpdate()}))}firstUpdated(){_e().catch(e=>{console.error("Failed to load HA form:",e)})}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:ye+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[t,i,s]=await Promise.all([Fs(this.hass),Ws(this.hass),Ys(this.hass)]);this.config=t,this.zones=i,this.mappings=s,this._initialLoadDone=!0,this.mappingCache.clear()}catch(e){console.error("Error fetching data:",e),Rs(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}handleAddMapping(){if(!this.mappingNameInput.value.trim())return;const e={[He]:"",[Me]:"",[De]:"",[Le]:"",[Ne]:"",[Ie]:"",[Pe]:"",[Be]:"",[Re]:""},t={name:this.mappingNameInput.value.trim(),mappings:e};this.mappings=[...this.mappings,t],this.isSaving=!0,this.saveToHA(t).then(()=>(this.mappingNameInput.value="",this._fetchData())).catch(e=>{console.error("Failed to add mapping:",e),Rs(this,this.hass,"common.errors.save_failed",e),this.mappings=this.mappings.slice(0,-1)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()})}handleRemoveMapping(e,t){const i=this.mappings[t].id;if(null==i)return;const s=[...this.mappings];var a,n;(this.mappings=this.mappings.filter((e,i)=>i!==t),this.mappingCache.delete(i.toString()),this.hass)&&(this.isSaving=!0,(a=this.hass,n=i.toString(),a.callApi("POST",ye+"/mappings",{id:n,remove:!0})).catch(e=>{console.error("Failed to delete mapping:",e),Rs(this,this.hass,"common.errors.delete_failed",e),this.mappings=s,this._fetchData().catch(e=>{console.error("Failed to refresh data after delete error:",e)})}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}))}handleEditMapping(e,t){this.mappings[e]=t,t.id&&this.mappingCache.delete(t.id.toString()),this.globalDebounceTimer&&clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=window.setTimeout(()=>{this.isSaving=!0,this.saveToHA(t).catch(e=>{console.error("Failed to save mapping:",e),Rs(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}),this.globalDebounceTimer=null},500),this._scheduleUpdate()}async saveToHA(e){var t;if(!this.hass)throw new Error("Home Assistant connection not available");const i=[],s=this.hass.states;for(const t in e.mappings){const a=e.mappings[t].sensorentity;if(a&&""!==a.trim()){const n=a.trim();e.mappings[t].sensorentity=n,n in s||i.push(n)}}if(i.length>0){const e=null===(t=this.shadowRoot)||void 0===t?void 0:t.querySelector("ha-card");throw e&&Ns({body:{message:Hs("panels.mappings.cards.mapping.errors.source_does_not_exist",this.hass.language)+": "+i.join(", ")},error:Hs("panels.mappings.cards.mapping.errors.invalid_source",this.hass.language)},e),new Error("Invalid sensor entities found")}const{id:a,name:n,mappings:o}=e;await Xs(this.hass,{id:a,name:n,mappings:o})}renderMappingSetting(e,t){const i=this.mappings[e];if(!i||!this.hass)return Z``;const s=i.mappings[t];return Z`
      <div class="mappingline">
        <div class="mappingsettingname">
          <label for="${`${t}_${e}`}">
            ${Hs(`panels.mappings.cards.mapping.items.${t.toLowerCase()}`,this.hass.language)}
          </label>
        </div>
        <div class="mappingsettingline">
          <label
            >${Hs("panels.mappings.cards.mapping.source",this.hass.language)}:</label
          >
          <div class="radio-group">
            ${this.renderSimpleRadioOptions(e,t,s)}
          </div>
        </div>
        ${this.renderMappingInputs(e,t,s)}
      </div>
    `}renderSimpleRadioOptions(e,t,i){if(!this.hass||!this.config)return Z``;const s=t===Me||t===Pe,a=i[Ke];return Z`
      ${!s&&this.config.use_weather_service?Z`
            <label>
              <input
                type="radio"
                name="${t}_${e}_source"
                value="${Ue}"
                ?checked="${a===Ue}"
                @change="${i=>this.handleSimpleSourceChange(e,t,i)}"
              />
              ${Hs("panels.mappings.cards.mapping.sources.weather_service",this.hass.language)}
            </label>
          `:""}
      ${s?Z`
            <label>
              <input
                type="radio"
                name="${t}_${e}_source"
                value="${Ge}"
                ?checked="${a===Ge}"
                @change="${i=>this.handleSimpleSourceChange(e,t,i)}"
              />
              ${Hs("panels.mappings.cards.mapping.sources.none",this.hass.language)}
            </label>
          `:""}

      <label>
        <input
          type="radio"
          name="${t}_${e}_source"
          value="${je}"
          ?checked="${a===je}"
          @change="${i=>this.handleSimpleSourceChange(e,t,i)}"
        />
        ${Hs("panels.mappings.cards.mapping.sources.sensor",this.hass.language)}
      </label>

      <label>
        <input
          type="radio"
          name="${t}_${e}_source"
          value="${Fe}"
          ?checked="${a===Fe}"
          @change="${i=>this.handleSimpleSourceChange(e,t,i)}"
        />
        ${Hs("panels.mappings.cards.mapping.sources.static",this.hass.language)}
      </label>
    `}handleSimpleSourceChange(e,t,i){const s=this.mappings[e],a=i.target.value;this.handleEditMapping(e,Object.assign(Object.assign({},s),{mappings:Object.assign(Object.assign({},s.mappings),{[t]:Object.assign(Object.assign({},s.mappings[t]),{[Ke]:a,[Ve]:""})})}))}handleSimpleInputChange(e,t,i,s){const a=this.mappings[e],n=s.target.value;this.handleEditMapping(e,Object.assign(Object.assign({},a),{mappings:Object.assign(Object.assign({},a.mappings),{[t]:Object.assign(Object.assign({},a.mappings[t]),{[i]:n})})}))}renderMappingInputs(e,t,i){if(!this.hass)return Z``;const s=i[Ke];return Z`
      ${s===je?this.renderSensorInput(e,t,i):""}
      ${s===Fe?this.renderStaticValueInput(e,t,i):""}
      ${s===je||s===Fe?this.renderUnitSelect(e,t,i):""}
      ${t!==Ie||s!==je&&s!==Fe?"":this.renderPressureTypeSelect(e,t,i)}
      ${s===je?this.renderAggregateSelect(e,t,i):""}
    `}renderSensorInput(e,t,i){if(!this.hass)return Z``;const s=`${t}_${e}`;return Z`
      <div class="mappingsettingline">
        <label for="${s}_sensor_entity">
          ${Hs("panels.mappings.cards.mapping.sensor-entity",this.hass.language)}:
        </label>
        <input
          type="text"
          class="settings-input"
          id="${s}_sensor_entity"
          .value="${i[Ve]||""}"
          @change="${i=>this.handleSensorChange(e,t,i)}"
        />
      </div>
    `}renderStaticValueInput(e,t,i){if(!this.hass)return Z``;const s=`${t}_${e}`;return Z`
      <div class="mappingsettingline">
        <label for="${s}_static_value">
          ${Hs("panels.mappings.cards.mapping.static_value",this.hass.language)}:
        </label>
        <input
          type="text"
          class="settings-input"
          id="${s}_static_value"
          .value="${i[Ye]||""}"
          @input="${i=>this.handleStaticValueChange(e,t,i)}"
        />
      </div>
    `}renderUnitSelect(e,t,i){if(!this.hass||!this.config)return Z``;const s=`${t}_${e}`;return Z`
      <div class="mappingsettingline">
        <label for="${s}_unit">
          ${Hs("panels.mappings.cards.mapping.input-units",this.hass.language)}:
        </label>
        <select
          id="${s}_unit"
          class="settings-input"
          @change="${i=>this.handleUnitChange(e,t,i)}"
        >
          ${this.renderUnitOptionsForMapping(t,i)}
        </select>
      </div>
    `}renderPressureTypeSelect(e,t,i){if(!this.hass)return Z``;const s=`${t}_${e}`;return Z`
      <div class="mappingsettingline">
        <label for="${s}_pressure_type">
          ${Hs("panels.mappings.cards.mapping.pressure-type",this.hass.language)}:
        </label>
        <select
          id="${s}_pressure_type"
          class="settings-input"
          @change="${i=>this.handlePressureTypeChange(e,t,i)}"
        >
          ${this.renderPressureTypes(t,i)}
        </select>
      </div>
    `}renderAggregateSelect(e,t,i){if(!this.hass)return Z``;const s=`${t}_${e}`;return Z`
      <div class="mappingsettingline">
        <label for="${s}_aggregate">
          ${Hs("panels.mappings.cards.mapping.sensor-aggregate-use-the",this.hass.language)}
        </label>
        <select
          id="${s}_aggregate"
          class="settings-input"
          @change="${i=>this.handleAggregateChange(e,t,i)}"
        >
          ${this.renderAggregateOptionsForMapping(t,i)}
        </select>
        <label for="${s}_aggregate">
          ${Hs("panels.mappings.cards.mapping.sensor-aggregate-of-sensor-values-to-calculate",this.hass.language)}
        </label>
      </div>
    `}handleSensorChange(e,t,i){const s=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},s),{mappings:Object.assign(Object.assign({},s.mappings),{[t]:Object.assign(Object.assign({},s.mappings[t]),{[Ve]:i.target.value})})}))}handleStaticValueChange(e,t,i){const s=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},s),{mappings:Object.assign(Object.assign({},s.mappings),{[t]:Object.assign(Object.assign({},s.mappings[t]),{[Ye]:i.target.value})})}))}handleUnitChange(e,t,i){const s=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},s),{mappings:Object.assign(Object.assign({},s.mappings),{[t]:Object.assign(Object.assign({},s.mappings[t]),{[Xe]:i.target.value})})}))}handlePressureTypeChange(e,t,i){const s=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},s),{mappings:Object.assign(Object.assign({},s.mappings),{[t]:Object.assign(Object.assign({},s.mappings[t]),{[Ze]:i.target.value})})}))}handleAggregateChange(e,t,i){const s=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},s),{mappings:Object.assign(Object.assign({},s.mappings),{[t]:Object.assign(Object.assign({},s.mappings[t]),{[Je]:i.target.value})})}))}renderAggregateOptionsForMapping(e,t){if(!this.hass||!this.config)return Z``;let i="average";return e===Le&&(i="delta"),e===Ne&&(i="average"),t[Je]&&(i=t[Je]),Z`
      ${Qe.map(e=>this.renderAggregateOption(e,i))}
    `}renderAggregateOption(e,t){if(this.hass&&this.config){return Z`<option value="${e}" ?selected="${e===t}">
        ${Hs("panels.mappings.cards.mapping.aggregates."+e,this.hass.language)}
      </option>`}return Z``}renderPressureTypes(e,t){if(this.hass&&this.config){let e=Z``;const i=t[Ze];return e=Z`${e}
        <option
          value="${We}"
          ?selected="${i===We}"
        >
          ${Hs("panels.mappings.cards.mapping.pressure_types."+We,this.hass.language)}
        </option>
        <option
          value="${qe}"
          ?selected="${i===qe}"
        >
          ${Hs("panels.mappings.cards.mapping.pressure_types."+qe,this.hass.language)}
        </option>`,e}return Z``}renderUnitOptionsForMapping(e,t){if(!this.hass||!this.config)return Z``;const i=function(e){switch(e){case He:case Be:return[{unit:"°C",system:Oe},{unit:"°F",system:Te}];case Le:case Me:return[{unit:st,system:Oe},{unit:at,system:Te}];case Ne:return[{unit:lt,system:Oe},{unit:ct,system:Te}];case De:return[{unit:"%",system:[Oe,Te]}];case Ie:return[{unit:"millibar",system:Oe},{unit:"hPa",system:Oe},{unit:"psi",system:Te},{unit:nt,system:Te}];case Re:return[{unit:"km/h",system:Oe},{unit:rt,system:Oe},{unit:ot,system:Te}];case Pe:return[{unit:"W/m2",system:Oe},{unit:"MJ/day/m2",system:Oe},{unit:"W/sq ft",system:Te},{unit:"MJ/day/sq ft",system:Te}];default:return[]}}(e);let s=t[Xe];const a=this.config.units;if(!t[Xe])for(const e of i)if("string"==typeof e.system){if(a===e.system){s=e.unit;break}}else{for(const t of e.system)if(a===t.system){s=e.unit;break}if(s===e.unit)break}return Z`
      ${i.map(e=>Z`
          <option value="${e.unit}" ?selected="${s===e.unit}">
            ${e.unit}
          </option>
        `)}
    `}render(){return this.hass?this.isLoading?Z`
        <ha-card
          header="${Hs("panels.mappings.title",this.hass.language)}"
        >
          <div class="card-content">
            <div class="loading-indicator">
              ${Hs("common.loading-messages.general",this.hass.language)}
            </div>
          </div>
        </ha-card>
      `:Z`
      <ha-card
        header="${Hs("panels.mappings.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Hs("panels.mappings.description",this.hass.language)}
          <div class="add-row">
            <input
              id="mappingNameInput"
              class="settings-input"
              type="text"
              placeholder="${Hs("panels.mappings.labels.mapping-name",this.hass.language)}"
            />
            <button
              class="action-btn ${this.isSaving?"saving":""}"
              ?disabled="${this.isSaving}"
              @click="${this.handleAddMapping}"
            >
              <ha-icon icon="mdi:plus"></ha-icon>
              ${Hs("panels.mappings.cards.add-mapping.actions.add",this.hass.language)}
            </button>
          </div>
        </div>
      </ha-card>

      ${this.renderMappingsList()}
    `:Z``}renderUsageChip(e){return this.hass?e?Z`<span class="usage-chip"
          >${Hs("panels.setup.advanced.used_by_zones",this.hass.language,"{count}",e)}</span
        >`:Z`<span class="usage-chip unused"
          >${Hs("panels.setup.advanced.not_used",this.hass.language)}</span
        >`:Z``}renderMappingsList(){const e=this.mappings.slice(0,Math.min(this.mappings.length,10)),t=this.mappings.slice(10);return Z`
      ${e.map((e,t)=>this.renderMappingCard(e,t))}
      ${t.length>0?Z`
            <div class="load-more">
              <button @click="${this.loadMoreMappings}">
                Load ${t.length} more mappings...
              </button>
            </div>
          `:""}
    `}renderMappingCard(e,t){if(!this.hass)return Z``;const i=this.zones.filter(t=>t.mapping===e.id).length;return Z`
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          ${this.renderUsageChip(i)}
        </div>
        <div class="card-content">
          <ha-settings-row>
            <span slot="heading"
              >${Hs("panels.mappings.labels.mapping-name",this.hass.language)}</span
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
            ${i?Z`<div class="weather-note">
                  ${Hs("panels.mappings.cards.mapping.errors.cannot-delete-mapping-because-zones-use-it",this.hass.language)}
                </div>`:Z`<button
                  class="action-btn danger"
                  @click="${e=>this.handleRemoveMapping(e,t)}"
                >
                  <ha-icon icon="mdi:delete"></ha-icon>
                  ${Hs("common.actions.delete",this.hass.language)}
                </button>`}
          </div>
        </div>
      </ha-card>
    `}renderMappingSettings(e,t){const i=Object.entries(e.mappings);return Z`
      ${i.map(([e])=>this.renderMappingSetting(t,e))}
    `}loadMoreMappings(){this._scheduleUpdate()}static get styles(){return r`
      ${la}

      /* Parameter section header inside a sensor-group card */
      .mappingsettingname {
        font-weight: 500;
        font-size: 0.95rem;
        color: var(--primary-text-color);
        padding-bottom: 6px;
        margin-bottom: 4px;
        border-bottom: 1px solid var(--divider-color);
      }
    `}disconnectedCallback(){super.disconnectedCallback(),this.debounceTimers.forEach(e=>{clearTimeout(e)}),this.debounceTimers.clear(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null),this.mappingCache.clear()}};t([pe()],Ea.prototype,"config",void 0),t([pe({type:Array})],Ea.prototype,"zones",void 0),t([pe({type:Array})],Ea.prototype,"mappings",void 0),t([pe({type:Boolean})],Ea.prototype,"isLoading",void 0),t([pe({type:Boolean})],Ea.prototype,"isSaving",void 0),t([me("#mappingNameInput")],Ea.prototype,"mappingNameInput",void 0),Ea=t([de("smart-irrigation-view-mappings")],Ea);const Aa=["monday","tuesday","wednesday","thursday","friday","saturday","sunday"];let Ca=class extends(sa(le)){constructor(){super(...arguments),this._schedules=[],this._zones=[],this._isLoading=!0,this._showDialog=!1,this._editingSchedule={name:"",type:"daily",enabled:!0,time:"06:00",action:"irrigate",zones:"all"},this._editingId=null}hassSubscribe(){return this._load(),[this.hass.connection.subscribeMessage(()=>this._load(),{type:ye+"_config_updated"})]}async _load(){var e;if(this.hass)try{const[t,i]=await Promise.all([(e=this.hass,e.callWS({type:ye+"/schedules"})),Ws(this.hass)]);this._schedules=t||[],this._zones=i||[]}catch(e){console.error("Failed to load schedules",e),Rs(this,this.hass,"common.errors.load_failed",e)}finally{this._isLoading=!1}}_openAdd(){this._editingSchedule={name:"",type:"daily",enabled:!0,time:"06:00",action:"irrigate",zones:"all"},this._editingId=null,this._showDialog=!0}_openEdit(e){var t;this._editingSchedule=Object.assign({},e),this._editingId=null!==(t=e.id)&&void 0!==t?t:null,this._showDialog=!0}_closeDialog(){this._showDialog=!1}async _save(){const e=Object.assign({},this._editingSchedule);this._editingId&&(e.id=this._editingId);try{await Qs(this.hass,e),this._closeDialog(),await this._load()}catch(e){console.error("Failed to save schedule",e),Rs(this,this.hass,"common.errors.save_failed",e)}}async _delete(e){try{await(t=this.hass,i=e,t.callWS({type:ye+"/schedule_delete",schedule_id:i})),await this._load()}catch(e){console.error("Failed to delete schedule",e),Rs(this,this.hass,"common.errors.delete_failed",e)}var t,i}_update(e){this._editingSchedule=Object.assign(Object.assign({},this._editingSchedule),e)}_typeLabel(e){return Hs(`panels.schedules.types.${e}`,this.hass.language)||e}_zonesLabel(e){if("all"===e)return Hs("panels.schedules.zones_all",this.hass.language);if(Array.isArray(e)){const t=e.map(e=>{const t=this._zones.find(t=>String(t.id)===String(e));return t?t.name:e}).join(", ");return t||e.join(", ")}return String(e)}_renderZonePicker(){const e="all"===this._editingSchedule.zones||!Array.isArray(this._editingSchedule.zones),t=e?[]:this._editingSchedule.zones.map(String);return Z`
      <div class="field">
        <label
          >${Hs("panels.schedules.fields.zones",this.hass.language)}</label
        >
        <div class="switch-container">
          <input
            type="radio"
            id="zones_all"
            name="zones_mode"
            ?checked="${e}"
            @change=${()=>this._update({zones:"all"})}
          />
          <label for="zones_all"
            >${Hs("panels.schedules.zones_all",this.hass.language)}</label
          >
          <input
            type="radio"
            id="zones_specific"
            name="zones_mode"
            ?checked="${!e}"
            @change=${()=>this._update({zones:[]})}
          />
          <label for="zones_specific"
            >${Hs("panels.schedules.zones_specific",this.hass.language)}</label
          >
        </div>
        ${e?"":Z`
              <div class="zone-checkboxes">
                ${this._zones.map(e=>Z`
                    <label class="zone-check">
                      <input
                        type="checkbox"
                        ?checked="${t.includes(String(e.id))}"
                        @change=${t=>{const i=t.target.checked,s=String(e.id),a=Array.isArray(this._editingSchedule.zones)?[...this._editingSchedule.zones]:[],n=i?[...a,s]:a.filter(e=>e!==s);this._update({zones:n})}}
                      />
                      ${e.name}
                    </label>
                  `)}
              </div>
            `}
      </div>
    `}_renderTypeFields(){var e;const t=this._editingSchedule;switch(t.type){case"daily":return Z`
          <div class="field">
            <label
              >${Hs("panels.schedules.fields.time",this.hass.language)}</label
            >
            <input
              type="time"
              .value="${t.time||"06:00"}"
              @change=${e=>this._update({time:e.target.value})}
            />
          </div>
        `;case"weekly":return Z`
          <div class="field">
            <label
              >${Hs("panels.schedules.fields.time",this.hass.language)}</label
            >
            <input
              type="time"
              .value="${t.time||"06:00"}"
              @change=${e=>this._update({time:e.target.value})}
            />
          </div>
          <div class="field">
            <label
              >${Hs("panels.schedules.fields.days_of_week",this.hass.language)}</label
            >
            <div class="day-checkboxes">
              ${Aa.map(e=>Z`
                  <label class="day-check">
                    <input
                      type="checkbox"
                      ?checked="${(t.days_of_week||[]).includes(e)}"
                      @change=${i=>{const s=i.target.checked,a=t.days_of_week||[],n=s?[...a,e]:a.filter(t=>t!==e);this._update({days_of_week:n})}}
                    />
                    ${Hs(`panels.schedules.days.${e}`,this.hass.language)}
                  </label>
                `)}
            </div>
          </div>
        `;case"monthly":return Z`
          <div class="field">
            <label
              >${Hs("panels.schedules.fields.time",this.hass.language)}</label
            >
            <input
              type="time"
              .value="${t.time||"06:00"}"
              @change=${e=>this._update({time:e.target.value})}
            />
          </div>
          <div class="field">
            <label
              >${Hs("panels.schedules.fields.day_of_month",this.hass.language)}</label
            >
            <input
              type="number"
              min="1"
              max="31"
              .value="${String(t.day_of_month||1)}"
              @input=${e=>this._update({day_of_month:parseInt(e.target.value)})}
            />
          </div>
        `;case"interval":return Z`
          <div class="field">
            <label
              >${Hs("panels.schedules.fields.interval_hours",this.hass.language)}</label
            >
            <div class="input-suffix-row">
              <input
                type="number"
                min="1"
                .value="${String(t.interval_hours||24)}"
                @input=${e=>this._update({interval_hours:parseInt(e.target.value)})}
              />
              <span class="suffix"
                >${Hs("panels.schedules.hours",this.hass.language)}</span
              >
            </div>
          </div>
          <div class="field">
            <label
              >${Hs("panels.schedules.fields.start_time",this.hass.language)}</label
            >
            <input
              type="time"
              .value="${t.start_time||""}"
              @change=${e=>this._update({start_time:e.target.value||void 0})}
            />
          </div>
        `;case"sunrise":case"sunset":return Z`${this._renderSunOffsetFields()}`;case"solar_azimuth":return Z`
          <div class="field">
            <label
              >${Hs("panels.schedules.fields.azimuth_angle",this.hass.language)}</label
            >
            <div class="input-suffix-row">
              <input
                type="number"
                min="0"
                max="359"
                step="1"
                .value="${String(null!==(e=t.azimuth_angle)&&void 0!==e?e:90)}"
                @input=${e=>this._update({azimuth_angle:parseInt(e.target.value)})}
              />
              <span class="suffix">°</span>
            </div>
          </div>
          ${this._renderSunOffsetFields()}
        `;default:return Z``}}_renderSunOffsetFields(){var e;const t=this._editingSchedule;return Z`
      <div class="field">
        <label
          >${Hs("panels.schedules.fields.offset_minutes",this.hass.language)}</label
        >
        <div class="input-suffix-row">
          <input
            type="number"
            step="1"
            .value="${String(null!==(e=t.offset_minutes)&&void 0!==e?e:0)}"
            @input=${e=>this._update({offset_minutes:parseInt(e.target.value)})}
          />
          <span class="suffix"
            >${Hs("panels.schedules.minutes",this.hass.language)}</span
          >
        </div>
      </div>
    `}_renderTimeAnchorField(){var e;const t=this._editingSchedule;if("irrigate"!==t.action||"interval"===t.type)return Z``;const i=["sunrise","sunset","solar_azimuth"].includes(t.type)&&!1!==t.account_for_duration,s=null!==(e=t.time_anchor)&&void 0!==e?e:i?"finish":"start";return Z`
      <div class="field">
        <label
          >${Hs("panels.schedules.fields.time_anchor",this.hass.language)}</label
        >
        <select
          @change=${e=>this._update({time_anchor:e.target.value})}
        >
          ${["start","finish"].map(e=>Z`
              <option value="${e}" ?selected="${s===e}">
                ${Hs(`panels.schedules.time_anchor.${e}`,this.hass.language)}
              </option>
            `)}
        </select>
      </div>
    `}_renderDialog(){if(!this._showDialog)return Z``;const e=this._editingSchedule,t=this._editingId?Hs("panels.schedules.dialog.edit_title",this.hass.language):Hs("panels.schedules.dialog.add_title",this.hass.language);return Z`
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
              >${Hs("panels.schedules.fields.name",this.hass.language)}</label
            >
            <input
              type="text"
              .value="${e.name}"
              @input=${e=>this._update({name:e.target.value})}
              required
            />
          </div>

          <div class="field">
            <label
              >${Hs("panels.schedules.fields.type",this.hass.language)}</label
            >
            <select
              @change=${e=>this._update({type:e.target.value})}
            >
              ${["daily","weekly","monthly","interval","sunrise","sunset","solar_azimuth"].map(t=>Z`
                  <option value="${t}" ?selected="${e.type===t}">
                    ${this._typeLabel(t)}
                  </option>
                `)}
            </select>
          </div>

          ${this._renderTypeFields()} ${this._renderTimeAnchorField()}
          ${this._renderZonePicker()}

          <div class="field-row">
            <label
              >${Hs("panels.schedules.fields.enabled",this.hass.language)}</label
            >
            <input
              type="checkbox"
              ?checked="${e.enabled}"
              @change=${e=>this._update({enabled:e.target.checked})}
            />
          </div>

          <div class="field">
            <label
              >${Hs("panels.schedules.fields.start_date",this.hass.language)}</label
            >
            <input
              type="date"
              .value="${e.start_date||""}"
              @change=${e=>this._update({start_date:e.target.value||void 0})}
            />
          </div>

          <div class="field">
            <label
              >${Hs("panels.schedules.fields.end_date",this.hass.language)}</label
            >
            <input
              type="date"
              .value="${e.end_date||""}"
              @change=${e=>this._update({end_date:e.target.value||void 0})}
            />
          </div>
        </div>

        <div class="dialog-footer">
          <button class="dialog-btn" @click=${this._closeDialog}>
            ${Hs("common.actions.cancel",this.hass.language)}
          </button>
          <button class="dialog-btn dialog-btn-primary" @click=${this._save}>
            ${Hs("common.actions.save",this.hass.language)}
          </button>
        </div>
      </ha-dialog>
    `}render(){return this.hass?this._isLoading?Z`
        <ha-card
          header="${Hs("panels.schedules.title",this.hass.language)}"
        >
          <div class="card-content">
            ${Hs("common.loading",this.hass.language)}...
          </div>
        </ha-card>
      `:Z`
      ${this._renderDialog()}

      <ha-card
        header="${Hs("panels.schedules.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Hs("panels.schedules.description",this.hass.language)}
        </div>
        <div class="card-content">
          <button class="add-btn" @click=${this._openAdd}>
            <svg style="width:20px;height:20px" viewBox="0 0 24 24">
              <path fill="currentColor" d="${js}" />
            </svg>
            ${Hs("panels.schedules.add",this.hass.language)}
          </button>
        </div>
      </ha-card>

      ${0===this._schedules.length?Z`
            <ha-card>
              <div class="card-content">
                ${Hs("panels.schedules.no_items",this.hass.language)}
              </div>
            </ha-card>
          `:this._schedules.map(e=>Z`
              <ha-card header="${e.name}">
                <div class="card-content">
                  <div class="info-row">
                    <span class="info-label"
                      >${Hs("panels.schedules.fields.type",this.hass.language)}:</span
                    >
                    <span>${this._typeLabel(e.type)}</span>
                  </div>
                  ${e.time&&["daily","weekly","monthly"].includes(e.type)?Z`
                        <div class="info-row">
                          <span class="info-label"
                            >${Hs("panels.schedules.fields.time",this.hass.language)}:</span
                          >
                          <span>${e.time}</span>
                        </div>
                      `:""}
                  ${e.interval_hours?Z`
                        <div class="info-row">
                          <span class="info-label"
                            >${Hs("panels.schedules.fields.interval_hours",this.hass.language)}:</span
                          >
                          <span
                            >${e.interval_hours}
                            ${Hs("panels.schedules.hours",this.hass.language)}</span
                          >
                        </div>
                      `:""}
                  ${"interval"===e.type&&e.start_time?Z`
                        <div class="info-row">
                          <span class="info-label"
                            >${Hs("panels.schedules.fields.start_time",this.hass.language)}:</span
                          >
                          <span>${e.start_time}</span>
                        </div>
                      `:""}
                  <div class="info-row">
                    <span class="info-label"
                      >${Hs("panels.schedules.fields.zones",this.hass.language)}:</span
                    >
                    <span>${this._zonesLabel(e.zones)}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${Hs("panels.schedules.fields.enabled",this.hass.language)}:</span
                    >
                    <span
                      >${e.enabled?Hs("common.labels.yes",this.hass.language):Hs("common.labels.no",this.hass.language)}</span
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
                        >${Hs("common.actions.edit",this.hass.language)}</span
                      >
                    </div>
                  </div>
                  <div class="action-buttons-right">
                    <div
                      class="action-button-right"
                      @click=${()=>e.id&&this._delete(e.id)}
                    >
                      <span class="action-button-label"
                        >${Hs("common.actions.delete",this.hass.language)}</span
                      >
                      <svg style="width:20px;height:20px" viewBox="0 0 24 24">
                        <path fill="#404040" d="${"M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"}" />
                      </svg>
                    </div>
                  </div>
                </div>
              </ha-card>
            `)}
    `:Z``}static get styles(){return[la,r`
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
      `]}};t([pe({attribute:!1})],Ca.prototype,"hass",void 0),t([ge()],Ca.prototype,"_schedules",void 0),t([ge()],Ca.prototype,"_zones",void 0),t([ge()],Ca.prototype,"_isLoading",void 0),t([ge()],Ca.prototype,"_showDialog",void 0),t([ge()],Ca.prototype,"_editingSchedule",void 0),t([ge()],Ca.prototype,"_editingId",void 0),Ca=t([de("smart-irrigation-view-schedules")],Ca);let Ta=class extends(sa(le)){constructor(){super(...arguments),this._forecast=null,this._mappings=[],this._records=new Map,this._loading=!0,this._metric=!0,this._climate=[]}hassSubscribe(){return this._fetch(),[this.hass.connection.subscribeMessage(()=>this._fetch(),{type:ye+"_config_updated"})]}async _fetch(){var e,t;if(this.hass)try{const[i,s,a,n]=await Promise.all([(t=this.hass,t.callWS({type:ye+"/weather_forecast"})),Ys(this.hass),Fs(this.hass),Js(this.hass)]);this._forecast=i,this._mappings=s||[],this._metric=(null==a?void 0:a.units)!==Te;const o=n?Object.values(n):[];this._climate=o.length>0&&(null===(e=o[0])||void 0===e?void 0:e.monthly_estimates)||[];const r=new Map;await Promise.all(this._mappings.map(async e=>{if(void 0!==e.id)try{r.set(e.id,await((e,t,i=10)=>e.callWS({type:ye+"/weather_records",mapping_id:t,limit:i}))(this.hass,e.id.toString(),0)||[])}catch(e){}})),this._records=r}catch(e){console.error("Failed to fetch weather data",e)}finally{this._loading=!1}}render(){return this.hass?Z`${this._renderForecast()} ${this._renderRecords()}
    ${this._renderSeasonal()}`:Z``}_renderSeasonal(){if(!this.hass)return Z``;const e=this.hass.language;return Z`
      <ha-card
        header="${Hs("panels.setup.weather_data.seasonal_title",e)}"
      >
        <div class="card-content">
          ${0===this._climate.length?Z`<div class="weather-note">
                ${Hs("panels.zones.calendar.no_data",e)}
              </div>`:Z`
                <div class="seasonal-table">
                  <div class="weather-header">
                    <span
                      >${Hs("panels.zones.calendar.month",e)}</span
                    >
                    <span>${Hs("panels.zones.calendar.et",e)}</span>
                    <span
                      >${Hs("panels.zones.calendar.precipitation",e)}</span
                    >
                    <span
                      >${Hs("panels.zones.calendar.avg_temp",e)}</span
                    >
                  </div>
                  ${this._climate.map(e=>Z`
                      <div class="weather-row">
                        <span
                          >${e.month_name||`Month ${e.month}`||"-"}</span
                        >
                        <span
                          >${$a(e.estimated_et_mm,"precipitation",this._metric)}</span
                        >
                        <span
                          >${$a(e.average_precipitation_mm,"precipitation",this._metric)}</span
                        >
                        <span
                          >${$a(e.average_temperature_c,"temperature",this._metric)}</span
                        >
                      </div>
                    `)}
                </div>
              `}
        </div>
      </ha-card>
    `}_renderForecast(){if(!this.hass)return Z``;const e=this.hass.language,t=this._forecast;return Z`
      <ha-card
        header="${Hs("panels.setup.weather_data.forecast_title",e)}"
      >
        <div class="card-content">
          ${t&&t.available&&0!==t.days.length?Z`
                <div class="forecast-row">
                  ${t.days.map(t=>this._renderForecastDay(t,e))}
                </div>
              `:Z`<div class="weather-note">
                ${Hs("panels.setup.weather_data.forecast_none",e)}
              </div>`}
        </div>
      </ha-card>
    `}_renderForecastDay(e,t){const i=(()=>{try{return new Intl.DateTimeFormat(t,{weekday:"short",month:"short",day:"numeric"}).format(new Date(e.date+"T00:00:00"))}catch(t){return e.date}})(),s=e=>{const t=wa(e,"temperature",this._metric);return t?`${Math.round(t.value)}°`:"-"};return Z`
      <div class="forecast-day">
        <div class="forecast-date">${i}</div>
        <div class="forecast-temps">
          <span class="hi">${s(e.temp_max)}</span>
          <span class="lo">${s(e.temp_min)}</span>
        </div>
        <div class="forecast-meta">
          <ha-icon icon="mdi:weather-rainy"></ha-icon>${$a(e.precipitation,"precipitation",this._metric)}
        </div>
        <div class="forecast-meta">
          <ha-icon icon="mdi:weather-windy"></ha-icon>${$a(e.windspeed,"windspeed",this._metric)}
        </div>
      </div>
    `}_renderRecords(){if(!this.hass)return Z``;const e=this.hass.language;return this._loading&&0===this._mappings.length?Z`<ha-card
        header="${Hs("panels.mappings.weather-records.title",e)}"
      >
        <div class="card-content">
          <div class="loading-indicator">
            ${Hs("common.loading-messages.general",e)}
          </div>
        </div>
      </ha-card>`:0===this._mappings.length?Z`<ha-card
        header="${Hs("panels.mappings.weather-records.title",e)}"
      >
        <div class="card-content">
          <div class="weather-note">
            ${Hs("panels.mappings.no_items",e)}
          </div>
        </div>
      </ha-card>`:Z`${this._mappings.map(t=>this._renderMappingRecords(t,e))}`}_renderMappingRecords(e,t){const i=void 0!==e.id&&this._records.get(e.id)||[],s=`${Hs("panels.mappings.weather-records.title",t)} — ${e.name}`,a=e=>{try{return t=e,Number.isNaN(da(t).getTime())?"-":function(e){const t=da(e);return`${ca(t.getMonth()+1)}-${ca(t.getDate())} ${ca(t.getHours())}:${ca(t.getMinutes())}`}(e)}catch(e){return"-"}var t};return Z`
      <ha-card header="${s}">
        <div class="card-content">
          ${0===i.length?Z`<div class="weather-note">
                ${Hs("panels.mappings.weather-records.no-data",t)}
              </div>`:Z`
                <div class="weather-table">
                  <div class="weather-header">
                    <span
                      >${Hs("panels.mappings.weather-records.timestamp",t)}</span
                    >
                    <span
                      >${Hs("panels.mappings.weather-records.temperature",t)}</span
                    >
                    <span
                      >${Hs("panels.mappings.weather-records.humidity",t)}</span
                    >
                    <span
                      >${Hs("panels.mappings.weather-records.dewpoint",t)}</span
                    >
                    <span
                      >${Hs("panels.mappings.weather-records.wind",t)}</span
                    >
                    <span
                      >${Hs("panels.mappings.weather-records.pressure",t)}</span
                    >
                    <span
                      >${Hs("panels.mappings.weather-records.precipitation",t)}</span
                    >
                    <span
                      >${Hs("panels.mappings.weather-records.retrieval-time",t)}</span
                    >
                  </div>
                  ${i.map(e=>Z`
                      <div class="weather-row">
                        <span>${a(e.timestamp)}</span>
                        <span
                          >${$a(e.temperature,"temperature",this._metric)}</span
                        >
                        <span>${(e=>null!=e?e.toFixed(1)+" %":"-")(e.humidity)}</span>
                        <span
                          >${$a(e.dewpoint,"temperature",this._metric)}</span
                        >
                        <span
                          >${$a(e.wind_speed,"windspeed",this._metric)}</span
                        >
                        <span
                          >${$a(e.pressure,"pressure",this._metric)}</span
                        >
                        <span
                          >${$a(e.precipitation,"precipitation",this._metric)}</span
                        >
                        <span>${a(e.retrieval_time)}</span>
                      </div>
                    `)}
                </div>
              `}
        </div>
      </ha-card>
    `}static get styles(){return r`
      ${la}

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
    `}};t([pe()],Ta.prototype,"narrow",void 0),t([ge()],Ta.prototype,"_forecast",void 0),t([ge()],Ta.prototype,"_mappings",void 0),t([ge()],Ta.prototype,"_records",void 0),t([ge()],Ta.prototype,"_loading",void 0),t([ge()],Ta.prototype,"_metric",void 0),t([ge()],Ta.prototype,"_climate",void 0),Ta=t([de("smart-irrigation-view-weather-data")],Ta);let Oa=class extends(sa(le)){constructor(){super(...arguments),this._saving=!1}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch experimental config:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to refresh experimental config:",e)})},{type:ye+"_config_updated"})]}async _fetchData(){if(this.hass)try{this.config=await Fs(this.hass)}catch(e){console.error("Error fetching config:",e),Rs(this,this.hass,"common.errors.load_failed",e)}}async _toggle(e,t){if(this.hass&&this.config){this.config=Object.assign(Object.assign({},this.config),{[e]:t}),this._saving=!0;try{await Zs(this.hass,{[e]:t})}catch(e){console.error("Error saving experimental config:",e),Rs(this,this.hass,"common.errors.save_failed",e),await this._fetchData()}finally{this._saving=!1}}}render(){var e,t;return this.hass&&this.config?Z`
      ${this._renderIntro()}
      ${this._renderToggleCard("observed_watering","observed_watering_enabled",this.config.observed_watering_enabled)}
      ${this._renderToggleCard("live_estimate","live_estimate_enabled",this.config.live_estimate_enabled)}
    `:Z`<div class="loading-indicator">
        ${Hs("common.loading-messages.configuration",null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en")}
      </div>`}_renderIntro(){return this.hass?Z`
      <div class="experimental-banner">
        <ha-icon icon="mdi:flask-outline"></ha-icon>
        <div>
          <div class="experimental-banner-title">
            ${Hs("panels.experimental.title",this.hass.language)}
          </div>
          <div class="experimental-banner-text">
            ${Hs("panels.experimental.warning",this.hass.language)}
          </div>
        </div>
      </div>
    `:Z``}_renderToggleCard(e,t,i){if(!this.hass)return Z``;const s=`panels.experimental.${e}`;return Z`
      <ha-card header="${Hs(`${s}.title`,this.hass.language)}">
        <div class="card-content description-text">
          ${Hs(`${s}.description`,this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>${Hs(`${s}.label`,this.hass.language)}</label>
            <ha-switch
              .checked="${i}"
              ?disabled="${this._saving}"
              @change="${e=>this._toggle(t,e.target.checked)}"
            ></ha-switch>
          </div>
          <div class="setting-note">
            ${Hs(`${s}.note`,this.hass.language)}
          </div>
        </div>
      </ha-card>
    `}static get styles(){return r`
      ${la}

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
    `}};t([pe()],Oa.prototype,"narrow",void 0),t([ge()],Oa.prototype,"config",void 0),t([ge()],Oa.prototype,"_saving",void 0),Oa=t([de("smart-irrigation-view-experimental")],Oa);var Ha;!function(e){e.WeatherLocation="weather-location",e.Zones="zones",e.WhenToWater="when-to-water",e.Advanced="advanced",e.Experimental="experimental",e.Help="help"}(Ha||(Ha={}));const Ma={[Ha.WeatherLocation]:"panels.setup.tabs.weather_location",[Ha.Zones]:"panels.setup.tabs.my_zones",[Ha.WhenToWater]:"panels.setup.tabs.when_to_water",[Ha.Advanced]:"panels.setup.tabs.advanced",[Ha.Experimental]:"panels.setup.tabs.experimental",[Ha.Help]:"panels.help.title"};let Da=class extends le{get _activeTab(){var e;const t=null===(e=this.path)||void 0===e?void 0:e.subpage;return Object.values(Ha).includes(null!=t?t:"")?t:Ha.WeatherLocation}_selectTab(e){Is(0,ra("setup",e))}_openWizard(){this.dispatchEvent(new CustomEvent("open-wizard",{bubbles:!0,composed:!0}))}render(){if(!this.hass)return Z``;const e=this._activeTab;return Z`
      <div class="setup-container">
        <nav class="setup-nav">
          ${Object.values(Ha).map(t=>Z`
              <button
                class="setup-nav-btn ${e===t?"active":""}"
                @click="${()=>this._selectTab(t)}"
              >
                ${Hs(Ma[t],this.hass.language)}
              </button>
            `)}
          <button
            class="setup-nav-btn wizard-btn"
            @click="${this._openWizard}"
            title="${Hs("wizard.title",this.hass.language)}"
          >
            <ha-icon icon="mdi:creation"></ha-icon>
            ${Hs("wizard.open_button",this.hass.language)}
          </button>
        </nav>
        <div class="setup-content">${this._renderContent(e)}</div>
      </div>
    `}_renderContent(e){if(!this.hass)return Z``;switch(e){case Ha.WeatherLocation:return Z`
          <smart-irrigation-view-general
            .hass="${this.hass}"
            .narrow="${this.narrow}"
            section="weather-location"
          ></smart-irrigation-view-general>
          <smart-irrigation-view-weather-data
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-weather-data>
        `;case Ha.Zones:return Z`<smart-irrigation-view-zone-settings
          .hass="${this.hass}"
          .narrow="${this.narrow}"
          .path="${this.path}"
        ></smart-irrigation-view-zone-settings>`;case Ha.WhenToWater:return Z`
          <smart-irrigation-view-general
            .hass="${this.hass}"
            .narrow="${this.narrow}"
            section="when-to-water"
          ></smart-irrigation-view-general>
          <smart-irrigation-view-schedules
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-schedules>
        `;case Ha.Advanced:return Z`
          <smart-irrigation-view-modules
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-modules>
          <smart-irrigation-view-mappings
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-mappings>
        `;case Ha.Experimental:return Z`<smart-irrigation-view-experimental
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-experimental>`;case Ha.Help:return this._renderHelp()}}_renderHelp(){return this.hass?Z`
      <ha-card
        header="${Hs("panels.help.cards.how-to-get-help.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Hs("panels.help.cards.how-to-get-help.first-read-the",this.hass.language)}
          <a href="${"https://justchr.github.io/HAsmartirrigation/"}"
            >${Hs("panels.help.cards.how-to-get-help.wiki",this.hass.language)}</a
          >.
          ${Hs("panels.help.cards.how-to-get-help.if-you-still-need-help",this.hass.language)}
          <a
            href="https://community.home-assistant.io/t/smart-irrigation-save-water-by-precisely-watering-your-lawn-garden"
            >${Hs("panels.help.cards.how-to-get-help.community-forum",this.hass.language)}</a
          >
          ${Hs("panels.help.cards.how-to-get-help.or-open-a",this.hass.language)}
          <a href="${"https://github.com/JustChr/HAsmartirrigation/issues"}"
            >${Hs("panels.help.cards.how-to-get-help.github-issue",this.hass.language)}</a
          >
          (${Hs("panels.help.cards.how-to-get-help.english-only",this.hass.language)}).
        </div>
      </ha-card>
    `:Z``}static get styles(){return r`
      ${la}

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
    `}};var La;t([pe({attribute:!1})],Da.prototype,"hass",void 0),t([pe({type:Boolean})],Da.prototype,"narrow",void 0),t([pe({attribute:!1})],Da.prototype,"path",void 0),Da=t([de("smart-irrigation-view-setup")],Da),function(e){e[e.Welcome=0]="Welcome",e[e.Weather=1]="Weather",e[e.Module=2]="Module",e[e.Mapping=3]="Mapping",e[e.Zone=4]="Zone",e[e.Done=5]="Done"}(La||(La={}));let Na=class extends le{constructor(){super(...arguments),this._step=La.Welcome,this._saving=!1,this._error="",this._confirmClose=!1,this._siConfig=null,this._useWeather=!1,this._weatherService=ze,this._apiKey="",this._weatherConfig=null,this._availableModules=[],this._selectedModuleIndex=0,this._moduleConfig={},this._mappingName="My Sensor Group",this._tempSource=Ue,this._humiditySource=Ue,this._precipSource=Ue,this._zoneName="My Zone",this._zoneSize="",this._zoneThroughput="",this._zoneEntity="",this._scheduleTime="06:00",this._scheduleCreated=!1,this._creatingSchedule=!1}async connectedCallback(){super.connectedCallback(),await this._loadInitialData()}async _loadInitialData(){var e;if(this.hass){try{const[t,i,s]=await Promise.all([Ks(this.hass),ea(this.hass),Fs(this.hass)]);this._availableModules=t,this._weatherConfig=i,this._siConfig=s,this._useWeather=i.use_weather_service,this._weatherService=null!==(e=i.weather_service)&&void 0!==e?e:ze}catch(e){console.error("Wizard: failed to load initial data",e),this._error=Ps(e)}this.requestUpdate()}}_close(){this.dispatchEvent(new CustomEvent("wizard-close",{bubbles:!0,composed:!0}))}_navigate(e){this.dispatchEvent(new CustomEvent("wizard-navigate",{detail:{page:e},bubbles:!0,composed:!0}))}async _next(){this._error="";try{switch(this._saving=!0,this._step){case La.Welcome:this._step=La.Weather;break;case La.Weather:await this._saveWeather(),this._step=La.Module;break;case La.Module:await this._saveModule(),this._step=La.Mapping;break;case La.Mapping:await this._saveMapping(),this._step=La.Zone;break;case La.Zone:await this._saveZone(),this._step=La.Done;break;case La.Done:this._close()}}catch(e){this._error=e instanceof Error?e.message:String(e)}finally{this._saving=!1,this.requestUpdate()}}_back(){this._step>La.Welcome&&(this._step=this._step-1,this._error="")}get _canSkipCurrentStep(){return this._step===La.Weather}_skipStep(){this._canSkipCurrentStep&&this._step<La.Done&&(this._step=this._step+1,this._error="")}async _saveWeather(){await ta(this.hass,this._useWeather,this._useWeather?this._weatherService:null,this._apiKey||null)}async _resolveSavedId(e,t){if("number"==typeof(null==e?void 0:e.id))return e.id;try{const e=(await t()).map(e=>e.id).filter(e=>"number"==typeof e);return e.length?Math.max(...e):void 0}catch(e){return}}async _saveModule(){if(0===this._availableModules.length)throw new Error("No calculation module is available to configure. Cannot continue.");const e=this._availableModules[this._selectedModuleIndex],t=await Vs(this.hass,{name:e.name,description:e.description,config:Object.assign(Object.assign({},e.config),this._moduleConfig),schema:e.schema});if(this._savedModuleId=await this._resolveSavedId(t,()=>Gs(this.hass)),void 0===this._savedModuleId)throw new Error("The calculation module was saved but could not be linked. Please try again.")}async _saveMapping(){const e=this._useWeather?Ue:Ge,t={[Be]:{[Ke]:this._tempSource},[De]:{[Ke]:this._humiditySource},[Le]:{[Ke]:this._precipSource}},i=["Dewpoint","Evapotranspiration","Maximum Temperature","Minimum Temperature","Current Precipitation","Pressure","Solar Radiation","Windspeed"];for(const s of i)t[s]={[Ke]:e};const s=await Xs(this.hass,{name:this._mappingName,mappings:t});if(this._savedMappingId=await this._resolveSavedId(s,()=>Ys(this.hass)),void 0===this._savedMappingId)throw new Error("The sensor group was saved but could not be linked. Please try again.")}async _saveZone(){if(!this._zoneName.trim())throw new Error("Zone name is required");const e=parseFloat(this._zoneSize),t=parseFloat(this._zoneThroughput);if(!(e>0))throw new Error("Zone size must be greater than 0.");if(!(t>0))throw new Error("Throughput must be greater than 0 (zones can't water otherwise).");await qs(this.hass,{name:this._zoneName.trim(),size:e,throughput:t,state:na.Automatic,duration:0,bucket:0,delta:0,explanation:"",multiplier:1,module:this._savedModuleId,mapping:this._savedMappingId,lead_time:0,linked_entity:this._zoneEntity||void 0})}async _createDefaultSchedule(){var e,t;if(!this._scheduleCreated&&!this._creatingSchedule){this._error="",this._creatingSchedule=!0;try{const i=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";await Qs(this.hass,{name:Hs("wizard.steps.done.schedule_name",i)||"Daily",type:"daily",enabled:!0,time:this._scheduleTime||"06:00",action:"irrigate",zones:"all"}),this._scheduleCreated=!0}catch(e){this._error=e instanceof Error?e.message:String(e)}finally{this._creatingSchedule=!1,this.requestUpdate()}}}render(){var e,t;const i=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";return Z`
      <div class="wizard-overlay" @click="${this._onOverlayClick}">
        <div
          class="wizard-dialog"
          @click="${e=>e.stopPropagation()}"
        >
          <div class="wizard-header">
            <span class="wizard-title">${Hs("wizard.title",i)}</span>
            <button
              class="wizard-close-btn"
              @click="${this._close}"
              title="${Hs("wizard.close",i)}"
              aria-label="${Hs("wizard.close",i)}"
            >
              <ha-icon icon="mdi:close"></ha-icon>
            </button>
          </div>
          ${this._step!==La.Welcome&&this._step!==La.Done?Z`<div class="wizard-stepper">${this._renderStepper()}</div>`:""}
          <div class="wizard-body">
            ${this._renderStep(i)}
            ${this._error?Z`<div class="wizard-error">${this._error}</div>`:""}
          </div>
          <div class="wizard-footer">${this._renderFooter(i)}</div>
          ${this._confirmClose?Z`
                <div class="wizard-confirm-close">
                  <div class="wizard-confirm-box">
                    <p>${Hs("wizard.confirm_close.body",i)}</p>
                    <div class="wizard-confirm-actions">
                      <button
                        class="wizard-btn secondary"
                        @click="${()=>{this._confirmClose=!1}}"
                      >
                        ${Hs("wizard.confirm_close.keep",i)}
                      </button>
                      <button
                        class="wizard-btn primary"
                        @click="${()=>{this._confirmClose=!1,this._close()}}"
                      >
                        ${Hs("wizard.confirm_close.close",i)}
                      </button>
                    </div>
                  </div>
                </div>
              `:""}
        </div>
      </div>
    `}_onOverlayClick(e){e.target===e.currentTarget&&(this._step>La.Welcome&&this._step<La.Done?this._confirmClose=!0:this._close())}_renderStepper(){var e,t;const i=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en",s=[Hs("wizard.stepper.weather",i),Hs("wizard.stepper.module",i),Hs("wizard.stepper.mapping",i),Hs("wizard.stepper.zone",i)];return Z`
      ${s.map((e,t)=>{const i=t+1,a=this._step===i,n=this._step>i;return Z`
          <div
            class="stepper-step ${a?"active":""} ${n?"done":""}"
          >
            <div class="stepper-circle">${n?"✓":i}</div>
            <span class="stepper-label">${e}</span>
          </div>
          ${t<s.length-1?Z`<div class="stepper-line ${n?"done":""}"></div>`:""}
        `})}
    `}_renderStep(e){switch(this._step){case La.Welcome:return this._renderWelcome(e);case La.Weather:return this._renderWeather(e);case La.Module:return this._renderModule(e);case La.Mapping:return this._renderMapping(e);case La.Zone:return this._renderZone(e);case La.Done:return this._renderDone(e);default:return Z``}}_renderFooter(e){return this._step===La.Done?Z``:Z`
      <div class="footer-left">
        ${this._step>La.Welcome?Z`<button
              class="wizard-btn secondary"
              @click="${this._back}"
              ?disabled="${this._saving}"
            >
              ${Hs("wizard.back",e)}
            </button>`:""}
        ${this._canSkipCurrentStep?Z`<button
              class="wizard-btn ghost"
              @click="${this._skipStep}"
              ?disabled="${this._saving}"
            >
              ${Hs("wizard.skip_step",e)}
            </button>`:""}
      </div>
      <button
        class="wizard-btn primary"
        @click="${this._next}"
        ?disabled="${this._saving}"
      >
        ${this._saving?Hs("common.saving-messages.saving",e):this._step===La.Welcome||this._step<La.Zone?Hs("wizard.next",e):Hs("wizard.finish",e)}
      </button>
    `}_renderWelcome(e){return Z`
      <h2 class="step-title">
        ${Hs("wizard.steps.welcome.title",e)}
      </h2>
      <p class="step-desc">${Hs("wizard.steps.welcome.intro",e)}</p>
      <ul class="step-list">
        <li>① ${Hs("wizard.steps.welcome.step1_label",e)}</li>
        <li>② ${Hs("wizard.steps.welcome.step2_label",e)}</li>
        <li>③ ${Hs("wizard.steps.welcome.step3_label",e)}</li>
        <li>④ ${Hs("wizard.steps.welcome.step4_label",e)}</li>
      </ul>
      <p class="step-tip">${Hs("wizard.steps.welcome.tip",e)}</p>
    `}_renderWeather(e){return Z`
      <h2 class="step-title">
        ${Hs("wizard.steps.weather.title",e)}
      </h2>
      <p class="step-desc">
        ${Hs("wizard.steps.weather.description",e)}
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
    `}_renderModule(e){if(0===this._availableModules.length)return Z`
        <h2 class="step-title">
          ${Hs("wizard.steps.module.title",e)}
        </h2>
        <p class="step-desc">
          ${Hs("wizard.steps.module.no_modules",e)}
        </p>
      `;const t=this._availableModules[this._selectedModuleIndex];return Z`
      <h2 class="step-title">${Hs("wizard.steps.module.title",e)}</h2>
      <p class="step-desc">
        ${Hs("wizard.steps.module.description",e)}
      </p>

      <si-field
        label="${Hs("wizard.steps.module.pick_label",e)}"
        required
      >
        <select
          class="wizard-input"
          @change="${e=>{this._selectedModuleIndex=parseInt(e.target.value),this._moduleConfig={}}}"
        >
          ${this._availableModules.map((e,t)=>Z`
              <option
                value="${t}"
                ?selected="${t===this._selectedModuleIndex}"
              >
                ${e.name}
              </option>
            `)}
        </select>
      </si-field>

      ${(null==t?void 0:t.description)?Z`<p class="module-desc">${t.description}</p>`:""}
      ${(null==t?void 0:t.schema)&&Array.isArray(t.schema)&&t.schema.length>0?Z`
            <div class="schema-fields">
              ${t.schema.map(e=>this._renderModuleField(e.name,e))}
            </div>
          `:""}
    `}_renderModuleField(e,t){var i,s;const a=e.replace(/_/g," ").replace(/\b\w/g,e=>e.toUpperCase()),n=null!==(s=null!==(i=this._moduleConfig[e])&&void 0!==i?i:t.default)&&void 0!==s?s:"",o=t.description;return"boolean"===t.type?Z`
        <si-field label="${a}" help="${null!=o?o:""}">
          <ha-switch
            .checked="${Boolean(n)}"
            @change="${t=>{this._moduleConfig=Object.assign(Object.assign({},this._moduleConfig),{[e]:t.target.checked})}}"
          ></ha-switch>
        </si-field>
      `:"select"===t.type&&t.options?Z`
        <si-field label="${a}" help="${null!=o?o:""}">
          <select
            class="wizard-input"
            @change="${t=>{this._moduleConfig=Object.assign(Object.assign({},this._moduleConfig),{[e]:t.target.value})}}"
          >
            ${t.options.map(([e,t])=>Z`<option
                  value="${e}"
                  ?selected="${e===String(n)}"
                >
                  ${t}
                </option>`)}
          </select>
        </si-field>
      `:Z`
      <si-field label="${a}" help="${null!=o?o:""}">
        <input
          type="${"float"===t.type||"integer"===t.type?"number":"text"}"
          class="wizard-input"
          step="${"float"===t.type?"0.01":"1"}"
          .value="${String(n)}"
          @input="${i=>{const s=i.target.value,a="float"===t.type?parseFloat(s):"integer"===t.type?parseInt(s):s;this._moduleConfig=Object.assign(Object.assign({},this._moduleConfig),{[e]:a})}}"
        />
      </si-field>
    `}_renderMapping(e){const t=[{value:Ue,label:Hs("wizard.steps.mapping.use_weather_service",e)},{value:"sensor",label:Hs("wizard.steps.mapping.use_sensor",e)},{value:"static",label:Hs("wizard.steps.mapping.use_static",e)},{value:Ge,label:Hs("wizard.steps.mapping.use_none",e)}],i=(i,s,a)=>Z`
      <si-field
        label="${Hs("wizard.steps.mapping.source_label",e)} ${i}"
      >
        <select
          class="wizard-input"
          @change="${e=>a(e.target.value)}"
        >
          ${t.map(e=>Z`<option value="${e.value}" ?selected="${e.value===s}">
                ${e.label}
              </option>`)}
        </select>
      </si-field>
    `;return Z`
      <h2 class="step-title">
        ${Hs("wizard.steps.mapping.title",e)}
      </h2>
      <p class="step-desc">
        ${Hs("wizard.steps.mapping.description",e)}
      </p>

      <si-field
        label="${Hs("wizard.steps.mapping.name_label",e)}"
        required
      >
        <input
          type="text"
          class="wizard-input"
          .value="${this._mappingName}"
          @input="${e=>{this._mappingName=e.target.value}}"
        />
      </si-field>

      ${i(Hs("panels.mappings.cards.mapping.items.temperature",e)||"Temperature",this._tempSource,e=>{this._tempSource=e,this.requestUpdate()})}
      ${i(Hs("panels.mappings.cards.mapping.items.humidity",e)||"Humidity",this._humiditySource,e=>{this._humiditySource=e,this.requestUpdate()})}
      ${i(Hs("panels.mappings.cards.mapping.items.precipitation",e)||"Precipitation",this._precipSource,e=>{this._precipSource=e,this.requestUpdate()})}

      <p class="step-tip">
        ${Hs("wizard.steps.mapping.description",e)}
      </p>
    `}_renderZone(e){var t;const i="imperial"!==(null===(t=this._siConfig)||void 0===t?void 0:t.units);return Z`
      <h2 class="step-title">${Hs("wizard.steps.zone.title",e)}</h2>
      <p class="step-desc">
        ${Hs("wizard.steps.zone.description",e)}
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
    `}_renderDone(e){return Z`
      <div class="done-wrapper">
        <div class="done-icon">
          <ha-icon icon="mdi:check-circle"></ha-icon>
        </div>
        <h2 class="step-title">${Hs("wizard.steps.done.title",e)}</h2>
        <p class="step-desc">
          ${Hs("wizard.steps.done.description",e)}
        </p>
        <ul class="step-list">
          <li>${Hs("wizard.steps.done.tip1",e)}</li>
          <li>${Hs("wizard.steps.done.tip2",e)}</li>
          <li>${Hs("wizard.steps.done.tip3",e)}</li>
        </ul>

        <div class="schedule-offer">
          ${this._scheduleCreated?Z`
                <div class="schedule-created">
                  <ha-icon icon="mdi:calendar-check"></ha-icon>
                  <span
                    >${Hs("wizard.steps.done.schedule_created",e)}</span
                  >
                </div>
              `:Z`
                <p class="schedule-offer-title">
                  ${Hs("wizard.steps.done.schedule_title",e)}
                </p>
                <p class="schedule-offer-desc">
                  ${Hs("wizard.steps.done.schedule_desc",e)}
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
                    ${this._creatingSchedule?Hs("common.saving-messages.saving",e):Hs("wizard.steps.done.schedule_create",e)}
                  </button>
                </div>
              `}
        </div>

        <div class="done-actions">
          <button
            class="wizard-btn primary"
            @click="${()=>{this._close(),this._navigate("zones")}}"
          >
            ${Hs("wizard.steps.done.go_zones",e)}
          </button>
          <button
            class="wizard-btn secondary"
            @click="${()=>{this._close(),this._navigate("setup")}}"
          >
            ${Hs("wizard.steps.done.go_setup",e)}
          </button>
        </div>
      </div>
    `}static get styles(){return r`
      ${la}

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
    `}};t([pe({attribute:!1})],Na.prototype,"hass",void 0),t([ge()],Na.prototype,"_step",void 0),t([ge()],Na.prototype,"_saving",void 0),t([ge()],Na.prototype,"_error",void 0),t([ge()],Na.prototype,"_confirmClose",void 0),t([ge()],Na.prototype,"_siConfig",void 0),t([ge()],Na.prototype,"_useWeather",void 0),t([ge()],Na.prototype,"_weatherService",void 0),t([ge()],Na.prototype,"_apiKey",void 0),t([ge()],Na.prototype,"_weatherConfig",void 0),t([ge()],Na.prototype,"_availableModules",void 0),t([ge()],Na.prototype,"_selectedModuleIndex",void 0),t([ge()],Na.prototype,"_moduleConfig",void 0),t([ge()],Na.prototype,"_mappingName",void 0),t([ge()],Na.prototype,"_tempSource",void 0),t([ge()],Na.prototype,"_humiditySource",void 0),t([ge()],Na.prototype,"_precipSource",void 0),t([ge()],Na.prototype,"_zoneName",void 0),t([ge()],Na.prototype,"_zoneSize",void 0),t([ge()],Na.prototype,"_zoneThroughput",void 0),t([ge()],Na.prototype,"_zoneEntity",void 0),t([ge()],Na.prototype,"_scheduleTime",void 0),t([ge()],Na.prototype,"_scheduleCreated",void 0),t([ge()],Na.prototype,"_creatingSchedule",void 0),Na=t([de("si-setup-wizard")],Na);const Ia=la;var Pa;!function(e){e.Zones="zones",e.Setup="setup"}(Pa||(Pa={})),e.SmartIrrigationPanel=class extends le{constructor(){super(...arguments),this._wizardOpen=!1,this._updateScheduled=!1,this._lastNavigationTime=0,this._navigationThrottleDelay=100}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}async firstUpdated(){const e=oa().page;Object.values(Pa).includes(e)||Is(0,ra(Pa.Zones)),window.addEventListener("location-changed",()=>{if(!window.location.pathname.includes("smart-irrigation"))return;const e=performance.now();e-this._lastNavigationTime<this._navigationThrottleDelay||(this._lastNavigationTime=e,this._scheduleUpdate())}),_e().then(()=>{this._scheduleUpdate()}).catch(e=>{console.error("Failed to load HA form elements:",e),this._scheduleUpdate()})}_ensureLanguage(){this.hass&&!Os(this.hass.language)&&function(e){const t=Ts(e);return Os(e)?Promise.resolve():(Cs[t]||(Cs[t]=fetch(`/smart_irrigation_static/languages/${t}.json?v=${be}`).then(e=>e.ok?e.json():Promise.reject(e.status)).then(e=>{As[t]=e}).catch(()=>{As[t]=As.en})),Cs[t])}(this.hass.language).then(()=>this.requestUpdate())}render(){if(this.hass&&!Os(this.hass.language))return this._ensureLanguage(),Z``;const e=oa(),t=!!customElements.get("ha-tab-group"),i=!!customElements.get("ha-tab-group-tab");return Z`
      <div class="header">
        <div class="toolbar">
          <ha-menu-button
            .hass=${this.hass}
            .narrow=${this.narrow}
          ></ha-menu-button>
          <div class="main-title">${Hs("title",this.hass.language)}</div>
          <div class="version">${be}</div>
        </div>

        ${t&&i?Z`
              <ha-tab-group @wa-tab-show=${this.handlePageSelected}>
                ${Object.values(Pa).map(t=>Z`
                    <ha-tab-group-tab
                      slot="nav"
                      panel="${t}"
                      .active=${e.page===t}
                    >
                      ${Hs(`panels.${t}.title`,this.hass.language)}
                    </ha-tab-group-tab>
                  `)}
              </ha-tab-group>
            `:Z`
              <div class="custom-tabs">
                ${Object.values(Pa).map(t=>Z`
                    <button
                      class="custom-tab ${e.page===t?"active":""}"
                      @click=${()=>this.navigateToPage(t)}
                    >
                      ${Hs(`panels.${t}.title`,this.hass.language)}
                    </button>
                  `)}
              </div>
            `}
      </div>
      <div class="view">${this.getView(e)}</div>
      ${this._wizardOpen?Z`
            <si-setup-wizard
              .hass="${this.hass}"
              @wizard-close="${()=>{this._wizardOpen=!1}}"
              @wizard-navigate="${e=>{var t,i;const s=null!==(i=null===(t=e.detail)||void 0===t?void 0:t.page)&&void 0!==i?i:"zones";this._wizardOpen=!1,this.navigateToPage(s)}}"
            ></si-setup-wizard>
          `:""}
    `}getView(e){switch(e.page){case"zones":default:return Z`
          <smart-irrigation-view-zones
            .hass=${this.hass}
            .narrow=${this.narrow}
            .path=${e}
            @open-wizard="${()=>{this._wizardOpen=!0}}"
          ></smart-irrigation-view-zones>
        `;case"setup":return Z`
          <smart-irrigation-view-setup
            .hass=${this.hass}
            .narrow=${this.narrow}
            .path=${e}
            @open-wizard="${()=>{this._wizardOpen=!0}}"
          ></smart-irrigation-view-setup>
        `}}navigateToPage(e){if(e!==oa().page){const t=ra(e);Is(0,t),this.requestUpdate()}else scrollTo(0,0)}handlePageSelected(e){const t=e.detail.name;if(t!==oa().page){const e=ra(t);Is(0,e),this.requestUpdate()}else scrollTo(0,0)}static get styles(){return[Ia,r`
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
      `]}},t([pe({attribute:!1})],e.SmartIrrigationPanel.prototype,"hass",void 0),t([pe({type:Boolean,reflect:!0})],e.SmartIrrigationPanel.prototype,"narrow",void 0),t([ge()],e.SmartIrrigationPanel.prototype,"_wizardOpen",void 0),e.SmartIrrigationPanel=t([de("smart-irrigation")],e.SmartIrrigationPanel);let Ba=class extends le{async showDialog(e){this._params=e,await this.updateComplete}async closeDialog(){this._params=void 0}render(){return this._params?Z`
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
              .path=${Us}
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
    `:Z``}static get styles(){return r`
      div.wrapper {
        color: var(--primary-text-color);
      }
      span.errortitle {
        font-size: 2em;
        font-weight: bold;
        vertical-align: bottom;
      }
    `}};t([pe({attribute:!1})],Ba.prototype,"hass",void 0),t([ge()],Ba.prototype,"_params",void 0),Ba=t([de("error-dialog")],Ba);var Ra=Object.freeze({__proto__:null,get ErrorDialog(){return Ba}})}({});
