!function(e){"use strict";function t(e,t,s,i){var a,n=arguments.length,o=n<3?t:null===i?i=Object.getOwnPropertyDescriptor(t,s):i;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)o=Reflect.decorate(e,t,s,i);else for(var r=e.length-1;r>=0;r--)(a=e[r])&&(o=(n<3?a(o):n>3?a(t,s,o):a(t,s))||o);return n>3&&o&&Object.defineProperty(t,s,o),o}"function"==typeof SuppressedError&&SuppressedError;
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const s=globalThis,i=s.ShadowRoot&&(void 0===s.ShadyCSS||s.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,a=Symbol(),n=new WeakMap;let o=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==a)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(i&&void 0===e){const s=void 0!==t&&1===t.length;s&&(e=n.get(t)),void 0===e&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&n.set(t,e))}return e}toString(){return this.cssText}};const r=(e,...t)=>{const s=1===e.length?e[0]:t.reduce((t,s,i)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+e[i+1],e[0]);return new o(s,e,a)},l=i?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const s of e.cssRules)t+=s.cssText;return(e=>new o("string"==typeof e?e:e+"",void 0,a))(t)})(e):e,{is:d,defineProperty:c,getOwnPropertyDescriptor:h,getOwnPropertyNames:u,getOwnPropertySymbols:p,getPrototypeOf:g}=Object,m=globalThis,v=m.trustedTypes,f=v?v.emptyScript:"",_=m.reactiveElementPolyfillSupport,b=(e,t)=>e,y={toAttribute(e,t){switch(t){case Boolean:e=e?f:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute(e,t){let s=e;switch(t){case Boolean:s=null!==e;break;case Number:s=null===e?null:Number(e);break;case Object:case Array:try{s=JSON.parse(e)}catch(e){s=null}}return s}},w=(e,t)=>!d(e,t),$={attribute:!0,type:String,converter:y,reflect:!1,useDefault:!1,hasChanged:w};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */Symbol.metadata??=Symbol("metadata"),m.litPropertyMetadata??=new WeakMap;let x=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=$){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const s=Symbol(),i=this.getPropertyDescriptor(e,s,t);void 0!==i&&c(this.prototype,e,i)}}static getPropertyDescriptor(e,t,s){const{get:i,set:a}=h(this.prototype,e)??{get(){return this[t]},set(e){this[t]=e}};return{get:i,set(t){const n=i?.call(this);a?.call(this,t),this.requestUpdate(e,n,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??$}static _$Ei(){if(this.hasOwnProperty(b("elementProperties")))return;const e=g(this);e.finalize(),void 0!==e.l&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(b("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(b("properties"))){const e=this.properties,t=[...u(e),...p(e)];for(const s of t)this.createProperty(s,e[s])}const e=this[Symbol.metadata];if(null!==e){const t=litPropertyMetadata.get(e);if(void 0!==t)for(const[e,s]of t)this.elementProperties.set(e,s)}this._$Eh=new Map;for(const[e,t]of this.elementProperties){const s=this._$Eu(e,t);void 0!==s&&this._$Eh.set(s,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const s=new Set(e.flat(1/0).reverse());for(const e of s)t.unshift(l(e))}else void 0!==e&&t.push(l(e));return t}static _$Eu(e,t){const s=t.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof e?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),void 0!==this.renderRoot&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((e,t)=>{if(i)e.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(const i of t){const t=document.createElement("style"),a=s.litNonce;void 0!==a&&t.setAttribute("nonce",a),t.textContent=i.cssText,e.appendChild(t)}})(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){const s=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,s);if(void 0!==i&&!0===s.reflect){const a=(void 0!==s.converter?.toAttribute?s.converter:y).toAttribute(t,s.type);this._$Em=e,null==a?this.removeAttribute(i):this.setAttribute(i,a),this._$Em=null}}_$AK(e,t){const s=this.constructor,i=s._$Eh.get(e);if(void 0!==i&&this._$Em!==i){const e=s.getPropertyOptions(i),a="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==e.converter?.fromAttribute?e.converter:y;this._$Em=i;const n=a.fromAttribute(t,e.type);this[i]=n??this._$Ej?.get(i)??n,this._$Em=null}}requestUpdate(e,t,s,i=!1,a){if(void 0!==e){const n=this.constructor;if(!1===i&&(a=this[e]),s??=n.getPropertyOptions(e),!((s.hasChanged??w)(a,t)||s.useDefault&&s.reflect&&a===this._$Ej?.get(e)&&!this.hasAttribute(n._$Eu(e,s))))return;this.C(e,t,s)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:i,wrapped:a},n){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,n??t??this[e]),!0!==a||void 0!==n)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),!0===i&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}const e=this.scheduleUpdate();return null!=e&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[e,t]of this._$Ep)this[e]=t;this._$Ep=void 0}const e=this.constructor.elementProperties;if(e.size>0)for(const[t,s]of e){const{wrapped:e}=s,i=this[t];!0!==e||this._$AL.has(t)||void 0===i||this.C(t,void 0,s,i)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(e=>e.hostUpdate?.()),this.update(t)):this._$EM()}catch(t){throw e=!1,this._$EM(),t}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(e){}firstUpdated(e){}};x.elementStyles=[],x.shadowRootOptions={mode:"open"},x[b("elementProperties")]=new Map,x[b("finalized")]=new Map,_?.({ReactiveElement:x}),(m.reactiveElementVersions??=[]).push("2.1.2");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const k=globalThis,z=e=>e,S=k.trustedTypes,A=S?S.createPolicy("lit-html",{createHTML:e=>e}):void 0,E="$lit$",C=`lit$${Math.random().toFixed(9).slice(2)}$`,T="?"+C,O=`<${T}>`,D=document,H=()=>D.createComment(""),M=e=>null===e||"object"!=typeof e&&"function"!=typeof e,I=Array.isArray,N="[ \t\n\f\r]",L=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,R=/-->/g,P=/>/g,B=RegExp(`>|${N}(?:([^\\s"'>=/]+)(${N}*=${N}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),U=/'/g,j=/"/g,F=/^(?:script|style|textarea|title)$/i,W=(e=>(t,...s)=>({_$litType$:e,strings:t,values:s}))(1),Z=Symbol.for("lit-noChange"),q=Symbol.for("lit-nothing"),G=new WeakMap,K=D.createTreeWalker(D,129);function V(e,t){if(!I(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==A?A.createHTML(t):t}const Y=(e,t)=>{const s=e.length-1,i=[];let a,n=2===t?"<svg>":3===t?"<math>":"",o=L;for(let t=0;t<s;t++){const s=e[t];let r,l,d=-1,c=0;for(;c<s.length&&(o.lastIndex=c,l=o.exec(s),null!==l);)c=o.lastIndex,o===L?"!--"===l[1]?o=R:void 0!==l[1]?o=P:void 0!==l[2]?(F.test(l[2])&&(a=RegExp("</"+l[2],"g")),o=B):void 0!==l[3]&&(o=B):o===B?">"===l[0]?(o=a??L,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,r=l[1],o=void 0===l[3]?B:'"'===l[3]?j:U):o===j||o===U?o=B:o===R||o===P?o=L:(o=B,a=void 0);const h=o===B&&e[t+1].startsWith("/>")?" ":"";n+=o===L?s+O:d>=0?(i.push(r),s.slice(0,d)+E+s.slice(d)+C+h):s+C+(-2===d?t:h)}return[V(e,n+(e[s]||"<?>")+(2===t?"</svg>":3===t?"</math>":"")),i]};class X{constructor({strings:e,_$litType$:t},s){let i;this.parts=[];let a=0,n=0;const o=e.length-1,r=this.parts,[l,d]=Y(e,t);if(this.el=X.createElement(l,s),K.currentNode=this.el.content,2===t||3===t){const e=this.el.content.firstChild;e.replaceWith(...e.childNodes)}for(;null!==(i=K.nextNode())&&r.length<o;){if(1===i.nodeType){if(i.hasAttributes())for(const e of i.getAttributeNames())if(e.endsWith(E)){const t=d[n++],s=i.getAttribute(e).split(C),o=/([.?@])?(.*)/.exec(t);r.push({type:1,index:a,name:o[2],strings:s,ctor:"."===o[1]?se:"?"===o[1]?ie:"@"===o[1]?ae:te}),i.removeAttribute(e)}else e.startsWith(C)&&(r.push({type:6,index:a}),i.removeAttribute(e));if(F.test(i.tagName)){const e=i.textContent.split(C),t=e.length-1;if(t>0){i.textContent=S?S.emptyScript:"";for(let s=0;s<t;s++)i.append(e[s],H()),K.nextNode(),r.push({type:2,index:++a});i.append(e[t],H())}}}else if(8===i.nodeType)if(i.data===T)r.push({type:2,index:a});else{let e=-1;for(;-1!==(e=i.data.indexOf(C,e+1));)r.push({type:7,index:a}),e+=C.length-1}a++}}static createElement(e,t){const s=D.createElement("template");return s.innerHTML=e,s}}function J(e,t,s=e,i){if(t===Z)return t;let a=void 0!==i?s._$Co?.[i]:s._$Cl;const n=M(t)?void 0:t._$litDirective$;return a?.constructor!==n&&(a?._$AO?.(!1),void 0===n?a=void 0:(a=new n(e),a._$AT(e,s,i)),void 0!==i?(s._$Co??=[])[i]=a:s._$Cl=a),void 0!==a&&(t=J(e,a._$AS(e,t.values),a,i)),t}class Q{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:s}=this._$AD,i=(e?.creationScope??D).importNode(t,!0);K.currentNode=i;let a=K.nextNode(),n=0,o=0,r=s[0];for(;void 0!==r;){if(n===r.index){let t;2===r.type?t=new ee(a,a.nextSibling,this,e):1===r.type?t=new r.ctor(a,r.name,r.strings,this,e):6===r.type&&(t=new ne(a,this,e)),this._$AV.push(t),r=s[++o]}n!==r?.index&&(a=K.nextNode(),n++)}return K.currentNode=D,i}p(e){let t=0;for(const s of this._$AV)void 0!==s&&(void 0!==s.strings?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}}class ee{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,i){this.type=2,this._$AH=q,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===e?.nodeType&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=J(this,e,t),M(e)?e===q||null==e||""===e?(this._$AH!==q&&this._$AR(),this._$AH=q):e!==this._$AH&&e!==Z&&this._(e):void 0!==e._$litType$?this.$(e):void 0!==e.nodeType?this.T(e):(e=>I(e)||"function"==typeof e?.[Symbol.iterator])(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==q&&M(this._$AH)?this._$AA.nextSibling.data=e:this.T(D.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:s}=e,i="number"==typeof s?this._$AC(e):(void 0===s.el&&(s.el=X.createElement(V(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(t);else{const e=new Q(i,this),s=e.u(this.options);e.p(t),this.T(s),this._$AH=e}}_$AC(e){let t=G.get(e.strings);return void 0===t&&G.set(e.strings,t=new X(e)),t}k(e){I(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let s,i=0;for(const a of e)i===t.length?t.push(s=new ee(this.O(H()),this.O(H()),this,this.options)):s=t[i],s._$AI(a),i++;i<t.length&&(this._$AR(s&&s._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const t=z(e).nextSibling;z(e).remove(),e=t}}setConnected(e){void 0===this._$AM&&(this._$Cv=e,this._$AP?.(e))}}class te{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,i,a){this.type=1,this._$AH=q,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=a,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=q}_$AI(e,t=this,s,i){const a=this.strings;let n=!1;if(void 0===a)e=J(this,e,t,0),n=!M(e)||e!==this._$AH&&e!==Z,n&&(this._$AH=e);else{const i=e;let o,r;for(e=a[0],o=0;o<a.length-1;o++)r=J(this,i[s+o],t,o),r===Z&&(r=this._$AH[o]),n||=!M(r)||r!==this._$AH[o],r===q?e=q:e!==q&&(e+=(r??"")+a[o+1]),this._$AH[o]=r}n&&!i&&this.j(e)}j(e){e===q?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class se extends te{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===q?void 0:e}}class ie extends te{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==q)}}class ae extends te{constructor(e,t,s,i,a){super(e,t,s,i,a),this.type=5}_$AI(e,t=this){if((e=J(this,e,t,0)??q)===Z)return;const s=this._$AH,i=e===q&&s!==q||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,a=e!==q&&(s===q||i);i&&this.element.removeEventListener(this.name,this,s),a&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class ne{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){J(this,e)}}const oe=k.litHtmlPolyfillSupport;oe?.(X,ee),(k.litHtmlVersions??=[]).push("3.3.3");const re=globalThis;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */let le=class extends x{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,s)=>{const i=s?.renderBefore??t;let a=i._$litPart$;if(void 0===a){const e=s?.renderBefore??null;i._$litPart$=a=new ee(t.insertBefore(H(),e),e,void 0,s??{})}return a._$AI(e),a})(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return Z}};le._$litElement$=!0,le.finalized=!0,re.litElementHydrateSupport?.({LitElement:le});const de=re.litElementPolyfillSupport;de?.({LitElement:le}),(re.litElementVersions??=[]).push("4.2.2");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const ce=e=>(t,s)=>{void 0!==s?s.addInitializer(()=>{customElements.define(e,t)}):customElements.define(e,t)},he={attribute:!0,type:String,converter:y,reflect:!1,hasChanged:w},ue=(e=he,t,s)=>{const{kind:i,metadata:a}=s;let n=globalThis.litPropertyMetadata.get(a);if(void 0===n&&globalThis.litPropertyMetadata.set(a,n=new Map),"setter"===i&&((e=Object.create(e)).wrapped=!0),n.set(s.name,e),"accessor"===i){const{name:i}=s;return{set(s){const a=t.get.call(this);t.set.call(this,s),this.requestUpdate(i,a,e,!0,s)},init(t){return void 0!==t&&this.C(i,void 0,e,t),t}}}if("setter"===i){const{name:i}=s;return function(s){const a=this[i];t.call(this,s),this.requestUpdate(i,a,e,!0,s)}}throw Error("Unsupported decorator location: "+i)};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function pe(e){return(t,s)=>"object"==typeof s?ue(e,t,s):((e,t,s)=>{const i=t.hasOwnProperty(s);return t.constructor.createProperty(s,e),i?Object.getOwnPropertyDescriptor(t,s):void 0})(e,t,s)}
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
function me(e,t){return(t,s,i)=>((e,t,s)=>(s.configurable=!0,s.enumerable=!0,Reflect.decorate&&"object"!=typeof t&&Object.defineProperty(e,t,s),s))(t,s,{get(){return(t=>t.renderRoot?.querySelector(e)??null)(this)}})}const ve=`v${"2026.08.05"}`,fe="smart_irrigation",_e=["de","en","es","fr","it","nl","no","sk"],be="fixed_time",ye=[be,"before_run"],we="precipitation_threshold_mm",$e="sensor_debounce",xe="Open Weather Map",ke="Pirate Weather",ze="Open-Meteo",Se="Met Office",Ae="minutes",Ee="hours",Ce="days",Te="imperial",Oe="metric",De="Dewpoint",He="Evapotranspiration",Me="Humidity",Ie="Precipitation",Ne="Current Precipitation",Le="Pressure",Re="Solar Radiation",Pe="Temperature",Be="Windspeed",Ue="weather_service",je="sensor",Fe="static",We="pressure_type",Ze="absolute",qe="relative",Ge="none",Ke="source",Ve="sensorentity",Ye="static_value",Xe="unit",Je="aggregate",Qe=["average","first","last","maximum","median","minimum","riemannsum","sum","delta"],et="sq ft",tt="l/minute",st="gal/minute",it="s",at="mm",nt="in",ot="inch Hg",rt="mile/h",lt="meter/s",dt="mm/h",ct="in/h",ht="name",ut="size",pt="throughput",gt="state",mt="duration",vt="module",ft="bucket",_t="multiplier",bt="mapping",yt="lead_time",wt="maximum_duration",$t="maximum_bucket",xt="drainage_rate",kt="kc",zt="plant_type",St="linked_entity",At="bucket_threshold",Et="flow_sensor",Ct="flow_counter_type",Tt="watering_mode",Ot="run_service",Dt="duration_field",Ht="duration_unit",Mt="stop_service",It="confirm_entity",Nt="observed_entity",Lt="soil_moisture_sensor",Rt="soil_moisture_threshold",Pt={lawn:.8,vegetables:1,flowers:.9,shrubs:.5,trees:.7,xeriscape:.3},Bt={sand:35,loam:20,silt:10,clay:5},Ut="zone_sequencing",jt="sequential",Ft="parallel",Wt="rotating",Zt="zone_sequencing_max_consecutive_duration",qt="zone_sequencing_min_absorption_time",Gt="master_entity",Kt="master_settle_seconds",Vt="master_kick_enabled",Yt="master_kick_pause_seconds",Xt="master_off_after",Jt="weekly",Qt="monthly",es="interval",ts=["daily",Jt,Qt,es],ss="none",is="time",as="sunrise",ns="sunset",os="solar_azimuth",rs=[ss,is,as,ns,os],ls="start",ds="finish",cs="name",hs="watering_mode",us="inlet_entity",ps="watch_mode",gs="run_service",ms="stop_service",vs="duration_field",fs="duration_unit",_s="confirm_entity",bs="flow_sensor",ys="notify_target",ws="commissioning_confirmed",$s=["count","warn","ignore"],xs="classic",ks="service",zs="opensprinkler",Ss="distributor_id",As="outlet_number",Es=e=>e.callWS({type:fe+"/config"}),Cs=(e,t)=>e.callApi("POST",fe+"/config",t),Ts=e=>e.callWS({type:fe+"/zones"}),Os=(e,t)=>e.callApi("POST",fe+"/zones",t),Ds=e=>e.callWS({type:fe+"/modules"}),Hs=e=>e.callWS({type:fe+"/allmodules"}),Ms=(e,t)=>e.callApi("POST",fe+"/modules",t),Is=e=>e.callWS({type:fe+"/mappings"}),Ns=(e,t)=>e.callApi("POST",fe+"/mappings",t),Ls=(e,t)=>e.callWS({type:fe+"/watering_calendar",zone_id:t}),Rs=(e,t)=>e.callWS({type:fe+"/schedule_save",schedule:t}),Ps=e=>e.callWS({type:fe+"/distributors"}),Bs=(e,t)=>e.callApi("POST",fe+"/distributors",t),Us=e=>e.callWS({type:fe+"/weather_config"}),js=(e,t,s,i)=>e.callWS({type:fe+"/weather_config_save",use_weather_service:t,weather_service:null!=s?s:null,api_key:null!=i?i:null}),Fs=e=>e.callWS({type:fe+"/coordinates"});let Ws=!1,Zs=null;const qs=async()=>{if(Ws&&Zs)return Zs;if(customElements.get("ha-checkbox")&&customElements.get("ha-slider")&&customElements.get("ha-panel-config")&&customElements.get("ha-entity-picker"))return Promise.resolve();Ws=!0,Zs=async function(){try{await new Promise(e=>{"requestIdleCallback"in window?requestIdleCallback(()=>e()):setTimeout(()=>e(),0)}),await customElements.whenDefined("partial-panel-resolver");const e=document.createDocumentFragment(),t=document.createElement("partial-panel-resolver");e.appendChild(t),t.hass={panels:[{url_path:"tmp",component_name:"config"}]},await new Promise(e=>queueMicrotask(()=>e())),t._updateRoutes(),await t.routerOptions.routes.tmp.load(),await customElements.whenDefined("ha-panel-config"),await new Promise(e=>queueMicrotask(()=>e()));const s=document.createElement("ha-panel-config");e.appendChild(s),await s.routerOptions.routes.automation.load(),customElements.get("ha-entity-picker")||await Promise.race([customElements.whenDefined("ha-entity-picker"),new Promise(e=>setTimeout(e,3e3))]),e.textContent=""}catch(e){console.error("Failed to load HA form elements:",e)}}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */();try{await Zs}finally{Ws=!1,Zs=null}};const Gs=1,Ks=2,Vs=3,Ys=4,Xs=e=>(...t)=>({_$litDirective$:e,values:t});class Js{constructor(e){}get _$AU(){return this._$AM._$AU}_$AT(e,t,s){this._$Ct=e,this._$AM=t,this._$Ci=s}_$AS(e,t){return this.update(e,t)}update(e,t){return this.render(...t)}}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */class Qs extends Js{constructor(e){if(super(e),this.it=q,e.type!==Ks)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(e){if(e===q||null==e)return this._t=void 0,this.it=e;if(e===Z)return e;if("string"!=typeof e)throw Error(this.constructor.directiveName+"() called with a non-string value");if(e===this.it)return this._t;this.it=e;const t=[e];return t.raw=t,this._t={_$litType$:this.constructor.resultType,strings:t,values:[]}}}Qs.directiveName="unsafeHTML",Qs.resultType=1;const ei=Xs(Qs);var ti={title:"Smart Irrigation: check flow rate",message_over:"Zone '{zone}' is consistently over-watering: the measured flow is ~{percent}% above the configured rate over {runs} runs. Its valve can't stop early, so consider setting the throughput to about {rate} {unit} (currently {current}).",message_under:"Zone '{zone}' is consistently under-watering: the measured flow is ~{percent}% below the configured rate over {runs} runs. Its valve can't stop early, so consider setting the throughput to about {rate} {unit} (currently {current}).",open_settings:"Open zone settings"},si={loading:"Loading",saving:"Saving",actions:{delete:"Delete",edit:"Edit",save:"Save",cancel:"Cancel",confirm_delete:"Confirm Delete",confirm_delete_zone:"Are you sure you want to delete this zone?"},labels:{module:"Module",no:"No",select:"Select",yes:"Yes",enabled:"Enabled",disabled:"Disabled",before:"before",after:"after",settings:"Settings",bulk_actions:"Bulk Actions"},units:{seconds:"seconds"},attributes:{size:"size",throughput:"throughput",state:"state",bucket:"bucket",last_updated:"last updated",last_calculated:"last calculated",number_of_data_points:"number of data points"},"loading-messages":{configuration:"Loading configuration...",modules:"Loading modules...",general:"Loading..."},"saving-messages":{adding:"Adding...",saving:"Saving..."},errors:{load_failed:"Couldn't load data",save_failed:"Couldn't save changes",delete_failed:"Couldn't delete",action_failed:"Action failed"}},ii={"default-zone":"Default zone","default-mapping":"Default sensor group"},ai={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"Note: this explanation uses '.' as decimal separator, shows rounded and metric values. Module returned Evapotranspiration deficiency ( = et0 * hour_multiplier + precipitation) of","module-returned-evapotranspiration-deficiency-hourly":"Note: this explanation uses '.' as decimal separator, shows rounded and metric values. Evapotranspiration deficiency ( = sum of hourly FAO-56 et0 over the window + precipitation) of","bucket-was":"Bucket was","new-bucket-values-is":"New bucket value is",bucket:"bucket","old-bucket-variable":"old_bucket","max-bucket-variable":"max_bucket",delta:"delta","bucket-less-than-zero-irrigation-necessary":"Since bucket < 0, irrigation is necessary","steps-taken-to-calculate-duration":"To calculate the exact duration, the following steps were taken","precipitation-rate-defined-as":"The precipitation rate is defined as","duration-is-calculated-as":"The duration is calculated as",drainage:"drainage","drainage-rate":"drainage_rate",hours:"hours","precipitation-rate-variable":"precipitation_rate","multiplier-is-applied":"Now, the multiplier is applied. The multiplier is","duration-after-multiplier-is":"hence the duration is","maximum-duration-is-applied":"Then, the maximum duration is applied. The maximum duration is","duration-after-maximum-duration-is":"hence the duration is","lead-time-is-applied":"Finally, the lead time is applied. The lead time is","duration-after-lead-time-is":"hence the final duration is","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Since bucket >= 0, no irrigation is necessary and duration is set to","maximum-bucket-is":"Maximum bucket size is","drainage-rate-is":"Drainage rate when saturated (bucket at max) is","current-drainage-is":"Current drainage is calculated as","drainage-integrated":"the surplus above field capacity drains continuously over the window (Brooks–Corey), so the rate falls as it drains","no-drainage":"Current drainage is 0 because","water-balance-substepped":"The water balance was replayed across the window, so rain, drainage and the maximum bucket clamp were applied at the times they occurred rather than all at the start of the window. Number of steps:","runoff-is":"Water above the maximum bucket that was lost to runoff:","runoff-variable":"runoff","forecast-weighting-applied":"Forecast weighting reduced the deficit for the expected rain","crop-coefficient-applied":"Scaled by the crop coefficient"}}},ni={pyeto:{description:"Calculate duration based on the FAO56 calculation from the PyETO library"},static:{description:"'Dummy' module with a static configurable delta"},passthrough:{description:"Passthrough module that returns the value of an Evapotranspiration sensor as delta"}},oi={general:{cards:{"automatic-duration-calculation":{header:"Automatic duration calculation",description:"Calculation takes collected weather data up to that point and updates the bucket for each automatic zone. Then, the duration is adjusted based on the new bucket value and the collected weather data is removed.",labels:{"auto-calc-enabled":"Automatically calculate irrigation durations","calc-time":"Calculate at","calc-mode":"Calculate"},modes:{fixed_time:"At a fixed time",before_run:"Before each irrigation run"},help:{"before-run":"Durations are calculated when each irrigation schedule plans its run, so a run is sized from weather data minutes old instead of hours old."}},"run-history-logging":{header:"Run history logging",description:"When on, a scheduled run that skips a zone because it currently has no water demand is recorded in that zone's history. Off by default; existing history is unaffected.",labels:{"log-no-demand":'Log "no demand" skips in the run history'}},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Warning: weather data update time on or after calculation time"},header:"Automatic weather data update",description:"Collect and store weather data automatically. Weather data is required to calculate zone buckets and durations.",labels:{"auto-update-enabled":"Automatically update weather data","auto-update-schedule":"Update schedule","auto-update-time":"Update at","auto-update-interval":"Update sensor data every","auto-update-delay":"Update delay"},options:{minutes:"minutes",hours:"hours",days:"days"}},"automatic-clear":{header:"Automatic weather data pruning",description:"Automatically remove collected weather data at a configured time. Use this to make sure that there is no left over weather data from previous days. Don't remove the weather data before you calculate and only use this option if you expect the automatic update to collect weather data after you calculated for the day. Ideally, you want to prune as late in the day as possible.",labels:{"automatic-clear-enabled":"Automatically clear collected weather data","automatic-clear-time":"Clear weather data at"}},continuousupdates:{header:"Continuous updates for sensors (experimental)",description:"This experimental feature will continuously update the sensor data. This is useful for sensor groups that use sources that provide continuous data, such as weather stations. This feature cannot be used for sensor groups that at least partly rely on weather services as continous polling of APIs will incur costs. Keep in mind that this is experimental and may not work as expected. Use at your own risk.",labels:{continuousupdates:"Enable continuous updates",sensor_debounce:"Sensor debounce"}}},description:"This page provides global settings.",title:"General",sections:{weather:"Weather",automation:"Automation",location:"Location",watering:"Watering behavior"}},schedules:{title:"Schedules",description:"Create recurring schedules to automatically irrigate your zones at specific times. No automations needed.",add:"Add Schedule",no_items:"No schedules configured yet. Click 'Add Schedule' to get started.",zones_all:"All zones",zones_specific:"Specific zones",hours:"hours",minutes:"min",types:{daily:"Daily",weekly:"Weekly",monthly:"Monthly",interval:"Every N hours"},actions:{calculate:"Calculate (update irrigation duration)",update:"Update (collect weather data)",irrigate:"Irrigate (run valves directly)"},days:{monday:"Mon",tuesday:"Tue",wednesday:"Wed",thursday:"Thu",friday:"Fri",saturday:"Sat",sunday:"Sun"},fields:{name:"Name",recurrence:"Recurrence",enabled:"Enabled",days_of_week:"Days of week",day_of_month:"Day of month",interval_hours:"Interval",action:"Action",zones:"Zones",start_mode:"Start",start_time:"Start time (optional)",finish_mode:"Finish",finish_time:"Finish time (HH:MM)",anchor:"Pinned to",offset_by:"offset by"},dialog:{add_title:"Add Schedule",edit_title:"Edit Schedule"},sections:{when:"When",zones:"Zones",season:"Season"},season:{label:"Date range",to:"to",note:"Leave both blank to run all year."},summary:{invalid:"This schedule has no start or finish set, so it never runs.",recurrence_daily:"Runs daily",recurrence_weekly:"Runs weekly on {days}",recurrence_monthly:"Runs monthly on day {day}",recurrence_interval:"Runs every {hours} hours",recurrence_interval_at:"Runs every {hours} hours, starting at {time}",zones_all:"all zones",zones_some:"{count, plural, one {# selected zone} other {# selected zones}}",watering:"watering {zones}",start_only:"starting at {when}; every zone runs to completion",finish_only:"finishing at {when}; every zone runs to completion",anchor_finish:"finishing at {finish}, starting as late as possible but never before {start}; zones that don't fit wait for the next run",anchor_start:"starting at {start}, finishing by {finish} at the latest; zones that don't fit wait for the next run",sunrise:"sunrise",sunset:"sunset",offset_before:"{minutes} min before {event}",offset_after:"{minutes} min after {event}",at_azimuth:"solar azimuth {degrees}°"},bound_mode:{none:"No limit",time:"At a time",sunrise:"At sunrise",sunset:"At sunset",solar_azimuth:"At solar azimuth"},anchor:{start:"As early as possible within the window",finish:"As late as possible within the window"},help:{error:"Must set either a start or finish condition",demand_open:"Set by demand. All zones run to completion.",exact:"Exact.",demand_floored:"Set by demand, but never before this.",exact_deferred:"Exact. Zones that don't fit are deferred.",demand_capped_deferred:"Set by demand, but never later than this. Zones that don't fit are deferred."}},setup:{title:"Setup",tabs:{weather_location:"Weather & Location",my_zones:"My Zones",when_to_water:"When to Water",advanced:"Advanced",experimental:"Experimental",distributors:"Distributors"},weather_data:{forecast_title:"Forecast",forecast_none:"Forecast is available when a weather service is enabled.",seasonal_title:"Seasonal outlook"},advanced:{used_by_zones:"Used by {count, plural, one {# zone} other {# zones}}",not_used:"Not used"}},experimental:{title:"Experimental features",warning:"These features are opt-in and still being refined. They change how each zone's bucket is filled, so turn them on one at a time and keep an eye on your zones — you can switch them back off at any time.",forecast_weighting:{title:"Forecast-weighted durations",description:"Instead of skipping a whole run when rain is forecast, water less. The upcoming precipitation (over the look-ahead window set under When to Water) is subtracted from the deficit used to compute the run duration, while the true deficit stays in the bucket so the real rain fills the rest. If the forecast rain misses, the next run makes up the difference. Requires a weather service.",label:"Reduce durations when rain is forecast",note:"Uses the precipitation look-ahead from When to Water. Works alongside the rain-skip guard (a skip still wins over a reduced run)."},observed_watering:{title:"Credit bucket from observed watering",description:"When a zone's linked valve runs outside Smart Irrigation — a manual tap, an automation, your own schedule — its bucket is credited for the water applied, estimated from the run time and the zone's throughput. This keeps the soil-moisture model honest when you water by other means. Smart Irrigation's own runs are already accounted for and are never double-counted.",label:"Credit the bucket when a linked valve runs externally",note:"Requires a linked valve and a throughput on the zone. Volume is estimated (run time × throughput), not metered."},live_estimate:{title:"Live-estimate watering",description:"By default a zone waters once a day, from the deficit the daily calculation produced (for example at 23:00). With this on, each scheduled run instead decides — and sizes itself — from the live intra-day deficit (the drainage-aware ET and rainfall since the last calculation). This lets a zone water more than once a day on real intra-day demand (for example pots on an every-12-hours schedule that the once-daily bucket would otherwise leave dry), and it shrinks or cancels a run that intra-day rain has already covered. The daily ledger is unchanged: after the run the bucket is credited with the water actually delivered, so the next daily calculation never double-counts. Requires a weather service.",label:"Trigger and size each run from the live deficit",note:"Affects scheduled runs only, and can start a run the daily calculation didn't approve. For frequent watering keep a sensible minimum deficit and a maximum bucket of at least a day's ET."},continuous_updates:{title:"Continuous sensor updates",description:"By default, sensor-based weather values are read once per scheduled update (hourly by default), so anything that happened in between is never recorded — the daily minimum and maximum temperature come from those spot readings, and solar radiation is integrated coarsely. With this on, a reading is recorded the moment the sensor changes, which makes the daily aggregates and the resulting evapotranspiration considerably more accurate. Sensor groups that also use a weather service keep their scheduled update for the weather-service values; only the sensor values become continuous. Small changes are ignored, so a noisy sensor does not fill the buffer.",label:"Record sensor readings when they change",debounce_label:"Group changes arriving within (milliseconds)",note:"Applies to sensor groups whose values come from Home Assistant sensors. The grouping delay only postpones the follow-up bookkeeping — no reading is ever dropped by it. Set it to 0 to disable grouping."},hourly_calculation:{title:"Hourly evapotranspiration",description:"By default the FAO-56 equation is run once, over the window's average weather, which cloud cover biases systematically: fed one identical hourly series across 362 days it returns 1.14 times the reference on overcast days and 0.93 times on clear ones. With this on, the equation is run for each hour and the hours are summed, which removes that bias, and the water balance is replayed hour by hour so rain and drainage are booked when they happened instead of all at the start of the window. Expect the daily figure to move by up to 12 percent, in either direction depending on the sky. Needs a Solar Radiation source that is measured rather than estimated, and it is not used on days where a forecast is blended in.",label:"Sum evapotranspiration hour by hour",note:"Independent of continuous sensor updates: scheduled hourly updates carry this too, and a denser buffer makes it more accurate without being required. Any window that cannot be reduced to hourly rows keeps the daily equation, so no series is ever invented."},distributors:{title:"Mechanical water distributors",description:"Drive a mechanical pressure-distributor — for example a Gardena Water Distributor — that splits one supply into several outlets and advances on water on/off pulses. Assign zones to a distributor's outlets and Smart Irrigation waters them in sequence, tracks the position, and coordinates a master valve or pump. This is a new feature that could not be fully hardware-tested, so treat it as a beta.",label:"Enable mechanical water distributors",note:"Watch the first days of use closely and keep the device's manual override handy. You can switch it back off at any time — existing zone watering is unaffected."}},help:{title:"Help",cards:{"how-to-get-help":{title:"How to get help","first-read-the":"First, read the",wiki:"Documentation","if-you-still-need-help":"If you still need help reach out on the","community-forum":"Community forum","or-open-a":"or open a","github-issue":"Github Issue","english-only":"English only"}}},info:{title:"Info",description:"View information about next irrigation and system status.","configuration-not-available":"Configuration not available.",cards:{"zone-bucket-values":{title:"Zone Bucket Values & Duration",labels:{bucket:"Bucket",duration:"Duration"},"no-zones":"No zones configured"},"next-irrigation":{title:"Next Irrigation",labels:{"next-start":"Next start",duration:"Duration",zones:"Zones"},"no-data":"No data available"},"irrigation-reason":{title:"Irrigation Reason",labels:{reason:"Reason",sunrise:"Sunrise","total-duration":"Total duration",explanation:"Explanation"},"no-data":"No data available"},irrigate_now:{title:"Irrigate Now",description:"Immediately start irrigation for all zones that have a linked entity. Skip conditions are ignored.",button_all:"Run all zones now",no_linked_zones:"No zones have a linked switch/valve entity with a calculated duration."}}},mappings:{cards:{"add-mapping":{actions:{add:"Add sensor group"},header:"Add sensor groups"},mapping:{aggregates:{average:"Average",first:"First",last:"Last",maximum:"Maximum",median:"Median",minimum:"Minimum",riemannsum:"Riemann sum",sum:"Sum",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"You cannot delete this sensor group because there is at least one zone using it.",invalid_source:"Invalid source",source_does_not_exist:"Source does not exist. Please enter a valid source, such as 'sensor.mysensor'."},items:{dewpoint:"Dewpoint",evapotranspiration:"Evapotranspiration",humidity:"Humidity","maximum temperature":"Maximum temperature","minimum temperature":"Minimum temperature",precipitation:"Total precipitation","current precipitation":"Current precipitation",pressure:"Pressure","solar radiation":"Solar radiation",temperature:"Temperature",windspeed:"Wind speed"},pressure_types:{absolute:"absolute",relative:"relative"},"pressure-type":"Pressure is","sensor-aggregate-of-sensor-values-to-calculate":"of sensor values to calculate duration","sensor-aggregate-use-the":"Use the","sensor-entity":"Sensor entity",static_value:"Value","input-units":"Input provides values in",source:"Source",sources:{none:"None",weather_service:"Weather service",sensor:"Sensor",static:"Static value"}}},description:"Add one or more sensor groups that retrieve weather data from Weather service, from sensors or a combination of these. You can map each sensor group to one or more zones",labels:{"mapping-name":"Name"},no_items:"There are no sensor group defined yet.",title:"Sensor Groups","weather-records":{title:"Weather Records",timestamp:"Time",temperature:"Temp",humidity:"Hum",dewpoint:"Dew",wind:"Wind",pressure:"Press",precipitation:"Precip","retrieval-time":"Retrieved","no-data":"No weather data available for this sensor group"}},modules:{cards:{"add-module":{actions:{add:"Add module"},header:"Add module"},module:{errors:{"cannot-delete-module-because-zones-use-it":"You cannot delete this module because there is at least one zone using it."},labels:{configuration:"Configuration",required:"indicates a required field"},"translated-options":{DontEstimate:"Do not estimate",EstimateFromSunHours:"Estimate from sun hours",EstimateFromTemp:"Estimate from temperature",EstimateFromSunHoursAndTemperature:"Estimate from average of sun hours and temperature"},fields:{coastal:{name:"Coastal",description:"Enable if the weather station is located near a coast or large body of water. Affects how atmospheric humidity is estimated."},solrad_behavior:{name:"Solar radiation estimation",description:"How solar radiation is estimated when it is not directly measured by a sensor."},forecast_days:{name:"Forecast days",description:"Number of future days to include in the ET calculation. 0 = current weather only (recommended — no extra API calls). Values > 0 average today's ET with forecasted ET for upcoming days (up to 4 days via the OWM free tier)."},delta:{name:"Delta",description:"Static evapotranspiration delta (mm) used directly without any weather-based calculation."}}}},description:"Add one or more modules that calculate irrigation duration. Each module comes with its own configuration and can be used to calculate duration for one or more zones.",no_items:"There are no modules defined yet.",title:"Modules"},zones:{actions:{add:"Add",calculate:"Calculate",information:"Information",update:"Update","reset-bucket":"Reset bucket","view-weather-info":"View weather data","view-weather-info-message":"Weather data available for","view-watering-calendar":"View watering calendar",irrigate_all:"Water all zones now",open_settings:"Edit settings"},cards:{"add-zone":{actions:{add:"Add zone"},header:"Add zone"},"zone-actions":{actions:{"calculate-all":"Recalculate durations","update-all":"Refresh weather data","reset-all-buckets":"Reset all buckets","clear-all-weatherdata":"Clear all weather data"},header:"Actions on all zones"}},description:"Specify one or more irrigation zones here. The irrigation duration is calculated per zone, depending on size, throughput, state, module and sensor group.",labels:{bucket:"Bucket",duration:"Duration","lead-time":"Lead time",mapping:"Sensor Group","maximum-duration":"Maximum duration",multiplier:"Multiplier",name:"Name",size:"Size",state:"State",states:{automatic:"Automatic",disabled:"Disabled",manual:"Manual"},throughput:"Throughput","maximum-bucket":"Maximum bucket",last_calculated:"Last calculated","data-last-updated":"Data last updated","data-number-of-data-points":"Number of data points",drainage_rate:"Drainage rate",linked_entity:"Linked switch/valve/helper entity",opensprinkler_station:"OpenSprinkler station",opensprinkler_station_help:"The station's enabled switch, e.g. switch.front_lawn_station_enabled. HASI queues the run on the controller and then watches that station's own running sensor, so a zone queued behind others is only counted as watering once it really starts. Set the controller's water level to 100% or turn its weather adjustment off, otherwise the weather correction is applied twice.",opensprinkler_no_stations:"No OpenSprinkler stations found. Check that the OpenSprinkler integration is set up and the controller is reachable. You can still type an entity id.",linked_entity_placeholder:"e.g. switch.garden_valve",flow_sensor:"Flow meter sensor (optional)",flow_sensor_placeholder:"e.g. sensor.zone_flow_rate",flow_counter_type:"Counter type",flow_counter_type_help:"How this cumulative flow sensor is read. Auto learns across runs whether the sensor resets each run. Per run: the sensor resets to ~0 each run and shows that run's total (e.g. Sonoff/Zigbee valves). Lifetime: a meter that only ever counts up across all runs (delta per run).",flow_counter_type_auto:"Auto (learn)",flow_counter_type_per_run:"Per run (resets each run)",flow_counter_type_lifetime:"Lifetime total (delta)",watering_mode:"Watering mode",watering_mode_description:"How HASI actuates this zone. Classic: HASI opens the valve and closes it itself with a software timer. Self-closing service: HASI sends the run duration to a self-closing valve via a script (see the shipped valve blueprints) and lets the hardware close itself, so an HA restart mid-run cannot cause continuous irrigation.",watering_modes:{classic:"Classic (HASI opens & closes the valve)",service:"Self-closing service (valve closes itself)",opensprinkler:"OpenSprinkler station (controller runs the queue)"},run_service:"Run service",run_service_help:"Service HASI calls to start the run (e.g. a script.* or a switch/valve service). It receives the duration field below plus zone_id and zone_name.",duration_field:"Duration field",duration_field_placeholder:"e.g. dauer",duration_field_help:"Name of the parameter that carries the run length in the call to your run service. The shipped valve blueprints use 'duration' (the default); a custom script may use another name (e.g. 'dauer').",duration_unit:"Duration unit",duration_units:{seconds:"Seconds",minutes:"Minutes"},duration_unit_help:"Unit your hardware expects for the run length. Check the device: many Zigbee/Tuya valves count in MINUTES. The wrong unit over- or under-waters by 60x. In Minutes mode HASI rounds up to whole minutes (minimum 1).",stop_service:"Stop service (optional)",stop_service_help:"Optional. Service HASI calls to close the valve when you stop the zone early, before its own timer expires. Leave empty if the valve cannot be stopped manually.",confirm_entity:"Confirm entity (optional)",confirm_entity_help:"Optional. The real valve/switch entity the run service drives (e.g. a valve or switch) — it holds a steady on-state while watering. If set, HASI verifies the open against it (poll only, it never re-actuates) and flags a problem plus skips the bucket credit if it never turns on. Leave empty to treat the run as write-only and credit optimistically (the hardware owns the close). When in doubt, leave it empty: it only helps with an entity that reports its on-state reliably — a valve that reports late (e.g. a sleepy Zigbee valve) could be read as 'off' and wrongly skip the credit, so the zone would water again next run. Do NOT point this at the run script itself — a fire-and-forget script is not a valid state signal.",observed_entity:"Observed valve/switch (optional)",observed_entity_help:"If Observed watering is on, external runs of this valve/switch (a manual tap, an automation) credit this zone's water storage. Leave empty to not observe this zone.",soil_moisture_sensor:"Soil-moisture sensor (optional)",soil_moisture_sensor_help:"Optional. A sensor reporting this zone's soil moisture in percent (higher = wetter). With a skip threshold set below, an automatic run skips this zone whenever the reading is above the threshold and resets the zone's bucket. Leave empty to disable. An unavailable or non-numeric reading never blocks watering (fail-open).",soil_moisture_threshold:"Skip above soil moisture (%)",soil_moisture_threshold_help:"On an automatic run, skip this zone (and reset its bucket to 0) when the soil-moisture sensor reads strictly above this percentage. Needs a soil-moisture sensor set above. Only affects scheduled runs; manual runs always water.",irrigate_now:"Irrigate Now",bucket_threshold:"Minimum deficit to irrigate",plant_type:"Plant type",kc:"Crop coefficient (Kc)",plant_types:{custom:"Custom (set Kc manually)",lawn:"Lawn / turf",vegetables:"Vegetable garden",flowers:"Flower bed",shrubs:"Shrubs",trees:"Trees",xeriscape:"Xeriscape / drought-tolerant"},soil_type:"Soil type",soil_types:{custom:"Custom (set rate manually)",sand:"Sandy (fast draining)",loam:"Loam (balanced)",silt:"Silt (slow draining)",clay:"Clay (very slow draining)"},distributor:"Water distributor",distributor_help:"Assign this zone to an outlet of a mechanical water distributor. The distributor's inlet valve and its pulse-advance sequence then water this zone, so the zone's own valve and schedule below are managed by the distributor.",distributor_none:"None (own valve)",outlet_number:"Outlet number",distributor_managed_note:"This zone is watered through a distributor (outlet above). Its valve, inlet control and flow sensor are managed by the distributor and hidden here — only the calculation and soil-moisture veto settings remain. To give the zone its own valve again, set the distributor above to “None (own valve)”.",outlet_number_readonly_help:"Which outlet of the distributor feeds this zone. Set on the distributor page — open it with the button.",configure_on_distributor:"Configure on distributor"},no_items:"There are no zones defined yet.",title:"Zones",status:{decision_disabled:"Turned off — this zone won't be watered automatically.",decision_water:"Watering needed: about {duration} on the next scheduled run.",decision_water_at:"Will water about {duration} at {time}.",decision_water_skip:"Deficit ~{duration}, but the next run will likely be skipped ({reason}).",decision_water_no_schedule:"Deficit ~{duration} — no schedule waters this zone; trigger it manually.",decision_no_water:"No watering needed right now — the soil has enough moisture.",decision_unknown:"Not calculated yet — press Update, then Calculate to check.",last_checked:"Last checked",never:"never",saved:"Saved",estimate_now:"Now",estimate_tag:"est.",estimate_method:{hourly:"Live estimate from hourly weather since the last calculation",hourly_sensor:"Live estimate from hourly sensor readings since the last calculation",proxy:"Estimate distributed from today's forecast since the last calculation"}},fault:{title:"Last run failed",valve_no_response:"The valve didn't respond — no water was delivered, so the bucket was left unchanged.",flow_never_started:"No flow was detected — no water was delivered, so the bucket was left unchanged.",station_never_ran:"The OpenSprinkler controller never ran the station — no water was delivered, so the bucket was left unchanged.",station_unresolved:"The OpenSprinkler station could not be found — the run was not started, so the bucket was left unchanged.",station_wrong_mode:"An OpenSprinkler station is linked, but the zone's watering mode is not OpenSprinkler station — the run was refused, so the bucket was left unchanged.",generic:"The last irrigation run failed."},skip:{title:"Skipped",soil_moisture:"Soil moisture {observed} % > {threshold} %"},clamped:{title:"Duration capped",detail:"This zone needs longer than its maximum duration of {maximum}, so part of the deficit is left unwatered on every run. Deepening the bucket threshold has no effect until the cap is raised."},help:{bucket:"Soil-moisture balance. A negative value means the soil is dry and the zone needs water.",calculate:"Works out how long to water from the latest data. Run this after Update.",update:"Fetches the latest weather/sensor data for this zone.",irrigate_link_entity:"Link a switch/valve in this zone's settings to enable manual watering.",irrigate_all:"Opens the linked valves now for every zone with a deficit. Skip conditions (rain, wind, temperature) are ignored.",update_all:"Collects the latest weather/sensor data for all zones. Does not change durations on its own.",calculate_all:"Recomputes each automatic zone's watering duration from the data collected so far."},outlook:{next_run:"Next run",estimated:"estimated",estimated_help:"The start time is still a projection: the run is sized from the water demand read shortly before it begins, so this time moves until then.",no_schedule:"No automatic schedule — zones water only when you trigger them.",setup_schedule:"Set up a schedule",targets_all:"all zones",targets_zones:"{count} zones",will_skip:"Next run will likely be skipped",will_run:"Conditions look clear for the next run.",why_skipped:"Why?",provisional:"forecast — may change",active_guards:"Active guards",last_run:"Last run",last_run_skipped:"skipped",last_run_ran:"ran",today:"today",tomorrow:"tomorrow",actions:{irrigate:"Water",calculate:"Recalculate",update:"Refresh data"},checks:{precipitation:"Rain forecast",days_between:"Days between watering",temperature:"Low temperature",wind:"High wind",rain_sensor:"Rain sensor",freeze:"Frost",paused:"Paused (rain delay)",soil_moisture:"Soil moisture",no_demand:"No water demand"},check_detail:{precipitation:"{observed} mm (≥ {threshold} mm)",days_between:"{observed}/{threshold} days",temperature:"{observed}° (below {threshold}°)",wind:"{observed} (above {threshold})",rain_sensor:"{observed}",freeze:"{observed}° (below {threshold}°)"}},calendar:{no_data:"No watering calendar data available for this zone.",error_prefix:"Error generating calendar:",month:"Month",et:"ET (mm)",precipitation:"Precipitation (mm)",watering:"Watering (L)",avg_temp:"Avg Temp (°C)",method_prefix:"Method:"},confirm_action:{reset_bucket_title:"Reset this zone's bucket?",reset_bucket_body:"This sets the bucket back to 0, discarding the accumulated moisture balance for this zone.",reset_all_buckets_title:"Reset all buckets?",reset_all_buckets_body:"This sets every zone's bucket back to 0, discarding the accumulated moisture balance. Watering calculations start fresh from the next update.",clear_weather_title:"Clear all weather data?",clear_weather_body:"This deletes all collected weather and sensor records for every zone. Zones will need fresh data before they can calculate again."},confirm_irrigate:{title:"Start irrigation?",body:"This opens the linked valve(s) now and bypasses all skip conditions (rain, temperature, minimum days between watering).",all_linked_zones:"All linked zones",toast_started:"Irrigation started",toast_failed:"Irrigation failed"},history:{title:"Run history",total_used:"Total water used",empty:"No runs recorded yet.",when:"When",result:"Result",volume:"Volume",detail:"Detail",results:{completed:"Completed",partial:"Partial",failed:"Failed",skipped:"Skipped",observed:"Observed"}},rain_delay:{title:"Pause watering",paused:"Paused",until:"until",delay_24h:"Delay 24 h",delay_48h:"Delay 48 h",resume:"Resume"},run_zone:{run:"Run",minutes:"min",help:"Water this zone for a custom time, ignoring the calculation",toast_started:"Started run",busy_hint:"Distributor is running — you can start again once it is back in its home position."},stop_zone:{stop:"Stop",watering:"Watering…",toast_stopped:"Stopped run"}},distributors:{title:"Distributors",description:"Mechanical water distributors split one supply into several outlets, advanced by pulsing the water on and off.",no_items:"No distributors configured yet.",add:{header:"Add distributor",name_placeholder:"Distributor name",actions:{add:"Add"}},status:{saved:"Saved"},confirm_delete:"Delete this distributor? Zones assigned to it keep their outlet numbers but lose their distributor link.",labels:{name:"Name",watering_mode_help:"How the distributor's inlet valve is opened and closed.",inlet_entity:"Inlet valve / switch (optional)",inlet_entity_help:"The switch or valve entity that opens the water supply into the distributor. It is also watched for foreign pulses; once a valve is selected, a setting appears below to control the reaction.",watch_inlet:"Watch inlet valve for manual pulses",watch_inlet_help:"Only detects valve switches Home Assistant can see — purely mechanical pulses at the device stay invisible.",inlet_entity_help_service:"The ring valve Home Assistant watches for foreign pulses to keep the outlet position in sync (e.g. when the valve is opened manually or by an automation outside a HASI run). Once a valve is selected, a setting appears below to control the reaction. Actuation is via the run/stop service; this field is only read, and is NOT the flow/confirm sensor. Leave empty to disable inlet watching.",watch_mode:"On a manual inlet pulse",watch_mode_help:"How to react when the inlet valve is opened outside a Home Assistant run (only pulses Home Assistant can see).",watch_mode_count:"Count it (advance the position)",watch_mode_warn:"Warn (mark position uncertain)",watch_mode_ignore:"Ignore",run_service:"Run script",run_service_help:"Script called to open the inlet. It receives the pulse duration.",stop_service:"Stop script (optional)",stop_service_help:"Script called to close the inlet.",duration_field:"Duration field",duration_field_help:"Name of the field the run script expects the duration in.",duration_field_placeholder:"duration",duration_unit:"Duration unit",duration_units:{seconds:"Seconds",minutes:"Minutes"},confirm_entity:"Confirmation sensor (optional)",confirm_entity_help:"Optional sensor on the distributor inlet confirming water actually flows (e.g. a flow or valve-position sensor). If it reports no flow when an outlet opens, the cycle halts safely and marks the distributor uncertain — this is the low-flow / fault detection.",flow_sensor:"Flow sensor (optional)",flow_sensor_help:"The shared inlet flow-rate meter (e.g. L/min, m³/h). When set, the actual delivered volume per outlet is measured and credited instead of the time estimate. Optional. Where the valve can be stopped (a classic inlet, or a self-closing stop-service), the outlet also stops early once its target volume is reached. Both an instantaneous rate meter (e.g. L/min) and a cumulative totalizer counter (e.g. m³, or state_class: total_increasing) are supported and detected automatically from the unit.",pause_seconds:"Advance pause",skip_pulse_seconds:"Skip pulse",notify_target:"Notification target (optional)",notify_target_help:"Optional additional channel. Halts always appear in the Home Assistant notifications panel; set a notify service here (e.g. notify.mobile_app_phone) to also push them there.",notify_target_placeholder:"notify.mobile_app_phone"},notify:{halted:"Distributor '{name}' halted ({reason}). Re-sync and re-confirm required.",reason:{valve_did_not_open:"valve did not open",restart_mid_advance:"restarted mid-advance",foreign_inlet_pulse:"manual inlet pulse"}},commissioning:{title:"Commissioning",outlet:"Outlet",states:{synced:"Synced",uncertain:"Uncertain"},test_run:"Test run",test_run_help:"Waters each mapped outlet for about 30 seconds in order, so you can watch the device advance and note the pause it needs.",set_outlet:"Set current outlet",set_outlet_help:"Read the outlet number shown in the device window and set it here to re-sync the tracked position.",resync_home:"Reset to outlet 1",confirm_resync:{title:"Reset to outlet 1?",body:"This sets the tracked position to outlet 1. Only confirm if the device is physically at outlet 1 — otherwise the distributor will water the wrong outlets (an undetected desync)."},confirm_set_outlet:{title:"Set current outlet?",body:"This marks the distributor as synced at the outlet you entered. Only confirm if the device's window physically shows that outlet right now — a wrong value silently waters the wrong outlets."},confirmed:"Commissioning confirmed",confirmed_help:"Arms the distributor for automatic and manual cycles. Can only be set while the position is synced, and drops to off automatically if the position ever becomes uncertain.",needs_sync:"Set the position to synced before you can arm this distributor.",run_now:"Run now",run_now_help:"Runs one full manual cycle over all mapped outlets.",run_now_active:"A cycle is already running.",confirm_dialog:{title:"Arm this distributor?",body:"Confirm the device is physically at outlet 1 and every outlet is mapped to the right zone. Automatic and manual cycles will start pulsing the inlet.",confirm:"Confirm & arm"}},hints:{pressure:"Give the distributor at least 1 bar of water pressure and 20 l/h of flow. Mechanical distributors need a firm pulse to advance reliably.",below_floor_pause:"Very short pause. The advance pulse must be long enough for the distributor to actually step; the backend enforces a minimum of 10 seconds.",below_floor_skip:"Very short skip pulse. The backend enforces a minimum of 10 seconds.",undetectable:"The device's manual selector button cannot be read back. If you turn it by hand, use “Set current outlet” afterwards so the tracked position matches.",outlet_change:"Changing an outlet mapping moves the device off its known position. Re-sync and re-confirm commissioning before the next cycle.",parallel_draw:"Parallel sequencing opens several zones at once, but a distributor feeds one outlet at a time, so its mapped zones still water in sequence. Plan the supply draw accordingly.",master_off_after:"With sequential or rotating sequencing and “master off after each zone”, the pump is switched per outlet, so expect it to cycle between every outlet of the distributor.",experimental:"Experimental feature — still being refined and not fully hardware-tested. Watch the first days of use closely and keep the device's manual override within reach."},outlets:{title:"Outlets / zones",help:"Set how many outlets the distributor has, then assign a zone to each. Only zones without their own valve or script can be assigned — a zone is either on a distributor or has its own valve. The number of outlets equals the number of assigned zones, numbered contiguously from 1.",count:"Number of outlets",none:"— none",no_zones:"No zones yet. Create zones first (Setup → Zones), then assign them here.",gap_warning:"Outlets must be filled contiguously from 1 — assign a zone to every outlet up to the highest used one."}}},ri="Smart Irrigation",li={title:"Weather Service",description:"Configure which weather service to use for ET calculations and skip conditions.",enabled_label:"Enable weather service",service_label:"Weather service",api_key_label:"API key",api_key_placeholder:"Leave blank to keep existing key",api_key_configured:"API key is configured",api_key_not_configured:"No API key configured",api_key_help:"An API key from your chosen weather service provider. Open-Meteo does not require a key. OpenWeatherMap, Pirate Weather and the Met Office (Weather DataHub) all offer free tiers.",no_api_key_needed:"Open-Meteo is a free service and requires no API key.",save_button:"Save weather settings",saved:"Weather settings saved",owm:"OpenWeatherMap",pw:"Pirate Weather",openmeteo:"Open-Meteo (free, no key needed)",met:"Met Office (UK)",test_button:"Test Connection",test_button_testing:"Testing…",test_success:"✓ Connection successful",test_error_invalid_auth:"✗ Invalid API key — check that it is correct and active",test_error_cannot_connect:"✗ Cannot connect — check your internet connection",test_error_no_service:"✗ Select a weather service first",test_error_unknown:"✗ Test failed — unknown error"},di={title:"Irrigation Start Triggers",description:"Configure when irrigation should start based on solar events. You can add multiple triggers for different schedules. For sunrise triggers, leaving offset at 0 will automatically use the total duration of all enabled zones.",add_trigger:"Add Trigger",edit_trigger:"Edit Trigger",delete_trigger:"Delete Trigger",trigger_types:{sunrise:"Sunrise",sunset:"Sunset",solar_azimuth:"Solar Azimuth"},fields:{name:{name:"Trigger Name",description:"A descriptive name to identify this trigger"},type:{name:"Trigger Type",description:"The type of solar event to trigger on"},enabled:{name:"Enabled",description:"Whether this trigger is currently active"},offset_minutes:{name:"Offset (minutes)",description:"Minutes before (-) or after (+) the solar event. For sunrise triggers, use 0 for automatic timing based on total zone duration."},azimuth_angle:{name:"Azimuth Angle (degrees)",description:"Solar azimuth angle in degrees where 0=North, 90=East, 180=South, 270=West"},account_for_duration:{name:"Account for Duration",description:"When enabled, irrigation will start early enough to finish at the specified time. When disabled, irrigation will start exactly at the specified time."}},dialog:{add_title:"Add Irrigation Start Trigger",edit_title:"Edit Irrigation Start Trigger",cancel:"Cancel",save:"Save",delete:"Delete"},no_triggers:"No irrigation start triggers configured. The system will use the default behavior (sunrise with total zone duration). Add triggers to customize when irrigation starts.",offset_auto:"Auto (calculated from total zone duration)",confirm_delete:"Are you sure you want to delete the trigger '{name}'?",validation:{name_required:"Trigger name is required",azimuth_invalid:"Azimuth angle must be a valid number"},help:{sunrise_offset:"For sunrise triggers: Use negative values to start before sunrise, positive to start after. Set to 0 to automatically start early enough to complete all zones before sunrise.",sunset_offset:"For sunset triggers: Use negative values to start before sunset, positive to start after sunset.",azimuth_explanation:"Solar azimuth is the compass direction of the sun. 0°=North, 90°=East, 180°=South, 270°=West. You can enter any angle value (e.g., 450° = 90°, -30° = 330°). Use this to trigger irrigation when the sun reaches a specific position.",multiple_triggers:"You can configure multiple triggers. Each enabled trigger will independently schedule irrigation starts."}},ci={title:"Skip Conditions",description:"Automatically skip irrigation when conditions are unfavorable. Precipitation check requires a weather service. Temperature and wind checks also require a weather service.",threshold_label:"Precipitation Threshold",threshold_description:"Minimum total precipitation (in mm) forecast across the look-ahead window to skip irrigation.",lookahead_label:"Forecast look-ahead (days)",lookahead_help:"How many upcoming forecast days to add up when checking for rain. The forecast starts at tomorrow (today is excluded), so 1 = just the next day, 2 = the next two days, and so on.",temp_section_title:"Skip on low temperature",temp_threshold_label:"Skip if temperature is below",wind_section_title:"Skip on high wind speed",wind_threshold_label:"Skip if wind speed is above",rain_sensor_section_title:"Skip on rain sensor",rain_sensor_label:"Rain sensor entity (optional)",rain_sensor_placeholder:"e.g. binary_sensor.rain",freeze_section_title:"Skip on frost",freeze_threshold_label:"Skip if minimum temperature is below",freeze_help:"Compares the current temperature and the coming night's forecast low; skips watering when frost is expected, to protect pipes and plants.",forecast_rain_label:"When rain is forecast",forecast_rain_options:{ignore:"Ignore it",water_less:"Water less",skip:"Skip watering"},forecast_rain_help:{ignore:"Forecast rain is ignored; runs use the calculated duration.",water_less:"Upcoming forecast rain trims the run duration (the deficit stays in the bucket for the real rain to fill).",skip:"Skip the run entirely when enough rain is forecast within the look-ahead window."}},hi={title:"Location Coordinates",description:"Configure location coordinates for weather data retrieval. You can use manual coordinates different from your Home Assistant location if needed.",manual_enabled:"Use manual coordinates",use_ha_location:"Use Home Assistant location",latitude:"Latitude (decimal degrees)",longitude:"Longitude (decimal degrees)",elevation:"Elevation (meters above sea level)",current_ha_coords:"Current Home Assistant coordinates"},ui={title:"Days Between Irrigation",description:"Configure the minimum number of days that must pass between irrigation events. This helps control watering frequency for water conservation and plant health management.\n\nTypical real-world use cases:\n• Lawn care: 1-2 day intervals prevent overwatering\n• Drought restrictions: 6+ day intervals for weekly watering\n• Deep-rooted plants: 3-7 day intervals for less frequent watering\n• Water conservation: Customizable based on climate and soil conditions",label:"Minimum days between irrigation",help_text:"Set to 0 to disable this feature. Values from 1-365 days are supported. This setting works alongside existing precipitation forecasting logic."},pi={title:"Zone Sequencing",description:"When multiple zones need irrigation, choose whether they run at the same time or one after another. Sequential mode waits for each zone to finish before starting the next. Rotating mode cycles through zones, giving each one a limited consecutive run before moving to the next.",parallel:"Parallel (all zones at once)",sequential:"Sequential (one zone at a time)",rotating:"Rotating (zones take turns)",max_consecutive_duration_label:"Max consecutive run time per zone",max_consecutive_duration_unit:"minutes",min_absorption_time_label:"Min. absorption time between slots",min_absorption_time_unit:"minutes (0 = disabled)"},gi={title:"Pump / master switch",description:"Optional. Powers a shared master — a pump or main valve — on before the first zone of a watering cycle, then optionally off after the last zone. Leave the entity empty to never touch a master (e.g. a pressure-controlled waterworks that starts on its own).",entity:"Master entity (switch/valve)",kick_enabled:"Kicker: pulse off then on to force a pump start",kick_pause:"Kick pause (off before on)",settle:"Settle delay before the first zone",off_after:"Turn the master off after irrigation",seconds_unit:"seconds"},mi={zone_size:"The total irrigated area of this zone. Used with throughput to calculate how much water is applied per run.",zone_throughput:"Total water flow of your irrigation system for this zone (litres/min in metric, gal/min in imperial). Check your sprinkler datasheet or measure by timing how long it takes to fill a known container.",zone_drainage_rate:"How fast saturated soil drains excess water. ~20 mm/h suits medium/loam soil; lower (2–10) for heavy clay, higher for sandy soil.",zone_bucket:"Current water deficit (negative) or surplus (positive) for this zone. Irrigation triggers when bucket drops below the threshold.",zone_maximum_bucket:"Maximum moisture surplus the zone can hold. Water above this level is treated as runoff. Typical value: 50 mm.",zone_bucket_threshold:"Irrigation triggers when the bucket drops below this value. Must be 0 or negative. 0 means irrigate whenever there is any deficit.",zone_multiplier:"Scale factor applied to the calculated duration. Use above 1.0 to increase, below 1.0 to decrease. Useful for fine-tuning without changing physical measurements.",zone_lead_time:"Extra seconds added before irrigation starts. Use for pump warm-up or system pressurisation.",zone_maximum_duration:"Hard cap on any single irrigation run in seconds. Prevents runaway watering. Default: 3600 s (1 hour).",zone_linked_entity:"The HA switch, valve or input_boolean (helper) entity controlling water flow for this zone. This entity is turned on when irrigation runs.",zone_flow_sensor:"Optional sensor measuring actual water flow rate. Used for reporting only — does not affect duration calculations.",general_autoupdatedelay:"Seconds to wait after HA starts before the first weather data fetch. Allows other integrations to initialise first.",general_sensor_debounce:"Minimum gap in milliseconds between sensor readings to filter noise from rapidly changing sensors.",general_calctime:"Time of day when irrigation durations are recalculated from collected weather data. Format: HH:MM (24-hour).",general_cleardatatime:"Time of day when old weather data is purged. Must be set later than the calculation time.",general_days_between:"Minimum days between irrigation events for the same zone. Set to 0 to disable (irrigate whenever deficit exists).",general_autoupdateinterval:"How often weather data is collected. Choose a value that balances fresh data against API rate limits.",general_precipitation_threshold:"Irrigation is skipped if total forecast precipitation across the look-ahead window exceeds this amount.",general_temp_threshold:"Irrigation is skipped if the current temperature is below this value (e.g. to prevent frost damage).",general_wind_threshold:"Irrigation is skipped if wind speed exceeds this value (high winds reduce efficiency and cause drift).",zone_plant_type:"Pick a plant type to set a typical crop coefficient, or choose Custom to enter Kc yourself.",zone_kc:"Scales reference (grass) ET to this zone's plants. 1.0 = reference grass; lower for drought-tolerant planting, higher for thirsty crops. Only the ET term is scaled — rain is not.",zone_soil_type:"Pick a soil type to set a typical drainage rate, or leave Custom to enter it by hand below.",distributor_pause_seconds:"Off-time between outlets. This is the pulse that advances the distributor to the next outlet; set it from what you saw during the test run. Minimum 10 seconds.",distributor_skip_pulse_seconds:"Short on/off pulse used to step past an outlet that has no zone mapped, without watering it. Minimum 10 seconds."},vi={title:"Setup Wizard",open_button:"Setup Wizard",close:"Close",next:"Next",back:"Back",finish:"Finish",skip_step:"Skip this step",step_indicator:"Step {current} of {total}",stepper:{weather:"Weather",module:"Module",mapping:"Sensor Group",zone:"Zone"},setup_complete_banner:"Setup not complete. Run the wizard to get started.",open_wizard:"Open Wizard",steps:{welcome:{title:"Welcome to Smart Irrigation",intro:"This wizard guides you through the four steps needed to get your first zone irrigating automatically.",step1_label:"Weather Service — where to get weather data",step2_label:"Calculation Module — how irrigation duration is computed",step3_label:"Sensor Group — which data sources to use",step4_label:"Zone — your first irrigation zone",tip:"You can skip any step and configure it later from the Setup tab."},weather:{title:"Weather Service",description:"Choose how to get weather data. Open-Meteo is free and requires no API key — it is the easiest choice for most users."},module:{title:"Calculation Module",description:"A module calculates how long to irrigate based on evapotranspiration (ET). The PyETO module (FAO-56 method) is recommended for most users.",pick_label:"Select module type",no_modules:"No module types available."},mapping:{title:"Sensor Group",description:"A sensor group links each weather variable to a data source. Set the key variables below — you can refine individual sensor mappings later from the Setup → Sensor Groups tab.",name_label:"Sensor group name",source_label:"Data source for",use_weather_service:"Weather service",use_sensor:"Sensor",use_static:"Static value",use_none:"None / not used"},zone:{title:"First Zone",description:"A zone is one irrigation area (e.g. lawn, garden bed). Set the physical properties so the system can calculate the correct irrigation duration.",name_label:"Zone name",size_label:"Area",throughput_label:"Sprinkler throughput",entity_label:"Linked switch, valve or helper",entity_placeholder:"e.g. switch.garden_valve",module_label:"Calculation module",mapping_label:"Sensor group"},done:{title:"Setup Complete!",description:"Your first zone is ready. Smart Irrigation will now calculate irrigation durations automatically based on weather data.",next_steps:"What you can do next:",tip1:"Go to Zones to view calculated durations and bucket values.",tip2:"Add more zones from the Zones tab.",tip3:"Refine all settings from the Setup tab.",go_zones:"Go to Zones",go_setup:"Go to Setup",schedule_name:"Daily",schedule_title:"Create a watering schedule",schedule_desc:"Your system is configured, but it won't water until a schedule exists. Create a daily schedule for all zones now (you can change or remove it later under Setup → When to Water).",schedule_create:"Create daily schedule",schedule_created:"Daily schedule created."}},confirm_close:{body:"Close the setup wizard? Your progress so far is saved.",keep:"Keep editing",close:"Close"}},fi={flow_calibration:ti,common:si,defaults:ii,module:ai,calcmodules:ni,panels:oi,title:ri,weather_service_config:li,irrigation_start_triggers:di,weather_skip:ci,coordinate_config:hi,days_between_irrigation:ui,zone_sequencing:pi,master:gi,field_help:mi,wizard:vi},_i=Object.freeze({__proto__:null,calcmodules:ni,common:si,coordinate_config:hi,days_between_irrigation:ui,default:fi,defaults:ii,field_help:mi,flow_calibration:ti,irrigation_start_triggers:di,master:gi,module:ai,panels:oi,title:ri,weather_service_config:li,weather_skip:ci,wizard:vi,zone_sequencing:pi});function bi(e,t){const s=t&&t.cache?t.cache:Si,i=t&&t.serializer?t.serializer:ki;return(t&&t.strategy?t.strategy:xi)(e,{cache:s,serializer:i})}function yi(e,t,s,i){const a=null==(n=i)||"number"==typeof n||"boolean"==typeof n?i:s(i);var n;let o=t.get(a);return void 0===o&&(o=e.call(this,i),t.set(a,o)),o}function wi(e,t,s){const i=Array.prototype.slice.call(arguments,3),a=s(i);let n=t.get(a);return void 0===n&&(n=e.apply(this,i),t.set(a,n)),n}function $i(e,t,s,i,a){return s.bind(t,e,i,a)}function xi(e,t){return $i(e,this,1===e.length?yi:wi,t.cache.create(),t.serializer)}const ki=function(){return JSON.stringify(arguments)};var zi=class{constructor(){this.cache=Object.create(null)}get(e){return this.cache[e]}set(e,t){this.cache[e]=t}};const Si={create:function(){return new zi}},Ai={variadic:function(e,t){return $i(e,this,wi,t.cache.create(),t.serializer)}},Ei=/(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;function Ci(e){const t={};return e.replace(Ei,e=>{const s=e.length;switch(e[0]){case"G":t.era=4===s?"long":5===s?"narrow":"short";break;case"y":t.year=2===s?"2-digit":"numeric";break;case"Y":case"u":case"U":case"r":throw new RangeError("`Y/u/U/r` (year) patterns are not supported, use `y` instead");case"q":case"Q":throw new RangeError("`q/Q` (quarter) patterns are not supported");case"M":case"L":t.month=["numeric","2-digit","short","long","narrow"][s-1];break;case"w":case"W":throw new RangeError("`w/W` (week) patterns are not supported");case"d":t.day=["numeric","2-digit"][s-1];break;case"D":case"F":case"g":throw new RangeError("`D/F/g` (day) patterns are not supported, use `d` instead");case"E":t.weekday=4===s?"long":5===s?"narrow":"short";break;case"e":if(s<4)throw new RangeError("`e..eee` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][s-4];break;case"c":if(s<4)throw new RangeError("`c..ccc` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][s-4];break;case"a":t.hour12=!0;break;case"b":case"B":throw new RangeError("`b/B` (period) patterns are not supported, use `a` instead");case"h":t.hourCycle="h12",t.hour=["numeric","2-digit"][s-1];break;case"H":t.hourCycle="h23",t.hour=["numeric","2-digit"][s-1];break;case"K":t.hourCycle="h11",t.hour=["numeric","2-digit"][s-1];break;case"k":t.hourCycle="h24",t.hour=["numeric","2-digit"][s-1];break;case"j":case"J":case"C":throw new RangeError("`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead");case"m":t.minute=["numeric","2-digit"][s-1];break;case"s":t.second=["numeric","2-digit"][s-1];break;case"S":case"A":throw new RangeError("`S/A` (second) patterns are not supported, use `s` instead");case"z":t.timeZoneName=s<4?"short":"long";break;case"Z":case"O":case"v":case"V":case"X":case"x":throw new RangeError("`Z/O/v/V/X/x` (timeZone) patterns are not supported, use `z` instead")}return""}),t}const Ti=/[\t-\r \x85\u200E\u200F\u2028\u2029]/i;function Oi(e){return e.replace(/^(.*?)-/,"")}const Di=/^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g,Hi=/^(@+)?(\+|#+)?[rs]?$/g,Mi=/(\*)(0+)|(#+)(0+)|(0+)/g,Ii=/^(0+)$/;function Ni(e){const t={};return"r"===e[e.length-1]?t.roundingPriority="morePrecision":"s"===e[e.length-1]&&(t.roundingPriority="lessPrecision"),e.replace(Hi,function(e,s,i){return"string"!=typeof i?(t.minimumSignificantDigits=s.length,t.maximumSignificantDigits=s.length):"+"===i?t.minimumSignificantDigits=s.length:"#"===s[0]?t.maximumSignificantDigits=s.length:(t.minimumSignificantDigits=s.length,t.maximumSignificantDigits=s.length+("string"==typeof i?i.length:0)),""}),t}function Li(e){switch(e){case"sign-auto":return{signDisplay:"auto"};case"sign-accounting":case"()":return{currencySign:"accounting"};case"sign-always":case"+!":return{signDisplay:"always"};case"sign-accounting-always":case"()!":return{signDisplay:"always",currencySign:"accounting"};case"sign-except-zero":case"+?":return{signDisplay:"exceptZero"};case"sign-accounting-except-zero":case"()?":return{signDisplay:"exceptZero",currencySign:"accounting"};case"sign-never":case"+_":return{signDisplay:"never"}}}function Ri(e){let t;if("E"===e[0]&&"E"===e[1]?(t={notation:"engineering"},e=e.slice(2)):"E"===e[0]&&(t={notation:"scientific"},e=e.slice(1)),t){const s=e.slice(0,2);if("+!"===s?(t.signDisplay="always",e=e.slice(2)):"+?"===s&&(t.signDisplay="exceptZero",e=e.slice(2)),!Ii.test(e))throw new Error("Malformed concise eng/scientific notation");t.minimumIntegerDigits=e.length}return t}function Pi(e){const t=Li(e);return t||{}}function Bi(e){let t={};for(const s of e){switch(s.stem){case"percent":case"%":t.style="percent";continue;case"%x100":t.style="percent",t.scale=100;continue;case"currency":t.style="currency",t.currency=s.options[0];continue;case"group-off":case",_":t.useGrouping=!1;continue;case"precision-integer":case".":t.maximumFractionDigits=0;continue;case"measure-unit":case"unit":t.style="unit",t.unit=Oi(s.options[0]);continue;case"compact-short":case"K":t.notation="compact",t.compactDisplay="short";continue;case"compact-long":case"KK":t.notation="compact",t.compactDisplay="long";continue;case"scientific":t={...t,notation:"scientific",...s.options.reduce((e,t)=>({...e,...Pi(t)}),{})};continue;case"engineering":t={...t,notation:"engineering",...s.options.reduce((e,t)=>({...e,...Pi(t)}),{})};continue;case"notation-simple":t.notation="standard";continue;case"unit-width-narrow":t.currencyDisplay="narrowSymbol",t.unitDisplay="narrow";continue;case"unit-width-short":t.currencyDisplay="code",t.unitDisplay="short";continue;case"unit-width-full-name":t.currencyDisplay="name",t.unitDisplay="long";continue;case"unit-width-iso-code":t.currencyDisplay="symbol";continue;case"scale":t.scale=parseFloat(s.options[0]);continue;case"rounding-mode-floor":t.roundingMode="floor";continue;case"rounding-mode-ceiling":t.roundingMode="ceil";continue;case"rounding-mode-down":t.roundingMode="trunc";continue;case"rounding-mode-up":t.roundingMode="expand";continue;case"rounding-mode-half-even":t.roundingMode="halfEven";continue;case"rounding-mode-half-down":t.roundingMode="halfTrunc";continue;case"rounding-mode-half-up":t.roundingMode="halfExpand";continue;case"integer-width":if(s.options.length>1)throw new RangeError("integer-width stems only accept a single optional option");s.options[0].replace(Mi,function(e,s,i,a,n,o){if(s)t.minimumIntegerDigits=i.length;else{if(a&&n)throw new Error("We currently do not support maximum integer digits");if(o)throw new Error("We currently do not support exact integer digits")}return""});continue}if(Ii.test(s.stem)){t.minimumIntegerDigits=s.stem.length;continue}if(Di.test(s.stem)){if(s.options.length>1)throw new RangeError("Fraction-precision stems only accept a single optional option");s.stem.replace(Di,function(e,s,i,a,n,o){return"*"===i?t.minimumFractionDigits=s.length:a&&"#"===a[0]?t.maximumFractionDigits=a.length:n&&o?(t.minimumFractionDigits=n.length,t.maximumFractionDigits=n.length+o.length):(t.minimumFractionDigits=s.length,t.maximumFractionDigits=s.length),""});const e=s.options[0];"w"===e?t={...t,trailingZeroDisplay:"stripIfInteger"}:e&&(t={...t,...Ni(e)});continue}if(Hi.test(s.stem)){t={...t,...Ni(s.stem)};continue}const e=Li(s.stem);e&&(t={...t,...e});const i=Ri(s.stem);i&&(t={...t,...i})}return t}let Ui=function(e){return e[e.EXPECT_ARGUMENT_CLOSING_BRACE=1]="EXPECT_ARGUMENT_CLOSING_BRACE",e[e.EMPTY_ARGUMENT=2]="EMPTY_ARGUMENT",e[e.MALFORMED_ARGUMENT=3]="MALFORMED_ARGUMENT",e[e.EXPECT_ARGUMENT_TYPE=4]="EXPECT_ARGUMENT_TYPE",e[e.INVALID_ARGUMENT_TYPE=5]="INVALID_ARGUMENT_TYPE",e[e.EXPECT_ARGUMENT_STYLE=6]="EXPECT_ARGUMENT_STYLE",e[e.INVALID_NUMBER_SKELETON=7]="INVALID_NUMBER_SKELETON",e[e.INVALID_DATE_TIME_SKELETON=8]="INVALID_DATE_TIME_SKELETON",e[e.EXPECT_NUMBER_SKELETON=9]="EXPECT_NUMBER_SKELETON",e[e.EXPECT_DATE_TIME_SKELETON=10]="EXPECT_DATE_TIME_SKELETON",e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE=11]="UNCLOSED_QUOTE_IN_ARGUMENT_STYLE",e[e.EXPECT_SELECT_ARGUMENT_OPTIONS=12]="EXPECT_SELECT_ARGUMENT_OPTIONS",e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE=13]="EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE=14]="INVALID_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR=15]="EXPECT_SELECT_ARGUMENT_SELECTOR",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR=16]="EXPECT_PLURAL_ARGUMENT_SELECTOR",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT=17]="EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT=18]="EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT",e[e.INVALID_PLURAL_ARGUMENT_SELECTOR=19]="INVALID_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR=20]="DUPLICATE_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR=21]="DUPLICATE_SELECT_ARGUMENT_SELECTOR",e[e.MISSING_OTHER_CLAUSE=22]="MISSING_OTHER_CLAUSE",e[e.INVALID_TAG=23]="INVALID_TAG",e[e.INVALID_TAG_NAME=25]="INVALID_TAG_NAME",e[e.UNMATCHED_CLOSING_TAG=26]="UNMATCHED_CLOSING_TAG",e[e.UNCLOSED_TAG=27]="UNCLOSED_TAG",e}({});function ji(e){return 0===e.type}function Fi(e){return 1===e.type}function Wi(e){return 2===e.type}function Zi(e){return 3===e.type}function qi(e){return 4===e.type}function Gi(e){return 5===e.type}function Ki(e){return 6===e.type}function Vi(e){return 7===e.type}function Yi(e){return 8===e.type}function Xi(e){return!(!e||"object"!=typeof e||0!==e.type)}function Ji(e){return!(!e||"object"!=typeof e||1!==e.type)}const Qi=/[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/,ea={"001":["H","h"],419:["h","H","hB","hb"],AC:["H","h","hb","hB"],AD:["H","hB"],AE:["h","hB","hb","H"],AF:["H","hb","hB","h"],AG:["h","hb","H","hB"],AI:["H","h","hb","hB"],AL:["h","H","hB"],AM:["H","hB"],AO:["H","hB"],AR:["h","H","hB","hb"],AS:["h","H"],AT:["H","hB"],AU:["h","hb","H","hB"],AW:["H","hB"],AX:["H"],AZ:["H","hB","h"],BA:["H","hB","h"],BB:["h","hb","H","hB"],BD:["h","hB","H"],BE:["H","hB"],BF:["H","hB"],BG:["H","hB","h"],BH:["h","hB","hb","H"],BI:["H","h"],BJ:["H","hB"],BL:["H","hB"],BM:["h","hb","H","hB"],BN:["hb","hB","h","H"],BO:["h","H","hB","hb"],BQ:["H"],BR:["H","hB"],BS:["h","hb","H","hB"],BT:["h","H"],BW:["H","h","hb","hB"],BY:["H","h"],BZ:["H","h","hb","hB"],CA:["h","hb","H","hB"],CC:["H","h","hb","hB"],CD:["hB","H"],CF:["H","h","hB"],CG:["H","hB"],CH:["H","hB","h"],CI:["H","hB"],CK:["H","h","hb","hB"],CL:["h","H","hB","hb"],CM:["H","h","hB"],CN:["H","hB","hb","h"],CO:["h","H","hB","hb"],CP:["H"],CR:["h","H","hB","hb"],CU:["h","H","hB","hb"],CV:["H","hB"],CW:["H","hB"],CX:["H","h","hb","hB"],CY:["h","H","hb","hB"],CZ:["H"],DE:["H","hB"],DG:["H","h","hb","hB"],DJ:["h","H"],DK:["H"],DM:["h","hb","H","hB"],DO:["h","H","hB","hb"],DZ:["h","hB","hb","H"],EA:["H","h","hB","hb"],EC:["h","H","hB","hb"],EE:["H","hB"],EG:["h","hB","hb","H"],EH:["h","hB","hb","H"],ER:["h","H"],ES:["H","hB","h","hb"],ET:["hB","hb","h","H"],FI:["H"],FJ:["h","hb","H","hB"],FK:["H","h","hb","hB"],FM:["h","hb","H","hB"],FO:["H","h"],FR:["H","hB"],GA:["H","hB"],GB:["H","h","hb","hB"],GD:["h","hb","H","hB"],GE:["H","hB","h"],GF:["H","hB"],GG:["H","h","hb","hB"],GH:["h","H"],GI:["H","h","hb","hB"],GL:["H","h"],GM:["h","hb","H","hB"],GN:["H","hB"],GP:["H","hB"],GQ:["H","hB","h","hb"],GR:["h","H","hb","hB"],GS:["H","h","hb","hB"],GT:["h","H","hB","hb"],GU:["h","hb","H","hB"],GW:["H","hB"],GY:["h","hb","H","hB"],HK:["h","hB","hb","H"],HN:["h","H","hB","hb"],HR:["H","hB"],HU:["H","h"],IC:["H","h","hB","hb"],ID:["H"],IE:["H","h","hb","hB"],IL:["H","hB"],IM:["H","h","hb","hB"],IN:["h","H"],IO:["H","h","hb","hB"],IQ:["h","hB","hb","H"],IR:["hB","H"],IS:["H"],IT:["H","hB"],JE:["H","h","hb","hB"],JM:["h","hb","H","hB"],JO:["h","hB","hb","H"],JP:["H","K","h"],KE:["hB","hb","H","h"],KG:["H","h","hB","hb"],KH:["hB","h","H","hb"],KI:["h","hb","H","hB"],KM:["H","h","hB","hb"],KN:["h","hb","H","hB"],KP:["h","H","hB","hb"],KR:["h","H","hB","hb"],KW:["h","hB","hb","H"],KY:["h","hb","H","hB"],KZ:["H","hB"],LA:["H","hb","hB","h"],LB:["h","hB","hb","H"],LC:["h","hb","H","hB"],LI:["H","hB","h"],LK:["H","h","hB","hb"],LR:["h","hb","H","hB"],LS:["h","H"],LT:["H","h","hb","hB"],LU:["H","h","hB"],LV:["H","hB","hb","h"],LY:["h","hB","hb","H"],MA:["H","h","hB","hb"],MC:["H","hB"],MD:["H","hB"],ME:["H","hB","h"],MF:["H","hB"],MG:["H","h"],MH:["h","hb","H","hB"],MK:["H","h","hb","hB"],ML:["H"],MM:["hB","hb","H","h"],MN:["H","h","hb","hB"],MO:["h","hB","hb","H"],MP:["h","hb","H","hB"],MQ:["H","hB"],MR:["h","hB","hb","H"],MS:["H","h","hb","hB"],MT:["H","h"],MU:["H","h"],MV:["H","h"],MW:["h","hb","H","hB"],MX:["h","H","hB","hb"],MY:["hb","hB","h","H"],MZ:["H","hB"],NA:["h","H","hB","hb"],NC:["H","hB"],NE:["H"],NF:["H","h","hb","hB"],NG:["H","h","hb","hB"],NI:["h","H","hB","hb"],NL:["H","hB"],NO:["H","h"],NP:["H","h","hB"],NR:["H","h","hb","hB"],NU:["H","h","hb","hB"],NZ:["h","hb","H","hB"],OM:["h","hB","hb","H"],PA:["h","H","hB","hb"],PE:["h","H","hB","hb"],PF:["H","h","hB"],PG:["h","H"],PH:["h","hB","hb","H"],PK:["h","hB","H"],PL:["H","h"],PM:["H","hB"],PN:["H","h","hb","hB"],PR:["h","H","hB","hb"],PS:["h","hB","hb","H"],PT:["H","hB"],PW:["h","H"],PY:["h","H","hB","hb"],QA:["h","hB","hb","H"],RE:["H","hB"],RO:["H","hB"],RS:["H","hB","h"],RU:["H"],RW:["H","h"],SA:["h","hB","hb","H"],SB:["h","hb","H","hB"],SC:["H","h","hB"],SD:["h","hB","hb","H"],SE:["H"],SG:["h","hb","H","hB"],SH:["H","h","hb","hB"],SI:["H","hB"],SJ:["H"],SK:["H"],SL:["h","hb","H","hB"],SM:["H","h","hB"],SN:["H","h","hB"],SO:["h","H"],SR:["H","hB"],SS:["h","hb","H","hB"],ST:["H","hB"],SV:["h","H","hB","hb"],SX:["H","h","hb","hB"],SY:["h","hB","hb","H"],SZ:["h","hb","H","hB"],TA:["H","h","hb","hB"],TC:["h","hb","H","hB"],TD:["h","H","hB"],TF:["H","h","hB"],TG:["H","hB"],TH:["H","h"],TJ:["H","h"],TL:["H","hB","hb","h"],TM:["H","h"],TN:["h","hB","hb","H"],TO:["h","H"],TR:["H","hB"],TT:["h","hb","H","hB"],TW:["hB","hb","h","H"],TZ:["hB","hb","H","h"],UA:["H","hB","h"],UG:["hB","hb","H","h"],UM:["h","hb","H","hB"],US:["h","hb","H","hB"],UY:["h","H","hB","hb"],UZ:["H","hB","h"],VA:["H","h","hB"],VC:["h","hb","H","hB"],VE:["h","H","hB","hb"],VG:["h","hb","H","hB"],VI:["h","hb","H","hB"],VN:["H","h"],VU:["h","H"],WF:["H","hB"],WS:["h","H"],XK:["H","hB","h"],YE:["h","hB","hb","H"],YT:["H","hB"],ZA:["H","h","hb","hB"],ZM:["h","hb","H","hB"],ZW:["H","h"],"af-ZA":["H","h","hB","hb"],"ar-001":["h","hB","hb","H"],"ca-ES":["H","h","hB"],"en-001":["h","hb","H","hB"],"en-HK":["h","hb","H","hB"],"en-IL":["H","h","hb","hB"],"en-MY":["h","hb","H","hB"],"es-BR":["H","h","hB","hb"],"es-ES":["H","h","hB","hb"],"es-GQ":["H","h","hB","hb"],"fr-CA":["H","h","hB"],"gl-ES":["H","h","hB"],"gu-IN":["hB","hb","h","H"],"hi-IN":["hB","h","H"],"it-CH":["H","h","hB"],"it-IT":["H","h","hB"],"kn-IN":["hB","h","H"],"ku-SY":["H","hB"],"ml-IN":["hB","h","H"],"mr-IN":["hB","hb","h","H"],"pa-IN":["hB","hb","h","H"],"ta-IN":["hB","h","hb","H"],"te-IN":["hB","h","H"],"zu-ZA":["H","hB","hb","h"]};function ta(e){let t=e.hourCycle;if(void 0===t&&e.hourCycles&&e.hourCycles.length&&(t=e.hourCycles[0]),t)switch(t){case"h24":return"k";case"h23":return"H";case"h12":return"h";case"h11":return"K";default:throw new Error("Invalid hourCycle")}const s=e.language;let i;return"root"!==s&&(i=e.maximize().region),(ea[i||""]||ea[s||""]||ea[`${s}-001`]||ea["001"])[0]}const sa=new RegExp(`^${Qi.source}*`),ia=new RegExp(`${Qi.source}*$`);function aa(e,t){return{start:e,end:t}}const na=!!Object.fromEntries,oa=!!String.prototype.trimStart,ra=!!String.prototype.trimEnd,la=na?Object.fromEntries:function(e){const t={};for(const[s,i]of e)t[s]=i;return t},da=oa?function(e){return e.trimStart()}:function(e){return e.replace(sa,"")},ca=ra?function(e){return e.trimEnd()}:function(e){return e.replace(ia,"")},ha=new RegExp("([^\\p{White_Space}\\p{Pattern_Syntax}]*)","yu");var ua=class{constructor(e,t={}){this.message=e,this.position={offset:0,line:1,column:1},this.ignoreTag=!!t.ignoreTag,this.locale=t.locale,this.requiresOtherClause=!!t.requiresOtherClause,this.shouldParseSkeletons=!!t.shouldParseSkeletons}parse(){if(0!==this.offset())throw Error("parser can only be used once");if(this.message.length>0){const e=this.message.charCodeAt(0);if(35!==e&&39!==e&&60!==e&&123!==e&&125!==e){const e=function(e){if(0===e.length)return null;let t=1,s=1;for(let i=0;i<e.length;){const a=e.charCodeAt(i);switch(a){case 35:case 39:case 60:case 123:case 125:return null}if(10===a)t++,s=1,i++;else if(s++,a>=55296&&a<=56319&&i+1<e.length){const t=e.charCodeAt(i+1);i+=t>=56320&&t<=57343?2:1}else i++}return{offset:e.length,line:t,column:s}}(this.message);if(e){const t=this.clonePosition();return this.position=e,{val:[{type:0,value:this.message,location:aa(t,this.clonePosition())}],err:null}}}}return this.parseMessage(0,"",!1)}parseMessage(e,t,s){let i=[];for(;!this.isEOF();){const a=this.char();if(123===a){const t=this.parseArgument(e,s);if(t.err)return t;i.push(t.val)}else{if(125===a&&e>0)break;if(35!==a||"plural"!==t&&"selectordinal"!==t){if(60===a&&!this.ignoreTag&&47===this.peek()){if(s)break;return this.error(26,aa(this.clonePosition(),this.clonePosition()))}if(60===a&&!this.ignoreTag&&pa(this.peek()||0)){const s=this.parseTag(e,t);if(s.err)return s;i.push(s.val)}else{const s=this.parseLiteral(e,t);if(s.err)return s;i.push(s.val)}}else{const e=this.clonePosition();this.bump(),i.push({type:7,location:aa(e,this.clonePosition())})}}}return{val:i,err:null}}parseTag(e,t){const s=this.clonePosition();this.bump();const i=this.parseTagName();if(this.bumpSpace(),this.bumpIf("/>"))return{val:{type:0,value:`<${i}/>`,location:aa(s,this.clonePosition())},err:null};if(this.bumpIf(">")){const a=this.parseMessage(e+1,t,!0);if(a.err)return a;const n=a.val,o=this.clonePosition();if(this.bumpIf("</")){if(this.isEOF()||!pa(this.char()))return this.error(23,aa(o,this.clonePosition()));const e=this.clonePosition();return i!==this.parseTagName()?this.error(26,aa(e,this.clonePosition())):(this.bumpSpace(),this.bumpIf(">")?{val:{type:8,value:i,children:n,location:aa(s,this.clonePosition())},err:null}:this.error(23,aa(o,this.clonePosition())))}return this.error(27,aa(s,this.clonePosition()))}return this.error(23,aa(s,this.clonePosition()))}parseTagName(){const e=this.offset();for(this.bump();!this.isEOF()&&ga(this.char());)this.bump();return this.message.slice(e,this.offset())}parseLiteral(e,t){const s=this.clonePosition();let i="";for(;;){const s=this.tryParseQuote(t);if(s){i+=s;continue}const a=this.tryParseUnquoted(e,t);if(a){i+=a;continue}const n=this.tryParseLeftAngleBracket();if(!n)break;i+=n}return{val:{type:0,value:i,location:aa(s,this.clonePosition())},err:null}}tryParseLeftAngleBracket(){return this.isEOF()||60!==this.char()||!this.ignoreTag&&(pa(e=this.peek()||0)||47===e)?null:(this.bump(),"<");var e}tryParseQuote(e){if(this.isEOF()||39!==this.char())return null;switch(this.peek()){case 39:return this.bump(),this.bump(),"'";case 123:case 60:case 62:case 125:break;case 35:if("plural"===e||"selectordinal"===e)break;return null;default:return null}this.bump();const t=[this.char()];for(this.bump();!this.isEOF();){const e=this.char();if(39===e){if(39!==this.peek()){this.bump();break}t.push(39),this.bump()}else t.push(e);this.bump()}return String.fromCodePoint(...t)}tryParseUnquoted(e,t){if(this.isEOF())return null;const s=this.char();return 60===s||123===s||35===s&&("plural"===t||"selectordinal"===t)||125===s&&e>0?null:(this.bump(),String.fromCodePoint(s))}parseArgument(e,t){const s=this.clonePosition();if(this.bump(),this.bumpSpace(),this.isEOF())return this.error(1,aa(s,this.clonePosition()));if(125===this.char())return this.bump(),this.error(2,aa(s,this.clonePosition()));let i=this.parseIdentifierIfPossible().value;if(!i)return this.error(3,aa(s,this.clonePosition()));if(this.bumpSpace(),this.isEOF())return this.error(1,aa(s,this.clonePosition()));switch(this.char()){case 125:return this.bump(),{val:{type:1,value:i,location:aa(s,this.clonePosition())},err:null};case 44:return this.bump(),this.bumpSpace(),this.isEOF()?this.error(1,aa(s,this.clonePosition())):this.parseArgumentOptions(e,t,i,s);default:return this.error(3,aa(s,this.clonePosition()))}}parseIdentifierIfPossible(){const e=this.clonePosition(),t=this.offset(),s=function(e,t){return ha.lastIndex=t,ha.exec(e)[1]??""}(this.message,t),i=t+s.length;return this.bumpTo(i),{value:s,location:aa(e,this.clonePosition())}}parseArgumentOptions(e,t,s,i){let a=this.clonePosition(),n=this.parseIdentifierIfPossible().value,o=this.clonePosition();switch(n){case"":return this.error(4,aa(a,o));case"number":case"date":case"time":{this.bumpSpace();let e=null;if(this.bumpIf(",")){this.bumpSpace();const t=this.clonePosition(),s=this.parseSimpleArgStyleIfPossible();if(s.err)return s;const i=ca(s.val);if(0===i.length)return this.error(6,aa(this.clonePosition(),this.clonePosition()));e={style:i,styleLocation:aa(t,this.clonePosition())}}const t=this.tryParseArgumentClose(i);if(t.err)return t;const a=aa(i,this.clonePosition());if(e&&e.style.startsWith("::")){let t=da(e.style.slice(2));if("number"===n){const i=this.parseNumberSkeletonFromString(t,e.styleLocation);return i.err?i:{val:{type:2,value:s,location:a,style:i.val},err:null}}{if(0===t.length)return this.error(10,a);let i=t;this.locale&&(i=function(e,t){let s="";for(let i=0;i<e.length;i++){const a=e.charAt(i);if("j"===a){let n=0;for(;i+1<e.length&&e.charAt(i+1)===a;)n++,i++;let o=1+(1&n),r=n<2?1:3+(n>>1),l="a",d=ta(t);for("H"!=d&&"k"!=d||(r=0);r-- >0;)s+=l;for(;o-- >0;)s=d+s}else s+="J"===a?"H":a}return s}(t,this.locale));return{val:{type:"date"===n?3:4,value:s,location:a,style:{type:1,pattern:i,location:e.styleLocation,parsedOptions:this.shouldParseSkeletons?Ci(i):{}}},err:null}}}return{val:{type:"number"===n?2:"date"===n?3:4,value:s,location:a,style:e?.style??null},err:null}}case"plural":case"selectordinal":case"select":{const a=this.clonePosition();if(this.bumpSpace(),!this.bumpIf(","))return this.error(12,aa(a,{...a}));this.bumpSpace();let o=this.parseIdentifierIfPossible(),r=0;if("select"!==n&&"offset"===o.value){if(!this.bumpIf(":"))return this.error(13,aa(this.clonePosition(),this.clonePosition()));this.bumpSpace();const e=this.tryParseDecimalInteger(13,14);if(e.err)return e;this.bumpSpace(),o=this.parseIdentifierIfPossible(),r=e.val}const l=this.tryParsePluralOrSelectOptions(e,n,t,o);if(l.err)return l;const d=this.tryParseArgumentClose(i);if(d.err)return d;const c=aa(i,this.clonePosition());return"select"===n?{val:{type:5,value:s,options:la(l.val),location:c},err:null}:{val:{type:6,value:s,options:la(l.val),offset:r,pluralType:"plural"===n?"cardinal":"ordinal",location:c},err:null}}default:return this.error(5,aa(a,o))}}tryParseArgumentClose(e){return this.isEOF()||125!==this.char()?this.error(1,aa(e,this.clonePosition())):(this.bump(),{val:!0,err:null})}parseSimpleArgStyleIfPossible(){let e=0;const t=this.clonePosition();for(;!this.isEOF();)switch(this.char()){case 39:{this.bump();let e=this.clonePosition();if(!this.bumpUntil("'"))return this.error(11,aa(e,this.clonePosition()));this.bump();break}case 123:e+=1,this.bump();break;case 125:if(!(e>0))return{val:this.message.slice(t.offset,this.offset()),err:null};e-=1;break;default:this.bump()}return{val:this.message.slice(t.offset,this.offset()),err:null}}parseNumberSkeletonFromString(e,t){let s=[];try{s=function(e){if(0===e.length)throw new Error("Number skeleton cannot be empty");const t=e.split(Ti).filter(e=>e.length>0),s=[];for(const e of t){let t=e.split("/");if(0===t.length)throw new Error("Invalid number skeleton");const[i,...a]=t;for(const e of a)if(0===e.length)throw new Error("Invalid number skeleton");s.push({stem:i,options:a})}return s}(e)}catch{return this.error(7,t)}return{val:{type:0,tokens:s,location:t,parsedOptions:this.shouldParseSkeletons?Bi(s):{}},err:null}}tryParsePluralOrSelectOptions(e,t,s,i){let a=!1;const n=[],o=new Set;let{value:r,location:l}=i;for(;;){if(0===r.length){const e=this.clonePosition();if("select"===t||!this.bumpIf("="))break;{const t=this.tryParseDecimalInteger(16,19);if(t.err)return t;l=aa(e,this.clonePosition()),r=this.message.slice(e.offset,this.offset())}}if(o.has(r))return this.error("select"===t?21:20,l);"other"===r&&(a=!0),this.bumpSpace();const i=this.clonePosition();if(!this.bumpIf("{"))return this.error("select"===t?17:18,aa(this.clonePosition(),this.clonePosition()));const d=this.parseMessage(e+1,t,s);if(d.err)return d;const c=this.tryParseArgumentClose(i);if(c.err)return c;n.push([r,{value:d.val,location:aa(i,this.clonePosition())}]),o.add(r),this.bumpSpace(),({value:r,location:l}=this.parseIdentifierIfPossible())}return 0===n.length?this.error("select"===t?15:16,aa(this.clonePosition(),this.clonePosition())):this.requiresOtherClause&&!a?this.error(22,aa(this.clonePosition(),this.clonePosition())):{val:n,err:null}}tryParseDecimalInteger(e,t){let s=1;const i=this.clonePosition();this.bumpIf("+")||this.bumpIf("-")&&(s=-1);let a=!1,n=0;for(;!this.isEOF();){const e=this.char();if(!(e>=48&&e<=57))break;a=!0,n=10*n+(e-48),this.bump()}const o=aa(i,this.clonePosition());return a?(n*=s,Number.isSafeInteger(n)?{val:n,err:null}:this.error(t,o)):this.error(e,o)}offset(){return this.position.offset}isEOF(){return this.offset()===this.message.length}clonePosition(){return{offset:this.position.offset,line:this.position.line,column:this.position.column}}char(){const e=this.position.offset;if(e>=this.message.length)throw Error("out of bound");const t=this.message.codePointAt(e);if(void 0===t)throw Error(`Offset ${e} is at invalid UTF-16 code unit boundary`);return t}error(e,t){return{val:null,err:{kind:e,message:this.message,location:t}}}bump(){if(this.isEOF())return;const e=this.char();10===e?(this.position.line+=1,this.position.column=1,this.position.offset+=1):(this.position.column+=1,this.position.offset+=e<65536?1:2)}bumpIf(e){if(this.message.startsWith(e,this.offset())){for(let t=0;t<e.length;t++)this.bump();return!0}return!1}bumpUntil(e){const t=this.offset(),s=this.message.indexOf(e,t);return s>=0?(this.bumpTo(s),!0):(this.bumpTo(this.message.length),!1)}bumpTo(e){if(this.offset()>e)throw Error(`targetOffset ${e} must be greater than or equal to the current offset ${this.offset()}`);for(e=Math.min(e,this.message.length);;){const t=this.offset();if(t===e)break;if(t>e)throw Error(`targetOffset ${e} is at invalid UTF-16 code unit boundary`);if(this.bump(),this.isEOF())break}}bumpSpace(){for(;!this.isEOF()&&ma(this.char());)this.bump()}peek(){if(this.isEOF())return null;const e=this.char(),t=this.offset();return this.message.charCodeAt(t+(e>=65536?2:1))??null}};function pa(e){return e>=97&&e<=122||e>=65&&e<=90}function ga(e){return 45===e||46===e||e>=48&&e<=57||95===e||e>=97&&e<=122||e>=65&&e<=90||183==e||e>=192&&e<=214||e>=216&&e<=246||e>=248&&e<=893||e>=895&&e<=8191||e>=8204&&e<=8205||e>=8255&&e<=8256||e>=8304&&e<=8591||e>=11264&&e<=12271||e>=12289&&e<=55295||e>=63744&&e<=64975||e>=65008&&e<=65533||e>=65536&&e<=983039}function ma(e){return e>=9&&e<=13||32===e||133===e||e>=8206&&e<=8207||8232===e||8233===e}function va(e){e.forEach(e=>{if(delete e.location,Gi(e)||Ki(e))for(const t in e.options)delete e.options[t].location,va(e.options[t].value);else Wi(e)&&Xi(e.style)||(Zi(e)||qi(e))&&Ji(e.style)?delete e.style.location:Yi(e)&&va(e.children)})}function fa(e,t={}){t={shouldParseSkeletons:!0,requiresOtherClause:!0,...t};const s=new ua(e,t).parse();if(s.err){const e=SyntaxError(Ui[s.err.kind]);throw e.location=s.err.location,e.originalMessage=s.err.message,e}return t?.captureLocation||va(s.val),s.val}var _a=class extends Error{constructor(e,t,s){super(e),this.code=t,this.originalMessage=s}toString(){return`[formatjs Error: ${this.code}] ${this.message}`}},ba=class extends _a{constructor(e,t,s,i){super(`Invalid values for "${e}": "${t}". Options are "${Object.keys(s).join('", "')}"`,"INVALID_VALUE",i)}},ya=class extends _a{constructor(e,t,s){super(`Value for "${e}" must be of type ${t}`,"INVALID_VALUE",s)}},wa=class extends _a{constructor(e,t){super(`The intl string context variable "${e}" was not provided to the string "${t}"`,"MISSING_VALUE",t)}};function $a(e){return"function"==typeof e}function xa(e,t,s,i,a,n,o){if(1===e.length&&ji(e[0]))return[{type:0,value:e[0].value}];const r=[];for(const l of e){if(ji(l)){r.push({type:0,value:l.value});continue}if(Vi(l)){"number"==typeof n&&r.push({type:0,value:s.getNumberFormat(t).format(n)});continue}const{value:e}=l;if(!a||!(e in a))throw new wa(e,o);let d=a[e];if(Fi(l))d&&"string"!=typeof d&&"number"!=typeof d&&"bigint"!=typeof d||(d="string"==typeof d||"number"==typeof d||"bigint"==typeof d?String(d):""),r.push({type:"string"==typeof d?0:1,value:d});else{if(Zi(l)){const e="string"==typeof l.style?i.date[l.style]:Ji(l.style)?l.style.parsedOptions:void 0;r.push({type:0,value:s.getDateTimeFormat(t,e).format(d)});continue}if(qi(l)){const e="string"==typeof l.style?i.time[l.style]:Ji(l.style)?l.style.parsedOptions:i.time.medium;r.push({type:0,value:s.getDateTimeFormat(t,e).format(d)});continue}if(Wi(l)){const e="string"==typeof l.style?i.number[l.style]:Xi(l.style)?l.style.parsedOptions:void 0;if(e&&e.scale){const t=e.scale||1;if("bigint"==typeof d){if(!Number.isInteger(t))throw new TypeError(`Cannot apply fractional scale ${t} to bigint value. Scale must be an integer when formatting bigint.`);d*=BigInt(t)}else d*=t}r.push({type:0,value:s.getNumberFormat(t,e).format(d)});continue}if(Yi(l)){const{children:e,value:d}=l,c=a[d];if(!$a(c))throw new ya(d,"function",o);let h=c(xa(e,t,s,i,a,n).map(e=>e.value));Array.isArray(h)||(h=[h]),r.push(...h.map(e=>({type:"string"==typeof e?0:1,value:e})))}if(Gi(l)){const e=d,n=(Object.prototype.hasOwnProperty.call(l.options,e)?l.options[e]:void 0)||l.options.other;if(!n)throw new ba(l.value,d,Object.keys(l.options),o);r.push(...xa(n.value,t,s,i,a));continue}if(Ki(l)){const e=`=${d}`;let n=Object.prototype.hasOwnProperty.call(l.options,e)?l.options[e]:void 0;if(!n){if(!Intl.PluralRules)throw new _a('Intl.PluralRules is not available in this environment.\nTry polyfilling it using "@formatjs/intl-pluralrules"\n',"MISSING_INTL_API",o);const e="bigint"==typeof d?Number(d):d,i=s.getPluralRules(t,{type:l.pluralType}).select(e-(l.offset||0));n=(Object.prototype.hasOwnProperty.call(l.options,i)?l.options[i]:void 0)||l.options.other}if(!n)throw new ba(l.value,d,Object.keys(l.options),o);const c="bigint"==typeof d?Number(d):d;r.push(...xa(n.value,t,s,i,a,c-(l.offset||0)));continue}}}return(l=r).length<2?l:l.reduce((e,t)=>{const s=e[e.length-1];return s&&0===s.type&&0===t.type?s.value+=t.value:e.push(t),e},[]);var l}function ka(e,t){return t?Object.keys(e).reduce((s,i)=>{var a,n;return s[i]=(a=e[i],(n=t[i])?{...a,...n,...Object.keys(a).reduce((e,t)=>(e[t]={...a[t],...n[t]},e),{})}:a),s},{...e}):e}function za(e){return{create:()=>({get:t=>e[t],set(t,s){e[t]=s}})}}var Sa=class e{constructor(t,s=e.defaultLocale,i,a){if(this.formatterCache={number:{},dateTime:{},pluralRules:{}},this.format=e=>{const t=this.formatToParts(e);if(1===t.length)return t[0].value;const s=t.reduce((e,t)=>(e.length&&0===t.type&&"string"==typeof e[e.length-1]?e[e.length-1]+=t.value:e.push(t.value),e),[]);return s.length<=1?s[0]||"":s},this.formatToParts=e=>xa(this.ast,this.locales,this.formatters,this.formats,e,void 0,this.message),this.resolvedOptions=()=>({locale:this.resolvedLocale?.toString()||Intl.NumberFormat.supportedLocalesOf(this.locales)[0]}),this.getAst=()=>this.ast,this.locales=s,this.resolvedLocale=e.resolveLocale(s),"string"==typeof t){if(this.message=t,!e.__parse)throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");const{...s}=a||{};this.ast=e.__parse(t,{...s,locale:this.resolvedLocale})}else this.ast=t;if(!Array.isArray(this.ast))throw new TypeError("A message must be provided as a String or AST.");this.formats=ka(e.formats,i),this.formatters=a&&a.formatters||function(e={number:{},dateTime:{},pluralRules:{}}){return{getNumberFormat:bi((...e)=>new Intl.NumberFormat(...e),{cache:za(e.number),strategy:Ai.variadic}),getDateTimeFormat:bi((...e)=>new Intl.DateTimeFormat(...e),{cache:za(e.dateTime),strategy:Ai.variadic}),getPluralRules:bi((...e)=>new Intl.PluralRules(...e),{cache:za(e.pluralRules),strategy:Ai.variadic})}}(this.formatterCache)}static{this.memoizedDefaultLocale=null}static get defaultLocale(){return e.memoizedDefaultLocale||(e.memoizedDefaultLocale=(new Intl.NumberFormat).resolvedOptions().locale),e.memoizedDefaultLocale}static{this.resolveLocale=e=>{if(void 0===Intl.Locale)return;const t=Intl.NumberFormat.supportedLocalesOf(e);return t.length>0?new Intl.Locale(t[0]):new Intl.Locale("string"==typeof e?e:e[0])}}static{this.__parse=fa}static{this.formats={number:{integer:{maximumFractionDigits:0},currency:{style:"currency"},percent:{style:"percent"}},date:{short:{month:"numeric",day:"numeric",year:"2-digit"},medium:{month:"short",day:"numeric",year:"numeric"},long:{month:"long",day:"numeric",year:"numeric"},full:{weekday:"long",month:"long",day:"numeric",year:"numeric"}},time:{short:{hour:"numeric",minute:"numeric"},medium:{hour:"numeric",minute:"numeric",second:"numeric"},long:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"},full:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"}}}}};const Aa={en:_i},Ea={};function Ca(e){return e.replace(/['"]+/g,"").split(/[-_]/)[0].toLowerCase()}function Ta(e){const t=Ca(e);return t in Aa||!_e.includes(t)}function Oa(e,t,...s){const i=Ca(t);let a;try{a=e.split(".").reduce((e,t)=>e[t],Aa[i])}catch(t){a=e.split(".").reduce((e,t)=>e[t],Aa.en)}if(void 0===a&&(a=e.split(".").reduce((e,t)=>e[t],Aa.en)),!s.length)return a;const n={};for(let e=0;e<s.length;e+=2){let t=s[e];t=t.replace(/^{([^}]+)?}$/,"$1"),n[t]=s[e+1]}try{return new Sa(a,t).format(n)}catch(e){return"Translation "+e}}function Da(e,t,s){e.dispatchEvent(new CustomEvent(t,{detail:s,bubbles:!0,composed:!0,cancelable:!1}))}function Ha(e,t){return(e=e.toString()).split(",")[t]}function Ma(e,t){switch(t){case xt:return e.units==Oe?W`${ei(dt)}`:W`${ei(ct)}`;case we:case ft:return e.units==Oe?W`${ei(at)}`:W`${ei(nt)}`;case ut:return e.units==Oe?W`${ei("m<sup>2</sup>")}`:W`${ei(et)}`;case pt:return e.units==Oe?W`${ei(tt)}`:W`${ei(st)}`;default:return W``}}function Ia(e,t){!function(e,t){Da(e,"show-dialog",{dialogTag:"error-dialog",dialogImport:()=>Promise.resolve().then(function(){return Bn}),dialogParams:{error:t}})}(t,W`
    ${e.error}:${e.body.message?W` ${e.body.message} `:""}
  `)}const Na=(e,t,s=!1)=>{s?history.replaceState(null,"",t):history.pushState(null,"",t),Da(window,"location-changed",{replace:s})};function La(e){var t;if(!e)return"Unknown error";if("string"==typeof e)return e;const s=e;return(null===(t=null==s?void 0:s.body)||void 0===t?void 0:t.message)||(null==s?void 0:s.message)||(null==s?void 0:s.error)||JSON.stringify(e)}function Ra(e){const t=Math.round(e);if(t<60)return`${t} s`;const s=Math.floor(t/60),i=t%60;return i?`${s} min ${i} s`:`${s} min`}function Pa(e,t){e.dispatchEvent(new CustomEvent("hass-notification",{detail:{message:t},bubbles:!0,composed:!0}))}function Ba(e,t,s,i){var a;Pa(e,`${Oa(s,null!==(a=null==t?void 0:t.language)&&void 0!==a?a:"en")}: ${La(i)}`)}var Ua="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",ja="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z";const Fa=e=>{class s extends e{connectedCallback(){super.connectedCallback(),this.__checkSubscribed()}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const e=this.__unsubs.pop();e instanceof Promise?e.then(e=>e()):e()}this.__unsubs=void 0}}updated(e){super.updated(e),e.has("hass")&&this.__checkSubscribed()}hassSubscribe(){return[]}__checkSubscribed(){void 0===this.__unsubs&&this.isConnected&&void 0!==this.hass&&(this.__unsubs=this.hassSubscribe())}}return t([pe({attribute:!1})],s.prototype,"hass",void 0),s};var Wa,Za;!function(e){e.Sunrise="sunrise",e.Sunset="sunset",e.SolarAzimuth="solar_azimuth"}(Wa||(Wa={})),function(e){e.Disabled="disabled",e.Manual="manual",e.Automatic="automatic"}(Za||(Za={}));const qa=()=>{const e=e=>{let t={};for(let s=0;s<e.length;s+=2){const i=e[s],a=s<e.length?e[s+1]:void 0;t=Object.assign(Object.assign({},t),{[i]:a})}return t},t=window.location.pathname.split("/");let s={page:t[2]||"general",params:{}};if(t.length>3){let i=t.slice(3);if(t.includes("filter")){const t=i.findIndex(e=>"filter"==e),a=i.slice(t+1);i=i.slice(0,t),s=Object.assign(Object.assign({},s),{filter:e(a)})}i.length&&(i.length%2&&(s=Object.assign(Object.assign({},s),{subpage:i.shift()})),i.length&&(s=Object.assign(Object.assign({},s),{params:e(i)})))}return s},Ga=(e,...t)=>{let s={page:e,params:{}};t.forEach(e=>{"string"==typeof e?s=Object.assign(Object.assign({},s),{subpage:e}):"params"in e?s=Object.assign(Object.assign({},s),{params:e.params}):"filter"in e&&(s=Object.assign(Object.assign({},s),{filter:e.filter}))});const i=e=>{let t=Object.keys(e);t=t.filter(t=>e[t]),t.sort();let s="";return t.forEach(t=>{const i=e[t];s=s.length?`${s}/${t}/${i}`:`${t}/${i}`}),s};let a=`/${fe}/${s.page}`;return s.subpage&&(a=`${a}/${s.subpage}`),i(s.params).length&&(a=`${a}/${i(s.params)}`),s.filter&&(a=`${a}/filter/${i(s.filter)}`),a},Ka=r`
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
`;const Va=e=>String(e).padStart(2,"0");function Ya(e){return e instanceof Date?e:new Date(e)}function Xa(e){const t=Ya(e);return`${Va(t.getHours())}:${Va(t.getMinutes())}`}function Ja(e){const t=Ya(e);return`${t.getFullYear()}-${Va(t.getMonth()+1)}-${Va(t.getDate())} ${Va(t.getHours())}:${Va(t.getMinutes())}`}function Qa(e,t){return e.getFullYear()===t.getFullYear()&&e.getMonth()===t.getMonth()&&e.getDate()===t.getDate()}class en extends(Fa(le)){constructor(){super(...arguments),this.hideSettingsLinks=!1,this.actionsMode="full",this.zones=[],this._distributors=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._operationError=null,this._confirmIrrigate=null,this._skipDetailsOpen=!1,this._runMinutes={},this._now=Date.now(),this._countdownTimer=null,this._updateScheduled=!1}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}firstUpdated(){qs().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}disconnectedCallback(){super.disconnectedCallback(),this._stopCountdownTicker()}_syncCountdownTicker(){var e,t;const s=Object.keys(null!==(t=null===(e=this._outlook)||void 0===e?void 0:e.active_runs)&&void 0!==t?t:{}).length>0;s&&null===this._countdownTimer?this._countdownTimer=window.setInterval(()=>{this._now=Date.now()},1e3):s||this._stopCountdownTicker()}_stopCountdownTicker(){null!==this._countdownTimer&&(window.clearInterval(this._countdownTimer),this._countdownTimer=null)}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:fe+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[s,i,a,n]=await Promise.all([Es(this.hass),Ts(this.hass),(t=this.hass,t.callWS({type:fe+"/irrigation_outlook"})).catch(e=>{console.error("Failed to fetch irrigation outlook:",e)}),Ps(this.hass).catch(e=>(console.error("Failed to fetch distributors:",e),[]))]);this.config=s,this.zones=i,this._outlook=a,this._distributors=n,this._initialLoadDone=!0,this._syncCountdownTicker()}catch(e){console.error("Error fetching data:",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}var t}handleCalculateAllZones(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",fe+"/zones",{calculate_all:!0})).catch(e=>{console.error("Failed to calculate all zones:",e),Ba(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after calc-all:",e))}))}handleUpdateAllZones(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",fe+"/zones",{update_all:!0})).catch(e=>{console.error("Failed to update all zones:",e),Ba(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after update-all:",e))}))}_canActuate(e){return!!(e.linked_entity||"service"===e.watering_mode&&e.run_service||null!=e.distributor_id)}get _linkedZoneCount(){return this.zones.filter(e=>{var t;return this._canActuate(e)&&(null!==(t=e.duration)&&void 0!==t?t:0)>0}).length}async _doIrrigate(){var e;const t=this._confirmIrrigate;if(this._confirmIrrigate=null,null===t||!this.hass)return;const s="all"===t,i=s?void 0:this.zones.find(e=>{var s;return(null===(s=e.id)||void 0===s?void 0:s.toString())===t}),a=s?`(${this._linkedZoneCount})`:`: ${null!==(e=null==i?void 0:i.name)&&void 0!==e?e:t}`;try{await(n=this.hass,o=s?void 0:t,n.callWS(Object.assign({type:fe+"/irrigate_now"},void 0!==o?{zone_id:o}:{}))),Pa(this,`${Oa("panels.zones.confirm_irrigate.toast_started",this.hass.language)} ${a}`)}catch(e){const t=La(e);console.error("irrigate_now failed",e),Pa(this,`${Oa("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}var n,o}get _rainDelayUntil(){var e;const t=null===(e=this._outlook)||void 0===e?void 0:e.rain_delay_until;if(!t)return null;const s=new Date(t);return s.getTime()>Date.now()?s:null}async _setRainDelay(e){if(this.hass)try{await((e,t)=>e.callWS({type:fe+"/set_rain_delay",hours:t}))(this.hass,e),await this._fetchData()}catch(e){console.error("set_rain_delay failed",e),Ba(this,this.hass,"common.errors.action_failed",e)}}async _clearRainDelay(){var e;if(this.hass)try{await(e=this.hass,e.callWS({type:fe+"/clear_rain_delay"})),await this._fetchData()}catch(e){console.error("clear_rain_delay failed",e),Ba(this,this.hass,"common.errors.action_failed",e)}}_zoneRunMinutes(e){var t,s;const i=String(null!==(t=e.id)&&void 0!==t?t:"");return null!==(s=this._runMinutes[i])&&void 0!==s?s:10}_zoneDistributor(e){if(null!=e.distributor_id)return this._distributors.find(t=>t.id===e.distributor_id)}_distributorBusy(e){var t;const s=this._zoneDistributor(e);return!!s&&Object.keys(null!==(t=s.active_cycle)&&void 0!==t?t:{}).length>0}async _runZoneFor(e){if(!this.hass||!this._canActuate(e)||void 0===e.id)return;if(this._distributorBusy(e))return;const t=this._zoneRunMinutes(e);var s,i,a;if(t>0)try{await(s=this.hass,i=e.id.toString(),a=t,s.callWS({type:fe+"/run_zone",zone_id:i,duration:a})),Pa(this,`${Oa("panels.zones.run_zone.toast_started",this.hass.language)}: ${e.name} (${t} min)`)}catch(e){const t=La(e);console.error("run_zone failed",e),Pa(this,`${Oa("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}}_activeRun(e){var t,s;if(void 0!==e.id)return null===(s=null===(t=this._outlook)||void 0===t?void 0:t.active_runs)||void 0===s?void 0:s[String(e.id)]}_runSecondsLeft(e){if(!e.ends_at)return null;const t=Math.round((new Date(e.ends_at).getTime()-this._now)/1e3);return t>0?t:0}async _stopZone(e){var t,s;if(this.hass&&void 0!==e.id)try{await(t=this.hass,s=e.id.toString(),t.callWS({type:fe+"/stop_zone",zone_id:s})),Pa(this,`${Oa("panels.zones.stop_zone.toast_stopped",this.hass.language)}: ${e.name}`),await this._fetchData()}catch(e){const t=La(e);console.error("stop_zone failed",e),Pa(this,`${Oa("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`)}}handleCalculateZone(e){const t=this.zones[e];var s,i;t&&null!=t.id&&this.hass&&(this._operationError=null,this.isSaving=!0,this._scheduleUpdate(),(s=this.hass,i=t.id.toString(),s.callApi("POST",fe+"/zones",{id:i,calculate:!0,override_cache:!0})).catch(e=>{const t=La(e);console.error("calculateZone failed:",e),this._operationError=t}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after calc:",e))}))}handleUpdateZone(e){const t=this.zones[e];var s,i;t&&null!=t.id&&this.hass&&(this._operationError=null,this.isSaving=!0,this._scheduleUpdate(),(s=this.hass,i=t.id.toString(),s.callApi("POST",fe+"/zones",{id:i,update:!0})).catch(e=>{const t=La(e);console.error("updateZone failed:",e),this._operationError=t}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after update:",e))}))}_openZoneSettings(e){const t=void 0!==e.id?{params:{zone:String(e.id)}}:void 0;Na(0,t?Ga("setup","zones",t):Ga("setup","zones"))}_runTargetsZone(e,t){return"all"===e.zones||!(!Array.isArray(e.zones)||void 0===t.id)&&e.zones.map(e=>Number(e)).includes(Number(t.id))}get _nextIrrigateRun(){var e;return null===(e=this._outlook)||void 0===e?void 0:e.upcoming_runs.find(e=>"irrigate"===e.action&&e.next_run_utc)}_nextIrrigateRunForZone(e){var t;return null===(t=this._outlook)||void 0===t?void 0:t.upcoming_runs.find(t=>"irrigate"===t.action&&t.next_run_utc&&this._runTargetsZone(t,e))}get _activeGuards(){var e,t;return null!==(t=null===(e=this._outlook)||void 0===e?void 0:e.skip_preview.checks.filter(e=>e.enabled))&&void 0!==t?t:[]}get _triggeredGuards(){return this._activeGuards.filter(e=>e.would_skip)}_zoneHasDeficit(e){var t,s,i;const a=null!==(t=e.duration)&&void 0!==t?t:0,n=Number(null!==(s=e.bucket_threshold)&&void 0!==s?s:0),o=this._zoneEstimate(e),r=o&&o.available&&null!=o.live_deficit?o.live_deficit:Number(null!==(i=e.bucket)&&void 0!==i?i:0);return a>0&&r<n}_formatRunTime(e){if(!this.hass)return"";const t=this.hass.language,s=new Date(e),i=Xa(s),a=new Date;return Qa(s,a)?`${Oa("panels.zones.outlook.today",t)} ${i}`:Qa(s,function(e,t){const s=new Date(e.getTime());return s.setDate(s.getDate()+t),s}(a,1))?`${Oa("panels.zones.outlook.tomorrow",t)} ${i}`:function(e,t){const s=Ya(e);return`${new Intl.DateTimeFormat(t,{weekday:"short"}).format(s)} ${Xa(s)}`}(s,t)}_renderEstimatedTag(e){if(!this.hass||!e.estimated)return W``;const t=this.hass.language;return W`<span
      class="estimate-tag"
      title="${Oa("panels.zones.outlook.estimated_help",t)}"
      >${Oa("panels.zones.outlook.estimated",t)}<ha-icon
        icon="mdi:information-outline"
      ></ha-icon
    ></span>`}_guardLabel(e){return Oa(`panels.zones.outlook.checks.${e.id}`,this.hass.language)}_guardDetail(e){var t;return e.available&&null!==e.observed?Oa(`panels.zones.outlook.check_detail.${e.id}`,this.hass.language,"{observed}",String(e.observed),"{threshold}",String(null!==(t=e.threshold)&&void 0!==t?t:"")):""}_renderSkipReasons(){const e=this.hass.language;return W`
      <div class="outlook-line outlook-skip-reasons">
        <ul class="skip-reasons">
          ${this._triggeredGuards.map(e=>{const t=this._guardDetail(e);return W`<li>
              ${this._guardLabel(e)}${t?W` — ${t}`:""}
            </li>`})}
        </ul>
      </div>
      <div class="outlook-line outlook-dim skip-reasons-note">
        ${Oa("panels.zones.outlook.provisional",e)}
      </div>
    `}_openSchedules(){Na(0,Ga("setup","when-to-water"))}_runActionLabel(e){return Oa(`panels.zones.outlook.actions.${e.action}`,this.hass.language)}_runTargetsLabel(e){const t=this.hass.language;if("all"===e.zones)return Oa("panels.zones.outlook.targets_all",t);const s=Array.isArray(e.zones)?e.zones.length:0;return Oa("panels.zones.outlook.targets_zones",t,"{count}",String(s))}_renderOutlookBanner(){if(!this.hass||!this._outlook)return W``;const e=this.hass.language,t=this._nextIrrigateRun,s=this._triggeredGuards,i=this._outlook.last_skip_evaluation;return t&&t.next_run_utc?W`
      <ha-card class="outlook-card">
        <div class="outlook">
          <div class="outlook-line outlook-headline">
            <ha-icon icon="mdi:calendar-clock"></ha-icon>
            <span>
              <strong
                >${Oa("panels.zones.outlook.next_run",e)}:</strong
              >
              ${this._runActionLabel(t)}
              ${this._formatRunTime(t.next_run_utc)}
              ${this._renderEstimatedTag(t)}
              <span class="outlook-dim"
                >· ${t.name} · ${this._runTargetsLabel(t)}</span
              >
            </span>
          </div>

          ${s.length>0?W`
                <div class="outlook-line outlook-skip">
                  <ha-icon icon="mdi:alert"></ha-icon>
                  <span
                    >${Oa("panels.zones.outlook.will_skip",e)}</span
                  >
                  <button
                    class="outlook-info-btn"
                    aria-expanded="${this._skipDetailsOpen}"
                    title="${Oa("panels.zones.outlook.why_skipped",e)}"
                    @click="${()=>{this._skipDetailsOpen=!this._skipDetailsOpen}}"
                  >
                    <ha-icon
                      icon="${this._skipDetailsOpen?"mdi:chevron-up":"mdi:information-outline"}"
                    ></ha-icon>
                    <span class="outlook-info-label"
                      >${Oa("panels.zones.outlook.why_skipped",e)}</span
                    >
                  </button>
                </div>
                ${this._skipDetailsOpen?this._renderSkipReasons():""}
              `:W`
                <div class="outlook-line outlook-clear">
                  <ha-icon icon="mdi:check-circle-outline"></ha-icon>
                  <span
                    >${Oa("panels.zones.outlook.will_run",e)}</span
                  >
                </div>
              `}
          ${i?this._renderLastRunLine(i):""}
        </div>
      </ha-card>
    `:W`
        <ha-card class="outlook-card">
          <div class="outlook">
            <div class="outlook-line outlook-headline">
              <ha-icon icon="mdi:calendar-alert"></ha-icon>
              <span>${Oa("panels.zones.outlook.no_schedule",e)}</span>
              ${this.hideSettingsLinks?"":W`
                    <button
                      class="outlook-link"
                      @click="${this._openSchedules}"
                    >
                      ${Oa("panels.zones.outlook.setup_schedule",e)}
                    </button>
                  `}
            </div>
            ${i?this._renderLastRunLine(i):""}
          </div>
        </ha-card>
      `}_renderRainDelay(){if(!this.hass||"none"===this.actionsMode)return W``;const e=this.hass.language,t=this._rainDelayUntil;return t?W`
        <ha-card class="rain-delay-card paused">
          <div class="rain-delay">
            <ha-icon icon="mdi:pause-circle"></ha-icon>
            <span class="rain-delay-msg">
              <strong
                >${Oa("panels.zones.rain_delay.paused",e)}</strong
              >
              ${Oa("panels.zones.rain_delay.until",e)}
              ${Ja(t.toISOString())}
            </span>
            <button class="action-btn" @click="${()=>this._clearRainDelay()}">
              <ha-icon icon="mdi:play"></ha-icon>
              ${Oa("panels.zones.rain_delay.resume",e)}
            </button>
          </div>
        </ha-card>
      `:W`
      <div class="rain-delay-row">
        <span class="rain-delay-label">
          <ha-icon icon="mdi:weather-rainy"></ha-icon>
          ${Oa("panels.zones.rain_delay.title",e)}
        </span>
        <button class="action-btn" @click="${()=>this._setRainDelay(24)}">
          ${Oa("panels.zones.rain_delay.delay_24h",e)}
        </button>
        <button class="action-btn" @click="${()=>this._setRainDelay(48)}">
          ${Oa("panels.zones.rain_delay.delay_48h",e)}
        </button>
      </div>
    `}_renderLastRunLine(e){const t=this.hass.language,s=function(e,t){const s=Ya(e).getTime()-Date.now(),i=new Intl.RelativeTimeFormat(t,{numeric:"auto"}),a=Math.round(s/1e3);if(Math.abs(a)<60)return i.format(a,"second");const n=Math.round(a/60);if(Math.abs(n)<60)return i.format(n,"minute");const o=Math.round(n/60);if(Math.abs(o)<24)return i.format(o,"hour");const r=Math.round(o/24);if(Math.abs(r)<30)return i.format(r,"day");const l=Math.round(r/30);return Math.abs(l)<12?i.format(l,"month"):i.format(Math.round(l/12),"year")}(e.timestamp,t),i=e.checks.filter(e=>e.enabled&&e.would_skip).map(e=>this._guardLabel(e).toLowerCase()).join(", "),a=e.would_skip?`${Oa("panels.zones.outlook.last_run_skipped",t)}${i?` (${i})`:""}`:Oa("panels.zones.outlook.last_run_ran",t);return W`
      <div class="outlook-line outlook-last">
        <span class="outlook-dim"
          >${Oa("panels.zones.outlook.last_run",t)}:</span
        >
        <span>${a} · ${s}</span>
      </div>
    `}_renderZoneDecision(e){var t;if(!this.hass)return W``;const s=this.hass.language,i=null!==(t=e.duration)&&void 0!==t?t:0;let a,n,o,r;if(e.state===Za.Disabled)a=Oa("panels.zones.status.decision_disabled",s),n="neutral",o="mdi:power-off";else if(e.last_calculated)if(this._zoneHasDeficit(e)){const t=Ra(i),l=this._triggeredGuards,d=this._nextIrrigateRunForZone(e);l.length>0?(a=Oa("panels.zones.status.decision_water_skip",s,"{duration}",t,"{reason}",this._guardLabel(l[0]).toLowerCase()),n="skip",o="mdi:weather-rainy"):d&&d.next_run_utc?(a=Oa("panels.zones.status.decision_water_at",s,"{duration}",t,"{time}",this._formatRunTime(d.next_run_utc)),n="water",o="mdi:water",r=d):(a=Oa("panels.zones.status.decision_water_no_schedule",s,"{duration}",t),n="water",o="mdi:water-alert")}else a=Oa("panels.zones.status.decision_no_water",s),n="ok",o="mdi:check-circle-outline";else a=Oa("panels.zones.status.decision_unknown",s),n="unknown",o="mdi:help-circle-outline";return W`
      <div class="zone-decision ${n}">
        <ha-icon icon="${o}"></ha-icon>
        <span>${a}</span>
        ${r?this._renderEstimatedTag(r):""}
      </div>
    `}_zoneEstimate(e){var t,s;if(void 0!==e.id)return null===(s=null===(t=this._outlook)||void 0===t?void 0:t.zone_estimates)||void 0===s?void 0:s[String(e.id)]}_zoneFault(e){var t,s;if(void 0!==e.id)return null===(s=null===(t=this._outlook)||void 0===t?void 0:t.zone_faults)||void 0===s?void 0:s[String(e.id)]}_renderZoneFault(e){if(!this.hass)return W``;const t=this._zoneFault(e);if(!t)return W``;const s=this.hass.language,i=Oa(`panels.zones.fault.${t.reason}`,s)||Oa("panels.zones.fault.generic",s),a=t.timestamp?Ja(t.timestamp):"";return W`
      <div class="zone-fault" title="${a}">
        <ha-icon icon="mdi:alert-circle"></ha-icon>
        <span>
          <strong>${Oa("panels.zones.fault.title",s)}</strong>
          — ${i}
        </span>
      </div>
    `}_zoneSkip(e){var t,s;if(void 0!==e.id)return null===(s=null===(t=this._outlook)||void 0===t?void 0:t.zone_skips)||void 0===s?void 0:s[String(e.id)]}_renderZoneSkip(e){if(!this.hass)return W``;const t=this._zoneSkip(e);if(!t)return W``;const s=this.hass.language,i=Oa("panels.zones.skip.soil_moisture",s,"{observed}",String(t.observed),"{threshold}",String(t.threshold)),a=t.timestamp?Ja(t.timestamp):"";return W`
      <div class="zone-skip" title="${a}">
        <ha-icon icon="mdi:water-off"></ha-icon>
        <span>
          <strong>${Oa("panels.zones.skip.title",s)}</strong>
          — ${i}
        </span>
      </div>
    `}_durationClamped(e){var t,s;if(e.state!==Za.Automatic)return!1;const i=e.maximum_duration;if(null==i||i<0)return!1;const a=null!==(t=e.duration)&&void 0!==t?t:0;return!(a<=0)&&a-(null!==(s=e.lead_time)&&void 0!==s?s:0)>=i}_renderDurationClamped(e){var t;if(!this.hass||!this._durationClamped(e))return W``;const s=this.hass.language,i=Oa("panels.zones.clamped.detail",s,"{maximum}",Ra(null!==(t=e.maximum_duration)&&void 0!==t?t:0));return W`
      <div class="zone-clamped" title="${i}">
        <ha-icon icon="mdi:timer-alert-outline"></ha-icon>
        <span>
          <strong>${Oa("panels.zones.clamped.title",s)}</strong>
          <ha-icon
            class="clamped-hint"
            icon="mdi:information-outline"
          ></ha-icon>
        </span>
      </div>
    `}_renderZoneEstimate(e){if(!this.hass)return W``;const t=this._zoneEstimate(e);if(!t||!t.available||null==t.live_deficit)return W``;const s=this.hass.language,i=Ma(this.config,ft),a=t.live_deficit<0?"var(--warning-color)":"var(--success-color)",n=Oa(`panels.zones.status.estimate_method.${"proxy"===t.method||"hourly_sensor"===t.method?t.method:"hourly"}`,s)+(t.as_of?` · ${Xa(t.as_of)}`:"");return W`
      <span class="status-sep">·</span>
      <span class="zone-estimate" title="${n}">
        ${Oa("panels.zones.status.estimate_now",s)}
        <strong style="color: ${a}"
          >≈ ${t.live_deficit.toFixed(2)} ${i}</strong
        >
        <span class="estimate-tag"
          >${Oa("panels.zones.status.estimate_tag",s)}</span
        >
      </span>
    `}_renderZoneNextRun(e){if(!this.hass)return W``;const t=this._nextIrrigateRunForZone(e);if(!t||!t.next_run_utc)return W``;return e.state!==Za.Disabled&&e.last_calculated&&this._zoneHasDeficit(e)&&0===this._triggeredGuards.length?W``:W`
      <span class="status-sep">·</span>
      <span>
        ${Oa("panels.zones.outlook.next_run",this.hass.language)}:
        <strong>${this._formatRunTime(t.next_run_utc)}</strong>
        ${this._renderEstimatedTag(t)}
      </span>
    `}renderZone(e,t){var s;if(!this.hass)return W``;const i=Number(null!==(s=e.bucket)&&void 0!==s?s:0),a=i<0?"var(--warning-color)":"var(--success-color)",n=e.state===Za.Automatic?"state-automatic":e.state===Za.Manual?"state-manual":"state-disabled",o=e.last_calculated?Ja(e.last_calculated):Oa("panels.zones.status.never",this.hass.language);return W`
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          <span class="zone-state-badge ${n}">
            ${Oa(`panels.zones.labels.states.${e.state}`,this.hass.language)}
          </span>
          ${this.hideSettingsLinks?"":W`
                <ha-icon-button
                  .path="${"M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"}"
                  title="${Oa("panels.zones.actions.open_settings",this.hass.language)}"
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
              title="${Oa("panels.zones.help.bucket",this.hass.language)}"
            >
              ${Oa("panels.zones.labels.bucket",this.hass.language)}:
              <strong style="color: ${a}"
                >${i.toFixed(2)}
                ${Ma(this.config,ft)}</strong
              >
            </span>
            <span class="status-sep">·</span>
            <span>
              ${Oa("panels.zones.status.last_checked",this.hass.language)}:
              <strong>${o}</strong>
            </span>
            ${this._renderZoneEstimate(e)} ${this._renderZoneNextRun(e)}
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div class="card-content zone-action-bar">
          ${"full"===this.actionsMode&&e.state===Za.Automatic?W`
                <button
                  class="action-btn"
                  title="${Oa("panels.zones.help.update",this.hass.language)}"
                  @click="${()=>this.handleUpdateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${Oa("panels.zones.actions.update",this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${Oa("panels.zones.help.calculate",this.hass.language)}"
                  @click="${()=>this.handleCalculateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${Oa("panels.zones.actions.calculate",this.hass.language)}
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
                  ${Oa("panels.zones.labels.irrigate_now",this.hass.language)}
                </button>
              `:this._canActuate(e)?"":W`
                  <button
                    class="action-btn"
                    disabled
                    title="${Oa("panels.zones.help.irrigate_link_entity",this.hass.language)}"
                  >
                    <ha-icon icon="mdi:water"></ha-icon>
                    ${Oa("panels.zones.labels.irrigate_now",this.hass.language)}
                  </button>
                  <span class="zones-top-note">
                    ${Oa("panels.zones.help.irrigate_link_entity",this.hass.language)}
                  </span>
                `}
          ${this._renderRunZoneControl(e)}
        </div>
      </ha-card>
    `}_renderRunZoneControl(e){if(!this.hass||"none"===this.actionsMode||!this._canActuate(e)||void 0===e.id)return W``;const t=this.hass.language,s=String(e.id),i=this._activeRun(e);if(i){const s=this._runSecondsLeft(i);return W`
        <div class="run-zone-control running">
          <span class="run-zone-countdown">
            <ha-icon icon="mdi:water-pump"></ha-icon>
            ${null===s?Oa("panels.zones.stop_zone.watering",t):this._formatCountdown(s)}
          </span>
          <button
            class="action-btn stop-btn"
            @click="${()=>this._stopZone(e)}"
          >
            <ha-icon icon="mdi:stop"></ha-icon>
            ${Oa("panels.zones.stop_zone.stop",t)}
          </button>
        </div>
      `}const a=this._distributorBusy(e);return W`
      <div class="run-zone-control-wrap">
        <div
          class="run-zone-control"
          title="${Oa("panels.zones.run_zone.help",t)}"
        >
          <input
            class="run-zone-input"
            type="number"
            min="1"
            max="600"
            .value="${String(this._zoneRunMinutes(e))}"
            ?disabled="${a}"
            @input="${e=>{const t=Number(e.target.value);this._runMinutes=Object.assign(Object.assign({},this._runMinutes),{[s]:t})}}"
          />
          <span class="run-zone-unit"
            >${Oa("panels.zones.run_zone.minutes",t)}</span
          >
          <button
            class="action-btn"
            @click="${()=>this._runZoneFor(e)}"
            ?disabled="${this.isSaving||a}"
          >
            <ha-icon icon="mdi:timer-play-outline"></ha-icon>
            ${Oa("panels.zones.run_zone.run",t)}
          </button>
        </div>
        ${a?W`<span class="run-zone-busy-hint">
              ${Oa("panels.zones.run_zone.busy_hint",t)}
            </span>`:""}
      </div>
    `}_formatCountdown(e){const t=Math.max(0,e),s=Math.floor(t/3600),i=Math.floor(t%3600/60),a=t%60,n=e=>String(e).padStart(2,"0");return s>0?`${s}:${n(i)}:${n(a)}`:`${i}:${n(a)}`}render(){var e,t;if(!this.hass)return W``;if(this.isLoading)return W`
        <ha-card header="${Oa("panels.zones.title",this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Oa("common.loading-messages.general",this.hass.language)}
            </div>
          </div>
        </ha-card>
      `;const s=this.zones.some(e=>{var t;return this._canActuate(e)&&(null!==(t=e.duration)&&void 0!==t?t:0)>0}),i=0===this.zones.length;return W`
      ${i?this.hideSettingsLinks?W`
              <ha-card>
                <div class="card-content description-text">
                  ${Oa("panels.zones.no_items",this.hass.language)}
                </div>
              </ha-card>
            `:W`
              <ha-card class="setup-banner-card">
                <div class="setup-banner">
                  <div class="setup-banner-icon">🌱</div>
                  <div class="setup-banner-content">
                    <div class="setup-banner-title">
                      ${Oa("wizard.title",this.hass.language)}
                    </div>
                    <div class="setup-banner-desc">
                      ${Oa("wizard.setup_complete_banner",this.hass.language)}
                    </div>
                  </div>
                  <button
                    class="action-btn setup-banner-btn"
                    @click="${()=>{this.dispatchEvent(new CustomEvent("open-wizard",{bubbles:!0,composed:!0}))}}"
                  >
                    ${Oa("wizard.open_wizard",this.hass.language)}
                  </button>
                </div>
              </ha-card>
            `:""}
      ${i?"":this._renderOutlookBanner()}
      ${i?"":this._renderRainDelay()}

      <!-- Zones header card: run-all operational actions -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${Oa("panels.zones.title",this.hass.language)}
          </div>
        </div>
        <div class="card-content zones-top-actions">
          ${"full"===this.actionsMode?W`
                <button
                  class="action-btn"
                  title="${Oa("panels.zones.help.update_all",this.hass.language)}"
                  @click="${this.handleUpdateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:update"></ha-icon>
                  ${Oa("panels.zones.cards.zone-actions.actions.update-all",this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  title="${Oa("panels.zones.help.calculate_all",this.hass.language)}"
                  @click="${this.handleCalculateAllZones}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon icon="mdi:calculator"></ha-icon>
                  ${Oa("panels.zones.cards.zone-actions.actions.calculate-all",this.hass.language)}
                </button>
              `:""}
          ${"none"!==this.actionsMode?W`
                <button
                  class="action-btn"
                  raised
                  title="${Oa("panels.zones.help.irrigate_all",this.hass.language)}"
                  @click="${()=>{this._confirmIrrigate="all"}}"
                  ?disabled="${!s||this.isSaving}"
                >
                  <ha-icon icon="mdi:water"></ha-icon>
                  ${Oa("panels.zones.actions.irrigate_all",this.hass.language)}
                </button>
              `:""}
          ${s?"":W`<span class="zones-top-note"
                >${Oa("panels.info.cards.irrigate_now.no_linked_zones",this.hass.language)}</span
              >`}
        </div>
      </ha-card>

      <!-- Irrigate confirmation dialog -->
      ${null!==this._confirmIrrigate?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmIrrigate=null}}"
              heading="${Oa("panels.zones.confirm_irrigate.title",this.hass.language)}"
            >
              <p>
                ${Oa("panels.zones.confirm_irrigate.body",this.hass.language)}
              </p>
              <p>
                <strong>
                  ${"all"===this._confirmIrrigate?`${Oa("panels.zones.confirm_irrigate.all_linked_zones",this.hass.language)} (${this._linkedZoneCount})`:null!==(t=null===(e=this.zones.find(e=>{var t;return(null===(t=e.id)||void 0===t?void 0:t.toString())===this._confirmIrrigate}))||void 0===e?void 0:e.name)&&void 0!==t?t:this._confirmIrrigate}
                </strong>
              </p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmIrrigate=null}}"
                >
                  ${Oa("common.actions.cancel",this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._doIrrigate}"
                >
                  ${Oa("panels.zones.labels.irrigate_now",this.hass.language)}
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
                  aria-label="${Oa("common.actions.cancel",this.hass.language)}"
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
    `}}t([pe()],en.prototype,"config",void 0),t([pe({type:Boolean})],en.prototype,"hideSettingsLinks",void 0),t([pe({attribute:!1})],en.prototype,"actionsMode",void 0),t([pe({type:Array})],en.prototype,"zones",void 0),t([ge()],en.prototype,"_outlook",void 0),t([ge()],en.prototype,"_distributors",void 0),t([pe({type:Boolean})],en.prototype,"isLoading",void 0),t([pe({type:Boolean})],en.prototype,"isSaving",void 0),t([ge()],en.prototype,"_operationError",void 0),t([ge()],en.prototype,"_confirmIrrigate",void 0),t([ge()],en.prototype,"_skipDetailsOpen",void 0),t([ge()],en.prototype,"_runMinutes",void 0),t([ge()],en.prototype,"_now",void 0),customElements.get("smart-irrigation-view-zones")||customElements.define("smart-irrigation-view-zones",en)
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */;const tn={},sn=Xs(class extends Js{constructor(e){if(super(e),e.type!==Vs&&e.type!==Gs&&e.type!==Ys)throw Error("The `live` directive is not allowed on child or event bindings");if(!(e=>void 0===e.strings)(e))throw Error("`live` bindings can only contain a single expression")}render(e){return e}update(e,[t]){if(t===Z||t===q)return t;const s=e.element,i=e.name;if(e.type===Vs){if(t===s[i])return Z}else if(e.type===Ys){if(!!t===s.hasAttribute(i))return Z}else if(e.type===Gs&&s.getAttribute(i)===t+"")return Z;return((e,t=tn)=>{e._$AH=t;
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */})(e),t}});let an=class extends le{constructor(){super(...arguments),this.label="",this.unit="",this.help="",this.required=!1,this._helpOpen=!1}_toggleHelp(){this._helpOpen=!this._helpOpen}render(){return W`
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
    `}};t([pe()],an.prototype,"label",void 0),t([pe()],an.prototype,"unit",void 0),t([pe()],an.prototype,"help",void 0),t([pe({type:Boolean})],an.prototype,"required",void 0),t([ge()],an.prototype,"_helpOpen",void 0),an=t([ce("si-field")],an);let nn=class extends le{constructor(){super(...arguments),this.useWeather=!1,this.service=ze,this.apiKey="",this.weatherConfig=null,this._testing=!1,this._testResult=null,this._testResultTimer=null}disconnectedCallback(){super.disconnectedCallback(),this._testResultTimer&&(clearTimeout(this._testResultTimer),this._testResultTimer=null)}_emit(e,t){this.dispatchEvent(new CustomEvent(e,{detail:{value:t},bubbles:!0,composed:!0}))}get _noApiKeyServices(){var e,t;return null!==(t=null===(e=this.weatherConfig)||void 0===e?void 0:e.no_api_key_services)&&void 0!==t?t:[ze]}get _needsKey(){return this.useWeather&&!!this.service&&!this._noApiKeyServices.includes(this.service)}get _hasStoredKey(){const e=this.weatherConfig;return this.service===xe?!!(null==e?void 0:e.has_owm_api_key):this.service===ke?!!(null==e?void 0:e.has_pw_api_key):this.service===Se&&!!(null==e?void 0:e.has_met_api_key)}async _testApiKey(){if(this.hass&&!this._testing){this._testing=!0,this._testResult=null,this._testResultTimer&&(clearTimeout(this._testResultTimer),this._testResultTimer=null);try{this._testResult=await(e=this.hass,t=this.service,s=this.apiKey||null,e.callWS({type:fe+"/weather_config_test",weather_service:null!=t?t:null,api_key:null!=s?s:null})),this._testResultTimer=window.setTimeout(()=>{this._testResult=null,this._testResultTimer=null},12e3)}catch(e){this._testResult={success:!1,error:"unknown"}}finally{this._testing=!1}var e,t,s}}render(){var e,t;const s=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";return W`
      <si-field
        label="${Oa("weather_service_config.enabled_label",s)}"
      >
        <ha-switch
          .checked="${this.useWeather}"
          @change="${e=>this._emit("useweather-changed",e.target.checked)}"
        ></ha-switch>
      </si-field>

      ${this.useWeather?this._renderServiceAndKey(s):""}
    `}_renderServiceAndKey(e){return W`
      <si-field
        label="${Oa("weather_service_config.service_label",e)}"
      >
        <select
          class="si-input"
          .value="${sn(this.service||ze)}"
          @change="${e=>{this._testResult=null,this._emit("service-changed",e.target.value)}}"
        >
          <option
            value="${ze}"
            ?selected="${(this.service||ze)===ze}"
          >
            ${Oa("weather_service_config.openmeteo",e)}
          </option>
          <option
            value="${xe}"
            ?selected="${this.service===xe}"
          >
            ${Oa("weather_service_config.owm",e)}
          </option>
          <option
            value="${ke}"
            ?selected="${this.service===ke}"
          >
            ${Oa("weather_service_config.pw",e)}
          </option>
          <option
            value="${Se}"
            ?selected="${this.service===Se}"
          >
            ${Oa("weather_service_config.met",e)}
          </option>
        </select>
      </si-field>

      ${this._needsKey?this._renderKeyField(e):W`<div class="info-note">
            ${Oa("weather_service_config.no_api_key_needed",e)}
          </div>`}
    `}_renderKeyField(e){var t;const s=this._hasStoredKey;return W`
      <si-field
        label="${Oa("weather_service_config.api_key_label",e)}"
        help="${Oa("weather_service_config.api_key_help",e)}"
      >
        <span class="api-badge ${s?"configured":"missing"}"
          >${Oa(s?"weather_service_config.api_key_configured":"weather_service_config.api_key_not_configured",e)}</span
        >
        <div class="api-row">
          <input
            type="password"
            class="si-input flex1"
            placeholder="${Oa("weather_service_config.api_key_placeholder",e)}"
            .value="${this.apiKey}"
            @input="${e=>{this._testResult=null,this._emit("apikey-changed",e.target.value)}}"
          />
          <button
            class="test-btn"
            type="button"
            ?disabled="${this._testing||!this.apiKey&&!s}"
            @click="${this._testApiKey}"
          >
            ${this._testing?Oa("weather_service_config.test_button_testing",e):Oa("weather_service_config.test_button",e)}
          </button>
        </div>
        ${null!==this._testResult?W`<div
              class="test-result ${this._testResult.success?"success":"error"}"
            >
              ${this._testResult.success?Oa("weather_service_config.test_success",e):Oa("weather_service_config.test_error_"+(null!==(t=this._testResult.error)&&void 0!==t?t:"unknown"),e)}
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
    `}};t([pe({attribute:!1})],nn.prototype,"hass",void 0),t([pe({type:Boolean})],nn.prototype,"useWeather",void 0),t([pe()],nn.prototype,"service",void 0),t([pe()],nn.prototype,"apiKey",void 0),t([pe({attribute:!1})],nn.prototype,"weatherConfig",void 0),t([ge()],nn.prototype,"_testing",void 0),t([ge()],nn.prototype,"_testResult",void 0),nn=t([ce("si-weather-source-config")],nn);let on=class extends(Fa(le)){constructor(){super(...arguments),this.section="all",this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._weatherConfig=null,this._weatherService=null,this._useWeatherService=!1,this._newApiKey="",this._weatherSaving=!1,this._coords=null,this._coordsEnabled=!1,this._coordsLat="",this._coordsLon="",this._coordsElev="",this._coordsSaving=!1,this._saveStatus="idle",this._savedResetTimer=null,this._updateScheduled=!1,this.debouncedSave=(()=>{let e=null,t={};return s=>{t=Object.assign(Object.assign({},t),s),e&&clearTimeout(e),e=window.setTimeout(()=>{const s=t;t={},e=null,this.saveData(s)},500)}})()}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:fe+"_config_updated"})]}async _fetchData(){var e;if(!this.hass)return;const t=!this._initialLoadDone;t&&(this.isLoading=!0,this._scheduleUpdate());try{const[t,a,n]=await Promise.all([Es(this.hass),Us(this.hass),Fs(this.hass)]);this.config=t,this._weatherConfig=a,this._useWeatherService=a.use_weather_service,this._weatherService=null!==(e=a.weather_service)&&void 0!==e?e:ze,this._applyCoordinates(n),this.data=(s=this.config,i=["calctime","autocalcenabled","autocalcmode","autoupdateenabled","autoupdateschedule","autoupdatefirsttime","autoupdateinterval","days_between_irrigation"],s?Object.entries(s).filter(([e])=>i.includes(e)).reduce((e,[t,s])=>Object.assign(e,{[t]:s}),{}):{}),this._initialLoadDone=!0}catch(e){console.error("Error fetching data:",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{t&&(this.isLoading=!1),this._scheduleUpdate()}var s,i}firstUpdated(){qs().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}render(){var e,t;return this.hass&&this.config&&this.data?this.isLoading?W`<div class="loading-indicator">
        ${Oa("common.loading-messages.general",this.hass.language)}
      </div>`:W`${this._renderSaveStatus()} ${this._renderCards()}`:W`<div class="loading-indicator">
        ${Oa("common.loading-messages.configuration",null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en")}
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
        ${Oa(`panels.general.sections.${e}`,this.hass.language)}
      </div>
    `:W``}async _saveWeatherConfig(){if(this.hass){this._weatherSaving=!0,this._scheduleUpdate();try{await js(this.hass,this._useWeatherService,this._useWeatherService?this._weatherService:null,this._newApiKey||null),this._newApiKey="",await this._fetchData()}catch(e){console.error("Failed to save weather config:",e),Ba(this,this.hass,"common.errors.save_failed",e)}finally{this._weatherSaving=!1,this._scheduleUpdate()}}}_renderWeatherServiceCard(){var e;return this.hass?W`
      <ha-card
        header="${Oa("weather_service_config.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("weather_service_config.description",this.hass.language)}
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
              ${this._weatherSaving?Oa("common.saving-messages.saving",this.hass.language):Oa("weather_service_config.save_button",this.hass.language)}
            </button>
          </div>
        </div>
      </ha-card>
    `:W``}_renderAutoUpdateCard(){var e,t;return this.hass&&this.config&&this.data?W`
      <ha-card
        header="${Oa("panels.general.cards.automatic-update.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("panels.general.cards.automatic-update.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Oa("panels.general.cards.automatic-update.labels.auto-update-enabled",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.autoupdateenabled}"
              @change="${e=>this.handleConfigChange({autoupdateenabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.data.autoupdateenabled?W`
                <div class="setting-row">
                  <label>
                    ${Oa("panels.general.cards.automatic-update.labels.auto-update-interval",this.hass.language)}
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
                      .value="${sn(this.data.autoupdateschedule||Ee)}"
                      @change="${e=>this.handleConfigChange({autoupdateschedule:e.target.value})}"
                    >
                      <option
                        value="${Ae}"
                        ?selected="${(this.data.autoupdateschedule||Ee)===Ae}"
                      >
                        ${Oa("panels.general.cards.automatic-update.options.minutes",this.hass.language)}
                      </option>
                      <option
                        value="${Ee}"
                        ?selected="${(this.data.autoupdateschedule||Ee)===Ee}"
                      >
                        ${Oa("panels.general.cards.automatic-update.options.hours",this.hass.language)}
                      </option>
                      <option
                        value="${Ce}"
                        ?selected="${this.data.autoupdateschedule===Ce}"
                      >
                        ${Oa("panels.general.cards.automatic-update.options.days",this.hass.language)}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="setting-row">
                  <label>
                    ${Oa("panels.general.cards.automatic-update.labels.auto-update-delay",this.hass.language)}
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
        header="${Oa("panels.general.cards.automatic-duration-calculation.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("panels.general.cards.automatic-duration-calculation.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Oa("panels.general.cards.automatic-duration-calculation.labels.auto-calc-enabled",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.autocalcenabled}"
              @change="${e=>this.handleConfigChange({autocalcenabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.data.autocalcenabled?this._renderAutoCalcMode():""}
        </div>
      </ha-card>
    `:W``}_renderAutoCalcMode(){if(!this.hass||!this.config)return W``;const e=this.hass.language,t=ye.includes(this.config.autocalcmode)?this.config.autocalcmode:be;return W`
      <div class="setting-row">
        <label>
          ${Oa("panels.general.cards.automatic-duration-calculation.labels.calc-mode",e)}
        </label>
        <select
          class="settings-input"
          .value="${sn(t)}"
          @change="${e=>this.handleConfigChange({autocalcmode:e.target.value,autocalcenabled:!0})}"
        >
          ${ye.map(s=>W`
              <option value="${s}" ?selected="${t===s}">
                ${Oa(`panels.general.cards.automatic-duration-calculation.modes.${s}`,e)}
              </option>
            `)}
        </select>
      </div>
      ${t===be?W`
            <div class="setting-row">
              <label>
                ${Oa("panels.general.cards.automatic-duration-calculation.labels.calc-time",e)}
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
              ${Oa("panels.general.cards.automatic-duration-calculation.help.before-run",e)}
            </div>
          `}
    `}_renderRunHistoryLoggingCard(){return this.hass&&this.config?W`
      <ha-card
        header="${Oa("panels.general.cards.run-history-logging.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("panels.general.cards.run-history-logging.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Oa("panels.general.cards.run-history-logging.labels.log-no-demand",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.log_no_demand}"
              @change="${e=>this.handleConfigChange({log_no_demand:e.target.checked})}"
            ></ha-switch>
          </div>
        </div>
      </ha-card>
    `:W``}_renderWeatherSkipCard(){var e,t,s,i,a;if(!this.hass||!this.config||!this.data)return W``;const n=this.hass.language,o=this.config.skip_irrigation_on_precipitation?"skip":this.config.forecast_weighting_enabled?"water_less":"ignore";return W`
      <ha-card header="${Oa("weather_skip.title",this.hass.language)}">
        <div class="card-content description-text">
          ${Oa("weather_skip.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Oa("weather_skip.forecast_rain_label",n)}
            </label>
            <select
              class="settings-input"
              .value="${sn(o)}"
              @change="${e=>{const t=e.target.value;this.handleConfigChange({skip_irrigation_on_precipitation:"skip"===t,forecast_weighting_enabled:"water_less"===t})}}"
            >
              ${["ignore","water_less","skip"].map(e=>W`
                  <option value="${e}" ?selected="${o===e}">
                    ${Oa(`weather_skip.forecast_rain_options.${e}`,n)}
                  </option>
                `)}
            </select>
          </div>
          <div class="description-text">
            ${Oa(`weather_skip.forecast_rain_help.${o}`,n)}
          </div>
          ${"ignore"!==o?W`
                <div class="setting-row">
                  <label>
                    ${Oa("weather_skip.lookahead_label",n)}
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
                  ${Oa("weather_skip.lookahead_help",n)}
                </div>
              `:""}
          ${"skip"===o?W`
                <div class="setting-row">
                  <label>
                    ${Oa("weather_skip.threshold_label",n)}
                    (${Ma(this.config,we)})
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
            ${Oa("weather_skip.temp_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Oa("weather_skip.temp_section_title",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_on_temp_enabled}"
              @change="${e=>this.handleConfigChange({skip_on_temp_enabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_temp_enabled?W`
                <div class="setting-row">
                  <label>
                    ${Oa("weather_skip.temp_threshold_label",this.hass.language)}
                    (°C)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.5"
                    .value="${null!==(s=this.config.temp_threshold)&&void 0!==s?s:5}"
                    @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({temp_threshold:t})}}"
                  />
                </div>
              `:""}

          <div class="section-divider">
            ${Oa("weather_skip.wind_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Oa("weather_skip.wind_section_title",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_on_wind_enabled}"
              @change="${e=>this.handleConfigChange({skip_on_wind_enabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_wind_enabled?W`
                <div class="setting-row">
                  <label>
                    ${Oa("weather_skip.wind_threshold_label",this.hass.language)}
                    (m/s)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="0.1"
                    inputmode="decimal"
                    .value="${null!==(i=this.config.wind_threshold)&&void 0!==i?i:6.9}"
                    @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({wind_threshold:t})}}"
                  />
                </div>
              `:""}

          <div class="section-divider">
            ${Oa("weather_skip.freeze_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Oa("weather_skip.freeze_section_title",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_on_freeze_enabled}"
              @change="${e=>this.handleConfigChange({skip_on_freeze_enabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_freeze_enabled?W`
                <div class="setting-row">
                  <label>
                    ${Oa("weather_skip.freeze_threshold_label",this.hass.language)}
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
                  ${Oa("weather_skip.freeze_help",this.hass.language)}
                </div>
              `:""}

          <div class="section-divider">
            ${Oa("weather_skip.rain_sensor_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Oa("weather_skip.rain_sensor_label",this.hass.language)}
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
    `}_applyCoordinates(e){this._coords=e,this._coordsEnabled=e.manual_coordinates_enabled;const t=(e,t)=>null!=e?String(e):null!=t?String(t):"";this._coordsLat=t(e.manual_latitude,e.ha_latitude),this._coordsLon=t(e.manual_longitude,e.ha_longitude),this._coordsElev=t(e.manual_elevation,e.ha_elevation)}async _saveCoordinates(){if(this.hass){this._coordsSaving=!0,this._scheduleUpdate();try{await(e=this.hass,t=this._coordsEnabled,s=this._coordsEnabled?parseFloat(this._coordsLat):null,i=this._coordsEnabled?parseFloat(this._coordsLon):null,a=this._coordsEnabled?parseFloat(this._coordsElev):null,e.callWS({type:fe+"/coordinates_save",manual_coordinates_enabled:t,manual_latitude:null!=s?s:null,manual_longitude:null!=i?i:null,manual_elevation:null!=a?a:null})),this._applyCoordinates(await Fs(this.hass))}catch(e){console.error("Failed to save coordinates:",e),Ba(this,this.hass,"common.errors.save_failed",e)}finally{this._coordsSaving=!1,this._scheduleUpdate()}var e,t,s,i,a}}_renderCoordinateCard(){var e,t,s;if(!this.hass||!this._coords)return W``;const i=this._coords;return W`
      <ha-card
        header="${Oa("coordinate_config.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("coordinate_config.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Oa("coordinate_config.manual_enabled",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this._coordsEnabled}"
              @change="${e=>{this._coordsEnabled=e.target.checked}}"
            ></ha-switch>
          </div>
          ${this._coordsEnabled?W`
                <div class="setting-row">
                  <label>
                    ${Oa("coordinate_config.latitude",this.hass.language)}
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
                    ${Oa("coordinate_config.longitude",this.hass.language)}
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
                    ${Oa("coordinate_config.elevation",this.hass.language)}
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
                  ${Oa("coordinate_config.current_ha_coords",this.hass.language)}:
                  ${Oa("coordinate_config.latitude",this.hass.language)}:
                  ${null!==(e=i.ha_latitude)&&void 0!==e?e:0},
                  ${Oa("coordinate_config.longitude",this.hass.language)}:
                  ${null!==(t=i.ha_longitude)&&void 0!==t?t:0},
                  ${Oa("coordinate_config.elevation",this.hass.language)}:
                  ${null!==(s=i.ha_elevation)&&void 0!==s?s:0}m
                </div>
              `}
          <div style="margin-top: 12px;">
            <button
              class="action-btn"
              raised
              ?disabled="${this._coordsSaving}"
              @click="${this._saveCoordinates}"
            >
              ${this._coordsSaving?Oa("common.saving-messages.saving",this.hass.language):Oa("common.actions.save",this.hass.language)}
            </button>
          </div>
        </div>
      </ha-card>
    `}_renderDaysBetweenIrrigationCard(){var e;return this.hass&&this.config&&this.data?W`
      <ha-card
        header="${Oa("days_between_irrigation.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("days_between_irrigation.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Oa("days_between_irrigation.label",this.hass.language)}
              <div class="setting-description">
                ${Oa("days_between_irrigation.help_text",this.hass.language)}
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
    `:W``}_renderZoneSequencingCard(){var e,t;if(!this.hass||!this.config||!this.data)return W``;const s=(this.config.zone_sequencing||Ft)===Wt;return W`
      <ha-card
        header="${Oa("zone_sequencing.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Oa("zone_sequencing.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Oa("zone_sequencing.title",this.hass.language)}
            </label>
            <select
              class="settings-input"
              .value="${sn(this.config.zone_sequencing||Ft)}"
              @change="${e=>this.handleConfigChange({[Ut]:e.target.value})}"
            >
              <option
                value="${Ft}"
                ?selected="${(this.config.zone_sequencing||Ft)===Ft}"
              >
                ${Oa("zone_sequencing.parallel",this.hass.language)}
              </option>
              <option
                value="${jt}"
                ?selected="${this.config.zone_sequencing===jt}"
              >
                ${Oa("zone_sequencing.sequential",this.hass.language)}
              </option>
              <option
                value="${Wt}"
                ?selected="${this.config.zone_sequencing===Wt}"
              >
                ${Oa("zone_sequencing.rotating",this.hass.language)}
              </option>
            </select>
          </div>
          ${s?W`
                <div class="setting-row">
                  <label>
                    ${Oa("zone_sequencing.max_consecutive_duration_label",this.hass.language)}
                  </label>
                  <input
                    type="number"
                    min="1"
                    class="settings-input"
                    .value="${null!==(e=this.config.zone_sequencing_max_consecutive_duration)&&void 0!==e?e:5}"
                    @input="${e=>{const t=parseInt(e.target.value,10);isNaN(t)||this.handleConfigChange({[Zt]:t})}}"
                  />
                  <span class="unit-label">
                    ${Oa("zone_sequencing.max_consecutive_duration_unit",this.hass.language)}
                  </span>
                </div>
                <div class="setting-row">
                  <label>
                    ${Oa("zone_sequencing.min_absorption_time_label",this.hass.language)}
                  </label>
                  <input
                    type="number"
                    min="0"
                    class="settings-input"
                    .value="${null!==(t=this.config.zone_sequencing_min_absorption_time)&&void 0!==t?t:0}"
                    @input="${e=>{const t=parseInt(e.target.value,10);isNaN(t)||this.handleConfigChange({[qt]:t})}}"
                  />
                  <span class="unit-label">
                    ${Oa("zone_sequencing.min_absorption_time_unit",this.hass.language)}
                  </span>
                </div>
              `:""}
        </div>
      </ha-card>
    `}_renderMasterSwitchCard(){var e,t;if(!this.hass||!this.config)return W``;const s=!!this.config.master_kick_enabled;return W`
      <ha-card header="${Oa("master.title",this.hass.language)}">
        <div class="card-content description-text">
          ${Oa("master.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>${Oa("master.entity",this.hass.language)}</label>
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${this.config.master_entity||""}"
              .includeDomains="${["switch","valve","input_boolean"]}"
              allow-custom-entity
              @value-changed="${e=>this.handleConfigChange({[Gt]:e.detail.value||null})}"
            ></ha-entity-picker>
          </div>
          ${this.config.master_entity?W`
                <div class="setting-row">
                  <label
                    >${Oa("master.kick_enabled",this.hass.language)}</label
                  >
                  <ha-switch
                    .checked="${s}"
                    @change="${e=>this.handleConfigChange({[Vt]:e.target.checked})}"
                  ></ha-switch>
                </div>
                ${s?W`
                      <div class="setting-row">
                        <label>
                          ${Oa("master.kick_pause",this.hass.language)}
                        </label>
                        <input
                          type="number"
                          min="0"
                          step="0.1"
                          class="settings-input"
                          .value="${null!==(e=this.config.master_kick_pause_seconds)&&void 0!==e?e:1}"
                          @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({[Yt]:t})}}"
                        />
                        <span class="unit-label">
                          ${Oa("master.seconds_unit",this.hass.language)}
                        </span>
                      </div>
                    `:""}
                <div class="setting-row">
                  <label
                    >${Oa("master.settle",this.hass.language)}</label
                  >
                  <input
                    type="number"
                    min="0"
                    class="settings-input"
                    .value="${null!==(t=this.config.master_settle_seconds)&&void 0!==t?t:10}"
                    @input="${e=>{const t=parseInt(e.target.value,10);isNaN(t)||this.handleConfigChange({[Kt]:t})}}"
                  />
                  <span class="unit-label">
                    ${Oa("master.seconds_unit",this.hass.language)}
                  </span>
                </div>
                <div class="setting-row">
                  <label
                    >${Oa("master.off_after",this.hass.language)}</label
                  >
                  <ha-switch
                    .checked="${!!this.config.master_off_after}"
                    @change="${e=>this.handleConfigChange({[Xt]:e.target.checked})}"
                  ></ha-switch>
                </div>
              `:""}
        </div>
      </ha-card>
    `}async saveData(e){if(this.hass&&this.data){this.isSaving=!0,this._saveStatus="saving",this._scheduleUpdate();try{this.data=Object.assign(Object.assign({},this.data),e),this._scheduleUpdate(),await Cs(this.hass,this.data),this._markSaved()}catch(e){console.error("Error saving config:",e),this._saveStatus="idle",Ba(this,this.hass,"common.errors.save_failed",e),await this._fetchData()}finally{this.isSaving=!1,this._scheduleUpdate()}}}_markSaved(){this._saveStatus="saved",this._savedResetTimer&&clearTimeout(this._savedResetTimer),this._savedResetTimer=window.setTimeout(()=>{this._saveStatus="idle",this._scheduleUpdate()},2e3)}_renderSaveStatus(){if(!this.hass||"idle"===this._saveStatus)return W``;const e="saving"===this._saveStatus;return W`
      <div class="save-status-float ${this._saveStatus}">
        <ha-icon
          icon="${e?"mdi:content-save-outline":"mdi:check-circle"}"
        ></ha-icon>
        ${Oa(e?"common.saving-messages.saving":"panels.zones.status.saved",this.hass.language)}
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
    `}};t([pe()],on.prototype,"narrow",void 0),t([pe()],on.prototype,"path",void 0),t([pe()],on.prototype,"section",void 0),t([pe()],on.prototype,"data",void 0),t([pe()],on.prototype,"config",void 0),t([pe({type:Boolean})],on.prototype,"isLoading",void 0),t([pe({type:Boolean})],on.prototype,"isSaving",void 0),t([pe()],on.prototype,"_weatherConfig",void 0),t([pe()],on.prototype,"_weatherService",void 0),t([pe({type:Boolean})],on.prototype,"_useWeatherService",void 0),t([pe()],on.prototype,"_newApiKey",void 0),t([pe({type:Boolean})],on.prototype,"_weatherSaving",void 0),t([ge()],on.prototype,"_coords",void 0),t([ge()],on.prototype,"_coordsEnabled",void 0),t([ge()],on.prototype,"_coordsLat",void 0),t([ge()],on.prototype,"_coordsLon",void 0),t([ge()],on.prototype,"_coordsElev",void 0),t([ge()],on.prototype,"_coordsSaving",void 0),t([ge()],on.prototype,"_saveStatus",void 0),on=t([ce("smart-irrigation-view-general")],on);const rn=e=>9*e/5+32;function ln(e,t,s){if(null==e||Number.isNaN(e))return null;switch(t){case"temperature":return s?{value:e,unit:"°C"}:{value:rn(e),unit:"°F"};case"precipitation":return s?{value:e,unit:at}:{value:(n=e,n/25.4),unit:nt};case"windspeed":return s?{value:e,unit:lt}:{value:(a=e,2.2369362920544*a),unit:rt};case"pressure":return s?{value:e,unit:"hPa"}:{value:(i=e,.0295299830714*i),unit:ot}}var i,a,n}function dn(e,t,s,i){const a=ln(e,t,s);if(!a)return"-";const n=function(e,t){return"pressure"===e?t?0:2:"precipitation"===e?t?1:2:1}(t,s);return`${a.value.toFixed(n)} ${a.unit}`}function cn(e,t){return null==e||Number.isNaN(e)?"-":t?`${e.toFixed(0)} L`:`${(e=>.264172052*e)(e).toFixed(1)} gal`}let hn=class extends le{constructor(){super(...arguments),this.metric=!0,this.name="",this.size="",this.throughput="",this.linkedEntity="",this.showEntity=!1}_emit(e,t){this.dispatchEvent(new CustomEvent(e,{detail:{value:t},bubbles:!0,composed:!0}))}render(){var e,t;const s=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en",i=this.metric?"m²":et,a=this.metric?tt:st;return W`
      <si-field label="${Oa("panels.zones.labels.name",s)}" required>
        <input
          type="text"
          class="si-input"
          .value="${this.name}"
          @input="${e=>this._emit("name-changed",e.target.value)}"
        />
      </si-field>

      <si-field
        label="${Oa("panels.zones.labels.size",s)}"
        unit="${i}"
        help="${Oa("field_help.zone_size",s)}"
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
        label="${Oa("panels.zones.labels.throughput",s)}"
        unit="${a}"
        help="${Oa("field_help.zone_throughput",s)}"
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
              label="${Oa("panels.zones.labels.linked_entity",s)}"
              help="${Oa("field_help.zone_linked_entity",s)}"
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
    `}};t([pe({attribute:!1})],hn.prototype,"hass",void 0),t([pe({type:Boolean})],hn.prototype,"metric",void 0),t([pe()],hn.prototype,"name",void 0),t([pe()],hn.prototype,"size",void 0),t([pe()],hn.prototype,"throughput",void 0),t([pe()],hn.prototype,"linkedEntity",void 0),t([pe({type:Boolean})],hn.prototype,"showEntity",void 0),hn=t([ce("si-zone-form")],hn);let un=class extends(Fa(le)){constructor(){super(...arguments),this.zones=[],this.modules=[],this.mappings=[],this.distributors=[],this.isLoading=!0,this._initialLoadDone=!1,this._scrolledTo=null,this._osStationFilter=e=>"station"===e.attributes.opensprinkler_type&&!e.attributes.is_master,this._expanded=new Set,this.isSaving=!1,this._showAddZone=!1,this._pendingConfirm=null,this._saveStatus="idle",this._savedResetTimer=null,this._confirmDeleteZoneId=null,this._newZoneName="",this._newZoneSize="",this._newZoneThroughput="",this._newZoneEntity="",this._updateScheduled=!1,this.globalDebounceTimer=null}_hasOpenSprinklerStations(){var e,t;const s=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.states)&&void 0!==t?t:{};return Object.keys(s).some(e=>e.startsWith("switch.")&&this._osStationFilter(s[e]))}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}get _targetZoneId(){var e,t;const s=null===(t=null===(e=this.path)||void 0===e?void 0:e.params)||void 0===t?void 0:t.zone;return null!=s&&""!==s?Number(s):null}_isExpanded(e){return void 0!==e.id&&this._expanded.has(e.id)}_toggleZone(e){const t=new Set(this._expanded);t.has(e)?t.delete(e):t.add(e),this._expanded=t}_flowSensorIsTotalizer(e){var t,s;const i=e.flow_sensor;if(!i)return!1;if(!this.hass)return!1;const a=this.hass.states[i];if(!a)return!1;const n=((null===(t=a.attributes)||void 0===t?void 0:t.unit_of_measurement)||"").trim();return"total_increasing"===(null===(s=a.attributes)||void 0===s?void 0:s.state_class)||!(!n||n.includes("/"))&&!["gpm","lpm","gph","lph"].includes(n.toLowerCase())}firstUpdated(){qs().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}updated(){var e;const t=this._targetZoneId;if(null===t||this.isLoading)return;if(this._scrolledTo===t)return;if(!this._expanded.has(t))return void(this._expanded=new Set(this._expanded).add(t));const s=null===(e=this.shadowRoot)||void 0===e?void 0:e.querySelector(`#zone-${t}`);s&&(this._scrolledTo=t,requestAnimationFrame(()=>s.scrollIntoView({behavior:"smooth",block:"start"})))}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:fe+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[t,s,i,a,n]=await Promise.all([Es(this.hass),Ts(this.hass),Ds(this.hass),Is(this.hass),Ps(this.hass)]);this.config=t,this.zones=s,this.modules=i,this.mappings=a,this.distributors=n,this._initialLoadDone=!0}catch(e){console.error("Error fetching data:",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}handleResetAllBuckets(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",fe+"/zones",{reset_all_buckets:!0})).catch(e=>{console.error("Failed to reset all buckets:",e),Ba(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after reset:",e))}))}handleClearAllWeatherdata(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",fe+"/zones",{clear_all_weatherdata:!0})).catch(e=>{console.error("Failed to clear all weather data:",e),Ba(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after clear-weather:",e))}))}handleAddZone(){var e;if(!this._newZoneName.trim())return;const t=null!==(e=this.modules.find(e=>"PyETO"===e.name))&&void 0!==e?e:this.modules[0],s=this.mappings[0],i={name:this._newZoneName.trim(),size:Math.round(100*(parseFloat(this._newZoneSize)||0))/100,throughput:Math.round(100*(parseFloat(this._newZoneThroughput)||0))/100,state:Za.Automatic,duration:0,bucket:0,module:null==t?void 0:t.id,delta:0,explanation:"",multiplier:1,mapping:null==s?void 0:s.id,lead_time:0,maximum_duration:void 0,maximum_bucket:void 0,drainage_rate:void 0,current_drainage:0,linked_entity:this._newZoneEntity||void 0};this.zones=[...this.zones,i],this.isSaving=!0,this._showAddZone=!1,this.saveToHA(i).then(()=>(this._newZoneName="",this._newZoneSize="",this._newZoneThroughput="",this._newZoneEntity="",this._fetchData())).catch(e=>{console.error("Failed to add zone:",e),this.zones=this.zones.slice(0,-1),Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()})}handleEditZone(e,t){this.hass&&(this.zones=this.zones.map((s,i)=>i===e?t:s),this.globalDebounceTimer&&clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=window.setTimeout(()=>{this.isSaving=!0,this._saveStatus="saving",this.saveToHA(t).then(()=>this._markSaved()).catch(e=>{console.error("Failed to save zone:",e),this._saveStatus="idle",Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}),this.globalDebounceTimer=null},500),this._scheduleUpdate())}handleRemoveZone(e){this._confirmDeleteZoneId=e}_confirmDelete(){const e=this._confirmDeleteZoneId;if(null===e||!this.hass)return;const t=this.zones.findIndex(t=>t.id===e);if(-1===t)return;const s=[...this.zones];var i,a;this.zones=this.zones.filter(t=>t.id!==e),this._confirmDeleteZoneId=null,this.isSaving=!0,(i=this.hass,a=e.toString(),i.callApi("POST",fe+"/zones",{id:a,remove:!0})).catch(e=>{console.error("Failed to delete zone:",e),Ba(this,this.hass,"common.errors.delete_failed",e),this.zones=s,this._fetchData().catch(e=>console.error("Failed to refresh data after delete error:",e))}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()})}_runPendingConfirm(){const e=this._pendingConfirm;this._pendingConfirm=null,null==e||e.onConfirm()}_markSaved(){this._saveStatus="saved",this._savedResetTimer&&clearTimeout(this._savedResetTimer),this._savedResetTimer=window.setTimeout(()=>{this._saveStatus="idle",this._scheduleUpdate()},2e3),this._scheduleUpdate()}_renderSaveStatus(){if(!this.hass||"idle"===this._saveStatus)return W``;const e="saving"===this._saveStatus;return W`
      <span class="save-status ${this._saveStatus}">
        <ha-icon
          icon="${e?"mdi:content-save-outline":"mdi:check-circle"}"
        ></ha-icon>
        ${Oa(e?"common.saving-messages.saving":"panels.zones.status.saved",this.hass.language)}
      </span>
    `}async saveToHA(e){if(!this.hass)throw new Error("Home Assistant connection not available");await Os(this.hass,e)}_renderModuleOptions(e){if(!this.hass)return W``;const t=null!=e?String(e):"";return W`
      <option value="" ?selected="${""===t}">
        ---${Oa("common.labels.select",this.hass.language)}---
      </option>
      ${this.modules.map(e=>W`
          <option value="${e.id}" ?selected="${t===String(e.id)}">
            ${e.id}: ${e.name}
          </option>
        `)}
    `}_renderMappingOptions(e){if(!this.hass)return W``;const t=null!=e?String(e):"";return W`
      <option value="" ?selected="${""===t}">
        ---${Oa("common.labels.select",this.hass.language)}---
      </option>
      ${this.mappings.map(e=>W`
          <option value="${e.id}" ?selected="${t===String(e.id)}">
            ${e.id}: ${e.name}
          </option>
        `)}
    `}_renderDistributorSelector(e,t){var s,i;if(!this.hass)return W``;if(!(null===(s=this.config)||void 0===s?void 0:s.distributors_enabled))return W``;const a=this.hass.language,n=null!=e.distributor_id;return W`
      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.zones.labels.distributor",a)}</span
        >
        <span slot="description"
          >${Oa("panels.zones.labels.distributor_help",a)}</span
        >
        <select
          class="settings-input"
          .value="${sn(n?String(e.distributor_id):"")}"
          @change="${s=>this._onZoneDistributorChange(t,e,s)}"
        >
          <option value="" ?selected="${!n}">
            ${Oa("panels.zones.labels.distributor_none",a)}
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
                >${Oa("panels.zones.labels.outlet_number",a)}</span
              >
              <span slot="description"
                >${Oa("panels.zones.labels.outlet_number_readonly_help",a)}</span
              >
              <div class="outlet-readonly">
                <span class="outlet-readonly-value"
                  >${null!==(i=e.outlet_number)&&void 0!==i?i:"—"}</span
                >
                <button
                  class="action-btn secondary"
                  @click="${()=>this._gotoDistributor(e.distributor_id)}"
                >
                  <ha-icon icon="mdi:open-in-new"></ha-icon>
                  ${Oa("panels.zones.labels.configure_on_distributor",a)}
                </button>
              </div>
            </ha-settings-row>
          `:""}
    `}_onZoneDistributorChange(e,t,s){var i;const a=s.target.value;if(!a)return void this.handleEditZone(e,Object.assign(Object.assign({},t),{[Ss]:null,[As]:null}));const n=parseInt(a);let o=null!==(i=t.outlet_number)&&void 0!==i?i:null;if(t.distributor_id!==n||null==o){const e=this.zones.filter(e=>e.distributor_id===n&&e.id!==t.id&&null!=e.outlet_number).map(e=>e.outlet_number),s=e.length?Math.max(...e):0;o=Math.min(s+1,6)}this.handleEditZone(e,Object.assign(Object.assign({},t),{[Ss]:n,[As]:o}))}_gotoDistributor(e){Na(0,Ga("setup","distributors",{params:{distributor:String(e)}}))}renderZone(e,t){var s,i,a,n,o,r,l,d,c,h,u,p,g,m,v,f,_;if(!this.hass)return W``;const b=this._isExpanded(e);return W`
      <ha-card id="zone-${null!==(s=e.id)&&void 0!==s?s:"new"}">
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
                    >${Oa("panels.zones.labels.name",this.hass.language)}</span
                  >
                  <input
                    type="text"
                    class="settings-input"
                    .value="${e.name}"
                    @input="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[ht]:s.target.value}))}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.size",this.hass.language)}
                    (${Ma(this.config,ut)})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat(e.size.toFixed(2))}"
                    @input="${s=>{const i=Math.round(100*s.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[ut]:i}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.throughput",this.hass.language)}
                    (${Ma(this.config,pt)})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat(e.throughput.toFixed(2))}"
                    @input="${s=>{const i=Math.round(100*s.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[pt]:i}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.soil_type",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Oa("field_help.zone_soil_type",this.hass.language)}</span
                  >
                  <select
                    class="settings-input"
                    .value="${sn(null!==(i=Object.keys(Bt).find(t=>Bt[t]===e.drainage_rate))&&void 0!==i?i:"custom")}"
                    @change="${s=>{const i=s.target.value;"custom"!==i&&void 0!==Bt[i]&&this.handleEditZone(t,Object.assign(Object.assign({},e),{[xt]:Bt[i]}))}}"
                  >
                    <option
                      value="custom"
                      ?selected="${!Object.values(Bt).includes(null!==(a=e.drainage_rate)&&void 0!==a?a:-1)}"
                    >
                      ${Oa("panels.zones.labels.soil_types.custom",this.hass.language)}
                    </option>
                    ${Object.keys(Bt).map(t=>W`
                        <option
                          value="${t}"
                          ?selected="${Bt[t]===e.drainage_rate}"
                        >
                          ${Oa(`panels.zones.labels.soil_types.${t}`,this.hass.language)}
                        </option>
                      `)}
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.drainage_rate",this.hass.language)}
                    (${Ma(this.config,xt)})</span
                  >
                  <span slot="description"
                    >${Oa("field_help.zone_drainage_rate",this.hass.language)}</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat((null!==(n=e.drainage_rate)&&void 0!==n?n:0).toFixed(2))}"
                    @input="${s=>{const i=Math.round(100*s.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[xt]:i}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.plant_type",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Oa("field_help.zone_plant_type",this.hass.language)}</span
                  >
                  <select
                    class="settings-input"
                    .value="${sn(null!==(o=e.plant_type)&&void 0!==o?o:"custom")}"
                    @change="${s=>{const i=s.target.value,a={[zt]:i};"custom"!==i&&void 0!==Pt[i]&&(a.kc=Pt[i]),this.handleEditZone(t,Object.assign(Object.assign({},e),a))}}"
                  >
                    <option
                      value="custom"
                      ?selected="${"custom"===(null!==(r=e.plant_type)&&void 0!==r?r:"custom")}"
                    >
                      ${Oa("panels.zones.labels.plant_types.custom",this.hass.language)}
                    </option>
                    ${Object.keys(Pt).map(t=>W`
                        <option
                          value="${t}"
                          ?selected="${e.plant_type===t}"
                        >
                          ${Oa(`panels.zones.labels.plant_types.${t}`,this.hass.language)}
                        </option>
                      `)}
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.kc",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Oa("field_help.zone_kc",this.hass.language)}</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.05"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat((null!==(l=e.kc)&&void 0!==l?l:1).toFixed(2))}"
                    @input="${s=>{const i=Math.round(100*s.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[kt]:i,[zt]:"custom"}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.state",this.hass.language)}</span
                  >
                  <select
                    class="settings-input"
                    .value="${sn(e.state)}"
                    @change="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[gt]:s.target.value,[mt]:0}))}"
                  >
                    <option
                      value="${Za.Automatic}"
                      ?selected="${e.state===Za.Automatic}"
                    >
                      ${Oa("panels.zones.labels.states.automatic",this.hass.language)}
                    </option>
                    <option
                      value="${Za.Manual}"
                      ?selected="${e.state===Za.Manual}"
                    >
                      ${Oa("panels.zones.labels.states.manual",this.hass.language)}
                    </option>
                    <option
                      value="${Za.Disabled}"
                      ?selected="${e.state===Za.Disabled}"
                    >
                      ${Oa("panels.zones.labels.states.disabled",this.hass.language)}
                    </option>
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("common.labels.module",this.hass.language)}</span
                  >
                  <select
                    class="settings-input"
                    .value="${sn(void 0!==e.module?String(e.module):"")}"
                    @change="${s=>{const i=s.target.value;this.handleEditZone(t,Object.assign(Object.assign({},e),{[vt]:i?parseInt(i):void 0}))}}"
                  >
                    ${this._renderModuleOptions(e.module)}
                  </select>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.mapping",this.hass.language)}</span
                  >
                  <select
                    class="settings-input"
                    .value="${sn(void 0!==e.mapping?String(e.mapping):"")}"
                    @change="${s=>{const i=s.target.value;this.handleEditZone(t,Object.assign(Object.assign({},e),{[bt]:i?parseInt(i):void 0}))}}"
                  >
                    ${this._renderMappingOptions(e.mapping)}
                  </select>
                </ha-settings-row>

                ${this._renderDistributorSelector(e,t)}
                ${null!=e.distributor_id?W`<div class="distributor-managed">
                      ${Oa("panels.zones.labels.distributor_managed_note",this.hass.language)}
                    </div>`:W`
                      <ha-settings-row>
                        <span slot="heading"
                          >${Oa("panels.zones.labels.watering_mode",this.hass.language)}</span
                        >
                        <span slot="description"
                          >${Oa("panels.zones.labels.watering_mode_description",this.hass.language)}</span
                        >
                        <select
                          class="settings-input"
                          .value="${sn(null!==(d=e.watering_mode)&&void 0!==d?d:"classic")}"
                          @change="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Tt]:s.target.value}))}"
                        >
                          <option
                            value="classic"
                            ?selected="${"classic"===(null!==(c=e.watering_mode)&&void 0!==c?c:"classic")}"
                          >
                            ${Oa("panels.zones.labels.watering_modes.classic",this.hass.language)}
                          </option>
                          <option
                            value="service"
                            ?selected="${"service"===e.watering_mode}"
                          >
                            ${Oa("panels.zones.labels.watering_modes.service",this.hass.language)}
                          </option>
                          <option
                            value="${zs}"
                            ?selected="${e.watering_mode===zs}"
                          >
                            ${Oa("panels.zones.labels.watering_modes.opensprinkler",this.hass.language)}
                          </option>
                        </select>
                      </ha-settings-row>

                      ${"service"===e.watering_mode?W`
                            <ha-settings-row>
                              <span slot="heading"
                                >${Oa("panels.zones.labels.run_service",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.run_service_help",this.hass.language)}</span
                              >
                              <ha-entity-picker
                                .hass="${this.hass}"
                                .value="${e.run_service||""}"
                                .includeDomains="${["script"]}"
                                allow-custom-entity
                                @value-changed="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Ot]:s.detail.value||null}))}"
                              ></ha-entity-picker>
                            </ha-settings-row>
                            <ha-settings-row>
                              <span slot="heading"
                                >${Oa("panels.zones.labels.duration_field",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.duration_field_help",this.hass.language)}</span
                              >
                              <input
                                type="text"
                                class="settings-input"
                                placeholder="${Oa("panels.zones.labels.duration_field_placeholder",this.hass.language)}"
                                .value="${e.duration_field||"duration"}"
                                @input="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Dt]:s.target.value||void 0}))}"
                              />
                            </ha-settings-row>
                            <ha-settings-row>
                              <span slot="heading"
                                >${Oa("panels.zones.labels.duration_unit",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.duration_unit_help",this.hass.language)}</span
                              >
                              <select
                                class="settings-input"
                                .value="${sn(null!==(h=e.duration_unit)&&void 0!==h?h:"seconds")}"
                                @change="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Ht]:s.target.value}))}"
                              >
                                <option
                                  value="seconds"
                                  ?selected="${"seconds"===(null!==(u=e.duration_unit)&&void 0!==u?u:"seconds")}"
                                >
                                  ${Oa("panels.zones.labels.duration_units.seconds",this.hass.language)}
                                </option>
                                <option
                                  value="minutes"
                                  ?selected="${"minutes"===e.duration_unit}"
                                >
                                  ${Oa("panels.zones.labels.duration_units.minutes",this.hass.language)}
                                </option>
                              </select>
                            </ha-settings-row>
                            <ha-settings-row>
                              <span slot="heading"
                                >${Oa("panels.zones.labels.stop_service",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.stop_service_help",this.hass.language)}</span
                              >
                              <ha-entity-picker
                                .hass="${this.hass}"
                                .value="${e.stop_service||""}"
                                .includeDomains="${["script"]}"
                                allow-custom-entity
                                @value-changed="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Mt]:s.detail.value||null}))}"
                              ></ha-entity-picker>
                            </ha-settings-row>
                            <ha-settings-row>
                              <span slot="heading"
                                >${Oa("panels.zones.labels.confirm_entity",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.confirm_entity_help",this.hass.language)}</span
                              >
                              <ha-entity-picker
                                .hass="${this.hass}"
                                .value="${e.confirm_entity||""}"
                                .includeDomains="${["valve","switch","input_boolean","number","binary_sensor"]}"
                                allow-custom-entity
                                @value-changed="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[It]:s.detail.value||null}))}"
                              ></ha-entity-picker>
                            </ha-settings-row>
                            ${(null===(p=this.config)||void 0===p?void 0:p.observed_watering_enabled)?W`
                                  <ha-settings-row>
                                    <span slot="heading"
                                      >${Oa("panels.zones.labels.observed_entity",this.hass.language)}</span
                                    >
                                    <span slot="description"
                                      >${Oa("panels.zones.labels.observed_entity_help",this.hass.language)}</span
                                    >
                                    <ha-entity-picker
                                      .hass="${this.hass}"
                                      .value="${e.observed_entity||""}"
                                      .includeDomains="${["valve","switch","input_boolean"]}"
                                      allow-custom-entity
                                      @value-changed="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Nt]:s.detail.value||null}))}"
                                    ></ha-entity-picker>
                                  </ha-settings-row>
                                `:""}
                          `:""}
                      ${e.watering_mode===zs?W`
                            <ha-settings-row>
                              <span slot="heading"
                                >${Oa("panels.zones.labels.opensprinkler_station",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.opensprinkler_station_help",this.hass.language)}</span
                              >
                              <ha-entity-picker
                                .hass="${this.hass}"
                                .value="${e.linked_entity||""}"
                                .includeDomains="${["switch"]}"
                                .entityFilter="${this._osStationFilter}"
                                allow-custom-entity
                                @value-changed="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[St]:s.detail.value||null}))}"
                              ></ha-entity-picker>
                            </ha-settings-row>
                            ${this._hasOpenSprinklerStations()?"":W`<div class="distributor-managed">
                                  ${Oa("panels.zones.labels.opensprinkler_no_stations",this.hass.language)}
                                </div>`}
                          `:"service"!==e.watering_mode?W`
                              <ha-settings-row>
                                <span slot="heading"
                                  >${Oa("panels.zones.labels.linked_entity",this.hass.language)}</span
                                >
                                <ha-entity-picker
                                  .hass="${this.hass}"
                                  .value="${e.linked_entity||""}"
                                  .includeDomains="${["switch","valve","input_boolean"]}"
                                  allow-custom-entity
                                  @value-changed="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[St]:s.detail.value||null}))}"
                                ></ha-entity-picker>
                              </ha-settings-row>
                            `:""}
                    `}

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.soil_moisture_sensor",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Oa("panels.zones.labels.soil_moisture_sensor_help",this.hass.language)}</span
                  >
                  <ha-entity-picker
                    .hass="${this.hass}"
                    .value="${e.soil_moisture_sensor||""}"
                    .includeDomains="${["sensor"]}"
                    .includeDeviceClasses="${["moisture"]}"
                    allow-custom-entity
                    @value-changed="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Lt]:s.detail.value||null}))}"
                  ></ha-entity-picker>
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.soil_moisture_threshold",this.hass.language)}</span
                  >
                  <span slot="description"
                    >${Oa("panels.zones.labels.soil_moisture_threshold_help",this.hass.language)}</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="1"
                    min="0"
                    max="100"
                    inputmode="decimal"
                    .value="${null!==(g=e.soil_moisture_threshold)&&void 0!==g?g:""}"
                    @input="${s=>{const i=s.target.value,a=""===i?null:Number(i);this.handleEditZone(t,Object.assign(Object.assign({},e),{[Rt]:null===a||isNaN(a)?null:a}))}}"
                  />
                </ha-settings-row>

                ${null==e.distributor_id?W`
                      <ha-settings-row>
                        <span slot="heading"
                          >${Oa("panels.zones.labels.flow_sensor",this.hass.language)}</span
                        >
                        <ha-entity-picker
                          .hass="${this.hass}"
                          .value="${e.flow_sensor||""}"
                          .includeDomains="${["sensor"]}"
                          allow-custom-entity
                          @value-changed="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Et]:s.detail.value||null}))}"
                        ></ha-entity-picker>
                      </ha-settings-row>

                      ${this._flowSensorIsTotalizer(e)?W`
                            <ha-settings-row>
                              <span slot="heading"
                                >${Oa("panels.zones.labels.flow_counter_type",this.hass.language)}</span
                              >
                              <span slot="description"
                                >${Oa("panels.zones.labels.flow_counter_type_help",this.hass.language)}</span
                              >
                              <select
                                class="settings-input"
                                .value="${sn(e.flow_counter_type||"auto")}"
                                @change="${s=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[Ct]:s.target.value||"auto"}))}"
                              >
                                ${["auto","per_run","lifetime"].map(t=>W`
                                    <option
                                      value="${t}"
                                      ?selected="${(e.flow_counter_type||"auto")===t}"
                                    >
                                      ${Oa(`panels.zones.labels.flow_counter_type_${t}`,this.hass.language)}
                                    </option>
                                  `)}
                              </select>
                            </ha-settings-row>
                          `:""}
                    `:""}

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.bucket",this.hass.language)}
                    (${Ma(this.config,ft)})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    inputmode="decimal"
                    .value="${parseFloat(Number(e.bucket).toFixed(2))}"
                    @input="${s=>{const i=Math.round(100*s.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[ft]:i}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.maximum-bucket",this.hass.language)}
                    (${Ma(this.config,ft)})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat(Number(e.maximum_bucket).toFixed(2))}"
                    @input="${s=>{const i=Math.round(100*s.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[$t]:i}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.multiplier",this.hass.language)}</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.1"
                    min="0"
                    inputmode="decimal"
                    .value="${parseFloat(e.multiplier.toFixed(2))}"
                    @input="${s=>{const i=Math.round(100*s.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[_t]:i}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.lead-time",this.hass.language)}
                    (${it})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="1"
                    min="0"
                    inputmode="numeric"
                    .value="${null!==(m=e.lead_time)&&void 0!==m?m:0}"
                    @input="${s=>{const i=s.target.valueAsNumber;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[yt]:Math.round(i)}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.maximum-duration",this.hass.language)}
                    (${it})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="1"
                    min="0"
                    inputmode="numeric"
                    .value="${null!==(v=e.maximum_duration)&&void 0!==v?v:""}"
                    @input="${s=>{const i=s.target.valueAsNumber;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[wt]:Math.round(i)}))}}"
                  />
                </ha-settings-row>

                <ha-settings-row>
                  <span slot="heading"
                    >${Oa("panels.zones.labels.bucket_threshold",this.hass.language)}
                    (${Ma(this.config,ft)})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.5"
                    max="0"
                    inputmode="decimal"
                    .value="${parseFloat((null!==(f=e.bucket_threshold)&&void 0!==f?f:0).toFixed(1))}"
                    @input="${s=>{const i=Math.round(10*s.target.valueAsNumber)/10;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[At]:Math.min(i,0)}))}}"
                  />
                </ha-settings-row>

                ${e.state===Za.Manual?W`
                      <ha-settings-row>
                        <span slot="heading"
                          >${Oa("panels.zones.labels.duration",this.hass.language)}
                          (${it})</span
                        >
                        <input
                          type="number"
                          class="settings-input shortfield"
                          step="1"
                          min="0"
                          inputmode="numeric"
                          .value="${null!==(_=e.duration)&&void 0!==_?_:0}"
                          @input="${s=>{const i=s.target.valueAsNumber;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[mt]:Math.round(i)}))}}"
                        />
                      </ha-settings-row>
                    `:""}

                <!-- Danger row -->
                <div class="settings-danger-row">
                  <button
                    class="action-btn"
                    @click="${()=>{this._pendingConfirm={title:Oa("panels.zones.confirm_action.reset_bucket_title",this.hass.language),body:Oa("panels.zones.confirm_action.reset_bucket_body",this.hass.language),confirmLabel:Oa("panels.zones.actions.reset-bucket",this.hass.language),onConfirm:()=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[ft]:0}))}}}"
                    ?disabled="${this.isSaving}"
                  >
                    ${Oa("panels.zones.actions.reset-bucket",this.hass.language)}
                  </button>
                  <button
                    class="action-btn danger-button"
                    @click="${()=>this.handleRemoveZone(void 0!==e.id?e.id:-1)}"
                    ?disabled="${this.isSaving||void 0===e.id}"
                  >
                    <ha-icon slot="icon" icon="mdi:delete"></ha-icon>
                    ${Oa("common.actions.delete",this.hass.language)}
                  </button>
                </div>
              </div>

              <!-- EXPLANATION EXPANSION -->
              ${e.explanation&&e.explanation.length>0?W`
                    <ha-expansion-panel
                      .header="${Oa("panels.zones.actions.information",this.hass.language)}"
                    >
                      <div class="card-content">
                        ${ei(e.explanation)}
                      </div>
                    </ha-expansion-panel>
                  `:""}

              <!-- Run history + cumulative water usage (WS-2) -->
              ${this._renderRunHistory(e)}

              <!-- Weather records + the watering/seasonal calendar now live on the
             Weather & Location tab (climate is the same for every zone). -->
            `:""}
      </ha-card>
    `}_renderRunHistory(e){var t,s,i;if(!this.hass)return W``;const a=(null===(t=this.config)||void 0===t?void 0:t.units)===Oe,n=null!==(s=e.run_log)&&void 0!==s?s:[],o=this.hass.language;return W`
      <ha-expansion-panel
        .header="${Oa("panels.zones.history.title",o)}"
      >
        <div class="card-content">
          <div class="history-usage">
            <span class="history-usage-label"
              >${Oa("panels.zones.history.total_used",o)}</span
            >
            <span class="history-usage-value"
              >${cn(null!==(i=e.water_used_total)&&void 0!==i?i:0,a)}</span
            >
          </div>
          ${0===n.length?W`<div class="weather-note">
                ${Oa("panels.zones.history.empty",o)}
              </div>`:W`
                <table class="history-table">
                  <thead>
                    <tr>
                      <th>${Oa("panels.zones.history.when",o)}</th>
                      <th>${Oa("panels.zones.history.result",o)}</th>
                      <th class="num">
                        ${Oa("panels.zones.history.volume",o)}
                      </th>
                      <th>${Oa("panels.zones.history.detail",o)}</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${n.map(e=>this._renderRunLogRow(e,a))}
                  </tbody>
                </table>
              `}
        </div>
      </ha-expansion-panel>
    `}_renderRunLogRow(e,t){const s=this.hass.language,i=Oa(`panels.zones.history.results.${e.result}`,s);let a="";return e.detail&&(a="skipped"===e.result?e.detail.split(",").map(e=>Oa(`panels.zones.outlook.checks.${e}`,s)||e).join(", "):Oa(`panels.zones.fault.${e.detail}`,s)||e.detail),W`
      <tr>
        <td>${Ja(e.ts)}</td>
        <td>
          <span class="history-chip history-${e.result}"
            >${i||e.result}</span
          >
        </td>
        <td class="num">
          ${e.volume_l>0?cn(e.volume_l,t):"-"}
        </td>
        <td class="history-detail">${ei(a)}</td>
      </tr>
    `}render(){var e;if(!this.hass)return W``;if(this.isLoading)return W`
        <ha-card header="${Oa("panels.zones.title",this.hass.language)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Oa("common.loading-messages.general",this.hass.language)}
            </div>
          </div>
        </ha-card>
      `;const t=null!==this._confirmDeleteZoneId?this.zones.find(e=>e.id===this._confirmDeleteZoneId):null;return W`
      <!-- Header: title + save chip + add zone -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${Oa("panels.zones.title",this.hass.language)}
          </div>
          ${this._renderSaveStatus()}
          <ha-icon-button
            .path="${ja}"
            title="${Oa("panels.zones.cards.add-zone.header",this.hass.language)}"
            @click="${()=>{this._showAddZone=!0}}"
          ></ha-icon-button>
        </div>
        ${0===this.zones.length?W`<div class="card-content">
              <div class="weather-note">
                ${Oa("panels.zones.no_items",this.hass.language)}
              </div>
            </div>`:""}
      </ha-card>

      <!-- Add Zone dialog -->
      <ha-dialog
        .open="${this._showAddZone}"
        @closed="${()=>{this._showAddZone=!1}}"
        heading="${Oa("panels.zones.cards.add-zone.header",this.hass.language)}"
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
            ${Oa("common.actions.cancel",this.hass.language)}
          </button>
          <button
            class="dialog-btn dialog-btn-primary"
            @click="${this.handleAddZone}"
            ?disabled="${!this._newZoneName.trim()||this.isSaving}"
          >
            ${this.isSaving?Oa("common.saving-messages.adding",this.hass.language):Oa("panels.zones.cards.add-zone.actions.add",this.hass.language)}
          </button>
        </div>
      </ha-dialog>

      <!-- Delete confirmation dialog -->
      ${t?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmDeleteZoneId=null}}"
              heading="${Oa("common.actions.confirm_delete",this.hass.language)}"
            >
              <p>
                ${Oa("common.actions.confirm_delete_zone",this.hass.language)}
              </p>
              <p><strong>${t.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmDeleteZoneId=null}}"
                >
                  ${Oa("common.actions.cancel",this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-danger"
                  @click="${this._confirmDelete}"
                >
                  ${Oa("common.actions.delete",this.hass.language)}
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
                  ${Oa("common.actions.cancel",this.hass.language)}
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
            ${Oa("common.labels.bulk_actions",this.hass.language)}
          </div>
        </div>
        <div class="card-content bulk-actions">
          <button
            class="action-btn danger-button"
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
    `}};t([pe()],un.prototype,"config",void 0),t([pe({attribute:!1})],un.prototype,"path",void 0),t([pe({type:Array})],un.prototype,"zones",void 0),t([pe({type:Array})],un.prototype,"modules",void 0),t([pe({type:Array})],un.prototype,"mappings",void 0),t([pe({type:Array})],un.prototype,"distributors",void 0),t([pe({type:Boolean})],un.prototype,"isLoading",void 0),t([ge()],un.prototype,"_expanded",void 0),t([pe({type:Boolean})],un.prototype,"isSaving",void 0),t([pe({type:Boolean})],un.prototype,"_showAddZone",void 0),t([ge()],un.prototype,"_pendingConfirm",void 0),t([ge()],un.prototype,"_saveStatus",void 0),t([pe()],un.prototype,"_confirmDeleteZoneId",void 0),t([pe()],un.prototype,"_newZoneName",void 0),t([pe()],un.prototype,"_newZoneSize",void 0),t([pe()],un.prototype,"_newZoneThroughput",void 0),t([pe()],un.prototype,"_newZoneEntity",void 0),un=t([ce("smart-irrigation-view-zone-settings")],un);let pn=class extends le{_emit(e){this.dispatchEvent(new CustomEvent("distributor-changed",{detail:{value:Object.assign(Object.assign({},this.distributor),e)},bubbles:!0,composed:!0}))}_onNumber(e,t){const s=t.target.valueAsNumber;isNaN(s)||this._emit({[e]:Math.max(0,Math.round(s))})}render(){var e,t,s,i;if(!this.hass||!this.distributor)return W``;const a=this.hass.language,n=this.distributor,o=n.watering_mode===ks;return W`
      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.distributors.labels.name",a)}</span
        >
        <input
          type="text"
          class="settings-input"
          .value="${null!==(e=n.name)&&void 0!==e?e:""}"
          @input="${e=>this._emit({[cs]:e.target.value})}"
        />
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.zones.labels.watering_mode",a)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.watering_mode_help",a)}</span
        >
        <select
          class="settings-input"
          .value="${sn(null!==(t=n.watering_mode)&&void 0!==t?t:xs)}"
          @change="${e=>this._emit({[hs]:e.target.value})}"
        >
          <option
            value="${xs}"
            ?selected="${(null!==(s=n.watering_mode)&&void 0!==s?s:xs)===xs}"
          >
            ${Oa("panels.zones.labels.watering_modes.classic",a)}
          </option>
          <option
            value="${ks}"
            ?selected="${n.watering_mode===ks}"
          >
            ${Oa("panels.zones.labels.watering_modes.service",a)}
          </option>
        </select>
      </ha-settings-row>

      ${o?this._renderServiceRows(a):""}
      ${this._renderInletWatchRows(a)} ${this._renderSensorRows(a)}
      ${this._renderTimingRows(a)}

      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.distributors.labels.notify_target",a)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.notify_target_help",a)}</span
        >
        <input
          type="text"
          class="settings-input"
          placeholder="${Oa("panels.distributors.labels.notify_target_placeholder",a)}"
          .value="${null!==(i=n.notify_target)&&void 0!==i?i:""}"
          @input="${e=>this._emit({[ys]:e.target.value||null})}"
        />
      </ha-settings-row>
    `}_renderInletWatchRows(e){var t;const s=this.distributor,i=s.watering_mode===ks?"panels.distributors.labels.inlet_entity_help_service":"panels.distributors.labels.inlet_entity_help",a=null!==(t=s.watch_mode)&&void 0!==t?t:"ignore";return W`
      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.distributors.labels.inlet_entity",e)}</span
        >
        <span slot="description">${Oa(i,e)}</span>
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${s.inlet_entity||""}"
          .includeDomains="${["switch","valve","input_boolean"]}"
          allow-custom-entity
          @value-changed="${e=>this._emit({[us]:e.detail.value||null})}"
        ></ha-entity-picker>
      </ha-settings-row>

      <!-- No inlet_entity => nothing to watch => the watch_mode row is hidden. -->
      ${s.inlet_entity?W`
            <ha-settings-row>
              <span slot="heading"
                >${Oa("panels.distributors.labels.watch_mode",e)}</span
              >
              <span slot="description"
                >${Oa("panels.distributors.labels.watch_mode_help",e)}</span
              >
              <select
                class="settings-input"
                .value="${sn(a)}"
                @change="${e=>this._emit({[ps]:e.target.value})}"
              >
                ${$s.map(t=>W`
                    <option value="${t}" ?selected="${a===t}">
                      ${Oa(`panels.distributors.labels.watch_mode_${t}`,e)}
                    </option>
                  `)}
              </select>
            </ha-settings-row>
          `:""}
    `}_renderServiceRows(e){var t,s;const i=this.distributor;return W`
      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.distributors.labels.run_service",e)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.run_service_help",e)}</span
        >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${i.run_service||""}"
          .includeDomains="${["script"]}"
          allow-custom-entity
          @value-changed="${e=>this._emit({[gs]:e.detail.value||null})}"
        ></ha-entity-picker>
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.distributors.labels.duration_field",e)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.duration_field_help",e)}</span
        >
        <input
          type="text"
          class="settings-input"
          placeholder="${Oa("panels.distributors.labels.duration_field_placeholder",e)}"
          .value="${i.duration_field||"duration"}"
          @input="${e=>this._emit({[vs]:e.target.value||"duration"})}"
        />
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.distributors.labels.duration_unit",e)}</span
        >
        <select
          class="settings-input"
          .value="${sn(null!==(t=i.duration_unit)&&void 0!==t?t:"seconds")}"
          @change="${e=>this._emit({[fs]:e.target.value})}"
        >
          <option
            value="seconds"
            ?selected="${"seconds"===(null!==(s=i.duration_unit)&&void 0!==s?s:"seconds")}"
          >
            ${Oa("panels.distributors.labels.duration_units.seconds",e)}
          </option>
          <option value="minutes" ?selected="${"minutes"===i.duration_unit}">
            ${Oa("panels.distributors.labels.duration_units.minutes",e)}
          </option>
        </select>
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.distributors.labels.stop_service",e)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.stop_service_help",e)}</span
        >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${i.stop_service||""}"
          .includeDomains="${["script"]}"
          allow-custom-entity
          @value-changed="${e=>this._emit({[ms]:e.detail.value||null})}"
        ></ha-entity-picker>
      </ha-settings-row>
    `}_renderSensorRows(e){const t=this.distributor;return W`
      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.distributors.labels.confirm_entity",e)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.confirm_entity_help",e)}</span
        >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${t.confirm_entity||""}"
          .includeDomains="${["binary_sensor","sensor","switch","valve","input_boolean"]}"
          allow-custom-entity
          @value-changed="${e=>this._emit({[_s]:e.detail.value||null})}"
        ></ha-entity-picker>
      </ha-settings-row>

      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.distributors.labels.flow_sensor",e)}</span
        >
        <span slot="description"
          >${Oa("panels.distributors.labels.flow_sensor_help",e)}</span
        >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${t.flow_sensor||""}"
          .includeDomains="${["sensor"]}"
          allow-custom-entity
          @value-changed="${e=>this._emit({[bs]:e.detail.value||null})}"
        ></ha-entity-picker>
      </ha-settings-row>
    `}_renderTimingRows(e){var t,s,i,a;const n=this.distributor,o=(null!==(t=n.pause_seconds)&&void 0!==t?t:0)<10,r=(null!==(s=n.skip_pulse_seconds)&&void 0!==s?s:0)<10;return W`
      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.distributors.labels.pause_seconds",e)}
          (${it})</span
        >
        <span slot="description"
          >${Oa("field_help.distributor_pause_seconds",e)}</span
        >
        <input
          type="number"
          class="settings-input shortfield"
          step="1"
          min="${10}"
          inputmode="numeric"
          .value="${null!==(i=n.pause_seconds)&&void 0!==i?i:""}"
          @input="${e=>this._onNumber("pause_seconds",e)}"
        />
      </ha-settings-row>
      ${o?W`<div class="timing-warning">
            ${Oa("panels.distributors.hints.below_floor_pause",e)}
          </div>`:""}

      <ha-settings-row>
        <span slot="heading"
          >${Oa("panels.distributors.labels.skip_pulse_seconds",e)}
          (${it})</span
        >
        <span slot="description"
          >${Oa("field_help.distributor_skip_pulse_seconds",e)}</span
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
            ${Oa("panels.distributors.hints.below_floor_skip",e)}
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
    `}};t([pe({attribute:!1})],pn.prototype,"hass",void 0),t([pe({attribute:!1})],pn.prototype,"distributor",void 0),pn=t([ce("si-distributor-form")],pn);let gn=class extends(Fa(le)){constructor(){super(...arguments),this.distributors=[],this.zones=[],this.isLoading=!0,this.isSaving=!1,this._initialLoadDone=!1,this._scrolledToDist=null,this._expanded=new Set,this._showAdd=!1,this._newName="",this._confirmDeleteId=null,this._armConfirmId=null,this._confirmResyncHomeId=null,this._confirmSetOutletId=null,this._outletDraft={},this._outletRows={},this._saveStatus="idle",this._savedResetTimer=null,this.globalDebounceTimer=null,this._updateScheduled=!1}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}_isExpanded(e){return void 0!==e.id&&this._expanded.has(e.id)}_toggle(e){const t=new Set(this._expanded);t.has(e)?t.delete(e):t.add(e),this._expanded=t}firstUpdated(){qs().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate()})}updated(){var e,t,s;const i=null===(t=null===(e=this.path)||void 0===e?void 0:e.params)||void 0===t?void 0:t.distributor;if(null==i||""===i||this.isLoading)return;const a=Number(i);if(Number.isNaN(a)||this._scrolledToDist===a)return;if(!this._expanded.has(a))return void(this._expanded=new Set(this._expanded).add(a));const n=null===(s=this.shadowRoot)||void 0===s?void 0:s.querySelector(`#distributor-${a}`);n&&(this._scrolledToDist=a,requestAnimationFrame(()=>n.scrollIntoView({behavior:"smooth",block:"start"})))}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial distributor data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to refetch on config update:",e)})},{type:fe+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[t,s,i]=await Promise.all([Es(this.hass),Ps(this.hass),Ts(this.hass)]);this.config=t,this.distributors=s,this.zones=i,this._initialLoadDone=!0}catch(e){console.error("Error fetching distributor data:",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}handleAdd(){this.hass&&this._newName.trim()&&(this.isSaving=!0,this._showAdd=!1,Bs(this.hass,{name:this._newName.trim()}).then(()=>(this._newName="",this._fetchData())).catch(e=>{console.error("Failed to add distributor:",e),Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}))}_configPayload(e){var t,s,i,a,n,o,r;return{id:e.id,name:e.name,watering_mode:e.watering_mode,inlet_entity:null!==(t=e.inlet_entity)&&void 0!==t?t:null,watch_mode:null!==(s=e.watch_mode)&&void 0!==s?s:"ignore",run_service:null!==(i=e.run_service)&&void 0!==i?i:null,stop_service:null!==(a=e.stop_service)&&void 0!==a?a:null,duration_field:e.duration_field,duration_unit:e.duration_unit,confirm_entity:null!==(n=e.confirm_entity)&&void 0!==n?n:null,flow_sensor:null!==(o=e.flow_sensor)&&void 0!==o?o:null,pause_seconds:e.pause_seconds,skip_pulse_seconds:e.skip_pulse_seconds,notify_target:null!==(r=e.notify_target)&&void 0!==r?r:null,use_master:e.use_master}}handleEditDistributor(e,t){this.hass&&(this.distributors=this.distributors.map((s,i)=>i===e?t:s),this.globalDebounceTimer&&clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=window.setTimeout(()=>{this.isSaving=!0,this._saveStatus="saving",Bs(this.hass,this._configPayload(t)).then(()=>this._markSaved()).catch(e=>{console.error("Failed to save distributor:",e),this._saveStatus="idle",Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}),this.globalDebounceTimer=null},500),this._scheduleUpdate())}_confirmDelete(){const e=this._confirmDeleteId;if(null===e||!this.hass)return;const t=[...this.distributors];var s,i;this.distributors=this.distributors.filter(t=>t.id!==e),this._confirmDeleteId=null,this.isSaving=!0,(s=this.hass,i=e,s.callApi("POST",fe+"/distributors",{id:i,remove:!0})).catch(e=>{console.error("Failed to delete distributor:",e),Ba(this,this.hass,"common.errors.delete_failed",e),this.distributors=t}).finally(()=>{this.isSaving=!1,this._fetchData().catch(()=>{})})}_callAction(e){this.hass&&(this.isSaving=!0,this._scheduleUpdate(),e.catch(e=>{console.error("Distributor action failed:",e),Ba(this,this.hass,"common.errors.action_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(()=>{})}))}_testRun(e){var t,s;this._callAction((t=this.hass,s=e,t.callService(fe,"distributor_test_run",{distributor_id:s})))}_setOutlet(e,t){var s;const i=null!==(s=this._outletDraft[e])&&void 0!==s?s:t;this._callAction(((e,t,s)=>e.callService(fe,"distributor_set_outlet",{distributor_id:t,outlet:s}))(this.hass,e,i))}_confirmSetOutlet(){const e=this._confirmSetOutletId;if(this._confirmSetOutletId=null,null===e)return;const t=this.distributors.find(t=>t.id===e);t&&this._setOutlet(e,t.current_outlet)}_resyncHome(e){var t,s;this._callAction((t=this.hass,s=e,t.callService(fe,"distributor_resync_home",{distributor_id:s})))}_confirmResyncHome(){const e=this._confirmResyncHomeId;this._confirmResyncHomeId=null,null!==e&&this._resyncHome(e)}_runNow(e){var t,s;this._callAction((t=this.hass,s=e,t.callService(fe,"distributor_run_now",{distributor_id:s})))}_setArmed(e,t){this.hass&&(this._armConfirmId=null,this.distributors=this.distributors.map(s=>s.id===e?Object.assign(Object.assign({},s),{commissioning_confirmed:t}):s),this.isSaving=!0,Bs(this.hass,{id:e,[ws]:t}).catch(e=>{console.error("Failed to set commissioning state:",e),Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(()=>{})}))}_onArmToggle(e,t){void 0!==e.id&&(t?this._armConfirmId=e.id:this._setArmed(e.id,!1))}_markSaved(){this._saveStatus="saved",this._savedResetTimer&&clearTimeout(this._savedResetTimer),this._savedResetTimer=window.setTimeout(()=>{this._saveStatus="idle",this._scheduleUpdate()},2e3),this._scheduleUpdate()}_renderSaveStatus(){if(!this.hass||"idle"===this._saveStatus)return W``;const e="saving"===this._saveStatus;return W`
      <span class="save-status ${this._saveStatus}">
        <ha-icon
          icon="${e?"mdi:content-save-outline":"mdi:check-circle"}"
        ></ha-icon>
        ${Oa(e?"common.saving-messages.saving":"panels.distributors.status.saved",this.hass.language)}
      </span>
    `}_hasOwnActuation(e){return!!(e.linked_entity||e.run_service||e.stop_service)}_membersByOutlet(e){const t=new Map;if(void 0===e)return t;for(const s of this.zones)s.distributor_id===e&&null!=s.outlet_number&&void 0!==s.id&&t.set(s.outlet_number,s);return t}_outletCount(e){const t=this._membersByOutlet(e.id),s=t.size?Math.max(...t.keys()):0,i=Math.max(2,s),a=void 0!==e.id?this._outletRows[e.id]:void 0;return Math.min(6,Math.max(i,null!=a?a:i))}_assignZone(e,t,s){return Os(this.hass,{id:e.id,[Ss]:t,[As]:s})}_optimisticZone(e,t,s){void 0!==e&&(this.zones=this.zones.map(i=>i.id===e?Object.assign(Object.assign({},i),{distributor_id:t,outlet_number:s}):i))}_runAssign(e){e.length&&(this.isSaving=!0,this._saveStatus="saving",this._scheduleUpdate(),Promise.all(e).then(()=>this._markSaved()).catch(e=>{console.error("Failed to assign zone to outlet:",e),this._saveStatus="idle",Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._fetchData().catch(()=>{})}))}_setOutletCount(e,t){if(void 0===e.id)return;const s=this._membersByOutlet(e.id),i=[];for(const[e,a]of s)e>t&&i.push(a);this._outletRows=Object.assign(Object.assign({},this._outletRows),{[e.id]:t}),i.length?(i.forEach(e=>this._optimisticZone(e.id,null,null)),this._runAssign(i.map(e=>this._assignZone(e,null,null)))):this._scheduleUpdate()}_onOutletZoneChange(e,t,s){const i=s.target.value,a=i?parseInt(i):null,n=this._membersByOutlet(e.id).get(t),o=null!==a?this.zones.find(e=>e.id===a):null,r=[];n&&n.id!==a&&(r.push(this._assignZone(n,null,null)),this._optimisticZone(n.id,null,null)),o&&(r.push(this._assignZone(o,e.id,t)),this._optimisticZone(o.id,e.id,t)),this._runAssign(r)}_renderOutletConfig(e){if(!this.hass)return W``;const t=this.hass.language,s=this._membersByOutlet(e.id),i=this._outletCount(e),a=this.zones.filter(e=>void 0!==e.id&&null==e.distributor_id&&!this._hasOwnActuation(e)),n=[...s.keys()].sort((e,t)=>e-t),o=n.some((e,t)=>e!==t+1),r=[];for(let n=1;n<=i;n++){const i=s.get(n),o=i?[...a,i]:[...a];o.sort((e,t)=>(e.name||"").localeCompare(t.name||"")),r.push(W`
        <div class="outlet-row">
          <span class="outlet-label"
            >${Oa("panels.distributors.commissioning.outlet",t)}
            ${n}</span
          >
          <select
            class="settings-input"
            .value="${sn(null!=(null==i?void 0:i.id)?String(i.id):"")}"
            @change="${t=>this._onOutletZoneChange(e,n,t)}"
            ?disabled="${this.isSaving}"
          >
            <option value="" ?selected="${!i}">
              ${Oa("panels.distributors.outlets.none",t)}
            </option>
            ${o.map(e=>W`
                <option value="${e.id}" ?selected="${(null==i?void 0:i.id)===e.id}">
                  ${e.name}
                </option>
              `)}
          </select>
        </div>
      `)}return W`
      <div class="outlet-config">
        <div class="commissioning-head">
          <span class="section-title"
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
                >
                <select
                  class="settings-input shortfield"
                  .value="${sn(String(i))}"
                  @change="${t=>this._setOutletCount(e,parseInt(t.target.value))}"
                  ?disabled="${this.isSaving}"
                >
                  ${Array.from({length:5},(e,t)=>2+t).map(e=>W`<option value="${e}" ?selected="${e===i}">
                        ${e}
                      </option>`)}
                </select>
              </ha-settings-row>
              <div class="outlet-rows">${r}</div>
              ${o?W`<div class="timing-warning">
                    ${Oa("panels.distributors.outlets.gap_warning",t)}
                  </div>`:""}
              <div class="commissioning-note">
                ${Oa("panels.distributors.hints.outlet_change",t)}
              </div>
            `}
      </div>
    `}_renderAdvisories(){var e,t;if(!this.hass)return W``;const s=this.hass.language,i=null===(e=this.config)||void 0===e?void 0:e.zone_sequencing,a=i===Ft,n=i===jt||i===Wt,o=!!(null===(t=this.config)||void 0===t?void 0:t.master_off_after);return W`
      <div class="advisories">
        <div class="advisory">
          <ha-icon icon="mdi:flask-outline"></ha-icon>
          <span
            >${Oa("panels.distributors.hints.experimental",s)}</span
          >
        </div>
        <div class="advisory">
          <ha-icon icon="mdi:water-alert-outline"></ha-icon>
          <span>${Oa("panels.distributors.hints.pressure",s)}</span>
        </div>
        ${a?W`<div class="advisory">
              <ha-icon icon="mdi:information-outline"></ha-icon>
              <span
                >${Oa("panels.distributors.hints.parallel_draw",s)}</span
              >
            </div>`:""}
        ${n&&o?W`<div class="advisory">
              <ha-icon icon="mdi:information-outline"></ha-icon>
              <span
                >${Oa("panels.distributors.hints.master_off_after",s)}</span
              >
            </div>`:""}
      </div>
    `}_renderCommissioning(e){var t;if(!this.hass)return W``;const s=this.hass.language,i="synced"===e.position_state,a=!!e.commissioning_confirmed,n=!!e.active_cycle&&Object.keys(e.active_cycle).length>0,o=e.id;return W`
      <div class="commissioning">
        <div class="commissioning-head">
          <span class="section-title"
            >${Oa("panels.distributors.commissioning.title",s)}</span
          >
          <span class="pos-badge pos-${e.position_state}">
            ${Oa("panels.distributors.commissioning.outlet",s)}
            ${e.current_outlet} ·
            ${Oa(`panels.distributors.commissioning.states.${e.position_state}`,s)}
          </span>
        </div>

        <!-- Re-sync controls -->
        <ha-settings-row>
          <span slot="heading"
            >${Oa("panels.distributors.commissioning.set_outlet",s)}</span
          >
          <span slot="description"
            >${Oa("panels.distributors.commissioning.set_outlet_help",s)}</span
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
              ${Oa("panels.distributors.commissioning.set_outlet",s)}
            </button>
            <button
              class="action-btn secondary"
              ?disabled="${this.isSaving}"
              @click="${()=>{this._confirmResyncHomeId=o}}"
            >
              ${Oa("panels.distributors.commissioning.resync_home",s)}
            </button>
          </div>
        </ha-settings-row>
        <div class="commissioning-note">
          ${Oa("panels.distributors.hints.undetectable",s)}
        </div>

        <!-- Test run -->
        <ha-settings-row>
          <span slot="heading"
            >${Oa("panels.distributors.commissioning.test_run",s)}</span
          >
          <span slot="description"
            >${Oa("panels.distributors.commissioning.test_run_help",s)}</span
          >
          <button
            class="action-btn secondary"
            ?disabled="${this.isSaving||!i}"
            @click="${()=>this._testRun(o)}"
          >
            <ha-icon icon="mdi:play-circle-outline"></ha-icon>
            ${Oa("panels.distributors.commissioning.test_run",s)}
          </button>
        </ha-settings-row>

        <!-- Arm switch -->
        <ha-settings-row>
          <span slot="heading"
            >${Oa("panels.distributors.commissioning.confirmed",s)}</span
          >
          <span slot="description"
            >${Oa(i?"panels.distributors.commissioning.confirmed_help":"panels.distributors.commissioning.needs_sync",s)}</span
          >
          <ha-switch
            .checked="${sn(a)}"
            .disabled="${this.isSaving||!i&&!a}"
            @change="${t=>this._onArmToggle(e,t.target.checked)}"
          ></ha-switch>
        </ha-settings-row>

        <!-- Run now -->
        <div class="run-now-row">
          <button
            class="action-btn"
            ?disabled="${this.isSaving||!i||!a||n}"
            @click="${()=>this._runNow(o)}"
          >
            <ha-icon icon="mdi:play"></ha-icon>
            ${Oa("panels.distributors.commissioning.run_now",s)}
          </button>
          <span class="run-now-hint">
            ${Oa(n?"panels.distributors.commissioning.run_now_active":"panels.distributors.commissioning.run_now_help",s)}
          </span>
        </div>
      </div>
    `}renderDistributor(e,t){var s;if(!this.hass)return W``;const i=this._isExpanded(e),a=this.hass.language;return W`
      <ha-card id="distributor-${null!==(s=e.id)&&void 0!==s?s:"new"}">
        <div
          class="card-header dist-toggle"
          role="button"
          tabindex="0"
          aria-expanded="${i?"true":"false"}"
          @click="${()=>void 0!==e.id&&this._toggle(e.id)}"
          @keydown="${t=>{"Enter"!==t.key&&" "!==t.key||void 0===e.id||(t.preventDefault(),this._toggle(e.id))}}"
        >
          <div class="name">${e.name}</div>
          <span class="pos-badge pos-${e.position_state}">
            ${Oa(`panels.distributors.commissioning.states.${e.position_state}`,a)}
          </span>
          <ha-icon
            class="dist-chevron"
            icon="${i?"mdi:chevron-up":"mdi:chevron-down"}"
          ></ha-icon>
        </div>
        ${i?W`
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
                    ${Oa("common.actions.delete",a)}
                  </button>
                </div>
              </div>
            `:""}
      </ha-card>
    `}render(){var e;if(!this.hass)return W``;const t=this.hass.language;if(this.isLoading)return W`
        <ha-card header="${Oa("panels.distributors.title",t)}">
          <div class="card-content">
            <div class="loading-indicator">
              ${Oa("common.loading-messages.general",t)}
            </div>
          </div>
        </ha-card>
      `;const s=null!==this._confirmDeleteId?this.distributors.find(e=>e.id===this._confirmDeleteId):null,i=null!==this._armConfirmId?this.distributors.find(e=>e.id===this._armConfirmId):null,a=null!==this._confirmResyncHomeId?this.distributors.find(e=>e.id===this._confirmResyncHomeId):null,n=null!==this._confirmSetOutletId?this.distributors.find(e=>e.id===this._confirmSetOutletId):null,o=n&&void 0!==n.id?null!==(e=this._outletDraft[n.id])&&void 0!==e?e:n.current_outlet:null;return W`
      <ha-card>
        <div class="card-header">
          <div class="name">${Oa("panels.distributors.title",t)}</div>
          ${this._renderSaveStatus()}
          <ha-icon-button
            .path="${ja}"
            title="${Oa("panels.distributors.add.header",t)}"
            @click="${()=>{this._showAdd=!0}}"
          ></ha-icon-button>
        </div>
        <div class="card-content">
          <div class="item-description">
            ${Oa("panels.distributors.description",t)}
          </div>
          ${this._renderAdvisories()}
          ${0===this.distributors.length?W`<div class="weather-note">
                ${Oa("panels.distributors.no_items",t)}
              </div>`:""}
        </div>
      </ha-card>

      <!-- Add dialog -->
      <ha-dialog
        .open="${this._showAdd}"
        @closed="${()=>{this._showAdd=!1}}"
        heading="${Oa("panels.distributors.add.header",t)}"
      >
        <div class="add-form">
          <si-field
            label="${Oa("panels.distributors.labels.name",t)}"
            required
          >
            <input
              type="text"
              class="settings-input"
              placeholder="${Oa("panels.distributors.add.name_placeholder",t)}"
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
            ${Oa("common.actions.cancel",t)}
          </button>
          <button
            class="dialog-btn dialog-btn-primary"
            ?disabled="${!this._newName.trim()||this.isSaving}"
            @click="${this.handleAdd}"
          >
            ${this.isSaving?Oa("common.saving-messages.adding",t):Oa("panels.distributors.add.actions.add",t)}
          </button>
        </div>
      </ha-dialog>

      <!-- Delete confirm -->
      ${s?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmDeleteId=null}}"
              heading="${Oa("common.actions.confirm_delete",t)}"
            >
              <p>${Oa("panels.distributors.confirm_delete",t)}</p>
              <p><strong>${s.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmDeleteId=null}}"
                >
                  ${Oa("common.actions.cancel",t)}
                </button>
                <button
                  class="dialog-btn dialog-btn-danger"
                  @click="${this._confirmDelete}"
                >
                  ${Oa("common.actions.delete",t)}
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Arm confirm -->
      ${i?W`
            <ha-dialog
              open
              @closed="${()=>{this._armConfirmId=null}}"
              heading="${Oa("panels.distributors.commissioning.confirm_dialog.title",t)}"
            >
              <p>
                ${Oa("panels.distributors.commissioning.confirm_dialog.body",t)}
              </p>
              <p><strong>${i.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._armConfirmId=null}}"
                >
                  ${Oa("common.actions.cancel",t)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${()=>void 0!==i.id&&this._setArmed(i.id,!0)}"
                >
                  ${Oa("panels.distributors.commissioning.confirm_dialog.confirm",t)}
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Reset-to-outlet-1 confirm (safety: a stray click would falsely mark synced) -->
      ${a?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmResyncHomeId=null}}"
              heading="${Oa("panels.distributors.commissioning.confirm_resync.title",t)}"
            >
              <p>
                ${Oa("panels.distributors.commissioning.confirm_resync.body",t)}
              </p>
              <p><strong>${a.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmResyncHomeId=null}}"
                >
                  ${Oa("common.actions.cancel",t)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._confirmResyncHome}"
                >
                  ${Oa("panels.distributors.commissioning.resync_home",t)}
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Set-current-outlet confirm (safety: a stray click would falsely mark synced at the entered outlet) -->
      ${n?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmSetOutletId=null}}"
              heading="${Oa("panels.distributors.commissioning.confirm_set_outlet.title",t)}"
            >
              <p>
                ${Oa("panels.distributors.commissioning.confirm_set_outlet.body",t)}
              </p>
              <p>
                <strong
                  >${n.name} ·
                  ${Oa("panels.distributors.commissioning.outlet",t)}
                  ${o}</strong
                >
              </p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmSetOutletId=null}}"
                >
                  ${Oa("common.actions.cancel",t)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._confirmSetOutlet}"
                >
                  ${Oa("panels.distributors.commissioning.set_outlet",t)}
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
    `}};t([pe()],gn.prototype,"config",void 0),t([pe({attribute:!1})],gn.prototype,"path",void 0),t([pe({type:Array})],gn.prototype,"distributors",void 0),t([pe({type:Array})],gn.prototype,"zones",void 0),t([pe({type:Boolean})],gn.prototype,"isLoading",void 0),t([pe({type:Boolean})],gn.prototype,"isSaving",void 0),t([ge()],gn.prototype,"_expanded",void 0),t([pe({type:Boolean})],gn.prototype,"_showAdd",void 0),t([pe()],gn.prototype,"_newName",void 0),t([pe()],gn.prototype,"_confirmDeleteId",void 0),t([ge()],gn.prototype,"_armConfirmId",void 0),t([ge()],gn.prototype,"_confirmResyncHomeId",void 0),t([ge()],gn.prototype,"_confirmSetOutletId",void 0),t([ge()],gn.prototype,"_outletDraft",void 0),t([ge()],gn.prototype,"_outletRows",void 0),t([ge()],gn.prototype,"_saveStatus",void 0),gn=t([ce("smart-irrigation-view-distributor-settings")],gn);let mn=class extends(Fa(le)){constructor(){super(...arguments),this.zones=[],this.modules=[],this.allmodules=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._updateScheduled=!1,this.globalDebounceTimer=null,this.moduleCache=new Map,this.debouncedSave=(()=>{let e=null;return t=>{e&&clearTimeout(e),e=window.setTimeout(()=>{this.saveToHA(t),e=null},500)}})()}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}firstUpdated(){qs().catch(e=>{console.error("Failed to load HA form:",e)})}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:fe+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;e&&(this.isLoading=!0,this._scheduleUpdate());try{const[e,t,s,i]=await Promise.all([Es(this.hass),Ts(this.hass),Ds(this.hass),Hs(this.hass)]);this.config=e,this.zones=t,this.modules=s,this.allmodules=i,this._initialLoadDone=!0,this.moduleCache.clear()}catch(e){console.error("Error fetching data:",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}async handleAddModule(){var e,t;if((null===(t=null===(e=this.moduleInput)||void 0===e?void 0:e.selectedOptions)||void 0===t?void 0:t[0])&&!this.isSaving){this.isSaving=!0,this._scheduleUpdate();try{const e=this.moduleInput.selectedOptions[0].text,t=this.allmodules.find(t=>t.name===e);if(!t)return;const s={name:e,description:t.description,config:t.config,schema:t.schema};this.modules=[...this.modules,s],this.moduleCache.clear(),this._scheduleUpdate(),await this.saveToHA(s),await this._fetchData()}catch(e){console.error("Error adding module:",e),await this._fetchData()}finally{this.isSaving=!1,this._scheduleUpdate()}}}async handleRemoveModule(e,t){if(!this.isSaving){this.isSaving=!0,this._scheduleUpdate();try{const e=this.modules[t],a=null==e?void 0:e.id;this.modules;this.modules=this.modules.filter((e,s)=>s!==t),this.moduleCache.clear(),this._scheduleUpdate(),this.hass&&void 0!==a&&await(s=this.hass,i=a.toString(),s.callApi("POST",fe+"/modules",{id:i,remove:!0}))}catch(e){console.error("Error removing module:",e),Ba(this,this.hass,"common.errors.delete_failed",e),await this._fetchData()}finally{this.isSaving=!1,this._scheduleUpdate()}var s,i}}async saveToHA(e){if(this.hass)try{await Ms(this.hass,e)}catch(e){throw console.error("Error saving module:",e),Ba(this,this.hass,"common.errors.save_failed",e),e}}renderModule(e,t){if(!this.hass)return W``;const s=this.zones.filter(t=>t.module===e.id).length,i=`module-${e.id||t}-${s}-${JSON.stringify(e)}`;if(this.moduleCache.has(i))return this.moduleCache.get(i);const a=W`
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          ${this.renderUsageChip(s)}
        </div>
        <div class="card-content">
          <div class="item-description">${e.description}</div>
          <div class="moduleconfig">
            <label class="subheader"
              >${Oa("panels.modules.cards.module.labels.configuration",this.hass.language)}
              (*
              ${Oa("panels.modules.cards.module.labels.required",this.hass.language)})</label
            >
            ${e.schema?Object.entries(e.schema).map(([e])=>this.renderConfig(t,e)):null}
          </div>
          <div class="card-footer">
            ${s?W`<div class="weather-note">
                  ${Oa("panels.modules.cards.module.errors.cannot-delete-module-because-zones-use-it",this.hass.language)}
                </div>`:W`<button
                  class="action-btn danger"
                  @click="${e=>this.handleRemoveModule(e,t)}"
                >
                  <ha-icon icon="mdi:delete"></ha-icon>
                  ${Oa("common.actions.delete",this.hass.language)}
                </button>`}
          </div>
        </div>
      </ha-card>
    `;return this.moduleCache.set(i,a),a}renderUsageChip(e){return this.hass?e?W`<span class="usage-chip"
          >${Oa("panels.setup.advanced.used_by_zones",this.hass.language,"{count}",e)}</span
        >`:W`<span class="usage-chip unused"
          >${Oa("panels.setup.advanced.not_used",this.hass.language)}</span
        >`:W``}renderConfig(e,t){var s,i;const a=Object.values(this.modules).at(e);if(!a||!this.hass)return;const n=a.schema[t],o=n.name,r=e=>{try{const t=Oa(e,this.hass.language);return null==t?void 0:t}catch(e){return}},l="panels.modules.cards.module.fields."+o,d=null!==(s=r(l+".name"))&&void 0!==s?s:function(e){if(e)return(e=e.replace("_"," ")).charAt(0).toUpperCase()+e.slice(1)}(o),c=null!==(i=r(l+".description"))&&void 0!==i?i:n.description;let h="";null==a.config&&(a.config=[]),o in a.config&&(h=a.config[o]);let u=W``;if("boolean"==n.type)u=W`<input
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
        ${Object.entries(n.options).map(([e,s])=>W`<option
              value="${Ha(s,0)}"
              ?selected="${h===Ha(s,0)}"
            >
              ${Oa("panels.modules.cards.module.translated-options."+Ha(s,1),t)}
            </option>`)}
      </select>`}return W`<ha-settings-row>
      <span slot="heading"
        >${d}${n.required?" *":""}</span
      >
      ${c?W`<span slot="description">${c}</span>`:""}
      ${u}
    </ha-settings-row>`}handleEditConfig(e,t){this.modules=Object.values(this.modules).map((s,i)=>i===e?t:s),this.moduleCache.clear(),this._scheduleUpdate(),this.debouncedSave(t)}render(){return this.hass?W`
      <ha-card header="${Oa("panels.modules.title",this.hass.language)}">
        <div class="card-content">
          ${Oa("panels.modules.description",this.hass.language)}
          ${this.isLoading?W`<div class="loading-indicator">
                ${Oa("common.loading-messages.general",this.hass.language)}
              </div>`:W`
                <div class="add-row">
                  <select
                    id="moduleInput"
                    class="settings-input"
                    aria-label="${Oa("common.labels.module",this.hass.language)}"
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
                    ${this.isSaving?Oa("common.saving-messages.adding",this.hass.language):Oa("panels.modules.cards.add-module.actions.add",this.hass.language)}
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
    `}};t([pe()],mn.prototype,"config",void 0),t([pe({type:Array})],mn.prototype,"zones",void 0),t([pe({type:Array})],mn.prototype,"modules",void 0),t([pe({type:Array})],mn.prototype,"allmodules",void 0),t([pe({type:Boolean})],mn.prototype,"isLoading",void 0),t([pe({type:Boolean})],mn.prototype,"isSaving",void 0),t([me("#moduleInput")],mn.prototype,"moduleInput",void 0),mn=t([ce("smart-irrigation-view-modules")],mn);let vn=class extends(Fa(le)){constructor(){super(...arguments),this.zones=[],this.mappings=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this.debounceTimers=new Map,this.globalDebounceTimer=null,this.mappingCache=new Map,this._updateScheduled=!1,this._lastUpdateTime=0,this._updateThrottleDelay=16}_scheduleUpdate(){if(this._updateScheduled)return;const e=performance.now()-this._lastUpdateTime;e<this._updateThrottleDelay?setTimeout(()=>{this._updateScheduled=!1,this._lastUpdateTime=performance.now(),this.requestUpdate()},this._updateThrottleDelay-e):(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this._lastUpdateTime=performance.now(),this.requestUpdate()}))}firstUpdated(){qs().catch(e=>{console.error("Failed to load HA form:",e)})}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e)})},{type:fe+"_config_updated"})]}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[t,s,i]=await Promise.all([Es(this.hass),Ts(this.hass),Is(this.hass)]);this.config=t,this.zones=s,this.mappings=i,this._initialLoadDone=!0,this.mappingCache.clear()}catch(e){console.error("Error fetching data:",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{e&&(this.isLoading=!1),this._scheduleUpdate()}}handleAddMapping(){if(!this.mappingNameInput.value.trim())return;const e={[De]:"",[He]:"",[Me]:"",[Ie]:"",[Ne]:"",[Le]:"",[Re]:"",[Pe]:"",[Be]:""},t={name:this.mappingNameInput.value.trim(),mappings:e};this.mappings=[...this.mappings,t],this.isSaving=!0,this.saveToHA(t).then(()=>(this.mappingNameInput.value="",this._fetchData())).catch(e=>{console.error("Failed to add mapping:",e),Ba(this,this.hass,"common.errors.save_failed",e),this.mappings=this.mappings.slice(0,-1)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()})}handleRemoveMapping(e,t){const s=this.mappings[t].id;if(null==s)return;const i=[...this.mappings];var a,n;(this.mappings=this.mappings.filter((e,s)=>s!==t),this.mappingCache.delete(s.toString()),this.hass)&&(this.isSaving=!0,(a=this.hass,n=s.toString(),a.callApi("POST",fe+"/mappings",{id:n,remove:!0})).catch(e=>{console.error("Failed to delete mapping:",e),Ba(this,this.hass,"common.errors.delete_failed",e),this.mappings=i,this._fetchData().catch(e=>{console.error("Failed to refresh data after delete error:",e)})}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}))}handleEditMapping(e,t){this.mappings[e]=t,t.id&&this.mappingCache.delete(t.id.toString()),this.globalDebounceTimer&&clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=window.setTimeout(()=>{this.isSaving=!0,this.saveToHA(t).catch(e=>{console.error("Failed to save mapping:",e),Ba(this,this.hass,"common.errors.save_failed",e)}).finally(()=>{this.isSaving=!1,this._scheduleUpdate()}),this.globalDebounceTimer=null},500),this._scheduleUpdate()}async saveToHA(e){var t;if(!this.hass)throw new Error("Home Assistant connection not available");const s=[],i=this.hass.states;for(const t in e.mappings){const a=e.mappings[t].sensorentity;if(a&&""!==a.trim()){const n=a.trim();e.mappings[t].sensorentity=n,n in i||s.push(n)}}if(s.length>0){const e=null===(t=this.shadowRoot)||void 0===t?void 0:t.querySelector("ha-card");throw e&&Ia({body:{message:Oa("panels.mappings.cards.mapping.errors.source_does_not_exist",this.hass.language)+": "+s.join(", ")},error:Oa("panels.mappings.cards.mapping.errors.invalid_source",this.hass.language)},e),new Error("Invalid sensor entities found")}const{id:a,name:n,mappings:o}=e;await Ns(this.hass,{id:a,name:n,mappings:o})}renderMappingSetting(e,t){const s=this.mappings[e];if(!s||!this.hass)return W``;const i=s.mappings[t];return W`
      <div class="mappingline">
        <div class="mappingsettingname">
          <label for="${`${t}_${e}`}">
            ${Oa(`panels.mappings.cards.mapping.items.${t.toLowerCase()}`,this.hass.language)}
          </label>
        </div>
        <div class="mappingsettingline">
          <label
            >${Oa("panels.mappings.cards.mapping.source",this.hass.language)}:</label
          >
          <div class="radio-group">
            ${this.renderSimpleRadioOptions(e,t,i)}
          </div>
        </div>
        ${this.renderMappingInputs(e,t,i)}
      </div>
    `}renderSimpleRadioOptions(e,t,s){if(!this.hass||!this.config)return W``;const i=t===He||t===Re,a=s[Ke];return W`
      ${!i&&this.config.use_weather_service?W`
            <label>
              <input
                type="radio"
                name="${t}_${e}_source"
                value="${Ue}"
                ?checked="${a===Ue}"
                @change="${s=>this.handleSimpleSourceChange(e,t,s)}"
              />
              ${Oa("panels.mappings.cards.mapping.sources.weather_service",this.hass.language)}
            </label>
          `:""}
      ${i?W`
            <label>
              <input
                type="radio"
                name="${t}_${e}_source"
                value="${Ge}"
                ?checked="${a===Ge}"
                @change="${s=>this.handleSimpleSourceChange(e,t,s)}"
              />
              ${Oa("panels.mappings.cards.mapping.sources.none",this.hass.language)}
            </label>
          `:""}

      <label>
        <input
          type="radio"
          name="${t}_${e}_source"
          value="${je}"
          ?checked="${a===je}"
          @change="${s=>this.handleSimpleSourceChange(e,t,s)}"
        />
        ${Oa("panels.mappings.cards.mapping.sources.sensor",this.hass.language)}
      </label>

      <label>
        <input
          type="radio"
          name="${t}_${e}_source"
          value="${Fe}"
          ?checked="${a===Fe}"
          @change="${s=>this.handleSimpleSourceChange(e,t,s)}"
        />
        ${Oa("panels.mappings.cards.mapping.sources.static",this.hass.language)}
      </label>
    `}handleSimpleSourceChange(e,t,s){const i=this.mappings[e],a=s.target.value;this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[Ke]:a,[Ve]:""})})}))}handleSimpleInputChange(e,t,s,i){const a=this.mappings[e],n=i.target.value;this.handleEditMapping(e,Object.assign(Object.assign({},a),{mappings:Object.assign(Object.assign({},a.mappings),{[t]:Object.assign(Object.assign({},a.mappings[t]),{[s]:n})})}))}renderMappingInputs(e,t,s){if(!this.hass)return W``;const i=s[Ke];return W`
      ${i===je?this.renderSensorInput(e,t,s):""}
      ${i===Fe?this.renderStaticValueInput(e,t,s):""}
      ${i===je||i===Fe?this.renderUnitSelect(e,t,s):""}
      ${t!==Le||i!==je&&i!==Fe?"":this.renderPressureTypeSelect(e,t,s)}
      ${i===je?this.renderAggregateSelect(e,t,s):""}
    `}renderSensorInput(e,t,s){if(!this.hass)return W``;const i=`${t}_${e}`;return W`
      <div class="mappingsettingline">
        <label for="${i}_sensor_entity">
          ${Oa("panels.mappings.cards.mapping.sensor-entity",this.hass.language)}:
        </label>
        <input
          type="text"
          class="settings-input"
          id="${i}_sensor_entity"
          .value="${s[Ve]||""}"
          @change="${s=>this.handleSensorChange(e,t,s)}"
        />
      </div>
    `}renderStaticValueInput(e,t,s){if(!this.hass)return W``;const i=`${t}_${e}`;return W`
      <div class="mappingsettingline">
        <label for="${i}_static_value">
          ${Oa("panels.mappings.cards.mapping.static_value",this.hass.language)}:
        </label>
        <input
          type="text"
          class="settings-input"
          id="${i}_static_value"
          .value="${s[Ye]||""}"
          @input="${s=>this.handleStaticValueChange(e,t,s)}"
        />
      </div>
    `}renderUnitSelect(e,t,s){if(!this.hass||!this.config)return W``;const i=`${t}_${e}`;return W`
      <div class="mappingsettingline">
        <label for="${i}_unit">
          ${Oa("panels.mappings.cards.mapping.input-units",this.hass.language)}:
        </label>
        <select
          id="${i}_unit"
          class="settings-input"
          @change="${s=>this.handleUnitChange(e,t,s)}"
        >
          ${this.renderUnitOptionsForMapping(t,s)}
        </select>
      </div>
    `}renderPressureTypeSelect(e,t,s){if(!this.hass)return W``;const i=`${t}_${e}`;return W`
      <div class="mappingsettingline">
        <label for="${i}_pressure_type">
          ${Oa("panels.mappings.cards.mapping.pressure-type",this.hass.language)}:
        </label>
        <select
          id="${i}_pressure_type"
          class="settings-input"
          @change="${s=>this.handlePressureTypeChange(e,t,s)}"
        >
          ${this.renderPressureTypes(t,s)}
        </select>
      </div>
    `}renderAggregateSelect(e,t,s){if(!this.hass)return W``;const i=`${t}_${e}`;return W`
      <div class="mappingsettingline">
        <label for="${i}_aggregate">
          ${Oa("panels.mappings.cards.mapping.sensor-aggregate-use-the",this.hass.language)}
        </label>
        <select
          id="${i}_aggregate"
          class="settings-input"
          @change="${s=>this.handleAggregateChange(e,t,s)}"
        >
          ${this.renderAggregateOptionsForMapping(t,s)}
        </select>
        <label for="${i}_aggregate">
          ${Oa("panels.mappings.cards.mapping.sensor-aggregate-of-sensor-values-to-calculate",this.hass.language)}
        </label>
      </div>
    `}handleSensorChange(e,t,s){const i=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[Ve]:s.target.value})})}))}handleStaticValueChange(e,t,s){const i=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[Ye]:s.target.value})})}))}handleUnitChange(e,t,s){const i=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[Xe]:s.target.value})})}))}handlePressureTypeChange(e,t,s){const i=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[We]:s.target.value})})}))}handleAggregateChange(e,t,s){const i=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[Je]:s.target.value})})}))}renderAggregateOptionsForMapping(e,t){if(!this.hass||!this.config)return W``;let s="average";return e===Ie&&(s="delta"),e===Ne&&(s="average"),t[Je]&&(s=t[Je]),W`
      ${Qe.map(e=>this.renderAggregateOption(e,s))}
    `}renderAggregateOption(e,t){if(this.hass&&this.config){return W`<option value="${e}" ?selected="${e===t}">
        ${Oa("panels.mappings.cards.mapping.aggregates."+e,this.hass.language)}
      </option>`}return W``}renderPressureTypes(e,t){if(this.hass&&this.config){let e=W``;const s=t[We];return e=W`${e}
        <option
          value="${Ze}"
          ?selected="${s===Ze}"
        >
          ${Oa("panels.mappings.cards.mapping.pressure_types."+Ze,this.hass.language)}
        </option>
        <option
          value="${qe}"
          ?selected="${s===qe}"
        >
          ${Oa("panels.mappings.cards.mapping.pressure_types."+qe,this.hass.language)}
        </option>`,e}return W``}renderUnitOptionsForMapping(e,t){if(!this.hass||!this.config)return W``;const s=function(e){switch(e){case De:case Pe:return[{unit:"°C",system:Oe},{unit:"°F",system:Te}];case Ie:case He:return[{unit:at,system:Oe},{unit:nt,system:Te}];case Ne:return[{unit:dt,system:Oe},{unit:ct,system:Te}];case Me:return[{unit:"%",system:[Oe,Te]}];case Le:return[{unit:"millibar",system:Oe},{unit:"hPa",system:Oe},{unit:"psi",system:Te},{unit:ot,system:Te}];case Be:return[{unit:"km/h",system:Oe},{unit:lt,system:Oe},{unit:rt,system:Te}];case Re:return[{unit:"W/m2",system:Oe},{unit:"MJ/day/m2",system:Oe},{unit:"W/sq ft",system:Te},{unit:"MJ/day/sq ft",system:Te}];default:return[]}}(e);let i=t[Xe];const a=this.config.units;if(!t[Xe])for(const e of s)if("string"==typeof e.system){if(a===e.system){i=e.unit;break}}else{for(const t of e.system)if(a===t.system){i=e.unit;break}if(i===e.unit)break}return W`
      ${s.map(e=>W`
          <option value="${e.unit}" ?selected="${i===e.unit}">
            ${e.unit}
          </option>
        `)}
    `}render(){return this.hass?this.isLoading?W`
        <ha-card
          header="${Oa("panels.mappings.title",this.hass.language)}"
        >
          <div class="card-content">
            <div class="loading-indicator">
              ${Oa("common.loading-messages.general",this.hass.language)}
            </div>
          </div>
        </ha-card>
      `:W`
      <ha-card
        header="${Oa("panels.mappings.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Oa("panels.mappings.description",this.hass.language)}
          <div class="add-row">
            <input
              id="mappingNameInput"
              class="settings-input"
              type="text"
              placeholder="${Oa("panels.mappings.labels.mapping-name",this.hass.language)}"
            />
            <button
              class="action-btn ${this.isSaving?"saving":""}"
              ?disabled="${this.isSaving}"
              @click="${this.handleAddMapping}"
            >
              <ha-icon icon="mdi:plus"></ha-icon>
              ${Oa("panels.mappings.cards.add-mapping.actions.add",this.hass.language)}
            </button>
          </div>
        </div>
      </ha-card>

      ${this.renderMappingsList()}
    `:W``}renderUsageChip(e){return this.hass?e?W`<span class="usage-chip"
          >${Oa("panels.setup.advanced.used_by_zones",this.hass.language,"{count}",e)}</span
        >`:W`<span class="usage-chip unused"
          >${Oa("panels.setup.advanced.not_used",this.hass.language)}</span
        >`:W``}renderMappingsList(){const e=this.mappings.slice(0,Math.min(this.mappings.length,10)),t=this.mappings.slice(10);return W`
      ${e.map((e,t)=>this.renderMappingCard(e,t))}
      ${t.length>0?W`
            <div class="load-more">
              <button @click="${this.loadMoreMappings}">
                Load ${t.length} more mappings...
              </button>
            </div>
          `:""}
    `}renderMappingCard(e,t){if(!this.hass)return W``;const s=this.zones.filter(t=>t.mapping===e.id).length;return W`
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          ${this.renderUsageChip(s)}
        </div>
        <div class="card-content">
          <ha-settings-row>
            <span slot="heading"
              >${Oa("panels.mappings.labels.mapping-name",this.hass.language)}</span
            >
            <input
              id="name${e.id}"
              class="settings-input"
              type="text"
              .value="${e.name}"
              @input="${s=>this.handleEditMapping(t,Object.assign(Object.assign({},e),{name:s.target.value}))}"
            />
          </ha-settings-row>
          ${this.renderMappingSettings(e,t)}
          <div class="card-footer">
            ${s?W`<div class="weather-note">
                  ${Oa("panels.mappings.cards.mapping.errors.cannot-delete-mapping-because-zones-use-it",this.hass.language)}
                </div>`:W`<button
                  class="action-btn danger"
                  @click="${e=>this.handleRemoveMapping(e,t)}"
                >
                  <ha-icon icon="mdi:delete"></ha-icon>
                  ${Oa("common.actions.delete",this.hass.language)}
                </button>`}
          </div>
        </div>
      </ha-card>
    `}renderMappingSettings(e,t){const s=Object.entries(e.mappings);return W`
      ${s.map(([e])=>this.renderMappingSetting(t,e))}
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
    `}disconnectedCallback(){super.disconnectedCallback(),this.debounceTimers.forEach(e=>{clearTimeout(e)}),this.debounceTimers.clear(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null),this.mappingCache.clear()}};t([pe()],vn.prototype,"config",void 0),t([pe({type:Array})],vn.prototype,"zones",void 0),t([pe({type:Array})],vn.prototype,"mappings",void 0),t([pe({type:Boolean})],vn.prototype,"isLoading",void 0),t([pe({type:Boolean})],vn.prototype,"isSaving",void 0),t([me("#mappingNameInput")],vn.prototype,"mappingNameInput",void 0),vn=t([ce("smart-irrigation-view-mappings")],vn);const fn="06:00";function _n(e){switch(e){case is:return{mode:e,time:fn};case as:case ns:return{mode:e,offset:0};case os:return{mode:e,azimuth:90};default:return{mode:ss}}}function bn(e,t,s,i){const a=function(e){return e===ss||e===is||e===as||e===ns||e===os}(e)?e:ss,n=_n(a);return a===is&&void 0!==t&&(n.time=t),a!==as&&a!==ns||void 0===s||(n.offset=s),a===os&&void 0!==i&&(n.azimuth=i),n}function yn(e){var t,s,i;return{mode:e.mode,time:e.mode===is?null!==(t=e.time)&&void 0!==t?t:fn:void 0,offset:e.mode===as||e.mode===ns?null!==(s=e.offset)&&void 0!==s?s:0:void 0,azimuth:e.mode===os?null!==(i=e.azimuth)&&void 0!==i?i:90:void 0}}function wn(e){return{start:bn(e.start_mode,e.start_time,e.start_offset,e.start_azimuth),finish:bn(e.finish_mode,e.finish_time,e.finish_offset,e.finish_azimuth),anchor:e.anchor===ls?ls:ds}}function $n(e){const t=e.start.mode!==ss,s=e.finish.mode!==ss;return t||s?t?s?e.anchor===ds?{start:"demand_floored",finish:"exact_deferred",valid:!0}:{start:"exact",finish:"demand_capped_deferred",valid:!0}:{start:"exact",finish:"demand_open",valid:!0}:{start:"demand_open",finish:"exact",valid:!0}:{start:"error",finish:"error",valid:!1}}function xn(e,t){const s=function(e,t){if("all"===e||!Array.isArray(e))return Oa("panels.schedules.summary.zones_all",t);return Oa("panels.schedules.summary.zones_some",t,"count",e.length)}(e.zones,t),i=function(e,t){switch(e.recurrence){case Jt:{const s=(e.days_of_week||[]).map(e=>Oa(`panels.schedules.days.${e}`,t)).join(", ");return Oa("panels.schedules.summary.recurrence_weekly",t,"days",s)}case Qt:return Oa("panels.schedules.summary.recurrence_monthly",t,"day",e.day_of_month||1);case es:{const s=e.interval_hours||24;return e.start_time?Oa("panels.schedules.summary.recurrence_interval_at",t,"hours",s,"time",e.start_time):Oa("panels.schedules.summary.recurrence_interval",t,"hours",s)}default:return Oa("panels.schedules.summary.recurrence_daily",t)}}(e,t);if(e.recurrence===es){return{text:`${i}, ${Oa("panels.schedules.summary.watering",t,"zones",s)}.`,isError:!1}}const a=wn(e),n=a.start.mode!==ss,o=a.finish.mode!==ss;if(!n&&!o)return{text:Oa("panels.schedules.summary.invalid",t),isError:!0};const r=Oa("panels.schedules.summary.watering",t,"zones",s);let l;return l=n?o?a.anchor===ds?Oa("panels.schedules.summary.anchor_finish",t,"finish",kn(a.finish,t),"start",kn(a.start,t)):Oa("panels.schedules.summary.anchor_start",t,"start",kn(a.start,t),"finish",kn(a.finish,t)):Oa("panels.schedules.summary.start_only",t,"when",kn(a.start,t)):Oa("panels.schedules.summary.finish_only",t,"when",kn(a.finish,t)),{text:`${i}, ${r}, ${l}.`,isError:!1}}function kn(e,t){var s,i,a;switch(e.mode){case is:return null!==(s=e.time)&&void 0!==s?s:"";case as:case ns:{const s=Oa(`panels.schedules.summary.${e.mode}`,t),a=null!==(i=e.offset)&&void 0!==i?i:0;if(0===a)return s;return Oa(a<0?"panels.schedules.summary.offset_before":"panels.schedules.summary.offset_after",t,"minutes",Math.abs(a),"event",s)}case os:return Oa("panels.schedules.summary.at_azimuth",t,"degrees",null!==(a=e.azimuth)&&void 0!==a?a:90);default:return""}}const zn=["monday","tuesday","wednesday","thursday","friday","saturday","sunday"];function Sn(){return{name:"",recurrence:"daily",enabled:!0,start_mode:is,start_time:"06:00",finish_mode:ss,action:"irrigate",zones:"all"}}function An(e,t){return Oa(`panels.schedules.types.${e}`,t)||e}let En=class extends le{constructor(){super(...arguments),this.zones=[],this.heading="",this._save=()=>{this.dispatchEvent(new CustomEvent("save",{detail:{value:this.schedule},bubbles:!0,composed:!0}))},this._cancel=()=>{this.dispatchEvent(new CustomEvent("cancel",{bubbles:!0,composed:!0}))}}_emitChanged(e){this.dispatchEvent(new CustomEvent("schedule-changed",{detail:{value:Object.assign(Object.assign({},this.schedule),e)},bubbles:!0,composed:!0}))}_renderZonePicker(){const e="all"===this.schedule.zones||!Array.isArray(this.schedule.zones),t=e?[]:this.schedule.zones.map(String);return W`
      <div class="field">
        <div class="switch-container">
          <input
            type="radio"
            id="zones_all"
            name="zones_mode"
            ?checked="${e}"
            @change=${()=>this._emitChanged({zones:"all"})}
          />
          <label for="zones_all"
            >${Oa("panels.schedules.zones_all",this.hass.language)}</label
          >
          <input
            type="radio"
            id="zones_specific"
            name="zones_mode"
            ?checked="${!e}"
            @change=${()=>this._emitChanged({zones:[]})}
          />
          <label for="zones_specific"
            >${Oa("panels.schedules.zones_specific",this.hass.language)}</label
          >
        </div>
        ${e?"":W`
              <div class="zone-checkboxes">
                ${this.zones.map(e=>W`
                    <label class="zone-check">
                      <input
                        type="checkbox"
                        ?checked="${t.includes(String(e.id))}"
                        @change=${t=>{const s=t.target.checked,i=String(e.id),a=Array.isArray(this.schedule.zones)?[...this.schedule.zones]:[],n=s?[...a,i]:a.filter(e=>e!==i);this._emitChanged({zones:n})}}
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
              >${Oa("panels.schedules.fields.days_of_week",t)}</label
            >
            <div class="day-checkboxes">
              ${zn.map(s=>W`
                  <label class="day-check">
                    <input
                      type="checkbox"
                      ?checked="${(e.days_of_week||[]).includes(s)}"
                      @change=${t=>{const i=t.target.checked,a=e.days_of_week||[],n=i?[...a,s]:a.filter(e=>e!==s);this._emitChanged({days_of_week:n})}}
                    />
                    ${Oa(`panels.schedules.days.${s}`,t)}
                  </label>
                `)}
            </div>
          </div>
        `;case"monthly":return W`
          <div class="field">
            <label
              >${Oa("panels.schedules.fields.day_of_month",t)}</label
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
              >${Oa("panels.schedules.fields.interval_hours",t)}</label
            >
            <div class="input-suffix-row">
              <input
                type="number"
                min="1"
                .value="${String(e.interval_hours||24)}"
                @input=${e=>this._emitChanged({interval_hours:parseInt(e.target.value)})}
              />
              <span class="suffix"
                >${Oa("panels.schedules.hours",t)}</span
              >
            </div>
          </div>
          <div class="field">
            <label
              >${Oa("panels.schedules.fields.start_time",t)}</label
            >
            <input
              type="time"
              .value="${e.start_time||""}"
              @change=${e=>this._emitChanged({start_time:e.target.value||void 0})}
            />
          </div>
        `;default:return W``}}_renderRowStepper(e,t){var s,i,a;const n=this.hass.language;switch(e.mode){case is:return W`
          <input
            type="time"
            .value="${null!==(s=e.time)&&void 0!==s?s:"06:00"}"
            @change=${s=>t(Object.assign(Object.assign({},e),{time:s.target.value}))}
          />
        `;case as:case ns:return W`
          <span class="row-inline"
            >${Oa("panels.schedules.fields.offset_by",n)}</span
          >
          <input
            type="number"
            step="1"
            .value="${String(null!==(i=e.offset)&&void 0!==i?i:0)}"
            @input=${s=>{const i=parseInt(s.target.value);t(Object.assign(Object.assign({},e),{offset:isNaN(i)?0:i}))}}
          />
          <span class="row-inline"
            >${Oa("panels.schedules.minutes",n)}</span
          >
        `;case os:return W`
          <input
            type="number"
            min="0"
            max="359"
            step="1"
            .value="${String(null!==(a=e.azimuth)&&void 0!==a?a:90)}"
            @input=${s=>{var i;const a=parseInt(s.target.value);t(Object.assign(Object.assign({},e),{azimuth:isNaN(a)?null!==(i=e.azimuth)&&void 0!==i?i:90:a}))}}
          />
          <span class="row-inline">°</span>
        `;default:return W``}}_renderWindowRow(e,t,s,i){const a=this.hass.language;return W`
      <div class="window-row">
        <label>${Oa(`panels.schedules.fields.${e}_mode`,a)}</label>
        <select
          @change=${e=>i(_n(e.target.value))}
        >
          ${rs.map(e=>W`
              <option value="${e}" ?selected="${t.mode===e}">
                ${Oa(`panels.schedules.bound_mode.${e}`,a)}
              </option>
            `)}
        </select>
        ${this._renderRowStepper(t,i)}
      </div>
      <div class="window-row-help ${"error"===s?"is-error":""}">
        <span class="help-arrow" aria-hidden="true">↳</span>
        <span class="help-text"
          >${Oa(`panels.schedules.help.${s}`,a)}</span
        >
      </div>
    `}_renderAnchorRow(e,t){const s=this.hass.language;return W`
      <div class="window-row">
        <label>${Oa("panels.schedules.fields.anchor",s)}</label>
        <select
          @change=${s=>t(Object.assign(Object.assign({},e),{anchor:s.target.value}))}
        >
          ${[ls,ds].map(t=>W`
              <option value="${t}" ?selected="${e.anchor===t}">
                ${Oa(`panels.schedules.anchor.${t}`,s)}
              </option>
            `)}
        </select>
      </div>
    `}_renderWindowRows(){const e=this.schedule;if(e.recurrence===es)return W``;const t=wn(e),s=$n(t),i=e=>this._emitChanged(function(e){const t=yn(e.start),s=yn(e.finish);return{start_mode:t.mode,start_time:t.time,start_offset:t.offset,start_azimuth:t.azimuth,finish_mode:s.mode,finish_time:s.time,finish_offset:s.offset,finish_azimuth:s.azimuth,anchor:e.anchor}}(e)),a=t.start.mode!==ss&&t.finish.mode!==ss;return W`
      ${this._renderWindowRow("start",t.start,s.start,e=>i(Object.assign(Object.assign({},t),{start:e})))}
      ${this._renderWindowRow("finish",t.finish,s.finish,e=>i(Object.assign(Object.assign({},t),{finish:e})))}
      ${a?this._renderAnchorRow(t,i):""}
    `}_canSave(){const e=this.schedule;return e.recurrence===es||$n(wn(e)).valid}_renderSection(e,t){return W`
      <div class="sect-card">
        <h4>
          ${Oa(`panels.schedules.sections.${e}`,this.hass.language)}
        </h4>
        ${t}
      </div>
    `}_renderSummary(){const e=xn(this.schedule,this.hass.language);return W`
      <div class="summary ${e.isError?"is-error":""}">
        ${e.text}
      </div>
    `}_renderSeasonSection(){const e=this.schedule,t=this.hass.language;return W`
      <div class="field">
        <label>${Oa("panels.schedules.season.label",t)}</label>
        <div class="rowfields">
          <input
            type="date"
            .value="${e.start_date||""}"
            @change=${e=>this._emitChanged({start_date:e.target.value||void 0})}
          />
          <span class="suffix"
            >${Oa("panels.schedules.season.to",t)}</span
          >
          <input
            type="date"
            .value="${e.end_date||""}"
            @change=${e=>this._emitChanged({end_date:e.target.value||void 0})}
          />
        </div>
        <span class="field-help"
          >${Oa("panels.schedules.season.note",t)}</span
        >
      </div>
    `}render(){if(!this.hass||!this.schedule)return W``;const e=this.schedule,t=this.hass.language;return W`
      <ha-dialog open @closed=${this._cancel}>
        <div slot="heading" class="dialog-heading-row">
          <span>${this.heading}</span>
          <label class="enabled-toggle">
            <input
              type="checkbox"
              ?checked="${e.enabled}"
              @change=${e=>this._emitChanged({enabled:e.target.checked})}
            />
            ${Oa("panels.schedules.fields.enabled",t)}
          </label>
        </div>
        <div class="dialog-content">
          ${this._renderSummary()}

          <div class="field">
            <label>${Oa("panels.schedules.fields.name",t)}</label>
            <input
              type="text"
              .value="${e.name}"
              @input=${e=>this._emitChanged({name:e.target.value})}
              required
            />
          </div>

          ${this._renderSection("when",W`
              <div class="field">
                <select
                  aria-label="${Oa("panels.schedules.fields.recurrence",t)}"
                  @change=${e=>this._emitChanged({recurrence:e.target.value})}
                >
                  ${ts.map(s=>W`
                      <option value="${s}" ?selected="${e.recurrence===s}">
                        ${An(s,t)}
                      </option>
                    `)}
                </select>
              </div>
              ${this._renderRecurrenceFields()} ${this._renderWindowRows()}
            `)}
          ${this._renderSection("zones",this._renderZonePicker())}
          ${this._renderSection("season",this._renderSeasonSection())}
        </div>

        <button
          slot="secondaryAction"
          class="dialog-btn"
          @click=${this._cancel}
        >
          ${Oa("common.actions.cancel",this.hass.language)}
        </button>
        <button
          slot="primaryAction"
          class="dialog-btn dialog-btn-primary"
          ?disabled="${!this._canSave()}"
          @click=${this._save}
        >
          ${Oa("common.actions.save",this.hass.language)}
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
        .field label {
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
        /* Dialog heading: the title plus the Enabled toggle (GitLab #30) —
           it reads as a property of the schedule, not of the date range it
           used to sit beside. */
        .dialog-heading-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
          width: 100%;
        }
        .enabled-toggle {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.8125rem;
          font-weight: 400;
          color: var(--secondary-text-color);
          cursor: pointer;
        }
        .enabled-toggle input[type="checkbox"] {
          width: 16px;
          height: 16px;
          accent-color: var(--primary-color);
        }
        /* The read-only summary sentence (GitLab #30): describes the
           schedule's own configuration only, never live bucket/weather
           state — see schedule-summary.ts. */
        .summary {
          border-left: 3px solid var(--primary-color);
          background: color-mix(in srgb, var(--primary-color) 7%, transparent);
          border-radius: 0 8px 8px 0;
          padding: 11px 14px;
          font-size: 0.90625rem;
          line-height: 1.6;
          margin-bottom: 18px;
          color: var(--primary-text-color);
        }
        .summary.is-error {
          border-left-color: var(--error-color, #db4437);
          background: color-mix(
            in srgb,
            var(--error-color, #db4437) 8%,
            transparent
          );
        }
        /* WHEN/ZONES/SEASON cards (GitLab #30): the heading is small-caps
           and doubles as the label for whatever unlabeled control sits
           directly under it. */
        .sect-card {
          border: 1px solid var(--divider-color, #e0e0e0);
          border-radius: 10px;
          padding: 14px 14px 2px;
          margin-bottom: 14px;
        }
        .sect-card > h4 {
          margin: 0 0 12px;
          font-size: 0.71875rem;
          letter-spacing: 0.09em;
          text-transform: uppercase;
          color: var(--secondary-text-color);
          font-weight: 500;
        }
        .rowfields {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
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
      `]}};t([pe({attribute:!1})],En.prototype,"hass",void 0),t([pe({attribute:!1})],En.prototype,"schedule",void 0),t([pe({attribute:!1})],En.prototype,"zones",void 0),t([pe({attribute:!1})],En.prototype,"heading",void 0),En=t([ce("si-schedule-dialog")],En);let Cn=class extends(Fa(le)){constructor(){super(...arguments),this._schedules=[],this._zones=[],this._isLoading=!0,this._showDialog=!1,this._editingSchedule=Sn(),this._editingId=null}hassSubscribe(){return this._load(),[this.hass.connection.subscribeMessage(()=>this._load(),{type:fe+"_config_updated"})]}async _load(){var e;if(this.hass)try{const[t,s]=await Promise.all([(e=this.hass,e.callWS({type:fe+"/schedules"})),Ts(this.hass)]);this._schedules=t||[],this._zones=s||[]}catch(e){console.error("Failed to load schedules",e),Ba(this,this.hass,"common.errors.load_failed",e)}finally{this._isLoading=!1}}_openAdd(){this._editingSchedule=Sn(),this._editingId=null,this._showDialog=!0}_openEdit(e){var t;this._editingSchedule=Object.assign({},e),this._editingId=null!==(t=e.id)&&void 0!==t?t:null,this._showDialog=!0}_closeDialog(){this._showDialog=!1}async _save(){const e=Object.assign({},this._editingSchedule);this._editingId&&(e.id=this._editingId);try{const t=await Rs(this.hass,e);if(t&&!1===t.success)throw new Error(t.error||"");this._closeDialog(),await this._load()}catch(e){console.error("Failed to save schedule",e),Ba(this,this.hass,"common.errors.save_failed",e)}}async _delete(e){try{await(t=this.hass,s=e,t.callWS({type:fe+"/schedule_delete",schedule_id:s})),await this._load()}catch(e){console.error("Failed to delete schedule",e),Ba(this,this.hass,"common.errors.delete_failed",e)}var t,s}_onScheduleChanged(e){this._editingSchedule=e.detail.value}_zonesLabel(e){if("all"===e)return Oa("panels.schedules.zones_all",this.hass.language);if(Array.isArray(e)){const t=e.map(e=>{const t=this._zones.find(t=>String(t.id)===String(e));return t?t.name:e}).join(", ");return t||e.join(", ")}return String(e)}_dialogTitle(){return this._editingId?Oa("panels.schedules.dialog.edit_title",this.hass.language):Oa("panels.schedules.dialog.add_title",this.hass.language)}render(){return this.hass?this._isLoading?W`
        <ha-card
          header="${Oa("panels.schedules.title",this.hass.language)}"
        >
          <div class="card-content">
            ${Oa("common.loading",this.hass.language)}...
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
        header="${Oa("panels.schedules.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Oa("panels.schedules.description",this.hass.language)}
        </div>
        <div class="card-content">
          <button class="add-btn" @click=${this._openAdd}>
            <svg style="width:20px;height:20px" viewBox="0 0 24 24">
              <path fill="currentColor" d="${ja}" />
            </svg>
            ${Oa("panels.schedules.add",this.hass.language)}
          </button>
        </div>
      </ha-card>

      ${0===this._schedules.length?W`
            <ha-card>
              <div class="card-content">
                ${Oa("panels.schedules.no_items",this.hass.language)}
              </div>
            </ha-card>
          `:this._schedules.map(e=>W`
              <ha-card header="${e.name}">
                <div class="card-content">
                  <div class="summary">
                    ${xn(e,this.hass.language).text}
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${Oa("panels.schedules.fields.recurrence",this.hass.language)}:</span
                    >
                    <span
                      >${An(e.recurrence,this.hass.language)}</span
                    >
                  </div>
                  ${"interval"!==e.recurrence&&"time"===e.start_mode&&e.start_time?W`
                        <div class="info-row">
                          <span class="info-label"
                            >${Oa("panels.schedules.fields.start_time",this.hass.language)}:</span
                          >
                          <span>${e.start_time}</span>
                        </div>
                      `:""}
                  ${"interval"!==e.recurrence&&"time"===e.finish_mode&&e.finish_time?W`
                        <div class="info-row">
                          <span class="info-label"
                            >${Oa("panels.schedules.fields.finish_time",this.hass.language)}:</span
                          >
                          <span>${e.finish_time}</span>
                        </div>
                      `:""}
                  ${e.interval_hours?W`
                        <div class="info-row">
                          <span class="info-label"
                            >${Oa("panels.schedules.fields.interval_hours",this.hass.language)}:</span
                          >
                          <span
                            >${e.interval_hours}
                            ${Oa("panels.schedules.hours",this.hass.language)}</span
                          >
                        </div>
                      `:""}
                  ${"interval"===e.recurrence&&e.start_time?W`
                        <div class="info-row">
                          <span class="info-label"
                            >${Oa("panels.schedules.fields.start_time",this.hass.language)}:</span
                          >
                          <span>${e.start_time}</span>
                        </div>
                      `:""}
                  <div class="info-row">
                    <span class="info-label"
                      >${Oa("panels.schedules.fields.zones",this.hass.language)}:</span
                    >
                    <span>${this._zonesLabel(e.zones)}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${Oa("panels.schedules.fields.enabled",this.hass.language)}:</span
                    >
                    <span
                      >${e.enabled?Oa("common.labels.yes",this.hass.language):Oa("common.labels.no",this.hass.language)}</span
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
                        >${Oa("common.actions.edit",this.hass.language)}</span
                      >
                    </div>
                  </div>
                  <div class="action-buttons-right">
                    <div
                      class="action-button-right"
                      @click=${()=>e.id&&this._delete(e.id)}
                    >
                      <span class="action-button-label"
                        >${Oa("common.actions.delete",this.hass.language)}</span
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
        /* Same read-only summary sentence as si-schedule-dialog.ts's own
           ".summary" (GitLab #30) — a schedule can be read without opening
           it. Kept as a second copy of the CSS rather than a shared style
           module because these two components don't otherwise share
           styling infrastructure; the text itself comes from the one
           shared schedule-summary.ts so the wording can't drift. */
        .summary {
          border-left: 3px solid var(--primary-color);
          background: color-mix(in srgb, var(--primary-color) 7%, transparent);
          border-radius: 0 8px 8px 0;
          padding: 11px 14px;
          font-size: 0.90625rem;
          line-height: 1.6;
          margin-bottom: 10px;
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
      `]}};t([pe({attribute:!1})],Cn.prototype,"hass",void 0),t([ge()],Cn.prototype,"_schedules",void 0),t([ge()],Cn.prototype,"_zones",void 0),t([ge()],Cn.prototype,"_isLoading",void 0),t([ge()],Cn.prototype,"_showDialog",void 0),t([ge()],Cn.prototype,"_editingSchedule",void 0),t([ge()],Cn.prototype,"_editingId",void 0),Cn=t([ce("smart-irrigation-view-schedules")],Cn);let Tn=class extends(Fa(le)){constructor(){super(...arguments),this._forecast=null,this._mappings=[],this._records=new Map,this._loading=!0,this._metric=!0,this._climate=[]}hassSubscribe(){return this._fetch(),[this.hass.connection.subscribeMessage(()=>this._fetch(),{type:fe+"_config_updated"})]}async _fetch(){var e,t;if(this.hass)try{const[s,i,a,n]=await Promise.all([(t=this.hass,t.callWS({type:fe+"/weather_forecast"})),Is(this.hass),Es(this.hass),Ls(this.hass)]);this._forecast=s,this._mappings=i||[],this._metric=(null==a?void 0:a.units)!==Te;const o=n?Object.values(n):[];this._climate=o.length>0&&(null===(e=o[0])||void 0===e?void 0:e.monthly_estimates)||[];const r=new Map;await Promise.all(this._mappings.map(async e=>{if(void 0!==e.id)try{r.set(e.id,await((e,t,s=10)=>e.callWS({type:fe+"/weather_records",mapping_id:t,limit:s}))(this.hass,e.id.toString(),0)||[])}catch(e){}})),this._records=r}catch(e){console.error("Failed to fetch weather data",e)}finally{this._loading=!1}}render(){return this.hass?W`${this._renderForecast()} ${this._renderRecords()}
    ${this._renderSeasonal()}`:W``}_renderSeasonal(){if(!this.hass)return W``;const e=this.hass.language;return W`
      <ha-card
        header="${Oa("panels.setup.weather_data.seasonal_title",e)}"
      >
        <div class="card-content">
          ${0===this._climate.length?W`<div class="weather-note">
                ${Oa("panels.zones.calendar.no_data",e)}
              </div>`:W`
                <div class="seasonal-table">
                  <div class="weather-header">
                    <span
                      >${Oa("panels.zones.calendar.month",e)}</span
                    >
                    <span>${Oa("panels.zones.calendar.et",e)}</span>
                    <span
                      >${Oa("panels.zones.calendar.precipitation",e)}</span
                    >
                    <span
                      >${Oa("panels.zones.calendar.avg_temp",e)}</span
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
        header="${Oa("panels.setup.weather_data.forecast_title",e)}"
      >
        <div class="card-content">
          ${t&&t.available&&0!==t.days.length?W`
                <div class="forecast-row">
                  ${t.days.map(t=>this._renderForecastDay(t,e))}
                </div>
              `:W`<div class="weather-note">
                ${Oa("panels.setup.weather_data.forecast_none",e)}
              </div>`}
        </div>
      </ha-card>
    `}_renderForecastDay(e,t){const s=(()=>{try{return new Intl.DateTimeFormat(t,{weekday:"short",month:"short",day:"numeric"}).format(new Date(e.date+"T00:00:00"))}catch(t){return e.date}})(),i=e=>{const t=ln(e,"temperature",this._metric);return t?`${Math.round(t.value)}°`:"-"};return W`
      <div class="forecast-day">
        <div class="forecast-date">${s}</div>
        <div class="forecast-temps">
          <span class="hi">${i(e.temp_max)}</span>
          <span class="lo">${i(e.temp_min)}</span>
        </div>
        <div class="forecast-meta">
          <ha-icon icon="mdi:weather-rainy"></ha-icon>${dn(e.precipitation,"precipitation",this._metric)}
        </div>
        <div class="forecast-meta">
          <ha-icon icon="mdi:weather-windy"></ha-icon>${dn(e.windspeed,"windspeed",this._metric)}
        </div>
      </div>
    `}_renderRecords(){if(!this.hass)return W``;const e=this.hass.language;return this._loading&&0===this._mappings.length?W`<ha-card
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
      </ha-card>`:W`${this._mappings.map(t=>this._renderMappingRecords(t,e))}`}_renderMappingRecords(e,t){const s=void 0!==e.id&&this._records.get(e.id)||[],i=`${Oa("panels.mappings.weather-records.title",t)} — ${e.name}`,a=e=>{try{return t=e,Number.isNaN(Ya(t).getTime())?"-":function(e){const t=Ya(e);return`${Va(t.getMonth()+1)}-${Va(t.getDate())} ${Va(t.getHours())}:${Va(t.getMinutes())}`}(e)}catch(e){return"-"}var t};return W`
      <ha-card header="${i}">
        <div class="card-content">
          ${0===s.length?W`<div class="weather-note">
                ${Oa("panels.mappings.weather-records.no-data",t)}
              </div>`:W`
                <div class="weather-table">
                  <div class="weather-header">
                    <span
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
                    >
                  </div>
                  ${s.map(e=>W`
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
    `}};t([pe()],Tn.prototype,"narrow",void 0),t([ge()],Tn.prototype,"_forecast",void 0),t([ge()],Tn.prototype,"_mappings",void 0),t([ge()],Tn.prototype,"_records",void 0),t([ge()],Tn.prototype,"_loading",void 0),t([ge()],Tn.prototype,"_metric",void 0),t([ge()],Tn.prototype,"_climate",void 0),Tn=t([ce("smart-irrigation-view-weather-data")],Tn);let On=class extends(Fa(le)){constructor(){super(...arguments),this._saving=!1}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch experimental config:",e)}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to refresh experimental config:",e)})},{type:fe+"_config_updated"})]}async _fetchData(){if(this.hass)try{this.config=await Es(this.hass)}catch(e){console.error("Error fetching config:",e),Ba(this,this.hass,"common.errors.load_failed",e)}}async _toggle(e,t){if(this.hass&&this.config){this.config=Object.assign(Object.assign({},this.config),{[e]:t}),this._saving=!0;try{await Cs(this.hass,{[e]:t})}catch(e){console.error("Error saving experimental config:",e),Ba(this,this.hass,"common.errors.save_failed",e),await this._fetchData()}finally{this._saving=!1}}}render(){var e,t;return this.hass&&this.config?W`
      ${this._renderIntro()}
      ${this._renderToggleCard("observed_watering","observed_watering_enabled",this.config.observed_watering_enabled)}
      ${this._renderToggleCard("live_estimate","live_estimate_enabled",this.config.live_estimate_enabled)}
      ${this._renderToggleCard("distributors","distributors_enabled",this.config.distributors_enabled)}
      ${this._renderContinuousUpdatesCard()}
      ${this._renderToggleCard("hourly_calculation","hourlycalculation",this.config.hourlycalculation)}
    `:W`<div class="loading-indicator">
        ${Oa("common.loading-messages.configuration",null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en")}
      </div>`}_renderContinuousUpdatesCard(){if(!this.hass||!this.config)return W``;const e="panels.experimental.continuous_updates",t=this.config.continuousupdates;return W`
      <ha-card header="${Oa(`${e}.title`,this.hass.language)}">
        <div class="card-content description-text">
          ${Oa(`${e}.description`,this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>${Oa(`${e}.label`,this.hass.language)}</label>
            <ha-switch
              .checked="${t}"
              ?disabled="${this._saving}"
              @change="${e=>this._toggle("continuousupdates",e.target.checked)}"
            ></ha-switch>
          </div>
          ${t?W`<div class="setting-row">
                <label>
                  ${Oa(`${e}.debounce_label`,this.hass.language)}
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
            ${Oa(`${e}.note`,this.hass.language)}
          </div>
        </div>
      </ha-card>
    `}async _saveDebounce(e){if(!this.hass||!this.config)return;const t=Number.parseInt(e,10);if(Number.isNaN(t)||t<0)await this._fetchData();else{this.config=Object.assign(Object.assign({},this.config),{[$e]:t}),this._saving=!0;try{await Cs(this.hass,{[$e]:t})}catch(e){console.error("Error saving sensor debounce:",e),Ba(this,this.hass,"common.errors.save_failed",e),await this._fetchData()}finally{this._saving=!1}}}_renderIntro(){return this.hass?W`
      <div class="experimental-banner">
        <ha-icon icon="mdi:flask-outline"></ha-icon>
        <div>
          <div class="experimental-banner-title">
            ${Oa("panels.experimental.title",this.hass.language)}
          </div>
          <div class="experimental-banner-text">
            ${Oa("panels.experimental.warning",this.hass.language)}
          </div>
        </div>
      </div>
    `:W``}_renderToggleCard(e,t,s){if(!this.hass)return W``;const i=`panels.experimental.${e}`;return W`
      <ha-card header="${Oa(`${i}.title`,this.hass.language)}">
        <div class="card-content description-text">
          ${Oa(`${i}.description`,this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>${Oa(`${i}.label`,this.hass.language)}</label>
            <ha-switch
              .checked="${s}"
              ?disabled="${this._saving}"
              @change="${e=>this._toggle(t,e.target.checked)}"
            ></ha-switch>
          </div>
          <div class="setting-note">
            ${Oa(`${i}.note`,this.hass.language)}
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
    `}};t([pe()],On.prototype,"narrow",void 0),t([ge()],On.prototype,"config",void 0),t([ge()],On.prototype,"_saving",void 0),On=t([ce("smart-irrigation-view-experimental")],On);var Dn;!function(e){e.WeatherLocation="weather-location",e.Zones="zones",e.Distributors="distributors",e.WhenToWater="when-to-water",e.Advanced="advanced",e.Experimental="experimental",e.Help="help"}(Dn||(Dn={}));const Hn={[Dn.WeatherLocation]:"panels.setup.tabs.weather_location",[Dn.Zones]:"panels.setup.tabs.my_zones",[Dn.Distributors]:"panels.setup.tabs.distributors",[Dn.WhenToWater]:"panels.setup.tabs.when_to_water",[Dn.Advanced]:"panels.setup.tabs.advanced",[Dn.Experimental]:"panels.setup.tabs.experimental",[Dn.Help]:"panels.help.title"};let Mn=class extends(Fa(le)){hassSubscribe(){return this._fetchConfig(),[this.hass.connection.subscribeMessage(()=>this._fetchConfig(),{type:fe+"_config_updated"})]}async _fetchConfig(){if(this.hass)try{this.config=await Es(this.hass)}catch(e){console.error("Failed to fetch setup config:",e)}}get _distributorsEnabled(){var e,t;return null!==(t=null===(e=this.config)||void 0===e?void 0:e.distributors_enabled)&&void 0!==t&&t}get _activeTab(){var e;const t=null===(e=this.path)||void 0===e?void 0:e.subpage;return Object.values(Dn).includes(null!=t?t:"")?t:Dn.WeatherLocation}_selectTab(e){Na(0,Ga("setup",e))}_openWizard(){this.dispatchEvent(new CustomEvent("open-wizard",{bubbles:!0,composed:!0}))}render(){if(!this.hass)return W``;const e=this._distributorsEnabled,t=Object.values(Dn).filter(t=>t!==Dn.Distributors||e);let s=this._activeTab;return s!==Dn.Distributors||e||(s=Dn.WeatherLocation),W`
      <div class="setup-container">
        <nav class="setup-nav">
          ${t.map(e=>W`
              <button
                class="setup-nav-btn ${s===e?"active":""}"
                @click="${()=>this._selectTab(e)}"
              >
                ${Oa(Hn[e],this.hass.language)}
              </button>
            `)}
          <button
            class="setup-nav-btn wizard-btn"
            @click="${this._openWizard}"
            title="${Oa("wizard.title",this.hass.language)}"
          >
            <ha-icon icon="mdi:creation"></ha-icon>
            ${Oa("wizard.open_button",this.hass.language)}
          </button>
        </nav>
        <div class="setup-content">${this._renderContent(s)}</div>
      </div>
    `}_renderContent(e){if(!this.hass)return W``;switch(e){case Dn.WeatherLocation:return W`
          <smart-irrigation-view-general
            .hass="${this.hass}"
            .narrow="${this.narrow}"
            section="weather-location"
          ></smart-irrigation-view-general>
          <smart-irrigation-view-weather-data
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-weather-data>
        `;case Dn.Zones:return W`<smart-irrigation-view-zone-settings
          .hass="${this.hass}"
          .narrow="${this.narrow}"
          .path="${this.path}"
        ></smart-irrigation-view-zone-settings>`;case Dn.Distributors:return W`<smart-irrigation-view-distributor-settings
          .hass="${this.hass}"
          .narrow="${this.narrow}"
          .path="${this.path}"
        ></smart-irrigation-view-distributor-settings>`;case Dn.WhenToWater:return W`
          <smart-irrigation-view-general
            .hass="${this.hass}"
            .narrow="${this.narrow}"
            section="when-to-water"
          ></smart-irrigation-view-general>
          <smart-irrigation-view-schedules
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-schedules>
        `;case Dn.Advanced:return W`
          <smart-irrigation-view-modules
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-modules>
          <smart-irrigation-view-mappings
            .hass="${this.hass}"
            .narrow="${this.narrow}"
          ></smart-irrigation-view-mappings>
        `;case Dn.Experimental:return W`<smart-irrigation-view-experimental
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-experimental>`;case Dn.Help:return this._renderHelp()}}_renderHelp(){return this.hass?W`
      <ha-card
        header="${Oa("panels.help.cards.how-to-get-help.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Oa("panels.help.cards.how-to-get-help.first-read-the",this.hass.language)}
          <a href="${"https://justchr.github.io/HAsmartirrigation/"}" target="_blank" rel="noopener noreferrer"
            >${Oa("panels.help.cards.how-to-get-help.wiki",this.hass.language)}</a
          >.
          ${Oa("panels.help.cards.how-to-get-help.if-you-still-need-help",this.hass.language)}
          <a
            href="https://community.home-assistant.io/t/smart-irrigation-save-water-by-precisely-watering-your-lawn-garden"
            target="_blank"
            rel="noopener noreferrer"
            >${Oa("panels.help.cards.how-to-get-help.community-forum",this.hass.language)}</a
          >
          ${Oa("panels.help.cards.how-to-get-help.or-open-a",this.hass.language)}
          <a href="${"https://github.com/JustChr/HAsmartirrigation/issues"}" target="_blank" rel="noopener noreferrer"
            >${Oa("panels.help.cards.how-to-get-help.github-issue",this.hass.language)}</a
          >
          (${Oa("panels.help.cards.how-to-get-help.english-only",this.hass.language)}).
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
    `}};var In;t([pe({attribute:!1})],Mn.prototype,"hass",void 0),t([pe({type:Boolean})],Mn.prototype,"narrow",void 0),t([pe({attribute:!1})],Mn.prototype,"path",void 0),t([ge()],Mn.prototype,"config",void 0),Mn=t([ce("smart-irrigation-view-setup")],Mn),function(e){e[e.Welcome=0]="Welcome",e[e.Weather=1]="Weather",e[e.Module=2]="Module",e[e.Mapping=3]="Mapping",e[e.Zone=4]="Zone",e[e.Done=5]="Done"}(In||(In={}));let Nn=class extends le{constructor(){super(...arguments),this._step=In.Welcome,this._saving=!1,this._error="",this._confirmClose=!1,this._siConfig=null,this._useWeather=!1,this._weatherService=ze,this._apiKey="",this._weatherConfig=null,this._availableModules=[],this._selectedModuleIndex=0,this._moduleConfig={},this._mappingName="My Sensor Group",this._tempSource=Ue,this._humiditySource=Ue,this._precipSource=Ue,this._zoneName="My Zone",this._zoneSize="",this._zoneThroughput="",this._zoneEntity="",this._scheduleTime="06:00",this._scheduleCreated=!1,this._creatingSchedule=!1}async connectedCallback(){super.connectedCallback(),await this._loadInitialData()}async _loadInitialData(){var e;if(this.hass){try{const[t,s,i]=await Promise.all([Hs(this.hass),Us(this.hass),Es(this.hass)]);this._availableModules=t,this._weatherConfig=s,this._siConfig=i,this._useWeather=s.use_weather_service,this._weatherService=null!==(e=s.weather_service)&&void 0!==e?e:ze}catch(e){console.error("Wizard: failed to load initial data",e),this._error=La(e)}this.requestUpdate()}}_close(){this.dispatchEvent(new CustomEvent("wizard-close",{bubbles:!0,composed:!0}))}_navigate(e){this.dispatchEvent(new CustomEvent("wizard-navigate",{detail:{page:e},bubbles:!0,composed:!0}))}async _next(){this._error="";try{switch(this._saving=!0,this._step){case In.Welcome:this._step=In.Weather;break;case In.Weather:await this._saveWeather(),this._step=In.Module;break;case In.Module:await this._saveModule(),this._step=In.Mapping;break;case In.Mapping:await this._saveMapping(),this._step=In.Zone;break;case In.Zone:await this._saveZone(),this._step=In.Done;break;case In.Done:this._close()}}catch(e){this._error=e instanceof Error?e.message:String(e)}finally{this._saving=!1,this.requestUpdate()}}_back(){this._step>In.Welcome&&(this._step=this._step-1,this._error="")}get _canSkipCurrentStep(){return this._step===In.Weather}_skipStep(){this._canSkipCurrentStep&&this._step<In.Done&&(this._step=this._step+1,this._error="")}async _saveWeather(){await js(this.hass,this._useWeather,this._useWeather?this._weatherService:null,this._apiKey||null)}async _resolveSavedId(e,t){if("number"==typeof(null==e?void 0:e.id))return e.id;try{const e=(await t()).map(e=>e.id).filter(e=>"number"==typeof e);return e.length?Math.max(...e):void 0}catch(e){return}}async _saveModule(){if(0===this._availableModules.length)throw new Error("No calculation module is available to configure. Cannot continue.");const e=this._availableModules[this._selectedModuleIndex],t=await Ms(this.hass,{name:e.name,description:e.description,config:Object.assign(Object.assign({},e.config),this._moduleConfig),schema:e.schema});if(this._savedModuleId=await this._resolveSavedId(t,()=>Ds(this.hass)),void 0===this._savedModuleId)throw new Error("The calculation module was saved but could not be linked. Please try again.")}async _saveMapping(){const e=this._useWeather?Ue:Ge,t={[Pe]:{[Ke]:this._tempSource},[Me]:{[Ke]:this._humiditySource},[Ie]:{[Ke]:this._precipSource}},s=["Dewpoint","Evapotranspiration","Maximum Temperature","Minimum Temperature","Current Precipitation","Pressure","Solar Radiation","Windspeed"];for(const i of s)t[i]={[Ke]:e};const i=await Ns(this.hass,{name:this._mappingName,mappings:t});if(this._savedMappingId=await this._resolveSavedId(i,()=>Is(this.hass)),void 0===this._savedMappingId)throw new Error("The sensor group was saved but could not be linked. Please try again.")}async _saveZone(){if(!this._zoneName.trim())throw new Error("Zone name is required");const e=parseFloat(this._zoneSize),t=parseFloat(this._zoneThroughput);if(!(e>0))throw new Error("Zone size must be greater than 0.");if(!(t>0))throw new Error("Throughput must be greater than 0 (zones can't water otherwise).");await Os(this.hass,{name:this._zoneName.trim(),size:e,throughput:t,state:Za.Automatic,duration:0,bucket:0,delta:0,explanation:"",multiplier:1,module:this._savedModuleId,mapping:this._savedMappingId,lead_time:0,linked_entity:this._zoneEntity||void 0})}async _createDefaultSchedule(){var e,t;if(!this._scheduleCreated&&!this._creatingSchedule){this._error="",this._creatingSchedule=!0;try{const s=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";await Rs(this.hass,{name:Oa("wizard.steps.done.schedule_name",s)||"Daily",type:"daily",enabled:!0,time:this._scheduleTime||"06:00",action:"irrigate",zones:"all"}),this._scheduleCreated=!0}catch(e){this._error=e instanceof Error?e.message:String(e)}finally{this._creatingSchedule=!1,this.requestUpdate()}}}render(){var e,t;const s=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";return W`
      <div class="wizard-overlay" @click="${this._onOverlayClick}">
        <div
          class="wizard-dialog"
          @click="${e=>e.stopPropagation()}"
        >
          <div class="wizard-header">
            <span class="wizard-title">${Oa("wizard.title",s)}</span>
            <button
              class="wizard-close-btn"
              @click="${this._close}"
              title="${Oa("wizard.close",s)}"
              aria-label="${Oa("wizard.close",s)}"
            >
              <ha-icon icon="mdi:close"></ha-icon>
            </button>
          </div>
          ${this._step!==In.Welcome&&this._step!==In.Done?W`<div class="wizard-stepper">${this._renderStepper()}</div>`:""}
          <div class="wizard-body">
            ${this._renderStep(s)}
            ${this._error?W`<div class="wizard-error">${this._error}</div>`:""}
          </div>
          <div class="wizard-footer">${this._renderFooter(s)}</div>
          ${this._confirmClose?W`
                <div class="wizard-confirm-close">
                  <div class="wizard-confirm-box">
                    <p>${Oa("wizard.confirm_close.body",s)}</p>
                    <div class="wizard-confirm-actions">
                      <button
                        class="wizard-btn secondary"
                        @click="${()=>{this._confirmClose=!1}}"
                      >
                        ${Oa("wizard.confirm_close.keep",s)}
                      </button>
                      <button
                        class="wizard-btn primary"
                        @click="${()=>{this._confirmClose=!1,this._close()}}"
                      >
                        ${Oa("wizard.confirm_close.close",s)}
                      </button>
                    </div>
                  </div>
                </div>
              `:""}
        </div>
      </div>
    `}_onOverlayClick(e){e.target===e.currentTarget&&(this._step>In.Welcome&&this._step<In.Done?this._confirmClose=!0:this._close())}_renderStepper(){var e,t;const s=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en",i=[Oa("wizard.stepper.weather",s),Oa("wizard.stepper.module",s),Oa("wizard.stepper.mapping",s),Oa("wizard.stepper.zone",s)];return W`
      ${i.map((e,t)=>{const s=t+1,a=this._step===s,n=this._step>s;return W`
          <div
            class="stepper-step ${a?"active":""} ${n?"done":""}"
          >
            <div class="stepper-circle">${n?"✓":s}</div>
            <span class="stepper-label">${e}</span>
          </div>
          ${t<i.length-1?W`<div class="stepper-line ${n?"done":""}"></div>`:""}
        `})}
    `}_renderStep(e){switch(this._step){case In.Welcome:return this._renderWelcome(e);case In.Weather:return this._renderWeather(e);case In.Module:return this._renderModule(e);case In.Mapping:return this._renderMapping(e);case In.Zone:return this._renderZone(e);case In.Done:return this._renderDone(e);default:return W``}}_renderFooter(e){return this._step===In.Done?W``:W`
      <div class="footer-left">
        ${this._step>In.Welcome?W`<button
              class="wizard-btn secondary"
              @click="${this._back}"
              ?disabled="${this._saving}"
            >
              ${Oa("wizard.back",e)}
            </button>`:""}
        ${this._canSkipCurrentStep?W`<button
              class="wizard-btn ghost"
              @click="${this._skipStep}"
              ?disabled="${this._saving}"
            >
              ${Oa("wizard.skip_step",e)}
            </button>`:""}
      </div>
      <button
        class="wizard-btn primary"
        @click="${this._next}"
        ?disabled="${this._saving}"
      >
        ${this._saving?Oa("common.saving-messages.saving",e):this._step===In.Welcome||this._step<In.Zone?Oa("wizard.next",e):Oa("wizard.finish",e)}
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
    `}_renderModuleField(e,t){var s,i;const a=e.replace(/_/g," ").replace(/\b\w/g,e=>e.toUpperCase()),n=null!==(i=null!==(s=this._moduleConfig[e])&&void 0!==s?s:t.default)&&void 0!==i?i:"",o=t.description;return"boolean"===t.type?W`
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
          @input="${s=>{const i=s.target.value,a="float"===t.type?parseFloat(i):"integer"===t.type?parseInt(i):i;this._moduleConfig=Object.assign(Object.assign({},this._moduleConfig),{[e]:a})}}"
        />
      </si-field>
    `}_renderMapping(e){const t=[{value:Ue,label:Oa("wizard.steps.mapping.use_weather_service",e)},{value:"sensor",label:Oa("wizard.steps.mapping.use_sensor",e)},{value:"static",label:Oa("wizard.steps.mapping.use_static",e)},{value:Ge,label:Oa("wizard.steps.mapping.use_none",e)}],s=(s,i,a)=>W`
      <si-field
        label="${Oa("wizard.steps.mapping.source_label",e)} ${s}"
      >
        <select
          class="wizard-input"
          @change="${e=>a(e.target.value)}"
        >
          ${t.map(e=>W`<option value="${e.value}" ?selected="${e.value===i}">
                ${e.label}
              </option>`)}
        </select>
      </si-field>
    `;return W`
      <h2 class="step-title">
        ${Oa("wizard.steps.mapping.title",e)}
      </h2>
      <p class="step-desc">
        ${Oa("wizard.steps.mapping.description",e)}
      </p>

      <si-field
        label="${Oa("wizard.steps.mapping.name_label",e)}"
        required
      >
        <input
          type="text"
          class="wizard-input"
          .value="${this._mappingName}"
          @input="${e=>{this._mappingName=e.target.value}}"
        />
      </si-field>

      ${s(Oa("panels.mappings.cards.mapping.items.temperature",e)||"Temperature",this._tempSource,e=>{this._tempSource=e,this.requestUpdate()})}
      ${s(Oa("panels.mappings.cards.mapping.items.humidity",e)||"Humidity",this._humiditySource,e=>{this._humiditySource=e,this.requestUpdate()})}
      ${s(Oa("panels.mappings.cards.mapping.items.precipitation",e)||"Precipitation",this._precipSource,e=>{this._precipSource=e,this.requestUpdate()})}

      <p class="step-tip">
        ${Oa("wizard.steps.mapping.description",e)}
      </p>
    `}_renderZone(e){var t;const s="imperial"!==(null===(t=this._siConfig)||void 0===t?void 0:t.units);return W`
      <h2 class="step-title">${Oa("wizard.steps.zone.title",e)}</h2>
      <p class="step-desc">
        ${Oa("wizard.steps.zone.description",e)}
      </p>

      <si-zone-form
        .hass="${this.hass}"
        .metric="${s}"
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
        <h2 class="step-title">${Oa("wizard.steps.done.title",e)}</h2>
        <p class="step-desc">
          ${Oa("wizard.steps.done.description",e)}
        </p>
        <ul class="step-list">
          <li>${Oa("wizard.steps.done.tip1",e)}</li>
          <li>${Oa("wizard.steps.done.tip2",e)}</li>
          <li>${Oa("wizard.steps.done.tip3",e)}</li>
        </ul>

        <div class="schedule-offer">
          ${this._scheduleCreated?W`
                <div class="schedule-created">
                  <ha-icon icon="mdi:calendar-check"></ha-icon>
                  <span
                    >${Oa("wizard.steps.done.schedule_created",e)}</span
                  >
                </div>
              `:W`
                <p class="schedule-offer-title">
                  ${Oa("wizard.steps.done.schedule_title",e)}
                </p>
                <p class="schedule-offer-desc">
                  ${Oa("wizard.steps.done.schedule_desc",e)}
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
                    ${this._creatingSchedule?Oa("common.saving-messages.saving",e):Oa("wizard.steps.done.schedule_create",e)}
                  </button>
                </div>
              `}
        </div>

        <div class="done-actions">
          <button
            class="wizard-btn primary"
            @click="${()=>{this._close(),this._navigate("zones")}}"
          >
            ${Oa("wizard.steps.done.go_zones",e)}
          </button>
          <button
            class="wizard-btn secondary"
            @click="${()=>{this._close(),this._navigate("setup")}}"
          >
            ${Oa("wizard.steps.done.go_setup",e)}
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
    `}};t([pe({attribute:!1})],Nn.prototype,"hass",void 0),t([ge()],Nn.prototype,"_step",void 0),t([ge()],Nn.prototype,"_saving",void 0),t([ge()],Nn.prototype,"_error",void 0),t([ge()],Nn.prototype,"_confirmClose",void 0),t([ge()],Nn.prototype,"_siConfig",void 0),t([ge()],Nn.prototype,"_useWeather",void 0),t([ge()],Nn.prototype,"_weatherService",void 0),t([ge()],Nn.prototype,"_apiKey",void 0),t([ge()],Nn.prototype,"_weatherConfig",void 0),t([ge()],Nn.prototype,"_availableModules",void 0),t([ge()],Nn.prototype,"_selectedModuleIndex",void 0),t([ge()],Nn.prototype,"_moduleConfig",void 0),t([ge()],Nn.prototype,"_mappingName",void 0),t([ge()],Nn.prototype,"_tempSource",void 0),t([ge()],Nn.prototype,"_humiditySource",void 0),t([ge()],Nn.prototype,"_precipSource",void 0),t([ge()],Nn.prototype,"_zoneName",void 0),t([ge()],Nn.prototype,"_zoneSize",void 0),t([ge()],Nn.prototype,"_zoneThroughput",void 0),t([ge()],Nn.prototype,"_zoneEntity",void 0),t([ge()],Nn.prototype,"_scheduleTime",void 0),t([ge()],Nn.prototype,"_scheduleCreated",void 0),t([ge()],Nn.prototype,"_creatingSchedule",void 0),Nn=t([ce("si-setup-wizard")],Nn);const Ln=Ka;var Rn;!function(e){e.Zones="zones",e.Setup="setup"}(Rn||(Rn={})),e.SmartIrrigationPanel=class extends le{constructor(){super(...arguments),this._wizardOpen=!1,this._updateScheduled=!1,this._lastNavigationTime=0,this._navigationThrottleDelay=100}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate()}))}async firstUpdated(){const e=qa().page;Object.values(Rn).includes(e)||Na(0,Ga(Rn.Zones)),window.addEventListener("location-changed",()=>{if(!window.location.pathname.includes("smart-irrigation"))return;const e=performance.now();e-this._lastNavigationTime<this._navigationThrottleDelay||(this._lastNavigationTime=e,this._scheduleUpdate())}),qs().then(()=>{this._scheduleUpdate()}).catch(e=>{console.error("Failed to load HA form elements:",e),this._scheduleUpdate()}),this.hass&&Es(this.hass).then(e=>{this._config=e,this._scheduleUpdate()}).catch(e=>{console.error("Failed to fetch config for version display:",e)})}_ensureLanguage(){this.hass&&!Ta(this.hass.language)&&function(e){const t=Ca(e);return Ta(e)?Promise.resolve():(Ea[t]||(Ea[t]=fetch(`/smart_irrigation_static/languages/${t}.json?v=${ve}`).then(e=>e.ok?e.json():Promise.reject(e.status)).then(e=>{Aa[t]=e}).catch(()=>{Aa[t]=Aa.en})),Ea[t])}(this.hass.language).then(()=>this.requestUpdate())}render(){var e,t;if(this.hass&&!Ta(this.hass.language))return this._ensureLanguage(),W``;const s=qa(),i=!!customElements.get("ha-tab-group"),a=!!customElements.get("ha-tab-group-tab");return W`
      <div class="header">
        <div class="toolbar">
          <ha-menu-button
            .hass=${this.hass}
            .narrow=${this.narrow}
          ></ha-menu-button>
          <div class="main-title">${Oa("title",this.hass.language)}</div>
          <div class="version">${null!==(t=null===(e=this._config)||void 0===e?void 0:e.version)&&void 0!==t?t:ve}</div>
        </div>

        ${i&&a?W`
              <ha-tab-group @wa-tab-show=${this.handlePageSelected}>
                ${Object.values(Rn).map(e=>W`
                    <ha-tab-group-tab
                      slot="nav"
                      panel="${e}"
                      .active=${s.page===e}
                    >
                      ${Oa(`panels.${e}.title`,this.hass.language)}
                    </ha-tab-group-tab>
                  `)}
              </ha-tab-group>
            `:W`
              <div class="custom-tabs">
                ${Object.values(Rn).map(e=>W`
                    <button
                      class="custom-tab ${s.page===e?"active":""}"
                      @click=${()=>this.navigateToPage(e)}
                    >
                      ${Oa(`panels.${e}.title`,this.hass.language)}
                    </button>
                  `)}
              </div>
            `}
      </div>
      <div class="view">${this.getView(s)}</div>
      ${this._wizardOpen?W`
            <si-setup-wizard
              .hass="${this.hass}"
              @wizard-close="${()=>{this._wizardOpen=!1}}"
              @wizard-navigate="${e=>{var t,s;const i=null!==(s=null===(t=e.detail)||void 0===t?void 0:t.page)&&void 0!==s?s:"zones";this._wizardOpen=!1,this.navigateToPage(i)}}"
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
        `}}navigateToPage(e){if(e!==qa().page){const t=Ga(e);Na(0,t),this.requestUpdate()}else scrollTo(0,0)}handlePageSelected(e){const t=e.detail.name;if(t!==qa().page){const e=Ga(t);Na(0,e),this.requestUpdate()}else scrollTo(0,0)}static get styles(){return[Ln,r`
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
      `]}},t([pe({attribute:!1})],e.SmartIrrigationPanel.prototype,"hass",void 0),t([pe({type:Boolean,reflect:!0})],e.SmartIrrigationPanel.prototype,"narrow",void 0),t([ge()],e.SmartIrrigationPanel.prototype,"_wizardOpen",void 0),t([ge()],e.SmartIrrigationPanel.prototype,"_config",void 0),e.SmartIrrigationPanel=t([ce("smart-irrigation")],e.SmartIrrigationPanel);let Pn=class extends le{async showDialog(e){this._params=e,await this.updateComplete}async closeDialog(){this._params=void 0}render(){return this._params?W`
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
    `}};t([pe({attribute:!1})],Pn.prototype,"hass",void 0),t([ge()],Pn.prototype,"_params",void 0),Pn=t([ce("error-dialog")],Pn);var Bn=Object.freeze({__proto__:null,get ErrorDialog(){return Pn}})}({});
